"""
Comprehensive tests for break-even analysis service.

This module provides extensive testing for the advanced break-even analysis
including Monte Carlo simulation, scenario analysis, and sensitivity analysis.
"""

import pytest
import asyncio
import numpy as np
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Dict, List, Any

from ..services.break_even_analysis_service import (
    BreakEvenAnalysisService,
    CostStructure,
    PriceDistribution,
    ScenarioType,
    RiskLevel
)
from ..models.break_even_models import (
    BreakEvenAnalysisRequest,
    ComprehensiveBreakEvenAnalysis,
    BreakEvenSummary
)
from ..models.roi_models import (
    ROIOptimizationRequest,
    FieldData,
    FertilizerProduct,
    OptimizationMethod,
    OptimizationResult
)


@pytest.fixture
def service():
    """Create break-even analysis service instance."""
    return BreakEvenAnalysisService()

@pytest.fixture
def sample_field_data():
    """Sample field data for testing."""
    return FieldData(
        field_id="test_field_1",
        acres=100.0,
        soil_tests={
            "ph": 6.5,
            "organic_matter_percent": 3.2,
            "nitrogen": 120,
            "phosphorus": 25,
            "potassium": 150
        },
        crop_plan={
            "crop_type": "corn",
            "planting_date": "2024-04-15",
            "harvest_date": "2024-10-15",
            "variety": "test_corn_variety"
        },
        historical_yield=175.0,
        target_yield=180.0,
        crop_price=4.50
    )

@pytest.fixture
def sample_fertilizer_product():
    """Sample fertilizer product for testing."""
    return FertilizerProduct(
        product_id="test_product_1",
        product_name="Test Urea",
        nutrient_content={"N": 46.0, "P": 0.0, "K": 0.0},
        price_per_unit=0.45,
        unit="lb",
        application_method="broadcast",
        availability=True
    )

@pytest.fixture
def sample_roi_request(sample_field_data, sample_fertilizer_product):
    """Sample ROI optimization request."""
    from ..models.roi_models import OptimizationConstraints, OptimizationGoals
    
    return ROIOptimizationRequest(
        farm_context={"farm_id": "test_farm"},
        fields=[sample_field_data],
        fertilizer_products=[sample_fertilizer_product],
        constraints=OptimizationConstraints(),
        goals=OptimizationGoals(),
        optimization_method=OptimizationMethod.LINEAR_PROGRAMMING,
        include_sensitivity_analysis=True,
        include_risk_assessment=True
    )

@pytest.fixture
def mock_optimization_result():
    """Mock optimization result."""
    return OptimizationResult(
        optimization_id="test_opt_1",
        total_expected_revenue=81000.0,  # 100 acres * 180 bu/acre * $4.50/bu
        total_fertilizer_cost=15000.0,
        net_profit=66000.0,
        roi_percentage=440.0,
        break_even_yield=33.33,  # 15000 / (100 * 4.50)
        marginal_return_rate=440.0,
        risk_adjusted_return=396.0,
        nutrient_recommendations=[],
        optimization_metadata={"method": "linear_programming"}
    )


