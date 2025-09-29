"""
Tests for Agricultural Validation Service

This module contains comprehensive tests for the agricultural validation
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
from unittest.mock import AsyncMock, patch, MagicMock

from src.services.agricultural_validation_service import (
    AgriculturalValidationService, ValidationResult, ValidationStatus,
    ValidationIssue, ValidationSeverity, ExpertReviewStatus
)
from src.services.expert_review_service import (
    ExpertReviewService, ExpertReviewer, ExpertReview, ReviewAssignment,
    ReviewPriority, ReviewAssignmentStatus
)
from src.services.validation_metrics_service import (
    ValidationMetricsService, ValidationMetricsReport, MetricsPeriod
)
from src.models.validation_models import (
    ValidationRequest, ExpertReviewRequest, FarmerFeedback
)
from src.models.crop_variety_models import VarietyRecommendation
from src.models.service_models import VarietyRecommendationRequest


class TestAgriculturalValidationService:
    """Test suite for AgriculturalValidationService."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.fixture
    def validation_service(self, mock_db_session):
        """Create validation service instance."""
        return AgriculturalValidationService(mock_db_session)

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
            max_recommendations=5
        )

    @pytest.fixture
    def sample_regional_context(self):
        """Sample regional context for testing."""
        return {
            "region": "Midwest",
            "climate_zone": "5a",
            "growing_season_days": 150,
            "average_yield": 170,
            "frost_free_days": 180,
            "precipitation": 35.0
        }

    @pytest.fixture
    def sample_crop_context(self):
        """Sample crop context for testing."""
        return {
            "crop_type": "corn",
            "soil_ph": 6.5,
            "soil_type": "clay_loam",
            "drainage": "well_drained",
            "irrigation": "rainfed"
        }

    @pytest.mark.asyncio
    async def test_validate_recommendations_success(
        self,
        validation_service,
        sample_recommendations,
        sample_request_context,
        sample_regional_context,
        sample_crop_context
    ):
        """Test successful validation of recommendations."""
        # Mock database operations
        validation_service._store_validation_result = AsyncMock()
        
        result = await validation_service.validate_recommendations(
            recommendations=sample_recommendations,
            request_context=sample_request_context,
            regional_context=sample_regional_context,
            crop_context=sample_crop_context
        )
        
        assert isinstance(result, ValidationResult)
        assert result.status == ValidationStatus.COMPLETED
        assert result.validation_id is not None
        assert result.overall_score >= 0.0
        assert result.validation_duration_ms > 0.0
        assert result.regional_context == sample_regional_context
        assert result.crop_context == sample_crop_context

    @pytest.mark.asyncio
    async def test_validate_agricultural_soundness(
        self,
        validation_service,
        sample_recommendations,
        sample_request_context,
        sample_regional_context,
        sample_crop_context
    ):
        """Test agricultural soundness validation."""
        result = await validation_service._validate_agricultural_soundness(
            sample_recommendations,
            sample_request_context,
            sample_regional_context,
            sample_crop_context
        )
        
        assert result is not None
        assert "score" in result
        assert "issues" in result
        assert 0.0 <= result["score"] <= 1.0
        assert isinstance(result["issues"], list)

    @pytest.mark.asyncio
    async def test_validate_regional_applicability(
        self,
        validation_service,
        sample_recommendations,
        sample_request_context,
        sample_regional_context,
        sample_crop_context
    ):
        """Test regional applicability validation."""
        result = await validation_service._validate_regional_applicability(
            sample_recommendations,
            sample_request_context,
            sample_regional_context,
            sample_crop_context
        )
        
        assert result is not None
        assert "score" in result
        assert "issues" in result
        assert 0.0 <= result["score"] <= 1.0

    @pytest.mark.asyncio
    async def test_validate_economic_feasibility(
        self,
        validation_service,
        sample_recommendations,
        sample_request_context,
        sample_regional_context,
        sample_crop_context
    ):
        """Test economic feasibility validation."""
        result = await validation_service._validate_economic_feasibility(
            sample_recommendations,
            sample_request_context,
            sample_regional_context,
            sample_crop_context
        )
        
        assert result is not None
        assert "score" in result
        assert "issues" in result
        assert 0.0 <= result["score"] <= 1.0

    @pytest.mark.asyncio
    async def test_validate_farmer_practicality(
        self,
        validation_service,
        sample_recommendations,
        sample_request_context,
        sample_regional_context,
        sample_crop_context
    ):
        """Test farmer practicality validation."""
        result = await validation_service._validate_farmer_practicality(
            sample_recommendations,
            sample_request_context,
            sample_regional_context,
            sample_crop_context
        )
        
        assert result is not None
        assert "score" in result
        assert "issues" in result
        assert 0.0 <= result["score"] <= 1.0

    @pytest.mark.asyncio
    async def test_requires_expert_review_low_score(
        self,
        validation_service,
        sample_recommendations,
        sample_request_context
    ):
        """Test expert review requirement for low validation score."""
        validation_result = ValidationResult(
            validation_id=uuid4(),
            status=ValidationStatus.COMPLETED,
            overall_score=0.5,  # Below threshold
            issues=[],
            expert_review_required=False,
            validation_timestamp=datetime.utcnow(),
            validation_duration_ms=100.0,
            regional_context={},
            crop_context={}
        )
        
        requires_review = await validation_service._requires_expert_review(
            validation_result, sample_recommendations, sample_request_context
        )
        
        assert requires_review is True

    @pytest.mark.asyncio
    async def test_requires_expert_review_high_score(
        self,
        validation_service,
        sample_recommendations,
        sample_request_context
    ):
        """Test expert review not required for high validation score."""
        validation_result = ValidationResult(
            validation_id=uuid4(),
            status=ValidationStatus.COMPLETED,
            overall_score=0.9,  # Above threshold
            issues=[],
            expert_review_required=False,
            validation_timestamp=datetime.utcnow(),
            validation_duration_ms=100.0,
            regional_context={},
            crop_context={}
        )
        
        requires_review = await validation_service._requires_expert_review(
            validation_result, sample_recommendations, sample_request_context
        )
        
        assert requires_review is False

    @pytest.mark.asyncio
    async def test_track_farmer_satisfaction(
        self,
        validation_service,
        mock_db_session
    ):
        """Test farmer satisfaction tracking."""
        recommendation_id = uuid4()
        farmer_id = uuid4()
        satisfaction_score = 0.85
        feedback = "Great recommendations!"
        
        # Mock database manager
        validation_service.db_manager.store_farmer_feedback = AsyncMock()
        
        await validation_service.track_farmer_satisfaction(
            recommendation_id=recommendation_id,
            farmer_id=farmer_id,
            satisfaction_score=satisfaction_score,
            feedback=feedback
        )
        
        validation_service.db_manager.store_farmer_feedback.assert_called_once_with(
            recommendation_id=recommendation_id,
            farmer_id=farmer_id,
            satisfaction_score=satisfaction_score,
            feedback=feedback
        )


