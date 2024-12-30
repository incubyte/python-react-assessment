from datetime import datetime

from pydantic import BaseModel


class AddAppointmentRequest(BaseModel):
    """
    Request model for booking an appointment.
    This class validates and ensures that the data for booking an appointment
    meets the expected structure and types.
    """

    doctor_id: int  # The ID of the doctor the appointment is booked with
    location_id: int  # The ID of the location where the appointment will take place
    start_time: datetime  # The start time of the appointment in datetime format
    end_time: datetime  # The end time of the appointment in datetime format
    day_of_week: str  # e.g., "Monday"
