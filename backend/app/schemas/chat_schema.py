from typing import Any

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    user_id: int


class ChatResponse(BaseModel):
    success: bool
    intent: str
    message: str

    requires_location: bool = False
    requires_business_name: bool = False
    requires_confirmation: bool = False

    metadata: dict[str, Any] | None = None
    workflow: dict[str, Any] | None = None