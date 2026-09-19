from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment_request import AppointmentRequest


async def create_appointment_request(
    db: AsyncSession,
    patient_id: int,
    hospital_id: int,
    doctor_id: int,
    requested_start_at: datetime,
    conversation_id: int | None = None,
    duration_minutes: int = 30,
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
        status="pending",
        expires_at=datetime.now().astimezone() + timedelta(hours=24),
    )

    db.add(appointment_request)

    await db.commit()
    await db.refresh(appointment_request)

    return appointment_request