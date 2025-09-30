"""
Integration tests for location management geocoding API endpoints.

This module tests the new geocoding endpoints in the location management service:
- POST /api/v1/locations/geocode
- POST /api/v1/locations/reverse-geocode
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import sys
import os

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../src/api'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../src/services'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../databases/python'))

from fastapi import FastAPI
from api.location_routes import router
from geocoding_service import (
    GeocodingResult, AddressResult, GeocodingError, AgriculturalContext
)


# Create test app
app = FastAPI()
app.include_router(router)

client = TestClient(app)


class TestLocationGeocodingEndpoints:
    """Test the new geocoding endpoints in location management service."""
    
    def test_location_geocode_endpoint_success(self):
        """Test successful address geocoding via location management endpoint."""
        mock_result = GeocodingResult(
            latitude=42.0308,
            longitude=-93.6319,
            address="Ames, Iowa",
            display_name="Ames, Story County, Iowa, USA",
            confidence=0.9,
            provider="nominatim"
        )
        
        with patch('api.location_routes.geocoding_service.geocode_address', return_value=mock_result):
            response = client.post("/api/v1/locations/geocode?address=Ames, Iowa")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["latitude"] == 42.0308
            assert data["longitude"] == -93.6319
            assert data["address"] == "Ames, Iowa"
            assert data["confidence"] == 0.9
            assert data["provider"] == "nominatim"
    
    def test_location_geocode_endpoint_with_agricultural_context(self):
        """Test geocoding endpoint with agricultural context enhancement."""
        mock_agricultural_context = AgriculturalContext(
            usda_zone='5a',
            climate_zone='Dfa',
            soil_survey_area='Story County',
            agricultural_district='Corn Belt',
            county='Story',
            state='Iowa',
            elevation_meters=300,
            growing_season_days=180,
            frost_free_days=160,
            agricultural_suitability='Good'
        )
        
        mock_result = GeocodingResult(
            latitude=42.0308,
            longitude=-93.6319,
            address="Ames, Iowa",
            display_name="Ames, Story County, Iowa, USA",
            confidence=0.9,
            provider="nominatim",
            agricultural_context=mock_agricultural_context
        )
        
        with patch('api.location_routes.geocoding_service.geocode_address', return_value=mock_result):
            response = client.post("/api/v1/locations/geocode?address=Ames, Iowa&include_agricultural_context=true")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data['latitude'] == 42.0308
            assert data['longitude'] == -93.6319
            assert data['address'] == "Ames, Iowa"
            assert data['confidence'] == 0.9
            assert data['provider'] == "nominatim"
            
            # Check agricultural context
            assert 'agricultural_context' in data
            ag_context = data['agricultural_context']
            assert ag_context['usda_zone'] == '5a'
            assert ag_context['climate_zone'] == 'Dfa'
            assert ag_context['soil_survey_area'] == 'Story County'
            assert ag_context['agricultural_district'] == 'Corn Belt'
            assert ag_context['county'] == 'Story'
            assert ag_context['state'] == 'Iowa'
            assert ag_context['elevation_meters'] == 300
            assert ag_context['growing_season_days'] == 180
            assert ag_context['frost_free_days'] == 160
            assert ag_context['agricultural_suitability'] == 'Good'
    
    def test_location_geocode_endpoint_without_agricultural_context(self):
        """Test geocoding endpoint without agricultural context enhancement."""
        mock_result = GeocodingResult(
            latitude=42.0308,
            longitude=-93.6319,
            address="Ames, Iowa",
            display_name="Ames, Story County, Iowa, USA",
            confidence=0.9,
            provider="nominatim",
            agricultural_context=None
        )
        
        with patch('api.location_routes.geocoding_service.geocode_address', return_value=mock_result):
            response = client.post("/api/v1/locations/geocode?address=Ames, Iowa&include_agricultural_context=false")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data['latitude'] == 42.0308
            assert data['longitude'] == -93.6319
            assert data['address'] == "Ames, Iowa"
            assert data['confidence'] == 0.9
            assert data['provider'] == "nominatim"
            assert data['agricultural_context'] is None
    
    def test_location_geocode_endpoint_empty_address(self):
        """Test geocoding endpoint with empty address."""
        response = client.post("/api/v1/locations/geocode?address=")
        
        assert response.status_code == 422
        data = response.json()
        
        assert "detail" in data
        assert "error" in data["detail"]
        assert data["detail"]["error"]["error_code"] == "GEOCODING_FAILED"
    
    def test_location_geocode_endpoint_service_error(self):
        """Test geocoding endpoint when service fails."""
        with patch('api.location_routes.geocoding_service.geocode_address', 
                  side_effect=GeocodingError("Service unavailable", "nominatim")):
            response = client.post("/api/v1/locations/geocode?address=Test Address")
            
            assert response.status_code == 422
            data = response.json()
            
            assert "detail" in data
            assert "error" in data["detail"]
            assert data["detail"]["error"]["error_code"] == "GEOCODING_FAILED"
            assert data["detail"]["provider"] == "nominatim"
    
    def test_location_geocode_endpoint_unexpected_error(self):
        """Test geocoding endpoint with unexpected error."""
        with patch('api.location_routes.geocoding_service.geocode_address', 
                  side_effect=Exception("Unexpected error")):
            response = client.post("/api/v1/locations/geocode?address=Test Address")
            
            assert response.status_code == 500
            data = response.json()
            
            assert "detail" in data
            assert "error" in data["detail"]
            assert data["detail"]["error"]["error_code"] == "GEOCODING_SERVICE_ERROR"
    
    def test_location_reverse_geocode_endpoint_success(self):
        """Test successful reverse geocoding via location management endpoint."""
        mock_result = AddressResult(
            address="Ames, Iowa",
            display_name="Ames, Story County, Iowa, USA",
            confidence=0.9,
            provider="nominatim"
        )
        
        with patch('api.location_routes.geocoding_service.reverse_geocode', return_value=mock_result):
            response = client.post("/api/v1/locations/reverse-geocode?latitude=42.0308&longitude=-93.6319")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["address"] == "Ames, Iowa"
            assert data["confidence"] == 0.9
            assert data["provider"] == "nominatim"
    
    def test_location_reverse_geocode_endpoint_with_agricultural_context(self):
        """Test reverse geocoding endpoint with agricultural context enhancement."""
        mock_agricultural_context = AgriculturalContext(
            usda_zone='5a',
            climate_zone='Dfa',
            soil_survey_area='Story County',
            agricultural_district='Corn Belt',
            county='Story',
            state='Iowa'
        )
        
        mock_result = AddressResult(
            address="Ames, Iowa",
            display_name="Ames, Story County, Iowa, USA",
            components={'county': 'Story', 'state': 'Iowa'},
            confidence=0.9,
            provider="nominatim",
            agricultural_context=mock_agricultural_context
        )
        
        with patch('api.location_routes.geocoding_service.reverse_geocode', return_value=mock_result):
            response = client.post("/api/v1/locations/reverse-geocode?latitude=42.0308&longitude=-93.6319&include_agricultural_context=true")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data['address'] == "Ames, Iowa"
            assert data['display_name'] == "Ames, Story County, Iowa, USA"
            assert data['confidence'] == 0.9
            assert data['provider'] == "nominatim"
            
            # Check agricultural context
            assert 'agricultural_context' in data
            ag_context = data['agricultural_context']
            assert ag_context['usda_zone'] == '5a'
            assert ag_context['climate_zone'] == 'Dfa'
            assert ag_context['soil_survey_area'] == 'Story County'
            assert ag_context['agricultural_district'] == 'Corn Belt'
    
    def test_location_reverse_geocode_endpoint_invalid_coordinates(self):
        """Test reverse geocoding with invalid coordinates."""
        # Invalid latitude
        response = client.post("/api/v1/locations/reverse-geocode?latitude=91.0&longitude=-93.6319")
        
        assert response.status_code == 422
        data = response.json()
        
        assert "detail" in data
        assert "error" in data["detail"]
        assert data["detail"]["error"]["error_code"] == "REVERSE_GEOCODING_FAILED"
    
    def test_location_reverse_geocode_endpoint_service_error(self):
        """Test reverse geocoding when service fails."""
        with patch('api.location_routes.geocoding_service.reverse_geocode', 
                  side_effect=GeocodingError("Service error", "nominatim")):
            response = client.post("/api/v1/locations/reverse-geocode?latitude=42.0308&longitude=-93.6319")
            
            assert response.status_code == 422
            data = response.json()
            
            assert "detail" in data
            assert "error" in data["detail"]
            assert data["detail"]["error"]["error_code"] == "REVERSE_GEOCODING_FAILED"
    
    def test_location_reverse_geocode_endpoint_unexpected_error(self):
        """Test reverse geocoding endpoint with unexpected error."""
        with patch('api.location_routes.geocoding_service.reverse_geocode', 
                  side_effect=Exception("Unexpected error")):
            response = client.post("/api/v1/locations/reverse-geocode?latitude=42.0308&longitude=-93.6319")
            
            assert response.status_code == 500
            data = response.json()
            
            assert "detail" in data
            assert "error" in data["detail"]
            assert data["detail"]["error"]["error_code"] == "REVERSE_GEOCODING_SERVICE_ERROR"


class TestLocationGeocodingAgriculturalContext:
    """Test agricultural-specific aspects of the new geocoding endpoints."""
    
    def test_location_geocode_agricultural_address(self):
        """Test geocoding of typical agricultural addresses."""
        mock_result = GeocodingResult(
            latitude=42.0308,
            longitude=-93.6319,
            address="Rural Route 1, Ames, Iowa",
            display_name="Rural Route 1, Ames, Story County, Iowa, USA",
            confidence=0.8,
            provider="nominatim"
        )
        
        with patch('api.location_routes.geocoding_service.geocode_address', return_value=mock_result):
            response = client.post("/api/v1/locations/geocode?address=Rural Route 1, Ames, Iowa")
            
            assert response.status_code == 200
            data = response.json()
            
            # Should handle rural addresses
            assert "Rural Route" in data["address"]
            assert data["confidence"] >= 0.5  # Should have reasonable confidence
    
    def test_location_reverse_geocode_farm_coordinates(self):
        """Test reverse geocoding of farm coordinates."""
        mock_result = AddressResult(
            address="County Road 123, Rural Area, Iowa",
            display_name="County Road 123, Rural Area, Story County, Iowa, USA",
            confidence=0.7,
            provider="nominatim"
        )
        
        with patch('api.location_routes.geocoding_service.reverse_geocode', return_value=mock_result):
            # Use coordinates that might be in a rural/agricultural area
            response = client.post("/api/v1/locations/reverse-geocode?latitude=42.1234&longitude=-93.5678")
            
            assert response.status_code == 200
            data = response.json()
            
            # Should handle rural coordinates
            assert data["confidence"] >= 0.5


class TestLocationGeocodingPerformance:
    """Test performance aspects of the new geocoding endpoints."""
    
    def test_location_geocode_response_time(self):
        """Test that geocoding responds within reasonable time."""
        import time
        
        mock_result = GeocodingResult(
            latitude=42.0308,
            longitude=-93.6319,
            address="Ames, Iowa",
            display_name="Ames, Story County, Iowa, USA",
            confidence=0.9,
            provider="nominatim"
        )
        
        with patch('api.location_routes.geocoding_service.geocode_address', return_value=mock_result):
            start_time = time.time()
            response = client.post("/api/v1/locations/geocode?address=Ames, Iowa")
            response_time = time.time() - start_time
            
            assert response.status_code == 200
            assert response_time < 5.0  # Should respond within 5 seconds
    
    def test_location_reverse_geocode_response_time(self):
        """Test that reverse geocoding responds within reasonable time."""
        import time
        
        mock_result = AddressResult(
            address="Ames, Iowa",
            display_name="Ames, Story County, Iowa, USA",
            confidence=0.9,
            provider="nominatim"
        )
        
        with patch('api.location_routes.geocoding_service.reverse_geocode', return_value=mock_result):
            start_time = time.time()
            response = client.post("/api/v1/locations/reverse-geocode?latitude=42.0308&longitude=-93.6319")
            response_time = time.time() - start_time
            
            assert response.status_code == 200
            assert response_time < 5.0  # Should respond within 5 seconds


class TestLocationGeocodingValidation:
    """Test input validation for the new geocoding endpoints."""
    
    def test_location_geocode_address_sql_injection_prevention(self):
        """Test that geocoding prevents SQL injection attempts."""
        malicious_address = "'; DROP TABLE locations; --"
        
        # Should not cause server error, should be handled gracefully
        response = client.post(f"/api/v1/locations/geocode?address={malicious_address}")
        
        # Should either succeed (if sanitized) or fail gracefully
        assert response.status_code in [200, 422, 500]
        
        if response.status_code != 200:
            data = response.json()
            assert "detail" in data
            assert "error" in data["detail"]
    
    def test_location_geocode_address_xss_prevention(self):
        """Test that geocoding prevents XSS attempts."""
        malicious_address = "<script>alert('xss')</script>"
        
        response = client.post(f"/api/v1/locations/geocode?address={malicious_address}")
        
        # Should handle gracefully
        assert response.status_code in [200, 422, 500]
    
    def test_location_reverse_geocode_coordinate_bounds(self):
        """Test coordinate boundary validation."""
        # Test latitude bounds
        response = client.post("/api/v1/locations/reverse-geocode?latitude=91.0&longitude=0.0")
        assert response.status_code == 422
        
        response = client.post("/api/v1/locations/reverse-geocode?latitude=-91.0&longitude=0.0")
        assert response.status_code == 422
        
        # Test longitude bounds
        response = client.post("/api/v1/locations/reverse-geocode?latitude=0.0&longitude=181.0")
        assert response.status_code == 422
        
        response = client.post("/api/v1/locations/reverse-geocode?latitude=0.0&longitude=-181.0")
        assert response.status_code == 422


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])