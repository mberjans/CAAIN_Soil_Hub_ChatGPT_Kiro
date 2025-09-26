#!/usr/bin/env python3
"""
Integration test for pH management system.
Tests the complete workflow from frontend to recommendation engine.
"""

import asyncio
import httpx
import json
from datetime import datetime

# Service URLs
FRONTEND_URL = "http://localhost:3000"
RECOMMENDATION_ENGINE_URL = "http://localhost:8001"

async def test_service_health():
    """Test that services are running and healthy."""
    print("🔍 Testing service health...")
    
    try:
        # Test frontend
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{FRONTEND_URL}/health")
            if response.status_code == 200:
                print("✅ Frontend service is healthy")
            else:
                print(f"❌ Frontend service unhealthy: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Frontend service unavailable: {e}")
        return False
    
    try:
        # Test recommendation engine
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{RECOMMENDATION_ENGINE_URL}/health")
            if response.status_code == 200:
                print("✅ Recommendation engine service is healthy (degraded mode OK)")
            else:
                print(f"❌ Recommendation engine unhealthy: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Recommendation engine unavailable: {e}")
        return False
    
    return True

async def test_direct_ph_analysis():
    """Test pH analysis directly through recommendation engine."""
    print("\n🧪 Testing direct pH analysis...")
    
    try:
        test_data = {
            "farm_id": "integration_test_farm",
            "field_id": "test_field_1",
            "crop_type": "corn",
            "soil_test_data": {
                "ph": 5.8,
                "organic_matter_percent": 4.2,
                "phosphorus_ppm": 22.0,
                "potassium_ppm": 165.0,
                "soil_texture": "clay_loam",
                "test_date": datetime.now().date().isoformat()
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{RECOMMENDATION_ENGINE_URL}/api/v1/ph/analyze",
                json=test_data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success") and "analysis" in result:
                    analysis = result["analysis"]
                    print(f"✅ pH analysis successful:")
                    print(f"   Current pH: {analysis['current_ph']}")
                    print(f"   Target pH: {analysis['target_ph']}")
                    print(f"   pH Level: {analysis['ph_level']}")
                    print(f"   Priority: {analysis['management_priority']}")
                    return True
                else:
                    print(f"❌ Invalid response format: {result}")
                    return False
            else:
                print(f"❌ pH analysis failed: {response.status_code} - {response.text}")
                return False
    except Exception as e:
        print(f"❌ Direct pH analysis error: {e}")
        return False

async def test_direct_lime_calculator():
    """Test lime calculator directly through recommendation engine."""
    print("\n🧮 Testing direct lime calculator...")
    
    try:
        test_data = {
            "current_ph": 5.2,
            "target_ph": 6.5,
            "soil_texture": "sandy_loam",
            "organic_matter_percent": 2.8,
            "field_size_acres": 15.5
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{RECOMMENDATION_ENGINE_URL}/api/v1/ph/lime-calculator",
                json=test_data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success") and "lime_requirements" in result:
                    requirements = result["lime_requirements"]
                    print(f"✅ Lime calculation successful:")
                    print(f"   Number of recommendations: {len(requirements)}")
                    for i, rec in enumerate(requirements):
                        print(f"   Option {i+1}: {rec['lime_type']} - {rec['application_rate_tons_per_acre']} tons/acre")
                        print(f"            Cost: ${rec['cost_per_acre']:.2f}/acre")
                    return True
                else:
                    print(f"❌ Invalid lime calculator response: {result}")
                    return False
            else:
                print(f"❌ Lime calculator failed: {response.status_code} - {response.text}")
                return False
    except Exception as e:
        print(f"❌ Direct lime calculator error: {e}")
        return False

async def test_frontend_ph_analysis():
    """Test pH analysis through frontend proxy."""
    print("\n🌐 Testing frontend pH analysis proxy...")
    
    try:
        form_data = {
            "farm_id": "frontend_test_farm",
            "field_id": "test_field_2",
            "crop_type": "soybeans",
            "ph": 6.8,
            "organic_matter": 3.2,
            "phosphorus": 18.5,
            "potassium": 140.0
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{FRONTEND_URL}/api/ph/analyze",
                data=form_data  # Using form data as expected by frontend
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success") and "analysis" in result:
                    analysis = result["analysis"]
                    print(f"✅ Frontend pH analysis successful:")
                    print(f"   Current pH: {analysis['current_ph']}")
                    print(f"   pH Level: {analysis['ph_level']}")
                    print(f"   Management Priority: {analysis['management_priority']}")
                    return True
                else:
                    print(f"❌ Invalid frontend response: {result}")
                    return False
            else:
                print(f"❌ Frontend pH analysis failed: {response.status_code} - {response.text}")
                return False
    except Exception as e:
        print(f"❌ Frontend pH analysis error: {e}")
        return False

async def test_frontend_lime_calculator():
    """Test lime calculator through frontend proxy."""
    print("\n🌐 Testing frontend lime calculator proxy...")
    
    try:
        form_data = {
            "current_ph": 5.0,
            "target_ph": 6.2,
            "soil_texture": "loam",
            "organic_matter_percent": 3.5,
            "field_size_acres": 8.0
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{FRONTEND_URL}/api/ph/lime-calculator",
                data=form_data  # Using form data as expected by frontend
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success") and "lime_requirements" in result:
                    requirements = result["lime_requirements"]
                    print(f"✅ Frontend lime calculator successful:")
                    print(f"   Recommendations: {len(requirements)}")
                    for rec in requirements:
                        print(f"   {rec['lime_type']}: {rec['application_rate_tons_per_acre']} tons/acre")
                    return True
                else:
                    print(f"❌ Invalid frontend lime response: {result}")
                    return False
            else:
                print(f"❌ Frontend lime calculator failed: {response.status_code} - {response.text}")
                return False
    except Exception as e:
        print(f"❌ Frontend lime calculator error: {e}")
        return False

async def run_integration_tests():
    """Run all integration tests."""
    print("🚀 Starting pH Management Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Service Health Check", test_service_health),
        ("Direct pH Analysis", test_direct_ph_analysis),
        ("Direct Lime Calculator", test_direct_lime_calculator),
        ("Frontend pH Analysis Proxy", test_frontend_ph_analysis),
        ("Frontend Lime Calculator Proxy", test_frontend_lime_calculator)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            success = await test_func()
            results[test_name] = success
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Print final results
    print("\n" + "=" * 50)
    print("📊 INTEGRATION TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
        if success:
            passed += 1
    
    print(f"\nSUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL INTEGRATION TESTS PASSED! pH Management system is fully functional.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    asyncio.run(run_integration_tests())