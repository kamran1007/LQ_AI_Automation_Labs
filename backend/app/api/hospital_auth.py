from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from app.models.user import User
from app.models.hospital import Hospital

from app.schemas.hospital_auth_schema import (
    HospitalVerifyOTPRequest,
    HospitalAuthResponse,
)

from app.services.otp_service import verify_otp

from app.services.auth_session_service import (
    create_auth_session,
)

from app.services.auth_token_service import (
    create_access_token,
)

from app.services.hospital_auth_service import (
    get_user_hospital_context,
)

from app.api.hospital import get_current_hospital_context

from app.services.auth_session_service import revoke_auth_session

from app.utils.mobile import normalize_indian_mobile


router = APIRouter()


@router.post(
    "/verify",
    response_model=HospitalAuthResponse,
)
async def verify_hospital_otp(
    request: HospitalVerifyOTPRequest,
    db: AsyncSession = Depends(get_db),
):

    # --------------------------------------------------
    # 1. Normalize Indian mobile number
    # --------------------------------------------------

    try:
        normalized_mobile = normalize_indian_mobile(
            request.mobile
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    # --------------------------------------------------
    # 2. Verify OTP
    # --------------------------------------------------

    otp_valid = await verify_otp(
        mobile=normalized_mobile,
        otp=request.otp,
    )

    if not otp_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP",
        )

    # --------------------------------------------------
    # 3. Find user by normalized mobile
    # --------------------------------------------------

    result = await db.execute(
        select(User).where(
            User.mobile == normalized_mobile
        )
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Hospital user not found",
        )

    # --------------------------------------------------
    # 4. Validate user
    # --------------------------------------------------

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not verified",
        )

    # --------------------------------------------------
    # 5. Resolve hospital + role from DB
    # --------------------------------------------------

    hospital_context = await get_user_hospital_context(
        db=db,
        user_id=user.id,
    )

    role_id = hospital_context["role_id"]
    role_name = hospital_context["role_name"]
    hospital_id = hospital_context["hospital_id"]

    # --------------------------------------------------
    # 6. Verify hospital
    # --------------------------------------------------

    result = await db.execute(
        select(Hospital).where(
            Hospital.id == hospital_id,
            Hospital.is_active == True,
        )
    )

    hospital = result.scalar_one_or_none()

    if hospital is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hospital not found or inactive",
        )

    # --------------------------------------------------
    # 7. Create authentication session
    # --------------------------------------------------

    auth_session = await create_auth_session(
        db=db,
        user_id=user.id,
        device_name="hospital",
    )

    # --------------------------------------------------
    # 8. Create hospital-scoped access token
    # --------------------------------------------------

    access_token = create_access_token(
        user_id=user.id,
        session_id=auth_session["session_id"],
        role_id=role_id,
        hospital_id=hospital_id,
    )

    # --------------------------------------------------
    # 9. Return tokens
    # --------------------------------------------------

    return {
        "success": True,
        "message": "Hospital login successful",

        "access_token": access_token,
        "refresh_token": auth_session["refresh_token"],

        "token_type": "bearer",

        "user_id": user.id,
        "user_name": user.name,

        "role_id": role_id,
        "role_name": role_name,

        "hospital_id": hospital_id,
        "hospital_name": hospital.name,

        "session_id": auth_session["session_id"],

        "expires_at": (
            auth_session["expires_at"].isoformat()
        ),
    }


@router.post("/logout")
async def hospital_logout(
    db: AsyncSession = Depends(get_db),
    context=Depends(get_current_hospital_context),
):
    auth_session = context["session"]

    await revoke_auth_session(
        db=db,
        auth_session=auth_session,
        reason="hospital_logout",
    )

    return {
        "success": True,
        "message": "Hospital logout successful.",
    }