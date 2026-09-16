from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.doctor import Doctor
from sqlalchemy import (
    String,
    Text,
    Boolean,
    DateTime,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Hospital(Base):
    __tablename__ = "hospitals"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )
    # Other hospital fields remain unchanged...

    doctors: Mapped[list["Doctor"]] = relationship(
        "Doctor",
        back_populates="hospital",
        cascade="all, delete-orphan"
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )

    state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    country: Mapped[str] = mapped_column(
        String(100),
        default="India",
        nullable=False
    )

    timezone: Mapped[str] = mapped_column(
        String(64),
        default="Asia/Kolkata",
        nullable=False
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

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )