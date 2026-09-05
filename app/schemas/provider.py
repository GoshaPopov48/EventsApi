from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ProviderPlace(BaseModel):
    id: UUID
    changed_at: datetime
    created_at: datetime
    name: str
    city: str
    address: str
    seats_pattern: str


class ProviderEvent(BaseModel):
    id: UUID
    place: ProviderPlace
    changed_at: datetime
    created_at: datetime
    name: str
    event_time: datetime
    registration_deadline: datetime
    status: str
    number_of_visitors: int
    status_changed_at: datetime


class ProviderEventResponse(BaseModel):
    next: Optional[str]
    previous: Optional[str]
    results: list[ProviderEvent]


class ProviderSeatResponse(BaseModel):
    seats: list[str]
