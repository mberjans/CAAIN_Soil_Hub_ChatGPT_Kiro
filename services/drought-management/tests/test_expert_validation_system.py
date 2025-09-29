"""
Comprehensive Test Suite for Expert Validation System

This test suite provides comprehensive coverage for the agricultural expert validation
and field testing system for drought management recommendations.

TICKET-014_drought-management-13.2: Implement agricultural expert validation and field testing
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from decimal import Decimal

# Import test fixtures
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from conftest import (
    mock_farm_location_id, mock_field_id, mock_user_id,
    sample_weather_data, sample_soil_data, sample_crop_data,
    sample_drought_assessment_request, sample_conservation_practices,
    mock_external_services, agricultural_validation_data
)

from src.services.expert_validation_service import (
    ExpertValidationService, ValidationStatus, ExpertType, ValidationCriteria
)
from src.models.expert_validation_models import (
    ExpertProfile, ValidationRequest, ExpertReview, FieldTestResult,
    ValidationMetrics, ExpertReviewSubmission, FieldTestRequest
)


class TestExpertValidationService:
    """Comprehensive tests for expert validation service."""
    
    @pytest.fixture
    async def expert_validation_service(self):
        """Create expert validation service instance."""
        service = ExpertValidationService()
        await service.initialize()
        return service
    
    @pytest.fixture
    def sample_expert_profile(self):
        """Create sample expert profile."""
        return ExpertProfile(
            expert_id=uuid4(),
            name="Dr. Test Expert",
            credentials="PhD in Soil Science, Certified Crop Advisor",
            expertise_areas=[ExpertType.DROUGHT_SPECIALIST, ExpertType.SOIL_SCIENTIST],
            regions=["IA", "NE", "KS"],
            years_experience=15,
            certifications=["CCA", "CPSS"],
            contact_info={"email": "test@university.edu", "phone": "555-0101"},
            approval_rate=0.95,
            average_review_time_hours=4.5
        )
    
    @pytest.fixture
    def sample_validation_request(self):
        """Create sample validation request."""
        return ValidationRequest(
            validation_id=uuid4(),
            recommendation_id=uuid4(),
            farm_location={"state": "IA", "county": "Story", "coordinates": {"lat": 41.8781, "lng": -87.6298}},
            field_conditions={"soil_type": "clay_loam", "crop_type": "corn", "acres": 40},
            drought_assessment={"risk_level": "moderate", "soil_moisture_deficit": 0.15},
            conservation_recommendations=[
                {"practice": "no_till", "estimated_cost": 500, "region_specific": True},
                {"practice": "cover_crops", "estimated_cost": 200, "environmental_impact_high": True}
            ],
            water_savings_estimates=[{"practice": "no_till", "water_savings_percent": 20}],
            validation_criteria=[ValidationCriteria.AGRICULTURAL_SOUNDNESS, ValidationCriteria.SAFETY],
            priority_level="normal",
            requested_expert_types=[ExpertType.DROUGHT_SPECIALIST],
            deadline=datetime.utcnow() + timedelta(hours=72)
        )
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, expert_validation_service):
        """Test expert validation service initialization."""
        assert expert_validation_service is not None
        assert expert_validation_service.db is not None
        assert len(expert_validation_service.expert_panel) > 0
        assert expert_validation_service.metrics.expert_panel_size > 0
    
    @pytest.mark.asyncio
    async def test_submit_validation_request(self, expert_validation_service, sample_validation_request):
        """Test submitting validation request."""
        with patch.object(expert_validation_service.db, 'save_validation_request') as mock_save:
            with patch.object(expert_validation_service, '_assign_experts') as mock_assign:
                validation_request = await expert_validation_service.submit_for_validation(
                    recommendation_id=sample_validation_request.recommendation_id,
                    farm_location=sample_validation_request.farm_location,
                    field_conditions=sample_validation_request.field_conditions,
                    drought_assessment=sample_validation_request.drought_assessment,
                    conservation_recommendations=sample_validation_request.conservation_recommendations,
                    water_savings_estimates=sample_validation_request.water_savings_estimates,
                    priority_level="normal"
                )
                
                assert validation_request.validation_id is not None
                assert validation_request.priority_level == "normal"
                assert len(validation_request.validation_criteria) > 0
                mock_save.assert_called_once()
                mock_assign.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_expert_assignment(self, expert_validation_service, sample_validation_request):
        """Test expert assignment to validation request."""
        # Mock expert panel with available experts
        expert_validation_service.expert_panel = {
            uuid4(): ExpertProfile(
                expert_id=uuid4(),
                name="Test Expert",
                credentials="PhD",
                expertise_areas=[ExpertType.DROUGHT_SPECIALIST],
                regions=["IA"],
                years_experience=10,
                certifications=[],
                contact_info={"email": "test@test.com"},
                availability_status="available"
            )
        }
        
        with patch.object(expert_validation_service.db, 'assign_experts_to_validation') as mock_assign:
            await expert_validation_service._assign_experts(sample_validation_request)
            mock_assign.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_expert_review_submission(self, expert_validation_service):
        """Test expert review submission."""
        validation_id = uuid4()
        expert_id = uuid4()
        
        # Mock expert in panel
        expert_validation_service.expert_panel[expert_id] = ExpertProfile(
            expert_id=expert_id,
            name="Test Expert",
            credentials="PhD",
            expertise_areas=[ExpertType.DROUGHT_SPECIALIST],
            regions=["IA"],
            years_experience=10,
            certifications=[],
            contact_info={"email": "test@test.com"}
        )
        
        with patch.object(expert_validation_service.db, 'save_expert_review') as mock_save:
            with patch.object(expert_validation_service, '_update_validation_metrics') as mock_update:
                review = await expert_validation_service.submit_expert_review(
                    validation_id=validation_id,
                    expert_id=expert_id,
                    criteria_scores={ValidationCriteria.AGRICULTURAL_SOUNDNESS: 0.9},
                    overall_score=0.85,
                    comments="Recommendation is agriculturally sound and safe to implement.",
                    recommendations=["Consider timing adjustments"],
                    concerns=[],
                    approval_status=True,
                    review_time_hours=4.0
                )
                
                assert review.validation_id == validation_id
                assert review.expert_id == expert_id
                assert review.approval_status is True
                assert review.overall_score == 0.85
                mock_save.assert_called_once()
                mock_update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_field_test_start(self, expert_validation_service):
        """Test starting field test."""
        farm_id = uuid4()
        field_id = uuid4()
        
        with patch.object(expert_validation_service.db, 'save_field_test') as mock_save:
            field_test = await expert_validation_service.start_field_test(
                farm_id=farm_id,
                field_id=field_id,
                practice_implemented="no_till",
                baseline_conditions={"soil_moisture": 0.6, "soil_type": "clay_loam", "crop_type": "corn"},
                test_duration_days=90
            )
            
            assert field_test.farm_id == farm_id
            assert field_test.field_id == field_id
            assert field_test.practice_implemented == "no_till"
            assert field_test.test_duration_days == 90
            mock_save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_field_test_monitoring_update(self, expert_validation_service):
        """Test field test monitoring data update."""
        test_id = uuid4()
        
        # Add test to active tests
        expert_validation_service.field_tests[test_id] = FieldTestResult(
            test_id=test_id,
            farm_id=uuid4(),
            field_id=uuid4(),
            practice_implemented="no_till",
            implementation_date=datetime.utcnow(),
            baseline_conditions={"soil_moisture": 0.6, "soil_type": "clay_loam", "crop_type": "corn"},
            test_duration_days=90
        )
        
        with patch.object(expert_validation_service.db, 'update_field_test_monitoring') as mock_update:
            await expert_validation_service.update_field_test_monitoring(
                test_id=test_id,
                monitoring_data={"soil_moisture": 0.55, "crop_health": 0.8},
                expert_observations=["Soil moisture decreasing as expected"]
            )
            
            mock_update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_field_test_completion(self, expert_validation_service):
        """Test field test completion."""
        test_id = uuid4()
        
        # Add test to active tests
        expert_validation_service.field_tests[test_id] = FieldTestResult(
            test_id=test_id,
            farm_id=uuid4(),
            field_id=uuid4(),
            practice_implemented="no_till",
            implementation_date=datetime.utcnow(),
            baseline_conditions={"soil_moisture": 0.6, "soil_type": "clay_loam", "crop_type": "corn"},
            test_duration_days=90
        )
        
        with patch.object(expert_validation_service.db, 'complete_field_test') as mock_complete:
            with patch.object(expert_validation_service, '_update_validation_metrics') as mock_update:
                await expert_validation_service.complete_field_test(
                    test_id=test_id,
                    outcome_metrics={"water_savings_percent": 18, "yield_impact_percent": 2, "cost_benefit_ratio": 1.5},
                    farmer_feedback={"satisfaction_rating": 4, "implementation_difficulty": "easy", "recommendation": "continue"},
                    effectiveness_score=0.85,
                    farmer_satisfaction_score=0.90
                )
                
                mock_complete.assert_called_once()
                mock_update.assert_called_once()
                assert test_id not in expert_validation_service.field_tests
    
    @pytest.mark.asyncio
    async def test_validation_status_query(self, expert_validation_service):
        """Test validation status query."""
        validation_id = uuid4()
        
        mock_status_data = {
            "status": "in_review",
            "progress_percentage": 50.0,
            "expert_reviews": 1,
            "total_experts_assigned": 2,
            "deadline": datetime.utcnow() + timedelta(hours=24),
            "overall_approval": None
        }
        
        with patch.object(expert_validation_service.db, 'get_validation_request') as mock_get_request:
            with patch.object(expert_validation_service.db, 'get_validation_reviews') as mock_get_reviews:
                mock_get_request.return_value = {"assigned_experts": [uuid4(), uuid4()]}
                mock_get_reviews.return_value = [{"approval_status": True}]
                
                status = await expert_validation_service.get_validation_status(validation_id)
                
                assert status["validation_id"] == validation_id
                mock_get_request.assert_called_once()
                mock_get_reviews.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_validation_metrics_calculation(self, expert_validation_service):
        """Test validation metrics calculation."""
        with patch.object(expert_validation_service.db, 'get_recent_reviews') as mock_reviews:
            with patch.object(expert_validation_service.db, 'get_completed_field_tests') as mock_tests:
                mock_reviews.return_value = [
                    {"approval_status": True},
                    {"approval_status": True},
                    {"approval_status": False}
                ]
                mock_tests.return_value = [
                    {"farmer_satisfaction_score": 0.9},
                    {"farmer_satisfaction_score": 0.8},
                    {"farmer_satisfaction_score": 0.85}
                ]
                
                await expert_validation_service._update_validation_metrics()
                
                # Check that metrics were calculated
                assert expert_validation_service.metrics.expert_approval_rate > 0
                assert expert_validation_service.metrics.farmer_satisfaction > 0
    
    @pytest.mark.asyncio
    async def test_expert_panel_status(self, expert_validation_service):
        """Test expert panel status query."""
        # Add sample experts to panel
        expert_validation_service.expert_panel = {
            uuid4(): ExpertProfile(
                expert_id=uuid4(),
                name="Expert 1",
                credentials="PhD",
                expertise_areas=[ExpertType.DROUGHT_SPECIALIST],
                regions=["IA"],
                years_experience=10,
                certifications=[],
                contact_info={"email": "test1@test.com"},
                availability_status="available",
                approval_rate=0.9
            ),
            uuid4(): ExpertProfile(
                expert_id=uuid4(),
                name="Expert 2",
                credentials="MS",
                expertise_areas=[ExpertType.SOIL_SCIENTIST],
                regions=["NE"],
                years_experience=8,
                certifications=[],
                contact_info={"email": "test2@test.com"},
                availability_status="assigned",
                approval_rate=0.85
            )
        }
        
        status = await expert_validation_service.get_expert_panel_status()
        
        assert status["total_experts"] == 2
        assert status["available_experts"] == 1
        assert status["assigned_experts"] == 1
        assert status["average_approval_rate"] == 0.875
        assert status["average_experience_years"] == 9.0
    
    @pytest.mark.asyncio
    async def test_validation_report_generation(self, expert_validation_service):
        """Test validation report generation."""
        validation_id = uuid4()
        
        mock_report_data = {
            "validation_summary": {
                "validation_id": validation_id,
                "recommendation_id": uuid4(),
                "priority_level": "normal",
                "created_at": datetime.utcnow(),
                "deadline": datetime.utcnow() + timedelta(hours=24),
                "status": "completed"
            },
            "expert_reviews": [
                {
                    "expert_name": "Dr. Test Expert",
                    "expert_type": "drought_specialist",
                    "overall_score": 0.85,
                    "approval_status": True,
                    "comments": "Good recommendation",
                    "recommendations": ["Consider timing"],
                    "concerns": [],
                    "review_time_hours": 4.0,
                    "submitted_at": datetime.utcnow()
                }
            ],
            "overall_assessment": {
                "total_reviews": 1,
                "approval_rate": 1.0,
                "average_score": 0.85,
                "consensus": "approved"
            },
            "recommendations": [{"practice": "no_till"}],
            "water_savings_estimates": [{"practice": "no_till", "water_savings_percent": 20}]
        }
        
        with patch.object(expert_validation_service.db, 'get_validation_request') as mock_get_request:
            with patch.object(expert_validation_service.db, 'get_validation_reviews') as mock_get_reviews:
                mock_get_request.return_value = mock_report_data["validation_summary"]
                mock_get_reviews.return_value = mock_report_data["expert_reviews"]
                
                report = await expert_validation_service.generate_validation_report(validation_id)
                
                assert report["validation_summary"]["validation_id"] == validation_id
                assert len(report["expert_reviews"]) == 1
                assert report["overall_assessment"]["consensus"] == "approved"


class TestValidationCriteria:
    """Test validation criteria determination."""
    
    def test_determine_validation_criteria_basic(self):
        """Test basic validation criteria determination."""
        service = ExpertValidationService()
        
        conservation_recommendations = [
            {"region_specific": False, "estimated_cost": 100, "environmental_impact_high": False, "implementation_complexity": "low", "effectiveness_uncertainty": 0.1}
        ]
        water_savings_estimates = [{"practice": "test", "water_savings_percent": 10}]
        
        criteria = service._determine_validation_criteria(conservation_recommendations, water_savings_estimates)
        
        assert ValidationCriteria.AGRICULTURAL_SOUNDNESS in criteria
        assert ValidationCriteria.SAFETY in criteria
        assert ValidationCriteria.REGIONAL_APPLICABILITY not in criteria
        assert ValidationCriteria.ECONOMIC_FEASIBILITY not in criteria
    
    def test_determine_validation_criteria_complex(self):
        """Test complex validation criteria determination."""
        service = ExpertValidationService()
        
        conservation_recommendations = [
            {
                "region_specific": True,
                "estimated_cost": 2000,
                "environmental_impact_high": True,
                "implementation_complexity": "high",
                "effectiveness_uncertainty": 0.4
            }
        ]
        water_savings_estimates = [{"practice": "test", "water_savings_percent": 25}]
        
        criteria = service._determine_validation_criteria(conservation_recommendations, water_savings_estimates)
        
        assert ValidationCriteria.AGRICULTURAL_SOUNDNESS in criteria
        assert ValidationCriteria.SAFETY in criteria
        assert ValidationCriteria.REGIONAL_APPLICABILITY in criteria
        assert ValidationCriteria.ECONOMIC_FEASIBILITY in criteria
        assert ValidationCriteria.ENVIRONMENTAL_IMPACT in criteria
        assert ValidationCriteria.PRACTICALITY in criteria
        assert ValidationCriteria.EFFECTIVENESS in criteria
    
    def test_determine_required_experts(self):
        """Test required expert type determination."""
        service = ExpertValidationService()
        
        farm_location = {"state": "IA"}
        field_conditions = {"crop_type": "corn"}
        conservation_recommendations = [
            {"category": "conservation"},
            {"category": "irrigation"},
            {"category": "soil_management"}
        ]
        
        expert_types = service._determine_required_experts(farm_location, field_conditions, conservation_recommendations)
        
        assert ExpertType.DROUGHT_SPECIALIST in expert_types
        assert ExpertType.EXTENSION_AGENT in expert_types
        assert ExpertType.CONSERVATION_PROFESSIONAL in expert_types
        assert ExpertType.IRRIGATION_SPECIALIST in expert_types
        assert ExpertType.SOIL_SCIENTIST in expert_types
        assert ExpertType.CROP_SPECIALIST in expert_types
    
    def test_deadline_hours_calculation(self):
        """Test deadline hours calculation based on priority."""
        service = ExpertValidationService()
        
        assert service._get_deadline_hours("low") == 168  # 1 week
        assert service._get_deadline_hours("normal") == 72  # 3 days
        assert service._get_deadline_hours("high") == 24  # 1 day
        assert service._get_deadline_hours("critical") == 8  # 8 hours
        assert service._get_deadline_hours("unknown") == 72  # default


class TestFieldTestValidation:
    """Test field test validation and edge cases."""
    
    @pytest.mark.asyncio
    async def test_field_test_baseline_validation(self):
        """Test field test baseline conditions validation."""
        service = ExpertValidationService()
        
        # Valid baseline conditions
        valid_baseline = {
            "soil_moisture": 0.6,
            "soil_type": "clay_loam",
            "crop_type": "corn"
        }
        
        # This should not raise an exception
        field_test = await service.start_field_test(
            farm_id=uuid4(),
            field_id=uuid4(),
            practice_implemented="no_till",
            baseline_conditions=valid_baseline,
            test_duration_days=90
        )
        
        assert field_test.baseline_conditions == valid_baseline
    
    @pytest.mark.asyncio
    async def test_field_test_duration_validation(self):
        """Test field test duration validation."""
        service = ExpertValidationService()
        
        # Test minimum duration
        field_test = await service.start_field_test(
            farm_id=uuid4(),
            field_id=uuid4(),
            practice_implemented="no_till",
            baseline_conditions={"soil_moisture": 0.6, "soil_type": "clay_loam", "crop_type": "corn"},
            test_duration_days=1
        )
        
        assert field_test.test_duration_days == 1
        
        # Test maximum duration
        field_test = await service.start_field_test(
            farm_id=uuid4(),
            field_id=uuid4(),
            practice_implemented="no_till",
            baseline_conditions={"soil_moisture": 0.6, "soil_type": "clay_loam", "crop_type": "corn"},
            test_duration_days=365
        )
        
        assert field_test.test_duration_days == 365


class TestAgriculturalValidation:
    """Agricultural validation tests for expert validation system."""
    
    @pytest.mark.agricultural
    @pytest.mark.asyncio
    async def test_drought_management_expert_validation(self):
        """Test expert validation against known drought management scenarios."""
        service = ExpertValidationService()
        
        # Test scenario: 2012 Midwest drought
        drought_2012_data = {
            "location": {"lat": 40.0, "lng": -95.0},  # Central Iowa
            "precipitation_deficit": -8.5,  # inches below normal
            "temperature_anomaly": 3.2,    # degrees F above normal
            "soil_moisture_deficit": 0.15, # 15% below field capacity
            "duration_months": 6,
            "expected_yield_loss": 25.0,   # percent
            "expected_risk_level": "severe"
        }
        
        # Mock expert review for 2012 drought scenario
        expert_review = ExpertReview(
            review_id=uuid4(),
            validation_id=uuid4(),
            expert_id=uuid4(),
            expert_type=ExpertType.DROUGHT_SPECIALIST,
            review_status=ValidationStatus.APPROVED,
            criteria_scores={
                ValidationCriteria.AGRICULTURAL_SOUNDNESS: 0.95,
                ValidationCriteria.REGIONAL_APPLICABILITY: 0.90,
                ValidationCriteria.SAFETY: 0.98,
                ValidationCriteria.EFFECTIVENESS: 0.92
            },
            overall_score=0.94,
            comments="Recommendations are appropriate for severe drought conditions. No-till and cover crops are essential practices for moisture conservation.",
            recommendations=["Implement no-till immediately", "Plant drought-tolerant varieties", "Consider irrigation if available"],
            concerns=["Monitor soil moisture closely", "Watch for pest pressure"],
            approval_status=True,
            review_time_hours=3.5,
            submitted_at=datetime.utcnow()
        )
        
        # Validate expert review scores are appropriate for severe drought
        assert expert_review.criteria_scores[ValidationCriteria.AGRICULTURAL_SOUNDNESS] >= 0.9
        assert expert_review.criteria_scores[ValidationCriteria.SAFETY] >= 0.95
        assert expert_review.overall_score >= 0.9
        assert expert_review.approval_status is True
    
    @pytest.mark.agricultural
    @pytest.mark.asyncio
    async def test_conservation_practice_validation(self):
        """Test validation of conservation practices against agricultural research."""
        service = ExpertValidationService()
        
        # Test no-till practice validation
        no_till_review = ExpertReview(
            review_id=uuid4(),
            validation_id=uuid4(),
            expert_id=uuid4(),
            expert_type=ExpertType.CONSERVATION_PROFESSIONAL,
            review_status=ValidationStatus.APPROVED,
            criteria_scores={
                ValidationCriteria.AGRICULTURAL_SOUNDNESS: 0.98,
                ValidationCriteria.ENVIRONMENTAL_IMPACT: 0.95,
                ValidationCriteria.EFFECTIVENESS: 0.92,
                ValidationCriteria.PRACTICALITY: 0.88
            },
            overall_score=0.93,
            comments="No-till is well-established practice with proven water conservation benefits. Implementation requires proper equipment and timing.",
            recommendations=["Ensure proper residue management", "Consider starter fertilizer placement"],
            concerns=["May require equipment modifications", "Transition period needed"],
            approval_status=True,
            review_time_hours=2.5,
            submitted_at=datetime.utcnow()
        )
        
        # Validate no-till practice scores
        assert no_till_review.criteria_scores[ValidationCriteria.AGRICULTURAL_SOUNDNESS] >= 0.95
        assert no_till_review.criteria_scores[ValidationCriteria.ENVIRONMENTAL_IMPACT] >= 0.90
        assert no_till_review.overall_score >= 0.90
        assert no_till_review.approval_status is True
    
    @pytest.mark.agricultural
    @pytest.mark.asyncio
    async def test_field_test_effectiveness_validation(self):
        """Test field test effectiveness against known conservation practice outcomes."""
        service = ExpertValidationService()
        
        # Test field test results for cover crops
        field_test = FieldTestResult(
            test_id=uuid4(),
            farm_id=uuid4(),
            field_id=uuid4(),
            practice_implemented="cover_crops",
            implementation_date=datetime.utcnow() - timedelta(days=90),
            baseline_conditions={
                "soil_moisture": 0.65,
                "soil_type": "silt_loam",
                "crop_type": "corn",
                "organic_matter": 2.5
            },
            monitoring_data={
                "soil_moisture": 0.72,
                "organic_matter": 2.8,
                "water_infiltration_rate": 1.2
            },
            outcome_metrics={
                "water_savings_percent": 15.0,
                "yield_impact_percent": 3.0,
                "cost_benefit_ratio": 1.8,
                "soil_health_improvement": 0.12
            },
            farmer_feedback={
                "satisfaction_rating": 4,
                "implementation_difficulty": "moderate",
                "recommendation": "continue",
                "cost_concerns": "moderate"
            },
            expert_observations=[
                "Cover crop established well",
                "Soil moisture retention improved",
                "Weed suppression effective"
            ],
            effectiveness_score=0.85,
            farmer_satisfaction_score=0.80,
            test_duration_days=90,
            completed_at=datetime.utcnow()
        )
        
        # Validate field test results against expected outcomes
        assert field_test.outcome_metrics["water_savings_percent"] >= 12.0  # Expected 12-18%
        assert field_test.outcome_metrics["water_savings_percent"] <= 18.0
        assert field_test.effectiveness_score >= 0.80  # Good effectiveness
        assert field_test.farmer_satisfaction_score >= 0.75  # Satisfied farmer
        assert field_test.outcome_metrics["cost_benefit_ratio"] >= 1.5  # Positive ROI


class TestPerformanceRequirements:
    """Performance tests for expert validation system."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_validation_submission_performance(self):
        """Test validation submission performance requirements."""
        service = ExpertValidationService()
        
        start_time = datetime.utcnow()
        
        # Submit multiple validation requests
        for i in range(10):
            await service.submit_for_validation(
                recommendation_id=uuid4(),
                farm_location={"state": "IA", "county": "Story"},
                field_conditions={"soil_type": "clay_loam", "crop_type": "corn"},
                drought_assessment={"risk_level": "moderate"},
                conservation_recommendations=[{"practice": "no_till", "estimated_cost": 500}],
                water_savings_estimates=[{"practice": "no_till", "water_savings_percent": 20}],
                priority_level="normal"
            )
        
        elapsed_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Should complete 10 submissions in under 5 seconds
        assert elapsed_time < 5.0, f"Validation submission took {elapsed_time}s, exceeds 5s requirement"
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_expert_review_performance(self):
        """Test expert review submission performance."""
        service = ExpertValidationService()
        
        start_time = datetime.utcnow()
        
        # Submit multiple expert reviews
        for i in range(20):
            await service.submit_expert_review(
                validation_id=uuid4(),
                expert_id=uuid4(),
                criteria_scores={ValidationCriteria.AGRICULTURAL_SOUNDNESS: 0.9},
                overall_score=0.85,
                comments="Good recommendation for drought management.",
                recommendations=["Consider timing"],
                concerns=[],
                approval_status=True,
                review_time_hours=3.0
            )
        
        elapsed_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Should complete 20 reviews in under 3 seconds
        assert elapsed_time < 3.0, f"Expert review submission took {elapsed_time}s, exceeds 3s requirement"
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_field_test_monitoring_performance(self):
        """Test field test monitoring update performance."""
        service = ExpertValidationService()
        
        # Create field test
        field_test = await service.start_field_test(
            farm_id=uuid4(),
            field_id=uuid4(),
            practice_implemented="no_till",
            baseline_conditions={"soil_moisture": 0.6, "soil_type": "clay_loam", "crop_type": "corn"},
            test_duration_days=90
        )
        
        start_time = datetime.utcnow()
        
        # Update monitoring data multiple times
        for i in range(50):
            await service.update_field_test_monitoring(
                test_id=field_test.test_id,
                monitoring_data={"soil_moisture": 0.55 + i * 0.001},
                expert_observations=[f"Monitoring update {i}"]
            )
        
        elapsed_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Should complete 50 updates in under 2 seconds
        assert elapsed_time < 2.0, f"Field test monitoring update took {elapsed_time}s, exceeds 2s requirement"


