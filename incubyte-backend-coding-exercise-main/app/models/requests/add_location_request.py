from pydantic import BaseModel


class AddLocationRequest(BaseModel):
    """
    Request model for creating a new location.
    This model validates the data required to add a location record.
    """

    address: str  # The address of the location to be created
