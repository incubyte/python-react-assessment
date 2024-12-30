import pytest
from fastapi.testclient import TestClient

from app.settings import Settings


@pytest.fixture(autouse=True, params=[True, False])
def mode(request) -> None:
    """
    Run all the tests in this file in both in_database and in_memory mode.
    """
    Settings.in_database = request.param


def test_get_all_locations(client: TestClient):
    # Test listing all locations
    rv = client.get("/locations/")
    assert rv.status_code == 200

    data = rv.json()
    assert len(data) > 0
    for field in ["id", "address"]:
        assert field in data[0]


def test_get_valid_location(client: TestClient):
    # Test getting a valid location
    rv = client.get("/locations/0")
    assert rv.status_code == 200

    data = rv.json()
    assert data["id"] == 0
    assert "address" in data


def test_get_invalid_location(client: TestClient):
    # Test getting an invalid location
    rv = client.get("/locations/99")
    assert rv.status_code == 404


def test_create_location(client: TestClient):
    # Test creating a new location
    rv = client.post("/locations/", json={"address": "123 New St"})
    assert rv.status_code == 200

    data = rv.json()
    assert "id" in data


def test_associate_doctor_with_location(client: TestClient):
    # Test associating a doctor with a location
    rv = client.post(
        "/locations/associate-doctor-location",
        json={"doctor_id": 0, "location_id": 1},
    )
    assert rv.status_code == 200
    data = rv.json()
    assert data["message"] == "Doctor successfully associated with location"


def test_deassociate_doctor_from_location(client: TestClient):
    rv = client.delete(
        "/locations/deassociate-doctor-location",
        params={"doctor_id": 1, "location_id": 1},  # Use params instead of json
    )
    assert rv.status_code == 200
    assert rv.json()["message"] == "Doctor successfully deassociated from location"
