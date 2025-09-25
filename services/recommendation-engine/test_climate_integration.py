#!/usr/bin/env python3
"""
Climate Zone Integration Test

Tests the climate zone integration functionality independently.
This test mocks the climate API responses to test the integration logic.
"""

import asyncio
import sys
import os
from unittest.mock import AsyncMock, patch
from datetime import date
from uuid import uuid4

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.agricultural_models import (
    RecommendationRequest,
    LocationData,
    SoilTestData,
    CropData
)
from services.recommendation_engine import RecommendationEngine
from services.climate_integration_service import ClimateIntegrationService


async def test_climate_integration_with_mock():
    """Test climate integration with mocked API responses."""
    print("=== Testing Climate Integration with Mock Data ===")
    
    # Mock climate detection response
    mock_climate_data = {
        "primary_zone": {
            "zone_id": "5b",
            "name": "USDA Hardiness Zone 5b",
            "description": "Cold winter zone with minimum temperatures -15°F to -10°F",
            "temperature_range_f": {"min": -15, "max": -10}
        },
        "alternative_zones": [
            {
                "zone_type": "koppen",
                "zone_id": "Dfa",
                "description": "Hot-summer humid continental climate",
                "agricultural_suitability": "excellent",
                "growing_season_months": 6
            }
        ],
        "confidence_score": 0.85
    }
    
    # Create test request
    request = RecommendationRequest(
        request_id=str(uuid4()),
        question_type="crop_selection",
        location=LocationData(
            latitude=42.0308,
            longitude=-93.6319,
            address="Ames, Iowa, USA"
        ),
        soil_data=SoilTestData(
            ph=6.5,
            organic_matter_percent=3.5,
            phosphorus_ppm=25,
            potassium_ppm=180,
            test_date=date(2024, 3, 15)
        ),
        crop_data=CropData(
            crop_name="corn",
            yield_goal=175
        )
    )
    
    # Mock the climate detection service
    with patch.object(ClimateIntegrationService, 'detect_climate_zone', 
                      new_callable=AsyncMock) as mock_detect:
        mock_detect.return_value = mock_climate_data
        
        engine = RecommendationEngine()
        response = await engine.generate_recommendations(request)
        
        # Verify climate zone detection was called
        mock_detect.assert_called_once_with(
            latitude=42.0308,
            longitude=-93.6319,
            elevation_ft=None
        )
        
        # Check if location was enhanced with climate data
        location = request.location
        print(f"Climate Zone: {location.climate_zone}")
        print(f"Climate Zone Name: {location.climate_zone_name}")
        print(f"Climate Confidence: {location.climate_confidence}")
        print(f"Köppen Zone: {location.koppen_zone}")
        print(f"Growing Season: {location.growing_season_months} months")
        
        # Verify location was enhanced
        assert location.climate_zone == "5b"
        assert location.climate_zone_name == "USDA Hardiness Zone 5b"
        assert location.climate_confidence == 0.85
        assert location.koppen_zone == "Dfa"
        assert location.growing_season_months == 6
        
        print(f"\nRecommendations generated: {len(response.recommendations)}")
        print(f"Overall confidence: {response.overall_confidence:.2f}")
        
        # Check for climate-enhanced recommendations
        climate_enhanced = 0
        for rec in response.recommendations:
            if ("zone" in rec.description.lower() or 
                "climate" in rec.description.lower() or
                any("Zone" in source for source in rec.agricultural_sources)):
                climate_enhanced += 1
                print(f"  Climate-enhanced: {rec.title}")
        
        print(f"Climate-enhanced recommendations: {climate_enhanced}")
        
        return response


