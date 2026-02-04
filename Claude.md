# Celestial Transit Data - Project Context

## Project Overview

This is a comprehensive astrological ephemeris data generation system that calculates and stores high-precision astronomical data as static JSON files. The data serves as the single source of truth for multiple astrological applications (BabyRhythm, Aster, etc.).

**Key Purpose**: Generate accurate planetary positions, moon phases, aspects, and retrograde periods using Swiss Ephemeris, making them easily accessible as static JSON files that any application can fetch.

## Architecture

### Hybrid System
- **Backend**: Python 3.12+ with `pyswisseph` for astronomical calculations (build-time only)
- **Frontend**: React 18 + TypeScript + Vite (optional, for viewing data)
- **Data Storage**: Static JSON files committed to git repository
- **Distribution**: Files can be served statically or fetched directly from repo

### Technology Stack

**Python Data Generation**:
- `pyswisseph` (Swiss Ephemeris bindings) - Arc-second precision astronomical calculations
- `pytz` - Timezone handling
- Modular architecture with separate calculation modules

**Frontend (Optional)**:
- React 18 with TypeScript
- Vite build tooling
- shadcn-ui component library
- Tailwind CSS

**Backend (Optional)**:
- Supabase (PostgreSQL + Edge Functions)
- Existing edge function: `/supabase/functions/natal-chart/index.ts`

## Project Structure

```
celestial-transit-data/
├── scripts/                     # Python data generation system
│   ├── requirements.txt         # pyswisseph>=2.10.3, pytz>=2024.1
│   ├── generate_ephemeris.py    # Main orchestrator (CLI)
│   ├── lib/                     # Calculation modules
│   │   ├── config.py            # Constants (planets, aspects, zodiac)
│   │   ├── planetary_positions.py   # Daily positions calculator
│   │   ├── moon_phases.py       # Moon phase calculations (8 phases)
│   │   ├── aspects.py           # Major aspects between outer planets
│   │   ├── ingresses.py         # Planetary sign changes
│   │   ├── retrogrades.py       # Retrograde period detection
│   │   ├── eclipses.py          # Solar/lunar eclipse calculations
│   │   └── curated_events.py    # Curated annual events aggregator
│   ├── utils/
│   │   ├── julian_date.py       # JD conversions
│   │   ├── formatters.py        # JSON formatting & zodiac helpers
│   │   └── validators.py        # Data validation
│   ├── test_birth_chart.py      # Natal chart calculator (test script)
│   └── current_transits.py      # Display current transits (test script)
│
├── data/                        # Generated JSON files (committed to git)
│   ├── daily-positions/         # 1,320 files (1920-2029, YYYY-MM.json)
│   ├── moon-phases/             # 110 files (1920-2029, YYYY.json)
│   ├── major-transits/          # 110 files (aspects + ingresses)
│   ├── retrogrades/             # 110 files (station Rx/direct times)
│   ├── eclipses/                # 5 files (2025-2029, YYYY.json)
│   └── curated/                 # 4 files (2026-2029, YYYY.json)
│
├── docs/
│   ├── EPHEMERIS_GUIDE.md       # Complete regeneration guide
│   └── JSON_SCHEMAS.md          # Schema docs + TypeScript types
│
├── src/                         # React frontend (optional)
├── supabase/                    # Supabase config (optional)
└── package.json                 # NPM scripts for data generation
```

## Data Coverage

**Historical Range**: 1920-2029 (110 years)
**Active Development**: 2025-2029 (includes 8-phase moon system)
**Total Size**: ~115MB for all 110 years

### Data Types

1. **Daily Planetary Positions** (`/data/daily-positions/YYYY-MM.json`)
   - All 10 planets at midnight UTC each day
   - Includes longitude, latitude, distance, speed, sign, degree, retrograde status
   - **NEW**: Includes `moon_phase` field (8 phases: new, waxing_crescent, first_quarter, waxing_gibbous, full, waning_gibbous, last_quarter, waning_crescent)

2. **Moon Phases** (`/data/moon-phases/YYYY.json`)
   - Exact times of 4 cardinal phases (new, first quarter, full, last quarter)
   - ~49 phases per year
   - Includes Sun/Moon positions at phase time

3. **Major Transits** (`/data/major-transits/YYYY.json`)
   - Aspects between outer planets (Jupiter-Pluto)
   - All planetary ingresses (sign changes)
   - 5 major aspects: conjunction, sextile, square, trine, opposition

