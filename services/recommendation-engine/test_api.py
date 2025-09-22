#!/usr/bin/env python3
"""
Test script for the Recommendation Engine API

Tests the FastAPI endpoints and API functionality.
"""

import asyncio
import sys
import os
from datetime import date
from uuid import uuid4
import json

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_endpoint():
    """Test the health check endpoint."""
    print("\n=== Testing Health Endpoint ===")
    
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    print(f"Service: {data['service']}")
    print(f"Status: {data['status']}")
    print(f"Version: {data['version']}")
    
    assert data["service"] == "recommendation-engine"
    assert data["status"] == "healthy"
    print("✓ Health endpoint working correctly")


def test_root_endpoint():
    """Test the root endpoint."""
    print("\n=== Testing Root Endpoint ===")
    
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    print(f"Message: {data['message']}")
    print(f"Available endpoints: {len(data['endpoints'])}")
    
    assert "Recommendation Engine" in data["message"]
    assert "endpoints" in data
    print("✓ Root endpoint working correctly")


def test_crop_selection_api():
    """Test the crop selection API endpoint."""
    print("\n=== Testing Crop Selection API ===")
    
    request_data = {
        "request_id": str(uuid4()),
        "question_type": "crop_selection",
        "location": {
            "latitude": 42.0308,
            "longitude": -93.6319,
            "address": "Ames, Iowa, USA"
        },
        "soil_data": {
            "ph": 6.2,
            "organic_matter_percent": 3.8,
            "phosphorus_ppm": 25,
            "potassium_ppm": 180,
            "test_date": "2024-03-15"
        },
        "farm_profile": {
            "farm_id": "test_farm_api",
            "farm_size_acres": 320,
            "primary_crops": ["corn", "soybean"],
            "equipment_available": ["planter", "combine"],
            "irrigation_available": False
        }
    }
    
    response = client.post("/api/v1/recommendations/crop-selection", json=request_data)
    
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 200
    
    data = response.json()
    print(f"Request ID: {data['request_id']}")
    print(f"Question Type: {data['question_type']}")
    print(f"Overall Confidence: {data['overall_confidence']:.2f}")
    print(f"Number of Recommendations: {len(data['recommendations'])}")
    
    # Validate response structure
    assert "request_id" in data
    assert "question_type" in data
    assert "overall_confidence" in data
    assert "recommendations" in data
    assert "confidence_factors" in data
    
    # Check recommendations
    for i, rec in enumerate(data["recommendations"][:2], 1):
        print(f"\n{i}. {rec['title']}")
        print(f"   Confidence: {rec['confidence_score']:.2f}")
        print(f"   Priority: {rec['priority']}")
    
    print("✓ Crop selection API working correctly")
    return data


def test_fertilizer_strategy_api():
    """Test the fertilizer strategy API endpoint."""
    print("\n=== Testing Fertilizer Strategy API ===")
    
    request_data = {
        "request_id": str(uuid4()),
        "question_type": "fertilizer_strategy",
        "location": {
            "latitude": 42.0,
            "longitude": -93.6
        },
        "soil_data": {
            "ph": 6.0,
            "organic_matter_percent": 3.2,
            "phosphorus_ppm": 18,
            "potassium_ppm": 140,
            "nitrogen_ppm": 8,
            "test_date": "2024-03-01"
        },
        "crop_data": {
            "crop_name": "corn",
            "yield_goal": 180,
            "previous_crop": "soybean"
        }
    }
    
    response = client.post("/api/v1/recommendations/fertilizer-strategy", json=request_data)
    
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 200
    
    data = response.json()
    print(f"Overall Confidence: {data['overall_confidence']:.2f}")
    print(f"Number of Recommendations: {len(data['recommendations'])}")
    
    # Check for fertilizer-specific recommendations
    fertilizer_types = [rec['recommendation_type'] for rec in data['recommendations']]
    print(f"Recommendation Types: {fertilizer_types}")
    
    print("✓ Fertilizer strategy API working correctly")
    return data


def test_soil_fertility_api():
    """Test the soil fertility API endpoint."""
    print("\n=== Testing Soil Fertility API ===")
    
    request_data = {
        "request_id": str(uuid4()),
        "question_type": "soil_fertility",
        "location": {
            "latitude": 40.5,
            "longitude": -89.4
        },
        "soil_data": {
            "ph": 5.8,
            "organic_matter_percent": 2.1,
            "phosphorus_ppm": 12,
            "potassium_ppm": 95,
            "test_date": "2024-02-15"
        }
    }
    
    response = client.post("/api/v1/recommendations/soil-fertility", json=request_data)
    
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 200
    
    data = response.json()
    print(f"Overall Confidence: {data['overall_confidence']:.2f}")
    print(f"Number of Recommendations: {len(data['recommendations'])}")
    
    # Should have lime recommendation for low pH
    lime_recs = [rec for rec in data['recommendations'] if 'lime' in rec['title'].lower()]
    print(f"Lime recommendations found: {len(lime_recs)}")
    
    print("✓ Soil fertility API working correctly")
    return data


