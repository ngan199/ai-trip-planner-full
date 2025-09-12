# Purpose: Provider-agnostic hotel pricing adapter with graceful fallback
# - If HOTEL_API_* settings are provided: call external API to fetch nightly price.
# - Else: fallback heuristics based on city buckets.
# Note: Replace with a real provider (e.g., RapidAPI Skyscanner/Hotels) when credentials are available.

from typing import Optional, Dict, Any  # Typing helpers
import httpx  # HTTP client
from ..settings import Settings  # Settings to read provider keys
from ..utils.cache import cache  # Simple TTL cache
from ..utils.metrics import metrics  # Metrics for timing


async def _provider_price_nightly(
    city: str, start_date: str, nights: int, rooms: int = 1
) -> Optional[float]:
    """
    Call external hotel provider to estimate nightly price for the given city/dates.
    Return price per night (float) or None if not available.
    """
    s = Settings()  # Load settings (keys and endpoint)
    if not (s.hotel_api_key and s.hotel_api_host and s.hotel_api_endpoint):
        # Provider not configured -> no direct price available
        return None

    # Cache key to avoid repeated calls
    key = f"hotel:{city}:{start_date}:{nights}:{rooms}"
    cached = cache.get(key)
    if cached is not None:
        return cached

    headers = {
        "X-RapidAPI-Key": s.hotel_api_key,  # Example: RapidAPI key header
        "X-RapidAPI-Host": s.hotel_api_host,  # Example: API host
    }
    # Below payload/params depend on the chosen provider; adapt accordingly.
    params = {
        "city": city,  # City name or ID
        "checkin": start_date,  # Check-in date (YYYY-MM-DD)
        "nights": str(nights),  # Number of nights
        "rooms": str(rooms),  # Room count
        "adults": "2",  # Assumption: 2 adults per room
        "currency": "USD",  # Normalize currency for budgeting
    }

    # Make the HTTP call protected by a timer for metrics
    with metrics.timer("hotels_http"):
        async with httpx.AsyncClient(timeout=20) as client:
            # NOTE: s.hotel_api_endpoint should be a fully-qualified URL
            r = await client.get(s.hotel_api_endpoint, headers=headers, params=params)
            r.raise_for_status()
            data = r.json()

    # The parsing below is pseudo; adapt to actual API response fields.
    # We try to extract a sensible nightly price (e.g., median of top results).
    nightly = None
    results = data.get("results") or data.get("hotels") or []
    prices = []
    for h in results:
        p = h.get("price") or h.get("rate") or h.get("nightly_price")
        if isinstance(p, (int, float)):
            prices.append(float(p))
    if prices:
        # Use median-ish approach: sort and pick middle
        prices.sort()
        nightly = prices[len(prices) // 2]

    # Save to cache for subsequent calls
    if nightly is not None:
        cache.set(key, nightly, ttl=900)

    return nightly


def _heuristic_price_nightly(city: str) -> float:
    """
    Fallback heuristic if provider is not configured or returns no data.
    Buckets are intentionally coarse but plausible.
    """
    c = city.lower()
    # Rough buckets based on global affordability (example values)
    if any(k in c for k in ["tokyo", "london", "new york", "paris", "zurich"]):
        return 140.0
    if any(k in c for k in ["bangkok", "hanoi", "ho chi minh", "delhi", "manila"]):
        return 55.0
    if any(k in c for k in ["barcelona", "berlin", "lisbon", "madrid", "prague"]):
        return 95.0
    # Default global average
    return 85.0


async def hotel_budget(
    city: str, start_date: str, nights: int, rooms: int = 1
) -> Dict[str, Any]:
    """
    Return a hotel budget breakdown:
    { "nightly": float, "nights": int, "rooms": int, "total": float, "currency": "USD", "source": "provider|heuristic" }
    """
    # First try provider price
    nightly = await _provider_price_nightly(city, start_date, nights, rooms)
    if nightly is not None:
        total = nightly * nights * rooms
        return {
            "nightly": round(nightly, 2),
            "nights": nights,
            "rooms": rooms,
            "total": round(total, 2),
            "currency": "USD",
            "source": "provider",
        }

    # Fallback to heuristic price
    nightly = _heuristic_price_nightly(city)
    total = nightly * nights * rooms
    return {
        "nightly": round(nightly, 2),
        "nights": nights,
        "rooms": rooms,
        "total": round(total, 2),
        "currency": "USD",
        "source": "heuristic",
    }