4. **Retrograde Periods** (`/data/retrogrades/YYYY.json`)
   - Station retrograde/direct times for all planets
   - Shadow periods for Mercury, Venus, Mars
   - Duration calculations

5. **Eclipses** (`/data/eclipses/YYYY.json`) - NEW
   - All solar and lunar eclipses for 2025-2029
   - Types: total, annular, partial, hybrid, penumbral
   - Includes Saros series, descriptions, visibility info
   - 4-6 eclipses per year

6. **Curated Events** (`/data/curated/YYYY.json`) - NEW
   - Consolidated annual event files for general audiences
   - Aggregates data from moon phases, eclipses, retrogrades, and major transits
   - Filters to most significant events:
     - Cardinal moon phases (new, first quarter, full, last quarter)
     - All eclipses with metadata
     - All retrogrades with shadow periods
     - Selected ingresses (Neptune, Uranus, Saturn, Jupiter, Chiron)
     - Rare conjunctions (12+ year cycles: Saturn-Neptune, Jupiter-Saturn, etc.)
   - Includes themes, importance levels, and frequencies

## Technical Specifications

### Astronomical Reference Frame
- **Zodiac**: Tropical (fixed to seasons, not constellations)
- **Perspective**: Geocentric (Earth-centered)
- **Coordinates**: Ecliptic longitude/latitude
- **Ephemeris**: Swiss Ephemeris 2.10.03 (JPL DE431)
- **Accuracy**: Arc-second precision for modern dates
- **Timezone**: UTC for all timestamps (ISO 8601 format)
- **Precision**: 6 decimal places (0.0001° = 0.36 arcseconds)

### Planets Tracked
Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto

### House System
Placidus (in natal chart calculator)

## Key Files & Their Purposes

### Python Calculation Modules

**`scripts/lib/config.py`**
- Central configuration for planets, aspects, zodiac signs
- Swiss Ephemeris constants and flags
- Phase definitions

**`scripts/lib/planetary_positions.py`**
- Core daily position calculations
- Calculates all 10 planets at midnight UTC
- **Includes moon phase calculation** (8 phases based on Sun-Moon angle)
- Exports monthly JSON files

**`scripts/lib/moon_phases.py`**
- Exact cardinal phase detection (new, first quarter, full, last quarter)
- Binary search for minute-level precision
- **NEW**: `get_moon_phase_name()` - determines 8-phase name from angle
- **NEW**: `get_moon_phase_emoji()` - returns emoji for phase

**`scripts/lib/aspects.py`**
- Detects major aspects between outer planets
- Uses orbs: conjunction/opposition (±8°), square (±6°), trine (±6°), sextile (±4°)
- Linear interpolation for exact times

**`scripts/lib/ingresses.py`**
- Detects planetary sign changes
- Tracks both forward and retrograde motion
- Interpolates exact crossing time

**`scripts/lib/retrogrades.py`**
- Detects when planet speed crosses zero
- Calculates shadow periods
- Station retrograde and direct times

**`scripts/lib/eclipses.py`** - NEW
- Solar eclipse detection using `swe.sol_eclipse_when_glob()`
- Lunar eclipse detection using `swe.lun_eclipse_when()`
- Eclipse types: total, annular, partial, hybrid, penumbral
- Saros series approximation
- Geographic visibility info for solar eclipses
- Human-readable descriptions

**`scripts/lib/curated_events.py`** - NEW
- Aggregates data from multiple sources into curated annual files
- Filters events for general audience relevance
- Rare conjunctions metadata (frequency, importance, themes):
  - Generational: Saturn-Neptune (36yr), Saturn-Pluto (35yr), Uranus-Neptune (171yr)
  - Major: Jupiter-Saturn (20yr), Jupiter-Uranus (14yr), Jupiter-Neptune (13yr)
- Ingress filtering for slow-moving planets only
- Outputs structured JSON with four arrays: moon_phases, eclipses, retrogrades, major_events

### Utility Modules

**`scripts/utils/julian_date.py`**
- `datetime_to_julian_day()` - Convert Python datetime to JD
- `julian_day_to_datetime()` - Convert JD to datetime
- `date_range()` - Generate date ranges

**`scripts/utils/formatters.py`**
- `get_zodiac_sign()` - Convert longitude to sign + degree
- `format_datetime_iso()` - ISO 8601 formatter
- `save_json()` / `load_json()` - JSON file operations
- `round_decimal()` - Precision control

### Main Scripts

