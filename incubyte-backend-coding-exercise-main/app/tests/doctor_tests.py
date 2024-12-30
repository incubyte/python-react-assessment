import pytest
from fastapi.testclient import TestClient

from app.settings import Settings


@pytest.fixture(autouse=True, params=[True, False])
def mode(request) -> None:
    """
    Run all the tests in this file in both in_database and in_memory mode.
    """
    Settings.in_database = request.param


def test_get_all_doctors(client: TestClient):
    # Test listing all doctors
    rv = client.get("/doctors/")
    assert rv.status_code == 200

    data = rv.json()
    assert len(data) > 0
    for field in ["id", "first_name", "last_name"]:
        assert field in data[0]


def test_get_valid_doctor(client: TestClient):
    # Test getting a specific doctor successfully
    rv = client.get("/doctors/0")
    assert rv.status_code == 200

    data = rv.json()
    assert data["id"] == 0
    assert data["first_name"] == "Jane"


def test_get_invalid_doctor(client: TestClient):
    # Test getting a non-existent doctor
    rv = client.get("/doctors/99")
    assert rv.status_code == 404


def test_create_doctor(client: TestClient):
    # Test creating a doctor
    rv = client.post("/doctors/", json={"first_name": "John", "last_name": "Doe"})
    assert rv.status_code == 200

    data = rv.json()
    assert "id" in data


def test_update_doctor(client: TestClient):
    # Test updating a doctor
    rv = client.put("/doctors/0", json={"first_name": "Jane", "last_name": "Smith"})
    assert rv.status_code == 200


def test_delete_doctor(client: TestClient):
    # Test deleting a doctor
    rv = client.delete("/doctors/0")
    assert rv.status_code == 200
