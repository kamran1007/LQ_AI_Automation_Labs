from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user_schema import (
    CreateUserRequest,
    UserResponse
)
from app.services.user_service import create_user
from app.core.auth_dependency import get_current_auth_session
from app.models.auth_session import AuthSession


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_user_endpoint(
    request: CreateUserRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        user = await create_user(
            db=db,
            mobile=request.mobile,
            name=request.name
        )

        return user

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@router.get(
    "/me"
)
async def get_current_user(
    auth_session: AuthSession = Depends(
        get_current_auth_session
    ),
):
    return {
        "success": True,
        "user_id": auth_session.user_id,
        "session_id": auth_session.session_id,
    }