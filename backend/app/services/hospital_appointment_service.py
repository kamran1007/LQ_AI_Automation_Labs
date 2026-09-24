from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment_request import AppointmentRequest
from app.services.notification_service import (
    create_patient_appointment_notification,
    create_patient_proposal_notification,
)


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
        .order_by(AppointmentRequest.created_at.desc())
    )

    if doctor_id is not None:
        query = query.where(
            AppointmentRequest.doctor_id == doctor_id
        )

    result = await db.execute(query)

    return list(result.scalars().all())


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


async def accept_hospital_appointment_request(
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
    )

    result = await db.execute(query)

    appointment_request = result.scalar_one_or_none()

    if appointment_request is None:
        return None

    # Only pending requests can be accepted
    if appointment_request.status != "pending":
        return appointment_request

    appointment_request.status = "accepted"

    await db.commit()
    await db.refresh(appointment_request)

    # -----------------------------
    # PATIENT NOTIFICATION
    # -----------------------------
    await create_patient_appointment_notification(
        db=db,
        appointment_request=appointment_request,
        event_type="appointment_accepted",
        title="Appointment Accepted",
        message=(
            "Your appointment request has been accepted "
            "by the hospital."
        ),
    )

    return appointment_request


async def decline_hospital_appointment_request(
    db: AsyncSession,
    appointment_request_id: int,
    hospital_id: int,
    reason: str,
):
    query = (
        select(AppointmentRequest)
        .where(
            AppointmentRequest.id == appointment_request_id,
            AppointmentRequest.hospital_id == hospital_id,
        )
    )

    result = await db.execute(query)

    appointment_request = result.scalar_one_or_none()

    if appointment_request is None:
        return None

    # Only pending requests can be declined
    if appointment_request.status != "pending":
        return appointment_request

    appointment_request.status = "declined"
    appointment_request.decline_reason = reason

    await db.commit()
    await db.refresh(appointment_request)

    # -----------------------------
    # PATIENT NOTIFICATION
    # -----------------------------
    await create_patient_appointment_notification(
        db=db,
        appointment_request=appointment_request,
        event_type="appointment_declined",
        title="Appointment Declined",
        message=(
            f"Your appointment request has been declined. "
            f"Reason: {reason}"
        ),
    )

    return appointment_request


async def propose_hospital_appointment_time(
    db: AsyncSession,
    appointment_request_id: int,
    hospital_id: int,
    proposed_start_at,
    message: str | None = None,
):
    query = (
        select(AppointmentRequest)
        .where(
            AppointmentRequest.id == appointment_request_id,
            AppointmentRequest.hospital_id == hospital_id,
        )
    )

    result = await db.execute(query)

    appointment_request = result.scalar_one_or_none()

    if appointment_request is None:
        return None

    # Only pending requests can receive a proposal
    if appointment_request.status != "pending":
        return appointment_request

    appointment_request.status = "proposed"
    appointment_request.proposed_start_at = proposed_start_at
    appointment_request.proposal_message = message

    await db.commit()
    await db.refresh(appointment_request)

    # -----------------------------
    # PATIENT NOTIFICATION
    # -----------------------------
    await create_patient_proposal_notification(
        db=db,
        appointment_request=appointment_request,
        title="Alternative Appointment Time Proposed",
        message=(
            message
            or "The hospital has proposed an alternative appointment time."
        ),
    )

    return appointment_request