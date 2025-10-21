"""
Comprehensive Testing Suite for Expert Validation Service
TICKET-023_fertilizer-application-method-11.2

This module provides comprehensive testing coverage for the agricultural expert
validation and field testing service, including unit tests, integration tests,
and agricultural validation tests.
"""

import pytest
import asyncio
import time
import json
import os
import sys
from typing import Dict, List, Any, Optional
from unittest.mock import AsyncMock, patch, MagicMock, Mock
from datetime import datetime, timedelta
from uuid import uuid4

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.services.expert_validation_service import (
    ExpertValidationService, ExpertType, ValidationStatus, FieldTestStatus,
    ExpertProfile, ValidationRequest, ExpertReview, FieldTestPlan, FieldTestResult,
    ValidationMetrics
)
from src.models.application_models import (
    ApplicationRequest, ApplicationResponse, ApplicationMethod,
    FieldConditions, CropRequirements, FertilizerSpecification,
    ApplicationMethodType, FertilizerForm, EquipmentType, EquipmentSpecification
)


class TestDataFactory:
    """Factory for creating test data."""
    
    @staticmethod
    def create_sample_application_request() -> ApplicationRequest:
        """Create a sample application request for testing."""
        return ApplicationRequest(
            field_conditions=FieldConditions(
                soil_type="clay_loam",
                ph_level=6.5,
                organic_matter_percent=3.2,
                drainage_class="well_drained",
                slope_percent=2.0,
                field_size_acres=40.0,
                previous_crop="corn",
                tillage_practice="conventional_till"
            ),
            crop_requirements=CropRequirements(
                crop_type="corn",
                growth_stage="V6",
                target_yield_bu_per_acre=180.0,
                planting_date=datetime.now() - timedelta(days=30),
                harvest_date=datetime.now() + timedelta(days=120)
            ),
            fertilizer_specification=FertilizerSpecification(
                fertilizer_type="urea",
                npk_ratio="46-0-0",
                form=FertilizerForm.GRANULAR,
                solubility=100.0,
                release_rate="immediate",
                cost_per_unit=0.50,
                unit="lb"
            ),
            equipment_specification=EquipmentSpecification(
                equipment_type=EquipmentType.SPREADER,
                capacity=10.0,
                capacity_unit="tons",
                application_width=40.0,
                application_rate_range={"min": 50.0, "max": 200.0},
                fuel_efficiency=0.8,
                maintenance_cost_per_hour=15.0
            ),
            application_method=ApplicationMethodType.BROADCAST,
            environmental_conditions={
                "temperature_f": 65.0,
                "humidity_percent": 70.0,
                "wind_speed_mph": 5.0,
                "precipitation_probability": 0.1
            },
            cost_constraints={
                "max_cost_per_acre": 50.0,
                "labor_cost_per_hour": 25.0,
                "fuel_cost_per_gallon": 3.50
            }
        )
    
    @staticmethod
    def create_sample_application_response() -> ApplicationResponse:
        """Create a sample application response for testing."""
        # Create primary application method
        primary_method = ApplicationMethod(
            method_id=str(uuid4()),
            method_type=ApplicationMethodType.BROADCAST,
            recommended_equipment=EquipmentSpecification(
                equipment_type=EquipmentType.SPREADER,
                capacity=10.0,
                capacity_unit="tons",
                application_width=40.0,
                application_rate_range={"min": 50.0, "max": 200.0},
                fuel_efficiency=0.8,
                maintenance_cost_per_hour=15.0
            ),
            application_rate=150.0,
            rate_unit="lbs/acre",
            application_timing="Apply during early morning hours",
            efficiency_score=0.78,
            cost_per_acre=45.0,
            labor_requirements="Medium",
            environmental_impact="Low",
            pros=["Uniform coverage", "Fast application", "Suitable for large fields"],
            cons=["Higher fertilizer use", "Weather dependent"],
            crop_compatibility_score=0.85,
            crop_compatibility_factors=["corn", "wheat", "soybean"]
        )
        
        # Create alternative application method
        alternative_method = ApplicationMethod(
            method_id=str(uuid4()),
            method_type=ApplicationMethodType.BAND,
            recommended_equipment=EquipmentSpecification(
                equipment_type=EquipmentType.SPREADER,
                capacity=8.0,
                capacity_unit="tons",
                application_width=30.0,
                application_rate_range={"min": 30.0, "max": 150.0},
                fuel_efficiency=0.75,
                maintenance_cost_per_hour=18.0
            ),
            application_rate=120.0,
            rate_unit="lbs/acre",
            application_timing="Apply during planting or early growth",
            efficiency_score=0.82,
            cost_per_acre=48.0,
            labor_requirements="High",
            environmental_impact="Very Low",
            pros=["More precise placement", "Reduced fertilizer use", "Better nutrient efficiency"],
            cons=["Requires specialized equipment", "Higher labor cost", "Slower application"],
            crop_compatibility_score=0.90,
            crop_compatibility_factors=["corn", "soybean"]
        )
        
        return ApplicationResponse(
            request_id=str(uuid4()),
            recommended_methods=[primary_method],
            primary_recommendation=primary_method,
            alternative_methods=[alternative_method],
            cost_comparison={
                "broadcast": 45.0,
                "band": 48.0
            },
            efficiency_analysis={
                "broadcast": {"efficiency": 0.78, "speed": "fast", "uniformity": "good"},
                "band": {"efficiency": 0.82, "speed": "medium", "uniformity": "excellent"}
            },
            equipment_compatibility={
                "spreader": True,
                "broadcast_head": True,
                "banding_equipment": False
            },
            processing_time_ms=1250.0,
            metadata={
                "confidence_score": 0.85,
                "environmental_impact_score": 0.75,
                "safety_considerations": [
                    "Wear appropriate PPE during application",
                    "Avoid application during high wind conditions",
                    "Ensure proper calibration of equipment"
                ],
                "recommendations": [
                    "Consider split application for better efficiency",
                    "Monitor soil moisture before application",
                    "Follow local regulations for fertilizer application"
                ]
            }
        )


