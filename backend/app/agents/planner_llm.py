# Purpose: Call LLMRouter to get POI candidates, then return a simple name list for verification
from typing import Dict, Any, List                          # Import typing helpers
from ..settings import Settings                             # Import Settings to construct router
from ..llm.provider import LLMRouter                        # Import our multi-provider router


async def llm_poi_candidates(req: Dict[str, Any]) -> List[str]:
    """
    Use LLM to propose candidate POI names (category is optional for Sprint 2).
    We DO NOT trust LLM blindly: output is strictly a candidate list for the Verifier.
    """
    s = Settings()                                          # Load settings (keys, model names, provider order)
    router = LLMRouter(s)                                   # Construct the LLM router with configured providers

    # Extract inputs from request with sane defaults
    city = req.get("city", "")                              # City name from request
    preferences = [p.lower() for p in (req.get("preferences") or [])]  # Normalize preferences to lowercase
    days = int(req.get("days", 3))                          # Fallback to 3 if missing
    budget = float(req.get("budget", 1000))                 # Fallback to 1000 if missing

    # Call the router (sync call inside async function is acceptable for our small workload)
    data = router.generate_pois(city, preferences, days, budget)  # Returns dict like {"pois":[{"name":...}]}

    # Collect names, avoid duplicates, trim whitespace
    names: List[str] = []                                   # Initialize result list
    seen = set()                                            # Track lowercase names to deduplicate
    for item in data.get("pois", []):                       # Iterate proposed POIs
        if not isinstance(item, dict):                      # Skip invalid shapes
            continue                                        # Continue if not a dict
        name = str(item.get("name", "")).strip()            # Extract and trim the name
        if not name:                                        # Skip empty names
            continue                                        # Continue if empty
        key = name.lower()                                  # Dedup key
        if key in seen:                                     # Skip duplicates
            continue                                        # Continue if seen
        seen.add(key)                                       # Record name in 'seen'
        names.append(name)                                  # Append clean name
    return names                                            # Return candidate list for verification
