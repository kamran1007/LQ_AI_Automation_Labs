from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.appointment_request import AppointmentRequest
from app.models.notification import Notification
from app.services.websocket_manager import manager


# ============================================================
# HOSPITAL SIDE
# Create notification when patient creates appointment request
#
# Flow:
#
# Patient books appointment
#       ↓
# AppointmentRequest
#       ↓
# Notification DB
#       ↓
# Hospital WebSocket
# ============================================================

async def create_appointment_notification(
    db: AsyncSession,
    appointment_request,
    recipient_user_id: int | None = None,
):
    # --------------------------------------------------------
    # Reload appointment request with relationships
    # explicitly loaded.
    #
    # This avoids MissingGreenlet with AsyncSession.
    # --------------------------------------------------------

    result = await db.execute(
        select(AppointmentRequest)
        .where(
            AppointmentRequest.id == appointment_request.id
        )
        .options(
            selectinload(
                AppointmentRequest.patient
            ),
            selectinload(
                AppointmentRequest.doctor
            ),
            selectinload(
                AppointmentRequest.hospital
            ),
        )
    )

    appointment_request = result.scalar_one()

    # --------------------------------------------------------
    # Get names safely
    # --------------------------------------------------------

    patient_name = (
        appointment_request.patient.name
        if appointment_request.patient
        else f"Patient #{appointment_request.patient_id}"
    )

    doctor_name = (
        appointment_request.doctor.name
        if appointment_request.doctor
        else f"Doctor #{appointment_request.doctor_id}"
    )

    requested_at = (
        appointment_request.requested_start_at
    )

    formatted_date = requested_at.strftime(
        "%B %d, %Y"
    )

    formatted_time = requested_at.strftime(
        "%I:%M %p"
    )

    visit_reason = (
        appointment_request.visit_reason
        or "Not provided"
    )

    # --------------------------------------------------------
    # Notification content
    # --------------------------------------------------------

    title = "New Appointment Request"

    message = (
        f"{patient_name} requested an appointment "
        f"with {doctor_name} on "
        f"{formatted_date} at "
        f"{formatted_time}. "
        f"Reason: {visit_reason}."
    )

    # --------------------------------------------------------
    # Persistent notification
    # --------------------------------------------------------

    notification = Notification(
        recipient_user_id=recipient_user_id,
        hospital_id=appointment_request.hospital_id,
        appointment_request_id=appointment_request.id,
        type="appointment_request_created",
        title=title,
        message=message,
        is_read=False,
    )

    db.add(notification)

    await db.commit()
    await db.refresh(notification)

    # --------------------------------------------------------
    # Debug information
    # --------------------------------------------------------

    print(
        "======================================"
    )

    print(
        "NOTIFICATION CREATED:",
        notification.id,
    )

    print(
        "RECIPIENT USER ID:",
        notification.recipient_user_id,
    )

    print(
        "HOSPITAL ID:",
        notification.hospital_id,
    )

    print(
        "APPOINTMENT REQUEST ID:",
        notification.appointment_request_id,
    )

    print(
        "TYPE:",
        notification.type,
    )

    print(
        "TITLE:",
        notification.title,
    )

    print(
        "MESSAGE:",
        notification.message,
    )

    print(
        "======================================"
    )

    # --------------------------------------------------------
    # Real-time Hospital WebSocket notification
    # --------------------------------------------------------

    await manager.send_to_hospital(
        hospital_id=appointment_request.hospital_id,
        message={
            "event": "appointment_request_created",
            "data": {
                "notification_id": notification.id,
                "appointment_request_id": (
                    appointment_request.id
                ),
                "hospital_id": (
                    appointment_request.hospital_id
                ),
                "patient_id": (
                    appointment_request.patient_id
                ),
                "patient_name": patient_name,
                "doctor_id": (
                    appointment_request.doctor_id
                ),
                "doctor_name": doctor_name,
                "requested_start_at": (
                    requested_at.isoformat()
                ),
                "duration_minutes": (
                    appointment_request.duration_minutes
                ),
                "visit_reason": visit_reason,
                "patient_message": (
                    appointment_request.patient_message
                ),
                "status": appointment_request.status,
                "title": title,
                "message": message,
            },
        },
    )

    print(
        "HOSPITAL WEBSOCKET NOTIFICATION SENT:",
        appointment_request.hospital_id,
    )

    return notification


# ============================================================
# PATIENT SIDE
# Create notification + send real-time WebSocket event
#
# Used for:
#
# - appointment_accepted
# - appointment_declined
# - appointment_proposal_accepted
# - appointment_proposal_rejected
#
# ============================================================

