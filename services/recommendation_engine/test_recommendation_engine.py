#!/usr/bin/env python3
"""
Test script for the Recommendation Engine

Tests the core recommendation engine functionality and all service integrations.
"""

import asyncio
import sys
import os
from datetime import date, datetime
from uuid import uuid4

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.agricultural_models import (
    RecommendationRequest,
    LocationData,
    SoilTestData,
    CropData,
    FarmProfile
)
from services.recommendation_engine import RecommendationEngine


async def test_crop_selection():
    """Test crop selection recommendations."""
    print("\n=== Testing Crop Selection Recommendations ===")
    
    # Create test request
    request = RecommendationRequest(
        request_id=str(uuid4()),
        question_type="crop_selection",
        location=LocationData(
            latitude=42.0308,
            longitude=-93.6319,
            address="Ames, Iowa, USA",
            state="Iowa"
        ),
        soil_data=SoilTestData(
            ph=6.2,
            organic_matter_percent=3.8,
            phosphorus_ppm=25,
            potassium_ppm=180,
            test_date=date(2024, 3, 15)
        ),
        farm_profile=FarmProfile(
            farm_id="test_farm_001",
            farm_size_acres=320,
            primary_crops=["corn", "soybean"],
            equipment_available=["planter", "combine", "sprayer"],
            irrigation_available=False
        )
    )
    
    engine = RecommendationEngine()
    response = await engine.generate_recommendations(request)
    
    print(f"Request ID: {response.request_id}")
    print(f"Overall Confidence: {response.overall_confidence:.2f}")
    print(f"Number of Recommendations: {len(response.recommendations)}")
    
    for i, rec in enumerate(response.recommendations, 1):
        print(f"\n{i}. {rec.title}")
        print(f"   Priority: {rec.priority}, Confidence: {rec.confidence_score:.2f}")
        print(f"   Description: {rec.description}")
        print(f"   Cost Estimate: ${rec.cost_estimate:.2f}/acre" if rec.cost_estimate else "   Cost: Not specified")
    
    print(f"\nWarnings: {len(response.warnings)}")
    for warning in response.warnings:
        print(f"  - {warning}")
    
    return response


async def test_fertilizer_strategy():
    """Test fertilizer strategy recommendations."""
    print("\n=== Testing Fertilizer Strategy Recommendations ===")
    
    request = RecommendationRequest(
        request_id=str(uuid4()),
        question_type="fertilizer_strategy",
        location=LocationData(
            latitude=42.0308,
            longitude=-93.6319
        ),
        soil_data=SoilTestData(
            ph=6.0,
            organic_matter_percent=3.2,
            phosphorus_ppm=18,
            potassium_ppm=140,
            nitrogen_ppm=8,
            test_date=date(2024, 3, 1)
        ),
        crop_data=CropData(
            crop_name="corn",
            yield_goal=180,
            previous_crop="soybean",
            planting_date=date(2024, 5, 1)
        ),
        farm_profile=FarmProfile(
            farm_id="test_farm_002",
            farm_size_acres=250,
            primary_crops=["corn", "soybean"]
        )
    )
    
    engine = RecommendationEngine()
    response = await engine.generate_recommendations(request)
    
    print(f"Request ID: {response.request_id}")
    print(f"Overall Confidence: {response.overall_confidence:.2f}")
    print(f"Number of Recommendations: {len(response.recommendations)}")
    
    for i, rec in enumerate(response.recommendations, 1):
        print(f"\n{i}. {rec.title}")
        print(f"   Priority: {rec.priority}, Confidence: {rec.confidence_score:.2f}")
        print(f"   Description: {rec.description}")
        if rec.cost_estimate:
            print(f"   Cost: ${rec.cost_estimate:.2f}/acre")
        if rec.roi_estimate:
            print(f"   ROI: {rec.roi_estimate:.0f}%")
    
    return response


