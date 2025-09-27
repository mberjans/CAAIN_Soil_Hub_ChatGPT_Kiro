"""
Tests for Preference Learning and Adaptation System

Comprehensive test suite for the preference learning service, interaction tracking,
feedback processing, and preference adaptation algorithms.
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, MagicMock, patch

# Test imports
try:
    from src.services.preference_learning_service import (
        PreferenceLearningService, UserInteraction, FeedbackEvent
    )
    from src.api.learning_routes import (
        InteractionRequest, FeedbackRequest, 
        InteractionResponse, FeedbackResponse, LearningInsightsResponse
    )
except ImportError:
    from services.preference_learning_service import (
        PreferenceLearningService, UserInteraction, FeedbackEvent
    )
    from api.learning_routes import (
        InteractionRequest, FeedbackRequest,
        InteractionResponse, FeedbackResponse, LearningInsightsResponse
    )


@pytest.fixture
def learning_service():
    """Create a PreferenceLearningService instance for testing"""
    service = PreferenceLearningService()
    service._get_connection = AsyncMock()
    return service


@pytest.fixture
def sample_user_id():
    """Sample user ID for testing"""
    return uuid4()


@pytest.fixture
def sample_interaction(sample_user_id):
    """Sample user interaction for testing"""
    return UserInteraction(
        user_id=sample_user_id,
        interaction_type='view',
        crop_id='corn_001',
        interaction_data={
            'duration_seconds': 30,
            'scroll_depth': 0.8,
            'elements_viewed': ['description', 'images']
        },
        session_id='session_123'
    )


@pytest.fixture
def sample_feedback(sample_user_id):
    """Sample feedback event for testing"""
    return FeedbackEvent(
        user_id=sample_user_id,
        recommendation_id=uuid4(),
        feedback_type='rating',
        feedback_value=4,
        feedback_text='Very helpful recommendation',
        crop_ids=['corn_001', 'soybean_002']
    )


class TestUserInteraction:
    """Test UserInteraction data class"""
    
    def test_user_interaction_creation(self, sample_user_id):
        """Test UserInteraction object creation"""
        interaction = UserInteraction(
            user_id=sample_user_id,
            interaction_type='select',
            crop_id='wheat_001'
        )
        
        assert interaction.user_id == sample_user_id
        assert interaction.interaction_type == 'select'
        assert interaction.crop_id == 'wheat_001'
        assert interaction.interaction_data == {}
        assert isinstance(interaction.timestamp, datetime)
    
    def test_user_interaction_with_data(self, sample_user_id):
        """Test UserInteraction with interaction data"""
        interaction_data = {
            'selection_time_ms': 1500,
            'alternatives_considered': 3
        }
        
        interaction = UserInteraction(
            user_id=sample_user_id,
            interaction_type='select',
            crop_id='corn_001',
            interaction_data=interaction_data
        )
        
        assert interaction.interaction_data == interaction_data


class TestFeedbackEvent:
    """Test FeedbackEvent data class"""
    
    def test_feedback_event_creation(self, sample_user_id):
        """Test FeedbackEvent object creation"""
        feedback = FeedbackEvent(
            user_id=sample_user_id,
            recommendation_id=uuid4(),
            feedback_type='implemented',
            feedback_value=True
        )
        
        assert feedback.user_id == sample_user_id
        assert feedback.feedback_type == 'implemented'
        assert feedback.feedback_value is True
        assert feedback.crop_ids == []
        assert isinstance(feedback.timestamp, datetime)
    
    def test_feedback_event_with_crops(self, sample_user_id):
        """Test FeedbackEvent with crop IDs"""
        crop_ids = ['corn_001', 'soybean_002']
        
        feedback = FeedbackEvent(
            user_id=sample_user_id,
            recommendation_id=uuid4(),
            feedback_type='rating',
            feedback_value=5,
            crop_ids=crop_ids
        )
        
        assert feedback.crop_ids == crop_ids


class TestPreferenceLearningService:
    """Test PreferenceLearningService functionality"""
    
    @pytest.mark.asyncio
    async def test_track_user_interaction(self, learning_service, sample_interaction):
        """Test tracking user interactions"""
        # Mock database connection and execution
        mock_conn = AsyncMock()
        mock_conn.execute.return_value = None
        learning_service._get_connection.return_value = mock_conn
        learning_service._trigger_learning_if_ready = AsyncMock()
        
        result = await learning_service.track_user_interaction(sample_interaction)
        
        assert result is True
        mock_conn.execute.assert_called_once()
        learning_service._trigger_learning_if_ready.assert_called_once_with(sample_interaction.user_id)
    
    @pytest.mark.asyncio
    async def test_record_feedback(self, learning_service, sample_feedback):
        """Test recording user feedback"""
        # Mock database connection and execution
        mock_conn = AsyncMock()
        mock_conn.execute.return_value = None
        learning_service._get_connection.return_value = mock_conn
        learning_service._learn_from_feedback = AsyncMock()
        
        result = await learning_service.record_feedback(sample_feedback)
        
        assert result is True
        mock_conn.execute.assert_called_once()
        learning_service._learn_from_feedback.assert_called_once_with(sample_feedback)
    
    @pytest.mark.asyncio
    async def test_trigger_learning_ready(self, learning_service, sample_user_id):
        """Test triggering learning when user has enough interactions"""
        # Mock database connection and query result
        mock_conn = AsyncMock()
        mock_result = {'interaction_count': 10}  # Above threshold
        mock_conn.fetchrow.return_value = mock_result
        learning_service._get_connection.return_value = mock_conn
        learning_service._learn_from_interactions = AsyncMock()
        
        await learning_service._trigger_learning_if_ready(sample_user_id)
        
        learning_service._learn_from_interactions.assert_called_once_with(sample_user_id)
    
    @pytest.mark.asyncio
    async def test_trigger_learning_not_ready(self, learning_service, sample_user_id):
        """Test not triggering learning when user has insufficient interactions"""
        # Mock database connection and query result
        mock_conn = AsyncMock()
        mock_result = {'interaction_count': 3}  # Below threshold
        mock_conn.fetchrow.return_value = mock_result
        learning_service._get_connection.return_value = mock_conn
        learning_service._learn_from_interactions = AsyncMock()
        
        await learning_service._trigger_learning_if_ready(sample_user_id)
        
        learning_service._learn_from_interactions.assert_not_called()
    
    def test_analyze_interaction_patterns(self, learning_service):
        """Test interaction pattern analysis"""
        # Mock interaction data
        interactions = [
            {
                'interaction_type': 'view',
                'crop_id': 'corn_001',
                'crop_category': 'grain',
                'timestamp': datetime.now() - timedelta(hours=1)
            },
            {
                'interaction_type': 'select',
                'crop_id': 'corn_001',
                'crop_category': 'grain',
                'timestamp': datetime.now() - timedelta(hours=2)
            },
            {
                'interaction_type': 'save',
                'crop_id': 'soybean_001',
                'crop_category': 'legume',
                'timestamp': datetime.now() - timedelta(hours=3)
            }
        ]
        
        patterns = learning_service._analyze_interaction_patterns(interactions)
        
        assert 'crop_preferences' in patterns
        assert 'category_preferences' in patterns
        assert 'interaction_preferences' in patterns
        assert patterns['crop_preferences']['corn_001'] > 0
        assert patterns['category_preferences']['grain'] > 0
        assert patterns['interaction_preferences']['view'] == 1
    
    def test_normalize_pattern_scores(self, learning_service):
        """Test pattern score normalization"""
        patterns = {
            'crop_preferences': {'crop_a': 10, 'crop_b': 5, 'crop_c': 15},
            'category_preferences': {'grain': 20, 'legume': 10}
        }
        
        learning_service._normalize_pattern_scores(patterns)
        
        # Check that scores are normalized to [0, 1] range
        for scores in [patterns['crop_preferences'], patterns['category_preferences']]:
            assert all(0 <= score <= 1 for score in scores.values())
    
    def test_calculate_preference_adjustments(self, learning_service, sample_feedback):
        """Test preference adjustment calculations"""
        # Test positive rating
        sample_feedback.feedback_type = 'rating'
        sample_feedback.feedback_value = 5
        
        adjustments = learning_service._calculate_preference_adjustments(sample_feedback)
        
        assert adjustments['weight_multiplier'] > 1.0
        assert adjustments['preference_boost'] is True
        
        # Test negative rating
        sample_feedback.feedback_value = 1
        
        adjustments = learning_service._calculate_preference_adjustments(sample_feedback)
        
        assert adjustments['weight_multiplier'] < 1.0
        assert adjustments['preference_penalty'] is True
        
        # Test implementation feedback
        sample_feedback.feedback_type = 'implemented'
        sample_feedback.feedback_value = True
        
        adjustments = learning_service._calculate_preference_adjustments(sample_feedback)
        
        assert adjustments['weight_multiplier'] > 1.0
        assert adjustments['implementation_boost'] is True
    
    def test_calculate_learning_confidence(self, learning_service):
        """Test learning confidence calculation"""
        # Mock interaction and feedback statistics
        interactions = [{'count': 25}, {'count': 15}]  # 40 total interactions
        feedback_stats = [{'count': 5}, {'count': 3}]  # 8 total feedback
        
        confidence = learning_service._calculate_learning_confidence(interactions, feedback_stats)
        
        assert 0 <= confidence <= 1
        assert confidence > 0  # Should have some confidence with this data
    
    @pytest.mark.asyncio
    async def test_get_learning_insights(self, learning_service, sample_user_id):
        """Test getting learning insights"""
        # Mock database queries
        mock_conn = AsyncMock()
        mock_interactions = [
            {'interaction_type': 'view', 'count': 10, 'last_interaction': datetime.now()},
            {'interaction_type': 'select', 'count': 5, 'last_interaction': datetime.now()}
        ]
        mock_feedback = [
            {'feedback_type': 'rating', 'count': 3, 'avg_rating': 4.5}
        ]
        
        mock_conn.fetch.side_effect = [mock_interactions, mock_feedback]
        learning_service._get_connection.return_value = mock_conn
        learning_service.preference_manager.get_user_preferences = AsyncMock(return_value=[])
        
        insights = await learning_service.get_learning_insights(sample_user_id)
        
        assert insights['user_id'] == str(sample_user_id)
        assert 'interaction_summary' in insights
        assert 'feedback_summary' in insights
        assert 'learning_confidence' in insights


class TestLearningAPI:
    """Test Learning API endpoints"""
    
    def test_interaction_request_validation(self, sample_user_id):
        """Test InteractionRequest validation"""
        # Valid request
        request = InteractionRequest(
            user_id=sample_user_id,
            interaction_type='view',
            crop_id='corn_001',
            interaction_data={'duration_seconds': 30}
        )
        
        assert request.user_id == sample_user_id
        assert request.interaction_type == 'view'
        
        # Test validation of interaction_type
        with pytest.raises(ValueError):
            InteractionRequest(
                user_id=sample_user_id,
                interaction_type='invalid_type'
            )
    
    def test_feedback_request_validation(self, sample_user_id):
        """Test FeedbackRequest validation"""
        # Valid rating feedback
        request = FeedbackRequest(
            user_id=sample_user_id,
            recommendation_id=uuid4(),
            feedback_type='rating',
            feedback_value=4
        )
        
        assert request.feedback_value == 4
        
        # Test invalid rating
        with pytest.raises(ValueError):
            FeedbackRequest(
                user_id=sample_user_id,
                recommendation_id=uuid4(),
                feedback_type='rating',
                feedback_value=6  # Invalid rating > 5
            )
        
        # Test boolean feedback
        request = FeedbackRequest(
            user_id=sample_user_id,
            recommendation_id=uuid4(),
            feedback_type='implemented',
            feedback_value=True
        )
        
        assert request.feedback_value is True
        
        # Test invalid boolean feedback
        with pytest.raises(ValueError):
            FeedbackRequest(
                user_id=sample_user_id,
                recommendation_id=uuid4(),
                feedback_type='implemented',
                feedback_value='not_boolean'
            )


class TestIntegration:
    """Integration tests for the preference learning system"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_learning_workflow(self, learning_service, sample_user_id):
        """Test complete learning workflow from interaction to preference update"""
        # Mock dependencies
        learning_service._get_connection = AsyncMock()
        learning_service.preference_manager.get_user_preferences = AsyncMock(return_value=[])
        learning_service.preference_manager.create_preference = AsyncMock()
        
        # Step 1: Track multiple interactions
        interactions = [
            UserInteraction(
                user_id=sample_user_id,
                interaction_type='view',
                crop_id='corn_001'
            ),
            UserInteraction(
                user_id=sample_user_id,
                interaction_type='select',
                crop_id='corn_001'
            ),
            UserInteraction(
                user_id=sample_user_id,
                interaction_type='save',
                crop_id='corn_001'
            )
        ]
        
        for interaction in interactions:
            await learning_service.track_user_interaction(interaction)
        
        # Step 2: Record positive feedback
        feedback = FeedbackEvent(
            user_id=sample_user_id,
            recommendation_id=uuid4(),
            feedback_type='rating',
            feedback_value=5,
            crop_ids=['corn_001']
        )
        
        await learning_service.record_feedback(feedback)
        
        # Verify that learning methods were called
        assert learning_service._get_connection.call_count >= 4  # 3 interactions + 1 feedback
    
    @pytest.mark.asyncio
    async def test_preference_adaptation_workflow(self, learning_service, sample_user_id):
        """Test preference adaptation based on user behavior"""
        # Mock pattern analysis
        mock_patterns = {
            'crop_preferences': {'corn_001': 0.9, 'soybean_001': 0.7},
            'category_preferences': {'grain': 0.8, 'legume': 0.6},
            'interaction_preferences': {'select': 5, 'save': 3}
        }
        
        # Mock preference manager
        learning_service.preference_manager.get_user_preferences = AsyncMock(return_value=[])
        learning_service.preference_manager.create_preference = AsyncMock()
        
        # Test preference updates
        await learning_service._update_preferences_from_patterns(sample_user_id, mock_patterns)
        
        # Verify preference creation was called
        learning_service.preference_manager.create_preference.assert_called()


