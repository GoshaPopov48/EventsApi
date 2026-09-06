from datetime import datetime, timezone
from uuid import UUID

from app.clients.event_provider import EventProviderClient
from app.clients.exeptions import (
    EventAlreadyStarted,
    EventNotFound,
    EventProviderError,
    RegistrationError,
    TicketNotFound,
)
from app.repositories.event import EventRepository
from app.repositories.ticket import TicketRepositories


class UnregisterTicketUsecase:
    def __init__(
        self,
        client: EventProviderClient,
        event_repository: EventRepository,
        ticket_repository: TicketRepositories,
    ):
        self.client = client
        self.event_repository = event_repository
        self.ticket_repository = ticket_repository

    async def execute(
        self,
        ticket_id: UUID,
    ) -> None:
        ticket = await self.ticket_repository.get_by_id(ticket_id)

        if ticket is None:
            raise TicketNotFound()

        event = await self.event_repository.get_by_id(ticket.event_id)
        if event is None:
            raise EventNotFound()

        now = datetime.now(timezone.utc)

        if now >= event.event_time:
            raise EventAlreadyStarted()

        try:
            await self.client.unregister(
                event_id=event.id,
                ticket_id=ticket_id,
            )
        except EventProviderError as error:
            raise RegistrationError(str(error)) from error

        await self.ticket_repository.delete(ticket_id)
        await self.ticket_repository.commit()