class TestCostStructureCalculation:
    """Test cost structure calculations."""
    
    @pytest.mark.asyncio
    async def test_calculate_detailed_cost_structure(self, service, sample_roi_request, mock_optimization_result):
        """Test detailed cost structure calculation."""
        cost_structure = await service._calculate_detailed_cost_structure(sample_roi_request, mock_optimization_result)
        
        # Validate cost structure
        assert isinstance(cost_structure, CostStructure)
        assert cost_structure.fixed_costs > 0
        assert cost_structure.variable_costs > 0
        assert cost_structure.fertilizer_costs == 15000.0
        assert cost_structure.application_costs > 0
        assert cost_structure.opportunity_costs > 0
        assert cost_structure.total_costs > 0
        
        # Validate total costs calculation
        expected_total = (cost_structure.fixed_costs + cost_structure.variable_costs + 
                         cost_structure.fertilizer_costs + cost_structure.application_costs + 
                         cost_structure.opportunity_costs)
        assert abs(cost_structure.total_costs - expected_total) < 0.01
    
    @pytest.mark.asyncio
    async def test_cost_structure_with_multiple_fields(self, service):
        """Test cost structure with multiple fields."""
        fields = [
            FieldData(
                field_id="field_1",
                acres=50.0,
                soil_type="sandy_loam",
                current_ph=6.0,
                organic_matter_percent=2.5,
                target_yield=160.0,
                crop_price=4.25,
                previous_crop="soybean",
                tillage_system="conventional",
                irrigation_available=False
            ),
            FieldData(
                field_id="field_2",
                acres=75.0,
                soil_type="clay",
                current_ph=7.0,
                organic_matter_percent=4.0,
                target_yield=200.0,
                crop_price=4.75,
                previous_crop="corn",
                tillage_system="no_till",
                irrigation_available=True
            )
        ]
        
        request = ROIOptimizationRequest(
            fields=fields,
            products=[],
            optimization_method=OptimizationMethod.LINEAR_PROGRAMMING
        )
        
        mock_result = OptimizationResult(
            optimization_id="test",
            total_expected_revenue=100000.0,
            total_fertilizer_cost=20000.0,
            net_profit=80000.0,
            roi_percentage=400.0,
            break_even_yield=25.0,
            marginal_return_rate=400.0,
            risk_adjusted_return=360.0,
            nutrient_recommendations=[],
            optimization_metadata={}
        )
        
        cost_structure = await service._calculate_detailed_cost_structure(request, mock_result)
        
        # Validate total acres calculation
        total_acres = sum(field.acres for field in fields)
        assert total_acres == 125.0
        
        # Validate cost scaling with acres
        assert cost_structure.fixed_costs > 0
        assert cost_structure.variable_costs > 0
        assert cost_structure.total_costs > 0


class TestBasicBreakEvenCalculation:
    """Test basic break-even calculations."""
    
    @pytest.mark.asyncio
    async def test_calculate_basic_break_even(self, service, sample_roi_request):
        """Test basic break-even calculation."""
        cost_structure = CostStructure(
            fixed_costs=15000.0,
            variable_costs=20000.0,
            fertilizer_costs=15000.0,
            application_costs=2500.0,
            opportunity_costs=10000.0,
            total_costs=62500.0
        )
        
        basic_analysis = await service._calculate_basic_break_even(sample_roi_request, cost_structure)
        
        # Validate break-even calculations
        assert basic_analysis["break_even_yield_per_acre"] > 0
        assert basic_analysis["break_even_price_per_unit"] > 0
        assert basic_analysis["break_even_fertilizer_cost_per_acre"] > 0
        assert basic_analysis["safety_margin_percentage"] is not None
        assert 0.0 <= basic_analysis["probability_of_profitability"] <= 1.0
        
        # Validate calculations
        total_acres = sum(field.acres for field in sample_roi_request.fields)
        crop_price = sample_roi_request.fields[0].crop_price
        
        expected_break_even_yield = cost_structure.total_costs / (total_acres * crop_price)
        assert abs(basic_analysis["break_even_yield_per_acre"] - expected_break_even_yield) < 0.01
    
    @pytest.mark.asyncio
    async def test_break_even_with_zero_crop_price(self, service):
        """Test break-even calculation with zero crop price."""
        field = FieldData(
            field_id="test_field",
            acres=100.0,
            soil_type="clay_loam",
            current_ph=6.5,
            organic_matter_percent=3.2,
            target_yield=180.0,
            crop_price=0.0,  # Zero crop price
            previous_crop="corn",
            tillage_system="no_till",
            irrigation_available=True
        )
        
        request = ROIOptimizationRequest(
            fields=[field],
            products=[],
            optimization_method=OptimizationMethod.LINEAR_PROGRAMMING
        )
        
        cost_structure = CostStructure(
            fixed_costs=10000.0,
            variable_costs=15000.0,
            fertilizer_costs=10000.0,
            application_costs=2000.0,
            opportunity_costs=5000.0,
            total_costs=42000.0
        )
        
        basic_analysis = await service._calculate_basic_break_even(request, cost_structure)
        
        # Should handle zero crop price gracefully
        assert basic_analysis["break_even_yield_per_acre"] == 0
        assert basic_analysis["break_even_price_per_unit"] > 0


