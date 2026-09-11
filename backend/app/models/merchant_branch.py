from datetime import datetime

from sqlalchemy import (
    String,
    Float,
    Integer,
    ForeignKey,
    DateTime
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.db.base import Base


class MerchantBranch(Base):

    __tablename__ = "merchant_branches"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    merchant_id: Mapped[int] = mapped_column(
        ForeignKey("merchants.id")
    )

    branch_name: Mapped[str] = mapped_column(
        String(255)
    )

    address: Mapped[str] = mapped_column(
        String(500)
    )

    latitude: Mapped[float] = mapped_column(
        Float
    )

    longitude: Mapped[float] = mapped_column(
        Float
    )

    service_radius_km: Mapped[int] = mapped_column(
        Integer,
        default=5
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )