"""Data Vault 2.0 persistence models."""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class HubCustomer(Base):
    """Hub containing the stable customer business key."""

    __tablename__ = "hub_customer"

    hub_customer_key: Mapped[str] = mapped_column(String(64), primary_key=True)
    external_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    load_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    record_source: Mapped[str] = mapped_column(String(100))


class HubEvent(Base):
    """Hub containing the stable source identifier for an event."""

    __tablename__ = "hub_event"

    hub_event_key: Mapped[str] = mapped_column(String(64), primary_key=True)
    source_event_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    load_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    record_source: Mapped[str] = mapped_column(String(100))


class LinkCustomerEvent(Base):
    """Link recording that a customer generated an event."""

    __tablename__ = "link_customer_event"

    link_customer_event_key: Mapped[str] = mapped_column(String(64), primary_key=True)
    hub_customer_key: Mapped[str] = mapped_column(
        ForeignKey("hub_customer.hub_customer_key"),
        index=True,
    )
    hub_event_key: Mapped[str] = mapped_column(
        ForeignKey("hub_event.hub_event_key"),
        index=True,
    )
    load_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    record_source: Mapped[str] = mapped_column(String(100))


class SatCustomerProfile(Base):
    """Historized descriptive attributes for a customer."""

    __tablename__ = "sat_customer_profile"

    hub_customer_key: Mapped[str] = mapped_column(
        ForeignKey("hub_customer.hub_customer_key"),
        primary_key=True,
    )
    load_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        primary_key=True,
    )
    hash_diff: Mapped[str] = mapped_column(String(64))
    email: Mapped[str | None] = mapped_column(String(255))
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    record_source: Mapped[str] = mapped_column(String(100))


class SatEventDetails(Base):
    """Historized descriptive attributes for an event."""

    __tablename__ = "sat_event_details"

    hub_event_key: Mapped[str] = mapped_column(
        ForeignKey("hub_event.hub_event_key"),
        primary_key=True,
    )
    load_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        primary_key=True,
    )
    hash_diff: Mapped[str] = mapped_column(String(64))
    event_type: Mapped[str] = mapped_column(String(100))
    event_data: Mapped[dict[str, Any]] = mapped_column(JSON)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    record_source: Mapped[str] = mapped_column(String(100))
