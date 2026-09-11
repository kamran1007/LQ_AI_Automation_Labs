from pydantic import BaseModel, Field


class SendOTPRequest(BaseModel):
    mobile: str = Field(
        min_length=10,
        max_length=20
    )


class SendOTPResponse(BaseModel):
    success: bool
    message: str


class VerifyOTPRequest(BaseModel):
    mobile: str = Field(
        min_length=10,
        max_length=20
    )

    otp: str = Field(
        min_length=4,
        max_length=10
    )


class VerifyOTPResponse(BaseModel):
    success: bool
    message: str
    access_token: str | None = None
    token_type: str = "bearer"
    user_id: int | None = None

class VerifyMSG91TokenRequest(BaseModel):
    access_token: str = Field(
        min_length=1
    )