from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User

from app.utils.mobile import normalize_indian_mobile

from app.services.msg91_service import (
    verify_msg91_access_token,
)

from app.services.registration_service import (
    create_registration_token,
    verify_registration_token,
)

from app.schemas.auth_schema import (
    RefreshTokenRequest,
    RefreshTokenResponse,
    VerifyMSG91TokenRequest,
    RegisterUserRequest,
)

from app.services.auth_session_service import (
    get_valid_session_by_refresh_token,
    rotate_auth_session,
    revoke_session_by_refresh_token,
    create_auth_session,
)


router = APIRouter(
    prefix="/authuser",
    tags=["Authentication"],
)


# ============================================================
# VERIFY MSG91 TOKEN
# ============================================================

@router.post("/verify")
async def verify_msg91_token_endpoint(
    request: VerifyMSG91TokenRequest,
    db: AsyncSession = Depends(get_db),
):

    # --------------------------------------------------------
    # 1. Verify MSG91 access token
    # --------------------------------------------------------

    try:
        msg91_response = await verify_msg91_access_token(
            request.access_token
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    # --------------------------------------------------------
    # 2. Confirm MSG91 verification succeeded
    # --------------------------------------------------------

    if msg91_response.get("type") != "success":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="MSG91 token verification failed",
        )

    verified_mobile = msg91_response.get("message")

    if not verified_mobile:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="MSG91 did not return a mobile number",
        )

    # --------------------------------------------------------
    # 3. Normalize mobile number
    # --------------------------------------------------------

    try:
        verified_mobile = normalize_indian_mobile(
            verified_mobile
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="MSG91 returned an invalid mobile number",
        ) from exc

    # --------------------------------------------------------
    # 4. Find existing user
    # --------------------------------------------------------

    result = await db.execute(
        select(User).where(
            User.mobile == verified_mobile
        )
    )

    user = result.scalar_one_or_none()

    # --------------------------------------------------------
    # 5. NEW USER
    # --------------------------------------------------------

    if user is None:

        registration_token = create_registration_token(
            verified_mobile
        )

        return {
            "success": True,
            "requires_name": True,
            "is_new_user": True,

            "mobile": verified_mobile,

            "registration_token": registration_token,

            "message": (
                "Your mobile number is verified. "
                "Name is required to create your account."
            ),
        }

    # --------------------------------------------------------
    # 6. EXISTING USER
    # --------------------------------------------------------

    user.is_verified = True

    await db.commit()
    await db.refresh(user)

    # --------------------------------------------------------
    # 7. Create application auth session
    # --------------------------------------------------------

    auth_session = await create_auth_session(
        db=db,
        user_id=user.id,
    )

    # --------------------------------------------------------
    # 8. Return login response
    # --------------------------------------------------------

    return {
        "success": True,

        "requires_name": False,
        "is_new_user": False,

        "message": "User verified successfully",

        "user_id": user.id,
        "mobile": user.mobile,
        "name": user.name,
        "is_verified": user.is_verified,

        "access_token": auth_session["access_token"],
        "refresh_token": auth_session["refresh_token"],

        "token_type": "bearer",

        "session_id": auth_session["session_id"],
        "expires_at": auth_session["expires_at"],
    }


# ============================================================
# REGISTER NEW USER
# ============================================================

@router.post("/register")
async def register_user(
    request: RegisterUserRequest,
    db: AsyncSession = Depends(get_db),
):

    # --------------------------------------------------------
    # 1. Validate registration token
    # --------------------------------------------------------

    try:
        registration_data = verify_registration_token(
            request.registration_token
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    # --------------------------------------------------------
    # 2. Get verified mobile
    # --------------------------------------------------------

    verified_mobile = registration_data.get(
        "mobile"
    )

    if not verified_mobile:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Registration token does not contain a mobile number.",
        )

    try:
        verified_mobile = normalize_indian_mobile(
            verified_mobile
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid mobile number.",
        ) from exc

    # --------------------------------------------------------
    # 3. Validate name
    # --------------------------------------------------------

    cleaned_name = request.name.strip()

    if len(cleaned_name) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please enter a valid name.",
        )

    # --------------------------------------------------------
    # 4. Make sure user wasn't already registered
    # --------------------------------------------------------

    result = await db.execute(
        select(User).where(
            User.mobile == verified_mobile
        )
    )

    existing_user = result.scalar_one_or_none()

    if existing_user is not None:

        # This can happen if registration was submitted twice.

        if not existing_user.is_verified:
            existing_user.is_verified = True

            if not existing_user.name:
                existing_user.name = cleaned_name

            await db.commit()
            await db.refresh(existing_user)

        auth_session = await create_auth_session(
            db=db,
            user_id=existing_user.id,
        )

        return {
            "success": True,

            "requires_name": False,
            "is_new_user": False,

            "message": "User already registered.",

            "user_id": existing_user.id,
            "mobile": existing_user.mobile,
            "name": existing_user.name,
            "is_verified": existing_user.is_verified,

            "access_token": auth_session["access_token"],
            "refresh_token": auth_session["refresh_token"],

            "token_type": "bearer",

            "session_id": auth_session["session_id"],
            "expires_at": auth_session["expires_at"],
        }

    # --------------------------------------------------------
    # 5. Create new user
    # --------------------------------------------------------

    user = User(
        mobile=verified_mobile,
        name=cleaned_name,
        is_verified=True,
        is_active=True,
    )

    db.add(user)

    try:
        await db.commit()
        await db.refresh(user)

    except Exception:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create user account.",
        )

    # --------------------------------------------------------
    # 6. Create application auth session
    # --------------------------------------------------------

    auth_session = await create_auth_session(
        db=db,
        user_id=user.id,
    )

    # --------------------------------------------------------
    # 7. Return authenticated user
    # --------------------------------------------------------

    return {
        "success": True,

        "requires_name": False,
        "is_new_user": True,

        "message": "Account created successfully.",

        "user_id": user.id,
        "mobile": user.mobile,
        "name": user.name,
        "is_verified": user.is_verified,

        "access_token": auth_session["access_token"],
        "refresh_token": auth_session["refresh_token"],

        "token_type": "bearer",

        "session_id": auth_session["session_id"],
        "expires_at": auth_session["expires_at"],
    }


# ============================================================
# REFRESH
# ============================================================

@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
)
async def refresh_access_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):

    session = await get_valid_session_by_refresh_token(
        db=db,
        refresh_token=request.refresh_token,
    )

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid, expired, or revoked refresh token",
        )

    try:
        tokens = await rotate_auth_session(
            db=db,
            session=session,
        )

    except Exception:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to refresh authentication session",
        )

    return RefreshTokenResponse(
        success=True,
        message="Token refreshed successfully",

        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],

        token_type="bearer",

        user_id=session.user_id,
        session_id=tokens["session_id"],

        refresh_token_expires_at=tokens["expires_at"],
    )


# ============================================================
# LOGOUT
# ============================================================

@router.post("/logout")
async def logout(
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
):

    revoked = await revoke_session_by_refresh_token(
        db=db,
        refresh_token=refresh_token,
        reason="logout",
    )

    if not revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid, expired, or revoked refresh token",
        )

    return {
        "success": True,
        "message": "Logged out successfully",
    }