def test_general_recommendations_api():
    """Test the general recommendations API endpoint."""
    print("\n=== Testing General Recommendations API ===")
    
    request_data = {
        "request_id": str(uuid4()),
        "question_type": "crop_rotation",
        "location": {
            "latitude": 41.5,
            "longitude": -90.5
        },
        "crop_data": {
            "crop_name": "corn",
            "rotation_history": ["corn", "corn", "corn"]
        }
    }
    
    response = client.post("/api/v1/recommendations/generate", json=request_data)
    
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 200
    
    data = response.json()
    print(f"Question Type: {data['question_type']}")
    print(f"Overall Confidence: {data['overall_confidence']:.2f}")
    print(f"Number of Recommendations: {len(data['recommendations'])}")
    
    print("✓ General recommendations API working correctly")
    return data


def test_error_handling():
    """Test API error handling."""
    print("\n=== Testing Error Handling ===")
    
    # Test with invalid data
    invalid_request = {
        "request_id": str(uuid4()),
        "question_type": "crop_selection",
        "location": {
            "latitude": 200,  # Invalid latitude
            "longitude": -93.6
        }
    }
    
    response = client.post("/api/v1/recommendations/crop-selection", json=invalid_request)
    
    print(f"Status Code for invalid data: {response.status_code}")
    # Should return 422 for validation error
    assert response.status_code == 422
    
    # Test with missing required fields
    incomplete_request = {
        "request_id": str(uuid4())
        # Missing question_type and location
    }
    
    response = client.post("/api/v1/recommendations/crop-selection", json=incomplete_request)
    
    print(f"Status Code for incomplete data: {response.status_code}")
    assert response.status_code == 422
    
    print("✓ Error handling working correctly")


def test_confidence_factors():
    """Test confidence factor calculations in API responses."""
    print("\n=== Testing Confidence Factors ===")
    
    # Test with complete data
    complete_request = {
        "request_id": str(uuid4()),
        "question_type": "crop_selection",
        "location": {
            "latitude": 42.0,
            "longitude": -93.6
        },
        "soil_data": {
            "ph": 6.5,
            "organic_matter_percent": 3.5,
            "phosphorus_ppm": 30,
            "potassium_ppm": 200,
            "test_date": "2024-03-01"
        }
    }
    
    response = client.post("/api/v1/recommendations/crop-selection", json=complete_request)
    assert response.status_code == 200
    
    data = response.json()
    cf = data["confidence_factors"]
    
    print("Complete Data Confidence Factors:")
    print(f"  Soil Data Quality: {cf['soil_data_quality']:.2f}")
    print(f"  Regional Data Availability: {cf['regional_data_availability']:.2f}")
    print(f"  Seasonal Appropriateness: {cf['seasonal_appropriateness']:.2f}")
    print(f"  Expert Validation: {cf['expert_validation']:.2f}")
    print(f"  Overall Confidence: {data['overall_confidence']:.2f}")
    
    # Test with minimal data
    minimal_request = {
        "request_id": str(uuid4()),
        "question_type": "crop_selection",
        "location": {
            "latitude": 42.0,
            "longitude": -93.6
        }
    }
    
    response = client.post("/api/v1/recommendations/crop-selection", json=minimal_request)
    assert response.status_code == 200
    
    data = response.json()
    cf = data["confidence_factors"]
    
    print("\nMinimal Data Confidence Factors:")
    print(f"  Soil Data Quality: {cf['soil_data_quality']:.2f}")
    print(f"  Overall Confidence: {data['overall_confidence']:.2f}")
    
    # Complete data should have higher confidence
    assert cf['soil_data_quality'] < 0.5  # Should be low without soil data
    
    print("✓ Confidence factors working correctly")


def main():
    """Run all API tests."""
    print("Starting Recommendation Engine API Tests")
    print("=" * 50)
    
    try:
        # Test basic endpoints
        test_health_endpoint()
        test_root_endpoint()
        
        # Test recommendation endpoints
        test_crop_selection_api()
        test_fertilizer_strategy_api()
        test_soil_fertility_api()
        test_general_recommendations_api()
        
        # Test error handling and edge cases
        test_error_handling()
        test_confidence_factors()
        
        print("\n" + "=" * 50)
        print("All API tests completed successfully!")
        
    except Exception as e:
        print(f"\nAPI test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)