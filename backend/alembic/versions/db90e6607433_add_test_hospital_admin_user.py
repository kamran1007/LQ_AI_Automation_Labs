"""add test hospital admin user

Revision ID: db90e6607433
Revises: a3ad99a188eb
Create Date: 2026-10-03 11:17:43.191347

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db90e6607433'
down_revision: Union[str, Sequence[str], None] = 'a3ad99a188eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TEST_MOBILE = "9430055724"
TEST_NAME = "LightningQ Test Admin"
HOSPITAL_NAME = "LightningQ Test Hospital"
ROLE_NAME = "hospital_admin"


def upgrade() -> None:

    connection = op.get_bind()

    # ======================================================
    # 1. Find hospital_admin role
    # ======================================================

    role = connection.execute(
        sa.text("""
            SELECT id
            FROM roles
            WHERE name = :role_name
            LIMIT 1
        """),
        {
            "role_name": ROLE_NAME,
        },
    ).fetchone()

    if role is None:
        raise RuntimeError(
            f"Role '{ROLE_NAME}' does not exist"
        )

    role_id = role.id

    # ======================================================
    # 2. Find test hospital
    # ======================================================

    hospital = connection.execute(
        sa.text("""
            SELECT id
            FROM hospitals
            WHERE name = :hospital_name
            LIMIT 1
        """),
        {
            "hospital_name": HOSPITAL_NAME,
        },
    ).fetchone()

    # ======================================================
    # 3. Create test hospital if it doesn't exist
    # ======================================================

    if hospital is None:

        result = connection.execute(
            sa.text("""
                INSERT INTO hospitals (
                    name,
                    phone,
                    email,
                    address,
                    city,
                    state,
                    country,
                    timezone,
                    is_verified,
                    is_active,
                    created_at,
                    updated_at
                )
                VALUES (
                    :name,
                    :phone,
                    :email,
                    :address,
                    :city,
                    :state,
                    :country,
                    :timezone,
                    TRUE,
                    TRUE,
                    NOW(),
                    NOW()
                )
                RETURNING id
            """),
            {
                "name": HOSPITAL_NAME,
                "phone": "9999900000",
                "email": "test@lightningq.local",
                "address": "123 Test Street",
                "city": "Test City",
                "state": "Test State",
                "country": "India",
                "timezone": "Asia/Kolkata",
            },
        )

        hospital_id = result.scalar_one()

    else:

        hospital_id = hospital.id

    # ======================================================
    # 4. Find test user
    # ======================================================

    existing_user = connection.execute(
        sa.text("""
            SELECT id
            FROM users
            WHERE mobile = :mobile
            LIMIT 1
        """),
        {
            "mobile": TEST_MOBILE,
        },
    ).fetchone()

    # ======================================================
    # 5. Create test user
    # ======================================================

    if existing_user is None:

        result = connection.execute(
            sa.text("""
                INSERT INTO users (
                    mobile,
                    name,
                    email,
                    is_verified,
                    is_active,
                    created_at
                )
                VALUES (
                    :mobile,
                    :name,
                    :email,
                    TRUE,
                    TRUE,
                    NOW()
                )
                RETURNING id
            """),
            {
                "mobile": TEST_MOBILE,
                "name": TEST_NAME,
                "email": "hospital-admin-test@lightningq.local",
            },
        )

        user_id = result.scalar_one()

    else:

        user_id = existing_user.id

    # ======================================================
    # 6. Check user + role + hospital assignment
    # ======================================================

    existing_assignment = connection.execute(
        sa.text("""
            SELECT id
            FROM user_roles
            WHERE user_id = :user_id
              AND role_id = :role_id
              AND hospital_id = :hospital_id
            LIMIT 1
        """),
        {
            "user_id": user_id,
            "role_id": role_id,
            "hospital_id": hospital_id,
        },
    ).fetchone()

    # ======================================================
    # 7. Create hospital authorization
    # ======================================================

    if existing_assignment is None:

        connection.execute(
            sa.text("""
                INSERT INTO user_roles (
                    user_id,
                    role_id,
                    hospital_id,
                    created_at
                )
                VALUES (
                    :user_id,
                    :role_id,
                    :hospital_id,
                    NOW()
                )
            """),
            {
                "user_id": user_id,
                "role_id": role_id,
                "hospital_id": hospital_id,
            },
        )


def downgrade() -> None:

    connection = op.get_bind()

    # ======================================================
    # Find test user
    # ======================================================

    user = connection.execute(
        sa.text("""
            SELECT id
            FROM users
            WHERE mobile = :mobile
            LIMIT 1
        """),
        {
            "mobile": TEST_MOBILE,
        },
    ).fetchone()

    if user is None:
        return

    # ======================================================
    # Remove user-role assignment
    # ======================================================

    connection.execute(
        sa.text("""
            DELETE FROM user_roles
            WHERE user_id = :user_id
        """),
        {
            "user_id": user.id,
        },
    )

    # ======================================================
    # Remove test user
    # ======================================================

    connection.execute(
        sa.text("""
            DELETE FROM users
            WHERE id = :user_id
        """),
        {
            "user_id": user.id,
        },
    )

    # ======================================================
    # Remove test hospital
    # ======================================================

    connection.execute(
        sa.text("""
            DELETE FROM hospitals
            WHERE name = :hospital_name
        """),
        {
            "hospital_name": HOSPITAL_NAME,
        },
    )