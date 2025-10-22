import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.models.filtering_models import Base
from src.api.crop_routes import get_db

# Setup test database
TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost/test_crop_taxonomy"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="session")
def session_fixture():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(name="client")
def client_fixture(session):
    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

def test_search_endpoint(client):
    """Test POST /search endpoint with a valid request."""
    request_data = {
        "crop_type": "corn",
        "maturity_days_min": 90,
        "maturity_days_max": 120,
        "pest_resistance": [
            {"pest_name": "corn_borer", "min_resistance_level": "resistant"}
        ],
        "min_yield_stability": 80,
        "page": 1,
        "page_size": 20
    }
    response = client.post("/api/v1/crop-taxonomy/search", json=request_data)

    assert response.status_code == 200
    response_data = response.json()
    assert "varieties" in response_data
    assert "total_count" in response_data
    assert "page" in response_data
    assert "page_size" in response_data
    assert "total_pages" in response_data
    assert "filters_applied" in response_data
    assert "search_time_ms" in response_data
    assert isinstance(response_data["varieties"], list)
    assert isinstance(response_data["total_count"], int)
    assert response_data["page"] == 1
    assert response_data["page_size"] == 20

