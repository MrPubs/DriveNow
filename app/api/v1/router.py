
# deps
from fastapi import APIRouter

# endpoints
from .endpoints.cars import router as cars_router
from .endpoints.rentals import router as rentals_router

# setup
router = APIRouter(prefix="/v1")
router.include_router(cars_router)
router.include_router(rentals_router)
