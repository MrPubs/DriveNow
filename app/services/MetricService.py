
# Functionality
from datetime import datetime

# Session
from sqlalchemy.ext.asyncio import AsyncSession

# Models and Types
from ..models.orm import CarTableSchema, RentalTableSchema
from typing import Tuple

# Query
from sqlalchemy import select, func

# Observability
from prometheus_client import REGISTRY
from ..core.logger import logger

class MetricService:

    @staticmethod
    async def get_active_cars(db: AsyncSession) -> int:

        query = select(func.count()).select_from(CarTableSchema)
        total_active_cars = (await db.execute(query)).scalar_one()
        return total_active_cars

    @staticmethod
    async def get_ongoing_rentals(db: AsyncSession) -> int:

        now = datetime.utcnow()
        query = select(func.count()).where(
            RentalTableSchema.start_date <= now,
            RentalTableSchema.end_date >= now
        )
        total_ongoing_rentals = (await db.execute(query)).scalar_one()
        return total_ongoing_rentals

    @staticmethod
    async def get_average_response_time() -> Tuple[float, int]:
        """
        Returns the average API request latency in ms
        from the Prometheus histogram `api_request_latency_ms`.
        """

        # # global Prometheus registry
        count = REGISTRY.get_sample_value("api_request_latency_ms_count") or 0
        total = REGISTRY.get_sample_value("api_request_latency_ms_sum") or 0

        # avoid division by zero
        avg = round((total / count if count > 0 else 0.0),2)
        return avg, int(total)
