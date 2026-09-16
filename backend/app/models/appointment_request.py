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
    from app.models.user import User
    from app.models.conversation import Conversation
    from app.models.hospital import Hospital
    from app.models.doctor import Doctor


class AppointmentRequest(Base):
    __tablename__ = "appointment_requests"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    hospital_id: Mapped[int] = mapped_column(
        ForeignKey("hospitals.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )

    conversation_id: Mapped[int | None] = mapped_column(
        ForeignKey("conversations.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    requested_start_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    duration_minutes: Mapped[int] = mapped_column(
        Integer,
        default=30,
        nullable=False
    )

    patient_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(40),
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

    patient: Mapped["User"] = relationship(
        "User"
    )

    hospital: Mapped["Hospital"] = relationship(
        "Hospital"
    )

    doctor: Mapped["Doctor"] = relationship(
        "Doctor"
    )

    conversation: Mapped["Conversation | None"] = relationship(
        "Conversation"
    )