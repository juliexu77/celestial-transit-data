const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

const ZODIAC = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"];

const PLANETS: Record<string, { name: string; motion: number; j2000: number }> = {
  sun: { name: "Sun", motion: 0.9856, j2000: 280.46 },
  moon: { name: "Moon", motion: 13.176, j2000: 218.32 },
  mercury: { name: "Mercury", motion: 4.092, j2000: 252.25 },
  venus: { name: "Venus", motion: 1.602, j2000: 181.98 },
  mars: { name: "Mars", motion: 0.524, j2000: 355.45 },
  jupiter: { name: "Jupiter", motion: 0.0831, j2000: 34.40 },
  saturn: { name: "Saturn", motion: 0.0335, j2000: 49.94 },
  uranus: { name: "Uranus", motion: 0.0117, j2000: 313.23 },
  neptune: { name: "Neptune", motion: 0.006, j2000: 304.88 },
  pluto: { name: "Pluto", motion: 0.004, j2000: 238.96 },
};

const ASPECTS: Record<string, { angle: number; orb: number; symbol: string; nature: string }> = {
  conjunction: { angle: 0, orb: 8, symbol: "☌", nature: "major" },
  sextile: { angle: 60, orb: 4, symbol: "⚹", nature: "harmonious" },
  square: { angle: 90, orb: 6, symbol: "□", nature: "challenging" },
  trine: { angle: 120, orb: 6, symbol: "△", nature: "harmonious" },
  opposition: { angle: 180, orb: 8, symbol: "☍", nature: "challenging" },
};

const HOUSE_MEANINGS = [
  "Self, identity, appearance",
  "Values, possessions, resources",
  "Communication, siblings, local travel",
  "Home, family, roots",
  "Creativity, romance, children",
  "Health, work, service",
  "Partnerships, marriage, contracts",
  "Transformation, shared resources, death",
  "Philosophy, travel, higher education",
  "Career, public image, authority",
  "Friends, groups, aspirations",
  "Spirituality, unconscious, endings"
];

const J2000 = 2451545.0;
const OBLIQUITY = 23.4393; // Earth's axial tilt in degrees

function toJD(y: number, m: number, d: number, h: number = 0): number {
  if (m <= 2) { y--; m += 12; }
  const A = Math.floor(y / 100);
  const jd = Math.floor(365.25 * (y + 4716)) + Math.floor(30.6001 * (m + 1)) + d + 2 - A + Math.floor(A / 4) - 1524.5;
  return jd + h / 24;
}

function norm(a: number): number { a = a % 360; return a < 0 ? a + 360 : a; }

function degToRad(d: number): number { return d * Math.PI / 180; }
function radToDeg(r: number): number { return r * 180 / Math.PI; }

function getSign(lon: number): { sign: string; degree: number; signIndex: number } {
  const n = norm(lon);
  const signIndex = Math.floor(n / 30);
  return { sign: ZODIAC[signIndex], degree: Math.round((n % 30) * 100) / 100, signIndex };
}

function lon(p: string, jd: number): number {
  const pl = PLANETS[p];
  return pl ? norm(pl.j2000 + pl.motion * (jd - J2000)) : 0;
}

// Calculate Greenwich Mean Sidereal Time
function gmst(jd: number): number {
  const T = (jd - 2451545.0) / 36525;
  let theta = 280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * T * T - T * T * T / 38710000;
  return norm(theta);
}

// Calculate Local Sidereal Time
function lst(jd: number, longitude: number): number {
  return norm(gmst(jd) + longitude);
}

// Calculate Ascendant (Rising Sign) using standard formula
function calcAscendant(jd: number, latitude: number, longitude: number): number {
  const localST = lst(jd, longitude);
  const latRad = degToRad(latitude);
  const oblRad = degToRad(OBLIQUITY);
  const lstRad = degToRad(localST);
  
  // Standard Ascendant formula: Asc = atan2(-cos(RAMC), sin(RAMC)*cos(ε) + tan(φ)*sin(ε))
  // where RAMC = Local Sidereal Time, ε = obliquity, φ = latitude
  const tanAsc = -Math.cos(lstRad) / (Math.sin(lstRad) * Math.cos(oblRad) + Math.tan(latRad) * Math.sin(oblRad));
  
  // Calculate base ascendant
  let asc = radToDeg(Math.atan(tanAsc));
  
  // Correct quadrant based on LST
  // LST 0-180° → Asc should be in 180-360° range (Libra through Pisces then Aries)
  // LST 180-360° → Asc should be in 0-180° range (Aries through Virgo)
  if (localST >= 0 && localST < 180) {
    asc = asc + 180;
  } else if (localST >= 180 && localST < 360) {
    if (asc < 0) {
      asc = asc + 360;
    }
  }
  
  return norm(asc);
}

