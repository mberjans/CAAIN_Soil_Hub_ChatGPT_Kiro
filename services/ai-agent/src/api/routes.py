"""
API Routes for AFAS AI Agent Service

Provides endpoints for LLM interactions, question classification,
and agricultural explanations.
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

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1", tags=["ai-agent"])

# Global LLM service instance
llm_service: Optional[LLMService] = None


async def get_llm_service() -> LLMService:
    """Dependency to get LLM service instance."""
    global llm_service
    if llm_service is None:
        llm_service = create_llm_service()
        await llm_service.__aenter__()
    return llm_service


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
    timestamp: datetime = Field(default_factory=datetime.utcnow)


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
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Generate conversational response to user message.
    
    This endpoint provides conversational AI capabilities with agricultural
    context awareness and conversation history management.
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Generate response
        response = await llm_service.generate_response(
            user_id=request.user_id,
            session_id=session_id,
            message=request.message,
            agricultural_context=request.agricultural_context,
            use_case="conversation",
            stream=False
        )
        
        return ChatResponse(
            response=response.content,
            session_id=session_id,
            model_used=response.model,
            confidence_score=response.confidence_score,
            cost_estimate=response.cost_estimate,
            response_time=response.response_time,
            agricultural_metadata=response.agricultural_metadata
        )
        
    except Exception as e:
        logger.error(f"Chat response generation failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Chat response generation failed: {str(e)}"
        )


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Generate streaming conversational response to user message.
    
    This endpoint provides real-time streaming responses for better user experience
    during longer agricultural explanations and recommendations.
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        async def generate_stream():
            try:
                # Get conversation context
                context = await llm_service.get_conversation_context(
                    request.user_id, session_id
                )
                
                # Prepare messages
                messages = []
                for msg in context.conversation_history:
                    if msg.get("role") != "system":
                        messages.append(msg)
                
                messages.append({
                    "role": "user",
                    "content": request.message
                })
                
                # Create streaming request
                from ..services.openrouter_client import LLMRequest
                llm_request = LLMRequest(
                    messages=messages,
                    use_case="conversation",
                    stream=True,
                    agricultural_context=request.agricultural_context or context.agricultural_context
                )
                
                # Stream response
                full_response = ""
                async for chunk in llm_service.openrouter_client.stream_complete(llm_request):
                    full_response += chunk
                    yield f"data: {chunk}\n\n"
                
                # Update conversation context
                await llm_service.update_conversation_context(
                    context,
                    {"role": "user", "content": request.message},
                    full_response,
                    request.agricultural_context
                )
                
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"Streaming failed: {e}")
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
        logger.error(f"Chat streaming setup failed: {e}")
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
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Check service health and connectivity.
    
    This endpoint provides comprehensive health information including
    OpenRouter API connectivity and service metrics.
    """
    try:
        health_data = await llm_service.get_service_health()
        
        return HealthResponse(
            service=health_data["service"],
            status=health_data["status"],
            active_conversations=health_data["active_conversations"],
            cached_responses=health_data["cached_responses"],
            openrouter_status=health_data["openrouter_status"],
            timestamp=datetime.fromisoformat(health_data["timestamp"])
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )


@router.delete("/conversations/{user_id}")
async def clear_user_conversations(
    user_id: str,
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Clear conversation history for a specific user.
    
    This endpoint allows users to clear their conversation history
    for privacy or to start fresh conversations.
    """
    try:
        # Remove all conversations for the user
        to_remove = []
        for key in llm_service.active_conversations:
            if key.startswith(f"{user_id}:"):
                to_remove.append(key)
        
        for key in to_remove:
            del llm_service.active_conversations[key]
        
        return {
            "message": f"Cleared {len(to_remove)} conversations for user {user_id}",
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
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Perform maintenance cleanup of old conversations and cache.
    
    This endpoint triggers cleanup of old conversation contexts
    and expired cache entries to manage memory usage.
    """
    try:
        # Run cleanup in background
        background_tasks.add_task(llm_service.cleanup_old_conversations)
        background_tasks.add_task(llm_service.cleanup_old_cache)
        
        return {
            "message": "Maintenance cleanup initiated",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Maintenance cleanup failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Maintenance cleanup failed: {str(e)}"
        )