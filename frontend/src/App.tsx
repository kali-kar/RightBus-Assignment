import { useRef, useState } from "react";
import { ArrowLeftRight, Search, X, Bus as BusIcon } from "lucide-react";
import { searchBuses, type Bus, type Point } from "./api";
import { applyFilters, duration, inr, type Filters } from "./utils";

type State = { kind: "idle" } | { kind: "loading" } | { kind: "error"; msg: string } | { kind: "done"; buses: Bus[] };
const CITIES = ["Bangalore", "Mumbai", "Delhi", "Chennai", "Hyderabad", "Pune"];
const noFilters: Filters = { ac: "all", seat: "all", sort: "none" };

function otherAmenities(amenities: string[]) {
  return amenities.filter(amenity => {
    const normalized = amenity.replace(/[^a-z]/gi, "").toLowerCase();
    return normalized !== "ac" && normalized !== "nonac";
  });
}

function Points({ title, pts }: { title: string; pts: Point[] }) {
  return (<section><h4>{title}</h4><ul>{pts.map((p, i) => (
    <li key={i}><strong>{p.time}</strong> — {p.name}{p.is_nearest && <em className="tag">Nearest</em>}
      <small>{p.distance_km != null && ` · ${p.distance_km} km`}{p.contact && p.contact !== "0" && ` · ${p.contact}`}</small></li>))}</ul></section>);
}

function StopSummary({ bus }: { bus: Bus }) {
  const stops = [...bus.boarding_points.slice(0, 2), ...bus.dropping_points.slice(-2)];
  if (!stops.length) return null;
  return <div className="stop-summary" aria-label="First boarding and last dropping stops" title={stops.map(point => point.name).join(" → ")}>
    {stops.map((point, index) => <span className="stop-segment" key={`${point.name}-${index}`}>
      {index > 0 && <span className="stop-arrow" aria-hidden="true">→</span>}
      <span>{point.name}</span>
    </span>)}
  </div>;
}

function Details({ bus, onClose }: { bus: Bus; onClose: () => void }) {
  const c = bus.cancellation_policy;
  return (<div className="overlay" onClick={onClose} onKeyDown={e => e.key === "Escape" && onClose()}>
    <div className="modal" role="dialog" aria-modal="true" aria-label="Bus details" onClick={e => e.stopPropagation()}>
      <button className="close" aria-label="Close details" autoFocus onClick={onClose}><X /></button>
      <h3>{bus.operator}</h3><p>{bus.bus_type} · {bus.amenities.join(", ")}</p>
      <p>Fare: {inr(bus.pricing.base_fare)} + tax {inr(bus.pricing.service_tax)} + surcharges {inr(bus.pricing.surcharges)} = <b>{inr(bus.pricing.total_fare)}</b></p>
      <p>Seats available: {bus.availability.seats_available}</p>
      {c && <p>Cancellable: {c.is_cancellable ? "Yes" : "No"} · Reschedule: {c.reschedule_allowed ? `Yes (charge ${inr(c.reschedule_charge ?? 0)})` : "No"}</p>}
      <Points title="Boarding points" pts={bus.boarding_points} /><Points title="Dropping points" pts={bus.dropping_points} />
    </div></div>);
}

