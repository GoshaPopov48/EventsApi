from unittest.mock import AsyncMock, Mock, patch
from uuid import UUID

import pytest

from app.clients.event_provider import EventProviderClient


@pytest.mark.asyncio
async def test_get_events():
    client = EventProviderClient(
        base_url="http://test",
        api_key="test_key",
    )

    response = Mock()
    response.json.return_value = {"next": None, "previous": None, "results": []}
    response.raise_for_status = lambda: None

    with patch.object(
        client.client,
        "get",
        new_callable=AsyncMock,
        return_value=response,
    ) as mock_get:
        result = await client.get_events(
            "2000-01-01",
            cursor="abc123",
        )

    assert result.next is None
    assert result.previous is None
    assert result.results == []

    mock_get.assert_awaited_once_with(
        "api/events/",
        params={
            "changed_at": "2000-01-01",
            "cursor": "abc123",
        },
    )
    await client.client.aclose()


@pytest.mark.asyncio
async def test_get_seats():
    client = EventProviderClient(
        base_url="http://test",
        api_key="test_key",
    )
    response = Mock()
    response.json.return_value = {
        "seats": ["A1", "A3", "A4", "B1"],
    }
    response.raise_for_status = lambda: None

    event_id = UUID("550e8400-e29b-41d4-a716-446655440000")

    with patch.object(
        client.client,
        "get",
        new_callable=AsyncMock,
        return_value=response,
    ) as mock_get:
        result = await client.get_seats(event_id)

        assert result.seats == ["A1", "A3", "A4", "B1"]

        mock_get.assert_awaited_once_with(
            "api/events/550e8400-e29b-41d4-a716-446655440000/seats/",
        )
        await client.client.aclose()
