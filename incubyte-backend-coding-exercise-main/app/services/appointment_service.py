from abc import ABC, abstractmethod
from typing import List

from fastapi.exceptions import HTTPException

from app.database.db import DB
from app.models import Appointment
from app.models.error import NotFoundException


class AppointmentService(ABC):
    """
    Abstract base class for appointment services.
    Defines the interface that any appointment service must implement.
    """

    @abstractmethod
    def list_appointments(self, doctor_id: int) -> List[Appointment]:
        """
        Return all appointments for a given doctor.
        """
        ...

    @abstractmethod
    def get_appointment(self, appointment_id: int) -> Appointment:
        """
        Retrieve a single appointment by its ID.
        """
        ...

    @abstractmethod
    def create_appointment(
        self,
        doctor_id: int,
        location_id: int,
        start_time: str,
        end_time: str,
        day_of_week: str,
    ) -> int:
        """
        Create and return the ID of a new appointment.
        """
        ...

    @abstractmethod
    def delete_appointment(self, appointment_id: int) -> None:
        """
        Delete an appointment by its ID.
        """
        ...


class InDatabaseAppointmentService(AppointmentService):
    """
    Implementation of AppointmentService that interacts with a database.
    """

    def __init__(self, db: DB):
        """
        Initialize the service with a database connection.
        """
        self.db = db

    def list_appointments(self, doctor_id: int) -> List[Appointment]:
        """
        Fetches all appointments for a given doctor from the database,
        returning them as a list of `Appointment` Pydantic models.
        """
        dict_result = self.db.execute(
            """
            SELECT a.id, dl.doctor_id, dl.location_id, a.start_time, a.end_time, a.day_of_week
            FROM appointments a
            INNER JOIN doctor_locations dl ON a.doctor_location_id = dl.id
            WHERE dl.doctor_id = ?
            """,
            [doctor_id],
        )
        return [Appointment(**row) for row in dict_result]

    def get_appointment(self, appointment_id: int) -> Appointment:
        """
        Fetches a single appointment by its ID, raising NotFoundException
        if it does not exist.
        """
        dict_result = self.db.execute(
            """
            SELECT a.id, dl.doctor_id, dl.location_id, a.start_time, a.end_time, a.day_of_week
            FROM appointments a
            INNER JOIN doctor_locations dl ON a.doctor_location_id = dl.id
            WHERE a.id = ?
            """,
            [appointment_id],
        )
        if not dict_result:
            raise NotFoundException()
        return Appointment(**dict_result[0])

    def create_appointment(
        self,
        doctor_id: int,
        location_id: int,
        start_time: str,
        end_time: str,
        day_of_week: str,
    ) -> int:

        start_time = start_time.strftime("%Y-%m-%dT%H:%M:%S")
        end_time = end_time.strftime("%Y-%m-%dT%H:%M:%S")

        # Step 1: Ensure the doctor-location association exists
        doctor_location = self.db.execute(
            """
            SELECT id FROM doctor_locations
            WHERE doctor_id = ? AND location_id = ?
            """,
            [doctor_id, location_id],
        )
        if not doctor_location:
            raise HTTPException(
                status_code=400, detail="Invalid doctor or location association."
            )

        doctor_location_id = doctor_location[0]["id"]

        # Step 2: Validate against availability
        availability = self.db.execute(
            """
            SELECT id FROM availability
            WHERE doctor_location_id = ?
            AND day_of_week = ?
            AND start_time <= ?
            AND end_time >= ?
            """,
            [doctor_location_id, day_of_week, start_time, end_time],
        )
        if not availability:
            raise HTTPException(status_code=400, detail="No matching availability.")

        # Step 3: Check for overlapping appointments
        conflict = self.db.execute(
            """
            SELECT id FROM appointments
            WHERE doctor_location_id = ?
            AND NOT (end_time <= ? OR start_time >= ?)
            """,
            [doctor_location_id, start_time, end_time],
        )
        if conflict:
            raise HTTPException(status_code=400, detail="Time slot already booked.")

        # Step 4: Insert new appointment
        self.db.execute(
            """
            INSERT INTO appointments (doctor_location_id, start_time, end_time, day_of_week)
            VALUES (?, ?, ?, ?)
            """,
            [doctor_location_id, start_time, end_time, day_of_week],
        )
        return self.db.last_row_id

    def delete_appointment(self, appointment_id: int) -> None:
        """
        Deletes an existing appointment if it exists,
        otherwise raises NotFoundException.
        """
        # Verify the appointment exists
        self.get_appointment(appointment_id)
        # Delete the appointment
        self.db.execute("DELETE FROM appointments WHERE id = ?", [appointment_id])