async def test_soil_fertility():
    """Test soil fertility improvement recommendations."""
    print("\n=== Testing Soil Fertility Recommendations ===")
    
    request = RecommendationRequest(
        request_id=str(uuid4()),
        question_type="soil_fertility",
        location=LocationData(
            latitude=40.5,
            longitude=-89.4
        ),
        soil_data=SoilTestData(
            ph=5.8,  # Acidic soil
            organic_matter_percent=2.1,  # Low organic matter
            phosphorus_ppm=12,  # Low phosphorus
            potassium_ppm=95,   # Low potassium
            test_date=date(2024, 2, 15)
        ),
        farm_profile=FarmProfile(
            farm_id="test_farm_003",
            farm_size_acres=160,
            primary_crops=["corn", "soybean"]
        )
    )
    
    engine = RecommendationEngine()
    response = await engine.generate_recommendations(request)
    
    print(f"Request ID: {response.request_id}")
    print(f"Overall Confidence: {response.overall_confidence:.2f}")
    print(f"Number of Recommendations: {len(response.recommendations)}")
    
    for i, rec in enumerate(response.recommendations, 1):
        print(f"\n{i}. {rec.title}")
        print(f"   Priority: {rec.priority}, Confidence: {rec.confidence_score:.2f}")
        print(f"   Description: {rec.description}")
        print(f"   Expected Outcomes:")
        for outcome in rec.expected_outcomes[:3]:  # Show first 3 outcomes
            print(f"     - {outcome}")
    
    return response


async def test_crop_rotation():
    """Test crop rotation recommendations."""
    print("\n=== Testing Crop Rotation Recommendations ===")
    
    request = RecommendationRequest(
        request_id=str(uuid4()),
        question_type="crop_rotation",
        location=LocationData(
            latitude=41.5,
            longitude=-90.5
        ),
        crop_data=CropData(
            crop_name="corn",
            rotation_history=["corn", "corn", "corn"]  # Continuous corn
        ),
        farm_profile=FarmProfile(
            farm_id="test_farm_004",
            farm_size_acres=400,
            primary_crops=["corn"],
            equipment_available=["planter", "combine", "sprayer", "tillage"]
        )
    )
    
    engine = RecommendationEngine()
    response = await engine.generate_recommendations(request)
    
    print(f"Request ID: {response.request_id}")
    print(f"Overall Confidence: {response.overall_confidence:.2f}")
    print(f"Number of Recommendations: {len(response.recommendations)}")
    
    for i, rec in enumerate(response.recommendations, 1):
        print(f"\n{i}. {rec.title}")
        print(f"   Priority: {rec.priority}, Confidence: {rec.confidence_score:.2f}")
        print(f"   Description: {rec.description}")
        if rec.roi_estimate:
            print(f"   ROI: {rec.roi_estimate:.0f}%")
    
    return response


async def test_nutrient_deficiency():
    """Test nutrient deficiency detection recommendations."""
    print("\n=== Testing Nutrient Deficiency Recommendations ===")
    
    request = RecommendationRequest(
        request_id=str(uuid4()),
        question_type="nutrient_deficiency",
        location=LocationData(
            latitude=43.0,
            longitude=-91.0
        ),
        soil_data=SoilTestData(
            ph=7.8,  # High pH - may cause micronutrient deficiencies
            organic_matter_percent=3.5,
            phosphorus_ppm=8,   # Very low phosphorus
            potassium_ppm=85,   # Low potassium
            nitrogen_ppm=5,     # Low nitrogen
            test_date=date(2024, 3, 10)
        ),
        crop_data=CropData(
            crop_name="corn",
            yield_goal=170
        )
    )
    
    engine = RecommendationEngine()
    response = await engine.generate_recommendations(request)
    
    print(f"Request ID: {response.request_id}")
    print(f"Overall Confidence: {response.overall_confidence:.2f}")
    print(f"Number of Recommendations: {len(response.recommendations)}")
    
    for i, rec in enumerate(response.recommendations, 1):
        print(f"\n{i}. {rec.title}")
        print(f"   Priority: {rec.priority}, Confidence: {rec.confidence_score:.2f}")
        print(f"   Type: {rec.recommendation_type}")
        print(f"   Description: {rec.description}")
    
    return response


async def test_fertilizer_selection():
    """Test fertilizer type selection recommendations."""
    print("\n=== Testing Fertilizer Selection Recommendations ===")
    
    request = RecommendationRequest(
        request_id=str(uuid4()),
        question_type="fertilizer_selection",
        location=LocationData(
            latitude=44.0,
            longitude=-92.0
        ),
        soil_data=SoilTestData(
            ph=6.5,
            organic_matter_percent=2.8,
            phosphorus_ppm=22,
            potassium_ppm=165,
            soil_texture="sandy_loam",
            test_date=date(2024, 2, 20)
        ),
        farm_profile=FarmProfile(
            farm_id="test_farm_005",
            farm_size_acres=80,
            primary_crops=["corn", "soybean"],
            organic_certified=False
        )
    )
    
    engine = RecommendationEngine()
    response = await engine.generate_recommendations(request)
    
    print(f"Request ID: {response.request_id}")
    print(f"Overall Confidence: {response.overall_confidence:.2f}")
    print(f"Number of Recommendations: {len(response.recommendations)}")
    
    for i, rec in enumerate(response.recommendations, 1):
        print(f"\n{i}. {rec.title}")
        print(f"   Priority: {rec.priority}, Confidence: {rec.confidence_score:.2f}")
        print(f"   Description: {rec.description}")
        if rec.cost_estimate:
            print(f"   Cost: ${rec.cost_estimate:.2f}/acre")
    
    return response


