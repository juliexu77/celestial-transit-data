# JSON Schema Documentation

Complete reference for all ephemeris data formats with TypeScript type definitions and examples.

## Table of Contents

1. [Daily Planetary Positions](#daily-planetary-positions)
2. [Moon Phases](#moon-phases)
3. [Major Transits](#major-transits)
4. [Retrograde Periods](#retrograde-periods)
5. [TypeScript Type Definitions](#typescript-type-definitions)
6. [Usage Examples](#usage-examples)

---

## Daily Planetary Positions

**Location**: `/data/daily-positions/YYYY-MM.json`

Provides positions for all 10 planets at midnight UTC each day of the month.

### Schema

```json
{
  "metadata": {
    "month": "2025-01",
    "generated_at": "2025-01-01T00:00:00Z",
    "ephemeris_version": "Swiss Ephemeris 2.10.03",
    "coordinate_system": "tropical zodiac, geocentric",
    "precision": "6 decimal places (~0.0001 degree)"
  },
  "positions": [
    {
      "date": "2025-01-01",
      "time": "00:00:00Z",
      "julian_day": 2460676.5,
      "planets": {
        "Sun": {
          "longitude": 280.123456,
          "latitude": -0.000182,
          "distance_au": 0.983353,
          "speed": 1.019646,
          "sign": "Capricorn",
          "degree_in_sign": 10.123456,
          "retrograde": false
        }
        // ... Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto
      }
    }
    // ... one entry per day
  ]
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `date` | string | Date in YYYY-MM-DD format |
| `time` | string | Always "00:00:00Z" (midnight UTC) |
| `julian_day` | number | Julian Day number for astronomical calculations |
| `longitude` | number | Ecliptic longitude in degrees (0-360) |
| `latitude` | number | Ecliptic latitude in degrees |
| `distance_au` | number | Distance from Earth in Astronomical Units |
| `speed` | number | Longitudinal speed in degrees/day (negative = retrograde) |
| `sign` | string | Tropical zodiac sign name |
| `degree_in_sign` | number | Degrees within the sign (0-30) |
| `retrograde` | boolean | True if planet is in retrograde motion |

### Notes

- All times are midnight UTC
- Longitude 0° = 0° Aries (Spring Equinox)
- Each sign spans 30°: Aries (0-30), Taurus (30-60), etc.
- Sun and Moon never go retrograde

---

## Moon Phases

**Location**: `/data/moon-phases/YYYY.json`

Exact times of all lunar phases for the year.

### Schema

```json
{
  "metadata": {
    "year": 2025,
    "generated_at": "2025-01-01T00:00:00Z",
    "total_phases": 49,
    "ephemeris_version": "Swiss Ephemeris 2.10.03"
  },
  "phases": [
    {
      "phase": "new",
      "date": "2025-01-06T18:23:47Z",
      "julian_day": 2460682.266412,
      "sun_longitude": 285.934567,
      "moon_longitude": 285.934589,
      "sun_sign": "Capricorn",
      "moon_sign": "Capricorn",
      "sun_degree": 15.934567,
      "moon_degree": 15.934589,
      "exactness_degrees": 0.000022
    }
    // ... ~49 phases per year
  ]
}
```

### Phase Types

| Phase | Sun-Moon Angle | Meaning |
|-------|----------------|---------|
| `new` | 0° | Conjunction - Moon between Earth and Sun |
| `first_quarter` | 90° | Waxing square - Half moon waxing |
| `full` | 180° | Opposition - Earth between Sun and Moon |
| `last_quarter` | 270° | Waning square - Half moon waning |

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `phase` | string | One of: "new", "first_quarter", "full", "last_quarter" |
| `date` | string | Exact time of phase in ISO 8601 UTC |
| `sun_longitude` | number | Sun's ecliptic longitude at phase time |
| `moon_longitude` | number | Moon's ecliptic longitude at phase time |
| `exactness_degrees` | number | How close to perfect alignment (ideally <0.01°) |

### Notes

- Phases calculated using binary search to minute precision
- Approximately 12-13 of each phase type per year
- New Moon = same sign; Full Moon = opposite signs (usually)

---

## Major Transits

**Location**: `/data/major-transits/YYYY.json`

Significant planetary aspects and sign ingresses.

### Schema

```json
{
  "metadata": {
    "year": 2025,
    "generated_at": "2025-01-01T00:00:00Z",
    "ephemeris_version": "Swiss Ephemeris 2.10.03",
    "aspects_tracked": "Outer planets (Jupiter-Pluto)"
  },
  "aspects": [
    {
      "type": "aspect",
      "aspect": "trine",
      "symbol": "△",
      "planet1": "Jupiter",
      "planet2": "Neptune",
      "date": "2025-03-15T14:32:18Z",
      "julian_day": 2460750.106181,
      "planet1_position": {
        "longitude": 127.345678,
        "sign": "Leo",
        "degree": 7.345678
      },
      "planet2_position": {
        "longitude": 7.345689,
        "sign": "Aries",
        "degree": 7.345689
      },
      "exactness": 0.000011,
      "orb_used": 6.0
    }
  ],
  "ingresses": [
    {
      "type": "ingress",
      "planet": "Mars",
      "date": "2025-02-14T09:47:23Z",
      "julian_day": 2460720.907674,
      "from_sign": "Capricorn",
      "to_sign": "Aquarius",
      "exact_degree": 0.000003
    }
  ]
}
```

### Aspect Types

| Aspect | Angle | Orb | Symbol | Harmonic |
|--------|-------|-----|--------|----------|
| Conjunction | 0° | ±8° | ☌ | Yes |
| Sextile | 60° | ±4° | ⚹ | Yes |
| Square | 90° | ±6° | □ | No |
| Trine | 120° | ±6° | △ | Yes |
| Opposition | 180° | ±8° | ☍ | No |

### Field Descriptions

#### Aspects

| Field | Type | Description |
|-------|------|-------------|
| `aspect` | string | Name of aspect (conjunction, sextile, etc.) |
| `symbol` | string | Unicode symbol for aspect |
| `planet1/2_position` | object | Position data for each planet |
| `exactness` | number | Deviation from perfect aspect angle |
| `orb_used` | number | Maximum orb allowed for this aspect |

#### Ingresses

| Field | Type | Description |
|-------|------|-------------|
| `planet` | string | Planet changing signs |
| `from_sign` | string | Previous zodiac sign |
| `to_sign` | string | New zodiac sign |
| `exact_degree` | number | Precision of crossing (should be near 0°) |

### Notes

- Only outer planets tracked for aspects (Jupiter-Pluto)
- All planets tracked for ingresses
- Aspects found when planets enter orb of exact angle

---

## Retrograde Periods

**Location**: `/data/retrogrades/YYYY.json`

Station retrograde and direct times for all planets.

### Schema

```json
{
  "metadata": {
    "year": 2025,
    "generated_at": "2025-01-01T00:00:00Z",
    "planets_tracked": ["Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"],
    "ephemeris_version": "Swiss Ephemeris 2.10.03"
  },
  "retrogrades": [
    {
      "planet": "Mercury",
      "station_retrograde": {
        "date": "2025-04-02T03:14:26Z",
        "julian_day": 2460797.634028,
        "longitude": 15.678901,
        "sign": "Aries",
        "degree": 15.678901
      },
      "station_direct": {
        "date": "2025-04-25T18:42:11Z",
        "julian_day": 2460821.279051,
        "longitude": 5.432109,
        "sign": "Aries",
        "degree": 5.432109
      },
      "duration_days": 23.645023,
      "pre_retrograde_shadow_start": "2025-03-15T00:00:00Z",
      "post_retrograde_shadow_end": "2025-05-10T00:00:00Z"
    }
  ]
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `planet` | string | Planet name |
| `station_retrograde` | object | When planet appears to stop and reverse |
| `station_direct` | object | When planet resumes forward motion |
| `duration_days` | number | Days between stations |
| `pre_retrograde_shadow_start` | string | When planet first reaches station direct degree |
| `post_retrograde_shadow_end` | string | When planet returns to station Rx degree |

### Shadow Periods

- **Mercury**: ±15 days
- **Venus/Mars**: ±20 days
- **Outer planets**: Not included (shadow period is very long)

### Notes

- Retrograde = planet's apparent backward motion in sky
- Caused by Earth's orbital motion relative to other planets
- Stations are when planet speed crosses 0°/day
- Sun and Moon never retrograde

---

## TypeScript Type Definitions

```typescript
// Daily Positions
interface DailyPositionsData {
  metadata: {
    month: string;
    generated_at: string;
    ephemeris_version: string;
    coordinate_system: string;
    precision: string;
  };
  positions: DailyPosition[];
}

interface DailyPosition {
  date: string;
  time: string;
  julian_day: number;
  planets: {
    [planetName: string]: PlanetPosition;
  };
}

interface PlanetPosition {
  longitude: number;
  latitude: number;
  distance_au: number;
  speed: number;
  sign: string;
  degree_in_sign: number;
  retrograde: boolean;
}

// Moon Phases
interface MoonPhasesData {
  metadata: {
    year: number;
    generated_at: string;
    total_phases: number;
    ephemeris_version: string;
  };
  phases: MoonPhase[];
}

interface MoonPhase {
  phase: 'new' | 'first_quarter' | 'full' | 'last_quarter';
  date: string;
  julian_day: number;
  sun_longitude: number;
  moon_longitude: number;
  sun_sign: string;
  moon_sign: string;
  sun_degree: number;
  moon_degree: number;
  exactness_degrees: number;
}

// Major Transits
interface MajorTransitsData {
  metadata: {
    year: number;
    generated_at: string;
    ephemeris_version: string;
    aspects_tracked: string;
  };
  aspects: Aspect[];
  ingresses: Ingress[];
}

interface Aspect {
  type: 'aspect';
  aspect: 'conjunction' | 'sextile' | 'square' | 'trine' | 'opposition';
  symbol: string;
  planet1: string;
  planet2: string;
  date: string;
  julian_day: number;
  planet1_position: {
    longitude: number;
    sign: string;
    degree: number;
  };
  planet2_position: {
    longitude: number;
    sign: string;
    degree: number;
  };
  exactness: number;
  orb_used: number;
}

interface Ingress {
  type: 'ingress';
  planet: string;
  date: string;
  julian_day: number;
  from_sign: string;
  to_sign: string;
  exact_degree: number;
}

// Retrogrades
interface RetrogradesData {
  metadata: {
    year: number;
    generated_at: string;
    planets_tracked: string[];
    ephemeris_version: string;
  };
  retrogrades: RetrogradePeriod[];
}

interface RetrogradePeriod {
  planet: string;
  station_retrograde: {
    date: string;
    julian_day: number;
    longitude: number;
    sign: string;
    degree: number;
  };
  station_direct: {
    date: string;
    julian_day: number;
    longitude: number;
    sign: string;
    degree: number;
  };
  duration_days: number;
  pre_retrograde_shadow_start?: string;
  post_retrograde_shadow_end?: string;
}
```

---

## Usage Examples

### TypeScript/React

```typescript
import { useState, useEffect } from 'react';

// Fetch daily positions for current month
async function getCurrentPlanetaryPositions() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');

  const response = await fetch(`/data/daily-positions/${year}-${month}.json`);
  const data: DailyPositionsData = await response.json();

  const today = now.toISOString().split('T')[0];
  return data.positions.find(p => p.date === today);
}

// Check if Mercury is retrograde
async function isMercuryRetrograde(date: Date): Promise<boolean> {
  const year = date.getFullYear();
  const response = await fetch(`/data/retrogrades/${year}.json`);
  const data: RetrogradesData = await response.json();

  const mercuryRetrogrades = data.retrogrades.filter(r => r.planet === 'Mercury');

  return mercuryRetrogrades.some(retro => {
    const start = new Date(retro.station_retrograde.date);
    const end = new Date(retro.station_direct.date);
    return date >= start && date <= end;
  });
}

// Get next full moon
async function getNextFullMoon(): Promise<MoonPhase | null> {
  const now = new Date();
  const year = now.getFullYear();

  const response = await fetch(`/data/moon-phases/${year}.json`);
  const data: MoonPhasesData = await response.json();

  const upcoming = data.phases.filter(p =>
    p.phase === 'full' && new Date(p.date) > now
  );

  return upcoming.length > 0 ? upcoming[0] : null;
}

// React component example
function AstroWidget() {
  const [moonPhase, setMoonPhase] = useState<MoonPhase | null>(null);
  const [mercuryRx, setMercuryRx] = useState<boolean>(false);

  useEffect(() => {
    getNextFullMoon().then(setMoonPhase);
    isMercuryRetrograde(new Date()).then(setMercuryRx);
  }, []);

  return (
    <div>
      {mercuryRx && <p>Mercury is retrograde!</p>}
      {moonPhase && (
        <p>Next full moon: {new Date(moonPhase.date).toLocaleDateString()}</p>
      )}
    </div>
  );
}
```

### JavaScript/Node.js

```javascript
const fs = require('fs');

// Load daily positions synchronously
function loadDailyPositions(year, month) {
  const monthStr = `${year}-${String(month).padStart(2, '0')}`;
  const data = JSON.parse(
    fs.readFileSync(`data/daily-positions/${monthStr}.json`, 'utf8')
  );
  return data;
}

// Find all Jupiter-Saturn conjunctions
function findJupiterSaturnConjunctions(year) {
  const data = JSON.parse(
    fs.readFileSync(`data/major-transits/${year}.json`, 'utf8')
  );

  return data.aspects.filter(aspect =>
    aspect.aspect === 'conjunction' &&
    ((aspect.planet1 === 'Jupiter' && aspect.planet2 === 'Saturn') ||
     (aspect.planet1 === 'Saturn' && aspect.planet2 === 'Jupiter'))
  );
}

// Get all planetary positions for a specific date
function getPositionsForDate(dateStr) {
  const [year, month, day] = dateStr.split('-');
  const data = loadDailyPositions(parseInt(year), parseInt(month));
  return data.positions.find(p => p.date === dateStr);
}
```

### Python

```python
import json
from datetime import datetime

# Load moon phases
with open('data/moon-phases/2025.json') as f:
    data = json.load(f)

# Find all new moons
new_moons = [p for p in data['phases'] if p['phase'] == 'new']

for moon in new_moons:
    date = datetime.fromisoformat(moon['date'].replace('Z', '+00:00'))
    print(f"New Moon: {date.strftime('%B %d, %Y at %H:%M UTC')}")
    print(f"  Sun/Moon in {moon['sun_sign']} at {moon['sun_degree']:.2f}°\n")
```

---

## Data Validation

To ensure data integrity:

1. **Check file sizes**: Monthly position files should be ~50-100KB
2. **Verify planet count**: Each daily position should have exactly 10 planets
3. **Check continuity**: Dates should be sequential with no gaps
4. **Validate ranges**:
   - Longitude: 0-360°
   - Latitude: -90 to +90° (planets typically <6°)
   - Speed: Varies by planet (Sun ~1°/day, Moon ~13°/day)
5. **Cross-reference**: Compare with [astro.com ephemeris](https://www.astro.com/swisseph/swepha_e.htm)
