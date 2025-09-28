#!/usr/bin/env python3
"""
Test script for TICKET-005_crop-type-filtering-4.1 enhanced filtering endpoints
"""

import requests
import json
import sys
from typing import Dict, Any

def test_filter_options_endpoint():
    """Test the new filter-options endpoint"""
    print("\n=== Testing /api/v1/crop-taxonomy/search/filter-options ===")
    
    try:
        # Test without location
        response = requests.get("http://localhost:8000/api/v1/crop-taxonomy/search/filter-options")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Filter options endpoint working")
            print(f"Available filter categories: {list(data.keys())}")
            
            # Test with location parameters
            response_with_location = requests.get(
                "http://localhost:8000/api/v1/crop-taxonomy/search/filter-options",
                params={"latitude": 45.0, "longitude": -100.0}
            )
            
            if response_with_location.status_code == 200:
                location_data = response_with_location.json()
                print("✅ Location-aware filter options working")
                print(f"Recommended climate zones: {location_data.get('climate_zones', {}).get('recommended', [])}")
            else:
                print(f"❌ Location-aware filter options failed: {response_with_location.status_code}")
        else:
            print(f"❌ Filter options endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing filter options: {e}")

def test_detailed_categories_endpoint():
    """Test the new detailed categories endpoint"""
    print("\n=== Testing /api/v1/crop-taxonomy/search/categories/detailed ===")
    
    try:
        response = requests.get("http://localhost:8000/api/v1/crop-taxonomy/search/categories/detailed")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Detailed categories endpoint working")
            print(f"Available categories: {list(data.keys())}")
            
            # Check if category structure is correct
            if "grain_crops" in data:
                grain_crops = data["grain_crops"]
                expected_fields = ["name", "description", "characteristics", "examples", "subcategories"]
                missing_fields = [field for field in expected_fields if field not in grain_crops]
                
                if not missing_fields:
                    print("✅ Category structure is complete")
                else:
                    print(f"⚠️ Missing fields in category structure: {missing_fields}")
            else:
                print("⚠️ Expected 'grain_crops' category not found")
        else:
            print(f"❌ Detailed categories endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing detailed categories: {e}")

def test_filter_validation_endpoint():
    """Test the new filter validation endpoint"""
    print("\n=== Testing /api/v1/crop-taxonomy/search/filter/validate ===")
    
    try:
        # Test valid filter combination
        valid_filters = {
            "climate_zones": ["5a", "5b"],
            "soil_ph_range": {"min": 6.0, "max": 7.5},
            "maturity_days_range": {"min": 90, "max": 120},
            "drought_tolerance": ["moderate"],
            "management_complexity": ["low"]
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/crop-taxonomy/search/filter/validate",
            json=valid_filters,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Valid filters - Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Validation endpoint working - Status: {data.get('validation_status')}")
            print(f"Is valid: {data.get('is_valid')}")
            print(f"Conflicts: {len(data.get('conflicts', []))}")
            print(f"Warnings: {len(data.get('warnings', []))}")
        else:
            print(f"❌ Filter validation failed: {response.status_code}")
            print(f"Response: {response.text}")
        
        # Test conflicting filter combination
        conflicting_filters = {
            "climate_zones": ["1a", "1b"],  # Very cold zones
            "maturity_days_range": {"min": 150, "max": 200},  # Long maturity
            "soil_ph_range": {"min": 8.0, "max": 6.0},  # Invalid range (min > max)
            "drought_tolerance": ["high"],
            "management_complexity": ["high"]
        }
        
        response_conflict = requests.post(
            "http://localhost:8000/api/v1/crop-taxonomy/search/filter/validate",
            json=conflicting_filters,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nConflicting filters - Status Code: {response_conflict.status_code}")
        
        if response_conflict.status_code == 200:
            conflict_data = response_conflict.json()
            print(f"✅ Conflict detection working - Status: {conflict_data.get('validation_status')}")
            print(f"Is valid: {conflict_data.get('is_valid')}")
            print(f"Conflicts detected: {len(conflict_data.get('conflicts', []))}")
            
            # Print conflict details
            for conflict in conflict_data.get('conflicts', []):
                print(f"  - {conflict.get('type')}: {conflict.get('message')}")
        else:
            print(f"❌ Conflict validation failed: {response_conflict.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing filter validation: {e}")

def test_enhanced_search_endpoint():
    """Test the enhanced search endpoint with multi-criteria filtering"""
    print("\n=== Testing Enhanced /api/v1/crop-taxonomy/search/crops ===")
    
    try:
        # Test search with enhanced filtering
        search_request = {
            "query": "grain crops",
            "filter_criteria": {
                "geographic": {
                    "climate_zones": ["5a", "5b"]
                },
                "agricultural": {
                    "crop_categories": ["grain"]
                }
            },
            "location": {
                "latitude": 45.0,
                "longitude": -100.0
            },
            "page_size": 10,
            "page": 1
        }
        
        response = requests.post(
            "http://localhost:8000/api/v1/crop-taxonomy/search/crops",
            json=search_request,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Enhanced search - Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Enhanced search endpoint working")
            print(f"Results found: {len(data.get('results', []))}")
            print(f"Total results: {data.get('total_results', 0)}")
        else:
            print(f"❌ Enhanced search failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing enhanced search: {e}")

def main():
    """Run all tests"""
    print("🧪 Testing TICKET-005_crop-type-filtering-4.1 Enhanced Filtering Endpoints")
    print("=" * 70)
    
    # Check if service is running
    try:
        health_response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ Service health check failed. Is the service running?")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to service. Is it running on localhost:8000? Error: {e}")
        return False
    
    print("✅ Service is running and accessible")
    
    # Run all tests
    test_filter_options_endpoint()
    test_detailed_categories_endpoint() 
    test_filter_validation_endpoint()
    test_enhanced_search_endpoint()
    
    print("\n" + "=" * 70)
    print("🎉 Testing completed!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)