// Calculate Midheaven (MC)
function calcMidheaven(jd: number, longitude: number): number {
  const localST = lst(jd, longitude);
  const oblRad = degToRad(OBLIQUITY);
  const lstRad = degToRad(localST);
  
  let mc = radToDeg(Math.atan2(Math.sin(lstRad), Math.cos(lstRad) * Math.cos(oblRad)));
  return norm(mc);
}

// Generate Whole Sign houses from Ascendant
function calcWholeSIgnHouses(ascendant: number): Array<{ house: number; sign: string; cusp: number; meaning: string }> {
  const ascSign = getSign(ascendant);
  const houses = [];
  
  for (let i = 0; i < 12; i++) {
    const signIndex = (ascSign.signIndex + i) % 12;
    const cusp = signIndex * 30;
    houses.push({
      house: i + 1,
      sign: ZODIAC[signIndex],
      cusp: cusp,
      meaning: HOUSE_MEANINGS[i]
    });
  }
  
  return houses;
}

// Determine which house a planet is in (Whole Sign)
function getHouse(planetLon: number, ascendant: number): number {
  const ascSign = getSign(ascendant);
  const planetSign = getSign(planetLon);
  let house = (planetSign.signIndex - ascSign.signIndex + 12) % 12 + 1;
  return house;
}

// Calculate aspects between two positions
function findAspect(lon1: number, lon2: number): { aspect: string; symbol: string; nature: string; orb: number; exact: boolean } | null {
  let sep = Math.abs(lon1 - lon2);
  if (sep > 180) sep = 360 - sep;
  
  for (const [name, data] of Object.entries(ASPECTS)) {
    const diff = Math.abs(sep - data.angle);
    if (diff <= data.orb) {
      return {
        aspect: name,
        symbol: data.symbol,
        nature: data.nature,
        orb: Math.round(diff * 100) / 100,
        exact: diff < 1
      };
    }
  }
  return null;
}

interface ChartInput {
  year: number;
  month: number;
  day: number;
  hour: number;
  minute: number;
  latitude: number;
  longitude: number;
  timezone: number; // offset from UTC in hours
  name?: string;
}

interface NatalChart {
  input: ChartInput;
  ascendant: { longitude: number; sign: string; degree: number };
  midheaven: { longitude: number; sign: string; degree: number };
  houses: Array<{ house: number; sign: string; cusp: number; meaning: string }>;
  planets: Array<{ name: string; longitude: number; sign: string; degree: number; house: number; retrograde?: boolean }>;
  aspects: Array<{ planet1: string; planet2: string; aspect: string; symbol: string; nature: string; orb: number; exact: boolean }>;
}

function calculateNatalChart(input: ChartInput): NatalChart {
  // Convert local time to UTC
  const utcHour = input.hour - input.timezone + input.minute / 60;
  const jd = toJD(input.year, input.month, input.day, utcHour);
  
  // Calculate angles
  const ascLon = calcAscendant(jd, input.latitude, input.longitude);
  const mcLon = calcMidheaven(jd, input.longitude);
  
  const ascData = getSign(ascLon);
  const mcData = getSign(mcLon);
  
  // Calculate houses (Whole Sign)
  const houses = calcWholeSIgnHouses(ascLon);
  
  // Calculate planetary positions
  const planets = [];
  for (const [key, data] of Object.entries(PLANETS)) {
    const planetLon = lon(key, jd);
    const signData = getSign(planetLon);
    const house = getHouse(planetLon, ascLon);
    
    planets.push({
      name: data.name,
      longitude: Math.round(planetLon * 100) / 100,
      sign: signData.sign,
      degree: signData.degree,
      house
    });
  }
  
  // Calculate aspects
  const aspects = [];
  const planetKeys = Object.keys(PLANETS);
  for (let i = 0; i < planetKeys.length; i++) {
    for (let j = i + 1; j < planetKeys.length; j++) {
      const lon1 = lon(planetKeys[i], jd);
      const lon2 = lon(planetKeys[j], jd);
      const aspect = findAspect(lon1, lon2);
      if (aspect) {
        aspects.push({
          planet1: PLANETS[planetKeys[i]].name,
          planet2: PLANETS[planetKeys[j]].name,
          ...aspect
        });
      }
    }
  }
  
  return {
    input,
    ascendant: { longitude: Math.round(ascLon * 100) / 100, sign: ascData.sign, degree: ascData.degree },
    midheaven: { longitude: Math.round(mcLon * 100) / 100, sign: mcData.sign, degree: mcData.degree },
    houses,
    planets,
    aspects
  };
}

