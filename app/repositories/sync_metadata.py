from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.sync import SyncMetadata


class SyncMetadataRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self) -> Optional[SyncMetadata]:
        result = await self.session.execute(select(SyncMetadata).limit(1))
        return result.scalar_one_or_none()

    async def create_or_up(
        self, last_changed_at: datetime, sync_status: str
    ) -> SyncMetadata:
        metadata = await self.get()

        if metadata is None:
            metadata = SyncMetadata(
                last_changed_at=last_changed_at,
                last_sync_time=datetime.now(),
                sync_status=sync_status,
            )
            self.session.add(metadata)
            return metadata
        if last_changed_at is not None:
            metadata.last_changed_at = last_changed_at
        metadata.last_sync_time = datetime.now()
        metadata.sync_status = sync_status
        return metadata

    async def commit(self) -> None:
        await self.session.commit()