class TestExpertValidationService:
    """Test suite for ExpertValidationService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return ExpertValidationService()
    
    @pytest.fixture
    def sample_application_request(self):
        """Create sample application request."""
        return TestDataFactory.create_sample_application_request()
    
    @pytest.fixture
    def sample_application_response(self):
        """Create sample application response."""
        return TestDataFactory.create_sample_application_response()
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, service):
        """Test service initialization and expert panel setup."""
        assert service is not None
        assert len(service.expert_database) > 0
        assert len(service.validation_requests) == 0
        assert len(service.expert_reviews) == 0
        assert len(service.field_test_plans) == 0
        assert len(service.field_test_results) == 0
        
        # Check that expert panel is initialized
        expert_panel = await service.get_expert_panel()
        assert len(expert_panel) == 4  # Should have 4 sample experts
        
        # Check expert types
        expert_types = set(expert["expert_type"] for expert in expert_panel)
        expected_types = {
            ExpertType.FERTILIZER_SPECIALIST.value,
            ExpertType.EXTENSION_AGENT.value,
            ExpertType.EQUIPMENT_SPECIALIST.value,
            ExpertType.AGRONOMIST.value
        }
        assert expert_types == expected_types
    
    @pytest.mark.asyncio
    async def test_submit_for_expert_validation(self, service, sample_application_request, sample_application_response):
        """Test submission for expert validation."""
        validation_request_id = await service.submit_for_expert_validation(
            application_request=sample_application_request,
            application_response=sample_application_response,
            validation_type="method_recommendation",
            priority="normal"
        )
        
        assert validation_request_id is not None
        assert validation_request_id in service.validation_requests
        
        validation_request = service.validation_requests[validation_request_id]
        assert validation_request.status == ValidationStatus.PENDING
        assert len(validation_request.assigned_experts) > 0
        assert validation_request.deadline > datetime.now()
        assert validation_request.priority == "normal"
    
    @pytest.mark.asyncio
    async def test_expert_selection_by_validation_type(self, service):
        """Test expert selection based on validation type."""
        # Test method recommendation validation
        experts = await service._select_experts_for_validation("method_recommendation")
        assert len(experts) > 0
        
        # Check that selected experts are appropriate for method recommendation
        for expert_id in experts:
            expert = service.expert_database[expert_id]
            assert expert.expert_type in [ExpertType.FERTILIZER_SPECIALIST, ExpertType.AGRONOMIST]
            assert expert.rating >= 4.5
        
        # Test equipment compatibility validation
        equipment_experts = await service._select_experts_for_validation("equipment_compatibility")
        assert len(equipment_experts) > 0
        
        for expert_id in equipment_experts:
            expert = service.expert_database[expert_id]
            assert expert.expert_type in [ExpertType.EQUIPMENT_SPECIALIST, ExpertType.EXTENSION_AGENT]
    
    @pytest.mark.asyncio
    async def test_submit_expert_review(self, service, sample_application_request, sample_application_response):
        """Test expert review submission."""
        # First submit for validation
        validation_request_id = await service.submit_for_expert_validation(
            application_request=sample_application_request,
            application_response=sample_application_response
        )
        
        # Get an assigned expert
        validation_request = service.validation_requests[validation_request_id]
        expert_id = validation_request.assigned_experts[0]
        
        # Submit expert review
        review_id = await service.submit_expert_review(
            validation_request_id=validation_request_id,
            expert_id=expert_id,
            recommendation_score=8.5,
            accuracy_score=9.0,
            feasibility_score=8.0,
            safety_score=9.5,
            cost_effectiveness_score=8.0,
            overall_approval=True,
            comments="Excellent recommendation with good technical accuracy",
            suggestions=["Consider split application for better efficiency"],
            concerns=["Monitor weather conditions closely"],
            confidence_level=0.9
        )
        
        assert review_id is not None
        assert review_id in service.expert_reviews
        
        review = service.expert_reviews[review_id]
        assert review.expert_id == expert_id
        assert review.validation_request_id == validation_request_id
        assert review.overall_approval is True
        assert review.recommendation_score == 8.5
        assert len(review.suggestions) == 1
        assert len(review.concerns) == 1
        
        # Check that validation request status was updated
        assert validation_request.status == ValidationStatus.IN_REVIEW
    
    @pytest.mark.asyncio
    async def test_get_validation_summary(self, service, sample_application_request, sample_application_response):
        """Test validation summary retrieval."""
        # Submit for validation
        validation_request_id = await service.submit_for_expert_validation(
            application_request=sample_application_request,
            application_response=sample_application_response
        )
        
        validation_request = service.validation_requests[validation_request_id]
        expert_ids = validation_request.assigned_experts
        
        # Submit multiple expert reviews
        for i, expert_id in enumerate(expert_ids[:2]):  # Submit reviews from 2 experts
            await service.submit_expert_review(
                validation_request_id=validation_request_id,
                expert_id=expert_id,
                recommendation_score=8.0 + i,
                accuracy_score=8.5 + i,
                feasibility_score=7.5 + i,
                safety_score=9.0,
                cost_effectiveness_score=8.0,
                overall_approval=True,
                comments=f"Review from expert {i+1}",
                confidence_level=0.85
            )
        
        # Get validation summary
        summary = await service.get_validation_summary(validation_request_id)
        
        assert summary["validation_request_id"] == validation_request_id
        assert summary["reviews_received"] == 2
        assert summary["consensus"] == "approved"  # Both experts approved
        assert summary["approval_rate"] == 1.0
        assert "average_scores" in summary
        assert "expert_reviews" in summary
        assert len(summary["expert_reviews"]) == 2
    
    @pytest.mark.asyncio
    async def test_create_field_test_plan(self, service, sample_application_request, sample_application_response):
        """Test field test plan creation."""
        # Submit for validation and get approval
        validation_request_id = await service.submit_for_expert_validation(
            application_request=sample_application_request,
            application_response=sample_application_response
        )
        
        # Create field test plan
        test_id = await service.create_field_test_plan(
            validation_request_id=validation_request_id,
            farm_id="farm_001",
            field_id="field_001",
            test_design={
                "experimental_design": "randomized_complete_block",
                "treatments": ["control", "recommended_method", "alternative_method"],
                "replications": 4,
                "plot_size_acres": 2.0
            },
            implementation_plan={
                "equipment_preparation": "Calibrate spreader and check all systems",
                "application_procedure": "Apply fertilizer according to recommended rates",
                "monitoring_protocol": "Daily monitoring of application quality"
            },
            data_collection_plan={
                "yield_data": "Harvest and weigh grain from each plot",
                "cost_data": "Track all input costs and labor hours",
                "environmental_data": "Monitor soil and water quality"
            },
            success_criteria={
                "yield_increase_percent": 5.0,
                "cost_savings_percent": 10.0,
                "farmer_satisfaction_score": 7.0
            },
            timeline={
                "start_date": datetime.now() + timedelta(days=7),
                "application_date": datetime.now() + timedelta(days=14),
                "harvest_date": datetime.now() + timedelta(days=120),
                "completion_date": datetime.now() + timedelta(days=130)
            },
            budget=5000.0
        )
        
        assert test_id is not None
        assert test_id in service.field_test_plans
        
        field_test_plan = service.field_test_plans[test_id]
        assert field_test_plan.validation_request_id == validation_request_id
        assert field_test_plan.farm_id == "farm_001"
        assert field_test_plan.field_id == "field_001"
        assert field_test_plan.status == FieldTestStatus.PLANNED
        assert field_test_plan.budget == 5000.0
        
        # Check that validation request status was updated
        validation_request = service.validation_requests[validation_request_id]
        assert validation_request.status == ValidationStatus.FIELD_TESTING
    
    @pytest.mark.asyncio
    async def test_submit_field_test_result(self, service, sample_application_request, sample_application_response):
        """Test field test result submission."""
        # Create field test plan first
        validation_request_id = await service.submit_for_expert_validation(
            application_request=sample_application_request,
            application_response=sample_application_response
        )
        
        test_id = await service.create_field_test_plan(
            validation_request_id=validation_request_id,
            farm_id="farm_001",
            field_id="field_001",
            test_design={"design": "test"},
            implementation_plan={"plan": "test"},
            data_collection_plan={"plan": "test"},
            success_criteria={"criteria": "test"},
            timeline={"start": datetime.now()},
            budget=1000.0
        )
        
        # Submit field test result
        result_id = await service.submit_field_test_result(
            test_id=test_id,
            implementation_success=True,
            yield_impact=8.5,  # 8.5% increase
            cost_savings=450.0,  # $450 savings
            farmer_satisfaction=8.0,
            environmental_impact={
                "nitrogen_leaching_reduction": 15.0,
                "soil_health_improvement": 5.0
            },
            lessons_learned=[
                "Split application improved efficiency",
                "Weather timing was critical for success"
            ],
            recommendations=[
                "Consider implementing split application",
                "Develop weather-based application timing"
            ],
            data_collected={
                "yield_data": {"control": 175.0, "treatment": 190.0},
                "cost_data": {"total_cost": 1800.0, "savings": 450.0}
            }
        )
        
        assert result_id is not None
        assert result_id in service.field_test_results
        
        field_test_result = service.field_test_results[result_id]
        assert field_test_result.test_id == test_id
        assert field_test_result.implementation_success is True
        assert field_test_result.yield_impact == 8.5
        assert field_test_result.cost_savings == 450.0
        assert field_test_result.farmer_satisfaction == 8.0
        assert len(field_test_result.lessons_learned) == 2
        assert len(field_test_result.recommendations) == 2
        
        # Check that field test plan status was updated
        field_test_plan = service.field_test_plans[test_id]
        assert field_test_plan.status == FieldTestStatus.COMPLETED
        
        # Check that validation request status was updated
        validation_request = service.validation_requests[validation_request_id]
        assert validation_request.status == ValidationStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_calculate_validation_metrics(self, service, sample_application_request, sample_application_response):
        """Test validation metrics calculation."""
        # Create some validation requests and results for metrics calculation
        validation_request_id = await service.submit_for_expert_validation(
            application_request=sample_application_request,
            application_response=sample_application_response
        )
        
        validation_request = service.validation_requests[validation_request_id]
        expert_ids = validation_request.assigned_experts
        
        # Submit expert reviews
        for expert_id in expert_ids[:2]:
            await service.submit_expert_review(
                validation_request_id=validation_request_id,
                expert_id=expert_id,
                recommendation_score=9.0,
                accuracy_score=9.0,
                feasibility_score=8.5,
                safety_score=9.5,
                cost_effectiveness_score=8.5,
                overall_approval=True,
                comments="Excellent recommendation",
                confidence_level=0.9
            )
        
        # Create field test and submit results
        test_id = await service.create_field_test_plan(
            validation_request_id=validation_request_id,
            farm_id="farm_001",
            field_id="field_001",
            test_design={"design": "test"},
            implementation_plan={"plan": "test"},
            data_collection_plan={"plan": "test"},
            success_criteria={"criteria": "test"},
            timeline={"start": datetime.now()},
            budget=1000.0
        )
        
        await service.submit_field_test_result(
            test_id=test_id,
            implementation_success=True,
            yield_impact=10.0,
            cost_savings=500.0,
            farmer_satisfaction=8.5,
            environmental_impact={"impact": "positive"},
            lessons_learned=["lesson1"],
            recommendations=["recommendation1"],
            data_collected={"data": "collected"}
        )
        
        # Calculate metrics
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        
        metrics = await service.calculate_validation_metrics(start_date, end_date)
        
        assert metrics.total_validations == 1
        assert metrics.expert_approval_rate == 1.0  # All experts approved
        assert metrics.farmer_satisfaction_rate == 1.0  # Farmer satisfaction >= 7.0
        assert metrics.recommendation_accuracy == 1.0  # Implementation was successful
        assert metrics.field_test_success_rate == 1.0  # Field test was successful
        assert metrics.expert_consensus_rate == 1.0  # Strong consensus
        assert metrics.validation_period == (start_date, end_date)
    
    @pytest.mark.asyncio
    async def test_add_expert_to_panel(self, service):
        """Test adding new expert to panel."""
        expert_id = await service.add_expert_to_panel(
            name="Dr. Test Expert",
            expert_type=ExpertType.SOIL_SCIENTIST,
            credentials="PhD Soil Science",
            specialization=["soil_health", "nutrient_cycling"],
            experience_years=10,
            certifications=["CCA", "CPSS"],
            contact_info={"email": "test@example.com", "phone": "+1-555-9999"},
            availability={"monday": True, "tuesday": True, "wednesday": False}
        )
        
        assert expert_id is not None
        assert expert_id in service.expert_database
        
        expert = service.expert_database[expert_id]
        assert expert.name == "Dr. Test Expert"
        assert expert.expert_type == ExpertType.SOIL_SCIENTIST
        assert expert.credentials == "PhD Soil Science"
        assert expert.experience_years == 10
        assert expert.rating == 5.0  # New experts start with perfect rating
        assert expert.review_count == 0
    
    @pytest.mark.asyncio
    async def test_get_validation_dashboard(self, service, sample_application_request, sample_application_response):
        """Test validation dashboard data retrieval."""
        # Create some data for dashboard
        validation_request_id = await service.submit_for_expert_validation(
            application_request=sample_application_request,
            application_response=sample_application_response
        )
        
        dashboard_data = await service.get_validation_dashboard()
        
        assert "recent_metrics" in dashboard_data
        assert "pending_validations" in dashboard_data
        assert "active_field_tests" in dashboard_data
        assert "expert_panel_size" in dashboard_data
        assert "expert_workload" in dashboard_data
        assert "performance_targets" in dashboard_data
        assert "targets_met" in dashboard_data
        
        assert dashboard_data["pending_validations"] >= 0
        assert dashboard_data["expert_panel_size"] == len(service.expert_database)
        assert "expert_approval_target" in dashboard_data["performance_targets"]
        assert "farmer_satisfaction_target" in dashboard_data["performance_targets"]
        assert "recommendation_accuracy_target" in dashboard_data["performance_targets"]


class TestAgriculturalValidation:
    """Agricultural domain validation tests."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return ExpertValidationService()
    
    @pytest.fixture
    def sample_application_request(self):
        """Create sample application request."""
        return TestDataFactory.create_sample_application_request()
    
    @pytest.fixture
    def sample_application_response(self):
        """Create sample application response."""
        return TestDataFactory.create_sample_application_response()
    
    @pytest.mark.asyncio
    async def test_fertilizer_specialist_validation(self, service):
        """Test validation by fertilizer specialists."""
        # Create a fertilizer-focused validation request
        application_request = TestDataFactory.create_sample_application_request()
        application_response = TestDataFactory.create_sample_application_response()
        
        validation_request_id = await service.submit_for_expert_validation(
            application_request=application_request,
            application_response=application_response,
            validation_type="method_recommendation"
        )
        
        validation_request = service.validation_requests[validation_request_id]
        
        # Check that fertilizer specialists are selected
        fertilizer_experts = [
            expert_id for expert_id in validation_request.assigned_experts
            if service.expert_database[expert_id].expert_type == ExpertType.FERTILIZER_SPECIALIST
        ]
        
        assert len(fertilizer_experts) > 0
        
        # Submit review from fertilizer specialist
        fertilizer_expert_id = fertilizer_experts[0]
        review_id = await service.submit_expert_review(
            validation_request_id=validation_request_id,
            expert_id=fertilizer_expert_id,
            recommendation_score=9.0,
            accuracy_score=9.5,
            feasibility_score=8.5,
            safety_score=9.0,
            cost_effectiveness_score=8.5,
            overall_approval=True,
            comments="Excellent nitrogen management recommendation. Rate and timing are optimal for corn at V6 stage.",
            suggestions=["Consider split application for better efficiency"],
            concerns=["Monitor soil moisture before application"],
            confidence_level=0.95
        )
        
        review = service.expert_reviews[review_id]
        assert review.expert_id == fertilizer_expert_id
        assert review.overall_approval is True
        assert review.accuracy_score >= 9.0  # High accuracy expected from specialist
        assert "nitrogen management" in review.comments.lower()
    
    @pytest.mark.asyncio
    async def test_equipment_specialist_validation(self, service):
        """Test validation by equipment specialists."""
        application_request = TestDataFactory.create_sample_application_request()
        application_response = TestDataFactory.create_sample_application_response()
        
        validation_request_id = await service.submit_for_expert_validation(
            application_request=application_request,
            application_response=application_response,
            validation_type="equipment_compatibility"
        )
        
        validation_request = service.validation_requests[validation_request_id]
        
        # Check that equipment specialists are selected
        equipment_experts = [
            expert_id for expert_id in validation_request.assigned_experts
            if service.expert_database[expert_id].expert_type == ExpertType.EQUIPMENT_SPECIALIST
        ]
        
        assert len(equipment_experts) > 0
        
        # Submit review from equipment specialist
        equipment_expert_id = equipment_experts[0]
        review_id = await service.submit_expert_review(
            validation_request_id=validation_request_id,
            expert_id=equipment_expert_id,
            recommendation_score=8.5,
            accuracy_score=8.0,
            feasibility_score=9.0,
            safety_score=9.5,
            cost_effectiveness_score=8.0,
            overall_approval=True,
            comments="Equipment compatibility is excellent. John Deere 1910 spreader is well-suited for broadcast application.",
            suggestions=["Ensure proper calibration before application"],
            concerns=["Check spreader pattern uniformity"],
            confidence_level=0.9
        )
        
        review = service.expert_reviews[review_id]
        assert review.expert_id == equipment_expert_id
        assert review.feasibility_score >= 9.0  # High feasibility expected from equipment specialist
        assert "equipment compatibility" in review.comments.lower()
        assert "calibration" in review.suggestions[0].lower()
    
    @pytest.mark.asyncio
    async def test_field_test_agricultural_validity(self, service):
        """Test field test agricultural validity."""
        application_request = TestDataFactory.create_sample_application_request()
        application_response = TestDataFactory.create_sample_application_response()
        
        # Create field test plan
        validation_request_id = await service.submit_for_expert_validation(
            application_request=application_request,
            application_response=application_response
        )
        
        test_id = await service.create_field_test_plan(
            validation_request_id=validation_request_id,
            farm_id="farm_001",
            field_id="field_001",
            test_design={
                "experimental_design": "randomized_complete_block",
                "treatments": ["control", "recommended_method"],
                "replications": 4,
                "plot_size_acres": 2.0,
                "statistical_power": 0.8
            },
            implementation_plan={
                "equipment_calibration": "Calibrate spreader to 150 lbs/acre",
                "application_timing": "Apply during early morning hours",
                "weather_monitoring": "Avoid application if rain expected within 24 hours"
            },
            data_collection_plan={
                "yield_data": "Harvest and weigh grain from each plot",
                "soil_data": "Collect soil samples before and after application",
                "cost_data": "Track fertilizer, labor, and equipment costs"
            },
            success_criteria={
                "yield_increase_percent": 5.0,
                "cost_savings_percent": 10.0,
                "farmer_satisfaction_score": 7.0,
                "environmental_impact": "positive"
            },
            timeline={
                "start_date": datetime.now() + timedelta(days=7),
                "application_date": datetime.now() + timedelta(days=14),
                "harvest_date": datetime.now() + timedelta(days=120),
                "completion_date": datetime.now() + timedelta(days=130)
            },
            budget=5000.0
        )
        
        field_test_plan = service.field_test_plans[test_id]
        
        # Validate agricultural aspects of field test plan
        assert field_test_plan.test_design["experimental_design"] == "randomized_complete_block"
        assert field_test_plan.test_design["replications"] >= 4  # Minimum for statistical validity
        assert field_test_plan.test_design["plot_size_acres"] >= 1.0  # Minimum plot size
        
        assert "equipment_calibration" in field_test_plan.implementation_plan
        assert "application_timing" in field_test_plan.implementation_plan
        assert "weather_monitoring" in field_test_plan.implementation_plan
        
        assert "yield_data" in field_test_plan.data_collection_plan
        assert "soil_data" in field_test_plan.data_collection_plan
        assert "cost_data" in field_test_plan.data_collection_plan
        
        assert field_test_plan.success_criteria["yield_increase_percent"] >= 5.0
        assert field_test_plan.success_criteria["farmer_satisfaction_score"] >= 7.0
    
    @pytest.mark.asyncio
    async def test_performance_targets_validation(self, service, sample_application_request, sample_application_response):
        """Test that performance targets are met."""
        # Create multiple validation requests with high-quality reviews
        for i in range(5):  # Create 5 validation requests
            validation_request_id = await service.submit_for_expert_validation(
                application_request=sample_application_request,
                application_response=sample_application_response
            )
            
            validation_request = service.validation_requests[validation_request_id]
            expert_ids = validation_request.assigned_experts
            
            # Submit high-quality expert reviews
            for expert_id in expert_ids[:2]:  # Submit from 2 experts each
                await service.submit_expert_review(
                    validation_request_id=validation_request_id,
                    expert_id=expert_id,
                    recommendation_score=9.0,
                    accuracy_score=9.0,
                    feasibility_score=8.5,
                    safety_score=9.5,
                    cost_effectiveness_score=8.5,
                    overall_approval=True,
                    comments="Excellent recommendation",
                    confidence_level=0.9
                )
            
            # Create field test and submit high-satisfaction results
            test_id = await service.create_field_test_plan(
                validation_request_id=validation_request_id,
                farm_id=f"farm_{i:03d}",
                field_id=f"field_{i:03d}",
                test_design={"design": "test"},
                implementation_plan={"plan": "test"},
                data_collection_plan={"plan": "test"},
                success_criteria={"criteria": "test"},
                timeline={"start": datetime.now()},
                budget=1000.0
            )
            
            await service.submit_field_test_result(
                test_id=test_id,
                implementation_success=True,
                yield_impact=8.0 + i,  # Varying yield impacts
                cost_savings=400.0 + i * 50,
                farmer_satisfaction=8.0 + i * 0.2,  # High satisfaction scores
                environmental_impact={"impact": "positive"},
                lessons_learned=["lesson"],
                recommendations=["recommendation"],
                data_collected={"data": "collected"}
            )
        
        # Calculate metrics
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        
        metrics = await service.calculate_validation_metrics(start_date, end_date)
        
        # Check that performance targets are met
        assert metrics.expert_approval_rate >= 0.95  # Target: >95%
        assert metrics.farmer_satisfaction_rate >= 0.85  # Target: >85%
        assert metrics.recommendation_accuracy >= 0.90  # Target: >90%
        
        # Check that all field tests were successful
        assert metrics.field_test_success_rate == 1.0
        
        # Check expert consensus
        assert metrics.expert_consensus_rate >= 0.8  # High consensus expected


