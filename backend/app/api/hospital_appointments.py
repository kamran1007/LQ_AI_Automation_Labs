from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from app.schemas.hospital_appointment_schema import (
    HospitalAppointmentRequestListResponse,
    HospitalAppointmentRequestDetailApiResponse,
    HospitalAppointmentRequestActionResponse,
    AppointmentDeclineRequest,
    AppointmentProposeRequest,
)

from app.services.hospital_appointment_service import (
    get_hospital_appointment_requests,
    get_hospital_appointment_request,
    accept_hospital_appointment_request,
    decline_hospital_appointment_request,
    propose_hospital_appointment_time,
)

router = APIRouter(
    prefix="/hospital",
    tags=["Hospital"],
)


@router.get(
    "/appointment-requests",
    response_model=HospitalAppointmentRequestListResponse,
)
async def get_appointment_requests(
    hospital_id: int = Query(...),
    doctor_id: int | None = Query(None),
    status: str = Query("pending"),
    db: AsyncSession = Depends(get_db),
):
    appointment_requests = await get_hospital_appointment_requests(
        db=db,
        hospital_id=hospital_id,
        doctor_id=doctor_id,
        status=status,
    )

    return {
        "success": True,
        "data": appointment_requests,
    }

@router.get(
    "/appointment-requests/{appointment_request_id}",
    response_model=HospitalAppointmentRequestDetailApiResponse,
)
async def get_appointment_request(
    appointment_request_id: int,
    hospital_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    appointment_request = await get_hospital_appointment_request(
        db=db,
        appointment_request_id=appointment_request_id,
        hospital_id=hospital_id,
    )

    if appointment_request is None:
        raise HTTPException(
            status_code=404,
            detail="Appointment request not found.",
        )

    return {
        "success": True,
        "data": appointment_request,
    }

@router.post(
    "/appointment-requests/{appointment_request_id}/accept",
    response_model=HospitalAppointmentRequestActionResponse,
)
async def accept_appointment_request(
    appointment_request_id: int,
    hospital_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    appointment_request = await accept_hospital_appointment_request(
        db=db,
        appointment_request_id=appointment_request_id,
        hospital_id=hospital_id,
    )

    if appointment_request is None:
        raise HTTPException(
            status_code=404,
            detail="Appointment request not found.",
        )

    return {
        "success": True,
        "message": "Appointment request accepted.",
        "data": appointment_request,
    }

@router.post(
    "/appointment-requests/{appointment_request_id}/accept"
)
async def accept_appointment(
    appointment_request_id: int,
    hospital_id: int,
    db: AsyncSession = Depends(get_db),
):
    appointment_request = (
        await accept_hospital_appointment_request(
            db=db,
            appointment_request_id=appointment_request_id,
            hospital_id=hospital_id,
        )
    )

    if appointment_request is None:
        raise HTTPException(
            status_code=404,
            detail="Appointment request not found.",
        )

    return {
        "success": True,
        "message": "Appointment request accepted.",
        "data": appointment_request,
    }

@router.post(
    "/appointment-requests/{appointment_request_id}/decline"
)
async def decline_appointment(
    appointment_request_id: int,
    request: AppointmentDeclineRequest,
    hospital_id: int,
    db: AsyncSession = Depends(get_db),
):
    appointment_request = (
        await decline_hospital_appointment_request(
            db=db,
            appointment_request_id=appointment_request_id,
            hospital_id=hospital_id,
            reason=request.reason,
        )
    )

    if appointment_request is None:
        raise HTTPException(
            status_code=404,
            detail="Appointment request not found.",
        )

    return {
        "success": True,
        "message": "Appointment request declined.",
        "data": appointment_request,
    }

@router.post(
    "/appointment-requests/{appointment_request_id}/propose"
)
async def propose_appointment(
    appointment_request_id: int,
    request: AppointmentProposeRequest,
    hospital_id: int,
    db: AsyncSession = Depends(get_db),
):
    appointment_request = (
        await propose_hospital_appointment_time(
            db=db,
            appointment_request_id=appointment_request_id,
            hospital_id=hospital_id,
            proposed_start_at=request.proposed_start_at,
            message=request.message,
        )
    )

    if appointment_request is None:
        raise HTTPException(
            status_code=404,
            detail="Appointment request not found.",
        )

    return {
        "success": True,
        "message": (
            "Alternative appointment time proposed."
        ),
        "data": appointment_request,
    }