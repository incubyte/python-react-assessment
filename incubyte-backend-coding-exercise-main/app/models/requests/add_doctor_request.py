from pydantic import BaseModel


class AddDoctorRequest(BaseModel):
    """
    Request model for adding a new doctor.
    This model validates the data required to create a doctor record.
    """

    first_name: str  # The first name of the doctor
    last_name: str  # The last name of the doctor
