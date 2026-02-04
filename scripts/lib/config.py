"""
Configuration constants for ephemeris calculations.
"""

import os
import swisseph as swe

# Set ephemeris path to include local directory for asteroid files
_ephe_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ephe')
if os.path.exists(_ephe_path):
    swe.set_ephe_path(_ephe_path)

# Swiss Ephemeris planet constants
# These map to pyswisseph.SUN, pyswisseph.MOON, etc.
PLANETS = {
    'Sun': {'id': 0, 'name': 'Sun'},
    'Moon': {'id': 1, 'name': 'Moon'},
    'Mercury': {'id': 2, 'name': 'Mercury'},
    'Venus': {'id': 3, 'name': 'Venus'},
    'Mars': {'id': 4, 'name': 'Mars'},
    'Jupiter': {'id': 5, 'name': 'Jupiter'},
    'Saturn': {'id': 6, 'name': 'Saturn'},
    'Uranus': {'id': 7, 'name': 'Uranus'},
    'Neptune': {'id': 8, 'name': 'Neptune'},
    'Pluto': {'id': 9, 'name': 'Pluto'},
    'TrueNode': {'id': 11, 'name': 'North Node'},  # True Lunar Node
    'Chiron': {'id': 15, 'name': 'Chiron'}
}

# Aspect definitions with orbs
ASPECTS = {
    'conjunction': {
        'angle': 0,
        'orb': 8,
        'symbol': '☌',
        'harmonic': True
    },
    'sextile': {
        'angle': 60,
        'orb': 4,
        'symbol': '⚹',
        'harmonic': True
    },
    'square': {
        'angle': 90,
        'orb': 6,
        'symbol': '□',
        'harmonic': False
    },
    'trine': {
        'angle': 120,
        'orb': 6,
        'symbol': '△',
        'harmonic': True
    },
    'opposition': {
        'angle': 180,
        'orb': 8,
        'symbol': '☍',
        'harmonic': False
    }
}

# Zodiac signs (tropical)
ZODIAC_SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagitarius",
    "Capricorn",
    "Aquarius",
    "Pisces"
]

# Swiss Ephemeris calculation flags
# SEFLG_SWIEPH = 2 (use Swiss Ephemeris)
# SEFLG_SPEED = 256 (calculate speed)
SWEPH_FLAGS = 2 | 256  # Tropical zodiac, geocentric, with speed

# Outer planets for major transit tracking (slower-moving planets)
OUTER_PLANETS = ['Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']

# Inner planets to track for conjunctions with outer planets
INNER_PLANETS_FOR_CONJUNCTIONS = ['Venus', 'Mars']

# Planets to track for retrograde periods
RETROGRADE_PLANETS = ['Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Chiron']

# Planets to track for ingresses (sign changes)
INGRESS_PLANETS = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Chiron', 'TrueNode']

# Moon phase definitions (Sun-Moon angle)
MOON_PHASES = {
    'new': 0,
    'first_quarter': 90,
    'full': 180,
    'last_quarter': 270
}
