
# API Deps
from fastapi import FastAPI
from app.api.v1.router import router as v1_router
from app.api.health.health_router import router as health_router
from app.api.metrics.metrics_router import router as metrics_router

# Observability
from app.api.metrics.metrics import track_latency_for_prefixes

# App
app = FastAPI(title="DriveNow", version="1.0.0")
track_latency_for_prefixes(app, prefixes=["/v1"])
app.include_router(v1_router)
app.include_router(health_router)
app.include_router(metrics_router)
