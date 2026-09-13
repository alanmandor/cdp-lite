"""Analytics endpoints backed by the Kimball mart."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.mart_models import DimDate, DimEventType, FactCustomerEvent
from app.schemas import EventSummaryRead


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/event-summary", response_model=list[EventSummaryRead])
def get_event_summary(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[dict[str, date | int | str]]:
    """Return daily event counts grouped by event type from the Kimball mart."""
    if start_date is not None and end_date is not None and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be on or before end_date.",
        )

    statement = (
        select(
            DimDate.calendar_date,
            DimEventType.event_type,
            func.count(FactCustomerEvent.hub_event_key).label("event_count"),
        )
        .join(FactCustomerEvent, FactCustomerEvent.date_key == DimDate.date_key)
        .join(
            DimEventType,
            FactCustomerEvent.event_type_key == DimEventType.event_type_key,
        )
        .group_by(DimDate.calendar_date, DimEventType.event_type)
        .order_by(DimDate.calendar_date, DimEventType.event_type)
    )
    if start_date is not None:
        statement = statement.where(DimDate.calendar_date >= start_date)
    if end_date is not None:
        statement = statement.where(DimDate.calendar_date <= end_date)

    return [dict(row) for row in db.execute(statement).mappings()]
