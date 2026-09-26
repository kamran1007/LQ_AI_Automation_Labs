from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.services.msg91_service import verify_msg91_access_token

from app.schemas.auth_schema import (
    RefreshTokenRequest,
    RefreshTokenResponse,
    VerifyMSG91TokenRequest,
)
from app.services.auth_session_service import (
    get_valid_session_by_refresh_token,
    rotate_auth_session,
    revoke_session_by_refresh_token,
)
from app.services.auth_session_service import create_auth_session

router = APIRouter(
    prefix="/authuser",
    tags=["Authentication"],
)


@router.post("/verify")
async def verify_msg91_token_endpoint(
    request: VerifyMSG91TokenRequest,
    db: AsyncSession = Depends(get_db),
):
    # --------------------------------------------------
    # 1. Verify MSG91 access token
    # --------------------------------------------------

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

    # --------------------------------------------------
    # 2. Confirm MSG91 verification succeeded
    # --------------------------------------------------

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

    # --------------------------------------------------
    # 3. Find existing user
    # --------------------------------------------------

    result = await db.execute(
        select(User).where(
            User.mobile == verified_mobile
        )
    )

    user = result.scalar_one_or_none()

    # --------------------------------------------------
    # 4. Create user if not registered
    # --------------------------------------------------

    if user is None:
        user = User(
            mobile=verified_mobile,
            is_verified=True,
            is_active=True,
        )

        db.add(user)

        await db.commit()
        await db.refresh(user)

    # --------------------------------------------------
    # 5. Existing user
    # --------------------------------------------------

    else:
        user.is_verified = True

        await db.commit()
        await db.refresh(user)

    # --------------------------------------------------
    # 6. Create our application auth session
    # --------------------------------------------------

    auth_session = await create_auth_session(
        db=db,
        user_id=user.id,
    )

    # --------------------------------------------------
    # 7. Return application tokens
    # --------------------------------------------------

    return {
        "success": True,
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
@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
)
async def refresh_access_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh an access token using a valid refresh token.

    Refresh-token rotation is performed:
    - old session is revoked
    - new session is created
    - new refresh token is generated
    - new access token is generated
    """

    # --------------------------------------------------
    # Find valid session
    # --------------------------------------------------

    session = await get_valid_session_by_refresh_token(
        db=db,
        refresh_token=request.refresh_token,
    )

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid, expired, or revoked refresh token",
        )

    # --------------------------------------------------
    # Rotate session
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Return new tokens
    # --------------------------------------------------

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