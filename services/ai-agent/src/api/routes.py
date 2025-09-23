"""
API Routes for AFAS AI Agent Service

Provides endpoints for LLM interactions, question classification,
agricultural explanations, and context management.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ..services.llm_service import LLMService, create_llm_service
from ..services.context_aware_service import (
    ContextAwareService, ContextAwareRequest, create_context_aware_service
)
from ..services.context_manager import ContextType, ContextPriority, get_context_manager

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1", tags=["ai-agent"])

# Global service instances
llm_service: Optional[LLMService] = None
context_aware_service: Optional[ContextAwareService] = None


async def get_llm_service() -> LLMService:
    """Dependency to get LLM service instance."""
    global llm_service
    if llm_service is None:
        llm_service = create_llm_service()
        await llm_service.__aenter__()
    return llm_service


async def get_context_aware_service() -> ContextAwareService:
    """Dependency to get context-aware service instance."""
    global context_aware_service
    if context_aware_service is None:
        llm_svc = await get_llm_service()
        context_aware_service = create_context_aware_service(llm_svc)
        await context_aware_service.__aenter__()
    return context_aware_service


# Request/Response Models
class QuestionClassificationRequest(BaseModel):
    """Request for question classification."""
    question: str = Field(..., description="Farmer's question to classify")


class QuestionClassificationResponse(BaseModel):
    """Response for question classification."""
    category_number: int
    category_name: str
    confidence: float
    processing_time: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    """Request for chat interaction."""
    message: str = Field(..., description="User message")
    user_id: str = Field(..., description="User identifier")
    session_id: Optional[str] = Field(None, description="Session identifier")
    agricultural_context: Optional[Dict[str, Any]] = Field(None, description="Agricultural context data")
    context_preferences: Optional[Dict[str, Any]] = Field(None, description="Context preferences")
    stream: bool = Field(False, description="Whether to stream response")


class ChatResponse(BaseModel):
    """Response for chat interaction."""
    response: str
    session_id: str
    model_used: str
    confidence_score: Optional[float]
    cost_estimate: float
    response_time: float
    agricultural_metadata: Optional[Dict[str, Any]]
    context_used: Dict[str, Any] = Field(default_factory=dict, description="Context information used")
    context_stored: List[str] = Field(default_factory=list, description="Context IDs stored")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ContextSummaryResponse(BaseModel):
    """Response for user context summary."""
    user_id: str
    agricultural_profile: Dict[str, Any]
    interaction_history: Dict[str, Any]
    user_preferences: Dict[str, Any]
    context_statistics: Dict[str, Any]


class UserPreferencesRequest(BaseModel):
    """Request to update user preferences."""
    communication_style: Optional[str] = Field(None, description="Preferred communication style")
    expertise_level: Optional[str] = Field(None, description="Agricultural expertise level")
    preferred_units: Optional[str] = Field(None, description="Preferred measurement units")
    notification_preferences: Optional[Dict[str, Any]] = Field(None, description="Notification settings")
    privacy_settings: Optional[Dict[str, Any]] = Field(None, description="Privacy preferences")


class ExplanationRequest(BaseModel):
    """Request for agricultural explanation."""
    recommendation: Dict[str, Any] = Field(..., description="Recommendation to explain")
    context: Dict[str, Any] = Field(..., description="Agricultural context")
    user_id: Optional[str] = Field(None, description="User identifier for personalization")


class ExplanationResponse(BaseModel):
    """Response for agricultural explanation."""
    explanation: str
    confidence_score: Optional[float]
    model_used: str
    cost_estimate: float
    response_time: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StructuredRecommendationRequest(BaseModel):
    """Request for structured recommendation."""
    question_type: str = Field(..., description="Type of agricultural question")
    input_data: Dict[str, Any] = Field(..., description="Input data for recommendation")
    user_id: Optional[str] = Field(None, description="User identifier")


class HealthResponse(BaseModel):
    """Health check response."""
    service: str
    status: str
    active_conversations: int
    cached_responses: int
    openrouter_status: Dict[str, Any]
    timestamp: datetime


# API Endpoints

@router.post("/classify-question", response_model=QuestionClassificationResponse)
async def classify_question(
    request: QuestionClassificationRequest,
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Classify farmer question into AFAS categories.
    
    This endpoint uses LLM to classify incoming questions into one of the 20
    predefined AFAS question categories for proper routing and processing.
    """
    try:
        start_time = datetime.utcnow()
        
        result = await llm_service.classify_question(request.question)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return QuestionClassificationResponse(
            category_number=result.get("category_number", 1),
            category_name=result.get("category_name", "General Agricultural Question"),
            confidence=result.get("confidence", 0.5),
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Question classification failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Question classification failed: {str(e)}"
        )


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    context_service: ContextAwareService = Depends(get_context_aware_service)
):
    """
    Generate conversational response to user message with context awareness.
    
    This endpoint provides conversational AI capabilities with comprehensive
    context management, agricultural awareness, and conversation continuity.
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Create context-aware request
        context_request = ContextAwareRequest(
            user_id=request.user_id,
            session_id=session_id,
            message=request.message,
            use_case="conversation",
            agricultural_context=request.agricultural_context,
            context_preferences=request.context_preferences
        )
        
        # Generate context-aware response
        response = await context_service.process_request(context_request)
        
        return ChatResponse(
            response=response.content,
            session_id=session_id,
            model_used=response.model,
            confidence_score=response.confidence_score,
            cost_estimate=response.cost_estimate,
            response_time=response.response_time,
            agricultural_metadata=response.agricultural_metadata,
            context_used=response.context_used,
            context_stored=response.context_stored
        )
        
    except Exception as e:
        logger.error(f"Context-aware chat response generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Chat response generation failed: {str(e)}"
        )


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    context_service: ContextAwareService = Depends(get_context_aware_service)
):
    """
    Generate streaming conversational response with context awareness.
    
    This endpoint provides real-time streaming responses with comprehensive
    context management for better user experience during agricultural interactions.
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        async def generate_stream():
            try:
                # Create context-aware request
                context_request = ContextAwareRequest(
                    user_id=request.user_id,
                    session_id=session_id,
                    message=request.message,
                    use_case="conversation",
                    agricultural_context=request.agricultural_context,
                    context_preferences=request.context_preferences
                )
                
                # Stream context-aware response
                async for chunk in context_service.stream_response(context_request):
                    yield f"data: {chunk}\n\n"
                
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"Context-aware streaming failed: {e}")
                yield f"data: Error: {str(e)}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Session-ID": session_id
            }
        )
        
    except Exception as e:
        logger.error(f"Context-aware chat streaming setup failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Chat streaming failed: {str(e)}"
        )


