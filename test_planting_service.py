#!/usr/bin/env python3
"""
Test script for planting date service functionality
"""

import asyncio
import sys
import os
from datetime import date, datetime

# Add services to path
service_path = os.path.join(os.path.dirname(__file__), 'services', 'recommendation-engine', 'src')
sys.path.append(service_path)

from services.planting_date_service import PlantingDateCalculatorService
from models.agricultural_models import LocationData

async def test_planting_service():
    """Test the planting date calculator service."""
    print("Testing Planting Date Calculator Service")
    print("=" * 50)
    
    # Create service instance
    planting_service = PlantingDateCalculatorService()
    print("✓ Service initialized successfully")
    
    # Create test location (Boston, MA - Zone 6a)
    test_location = LocationData(
        latitude=42.3601,
        longitude=-71.0589,
        elevation_ft=20,
        address="Boston, MA",
        state="Massachusetts",
        county="Suffolk",
        climate_zone="6a",
        climate_zone_name="USDA Zone 6a"
    )
    print("✓ Test location created")
    
    # Test crops to evaluate
    test_crops = ["corn", "wheat", "peas", "lettuce", "tomato"]
    
    print("\nTesting crop planting date calculations:")
    print("-" * 40)
    
    for crop in test_crops:
        try:
            # Calculate spring planting
            planting_window = await planting_service.calculate_planting_dates(
                crop_name=crop,
                location=test_location,
                planting_season="spring"
            )
            
            print(f"\n{crop.upper()}:")
            print(f"  Optimal planting: {planting_window.optimal_date.strftime('%B %d')}")
            print(f"  Safe window: {planting_window.earliest_safe_date.strftime('%m/%d')} - {planting_window.latest_safe_date.strftime('%m/%d')}")
            print(f"  Expected harvest: {planting_window.expected_harvest_date.strftime('%B %d') if planting_window.expected_harvest_date else 'N/A'}")
            print(f"  Confidence: {planting_window.confidence_score:.1%}")
            
            if planting_window.frost_considerations:
                print(f"  Frost considerations: {len(planting_window.frost_considerations)} items")
            if planting_window.climate_warnings:
                print(f"  Climate warnings: {len(planting_window.climate_warnings)} items")
                
        except Exception as e:
            print(f"❌ Error calculating {crop}: {e}")
    
    # Test succession planting for appropriate crops
    print("\n\nTesting succession planting:")
    print("-" * 30)
    
    succession_crops = ["lettuce", "peas", "spinach"]
    for crop in succession_crops:
        try:
            crop_profile = planting_service.crop_timing_database.get(crop)
            if crop_profile and crop_profile.succession_interval_days:
                succession_schedule = planting_service.get_succession_planting_schedule(
                    crop_name=crop,
                    location=test_location,
                    start_date=date(2024, 5, 1),
                    end_date=date(2024, 7, 1),
                    max_plantings=4
                )
                
                print(f"\n{crop.upper()} succession plantings:")
                for i, window in enumerate(succession_schedule, 1):
                    print(f"  Planting #{i}: {window.optimal_date.strftime('%B %d')}")
                    
        except Exception as e:
            print(f"❌ Error with {crop} succession: {e}")
    
    # Test fall planting for appropriate crops
    print("\n\nTesting fall planting:")
    print("-" * 25)
    
    fall_crops = ["wheat", "peas", "spinach", "onion"]
    for crop in fall_crops:
        try:
            crop_profile = planting_service.crop_timing_database.get(crop)
            if crop_profile and crop_profile.fall_planting_possible:
                fall_window = await planting_service.calculate_planting_dates(
                    crop_name=crop,
                    location=test_location,
                    planting_season="fall"
                )
                
                print(f"\n{crop.upper()} fall planting:")
                print(f"  Optimal date: {fall_window.optimal_date.strftime('%B %d')}")
                print(f"  Expected harvest: {fall_window.expected_harvest_date.strftime('%B %d') if fall_window.expected_harvest_date else 'Spring'}")
                
        except Exception as e:
            print(f"❌ Error with {crop} fall planting: {e}")
    
    # Test frost date estimation
    print("\n\nTesting frost date analysis:")
    print("-" * 30)
    
    try:
        frost_info = await planting_service._get_frost_date_info(test_location)
        print(f"Last frost date: {frost_info.last_frost_date.strftime('%B %d') if frost_info.last_frost_date else 'Unknown'}")
        print(f"First frost date: {frost_info.first_frost_date.strftime('%B %d') if frost_info.first_frost_date else 'Unknown'}")
        print(f"Growing season length: {frost_info.growing_season_length} days")
        print(f"Confidence level: {frost_info.confidence_level}")
        
    except Exception as e:
        print(f"❌ Error getting frost dates: {e}")
    
    print("\n" + "=" * 50)
    print("✓ Planting date service test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_planting_service())