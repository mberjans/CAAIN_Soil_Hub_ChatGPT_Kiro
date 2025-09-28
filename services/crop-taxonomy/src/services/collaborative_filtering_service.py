"""
Collaborative Filtering and Community Features Service

Service for implementing community-driven crop filtering features including
filter sharing, ratings, expert validation, and regional recommendations.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
from collections import defaultdict, Counter

from ..models.community_models import (
    CommunityFilterPreset, CommunityRating, FilterPresetShare, CommunityDiscussion,
    CommunityComment, CommunityRecommendation, FilterModerationReport,
    RegionalFilterRecommendation, ExpertValidation, ExpertValidationStatus
)
from ..models.crop_filtering_models import TaxonomyFilterCriteria

logger = logging.getLogger(__name__)


class CollaborativeFilteringService:
    """Service for collaborative filtering and community features."""

    def __init__(self):
        # In-memory storage for development; in production this would be a database
        self._presets: Dict[str, CommunityFilterPreset] = {}
        self._ratings: Dict[str, CommunityRating] = {}
        self._shares: Dict[str, FilterPresetShare] = {}
        self._discussions: Dict[str, CommunityDiscussion] = {}
        self._comments: Dict[str, CommunityComment] = {}
        self._reports: Dict[str, FilterModerationReport] = {}
        self._regional_recommendations: Dict[str, RegionalFilterRecommendation] = {}
        self._expert_validations: Dict[str, ExpertValidation] = {}

    async def create_filter_preset(
        self,
        creator_id: UUID,
        name: str,
        filter_config: Dict[str, Any],
        description: Optional[str] = None,
        visibility: str = "private",
        tags: Optional[List[str]] = None,
        region_codes: Optional[List[str]] = None
    ) -> CommunityFilterPreset:
        """
        Create a new community filter preset.
        
        Args:
            creator_id: User who created the preset
            name: Name of the preset
            filter_config: Filter configuration
            description: Description of the preset
            visibility: Visibility level (public, private, shared)
            tags: Tags for categorizing the preset
            region_codes: Region codes where preset is applicable
            
        Returns:
            Created CommunityFilterPreset object
        """
        preset = CommunityFilterPreset(
            creator_id=creator_id,
            name=name,
            description=description,
            filter_config=filter_config,
            visibility=visibility,
            tags=tags or [],
            region_codes=region_codes or [],
            expert_validation_status=ExpertValidationStatus.PENDING
        )
        
        preset.preset_id = UUID(int=hash(str(preset.name + str(creator_id))) % (10**20))
        self._presets[str(preset.preset_id)] = preset
        
        logger.info(f"Created filter preset: {preset.preset_id} ({name})")
        return preset

    async def get_preset_by_id(self, preset_id: UUID) -> Optional[CommunityFilterPreset]:
        """
        Get a filter preset by its ID.
        
        Args:
            preset_id: The ID of the preset to retrieve
            
        Returns:
            The CommunityFilterPreset object if found, None otherwise
        """
        return self._presets.get(str(preset_id))

    async def get_public_presets(
        self,
        tags: Optional[List[str]] = None,
        region_codes: Optional[List[str]] = None,
        min_rating: float = 0.0,
        limit: int = 50,
        offset: int = 0
    ) -> List[CommunityFilterPreset]:
        """
        Get public filter presets with optional filtering.
        
        Args:
            tags: Filter by tags (preset must have at least one of these tags)
            region_codes: Filter by region codes (preset must be applicable to at least one region)
            min_rating: Minimum rating threshold (0.0 to 5.0)
            limit: Maximum number of presets to return
            offset: Offset for pagination
            
        Returns:
            List of public CommunityFilterPreset objects
        """
        public_presets = []
        
        for preset in self._presets.values():
            if preset.visibility != "public":
                continue
                
            # Apply tag filter if specified
            if tags:
                if not any(tag in preset.tags for tag in tags if preset.tags):
                    continue
            
            # Apply region filter if specified
            if region_codes:
                if not any(region in preset.region_codes for region in region_codes if preset.region_codes):
                    continue
            
            # Apply rating filter if specified
            if min_rating > 0.0 and preset.average_rating < min_rating:
                continue
                
            public_presets.append(preset)
        
        # Sort by average rating (descending) and usage count (descending)
        public_presets.sort(key=lambda p: (p.average_rating, p.usage_count), reverse=True)
        
        # Apply pagination
        paginated_presets = public_presets[offset:offset + limit]
        
        return paginated_presets

    async def rate_preset(
        self,
        user_id: UUID,
        preset_id: UUID,
        rating: int,
        review_text: Optional[str] = None
    ) -> CommunityRating:
        """
        Rate a filter preset.
        
        Args:
            user_id: User rating the preset
            preset_id: Preset being rated
            rating: Rating value (1-5)
            review_text: Optional review text
            
        Returns:
            Created CommunityRating object
        """
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")
        
        rating_obj = CommunityRating(
            user_id=user_id,
            preset_id=preset_id,
            rating=rating,
            review_text=review_text
        )
        
        rating_obj.rating_id = UUID(int=hash(str(user_id) + str(preset_id) + str(rating)) % (10**20))
        self._ratings[str(rating_obj.rating_id)] = rating_obj
        
        # Update preset rating statistics
        preset = self._presets.get(str(preset_id))
        if preset:
            preset.rating_count += 1
            total_rating = preset.average_rating * (preset.rating_count - 1) + rating
            preset.average_rating = total_rating / preset.rating_count
            preset.updated_at = datetime.utcnow()
        
        logger.info(f"Rated preset {preset_id} with rating {rating} by user {user_id}")
        return rating_obj

    async def share_preset(
        self,
        preset_id: UUID,
        shared_by_user_id: UUID,
        shared_with_user_id: Optional[UUID] = None,
        shared_with_group: Optional[str] = None,
        share_message: Optional[str] = None,
        permission_level: str = "view"
    ) -> FilterPresetShare:
        """
        Share a filter preset with another user or group.
        
        Args:
            preset_id: ID of the preset to share
            shared_by_user_id: User sharing the preset
            shared_with_user_id: User receiving the share (optional)
            shared_with_group: Group receiving the share (optional)
            share_message: Message to send with share
            permission_level: Permission level ('view', 'edit', 'admin')
            
        Returns:
            Created FilterPresetShare object
        """
        if not shared_with_user_id and not shared_with_group:
            raise ValueError("Either shared_with_user_id or shared_with_group must be provided")
        
        share = FilterPresetShare(
            preset_id=preset_id,
            shared_by_user_id=shared_by_user_id,
            shared_with_user_id=shared_with_user_id,
            shared_with_group=shared_with_group,
            share_message=share_message,
            permission_level=permission_level
        )
        
        share.share_id = UUID(int=hash(str(preset_id) + str(shared_by_user_id) + str(shared_with_user_id or shared_with_group)) % (10**20))
        self._shares[str(share.share_id)] = share
        
        # Update preset share count
        preset = self._presets.get(str(preset_id))
        if preset:
            preset.share_count += 1
            preset.updated_at = datetime.utcnow()
        
        logger.info(f"Shared preset {preset_id} from user {shared_by_user_id} to {shared_with_user_id or shared_with_group}")
        return share

    async def get_user_presets(
        self,
        user_id: UUID,
        visibility: Optional[str] = None,
        include_shared: bool = True
    ) -> List[CommunityFilterPreset]:
        """
        Get filter presets created by or shared with a user.
        
        Args:
            user_id: User ID to get presets for
            visibility: Filter by visibility level
            include_shared: Whether to include shared presets
            
        Returns:
            List of CommunityFilterPreset objects
        """
        user_presets = []
        
        # Get presets created by user
        for preset in self._presets.values():
            if preset.creator_id == user_id:
                if visibility and preset.visibility != visibility:
                    continue
                user_presets.append(preset)
        
        # Optionally include presets shared with user
        if include_shared:
            for share in self._shares.values():
                if share.shared_with_user_id == user_id:
                    preset = self._presets.get(str(share.preset_id))
                    if preset and preset not in user_presets:
                        user_presets.append(preset)
        
        return user_presets

    async def create_discussion(
        self,
        preset_id: UUID,
        title: str,
        created_by_user_id: UUID,
        is_pinned: bool = False
    ) -> CommunityDiscussion:
        """
        Create a discussion thread for a filter preset.
        
        Args:
            preset_id: Preset this discussion is about
            title: Discussion title
            created_by_user_id: User creating the discussion
            is_pinned: Whether to pin the discussion
            
        Returns:
            Created CommunityDiscussion object
        """
        discussion = CommunityDiscussion(
            preset_id=preset_id,
            title=title,
            created_by_user_id=created_by_user_id,
            is_pinned=is_pinned
        )
        
        discussion.discussion_id = UUID(int=hash(str(preset_id) + title + str(created_by_user_id)) % (10**20))
        self._discussions[str(discussion.discussion_id)] = discussion
        
        logger.info(f"Created discussion {discussion.discussion_id} for preset {preset_id}")
        return discussion

    async def add_comment(
        self,
        discussion_id: UUID,
        author_user_id: UUID,
        content: str,
        parent_comment_id: Optional[UUID] = None
    ) -> CommunityComment:
        """
        Add a comment to a discussion.
        
        Args:
            discussion_id: Discussion to add comment to
            author_user_id: User creating the comment
            content: Comment content
            parent_comment_id: Parent comment for nested replies
            
        Returns:
            Created CommunityComment object
        """
        comment = CommunityComment(
            discussion_id=discussion_id,
            author_user_id=author_user_id,
            content=content,
            parent_comment_id=parent_comment_id
        )
        
        comment.comment_id = UUID(int=hash(str(discussion_id) + str(author_user_id) + content) % (10**20))
        self._comments[str(comment.comment_id)] = comment
        
        # Update discussion timestamp
        discussion = self._discussions.get(str(discussion_id))
        if discussion:
            discussion.updated_at = datetime.utcnow()
        
        logger.info(f"Added comment {comment.comment_id} to discussion {discussion_id}")
        return comment

    async def get_discussion_comments(
        self,
        discussion_id: UUID,
        include_replies: bool = True
    ) -> List[CommunityComment]:
        """
        Get comments for a discussion.
        
        Args:
            discussion_id: Discussion to get comments for
            include_replies: Whether to include nested replies
            
        Returns:
            List of CommunityComment objects
        """
        discussion_comments = []
        
        for comment in self._comments.values():
            if comment.discussion_id == discussion_id:
                if include_replies or comment.parent_comment_id is None:
                    discussion_comments.append(comment)
        
        # Sort by creation time
        discussion_comments.sort(key=lambda c: c.created_at)
        return discussion_comments

    async def report_content(
        self,
        reported_content_type: str,
        reported_content_id: UUID,
        reporter_user_id: UUID,
        reason: str,
        additional_details: Optional[str] = None
    ) -> FilterModerationReport:
        """
        Report inappropriate content.
        
        Args:
            reported_content_type: Type of content being reported
            reported_content_id: ID of the reported content
            reporter_user_id: User filing the report
            reason: Reason for the report
            additional_details: Additional details about the report
            
        Returns:
            Created FilterModerationReport object
        """
        report = FilterModerationReport(
            reported_content_type=reported_content_type,
            reported_content_id=reported_content_id,
            reporter_user_id=reporter_user_id,
            reason=reason,
            additional_details=additional_details
        )
        
        report.report_id = UUID(int=hash(str(reporter_user_id) + reported_content_type + str(reported_content_id)) % (10**20))
        self._reports[str(report.report_id)] = report
        
        logger.info(f"Report filed for {reported_content_type} {reported_content_id} by user {reporter_user_id}")
        return report

    async def validate_preset_expert(
        self,
        preset_id: UUID,
        validated_by: UUID,
        validation_status: str,
        validation_notes: Optional[str] = None
    ) -> ExpertValidation:
        """
        Validate a preset with expert validation.
        
        Args:
            preset_id: Preset to validate
            validated_by: Expert validating the preset
            validation_status: Validation status (approved, rejected, flagged, pending)
            validation_notes: Notes about validation
            
        Returns:
            Created ExpertValidation object
        """
        validation = ExpertValidation(
            preset_id=preset_id,
            validated_by=validated_by,
            validation_status=validation_status,
            validation_notes=validation_notes
        )
        
        validation.validation_id = UUID(int=hash(str(preset_id) + str(validated_by) + validation_status) % (10**20))
        self._expert_validations[str(validation.validation_id)] = validation
        
        # Update preset validation status
        preset = self._presets.get(str(preset_id))
        if preset:
            preset.expert_validation_status = validation_status
            preset.expert_validated_by = validated_by
            preset.expert_validation_date = datetime.utcnow()
            preset.expert_notes = validation_notes
            preset.updated_at = datetime.utcnow()
        
        logger.info(f"Expert validation {validation_status} for preset {preset_id} by expert {validated_by}")
        return validation

    async def get_expert_validated_presets(
        self,
        region_codes: Optional[List[str]] = None
    ) -> List[CommunityFilterPreset]:
        """
        Get presets that have been expert validated.
        
        Args:
            region_codes: Filter by region codes (preset must be applicable to at least one region)
            
        Returns:
            List of expert validated CommunityFilterPreset objects
        """
        validated_presets = []
        
        for preset in self._presets.values():
            if preset.expert_validation_status == ExpertValidationStatus.APPROVED:
                # Apply region filter if specified
                if region_codes:
                    if not any(region in preset.region_codes for region in region_codes if preset.region_codes):
                        continue
                validated_presets.append(preset)
        
        # Sort by average rating and validation date
        validated_presets.sort(key=lambda p: (p.average_rating, p.expert_validation_date), reverse=True)
        return validated_presets

    async def generate_collaborative_recommendations(
        self,
        user_id: UUID,
        limit: int = 5
    ) -> List[CommunityRecommendation]:
        """
        Generate collaborative filtering recommendations based on user behavior and similar users.
        
        Args:
            user_id: User to generate recommendations for
            limit: Maximum number of recommendations to return
            
        Returns:
            List of CommunityRecommendation objects
        """
        recommendations = []
        
        # For this implementation, we'll use a simple approach:
        # 1. Find presets created by users with similar interests
        # 2. Rank by popularity, rating, and region relevance
        
        # Get user's existing presets to find similar users
        user_presets = await self.get_user_presets(user_id)
        user_tags = set()
        user_regions = set()
        
        for preset in user_presets:
            user_tags.update(preset.tags)
            user_regions.update(preset.region_codes)
        
        # Find public presets with similar tags or regions
        potential_presets = await self.get_public_presets(
            tags=list(user_tags) if user_tags else None,
            region_codes=list(user_regions) if user_regions else None,
            min_rating=3.0
        )
        
        # Create recommendations based on similarity
        for preset in potential_presets[:limit]:
            if preset.creator_id != user_id:  # Don't recommend user's own presets
                confidence_score = min(0.7 + (preset.average_rating / 10.0), 1.0)  # Higher ratings = higher confidence
                
                recommendation = CommunityRecommendation(
                    user_id=user_id,
                    preset_id=preset.preset_id,
                    source_user_id=preset.creator_id,
                    confidence_score=confidence_score,
                    reason=f"Similar to your {', '.join(preset.tags[:2])} presets"
                )
                recommendation.recommendation_id = UUID(int=hash(str(user_id) + str(preset.preset_id)) % (10**20))
                recommendations.append(recommendation)
        
        logger.info(f"Generated {len(recommendations)} collaborative recommendations for user {user_id}")
        return recommendations

    async def get_regional_presets(
        self,
        region_code: str,
        min_popularity: float = 0.1,
        limit: int = 10
    ) -> List[CommunityFilterPreset]:
        """
        Get filter presets popular in a specific region.
        
        Args:
            region_code: Region code to get presets for
            min_popularity: Minimum popularity threshold
            limit: Maximum number of presets to return
            
        Returns:
            List of CommunityFilterPreset objects
        """
        regional_presets = []
        
        for preset in self._presets.values():
            if region_code in preset.region_codes:
                if preset.visibility == "public" and preset.average_rating >= 3.0:
                    # Calculate or use regional popularity score
                    regional_score = preset.average_rating * preset.usage_count / 100.0
                    if regional_score >= min_popularity:
                        regional_presets.append(preset)
        
        # Sort by regional relevance (rating * usage / regional popularity)
        regional_presets.sort(key=lambda p: p.average_rating * p.usage_count, reverse=True)
        
        return regional_presets[:limit]

    async def increment_preset_usage(self, preset_id: UUID) -> bool:
        """
        Increment the usage count of a preset.
        
        Args:
            preset_id: ID of the preset to update
            
        Returns:
            True if successful, False if preset not found
        """
        preset = self._presets.get(str(preset_id))
        if not preset:
            return False
        
        preset.usage_count += 1
        preset.updated_at = datetime.utcnow()
        return True


# Global instance
collaborative_filtering_service = CollaborativeFilteringService()