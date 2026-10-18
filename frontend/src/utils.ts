import type { Bus } from "./api";
export const inr = (n: number) => new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(n);
export const duration = (m?: number | null) => (m == null ? "—" : `${Math.floor(m / 60)}h ${m % 60}m`);
export function departureKey(b: Bus): number {
  const m = /^(\d{1,2}):(\d{2})\s*(AM|PM)$/i.exec(b.schedule.departure_time.trim());
  if (!m) return Number.MAX_SAFE_INTEGER;
  const h = (Number(m[1]) % 12) + (m[3].toUpperCase() === "PM" ? 12 : 0);
  return Date.parse(b.schedule.departure_date) + (h * 60 + Number(m[2])) * 60000;
}
export interface Filters { ac: "all" | "ac" | "nonac"; seat: "all" | "sleeper" | "seater"; sort: "none" | "price" | "departure" }
export function applyFilters(buses: Bus[], f: Filters): Bus[] {
  let r = buses.filter(b =>
    (f.ac === "all" || (f.ac === "ac") === b.is_ac) &&
    (f.seat === "all" || (b.bus_seat_type ?? "").toLowerCase() === f.seat));
  if (f.sort === "price") r = [...r].sort((a, b) => a.pricing.total_fare - b.pricing.total_fare);
  if (f.sort === "departure") r = [...r].sort((a, b) => departureKey(a) - departureKey(b));
  return r;
}
