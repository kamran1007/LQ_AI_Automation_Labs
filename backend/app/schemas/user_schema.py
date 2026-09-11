from datetime import datetime

from pydantic import BaseModel, Field


class CreateUserRequest(BaseModel):
    mobile: str = Field(
        min_length=10,
        max_length=20
    )

    name: str | None = Field(
        default=None,
        max_length=255
    )


class UserResponse(BaseModel):
    id: int
    mobile: str
    name: str | None
    latitude: float | None
    longitude: float | None
    location_updated_at: datetime | None
    is_active: bool

    class Config:
        from_attributes = True