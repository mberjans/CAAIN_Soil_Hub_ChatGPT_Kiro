"""
Comprehensive tests for the MethodComparisonService.

Tests the multi-criteria analysis, statistical comparison, economic analysis,
and environmental impact assessment features of the comparison engine.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from typing import List, Dict, Any

from src.services.comparison_service import (
    MethodComparisonService, ComparisonCriteria, ComparisonResult, MultiCriteriaAnalysis
)
from src.models.application_models import (
    ApplicationMethod, ApplicationMethodType, FieldConditions, CropRequirements,
    FertilizerSpecification, EquipmentSpecification, FertilizerForm, EquipmentType
)


class TestMethodComparisonService:
    """Test suite for MethodComparisonService."""
    
    @pytest.fixture
    def comparison_service(self):
        """Create comparison service instance."""
        return MethodComparisonService()
    
    @pytest.fixture
    def sample_field_conditions(self):
        """Sample field conditions for testing."""
        return FieldConditions(
            field_size_acres=100.0,
            soil_type="loam",
            drainage_class="well_drained",
            slope_percent=2.0,
            irrigation_available=True,
            access_roads=["main_road", "field_access"]
        )
    
    @pytest.fixture
    def sample_crop_requirements(self):
        """Sample crop requirements for testing."""
        return CropRequirements(
            crop_type="corn",
            growth_stage="vegetative",
            target_yield=180.0,
            nutrient_requirements={"nitrogen": 150, "phosphorus": 60, "potassium": 120},
            application_timing_preferences=["early_season", "mid_season"]
        )
    
    @pytest.fixture
    def sample_fertilizer_spec(self):
        """Sample fertilizer specification for testing."""
        return FertilizerSpecification(
            fertilizer_type="NPK",
            form=FertilizerForm.GRANULAR,
            npk_ratio="10-10-10",
            solubility=0.8,
            release_rate="immediate",
            cost_per_unit=0.5,
            unit="lbs"
        )
    
    @pytest.fixture
    def sample_equipment(self):
        """Sample equipment for testing."""
        return [
            EquipmentSpecification(
                equipment_type=EquipmentType.SPREADER,
                capacity=1000.0,
                cost_per_hour=25.0,
                maintenance_cost_per_hour=2.0
            )
        ]
    
    @pytest.fixture
    def sample_methods(self):
        """Sample application methods for testing."""
        method_a = ApplicationMethod(
            method_id="broadcast_001",
            method_type=ApplicationMethodType.BROADCAST,
            recommended_equipment=EquipmentSpecification(
                equipment_type=EquipmentType.SPREADER,
                capacity=1000.0,
                cost_per_hour=25.0
            ),
            application_rate=150.0,
            rate_unit="lbs/acre",
            application_timing="Pre-plant application",
            efficiency_score=0.7,
            cost_per_acre=15.0,
            labor_requirements="medium",
            environmental_impact="moderate",
            pros=["Simple application", "Good for large fields"],
            cons=["Lower efficiency", "Potential runoff"]
        )
        
        method_b = ApplicationMethod(
            method_id="band_001",
            method_type=ApplicationMethodType.BAND,
            recommended_equipment=EquipmentSpecification(
                equipment_type=EquipmentType.SPREADER,
                capacity=800.0,
                cost_per_hour=30.0
            ),
            application_rate=120.0,
            rate_unit="lbs/acre",
            application_timing="At planting",
            efficiency_score=0.8,
            cost_per_acre=20.0,
            labor_requirements="medium",
            environmental_impact="low",
            pros=["Higher efficiency", "Reduced runoff"],
            cons=["More complex setup", "Higher cost"]
        )
        
        return method_a, method_b
    
    @pytest.mark.asyncio
    async def test_compare_methods_comprehensive(
        self, comparison_service, sample_methods, sample_field_conditions,
        sample_crop_requirements, sample_fertilizer_spec, sample_equipment
    ):
        """Test comprehensive method comparison."""
        method_a, method_b = sample_methods
        
        comparison = await comparison_service.compare_methods(
            method_a=method_a,
            method_b=method_b,
            field_conditions=sample_field_conditions,
            crop_requirements=sample_crop_requirements,
            fertilizer_spec=sample_fertilizer_spec,
            available_equipment=sample_equipment
        )
        
        # Verify comparison structure
        assert comparison.method_a is not None
        assert comparison.method_b is not None
        assert comparison.comparison_criteria is not None
        assert comparison.method_a_scores is not None
        assert comparison.method_b_scores is not None
        assert comparison.winner_by_criteria is not None
        assert comparison.overall_winner is not None
        assert comparison.recommendation is not None
        
        # Verify scores are between 0 and 1
        for score in comparison.method_a_scores.values():
            assert 0.0 <= score <= 1.0
        for score in comparison.method_b_scores.values():
            assert 0.0 <= score <= 1.0
    
    @pytest.mark.asyncio
    async def test_compare_cost_effectiveness(
        self, comparison_service, sample_methods, sample_field_conditions
    ):
        """Test cost effectiveness comparison."""
        method_a, method_b = sample_methods
        
        result = await comparison_service._compare_criterion(
            ComparisonCriteria.COST_EFFECTIVENESS,
            method_a, method_b, sample_field_conditions,
            None, None, []
        )
        
        assert isinstance(result, ComparisonResult)
        assert 0.0 <= result.method_a_score <= 1.0
        assert 0.0 <= result.method_b_score <= 1.0
        assert result.winner in ["method_a", "method_b"]
        assert 0.0 <= result.confidence_level <= 1.0
        assert len(result.analysis_notes) > 0
    
    @pytest.mark.asyncio
    async def test_compare_application_efficiency(
        self, comparison_service, sample_methods
    ):
        """Test application efficiency comparison."""
        method_a, method_b = sample_methods
        
        result = await comparison_service._compare_criterion(
            ComparisonCriteria.APPLICATION_EFFICIENCY,
            method_a, method_b, None, None, None, []
        )
        
        assert isinstance(result, ComparisonResult)
        assert result.method_a_score == method_a.efficiency_score
        assert result.method_b_score == method_b.efficiency_score
        assert result.winner == "method_b"  # method_b has higher efficiency
    
    @pytest.mark.asyncio
    async def test_compare_environmental_impact(
        self, comparison_service, sample_methods, sample_field_conditions
    ):
        """Test environmental impact comparison."""
        method_a, method_b = sample_methods
        
        result = await comparison_service._compare_criterion(
            ComparisonCriteria.ENVIRONMENTAL_IMPACT,
            method_a, method_b, sample_field_conditions, None, None, []
        )
        
        assert isinstance(result, ComparisonResult)
        assert 0.0 <= result.method_a_score <= 1.0
        assert 0.0 <= result.method_b_score <= 1.0
        # method_b should win due to lower environmental impact
        assert result.winner == "method_b"
    
    @pytest.mark.asyncio
    async def test_compare_equipment_needs(
        self, comparison_service, sample_methods, sample_equipment
    ):
        """Test equipment needs comparison."""
        method_a, method_b = sample_methods
        
        result = await comparison_service._compare_criterion(
            ComparisonCriteria.EQUIPMENT_NEEDS,
            method_a, method_b, None, None, None, sample_equipment
        )
        
        assert isinstance(result, ComparisonResult)
        assert 0.0 <= result.method_a_score <= 1.0
        assert 0.0 <= result.method_b_score <= 1.0
        # Both methods use same equipment type, so scores should be similar
        assert abs(result.method_a_score - result.method_b_score) < 0.5
    
    @pytest.mark.asyncio
    async def test_compare_field_suitability(
        self, comparison_service, sample_methods, sample_field_conditions
    ):
        """Test field suitability comparison."""
        method_a, method_b = sample_methods
        
        result = await comparison_service._compare_criterion(
            ComparisonCriteria.FIELD_SUITABILITY,
            method_a, method_b, sample_field_conditions, None, None, []
        )
        
        assert isinstance(result, ComparisonResult)
        assert 0.0 <= result.method_a_score <= 1.0
        assert 0.0 <= result.method_b_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_compare_nutrient_use_efficiency(
        self, comparison_service, sample_methods, sample_crop_requirements
    ):
        """Test nutrient use efficiency comparison."""
        method_a, method_b = sample_methods
        
        result = await comparison_service._compare_criterion(
            ComparisonCriteria.NUTRIENT_USE_EFFICIENCY,
            method_a, method_b, None, sample_crop_requirements, None, []
        )
        
        assert isinstance(result, ComparisonResult)
        assert 0.0 <= result.method_a_score <= 1.0
        assert 0.0 <= result.method_b_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_compare_timing_flexibility(
        self, comparison_service, sample_methods, sample_crop_requirements
    ):
        """Test timing flexibility comparison."""
        method_a, method_b = sample_methods
        
        result = await comparison_service._compare_criterion(
            ComparisonCriteria.TIMING_FLEXIBILITY,
            method_a, method_b, None, sample_crop_requirements, None, []
        )
        
        assert isinstance(result, ComparisonResult)
        assert 0.0 <= result.method_a_score <= 1.0
        assert 0.0 <= result.method_b_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_compare_weather_dependency(
        self, comparison_service, sample_methods
    ):
        """Test weather dependency comparison."""
        method_a, method_b = sample_methods
        
        result = await comparison_service._compare_criterion(
            ComparisonCriteria.WEATHER_DEPENDENCY,
            method_a, method_b, None, None, None, []
        )
        
        assert isinstance(result, ComparisonResult)
        assert 0.0 <= result.method_a_score <= 1.0
        assert 0.0 <= result.method_b_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_multi_criteria_analysis(
        self, comparison_service, sample_methods, sample_field_conditions,
        sample_crop_requirements, sample_fertilizer_spec, sample_equipment
    ):
        """Test multi-criteria analysis."""
        method_a, method_b = sample_methods
        
        analysis = await comparison_service._perform_multi_criteria_analysis(
            method_a, method_b, sample_field_conditions,
            sample_crop_requirements, sample_fertilizer_spec,
            sample_equipment, list(ComparisonCriteria), comparison_service.default_weights
        )
        
        assert isinstance(analysis, MultiCriteriaAnalysis)
        assert len(analysis.criteria_scores) > 0
        assert len(analysis.weighted_scores) == 2
        assert analysis.overall_winner in [method_a.method_type.value, method_b.method_type.value]
        assert 0.0 <= analysis.recommendation_strength <= 1.0
        assert isinstance(analysis.sensitivity_analysis, dict)
    
    @pytest.mark.asyncio
    async def test_custom_criteria_and_weights(
        self, comparison_service, sample_methods, sample_field_conditions,
        sample_crop_requirements, sample_fertilizer_spec, sample_equipment
    ):
        """Test comparison with custom criteria and weights."""
        method_a, method_b = sample_methods
        
        custom_criteria = [
            ComparisonCriteria.COST_EFFECTIVENESS,
            ComparisonCriteria.APPLICATION_EFFICIENCY,
            ComparisonCriteria.ENVIRONMENTAL_IMPACT
        ]
        
        custom_weights = {
            ComparisonCriteria.COST_EFFECTIVENESS: 0.5,
            ComparisonCriteria.APPLICATION_EFFICIENCY: 0.3,
            ComparisonCriteria.ENVIRONMENTAL_IMPACT: 0.2
        }
        
        comparison = await comparison_service.compare_methods(
            method_a=method_a,
            method_b=method_b,
            field_conditions=sample_field_conditions,
            crop_requirements=sample_crop_requirements,
            fertilizer_spec=sample_fertilizer_spec,
            available_equipment=sample_equipment,
            comparison_criteria=custom_criteria,
            custom_weights=custom_weights
        )
        
        assert len(comparison.comparison_criteria) == 3
        assert ComparisonCriteria.COST_EFFECTIVENESS in comparison.comparison_criteria
        assert ComparisonCriteria.APPLICATION_EFFICIENCY in comparison.comparison_criteria
        assert ComparisonCriteria.ENVIRONMENTAL_IMPACT in comparison.comparison_criteria
    
    def test_calculate_total_cost(self, comparison_service, sample_methods, sample_field_conditions):
        """Test total cost calculation."""
        method_a, method_b = sample_methods
        
        cost_a = asyncio.run(comparison_service._calculate_total_cost(method_a, sample_field_conditions))
        cost_b = asyncio.run(comparison_service._calculate_total_cost(method_b, sample_field_conditions))
        
        assert cost_a > 0
        assert cost_b > 0
        # method_a should be cheaper due to lower cost_per_acre
        assert cost_a < cost_b
    
    def test_adjust_environmental_score(self, comparison_service, sample_field_conditions):
        """Test environmental score adjustment based on field conditions."""
        base_score = 0.8
        
        # Test with moderate slope
        adjusted_score = comparison_service._adjust_environmental_score(base_score, sample_field_conditions)
        assert adjusted_score <= base_score
        
        # Test with steep slope
        steep_field = FieldConditions(
            field_size_acres=100.0,
            soil_type="loam",
            drainage_class="well_drained",
            slope_percent=8.0,  # Steep slope
            irrigation_available=True,
            access_roads=["main_road"]
        )
        adjusted_score_steep = comparison_service._adjust_environmental_score(base_score, steep_field)
        assert adjusted_score_steep < adjusted_score
    
    def test_check_equipment_compatibility(self, comparison_service, sample_methods, sample_equipment):
        """Test equipment compatibility checking."""
        method_a, method_b = sample_methods
        
        compat_a = comparison_service._check_equipment_compatibility(method_a, sample_equipment)
        compat_b = comparison_service._check_equipment_compatibility(method_b, sample_equipment)
        
        assert compat_a == 1.0  # Should be compatible
        assert compat_b == 1.0  # Should be compatible
        
        # Test with incompatible equipment
        incompatible_equipment = [
            EquipmentSpecification(
                equipment_type=EquipmentType.SPRAYER,  # Different type
                capacity=500.0,
                cost_per_hour=20.0
            )
        ]
        
        compat_incompatible = comparison_service._check_equipment_compatibility(method_a, incompatible_equipment)
        assert compat_incompatible == 0.0  # Should be incompatible
    
    def test_assess_field_suitability(self, comparison_service, sample_methods, sample_field_conditions):
        """Test field suitability assessment."""
        method_a, method_b = sample_methods
        
        suitability_a = comparison_service._assess_field_suitability(method_a, sample_field_conditions)
        suitability_b = comparison_service._assess_field_suitability(method_b, sample_field_conditions)
        
        assert 0.0 <= suitability_a <= 1.0
        assert 0.0 <= suitability_b <= 1.0
        
        # Test with small field (should favor band over broadcast)
        small_field = FieldConditions(
            field_size_acres=5.0,  # Small field
            soil_type="loam",
            drainage_class="well_drained",
            slope_percent=1.0,
            irrigation_available=True,
            access_roads=["main_road"]
        )
        
        suitability_a_small = comparison_service._assess_field_suitability(method_a, small_field)
        suitability_b_small = comparison_service._assess_field_suitability(method_b, small_field)
        
        # Band should be more suitable for small fields
        assert suitability_b_small > suitability_a_small
    
    def test_calculate_nutrient_efficiency(self, comparison_service, sample_methods, sample_crop_requirements):
        """Test nutrient efficiency calculation."""
        method_a, method_b = sample_methods
        
        efficiency_a = comparison_service._calculate_nutrient_efficiency(method_a, sample_crop_requirements)
        efficiency_b = comparison_service._calculate_nutrient_efficiency(method_b, sample_crop_requirements)
        
        assert 0.0 <= efficiency_a <= 1.0
        assert 0.0 <= efficiency_b <= 1.0
        
        # Test with different crop types
        soybean_requirements = CropRequirements(
            crop_type="soybean",
            growth_stage="vegetative",
            target_yield=50.0,
            nutrient_requirements={"nitrogen": 0, "phosphorus": 40, "potassium": 80},
            application_timing_preferences=["early_season"]
        )
        
        efficiency_a_soy = comparison_service._calculate_nutrient_efficiency(method_a, soybean_requirements)
        efficiency_b_soy = comparison_service._calculate_nutrient_efficiency(method_b, soybean_requirements)
        
        assert 0.0 <= efficiency_a_soy <= 1.0
        assert 0.0 <= efficiency_b_soy <= 1.0
    
    def test_assess_timing_flexibility(self, comparison_service, sample_methods, sample_crop_requirements):
        """Test timing flexibility assessment."""
        method_a, method_b = sample_methods
        
        flexibility_a = comparison_service._assess_timing_flexibility(method_a, sample_crop_requirements)
        flexibility_b = comparison_service._assess_timing_flexibility(method_b, sample_crop_requirements)
        
        assert 0.0 <= flexibility_a <= 1.0
        assert 0.0 <= flexibility_b <= 1.0
        
        # Broadcast should be more flexible than band
        assert flexibility_a > flexibility_b
    
    def test_assess_weather_dependency(self, comparison_service, sample_methods):
        """Test weather dependency assessment."""
        method_a, method_b = sample_methods
        
        weather_a = comparison_service._assess_weather_dependency(method_a)
        weather_b = comparison_service._assess_weather_dependency(method_b)
        
        assert 0.0 <= weather_a <= 1.0
        assert 0.0 <= weather_b <= 1.0
        
        # Band should be less weather dependent than broadcast
        assert weather_b > weather_a
    
    @pytest.mark.asyncio
    async def test_sensitivity_analysis(
        self, comparison_service, sample_methods, sample_field_conditions,
        sample_crop_requirements, sample_fertilizer_spec, sample_equipment
    ):
        """Test sensitivity analysis."""
        method_a, method_b = sample_methods
        
        # Create mock criteria scores
        criteria_scores = {
            ComparisonCriteria.COST_EFFECTIVENESS: ComparisonResult(
                method_a_score=0.8, method_b_score=0.6, winner="method_a",
                score_difference=0.2, confidence_level=0.9, analysis_notes=[]
            ),
            ComparisonCriteria.APPLICATION_EFFICIENCY: ComparisonResult(
                method_a_score=0.7, method_b_score=0.8, winner="method_b",
                score_difference=0.1, confidence_level=0.8, analysis_notes=[]
            )
        }
        
        weights = {
            ComparisonCriteria.COST_EFFECTIVENESS: 0.6,
            ComparisonCriteria.APPLICATION_EFFICIENCY: 0.4
        }
        
        sensitivity = await comparison_service._perform_sensitivity_analysis(
            criteria_scores, weights, method_a.method_type.value, method_b.method_type.value
        )
        
        assert isinstance(sensitivity, dict)
        assert ComparisonCriteria.COST_EFFECTIVENESS in sensitivity
        assert ComparisonCriteria.APPLICATION_EFFICIENCY in sensitivity
        
        for criterion, analysis in sensitivity.items():
            assert "original_weight" in analysis
            assert "variations" in analysis
            assert "sensitive" in analysis
            assert len(analysis["variations"]) == 3  # Three variations tested
    
    @pytest.mark.asyncio
    async def test_error_handling(self, comparison_service):
        """Test error handling in comparison service."""
        # Test with invalid criterion
        with pytest.raises(ValueError):
            await comparison_service._compare_criterion(
                "invalid_criterion", None, None, None, None, None, []
            )
    
    @pytest.mark.asyncio
    async def test_performance_requirements(self, comparison_service, sample_methods,
                                         sample_field_conditions, sample_crop_requirements,
                                         sample_fertilizer_spec, sample_equipment):
        """Test that comparison meets performance requirements."""
        method_a, method_b = sample_methods
        
        import time
        start_time = time.time()
        
        comparison = await comparison_service.compare_methods(
            method_a=method_a,
            method_b=method_b,
            field_conditions=sample_field_conditions,
            crop_requirements=sample_crop_requirements,
            fertilizer_spec=sample_fertilizer_spec,
            available_equipment=sample_equipment
        )
        
        elapsed_time = time.time() - start_time
        
        # Should complete within reasonable time (less than 5 seconds)
        assert elapsed_time < 5.0
        assert comparison is not None


class TestComparisonCriteria:
    """Test comparison criteria enum."""
    
    def test_criteria_values(self):
        """Test that all criteria have valid values."""
        criteria = [
            ComparisonCriteria.COST_EFFECTIVENESS,
            ComparisonCriteria.APPLICATION_EFFICIENCY,
            ComparisonCriteria.ENVIRONMENTAL_IMPACT,
            ComparisonCriteria.LABOR_REQUIREMENTS,
            ComparisonCriteria.EQUIPMENT_NEEDS,
            ComparisonCriteria.FIELD_SUITABILITY,
            ComparisonCriteria.NUTRIENT_USE_EFFICIENCY,
            ComparisonCriteria.TIMING_FLEXIBILITY,
            ComparisonCriteria.SKILL_REQUIREMENTS,
            ComparisonCriteria.WEATHER_DEPENDENCY
        ]
        
        for criterion in criteria:
            assert isinstance(criterion.value, str)
            assert len(criterion.value) > 0


class TestComparisonResult:
    """Test ComparisonResult dataclass."""
    
    def test_comparison_result_creation(self):
        """Test ComparisonResult creation and validation."""
        result = ComparisonResult(
            method_a_score=0.8,
            method_b_score=0.6,
            winner="method_a",
            score_difference=0.2,
            confidence_level=0.9,
            analysis_notes=["Test note"]
        )
        
        assert result.method_a_score == 0.8
        assert result.method_b_score == 0.6
        assert result.winner == "method_a"
        assert result.score_difference == 0.2
        assert result.confidence_level == 0.9
        assert len(result.analysis_notes) == 1


class TestMultiCriteriaAnalysis:
    """Test MultiCriteriaAnalysis dataclass."""
    
    def test_multi_criteria_analysis_creation(self):
        """Test MultiCriteriaAnalysis creation and validation."""
        criteria_scores = {
            "cost": ComparisonResult(
                method_a_score=0.8, method_b_score=0.6, winner="method_a",
                score_difference=0.2, confidence_level=0.9, analysis_notes=[]
            )
        }
        
        weighted_scores = {"method_a": 0.8, "method_b": 0.6}
        
        analysis = MultiCriteriaAnalysis(
            criteria_scores=criteria_scores,
            weighted_scores=weighted_scores,
            overall_winner="method_a",
            sensitivity_analysis={},
            recommendation_strength=0.2
        )
        
        assert len(analysis.criteria_scores) == 1
        assert len(analysis.weighted_scores) == 2
        assert analysis.overall_winner == "method_a"
        assert analysis.recommendation_strength == 0.2