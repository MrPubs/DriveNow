
# Response
from fastapi import HTTPException, status

# Session
from sqlalchemy.ext.asyncio import AsyncSession

# Query
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# Logging
from ..core.logger import logger

class HealthService:

    @staticmethod
    async def ping():
        return{'msg': "pong"}

    @staticmethod
    async def db_health(db: AsyncSession):
        try:
            await db.execute(text("SELECT 1"))
            return {"status": "healthy"}
        except SQLAlchemyError:
            logger.error("DB cannot be reached!")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database unavailable"
            )