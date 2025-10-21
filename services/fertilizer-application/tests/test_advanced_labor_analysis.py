"""
Unit tests for Advanced Labor Analysis Service.

This test suite verifies the functionality of the advanced labor analysis service,
including labor efficiency calculations, optimization, and ROI analysis.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime
from decimal import Decimal

from src.models.application_models import (
    ApplicationMethod, FieldConditions, CropRequirements,
    FertilizerSpecification, EquipmentSpecification, ApplicationMethodType, EquipmentType
)
from src.services.advanced_labor_analysis_service import (
    AdvancedLaborAnalysisService, LaborEfficiencyScore, LaborOptimizationResult
)


@pytest.fixture
def advanced_labor_service():
    """Create an instance of AdvancedLaborAnalysisService for testing."""
    return AdvancedLaborAnalysisService()


@pytest.fixture
def sample_field_conditions():
    """Sample field conditions for testing."""
    return FieldConditions(
        field_size_acres=100.0,
        soil_type="loam",
        slope_percent=2.5,
        irrigation_available=False
    )


@pytest.fixture
def sample_crop_requirements():
    """Sample crop requirements for testing."""
    return CropRequirements(
        crop_type="corn",
        growth_stage="V6",
        target_yield=180.0,
        nutrient_requirements={"nitrogen": 150.0, "phosphorus": 40.0, "potassium": 120.0}
    )


@pytest.fixture
def sample_fertilizer_specification():
    """Sample fertilizer specification for testing."""
    return FertilizerSpecification(
        fertilizer_type="nitrogen",
        npk_ratio="30-0-0",
        form="liquid",
        cost_per_unit=0.80
    )


@pytest.fixture
def sample_equipment_specifications():
    """Sample equipment specifications for testing."""
    return [
        EquipmentSpecification(
            equipment_type=EquipmentType.SPRAYER,
            capacity=1000.0,
            application_width=60.0,
            fuel_efficiency=5.0
        ),
        EquipmentSpecification(
            equipment_type=EquipmentType.SPREADER,
            capacity=800.0,
            application_width=40.0,
            fuel_efficiency=4.0
        )
    ]


@pytest.fixture
def sample_application_methods(sample_equipment_specifications):
    """Sample application methods for testing."""
    return [
        ApplicationMethod(
            method_id="method_1",
            method_type=ApplicationMethodType.BROADCAST,
            recommended_equipment=sample_equipment_specifications[1],
            application_rate=100.0,
            rate_unit="lbs/acre",
            application_timing="pre-plant",
            efficiency_score=0.75,
            cost_per_acre=45.0,
            labor_requirements="semi-skilled",
            environmental_impact="medium",
            pros=["Low cost", "Fast application"],
            cons=["Lower precision", "Weather dependent"]
        ),
        ApplicationMethod(
            method_id="method_2",
            method_type=ApplicationMethodType.BAND,
            recommended_equipment=sample_equipment_specifications[0],
            application_rate=80.0,
            rate_unit="lbs/acre",
            application_timing="at-planting",
            efficiency_score=0.85,
            cost_per_acre=55.0,
            labor_requirements="skilled",
            environmental_impact="low",
            pros=["Higher efficiency", "Targeted application"],
            cons=["Higher cost", "Requires skilled labor"]
        )
    ]


@pytest.mark.asyncio
async def test_analyze_labor_efficiency(
    advanced_labor_service,
    sample_application_methods,
    sample_field_conditions,
    sample_crop_requirements,
    sample_equipment_specifications
):
    """Test labor efficiency analysis for different application methods."""
    efficiency_scores = await advanced_labor_service.analyze_labor_efficiency(
        sample_application_methods,
        sample_field_conditions,
        sample_crop_requirements,
        sample_equipment_specifications
    )
    
    # Verify that we get efficiency scores for both methods
    assert len(efficiency_scores) == 2
    assert "method_1" in efficiency_scores
    assert "method_2" in efficiency_scores
    
    # Verify the structure of a labor efficiency score
    score = efficiency_scores["method_1"]
    assert isinstance(score, LaborEfficiencyScore)
    assert score.method_id == "method_1"
    assert 0 <= score.overall_efficiency <= 1
    assert 0 <= score.productivity_rate
    assert 0 <= score.quality_score <= 1
    assert 0 <= score.safety_score <= 1
    assert 0 <= score.equipment_utilization <= 1
    assert 0 <= score.skill_alignment_score <= 1
    assert 0 <= score.training_requirement_score <= 1


@pytest.mark.asyncio
async def test_perform_labor_optimization(
    advanced_labor_service,
    sample_application_methods,
    sample_field_conditions,
    sample_crop_requirements,
    sample_fertilizer_specification,
    sample_equipment_specifications
):
    """Test comprehensive labor optimization analysis."""
    result = await advanced_labor_service.perform_labor_optimization(
        sample_application_methods,
        sample_field_conditions,
        sample_crop_requirements,
        sample_fertilizer_specification,
        sample_equipment_specifications
    )
    
    # Verify the structure of the optimization result
    assert isinstance(result, LaborOptimizationResult)
    assert result.optimization_time_ms > 0
    assert len(result.efficiency_metrics) == 2
    assert len(result.cost_per_unit_metrics) == 2
    assert "total_labor_hours" in result.labor_requirements_summary
    assert "overall_risk_level" in result.risk_assessment
    assert isinstance(result.recommended_labor_plan, dict)
    assert "recommended_method" in result.recommended_labor_plan
    assert "method_rankings" in result.recommended_labor_plan


@pytest.mark.asyncio
async def test_calculate_labor_roi(
    advanced_labor_service,
    sample_application_methods,
    sample_field_conditions,
    sample_crop_requirements,
    sample_fertilizer_specification,
    sample_equipment_specifications
):
    """Test labor ROI calculation."""
    labor_roi = await advanced_labor_service.calculate_labor_roi(
        sample_application_methods,
        sample_field_conditions,
        sample_crop_requirements,
        sample_fertilizer_specification,
        sample_equipment_specifications
    )
    
    # Verify we get ROI for each method
    assert len(labor_roi) == 2
    assert "method_1" in labor_roi
    assert "method_2" in labor_roi
    
    # Verify the structure of ROI data
    roi_data = labor_roi["method_1"]
    assert "labor_cost" in roi_data
    assert "estimated_revenue" in roi_data
    assert "roi" in roi_data
    assert "roi_percentage" in roi_data


@pytest.mark.asyncio
async def test_calculate_productivity_rate(
    advanced_labor_service,
    sample_application_methods,
    sample_field_conditions,
    sample_equipment_specifications
):
    """Test productivity rate calculation."""
    # Test with broadcast method
    method = sample_application_methods[0]
    productivity_rate = await advanced_labor_service._calculate_productivity_rate(
        method, sample_field_conditions, sample_equipment_specifications
    )
    
    assert isinstance(productivity_rate, float)
    assert productivity_rate > 0
    assert productivity_rate <= 100.0  # Capped at 100 acres per hour


@pytest.mark.asyncio
async def test_calculate_quality_score(
    advanced_labor_service,
    sample_application_methods,
    sample_equipment_specifications
):
    """Test quality score calculation."""
    method = sample_application_methods[0]
    quality_score = await advanced_labor_service._calculate_quality_score(
        method, sample_equipment_specifications
    )
    
    assert isinstance(quality_score, float)
    assert 0 <= quality_score <= 1


@pytest.mark.asyncio
async def test_calculate_safety_score(
    advanced_labor_service,
    sample_application_methods
):
    """Test safety score calculation."""
    method = sample_application_methods[0]
    safety_score = await advanced_labor_service._calculate_safety_score(method)
    
    assert isinstance(safety_score, float)
    assert 0 <= safety_score <= 1


@pytest.mark.asyncio
async def test_find_compatible_equipment(
    advanced_labor_service,
    sample_equipment_specifications
):
    """Test finding compatible equipment."""
    compatible = advanced_labor_service._find_compatible_equipment(
        "spreader",
        sample_equipment_specifications
    )
    
    assert compatible is not None
    assert compatible.equipment_type == EquipmentType.SPREADER


@pytest.mark.asyncio
async def test_perform_labor_optimization_with_seasonal_constraint(
    advanced_labor_service,
    sample_application_methods,
    sample_field_conditions,
    sample_crop_requirements,
    sample_fertilizer_specification,
    sample_equipment_specifications
):
    """Test labor optimization with seasonal constraint."""
    from src.services.cost_analysis_service import SeasonalConstraint
    
    result = await advanced_labor_service.perform_labor_optimization(
        sample_application_methods,
        sample_field_conditions,
        sample_crop_requirements,
        sample_fertilizer_specification,
        sample_equipment_specifications,
        seasonal_constraint=SeasonalConstraint.SPRING_PEAK
    )
    
    # Verify the result structure is the same as without constraint
    assert isinstance(result, LaborOptimizationResult)
    assert result.optimization_time_ms > 0


@pytest.mark.asyncio
async def test_calculate_labor_sensitivity_analysis(
    advanced_labor_service,
    sample_application_methods,
    sample_field_conditions,
    sample_crop_requirements,
    sample_fertilizer_specification,
    sample_equipment_specifications
):
    """Test labor sensitivity analysis."""
    sensitivity_analysis = await advanced_labor_service.calculate_labor_sensitivity_analysis(
        sample_application_methods,
        sample_field_conditions,
        sample_crop_requirements,
        sample_fertilizer_specification,
        sample_equipment_specifications
    )
    
    assert "sensitivity_analysis" in sensitivity_analysis
    assert "summary" in sensitivity_analysis
    assert sensitivity_analysis["summary"]["methods_analyzed"] == 2
    assert sensitivity_analysis["summary"]["scenarios_tested"] == 5


@pytest.mark.asyncio
async def test_create_recommended_labor_plan(
    advanced_labor_service,
    sample_application_methods,
    sample_field_conditions,
    sample_crop_requirements,
    sample_fertilizer_specification,
    sample_equipment_specifications
):
    """Test creating recommended labor plan."""
    # First, get efficiency scores and cost analysis
    efficiency_scores = await advanced_labor_service.analyze_labor_efficiency(
        sample_application_methods,
        sample_field_conditions,
        sample_crop_requirements,
        sample_equipment_specifications
    )
    
    # Use the cost analysis service to get cost data
    cost_analysis = await advanced_labor_service.cost_analysis_service.analyze_application_costs(
        sample_application_methods,
        sample_field_conditions,
        sample_crop_requirements,
        sample_fertilizer_specification,
        sample_equipment_specifications
    )
    
    # Create recommended plan
    recommended_plan = await advanced_labor_service._create_recommended_labor_plan(
        sample_application_methods,
        efficiency_scores,
        cost_analysis
    )
    
    assert "recommended_method" in recommended_plan
    assert "method_rankings" in recommended_plan
    assert "labor_allocation_recommendations" in recommended_plan
    assert len(recommended_plan["method_rankings"]) == 2


@pytest.mark.asyncio
async def test_calculate_labor_requirements_summary(
    advanced_labor_service,
    sample_field_conditions,
    sample_crop_requirements,
    sample_fertilizer_specification,
    sample_equipment_specifications
):
    """Test calculating labor requirements summary."""
    # First, get cost analysis
    cost_analysis = await advanced_labor_service.cost_analysis_service.analyze_application_costs(
        [sample_application_methods[0]],
        sample_field_conditions,
        sample_crop_requirements,
        sample_fertilizer_specification,
        sample_equipment_specifications
    )
    
    # Calculate labor requirements summary
    labor_summary = await advanced_labor_service._calculate_labor_requirements_summary(
        cost_analysis,
        sample_field_conditions
    )
    
    assert "total_labor_hours" in labor_summary
    assert "total_labor_cost" in labor_summary
    assert "avg_labor_cost_per_acre" in labor_summary
    assert "labor_intensity" in labor_summary


@pytest.mark.asyncio
async def test_perform_labor_risk_assessment(
    advanced_labor_service,
    sample_application_methods
):
    """Test performing labor risk assessment."""
    # Create sample efficiency scores for testing
    efficiency_scores = {}
    for method in sample_application_methods:
        efficiency_scores[method.method_id] = LaborEfficiencyScore(
            method_id=method.method_id,
            productivity_rate=50.0,
            quality_score=0.8,
            safety_score=0.85,
            equipment_utilization=0.75,
            overall_efficiency=0.8,
            skill_alignment_score=0.7,
            training_requirement_score=0.8
        )
    
    # Calculate labor requirements summary for testing
    labor_summary = {
        "total_labor_hours": 80.0,
        "total_labor_cost": 1200.0,
        "avg_labor_cost_per_acre": 12.0,
        "labor_intensity": 0.8
    }
    
    risk_assessment = await advanced_labor_service._perform_labor_risk_assessment(
        efficiency_scores,
        labor_summary
    )
    
    assert "overall_risk_level" in risk_assessment
    assert "high_risk_methods" in risk_assessment
    assert "avg_efficiency_score" in risk_assessment
    assert "avg_safety_score" in risk_assessment
    assert "risk_mitigation_recommendations" in risk_assessment


@pytest.mark.asyncio
async def test_generate_risk_mitigation_recommendations(
    advanced_labor_service
):
    """Test generating risk mitigation recommendations."""
    recommendations = advanced_labor_service._generate_risk_mitigation_recommendations(
        "medium",
        ["method_1"]
    )
    
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
    assert isinstance(recommendations[0], str)