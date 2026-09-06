from collections.abc import AsyncIterator
from urllib.parse import parse_qs, urlparse

from app.clients.event_provider import EventProviderClient
from app.schemas.provider import ProviderEvent


class EventPaginator:
    def __init__(self, client: EventProviderClient, changed_at: str):
        self.client = client
        self.changed_at = changed_at

    async def __aiter__(self) -> AsyncIterator[ProviderEvent]:
        cursor = None

        while True:
            response = await self.client.get_events(
                changed_at=self.changed_at, cursor=cursor
            )

            for event in response.results:
                yield event

            if response.next is None:
                break

            query_param = parse_qs(urlparse(response.next).query)
            cursor_value = query_param.get("cursor")

            if not cursor_value:
                break

            cursor = cursor_value[0]
