# app/models/appointment.py

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.hospital import Hospital
    from app.models.doctor import Doctor
    from app.models.appointment_request import AppointmentRequest
    from app.models.appointment_proposal import AppointmentProposal


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    appointment_request_id: Mapped[int] = mapped_column(
        ForeignKey(
            "appointment_requests.id",
            ondelete="RESTRICT"
        ),
        nullable=False,
        index=True
    )

    appointment_proposal_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "appointment_proposals.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
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

    confirmed_start_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    duration_minutes: Mapped[int] = mapped_column(
        Integer,
        default=30,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="confirmed",
        nullable=False,
        index=True
    )

    confirmation_sent: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
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

    appointment_proposal: Mapped["AppointmentProposal | None"] = relationship(
        "AppointmentProposal"
    )

    patient: Mapped["User"] = relationship("User")
    hospital: Mapped["Hospital"] = relationship("Hospital")
    doctor: Mapped["Doctor"] = relationship("Doctor")