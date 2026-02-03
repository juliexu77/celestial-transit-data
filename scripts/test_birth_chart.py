#!/usr/bin/env python3
"""
Test script to calculate a natal chart.
"""

import swisseph as swe
from datetime import datetime
import pytz
from lib.config import PLANETS, SWEPH_FLAGS, ZODIAC_SIGNS
from utils.formatters import get_zodiac_sign, round_decimal
from utils.julian_date import datetime_to_julian_day


def calculate_ascendant(jd: float, latitude: float, longitude: float) -> dict:
    """
    Calculate Ascendant (Rising Sign) for a given time and location.

    Args:
        jd: Julian Day in UTC
        latitude: Geographic latitude in degrees
        longitude: Geographic longitude in degrees

    Returns:
        Dictionary with ascendant longitude and sign
    """
    # Calculate houses using Placidus system (most common)
    # swe.houses returns (cusps, ascmc)
    # ascmc[0] is Ascendant, ascmc[1] is MC
    houses_result = swe.houses(jd, latitude, longitude, b'P')  # 'P' = Placidus
    cusps = houses_result[0]
    ascmc = houses_result[1]

    ascendant_lon = ascmc[0]  # Ascendant longitude
    mc_lon = ascmc[1]  # Midheaven (MC)

    asc_sign, asc_degree = get_zodiac_sign(ascendant_lon)
    mc_sign, mc_degree = get_zodiac_sign(mc_lon)

    # Calculate all 12 house cusps
    # cusps is a tuple with indices 0-11, where 0 is House 1, 1 is House 2, etc.
    house_cusps = []
    for i in range(12):
        cusp_lon = cusps[i]
        sign, degree = get_zodiac_sign(cusp_lon)
        house_cusps.append({
            'house': i + 1,  # Houses are numbered 1-12
            'longitude': round_decimal(cusp_lon),
            'sign': sign,
            'degree': round_decimal(degree)
        })

    return {
        'ascendant': {
            'longitude': round_decimal(ascendant_lon),
            'sign': asc_sign,
            'degree': round_decimal(asc_degree)
        },
        'midheaven': {
            'longitude': round_decimal(mc_lon),
            'sign': mc_sign,
            'degree': round_decimal(mc_degree)
        },
        'house_cusps': house_cusps
    }


def calculate_natal_chart(birth_datetime: datetime, latitude: float, longitude: float):
    """
    Calculate complete natal chart for a birth time and location.

    Args:
        birth_datetime: Birth date/time (should be in local timezone or UTC)
        latitude: Birth location latitude
        longitude: Birth location longitude

    Returns:
        Dictionary with complete natal chart data
    """
    # Convert to Julian Day
    jd = datetime_to_julian_day(birth_datetime)

    # Calculate Ascendant and houses
    houses_data = calculate_ascendant(jd, latitude, longitude)

    # Calculate planetary positions
    planets = {}
    for planet_name, planet_info in PLANETS.items():
        planet_id = planet_info['id']
        result = swe.calc_ut(jd, planet_id, SWEPH_FLAGS)

        longitude = result[0][0]
        latitude_planet = result[0][1]
        distance = result[0][2]
        speed = result[0][3]

        sign, degree = get_zodiac_sign(longitude)

        planets[planet_name] = {
            'longitude': round_decimal(longitude),
            'latitude': round_decimal(latitude_planet),
            'distance_au': round_decimal(distance),
            'speed': round_decimal(speed),
            'sign': sign,
            'degree': round_decimal(degree),
            'retrograde': speed < 0
        }

    # Determine which house each planet is in
    for planet_name, planet_data in planets.items():
        planet_lon = planet_data['longitude']

        # Find which house the planet is in
        # A planet is in a house if its longitude is between the cusp of that house
        # and the cusp of the next house
        for i, cusp in enumerate(houses_data['house_cusps']):
            next_i = (i + 1) % 12
            next_cusp = houses_data['house_cusps'][next_i]

            cusp_lon = cusp['longitude']
            next_cusp_lon = next_cusp['longitude']

            # Handle zodiac wrap-around (Pisces to Aries)
            if next_cusp_lon < cusp_lon:
                # House crosses 0° Aries
                if planet_lon >= cusp_lon or planet_lon < next_cusp_lon:
                    planet_data['house'] = cusp['house']
                    break
            else:
                # Normal case
                if cusp_lon <= planet_lon < next_cusp_lon:
                    planet_data['house'] = cusp['house']
                    break

    return {
        'birth_datetime': birth_datetime.isoformat(),
        'location': {
            'latitude': latitude,
            'longitude': longitude
        },
        'ascendant': houses_data['ascendant'],
        'midheaven': houses_data['midheaven'],
        'house_cusps': houses_data['house_cusps'],
        'planets': planets
    }