function calculateSynastry(chart1: NatalChart, chart2: NatalChart): object {
  const crossAspects = [];
  
  // Find aspects between chart1 planets and chart2 planets
  for (const p1 of chart1.planets) {
    for (const p2 of chart2.planets) {
      const aspect = findAspect(p1.longitude, p2.longitude);
      if (aspect) {
        crossAspects.push({
          person1_planet: p1.name,
          person2_planet: p2.name,
          ...aspect,
          interpretation: interpretSynastryAspect(p1.name, p2.name, aspect.aspect, aspect.nature)
        });
      }
    }
  }
  
  // House overlays - where do person2's planets fall in person1's houses
  const houseOverlays1 = chart2.planets.map(p => ({
    planet: p.name,
    in_house: getHouse(p.longitude, chart1.ascendant.longitude),
    meaning: `${p.name} activates ${chart1.input.name || "Person 1"}'s house of ${HOUSE_MEANINGS[getHouse(p.longitude, chart1.ascendant.longitude) - 1]}`
  }));
  
  const houseOverlays2 = chart1.planets.map(p => ({
    planet: p.name,
    in_house: getHouse(p.longitude, chart2.ascendant.longitude),
    meaning: `${p.name} activates ${chart2.input.name || "Person 2"}'s house of ${HOUSE_MEANINGS[getHouse(p.longitude, chart2.ascendant.longitude) - 1]}`
  }));
  
  // Calculate compatibility score based on aspects
  let harmoniousCount = crossAspects.filter(a => a.nature === "harmonious").length;
  let challengingCount = crossAspects.filter(a => a.nature === "challenging").length;
  let majorConjunctions = crossAspects.filter(a => a.aspect === "conjunction").length;
  
  return {
    person1: chart1.input.name || "Person 1",
    person2: chart2.input.name || "Person 2",
    summary: {
      total_aspects: crossAspects.length,
      harmonious_aspects: harmoniousCount,
      challenging_aspects: challengingCount,
      conjunctions: majorConjunctions,
      compatibility_index: Math.round((harmoniousCount + majorConjunctions * 0.5) / (crossAspects.length || 1) * 100)
    },
    cross_aspects: crossAspects,
    house_overlays: {
      person2_in_person1_houses: houseOverlays1,
      person1_in_person2_houses: houseOverlays2
    }
  };
}

function interpretSynastryAspect(planet1: string, planet2: string, aspect: string, nature: string): string {
  const base = `${planet1} ${aspect} ${planet2}`;
  if (nature === "harmonious") {
    return `${base}: Easy flow of energy, mutual support and understanding`;
  } else if (nature === "challenging") {
    return `${base}: Dynamic tension that can fuel growth or create friction`;
  }
  return `${base}: Powerful connection that merges these planetary energies`;
}

// ============ MOON PHASE CALCULATIONS ============

interface MoonPhase {
  phase: string;
  name: string;
  emoji: string;
  date: string;
  jd: number;
  sun_longitude: number;
  moon_longitude: number;
  sun_sign: string;
  moon_sign: string;
  sun_degree: number;
  moon_degree: number;
  exactness_degrees: number;
}

const MOON_PHASE_ANGLES: Record<string, number> = {
  new: 0,
  first_quarter: 90,
  full: 180,
  last_quarter: 270
};

const MOON_PHASE_NAMES: Record<string, string> = {
  new: "New Moon",
  first_quarter: "First Quarter",
  full: "Full Moon",
  last_quarter: "Last Quarter"
};

const MOON_PHASE_EMOJIS: Record<string, string> = {
  new: "🌑",
  first_quarter: "🌓",
  full: "🌕",
  last_quarter: "🌗"
};

function getSunMoonAngle(jd: number): number {
  const sunLon = lon("sun", jd);
  const moonLon = lon("moon", jd);
  return norm(moonLon - sunLon);
}

