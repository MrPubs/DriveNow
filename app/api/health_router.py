
# API Deps
from fastapi import APIRouter, Depends, HTTPException, status
router = APIRouter(prefix="/health", tags=["Health"])

# Session
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db_session


@router.get("/health/ping")
def ping():
    return{'msg': "pong"}


@router.get("/health/db")
async def health_check(db: AsyncSession = Depends(get_db_session)):

    # Check health
    try:
        result = await db.execute(text("SELECT 1")) # TODO: Consider making this a service if health expands
        row = result.scalar()

        if row != 1:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database health check returned unexpected result"
            )

        return {"status": "healthy"}

    except HTTPException:
        raise

    except OperationalError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection error: {str(e)}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Unexpected error during DB health check: {str(e)}"
        )