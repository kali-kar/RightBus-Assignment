import httpx
import os
from app.core.config import GDS_BASE_URL, GDS_TIMEOUT_SECONDS
from app.services.mock_gds_service import DatasetError, load_dataset


class GdsError(Exception):
    pass


def fetch_gds(source: str, destination: str, journey_date: str) -> dict:
    """Real HTTP call: RightBus backend -> GET /mock-gds/search."""
    # Vercel runs each request in a serverless function, so calling the same
    # deployment over HTTP is unreliable. Load the bundled mock supplier data
    # directly there; local and container deployments retain the HTTP behavior.
    if os.getenv("VERCEL"):
        try:
            return load_dataset()
        except DatasetError as exc:
            raise GdsError(str(exc)) from exc
    try:
        r = httpx.get(
            f"{GDS_BASE_URL}/mock-gds/search",
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
