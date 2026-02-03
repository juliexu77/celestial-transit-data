"""
Calculate planetary ingresses (sign changes).
"""

import swisseph as swe
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any
from lib.config import PLANETS, SWEPH_FLAGS, ZODIAC_SIGNS
from utils.formatters import get_zodiac_sign, format_datetime_iso, round_decimal
from utils.julian_date import datetime_to_julian_day, julian_day_to_datetime


def get_planet_position(jd: float, planet_name: str) -> tuple[float, float]:
    """
    Get planet longitude and speed at given Julian Day.

    Args:
        jd: Julian Day number
        planet_name: Name of planet

    Returns:
        Tuple of (longitude, speed)
    """
    planet_id = PLANETS[planet_name]['id']
    result = swe.calc_ut(jd, planet_id, SWEPH_FLAGS)
    longitude = result[0][0]
    speed = result[0][3]  # Longitudinal speed
    return longitude, speed


def find_exact_ingress_time(start_jd: float, end_jd: float, planet_name: str,
                            sign_boundary: float, tolerance: float = 0.001) -> float:
    """
    Find exact time when planet crosses a sign boundary.

    Args:
        start_jd: Starting Julian Day
        end_jd: Ending Julian Day
        planet_name: Name of planet
        sign_boundary: Target longitude (0, 30, 60, ..., 330)
        tolerance: Acceptable error in degrees

    Returns:
        Julian Day of exact ingress
    """
    max_iterations = 50
    iteration = 0

    while iteration < max_iterations:
        mid_jd = (start_jd + end_jd) / 2
        lon, speed = get_planet_position(mid_jd, planet_name)

        # Normalize longitude to match sign boundary
        if sign_boundary == 0:
            # Handle Pisces -> Aries crossing (330-360 -> 0-30)
            if lon > 300:
                lon = lon - 360

        error = lon - sign_boundary

        if abs(error) < tolerance:
            return mid_jd

        if error > 0:
            end_jd = mid_jd
        else:
            start_jd = mid_jd

        iteration += 1

    return (start_jd + end_jd) / 2


def detect_sign_crossing(prev_lon: float, curr_lon: float) -> int | None:
    """
    Detect if a sign boundary was crossed.

    Args:
        prev_lon: Previous longitude
        curr_lon: Current longitude

    Returns:
        Sign boundary crossed (0, 30, 60, etc.) or None
    """
    prev_sign_index = int(prev_lon / 30)
    curr_sign_index = int(curr_lon / 30)

    # Handle retrograde motion (backwards)
    if prev_sign_index != curr_sign_index:
        # Check for forward motion
        if curr_sign_index == (prev_sign_index + 1) % 12:
            return curr_sign_index * 30
        # Check for retrograde motion (backward)
        elif prev_sign_index == (curr_sign_index + 1) % 12:
            return prev_sign_index * 30

    return None


def find_ingresses(year: int, planet_names: List[str] = None) -> List[Dict[str, Any]]:
    """
    Find all sign ingresses for specified planets in a given year.

    Args:
        year: Year to find ingresses for
        planet_names: List of planet names (default: all planets)

    Returns:
        List of ingress events
    """
    if planet_names is None:
        planet_names = list(PLANETS.keys())

    ingresses = []

    # Scan through year at daily intervals
    start_date = datetime(year, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)

    for planet_name in planet_names:
        current_date = start_date
        prev_lon, _ = get_planet_position(datetime_to_julian_day(current_date), planet_name)

        while current_date < end_date:
            current_date += timedelta(days=1)
            current_jd = datetime_to_julian_day(current_date)
            curr_lon, _ = get_planet_position(current_jd, planet_name)

            # Check for sign crossing
            boundary = detect_sign_crossing(prev_lon, curr_lon)

            if boundary is not None:
                # Found an ingress, find exact time
                prev_jd = current_jd - 1.0
                exact_jd = find_exact_ingress_time(prev_jd, current_jd, planet_name, boundary)

                # Get exact longitude at ingress
                exact_lon, _ = get_planet_position(exact_jd, planet_name)

                # Determine from and to signs
                from_sign_index = int(prev_lon / 30)
                to_sign_index = int(boundary / 30)

                from_sign = ZODIAC_SIGNS[from_sign_index]
                to_sign = ZODIAC_SIGNS[to_sign_index]

                ingress_info = {
                    'type': 'ingress',
                    'planet': planet_name,
                    'date': format_datetime_iso(julian_day_to_datetime(exact_jd)),
                    'julian_day': round_decimal(exact_jd),
                    'from_sign': from_sign,
                    'to_sign': to_sign,
                    'exact_degree': round_decimal(exact_lon % 30, 8)
                }

                ingresses.append(ingress_info)

            prev_lon = curr_lon

    # Sort by date
    ingresses.sort(key=lambda x: x['julian_day'])

    return ingresses


def generate_year_ingresses(year: int, output_dir: str = '../data/major-transits') -> List[Dict[str, Any]]:
    """
    Generate planetary ingresses for a year (to be combined with aspects).

    Args:
        year: Year to generate data for
        output_dir: Directory to save output file

    Returns:
        List of ingress events
    """
    print(f"Calculating planetary ingresses for {year}...")
    ingresses = find_ingresses(year)
    print(f"  Found {len(ingresses)} sign changes")

    return ingresses
