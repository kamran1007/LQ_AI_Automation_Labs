from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment_request import AppointmentRequest


# ============================================================
# STEP 1
# Get appointment requests for a hospital
# Supports:
# - hospital_id
# - doctor_id
# - status
# ============================================================

async def get_hospital_appointment_requests(
    db: AsyncSession,
    hospital_id: int,
    doctor_id: int | None = None,
    status: str = "pending",
):
    query = (
        select(AppointmentRequest)
        .where(
            AppointmentRequest.hospital_id == hospital_id,
            AppointmentRequest.status == status,
        )
        .options(
            selectinload(AppointmentRequest.patient),
            selectinload(AppointmentRequest.doctor),
            selectinload(AppointmentRequest.hospital),
        )
        .order_by(
            AppointmentRequest.created_at.desc()
        )
    )

    if doctor_id is not None:
        query = query.where(
            AppointmentRequest.doctor_id == doctor_id
        )

    result = await db.execute(query)

    return list(result.scalars().all())


# ============================================================
# STEP 2
# Get ONE appointment request
# ============================================================

async def get_hospital_appointment_request(
    db: AsyncSession,
    appointment_request_id: int,
    hospital_id: int,
):
    query = (
        select(AppointmentRequest)
        .where(
            AppointmentRequest.id == appointment_request_id,
            AppointmentRequest.hospital_id == hospital_id,
        )
        .options(
            selectinload(AppointmentRequest.patient),
            selectinload(AppointmentRequest.doctor),
            selectinload(AppointmentRequest.hospital),
        )
    )

    result = await db.execute(query)

    return result.scalar_one_or_none()