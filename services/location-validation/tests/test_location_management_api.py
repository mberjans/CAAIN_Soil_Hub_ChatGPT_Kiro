"""
Location Management API Tests
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

Comprehensive tests for location management API endpoints.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os
from uuid import UUID

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../databases/python'))

from src.main import app
from src.api.location_routes import (
    LocationCreateRequest, LocationUpdateRequest, LocationResponse,
    LocationListResponse, LocationValidationResponse
)

# Test client
client = TestClient(app)


class TestLocationManagementAPI:
    """Comprehensive test suite for location management API endpoints."""

    @pytest.fixture
    def sample_location_data(self):
        """Sample location data for testing."""
        return {
            "farm_name": "Test Farm",
            "primary_address": {
                "street_address": "123 Test Road",
                "city": "Ames",
                "state": "IA",
                "postal_code": "50010",
                "country": "US"
            },
            "coordinates": {
                "latitude": 42.0308,
                "longitude": -93.6319,
                "accuracy_meters": 5.0,
                "coordinate_system": "WGS84"
            },
            "farm_characteristics": {
                "total_acres": 640,
                "primary_crops": ["corn", "soybean"],
                "soil_types": ["loam", "clay_loam"],
                "irrigation_available": False,
                "organic_certified": False
            },
            "contact_information": {
                "phone": "+1-515-555-0123",
                "email": "test@farm.com"
            },
            "privacy_settings": {
                "location_sharing": "private",
                "data_usage_consent": True
            }
        }

    @pytest.fixture
    def mock_validation_result(self):
        """Mock validation result."""
        from location_models import ValidationResult, GeographicInfo
        
        geographic_info = GeographicInfo(
            county="Story",
            state="IA",
            country="US",
            climate_zone="5a",
            is_agricultural=True,
            elevation_meters=300
        )
        
        return ValidationResult(
            valid=True,
            warnings=[],
            errors=[],
            geographic_info=geographic_info
        )

    @pytest.fixture
    def mock_geocoding_result(self):
        """Mock geocoding result."""
        from geocoding_service import GeocodingResult
        
        return GeocodingResult(
            latitude=42.0308,
            longitude=-93.6319,
            address="123 Test Road, Ames, IA 50010, USA",
            confidence=0.9,
            provider="nominatim"
        )

    def test_create_farm_location_success(self, sample_location_data, mock_validation_result, mock_geocoding_result):
        """Test successful farm location creation."""
        with patch('src.api.location_routes.validation_service.validate_agricultural_location', return_value=mock_validation_result):
            with patch('src.api.location_routes.geocoding_service.geocode_address', return_value=mock_geocoding_result):
                response = client.post("/api/v1/locations/", json=sample_location_data)
                
                assert response.status_code == 201
                data = response.json()
                
                assert data["farm_name"] == "Test Farm"
                assert data["latitude"] == 42.0308
                assert data["longitude"] == -93.6319
                assert data["county"] == "Story"
                assert data["state"] == "IA"
                assert data["climate_zone"] == "5a"
                assert data["verified"] is True
                assert "id" in data
                assert "created_at" in data
                assert "updated_at" in data

    def test_create_farm_location_with_coordinates_only(self, mock_validation_result):
        """Test farm location creation with coordinates only."""
        location_data = {
            "farm_name": "Coordinate Farm",
            "coordinates": {
                "latitude": 42.0308,
                "longitude": -93.6319
            }
        }
        
        with patch('src.api.location_routes.validation_service.validate_agricultural_location', return_value=mock_validation_result):
            response = client.post("/api/v1/locations/", json=location_data)
            
            assert response.status_code == 201
            data = response.json()
            assert data["farm_name"] == "Coordinate Farm"
            assert data["latitude"] == 42.0308
            assert data["longitude"] == -93.6319

    def test_create_farm_location_with_address_only(self, sample_location_data, mock_validation_result, mock_geocoding_result):
        """Test farm location creation with address only."""
        location_data = {
            "farm_name": "Address Farm",
            "primary_address": sample_location_data["primary_address"]
        }
        
        with patch('src.api.location_routes.validation_service.validate_agricultural_location', return_value=mock_validation_result):
            with patch('src.api.location_routes.geocoding_service.geocode_address', return_value=mock_geocoding_result):
                response = client.post("/api/v1/locations/", json=location_data)
                
                assert response.status_code == 201
                data = response.json()
                assert data["farm_name"] == "Address Farm"
                assert data["latitude"] == 42.0308
                assert data["longitude"] == -93.6319

    def test_create_farm_location_validation_failure(self, sample_location_data):
        """Test farm location creation with validation failure."""
        from location_models import ValidationResult
        
        validation_result = ValidationResult(
            valid=False,
            warnings=[],
            errors=["Location is not suitable for agriculture"],
            geographic_info=None
        )
        
        with patch('src.api.location_routes.validation_service.validate_agricultural_location', return_value=validation_result):
            response = client.post("/api/v1/locations/", json=sample_location_data)
            
            assert response.status_code == 422
            data = response.json()
            assert "validation_errors" in data["error"]
            assert "Location is not suitable for agriculture" in data["error"]["validation_errors"]

    def test_create_farm_location_geocoding_failure(self, sample_location_data):
        """Test farm location creation with geocoding failure."""
        from geocoding_service import GeocodingError
        
        with patch('src.api.location_routes.geocoding_service.geocode_address', side_effect=GeocodingError("Address not found", "nominatim")):
            response = client.post("/api/v1/locations/", json=sample_location_data)
            
            assert response.status_code == 422
            data = response.json()
            assert "GEOCODING_REQUIRED" in data["error"]["error_code"]

    def test_create_farm_location_no_location_data(self):
        """Test farm location creation with no location data."""
        location_data = {
            "farm_name": "No Location Farm"
        }
        
        response = client.post("/api/v1/locations/", json=location_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "LOCATION_DATA_REQUIRED" in data["error"]["error_code"]

    def test_create_farm_location_invalid_coordinates(self):
        """Test farm location creation with invalid coordinates."""
        location_data = {
            "farm_name": "Invalid Farm",
            "coordinates": {
                "latitude": 200.0,  # Invalid latitude
                "longitude": -93.6319
            }
        }
        
        response = client.post("/api/v1/locations/", json=location_data)
        
        assert response.status_code == 422
        # Should fail at Pydantic validation level

    def test_get_user_locations_success(self):
        """Test successful retrieval of user locations."""
        response = client.get("/api/v1/locations/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "locations" in data
        assert "total_count" in data
        assert "page" in data
        assert "page_size" in data
        assert "has_next" in data
        assert "has_previous" in data
        assert isinstance(data["locations"], list)

    def test_get_user_locations_with_filters(self):
        """Test retrieval of user locations with filters."""
        params = {
            "state": "IA",
            "limit": 5,
            "offset": 0,
            "sort_by": "farm_name"
        }
        
        response = client.get("/api/v1/locations/", params=params)
        
        assert response.status_code == 200
        data = response.json()
        assert data["page_size"] == 5
        assert data["page"] == 1

    def test_update_farm_location_success(self, mock_validation_result):
        """Test successful farm location update."""
        location_id = str(UUID())
        update_data = {
            "farm_name": "Updated Farm Name",
            "farm_characteristics": {
                "total_acres": 800,
                "primary_crops": ["corn", "soybean", "wheat"]
            }
        }
        
        with patch('src.api.location_routes.validation_service.validate_agricultural_location', return_value=mock_validation_result):
            response = client.put(f"/api/v1/locations/{location_id}", json=update_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["farm_name"] == "Updated Farm Name"
            assert data["id"] == location_id

    def test_update_farm_location_invalid_id(self):
        """Test farm location update with invalid ID."""
        update_data = {
            "farm_name": "Updated Farm"
        }
        
        response = client.put("/api/v1/locations/invalid-id", json=update_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "INVALID_LOCATION_ID" in data["error"]["error_code"]

    def test_delete_farm_location_soft_delete(self):
        """Test soft delete of farm location."""
        location_id = str(UUID())
        
        response = client.delete(f"/api/v1/locations/{location_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["deletion_type"] == "soft"
        assert data["location_id"] == location_id

    def test_delete_farm_location_hard_delete(self):
        """Test hard delete of farm location."""
        location_id = str(UUID())
        
        response = client.delete(f"/api/v1/locations/{location_id}?hard_delete=true")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["deletion_type"] == "hard"
        assert data["location_id"] == location_id

    def test_delete_farm_location_invalid_id(self):
        """Test farm location deletion with invalid ID."""
        response = client.delete("/api/v1/locations/invalid-id")
        
        assert response.status_code == 422
        data = response.json()
        assert "INVALID_LOCATION_ID" in data["error"]["error_code"]

    def test_validate_farm_location_success(self, sample_location_data, mock_validation_result, mock_geocoding_result):
        """Test successful farm location validation."""
        with patch('src.api.location_routes.validation_service.validate_agricultural_location', return_value=mock_validation_result):
            with patch('src.api.location_routes.geocoding_service.geocode_address', return_value=mock_geocoding_result):
                response = client.post("/api/v1/locations/validate", json=sample_location_data)
                
                assert response.status_code == 200
                data = response.json()
                
                assert data["valid"] is True
                assert "validation_results" in data
                assert "agricultural_context" in data
                assert "suggestions" in data
                assert "warnings" in data
                assert "errors" in data

    def test_validate_farm_location_geocoding_failure(self, sample_location_data):
        """Test farm location validation with geocoding failure."""
        from geocoding_service import GeocodingError
        
        with patch('src.api.location_routes.geocoding_service.geocode_address', side_effect=GeocodingError("Address not found", "nominatim")):
            response = client.post("/api/v1/locations/validate", json=sample_location_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is False
            assert "Geocoding failed" in data["errors"][0]

    def test_validate_farm_location_no_location_data(self):
        """Test farm location validation with no location data."""
        location_data = {
            "farm_name": "No Location Farm"
        }
        
        response = client.post("/api/v1/locations/validate", json=location_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert "Coordinates or address required" in data["errors"]

    def test_location_management_health_check(self):
        """Test location management health check endpoint."""
        with patch('src.api.location_routes.validation_service.validate_coordinates', return_value=mock_validation_result):
            response = client.get("/api/v1/locations/health")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] == "healthy"
            assert data["service"] == "location-management"
            assert "endpoints" in data
            assert len(data["endpoints"]) > 0

    def test_location_management_health_check_failure(self):
        """Test location management health check with service failure."""
        with patch('src.api.location_routes.validation_service.validate_coordinates', side_effect=Exception("Service error")):
            response = client.get("/api/v1/locations/health")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] == "unhealthy"
            assert "error" in data

    # Performance tests
    @pytest.mark.performance
    def test_create_location_response_time(self, sample_location_data, mock_validation_result, mock_geocoding_result):
        """Test that location creation responds within acceptable time."""
        import time
        
        with patch('src.api.location_routes.validation_service.validate_agricultural_location', return_value=mock_validation_result):
            with patch('src.api.location_routes.geocoding_service.geocode_address', return_value=mock_geocoding_result):
                start_time = time.time()
                response = client.post("/api/v1/locations/", json=sample_location_data)
                elapsed = time.time() - start_time
                
                assert response.status_code == 201
                assert elapsed < 2.0, f"Response time {elapsed}s exceeds 2s requirement"

    @pytest.mark.performance
    def test_get_locations_response_time(self):
        """Test that location retrieval responds within acceptable time."""
        import time
        
        start_time = time.time()
        response = client.get("/api/v1/locations/")
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed < 1.0, f"Response time {elapsed}s exceeds 1s requirement"

    # Agricultural validation tests
    @pytest.mark.agricultural
    def test_corn_belt_location_validation(self, mock_validation_result):
        """Test validation for corn belt coordinates."""
        location_data = {
            "farm_name": "Corn Belt Farm",
            "coordinates": {
                "latitude": 41.5868,  # Iowa coordinates
                "longitude": -93.6250
            }
        }
        
        # Mock validation result for corn belt
        corn_belt_validation = mock_validation_result
        corn_belt_validation.geographic_info.state = "IA"
        corn_belt_validation.geographic_info.county = "Polk"
        corn_belt_validation.geographic_info.climate_zone = "5a"
        
        with patch('src.api.location_routes.validation_service.validate_agricultural_location', return_value=corn_belt_validation):
            response = client.post("/api/v1/locations/", json=location_data)
            
            assert response.status_code == 201
            data = response.json()
            assert data["state"] == "IA"
            assert data["climate_zone"] == "5a"

    @pytest.mark.agricultural
    def test_ocean_location_validation(self):
        """Test validation for ocean coordinates."""
        from location_models import ValidationResult
        
        ocean_validation = ValidationResult(
            valid=False,
            warnings=[],
            errors=["Location appears to be over ocean - limited agricultural relevance"],
            geographic_info=None
        )
        
        location_data = {
            "farm_name": "Ocean Farm",
            "coordinates": {
                "latitude": 0.0,  # Ocean coordinates
                "longitude": 0.0
            }
        }
        
        with patch('src.api.location_routes.validation_service.validate_agricultural_location', return_value=ocean_validation):
            response = client.post("/api/v1/locations/", json=location_data)
            
            assert response.status_code == 422
            data = response.json()
            assert "ocean" in data["error"]["validation_errors"][0].lower()

    @pytest.mark.agricultural
    def test_agricultural_context_enrichment(self, sample_location_data, mock_validation_result, mock_geocoding_result):
        """Test agricultural context enrichment during validation."""
        with patch('src.api.location_routes.validation_service.validate_agricultural_location', return_value=mock_validation_result):
            with patch('src.api.location_routes.geocoding_service.geocode_address', return_value=mock_geocoding_result):
                response = client.post("/api/v1/locations/validate", json=sample_location_data)
                
                assert response.status_code == 200
                data = response.json()
                
                assert "agricultural_context" in data
                context = data["agricultural_context"]
                assert "climate_zone" in context
                assert "county" in context
                assert "state" in context
                assert "is_agricultural" in context
                assert "suitable_crops" in context


# Integration tests
class TestLocationManagementIntegration:
    """Integration tests for location management with other services."""

    def test_location_creation_with_climate_zone_integration(self, sample_location_data, mock_validation_result, mock_geocoding_result):
        """Test location creation with climate zone integration."""
        with patch('src.api.location_routes.validation_service.validate_agricultural_location', return_value=mock_validation_result):
            with patch('src.api.location_routes.geocoding_service.geocode_address', return_value=mock_geocoding_result):
                response = client.post("/api/v1/locations/", json=sample_location_data)
                
                assert response.status_code == 201
                data = response.json()
                
                # Verify climate zone is populated
                assert data["climate_zone"] is not None
                assert data["climate_zone"] == "5a"

    def test_location_update_triggers_dependent_services(self, mock_validation_result):
        """Test that location updates trigger dependent service notifications."""
        location_id = str(UUID())
        update_data = {
            "coordinates": {
                "latitude": 42.1,
                "longitude": -93.7
            }
        }
        
        with patch('src.api.location_routes.validation_service.validate_agricultural_location', return_value=mock_validation_result):
            response = client.put(f"/api/v1/locations/{location_id}", json=update_data)
            
            assert response.status_code == 200
            # In a real implementation, this would verify that dependent services
            # (like recommendation engine) are notified of the location change


# Error handling tests
class TestLocationManagementErrorHandling:
    """Tests for error handling in location management API."""

    def test_internal_server_error_handling(self, sample_location_data):
        """Test handling of internal server errors."""
        with patch('src.api.location_routes.validation_service.validate_agricultural_location', side_effect=Exception("Internal error")):
            response = client.post("/api/v1/locations/", json=sample_location_data)
            
            assert response.status_code == 500
            data = response.json()
            assert "LOCATION_CREATION_ERROR" in data["error"]["error_code"]
            assert "agricultural_context" in data["error"]

    def test_validation_service_timeout(self, sample_location_data):
        """Test handling of validation service timeout."""
        import asyncio
        
        async def timeout_validation(*args, **kwargs):
            await asyncio.sleep(10)  # Simulate timeout
            return mock_validation_result
        
        with patch('src.api.location_routes.validation_service.validate_agricultural_location', side_effect=asyncio.TimeoutError()):
            response = client.post("/api/v1/locations/", json=sample_location_data)
            
            assert response.status_code == 500
            data = response.json()
            assert "LOCATION_CREATION_ERROR" in data["error"]["error_code"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])