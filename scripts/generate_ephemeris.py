#!/usr/bin/env python3
"""
Main orchestrator script for generating ephemeris data.

Usage:
    python3 generate_ephemeris.py --all                    # Generate all data types for 2025-2026
    python3 generate_ephemeris.py --type positions         # Generate only daily positions
    python3 generate_ephemeris.py --year 2025 --type moon  # Generate moon phases for 2025
"""

import argparse
import sys
import os
from datetime import datetime, timezone

# Add scripts directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from lib.planetary_positions import generate_year_positions
from lib.moon_phases import generate_year_moon_phases
from lib.aspects import generate_year_aspects
from lib.ingresses import generate_year_ingresses
from lib.retrogrades import generate_year_retrogrades
from utils.formatters import save_json, format_datetime_iso


def generate_major_transits(year: int, output_dir: str = '../data/major-transits'):
    """
    Generate combined major transits file (aspects + ingresses).

    Args:
        year: Year to generate for
        output_dir: Output directory
    """
    import swisseph as swe

    print(f"\n{'='*60}")
    print(f"GENERATING MAJOR TRANSITS FOR {year}")
    print(f"{'='*60}")

    # Generate aspects and ingresses
    aspects = generate_year_aspects(year, output_dir)
    ingresses = generate_year_ingresses(year, output_dir)

    # Combine and sort by date
    all_transits = aspects + ingresses
    all_transits.sort(key=lambda x: x['julian_day'])

    # Separate back into aspects and ingresses for output
    aspects_output = [t for t in all_transits if t['type'] == 'aspect']
    ingresses_output = [t for t in all_transits if t['type'] == 'ingress']

    # Create output structure
    output = {
        'metadata': {
            'year': year,
            'generated_at': format_datetime_iso(datetime.now(timezone.utc)),
            'ephemeris_version': f'Swiss Ephemeris {swe.version}',
            'aspects_tracked': 'Outer planets (Jupiter-Pluto) and Sun to outer planets'
        },
        'aspects': aspects_output,
        'ingresses': ingresses_output
    }

    # Save to file
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{year}.json")
    save_json(output, output_file)

    print(f"\nCombined major transits saved to {output_file}")
    print(f"  Total aspects: {len(aspects_output)}")
    print(f"  Total ingresses: {len(ingresses_output)}")


def generate_all_data(years: list[int]):
    """
    Generate all ephemeris data types for specified years.

    Args:
        years: List of years to generate data for
    """
    print(f"\n{'#'*60}")
    print(f"# CELESTIAL TRANSIT DATA GENERATION")
    print(f"# Years: {', '.join(map(str, years))}")
    print(f"# Started: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"{'#'*60}\n")

    for year in years:
        print(f"\n{'*'*60}")
        print(f"* PROCESSING YEAR {year}")
        print(f"{'*'*60}\n")

        # 1. Daily Positions
        print(f"\n{'='*60}")
        print(f"GENERATING DAILY POSITIONS FOR {year}")
        print(f"{'='*60}")
        generate_year_positions(year)

        # 2. Moon Phases
        print(f"\n{'='*60}")
        print(f"GENERATING MOON PHASES FOR {year}")
        print(f"{'='*60}")
        generate_year_moon_phases(year)

        # 3. Major Transits (Aspects + Ingresses)
        generate_major_transits(year)

        # 4. Retrograde Periods
        print(f"\n{'='*60}")
        print(f"GENERATING RETROGRADE PERIODS FOR {year}")
        print(f"{'='*60}")
        generate_year_retrogrades(year)

        print(f"\n{'*'*60}")
        print(f"* COMPLETED YEAR {year}")
        print(f"{'*'*60}\n")

    print(f"\n{'#'*60}")
    print(f"# GENERATION COMPLETE!")
    print(f"# Finished: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"{'#'*60}\n")


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description='Generate ephemeris data for astrological applications',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Generate all data for 2025-2026 (default):
    python3 generate_ephemeris.py --all

  Generate only daily positions for 2025-2026:
    python3 generate_ephemeris.py --type positions

  Generate moon phases for specific year:
    python3 generate_ephemeris.py --year 2025 --type moon-phases

  Generate major transits for 2027:
    python3 generate_ephemeris.py --year 2027 --type major-transits
        """
    )

    parser.add_argument(
        '--year',
        type=int,
        nargs='+',
        default=[2025, 2026],
        help='Year(s) to generate data for (default: 2025 2026)'
    )

    parser.add_argument(
        '--type',
        choices=['positions', 'moon-phases', 'major-transits', 'retrogrades', 'all'],
        default='all',
        help='Type of data to generate (default: all)'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Generate all data types (same as --type all)'
    )

    args = parser.parse_args()

    # Normalize years to list
    if isinstance(args.year, int):
        years = [args.year]
    else:
        years = args.year

    # Determine data type
    data_type = 'all' if args.all else args.type

    print(f"\nConfiguration:")
    print(f"  Years: {years}")
    print(f"  Data type: {data_type}\n")

    try:
        if data_type == 'all':
            generate_all_data(years)
        else:
            for year in years:
                print(f"\nGenerating {data_type} for {year}...\n")

                if data_type == 'positions':
                    generate_year_positions(year)
                elif data_type == 'moon-phases':
                    generate_year_moon_phases(year)
                elif data_type == 'major-transits':
                    generate_major_transits(year)
                elif data_type == 'retrogrades':
                    generate_year_retrogrades(year)

        print("\n✓ Generation completed successfully!\n")

    except Exception as e:
        print(f"\n✗ Error during generation: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
