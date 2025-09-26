#!/usr/bin/env python3
"""
Cover Crop Selection Integration Test

Tests the integration between frontend UI and cover crop backend service
by verifying API proxy routes and template structure.
"""

import sys
import os
sys.path.append('services/frontend/src')

def test_frontend_integration():
    """Test frontend integration components"""
    results = []
    
    # Test 1: Frontend module import
    try:
        from main import app
        results.append("✅ Frontend main module imported successfully")
    except Exception as e:
        results.append(f"❌ Frontend import failed: {e}")
        return results
    
    # Test 2: Cover crop page route exists
    cover_crop_routes = [route for route in app.routes if 'cover-crop-selection' in str(route.path)]
    if cover_crop_routes:
        results.append("✅ Cover crop selection page route exists")
    else:
        results.append("❌ Cover crop selection page route missing")
    
    # Test 3: API proxy routes exist
    api_routes = [route for route in app.routes if 'cover-crop' in str(route.path) and '/api/' in str(route.path)]
    if len(api_routes) >= 15:
        results.append(f"✅ Cover crop API proxy routes exist ({len(api_routes)} routes)")
    else:
        results.append(f"❌ Insufficient API proxy routes ({len(api_routes)} found, expected 15+)")
    
    # Test 4: Template file exists
    template_path = "services/frontend/src/templates/cover_crop_selection.html"
    if os.path.exists(template_path):
        results.append("✅ Cover crop selection HTML template exists")
        
        # Test 5: Template uses correct API endpoints
        with open(template_path, 'r') as f:
            template_content = f.read()
            
        api_calls = [
            '/api/cover-crops/species',
            '/api/cover-crops/goal-based-recommendations', 
            '/api/cover-crops/benefits/predict',
            '/api/cover-crops/timing'
        ]
        
        missing_apis = []
        for api_call in api_calls:
            if api_call not in template_content:
                missing_apis.append(api_call)
        
        if not missing_apis:
            results.append("✅ Template uses correct API endpoints")
        else:
            results.append(f"❌ Template missing API calls: {missing_apis}")
    else:
        results.append("❌ Cover crop selection HTML template missing")
    
    # Test 6: Key proxy routes validation
    key_routes = [
        '/api/cover-crops/select',
        '/api/cover-crops/species', 
        '/api/cover-crops/goal-based-recommendations',
        '/api/cover-crops/benefits/predict',
        '/api/cover-crops/timing',
        '/api/cover-crops/types',
        '/api/cover-crops/benefits'
    ]
    
    route_paths = [str(route.path) for route in app.routes]
    missing_routes = []
    for key_route in key_routes:
        if not any(key_route in path for path in route_paths):
            missing_routes.append(key_route)
    
    if not missing_routes:
        results.append("✅ All key API proxy routes implemented")
    else:
        results.append(f"❌ Missing key proxy routes: {missing_routes}")
    
    return results

def test_backend_service_structure():
    """Test backend service structure and endpoints"""
    results = []
    
    # Test 7: Backend service files exist
    backend_files = [
        "services/cover-crop-selection/src/api/routes.py",
        "services/cover-crop-selection/src/services/cover_crop_selection_service.py"
    ]
    
    for file_path in backend_files:
        if os.path.exists(file_path):
            results.append(f"✅ Backend file exists: {file_path}")
        else:
            results.append(f"❌ Backend file missing: {file_path}")
    
    return results

def main():
    """Run integration tests"""
    print("🧪 Running Cover Crop Selection Integration Tests...\n")
    
    # Run frontend integration tests
    print("Frontend Integration Tests:")
    frontend_results = test_frontend_integration()
    for result in frontend_results:
        print(f"  {result}")
    
    print(f"\nBackend Structure Tests:")
    backend_results = test_backend_service_structure()
    for result in backend_results:
        print(f"  {result}")
    
    # Summary
    all_results = frontend_results + backend_results
    passed = len([r for r in all_results if r.startswith("✅")])
    total = len(all_results)
    
    print(f"\n📊 Integration Test Summary:")
    print(f"   Passed: {passed}/{total} tests")
    
    if passed == total:
        print("🎉 All integration tests passed! Cover crop selection UI is ready.")
        return True
    else:
        print("⚠️  Some integration tests failed. Review the results above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)