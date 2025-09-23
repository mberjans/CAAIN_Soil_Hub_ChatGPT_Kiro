"""
API Routes Tests for Location Validation Service
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

Tests for the FastAPI routes in the location validation service.
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from main import app

# Create test client
client = TestClient(app)


class TestLocationValidationAPI:
    """Test suite for location validation API endpoints."""
    
    def test_root_endpoint(self):
        """Test the root endpoint returns service information."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "service" in data
        assert "version" in data
        assert "endpoints" in data
        assert "agricultural_features" in data
        
        assert data["service"] == "AFAS Location Validation Service"
        assert data["version"] == "1.0.0"
    
    def test_validate_coordinates_valid(self):
        """Test coordinate validation with valid coordinates."""
        request_data = {
            "latitude": 42.0308,
            "longitude": -93.6319
        }
        
        response = client.post("/api/v1/validation/coordinates", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "valid" in data
        assert "warnings" in data
        assert "errors" in data
        assert "geographic_info" in data
        
        assert data["valid"] is True
        assert isinstance(data["warnings"], list)
        assert isinstance(data["errors"], list)
        assert len(data["errors"]) == 0
    
    def test_validate_coordinates_invalid(self):
        """Test coordinate validation with invalid coordinates."""
        request_data = {
            "latitude": 91.0,  # Invalid latitude
            "longitude": -93.6319
        }
        
        response = client.post("/api/v1/validation/coordinates", json=request_data)
        
        assert response.status_code == 422
        data = response.json()
        
        assert "error" in data["detail"]
        assert data["detail"]["error"]["error_code"] == "INVALID_COORDINATES"
    
    def test_validate_agricultural_location_valid(self):
        """Test agricultural location validation with valid coordinates."""
        request_data = {
            "latitude": 42.0308,
            "longitude": -93.6319
        }
        
        response = client.post("/api/v1/validation/agricultural", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "valid" in data
        assert "geographic_info" in data
        
        assert data["valid"] is True
        
        if data["geographic_info"]:
            assert "is_agricultural" in data["geographic_info"]
            assert "climate_zone" in data["geographic_info"]
    
    def test_validate_agricultural_location_invalid(self):
        """Test agricultural location validation with invalid coordinates."""
        request_data = {
            "latitude": -91.0,  # Invalid latitude
            "longitude": -93.6319
        }
        
        response = client.post("/api/v1/validation/agricultural", json=request_data)
        
        assert response.status_code == 422
        data = response.json()
        
        assert "error" in data["detail"]
    
    def test_health_check(self):
        """Test the health check endpoint."""
        response = client.get("/api/v1/validation/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "service" in data
        assert "version" in data
        
        assert data["service"] == "location-validation"
        assert data["version"] == "1.0"
    
    def test_get_validation_error_known(self):
        """Test getting a known validation error."""
        response = client.get("/api/v1/validation/errors/INVALID_COORDINATES")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "error_code" in data
        assert "error_message" in data
        assert "suggested_actions" in data
        
        assert data["error_code"] == "INVALID_COORDINATES"
        assert isinstance(data["suggested_actions"], list)
        assert len(data["suggested_actions"]) > 0
    
    def test_get_validation_error_unknown(self):
        """Test getting an unknown validation error."""
        response = client.get("/api/v1/validation/errors/UNKNOWN_ERROR")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return default error
        assert "error_code" in data
        assert data["error_code"] == "LOCATION_NOT_FOUND"
    
    def test_coordinate_validation_missing_fields(self):
        """Test coordinate validation with missing fields."""
        # Missing longitude
        request_data = {
            "latitude": 42.0308
        }
        
        response = client.post("/api/v1/validation/coordinates", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_coordinate_validation_wrong_types(self):
        """Test coordinate validation with wrong data types."""
        request_data = {
            "latitude": "not_a_number",
            "longitude": -93.6319
        }
        
        response = client.post("/api/v1/validation/coordinates", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_agricultural_validation_edge_cases(self):
        """Test agricultural validation with edge case coordinates."""
        # Test coordinates at equator
        request_data = {
            "latitude": 0.0,
            "longitude": 0.0
        }
        
        response = client.post("/api/v1/validation/agricultural", json=request_data)
        
        # Should return a response (may have warnings about ocean location)
        assert response.status_code in [200, 422]
        
        # Test coordinates at poles
        request_data = {
            "latitude": 90.0,
            "longitude": 0.0
        }
        
        response = client.post("/api/v1/validation/agricultural", json=request_data)
        
        # Should return a response
        assert response.status_code in [200, 422]


class TestAPIDocumentation:
    """Test API documentation endpoints."""
    
    def test_openapi_docs(self):
        """Test that OpenAPI documentation is available."""
        response = client.get("/docs")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_redoc_docs(self):
        """Test that ReDoc documentation is available."""
        response = client.get("/redoc")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_openapi_json(self):
        """Test that OpenAPI JSON schema is available."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
        
        # Check that our endpoints are documented
        assert "/api/v1/validation/coordinates" in data["paths"]
        assert "/api/v1/validation/agricultural" in data["paths"]


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])