import pytest
from fastapi.testclient import TestClient
from uuid import UUID, uuid4

from services.fertilizer_application.src.main import app
from services.fertilizer_application.src.models.fertilizer_type_models import (
    FertilizerType, FertilizerTypeEnum, FertilizerFormEnum, FertilizerReleaseTypeEnum,
    EnvironmentalImpactEnum, SuitabilityCriteria
)
from services.fertilizer_application.src.services.fertilizer_type_service import FertilizerTypeService

client = TestClient(app)

# --- Fixtures for testing ---

@pytest.fixture
def fertilizer_type_service_fixture():
    """Fixture for a fresh FertilizerTypeService instance."""
    return FertilizerTypeService()

@pytest.fixture
def sample_fertilizer_type_data():
    """Sample data for creating a fertilizer type."""
    return {
        "name": "SuperGrow NPK",
        "description": "A balanced NPK fertilizer for general use.",
        "npk_ratio": "15-15-15",
        "fertilizer_type": "synthetic",
        "form": "granular",
        "release_type": "quick",
        "cost_per_unit": 1.25,
        "unit": "USD/kg",
        "environmental_impact_score": "medium",
        "suitability_criteria": {
            "min_ph": 6.0,
            "max_ph": 7.0,
            "soil_types": ["loam"],
            "crop_types": ["corn", "soybean"]
        }
    }

@pytest.fixture
def another_fertilizer_type_data():
    """Another sample data for creating a fertilizer type."""
    return {
        "name": "Organic Boost",
        "description": "Organic liquid fertilizer for leafy greens.",
        "npk_ratio": "5-1-1",
        "fertilizer_type": "organic",
        "form": "liquid",
        "release_type": "quick",
        "cost_per_unit": 2.50,
        "unit": "USD/L",
        "environmental_impact_score": "low",
        "suitability_criteria": {
            "min_ph": 5.5,
            "max_ph": 6.5,
            "crop_types": ["lettuce", "spinach"]
        }
    }

# --- Tests for FertilizerType Model ---

def test_fertilizer_type_model_creation(sample_fertilizer_type_data):
    ft = FertilizerType(**sample_fertilizer_type_data)
    assert ft.name == "SuperGrow NPK"
    assert ft.npk_ratio == "15-15-15"
    assert ft.fertilizer_type == FertilizerTypeEnum.SYNTHETIC
    assert ft.suitability_criteria.min_ph == 6.0

def test_fertilizer_type_model_invalid_npk():
    invalid_data = {
        "name": "Test", "npk_ratio": "invalid", "fertilizer_type": "synthetic",
        "form": "granular", "release_type": "quick", "cost_per_unit": 1.0, "unit": "USD/kg",
        "environmental_impact_score": "medium"
    }
    with pytest.raises(ValueError):
        FertilizerType(**invalid_data)

# --- Tests for FertilizerTypeService ---

def test_service_get_all_fertilizer_types(fertilizer_type_service_fixture):
    types = fertilizer_type_service_fixture.get_all_fertilizer_types()
    assert len(types) == 3  # Default types
    assert any(ft.name == "Urea" for ft in types)

def test_service_get_fertilizer_type_by_id(fertilizer_type_service_fixture):
    urea_id = UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11")
    urea = fertilizer_type_service_fixture.get_fertilizer_type_by_id(urea_id)
    assert urea is not None
    assert urea.name == "Urea"

def test_service_create_fertilizer_type(fertilizer_type_service_fixture, sample_fertilizer_type_data):
    new_ft = FertilizerType(id=uuid4(), **sample_fertilizer_type_data)
    created_ft = fertilizer_type_service_fixture.create_fertilizer_type(new_ft)
    assert created_ft.id == new_ft.id
    assert fertilizer_type_service_fixture.get_fertilizer_type_by_id(new_ft.id) is not None

def test_service_create_fertilizer_type_duplicate_id(fertilizer_type_service_fixture, sample_fertilizer_type_data):
    existing_id = UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11") # Urea's ID
    duplicate_ft = FertilizerType(id=existing_id, **sample_fertilizer_type_data)
    with pytest.raises(ValueError, match=f"Fertilizer type with ID {existing_id} already exists."):
        fertilizer_type_service_fixture.create_fertilizer_type(duplicate_ft)

def test_service_update_fertilizer_type(fertilizer_type_service_fixture, sample_fertilizer_type_data):
    urea_id = UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11")
    updated_data = FertilizerType(id=urea_id, name="Updated Urea", **{k:v for k,v in sample_fertilizer_type_data.items() if k != 'name'})
    updated_ft = fertilizer_type_service_fixture.update_fertilizer_type(urea_id, updated_data)
    assert updated_ft.name == "Updated Urea"
    assert fertilizer_type_service_fixture.get_fertilizer_type_by_id(urea_id).name == "Updated Urea"

def test_service_update_fertilizer_type_not_found(fertilizer_type_service_fixture, sample_fertilizer_type_data):
    non_existent_id = uuid4()
    updated_data = FertilizerType(id=non_existent_id, **sample_fertilizer_type_data)
    updated_ft = fertilizer_type_service_fixture.update_fertilizer_type(non_existent_id, updated_data)
    assert updated_ft is None

def test_service_delete_fertilizer_type(fertilizer_type_service_fixture):
    urea_id = UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11")
    deleted = fertilizer_type_service_fixture.delete_fertilizer_type(urea_id)
    assert deleted is True
    assert fertilizer_type_service_fixture.get_fertilizer_type_by_id(urea_id) is None

def test_service_delete_fertilizer_type_not_found(fertilizer_type_service_fixture):
    non_existent_id = uuid4()
    deleted = fertilizer_type_service_fixture.delete_fertilizer_type(non_existent_id)
    assert deleted is False

