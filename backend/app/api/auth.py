from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.schemas.auth_schema import VerifyMSG91TokenRequest
from app.services.msg91_service import verify_msg91_access_token


router = APIRouter(
    prefix="/authuser",
    tags=["Authentication"],
)


@router.post("/verify")
async def verify_msg91_token_endpoint(
    request: VerifyMSG91TokenRequest,
    db: AsyncSession = Depends(get_db),
):
    # Verify the access token with MSG91
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

    # Confirm MSG91 verification succeeded
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

    # Find the user by mobile number
    result = await db.execute(
        select(User).where(User.mobile == verified_mobile)
    )
    user = result.scalar_one_or_none()

    # Create a new user if the mobile number is not registered
    if user is None:
        user = User(
            mobile=verified_mobile,
            is_verified=True,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

    # Mark an existing user as verified
    else:
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