class TestMonteCarloSimulation:
    """Test Monte Carlo simulation functionality."""
    
    @pytest.mark.asyncio
    async def test_monte_carlo_simulation(self, service, sample_roi_request):
        """Test Monte Carlo simulation."""
        cost_structure = CostStructure(
            fixed_costs=15000.0,
            variable_costs=20000.0,
            fertilizer_costs=15000.0,
            application_costs=2500.0,
            opportunity_costs=10000.0,
            total_costs=62500.0
        )
        
        # Run Monte Carlo simulation with fewer iterations for testing
        monte_carlo_result = await service._perform_monte_carlo_simulation(
            sample_roi_request, cost_structure, 1000
        )
        
        # Validate Monte Carlo results
        assert monte_carlo_result.iterations == 1000
        assert monte_carlo_result.simulation_id is not None
        assert "profitable" in monte_carlo_result.break_even_probabilities
        assert "break_even_yield_achievable" in monte_carlo_result.break_even_probabilities
        assert "safety_margin_adequate" in monte_carlo_result.break_even_probabilities
        
        # Validate probability values
        for prob in monte_carlo_result.break_even_probabilities.values():
            assert 0.0 <= prob <= 1.0
        
        # Validate confidence intervals
        assert "break_even_yield" in monte_carlo_result.confidence_intervals
        assert "break_even_price" in monte_carlo_result.confidence_intervals
        assert "profit" in monte_carlo_result.confidence_intervals
        assert "safety_margin" in monte_carlo_result.confidence_intervals
        
        # Validate risk metrics
        assert "value_at_risk_5pct" in monte_carlo_result.risk_metrics
        assert "expected_shortfall" in monte_carlo_result.risk_metrics
        assert "volatility" in monte_carlo_result.risk_metrics
        assert "sharpe_ratio" in monte_carlo_result.risk_metrics
        
        # Validate probability distributions
        assert "break_even_yields" in monte_carlo_result.probability_distributions
        assert "break_even_prices" in monte_carlo_result.probability_distributions
        assert "profits" in monte_carlo_result.probability_distributions
        assert "safety_margins" in monte_carlo_result.probability_distributions
        
        # Validate distribution lengths
        for dist_name, dist_values in monte_carlo_result.probability_distributions.items():
            assert len(dist_values) == 1000
    
    @pytest.mark.asyncio
    async def test_price_distribution_sampling(self, service):
        """Test price distribution sampling."""
        # Test normal distribution
        normal_dist = PriceDistribution(
            mean_price=100.0,
            std_deviation=10.0,
            min_price=50.0,
            max_price=150.0,
            distribution_type="normal"
        )
        
        samples = [service._sample_from_distribution(normal_dist) for _ in range(1000)]
        
        # Validate samples are within bounds
        for sample in samples:
            assert normal_dist.min_price <= sample <= normal_dist.max_price
        
        # Validate sample statistics (approximate)
        sample_mean = np.mean(samples)
        assert abs(sample_mean - normal_dist.mean_price) < 5.0  # Within 5 units
        
        # Test lognormal distribution
        lognormal_dist = PriceDistribution(
            mean_price=100.0,
            std_deviation=0.2,
            min_price=50.0,
            max_price=200.0,
            distribution_type="lognormal"
        )
        
        samples = [service._sample_from_distribution(lognormal_dist) for _ in range(1000)]
        
        # Validate samples are within bounds
        for sample in samples:
            assert lognormal_dist.min_price <= sample <= lognormal_dist.max_price
        
        # Test triangular distribution
        triangular_dist = PriceDistribution(
            mean_price=100.0,
            std_deviation=20.0,
            min_price=50.0,
            max_price=150.0,
            distribution_type="triangular"
        )
        
        samples = [service._sample_from_distribution(triangular_dist) for _ in range(1000)]
        
        # Validate samples are within bounds
        for sample in samples:
            assert triangular_dist.min_price <= sample <= triangular_dist.max_price


