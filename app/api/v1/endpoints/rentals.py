
# Deps
from fastapi import APIRouter, status
router = APIRouter(prefix="/rentals", tags=["rentals"])

# Models
from uuid import UUID
from app.models.validations.items import Rental, RentalUpdateReq
from typing import List

# Functionality
from datetime import datetime
from uuid import uuid4

# TODO: Remove!
test = Rental(id=uuid4(),
                    car_id=uuid4(),
                    customer_name="Alice Johnson",
                    start_date=datetime(2026, 2, 26, 16, 30),
                    end_date=datetime(2026, 2, 28, 10, 0)
                )

# GET ------------------
# Get a rental by id
@router.get("/{rental_id}", response_model=Rental, status_code=status.HTTP_200_OK)
async def get_rental_by_id(rental_id: UUID):

    rental = test
    return rental

@router.get("/", response_model=List[Rental], status_code=status.HTTP_200_OK)
async def get_all_rentals():

    rentals = [test]
    return rentals


# POST ------------------
# Add a rental
@router.post("/", response_model=Rental, status_code=status.HTTP_201_CREATED)
async def add_rental(rental: Rental):

    rental = test
    return rental


# PATCH ----------------
# Update rental based on id
@router.patch("/{rental_id}", response_model=Rental, status_code=status.HTTP_200_OK)
async def update_rental_by_id(rental_id: UUID, rental: RentalUpdateReq):

    rental = test
    return rental


# DELETE --------------
# Delete rental
@router.delete("/{rental_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rental_by_id(rental_id: UUID):
    return None

