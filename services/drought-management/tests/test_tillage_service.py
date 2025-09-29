"""
Comprehensive tests for Tillage Optimization Service

Tests for tillage system optimization, assessment, equipment recommendations,
transition planning, and water conservation analysis.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from decimal import Decimal
from uuid import uuid4
from datetime import datetime, date

from src.services.tillage_service import TillageOptimizationService
from src.models.tillage_models import (
    TillageOptimizationRequest,
    TillageOptimizationResponse,
    TillageSystemAssessment,
    EquipmentRecommendation,
    TransitionPlan,
    TillageSystem,
    TillageEquipment,
    SoilType,
    CropType,
    TransitionPhase
)


class TestTillageOptimizationService:
    """Test suite for TillageOptimizationService."""
    
    @pytest.fixture
    def service(self):
        """Create TillageOptimizationService instance."""
        return TillageOptimizationService()
    
    @pytest.fixture
    def sample_request(self):
        """Create sample tillage optimization request."""
        return TillageOptimizationRequest(
            field_id=uuid4(),
            current_tillage_system=TillageSystem.CONVENTIONAL,
            soil_type=SoilType.LOAM,
            soil_texture="Loam with good drainage",
            field_size_acres=100.0,
            slope_percent=5.0,
            drainage_class="Well drained",
            organic_matter_percent=2.5,
            compaction_level="Moderate",
            crop_rotation=[CropType.CORN, CropType.SOYBEAN],
            equipment_available=[TillageEquipment.MOLDBOARD_PLOW, TillageEquipment.DISK_HARROW],
            irrigation_available=True,
            cover_crop_usage=False,
            water_conservation_priority=8.0,
            soil_health_priority=7.0,
            labor_availability=6.0,
            budget_constraints=Decimal('50000.00')
        )
    
    @pytest.fixture
    def sample_request_no_till(self):
        """Create sample request for no-till optimization."""
        return TillageOptimizationRequest(
            field_id=uuid4(),
            current_tillage_system=TillageSystem.NO_TILL,
            soil_type=SoilType.SANDY_LOAM,
            soil_texture="Sandy loam with excellent drainage",
            field_size_acres=200.0,
            slope_percent=2.0,
            drainage_class="Excessively drained",
            organic_matter_percent=3.5,
            compaction_level="Low",
            crop_rotation=[CropType.CORN, CropType.SOYBEAN, CropType.WHEAT],
            equipment_available=[TillageEquipment.NO_TILL_DRILL],
            irrigation_available=False,
            cover_crop_usage=True,
            water_conservation_priority=9.0,
            soil_health_priority=9.0,
            labor_availability=8.0,
            budget_constraints=Decimal('100000.00')
        )

    @pytest.mark.asyncio
    async def test_optimize_tillage_system_success(self, service, sample_request):
        """Test successful tillage system optimization."""
        result = await service.optimize_tillage_system(sample_request)
        
        assert isinstance(result, TillageOptimizationResponse)
        assert result.field_id == sample_request.field_id
        assert result.request_id is not None
        assert result.current_system_assessment is not None
        assert result.recommended_systems is not None
        assert len(result.recommended_systems) > 0
        assert result.optimal_system is not None
        assert result.equipment_recommendations is not None
        assert result.water_savings_potential is not None
        assert result.soil_health_improvements is not None
        assert result.economic_analysis is not None
        assert result.implementation_priority in ["low", "medium", "high"]
        assert 0 <= result.confidence_score <= 100
        assert result.processing_time_ms > 0

    @pytest.mark.asyncio
    async def test_optimize_tillage_system_no_till_current(self, service, sample_request_no_till):
        """Test optimization when current system is already no-till."""
        result = await service.optimize_tillage_system(sample_request_no_till)
        
        assert isinstance(result, TillageOptimizationResponse)
        assert result.current_system_assessment.tillage_system == TillageSystem.NO_TILL
        # Should recommend staying with no-till or similar conservation systems
        assert result.optimal_system.tillage_system in [
            TillageSystem.NO_TILL, 
            TillageSystem.STRIP_TILL
        ]

    @pytest.mark.asyncio
    async def test_assess_tillage_system_no_till(self, service, sample_request):
        """Test assessment of no-till system."""
        assessment = await service._assess_tillage_system(TillageSystem.NO_TILL, sample_request)
        
        assert isinstance(assessment, TillageSystemAssessment)
        assert assessment.tillage_system == TillageSystem.NO_TILL
        assert assessment.water_conservation_score >= 80  # Should be high for no-till
        assert assessment.soil_health_score >= 80  # Should be high for no-till
        assert assessment.erosion_control_score >= 80  # Should be high for no-till
        assert assessment.fuel_efficiency_score >= 80  # Should be high for no-till
        assert assessment.labor_efficiency_score >= 70  # Should be good for no-till
        assert assessment.overall_score > 0
        assert assessment.compatibility_score > 0
        assert len(assessment.benefits) > 0
        assert len(assessment.challenges) > 0
        assert len(assessment.recommendations) > 0

    @pytest.mark.asyncio
    async def test_assess_tillage_system_conventional(self, service, sample_request):
        """Test assessment of conventional tillage system."""
        assessment = await service._assess_tillage_system(TillageSystem.CONVENTIONAL, sample_request)
        
        assert isinstance(assessment, TillageSystemAssessment)
        assert assessment.tillage_system == TillageSystem.CONVENTIONAL
        assert assessment.water_conservation_score <= 50  # Should be low for conventional
        assert assessment.soil_health_score <= 50  # Should be low for conventional
        assert assessment.erosion_control_score <= 50  # Should be low for conventional
        assert assessment.fuel_efficiency_score <= 50  # Should be low for conventional
        assert assessment.overall_score > 0
        assert len(assessment.benefits) > 0
        assert len(assessment.challenges) > 0

    def test_calculate_water_conservation_score(self, service, sample_request):
        """Test water conservation score calculation."""
        # Test no-till
        score = service._calculate_water_conservation_score(TillageSystem.NO_TILL, sample_request)
        assert 80 <= score <= 100
        
        # Test conventional tillage
        score = service._calculate_water_conservation_score(TillageSystem.CONVENTIONAL, sample_request)
        assert 20 <= score <= 50
        
        # Test strip-till
        score = service._calculate_water_conservation_score(TillageSystem.STRIP_TILL, sample_request)
        assert 70 <= score <= 90

    def test_calculate_soil_health_score(self, service, sample_request):
        """Test soil health score calculation."""
        # Test no-till
        score = service._calculate_soil_health_score(TillageSystem.NO_TILL, sample_request)
        assert 70 <= score <= 100
        
        # Test conventional tillage
        score = service._calculate_soil_health_score(TillageSystem.CONVENTIONAL, sample_request)
        assert 20 <= score <= 50

    def test_calculate_erosion_control_score(self, service, sample_request):
        """Test erosion control score calculation."""
        # Test no-till
        score = service._calculate_erosion_control_score(TillageSystem.NO_TILL, sample_request)
        assert 80 <= score <= 100
        
        # Test conventional tillage
        score = service._calculate_erosion_control_score(TillageSystem.CONVENTIONAL, sample_request)
        assert 15 <= score <= 40

    def test_calculate_fuel_efficiency_score(self, service, sample_request):
        """Test fuel efficiency score calculation."""
        # Test no-till
        score = service._calculate_fuel_efficiency_score(TillageSystem.NO_TILL, sample_request)
        assert score == 100  # Should be maximum
        
        # Test conventional tillage
        score = service._calculate_fuel_efficiency_score(TillageSystem.CONVENTIONAL, sample_request)
        assert 20 <= score <= 40

    def test_calculate_labor_efficiency_score(self, service, sample_request):
        """Test labor efficiency score calculation."""
        # Test no-till
        score = service._calculate_labor_efficiency_score(TillageSystem.NO_TILL, sample_request)
        assert 80 <= score <= 100
        
        # Test conventional tillage
        score = service._calculate_labor_efficiency_score(TillageSystem.CONVENTIONAL, sample_request)
        assert 30 <= score <= 50

    def test_calculate_equipment_cost_score(self, service, sample_request):
        """Test equipment cost score calculation."""
        # Test no-till (requires expensive equipment)
        score = service._calculate_equipment_cost_score(TillageSystem.NO_TILL, sample_request)
        assert 60 <= score <= 80
        
        # Test conventional tillage (uses common equipment)
        score = service._calculate_equipment_cost_score(TillageSystem.CONVENTIONAL, sample_request)
        assert 80 <= score <= 100

    def test_calculate_crop_yield_potential(self, service, sample_request):
        """Test crop yield potential calculation."""
        # Test strip-till (good for corn)
        score = service._calculate_crop_yield_potential(TillageSystem.STRIP_TILL, sample_request)
        assert 80 <= score <= 100
        
        # Test no-till (may take time to reach potential)
        score = service._calculate_crop_yield_potential(TillageSystem.NO_TILL, sample_request)
        assert 70 <= score <= 90

    def test_calculate_compatibility_score(self, service, sample_request):
        """Test compatibility score calculation."""
        # Test with loam soil (good compatibility)
        score = service._calculate_compatibility_score(TillageSystem.NO_TILL, sample_request)
        assert 60 <= score <= 100
        
        # Test with clay soil
        clay_request = sample_request.copy()
        clay_request.soil_type = SoilType.CLAY
        score = service._calculate_compatibility_score(TillageSystem.NO_TILL, clay_request)
        assert 40 <= score <= 80

    def test_generate_benefits(self, service, sample_request):
        """Test benefits generation."""
        benefits = service._generate_benefits(TillageSystem.NO_TILL, sample_request)
        assert isinstance(benefits, list)
        assert len(benefits) > 0
        assert any("water conservation" in benefit.lower() for benefit in benefits)
        assert any("soil" in benefit.lower() for benefit in benefits)

    def test_generate_challenges(self, service, sample_request):
        """Test challenges generation."""
        challenges = service._generate_challenges(TillageSystem.NO_TILL, sample_request)
        assert isinstance(challenges, list)
        assert len(challenges) > 0
        assert any("equipment" in challenge.lower() for challenge in challenges)

    def test_generate_recommendations(self, service, sample_request):
        """Test recommendations generation."""
        recommendations = service._generate_recommendations(TillageSystem.NO_TILL, sample_request)
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert any("transition" in rec.lower() for rec in recommendations)

    @pytest.mark.asyncio
    async def test_generate_equipment_recommendations(self, service, sample_request):
        """Test equipment recommendations generation."""
        recommendations = await service._generate_equipment_recommendations(
            TillageSystem.NO_TILL, sample_request
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        for rec in recommendations:
            assert isinstance(rec, EquipmentRecommendation)
            assert rec.equipment_type is not None
            assert rec.equipment_name is not None
            assert rec.estimated_cost > 0
            assert rec.cost_per_acre > 0
            assert rec.fuel_consumption >= 0
            assert rec.labor_hours_per_acre >= 0
            assert rec.maintenance_cost_per_year >= 0
            assert rec.lifespan_years > 0
            assert 0 <= rec.compatibility_score <= 100
            assert rec.priority_level in ["low", "medium", "high"]

    def test_calculate_equipment_compatibility(self, service, sample_request):
        """Test equipment compatibility calculation."""
        score = service._calculate_equipment_compatibility(
            TillageEquipment.NO_TILL_DRILL, sample_request
        )
        assert 0 <= score <= 100

    def test_determine_equipment_priority(self, service, sample_request):
        """Test equipment priority determination."""
        priority = service._determine_equipment_priority(
            TillageEquipment.NO_TILL_DRILL, sample_request
        )
        assert priority in ["low", "medium", "high"]

    @pytest.mark.asyncio
    async def test_create_transition_plan(self, service, sample_request):
        """Test transition plan creation."""
        plan = await service._create_transition_plan(
            TillageSystem.CONVENTIONAL,
            TillageSystem.NO_TILL,
            sample_request
        )
        
        assert isinstance(plan, TransitionPlan)
        assert plan.target_system == TillageSystem.NO_TILL
        assert plan.transition_duration_years > 0
        assert len(plan.phases) > 0
        assert len(plan.equipment_acquisition_plan) > 0
        assert len(plan.cost_breakdown) > 0
        assert len(plan.risk_assessment) > 0
        assert len(plan.success_metrics) > 0
        assert len(plan.timeline) > 0

    def test_create_transition_phases(self, service):
        """Test transition phases creation."""
        phases = service._create_transition_phases(
            TillageSystem.CONVENTIONAL,
            TillageSystem.NO_TILL,
            2
        )
        
        assert isinstance(phases, list)
        assert len(phases) > 0
        
        for phase in phases:
            assert "phase" in phase
            assert "duration_months" in phase
            assert "description" in phase
            assert "activities" in phase
            assert isinstance(phase["activities"], list)

    @pytest.mark.asyncio
    async def test_calculate_water_savings_potential(self, service, sample_request):
        """Test water savings potential calculation."""
        current_assessment = await service._assess_tillage_system(
            TillageSystem.CONVENTIONAL, sample_request
        )
        optimal_assessment = await service._assess_tillage_system(
            TillageSystem.NO_TILL, sample_request
        )
        
        savings = await service._calculate_water_savings_potential(
            current_assessment, optimal_assessment, sample_request
        )
        
        assert isinstance(savings, dict)
        assert "soil_moisture_retention" in savings
        assert "irrigation_water_savings" in savings
        assert "runoff_reduction" in savings
        assert "evaporation_reduction" in savings
        assert "total_water_savings" in savings
        
        # Should show improvement for no-till vs conventional
        assert savings["total_water_savings"] > 0

    @pytest.mark.asyncio
    async def test_calculate_soil_health_improvements(self, service, sample_request):
        """Test soil health improvements calculation."""
        current_assessment = await service._assess_tillage_system(
            TillageSystem.CONVENTIONAL, sample_request
        )
        optimal_assessment = await service._assess_tillage_system(
            TillageSystem.NO_TILL, sample_request
        )
        
        improvements = await service._calculate_soil_health_improvements(
            current_assessment, optimal_assessment, sample_request
        )
        
        assert isinstance(improvements, dict)
        assert "organic_matter_increase" in improvements
        assert "biological_activity" in improvements
        assert "soil_structure" in improvements
        assert "nutrient_cycling" in improvements
        assert "overall_soil_health" in improvements
        
        # Should show improvement for no-till vs conventional
        assert improvements["overall_soil_health"] > 0

    @pytest.mark.asyncio
    async def test_perform_economic_analysis(self, service, sample_request):
        """Test economic analysis."""
        current_assessment = await service._assess_tillage_system(
            TillageSystem.CONVENTIONAL, sample_request
        )
        optimal_assessment = await service._assess_tillage_system(
            TillageSystem.NO_TILL, sample_request
        )
        equipment_recommendations = await service._generate_equipment_recommendations(
            TillageSystem.NO_TILL, sample_request
        )
        
        analysis = await service._perform_economic_analysis(
            current_assessment, optimal_assessment, equipment_recommendations, sample_request
        )
        
        assert isinstance(analysis, dict)
        assert "annual_fuel_savings" in analysis
        assert "annual_labor_savings" in analysis
        assert "total_equipment_cost" in analysis
        assert "payback_period_years" in analysis
        assert "roi_percentage" in analysis
        assert "net_present_value" in analysis

    def test_determine_implementation_priority(self, service):
        """Test implementation priority determination."""
        # Create mock assessments
        optimal_system = MagicMock()
        optimal_system.overall_score = 85
        
        water_savings = {"total_water_savings": 25.0}
        economic_analysis = {"payback_period_years": 2.5}
        
        priority = service._determine_implementation_priority(
            optimal_system, water_savings, economic_analysis
        )
        
        assert priority in ["low", "medium", "high"]

    def test_calculate_confidence_score(self, service, sample_request):
        """Test confidence score calculation."""
        # Create mock assessments
        optimal_system = MagicMock()
        optimal_system.compatibility_score = 80
        optimal_system.overall_score = 85
        
        system_assessments = [optimal_system, MagicMock()]
        system_assessments[1].overall_score = 75
        
        confidence = service._calculate_confidence_score(
            sample_request, optimal_system, system_assessments
        )
        
        assert 0 <= confidence <= 100

    def test_initialize_tillage_systems(self, service):
        """Test tillage systems initialization."""
        assert hasattr(service, 'tillage_systems')
        assert len(service.tillage_systems) > 0
        
        # Check that all tillage systems are included
        for system in TillageSystem:
            assert system in service.tillage_systems
            system_data = service.tillage_systems[system]
            assert "water_conservation" in system_data
            assert "soil_health" in system_data
            assert "erosion_control" in system_data
            assert "fuel_efficiency" in system_data
            assert "labor_efficiency" in system_data
            assert "equipment_cost" in system_data

    def test_initialize_equipment_database(self, service):
        """Test equipment database initialization."""
        assert hasattr(service, 'equipment_database')
        assert len(service.equipment_database) > 0
        
        # Check that equipment is available for major tillage systems
        assert TillageSystem.NO_TILL in service.equipment_database
        assert TillageSystem.STRIP_TILL in service.equipment_database
        assert TillageSystem.CONVENTIONAL in service.equipment_database

    @pytest.mark.asyncio
    async def test_error_handling(self, service):
        """Test error handling in optimization."""
        # Test with invalid request
        invalid_request = TillageOptimizationRequest(
            field_id=uuid4(),
            current_tillage_system=TillageSystem.CONVENTIONAL,
            soil_type=SoilType.LOAM,
            soil_texture="Test",
            field_size_acres=-1,  # Invalid field size
            slope_percent=5.0,
            drainage_class="Well drained",
            organic_matter_percent=2.5,
            compaction_level="Moderate",
            crop_rotation=[CropType.CORN],
            water_conservation_priority=8.0,
            soil_health_priority=7.0,
            labor_availability=6.0
        )
        
        with pytest.raises(Exception):
            await service.optimize_tillage_system(invalid_request)

    @pytest.mark.asyncio
    async def test_performance_requirements(self, service, sample_request):
        """Test that optimization meets performance requirements."""
        import time
        
        start_time = time.time()
        result = await service.optimize_tillage_system(sample_request)
        elapsed_time = time.time() - start_time
        
        # Should complete within reasonable time (less than 5 seconds)
        assert elapsed_time < 5.0
        assert result.processing_time_ms < 5000

    @pytest.mark.asyncio
    async def test_agricultural_validation(self, service, sample_request):
        """Test agricultural validation of recommendations."""
        result = await service.optimize_tillage_system(sample_request)
        
        # Check that recommendations make agricultural sense
        optimal_system = result.optimal_system
        
        # No-till should have high water conservation score
        if optimal_system.tillage_system == TillageSystem.NO_TILL:
            assert optimal_system.water_conservation_score >= 80
            assert optimal_system.soil_health_score >= 70
            assert optimal_system.erosion_control_score >= 80
        
        # Strip-till should be good compromise
        elif optimal_system.tillage_system == TillageSystem.STRIP_TILL:
            assert optimal_system.water_conservation_score >= 70
            assert optimal_system.soil_health_score >= 60
        
        # Check that water savings are realistic
        water_savings = result.water_savings_potential
        assert water_savings["total_water_savings"] >= 0
        assert water_savings["total_water_savings"] <= 100  # Should not exceed 100%

    @pytest.mark.asyncio
    async def test_equipment_cost_validation(self, service, sample_request):
        """Test equipment cost validation."""
        result = await service.optimize_tillage_system(sample_request)
        
        for equipment in result.equipment_recommendations:
            # Equipment costs should be realistic
            assert equipment.estimated_cost > 0
            assert equipment.cost_per_acre > 0
            assert equipment.maintenance_cost_per_year >= 0
            assert equipment.lifespan_years > 0
            
            # No-till equipment should be more expensive
            if equipment.equipment_type == TillageEquipment.NO_TILL_DRILL:
                assert equipment.estimated_cost >= 50000  # Should be expensive

    @pytest.mark.asyncio
    async def test_transition_plan_validation(self, service, sample_request):
        """Test transition plan validation."""
        result = await service.optimize_tillage_system(sample_request)
        
        if result.transition_plan:
            plan = result.transition_plan
            
            # Transition duration should be reasonable
            assert 1 <= plan.transition_duration_years <= 5
            
            # Should have phases
            assert len(plan.phases) > 0
            
            # Should have cost breakdown
            assert len(plan.cost_breakdown) > 0
            assert "total" in plan.cost_breakdown
            
            # Should have risk assessment
            assert len(plan.risk_assessment) > 0
            
            # Should have success metrics
            assert len(plan.success_metrics) > 0


class TestTillageOptimizationValidator:
    """Test suite for TillageOptimizationValidator."""
    
    def test_validate_field_conditions(self, sample_request):
        """Test field conditions validation."""
        from src.models.tillage_models import TillageOptimizationValidator
        
        validator = TillageOptimizationValidator()
        issues = validator.validate_field_conditions(sample_request)
        
        assert isinstance(issues, list)
        # Should not have issues for normal conditions
        assert len(issues) == 0

    def test_validate_field_conditions_high_slope(self):
        """Test validation with high slope."""
        from src.models.tillage_models import TillageOptimizationValidator
        
        validator = TillageOptimizationValidator()
        
        high_slope_request = TillageOptimizationRequest(
            field_id=uuid4(),
            current_tillage_system=TillageSystem.CONVENTIONAL,
            soil_type=SoilType.LOAM,
            soil_texture="Loam",
            field_size_acres=100.0,
            slope_percent=20.0,  # High slope
            drainage_class="Well drained",
            organic_matter_percent=2.5,
            compaction_level="Moderate",
            crop_rotation=[CropType.CORN],
            water_conservation_priority=8.0,
            soil_health_priority=7.0,
            labor_availability=6.0
        )
        
        issues = validator.validate_field_conditions(high_slope_request)
        assert len(issues) > 0
        assert any("slope" in issue.lower() for issue in issues)

    def test_validate_equipment_compatibility(self):
        """Test equipment compatibility validation."""
        from src.models.tillage_models import TillageOptimizationValidator
        
        validator = TillageOptimizationValidator()
        
        # Test compatible equipment
        compatible = validator.validate_equipment_compatibility(
            TillageEquipment.NO_TILL_DRILL, SoilType.LOAM
        )
        assert compatible is True
        
        # Test incompatible equipment
        incompatible = validator.validate_equipment_compatibility(
            TillageEquipment.NO_TILL_DRILL, SoilType.CLAY
        )
        assert incompatible is False

    def test_calculate_transition_difficulty(self):
        """Test transition difficulty calculation."""
        from src.models.tillage_models import TillageOptimizationValidator
        
        validator = TillageOptimizationValidator()
        
        # Test easy transition
        difficulty = validator.calculate_transition_difficulty(
            TillageSystem.CONVENTIONAL, TillageSystem.REDUCED_TILL
        )
        assert difficulty == "low"
        
        # Test difficult transition
        difficulty = validator.calculate_transition_difficulty(
            TillageSystem.CONVENTIONAL, TillageSystem.NO_TILL
        )
        assert difficulty == "high"
        
        # Test medium transition
        difficulty = validator.calculate_transition_difficulty(
            TillageSystem.REDUCED_TILL, TillageSystem.NO_TILL
        )
        assert difficulty == "medium"


class TestTillageModels:
    """Test suite for tillage models."""
    
    def test_tillage_optimization_request_validation(self):
        """Test TillageOptimizationRequest validation."""
        request = TillageOptimizationRequest(
            field_id=uuid4(),
            current_tillage_system=TillageSystem.CONVENTIONAL,
            soil_type=SoilType.LOAM,
            soil_texture="Loam",
            field_size_acres=100.0,
            slope_percent=5.0,
            drainage_class="Well drained",
            organic_matter_percent=2.5,
            compaction_level="Moderate",
            crop_rotation=[CropType.CORN, CropType.SOYBEAN],
            water_conservation_priority=8.0,
            soil_health_priority=7.0,
            labor_availability=6.0
        )
        
        assert request.field_id is not None
        assert request.current_tillage_system == TillageSystem.CONVENTIONAL
        assert request.soil_type == SoilType.LOAM
        assert request.field_size_acres == 100.0
        assert len(request.crop_rotation) == 2

    def test_tillage_system_assessment_creation(self):
        """Test TillageSystemAssessment creation."""
        assessment = TillageSystemAssessment(
            tillage_system=TillageSystem.NO_TILL,
            water_conservation_score=90.0,
            soil_health_score=85.0,
            erosion_control_score=95.0,
            fuel_efficiency_score=100.0,
            labor_efficiency_score=80.0,
            equipment_cost_score=70.0,
            crop_yield_potential=85.0,
            overall_score=87.5,
            compatibility_score=80.0,
            transition_difficulty="high",
            benefits=["Water conservation", "Soil health"],
            challenges=["Equipment cost", "Transition time"],
            recommendations=["Gradual transition", "Cover crops"]
        )
        
        assert assessment.tillage_system == TillageSystem.NO_TILL
        assert assessment.water_conservation_score == 90.0
        assert assessment.overall_score == 87.5
        assert len(assessment.benefits) == 2
        assert len(assessment.challenges) == 2
        assert len(assessment.recommendations) == 2

    def test_equipment_recommendation_creation(self):
        """Test EquipmentRecommendation creation."""
        recommendation = EquipmentRecommendation(
            equipment_type=TillageEquipment.NO_TILL_DRILL,
            equipment_name="John Deere 1590 No-Till Drill",
            estimated_cost=Decimal('85000.00'),
            cost_per_acre=Decimal('8.50'),
            fuel_consumption=0.5,
            labor_hours_per_acre=0.3,
            maintenance_cost_per_year=Decimal('5000.00'),
            lifespan_years=15,
            compatibility_score=85.0,
            priority_level="high"
        )
        
        assert recommendation.equipment_type == TillageEquipment.NO_TILL_DRILL
        assert recommendation.estimated_cost == Decimal('85000.00')
        assert recommendation.fuel_consumption == 0.5
        assert recommendation.compatibility_score == 85.0
        assert recommendation.priority_level == "high"

    def test_transition_plan_creation(self):
        """Test TransitionPlan creation."""
        plan = TransitionPlan(
            target_system=TillageSystem.NO_TILL,
            transition_duration_years=2,
            phases=[
                {
                    "phase": TransitionPhase.PLANNING,
                    "duration_months": 3,
                    "description": "Planning phase",
                    "activities": ["Assessment", "Planning"]
                }
            ],
            equipment_acquisition_plan=[],
            cost_breakdown={
                "equipment": Decimal('80000.00'),
                "training": Decimal('3000.00'),
                "total": Decimal('83000.00')
            },
            risk_assessment={
                "yield_reduction": {
                    "probability": "medium",
                    "impact": "medium"
                }
            },
            success_metrics=["Soil health", "Water conservation"],
            timeline=[]
        )
        
        assert plan.target_system == TillageSystem.NO_TILL
        assert plan.transition_duration_years == 2
        assert len(plan.phases) == 1
        assert len(plan.cost_breakdown) == 3
        assert len(plan.risk_assessment) == 1
        assert len(plan.success_metrics) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])