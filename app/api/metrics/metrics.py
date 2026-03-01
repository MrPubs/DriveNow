
# API
from fastapi import Request
import time

# Types
from typing import List

# Observability
from prometheus_client import Histogram

# Define a histogram for API request latency
REQUEST_LATENCY = Histogram(
    "api_request_latency_ms",
    "API request latency in ms"
)


def track_latency_for_prefixes(app, prefixes: List[str]):

    @app.middleware("http")
    async def track_latency(request: Request, call_next):
        if any(request.url.path.startswith(p) for p in prefixes):
            start = time.time()
            response = await call_next(request)
            duration = round((time.time() - start) * 1000, 2)
            REQUEST_LATENCY.observe(duration)
            return response
        else:
            return await call_next(request)