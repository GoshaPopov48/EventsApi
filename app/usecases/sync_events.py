import logging

from app.clients.event_provider import EventProviderClient
from app.clients.events_paginator import EventPaginator
from app.db.models.event import Event
from app.db.models.place import Place
from app.repositories.event import EventRepository
from app.repositories.place import PlaceRepository
from app.repositories.sync_metadata import SyncMetadataRepository

logger = logging.getLogger(__name__)


class SyncEventsUsecase:
    def __init__(
        self,
        client: EventProviderClient,
        event_repository: EventRepository,
        place_repository: PlaceRepository,
        sync_metadata_repository: SyncMetadataRepository,
    ):
        self.client = client
        self.event_repository = event_repository
        self.place_repository = place_repository
        self.sync_metadata_repository = sync_metadata_repository

    async def execute(self) -> None:
        logger.info("Синхронизация событий началась")

        metadata = await self.sync_metadata_repository.get()

        if metadata is None or metadata.last_changed_at is None:
            changed_at = "2000-01-01"
            logger.info(
                "Первая синхронизация. changed_at=%s",
                changed_at,
            )
        else:
            changed_at = metadata.last_changed_at.strftime("%Y-%m-%d")
            logger.info(
                "Инкрементальная синхронизация. changed_at=%s",
                changed_at,
            )

        paginator = EventPaginator(
            client=self.client,
            changed_at=changed_at,
        )

        last_changed_at = None
        events_count = 0

        try:
            async for event in paginator:
                provider_place = event.place

                place = Place(
                    id=provider_place.id,
                    name=provider_place.name,
                    city=provider_place.city,
                    adress=provider_place.address,
                    seats_pattern=provider_place.seats_pattern,
                    changed_at=provider_place.changed_at,
                    created_at=provider_place.created_at,
                )

                await self.place_repository.create_or_up(place)

                event_model = Event(
                    id=event.id,
                    name=event.name,
                    place_id=event.place.id,
                    event_time=event.event_time,
                    registration_deadline=event.registration_deadline,
                    status=event.status,
                    number_of_visitors=event.number_of_visitors,
                    changed_at=event.changed_at,
                    created_at=event.created_at,
                    status_changed_at=event.status_changed_at,
                )

                await self.event_repository.create_or_up(event_model)

                events_count += 1

                if last_changed_at is None or event.changed_at > last_changed_at:
                    last_changed_at = event.changed_at

            await self.event_repository.commit()

            if last_changed_at is not None:
                await self.sync_metadata_repository.create_or_up(
                    last_changed_at=last_changed_at,
                    sync_status="success",
                )

            await self.sync_metadata_repository.commit()

            logger.info(
                "Синхронизация успешно завершена. "
                "Обработано событий: %s, last_changed_at=%s",
                events_count,
                last_changed_at,
            )

        except Exception:
            logger.exception("Ошибка во время синхронизации")

            if metadata is not None:
                metadata.sync_status = "error"
                await self.sync_metadata_repository.commit()

            raise
