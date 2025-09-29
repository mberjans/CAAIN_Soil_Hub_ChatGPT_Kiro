"""
Tests for Drought-Resilient Crop Recommendation API Endpoints

Comprehensive test suite for drought-tolerant crop variety recommendation
API endpoints, including request validation, response formatting, and
error handling.
"""

import pytest
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from datetime import datetime
from uuid import uuid4

from src.main import app
from src.models.drought_resilient_models import (
    DroughtRecommendationRequest,
    DroughtRecommendationResponse,
    DroughtRiskAssessment,
    DroughtRiskLevel,
    AlternativeCropRecommendation,
    DiversificationStrategy,
    WaterConservationPotential
)


class TestDroughtResilientAPI:
    """Test suite for drought-resilient API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def sample_location(self):
        """Sample location data for testing."""
        return {
            "latitude": 40.0,
            "longitude": -95.0,
            "climate_zone": "humid_continental",
            "soil_type": "clay_loam",
            "irrigation_available": True,
            "region": "Midwest"
        }

    @pytest.fixture
    def sample_request_data(self, sample_location):
        """Sample request data for testing."""
        return {
            "request_id": str(uuid4()),
            "location": sample_location,
            "crop_type": "corn",
            "drought_risk_level": "moderate",
            "irrigation_available": True,
            "include_alternative_crops": True,
            "include_diversification_strategies": True,
            "include_water_conservation_analysis": True
        }

    @pytest.fixture
    def mock_response_data(self):
        """Mock response data for testing."""
        return {
            "request_id": str(uuid4()),
            "location": {"latitude": 40.0, "longitude": -95.0},
            "drought_risk_assessment": {
                "location": {"latitude": 40.0, "longitude": -95.0},
                "overall_risk_level": "moderate",
                "risk_factors": {"drought_risk": 0.5},
                "confidence_score": 0.8,
                "assessment_date": datetime.utcnow().isoformat()
            },
            "recommended_varieties": [],
            "alternative_crops": [
                {
                    "crop_name": "Sorghum",
                    "scientific_name": "Sorghum bicolor",
                    "drought_tolerance_level": "high",
                    "water_use_efficiency": "very_high",
                    "yield_potential": "moderate",
                    "market_demand": "moderate",
                    "management_complexity": "low",
                    "suitability_score": 0.8,
                    "advantages": ["Excellent drought tolerance"],
                    "considerations": ["Lower yield potential"],
                    "transition_requirements": ["Evaluate equipment compatibility"]
                }
            ],
            "diversification_strategies": [
                {
                    "strategy_type": "crop_rotation",
                    "description": "Implement diverse crop rotation",
                    "implementation_steps": ["Include drought-tolerant crops"],
                    "expected_benefits": ["Reduced drought risk"],
                    "risk_reduction_potential": 0.3,
                    "implementation_difficulty": "moderate"
                }
            ],
            "water_conservation_potential": {
                "variety_based_savings": 50.0,
                "alternative_crop_savings": 75.0,
                "total_potential_savings": 125.0,
                "savings_percentage": 25.0,
                "implementation_timeline": "1-3 years",
                "cost_benefit_ratio": 0.5
            },
            "confidence_score": 0.8,
            "generated_at": datetime.utcnow().isoformat()
        }


class TestMainRecommendationEndpoints:
    """Test main recommendation endpoints."""

    @patch('src.api.drought_resilient_routes.get_drought_service')
    def test_get_drought_resilient_recommendations_success(
        self, mock_get_service, client, sample_request_data, mock_response_data
    ):
        """Test successful drought-resilient recommendation generation."""
        # Mock the service
        mock_service = AsyncMock()
        mock_service.get_drought_resilient_recommendations.return_value = mock_response_data
        mock_get_service.return_value = mock_service
        
        response = client.post(
            "/api/v1/drought-resilient/recommendations",
            json=sample_request_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["request_id"] == sample_request_data["request_id"]
        assert "drought_risk_assessment" in data
        assert "recommended_varieties" in data
        assert "alternative_crops" in data
        assert "diversification_strategies" in data
        assert "water_conservation_potential" in data

    def test_get_drought_resilient_recommendations_invalid_request(self, client):
        """Test invalid request handling."""
        invalid_request = {
            "request_id": "",  # Invalid empty request ID
            "location": {}  # Invalid empty location
        }
        
        response = client.post(
            "/api/v1/drought-resilient/recommendations",
            json=invalid_request
        )
        
        assert response.status_code == 422  # Validation error

    def test_get_drought_resilient_recommendations_missing_location(self, client):
        """Test missing location data."""
        invalid_request = {
            "request_id": str(uuid4())
            # Missing location field
        }
        
        response = client.post(
            "/api/v1/drought-resilient/recommendations",
            json=invalid_request
        )
        
        assert response.status_code == 422  # Validation error

    @patch('src.api.drought_resilient_routes.get_drought_service')
    def test_get_simple_drought_recommendations(
        self, mock_get_service, client, sample_location, mock_response_data
    ):
        """Test simplified drought recommendation endpoint."""
        # Mock the service
        mock_service = AsyncMock()
        mock_service.get_drought_resilient_recommendations.return_value = mock_response_data
        mock_get_service.return_value = mock_service
        
        response = client.post(
            "/api/v1/drought-resilient/recommendations/simple",
            json=sample_location,
            params={
                "crop_type": "corn",
                "drought_risk_level": "moderate",
                "irrigation_available": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "drought_risk_assessment" in data
        assert "recommended_varieties" in data
        assert "alternative_crops" in data

    def test_get_simple_drought_recommendations_missing_location(self, client):
        """Test simplified endpoint with missing location."""
        response = client.post(
            "/api/v1/drought-resilient/recommendations/simple",
            json={}  # Empty location
        )
        
        assert response.status_code == 422  # Validation error


class TestDroughtRiskAssessmentEndpoints:
    """Test drought risk assessment endpoints."""

    @patch('src.api.drought_resilient_routes.get_drought_service')
    def test_assess_drought_risk_success(
        self, mock_get_service, client, sample_location
    ):
        """Test successful drought risk assessment."""
        # Mock the service
        mock_service = AsyncMock()
        mock_service._assess_drought_risk.return_value = {
            "location": sample_location,
            "overall_risk_level": "moderate",
            "risk_factors": {"drought_risk": 0.5},
            "confidence_score": 0.8,
            "assessment_date": datetime.utcnow().isoformat()
        }
        mock_get_service.return_value = mock_service
        
        response = client.post(
            "/api/v1/drought-resilient/risk-assessment",
            json=sample_location,
            params={"drought_risk_level": "moderate"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["overall_risk_level"] == "moderate"
        assert "risk_factors" in data
        assert "confidence_score" in data

    def test_assess_drought_risk_invalid_location(self, client):
        """Test drought risk assessment with invalid location."""
        response = client.post(
            "/api/v1/drought-resilient/risk-assessment",
            json={}  # Empty location
        )
        
        assert response.status_code == 422  # Validation error

    def test_get_drought_risk_levels(self, client):
        """Test drought risk levels endpoint."""
        response = client.get("/api/v1/drought-resilient/risk-levels")
        
        assert response.status_code == 200
        data = response.json()
        assert "risk_levels" in data
        assert len(data["risk_levels"]) == 5
        
        # Check that all risk levels are present
        risk_levels = [level["level"] for level in data["risk_levels"]]
        assert "very_low" in risk_levels
        assert "low" in risk_levels
        assert "moderate" in risk_levels
        assert "high" in risk_levels
        assert "severe" in risk_levels


class TestAlternativeCropEndpoints:
    """Test alternative crop recommendation endpoints."""

    @patch('src.api.drought_resilient_routes.get_drought_service')
    def test_get_alternative_crop_recommendations_success(
        self, mock_get_service, client, sample_location
    ):
        """Test successful alternative crop recommendations."""
        # Mock the service
        mock_service = AsyncMock()
        mock_service._get_alternative_crop_recommendations.return_value = [
            {
                "crop_name": "Sorghum",
                "scientific_name": "Sorghum bicolor",
                "drought_tolerance_level": "high",
                "water_use_efficiency": "very_high",
                "yield_potential": "moderate",
                "market_demand": "moderate",
                "management_complexity": "low",
                "suitability_score": 0.8,
                "advantages": ["Excellent drought tolerance"],
                "considerations": ["Lower yield potential"],
                "transition_requirements": ["Evaluate equipment compatibility"]
            }
        ]
        mock_service._assess_drought_risk.return_value = {
            "location": sample_location,
            "overall_risk_level": "moderate",
            "risk_factors": {"drought_risk": 0.5},
            "confidence_score": 0.8
        }
        mock_get_service.return_value = mock_service
        
        response = client.get(
            "/api/v1/drought-resilient/alternative-crops",
            json=sample_location,
            params={"drought_risk_level": "moderate"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["crop_name"] == "Sorghum"

    def test_get_alternative_crop_recommendations_invalid_location(self, client):
        """Test alternative crop recommendations with invalid location."""
        response = client.get(
            "/api/v1/drought-resilient/alternative-crops",
            json={}  # Empty location
        )
        
        assert response.status_code == 422  # Validation error

    def test_get_alternative_crop_details(self, client):
        """Test alternative crop details endpoint."""
        response = client.get(
            "/api/v1/drought-resilient/alternative-crops/sorghum",
            json={"latitude": 40.0, "longitude": -95.0}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["crop_name"] == "sorghum"
        assert "drought_characteristics" in data
        assert "management_requirements" in data
        assert "economic_considerations" in data


class TestDiversificationStrategyEndpoints:
    """Test diversification strategy endpoints."""

    @patch('src.api.drought_resilient_routes.get_drought_service')
    def test_get_diversification_strategies_success(
        self, mock_get_service, client, sample_location
    ):
        """Test successful diversification strategy recommendations."""
        # Mock the service
        mock_service = AsyncMock()
        mock_service._generate_diversification_strategies.return_value = [
            {
                "strategy_type": "crop_rotation",
                "description": "Implement diverse crop rotation",
                "implementation_steps": ["Include drought-tolerant crops"],
                "expected_benefits": ["Reduced drought risk"],
                "risk_reduction_potential": 0.3,
                "implementation_difficulty": "moderate"
            }
        ]
        mock_service._assess_drought_risk.return_value = {
            "location": sample_location,
            "overall_risk_level": "moderate",
            "risk_factors": {"drought_risk": 0.5},
            "confidence_score": 0.8
        }
        mock_get_service.return_value = mock_service
        
        response = client.get(
            "/api/v1/drought-resilient/diversification-strategies",
            json=sample_location,
            params={"drought_risk_level": "moderate"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["strategy_type"] == "crop_rotation"

    def test_get_diversification_strategies_invalid_location(self, client):
        """Test diversification strategies with invalid location."""
        response = client.get(
            "/api/v1/drought-resilient/diversification-strategies",
            json={}  # Empty location
        )
        
        assert response.status_code == 422  # Validation error


class TestWaterConservationEndpoints:
    """Test water conservation analysis endpoints."""

    @patch('src.api.drought_resilient_routes.get_drought_service')
    def test_analyze_water_conservation_potential_success(
        self, mock_get_service, client, sample_location
    ):
        """Test successful water conservation analysis."""
        # Mock the service
        mock_service = AsyncMock()
        mock_response = {
            "request_id": str(uuid4()),
            "location": sample_location,
            "water_conservation_potential": {
                "variety_based_savings": 50.0,
                "alternative_crop_savings": 75.0,
                "total_potential_savings": 125.0,
                "savings_percentage": 25.0,
                "implementation_timeline": "1-3 years",
                "cost_benefit_ratio": 0.5
            }
        }
        mock_service.get_drought_resilient_recommendations.return_value = mock_response
        mock_get_service.return_value = mock_service
        
        response = client.post(
            "/api/v1/drought-resilient/water-conservation-analysis",
            json=sample_location,
            params={"irrigation_method": "drip"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "variety_based_savings" in data
        assert "alternative_crop_savings" in data
        assert "total_potential_savings" in data
        assert "savings_percentage" in data

    def test_analyze_water_conservation_potential_invalid_location(self, client):
        """Test water conservation analysis with invalid location."""
        response = client.post(
            "/api/v1/drought-resilient/water-conservation-analysis",
            json={}  # Empty location
        )
        
        assert response.status_code == 422  # Validation error

    def test_get_water_efficiency_levels(self, client):
        """Test water efficiency levels endpoint."""
        response = client.get("/api/v1/drought-resilient/water-efficiency-levels")
        
        assert response.status_code == 200
        data = response.json()
        assert "efficiency_levels" in data
        assert len(data["efficiency_levels"]) == 5
        
        # Check that all efficiency levels are present
        efficiency_levels = [level["level"] for level in data["efficiency_levels"]]
        assert "very_high" in efficiency_levels
        assert "high" in efficiency_levels
        assert "moderate" in efficiency_levels
        assert "low" in efficiency_levels
        assert "very_low" in efficiency_levels


class TestDroughtManagementPracticesEndpoints:
    """Test drought management practices endpoints."""

    def test_get_drought_management_practices_success(self, client, sample_location):
        """Test successful drought management practices retrieval."""
        response = client.get(
            "/api/v1/drought-resilient/management-practices",
            json=sample_location,
            params={"effectiveness_threshold": 0.5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check that practices have required fields
        for practice in data:
            assert "practice_name" in practice
            assert "practice_type" in practice
            assert "description" in practice
            assert "implementation_steps" in practice
            assert "water_savings_potential" in practice
            assert "effectiveness_rating" in practice

    def test_get_drought_management_practices_with_filters(self, client, sample_location):
        """Test drought management practices with filters."""
        response = client.get(
            "/api/v1/drought-resilient/management-practices",
            json=sample_location,
            params={
                "practice_type": "soil",
                "effectiveness_threshold": 0.7
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Check that filtered practices meet criteria
        for practice in data:
            assert practice["effectiveness_rating"] >= 0.7

    def test_get_drought_management_practices_invalid_location(self, client):
        """Test drought management practices with invalid location."""
        response = client.get(
            "/api/v1/drought-resilient/management-practices",
            json={}  # Empty location
        )
        
        assert response.status_code == 422  # Validation error


class TestHealthAndStatusEndpoints:
    """Test health check and status endpoints."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/v1/drought-resilient/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "drought-resilient-crop-recommendations"
        assert "timestamp" in data
        assert "version" in data

    @patch('src.api.drought_resilient_routes.get_drought_service')
    def test_service_status(self, mock_get_service, client):
        """Test service status endpoint."""
        # Mock the service
        mock_service = AsyncMock()
        mock_service.database_available = True
        mock_get_service.return_value = mock_service
        
        response = client.get("/api/v1/drought-resilient/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "drought-resilient-crop-recommendations"
        assert data["status"] == "operational"
        assert "capabilities" in data
        assert "database_available" in data
        assert "timestamp" in data


class TestErrorHandling:
    """Test error handling and edge cases."""

    @patch('src.api.drought_resilient_routes.get_drought_service')
    def test_service_error_handling(self, mock_get_service, client, sample_request_data):
        """Test service error handling."""
        # Mock service to raise an exception
        mock_service = AsyncMock()
        mock_service.get_drought_resilient_recommendations.side_effect = Exception("Service error")
        mock_get_service.return_value = mock_service
        
        response = client.post(
            "/api/v1/drought-resilient/recommendations",
            json=sample_request_data
        )
        
        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert "Service error" in data["error"]

    def test_invalid_json_request(self, client):
        """Test invalid JSON request handling."""
        response = client.post(
            "/api/v1/drought-resilient/recommendations",
            data="invalid json"
        )
        
        assert response.status_code == 422

    def test_missing_required_fields(self, client):
        """Test missing required fields handling."""
        incomplete_request = {
            "request_id": str(uuid4())
            # Missing location field
        }
        
        response = client.post(
            "/api/v1/drought-resilient/recommendations",
            json=incomplete_request
        )
        
        assert response.status_code == 422

    def test_invalid_enum_values(self, client, sample_location):
        """Test invalid enum values handling."""
        invalid_request = {
            "request_id": str(uuid4()),
            "location": sample_location,
            "drought_risk_level": "invalid_level"  # Invalid enum value
        }
        
        response = client.post(
            "/api/v1/drought-resilient/recommendations",
            json=invalid_request
        )
        
        assert response.status_code == 422


class TestAPIValidation:
    """Test API request validation."""

    def test_request_id_validation(self, client, sample_location):
        """Test request ID validation."""
        # Test empty request ID
        invalid_request = {
            "request_id": "",
            "location": sample_location
        }
        
        response = client.post(
            "/api/v1/drought-resilient/recommendations",
            json=invalid_request
        )
        
        assert response.status_code == 422

    def test_location_validation(self, client):
        """Test location validation."""
        # Test empty location
        invalid_request = {
            "request_id": str(uuid4()),
            "location": {}
        }
        
        response = client.post(
            "/api/v1/drought-resilient/recommendations",
            json=invalid_request
        )
        
        assert response.status_code == 422

    def test_boolean_field_validation(self, client, sample_location):
        """Test boolean field validation."""
        # Test invalid boolean values
        invalid_request = {
            "request_id": str(uuid4()),
            "location": sample_location,
            "irrigation_available": "yes"  # Should be boolean
        }
        
        response = client.post(
            "/api/v1/drought-resilient/recommendations",
            json=invalid_request
        )
        
        assert response.status_code == 422

    def test_enum_field_validation(self, client, sample_location):
        """Test enum field validation."""
        # Test invalid enum values
        invalid_request = {
            "request_id": str(uuid4()),
            "location": sample_location,
            "drought_risk_level": "extreme"  # Should be "severe"
        }
        
        response = client.post(
            "/api/v1/drought-resilient/recommendations",
            json=invalid_request
        )
        
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])