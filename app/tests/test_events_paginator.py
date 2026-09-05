from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.clients.events_paginator import EventPaginator
from app.schemas.provider import ProviderEvent, ProviderEventResponse, ProviderPlace


@pytest.mark.asyncio
async def test_event_paginator():
    client = AsyncMock()

    client.get_events.side_effect = [
        ProviderEventResponse(
            next=None,
            previous=None,
            results=[],
        )
    ]
    paginator = EventPaginator(client=client, changed_at="2000-01-01")

    events = []

    async for event in paginator:
        events.append(event)

    assert events == []

    client.get_events.assert_awaited_once_with(
        changed_at="2000-01-01",
        cursor=None,
    )


@pytest.mark.asyncio
async def test_event_paginator_with_multiple_pages():
    client = AsyncMock()

    place = ProviderPlace(
        id=uuid4(),
        changed_at=datetime.now(),
        created_at=datetime.now(),
        name="Green island",
        city="Lipetsk",
        address="green island, 1",
        seats_pattern="A1-10",
    )

    event_1 = ProviderEvent(
        id=uuid4(),
        place=place,
        changed_at=datetime.now(),
        created_at=datetime.now(),
        name="Event 1",
        event_time=datetime.now(),
        registration_deadline=datetime.now(),
        status="published",
        number_of_visitors=0,
        status_changed_at=datetime.now(),
    )

    event_2 = ProviderEvent(
        id=uuid4(),
        place=place,
        changed_at=datetime.now(),
        created_at=datetime.now(),
        name="Event2",
        event_time=datetime.now(),
        registration_deadline=datetime.now(),
        status="published",
        number_of_visitors=0,
        status_changed_at=datetime.now(),
    )

    first_response = ProviderEventResponse(
        next=("http://test/api/events/?changed_at=2000-01-01&cursor=abc123"),
        previous=None,
        results=[event_1],
    )

    second_response = ProviderEventResponse(
        next=None,
        previous="http://test/api/events/?changed_at=2000-01-01",
        results=[event_2],
    )

    client.get_events.side_effect = [
        first_response,
        second_response,
    ]

    paginator = EventPaginator(
        client=client,
        changed_at="2000-01-01",
    )

    events = []

    async for event in paginator:
        events.append(event)

    assert events == [event_1, event_2]

    assert client.get_events.await_count == 2

    client.get_events.assert_any_await(
        changed_at="2000-01-01",
        cursor=None,
    )

    client.get_events.assert_any_await(
        changed_at="2000-01-01",
        cursor="abc123",
    )
