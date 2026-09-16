"""add appointment workflow models

Revision ID: 713dfd845718
Revises:
Create Date: 2026-09-15 21:30:54.248314
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic.
revision: str = "713dfd845718"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # ---------------------------------------------------------
    # 1. Create hospitals
    # ---------------------------------------------------------
    op.create_table(
        "hospitals",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("state", sa.String(length=100), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_hospitals_city",
        "hospitals",
        ["city"],
        unique=False,
    )

    op.create_index(
        "ix_hospitals_name",
        "hospitals",
        ["name"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 2. Create roles
    # ---------------------------------------------------------
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_roles_name",
        "roles",
        ["name"],
        unique=True,
    )

    # ---------------------------------------------------------
    # 3. Create doctors
    # ---------------------------------------------------------
    op.create_table(
        "doctors",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("hospital_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "specialization",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "qualification",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["hospital_id"],
            ["hospitals.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_doctors_hospital_id",
        "doctors",
        ["hospital_id"],
        unique=False,
    )

    op.create_index(
        "ix_doctors_name",
        "doctors",
        ["name"],
        unique=False,
    )

    op.create_index(
        "ix_doctors_specialization",
        "doctors",
        ["specialization"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 4. Create appointment_requests
    # ---------------------------------------------------------
    op.create_table(
        "appointment_requests",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("patient_id", sa.Integer(), nullable=False),
        sa.Column("hospital_id", sa.Integer(), nullable=False),
        sa.Column("doctor_id", sa.Integer(), nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=True),
        sa.Column(
            "requested_start_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("patient_message", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["doctor_id"],
            ["doctors.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["hospital_id"],
            ["hospitals.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["patient_id"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_appointment_requests_conversation_id",
        "appointment_requests",
        ["conversation_id"],
        unique=False,
    )

    op.create_index(
        "ix_appointment_requests_doctor_id",
        "appointment_requests",
        ["doctor_id"],
        unique=False,
    )

    op.create_index(
        "ix_appointment_requests_hospital_id",
        "appointment_requests",
        ["hospital_id"],
        unique=False,
    )

    op.create_index(
        "ix_appointment_requests_patient_id",
        "appointment_requests",
        ["patient_id"],
        unique=False,
    )

    op.create_index(
        "ix_appointment_requests_status",
        "appointment_requests",
        ["status"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 5. Create appointment_proposals
    # ---------------------------------------------------------
    op.create_table(
        "appointment_proposals",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "appointment_request_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "proposed_by_user_id",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column(
            "proposed_start_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["appointment_request_id"],
            ["appointment_requests.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["proposed_by_user_id"],
            ["users.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_appointment_proposals_appointment_request_id",
        "appointment_proposals",
        ["appointment_request_id"],
        unique=False,
    )

    op.create_index(
        "ix_appointment_proposals_proposed_by_user_id",
        "appointment_proposals",
        ["proposed_by_user_id"],
        unique=False,
    )

    op.create_index(
        "ix_appointment_proposals_status",
        "appointment_proposals",
        ["status"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 6. Create appointments
    # ---------------------------------------------------------
    op.create_table(
        "appointments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "appointment_request_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "appointment_proposal_id",
            sa.Integer(),
            nullable=True,
        ),
        sa.Column("patient_id", sa.Integer(), nullable=False),
        sa.Column("hospital_id", sa.Integer(), nullable=False),
        sa.Column("doctor_id", sa.Integer(), nullable=False),
        sa.Column(
            "confirmed_start_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("confirmation_sent", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["appointment_proposal_id"],
            ["appointment_proposals.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["appointment_request_id"],
            ["appointment_requests.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["doctor_id"],
            ["doctors.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["hospital_id"],
            ["hospitals.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["patient_id"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_appointments_appointment_proposal_id",
        "appointments",
        ["appointment_proposal_id"],
        unique=False,
    )

    op.create_index(
        "ix_appointments_appointment_request_id",
        "appointments",
        ["appointment_request_id"],
        unique=False,
    )

    op.create_index(
        "ix_appointments_confirmed_start_at",
        "appointments",
        ["confirmed_start_at"],
        unique=False,
    )

    op.create_index(
        "ix_appointments_doctor_id",
        "appointments",
        ["doctor_id"],
        unique=False,
    )

    op.create_index(
        "ix_appointments_hospital_id",
        "appointments",
        ["hospital_id"],
        unique=False,
    )

    op.create_index(
        "ix_appointments_patient_id",
        "appointments",
        ["patient_id"],
        unique=False,
    )

    op.create_index(
        "ix_appointments_status",
        "appointments",
        ["status"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 7. Safely convert conversations.user_id
    #    Existing value: "kamran"
    #    Matching users.id: 1
    # ---------------------------------------------------------

    op.add_column(
        "conversations",
        sa.Column(
            "user_id_new",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE conversations
        SET user_id_new = 1
        WHERE LOWER(user_id) = 'kamran'
        """
    )

    # Stop the migration if any old value could not be mapped.
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM conversations
                WHERE user_id_new IS NULL
            ) THEN
                RAISE EXCEPTION
                    'Some conversations.user_id values could not be mapped to users.id';
            END IF;
        END
        $$;
        """
    )

    op.drop_column(
        "conversations",
        "user_id",
    )

    op.alter_column(
        "conversations",
        "user_id_new",
        new_column_name="user_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.create_foreign_key(
        "fk_conversations_user_id_users",
        "conversations",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # ---------------------------------------------------------
    # 8. Add users.email
    # ---------------------------------------------------------
    op.add_column(
        "users",
        sa.Column(
            "email",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.create_unique_constraint(
        "uq_users_email",
        "users",
        ["email"],
    )


def downgrade() -> None:
    """Downgrade schema."""

    # ---------------------------------------------------------
    # 1. Remove users.email
    # ---------------------------------------------------------
    op.drop_constraint(
        "uq_users_email",
        "users",
        type_="unique",
    )

    op.drop_column(
        "users",
        "email",
    )

    # ---------------------------------------------------------
    # 2. Restore conversations.user_id to text
    # ---------------------------------------------------------
    op.drop_constraint(
        "fk_conversations_user_id_users",
        "conversations",
        type_="foreignkey",
    )

    op.add_column(
        "conversations",
        sa.Column(
            "user_id_old",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE conversations
        SET user_id_old = LOWER(users.name)
        FROM users
        WHERE conversations.user_id = users.id
        """
    )

    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM conversations
                WHERE user_id_old IS NULL
            ) THEN
                RAISE EXCEPTION
                    'Some conversations.user_id values could not be converted back to text';
            END IF;
        END
        $$;
        """
    )

    op.drop_column(
        "conversations",
        "user_id",
    )

    op.alter_column(
        "conversations",
        "user_id_old",
        new_column_name="user_id",
        existing_type=sa.String(length=255),
        nullable=False,
    )

    # ---------------------------------------------------------
    # 3. Remove appointment tables
    # ---------------------------------------------------------
    op.drop_index(
        "ix_appointments_status",
        table_name="appointments",
    )
    op.drop_index(
        "ix_appointments_patient_id",
        table_name="appointments",
    )
    op.drop_index(
        "ix_appointments_hospital_id",
        table_name="appointments",
    )
    op.drop_index(
        "ix_appointments_doctor_id",
        table_name="appointments",
    )
    op.drop_index(
        "ix_appointments_confirmed_start_at",
        table_name="appointments",
    )
    op.drop_index(
        "ix_appointments_appointment_request_id",
        table_name="appointments",
    )
    op.drop_index(
        "ix_appointments_appointment_proposal_id",
        table_name="appointments",
    )
    op.drop_table("appointments")

    op.drop_index(
        "ix_appointment_proposals_status",
        table_name="appointment_proposals",
    )
    op.drop_index(
        "ix_appointment_proposals_proposed_by_user_id",
        table_name="appointment_proposals",
    )
    op.drop_index(
        "ix_appointment_proposals_appointment_request_id",
        table_name="appointment_proposals",
    )
    op.drop_table("appointment_proposals")

    op.drop_index(
        "ix_appointment_requests_status",
        table_name="appointment_requests",
    )
    op.drop_index(
        "ix_appointment_requests_patient_id",
        table_name="appointment_requests",
    )
    op.drop_index(
        "ix_appointment_requests_hospital_id",
        table_name="appointment_requests",
    )
    op.drop_index(
        "ix_appointment_requests_doctor_id",
        table_name="appointment_requests",
    )
    op.drop_index(
        "ix_appointment_requests_conversation_id",
        table_name="appointment_requests",
    )
    op.drop_table("appointment_requests")

    op.drop_index(
        "ix_doctors_specialization",
        table_name="doctors",
    )
    op.drop_index(
        "ix_doctors_name",
        table_name="doctors",
    )
    op.drop_index(
        "ix_doctors_hospital_id",
        table_name="doctors",
    )
    op.drop_table("doctors")

    op.drop_index(
        "ix_roles_name",
        table_name="roles",
    )
    op.drop_table("roles")

    op.drop_index(
        "ix_hospitals_name",
        table_name="hospitals",
    )
    op.drop_index(
        "ix_hospitals_city",
        table_name="hospitals",
    )
    op.drop_table("hospitals")