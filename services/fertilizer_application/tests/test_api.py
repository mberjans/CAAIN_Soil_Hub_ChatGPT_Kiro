"""
Tests for the fertilizer application API endpoints.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from src.main import app
from src.models.application_models import ApplicationRequest, FieldConditions, CropRequirements, FertilizerSpecification


class TestApplicationAPI:
    """Test cases for application API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_request(self):
        """Create sample application request."""
        return {
            "field_conditions": {
                "field_size_acres": 100.0,
                "soil_type": "loam",
                "drainage_class": "well_drained",
                "slope_percent": 2.5,
                "irrigation_available": True,
                "field_shape": "rectangular",
                "access_roads": ["north", "south"]
            },
            "crop_requirements": {
                "crop_type": "corn",
                "growth_stage": "vegetative",
                "target_yield": 180.0,
                "nutrient_requirements": {
                    "nitrogen": 150.0,
                    "phosphorus": 60.0,
                    "potassium": 120.0
                },
                "application_timing_preferences": ["early_morning", "late_evening"]
            },
            "fertilizer_specification": {
                "fertilizer_type": "liquid",
                "npk_ratio": "28-0-0",
                "form": "liquid",
                "solubility": 100.0,
                "release_rate": "immediate",
                "cost_per_unit": 0.85,
                "unit": "lbs"
            },
            "available_equipment": [
                {
                    "equipment_type": "sprayer",
                    "capacity": 500.0,
                    "capacity_unit": "gallons",
                    "application_width": 60.0,
                    "application_rate_range": {"min": 10.0, "max": 50.0},
                    "fuel_efficiency": 0.8,
                    "maintenance_cost_per_hour": 15.0
                }
            ],
            "application_goals": ["maximize_efficiency", "minimize_cost"],
            "constraints": {
                "budget_limit": 5000.0,
                "time_constraint": "3_days"
            },
            "budget_limit": 5000.0
        }
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "fertilizer-application"
        assert data["status"] == "healthy"
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "AFAS Fertilizer Application Service" in data["message"]
    
    @patch('src.api.application_routes.ApplicationMethodService')
    def test_select_application_methods(self, mock_service, client, sample_request):
        """Test application method selection endpoint."""
        # Mock the service response
        mock_response = {
            "request_id": "test_request_001",
            "recommended_methods": [
                {
                    "method_id": "foliar_001",
                    "method_type": "foliar",
                    "recommended_equipment": {
                        "equipment_type": "sprayer",
                        "capacity": 500.0
                    },
                    "application_rate": 2.5,
                    "rate_unit": "gallons/acre",
                    "application_timing": "Early morning",
                    "efficiency_score": 0.9,
                    "cost_per_acre": 30.0,
                    "labor_requirements": "high",
                    "environmental_impact": "low",
                    "pros": ["High efficiency", "Quick response"],
                    "cons": ["Weather sensitive", "Higher cost"]
                }
            ],
            "primary_recommendation": {
                "method_id": "foliar_001",
                "method_type": "foliar"
            },
            "alternative_methods": [],
            "cost_comparison": {"foliar": 30.0},
            "efficiency_analysis": {"method_efficiencies": {"foliar": 0.9}},
            "equipment_compatibility": {"foliar": True},
            "processing_time_ms": 150.0,
            "metadata": {}
        }
        
        mock_service_instance = AsyncMock()
        mock_service_instance.select_application_methods.return_value = mock_response
        mock_service.return_value = mock_service_instance
        
        response = client.post("/api/v1/application/select-methods", json=sample_request)
        assert response.status_code == 200
        data = response.json()
        assert data["request_id"] == "test_request_001"
        assert len(data["recommended_methods"]) == 1
        assert data["recommended_methods"][0]["method_type"] == "foliar"
    
    def test_get_available_methods(self, client):
        """Test get available methods endpoint."""
        response = client.get("/api/v1/application/methods")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check method structure
        method = data[0]
        assert "method_type" in method
        assert "name" in method
        assert "description" in method
        assert "efficiency_score" in method
        assert "cost_per_acre" in method
    
    def test_validate_request(self, client, sample_request):
        """Test request validation endpoint."""
        response = client.post("/api/v1/application/validate-request", json=sample_request)
        assert response.status_code == 200
        data = response.json()
        assert "valid" in data
        assert "warnings" in data
        assert "errors" in data
        assert "suggestions" in data
    
    def test_validate_request_invalid(self, client):
        """Test request validation with invalid data."""
        invalid_request = {
            "field_conditions": {
                "field_size_acres": -1.0,  # Invalid field size
                "soil_type": "loam"
            },
            "crop_requirements": {
                "crop_type": "",  # Empty crop type
                "growth_stage": "vegetative"
            },
            "fertilizer_specification": {
                "fertilizer_type": "liquid",
                "npk_ratio": ""  # Empty NPK ratio
            }
        }
        
        response = client.post("/api/v1/application/validate-request", json=invalid_request)
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] == False
        assert len(data["errors"]) > 0


