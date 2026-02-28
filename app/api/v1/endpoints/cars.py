
# Routing
from fastapi import APIRouter, status, Query, Depends
router = APIRouter(prefix="/cars", tags=["Cars"])

# Models
from uuid import UUID
from ....models.validations.items import Car, CarUpdateReq, RentalStatusEnum
from ....models.validations.responses import GetAllCarsResponse
from typing import List, Optional

# Functionality
from ....services.car_service import CarService

# Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session

# Observability
from ....core.logger import logger

# GET ------------------
# Get a car by id
@router.get("/{car_id}", response_model=Car, status_code=status.HTTP_200_OK)
async def get_car_by_id(car_id: UUID,
                        db: AsyncSession = Depends(get_db_session)):

    logger.info(f"Fetching Car with id: {car_id}")
    car = await CarService.get_one_by_id(db=db, car_id=car_id)
    logger.info(f"Found Car with id: {car_id}")
    return car

@router.get("/", response_model=GetAllCarsResponse, status_code=status.HTTP_200_OK)
async def get_all_cars(status_filter: Optional[RentalStatusEnum] = Query(None, description="Filter by car rental status"),
                       db: AsyncSession = Depends(get_db_session)):

    # Query db for all cars with filter using the car Service
    logger.info(f"Fetching all Cars with status: {status_filter.value if status_filter else 'ANY'}")
    cars = await CarService.get_all(db=db, status_filter=status_filter)
    resp = {"length": len(cars),
            "filter": status_filter,
            "cars":cars
            }
    logger.info(f"Found {resp['length']} Cars with Status: {status_filter.value if status_filter else 'ANY'}")
    return resp

# POST ------------------
# Add a new car
@router.post("/", response_model=Car, status_code=status.HTTP_201_CREATED)
async def add_car(car: Car,
                  db: AsyncSession = Depends(get_db_session)):

    logger.info(f"Adding Car: {str(car)}")
    new_car = await CarService.add_one(db=db, car=car)
    logger.info(f"Successfully added Car: {str(car)}")
    return new_car


# PATCH ----------------
# Update existing car based on id
@router.patch("/{car_id}", response_model=Car, status_code=status.HTTP_200_OK)
async def update_car_by_id(car_id: UUID,
                           update_req: CarUpdateReq,
                           db: AsyncSession = Depends(get_db_session)):

    logger.info(f"Updating Car with id: {car_id} with request: {str(update_req)}")
    patched_car = await CarService.update_one_by_id(db=db, car_id=car_id, update_req=update_req)
    logger.info(f"Successfully Updated")
    return patched_car


# DELETE --------------
# Delete existing car
@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car_by_id(car_id: UUID,
                           db: AsyncSession = Depends(get_db_session)):

    logger.info(f"Deleting Car with id: {car_id}")
    await CarService.delete_one_by_id(db=db, car_id=car_id)
    logger.info(f"Successfully deleted Car with id: {car_id}")
    return None

