from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    String,
    Text,
    DateTime,
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


if TYPE_CHECKING:
    from app.models.appointment_request import AppointmentRequest
    from app.models.user import User


class AppointmentProposal(Base):
    __tablename__ = "appointment_proposals"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    appointment_request_id: Mapped[int] = mapped_column(
        ForeignKey(
            "appointment_requests.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    proposed_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    proposed_start_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    duration_minutes: Mapped[int] = mapped_column(
        Integer,
        default=30,
        nullable=False
    )

    message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="pending",
        nullable=False,
        index=True
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    appointment_request: Mapped["AppointmentRequest"] = relationship(
        "AppointmentRequest"
    )

    proposed_by: Mapped["User | None"] = relationship(
        "User"
    )