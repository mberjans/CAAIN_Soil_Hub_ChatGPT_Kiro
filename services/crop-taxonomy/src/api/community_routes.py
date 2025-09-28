"""
Community and Collaborative Filtering API Routes

FastAPI endpoints for community-driven crop filtering features including
filter sharing, ratings, expert validation, and regional recommendations.
"""

import logging
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body
from pydantic import BaseModel, Field

from ..models.community_models import (
    CommunityFilterPreset, CommunityRating, FilterPresetShare, CommunityDiscussion,
    CommunityComment, CommunityRecommendation, FilterModerationReport,
    RegionalFilterRecommendation, ExpertValidation
)
from ..services.collaborative_filtering_service import collaborative_filtering_service

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v1/crop-taxonomy/community", tags=["community"])

# Request/Response Models
class CreateFilterPresetRequest(BaseModel):
    """Request model for creating a filter preset."""
    name: str = Field(..., min_length=1, max_length=200, description="Display name for the preset")
    description: Optional[str] = Field(None, description="Detailed description of the preset")
    filter_config: dict = Field(..., description="The filter configuration")
    visibility: str = Field(default="private", regex="^(public|private|shared)$", description="Visibility level")
    tags: List[str] = Field(default_factory=list, description="Tags for categorizing the preset")
    region_codes: List[str] = Field(default_factory=list, description="Region codes where preset is applicable")


class RatePresetRequest(BaseModel):
    """Request model for rating a filter preset."""
    rating: int = Field(..., ge=1, le=5, description="Rating value (1-5 stars)")
    review_text: Optional[str] = Field(None, max_length=1000, description="Optional review text")


class SharePresetRequest(BaseModel):
    """Request model for sharing a filter preset."""
    shared_with_user_id: Optional[UUID] = Field(None, description="User to share with")
    shared_with_group: Optional[str] = Field(None, description="Group to share with")
    share_message: Optional[str] = Field(None, max_length=500, description="Message to send with share")
    permission_level: str = Field(default="view", regex="^(view|edit|admin)$", description="Permission level")


class CreateDiscussionRequest(BaseModel):
    """Request model for creating a discussion."""
    title: str = Field(..., min_length=1, max_length=200, description="Discussion title")
    is_pinned: bool = Field(default=False, description="Whether to pin the discussion")


class AddCommentRequest(BaseModel):
    """Request model for adding a comment."""
    content: str = Field(..., min_length=1, max_length=2000, description="Comment content")
    parent_comment_id: Optional[UUID] = Field(None, description="Parent comment for nested replies")


class ReportContentRequest(BaseModel):
    """Request model for reporting inappropriate content."""
    reported_content_type: str = Field(..., regex="^(preset|comment|rating)$", description="Type of content being reported")
    reported_content_id: UUID = Field(..., description="ID of the reported content")
    reason: str = Field(..., max_length=500, description="Reason for the report")
    additional_details: Optional[str] = Field(None, max_length=1000, description="Additional details")


class ValidatePresetRequest(BaseModel):
    """Request model for expert validation of a preset."""
    validation_status: str = Field(..., regex="^(pending|approved|rejected|flagged)$", description="Validation status")
    validation_notes: Optional[str] = Field(None, max_length=1000, description="Notes about validation")


class GetPresetsRequest(BaseModel):
    """Request model for getting filter presets."""
    tags: List[str] = Field(default_factory=list, description="Filter by tags")
    region_codes: List[str] = Field(default_factory=list, description="Filter by region codes")
    min_rating: float = Field(default=0.0, ge=0.0, le=5.0, description="Minimum rating threshold")
    limit: int = Field(default=50, ge=1, le=100, description="Maximum number of presets to return")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")


class GetRecommendationsRequest(BaseModel):
    """Request model for getting recommendations."""
    limit: int = Field(default=5, ge=1, le=20, description="Maximum number of recommendations to return")


# API Endpoints
@router.post("/presets", response_model=CommunityFilterPreset)
async def create_filter_preset(
    request: CreateFilterPresetRequest,
    user_id: UUID = Query(..., description="User creating the preset")
) -> CommunityFilterPreset:
    """
    Create a new community filter preset.
    
    Creates a new filter preset that can be shared with the community,
    rated by other users, and validated by experts.
    """
    try:
        preset = await collaborative_filtering_service.create_filter_preset(
            creator_id=user_id,
            name=request.name,
            description=request.description,
            filter_config=request.filter_config,
            visibility=request.visibility,
            tags=request.tags,
            region_codes=request.region_codes
        )
        return preset
    except Exception as e:
        logger.error(f"Error creating filter preset: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presets/{preset_id}", response_model=CommunityFilterPreset)
async def get_filter_preset(
    preset_id: UUID = Path(..., description="ID of the preset to retrieve")
) -> CommunityFilterPreset:
    """
    Get a filter preset by ID.
    
    Retrieves detailed information about a specific filter preset.
    """
    preset = await collaborative_filtering_service.get_preset_by_id(preset_id)
    if not preset:
        raise HTTPException(status_code=404, detail="Filter preset not found")
    return preset


