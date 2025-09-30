"""
Tests for Budget Constraint Optimization Service.

This module contains comprehensive tests for the budget constraint optimization
service including multi-objective optimization, Pareto frontier analysis, and
constraint relaxation functionality.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from typing import List, Dict, Any

from ..services.budget_constraint_optimizer import BudgetConstraintOptimizer
from ..models.roi_models import (
    ROIOptimizationRequest,
    BudgetConstraint,
    OptimizationConstraints,
    OptimizationGoals,
    FieldData,
    FertilizerProduct,
    RiskTolerance,
    MultiObjectiveOptimizationResult,
    BudgetAllocationResult,
    ParetoFrontierPoint,
    ConstraintRelaxationAnalysis
)


class TestBudgetConstraintOptimizer:
    """Comprehensive test suite for budget constraint optimizer."""

    @pytest.fixture
    def optimizer(self):
        """Create optimizer instance for testing."""
        return BudgetConstraintOptimizer()

    @pytest.fixture
    def sample_fields(self):
        """Create sample field data for testing."""
        return [
            FieldData(
                field_id="field_1",
                acres=100.0,
                soil_tests={"N": 50, "P": 20, "K": 150},
                crop_plan={"crop": "corn", "variety": "hybrid"},
                target_yield=180.0,
                crop_price=5.50
            ),
            FieldData(
                field_id="field_2",
                acres=150.0,
                soil_tests={"N": 40, "P": 15, "K": 120},
                crop_plan={"crop": "soybean", "variety": "roundup_ready"},
                target_yield=50.0,
                crop_price=12.00
            )
        ]

    @pytest.fixture
    def sample_products(self):
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
                product_name="Potash 0-0-60",
                nutrient_content={"N": 0, "P": 0, "K": 60},
                price_per_unit=400.0,
                unit="ton",
                application_method="broadcast"
            )
        ]

    @pytest.fixture
    def sample_budget_constraint(self):
        """Create sample budget constraint for testing."""
        return BudgetConstraint(
            total_budget_limit=50000.0,
            per_field_budget_limit=30000.0,
            per_acre_budget_limit=200.0,
            nutrient_budget_allocation={"N": 0.4, "P": 0.3, "K": 0.3},
            product_budget_allocation={"urea_46_0_0": 0.5, "dap_18_46_0": 0.3, "potash_0_0_60": 0.2},
            budget_flexibility_percentage=15.0,
            allow_budget_reallocation=True,
            budget_utilization_target=95.0
        )

    @pytest.fixture
    def sample_constraints(self, sample_budget_constraint):
        """Create sample optimization constraints for testing."""
        return OptimizationConstraints(
            max_nitrogen_rate=200.0,
            max_phosphorus_rate=100.0,
            max_potassium_rate=150.0,
            budget_constraint=sample_budget_constraint,
            max_per_acre_cost=250.0
        )

    @pytest.fixture
    def sample_goals(self):
        """Create sample optimization goals for testing."""
        return OptimizationGoals(
            primary_goal="profit_maximization",
            yield_priority=0.8,
            cost_priority=0.7,
            environmental_priority=0.6,
            risk_tolerance=RiskTolerance.MODERATE
        )

    @pytest.fixture
    def sample_request(self, sample_fields, sample_products, sample_constraints, sample_goals):
        """Create sample optimization request for testing."""
        return ROIOptimizationRequest(
            farm_context={"farm_id": "test_farm", "region": "midwest"},
            fields=sample_fields,
            fertilizer_products=sample_products,
            constraints=sample_constraints,
            goals=sample_goals,
            include_sensitivity_analysis=True,
            include_risk_assessment=True
        )

    @pytest.mark.asyncio
    async def test_optimize_budget_constraints_success(self, optimizer, sample_request):
        """Test successful budget constraint optimization."""
        with patch.object(optimizer, '_generate_pareto_frontier') as mock_pareto, \
             patch.object(optimizer, '_select_recommended_scenario') as mock_scenario, \
             patch.object(optimizer, '_optimize_budget_allocation') as mock_allocation, \
             patch.object(optimizer, '_analyze_constraint_relaxation') as mock_relaxation, \
             patch.object(optimizer, '_generate_trade_off_analysis') as mock_trade_off:
            
            # Create proper model instances for mocks
            pareto_point = ParetoFrontierPoint(
                scenario_id="scenario_1",
                total_cost=30000.0,
                total_revenue=45000.0,
                roi_percentage=50.0,
                environmental_score=80.0,
                risk_score=70.0,
                yield_target_achievement=95.0,
                budget_utilization=90.0,
                trade_off_description="Profit-focused"
            )
            
            budget_allocation = BudgetAllocationResult(
                field_id="field_1",
                allocated_budget=15000.0,
                budget_utilization_percentage=90.0,
                nutrient_allocation={"N": 0.4, "P": 0.3, "K": 0.3},
                product_allocation={"urea_46_0_0": 0.5, "dap_18_46_0": 0.3, "potash_0_0_60": 0.2},
                expected_roi=45.0,
                priority_score=0.8,
                constraint_violations=[]
            )
            
            constraint_relaxation = ConstraintRelaxationAnalysis(
                constraint_type="total_budget_limit",
                original_value=50000.0,
                relaxed_value=60000.0,
                relaxation_impact={"roi_improvement": 5.0, "cost_increase": 10000.0},
                cost_of_relaxation=10000.0,
                benefit_of_relaxation=2500.0,
                recommendation="Consider relaxing budget constraint"
            )
            
            # Mock return values
            mock_pareto.return_value = [pareto_point]
            mock_scenario.return_value = pareto_point
            mock_allocation.return_value = [budget_allocation]
            mock_relaxation.return_value = [constraint_relaxation]
            mock_trade_off.return_value = {"correlations": {}, "trade_offs": []}
            
            result = await optimizer.optimize_budget_constraints(sample_request)
            
            assert isinstance(result, MultiObjectiveOptimizationResult)
            assert result.optimization_id is not None
            assert len(result.pareto_frontier) == 1
            assert len(result.budget_allocations) == 1
            assert len(result.constraint_relaxation_analysis) == 1
            assert result.trade_off_analysis is not None

    @pytest.mark.asyncio
    async def test_optimize_budget_constraints_validation_error(self, optimizer, sample_request):
        """Test budget constraint optimization with validation error."""
        # Remove budget constraint to trigger validation error
        sample_request.constraints.budget_constraint = None
        
        with pytest.raises(ValueError, match="Budget constraints are required"):
            await optimizer.optimize_budget_constraints(sample_request)

    @pytest.mark.asyncio
    async def test_generate_pareto_frontier(self, optimizer, sample_request):
        """Test Pareto frontier generation."""
        with patch.object(optimizer, '_optimize_scenario') as mock_scenario, \
             patch.object(optimizer, '_filter_pareto_frontier') as mock_filter:
            
            # Mock scenario optimization results
            mock_scenario.return_value = {
                "total_cost": 30000.0,
                "total_revenue": 45000.0,
                "roi_percentage": 50.0,
                "environmental_score": 80.0,
                "risk_score": 70.0,
                "yield_target_achievement": 95.0,
                "budget_utilization": 90.0
            }
            
            mock_filter.return_value = [MagicMock()]
            
            result = await optimizer._generate_pareto_frontier(sample_request)
            
            assert isinstance(result, list)
            assert len(result) == 1
            mock_scenario.assert_called()
            mock_filter.assert_called()

    @pytest.mark.asyncio
    async def test_optimize_scenario(self, optimizer, sample_request):
        """Test single scenario optimization."""
        objective_weights = {"profit": 1.0, "environment": 0.0, "risk": 0.0}
        
        with patch('scipy.optimize.minimize') as mock_minimize:
            # Mock successful optimization
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.x = [10.0, 15.0, 20.0, 25.0, 30.0, 35.0]
            mock_minimize.return_value = mock_result
            
            result = await optimizer._optimize_scenario(sample_request, objective_weights)
            
            assert isinstance(result, dict)
            assert "total_cost" in result
            assert "total_revenue" in result
            assert "roi_percentage" in result
            assert "environmental_score" in result
            assert "risk_score" in result
            assert "yield_target_achievement" in result
            assert "budget_utilization" in result

    @pytest.mark.asyncio
    async def test_optimize_scenario_failure(self, optimizer, sample_request):
        """Test scenario optimization failure handling."""
        objective_weights = {"profit": 1.0, "environment": 0.0, "risk": 0.0}
        
        with patch('scipy.optimize.minimize') as mock_minimize:
            # Mock failed optimization
            mock_result = MagicMock()
            mock_result.success = False
            mock_result.message = "Optimization failed"
            mock_minimize.return_value = mock_result
            
            result = await optimizer._optimize_scenario(sample_request, objective_weights)
            
            # Should return default values on failure
            assert result["total_cost"] == 0
            assert result["total_revenue"] == 0
            assert result["roi_percentage"] == 0

    @pytest.mark.asyncio
    async def test_select_recommended_scenario(self, optimizer, sample_goals):
        """Test recommended scenario selection."""
        pareto_frontier = [
            ParetoFrontierPoint(
                scenario_id="scenario_1",
                total_cost=30000.0,
                total_revenue=45000.0,
                roi_percentage=50.0,
                environmental_score=80.0,
                risk_score=70.0,
                yield_target_achievement=95.0,
                budget_utilization=90.0,
                trade_off_description="Profit-focused"
            ),
            ParetoFrontierPoint(
                scenario_id="scenario_2",
                total_cost=25000.0,
                total_revenue=40000.0,
                roi_percentage=60.0,
                environmental_score=70.0,
                risk_score=80.0,
                yield_target_achievement=90.0,
                budget_utilization=85.0,
                trade_off_description="Environment-focused"
            )
        ]
        
        result = await optimizer._select_recommended_scenario(pareto_frontier, sample_goals)
        
        assert isinstance(result, ParetoFrontierPoint)
        assert result.scenario_id in ["scenario_1", "scenario_2"]

    @pytest.mark.asyncio
    async def test_optimize_budget_allocation(self, optimizer, sample_request):
        """Test budget allocation optimization."""
        scenario = ParetoFrontierPoint(
            scenario_id="scenario_1",
            total_cost=30000.0,
            total_revenue=45000.0,
            roi_percentage=50.0,
            environmental_score=80.0,
            risk_score=70.0,
            yield_target_achievement=95.0,
            budget_utilization=90.0,
            trade_off_description="Profit-focused"
        )
        
        with patch.object(optimizer, '_calculate_field_priorities') as mock_priorities, \
             patch.object(optimizer, '_calculate_field_roi') as mock_roi, \
             patch.object(optimizer, '_check_field_constraint_violations') as mock_violations:
            
            mock_priorities.return_value = [0.6, 0.4]
            mock_roi.return_value = 45.0
            mock_violations.return_value = []
            
            result = await optimizer._optimize_budget_allocation(sample_request, scenario)
            
            assert isinstance(result, list)
            assert len(result) == 2  # Two fields
            assert all(isinstance(allocation, BudgetAllocationResult) for allocation in result)

    @pytest.mark.asyncio
    async def test_analyze_constraint_relaxation(self, optimizer, sample_request):
        """Test constraint relaxation analysis."""
        scenario = ParetoFrontierPoint(
            scenario_id="scenario_1",
            total_cost=30000.0,
            total_revenue=45000.0,
            roi_percentage=50.0,
            environmental_score=80.0,
            risk_score=70.0,
            yield_target_achievement=95.0,
            budget_utilization=90.0,
            trade_off_description="Profit-focused"
        )
        
        with patch.object(optimizer, '_analyze_budget_relaxation') as mock_budget, \
             patch.object(optimizer, '_analyze_nutrient_relaxation') as mock_nutrient, \
             patch.object(optimizer, '_analyze_per_acre_cost_relaxation') as mock_per_acre:
            
            mock_budget.return_value = MagicMock()
            mock_nutrient.return_value = MagicMock()
            mock_per_acre.return_value = MagicMock()
            
            result = await optimizer._analyze_constraint_relaxation(sample_request, scenario)
            
            assert isinstance(result, list)
            assert len(result) >= 1  # At least budget relaxation

    @pytest.mark.asyncio
    async def test_analyze_budget_relaxation(self, optimizer, sample_request):
        """Test budget constraint relaxation analysis."""
        scenario = ParetoFrontierPoint(
            scenario_id="scenario_1",
            total_cost=30000.0,
            total_revenue=45000.0,
            roi_percentage=50.0,
            environmental_score=80.0,
            risk_score=70.0,
            yield_target_achievement=95.0,
            budget_utilization=90.0,
            trade_off_description="Profit-focused"
        )
        
        with patch.object(optimizer, '_optimize_scenario') as mock_scenario:
            mock_scenario.return_value = {
                "roi_percentage": 60.0,
                "yield_target_achievement": 100.0
            }
            
            result = await optimizer._analyze_budget_relaxation(sample_request, scenario)
            
            assert isinstance(result, ConstraintRelaxationAnalysis)
            assert result.constraint_type == "total_budget_limit"
            assert result.original_value == 50000.0
            assert result.relaxed_value == 60000.0
            assert "roi_improvement" in result.relaxation_impact

    @pytest.mark.asyncio
    async def test_analyze_nutrient_relaxation(self, optimizer, sample_request):
        """Test nutrient rate constraint relaxation analysis."""
        scenario = ParetoFrontierPoint(
            scenario_id="scenario_1",
            total_cost=30000.0,
            total_revenue=45000.0,
            roi_percentage=50.0,
            environmental_score=80.0,
            risk_score=70.0,
            yield_target_achievement=95.0,
            budget_utilization=90.0,
            trade_off_description="Profit-focused"
        )
        
        with patch.object(optimizer, '_optimize_scenario') as mock_scenario:
            mock_scenario.return_value = {
                "roi_percentage": 55.0,
                "environmental_score": 75.0,
                "yield_target_achievement": 98.0
            }
            
            result = await optimizer._analyze_nutrient_relaxation(sample_request, scenario, "N", 200.0)
            
            assert isinstance(result, ConstraintRelaxationAnalysis)
            assert result.constraint_type == "max_nitrogen_rate"
            assert result.original_value == 200.0
            assert result.relaxed_value == 250.0
            assert "roi_improvement" in result.relaxation_impact

    @pytest.mark.asyncio
    async def test_generate_trade_off_analysis(self, optimizer, sample_goals):
        """Test trade-off analysis generation."""
        pareto_frontier = [
            ParetoFrontierPoint(
                scenario_id="scenario_1",
                total_cost=30000.0,
                total_revenue=45000.0,
                roi_percentage=50.0,
                environmental_score=80.0,
                risk_score=70.0,
                yield_target_achievement=95.0,
                budget_utilization=90.0,
                trade_off_description="Profit-focused"
            ),
            ParetoFrontierPoint(
                scenario_id="scenario_2",
                total_cost=25000.0,
                total_revenue=40000.0,
                roi_percentage=60.0,
                environmental_score=70.0,
                risk_score=80.0,
                yield_target_achievement=90.0,
                budget_utilization=85.0,
                trade_off_description="Environment-focused"
            )
        ]
        
        result = await optimizer._generate_trade_off_analysis(pareto_frontier, sample_goals)
        
        assert isinstance(result, dict)
        assert "correlations" in result
        assert "trade_offs" in result
        assert "efficiency_analysis" in result
        assert "recommendations" in result

    def test_filter_pareto_frontier(self, optimizer):
        """Test Pareto frontier filtering."""
        points = [
            ParetoFrontierPoint(
                scenario_id="scenario_1",
                total_cost=30000.0,
                total_revenue=45000.0,
                roi_percentage=50.0,
                environmental_score=80.0,
                risk_score=70.0,
                yield_target_achievement=95.0,
                budget_utilization=90.0,
                trade_off_description="Profit-focused"
            ),
            ParetoFrontierPoint(
                scenario_id="scenario_2",
                total_cost=25000.0,
                total_revenue=40000.0,
                roi_percentage=60.0,
                environmental_score=70.0,
                risk_score=80.0,
                yield_target_achievement=90.0,
                budget_utilization=85.0,
                trade_off_description="Environment-focused"
            )
        ]
        
        result = optimizer._filter_pareto_frontier(points)
        
        assert isinstance(result, list)
        assert len(result) <= len(points)

    def test_generate_trade_off_description(self, optimizer):
        """Test trade-off description generation."""
        weights = {"profit": 0.8, "environment": 0.2, "risk": 0.0}
        result = optimizer._generate_trade_off_description(weights)
        
        assert isinstance(result, str)
        assert "Profit-focused" in result

    def test_calculate_field_priorities(self, optimizer, sample_fields, sample_goals):
        """Test field priority calculation."""
        result = optimizer._calculate_field_priorities(sample_fields, sample_goals)
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(0 <= priority <= 1 for priority in result)

    def test_calculate_field_roi(self, optimizer, sample_fields, sample_products):
        """Test field ROI calculation."""
        field = sample_fields[0]
        budget = 10000.0
        
        result = optimizer._calculate_field_roi(field, budget, sample_products)
        
        assert isinstance(result, float)
        assert result >= 0

    def test_check_field_constraint_violations(self, optimizer, sample_fields, sample_constraints):
        """Test field constraint violation checking."""
        field = sample_fields[0]
        budget = 30000.0
        
        result = optimizer._check_field_constraint_violations(field, budget, sample_constraints)
        
        assert isinstance(result, list)
        assert all(isinstance(violation, str) for violation in result)

    def test_calculate_yield_response(self, optimizer, sample_fields, sample_products):
        """Test yield response calculation."""
        field = sample_fields[0]
        product = sample_products[0]
        
        result = optimizer._calculate_yield_response(field, product)
        
        assert isinstance(result, float)
        assert result >= 0

    def test_calculate_environmental_impact(self, optimizer, sample_fields, sample_products):
        """Test environmental impact calculation."""
        field = sample_fields[0]
        product = sample_products[0]
        rate = 100.0
        
        result = optimizer._calculate_environmental_impact(product, rate, field)
        
        assert isinstance(result, float)
        assert result >= 0

    def test_calculate_risk_factor(self, optimizer, sample_fields, sample_products):
        """Test risk factor calculation."""
        field = sample_fields[0]
        product = sample_products[0]
        rate = 100.0
        
        result = optimizer._calculate_risk_factor(product, rate, field)
        
        assert isinstance(result, float)
        assert result >= 0

    def test_validate_budget_constraints_valid(self, optimizer, sample_request):
        """Test budget constraint validation with valid constraints."""
        # Should not raise any exception
        optimizer._validate_budget_constraints(sample_request)

    def test_validate_budget_constraints_invalid_total_budget(self, optimizer, sample_request):
        """Test budget constraint validation with invalid total budget."""
        sample_request.constraints.budget_constraint.total_budget_limit = -1000.0
        
        with pytest.raises(ValueError, match="Total budget limit must be positive"):
            optimizer._validate_budget_constraints(sample_request)

    def test_validate_budget_constraints_invalid_per_field_budget(self, optimizer, sample_request):
        """Test budget constraint validation with invalid per-field budget."""
        sample_request.constraints.budget_constraint.per_field_budget_limit = -500.0
        
        with pytest.raises(ValueError, match="Per-field budget limit must be positive"):
            optimizer._validate_budget_constraints(sample_request)

    def test_validate_budget_constraints_invalid_per_acre_budget(self, optimizer, sample_request):
        """Test budget constraint validation with invalid per-acre budget."""
        sample_request.constraints.budget_constraint.per_acre_budget_limit = -50.0
        
        with pytest.raises(ValueError, match="Per-acre budget limit must be positive"):
            optimizer._validate_budget_constraints(sample_request)

    def test_validate_budget_constraints_invalid_flexibility_percentage(self, optimizer, sample_request):
        """Test budget constraint validation with invalid flexibility percentage."""
        sample_request.constraints.budget_constraint.budget_flexibility_percentage = 75.0
        
        with pytest.raises(ValueError, match="Budget flexibility percentage must be between 0 and 50"):
            optimizer._validate_budget_constraints(sample_request)

    def test_validate_budget_constraints_invalid_utilization_target(self, optimizer, sample_request):
        """Test budget constraint validation with invalid utilization target."""
        sample_request.constraints.budget_constraint.budget_utilization_target = 50.0
        
        with pytest.raises(ValueError, match="Budget utilization target must be between 80 and 100"):
            optimizer._validate_budget_constraints(sample_request)


class TestBudgetConstraintOptimizerIntegration:
    """Integration tests for budget constraint optimizer."""

    @pytest.fixture
    def optimizer(self):
        """Create optimizer instance for testing."""
        return BudgetConstraintOptimizer()

    @pytest.fixture
    def realistic_request(self):
        """Create realistic optimization request for integration testing."""
        fields = [
            FieldData(
                field_id="field_1",
                acres=200.0,
                soil_tests={"N": 45, "P": 18, "K": 140},
                crop_plan={"crop": "corn", "variety": "hybrid"},
                target_yield=190.0,
                crop_price=5.75,
                historical_yield=185.0
            ),
            FieldData(
                field_id="field_2",
                acres=180.0,
                soil_tests={"N": 35, "P": 12, "K": 110},
                crop_plan={"crop": "soybean", "variety": "roundup_ready"},
                target_yield=55.0,
                crop_price=13.50,
                historical_yield=52.0
            )
        ]
        
        products = [
            FertilizerProduct(
                product_id="urea_46_0_0",
                product_name="Urea 46-0-0",
                nutrient_content={"N": 46, "P": 0, "K": 0},
                price_per_unit=520.0,
                unit="ton",
                application_method="broadcast"
            ),
            FertilizerProduct(
                product_id="dap_18_46_0",
                product_name="DAP 18-46-0",
                nutrient_content={"N": 18, "P": 46, "K": 0},
                price_per_unit=650.0,
                unit="ton",
                application_method="broadcast"
            ),
            FertilizerProduct(
                product_id="potash_0_0_60",
                product_name="Potash 0-0-60",
                nutrient_content={"N": 0, "P": 0, "K": 60},
                price_per_unit=420.0,
                unit="ton",
                application_method="broadcast"
            )
        ]
        
        budget_constraint = BudgetConstraint(
            total_budget_limit=75000.0,
            per_field_budget_limit=45000.0,
            per_acre_budget_limit=250.0,
            nutrient_budget_allocation={"N": 0.5, "P": 0.3, "K": 0.2},
            budget_flexibility_percentage=12.0,
            allow_budget_reallocation=True,
            budget_utilization_target=92.0
        )
        
        constraints = OptimizationConstraints(
            max_nitrogen_rate=180.0,
            max_phosphorus_rate=80.0,
            max_potassium_rate=120.0,
            budget_constraint=budget_constraint,
            max_per_acre_cost=300.0
        )
        
        goals = OptimizationGoals(
            primary_goal="profit_maximization",
            yield_priority=0.85,
            cost_priority=0.75,
            environmental_priority=0.65,
            risk_tolerance=RiskTolerance.MODERATE
        )
        
        return ROIOptimizationRequest(
            farm_context={"farm_id": "integration_test", "region": "corn_belt"},
            fields=fields,
            fertilizer_products=products,
            constraints=constraints,
            goals=goals,
            include_sensitivity_analysis=True,
            include_risk_assessment=True
        )

    @pytest.mark.asyncio
    async def test_full_optimization_workflow(self, optimizer, realistic_request):
        """Test complete optimization workflow with realistic data."""
        result = await optimizer.optimize_budget_constraints(realistic_request)
        
        # Verify result structure
        assert isinstance(result, MultiObjectiveOptimizationResult)
        assert result.optimization_id is not None
        assert len(result.pareto_frontier) > 0
        assert len(result.budget_allocations) == 2  # Two fields
        assert len(result.constraint_relaxation_analysis) > 0
        assert result.trade_off_analysis is not None
        
        # Verify Pareto frontier quality
        for point in result.pareto_frontier:
            assert point.roi_percentage >= 0
            assert point.environmental_score >= 0
            assert point.risk_score >= 0
            assert point.budget_utilization >= 0
        
        # Verify budget allocations
        for allocation in result.budget_allocations:
            assert allocation.allocated_budget > 0
            assert allocation.budget_utilization_percentage >= 0
            assert allocation.expected_roi >= 0
            assert allocation.priority_score >= 0
        
        # Verify constraint relaxation analysis
        for analysis in result.constraint_relaxation_analysis:
            assert analysis.original_value > 0
            assert analysis.relaxed_value > analysis.original_value
            assert analysis.recommendation is not None

    @pytest.mark.asyncio
    async def test_scenario_comparison(self, optimizer, realistic_request):
        """Test scenario comparison and selection."""
        result = await optimizer.optimize_budget_constraints(realistic_request)
        
        # Verify recommended scenario selection
        assert result.recommended_scenario is not None
        assert result.recommended_scenario.scenario_id in [p.scenario_id for p in result.pareto_frontier]
        
        # Verify trade-off analysis
        trade_off_analysis = result.trade_off_analysis
        assert "correlations" in trade_off_analysis
        assert "trade_offs" in trade_off_analysis
        assert "efficiency_analysis" in trade_off_analysis
        assert "recommendations" in trade_off_analysis

    @pytest.mark.asyncio
    async def test_budget_allocation_optimization(self, optimizer, realistic_request):
        """Test budget allocation optimization with realistic constraints."""
        result = await optimizer.optimize_budget_constraints(realistic_request)
        
        # Verify budget allocation respects constraints
        total_allocated = sum(allocation.allocated_budget for allocation in result.budget_allocations)
        budget_limit = realistic_request.constraints.budget_constraint.total_budget_limit
        
        assert total_allocated <= budget_limit * 1.1  # Allow some tolerance
        
        # Verify per-field constraints
        for allocation in result.budget_allocations:
            per_field_limit = realistic_request.constraints.budget_constraint.per_field_budget_limit
            assert allocation.allocated_budget <= per_field_limit * 1.1  # Allow some tolerance

    @pytest.mark.asyncio
    async def test_constraint_relaxation_benefits(self, optimizer, realistic_request):
        """Test constraint relaxation analysis with realistic scenarios."""
        result = await optimizer.optimize_budget_constraints(realistic_request)
        
        # Verify constraint relaxation analysis provides meaningful insights
        for analysis in result.constraint_relaxation_analysis:
            assert analysis.relaxation_impact is not None
            assert "roi_improvement" in analysis.relaxation_impact
            assert "cost_increase" in analysis.relaxation_impact or "environmental_impact" in analysis.relaxation_impact
            assert analysis.recommendation is not None and len(analysis.recommendation) > 0
