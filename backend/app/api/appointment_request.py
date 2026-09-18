from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.appointment_request import AppointmentRequest
from app.schemas.appointment_request_schema import (
    AppointmentRequestCreate,
    AppointmentRequestResponse,
)


router = APIRouter(
    prefix="/appointment-requests",
    tags=["Appointment Requests"],
)


@router.post(
    "/",
    response_model=AppointmentRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_appointment_request(
    request: AppointmentRequestCreate,
    db: AsyncSession = Depends(get_db),
):
    appointment_request = AppointmentRequest(
        patient_id=request.patient_id,
        hospital_id=request.hospital_id,
        doctor_id=request.doctor_id,
        conversation_id=request.conversation_id,
        requested_start_at=request.requested_start_at,
        duration_minutes=request.duration_minutes,
        patient_message=request.patient_message,
        expires_at=request.expires_at,
    )

    db.add(appointment_request)

    try:
        await db.commit()
        await db.refresh(appointment_request)

    except IntegrityError:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid patient_id, hospital_id, doctor_id, "
                "or conversation_id."
            ),
        )

    return appointment_request