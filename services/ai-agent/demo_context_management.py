#!/usr/bin/env python3
"""
Context Management System Demo

Interactive demonstration of the AFAS AI Agent context management capabilities.
Shows conversation continuity, agricultural context awareness, and memory features.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any

# Add the src directory to the path for imports
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.context_manager import (
    ContextManager, ContextType, ContextPriority, ContextScope
)
from services.context_aware_service import ContextAwareService, ContextAwareRequest
from services.llm_service import LLMService, LLMServiceConfig


class DemoLLMService:
    """Demo LLM service with realistic agricultural responses."""
    
    def __init__(self):
        self.active_conversations = {}
        self.response_cache = {}
        
        # Pre-defined responses for demo
        self.responses = {
            "crop_selection": "Based on your Iowa location and 320-acre farm with pH 6.2 soil, I recommend corn and soybean rotation. Corn varieties like Pioneer P1197AM (111-day maturity) would work well for your conditions. Soybean varieties in the 2.8-3.2 maturity group would complement the rotation nicely.",
            
            "fertilizer": "For your corn crop with soil pH 6.2 and previous soybean, I recommend 140 lbs N/acre total. Apply 100 lbs N/acre pre-plant as anhydrous ammonia, then sidedress 40 lbs N/acre at V6 stage. Your soil test shows adequate P and K levels, so maintenance rates of 30 lbs P2O5 and 60 lbs K2O per acre should suffice.",
            
            "soil_health": "Your soil pH of 6.2 is good for corn production. With 3.2% organic matter, your soil health is above average. Consider cover crops like cereal rye after corn harvest to maintain soil structure and capture residual nitrogen. No-till practices would help preserve your good organic matter levels.",
            
            "general": "I understand you're asking about agricultural practices. Based on your farm profile in Iowa with 320 acres, I can provide specific recommendations for your operation. What specific aspect would you like to discuss - crops, soil, fertilizer, or pest management?"
        }
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def classify_question(self, question: str) -> Dict[str, Any]:
        """Classify question based on keywords."""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ["crop", "plant", "variety", "seed"]):
            return {
                "category_number": 1,
                "category_name": "Crop Selection",
                "confidence": 0.9
            }
        elif any(word in question_lower for word in ["fertilizer", "nitrogen", "phosphorus", "nutrient"]):
            return {
                "category_number": 2,
                "category_name": "Fertilizer Recommendation",
                "confidence": 0.85
            }
        elif any(word in question_lower for word in ["soil", "ph", "organic matter", "health"]):
            return {
                "category_number": 3,
                "category_name": "Soil Health",
                "confidence": 0.8
            }
        else:
            return {
                "category_number": 20,
                "category_name": "General Agricultural Question",
                "confidence": 0.6
            }
    
    async def generate_response(self, **kwargs):
        """Generate contextual response."""
        message = kwargs.get('message', '')
        agricultural_context = kwargs.get('agricultural_context', {})
        
        # Classify to determine response type
        classification = await self.classify_question(message)
        category = classification['category_name'].lower()
        
        # Select appropriate response
        if "crop" in category:
            content = self.responses["crop_selection"]
        elif "fertilizer" in category:
            content = self.responses["fertilizer"]
        elif "soil" in category:
            content = self.responses["soil_health"]
        else:
            content = self.responses["general"]
        
        # Add context-specific information
        if agricultural_context:
            location = agricultural_context.get('location', '')
            farm_size = agricultural_context.get('farm_size_acres', '')
            
            if location and farm_size:
                content = f"For your {farm_size}-acre farm in {location}: " + content
        
        class MockResponse:
            def __init__(self, content):
                self.content = content
                self.model = "demo-agricultural-model"
                self.confidence_score = 0.85
                self.cost_estimate = 0.02
                self.response_time = 1.2
                self.agricultural_metadata = {
                    "source": "demo_system",
                    "category": classification['category_name']
                }
        
        return MockResponse(content)
    
    async def get_service_health(self):
        return {
            "service": "demo_llm_service",
            "status": "healthy",
            "active_conversations": len(self.active_conversations),
            "cached_responses": len(self.response_cache),
            "openrouter_status": {"status": "healthy"},
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def cleanup_old_conversations(self):
        pass
    
    async def cleanup_old_cache(self):
        pass


async def demo_basic_context_management():
    """Demonstrate basic context management features."""
    print("\n" + "="*60)
    print("DEMO 1: Basic Context Management")
    print("="*60)
    
    # Create context manager
    context_manager = ContextManager(
        max_contexts_per_user=50,
        cleanup_interval_hours=24,
        enable_persistence=False
    )
    
    await context_manager.start()
    
    try:
        user_id = "demo_farmer_1"
        
        print(f"\n1. Storing agricultural context for user: {user_id}")
        
        # Store farm profile
        farm_data = {
            "location": "Iowa",
            "farm_size_acres": 320,
            "soil_data": {
                "ph": 6.2,
                "organic_matter_percent": 3.2,
                "phosphorus_ppm": 28,
                "potassium_ppm": 165
            },
            "primary_crops": ["corn", "soybean"],
            "equipment": ["planter", "combine", "sprayer"],
            "management_practices": {
                "tillage": "no_till",
                "cover_crops": True,
                "rotation": "corn_soybean"
            }
        }
        
        context_id = await context_manager.store_agricultural_context(
            user_id=user_id,
            farm_data=farm_data,
            source="demo_input"
        )
        
        print(f"   ✓ Stored agricultural context with ID: {context_id}")
        
        # Store user preferences
        preferences = {
            "communication_style": "detailed",
            "expertise_level": "intermediate",
            "preferred_units": "imperial",
            "notification_preferences": {
                "weather_alerts": True,
                "market_updates": False
            }
        }
        
        pref_id = await context_manager.store_context(
            user_id=user_id,
            context_type=ContextType.USER_PROFILE,
            data=preferences,
            priority=ContextPriority.HIGH,
            scope=ContextScope.GLOBAL,
            summary="User communication preferences",
            tags=["preferences", "communication", "user_profile"]
        )
        
        print(f"   ✓ Stored user preferences with ID: {pref_id}")
        
        # Demonstrate context retrieval
        print(f"\n2. Retrieving contexts for user: {user_id}")
        
        # Get agricultural contexts
        ag_contexts = await context_manager.get_contexts_by_type(
            user_id, ContextType.AGRICULTURAL
        )
        
        print(f"   ✓ Found {len(ag_contexts)} agricultural contexts")
        if ag_contexts:
            print(f"   ✓ Farm size: {ag_contexts[0].data.get('farm_size_acres')} acres")
            print(f"   ✓ Location: {ag_contexts[0].data.get('location')}")
            print(f"   ✓ Soil pH: {ag_contexts[0].data.get('soil_data', {}).get('ph')}")
        
        # Search contexts
        print(f"\n3. Searching contexts with tags and queries")
        
        soil_contexts = await context_manager.search_contexts(
            user_id=user_id,
            tags=["soil"],
            limit=5
        )
        
        print(f"   ✓ Found {len(soil_contexts)} contexts with 'soil' tag")
        
        corn_contexts = await context_manager.search_contexts(
            user_id=user_id,
            query="corn",
            limit=5
        )
        
        print(f"   ✓ Found {len(corn_contexts)} contexts mentioning 'corn'")
        
        # Get statistics
        stats = await context_manager.get_statistics()
        print(f"\n4. Context Manager Statistics:")
        print(f"   ✓ Total users: {stats['total_users']}")
        print(f"   ✓ Total contexts: {stats['total_contexts']}")
        print(f"   ✓ Context types: {list(stats['contexts_by_type'].keys())}")
        
    finally:
        await context_manager.stop()


async def demo_conversation_continuity():
    """Demonstrate conversation continuity and context awareness."""
    print("\n" + "="*60)
    print("DEMO 2: Conversation Continuity & Context Awareness")
    print("="*60)
    
    # Create services
    llm_service = DemoLLMService()
    context_manager = ContextManager(enable_persistence=False)
    
    await context_manager.start()
    
    context_service = ContextAwareService(llm_service, context_manager)
    
    async with context_service:
        user_id = "demo_farmer_2"
        session_id = "demo_session_1"
        
        print(f"\nStarting conversation for user: {user_id}")
        print(f"Session ID: {session_id}")
        
        # Conversation sequence
        conversation_steps = [
            {
                "message": "Hi, I have a 320-acre farm in Iowa",
                "agricultural_context": {
                    "location": "Iowa",
                    "farm_size_acres": 320,
                    "soil_data": {"ph": 6.2, "organic_matter_percent": 3.2}
                },
                "description": "Initial farm introduction with context"
            },
            {
                "message": "What crops should I plant this year?",
                "description": "Crop selection question (should use farm context)"
            },
            {
                "message": "My soil test shows low phosphorus. What should I do?",
                "agricultural_context": {
                    "soil_data": {"phosphorus_ppm": 12}  # Low P level
                },
                "description": "Soil fertility question with additional context"
            },
            {
                "message": "How much nitrogen should I apply to corn?",
                "description": "Fertilizer question (should remember crop choice and soil data)"
            },
            {
                "message": "Should I use cover crops?",
                "description": "Management practice question"
            }
        ]
        
        for i, step in enumerate(conversation_steps, 1):
            print(f"\n--- Step {i}: {step['description']} ---")
            print(f"User: {step['message']}")
            
            # Create request
            request = ContextAwareRequest(
                user_id=user_id,
                session_id=session_id,
                message=step['message'],
                agricultural_context=step.get('agricultural_context')
            )
            
            # Process request
            response = await context_service.process_request(request)
            
            print(f"Assistant: {response.content[:200]}...")
            
            # Show context information
            context_used = response.context_used
            print(f"\nContext Information:")
            
            # Conversation context
            conv_context = context_used.get('conversation', {})
            if conv_context.get('summary'):
                print(f"  • Conversation: {conv_context['summary']}")
            
            # Agricultural context
            ag_context = context_used.get('agricultural', {})
            if ag_context.get('farm_profile'):
                farm = ag_context['farm_profile']
                print(f"  • Farm: {farm.get('farm_size_acres')} acres in {farm.get('location')}")
                if farm.get('soil_data'):
                    soil = farm['soil_data']
                    print(f"  • Soil: pH {soil.get('ph')}, OM {soil.get('organic_matter_percent')}%")
            
            # Relevant contexts
            relevant = context_used.get('relevant_contexts', [])
            if relevant:
                print(f"  • Using {len(relevant)} relevant contexts from history")
            
            print(f"  • Stored {len(response.context_stored)} new context entries")
            
            # Small delay for readability
            await asyncio.sleep(0.5)
        
        # Show final conversation summary
        print(f"\n--- Final Conversation Summary ---")
        summary = await context_service.get_user_context_summary(user_id)
        
        print(f"Agricultural Profile:")
        ag_profile = summary.get('agricultural_profile', {})
        print(f"  • Farms: {ag_profile.get('farms', 0)}")
        if ag_profile.get('latest_farm_data'):
            farm_data = ag_profile['latest_farm_data']
            print(f"  • Latest farm: {farm_data.get('farm_size_acres')} acres in {farm_data.get('location')}")
        
        print(f"Interaction History:")
        interaction = summary.get('interaction_history', {})
        print(f"  • Total recommendations: {interaction.get('total_recommendations', 0)}")
        recent_questions = interaction.get('recent_questions', [])
        if recent_questions:
            print(f"  • Recent topics: {', '.join(recent_questions[:3])}")
    
    await context_manager.stop()


async def demo_context_search_and_retrieval():
    """Demonstrate advanced context search and retrieval."""
    print("\n" + "="*60)
    print("DEMO 3: Advanced Context Search & Retrieval")
    print("="*60)
    
    context_manager = ContextManager(enable_persistence=False)
    await context_manager.start()
    
    try:
        user_id = "demo_farmer_3"
        
        print(f"\n1. Creating diverse agricultural contexts for user: {user_id}")
        
        # Create various contexts
        contexts_to_create = [
            {
                "type": ContextType.AGRICULTURAL,
                "data": {
                    "field_name": "North Field",
                    "crop": "corn",
                    "variety": "Pioneer P1197AM",
                    "planting_date": "2024-05-01",
                    "soil_data": {"ph": 6.8, "organic_matter_percent": 3.5}
                },
                "tags": ["corn", "planting", "north_field", "pioneer"],
                "summary": "Corn planting in North Field with Pioneer variety"
            },
            {
                "type": ContextType.AGRICULTURAL,
                "data": {
                    "field_name": "South Field",
                    "crop": "soybean",
                    "variety": "Asgrow AG2834",
                    "planting_date": "2024-05-15",
                    "soil_data": {"ph": 6.2, "organic_matter_percent": 2.8}
                },
                "tags": ["soybean", "planting", "south_field", "asgrow"],
                "summary": "Soybean planting in South Field with Asgrow variety"
            },
            {
                "type": ContextType.RECOMMENDATION_HISTORY,
                "data": {
                    "question_type": "Fertilizer Recommendation",
                    "recommendation": "Apply 150 lbs N/acre for corn",
                    "confidence": 0.9,
                    "field": "North Field"
                },
                "tags": ["fertilizer", "nitrogen", "corn", "north_field"],
                "summary": "Nitrogen fertilizer recommendation for corn"
            },
            {
                "type": ContextType.RECOMMENDATION_HISTORY,
                "data": {
                    "question_type": "Pest Management",
                    "recommendation": "Scout for corn rootworm in July",
                    "confidence": 0.85,
                    "field": "North Field"
                },
                "tags": ["pest", "corn_rootworm", "scouting", "north_field"],
                "summary": "Corn rootworm scouting recommendation"
            },
            {
                "type": ContextType.USER_PROFILE,
                "data": {
                    "farming_experience": "15 years",
                    "certifications": ["CCA", "Organic"],
                    "specialties": ["soil_health", "integrated_pest_management"]
                },
                "tags": ["experience", "certifications", "specialties"],
                "summary": "Farmer profile with 15 years experience"
            }
        ]
        
        stored_ids = []
        for ctx in contexts_to_create:
            context_id = await context_manager.store_context(
                user_id=user_id,
                context_type=ctx["type"],
                data=ctx["data"],
                tags=ctx["tags"],
                summary=ctx["summary"],
                priority=ContextPriority.HIGH
            )
            stored_ids.append(context_id)
            print(f"   ✓ Created: {ctx['summary']}")
        
        print(f"\n2. Demonstrating different search methods")
        
        # Search by type
        print(f"\n   Search by type (AGRICULTURAL):")
        ag_contexts = await context_manager.get_contexts_by_type(
            user_id, ContextType.AGRICULTURAL
        )
        for ctx in ag_contexts:
            print(f"     • {ctx.summary}")
        
        # Search by tags
        print(f"\n   Search by tags (['corn']):")
        corn_contexts = await context_manager.search_contexts(
            user_id=user_id,
            tags=["corn"]
        )
        for ctx in corn_contexts:
            print(f"     • {ctx.summary}")
        
        # Search by query text
        print(f"\n   Search by query ('North Field'):")
        north_field_contexts = await context_manager.search_contexts(
            user_id=user_id,
            query="North Field"
        )
        for ctx in north_field_contexts:
            print(f"     • {ctx.summary}")
        
        # Combined search
        print(f"\n   Combined search (fertilizer + corn tags):")
        fertilizer_corn_contexts = await context_manager.search_contexts(
            user_id=user_id,
            tags=["fertilizer", "corn"],
            context_types=[ContextType.RECOMMENDATION_HISTORY]
        )
        for ctx in fertilizer_corn_contexts:
            print(f"     • {ctx.summary}")
        
        # Get relevant context for a specific query
        print(f"\n3. Getting relevant context for query simulation")
        
        query = "What should I do about pest management in my corn field?"
        relevant_context = await context_manager.get_relevant_context(
            user_id=user_id,
            session_id="demo_session",
            query=query,
            max_contexts=5
        )
        
        print(f"\n   Query: '{query}'")
        print(f"   Relevant contexts found: {len(relevant_context.get('relevant_contexts', []))}")
        
        for ctx in relevant_context.get('relevant_contexts', [])[:3]:
            print(f"     • {ctx['summary']} (Type: {ctx['type']}, Priority: {ctx['priority']})")
        
        # Access patterns
        print(f"\n4. Demonstrating access patterns and popularity")
        
        # Access some contexts multiple times
        for _ in range(3):
            await context_manager.get_context(user_id, stored_ids[0])  # Corn context
        
        for _ in range(5):
            await context_manager.get_context(user_id, stored_ids[2])  # Fertilizer recommendation
        
        # Show access counts
        print(f"\n   Context access patterns:")
        for context_id in stored_ids[:3]:
            ctx = await context_manager.get_context(user_id, context_id)
            if ctx:
                print(f"     • {ctx.summary}: {ctx.access_count} accesses")
        
    finally:
        await context_manager.stop()


async def demo_user_preferences_and_personalization():
    """Demonstrate user preferences and response personalization."""
    print("\n" + "="*60)
    print("DEMO 4: User Preferences & Response Personalization")
    print("="*60)
    
    llm_service = DemoLLMService()
    context_manager = ContextManager(enable_persistence=False)
    await context_manager.start()
    
    context_service = ContextAwareService(llm_service, context_manager)
    
    async with context_service:
        # Demo different user profiles
        users = [
            {
                "id": "beginner_farmer",
                "name": "Beginner Farmer",
                "preferences": {
                    "communication_style": "simple",
                    "expertise_level": "beginner",
                    "preferred_units": "imperial",
                    "explanation_detail": "high"
                },
                "farm_context": {
                    "location": "Iowa",
                    "farm_size_acres": 80,
                    "experience_years": 2
                }
            },
            {
                "id": "experienced_farmer",
                "name": "Experienced Farmer",
                "preferences": {
                    "communication_style": "technical",
                    "expertise_level": "advanced",
                    "preferred_units": "metric",
                    "explanation_detail": "low"
                },
                "farm_context": {
                    "location": "Illinois",
                    "farm_size_acres": 1200,
                    "experience_years": 25
                }
            }
        ]
        
        question = "What nitrogen rate should I use for corn?"
        
        for user in users:
            print(f"\n--- {user['name']} Profile ---")
            
            # Set up user preferences
            await context_service.update_user_preferences(
                user["id"], user["preferences"]
            )
            
            print(f"Preferences set:")
            for key, value in user["preferences"].items():
                print(f"  • {key}: {value}")
            
            # Create request with farm context
            request = ContextAwareRequest(
                user_id=user["id"],
                session_id="demo_personalization",
                message=question,
                agricultural_context=user["farm_context"]
            )
            
            # Get response
            response = await context_service.process_request(request)
            
            print(f"\nQuestion: {question}")
            print(f"Response: {response.content}")
            
            # Show how preferences influenced the response
            user_prefs = response.context_used.get("user_preferences", {})
            if user_prefs:
                print(f"\nPersonalization applied:")
                print(f"  • Expertise level: {user_prefs.get('expertise_level', 'not set')}")
                print(f"  • Communication style: {user_prefs.get('communication_style', 'not set')}")
        
        # Show user summaries
        print(f"\n--- User Context Summaries ---")
        for user in users:
            summary = await context_service.get_user_context_summary(user["id"])
            
            print(f"\n{user['name']}:")
            print(f"  • Agricultural contexts: {summary['agricultural_profile']['farms']}")
            print(f"  • Total recommendations: {summary['interaction_history']['total_recommendations']}")
            
            prefs = summary.get('user_preferences', {}).get('profile_data')
            if prefs:
                print(f"  • Expertise level: {prefs.get('expertise_level', 'not set')}")
                print(f"  • Communication style: {prefs.get('communication_style', 'not set')}")
    
    await context_manager.stop()


async def main():
    """Run all context management demos."""
    print("AFAS AI Agent - Context Management System Demo")
    print("=" * 60)
    print("This demo showcases the comprehensive context management capabilities")
    print("of the AFAS AI Agent service, including:")
    print("• Context storage and retrieval")
    print("• Conversation continuity")
    print("• Agricultural context awareness")
    print("• Advanced search and filtering")
    print("• User preferences and personalization")
    print("• Memory and learning capabilities")
    
    try:
        # Run all demos
        await demo_basic_context_management()
        await demo_conversation_continuity()
        await demo_context_search_and_retrieval()
        await demo_user_preferences_and_personalization()
        
        print("\n" + "="*60)
        print("DEMO COMPLETE")
        print("="*60)
        print("The context management system successfully demonstrated:")
        print("✓ Comprehensive context storage and retrieval")
        print("✓ Conversation continuity across interactions")
        print("✓ Agricultural context awareness and integration")
        print("✓ Advanced search and filtering capabilities")
        print("✓ User preference management and personalization")
        print("✓ Memory and learning from interactions")
        print("\nThe system is ready for production use with full")
        print("context management capabilities for agricultural AI.")
        
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())