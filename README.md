# RightBus — Full-Stack Bus Search (demo)

React + TypeScript (Vite) → FastAPI **RightBus backend** → **Mock GDS** (`/mock-gds/search`) → `backend/data/mock_gds_response.json`.
The frontend only calls `/api/buses/search`; the backend calls the mock GDS over real HTTP (`GDS_BASE_URL`, default = itself on `$PORT`).

## Run locally
```bash
cd backend && python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --port 8000          # docs at /docs
# second terminal
cd frontend && npm install && npm run dev  # proxies /api to :8000
```
## Tests
`cd backend && pytest` (API tests override the GDS fetcher with the dataset loader; no live server needed) · `python scripts/validate_dataset.py` · `cd frontend && npm test`

## Production
`docker build -t rightbus . && docker run -p 8000:8000 rightbus` (FastAPI serves the built React app). Health check: `/health`.
Env vars: `PORT`, `GDS_BASE_URL`, `GDS_TIMEOUT_SECONDS`, `DATASET_PATH`, `FRONTEND_DIST`, `VITE_API_BASE_URL`.

## Deploy to Vercel
This folder is configured as a single Vercel project: Vercel builds the Vite frontend as static output and serves the FastAPI endpoints through a Python function. The function bundles `backend/data/mock_gds_response.json` and reads that dataset directly, avoiding a serverless function making an HTTP request back to its own deployment.

1. Push this folder to a Git provider and import the repository into Vercel.
2. Keep the Vercel project root set to the repository root (do not set it to `frontend`).
3. Deploy with the default build settings from `vercel.json`. No environment variables are required for the demo.

Vercel uses the root `requirements.txt` for the Python function. `/api/buses/search`, `/mock-gds/search`, and `/health` are routed to FastAPI; the built frontend and its assets are served from `frontend/dist`.

## Matching rules
Source/destination: trimmed, case-insensitive equality on `from_city_name`/`to_city_name`. **`route_name` is never used** (the data has deliberately wrong values such as "Bangalore To Jaisalmer"). Date: exact match on `schedule.departure_date`. Excluded: `is_available != true` or `seats_available <= 0`. Booking tokens are stripped.

## Status codes
200 (incl. empty results) · 400 blank/identical cities · 422 missing params or bad date · 502 GDS failure/malformed data.

## Dataset
Extracted from the assignment PDF by `backend/scripts/extract_dataset.py` (5 trips, all Bangalore → Mumbai on 2026-08-09). Note trip TRP-128475 has `is_ac: true` with "NON AC" in its bus type; the UI uses the boolean.
