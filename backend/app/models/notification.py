from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    String,
    Text,
    DateTime,
    ForeignKey,
    Boolean,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.db.base import Base


if TYPE_CHECKING:
    from app.models.user import User
    from app.models.hospital import Hospital
    from app.models.appointment_request import AppointmentRequest


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    recipient_user_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    hospital_id: Mapped[int] = mapped_column(
        ForeignKey(
            "hospitals.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    appointment_request_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "appointment_requests.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # -----------------------------------------
    # RELATIONSHIPS
    # -----------------------------------------

    recipient: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[recipient_user_id],
        back_populates="notifications",
    )

    hospital: Mapped["Hospital"] = relationship(
        "Hospital",
    )

    appointment_request: Mapped[
        "AppointmentRequest | None"
    ] = relationship(
        "AppointmentRequest",
    )