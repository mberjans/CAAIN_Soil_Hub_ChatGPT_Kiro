"""
Comprehensive tests for yield goal optimization service.

This module provides comprehensive test coverage for:
- Yield goal optimization with economic constraints
- Goal-oriented fertilizer planning
- Risk-adjusted optimization and scenario analysis
- Multi-criteria optimization algorithms
- Integration with yield response curves and economic analysis
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from datetime import datetime

from ..models.yield_goal_models import (
    YieldGoalRequest, YieldGoalAnalysis, YieldGoalRecommendation,
    YieldGoalType, YieldRiskLevel, HistoricalYieldData,
    SoilCharacteristic, WeatherPattern, ManagementPractice
)
from ..models.yield_response_models import (
    YieldResponseCurve, NutrientResponseData, ResponseModelType
)
from ..models.price_models import FertilizerPriceData
from ..services.yield_goal_optimization_service import (
    YieldGoalOptimizationService, YieldGoalOptimizationRequest,
    YieldGoalOptimizationResponse, OptimizationObjective, OptimizationMethod,
    OptimizationConstraints, OptimizationScenario, ScenarioType,
    FertilizerStrategy
)


class TestYieldGoalOptimizationService:
    """Comprehensive test suite for yield goal optimization service."""
    
    @pytest.fixture
    def service(self):
        """Create yield goal optimization service instance."""
        return YieldGoalOptimizationService()
    
    @pytest.fixture
    def sample_yield_response_curves(self):
        """Create sample yield response curves."""
        field_id = uuid4()
        return [
            YieldResponseCurve(
                curve_id=uuid4(),
                field_id=field_id,
                crop_type="corn",
                nutrient_type="nitrogen",
                curve_type=ResponseModelType.QUADRATIC_PLATEAU,
                base_yield=100.0,
                max_yield_response=80.0,
                response_coefficient=0.8,
                diminishing_returns_coefficient=0.001,
                confidence_level=0.8,
                data_points=[],
                model_parameters={}
            ),
            YieldResponseCurve(
                curve_id=uuid4(),
                field_id=field_id,
                crop_type="corn",
                nutrient_type="phosphorus",
                curve_type=ResponseModelType.QUADRATIC_PLATEAU,
                base_yield=100.0,
                max_yield_response=40.0,
                response_coefficient=0.6,
                diminishing_returns_coefficient=0.002,
                confidence_level=0.7,
                data_points=[],
                model_parameters={}
            ),
            YieldResponseCurve(
                curve_id=uuid4(),
                field_id=field_id,
                crop_type="corn",
                nutrient_type="potassium",
                curve_type=ResponseModelType.QUADRATIC_PLATEAU,
                base_yield=100.0,
                max_yield_response=30.0,
                response_coefficient=0.4,
                diminishing_returns_coefficient=0.0015,
                confidence_level=0.6,
                data_points=[],
                model_parameters={}
            )
        ]
    
    @pytest.fixture
    def sample_fertilizer_prices(self):
        """Create sample fertilizer price data."""
        return [
            FertilizerPriceData(
                fertilizer_type="nitrogen",
                price_per_unit=0.80,
                unit="lb",
                region="default",
                source="default",
                price_date="2024-01-01"
            ),
            FertilizerPriceData(
                fertilizer_type="phosphorus",
                price_per_unit=0.60,
                unit="lb",
                region="default",
                source="default",
                price_date="2024-01-01"
            ),
            FertilizerPriceData(
                fertilizer_type="potassium",
                price_per_unit=0.50,
                unit="lb",
                region="default",
                source="default",
                price_date="2024-01-01"
            )
        ]
    
    @pytest.fixture
    def sample_optimization_scenarios(self):
        """Create sample optimization scenarios."""
        return [
            OptimizationScenario(
                scenario_type=ScenarioType.BASELINE,
                yield_goal=200.0,
                price_scenario={
                    'nitrogen': 0.80,
                    'phosphorus': 0.60,
                    'potassium': 0.50
                },
                risk_tolerance=YieldRiskLevel.MEDIUM,
                probability_weight=1.0
            )
        ]
    
    @pytest.fixture
    def sample_optimization_request(
        self,
        sample_yield_response_curves,
        sample_fertilizer_prices,
        sample_optimization_scenarios
    ):
        """Create sample optimization request."""
        return YieldGoalOptimizationRequest(
            field_id=uuid4(),
            crop_type="corn",
            yield_goal=200.0,
            optimization_objective=OptimizationObjective.BALANCED,
            optimization_method=OptimizationMethod.MULTI_CRITERIA,
            constraints=OptimizationConstraints(
                max_nitrogen_rate=300.0,
                max_phosphorus_rate=150.0,
                max_potassium_rate=200.0,
                budget_limit=200.0
            ),
            scenarios=sample_optimization_scenarios,
            yield_response_curves=sample_yield_response_curves,
            fertilizer_prices=sample_fertilizer_prices,
            crop_price=5.50
        )
    
    @pytest.mark.asyncio
    async def test_optimize_yield_goals_comprehensive(self, service, sample_optimization_request):
        """Test comprehensive yield goal optimization."""
        response = await service.optimize_yield_goals(sample_optimization_request)
        
        # Validate response structure
        assert response.success is True
        assert response.message is not None
        assert len(response.optimization_results) == 1
        assert response.best_strategy is not None
        assert isinstance(response.risk_assessment, dict)
        assert isinstance(response.recommendations, list)
        assert isinstance(response.metadata, dict)
        
        # Validate optimization result
        result = response.optimization_results[0]
        assert result.optimization_id is not None
        assert result.scenario is not None
        assert result.optimal_strategy is not None
        assert result.expected_yield > 0
        assert 0.0 <= result.yield_probability <= 1.0
        assert result.expected_profit is not None
        assert 0.0 <= result.profit_probability <= 1.0
        assert isinstance(result.risk_metrics, dict)
        assert isinstance(result.sensitivity_analysis, dict)
        assert isinstance(result.optimization_metadata, dict)
        
        # Validate optimal strategy
        strategy = result.optimal_strategy
        assert strategy.nitrogen_rate >= 0
        assert strategy.phosphorus_rate >= 0
        assert strategy.potassium_rate >= 0
        assert strategy.total_cost >= 0
        assert strategy.application_method is not None
    
    @pytest.mark.asyncio
    async def test_goal_programming_optimization(self, service, sample_optimization_request):
        """Test goal programming optimization method."""
        sample_optimization_request.optimization_method = OptimizationMethod.GOAL_PROGRAMMING
        
        response = await service.optimize_yield_goals(sample_optimization_request)
        
        assert response.success is True
        assert len(response.optimization_results) == 1
        
        result = response.optimization_results[0]
        assert result.optimal_strategy is not None
        assert result.expected_yield > 0
        assert result.expected_profit is not None
    
    @pytest.mark.asyncio
    async def test_multi_criteria_optimization(self, service, sample_optimization_request):
        """Test multi-criteria optimization method."""
        sample_optimization_request.optimization_method = OptimizationMethod.MULTI_CRITERIA
        
        response = await service.optimize_yield_goals(sample_optimization_request)
        
        assert response.success is True
        assert len(response.optimization_results) == 1
        
        result = response.optimization_results[0]
        assert result.optimal_strategy is not None
        assert result.expected_yield > 0
        assert result.expected_profit is not None
    
    @pytest.mark.asyncio
    async def test_robust_optimization(self, service, sample_optimization_request):
        """Test robust optimization method."""
        sample_optimization_request.optimization_method = OptimizationMethod.ROBUST_OPTIMIZATION
        
        response = await service.optimize_yield_goals(sample_optimization_request)
        
        assert response.success is True
        assert len(response.optimization_results) == 1
        
        result = response.optimization_results[0]
        assert result.optimal_strategy is not None
        assert result.expected_yield > 0
        assert result.expected_profit is not None
    
    @pytest.mark.asyncio
    async def test_stochastic_optimization(self, service, sample_optimization_request):
        """Test stochastic optimization method."""
        sample_optimization_request.optimization_method = OptimizationMethod.STOCHASTIC
        
        response = await service.optimize_yield_goals(sample_optimization_request)
        
        assert response.success is True
        assert len(response.optimization_results) == 1
        
        result = response.optimization_results[0]
        assert result.optimal_strategy is not None
        assert result.expected_yield > 0
        assert result.expected_profit is not None
    
    @pytest.mark.asyncio
    async def test_genetic_algorithm_optimization(self, service, sample_optimization_request):
        """Test genetic algorithm optimization method."""
        sample_optimization_request.optimization_method = OptimizationMethod.GENETIC_ALGORITHM
        
        response = await service.optimize_yield_goals(sample_optimization_request)
        
        assert response.success is True
        assert len(response.optimization_results) == 1
        
        result = response.optimization_results[0]
        assert result.optimal_strategy is not None
        assert result.expected_yield > 0
        assert result.expected_profit is not None
    
    @pytest.mark.asyncio
    async def test_different_optimization_objectives(self, service, sample_optimization_request):
        """Test different optimization objectives."""
        objectives = [
            OptimizationObjective.MAXIMIZE_PROFIT,
            OptimizationObjective.MINIMIZE_COST,
            OptimizationObjective.MAXIMIZE_YIELD,
            OptimizationObjective.MINIMIZE_RISK,
            OptimizationObjective.BALANCED
        ]
        
        for objective in objectives:
            sample_optimization_request.optimization_objective = objective
            
            response = await service.optimize_yield_goals(sample_optimization_request)
            
            assert response.success is True
            assert len(response.optimization_results) == 1
            
            result = response.optimization_results[0]
            assert result.optimal_strategy is not None
            assert result.expected_yield > 0
            assert result.expected_profit is not None
    
    @pytest.mark.asyncio
    async def test_multiple_scenarios_optimization(self, service, sample_yield_response_curves, sample_fertilizer_prices):
        """Test optimization with multiple scenarios."""
        scenarios = [
            OptimizationScenario(
                scenario_type=ScenarioType.BASELINE,
                yield_goal=200.0,
                price_scenario={'nitrogen': 0.80, 'phosphorus': 0.60, 'potassium': 0.50},
                risk_tolerance=YieldRiskLevel.MEDIUM,
                probability_weight=0.5
            ),
            OptimizationScenario(
                scenario_type=ScenarioType.OPTIMISTIC,
                yield_goal=220.0,
                price_scenario={'nitrogen': 0.70, 'phosphorus': 0.50, 'potassium': 0.40},
                risk_tolerance=YieldRiskLevel.LOW,
                probability_weight=0.3
            ),
            OptimizationScenario(
                scenario_type=ScenarioType.PESSIMISTIC,
                yield_goal=180.0,
                price_scenario={'nitrogen': 0.90, 'phosphorus': 0.70, 'potassium': 0.60},
                risk_tolerance=YieldRiskLevel.HIGH,
                probability_weight=0.2
            )
        ]
        
        request = YieldGoalOptimizationRequest(
            field_id=uuid4(),
            crop_type="corn",
            yield_goal=200.0,
            optimization_objective=OptimizationObjective.BALANCED,
            optimization_method=OptimizationMethod.MULTI_CRITERIA,
            constraints=OptimizationConstraints(
                max_nitrogen_rate=300.0,
                max_phosphorus_rate=150.0,
                max_potassium_rate=200.0,
                budget_limit=200.0
            ),
            scenarios=scenarios,
            yield_response_curves=sample_yield_response_curves,
            fertilizer_prices=sample_fertilizer_prices,
            crop_price=5.50
        )
        
        response = await service.optimize_yield_goals(request)
        
        assert response.success is True
        assert len(response.optimization_results) == 3
        assert response.best_strategy is not None
        assert isinstance(response.risk_assessment, dict)
        assert len(response.recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_constraint_handling(self, service, sample_optimization_request):
        """Test optimization with various constraints."""
        # Test budget constraint
        sample_optimization_request.constraints.budget_limit = 100.0  # Low budget
        
        response = await service.optimize_yield_goals(sample_optimization_request)
        
        assert response.success is True
        result = response.optimization_results[0]
        assert result.optimal_strategy.total_cost <= 100.0
        
        # Test rate constraints
        sample_optimization_request.constraints.max_nitrogen_rate = 50.0  # Low N limit
        
        response = await service.optimize_yield_goals(sample_optimization_request)
        
        assert response.success is True
        result = response.optimization_results[0]
        assert result.optimal_strategy.nitrogen_rate <= 50.0
    
    @pytest.mark.asyncio
    async def test_yield_calculation_from_rates(self, service, sample_yield_response_curves):
        """Test yield calculation from fertilizer rates."""
        yield_val = service._calculate_yield_from_rates(100.0, 50.0, 75.0, sample_yield_response_curves)
        
        assert yield_val > 0
        assert yield_val > 100.0  # Should be above base yield
    
    @pytest.mark.asyncio
    async def test_response_curve_evaluation(self, service):
        """Test response curve evaluation methods."""
        curve = YieldResponseCurve(
            curve_id=uuid4(),
            field_id=uuid4(),
            crop_type="corn",
            nutrient_type="nitrogen",
            curve_type=ResponseCurveType.QUADRATIC_PLATEAU,
            base_yield=100.0,
            max_yield_response=80.0,
            response_coefficient=0.8,
            diminishing_returns_coefficient=0.001,
            confidence_level=0.8,
            data_points=[],
            model_parameters={}
        )
        
        # Test different curve types
        yield_val = service._evaluate_response_curve(curve, 100.0)
        assert yield_val > 0
        
        # Test Mitscherlich-Baule
        curve.curve_type = ResponseModelType.MITSCHERLICH_BAULE
        yield_val = service._evaluate_response_curve(curve, 100.0)
        assert yield_val > 0
        
        # Test linear plateau
        curve.curve_type = ResponseModelType.LINEAR_PLATEAU
        yield_val = service._evaluate_response_curve(curve, 100.0)
        assert yield_val > 0
        
        # Test exponential
        curve.curve_type = ResponseModelType.EXPONENTIAL
        yield_val = service._evaluate_response_curve(curve, 100.0)
        assert yield_val > 0
    
    @pytest.mark.asyncio
    async def test_fertilizer_cost_calculation(self, service):
        """Test fertilizer cost calculation."""
        price_scenario = {
            'nitrogen': 0.80,
            'phosphorus': 0.60,
            'potassium': 0.50
        }
        
        cost = service._calculate_fertilizer_cost(100.0, 50.0, 75.0, price_scenario)
        
        expected_cost = (100.0 * 0.80) + (50.0 * 0.60) + (75.0 * 0.50)
        assert cost == expected_cost
        assert cost > 0
    
    @pytest.mark.asyncio
    async def test_yield_probability_calculation(self, service):
        """Test yield probability calculation."""
        probability = await service._calculate_yield_probability(200.0, 200.0)
        assert 0.0 <= probability <= 1.0
        
        # Higher expected yield should have higher probability
        probability_higher = await service._calculate_yield_probability(220.0, 200.0)
        assert probability_higher > probability
    
    @pytest.mark.asyncio
    async def test_profit_probability_calculation(self, service):
        """Test profit probability calculation."""
        probability = await service._calculate_profit_probability(100.0)
        assert 0.0 <= probability <= 1.0
        
        # Higher expected profit should have higher probability
        probability_higher = await service._calculate_profit_probability(200.0)
        assert probability_higher > probability
    
    @pytest.mark.asyncio
    async def test_risk_metrics_calculation(self, service):
        """Test risk metrics calculation."""
        strategy = FertilizerStrategy(
            nitrogen_rate=100.0,
            phosphorus_rate=50.0,
            potassium_rate=75.0,
            total_cost=150.0,
            application_method="broadcast"
        )
        
        risk_metrics = await service._calculate_risk_metrics(strategy, 200.0, 100.0)
        
        assert isinstance(risk_metrics, dict)
        assert "yield_volatility" in risk_metrics
        assert "profit_volatility" in risk_metrics
        assert "value_at_risk_95" in risk_metrics
        assert "conditional_value_at_risk" in risk_metrics
        assert "sharpe_ratio" in risk_metrics
        
        assert risk_metrics["yield_volatility"] > 0
        assert risk_metrics["profit_volatility"] > 0
    
    @pytest.mark.asyncio
    async def test_sensitivity_analysis(self, service, sample_optimization_request, sample_optimization_scenarios):
        """Test sensitivity analysis."""
        strategy = FertilizerStrategy(
            nitrogen_rate=100.0,
            phosphorus_rate=50.0,
            potassium_rate=75.0,
            total_cost=150.0,
            application_method="broadcast"
        )
        
        sensitivity = await service._perform_sensitivity_analysis(
            strategy, sample_optimization_request, sample_optimization_scenarios[0]
        )
        
        assert isinstance(sensitivity, dict)
        assert "price_sensitivity" in sensitivity
        assert "yield_sensitivity" in sensitivity
        assert "base_yield" in sensitivity
        assert "base_profit" in sensitivity
        
        assert isinstance(sensitivity["price_sensitivity"], dict)
        assert isinstance(sensitivity["yield_sensitivity"], dict)
    
    @pytest.mark.asyncio
    async def test_best_strategy_determination(self, service):
        """Test best strategy determination."""
        # Create mock optimization results
        results = []
        for i in range(3):
            result = type('OptimizationResult', (), {
                'optimal_strategy': FertilizerStrategy(
                    nitrogen_rate=100.0 + i * 10,
                    phosphorus_rate=50.0 + i * 5,
                    potassium_rate=75.0 + i * 5,
                    total_cost=150.0 + i * 10,
                    application_method="broadcast"
                ),
                'yield_probability': 0.8 - i * 0.1,
                'profit_probability': 0.7 - i * 0.1,
                'risk_metrics': {'yield_volatility': 10.0 + i * 5}
            })()
            results.append(result)
        
        best_strategy = await service._determine_best_strategy(results, sample_optimization_request)
        
        assert best_strategy is not None
        assert isinstance(best_strategy, FertilizerStrategy)
    
    @pytest.mark.asyncio
    async def test_risk_assessment(self, service):
        """Test risk assessment across scenarios."""
        # Create mock optimization results
        results = []
        for i in range(3):
            result = type('OptimizationResult', (), {
                'expected_yield': 200.0 + i * 10,
                'expected_profit': 100.0 + i * 20,
                'yield_probability': 0.8 - i * 0.1,
                'profit_probability': 0.7 - i * 0.1,
                'optimal_strategy': FertilizerStrategy(
                    nitrogen_rate=100.0,
                    phosphorus_rate=50.0,
                    potassium_rate=75.0,
                    total_cost=150.0,
                    application_method="broadcast"
                ),
                'scenario': type('Scenario', (), {
                    'probability_weight': 0.33
                })()
            })()
            results.append(result)
        
        risk_assessment = await service._assess_optimization_risk(results, sample_optimization_request)
        
        assert isinstance(risk_assessment, dict)
        assert "overall_risk_level" in risk_assessment
        assert "weighted_yield_probability" in risk_assessment
        assert "weighted_profit_probability" in risk_assessment
        assert "yield_volatility" in risk_assessment
        assert "profit_volatility" in risk_assessment
        assert "scenario_count" in risk_assessment
        assert "risk_factors" in risk_assessment
    
    @pytest.mark.asyncio
    async def test_recommendation_generation(self, service):
        """Test recommendation generation."""
        # Create mock optimization results
        results = []
        for i in range(2):
            result = type('OptimizationResult', (), {
                'optimal_strategy': FertilizerStrategy(
                    nitrogen_rate=100.0 + i * 10,
                    phosphorus_rate=50.0 + i * 5,
                    potassium_rate=75.0 + i * 5,
                    total_cost=150.0 + i * 10,
                    application_method="broadcast"
                ),
                'yield_probability': 0.8 - i * 0.1,
                'profit_probability': 0.7 - i * 0.1
            })()
            results.append(result)
        
        best_strategy = FertilizerStrategy(
            nitrogen_rate=110.0,
            phosphorus_rate=55.0,
            potassium_rate=80.0,
            total_cost=160.0,
            application_method="broadcast"
        )
        
        risk_assessment = {
            "overall_risk_level": "medium",
            "weighted_yield_probability": 0.75,
            "weighted_profit_probability": 0.65
        }
        
        recommendations = await service._generate_optimization_recommendations(
            results, best_strategy, risk_assessment
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Check for specific recommendation types
        recommendation_text = " ".join(recommendations)
        assert "nitrogen rate" in recommendation_text.lower()
        assert "phosphorus rate" in recommendation_text.lower()
        assert "potassium rate" in recommendation_text.lower()
    
    @pytest.mark.asyncio
    async def test_validation_error_handling(self, service):
        """Test validation error handling."""
        # Test with empty scenarios
        request = YieldGoalOptimizationRequest(
            field_id=uuid4(),
            crop_type="corn",
            yield_goal=200.0,
            optimization_objective=OptimizationObjective.BALANCED,
            optimization_method=OptimizationMethod.MULTI_CRITERIA,
            constraints=OptimizationConstraints(),
            scenarios=[],  # Empty scenarios
            yield_response_curves=[],
            fertilizer_prices=[],
            crop_price=5.50
        )
        
        with pytest.raises(ValueError, match="At least one optimization scenario is required"):
            await service.optimize_yield_goals(request)
        
        # Test with invalid crop price
        request.scenarios = [OptimizationScenario(
            scenario_type=ScenarioType.BASELINE,
            yield_goal=200.0,
            price_scenario={'nitrogen': 0.80},
            risk_tolerance=YieldRiskLevel.MEDIUM,
            probability_weight=1.0
        )]
        request.crop_price = -1.0  # Invalid price
        
        with pytest.raises(ValueError, match="Crop price must be positive"):
            await service.optimize_yield_goals(request)
    
    @pytest.mark.asyncio
    async def test_edge_cases(self, service, sample_optimization_request):
        """Test edge cases and boundary conditions."""
        # Test with very low yield goal
        sample_optimization_request.yield_goal = 50.0
        sample_optimization_request.scenarios[0].yield_goal = 50.0
        
        response = await service.optimize_yield_goals(sample_optimization_request)
        assert response.success is True
        
        # Test with very high yield goal
        sample_optimization_request.yield_goal = 500.0
        sample_optimization_request.scenarios[0].yield_goal = 500.0
        
        response = await service.optimize_yield_goals(sample_optimization_request)
        assert response.success is True
        
        # Test with very low budget
        sample_optimization_request.constraints.budget_limit = 10.0
        
        response = await service.optimize_yield_goals(sample_optimization_request)
        assert response.success is True
        
        result = response.optimization_results[0]
        assert result.optimal_strategy.total_cost <= 10.0


class TestYieldGoalOptimizationIntegration:
    """Integration tests for yield goal optimization service."""
    
    @pytest.fixture
    def service(self):
        """Create yield goal optimization service instance."""
        return YieldGoalOptimizationService()
    
    @pytest.mark.asyncio
    async def test_end_to_end_optimization(self, service):
        """Test complete end-to-end yield goal optimization."""
        # Create comprehensive test data
        field_id = uuid4()
        
        yield_response_curves = [
            YieldResponseCurve(
                curve_id=uuid4(),
                field_id=field_id,
                crop_type="corn",
                nutrient_type="nitrogen",
                curve_type=ResponseModelType.QUADRATIC_PLATEAU,
                base_yield=120.0,
                max_yield_response=100.0,
                response_coefficient=1.0,
                diminishing_returns_coefficient=0.0008,
                confidence_level=0.9,
                data_points=[],
                model_parameters={}
            ),
            YieldResponseCurve(
                curve_id=uuid4(),
                field_id=field_id,
                crop_type="corn",
                nutrient_type="phosphorus",
                curve_type=ResponseModelType.QUADRATIC_PLATEAU,
                base_yield=120.0,
                max_yield_response=50.0,
                response_coefficient=0.8,
                diminishing_returns_coefficient=0.0015,
                confidence_level=0.8,
                data_points=[],
                model_parameters={}
            ),
            YieldResponseCurve(
                curve_id=uuid4(),
                field_id=field_id,
                crop_type="corn",
                nutrient_type="potassium",
                curve_type=ResponseModelType.QUADRATIC_PLATEAU,
                base_yield=120.0,
                max_yield_response=40.0,
                response_coefficient=0.6,
                diminishing_returns_coefficient=0.0012,
                confidence_level=0.7,
                data_points=[],
                model_parameters={}
            )
        ]
        
        fertilizer_prices = [
            FertilizerPriceData(
                fertilizer_type="nitrogen",
                price_per_unit=0.75,
                unit="lb",
                region="test",
                source="test",
                price_date="2024-01-01"
            ),
            FertilizerPriceData(
                fertilizer_type="phosphorus",
                price_per_unit=0.55,
                unit="lb",
                region="test",
                source="test",
                price_date="2024-01-01"
            ),
            FertilizerPriceData(
                fertilizer_type="potassium",
                price_per_unit=0.45,
                unit="lb",
                region="test",
                source="test",
                price_date="2024-01-01"
            )
        ]
        
        scenarios = [
            OptimizationScenario(
                scenario_type=ScenarioType.BASELINE,
                yield_goal=250.0,
                price_scenario={'nitrogen': 0.75, 'phosphorus': 0.55, 'potassium': 0.45},
                risk_tolerance=YieldRiskLevel.MEDIUM,
                probability_weight=0.6
            ),
            OptimizationScenario(
                scenario_type=ScenarioType.OPTIMISTIC,
                yield_goal=275.0,
                price_scenario={'nitrogen': 0.65, 'phosphorus': 0.45, 'potassium': 0.35},
                risk_tolerance=YieldRiskLevel.LOW,
                probability_weight=0.25
            ),
            OptimizationScenario(
                scenario_type=ScenarioType.PESSIMISTIC,
                yield_goal=225.0,
                price_scenario={'nitrogen': 0.85, 'phosphorus': 0.65, 'potassium': 0.55},
                risk_tolerance=YieldRiskLevel.HIGH,
                probability_weight=0.15
            )
        ]
        
        request = YieldGoalOptimizationRequest(
            field_id=field_id,
            crop_type="corn",
            yield_goal=250.0,
            optimization_objective=OptimizationObjective.BALANCED,
            optimization_method=OptimizationMethod.MULTI_CRITERIA,
            constraints=OptimizationConstraints(
                max_nitrogen_rate=250.0,
                max_phosphorus_rate=120.0,
                max_potassium_rate=150.0,
                budget_limit=180.0
            ),
            scenarios=scenarios,
            yield_response_curves=yield_response_curves,
            fertilizer_prices=fertilizer_prices,
            crop_price=6.00
        )
        
        # Perform optimization
        response = await service.optimize_yield_goals(request)
        
        # Validate comprehensive results
        assert response.success is True
        assert len(response.optimization_results) == 3
        assert response.best_strategy is not None
        assert isinstance(response.risk_assessment, dict)
        assert len(response.recommendations) > 0
        
        # Validate each scenario result
        for result in response.optimization_results:
            assert result.optimal_strategy is not None
            assert result.expected_yield > 0
            assert result.expected_profit is not None
            assert 0.0 <= result.yield_probability <= 1.0
            assert 0.0 <= result.profit_probability <= 1.0
            assert isinstance(result.risk_metrics, dict)
            assert isinstance(result.sensitivity_analysis, dict)
        
        # Validate best strategy
        best_strategy = response.best_strategy
        assert best_strategy.nitrogen_rate >= 0
        assert best_strategy.phosphorus_rate >= 0
        assert best_strategy.potassium_rate >= 0
        assert best_strategy.total_cost >= 0
        
        # Validate risk assessment
        risk_assessment = response.risk_assessment
        assert "overall_risk_level" in risk_assessment
        assert "weighted_yield_probability" in risk_assessment
        assert "weighted_profit_probability" in risk_assessment
        assert risk_assessment["scenario_count"] == 3
        
        # Validate recommendations
        recommendations = response.recommendations
        assert len(recommendations) > 0
        recommendation_text = " ".join(recommendations)
        assert "nitrogen" in recommendation_text.lower()
        assert "phosphorus" in recommendation_text.lower()
        assert "potassium" in recommendation_text.lower()
    
    @pytest.mark.asyncio
    async def test_different_crop_types(self, service):
        """Test optimization with different crop types."""
        crops = ["corn", "soybean", "wheat"]
        
        for crop_type in crops:
            # Create crop-specific response curves
            yield_response_curves = [
                YieldResponseCurve(
                    curve_id=uuid4(),
                    field_id=uuid4(),
                    crop_type=crop_type,
                    nutrient_type="nitrogen",
                    curve_type=ResponseModelType.QUADRATIC_PLATEAU,
                    base_yield=100.0,
                    max_yield_response=80.0,
                    response_coefficient=0.8,
                    diminishing_returns_coefficient=0.001,
                    confidence_level=0.8,
                    data_points=[],
                    model_parameters={}
                )
            ]
            
            fertilizer_prices = [
                FertilizerPriceData(
                    fertilizer_type="nitrogen",
                    price_per_unit=0.80,
                    unit="lb",
                    region="test",
                    source="test",
                    price_date="2024-01-01"
                )
            ]
            
            scenarios = [
                OptimizationScenario(
                    scenario_type=ScenarioType.BASELINE,
                    yield_goal=200.0,
                    price_scenario={'nitrogen': 0.80},
                    risk_tolerance=YieldRiskLevel.MEDIUM,
                    probability_weight=1.0
                )
            ]
            
            request = YieldGoalOptimizationRequest(
                field_id=uuid4(),
                crop_type=crop_type,
                yield_goal=200.0,
                optimization_objective=OptimizationObjective.BALANCED,
                optimization_method=OptimizationMethod.MULTI_CRITERIA,
                constraints=OptimizationConstraints(),
                scenarios=scenarios,
                yield_response_curves=yield_response_curves,
                fertilizer_prices=fertilizer_prices,
                crop_price=5.50
            )
            
            response = await service.optimize_yield_goals(request)
            
            assert response.success is True
            assert len(response.optimization_results) == 1
            assert response.best_strategy is not None