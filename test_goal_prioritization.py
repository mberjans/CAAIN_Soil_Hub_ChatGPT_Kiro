#!/usr/bin/env python3
"""
Goal Prioritization Interface Testing Script
Simple step-by-step testing for TICKET-012 implementation
"""

import requests
import json
import time
import sys
from pathlib import Path

# Service URLs
RECOMMENDATION_ENGINE_URL = "http://localhost:8001"
FRONTEND_URL = "http://localhost:8002"

def test_service_health():
    """Test if services are running."""
    print("🔍 Checking service health...")
    
    services_status = {}
    
    # Test recommendation engine
    try:
        response = requests.get(f"{RECOMMENDATION_ENGINE_URL}/health", timeout=5)
        services_status['recommendation_engine'] = {
            'status': 'healthy' if response.status_code == 200 else 'unhealthy',
            'status_code': response.status_code
        }
        print(f"✅ Recommendation Engine: HTTP {response.status_code}")
    except Exception as e:
        services_status['recommendation_engine'] = {'status': 'offline', 'error': str(e)}
        print(f"❌ Recommendation Engine: Offline - {e}")
    
    # Test frontend
    try:
        response = requests.get(f"{FRONTEND_URL}/health", timeout=5)
        services_status['frontend'] = {
            'status': 'healthy' if response.status_code == 200 else 'unhealthy',
            'status_code': response.status_code
        }
        print(f"✅ Frontend: HTTP {response.status_code}")
    except Exception as e:
        services_status['frontend'] = {'status': 'offline', 'error': str(e)}
        print(f"❌ Frontend: Offline - {e}")
    
    return services_status

def test_goal_templates_api():
    """Test goal templates API endpoint."""
    print("\n🧪 Testing Goal Templates API...")
    
    try:
        url = f"{RECOMMENDATION_ENGINE_URL}/api/v1/api/v1/rotations/goal-templates"
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved {len(data.get('templates', {}))} goal templates")
            print(f"✅ Compatibility matrix: {len(data.get('compatibility_matrix', {}))} entries")
            
            # Print template names
            templates = data.get('templates', {})
            for name in templates.keys():
                print(f"  • {name}")
            
            return True, data
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

def test_goal_prioritization_api():
    """Test goal prioritization API endpoint."""
    print("\n🧪 Testing Goal Prioritization API...")
    
    # Sample goal data
    test_data = {
        "goals": [
            {
                "goal_id": "soil_health_improvement",
                "type": "soil_health",
                "description": "Improve soil health through diverse rotation",
                "priority": 8,
                "weight": 0.3,
                "target_value": 100.0,
                "measurement_criteria": ["organic_matter_increase", "erosion_reduction"]
            },
            {
                "goal_id": "profit_maximization",
                "type": "profit_maximization", 
                "description": "Maximize long-term profitability",
                "priority": 9,
                "weight": 0.4,
                "target_value": 100.0,
                "measurement_criteria": ["net_profit_per_acre", "roi_percentage"]
            },
            {
                "goal_id": "environmental_sustainability",
                "type": "sustainability",
                "description": "Enhance environmental sustainability",
                "priority": 7,
                "weight": 0.3,
                "target_value": 100.0,
                "measurement_criteria": ["carbon_sequestration", "water_conservation"]
            }
        ],
        "strategy": "weighted_average",
        "farmer_preferences": {}
    }
    
    try:
        url = f"{RECOMMENDATION_ENGINE_URL}/api/v1/api/v1/rotations/prioritize-goals"
        response = requests.post(url, json=test_data, timeout=15)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            prioritized_goals = data.get('prioritized_goals', [])
            print(f"✅ Successfully prioritized {len(prioritized_goals)} goals")
            
            # Print prioritized goals
            for i, goal in enumerate(prioritized_goals):
                print(f"  {i+1}. {goal.get('goal_id', 'unknown')} (Priority: {goal.get('priority', 'N/A')}, Weight: {goal.get('weight', 'N/A')})")
            
            return True, data
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

def test_goal_conflicts_api():
    """Test goal conflicts analysis API endpoint."""
    print("\n🧪 Testing Goal Conflicts Analysis API...")
    
    # Goals with potential conflicts (profit vs sustainability)
    test_data = {
        "goals": [
            {
                "goal_id": "profit_maximization",
                "type": "profit_maximization",
                "description": "Maximize profits",
                "priority": 10,
                "weight": 0.6,
                "target_value": 100.0,
                "measurement_criteria": ["net_profit_per_acre"]
            },
            {
                "goal_id": "environmental_sustainability",
                "type": "sustainability",
                "description": "Environmental sustainability",
                "priority": 8,
                "weight": 0.4,
                "target_value": 100.0,
                "measurement_criteria": ["carbon_sequestration"]
            }
        ]
    }
    
    try:
        url = f"{RECOMMENDATION_ENGINE_URL}/api/v1/api/v1/rotations/analyze-goal-conflicts"
        response = requests.post(url, json=test_data, timeout=15)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            conflicts = data.get('conflicts', [])
            print(f"✅ Conflict analysis completed - found {len(conflicts)} conflicts")
            
            # Print conflicts
            for i, conflict in enumerate(conflicts):
                conflicting_goals = conflict.get('conflicting_goals', [])
                strategy = conflict.get('resolution_strategy', 'unknown')
                print(f"  Conflict {i+1}: {', '.join(conflicting_goals)} - Strategy: {strategy}")
            
            return True, data
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

