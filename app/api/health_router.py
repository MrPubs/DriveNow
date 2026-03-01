
# Service
from ..services.HealthService import HealthService

# API Deps
from fastapi import APIRouter, Depends, HTTPException, status
router = APIRouter(prefix="/health", tags=["Health"])

# Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session

from app.core.logger import logger

@router.get("/health/ping")
def ping():
    return{'msg': "pong"}


@router.get("/health/db")
async def health_check(db: AsyncSession = Depends(get_db_session)):

    logger.info("Testing DB for connectivity.")
    resp = await HealthService.db_health(db=db)
    logger.info("Valid DB connection!")
    return resp