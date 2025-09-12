# Purpose: Request/response timing + simple rate limit
from starlette.middleware.base import BaseHTTPMiddleware                              # Base middleware
from starlette.requests import Request                                                # Request type
from starlette.responses import Response                                              # Response type
import time                                                                           # Timing
from .utils.metrics import metrics                                                    # Metrics store

class TimingMiddleware(BaseHTTPMiddleware):
    """Measure per-request latency and increment counters."""
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        try:
            response: Response = await call_next(request)
            return response
        finally:
            dt = time.perf_counter() - start
            path = request.url.path
            metrics.timings[path] = metrics.timings.get(path, 0.0) + dt
            metrics.inc(f"hits:{path}")

# (Optional) Very basic global rate-limit can be added here if needed.
