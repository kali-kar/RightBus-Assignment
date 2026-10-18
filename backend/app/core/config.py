import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATASET_PATH = Path(os.getenv("DATASET_PATH", BASE_DIR / "data" / "mock_gds_response.json"))
FRONTEND_DIST = Path(os.getenv("FRONTEND_DIST", BASE_DIR.parent / "frontend" / "dist"))
# Where the RightBus backend reaches the Mock GDS over HTTP. Single-service default = itself.
GDS_BASE_URL = os.getenv("GDS_BASE_URL", f"http://127.0.0.1:{os.getenv('PORT', '8000')}")
GDS_TIMEOUT_SECONDS = float(os.getenv("GDS_TIMEOUT_SECONDS", "10"))
