from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.event import Event


class EventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(
        self,
        page: int,
        page_size: int = 20,
        date_from: Optional[datetime] = None,
    ) -> list[Event]:
        query = select(Event).options(selectinload(Event.place))

        if date_from is not None:
            query = query.where(Event.event_time >= date_from)

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count(self, date_from: Optional[datetime] = None) -> int:
        query = select(func.count(Event.id))

        if date_from is not None:
            query = query.where(Event.event_time >= date_from)

        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_by_id(self, event_id: UUID) -> Optional[Event]:
        result = await self.session.execute(
            select(Event).options(selectinload(Event.place)).where(Event.id == event_id)
        )
        return result.scalar_one_or_none()

    async def create_or_up(self, event: Event) -> Event:
        existing_event = await self.get_by_id(event.id)

        if existing_event is None:
            self.session.add(event)
            return event

        existing_event.name = event.name
        existing_event.place_id = event.place_id
        existing_event.event_time = event.event_time
        existing_event.registration_deadline = event.registration_deadline
        existing_event.status = event.status
        existing_event.number_of_visitors = event.number_of_visitors
        existing_event.changed_at = event.changed_at
        existing_event.created_at = event.created_at
        existing_event.status_changed_at = event.status_changed_at

        return existing_event

    async def commit(self) -> None:
        await self.session.commit()
