import logging
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from app.models.bus import BusSearchResponse, Bus, SearchParams
from app.services import mock_gds_service, bus_search_service
from app.services.gds_client import fetch_gds, GdsError

log = logging.getLogger("rightbus")
router = APIRouter()


def get_gds_fetcher():
    return fetch_gds  # overridden in tests


@router.get("/mock-gds/search", tags=["Mock GDS"])
def mock_gds_search(source: str = Query(...), destination: str = Query(...), journey_date: str = Query(...)):
    """Returns the supplied static GDS payload; filtering is the RightBus backend's job."""
    try:
        return mock_gds_service.load_dataset()
    except mock_gds_service.DatasetError:
        log.exception("Mock GDS dataset failure")
        raise HTTPException(500, "Mock GDS data unavailable")


@router.get("/api/buses/search", response_model=BusSearchResponse, tags=["RightBus"])
def search_buses(source: str = Query(...), destination: str = Query(...), journey_date: str = Query(...),
                 fetcher=Depends(get_gds_fetcher)):
    source, destination, journey_date = source.strip(), destination.strip(), journey_date.strip()
    if not source or not destination:
        raise HTTPException(400, "Source and destination are required.")
    if source.casefold() == destination.casefold():
        raise HTTPException(400, "Source and destination must be different cities.")
    try:
        date.fromisoformat(journey_date)
        if len(journey_date) != 10:
            raise ValueError
    except ValueError:
        raise HTTPException(422, "journey_date must be a valid date in YYYY-MM-DD format.")
    try:
        gds = fetcher(source, destination, journey_date)
        trips = bus_search_service.filter_trips(gds["trips"], source, destination, journey_date)
        buses = [Bus.model_validate(t) for t in trips]
    except GdsError:
        log.exception("GDS call failed")
        raise HTTPException(502, "Bus supplier is temporarily unavailable.")
    except ValueError:  # pydantic ValidationError subclasses ValueError
        log.exception("Malformed trip record")
        raise HTTPException(502, "Bus supplier returned invalid data.")
    return BusSearchResponse(
        message="Buses retrieved successfully" if buses else "No buses found for this search",
        search=SearchParams(source=source, destination=destination, journey_date=journey_date),
        count=len(buses), buses=buses)
