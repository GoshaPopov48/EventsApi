from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest
from fastapi import HTTPException

from app.cache import seats_cache
from app.clients.event_provider import EventProviderClient
from app.db.models.event import Event
from app.repositories.event import EventRepository
from app.schemas.provider import ProviderSeatResponse
from app.usecases.get_event_seat import GetEventSeatUsecase


@pytest.mark.asyncio
async def test_get_event_seats():
    event_id = UUID("550e8400-e29b-41d4-a716-446655440000")

    event = Event(
        id=event_id,
        name="Тестовое мероприятие",
        status="published",
    )

    repository = Mock(spec=EventRepository)
    repository.get_by_id = AsyncMock(return_value=event)

    client = Mock(spec=EventProviderClient)
    client.get_seats = AsyncMock(
        return_value=ProviderSeatResponse(
            seats=["A1", "A3", "B1"],
        )
    )

    usecase = GetEventSeatUsecase(
        client=client,
        event_repository=repository,
    )

    result = await usecase.execute(event_id)

    assert result == {
        "event_id": event_id,
        "available_seats": ["A1", "A3", "B1"],
    }

    repository.get_by_id.assert_awaited_once_with(event_id)
    client.get_seats.assert_awaited_once_with(event_id)


@pytest.mark.asyncio
async def test_get_event_seats_not():
    event_id = UUID("550e8400-e29b-41d4-a716-446655440000")

    repository = Mock(spec=EventRepository)
    repository.get_by_id = AsyncMock(return_value=None)

    client = Mock(spec=EventProviderClient)

    usecase = GetEventSeatUsecase(
        client=client,
        event_repository=repository,
    )

    with pytest.raises(HTTPException) as exc:
        await usecase.execute(event_id)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Мероприятие отсутствует"

    repository.get_by_id.assert_awaited_once_with(event_id)
    client.get_seats.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_event_seats_not_published():
    event_id = UUID("550e8400-e29b-41d4-a716-446655440000")

    event = Event(
        id=event_id,
        name="Тестовое мероприятие",
        status="new",
    )

    repository = Mock(spec=EventRepository)
    repository.get_by_id = AsyncMock(return_value=event)

    client = Mock(spec=EventProviderClient)

    usecase = GetEventSeatUsecase(
        client=client,
        event_repository=repository,
    )

    with pytest.raises(HTTPException) as exc:
        await usecase.execute(event_id)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Мероприятие не опубликовано"

    repository.get_by_id.assert_awaited_once_with(event_id)
    client.get_seats.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_event_seats_uses_cache():
    event_id = UUID("550e8400-e29b-41d4-a716-446655440000")

    event = Event(
        id=event_id,
        name="Тестовое мероприятие",
        status="published",
    )

    repository = Mock(spec=EventRepository)
    repository.get_by_id = AsyncMock(return_value=event)

    client = Mock(spec=EventProviderClient)
    client.get_seats = AsyncMock(
        return_value=ProviderSeatResponse(
            seats=["A1", "A3", "B1"],
        )
    )

    usecase = GetEventSeatUsecase(
        client=client,
        event_repository=repository,
    )

    seats_cache._cache.clear()

    first_result = await usecase.execute(event_id)
    second_result = await usecase.execute(event_id)

    assert first_result == {
        "event_id": event_id,
        "available_seats": ["A1", "A3", "B1"],
    }

    assert second_result == first_result

    client.get_seats.assert_awaited_once_with(event_id)
