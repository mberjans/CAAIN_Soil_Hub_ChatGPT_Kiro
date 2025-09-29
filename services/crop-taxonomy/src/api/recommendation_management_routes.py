"""
Recommendation Management API Routes

API endpoints for comprehensive recommendation management including
saving, tracking, feedback collection, and updating variety recommendations.
"""

import logging
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body, status
from pydantic import ValidationError

try:
    from ..models.recommendation_management_models import (
        SaveRecommendationRequest, RecommendationHistoryRequest, RecommendationFeedbackRequest,
        UpdateRecommendationRequest, SaveRecommendationResponse, RecommendationHistoryResponse,
        RecommendationFeedbackResponse, UpdateRecommendationResponse, RecommendationAnalytics
    )
    from ..services.recommendation_management_service import recommendation_management_service
except ImportError:
    from models.recommendation_management_models import (
        SaveRecommendationRequest, RecommendationHistoryRequest, RecommendationFeedbackRequest,
        UpdateRecommendationRequest, SaveRecommendationResponse, RecommendationHistoryResponse,
        RecommendationFeedbackResponse, UpdateRecommendationResponse, RecommendationAnalytics
    )
    from services.recommendation_management_service import recommendation_management_service

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v1/recommendations/variety", tags=["recommendation-management"])


# ============================================================================
# SAVE RECOMMENDATION ENDPOINTS
# ============================================================================

@router.post("/save", response_model=SaveRecommendationResponse, status_code=status.HTTP_201_CREATED)
async def save_variety_recommendation(
    request: SaveRecommendationRequest
) -> SaveRecommendationResponse:
    """
    Save variety recommendations for future reference.
    
    Allows users to save variety recommendations from the recommendation engine
    for later review, implementation, or sharing. Saved recommendations include
    the full context of the recommendation including farm conditions, preferences,
    and criteria used.
    
    **Features:**
    - Save complete recommendation context
    - Add user notes and tags
    - Set expiration dates
    - Track recommendation source
    - Automatic history logging
    
    **Use Cases:**
    - Bookmark promising variety recommendations
    - Save recommendations for different field conditions
    - Create variety lists for different seasons
    - Share recommendations with team members
    
    **Request Body:**
    - **user_id**: UUID of the user saving the recommendation
    - **crop_id**: Identifier for the crop type
    - **variety_ids**: List of recommended variety IDs
    - **farm_context**: Farm conditions and context
    - **farmer_preferences**: User preferences used in recommendation
    - **recommendation_criteria**: Criteria used for recommendation
    - **notes**: Optional user notes
    - **tags**: Optional user-defined tags
    - **expires_at**: Optional expiration date
    """
    try:
        result = await recommendation_management_service.save_recommendation(request)
        return result
        
    except ValidationError as e:
        logger.error(f"Validation error saving recommendation: {e}")
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except ValueError as e:
        logger.error(f"Value error saving recommendation: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error saving recommendation: {e}")
        raise HTTPException(status_code=500, detail="Failed to save recommendation")


