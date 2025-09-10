# Purpose: Add transit estimates between consecutive items
from typing import Dict, Any, List

from ..tools.maps import google_route


async def route_day(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not items:
        return items

    new_items: List[Dict[str, Any]] = []

    for idx, it in enumerate(items):
        if idx == 0:
            new_items.append(it)
            continue

        prev = items[idx - 1]
        origin = f"{prev['poi']['lat']},{prev['poi']['lng']}"
        dest = f"{it['poi']['lat']},{it['poi']['lng']}"

        route = await google_route(origin, dest, mode="transit")

        it["transport"] = {
            "mode": "transit",
            **route,
        }
        new_items.append(it)

    return new_items
