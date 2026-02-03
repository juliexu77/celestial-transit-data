# Ephemeris Data Generation Guide

This guide explains how to regenerate and use the astrological ephemeris data in this repository.

## Overview

This repository provides high-precision astronomical data calculated using the Swiss Ephemeris library. The data is pre-computed and stored as static JSON files, making it easy to consume from any application.

## Data Types

The repository contains four types of ephemeris data:

1. **Daily Planetary Positions** - Positions of all 10 planets at midnight UTC each day
2. **Moon Phases** - Exact times of new moons, full moons, and quarter moons
3. **Major Transits** - Significant aspects between outer planets and planetary sign changes
4. **Retrograde Periods** - Station retrograde and direct times for all planets

## Technical Specifications

### Astronomical Reference Frame

- **Zodiac System**: Tropical (fixed to seasons, not constellations)
- **Perspective**: Geocentric (Earth-centered)
- **Coordinate System**: Ecliptic longitude and latitude
- **Ephemeris Source**: Swiss Ephemeris 2.10.03 with JPL DE431
- **Accuracy**: Arc-second precision for modern dates

### Time System

- **Timezone**: UTC (Coordinated Universal Time)
- **Format**: ISO 8601 (e.g., `2025-01-15T14:23:47Z`)
- **Julian Day**: Used internally for calculations, included in output

### Precision

- **Positions**: 6 decimal places (0.0001° = 0.36 arcseconds)
- **Times**: To the second for most events
- **Moon phases**: To the minute using binary search
- **Aspects**: Linear interpolation between daily positions

### Planets Tracked

1. Sun
2. Moon
3. Mercury
4. Venus
5. Mars
6. Jupiter
7. Saturn
8. Uranus
9. Neptune
10. Pluto

## Regenerating Data

### Prerequisites

1. **Python 3.12+** installed on your system
2. **pip** package manager
3. **Swiss Ephemeris data files** (automatically downloaded by pyswisseph)

### Installation

Install Python dependencies:

```bash
cd scripts
pip install -r requirements.txt
```

This will install:
- `pyswisseph` - Swiss Ephemeris bindings
- `pytz` - Timezone handling

### Generating All Data

To generate all ephemeris data for 2025-2026 (default):

```bash
npm run generate:ephemeris
```

Or directly with Python:

```bash
cd scripts
python3 generate_ephemeris.py --all
```

### Generating Specific Data Types

Generate only daily positions:
```bash
npm run generate:positions
```

Generate only moon phases:
```bash
npm run generate:moon
```

Generate only major transits (aspects + ingresses):
```bash
npm run generate:transits
```

Generate only retrograde periods:
```bash
npm run generate:retrogrades
```

### Generating for Custom Years

To generate data for specific years:

```bash
cd scripts
python3 generate_ephemeris.py --year 2027 --type all
python3 generate_ephemeris.py --year 2028 2029 --type moon-phases
```

### Cleaning Generated Data

To remove all generated JSON files:

```bash
npm run clean:data
```

## File Structure

```
data/
├── daily-positions/
│   ├── 2025-01.json    # January 2025
│   ├── 2025-02.json    # February 2025
│   └── ...             # One file per month
├── moon-phases/
│   ├── 2025.json       # All phases for 2025
│   └── 2026.json       # All phases for 2026
├── major-transits/
│   ├── 2025.json       # Aspects + ingresses for 2025
│   └── 2026.json       # Aspects + ingresses for 2026
└── retrogrades/
    ├── 2025.json       # All retrogrades for 2025
    └── 2026.json       # All retrogrades for 2026
```

## Usage Examples

See [JSON_SCHEMAS.md](JSON_SCHEMAS.md) for complete schema documentation and TypeScript examples.

### Fetching Daily Positions

