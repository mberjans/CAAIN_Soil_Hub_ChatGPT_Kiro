#!/usr/bin/env python3
"""
Test script for variety selection endpoints
"""

import requests
import json
import sys
from pathlib import Path

# Add the crop-taxonomy service to Python path
sys.path.insert(0, str(Path(__file__).parent / "services" / "crop-taxonomy" / "src"))

def test_crop_search():
    """Test the crop search endpoint"""
    print("Testing crop search endpoint...")
    
    # Import the search function directly
    from api.taxonomy_routes import search_crops
    
    # Test the search function
    try:
        # Mock request with query parameter
        class MockQuery:
            def __init__(self, value):
                self.value = value
        
        # Test search for corn
        result = search_crops("corn", 5)
        print(f"✓ Crop search for 'corn': Found {len(result)} results")
        if result:
            print(f"  First result: {result[0]['name']} ({result[0]['scientific_name']})")
        
        # Test search for soybean
        result = search_crops("soybean", 5)
        print(f"✓ Crop search for 'soybean': Found {len(result)} results")
        
        return True
    except Exception as e:
        print(f"✗ Crop search test failed: {e}")
        return False

def test_variety_recommendations():
    """Test the variety recommendations endpoint"""
    print("\nTesting variety recommendations endpoint...")
    
    # Import the recommendation function directly
    from api.variety_routes import recommend_varieties_advanced
    
    try:
        # Test request data
        request_data = {
            "crop_id": "corn",
            "farm_data": {
                "location": "Ames, Iowa",
                "farmSize": 160,
                "soilType": "loam",
                "irrigation": True
            },
            "user_preferences": {
                "yieldPriority": 8,
                "qualityFocus": "premium",
                "riskTolerance": "moderate",
                "managementIntensity": "medium"
            },
            "max_recommendations": 5
        }
        
        result = recommend_varieties_advanced(request_data)
        print(f"✓ Variety recommendations for corn: Found {len(result)} recommendations")
        if result:
            print(f"  First recommendation: {result[0]['name']} (Confidence: {result[0]['confidence']})")
        
        return True
    except Exception as e:
        print(f"✗ Variety recommendations test failed: {e}")
        return False

def test_variety_explanations():
    """Test the variety explanations endpoint"""
    print("\nTesting variety explanations endpoint...")
    
    # Import the explanation function directly
    from api.variety_routes import explain_variety_recommendations
    
    try:
        # Test request data (frontend format)
        request_data = {
            "crop_id": "corn",
            "farm_data": {
                "location": "Ames, Iowa",
                "farmSize": 160,
                "soilType": "loam",
                "irrigation": True
            },
            "user_preferences": {
                "yieldPriority": 8,
                "qualityFocus": "premium",
                "riskTolerance": "moderate",
                "managementIntensity": "medium"
            },
            "recommendations": [
                {
                    "id": "pioneer-1197",
                    "name": "Pioneer P1197AM",
                    "confidence": 0.92
                }
            ]
        }
        
        result = explain_variety_recommendations(request_data)
        print(f"✓ Variety explanations: Generated explanation")
        if result and "summary" in result:
            print(f"  Summary: {result['summary'][:100]}...")
        
        return True
    except Exception as e:
        print(f"✗ Variety explanations test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Variety Selection Endpoints")
    print("=" * 50)
    
    tests = [
        test_crop_search,
        test_variety_recommendations,
        test_variety_explanations
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The variety selection interface should work correctly.")
        return True
    else:
        print("❌ Some tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)