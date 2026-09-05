from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException

from app.clients.event_provider import EventProviderClient
from app.clients.exeptions import EventProviderError
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
            raise HTTPException(
                status_code=404,
                detail="Мероприятие отсутствует",
            )

        if event.status != "published":
            raise HTTPException(status_code=400, detail="Мероприятие не опубликовано")
        now = datetime.now(timezone.utc)

        if now >= event.registration_deadline:
            raise HTTPException(
                status_code=400,
                detail="Регистрация на мероприятие завершена",
            )

        if now >= event.event_time:
            raise HTTPException(status_code=400, detail="Мероприятие уже прошло")

        response = await self.client.get_seats(event_id)

        if seat not in response.seats:
            raise HTTPException(status_code=400, detail="Выбранное место недоступно")
        try:
            ticket_id = await self.client.register(
                event_id=event_id,
                first_name=first_name,
                last_name=last_name,
                seat=seat,
                email=email,
            )
        except EventProviderError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

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
