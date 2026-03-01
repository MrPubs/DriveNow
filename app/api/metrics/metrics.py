
# API
from fastapi import Request
from time import perf_counter

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

        # get request path
        route = request.scope.get("route")
        route_path = getattr(route, "path", request.url.path)

        # verify its a tracked path
        if any(route_path.startswith(p) for p in prefixes):
            start = perf_counter()
            response = await call_next(request)
            duration = (perf_counter() - start) * 1000
            REQUEST_LATENCY.observe(duration)
            return response
        else:
            return await call_next(request)