"""
Calculate planetary retrograde periods.
"""

import swisseph as swe
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Tuple
from lib.config import PLANETS, SWEPH_FLAGS, RETROGRADE_PLANETS
from utils.formatters import get_zodiac_sign, format_datetime_iso, round_decimal
from utils.julian_date import datetime_to_julian_day, julian_day_to_datetime


def get_planet_speed(jd: float, planet_name: str) -> Tuple[float, float]:
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
    speed = result[0][3]  # Longitudinal speed in degrees/day
    return longitude, speed


def find_exact_station_time(start_jd: float, end_jd: float, planet_name: str,
                            tolerance: float = 0.0001) -> float:
    """
    Find exact time when planet speed crosses zero (station).

    Args:
        start_jd: Starting Julian Day
        end_jd: Ending Julian Day
        planet_name: Name of planet
        tolerance: Acceptable error in speed

    Returns:
        Julian Day of exact station
    """
    max_iterations = 50
    iteration = 0

    while iteration < max_iterations:
        mid_jd = (start_jd + end_jd) / 2
        _, speed = get_planet_speed(mid_jd, planet_name)

        if abs(speed) < tolerance:
            return mid_jd

        # Check which direction to search
        _, start_speed = get_planet_speed(start_jd, planet_name)
        _, end_speed = get_planet_speed(end_jd, planet_name)

        # Use bisection based on sign of speed
        if speed > 0:
            if start_speed < 0:
                end_jd = mid_jd
            else:
                start_jd = mid_jd
        else:
            if end_speed > 0:
                start_jd = mid_jd
            else:
                end_jd = mid_jd

        iteration += 1

    return (start_jd + end_jd) / 2


def find_retrograde_periods(year: int, planet_names: List[str] = None) -> List[Dict[str, Any]]:
    """
    Find all retrograde periods for specified planets in a given year.

    Args:
        year: Year to find retrogrades for
        planet_names: List of planet names (default: RETROGRADE_PLANETS)

    Returns:
        List of retrograde period events
    """
    if planet_names is None:
        planet_names = RETROGRADE_PLANETS

    retrograde_periods = []

    # Scan through year at daily intervals
    start_date = datetime(year, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)

    for planet_name in planet_names:
        current_date = start_date
        prev_lon, prev_speed = get_planet_speed(datetime_to_julian_day(current_date), planet_name)

        station_rx_data = None  # Store station retrograde data

        while current_date < end_date:
            current_date += timedelta(days=1)
            current_jd = datetime_to_julian_day(current_date)
            curr_lon, curr_speed = get_planet_speed(current_jd, planet_name)

            # Check for station retrograde (speed crosses 0 from + to -)
            if prev_speed > 0 and curr_speed < 0:
                # Found station retrograde
                prev_jd = current_jd - 1.0
                exact_jd = find_exact_station_time(prev_jd, current_jd, planet_name)

                exact_lon, _ = get_planet_speed(exact_jd, planet_name)
                sign, degree = get_zodiac_sign(exact_lon)

                station_rx_data = {
                    'date': format_datetime_iso(julian_day_to_datetime(exact_jd)),
                    'julian_day': round_decimal(exact_jd),
                    'longitude': round_decimal(exact_lon),
                    'sign': sign,
                    'degree': round_decimal(degree)
                }

            # Check for station direct (speed crosses 0 from - to +)
            elif prev_speed < 0 and curr_speed > 0:
                # Found station direct
                if station_rx_data is not None:
                    # Complete the retrograde period
                    prev_jd = current_jd - 1.0
                    exact_jd = find_exact_station_time(prev_jd, current_jd, planet_name)

                    exact_lon, _ = get_planet_speed(exact_jd, planet_name)
                    sign, degree = get_zodiac_sign(exact_lon)

                    station_direct_data = {
                        'date': format_datetime_iso(julian_day_to_datetime(exact_jd)),
                        'julian_day': round_decimal(exact_jd),
                        'longitude': round_decimal(exact_lon),
                        'sign': sign,
                        'degree': round_decimal(degree)
                    }

                    # Calculate duration
                    duration_days = station_direct_data['julian_day'] - station_rx_data['julian_day']

                    # Calculate shadow periods (simplified: ±15 days for Mercury, ±20 for Venus/Mars)
                    if planet_name == 'Mercury':
                        shadow_days = 15
                    elif planet_name in ['Venus', 'Mars']:
                        shadow_days = 20
                    else:
                        shadow_days = 0

                    retrograde_info = {
                        'planet': planet_name,
                        'station_retrograde': station_rx_data,
                        'station_direct': station_direct_data,
                        'duration_days': round_decimal(duration_days)
                    }

                    if shadow_days > 0:
                        shadow_start = julian_day_to_datetime(station_rx_data['julian_day'] - shadow_days)
                        shadow_end = julian_day_to_datetime(station_direct_data['julian_day'] + shadow_days)
                        retrograde_info['pre_retrograde_shadow_start'] = format_datetime_iso(shadow_start)
                        retrograde_info['post_retrograde_shadow_end'] = format_datetime_iso(shadow_end)

                    retrograde_periods.append(retrograde_info)
                    station_rx_data = None

            prev_lon = curr_lon
            prev_speed = curr_speed

    # Sort by station retrograde date
    retrograde_periods.sort(key=lambda x: x['station_retrograde']['julian_day'])

    return retrograde_periods


def generate_year_retrogrades(year: int, output_dir: str = '../data/retrogrades') -> None:
    """
    Generate retrograde periods for a year and save to JSON file.

    Args:
        year: Year to generate data for
        output_dir: Directory to save output file
    """
    import os
    from utils.formatters import save_json

    print(f"Calculating retrograde periods for {year}...")
    retrogrades = find_retrograde_periods(year)

    # Create output structure
    output = {
        'metadata': {
            'year': year,
            'generated_at': format_datetime_iso(datetime.now(timezone.utc)),
            'planets_tracked': RETROGRADE_PLANETS,
            'ephemeris_version': f'Swiss Ephemeris {swe.version}'
        },
        'retrogrades': retrogrades
    }

    # Save to file
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{year}.json")
    save_json(output, output_file)

    print(f"  Found {len(retrogrades)} retrograde periods")
    print(f"  Saved to {output_file}")

    # Print summary by planet
    planet_counts = {}
    for retro in retrogrades:
        planet = retro['planet']
        planet_counts[planet] = planet_counts.get(planet, 0) + 1

    print(f"  Retrograde breakdown: {planet_counts}")
