
# Deps
from fastapi import APIRouter, status, Query, Depends
router = APIRouter(prefix="/cars", tags=["Cars"])

# Models
from uuid import UUID
from ....models.validations.items import Car, CarUpdateReq, RentalStatus, RentalStatusEnum, CarModel, Rental
from typing import List, Optional

# Functionality
from uuid import uuid4
from ....services.car_service import CarService

# Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session

# TODO: Remove!
test = Car(id=uuid4(), model=CarModel(company='hyundai', name='tiburon', year=2005), status=RentalStatus(status="available"))

# GET ------------------
# Get a car by id
@router.get("/{car_id}", response_model=Car, status_code=status.HTTP_200_OK)
async def get_car_by_id(car_id: UUID,
                        db: AsyncSession = Depends(get_db_session)):

    car = await CarService.get_one_by_id(db=db, id=car_id)
    return car

@router.get("/", response_model=List[Car], status_code=status.HTTP_200_OK)
async def get_all_cars(status_filter: Optional[RentalStatusEnum] = Query(None, description="Filter by car rental status"),
                       db: AsyncSession = Depends(get_db_session)):

    # Query db for all cars with filter using the car Service
    cars = await CarService.get_all(db=db, status_filter=status_filter)
    print(f"cars: {cars}")

    # conditional filter for status col
    if status_filter:
        pass # do something

    return cars

# POST ------------------
# Add a new car
@router.post("/", response_model=Car, status_code=status.HTTP_201_CREATED)
async def add_car(car: Car,
                  db: AsyncSession = Depends(get_db_session)):

    new_car = await CarService.add_one(db=db, car=car)
    print("yahahahah")
    return car


# PATCH ----------------
# Update existing car based on id
@router.patch("/{car_id}", response_model=Car, status_code=status.HTTP_200_OK)
async def update_car_by_id(car_id: UUID, update_req: CarUpdateReq,
                           db: AsyncSession = Depends(get_db_session)):

    patched_car = await CarService.update_one_by_id(db=db, id=car_id, update_req=update_req)
    return patched_car


# DELETE --------------
# Delete existing car
@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car_by_id(car_id: UUID,
                           db: AsyncSession = Depends(get_db_session)):

    successfully_deleted = await CarService.update_one_by_id(db=db, id=car_id)
    return None

