
from datetime import datetime

# Session
from sqlalchemy.ext.asyncio import AsyncSession

# Models and Types
from ..models.orm import CarTableSchema, RentalTableSchema

# Query
from sqlalchemy import select, func

# Logging
from ..core.logger import logger

class MetricService:

    @staticmethod
    async def get_active_cars(db: AsyncSession):

        query = select(func.count()).select_from(CarTableSchema)
        total_active_cars = (await db.execute(query)).scalar_one()
        return total_active_cars

    @staticmethod
    async def get_ongoing_rentals(db: AsyncSession):

        now = datetime.utcnow()
        query = select(func.count()).where(
            RentalTableSchema.start_date <= now,
            RentalTableSchema.end_date >= now
        )
        total_ongoing_rentals = (await db.execute(query)).scalar_one()
        return total_ongoing_rentals