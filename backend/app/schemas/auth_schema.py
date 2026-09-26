from datetime import datetime

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
    refresh_token: str | None = None

    token_type: str = "bearer"

    user_id: int | None = None
    mobile: str | None = None
    name: str | None = None
    is_verified: bool | None = None

    session_id: str | None = None

class VerifyMSG91TokenRequest(BaseModel):
    access_token: str = Field(
        min_length=1
    )

class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(
        min_length=1
    )


class RefreshTokenResponse(BaseModel):
    success: bool
    message: str

    access_token: str
    refresh_token: str

    token_type: str = "bearer"

    user_id: int
    session_id: str

    refresh_token_expires_at: datetime