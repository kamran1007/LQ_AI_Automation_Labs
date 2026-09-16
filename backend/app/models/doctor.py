from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.hospital import Hospital
from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    hospital_id: Mapped[int] = mapped_column(
        ForeignKey("hospitals.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )

    specialization: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )

    qualification: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
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

    hospital: Mapped["Hospital"] = relationship(
        "Hospital",
        back_populates="doctors"
    )