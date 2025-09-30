"""
Comprehensive test suite for the enhanced Cost Analysis Service.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from typing import List, Dict, Any

from src.services.cost_analysis_service import (
    CostAnalysisService, 
    LaborSkillLevel, 
    SeasonalConstraint, 
    EconomicScenario
)
from src.models.application_models import (
    ApplicationMethod, 
    FieldConditions, 
    CropRequirements, 
    FertilizerSpecification,
    EquipmentSpecification,
    ApplicationMethodType,
    FertilizerForm,
    EquipmentType
)


class TestCostAnalysisService:
    """Test suite for CostAnalysisService."""

    @pytest.fixture
    def cost_service(self):
        """Create CostAnalysisService instance for testing."""
        return CostAnalysisService()

    @pytest.fixture
    def sample_field_conditions(self):
        """Create sample field conditions for testing."""
        return FieldConditions(
            field_size_acres=100.0,
            soil_type="clay_loam",
            drainage_class="moderate",
            slope_percent=5.0,
            irrigation_available=True,
            field_shape="rectangular"
        )

    @pytest.fixture
    def sample_crop_requirements(self):
        """Create sample crop requirements for testing."""
        return CropRequirements(
            crop_type="corn",
            growth_stage="V6",
            target_yield=180.0,
            nutrient_requirements={"N": 150, "P": 60, "K": 120},
            application_timing_preferences=["spring", "early_season"]
        )

    @pytest.fixture
    def sample_fertilizer_specification(self):
        """Create sample fertilizer specification for testing."""
        return FertilizerSpecification(
            fertilizer_type="nitrogen",
            npk_ratio="32-0-0",
            form=FertilizerForm.LIQUID,
            solubility=95.0,
            release_rate="immediate",
            cost_per_unit=0.80,
            unit="lb"
        )

    @pytest.fixture
    def sample_equipment_specifications(self):
        """Create sample equipment specifications for testing."""
        return [
            EquipmentSpecification(
                equipment_type=EquipmentType.SPREADER,
                capacity=2000.0,
                capacity_unit="lbs",
                application_width=30.0,
                application_rate_range={"min": 50, "max": 300},
                fuel_efficiency=0.8,
                maintenance_cost_per_hour=5.0
            ),
            EquipmentSpecification(
                equipment_type=EquipmentType.SPRAYER,
                capacity=500.0,
                capacity_unit="gallons",
                application_width=40.0,
                application_rate_range={"min": 10, "max": 50},
                fuel_efficiency=0.7,
                maintenance_cost_per_hour=7.0
            )
        ]

    @pytest.fixture
    def sample_application_methods(self):
        """Create sample application methods for testing."""
        return [
            ApplicationMethod(
                method_id="method_1",
                method_type=ApplicationMethodType.BROADCAST,
                recommended_equipment=EquipmentSpecification(
                    equipment_type=EquipmentType.SPREADER,
                    capacity=2000.0,
                    capacity_unit="lbs"
                ),
                application_rate=150.0,
                rate_unit="lbs/acre",
                application_timing="spring",
                efficiency_score=0.7,
                cost_per_acre=25.0,
                labor_requirements="moderate",
                environmental_impact="low",
                pros=["Simple operation", "Wide coverage"],
                cons=["Lower efficiency", "Weather dependent"]
            ),
            ApplicationMethod(
                method_id="method_2",
                method_type=ApplicationMethodType.BAND,
                recommended_equipment=EquipmentSpecification(
                    equipment_type=EquipmentType.SPREADER,
                    capacity=2000.0,
                    capacity_unit="lbs"
                ),
                application_rate=120.0,
                rate_unit="lbs/acre",
                application_timing="spring",
                efficiency_score=0.85,
                cost_per_acre=30.0,
                labor_requirements="moderate",
                environmental_impact="medium",
                pros=["Higher efficiency", "Reduced fertilizer use"],
                cons=["More complex setup", "Requires precision"]
            )
        ]

    @pytest.mark.asyncio
    async def test_analyze_application_costs_basic(self, cost_service, sample_application_methods, 
                                                  sample_field_conditions, sample_crop_requirements,
                                                  sample_fertilizer_specification, sample_equipment_specifications):
        """Test basic application cost analysis."""
        
        result = await cost_service.analyze_application_costs(
            sample_application_methods,
            sample_field_conditions,
            sample_crop_requirements,
            sample_fertilizer_specification,
            sample_equipment_specifications
        )
        
        assert "method_costs" in result
        assert "comparative_analysis" in result
        assert "optimization_recommendations" in result
        assert "roi_analysis" in result
        assert "sensitivity_analysis" in result
        assert "processing_time_ms" in result
        
        # Verify method costs structure
        assert len(result["method_costs"]) == 2
        for method_cost in result["method_costs"]:
            assert "method_id" in method_cost
            assert "method_type" in method_cost
            assert "fertilizer_costs" in method_cost
            assert "equipment_costs" in method_cost
            assert "labor_costs" in method_cost
            assert "fuel_costs" in method_cost
            assert "maintenance_costs" in method_cost
            assert "total_costs" in method_cost
            assert "cost_per_acre" in method_cost
            assert "cost_per_field" in method_cost

    @pytest.mark.asyncio
    async def test_analyze_comprehensive_labor_requirements(self, cost_service, sample_application_methods,
                                                          sample_field_conditions, sample_crop_requirements):
        """Test comprehensive labor requirements analysis."""
        
        result = await cost_service.analyze_comprehensive_labor_requirements(
            sample_application_methods,
            sample_field_conditions,
            sample_crop_requirements,
            SeasonalConstraint.SPRING_PEAK
        )
        
        assert "method_labor_analyses" in result
        assert "comparative_labor_analysis" in result
        assert "labor_optimization_recommendations" in result
        assert "labor_cost_sensitivity" in result
        assert "processing_time_ms" in result
        
        # Verify labor analysis structure
        assert len(result["method_labor_analyses"]) == 2
        for labor_analysis in result["method_labor_analyses"]:
            assert "method_type" in labor_analysis
            assert "skill_level" in labor_analysis
            assert "labor_rate" in labor_analysis
            assert "base_labor_hours" in labor_analysis
            assert "availability_factor" in labor_analysis
            assert "adjusted_labor_hours" in labor_analysis
            assert "total_labor_cost" in labor_analysis
            assert "labor_cost_per_acre" in labor_analysis
            assert "labor_intensity_score" in labor_analysis
            assert "skill_requirements" in labor_analysis
            assert "training_requirements" in labor_analysis

    @pytest.mark.asyncio
    async def test_perform_economic_scenario_analysis(self, cost_service, sample_application_methods,
                                                     sample_field_conditions, sample_crop_requirements,
                                                     sample_fertilizer_specification, sample_equipment_specifications):
        """Test economic scenario analysis."""
        
        scenarios = [EconomicScenario.OPTIMISTIC, EconomicScenario.REALISTIC, EconomicScenario.PESSIMISTIC]
        
        result = await cost_service.perform_economic_scenario_analysis(
            sample_application_methods,
            sample_field_conditions,
            sample_crop_requirements,
            sample_fertilizer_specification,
            sample_equipment_specifications,
            scenarios
        )
        
        assert "scenario_results" in result
        assert "cross_scenario_analysis" in result
        assert "risk_assessment" in result
        assert "processing_time_ms" in result
        
        # Verify scenario results
        assert len(result["scenario_results"]) == 3
        for scenario_name in ["optimistic", "realistic", "pessimistic"]:
            assert scenario_name in result["scenario_results"]
            scenario_result = result["scenario_results"][scenario_name]
            assert "method_costs" in scenario_result
            assert "scenario" in scenario_result
            assert "scenario_multipliers" in scenario_result

    @pytest.mark.asyncio
    async def test_calculate_break_even_analysis(self, cost_service, sample_application_methods,
                                                sample_field_conditions, sample_crop_requirements,
                                                sample_fertilizer_specification, sample_equipment_specifications):
        """Test break-even analysis calculation."""
        
        result = await cost_service.calculate_break_even_analysis(
            sample_application_methods,
            sample_field_conditions,
            sample_crop_requirements,
            sample_fertilizer_specification,
            sample_equipment_specifications,
            crop_price_per_unit=5.0,
            yield_units="bushels"
        )
        
        assert "break_even_results" in result
        assert "comparative_break_even_analysis" in result
        assert "optimization_recommendations" in result
        assert "processing_time_ms" in result
        
        # Verify break-even results structure
        assert len(result["break_even_results"]) == 2
        for method_type, break_even_result in result["break_even_results"].items():
            assert "break_even_yield" in break_even_result
            assert "break_even_price" in break_even_result
            assert "target_yield" in break_even_result
            assert "crop_price_per_unit" in break_even_result
            assert "total_cost_per_acre" in break_even_result
            assert "profit_scenarios" in break_even_result
            assert "risk_level" in break_even_result

    @pytest.mark.asyncio
    async def test_calculate_opportunity_cost_analysis(self, cost_service, sample_application_methods,
                                                       sample_field_conditions, sample_crop_requirements,
                                                       sample_fertilizer_specification, sample_equipment_specifications):
        """Test opportunity cost analysis calculation."""
        
        alternative_uses = [
            {"type": "land_rental", "revenue_per_acre": 150.0},
            {"type": "alternative_crop", "revenue_per_acre": 800.0},
            {"type": "equipment_rental", "revenue_per_hour": 25.0}
        ]
        
        result = await cost_service.calculate_opportunity_cost_analysis(
            sample_application_methods,
            sample_field_conditions,
            sample_crop_requirements,
            sample_fertilizer_specification,
            sample_equipment_specifications,
            alternative_uses
        )
        
        assert "opportunity_cost_results" in result
        assert "comparative_opportunity_cost_analysis" in result
        assert "optimization_recommendations" in result
        assert "processing_time_ms" in result
        
        # Verify opportunity cost results structure
        assert len(result["opportunity_cost_results"]) == 2
        for method_type, opportunity_result in result["opportunity_cost_results"].items():
            assert "land_opportunity_cost" in opportunity_result
            assert "equipment_opportunity_cost" in opportunity_result
            assert "labor_opportunity_cost" in opportunity_result
            assert "total_opportunity_cost" in opportunity_result
            assert "total_cost_with_opportunity" in opportunity_result
            assert "opportunity_cost_per_acre" in opportunity_result
            assert "economic_profit" in opportunity_result

    def test_cost_database_initialization(self, cost_service):
        """Test cost database initialization."""
        
        assert "labor_rates" in cost_service.cost_database
        assert "fuel_costs" in cost_service.cost_database
        assert "equipment_costs" in cost_service.cost_database
        assert "fertilizer_costs" in cost_service.cost_database
        assert "application_efficiency" in cost_service.cost_database
        assert "economic_scenarios" in cost_service.cost_database
        assert "risk_factors" in cost_service.cost_database
        
        # Verify labor rates
        labor_rates = cost_service.cost_database["labor_rates"]
        assert "unskilled" in labor_rates
        assert "semi_skilled" in labor_rates
        assert "skilled" in labor_rates
        assert "highly_skilled" in labor_rates
        
        # Verify economic scenarios
        scenarios = cost_service.cost_database["economic_scenarios"]
        assert "optimistic" in scenarios
        assert "realistic" in scenarios
        assert "pessimistic" in scenarios
        assert "crisis" in scenarios

    def test_labor_skill_level_enum(self):
        """Test LaborSkillLevel enum values."""
        assert LaborSkillLevel.UNSKILLED == "unskilled"
        assert LaborSkillLevel.SEMI_SKILLED == "semi_skilled"
        assert LaborSkillLevel.SKILLED == "skilled"
        assert LaborSkillLevel.HIGHLY_SKILLED == "highly_skilled"

    def test_seasonal_constraint_enum(self):
        """Test SeasonalConstraint enum values."""
        assert SeasonalConstraint.SPRING_PEAK == "spring_peak"
        assert SeasonalConstraint.SUMMER_PEAK == "summer_peak"
        assert SeasonalConstraint.FALL_PEAK == "fall_peak"
        assert SeasonalConstraint.WINTER_LOW == "winter_low"
        assert SeasonalConstraint.YEAR_ROUND == "year_round"

    def test_economic_scenario_enum(self):
        """Test EconomicScenario enum values."""
        assert EconomicScenario.OPTIMISTIC == "optimistic"
        assert EconomicScenario.REALISTIC == "realistic"
        assert EconomicScenario.PESSIMISTIC == "pessimistic"
        assert EconomicScenario.CRISIS == "crisis"

    @pytest.mark.asyncio
    async def test_error_handling(self, cost_service):
        """Test error handling in cost analysis."""
        
        # Test with empty application methods
        with pytest.raises(Exception):
            await cost_service.analyze_application_costs(
                [],  # Empty methods
                FieldConditions(field_size_acres=100.0, soil_type="clay"),
                CropRequirements(crop_type="corn", growth_stage="V6"),
                FertilizerSpecification(fertilizer_type="nitrogen", npk_ratio="32-0-0", form=FertilizerForm.LIQUID),
                []
            )

    @pytest.mark.asyncio
    async def test_cost_calculation_accuracy(self, cost_service, sample_application_methods,
                                            sample_field_conditions, sample_crop_requirements,
                                            sample_fertilizer_specification, sample_equipment_specifications):
        """Test cost calculation accuracy."""
        
        result = await cost_service.analyze_application_costs(
            sample_application_methods,
            sample_field_conditions,
            sample_crop_requirements,
            sample_fertilizer_specification,
            sample_equipment_specifications
        )
        
        # Verify cost calculations are reasonable
        for method_cost in result["method_costs"]:
            assert method_cost["cost_per_acre"] > 0
            assert method_cost["cost_per_field"] > 0
            
            # Verify cost breakdown adds up
            total_costs = method_cost["total_costs"]
            calculated_total = (
                total_costs["fertilizer"] +
                total_costs["equipment"] +
                total_costs["labor"] +
                total_costs["fuel"] +
                total_costs["maintenance"]
            )
            assert abs(method_cost["cost_per_field"] - calculated_total) < 0.01

    @pytest.mark.asyncio
    async def test_labor_analysis_accuracy(self, cost_service, sample_application_methods,
                                          sample_field_conditions, sample_crop_requirements):
        """Test labor analysis accuracy."""
        
        result = await cost_service.analyze_comprehensive_labor_requirements(
            sample_application_methods,
            sample_field_conditions,
            sample_crop_requirements,
            SeasonalConstraint.SPRING_PEAK
        )
        
        # Verify labor calculations are reasonable
        for labor_analysis in result["method_labor_analyses"]:
            assert labor_analysis["labor_rate"] > 0
            assert labor_analysis["base_labor_hours"] > 0
            assert labor_analysis["adjusted_labor_hours"] > 0
            assert labor_analysis["total_labor_cost"] > 0
            assert labor_analysis["labor_cost_per_acre"] > 0
            assert 0 <= labor_analysis["labor_intensity_score"] <= 1

    @pytest.mark.asyncio
    async def test_scenario_analysis_consistency(self, cost_service, sample_application_methods,
                                                 sample_field_conditions, sample_crop_requirements,
                                                 sample_fertilizer_specification, sample_equipment_specifications):
        """Test scenario analysis consistency."""
        
        scenarios = [EconomicScenario.OPTIMISTIC, EconomicScenario.REALISTIC, EconomicScenario.PESSIMISTIC]
        
        result = await cost_service.perform_economic_scenario_analysis(
            sample_application_methods,
            sample_field_conditions,
            sample_crop_requirements,
            sample_fertilizer_specification,
            sample_equipment_specifications,
            scenarios
        )
        
        # Verify scenario costs follow expected pattern
        scenario_costs = result["cross_scenario_analysis"]["scenario_costs"]
        assert scenario_costs["optimistic"] < scenario_costs["realistic"]
        assert scenario_costs["realistic"] < scenario_costs["pessimistic"]

    @pytest.mark.asyncio
    async def test_break_even_analysis_logic(self, cost_service, sample_application_methods,
                                            sample_field_conditions, sample_crop_requirements,
                                            sample_fertilizer_specification, sample_equipment_specifications):
        """Test break-even analysis logic."""
        
        result = await cost_service.calculate_break_even_analysis(
            sample_application_methods,
            sample_field_conditions,
            sample_crop_requirements,
            sample_fertilizer_specification,
            sample_equipment_specifications,
            crop_price_per_unit=5.0
        )
        
        # Verify break-even calculations
        for method_type, break_even_result in result["break_even_results"].items():
            cost_per_acre = break_even_result["total_cost_per_acre"]
            break_even_yield = break_even_result["break_even_yield"]
            crop_price = break_even_result["crop_price_per_unit"]
            
            # Verify break-even yield calculation
            expected_break_even = cost_per_acre / crop_price
            assert abs(break_even_result["break_even_yield"] - expected_break_even) < 0.01

    @pytest.mark.asyncio
    async def test_opportunity_cost_calculation(self, cost_service, sample_application_methods,
                                               sample_field_conditions, sample_crop_requirements,
                                               sample_fertilizer_specification, sample_equipment_specifications):
        """Test opportunity cost calculation."""
        
        result = await cost_service.calculate_opportunity_cost_analysis(
            sample_application_methods,
            sample_field_conditions,
            sample_crop_requirements,
            sample_fertilizer_specification,
            sample_equipment_specifications
        )
        
        # Verify opportunity cost calculations
        for method_type, opportunity_result in result["opportunity_cost_results"].items():
            assert opportunity_result["land_opportunity_cost"] > 0
            assert opportunity_result["equipment_opportunity_cost"] >= 0
            assert opportunity_result["labor_opportunity_cost"] >= 0
            assert opportunity_result["total_opportunity_cost"] > 0
            
            # Verify economic profit calculation
            economic_profit = opportunity_result["economic_profit"]
            assert "estimated_revenue" in economic_profit
            assert "total_economic_cost" in economic_profit
            assert "economic_profit" in economic_profit
            assert "economic_profit_per_acre" in economic_profit
            assert "economic_profit_margin" in economic_profit

    @pytest.mark.asyncio
    async def test_performance_requirements(self, cost_service, sample_application_methods,
                                           sample_field_conditions, sample_crop_requirements,
                                           sample_fertilizer_specification, sample_equipment_specifications):
        """Test performance requirements (< 3 seconds)."""
        
        import time
        start_time = time.time()
        
        result = await cost_service.analyze_application_costs(
            sample_application_methods,
            sample_field_conditions,
            sample_crop_requirements,
            sample_fertilizer_specification,
            sample_equipment_specifications
        )
        
        elapsed_time = time.time() - start_time
        assert elapsed_time < 3.0, f"Analysis took {elapsed_time:.2f} seconds, exceeds 3 second requirement"
        assert result["processing_time_ms"] < 3000, f"Processing time {result['processing_time_ms']:.2f}ms exceeds 3000ms requirement"

    def test_helper_methods(self, cost_service):
        """Test helper methods."""
        
        # Test labor intensity score calculation
        assert cost_service._calculate_labor_intensity_score("broadcast") == 0.3
        assert cost_service._calculate_labor_intensity_score("foliar") == 0.9
        assert cost_service._calculate_labor_intensity_score("unknown") == 0.5
        
        # Test skill requirements
        skill_reqs = cost_service._get_skill_requirements("skilled")
        assert isinstance(skill_reqs, list)
        assert len(skill_reqs) > 0
        
        # Test training requirements
        training_reqs = cost_service._get_training_requirements("highly_skilled")
        assert isinstance(training_reqs, list)
        assert len(training_reqs) > 0
        
        # Test risk level assessment
        assert cost_service._assess_risk_level(0.1) == "low"
        assert cost_service._assess_risk_level(0.2) == "medium"
        assert cost_service._assess_risk_level(0.4) == "high"


class TestCostAnalysisServiceIntegration:
    """Integration tests for CostAnalysisService."""

    @pytest.fixture
    def cost_service(self):
        """Create CostAnalysisService instance for integration testing."""
        return CostAnalysisService()

    @pytest.mark.asyncio
    async def test_full_workflow_integration(self, cost_service):
        """Test full workflow integration."""
        
        # Create comprehensive test data
        field_conditions = FieldConditions(
            field_size_acres=200.0,
            soil_type="sandy_loam",
            drainage_class="well",
            slope_percent=3.0,
            irrigation_available=True,
            field_shape="rectangular"
        )
        
        crop_requirements = CropRequirements(
            crop_type="soybean",
            growth_stage="R1",
            target_yield=50.0,
            nutrient_requirements={"N": 0, "P": 40, "K": 80},
            application_timing_preferences=["spring", "pre_plant"]
        )
        
        fertilizer_specification = FertilizerSpecification(
            fertilizer_type="phosphorus",
            npk_ratio="0-46-0",
            form=FertilizerForm.GRANULAR,
            solubility=85.0,
            release_rate="immediate",
            cost_per_unit=0.60,
            unit="lb"
        )
        
        equipment_specifications = [
            EquipmentSpecification(
                equipment_type=EquipmentType.SPREADER,
                capacity=3000.0,
                capacity_unit="lbs",
                application_width=40.0,
                application_rate_range={"min": 100, "max": 400},
                fuel_efficiency=0.75,
                maintenance_cost_per_hour=6.0
            )
        ]
        
        application_methods = [
            ApplicationMethod(
                method_id="soybean_method_1",
                method_type=ApplicationMethodType.BROADCAST,
                recommended_equipment=equipment_specifications[0],
                application_rate=80.0,
                rate_unit="lbs/acre",
                application_timing="spring",
                efficiency_score=0.75,
                cost_per_acre=20.0,
                labor_requirements="low",
                environmental_impact="low",
                pros=["Simple", "Fast"],
                cons=["Lower efficiency"]
            )
        ]
        
        # Test comprehensive cost analysis
        cost_result = await cost_service.analyze_application_costs(
            application_methods,
            field_conditions,
            crop_requirements,
            fertilizer_specification,
            equipment_specifications
        )
        
        # Test labor analysis
        labor_result = await cost_service.analyze_comprehensive_labor_requirements(
            application_methods,
            field_conditions,
            crop_requirements,
            SeasonalConstraint.SPRING_PEAK
        )
        
        # Test economic scenario analysis
        scenario_result = await cost_service.perform_economic_scenario_analysis(
            application_methods,
            field_conditions,
            crop_requirements,
            fertilizer_specification,
            equipment_specifications,
            [EconomicScenario.REALISTIC, EconomicScenario.PESSIMISTIC]
        )
        
        # Test break-even analysis
        break_even_result = await cost_service.calculate_break_even_analysis(
            application_methods,
            field_conditions,
            crop_requirements,
            fertilizer_specification,
            equipment_specifications,
            crop_price_per_unit=12.0,
            yield_units="bushels"
        )
        
        # Test opportunity cost analysis
        opportunity_result = await cost_service.calculate_opportunity_cost_analysis(
            application_methods,
            field_conditions,
            crop_requirements,
            fertilizer_specification,
            equipment_specifications
        )
        
        # Verify all analyses completed successfully
        assert cost_result["processing_time_ms"] > 0
        assert labor_result["processing_time_ms"] > 0
        assert scenario_result["processing_time_ms"] > 0
        assert break_even_result["processing_time_ms"] > 0
        assert opportunity_result["processing_time_ms"] > 0
        
        # Verify data consistency across analyses
        assert len(cost_result["method_costs"]) == 1
        assert len(labor_result["method_labor_analyses"]) == 1
        assert len(scenario_result["scenario_results"]) == 2
        assert len(break_even_result["break_even_results"]) == 1
        assert len(opportunity_result["opportunity_cost_results"]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