function detectPhaseCrossing(prevAngle: number, currAngle: number, targetAngle: number): boolean {
  if (targetAngle === 0) {
    // New moon: crossing from ~360 to ~0
    if (prevAngle > 270 && currAngle < 90) return true;
  } else {
    if (prevAngle < targetAngle && currAngle >= targetAngle) return true;
  }
  return false;
}

function findExactPhaseTime(startJd: number, endJd: number, targetAngle: number): number {
  const tolerance = 0.01;
  let lo = startJd, hi = endJd;
  
  for (let i = 0; i < 50; i++) {
    const mid = (lo + hi) / 2;
    let angle = getSunMoonAngle(mid);
    
    if (targetAngle === 0 && angle > 180) {
      angle = angle - 360;
    }
    
    const error = angle - targetAngle;
    if (Math.abs(error) < tolerance) return mid;
    
    if (error > 0) hi = mid;
    else lo = mid;
  }
  
  return (lo + hi) / 2;
}

function calcMoonPhases(year: number): MoonPhase[] {
  const phases: MoonPhase[] = [];
  const startJd = toJD(year, 1, 1);
  const endJd = toJD(year + 1, 1, 1);
  
  let prevAngle = getSunMoonAngle(startJd);
  
  for (let jd = startJd + 0.5; jd < endJd; jd += 0.5) {
    const currAngle = getSunMoonAngle(jd);
    
    for (const [phaseName, targetAngle] of Object.entries(MOON_PHASE_ANGLES)) {
      if (detectPhaseCrossing(prevAngle, currAngle, targetAngle)) {
        const exactJd = findExactPhaseTime(jd - 0.5, jd, targetAngle);
        
        const sunLon = lon("sun", exactJd);
        const moonLon = lon("moon", exactJd);
        const sunData = getSign(sunLon);
        const moonData = getSign(moonLon);
        
        let angleDiff = Math.abs(getSunMoonAngle(exactJd) - targetAngle);
        if (targetAngle === 0 && angleDiff > 180) angleDiff = 360 - angleDiff;
        
        phases.push({
          phase: phaseName,
          name: MOON_PHASE_NAMES[phaseName],
          emoji: MOON_PHASE_EMOJIS[phaseName],
          date: fromJD(exactJd),
          jd: Math.round(exactJd * 1000) / 1000,
          sun_longitude: Math.round(sunLon * 100) / 100,
          moon_longitude: Math.round(moonLon * 100) / 100,
          sun_sign: sunData.sign,
          moon_sign: moonData.sign,
          sun_degree: sunData.degree,
          moon_degree: moonData.degree,
          exactness_degrees: Math.round(angleDiff * 10000) / 10000
        });
      }
    }
    
    prevAngle = currAngle;
  }
  
  return phases.sort((a, b) => a.jd - b.jd);
}

function getCurrentMoonPhase(jd: number): { phase: string; name: string; emoji: string; illumination: number; age_days: number } {
  const angle = getSunMoonAngle(jd);
  
  // Determine phase name from angle
  let phase: string;
  if (angle < 22.5 || angle >= 337.5) phase = "new";
  else if (angle < 67.5) phase = "waxing_crescent";
  else if (angle < 112.5) phase = "first_quarter";
  else if (angle < 157.5) phase = "waxing_gibbous";
  else if (angle < 202.5) phase = "full";
  else if (angle < 247.5) phase = "waning_gibbous";
  else if (angle < 292.5) phase = "last_quarter";
  else phase = "waning_crescent";
  
  const phaseNames: Record<string, string> = {
    new: "New Moon", waxing_crescent: "Waxing Crescent", first_quarter: "First Quarter",
    waxing_gibbous: "Waxing Gibbous", full: "Full Moon", waning_gibbous: "Waning Gibbous",
    last_quarter: "Last Quarter", waning_crescent: "Waning Crescent"
  };
  
  const phaseEmojis: Record<string, string> = {
    new: "🌑", waxing_crescent: "🌒", first_quarter: "🌓", waxing_gibbous: "🌔",
    full: "🌕", waning_gibbous: "🌖", last_quarter: "🌗", waning_crescent: "🌘"
  };
  
  // Illumination: 0% at new, 100% at full
  const illumination = Math.round((1 - Math.cos(degToRad(angle))) / 2 * 100);
  
  // Approximate age (days since new moon, synodic month ~29.53 days)
  const ageDays = Math.round(angle / 360 * 29.53 * 10) / 10;
  
  return {
    phase,
    name: phaseNames[phase],
    emoji: phaseEmojis[phase],
    illumination,
    age_days: ageDays
  };
}

