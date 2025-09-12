# Purpose: Ask the LLM for enough POIs to cover multiple days (3 per day target), then deduplicate
from typing import Dict, Any, List                         # Typing helpers
from ..settings import Settings                            # Settings (provider choices)
from ..llm.provider import LLMRouter                       # Multi-provider router


async def llm_poi_candidates(req: Dict[str, Any]) -> List[str]:
    """
    Request ~3 POIs per day (e.g., days * 3 + buffer).
    Return a clean list of unique names, normalized and deduplicated.
    """
    s = Settings()                                         # Load settings
    router = LLMRouter(s)                                  # Create LLM router

    city = req.get("city", "")
    preferences = [p.lower() for p in (req.get("preferences") or [])]
    days = int(req.get("days", 3))
    budget = float(req.get("budget", 1000))

    # Increase count implicitly by tweaking 'days' in the user payload (provider-agnostic)
    # Alternatively, you could modify the build_poi_prompt to accept a 'count' param.
    want = max(8, days * 3 + 2)                            # Minimum target size with a small buffer
    # Trick: pass a higher 'days' to bias providers that scale with duration (simple, effective)
    data = router.generate_pois(city, preferences, max(days, (want // 3)), budget)  # Sync call

    names: List[str] = []
    seen = set()
    for item in data.get("pois", []):
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        names.append(name)

    return names
