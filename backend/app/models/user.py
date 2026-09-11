from datetime import datetime

from sqlalchemy import String, Float, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    mobile: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True
    )

    name: Mapped[str | None] = mapped_column(
        String(255),
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

    location_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
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