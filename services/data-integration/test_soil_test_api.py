#!/usr/bin/env python3
"""
Test script for soil test API endpoints.

This script tests the soil test functionality including manual entry,
file upload, and interpretation endpoints.
"""

import asyncio
import httpx
import json
from datetime import date

# Test data
SAMPLE_SOIL_TEST = {
    "ph": 6.2,
    "organic_matter_percent": 3.5,
    "phosphorus_ppm": 25,
    "potassium_ppm": 180,
    "nitrogen_ppm": 12,
    "soil_texture": "silt_loam",
    "cec_meq_per_100g": 18.5,
    "test_date": date.today().isoformat(),
    "lab_name": "Iowa State Soil Testing Lab",
    "test_notes": "Test sample from north field"
}

PROBLEMATIC_SOIL_TEST = {
    "ph": 5.1,  # Too acidic
    "organic_matter_percent": 1.2,  # Too low
    "phosphorus_ppm": 8,  # Deficient
    "potassium_ppm": 65,  # Low
    "test_date": date.today().isoformat()
}

BASE_URL = "http://localhost:8003"

async def test_manual_soil_test_submission():
    """Test manual soil test data submission."""
    print("Testing manual soil test submission...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/soil-tests/manual",
                json=SAMPLE_SOIL_TEST,
                timeout=30.0
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Manual soil test submission successful!")
                print(f"Test ID: {result.get('test_id')}")
                print(f"Confidence Score: {result.get('confidence_score', 0):.2f}")
                print(f"Recommendations: {len(result.get('recommendations', []))}")
                
                # Print first few recommendations
                for i, rec in enumerate(result.get('recommendations', [])[:3]):
                    print(f"  {i+1}. {rec}")
                
                return True
            else:
                print(f"❌ Manual soil test submission failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing manual submission: {e}")
            return False

async def test_soil_test_interpretation():
    """Test soil test interpretation endpoint."""
    print("\nTesting soil test interpretation...")
    
    async with httpx.AsyncClient() as client:
        try:
            params = {
                "ph": 6.2,
                "organic_matter_percent": 3.5,
                "phosphorus_ppm": 25,
                "potassium_ppm": 180,
                "soil_texture": "silt_loam",
                "crop_type": "corn"
            }
            
            response = await client.post(
                f"{BASE_URL}/api/v1/soil-tests/interpret",
                params=params,
                timeout=30.0
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Soil test interpretation successful!")
                print(f"Overall Rating: {result.get('overall_rating')}")
                print(f"Confidence Score: {result.get('confidence_score', 0):.2f}")
                print(f"Limiting Factors: {result.get('limiting_factors', [])}")
                print(f"Nutrient Status: {result.get('nutrient_status', {})}")
                print(f"Recommendations: {len(result.get('recommendations', []))}")
                
                return True
            else:
                print(f"❌ Soil test interpretation failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing interpretation: {e}")
            return False

async def test_problematic_soil():
    """Test with problematic soil conditions."""
    print("\nTesting problematic soil conditions...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/soil-tests/manual",
                json=PROBLEMATIC_SOIL_TEST,
                timeout=30.0
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Problematic soil test processed!")
                print(f"Confidence Score: {result.get('confidence_score', 0):.2f}")
                
                # Should have multiple recommendations for problematic soil
                recommendations = result.get('recommendations', [])
                print(f"Recommendations: {len(recommendations)}")
                
                # Check for expected recommendations
                rec_text = ' '.join(recommendations).lower()
                if 'lime' in rec_text:
                    print("  ✅ Lime recommendation found (for low pH)")
                if 'organic matter' in rec_text:
                    print("  ✅ Organic matter recommendation found")
                if 'phosphorus' in rec_text:
                    print("  ✅ Phosphorus recommendation found")
                
                return True
            else:
                print(f"❌ Problematic soil test failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing problematic soil: {e}")
            return False

async def test_validation_ranges():
    """Test validation ranges endpoint."""
    print("\nTesting validation ranges endpoint...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/api/v1/soil-tests/validation-ranges",
                timeout=30.0
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Validation ranges retrieved!")
                
                # Check key parameters
                if 'ph' in result:
                    ph_range = result['ph']
                    print(f"  pH range: {ph_range['min']}-{ph_range['max']}")
                    print(f"  pH optimal: {ph_range['optimal_range']['min']}-{ph_range['optimal_range']['max']}")
                
                if 'phosphorus_ppm' in result:
                    p_range = result['phosphorus_ppm']
                    print(f"  P range: {p_range['min']}-{p_range['max']} {p_range['units']}")
                
                if 'soil_texture_options' in result:
                    textures = result['soil_texture_options']
                    print(f"  Soil textures: {len(textures)} options")
                
                return True
            else:
                print(f"❌ Validation ranges failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing validation ranges: {e}")
            return False

async def test_invalid_data():
    """Test with invalid soil test data."""
    print("\nTesting invalid data handling...")
    
    invalid_data = {
        "ph": 15.0,  # Invalid pH
        "organic_matter_percent": -5.0,  # Invalid negative value
        "phosphorus_ppm": "not_a_number",  # Invalid type
        "test_date": "invalid_date"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/v1/soil-tests/manual",
                json=invalid_data,
                timeout=30.0
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 422:
                print("✅ Invalid data properly rejected!")
                error_detail = response.json().get('detail', '')
                print(f"  Error: {error_detail}")
                return True
            else:
                print(f"❌ Invalid data should have been rejected but got: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing invalid data: {e}")
            return False

async def main():
    """Run all soil test API tests."""
    print("🧪 Starting Soil Test API Tests")
    print("=" * 50)
    
    tests = [
        test_validation_ranges,
        test_manual_soil_test_submission,
        test_soil_test_interpretation,
        test_problematic_soil,
        test_invalid_data
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("🧪 Test Results Summary")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)