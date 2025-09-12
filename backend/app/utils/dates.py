# Purpose: Utilities to handle multi-day date generation and formatting
from datetime import date, timedelta  # For date handling
from dateutil.parser import parse  # For parsing string dates (flexible)


def normalize_start_date(start_date: str | None) -> str:
    """
    Normalize start_date into YYYY-MM-DD.
    If not provided, use today's date as a baseline.
    """
    # Parse provided start_date or fallback to today
    d = parse(start_date).date() if start_date else date.today()
    # Return formatted ISO string for consistency
    return d.isoformat()


def expand_dates(start_date_iso: str, days: int) -> list[str]:
    """
    Given a start date (YYYY-MM-DD) and a number of days, produce a list of ISO dates.
    Example: start=2025-09-11, days=3 -> ["2025-09-11", "2025-09-12", "2025-09-13"]
    """
    # Parse string back to date object
    d0 = parse(start_date_iso).date()
    # Build consecutive dates
    return [(d0 + timedelta(days=i)).isoformat() for i in range(days)]
