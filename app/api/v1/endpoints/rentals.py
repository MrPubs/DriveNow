
# Routing
from fastapi import APIRouter, status, Depends
router = APIRouter(prefix="/rentals", tags=["Rentals"])

# Functionality
from app.services.rental_service import RentalService

# Models
from uuid import UUID
from app.models.validations.items import Rental, RentalUpdateReq
from app.models.validations.responses import GetAllRentalsResponse

# Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session

# Observability
from ....core.logger import logger

# GET ------------------
# Get a rental by id
@router.get("/{rental_id}", response_model=Rental, status_code=status.HTTP_200_OK)
async def get_rental_by_id(rental_id: UUID,
                           db: AsyncSession = Depends(get_db_session)):

    logger.info(f"Fetching Rental with id: {rental_id}")
    rental = await RentalService.get_one_by_id(db=db, rental_id=rental_id)
    logger.info(f"Found Rental with id: {rental_id}")
    return rental

@router.get("/", response_model=GetAllRentalsResponse, status_code=status.HTTP_200_OK)
async def get_all_rentals(db: AsyncSession = Depends(get_db_session)):

    logger.info(f"Fetching all Rentals")
    rentals = await RentalService.get_all(db=db)
    resp = {"length": len(rentals),
            "rentals": rentals
            }
    logger.info(f"Found {resp['length']}")
    return resp


# POST ------------------
# Add a new rental
@router.post("/", response_model=Rental, status_code=status.HTTP_201_CREATED)
async def start_rental(rental: Rental,
                       db: AsyncSession = Depends(get_db_session)):

    logger.info(f"Adding Rental: {str(rental)}")
    rental = await RentalService.add_one(db=db, rental=rental)
    logger.info(f"Successfully added Rental: {str(rental)}")
    return rental

# DELETE --------------
# Delete rental
@router.delete("/{rental_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rental_by_id(rental_id: UUID,
                              db: AsyncSession = Depends(get_db_session)):

    logger.info(f"Deleting Rental with id: {rental_id}")
    await RentalService.delete_one_by_id(db=db, rental_id=rental_id)
    logger.info(f"Successfully Deleted Rental with id: {rental_id}")
    return None

