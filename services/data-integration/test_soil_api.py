#!/usr/bin/env python3
"""
Test script for Soil API endpoints

Tests the soil-related API endpoints in the data integration service.
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import httpx
from fastapi.testclient import TestClient
from fastapi import FastAPI

# Import the router with proper path handling
try:
    from src.api.routes import router
except ImportError:
    # Fallback for different path structures
    sys.path.insert(0, os.path.dirname(__file__))
    from src.api.routes import router

# Create test app
app = FastAPI()
app.include_router(router)
client = TestClient(app)


def test_soil_characteristics_endpoint():
    """Test the soil characteristics endpoint."""
    
    print("🧪 Testing /api/v1/soil/characteristics endpoint")
    
    # Test data
    test_locations = [
        {"latitude": 42.0308, "longitude": -93.6319, "name": "Ames, Iowa"},
        {"latitude": 40.1164, "longitude": -88.2434, "name": "Champaign, Illinois"},
    ]
    
    for location in test_locations:
        print(f"   Testing {location['name']}...")
        
        response = client.post(
            "/api/v1/soil/characteristics",
            json={
                "latitude": location["latitude"],
                "longitude": location["longitude"]
            }
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Soil Series: {data.get('soil_series', 'Unknown')}")
            print(f"   ✅ Texture: {data.get('soil_texture', 'Unknown')}")
            print(f"   ✅ Drainage: {data.get('drainage_class', 'Unknown')}")
            print(f"   ✅ pH Range: {data.get('typical_ph_range', {})}")
            print(f"   ✅ Organic Matter: {data.get('organic_matter_typical', 0)}%")
        else:
            print(f"   ❌ Error: {response.text}")


def test_soil_nutrient_ranges_endpoint():
    """Test the soil nutrient ranges endpoint."""
    
    print("\n🧪 Testing /api/v1/soil/nutrient-ranges endpoint")
    
    response = client.post(
        "/api/v1/soil/nutrient-ranges",
        json={
            "latitude": 42.0308,
            "longitude": -93.6319
        }
    )
    
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ P Range: {data.get('phosphorus_ppm_range', {})}")
        print(f"   ✅ K Range: {data.get('potassium_ppm_range', {})}")
        print(f"   ✅ Typical N: {data.get('nitrogen_typical', 0)} lbs/acre")
        print(f"   ✅ CEC Range: {data.get('cec_range', {})}")
        print(f"   ✅ Micronutrients: {data.get('micronutrient_status', {})}")
    else:
        print(f"   ❌ Error: {response.text}")


def test_soil_crop_suitability_endpoint():
    """Test the soil crop suitability endpoint."""
    
    print("\n🧪 Testing /api/v1/soil/crop-suitability endpoint")
    
    response = client.post(
        "/api/v1/soil/crop-suitability",
        json={
            "latitude": 42.0308,
            "longitude": -93.6319
        }
    )
    
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Crop Suitability: {data.get('crop_suitability', {})}")
        print(f"   ✅ Limitations: {data.get('limitations', [])}")
        print(f"   ✅ Management: {data.get('management_considerations', [])}")
        print(f"   ✅ Irrigation Suitability: {data.get('irrigation_suitability', 'Unknown')}")
        print(f"   ✅ Erosion Risk: {data.get('erosion_risk', 'Unknown')}")
    else:
        print(f"   ❌ Error: {response.text}")


def test_invalid_coordinates():
    """Test error handling with invalid coordinates."""
    
    print("\n🧪 Testing error handling with invalid coordinates")
    
    # Test with invalid latitude
    response = client.post(
        "/api/v1/soil/characteristics",
        json={
            "latitude": 999,  # Invalid
            "longitude": -93.6319
        }
    )
    
    print(f"   Invalid latitude - Status Code: {response.status_code}")
    if response.status_code == 422:
        print("   ✅ Properly rejected invalid latitude")
    else:
        print(f"   ⚠️  Unexpected response: {response.text}")
    
    # Test with invalid longitude
    response = client.post(
        "/api/v1/soil/characteristics",
        json={
            "latitude": 42.0308,
            "longitude": 999  # Invalid
        }
    )
    
    print(f"   Invalid longitude - Status Code: {response.status_code}")
    if response.status_code == 422:
        print("   ✅ Properly rejected invalid longitude")
    else:
        print(f"   ⚠️  Unexpected response: {response.text}")


def test_response_schemas():
    """Test that responses match expected schemas."""
    
    print("\n🧪 Testing response schemas")
    
    # Test soil characteristics schema
    response = client.post(
        "/api/v1/soil/characteristics",
        json={"latitude": 42.0308, "longitude": -93.6319}
    )
    
    if response.status_code == 200:
        data = response.json()
        
        # Check required fields
        required_fields = [
            'soil_series', 'soil_texture', 'drainage_class',
            'typical_ph_range', 'organic_matter_typical', 'slope_range'
        ]
        
        missing_fields = [field for field in required_fields if field not in data]
        
        if not missing_fields:
            print("   ✅ Soil characteristics schema valid")
        else:
            print(f"   ❌ Missing fields in soil characteristics: {missing_fields}")
        
        # Check data types
        if isinstance(data.get('typical_ph_range'), dict):
            print("   ✅ pH range is properly formatted as dict")
        else:
            print("   ❌ pH range should be a dict")
        
        if isinstance(data.get('organic_matter_typical'), (int, float)):
            print("   ✅ Organic matter is numeric")
        else:
            print("   ❌ Organic matter should be numeric")
    
    # Test nutrient ranges schema
    response = client.post(
        "/api/v1/soil/nutrient-ranges",
        json={"latitude": 42.0308, "longitude": -93.6319}
    )
    
    if response.status_code == 200:
        data = response.json()
        
        required_fields = [
            'phosphorus_ppm_range', 'potassium_ppm_range', 'nitrogen_typical',
            'cec_range', 'base_saturation_range', 'micronutrient_status'
        ]
        
        missing_fields = [field for field in required_fields if field not in data]
        
        if not missing_fields:
            print("   ✅ Nutrient ranges schema valid")
        else:
            print(f"   ❌ Missing fields in nutrient ranges: {missing_fields}")


def test_agricultural_accuracy():
    """Test agricultural accuracy of responses."""
    
    print("\n🧪 Testing agricultural accuracy")
    
    # Test Iowa location (should be good for corn/soybean)
    response = client.post(
        "/api/v1/soil/crop-suitability",
        json={"latitude": 42.0308, "longitude": -93.6319}
    )
    
    if response.status_code == 200:
        data = response.json()
        crop_suitability = data.get('crop_suitability', {})
        
        # Iowa should be good for corn and soybean
        corn_rating = crop_suitability.get('corn', 'unknown')
        soybean_rating = crop_suitability.get('soybean', 'unknown')
        
        if corn_rating in ['excellent', 'good']:
            print(f"   ✅ Corn rating appropriate for Iowa: {corn_rating}")
        else:
            print(f"   ⚠️  Corn rating may be low for Iowa: {corn_rating}")
        
        if soybean_rating in ['excellent', 'good']:
            print(f"   ✅ Soybean rating appropriate for Iowa: {soybean_rating}")
        else:
            print(f"   ⚠️  Soybean rating may be low for Iowa: {soybean_rating}")
        
        # Check for reasonable limitations
        limitations = data.get('limitations', [])
        print(f"   📋 Identified limitations: {len(limitations)}")
        
        # Check for management considerations
        management = data.get('management_considerations', [])
        print(f"   💡 Management considerations: {len(management)}")


def performance_test():
    """Test API response times."""
    
    print("\n⏱️  Testing API performance")
    
    import time
    
    # Test multiple requests
    locations = [
        {"latitude": 42.0308, "longitude": -93.6319},
        {"latitude": 40.1164, "longitude": -88.2434},
        {"latitude": 39.1836, "longitude": -96.5717}
    ]
    
    total_time = 0
    successful_requests = 0
    
    for i, location in enumerate(locations):
        start_time = time.time()
        
        response = client.post(
            "/api/v1/soil/characteristics",
            json=location
        )
        
        end_time = time.time()
        request_time = end_time - start_time
        total_time += request_time
        
        if response.status_code == 200:
            successful_requests += 1
            print(f"   Request {i+1}: {request_time:.2f}s ✅")
        else:
            print(f"   Request {i+1}: {request_time:.2f}s ❌")
    
    if successful_requests > 0:
        avg_time = total_time / successful_requests
        print(f"   Average response time: {avg_time:.2f}s")
        
        if avg_time < 5.0:
            print("   ✅ Performance acceptable (<5s)")
        else:
            print("   ⚠️  Performance may be slow (>5s)")


if __name__ == "__main__":
    print("🌾 AFAS Soil API Test Suite")
    print(f"Started at: {datetime.now().isoformat()}")
    print("=" * 60)
    
    try:
        # Run API endpoint tests
        test_soil_characteristics_endpoint()
        test_soil_nutrient_ranges_endpoint()
        test_soil_crop_suitability_endpoint()
        
        # Run error handling tests
        test_invalid_coordinates()
        
        # Run schema validation tests
        test_response_schemas()
        
        # Run agricultural accuracy tests
        test_agricultural_accuracy()
        
        # Run performance tests
        performance_test()
        
        print("\n" + "=" * 60)
        print("✅ All API tests completed!")
        print(f"Completed at: {datetime.now().isoformat()}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)