class TestMethodAPI:
    """Test cases for method API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_get_all_methods(self, client):
        """Test get all methods endpoint."""
        response = client.get("/api/v1/methods/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_all_methods_with_filters(self, client):
        """Test get all methods with filters."""
        response = client.get("/api/v1/methods/?method_type=broadcast&efficiency_min=0.7")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_method_by_id(self, client):
        """Test get method by ID endpoint."""
        response = client.get("/api/v1/methods/broadcast_001")
        assert response.status_code == 200
        data = response.json()
        assert data["method_id"] == "broadcast_001"
        assert data["method_type"] == "broadcast"
    
    def test_get_method_by_id_not_found(self, client):
        """Test get method by ID with non-existent ID."""
        response = client.get("/api/v1/methods/nonexistent")
        assert response.status_code == 404
    
    def test_compare_methods(self, client):
        """Test method comparison endpoint."""
        comparison_request = {
            "method_a_id": "broadcast_001",
            "method_b_id": "band_001",
            "comparison_criteria": ["cost", "efficiency", "environmental_impact"],
            "weights": {"cost": 0.4, "efficiency": 0.4, "environmental_impact": 0.2}
        }
        
        response = client.post("/api/v1/methods/compare", json=comparison_request)
        assert response.status_code == 200
        data = response.json()
        assert "method_a" in data
        assert "method_b" in data
        assert "comparison_criteria" in data
        assert "overall_winner" in data
    
    def test_optimize_method_selection(self, client):
        """Test method optimization endpoint."""
        optimization_request = {
            "field_conditions": {
                "field_size_acres": 100.0,
                "soil_type": "loam"
            },
            "crop_requirements": {
                "crop_type": "corn",
                "growth_stage": "vegetative"
            },
            "objectives": ["minimize_cost", "maximize_efficiency"],
            "constraints": {
                "budget_limit": 5000.0
            }
        }
        
        response = client.post("/api/v1/methods/optimize", json=optimization_request)
        assert response.status_code == 200
        data = response.json()
        assert "optimal_method" in data
        assert "optimal_parameters" in data
        assert "objective_values" in data
    
    def test_rank_methods(self, client):
        """Test method ranking endpoint."""
        ranking_request = {
            "methods": ["broadcast_001", "band_001", "foliar_001"],
            "ranking_criteria": ["cost", "efficiency"],
            "weights": {"cost": 0.6, "efficiency": 0.4}
        }
        
        response = client.post("/api/v1/methods/rank", json=ranking_request)
        assert response.status_code == 200
        data = response.json()
        assert "ranked_methods" in data
        assert "ranking_scores" in data
        assert "ranking_criteria" in data
    
    def test_validate_method(self, client):
        """Test method validation endpoint."""
        field_conditions = {
            "field_size_acres": 100.0,
            "soil_type": "loam",
            "slope_percent": 5.0
        }
        
        response = client.post("/api/v1/methods/validate/broadcast_001", json=field_conditions)
        assert response.status_code == 200
        data = response.json()
        assert "method" in data
        assert "validation_results" in data
        assert "overall_validity" in data
    
    def test_get_method_performance(self, client):
        """Test get method performance endpoint."""
        response = client.get("/api/v1/methods/performance/broadcast_001")
        assert response.status_code == 200
        data = response.json()
        assert data["method_id"] == "broadcast_001"
        assert "application_efficiency" in data
        assert "overall_performance" in data


class TestGuidanceAPI:
    """Test cases for guidance API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @patch('src.api.guidance_routes.GuidanceService')
    def test_get_application_guidance(self, mock_service, client):
        """Test application guidance endpoint."""
        # Mock the service response
        mock_response = {
            "request_id": "guidance_001",
            "guidance": {
                "guidance_id": "guidance_001",
                "pre_application_checklist": [
                    "Calibrate sprayer according to manufacturer specifications",
                    "Check spray pattern uniformity"
                ],
                "application_instructions": [
                    "Apply during early morning or late evening",
                    "Maintain consistent spray pressure"
                ],
                "safety_precautions": [
                    "Wear appropriate personal protective equipment",
                    "Avoid skin contact with fertilizer"
                ],
                "calibration_instructions": [
                    "Measure spray width and application rate",
                    "Adjust settings to achieve target rate"
                ],
                "troubleshooting_tips": [
                    "Check for clogged nozzles",
                    "Verify spray pressure"
                ],
                "post_application_tasks": [
                    "Clean sprayer thoroughly",
                    "Monitor crop response"
                ],
                "optimal_conditions": {
                    "temperature_range": "18-25°C",
                    "humidity_range": "50-80%"
                },
                "timing_recommendations": "Apply during early morning or late evening"
            },
            "weather_advisories": ["Good conditions for application"],
            "equipment_preparation": ["Check nozzle condition"],
            "quality_control_measures": ["Monitor application rate"],
            "processing_time_ms": 100.0
        }
        
        mock_service_instance = AsyncMock()
        mock_service_instance.provide_application_guidance.return_value = mock_response
        mock_service.return_value = mock_service_instance
        
        guidance_request = {
            "application_method": {
                "method_id": "foliar_001",
                "method_type": "foliar",
                "recommended_equipment": {
                    "equipment_type": "sprayer",
                    "capacity": 500.0
                },
                "application_rate": 2.5,
                "rate_unit": "gallons/acre",
                "application_timing": "Early morning",
                "efficiency_score": 0.9,
                "cost_per_acre": 30.0,
                "labor_requirements": "high",
                "environmental_impact": "low",
                "pros": ["High efficiency"],
                "cons": ["Weather sensitive"]
            },
            "field_conditions": {
                "field_size_acres": 50.0,
                "soil_type": "loam",
                "irrigation_available": True
            },
            "weather_conditions": {
                "temperature_celsius": 22.0,
                "humidity_percent": 65.0,
                "wind_speed_kmh": 8.0,
                "precipitation_mm": 0.0
            },
            "application_date": "2024-05-15",
            "experience_level": "intermediate"
        }
        
        response = client.post("/api/v1/guidance/application-guidance", json=guidance_request)
        assert response.status_code == 200
        data = response.json()
        assert data["request_id"] == "guidance_001"
        assert "guidance" in data
        assert "pre_application_checklist" in data["guidance"]
    
    def test_get_best_practices(self, client):
        """Test get best practices endpoint."""
        response = client.get("/api/v1/guidance/best-practices/foliar")
        assert response.status_code == 200
        data = response.json()
        assert data["method_type"] == "foliar"
        assert "pre_application" in data
        assert "application" in data
        assert "safety" in data
    
    def test_get_safety_guidelines(self, client):
        """Test get safety guidelines endpoint."""
        response = client.get("/api/v1/guidance/safety-guidelines/foliar")
        assert response.status_code == 200
        data = response.json()
        assert data["method_type"] == "foliar"
        assert "ppe_requirements" in data
        assert "handling_procedures" in data
        assert "emergency_protocols" in data
    
    def test_get_calibration_guide(self, client):
        """Test get calibration guide endpoint."""
        response = client.get("/api/v1/guidance/calibration-guide/foliar")
        assert response.status_code == 200
        data = response.json()
        assert data["method_type"] == "foliar"
        assert "equipment_setup" in data
        assert "rate_calculation" in data
        assert "verification_steps" in data
    
    def test_get_weather_advisories(self, client):
        """Test get weather advisories endpoint."""
        response = client.get(
            "/api/v1/guidance/weather-advisories",
            params={
                "method_type": "foliar",
                "temperature": 25.0,
                "humidity": 70.0,
                "wind_speed": 12.0,
                "precipitation": 0.0
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["method_type"] == "foliar"
        assert "advisories" in data
        assert "recommendation" in data
    
    def test_get_timing_recommendations(self, client):
        """Test get timing recommendations endpoint."""
        response = client.get(
            "/api/v1/guidance/timing-recommendations/foliar",
            params={
                "crop_stage": "vegetative",
                "field_size": 50.0
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["method_type"] == "foliar"
        assert "timing_recommendations" in data
        assert "optimal_windows" in data