from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, Mock
from uuid import UUID

import pytest
from fastapi import HTTPException

from app.clients.event_provider import EventProviderClient
from app.db.models.event import Event
from app.repositories.event import EventRepository
from app.repositories.ticket import TicketRepositories
from app.schemas.provider import ProviderSeatResponse
from app.usecases.create_ticket import CreateTicketUsecase


@pytest.mark.asyncio
async def test_create_ticket():
    event_id = UUID("550e8400-e29b-41d4-a716-446655440000")

    event = Event(
        id=event_id,
        name="Тестовое мероприятие",
        status="published",
        registration_deadline=datetime.now(timezone.utc) + timedelta(days=1),
        event_time=datetime.now(timezone.utc) + timedelta(days=2),
    )

    repository = Mock(spec=EventRepository)
    repository.get_by_id = AsyncMock(return_value=event)

    ticket_repository = Mock(spec=TicketRepositories)
    ticket_repository.create = AsyncMock()
    ticket_repository.commit = AsyncMock()

    client = Mock(spec=EventProviderClient)

    client.get_seats = AsyncMock(
        return_value=ProviderSeatResponse(
            seats=["A1", "A3", "B1"],
        )
    )

    ticket_id = UUID("1fed0122-b675-42e2-8ae7-49bfb53e8d7f")

    client.register = AsyncMock(return_value=ticket_id)

    usecase = CreateTicketUsecase(
        client=client,
        event_repository=repository,
        ticket_repository=ticket_repository,
    )

    result = await usecase.execute(
        event_id=event_id,
        first_name="Иван",
        last_name="Иванов",
        seat="A1",
        email="ivan@example.com",
    )

    assert result == ticket_id

    repository.get_by_id.assert_awaited_once_with(event_id)
    client.get_seats.assert_awaited_once_with(event_id)
    client.register.assert_awaited_once_with(
        event_id=event_id,
        first_name="Иван",
        last_name="Иванов",
        seat="A1",
        email="ivan@example.com",
    )

    ticket_repository.create.assert_awaited_once()
    ticket_repository.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_ticket_event_not_found():
    event_id = UUID("550e8400-e29b-41d4-a716-446655440000")

    repository = Mock(spec=EventRepository)
    repository.get_by_id = AsyncMock(return_value=None)

    ticket_repository = Mock(spec=TicketRepositories)
    client = Mock(spec=EventProviderClient)
    client.register = AsyncMock()

    usecase = CreateTicketUsecase(
        client=client,
        event_repository=repository,
        ticket_repository=ticket_repository,
    )

    with pytest.raises(HTTPException) as exc:
        await usecase.execute(
            event_id=event_id,
            first_name="Иван",
            last_name="Иванов",
            seat="A1",
            email="ivan@example.com",
        )

    assert exc.value.status_code == 404
    assert exc.value.detail == "Мероприятие отсутствует"

    client.get_seats.assert_not_awaited()
    client.register.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_ticket_event_not_published():
    event_id = UUID("550e8400-e29b-41d4-a716-446655440000")

    event = Event(
        id=event_id,
        name="Тестовое мероприятие",
        status="new",
        registration_deadline=datetime.now(timezone.utc) + timedelta(days=1),
        event_time=datetime.now(timezone.utc) + timedelta(days=2),
    )

    repository = Mock(spec=EventRepository)
    repository.get_by_id = AsyncMock(return_value=event)

    ticket_repository = Mock(spec=TicketRepositories)
    client = Mock(spec=EventProviderClient)
    client.register = AsyncMock()

    usecase = CreateTicketUsecase(
        client=client,
        event_repository=repository,
        ticket_repository=ticket_repository,
    )

    with pytest.raises(HTTPException) as exc:
        await usecase.execute(
            event_id=event_id,
            first_name="Иван",
            last_name="Иванов",
            seat="A1",
            email="ivan@example.com",
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "Мероприятие не опубликовано"

    client.get_seats.assert_not_awaited()
    client.register.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_ticket_seat_not_available():
    event_id = UUID("550e8400-e29b-41d4-a716-446655440000")

    event = Event(
        id=event_id,
        name="Тестовое мероприятие",
        status="published",
        registration_deadline=datetime.now(timezone.utc) + timedelta(days=1),
        event_time=datetime.now(timezone.utc) + timedelta(days=2),
    )

    repository = Mock(spec=EventRepository)
    repository.get_by_id = AsyncMock(return_value=event)

    ticket_repository = Mock(spec=TicketRepositories)

    client = Mock(spec=EventProviderClient)
    client.get_seats = AsyncMock(
        return_value=ProviderSeatResponse(
            seats=["A1", "A3", "B1"],
        )
    )

    usecase = CreateTicketUsecase(
        client=client,
        event_repository=repository,
        ticket_repository=ticket_repository,
    )

    with pytest.raises(HTTPException) as exc:
        await usecase.execute(
            event_id=event_id,
            first_name="Иван",
            last_name="Иванов",
            seat="A2",
            email="ivan@example.com",
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "Выбранное место недоступно"

    client.get_seats.assert_awaited_once_with(event_id)
    client.register.assert_not_awaited()
