# Purpose: Multi-day itinerary grounded by RAG + verified by Maps + budgeted.
from typing import Dict, Any, List
from math import ceil
from sqlalchemy.ext.asyncio import AsyncSession

from .agents.planner_llm import llm_poi_candidates
from .agents.verifier import verify_pois
from .agents.router import route_day
from .agents.budget import estimate_budget
from .utils.dates import normalize_start_date, expand_dates
from .settings import Settings
from .utils.metrics import metrics
from .rag import retrieve_context
from .llm.provider import LLMRouter  # context-enabled router


def _distribute(verified: List[Dict[str, Any]], day_count: int) -> List[List[Dict[str, Any]]]:
    """Evenly distribute verified POIs across days (2..4 per day)."""
    if not verified:
        return [[] for _ in range(day_count)]
    per_day = max(2, min(4, ceil(len(verified) / max(1, day_count))))
    buckets: List[List[Dict[str, Any]]] = [[] for _ in range(day_count)]
    di = 0
    for poi in verified:
        buckets[di].append(poi)
        if len(buckets[di]) >= per_day:
            di = (di + 1) % day_count
    return buckets


async def build_itinerary(
    req: Dict[str, Any],
    session: AsyncSession | None = None,   # kept for future extensions (RAG already uses a session)
    user_email: str | None = None          # not used here; persistence is handled by /api/trips
) -> Dict[str, Any]:
    """Main pipeline used by /api/agent/plan — enriched by RAG and verified via Maps."""
    s = Settings()

    start_iso = normalize_start_date(req.get("start_date"))
    days = int(req.get("days", 3))
    dates = expand_dates(start_iso, days)
    city = req.get("city", "Unknown City")
    currency = req.get("currency", "USD")
    budget_value = float(req.get("budget", 1000))
    prefs = [p.lower() for p in (req.get("preferences") or [])]

    itinerary: Dict[str, Any] = {
        "trip": {"city": city, "days": days, "currency": currency, "budget": budget_value},
        "days": [{"date": d, "items": []} for d in dates],
        "totals": {"lodging": 0, "food": 0, "transport": 0, "tickets": 0, "misc": 0, "currency": currency},
        "notes": [],
        "uncertainties": [],
    }

    # RAG context (local knowledge) to steer LLM
    with metrics.timer("rag_retrieve"):
        ctx = ""
        if session is not None:
            ctx = await retrieve_context(city=city, preferences=prefs, session=session, limit=5)

    # LLM candidates with context
    with metrics.timer("llm_candidates"):
        router = LLMRouter(s)
        data = router.generate_pois(city, prefs, days, budget_value, context=ctx)
        candidates = [str(x.get("name", "")).strip() for x in data.get("pois", []) if isinstance(x, dict)]

    if not candidates:
        candidates = ["City Museum", "Central Park", "Old Town", "Local Market"]

    # Verify via Maps
    with metrics.timer("verify_pois"):
        verified = await verify_pois(candidates, city)

    if not verified:
        itinerary["notes"].append("Verification returned no POIs; check API keys, quotas, or relax MIN_RATING.")
        itinerary["uncertainties"].append("No verified POIs, itinerary is skeletal.")
        itinerary = await estimate_budget(itinerary, currency=currency)
        return itinerary

    # Distribute and route
    buckets = _distribute(verified, days)
    for di, bucket in enumerate(buckets):
        items: List[Dict[str, Any]] = []
        for p in bucket:
            items.append({
                "time": "09:00",
                "poi": {
                    "name": p.get("name"),
                    "address": p.get("address"),
                    "place_id": p.get("place_id"),
                    "rating": p.get("rating"),
                    "lat": p.get("lat"),
                    "lng": p.get("lng"),
                },
                "source": {"type": "maps", "place_id": p.get("place_id"), "url": p.get("url")},
            })
        if items:
            items = await route_day(items)
        itinerary["days"][di]["items"] = items

    # Budget
    itinerary = await estimate_budget(itinerary, currency=currency)
    itinerary["notes"].append(f"POIs verified via Google Maps (min rating {s.min_rating}); RAG context applied.")
    return itinerary