// ============ TRANSIT CALCULATIONS ============

interface TransitEvent { type: string; [k: string]: unknown }

function calcIngresses(year: number): TransitEvent[] {
  const r: TransitEvent[] = [];
  const s = toJD(year, 1, 1), e = toJD(year + 1, 1, 1);
  const steps: Record<string, number> = { moon: 0.5, sun: 1, mercury: 0.5, venus: 0.5, mars: 1, jupiter: 2, saturn: 3, uranus: 5, neptune: 7, pluto: 10 };
  for (const [k, p] of Object.entries(PLANETS)) {
    const st = steps[k] || 1;
    let prev: string | null = null;
    for (let jd = s; jd < e; jd += st) {
      const { sign: sg } = getSign(lon(k, jd));
      if (prev && sg !== prev) r.push({ type: "ingress", body: p.name, from: prev, to: sg, date: fromJD(jd), jd: Math.round(jd * 100) / 100 });
      prev = sg;
    }
  }
  return r.sort((a, b) => (a.jd as number) - (b.jd as number));
}

function fromJD(jd: number): string {
  const Z = Math.floor(jd + 0.5);
  const alpha = Math.floor((Z - 1867216.25) / 36524.25);
  const A = Z < 2299161 ? Z : Z + 1 + alpha - Math.floor(alpha / 4);
  const B = A + 1524;
  const C = Math.floor((B - 122.1) / 365.25);
  const D = Math.floor(365.25 * C);
  const E = Math.floor((B - D) / 30.6001);
  const day = Math.floor(B - D - Math.floor(30.6001 * E));
  const month = E < 14 ? E - 1 : E - 13;
  const year = month > 2 ? C - 4716 : C - 4715;
  return `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
}

function calcRetrogrades(year: number): TransitEvent[] {
  const r: TransitEvent[] = [];
  const s = toJD(year, 1, 1), e = toJD(year + 1, 1, 1);
  for (const k of ["mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]) {
    let pL: number | null = null, pD: string | null = null, sJd: number | null = null;
    const st = k === "mercury" || k === "venus" ? 0.5 : 1;
    for (let jd = s; jd < e; jd += st) {
      const l = lon(k, jd);
      if (pL !== null) {
        let m = l - pL; if (m > 180) m -= 360; if (m < -180) m += 360;
        const d = m > 0 ? "direct" : "retrograde";
        if (pD && d !== pD) {
          const { sign: sg, degree: deg } = getSign(l);
          if (d === "retrograde") { sJd = jd; r.push({ type: "retrograde_start", body: PLANETS[k].name, date: fromJD(jd), sign: sg, degree: deg, jd: Math.round(jd * 100) / 100 }); }
          else if (sJd) { r.push({ type: "retrograde_end", body: PLANETS[k].name, date: fromJD(jd), sign: sg, degree: deg, duration_days: Math.round(jd - sJd), jd: Math.round(jd * 100) / 100 }); sJd = null; }
        }
        pD = d;
      }
      pL = l;
    }
  }
  return r.sort((a, b) => (a.jd as number) - (b.jd as number));
}

function calcTransitAspects(year: number): TransitEvent[] {
  const r: TransitEvent[] = [];
  const s = toJD(year, 1, 1), e = toJD(year + 1, 1, 1);
  const outer = ["jupiter", "saturn", "uranus", "neptune", "pluto"];
  
  for (let i = 0; i < outer.length; i++) {
    for (let j = i + 1; j < outer.length; j++) {
      for (const [n, a] of Object.entries(ASPECTS)) {
        let io = false, bJd: number | null = null, bD = 999;
        for (let jd = s; jd < e; jd += 1) {
          let sep = Math.abs(lon(outer[i], jd) - lon(outer[j], jd)); if (sep > 180) sep = 360 - sep;
          const df = Math.abs(sep - a.angle);
          if (df <= a.orb) { if (df < bD) { bD = df; bJd = jd; } io = true; }
          else if (io && bJd) {
            r.push({ type: "aspect", aspect: n, symbol: a.symbol, body1: PLANETS[outer[i]].name, body2: PLANETS[outer[j]].name, pos1: getSign(lon(outer[i], bJd)), pos2: getSign(lon(outer[j], bJd)), date: fromJD(bJd), exactness: Math.round(bD * 100) / 100, jd: Math.round(bJd * 100) / 100 });
            io = false; bJd = null; bD = 999;
          }
        }
      }
    }
  }
  
  // Sun aspects to outer planets
  for (const p of outer) {
    for (const [n, a] of Object.entries(ASPECTS)) {
      if (!["conjunction", "opposition", "square"].includes(n)) continue;
      let io = false, bJd: number | null = null, bD = 999;
      for (let jd = s; jd < e; jd += 0.5) {
        let sep = Math.abs(lon("sun", jd) - lon(p, jd)); if (sep > 180) sep = 360 - sep;
        const df = Math.abs(sep - a.angle);
        if (df <= 3) { if (df < bD) { bD = df; bJd = jd; } io = true; }
        else if (io && bJd) {
          r.push({ type: "aspect", aspect: n, symbol: a.symbol, body1: "Sun", body2: PLANETS[p].name, pos1: getSign(lon("sun", bJd)), pos2: getSign(lon(p, bJd)), date: fromJD(bJd), exactness: Math.round(bD * 100) / 100, jd: Math.round(bJd * 100) / 100 });
          io = false; bJd = null; bD = 999;
        }
      }
    }
  }
  return r.sort((a, b) => (a.jd as number) - (b.jd as number));
}

function generateTransitReport(years: number[]): object {
  const report: Record<string, unknown> = {
    metadata: {
      generated_at: new Date().toISOString(),
      calculation_method: "Keplerian Mean Elements",
      accuracy: "Mean longitude calculations, ~1-2 degree accuracy",
      years_covered: years
    },
    transits_by_year: {}
  };
  
  for (const y of years) {
    const ingresses = calcIngresses(y);
    const retrogrades = calcRetrogrades(y);
    const aspects = calcTransitAspects(y);
    (report.transits_by_year as Record<number, object>)[y] = {
      summary: { total_ingresses: ingresses.length, total_retrogrades: retrogrades.length, total_aspects: aspects.length },
      ingresses, retrogrades, aspects
    };
  }
  return report;
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  
  try {
    const url = new URL(req.url);
    const pathSegments = url.pathname.split("/").filter(s => s.length > 0);
    let path = pathSegments[pathSegments.length - 1] || "";
    // Handle URL-encoded query strings in path
    if (path.includes("%3F") || path.includes("?")) {
      path = path.split(/[%3F?]/)[0];
    }
    console.log(`Request: ${req.method} ${url.pathname} -> path segment: "${path}"`);
    
    // GET request for transits
    if (req.method === "GET" && (path === "transits" || path.startsWith("transits"))) {
      const yearsParam = url.searchParams.get("years");
      let years = [2025, 2026, 2027];
      if (yearsParam) years = yearsParam.split(",").map(y => parseInt(y.trim())).filter(y => !isNaN(y));
      
      console.log(`Generating transit report for: ${years.join(", ")}`);
      const report = generateTransitReport(years);
      
      return new Response(JSON.stringify(report, null, 2), { headers: { ...corsHeaders, "Content-Type": "application/json" } });
    }
    
    // GET or POST request for moon phases
    if (path === "moon-phases" || path === "moon") {
      let year = new Date().getFullYear();
      
      if (req.method === "GET") {
        const yearParam = url.searchParams.get("year");
        if (yearParam) year = parseInt(yearParam);
      } else if (req.method === "POST") {
        const body = await req.json();
        if (body.year) year = body.year;
      }
      
      console.log(`Calculating moon phases for year: ${year}`);
      const phases = calcMoonPhases(year);
      const currentJd = toJD(new Date().getFullYear(), new Date().getMonth() + 1, new Date().getDate(), new Date().getHours());
      const current = getCurrentMoonPhase(currentJd);
      
      return new Response(JSON.stringify({
        success: true,
        year,
        total_phases: phases.length,
        current: {
          ...current,
          moon_position: getSign(lon("moon", currentJd))
        },
        phases
      }, null, 2), { headers: { ...corsHeaders, "Content-Type": "application/json" } });
    }
    
    if (req.method === "POST") {
      const body = await req.json();
      
      if (path === "natal" || path === "natal-chart") {
        const input: ChartInput = {
          year: body.year,
          month: body.month,
          day: body.day,
          hour: body.hour || 12,
          minute: body.minute || 0,
          latitude: body.latitude,
          longitude: body.longitude,
          timezone: body.timezone || 0,
          name: body.name
        };
        
        if (!input.year || !input.month || !input.day || input.latitude === undefined || input.longitude === undefined) {
          return new Response(JSON.stringify({ 
            error: "Missing required fields: year, month, day, latitude, longitude" 
          }), { status: 400, headers: { ...corsHeaders, "Content-Type": "application/json" } });
        }
        
        const chart = calculateNatalChart(input);
        
        return new Response(JSON.stringify({
          success: true,
          calculation_method: "Keplerian Mean Elements with Whole Sign Houses",
          accuracy_note: "Positions accurate to ~1-2 degrees. For precise calculations, use Swiss Ephemeris.",
          chart
        }, null, 2), { headers: { ...corsHeaders, "Content-Type": "application/json" } });
      }
      
      if (path === "synastry") {
        const person1: ChartInput = {
          year: body.person1.year,
          month: body.person1.month,
          day: body.person1.day,
          hour: body.person1.hour || 12,
          minute: body.person1.minute || 0,
          latitude: body.person1.latitude,
          longitude: body.person1.longitude,
          timezone: body.person1.timezone || 0,
          name: body.person1.name || "Person 1"
        };
        
        const person2: ChartInput = {
          year: body.person2.year,
          month: body.person2.month,
          day: body.person2.day,
          hour: body.person2.hour || 12,
          minute: body.person2.minute || 0,
          latitude: body.person2.latitude,
          longitude: body.person2.longitude,
          timezone: body.person2.timezone || 0,
          name: body.person2.name || "Person 2"
        };
        
        const chart1 = calculateNatalChart(person1);
        const chart2 = calculateNatalChart(person2);
        const synastry = calculateSynastry(chart1, chart2);
        
        return new Response(JSON.stringify({
          success: true,
          calculation_method: "Keplerian Mean Elements with Whole Sign Houses",
          chart1,
          chart2,
          synastry
        }, null, 2), { headers: { ...corsHeaders, "Content-Type": "application/json" } });
      }
    }
    
    // Default: show API documentation
    return new Response(JSON.stringify({
      api: "Astrology API",
      base_url: url.origin + "/functions/v1/natal-chart",
      endpoints: {
        "GET /transits": {
          description: "Get planetary transits for specified years",
          query_params: { years: "Comma-separated years (default: 2025,2026,2027)" },
          returns: "Ingresses, retrogrades, and major aspects for each year"
        },
        "GET /moon-phases": {
          description: "Get all moon phases for a year with current moon info",
          query_params: { year: "Year to calculate (default: current year)" },
          returns: "All new/full/quarter moons with current phase and illumination"
        },
        "POST /moon-phases": {
          description: "Get moon phases for specified year",
          body: { year: "Year to calculate (default: current year)" },
          returns: "All new/full/quarter moons with current phase and illumination"
        },
        "POST /natal": {
          description: "Calculate a complete natal chart with rising sign",
          body: {
            year: "Birth year (required)",
            month: "Birth month 1-12 (required)",
            day: "Birth day 1-31 (required)",
            hour: "Birth hour 0-23 (default: 12)",
            minute: "Birth minute 0-59 (default: 0)",
            latitude: "Birth location latitude (required)",
            longitude: "Birth location longitude (required)",
            timezone: "Timezone offset from UTC in hours (default: 0)",
            name: "Optional name for the chart"
          },
          returns: "Full natal chart with ascendant (rising sign), midheaven, houses, planets, and aspects"
        },
        "POST /synastry": {
          description: "Compare two natal charts for compatibility",
          body: {
            person1: "First person's birth data",
            person2: "Second person's birth data"
          },
          returns: "Both natal charts plus synastry analysis with cross-aspects and house overlays"
        }
      },
      examples: {
        transits: "GET /transits?years=2025,2026,2027",
        moon_phases: "GET /moon-phases?year=2025",
        natal_chart: {
          year: 1990, month: 6, day: 15, hour: 14, minute: 30,
          latitude: 40.7128, longitude: -74.0060, timezone: -5, name: "Example"
        }
      }
    }, null, 2), { headers: { ...corsHeaders, "Content-Type": "application/json" } });
    
  } catch (err) {
    console.error("Error:", err);
    return new Response(JSON.stringify({ error: String(err) }), { 
      status: 500, 
      headers: { ...corsHeaders, "Content-Type": "application/json" } 
    });
  }
});
