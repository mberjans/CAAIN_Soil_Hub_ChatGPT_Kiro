#!/usr/bin/env python3
"""
Demo script for AFAS OpenRouter LLM Integration

This script demonstrates the key features of the OpenRouter integration:
- Question classification
- Agricultural explanations
- Conversational AI
- Streaming responses
- Multiple model support

Usage:
    python demo_openrouter.py
    
Environment variables required:
    OPENROUTER_API_KEY=sk-or-your-api-key-here
"""

import asyncio
import os
import json
from datetime import datetime
from dotenv import load_dotenv

from src.services.openrouter_client import OpenRouterClient, LLMRequest
from src.services.llm_service import LLMService, LLMServiceConfig

load_dotenv()


async def demo_question_classification():
    """Demonstrate question classification capabilities."""
    print("\n" + "="*60)
    print("DEMO: Question Classification")
    print("="*60)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY not set. Skipping demo.")
        return
    
    async with OpenRouterClient(api_key=api_key) as client:
        questions = [
            "What crops should I plant on my farm in Iowa?",
            "How can I improve my soil fertility without over-fertilizing?",
            "When is the best time to apply nitrogen fertilizer to corn?",
            "Should I invest in precision agriculture equipment?",
            "How do I manage soil pH for optimal crop growth?"
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"\n{i}. Question: {question}")
            
            try:
                result = await client.classify_question(question)
                print(f"   Category: {result['category_name']} (#{result['category_number']})")
                print(f"   Confidence: {result['confidence']:.2f}")
            except Exception as e:
                print(f"   ❌ Error: {e}")


async def demo_agricultural_explanation():
    """Demonstrate agricultural explanation generation."""
    print("\n" + "="*60)
    print("DEMO: Agricultural Explanation")
    print("="*60)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY not set. Skipping demo.")
        return
    
    async with OpenRouterClient(api_key=api_key) as client:
        # Sample recommendation from recommendation engine
        recommendation = {
            "type": "nitrogen_fertilizer",
            "rate_lbs_per_acre": 150,
            "application_timing": [
                {"timing": "pre_plant", "rate": 80},
                {"timing": "side_dress_v6", "rate": 70}
            ],
            "fertilizer_source": "anhydrous_ammonia",
            "reasoning": "Based on soil test, yield goal, and previous crop credit"
        }
        
        # Agricultural context
        context = {
            "farm_location": "Central Iowa",
            "soil_data": {
                "ph": 6.2,
                "organic_matter_percent": 3.5,
                "nitrate_n_ppm": 8,
                "phosphorus_ppm": 25,
                "potassium_ppm": 180
            },
            "crop_info": {
                "type": "corn",
                "variety": "Pioneer P1197AM",
                "yield_goal": 180,
                "previous_crop": "soybean"
            },
            "season": "spring_2024"
        }
        
        print("Recommendation to explain:")
        print(json.dumps(recommendation, indent=2))
        print("\nContext:")
        print(json.dumps(context, indent=2))
        
        try:
            explanation = await client.explain_recommendation(recommendation, context)
            print(f"\n📝 AI Explanation:")
            print("-" * 40)
            print(explanation)
        except Exception as e:
            print(f"❌ Error generating explanation: {e}")


async def demo_conversational_ai():
    """Demonstrate conversational AI capabilities."""
    print("\n" + "="*60)
    print("DEMO: Conversational AI")
    print("="*60)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY not set. Skipping demo.")
        return
    
    config = LLMServiceConfig(
        openrouter_api_key=api_key,
        cache_responses=False  # Disable caching for demo
    )
    
    async with LLMService(config) as llm_service:
        user_id = "demo_user"
        session_id = "demo_session"
        
        # Agricultural context for the conversation
        agricultural_context = {
            "farm_location": "Central Iowa",
            "farm_size_acres": 320,
            "primary_crops": ["corn", "soybean"],
            "soil_data": {
                "ph": 6.2,
                "organic_matter_percent": 3.5,
                "phosphorus_ppm": 25,
                "potassium_ppm": 180
            }
        }
        
        conversation = [
            "Hi, I'm a farmer in Iowa with 320 acres. Can you help me with crop planning?",
            "What factors should I consider when choosing between corn and soybean varieties?",
            "My soil pH is 6.2. Is that good for corn production?",
            "What about fertilizer recommendations for this soil?"
        ]
        
        print("Starting conversation with agricultural context:")
        print(json.dumps(agricultural_context, indent=2))
        
        for i, message in enumerate(conversation, 1):
            print(f"\n👨‍🌾 Farmer: {message}")
            
            try:
                response = await llm_service.generate_response(
                    user_id=user_id,
                    session_id=session_id,
                    message=message,
                    agricultural_context=agricultural_context if i == 1 else None,
                    use_case="conversation"
                )
                
                print(f"🤖 AI Assistant: {response.content}")
                print(f"   Model: {response.model}")
                print(f"   Confidence: {response.confidence_score:.2f}")
                print(f"   Cost: ${response.cost_estimate:.4f}")
                print(f"   Time: {response.response_time:.2f}s")
                
                if response.agricultural_metadata:
                    topics = response.agricultural_metadata.get("topics_mentioned", [])
                    if topics:
                        print(f"   Topics: {', '.join(topics[:5])}")
                
            except Exception as e:
                print(f"❌ Error: {e}")