class TestErrorHandling:
    """Test error handling in the learning system"""
    
    @pytest.mark.asyncio
    async def test_database_error_handling(self, learning_service, sample_interaction):
        """Test handling of database errors"""
        # Mock database connection failure
        learning_service._get_connection.side_effect = Exception("Database connection failed")
        
        result = await learning_service.track_user_interaction(sample_interaction)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_invalid_feedback_handling(self, learning_service, sample_user_id):
        """Test handling of invalid feedback data"""
        invalid_feedback = FeedbackEvent(
            user_id=sample_user_id,
            recommendation_id=uuid4(),
            feedback_type='rating',
            feedback_value='invalid_rating'  # Should be numeric
        )
        
        # This should be handled gracefully
        adjustments = learning_service._calculate_preference_adjustments(invalid_feedback)
        
        # Should return empty adjustments for invalid data
        assert adjustments == {}


class TestPerformance:
    """Test performance aspects of the learning system"""
    
    def test_pattern_analysis_performance(self, learning_service):
        """Test pattern analysis with large datasets"""
        # Generate large interaction dataset
        interactions = []
        for i in range(1000):
            interactions.append({
                'interaction_type': 'view',
                'crop_id': f'crop_{i % 10}',
                'crop_category': f'category_{i % 5}',
                'timestamp': datetime.now() - timedelta(hours=i)
            })
        
        # This should complete within reasonable time
        import time
        start_time = time.time()
        patterns = learning_service._analyze_interaction_patterns(interactions)
        end_time = time.time()
        
        assert end_time - start_time < 1.0  # Should complete in under 1 second
        assert len(patterns['crop_preferences']) <= 10  # Should have detected crops
    
    def test_learning_confidence_calculation_performance(self, learning_service):
        """Test learning confidence calculation performance"""
        # Generate large statistics
        interactions = [{'count': i} for i in range(100)]
        feedback_stats = [{'count': i} for i in range(50)]
        
        import time
        start_time = time.time()
        confidence = learning_service._calculate_learning_confidence(interactions, feedback_stats)
        end_time = time.time()
        
        assert end_time - start_time < 0.1  # Should be very fast
        assert 0 <= confidence <= 1


# Test data fixtures
@pytest.fixture
def sample_learning_insights():
    """Sample learning insights data for testing"""
    return {
        'user_id': str(uuid4()),
        'learning_period_days': 30,
        'interaction_summary': {
            'view': {'count': 25, 'last_interaction': datetime.now().isoformat()},
            'select': {'count': 10, 'last_interaction': datetime.now().isoformat()}
        },
        'feedback_summary': {
            'rating': {'count': 5, 'avg_rating': 4.2}
        },
        'learned_preferences_count': 3,
        'total_preferences': 5,
        'learning_confidence': 0.75,
        'generated_at': datetime.now().isoformat()
    }


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])