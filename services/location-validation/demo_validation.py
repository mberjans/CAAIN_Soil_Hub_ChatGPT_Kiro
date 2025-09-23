"""
Location Validation Service Demo
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

Demo script to test the location validation service functionality.
"""

import asyncio
import sys
import os

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src/services'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../databases/python'))

from location_validation_service import LocationValidationService


async def demo_location_validation():
    """Demonstrate location validation functionality."""
    
    print("=== AFAS Location Validation Service Demo ===\n")
    
    # Create validation service
    service = LocationValidationService()
    
    # Test cases
    test_locations = [
        {
            "name": "Ames, Iowa (Agricultural Area)",
            "latitude": 42.0308,
            "longitude": -93.6319,
            "expected": "agricultural"
        },
        {
            "name": "Chicago, Illinois (Urban Area)",
            "latitude": 41.8781,
            "longitude": -87.6298,
            "expected": "urban"
        },
        {
            "name": "Atlantic Ocean",
            "latitude": 30.0,
            "longitude": -40.0,
            "expected": "ocean"
        },
        {
            "name": "Northern Canada (Extreme Climate)",
            "latitude": 60.0,
            "longitude": -100.0,
            "expected": "extreme_climate"
        },
        {
            "name": "Invalid Coordinates",
            "latitude": 91.0,
            "longitude": -93.6319,
            "expected": "invalid"
        }
    ]
    
    for i, location in enumerate(test_locations, 1):
        print(f"{i}. Testing: {location['name']}")
        print(f"   Coordinates: ({location['latitude']}, {location['longitude']})")
        
        try:
            # Test basic coordinate validation
            result = await service.validate_coordinates(location['latitude'], location['longitude'])
            
            print(f"   Basic Validation: {'✓ Valid' if result.valid else '✗ Invalid'}")
            
            if result.errors:
                print(f"   Errors: {', '.join(result.errors)}")
            
            if result.warnings:
                print(f"   Warnings: {', '.join(result.warnings)}")
            
            if result.geographic_info:
                print(f"   Geographic Info:")
                print(f"     - State: {result.geographic_info.state}")
                print(f"     - County: {result.geographic_info.county}")
                print(f"     - Climate Zone: {result.geographic_info.climate_zone}")
                print(f"     - Agricultural Area: {'Yes' if result.geographic_info.is_agricultural else 'No'}")
            
            # Test agricultural validation if basic validation passes
            if result.valid:
                agri_result = await service.validate_agricultural_location(
                    location['latitude'], location['longitude']
                )
                
                print(f"   Agricultural Validation: {'✓ Valid' if agri_result.valid else '✗ Invalid'}")
                
                if agri_result.warnings and agri_result.warnings != result.warnings:
                    print(f"   Additional Agricultural Warnings: {', '.join(agri_result.warnings)}")
        
        except Exception as e:
            print(f"   Error: {e}")
        
        print()  # Empty line for readability
    
    # Test agricultural suitability analysis
    print("=== Agricultural Suitability Analysis ===\n")
    
    agricultural_locations = [
        ("Iowa Farmland", 42.0308, -93.6319),
        ("Illinois Farmland", 40.1164, -88.2434),
        ("Nebraska Farmland", 41.2565, -95.9345),
        ("California Central Valley", 36.7783, -119.4179)
    ]
    
    for name, lat, lon in agricultural_locations:
        print(f"Analyzing: {name}")
        print(f"Coordinates: ({lat}, {lon})")
        
        try:
            analysis = await service._analyze_agricultural_suitability(lat, lon)
            
            print(f"Agricultural Area: {'Yes' if analysis['is_agricultural'] else 'No'}")
            print(f"Suitability Score: {analysis['suitability_score']:.2f}")
            print(f"Reasoning: {analysis['reasoning']}")
            
            if 'factors' in analysis:
                print("Suitability Factors:")
                for factor, score in analysis['factors'].items():
                    print(f"  - {factor.replace('_', ' ').title()}: {score:.2f}")
        
        except Exception as e:
            print(f"Error: {e}")
        
        print()
    
    print("=== Demo Complete ===")


async def demo_error_handling():
    """Demonstrate error handling capabilities."""
    
    print("=== Error Handling Demo ===\n")
    
    service = LocationValidationService()
    
    # Test predefined errors
    error_codes = ["INVALID_COORDINATES", "NON_AGRICULTURAL_AREA", "GEOCODING_FAILED"]
    
    for error_code in error_codes:
        error = await service.get_validation_error(error_code)
        print(f"Error Code: {error.error_code}")
        print(f"Message: {error.error_message}")
        print(f"Agricultural Context: {error.agricultural_context}")
        print(f"Suggested Actions: {', '.join(error.suggested_actions)}")
        print()


if __name__ == "__main__":
    print("Starting Location Validation Service Demo...\n")
    
    # Run the demo
    asyncio.run(demo_location_validation())
    print("\n" + "="*50 + "\n")
    asyncio.run(demo_error_handling())
    
    print("\nDemo completed successfully!")