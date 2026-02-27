
# API Deps
from fastapi import FastAPI
from app.api.v1.router import router as v1_router
from app.api.health_router import router as health_router

# App
app = FastAPI(title="DriveNow", version="1.0.0")
app.include_router(health_router)
app.include_router(v1_router)
