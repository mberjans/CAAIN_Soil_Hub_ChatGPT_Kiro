#!/usr/bin/env python3
\"\"\"
Test script for Climate Zone Enhanced Weather Service Integration

Verifies that the climate zone enhanced weather service endpoints
are properly registered and accessible.
\"\"\"

import asyncio
import sys
import os

# Add the services directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services', 'data-integration', 'src'))

async def test_climate_zone_integration():
    \"\"\"Test that climate zone enhanced weather service is working.\"\"\"
    print(\"Testing Climate Zone Enhanced Weather Service Integration...\")
    
    try:
        # Import required modules
        from services.data_integration.src.services.weather_service import WeatherService
        from services.data_integration.src.api.climate_weather_routes import ClimateZoneDataResponse
        
        # Create weather service instance
        weather_service = WeatherService()
        
        # Test coordinates (Ames, Iowa - typical agricultural area)
        latitude = 42.0308
        longitude = -93.6319
        
        print(f\"Testing with coordinates: {latitude}, {longitude}\")
        
        # Test climate zone data retrieval
        print(\"1. Testing climate zone data retrieval...\")
        climate_data = await weather_service.get_climate_zone_data(latitude, longitude)
        
        if climate_data:
            print(f\"   ✓ Successfully retrieved climate zone data\")
            print(f\"   USDA Zone: {climate_data.usda_zone}\")
            print(f\"   Köppen Classification: {climate_data.koppen_classification}\")
            print(f\"   Average Min Temp: {climate_data.average_min_temp_f}°F\")
            print(f\"   Growing Season Length: {climate_data.growing_season_length} days\")
        else:
            print(\"   ✗ Failed to retrieve climate zone data\")
            return False
            
        # Test that the data is properly structured
        print(\"2. Testing climate zone data structure...\")
        required_fields = [
            'usda_zone', 'koppen_classification', 'average_min_temp_f', 
            'average_max_temp_f', 'annual_precipitation_inches', 'growing_season_length'
        ]
        
        for field in required_fields:
            if not hasattr(climate_data, field):
                print(f\"   ✗ Missing required field: {field}\")
                return False
                
        print(\"   ✓ All required fields present\")
        
        # Test that the data makes sense agriculturally
        print(\"3. Testing climate zone data validity...\")
        if not (1 <= int(climate_data.usda_zone[0]) <= 13):
            print(f\"   ✗ Invalid USDA zone: {climate_data.usda_zone}\")
            return False
            
        if climate_data.growing_season_length < 0 or climate_data.growing_season_length > 365:
            print(f\"   ✗ Invalid growing season length: {climate_data.growing_season_length}\")
            return False
            
        print(\"   ✓ Climate zone data appears valid\")
        
        # Test cache functionality
        print(\"4. Testing cache functionality...\")
        # Get the same data again (should come from cache)
        climate_data_cached = await weather_service.get_climate_zone_data(latitude, longitude)
        
        if climate_data_cached.usda_zone == climate_data.usda_zone:
            print(\"   ✓ Cache appears to be working\")
        else:
            print(\"   ⚠ Cache may not be working correctly\")
            
        print(\"\\n✓ All climate zone integration tests passed!\")
        return True
        
    except Exception as e:
        print(f\"✗ Error during testing: {str(e)}\")
        import traceback
        traceback.print_exc()
        return False

async def test_api_route_registration():
    \"\"\"Test that API routes are properly registered.\"\"\"
    print(\"\\nTesting API Route Registration...\")
    
    try:
        # Import the routes
        from services.data_integration.src.api.routes import router
        from services.data_integration.src.api.climate_weather_routes import router as climate_router
        
        # Check that climate routes are registered
        print(\"1. Checking climate weather route registration...\")
        
        # Look for our new endpoints
        climate_endpoints = [
            \"/api/v1/weather/climate-zone\",
            \"/api/v1/weather/climate-enhanced\",
            \"/api/v1/weather/agricultural-metrics-climate-enhanced\",
            \"/api/v1/weather/climate-forecast\"
        ]
        
        registered_paths = [route.path for route in router.routes]
        
        found_endpoints = []
        missing_endpoints = []
        
        for endpoint in climate_endpoints:
            if any(path.endswith(endpoint) for path in registered_paths):
                found_endpoints.append(endpoint)
            else:
                missing_endpoints.append(endpoint)
                
        if found_endpoints:
            print(f\"   ✓ Found registered endpoints: {found_endpoints}\")
            
        if missing_endpoints:
            print(f\"   ⚠ Missing endpoints: {missing_endpoints}\")
        else:
            print(\"   ✓ All climate weather endpoints registered\")
            
        return len(missing_endpoints) == 0
        
    except Exception as e:
        print(f\"✗ Error testing API route registration: {str(e)}\")
        return False

async def main():
    \"\"\"Main test function.\"\"\"
    print(\"=\" * 60)
    print(\"CLIMATE ZONE ENHANCED WEATHER SERVICE INTEGRATION TEST\")
    print(\"=\" * 60)
    
    # Run integration tests
    climate_success = await test_climate_zone_integration()
    api_success = await test_api_route_registration()
    
    print(\"\\n\" + \"=\" * 60)
    if climate_success and api_success:
        print(\"🎉 ALL TESTS PASSED!\")
        print(\"Climate zone enhanced weather service integration is working correctly.\")
        return True
    else:
        print(\"❌ SOME TESTS FAILED!\")
        print(\"Please check the implementation and run tests again.\")
        return False
    print(\"=\" * 60)

if __name__ == \"__main__\":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)