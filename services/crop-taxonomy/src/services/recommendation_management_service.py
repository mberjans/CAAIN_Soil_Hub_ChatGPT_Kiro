"""
Recommendation Management Service

Service layer for comprehensive recommendation management including
saving, tracking, feedback collection, and updating variety recommendations.
"""

import logging
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID, uuid4
from pydantic import ValidationError

try:
    from ..models.recommendation_management_models import (
        SavedVarietyRecommendation, RecommendationHistory, RecommendationFeedback,
        SaveRecommendationRequest, RecommendationHistoryRequest, RecommendationFeedbackRequest,
        UpdateRecommendationRequest, SaveRecommendationResponse, RecommendationHistoryResponse,
        RecommendationFeedbackResponse, UpdateRecommendationResponse, RecommendationAnalytics,
        RecommendationStatus, FeedbackType, RecommendationSource,
        RecommendationManagementValidator
    )
    from ..database.recommendation_management_db import recommendation_management_db
except ImportError:
    from models.recommendation_management_models import (
        SavedVarietyRecommendation, RecommendationHistory, RecommendationFeedback,
        SaveRecommendationRequest, RecommendationHistoryRequest, RecommendationFeedbackRequest,
        UpdateRecommendationRequest, SaveRecommendationResponse, RecommendationHistoryResponse,
        RecommendationFeedbackResponse, UpdateRecommendationResponse, RecommendationAnalytics,
        RecommendationStatus, FeedbackType, RecommendationSource,
        RecommendationManagementValidator
    )
    from database.recommendation_management_db import recommendation_management_db

logger = logging.getLogger(__name__)


