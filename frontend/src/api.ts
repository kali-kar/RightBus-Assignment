export interface Point { name: string; time?: string | null; contact?: string | null; distance_km?: number | null; is_nearest: boolean }
export interface Bus {
  trip_id: string; operator: string; bus_type: string; bus_seat_type?: string | null; is_ac: boolean;
  amenities: string[]; from_city_name: string; to_city_name: string;
  schedule: { departure_time: string; arrival_time: string; departure_date: string; estimated_arrival_date?: string | null; duration_minutes?: number | null };
  pricing: { base_fare: number; service_tax: number; surcharges: number; total_fare: number };
  availability: { seats_available: number };
  boarding_points: Point[]; dropping_points: Point[];
  cancellation_policy?: { is_cancellable?: boolean; reschedule_allowed?: boolean; reschedule_charge?: number } | null;
}
export interface SearchResponse { count: number; buses: Bus[] }

const BASE = import.meta.env.VITE_API_BASE_URL ?? "";

// The frontend only ever talks to the RightBus backend, never /mock-gds.
export async function searchBuses(source: string, destination: string, journey_date: string, signal?: AbortSignal): Promise<SearchResponse> {
  const qs = new URLSearchParams({ source, destination, journey_date });
  const res = await fetch(`${BASE}/api/buses/search?${qs}`, { signal });
  let body: unknown;
  try { body = await res.json(); } catch { throw new Error("Unexpected response from server."); }
  if (!res.ok) throw new Error((body as { detail?: string }).detail ?? "Search failed.");
  return body as SearchResponse;
}
