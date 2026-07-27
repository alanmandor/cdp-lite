"""CDP Lite API entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # noqa: F401
from app.db import Base, engine
from app.routers.events import router as events_router
from app.routers.profiles import router as profiles_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Create database tables when the application starts."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="CDP Lite API",
    version="0.1.0",
    description="A minimal API for managing customer profiles, events, and segments.",
    lifespan=lifespan,
)
app.include_router(profiles_router)
app.include_router(events_router)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Report that the API is available."""
    return {"status": "ok"}
