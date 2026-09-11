"""Warehouse loading endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import VaultLoadReport
from app.services.vault_loader import load_vault


router = APIRouter(prefix="/warehouse", tags=["warehouse"])


@router.post("/vault/load", response_model=VaultLoadReport)
def load_operational_data_into_vault(
    db: Session = Depends(get_db),
) -> dict[str, int]:
    """Load operational profiles and events into the Data Vault layer."""
    return load_vault(db)
