# RightBus

RightBus is a bus search demo website. Search available buses by origin, destination, and journey date, then compare operators, bus types, departure and arrival times, fares, and available seats. Each result shows the first two boarding stops and last two dropping stops in a compact route line; hover over the line to reveal the complete route. Open **View Details** for boarding and dropping point information, amenities, fares, and cancellation details.

## Technologies

- Frontend: React, TypeScript, and Vite
- Backend: Python, FastAPI, and Pydantic
- Supplier demo: a static mock GDS response in `backend/data/mock_gds_response.json`
- Tests: Vitest and React Testing Library for the frontend; pytest for the backend

## Setup

Requirements: Node.js and npm, plus Python 3.10 or newer.

Install backend dependencies and start the API:

```bash
cd backend
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux:       source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

In another terminal, install frontend dependencies and start Vite:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite. During development, Vite proxies `/api` requests to the backend at `http://127.0.0.1:8000`.

## Search API

| Method and path | Purpose |
| --- | --- |
| `GET /api/buses/search?source=Bangalore&destination=Mumbai&journey_date=2026-08-09` | Search and filter bus trips by route and date. |
| `GET /mock-gds/search?source=...&destination=...&journey_date=...` | Return the mock supplier dataset. |
| `GET /health` | Return the API health status. |

The search endpoint requires `source`, `destination`, and `journey_date` in `YYYY-MM-DD` format. It returns the matching bus records and a result count. FastAPI's interactive API documentation is available at `/docs` while the backend is running.

## How the mock GDS works

The mock GDS is a local JSON file containing sample supplier data. Its endpoint returns that payload; the RightBus search service then applies the requested route and date to the structured trip fields. Route matching trims whitespace and ignores letter case when comparing `from_city_name` and `to_city_name`. The service matches `schedule.departure_date` exactly and excludes unavailable trips and trips with no seats. `route_name` is display data and is not used for matching.

For local and Docker runs, the backend calls `/mock-gds/search` over HTTP. On Vercel, the serverless function reads the bundled dataset directly, avoiding a network request back to the same deployment.

## Filtering and route display

Use the result controls to filter for AC or non-AC buses, sleeper or seater buses, and sort by fare or earliest departure. Reset filters restores the full result list. The route line shows the first two boarding points followed by the last two dropping points, with theme-blue arrows between stops. Hover over the line to reveal the full names and route.

## Tests

Run backend tests and validate the sample dataset:

```bash
cd backend
pytest
python scripts/validate_dataset.py
```

Run frontend tests:

```bash
cd frontend
npm test
```

## Vercel deployment

Import the repository into Vercel with the project root set to this folder. The root `vercel.json` builds the Vite frontend and routes API requests to the FastAPI function. The demo needs no environment variables.
