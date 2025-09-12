# Purpose: App entrypoint, CORS, routes, middleware, and startup
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models import PlanRequest, Itinerary                                  # Pydantic schemas
from .orchestrator import build_itinerary                                   # Main pipeline
from .auth import router as auth_router                                     # Auth routes
from .rag import router as rag_router                                       # RAG routes
from .booking import router as booking_router                               # Booking routes
from .trips import router as trips_router                                   # Trip routes
from .metrics_api import router as metrics_router                           # Metrics
from .middleware import TimingMiddleware                                    # Timing middleware
from .startup import on_startup                                             # Startup tasks
from .database import get_session                                           # Session dep (for type hints)

app = FastAPI(title="Travel Planner AI Backend — Sprint 4")

# Dev-friendly CORS (restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # TODO: restrict to FE origin in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Timing middleware for monitoring
app.add_middleware(TimingMiddleware)

@app.on_event("startup")
async def _startup():
    await on_startup()

@app.get("/")
async def root():
    return {"status": "ok", "docs": "/docs", "health": "/health"}

@app.get("/health")
async def health():
    return {"ok": True}

@app.post("/api/agent/plan", response_model=Itinerary)
async def plan_trip(req: PlanRequest):
    # Note: we keep anonymous allowed; FE can pass auth header to /api/trips to save result
    itinerary = await build_itinerary(req.dict())
    return itinerary

# Mount feature routers
app.include_router(auth_router)
app.include_router(rag_router)
app.include_router(booking_router)
app.include_router(trips_router)
app.include_router(metrics_router)
