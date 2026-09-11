"""Tests for loading operational data into the Data Vault."""

from fastapi.testclient import TestClient


def test_vault_load_creates_hubs_links_and_satellites(client: TestClient) -> None:
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

    response = client.post("/warehouse/vault/load")

    assert response.status_code == 200
    assert response.json() == {
        "hub_customers_created": 1,
        "hub_events_created": 1,
        "customer_event_links_created": 1,
        "customer_satellites_created": 1,
        "event_satellites_created": 1,
    }


def test_vault_load_is_idempotent(client: TestClient) -> None:
    profile_response = client.post(
        "/profiles",
        json={"external_id": "customer-123"},
    )
    assert profile_response.status_code == 201

    first_load = client.post("/warehouse/vault/load")
    second_load = client.post("/warehouse/vault/load")

    assert first_load.status_code == 200
    assert second_load.status_code == 200
    assert second_load.json() == {
        "hub_customers_created": 0,
        "hub_events_created": 0,
        "customer_event_links_created": 0,
        "customer_satellites_created": 0,
        "event_satellites_created": 0,
    }
