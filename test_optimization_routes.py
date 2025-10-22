import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from services.fertilizer_application.main import app
from services.fertilizer_application.src.database.fertilizer_db import Base, get_db

# Setup for in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="session")
def session_fixture():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(name="client")
def client_fixture(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

def test_optimize_fertilizer(client: TestClient):
    optimization_data = {
        "crop": "corn",
        "soil_type": "loam",
        "area": 100,
        "current_nutrients": {"N": 10, "P": 5, "K": 8},
        "budget": 500,
        "environmental_impact_preference": "low"
    }
    response = client.post("/optimize", json=optimization_data)
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert "total_cost" in data
    assert "environmental_impact" in data
    assert isinstance(data["recommendations"], list)
    assert data["total_cost"] >= 0
    assert data["environmental_impact"] in ["low", "medium", "high"]