class TestScenarioAnalysis:
    """Test scenario analysis functionality."""
    
    @pytest.mark.asyncio
    async def test_scenario_analysis(self, service, sample_roi_request):
        """Test scenario analysis."""
        cost_structure = CostStructure(
            fixed_costs=15000.0,
            variable_costs=20000.0,
            fertilizer_costs=15000.0,
            application_costs=2500.0,
            opportunity_costs=10000.0,
            total_costs=62500.0
        )
        
        scenarios = await service._perform_scenario_analysis(sample_roi_request, cost_structure)
        
        # Validate scenarios
        assert len(scenarios) == 4  # Optimistic, Realistic, Pessimistic, Stress Test
        
        scenario_types = [s.scenario_type for s in scenarios]
        assert ScenarioType.OPTIMISTIC in scenario_types
        assert ScenarioType.REALISTIC in scenario_types
        assert ScenarioType.PESSIMISTIC in scenario_types
        assert ScenarioType.STRESS_TEST in scenario_types
        
        # Validate each scenario
        for scenario in scenarios:
            assert scenario.scenario_id is not None
            assert scenario.crop_price > 0
            assert scenario.expected_yield > 0
            assert scenario.break_even_yield > 0
            assert scenario.break_even_price > 0
            assert scenario.break_even_cost > 0
            assert 0.0 <= scenario.probability <= 1.0
            assert scenario.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
            assert scenario.safety_margin is not None
        
        # Validate scenario ordering (optimistic should have highest safety margin)
        optimistic_scenario = next(s for s in scenarios if s.scenario_type == ScenarioType.OPTIMISTIC)
        pessimistic_scenario = next(s for s in scenarios if s.scenario_type == ScenarioType.PESSIMISTIC)
        
        assert optimistic_scenario.safety_margin > pessimistic_scenario.safety_margin
    
    @pytest.mark.asyncio
    async def test_risk_level_determination(self, service):
        """Test risk level determination."""
        # Test different risk levels
        test_cases = [
            (50.0, 150.0, 180.0, RiskLevel.LOW),      # High safety margin, achievable yield
            (15.0, 180.0, 180.0, RiskLevel.MEDIUM),   # Medium safety margin, achievable yield
            (5.0, 200.0, 180.0, RiskLevel.HIGH),      # Low safety margin, high break-even yield
            (-5.0, 220.0, 180.0, RiskLevel.CRITICAL)  # Negative safety margin, very high break-even yield
        ]
        
        for safety_margin, break_even_yield, target_yield, expected_risk in test_cases:
            risk_level = service._determine_risk_level(safety_margin, break_even_yield, target_yield)
            assert risk_level == expected_risk