@router.get("/saved/{user_id}", response_model=List[Dict[str, Any]])
async def get_saved_recommendations(
    user_id: UUID = Path(..., description="User ID to get saved recommendations for"),
    status: Optional[str] = Query(None, description="Filter by recommendation status"),
    crop_id: Optional[str] = Query(None, description="Filter by crop ID"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
) -> List[Dict[str, Any]]:
    """
    Get saved recommendations for a user.
    
    Retrieves all saved variety recommendations for a specific user with optional
    filtering by status, crop type, and pagination support.
    
    **Features:**
    - Filter by recommendation status (active, implemented, rejected, etc.)
    - Filter by crop type
    - Pagination support
    - Complete recommendation context
    
    **Use Cases:**
    - Review previously saved recommendations
    - Find recommendations for specific crops
    - Check status of saved recommendations
    - Browse recommendation history
    """
    try:
        recommendations = await recommendation_management_service.get_user_recommendations(
            user_id=user_id,
            status=status,
            crop_id=crop_id,
            limit=limit,
            offset=offset
        )
        return recommendations
        
    except Exception as e:
        logger.error(f"Error getting saved recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get saved recommendations")


@router.get("/saved/{user_id}/{recommendation_id}", response_model=Dict[str, Any])
async def get_saved_recommendation(
    user_id: UUID = Path(..., description="User ID"),
    recommendation_id: str = Path(..., description="Recommendation ID")
) -> Dict[str, Any]:
    """
    Get a specific saved recommendation.
    
    Retrieves a single saved recommendation by ID with full context and details.
    Users can only access their own recommendations.
    
    **Features:**
    - Complete recommendation details
    - User authorization check
    - Full context and metadata
    
    **Use Cases:**
    - Review specific recommendation details
    - Access recommendation for updates
    - Share recommendation with others
    """
    try:
        recommendation = await recommendation_management_service.get_saved_recommendation(
            recommendation_id=recommendation_id,
            user_id=user_id
        )
        
        if not recommendation:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        
        return recommendation
        
    except PermissionError as e:
        logger.error(f"Permission error getting recommendation: {e}")
        raise HTTPException(status_code=403, detail="Access denied")
    except Exception as e:
        logger.error(f"Error getting saved recommendation: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recommendation")


# ============================================================================
# HISTORY TRACKING ENDPOINTS
# ============================================================================

@router.get("/history", response_model=RecommendationHistoryResponse)
async def get_recommendation_history(
    user_id: UUID = Query(..., description="User ID to get history for"),
    start_date: Optional[date] = Query(None, description="Start date for history (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date for history (YYYY-MM-DD)"),
    action_types: Optional[str] = Query(None, description="Comma-separated action types to filter"),
    crop_ids: Optional[str] = Query(None, description="Comma-separated crop IDs to filter"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
) -> RecommendationHistoryResponse:
    """
    Get recommendation history and tracking data.
    
    Provides comprehensive historical tracking of user interactions with recommendations
    including views, saves, implementations, and feedback. Includes analytics and
    summary statistics.
    
    **Features:**
    - Complete interaction history
    - Date range filtering
    - Action type filtering
    - Crop-specific filtering
    - Pagination support
    - Summary statistics
    - Performance analytics
    
    **Use Cases:**
    - Track recommendation usage patterns
    - Analyze user engagement
    - Monitor implementation success
    - Generate usage reports
    - Identify popular recommendations
    
    **Response Includes:**
    - Historical interaction records
    - Action counts and summaries
    - Crop popularity analysis
    - Pagination information
    - Date range statistics
    """
    try:
        # Parse comma-separated parameters
        action_types_list = action_types.split(",") if action_types else None
        crop_ids_list = crop_ids.split(",") if crop_ids else None
        
        request = RecommendationHistoryRequest(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            action_types=action_types_list,
            crop_ids=crop_ids_list,
            limit=limit,
            offset=offset
        )
        
        result = await recommendation_management_service.get_recommendation_history(request)
        return result
        
    except ValidationError as e:
        logger.error(f"Validation error getting history: {e}")
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except Exception as e:
        logger.error(f"Error getting recommendation history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recommendation history")


# ============================================================================
# FEEDBACK ENDPOINTS
# ============================================================================

@router.post("/feedback", response_model=RecommendationFeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_recommendation_feedback(
    request: RecommendationFeedbackRequest
) -> RecommendationFeedbackResponse:
    """
    Submit feedback on variety recommendations.
    
    Allows users to provide feedback on recommendations they have received or
    implemented. Feedback is used to improve future recommendations through
    machine learning and preference adaptation.
    
    **Feedback Types:**
    - **rating**: Numerical rating (1-5 scale)
    - **implemented**: Boolean indicating if recommendation was implemented
    - **rejected**: Boolean indicating if recommendation was rejected
    - **modified**: Details of modifications made to recommendation
    - **helpful/not_helpful**: Boolean feedback on recommendation usefulness
    - **outcome**: Detailed outcome information
    
    **Features:**
    - Multiple feedback types supported
    - Performance data collection
    - Implementation notes
    - Modification tracking
    - Confidence scoring
    - Automatic preference learning
    
    **Use Cases:**
    - Rate recommendation quality
    - Report implementation results
    - Provide outcome data
    - Improve system recommendations
    - Track variety performance
    """
    try:
        result = await recommendation_management_service.submit_feedback(request)
        return result
        
    except ValidationError as e:
        logger.error(f"Validation error submitting feedback: {e}")
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except ValueError as e:
        logger.error(f"Value error submitting feedback: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")


@router.get("/feedback/{recommendation_id}", response_model=List[Dict[str, Any]])
async def get_recommendation_feedback(
    recommendation_id: str = Path(..., description="Recommendation ID to get feedback for"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
) -> List[Dict[str, Any]]:
    """
    Get feedback for a specific recommendation.
    
    Retrieves all feedback submitted for a particular recommendation,
    useful for analyzing recommendation performance and user satisfaction.
    
    **Features:**
    - Complete feedback history
    - Multiple feedback types
    - Performance data
    - Implementation notes
    - Pagination support
    
    **Use Cases:**
    - Analyze recommendation performance
    - Review user feedback
    - Track implementation outcomes
    - Generate recommendation reports
    """
    try:
        feedback = await recommendation_management_service.get_recommendation_feedback(
            recommendation_id=recommendation_id,
            limit=limit,
            offset=offset
        )
        return feedback
        
    except Exception as e:
        logger.error(f"Error getting recommendation feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recommendation feedback")


# ============================================================================
# UPDATE RECOMMENDATION ENDPOINTS
# ============================================================================

@router.put("/{recommendation_id}/update", response_model=UpdateRecommendationResponse)
async def update_saved_recommendation(
    recommendation_id: str = Path(..., description="Recommendation ID to update"),
    request: UpdateRecommendationRequest = Body(..., description="Update request")
) -> UpdateRecommendationResponse:
    """
    Update a saved variety recommendation.
    
    Allows users to modify saved recommendations with new data, preferences,
    or criteria. Supports re-ranking varieties based on updated information.
    
    **Updateable Fields:**
    - **variety_ids**: Updated list of variety IDs
    - **farm_context**: Updated farm conditions
    - **farmer_preferences**: Updated user preferences
    - **recommendation_criteria**: Updated criteria
    - **status**: Updated recommendation status
    - **notes**: Updated user notes
    - **tags**: Updated user tags
    - **expires_at**: Updated expiration date
    - **metadata**: Updated metadata
    
    **Features:**
    - Selective field updates
    - Automatic re-ranking option
    - User authorization check
    - Change tracking
    - History logging
    
    **Use Cases:**
    - Update farm conditions
    - Modify preferences
    - Add implementation notes
    - Change recommendation status
    - Re-rank varieties with new criteria
    """
    try:
        # Set the recommendation_id from the path
        request.recommendation_id = UUID(recommendation_id)
        
        result = await recommendation_management_service.update_recommendation(request)
        return result
        
    except ValidationError as e:
        logger.error(f"Validation error updating recommendation: {e}")
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except ValueError as e:
        logger.error(f"Value error updating recommendation: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating recommendation: {e}")
        raise HTTPException(status_code=500, detail="Failed to update recommendation")


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@router.get("/analytics/{user_id}", response_model=RecommendationAnalytics)
async def get_recommendation_analytics(
    user_id: UUID = Path(..., description="User ID to get analytics for")
) -> RecommendationAnalytics:
    """
    Get comprehensive analytics for user recommendations.
    
    Provides detailed analytics and insights about a user's recommendation
    usage, performance, and patterns. Includes statistics, trends, and
    performance insights.
    
    **Analytics Include:**
    - Total recommendations saved
    - Active vs implemented recommendations
    - Feedback statistics
    - Average ratings
    - Most common crops
    - Recommendation trends
    - Performance insights
    
    **Use Cases:**
    - Track recommendation usage
    - Analyze success patterns
    - Identify popular crops
    - Monitor feedback trends
    - Generate user reports
    """
    try:
        analytics = await recommendation_management_service.get_recommendation_analytics(user_id)
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting recommendation analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recommendation analytics")


# ============================================================================
# SYSTEM ENDPOINTS
# ============================================================================

@router.get("/statistics", response_model=Dict[str, Any])
async def get_system_statistics() -> Dict[str, Any]:
    """
    Get system-wide recommendation statistics.
    
    Provides system-level statistics about recommendation usage,
    performance, and health across all users.
    
    **Statistics Include:**
    - Total recommendations system-wide
    - Active recommendations count
    - Total feedback submissions
    - Average system rating
    - Most popular crops
    - System health status
    
    **Use Cases:**
    - Monitor system performance
    - Track overall usage
    - Identify popular crops
    - System health monitoring
    """
    try:
        statistics = await recommendation_management_service.get_recommendation_statistics()
        return statistics
        
    except Exception as e:
        logger.error(f"Error getting system statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system statistics")


@router.post("/cleanup", response_model=Dict[str, Any])
async def cleanup_expired_recommendations() -> Dict[str, Any]:
    """
    Clean up expired recommendations.
    
    Removes expired recommendations from the system to maintain
    data quality and performance.
    
    **Features:**
    - Automatic expiration handling
    - Data cleanup
    - Performance optimization
    - Cleanup reporting
    
    **Use Cases:**
    - System maintenance
    - Data cleanup
    - Performance optimization
    """
    try:
        cleaned_count = await recommendation_management_service.cleanup_expired_recommendations()
        
        return {
            "success": True,
            "message": f"Cleanup completed successfully",
            "cleaned_recommendations": cleaned_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up expired recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to cleanup expired recommendations")


@router.get("/health")
async def recommendation_management_health_check() -> Dict[str, Any]:
    """
    Health check endpoint for recommendation management system.
    
    Provides system health status and feature availability.
    """
    try:
        return {
            "status": "healthy",
            "service": "recommendation_management",
            "features": [
                "save_recommendations",
                "recommendation_history",
                "feedback_collection",
                "recommendation_updates",
                "analytics",
                "system_statistics"
            ],
            "database_connected": recommendation_management_service.db.test_connection(),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Service unhealthy")


# Export router
__all__ = ["router"]