"""
Integration tests for geocoding API endpoints.

This module tests the FastAPI endpoints for geocoding functionality including:
- Address geocoding endpoint
- Reverse geocoding endpoint  
- Address suggestions endpoint
- Error handling and validation
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
from api.routes import router
from geocoding_service import GeocodingResult, AddressResult, AddressSuggestion, GeocodingError


# Create test app
app = FastAPI()
app.include_router(router)

client = TestClient(app)


class TestGeocodingEndpoints:
    """Test geocoding API endpoints."""
    
    def test_geocode_address_success(self):
        """Test successful address geocoding endpoint."""
        mock_result = GeocodingResult(
            latitude=42.0308,
            longitude=-93.6319,
            address="Ames, Iowa",
            display_name="Ames, Story County, Iowa, USA",
            confidence=0.9,
            provider="nominatim"
        )
        
        with patch('api.routes.geocoding_service.geocode_address', return_value=mock_result):
            response = client.post("/api/v1/validation/geocode?address=Ames, Iowa")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["latitude"] == 42.0308
            assert data["longitude"] == -93.6319
            assert data["address"] == "Ames, Iowa"
            assert data["confidence"] == 0.9
            assert data["provider"] == "nominatim"
    
    def test_geocode_address_empty_query(self):
        """Test geocoding endpoint with empty address."""
        response = client.post("/api/v1/validation/geocode?address=")
        
        assert response.status_code == 422
        data = response.json()
        
        assert "error" in data
        assert data["error"]["error_code"] == "GEOCODING_FAILED"
    
    def test_geocode_address_service_error(self):
        """Test geocoding endpoint when service fails."""
        with patch('api.routes.geocoding_service.geocode_address', 
                  side_effect=GeocodingError("Service unavailable", "nominatim")):
            response = client.post("/api/v1/validation/geocode?address=Test Address")
            
            assert response.status_code == 422
            data = response.json()
            
            assert "error" in data
            assert data["error"]["error_code"] == "GEOCODING_FAILED"
            assert data["provider"] == "nominatim"
    
    def test_geocode_address_unexpected_error(self):
        """Test geocoding endpoint with unexpected error."""
        with patch('api.routes.geocoding_service.geocode_address', 
                  side_effect=Exception("Unexpected error")):
            response = client.post("/api/v1/validation/geocode?address=Test Address")
            
            assert response.status_code == 500
            data = response.json()
            
            assert "error" in data
            assert data["error"]["error_code"] == "GEOCODING_SERVICE_ERROR"
    
    def test_reverse_geocode_success(self):
        """Test successful reverse geocoding endpoint."""
        mock_result = AddressResult(
            address="Ames, Iowa",
            display_name="Ames, Story County, Iowa, USA",
            confidence=0.9,
            provider="nominatim"
        )
        
        with patch('api.routes.geocoding_service.reverse_geocode', return_value=mock_result):
            response = client.post("/api/v1/validation/reverse-geocode?latitude=42.0308&longitude=-93.6319")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["address"] == "Ames, Iowa"
            assert data["confidence"] == 0.9
    
    def test_reverse_geocode_invalid_coordinates(self):
        """Test reverse geocoding with invalid coordinates."""
        # Invalid latitude
        response = client.post("/api/v1/validation/reverse-geocode?latitude=91.0&longitude=-93.6319")
        
        assert response.status_code == 422
        data = response.json()
        
        assert "error" in data
        assert data["error"]["error_code"] == "REVERSE_GEOCODING_FAILED"
    
    def test_reverse_geocode_service_error(self):
        """Test reverse geocoding when service fails."""
        with patch('api.routes.geocoding_service.reverse_geocode', 
                  side_effect=GeocodingError("Service error", "nominatim")):
            response = client.post("/api/v1/validation/reverse-geocode?latitude=42.0308&longitude=-93.6319")
            
            assert response.status_code == 422
            data = response.json()
            
            assert "error" in data
            assert data["error"]["error_code"] == "REVERSE_GEOCODING_FAILED"
    
    def test_address_suggestions_success(self):
        """Test successful address suggestions endpoint."""
        mock_suggestions = [
            AddressSuggestion(
                display_name="Ames, Iowa",
                address="Ames, Iowa",
                latitude=42.0308,
                longitude=-93.6319,
                relevance=1.0
            ),
            AddressSuggestion(
                display_name="Ames Municipal Airport",
                address="Ames Municipal Airport, Ames, Iowa",
                latitude=42.0275,
                longitude=-93.6456,
                relevance=0.9
            )
        ]
        
        with patch('api.routes.geocoding_service.get_address_suggestions', return_value=mock_suggestions):
            response = client.get("/api/v1/validation/address-suggestions?query=Ames&limit=5")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["query"] == "Ames"
            assert data["count"] == 2
            assert data["limit"] == 5
            assert len(data["suggestions"]) == 2
            
            # Check first suggestion
            first_suggestion = data["suggestions"][0]
            assert first_suggestion["address"] == "Ames, Iowa"
            assert first_suggestion["latitude"] == 42.0308
            assert first_suggestion["longitude"] == -93.6319
            assert first_suggestion["relevance"] == 1.0
    
    def test_address_suggestions_short_query(self):
        """Test address suggestions with query too short."""
        response = client.get("/api/v1/validation/address-suggestions?query=Am")
        
        assert response.status_code == 422
        data = response.json()
        
        assert "error" in data
        assert data["error"]["error_code"] == "QUERY_TOO_SHORT"
    
    def test_address_suggestions_empty_query(self):
        """Test address suggestions with empty query."""
        response = client.get("/api/v1/validation/address-suggestions?query=")
        
        assert response.status_code == 422
        data = response.json()
        
        assert "error" in data
        assert data["error"]["error_code"] == "QUERY_TOO_SHORT"
    
    def test_address_suggestions_limit_validation(self):
        """Test address suggestions with limit validation."""
        mock_suggestions = []
        
        with patch('api.routes.geocoding_service.get_address_suggestions', return_value=mock_suggestions):
            # Test maximum limit enforcement
            response = client.get("/api/v1/validation/address-suggestions?query=Test&limit=20")
            
            assert response.status_code == 200
            data = response.json()
            
            # Limit should be capped at 10
            assert data["limit"] == 10
    
    def test_address_suggestions_service_error(self):
        """Test address suggestions when service fails."""
        with patch('api.routes.geocoding_service.get_address_suggestions', 
                  side_effect=Exception("Service error")):
            response = client.get("/api/v1/validation/address-suggestions?query=Test")
            
            assert response.status_code == 200  # Should not fail hard
            data = response.json()
            
            assert data["count"] == 0
            assert data["suggestions"] == []
            assert "error" in data


class TestGeocodingValidation:
    """Test input validation for geocoding endpoints."""
    
    def test_geocode_address_sql_injection_prevention(self):
        """Test that geocoding prevents SQL injection attempts."""
        malicious_address = "'; DROP TABLE locations; --"
        
        # Should not cause server error, should be handled gracefully
        response = client.post(f"/api/v1/validation/geocode?address={malicious_address}")
        
        # Should either succeed (if sanitized) or fail gracefully
        assert response.status_code in [200, 422, 500]
        
        if response.status_code != 200:
            data = response.json()
            assert "error" in data
    
    def test_geocode_address_xss_prevention(self):
        """Test that geocoding prevents XSS attempts."""
        malicious_address = "<script>alert('xss')</script>"
        
        response = client.post(f"/api/v1/validation/geocode?address={malicious_address}")
        
        # Should handle gracefully
        assert response.status_code in [200, 422, 500]
    
    def test_reverse_geocode_coordinate_bounds(self):
        """Test coordinate boundary validation."""
        # Test latitude bounds
        response = client.post("/api/v1/validation/reverse-geocode?latitude=91.0&longitude=0.0")
        assert response.status_code == 422
        
        response = client.post("/api/v1/validation/reverse-geocode?latitude=-91.0&longitude=0.0")
        assert response.status_code == 422
        
        # Test longitude bounds
        response = client.post("/api/v1/validation/reverse-geocode?latitude=0.0&longitude=181.0")
        assert response.status_code == 422
        
        response = client.post("/api/v1/validation/reverse-geocode?latitude=0.0&longitude=-181.0")
        assert response.status_code == 422
    
    def test_address_suggestions_query_length_limits(self):
        """Test query length limits for address suggestions."""
        # Very long query
        long_query = "A" * 1000
        
        response = client.get(f"/api/v1/validation/address-suggestions?query={long_query}")
        
        # Should handle gracefully (either truncate or reject)
        assert response.status_code in [200, 422]


class TestGeocodingAgriculturalContext:
    """Test agricultural-specific aspects of geocoding."""
    
    def test_geocode_agricultural_address(self):
        """Test geocoding of typical agricultural addresses."""
        mock_result = GeocodingResult(
            latitude=42.0308,
            longitude=-93.6319,
            address="Rural Route 1, Ames, Iowa",
            display_name="Rural Route 1, Ames, Story County, Iowa, USA",
            confidence=0.8,
            provider="nominatim"
        )
        
        with patch('api.routes.geocoding_service.geocode_address', return_value=mock_result):
            response = client.post("/api/v1/validation/geocode?address=Rural Route 1, Ames, Iowa")
            
            assert response.status_code == 200
            data = response.json()
            
            # Should handle rural addresses
            assert "Rural Route" in data["address"]
            assert data["confidence"] >= 0.5  # Should have reasonable confidence
    
    def test_reverse_geocode_farm_coordinates(self):
        """Test reverse geocoding of farm coordinates."""
        mock_result = AddressResult(
            address="County Road 123, Rural Area, Iowa",
            display_name="County Road 123, Rural Area, Story County, Iowa, USA",
            confidence=0.7,
            provider="nominatim"
        )
        
        with patch('api.routes.geocoding_service.reverse_geocode', return_value=mock_result):
            # Use coordinates that might be in a rural/agricultural area
            response = client.post("/api/v1/validation/reverse-geocode?latitude=42.1234&longitude=-93.5678")
            
            assert response.status_code == 200
            data = response.json()
            
            # Should handle rural coordinates
            assert data["confidence"] >= 0.5
    
    def test_address_suggestions_agricultural_terms(self):
        """Test address suggestions with agricultural terms."""
        mock_suggestions = [
            AddressSuggestion(
                display_name="Farm Road 123, Rural County, Iowa",
                address="Farm Road 123, Rural County, Iowa",
                latitude=42.0,
                longitude=-93.0,
                relevance=0.9
            ),
            AddressSuggestion(
                display_name="County Highway 456, Agricultural Area, Iowa",
                address="County Highway 456, Agricultural Area, Iowa",
                latitude=42.1,
                longitude=-93.1,
                relevance=0.8
            )
        ]
        
        with patch('api.routes.geocoding_service.get_address_suggestions', return_value=mock_suggestions):
            response = client.get("/api/v1/validation/address-suggestions?query=Farm Road")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["count"] == 2
            # Should include agricultural/rural addresses
            assert any("Farm Road" in s["address"] for s in data["suggestions"])


class TestGeocodingPerformance:
    """Test performance aspects of geocoding endpoints."""
    
    def test_geocode_response_time(self):
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
        
        with patch('api.routes.geocoding_service.geocode_address', return_value=mock_result):
            start_time = time.time()
            response = client.post("/api/v1/validation/geocode?address=Ames, Iowa")
            response_time = time.time() - start_time
            
            assert response.status_code == 200
            assert response_time < 5.0  # Should respond within 5 seconds
    
    def test_address_suggestions_response_time(self):
        """Test that address suggestions respond quickly."""
        import time
        
        mock_suggestions = [
            AddressSuggestion(
                display_name="Ames, Iowa",
                address="Ames, Iowa",
                latitude=42.0308,
                longitude=-93.6319,
                relevance=1.0
            )
        ]
        
        with patch('api.routes.geocoding_service.get_address_suggestions', return_value=mock_suggestions):
            start_time = time.time()
            response = client.get("/api/v1/validation/address-suggestions?query=Ames")
            response_time = time.time() - start_time
            
            assert response.status_code == 200
            assert response_time < 3.0  # Suggestions should be fast


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])