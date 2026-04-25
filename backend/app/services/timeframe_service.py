from datetime import date, datetime, timedelta
from typing import Optional


MAX_LOOKBACK_DAYS = 365


def normalize_timeframe(
    start_date_str: Optional[str],
    end_date_str: Optional[str],
) -> tuple[Optional[date], Optional[date], Optional[str]]:
    """
    Returns:
      (start_date, end_date, status)

    status can be:
      - None
      - "invalid_date_format"
      - "invalid_range"
      - "clamped_to_today"
      - "clamped_to_365_days"
    """

    if not start_date_str and not end_date_str:
        return None, None, None

    if not start_date_str or not end_date_str:
        return None, None, "invalid_range"

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        return None, None, "invalid_date_format"

    today = date.today()
    earliest_allowed = today - timedelta(days=MAX_LOOKBACK_DAYS)

    status = None

    if end_date > today:
        end_date = today
        status = "clamped_to_today"

    if start_date > end_date:
        return None, None, "invalid_range"

    # If the whole requested period is older than our supported range,
    # analyze the most recent supported 365-day window instead.
    if end_date < earliest_allowed:
        return earliest_allowed, today, "clamped_to_365_days"

    # If only the start date is too old, clamp it but keep the user's end date.
    if start_date < earliest_allowed:
        start_date = earliest_allowed
        status = "clamped_to_365_days"

    return start_date, end_date, status


def calculate_days_for_range(start_date: date, end_date: date) -> int:
    delta_days = (end_date - start_date).days
    return max(delta_days, 1)