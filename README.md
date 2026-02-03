# Celestial Transit Data

High-precision astrological ephemeris data as static JSON files, calculated using Swiss Ephemeris and ready to consume from any application.

## Overview

This repository provides comprehensive astronomical data for astrological applications:

- **Daily Planetary Positions** - All 10 planets at midnight UTC each day
- **Moon Phases** - Exact times of new moons, full moons, and quarters
- **Major Transits** - Significant aspects between outer planets and sign ingresses
- **Retrograde Periods** - Station retrograde/direct times with shadow periods

All data is pre-calculated and stored as static JSON files for easy consumption by web apps, mobile apps, or any other client.

## Quick Start

### Using the Data

Fetch daily positions for January 2025:
```typescript
const data = await fetch('/data/daily-positions/2025-01.json').then(r => r.json());
const jan1 = data.positions[0];
console.log(`Sun in ${jan1.planets.Sun.sign} at ${jan1.planets.Sun.degree_in_sign}°`);
```

Find next full moon:
```typescript
const phases = await fetch('/data/moon-phases/2025.json').then(r => r.json());
const nextFullMoon = phases.phases.find(p =>
  p.phase === 'full' && new Date(p.date) > new Date()
);
```

Check if Mercury is retrograde:
```typescript
const retro = await fetch('/data/retrogrades/2025.json').then(r => r.json());
const mercuryRx = retro.retrogrades.filter(r => r.planet === 'Mercury');
```

### Regenerating Data

Install Python dependencies:
```bash
cd scripts
pip install -r requirements.txt
```

Generate all ephemeris data for 2025-2026:
```bash
npm run generate:ephemeris
```

Or generate specific data types:
```bash
npm run generate:positions    # Daily positions only
npm run generate:moon          # Moon phases only
npm run generate:transits      # Aspects and ingresses
npm run generate:retrogrades   # Retrograde periods
```

## Data Files

```
data/
├── daily-positions/    # 24 files (YYYY-MM.json)
│   ├── 2025-01.json   # ~50KB each
│   └── ...
├── moon-phases/        # 2 files (YYYY.json)
│   ├── 2025.json      # ~20KB each
│   └── 2026.json
├── major-transits/     # 2 files (YYYY.json)
│   ├── 2025.json      # ~30KB each
│   └── 2026.json
└── retrogrades/        # 2 files (YYYY.json)
    ├── 2025.json      # ~10KB each
    └── 2026.json
```

Total size: ~5MB for 2 years of comprehensive data

## Documentation

- **[Ephemeris Guide](docs/EPHEMERIS_GUIDE.md)** - Complete guide to regenerating and using the data
- **[JSON Schemas](docs/JSON_SCHEMAS.md)** - Detailed schema documentation with TypeScript types and examples

## Technical Specifications

- **Ephemeris**: Swiss Ephemeris 2.10.03 (JPL DE431)
- **Accuracy**: Arc-second precision for modern dates
- **Zodiac**: Tropical (fixed to seasons)
- **Perspective**: Geocentric (Earth-centered)
- **Timezone**: UTC (all timestamps)
- **Precision**: 6 decimal places (0.0001° = 0.36 arcseconds)

### Planets Tracked

Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto

### Aspect Types

- Conjunction (0°, ±8° orb)
- Sextile (60°, ±4° orb)
- Square (90°, ±6° orb)
- Trine (120°, ±6° orb)
- Opposition (180°, ±8° orb)

## Development

### Frontend Development

This repository also includes a React/TypeScript frontend for viewing the ephemeris data.

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### Technology Stack

**Frontend:**
- React 18 with TypeScript
- Vite for build tooling
- shadcn-ui component library
- Tailwind CSS for styling
- Supabase for backend (optional)

**Data Generation:**
- Python 3.12+
- pyswisseph (Swiss Ephemeris bindings)
- pytz (timezone handling)

## Project Structure

```
celestial-transit-data/
├── data/                    # Generated JSON data files
├── docs/                    # Documentation
├── scripts/                 # Python data generation
│   ├── lib/                # Calculation modules
│   ├── utils/              # Helper utilities
│   └── generate_ephemeris.py
├── src/                     # React frontend
├── supabase/               # Supabase configuration
└── package.json            # NPM scripts
```

## Use Cases

This ephemeris data is the single source of truth for:

- **BabyRhythm** - Fertility tracking with lunar cycles
- **Aster** - Birth chart analysis and transits
- **General astrology apps** - Any application needing accurate planetary positions

## Contributing

To add more years:
```bash
cd scripts
python3 generate_ephemeris.py --year 2027 2028 --all
```

To add more celestial bodies, edit `scripts/lib/config.py` and add entries to `PLANETS`.

## License

Data calculated using Swiss Ephemeris, which is licensed under AGPL or commercial license.

## References

- [Swiss Ephemeris](https://www.astro.com/swisseph/swisseph.htm)
- [pyswisseph Documentation](https://astrorigin.com/pyswisseph/)
- [Tropical Zodiac Explanation](https://www.astro.com/faq/fq_fh_owzodiac_e.htm)

---

## Deployment

This project can be deployed through [Lovable](https://lovable.dev) or any static hosting service.

To deploy via Lovable:
1. Open your [Lovable project](https://lovable.dev/projects/REPLACE_WITH_PROJECT_ID)
2. Click Share → Publish

To deploy statically:
```bash
npm run build
# Upload dist/ folder to your hosting service
```

The JSON data files in `/data` will be accessible via HTTP fetch from any deployed frontend.
