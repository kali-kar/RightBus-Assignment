import pytest
from app.api.routes import get_gds_fetcher
from app.main import app
from app.services.bus_search_service import filter_trips
from app.services.gds_client import GdsError

URL = "/api/buses/search"
D = "2026-08-09"


def test_bangalore_mumbai(client):
    r = client.get(URL, params={"source": "Bangalore", "destination": "Mumbai", "journey_date": D})
    assert r.status_code == 200
    body = r.json()
    assert body["count"] == len(body["buses"]) == 5
    for b in body["buses"]:
        assert b["from_city_name"] == "Bangalore" and b["to_city_name"] == "Mumbai"
        assert b["schedule"]["departure_date"] == D and b["availability"]["seats_available"] > 0
        assert "booking_token" not in b
    # inconsistent route_name trips are still included
    assert any("Jaisalmer" in b["route_name"] for b in body["buses"])


def test_bangalore_delhi_empty(client):
    r = client.get(URL, params={"source": "Bangalore", "destination": "Delhi", "journey_date": D})
    assert r.status_code == 200 and r.json()["count"] == 0


def test_missing_source(client):
    assert client.get(URL, params={"destination": "Mumbai", "journey_date": D}).status_code == 422


def test_missing_destination(client):
    assert client.get(URL, params={"source": "Bangalore", "journey_date": D}).status_code == 422


def test_same_city(client):
    r = client.get(URL, params={"source": "Bangalore", "destination": " bangalore ", "journey_date": D})
    assert r.status_code == 400 and "different" in r.json()["detail"]


@pytest.mark.parametrize("d", ["09-08-2026", "2026-02-30", "abc"])
def test_bad_dates(client, d):
    assert client.get(URL, params={"source": "A", "destination": "B", "journey_date": d}).status_code == 422


def test_blank_source(client):
    assert client.get(URL, params={"source": "  ", "destination": "Mumbai", "journey_date": D}).status_code == 400


def test_case_and_whitespace(client):
    r = client.get(URL, params={"source": "  bangalore", "destination": "MUMBAI ", "journey_date": D})
    assert r.json()["count"] == 5


def test_other_date_empty(client):
    r = client.get(URL, params={"source": "Bangalore", "destination": "Mumbai", "journey_date": "2026-08-10"})
    assert r.status_code == 200 and r.json()["count"] == 0


def test_unavailable_and_zero_seats_excluded():
    base = {"from_city_name": "A", "to_city_name": "B", "schedule": {"departure_date": D}}
    trips = [{**base, "availability": {"is_available": False, "seats_available": 5}},
             {**base, "availability": {"is_available": True, "seats_available": 0}},
             {**base, "availability": {"is_available": True, "seats_available": 2}}]
    assert len(filter_trips(trips, "a", "b", D)) == 1


def test_gds_failure_returns_502(client):
    def boom(*a):
        raise GdsError("down")
    app.dependency_overrides[get_gds_fetcher] = lambda: boom
    r = client.get(URL, params={"source": "Bangalore", "destination": "Mumbai", "journey_date": D})
    assert r.status_code == 502


def test_malformed_gds_record_returns_502(client):
    app.dependency_overrides[get_gds_fetcher] = lambda: (lambda *a: {"trips": [{
        "from_city_name": "Bangalore", "to_city_name": "Mumbai", "schedule": {"departure_date": D},
        "availability": {"is_available": True, "seats_available": 3}}]})
    r = client.get(URL, params={"source": "Bangalore", "destination": "Mumbai", "journey_date": D})
    assert r.status_code == 502


def test_mock_gds_and_health(client):
    r = client.get("/mock-gds/search", params={"source": "x", "destination": "y", "journey_date": D})
    assert r.status_code == 200 and len(r.json()["trips"]) == 5
    assert client.get("/health").json() == {"status": "ok"}
