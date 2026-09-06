from datetime import datetime, timezone
from uuid import UUID

from app.clients.event_provider import EventProviderClient
from app.clients.exeptions import (
    EventAlreadyStarted,
    EventNotFound,
    EventNotPublished,
    EventProviderError,
    RegistrationClosed,
    RegistrationError,
    SeatNotAvailable,
)
from app.db.models.ticket import Ticket
from app.repositories.event import EventRepository
from app.repositories.ticket import TicketRepositories


class CreateTicketUsecase:
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
        self, event_id: UUID, first_name: str, last_name: str, seat: str, email: str
    ) -> UUID:
        event = await self.event_repository.get_by_id(event_id)

        if event is None:
            raise EventNotFound()

        if event.status != "published":
            raise EventNotPublished()
        now = datetime.now(timezone.utc)

        if now >= event.registration_deadline:
            raise RegistrationClosed()

        if now >= event.event_time:
            raise EventAlreadyStarted

        response = await self.client.get_seats(event_id)

        if seat not in response.seats:
            raise SeatNotAvailable()
        try:
            ticket_id = await self.client.register(
                event_id=event_id,
                first_name=first_name,
                last_name=last_name,
                seat=seat,
                email=email,
            )
        except EventProviderError as error:
            raise RegistrationError(str(error)) from error

        ticket = Ticket(
            id=ticket_id,
            event_id=event_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat,
            created_at=now,
        )

        await self.ticket_repository.create(ticket)
        await self.ticket_repository.commit()

        return ticket_id
