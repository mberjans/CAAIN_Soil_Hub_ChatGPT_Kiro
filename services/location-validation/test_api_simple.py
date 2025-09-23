"""
Simple test script for geocoding API endpoints.
"""

import sys
import os
sys.path.append('src')
sys.path.append('src/api')
sys.path.append('src/services')
sys.path.append('../../databases/python')

from fastapi.testclient import TestClient
from fastapi import FastAPI
from api.routes import router

# Create test app
app = FastAPI()
app.include_router(router)

client = TestClient(app)

def test_geocode_endpoint():
    """Test the geocode endpoint."""
    print("Testing geocode endpoint...")
    
    response = client.post("/api/v1/validation/geocode?address=Ames, Iowa")
    
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success! Coordinates: {data['latitude']:.4f}, {data['longitude']:.4f}")
        print(f"Address: {data['address']}")
        print(f"Confidence: {data['confidence']:.2f}")
    else:
        print(f"Error: {response.json()}")

def test_reverse_geocode_endpoint():
    """Test the reverse geocode endpoint."""
    print("\nTesting reverse geocode endpoint...")
    
    response = client.post("/api/v1/validation/reverse-geocode?latitude=42.0308&longitude=-93.6319")
    
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success! Address: {data['address']}")
        print(f"Confidence: {data['confidence']:.2f}")
    else:
        print(f"Error: {response.json()}")

def test_suggestions_endpoint():
    """Test the address suggestions endpoint."""
    print("\nTesting address suggestions endpoint...")
    
    response = client.get("/api/v1/validation/address-suggestions?query=Ames&limit=3")
    
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success! Found {data['count']} suggestions:")
        for i, suggestion in enumerate(data['suggestions'], 1):
            print(f"  {i}. {suggestion['address']}")
    else:
        print(f"Error: {response.json()}")

if __name__ == "__main__":
    print("Testing Geocoding API Endpoints")
    print("=" * 40)
    
    try:
        test_geocode_endpoint()
        test_reverse_geocode_endpoint()
        test_suggestions_endpoint()
        
        print("\n" + "=" * 40)
        print("All API tests completed!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()