#!/usr/bin/env python3
"""
Advanced Variety Display Integration Test

Tests the integration between the advanced variety display frontend
and the crop taxonomy backend services.
"""

import asyncio
import httpx
import json
import pytest
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test configuration
FRONTEND_URL = "http://localhost:3000"
CROP_TAXONOMY_URL = "http://localhost:8003"
TEST_TIMEOUT = 30.0

class AdvancedVarietyDisplayTester:
    """Test suite for advanced variety display integration."""
    
    def __init__(self):
        self.frontend_url = FRONTEND_URL
        self.backend_url = CROP_TAXONOMY_URL
        self.test_results = []
    
    async def test_frontend_availability(self) -> bool:
        """Test that the frontend service is available."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.frontend_url}/advanced-variety-display",
                    timeout=TEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    logger.info("✅ Frontend service is available")
                    return True
                else:
                    logger.error(f"❌ Frontend service returned status {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Frontend service unavailable: {e}")
            return False
    
    async def test_backend_availability(self) -> bool:
        """Test that the crop taxonomy backend service is available."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.backend_url}/health",
                    timeout=TEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    logger.info("✅ Crop taxonomy backend service is available")
                    return True
                else:
                    logger.error(f"❌ Backend service returned status {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Backend service unavailable: {e}")
            return False
    
    async def test_crop_search_api(self) -> bool:
        """Test crop search API functionality."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.backend_url}/api/v1/crops/search",
                    params={
                        "query": "corn",
                        "limit": 10
                    },
                    timeout=TEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("crops") and len(data["crops"]) > 0:
                        logger.info(f"✅ Crop search API working - found {len(data['crops'])} crops")
                        return True
                    else:
                        logger.warning("⚠️ Crop search API returned empty results")
                        return False
                else:
                    logger.error(f"❌ Crop search API returned status {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Crop search API error: {e}")
            return False
    
    async def test_variety_recommendation_api(self) -> bool:
        """Test variety recommendation API functionality."""
        try:
            # First get a crop ID
            async with httpx.AsyncClient() as client:
                crop_response = await client.get(
                    f"{self.backend_url}/api/v1/crops/search",
                    params={"query": "corn", "limit": 1},
                    timeout=TEST_TIMEOUT
                )
                
                if crop_response.status_code != 200:
                    logger.error("❌ Could not get crop for variety recommendation test")
                    return False
                
                crop_data = crop_response.json()
                if not crop_data.get("crops"):
                    logger.error("❌ No crops found for variety recommendation test")
                    return False
                
                crop_id = crop_data["crops"][0]["id"]
                
                # Test variety recommendation
                recommendation_response = await client.post(
                    f"{self.backend_url}/api/v1/varieties/recommend",
                    json={
                        "crop_id": crop_id,
                        "location": {
                            "latitude": 40.0,
                            "longitude": -95.0,
                            "climate_zone": "5a"
                        },
                        "soil_data": {
                            "ph": 6.5,
                            "organic_matter_percent": 3.0,
                            "phosphorus_ppm": 25,
                            "potassium_ppm": 150
                        },
                        "preferences": {
                            "yield_priority": "high",
                            "disease_resistance_priority": "medium",
                            "maturity_preference": "early"
                        }
                    },
                    timeout=TEST_TIMEOUT
                )
                
                if recommendation_response.status_code == 200:
                    data = recommendation_response.json()
                    if data.get("recommended_varieties") and len(data["recommended_varieties"]) > 0:
                        logger.info(f"✅ Variety recommendation API working - found {len(data['recommended_varieties'])} varieties")
                        return True
                    else:
                        logger.warning("⚠️ Variety recommendation API returned empty results")
                        return False
                else:
                    logger.error(f"❌ Variety recommendation API returned status {recommendation_response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Variety recommendation API error: {e}")
            return False
    
    async def test_variety_comparison_api(self) -> bool:
        """Test variety comparison API functionality."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.backend_url}/api/v1/varieties/compare",
                    json={
                        "variety_ids": ["1", "2", "3"],
                        "comparison_criteria": [
                            "yield_potential",
                            "disease_resistance",
                            "maturity_days",
                            "climate_adaptation"
                        ]
                    },
                    timeout=TEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("comparison_matrix"):
                        logger.info("✅ Variety comparison API working")
                        return True
                    else:
                        logger.warning("⚠️ Variety comparison API returned empty comparison matrix")
                        return False
                else:
                    logger.error(f"❌ Variety comparison API returned status {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Variety comparison API error: {e}")
            return False
    
    async def test_variety_filtering_api(self) -> bool:
        """Test variety filtering API functionality."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.backend_url}/api/v1/varieties/filter",
                    json={
                        "crop_id": "1",
                        "filters": {
                            "min_overall_score": 0.8,
                            "max_overall_score": 1.0,
                            "min_confidence": 0.7,
                            "max_confidence": 1.0,
                            "disease_resistance_level": "high",
                            "maturity_range": {
                                "min": 100,
                                "max": 130
                            }
                        },
                        "sort_criteria": "overall_score",
                        "sort_direction": "desc"
                    },
                    timeout=TEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("filtered_varieties") is not None:
                        logger.info(f"✅ Variety filtering API working - found {len(data.get('filtered_varieties', []))} varieties")
                        return True
                    else:
                        logger.warning("⚠️ Variety filtering API returned no filtered varieties")
                        return False
                else:
                    logger.error(f"❌ Variety filtering API returned status {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Variety filtering API error: {e}")
            return False
    
    async def test_frontend_api_proxy(self) -> bool:
        """Test that frontend API proxy routes work correctly."""
        try:
            async with httpx.AsyncClient() as client:
                # Test crops API proxy
                response = await client.get(
                    f"{self.frontend_url}/api/v1/crops/search",
                    params={"query": "corn", "limit": 5},
                    timeout=TEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("crops"):
                        logger.info("✅ Frontend crops API proxy working")
                        return True
                    else:
                        logger.warning("⚠️ Frontend crops API proxy returned empty results")
                        return False
                else:
                    logger.error(f"❌ Frontend crops API proxy returned status {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Frontend API proxy error: {e}")
            return False
    
    async def test_advanced_variety_display_page(self) -> bool:
        """Test that the advanced variety display page loads correctly."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.frontend_url}/advanced-variety-display",
                    timeout=TEST_TIMEOUT
                )
                
                if response.status_code == 200:
                    content = response.text
                    # Check for key elements
                    required_elements = [
                        "Advanced Variety Display",
                        "advanced-variety-display.js",
                        "advanced-variety-display.css",
                        "variety-display-container",
                        "filter-section",
                        "view-controls"
                    ]
                    
                    missing_elements = []
                    for element in required_elements:
                        if element not in content:
                            missing_elements.append(element)
                    
                    if not missing_elements:
                        logger.info("✅ Advanced variety display page loads correctly")
                        return True
                    else:
                        logger.error(f"❌ Advanced variety display page missing elements: {missing_elements}")
                        return False
                else:
                    logger.error(f"❌ Advanced variety display page returned status {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Advanced variety display page error: {e}")
            return False
    
    async def test_static_assets(self) -> bool:
        """Test that static assets (CSS, JS) are accessible."""
        try:
            async with httpx.AsyncClient() as client:
                # Test CSS file
                css_response = await client.get(
                    f"{self.frontend_url}/static/css/advanced-variety-display.css",
                    timeout=TEST_TIMEOUT
                )
                
                # Test JS file
                js_response = await client.get(
                    f"{self.frontend_url}/static/js/advanced-variety-display.js",
                    timeout=TEST_TIMEOUT
                )
                
                if css_response.status_code == 200 and js_response.status_code == 200:
                    logger.info("✅ Static assets are accessible")
                    return True
                else:
                    logger.error(f"❌ Static assets not accessible - CSS: {css_response.status_code}, JS: {js_response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Static assets error: {e}")
            return False
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive integration test suite."""
        logger.info("🚀 Starting Advanced Variety Display Integration Tests")
        
        test_results = {
            "frontend_availability": await self.test_frontend_availability(),
            "backend_availability": await self.test_backend_availability(),
            "crop_search_api": await self.test_crop_search_api(),
            "variety_recommendation_api": await self.test_variety_recommendation_api(),
            "variety_comparison_api": await self.test_variety_comparison_api(),
            "variety_filtering_api": await self.test_variety_filtering_api(),
            "frontend_api_proxy": await self.test_frontend_api_proxy(),
            "advanced_variety_display_page": await self.test_advanced_variety_display_page(),
            "static_assets": await self.test_static_assets()
        }
        
        # Calculate overall success rate
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        logger.info(f"📊 Test Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        return {
            "test_results": test_results,
            "success_rate": success_rate,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "overall_status": "PASS" if success_rate >= 80 else "FAIL"
        }
    
    async def test_performance_requirements(self) -> Dict[str, Any]:
        """Test performance requirements for the advanced variety display."""
        logger.info("⚡ Testing Performance Requirements")
        
        performance_results = {}
        
        try:
            # Test API response times
            async with httpx.AsyncClient() as client:
                start_time = asyncio.get_event_loop().time()
                
                response = await client.get(
                    f"{self.backend_url}/api/v1/crops/search",
                    params={"query": "corn", "limit": 100},
                    timeout=TEST_TIMEOUT
                )
                
                end_time = asyncio.get_event_loop().time()
                response_time = end_time - start_time
                
                performance_results["api_response_time"] = {
                    "value": response_time,
                    "requirement": "< 3 seconds",
                    "passed": response_time < 3.0
                }
                
                if response_time < 3.0:
                    logger.info(f"✅ API response time: {response_time:.2f}s (requirement: < 3s)")
                else:
                    logger.error(f"❌ API response time: {response_time:.2f}s (requirement: < 3s)")
                
                # Test large dataset handling
                if response.status_code == 200:
                    data = response.json()
                    variety_count = len(data.get("crops", []))
                    
                    performance_results["large_dataset_handling"] = {
                        "value": variety_count,
                        "requirement": "Handle 100+ varieties",
                        "passed": variety_count >= 100
                    }
                    
                    if variety_count >= 100:
                        logger.info(f"✅ Large dataset handling: {variety_count} varieties (requirement: 100+)")
                    else:
                        logger.warning(f"⚠️ Large dataset handling: {variety_count} varieties (requirement: 100+)")
                
        except Exception as e:
            logger.error(f"❌ Performance test error: {e}")
            performance_results["error"] = str(e)
        
        return performance_results

async def main():
    """Main test execution function."""
    tester = AdvancedVarietyDisplayTester()
    
    # Run comprehensive integration tests
    integration_results = await tester.run_comprehensive_test()
    
    # Run performance tests
    performance_results = await tester.test_performance_requirements()
    
    # Print summary
    print("\n" + "="*60)
    print("ADVANCED VARIETY DISPLAY INTEGRATION TEST SUMMARY")
    print("="*60)
    
    print(f"\n📊 Integration Tests:")
    for test_name, result in integration_results["test_results"].items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\n⚡ Performance Tests:")
    for test_name, result in performance_results.items():
        if isinstance(result, dict) and "passed" in result:
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(f"  {test_name}: {status} ({result['value']} - {result['requirement']})")
    
    print(f"\n🎯 Overall Status: {integration_results['overall_status']}")
    print(f"📈 Success Rate: {integration_results['success_rate']:.1f}%")
    
    if integration_results['success_rate'] >= 80:
        print("\n🎉 Advanced Variety Display Integration Tests PASSED!")
        return 0
    else:
        print("\n💥 Advanced Variety Display Integration Tests FAILED!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)