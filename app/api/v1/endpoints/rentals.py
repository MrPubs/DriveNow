
# Deps
from fastapi import APIRouter, status, Depends

from app.services.rental_service import RentalService

router = APIRouter(prefix="/rentals", tags=["Rentals"])

# Models
from uuid import UUID
from app.models.validations.items import Rental, RentalUpdateReq
from app.models.validations.responses import GetAllRentalsResponse

# Functionality
from datetime import datetime
from uuid import uuid4

# Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session

# GET ------------------
# Get a rental by id
@router.get("/{rental_id}", response_model=Rental, status_code=status.HTTP_200_OK)
async def get_rental_by_id(rental_id: UUID,
                           db: AsyncSession = Depends(get_db_session)):

    rental = await RentalService.get_one_by_id(db=db, rental_id=rental_id)
    return rental

@router.get("/", response_model=GetAllRentalsResponse, status_code=status.HTTP_200_OK)
async def get_all_rentals(db: AsyncSession = Depends(get_db_session)):

    rentals = await RentalService.get_all(db=db)
    return {"length": len(rentals),
            "rentals": rentals
            }


# POST ------------------
# Add a new rental
@router.post("/", response_model=Rental, status_code=status.HTTP_201_CREATED)
async def start_rental(rental: Rental,
                       db: AsyncSession = Depends(get_db_session)):

    rental = await RentalService.add_one(db=db, rental=rental)
    return rental

# DELETE --------------
# Delete rental
@router.delete("/{rental_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rental_by_id(rental_id: UUID,
                              db: AsyncSession = Depends(get_db_session)):

    await RentalService.delete_one_by_id(db=db, rental_id=rental_id)
    return None

