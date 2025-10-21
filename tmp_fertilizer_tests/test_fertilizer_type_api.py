import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from services.fertilizer_application.main import app
from services.fertilizer_application.src.database.fertilizer_db import Base, get_db
from services.fertilizer_application.src.models.fertilizer_type_models import FertilizerType, FertilizerTypeEnum, EnvironmentalImpactEnum
from services.fertilizer_application.src.schemas.fertilizer_type_schemas import FertilizerTypeCreate, NPKRatio

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

def test_create_fertilizer_type_api(client: TestClient):
    npk = {"N": 10, "P": 10, "K": 10}
    fertilizer_data = {
        "name": "API Test Fertilizer",
        "type": "synthetic",
        "npk_ratio": npk,
        "cost_per_unit": 1.5,
        "unit": "kg",
        "environmental_impact_score": "medium",
        "release_rate": "fast",
        "organic_certified": False,
        "application_methods": ["broadcast"]
    }
    response = client.post("/api/v1/fertilizer-types/", json=fertilizer_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "API Test Fertilizer"
    assert data["type"] == "synthetic"
    assert data["npk_ratio"] == {"N": 10.0, "P": 10.0, "K": 10.0}

def test_create_fertilizer_type_api_duplicate_name(client: TestClient):
    npk = {"N": 10, "P": 10, "K": 10}
    fertilizer_data = {
        "name": "Duplicate API Fertilizer",
        "type": "synthetic",
        "npk_ratio": npk,
        "cost_per_unit": 1.5,
        "unit": "kg",
        "environmental_impact_score": "medium",
        "release_rate": "fast",
        "organic_certified": False,
        "application_methods": ["broadcast"]
    }
    client.post("/api/v1/fertilizer-types/", json=fertilizer_data)
    response = client.post("/api/v1/fertilizer-types/", json=fertilizer_data)
    assert response.status_code == 400
    assert "Fertilizer type with this name already exists." in response.json()["detail"]

def test_get_all_fertilizer_types_api(client: TestClient):
    npk = {"N": 10, "P": 10, "K": 10}
    fertilizer_data1 = {
        "name": "API Fert 1",
        "type": "synthetic",
        "npk_ratio": npk,
        "cost_per_unit": 1.0,
        "unit": "kg",
        "environmental_impact_score": "low",
        "release_rate": "fast",
        "organic_certified": False,
        "application_methods": ["broadcast"]
    }
    fertilizer_data2 = {
        "name": "API Fert 2",
        "type": "organic",
        "npk_ratio": npk,
        "cost_per_unit": 2.0,
        "unit": "lb",
        "environmental_impact_score": "medium",
        "release_rate": "slow",
        "organic_certified": True,
        "application_methods": ["foliar"]
    }
    client.post("/api/v1/fertilizer-types/", json=fertilizer_data1)
    client.post("/api/v1/fertilizer-types/", json=fertilizer_data2)

    response = client.get("/api/v1/fertilizer-types/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(f["name"] == "API Fert 1" for f in data)
    assert any(f["name"] == "API Fert 2" for f in data)

def test_get_fertilizer_type_api(client: TestClient):
    npk = {"N": 10, "P": 10, "K": 10}
    fertilizer_data = {
        "name": "Get API Fert",
        "type": "synthetic",
        "npk_ratio": npk,
        "cost_per_unit": 1.5,
        "unit": "kg",
        "environmental_impact_score": "medium",
        "release_rate": "fast",
        "organic_certified": False,
        "application_methods": ["broadcast"]
    }
    post_response = client.post("/api/v1/fertilizer-types/", json=fertilizer_data)
    created_id = post_response.json()["id"]

    get_response = client.get(f"/api/v1/fertilizer-types/{created_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["name"] == "Get API Fert"

def test_get_fertilizer_type_api_not_found(client: TestClient):
    response = client.get("/api/v1/fertilizer-types/999")
    assert response.status_code == 404
    assert "Fertilizer type not found" in response.json()["detail"]

def test_update_fertilizer_type_api(client: TestClient):
    npk = {"N": 10, "P": 10, "K": 10}
    fertilizer_data = {
        "name": "Update API Fert",
        "type": "synthetic",
        "npk_ratio": npk,
        "cost_per_unit": 1.5,
        "unit": "kg",
        "environmental_impact_score": "medium",
        "release_rate": "fast",
        "organic_certified": False,
        "application_methods": ["broadcast"]
    }
    post_response = client.post("/api/v1/fertilizer-types/", json=fertilizer_data)
    created_id = post_response.json()["id"]

    update_data = {"name": "Updated API Fert Name", "cost_per_unit": 2.0, "organic_certified": True}
    put_response = client.put(f"/api/v1/fertilizer-types/{created_id}", json=update_data)
    assert put_response.status_code == 200
    data = put_response.json()
    assert data["name"] == "Updated API Fert Name"
    assert data["cost_per_unit"] == 2.0
    assert data["organic_certified"] is True

def test_update_fertilizer_type_api_not_found(client: TestClient):
    update_data = {"name": "Non Existent", "cost_per_unit": 2.0}
    response = client.put("/api/v1/fertilizer-types/999", json=update_data)
    assert response.status_code == 404
    assert "Fertilizer type not found" in response.json()["detail"]

def test_delete_fertilizer_type_api(client: TestClient):
    npk = {"N": 10, "P": 10, "K": 10}
    fertilizer_data = {
        "name": "Delete API Fert",
        "type": "synthetic",
        "npk_ratio": npk,
        "cost_per_unit": 1.5,
        "unit": "kg",
        "environmental_impact_score": "medium",
        "release_rate": "fast",
        "organic_certified": False,
        "application_methods": ["broadcast"]
    }
    post_response = client.post("/api/v1/fertilizer-types/", json=fertilizer_data)
    created_id = post_response.json()["id"]

    delete_response = client.delete(f"/api/v1/fertilizer-types/{created_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/fertilizer-types/{created_id}")
    assert get_response.status_code == 404

def test_delete_fertilizer_type_api_not_found(client: TestClient):
    response = client.delete("/api/v1/fertilizer-types/999")
    assert response.status_code == 404
    assert "Fertilizer type not found" in response.json()["detail"]

def test_compare_fertilizer_types_api(client: TestClient):
    npk1 = {"N": 10, "P": 10, "K": 10}
    fertilizer_data1 = {
        "name": "Compare API Fert 1",
        "type": "synthetic",
        "npk_ratio": npk1,
        "cost_per_unit": 1.0,
        "unit": "kg",
        "environmental_impact_score": "low",
        "release_rate": "fast",
        "organic_certified": False,
        "application_methods": ["broadcast"]
    }
    npk2 = {"N": 5, "P": 15, "K": 5}
    fertilizer_data2 = {
        "name": "Compare API Fert 2",
        "type": "organic",
        "npk_ratio": npk2,
        "cost_per_unit": 2.0,
        "unit": "lb",
        "environmental_impact_score": "medium",
        "release_rate": "slow",
        "organic_certified": True,
        "application_methods": ["foliar"]
    }
    post_response1 = client.post("/api/v1/fertilizer-types/", json=fertilizer_data1)
    created_id1 = post_response1.json()["id"]
    post_response2 = client.post("/api/v1/fertilizer-types/", json=fertilizer_data2)
    created_id2 = post_response2.json()["id"]

    compare_response = client.post("/api/v1/fertilizer-types/compare", json=[created_id1, created_id2])
    assert compare_response.status_code == 200
    data = compare_response.json()
    assert len(data) == 2
    assert any(f["name"] == "Compare API Fert 1" for f in data)
    assert any(f["name"] == "Compare API Fert 2" for f in data)

def test_compare_fertilizer_types_api_not_found(client: TestClient):
    compare_response = client.post("/api/v1/fertilizer-types/compare", json=[999])
    assert compare_response.status_code == 404
    assert "No fertilizer types found for comparison" in compare_response.json()["detail"]