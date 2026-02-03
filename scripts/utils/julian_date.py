"""
Julian date conversion utilities.
"""

from datetime import datetime, timezone
import swisseph as swe


def datetime_to_julian_day(dt: datetime) -> float:
    """
    Convert a datetime object to Julian Day number.

    Args:
        dt: datetime object (should be in UTC)

    Returns:
        Julian Day number as float
    """
    # Ensure datetime is in UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    year = dt.year
    month = dt.month
    day = dt.day
    hour = dt.hour + dt.minute / 60.0 + dt.second / 3600.0

    # Use Swiss Ephemeris function for accurate conversion
    jd = swe.julday(year, month, day, hour, swe.GREG_CAL)
    return jd


def julian_day_to_datetime(jd: float) -> datetime:
    """
    Convert Julian Day number to datetime object (UTC).

    Args:
        jd: Julian Day number as float

    Returns:
        datetime object in UTC
    """
    # Use Swiss Ephemeris function for accurate conversion
    year, month, day, hour = swe.revjul(jd, swe.GREG_CAL)

    # Convert hour to hours, minutes, seconds
    hours = int(hour)
    minutes = int((hour - hours) * 60)
    seconds = int(((hour - hours) * 60 - minutes) * 60)

    return datetime(year, month, day, hours, minutes, seconds, tzinfo=timezone.utc)


def date_range(start_date: datetime, end_date: datetime, step_days: int = 1):
    """
    Generate a range of dates from start_date to end_date.

    Args:
        start_date: Starting datetime
        end_date: Ending datetime
        step_days: Number of days to step (default 1)

    Yields:
        datetime objects in the range
    """
    from datetime import timedelta

    current = start_date
    while current <= end_date:
        yield current
        current += timedelta(days=step_days)
