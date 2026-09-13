"""Tests for analytics endpoints backed by the Kimball mart."""

from fastapi.testclient import TestClient


def load_mart_with_events(client: TestClient) -> None:
    profile_response = client.post(
        "/profiles",
        json={"external_id": "customer-123"},
    )
    assert profile_response.status_code == 201
    first_event_response = client.post(
        "/profiles/customer-123/events",
        json={"event_type": "page_view", "occurred_at": "2026-09-10T10:00:00Z"},
    )
    assert first_event_response.status_code == 201
    second_event_response = client.post(
        "/profiles/customer-123/events",
        json={"event_type": "purchase", "occurred_at": "2026-09-11T12:00:00Z"},
    )
    assert second_event_response.status_code == 201
    third_event_response = client.post(
        "/profiles/customer-123/events",
        json={"event_type": "purchase", "occurred_at": "2026-09-11T13:00:00Z"},
    )
    assert third_event_response.status_code == 201
    vault_response = client.post("/warehouse/vault/load")
    assert vault_response.status_code == 200
    mart_response = client.post("/warehouse/mart/load")
    assert mart_response.status_code == 200


def test_event_summary_aggregates_mart_facts(client: TestClient) -> None:
    load_mart_with_events(client)

    response = client.get("/analytics/event-summary")

    assert response.status_code == 200
    assert response.json() == [
        {
            "calendar_date": "2026-09-10",
            "event_type": "page_view",
            "event_count": 1,
        },
        {
            "calendar_date": "2026-09-11",
            "event_type": "purchase",
            "event_count": 2,
        },
    ]


def test_event_summary_filters_by_date_range(client: TestClient) -> None:
    load_mart_with_events(client)

    response = client.get(
        "/analytics/event-summary?start_date=2026-09-11&end_date=2026-09-11",
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "calendar_date": "2026-09-11",
            "event_type": "purchase",
            "event_count": 2,
        },
    ]


def test_event_summary_rejects_an_invalid_date_range(client: TestClient) -> None:
    response = client.get(
        "/analytics/event-summary?start_date=2026-09-12&end_date=2026-09-11",
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "start_date must be on or before end_date."
