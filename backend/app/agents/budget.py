# Purpose: Compute realistic totals using provider-agnostic hotel quotes + per-day heuristics
from typing import Dict, Any                               # Typing
from ..tools.hotels import hotel_budget                    # Hotel adapter (provider/fallback)
from ..settings import Settings                            # Defaults for daily costs
from ..utils.metrics import metrics                        # Metrics timer


async def estimate_budget(itinerary: Dict[str, Any], currency: str = "USD") -> Dict[str, Any]:
    """
    Compute totals:
      - lodging: provider-quoted (or heuristic) nightly * nights
      - food/transport/tickets/misc: per-day heuristics
    Also attach an 'explain' section with sources and assumptions.
    """
    s = Settings()                                         # Load settings
    trip = itinerary["trip"]                                # Trip block (city, days, budget, currency)
    city = trip["city"]
    days = int(trip["days"])
    nights = max(1, days - 1)                               # Nights = days - 1 (min 1 for short trips)
    rooms = 1                                               # Assume 1 room (can parameterize later)

    # Hotels quote (async provider call) protected by timer
    with metrics.timer("budget_hotels"):
        hotel = await hotel_budget(city, itinerary["days"][0]["date"], nights, rooms)

    # Heuristic daily costs
    food = round(s.default_food_per_day * days, 2)
    transport = round(s.default_transport_per_day * days, 2)
    tickets = round(s.default_tickets_per_day * days, 2)
    misc = round(s.default_misc_per_day * days, 2)

    # Totals
    lodging = float(hotel["total"])
    totals = {
        "lodging": lodging,
        "food": food,
        "transport": transport,
        "tickets": tickets,
        "misc": misc,
        "currency": currency,
    }
    itinerary["totals"] = totals

    # Explainability: why these numbers exist
    explain = {
        "lodging": {
            "source": hotel["source"],               # 'provider' or 'heuristic'
            "nightly": hotel["nightly"],
            "nights": hotel["nights"],
            "rooms": hotel["rooms"],
            "currency": hotel["currency"],
        },
        "daily_costs": {
            "food_per_day": s.default_food_per_day,
            "transport_per_day": s.default_transport_per_day,
            "tickets_per_day": s.default_tickets_per_day,
            "misc_per_day": s.default_misc_per_day,
            "currency": currency,
        }
    }
    # Attach to notes as a compact human-readable message
    itinerary.setdefault("notes", []).append(
        f"Budget sources — lodging:{hotel['source']}, nightly≈{hotel['nightly']} {hotel['currency']}; "
        f"daily heuristics in {currency}: food {s.default_food_per_day}, transport {s.default_transport_per_day}, "
        f"tickets {s.default_tickets_per_day}, misc {s.default_misc_per_day}."
    )
    # Also mount a machine-friendly explain block (optional)
    itinerary["budget_explain"] = explain

    return itinerary
