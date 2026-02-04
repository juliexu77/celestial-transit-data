"""
Calculate solar and lunar eclipses using Swiss Ephemeris.
"""

import swisseph as swe
from datetime import datetime, timezone
from typing import Dict, List, Any
from lib.config import SWEPH_FLAGS
from utils.formatters import get_zodiac_sign, format_datetime_iso, round_decimal
from utils.julian_date import datetime_to_julian_day, julian_day_to_datetime


# Eclipse type flags from Swiss Ephemeris
ECLIPSE_TYPES = {
    # Solar eclipse types
    swe.ECL_TOTAL: 'total',
    swe.ECL_ANNULAR: 'annular',
    swe.ECL_PARTIAL: 'partial',
    swe.ECL_ANNULAR_TOTAL: 'hybrid',  # Annular-total (hybrid)
    # Lunar eclipse types
    swe.ECL_PENUMBRAL: 'penumbral',
}


def get_eclipse_type_name(eclipse_flags: int, is_solar: bool) -> str:
    """
    Determine eclipse type from Swiss Ephemeris flags.

    Args:
        eclipse_flags: Flags returned by eclipse function
        is_solar: True for solar eclipse, False for lunar

    Returns:
        Eclipse type name
    """
    if is_solar:
        if eclipse_flags & swe.ECL_TOTAL:
            return 'total'
        elif eclipse_flags & swe.ECL_ANNULAR:
            return 'annular'
        elif eclipse_flags & swe.ECL_ANNULAR_TOTAL:
            return 'hybrid'
        elif eclipse_flags & swe.ECL_PARTIAL:
            return 'partial'
    else:
        if eclipse_flags & swe.ECL_TOTAL:
            return 'total'
        elif eclipse_flags & swe.ECL_PENUMBRAL:
            return 'penumbral'
        elif eclipse_flags & swe.ECL_PARTIAL:
            return 'partial'

    return 'unknown'


def get_saros_series(jd: float, is_solar: bool) -> int:
    """
    Calculate approximate Saros series number.

    The Saros cycle is ~18 years, 11 days, 8 hours (6585.32 days).
    This is an approximation based on eclipse dates.

    Args:
        jd: Julian Day of eclipse
        is_solar: True for solar, False for lunar

    Returns:
        Approximate Saros series number
    """
    # Reference eclipses (approximate starting points)
    # Solar: Saros 1 started around 2872 BC
    # Lunar: Similar ancient origin

    # Use a simpler approximation based on known recent Saros numbers
    # Solar eclipse Jan 4, 2011 was Saros 151
    # Lunar eclipse Dec 21, 2010 was Saros 125

    saros_period = 6585.32  # days

    if is_solar:
        ref_jd = 2455565.5  # Jan 4, 2011
        ref_saros = 151
    else:
        ref_jd = 2455551.5  # Dec 21, 2010
        ref_saros = 125

    # Calculate cycles from reference
    cycles = (jd - ref_jd) / saros_period
    saros = ref_saros + round(cycles)

    return saros


def get_eclipse_description(eclipse_type: str, is_solar: bool, sign: str) -> str:
    """
    Generate a human-readable description for an eclipse.

    Args:
        eclipse_type: Type of eclipse (total, partial, etc.)
        is_solar: True for solar, False for lunar
        sign: Zodiac sign of eclipse

    Returns:
        Human-readable description
    """
    body = "Solar" if is_solar else "Lunar"
    type_desc = eclipse_type.capitalize()

    if is_solar:
        if eclipse_type == 'total':
            return f"Total Solar Eclipse in {sign} - Moon completely blocks the Sun"
        elif eclipse_type == 'annular':
            return f"Annular Solar Eclipse in {sign} - 'Ring of Fire' effect visible"
        elif eclipse_type == 'hybrid':
            return f"Hybrid Solar Eclipse in {sign} - Appears both total and annular"
        else:
            return f"Partial Solar Eclipse in {sign} - Moon partially covers the Sun"
    else:
        if eclipse_type == 'total':
            return f"Total Lunar Eclipse in {sign} - 'Blood Moon' visible"
        elif eclipse_type == 'penumbral':
            return f"Penumbral Lunar Eclipse in {sign} - Subtle darkening of Moon"
        else:
            return f"Partial Lunar Eclipse in {sign} - Earth's shadow partially covers Moon"


