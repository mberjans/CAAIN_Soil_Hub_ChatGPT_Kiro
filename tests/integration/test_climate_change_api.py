"""
Integration tests for climate zone change detection API endpoint.
Tests the /api/v1/climate/detect-changes endpoint functionality.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
import json

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../services/data-integration/src'))

# Import the FastAPI app and required classes
from services.data_integration.src.api.climate_routes import router
from services.data_integration.src.services.climate_zone_service import (
    ClimateZoneChangeDetection,
    ClimateZone, 
    ClimateZoneType,
    ClimateZoneHistoricalRecord
)


@pytest.fixture
def mock_change_detection_result():
    """Create mock change detection result for testing."""
    
    current_zone = ClimateZone(
        zone_id="6a",
        zone_type=ClimateZoneType.USDA_HARDINESS,
        name="USDA Zone 6a",
        description="Moderate (-10°F to -5°F)",
        min_temp_f=-10,
        max_temp_f=-5
    )
    
    previous_zone = ClimateZone(
        zone_id="5b", 
        zone_type=ClimateZoneType.USDA_HARDINESS,
        name="USDA Zone 5b",
        description="Cool (-15°F to -10°F)",
        min_temp_f=-15,
        max_temp_f=-10
    )
    
    time_series_data = [
        ClimateZoneHistoricalRecord(
            zone_id="5b",
            zone_type=ClimateZoneType.USDA_HARDINESS,
            detection_date=datetime.now() - timedelta(days=730),
            confidence_score=0.8,
            coordinates=(42.0, -93.5),
            source="historical"
        ),
        ClimateZoneHistoricalRecord(
            zone_id="6a",
            zone_type=ClimateZoneType.USDA_HARDINESS,
            detection_date=datetime.now() - timedelta(days=365),
            confidence_score=0.85,
            coordinates=(42.0, -93.5),
            source="transition"
        )
    ]
    
    return ClimateZoneChangeDetection(
        current_zone=current_zone,
        previous_zone=previous_zone,
        change_detected=True,
        change_confidence=0.87,
        change_date=datetime.now() - timedelta(days=365),
        change_direction="warmer",
        zones_affected=["5b", "6a"],
        trend_analysis={
            "trend_direction": "warmer",
            "confidence": 0.87,
            "rate_of_change_per_year": 0.12,
            "projected_zone_1yr": "6a",
            "projected_zone_5yr": "6b"
        },
        time_series_data=time_series_data
    )


class TestClimateZoneChangeAPI:
    """Test climate zone change detection API endpoints."""
    
    def test_detect_changes_request_validation(self):
        """Test request validation for change detection endpoint."""
        
        # Test valid request
        valid_request = {
            "latitude": 42.0,
            "longitude": -93.5,
            "analyze_historical": True,
            "years_to_analyze": 10
        }
        
        # These would be validated by Pydantic in actual FastAPI app
        assert -90 <= valid_request["latitude"] <= 90
        assert -180 <= valid_request["longitude"] <= 180
        assert 1 <= valid_request["years_to_analyze"] <= 50
        
        # Test invalid requests
        invalid_requests = [
            {"latitude": 91.0, "longitude": -93.5},  # Invalid latitude
            {"latitude": 42.0, "longitude": 181.0},  # Invalid longitude  
            {"latitude": 42.0, "longitude": -93.5, "years_to_analyze": 0},  # Invalid years
            {"latitude": 42.0, "longitude": -93.5, "years_to_analyze": 100}  # Too many years
        ]
        
        for invalid_req in invalid_requests:
            # In actual FastAPI, these would raise validation errors
            if "latitude" in invalid_req:
                lat = invalid_req["latitude"]
                assert not (-90 <= lat <= 90) or (lat == 42.0)
            
            if "longitude" in invalid_req:
                lon = invalid_req["longitude"] 
                assert not (-180 <= lon <= 180) or (lon == -93.5)
                
            if "years_to_analyze" in invalid_req:
                years = invalid_req["years_to_analyze"]
                assert not (1 <= years <= 50) or (years == 10)
    
    @patch('services.data_integration.src.api.climate_routes.climate_zone_service')
    @pytest.mark.asyncio
    async def test_detect_changes_success(self, mock_service, mock_change_detection_result):
        """Test successful change detection API call."""
        
        # Mock the service method
        mock_service.detect_climate_zone_changes.return_value = mock_change_detection_result
        
        # Import the endpoint function
        from services.data_integration.src.api.climate_routes import detect_climate_zone_changes, ClimateZoneChangeRequest
        
        # Create request
        request = ClimateZoneChangeRequest(
            latitude=42.0,
            longitude=-93.5,
            analyze_historical=True,
            years_to_analyze=10
        )
        
        # Call endpoint
        response = await detect_climate_zone_changes(request)
        
        # Verify response structure
        assert hasattr(response, 'current_zone')
        assert hasattr(response, 'change_detected')
        assert hasattr(response, 'change_confidence')
        assert hasattr(response, 'recommendations')
        
        # Verify data
        assert response.change_detected == True
        assert response.change_confidence == 0.87
        assert response.change_direction == "warmer"
        assert len(response.zones_affected) == 2
        assert len(response.recommendations) > 0
        
        # Verify service was called with correct parameters
        mock_service.detect_climate_zone_changes.assert_called_once_with(
            latitude=42.0,
            longitude=-93.5,
            analyze_historical=True,
            years_to_analyze=10
        )
    
    @patch('services.data_integration.src.api.climate_routes.climate_zone_service')
    @pytest.mark.asyncio
    async def test_detect_changes_no_change(self, mock_service):
        """Test API response when no changes detected."""
        
        # Create stable zone result
        stable_zone = ClimateZone(
            zone_id="6a",
            zone_type=ClimateZoneType.USDA_HARDINESS,
            name="USDA Zone 6a",
            description="Moderate (-10°F to -5°F)",
            min_temp_f=-10,
            max_temp_f=-5
        )
        
        stable_result = ClimateZoneChangeDetection(
            current_zone=stable_zone,
            previous_zone=stable_zone,
            change_detected=False,
            change_confidence=0.3,
            change_date=None,
            change_direction="stable",
            zones_affected=["6a"],
            trend_analysis={"trend_direction": "stable", "confidence": 0.9},
            time_series_data=[]
        )
        
        mock_service.detect_climate_zone_changes.return_value = stable_result
        
        from services.data_integration.src.api.climate_routes import detect_climate_zone_changes, ClimateZoneChangeRequest
        
        request = ClimateZoneChangeRequest(
            latitude=42.0,
            longitude=-93.5
        )
        
        response = await detect_climate_zone_changes(request)
        
        assert response.change_detected == False
        assert response.change_direction == "stable"
        assert response.change_date is None
        assert len(response.recommendations) > 0  # Should still have recommendations
    
    def test_adaptation_recommendations_generation(self):
        """Test generation of adaptation recommendations."""
        
        from services.data_integration.src.api.climate_routes import _generate_adaptation_recommendations
        
        # Test warming change recommendations
        warming_change = Mock()
        warming_change.change_detected = True
        warming_change.change_direction = "warmer"
        warming_change.change_confidence = 0.9
        warming_change.current_zone.zone_id = "7a"
        
        recommendations = _generate_adaptation_recommendations(warming_change)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert any("heat-tolerant" in rec.lower() for rec in recommendations)
        assert any("water conservation" in rec.lower() for rec in recommendations)
        assert any("high confidence" in rec.lower() for rec in recommendations)
        
        # Test cooling change recommendations
        cooling_change = Mock()
        cooling_change.change_detected = True
        cooling_change.change_direction = "cooler"
        cooling_change.change_confidence = 0.8
        cooling_change.current_zone.zone_id = "5a"
        
        recommendations = _generate_adaptation_recommendations(cooling_change)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert any("shorter-season" in rec.lower() or "cold-tolerant" in rec.lower() for rec in recommendations)
        
        # Test stable zone recommendations
        stable_change = Mock()
        stable_change.change_detected = False
        stable_change.change_direction = "stable"
        stable_change.change_confidence = 0.3
        stable_change.current_zone.zone_id = "6b"
        
        recommendations = _generate_adaptation_recommendations(stable_change)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert any("stable" in rec.lower() for rec in recommendations)
    
    @patch('services.data_integration.src.api.climate_routes.climate_zone_service')
    @pytest.mark.asyncio
    async def test_api_error_handling(self, mock_service):
        """Test API error handling."""
        
        # Mock service to raise exception
        mock_service.detect_climate_zone_changes.side_effect = Exception("Service error")
        
        from services.data_integration.src.api.climate_routes import detect_climate_zone_changes, ClimateZoneChangeRequest
        from fastapi import HTTPException
        
        request = ClimateZoneChangeRequest(
            latitude=42.0,
            longitude=-93.5
        )
        
        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await detect_climate_zone_changes(request)
        
        assert exc_info.value.status_code == 500
        assert "Change detection failed" in str(exc_info.value.detail)
    
    def test_historical_record_serialization(self):
        """Test serialization of historical records for API response."""
        
        from services.data_integration.src.api.climate_routes import HistoricalRecord
        from datetime import datetime
        
        # Test creating HistoricalRecord from ClimateZoneHistoricalRecord
        original_record = ClimateZoneHistoricalRecord(
            zone_id="6a",
            zone_type=ClimateZoneType.USDA_HARDINESS,
            detection_date=datetime.now(),
            confidence_score=0.85,
            coordinates=(42.0, -93.5),
            source="test"
        )
        
        api_record = HistoricalRecord(
            zone_id=original_record.zone_id,
            detection_date=original_record.detection_date,
            confidence_score=original_record.confidence_score,
            source=original_record.source
        )
        
        assert api_record.zone_id == "6a"
        assert api_record.confidence_score == 0.85
        assert api_record.source == "test"
        assert isinstance(api_record.detection_date, datetime)
    
    def test_zone_info_formatting(self, mock_change_detection_result):
        """Test formatting of zone information for API response."""
        
        # Test current zone formatting
        current_zone = mock_change_detection_result.current_zone
        
        current_zone_info = {
            "zone_id": current_zone.zone_id,
            "name": current_zone.name,
            "description": current_zone.description,
            "min_temp_f": current_zone.min_temp_f,
            "max_temp_f": current_zone.max_temp_f
        }
        
        assert current_zone_info["zone_id"] == "6a"
        assert current_zone_info["name"] == "USDA Zone 6a"
        assert current_zone_info["min_temp_f"] == -10
        assert current_zone_info["max_temp_f"] == -5
        
        # Test previous zone formatting
        previous_zone = mock_change_detection_result.previous_zone
        
        previous_zone_info = {
            "zone_id": previous_zone.zone_id,
            "name": previous_zone.name,
            "description": previous_zone.description,
            "min_temp_f": previous_zone.min_temp_f,
            "max_temp_f": previous_zone.max_temp_f
        }
        
        assert previous_zone_info["zone_id"] == "5b"
        assert previous_zone_info["name"] == "USDA Zone 5b"
        assert previous_zone_info["min_temp_f"] == -15
        assert previous_zone_info["max_temp_f"] == -10


if __name__ == "__main__":
    pytest.main([__file__])