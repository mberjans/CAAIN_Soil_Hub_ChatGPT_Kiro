"""
Tests for OpenRouter LLM integration
"""

import pytest
import asyncio
import os
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from src.services.openrouter_client import OpenRouterClient, LLMRequest, LLMResponse
from src.services.llm_service import LLMService, LLMServiceConfig


class TestOpenRouterClient:
    """Test OpenRouter client functionality."""
    
    @pytest.fixture
    def mock_api_key(self):
        return "sk-or-test-key-12345"
    
    @pytest.fixture
    def openrouter_client(self, mock_api_key):
        return OpenRouterClient(api_key=mock_api_key)
    
    @pytest.fixture
    def sample_llm_request(self):
        return LLMRequest(
            messages=[
                {"role": "user", "content": "What crops should I plant in Iowa?"}
            ],
            use_case="conversation"
        )
    
    def test_client_initialization(self, mock_api_key):
        """Test OpenRouter client initialization."""
        client = OpenRouterClient(api_key=mock_api_key)
        
        assert client.api_key == mock_api_key
        assert client.base_url == "https://openrouter.ai/api/v1"
        assert "conversation" in client.model_configs
        assert "explanation" in client.model_configs
    
    def test_get_model_config(self, openrouter_client):
        """Test model configuration retrieval."""
        # Test valid use case
        config = openrouter_client.get_model_config("explanation")
        assert config["model"] == "anthropic/claude-3-sonnet"
        assert config["temperature"] == 0.3
        
        # Test invalid use case (should default to conversation)
        config = openrouter_client.get_model_config("invalid_use_case")
        assert config["model"] == "anthropic/claude-3-sonnet"
    
    def test_estimate_tokens(self, openrouter_client):
        """Test token estimation."""
        text = "This is a test message for token estimation."
        tokens = openrouter_client.estimate_tokens(text)
        
        assert isinstance(tokens, int)
        assert tokens > 0
        assert tokens < len(text)  # Should be less than character count
    
    def test_calculate_cost(self, openrouter_client):
        """Test cost calculation."""
        model = "openai/gpt-3.5-turbo"
        input_tokens = 100
        output_tokens = 50
        
        cost = openrouter_client.calculate_cost(model, input_tokens, output_tokens)
        
        assert isinstance(cost, float)
        assert cost > 0
        
        # Test unknown model
        cost_unknown = openrouter_client.calculate_cost("unknown/model", 100, 50)
        assert cost_unknown == 0.0
    
    def test_prepare_messages(self, openrouter_client, sample_llm_request):
        """Test message preparation with system prompt."""
        messages = openrouter_client.prepare_messages(sample_llm_request)
        
        # Should add system prompt
        assert len(messages) >= 2
        assert messages[0]["role"] == "system"
        assert "agricultural advisor" in messages[0]["content"].lower()
        
        # Original message should be preserved
        assert messages[-1]["content"] == "What crops should I plant in Iowa?"
    
    def test_prepare_messages_with_agricultural_context(self, openrouter_client):
        """Test message preparation with agricultural context."""
        request = LLMRequest(
            messages=[{"role": "user", "content": "Test message"}],
            agricultural_context={
                "farm_location": "Iowa",
                "soil_data": {"ph": 6.2, "organic_matter_percent": 3.5}
            }
        )
        
        messages = openrouter_client.prepare_messages(request)
        
        # Should include agricultural context
        context_message = next(
            (msg for msg in messages if "Agricultural Context" in msg["content"]), 
            None
        )
        assert context_message is not None
        assert "Iowa" in context_message["content"]
        assert "pH 6.2" in context_message["content"]
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, openrouter_client):
        """Test rate limiting functionality."""
        model = "test/model"
        
        # First request should pass
        assert await openrouter_client.check_rate_limit(model) == True
        
        # Simulate many requests
        for _ in range(60):  # Exceed default limit of 50
            await openrouter_client.check_rate_limit(model)
        
        # Should now be rate limited
        assert await openrouter_client.check_rate_limit(model) == False
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_complete_success(self, mock_post, openrouter_client, sample_llm_request):
        """Test successful completion request."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "For Iowa conditions, I recommend corn and soybean varieties..."
                }
            }],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 150,
                "total_tokens": 250
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        response = await openrouter_client.complete(sample_llm_request)
        
        assert isinstance(response, LLMResponse)
        assert "corn and soybean" in response.content
        assert response.usage["total_tokens"] == 250
        assert response.cost_estimate > 0
        assert response.confidence_score is not None
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_complete_with_fallback(self, mock_post, openrouter_client, sample_llm_request):
        """Test completion with fallback on primary model failure."""
        # Mock primary model failure, then fallback success
        mock_post.side_effect = [
            Exception("Primary model failed"),
            MagicMock(json=lambda: {
                "choices": [{"message": {"content": "Fallback response"}}],
                "usage": {"prompt_tokens": 50, "completion_tokens": 75, "total_tokens": 125}
            }, raise_for_status=lambda: None)
        ]
        
        response = await openrouter_client.complete(sample_llm_request)
        
        assert response.content == "Fallback response"
        assert response.model == openrouter_client.model_configs["fallback"]["model"]
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.stream')
    async def test_stream_complete(self, mock_stream, openrouter_client, sample_llm_request):
        """Test streaming completion."""
        # Mock streaming response
        mock_response = AsyncMock()
        mock_response.raise_for_status.return_value = None
        
        async def mock_aiter_lines():
            yield "data: {'choices': [{'delta': {'content': 'For '}}]}"
            yield "data: {'choices': [{'delta': {'content': 'Iowa '}}]}"
            yield "data: {'choices': [{'delta': {'content': 'farming...'}}]}"
            yield "data: [DONE]"
        
        mock_response.aiter_lines = mock_aiter_lines
        mock_stream.return_value.__aenter__.return_value = mock_response
        
        sample_llm_request.stream = True
        chunks = []
        async for chunk in openrouter_client.stream_complete(sample_llm_request):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        assert "For " in chunks[0] or "Iowa " in chunks[1]
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_classify_question(self, mock_post, openrouter_client):
        """Test question classification."""
        # Mock classification response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": '{"category_number": 1, "category_name": "Crop Selection", "confidence": 0.95}'
                }
            }],
            "usage": {"prompt_tokens": 50, "completion_tokens": 25, "total_tokens": 75}
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = await openrouter_client.classify_question("What crops should I plant?")
        
        assert result["category_number"] == 1
        assert result["category_name"] == "Crop Selection"
        assert result["confidence"] == 0.95
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_explain_recommendation(self, mock_post, openrouter_client):
        """Test recommendation explanation."""
        # Mock explanation response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "This recommendation is based on your soil pH of 6.2..."
                }
            }],
            "usage": {"prompt_tokens": 200, "completion_tokens": 300, "total_tokens": 500}
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        recommendation = {"crop": "corn", "variety": "Pioneer P1197AM"}
        context = {"soil_data": {"ph": 6.2}}
        
        explanation = await openrouter_client.explain_recommendation(recommendation, context)
        
        assert "soil pH of 6.2" in explanation
        assert len(explanation) > 50
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.get')
    async def test_get_available_models(self, mock_get, openrouter_client):
        """Test getting available models."""
        # Mock models response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {
                    "id": "openai/gpt-4-turbo",
                    "name": "GPT-4 Turbo",
                    "context_length": 128000,
                    "pricing": {"prompt": "0.01", "completion": "0.03"}
                },
                {
                    "id": "anthropic/claude-3-sonnet",
                    "name": "Claude 3 Sonnet",
                    "context_length": 200000,
                    "pricing": {"prompt": "0.003", "completion": "0.015"}
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        models = await openrouter_client.get_available_models()
        
        assert len(models) == 2
        assert any(model["id"] == "openai/gpt-4-turbo" for model in models)
        assert any(model["id"] == "anthropic/claude-3-sonnet" for model in models)
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    @patch('httpx.AsyncClient.get')
    async def test_health_check(self, mock_get, mock_post, openrouter_client):
        """Test health check functionality."""
        # Mock models response
        mock_get.return_value = MagicMock(
            json=lambda: {"data": []},
            raise_for_status=lambda: None
        )
        
        # Mock test completion response
        mock_post.return_value = MagicMock(
            json=lambda: {
                "choices": [{"message": {"content": "Hello!"}}],
                "usage": {"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10}
            },
            raise_for_status=lambda: None
        )
        
        health = await openrouter_client.health_check()
        
        assert health["status"] == "healthy"
        assert health["api_accessible"] == True
        assert "test_response_time" in health


class TestLLMService:
    """Test LLM service functionality."""
    
    @pytest.fixture
    def llm_config(self):
        return LLMServiceConfig(
            openrouter_api_key="sk-or-test-key-12345",
            max_conversation_length=10,
            cache_responses=True
        )
    
    @pytest.fixture
    def llm_service(self, llm_config):
        return LLMService(llm_config)
    
    @pytest.mark.asyncio
    async def test_conversation_context_management(self, llm_service):
        """Test conversation context creation and management."""
        user_id = "test_user"
        session_id = "test_session"
        
        # Get new context
        context = await llm_service.get_conversation_context(user_id, session_id)
        
        assert context.user_id == user_id
        assert context.session_id == session_id
        assert len(context.conversation_history) == 0
        
        # Update context
        message = {"role": "user", "content": "Hello"}
        response = "Hi there!"
        agricultural_context = {"farm_location": "Iowa"}
        
        await llm_service.update_conversation_context(
            context, message, response, agricultural_context
        )
        
        assert len(context.conversation_history) == 2
        assert context.agricultural_context["farm_location"] == "Iowa"
    
    @pytest.mark.asyncio
    async def test_conversation_history_trimming(self, llm_service):
        """Test conversation history trimming when too long."""
        user_id = "test_user"
        session_id = "test_session"
        
        context = await llm_service.get_conversation_context(user_id, session_id)
        
        # Add many messages to exceed limit
        for i in range(15):
            message = {"role": "user", "content": f"Message {i}"}
            response = f"Response {i}"
            
            await llm_service.update_conversation_context(context, message, response)
        
        # Should be trimmed to max length
        assert len(context.conversation_history) <= llm_service.config.max_conversation_length
        
        # Should keep most recent messages
        last_message = context.conversation_history[-2]
        assert "Message 14" in last_message["content"]
    
    @pytest.mark.asyncio
    @patch('src.services.llm_service.LLMService.openrouter_client')
    async def test_classify_question(self, mock_client, llm_service):
        """Test question classification through service."""
        # Mock classification result
        mock_client.classify_question.return_value = {
            "category_number": 2,
            "category_name": "Soil Fertility",
            "confidence": 0.88
        }
        
        result = await llm_service.classify_question("How can I improve my soil?")
        
        assert result["category_number"] == 2
        assert result["category_name"] == "Soil Fertility"
        assert result["confidence"] == 0.88
        
        mock_client.classify_question.assert_called_once_with("How can I improve my soil?")
    
    @pytest.mark.asyncio
    @patch('src.services.llm_service.LLMService.openrouter_client')
    async def test_generate_response_with_caching(self, mock_client, llm_service):
        """Test response generation with caching."""
        # Mock LLM response
        mock_response = LLMResponse(
            content="Based on your Iowa location, I recommend corn and soybean...",
            model="anthropic/claude-3-sonnet",
            usage={"prompt_tokens": 100, "completion_tokens": 150, "total_tokens": 250},
            cost_estimate=0.01,
            response_time=2.5,
            confidence_score=0.85
        )
        mock_client.complete.return_value = mock_response
        
        user_id = "test_user"
        session_id = "test_session"
        message = "What crops should I plant?"
        
        # First call
        response1 = await llm_service.generate_response(
            user_id, session_id, message
        )
        
        # Second call with same parameters (should use cache)
        response2 = await llm_service.generate_response(
            user_id, session_id, message
        )
        
        assert response1.content == response2.content
        # Should only call LLM once due to caching
        assert mock_client.complete.call_count == 1
    
    @pytest.mark.asyncio
    @patch('src.services.llm_service.LLMService.openrouter_client')
    async def test_generate_agricultural_explanation(self, mock_client, llm_service):
        """Test agricultural explanation generation."""
        # Mock explanation
        mock_client.explain_recommendation.return_value = (
            "This nitrogen recommendation is based on your soil test results..."
        )

        recommendation = {
            "type": "nitrogen_rate",
            "rate_lbs_per_acre": 150,
            "reasoning": "Based on soil test and yield goal"
        }
        context = {
            "soil_data": {"ph": 6.2, "organic_matter_percent": 3.5},
            "crop": "corn",
            "yield_goal": 180
        }

        explanation = await llm_service.generate_agricultural_explanation(
            recommendation, context
        )

        assert "nitrogen recommendation" in explanation
        assert len(explanation) > 50

        mock_client.explain_recommendation.assert_called_once_with(recommendation, context)

    @pytest.mark.asyncio
    async def test_generate_variety_explanation(self, llm_service):
        """Ensure variety explanations use specialized generation."""
        mock_client = MagicMock()
        mock_client.generate_variety_explanation = AsyncMock(return_value="Variety explanation output")
        llm_service.openrouter_client = mock_client

        recommendation = {
            "recommended_varieties": [
                {
                    "variety_name": "Hybrid Advantage",
                    "overall_score": 0.92,
                    "key_advantages": ["Excellent drought tolerance"]
                }
            ]
        }
        context = {
            "user_preferences": {
                "language": "fr"
            }
        }

        explanation = await llm_service.generate_agricultural_explanation(
            recommendation,
            context
        )

        assert explanation == "Variety explanation output"
        mock_client.generate_variety_explanation.assert_called_once()
        call_args = mock_client.generate_variety_explanation.call_args
        payload = call_args[0][0]
        assert "yield_insights" in payload
        assert "disease_highlights" in payload
        assert "climate_adaptation" in payload
        assert "quality_metrics" in payload

    @pytest.mark.asyncio
    async def test_generate_structured_recommendation(self, llm_service):
        """Test structured recommendation generation."""
        # Mock LLM response
        mock_response = LLMResponse(
            content="For corn production in Iowa with your soil conditions...",
            model="anthropic/claude-3-sonnet",
            usage={"prompt_tokens": 200, "completion_tokens": 300, "total_tokens": 500},
            cost_estimate=0.02,
            response_time=3.0,
            confidence_score=0.90,
            agricultural_metadata={"topics_mentioned": ["corn", "soil", "nitrogen"]}
        )
        mock_client = MagicMock()
        mock_client.complete = AsyncMock(return_value=mock_response)
        llm_service.openrouter_client = mock_client
        
        input_data = {
            "crop_type": "corn",
            "soil_data": {"ph": 6.2, "organic_matter_percent": 3.5},
            "location": "Iowa",
            "farm_size": 320
        }
        
        result = await llm_service.generate_structured_recommendation(
            "crop_selection", input_data
        )
        
        assert result["question_type"] == "crop_selection"
        assert result["confidence_score"] == 0.90
        assert result["model_used"] == "anthropic/claude-3-sonnet"
        assert "generated_at" in result
    
    @pytest.mark.asyncio
    async def test_cleanup_old_conversations(self, llm_service):
        """Test cleanup of old conversations."""
        # Create some conversations with different ages
        old_context = await llm_service.get_conversation_context("old_user", "old_session")
        old_context.last_updated = datetime.utcnow().replace(year=2020)  # Very old
        
        new_context = await llm_service.get_conversation_context("new_user", "new_session")
        # new_context has current timestamp
        
        initial_count = len(llm_service.active_conversations)
        
        # Cleanup conversations older than 1 hour
        await llm_service.cleanup_old_conversations(max_age_hours=1)
        
        # Should have removed old conversation
        assert len(llm_service.active_conversations) < initial_count
        assert "new_user:new_session" in llm_service.active_conversations
        assert "old_user:old_session" not in llm_service.active_conversations
    
    @pytest.mark.asyncio
    @patch('src.services.llm_service.LLMService.openrouter_client')
    async def test_service_health_check(self, mock_client, llm_service):
        """Test service health check."""
        # Mock OpenRouter health check
        mock_client.health_check.return_value = {
            "status": "healthy",
            "available_models": 5,
            "test_response_time": 1.2,
            "api_accessible": True
        }
        
        health = await llm_service.get_service_health()
        
        assert health["service"] == "llm_service"
        assert health["status"] == "healthy"
        assert "active_conversations" in health
        assert "cached_responses" in health
        assert "openrouter_status" in health


@pytest.mark.integration
class TestOpenRouterIntegration:
    """Integration tests for OpenRouter (requires API key)."""
    
    @pytest.fixture
    def api_key(self):
        """Get API key from environment or skip tests."""
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            pytest.skip("OPENROUTER_API_KEY not set")
        return api_key
    
    @pytest.mark.asyncio
    async def test_real_classification(self, api_key):
        """Test real question classification with OpenRouter."""
        async with OpenRouterClient(api_key=api_key) as client:
            result = await client.classify_question(
                "What fertilizer should I use for my corn crop?"
            )
            
            assert "category_number" in result
            assert "category_name" in result
            assert "confidence" in result
            assert 1 <= result["category_number"] <= 20
    
    @pytest.mark.asyncio
    async def test_real_completion(self, api_key):
        """Test real completion with OpenRouter."""
        async with OpenRouterClient(api_key=api_key) as client:
            request = LLMRequest(
                messages=[{
                    "role": "user", 
                    "content": "What are the key factors for successful corn production?"
                }],
                use_case="conversation"
            )
            
            response = await client.complete(request)
            
            assert isinstance(response, LLMResponse)
            assert len(response.content) > 100
            assert response.confidence_score > 0.5
            assert response.cost_estimate > 0
    
    @pytest.mark.asyncio
    async def test_real_streaming(self, api_key):
        """Test real streaming with OpenRouter."""
        async with OpenRouterClient(api_key=api_key) as client:
            request = LLMRequest(
                messages=[{
                    "role": "user", 
                    "content": "Explain the nitrogen cycle in agriculture."
                }],
                use_case="explanation",
                stream=True
            )
            
            chunks = []
            async for chunk in client.stream_complete(request):
                chunks.append(chunk)
                if len(chunks) > 10:  # Limit for testing
                    break
            
            assert len(chunks) > 0
            full_text = "".join(chunks)
            assert len(full_text) > 50
    
    @pytest.mark.asyncio
    async def test_real_health_check(self, api_key):
        """Test real health check with OpenRouter."""
        async with OpenRouterClient(api_key=api_key) as client:
            health = await client.health_check()
            
            assert health["status"] == "healthy"
            assert health["api_accessible"] == True
            assert health["available_models"] > 0
