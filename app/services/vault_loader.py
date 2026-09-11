"""Load operational CDP data into the Data Vault layer."""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CustomerEvent, CustomerProfile
from app.vault_models import (
    HubCustomer,
    HubEvent,
    LinkCustomerEvent,
    SatCustomerProfile,
    SatEventDetails,
)


RECORD_SOURCE = "cdp_lite_operational"


def create_hash(value: str) -> str:
    """Create a deterministic SHA-256 hash key from a canonical value."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def create_hash_diff(attributes: dict[str, Any]) -> str:
    """Create a deterministic hash for a satellite's descriptive attributes."""
    serialized_attributes = json.dumps(
        attributes,
        default=str,
        separators=(",", ":"),
        sort_keys=True,
    )
    return create_hash(serialized_attributes)


def load_vault(db: Session) -> dict[str, int]:
    """Load profiles and events into hubs, links, and change-only satellites."""
    report = {
        "hub_customers_created": 0,
        "hub_events_created": 0,
        "customer_event_links_created": 0,
        "customer_satellites_created": 0,
        "event_satellites_created": 0,
    }
    profiles = db.scalars(select(CustomerProfile).order_by(CustomerProfile.id)).all()

    for profile in profiles:
        hub_customer_key = create_hash(profile.external_id)
        hub_customer = db.get(HubCustomer, hub_customer_key)
        if hub_customer is None:
            db.add(
                HubCustomer(
                    hub_customer_key=hub_customer_key,
                    external_id=profile.external_id,
                    record_source=RECORD_SOURCE,
                ),
            )
            report["hub_customers_created"] += 1

        customer_attributes = {
            "email": profile.email,
            "first_name": profile.first_name,
            "last_name": profile.last_name,
        }
        customer_hash_diff = create_hash_diff(customer_attributes)
        latest_customer_satellite = db.scalar(
            select(SatCustomerProfile)
            .where(SatCustomerProfile.hub_customer_key == hub_customer_key)
            .order_by(SatCustomerProfile.load_datetime.desc())
            .limit(1),
        )
        if (
            latest_customer_satellite is None
            or latest_customer_satellite.hash_diff != customer_hash_diff
        ):
            db.add(
                SatCustomerProfile(
                    hub_customer_key=hub_customer_key,
                    load_datetime=datetime.now(timezone.utc),
                    hash_diff=customer_hash_diff,
                    record_source=RECORD_SOURCE,
                    **customer_attributes,
                ),
            )
            report["customer_satellites_created"] += 1

    events = db.scalars(select(CustomerEvent).order_by(CustomerEvent.id)).all()
    for event in events:
        profile = db.get(CustomerProfile, event.profile_id)
        if profile is None:
            continue

        hub_customer_key = create_hash(profile.external_id)
        source_event_id = f"customer_event:{event.id}"
        hub_event_key = create_hash(source_event_id)
        if db.get(HubEvent, hub_event_key) is None:
            db.add(
                HubEvent(
                    hub_event_key=hub_event_key,
                    source_event_id=source_event_id,
                    record_source=RECORD_SOURCE,
                ),
            )
            report["hub_events_created"] += 1

        link_key = create_hash(f"{hub_customer_key}|{hub_event_key}")
        if db.get(LinkCustomerEvent, link_key) is None:
            db.add(
                LinkCustomerEvent(
                    link_customer_event_key=link_key,
                    hub_customer_key=hub_customer_key,
                    hub_event_key=hub_event_key,
                    record_source=RECORD_SOURCE,
                ),
            )
            report["customer_event_links_created"] += 1

        event_attributes = {
            "event_type": event.event_type,
            "event_data": event.event_data,
            "occurred_at": event.occurred_at,
        }
        event_hash_diff = create_hash_diff(event_attributes)
        latest_event_satellite = db.scalar(
            select(SatEventDetails)
            .where(SatEventDetails.hub_event_key == hub_event_key)
            .order_by(SatEventDetails.load_datetime.desc())
            .limit(1),
        )
        if latest_event_satellite is None or latest_event_satellite.hash_diff != event_hash_diff:
            db.add(
                SatEventDetails(
                    hub_event_key=hub_event_key,
                    load_datetime=datetime.now(timezone.utc),
                    hash_diff=event_hash_diff,
                    record_source=RECORD_SOURCE,
                    **event_attributes,
                ),
            )
            report["event_satellites_created"] += 1

    db.commit()
    return report
