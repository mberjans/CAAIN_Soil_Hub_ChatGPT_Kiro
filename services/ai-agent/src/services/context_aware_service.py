"""
Context-Aware AI Service for AFAS

Integrates context management with LLM service to provide
context-aware responses with memory and continuity.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime
import json

from .context_manager import (
    ContextManager, ContextType, ContextPriority, ContextScope,
    get_context_manager
)
from .llm_service import LLMService, LLMServiceConfig
from .openrouter_client import LLMRequest, LLMResponse

logger = logging.getLogger(__name__)


class ContextAwareRequest:
    """Request with context awareness."""
    
    def __init__(self,
                 user_id: str,
                 session_id: str,
                 message: str,
                 use_case: str = "conversation",
                 agricultural_context: Optional[Dict[str, Any]] = None,
                 context_preferences: Optional[Dict[str, Any]] = None):
        self.user_id = user_id
        self.session_id = session_id
        self.message = message
        self.use_case = use_case
        self.agricultural_context = agricultural_context or {}
        self.context_preferences = context_preferences or {}


class ContextAwareResponse:
    """Response with context information."""
    
    def __init__(self,
                 content: str,
                 llm_response: LLMResponse,
                 context_used: Dict[str, Any],
                 context_stored: List[str],
                 conversation_updated: bool = True):
        self.content = content
        self.llm_response = llm_response
        self.context_used = context_used
        self.context_stored = context_stored
        self.conversation_updated = conversation_updated
        
        # Inherit LLM response properties
        self.model = llm_response.model
        self.cost_estimate = llm_response.cost_estimate
        self.response_time = llm_response.response_time
        self.confidence_score = llm_response.confidence_score
        self.agricultural_metadata = llm_response.agricultural_metadata


class ContextAwareService:
    """
    Context-aware AI service that combines LLM capabilities with
    comprehensive context management for enhanced agricultural AI.
    """
    
    def __init__(self, 
                 llm_service: LLMService,
                 context_manager: Optional[ContextManager] = None,
                 max_context_tokens: int = 2000,
                 context_relevance_threshold: float = 0.3):
        """
        Initialize context-aware service.
        
        Args:
            llm_service: LLM service instance
            context_manager: Context manager instance
            max_context_tokens: Maximum tokens to use for context
            context_relevance_threshold: Minimum relevance score for context inclusion
        """
        self.llm_service = llm_service
        self.context_manager = context_manager or get_context_manager()
        self.max_context_tokens = max_context_tokens
        self.context_relevance_threshold = context_relevance_threshold
        
        logger.info("Context-aware service initialized")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.llm_service.__aenter__()
        await self.context_manager.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.llm_service.__aexit__(exc_type, exc_val, exc_tb)
        await self.context_manager.stop()
    
    async def process_request(self, request: ContextAwareRequest) -> ContextAwareResponse:
        """
        Process context-aware request with full context integration.
        
        Args:
            request: Context-aware request
            
        Returns:
            Context-aware response with metadata
        """
        try:
            # Get relevant context
            context_data = await self.context_manager.get_relevant_context(
                user_id=request.user_id,
                session_id=request.session_id,
                query=request.message,
                max_contexts=10
            )
            
            # Update conversation context with current message
            conversation = await self.context_manager.get_conversation_context(
                request.user_id, request.session_id
            )
            
            # Detect question type and update conversation state
            question_classification = await self.llm_service.classify_question(request.message)
            
            if question_classification.get('category_name'):
                conversation.current_topic = question_classification['category_name']
                conversation.question_sequence.append(question_classification['category_name'])
            
            # Add agricultural context if provided
            if request.agricultural_context:
                await self._store_agricultural_context(request, context_data)
            
            # Prepare enhanced LLM request with context
            enhanced_request = await self._prepare_enhanced_request(
                request, context_data, conversation
            )
            
            # Generate response using LLM service
            llm_response = await self.llm_service.generate_response(
                user_id=request.user_id,
                session_id=request.session_id,
                message=enhanced_request.messages[-1]["content"],
                agricultural_context=enhanced_request.agricultural_context,
                use_case=request.use_case
            )
            
            # Store response context
            stored_contexts = await self._store_response_context(
                request, llm_response, question_classification
            )
            
            # Update conversation with response
            conversation.add_message("user", request.message)
            conversation.add_message("assistant", llm_response.content, {
                "model": llm_response.model,
                "confidence": llm_response.confidence_score,
                "question_type": question_classification.get('category_name')
            })
            
            # Create context-aware response
            response = ContextAwareResponse(
                content=llm_response.content,
                llm_response=llm_response,
                context_used=context_data,
                context_stored=stored_contexts,
                conversation_updated=True
            )
            
            logger.info(f"Processed context-aware request for user {request.user_id}: "
                       f"contexts_used={len(context_data.get('relevant_contexts', []))}, "
                       f"contexts_stored={len(stored_contexts)}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing context-aware request: {e}")
            raise
    
    async def stream_response(self, request: ContextAwareRequest) -> AsyncGenerator[str, None]:
        """
        Stream context-aware response.
        
        Args:
            request: Context-aware request
            
        Yields:
            Response chunks
        """
        try:
            # Get context (similar to process_request but for streaming)
            context_data = await self.context_manager.get_relevant_context(
                user_id=request.user_id,
                session_id=request.session_id,
                query=request.message,
                max_contexts=10
            )
            
            conversation = await self.context_manager.get_conversation_context(
                request.user_id, request.session_id
            )
            
            # Prepare enhanced request
            enhanced_request = await self._prepare_enhanced_request(
                request, context_data, conversation
            )
            
            # Stream response
            full_response = ""
            async for chunk in self.llm_service._generate_streaming_response(
                enhanced_request, conversation, request.message, 
                enhanced_request.agricultural_context
            ):
                full_response += chunk
                yield chunk
            
            # Store context after streaming completes
            question_classification = await self.llm_service.classify_question(request.message)
            
            # Create mock LLM response for context storage
            mock_response = type('MockResponse', (), {
                'content': full_response,
                'model': 'streaming',
                'confidence_score': 0.8,
                'agricultural_metadata': {}
            })()
            
            await self._store_response_context(request, mock_response, question_classification)
            
        except Exception as e:
            logger.error(f"Error streaming context-aware response: {e}")
            yield f"Error: {str(e)}"
    
    async def _prepare_enhanced_request(self,
                                      request: ContextAwareRequest,
                                      context_data: Dict[str, Any],
                                      conversation) -> LLMRequest:
        """
        Prepare enhanced LLM request with context information.
        
        Args:
            request: Original request
            context_data: Retrieved context data
            conversation: Conversation context
            
        Returns:
            Enhanced LLM request
        """
        # Build context-enhanced system message
        system_parts = []
        
        # Add conversation context
        if context_data.get("conversation", {}).get("summary"):
            system_parts.append(f"Conversation context: {context_data['conversation']['summary']}")
        
        # Add agricultural context
        agricultural_info = context_data.get("agricultural", {})
        if agricultural_info.get("farm_profile"):
            farm_profile = agricultural_info["farm_profile"]
            farm_info = []
            
            if farm_profile.get("location"):
                farm_info.append(f"Farm location: {farm_profile['location']}")
            if farm_profile.get("farm_size_acres"):
                farm_info.append(f"Farm size: {farm_profile['farm_size_acres']} acres")
            if farm_profile.get("primary_crops"):
                farm_info.append(f"Primary crops: {', '.join(farm_profile['primary_crops'])}")
            if farm_profile.get("soil_data"):
                soil_data = farm_profile["soil_data"]
                soil_info = []
                if soil_data.get("ph"):
                    soil_info.append(f"pH {soil_data['ph']}")
                if soil_data.get("organic_matter_percent"):
                    soil_info.append(f"OM {soil_data['organic_matter_percent']}%")
                if soil_info:
                    farm_info.append(f"Soil: {', '.join(soil_info)}")
            
            if farm_info:
                system_parts.append(f"Farm profile: {'; '.join(farm_info)}")
        
        # Add relevant historical context
        relevant_contexts = context_data.get("relevant_contexts", [])
        if relevant_contexts:
            context_summaries = []
            for ctx in relevant_contexts[:3]:  # Top 3 most relevant
                if ctx.get("summary"):
                    context_summaries.append(f"- {ctx['summary']}")
            
            if context_summaries:
                system_parts.append(f"Relevant context:\n{chr(10).join(context_summaries)}")
        
        # Add user preferences
        user_prefs = context_data.get("user_preferences", {})
        if user_prefs.get("expertise_level"):
            system_parts.append(f"User expertise level: {user_prefs['expertise_level']}")
        if user_prefs.get("communication_style"):
            system_parts.append(f"Preferred communication style: {user_prefs['communication_style']}")
        
        # Build messages
        messages = []
        
        # Add system message with context
        if system_parts:
            system_message = "Context for this conversation:\n" + "\n".join(system_parts)
            messages.append({"role": "system", "content": system_message})
        
        # Add recent conversation history
        recent_messages = context_data.get("conversation", {}).get("recent_messages", [])
        for msg in recent_messages[-5:]:  # Last 5 messages
            if msg.get("role") and msg.get("content"):
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Add current message
        messages.append({"role": "user", "content": request.message})
        
        # Combine agricultural context
        combined_agricultural_context = {}
        if request.agricultural_context:
            combined_agricultural_context.update(request.agricultural_context)
        if agricultural_info:
            combined_agricultural_context.update(agricultural_info)
        
        return LLMRequest(
            messages=messages,
            use_case=request.use_case,
            agricultural_context=combined_agricultural_context
        )
    
    async def _store_agricultural_context(self,
                                        request: ContextAwareRequest,
                                        existing_context: Dict[str, Any]):
        """Store new agricultural context information."""
        if not request.agricultural_context:
            return
        
        # Check if this is new farm data
        existing_farm = existing_context.get("agricultural", {}).get("farm_profile")
        new_farm_data = request.agricultural_context
        
        # Store if significantly different or new
        should_store = False
        
        if not existing_farm:
            should_store = True
        else:
            # Check for significant changes
            for key in ["location", "farm_size_acres", "soil_data", "equipment"]:
                if key in new_farm_data and new_farm_data[key] != existing_farm.get(key):
                    should_store = True
                    break
        
        if should_store:
            await self.context_manager.store_agricultural_context(
                user_id=request.user_id,
                farm_data=new_farm_data,
                source="user_input"
            )
            
            # Update conversation context
            await self.context_manager.update_conversation_context(
                request.user_id,
                request.session_id,
                farm_profile=new_farm_data
            )
    
    async def _store_response_context(self,
                                    request: ContextAwareRequest,
                                    llm_response,
                                    question_classification: Dict[str, Any]) -> List[str]:
        """Store response-related context information."""
        stored_contexts = []
        
        try:
            # Store recommendation if this was a recommendation request
            if question_classification.get('category_name') and llm_response.content:
                recommendation_data = {
                    "question_type": question_classification['category_name'],
                    "question": request.message,
                    "response": llm_response.content,
                    "confidence": getattr(llm_response, 'confidence_score', 0.8),
                    "model": getattr(llm_response, 'model', 'unknown'),
                    "timestamp": datetime.utcnow().isoformat(),
                    "agricultural_context": request.agricultural_context
                }
                
                context_id = await self.context_manager.store_recommendation_context(
                    user_id=request.user_id,
                    recommendation=recommendation_data,
                    question_type=question_classification['category_name']
                )
                stored_contexts.append(context_id)
            
            # Store interaction context for learning
            interaction_data = {
                "message": request.message,
                "response_length": len(llm_response.content),
                "use_case": request.use_case,
                "question_classification": question_classification,
                "response_time": getattr(llm_response, 'response_time', 0),
                "cost": getattr(llm_response, 'cost_estimate', 0)
            }
            
            context_id = await self.context_manager.store_context(
                user_id=request.user_id,
                context_type=ContextType.SESSION,
                data=interaction_data,
                priority=ContextPriority.LOW,
                scope=ContextScope.SESSION,
                summary=f"Interaction: {question_classification.get('category_name', 'general')}",
                tags=["interaction", "session_data"],
                source="context_aware_service"
            )
            stored_contexts.append(context_id)
            
        except Exception as e:
            logger.error(f"Error storing response context: {e}")
        
        return stored_contexts
    
    async def get_user_context_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive context summary for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Context summary
        """
        try:
            # Get agricultural contexts
            agricultural_contexts = await self.context_manager.get_contexts_by_type(
                user_id, ContextType.AGRICULTURAL, limit=5
            )
            
            # Get recommendation history
            recommendation_contexts = await self.context_manager.get_contexts_by_type(
                user_id, ContextType.RECOMMENDATION_HISTORY, limit=10
            )
            
            # Get user profile contexts
            profile_contexts = await self.context_manager.get_contexts_by_type(
                user_id, ContextType.USER_PROFILE, limit=3
            )
            
            # Compile summary
            summary = {
                "user_id": user_id,
                "agricultural_profile": {
                    "farms": len(agricultural_contexts),
                    "latest_farm_data": agricultural_contexts[0].data if agricultural_contexts else None
                },
                "interaction_history": {
                    "total_recommendations": len(recommendation_contexts),
                    "recent_questions": [
                        ctx.data.get("question_type", "unknown") 
                        for ctx in recommendation_contexts[:5]
                    ]
                },
                "user_preferences": {
                    "profile_data": profile_contexts[0].data if profile_contexts else None
                },
                "context_statistics": await self.context_manager.get_statistics()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting user context summary: {e}")
            return {"error": str(e)}
    
    async def update_user_preferences(self,
                                    user_id: str,
                                    preferences: Dict[str, Any]) -> bool:
        """
        Update user preferences and communication style.
        
        Args:
            user_id: User identifier
            preferences: User preferences to store
            
        Returns:
            Success status
        """
        try:
            await self.context_manager.store_context(
                user_id=user_id,
                context_type=ContextType.USER_PROFILE,
                data=preferences,
                priority=ContextPriority.HIGH,
                scope=ContextScope.GLOBAL,
                summary=f"User preferences: {', '.join(preferences.keys())}",
                tags=["preferences", "user_profile"],
                source="user_settings"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
            return False
    
    async def clear_user_context(self, 
                               user_id: str,
                               context_types: Optional[List[ContextType]] = None) -> int:
        """
        Clear user context data.
        
        Args:
            user_id: User identifier
            context_types: Specific context types to clear (None for all)
            
        Returns:
            Number of contexts cleared
        """
        try:
            if user_id not in self.context_manager.contexts:
                return 0
            
            user_contexts = self.context_manager.contexts[user_id]
            contexts_to_remove = []
            
            for context_id, entry in user_contexts.items():
                if context_types is None or entry.context_type in context_types:
                    contexts_to_remove.append(context_id)
            
            for context_id in contexts_to_remove:
                await self.context_manager._remove_context(user_id, context_id)
            
            # Clear conversations if requested
            if context_types is None or ContextType.CONVERSATION in context_types:
                conv_keys_to_remove = [
                    key for key in self.context_manager.conversations.keys()
                    if key.startswith(f"{user_id}:")
                ]
                for key in conv_keys_to_remove:
                    del self.context_manager.conversations[key]
            
            logger.info(f"Cleared {len(contexts_to_remove)} contexts for user {user_id}")
            return len(contexts_to_remove)
            
        except Exception as e:
            logger.error(f"Error clearing user context: {e}")
            return 0
    
    async def get_service_health(self) -> Dict[str, Any]:
        """Get comprehensive service health status."""
        try:
            llm_health = await self.llm_service.get_service_health()
            context_stats = await self.context_manager.get_statistics()
            
            return {
                "service": "context_aware_service",
                "status": "healthy" if llm_health["status"] == "healthy" else "degraded",
                "llm_service": llm_health,
                "context_manager": context_stats,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "service": "context_aware_service",
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


def create_context_aware_service(llm_service: LLMService) -> ContextAwareService:
    """Create context-aware service with LLM service."""
    return ContextAwareService(llm_service)