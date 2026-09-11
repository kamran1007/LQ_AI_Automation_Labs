from pydantic import BaseModel
from typing import Optional, Dict, Any


class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    success: bool
    intent: str
    message: str

    requires_location: bool = False
    requires_business_name: bool = False
    requires_confirmation: bool = False

    metadata: Optional[Dict[str, Any]] = None
    workflow: Optional[Dict[str, Any]] = None
