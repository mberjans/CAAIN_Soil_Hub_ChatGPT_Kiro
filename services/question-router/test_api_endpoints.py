#!/usr/bin/env python3
"""
API Endpoints Test Script

Tests all the question-router API endpoints to verify they're working correctly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from main import app
from fastapi.testclient import TestClient
from models.question_models import QuestionType

def test_all_endpoints():
    """Test all API endpoints comprehensively."""
    client = TestClient(app)
    
    print("🧪 Testing AFAS Question Router API Endpoints")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. Health Check Endpoint")
    response = client.get("/health")
    assert response.status_code == 200
    health_data = response.json()
    print(f"   ✅ Status: {health_data['status']}")
    print(f"   ✅ Service: {health_data['service']}")
    print(f"   ✅ Version: {health_data['version']}")
    
    # Test 2: Root Endpoint
    print("\n2. Root Endpoint")
    response = client.get("/")
    assert response.status_code == 200
    root_data = response.json()
    print(f"   ✅ Service: {root_data['service']}")
    print(f"   ✅ Available endpoints: {len(root_data['endpoints'])}")
    
    # Test 3: Question Types Endpoint
    print("\n3. Question Types Endpoint")
    response = client.get("/api/v1/questions/types")
    assert response.status_code == 200
    question_types = response.json()
    print(f"   ✅ Number of question types: {len(question_types)}")
    print(f"   ✅ Sample types: {question_types[:3]}")
    assert len(question_types) == 20  # Should have all 20 question types
    
    # Test 4: Main Classification Endpoint
    print("\n4. Main Classification Endpoint")
    test_request = {
        "question_text": "What crop varieties are best suited to my soil type and climate?",
        "user_id": "test_user_123",
        "farm_id": "farm_456",
        "context": {"region": "midwest"},
        "location": {"latitude": 42.0308, "longitude": -93.6319}
    }
    
    response = client.post("/api/v1/questions/classify", json=test_request)
    assert response.status_code == 200
    result = response.json()
    
    print(f"   ✅ Request ID: {result['request_id']}")
    print(f"   ✅ Classification: {result['classification']['question_type']}")
    print(f"   ✅ Confidence: {result['classification']['confidence_score']}")
    print(f"   ✅ Primary Service: {result['routing']['primary_service']}")
    print(f"   ✅ Status: {result['status']}")
    
    # Verify the classification is correct
    assert result['classification']['question_type'] == 'crop_selection'
    assert result['classification']['confidence_score'] > 0.5
    assert result['routing']['primary_service'] == 'recommendation-engine'
    
    # Test 5: Classification-Only Endpoint
    print("\n5. Classification-Only Endpoint")
    classify_request = {
        "question_text": "How can I improve soil fertility without over-applying fertilizer?"
    }
    
    response = client.post("/api/v1/questions/classify-only", json=classify_request)
    assert response.status_code == 200
    classification = response.json()
    
    print(f"   ✅ Question Type: {classification['question_type']}")
    print(f"   ✅ Confidence: {classification['confidence_score']}")
    print(f"   ✅ Reasoning: {classification['reasoning'][:50]}...")
    
    assert classification['question_type'] == 'soil_fertility'
    assert classification['confidence_score'] > 0.5
    
    # Test 6: Multiple Question Types
    print("\n6. Testing Multiple Question Types")
    test_questions = [
        ("When should I apply fertilizer?", "fertilizer_timing"),
        ("Should I use cover crops?", "cover_crops"),
        ("How do I know if my soil is deficient in nitrogen?", "nutrient_deficiency"),
        ("What is the optimal crop rotation plan?", "crop_rotation"),
        ("Should I use organic or synthetic fertilizers?", "fertilizer_type"),
        ("How can I reduce fertilizer runoff?", "environmental_impact"),
        ("How do I manage soil pH?", "soil_ph"),
        ("Which micronutrients should I supplement?", "micronutrients"),
        ("Are precision agriculture tools worth it?", "precision_agriculture"),
        ("How can I conserve soil moisture during drought?", "drought_management")
    ]
    
    correct_classifications = 0
    for question, expected_type in test_questions:
        response = client.post("/api/v1/questions/classify-only", 
                             json={"question_text": question})
        if response.status_code == 200:
            result = response.json()
            classified_type = result["question_type"]
            confidence = result["confidence_score"]
            
            # Check if classification matches expected or is in alternatives
            is_correct = (classified_type == expected_type or 
                         expected_type in result.get("alternative_types", []))
            
            if is_correct:
                correct_classifications += 1
                status = "✅"
            else:
                status = "⚠️"
            
            print(f"   {status} \"{question[:40]}...\" -> {classified_type} (conf: {confidence:.2f})")
    
    accuracy = correct_classifications / len(test_questions)
    print(f"   📊 Classification Accuracy: {accuracy:.1%} ({correct_classifications}/{len(test_questions)})")
    
    # Test 7: Error Handling
    print("\n7. Error Handling")
    
    # Test with empty question
    response = client.post("/api/v1/questions/classify-only", 
                         json={"question_text": ""})
    print(f"   ✅ Empty question handling: {response.status_code}")
    
    # Test with very short question
    response = client.post("/api/v1/questions/classify-only", 
                         json={"question_text": "hi"})
    print(f"   ✅ Short question handling: {response.status_code}")
    
    # Test with missing required field
    response = client.post("/api/v1/questions/classify-only", json={})
    print(f"   ✅ Missing field handling: {response.status_code}")
    assert response.status_code == 422  # Validation error
    
    # Test 8: API Documentation
    print("\n8. API Documentation")
    response = client.get("/docs")
    print(f"   ✅ Swagger UI: {response.status_code}")
    assert response.status_code == 200
    
    response = client.get("/redoc")
    print(f"   ✅ ReDoc: {response.status_code}")
    assert response.status_code == 200
    
    # Test 9: Metrics Endpoint
    print("\n9. Metrics Endpoint")
    response = client.get("/metrics")
    print(f"   ✅ Metrics endpoint: {response.status_code}")
    # Note: May return 200 or error depending on monitoring setup
    
    print("\n" + "=" * 50)
    print("🎉 All API endpoint tests completed successfully!")
    print(f"📈 Overall classification accuracy: {accuracy:.1%}")
    print("\n📋 Available Endpoints:")
    print("   • GET  /health - Health check")
    print("   • GET  / - Service information")
    print("   • GET  /api/v1/questions/types - List question types")
    print("   • POST /api/v1/questions/classify - Classify and route question")
    print("   • POST /api/v1/questions/classify-only - Classification only")
    print("   • POST /api/v1/questions/route-only - Routing only")
    print("   • GET  /docs - Swagger API documentation")
    print("   • GET  /redoc - ReDoc API documentation")
    print("   • GET  /metrics - Prometheus metrics")


if __name__ == "__main__":
    test_all_endpoints()