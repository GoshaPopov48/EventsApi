from uuid import UUID

from app.cache import seats_cache
from app.clients.event_provider import EventProviderClient
from app.clients.exeptions import (
    EventNotFound,
    EventNotPublished,
)
from app.repositories.event import EventRepository


class GetEventSeatUsecase:
    def __init__(self, client: EventProviderClient, event_repository: EventRepository):
        self.client = client
        self.event_repository = event_repository

    async def execute(self, event_id: UUID) -> dict:
        event = await self.event_repository.get_by_id(event_id)

        if event is None:
            raise EventNotFound()
        if event.status != "published":
            raise EventNotPublished()
        cached_seats = seats_cache.get(event_id)

        if cached_seats is not None:
            return {"event_id": event_id, "available_seats": cached_seats}

        response = await self.client.get_seats(event_id)
        seats_cache.set(event_id, response.seats)
        return {
            "event_id": event_id,
            "available_seats": response.seats,
        }