async def create_patient_appointment_notification(
    db: AsyncSession,
    appointment_request: AppointmentRequest,
    event_type: str,
    title: str,
    message: str,
):
    # --------------------------------------------------------
    # Create persistent notification
    # --------------------------------------------------------

    notification = Notification(
        recipient_user_id=appointment_request.patient_id,
        hospital_id=appointment_request.hospital_id,
        appointment_request_id=appointment_request.id,
        type=event_type,
        title=title,
        message=message,
        is_read=False,
    )

    db.add(notification)

    await db.commit()
    await db.refresh(notification)

    # --------------------------------------------------------
    # Debug
    # --------------------------------------------------------

    print(
        "======================================"
    )

    print(
        "PATIENT NOTIFICATION CREATED:",
        notification.id,
    )

    print(
        "RECIPIENT PATIENT ID:",
        notification.recipient_user_id,
    )

    print(
        "HOSPITAL ID:",
        notification.hospital_id,
    )

    print(
        "APPOINTMENT REQUEST ID:",
        notification.appointment_request_id,
    )

    print(
        "TYPE:",
        notification.type,
    )

    print(
        "TITLE:",
        notification.title,
    )

    print(
        "MESSAGE:",
        notification.message,
    )

    print(
        "======================================"
    )

    # --------------------------------------------------------
    # Real-time Patient WebSocket
    # --------------------------------------------------------

    await manager.send_to_patient(
        patient_id=appointment_request.patient_id,
        message={
            "event": event_type,
            "data": {
                "notification_id": notification.id,
                "appointment_request_id": (
                    appointment_request.id
                ),
                "patient_id": (
                    appointment_request.patient_id
                ),
                "hospital_id": (
                    appointment_request.hospital_id
                ),
                "doctor_id": (
                    appointment_request.doctor_id
                ),
                "status": appointment_request.status,
                "title": title,
                "message": message,
            },
        },
    )

    print(
        "PATIENT WEBSOCKET NOTIFICATION SENT:",
        appointment_request.patient_id,
    )

    return notification


# ============================================================
# PATIENT SIDE - PROPOSED TIME
#
# Hospital proposes a different appointment time.
#
# This sends:
#
# 1. Persistent notification
# 2. Real-time WebSocket event
# 3. proposed_start_at as structured data
#
# ============================================================

async def create_patient_proposal_notification(
    db: AsyncSession,
    appointment_request: AppointmentRequest,
    title: str,
    message: str,
):
    # --------------------------------------------------------
    # Make sure a proposed time actually exists
    # --------------------------------------------------------

    proposed_start_at = (
        appointment_request.proposed_start_at
    )

    if proposed_start_at is None:
        raise ValueError(
            "Cannot create proposal notification: "
            "proposed_start_at is missing."
        )

    # --------------------------------------------------------
    # Persistent notification
    # --------------------------------------------------------

    notification = Notification(
        recipient_user_id=appointment_request.patient_id,
        hospital_id=appointment_request.hospital_id,
        appointment_request_id=appointment_request.id,
        type="appointment_time_proposed",
        title=title,
        message=message,
        is_read=False,
    )

    db.add(notification)

    await db.commit()
    await db.refresh(notification)

    # --------------------------------------------------------
    # Debug
    # --------------------------------------------------------

    print(
        "======================================"
    )

    print(
        "PATIENT PROPOSAL NOTIFICATION CREATED:",
        notification.id,
    )

    print(
        "RECIPIENT PATIENT ID:",
        notification.recipient_user_id,
    )

    print(
        "APPOINTMENT REQUEST ID:",
        notification.appointment_request_id,
    )

    print(
        "PROPOSED START AT:",
        proposed_start_at,
    )

    print(
        "TYPE:",
        notification.type,
    )

    print(
        "TITLE:",
        notification.title,
    )

    print(
        "MESSAGE:",
        notification.message,
    )

    print(
        "======================================"
    )

    # --------------------------------------------------------
    # Real-time Patient WebSocket
    # --------------------------------------------------------

    await manager.send_to_patient(
        patient_id=appointment_request.patient_id,
        message={
            "event": "appointment_time_proposed",
            "data": {
                "notification_id": notification.id,
                "appointment_request_id": (
                    appointment_request.id
                ),
                "patient_id": (
                    appointment_request.patient_id
                ),
                "hospital_id": (
                    appointment_request.hospital_id
                ),
                "doctor_id": (
                    appointment_request.doctor_id
                ),
                "status": appointment_request.status,
                "proposed_start_at": (
                    proposed_start_at.isoformat()
                ),
                "title": title,
                "message": message,
            },
        },
    )

    print(
        "PATIENT PROPOSAL WEBSOCKET SENT:",
        appointment_request.patient_id,
    )

    return notification