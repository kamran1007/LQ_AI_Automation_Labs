from datetime import datetime

from pydantic import BaseModel


# -----------------------------
# Patient
# -----------------------------

class PatientInfo(BaseModel):
    id: int
    name: str


# -----------------------------
# Doctor
# -----------------------------

class DoctorInfo(BaseModel):
    id: int
    name: str
    specialization: str | None = None


# -----------------------------
# Hospital
# -----------------------------

class HospitalInfo(BaseModel):
    id: int
    name: str


# -----------------------------
# Step 1
# Hospital appointment list
# -----------------------------

class HospitalAppointmentRequestResponse(BaseModel):
    id: int
    patient_id: int
    hospital_id: int
    doctor_id: int

    requested_start_at: datetime
    duration_minutes: int

    visit_reason: str | None = None
    patient_note: str | None = None

    status: str

    class Config:
        from_attributes = True


class HospitalAppointmentRequestListResponse(BaseModel):
    success: bool
    data: list[HospitalAppointmentRequestResponse]


# -----------------------------
# Step 2
# Hospital appointment detail
# -----------------------------

class HospitalAppointmentRequestDetailResponse(BaseModel):
    id: int
    status: str

    requested_start_at: datetime
    duration_minutes: int

    visit_reason: str | None = None
    patient_note: str | None = None

    created_at: datetime
    updated_at: datetime

    patient: PatientInfo
    doctor: DoctorInfo
    hospital: HospitalInfo

    class Config:
        from_attributes = True


class HospitalAppointmentRequestDetailApiResponse(BaseModel):
    success: bool
    data: HospitalAppointmentRequestDetailResponse

class HospitalAppointmentRequestActionResponse(BaseModel):
    success: bool
    message: str
    data: HospitalAppointmentRequestResponse


class AppointmentAcceptRequest(BaseModel):
    message: str | None = None


class AppointmentDeclineRequest(BaseModel):
    reason: str


class AppointmentProposeRequest(BaseModel):
    proposed_start_at: datetime
    message: str | None = None