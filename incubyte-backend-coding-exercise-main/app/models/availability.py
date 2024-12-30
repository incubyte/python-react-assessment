from pydantic import BaseModel


class Availability(BaseModel):
    """
    Represents a single availability slot for a doctor at a given location.
    This model is used to define the structure of an availability record.
    """

    id: int  # Unique identifier for the availability slot
    doctor_id: int  # Identifier for the doctor associated with the availability
    location_id: int  # Identifier for the location where the availability is applicable
    start_time: str  # Start time of the availability slot, represented as a string
    end_time: str  # End time of the availability slot, represented as a string
    day_of_week: str  # e.g., "Monday"
