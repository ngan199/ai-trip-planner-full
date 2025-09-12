# Purpose: Expose in-memory metrics and LLM cost
from fastapi import APIRouter                                                     # Router
from .utils.metrics import metrics                                                # Timings/counters
from .costs import cost_tracker                                                   # LLM cost

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("")
async def metrics_json():
    """Return JSON metrics for quick inspection."""
    return {
        "timings_total_seconds": metrics.timings,
        "counters": metrics.counts,
        "llm_total_cost_usd": round(cost_tracker.total_usd, 4),
    }
