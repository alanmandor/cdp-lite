"""Tests for loading the Kimball customer-event mart."""

from fastapi.testclient import TestClient


def test_mart_load_creates_dimensions_and_event_fact(client: TestClient) -> None:
    profile_response = client.post(
        "/profiles",
        json={"external_id": "customer-123", "email": "alice@example.com"},
    )
    assert profile_response.status_code == 201
    event_response = client.post(
        "/profiles/customer-123/events",
        json={"event_type": "purchase", "event_data": {"amount": 49.99}},
    )
    assert event_response.status_code == 201
    vault_response = client.post("/warehouse/vault/load")
    assert vault_response.status_code == 200

    response = client.post("/warehouse/mart/load")

    assert response.status_code == 200
    assert response.json()["customer_dimension_rows_created"] == 1
    assert response.json()["event_type_dimension_rows_created"] == 1
    assert response.json()["date_dimension_rows_created"] == 1
    assert response.json()["event_facts_created"] == 1


def test_mart_load_is_idempotent(client: TestClient) -> None:
    profile_response = client.post(
        "/profiles",
        json={"external_id": "customer-123"},
    )
    assert profile_response.status_code == 201
    vault_response = client.post("/warehouse/vault/load")
    assert vault_response.status_code == 200
    first_load = client.post("/warehouse/mart/load")
    second_load = client.post("/warehouse/mart/load")

    assert first_load.status_code == 200
    assert second_load.status_code == 200
    assert second_load.json() == {
        "customer_dimension_rows_created": 0,
        "event_type_dimension_rows_created": 0,
        "date_dimension_rows_created": 0,
        "event_facts_created": 0,
    }
