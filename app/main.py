import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.events import router as events_router
from app.api.healthy import router as health_check
from app.api.sync import router as sync_router
from app.clients.event_provider import EventProviderClient
from app.config import settings
from app.worker.sync_worker import sync_worker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    stop_event = asyncio.Event()

    app.state.event_provider_client = EventProviderClient(
        base_url=settings.events_provider_url,
        api_key=settings.api_key_lms,
    )
    sync_task = asyncio.create_task(sync_worker(stop_event))

    yield

    stop_event.set()

    await sync_task


app = FastAPI(lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=400,
        content={"detail": "Некорректные данные запроса"},
    )


app.include_router(health_check)
app.include_router(events_router)
app.include_router(sync_router)
