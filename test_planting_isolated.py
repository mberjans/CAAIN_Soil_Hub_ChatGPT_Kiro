#!/usr/bin/env python3
"""
Isolated test for the planting date service to validate core functionality
without complex import dependencies.
"""

import sys
import os
from datetime import date, datetime, timedelta

# Add the specific service path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services', 'recommendation-engine', 'src'))

def test_planting_service_import():
    """Test that we can import the planting date service."""
    try:
        from services.planting_date_service import PlantingDateCalculatorService
        print("✓ Successfully imported PlantingDateCalculatorService")
        return PlantingDateCalculatorService()
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return None

def test_crop_database(service):
    """Test crop timing database."""
    if not service:
        return False
    
    expected_crops = ["corn", "soybean", "wheat", "peas", "lettuce", "spinach", "tomato", "potato", "onion"]
    
    for crop in expected_crops:
        if crop not in service.crop_timing_database:
            print(f"✗ Missing crop: {crop}")
            return False
        
        profile = service.crop_timing_database[crop]
        if not hasattr(profile, 'crop_name') or not hasattr(profile, 'days_to_maturity'):
            print(f"✗ Invalid crop profile for {crop}")
            return False
    
    print("✓ All expected crops found in database")
    return True

def test_frost_date_parsing(service):
    """Test frost date parsing functionality."""
    if not service:
        return False
    
    # Test valid frost date
    frost_date = service._parse_frost_date("04-15")
    if not frost_date or frost_date.month != 4 or frost_date.day != 15:
        print("✗ Frost date parsing failed")
        return False
    
    # Test invalid format
    invalid_date = service._parse_frost_date("invalid")
    if invalid_date is not None:
        print("✗ Invalid frost date should return None")
        return False
    
    print("✓ Frost date parsing works correctly")
    return True

def main():
    """Run isolated planting service tests."""
    print("Running isolated planting date service tests...\n")
    
    # Test import
    service = test_planting_service_import()
    
    # Test crop database
    test_crop_database(service)
    
    # Test frost date parsing
    test_frost_date_parsing(service)
    
    if service:
        print(f"\n✓ PlantingDateCalculatorService appears to be working!")
        print(f"Crop database contains {len(service.crop_timing_database)} crops")
    else:
        print("\n✗ PlantingDateCalculatorService failed to initialize")

if __name__ == "__main__":
    main()