class TestSensitivityAnalysis:
    """Test sensitivity analysis functionality."""
    
    @pytest.mark.asyncio
    async def test_sensitivity_analysis(self, service, sample_roi_request):
        """Test sensitivity analysis."""
        cost_structure = CostStructure(
            fixed_costs=15000.0,
            variable_costs=20000.0,
            fertilizer_costs=15000.0,
            application_costs=2500.0,
            opportunity_costs=10000.0,
            total_costs=62500.0
        )
        
        sensitivity_results = await service._perform_sensitivity_analysis(sample_roi_request, cost_structure)
        
        # Validate sensitivity analysis
        assert len(sensitivity_results) > 0
        
        # Check that key variables are analyzed
        variable_names = [s.variable_name for s in sensitivity_results]
        assert "crop_price" in variable_names
        assert "fertilizer_cost" in variable_names
        assert "yield" in variable_names
        
        # Validate each sensitivity analysis
        for analysis in sensitivity_results:
            assert analysis.variable_name is not None
            assert analysis.base_value > 0
            assert len(analysis.sensitivity_range) == 2
            assert analysis.sensitivity_range[0] < analysis.sensitivity_range[1]
            assert "0.9x" in analysis.break_even_impact
            assert "1.0x" in analysis.break_even_impact
            assert "1.1x" in analysis.break_even_impact
            assert isinstance(analysis.elasticity, (int, float))
    
    @pytest.mark.asyncio
    async def test_elasticity_calculation(self, service):
        """Test elasticity calculation."""
        # Test elasticity calculation
        base_value = 100.0
        base_break_even = 50.0
        adjusted_break_even = 55.0
        
        elasticity = service._calculate_elasticity(base_value, base_break_even, adjusted_break_even)
        
        # Expected elasticity: ((55-50)/50) / 0.1 = 0.1 / 0.1 = 1.0
        expected_elasticity = 1.0
        assert abs(elasticity - expected_elasticity) < 0.01
        
        # Test with zero values
        elasticity_zero = service._calculate_elasticity(0.0, base_break_even, adjusted_break_even)
        assert elasticity_zero == 0.0
        
        elasticity_zero_break_even = service._calculate_elasticity(base_value, 0.0, adjusted_break_even)
        assert elasticity_zero_break_even == 0.0


class TestRiskAssessment:
    """Test risk assessment functionality."""
    
    @pytest.mark.asyncio
    async def test_risk_assessment(self, service):
        """Test risk assessment."""
        # Create mock analysis results
        analysis_results = {
            "basic_analysis": {
                "safety_margin_percentage": 15.0,
                "probability_of_profitability": 0.7
            },
            "stochastic_analysis": {
                "break_even_probabilities": {
                    "profitable": 0.65
                },
                "risk_metrics": {
                    "value_at_risk_5pct": -2000.0
                }
            }
        }
        
        risk_assessment = await service._assess_break_even_risk(analysis_results)
        
        # Validate risk assessment
        assert risk_assessment["overall_risk_level"] in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        assert isinstance(risk_assessment["risk_score"], int)
        assert 0 <= risk_assessment["risk_score"] <= 10
        assert isinstance(risk_assessment["risk_factors"], list)
        assert isinstance(risk_assessment["risk_mitigation_recommendations"], list)
    
    @pytest.mark.asyncio
    async def test_risk_mitigation_recommendations(self, service):
        """Test risk mitigation recommendations."""
        risk_factors = [
            "Very low safety margin",
            "Low probability of profitability",
            "High downside risk"
        ]
        
        recommendations = service._get_risk_mitigation_recommendations(risk_factors)
        
        # Validate recommendations
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Check that appropriate recommendations are generated
        recommendation_text = " ".join(recommendations).lower()
        assert "cost" in recommendation_text or "strategy" in recommendation_text


