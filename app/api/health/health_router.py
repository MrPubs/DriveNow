
# Service
from app.services.HealthService import HealthService

# API Deps
from fastapi import APIRouter, Depends, HTTPException, status
router = APIRouter(prefix="/health", tags=["Health"])

# Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session

# Observability
from app.core.logger import logger

# Response
from app.models.validations.responses import PingResp, DBHealthCheckResp

@router.get("/ping", response_model=PingResp)
async def ping():

    resp = await HealthService.ping()
    return {"msg": resp}


@router.get("/db", response_model=DBHealthCheckResp)
async def health_check(db: AsyncSession = Depends(get_db_session)):

    logger.info("Testing DB for connectivity.")
    resp = await HealthService.db_health(db=db)
    logger.info("Valid DB connection!")
    return {"msg": resp}
