
# Routing
from fastapi import APIRouter, Depends
router = APIRouter(prefix="/metrics", tags=["Metrics"])

# Service
from ..services.MetricService import MetricService

# Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session

# Logging
from ..core.logger import logger

@router.get("/activecars")
async def get_active_cars(db: AsyncSession = Depends(get_db_session)):
    """
    Define active cars as cars in the fleet
    """

    logger.info("Getting active Cars count")
    active_cars_count = await MetricService.get_active_cars(db=db)
    logger.info(f"Successfully got car count: {active_cars_count}")

    resp = {"active_cars": active_cars_count}
    return resp

@router.get("/ongoingrentals")
async def get_ongoing_rentals(db: AsyncSession = Depends(get_db_session)):
    """
    Define ongoing rentals as rentals that have start_date <= now <= end_date
    """

    logger.info("Getting ongoing rentals count")
    ongoing_rentals_count = await MetricService.get_ongoing_rentals(db=db)
    logger.info(f"Successfully ongoing rentals count: {ongoing_rentals_count}")

    resp = {"ongoing_rentals": ongoing_rentals_count}
    return resp