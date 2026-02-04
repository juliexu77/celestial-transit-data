import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";

// ============ TYPES ============

export interface MoonPhase {
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

export interface CurrentMoonPhase {
  phase: string;
  name: string;
  emoji: string;
  illumination: number;
  age_days: number;
  moon_position: {
    longitude: number;
    sign: string;
    degree: number;
  };
}

export interface TransitEvent {
  type: string;
  body?: string;
  body1?: string;
  body2?: string;
  date: string;
  jd: number;
  sign?: string;
  from?: string;
  to?: string;
  aspect?: string;
  symbol?: string;
  degree?: number;
  duration_days?: number;
  exactness?: number;
}

export interface YearTransits {
  summary: {
    total_ingresses: number;
    total_retrogrades: number;
    total_aspects: number;
  };
  ingresses: TransitEvent[];
  retrogrades: TransitEvent[];
  aspects: TransitEvent[];
}

export interface TransitReport {
  metadata: {
    generated_at: string;
    calculation_method: string;
    accuracy: string;
    years_covered: number[];
  };
  transits_by_year: Record<number, YearTransits>;
}

export interface MoonPhasesResponse {
  success: boolean;
  year: number;
  total_phases: number;
  phases: MoonPhase[];
  current?: CurrentMoonPhase;
}

export interface PlanetPosition {
  name: string;
  longitude: number;
  sign: string;
  degree: number;
  house: number;
}

export interface NatalChart {
  input: {
    year: number;
    month: number;
    day: number;
    hour: number;
    minute: number;
    latitude: number;
    longitude: number;
    timezone: number;
    name?: string;
  };
  ascendant: { longitude: number; sign: string; degree: number };
  midheaven: { longitude: number; sign: string; degree: number };
  houses: Array<{ house: number; sign: string; cusp: number; meaning: string }>;
  planets: PlanetPosition[];
  aspects: Array<{
    planet1: string;
    planet2: string;
    aspect: string;
    symbol: string;
    nature: string;
    orb: number;
    exact: boolean;
  }>;
}

// ============ API FUNCTIONS ============

const API_BASE_URL = `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/natal-chart`;
const API_KEY = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY;

async function fetchMoonPhases(year: number): Promise<MoonPhasesResponse> {
  console.log(`[AstrologyAPI] Fetching moon phases for ${year}`);
  
  const response = await fetch(`${API_BASE_URL}/moon-phases?year=${year}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'apikey': API_KEY,
    },
  });

  if (!response.ok) {
    console.error(`[AstrologyAPI] Moon phases request failed: ${response.status}`);
    throw new Error(`Failed to fetch moon phases: ${response.status}`);
  }

  return response.json();
}

async function fetchTransits(years: number[]): Promise<TransitReport> {
  const { data, error } = await supabase.functions.invoke("natal-chart/transits", {
    method: "GET",
    body: { years: years.join(",") },
  });
  
  if (error) {
    // Fallback to query param approach
    const response = await fetch(
      `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/natal-chart/transits?years=${years.join(",")}`,
      {
        headers: {
          "apikey": import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY,
          "Content-Type": "application/json",
        },
      }
    );
    if (!response.ok) throw new Error("Failed to fetch transits");
    return response.json();
  }
  return data;
}

async function fetchNatalChart(params: {
  year: number;
  month: number;
  day: number;
  hour?: number;
  minute?: number;
  latitude: number;
  longitude: number;
  timezone?: number;
  name?: string;
}): Promise<{ success: boolean; chart: NatalChart }> {
  const { data, error } = await supabase.functions.invoke("natal-chart/natal", {
    body: params,
  });
  
  if (error) throw new Error(error.message);
  return data;
}

// ============ HOOKS ============

export function useMoonPhases(year: number = new Date().getFullYear()) {
  return useQuery({
    queryKey: ["moon-phases", year],
    queryFn: () => fetchMoonPhases(year),
    staleTime: 1000 * 60 * 60, // 1 hour
  });
}

export function useTransits(years: number[] = [new Date().getFullYear()]) {
  return useQuery({
    queryKey: ["transits", years],
    queryFn: () => fetchTransits(years),
    staleTime: 1000 * 60 * 60, // 1 hour
  });
}

export function useNatalChart(params: {
  year: number;
  month: number;
  day: number;
  hour?: number;
  minute?: number;
  latitude: number;
  longitude: number;
  timezone?: number;
  name?: string;
} | null) {
  return useQuery({
    queryKey: ["natal-chart", params],
    queryFn: () => params ? fetchNatalChart(params) : null,
    enabled: !!params,
    staleTime: Infinity, // Birth chart never changes
  });
}

// ============ UTILITY FUNCTIONS ============

export function getUpcomingMoonPhases(phases: MoonPhase[], count: number = 4): MoonPhase[] {
  const today = new Date().toISOString().split("T")[0];
  return phases.filter((p) => p.date >= today).slice(0, count);
}

export function getRecentTransits(transits: YearTransits, days: number = 30): TransitEvent[] {
  const today = new Date();
  const cutoff = new Date(today.getTime() - days * 24 * 60 * 60 * 1000);
  const cutoffStr = cutoff.toISOString().split("T")[0];
  const todayStr = today.toISOString().split("T")[0];
  
  const all = [...transits.ingresses, ...transits.retrogrades, ...transits.aspects];
  return all
    .filter((t) => t.date >= cutoffStr && t.date <= todayStr)
    .sort((a, b) => b.date.localeCompare(a.date));
}

export function getUpcomingTransits(transits: YearTransits, days: number = 30): TransitEvent[] {
  const today = new Date();
  const future = new Date(today.getTime() + days * 24 * 60 * 60 * 1000);
  const todayStr = today.toISOString().split("T")[0];
  const futureStr = future.toISOString().split("T")[0];
  
  const all = [...transits.ingresses, ...transits.retrogrades, ...transits.aspects];
  return all
    .filter((t) => t.date > todayStr && t.date <= futureStr)
    .sort((a, b) => a.date.localeCompare(b.date));
}
