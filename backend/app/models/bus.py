from typing import Any, Optional
from pydantic import BaseModel, ConfigDict


class Schedule(BaseModel):
    departure_time: str
    arrival_time: str
    departure_date: str
    estimated_arrival_date: Optional[str] = None
    duration_minutes: Optional[int] = None


class Pricing(BaseModel):
    base_fare: float
    service_tax: float = 0
    surcharges: float = 0
    total_fare: float
    currency: str = "INR"


class Availability(BaseModel):
    seats_available: int
    is_available: bool
    seat_types: list[str] = []


class Point(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str
    time: Optional[str] = None
    contact: Optional[str] = None
    distance_km: Optional[float] = None
    is_nearest: bool = False


class Bus(BaseModel):
    model_config = ConfigDict(extra="ignore")
    trip_id: str
    operator: str
    bus_type: str
    bus_type_name: Optional[str] = None
    bus_seat_type: Optional[str] = None
    is_ac: bool
    amenities: list[str] = []
    from_city_name: str
    to_city_name: str
    route_name: Optional[str] = None  # display only
    schedule: Schedule
    pricing: Pricing
    availability: Availability
    boarding_points: list[Point] = []
    dropping_points: list[Point] = []
    proximity_info: Optional[dict[str, Any]] = None
    cancellation_policy: Optional[dict[str, Any]] = None


class SearchParams(BaseModel):
    source: str
    destination: str
    journey_date: str


class BusSearchResponse(BaseModel):
    success: bool = True
    message: str
    search: SearchParams
    count: int
    buses: list[Bus]
