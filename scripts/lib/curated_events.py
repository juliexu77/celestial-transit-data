"""
Generate curated annual event files consolidating the most important astrological events.

Pulls from existing generated data and filters to events relevant for general audiences.
"""

import os
import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from utils.formatters import format_datetime_iso


# Planets to include for ingresses (slow-moving, significant sign changes)
INGRESS_PLANETS = ['Neptune', 'Uranus', 'Saturn', 'Jupiter', 'Chiron', 'TrueNode']

# Rare conjunction pairs (occur every 12+ years)
RARE_CONJUNCTIONS = [
    ('Saturn', 'Neptune'),
    ('Saturn', 'Uranus'),
    ('Saturn', 'Pluto'),
    ('Jupiter', 'Saturn'),
    ('Jupiter', 'Uranus'),
    ('Jupiter', 'Neptune'),
    ('Jupiter', 'Pluto'),
    ('Uranus', 'Neptune'),
    ('Uranus', 'Pluto'),
    ('Neptune', 'Pluto'),
    # Include Venus-Jupiter as it's visually spectacular and culturally significant
    ('Venus', 'Jupiter'),
    ('Mars', 'Neptune'),
]

# Conjunction frequencies and importance
CONJUNCTION_METADATA = {
    ('Saturn', 'Neptune'): {
        'frequency': 'Every ~36 years',
        'importance': 'generational',
        'themes': ['dissolution of structures', 'spiritual awakening', 'collective dreams', 'institutional reform']
    },
    ('Saturn', 'Uranus'): {
        'frequency': 'Every ~45 years',
        'importance': 'generational',
        'themes': ['revolution vs tradition', 'systemic change', 'technological disruption', 'liberation']
    },
    ('Saturn', 'Pluto'): {
        'frequency': 'Every ~33-38 years',
        'importance': 'generational',
        'themes': ['power structures', 'transformation', 'endings and beginnings', 'karmic reckoning']
    },
    ('Jupiter', 'Saturn'): {
        'frequency': 'Every ~20 years',
        'importance': 'major',
        'themes': ['new era', 'social cycles', 'expansion meets contraction', 'economic shifts']
    },
    ('Jupiter', 'Uranus'): {
        'frequency': 'Every ~14 years',
        'importance': 'major',
        'themes': ['breakthrough', 'innovation', 'sudden expansion', 'freedom', 'technological leaps']
    },
    ('Jupiter', 'Neptune'): {
        'frequency': 'Every ~13 years',
        'importance': 'major',
        'themes': ['spiritual expansion', 'idealism', 'creativity', 'compassion', 'dreams realized']
    },
    ('Jupiter', 'Pluto'): {
        'frequency': 'Every ~13 years',
        'importance': 'major',
        'themes': ['power expansion', 'transformation', 'wealth cycles', 'truth revealed']
    },
    ('Uranus', 'Neptune'): {
        'frequency': 'Every ~171 years',
        'importance': 'generational',
        'themes': ['cultural renaissance', 'consciousness shift', 'collective awakening']
    },
    ('Uranus', 'Pluto'): {
        'frequency': 'Every ~127 years',
        'importance': 'generational',
        'themes': ['revolutionary transformation', 'power to the people', 'radical change']
    },
    ('Neptune', 'Pluto'): {
        'frequency': 'Every ~492 years',
        'importance': 'generational',
        'themes': ['civilization shifts', 'spiritual transformation', 'collective unconscious']
    },
    ('Venus', 'Jupiter'): {
        'frequency': 'Every ~1 year',
        'importance': 'moderate',
        'themes': ['love', 'abundance', 'beauty', 'harmony', 'good fortune']
    },
    ('Mars', 'Neptune'): {
        'frequency': 'Every ~2 years',
        'importance': 'moderate',
        'themes': ['inspired action', 'spiritual warrior', 'imagination', 'creative drive']
    },
}

# Ingress importance and themes
INGRESS_METADATA = {
    'Neptune': {
        'importance': 'generational',
        'frequency': 'Every ~14 years per sign',
        'themes': ['collective dreams', 'spirituality', 'illusion', 'compassion', 'artistic movements']
    },
    'Uranus': {
        'importance': 'generational',
        'frequency': 'Every ~7 years per sign',
        'themes': ['innovation', 'revolution', 'technology', 'awakening', 'disruption']
    },
    'Saturn': {
        'importance': 'major',
        'frequency': 'Every ~2.5 years per sign',
        'themes': ['responsibility', 'structure', 'lessons', 'maturity', 'discipline']
    },
    'Jupiter': {
        'importance': 'major',
        'frequency': 'Every ~1 year per sign',
        'themes': ['expansion', 'growth', 'luck', 'wisdom', 'opportunity']
    },
    'Chiron': {
        'importance': 'major',
        'frequency': 'Every ~4-8 years per sign (varies)',
        'themes': ['healing', 'wounds', 'teaching', 'integration', 'wisdom through suffering']
    },
    'TrueNode': {
        'importance': 'major',
        'frequency': 'Every ~18 months per sign',
        'themes': ['collective destiny', 'karmic direction', 'soul purpose', 'evolutionary path']
    },
}


