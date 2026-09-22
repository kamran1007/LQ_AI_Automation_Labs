from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment_request import AppointmentRequest
from app.services.websocket_manager import manager
from app.services.notification_service import (
    create_appointment_notification,
)


async def create_appointment_request(
    db: AsyncSession,
    patient_id: int,
    hospital_id: int,
    doctor_id: int,
    requested_start_at: datetime,
    conversation_id: int | None = None,
    duration_minutes: int = 30,
    visit_reason: str | None = None,
    patient_message: str | None = None,
):
    appointment_request = AppointmentRequest(
        patient_id=patient_id,
        hospital_id=hospital_id,
        doctor_id=doctor_id,
        conversation_id=conversation_id,
        requested_start_at=requested_start_at,
        duration_minutes=duration_minutes,
        patient_message=patient_message,
        visit_reason=visit_reason,
        status="pending",
        expires_at=(
            datetime.now().astimezone()
            + timedelta(hours=24)
        ),
    )

    db.add(appointment_request)

    await db.commit()
    await db.refresh(appointment_request)
    
    await create_appointment_notification(
    db=db,
    appointment_request=appointment_request,
    )

    print(
        "APPOINTMENT REQUEST CREATED:",
        appointment_request.id,
    )
    # ------------------------------------------
    # REAL-TIME HOSPITAL NOTIFICATION
    # ------------------------------------------

    await manager.send_to_hospital(
        hospital_id=appointment_request.hospital_id,
        message={
            "event": "appointment_request_created",
            "data": {
                "appointment_request_id": appointment_request.id,
                "patient_id": appointment_request.patient_id,
                "hospital_id": appointment_request.hospital_id,
                "doctor_id": appointment_request.doctor_id,
                "requested_start_at": (
                    appointment_request
                    .requested_start_at
                    .isoformat()
                ),
                "duration_minutes": (
                    appointment_request.duration_minutes
                ),
                "visit_reason": (
                    appointment_request.visit_reason
                ),
                "patient_message": (
                    appointment_request.patient_message
                ),
                "status": appointment_request.status,
                "created_at": (
                    appointment_request.created_at
                    .isoformat()
                ),
            },
        },
    )

    print(
        "HOSPITAL WEBSOCKET NOTIFICATION SENT:",
        appointment_request.hospital_id,
    )

    return appointment_request