"""Kimball mart loading endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import MartLoadReport
from app.services.mart_loader import load_mart


router = APIRouter(prefix="/warehouse", tags=["warehouse"])


@router.post("/mart/load", response_model=MartLoadReport)
def load_vault_data_into_mart(db: Session = Depends(get_db)) -> dict[str, int]:
    """Load Data Vault records into the Kimball customer-event mart."""
    return load_mart(db)
