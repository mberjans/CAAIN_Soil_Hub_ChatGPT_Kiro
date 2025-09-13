"""
Question Router API Routes

FastAPI routes for question processing and routing.
"""

import uuid
from fastapi import APIRouter, HTTPException, Depends
from typing import List

try:
    from ..models.question_models import (
        QuestionRequest, 
        QuestionResponse, 
        QuestionType,
        ClassificationResult,
        RoutingDecision
    )
    from ..services.classification_service import QuestionClassificationService
    from ..services.routing_service import QuestionRoutingService
except ImportError:
    from models.question_models import (
        QuestionRequest, 
        QuestionResponse, 
        QuestionType,
        ClassificationResult,
        RoutingDecision
    )
    from services.classification_service import QuestionClassificationService
    from services.routing_service import QuestionRoutingService

router = APIRouter(prefix="/api/v1", tags=["question-router"])

# Service dependencies
classification_service = QuestionClassificationService()
routing_service = QuestionRoutingService()


@router.post("/questions/classify", response_model=QuestionResponse)
async def classify_and_route_question(request: QuestionRequest):
    """
    Classify a farmer's question and determine routing.
    
    This endpoint processes natural language questions from farmers and:
    1. Classifies the question into one of 20 key question types
    2. Determines which microservices should handle the question
    3. Returns routing information for downstream processing
    """
    try:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Classify the question
        classification = await classification_service.classify_question(request.question_text)
        
        # Determine routing
        routing = await routing_service.route_question(classification.question_type)
        
        return QuestionResponse(
            request_id=request_id,
            classification=classification,
            routing=routing,
            status="routed"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )


@router.get("/questions/types", response_model=List[str])
async def get_question_types():
    """
    Get list of supported question types.
    
    Returns all 20 key farmer question types that the system can handle.
    """
    return [qtype.value for qtype in QuestionType]


@router.post("/questions/classify-only", response_model=ClassificationResult)
async def classify_question_only(request: QuestionRequest):
    """
    Classify a question without routing (for testing/debugging).
    
    This endpoint only performs question classification without determining
    routing information. Useful for testing classification accuracy.
    """
    try:
        classification = await classification_service.classify_question(request.question_text)
        return classification
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error classifying question: {str(e)}"
        )


@router.post("/questions/route-only", response_model=RoutingDecision)
async def route_question_type(question_type: QuestionType):
    """
    Get routing information for a specific question type.
    
    This endpoint returns routing information for a given question type
    without performing classification. Useful for testing routing logic.
    """
    try:
        routing = await routing_service.route_question(question_type)
        return routing
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error routing question type: {str(e)}"
        )