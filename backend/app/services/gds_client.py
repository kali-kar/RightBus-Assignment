import httpx
from app.core.config import GDS_BASE_URL, GDS_TIMEOUT_SECONDS


class GdsError(Exception):
    pass


def fetch_gds(source: str, destination: str, journey_date: str) -> dict:
    """Real HTTP call: RightBus backend -> GET /mock-gds/search."""
    try:
        r = httpx.get(
            f"{GDS_BASE_URL.rstrip('/')}/mock-gds/search",
            params={"source": source, "destination": destination, "journey_date": journey_date},
            timeout=GDS_TIMEOUT_SECONDS,
        )
        r.raise_for_status()
        data = r.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise GdsError(str(exc)) from exc
    if not isinstance(data, dict) or not isinstance(data.get("trips"), list):
        raise GdsError("Malformed GDS response")
    return data
