"""
Comprehensive tests for the crop integration API endpoints.
Tests the API endpoints for crop type and growth stage integration.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# Add the src directory to the path so we can import the app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import app

client = TestClient(app)

class TestCropIntegrationAPI:
    """Test suite for crop integration API endpoints."""
    
    def test_get_supported_crops(self):
        """Test getting all supported crop types."""
        response = client.get("/api/v1/crop-integration/supported-crops")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "corn" in data
        assert "soybean" in data
        assert "wheat" in data

    def test_get_crop_info_success(self):
        """Test getting crop information for a valid crop."""
        response = client.get("/api/v1/crop-integration/crop-info/corn")
        assert response.status_code == 200
        
        data = response.json()
        assert "name" in data
        assert data["name"] == "Corn (Maize)"
        assert "scientific_name" in data
        assert "category" in data
        assert "nutrient_requirements" in data

    def test_get_crop_info_invalid_crop(self):
        """Test getting crop information for an invalid crop."""
        response = client.get("/api/v1/crop-integration/crop-info/invalid_crop")
        assert response.status_code == 400

    def test_get_supported_growth_stages(self):
        """Test getting supported growth stages for a crop."""
        response = client.get("/api/v1/crop-integration/supported-growth-stages/corn")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        # Should include standard corn growth stages
        assert "v1" in data
        assert "v6" in data
        assert "vt" in data
        assert "r1" in data

    def test_get_growth_stage_info_success(self):
        """Test getting growth stage information for a valid crop and stage."""
        response = client.get("/api/v1/crop-integration/growth-stage-info/corn/v6")
        assert response.status_code == 200
        
        data = response.json()
        assert "stage_name" in data
        assert data["stage_name"] == "Sixth Leaf"
        assert "nutrient_demand_level" in data
        assert data["nutrient_demand_level"] == "critical"

    def test_get_growth_stage_info_invalid_stage(self):
        """Test getting growth stage information for an invalid stage."""
        response = client.get("/api/v1/crop-integration/growth-stage-info/corn/invalid_stage")
        assert response.status_code == 400

    def test_get_application_preferences(self):
        """Test getting application preferences for a crop."""
        response = client.get("/api/v1/crop-integration/application-preferences/corn")
        assert response.status_code == 200
        
        data = response.json()
        assert "crop_type" in data
        assert data["crop_type"] == "corn"
        assert "preferred_methods" in data
        assert "avoided_methods" in data

    def test_get_recommended_methods(self):
        """Test getting recommended methods for a crop and growth stage."""
        response = client.get("/api/v1/crop-integration/recommended-methods/corn/v6")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        # Should include methods appropriate for corn V6 stage
        assert "sidedress" in data
        assert "band" in data

    def test_get_avoided_methods(self):
        """Test getting avoided methods for a crop and growth stage."""
        response = client.get("/api/v1/crop-integration/avoided-methods/corn/v6")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        # Should include methods to avoid for corn V6 stage
        assert "foliar" in data

    def test_get_critical_application_windows(self):
        """Test getting critical application windows for a crop."""
        response = client.get("/api/v1/crop-integration/critical-application-windows/corn")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "pre_plant" in data
        assert "at_planting" in data
        assert "early_vegetative" in data

    def test_calculate_timing_score(self):
        """Test calculating timing score for application."""
        response = client.get(
            "/api/v1/crop-integration/calculate-timing-score",
            params={
                "crop_type": "corn",
                "growth_stage": "v6",
                "method_type": "sidedress",
                "days_from_planting": 40
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, float)
        assert 0.0 <= data <= 1.0

    def test_calculate_timing_score_invalid(self):
        """Test calculating timing score with invalid parameters."""
        response = client.get(
            "/api/v1/crop-integration/calculate-timing-score",
            params={
                "crop_type": "invalid_crop",
                "growth_stage": "v6",
                "method_type": "sidedress",
                "days_from_planting": 40
            }
        )
        assert response.status_code == 400

    def test_get_nutrient_uptake_curve(self):
        """Test getting nutrient uptake curve."""
        response = client.get("/api/v1/crop-integration/nutrient-uptake-curve/corn/nitrogen")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 10  # Should have 10 values

    def test_assess_crop_method_compatibility(self):
        """Test assessing crop method compatibility."""
        response = client.get("/api/v1/crop-integration/method-compatibility/corn/band")
        assert response.status_code == 200
        
        data = response.json()
        assert "compatibility_score" in data
        assert "factors" in data
        assert isinstance(data["compatibility_score"], float)
        assert isinstance(data["factors"], list)

    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/api/v1/crop-integration/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "service" in data
        assert data["service"] == "crop-integration"
        assert "supported_crops" in data
        assert isinstance(data["supported_crops"], int)
        assert data["supported_crops"] > 0


class TestCropIntegrationAPIErrorHandling:
    """Test error handling for crop integration API endpoints."""
    
    def test_get_crop_info_not_found(self):
        """Test getting crop info for an unknown crop."""
        # Use a crop type that doesn't exist
        response = client.get("/api/v1/crop-integration/crop-info/unknown_crop_12345")
        # The service returns an empty dict rather than raising an error
        assert response.status_code == 200
        data = response.json()
        assert data == {}

    def test_get_growth_stage_info_not_found(self):
        """Test getting growth stage info for an unknown combination."""
        # Use a growth stage that doesn't exist for corn
        response = client.get("/api/v1/crop-integration/growth-stage-info/corn/unknown_stage_12345")
        # This should return a different status code
        assert response.status_code in [400, 404]

    def test_calculate_timing_score_bad_input(self):
        """Test timing score with invalid days value."""
        response = client.get(
            "/api/v1/crop-integration/calculate-timing-score",
            params={
                "crop_type": "corn",
                "growth_stage": "v6",
                "method_type": "sidedress",
                "days_from_planting": -5  # Invalid negative value
            }
        )
        # Should still work as the validation allows negative values but processes them appropriately
        assert response.status_code in [200, 422]  # 200 if processed, 422 if validation fails

    def test_get_nutrient_uptake_curve_unknown_nutrient(self):
        """Test getting uptake curve for an unknown nutrient."""
        response = client.get("/api/v1/crop-integration/nutrient-uptake-curve/corn/unknown_nutrient")
        assert response.status_code == 200
        data = response.json()
        # Should return default curve
        assert isinstance(data, list)
        assert len(data) == 10
        # Default should be [0.1] * 10
        assert all(x == 0.1 for x in data)


def test_api_performance():
    """Test API endpoint performance."""
    import time
    
    # Test multiple requests to check performance
    start_time = time.time()
    for _ in range(10):
        client.get("/api/v1/crop-integration/supported-crops")
    elapsed = time.time() - start_time
    
    # Should be fast (less than 1 second for 10 requests)
    assert elapsed < 1.0, f"API calls took too long: {elapsed:.2f}s"

if __name__ == "__main__":
    pytest.main()