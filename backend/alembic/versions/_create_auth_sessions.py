"""create auth_sessions table

Revision ID: create_auth_sessions
Revises: <PREVIOUS_REVISION_ID>
Create Date: 2026-09-25
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "create_auth_sessions"
down_revision: Union[str, Sequence[str], None] = "ad29b283d485"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # Create auth_sessions table
    # ---------------------------------------------------------
    op.create_table(
        "auth_sessions",

        # Primary key
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        # User relationship
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),

        # Unique session identifier
        sa.Column(
            "session_id",
            sa.String(length=128),
            nullable=False,
        ),

        # Hashed refresh token
        sa.Column(
            "refresh_token_hash",
            sa.String(length=255),
            nullable=False,
        ),

        # Session lifetime
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),

        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.Column(
            "last_used_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        # Revocation
        sa.Column(
            "is_revoked",
            sa.Boolean(),
            server_default=sa.text("FALSE"),
            nullable=False,
        ),

        sa.Column(
            "revoked_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),

        sa.Column(
            "revoked_reason",
            sa.String(length=255),
            nullable=True,
        ),

        # Refresh-token rotation
        sa.Column(
            "replaced_by_session_id",
            sa.String(length=128),
            nullable=True,
        ),

        # Device information
        sa.Column(
            "device_name",
            sa.String(length=255),
            nullable=True,
        ),

        sa.Column(
            "user_agent",
            sa.String(length=1000),
            nullable=True,
        ),

        sa.Column(
            "ip_address",
            sa.String(length=64),
            nullable=True,
        ),

        # Primary key
        sa.PrimaryKeyConstraint("id"),

        # Foreign key
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),

        # Unique constraints
        sa.UniqueConstraint(
            "session_id",
            name="uq_auth_sessions_session_id",
        ),

        sa.UniqueConstraint(
            "refresh_token_hash",
            name="uq_auth_sessions_refresh_token_hash",
        ),
    )

    # ---------------------------------------------------------
    # Index: user_id
    # ---------------------------------------------------------
    op.create_index(
        "ix_auth_sessions_user_id",
        "auth_sessions",
        ["user_id"],
        unique=False,
    )

    # ---------------------------------------------------------
    # Index: expires_at
    # ---------------------------------------------------------
    op.create_index(
        "ix_auth_sessions_expires_at",
        "auth_sessions",
        ["expires_at"],
        unique=False,
    )

    # ---------------------------------------------------------
    # Composite index:
    # user_id + is_revoked
    # ---------------------------------------------------------
    op.create_index(
        "ix_auth_sessions_user_active",
        "auth_sessions",
        ["user_id", "is_revoked"],
        unique=False,
    )


def downgrade() -> None:
    # Remove indexes first
    op.drop_index(
        "ix_auth_sessions_user_active",
        table_name="auth_sessions",
    )

    op.drop_index(
        "ix_auth_sessions_expires_at",
        table_name="auth_sessions",
    )

    op.drop_index(
        "ix_auth_sessions_user_id",
        table_name="auth_sessions",
    )

    # Remove table
    op.drop_table("auth_sessions")