def load_json_file(filepath: str) -> Optional[Dict]:
    """Load a JSON file if it exists."""
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return None


def extract_cardinal_moon_phases(moon_data: Dict) -> List[Dict[str, Any]]:
    """
    Extract cardinal moon phases (new, first quarter, full, last quarter).

    Args:
        moon_data: Raw moon phases data from JSON

    Returns:
        List of moon phase events in curated format
    """
    curated_phases = []
    cardinal_phases = ['new', 'first_quarter', 'full', 'last_quarter']

    for phase in moon_data.get('phases', []):
        if phase.get('phase') in cardinal_phases:
            curated_phases.append({
                'date': phase['date'][:10],  # YYYY-MM-DD
                'phase': phase['phase'],
                'sign': phase['moon_sign'],
                'degree': phase['moon_degree']
            })

    return curated_phases


def extract_eclipses(eclipse_data: Dict) -> List[Dict[str, Any]]:
    """
    Extract eclipse data in curated format.

    Args:
        eclipse_data: Raw eclipse data from JSON

    Returns:
        List of eclipse events in curated format
    """
    curated_eclipses = []

    for eclipse in eclipse_data.get('eclipses', []):
        curated_eclipses.append({
            'date': eclipse['date'][:10],
            'type': eclipse['type'],
            'eclipse_type': eclipse['eclipse_type'],
            'sign': eclipse['sign'],
            'degree': eclipse['degree'],
            'description': eclipse['description'],
            'visibility': eclipse['visibility']
        })

    return curated_eclipses


def extract_retrogrades(retro_data: Dict) -> List[Dict[str, Any]]:
    """
    Extract retrograde data in curated format.

    Args:
        retro_data: Raw retrograde data from JSON

    Returns:
        List of retrograde events in curated format
    """
    curated_retros = []

    for retro in retro_data.get('retrogrades', []):
        station_rx = retro['station_retrograde']
        station_direct = retro['station_direct']

        curated_retro = {
            'planet': retro['planet'],
            'station_retrograde': station_rx['date'][:10],
            'station_direct': station_direct['date'][:10],
            'sign_at_start': station_rx['sign'],
            'degree_at_start': station_rx['degree'],
        }

        # Add shadow periods if available
        if 'pre_retrograde_shadow_start' in retro:
            curated_retro['shadow_start'] = retro['pre_retrograde_shadow_start'][:10]
        if 'post_retrograde_shadow_end' in retro:
            curated_retro['shadow_end'] = retro['post_retrograde_shadow_end'][:10]

        curated_retros.append(curated_retro)

    return curated_retros


def is_rare_conjunction(planet1: str, planet2: str) -> bool:
    """Check if a conjunction pair is considered rare."""
    pair = tuple(sorted([planet1, planet2]))
    return any(tuple(sorted(p)) == pair for p in RARE_CONJUNCTIONS)


def get_conjunction_metadata(planet1: str, planet2: str) -> Dict[str, Any]:
    """Get metadata for a conjunction pair."""
    pair = tuple(sorted([planet1, planet2]))
    for key, meta in CONJUNCTION_METADATA.items():
        if tuple(sorted(key)) == pair:
            return meta
    return {
        'frequency': 'Unknown',
        'importance': 'moderate',
        'themes': []
    }


