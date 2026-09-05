import time
from typing import Optional
from uuid import UUID


class SeatsCache:
    def __init__(self, ttl: int = 30):
        self.ttl = ttl
        self._cache: dict[UUID, tuple[float, list[str]]] = {}

    def get(self, event_id: UUID) -> Optional[list[str]]:
        cached = self._cache.get(event_id)

        if cached is None:
            return None

        created_at, seats = cached

        if time.monotonic() - created_at >= self.ttl:
            del self._cache[event_id]
            return None

        return seats

    def set(self, event_id: UUID, seats: list[str]) -> None:
        self._cache[event_id] = (time.monotonic(), seats)


seats_cache = SeatsCache()
