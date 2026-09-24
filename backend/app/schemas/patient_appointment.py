from pydantic import BaseModel


class AppointmentProposalRejectRequest(BaseModel):
    reason: str | None = None