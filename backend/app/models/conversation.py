from sqlalchemy import String, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional

from app.db.base import Base


class Conversation(Base):

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[str] = mapped_column(
        String(255),
        index=True
    )

    message: Mapped[str] = mapped_column(
        Text
    )

    ai_response: Mapped[str] = mapped_column(
        Text
    )

    intent: Mapped[str] = mapped_column(
        String(100),
        index=True
    )

    extra_data: Mapped[Optional[dict]] = mapped_column(
    JSON,
    nullable=True
)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )