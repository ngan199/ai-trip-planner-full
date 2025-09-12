# Purpose: Verify POIs via Google Maps and filter by rating/open-hours
from typing import List, Dict, Any  # Typing
from ..tools.maps import google_place_search, google_place_detail  # Google adapters
from ..settings import Settings  # Access MIN_RATING threshold


async def verify_pois(poi_names: List[str], city: str) -> List[Dict[str, Any]]:
    """
    For each POI name candidate: search & fetch details, then filter by rating.
    Returns a list of verified POI dicts (name/address/place_id/lat/lng/rating/url/opening_hours?).
    """
    s = Settings()  # Load settings (min rating)
    verified: List[Dict[str, Any]] = []  # Accumulator for valid POIs

    for name in poi_names:  # Iterate each candidate name
        # Search for the place with city context to disambiguate
        results = await google_place_search(f"{name} {city}")
        if not results:  # If nothing found -> skip
            continue

        # Pick top result and fetch details for canonical metadata
        detail = await google_place_detail(results[0]["place_id"])
        if not detail:  # If details failed -> skip
            continue

        # Filter: rating must meet threshold (if a rating exists)
        rating = detail.get("rating")
        if isinstance(rating, (int, float)) and rating < s.min_rating:
            # Below threshold -> skip
            continue

        # Keep verified record
        verified.append(detail)

    # Return verified POIs (can be empty; orchestrator handles fallback)
    return verified
