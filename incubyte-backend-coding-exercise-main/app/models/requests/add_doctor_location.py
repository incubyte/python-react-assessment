from pydantic import BaseModel


class AddDoctorLocationRequest(BaseModel):
    doctor_id: int
    location_id: int