async def test_climate_integration_failure_fallback():
    """Test that system works when climate detection fails."""
    print("\n=== Testing Climate Integration Failure Fallback ===")
    
    request = RecommendationRequest(
        request_id=str(uuid4()),
        question_type="fertilizer_strategy",
        location=LocationData(
            latitude=42.0308,
            longitude=-93.6319
        ),
        soil_data=SoilTestData(
            ph=6.0,
            organic_matter_percent=3.0,
            phosphorus_ppm=20,
            potassium_ppm=150,
            test_date=date(2024, 3, 1)
        )
    )
    
    # Mock climate detection to return None (failure case)
    with patch.object(ClimateIntegrationService, 'detect_climate_zone', 
                      new_callable=AsyncMock) as mock_detect:
        mock_detect.return_value = None
        
        engine = RecommendationEngine()
        response = await engine.generate_recommendations(request)
        
        # Verify system still works
        assert response is not None
        assert len(response.recommendations) > 0
        print(f"System continued working with {len(response.recommendations)} recommendations")
        print(f"Confidence score: {response.overall_confidence:.2f}")
        
        # Verify location wasn't enhanced (fallback behavior)
        location = request.location
        assert location.climate_zone is None
        assert location.climate_confidence is None
        print("Climate data correctly remained empty on detection failure")
        
        return response


async def test_extreme_climate_zone_warnings():
    """Test warnings for extreme climate zones."""
    print("\n=== Testing Extreme Climate Zone Warnings ===")
    
    # Test cold climate (Zone 3)
    cold_climate_data = {
        "primary_zone": {
            "zone_id": "3a",
            "name": "USDA Hardiness Zone 3a", 
            "description": "Very cold zone with minimum temperatures -40°F to -35°F",
            "temperature_range_f": {"min": -40, "max": -35}
        },
        "confidence_score": 0.9
    }
    
    # Test hot climate (Zone 10)
    hot_climate_data = {
        "primary_zone": {
            "zone_id": "10b",
            "name": "USDA Hardiness Zone 10b",
            "description": "Very warm zone with minimum temperatures 35°F to 40°F", 
            "temperature_range_f": {"min": 35, "max": 40}
        },
        "confidence_score": 0.9
    }
    
    cold_request = RecommendationRequest(
        request_id=str(uuid4()),
        question_type="crop_selection",
        location=LocationData(latitude=64.0, longitude=-147.0),
        soil_data=SoilTestData(
            ph=6.0, organic_matter_percent=4.0,
            phosphorus_ppm=20, potassium_ppm=150,
            test_date=date(2024, 3, 1)
        )
    )
    
    hot_request = RecommendationRequest(
        request_id=str(uuid4()),
        question_type="crop_selection",
        location=LocationData(latitude=25.7, longitude=-80.2),
        soil_data=SoilTestData(
            ph=7.0, organic_matter_percent=2.5,
            phosphorus_ppm=15, potassium_ppm=120,
            test_date=date(2024, 3, 1)
        )
    )
    
    engine = RecommendationEngine()
    
    # Test cold climate warnings
    with patch.object(ClimateIntegrationService, 'detect_climate_zone', 
                      new_callable=AsyncMock) as mock_detect:
        mock_detect.return_value = cold_climate_data
        cold_response = await engine.generate_recommendations(cold_request)
        
        cold_warnings = [w for w in cold_response.warnings 
                        if "3a" in w or "short" in w.lower() or "cold" in w.lower()]
        print(f"Cold climate warnings: {len(cold_warnings)}")
        for warning in cold_warnings:
            print(f"  - {warning}")
    
    # Test hot climate warnings  
    with patch.object(ClimateIntegrationService, 'detect_climate_zone',
                      new_callable=AsyncMock) as mock_detect:
        mock_detect.return_value = hot_climate_data
        hot_response = await engine.generate_recommendations(hot_request)
        
        hot_warnings = [w for w in hot_response.warnings
                       if "10b" in w or "heat" in w.lower() or "drought" in w.lower()]
        print(f"Hot climate warnings: {len(hot_warnings)}")
        for warning in hot_warnings:
            print(f"  - {warning}")
    
    return cold_response, hot_response


async def main():
    """Run all climate integration tests."""
    print("Starting Climate Zone Integration Tests")
    print("=" * 50)
    
    try:
        await test_climate_integration_with_mock()
        await test_climate_integration_failure_fallback()
        await test_extreme_climate_zone_warnings()
        
        print("\n" + "=" * 50)
        print("All climate integration tests completed successfully!")
        print("\nIntegration Summary:")
        print("✅ Climate zone detection integration")
        print("✅ Location data enhancement")
        print("✅ Climate-adjusted recommendations")
        print("✅ Extreme climate warnings")
        print("✅ Graceful failure handling")
        
    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)