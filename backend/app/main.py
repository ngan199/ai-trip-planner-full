# Purpose: App entrypoint and HTTP routes
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .models import PlanRequest, Itinerary
from .orchestrator import build_itinerary

app = FastAPI(title="Travel Planner AI Backend")

# Dev-friendly CORS; restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "status": "ok",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health():
    return {"ok": True}


@app.post("/api/agent/plan", response_model=Itinerary)
async def plan_trip(req: PlanRequest):
    itinerary = await build_itinerary(req.dict())
    return itinerary
