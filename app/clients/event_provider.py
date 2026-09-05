from typing import Optional
from uuid import UUID

import httpx

from app.clients.exeptions import EventProviderError
from app.schemas.provider import ProviderEventResponse, ProviderSeatResponse


class EventProviderClient:
    def __init__(self, base_url: str, api_key: str):
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={"x-api-key": api_key},
            follow_redirects=True,
        )

    async def get_events(
        self, changed_at: str, cursor: Optional[str] = None
    ) -> ProviderEventResponse:
        params = {"changed_at": changed_at}

        if cursor:
            params["cursor"] = cursor
        response = await self.client.get("api/events/", params=params)

        response.raise_for_status()
        return ProviderEventResponse.model_validate(response.json())

    async def get_seats(self, event_id: UUID) -> ProviderSeatResponse:
        response = await self.client.get(f"api/events/{event_id}/seats/")
        response.raise_for_status()
        return ProviderSeatResponse.model_validate(response.json())

    async def register(
        self, event_id: UUID, first_name: str, last_name: str, seat: str, email: str
    ) -> UUID:
        response = await self.client.post(
            f"api/events/{event_id}/register/",
            json={
                "first_name": first_name,
                "last_name": last_name,
                "seat": seat,
                "email": email,
            },
        )
        if response.status_code == 400:
            raise EventProviderError("This ticket is not available (already sold).")

        if response.status_code == 404:
            raise EventProviderError("Event not found.")
        if response.status_code == 401:
            raise EventProviderError("Ошибка авторизации Events Provider")

        response.raise_for_status()
        return UUID(response.json()["ticket_id"])

    async def unregister(self, event_id: UUID, ticket_id: UUID) -> None:
        response = await self.client.request(
            "DELETE",
            f"api/events/{event_id}/unregister/",
            json={
                "ticket_id": str(ticket_id),
            },
        )

        if response.status_code == 400:
            raise EventProviderError("Невозможно отменить регистрацию")

        if response.status_code == 404:
            raise EventProviderError("Мероприятие или регистрация не найдены")

        if response.status_code == 401:
            raise EventProviderError("Ошибка авторизации Events Provider")

        response.raise_for_status()