class TestIntegrationWithDroughtServices:
    """Integration tests with existing drought management services."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_integration_with_drought_assessment(self):
        """Test integration with drought assessment service."""
        from src.services.drought_assessment_service import DroughtAssessmentService
        
        drought_service = DroughtAssessmentService()
        expert_service = ExpertValidationService()
        
        # Create drought assessment
        assessment_request = {
            "farm_location": {"lat": 40.0, "lng": -95.0},
            "field_conditions": {"soil_type": "clay_loam", "crop_type": "corn"},
            "weather_data": {"precipitation_deficit": -5.0, "temperature_anomaly": 2.0}
        }
        
        # Mock drought assessment response
        drought_assessment = {
            "risk_level": "moderate",
            "soil_moisture_deficit": 0.12,
            "confidence": 0.85
        }
        
        # Submit for expert validation
        validation_request = await expert_service.submit_for_validation(
            recommendation_id=uuid4(),
            farm_location=assessment_request["farm_location"],
            field_conditions=assessment_request["field_conditions"],
            drought_assessment=drought_assessment,
            conservation_recommendations=[{"practice": "no_till", "estimated_cost": 500}],
            water_savings_estimates=[{"practice": "no_till", "water_savings_percent": 20}],
            priority_level="normal"
        )
        
        assert validation_request.validation_id is not None
        assert validation_request.drought_assessment["risk_level"] == "moderate"
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_integration_with_conservation_service(self):
        """Test integration with moisture conservation service."""
        from src.services.moisture_conservation_service import MoistureConservationService
        
        conservation_service = MoistureConservationService()
        expert_service = ExpertValidationService()
        
        # Mock conservation recommendations
        conservation_recommendations = [
            {
                "practice": "no_till",
                "estimated_cost": 500,
                "water_savings_percent": 20,
                "implementation_complexity": "medium",
                "region_specific": True
            },
            {
                "practice": "cover_crops",
                "estimated_cost": 200,
                "water_savings_percent": 15,
                "implementation_complexity": "low",
                "environmental_impact_high": True
            }
        ]
        
        # Submit for expert validation
        validation_request = await expert_service.submit_for_validation(
            recommendation_id=uuid4(),
            farm_location={"state": "IA", "county": "Story"},
            field_conditions={"soil_type": "clay_loam", "crop_type": "corn"},
            drought_assessment={"risk_level": "moderate"},
            conservation_recommendations=conservation_recommendations,
            water_savings_estimates=[{"practice": "no_till", "water_savings_percent": 20}],
            priority_level="normal"
        )
        
        assert validation_request.validation_id is not None
        assert len(validation_request.conservation_recommendations) == 2
        assert validation_request.validation_criteria  # Should have multiple criteria for complex recommendations