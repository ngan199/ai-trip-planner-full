# Purpose: Booking intent generator; use typed Settings (no dict())
from typing import Dict, Any
import httpx
from app.settings import Settings
from app.utils.cache import cache
from app.utils.metrics import metrics

def _fallback_hotel_link(city: str, checkin: str, nights: int) -> str:
    return f"https://www.google.com/maps/search/hotels+in+{city.replace(' ', '+')}?checkin={checkin}&nights={nights}"

async def booking_hotel_intent(city: str, checkin: str, nights: int) -> Dict[str, Any]:
    s = Settings()
    key = f"booking:{city}:{checkin}:{nights}"
    cached = cache.get(key)
    if cached:
        return cached

    if s.hotel_api_key and s.hotel_api_endpoint:
        headers = {"X-Api-Key": s.hotel_api_key}
        params = {"city": city, "checkin": checkin, "nights": nights}
        with metrics.timer("booking_http"):
            async with httpx.AsyncClient(timeout=20) as client:
                r = await client.get(s.hotel_api_endpoint, headers=headers, params=params)
                r.raise_for_status()
                data = r.json()
        url = data.get("deeplink") or data.get("url")
        if url:
            result = {"url": url, "source": "provider"}
            cache.set(key, result)
            return result

    url = _fallback_hotel_link(city, checkin, nights)
    result = {"url": url, "source": "fallback"}
    cache.set(key, result)
    return result