```typescript
const data = await fetch('/data/daily-positions/2025-01.json').then(r => r.json());
const jan1 = data.positions.find(p => p.date === '2025-01-01');
console.log(`Sun: ${jan1.planets.Sun.sign} ${jan1.planets.Sun.degree_in_sign}°`);
```

### Finding Next Full Moon

```typescript
const phases = await fetch('/data/moon-phases/2025.json').then(r => r.json());
const now = new Date();
const nextFullMoon = phases.phases.find(p =>
  p.phase === 'full' && new Date(p.date) > now
);
console.log(`Next full moon: ${nextFullMoon.date}`);
```

### Checking Mercury Retrograde

```typescript
const retro = await fetch('/data/retrogrades/2025.json').then(r => r.json());
const mercuryRetrogrades = retro.retrogrades.filter(r => r.planet === 'Mercury');
console.log(`Mercury retrograde ${mercuryRetrogrades.length} times in 2025`);
```

## Validation

After generation, verify the data:

1. **File count**: Should have 24 monthly position files, 2 moon phase files, etc.
2. **Moon phases**: Should occur approximately every 7.4 days
3. **Mercury retrograde**: Should occur 3-4 times per year
4. **Cross-validation**: Compare sample dates with [astro.com](https://www.astro.com/swisseph/swepha_e.htm)

## Troubleshooting

### Import Errors

If you see `ModuleNotFoundError`:
```bash
cd scripts
pip install -r requirements.txt
```

### Swiss Ephemeris Data Missing

pyswisseph automatically downloads required ephemeris files on first use. If you see errors about missing files, ensure you have internet connection during the first run.

### Memory Issues

Generating all data for multiple years requires ~500MB RAM. If you encounter memory issues:
1. Generate one data type at a time
2. Generate one year at a time

### Incorrect Calculations

If planetary positions seem wrong:
1. Verify your system clock is correct
2. Check that pyswisseph version is 2.10.3+
3. Cross-reference with online ephemeris tools

## Performance

- **Daily positions for 1 year**: ~30 seconds
- **Moon phases for 1 year**: ~20 seconds
- **Major transits for 1 year**: ~40 seconds (many planetary pairs)
- **Retrogrades for 1 year**: ~15 seconds
- **All data for 2025-2026**: ~3-4 minutes total

## Extending the System

### Adding More Years

Simply run the generator with additional years:
```bash
python3 generate_ephemeris.py --year 2027 2028 2029 --all
```

### Adding More Celestial Bodies

Edit `scripts/lib/config.py` and add to `PLANETS`:
```python
PLANETS = {
    # ... existing planets ...
    'Chiron': {'id': 15, 'name': 'Chiron'},  # Centaur
    'Ceres': {'id': 17, 'name': 'Ceres'},    # Asteroid
}
```

Swiss Ephemeris planet IDs:
- 15: Chiron
- 17-19: Ceres, Pallas, Juno
- 10: True Node
- 11: Mean Node

### Adding More Aspect Types

Edit `scripts/lib/config.py`:
```python
ASPECTS = {
    # ... existing aspects ...
    'quintile': {'angle': 72, 'orb': 2, 'symbol': 'Q', 'harmonic': True},
    'biquintile': {'angle': 144, 'orb': 2, 'symbol': 'bQ', 'harmonic': True},
}
```

### Calculating Eclipses

Solar and lunar eclipses require specialized functions. See Swiss Ephemeris documentation for `swe_sol_eclipse_when_glob()` and `swe_lun_eclipse_when()`.

## References

- [Swiss Ephemeris Documentation](https://www.astro.com/swisseph/swisseph.htm)
- [pyswisseph GitHub](https://github.com/astrorigin/pyswisseph)
- [Tropical vs Sidereal Zodiac](https://www.astro.com/faq/fq_fh_owzodiac_e.htm)

## Support

For issues or questions:
- Check [JSON_SCHEMAS.md](JSON_SCHEMAS.md) for data format details
- Review calculation modules in `scripts/lib/`
- Open an issue on GitHub
