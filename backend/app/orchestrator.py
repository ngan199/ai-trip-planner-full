# Purpose: Compose agents into a robust pipeline with LLM planning + verification guardrails
from typing import Dict, Any, List  # Import types for clarity

from .agents.planner_llm import llm_poi_candidates  # NEW: LLM-based candidate generator
from .agents.verifier import verify_pois  # Verify POIs via Google Maps (truth source)
from .agents.router import route_day  # Add transit times between consecutive points
from .agents.budget import estimate_budget  # Provide mock budget totals for UI


async def build_itinerary(req: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build an itinerary using the following steps:
    1) Ask LLM to propose candidate POI names (fast JSON mode).
    2) Verify each candidate via Google Maps (filter out hallucinations).
    3) Assemble Day 1 with first verified POIs, add transit estimates.
    4) Compute mock budget totals.
    5) Return a typed Itinerary JSON (schema enforced by FastAPI response_model).
    """

    # Extract top-level fields (provide defaults for safety)
    city = req.get("city", "Unknown City")  # City used for both LLM and verifier
    days = int(req.get("days", 3))  # Number of days (used for budget calc)
    currency = req.get("currency", "USD")  # Currency code (passed to totals)
    budget_value = float(
        req.get("budget", 1000)
    )  # Total budget (not used in mock calc yet)

    # 1) LLM proposes candidate POIs (UNTRUSTED, best-effort)
    candidates: List[str] = await llm_poi_candidates(
        req
    )  # Returns a list of strings (names only)

    # Safety: fallback if LLM returned nothing usable
    if not candidates:  # If no candidates were produced
        # Provide a minimal safe default set based on generic city landmarks
        candidates = ["City Museum", "Central Park", "Old Town"]  # Basic placeholders

    # 2) Verify candidates against Google Maps (TRUSTED)
    verified = await verify_pois(
        candidates, city
    )  # Returns detailed dicts with place_id/lat/lng/rating/url

    # Safety: if verification found nothing, we still return a valid shape
    if not verified:  # If nothing verified (e.g., quota exhausted)
        itinerary = {  # Build minimal itinerary shape
            "trip": {
                "city": city,
                "days": days,
                "currency": currency,
                "budget": budget_value,
            },  # Trip meta
            "days": [
                {"date": req.get("start_date", "D1"), "items": []}
            ],  # Day list with empty items
            "totals": {
                "lodging": 0,
                "food": 0,
                "transport": 0,
                "tickets": 0,
                "misc": 0,
                "currency": currency,
            },  # Totals
            "notes": [
                "LLM proposed POIs, but verification returned none. Check API keys and quotas."
            ],  # Note
            "uncertainties": [
                "No verified POIs due to verification failure or empty results."
            ],  # Uncertainty
        }
        return itinerary  # Return safe fallback

    # 3) Build Day 1 with first 2–3 verified POIs (keep pipeline simple for Sprint 2)
    day0_items: List[Dict[str, Any]] = []  # Prepare day items list
    for p in verified[:3]:  # Take at most three to keep map readable
        day0_items.append(
            {  # Convert each place into an item
                "time": "09:00",  # Fixed time slot for demo purposes
                "poi": {  # POI details required by schema
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
                },  # Source attribution
            }
        )

    # If we have items, add transit estimates in sequence
    if day0_items:  # Only route if we have at least one item
        day0_items = await route_day(
            day0_items
        )  # Enrich items with transport duration/distance

    # Compose the full itinerary structure
    itinerary = {  # Build response object
        "trip": {
            "city": city,
            "days": days,
            "currency": currency,
            "budget": budget_value,
        },  # Trip block
        "days": [
            {"date": req.get("start_date", "D1"), "items": day0_items}
        ],  # Day list
        "totals": {
            "lodging": 0,
            "food": 0,
            "transport": 0,
            "tickets": 0,
            "misc": 0,
            "currency": currency,
        },  # Placeholder
        "notes": [  # Helpful human-readable notes
            "POIs proposed by LLM; only verified places (Google Maps) are included.",
            "Transit estimates are approximate and for demo purposes.",
        ],
        "uncertainties": [],  # A place to record known caveats
    }

    # 4) Compute mock totals to unblock the UI (sprint 3 will fetch real quotes)
    itinerary = await estimate_budget(
        itinerary, currency=currency
    )  # Replace totals with mock calculation

    # 5) Return final itinerary
    return itinerary  # FastAPI will validate against response_model
