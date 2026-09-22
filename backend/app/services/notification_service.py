from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.services.websocket_manager import manager


async def create_appointment_notification(
    db: AsyncSession,
    appointment_request,
):
    notification = Notification(
        recipient_user_id=None,
        hospital_id=appointment_request.hospital_id,
        appointment_request_id=appointment_request.id,
        type="appointment_request",
        title="New Appointment Request",
        message=(
            "New appointment request received."
        ),
        is_read=False,
    )

    db.add(notification)

    await db.commit()
    await db.refresh(notification)

    print(
        "NOTIFICATION CREATED:",
        notification.id,
    )

    # -----------------------------------------
    # REAL-TIME HOSPITAL NOTIFICATION
    # -----------------------------------------

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
                "doctor_id": (
                    appointment_request.doctor_id
                ),
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
        "WEBSOCKET NOTIFICATION SENT:",
        appointment_request.hospital_id,
    )

    return notification