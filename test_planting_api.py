#!/usr/bin/env python3
"""
Test script for planting date API endpoints
"""

import asyncio
import sys
import os
import json
from datetime import date

# Add services to path
service_path = os.path.join(os.path.dirname(__file__), 'services', 'recommendation-engine', 'src')
sys.path.append(service_path)

from fastapi.testclient import TestClient
from fastapi import FastAPI
from api.planting_routes import router

def test_planting_api():
    """Test the planting date API endpoints."""
    print("Testing Planting Date API Endpoints")
    print("=" * 50)
    
    # Create test app
    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)
    print("✓ Test API client created")
    
    # Sample location data
    sample_location = {
        "latitude": 42.3601,
        "longitude": -71.0589,
        "elevation_ft": 20,
        "address": "Boston, MA",
        "state": "Massachusetts",
        "county": "Suffolk",
        "climate_zone": "6a",
        "climate_zone_name": "USDA Zone 6a"
    }
    
    print("\n1. Testing available crops endpoint:")
    print("-" * 35)
    
    try:
        response = client.get("/api/v1/planting/available-crops")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Found {data['total_crops']} available crops")
            
            # Show sample crops
            for crop in data['available_crops'][:3]:
                print(f"  - {crop['crop_name']}: {crop['crop_category']}, {crop['frost_tolerance']} frost tolerance")
        else:
            print(f"❌ Failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n2. Testing frost dates endpoint:")
    print("-" * 30)
    
    try:
        frost_request = {"location": sample_location}
        response = client.post("/api/v1/planting/frost-dates", json=frost_request)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Frost dates retrieved successfully")
            print(f"  Last frost: {data.get('last_frost_date', 'Unknown')}")
            print(f"  First frost: {data.get('first_frost_date', 'Unknown')}")
            print(f"  Growing season: {data.get('growing_season_length', 'Unknown')} days")
            print(f"  Confidence: {data.get('confidence_level', 'Unknown')}")
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n3. Testing planting date calculation:")
    print("-" * 35)
    
    test_crops = ["corn", "lettuce", "wheat"]
    
    for crop in test_crops:
        try:
            planting_request = {
                "crop_name": crop,
                "location": sample_location,
                "planting_season": "spring"
            }
            
            response = client.post("/api/v1/planting/calculate-dates", json=planting_request)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ {crop.upper()}: {data['optimal_date']} (confidence: {data['confidence_score']:.1%})")
            else:
                print(f"❌ {crop.upper()} failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error with {crop}: {e}")
    
    print("\n4. Testing comprehensive planting window:")
    print("-" * 40)
    
    try:
        window_request = {
            "crop_name": "lettuce",
            "location": sample_location,
            "succession_planting": True,
            "max_plantings": 3
        }
        
        response = client.post("/api/v1/planting/planting-window", json=window_request)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Comprehensive analysis for {data['crop_name']}")
            print(f"  Found {len(data['planting_windows'])} planting windows")
            print(f"  Location: {data['location_summary']}")
            
            if data.get('succession_schedule'):
                print(f"  Succession plantings: {len(data['succession_schedule'])}")
            
            if data.get('recommendations'):
                print(f"  Recommendations: {len(data['recommendations'])}")
                for rec in data['recommendations'][:2]:
                    print(f"    - {rec}")
                    
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n5. Testing succession planting schedule:")
    print("-" * 40)
    
    try:
        succession_request = {
            "crop_name": "lettuce",
            "location": sample_location,
            "start_date": "2024-05-01",
            "end_date": "2024-07-01",
            "max_plantings": 4
        }
        
        response = client.post("/api/v1/planting/succession-schedule", json=succession_request)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Generated {len(data)} succession plantings")
            for i, planting in enumerate(data, 1):
                print(f"  Planting #{i}: {planting['optimal_date']}")
        else:
            print(f"❌ Failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✓ API endpoint testing completed!")

if __name__ == "__main__":
    test_planting_api()