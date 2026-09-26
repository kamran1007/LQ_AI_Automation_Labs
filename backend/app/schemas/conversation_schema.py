from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ConversationResponse(BaseModel):
    id: int
    message: str
    ai_response: str
    intent: str
    extra_data: dict[str, Any] | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)