@router.post("/explain", response_model=ExplanationResponse)
async def explain_recommendation(
    request: ExplanationRequest,
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Generate explanation for agricultural recommendation.
    
    This endpoint provides detailed, farmer-friendly explanations for
    agricultural recommendations generated by the recommendation engine.
    """
    try:
        start_time = datetime.utcnow()
        
        explanation = await llm_service.generate_agricultural_explanation(
            recommendation=request.recommendation,
            context=request.context,
            user_id=request.user_id
        )
        
        # For explanation endpoint, we need to make a separate call to get metadata
        # This is a simplified version - in production, you might want to modify
        # the service to return more metadata
        response_time = (datetime.utcnow() - start_time).total_seconds()
        
        return ExplanationResponse(
            explanation=explanation,
            confidence_score=0.85,  # Default confidence for explanations
            model_used="anthropic/claude-3-sonnet",  # Default explanation model
            cost_estimate=0.01,  # Estimated cost
            response_time=response_time
        )
        
    except Exception as e:
        logger.error(f"Explanation generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Explanation generation failed: {str(e)}"
        )


@router.post("/recommend")
async def generate_structured_recommendation(
    request: StructuredRecommendationRequest,
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Generate structured recommendation for specific question type.
    
    This endpoint provides structured agricultural recommendations using
    predefined templates and agricultural context.
    """
    try:
        recommendation = await llm_service.generate_structured_recommendation(
            question_type=request.question_type,
            input_data=request.input_data,
            user_id=request.user_id
        )
        
        return recommendation
        
    except Exception as e:
        logger.error(f"Structured recommendation generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Structured recommendation generation failed: {str(e)}"
        )


@router.get("/models")
async def get_available_models(
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Get list of available LLM models from OpenRouter.
    
    This endpoint provides information about available models,
    their capabilities, and pricing for transparency.
    """
    try:
        models = await llm_service.openrouter_client.get_available_models()
        
        return {
            "available_models": models,
            "model_configs": llm_service.openrouter_client.model_configs,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get available models: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get available models: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check(
    context_service: ContextAwareService = Depends(get_context_aware_service)
):
    """
    Check service health and connectivity.
    
    This endpoint provides comprehensive health information including
    OpenRouter API connectivity, context management, and service metrics.
    """
    try:
        health_data = await context_service.get_service_health()
        
        return HealthResponse(
            service=health_data["service"],
            status=health_data["status"],
            active_conversations=health_data.get("context_manager", {}).get("active_conversations", 0),
            cached_responses=health_data.get("llm_service", {}).get("cached_responses", 0),
            openrouter_status=health_data.get("llm_service", {}).get("openrouter_status", {}),
            timestamp=datetime.fromisoformat(health_data["timestamp"])
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/context/{user_id}", response_model=ContextSummaryResponse)
async def get_user_context_summary(
    user_id: str,
    context_service: ContextAwareService = Depends(get_context_aware_service)
):
    """
    Get comprehensive context summary for a user.
    
    This endpoint provides detailed information about user's agricultural profile,
    interaction history, preferences, and context statistics.
    """
    try:
        summary = await context_service.get_user_context_summary(user_id)
        
        return ContextSummaryResponse(
            user_id=user_id,
            agricultural_profile=summary.get("agricultural_profile", {}),
            interaction_history=summary.get("interaction_history", {}),
            user_preferences=summary.get("user_preferences", {}),
            context_statistics=summary.get("context_statistics", {})
        )
        
    except Exception as e:
        logger.error(f"Failed to get context summary for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get context summary: {str(e)}"
        )


@router.post("/context/{user_id}/preferences")
async def update_user_preferences(
    user_id: str,
    request: UserPreferencesRequest,
    context_service: ContextAwareService = Depends(get_context_aware_service)
):
    """
    Update user preferences and communication settings.
    
    This endpoint allows users to customize their interaction preferences,
    communication style, and agricultural expertise level for better responses.
    """
    try:
        # Convert request to preferences dict
        preferences = {}
        for field, value in request.dict(exclude_unset=True).items():
            if value is not None:
                preferences[field] = value
        
        success = await context_service.update_user_preferences(user_id, preferences)
        
        if success:
            return {
                "message": "User preferences updated successfully",
                "user_id": user_id,
                "updated_preferences": list(preferences.keys()),
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to update user preferences"
            )
        
    except Exception as e:
        logger.error(f"Failed to update preferences for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update preferences: {str(e)}"
        )


@router.delete("/context/{user_id}")
async def clear_user_context(
    user_id: str,
    context_types: Optional[List[str]] = None,
    context_service: ContextAwareService = Depends(get_context_aware_service)
):
    """
    Clear user context data.
    
    This endpoint allows users to clear their context data for privacy
    or to start fresh. Can clear specific context types or all data.
    """
    try:
        # Convert string context types to enum
        context_type_enums = None
        if context_types:
            context_type_enums = []
            for ct in context_types:
                try:
                    context_type_enums.append(ContextType(ct))
                except ValueError:
                    logger.warning(f"Invalid context type: {ct}")
        
        cleared_count = await context_service.clear_user_context(
            user_id, context_type_enums
        )
        
        return {
            "message": f"Cleared {cleared_count} context entries for user {user_id}",
            "user_id": user_id,
            "context_types_cleared": context_types or ["all"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to clear context for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear context: {str(e)}"
        )


@router.delete("/conversations/{user_id}")
async def clear_user_conversations(
    user_id: str,
    context_service: ContextAwareService = Depends(get_context_aware_service)
):
    """
    Clear conversation history for a specific user.
    
    This endpoint allows users to clear their conversation history
    for privacy or to start fresh conversations.
    """
    try:
        # Clear conversation contexts only
        cleared_count = await context_service.clear_user_context(
            user_id, [ContextType.CONVERSATION]
        )
        
        return {
            "message": f"Cleared {cleared_count} conversations for user {user_id}",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to clear conversations for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear conversations: {str(e)}"
        )


@router.post("/maintenance/cleanup")
async def maintenance_cleanup(
    background_tasks: BackgroundTasks,
    context_service: ContextAwareService = Depends(get_context_aware_service)
):
    """
    Perform maintenance cleanup of old conversations, contexts, and cache.
    
    This endpoint triggers comprehensive cleanup of old conversation contexts,
    expired context entries, and cache to manage memory usage.
    """
    try:
        # Run cleanup in background
        background_tasks.add_task(context_service.llm_service.cleanup_old_conversations)
        background_tasks.add_task(context_service.llm_service.cleanup_old_cache)
        background_tasks.add_task(context_service.context_manager.cleanup_expired_contexts)
        
        return {
            "message": "Comprehensive maintenance cleanup initiated",
            "cleanup_tasks": ["conversations", "cache", "contexts"],
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Maintenance cleanup failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Maintenance cleanup failed: {str(e)}"
        )


@router.get("/context/statistics")
async def get_context_statistics(
    context_service: ContextAwareService = Depends(get_context_aware_service)
):
    """
    Get context management statistics.
    
    This endpoint provides detailed statistics about context usage,
    memory consumption, and system performance metrics.
    """
    try:
        stats = await context_service.context_manager.get_statistics()
        
        return {
            "context_statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get context statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get context statistics: {str(e)}"
        )