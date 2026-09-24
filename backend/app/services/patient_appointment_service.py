from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.appointment_request import AppointmentRequest
from app.models.notification import Notification
from app.services.websocket_manager import manager


async def accept_appointment_proposal(
    db: AsyncSession,
    appointment_request_id: int,
    patient_id: int,
):
    query = (
    select(AppointmentRequest)
    .where(
        AppointmentRequest.id == appointment_request_id,
        AppointmentRequest.patient_id == patient_id,
    )
    .options(
        selectinload(AppointmentRequest.patient)
        )
    )

    result = await db.execute(query)
    appointment_request = result.scalar_one_or_none()
    patient_name = (
    appointment_request.patient.name
    if appointment_request.patient
    else f"Patient {appointment_request.patient_id}"
)

    if appointment_request is None:
        return None, "Appointment request not found."

    if appointment_request.status != "proposed":
        return (
            appointment_request,
            "Only proposed appointments can be accepted.",
        )

    if appointment_request.proposed_start_at is None:
        return (
            appointment_request,
            "No proposed appointment time exists.",
        )

    # The proposed time becomes the confirmed appointment time
    appointment_request.requested_start_at = (
        appointment_request.proposed_start_at
    )

    appointment_request.status = "accepted"

    await db.commit()
    await db.refresh(appointment_request)

    # -----------------------------
    # NOTIFICATION FOR HOSPITAL
    # -----------------------------

    notification = Notification(
        recipient_user_id=None,
        hospital_id=appointment_request.hospital_id,
        appointment_request_id=appointment_request.id,
        type="appointment_proposal_accepted",
        title="Appointment Proposal Accepted",
            message=(
            f"{patient_name} accepted the proposed "
            f"appointment time."
        ),
        is_read=False,
    )

    db.add(notification)

    await db.commit()
    await db.refresh(notification)

    # -----------------------------
    # HOSPITAL WEBSOCKET
    # -----------------------------

    await manager.send_to_hospital(
        hospital_id=appointment_request.hospital_id,
        message={
            "event": "appointment_proposal_accepted",
            "data": {
                "notification_id": notification.id,
                "appointment_request_id": appointment_request.id,
                "patient_name": patient_name,
                "hospital_id": appointment_request.hospital_id,
                "doctor_id": appointment_request.doctor_id,
                "status": appointment_request.status,
                "confirmed_start_at": (
                    appointment_request.requested_start_at.isoformat()
                ),
                "title": notification.title,
                "message": notification.message,
            },
        },
    )

    return appointment_request, None


async def reject_appointment_proposal(
    db: AsyncSession,
    appointment_request_id: int,
    patient_id: int,
    reason: str | None = None,
):
    query = (
        select(AppointmentRequest)
        .where(
            AppointmentRequest.id == appointment_request_id,
            AppointmentRequest.patient_id == patient_id,
        )
    )

    result = await db.execute(query)
    appointment_request = result.scalar_one_or_none()

    if appointment_request is None:
        return None, "Appointment request not found."

    if appointment_request.status != "proposed":
        return (
            appointment_request,
            "Only proposed appointments can be rejected.",
        )

    # Return to pending so hospital can propose another time
    appointment_request.status = "pending"

    await db.commit()
    await db.refresh(appointment_request)

    rejection_reason = (
        reason
        or "Patient rejected the proposed appointment time."
    )

    # -----------------------------
    # NOTIFICATION FOR HOSPITAL
    # -----------------------------

    notification = Notification(
        recipient_user_id=None,
        hospital_id=appointment_request.hospital_id,
        appointment_request_id=appointment_request.id,
        type="appointment_proposal_rejected",
        title="Appointment Proposal Rejected",
        message=(
            f"Patient rejected the proposed appointment time. "
            f"Reason: {rejection_reason}"
        ),
        is_read=False,
    )

    db.add(notification)

    await db.commit()
    await db.refresh(notification)

    # -----------------------------
    # HOSPITAL WEBSOCKET
    # -----------------------------

    await manager.send_to_hospital(
        hospital_id=appointment_request.hospital_id,
        message={
            "event": "appointment_proposal_rejected",
            "data": {
                "notification_id": notification.id,
                "appointment_request_id": appointment_request.id,
                "patient_id": appointment_request.patient_id,
                "hospital_id": appointment_request.hospital_id,
                "doctor_id": appointment_request.doctor_id,
                "status": appointment_request.status,
                "reason": rejection_reason,
                "title": notification.title,
                "message": notification.message,
            },
        },
    )

    return appointment_request, None