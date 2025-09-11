# Purpose: Thin adapters over Google APIs to keep business logic clean
import os
from typing import List, Dict, Any, Optional

import httpx

GOOGLE_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")


async def google_place_search(
    query: str,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    radius_m: int = 5000,
) -> List[Dict[str, Any]]:
    if not GOOGLE_KEY:
        # Fail-soft for local dev without key
        return []

    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": query, "key": GOOGLE_KEY}

    if lat is not None and lng is not None:
        params.update({"location": f"{lat},{lng}", "radius": radius_m})

    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        data = r.json().get("results", [])

        return [
            {
                "name": d.get("name"),
                "address": d.get("formatted_address"),
                "place_id": d.get("place_id"),
                "rating": d.get("rating"),
                "lat": d.get("geometry", {}).get("location", {}).get("lat"),
                "lng": d.get("geometry", {}).get("location", {}).get("lng"),
            }
            for d in data
        ]


async def google_place_detail(place_id: str) -> Dict[str, Any]:
    if not GOOGLE_KEY:
        return {}

    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "key": GOOGLE_KEY,
        "fields": "name,geometry,formatted_address,rating,opening_hours,url",
    }

    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        d = r.json().get("result", {})

        return {
            "name": d.get("name"),
            "address": d.get("formatted_address"),
            "place_id": place_id,
            "rating": d.get("rating"),
            "lat": d.get("geometry", {}).get("location", {}).get("lat"),
            "lng": d.get("geometry", {}).get("location", {}).get("lng"),
            "url": d.get("url"),
            "opening_hours": d.get("opening_hours", {}).get("weekday_text"),
        }


async def google_route(
    origin: str, destination: str, mode: str = "transit"
) -> Dict[str, Any]:
    if not GOOGLE_KEY:
        return {"duration_min": 0, "distance_km": 0.0}

    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "mode": mode,
        "key": GOOGLE_KEY,
    }

    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        routes = r.json().get("routes", [])

        if not routes:
            return {"duration_min": 0, "distance_km": 0.0}

        leg = routes[0].get("legs", [{}])[0]

        return {
            "duration_min": int(leg.get("duration", {}).get("value", 0) / 60),
            "distance_km": round(leg.get("distance", {}).get("value", 0) / 1000, 2),
        }
