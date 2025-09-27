#!/usr/bin/env python3
"""
TICKET-005_crop-type-filtering-3.3: Demo for Preference Recommendation Engine

This demo showcases the capabilities of the preference-based recommendation enhancement engine.
"""

import sys
import os
from pathlib import Path
import json

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from services.preference_recommendation_engine import (
    PreferenceRecommendationEngine,
    FarmCharacteristics,
    FarmerProfile,
    RecommendationType
)


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_result(result):
    """Print a recommendation result in a formatted way"""
    print(f"\nRecommendation Type: {result.recommendation_type.value}")
    print(f"Confidence Score: {result.confidence_score:.2f}")
    print(f"Reasoning: {result.reasoning}")
    
    if result.conflicts_detected:
        print(f"\nConflicts Detected:")
        for conflict in result.conflicts_detected:
            print(f"  ⚠️  {conflict}")
    
    print(f"\nSuggestions ({len(result.suggestions)}):")
    for i, suggestion in enumerate(result.suggestions, 1):
        print(f"  {i}. {json.dumps(suggestion, indent=6)}")


def demo_crop_suggestions():
    """Demo crop type suggestions"""
    print_section("CROP TYPE SUGGESTIONS DEMO")
    
    engine = PreferenceRecommendationEngine()
    
    # Test different farm scenarios
    scenarios = [
        {
            "name": "Midwest Corn Belt Farm",
            "farm": FarmCharacteristics(
                location="Iowa, USA",
                climate_zone="zone_5",
                soil_type="loam",
                farm_size_acres=250.0,
                precipitation_annual=32.0,
                temperature_range=(25.0, 85.0),
                irrigation_available=False,
                organic_certification=False,
                equipment_capabilities=["tractor", "combine", "planter"]
            )
        },
        {
            "name": "Small Organic Vegetable Farm",
            "farm": FarmCharacteristics(
                location="Vermont, USA",
                climate_zone="zone_4",
                soil_type="loam",
                farm_size_acres=15.0,
                precipitation_annual=40.0,
                temperature_range=(20.0, 80.0),
                irrigation_available=True,
                organic_certification=True,
                equipment_capabilities=["tractor", "cultivator"]
            )
        },
        {
            "name": "Large Southern Cotton Farm",
            "farm": FarmCharacteristics(
                location="Georgia, USA",
                climate_zone="zone_8",
                soil_type="sandy",
                farm_size_acres=800.0,
                precipitation_annual=45.0,
                temperature_range=(35.0, 95.0),
                irrigation_available=True,
                organic_certification=False,
                equipment_capabilities=["tractor", "combine", "cotton_picker"]
            )
        }
    ]
    
    for scenario in scenarios:
        print(f"\n--- {scenario['name']} ---")
        result = engine.suggest_crop_types(scenario['farm'], max_suggestions=3)
        print_result(result)


