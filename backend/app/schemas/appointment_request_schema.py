from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class AppointmentRequestCreate(BaseModel):
    patient_id: int = Field(gt=0)
    hospital_id: int = Field(gt=0)
    doctor_id: int = Field(gt=0)

    conversation_id: int | None = Field(
        default=None,
        gt=0,
    )

    requested_start_at: datetime

    duration_minutes: int = Field(
        default=30,
        gt=0,
        le=480,
    )

    patient_message: str | None = None

    expires_at: datetime | None = None


class AppointmentRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    hospital_id: int
    doctor_id: int
    conversation_id: int | None
    requested_start_at: datetime
    duration_minutes: int
    patient_message: str | None
    status: str
    expires_at: datetime | None
    created_at: datetime
    updated_at: datetime