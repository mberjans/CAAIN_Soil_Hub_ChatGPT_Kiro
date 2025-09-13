#!/usr/bin/env python3
"""
Test Weather API Endpoints

Simple script to test the weather API endpoints using requests.
"""

import requests
import json
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_weather_endpoints():
    """Test weather API endpoints."""
    
    print("🧪 Testing Weather API Endpoints")
    print("=" * 40)
    
    # Test data
    test_location = {
        "latitude": 42.0308,
        "longitude": -93.6319
    }
    
    base_url = "http://localhost:8003"
    
    # Test health endpoint
    print("\n🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        print("   Make sure the service is running on port 8003")
        return
    
    # Test current weather endpoint
    print("\n🌡️ Testing current weather endpoint...")
    try:
        response = requests.post(
            f"{base_url}/api/v1/weather/current",
            json=test_location,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Current weather endpoint working")
            print(f"   Temperature: {data.get('temperature_f')}°F")
            print(f"   Conditions: {data.get('conditions')}")
            print(f"   Humidity: {data.get('humidity_percent')}%")
        else:
            print(f"❌ Current weather failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Current weather failed: {e}")
    
    # Test forecast endpoint
    print("\n📅 Testing forecast endpoint...")
    try:
        response = requests.post(
            f"{base_url}/api/v1/weather/forecast?days=3",
            json=test_location,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Forecast endpoint working")
            print(f"   Forecast days: {len(data)}")
            if data:
                print(f"   First day: {data[0].get('date')} - {data[0].get('high_temp_f')}°F/{data[0].get('low_temp_f')}°F")
        else:
            print(f"❌ Forecast failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Forecast failed: {e}")
    
    # Test agricultural metrics endpoint
    print("\n🌾 Testing agricultural metrics endpoint...")
    try:
        response = requests.post(
            f"{base_url}/api/v1/weather/agricultural-metrics?base_temp_f=50.0",
            json=test_location,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Agricultural metrics endpoint working")
            print(f"   Growing Degree Days: {data.get('growing_degree_days')}")
            print(f"   Days Since Rain: {data.get('days_since_rain')}")
            print(f"   Recommendations: {len(data.get('recommendations', []))}")
        else:
            print(f"❌ Agricultural metrics failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Agricultural metrics failed: {e}")
    
    print("\n✨ API endpoint testing completed!")


if __name__ == "__main__":
    test_weather_endpoints()