# Purpose: Provide a simple mocked budget to unblock UI
from typing import Dict, Any


async def estimate_budget(
    itinerary: Dict[str, Any], currency: str = "USD"
) -> Dict[str, Any]:
    days = itinerary["trip"]["days"]

    totals = {
        "lodging": 80 * days,
        "food": 35 * days,
        "transport": 20 * days,
        "tickets": 25 * days,
        "misc": 15 * days,
        "currency": currency,
    }

    itinerary["totals"] = totals

    return itinerary
