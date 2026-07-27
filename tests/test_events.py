"""Tests for customer event endpoints."""

from fastapi.testclient import TestClient


def create_profile(client: TestClient) -> None:
    response = client.post("/profiles", json={"external_id": "customer-123"})
    assert response.status_code == 201


def test_record_and_list_customer_events(client: TestClient) -> None:
    create_profile(client)
    payload = {
        "event_type": "purchase",
        "event_data": {"amount": 49.99, "currency": "USD"},
    }

    create_response = client.post("/profiles/customer-123/events", json=payload)

    assert create_response.status_code == 201
    assert create_response.json()["event_type"] == "purchase"
    assert create_response.json()["event_data"] == {
        "amount": 49.99,
        "currency": "USD",
    }

    list_response = client.get("/profiles/customer-123/events")

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert list_response.json()[0]["event_type"] == "purchase"


def test_record_event_returns_not_found_for_unknown_profile(client: TestClient) -> None:
    response = client.post(
        "/profiles/unknown-customer/events",
        json={"event_type": "page_view"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Profile not found."
