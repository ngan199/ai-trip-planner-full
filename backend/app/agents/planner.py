# Purpose: Build an empty skeleton for the itinerary; LLM comes in Sprint 2
from typing import Dict, Any


async def plan_skeleton(req: Dict[str, Any]) -> Dict[str, Any]:
    days = []
    for i in range(req["days"]):
        # For simplicity use Dx when start_date is not provided
        days.append(
            {
                "date": req.get("start_date", f"D{i + 1}"),
                "items": [],
            }
        )

    return {
        "trip": {
            "city": req["city"],
            "days": req["days"],
            "currency": req.get("currency", "USD"),
            "budget": req["budget"],
        },
        "days": days,
        "totals": {
            "lodging": 0,
            "food": 0,
            "transport": 0,
            "tickets": 0,
            "misc": 0,
            "currency": req.get("currency", "USD"),
        },
        "notes": [],
        "uncertainties": [],
    }
