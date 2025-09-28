"""
Community and Collaborative Filtering Models

Pydantic models for community-driven crop filtering features.
Provides functionality for filter sharing, ratings, expert validation, and regional recommendations.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum


class FilterPresetStatus(str, Enum):
    """Status of a filter preset."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    EXPIRED = "expired"


class FilterPresetVisibility(str, Enum):
    """Visibility level of a filter preset."""
    PUBLIC = "public"
    PRIVATE = "private"
    SHARED = "shared"


class ExpertValidationStatus(str, Enum):
    """Validation status by expert."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"


class CommunityRating(BaseModel):
    """Rating given by a community member to a filter preset."""
    
    rating_id: Optional[UUID] = Field(None, description="Unique identifier for the rating")
    user_id: UUID = Field(..., description="User who provided the rating")
    preset_id: UUID = Field(..., description="Filter preset being rated")
    rating: int = Field(..., ge=1, le=5, description="Rating value (1-5 stars)")
    review_text: Optional[str] = Field(None, description="Optional review text")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of rating creation")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of last update")


class CommunityFilterPreset(BaseModel):
    """Community-driven filter preset with sharing and validation features."""
    
    preset_id: Optional[UUID] = Field(None, description="Unique identifier for the preset")
    creator_id: UUID = Field(..., description="User who created the preset")
    name: str = Field(..., min_length=1, max_length=200, description="Display name for the preset")
    description: Optional[str] = Field(None, description="Detailed description of the preset")
    filter_config: Dict[str, Any] = Field(..., description="The filter configuration")
    visibility: FilterPresetVisibility = Field(
        default=FilterPresetVisibility.PRIVATE, 
        description="Visibility level of the preset"
    )
    status: FilterPresetStatus = Field(
        default=FilterPresetStatus.DRAFT, 
        description="Status of the preset"
    )
    tags: List[str] = Field(default_factory=list, description="Tags for categorizing the preset")
    region_codes: List[str] = Field(default_factory=list, description="Region codes where preset is applicable")
    expert_validation_status: ExpertValidationStatus = Field(
        default=ExpertValidationStatus.PENDING, 
        description="Expert validation status"
    )
    expert_validated_by: Optional[UUID] = Field(None, description="Expert who validated the preset")
    expert_validation_date: Optional[datetime] = Field(None, description="Date of expert validation")
    expert_notes: Optional[str] = Field(None, description="Expert notes about validation")
    
    # Engagement metrics
    usage_count: int = Field(default=0, description="Number of times the preset has been used")
    rating_count: int = Field(default=0, description="Number of ratings received")
    average_rating: float = Field(default=0.0, ge=0.0, le=5.0, description="Average rating from community")
    share_count: int = Field(default=0, description="Number of shares")
    favorite_count: int = Field(default=0, description="Number of favorites/bookmarks")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    published_at: Optional[datetime] = Field(None, description="Publication timestamp")
    
    @validator('tags')
    def validate_tags(cls, v):
        """Validate tags list."""
        if v is None:
            return []
        # Limit to 10 tags and ensure each tag is not too long
        validated = [tag.strip()[:50] for tag in v if tag.strip()]
        return validated[:10]
    
    @validator('region_codes')
    def validate_region_codes(cls, v):
        """Validate region codes."""
        if v is None:
            return []
        # Simple validation - could be more specific based on actual region codes
        validated = []
        for code in v:
            if isinstance(code, str) and len(code) >= 2 and code.isalnum():
                validated.append(code.upper())
        return validated
    
    @validator('average_rating')
    def validate_rating(cls, v):
        """Validate average rating is within bounds."""
        if v is None:
            return 0.0
        return max(0.0, min(5.0, float(v)))


class FilterPresetShare(BaseModel):
    """Record of sharing a filter preset with another user or group."""
    
    share_id: Optional[UUID] = Field(None, description="Unique identifier for the share record")
    preset_id: UUID = Field(..., description="Filter preset being shared")
    shared_by_user_id: UUID = Field(..., description="User who shared the preset")
    shared_with_user_id: Optional[UUID] = Field(None, description="User who received the share")
    shared_with_group: Optional[str] = Field(None, description="Group the preset was shared with")
    share_message: Optional[str] = Field(None, description="Message sent with the share")
    permission_level: str = Field(default="view", description="Permission level ('view', 'edit', 'admin')")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of share")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp for the share")


class CommunityDiscussion(BaseModel):
    """Discussion thread associated with a filter preset."""
    
    discussion_id: Optional[UUID] = Field(None, description="Unique identifier for the discussion")
    preset_id: UUID = Field(..., description="Filter preset this discussion is about")
    title: str = Field(..., min_length=1, max_length=200, description="Discussion title")
    created_by_user_id: UUID = Field(..., description="User who started the discussion")
    is_pinned: bool = Field(default=False, description="Whether discussion is pinned")
    is_locked: bool = Field(default=False, description="Whether discussion is locked from new replies")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")


class CommunityComment(BaseModel):
    """Comment within a community discussion."""
    
    comment_id: Optional[UUID] = Field(None, description="Unique identifier for the comment")
    discussion_id: UUID = Field(..., description="Discussion this comment belongs to")
    parent_comment_id: Optional[UUID] = Field(None, description="Parent comment for nested replies")
    author_user_id: UUID = Field(..., description="User who authored the comment")
    content: str = Field(..., min_length=1, max_length=2000, description="Comment content")
    is_edited: bool = Field(default=False, description="Whether comment has been edited")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")


class CommunityRecommendation(BaseModel):
    """Community-driven recommendation based on collaborative filtering."""
    
    recommendation_id: Optional[UUID] = Field(None, description="Unique identifier for the recommendation")
    user_id: UUID = Field(..., description="User receiving the recommendation")
    preset_id: UUID = Field(..., description="Recommended filter preset")
    source_user_id: UUID = Field(..., description="User who created the original preset")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in recommendation")
    reason: str = Field(..., description="Reason for the recommendation")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


class FilterModerationReport(BaseModel):
    """Report of inappropriate content in community features."""
    
    report_id: Optional[UUID] = Field(None, description="Unique identifier for the report")
    reported_content_type: str = Field(..., description="Type of content being reported ('preset', 'comment', 'rating')")
    reported_content_id: UUID = Field(..., description="ID of the reported content")
    reporter_user_id: UUID = Field(..., description="User who filed the report")
    reason: str = Field(..., description="Reason for the report")
    additional_details: Optional[str] = Field(None, description="Additional details about the report")
    status: str = Field(default="pending", description="Status of the report ('pending', 'reviewed', 'resolved')")
    reviewed_by: Optional[UUID] = Field(None, description="Moderator who reviewed the report")
    reviewed_at: Optional[datetime] = Field(None, description="Time when report was reviewed")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    resolved_at: Optional[datetime] = Field(None, description="Time when report was resolved")


class RegionalFilterRecommendation(BaseModel):
    """Regional recommendation for filter presets."""
    
    recommendation_id: Optional[UUID] = Field(None, description="Unique identifier for the recommendation")
    region_code: str = Field(..., description="Region code for the recommendation")
    preset_id: UUID = Field(..., description="Recommended filter preset")
    popularity_score: float = Field(..., ge=0.0, le=1.0, description="Popularity score in the region")
    effectiveness_score: float = Field(..., ge=0.0, le=1.0, description="Effectiveness score in the region")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")


class ExpertValidation(BaseModel):
    """Expert validation of a filter preset."""
    
    validation_id: Optional[UUID] = Field(None, description="Unique identifier for the validation")
    preset_id: UUID = Field(..., description="Filter preset being validated")
    validated_by: UUID = Field(..., description="Expert who validated the preset")
    validation_status: ExpertValidationStatus = Field(..., description="Validation status")
    validation_notes: Optional[str] = Field(None, description="Expert's notes about validation")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")