**`scripts/generate_ephemeris.py`**
Main orchestrator for data generation. CLI usage:
```bash
python3 generate_ephemeris.py --all                    # All data for 1920-2029
python3 generate_ephemeris.py --year 2025 2026 --all   # Specific years
python3 generate_ephemeris.py --type positions          # Only daily positions
python3 generate_ephemeris.py --type moon-phases        # Only moon phases
python3 generate_ephemeris.py --type eclipses          # Only eclipses
python3 generate_ephemeris.py --type curated           # Only curated events
```

**`scripts/test_birth_chart.py`**
Natal chart calculator for testing. Calculates:
- Sun, Moon, Rising (Ascendant)
- Midheaven (MC)
- 12 house cusps (Placidus system)
- All planetary positions with house placements

**`scripts/current_transits.py`**
Display current transits for today:
- Current planetary positions
- Current moon phase (8-phase system with emoji)
- Recent/next cardinal moon phases
- Retrograde planets

## NPM Scripts

```bash
npm run generate:ephemeris     # Generate all data for 1920-2029
npm run generate:positions     # Daily positions only
npm run generate:moon          # Moon phases only
npm run generate:transits      # Aspects + ingresses
npm run generate:retrogrades   # Retrograde periods only
npm run clean:data             # Remove all generated JSON files
```

## Common Workflows

### Regenerate All Data
```bash
cd scripts
pip install -r requirements.txt
cd ..
npm run generate:ephemeris
```

### Add New Years
```bash
cd scripts
python3 generate_ephemeris.py --year 2030 2031 --all
```

### Test Current Transits
```bash
cd scripts
python3 current_transits.py
```

### Calculate Natal Chart
```bash
cd scripts
# Edit test_birth_chart.py with birth data
python3 test_birth_chart.py
```

### Generate Data in Batches (for many years)
```bash
cd scripts
for start in $(seq 1920 10 2020); do
    end=$((start + 9))
    python3 generate_ephemeris.py --year $(seq $start $end) --all
done
```

## JSON Schema Examples

### Daily Positions
```json
{
  "date": "2026-02-03",
  "time": "00:00:00Z",
  "julian_day": 2460706.5,
  "moon_phase": "waning_gibbous",
  "planets": {
    "Sun": {
      "longitude": 314.15,
      "latitude": 0.0,
      "distance_au": 0.985,
      "speed": 1.02,
      "sign": "Aquarius",
      "degree_in_sign": 14.15,
      "retrograde": false
    }
  }
}
```

### Moon Phase (8 phases)
Phase names returned in `moon_phase` field:
- `new` 🌑
- `waxing_crescent` 🌒
- `first_quarter` 🌓
- `waxing_gibbous` 🌔
- `full` 🌕
- `waning_gibbous` 🌖
- `last_quarter` 🌗
- `waning_crescent` 🌘

Calculation: Based on Sun-Moon angle (0-360°), divided into 8 ranges of 45° each.

### Eclipse
```json
{
  "type": "solar",
  "eclipse_type": "total",
  "date": "2026-08-12T17:45:57Z",
  "sign": "Leo",
  "degree": 20.125401,
  "saros_series": 152,
  "description": "Total Solar Eclipse in Leo - Moon completely blocks the Sun",
  "visibility": "Global visibility varies by location"
}
```

### Curated Event (Major Event)
```json
{
  "date": "2026-01-02",
  "type": "conjunction",
  "planets": ["Saturn", "Neptune"],
  "sign": "Aries",
  "degree": 0.5,
  "title": "Saturn-Neptune Conjunction",
  "description": "Saturn and Neptune align in Aries, marking a significant cosmic event",
  "frequency": "Every ~36 years",
  "importance": "generational",
  "themes": ["dissolution of structures", "spiritual awakening", "collective dreams"]
}
```

## Usage in Consumer Apps

### Fetch Daily Positions
```typescript
const data = await fetch('/data/daily-positions/2026-02.json').then(r => r.json());
const today = data.positions.find(p => p.date === '2026-02-03');
console.log(today.moon_phase); // "waning_gibbous"
```

### Check Mercury Retrograde
```typescript
const retro = await fetch('/data/retrogrades/2026.json').then(r => r.json());
const mercuryRx = retro.retrogrades.filter(r => r.planet === 'Mercury');
// Mercury retrogrades 3 times per year
```

### Get Next Full Moon
```typescript
const phases = await fetch('/data/moon-phases/2026.json').then(r => r.json());
const nextFull = phases.phases.find(p =>
  p.phase === 'full' && new Date(p.date) > new Date()
);
```