class TestPerformanceAndScalability:
    """Performance and scalability tests."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return ExpertValidationService()
    
    @pytest.fixture
    def sample_application_request(self):
        """Create sample application request."""
        return TestDataFactory.create_sample_application_request()
    
    @pytest.fixture
    def sample_application_response(self):
        """Create sample application response."""
        return TestDataFactory.create_sample_application_response()
    
    @pytest.mark.asyncio
    async def test_concurrent_validation_requests(self, service):
        """Test handling of concurrent validation requests."""
        application_request = TestDataFactory.create_sample_application_request()
        application_response = TestDataFactory.create_sample_application_response()
        
        # Submit multiple validation requests concurrently
        tasks = []
        for i in range(10):
            task = service.submit_for_expert_validation(
                application_request=application_request,
                application_response=application_response
            )
            tasks.append(task)
        
        validation_request_ids = await asyncio.gather(*tasks)
        
        # Verify all requests were processed
        assert len(validation_request_ids) == 10
        assert len(service.validation_requests) == 10
        
        # Verify all requests have unique IDs
        assert len(set(validation_request_ids)) == 10
    
    @pytest.mark.asyncio
    async def test_large_expert_panel_performance(self, service):
        """Test performance with large expert panel."""
        # Add many experts to the panel
        expert_ids = []
        for i in range(50):
            expert_id = await service.add_expert_to_panel(
                name=f"Expert {i}",
                expert_type=ExpertType.AGRONOMIST,
                credentials=f"PhD Agronomy {i}",
                specialization=["crop_production"],
                experience_years=5 + i,
                certifications=["CCA"],
                contact_info={"email": f"expert{i}@example.com"},
                availability={"monday": True, "tuesday": True}
            )
            expert_ids.append(expert_id)
        
        # Test expert selection performance
        start_time = time.time()
        experts = await service._select_experts_for_validation("method_recommendation")
        selection_time = time.time() - start_time
        
        # Should complete quickly even with large panel
        assert selection_time < 1.0  # Less than 1 second
        assert len(experts) <= 3  # Should still select only top experts
    
    @pytest.mark.asyncio
    async def test_metrics_calculation_performance(self, service):
        """Test performance of metrics calculation with large dataset."""
        application_request = TestDataFactory.create_sample_application_request()
        application_response = TestDataFactory.create_sample_application_response()
        
        # Create many validation requests and results
        for i in range(100):
            validation_request_id = await service.submit_for_expert_validation(
                application_request=application_request,
                application_response=application_response
            )
            
            validation_request = service.validation_requests[validation_request_id]
            expert_ids = validation_request.assigned_experts
            
            # Submit expert reviews
            for expert_id in expert_ids[:2]:
                await service.submit_expert_review(
                    validation_request_id=validation_request_id,
                    expert_id=expert_id,
                    recommendation_score=8.0,
                    accuracy_score=8.0,
                    feasibility_score=8.0,
                    safety_score=8.0,
                    cost_effectiveness_score=8.0,
                    overall_approval=True,
                    comments="Good recommendation",
                    confidence_level=0.8
                )
        
        # Test metrics calculation performance
        start_time = time.time()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        
        metrics = await service.calculate_validation_metrics(start_date, end_date)
        calculation_time = time.time() - start_time
        
        # Should complete quickly even with large dataset
        assert calculation_time < 5.0  # Less than 5 seconds
        assert metrics.total_validations == 100
        assert metrics.expert_approval_rate > 0.9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])