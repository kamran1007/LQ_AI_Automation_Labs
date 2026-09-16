from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Float, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
if TYPE_CHECKING:
    from app.models.user_role import UserRole

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    mobile: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True,
        nullable=False
    )

    name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True
    )
    # NEED TO CREATE SEPARATE ROLE AND ROLE NAME TABLE AND MAP TO USER TABLE IN FUTURE
    # role: Mapped[str] = mapped_column(  
    #     String(50),
    #     default="user",
    #     nullable=False,
    #     index=True
    # )

    latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    location_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    roles: Mapped[list["UserRole"]] = relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan"
    )