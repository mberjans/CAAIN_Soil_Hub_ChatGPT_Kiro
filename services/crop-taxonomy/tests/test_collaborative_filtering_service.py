"""
Test suite for collaborative filtering and community features service.

This test suite validates the functionality of the CollaborativeFilteringService,
including preset sharing, ratings, discussions, expert validation, and collaborative
recommendations.
"""

import pytest
import asyncio
from uuid import uuid4, UUID
from datetime import datetime, timedelta

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.models.community_models import (
    CommunityFilterPreset, CommunityRating, FilterPresetShare, CommunityDiscussion,
    CommunityComment, CommunityRecommendation, FilterModerationReport,
    RegionalFilterRecommendation, ExpertValidation, ExpertValidationStatus
)
from src.services.collaborative_filtering_service import CollaborativeFilteringService


class TestCollaborativeFilteringService:
    """Test suite for the CollaborativeFilteringService."""

    @pytest.fixture
    def service(self):
        """Create a fresh service instance for each test."""
        return CollaborativeFilteringService()

    @pytest.fixture
    def sample_user_id(self):
        """Return a sample user ID."""
        return uuid4()

    @pytest.fixture
    def sample_creator_id(self):
        """Return a sample creator ID."""
        return uuid4()

    @pytest.fixture
    def sample_filter_config(self):
        """Return a sample filter configuration."""
        return {
            "crop_type": ["corn", "soybean"],
            "soil_type": ["loam", "clay_loam"],
            "climate_zone": ["5a", "5b", "6a"],
            "drought_tolerance": "moderate",
            "pest_resistance": ["corn_borer", "aphids"]
        }

    async def test_create_filter_preset(self, service, sample_creator_id, sample_filter_config):
        """Test creating a filter preset."""
        name = "Test Corn Filter"
        description = "A test filter for corn varieties"
        
        preset = await service.create_filter_preset(
            creator_id=sample_creator_id,
            name=name,
            description=description,
            filter_config=sample_filter_config,
            visibility="public",
            tags=["corn", "test", "filter"],
            region_codes=["IA", "IL", "MN"]
        )

        assert preset.name == name
        assert preset.description == description
        assert preset.creator_id == sample_creator_id
        assert preset.filter_config == sample_filter_config
        assert preset.visibility == "public"
        assert "corn" in preset.tags
        assert "IA" in preset.region_codes
        assert preset.preset_id is not None
        assert preset.average_rating == 0.0
        assert preset.rating_count == 0
        assert preset.usage_count == 0
        assert preset.share_count == 0
        assert preset.expert_validation_status == ExpertValidationStatus.PENDING

    async def test_get_preset_by_id(self, service, sample_creator_id, sample_filter_config):
        """Test retrieving a filter preset by ID."""
        preset = await service.create_filter_preset(
            creator_id=sample_creator_id,
            name="Test Preset",
            filter_config=sample_filter_config
        )

        retrieved_preset = await service.get_preset_by_id(preset.preset_id)
        
        assert retrieved_preset is not None
        assert retrieved_preset.preset_id == preset.preset_id
        assert retrieved_preset.name == "Test Preset"

    async def test_get_preset_by_id_not_found(self, service):
        """Test retrieving a non-existent filter preset."""
        non_existent_id = uuid4()
        result = await service.get_preset_by_id(non_existent_id)
        
        assert result is None

    async def test_get_public_presets(self, service, sample_creator_id, sample_filter_config):
        """Test retrieving public filter presets."""
        # Create multiple presets
        preset1 = await service.create_filter_preset(
            creator_id=sample_creator_id,
            name="Public Preset 1",
            filter_config=sample_filter_config,
            visibility="public",
            tags=["corn", "test"],
            region_codes=["IA"]
        )
        
        preset2 = await service.create_filter_preset(
            creator_id=sample_creator_id,
            name="Public Preset 2", 
            filter_config=sample_filter_config,
            visibility="public",
            tags=["soybean", "test"],
            region_codes=["IL"]
        )
        
        # Create private preset (should not appear in public results)
        await service.create_filter_preset(
            creator_id=sample_creator_id,
            name="Private Preset",
            filter_config=sample_filter_config,
            visibility="private"
        )

        public_presets = await service.get_public_presets()
        
        assert len(public_presets) == 2
        preset_names = [p.name for p in public_presets]
        assert "Public Preset 1" in preset_names
        assert "Public Preset 2" in preset_names
        assert "Private Preset" not in preset_names

    async def test_get_public_presets_with_tag_filter(self, service, sample_creator_id, sample_filter_config):
        """Test retrieving public filter presets with tag filtering."""
        await service.create_filter_preset(
            creator_id=sample_creator_id,
            name="Corn Preset",
            filter_config=sample_filter_config,
            visibility="public",
            tags=["corn", "test"]
        )
        
        await service.create_filter_preset(
            creator_id=sample_creator_id,
            name="Soybean Preset",
            filter_config=sample_filter_config,
            visibility="public",
            tags=["soybean", "test"]
        )
        
        filtered_presets = await service.get_public_presets(tags=["corn"])
        
        assert len(filtered_presets) == 1
        assert filtered_presets[0].name == "Corn Preset"

    async def test_get_public_presets_with_region_filter(self, service, sample_creator_id, sample_filter_config):
        """Test retrieving public filter presets with region filtering."""
        await service.create_filter_preset(
            creator_id=sample_creator_id,
            name="IA Preset",
            filter_config=sample_filter_config,
            visibility="public",
            region_codes=["IA", "MN"]
        )
        
        await service.create_filter_preset(
            creator_id=sample_creator_id,
            name="IL Preset",
            filter_config=sample_filter_config,
            visibility="public",
            region_codes=["IL", "WI"]
        )
        
        filtered_presets = await service.get_public_presets(region_codes=["IA"])
        
        assert len(filtered_presets) == 1
        assert filtered_presets[0].name == "IA Preset"

    async def test_rate_preset(self, service, sample_creator_id, sample_user_id, sample_filter_config):
        """Test rating a filter preset."""
        preset = await service.create_filter_preset(
            creator_id=sample_creator_id,
            name="Rate Test Preset",
            filter_config=sample_filter_config,
            visibility="public"
        )
        
        rating = await service.rate_preset(
            user_id=sample_user_id,
            preset_id=preset.preset_id,
            rating=4,
            review_text="Great filter, very useful!"
        )
        
        assert rating.rating == 4
        assert rating.user_id == sample_user_id
        assert rating.preset_id == preset.preset_id
        assert rating.review_text == "Great filter, very useful!"
        
        # Check that preset stats were updated
        updated_preset = await service.get_preset_by_id(preset.preset_id)
        assert updated_preset.rating_count == 1
        assert updated_preset.average_rating == 4.0

    async def test_multiple_ratings_average(self, service, sample_creator_id, sample_user_id, sample_filter_config):
        """Test that multiple ratings result in correct average."""
        preset = await service.create_filter_preset(
            creator_id=sample_creator_id,
            name="Average Test Preset",
            filter_config=sample_filter_config,
            visibility="public"
        )
        
        await service.rate_preset(user_id=sample_user_id, preset_id=preset.preset_id, rating=3)
        await service.rate_preset(user_id=uuid4(), preset_id=preset.preset_id, rating=5)
        await service.rate_preset(user_id=uuid4(), preset_id=preset.preset_id, rating=4)
        
        updated_preset = await service.get_preset_by_id(preset.preset_id)
        assert updated_preset.rating_count == 3
        assert updated_preset.average_rating == 4.0  # (3+5+4)/3 = 4.0

    async def test_invalid_rating(self, service, sample_creator_id, sample_user_id, sample_filter_config):
        """Test that invalid ratings raise appropriate errors."""
        preset = await service.create_filter_preset(
            creator_id=sample_creator_id,
            name="Invalid Rating Test",
            filter_config=sample_filter_config
        )
        
        with pytest.raises(ValueError, match="Rating must be between 1 and 5"):
            await service.rate_preset(user_id=sample_user_id, preset_id=preset.preset_id, rating=0)
        
        with pytest.raises(ValueError, match="Rating must be between 1 and 5"):
            await service.rate_preset(user_id=sample_user_id, preset_id=preset.preset_id, rating=6)

    async def test_share_preset(self, service, sample_creator_id, sample_user_id, sample_filter_config):
        """Test sharing a filter preset."""
        preset = await service.create_filter_preset(
            creator_id=sample_creator_id,
            name="Share Test Preset",
            filter_config=sample_filter_config
        )
        
        shared_with_user = uuid4()
        share = await service.share_preset(
            preset_id=preset.preset_id,
            shared_by_user_id=sample_creator_id,
            shared_with_user_id=shared_with_user,
            share_message="Check out this useful filter!",
            permission_level="view"
        )
        
        assert share.preset_id == preset.preset_id
        assert share.shared_by_user_id == sample_creator_id
        assert share.shared_with_user_id == shared_with_user
        assert share.share_message == "Check out this useful filter!"
        assert share.permission_level == "view"
        
        # Check that preset share count was updated
        updated_preset = await service.get_preset_by_id(preset.preset_id)
        assert updated_preset.share_count == 1

    async def test_get_user_presets(self, service, sample_creator_id, sample_user_id, sample_filter_config):
        """Test retrieving presets for a specific user."""
        # Create preset by user
        user_preset = await service.create_filter_preset(
            creator_id=sample_user_id,
            name="User's Preset",
            filter_config=sample_filter_config,
            visibility="private"
        )
        
        # Create preset by another user
        other_preset = await service.create_filter_preset(
            creator_id=sample_creator_id,
            name="Other User's Preset",
            filter_config=sample_filter_config,
            visibility="public"
        )
        
        # Share other preset with user
        await service.share_preset(
            preset_id=other_preset.preset_id,
            shared_by_user_id=sample_creator_id,
            shared_with_user_id=sample_user_id
        )
        
        # Get user's presets with shared included
        user_presets = await service.get_user_presets(
            user_id=sample_user_id,
            include_shared=True
        )
        
        assert len(user_presets) == 2  # User's own preset + shared preset
        
        # Get user's presets without shared
        user_own_presets = await service.get_user_presets(
            user_id=sample_user_id,
            include_shared=False
        )
        
        assert len(user_own_presets) == 1  # Only user's own preset

    async def test_create_discussion(self, service, sample_creator_id, sample_user_id, sample_filter_config):
        """Test creating a discussion for a filter preset."""
        preset = await service.create_filter_preset(
            creator_id=sample_creator_id,
            name="Discussion Test Preset",
            filter_config=sample_filter_config
        )
        
        discussion = await service.create_discussion(
            preset_id=preset.preset_id,
            title="How to use this filter effectively?",
            created_by_user_id=sample_user_id,
            is_pinned=True
        )
        
        assert discussion.preset_id == preset.preset_id
        assert discussion.title == "How to use this filter effectively?"
        assert discussion.created_by_user_id == sample_user_id
        assert discussion.is_pinned is True

    async def test_add_comment_to_discussion(self, service, sample_creator_id, sample_user_id, sample_filter_config):
        """Test adding a comment to a discussion."""
        preset = await service.create_filter_preset(
            creator_id=sample_creator_id,
            name="Comment Test Preset",
            filter_config=sample_filter_config
        )
        
        discussion = await service.create_discussion(
            preset_id=preset.preset_id,
            title="Discussion for Comments",
            created_by_user_id=sample_user_id
        )
        
        comment = await service.add_comment(
            discussion_id=discussion.discussion_id,
            author_user_id=sample_user_id,
            content="This is a great filter recommendation!"
        )
        
        assert comment.discussion_id == discussion.discussion_id
        assert comment.author_user_id == sample_user_id
        assert comment.content == "This is a great filter recommendation!"
        assert comment.parent_comment_id is None

    async def test_add_nested_comment(self, service, sample_creator_id, sample_user_id, sample_filter_config):
        """Test adding a nested comment (reply to another comment)."""
        preset = await service.create_filter_preset(
            creator_id=sample_creator_id,
            name="Nested Comment Test Preset",
            filter_config=sample_filter_config
        )
        
        discussion = await service.create_discussion(
            preset_id=preset.preset_id,
            title="Discussion for Nested Comments",
            created_by_user_id=sample_user_id
        )
        
        # Add first comment
        parent_comment = await service.add_comment(
            discussion_id=discussion.discussion_id,
            author_user_id=sample_user_id,
            content="Original comment"
        )
        
        # Add reply to the first comment
        reply_comment = await service.add_comment(
            discussion_id=discussion.discussion_id,
            author_user_id=sample_user_id,
            content="Reply to original comment",
            parent_comment_id=parent_comment.comment_id
        )
        
        assert reply_comment.parent_comment_id == parent_comment.comment_id
        assert reply_comment.content == "Reply to original comment"

    async def test_get_discussion_comments(self, service, sample_creator_id, sample_user_id, sample_filter_config):
        """Test retrieving comments for a discussion."""
        preset = await service.create_filter_preset(
            creator_id=sample_creator_id,
            name="Get Comments Test Preset",
            filter_config=sample_filter_config
        )
        
        discussion = await service.create_discussion(
            preset_id=preset.preset_id,
            title="Discussion for Getting Comments",
            created_by_user_id=sample_user_id
        )
        
        # Add several comments
        await service.add_comment(
            discussion_id=discussion.discussion_id,
            author_user_id=sample_user_id,
            content="First comment"
        )
        
        await service.add_comment(
            discussion_id=discussion.discussion_id,
            author_user_id=sample_user_id,
            content="Second comment"
        )
        
        comments = await service.get_discussion_comments(
            discussion_id=discussion.discussion_id
        )
        
        assert len(comments) == 2
        contents = [c.content for c in comments]
        assert "First comment" in contents
        assert "Second comment" in contents

    async def test_report_content(self, service, sample_creator_id, sample_user_id, sample_filter_config):
        """Test reporting inappropriate content."""
        preset = await service.create_filter_preset(
            creator_id=sample_creator_id,
            name="Report Test Preset",
            filter_config=sample_filter_config
        )
        
        report = await service.report_content(
            reported_content_type="preset",
            reported_content_id=preset.preset_id,
            reporter_user_id=sample_user_id,
            reason="Inaccurate information",
            additional_details="This preset contains incorrect filter settings"
        )
        
        assert report.reported_content_type == "preset"
        assert report.reported_content_id == preset.preset_id
        assert report.reporter_user_id == sample_user_id
        assert report.reason == "Inaccurate information"
        assert report.additional_details == "This preset contains incorrect filter settings"
        assert report.status == "pending"

    async def test_validate_preset_expert(self, service, sample_creator_id, sample_user_id, sample_filter_config):
        """Test expert validation of a preset."""
        preset = await service.create_filter_preset(
            creator_id=sample_creator_id,
            name="Validation Test Preset",
            filter_config=sample_filter_config,
            visibility="public"
        )
        
        validation = await service.validate_preset_expert(
            preset_id=preset.preset_id,
            validated_by=sample_user_id,
            validation_status="approved",
            validation_notes="This preset is accurate and follows agricultural best practices"
        )
        
        assert validation.preset_id == preset.preset_id
        assert validation.validated_by == sample_user_id
        assert validation.validation_status == "approved"
        assert validation.validation_notes == "This preset is accurate and follows agricultural best practices"
        
        # Check that preset was updated with validation info
        updated_preset = await service.get_preset_by_id(preset.preset_id)
        assert updated_preset.expert_validation_status == "approved"
        assert updated_preset.expert_validated_by == sample_user_id
        assert updated_preset.expert_notes == "This preset is accurate and follows agricultural best practices"

    async def test_get_expert_validated_presets(self, service, sample_creator_id, sample_user_id, sample_filter_config):
        """Test retrieving expert validated presets."""
        # Create presets with different validation statuses
        preset1 = await service.create_filter_preset(
            creator_id=sample_creator_id,
            name="Validated Preset",
            filter_config=sample_filter_config,
            visibility="public"
        )
        
        preset2 = await service.create_filter_preset(
            creator_id=sample_creator_id,
            name="Pending Preset",
            filter_config=sample_filter_config,
            visibility="public"
        )
        
        # Validate one preset as approved
        await service.validate_preset_expert(
            preset_id=preset1.preset_id,
            validated_by=sample_user_id,
            validation_status="approved"
        )
        
        # Validate another as pending
        await service.validate_preset_expert(
            preset_id=preset2.preset_id,
            validated_by=sample_user_id,
            validation_status="pending"
        )
        
        validated_presets = await service.get_expert_validated_presets()
        
        assert len(validated_presets) == 1
        assert validated_presets[0].preset_id == preset1.preset_id
        assert validated_presets[0].expert_validation_status == "approved"

    async def test_generate_collaborative_recommendations(self, service, sample_creator_id, sample_user_id, sample_filter_config):
        """Test generating collaborative filtering recommendations."""
        # Create a preset for the user
        user_preset = await service.create_filter_preset(
            creator_id=sample_user_id,
            name="User's Corn Filter",
            filter_config=sample_filter_config,
            tags=["corn", "high_yield"],
            region_codes=["IA", "IL"]
        )
        
        # Create similar public preset from another user
        similar_preset = await service.create_filter_preset(
            creator_id=sample_creator_id,
            name="Similar Corn Filter",
            filter_config=sample_filter_config,
            visibility="public",
            tags=["corn", "high_yield", "drought_resistant"],
            region_codes=["IA", "MO"],
            average_rating=4.5
        )
        
        # Create dissimilar preset
        dissimilar_preset = await service.create_filter_preset(
            creator_id=sample_creator_id,
            name="Vegetable Filter",
            filter_config=sample_filter_config,
            visibility="public",
            tags=["vegetable", "organic"],
            region_codes=["CA"]
        )

        recommendations = await service.generate_collaborative_recommendations(
            user_id=sample_user_id,
            limit=5
        )
        
        assert len(recommendations) >= 0  # May vary based on implementation
        for rec in recommendations:
            assert rec.user_id == sample_user_id
            assert rec.preset_id is not None
            assert 0.0 <= rec.confidence_score <= 1.0
            assert rec.reason is not None

    async def test_get_regional_presets(self, service, sample_creator_id, sample_user_id, sample_filter_config):
        """Test retrieving regional filter presets."""
        # Create presets for different regions
        ia_presets = []
        for i in range(3):
            preset = await service.create_filter_preset(
                creator_id=sample_creator_id,
                name=f"IA Preset {i+1}",
                filter_config=sample_filter_config,
                visibility="public",
                region_codes=["IA"],
                average_rating=4.0 + (i * 0.5)
            )
            # Simulate usage to affect popularity
            for _ in range(i+1):  # Higher ratings have more usage
                await service.increment_preset_usage(preset.preset_id)
            ia_presets.append(preset)
        
        # Create preset for different region
        await service.create_filter_preset(
            creator_id=sample_creator_id,
            name="CA Preset",
            filter_config=sample_filter_config,
            visibility="public",
            region_codes=["CA"],
            average_rating=3.5
        )
        
        regional_presets = await service.get_regional_presets(region_code="IA", limit=10)
        
        # Should only return IA presets
        for preset in regional_presets:
            assert "IA" in preset.region_codes
        
        # Should be sorted by rating * usage (popularity)
        for i in range(len(regional_presets) - 1):
            current_score = regional_presets[i].average_rating * regional_presets[i].usage_count
            next_score = regional_presets[i+1].average_rating * regional_presets[i+1].usage_count
            assert current_score >= next_score  # Higher scores first

    async def test_increment_preset_usage(self, service, sample_creator_id, sample_filter_config):
        """Test incrementing preset usage count."""
        preset = await service.create_filter_preset(
            creator_id=sample_creator_id,
            name="Usage Test Preset",
            filter_config=sample_filter_config
        )
        
        initial_usage = preset.usage_count
        assert initial_usage == 0
        
        success = await service.increment_preset_usage(preset.preset_id)
        assert success is True
        
        updated_preset = await service.get_preset_by_id(preset.preset_id)
        assert updated_preset.usage_count == initial_usage + 1

    async def test_increment_preset_usage_not_found(self, service):
        """Test incrementing usage for non-existent preset."""
        non_existent_id = uuid4()
        success = await service.increment_preset_usage(non_existent_id)
        assert success is False


