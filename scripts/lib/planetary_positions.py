"""
Calculate daily planetary positions for all planets.
"""

import swisseph as swe
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any
from lib.config import PLANETS, SWEPH_FLAGS
from utils.formatters import get_zodiac_sign, format_datetime_iso, format_date_only, round_decimal
from utils.julian_date import datetime_to_julian_day
from lib.moon_phases import get_sun_moon_angle, get_moon_phase_name


def calculate_planet_position(planet_id: int, jd: float) -> Dict[str, Any]:
    """
    Calculate position data for a single planet at a given Julian Day.

    Args:
        planet_id: Swiss Ephemeris planet ID
        jd: Julian Day number

    Returns:
        Dictionary with planet position data
    """
    # Calculate position with speed
    result = swe.calc_ut(jd, planet_id, SWEPH_FLAGS)

    # result[0] contains: [longitude, latitude, distance, speed_lon, speed_lat, speed_dist]
    longitude = result[0][0]
    latitude = result[0][1]
    distance = result[0][2]
    speed = result[0][3]  # Longitudinal speed in degrees/day

    # Get zodiac sign and degree within sign
    sign, degree_in_sign = get_zodiac_sign(longitude)

    # Determine if retrograde (negative longitudinal speed)
    is_retrograde = speed < 0

    return {
        'longitude': round_decimal(longitude),
        'latitude': round_decimal(latitude),
        'distance_au': round_decimal(distance),
        'speed': round_decimal(speed),
        'sign': sign,
        'degree_in_sign': round_decimal(degree_in_sign),
        'retrograde': is_retrograde
    }


def calculate_daily_positions(date: datetime) -> Dict[str, Dict[str, Any]]:
    """
    Calculate positions for all planets at midnight UTC on a given date.

    Args:
        date: Date to calculate positions for (time will be set to midnight UTC)

    Returns:
        Dictionary mapping planet names to their position data
    """
    # Set to midnight UTC
    date_utc = date.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
    jd = datetime_to_julian_day(date_utc)

    positions = {}
    for planet_name, planet_data in PLANETS.items():
        planet_id = planet_data['id']
        positions[planet_name] = calculate_planet_position(planet_id, jd)

    return positions


def generate_month_positions(year: int, month: int) -> Dict[str, Any]:
    """
    Generate daily positions for all planets for a given month.

    Args:
        year: Year (e.g., 2025)
        month: Month (1-12)

    Returns:
        Dictionary with metadata and daily position data
    """
    # Determine number of days in month
    if month == 12:
        next_month = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        next_month = datetime(year, month + 1, 1, tzinfo=timezone.utc)

    first_day = datetime(year, month, 1, tzinfo=timezone.utc)
    days_in_month = (next_month - first_day).days

    # Generate positions for each day
    positions = []
    for day in range(1, days_in_month + 1):
        date = datetime(year, month, day, tzinfo=timezone.utc)
        jd = datetime_to_julian_day(date)
        planet_positions = calculate_daily_positions(date)

        # Calculate moon phase
        sun_moon_angle = get_sun_moon_angle(jd)
        moon_phase = get_moon_phase_name(sun_moon_angle)

        positions.append({
            'date': format_date_only(date),
            'time': '00:00:00Z',
            'julian_day': round_decimal(jd),
            'moon_phase': moon_phase,
            'planets': planet_positions
        })

    # Create output structure with metadata
    month_str = f"{year}-{month:02d}"
    output = {
        'metadata': {
            'month': month_str,
            'generated_at': format_datetime_iso(datetime.now(timezone.utc)),
            'ephemeris_version': f'Swiss Ephemeris {swe.version}',
            'coordinate_system': 'tropical zodiac, geocentric',
            'precision': '6 decimal places (~0.0001 degree)'
        },
        'positions': positions
    }

    return output


def generate_year_positions(year: int, output_dir: str = '../data/daily-positions') -> None:
    """
    Generate daily positions for all 12 months of a year and save to JSON files.

    Args:
        year: Year to generate data for
        output_dir: Directory to save output files (relative to scripts directory)
    """
    import os
    from utils.formatters import save_json

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    for month in range(1, 13):
        print(f"Generating positions for {year}-{month:02d}...")
        data = generate_month_positions(year, month)

        output_file = os.path.join(output_dir, f"{year}-{month:02d}.json")
        save_json(data, output_file)
        print(f"  Saved to {output_file}")

    print(f"\nCompleted generating positions for {year}!")
