
# Deps
from fastapi import APIRouter, status
router = APIRouter(prefix="/cars", tags=["cars"])

# Models
from uuid import UUID
from ....models.validations.items import Car, CarUpdateReq, RentalStatus, CarModel
from typing import List

# Functionality
from uuid import uuid4

# TODO: Remove!
test = Car(id=uuid4(), model=CarModel(company='hyundai', name='tiburon', year=2005), status=RentalStatus(status="available"))

# GET ------------------
# Get a car by id
@router.get("/{car_id}", response_model=Car, status_code=status.HTTP_200_OK)
async def get_car_by_id(car_id: UUID):

    car = test
    return car

@router.get("/", response_model=List[Car], status_code=status.HTTP_200_OK)
async def get_all_cars():

    cars = [test]
    return cars


# POST ------------------
# Add a new car
@router.post("/", response_model=Car, status_code=status.HTTP_201_CREATED)
async def add_car(car: Car):

    car = car
    return car


# PATCH ----------------
# Update existing car based on id
@router.patch("/{car_id}", response_model=Car, status_code=status.HTTP_200_OK)
async def update_car_by_id(car_id: UUID, update_req: CarUpdateReq):

    car = test
    return car


# DELETE --------------
# Delete existing car
@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car_by_id(car_id: UUID):
    return None