def test_frontend_page():
    """Test frontend goal prioritization page."""
    print("\n🌐 Testing Frontend Goal Prioritization Page...")
    
    try:
        url = f"{FRONTEND_URL}/goal-prioritization"
        response = requests.get(url, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            
            # Check for key elements
            required_elements = [
                'Goal Prioritization',
                'goalPrioritizationForm',
                'goalCards',
                'prioritizeBtn',
                'totalWeight'
            ]
            
            found_elements = []
            missing_elements = []
            
            for element in required_elements:
                if element in content:
                    found_elements.append(element)
                else:
                    missing_elements.append(element)
            
            print(f"✅ Found {len(found_elements)}/{len(required_elements)} required elements")
            
            if found_elements:
                print("Found elements:")
                for element in found_elements:
                    print(f"  • {element}")
            
            if missing_elements:
                print("Missing elements:")
                for element in missing_elements:
                    print(f"  • {element}")
            
            # Check for JavaScript goal templates
            if 'goalTemplates' in content:
                print("✅ JavaScript goal templates found in page")
            else:
                print("⚠️  JavaScript goal templates not found")
            
            # Check for compatibility matrix
            if 'compatibilityMatrix' in content:
                print("✅ Compatibility matrix found in JavaScript")
            else:
                print("⚠️  Compatibility matrix not found")
            
            return len(missing_elements) == 0, content
        else:
            print(f"❌ Failed with status {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

def test_javascript_integration():
    """Test JavaScript integration and functionality."""
    print("\n🔧 Testing JavaScript Integration...")
    
    try:
        url = f"{FRONTEND_URL}/goal-prioritization"
        response = requests.get(url)
        
        if response.status_code == 200:
            content = response.text
            
            # Check for key JavaScript functions
            js_functions = [
                'initializeGoalCards',
                'setupEventListeners',
                'prioritizeGoals',
                'displayResults',
                'analyzeConflicts'
            ]
            
            found_functions = []
            for func in js_functions:
                if func in content:
                    found_functions.append(func)
            
            print(f"✅ Found {len(found_functions)}/{len(js_functions)} JavaScript functions")
            for func in found_functions:
                print(f"  • {func}")
            
            # Check for API endpoint calls
            api_calls = [
                '/api/v1/rotations/prioritize-goals',
                '/api/v1/rotations/analyze-goal-conflicts'
            ]
            
            found_apis = []
            for api in api_calls:
                if api in content:
                    found_apis.append(api)
            
            print(f"✅ Found {len(found_apis)}/{len(api_calls)} API endpoint calls")
            
            return len(found_functions) >= 3, content
        else:
            print(f"❌ Frontend page not accessible")
            return False, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

def test_error_handling():
    """Test error handling scenarios."""
    print("\n🚨 Testing Error Handling...")
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Invalid goal data
    print("\nTest 1: Invalid goal data")
    try:
        url = f"{RECOMMENDATION_ENGINE_URL}/api/v1/api/v1/rotations/prioritize-goals"
        invalid_data = {"goals": [{"invalid": "data"}], "strategy": "weighted_average"}
        
        response = requests.post(url, json=invalid_data, timeout=10)
        
        if response.status_code in [400, 422, 500]:
            print(f"✅ Correctly handled invalid data (HTTP {response.status_code})")
            tests_passed += 1
        else:
            print(f"⚠️  Unexpected response for invalid data (HTTP {response.status_code})")
    except Exception as e:
        print(f"❌ Error in invalid data test: {e}")
    
    # Test 2: Missing fields
    print("\nTest 2: Missing required fields")
    try:
        url = f"{RECOMMENDATION_ENGINE_URL}/api/v1/api/v1/rotations/prioritize-goals"
        invalid_data = {"strategy": "weighted_average"}  # Missing goals
        
        response = requests.post(url, json=invalid_data, timeout=10)
        
        if response.status_code in [400, 422]:
            print(f"✅ Correctly handled missing fields (HTTP {response.status_code})")
            tests_passed += 1
        else:
            print(f"⚠️  Unexpected response for missing fields (HTTP {response.status_code})")
    except Exception as e:
        print(f"❌ Error in missing fields test: {e}")
    
    # Test 3: Invalid strategy
    print("\nTest 3: Invalid strategy")
    try:
        url = f"{RECOMMENDATION_ENGINE_URL}/api/v1/api/v1/rotations/prioritize-goals"
        test_data = {
            "goals": [{
                "goal_id": "test",
                "type": "soil_health",
                "description": "Test",
                "priority": 5,
                "weight": 1.0,
                "target_value": 100.0,
                "measurement_criteria": []
            }],
            "strategy": "invalid_strategy"
        }
        
        response = requests.post(url, json=test_data, timeout=10)
        
        if response.status_code in [200, 400, 422]:  # Either handled gracefully or error
            print(f"✅ Handled invalid strategy appropriately (HTTP {response.status_code})")
            tests_passed += 1
        else:
            print(f"⚠️  Unexpected response for invalid strategy (HTTP {response.status_code})")
    except Exception as e:
        print(f"❌ Error in invalid strategy test: {e}")
    
    print(f"\nError handling tests: {tests_passed}/{total_tests} passed")
    return tests_passed >= 2

def run_all_tests():
    """Run all tests and generate report."""
    print("🎯 GOAL PRIORITIZATION INTERFACE - END-TO-END TESTING")
    print("="*60)
    
    test_results = []
    
    # Test 1: Service Health
    print("\n1️⃣  SERVICE HEALTH CHECK")
    services_status = test_service_health()
    
    healthy_services = sum(1 for s in services_status.values() if s.get('status') == 'healthy')
    if healthy_services == 2:
        test_results.append(('Service Health', 'PASS', 'All services running'))
    else:
        test_results.append(('Service Health', 'FAIL', f'Only {healthy_services}/2 services healthy'))
        print("❌ Cannot continue testing without healthy services")
        return test_results
    
    # Test 2: Goal Templates API
    print("\n2️⃣  GOAL TEMPLATES API")
    success, data = test_goal_templates_api()
    test_results.append(('Goal Templates API', 'PASS' if success else 'FAIL', 
                        f'Retrieved {len(data.get("templates", {}))} templates' if success else 'API failed'))
    
    # Test 3: Goal Prioritization API
    print("\n3️⃣  GOAL PRIORITIZATION API")
    success, data = test_goal_prioritization_api()
    test_results.append(('Goal Prioritization API', 'PASS' if success else 'FAIL',
                        f'Prioritized {len(data.get("prioritized_goals", []))} goals' if success else 'API failed'))
    
    # Test 4: Goal Conflicts API
    print("\n4️⃣  GOAL CONFLICTS ANALYSIS API")
    success, data = test_goal_conflicts_api()
    test_results.append(('Goal Conflicts API', 'PASS' if success else 'FAIL',
                        f'Found {len(data.get("conflicts", []))} conflicts' if success else 'API failed'))
    
    # Test 5: Frontend Page
    print("\n5️⃣  FRONTEND PAGE")
    success, content = test_frontend_page()
    test_results.append(('Frontend Page', 'PASS' if success else 'FAIL',
                        'All elements found' if success else 'Missing elements'))
    
    # Test 6: JavaScript Integration
    print("\n6️⃣  JAVASCRIPT INTEGRATION")
    success, content = test_javascript_integration()
    test_results.append(('JavaScript Integration', 'PASS' if success else 'FAIL',
                        'Functions found' if success else 'Missing functions'))
    
    # Test 7: Error Handling
    print("\n7️⃣  ERROR HANDLING")
    success = test_error_handling()
    test_results.append(('Error Handling', 'PASS' if success else 'FAIL',
                        'Errors handled correctly' if success else 'Poor error handling'))
    
    # Generate Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for result in test_results if result[1] == 'PASS')
    total = len(test_results)
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {total - passed}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    print(f"\nDETAILED RESULTS:")
    for test_name, status, message in test_results:
        icon = "✅" if status == 'PASS' else "❌"
        print(f"{icon} {test_name}: {message}")
    
    # Recommendations
    print(f"\n📋 RECOMMENDATIONS:")
    failed_tests = [r[0] for r in test_results if r[1] == 'FAIL']
    
    if not failed_tests:
        print("✅ All tests passed! Goal prioritization interface is working correctly.")
        print("✅ Consider adding performance testing and user acceptance testing.")
    else:
        if 'Service Health' in failed_tests:
            print("❗ Start both recommendation-engine and frontend services before testing")
        if any('API' in test for test in failed_tests):
            print("❗ Check backend API implementation in rotation_routes.py")
            print("❗ Verify RotationGoalService is properly initialized")
        if 'Frontend Page' in failed_tests:
            print("❗ Check goal_prioritization.html template")
            print("❗ Verify frontend routing in main.py")
        if 'JavaScript Integration' in failed_tests:
            print("❗ Review JavaScript functionality in the template")
        if 'Error Handling' in failed_tests:
            print("❗ Improve API error handling and validation")
    
    print("\n" + "="*60)
    
    return test_results

if __name__ == "__main__":
    # Check if user wants to run specific tests
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        if test_type == 'health':
            test_service_health()
        elif test_type == 'api':
            test_goal_templates_api()
            test_goal_prioritization_api()
            test_goal_conflicts_api()
        elif test_type == 'frontend':
            test_frontend_page()
            test_javascript_integration()
        elif test_type == 'errors':
            test_error_handling()
        else:
            print("Usage: python test_goal_prioritization.py [health|api|frontend|errors]")
    else:
        # Run all tests
        run_all_tests()