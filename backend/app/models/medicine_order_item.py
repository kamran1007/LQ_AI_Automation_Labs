from sqlalchemy import (
    Integer,
    String,
    ForeignKey
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.db.base import Base


class MedicineOrderItem(Base):

    __tablename__ = "medicine_order_items"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey("medicine_orders.id"),
        index=True
    )

    medicine_name: Mapped[str] = mapped_column(
        String(255)
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        default=1
    )