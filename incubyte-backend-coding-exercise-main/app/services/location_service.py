from abc import ABC, abstractmethod
from typing import List

from fastapi.exceptions import HTTPException

from app.database.db import DB
from app.models import Location
from app.models.error import NotFoundException


class LocationService(ABC):
    """
    Abstract base class for managing locations.
    Defines the interface for listing, retrieving, and adding locations.
    """

    @abstractmethod
    def list_locations(self) -> List[Location]:
        """
        Retrieve a list of all locations.
        """
        ...

    @abstractmethod
    def get_location(self, id: int) -> Location:
        """
        Retrieve a specific location by its ID.
        """
        ...

    @abstractmethod
    def add_location(self, address: str) -> int:
        """
        Add a new location and return its ID.
        """
        ...

    @abstractmethod
    def add_doctor_location(self, doctor_id: int, location_id: int) -> int:
        """
        Add a new association between location and doctor and return its ID.
        """
        ...

    @abstractmethod
    def remove_doctor_location(self, doctor_id: int, location_id: int) -> None:
        """
        Remove already associated link between location and doctor and return its ID.
        """
        ...


class InDatabaseLocationService(LocationService):
    """
    Database-backed implementation of LocationService.
    Handles all location-related operations by interacting with a database.
    """

    def __init__(self, db: DB):
        """
        Initialize the service with a database connection.
        """
        self.db = db

    def list_locations(self) -> List[Location]:
        """
        Retrieve all locations from the database.
        """
        dict_result = self.db.execute("SELECT id, address FROM locations")
        return [Location(**row) for row in dict_result]

    def get_location(self, id: int) -> Location:
        """
        Retrieve a single location by its ID, or raise NotFoundException if not found.
        """
        dict_result = self.db.execute(
            "SELECT id, address FROM locations WHERE id = ?", [id]
        )
        if not dict_result:
            raise NotFoundException()
        return Location(**dict_result[0])

    def add_location(self, address: str) -> int:
        """
        Add a new location to the database. Checks for duplicates before adding.
        Returns the ID of the newly created location.
        """
        duplicate_locations = self.db.execute(
            """
            SELECT *
            FROM locations
            WHERE address = ?
            """,
            [address],
        )

        if duplicate_locations:
            # Raise an exception if the location already exists
            raise HTTPException(
                status_code=400,
                detail=f"Location already exists in the database: {address}",
            )

        # Insert the new location
        self.db.execute("INSERT INTO locations (address) VALUES (?)", [address])
        new_id = self.db.last_row_id
        return new_id

    def add_doctor_location(self, doctor_id: int, location_id: int) -> int:
        """
        Add an association between a doctor and a location.
        """
        # Check if the association already exists
        existing_association = self.db.execute(
            """
                SELECT id
                FROM doctor_locations
                WHERE doctor_id = ? AND location_id = ?
                """,
            [doctor_id, location_id],
        )
        if existing_association:
            raise HTTPException(
                status_code=400,
                detail="Doctor is already associated with this location",
            )

        # Insert the association
        self.db.execute(
            """
                INSERT INTO doctor_locations (doctor_id, location_id)
                VALUES (?, ?)
                """,
            [doctor_id, location_id],
        )
        return self.db.last_row_id

    def remove_doctor_location(self, doctor_id: int, location_id: int) -> None:
        """
        Remove an association between a doctor and a location.
        """
        # Check if the association exists
        existing_association = self.db.execute(
            """
            SELECT id
            FROM doctor_locations
            WHERE doctor_id = ? AND location_id = ?
            """,
            [doctor_id, location_id],
        )
        if not existing_association:
            raise NotFoundException("Doctor-location association does not exist")

        # Delete the association
        self.db.execute(
            """
            DELETE FROM doctor_locations
            WHERE doctor_id = ? AND location_id = ?
            """,
            [doctor_id, location_id],
        )
