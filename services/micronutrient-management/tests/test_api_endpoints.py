import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.micronutrient_schemas import (
    ApplicationMethodRequest,
    TimingRecommendationRequest,
    EquipmentAvailability,
    FieldCondition,
    MicronutrientType,
    ApplicationMethod,
    TimingRecommendationType
)
from src.api.micronutrient_routes import router
from main import app  # Assuming the main FastAPI app is in main.py


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_equipment_availability():
    return EquipmentAvailability(
        sprayer=True,
        fertilizer_applicator=True,
        irrigation_system=True,
        seeding_equipment=True
    )


@pytest.fixture
def sample_field_conditions():
    return FieldCondition(
        moisture="adequate",
        temperature=70.0,
        weather_forecast=[],
        soil_compaction=False
    )


@pytest.fixture
def sample_application_method_request_payload(sample_equipment_availability, sample_field_conditions):
    return {
        "crop_type": "Corn",
        "growth_stage": "Vegetative",
        "deficiency_severity": "High",
        "equipment_availability": {
            "sprayer": True,
            "fertilizer_applicator": True,
            "irrigation_system": False,
            "seeding_equipment": False
        },
        "field_conditions": {
            "moisture": "adequate",
            "temperature": 70.0,
            "weather_forecast": [],
            "soil_compaction": False
        },
        "nutrient_type": "ZINC",
        "recommended_amount": 2.5
    }


@pytest.fixture
def sample_timing_request_payload(sample_field_conditions):
    return {
        "crop_type": "Corn",
        "growth_stage": "Vegetative",
        "nutrient_uptake_pattern": "High demand during vegetative growth",
        "weather_conditions": "Clear",
        "nutrient_type": "ZINC",
        "application_method": "Foliar Application",
        "field_conditions": {
            "moisture": "adequate",
            "temperature": 70.0,
            "weather_forecast": [],
            "soil_compaction": False
        }
    }


