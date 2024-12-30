from datetime import datetime

from pydantic import BaseModel


class AddAvailabilityRequest(BaseModel):
    """
    Request model for adding an availability slot for a doctor.
    This class ensures that the data provided for a doctor's availability
    adheres to the required structure and data types.
    """

    doctor_id: int  # The unique identifier of the doctor
    location_id: int  # The unique identifier of the location
    start_time: datetime  # The start time of the availability slot
    end_time: datetime  # The end time of the availability slot
    day_of_week: str  # e.g., "Monday"
