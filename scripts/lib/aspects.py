"""
Calculate major aspects between outer planets.
"""

import swisseph as swe
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Tuple
from lib.config import PLANETS, SWEPH_FLAGS, ASPECTS, OUTER_PLANETS, INNER_PLANETS_FOR_CONJUNCTIONS
from utils.formatters import get_zodiac_sign, format_datetime_iso, round_decimal
from utils.julian_date import datetime_to_julian_day, julian_day_to_datetime


def get_planet_longitude(jd: float, planet_name: str) -> float:
    """
    Get ecliptic longitude of a planet at given Julian Day.

    Args:
        jd: Julian Day number
        planet_name: Name of planet

    Returns:
        Longitude in degrees (0-360)
    """
    planet_id = PLANETS[planet_name]['id']
    result = swe.calc_ut(jd, planet_id, SWEPH_FLAGS)
    return result[0][0]


def calculate_aspect_angle(lon1: float, lon2: float) -> float:
    """
    Calculate the angular separation between two longitudes.

    Args:
        lon1: First longitude
        lon2: Second longitude

    Returns:
        Angular separation in degrees (0-180)
    """
    diff = abs(lon2 - lon1) % 360
    # Always return the smaller angle
    if diff > 180:
        diff = 360 - diff
    return diff


def calculate_signed_separation(lon1: float, lon2: float) -> float:
    """
    Calculate signed separation between two longitudes.
    Positive = planet1 ahead of planet2, Negative = planet1 behind.
    Used to detect when faster planet passes slower (sign change = exact pass).

    Args:
        lon1: First planet longitude
        lon2: Second planet longitude

    Returns:
        Signed separation in degrees (-180 to +180)
    """
    diff = (lon1 - lon2) % 360
    if diff > 180:
        diff -= 360
    return diff


def is_in_aspect(angle: float, aspect_name: str) -> bool:
    """
    Check if an angular separation qualifies as a specific aspect.

    Args:
        angle: Angular separation in degrees
        aspect_name: Name of aspect to check

    Returns:
        True if within orb
    """
    aspect_data = ASPECTS[aspect_name]
    target_angle = aspect_data['angle']
    orb = aspect_data['orb']

    return abs(angle - target_angle) <= orb


def find_exact_aspect_time(start_jd: float, end_jd: float, planet1: str, planet2: str,
                           target_angle: float, tolerance: float = 0.01) -> float:
    """
    Find exact time when two planets reach a specific aspect angle.

    Args:
        start_jd: Starting Julian Day
        end_jd: Ending Julian Day
        planet1: Name of first planet
        planet2: Name of second planet
        target_angle: Target aspect angle
        tolerance: Acceptable error in degrees

    Returns:
        Julian Day of exact aspect
    """
    max_iterations = 50
    iteration = 0

    while iteration < max_iterations:
        mid_jd = (start_jd + end_jd) / 2

        lon1 = get_planet_longitude(mid_jd, planet1)
        lon2 = get_planet_longitude(mid_jd, planet2)
        current_angle = calculate_aspect_angle(lon1, lon2)

        error = abs(current_angle - target_angle)

        if error < tolerance:
            return mid_jd

        # Determine which direction to search
        # Sample slightly before and after to find gradient
        test_jd = mid_jd + 0.1
        test_lon1 = get_planet_longitude(test_jd, planet1)
        test_lon2 = get_planet_longitude(test_jd, planet2)
        test_angle = calculate_aspect_angle(test_lon1, test_lon2)

        # If angle is increasing, we need to go backwards; if decreasing, go forwards
        if abs(test_angle - target_angle) < abs(current_angle - target_angle):
            # Getting closer, move forward
            start_jd = mid_jd
        else:
            # Getting further, move backward
            end_jd = mid_jd

        iteration += 1

    return (start_jd + end_jd) / 2


