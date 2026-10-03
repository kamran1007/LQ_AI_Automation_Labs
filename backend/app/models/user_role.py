from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.role import Role
    from app.models.user import User
    from app.models.hospital import Hospital


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UserRole(Base):
    __tablename__ = "user_roles"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    hospital_id: Mapped[int | None] = mapped_column(
        ForeignKey("hospitals.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="roles"
    )

    role: Mapped["Role"] = relationship(
        "Role",
        back_populates="users"
    )

    hospital: Mapped["Hospital | None"] = relationship(
        "Hospital"
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "role_id",
            "hospital_id",
            name="uq_user_roles_user_role_hospital"
        ),
    )