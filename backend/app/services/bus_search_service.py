"""Route/date/availability filtering. Pure functions on plain dicts (no framework needed)."""
from typing import Any

KEEP = ["trip_id", "operator", "bus_type", "bus_type_name", "bus_seat_type", "is_ac", "amenities",
        "from_city_name", "to_city_name", "route_name", "schedule", "pricing", "availability",
        "boarding_points", "dropping_points", "proximity_info", "cancellation_policy"]


def norm(value: Any) -> str:
    return str(value or "").strip().casefold()


def filter_trips(trips: list, source: str, destination: str, journey_date: str) -> list[dict]:
    """Match on structured fields only. route_name is display-only and never used for matching."""
    src, dst, result = norm(source), norm(destination), []
    for t in trips:
        if not isinstance(t, dict):
            continue
        sched, avail = t.get("schedule") or {}, t.get("availability") or {}
        if norm(t.get("from_city_name")) != src or norm(t.get("to_city_name")) != dst:
            continue
        if sched.get("departure_date") != journey_date:
            continue
        seats = avail.get("seats_available")
        if avail.get("is_available") is not True or not isinstance(seats, int) or seats <= 0:
            continue
        result.append({k: t.get(k) for k in KEEP})  # booking_token intentionally dropped
    return result