class TestComprehensiveAnalysis:
    """Test comprehensive break-even analysis."""
    
    @pytest.mark.asyncio
    async def test_comprehensive_analysis_basic_only(self, service, sample_roi_request):
        """Test comprehensive analysis with basic features only."""
        with patch.object(service.roi_optimizer, 'optimize_fertilizer_roi') as mock_optimize:
            mock_optimize.return_value = MagicMock(
                optimization_result=OptimizationResult(
                    optimization_id="test",
                    total_expected_revenue=81000.0,
                    total_fertilizer_cost=15000.0,
                    net_profit=66000.0,
                    roi_percentage=440.0,
                    break_even_yield=33.33,
                    marginal_return_rate=440.0,
                    risk_adjusted_return=396.0,
                    nutrient_recommendations=[],
                    optimization_metadata={}
                )
            )
            
            results = await service.perform_comprehensive_break_even_analysis(
                sample_roi_request,
                include_stochastic=False,
                include_scenarios=False,
                include_sensitivity=False,
                monte_carlo_iterations=1000
            )
            
            # Validate basic results
            assert "analysis_id" in results
            assert "timestamp" in results
            assert "basic_analysis" in results
            assert "cost_structure" in results
            assert "field_summary" in results
            assert "product_summary" in results
            assert "risk_assessment" in results
            assert "recommendations" in results
            
            # Validate that advanced features are not included
            assert "stochastic_analysis" not in results
            assert "scenario_analysis" not in results
            assert "sensitivity_analysis" not in results
    
    @pytest.mark.asyncio
    async def test_comprehensive_analysis_all_features(self, service, sample_roi_request):
        """Test comprehensive analysis with all features."""
        with patch.object(service.roi_optimizer, 'optimize_fertilizer_roi') as mock_optimize:
            mock_optimize.return_value = MagicMock(
                optimization_result=OptimizationResult(
                    optimization_id="test",
                    total_expected_revenue=81000.0,
                    total_fertilizer_cost=15000.0,
                    net_profit=66000.0,
                    roi_percentage=440.0,
                    break_even_yield=33.33,
                    marginal_return_rate=440.0,
                    risk_adjusted_return=396.0,
                    nutrient_recommendations=[],
                    optimization_metadata={}
                )
            )
            
            results = await service.perform_comprehensive_break_even_analysis(
                sample_roi_request,
                include_stochastic=True,
                include_scenarios=True,
                include_sensitivity=True,
                monte_carlo_iterations=1000
            )
            
            # Validate all features are included
            assert "stochastic_analysis" in results
            assert "scenario_analysis" in results
            assert "sensitivity_analysis" in results
            
            # Validate stochastic analysis
            stochastic = results["stochastic_analysis"]
            assert stochastic.iterations == 1000
            assert "profitable" in stochastic.break_even_probabilities
            
            # Validate scenario analysis
            scenarios = results["scenario_analysis"]
            assert len(scenarios) == 4
            
            # Validate sensitivity analysis
            sensitivity = results["sensitivity_analysis"]
            assert len(sensitivity) > 0
    
    @pytest.mark.asyncio
    async def test_field_summary(self, service, sample_field_data):
        """Test field summary generation."""
        fields = [sample_field_data]
        summary = await service._summarize_fields(fields)
        
        assert summary["total_fields"] == 1
        assert summary["total_acres"] == 100.0
        assert summary["average_yield_target"] == 180.0
        assert "corn" in summary["crop_types"]
        assert "clay_loam" in summary["soil_types"]
    
    @pytest.mark.asyncio
    async def test_product_summary(self, service, sample_fertilizer_product):
        """Test product summary generation."""
        products = [sample_fertilizer_product]
        summary = await service._summarize_products(products)
        
        assert summary["total_products"] == 1
        assert "N" in summary["nutrient_types"]
        assert summary["average_cost_per_unit"] == 0.45
        assert "Test Urea" in summary["product_names"]


class TestErrorHandling:
    """Test error handling in break-even analysis."""
    
    @pytest.mark.asyncio
    async def test_error_handling_in_comprehensive_analysis(self, service, sample_roi_request):
        """Test error handling in comprehensive analysis."""
        with patch.object(service.roi_optimizer, 'optimize_fertilizer_roi') as mock_optimize:
            mock_optimize.side_effect = Exception("Optimization failed")
            
            with pytest.raises(Exception) as exc_info:
                await service.perform_comprehensive_break_even_analysis(sample_roi_request)
            
            assert "Optimization failed" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_error_handling_with_empty_fields(self, service):
        """Test error handling with empty fields."""
        empty_request = ROIOptimizationRequest(
            fields=[],
            products=[],
            optimization_method=OptimizationMethod.LINEAR_PROGRAMMING
        )
        
        with pytest.raises(Exception):
            await service.perform_comprehensive_break_even_analysis(empty_request)


