"""Customer event endpoints."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import CustomerEvent, CustomerProfile
from app.schemas import CustomerEventCreate, CustomerEventRead


router = APIRouter(prefix="/profiles/{external_id}/events", tags=["events"])


def get_profile_or_404(external_id: str, db: Session) -> CustomerProfile:
    """Return a profile or raise a not-found response."""
    profile = db.scalar(
        select(CustomerProfile).where(CustomerProfile.external_id == external_id),
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found.",
        )
    return profile


@router.post("", response_model=CustomerEventRead, status_code=status.HTTP_201_CREATED)
def create_event(
    external_id: str,
    event_data: CustomerEventCreate,
    db: Session = Depends(get_db),
) -> CustomerEvent:
    """Record an event for an existing customer profile."""
    profile = get_profile_or_404(external_id, db)
    event = CustomerEvent(
        profile_id=profile.id,
        event_type=event_data.event_type,
        event_data=event_data.event_data,
        occurred_at=event_data.occurred_at or datetime.now(timezone.utc),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("", response_model=list[CustomerEventRead])
def list_events(
    external_id: str,
    db: Session = Depends(get_db),
) -> list[CustomerEvent]:
    """List a profile's events from newest to oldest."""
    profile = get_profile_or_404(external_id, db)
    return list(
        db.scalars(
            select(CustomerEvent)
            .where(CustomerEvent.profile_id == profile.id)
            .order_by(CustomerEvent.occurred_at.desc()),
        ),
    )
