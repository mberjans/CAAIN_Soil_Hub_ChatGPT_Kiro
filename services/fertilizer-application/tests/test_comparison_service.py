"""
Unit tests for the MethodComparisonService in the fertilizer application service.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from decimal import Decimal

from src.services.comparison_service import MethodComparisonService, ComparisonCriteria, ComparisonResult, MultiCriteriaAnalysis
from src.models.application_models import (
    ApplicationMethod, ApplicationMethodType, FieldConditions, 
    CropRequirements, FertilizerSpecification, EquipmentSpecification
)
from src.models.method_models import ApplicationTiming, ApplicationPrecision, EnvironmentalImpact


@pytest.fixture
def comparison_service():
    """Create a MethodComparisonService instance for testing."""
    return MethodComparisonService()


@pytest.fixture
def sample_method_a():
    """Create a sample application method A."""
    return ApplicationMethod(
        method_id="method_a",
        method_type=ApplicationMethodType.BROADCAST,
        method_name="Broadcast Application",
        description="Broadcast fertilizer across entire field",
        application_timing=[ApplicationTiming.PRE_PLANT],
        precision_level=ApplicationPrecision.BROADCAST,
        environmental_impact=EnvironmentalImpact.MODERATE,
        equipment_requirements=["spreader"],
        labor_requirements="medium",
        skill_requirements="semi_skilled",
        cost_per_acre=15.0,
        efficiency_score=0.7,
        recommended_equipment=EquipmentSpecification(
            equipment_type="spreader",
            capacity=10.0,
            maintenance_cost_per_hour=15.0
        )
    )


@pytest.fixture
def sample_method_b():
    """Create a sample application method B."""
    return ApplicationMethod(
        method_id="method_b",
        method_type=ApplicationMethodType.BAND,
        method_name="Band Application",
        description="Apply fertilizer in bands near seed row",
        application_timing=[ApplicationTiming.AT_PLANTING],
        precision_level=ApplicationPrecision.BAND,
        environmental_impact=EnvironmentalImpact.LOW,
        equipment_requirements=["spreader"],
        labor_requirements="high",
        skill_requirements="skilled",
        cost_per_acre=20.0,
        efficiency_score=0.85,
        recommended_equipment=EquipmentSpecification(
            equipment_type="spreader",
            capacity=8.0,
            maintenance_cost_per_hour=20.0
        )
    )


@pytest.fixture
def sample_field_conditions():
    """Create sample field conditions."""
    return FieldConditions(
        field_size_acres=100.0,
        soil_type="loam",
        slope_percent=2.5,
        drainage_class="well_drained",
        ph_level=6.5,
        organic_matter_percent=3.2,
        previous_crop_type="soybean",
        climate_zone="5b",
        temperature_range_f=(60, 80),
        precipitation_inch=2.5
    )


@pytest.fixture
def sample_crop_requirements():
    """Create sample crop requirements."""
    return CropRequirements(
        crop_type="corn",
        growth_stage="V6",
        target_yield=200.0,
        nutrient_requirements={"nitrogen": 150.0, "phosphorus": 40.0, "potassium": 80.0},
        application_timing_preferences=[ApplicationTiming.AT_PLANTING],
        growth_stage_deadlines={"V6": "2024-06-15", "R1": "2024-07-20"}
    )


@pytest.fixture
def sample_fertilizer_spec():
    """Create sample fertilizer specification."""
    return FertilizerSpecification(
        fertilizer_type="nitrogen",
        nutrient_content={"nitrogen": 46.0},
        application_rate_lb_per_acre=150.0,
        fertilizer_form="granular",
        application_rate_unit="lbs/acre",
        nutrient_ratios={"n": 1.0, "p": 0.2, "k": 0.1},
        application_timing=ApplicationTiming.AT_PLANTING,
        cost_per_unit=0.5,
        cost_unit="per_lb"
    )


@pytest.fixture
def sample_equipment():
    """Create sample equipment specification."""
    return EquipmentSpecification(
        equipment_id="eq_001",
        equipment_type="spreader",
        manufacturer="John Deere",
        model="1234",
        year=2022,
        capacity=10.0,
        maintenance_cost_per_hour=15.0,
        operator_skills_required="skilled",
        compatibility_notes="Standard 3-point hitch"
    )


class TestMethodComparisonService:
    """Test suite for the MethodComparisonService."""

    @pytest.mark.asyncio
    async def test_compare_methods_success(
        self, 
        comparison_service, 
        sample_method_a, 
        sample_method_b,
        sample_field_conditions,
        sample_crop_requirements,
        sample_fertilizer_spec,
        sample_equipment
    ):
        """Test successful comparison of two application methods."""
        result = await comparison_service.compare_methods(
            sample_method_a,
            sample_method_b,
            sample_field_conditions,
            sample_crop_requirements,
            sample_fertilizer_spec,
            [sample_equipment]
        )

        # Verify the result structure
        assert result.method_a is not None
        assert result.method_b is not None
        assert result.comparison_criteria is not None
        assert result.method_a_scores is not None
        assert result.method_b_scores is not None
        assert result.winner_by_criteria is not None
        assert result.overall_winner is not None
        assert result.recommendation is not None

        # Verify method names are preserved
        assert result.method_a.method_name == sample_method_a.method_name
        assert result.method_b.method_name == sample_method_b.method_name

    @pytest.mark.asyncio
    async def test_compare_cost_effectiveness(
        self, 
        comparison_service, 
        sample_method_a, 
        sample_method_b
    ):
        """Test cost effectiveness comparison."""
        result = await comparison_service._compare_cost_effectiveness(
            sample_method_a,
            sample_method_b,
            FieldConditions(
                field_size_acres=100.0,
                soil_type="loam"
            )
        )

        assert isinstance(result, ComparisonResult)
        assert result.method_a_score >= 0 and result.method_a_score <= 1.0
        assert result.method_b_score >= 0 and result.method_b_score <= 1.0
        assert result.winner in ["method_a", "method_b"]
        assert result.confidence_level >= 0 and result.confidence_level <= 1.0
        assert len(result.analysis_notes) > 0

    @pytest.mark.asyncio
    async def test_compare_application_efficiency(
        self, 
        comparison_service, 
        sample_method_a, 
        sample_method_b
    ):
        """Test application efficiency comparison."""
        result = await comparison_service._compare_application_efficiency(
            sample_method_a,
            sample_method_b
        )

        assert isinstance(result, ComparisonResult)
        assert result.method_a_score == sample_method_a.efficiency_score
        assert result.method_b_score == sample_method_b.efficiency_score
        assert result.confidence_level >= 0 and result.confidence_level <= 1.0

    @pytest.mark.asyncio
    async def test_compare_environmental_impact(
        self, 
        comparison_service, 
        sample_method_a, 
        sample_method_b,
        sample_field_conditions
    ):
        """Test environmental impact comparison."""
        result = await comparison_service._compare_environmental_impact(
            sample_method_a,
            sample_method_b,
            sample_field_conditions
        )

        assert isinstance(result, ComparisonResult)
        assert result.method_a_score >= 0 and result.method_a_score <= 1.0
        assert result.method_b_score >= 0 and result.method_b_score <= 1.0
        assert result.winner in ["method_a", "method_b"]

    @pytest.mark.asyncio
    async def test_compare_labor_requirements(
        self, 
        comparison_service, 
        sample_method_a, 
        sample_method_b
    ):
        """Test labor requirements comparison."""
        result = await comparison_service._compare_labor_requirements(
            sample_method_a,
            sample_method_b
        )

        assert isinstance(result, ComparisonResult)
        assert result.method_a_score >= 0 and result.method_a_score <= 1.0
        assert result.method_b_score >= 0 and result.method_b_score <= 1.0

    @pytest.mark.asyncio
    async def test_compare_equipment_needs(
        self, 
        comparison_service, 
        sample_method_a, 
        sample_method_b,
        sample_equipment
    ):
        """Test equipment needs comparison."""
        result = await comparison_service._compare_equipment_needs(
            sample_method_a,
            sample_method_b,
            [sample_equipment]
        )

        assert isinstance(result, ComparisonResult)
        assert result.method_a_score >= 0 and result.method_a_score <= 1.0
        assert result.method_b_score >= 0 and result.method_b_score <= 1.0

    @pytest.mark.asyncio
    async def test_compare_field_suitability(
        self, 
        comparison_service, 
        sample_method_a, 
        sample_method_b,
        sample_field_conditions
    ):
        """Test field suitability comparison."""
        result = await comparison_service._compare_field_suitability(
            sample_method_a,
            sample_method_b,
            sample_field_conditions
        )

        assert isinstance(result, ComparisonResult)
        assert result.method_a_score >= 0 and result.method_a_score <= 1.0
        assert result.method_b_score >= 0 and result.method_b_score <= 1.0

    @pytest.mark.asyncio
    async def test_compare_nutrient_use_efficiency(
        self, 
        comparison_service, 
        sample_method_a, 
        sample_method_b,
        sample_crop_requirements
    ):
        """Test nutrient use efficiency comparison."""
        result = await comparison_service._compare_nutrient_use_efficiency(
            sample_method_a,
            sample_method_b,
            sample_crop_requirements
        )

        assert isinstance(result, ComparisonResult)
        assert result.method_a_score >= 0 and result.method_a_score <= 1.0
        assert result.method_b_score >= 0 and result.method_b_score <= 1.0

    @pytest.mark.asyncio
    async def test_compare_timing_flexibility(
        self, 
        comparison_service, 
        sample_method_a, 
        sample_method_b,
        sample_crop_requirements
    ):
        """Test timing flexibility comparison."""
        result = await comparison_service._compare_timing_flexibility(
            sample_method_a,
            sample_method_b,
            sample_crop_requirements
        )

        assert isinstance(result, ComparisonResult)
        assert result.method_a_score >= 0 and result.method_a_score <= 1.0
        assert result.method_b_score >= 0 and result.method_b_score <= 1.0

    @pytest.mark.asyncio
    async def test_compare_weather_dependency(
        self, 
        comparison_service, 
        sample_method_a, 
        sample_method_b
    ):
        """Test weather dependency comparison."""
        result = await comparison_service._compare_weather_dependency(
            sample_method_a,
            sample_method_b
        )

        assert isinstance(result, ComparisonResult)
        assert result.method_a_score >= 0 and result.method_a_score <= 1.0
        assert result.method_b_score >= 0 and result.method_b_score <= 1.0

    def test_calculate_total_cost(self, comparison_service, sample_method_a, sample_field_conditions):
        """Test total cost calculation."""
        cost = asyncio.run(
            comparison_service._calculate_total_cost(sample_method_a, sample_field_conditions)
        )
        
        assert isinstance(cost, float)
        assert cost >= 0

    def test_adjust_environmental_score(self, comparison_service, sample_field_conditions):
        """Test environmental score adjustment based on field conditions."""
        base_score = 0.8
        adjusted_score = comparison_service._adjust_environmental_score(base_score, sample_field_conditions)
        
        assert isinstance(adjusted_score, float)
        assert 0 <= adjusted_score <= 1.0

    def test_check_equipment_compatibility(self, comparison_service, sample_method_a, sample_equipment):
        """Test equipment compatibility checking."""
        compatibility = comparison_service._check_equipment_compatibility(sample_method_a, [sample_equipment])
        
        assert isinstance(compatibility, float)
        assert compatibility in [0.0, 1.0]  # Either compatible or not

    def test_assess_field_suitability(self, comparison_service, sample_method_a, sample_field_conditions):
        """Test field suitability assessment."""
        suitability = comparison_service._assess_field_suitability(sample_method_a, sample_field_conditions)
        
        assert isinstance(suitability, float)
        assert 0 <= suitability <= 1.0

    def test_calculate_nutrient_efficiency(self, comparison_service, sample_method_a, sample_crop_requirements):
        """Test nutrient efficiency calculation."""
        efficiency = comparison_service._calculate_nutrient_efficiency(sample_method_a, sample_crop_requirements)
        
        assert isinstance(efficiency, float)
        assert 0 <= efficiency <= 1.0

    def test_assess_timing_flexibility(self, comparison_service, sample_method_a, sample_crop_requirements):
        """Test timing flexibility assessment."""
        flexibility = comparison_service._assess_timing_flexibility(sample_method_a, sample_crop_requirements)
        
        assert isinstance(flexibility, float)
        assert 0 <= flexibility <= 1.0

    def test_assess_weather_dependency(self, comparison_service, sample_method_a):
        """Test weather dependency assessment."""
        dependency = comparison_service._assess_weather_dependency(sample_method_a)
        
        assert isinstance(dependency, float)
        assert 0 <= dependency <= 1.0

    @pytest.mark.asyncio
    async def test_perform_sensitivity_analysis(self, comparison_service, sample_method_a, sample_method_b):
        """Test sensitivity analysis functionality."""
        # Create comparison results
        comparison_result = ComparisonResult(
            method_a_score=0.8,
            method_b_score=0.6,
            winner="method_a",
            score_difference=0.2,
            confidence_level=0.9,
            analysis_notes=["Test analysis"]
        )
        
        criteria_scores = {ComparisonCriteria.COST_EFFECTIVENESS.value: comparison_result}
        weights = {ComparisonCriteria.COST_EFFECTIVENESS.value: 0.2}
        
        sensitivity_results = await comparison_service._perform_sensitivity_analysis(
            criteria_scores,
            weights,
            sample_method_a.method_type,
            sample_method_b.method_type
        )
        
        assert isinstance(sensitivity_results, dict)
        assert ComparisonCriteria.COST_EFFECTIVENESS.value in sensitivity_results
        assert "variations" in sensitivity_results[ComparisonCriteria.COST_EFFECTIVENESS.value]

    @pytest.mark.asyncio
    async def test_multi_criteria_analysis(
        self, 
        comparison_service, 
        sample_method_a, 
        sample_method_b,
        sample_field_conditions,
        sample_crop_requirements,
        sample_fertilizer_spec,
        sample_equipment
    ):
        """Test multi-criteria analysis functionality."""
        criteria = [ComparisonCriteria.COST_EFFECTIVENESS, ComparisonCriteria.APPLICATION_EFFICIENCY]
        weights = {
            ComparisonCriteria.COST_EFFECTIVENESS: 0.5,
            ComparisonCriteria.APPLICATION_EFFICIENCY: 0.5
        }
        
        result = await comparison_service._perform_multi_criteria_analysis(
            sample_method_a,
            sample_method_b,
            sample_field_conditions,
            sample_crop_requirements,
            sample_fertilizer_spec,
            [sample_equipment],
            criteria,
            weights
        )
        
        assert isinstance(result, MultiCriteriaAnalysis)
        assert result.criteria_scores is not None
        assert result.weighted_scores is not None
        assert result.overall_winner is not None

    def test_initialization(self, comparison_service):
        """Test service initialization."""
        assert comparison_service.default_weights is not None
        assert len(comparison_service.default_weights) == 10  # All criteria
        assert ComparisonCriteria.COST_EFFECTIVENESS in comparison_service.default_weights

    @pytest.mark.asyncio
    async def test_compare_methods_with_custom_criteria(
        self, 
        comparison_service, 
        sample_method_a, 
        sample_method_b,
        sample_field_conditions,
        sample_crop_requirements,
        sample_fertilizer_spec,
        sample_equipment
    ):
        """Test comparison with custom criteria selection."""
        result = await comparison_service.compare_methods(
            sample_method_a,
            sample_method_b,
            sample_field_conditions,
            sample_crop_requirements,
            sample_fertilizer_spec,
            [sample_equipment],
            comparison_criteria=[ComparisonCriteria.COST_EFFECTIVENESS, ComparisonCriteria.APPLICATION_EFFICIENCY]
        )

        assert result.comparison_criteria == [ComparisonCriteria.COST_EFFECTIVENESS, ComparisonCriteria.APPLICATION_EFFICIENCY]

    @pytest.mark.asyncio
    async def test_compare_methods_with_custom_weights(
        self, 
        comparison_service, 
        sample_method_a, 
        sample_method_b,
        sample_field_conditions,
        sample_crop_requirements,
        sample_fertilizer_spec,
        sample_equipment
    ):
        """Test comparison with custom weights."""
        custom_weights = {
            ComparisonCriteria.COST_EFFECTIVENESS: 0.8,
            ComparisonCriteria.APPLICATION_EFFICIENCY: 0.2
        }
        
        result = await comparison_service.compare_methods(
            sample_method_a,
            sample_method_b,
            sample_field_conditions,
            sample_crop_requirements,
            sample_fertilizer_spec,
            [sample_equipment],
            custom_weights=custom_weights
        )

        # The result should reflect the custom weights
        assert result.recommendation is not None

    @pytest.mark.asyncio
    async def test_compare_criteria_invalid(
        self, 
        comparison_service, 
        sample_method_a, 
        sample_method_b,
        sample_field_conditions,
        sample_crop_requirements,
        sample_fertilizer_spec,
        sample_equipment
    ):
        """Test comparison with invalid criterion."""
        with pytest.raises(ValueError) as exc_info:
            await comparison_service._compare_criterion(
                "invalid_criterion",
                sample_method_a,
                sample_method_b,
                sample_field_conditions,
                sample_crop_requirements,
                sample_fertilizer_spec,
                [sample_equipment]
            )
        
        assert "Unknown comparison criterion" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_compare_methods_exception_handling(
        self, 
        comparison_service, 
        sample_method_a, 
        sample_method_b
    ):
        """Test exception handling in comparison method."""
        with patch.object(comparison_service, '_perform_multi_criteria_analysis', side_effect=Exception("Test error")):
            with pytest.raises(Exception) as exc_info:
                await comparison_service.compare_methods(
                    sample_method_a,
                    sample_method_b,
                    FieldConditions(field_size_acres=100.0, soil_type="loam"),
                    CropRequirements(crop_type="corn", growth_stage="V6"),
                    FertilizerSpecification(fertilizer_type="nitrogen", application_rate_lb_per_acre=150.0),
                    []
                )
            
            assert "Test error" in str(exc_info.value)