class TestPerformanceRequirements:
    """Test performance requirements for break-even analysis."""
    
    @pytest.mark.asyncio
    async def test_monte_carlo_performance(self, service, sample_roi_request):
        """Test Monte Carlo simulation performance."""
        import time
        
        cost_structure = CostStructure(
            fixed_costs=15000.0,
            variable_costs=20000.0,
            fertilizer_costs=15000.0,
            application_costs=2500.0,
            opportunity_costs=10000.0,
            total_costs=62500.0
        )
        
        start_time = time.time()
        
        # Run Monte Carlo with moderate iterations
        await service._perform_monte_carlo_simulation(sample_roi_request, cost_structure, 5000)
        
        elapsed_time = time.time() - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert elapsed_time < 30.0, f"Monte Carlo simulation took too long: {elapsed_time:.2f}s"
    
    @pytest.mark.asyncio
    async def test_comprehensive_analysis_performance(self, service, sample_roi_request):
        """Test comprehensive analysis performance."""
        import time
        
        with patch.object(service.roi_optimizer, 'optimize_fertilizer_roi') as mock_optimize:
            mock_optimize.return_value = MagicMock(
                optimization_result=OptimizationResult(
                    optimization_id="test",
                    total_expected_revenue=81000.0,
                    total_fertilizer_cost=15000.0,
                    net_profit=66000.0,
                    roi_percentage=440.0,
                    break_even_yield=33.33,
                    marginal_return_rate=440.0,
                    risk_adjusted_return=396.0,
                    nutrient_recommendations=[],
                    optimization_metadata={}
                )
            )
            
            start_time = time.time()
            
            # Run comprehensive analysis with moderate Monte Carlo iterations
            await service.perform_comprehensive_break_even_analysis(
                sample_roi_request,
                include_stochastic=True,
                include_scenarios=True,
                include_sensitivity=True,
                monte_carlo_iterations=2000
            )
            
            elapsed_time = time.time() - start_time
            
            # Should complete within reasonable time
            assert elapsed_time < 60.0, f"Comprehensive analysis took too long: {elapsed_time:.2f}s"


