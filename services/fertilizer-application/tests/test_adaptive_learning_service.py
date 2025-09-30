"""
Comprehensive tests for the adaptive learning service.

This module tests all aspects of the adaptive recommendation learning system
including outcome tracking, farmer feedback integration, ML model training,
regional adaptation, farm-specific learning, and seasonal adjustments.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from uuid import uuid4

from src.services.adaptive_learning_service import (
    AdaptiveLearningService, FeedbackType, RecommendationOutcome,
    LearningMetrics, AdaptationProfile
)
from src.models.application_models import (
    ApplicationRequest, ApplicationResponse, ApplicationMethod,
    FieldConditions, CropRequirements, FertilizerSpecification,
    ApplicationMethodType, FertilizerForm, EquipmentType
)
from src.models.application_models import EquipmentSpecification


class TestAdaptiveLearningService:
    """Test suite for the adaptive learning service."""
    
    @pytest.fixture
    def service(self):
        """Create a test instance of the adaptive learning service."""
        return AdaptiveLearningService()
    
    @pytest.fixture
    def sample_field_conditions(self):
        """Create sample field conditions for testing."""
        return FieldConditions(
            field_size_acres=100.0,
            soil_type="clay_loam",
            soil_ph=6.5,
            organic_matter_percent=2.5,
            drainage_class="well_drained",
            slope_percent=2.0,
            irrigation_available=True
        )
    
    @pytest.fixture
    def sample_crop_requirements(self):
        """Create sample crop requirements for testing."""
        return CropRequirements(
            crop_type="corn",
            growth_stage="V6",
            target_yield=180.0,
            planting_date=datetime(2024, 4, 15),
            harvest_date=datetime(2024, 9, 15)
        )
    
    @pytest.fixture
    def sample_fertilizer_specification(self):
        """Create sample fertilizer specification for testing."""
        return FertilizerSpecification(
            fertilizer_type="NPK",
            form=FertilizerForm.GRANULAR,
            npk_ratio="10-10-10",
            application_rate=150.0,
            cost_per_unit=0.5,
            release_rate="medium"
        )
    
    @pytest.fixture
    def sample_outcome_data(self):
        """Create sample outcome data for testing."""
        return {
            "application_date": datetime(2024, 5, 1),
            "harvest_date": datetime(2024, 9, 15),
            "actual_yield": 175.0,
            "predicted_yield": 180.0,
            "actual_cost_per_acre": 22.0,
            "predicted_cost_per_acre": 20.0,
            "labor_hours": 8.0,
            "equipment_issues": [],
            "runoff_incident": False,
            "nutrient_loss_percent": 5.0,
            "farmer_rating": 4,
            "farmer_comments": "Good results, would recommend",
            "would_recommend": True
        }
    
    @pytest.fixture
    def sample_application_request(self, sample_field_conditions, sample_crop_requirements, sample_fertilizer_specification):
        """Create sample application request for testing."""
        return ApplicationRequest(
            field_conditions=sample_field_conditions,
            crop_requirements=sample_crop_requirements,
            fertilizer_specification=sample_fertilizer_specification,
            available_equipment=[
                EquipmentSpecification(
                    equipment_type=EquipmentType.SPREADER,
                    capacity_tons=5.0,
                    efficiency_rating=0.8
                )
            ]
        )


class TestOutcomeTracking:
    """Test outcome tracking functionality."""
    
    @pytest.mark.asyncio
    async def test_track_recommendation_outcome_success(self, service, sample_field_conditions, 
                                                      sample_crop_requirements, sample_fertilizer_specification, 
                                                      sample_outcome_data):
        """Test successful outcome tracking."""
        recommendation_id = str(uuid4())
        farmer_id = "farmer_123"
        field_id = "field_456"
        method_type = ApplicationMethodType.BROADCAST
        
        outcome = await service.track_recommendation_outcome(
            recommendation_id=recommendation_id,
            farmer_id=farmer_id,
            field_id=field_id,
            method_type=method_type,
            field_conditions=sample_field_conditions,
            crop_requirements=sample_crop_requirements,
            fertilizer_specification=sample_fertilizer_specification,
            outcome_data=sample_outcome_data
        )
        
        assert outcome.recommendation_id == recommendation_id
        assert outcome.farmer_id == farmer_id
        assert outcome.field_id == field_id
        assert outcome.method_type == method_type
        assert outcome.actual_yield == 175.0
        assert outcome.predicted_yield == 180.0
        assert outcome.farmer_rating == 4
        assert outcome.yield_accuracy is not None
        assert outcome.cost_accuracy is not None
        
        # Verify outcome is stored
        assert recommendation_id in service.outcomes_db
        assert service.outcomes_db[recommendation_id] == outcome
    
    @pytest.mark.asyncio
    async def test_track_recommendation_outcome_accuracy_calculation(self, service, sample_field_conditions, 
                                                                   sample_crop_requirements, sample_fertilizer_specification):
        """Test accuracy calculation for outcomes."""
        recommendation_id = str(uuid4())
        farmer_id = "farmer_123"
        field_id = "field_456"
        method_type = ApplicationMethodType.BROADCAST
        
        outcome_data = {
            "actual_yield": 180.0,
            "predicted_yield": 200.0,
            "actual_cost_per_acre": 20.0,
            "predicted_cost_per_acre": 25.0
        }
        
        outcome = await service.track_recommendation_outcome(
            recommendation_id=recommendation_id,
            farmer_id=farmer_id,
            field_id=field_id,
            method_type=method_type,
            field_conditions=sample_field_conditions,
            crop_requirements=sample_crop_requirements,
            fertilizer_specification=sample_fertilizer_specification,
            outcome_data=outcome_data
        )
        
        # Yield accuracy: 1.0 - |180 - 200| / 200 = 1.0 - 0.1 = 0.9
        expected_yield_accuracy = 1.0 - abs(180.0 - 200.0) / 200.0
        assert abs(outcome.yield_accuracy - expected_yield_accuracy) < 0.001
        
        # Cost accuracy: 1.0 - |20 - 25| / 25 = 1.0 - 0.2 = 0.8
        expected_cost_accuracy = 1.0 - abs(20.0 - 25.0) / 25.0
        assert abs(outcome.cost_accuracy - expected_cost_accuracy) < 0.001


class TestFarmerFeedbackIntegration:
    """Test farmer feedback integration functionality."""
    
    @pytest.mark.asyncio
    async def test_integrate_farmer_feedback_success(self, service, sample_field_conditions, 
                                                   sample_crop_requirements, sample_fertilizer_specification, 
                                                   sample_outcome_data):
        """Test successful farmer feedback integration."""
        # First track an outcome
        recommendation_id = str(uuid4())
        farmer_id = "farmer_123"
        field_id = "field_456"
        method_type = ApplicationMethodType.BROADCAST
        
        await service.track_recommendation_outcome(
            recommendation_id=recommendation_id,
            farmer_id=farmer_id,
            field_id=field_id,
            method_type=method_type,
            field_conditions=sample_field_conditions,
            crop_requirements=sample_crop_requirements,
            fertilizer_specification=sample_fertilizer_specification,
            outcome_data=sample_outcome_data
        )
        
        # Now integrate feedback
        success = await service.integrate_farmer_feedback(
            recommendation_id=recommendation_id,
            feedback_type=FeedbackType.OVERALL_SATISFACTION,
            feedback_value=5,
            comments="Excellent results!"
        )
        
        assert success is True
        
        # Verify feedback is stored
        assert recommendation_id in service.feedback_db
        feedback = service.feedback_db[recommendation_id]
        assert feedback["feedback_type"] == FeedbackType.OVERALL_SATISFACTION
        assert feedback["feedback_value"] == 5
        assert feedback["comments"] == "Excellent results!"
        
        # Verify outcome is updated
        outcome = service.outcomes_db[recommendation_id]
        assert outcome.farmer_rating == 5
        assert outcome.farmer_comments == "Excellent results!"
    
    @pytest.mark.asyncio
    async def test_integrate_farmer_feedback_not_found(self, service):
        """Test farmer feedback integration when recommendation not found."""
        recommendation_id = "nonexistent_id"
        
        success = await service.integrate_farmer_feedback(
            recommendation_id=recommendation_id,
            feedback_type=FeedbackType.OVERALL_SATISFACTION,
            feedback_value=5
        )
        
        assert success is False


class TestAdaptationProfiles:
    """Test adaptation profile functionality."""
    
    @pytest.mark.asyncio
    async def test_update_adaptation_profile(self, service, sample_field_conditions, 
                                           sample_crop_requirements, sample_fertilizer_specification, 
                                           sample_outcome_data):
        """Test adaptation profile updates."""
        recommendation_id = str(uuid4())
        farmer_id = "farmer_123"
        field_id = "field_456"
        method_type = ApplicationMethodType.BROADCAST
        
        # Track outcome with good rating
        outcome_data = sample_outcome_data.copy()
        outcome_data["farmer_rating"] = 5
        
        await service.track_recommendation_outcome(
            recommendation_id=recommendation_id,
            farmer_id=farmer_id,
            field_id=field_id,
            method_type=method_type,
            field_conditions=sample_field_conditions,
            crop_requirements=sample_crop_requirements,
            fertilizer_specification=sample_fertilizer_specification,
            outcome_data=outcome_data
        )
        
        # Check adaptation profile is created
        profile_key = f"{farmer_id}_{field_id}"
        assert profile_key in service.adaptation_profiles
        
        profile = service.adaptation_profiles[profile_key]
        assert profile.farm_id == farmer_id
        assert profile.region_id is not None
        
        # Check soil type preferences are updated
        assert "clay_loam" in profile.soil_type_preferences
        assert profile.soil_type_preferences["clay_loam"] > 0
        
        # Check crop success patterns are updated (rating >= 4)
        assert "corn" in profile.crop_success_patterns
        assert profile.crop_success_patterns["corn"] > 0
        
        # Check seasonal factors are updated
        current_season = service._get_season(datetime.utcnow())
        assert current_season in profile.seasonal_factors
        assert profile.seasonal_factors[current_season] > 0


class TestRegionalAdaptation:
    """Test regional adaptation functionality."""
    
    @pytest.mark.asyncio
    async def test_apply_regional_adaptation(self, service, sample_application_request):
        """Test regional adaptation application."""
        farmer_id = "farmer_123"
        field_id = "field_456"
        
        # Create some regional data
        profile_key1 = f"{farmer_id}_field1"
        profile_key2 = f"farmer_456_field2"
        
        service.adaptation_profiles[profile_key1] = AdaptationProfile(
            region_id="region_1",
            farm_id=farmer_id,
            soil_type_preferences={"clay_loam": 0.8, "sandy_loam": 0.2},
            crop_success_patterns={},
            seasonal_factors={},
            equipment_efficiency={},
            cost_sensitivity=0.5,
            labor_preferences={},
            environmental_priorities={},
            last_updated=datetime.utcnow()
        )
        
        service.adaptation_profiles[profile_key2] = AdaptationProfile(
            region_id="region_1",
            farm_id="farmer_456",
            soil_type_preferences={"clay_loam": 0.6, "sandy_loam": 0.4},
            crop_success_patterns={},
            seasonal_factors={},
            equipment_efficiency={},
            cost_sensitivity=0.5,
            labor_preferences={},
            environmental_priorities={},
            last_updated=datetime.utcnow()
        )
        
        regional_adjustments = await service._apply_regional_adaptation(
            farmer_id, field_id, sample_application_request
        )
        
        # Should aggregate preferences from region_1
        assert "clay_loam" in regional_adjustments
        assert "sandy_loam" in regional_adjustments
        
        # Clay loam should have higher preference (0.8 + 0.6 = 1.4, normalized)
        assert regional_adjustments["clay_loam"] > regional_adjustments["sandy_loam"]


class TestSeasonalAdjustments:
    """Test seasonal adjustment functionality."""
    
    @pytest.mark.asyncio
    async def test_apply_seasonal_adjustments_spring(self, service, sample_application_request):
        """Test seasonal adjustments for spring."""
        spring_date = datetime(2024, 4, 15)  # Spring
        
        seasonal_adjustments = await service._apply_seasonal_adjustments(
            sample_application_request, spring_date
        )
        
        assert "broadcast" in seasonal_adjustments
        assert "band" in seasonal_adjustments
        assert "injection" in seasonal_adjustments
        assert "foliar" in seasonal_adjustments
        
        # Spring should favor broadcast applications
        assert seasonal_adjustments["broadcast"] > 1.0
        assert seasonal_adjustments["band"] == 1.0
        assert seasonal_adjustments["injection"] < 1.0
        assert seasonal_adjustments["foliar"] < 1.0
    
    @pytest.mark.asyncio
    async def test_apply_seasonal_adjustments_summer(self, service, sample_application_request):
        """Test seasonal adjustments for summer."""
        summer_date = datetime(2024, 7, 15)  # Summer
        
        seasonal_adjustments = await service._apply_seasonal_adjustments(
            sample_application_request, summer_date
        )
        
        # Summer should favor injection applications (less volatilization)
        assert seasonal_adjustments["broadcast"] < 1.0
        assert seasonal_adjustments["band"] == 1.0
        assert seasonal_adjustments["injection"] > 1.0
        assert seasonal_adjustments["foliar"] > 1.0


class TestMLPredictions:
    """Test ML prediction functionality."""
    
    @pytest.mark.asyncio
    async def test_predict_method_outcomes(self, service, sample_application_request):
        """Test method outcome predictions."""
        method_scores = {
            "broadcast": 0.8,
            "band": 0.9,
            "injection": 0.7
        }
        
        predictions = await service._predict_method_outcomes(
            sample_application_request, method_scores
        )
        
        assert "broadcast" in predictions
        assert "band" in predictions
        assert "injection" in predictions
        
        for method_type, pred_data in predictions.items():
            assert "predicted_yield" in pred_data
            assert "predicted_cost" in pred_data
            assert "predicted_satisfaction" in pred_data
            assert "confidence" in pred_data
            assert pred_data["confidence"] == method_scores[method_type]
    
    def test_prepare_prediction_features(self, service, sample_application_request):
        """Test feature preparation for ML predictions."""
        features = service._prepare_prediction_features(
            sample_application_request, "broadcast"
        )
        
        assert features["field_size"] == 100.0
        assert features["soil_ph"] == 6.5
        assert features["organic_matter"] == 2.5
        assert features["method_type"] == "broadcast"
        assert features["fertilizer_rate"] == 150.0
        assert features["crop_type"] == "corn"
        assert features["target_yield"] == 180.0
        assert features["fertilizer_cost"] == 0.5
        assert features["equipment_available"] == 1


class TestRecommendationImprovement:
    """Test recommendation improvement functionality."""
    
    @pytest.mark.asyncio
    async def test_improve_recommendations(self, service, sample_application_request):
        """Test ML-improved recommendation generation."""
        farmer_id = "farmer_123"
        field_id = "field_456"
        
        # Mock the goal-based engine
        with patch.object(service.goal_engine, 'optimize_application_methods') as mock_optimize:
            mock_response = MagicMock()
            mock_response.method_scores = {
                "broadcast": 0.8,
                "band": 0.9,
                "injection": 0.7
            }
            mock_response.request_id = str(uuid4())
            mock_response.optimization_time_ms = 100.0
            mock_optimize.return_value = mock_response
            
            response = await service.improve_recommendations(
                request=sample_application_request,
                farmer_id=farmer_id,
                field_id=field_id
            )
            
            assert response is not None
            assert hasattr(response, 'recommended_methods')
            assert hasattr(response, 'analysis_summary')
            
            # Check that ML enhancement is indicated
            assert response.analysis_summary["ml_enhanced"] is True
            assert response.analysis_summary["adaptation_applied"] is True
            assert "learning_metrics" in response.analysis_summary


class TestLearningMetrics:
    """Test learning metrics functionality."""
    
    @pytest.mark.asyncio
    async def test_get_learning_metrics(self, service):
        """Test learning metrics retrieval."""
        metrics = await service.get_learning_metrics()
        
        assert isinstance(metrics, LearningMetrics)
        assert hasattr(metrics, 'model_accuracy')
        assert hasattr(metrics, 'prediction_error')
        assert hasattr(metrics, 'feedback_integration_rate')
        assert hasattr(metrics, 'adaptation_effectiveness')
        assert hasattr(metrics, 'seasonal_adjustment_accuracy')
        assert hasattr(metrics, 'regional_adaptation_score')
        assert hasattr(metrics, 'last_updated')
    
    @pytest.mark.asyncio
    async def test_update_learning_metrics(self, service, sample_field_conditions, 
                                         sample_crop_requirements, sample_fertilizer_specification, 
                                         sample_outcome_data):
        """Test learning metrics updates."""
        # Track some outcomes and feedback
        recommendation_id = str(uuid4())
        farmer_id = "farmer_123"
        field_id = "field_456"
        method_type = ApplicationMethodType.BROADCAST
        
        await service.track_recommendation_outcome(
            recommendation_id=recommendation_id,
            farmer_id=farmer_id,
            field_id=field_id,
            method_type=method_type,
            field_conditions=sample_field_conditions,
            crop_requirements=sample_crop_requirements,
            fertilizer_specification=sample_fertilizer_specification,
            outcome_data=sample_outcome_data
        )
        
        await service.integrate_farmer_feedback(
            recommendation_id=recommendation_id,
            feedback_type=FeedbackType.OVERALL_SATISFACTION,
            feedback_value=4
        )
        
        # Update metrics
        await service._update_learning_metrics()
        
        metrics = await service.get_learning_metrics()
        
        # Should have some feedback integration
        assert metrics.feedback_integration_rate > 0
        assert metrics.adaptation_effectiveness > 0


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_get_region_id(self, service):
        """Test region ID generation."""
        field_id = "field_123"
        region_id = service._get_region_id(field_id)
        
        assert region_id.startswith("region_")
        assert region_id.isdigit() or region_id.endswith("_")
        
        # Same field should get same region
        region_id2 = service._get_region_id(field_id)
        assert region_id == region_id2
    
    def test_get_season(self, service):
        """Test season determination."""
        # Winter months
        winter_date = datetime(2024, 1, 15)
        assert service._get_season(winter_date) == "winter"
        
        # Spring months
        spring_date = datetime(2024, 4, 15)
        assert service._get_season(spring_date) == "spring"
        
        # Summer months
        summer_date = datetime(2024, 7, 15)
        assert service._get_season(summer_date) == "summer"
        
        # Fall months
        fall_date = datetime(2024, 10, 15)
        assert service._get_season(fall_date) == "fall"


class TestDataExport:
    """Test data export functionality."""
    
    @pytest.mark.asyncio
    async def test_export_learning_data(self, service, sample_field_conditions, 
                                      sample_crop_requirements, sample_fertilizer_specification, 
                                      sample_outcome_data):
        """Test learning data export."""
        # Add some test data
        recommendation_id = str(uuid4())
        farmer_id = "farmer_123"
        field_id = "field_456"
        method_type = ApplicationMethodType.BROADCAST
        
        await service.track_recommendation_outcome(
            recommendation_id=recommendation_id,
            farmer_id=farmer_id,
            field_id=field_id,
            method_type=method_type,
            field_conditions=sample_field_conditions,
            crop_requirements=sample_crop_requirements,
            fertilizer_specification=sample_fertilizer_specification,
            outcome_data=sample_outcome_data
        )
        
        await service.integrate_farmer_feedback(
            recommendation_id=recommendation_id,
            feedback_type=FeedbackType.OVERALL_SATISFACTION,
            feedback_value=4
        )
        
        # Export data
        data = await service.export_learning_data()
        
        assert "outcomes" in data
        assert "feedback" in data
        assert "adaptation_profiles" in data
        assert "learning_metrics" in data
        
        # Check that our test data is included
        assert recommendation_id in data["outcomes"]
        assert recommendation_id in data["feedback"]
        
        # Check adaptation profile
        profile_key = f"{farmer_id}_{field_id}"
        assert profile_key in data["adaptation_profiles"]


# Integration tests
class TestAdaptiveLearningIntegration:
    """Integration tests for the adaptive learning system."""
    
    @pytest.mark.asyncio
    async def test_full_learning_cycle(self, service, sample_field_conditions, 
                                     sample_crop_requirements, sample_fertilizer_specification, 
                                     sample_outcome_data, sample_application_request):
        """Test a complete learning cycle from recommendation to improvement."""
        farmer_id = "farmer_123"
        field_id = "field_456"
        
        # Step 1: Generate initial recommendations
        with patch.object(service.goal_engine, 'optimize_application_methods') as mock_optimize:
            mock_response = MagicMock()
            mock_response.method_scores = {
                "broadcast": 0.8,
                "band": 0.9,
                "injection": 0.7
            }
            mock_response.request_id = str(uuid4())
            mock_response.optimization_time_ms = 100.0
            mock_optimize.return_value = mock_response
            
            initial_response = await service.improve_recommendations(
                request=sample_application_request,
                farmer_id=farmer_id,
                field_id=field_id
            )
        
        # Step 2: Track outcome
        recommendation_id = str(uuid4())
        method_type = ApplicationMethodType.BROADCAST
        
        outcome = await service.track_recommendation_outcome(
            recommendation_id=recommendation_id,
            farmer_id=farmer_id,
            field_id=field_id,
            method_type=method_type,
            field_conditions=sample_field_conditions,
            crop_requirements=sample_crop_requirements,
            fertilizer_specification=sample_fertilizer_specification,
            outcome_data=sample_outcome_data
        )
        
        # Step 3: Integrate feedback
        await service.integrate_farmer_feedback(
            recommendation_id=recommendation_id,
            feedback_type=FeedbackType.OVERALL_SATISFACTION,
            feedback_value=5,
            comments="Excellent results!"
        )
        
        # Step 4: Generate improved recommendations
        with patch.object(service.goal_engine, 'optimize_application_methods') as mock_optimize:
            mock_response = MagicMock()
            mock_response.method_scores = {
                "broadcast": 0.8,
                "band": 0.9,
                "injection": 0.7
            }
            mock_response.request_id = str(uuid4())
            mock_response.optimization_time_ms = 100.0
            mock_optimize.return_value = mock_response
            
            improved_response = await service.improve_recommendations(
                request=sample_application_request,
                farmer_id=farmer_id,
                field_id=field_id
            )
        
        # Step 5: Verify learning has occurred
        metrics = await service.get_learning_metrics()
        assert metrics.feedback_integration_rate > 0
        assert metrics.adaptation_effectiveness > 0
        
        # Step 6: Check adaptation profile
        profile = await service.get_adaptation_profile(farmer_id, field_id)
        assert profile is not None
        assert profile.farm_id == farmer_id
        assert "clay_loam" in profile.soil_type_preferences
        assert "corn" in profile.crop_success_patterns
        
        # Step 7: Export data
        data = await service.export_learning_data()
        assert recommendation_id in data["outcomes"]
        assert recommendation_id in data["feedback"]
        
        logger.info("Full learning cycle completed successfully")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
