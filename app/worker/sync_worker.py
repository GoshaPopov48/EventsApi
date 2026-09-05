import asyncio
import logging

from app.clients.event_provider import EventProviderClient
from app.config import settings
from app.db.database import async_session_maker
from app.repositories.event import EventRepository
from app.repositories.place import PlaceRepository
from app.repositories.sync_metadata import SyncMetadataRepository
from app.usecases.sync_events import SyncEventsUsecase

logger = logging.getLogger(__name__)


async def sync_worker(stop_event: asyncio.Event) -> None:
    client = EventProviderClient(
        base_url=settings.events_provider_url,
        api_key=settings.api_key_lms,
    )

    try:
        while not stop_event.is_set():
            try:
                async with async_session_maker() as session:
                    event_repository = EventRepository(session)
                    place_repository = PlaceRepository(session)
                    sync_metadata_repository = SyncMetadataRepository(session)

                    usecase = SyncEventsUsecase(
                        client=client,
                        event_repository=event_repository,
                        place_repository=place_repository,
                        sync_metadata_repository=sync_metadata_repository,
                    )

                    await usecase.execute()

            except Exception:
                logger.exception("Ошибка фоновой синхронизации")

            try:
                await asyncio.wait_for(
                    stop_event.wait(),
                    timeout=60 * 60 * 24,
                )
            except asyncio.TimeoutError:
                continue

    finally:
        await client.client.aclose()
        logger.info("Фоновый worker остановлен")
