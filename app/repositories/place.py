from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.place import Place


class PlaceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, place_id: UUID) -> Optional[Place]:
        result = await self.session.execute(select(Place).where(Place.id == place_id))
        return result.scalar_one_or_none()

    async def create_or_up(
        self,
        place: Place,
    ) -> Place:
        existing_place = await self.get_by_id(place.id)

        if existing_place is None:
            self.session.add(place)
            return place

        existing_place.name = place.name
        existing_place.city = place.city
        existing_place.adress = place.adress
        existing_place.seats_pattern = place.seats_pattern
        existing_place.changed_at = place.changed_at
        existing_place.created_at = place.created_at

        return existing_place

    async def commit(self) -> None:
        await self.session.commit()
