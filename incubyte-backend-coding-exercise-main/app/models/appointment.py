from pydantic import BaseModel


class Appointment(BaseModel):
    """
    Represents a booked appointment for a doctor at a given location.
    This model is used to define the structure of an appointment record.
    """

    id: int  # Unique identifier for the appointment
    doctor_id: int  # Identifier for the doctor associated with the appointment
    location_id: int  # Identifier for the location where the appointment will occur
    start_time: str  # Start time of the appointment, represented as a string
    end_time: str  # End time of the appointment, represented as a string
    day_of_week: str  # e.g., "Monday"