### Get Upcoming Eclipses
```typescript
const eclipses = await fetch('/data/eclipses/2026.json').then(r => r.json());
const solarEclipses = eclipses.eclipses.filter(e => e.type === 'solar');
console.log(solarEclipses[0].description); // "Annular Solar Eclipse in Aquarius..."
```

### Get Curated Events for a Year
```typescript
const curated = await fetch('/data/curated/2026.json').then(r => r.json());
// Access different event types
console.log(curated.moon_phases.length);   // 50
console.log(curated.eclipses.length);      // 4
console.log(curated.retrogrades.length);   // 7
console.log(curated.major_events.length);  // 6

// Find generational events
const generational = curated.major_events.filter(e => e.importance === 'generational');
```

## Important Notes

### Moon Phase System Evolution
- **Historical data (1920-2024)**: Only 4 cardinal phases in separate files
- **Current data (2025-2029)**:
  - Cardinal phases still in separate files
  - **8-phase names included in daily positions** as `moon_phase` field
  - Phase name is calculated dynamically based on Sun-Moon angle

### Retrograde Detection
- Based on longitudinal speed crossing zero
- Positive speed = direct motion
- Negative speed = retrograde motion
- Sun and Moon never retrograde

### Aspect Orbs
- Conjunction/Opposition: ±8°
- Square: ±6°
- Trine: ±6°
- Sextile: ±4°

### House Systems
- Daily positions: No houses (just planetary positions)
- Natal chart calculator: Placidus system
- Whole Sign system exists in edge function but not used in Python

## Git Workflow

### What's Committed
✅ All generated JSON data files (~115MB)
✅ Python calculation scripts
✅ Documentation
✅ Frontend code (React/TypeScript)

### What's Ignored
❌ Python cache (`__pycache__/`, `*.pyc`)
❌ Virtual environments (`venv/`, `.venv/`)
❌ Node modules
❌ Build artifacts

## Dependencies

### Python (Required for Data Generation)
- `pyswisseph>=2.10.3` - Swiss Ephemeris calculations
- `pytz>=2024.1` - Timezone handling

### Node.js (Optional, for Frontend)
- React 18
- TypeScript 5.8
- Vite 5.4
- shadcn-ui components
- Tailwind CSS 3.4

### Supabase (Optional)
- Project ID: fhfqzquectklbjwkhrgb
- Edge function: `natal-chart` (TypeScript-based natal chart calculator)
- Database currently empty (no tables)

## Future Enhancements

Potential additions:
- Extended date ranges (1900-2100)
- Additional celestial bodies (Chiron, Ceres, asteroids)
- ~~Solar/Lunar eclipse calculations~~ ✅ Implemented
- ~~Curated events aggregation~~ ✅ Implemented
- House cusps for major cities
- Aspect patterns (grand trines, T-squares)
- Database integration with Supabase
- Node axis tracking (North/South Node sign changes)
- Eclipse path visibility calculations
- Historical eclipse data (1920-2024)

## Troubleshooting

### "ModuleNotFoundError: No module named 'lib'"
Run scripts from `/workspaces/celestial-transit-data/scripts/` directory:
```bash
cd scripts
python3 generate_ephemeris.py --all
```

### Command line argument list too long
Generate in batches of 10 years:
```bash
for start in $(seq 1920 10 2020); do
    python3 generate_ephemeris.py --year $(seq $start $((start+9))) --all
done
```

### Swiss Ephemeris data files missing
pyswisseph automatically downloads required files on first use. Ensure internet connection on first run.

## Testing & Validation

### Verify Data Generation
```bash
cd scripts
python3 -c "
import json
with open('../data/daily-positions/2026-02.json') as f:
    data = json.load(f)
    print('Moon phase:', data['positions'][0].get('moon_phase'))
"
```

### Cross-Validation
Compare sample dates with [astro.com ephemeris](https://www.astro.com/swisseph/swepha_e.htm)

### Expected Values
- Moon phases: ~49 per year (12-13 of each type)
- Mercury retrogrades: 3-4 per year
- Daily positions: Exactly 1 per day (365 or 366)
- Planetary ingresses: ~200-220 per year (varies by planet speeds)

## Contact & Resources

- [Swiss Ephemeris Documentation](https://www.astro.com/swisseph/swisseph.htm)
- [pyswisseph GitHub](https://github.com/astrorigin/pyswisseph)
- [Ephemeris Guide](docs/EPHEMERIS_GUIDE.md)
- [JSON Schemas](docs/JSON_SCHEMAS.md)