export default function App() {
  const [source, setSource] = useState("Bangalore");
  const [destination, setDestination] = useState("Mumbai");
  const [date, setDate] = useState("2026-08-09");
  const [formErr, setFormErr] = useState("");
  const [state, setState] = useState<State>({ kind: "idle" });
  const [filters, setFilters] = useState<Filters>(noFilters);
  const [selected, setSelected] = useState<Bus | null>(null);
  const abort = useRef<AbortController | null>(null);

  async function submit(e?: React.FormEvent) {
    e?.preventDefault();
    const s = source.trim(), d = destination.trim();
    if (!s || !d || !date) return setFormErr("Please fill in source, destination and journey date.");
    if (s.toLowerCase() === d.toLowerCase()) return setFormErr("Source and destination must be different.");
    setFormErr(""); abort.current?.abort();
    const ctl = (abort.current = new AbortController());
    setState({ kind: "loading" });
    try {
      const r = await searchBuses(s, d, date, ctl.signal);
      if (!ctl.signal.aborted) setState({ kind: "done", buses: r.buses });
    } catch (err) {
      if (!ctl.signal.aborted) setState({ kind: "error", msg: err instanceof Error ? err.message : "Something went wrong." });
    }
  }

  const shown = state.kind === "done" ? applyFilters(state.buses, filters) : [];
  return (<>
    <header><img src="/logo.png" alt="RightBus" /><span className="demo">Demo search</span></header>
    <section className="hero"><h1>Your Journey Starts Here</h1><p>Find your next bus journey with a simple, seamless search.</p>
      <form onSubmit={submit} noValidate>
        <label>From<input list="cities" value={source} onChange={e => setSource(e.target.value)} /></label>
        <button type="button" aria-label="Swap cities" onClick={() => { setSource(destination); setDestination(source); }}><ArrowLeftRight /></button>
        <label>To<input list="cities" value={destination} onChange={e => setDestination(e.target.value)} /></label>
        <label>Journey date<input type="date" value={date} onChange={e => setDate(e.target.value)} /></label>
        <button className="primary" disabled={state.kind === "loading"}><Search /> {state.kind === "loading" ? "Searching…" : "Search Buses"}</button>
        <datalist id="cities">{CITIES.map(c => <option key={c} value={c} />)}</datalist>
      </form>
      {formErr && <p role="alert" className="err">{formErr}</p>}
      <p className="hint">The demo dataset only contains Bangalore → Mumbai trips on 2026-08-09.</p>
    </section>
    <main>
      {state.kind === "idle" && <p className="center"><BusIcon /> Enter a route and date to see buses.</p>}
      {state.kind === "loading" && <div aria-busy="true">{[1, 2, 3].map(i => <div key={i} className="card skeleton" />)}</div>}
      {state.kind === "error" && <div role="alert" className="center"><p>{state.msg}</p><button onClick={() => submit()}>Retry</button></div>}
      {state.kind === "done" && state.buses.length === 0 && <div className="center"><h3>No buses found</h3><p>Check the route or try another journey date.</p></div>}
      {state.kind === "done" && state.buses.length > 0 && (<>
        <h2>{source} → {destination} · {date} · {shown.length} of {state.buses.length} buses</h2>
        <div className="filters">
          <select aria-label="AC filter" value={filters.ac} onChange={e => setFilters({ ...filters, ac: e.target.value as Filters["ac"] })}><option value="all">AC / Non-AC</option><option value="ac">AC</option><option value="nonac">Non-AC</option></select>
          <select aria-label="Seat type filter" value={filters.seat} onChange={e => setFilters({ ...filters, seat: e.target.value as Filters["seat"] })}><option value="all">Sleeper / Seater</option><option value="sleeper">Sleeper</option><option value="seater">Seater</option></select>
          <select aria-label="Sort" value={filters.sort} onChange={e => setFilters({ ...filters, sort: e.target.value as Filters["sort"] })}><option value="none">Sort by…</option><option value="price">Price: low to high</option><option value="departure">Earliest departure</option></select>
          <button onClick={() => setFilters(noFilters)}>Reset filters</button>
        </div>
        {shown.length === 0 && <p className="center">No buses match these filters.</p>}
        {shown.map(b => (<article className="card bus-card" key={b.trip_id}>
          <div><h3>{b.operator}</h3><p>{b.bus_type}</p>
            <span className="badge">{b.is_ac ? "AC" : "Non-AC"}</span><span className="badge">{b.bus_seat_type}</span>
            {otherAmenities(b.amenities).length > 0 && <p className="amenities">{otherAmenities(b.amenities).join(" · ")}</p>}
          </div>
          <div className="bus-schedule">
            <div className="bus-timeline">
              <span><b>{b.schedule.departure_time}</b> {b.from_city_name}</span>
              <small>{duration(b.schedule.duration_minutes)}</small>
              <span><b>{b.schedule.arrival_time}</b> {b.to_city_name}{b.schedule.estimated_arrival_date !== b.schedule.departure_date && <small> ({b.schedule.estimated_arrival_date})</small>}</span>
            </div>
            <StopSummary bus={b} />
          </div>
          <div><p className="fare">{inr(b.pricing.total_fare)}</p><p>{b.availability.seats_available} seats left</p>
            <button onClick={() => setSelected(b)}>View Details</button></div>
        </article>))}</>)}
    </main>
    {selected && <Details bus={selected} onClose={() => setSelected(null)} />}
    <footer>RightBus is a demo application. Fares and availability come from a static mock GDS dataset; no real booking is possible.</footer>
  </>);
}
