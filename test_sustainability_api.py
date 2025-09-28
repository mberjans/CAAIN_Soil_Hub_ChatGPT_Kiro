#!/usr/bin/env python3
"""
Integration test script for the sustainability-score endpoint.
"""

import requests
import json
import sys

def test_sustainability_api_endpoint():
    """Test the sustainability API endpoint with different scenarios."""
    
    # Base URL - adjust this based on your actual service configuration
    base_url = "http://localhost:8000/api/v1/rotations"
    
    print("Testing Sustainability Score API Endpoint...")
    print(f"Base URL: {base_url}")
    
    # Test cases
    test_cases = [
        {
            "name": "Diverse 4-crop rotation",
            "field_id": "field_001",
            "rotation_sequence": ["corn", "soybean", "wheat", "oats"],
            "expected_grade_range": ["C", "D", "B"]  # Possible grades
        },
        {
            "name": "Sustainable rotation with legumes",
            "field_id": "field_002", 
            "rotation_sequence": ["corn", "soybean", "alfalfa", "wheat"],
            "expected_grade_range": ["B", "C", "A"]
        },
        {
            "name": "Simple corn-soybean rotation",
            "field_id": "field_003",
            "rotation_sequence": ["corn", "soybean"],
            "expected_grade_range": ["C", "D", "B"]
        },
        {
            "name": "High diversity rotation",
            "field_id": "field_004",
            "rotation_sequence": ["corn", "soybean", "wheat", "oats", "alfalfa", "barley"],
            "expected_grade_range": ["A", "B", "C"]
        }
    ]
    
    print(f"\n📋 Running {len(test_cases)} test cases...\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['name']}")
        print(f"  Field ID: {test_case['field_id']}")
        print(f"  Rotation: {test_case['rotation_sequence']}")
        
        # Prepare request parameters
        params = {
            "field_id": test_case["field_id"],
            "rotation_sequence": test_case["rotation_sequence"]
        }
        
        try:
            # Make API request
            response = requests.post(
                f"{base_url}/sustainability-score",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = [
                    "field_id", "rotation_sequence", "sustainability_scores",
                    "overall_sustainability_score", "sustainability_grade", "recommendations"
                ]
                
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    print(f"  ❌ Missing fields: {missing_fields}")
                    continue
                
                # Extract key results
                overall_score = data["overall_sustainability_score"]
                grade = data["sustainability_grade"]
                recommendations_count = len(data.get("recommendations", []))
                
                print(f"  ✅ Success: Score={overall_score:.1f}, Grade={grade}, Recommendations={recommendations_count}")
                
                # Validate score components
                scores = data["sustainability_scores"]
                score_components = [
                    "environmental_impact", "soil_health", "carbon_sequestration",
                    "water_efficiency", "biodiversity", "long_term_viability"
                ]
                
                all_scores_valid = all(
                    component in scores and 0 <= scores[component] <= 100
                    for component in score_components
                )
                
                if all_scores_valid:
                    print(f"  ✅ All sustainability scores within valid range (0-100)")
                else:
                    print(f"  ⚠️  Some scores may be out of range")
                
                # Show top sustainability metrics
                top_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
                print(f"  📊 Top metrics: {', '.join([f'{k}={v:.1f}' for k, v in top_scores])}")
                
                # Show sample recommendations
                if data.get("recommendations"):
                    print(f"  💡 Sample recommendation: {data['recommendations'][0]}")
                
            else:
                print(f"  ❌ API Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"  ⚠️  Connection failed - service may not be running")
            print(f"     To test: Start the recommendation engine service first")
            
        except requests.exceptions.Timeout:
            print(f"  ⚠️  Request timeout - service may be slow")
            
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")
        
        print()  # Empty line between tests
    
    print("🏁 Test completed!")
    print("\n📚 API Usage Examples:")
    print("  POST /api/v1/rotations/sustainability-score")
    print("  Parameters:")
    print("    - field_id: string (required)")
    print("    - rotation_sequence: array of strings (required)")
    print("\n  Example curl command:")
    print('  curl -X POST "http://localhost:8000/api/v1/rotations/sustainability-score" \\')
    print('       -G -d "field_id=field_001" \\')
    print('       -d "rotation_sequence=corn" \\')
    print('       -d "rotation_sequence=soybean" \\')
    print('       -d "rotation_sequence=wheat"')

if __name__ == "__main__":
    test_sustainability_api_endpoint()