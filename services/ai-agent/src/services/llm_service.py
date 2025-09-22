"""
LLM Service for AFAS AI Agent

High-level service for managing LLM interactions with agricultural context,
conversation management, and response optimization.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime, timedelta
import json
import os
from pydantic import BaseModel, Field

from .openrouter_client import OpenRouterClient, LLMRequest, LLMResponse

logger = logging.getLogger(__name__)


class ConversationContext(BaseModel):
    """Context for ongoing conversations."""
    
    user_id: str
    session_id: str
    farm_profile: Optional[Dict[str, Any]] = None
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    agricultural_context: Optional[Dict[str, Any]] = None
    preferences: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class LLMServiceConfig(BaseModel):
    """Configuration for LLM service."""
    
    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    max_conversation_length: int = 20
    context_window_tokens: int = 4000
    enable_streaming: bool = True
    cache_responses: bool = True
    cache_ttl_seconds: int = 3600


class LLMService:
    """
    High-level LLM service for agricultural AI interactions.
    """
    
    def __init__(self, config: LLMServiceConfig):
        self.config = config
        self.openrouter_client = OpenRouterClient(
            api_key=config.openrouter_api_key,
            base_url=config.openrouter_base_url
        )
        
        # Conversation management
        self.active_conversations: Dict[str, ConversationContext] = {}
        
        # Response cache
        self.response_cache: Dict[str, Any] = {}
        
        # Agricultural prompt templates
        self.prompt_templates = {
            "crop_selection": """Based on the provided soil data and farm conditions, recommend suitable crop varieties.

Soil Data: {soil_data}
Farm Location: {location}
Farm Size: {farm_size} acres
Available Equipment: {equipment}

Consider:
- Soil pH and nutrient levels
- Climate zone and growing season
- Economic viability for farm size
- Equipment compatibility
- Regional pest and disease pressure

Provide specific variety recommendations with reasoning.""",

            "fertilizer_recommendation": """Calculate fertilizer recommendations based on soil test results and crop requirements.

Crop: {crop_type}
Yield Goal: {yield_goal} bu/acre
Soil Test Results: {soil_test}
Previous Crop: {previous_crop}

Calculate:
- Nitrogen rate (accounting for legume credit, soil test, organic matter)
- Phosphorus rate (buildup vs maintenance)
- Potassium rate (soil test interpretation)
- Application timing and method
- Cost analysis and ROI

Show calculations and cite extension guidelines.""",

            "soil_health": """Assess soil health and provide improvement recommendations.

Current Soil Data: {soil_data}
Field History: {field_history}
Management Goals: {goals}

Evaluate:
- Soil health indicators (pH, OM, nutrients, compaction)
- Limiting factors for crop production
- Improvement strategies (cover crops, organic amendments, tillage)
- Timeline and expected outcomes
- Cost-benefit analysis

Prioritize recommendations by impact and feasibility.""",

            "problem_diagnosis": """Diagnose crop problems based on symptoms and conditions.

Crop: {crop_type}
Growth Stage: {growth_stage}
Symptoms: {symptoms}
Recent Weather: {weather}
Management History: {management}

Analyze:
- Possible causes (nutrient deficiency, disease, pest, environmental)
- Differential diagnosis
- Recommended tests or observations
- Treatment options
- Prevention strategies

