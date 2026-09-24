from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.patient_appointment import (
    AppointmentProposalRejectRequest,
)
from app.services.patient_appointment_service import (
    accept_appointment_proposal,
    reject_appointment_proposal,
)


router = APIRouter(
    prefix="/patient",
    tags=["Patient Appointments"],
)


@router.post(
    "/appointment-requests/{appointment_request_id}/proposal/accept"
)
async def accept_proposal(
    appointment_request_id: int,
    patient_id: int,
    db: AsyncSession = Depends(get_db),
):
    appointment_request, error = await accept_appointment_proposal(
        db=db,
        appointment_request_id=appointment_request_id,
        patient_id=patient_id,
    )

    if appointment_request is None:
        raise HTTPException(
            status_code=404,
            detail=error,
        )

    if error:
        raise HTTPException(
            status_code=409,
            detail=error,
        )

    return {
        "success": True,
        "message": "Proposed appointment time accepted.",
        "data": {
            "appointment_request_id": appointment_request.id,
            "status": appointment_request.status,
            "confirmed_start_at": (
                appointment_request.requested_start_at.isoformat()
            ),
            "doctor_id": appointment_request.doctor_id,
            "hospital_id": appointment_request.hospital_id,
            "patient_id": appointment_request.patient_id,
        },
    }


@router.post(
    "/appointment-requests/{appointment_request_id}/proposal/reject"
)
async def reject_proposal(
    appointment_request_id: int,
    patient_id: int,
    request: AppointmentProposalRejectRequest,
    db: AsyncSession = Depends(get_db),
):
    appointment_request, error = await reject_appointment_proposal(
        db=db,
        appointment_request_id=appointment_request_id,
        patient_id=patient_id,
        reason=request.reason,
    )

    if appointment_request is None:
        raise HTTPException(
            status_code=404,
            detail=error,
        )

    if error:
        raise HTTPException(
            status_code=409,
            detail=error,
        )

    return {
        "success": True,
        "message": "Proposed appointment time rejected.",
        "data": {
            "appointment_request_id": appointment_request.id,
            "status": appointment_request.status,
            "patient_id": appointment_request.patient_id,
            "doctor_id": appointment_request.doctor_id,
            "hospital_id": appointment_request.hospital_id,
        },
    }