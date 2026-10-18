"""Internal Vercel service for the mock GDS supplier endpoint."""
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.services import mock_gds_service  # noqa: E402

app = FastAPI(title="RightBus Mock GDS")


@app.get("/mock-gds/search")
def mock_gds_search(
    source: str = Query(...),
    destination: str = Query(...),
    journey_date: str = Query(...),
):
    """Return the static supplier response; RightBus applies search filters."""
    try:
        return mock_gds_service.load_dataset()
    except mock_gds_service.DatasetError as exc:
        raise HTTPException(500, "Mock GDS data unavailable") from exc
