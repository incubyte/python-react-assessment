import pytest
from fastapi.testclient import TestClient

from app.settings import Settings


@pytest.fixture(autouse=True, params=[True, False])
def mode(request) -> None:
    """
    Run all the tests in this file in both in_database and in_memory mode.
    """
    Settings.in_database = request.param


def test_get_valid_availability(client: TestClient):
    rv = client.get("/availability/1")
    assert rv.status_code == 200

    data = rv.json()
    assert data["id"] == 1
    assert data["doctor_id"] == 1  # Corrected to match the seed data


def test_get_invalid_availability(client: TestClient):
    # Test retrieving a non-existent availability
    rv = client.get("/availability/99")
    assert rv.status_code == 404


def test_get_all_availabilities_for_doctor(client: TestClient):
    # Test getting all availabilities for a doctor
    rv = client.get("/availability/doctor/0")
    assert rv.status_code == 200

    data = rv.json()
    assert len(data) > 0
    for field in [
        "id",
        "doctor_id",
        "location_id",
        "start_time",
        "end_time",
        "day_of_week",
    ]:
        assert field in data[0]


def test_create_availability(client: TestClient):
    # Test creating an availability slot
    rv = client.post(
        "/availability/",
        json={
            "doctor_id": 0,
            "location_id": 0,
            "start_time": "2025-01-01T09:00:00",
            "end_time": "2025-01-01T10:00:00",
            "day_of_week": "Monday",
        },
    )
    assert rv.status_code == 200

    data = rv.json()
    assert "id" in data


def test_delete_availability(client: TestClient):
    rv = client.delete(
        "/availability/doctor/1?availability_id=2"
    )  # Adjusted doctor_id and availability_id
    assert rv.status_code == 204