@router.get("/presets", response_model=List[CommunityFilterPreset])
async def get_public_presets(
    tags: List[str] = Query(default_factory=list, description="Filter by tags"),
    region_codes: List[str] = Query(default_factory=list, description="Filter by region codes"),
    min_rating: float = Query(default=0.0, ge=0.0, le=5.0, description="Minimum rating threshold"),
    limit: int = Query(default=50, ge=1, le=100, description="Maximum number of presets to return"),
    offset: int = Query(default=0, ge=0, description="Offset for pagination")
) -> List[CommunityFilterPreset]:
    """
    Get public filter presets.
    
    Retrieves public filter presets with optional filtering by tags, regions, and minimum rating.
    Results are sorted by rating and usage count.
    """
    try:
        presets = await collaborative_filtering_service.get_public_presets(
            tags=tags,
            region_codes=region_codes,
            min_rating=min_rating,
            limit=limit,
            offset=offset
        )
        return presets
    except Exception as e:
        logger.error(f"Error getting public presets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/my-presets", response_model=List[CommunityFilterPreset])
async def get_user_presets(
    user_id: UUID = Query(..., description="User ID to get presets for"),
    visibility: Optional[str] = Query(None, regex="^(public|private|shared)$", description="Filter by visibility level"),
    include_shared: bool = Query(default=True, description="Whether to include shared presets")
) -> List[CommunityFilterPreset]:
    """
    Get filter presets created by or shared with a user.
    
    Retrieves presets that were created by the user or shared with them.
    """
    try:
        presets = await collaborative_filtering_service.get_user_presets(
            user_id=user_id,
            visibility=visibility,
            include_shared=include_shared
        )
        return presets
    except Exception as e:
        logger.error(f"Error getting user presets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/presets/{preset_id}/rate", response_model=CommunityRating)
async def rate_preset(
    preset_id: UUID,
    request: RatePresetRequest,
    user_id: UUID = Query(..., description="User rating the preset")
) -> CommunityRating:
    """
    Rate a filter preset.
    
    Allows users to rate a filter preset with a 1-5 star rating and optional review text.
    """
    try:
        rating = await collaborative_filtering_service.rate_preset(
            user_id=user_id,
            preset_id=preset_id,
            rating=request.rating,
            review_text=request.review_text
        )
        return rating
    except Exception as e:
        logger.error(f"Error rating preset: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/presets/{preset_id}/share", response_model=FilterPresetShare)
async def share_preset(
    preset_id: UUID,
    request: SharePresetRequest,
    shared_by_user_id: UUID = Query(..., description="User sharing the preset")
) -> FilterPresetShare:
    """
    Share a filter preset with another user or group.
    
    Allows users to share their filter presets with others.
    """
    if not request.shared_with_user_id and not request.shared_with_group:
        raise HTTPException(status_code=400, detail="Either shared_with_user_id or shared_with_group must be provided")
    
    try:
        share = await collaborative_filtering_service.share_preset(
            preset_id=preset_id,
            shared_by_user_id=shared_by_user_id,
            shared_with_user_id=request.shared_with_user_id,
            shared_with_group=request.shared_with_group,
            share_message=request.share_message,
            permission_level=request.permission_level
        )
        return share
    except Exception as e:
        logger.error(f"Error sharing preset: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/presets/{preset_id}/discussions", response_model=CommunityDiscussion)
async def create_discussion(
    preset_id: UUID,
    request: CreateDiscussionRequest,
    created_by_user_id: UUID = Query(..., description="User creating the discussion")
) -> CommunityDiscussion:
    """
    Create a discussion thread for a filter preset.
    
    Creates a new discussion thread where community members can discuss the preset.
    """
    try:
        discussion = await collaborative_filtering_service.create_discussion(
            preset_id=preset_id,
            title=request.title,
            created_by_user_id=created_by_user_id,
            is_pinned=request.is_pinned
        )
        return discussion
    except Exception as e:
        logger.error(f"Error creating discussion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/discussions/{discussion_id}/comments", response_model=List[CommunityComment])
async def get_discussion_comments(
    discussion_id: UUID,
    include_replies: bool = Query(default=True, description="Whether to include nested replies")
) -> List[CommunityComment]:
    """
    Get comments for a discussion.
    
    Retrieves all comments for a specific discussion thread.
    """
    try:
        comments = await collaborative_filtering_service.get_discussion_comments(
            discussion_id=discussion_id,
            include_replies=include_replies
        )
        return comments
    except Exception as e:
        logger.error(f"Error getting discussion comments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/discussions/{discussion_id}/comments", response_model=CommunityComment)
