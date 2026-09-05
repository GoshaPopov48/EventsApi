from datetime import date, datetime, time, timezone
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.event_provider import EventProviderClient
from app.db.database import get_session
from app.repositories.event import EventRepository
from app.repositories.ticket import TicketRepositories
from app.schemas.event import EventListResponse, EventResponse
from app.schemas.ticket import (
    RegistrationTicketRequest,
    RegistrationTicketResponse,
    UnregisterTicketRequest,
    UnregisterTicketResponse,
)
from app.usecases.create_ticket import CreateTicketUsecase
from app.usecases.get_event_seat import GetEventSeatUsecase
from app.usecases.unregister_ticket import UnregisterTicketUsecase

router = APIRouter(prefix="/api")
SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_event_provider_client(request: Request):
    return request.app.state.event_provider_client


@router.get("/events/", response_model=EventListResponse)
async def get_events(
    session: SessionDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1),
    date_from: Optional[date] = None,
):
    repository = EventRepository(session)

    date_from_datetime = None
    if date_from is not None:
        date_from_datetime = datetime.combine(
            date_from,
            time.min,
            tzinfo=timezone.utc,
        )
    events = await repository.get_all(
        page=page, page_size=page_size, date_from=date_from_datetime
    )
    count = await repository.count(date_from=date_from_datetime)
    next_url = None
    previous_url = None

    date_param = ""

    if date_from is not None:
        date_param = f"&date_from={date_from}"

    if page * page_size < count:
        next_url = f"/events/?page={page + 1}&page_size={page_size}{date_param}"

    if page > 1:
        previous_url = f"/events/?page={page - 1}&page_size={page_size}{date_param}"

    return {
        "count": count,
        "next": next_url,
        "previous": previous_url,
        "results": events,
    }


@router.get("/events/{event_id}/", response_model=EventResponse)
async def get_event(event_id: UUID, session: SessionDep):
    repository = EventRepository(session)
    event = await repository.get_by_id(event_id)

    if event is None:
        raise HTTPException(status_code=404, detail="Мероприятие отсутствует")

    return event


@router.get("/events/{event_id}/seats/")
async def get_event_seat(
    event_id: UUID,
    session: SessionDep,
    client: Annotated[
        EventProviderClient,
        Depends(get_event_provider_client),
    ],
):
    event_repository = EventRepository(session)

    usecase = GetEventSeatUsecase(client=client, event_repository=event_repository)
    return await usecase.execute(event_id)


@router.post("/tickets/", response_model=RegistrationTicketResponse)
async def register_event(
    event_id: UUID,
    data: RegistrationTicketRequest,
    session: SessionDep,
    client: Annotated[EventProviderClient, Depends(get_event_provider_client)],
):
    event_repository = EventRepository(session)
    ticket_repository = TicketRepositories(session)

    usecase = CreateTicketUsecase(
        client=client,
        event_repository=event_repository,
        ticket_repository=ticket_repository,
    )

    ticket_id = await usecase.execute(
        event_id=event_id,
        first_name=data.first_name,
        last_name=data.last_name,
        seat=data.seat,
        email=data.email,
    )

    return RegistrationTicketResponse(ticket_id=ticket_id)


@router.delete("/events/{event_id}/unregister/")
async def unregister_event(
    event_id: UUID,
    data: UnregisterTicketRequest,
    session: SessionDep,
    client: Annotated[
        EventProviderClient,
        Depends(get_event_provider_client),
    ],
):
    event_repository = EventRepository(session)
    ticket_repository = TicketRepositories(session)

    usecase = UnregisterTicketUsecase(
        client=client,
        event_repository=event_repository,
        ticket_repository=ticket_repository,
    )

    await usecase.execute(
        event_id=event_id,
        ticket_id=data.ticket_id,
    )

    return UnregisterTicketResponse(success=True)
