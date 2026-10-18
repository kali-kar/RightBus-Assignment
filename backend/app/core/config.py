import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATASET_PATH = Path(os.getenv("DATASET_PATH", BASE_DIR / "data" / "mock_gds_response.json"))
FRONTEND_DIST = Path(os.getenv("FRONTEND_DIST", BASE_DIR.parent / "frontend" / "dist"))
# Vercel injects GDS_SERVICE_URL as a service binding. Local and Docker runs
# retain the single-service localhost default unless GDS_BASE_URL is provided.
GDS_BASE_URL = os.getenv(
    "GDS_SERVICE_URL",
    os.getenv("GDS_BASE_URL", f"http://127.0.0.1:{os.getenv('PORT', '8000')}"),
)
GDS_TIMEOUT_SECONDS = float(os.getenv("GDS_TIMEOUT_SECONDS", "10"))