class RecommendationManagementService:
    """Service for managing variety recommendations."""
    
    def __init__(self):
        """Initialize the recommendation management service."""
        self.db = recommendation_management_db
        self.validator = RecommendationManagementValidator()
    
    # ============================================================================
    # SAVE RECOMMENDATION OPERATIONS
    # ============================================================================
    
    async def save_recommendation(self, request: SaveRecommendationRequest) -> SaveRecommendationResponse:
        """
        Save a variety recommendation for a user.
        
        Args:
            request: Save recommendation request
            
        Returns:
            SaveRecommendationResponse with result details
        """
        try:
            # Validate input
            if not self.validator.validate_variety_ids(request.variety_ids):
                raise ValueError("Invalid variety IDs provided")
            
            if not self.validator.validate_recommendation_expiry(request.expires_at):
                raise ValueError("Expiry date must be in the future")
            
            # Save to database
            recommendation_id = self.db.save_recommendation(
                user_id=request.user_id,
                session_id=request.session_id,
                crop_id=request.crop_id,
                variety_ids=request.variety_ids,
                farm_context=request.farm_context,
                farmer_preferences=request.farmer_preferences,
                recommendation_criteria=request.recommendation_criteria,
                recommendation_source=request.recommendation_source.value,
                notes=request.notes,
                tags=request.tags,
                expires_at=request.expires_at,
                metadata=request.metadata
            )
            
            return SaveRecommendationResponse(
                success=True,
                recommendation_id=UUID(recommendation_id),
                message="Recommendation saved successfully",
                saved_varieties_count=len(request.variety_ids),
                expires_at=request.expires_at
            )
            
        except Exception as e:
            logger.error(f"Error saving recommendation: {e}")
            raise
    
    async def get_saved_recommendation(self, recommendation_id: str, user_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get a saved recommendation by ID.
        
        Args:
            recommendation_id: Recommendation ID
            user_id: User ID for authorization
            
        Returns:
            Recommendation data or None if not found
        """
        try:
            recommendation = self.db.get_recommendation(recommendation_id)
            
            if not recommendation:
                return None
            
            # Check user authorization
            if recommendation["user_id"] != str(user_id):
                raise PermissionError("User not authorized to access this recommendation")
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error getting saved recommendation: {e}")
            raise
    
    async def get_user_recommendations(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        crop_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get saved recommendations for a user.
        
        Args:
            user_id: User ID
            status: Optional status filter
            crop_id: Optional crop ID filter
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of saved recommendations
        """
        try:
            return self.db.get_user_recommendations(
                user_id=user_id,
                status=status,
                crop_id=crop_id,
                limit=limit,
                offset=offset
            )
            
        except Exception as e:
            logger.error(f"Error getting user recommendations: {e}")
            raise
    
    # ============================================================================
    # UPDATE RECOMMENDATION OPERATIONS
    # ============================================================================
    
    async def update_recommendation(self, request: UpdateRecommendationRequest) -> UpdateRecommendationResponse:
        """
        Update a saved recommendation.
        
        Args:
            request: Update recommendation request
            
        Returns:
            UpdateRecommendationResponse with result details
        """
        try:
            # Validate input
            if request.variety_ids and not self.validator.validate_variety_ids(request.variety_ids):
                raise ValueError("Invalid variety IDs provided")
            
            if request.expires_at and not self.validator.validate_recommendation_expiry(request.expires_at):
                raise ValueError("Expiry date must be in the future")
            
            # Prepare updates
            updates = {}
            updated_fields = []
            
            if request.variety_ids is not None:
                updates["variety_ids"] = request.variety_ids
                updated_fields.append("variety_ids")
            
            if request.farm_context is not None:
                updates["farm_context"] = request.farm_context
                updated_fields.append("farm_context")
            
            if request.farmer_preferences is not None:
                updates["farmer_preferences"] = request.farmer_preferences
                updated_fields.append("farmer_preferences")
            
            if request.recommendation_criteria is not None:
                updates["recommendation_criteria"] = request.recommendation_criteria
                updated_fields.append("recommendation_criteria")
            
            if request.status is not None:
                updates["status"] = request.status.value
                updated_fields.append("status")
            
            if request.notes is not None:
                updates["notes"] = request.notes
                updated_fields.append("notes")
            
            if request.tags is not None:
                updates["tags"] = request.tags
                updated_fields.append("tags")
            
            if request.expires_at is not None:
                updates["expires_at"] = request.expires_at
                updated_fields.append("expires_at")
            
            if request.metadata is not None:
                updates["metadata"] = request.metadata
                updated_fields.append("metadata")
            
            if not updates:
                raise ValueError("No updates provided")
            
            # Update in database
            success = self.db.update_recommendation(
                recommendation_id=str(request.recommendation_id),
                user_id=request.user_id,
                updates=updates
            )
            
            if not success:
                raise ValueError("Recommendation not found or user not authorized")
            
            # Handle re-ranking if requested
            new_variety_order = None
            if request.re_rank and request.variety_ids:
                # In a real implementation, this would call the recommendation engine
                # to re-rank varieties based on updated criteria
                new_variety_order = request.variety_ids
            
            return UpdateRecommendationResponse(
                success=True,
                recommendation_id=request.recommendation_id,
                message="Recommendation updated successfully",
                updated_fields=updated_fields,
                re_ranked=request.re_rank,
                new_variety_order=new_variety_order
            )
            
        except Exception as e:
            logger.error(f"Error updating recommendation: {e}")
            raise
    
    # ============================================================================
    # HISTORY OPERATIONS
    # ============================================================================
    
    async def get_recommendation_history(self, request: RecommendationHistoryRequest) -> RecommendationHistoryResponse:
        """
        Get recommendation history for a user.
        
        Args:
            request: History request parameters
            
        Returns:
            RecommendationHistoryResponse with history data
        """
        try:
            # Get history from database
            history_records, total_count = self.db.get_recommendation_history(
                user_id=request.user_id,
                start_date=request.start_date,
                end_date=request.end_date,
                action_types=request.action_types,
                crop_ids=request.crop_ids,
                limit=request.limit,
                offset=request.offset
            )
            
            # Calculate pagination info
            total_pages = (total_count + request.limit - 1) // request.limit
            current_page = (request.offset // request.limit) + 1
            
            pagination = {
                "total_records": total_count,
                "total_pages": total_pages,
                "current_page": current_page,
                "limit": request.limit,
                "offset": request.offset,
                "has_next": request.offset + request.limit < total_count,
                "has_previous": request.offset > 0
            }
            
            # Calculate summary statistics
            action_counts = {}
            crop_counts = {}
            
            for record in history_records:
                action_type = record["action_type"]
                action_counts[action_type] = action_counts.get(action_type, 0) + 1
                
                # Extract crop_id from action_data if available
                if "crop_id" in record.get("action_data", {}):
                    crop_id = record["action_data"]["crop_id"]
                    crop_counts[crop_id] = crop_counts.get(crop_id, 0) + 1
            
            summary_stats = {
                "action_counts": action_counts,
                "crop_counts": crop_counts,
                "date_range": {
                    "start": request.start_date.isoformat() if request.start_date else None,
                    "end": request.end_date.isoformat() if request.end_date else None
                }
            }
            
            return RecommendationHistoryResponse(
                user_id=request.user_id,
                total_records=total_count,
                records=[RecommendationHistory(**record) for record in history_records],
                pagination=pagination,
                summary_stats=summary_stats
            )
            
        except Exception as e:
            logger.error(f"Error getting recommendation history: {e}")
            raise
    
    # ============================================================================
    # FEEDBACK OPERATIONS
    # ============================================================================
    
    async def submit_feedback(self, request: RecommendationFeedbackRequest) -> RecommendationFeedbackResponse:
        """
        Submit feedback for a recommendation.
        
        Args:
            request: Feedback request
            
        Returns:
            RecommendationFeedbackResponse with result details
        """
        try:
            # Validate feedback value
            if not self.validator.validate_feedback_value(request.feedback_type, request.feedback_value):
                raise ValueError(f"Invalid feedback value for type {request.feedback_type}")
            
            # Submit feedback to database
            feedback_id = self.db.submit_feedback(
                recommendation_id=str(request.recommendation_id),
                user_id=request.user_id,
                feedback_type=request.feedback_type.value,
                feedback_value=request.feedback_value,
                feedback_text=request.feedback_text,
                variety_performance=request.variety_performance,
                implementation_notes=request.implementation_notes,
                modification_details=request.modification_details,
                confidence_level=request.confidence_level,
                metadata=request.metadata
            )
            
            # In a real implementation, this would trigger preference learning
            preference_adjustments_applied = await self._process_feedback_for_learning(
                request.user_id, request.recommendation_id, request.feedback_type, request.feedback_value
            )
            
            return RecommendationFeedbackResponse(
                success=True,
                feedback_id=UUID(feedback_id),
                message="Feedback submitted successfully",
                preference_adjustments_applied=preference_adjustments_applied,
                learning_triggered=preference_adjustments_applied
            )
            
        except Exception as e:
            logger.error(f"Error submitting feedback: {e}")
            raise
    
    async def get_recommendation_feedback(
        self,
        recommendation_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get feedback for a recommendation.
        
        Args:
            recommendation_id: Recommendation ID
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of feedback records
        """
        try:
            return self.db.get_recommendation_feedback(
                recommendation_id=recommendation_id,
                limit=limit,
                offset=offset
            )
            
        except Exception as e:
            logger.error(f"Error getting recommendation feedback: {e}")
            raise
    
    # ============================================================================
    # ANALYTICS OPERATIONS
    # ============================================================================
    
    async def get_recommendation_analytics(self, user_id: UUID) -> RecommendationAnalytics:
        """
        Get analytics for a user's recommendations.
        
        Args:
            user_id: User ID
            
        Returns:
            RecommendationAnalytics with user statistics
        """
        try:
            analytics_data = self.db.get_recommendation_analytics(user_id)
            
            return RecommendationAnalytics(
                user_id=user_id,
                total_recommendations=analytics_data["total_recommendations"],
                active_recommendations=analytics_data["active_recommendations"],
                implemented_recommendations=analytics_data["implemented_recommendations"],
                feedback_count=analytics_data["feedback_count"],
                average_rating=analytics_data["average_rating"],
                most_common_crops=analytics_data["most_common_crops"],
                recommendation_trends={},  # Would be calculated from historical data
                performance_insights={}  # Would be calculated from feedback data
            )
            
        except Exception as e:
            logger.error(f"Error getting recommendation analytics: {e}")
            raise
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    async def _process_feedback_for_learning(
        self,
        user_id: UUID,
        recommendation_id: str,
        feedback_type: FeedbackType,
        feedback_value: Any
    ) -> bool:
        """
        Process feedback for preference learning.
        
        Args:
            user_id: User ID
            recommendation_id: Recommendation ID
            feedback_type: Type of feedback
            feedback_value: Feedback value
            
        Returns:
            Whether preference adjustments were applied
        """
        try:
            # In a real implementation, this would:
            # 1. Analyze the feedback
            # 2. Update user preferences based on feedback
            # 3. Trigger recommendation engine retraining
            # 4. Log learning events
            
            logger.info(f"Processing feedback for learning: user={user_id}, type={feedback_type}")
            
            # For now, return True to indicate learning was triggered
            return True
            
        except Exception as e:
            logger.error(f"Error processing feedback for learning: {e}")
            return False
    
    async def cleanup_expired_recommendations(self) -> int:
        """
        Clean up expired recommendations.
        
        Returns:
            Number of recommendations cleaned up
        """
        try:
            # This would implement cleanup logic for expired recommendations
            # For now, return 0 as no cleanup is implemented
            return 0
            
        except Exception as e:
            logger.error(f"Error cleaning up expired recommendations: {e}")
            return 0
    
    async def get_recommendation_statistics(self) -> Dict[str, Any]:
        """
        Get system-wide recommendation statistics.
        
        Returns:
            Dictionary with system statistics
        """
        try:
            # This would implement system-wide statistics
            # For now, return basic structure
            return {
                "total_recommendations": 0,
                "active_recommendations": 0,
                "total_feedback": 0,
                "average_rating": None,
                "most_popular_crops": [],
                "system_health": "healthy"
            }
            
        except Exception as e:
            logger.error(f"Error getting recommendation statistics: {e}")
            raise


# Create a singleton instance for easy import
recommendation_management_service = RecommendationManagementService()