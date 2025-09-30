"""
Comprehensive tests for ROI Optimizer Service.

This module contains unit tests, integration tests, and agricultural validation tests
for the fertilizer ROI optimization service.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from typing import List, Dict, Any
import numpy as np

from ..models.roi_models import (
    ROIOptimizationRequest,
    FieldData,
    FertilizerProduct,
    OptimizationConstraints,
    OptimizationGoals,
    OptimizationMethod,
    RiskTolerance,
    NutrientType
)
from ..services.roi_optimizer import FertilizerROIOptimizer


class TestFertilizerROIOptimizer:
    """Test suite for FertilizerROIOptimizer service."""

    @pytest.fixture
    def optimizer(self):
        """Create ROI optimizer instance for testing."""
        return FertilizerROIOptimizer()

    @pytest.fixture
    def sample_field_data(self):
        """Create sample field data for testing."""
        return FieldData(
            field_id="test_field_1",
            acres=100.0,
            soil_tests={"N": 25, "P": 45, "K": 180, "pH": 6.5},
            crop_plan={"crop": "corn", "variety": "test_variety"},
            target_yield=180.0,
            crop_price=5.50
        )

    @pytest.fixture
    def sample_fertilizer_products(self):
        """Create sample fertilizer products for testing."""
        return [
            FertilizerProduct(
                product_id="urea_46_0_0",
                product_name="Urea 46-0-0",
                nutrient_content={"N": 46, "P": 0, "K": 0},
                price_per_unit=500.0,
                unit="ton",
                application_method="broadcast"
            ),
            FertilizerProduct(
                product_id="dap_18_46_0",
                product_name="DAP 18-46-0",
                nutrient_content={"N": 18, "P": 46, "K": 0},
                price_per_unit=600.0,
                unit="ton",
                application_method="broadcast"
            ),
            FertilizerProduct(
                product_id="potash_0_0_60",
                product_name="Muriate of Potash 0-0-60",
                nutrient_content={"N": 0, "P": 0, "K": 60},
                price_per_unit=400.0,
                unit="ton",
                application_method="broadcast"
            )
        ]

    @pytest.fixture
    def sample_constraints(self):
        """Create sample optimization constraints."""
        return OptimizationConstraints(
            max_nitrogen_rate=200.0,
            max_phosphorus_rate=100.0,
            max_potassium_rate=150.0,
            budget_limit=15000.0,
            max_per_acre_cost=150.0,
            environmental_limits={"buffer_zones": True},
            equipment_limitations=["broadcast_spreader"]
        )

    @pytest.fixture
    def sample_goals(self):
        """Create sample optimization goals."""
        return OptimizationGoals(
            primary_goal="profit_maximization",
            yield_priority=0.8,
            cost_priority=0.7,
            environmental_priority=0.6,
            risk_tolerance=RiskTolerance.MODERATE
        )

    @pytest.fixture
    def sample_optimization_request(
        self,
        sample_field_data,
        sample_fertilizer_products,
        sample_constraints,
        sample_goals
    ):
        """Create sample optimization request."""
        return ROIOptimizationRequest(
            farm_context={"farm_id": "test_farm"},
            fields=[sample_field_data],
            fertilizer_products=sample_fertilizer_products,
            constraints=sample_constraints,
            goals=sample_goals,
            optimization_method=OptimizationMethod.LINEAR_PROGRAMMING,
            include_sensitivity_analysis=True,
            include_risk_assessment=True
        )

    @pytest.mark.asyncio
    async def test_optimize_fertilizer_roi_success(self, optimizer, sample_optimization_request):
        """Test successful ROI optimization."""
        result = await optimizer.optimize_fertilizer_roi(sample_optimization_request)
        
        assert result is not None
        assert result.optimization_result is not None
        assert result.optimization_result.roi_percentage > 0
        assert result.optimization_result.total_expected_revenue > 0
        assert result.optimization_result.total_fertilizer_cost > 0
        assert result.optimization_result.net_profit is not None
        assert len(result.optimization_result.nutrient_recommendations) > 0
        assert result.sensitivity_analysis is not None
        assert result.risk_assessment is not None
        assert result.processing_time_ms > 0

    @pytest.mark.asyncio
    async def test_linear_programming_optimization(self, optimizer, sample_optimization_request):
        """Test linear programming optimization method."""
        sample_optimization_request.optimization_method = OptimizationMethod.LINEAR_PROGRAMMING
        
        result = await optimizer._linear_programming_optimization(sample_optimization_request)
        
        assert result is not None
        assert result.roi_percentage > 0
        assert result.total_expected_revenue > 0
        assert result.total_fertilizer_cost > 0
        assert result.net_profit is not None

    @pytest.mark.asyncio
    async def test_quadratic_programming_optimization(self, optimizer, sample_optimization_request):
        """Test quadratic programming optimization method."""
        sample_optimization_request.optimization_method = OptimizationMethod.QUADRATIC_PROGRAMMING
        
        result = await optimizer._quadratic_programming_optimization(sample_optimization_request)
        
        assert result is not None
        assert result.roi_percentage > 0
        assert result.total_expected_revenue > 0
        assert result.total_fertilizer_cost > 0
        assert result.net_profit is not None

    @pytest.mark.asyncio
    async def test_genetic_algorithm_optimization(self, optimizer, sample_optimization_request):
        """Test genetic algorithm optimization method."""
        sample_optimization_request.optimization_method = OptimizationMethod.GENETIC_ALGORITHM
        
        result = await optimizer._genetic_algorithm_optimization(sample_optimization_request)
        
        assert result is not None
        assert result.roi_percentage > 0
        assert result.total_expected_revenue > 0
        assert result.total_fertilizer_cost > 0
        assert result.net_profit is not None

    @pytest.mark.asyncio
    async def test_gradient_descent_optimization(self, optimizer, sample_optimization_request):
        """Test gradient descent optimization method."""
        sample_optimization_request.optimization_method = OptimizationMethod.GRADIENT_DESCENT
        
        result = await optimizer._gradient_descent_optimization(sample_optimization_request)
        
        assert result is not None
        assert result.roi_percentage > 0
        assert result.total_expected_revenue > 0
        assert result.total_fertilizer_cost > 0
        assert result.net_profit is not None

    @pytest.mark.asyncio
    async def test_sensitivity_analysis(self, optimizer, sample_optimization_request):
        """Test sensitivity analysis functionality."""
        # Create a mock optimization result
        mock_result = MagicMock()
        mock_result.roi_percentage = 125.0
        mock_result.total_fertilizer_cost = 10000.0
        
        sensitivity_analysis = await optimizer._perform_sensitivity_analysis(
            sample_optimization_request, mock_result
        )
        
        assert sensitivity_analysis is not None
        assert len(sensitivity_analysis) > 0
        
        for analysis in sensitivity_analysis:
            assert analysis.parameter is not None
            assert analysis.base_value is not None
            assert len(analysis.sensitivity_range) > 0
            assert len(analysis.roi_impact) > 0
            assert analysis.risk_level is not None

    @pytest.mark.asyncio
    async def test_risk_assessment(self, optimizer, sample_optimization_request):
        """Test risk assessment functionality."""
        # Create a mock optimization result
        mock_result = MagicMock()
        mock_result.roi_percentage = 125.0
        mock_result.total_fertilizer_cost = 10000.0
        
        risk_assessment = await optimizer._perform_risk_assessment(
            sample_optimization_request, mock_result
        )
        
        assert risk_assessment is not None
        assert 0 <= risk_assessment.overall_risk_score <= 1
        assert len(risk_assessment.risk_factors) > 0
        assert len(risk_assessment.mitigation_strategies) >= 0
        assert 0 <= risk_assessment.confidence_level <= 1
        assert risk_assessment.scenario_analysis is not None

    @pytest.mark.asyncio
    async def test_alternative_scenarios_generation(self, optimizer, sample_optimization_request):
        """Test alternative scenarios generation."""
        # Create a mock optimization result
        mock_result = MagicMock()
        mock_result.total_fertilizer_cost = 10000.0
        mock_result.total_expected_revenue = 15000.0
        mock_result.roi_percentage = 50.0
        
        scenarios = await optimizer._generate_alternative_scenarios(
            sample_optimization_request, mock_result
        )
        
        assert scenarios is not None
        assert len(scenarios) > 0
        
        for scenario in scenarios:
            assert "scenario_name" in scenario
            assert "description" in scenario
            assert "fertilizer_cost" in scenario
            assert "expected_revenue" in scenario
            assert "roi_percentage" in scenario
            assert "risk_level" in scenario

    @pytest.mark.asyncio
    async def test_recommendations_generation(self, optimizer, sample_optimization_request):
        """Test recommendations generation."""
        # Create a mock optimization result
        mock_result = MagicMock()
        mock_result.roi_percentage = 125.0
        mock_result.total_fertilizer_cost = 10000.0
        
        # Create a mock risk assessment
        mock_risk_assessment = MagicMock()
        mock_risk_assessment.overall_risk_score = 0.3
        
        recommendations = await optimizer._generate_recommendations(
            sample_optimization_request, mock_result, mock_risk_assessment
        )
        
        assert recommendations is not None
        assert len(recommendations) > 0
        
        for recommendation in recommendations:
            assert isinstance(recommendation, str)
            assert len(recommendation) > 0

    def test_calculate_yield_response(self, optimizer, sample_field_data, sample_fertilizer_products):
        """Test yield response calculation."""
        field = sample_field_data
        product = sample_fertilizer_products[0]  # Urea
        
        yield_response = optimizer._calculate_yield_response(field, product)
        
        assert yield_response >= 0
        assert isinstance(yield_response, float)

    def test_calculate_optimal_rate(self, optimizer, sample_field_data, sample_fertilizer_products, sample_constraints):
        """Test optimal rate calculation."""
        field = sample_field_data
        product = sample_fertilizer_products[0]  # Urea
        constraints = sample_constraints
        
        optimal_rate = optimizer._calculate_optimal_rate(field, product, constraints)
        
        assert optimal_rate >= 0
        assert isinstance(optimal_rate, float)

    def test_validate_optimization_request_valid(self, optimizer, sample_optimization_request):
        """Test validation of valid optimization request."""
        # Should not raise any exception
        optimizer._validate_optimization_request(sample_optimization_request)

    def test_validate_optimization_request_empty_fields(self, optimizer, sample_fertilizer_products, sample_constraints, sample_goals):
        """Test validation with empty fields."""
        invalid_request = ROIOptimizationRequest(
            farm_context={"farm_id": "test_farm"},
            fields=[],  # Empty fields
            fertilizer_products=sample_fertilizer_products,
            constraints=sample_constraints,
            goals=sample_goals
        )
        
        with pytest.raises(ValueError, match="At least one field is required"):
            optimizer._validate_optimization_request(invalid_request)

    def test_validate_optimization_request_empty_products(self, optimizer, sample_field_data, sample_constraints, sample_goals):
        """Test validation with empty fertilizer products."""
        invalid_request = ROIOptimizationRequest(
            farm_context={"farm_id": "test_farm"},
            fields=[sample_field_data],
            fertilizer_products=[],  # Empty products
            constraints=sample_constraints,
            goals=sample_goals
        )
        
        with pytest.raises(ValueError, match="At least one fertilizer product is required"):
            optimizer._validate_optimization_request(invalid_request)

    def test_validate_optimization_request_invalid_field_data(self, optimizer, sample_fertilizer_products, sample_constraints, sample_goals):
        """Test validation with invalid field data."""
        invalid_field = FieldData(
            field_id="invalid_field",
            acres=0,  # Invalid acres
            soil_tests={"N": 25, "P": 45, "K": 180, "pH": 6.5},
            crop_plan={"crop": "corn"},
            target_yield=180.0,
            crop_price=5.50
        )
        
        invalid_request = ROIOptimizationRequest(
            farm_context={"farm_id": "test_farm"},
            fields=[invalid_field],
            fertilizer_products=sample_fertilizer_products,
            constraints=sample_constraints,
            goals=sample_goals
        )
        
        with pytest.raises(ValueError, match="must have positive acres"):
            optimizer._validate_optimization_request(invalid_request)

    def test_genetic_algorithm_crossover(self, optimizer):
        """Test genetic algorithm crossover operation."""
        parent1 = [10.0, 20.0, 30.0]
        parent2 = [15.0, 25.0, 35.0]
        
        child = optimizer._crossover(parent1, parent2)
        
        assert len(child) == len(parent1)
        assert len(child) == len(parent2)
        
        for i in range(len(child)):
            assert child[i] == parent1[i] or child[i] == parent2[i]

    def test_genetic_algorithm_mutation(self, optimizer, sample_optimization_request):
        """Test genetic algorithm mutation operation."""
        individual = [10.0, 20.0, 30.0]
        
        mutated = optimizer._mutate(individual, sample_optimization_request)
        
        assert len(mutated) == len(individual)
        
        # Check that values are non-negative
        for value in mutated:
            assert value >= 0

    @pytest.mark.asyncio
    async def test_calculate_fitness(self, optimizer, sample_optimization_request):
        """Test fitness calculation for genetic algorithm."""
        individual = [10.0, 20.0, 30.0]
        
        fitness = await optimizer._calculate_fitness(individual, sample_optimization_request)
        
        assert isinstance(fitness, float)
        assert fitness >= 0  # Profit should be non-negative

    @pytest.mark.asyncio
    async def test_create_optimization_result(self, optimizer, sample_optimization_request):
        """Test optimization result creation."""
        rates = [10.0, 20.0, 30.0]
        objective_value = -1000.0
        
        result = await optimizer._create_optimization_result(
            sample_optimization_request, rates, objective_value
        )
        
        assert result is not None
        assert result.optimization_id is not None
        assert result.total_expected_revenue >= 0
        assert result.total_fertilizer_cost >= 0
        assert result.net_profit is not None
        assert result.roi_percentage is not None
        assert result.break_even_yield >= 0
        assert len(result.nutrient_recommendations) > 0
        assert result.optimization_metadata is not None

    @pytest.mark.asyncio
    async def test_simplified_optimization_fallback(self, optimizer, sample_optimization_request):
        """Test simplified optimization as fallback."""
        result = await optimizer._simplified_optimization(sample_optimization_request)
        
        assert result is not None
        assert result.roi_percentage >= 0
        assert result.total_expected_revenue >= 0
        assert result.total_fertilizer_cost >= 0
        assert result.net_profit is not None

    @pytest.mark.asyncio
    async def test_optimization_with_multiple_fields(self, optimizer, sample_fertilizer_products, sample_constraints, sample_goals):
        """Test optimization with multiple fields."""
        field1 = FieldData(
            field_id="field_1",
            acres=100.0,
            soil_tests={"N": 25, "P": 45, "K": 180, "pH": 6.5},
            crop_plan={"crop": "corn"},
            target_yield=180.0,
            crop_price=5.50
        )
        
        field2 = FieldData(
            field_id="field_2",
            acres=150.0,
            soil_tests={"N": 30, "P": 50, "K": 200, "pH": 6.8},
            crop_plan={"crop": "corn"},
            target_yield=190.0,
            crop_price=5.50
        )
        
        multi_field_request = ROIOptimizationRequest(
            farm_context={"farm_id": "test_farm"},
            fields=[field1, field2],
            fertilizer_products=sample_fertilizer_products,
            constraints=sample_constraints,
            goals=sample_goals
        )
        
        result = await optimizer.optimize_fertilizer_roi(multi_field_request)
        
        assert result is not None
        assert result.optimization_result is not None
        assert result.optimization_result.roi_percentage > 0
        assert len(result.optimization_result.nutrient_recommendations) > 0

    @pytest.mark.asyncio
    async def test_optimization_with_budget_constraints(self, optimizer, sample_field_data, sample_fertilizer_products, sample_goals):
        """Test optimization with budget constraints."""
        tight_constraints = OptimizationConstraints(
            max_nitrogen_rate=100.0,  # Lower than default
            max_phosphorus_rate=50.0,
            max_potassium_rate=75.0,
            budget_limit=5000.0,  # Tight budget
            max_per_acre_cost=50.0,
            environmental_limits={"buffer_zones": True},
            equipment_limitations=["broadcast_spreader"]
        )
        
        budget_request = ROIOptimizationRequest(
            farm_context={"farm_id": "test_farm"},
            fields=[sample_field_data],
            fertilizer_products=sample_fertilizer_products,
            constraints=tight_constraints,
            goals=sample_goals
        )
        
        result = await optimizer.optimize_fertilizer_roi(budget_request)
        
        assert result is not None
        assert result.optimization_result is not None
        assert result.optimization_result.total_fertilizer_cost <= tight_constraints.budget_limit

    @pytest.mark.asyncio
    async def test_optimization_with_different_risk_tolerances(self, optimizer, sample_field_data, sample_fertilizer_products, sample_constraints):
        """Test optimization with different risk tolerance levels."""
        for risk_tolerance in [RiskTolerance.CONSERVATIVE, RiskTolerance.MODERATE, RiskTolerance.AGGRESSIVE]:
            goals = OptimizationGoals(
                primary_goal="profit_maximization",
                yield_priority=0.8,
                cost_priority=0.7,
                environmental_priority=0.6,
                risk_tolerance=risk_tolerance
            )
            
            risk_request = ROIOptimizationRequest(
                farm_context={"farm_id": "test_farm"},
                fields=[sample_field_data],
                fertilizer_products=sample_fertilizer_products,
                constraints=sample_constraints,
                goals=goals
            )
            
            result = await optimizer.optimize_fertilizer_roi(risk_request)
            
            assert result is not None
            assert result.optimization_result is not None
            assert result.risk_assessment is not None
            assert result.risk_assessment.overall_risk_score >= 0


class TestAgriculturalValidation:
    """Agricultural validation tests for ROI optimization."""

    @pytest.fixture
    def optimizer(self):
        """Create ROI optimizer instance for testing."""
        return FertilizerROIOptimizer()

    @pytest.mark.asyncio
    async def test_corn_belt_optimization_realistic(self, optimizer):
        """Test optimization with realistic corn belt parameters."""
        field = FieldData(
            field_id="corn_belt_field",
            acres=80.0,
            soil_tests={"N": 20, "P": 40, "K": 150, "pH": 6.2},
            crop_plan={"crop": "corn", "variety": "pioneer_1234"},
            target_yield=200.0,
            crop_price=5.25
        )
        
        products = [
            FertilizerProduct(
                product_id="urea_46_0_0",
                product_name="Urea 46-0-0",
                nutrient_content={"N": 46, "P": 0, "K": 0},
                price_per_unit=450.0,  # Realistic price
                unit="ton",
                application_method="broadcast"
            ),
            FertilizerProduct(
                product_id="dap_18_46_0",
                product_name="DAP 18-46-0",
                nutrient_content={"N": 18, "P": 46, "K": 0},
                price_per_unit=550.0,
                unit="ton",
                application_method="broadcast"
            )
        ]
        
        constraints = OptimizationConstraints(
            max_nitrogen_rate=180.0,
            max_phosphorus_rate=80.0,
            budget_limit=12000.0,
            max_per_acre_cost=150.0
        )
        
        goals = OptimizationGoals(
            primary_goal="profit_maximization",
            yield_priority=0.8,
            cost_priority=0.7,
            risk_tolerance=RiskTolerance.MODERATE
        )
        
        request = ROIOptimizationRequest(
            farm_context={"farm_id": "corn_belt_farm"},
            fields=[field],
            fertilizer_products=products,
            constraints=constraints,
            goals=goals
        )
        
        result = await optimizer.optimize_fertilizer_roi(request)
        
        # Validate agricultural realism
        assert result.optimization_result.roi_percentage > 0
        assert result.optimization_result.roi_percentage < 500  # Realistic upper bound
        
        # Check nutrient recommendations are reasonable
        n_recommendations = [
            rec for rec in result.optimization_result.nutrient_recommendations
            if rec.nutrient_type == NutrientType.NITROGEN
        ]
        assert len(n_recommendations) > 0
        
        for rec in n_recommendations:
            assert 0 <= rec.recommended_rate <= 200  # Realistic N rate range

    @pytest.mark.asyncio
    async def test_soybean_optimization_realistic(self, optimizer):
        """Test optimization with realistic soybean parameters."""
        field = FieldData(
            field_id="soybean_field",
            acres=120.0,
            soil_tests={"N": 35, "P": 25, "K": 120, "pH": 6.5},
            crop_plan={"crop": "soybean", "variety": "asgrow_1234"},
            target_yield=55.0,  # Realistic soybean yield
            crop_price=12.50  # Realistic soybean price
        )
        
        products = [
            FertilizerProduct(
                product_id="dap_18_46_0",
                product_name="DAP 18-46-0",
                nutrient_content={"N": 18, "P": 46, "K": 0},
                price_per_unit=550.0,
                unit="ton",
                application_method="broadcast"
            ),
            FertilizerProduct(
                product_id="potash_0_0_60",
                product_name="Muriate of Potash 0-0-60",
                nutrient_content={"N": 0, "P": 0, "K": 60},
                price_per_unit=400.0,
                unit="ton",
                application_method="broadcast"
            )
        ]
        
        constraints = OptimizationConstraints(
            max_phosphorus_rate=60.0,
            max_potassium_rate=100.0,
            budget_limit=8000.0,
            max_per_acre_cost=70.0
        )
        
        goals = OptimizationGoals(
            primary_goal="profit_maximization",
            yield_priority=0.8,
            cost_priority=0.7,
            risk_tolerance=RiskTolerance.CONSERVATIVE
        )
        
        request = ROIOptimizationRequest(
            farm_context={"farm_id": "soybean_farm"},
            fields=[field],
            fertilizer_products=products,
            constraints=constraints,
            goals=goals
        )
        
        result = await optimizer.optimize_fertilizer_roi(request)
        
        # Validate agricultural realism for soybeans
        assert result.optimization_result.roi_percentage > 0
        assert result.optimization_result.roi_percentage < 300  # Lower ROI for soybeans
        
        # Check that P and K recommendations are reasonable
        p_recommendations = [
            rec for rec in result.optimization_result.nutrient_recommendations
            if rec.nutrient_type == NutrientType.PHOSPHORUS
        ]
        k_recommendations = [
            rec for rec in result.optimization_result.nutrient_recommendations
            if rec.nutrient_type == NutrientType.POTASSIUM
        ]
        
        assert len(p_recommendations) > 0 or len(k_recommendations) > 0

    @pytest.mark.asyncio
    async def test_break_even_analysis_realistic(self, optimizer):
        """Test break-even analysis with realistic parameters."""
        field = FieldData(
            field_id="break_even_field",
            acres=100.0,
            soil_tests={"N": 15, "P": 30, "K": 100, "pH": 6.0},
            crop_plan={"crop": "corn"},
            target_yield=160.0,
            crop_price=4.50  # Lower price for break-even testing
        )
        
        products = [
            FertilizerProduct(
                product_id="urea_46_0_0",
                product_name="Urea 46-0-0",
                nutrient_content={"N": 46, "P": 0, "K": 0},
                price_per_unit=500.0,
                unit="ton",
                application_method="broadcast"
            )
        ]
        
        constraints = OptimizationConstraints(
            max_nitrogen_rate=150.0,
            budget_limit=10000.0
        )
        
        goals = OptimizationGoals(
            primary_goal="profit_maximization",
            yield_priority=0.8,
            cost_priority=0.7,
            risk_tolerance=RiskTolerance.MODERATE
        )
        
        request = ROIOptimizationRequest(
            farm_context={"farm_id": "break_even_farm"},
            fields=[field],
            fertilizer_products=products,
            constraints=constraints,
            goals=goals
        )
        
        result = await optimizer.optimize_fertilizer_roi(request)
        
        # Validate break-even analysis
        assert result.optimization_result.break_even_yield > 0
        assert result.optimization_result.break_even_yield < field.target_yield * 1.5  # Reasonable upper bound
        
        # Check that break-even yield is achievable
        assert result.optimization_result.break_even_yield <= field.target_yield * 1.2


class TestPerformanceValidation:
    """Performance validation tests for ROI optimization."""

    @pytest.fixture
    def optimizer(self):
        """Create ROI optimizer instance for testing."""
        return FertilizerROIOptimizer()

    @pytest.fixture
    def sample_field_data(self):
        """Create sample field data for testing."""
        return FieldData(
            field_id="test_field_1",
            acres=100.0,
            soil_tests={"N": 25, "P": 45, "K": 180, "pH": 6.5},
            crop_plan={"crop": "corn", "variety": "test_variety"},
            target_yield=180.0,
            crop_price=5.50
        )

    @pytest.fixture
    def sample_fertilizer_products(self):
        """Create sample fertilizer products for testing."""
        return [
            FertilizerProduct(
                product_id="urea_46_0_0",
                product_name="Urea 46-0-0",
                nutrient_content={"N": 46, "P": 0, "K": 0},
                price_per_unit=500.0,
                unit="ton",
                application_method="broadcast"
            ),
            FertilizerProduct(
                product_id="dap_18_46_0",
                product_name="DAP 18-46-0",
                nutrient_content={"N": 18, "P": 46, "K": 0},
                price_per_unit=600.0,
                unit="ton",
                application_method="broadcast"
            )
        ]

    @pytest.fixture
    def sample_constraints(self):
        """Create sample optimization constraints."""
        return OptimizationConstraints(
            max_nitrogen_rate=200.0,
            max_phosphorus_rate=100.0,
            max_potassium_rate=150.0,
            budget_limit=15000.0,
            max_per_acre_cost=150.0,
            environmental_limits={"buffer_zones": True},
            equipment_limitations=["broadcast_spreader"]
        )

    @pytest.fixture
    def sample_goals(self):
        """Create sample optimization goals."""
        return OptimizationGoals(
            primary_goal="profit_maximization",
            yield_priority=0.8,
            cost_priority=0.7,
            environmental_priority=0.6,
            risk_tolerance=RiskTolerance.MODERATE
        )

    @pytest.fixture
    def sample_optimization_request(
        self,
        sample_field_data,
        sample_fertilizer_products,
        sample_constraints,
        sample_goals
    ):
        """Create sample optimization request."""
        return ROIOptimizationRequest(
            farm_context={"farm_id": "test_farm"},
            fields=[sample_field_data],
            fertilizer_products=sample_fertilizer_products,
            constraints=sample_constraints,
            goals=sample_goals,
            optimization_method=OptimizationMethod.LINEAR_PROGRAMMING,
            include_sensitivity_analysis=True,
            include_risk_assessment=True
        )

    @pytest.mark.asyncio
    async def test_optimization_response_time(self, optimizer, sample_optimization_request):
        """Test that optimization completes within acceptable time."""
        import time
        
        start_time = time.time()
        result = await optimizer.optimize_fertilizer_roi(sample_optimization_request)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should complete within 5 seconds for simple optimization
        assert processing_time < 5.0
        assert result.processing_time_ms > 0
        assert result.processing_time_ms < 5000  # 5 seconds in milliseconds

    @pytest.mark.asyncio
    async def test_optimization_with_large_field_count(self, optimizer, sample_fertilizer_products, sample_constraints, sample_goals):
        """Test optimization performance with multiple fields."""
        # Create multiple fields
        fields = []
        for i in range(10):  # 10 fields
            field = FieldData(
                field_id=f"field_{i}",
                acres=100.0,
                soil_tests={"N": 25, "P": 45, "K": 180, "pH": 6.5},
                crop_plan={"crop": "corn"},
                target_yield=180.0,
                crop_price=5.50
            )
            fields.append(field)
        
        large_request = ROIOptimizationRequest(
            farm_context={"farm_id": "large_farm"},
            fields=fields,
            fertilizer_products=sample_fertilizer_products,
            constraints=sample_constraints,
            goals=sample_goals
        )
        
        import time
        start_time = time.time()
        result = await optimizer.optimize_fertilizer_roi(large_request)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should still complete within reasonable time
        assert processing_time < 10.0
        assert result.optimization_result is not None
        assert len(result.optimization_result.nutrient_recommendations) > 0

    @pytest.mark.asyncio
    async def test_optimization_memory_usage(self, optimizer, sample_optimization_request):
        """Test that optimization doesn't consume excessive memory."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Perform optimization
        result = await optimizer.optimize_fertilizer_roi(sample_optimization_request)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024  # 100MB in bytes
        assert result.optimization_result is not None