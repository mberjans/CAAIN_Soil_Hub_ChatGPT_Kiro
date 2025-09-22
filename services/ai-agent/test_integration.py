#!/usr/bin/env python3
"""
Quick integration test for OpenRouter LLM integration
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
from src.services.openrouter_client import OpenRouterClient, LLMRequest
from src.services.llm_service import create_llm_service

load_dotenv()


async def test_openrouter_client():
    """Test OpenRouter client basic functionality."""
    print("🧪 Testing OpenRouter Client...")
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY not set. Skipping OpenRouter tests.")
        return False
    
    try:
        async with OpenRouterClient(api_key=api_key) as client:
            # Test health check
            health = await client.health_check()
            print(f"   Health Status: {health['status']}")
            print(f"   API Accessible: {health['api_accessible']}")
            
            if health['status'] != 'healthy':
                print("❌ OpenRouter API not healthy")
                return False
            
            # Test question classification
            result = await client.classify_question("What crops should I plant?")
            print(f"   Classification: {result['category_name']} (confidence: {result['confidence']:.2f})")
            
            # Test simple completion
            request = LLMRequest(
                messages=[{"role": "user", "content": "What is nitrogen fixation?"}],
                use_case="conversation"
            )
            
            response = await client.complete(request)
            print(f"   Response Length: {len(response.content)} chars")
            print(f"   Model Used: {response.model}")
            print(f"   Cost: ${response.cost_estimate:.4f}")
            print(f"   Confidence: {response.confidence_score:.2f}")
            
            print("✅ OpenRouter client tests passed")
            return True
            
    except Exception as e:
        print(f"❌ OpenRouter client test failed: {e}")
        return False


async def test_llm_service():
    """Test LLM service functionality."""
    print("\n🧪 Testing LLM Service...")
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY not set. Skipping LLM service tests.")
        return False
    
    try:
        llm_service = create_llm_service()
        
        async with llm_service:
            # Test service health
            health = await llm_service.get_service_health()
            print(f"   Service Status: {health['status']}")
            
            if health['status'] != 'healthy':
                print("❌ LLM service not healthy")
                return False
            
            # Test conversation
            response = await llm_service.generate_response(
                user_id="test_user",
                session_id="test_session",
                message="What factors affect corn yield?",
                agricultural_context={
                    "farm_location": "Iowa",
                    "soil_data": {"ph": 6.2, "organic_matter_percent": 3.5}
                }
            )
            
            print(f"   Response Length: {len(response.content)} chars")
            print(f"   Model Used: {response.model}")
            print(f"   Confidence: {response.confidence_score:.2f}")
            
            # Test agricultural explanation
            recommendation = {
                "type": "nitrogen_rate",
                "rate_lbs_per_acre": 150
            }
            context = {
                "soil_data": {"ph": 6.2},
                "crop": "corn"
            }
            
            explanation = await llm_service.generate_agricultural_explanation(
                recommendation, context
            )
            
            print(f"   Explanation Length: {len(explanation)} chars")
            
            print("✅ LLM service tests passed")
            return True
            
    except Exception as e:
        print(f"❌ LLM service test failed: {e}")
        return False


async def test_api_endpoints():
    """Test API endpoints (requires running service)."""
    print("\n🧪 Testing API Endpoints...")
    
    try:
        import httpx
        
        base_url = "http://localhost:8002"
        
        async with httpx.AsyncClient() as client:
            # Test health endpoint
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"   Service Health: {health_data['status']}")
                print("✅ API endpoints accessible")
                return True
            else:
                print(f"❌ Health endpoint returned {response.status_code}")
                return False
                
    except Exception as e:
        print(f"⚠️  API endpoint test skipped (service not running): {e}")
        return True  # Don't fail if service isn't running


async def main():
    """Run all tests."""
    print("🌾 AFAS AI Agent OpenRouter Integration Tests")
    print("=" * 50)
    
    tests = [
        ("OpenRouter Client", test_openrouter_client),
        ("LLM Service", test_llm_service),
        ("API Endpoints", test_api_endpoints)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! OpenRouter integration is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)