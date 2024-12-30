from typing import List, Optional

from fastapi import APIRouter, FastAPI, HTTPException, Request, Response
from fastapi.responses import RedirectResponse

from app.database.db import DB
from app.models import (
    AddAppointmentRequest,
    AddAvailabilityRequest,
    AddDoctorLocationRequest,
    AddDoctorRequest,
    AddLocationRequest,
    Appointment,
    Availability,
    Doctor,
    Location,
)
from app.models.error import NotFoundException
from app.services import (
    AppointmentService,
    AvailabilityService,
    DoctorService,
    InDatabaseAppointmentService,
    InDatabaseAvailabilityService,
    InDatabaseDoctorService,
    InDatabaseLocationService,
    LocationService,
)


def create_app() -> FastAPI:
    db: Optional[DB] = None

    # Instantiate services
    db = DB()
    db.init_if_needed()

    doctor_service: DoctorService = InDatabaseDoctorService(db=db)
    location_service: LocationService = InDatabaseLocationService(db=db)
    availability_service: AvailabilityService = InDatabaseAvailabilityService(db=db)
    appointment_service: AppointmentService = InDatabaseAppointmentService(db=db)

    # Initialize FastAPI app
    app = FastAPI(swagger_ui_parameters={"tryItOutEnabled": False})

    # Define routers
    doctor_router = APIRouter(tags=["Doctors"])
    location_router = APIRouter(tags=["Locations"])
    availability_router = APIRouter(tags=["Availability"])
    appointment_router = APIRouter(tags=["Appointments"])

    # Doctors Routes
    @doctor_router.get("/", response_model=List[Doctor])
    def list_doctors():
        return doctor_service.list_doctors()

    @doctor_router.get("/{doctor_id}", response_model=Doctor)
    def get_doctor(doctor_id: int):
        try:
            return doctor_service.get_doctor(doctor_id)
        except NotFoundException as exception:
            raise HTTPException(
                status_code=404, detail="Doctor not found"
            ) from exception

    @doctor_router.post("/")
    def add_doctor(request: AddDoctorRequest):
        new_id = doctor_service.add_doctor(
            first_name=request.first_name, last_name=request.last_name
        )
        return {"id": new_id}

    @doctor_router.put("/{doctor_id}")
    def update_doctor(doctor_id: int, request: AddDoctorRequest):
        doctor_service.update_doctor(
            id=doctor_id,
            first_name=request.first_name,
            last_name=request.last_name,
        )
        return {"success": True}

    @doctor_router.delete("/{doctor_id}")
    def delete_doctor(doctor_id: int):
        doctor_service.delete_doctor(doctor_id)
        return {"success": True}

    @doctor_router.get("/{doctor_id}/locations", response_model=List[Location])
    def get_doctor_locations(doctor_id: int):
        return doctor_service.list_doctor_locations(doctor_id=doctor_id)

    # Locations Routes
    @location_router.get("/", response_model=List[Location])
    def list_locations():
        return location_service.list_locations()

    @location_router.get("/{location_id}", response_model=Location)
    def get_location(location_id: int):
        try:
            return location_service.get_location(location_id)
        except NotFoundException as exception:
            raise HTTPException(
                status_code=404, detail="Location not found"
            ) from exception

    @location_router.post("/")
    def add_location(request: AddLocationRequest):
        new_id = location_service.add_location(address=request.address)
        return {"id": new_id}

    @location_router.post("/associate-doctor-location")
    def associate_doctor_location(request: AddDoctorLocationRequest):
        """
        Endpoint to associate a doctor with a location.
        """
        # Check if the doctor exists
        try:
            doctor_service.get_doctor(request.doctor_id)
        except NotFoundException:
            raise HTTPException(
                status_code=404, detail=f"Doctor with id {request.doctor_id} not found"
            )

        # Check if the location exists
        try:
            location_service.get_location(request.location_id)
        except NotFoundException:
            raise HTTPException(
                status_code=404,
                detail=f"Location with id {request.location_id} not found",
            )

        # Add association
        new_id = location_service.add_doctor_location(
            doctor_id=request.doctor_id, location_id=request.location_id
        )
        return {"id": new_id, "message": "Doctor successfully associated with location"}

    @location_router.delete("/deassociate-doctor-location")
    def deassociate_doctor_location(doctor_id: int, location_id: int):
        """
        Endpoint to deassociate a doctor from a location.
        """
        # Check if the doctor exists
        try:
            doctor_service.get_doctor(doctor_id)
        except NotFoundException:
            raise HTTPException(
                status_code=404, detail=f"Doctor with id {doctor_id} not found"
            )

        # Check if the location exists
        try:
            location_service.get_location(location_id)
        except NotFoundException:
            raise HTTPException(
                status_code=404, detail=f"Location with id {location_id} not found"
            )

        # Attempt to remove the association
        try:
            location_service.remove_doctor_location(
                doctor_id=doctor_id, location_id=location_id
            )
        except NotFoundException:
            raise HTTPException(
                status_code=404,
                detail=f"Association between doctor {doctor_id} and location {location_id} not found",
            )

        return {"message": "Doctor successfully deassociated from location"}

    # Availability Routes
    @availability_router.get("/doctor/{doctor_id}", response_model=List[Availability])
    def list_doctor_availabilities(doctor_id: int):
        return availability_service.list_availabilities(doctor_id)

    @availability_router.get("/{availability_id}", response_model=Availability)
    def get_availability(availability_id: int):
        try:
            return availability_service.get_availability(availability_id)
        except NotFoundException as exception:
            raise HTTPException(
                status_code=404, detail="Availability not found"
            ) from exception

    @availability_router.post("/")
    def add_availability(request: AddAvailabilityRequest):
        new_id = availability_service.add_availability(
            doctor_id=request.doctor_id,
            location_id=request.location_id,
            start_time=request.start_time,
            end_time=request.end_time,
            day_of_week=request.day_of_week,
        )
        return {"id": new_id}

    @availability_router.delete("/doctor/{doctor_id}", status_code=204)
    def delete_availability_by_doctor(doctor_id: int, availability_id: int):
        availability_service.delete_availability(
            doctor_id=doctor_id, availability_id=availability_id
        )
        return None

    # Appointments Routes
    @appointment_router.get("/doctor/{doctor_id}", response_model=List[Appointment])
    def list_doctor_appointments(doctor_id: int):
        return appointment_service.list_appointments(doctor_id)

    @appointment_router.get("/{appointment_id}", response_model=Appointment)
    def get_appointment(appointment_id: int):
        try:
            return appointment_service.get_appointment(appointment_id)
        except NotFoundException as exception:
            raise HTTPException(
                status_code=404, detail="Appointment not found"
            ) from exception

    @appointment_router.post("/")
    def create_appointment(request: AddAppointmentRequest):
        new_id = appointment_service.create_appointment(
            doctor_id=request.doctor_id,
            location_id=request.location_id,
            start_time=request.start_time,
            end_time=request.end_time,
            day_of_week=request.day_of_week,
        )
        return {"id": new_id}

    @appointment_router.delete("/{appointment_id}", status_code=204)
    def delete_appointment(appointment_id: int):
        appointment_service.delete_appointment(appointment_id)
        return None

    # Register routes
    app.include_router(doctor_router, prefix="/doctors")
    app.include_router(location_router, prefix="/locations")
    app.include_router(availability_router, prefix="/availability")
    app.include_router(appointment_router, prefix="/appointments")

    # Exception Handlers
    @app.exception_handler(NotFoundException)
    async def not_found(request: Request, exc: NotFoundException):
        return Response(status_code=404)

    @app.on_event("shutdown")
    def shutdown():
        if db:
            db.close_db()

    @app.get("/", include_in_schema=False)
    def root():
        return RedirectResponse("/docs")

    return app


main_app = create_app()