def find_exact_conjunction_pass(start_jd: float, end_jd: float, planet1: str, planet2: str,
                                 tolerance: float = 0.001) -> float:
    """
    Find exact time when one planet passes another (conjunction exactness).
    Uses signed separation to find the zero crossing.

    Args:
        start_jd: Starting Julian Day (before pass)
        end_jd: Ending Julian Day (after pass)
        planet1: Name of first planet
        planet2: Name of second planet
        tolerance: Acceptable error in degrees

    Returns:
        Julian Day of exact conjunction pass
    """
    max_iterations = 50
    iteration = 0

    # Binary search for zero crossing of signed separation
    while iteration < max_iterations and (end_jd - start_jd) > tolerance / 100:
        mid_jd = (start_jd + end_jd) / 2

        lon1_start = get_planet_longitude(start_jd, planet1)
        lon2_start = get_planet_longitude(start_jd, planet2)
        sep_start = calculate_signed_separation(lon1_start, lon2_start)

        lon1_mid = get_planet_longitude(mid_jd, planet1)
        lon2_mid = get_planet_longitude(mid_jd, planet2)
        sep_mid = calculate_signed_separation(lon1_mid, lon2_mid)

        # Check if zero crossing is in first half or second half
        if sep_start * sep_mid <= 0:
            # Zero crossing in first half
            end_jd = mid_jd
        else:
            # Zero crossing in second half
            start_jd = mid_jd

        iteration += 1

    return (start_jd + end_jd) / 2


