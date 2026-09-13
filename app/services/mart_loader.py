"""Load Data Vault records into the Kimball customer-event mart."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.mart_models import DimCustomer, DimDate, DimEventType, FactCustomerEvent
from app.vault_models import (
    HubCustomer,
    LinkCustomerEvent,
    SatCustomerProfile,
    SatEventDetails,
)


def load_mart(db: Session) -> dict[str, int]:
    """Build Type 2 dimensions and event facts from the Data Vault."""
    report = {
        "customer_dimension_rows_created": 0,
        "event_type_dimension_rows_created": 0,
        "date_dimension_rows_created": 0,
        "event_facts_created": 0,
    }
    load_customer_dimension(db, report)
    db.flush()
    load_event_facts(db, report)
    db.commit()
    return report


def load_customer_dimension(db: Session, report: dict[str, int]) -> None:
    """Create one Type 2 dimension version for every new customer satellite row."""
    customer_satellites = db.execute(
        select(SatCustomerProfile, HubCustomer)
        .join(
            HubCustomer,
            HubCustomer.hub_customer_key == SatCustomerProfile.hub_customer_key,
        )
        .order_by(SatCustomerProfile.hub_customer_key, SatCustomerProfile.load_datetime),
    ).all()

    for satellite, hub in customer_satellites:
        existing_dimension_row = db.scalar(
            select(DimCustomer).where(
                DimCustomer.hub_customer_key == satellite.hub_customer_key,
                DimCustomer.satellite_load_datetime == satellite.load_datetime,
            ),
        )
        if existing_dimension_row is not None:
            continue

        current_dimension_row = db.scalar(
            select(DimCustomer).where(
                DimCustomer.hub_customer_key == satellite.hub_customer_key,
                DimCustomer.is_current.is_(True),
            ),
        )
        if current_dimension_row is not None:
            current_dimension_row.effective_to = satellite.load_datetime
            current_dimension_row.is_current = False

        db.add(
            DimCustomer(
                hub_customer_key=satellite.hub_customer_key,
                satellite_load_datetime=satellite.load_datetime,
                external_id=hub.external_id,
                email=satellite.email,
                first_name=satellite.first_name,
                last_name=satellite.last_name,
                effective_from=satellite.load_datetime,
                effective_to=None,
                is_current=True,
            ),
        )
        report["customer_dimension_rows_created"] += 1


def load_event_facts(db: Session, report: dict[str, int]) -> None:
    """Create dimensions and facts for Data Vault events not yet in the mart."""
    latest_event_satellites = latest_satellites_by_event(db)
    customer_links = db.scalars(select(LinkCustomerEvent)).all()

    for link in customer_links:
        if db.get(FactCustomerEvent, link.hub_event_key) is not None:
            continue

        event_satellite = latest_event_satellites[link.hub_event_key]
        customer_dimension = db.scalar(
            select(DimCustomer)
            .where(
                DimCustomer.hub_customer_key == link.hub_customer_key,
                DimCustomer.is_current.is_(True),
            )
            .limit(1),
        )
        if customer_dimension is None:
            continue

        event_type_dimension = get_or_create_event_type(
            db,
            event_satellite.event_type,
            report,
        )
        date_dimension = get_or_create_date(
            db,
            event_satellite.occurred_at,
            report,
        )
        db.add(
            FactCustomerEvent(
                hub_event_key=link.hub_event_key,
                customer_key=customer_dimension.customer_key,
                event_type_key=event_type_dimension.event_type_key,
                date_key=date_dimension.date_key,
                occurred_at=event_satellite.occurred_at,
            ),
        )
        report["event_facts_created"] += 1


def latest_satellites_by_event(db: Session) -> dict[str, SatEventDetails]:
    """Return the most recently loaded satellite version for every event hub."""
    satellites = db.scalars(
        select(SatEventDetails).order_by(
            SatEventDetails.hub_event_key,
            SatEventDetails.load_datetime,
        ),
    ).all()
    return {satellite.hub_event_key: satellite for satellite in satellites}


def get_or_create_event_type(
    db: Session,
    event_type: str,
    report: dict[str, int],
) -> DimEventType:
    """Return the event-type dimension row, creating it when necessary."""
    event_type_dimension = db.scalar(
        select(DimEventType).where(DimEventType.event_type == event_type),
    )
    if event_type_dimension is None:
        event_type_dimension = DimEventType(event_type=event_type)
        db.add(event_type_dimension)
        db.flush()
        report["event_type_dimension_rows_created"] += 1
    return event_type_dimension


def get_or_create_date(
    db: Session,
    occurred_at: datetime,
    report: dict[str, int],
) -> DimDate:
    """Return the calendar dimension row for an event timestamp."""
    calendar_date = occurred_at.date()
    date_key = int(calendar_date.strftime("%Y%m%d"))
    date_dimension = db.get(DimDate, date_key)
    if date_dimension is None:
        date_dimension = DimDate(
            date_key=date_key,
            calendar_date=calendar_date,
            day_of_month=calendar_date.day,
            month_number=calendar_date.month,
            quarter_number=(calendar_date.month - 1) // 3 + 1,
            year_number=calendar_date.year,
        )
        db.add(date_dimension)
        db.flush()
        report["date_dimension_rows_created"] += 1
    return date_dimension
