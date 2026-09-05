from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException

from app.clients.event_provider import EventProviderClient
from app.clients.exeptions import EventProviderError
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
        event_id: UUID,
        ticket_id: UUID,
    ) -> None:
        event = await self.event_repository.get_by_id(event_id)

        if event is None:
            raise HTTPException(
                status_code=404,
                detail="Мероприятие отсутствует",
            )

        ticket = await self.ticket_repository.get_by_id(ticket_id)

        if ticket is None or ticket.event_id != event_id:
            raise HTTPException(
                status_code=404,
                detail="Регистрация не найдена",
            )

        now = datetime.now(timezone.utc)

        if now >= event.event_time:
            raise HTTPException(
                status_code=400,
                detail="Нельзя отменить регистрацию после начала мероприятия",
            )

        try:
            await self.client.unregister(
                event_id=event_id,
                ticket_id=ticket_id,
            )
        except EventProviderError as error:
            raise HTTPException(
                status_code=400,
                detail=str(error),
            ) from error

        await self.ticket_repository.delete(ticket_id)
        await self.ticket_repository.commit()
