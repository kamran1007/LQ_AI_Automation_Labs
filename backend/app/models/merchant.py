from datetime import datetime

from sqlalchemy import (
    String,
    Boolean,
    DateTime
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.db.base import Base


class Merchant(Base):

    __tablename__ = "merchants"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        index=True
    )

    merchant_type: Mapped[str] = mapped_column(
        String(100),
        index=True
    )

    mobile: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )