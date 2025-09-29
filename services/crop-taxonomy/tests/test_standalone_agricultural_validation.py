"""
Tests for Standalone Agricultural Validation Service

This module contains comprehensive tests for the standalone agricultural validation
and expert review system.

Author: AI Assistant
Date: 2024-12-28
Version: 1.0
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any
from uuid import UUID, uuid4

from src.services.standalone_agricultural_validation_service import (
    StandaloneAgriculturalValidationService, ValidationResult, ValidationStatus,
    ValidationIssue, ValidationSeverity, ExpertReviewStatus, ExpertReviewer,
    ExpertReview, VarietyRecommendation, VarietyRecommendationRequest
)


class TestStandaloneAgriculturalValidationService:
    """Test suite for StandaloneAgriculturalValidationService."""

    @pytest.fixture
    def validation_service(self):
        """Create validation service instance."""
        return StandaloneAgriculturalValidationService()

    @pytest.fixture
    def sample_recommendations(self):
        """Sample variety recommendations for testing."""
        return [
            VarietyRecommendation(
                variety_id=uuid4(),
                variety_name="Test Corn Variety 1",
                overall_score=0.85,
                suitability_factors={"yield": 0.9, "disease_resistance": 0.8},
                individual_scores={"yield": 0.9, "disease_resistance": 0.8},
                weighted_contributions={"yield": 0.4, "disease_resistance": 0.3},
                score_details={"yield": "High yield potential", "disease_resistance": "Good resistance"},
                yield_expectation="High",
                risk_assessment={"overall_risk": "low"},
                management_difficulty="medium",
                performance_prediction={"regional_performance": {"confidence": 0.8}},
                adaptation_strategies=[{"strategy": "optimal_planting_date"}],
                recommended_practices=["fertilizer_application", "pest_monitoring"],
                economic_analysis={"roi": 0.15, "break_even_yield": 150, "expected_yield": 180}
            ),
            VarietyRecommendation(
                variety_id=uuid4(),
                variety_name="Test Corn Variety 2",
                overall_score=0.75,
                suitability_factors={"yield": 0.7, "disease_resistance": 0.9},
                individual_scores={"yield": 0.7, "disease_resistance": 0.9},
                weighted_contributions={"yield": 0.3, "disease_resistance": 0.4},
                score_details={"yield": "Moderate yield", "disease_resistance": "Excellent resistance"},
                yield_expectation="Medium",
                risk_assessment={"overall_risk": "medium"},
                management_difficulty="low",
                performance_prediction={"regional_performance": {"confidence": 0.9}},
                adaptation_strategies=[{"strategy": "disease_management"}],
                recommended_practices=["disease_monitoring"],
                economic_analysis={"roi": 0.12, "break_even_yield": 140, "expected_yield": 160}
            )
        ]

    @pytest.fixture
    def sample_request_context(self):
        """Sample request context for testing."""
        return VarietyRecommendationRequest(
            crop_id=uuid4(),
            crop_name="corn",
            location_data={"latitude": 40.0, "longitude": -95.0, "region": "Midwest"},
            soil_conditions={"ph": 6.5, "organic_matter": 3.2},
            farming_objectives=["high_yield", "disease_resistance"],
            production_system="conventional",
            available_equipment=["planter", "sprayer"],
            yield_priority_weight=0.4,
            quality_priority_weight=0.3,
            risk_management_weight=0.3,
            max_recommendations=10
        )

    @pytest.fixture
    def sample_regional_context(self):
        """Sample regional context for testing."""
        return {
            "region": "Midwest",
            "climate_zone": "6a",
            "average_yield": 150,
            "growing_season_days": 120
        }

    @pytest.fixture
    def sample_crop_context(self):
        """Sample crop context for testing."""
        return {
            "soil_ph": 6.5,
            "organic_matter": 3.2,
            "crop_type": "corn"
        }

    @pytest.mark.asyncio
    async def test_validate_recommendations_success(
        self, validation_service, sample_recommendations, sample_request_context,
        sample_regional_context, sample_crop_context
    ):
        """Test successful validation of recommendations."""
        result = await validation_service.validate_recommendations(
            recommendations=sample_recommendations,
            request_context=sample_request_context,
            regional_context=sample_regional_context,
            crop_context=sample_crop_context
        )

        assert result.status == ValidationStatus.COMPLETED
        assert result.overall_score > 0.0
        assert result.validation_id is not None
        assert result.validation_timestamp is not None
        assert result.validation_duration_ms > 0.0
        assert isinstance(result.issues, list)

    @pytest.mark.asyncio
    async def test_validate_recommendations_with_issues(
        self, validation_service, sample_request_context, sample_regional_context, sample_crop_context
    ):
        """Test validation with problematic recommendations."""
        # Create recommendations with issues
        problematic_recommendations = [
            VarietyRecommendation(
                variety_name="Low ROI Variety",
                overall_score=0.3,
                economic_analysis={"roi": 0.02},  # Very low ROI
                performance_prediction={"regional_performance": {"confidence": 0.3}}  # Low confidence
            ),
            VarietyRecommendation(
                variety_name="High Management Variety",
                overall_score=0.4,
                management_difficulty="high",
                economic_analysis={"roi": 0.08}
            )
        ]

        result = await validation_service.validate_recommendations(
            recommendations=problematic_recommendations,
            request_context=sample_request_context,
            regional_context=sample_regional_context,
            crop_context=sample_crop_context
        )

        assert result.status == ValidationStatus.COMPLETED
        assert len(result.issues) > 0
        assert any(issue.severity in [ValidationSeverity.WARNING, ValidationSeverity.ERROR] for issue in result.issues)

    @pytest.mark.asyncio
    async def test_expert_review_required_low_score(
        self, validation_service, sample_request_context, sample_regional_context, sample_crop_context
    ):
        """Test that expert review is required for low-scoring recommendations."""
        low_score_recommendations = [
            VarietyRecommendation(
                variety_name="Low Score Variety",
                overall_score=0.3,
                economic_analysis={"roi": 0.01},
                performance_prediction={"regional_performance": {"confidence": 0.2}}
            )
        ]

        result = await validation_service.validate_recommendations(
            recommendations=low_score_recommendations,
            request_context=sample_request_context,
            regional_context=sample_regional_context,
            crop_context=sample_crop_context
        )

        assert result.expert_review_required is True

    @pytest.mark.asyncio
    async def test_expert_review_required_edge_case_region(
        self, validation_service, sample_recommendations, sample_request_context, sample_crop_context
    ):
        """Test that expert review is required for edge case regions."""
        edge_case_regional_context = {
            "region": "arctic",  # Edge case region
            "climate_zone": "1a",
            "average_yield": 50,
            "growing_season_days": 60
        }

        result = await validation_service.validate_recommendations(
            recommendations=sample_recommendations,
            request_context=sample_request_context,
            regional_context=edge_case_regional_context,
            crop_context=sample_crop_context
        )

        assert result.expert_review_required is True

    @pytest.mark.asyncio
    async def test_expert_review_required_new_variety(
        self, validation_service, sample_request_context, sample_regional_context, sample_crop_context
    ):
        """Test that expert review is required for new varieties with low confidence."""
        new_variety_recommendations = [
            VarietyRecommendation(
                variety_name="New Variety",
                overall_score=0.8,
                performance_prediction={"regional_performance": {"confidence": 0.3}}  # Low confidence
            )
        ]

        result = await validation_service.validate_recommendations(
            recommendations=new_variety_recommendations,
            request_context=sample_request_context,
            regional_context=sample_regional_context,
            crop_context=sample_crop_context
        )

        assert result.expert_review_required is True

    @pytest.mark.asyncio
    async def test_create_expert_reviewer(self, validation_service):
        """Test creating an expert reviewer."""
        reviewer = await validation_service.create_expert_reviewer(
            name="Dr. John Smith",
            credentials="PhD in Agronomy, 20 years experience",
            specialization=["corn", "soybean", "precision_agriculture"],
            region="Midwest",
            institution="University of Illinois",
            contact_email="john.smith@illinois.edu"
        )

        assert reviewer.name == "Dr. John Smith"
        assert reviewer.credentials == "PhD in Agronomy, 20 years experience"
        assert "corn" in reviewer.specialization
        assert reviewer.region == "Midwest"
        assert reviewer.institution == "University of Illinois"
        assert reviewer.contact_email == "john.smith@illinois.edu"
        assert reviewer.is_active is True
        assert reviewer.review_count == 0

    @pytest.mark.asyncio
    async def test_submit_expert_review(self, validation_service):
        """Test submitting an expert review."""
        validation_id = uuid4()
        reviewer_id = uuid4()

        review_data = {
            "overall_score": 0.85,
            "agricultural_soundness": 0.9,
            "regional_applicability": 0.8,
            "economic_feasibility": 0.75,
            "farmer_practicality": 0.9,
            "comments": "Good variety selection with minor concerns about economic feasibility",
            "recommendations": ["Consider cost reduction strategies", "Monitor yield closely"],
            "concerns": ["High input costs"],
            "approval_conditions": ["Verify cost assumptions"],
            "overall_approval": True
        }

        review = await validation_service.submit_expert_review(
            validation_id=validation_id,
            reviewer_id=reviewer_id,
            review_data=review_data
        )

        assert review.validation_id == validation_id
        assert review.reviewer_id == reviewer_id
        assert review.overall_score == 0.85
        assert review.agricultural_soundness == 0.9
        assert review.regional_applicability == 0.8
        assert review.economic_feasibility == 0.75
        assert review.farmer_practicality == 0.9
        assert review.comments == "Good variety selection with minor concerns about economic feasibility"
        assert len(review.recommendations) == 2
        assert len(review.concerns) == 1
        assert review.overall_approval is True

    @pytest.mark.asyncio
    async def test_track_farmer_satisfaction(self, validation_service):
        """Test tracking farmer satisfaction."""
        recommendation_id = uuid4()
        farmer_id = uuid4()
        satisfaction_score = 4.5
        feedback = "Great recommendations, helped increase yield by 15%"

        # This should not raise an exception
        await validation_service.track_farmer_satisfaction(
            recommendation_id=recommendation_id,
            farmer_id=farmer_id,
            satisfaction_score=satisfaction_score,
            feedback=feedback
        )

    @pytest.mark.asyncio
    async def test_validation_with_extreme_soil_ph(self, validation_service, sample_recommendations, sample_request_context, sample_regional_context):
        """Test validation with extreme soil pH values."""
        extreme_ph_crop_context = {
            "soil_ph": 3.5,  # Very acidic
            "organic_matter": 3.2,
            "crop_type": "corn"
        }

        result = await validation_service.validate_recommendations(
            recommendations=sample_recommendations,
            request_context=sample_request_context,
            regional_context=sample_regional_context,
            crop_context=extreme_ph_crop_context
        )

        assert result.status == ValidationStatus.COMPLETED
        # Should have issues related to soil pH
        ph_issues = [issue for issue in result.issues if "soil_ph" in issue.category.lower()]
        assert len(ph_issues) > 0

    @pytest.mark.asyncio
    async def test_validation_with_low_yield_region(self, validation_service, sample_recommendations, sample_request_context, sample_crop_context):
        """Test validation with low yield region."""
        low_yield_regional_context = {
            "region": "Desert Southwest",
            "climate_zone": "9a",
            "average_yield": 80,  # Very low average yield
            "growing_season_days": 200
        }

        result = await validation_service.validate_recommendations(
            recommendations=sample_recommendations,
            request_context=sample_request_context,
            regional_context=low_yield_regional_context,
            crop_context=sample_crop_context
        )

        assert result.status == ValidationStatus.COMPLETED
        # Should have issues related to yield expectations
        yield_issues = [issue for issue in result.issues if "yield" in issue.category.lower()]
        assert len(yield_issues) > 0

    @pytest.mark.asyncio
    async def test_validation_performance(self, validation_service, sample_recommendations, sample_request_context, sample_regional_context, sample_crop_context):
        """Test validation performance."""
        start_time = datetime.utcnow()

        result = await validation_service.validate_recommendations(
            recommendations=sample_recommendations,
            request_context=sample_request_context,
            regional_context=sample_regional_context,
            crop_context=sample_crop_context
        )

        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        assert result.status == ValidationStatus.COMPLETED
        assert duration < 5.0  # Should complete within 5 seconds
        assert result.validation_duration_ms < 5000  # Should complete within 5000ms

    @pytest.mark.asyncio
    async def test_validation_with_empty_recommendations(self, validation_service, sample_request_context, sample_regional_context, sample_crop_context):
        """Test validation with empty recommendations list."""
        result = await validation_service.validate_recommendations(
            recommendations=[],
            request_context=sample_request_context,
            regional_context=sample_regional_context,
            crop_context=sample_crop_context
        )

        assert result.status == ValidationStatus.COMPLETED
        assert result.overall_score == 0.0
        assert len(result.issues) == 1
        assert result.issues[0].category == "empty_recommendations"

    @pytest.mark.asyncio
    async def test_validation_error_handling(self, validation_service):
        """Test validation error handling."""
        # Test with valid data but problematic scenarios that should cause validation errors
        problematic_recommendations = [
            VarietyRecommendation(
                variety_name="Problematic Variety",
                overall_score=0.3,  # Very low score
                suitability_factors={"yield": 0.1, "disease_resistance": 0.1},
                individual_scores={"yield": 0.1, "disease_resistance": 0.1},
                weighted_contributions={"yield": 0.5, "disease_resistance": 0.5},
                score_details={"yield": "Very low yield", "disease_resistance": "Poor resistance"},
                yield_expectation="Low",
                risk_assessment={"overall_risk": "high"},
                management_difficulty="high",
                performance_prediction={"regional_performance": {"confidence": 0.1}},
                adaptation_strategies=[{"strategy": "emergency_management"}],
                recommended_practices=["intensive_monitoring"],
                economic_analysis={"roi": -0.5, "break_even_yield": 200, "expected_yield": 50}
            )
        ]

        problematic_request_context = VarietyRecommendationRequest(
            crop_id=uuid4(),
            crop_name="corn",
            location_data={"latitude": 40.0, "longitude": -95.0, "region": "Midwest"},
            soil_conditions={"ph": 3.0, "organic_matter": 0.1},  # Extreme soil conditions
            farming_objectives=["high_yield", "disease_resistance"],
            production_system="conventional",
            available_equipment=["planter"],
            yield_priority_weight=0.4,
            quality_priority_weight=0.3,
            risk_management_weight=0.3,
            max_recommendations=10
        )

        result = await validation_service.validate_recommendations(
            recommendations=problematic_recommendations,
            request_context=problematic_request_context,
            regional_context={"region": "Midwest", "climate_zone": "6a", "average_yield": 150},
            crop_context={"soil_ph": 3.0, "organic_matter": 0.1, "crop_type": "corn"}
        )

        # Should complete but with issues and require expert review
        assert result.status == ValidationStatus.COMPLETED
        assert len(result.issues) > 0
        assert result.expert_review_required is True


class TestValidationMetrics:
    """Test validation metrics and reporting."""

    @pytest.fixture
    def validation_service(self):
        """Create validation service instance."""
        return StandaloneAgriculturalValidationService()

    @pytest.mark.asyncio
    async def test_validation_score_calculation(self, validation_service):
        """Test validation score calculation accuracy."""
        # Create recommendations with known scores
        recommendations = [
            VarietyRecommendation(
                variety_name="High Score Variety",
                overall_score=0.9,
                economic_analysis={"roi": 0.2},
                performance_prediction={"regional_performance": {"confidence": 0.9}}
            ),
            VarietyRecommendation(
                variety_name="Medium Score Variety",
                overall_score=0.7,
                economic_analysis={"roi": 0.1},
                performance_prediction={"regional_performance": {"confidence": 0.7}}
            )
        ]

        request_context = VarietyRecommendationRequest(crop_name="corn")
        regional_context = {"region": "Midwest", "average_yield": 150}
        crop_context = {"soil_ph": 6.5}

        result = await validation_service.validate_recommendations(
            recommendations=recommendations,
            request_context=request_context,
            regional_context=regional_context,
            crop_context=crop_context
        )

        assert result.overall_score > 0.0
        assert result.overall_score <= 1.0

    @pytest.mark.asyncio
    async def test_expert_review_thresholds(self, validation_service):
        """Test expert review threshold logic."""
        # Test low confidence threshold
        low_confidence_recommendations = [
            VarietyRecommendation(
                variety_name="Low Confidence Variety",
                overall_score=0.5,  # Below threshold
                performance_prediction={"regional_performance": {"confidence": 0.5}}
            )
        ]

        request_context = VarietyRecommendationRequest(crop_name="corn")
        regional_context = {"region": "Midwest", "average_yield": 150}
        crop_context = {"soil_ph": 6.5}

        result = await validation_service.validate_recommendations(
            recommendations=low_confidence_recommendations,
            request_context=request_context,
            regional_context=regional_context,
            crop_context=crop_context
        )

        assert result.expert_review_required is True


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])