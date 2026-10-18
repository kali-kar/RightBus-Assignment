import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.routes import get_gds_fetcher
from app.services.mock_gds_service import load_dataset


@pytest.fixture
def client():
    # Tests call the mock GDS data layer directly (no live HTTP server); /mock-gds/search is tested separately.
    app.dependency_overrides[get_gds_fetcher] = lambda: (lambda s, d, j: load_dataset())
    yield TestClient(app)
    app.dependency_overrides.clear()