def find_solar_eclipses(year: int) -> List[Dict[str, Any]]:
    """
    Find all solar eclipses in a given year.

    Args:
        year: Year to find eclipses for

    Returns:
        List of solar eclipse events
    """
    eclipses = []

    # Start from beginning of year
    start_jd = datetime_to_julian_day(datetime(year, 1, 1, tzinfo=timezone.utc))
    end_jd = datetime_to_julian_day(datetime(year + 1, 1, 1, tzinfo=timezone.utc))

    current_jd = start_jd

    while current_jd < end_jd:
        # Find next solar eclipse globally
        # Returns: (return_flag, [jd_max, jd_first, jd_second, jd_third, jd_fourth, ...])
        result = swe.sol_eclipse_when_glob(current_jd, SWEPH_FLAGS)

        if result[0] == 0:
            # No eclipse found
            break

        eclipse_flags = result[0]
        eclipse_times = result[1]
        eclipse_jd = eclipse_times[0]  # Time of maximum eclipse

        # Check if eclipse is within our year
        if eclipse_jd >= end_jd:
            break

        if eclipse_jd >= start_jd:
            # Get eclipse type
            eclipse_type = get_eclipse_type_name(eclipse_flags, is_solar=True)

            # Get Sun and Moon positions at eclipse time
            sun_pos = swe.calc_ut(eclipse_jd, swe.SUN, SWEPH_FLAGS)[0]
            moon_pos = swe.calc_ut(eclipse_jd, swe.MOON, SWEPH_FLAGS)[0]

            sun_lon = sun_pos[0]
            moon_lon = moon_pos[0]

            # Eclipse occurs at the Moon's position (New Moon for solar)
            sign, degree = get_zodiac_sign(moon_lon)

            # Get geographic visibility (central line)
            # swe.sol_eclipse_where returns [longitude, latitude, ...]
            try:
                where_result = swe.sol_eclipse_where(eclipse_jd, SWEPH_FLAGS)
                geo_lon = where_result[0][0]
                geo_lat = where_result[0][1]
                visibility = f"Maximum visibility near {abs(geo_lat):.1f}°{'N' if geo_lat >= 0 else 'S'}, {abs(geo_lon):.1f}°{'E' if geo_lon >= 0 else 'W'}"
            except:
                visibility = "Global visibility varies by location"

            # Get Saros series
            saros = get_saros_series(eclipse_jd, is_solar=True)

            eclipse_data = {
                'type': 'solar',
                'eclipse_type': eclipse_type,
                'date': format_datetime_iso(julian_day_to_datetime(eclipse_jd)),
                'julian_day': round_decimal(eclipse_jd),
                'sun_longitude': round_decimal(sun_lon),
                'moon_longitude': round_decimal(moon_lon),
                'sign': sign,
                'degree': round_decimal(degree),
                'saros_series': saros,
                'description': get_eclipse_description(eclipse_type, True, sign),
                'visibility': visibility
            }

            eclipses.append(eclipse_data)

        # Move to next eclipse (at least 25 days later)
        current_jd = eclipse_jd + 25

    return eclipses


