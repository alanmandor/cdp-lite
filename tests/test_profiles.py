"""Tests for customer profile endpoints."""

from fastapi.testclient import TestClient


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