Provide confidence levels for each diagnosis."""
        }

    async def __aenter__(self):
        await self.openrouter_client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.openrouter_client.__aexit__(exc_type, exc_val, exc_tb)

    def _generate_cache_key(self, request_data: Dict[str, Any]) -> str:
        """Generate cache key for request."""
        # Create a hash of the request data for caching
        import hashlib
        request_str = json.dumps(request_data, sort_keys=True)
        return hashlib.md5(request_str.encode()).hexdigest()

    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid."""
        if not self.config.cache_responses:
            return False
        
        created_at = datetime.fromisoformat(cache_entry.get("created_at", ""))
        expiry = created_at + timedelta(seconds=self.config.cache_ttl_seconds)
        return datetime.utcnow() < expiry

    async def get_conversation_context(self, user_id: str, session_id: str) -> ConversationContext:
        """Get or create conversation context."""
        context_key = f"{user_id}:{session_id}"
        
        if context_key not in self.active_conversations:
            self.active_conversations[context_key] = ConversationContext(
                user_id=user_id,
                session_id=session_id
            )
        
        return self.active_conversations[context_key]

    async def update_conversation_context(
        self, 
        context: ConversationContext,
        message: Dict[str, str],
        response: str,
        agricultural_context: Optional[Dict[str, Any]] = None
    ):
        """Update conversation context with new message and response."""
        # Add message and response to history
        context.conversation_history.append(message)
        context.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        # Trim conversation history if too long
        if len(context.conversation_history) > self.config.max_conversation_length:
            # Keep system message and trim from the beginning
            system_messages = [msg for msg in context.conversation_history if msg.get("role") == "system"]
            other_messages = [msg for msg in context.conversation_history if msg.get("role") != "system"]
            
            # Keep most recent messages
            keep_count = self.config.max_conversation_length - len(system_messages)
            context.conversation_history = system_messages + other_messages[-keep_count:]
        
        # Update agricultural context
        if agricultural_context:
            if context.agricultural_context:
                context.agricultural_context.update(agricultural_context)
            else:
                context.agricultural_context = agricultural_context
        
        context.last_updated = datetime.utcnow()

    async def classify_question(self, question: str) -> Dict[str, Any]:
        """
        Classify farmer question into AFAS categories.
        
        Args:
            question: Farmer's question text
            
        Returns:
            Classification result with category and confidence
        """
        try:
            result = await self.openrouter_client.classify_question(question)
            
            logger.info(f"Question classified: category={result.get('category_name')}, "
                       f"confidence={result.get('confidence')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Question classification failed: {e}")
            return {
                "category_number": 1,
                "category_name": "General Agricultural Question",
                "confidence": 0.5,
                "error": str(e)
            }

    async def generate_response(
        self,
        user_id: str,
        session_id: str,
        message: str,
        agricultural_context: Optional[Dict[str, Any]] = None,
        use_case: str = "conversation",
        stream: bool = False
    ) -> LLMResponse:
        """
        Generate response to user message with conversation context.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            message: User message
            agricultural_context: Agricultural context data
            use_case: LLM use case (conversation, explanation, etc.)
            stream: Whether to stream response
            
        Returns:
            LLM response with content and metadata
        """
        try:
            # Get conversation context
            context = await self.get_conversation_context(user_id, session_id)
            
            # Check cache if enabled
            cache_key = None
            if self.config.cache_responses and not stream:
                cache_data = {
                    "message": message,
                    "agricultural_context": agricultural_context,
                    "use_case": use_case,
                    "conversation_history": context.conversation_history[-5:]  # Last 5 messages
                }
                cache_key = self._generate_cache_key(cache_data)
                
                if cache_key in self.response_cache:
                    cache_entry = self.response_cache[cache_key]
                    if self._is_cache_valid(cache_entry):
                        logger.info(f"Returning cached response for user {user_id}")
                        return LLMResponse(**cache_entry["response"])
            
            # Prepare messages with conversation history
            messages = []
            
            # Add conversation history (excluding system messages)
            for msg in context.conversation_history:
                if msg.get("role") != "system":
                    messages.append(msg)
            
            # Add current message
            messages.append({
                "role": "user",
                "content": message
            })
            
            # Create LLM request
            request = LLMRequest(
                messages=messages,
                use_case=use_case,
                stream=stream,
                agricultural_context=agricultural_context or context.agricultural_context
            )
            
            # Generate response
            if stream:
                # Return streaming response (handled separately)
                return await self._generate_streaming_response(request, context, message, agricultural_context)
            else:
                response = await self.openrouter_client.complete(request)
                
                # Update conversation context
                await self.update_conversation_context(
                    context,
                    {"role": "user", "content": message},
                    response.content,
                    agricultural_context
                )
                
                # Cache response if enabled
                if cache_key and self.config.cache_responses:
                    self.response_cache[cache_key] = {
                        "response": response.dict(),
                        "created_at": datetime.utcnow().isoformat()
                    }
                
                logger.info(f"Generated response for user {user_id}: "
                           f"model={response.model}, cost=${response.cost_estimate:.4f}")
                
                return response
                
        except Exception as e:
            logger.error(f"Response generation failed for user {user_id}: {e}")
            raise

    async def _generate_streaming_response(
        self,
        request: LLMRequest,
        context: ConversationContext,
        message: str,
        agricultural_context: Optional[Dict[str, Any]]
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response."""
        full_response = ""
        
        async for chunk in self.openrouter_client.stream_complete(request):
            full_response += chunk
            yield chunk
        
        # Update conversation context with complete response
        await self.update_conversation_context(
            context,
            {"role": "user", "content": message},
            full_response,
            agricultural_context
        )

    async def generate_agricultural_explanation(
        self,
        recommendation: Dict[str, Any],
        context: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> str:
        """
        Generate explanation for agricultural recommendation.
        
        Args:
            recommendation: Recommendation data
            context: Agricultural context
            user_id: Optional user ID for personalization
            
        Returns:
            Human-readable explanation
        """
        try:
            explanation = await self.openrouter_client.explain_recommendation(
                recommendation, context
            )
            
            logger.info(f"Generated agricultural explanation for recommendation type: "
                       f"{recommendation.get('type', 'unknown')}")
            
            return explanation
            
        except Exception as e:
            logger.error(f"Agricultural explanation generation failed: {e}")
            return "Unable to generate explanation at this time. Please try again later."

    async def generate_structured_recommendation(
        self,
        question_type: str,
        input_data: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate structured recommendation for specific question type.
        
        Args:
            question_type: Type of agricultural question
            input_data: Input data for recommendation
            user_id: Optional user ID
            
        Returns:
            Structured recommendation with explanation
        """
        try:
            # Get appropriate prompt template
            template_key = self._get_template_key(question_type)
            if template_key not in self.prompt_templates:
                template_key = "crop_selection"  # Default template
            
            # Format prompt with input data
            prompt = self.prompt_templates[template_key].format(**input_data)
            
            # Generate response
            request = LLMRequest(
                messages=[{"role": "user", "content": prompt}],
                use_case="explanation",
                agricultural_context=input_data
            )
            
            response = await self.openrouter_client.complete(request)
            
            # Structure the response
            structured_response = {
                "question_type": question_type,
                "recommendation": response.content,
                "confidence_score": response.confidence_score,
                "model_used": response.model,
                "cost_estimate": response.cost_estimate,
                "response_time": response.response_time,
                "agricultural_metadata": response.agricultural_metadata,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Generated structured recommendation for {question_type}")
            
            return structured_response
            
        except Exception as e:
            logger.error(f"Structured recommendation generation failed: {e}")
            raise

    def _get_template_key(self, question_type: str) -> str:
        """Map question type to prompt template key."""
        mapping = {
            "crop_selection": "crop_selection",
            "fertilizer_rate": "fertilizer_recommendation",
            "fertilizer_strategy": "fertilizer_recommendation",
            "soil_fertility": "soil_health",
            "soil_health": "soil_health",
            "nutrient_deficiency": "problem_diagnosis",
            "problem_diagnosis": "problem_diagnosis"
        }
        
        return mapping.get(question_type.lower(), "crop_selection")

    async def get_service_health(self) -> Dict[str, Any]:
        """Get service health status."""
        try:
            # Check OpenRouter client health
            openrouter_health = await self.openrouter_client.health_check()
            
            # Service-specific metrics
            service_health = {
                "service": "llm_service",
                "status": "healthy" if openrouter_health["status"] == "healthy" else "degraded",
                "active_conversations": len(self.active_conversations),
                "cached_responses": len(self.response_cache),
                "openrouter_status": openrouter_health,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return service_health
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "service": "llm_service",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def cleanup_old_conversations(self, max_age_hours: int = 24):
        """Clean up old conversation contexts."""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        to_remove = []
        for key, context in self.active_conversations.items():
            if context.last_updated < cutoff_time:
                to_remove.append(key)
        
        for key in to_remove:
            del self.active_conversations[key]
        
        logger.info(f"Cleaned up {len(to_remove)} old conversations")

    async def cleanup_old_cache(self):
        """Clean up expired cache entries."""
        to_remove = []
        for key, entry in self.response_cache.items():
            if not self._is_cache_valid(entry):
                to_remove.append(key)
        
        for key in to_remove:
            del self.response_cache[key]
        
        logger.info(f"Cleaned up {len(to_remove)} expired cache entries")


def create_llm_service() -> LLMService:
    """Create LLM service with configuration from environment."""
    config = LLMServiceConfig(
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", ""),
        openrouter_base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        max_conversation_length=int(os.getenv("MAX_CONVERSATION_LENGTH", "20")),
        context_window_tokens=int(os.getenv("CONTEXT_WINDOW_TOKENS", "4000")),
        enable_streaming=os.getenv("ENABLE_STREAMING", "true").lower() == "true",
        cache_responses=os.getenv("CACHE_RESPONSES", "true").lower() == "true",
        cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "3600"))
    )
    
    return LLMService(config)