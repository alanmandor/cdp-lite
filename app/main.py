"""Punto de entrada de la API CDP Lite."""

from fastapi import FastAPI


app = FastAPI(
    title="CDP Lite API",
    version="0.1.0",
    description="API mínima para gestionar perfiles, eventos y segmentos de clientes.",
)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """Indica que la API está disponible."""
    return {"status": "ok"}
