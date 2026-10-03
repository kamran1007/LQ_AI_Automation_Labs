"""restore missing auth sessions table

Revision ID: 17252b10610f
Revises: db90e6607433
Create Date: 2026-10-03
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "17252b10610f"
down_revision: Union[str, Sequence[str], None] = "db90e6607433"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # ---------------------------------------------------------
    # Create auth_sessions table
    # ---------------------------------------------------------

    op.create_table(
        "auth_sessions",

        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),

        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),

        sa.Column(
            "session_id",
            sa.String(length=128),
            nullable=False,
        ),

        sa.Column(
            "refresh_token_hash",
            sa.String(length=255),
            nullable=False,
        ),

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

        sa.Column(
            "replaced_by_session_id",
            sa.String(length=128),
            nullable=True,
        ),

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

        sa.PrimaryKeyConstraint("id"),

        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),

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
    # Indexes
    # ---------------------------------------------------------

    op.create_index(
        "ix_auth_sessions_user_id",
        "auth_sessions",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        "ix_auth_sessions_expires_at",
        "auth_sessions",
        ["expires_at"],
        unique=False,
    )

    op.create_index(
        "ix_auth_sessions_user_active",
        "auth_sessions",
        ["user_id", "is_revoked"],
        unique=False,
    )


def downgrade() -> None:

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

    op.drop_table("auth_sessions")