def find_house_for_sign(house_cusps: list, sign_name: str) -> list:
    """
    Find which house(s) contain a specific zodiac sign.

    Args:
        house_cusps: List of house cusp data
        sign_name: Name of zodiac sign

    Returns:
        List of house numbers that contain this sign
    """
    houses_with_sign = []

    for i, cusp in enumerate(house_cusps):
        next_i = (i + 1) % 12
        next_cusp = house_cusps[next_i]

        cusp_lon = cusp['longitude']
        next_cusp_lon = next_cusp['longitude']

        # Get the range of signs covered by this house
        sign_index = ZODIAC_SIGNS.index(sign_name)
        sign_start = sign_index * 30
        sign_end = sign_start + 30

        # Check if the sign falls within this house
        if next_cusp_lon < cusp_lon:
            # House crosses 0° Aries
            if (sign_start >= cusp_lon or sign_end <= next_cusp_lon or
                (sign_start < next_cusp_lon and cusp_lon <= sign_end)):
                houses_with_sign.append(cusp['house'])
        else:
            # Normal case - check if sign overlaps with house
            if (sign_start < next_cusp_lon and sign_end > cusp_lon):
                houses_with_sign.append(cusp['house'])

    return houses_with_sign


def main():
    """Test natal chart calculation."""

    # Birth data
    # December 16, 1988, 9:30 PM in Shanghai, China
    # Shanghai: 31.2304° N, 121.4737° E
    # Timezone: China Standard Time (UTC+8)

    # Create datetime in China Standard Time
    china_tz = pytz.timezone('Asia/Shanghai')
    birth_local = china_tz.localize(datetime(1988, 12, 16, 21, 30, 0))

    # Convert to UTC for calculations
    birth_utc = birth_local.astimezone(pytz.UTC)

    latitude = 31.2304  # Shanghai latitude
    longitude = 121.4737  # Shanghai longitude

    print("=" * 70)
    print("NATAL CHART CALCULATION")
    print("=" * 70)
    print(f"\nBirth Date: December 16, 1988")
    print(f"Birth Time: 9:30 PM (local time)")
    print(f"Location: Shanghai, China ({latitude}°N, {longitude}°E)")
    print(f"UTC Time: {birth_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Local Time: {birth_local.strftime('%Y-%m-%d %H:%M:%S %Z')}")

    # Calculate natal chart
    chart = calculate_natal_chart(birth_utc, latitude, longitude)

    print("\n" + "=" * 70)
    print("1. SUN / MOON / RISING (ASCENDANT)")
    print("=" * 70)

    sun = chart['planets']['Sun']
    moon = chart['planets']['Moon']
    ascendant = chart['ascendant']

    print(f"\nSUN:       {sun['sign']} {sun['degree']:.2f}° (House {sun.get('house', '?')})")
    print(f"MOON:      {moon['sign']} {moon['degree']:.2f}° (House {moon.get('house', '?')})")
    print(f"RISING:    {ascendant['sign']} {ascendant['degree']:.2f}°")
    print(f"MIDHEAVEN: {chart['midheaven']['sign']} {chart['midheaven']['degree']:.2f}°")

    print("\n" + "=" * 70)
    print("2. CAPRICORN HOUSE PLACEMENT")
    print("=" * 70)

    # Find which house(s) contain Capricorn
    capricorn_houses = find_house_for_sign(chart['house_cusps'], 'Capricorn')

    print(f"\nCapricorn is in House(s): {capricorn_houses}")

    # Count planets in Capricorn houses
    planets_in_cap_houses = []
    for planet_name, planet_data in chart['planets'].items():
        if planet_data.get('house') in capricorn_houses:
            planets_in_cap_houses.append(planet_name)

    print(f"Number of planets in Capricorn house(s): {len(planets_in_cap_houses)}")
    if planets_in_cap_houses:
        print(f"Planets: {', '.join(planets_in_cap_houses)}")

    # Also show planets actually in Capricorn sign
    planets_in_cap_sign = [name for name, data in chart['planets'].items()
                           if data['sign'] == 'Capricorn']
    print(f"\nPlanets in Capricorn sign: {len(planets_in_cap_sign)}")
    if planets_in_cap_sign:
        print(f"Planets: {', '.join(planets_in_cap_sign)}")

    print("\n" + "=" * 70)
    print("COMPLETE PLANETARY POSITIONS")
    print("=" * 70)

    for planet_name, planet_data in chart['planets'].items():
        rx = " (R)" if planet_data['retrograde'] else ""
        print(f"{planet_name:10} {planet_data['sign']:12} {planet_data['degree']:6.2f}° "
              f"House {planet_data.get('house', '?')}{rx}")

    print("\n" + "=" * 70)
    print("HOUSE CUSPS")
    print("=" * 70)

    for cusp in chart['house_cusps']:
        print(f"House {cusp['house']:2}:  {cusp['sign']:12} {cusp['degree']:6.2f}°")


if __name__ == '__main__':
    main()
