#!/usr/bin/env python3
"""
Show current transits and moon phase for today.
"""

import json
from datetime import datetime, timezone
import os


def load_json(filepath):
    """Load JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def get_current_positions(date_str):
    """
    Get planetary positions for a specific date.

    Args:
        date_str: Date in YYYY-MM-DD format

    Returns:
        Dictionary with planetary positions
    """
    year, month, day = date_str.split('-')
    month_str = f"{year}-{month}"

    filepath = f"../data/daily-positions/{month_str}.json"

    if not os.path.exists(filepath):
        return None

    data = load_json(filepath)

    # Find the specific date
    for position in data['positions']:
        if position['date'] == date_str:
            return position

    return None


def get_current_moon_phase(date_str):
    """
    Get the most recent moon phase before or on the given date.

    Args:
        date_str: Date in YYYY-MM-DD format

    Returns:
        Dictionary with moon phase information
    """
    year = date_str.split('-')[0]
    filepath = f"../data/moon-phases/{year}.json"

    if not os.path.exists(filepath):
        return None

    data = load_json(filepath)
    target_date = datetime.fromisoformat(date_str + "T00:00:00Z")

    # Find the most recent phase
    recent_phase = None
    next_phase = None

    for phase in data['phases']:
        phase_date = datetime.fromisoformat(phase['date'].replace('Z', '+00:00'))

        if phase_date <= target_date:
            recent_phase = phase
        elif phase_date > target_date and next_phase is None:
            next_phase = phase
            break

    return recent_phase, next_phase


def format_phase_name(phase):
    """Format phase name for display."""
    names = {
        'new': 'New Moon 🌑',
        'first_quarter': 'First Quarter 🌓',
        'full': 'Full Moon 🌕',
        'last_quarter': 'Last Quarter 🌗'
    }
    return names.get(phase, phase)


def calculate_days_between(date1_str, date2_str):
    """Calculate days between two ISO date strings."""
    d1 = datetime.fromisoformat(date1_str.replace('Z', '+00:00'))
    d2 = datetime.fromisoformat(date2_str.replace('Z', '+00:00'))
    return abs((d2 - d1).days)


def main():
    """Show current transits and moon phase."""

    # Get today's date
    today = datetime.now(timezone.utc)
    date_str = today.strftime('%Y-%m-%d')

    print("=" * 70)
    print("CURRENT TRANSITS & MOON PHASE")
    print("=" * 70)
    print(f"\nDate: {today.strftime('%B %d, %Y')} (UTC)")
    print(f"Time: {today.strftime('%H:%M:%S UTC')}")

    # Get current positions
    positions = get_current_positions(date_str)

    if positions is None:
        print(f"\n⚠ No data available for {date_str}")
        print("Run: npm run generate:ephemeris")
        return

    print("\n" + "=" * 70)
    print("CURRENT PLANETARY POSITIONS")
    print("=" * 70)
    print()

    # Display planets in order
    for planet_name in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars',
                        'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']:
        planet = positions['planets'][planet_name]
        rx = " ℞" if planet['retrograde'] else ""

        # Add emoji for personal planets
        emoji = {
            'Sun': '☉',
            'Moon': '☽',
            'Mercury': '☿',
            'Venus': '♀',
            'Mars': '♂',
            'Jupiter': '♃',
            'Saturn': '♄',
            'Uranus': '♅',
            'Neptune': '♆',
            'Pluto': '♇'
        }.get(planet_name, '')

        print(f"{emoji} {planet_name:10} {planet['sign']:12} {planet['degree_in_sign']:6.2f}°{rx}")

    # Get moon phase
    recent_phase, next_phase = get_current_moon_phase(date_str)

    if recent_phase:
        print("\n" + "=" * 70)
        print("MOON PHASE")
        print("=" * 70)
        print()

        phase_date = datetime.fromisoformat(recent_phase['date'].replace('Z', '+00:00'))
        days_since = (today - phase_date).days

        print(f"Most Recent: {format_phase_name(recent_phase['phase'])}")
        print(f"Date: {phase_date.strftime('%B %d, %Y at %H:%M UTC')}")
        print(f"Days ago: {days_since}")
        print(f"Moon was in: {recent_phase['moon_sign']} {recent_phase['moon_degree']:.2f}°")

        if next_phase:
            next_date = datetime.fromisoformat(next_phase['date'].replace('Z', '+00:00'))
            days_until = (next_date - today).days

            print(f"\nNext Phase: {format_phase_name(next_phase['phase'])}")
            print(f"Date: {next_date.strftime('%B %d, %Y at %H:%M UTC')}")
            print(f"Days until: {days_until}")
            print(f"Moon will be in: {next_phase['moon_sign']} {next_phase['moon_degree']:.2f}°")

    # Show current moon position
    moon = positions['planets']['Moon']
    print("\n" + "=" * 70)
    print("CURRENT MOON")
    print("=" * 70)
    print(f"\nMoon is currently in: {moon['sign']} {moon['degree_in_sign']:.2f}°")
    print(f"Moon phase cycle: ~29.5 days")

    # Calculate approximate moon phase percentage
    if recent_phase and next_phase:
        total_cycle = (datetime.fromisoformat(next_phase['date'].replace('Z', '+00:00')) -
                      datetime.fromisoformat(recent_phase['date'].replace('Z', '+00:00'))).total_seconds()
        elapsed = (today - datetime.fromisoformat(recent_phase['date'].replace('Z', '+00:00'))).total_seconds()

        if total_cycle > 0:
            phase_progress = (elapsed / total_cycle) * 100
            print(f"Progress to next phase: {phase_progress:.1f}%")

    # Check for retrograde planets
    retrogrades = [name for name, data in positions['planets'].items() if data['retrograde']]

    if retrogrades:
        print("\n" + "=" * 70)
        print("RETROGRADE PLANETS")
        print("=" * 70)
        print()
        for planet in retrogrades:
            planet_data = positions['planets'][planet]
            print(f"℞ {planet} is retrograde in {planet_data['sign']} {planet_data['degree_in_sign']:.2f}°")

    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
