# Purpose: Minimal metrics helpers (timing + simple counters) to aid observability
import time  # Time measurements
from contextlib import contextmanager  # Context manager helper
from typing import Dict  # Typing hints


class Metrics:
    """
    Very lightweight metrics store (in-memory).
    In production, replace with Prometheus/OpenTelemetry exporters.
    """

    def __init__(self) -> None:
        # Store cumulative durations per label
        self.timings: Dict[str, float] = {}
        # Store occurrence counters
        self.counts: Dict[str, int] = {}

    @contextmanager
    def timer(self, label: str):
        # Record start time
        t0 = time.perf_counter()
        try:
            yield
        finally:
            # Accumulate elapsed time to label
            dt = time.perf_counter() - t0
            self.timings[label] = self.timings.get(label, 0.0) + dt

    def inc(self, label: str, delta: int = 1):
        # Increment counter by delta
        self.counts[label] = self.counts.get(label, 0) + delta


# Global singleton (simple for this project)
metrics = Metrics()