def test_get_application_method_recommendation_success(
    client, 
    sample_application_method_request_payload
):
    response = client.post(
        "/api/v1/micronutrients/application-method", 
        json=sample_application_method_request_payload
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "request_id" in data
    assert "application_method" in data
    assert "timing" in data
    assert "economic_efficiency" in data
    assert "risk_assessment" in data
    assert "notes" in data
    
    # Verify application method structure
    app_method = data["application_method"]
    assert "method" in app_method
    assert "confidence_score" in app_method
    assert "timing_recommendation" in app_method
    assert "reason" in app_method
    assert "equipment_required" in app_method
    assert "field_conditions_suitable" in app_method
    assert "alternative_methods" in app_method


def test_get_timing_recommendation_success(
    client, 
    sample_timing_request_payload
):
    response = client.post(
        "/api/v1/micronutrients/timing", 
        json=sample_timing_request_payload
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "timing" in data
    assert "optimal_window_start" in data
    assert "optimal_window_end" in data
    assert "reason" in data
    assert "weather_considerations" in data
    assert "compatibility_notes" in data
    assert "expected_efficacy" in data


def test_get_application_method_and_timing_recommendation_success(
    client, 
    sample_application_method_request_payload
):
    response = client.post(
        "/api/v1/micronutrients/application-method-and-timing", 
        json=sample_application_method_request_payload
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "request_id" in data
    assert "application_method" in data
    assert "timing" in data
    assert "economic_efficiency" in data
    assert "risk_assessment" in data
    assert "notes" in data


def test_get_application_method_recommendation_validation_error(
    client
):
    # Send invalid request without required fields
    invalid_payload = {
        "crop_type": "Corn"  # Missing required fields
    }
    
    response = client.post(
        "/api/v1/micronutrients/application-method", 
        json=invalid_payload
    )
    
    assert response.status_code == 422  # Validation error


def test_get_timing_recommendation_validation_error(
    client
):
    # Send invalid request without required fields
    invalid_payload = {
        "crop_type": "Corn"  # Missing required fields
    }
    
    response = client.post(
        "/api/v1/micronutrients/timing", 
        json=invalid_payload
    )
    
    assert response.status_code == 422  # Validation error


def test_get_application_method_and_timing_validation_error(
    client
):
    # Send invalid request without required fields
    invalid_payload = {
        "crop_type": "Corn"  # Missing required fields
    }
    
    response = client.post(
        "/api/v1/micronutrients/application-method-and-timing", 
        json=invalid_payload
    )
    
    assert response.status_code == 422  # Validation error


def test_get_application_method_recommendation_internal_error(
    client, 
    sample_application_method_request_payload
):
    # Test with an invalid nutrient type to trigger an internal error
    invalid_payload = sample_application_method_request_payload.copy()
    invalid_payload["nutrient_type"] = "INVALID_NUTRIENT"
    
    response = client.post(
        "/api/v1/micronutrients/application-method", 
        json=invalid_payload
    )
    
    # Should return 500 for internal server errors
    assert response.status_code == 500


def test_get_timing_recommendation_internal_error(
    client, 
    sample_timing_request_payload
):
    # Test with an invalid nutrient type to trigger an internal error
    invalid_payload = sample_timing_request_payload.copy()
    invalid_payload["nutrient_type"] = "INVALID_NUTRIENT"
    
    response = client.post(
        "/api/v1/micronutrients/timing", 
        json=invalid_payload
    )
    
    # Should return 500 for internal server errors
    assert response.status_code == 500


def test_get_application_method_and_timing_internal_error(
    client, 
    sample_application_method_request_payload
):
    # Test with an invalid nutrient type to trigger an internal error
    invalid_payload = sample_application_method_request_payload.copy()
    invalid_payload["nutrient_type"] = "INVALID_NUTRIENT"
    
    response = client.post(
        "/api/v1/micronutrients/application-method-and-timing", 
        json=invalid_payload
    )
    
    # Should return 500 for internal server errors
    assert response.status_code == 500


def test_application_method_service_integration(
    client,
    sample_application_method_request_payload
):
    """Test that the application method service integrates properly with the API"""
    response = client.post(
        "/api/v1/micronutrients/application-method-and-timing", 
        json=sample_application_method_request_payload
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check that we received valid recommendation data
    app_method = data["application_method"]
    timing = data["timing"]
    
    # Verify that the method is one of the expected enums
    assert app_method["method"] in [e.value for e in ApplicationMethod]
    
    # Verify that the timing is one of the expected enums
    assert timing["timing"] in [e.value for e in TimingRecommendationType]
    
    # Verify numeric fields are within valid ranges
    assert 0.0 <= data["economic_efficiency"] <= 1.0
    assert 0.0 <= app_method["confidence_score"] <= 1.0
    assert 0.0 <= timing["expected_efficacy"] <= 1.0
    assert data["risk_assessment"] in ["Low", "Medium", "High"]
    
    # Verify that notes is a list
    assert isinstance(data["notes"], list)
    assert len(data["notes"]) > 0


def test_timing_service_integration(
    client,
    sample_timing_request_payload
):
    """Test that the timing service integrates properly with the API"""
    response = client.post(
        "/api/v1/micronutrients/timing", 
        json=sample_timing_request_payload
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify that the timing is one of the expected enums
    assert data["timing"] in [e.value for e in TimingRecommendationType]
    
    # Verify numeric fields are within valid ranges
    assert 0.0 <= data["expected_efficacy"] <= 1.0
    
    # Verify that lists are present
    assert isinstance(data["weather_considerations"], list)
    assert isinstance(data["compatibility_notes"], list)
    
    # Verify that datetime fields are present (as strings in JSON)
    assert isinstance(data["optimal_window_start"], (str, type(None)))
    assert isinstance(data["optimal_window_end"], (str, type(None)))
    
    # Verify that reason is a string
    assert isinstance(data["reason"], str)
    assert len(data["reason"]) > 0