# Purpose: Compose agents into a single pipeline invoked by the endpoint
from typing import Dict, Any, List

from .agents.planner import plan_skeleton
from .agents.verifier import verify_pois
from .agents.router import route_day
from .agents.budget import estimate_budget


async def build_itinerary(req: Dict[str, Any]) -> Dict[str, Any]:
    # 1) Skeleton
    it = await plan_skeleton(req)

    # 2) Seed POIs derived from preferences (LLM comes later)
    seed: List[str] = []
    prefs = [p.lower() for p in (req.get("preferences") or [])]
    if "food" in prefs:
        seed += ["Local Market", "Famous Ramen", "Street Food"]
    if "culture" in prefs:
        seed += ["Old Town", "Traditional Museum", "Shrine"]
    if not seed:
        seed = ["Central Park", "City Museum", "Main Cathedral"]

    verified = await verify_pois(seed, req["city"])  # place_id, lat/lng, rating

    # 3) Put first 2-3 POIs in Day 1 and route them
    day0_items: List[Dict[str, Any]] = []
    for p in verified[:3]:
        day0_items.append(
            {
                "time": "09:00",
                "poi": {
                    "name": p.get("name"),
                    "address": p.get("address"),
                    "place_id": p.get("place_id"),
                    "rating": p.get("rating"),
                    "lat": p.get("lat"),
                    "lng": p.get("lng"),
                },
                "source": {
                    "type": "maps",
                    "place_id": p.get("place_id"),
                    "url": p.get("url"),
                },
            }
        )

    if day0_items:
        it["days"][0]["items"] = await route_day(day0_items)

    # 4) Budget
    it = await estimate_budget(it, currency=req.get("currency", "USD"))

    # 5) Notes / guardrails summary
    it.setdefault("notes", []).append(
        "POIs verified via Google Maps; budget is mocked for Sprint 1."
    )
    return it
