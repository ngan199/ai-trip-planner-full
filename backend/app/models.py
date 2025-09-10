# Purpose: Define typed contracts for request/response using Pydantic
from typing import List, Optional, Literal
from pydantic import BaseModel


class Source(BaseModel):
    type: Literal["maps", "rag", "user", "provider"]
    url: Optional[str] = None
    place_id: Optional[str] = None


class Cost(BaseModel):
    amount: float
    currency: str


class Transport(BaseModel):
    mode: Literal["walk", "metro", "bus", "car", "train", "flight"]
    duration_min: int
    distance_km: Optional[float] = None


class POI(BaseModel):
    name: str
    address: Optional[str] = None
    place_id: Optional[str] = None
    rating: Optional[float] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


class DayItem(BaseModel):
    time: str
    poi: POI
    transport: Optional[Transport] = None
    cost: Optional[Cost] = None
    source: Optional[Source] = None
    notes: Optional[str] = None


class DayPlan(BaseModel):
    date: str  # YYYY-MM-DD or D1..
    items: List[DayItem]


class Totals(BaseModel):
    lodging: float = 0
    food: float = 0
    transport: float = 0
    tickets: float = 0
    misc: float = 0
    currency: str = "USD"


class TripInfo(BaseModel):
    city: str
    days: int
    currency: str = "USD"
    budget: float


class Itinerary(BaseModel):
    trip: TripInfo
    days: List[DayPlan]
    totals: Totals
    notes: List[str] = []
    uncertainties: List[str] = []


class PlanRequest(BaseModel):
    city: str
    country: Optional[str] = None
    start_date: Optional[str] = None
    days: int
    budget: float
    preferences: List[str] = []
    travelers: Optional[int] = 1
    currency: str = "USD"
