"""Tests for dynamic customer segments."""

from fastapi.testclient import TestClient


def create_profile(client: TestClient, external_id: str, email: str | None) -> None:
    response = client.post(
        "/profiles",
        json={"external_id": external_id, "email": email},
    )
    assert response.status_code == 201


def test_segment_filters_profiles_by_email_and_event_type(client: TestClient) -> None:
    create_profile(client, "purchaser", "buyer@example.com")
    create_profile(client, "visitor", "visitor@example.com")
    create_profile(client, "anonymous", None)
    event_response = client.post(
        "/profiles/purchaser/events",
        json={"event_type": "purchase"},
    )
    assert event_response.status_code == 201

    response = client.get("/segments?has_email=true&event_type=purchase")

    assert response.status_code == 200
    assert [profile["external_id"] for profile in response.json()] == ["purchaser"]


def test_segment_filters_profiles_without_an_email(client: TestClient) -> None:
    create_profile(client, "identified", "person@example.com")
    create_profile(client, "anonymous", None)

    response = client.get("/segments?has_email=false")

    assert response.status_code == 200
    assert [profile["external_id"] for profile in response.json()] == ["anonymous"]


def test_segment_without_criteria_returns_all_profiles(client: TestClient) -> None:
    create_profile(client, "first", None)
    create_profile(client, "second", "second@example.com")

    response = client.get("/segments")

    assert response.status_code == 200
    assert [profile["external_id"] for profile in response.json()] == ["first", "second"]
