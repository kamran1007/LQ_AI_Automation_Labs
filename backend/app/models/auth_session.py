from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    # ---------------------------------------------------------
    # Primary key
    # ---------------------------------------------------------

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    # ---------------------------------------------------------
    # User
    # ---------------------------------------------------------

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    # ---------------------------------------------------------
    # Session identification
    #
    # This is NOT the refresh token itself.
    # ---------------------------------------------------------

    session_id: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
    )

    # ---------------------------------------------------------
    # Refresh token
    #
    # Store only the HASH of the refresh token.
    # Never store the raw refresh token in DB.
    # ---------------------------------------------------------

    refresh_token_hash: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    # ---------------------------------------------------------
    # Token/session lifetime
    # ---------------------------------------------------------

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ---------------------------------------------------------
    # Revocation
    # ---------------------------------------------------------

    is_revoked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("FALSE"),
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    revoked_reason: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # ---------------------------------------------------------
    # Token rotation / reuse detection
    # ---------------------------------------------------------

    replaced_by_session_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    # ---------------------------------------------------------
    # Device/session information
    # ---------------------------------------------------------

    device_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    user_agent: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    # ---------------------------------------------------------
    # Relationship
    # ---------------------------------------------------------

    user = relationship(
        "User",
        back_populates="auth_sessions",
    )

    # ---------------------------------------------------------
    # Indexes
    # ---------------------------------------------------------

    __table_args__ = (
        Index(
            "ix_auth_sessions_user_id",
            "user_id",
        ),
        Index(
            "ix_auth_sessions_expires_at",
            "expires_at",
        ),
        Index(
            "ix_auth_sessions_user_active",
            "user_id",
            "is_revoked",
        ),
    )