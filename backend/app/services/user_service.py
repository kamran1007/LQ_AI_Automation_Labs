from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def create_user(
    db: AsyncSession,
    mobile: str,
    name: str | None = None
) -> User:

    # Check whether mobile already exists
    result = await db.execute(
        select(User).where(User.mobile == mobile)
    )

    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise ValueError("User with this mobile number already exists")

    # Create new user
    user = User(
        mobile=mobile,
        name=name,
        is_verified=False,
        is_active=True
    )

    db.add(user)

    await db.commit()

    await db.refresh(user)

    return user