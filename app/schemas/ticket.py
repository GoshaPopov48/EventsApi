from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegistrationTicketRequest(BaseModel):
    event_id: UUID
    first_name: str = Field(min_length=1)
    last_name: str = Field(min_length=1)
    seat: str = Field(min_length=1)
    email: EmailStr


class RegistrationTicketResponse(BaseModel):
    ticket_id: UUID


class UnregisterTicketRequest(BaseModel):
    ticket_id: UUID


class UnregisterTicketResponse(BaseModel):
    success: bool
