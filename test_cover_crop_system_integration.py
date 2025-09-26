#!/usr/bin/env python3
"""
Cover Crop System Integration Test

Tests the complete integration of cover crop selection service with other system components.
"""

import asyncio
import sys
from pathlib import Path

# Add service paths
sys.path.append(str(Path(__file__).parent / "services" / "question-router" / "src"))
sys.path.append(str(Path(__file__).parent / "services" / "recommendation-engine" / "src"))
sys.path.append(str(Path(__file__).parent / "shared"))

async def test_question_routing():
    """Test that cover crop questions are routed to the correct service."""
    print("🧪 Testing Question Router Integration...")
    
    try:
        from services.routing_service import QuestionRoutingService
        from models.question_models import QuestionType
        
        service = QuestionRoutingService()
        routing = await service.route_question(QuestionType.COVER_CROPS)
        
        assert routing.primary_service == "cover-crop-selection", f"Expected cover-crop-selection, got {routing.primary_service}"
        assert "recommendation-engine" in routing.secondary_services, "recommendation-engine should be in secondary services"
        assert "data-integration" in routing.secondary_services, "data-integration should be in secondary services"
        
        print("  ✅ Cover crop questions correctly routed to cover-crop-selection service")
        print(f"  ✅ Primary: {routing.primary_service}")
        print(f"  ✅ Secondary: {routing.secondary_services}")
        return True
        
    except Exception as e:
        print(f"  ❌ Question routing test failed: {e}")
        return False


async def test_service_client():
    """Test the service client utility."""
    print("🧪 Testing Service Client Utility...")
    
    try:
        from utils.service_client import ServiceClient
        
        client = ServiceClient("cover-crop-selection", "http://localhost:8001")
        
        # Test client creation
        assert client.base_url == "http://localhost:8001"
        assert client.service_name == "cover-crop-selection"
        
        print("  ✅ Service client created successfully")
        print(f"  ✅ Base URL: {client.base_url}")
        print(f"  ✅ Service Name: {client.service_name}")
        return True
        
    except Exception as e:
        print(f"  ❌ Service client test failed: {e}")
        return False


def test_integration_files():
    """Test that integration files exist."""
    print("🧪 Testing Integration Files...")
    
    files_to_check = [
        "shared/utils/service_client.py",
        "services/question-router/src/services/routing_service.py",
        "services/cover-crop-selection/src/api/routes.py",
        "services/frontend/src/templates/cover_crop_selection.html"
    ]
    
    all_exist = True
    for file_path in files_to_check:
        full_path = Path(__file__).parent / file_path
        if full_path.exists():
            print(f"  ✅ {file_path} exists")
        else:
            print(f"  ❌ {file_path} missing")
            all_exist = False
    
    return all_exist


async def test_cover_crop_service_endpoints():
    """Test that cover crop service has expected endpoints."""
    print("🧪 Testing Cover Crop Service Endpoints...")
    
    try:
        sys.path.append(str(Path(__file__).parent / "services" / "cover-crop-selection" / "src"))
        from main import app
        
        # Check that the FastAPI app can be created
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
        
        expected_endpoints = [
            "/api/cover-crops/select",
            "/api/cover-crops/species",
            "/api/cover-crops/goal-based-recommendations",
            "/api/cover-crops/timing",
            "/api/cover-crops/benefits/predict"
        ]
        
        all_found = True
        for endpoint in expected_endpoints:
            if endpoint in routes:
                print(f"  ✅ {endpoint} endpoint exists")
            else:
                print(f"  ❌ {endpoint} endpoint missing")
                all_found = False
        
        print(f"  ✅ Total cover crop endpoints: {len([r for r in routes if '/cover-crops/' in r])}")
        return all_found
        
    except Exception as e:
        print(f"  ❌ Cover crop service endpoints test failed: {e}")
        return False


async def main():
    """Run all integration tests."""
    print("🚀 Cover Crop System Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Question Routing", test_question_routing()),
        ("Service Client", test_service_client()),
        ("Integration Files", test_integration_files()),
        ("Cover Crop Endpoints", test_cover_crop_service_endpoints())
    ]
    
    results = []
    for test_name, test_coro in tests:
        if asyncio.iscoroutine(test_coro):
            result = await test_coro
        else:
            result = test_coro
        results.append((test_name, result))
        print()
    
    print("📊 Integration Test Summary:")
    print("-" * 30)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All integration tests passed! The cover crop system is fully integrated.")
        return True
    else:
        print("⚠️  Some integration tests failed. Please check the output above.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)