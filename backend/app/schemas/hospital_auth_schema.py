
from pydantic import BaseModel, Field

class HospitalVerifyOTPRequest(BaseModel):
    mobile: str = Field(..., min_length=10, max_length=20)
    otp: str = Field(..., min_length=4, max_length=10)
    


class HospitalAuthResponse(BaseModel):
    success: bool
    message: str

    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    user_id: int
    role_id: int
    hospital_id: int
    session_id: str
    expires_at: str