async def demo_streaming_response():
    """Demonstrate streaming response capabilities."""
    print("\n" + "="*60)
    print("DEMO: Streaming Response")
    print("="*60)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY not set. Skipping demo.")
        return
    
    async with OpenRouterClient(api_key=api_key) as client:
        request = LLMRequest(
            messages=[{
                "role": "user",
                "content": "Explain the complete process of soil testing and fertilizer recommendation for corn production, including timing, interpretation, and application strategies."
            }],
            use_case="explanation",
            agricultural_context={
                "crop": "corn",
                "location": "Midwest USA",
                "farm_size": "medium"
            }
        )
        
        print("🔄 Generating streaming response...")
        print("-" * 40)
        
        try:
            full_response = ""
            async for chunk in client.stream_complete(request):
                print(chunk, end="", flush=True)
                full_response += chunk
            
            print(f"\n\n📊 Response Statistics:")
            print(f"   Total characters: {len(full_response)}")
            print(f"   Estimated tokens: {client.estimate_tokens(full_response)}")
            
        except Exception as e:
            print(f"❌ Streaming error: {e}")


async def demo_model_comparison():
    """Demonstrate different models for different use cases."""
    print("\n" + "="*60)
    print("DEMO: Model Comparison")
    print("="*60)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY not set. Skipping demo.")
        return
    
    async with OpenRouterClient(api_key=api_key) as client:
        question = "What is the optimal nitrogen rate for corn in Iowa?"
        
        use_cases = [
            ("classification", "Quick Classification"),
            ("conversation", "Conversational Response"),
            ("explanation", "Detailed Explanation"),
            ("bulk", "Cost-Effective Processing")
        ]
        
        for use_case, description in use_cases:
            print(f"\n🔧 {description} ({use_case}):")
            
            config = client.get_model_config(use_case)
            print(f"   Model: {config['model']}")
            print(f"   Temperature: {config['temperature']}")
            print(f"   Max Tokens: {config['max_tokens']}")
            
            try:
                request = LLMRequest(
                    messages=[{"role": "user", "content": question}],
                    use_case=use_case
                )
                
                start_time = datetime.now()
                response = await client.complete(request)
                end_time = datetime.now()
                
                print(f"   Response Time: {(end_time - start_time).total_seconds():.2f}s")
                print(f"   Cost: ${response.cost_estimate:.4f}")
                print(f"   Confidence: {response.confidence_score:.2f}")
                print(f"   Response Length: {len(response.content)} chars")
                print(f"   Preview: {response.content[:100]}...")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")


async def demo_health_and_monitoring():
    """Demonstrate health check and monitoring capabilities."""
    print("\n" + "="*60)
    print("DEMO: Health Check & Monitoring")
    print("="*60)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY not set. Skipping demo.")
        return
    
    async with OpenRouterClient(api_key=api_key) as client:
        print("🏥 Checking OpenRouter API Health...")
        
        try:
            health = await client.health_check()
            
            print(f"   Status: {'✅ ' + health['status'].upper() if health['status'] == 'healthy' else '❌ ' + health['status'].upper()}")
            print(f"   API Accessible: {'✅ Yes' if health['api_accessible'] else '❌ No'}")
            print(f"   Available Models: {health.get('available_models', 'Unknown')}")
            print(f"   Test Response Time: {health.get('test_response_time', 0):.2f}s")
            
        except Exception as e:
            print(f"❌ Health check failed: {e}")
        
        print("\n🔍 Available Models:")
        try:
            models = await client.get_available_models()
            
            for model in models[:5]:  # Show first 5 models
                print(f"   • {model['id']}")
                print(f"     Name: {model['name']}")
                print(f"     Context: {model['context_length']:,} tokens")
                if model.get('pricing'):
                    pricing = model['pricing']
                    print(f"     Pricing: ${pricing.get('prompt', 'N/A')}/1K input, ${pricing.get('completion', 'N/A')}/1K output")
                print()
            
            if len(models) > 5:
                print(f"   ... and {len(models) - 5} more models")
                
        except Exception as e:
            print(f"❌ Failed to get models: {e}")


async def main():
    """Run all demos."""
    print("🌾 AFAS OpenRouter LLM Integration Demo")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY environment variable not set!")
        print("Please set your OpenRouter API key:")
        print("export OPENROUTER_API_KEY=sk-or-your-api-key-here")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    demos = [
        ("Question Classification", demo_question_classification),
        ("Agricultural Explanation", demo_agricultural_explanation),
        ("Conversational AI", demo_conversational_ai),
        ("Streaming Response", demo_streaming_response),
        ("Model Comparison", demo_model_comparison),
        ("Health & Monitoring", demo_health_and_monitoring)
    ]
    
    for name, demo_func in demos:
        try:
            await demo_func()
        except KeyboardInterrupt:
            print(f"\n⏹️  Demo interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Demo '{name}' failed: {e}")
        
        # Pause between demos
        print("\n" + "-" * 60)
        await asyncio.sleep(1)
    
    print("\n🎉 Demo completed!")
    print("For more information, see the API documentation at /docs")


if __name__ == "__main__":
    asyncio.run(main())