# Purpose: HTTP endpoint to create booking intents (hotels)
from fastapi import APIRouter, Query                                                         # API tools
from pydantic import BaseModel                                                               # Response model
from .tools.booking import booking_hotel_intent                                              # Adapter

router = APIRouter(prefix="/api/booking", tags=["booking"])                                  # Router

class BookingIntentOut(BaseModel):
    url: str                                                                                 # URL to open
    source: str                                                                              # 'provider' or 'fallback'

@router.get("/hotel-intent", response_model=BookingIntentOut)
async def hotel_intent(city: str = Query(...), checkin: str = Query(...), nights: int = Query(1)):
    """Return a hotel booking link for the given city and dates."""
    data = await booking_hotel_intent(city, checkin, nights)
    return BookingIntentOut(**data)
