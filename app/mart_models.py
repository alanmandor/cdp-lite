"""Kimball star-schema persistence models."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class DimCustomer(Base):
    """Type 2 customer dimension derived from the customer profile satellite."""

    __tablename__ = "dim_customer"

    customer_key: Mapped[int] = mapped_column(Integer, primary_key=True)
    hub_customer_key: Mapped[str] = mapped_column(String(64), index=True)
    satellite_load_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    external_id: Mapped[str] = mapped_column(String(100), index=True)
    email: Mapped[str | None] = mapped_column(String(255))
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)


class DimEventType(Base):
    """Dimension classifying the type of customer event."""

    __tablename__ = "dim_event_type"

    event_type_key: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_type: Mapped[str] = mapped_column(String(100), unique=True, index=True)


class DimDate(Base):
    """Calendar dimension used by event facts."""

    __tablename__ = "dim_date"

    date_key: Mapped[int] = mapped_column(Integer, primary_key=True)
    calendar_date: Mapped[date] = mapped_column(Date, unique=True)
    day_of_month: Mapped[int] = mapped_column(Integer)
    month_number: Mapped[int] = mapped_column(Integer)
    quarter_number: Mapped[int] = mapped_column(Integer)
    year_number: Mapped[int] = mapped_column(Integer)


class FactCustomerEvent(Base):
    """Fact table with one row for every customer event."""

    __tablename__ = "fact_customer_event"

    hub_event_key: Mapped[str] = mapped_column(String(64), primary_key=True)
    customer_key: Mapped[int] = mapped_column(
        ForeignKey("dim_customer.customer_key"),
        index=True,
    )
    event_type_key: Mapped[int] = mapped_column(
        ForeignKey("dim_event_type.event_type_key"),
        index=True,
    )
    date_key: Mapped[int] = mapped_column(ForeignKey("dim_date.date_key"), index=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    purchase_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    currency_code: Mapped[str | None] = mapped_column(String(3))
