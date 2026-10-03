from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_role import UserRole
from app.models.role import Role


async def get_user_hospital_context(
    db: AsyncSession,
    user_id: int,
):
    result = await db.execute(
        select(UserRole, Role)
        .join(
            Role,
            Role.id == UserRole.role_id
        )
        .where(
            UserRole.user_id == user_id,
            UserRole.hospital_id.is_not(None),
        )
    )

    rows = result.all()

    if not rows:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with a hospital",
        )

    # For the MVP, use the hospital membership.
    # Later, if multiple hospital memberships are allowed,
    # the login flow should explicitly select the membership
    # after authentication.
    user_role, role = rows[0]

    return {
        "role_id": user_role.role_id,
        "role_name": role.name,
        "hospital_id": user_role.hospital_id,
    }