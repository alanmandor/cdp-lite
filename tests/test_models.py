"""Tests for database models."""

from sqlalchemy import create_engine, inspect

from app.db import Base
from app.models import CustomerProfile


def test_customer_profiles_table_can_be_created() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")

    Base.metadata.create_all(bind=engine)

    assert "customer_profiles" in inspect(engine).get_table_names()


def test_customer_profile_exposes_core_attributes() -> None:
    profile = CustomerProfile(
        external_id="customer-123",
        email="alice@example.com",
        first_name="Alice",
        last_name="Smith",
    )

    assert profile.external_id == "customer-123"
    assert profile.email == "alice@example.com"
    assert profile.first_name == "Alice"
    assert profile.last_name == "Smith"