def find_lunar_eclipses(year: int) -> List[Dict[str, Any]]:
    """
    Find all lunar eclipses in a given year.

    Args:
        year: Year to find eclipses for

    Returns:
        List of lunar eclipse events
    """
    eclipses = []

    # Start from beginning of year
    start_jd = datetime_to_julian_day(datetime(year, 1, 1, tzinfo=timezone.utc))
    end_jd = datetime_to_julian_day(datetime(year + 1, 1, 1, tzinfo=timezone.utc))

    current_jd = start_jd

    while current_jd < end_jd:
        # Find next lunar eclipse
        # Returns: (return_flag, [jd_max, jd_partial_begin, jd_partial_end, jd_total_begin, jd_total_end, ...])
        result = swe.lun_eclipse_when(current_jd, SWEPH_FLAGS)

        if result[0] == 0:
            # No eclipse found
            break

        eclipse_flags = result[0]
        eclipse_times = result[1]
        eclipse_jd = eclipse_times[0]  # Time of maximum eclipse

        # Check if eclipse is within our year
        if eclipse_jd >= end_jd:
            break

        if eclipse_jd >= start_jd:
            # Get eclipse type
            eclipse_type = get_eclipse_type_name(eclipse_flags, is_solar=False)

            # Get Sun and Moon positions at eclipse time
            sun_pos = swe.calc_ut(eclipse_jd, swe.SUN, SWEPH_FLAGS)[0]
            moon_pos = swe.calc_ut(eclipse_jd, swe.MOON, SWEPH_FLAGS)[0]

            sun_lon = sun_pos[0]
            moon_lon = moon_pos[0]

            # Eclipse occurs at the Moon's position (Full Moon for lunar)
            sign, degree = get_zodiac_sign(moon_lon)

            # Lunar eclipses visible from anywhere Moon is above horizon
            visibility = "Visible from anywhere the Moon is above the horizon"

            # Get Saros series
            saros = get_saros_series(eclipse_jd, is_solar=False)

            eclipse_data = {
                'type': 'lunar',
                'eclipse_type': eclipse_type,
                'date': format_datetime_iso(julian_day_to_datetime(eclipse_jd)),
                'julian_day': round_decimal(eclipse_jd),
                'sun_longitude': round_decimal(sun_lon),
                'moon_longitude': round_decimal(moon_lon),
                'sign': sign,
                'degree': round_decimal(degree),
                'saros_series': saros,
                'description': get_eclipse_description(eclipse_type, False, sign),
                'visibility': visibility
            }

            eclipses.append(eclipse_data)

        # Move to next eclipse (at least 25 days later)
        current_jd = eclipse_jd + 25

    return eclipses


def find_all_eclipses(year: int) -> List[Dict[str, Any]]:
    """
    Find all solar and lunar eclipses in a given year.

    Args:
        year: Year to find eclipses for

    Returns:
        List of all eclipse events, sorted by date
    """
    solar = find_solar_eclipses(year)
    lunar = find_lunar_eclipses(year)

    all_eclipses = solar + lunar
    all_eclipses.sort(key=lambda x: x['julian_day'])

    return all_eclipses


def generate_year_eclipses(year: int, output_dir: str = '../data/eclipses') -> None:
    """
    Generate eclipse data for a year and save to JSON file.

    Args:
        year: Year to generate data for
        output_dir: Directory to save output file
    """
    import os
    from utils.formatters import save_json

    print(f"Calculating eclipses for {year}...")
    eclipses = find_all_eclipses(year)

    # Count by type
    solar_count = len([e for e in eclipses if e['type'] == 'solar'])
    lunar_count = len([e for e in eclipses if e['type'] == 'lunar'])

    # Create output structure
    output = {
        'metadata': {
            'year': year,
            'generated_at': format_datetime_iso(datetime.now(timezone.utc)),
            'total_eclipses': len(eclipses),
            'solar_eclipses': solar_count,
            'lunar_eclipses': lunar_count,
            'ephemeris_version': f'Swiss Ephemeris {swe.version}'
        },
        'eclipses': eclipses
    }

    # Save to file
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{year}.json")
    save_json(output, output_file)

    print(f"  Found {len(eclipses)} eclipses ({solar_count} solar, {lunar_count} lunar)")
    print(f"  Saved to {output_file}")

    # Print details
    for eclipse in eclipses:
        print(f"    {eclipse['date'][:10]}: {eclipse['eclipse_type'].capitalize()} {eclipse['type'].capitalize()} in {eclipse['sign']}")
