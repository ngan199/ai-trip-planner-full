# Purpose: Build a multi-day grounded itinerary with budgeting and notes
from typing import Dict, Any, List  # Typing helpers
from math import ceil  # For bucket sizing

from .agents.planner_llm import llm_poi_candidates  # LLM candidates
from .agents.verifier import verify_pois  # Google Maps verification
from .agents.router import route_day  # Directions estimates
from .agents.budget import estimate_budget  # Budget totals
from .utils.dates import normalize_start_date, expand_dates  # Date utils
from .settings import Settings  # Thresholds and defaults
from .utils.metrics import metrics  # Timing metrics


def _distribute_across_days(
    verified: List[Dict[str, Any]], day_count: int
) -> List[List[Dict[str, Any]]]:
    """
    Evenly distribute verified POIs across days (target ~3 per day).
    Keep order stable (as returned by verifier).
    """
    if not verified:
        return [[] for _ in range(day_count)]
    per_day = max(
        2, min(4, ceil(len(verified) / max(1, day_count)))
    )  # target between 2..4 per day
    buckets: List[List[Dict[str, Any]]] = [[] for _ in range(day_count)]
    day_idx = 0
    for poi in verified:
        buckets[day_idx].append(poi)
        day_idx = (day_idx + 1) % day_count
        # Cap each bucket at per_day items to avoid overloading a day
        if len(buckets[day_idx]) >= per_day:
            day_idx = (day_idx + 1) % day_count
    return buckets


async def build_itinerary(req: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pipeline:
      1) Normalize & expand dates.
      2) LLM candidates (many) -> Verify via Google (filter by rating).
      3) Distribute POIs across days and add routing per day.
      4) Compute budget with real provider or heuristics.
      5) Add notes & uncertainties for explainability.
    """
    s = Settings()  # Load thresholds
    # 1) Normalize and expand dates
    start_iso = normalize_start_date(req.get("start_date"))  # Ensure YYYY-MM-DD
    days = int(req.get("days", 3))  # Duration in days
    dates = expand_dates(start_iso, days)  # ["YYYY-MM-DD", ...]

    city = req.get("city", "Unknown City")  # City for all steps
    currency = req.get("currency", "USD")  # Currency code
    budget_value = float(req.get("budget", 1000))  # User budget (not enforced here)

    # Base itinerary shell
    itinerary: Dict[str, Any] = {
        "trip": {
            "city": city,
            "days": days,
            "currency": currency,
            "budget": budget_value,
        },
        "days": [{"date": d, "items": []} for d in dates],
        "totals": {
            "lodging": 0,
            "food": 0,
            "transport": 0,
            "tickets": 0,
            "misc": 0,
            "currency": currency,
        },
        "notes": [],
        "uncertainties": [],
    }

    # 2) LLM → candidates (untrusted)
    with metrics.timer("llm_candidates"):
        candidates: List[str] = await llm_poi_candidates(req)

    if not candidates:
        # Fallback baseline if LLM is down or empty response
        candidates = [
            "City Museum",
            "Central Park",
            "Old Town",
            "Main Cathedral",
            "Local Market",
        ]

    # Verify via Google Maps (trusted)
    with metrics.timer("verify_pois"):
        verified = await verify_pois(candidates, city)

    if not verified:
        itinerary["notes"].append(
            "Verification returned no POIs; check API keys, quotas, or raise MIN_RATING."
        )
        itinerary["uncertainties"].append("No verified POIs, itinerary is skeletal.")
        # Budget still computed to give user something actionable
        itinerary = await estimate_budget(itinerary, currency=currency)
        return itinerary

    # 3) Distribute across days and route each day
    buckets = _distribute_across_days(verified, days)
    for day_idx, bucket in enumerate(buckets):
        # Convert raw place dicts into DayItems
        items: List[Dict[str, Any]] = []
        for p in bucket:
            items.append(
                {
                    "time": "09:00",  # Simplified fixed slot for demo
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
                    # Optional: add minimal notes (open hours could be appended here if you require)
                }
            )

        # Add transit estimates for that day's sequence
        if items:
            items = await route_day(items)

        itinerary["days"][day_idx]["items"] = items

    # 4) Budget with hotels provider (or heuristic)
    itinerary = await estimate_budget(itinerary, currency=currency)

    # 5) Explainability notes
    itinerary["notes"].append(
        f"POIs verified via Google Maps (min rating {s.min_rating}). Transit estimates are approximate."
    )
    return itinerary
