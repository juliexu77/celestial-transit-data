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
};

const ASPECTS: Record<string, { angle: number; orb: number; symbol: string }> = {
  conjunction: { angle: 0, orb: 8, symbol: "☌" },
  sextile: { angle: 60, orb: 6, symbol: "⚹" },
  square: { angle: 90, orb: 8, symbol: "□" },
  trine: { angle: 120, orb: 8, symbol: "△" },
  opposition: { angle: 180, orb: 8, symbol: "☍" },
};

const J2000 = 2451545.0;

function toJD(y: number, m: number, d: number): number {
  if (m <= 2) { y--; m += 12; }
  const A = Math.floor(y / 100);
  return Math.floor(365.25 * (y + 4716)) + Math.floor(30.6001 * (m + 1)) + d + 2 - A + Math.floor(A / 4) - 1524.5;
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

function norm(a: number): number { a = a % 360; return a < 0 ? a + 360 : a; }
function sign(lon: number): { sign: string; deg: number } {
  const n = norm(lon);
  return { sign: ZODIAC[Math.floor(n / 30)], deg: Math.round((n % 30) * 10) / 10 };
}
function lon(p: string, jd: number): number {
  const pl = PLANETS[p];
  return pl ? norm(pl.j2000 + pl.motion * (jd - J2000)) : 0;
}

interface Evt { type: string; [k: string]: unknown }

function ingresses(year: number): Evt[] {
  const r: Evt[] = [];
  const s = toJD(year, 1, 1), e = toJD(year + 1, 1, 1);
  const steps: Record<string, number> = { moon: 0.5, sun: 1, mercury: 0.5, venus: 0.5, mars: 1, jupiter: 2, saturn: 3, uranus: 5, neptune: 7 };
  for (const [k, p] of Object.entries(PLANETS)) {
    const st = steps[k] || 1;
    let prev: string | null = null;
    for (let jd = s; jd < e; jd += st) {
      const { sign: sg } = sign(lon(k, jd));
      if (prev && sg !== prev) r.push({ type: "ingress", body: p.name, from: prev, to: sg, date: fromJD(jd), jd: Math.round(jd * 100) / 100 });
      prev = sg;
    }
  }
  return r.sort((a, b) => (a.jd as number) - (b.jd as number));
}

function retrogrades(year: number): Evt[] {
  const r: Evt[] = [];
  const s = toJD(year, 1, 1), e = toJD(year + 1, 1, 1);
  for (const k of ["mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune"]) {
    let pL: number | null = null, pD: string | null = null, sJd: number | null = null;
    const st = k === "mercury" || k === "venus" ? 0.5 : 1;
    for (let jd = s; jd < e; jd += st) {
      const l = lon(k, jd);
      if (pL !== null) {
        let m = l - pL; if (m > 180) m -= 360; if (m < -180) m += 360;
        const d = m > 0 ? "direct" : "retro";
        if (pD && d !== pD) {
          const { sign: sg, deg } = sign(l);
          if (d === "retro") { sJd = jd; r.push({ type: "retro_start", body: PLANETS[k].name, date: fromJD(jd), sign: sg, deg, jd: Math.round(jd * 100) / 100 }); }
          else if (sJd) { r.push({ type: "retro_end", body: PLANETS[k].name, date: fromJD(jd), sign: sg, deg, days: Math.round(jd - sJd), jd: Math.round(jd * 100) / 100 }); sJd = null; }
        }
        pD = d;
      }
      pL = l;
    }
  }
  return r.sort((a, b) => (a.jd as number) - (b.jd as number));
}

function aspects(year: number): Evt[] {
  const r: Evt[] = [];
  const s = toJD(year, 1, 1), e = toJD(year + 1, 1, 1);
  const outer = ["jupiter", "saturn", "uranus", "neptune"];
  for (let i = 0; i < outer.length; i++) {
    for (let j = i + 1; j < outer.length; j++) {
      for (const [n, a] of Object.entries(ASPECTS)) {
        let io = false, bJd: number | null = null, bD = 999;
        for (let jd = s; jd < e; jd += 1) {
          let sep = Math.abs(lon(outer[i], jd) - lon(outer[j], jd)); if (sep > 180) sep = 360 - sep;
          const df = Math.abs(sep - a.angle);
          if (df <= a.orb) { if (df < bD) { bD = df; bJd = jd; } io = true; }
          else if (io && bJd) {
            r.push({ type: "aspect", asp: n, sym: a.symbol, b1: PLANETS[outer[i]].name, b2: PLANETS[outer[j]].name, p1: sign(lon(outer[i], bJd)), p2: sign(lon(outer[j], bJd)), date: fromJD(bJd), ex: Math.round(bD * 100) / 100, jd: Math.round(bJd * 100) / 100 });
            io = false; bJd = null; bD = 999;
          }
        }
      }
    }
  }
  for (const p of outer) {
    for (const [n, a] of Object.entries(ASPECTS)) {
      if (!["conjunction", "opposition", "square"].includes(n)) continue;
      let io = false, bJd: number | null = null, bD = 999;
      for (let jd = s; jd < e; jd += 0.5) {
        let sep = Math.abs(lon("sun", jd) - lon(p, jd)); if (sep > 180) sep = 360 - sep;
        const df = Math.abs(sep - a.angle);
        if (df <= 3) { if (df < bD) { bD = df; bJd = jd; } io = true; }
        else if (io && bJd) {
          r.push({ type: "aspect", asp: n, sym: a.symbol, b1: "Sun", b2: PLANETS[p].name, p1: sign(lon("sun", bJd)), p2: sign(lon(p, bJd)), date: fromJD(bJd), ex: Math.round(bD * 100) / 100, jd: Math.round(bJd * 100) / 100 });
          io = false; bJd = null; bD = 999;
        }
      }
    }
  }
  return r.sort((a, b) => (a.jd as number) - (b.jd as number));
}

function report(years: number[]): object {
  const out: Record<string, unknown> = {
    meta: { generated: new Date().toISOString(), method: "Keplerian Mean Elements", accuracy: "1-2 deg", years },
    data: {}
  };
  for (const y of years) {
    const i = ingresses(y), rt = retrogrades(y), a = aspects(y);
    (out.data as Record<number, object>)[y] = { summary: { ingresses: i.length, retrogrades: rt.length, aspects: a.length }, ingresses: i, retrogrades: rt, aspects: a };
  }
  return out;
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: corsHeaders });
  try {
    const url = new URL(req.url);
    const yp = url.searchParams.get("years");
    let yrs = [2025, 2026, 2027];
    if (yp) yrs = yp.split(",").map(y => parseInt(y.trim())).filter(y => !isNaN(y));
    console.log(`Gen: ${yrs.join(", ")}`);
    return new Response(JSON.stringify(report(yrs), null, 2), { headers: { ...corsHeaders, "Content-Type": "application/json" } });
  } catch (err) {
    console.error("Err:", err);
    return new Response(JSON.stringify({ error: String(err) }), { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } });
  }
});