def test_service_filter_fertilizer_types(fertilizer_type_service_fixture):
    # Filter by type
    organic_types = fertilizer_type_service_fixture.filter_fertilizer_types(fertilizer_type=FertilizerTypeEnum.ORGANIC)
    assert len(organic_types) == 2
    assert all(ft.fertilizer_type == FertilizerTypeEnum.ORGANIC for ft in organic_types)

    # Filter by form
    granular_types = fertilizer_type_service_fixture.filter_fertilizer_types(form=FertilizerFormEnum.GRANULAR)
    assert len(granular_types) == 2
    assert all(ft.form == FertilizerFormEnum.GRANULAR for ft in granular_types)

    # Filter by NPK ratio (Urea is 46-0-0)
    urea_filtered = fertilizer_type_service_fixture.filter_fertilizer_types(npk_ratio="46-0-0")
    assert len(urea_filtered) == 1
    assert urea_filtered[0].name == "Urea"

    # Filter by suitability criteria (crop_type)
    corn_suitable = fertilizer_type_service_fixture.filter_fertilizer_types(crop_type="corn")
    assert len(corn_suitable) == 1
    assert corn_suitable[0].name == "Urea"

    # Filter by suitability criteria (soil_type)
    loam_suitable = fertilizer_type_service_fixture.filter_fertilizer_types(soil_type="loam")
    assert len(loam_suitable) == 2 # Compost and SuperGrow NPK (if added)

    # Filter by name
    filtered_by_name = fertilizer_type_service_fixture.filter_fertilizer_types(name="Urea")
    assert len(filtered_by_name) == 1
    assert filtered_by_name[0].name == "Urea"

# --- Tests for API Endpoints ---

def test_api_get_all_fertilizer_types():
    response = client.get("/api/v1/fertilizer-types/")
    assert response.status_code == 200
    assert len(response.json()) == 3 # Default types

def test_api_get_fertilizer_type_by_id():
    urea_id = UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11")
    response = client.get(f"/api/v1/fertilizer-types/{urea_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Urea"

def test_api_get_fertilizer_type_by_id_not_found():
    non_existent_id = uuid4()
    response = client.get(f"/api/v1/fertilizer-types/{non_existent_id}")
    assert response.status_code == 404

def test_api_create_fertilizer_type(sample_fertilizer_type_data):
    new_id = uuid4()
    sample_fertilizer_type_data["id"] = str(new_id)
    response = client.post("/api/v1/fertilizer-types/", json=sample_fertilizer_type_data)
    assert response.status_code == 201
    assert response.json()["name"] == "SuperGrow NPK"

    # Clean up
    client.delete(f"/api/v1/fertilizer-types/{new_id}")

def test_api_create_fertilizer_type_duplicate_id(sample_fertilizer_type_data):
    existing_id = UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11") # Urea's ID
    sample_fertilizer_type_data["id"] = str(existing_id)
    response = client.post("/api/v1/fertilizer-types/", json=sample_fertilizer_type_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_api_update_fertilizer_type(sample_fertilizer_type_data):
    urea_id = UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11")
    updated_data = sample_fertilizer_type_data.copy()
    updated_data["id"] = str(urea_id)
    updated_data["name"] = "Super Urea Plus"
    response = client.put(f"/api/v1/fertilizer-types/{urea_id}", json=updated_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Super Urea Plus"

def test_api_update_fertilizer_type_not_found(sample_fertilizer_type_data):
    non_existent_id = uuid4()
    updated_data = sample_fertilizer_type_data.copy()
    updated_data["id"] = str(non_existent_id)
    response = client.put(f"/api/v1/fertilizer-types/{non_existent_id}", json=updated_data)
    assert response.status_code == 404

def test_api_delete_fertilizer_type():
    # Create a new one to delete
    new_id = uuid4()
    create_data = {
        "id": str(new_id),
        "name": "Temp Fertilizer",
        "npk_ratio": "1-1-1",
        "fertilizer_type": "organic",
        "form": "granular",
        "release_type": "quick",
        "cost_per_unit": 0.1,
        "unit": "USD/kg",
        "environmental_impact_score": "low"
    }
    client.post("/api/v1/fertilizer-types/", json=create_data)

    response = client.delete(f"/api/v1/fertilizer-types/{new_id}")
    assert response.status_code == 204
    get_response = client.get(f"/api/v1/fertilizer-types/{new_id}")
    assert get_response.status_code == 404

def test_api_delete_fertilizer_type_not_found():
    non_existent_id = uuid4()
    response = client.delete(f"/api/v1/fertilizer-types/{non_existent_id}")
    assert response.status_code == 404

def test_api_filter_fertilizer_types_by_type():
    response = client.get("/api/v1/fertilizer-types/filter/?fertilizer_type=organic")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert all(ft["fertilizer_type"] == "organic" for ft in response.json())

def test_api_filter_fertilizer_types_by_npk_ratio():
    response = client.get("/api/v1/fertilizer-types/filter/?npk_ratio=46-0-0")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Urea"

def test_api_filter_fertilizer_types_by_suitability_crop_type():
    response = client.get("/api/v1/fertilizer-types/filter/?crop_type=corn")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Urea"

def test_api_filter_fertilizer_types_by_suitability_soil_type():
    response = client.get("/api/v1/fertilizer-types/filter/?soil_type=loam")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert any(ft["name"] == "Urea" for ft in response.json())
    assert any(ft["name"] == "Compost" for ft in response.json())

def test_api_filter_fertilizer_types_no_match():
    response = client.get("/api/v1/fertilizer-types/filter/?fertilizer_type=organic&form=gaseous")
    assert response.status_code == 200
    assert len(response.json()) == 0