# Agricultural validation tests
class TestAgriculturalValidation:
    """Agricultural validation tests for break-even analysis."""
    
    @pytest.mark.asyncio
    async def test_realistic_corn_scenario(self, service):
        """Test break-even analysis with realistic corn scenario."""
        # Realistic corn field data
        corn_field = FieldData(
            field_id="corn_field_1",
            acres=80.0,
            soil_type="silt_loam",
            current_ph=6.2,
            organic_matter_percent=2.8,
            target_yield=175.0,  # Realistic corn yield
            crop_price=4.25,     # Realistic corn price
            previous_crop="soybean",
            tillage_system="no_till",
            irrigation_available=False
        )
        
        # Realistic fertilizer products
        urea = FertilizerProduct(
            product_id="urea_46",
            product_name="Urea 46-0-0",
            nutrient_type="N",
            nutrient_percentage=46.0,
            cost_per_unit=0.42,
            unit="lb",
            application_method="broadcast",
            availability="available"
        )
        
        request = ROIOptimizationRequest(
            fields=[corn_field],
            products=[urea],
            optimization_method=OptimizationMethod.LINEAR_PROGRAMMING
        )
        
        with patch.object(service.roi_optimizer, 'optimize_fertilizer_roi') as mock_optimize:
            mock_optimize.return_value = MagicMock(
                optimization_result=OptimizationResult(
                    optimization_id="corn_test",
                    total_expected_revenue=59500.0,  # 80 * 175 * 4.25
                    total_fertilizer_cost=8000.0,    # Realistic fertilizer cost
                    net_profit=51500.0,
                    roi_percentage=643.75,
                    break_even_yield=23.53,  # 8000 / (80 * 4.25)
                    marginal_return_rate=643.75,
                    risk_adjusted_return=579.38,
                    nutrient_recommendations=[],
                    optimization_metadata={}
                )
            )
            
            results = await service.perform_comprehensive_break_even_analysis(
                request,
                include_stochastic=True,
                include_scenarios=True,
                include_sensitivity=True,
                monte_carlo_iterations=2000
            )
            
            # Validate realistic break-even metrics
            basic_analysis = results["basic_analysis"]
            break_even_yield = basic_analysis["break_even_yield_per_acre"]
            
            # Break-even yield should be reasonable for corn
            assert 20.0 <= break_even_yield <= 50.0, f"Break-even yield {break_even_yield} seems unrealistic for corn"
            
            # Safety margin should be positive for profitable scenario
            safety_margin = basic_analysis["safety_margin_percentage"]
            assert safety_margin > 0, "Safety margin should be positive for profitable scenario"
            
            # Probability of profitability should be high for good scenario
            probability = basic_analysis["probability_of_profitability"]
            assert probability > 0.7, "Probability of profitability should be high for good scenario"
    
    @pytest.mark.asyncio
    async def test_soybean_scenario(self, service):
        """Test break-even analysis with soybean scenario."""
        # Soybean field data
        soybean_field = FieldData(
            field_id="soybean_field_1",
            acres=120.0,
            soil_type="clay_loam",
            current_ph=6.8,
            organic_matter_percent=3.5,
            target_yield=55.0,   # Realistic soybean yield
            crop_price=12.50,    # Realistic soybean price
            previous_crop="corn",
            tillage_system="conventional",
            irrigation_available=True
        )
        
        # Phosphorus fertilizer
        dap = FertilizerProduct(
            product_id="dap_18_46",
            product_name="DAP 18-46-0",
            nutrient_type="P",
            nutrient_percentage=46.0,
            cost_per_unit=0.38,
            unit="lb",
            application_method="broadcast",
            availability="available"
        )
        
        request = ROIOptimizationRequest(
            fields=[soybean_field],
            products=[dap],
            optimization_method=OptimizationMethod.LINEAR_PROGRAMMING
        )
        
        with patch.object(service.roi_optimizer, 'optimize_fertilizer_roi') as mock_optimize:
            mock_optimize.return_value = MagicMock(
                optimization_result=OptimizationResult(
                    optimization_id="soybean_test",
                    total_expected_revenue=82500.0,  # 120 * 55 * 12.50
                    total_fertilizer_cost=6000.0,    # Lower fertilizer cost for soybeans
                    net_profit=76500.0,
                    roi_percentage=1275.0,
                    break_even_yield=4.0,  # 6000 / (120 * 12.50)
                    marginal_return_rate=1275.0,
                    risk_adjusted_return=1147.5,
                    nutrient_recommendations=[],
                    optimization_metadata={}
                )
            )
            
            results = await service.perform_comprehensive_break_even_analysis(
                request,
                include_stochastic=True,
                include_scenarios=True,
                include_sensitivity=True,
                monte_carlo_iterations=2000
            )
            
            # Validate soybean-specific metrics
            basic_analysis = results["basic_analysis"]
            break_even_yield = basic_analysis["break_even_yield_per_acre"]
            
            # Break-even yield should be very low for soybeans (low fertilizer needs)
            assert break_even_yield < 10.0, f"Break-even yield {break_even_yield} seems too high for soybeans"
            
            # Safety margin should be very high for profitable soybean scenario
            safety_margin = basic_analysis["safety_margin_percentage"]
            assert safety_margin > 50, "Safety margin should be high for profitable soybean scenario"