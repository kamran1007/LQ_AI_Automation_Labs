from pydantic import BaseModel


class HospitalMeUser(BaseModel):
    id: int
    name: str | None
    mobile: str
    email: str | None


class HospitalMeRole(BaseModel):
    id: int
    name: str


class HospitalMeHospital(BaseModel):
    id: int
    name: str
    phone: str | None
    email: str | None
    address: str | None
    city: str | None
    state: str | None
    country: str
    timezone: str
    is_verified: bool
    is_active: bool


class HospitalMeResponse(BaseModel):
    success: bool
    user: HospitalMeUser
    role: HospitalMeRole
    hospital: HospitalMeHospital
    session_id: str