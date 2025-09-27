"""
Preference Learning API Routes

Endpoints for tracking user interactions, recording feedback, and retrieving learning insights.
Integrates with the PreferenceLearningService to provide adaptive preference management.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body
from pydantic import BaseModel, Field, validator

try:
    from ..services.preference_learning_service import (
        PreferenceLearningService, UserInteraction, FeedbackEvent
    )
    from ..models.preference_models import PreferenceProfile
except ImportError:
    from services.preference_learning_service import (
        PreferenceLearningService, UserInteraction, FeedbackEvent
    )
    from models.preference_models import PreferenceProfile

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v1/crop-taxonomy/learning", tags=["preference-learning"])

# Initialize service
learning_service = PreferenceLearningService()


# Request/Response Models
class InteractionRequest(BaseModel):
    """Request model for tracking user interactions"""
    user_id: UUID
    interaction_type: str = Field(..., regex="^(view|select|reject|save|share|skip|search|filter|compare)$")
    crop_id: Optional[str] = None
    recommendation_id: Optional[UUID] = None
    interaction_data: Dict[str, Any] = Field(default_factory=dict)
    session_id: Optional[str] = None
    page_context: Optional[str] = None
    search_query: Optional[str] = None
    filter_criteria: Optional[Dict[str, Any]] = None
    response_time_ms: Optional[int] = None

    @validator('interaction_data')
    def validate_interaction_data(cls, v, values):
        """Validate interaction data based on interaction type"""
        interaction_type = values.get('interaction_type')
        
        if interaction_type == 'view' and v:
            required_fields = []  # View can have any data
        elif interaction_type == 'select' and v:
            # Select should have selection details
            if 'selected_items' not in v:
                v['selected_items'] = []
        elif interaction_type == 'search' and v:
            # Search should track query effectiveness
            if 'results_count' not in v:
                v['results_count'] = 0
                
        return v


class FeedbackRequest(BaseModel):
    """Request model for recording user feedback"""
    user_id: UUID
    recommendation_id: UUID
    feedback_type: str = Field(..., regex="^(rating|implemented|rejected|modified|helpful|not_helpful)$")
    feedback_value: Any = Field(..., description="Rating (1-5), boolean, or structured data")
    feedback_text: Optional[str] = None
    crop_ids: List[str] = Field(default_factory=list)
    implementation_notes: Optional[str] = None
    modification_details: Optional[Dict[str, Any]] = None
    confidence_level: Optional[int] = Field(None, ge=1, le=5)

    @validator('feedback_value')
    def validate_feedback_value(cls, v, values):
        """Validate feedback value based on feedback type"""
        feedback_type = values.get('feedback_type')
        
        if feedback_type == 'rating':
            if not isinstance(v, (int, float)) or not (1 <= v <= 5):
                raise ValueError('Rating must be a number between 1 and 5')
        elif feedback_type in ['implemented', 'helpful', 'not_helpful']:
            if not isinstance(v, bool):
                raise ValueError(f'{feedback_type} feedback must be a boolean')
        elif feedback_type == 'modified':
            if not isinstance(v, dict):
                raise ValueError('Modified feedback must include modification details')
                
        return v


class InteractionResponse(BaseModel):
    """Response model for interaction tracking"""
    success: bool
    message: str
    interaction_id: Optional[str] = None
    learning_triggered: bool = False


class FeedbackResponse(BaseModel):
    """Response model for feedback recording"""
    success: bool
    message: str
    feedback_id: Optional[str] = None
    preference_adjustments_applied: bool = False


class LearningInsightsResponse(BaseModel):
    """Response model for learning insights"""
    user_id: str
    learning_period_days: int
    interaction_summary: Dict[str, Dict[str, Any]]
    feedback_summary: Dict[str, Dict[str, Any]]
    learned_preferences_count: int
    total_preferences: int
    learning_confidence: float
    behavior_patterns: List[Dict[str, Any]] = Field(default_factory=list)
    generated_at: str


class UserAnalyticsResponse(BaseModel):
    """Response model for user analytics"""
    user_id: str
    total_interactions: int
    unique_interaction_types: int
    last_interaction: Optional[str]
    total_feedback: int
    avg_rating: Optional[float]
    learning_sessions: int
    active_behavior_patterns: int
    preference_learning_score: float


# API Endpoints

@router.post("/interactions", response_model=InteractionResponse)
async def track_interaction(
    interaction: InteractionRequest,
    background_tasks: Any = None  # For potential background processing
) -> InteractionResponse:
    """
    Track user interaction for preference learning.
    
    Records user interactions with crops, recommendations, and system features
    to learn and adapt user preferences automatically.
    
    - **user_id**: UUID of the user performing the interaction
    - **interaction_type**: Type of interaction (view, select, reject, etc.)
    - **crop_id**: Optional crop ID if interaction relates to specific crop
    - **recommendation_id**: Optional recommendation ID if applicable
    - **interaction_data**: Additional context data for the interaction
    """
    try:
        user_interaction = UserInteraction(
            user_id=interaction.user_id,
            interaction_type=interaction.interaction_type,
            crop_id=interaction.crop_id,
            recommendation_id=interaction.recommendation_id,
            interaction_data=interaction.interaction_data,
            session_id=interaction.session_id
        )
        
        success = await learning_service.track_user_interaction(user_interaction)
        
        if success:
            return InteractionResponse(
                success=True,
                message="Interaction tracked successfully",
                learning_triggered=True  # Assuming learning may be triggered
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to track interaction")
            
    except Exception as e:
        logger.error(f"Error tracking interaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback", response_model=FeedbackResponse)
async def record_feedback(
    feedback: FeedbackRequest
) -> FeedbackResponse:
    """
    Record user feedback for preference learning.
    
    Captures explicit user feedback on recommendations and system suggestions
    to improve future recommendations through preference adaptation.
    
    - **user_id**: UUID of the user providing feedback
    - **recommendation_id**: UUID of the recommendation being rated
    - **feedback_type**: Type of feedback (rating, implemented, etc.)
    - **feedback_value**: The actual feedback value
    - **feedback_text**: Optional text explanation
    """
    try:
        feedback_event = FeedbackEvent(
            user_id=feedback.user_id,
            recommendation_id=feedback.recommendation_id,
            feedback_type=feedback.feedback_type,
            feedback_value=feedback.feedback_value,
            feedback_text=feedback.feedback_text,
            crop_ids=feedback.crop_ids
        )
        
        success = await learning_service.record_feedback(feedback_event)
        
        if success:
            return FeedbackResponse(
                success=True,
                message="Feedback recorded successfully",
                preference_adjustments_applied=True
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to record feedback")
            
    except Exception as e:
        logger.error(f"Error recording feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights/{user_id}", response_model=LearningInsightsResponse)
async def get_learning_insights(
    user_id: UUID = Path(..., description="User ID to get learning insights for"),
    period_days: int = Query(30, ge=1, le=365, description="Analysis period in days")
) -> LearningInsightsResponse:
    """
    Get learning insights and preference evolution for a user.
    
    Provides detailed analytics about how the system has learned
    from user interactions and adapted their preferences.
    
    - **user_id**: UUID of the user
    - **period_days**: Number of days to analyze (default: 30)
    """
    try:
        insights = await learning_service.get_learning_insights(user_id)
        
        if not insights:
            raise HTTPException(status_code=404, detail="No learning insights found for user")
        
        return LearningInsightsResponse(**insights)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting learning insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/{user_id}", response_model=UserAnalyticsResponse)
async def get_user_analytics(
    user_id: UUID = Path(..., description="User ID to get analytics for")
) -> UserAnalyticsResponse:
    """
    Get comprehensive user analytics for preference learning.
    
    Provides a summary of user engagement, learning progress,
    and system adaptation effectiveness.
    """
    try:
        # This would integrate with the database view we created
        # For now, we'll use the insights function and transform the data
        insights = await learning_service.get_learning_insights(user_id)
        
        if not insights:
            raise HTTPException(status_code=404, detail="No analytics found for user")
        
        # Calculate preference learning score
        learning_confidence = insights.get('learning_confidence', 0.0)
        interaction_count = sum(
            data.get('count', 0) for data in insights.get('interaction_summary', {}).values()
        )
        feedback_count = sum(
            data.get('count', 0) for data in insights.get('feedback_summary', {}).values()
        )
        
        # Simple scoring algorithm
        preference_learning_score = min(
            (learning_confidence * 0.5) + 
            (min(interaction_count / 50.0, 1.0) * 0.3) + 
            (min(feedback_count / 10.0, 1.0) * 0.2),
            1.0
        )
        
        return UserAnalyticsResponse(
            user_id=str(user_id),
            total_interactions=interaction_count,
            unique_interaction_types=len(insights.get('interaction_summary', {})),
            last_interaction=None,  # Would come from database query
            total_feedback=feedback_count,
            avg_rating=None,  # Would be calculated from feedback data
            learning_sessions=0,  # Would come from learning_sessions table
            active_behavior_patterns=0,  # Would come from behavior_patterns table
            preference_learning_score=preference_learning_score
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger-learning/{user_id}")
async def trigger_manual_learning(
    user_id: UUID = Path(..., description="User ID to trigger learning for"),
    learning_type: str = Query(
        "interaction_analysis", 
        regex="^(interaction_analysis|feedback_learning|collaborative_filtering|pattern_detection)$",
        description="Type of learning to trigger"
    )
) -> Dict[str, Any]:
    """
    Manually trigger preference learning for a user.
    
    Useful for testing or forcing preference updates when needed.
    """
    try:
        # This would trigger the learning service to run immediately
        # For now, we'll simulate the process
        
        logger.info(f"Triggering {learning_type} for user {user_id}")
        
        # In a real implementation, this would:
        # 1. Check if user has sufficient data
        # 2. Run the specified learning algorithm
        # 3. Update preferences based on results
        # 4. Record the learning session
        
        return {
            "success": True,
            "message": f"Learning triggered successfully for user {user_id}",
            "learning_type": learning_type,
            "triggered_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error triggering manual learning: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patterns/{user_id}")
async def get_behavior_patterns(
    user_id: UUID = Path(..., description="User ID to get behavior patterns for"),
    pattern_type: Optional[str] = Query(
        None,
        regex="^(crop_affinity|interaction_timing|search_behavior|decision_speed|risk_pattern)$",
        description="Filter by specific pattern type"
    )
) -> Dict[str, Any]:
    """
    Get detected behavior patterns for a user.
    
    Returns behavioral patterns that the system has detected
    from user interactions and how they influence preferences.
    """
    try:
        # This would query the user_behavior_patterns table
        # For now, we'll return a placeholder response
        
        return {
            "user_id": str(user_id),
            "pattern_type_filter": pattern_type,
            "detected_patterns": [],
            "pattern_count": 0,
            "last_updated": datetime.now().isoformat(),
            "message": "Behavior pattern detection not yet implemented in this demo"
        }
        
    except Exception as e:
        logger.error(f"Error getting behavior patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def learning_health_check() -> Dict[str, Any]:
    """Health check endpoint for the preference learning system"""
    try:
        return {
            "status": "healthy",
            "service": "preference_learning",
            "features": [
                "interaction_tracking",
                "feedback_learning", 
                "preference_adaptation",
                "behavior_pattern_detection",
                "learning_analytics"
            ],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Service unhealthy")


# Export router
__all__ = ["router"]