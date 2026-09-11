from datetime import datetime

from sqlalchemy import (
    Float,
    Integer,
    String,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.db.base import Base


class MerchantResponse(Base):

    __tablename__ = "merchant_responses"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey("medicine_orders.id"),
        index=True
    )

    merchant_id: Mapped[int] = mapped_column(
        ForeignKey("merchants.id")
    )

    total_price: Mapped[float] = mapped_column(
        Float
    )

    delivery_charge: Mapped[float] = mapped_column(
        Float,
        default=0
    )

    eta_minutes: Mapped[int] = mapped_column(
        Integer,
        default=30
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="quoted"
    )

    remarks: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )