#!/usr/bin/env python3
"""
Climate Zone Integration Demonstration

This script demonstrates the climate zone integration in the crop recommendation system,
showing how climate zone data affects crop suitability scoring and filtering.
"""

import asyncio
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.crop_recommendation_service import CropRecommendationService
from models.agricultural_models import (
    RecommendationRequest,
    LocationData,
    SoilTestData,
    FarmProfile
)
from datetime import date


async def demonstrate_climate_zone_integration():
    """Demonstrate climate zone integration with different scenarios."""
    
    print("🌱 Climate Zone Integration Demonstration for Crop Recommendations")
    print("=" * 70)
    
    service = CropRecommendationService()
    
    # Standard soil data for consistent comparisons
    soil_data = SoilTestData(
        ph=6.5,
        organic_matter_percent=3.5,
        phosphorus_ppm=25,
        potassium_ppm=200,
        test_date=date.today()
    )
    
    farm_profile = FarmProfile(
        farm_id="demo_farm",
        farm_size_acres=100,
        primary_crops=["corn", "soybean"]
    )
    
    # Test scenarios with different climate zones
    scenarios = [
        {
            "name": "Midwest - Zone 6a (Ideal for major crops)",
            "location": LocationData(
                latitude=41.8781,
                longitude=-87.6298,
                climate_zone="6a",
                climate_zone_name="USDA Hardiness Zone 6a",
                address="Chicago, IL area"
            )
        },
        {
            "name": "Northern Plains - Zone 3a (Cold climate)",
            "location": LocationData(
                latitude=46.7296,
                longitude=-94.6859,
                climate_zone="3a",
                climate_zone_name="USDA Hardiness Zone 3a",
                address="Brainerd, MN area"
            )
        },
        {
            "name": "Southeast - Zone 9a (Warm climate)",
            "location": LocationData(
                latitude=28.5383,
                longitude=-81.3792,
                climate_zone="9a",
                climate_zone_name="USDA Hardiness Zone 9a",
                address="Orlando, FL area"
            )
        },
        {
            "name": "No Climate Zone (Default scoring)",
            "location": LocationData(
                latitude=41.8781,
                longitude=-87.6298,
                address="Unknown climate zone location"
            )
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print("-" * 50)
        
        # Create recommendation request
        request = RecommendationRequest(
            request_id=f"demo_climate_{i}",
            question_type="crop_selection",
            location=scenario['location'],
            soil_data=soil_data,
            farm_profile=farm_profile
        )
        
        # Show climate zone filtering results
        filtered_crops = service._filter_crops_by_climate_zone(scenario['location'])
        excluded_crops = service._get_excluded_crops_by_climate(scenario['location'])
        
        print(f"📍 Location: {scenario['location'].address}")
        climate_zone = getattr(scenario['location'], 'climate_zone', 'Not specified')
        print(f"🌡️  Climate Zone: {climate_zone}")
        print(f"✅ Compatible crops: {list(filtered_crops.keys())}")
        if excluded_crops:
            print(f"❌ Excluded crops: {excluded_crops}")
        
        # Get detailed suitability scores for each crop
        print(f"\n🎯 Climate Suitability Scores:")
        for crop_name, crop_data in service.crop_database.items():
            score = service._calculate_climate_zone_suitability(scenario['location'], crop_data)
            score_desc = "Optimal" if score == 1.0 else "Good" if score >= 0.8 else "Marginal" if score >= 0.5 else "Poor"
            print(f"   {crop_name.capitalize()}: {score:.2f} ({score_desc})")
        
        # Get full recommendations
        try:
            recommendations = await service.get_crop_recommendations(request)
            print(f"\n📋 Top Recommendations ({len(recommendations)} total):")
            
            for j, rec in enumerate(recommendations[:2], 1):  # Show top 2
                print(f"   {j}. {rec.title} (Confidence: {rec.confidence_score:.2f})")
                # Show first sentence of description
                description = rec.description.split('.')[0] + '.'
                print(f"      {description}")
        except Exception as e:
            print(f"   Error generating recommendations: {str(e)}")
    
    # Demonstrate climate compatibility descriptions
    print(f"\n🗣️  Climate Compatibility Descriptions")
    print("-" * 50)
    
    # Test different compatibility scenarios
    test_cases = [
        ("Zone 6a with Corn", scenarios[0]['location'], service.crop_database['corn'], "corn"),
        ("Zone 3a with Wheat", scenarios[1]['location'], service.crop_database['wheat'], "wheat"),
        ("Zone 9a with Corn", scenarios[2]['location'], service.crop_database['corn'], "corn")
    ]
    
    for case_name, location, crop_data, crop_name in test_cases:
        description = service._get_climate_compatibility_description(location, crop_data, crop_name)
        print(f"• {case_name}: {description}")
    
    # Demonstrate adjacent zone compatibility
    print(f"\n🔄 Adjacent Zone Compatibility Examples")
    print("-" * 50)
    
    # Create test scenarios for adjacent zones
    adjacent_tests = [
        ("Zone 5a crop tested in Zone 6a", "6a", ["5a", "5b"], "Expected: 0.8 (adjacent)"),
        ("Zone 6a crop tested in Zone 6b", "6b", ["6a"], "Expected: 0.9 (same zone, different subzone)"),
        ("Zone 4a crop tested in Zone 7a", "7a", ["4a", "4b"], "Expected: 0.3 (too far apart)")
    ]
    
    for test_name, farm_zone, crop_zones, expected in adjacent_tests:
        score = service._calculate_adjacent_zone_compatibility(farm_zone, crop_zones)
        print(f"• {test_name}")
        print(f"  Farm: {farm_zone}, Crop zones: {crop_zones}")
        print(f"  Result: {score:.1f} - {expected}")


if __name__ == "__main__":
    print("Starting Climate Zone Integration Demonstration...")
    asyncio.run(demonstrate_climate_zone_integration())
    print(f"\n✅ Demonstration complete!")
    print(f"\nKey Features Demonstrated:")
    print(f"• Climate zone suitability scoring (perfect match, adjacent, incompatible)")
    print(f"• Crop filtering based on climate compatibility")
    print(f"• Climate-aware recommendation descriptions")
    print(f"• Graceful handling of missing climate data")
    print(f"• Integration with existing soil and farm data scoring")