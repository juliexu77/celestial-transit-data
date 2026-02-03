"""
Calculate exact times of moon phases using binary search.
"""

import swisseph as swe
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Tuple
from lib.config import PLANETS, SWEPH_FLAGS, MOON_PHASES
from utils.formatters import get_zodiac_sign, format_datetime_iso, round_decimal
from utils.julian_date import datetime_to_julian_day, julian_day_to_datetime


def get_sun_moon_angle(jd: float) -> float:
    """
    Calculate the angle between Sun and Moon (in degrees).

    Args:
        jd: Julian Day number

    Returns:
        Angle in degrees (0-360)
    """
    sun_pos = swe.calc_ut(jd, PLANETS['Sun']['id'], SWEPH_FLAGS)[0]
    moon_pos = swe.calc_ut(jd, PLANETS['Moon']['id'], SWEPH_FLAGS)[0]

    sun_lon = sun_pos[0]
    moon_lon = moon_pos[0]

    # Calculate angle difference
    angle = (moon_lon - sun_lon) % 360
    return angle


def find_exact_phase_time(start_jd: float, end_jd: float, target_angle: float, tolerance: float = 0.01) -> float:
    """
    Use binary search to find exact Julian Day when Sun-Moon angle matches target.

    Args:
        start_jd: Starting Julian Day
        end_jd: Ending Julian Day
        target_angle: Target angle in degrees (0, 90, 180, 270)
        tolerance: Acceptable error in degrees (default 0.01 = ~0.6 arcminutes)

    Returns:
        Julian Day of exact phase
    """
    max_iterations = 50
    iteration = 0

    while iteration < max_iterations:
        mid_jd = (start_jd + end_jd) / 2
        current_angle = get_sun_moon_angle(mid_jd)

        # Handle angle wrapping (e.g., New Moon around 0°/360°)
        if target_angle == 0:
            # For new moon, treat angles > 180 as negative
            if current_angle > 180:
                current_angle = current_angle - 360

        # Calculate error
        error = current_angle - target_angle

        # Check if we're within tolerance
        if abs(error) < tolerance:
            return mid_jd

        # Adjust search range
        if error > 0:
            end_jd = mid_jd
        else:
            start_jd = mid_jd

        iteration += 1

    # Return best estimate if we didn't converge
    return (start_jd + end_jd) / 2


def detect_phase_crossing(prev_angle: float, curr_angle: float, target_angle: float) -> bool:
    """
    Detect if a phase angle was crossed between two measurements.

    Args:
        prev_angle: Previous Sun-Moon angle
        curr_angle: Current Sun-Moon angle
        target_angle: Target phase angle (0, 90, 180, 270)

    Returns:
        True if phase was crossed
    """
    # Handle angle wrapping for new moon (around 0°/360°)
    if target_angle == 0:
        # Crossing new moon if we go from high angle (>270) to low angle (<90)
        if prev_angle > 270 and curr_angle < 90:
            return True
    else:
        # For other phases, check if we crossed the target
        if prev_angle < target_angle <= curr_angle:
            return True

    return False


def find_moon_phases(year: int) -> List[Dict[str, Any]]:
    """
    Find all moon phases for a given year.

    Args:
        year: Year to find phases for

    Returns:
        List of moon phase events with exact times
    """
    phases = []

    # Scan through year at daily intervals
    start_date = datetime(year, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)

    current_date = start_date
    prev_angle = get_sun_moon_angle(datetime_to_julian_day(current_date))

    while current_date < end_date:
        current_date += timedelta(days=1)
        current_jd = datetime_to_julian_day(current_date)
        current_angle = get_sun_moon_angle(current_jd)

        # Check for each phase type
        for phase_name, target_angle in MOON_PHASES.items():
            if detect_phase_crossing(prev_angle, current_angle, target_angle):
                # Found a phase crossing, use binary search to find exact time
                prev_jd = current_jd - 1.0  # Previous day
                exact_jd = find_exact_phase_time(prev_jd, current_jd, target_angle)

                # Get exact positions at phase time
                sun_pos = swe.calc_ut(exact_jd, PLANETS['Sun']['id'], SWEPH_FLAGS)[0]
                moon_pos = swe.calc_ut(exact_jd, PLANETS['Moon']['id'], SWEPH_FLAGS)[0]

                sun_lon = sun_pos[0]
                moon_lon = moon_pos[0]

                sun_sign, sun_degree = get_zodiac_sign(sun_lon)
                moon_sign, moon_degree = get_zodiac_sign(moon_lon)

                # Calculate exactness (how close to perfect alignment)
                angle_diff = abs(get_sun_moon_angle(exact_jd) - target_angle)
                if target_angle == 0 and angle_diff > 180:
                    angle_diff = 360 - angle_diff

                phase_data = {
                    'phase': phase_name,
                    'date': format_datetime_iso(julian_day_to_datetime(exact_jd)),
                    'julian_day': round_decimal(exact_jd),
                    'sun_longitude': round_decimal(sun_lon),
                    'moon_longitude': round_decimal(moon_lon),
                    'sun_sign': sun_sign,
                    'moon_sign': moon_sign,
                    'sun_degree': round_decimal(sun_degree),
                    'moon_degree': round_decimal(moon_degree),
                    'exactness_degrees': round_decimal(angle_diff, 8)
                }

                phases.append(phase_data)

        prev_angle = current_angle

    # Sort phases by date
    phases.sort(key=lambda x: x['julian_day'])

    return phases


def generate_year_moon_phases(year: int, output_dir: str = '../data/moon-phases') -> None:
    """
    Generate moon phases for a year and save to JSON file.

    Args:
        year: Year to generate data for
        output_dir: Directory to save output file
    """
    import os
    from utils.formatters import save_json

    print(f"Calculating moon phases for {year}...")
    phases = find_moon_phases(year)

    # Create output structure
    output = {
        'metadata': {
            'year': year,
            'generated_at': format_datetime_iso(datetime.now(timezone.utc)),
            'total_phases': len(phases),
            'ephemeris_version': f'Swiss Ephemeris {swe.version}'
        },
        'phases': phases
    }

    # Save to file
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{year}.json")
    save_json(output, output_file)

    print(f"  Found {len(phases)} moon phases")
    print(f"  Saved to {output_file}")

    # Print summary
    phase_counts = {}
    for phase in phases:
        phase_name = phase['phase']
        phase_counts[phase_name] = phase_counts.get(phase_name, 0) + 1

    print(f"  Phase breakdown: {phase_counts}")