async def add_comment(
    discussion_id: UUID,
    request: AddCommentRequest,
    author_user_id: UUID = Query(..., description="User creating the comment")
) -> CommunityComment:
    """
    Add a comment to a discussion.
    
    Adds a new comment to an existing discussion thread.
    """
    try:
        comment = await collaborative_filtering_service.add_comment(
            discussion_id=discussion_id,
            author_user_id=author_user_id,
            content=request.content,
            parent_comment_id=request.parent_comment_id
        )
        return comment
    except Exception as e:
        logger.error(f"Error adding comment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/moderate/report", response_model=FilterModerationReport)
async def report_content(
    request: ReportContentRequest,
    reporter_user_id: UUID = Query(..., description="User filing the report")
) -> FilterModerationReport:
    """
    Report inappropriate content in community features.
    
    Allows users to report inappropriate content in presets, comments, or ratings.
    """
    try:
        report = await collaborative_filtering_service.report_content(
            reported_content_type=request.reported_content_type,
            reported_content_id=request.reported_content_id,
            reporter_user_id=reporter_user_id,
            reason=request.reason,
            additional_details=request.additional_details
        )
        return report
    except Exception as e:
        logger.error(f"Error creating report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/presets/{preset_id}/validate", response_model=ExpertValidation)
async def validate_preset_expert(
    preset_id: UUID,
    request: ValidatePresetRequest,
    validated_by: UUID = Query(..., description="Expert validating the preset")
) -> ExpertValidation:
    """
    Validate a filter preset with expert validation.
    
    Allows experts to validate filter presets for accuracy and agricultural relevance.
    """
    try:
        validation = await collaborative_filtering_service.validate_preset_expert(
            preset_id=preset_id,
            validated_by=validated_by,
            validation_status=request.validation_status,
            validation_notes=request.validation_notes
        )
        return validation
    except Exception as e:
        logger.error(f"Error validating preset: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presets/expert-validated", response_model=List[CommunityFilterPreset])
async def get_expert_validated_presets(
    region_codes: List[str] = Query(default_factory=list, description="Filter by region codes")
) -> List[CommunityFilterPreset]:
    """
    Get filter presets that have been expert validated.
    
    Retrieves all presets that have been validated by agricultural experts.
    """
    try:
        presets = await collaborative_filtering_service.get_expert_validated_presets(
            region_codes=region_codes
        )
        return presets
    except Exception as e:
        logger.error(f"Error getting expert validated presets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations/collaborative", response_model=List[CommunityRecommendation])
async def get_collaborative_recommendations(
    user_id: UUID = Query(..., description="User to generate recommendations for"),
    limit: int = Query(default=5, ge=1, le=20, description="Maximum number of recommendations to return")
) -> List[CommunityRecommendation]:
    """
    Get collaborative filtering recommendations.
    
    Generates personalized filter preset recommendations based on similar users' preferences.
    """
    try:
        recommendations = await collaborative_filtering_service.generate_collaborative_recommendations(
            user_id=user_id,
            limit=limit
        )
        return recommendations
    except Exception as e:
        logger.error(f"Error generating collaborative recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presets/regional/{region_code}", response_model=List[CommunityFilterPreset])
async def get_regional_presets(
    region_code: str,
    min_popularity: float = Query(default=0.1, ge=0.0, le=1.0, description="Minimum popularity threshold"),
    limit: int = Query(default=10, ge=1, le=50, description="Maximum number of presets to return")
) -> List[CommunityFilterPreset]:
    """
    Get filter presets popular in a specific region.
    
    Retrieves presets that are popular and relevant to a specific geographic region.
    """
    try:
        presets = await collaborative_filtering_service.get_regional_presets(
            region_code=region_code,
            min_popularity=min_popularity,
            limit=limit
        )
        return presets
    except Exception as e:
        logger.error(f"Error getting regional presets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/presets/{preset_id}/increment-usage")
async def increment_preset_usage(
    preset_id: UUID
) -> dict:
    """
    Increment the usage count of a preset.
    
    Updates the usage statistics for a preset when it's applied by a user.
    """
    try:
        success = await collaborative_filtering_service.increment_preset_usage(preset_id)
        if success:
            return {"success": True, "message": f"Usage count incremented for preset {preset_id}"}
        else:
            raise HTTPException(status_code=404, detail="Filter preset not found")
    except Exception as e:
        logger.error(f"Error incrementing preset usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def community_features_health_check() -> dict:
    """Health check endpoint for community features."""
    try:
        return {
            "status": "healthy",
            "service": "community_features",
            "features": [
                "filter_preset_sharing",
                "community_ratings",
                "discussions",
                "expert_validation",
                "collaborative_filtering",
                "regional_recommendations",
                "content_moderation"
            ],
            "preset_count": len(collaborative_filtering_service._presets),
            "rating_count": len(collaborative_filtering_service._ratings),
            "comment_count": len(collaborative_filtering_service._comments),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Service unhealthy")


# Export router
__all__ = ["router"]