def extract_major_events(transit_data: Dict) -> List[Dict[str, Any]]:
    """
    Extract major events (selected ingresses and rare conjunctions).

    Args:
        transit_data: Raw major transits data from JSON

    Returns:
        List of major events in curated format
    """
    major_events = []

    # Process ingresses
    for ingress in transit_data.get('ingresses', []):
        planet = ingress.get('planet')
        if planet in INGRESS_PLANETS:
            meta = INGRESS_METADATA.get(planet, {})

            # Use friendly name for display
            display_name = 'North Node' if planet == 'TrueNode' else planet
            event_type = 'node_axis_shift' if planet == 'TrueNode' else 'planetary_ingress'

            event = {
                'date': ingress['date'][:10],
                'type': event_type,
                'planets': [display_name],
                'from_sign': ingress.get('from_sign'),
                'to_sign': ingress.get('to_sign'),
                'sign': ingress.get('to_sign'),
                'degree': ingress.get('degree', 0),
                'title': f"{display_name} enters {ingress.get('to_sign')}",
                'description': f"{display_name} moves into {ingress.get('to_sign')}, beginning a new phase of {meta.get('themes', ['transformation'])[0] if meta.get('themes') else 'transformation'}",
                'frequency': meta.get('frequency', 'Varies'),
                'importance': meta.get('importance', 'major'),
                'themes': meta.get('themes', [])
            }
            major_events.append(event)

    # Process conjunctions (only rare ones)
    for aspect in transit_data.get('aspects', []):
        if aspect.get('aspect') == 'conjunction':
            planet1 = aspect.get('planet1')
            planet2 = aspect.get('planet2')

            if is_rare_conjunction(planet1, planet2):
                meta = get_conjunction_metadata(planet1, planet2)
                sign = aspect.get('planet1_position', {}).get('sign', 'Unknown')
                degree = aspect.get('planet1_position', {}).get('degree', 0)

                event = {
                    'date': aspect['date'][:10],
                    'type': 'conjunction',
                    'planets': [planet1, planet2],
                    'from_sign': None,
                    'to_sign': None,
                    'sign': sign,
                    'degree': degree,
                    'title': f"{planet1}-{planet2} Conjunction",
                    'description': f"{planet1} and {planet2} align in {sign}, marking a significant cosmic event",
                    'frequency': meta.get('frequency', 'Rare'),
                    'importance': meta.get('importance', 'major'),
                    'themes': meta.get('themes', [])
                }
                major_events.append(event)

    # Sort by date
    major_events.sort(key=lambda x: x['date'])

    return major_events


def generate_curated_year(year: int, data_dir: str = '../data', output_dir: str = '../data/curated') -> Dict[str, Any]:
    """
    Generate curated annual event file for a given year.

    Args:
        year: Year to generate for
        data_dir: Base data directory
        output_dir: Output directory for curated files

    Returns:
        Curated data structure
    """
    print(f"Generating curated events for {year}...")

    # Load source data
    moon_data = load_json_file(os.path.join(data_dir, 'moon-phases', f'{year}.json'))
    eclipse_data = load_json_file(os.path.join(data_dir, 'eclipses', f'{year}.json'))
    retro_data = load_json_file(os.path.join(data_dir, 'retrogrades', f'{year}.json'))
    transit_data = load_json_file(os.path.join(data_dir, 'major-transits', f'{year}.json'))

    # Extract curated data from each source
    moon_phases = extract_cardinal_moon_phases(moon_data) if moon_data else []
    eclipses = extract_eclipses(eclipse_data) if eclipse_data else []
    retrogrades = extract_retrogrades(retro_data) if retro_data else []
    major_events = extract_major_events(transit_data) if transit_data else []

    print(f"  Moon phases: {len(moon_phases)}")
    print(f"  Eclipses: {len(eclipses)}")
    print(f"  Retrogrades: {len(retrogrades)}")
    print(f"  Major events: {len(major_events)}")

    # Create output structure
    curated = {
        'metadata': {
            'year': year,
            'generated_at': format_datetime_iso(datetime.now(timezone.utc)),
            'description': 'Curated astrological events for general audiences',
            'sources': {
                'moon_phases': f'moon-phases/{year}.json',
                'eclipses': f'eclipses/{year}.json',
                'retrogrades': f'retrogrades/{year}.json',
                'major_transits': f'major-transits/{year}.json'
            }
        },
        'moon_phases': moon_phases,
        'eclipses': eclipses,
        'retrogrades': retrogrades,
        'major_events': major_events
    }

    # Save to file
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'{year}.json')

    with open(output_file, 'w') as f:
        json.dump(curated, f, indent=2)

    print(f"  Saved to {output_file}")

    return curated


def generate_curated_years(years: List[int], data_dir: str = '../data', output_dir: str = '../data/curated') -> None:
    """
    Generate curated annual event files for multiple years.

    Args:
        years: List of years to generate
        data_dir: Base data directory
        output_dir: Output directory for curated files
    """
    print(f"\n{'='*60}")
    print(f"GENERATING CURATED EVENTS")
    print(f"Years: {', '.join(map(str, years))}")
    print(f"{'='*60}\n")

    for year in years:
        generate_curated_year(year, data_dir, output_dir)
        print()

    print(f"{'='*60}")
    print(f"CURATED GENERATION COMPLETE!")
    print(f"{'='*60}\n")
