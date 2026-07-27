"""Dynamic customer segment endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import CustomerEvent, CustomerProfile
from app.schemas import CustomerProfileRead


router = APIRouter(prefix="/segments", tags=["segments"])


@router.get("", response_model=list[CustomerProfileRead])
def list_segment_profiles(
    has_email: bool | None = Query(default=None),
    event_type: str | None = Query(default=None, min_length=1, max_length=100),
    db: Session = Depends(get_db),
) -> list[CustomerProfile]:
    """Return profiles matching all supplied segment criteria."""
    statement = select(CustomerProfile)

    if has_email is True:
        statement = statement.where(
            CustomerProfile.email.is_not(None),
            CustomerProfile.email != "",
        )
    elif has_email is False:
        statement = statement.where(
            or_(CustomerProfile.email.is_(None), CustomerProfile.email == ""),
        )

    if event_type is not None:
        statement = statement.where(
            CustomerProfile.events.any(CustomerEvent.event_type == event_type),
        )

    return list(db.scalars(statement.order_by(CustomerProfile.id)))