def demo_filter_recommendations():
    """Demo filter recommendations based on similar farmers"""
    print_section("FILTER RECOMMENDATIONS DEMO")
    
    engine = PreferenceRecommendationEngine()
    
    # Create a base farm
    target_farm = FarmCharacteristics(
        location="Minnesota, USA",
        climate_zone="zone_4",
        soil_type="loam",
        farm_size_acres=180.0,
        precipitation_annual=28.0,
        temperature_range=(22.0, 82.0),
        irrigation_available=False,
        organic_certification=False
    )
    
    # Register similar farmers
    similar_farmers = [
        {
            "id": "farmer_001",
            "farm": FarmCharacteristics(
                location="Minnesota, USA",
                climate_zone="zone_4",
                soil_type="loam",
                farm_size_acres=160.0,
                precipitation_annual=30.0,
                temperature_range=(20.0, 80.0),
                irrigation_available=False,
                organic_certification=False
            ),
            "preferences": {"corn": 0.9, "soybeans": 0.8, "wheat": 0.6},
            "filters": {"climate_zone": 12, "soil_type": 8, "farm_size": 6}
        },
        {
            "id": "farmer_002", 
            "farm": FarmCharacteristics(
                location="Wisconsin, USA",
                climate_zone="zone_4",
                soil_type="clay",  # Different soil but similar climate
                farm_size_acres=200.0,
                precipitation_annual=32.0,
                temperature_range=(18.0, 78.0),
                irrigation_available=False,
                organic_certification=False
            ),
            "preferences": {"corn": 0.8, "soybeans": 0.9, "alfalfa": 0.7},
            "filters": {"climate_zone": 15, "soil_type": 10, "precipitation": 8}
        },
        {
            "id": "farmer_003",
            "farm": FarmCharacteristics(
                location="North Dakota, USA",
                climate_zone="zone_3",  # Colder but similar farming
                soil_type="loam",
                farm_size_acres=220.0,
                precipitation_annual=18.0,
                temperature_range=(15.0, 75.0),
                irrigation_available=False,
                organic_certification=False
            ),
            "preferences": {"wheat": 0.9, "barley": 0.7, "canola": 0.6},
            "filters": {"climate_zone": 20, "soil_type": 5, "precipitation": 12}
        }
    ]
    
    # Register farmers
    for farmer_data in similar_farmers:
        profile = FarmerProfile(
            farmer_id=farmer_data["id"],
            experience_years=12,
            farm_characteristics=farmer_data["farm"],
            crop_preferences=farmer_data["preferences"],
            filter_usage_patterns=farmer_data["filters"],
            success_metrics={"yield_efficiency": 0.82, "profit_margin": 0.15}
        )
        engine.register_farmer_profile(profile)
    
    print(f"Registered {len(similar_farmers)} similar farmers")
    
    # Get filter recommendations
    result = engine.recommend_filters_by_similarity(target_farm, max_recommendations=3)
    print_result(result)


def demo_preference_optimization():
    """Demo preference optimization"""
    print_section("PREFERENCE OPTIMIZATION DEMO")
    
    engine = PreferenceRecommendationEngine()
    
    farm = FarmCharacteristics(
        location="Kansas, USA",
        climate_zone="zone_6",
        soil_type="clay",
        farm_size_acres=320.0,
        precipitation_annual=25.0,
        temperature_range=(28.0, 92.0),
        irrigation_available=True,
        organic_certification=False
    )
    
    # Suboptimal preferences (high preference for unsuitable crops, low for suitable ones)
    current_preferences = {
        "tropical_fruits": 0.9,  # Not suitable for zone 6
        "rice": 0.3,  # Actually good for clay soil with irrigation
        "wheat": 0.4,  # Good for this climate
        "corn": 0.6,  # Should be higher for this region
        "soybeans": 0.5,  # Should be higher
        "cotton": 0.8,  # Good match for climate
        "citrus": 0.7   # Not suitable for zone 6
    }
    
    print("Current Preferences:")
    for crop, score in current_preferences.items():
        print(f"  {crop}: {score}")
    
    result = engine.optimize_preferences(current_preferences, farm)
    print_result(result)


def demo_conflict_resolution():
    """Demo preference conflict resolution"""
    print_section("PREFERENCE CONFLICT RESOLUTION DEMO")
    
    engine = PreferenceRecommendationEngine()
    
    # Small farm with conflicting high-input crop preferences
    small_farm = FarmCharacteristics(
        location="California, USA",
        climate_zone="zone_9",
        soil_type="sandy",
        farm_size_acres=45.0,
        precipitation_annual=15.0,
        temperature_range=(45.0, 95.0),
        irrigation_available=True,
        organic_certification=True
    )
    
    # Conflicting preferences
    conflicting_preferences = {
        "corn": 0.9,        # High-input crop
        "soybeans": 0.9,    # Potentially rotational conflict with corn
        "vegetables": 0.8,   # High-input crop
        "fruits": 0.9,      # High-input crop - too many for small farm
        "organic": 0.9,     # Management style
        "conventional": 0.7  # Conflicting management style
    }
    
    print("Potentially Conflicting Preferences:")
    for crop, score in conflicting_preferences.items():
        print(f"  {crop}: {score}")
    
    result = engine.resolve_preference_conflicts(conflicting_preferences, small_farm)
    print_result(result)


