"""
Tests for Context Management System

Comprehensive tests for context manager, context-aware service,
and context integration with LLM service.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any
import json

from src.services.context_manager import (
    ContextManager, ContextEntry, ConversationContext,
    ContextType, ContextPriority, ContextScope
)
from src.services.context_aware_service import (
    ContextAwareService, ContextAwareRequest, create_context_aware_service
)
from src.services.llm_service import LLMService, LLMServiceConfig


class MockLLMService:
    """Mock LLM service for testing."""
    
    def __init__(self):
        self.active_conversations = {}
        self.response_cache = {}
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
    
    async def classify_question(self, question: str) -> Dict[str, Any]:
        """Mock question classification."""
        return {
            "category_number": 1,
            "category_name": "Crop Selection",
            "confidence": 0.85
        }
    
    async def generate_response(self, **kwargs):
        """Mock response generation."""
        class MockResponse:
            def __init__(self):
                self.content = "Mock agricultural response"
                self.model = "mock-model"
                self.confidence_score = 0.8
                self.cost_estimate = 0.01
                self.response_time = 1.5
                self.agricultural_metadata = {"source": "mock"}
        
        return MockResponse()
    
    async def get_service_health(self):
        """Mock health check."""
        return {
            "service": "mock_llm_service",
            "status": "healthy",
            "active_conversations": 0,
            "cached_responses": 0,
            "openrouter_status": {"status": "healthy"},
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def cleanup_old_conversations(self):
        """Mock cleanup."""
        pass
    
    async def cleanup_old_cache(self):
        """Mock cleanup."""
        pass


@pytest.fixture
async def context_manager():
    """Create context manager for testing."""
    manager = ContextManager(
        max_contexts_per_user=100,
        cleanup_interval_hours=1,
        enable_persistence=False
    )
    await manager.start()
    yield manager
    await manager.stop()


@pytest.fixture
async def mock_llm_service():
    """Create mock LLM service."""
    service = MockLLMService()
    async with service:
        yield service


@pytest.fixture
async def context_aware_service(mock_llm_service, context_manager):
    """Create context-aware service for testing."""
    service = ContextAwareService(mock_llm_service, context_manager)
    async with service:
        yield service


class TestContextManager:
    """Test context manager functionality."""
    
    @pytest.mark.asyncio
    async def test_store_and_retrieve_context(self, context_manager):
        """Test basic context storage and retrieval."""
        user_id = "test_user_1"
        test_data = {"farm_size": 320, "location": "Iowa"}
        
        # Store context
        context_id = await context_manager.store_context(
            user_id=user_id,
            context_type=ContextType.AGRICULTURAL,
            data=test_data,
            priority=ContextPriority.HIGH,
            summary="Test farm data"
        )
        
        assert context_id is not None
        
        # Retrieve context
        entry = await context_manager.get_context(user_id, context_id)
        
        assert entry is not None
        assert entry.data == test_data
        assert entry.context_type == ContextType.AGRICULTURAL
        assert entry.priority == ContextPriority.HIGH
        assert entry.access_count == 1
    
    @pytest.mark.asyncio
    async def test_context_expiration(self, context_manager):
        """Test context expiration handling."""
        user_id = "test_user_2"
        
        # Store context with immediate expiration
        context_id = await context_manager.store_context(
            user_id=user_id,
            context_type=ContextType.TEMPORARY,
            data={"test": "data"},
            expires_at=datetime.utcnow() - timedelta(seconds=1)  # Already expired
        )
        
        # Try to retrieve expired context
        entry = await context_manager.get_context(user_id, context_id)
        
        assert entry is None  # Should be None due to expiration
    
    @pytest.mark.asyncio
    async def test_get_contexts_by_type(self, context_manager):
        """Test retrieving contexts by type."""
        user_id = "test_user_3"
        
        # Store multiple contexts of different types
        await context_manager.store_context(
            user_id=user_id,
            context_type=ContextType.AGRICULTURAL,
            data={"farm": "data1"}
        )
        
        await context_manager.store_context(
            user_id=user_id,
            context_type=ContextType.AGRICULTURAL,
            data={"farm": "data2"}
        )
        
        await context_manager.store_context(
            user_id=user_id,
            context_type=ContextType.USER_PROFILE,
            data={"profile": "data"}
        )
        
        # Get agricultural contexts
        agricultural_contexts = await context_manager.get_contexts_by_type(
            user_id, ContextType.AGRICULTURAL
        )
        
        assert len(agricultural_contexts) == 2
        assert all(ctx.context_type == ContextType.AGRICULTURAL for ctx in agricultural_contexts)
    
    @pytest.mark.asyncio
    async def test_search_contexts(self, context_manager):
        """Test context search functionality."""
        user_id = "test_user_4"
        
        # Store contexts with different tags and content
        await context_manager.store_context(
            user_id=user_id,
            context_type=ContextType.AGRICULTURAL,
            data={"crop": "corn", "soil_ph": 6.2},
            tags=["corn", "soil", "ph"],
            summary="Corn farming with soil pH 6.2"
        )
        
        await context_manager.store_context(
            user_id=user_id,
            context_type=ContextType.AGRICULTURAL,
            data={"crop": "soybean", "fertilizer": "nitrogen"},
            tags=["soybean", "fertilizer", "nitrogen"],
            summary="Soybean nitrogen fertilizer application"
        )
        
        # Search by tag
        corn_contexts = await context_manager.search_contexts(
            user_id=user_id,
            tags=["corn"]
        )
        
        assert len(corn_contexts) == 1
        assert "corn" in corn_contexts[0].tags
        
        # Search by query text
        soil_contexts = await context_manager.search_contexts(
            user_id=user_id,
            query="soil"
        )
        
        assert len(soil_contexts) == 1
        assert "soil" in soil_contexts[0].summary.lower()
    
    @pytest.mark.asyncio
    async def test_conversation_context(self, context_manager):
        """Test conversation context management."""
        user_id = "test_user_5"
        session_id = "session_123"
        
        # Get conversation context (should create new)
        context = await context_manager.get_conversation_context(user_id, session_id)
        
        assert context.user_id == user_id
        assert context.session_id == session_id
        assert len(context.messages) == 0
        
        # Add messages
        context.add_message("user", "What crops should I plant?")
        context.add_message("assistant", "Consider corn and soybean for your region.")
        
        assert len(context.messages) == 2
        assert context.total_interactions == 2
        
        # Get same context again (should return existing)
        same_context = await context_manager.get_conversation_context(user_id, session_id)
        
        assert same_context.conversation_id == context.conversation_id
        assert len(same_context.messages) == 2
    
    @pytest.mark.asyncio
    async def test_agricultural_context_storage(self, context_manager):
        """Test agricultural context storage helper."""
        user_id = "test_user_6"
        
        farm_data = {
            "location": "Iowa",
            "farm_size_acres": 320,
            "soil_data": {"ph": 6.2, "organic_matter_percent": 3.5},
            "primary_crops": ["corn", "soybean"],
            "equipment": ["planter", "combine"]
        }
        
        context_id = await context_manager.store_agricultural_context(
            user_id=user_id,
            farm_data=farm_data,
            source="test_input"
        )
        
        # Retrieve and verify
        entry = await context_manager.get_context(user_id, context_id)
        
        assert entry is not None
        assert entry.context_type == ContextType.AGRICULTURAL
        assert entry.data == farm_data
        assert "agricultural" in entry.tags
        assert "farm_data" in entry.tags
        assert "soil" in entry.tags
        assert "crops" in entry.tags
    
    @pytest.mark.asyncio
    async def test_context_limits_enforcement(self, context_manager):
        """Test context limits per user."""
        user_id = "test_user_7"
        
        # Store more contexts than the limit (100 for test)
        for i in range(105):
            await context_manager.store_context(
                user_id=user_id,
                context_type=ContextType.SESSION,
                data={"index": i},
                priority=ContextPriority.LOW if i < 50 else ContextPriority.HIGH
            )
        
        # Check that limit is enforced
        user_contexts = context_manager.contexts.get(user_id, {})
        assert len(user_contexts) <= 100
        
        # Higher priority contexts should be retained
        remaining_contexts = list(user_contexts.values())
        high_priority_count = sum(1 for ctx in remaining_contexts 
                                if ctx.priority == ContextPriority.HIGH)
        assert high_priority_count > 0
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_contexts(self, context_manager):
        """Test cleanup of expired contexts."""
        user_id = "test_user_8"
        
        # Store expired context
        expired_id = await context_manager.store_context(
            user_id=user_id,
            context_type=ContextType.TEMPORARY,
            data={"expired": True},
            expires_at=datetime.utcnow() - timedelta(hours=1)
        )
        
        # Store valid context
        valid_id = await context_manager.store_context(
            user_id=user_id,
            context_type=ContextType.SESSION,
            data={"valid": True}
        )
        
        # Run cleanup
        await context_manager.cleanup_expired_contexts()
        
        # Check results
        expired_entry = await context_manager.get_context(user_id, expired_id)
        valid_entry = await context_manager.get_context(user_id, valid_id)
        
        assert expired_entry is None
        assert valid_entry is not None
    
    @pytest.mark.asyncio
    async def test_get_statistics(self, context_manager):
        """Test statistics generation."""
        user_id = "test_user_9"
        
        # Store some contexts
        await context_manager.store_context(
            user_id=user_id,
            context_type=ContextType.AGRICULTURAL,
            data={"test": "data1"}
        )
        
        await context_manager.store_context(
            user_id=user_id,
            context_type=ContextType.USER_PROFILE,
            data={"test": "data2"}
        )
        
        # Get statistics
        stats = await context_manager.get_statistics()
        
        assert "total_users" in stats
        assert "total_contexts" in stats
        assert "contexts_by_type" in stats
        assert stats["total_users"] >= 1
        assert stats["total_contexts"] >= 2


class TestContextAwareService:
    """Test context-aware service functionality."""
    
    @pytest.mark.asyncio
    async def test_process_request_basic(self, context_aware_service):
        """Test basic request processing with context."""
        request = ContextAwareRequest(
            user_id="test_user_10",
            session_id="session_456",
            message="What crops should I plant in Iowa?",
            agricultural_context={
                "location": "Iowa",
                "farm_size_acres": 320,
                "soil_data": {"ph": 6.2}
            }
        )
        
        response = await context_aware_service.process_request(request)
        
        assert response.content == "Mock agricultural response"
        assert response.model == "mock-model"
        assert response.conversation_updated is True
        assert len(response.context_stored) > 0
    
    @pytest.mark.asyncio
    async def test_context_continuity(self, context_aware_service):
        """Test conversation context continuity across requests."""
        user_id = "test_user_11"
        session_id = "session_789"
        
        # First request
        request1 = ContextAwareRequest(
            user_id=user_id,
            session_id=session_id,
            message="I have a 320-acre farm in Iowa",
            agricultural_context={
                "location": "Iowa",
                "farm_size_acres": 320
            }
        )
        
        response1 = await context_aware_service.process_request(request1)
        
        # Second request (should have context from first)
        request2 = ContextAwareRequest(
            user_id=user_id,
            session_id=session_id,
            message="What crops should I plant?"
        )
        
        response2 = await context_aware_service.process_request(request2)
        
        # Check that context was used
        assert "agricultural" in response2.context_used
        farm_profile = response2.context_used["agricultural"].get("farm_profile")
        if farm_profile:
            assert farm_profile.get("farm_size_acres") == 320
    
    @pytest.mark.asyncio
    async def test_user_preferences_update(self, context_aware_service):
        """Test user preferences update and usage."""
        user_id = "test_user_12"
        
        preferences = {
            "communication_style": "detailed",
            "expertise_level": "beginner",
            "preferred_units": "imperial"
        }
        
        success = await context_aware_service.update_user_preferences(
            user_id, preferences
        )
        
        assert success is True
        
        # Get context summary to verify preferences were stored
        summary = await context_aware_service.get_user_context_summary(user_id)
        
        assert "user_preferences" in summary
    
    @pytest.mark.asyncio
    async def test_clear_user_context(self, context_aware_service):
        """Test clearing user context."""
        user_id = "test_user_13"
        
        # Create some context first
        request = ContextAwareRequest(
            user_id=user_id,
            session_id="session_clear",
            message="Test message",
            agricultural_context={"test": "data"}
        )
        
        await context_aware_service.process_request(request)
        
        # Clear context
        cleared_count = await context_aware_service.clear_user_context(user_id)
        
        assert cleared_count > 0
        
        # Verify context is cleared
        summary = await context_aware_service.get_user_context_summary(user_id)
        assert summary["agricultural_profile"]["farms"] == 0
    
    @pytest.mark.asyncio
    async def test_service_health(self, context_aware_service):
        """Test service health check."""
        health = await context_aware_service.get_service_health()
        
        assert health["service"] == "context_aware_service"
        assert health["status"] in ["healthy", "degraded", "unhealthy"]
        assert "llm_service" in health
        assert "context_manager" in health
        assert "timestamp" in health


class TestContextIntegration:
    """Test integration between context management and LLM service."""
    
    @pytest.mark.asyncio
    async def test_agricultural_context_enhancement(self, context_aware_service):
        """Test that agricultural context enhances responses."""
        user_id = "test_user_14"
        session_id = "session_integration"
        
        # First, establish farm context
        farm_request = ContextAwareRequest(
            user_id=user_id,
            session_id=session_id,
            message="I have a farm in Iowa",
            agricultural_context={
                "location": "Iowa",
                "farm_size_acres": 160,
                "soil_data": {
                    "ph": 6.8,
                    "organic_matter_percent": 3.2,
                    "phosphorus_ppm": 28
                },
                "primary_crops": ["corn", "soybean"]
            }
        )
        
        await context_aware_service.process_request(farm_request)
        
        # Then ask a question that should use the context
        question_request = ContextAwareRequest(
            user_id=user_id,
            session_id=session_id,
            message="What fertilizer should I use?"
        )
        
        response = await context_aware_service.process_request(question_request)
        
        # Verify context was used
        assert "agricultural" in response.context_used
        agricultural_context = response.context_used["agricultural"]
        
        if agricultural_context.get("farm_profile"):
            farm_profile = agricultural_context["farm_profile"]
            assert farm_profile.get("location") == "Iowa"
            assert farm_profile.get("farm_size_acres") == 160
            assert "soil_data" in farm_profile
    
    @pytest.mark.asyncio
    async def test_conversation_memory(self, context_aware_service):
        """Test that conversation memory is maintained."""
        user_id = "test_user_15"
        session_id = "session_memory"
        
        # Series of related messages
        messages = [
            "I'm planning to plant corn this year",
            "My soil pH is 6.2",
            "What nitrogen rate should I use?",
            "Should I split the application?"
        ]
        
        responses = []
        for message in messages:
            request = ContextAwareRequest(
                user_id=user_id,
                session_id=session_id,
                message=message
            )
            
            response = await context_aware_service.process_request(request)
            responses.append(response)
        
        # Check that later responses have conversation context
        final_response = responses[-1]
        conversation_context = final_response.context_used.get("conversation", {})
        
        assert conversation_context.get("total_interactions", 0) > 0
        assert len(conversation_context.get("recent_messages", [])) > 0
    
    @pytest.mark.asyncio
    async def test_recommendation_context_storage(self, context_aware_service):
        """Test that recommendations are stored as context."""
        user_id = "test_user_16"
        session_id = "session_recommendations"
        
        # Ask for a recommendation
        request = ContextAwareRequest(
            user_id=user_id,
            session_id=session_id,
            message="What crops should I plant?",
            agricultural_context={
                "location": "Illinois",
                "farm_size_acres": 240
            }
        )
        
        response = await context_aware_service.process_request(request)
        
        # Check that recommendation context was stored
        assert len(response.context_stored) > 0
        
        # Get user summary to verify recommendation history
        summary = await context_aware_service.get_user_context_summary(user_id)
        
        interaction_history = summary.get("interaction_history", {})
        assert interaction_history.get("total_recommendations", 0) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])