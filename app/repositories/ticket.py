from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.ticket import Ticket


class TicketRepositories:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, ticket: Ticket) -> Ticket:
        self.session.add(ticket)
        return ticket

    async def get_by_id(self, ticket_id: UUID) -> Optional[Ticket]:
        return await self.session.get(Ticket, ticket_id)

    async def delete(self, ticket_id: UUID) -> None:
        ticket = await self.get_by_id(ticket_id)

        if ticket is not None:
            await self.session.delete(ticket)

    async def commit(self) -> None:
        await self.session.commit()
