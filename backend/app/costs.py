# Purpose: Estimate LLM cost per call and track usage (very rough; replace with real provider telemetry later)
from typing import Dict                                                                       # Typing

# Default cost tables (USD per 1K tokens) — adjust as needed
COST_TABLE: Dict[str, Dict[str, float]] = {
    "openai:gpt-4o-mini": {"input": 0.15, "output": 0.6},
    "anthropic:claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
    "gemini:gemini-1.5-flash": {"input": 0.075, "output": 0.30},
}

class CostTracker:
    """In-memory counters for cost; swap with persistent store if needed."""
    def __init__(self) -> None:
        self.total_usd: float = 0.0

    def add(self, provider: str, model: str, prompt_chars: int, output_chars: int) -> float:
        # Approximate tokens as chars/4 (very rough)
        inp_tok = prompt_chars / 4.0
        out_tok = output_chars / 4.0
        key = f"{provider}:{model}"
        table = COST_TABLE.get(key, {"input": 0.1, "output": 0.1})
        usd = (inp_tok / 1000.0) * table["input"] + (out_tok / 1000.0) * table["output"]
        self.total_usd += usd
        return usd

cost_tracker = CostTracker()
