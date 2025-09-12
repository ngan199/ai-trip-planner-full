# Purpose: Save/load user's itineraries
from fastapi import APIRouter, Depends, HTTPException, Header                                        # API tools
from sqlalchemy.ext.asyncio import AsyncSession                                                     # Session
from sqlalchemy import select, insert                                                               # Query
from pydantic import BaseModel                                                                      # Schemas
from typing import List                                                                             # Typing
from .database import get_session                                                                   # DB dep
from .models_db import User, Trip                                                                   # ORM
from .auth import get_current_user                                                                  # Optional user

router = APIRouter(prefix="/api/trips", tags=["trips"])

class TripIn(BaseModel):
    title: str                                                                                      # Friendly name
    itinerary: dict                                                                                 # Itinerary JSON

class TripOut(BaseModel):
    id: int
    title: str
    itinerary: dict

@router.post("", response_model=TripOut)
async def save_trip(body: TripIn, authorization: str | None = Header(default=None), session: AsyncSession = Depends(get_session)):
    """Persist an itinerary for the authenticated user."""
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:]
    user = await get_current_user(session=session, token=token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    q = insert(Trip).values(user_id=user.id, title=body.title, itinerary=body.itinerary).returning(Trip.id)
    res = await session.execute(q)
    trip_id = res.scalar_one()
    await session.commit()
    return TripOut(id=trip_id, title=body.title, itinerary=body.itinerary)

@router.get("", response_model=List[TripOut])
async def list_trips(authorization: str | None = Header(default=None), session: AsyncSession = Depends(get_session)):
    """List user's trips."""
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:]
    user = await get_current_user(session=session, token=token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    rows = (await session.execute(select(Trip).where(Trip.user_id == user.id))).scalars().all()
    return [TripOut(id=t.id, title=t.title, itinerary=t.itinerary) for t in rows]
