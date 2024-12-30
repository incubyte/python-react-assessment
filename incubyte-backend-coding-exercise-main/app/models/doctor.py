from typing import List

from pydantic import BaseModel


class Doctor(BaseModel):
    """
    Represents a doctor in the system.
    """

    id: int  # Unique identifier for the doctor
    first_name: str  # First name of the doctor
    last_name: str  # Last name of the doctor


class Location(BaseModel):
    """
    Represents a physical location where doctors provide services.
    """

    id: int  # Unique identifier for the location
    address: str  # Address of the location


class DoctorLocation(BaseModel):
    """
    Represents the association between a doctor and a location.
    This indicates that a doctor works at a location. Locations can have
    multiple doctors, and doctors can work at multiple locations.
    """

    id: int  # Unique identifier for the doctor-location association
    doctor_id: int  # Identifier for the doctor
    location_id: int  # Identifier for the location
