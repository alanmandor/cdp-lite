"""Tests for Type 2 customer history in the Kimball mart."""

from fastapi.testclient import TestClient


def test_profile_change_creates_a_new_type_2_dimension_version(
    client: TestClient,
) -> None:
    create_response = client.post(
        "/profiles",
        json={"external_id": "customer-123", "email": "old@example.com"},
    )
    assert create_response.status_code == 201
    assert client.post("/warehouse/vault/load").status_code == 200
    assert client.post("/warehouse/mart/load").status_code == 200

    update_response = client.put(
        "/profiles/customer-123",
        json={"email": "new@example.com"},
    )
    assert update_response.status_code == 200
    vault_response = client.post("/warehouse/vault/load")
    mart_response = client.post("/warehouse/mart/load")

    assert vault_response.json()["customer_satellites_created"] == 1
    assert mart_response.json()["customer_dimension_rows_created"] == 1

    history_response = client.get("/analytics/customer-history/customer-123")

    assert history_response.status_code == 200
    history = history_response.json()
    assert [version["email"] for version in history] == [
        "old@example.com",
        "new@example.com",
    ]
    assert [version["is_current"] for version in history] == [False, True]
    assert history[0]["effective_to"] is not None
    assert history[1]["effective_to"] is None
