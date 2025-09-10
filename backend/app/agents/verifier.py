# Purpose: Ensure POIs exist and carry canonical metadata
from typing import List, Dict, Any
from ..tools.maps import google_place_search, google_place_detail


async def verify_pois(poi_names: List[str], city: str) -> List[Dict[str, Any]]:
    verified: List[Dict[str, Any]] = []
    for name in poi_names:
        # Text search best-effort
        results = await google_place_search(f"{name} {city}")
        if results:
            detail = await google_place_detail(results[0]["place_id"])
            if detail:
                verified.append(detail)
    return verified