def demo_complete_workflow():
    """Demo a complete recommendation workflow"""
    print_section("COMPLETE WORKFLOW DEMO")
    
    engine = PreferenceRecommendationEngine()
    
    # Setup farm
    farm = FarmCharacteristics(
        location="Nebraska, USA",
        climate_zone="zone_5",
        soil_type="silt",
        farm_size_acres=280.0,
        precipitation_annual=26.0,
        temperature_range=(24.0, 88.0),
        irrigation_available=False,
        organic_certification=True,
        equipment_capabilities=["tractor", "combine", "planter", "cultivator"]
    )
    
    print("Farm Characteristics:")
    print(f"  Location: {farm.location}")
    print(f"  Climate Zone: {farm.climate_zone}")
    print(f"  Soil Type: {farm.soil_type}")
    print(f"  Size: {farm.farm_size_acres} acres")
    print(f"  Irrigation: {farm.irrigation_available}")
    print(f"  Organic: {farm.organic_certification}")
    
    # Step 1: Get initial crop suggestions
    print("\n--- Step 1: Initial Crop Suggestions ---")
    crop_suggestions = engine.suggest_crop_types(farm, max_suggestions=4)
    print_result(crop_suggestions)
    
    # Step 2: Simulate user setting preferences (some suboptimal)
    print("\n--- Step 2: User Sets Initial Preferences ---")
    user_preferences = {
        "corn": 0.8,           # Good choice
        "tropical_fruits": 0.7, # Poor choice for zone 5
        "soybeans": 0.5,       # Should be higher
        "wheat": 0.9,          # Good choice
        "vegetables": 0.8,     # Reasonable for organic
        "cotton": 0.6          # Not great for zone 5
    }
    
    for crop, score in user_preferences.items():
        print(f"  {crop}: {score}")
    
    # Step 3: Optimize preferences
    print("\n--- Step 3: Preference Optimization ---")
    optimization = engine.optimize_preferences(user_preferences, farm)
    print_result(optimization)
    
    # Step 4: Check for conflicts
    print("\n--- Step 4: Conflict Resolution ---")
    conflicts = engine.resolve_preference_conflicts(user_preferences, farm)
    print_result(conflicts)
    
    # Step 5: Register farmer and test similarity (would be useful for future users)
    print("\n--- Step 5: Register Farmer Profile ---")
    farmer_profile = FarmerProfile(
        farmer_id="demo_farmer_nebraska",
        experience_years=8,
        farm_characteristics=farm,
        crop_preferences=user_preferences,
        filter_usage_patterns={"climate_zone": 10, "soil_type": 8, "organic": 12, "farm_size": 6},
        success_metrics={"yield_efficiency": 0.75, "profit_margin": 0.18, "sustainability_score": 0.85}
    )
    
    engine.register_farmer_profile(farmer_profile)
    print(f"Registered farmer profile: {farmer_profile.farmer_id}")
    
    print("\n--- Workflow Complete ---")
    print("The preference recommendation engine has analyzed the farm,")
    print("provided optimized crop suggestions, identified conflicts,")
    print("and registered the farmer profile for future similarity matching.")


def main():
    """Run all demos"""
    print("🌾 PREFERENCE RECOMMENDATION ENGINE DEMO")
    print("TICKET-005_crop-type-filtering-3.3 Implementation")
    
    try:
        demo_crop_suggestions()
        demo_filter_recommendations()
        demo_preference_optimization()
        demo_conflict_resolution()
        demo_complete_workflow()
        
        print_section("DEMO COMPLETION")
        print("✅ All demos completed successfully!")
        print("🌾 The preference-based recommendation enhancement engine is ready for production use.")
        print("\nKey Features Demonstrated:")
        print("  • Intelligent crop type suggestions based on farm characteristics")
        print("  • Filter recommendations from similar farmer patterns")
        print("  • Preference optimization with conflict detection")
        print("  • Comprehensive conflict resolution strategies")
        print("  • Complete workflow integration")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)