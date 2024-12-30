from abc import ABC, abstractmethod
from typing import List

from fastapi.exceptions import HTTPException

from app.database.db import DB
from app.models import Availability
from app.models.error import NotFoundException


class AvailabilityService(ABC):

    @abstractmethod
    def list_availabilities(self, doctor_id: int) -> List[Availability]:
        """
        Return all availability slots for a given doctor
        """
        ...

    @abstractmethod
    def add_availability(
        self,
        doctor_id: int,
        location_id: int,
        start_time: str,
        end_time: str,
        day_of_week: str,
    ) -> int:
        """
        Create a new availability slot. Returns the id of the new availability row.
        """
        ...

    @abstractmethod
    def get_availability(self, availability_id: int) -> Availability:
        """
        Retrieve a single availability by ID.
        """
        ...

    @abstractmethod
    def delete_availability(self, availability_id: int) -> None:
        """
        Delete a single availability by ID (or raise NotFoundException if not found).
        """
        ...


class InDatabaseAvailabilityService(AvailabilityService):
    def __init__(self, db: DB):
        self.db = db

    def list_availabilities(self, doctor_id: int) -> List[Availability]:
        """
        Returns all availability slots for a given doctor ID.
        """
        dict_result = self.db.execute(
            """
            SELECT a.id, dl.doctor_id, dl.location_id, a.start_time, a.end_time, a.day_of_week
            FROM availability a
            INNER JOIN doctor_locations dl ON a.doctor_location_id = dl.id
            WHERE dl.doctor_id = ?
            """,
            [doctor_id],
        )
        return [Availability(**row) for row in dict_result]

    def add_availability(
        self,
        doctor_id: int,
        location_id: int,
        start_time: str,
        end_time: str,
        day_of_week: str,
    ) -> int:
        """
        Inserts a new availability slot into the DB.
        """

        start_time = start_time.strftime("%Y-%m-%dT%H:%M:%S")
        end_time = end_time.strftime("%Y-%m-%dT%H:%M:%S")

        # Get the doctor_location_id for the given doctor and location
        doctor_location = self.db.execute(
            """
            SELECT id
            FROM doctor_locations
            WHERE doctor_id = ? AND location_id = ?
            """,
            [doctor_id, location_id],
        )

        if not doctor_location:
            raise HTTPException(
                status_code=400,
                detail="Doctor is not associated with the selected location.",
            )

        doctor_location_id = doctor_location[0]["id"]

        # Check for conflicting availabilities
        conflict_availabilities = self.db.execute(
            """
            SELECT id
            FROM availability
            WHERE doctor_location_id = ?
            AND day_of_week = ?
            AND NOT (
                end_time <= ?
                OR
                start_time >= ?
            )
            """,
            [doctor_location_id, day_of_week, start_time, end_time],
        )

        if conflict_availabilities:
            raise HTTPException(
                status_code=400,
                detail="Doctor is already available for that time slot",
            )

        # Insert the new availability
        self.db.execute(
            """
            INSERT INTO availability (doctor_location_id, start_time, end_time, day_of_week)
            VALUES (?, ?, ?, ?)
            """,
            [doctor_location_id, start_time, end_time, day_of_week],
        )
        return self.db.last_row_id

    def get_availability(self, availability_id: int) -> Availability:
        """
        Retrieves a single availability slot by ID, raises NotFoundException if not found.
        """
        dict_result = self.db.execute(
            """
            SELECT a.id, dl.doctor_id, dl.location_id, a.start_time, a.end_time, a.day_of_week
            FROM availability a
            INNER JOIN doctor_locations dl ON a.doctor_location_id = dl.id
            WHERE a.id = ?
            """,
            [availability_id],
        )
        if not dict_result:
            raise NotFoundException("Availability not found.")
        return Availability(**dict_result[0])

    def delete_availability(self, doctor_id: int, availability_id: int) -> None:
        """
        Deletes an availability slot by its ID and associated doctor ID.
        Ensures the availability exists and belongs to the specified doctor.
        """
        # Verify the availability exists and is associated with the specified doctor
        existing = self.db.execute(
            """
            SELECT a.id
            FROM availability a
            INNER JOIN doctor_locations dl ON a.doctor_location_id = dl.id
            WHERE a.id = ? AND dl.doctor_id = ?
            """,
            [availability_id, doctor_id],
        )

        if not existing:
            raise NotFoundException(
                "Availability not found or does not belong to the specified doctor."
            )

        # Delete the availability slot
        self.db.execute(
            """
            DELETE FROM availability
            WHERE id = ?
            """,
            [availability_id],
        )