class TestExpertReviewService:
    """Test suite for ExpertReviewService."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.fixture
    def expert_service(self, mock_db_session):
        """Create expert review service instance."""
        return ExpertReviewService(mock_db_session)

    @pytest.fixture
    def sample_reviewer(self):
        """Sample expert reviewer for testing."""
        return ExpertReviewer(
            name="Dr. John Smith",
            credentials="Ph.D. in Agronomy",
            specialization=["corn", "soybeans", "soil_health"],
            region="Midwest",
            institution="Iowa State University",
            contact_email="john.smith@iastate.edu"
        )

    @pytest.mark.asyncio
    async def test_create_expert_reviewer(
        self,
        expert_service,
        sample_reviewer,
        mock_db_session
    ):
        """Test creating expert reviewer."""
        expert_service.db_manager.store_expert_reviewer = AsyncMock()
        
        reviewer = await expert_service.create_expert_reviewer(
            name=sample_reviewer.name,
            credentials=sample_reviewer.credentials,
            specialization=sample_reviewer.specialization,
            region=sample_reviewer.region,
            institution=sample_reviewer.institution,
            contact_email=sample_reviewer.contact_email
        )
        
        assert isinstance(reviewer, ExpertReviewer)
        assert reviewer.name == sample_reviewer.name
        assert reviewer.credentials == sample_reviewer.credentials
        assert reviewer.specialization == sample_reviewer.specialization
        assert reviewer.region == sample_reviewer.region
        assert reviewer.institution == sample_reviewer.institution
        assert reviewer.contact_email == sample_reviewer.contact_email
        assert reviewer.is_active is True
        assert reviewer.review_count == 0

    @pytest.mark.asyncio
    async def test_get_expert_reviewers(
        self,
        expert_service,
        mock_db_session
    ):
        """Test getting expert reviewers."""
        expert_service.db_manager.get_expert_reviewers = AsyncMock(return_value=[])
        
        reviewers = await expert_service.get_expert_reviewers(
            region="Midwest",
            crop_type="corn",
            specialization=["corn"],
            active_only=True
        )
        
        assert isinstance(reviewers, list)
        expert_service.db_manager.get_expert_reviewers.assert_called_once()

    @pytest.mark.asyncio
    async def test_assign_expert_review(
        self,
        expert_service,
        mock_db_session
    ):
        """Test assigning expert review."""
        validation_id = uuid4()
        region = "Midwest"
        crop_type = "corn"
        
        # Mock reviewer selection
        expert_service._find_suitable_reviewers = AsyncMock(return_value=[
            ExpertReviewer(
                reviewer_id=uuid4(),
                name="Test Reviewer",
                credentials="Ph.D.",
                specialization=["corn"],
                region="Midwest",
                institution="Test University",
                contact_email="test@university.edu"
            )
        ])
        expert_service._select_best_reviewer = AsyncMock(return_value=ExpertReviewer(
            reviewer_id=uuid4(),
            name="Test Reviewer",
            credentials="Ph.D.",
            specialization=["corn"],
            region="Midwest",
            institution="Test University",
            contact_email="test@university.edu"
        ))
        expert_service.db_manager.store_review_assignment = AsyncMock()
        expert_service._update_reviewer_workload = AsyncMock()
        
        assignment = await expert_service.assign_expert_review(
            validation_id=validation_id,
            region=region,
            crop_type=crop_type,
            priority=ReviewPriority.NORMAL
        )
        
        assert isinstance(assignment, ReviewAssignment)
        assert assignment.validation_id == validation_id
        assert assignment.priority == ReviewPriority.NORMAL
        assert assignment.status == ReviewAssignmentStatus.PENDING

    @pytest.mark.asyncio
    async def test_submit_expert_review(
        self,
        expert_service,
        mock_db_session
    ):
        """Test submitting expert review."""
        assignment_id = uuid4()
        reviewer_id = uuid4()
        
        # Mock assignment retrieval
        assignment = ReviewAssignment(
            assignment_id=assignment_id,
            validation_id=uuid4(),
            reviewer_id=reviewer_id,
            priority=ReviewPriority.NORMAL,
            status=ReviewAssignmentStatus.IN_PROGRESS,
            assigned_at=datetime.utcnow(),
            due_date=datetime.utcnow() + timedelta(days=7),
            created_by=uuid4()
        )
        
        expert_service.db_manager.get_review_assignment = AsyncMock(return_value=assignment)
        expert_service.db_manager.store_expert_review = AsyncMock()
        expert_service.db_manager.update_review_assignment = AsyncMock()
        expert_service._update_reviewer_statistics = AsyncMock()
        
        review_data = {
            "overall_score": 0.85,
            "agricultural_soundness": 0.9,
            "regional_applicability": 0.8,
            "economic_feasibility": 0.7,
            "farmer_practicality": 0.85,
            "comments": "Good recommendations overall",
            "recommendations": ["Consider earlier planting"],
            "concerns": ["Yield variability"],
            "approval_conditions": [],
            "overall_approval": True
        }
        
        review = await expert_service.submit_expert_review(
            assignment_id=assignment_id,
            reviewer_id=reviewer_id,
            review_data=review_data
        )
        
        assert isinstance(review, ExpertReview)
        assert review.validation_id == assignment.validation_id
        assert review.reviewer_id == reviewer_id
        assert review.review_score == 0.85
        assert review.agricultural_soundness == 0.9
        assert review.comments == "Good recommendations overall"

    @pytest.mark.asyncio
    async def test_get_reviewer_performance(
        self,
        expert_service,
        mock_db_session
    ):
        """Test getting reviewer performance metrics."""
        reviewer_id = uuid4()
        
        expert_service.db_manager.get_reviewer_reviews = AsyncMock(return_value=[])
        
        performance = await expert_service.get_reviewer_performance(
            reviewer_id=reviewer_id,
            start_date=datetime.utcnow() - timedelta(days=90),
            end_date=datetime.utcnow()
        )
        
        assert isinstance(performance, dict)
        assert "review_count" in performance
        assert "average_score" in performance
        assert "completion_rate" in performance
        assert "on_time_rate" in performance
        assert "quality_score" in performance


class TestValidationMetricsService:
    """Test suite for ValidationMetricsService."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.fixture
    def metrics_service(self, mock_db_session):
        """Create validation metrics service instance."""
        return ValidationMetricsService(mock_db_session)

    @pytest.mark.asyncio
    async def test_generate_metrics_report(
        self,
        metrics_service,
        mock_db_session
    ):
        """Test generating validation metrics report."""
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
        
        # Mock database operations
        metrics_service.db_manager.get_validation_results = AsyncMock(return_value=[])
        metrics_service.db_manager.get_expert_reviews = AsyncMock(return_value=[])
        metrics_service.db_manager.get_farmer_feedback = AsyncMock(return_value=[])
        metrics_service.db_manager.store_metrics_report = AsyncMock()
        
        report = await metrics_service.generate_metrics_report(
            period_start=start_date,
            period_end=end_date,
            period_type=MetricsPeriod.MONTHLY
        )
        
        assert isinstance(report, ValidationMetricsReport)
        assert report.period_start == start_date
        assert report.period_end == end_date
        assert report.period_type == MetricsPeriod.MONTHLY
        assert report.total_validations >= 0
        assert report.validation_success_rate >= 0.0
        assert report.average_validation_score >= 0.0

    @pytest.mark.asyncio
    async def test_get_real_time_metrics(
        self,
        metrics_service,
        mock_db_session
    ):
        """Test getting real-time metrics."""
        metrics_service.db_manager.get_validation_results = AsyncMock(return_value=[])
        metrics_service.db_manager.get_expert_reviews = AsyncMock(return_value=[])
        metrics_service.db_manager.get_farmer_feedback = AsyncMock(return_value=[])
        
        metrics = await metrics_service.get_real_time_metrics()
        
        assert isinstance(metrics, dict)
        assert "timestamp" in metrics
        assert "validations_last_24h" in metrics
        assert "expert_reviews_last_24h" in metrics
        assert "farmer_feedback_last_24h" in metrics
        assert "system_status" in metrics

    @pytest.mark.asyncio
    async def test_get_performance_alerts(
        self,
        metrics_service,
        mock_db_session
    ):
        """Test getting performance alerts."""
        # Mock report generation
        metrics_service.generate_metrics_report = AsyncMock(return_value=ValidationMetricsReport(
            period_start=datetime.utcnow() - timedelta(days=7),
            period_end=datetime.utcnow(),
            period_type=MetricsPeriod.WEEKLY,
            validation_success_rate=0.90,  # Below threshold
            expert_review_completion_rate=0.85,  # Below threshold
            average_farmer_satisfaction=0.80  # Below threshold
        ))
        
        alerts = await metrics_service.get_performance_alerts()
        
        assert isinstance(alerts, list)
        # Should have alerts for metrics below thresholds
        assert len(alerts) > 0


