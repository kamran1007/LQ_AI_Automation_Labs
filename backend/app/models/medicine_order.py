from datetime import datetime

from sqlalchemy import (
    String,
    Float,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.db.base import Base


class MedicineOrder(Base):

    __tablename__ = "medicine_orders"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        index=True
    )

    delivery_address: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    selected_merchant_id: Mapped[int | None] = mapped_column(
        ForeignKey("merchants.id"),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )