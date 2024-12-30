from abc import ABC, abstractmethod
from typing import List, Optional

from fastapi.exceptions import HTTPException

from app.database.db import DB
from app.models import Doctor, DoctorLocation, Location
from app.models.error import NotFoundException


class DoctorService(ABC):
    """
    Abstract base class defining the interface for doctor-related operations.
    """

    @abstractmethod
    def list_doctors(self) -> List[Doctor]:
        """
        Retrieve a list of all doctors.
        """
        ...

    @abstractmethod
    def get_doctor(self, id: int) -> Doctor:
        """
        Retrieve details of a single doctor by ID.
        """
        ...

    @abstractmethod
    def add_doctor(self, first_name: str, last_name: str) -> int:
        """
        Add a new doctor to the system and return their ID.
        """
        ...

    @abstractmethod
    def list_doctor_locations(self, doctor_id: int) -> List[Location]:
        """
        Retrieve all locations associated with a given doctor.
        """
        ...

    @abstractmethod
    def update_doctor(
        self, id: int, first_name: Optional[str], last_name: Optional[str]
    ) -> None:
        """
        Update a doctor's details by ID.
        """
        ...

    @abstractmethod
    def delete_doctor(self, id: int) -> None:
        """
        Delete a doctor by ID.
        """
        ...


class InMemoryDoctorService(DoctorService):
    """
    In-memory implementation of the DoctorService.
    Used for testing or scenarios without a database.
    """

    def __init__(self) -> None:
        self.doctors: List[Doctor] = []
        self.locations: List[Location] = []
        self.doctor_locations: List[DoctorLocation] = []

    def seed(self):
        """
        Seed the in-memory storage with initial test data.
        """
        self.doctors.extend(
            [
                {"id": 0, "first_name": "Jane", "last_name": "Wright"},
                {"id": 1, "first_name": "Joseph", "last_name": "Lister"},
            ]
        )

        self.locations.extend(
            [
                {"id": 0, "address": "1 Park St"},
                {"id": 1, "address": "2 University Ave"},
            ]
        )

        self.doctor_locations.extend(
            [
                {"id": 0, "doctor_id": 0, "location_id": 0},
                {"id": 1, "doctor_id": 1, "location_id": 0},
                {"id": 2, "doctor_id": 1, "location_id": 1},
            ]
        )

    def list_doctors(self) -> List[Doctor]:
        """
        Return the list of all doctors in memory.
        """
        return self.doctors

    def get_doctor(self, id: int) -> Doctor:
        """
        Retrieve a doctor by ID, or raise NotFoundException if not found.
        """
        if id < 0 or id >= len(self.doctors):
            raise NotFoundException()
        return self.doctors[id]

    def add_doctor(self, first_name: str, last_name: str) -> int:
        """
        Add a new doctor and return their ID.
        """
        new_doctor = Doctor(
            id=len(self.doctors), first_name=first_name, last_name=last_name
        )
        self.doctors.append(new_doctor)
        return new_doctor.id

    def list_doctor_locations(self, doctor_id: int) -> List[Location]:
        """
        List all locations associated with a given doctor ID.
        """
        if doctor_id < 0 or doctor_id >= len(self.doctors):
            raise NotFoundException()

        location_ids = [
            doctor_loc.location_id
            for doctor_loc in self.doctor_locations
            if doctor_loc.doctor_id == doctor_id
        ]
        return [loc for loc in self.locations if loc.id in location_ids]


class InDatabaseDoctorService(DoctorService):
    """
    Database-backed implementation of the DoctorService.
    """

    def __init__(self, db: DB):
        self.db = db

    def list_doctors(self) -> List[Doctor]:
        """
        Retrieve all doctors from the database.
        """
        dict_result = self.db.execute("SELECT id, first_name, last_name FROM doctors")
        return [Doctor(**res) for res in dict_result]

    def get_doctor(self, id: int) -> Doctor:
        """
        Retrieve a single doctor by ID, or raise NotFoundException if not found.
        """
        dict_result = self.db.execute(
            "SELECT id, first_name, last_name FROM doctors WHERE id = ?", [id]
        )
        if not dict_result:
            raise NotFoundException()
        if len(dict_result) > 1:
            raise Exception("Found more than one doctor with that ID")
        return Doctor(**dict_result[0])

    def add_doctor(self, first_name: str, last_name: str) -> int:
        """
        Add a new doctor to the database, ensuring no duplicate exists.
        """
        conflict_doctors = self.db.execute(
            """
            SELECT *
            FROM doctors
            WHERE first_name = ?
            AND last_name = ?
            """,
            [first_name, last_name],
        )
        if conflict_doctors:
            raise HTTPException(
                status_code=400,
                detail=f"Doctor: {first_name} {last_name} already exists in the database",
            )
        self.db.execute(
            "INSERT INTO doctors (first_name, last_name) VALUES (?, ?)",
            [first_name, last_name],
        )
        _id = self.db.last_row_id
        assert _id
        return _id

    def list_doctor_locations(self, doctor_id: int) -> List[Location]:
        """
        Retrieve all locations associated with a specific doctor from the database.
        """
        dict_result = self.db.execute(
            """
            SELECT l.id, l.address
            FROM doctor_locations dl
            INNER JOIN locations l ON dl.location_id = l.id
            WHERE dl.doctor_id = ?
            """,
            [doctor_id],
        )

        # Handle case where no locations are found
        if not dict_result:
            raise NotFoundException(
                f"No locations found for doctor with ID {doctor_id}."
            )

        # Convert results to a list of Location models
        return [Location(**res) for res in dict_result]

    def update_doctor(
        self, id: int, first_name: Optional[str], last_name: Optional[str]
    ) -> None:
        """
        Update the details of an existing doctor.
        """
        existing_doctor = self.get_doctor(id)
        if not existing_doctor:
            raise NotFoundException()

        self.db.execute(
            """
            UPDATE doctors
            SET first_name = COALESCE(?, first_name),
                last_name = COALESCE(?, last_name)
            WHERE id = ?
            """,
            [first_name, last_name, id],
        )

    def delete_doctor(self, id: int) -> None:
        """
        Delete a doctor from the database.
        """
        existing_doctor = self.get_doctor(id)
        if not existing_doctor:
            raise NotFoundException()

        self.db.execute("DELETE FROM doctors WHERE id = ?", [id])