async def test_climate_zone_integration():
    """Test climate zone integration functionality."""
    print("\n=== Testing Climate Zone Integration ===")
    
    # Test with coordinates that should trigger climate zone detection
    request = RecommendationRequest(
        request_id=str(uuid4()),
        question_type="crop_selection",
        location=LocationData(
            latitude=42.0308,  # Ames, Iowa coordinates
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
    
    engine = RecommendationEngine()
    response = await engine.generate_recommendations(request)
    
    print(f"Request ID: {response.request_id}")
    print(f"Overall Confidence: {response.overall_confidence:.2f}")
    
    # Check if climate zone data was populated
    location = request.location
    print(f"\nClimate Zone Detection Results:")
    print(f"  Climate Zone: {location.climate_zone or 'Not detected'}")
    print(f"  Climate Zone Name: {location.climate_zone_name or 'Not available'}")
    print(f"  Climate Confidence: {location.climate_confidence or 'Not available'}")
    print(f"  Köppen Zone: {location.koppen_zone or 'Not available'}")
    print(f"  Growing Season: {location.growing_season_months or 'Not available'} months")
    
    # Check if climate considerations are in recommendations
    print(f"\nRecommendations with Climate Integration:")
    climate_enhanced_count = 0
    for i, rec in enumerate(response.recommendations, 1):
        has_climate_info = (
            "climate" in rec.description.lower() or 
            "zone" in rec.description.lower() or
            "usda" in rec.description.lower() or
            any("Climate" in source or "Zone" in source for source in rec.agricultural_sources)
        )
        if has_climate_info:
            climate_enhanced_count += 1
            print(f"\n{i}. {rec.title} (Climate Enhanced)")
            print(f"   Description: {rec.description[:200]}...")
            print(f"   Climate Sources: {[s for s in rec.agricultural_sources if 'Climate' in s or 'Zone' in s]}")
    
    print(f"\nClimate-enhanced recommendations: {climate_enhanced_count}/{len(response.recommendations)}")
    
    # Check for climate-related warnings
    climate_warnings = [w for w in response.warnings if "zone" in w.lower() or "climate" in w.lower()]
    if climate_warnings:
        print(f"\nClimate-related warnings:")
        for warning in climate_warnings:
            print(f"  - {warning}")
    
    return response


async def test_extreme_climate_zones():
    """Test recommendations for extreme climate zones."""
    print("\n=== Testing Extreme Climate Zone Recommendations ===")
    
    # Test northern location (should trigger cold climate warnings)
    northern_request = RecommendationRequest(
        request_id=str(uuid4()),
        question_type="crop_selection",
        location=LocationData(
            latitude=64.0685,  # Fairbanks, Alaska
            longitude=-147.7208,
            address="Fairbanks, Alaska, USA"
        ),
        soil_data=SoilTestData(
            ph=6.0,
            organic_matter_percent=4.0,
            phosphorus_ppm=20,
            potassium_ppm=150,
            test_date=date(2024, 3, 1)
        ),
        crop_data=CropData(crop_name="potato")
    )
    
    # Test southern location (should trigger heat warnings)  
    southern_request = RecommendationRequest(
        request_id=str(uuid4()),
        question_type="fertilizer_strategy", 
        location=LocationData(
            latitude=25.7617,  # Miami, Florida
            longitude=-80.1918,
            address="Miami, Florida, USA"
        ),
        soil_data=SoilTestData(
            ph=7.0,
            organic_matter_percent=2.5,
            phosphorus_ppm=15,
            potassium_ppm=120,
            test_date=date(2024, 2, 15)
        )
    )
    
    engine = RecommendationEngine()
    
    print("Northern Location (Alaska) Test:")
    northern_response = await engine.generate_recommendations(northern_request)
    print(f"  Climate Zone: {northern_request.location.climate_zone or 'Not detected'}")
    print(f"  Warnings: {len(northern_response.warnings)}")
    cold_warnings = [w for w in northern_response.warnings if "cold" in w.lower() or "short" in w.lower() or "northern" in w.lower()]
    for warning in cold_warnings:
        print(f"    - {warning}")
    
    print("\nSouthern Location (Florida) Test:")
    southern_response = await engine.generate_recommendations(southern_request)
    print(f"  Climate Zone: {southern_request.location.climate_zone or 'Not detected'}")
    print(f"  Warnings: {len(southern_response.warnings)}")
    heat_warnings = [w for w in southern_response.warnings if "heat" in w.lower() or "warm" in w.lower() or "drought" in w.lower()]
    for warning in heat_warnings:
        print(f"    - {warning}")
    
    return northern_response, southern_response


async def test_confidence_factors():
    """Test confidence factor calculations."""
    print("\n=== Testing Confidence Factor Calculations ===")
    
    # Test with complete data
    complete_request = RecommendationRequest(
        request_id=str(uuid4()),
        question_type="crop_selection",
        location=LocationData(latitude=42.0, longitude=-93.6),
        soil_data=SoilTestData(
            ph=6.5,
            organic_matter_percent=3.5,
            phosphorus_ppm=30,
            potassium_ppm=200,
            test_date=date(2024, 3, 1)  # Recent test
        ),
        farm_profile=FarmProfile(
            farm_id="complete_farm",
            farm_size_acres=200,
            primary_crops=["corn", "soybean"]
        )
    )
    
    # Test with minimal data
    minimal_request = RecommendationRequest(
        request_id=str(uuid4()),
        question_type="crop_selection",
        location=LocationData(latitude=42.0, longitude=-93.6)
    )
    
    engine = RecommendationEngine()
    
    complete_response = await engine.generate_recommendations(complete_request)
    minimal_response = await engine.generate_recommendations(minimal_request)
    
    print("Complete Data Confidence Factors:")
    cf = complete_response.confidence_factors
    print(f"  Soil Data Quality: {cf.soil_data_quality:.2f}")
    print(f"  Regional Data Availability: {cf.regional_data_availability:.2f}")
    print(f"  Seasonal Appropriateness: {cf.seasonal_appropriateness:.2f}")
    print(f"  Expert Validation: {cf.expert_validation:.2f}")
    print(f"  Overall Confidence: {complete_response.overall_confidence:.2f}")
    
    print("\nMinimal Data Confidence Factors:")
    cf = minimal_response.confidence_factors
    print(f"  Soil Data Quality: {cf.soil_data_quality:.2f}")
    print(f"  Regional Data Availability: {cf.regional_data_availability:.2f}")
    print(f"  Seasonal Appropriateness: {cf.seasonal_appropriateness:.2f}")
    print(f"  Expert Validation: {cf.expert_validation:.2f}")
    print(f"  Overall Confidence: {minimal_response.overall_confidence:.2f}")


async def main():
    """Run all tests."""
    print("Starting Recommendation Engine Tests")
    print("=" * 50)
    
    try:
        # Test all question types
        await test_crop_selection()
        await test_fertilizer_strategy()
        await test_soil_fertility()
        await test_crop_rotation()
        await test_nutrient_deficiency()
        await test_fertilizer_selection()
        await test_confidence_factors()
        
        # Test climate zone integration
        await test_climate_zone_integration()
        await test_extreme_climate_zones()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)