from uuid import UUID

from pydantic import BaseModel, EmailStr


class RegistrationTicketRequest(BaseModel):
    event_id: UUID
    first_name: str
    last_name: str
    seat: str
    email: EmailStr


class RegistrationTicketResponse(BaseModel):
    ticket_id: UUID


class UnregisterTicketRequest(BaseModel):
    ticket_id: UUID


class UnregisterTicketResponse(BaseModel):
    success: bool
