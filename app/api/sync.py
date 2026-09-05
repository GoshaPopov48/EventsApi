from fastapi import APIRouter

from app.clients.event_provider import EventProviderClient
from app.config import settings
from app.db.database import async_session_maker
from app.repositories.event import EventRepository
from app.repositories.place import PlaceRepository
from app.repositories.sync_metadata import SyncMetadataRepository
from app.usecases.sync_events import SyncEventsUsecase

router = APIRouter()


@router.post("/api/sync/trigger")
async def trigger_sync():
    client = EventProviderClient(
        base_url=settings.events_provider_url,
        api_key=settings.api_key_lms,
    )

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
    await client.client.aclose()

    return {"status": "ok"}