def find_aspects(year: int) -> List[Dict[str, Any]]:
    """
    Find all major aspects between outer planets for a given year.

    For conjunctions, detects each exact pass (when planets' longitudes cross).
    For other aspects, uses orb-based detection.

    Args:
        year: Year to find aspects for

    Returns:
        List of aspect events
    """
    aspects_found = []

    # Track active aspects for non-conjunction aspects (orb-based)
    active_aspects = {}

    # Track previous signed separations for conjunction exact pass detection
    prev_separations = {}

    # Scan through year at daily intervals
    start_date = datetime(year, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)

    current_date = start_date

    while current_date < end_date:
        current_jd = datetime_to_julian_day(current_date)

        # Check all pairs of outer planets
        for i, planet1 in enumerate(OUTER_PLANETS):
            for planet2 in OUTER_PLANETS[i + 1:]:
                lon1 = get_planet_longitude(current_jd, planet1)
                lon2 = get_planet_longitude(current_jd, planet2)
                angle = calculate_aspect_angle(lon1, lon2)

                # CONJUNCTIONS: Detect each exact pass via signed separation crossing
                conj_key = f"{planet1}-{planet2}-conjunction"
                curr_sep = calculate_signed_separation(lon1, lon2)

                if conj_key in prev_separations:
                    prev_sep = prev_separations[conj_key]
                    # Detect zero crossing (sign change) = exact conjunction pass
                    if prev_sep * curr_sep < 0 and abs(prev_sep) < 15 and abs(curr_sep) < 15:
                        # Found an exact pass - refine the time
                        prev_jd = current_jd - 1.0
                        exact_jd = find_exact_conjunction_pass(prev_jd, current_jd, planet1, planet2)

                        # Get exact positions
                        exact_lon1 = get_planet_longitude(exact_jd, planet1)
                        exact_lon2 = get_planet_longitude(exact_jd, planet2)

                        sign1, degree1 = get_zodiac_sign(exact_lon1)
                        sign2, degree2 = get_zodiac_sign(exact_lon2)

                        exact_angle = calculate_aspect_angle(exact_lon1, exact_lon2)

                        aspect_info = {
                            'type': 'aspect',
                            'aspect': 'conjunction',
                            'symbol': ASPECTS['conjunction']['symbol'],
                            'planet1': planet1,
                            'planet2': planet2,
                            'date': format_datetime_iso(julian_day_to_datetime(exact_jd)),
                            'julian_day': round_decimal(exact_jd),
                            'planet1_position': {
                                'longitude': round_decimal(exact_lon1),
                                'sign': sign1,
                                'degree': round_decimal(degree1)
                            },
                            'planet2_position': {
                                'longitude': round_decimal(exact_lon2),
                                'sign': sign2,
                                'degree': round_decimal(degree2)
                            },
                            'exactness': round_decimal(exact_angle, 8),
                            'orb_used': ASPECTS['conjunction']['orb']
                        }
                        aspects_found.append(aspect_info)

                prev_separations[conj_key] = curr_sep

                # OTHER ASPECTS: Use orb-based detection (unchanged)
                for aspect_name, aspect_data in ASPECTS.items():
                    if aspect_name == 'conjunction':
                        continue  # Already handled above

                    aspect_key = f"{planet1}-{planet2}-{aspect_name}"

                    if is_in_aspect(angle, aspect_name):
                        if aspect_key not in active_aspects:
                            prev_jd = current_jd - 1.0
                            exact_jd = find_exact_aspect_time(
                                prev_jd, current_jd + 1.0,
                                planet1, planet2,
                                aspect_data['angle']
                            )

                            exact_lon1 = get_planet_longitude(exact_jd, planet1)
                            exact_lon2 = get_planet_longitude(exact_jd, planet2)

                            sign1, degree1 = get_zodiac_sign(exact_lon1)
                            sign2, degree2 = get_zodiac_sign(exact_lon2)

                            exact_angle = calculate_aspect_angle(exact_lon1, exact_lon2)
                            exactness = abs(exact_angle - aspect_data['angle'])

                            aspect_info = {
                                'type': 'aspect',
                                'aspect': aspect_name,
                                'symbol': aspect_data['symbol'],
                                'planet1': planet1,
                                'planet2': planet2,
                                'date': format_datetime_iso(julian_day_to_datetime(exact_jd)),
                                'julian_day': round_decimal(exact_jd),
                                'planet1_position': {
                                    'longitude': round_decimal(exact_lon1),
                                    'sign': sign1,
                                    'degree': round_decimal(degree1)
                                },
                                'planet2_position': {
                                    'longitude': round_decimal(exact_lon2),
                                    'sign': sign2,
                                    'degree': round_decimal(degree2)
                                },
                                'exactness': round_decimal(exactness, 8),
                                'orb_used': aspect_data['orb']
                            }

                            aspects_found.append(aspect_info)
                            active_aspects[aspect_key] = True
                    else:
                        if aspect_key in active_aspects:
                            del active_aspects[aspect_key]

        # Check conjunctions between inner planets (Venus, Mars) and outer planets
        # Also use exact pass detection for these
        for inner_planet in INNER_PLANETS_FOR_CONJUNCTIONS:
            for outer_planet in OUTER_PLANETS:
                lon1 = get_planet_longitude(current_jd, inner_planet)
                lon2 = get_planet_longitude(current_jd, outer_planet)

                conj_key = f"{inner_planet}-{outer_planet}-conjunction"
                curr_sep = calculate_signed_separation(lon1, lon2)

                if conj_key in prev_separations:
                    prev_sep = prev_separations[conj_key]
                    # Detect zero crossing (sign change) = exact conjunction pass
                    if prev_sep * curr_sep < 0 and abs(prev_sep) < 20 and abs(curr_sep) < 20:
                        prev_jd = current_jd - 1.0
                        exact_jd = find_exact_conjunction_pass(prev_jd, current_jd, inner_planet, outer_planet)

                        exact_lon1 = get_planet_longitude(exact_jd, inner_planet)
                        exact_lon2 = get_planet_longitude(exact_jd, outer_planet)

                        sign1, degree1 = get_zodiac_sign(exact_lon1)
                        sign2, degree2 = get_zodiac_sign(exact_lon2)

                        exact_angle = calculate_aspect_angle(exact_lon1, exact_lon2)

                        aspect_info = {
                            'type': 'aspect',
                            'aspect': 'conjunction',
                            'symbol': ASPECTS['conjunction']['symbol'],
                            'planet1': inner_planet,
                            'planet2': outer_planet,
                            'date': format_datetime_iso(julian_day_to_datetime(exact_jd)),
                            'julian_day': round_decimal(exact_jd),
                            'planet1_position': {
                                'longitude': round_decimal(exact_lon1),
                                'sign': sign1,
                                'degree': round_decimal(degree1)
                            },
                            'planet2_position': {
                                'longitude': round_decimal(exact_lon2),
                                'sign': sign2,
                                'degree': round_decimal(degree2)
                            },
                            'exactness': round_decimal(exact_angle, 8),
                            'orb_used': ASPECTS['conjunction']['orb']
                        }

                        aspects_found.append(aspect_info)

                prev_separations[conj_key] = curr_sep

        current_date += timedelta(days=1)

    # Sort by date
    aspects_found.sort(key=lambda x: x['julian_day'])

    return aspects_found


def generate_year_aspects(year: int, output_dir: str = '../data/major-transits') -> List[Dict[str, Any]]:
    """
    Generate major aspects for a year (to be combined with ingresses).

    Args:
        year: Year to generate data for
        output_dir: Directory to save output file

    Returns:
        List of aspect events
    """
    print(f"Calculating major aspects for {year}...")
    aspects = find_aspects(year)
    print(f"  Found {len(aspects)} major aspects")

    return aspects
