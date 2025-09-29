"""
Recommendation Management Models

Pydantic models for comprehensive recommendation management system including
saving, tracking, feedback collection, and updating variety recommendations.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from enum import Enum
from uuid import UUID


# ============================================================================
# RECOMMENDATION MANAGEMENT ENUMERATIONS
# ============================================================================

class RecommendationStatus(str, Enum):
    """Status of saved recommendations."""
    ACTIVE = "active"
    IMPLEMENTED = "implemented"
    REJECTED = "rejected"
    MODIFIED = "modified"
    EXPIRED = "expired"


class FeedbackType(str, Enum):
    """Types of feedback that can be provided."""
    RATING = "rating"
    IMPLEMENTED = "implemented"
    REJECTED = "rejected"
    MODIFIED = "modified"
    HELPFUL = "helpful"
    NOT_HELPFUL = "not_helpful"
    OUTCOME = "outcome"


class RecommendationSource(str, Enum):
    """Source of the recommendation."""
    SYSTEM_GENERATED = "system_generated"
    USER_REQUESTED = "user_requested"
    EXPERT_REVIEWED = "expert_reviewed"
    COMMUNITY_SHARED = "community_shared"


# ============================================================================
# CORE RECOMMENDATION MODELS
# ============================================================================

class SavedVarietyRecommendation(BaseModel):
    """Model for saved variety recommendations."""
    
    recommendation_id: UUID = Field(..., description="Unique recommendation identifier")
    user_id: UUID = Field(..., description="User who saved the recommendation")
    session_id: Optional[str] = Field(None, description="Session identifier")
    crop_id: str = Field(..., description="Crop identifier")
    variety_ids: List[str] = Field(..., description="List of recommended variety IDs")
    farm_context: Dict[str, Any] = Field(..., description="Farm context when recommendation was made")
    farmer_preferences: Dict[str, Any] = Field(..., description="Farmer preferences used")
    recommendation_criteria: Dict[str, Any] = Field(..., description="Criteria used for recommendation")
    recommendation_source: RecommendationSource = Field(..., description="Source of recommendation")
    status: RecommendationStatus = Field(default=RecommendationStatus.ACTIVE, description="Current status")
    saved_at: datetime = Field(default_factory=datetime.utcnow, description="When recommendation was saved")
    expires_at: Optional[datetime] = Field(None, description="When recommendation expires")
    notes: Optional[str] = Field(None, description="User notes about the recommendation")
    tags: List[str] = Field(default_factory=list, description="User-defined tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class RecommendationHistory(BaseModel):
    """Model for recommendation history tracking."""
    
    history_id: UUID = Field(..., description="Unique history identifier")
    recommendation_id: UUID = Field(..., description="Related recommendation ID")
    user_id: UUID = Field(..., description="User ID")
    action_type: str = Field(..., description="Action taken (view, save, implement, etc.)")
    action_timestamp: datetime = Field(default_factory=datetime.utcnow, description="When action occurred")
    action_data: Dict[str, Any] = Field(default_factory=dict, description="Data related to the action")
    session_context: Optional[Dict[str, Any]] = Field(None, description="Session context")
    ip_address: Optional[str] = Field(None, description="IP address for tracking")
    user_agent: Optional[str] = Field(None, description="User agent string")


class RecommendationFeedback(BaseModel):
    """Model for recommendation feedback."""
    
    feedback_id: UUID = Field(..., description="Unique feedback identifier")
    recommendation_id: UUID = Field(..., description="Related recommendation ID")
    user_id: UUID = Field(..., description="User providing feedback")
    feedback_type: FeedbackType = Field(..., description="Type of feedback")
    feedback_value: Union[int, float, bool, str, Dict[str, Any]] = Field(..., description="Feedback value")
    feedback_text: Optional[str] = Field(None, description="Text explanation of feedback")
    variety_performance: Optional[Dict[str, Any]] = Field(None, description="Performance data for varieties")
    implementation_notes: Optional[str] = Field(None, description="Notes about implementation")
    modification_details: Optional[Dict[str, Any]] = Field(None, description="Details of modifications made")
    confidence_level: Optional[int] = Field(None, ge=1, le=5, description="Confidence in feedback")
    submitted_at: datetime = Field(default_factory=datetime.utcnow, description="When feedback was submitted")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional feedback metadata")


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class SaveRecommendationRequest(BaseModel):
    """Request model for saving variety recommendations."""
    
    user_id: UUID = Field(..., description="User ID")
    session_id: Optional[str] = Field(None, description="Session identifier")
    crop_id: str = Field(..., description="Crop identifier")
    variety_ids: List[str] = Field(..., min_items=1, description="List of variety IDs to save")
    farm_context: Dict[str, Any] = Field(..., description="Farm context")
    farmer_preferences: Dict[str, Any] = Field(..., description="Farmer preferences")
    recommendation_criteria: Dict[str, Any] = Field(..., description="Recommendation criteria")
    recommendation_source: RecommendationSource = Field(default=RecommendationSource.SYSTEM_GENERATED, description="Source")
    notes: Optional[str] = Field(None, description="User notes")
    tags: List[str] = Field(default_factory=list, description="User tags")
    expires_at: Optional[datetime] = Field(None, description="Expiration date")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class RecommendationHistoryRequest(BaseModel):
    """Request model for retrieving recommendation history."""
    
    user_id: UUID = Field(..., description="User ID")
    start_date: Optional[date] = Field(None, description="Start date for history")
    end_date: Optional[date] = Field(None, description="End date for history")
    action_types: Optional[List[str]] = Field(None, description="Filter by action types")
    crop_ids: Optional[List[str]] = Field(None, description="Filter by crop IDs")
    limit: int = Field(default=50, ge=1, le=500, description="Maximum number of records")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")


class RecommendationFeedbackRequest(BaseModel):
    """Request model for submitting recommendation feedback."""
    
    user_id: UUID = Field(..., description="User ID")
    recommendation_id: UUID = Field(..., description="Recommendation ID")
    feedback_type: FeedbackType = Field(..., description="Type of feedback")
    feedback_value: Union[int, float, bool, str, Dict[str, Any]] = Field(..., description="Feedback value")
    feedback_text: Optional[str] = Field(None, description="Text explanation")
    variety_performance: Optional[Dict[str, Any]] = Field(None, description="Performance data")
    implementation_notes: Optional[str] = Field(None, description="Implementation notes")
    modification_details: Optional[Dict[str, Any]] = Field(None, description="Modification details")
    confidence_level: Optional[int] = Field(None, ge=1, le=5, description="Confidence level")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class UpdateRecommendationRequest(BaseModel):
    """Request model for updating saved recommendations."""
    
    user_id: UUID = Field(..., description="User ID")
    recommendation_id: UUID = Field(..., description="Recommendation ID to update")
    variety_ids: Optional[List[str]] = Field(None, description="Updated variety IDs")
    farm_context: Optional[Dict[str, Any]] = Field(None, description="Updated farm context")
    farmer_preferences: Optional[Dict[str, Any]] = Field(None, description="Updated preferences")
    recommendation_criteria: Optional[Dict[str, Any]] = Field(None, description="Updated criteria")
    status: Optional[RecommendationStatus] = Field(None, description="Updated status")
    notes: Optional[str] = Field(None, description="Updated notes")
    tags: Optional[List[str]] = Field(None, description="Updated tags")
    expires_at: Optional[datetime] = Field(None, description="Updated expiration")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")
    re_rank: bool = Field(default=False, description="Whether to re-rank varieties")


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class SaveRecommendationResponse(BaseModel):
    """Response model for saving recommendations."""
    
    success: bool = Field(..., description="Whether operation was successful")
    recommendation_id: UUID = Field(..., description="ID of saved recommendation")
    message: str = Field(..., description="Response message")
    saved_varieties_count: int = Field(..., description="Number of varieties saved")
    expires_at: Optional[datetime] = Field(None, description="Expiration date")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


class RecommendationHistoryResponse(BaseModel):
    """Response model for recommendation history."""
    
    user_id: UUID = Field(..., description="User ID")
    total_records: int = Field(..., description="Total number of records")
    records: List[RecommendationHistory] = Field(..., description="History records")
    pagination: Dict[str, Any] = Field(..., description="Pagination information")
    summary_stats: Dict[str, Any] = Field(..., description="Summary statistics")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class RecommendationFeedbackResponse(BaseModel):
    """Response model for feedback submission."""
    
    success: bool = Field(..., description="Whether operation was successful")
    feedback_id: UUID = Field(..., description="ID of submitted feedback")
    message: str = Field(..., description="Response message")
    preference_adjustments_applied: bool = Field(default=False, description="Whether preferences were updated")
    learning_triggered: bool = Field(default=False, description="Whether learning was triggered")
    submitted_at: datetime = Field(default_factory=datetime.utcnow, description="Submission timestamp")


class UpdateRecommendationResponse(BaseModel):
    """Response model for updating recommendations."""
    
    success: bool = Field(..., description="Whether operation was successful")
    recommendation_id: UUID = Field(..., description="Updated recommendation ID")
    message: str = Field(..., description="Response message")
    updated_fields: List[str] = Field(..., description="List of updated fields")
    re_ranked: bool = Field(default=False, description="Whether varieties were re-ranked")
    new_variety_order: Optional[List[str]] = Field(None, description="New variety order if re-ranked")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Update timestamp")


class RecommendationAnalytics(BaseModel):
    """Model for recommendation analytics and insights."""
    
    user_id: UUID = Field(..., description="User ID")
    total_recommendations: int = Field(..., description="Total recommendations saved")
    active_recommendations: int = Field(..., description="Currently active recommendations")
    implemented_recommendations: int = Field(..., description="Implemented recommendations")
    feedback_count: int = Field(..., description="Total feedback submissions")
    average_rating: Optional[float] = Field(None, description="Average feedback rating")
    most_common_crops: List[Dict[str, Any]] = Field(default_factory=list, description="Most common crops")
    recommendation_trends: Dict[str, Any] = Field(default_factory=dict, description="Trend analysis")
    performance_insights: Dict[str, Any] = Field(default_factory=dict, description="Performance insights")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")


# ============================================================================
# VALIDATION METHODS
# ============================================================================

class RecommendationManagementValidator:
    """Validator class for recommendation management operations."""
    
    @staticmethod
    def validate_feedback_value(feedback_type: FeedbackType, feedback_value: Any) -> bool:
        """Validate feedback value based on feedback type."""
        if feedback_type == FeedbackType.RATING:
            return isinstance(feedback_value, (int, float)) and 1 <= feedback_value <= 5
        elif feedback_type in [FeedbackType.IMPLEMENTED, FeedbackType.HELPFUL, FeedbackType.NOT_HELPFUL]:
            return isinstance(feedback_value, bool)
        elif feedback_type == FeedbackType.MODIFIED:
            return isinstance(feedback_value, dict)
        elif feedback_type == FeedbackType.OUTCOME:
            return isinstance(feedback_value, (str, dict))
        return True
    
    @staticmethod
    def validate_recommendation_expiry(expires_at: Optional[datetime]) -> bool:
        """Validate that expiry date is in the future."""
        if expires_at is None:
            return True
        return expires_at > datetime.utcnow()
    
    @staticmethod
    def validate_variety_ids(variety_ids: List[str]) -> bool:
        """Validate variety IDs format."""
        if not variety_ids:
            return False
        # Basic validation - variety IDs should be non-empty strings
        return all(isinstance(vid, str) and len(vid.strip()) > 0 for vid in variety_ids)