class TestAgriculturalValidationIntegration:
    """Integration tests for agricultural validation system."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.fixture
    def validation_service(self, mock_db_session):
        """Create validation service instance."""
        return AgriculturalValidationService(mock_db_session)

    @pytest.fixture
    def expert_service(self, mock_db_session):
        """Create expert review service instance."""
        return ExpertReviewService(mock_db_session)

    @pytest.fixture
    def metrics_service(self, mock_db_session):
        """Create metrics service instance."""
        return ValidationMetricsService(mock_db_session)

    @pytest.mark.asyncio
    async def test_end_to_end_validation_workflow(
        self,
        validation_service,
        expert_service,
        metrics_service
    ):
        """Test complete validation workflow from recommendation to metrics."""
        # Sample data
        recommendations = [
            VarietyRecommendation(
                variety_id=uuid4(),
                variety_name="Test Variety",
                overall_score=0.8,
                suitability_factors={"yield": 0.9},
                individual_scores={"yield": 0.9},
                weighted_contributions={"yield": 0.4},
                score_details={"yield": "High yield"},
                yield_expectation="High",
                risk_assessment={"overall_risk": "low"},
                management_difficulty="medium",
                performance_prediction={"regional_performance": {"confidence": 0.8}},
                adaptation_strategies=[],
                recommended_practices=[],
                economic_analysis={"roi": 0.15}
            )
        ]
        
        request_context = VarietyRecommendationRequest(
            crop_id=uuid4(),
            crop_name="corn",
            location_data={"region": "Midwest"},
            soil_conditions={"ph": 6.5},
            farming_objectives=["high_yield"],
            production_system="conventional",
            available_equipment=["planter"],
            max_recommendations=1
        )
        
        regional_context = {"region": "Midwest", "climate_zone": "5a"}
        crop_context = {"crop_type": "corn", "soil_ph": 6.5}
        
        # Mock database operations
        validation_service._store_validation_result = AsyncMock()
        expert_service.db_manager.store_review_assignment = AsyncMock()
        expert_service.db_manager.store_expert_reviewer = AsyncMock()
        metrics_service.db_manager.store_metrics_report = AsyncMock()
        
        # Step 1: Validate recommendations
        validation_result = await validation_service.validate_recommendations(
            recommendations=recommendations,
            request_context=request_context,
            regional_context=regional_context,
            crop_context=crop_context
        )
        
        assert validation_result.status == ValidationStatus.COMPLETED
        
        # Step 2: Assign expert review if required
        if validation_result.expert_review_required:
            expert_reviewer = await expert_service.create_expert_reviewer(
                name="Test Expert",
                credentials="Ph.D.",
                specialization=["corn"],
                region="Midwest",
                institution="Test University",
                contact_email="test@university.edu"
            )
            
            assignment = await expert_service.assign_expert_review(
                validation_id=validation_result.validation_id,
                region="Midwest",
                crop_type="corn"
            )
            
            assert assignment.validation_id == validation_result.validation_id
        
        # Step 3: Generate metrics report
        report = await metrics_service.generate_metrics_report(
            period_start=datetime.utcnow() - timedelta(days=1),
            period_end=datetime.utcnow(),
            period_type=MetricsPeriod.DAILY
        )
        
        assert isinstance(report, ValidationMetricsReport)
        assert report.total_validations >= 0

    @pytest.mark.asyncio
    async def test_validation_with_issues(
        self,
        validation_service
    ):
        """Test validation with agricultural issues."""
        # Create recommendations with potential issues
        recommendations = [
            VarietyRecommendation(
                variety_id=uuid4(),
                variety_name="Problematic Variety",
                overall_score=0.6,  # Lower score
                suitability_factors={"yield": 0.5},
                individual_scores={"yield": 0.5},
                weighted_contributions={"yield": 0.4},
                score_details={"yield": "Low yield potential"},
                yield_expectation="Low",
                risk_assessment={"overall_risk": "high"},
                management_difficulty="high",
                performance_prediction={"regional_performance": {"confidence": 0.4}},
                adaptation_strategies=[],
                recommended_practices=[],
                economic_analysis={"roi": 0.05}  # Low ROI
            )
        ]
        
        request_context = VarietyRecommendationRequest(
            crop_id=uuid4(),
            crop_name="corn",
            location_data={"region": "Midwest"},
            soil_conditions={"ph": 5.0},  # Low pH
            farming_objectives=["high_yield"],
            production_system="conventional",
            available_equipment=["planter"],
            max_recommendations=1
        )
        
        regional_context = {"region": "Midwest", "climate_zone": "5a", "average_yield": 170}
        crop_context = {"crop_type": "corn", "soil_ph": 5.0}
        
        validation_service._store_validation_result = AsyncMock()
        
        result = await validation_service.validate_recommendations(
            recommendations=recommendations,
            request_context=request_context,
            regional_context=regional_context,
            crop_context=crop_context
        )
        
        assert result.status == ValidationStatus.COMPLETED
        assert len(result.issues) > 0  # Should have validation issues
        assert result.expert_review_required is True  # Should require expert review


# Performance tests
class TestValidationPerformance:
    """Performance tests for validation system."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.fixture
    def validation_service(self, mock_db_session):
        """Create validation service instance."""
        return AgriculturalValidationService(mock_db_session)

    @pytest.mark.asyncio
    async def test_validation_performance_large_dataset(self, validation_service):
        """Test validation performance with large dataset."""
        # Create large number of recommendations
        recommendations = []
        for i in range(100):
            recommendations.append(VarietyRecommendation(
                variety_id=uuid4(),
                variety_name=f"Variety {i}",
                overall_score=0.8,
                suitability_factors={"yield": 0.9},
                individual_scores={"yield": 0.9},
                weighted_contributions={"yield": 0.4},
                score_details={"yield": "High yield"},
                yield_expectation="High",
                risk_assessment={"overall_risk": "low"},
                management_difficulty="medium",
                performance_prediction={"regional_performance": {"confidence": 0.8}},
                adaptation_strategies=[],
                recommended_practices=[],
                economic_analysis={"roi": 0.15}
            ))
        
        request_context = VarietyRecommendationRequest(
            crop_id=uuid4(),
            crop_name="corn",
            location_data={"region": "Midwest"},
            soil_conditions={"ph": 6.5},
            farming_objectives=["high_yield"],
            production_system="conventional",
            available_equipment=["planter"],
            max_recommendations=100
        )
        
        regional_context = {"region": "Midwest", "climate_zone": "5a"}
        crop_context = {"crop_type": "corn", "soil_ph": 6.5}
        
        validation_service._store_validation_result = AsyncMock()
        
        import time
        start_time = time.time()
        
        result = await validation_service.validate_recommendations(
            recommendations=recommendations,
            request_context=request_context,
            regional_context=regional_context,
            crop_context=crop_context
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert result.status == ValidationStatus.COMPLETED
        assert duration < 5.0  # Should complete within 5 seconds
        assert result.validation_duration_ms < 5000  # Should complete within 5 seconds