"""Tests for customer profile endpoints."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def test_create_and_retrieve_profile(client: TestClient) -> None:
    payload = {
        "external_id": "customer-123",
        "email": "alice@example.com",
        "first_name": "Alice",
        "last_name": "Smith",
    }

    create_response = client.post("/profiles", json=payload)

    assert create_response.status_code == 201
    assert create_response.json()["external_id"] == "customer-123"
    assert create_response.json()["email"] == "alice@example.com"

    get_response = client.get("/profiles/customer-123")

    assert get_response.status_code == 200
    assert get_response.json()["first_name"] == "Alice"


def test_create_profile_rejects_duplicate_external_id(client: TestClient) -> None:
    payload = {"external_id": "customer-123"}
    client.post("/profiles", json=payload)

    response = client.post("/profiles", json=payload)

    assert response.status_code == 409
    assert response.json()["detail"] == "A profile with this external_id already exists."


def test_get_profile_returns_not_found_for_unknown_external_id(client: TestClient) -> None:
    response = client.get("/profiles/unknown-customer")

    assert response.status_code == 404
    assert response.json()["detail"] == "Profile not found."
