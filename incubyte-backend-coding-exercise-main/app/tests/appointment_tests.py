import pytest
from fastapi.testclient import TestClient

from app.settings import Settings


@pytest.fixture(autouse=True, params=[True, False])
def mode(request) -> None:
    """
    Run all the tests in this file in both in_database and in_memory mode.
    """
    Settings.in_database = request.param


def test_get_valid_appointment(client: TestClient):
    rv = client.get("/appointments/1")
    assert rv.status_code == 200

    data = rv.json()
    assert data["id"] == 1
    assert data["doctor_id"] == 1
    assert data["location_id"] == 1


def test_get_invalid_appointment(client: TestClient):
    # Test retrieving a non-existent appointment
    rv = client.get("/appointments/99")
    assert rv.status_code == 404


def test_get_all_appointments_for_doctor(client: TestClient):
    # Test listing all appointments for a doctor
    rv = client.get("/appointments/doctor/0")
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


def test_create_appointment(client: TestClient):
    rv = client.post(
        "/appointments/",
        json={
            "doctor_id": 1,
            "location_id": 1,
            "start_time": "2025-01-01T12:00:00",
            "end_time": "2025-01-01T12:30:00",
            "day_of_week": "Wednesday",
        },
    )
    assert rv.status_code == 200
    data = rv.json()
    assert "id" in data


def test_delete_appointment(client: TestClient):
    # Test deleting an appointment
    rv = client.delete("/appointments/1")
    assert rv.status_code == 204
