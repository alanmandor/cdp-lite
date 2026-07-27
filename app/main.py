"""CDP Lite API entry point."""

from fastapi import FastAPI


app = FastAPI(
    title="CDP Lite API",
    version="0.1.0",
    description="A minimal API for managing customer profiles, events, and segments.",
)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Report that the API is available."""
    return {"status": "ok"}
