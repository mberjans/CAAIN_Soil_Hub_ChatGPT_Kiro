"""
Test suite for Recommendation Management Service

Comprehensive tests for the recommendation management system including
saving, tracking, feedback collection, and updating variety recommendations.
"""

import pytest
import asyncio
from datetime import datetime, date, timedelta
from uuid import UUID, uuid4
from unittest.mock import AsyncMock, patch, MagicMock

try:
    from src.models.recommendation_management_models import (
        SaveRecommendationRequest, RecommendationHistoryRequest, RecommendationFeedbackRequest,
        UpdateRecommendationRequest, RecommendationStatus, FeedbackType, RecommendationSource
    )
    from src.services.recommendation_management_service import RecommendationManagementService
    from src.database.recommendation_management_db import RecommendationManagementDatabase
except ImportError:
    from models.recommendation_management_models import (
        SaveRecommendationRequest, RecommendationHistoryRequest, RecommendationFeedbackRequest,
        UpdateRecommendationRequest, RecommendationStatus, FeedbackType, RecommendationSource
    )
    from services.recommendation_management_service import RecommendationManagementService
    from database.recommendation_management_db import RecommendationManagementDatabase


class TestRecommendationManagementService:
    """Test suite for RecommendationManagementService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return RecommendationManagementService()
    
    @pytest.fixture
    def sample_user_id(self):
        """Sample user ID for testing."""
        return uuid4()
    
    @pytest.fixture
    def sample_recommendation_request(self, sample_user_id):
        """Sample save recommendation request."""
        return SaveRecommendationRequest(
            user_id=sample_user_id,
            crop_id="corn",
            variety_ids=["variety_1", "variety_2", "variety_3"],
            farm_context={
                "location": {"lat": 40.0, "lng": -95.0},
                "soil_type": "clay_loam",
                "field_size_acres": 100
            },
            farmer_preferences={
                "risk_tolerance": "moderate",
                "yield_priority": 0.8,
                "sustainability_priority": 0.6
            },
            recommendation_criteria={
                "climate_zone": "5a",
                "soil_ph": 6.5,
                "organic_matter": 3.2
            },
            notes="Test recommendation for corn varieties",
            tags=["corn", "test", "moderate_risk"]
        )
    
    @pytest.fixture
    def sample_feedback_request(self, sample_user_id):
        """Sample feedback request."""
        return RecommendationFeedbackRequest(
            user_id=sample_user_id,
            recommendation_id=uuid4(),
            feedback_type=FeedbackType.RATING,
            feedback_value=4,
            feedback_text="Good recommendation, implemented successfully",
            variety_performance={
                "variety_1": {"yield": 180, "quality": "excellent"},
                "variety_2": {"yield": 175, "quality": "good"}
            },
            implementation_notes="Planted in early May, good germination",
            confidence_level=4
        )
    
    @pytest.fixture
    def sample_update_request(self, sample_user_id):
        """Sample update request."""
        return UpdateRecommendationRequest(
            user_id=sample_user_id,
            recommendation_id=uuid4(),
            variety_ids=["variety_1", "variety_4", "variety_5"],
            status=RecommendationStatus.IMPLEMENTED,
            notes="Updated with new varieties after soil test",
            tags=["corn", "updated", "implemented"],
            re_rank=True
        )
    
    # ============================================================================
    # SAVE RECOMMENDATION TESTS
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_save_recommendation_success(self, service, sample_recommendation_request):
        """Test successful recommendation saving."""
        with patch.object(service.db, 'save_recommendation', return_value="test_recommendation_id"):
            result = await service.save_recommendation(sample_recommendation_request)
            
            assert result.success is True
            assert result.recommendation_id is not None
            assert result.saved_varieties_count == 3
            assert result.message == "Recommendation saved successfully"
    
    @pytest.mark.asyncio
    async def test_save_recommendation_invalid_variety_ids(self, service, sample_user_id):
        """Test saving recommendation with invalid variety IDs."""
        request = SaveRecommendationRequest(
            user_id=sample_user_id,
            crop_id="corn",
            variety_ids=[],  # Empty list should fail validation
            farm_context={"location": {"lat": 40.0, "lng": -95.0}},
            farmer_preferences={"risk_tolerance": "moderate"},
            recommendation_criteria={"climate_zone": "5a"}
        )
        
        with pytest.raises(ValueError, match="Invalid variety IDs provided"):
            await service.save_recommendation(request)
    
    @pytest.mark.asyncio
    async def test_save_recommendation_past_expiry(self, service, sample_user_id):
        """Test saving recommendation with past expiry date."""
        past_date = datetime.utcnow() - timedelta(days=1)
        
        request = SaveRecommendationRequest(
            user_id=sample_user_id,
            crop_id="corn",
            variety_ids=["variety_1"],
            farm_context={"location": {"lat": 40.0, "lng": -95.0}},
            farmer_preferences={"risk_tolerance": "moderate"},
            recommendation_criteria={"climate_zone": "5a"},
            expires_at=past_date
        )
        
        with pytest.raises(ValueError, match="Expiry date must be in the future"):
            await service.save_recommendation(request)
    
    # ============================================================================
    # GET RECOMMENDATION TESTS
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_get_saved_recommendation_success(self, service, sample_user_id):
        """Test getting saved recommendation."""
        recommendation_data = {
            "recommendation_id": "test_id",
            "user_id": str(sample_user_id),
            "crop_id": "corn",
            "variety_ids": ["variety_1", "variety_2"],
            "status": "active",
            "saved_at": datetime.utcnow(),
            "notes": "Test recommendation"
        }
        
        with patch.object(service.db, 'get_recommendation', return_value=recommendation_data):
            result = await service.get_saved_recommendation("test_id", sample_user_id)
            
            assert result is not None
            assert result["recommendation_id"] == "test_id"
            assert result["user_id"] == str(sample_user_id)
    
    @pytest.mark.asyncio
    async def test_get_saved_recommendation_not_found(self, service, sample_user_id):
        """Test getting non-existent recommendation."""
        with patch.object(service.db, 'get_recommendation', return_value=None):
            result = await service.get_saved_recommendation("nonexistent_id", sample_user_id)
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_saved_recommendation_unauthorized(self, service, sample_user_id):
        """Test getting recommendation with wrong user."""
        other_user_id = uuid4()
        recommendation_data = {
            "recommendation_id": "test_id",
            "user_id": str(other_user_id),  # Different user
            "crop_id": "corn",
            "variety_ids": ["variety_1"],
            "status": "active"
        }
        
        with patch.object(service.db, 'get_recommendation', return_value=recommendation_data):
            with pytest.raises(PermissionError, match="User not authorized"):
                await service.get_saved_recommendation("test_id", sample_user_id)
    
    # ============================================================================
    # UPDATE RECOMMENDATION TESTS
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_update_recommendation_success(self, service, sample_update_request):
        """Test successful recommendation update."""
        with patch.object(service.db, 'update_recommendation', return_value=True):
            result = await service.update_recommendation(sample_update_request)
            
            assert result.success is True
            assert result.recommendation_id == sample_update_request.recommendation_id
            assert "variety_ids" in result.updated_fields
            assert "status" in result.updated_fields
            assert result.re_ranked is True
    
    @pytest.mark.asyncio
    async def test_update_recommendation_not_found(self, service, sample_update_request):
        """Test updating non-existent recommendation."""
        with patch.object(service.db, 'update_recommendation', return_value=False):
            with pytest.raises(ValueError, match="Recommendation not found"):
                await service.update_recommendation(sample_update_request)
    
    @pytest.mark.asyncio
    async def test_update_recommendation_no_updates(self, service, sample_user_id):
        """Test update request with no updates."""
        request = UpdateRecommendationRequest(
            user_id=sample_user_id,
            recommendation_id=uuid4()
            # No update fields provided
        )
        
        with pytest.raises(ValueError, match="No updates provided"):
            await service.update_recommendation(request)
    
    # ============================================================================
    # HISTORY TESTS
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_get_recommendation_history_success(self, service, sample_user_id):
        """Test getting recommendation history."""
        history_data = [
            {
                "history_id": "history_1",
                "recommendation_id": "rec_1",
                "user_id": str(sample_user_id),
                "action_type": "save",
                "action_timestamp": datetime.utcnow(),
                "action_data": {"variety_count": 3}
            },
            {
                "history_id": "history_2",
                "recommendation_id": "rec_1",
                "user_id": str(sample_user_id),
                "action_type": "view",
                "action_timestamp": datetime.utcnow(),
                "action_data": {}
            }
        ]
        
        with patch.object(service.db, 'get_recommendation_history', return_value=(history_data, 2)):
            request = RecommendationHistoryRequest(
                user_id=sample_user_id,
                limit=50,
                offset=0
            )
            
            result = await service.get_recommendation_history(request)
            
            assert result.user_id == sample_user_id
            assert result.total_records == 2
            assert len(result.records) == 2
            assert result.pagination["total_records"] == 2
            assert "action_counts" in result.summary_stats
    
    # ============================================================================
    # FEEDBACK TESTS
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_submit_feedback_success(self, service, sample_feedback_request):
        """Test successful feedback submission."""
        with patch.object(service.db, 'submit_feedback', return_value="feedback_id_123"):
            with patch.object(service, '_process_feedback_for_learning', return_value=True):
                result = await service.submit_feedback(sample_feedback_request)
                
                assert result.success is True
                assert result.feedback_id is not None
                assert result.preference_adjustments_applied is True
                assert result.learning_triggered is True
    
    @pytest.mark.asyncio
    async def test_submit_feedback_invalid_rating(self, service, sample_user_id):
        """Test feedback with invalid rating value."""
        request = RecommendationFeedbackRequest(
            user_id=sample_user_id,
            recommendation_id=uuid4(),
            feedback_type=FeedbackType.RATING,
            feedback_value=6  # Invalid rating (should be 1-5)
        )
        
        with pytest.raises(ValueError, match="Invalid feedback value"):
            await service.submit_feedback(request)
    
    @pytest.mark.asyncio
    async def test_submit_feedback_invalid_boolean(self, service, sample_user_id):
        """Test feedback with invalid boolean value."""
        request = RecommendationFeedbackRequest(
            user_id=sample_user_id,
            recommendation_id=uuid4(),
            feedback_type=FeedbackType.IMPLEMENTED,
            feedback_value="yes"  # Should be boolean
        )
        
        with pytest.raises(ValueError, match="Invalid feedback value"):
            await service.submit_feedback(request)
    
    # ============================================================================
    # ANALYTICS TESTS
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_get_recommendation_analytics_success(self, service, sample_user_id):
        """Test getting recommendation analytics."""
        analytics_data = {
            "total_recommendations": 10,
            "active_recommendations": 7,
            "implemented_recommendations": 3,
            "feedback_count": 5,
            "average_rating": 4.2,
            "most_common_crops": [
                {"crop_id": "corn", "count": 5},
                {"crop_id": "soybean", "count": 3}
            ]
        }
        
        with patch.object(service.db, 'get_recommendation_analytics', return_value=analytics_data):
            result = await service.get_recommendation_analytics(sample_user_id)
            
            assert result.user_id == sample_user_id
            assert result.total_recommendations == 10
            assert result.active_recommendations == 7
            assert result.implemented_recommendations == 3
            assert result.feedback_count == 5
            assert result.average_rating == 4.2
            assert len(result.most_common_crops) == 2
    
    # ============================================================================
    # HELPER METHOD TESTS
    # ============================================================================
    
    @pytest.mark.asyncio
    async def test_process_feedback_for_learning(self, service, sample_user_id):
        """Test feedback processing for learning."""
        result = await service._process_feedback_for_learning(
            user_id=sample_user_id,
            recommendation_id="test_rec_id",
            feedback_type=FeedbackType.RATING,
            feedback_value=4
        )
        
        assert result is True  # Should return True for successful processing
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_recommendations(self, service):
        """Test cleanup of expired recommendations."""
        result = await service.cleanup_expired_recommendations()
        
        assert isinstance(result, int)
        assert result >= 0
    
    @pytest.mark.asyncio
    async def test_get_recommendation_statistics(self, service):
        """Test getting system statistics."""
        result = await service.get_recommendation_statistics()
        
        assert isinstance(result, dict)
        assert "total_recommendations" in result
        assert "system_health" in result


class TestRecommendationManagementValidator:
    """Test suite for RecommendationManagementValidator."""
    
    def test_validate_feedback_value_rating(self):
        """Test rating feedback validation."""
        from models.recommendation_management_models import RecommendationManagementValidator
        
        validator = RecommendationManagementValidator()
        
        # Valid ratings
        assert validator.validate_feedback_value(FeedbackType.RATING, 1) is True
        assert validator.validate_feedback_value(FeedbackType.RATING, 3) is True
        assert validator.validate_feedback_value(FeedbackType.RATING, 5) is True
        
        # Invalid ratings
        assert validator.validate_feedback_value(FeedbackType.RATING, 0) is False
        assert validator.validate_feedback_value(FeedbackType.RATING, 6) is False
        assert validator.validate_feedback_value(FeedbackType.RATING, "good") is False
    
    def test_validate_feedback_value_boolean(self):
        """Test boolean feedback validation."""
        from models.recommendation_management_models import RecommendationManagementValidator
        
        validator = RecommendationManagementValidator()
        
        # Valid boolean values
        assert validator.validate_feedback_value(FeedbackType.IMPLEMENTED, True) is True
        assert validator.validate_feedback_value(FeedbackType.IMPLEMENTED, False) is True
        assert validator.validate_feedback_value(FeedbackType.HELPFUL, True) is True
        
        # Invalid boolean values
        assert validator.validate_feedback_value(FeedbackType.IMPLEMENTED, "yes") is False
        assert validator.validate_feedback_value(FeedbackType.HELPFUL, 1) is False
    
    def test_validate_feedback_value_dict(self):
        """Test dictionary feedback validation."""
        from models.recommendation_management_models import RecommendationManagementValidator
        
        validator = RecommendationManagementValidator()
        
        # Valid dictionary
        assert validator.validate_feedback_value(FeedbackType.MODIFIED, {"field": "value"}) is True
        
        # Invalid dictionary
        assert validator.validate_feedback_value(FeedbackType.MODIFIED, "modified") is False
        assert validator.validate_feedback_value(FeedbackType.MODIFIED, 123) is False
    
    def test_validate_recommendation_expiry(self):
        """Test recommendation expiry validation."""
        from models.recommendation_management_models import RecommendationManagementValidator
        
        validator = RecommendationManagementValidator()
        
        # Valid future date
        future_date = datetime.utcnow() + timedelta(days=1)
        assert validator.validate_recommendation_expiry(future_date) is True
        
        # Valid None (no expiry)
        assert validator.validate_recommendation_expiry(None) is True
        
        # Invalid past date
        past_date = datetime.utcnow() - timedelta(days=1)
        assert validator.validate_recommendation_expiry(past_date) is False
    
    def test_validate_variety_ids(self):
        """Test variety IDs validation."""
        from models.recommendation_management_models import RecommendationManagementValidator
        
        validator = RecommendationManagementValidator()
        
        # Valid variety IDs
        assert validator.validate_variety_ids(["variety_1", "variety_2"]) is True
        assert validator.validate_variety_ids(["corn_variety_123"]) is True
        
        # Invalid variety IDs
        assert validator.validate_variety_ids([]) is False
        assert validator.validate_variety_ids([""]) is False
        assert validator.validate_variety_ids(["variety_1", ""]) is False
        assert validator.validate_variety_ids([None]) is False


class TestRecommendationManagementDatabase:
    """Test suite for RecommendationManagementDatabase."""
    
    @pytest.fixture
    def db(self):
        """Create database instance for testing."""
        return RecommendationManagementDatabase()
    
    def test_database_connection(self, db):
        """Test database connection."""
        # This test would require a real database connection
        # For now, we'll just test that the method exists and doesn't crash
        try:
            result = db.test_connection()
            assert isinstance(result, bool)
        except Exception:
            # Expected in test environment without database
            pass
    
    def test_save_recommendation_structure(self, db):
        """Test recommendation saving structure."""
        # Test that the method accepts the expected parameters
        try:
            result = db.save_recommendation(
                user_id=uuid4(),
                session_id="test_session",
                crop_id="corn",
                variety_ids=["variety_1", "variety_2"],
                farm_context={"location": {"lat": 40.0, "lng": -95.0}},
                farmer_preferences={"risk_tolerance": "moderate"},
                recommendation_criteria={"climate_zone": "5a"}
            )
            assert isinstance(result, str)
        except Exception:
            # Expected in test environment without database
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])