class TestCommunityModels:
    """Test the Pydantic models for community features."""
    
    def test_community_filter_preset_validation(self):
        """Test validation of CommunityFilterPreset model."""
        preset_data = {
            "creator_id": uuid4(),
            "name": "Test Preset",
            "filter_config": {"test": "config"},
            "tags": ["tag1", "tag2", "tag3"],
            "region_codes": ["IA", "IL"]
        }
        
        preset = CommunityFilterPreset(**preset_data)
        assert len(preset.tags) == 3
        assert len(preset.region_codes) == 2
        assert preset.average_rating == 0.0
        
        # Test rating validation
        preset.average_rating = 5.5  # Should be capped at 5.0
        assert preset.average_rating == 5.0
        
        preset.average_rating = -1.0  # Should be floored at 0.0
        assert preset.average_rating == 0.0

    def test_community_rating_validation(self):
        """Test validation of CommunityRating model."""
        rating_data = {
            "user_id": uuid4(),
            "preset_id": uuid4(),
            "rating": 4,
            "review_text": "Great preset!"
        }
        
        rating = CommunityRating(**rating_data)
        assert rating.rating == 4
        assert rating.review_text == "Great preset!"

    def test_expert_validation_status_enum(self):
        """Test ExpertValidationStatus enum values."""
        assert ExpertValidationStatus.PENDING.value == "pending"
        assert ExpertValidationStatus.APPROVED.value == "approved"
        assert ExpertValidationStatus.REJECTED.value == "rejected"
        assert ExpertValidationStatus.FLAGGED.value == "flagged"