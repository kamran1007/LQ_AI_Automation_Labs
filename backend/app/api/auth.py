from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.schemas.auth_schema import VerifyMSG91TokenRequest
from app.services.msg91_service import (
    verify_msg91_access_token,
)


router = APIRouter(
    prefix="/authuser",
    tags=["Authentication"],
)


@router.post("/verify")
async def verify_msg91_token_endpoint(
    request: VerifyMSG91TokenRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        msg91_response = (
            await verify_msg91_access_token(
                request.access_token
            )
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )

    # -----------------------------------------
    # MSG91 successfully verified the token
    # -----------------------------------------

    if msg91_response.get("type") != "success":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="MSG91 token verification failed",
        )

    verified_mobile = msg91_response.get(
        "message"
    )

    if not verified_mobile:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="MSG91 did not return a mobile number",
        )

    # -----------------------------------------
    # Find LightningQ user
    # -----------------------------------------

    result = await db.execute(
        select(User).where(
            User.mobile == verified_mobile
        )
    )

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not registered with LightningQ",
        )

    # -----------------------------------------
    # Mark user as verified
    # -----------------------------------------

    user.is_verified = True

    await db.commit()
    await db.refresh(user)

    return {
        "success": True,
        "message": "User verified successfully",
        "user_id": user.id,
        "mobile": user.mobile,
        "name": user.name,
        "is_verified": user.is_verified,
    }