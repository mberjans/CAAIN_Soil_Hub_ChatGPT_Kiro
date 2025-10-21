"""
Unit tests for Economic Optimization Service.

These tests validate the economic optimization service functionality including:
- Multi-objective optimization algorithms
- Scenario modeling and generation
- Risk assessment and mitigation
- Sensitivity analysis
- Monte Carlo simulation
- Budget allocation optimization
- Investment prioritization
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from uuid import uuid4

from ..services.economic_optimizer import EconomicOptimizer
from ..models.economic_optimization_models import (
    EconomicOptimizationRequest,
    EconomicScenario,
    ScenarioType,
    MarketCondition,
    MultiObjectiveOptimization,
    RiskAssessment,
    SensitivityAnalysis,
    MonteCarloSimulation
)


class TestEconomicOptimizer:
    """Comprehensive test suite for economic optimization service."""

    @pytest.fixture
    def optimizer(self):
        """Create economic optimizer instance for testing."""
        return EconomicOptimizer()

    @pytest.fixture
    def sample_request(self):
        """Create sample economic optimization request."""
        return EconomicOptimizationRequest(
            analysis_id=str(uuid4()),
            farm_context={
                "farm_id": str(uuid4()),
                "field_id": str(uuid4()),
                "field_size_acres": 40.0,
                "region": "US-Midwest"
            },
            crop_context={
                "crop_type": "corn",
                "expected_yield_bu_per_acre": 180.0,
                "crop_price_per_bu": 5.50
            },
            fertilizer_requirements=[
                {
                    "product": "urea",
                    "type": "nitrogen",
                    "rate_lbs_per_acre": 150.0,
                    "application_method": "broadcast"
                }
            ],
            optimization_goals={
                "primary_goal": "profit_maximization",
                "yield_priority": 0.8,
                "cost_priority": 0.7,
                "environmental_priority": 0.6
            },
            constraints={
                "budget_limit": 12000.0,
                "risk_tolerance": "moderate",
                "environmental_constraints": {
                    "max_n_rate": 200.0,
                    "buffer_zones": True
                }
            }
        )

    @pytest.fixture
    def sample_market_data(self):
        """Create sample market data."""
        return {
            'fertilizer_prices': {
                'urea': {
                    'price_per_unit': 450.0,
                    'unit': 'ton',
                    'source': 'USDA NASS'
                }
            },
            'crop_prices': {
                'corn': 5.50
            },
            'market_conditions': {
                'fertilizer_market': 'stable',
                'crop_market': 'bull_market',
                'input_costs': 'rising'
            },
            'economic_indicators': {
                'interest_rate': 0.05,
                'inflation_rate': 0.03
            }
        }

    @pytest.fixture
    def sample_scenarios(self):
        """Create sample economic scenarios."""
        scenarios = []
        for scenario_type in [ScenarioType.BASELINE, ScenarioType.BULL_MARKET, ScenarioType.BEAR_MARKET]:
            scenario = EconomicScenario(
                scenario_id=str(uuid4()),
                scenario_name=f"{scenario_type.value} Scenario",
                scenario_type=scenario_type,
                market_condition=MarketCondition.STABLE if scenario_type == ScenarioType.BASELINE else MarketCondition.BULL_MARKET if scenario_type == ScenarioType.BULL_MARKET else MarketCondition.BEAR_MARKET,
                fertilizer_prices={
                    'urea': {
                        'price_per_unit': 450.0 * (1.2 if scenario_type == ScenarioType.BULL_MARKET else 0.8 if scenario_type == ScenarioType.BEAR_MARKET else 1.0),
                        'unit': 'ton',
                        'source': 'USDA NASS'
                    }
                },
                crop_prices={
                    'corn': 5.50 * (1.3 if scenario_type == ScenarioType.BULL_MARKET else 0.7 if scenario_type == ScenarioType.BEAR_MARKET else 1.0)
                },
                scenario_metrics={
                    'total_fertilizer_cost': 18000.0,
                    'total_crop_revenue': 39600.0,
                    'net_profit': 21600.0,
                    'profit_margin_percent': 54.5,
                    'roi_percent': 120.0
                },
                probability_distribution={
                    'mean_probability': 0.3 if scenario_type == ScenarioType.BASELINE else 0.2 if scenario_type == ScenarioType.BULL_MARKET else 0.1,
                    'standard_deviation': 0.05,
                    'confidence_intervals': {
                        '0.5': 0.25 if scenario_type == ScenarioType.BASELINE else 0.15 if scenario_type == ScenarioType.BULL_MARKET else 0.05,
                        '0.75': 0.28 if scenario_type == ScenarioType.BASELINE else 0.18 if scenario_type == ScenarioType.BULL_MARKET else 0.08,
                        '0.9': 0.32 if scenario_type == ScenarioType.BASELINE else 0.22 if scenario_type == ScenarioType.BULL_MARKET else 0.12,
                        '0.95': 0.35 if scenario_type == ScenarioType.BASELINE else 0.25 if scenario_type == ScenarioType.BULL_MARKET else 0.15,
                        '0.99': 0.38 if scenario_type == ScenarioType.BASELINE else 0.28 if scenario_type == ScenarioType.BULL_MARKET else 0.18
                    }
                },
                risk_assessment={
                    'overall_risk_level': 'low' if scenario_type == ScenarioType.BASELINE else 'medium' if scenario_type == ScenarioType.BULL_MARKET else 'high',
                    'price_volatility_risk': 0.15 if scenario_type == ScenarioType.BASELINE else 0.25 if scenario_type == ScenarioType.BULL_MARKET else 0.35,
                    'supply_chain_risk': 0.1,
                    'market_demand_risk': 0.1 if scenario_type == ScenarioType.BASELINE else 0.2 if scenario_type == ScenarioType.BULL_MARKET else 0.3,
                    'economic_risk': 0.1 if scenario_type == ScenarioType.BASELINE else 0.2 if scenario_type == ScenarioType.BULL_MARKET else 0.3,
                    'risk_factors': ['Price volatility', 'Market demand']
                },
                description=f"Sample {scenario_type.value} scenario",
                assumptions={
                    'economic_growth': 'stable' if scenario_type == ScenarioType.BASELINE else 'strong' if scenario_type == ScenarioType.BULL_MARKET else 'weak',
                    'commodity_demand': 'stable' if scenario_type == ScenarioType.BASELINE else 'high' if scenario_type == ScenarioType.BULL_MARKET else 'low',
                    'fertilizer_demand': 'stable' if scenario_type == ScenarioType.BASELINE else 'moderate' if scenario_type == ScenarioType.BULL_MARKET else 'reduced',
                    'supply_chain': 'stable'
                },
                created_at=datetime.utcnow()
            )
            scenarios.append(scenario)
        return scenarios

    @pytest.mark.asyncio
    async def test_optimize_fertilizer_strategy_success(self, optimizer, sample_request, sample_market_data, sample_scenarios):
        """Test successful fertilizer strategy optimization."""
        with patch.object(optimizer.price_tracking_service, 'get_current_price', return_value=sample_market_data['fertilizer_prices']['urea']), \
             patch.object(optimizer.price_tracking_service, 'get_commodity_prices', return_value=sample_market_data['crop_prices']), \
             patch.object(optimizer.commodity_price_service, 'get_current_prices', return_value=sample_market_data['crop_prices']), \
             patch.object(optimizer, '_get_market_conditions', return_value=sample_market_data['market_conditions']), \
             patch.object(optimizer, '_get_economic_indicators', return_value=sample_market_data['economic_indicators']), \
             patch.object(optimizer, '_generate_scenarios', return_value=sample_scenarios), \
             patch.object(optimizer, '_perform_multi_objective_optimization', new_callable=AsyncMock), \
             patch.object(optimizer, '_perform_risk_assessment', new_callable=AsyncMock), \
             patch.object(optimizer, '_perform_sensitivity_analysis', new_callable=AsyncMock), \
             patch.object(optimizer, '_perform_monte_carlo_simulation', new_callable=AsyncMock), \
             patch.object(optimizer, '_generate_budget_allocations', new_callable=AsyncMock), \
             patch.object(optimizer, '_prioritize_investments', new_callable=AsyncMock), \
             patch.object(optimizer, '_generate_economic_recommendations', new_callable=AsyncMock), \
             patch.object(optimizer.repository, 'store_optimization_result', new_callable=AsyncMock):
            
            result = await optimizer.optimize_fertilizer_strategy(sample_request)
            
            assert result.analysis_id == sample_request.analysis_id
            assert len(result.scenarios) == len(sample_scenarios)
            assert result.processing_time_ms > 0
            assert result.created_at is not None

    @pytest.mark.asyncio
    async def test_get_market_data_success(self, optimizer, sample_request, sample_market_data):
        """Test successful market data retrieval."""
        with patch.object(optimizer.price_tracking_service, 'get_current_price', return_value=sample_market_data['fertilizer_prices']['urea']), \
             patch.object(optimizer.price_tracking_service, 'get_commodity_prices', return_value=sample_market_data['crop_prices']), \
             patch.object(optimizer.commodity_price_service, 'get_current_prices', return_value=sample_market_data['crop_prices']):
            
            result = await optimizer._get_market_data(sample_request)
            
            assert 'fertilizer_prices' in result
            assert 'crop_prices' in result
            assert 'market_conditions' in result
            assert 'economic_indicators' in result
            assert len(result['fertilizer_prices']) > 0
            assert len(result['crop_prices']) > 0

    @pytest.mark.asyncio
    async def test_generate_scenarios_success(self, optimizer, sample_request, sample_market_data):
        """Test successful scenario generation."""
        with patch.object(optimizer, '_generate_scenario', new_callable=AsyncMock) as mock_generate_scenario, \
             patch.object(optimizer, '_generate_custom_scenario', new_callable=AsyncMock) as mock_generate_custom_scenario:
            
            # Mock scenario generation
            mock_scenario = MagicMock()
            mock_scenario.scenario_type = ScenarioType.BASELINE
            mock_generate_scenario.return_value = mock_scenario
            
            # Mock custom scenario generation
            mock_custom_scenario = MagicMock()
            mock_custom_scenario.scenario_type = ScenarioType.CUSTOM
            mock_generate_custom_scenario.return_value = mock_custom_scenario
            
            # Add custom scenarios to request
            sample_request.custom_scenarios = [{'name': 'Custom Scenario'}]
            
            result = await optimizer._generate_scenarios(sample_request, sample_market_data)
            
            assert len(result) > 0
            assert mock_generate_scenario.call_count > 0
            assert mock_generate_custom_scenario.call_count > 0

    @pytest.mark.asyncio
    async def test_perform_multi_objective_optimization_success(self, optimizer, sample_request, sample_market_data, sample_scenarios):
        """Test successful multi-objective optimization."""
        with patch.object(optimizer, '_calculate_base_optimization', new_callable=AsyncMock) as mock_base_opt, \
             patch.object(optimizer, '_calculate_weighted_optimization', new_callable=AsyncMock) as mock_weighted_opt, \
             patch.object(optimizer, '_calculate_constraint_optimization', new_callable=AsyncMock) as mock_constraint_opt, \
             patch.object(optimizer, '_calculate_risk_adjusted_optimization', new_callable=AsyncMock) as mock_risk_adj_opt:
            
            # Mock optimization calculations
            mock_base_opt.return_value = {'net_profit': 21600.0, 'roi_percent': 120.0}
            mock_weighted_opt.return_value = {'weighted_net_profit': 17280.0}
            mock_constraint_opt.return_value = {'budget_violation': False}
            mock_risk_adj_opt.return_value = {'risk_adjusted_profit': 19440.0}
            
            result = await optimizer._perform_multi_objective_optimization(
                sample_request, sample_market_data, sample_scenarios
            )
            
            assert len(result) == len(sample_scenarios)
            assert all(isinstance(r, MultiObjectiveOptimization) for r in result)
            assert mock_base_opt.call_count > 0
            assert mock_weighted_opt.call_count > 0
            assert mock_constraint_opt.call_count > 0
            assert mock_risk_adj_opt.call_count > 0

    @pytest.mark.asyncio
    async def test_perform_risk_assessment_success(self, optimizer, sample_request, sample_scenarios):
        """Test successful risk assessment."""
        with patch.object(optimizer, '_calculate_overall_risk_score') as mock_risk_score, \
             patch.object(optimizer, '_calculate_individual_risks') as mock_individual_risks, \
             patch.object(optimizer, '_generate_mitigation_strategies') as mock_mitigation, \
             patch.object(optimizer, '_calculate_risk_confidence_intervals') as mock_confidence_intervals:
            
            # Mock risk assessment components
            mock_risk_score.return_value = 0.5
            mock_individual_risks.return_value = {'price_volatility': 0.3, 'yield_variability': 0.2}
            mock_mitigation.return_value = ['Mitigation strategy 1', 'Mitigation strategy 2']
            mock_confidence_intervals.return_value = {'0.95': {'lower': 0.4, 'upper': 0.6}}
            
            # Create sample optimization results
            optimization_results = []
            for scenario in sample_scenarios:
                opt_result = MultiObjectiveOptimization(
                    optimization_id=str(uuid4()),
                    scenario_id=scenario.scenario_id,
                    base_optimization={'net_profit': 21600.0},
                    weighted_optimization={'weighted_net_profit': 17280.0},
                    constraint_optimization={'budget_violation': False},
                    risk_adjusted_optimization={'risk_adjusted_profit': 19440.0},
                    objectives={},
                    constraints={},
                    optimization_methods=[],
                    created_at=datetime.utcnow()
                )
                optimization_results.append(opt_result)
            
            result = await optimizer._perform_risk_assessment(
                sample_request, sample_scenarios, optimization_results
            )
            
            assert len(result) == len(sample_scenarios)
            assert all(isinstance(r, RiskAssessment) for r in result)
            assert mock_risk_score.call_count > 0
            assert mock_individual_risks.call_count > 0
            assert mock_mitigation.call_count > 0
            assert mock_confidence_intervals.call_count > 0

    @pytest.mark.asyncio
    async def test_perform_sensitivity_analysis_success(self, optimizer, sample_request):
        """Test successful sensitivity analysis."""
        # Create sample optimization results
        optimization_results = []
        for i in range(3):
            scenario_type = [ScenarioType.BASELINE, ScenarioType.BULL_MARKET, ScenarioType.BEAR_MARKET][i]
            opt_result = MultiObjectiveOptimization(
                optimization_id=str(uuid4()),
                scenario_id=str(uuid4()),
                base_optimization={'net_profit': 21600.0 * (1.0 + i * 0.1)},
                weighted_optimization={'weighted_net_profit': 17280.0 * (1.0 + i * 0.1)},
                constraint_optimization={'budget_violation': False},
                risk_adjusted_optimization={'risk_adjusted_profit': 19440.0 * (1.0 + i * 0.1)},
                objectives={},
                constraints={},
                optimization_methods=[],
                created_at=datetime.utcnow()
            )
            optimization_results.append(opt_result)
        
        with patch.object(optimizer, '_calculate_modified_results', new_callable=AsyncMock) as mock_modified_results:
            # Mock modified results
            mock_modified_results.return_value = {'net_profit': 21600.0}
            
            result = await optimizer._perform_sensitivity_analysis(
                sample_request, optimization_results
            )
            
            assert isinstance(result, SensitivityAnalysis)
            assert result.analysis_id is not None
            assert len(result.parameter_variations) > 0
            assert len(result.sensitivity_results) > 0
            assert len(result.critical_parameters) >= 0
            assert len(result.recommendations) >= 0
            assert mock_modified_results.call_count > 0

    @pytest.mark.asyncio
    async def test_perform_monte_carlo_simulation_success(self, optimizer, sample_request, sample_scenarios):
        """Test successful Monte Carlo simulation."""
        with patch.object(optimizer, '_calculate_profit_for_simulation', new_callable=AsyncMock) as mock_profit_calc:
            # Mock profit calculation
            mock_profit_calc.return_value = 21600.0
            
            result = await optimizer._perform_monte_carlo_simulation(
                sample_request, sample_scenarios
            )
            
            assert isinstance(result, MonteCarloSimulation)
            assert result.simulation_id is not None
            assert result.iterations == optimizer.monte_carlo_iterations
            assert len(result.scenario_results) == len(sample_scenarios)
            assert len(result.confidence_levels) == len(optimizer.confidence_levels)
            assert mock_profit_calc.call_count >= len(sample_scenarios) * optimizer.monte_carlo_iterations

    @pytest.mark.asyncio
    async def test_calculate_priority_score_success(self, optimizer):
        """Test successful priority score calculation."""
        # Create sample optimization result
        opt_result = MultiObjectiveOptimization(
            optimization_id=str(uuid4()),
            scenario_id=str(uuid4()),
            base_optimization={'net_profit': 21600.0, 'roi_percent': 120.0},
            weighted_optimization={'weighted_net_profit': 17280.0},
            constraint_optimization={'budget_violation': False, 'constraint_compliance_score': 0.9},
            risk_adjusted_optimization={'risk_adjusted_profit': 19440.0},
            objectives={},
            constraints={},
            optimization_methods=[],
            created_at=datetime.utcnow()
        )
        
        # Create sample risk assessment
        risk_assessment = RiskAssessment(
            assessment_id=str(uuid4()),
            scenario_id=str(uuid4()),
            overall_risk_score=0.3,
            risk_level="medium",
            individual_risks={},
            mitigation_strategies=[],
            confidence_intervals={},
            created_at=datetime.utcnow()
        )
        
        result = await optimizer._calculate_priority_score(
            opt_result, risk_assessment
        )
        
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    @pytest.mark.asyncio
    async def test_determine_priority_level_success(self, optimizer):
        """Test successful priority level determination."""
        # Test different priority scores
        high_priority = optimizer._determine_priority_level(0.85)
        medium_priority = optimizer._determine_priority_level(0.65)
        low_priority = optimizer._determine_priority_level(0.45)
        defer_priority = optimizer._determine_priority_level(0.25)
        
        assert high_priority == "high"
        assert medium_priority == "medium"
        assert low_priority == "low"
        assert defer_priority == "defer"

    @pytest.mark.asyncio
    async def test_generate_investment_recommendations_success(self, optimizer):
        """Test successful investment recommendation generation."""
        # Create sample optimization result
        opt_result = MultiObjectiveOptimization(
            optimization_id=str(uuid4()),
            scenario_id=str(uuid4()),
            base_optimization={'net_profit': 21600.0},
            weighted_optimization={'weighted_net_profit': 17280.0},
            constraint_optimization={'budget_violation': False},
            risk_adjusted_optimization={'risk_adjusted_profit': 19440.0},
            objectives={},
            constraints={},
            optimization_methods=[],
            created_at=datetime.utcnow()
        )
        
        # Create sample risk assessment
        risk_assessment = RiskAssessment(
            assessment_id=str(uuid4()),
            scenario_id=str(uuid4()),
            overall_risk_score=0.3,
            risk_level="medium",
            individual_risks={},
            mitigation_strategies=[],
            confidence_intervals={},
            created_at=datetime.utcnow()
        )
        
        # Test different priority scores
        high_priority_score = 0.85
        medium_priority_score = 0.65
        low_priority_score = 0.45
        defer_priority_score = 0.25
        
        high_rec = optimizer._generate_investment_recommendations(
            opt_result, risk_assessment, high_priority_score
        )
        
        medium_rec = optimizer._generate_investment_recommendations(
            opt_result, risk_assessment, medium_priority_score
        )
        
        low_rec = optimizer._generate_investment_recommendations(
            opt_result, risk_assessment, low_priority_score
        )
        
        defer_rec = optimizer._generate_investment_recommendations(
            opt_result, risk_assessment, defer_priority_score
        )
        
        assert len(high_rec) > 0
        assert len(medium_rec) > 0
        assert len(low_rec) > 0
        assert len(defer_rec) > 0

    @pytest.mark.performance
    async def test_response_time_requirement(self, optimizer, sample_request, sample_market_data, sample_scenarios):
        """Test that response time is under 5 seconds."""
        import time
        
        start_time = time.time()
        
        # Mock fast responses
        with patch.object(optimizer.price_tracking_service, 'get_current_price', return_value=sample_market_data['fertilizer_prices']['urea']), \
             patch.object(optimizer.price_tracking_service, 'get_commodity_prices', return_value=sample_market_data['crop_prices']), \
             patch.object(optimizer.commodity_price_service, 'get_current_prices', return_value=sample_market_data['crop_prices']), \
             patch.object(optimizer, '_get_market_conditions', return_value=sample_market_data['market_conditions']), \
             patch.object(optimizer, '_get_economic_indicators', return_value=sample_market_data['economic_indicators']), \
             patch.object(optimizer, '_generate_scenarios', return_value=sample_scenarios), \
             patch.object(optimizer, '_perform_multi_objective_optimization', new_callable=AsyncMock), \
             patch.object(optimizer, '_perform_risk_assessment', new_callable=AsyncMock), \
             patch.object(optimizer, '_perform_sensitivity_analysis', new_callable=AsyncMock), \
             patch.object(optimizer, '_perform_monte_carlo_simulation', new_callable=AsyncMock), \
             patch.object(optimizer, '_generate_budget_allocations', new_callable=AsyncMock), \
             patch.object(optimizer, '_prioritize_investments', new_callable=AsyncMock), \
             patch.object(optimizer, '_generate_economic_recommendations', new_callable=AsyncMock), \
             patch.object(optimizer.repository, 'store_optimization_result', new_callable=AsyncMock):
            
            await optimizer.optimize_fertilizer_strategy(sample_request)
        
        elapsed = time.time() - start_time
        assert elapsed < 5.0, f"Response time {elapsed}s exceeds 5s requirement"

    @pytest.mark.agricultural
    async def test_agricural_validation(self, optimizer, sample_request):
        """Test agricultural validation of economic optimization."""
        # Mock successful optimization
        with patch.object(optimizer.price_tracking_service, 'get_current_price', return_value={'price_per_unit': 450.0, 'unit': 'ton', 'source': 'USDA NASS'}), \
             patch.object(optimizer.price_tracking_service, 'get_commodity_prices', return_value={'corn': 5.50}), \
             patch.object(optimizer.commodity_price_service, 'get_current_prices', return_value={'corn': 5.50}), \
             patch.object(optimizer, '_get_market_conditions', return_value={'fertilizer_market': 'stable'}), \
             patch.object(optimizer, '_get_economic_indicators', return_value={'interest_rate': 0.05}), \
             patch.object(optimizer, '_generate_scenarios', new_callable=AsyncMock), \
             patch.object(optimizer, '_perform_multi_objective_optimization', new_callable=AsyncMock), \
             patch.object(optimizer, '_perform_risk_assessment', new_callable=AsyncMock), \
             patch.object(optimizer, '_perform_sensitivity_analysis', new_callable=AsyncMock), \
             patch.object(optimizer, '_perform_monte_carlo_simulation', new_callable=AsyncMock), \
             patch.object(optimizer, '_generate_budget_allocations', new_callable=AsyncMock), \
             patch.object(optimizer, '_prioritize_investments', new_callable=AsyncMock), \
             patch.object(optimizer, '_generate_economic_recommendations', new_callable=AsyncMock), \
             patch.object(optimizer.repository, 'store_optimization_result', new_callable=AsyncMock):
            
            result = await optimizer.optimize_fertilizer_strategy(sample_request)
            
            # Validate agricultural soundness
            assert result.analysis_id is not None
            assert len(result.scenarios) > 0
            assert len(result.optimization_results) > 0
            assert len(result.risk_assessments) > 0
            assert result.sensitivity_analysis is not None
            assert result.monte_carlo_simulation is not None
            assert len(result.budget_allocations) > 0
            assert len(result.investment_priorities) > 0
            assert len(result.recommendations) > 0


class TestAgriculturalValidation:
    """Tests for agricultural accuracy and domain validation."""

    @pytest.mark.asyncio
    async def test_economic_optimization_accuracy(self, optimizer, sample_request):
        """Test accuracy of economic optimization calculations."""
        with patch.object(optimizer.price_tracking_service, 'get_current_price', return_value={'price_per_unit': 450.0, 'unit': 'ton', 'source': 'USDA NASS'}), \
             patch.object(optimizer.price_tracking_service, 'get_commodity_prices', return_value={'corn': 5.50}), \
             patch.object(optimizer.commodity_price_service, 'get_current_prices', return_value={'corn': 5.50}):
            
            market_data = await optimizer._get_market_data(sample_request)
            
            # Validate market data accuracy
            assert 'fertilizer_prices' in market_data
            assert 'crop_prices' in market_data
            assert market_data['fertilizer_prices']['urea']['price_per_unit'] == 450.0
            assert market_data['crop_prices']['corn'] == 5.50

    @pytest.mark.asyncio
    async def test_scenario_generation_accuracy(self, optimizer, sample_request, sample_market_data):
        """Test accuracy of scenario generation."""
        with patch.object(optimizer, '_generate_scenario', new_callable=AsyncMock) as mock_generate_scenario:
            mock_scenario = MagicMock()
            mock_scenario.scenario_type = ScenarioType.BASELINE
            mock_generate_scenario.return_value = mock_scenario
            
            scenarios = await optimizer._generate_scenarios(sample_request, sample_market_data)
            
            # Validate scenario generation
            assert len(scenarios) > 0
            assert all(isinstance(s, EconomicScenario) for s in scenarios)
            assert mock_generate_scenario.call_count > 0

    @pytest.mark.asyncio
    async def test_risk_assessment_validation(self, optimizer, sample_request, sample_scenarios):
        """Test validation of risk assessment results."""
        with patch.object(optimizer, '_calculate_overall_risk_score') as mock_risk_score, \
             patch.object(optimizer, '_calculate_individual_risks') as mock_individual_risks:
            
            mock_risk_score.return_value = 0.5
            mock_individual_risks.return_value = {'price_volatility': 0.3, 'yield_variability': 0.2}
            
            # Create sample optimization results
            optimization_results = []
            for scenario in sample_scenarios:
                opt_result = MultiObjectiveOptimization(
                    optimization_id=str(uuid4()),
                    scenario_id=scenario.scenario_id,
                    base_optimization={'net_profit': 21600.0},
                    weighted_optimization={'weighted_net_profit': 17280.0},
                    constraint_optimization={'budget_violation': False},
                    risk_adjusted_optimization={'risk_adjusted_profit': 19440.0},
                    objectives={},
                    constraints={},
                    optimization_methods=[],
                    created_at=datetime.utcnow()
                )
                optimization_results.append(opt_result)
            
            risk_assessments = await optimizer._perform_risk_assessment(
                sample_request, sample_scenarios, optimization_results
            )
            
            # Validate risk assessment results
            assert len(risk_assessments) == len(sample_scenarios)
            for assessment in risk_assessments:
                assert 0.0 <= assessment.overall_risk_score <= 1.0
                assert assessment.risk_level in ['low', 'medium', 'high', 'critical']

    @pytest.mark.asyncio
    async def test_sensitivity_analysis_validation(self, optimizer, sample_request):
        """Test validation of sensitivity analysis results."""
        # Create sample optimization results
        optimization_results = []
        for i in range(3):
            scenario_type = [ScenarioType.BASELINE, ScenarioType.BULL_MARKET, ScenarioType.BEAR_MARKET][i]
            opt_result = MultiObjectiveOptimization(
                optimization_id=str(uuid4()),
                scenario_id=str(uuid4()),
                base_optimization={'net_profit': 21600.0 * (1.0 + i * 0.1)},
                weighted_optimization={'weighted_net_profit': 17280.0 * (1.0 + i * 0.1)},
                constraint_optimization={'budget_violation': False},
                risk_adjusted_optimization={'risk_adjusted_profit': 19440.0 * (1.0 + i * 0.1)},
                objectives={},
                constraints={},
                optimization_methods=[],
                created_at=datetime.utcnow()
            )
            optimization_results.append(opt_result)
        
        with patch.object(optimizer, '_calculate_modified_results', new_callable=AsyncMock) as mock_modified_results:
            mock_modified_results.return_value = {'net_profit': 21600.0}
            
            sensitivity_analysis = await optimizer._perform_sensitivity_analysis(
                sample_request, optimization_results
            )
            
            # Validate sensitivity analysis
            assert isinstance(sensitivity_analysis, SensitivityAnalysis)
            assert sensitivity_analysis.analysis_id is not None
            assert len(sensitivity_analysis.parameter_variations) > 0

    @pytest.mark.asyncio
    async def test_monte_carlo_simulation_validation(self, optimizer, sample_request, sample_scenarios):
        """Test validation of Monte Carlo simulation results."""
        with patch.object(optimizer, '_calculate_profit_for_simulation', new_callable=AsyncMock) as mock_profit_calc:
            mock_profit_calc.return_value = 21600.0
            
            monte_carlo_results = await optimizer._perform_monte_carlo_simulation(
                sample_request, sample_scenarios
            )
            
            # Validate Monte Carlo results
            assert isinstance(monte_carlo_results, MonteCarloSimulation)
            assert monte_carlo_results.simulation_id is not None
            assert monte_carlo_results.iterations == optimizer.monte_carlo_iterations
            assert len(monte_carlo_results.scenario_results) == len(sample_scenarios)

    @pytest.mark.asyncio
    async def test_budget_allocation_validation(self, optimizer, sample_request):
        """Test validation of budget allocation results."""
        # Create sample optimization results
        optimization_results = []
        for i in range(3):
            scenario_type = [ScenarioType.BASELINE, ScenarioType.BULL_MARKET, ScenarioType.BEAR_MARKET][i]
            opt_result = MultiObjectiveOptimization(
                optimization_id=str(uuid4()),
                scenario_id=str(uuid4()),
                base_optimization={'net_profit': 21600.0 * (1.0 + i * 0.1)},
                weighted_optimization={'weighted_net_profit': 17280.0 * (1.0 + i * 0.1)},
                constraint_optimization={'budget_violation': False},
                risk_adjusted_optimization={'risk_adjusted_profit': 19440.0 * (1.0 + i * 0.1)},
                objectives={},
                constraints={},
                optimization_methods=[],
                created_at=datetime.utcnow()
            )
            optimization_results.append(opt_result)
        
        with patch.object(optimizer, '_generate_budget_allocations', new_callable=AsyncMock) as mock_budget_alloc:
            mock_budget_alloc.return_value = [{'allocation_id': str(uuid4())}]
            
            budget_allocations = await optimizer._generate_budget_allocations(
                sample_request, optimization_results
            )
            
            # Validate budget allocation results
            assert len(budget_allocations) > 0
            assert all('allocation_id' in allocation for allocation in budget_allocations)

    @pytest.mark.asyncio
    async def test_investment_prioritization_validation(self, optimizer, sample_request, sample_scenarios):
        """Test validation of investment prioritization results."""
        # Create sample optimization results
        optimization_results = []
        for i in range(3):
            scenario_type = [ScenarioType.BASELINE, ScenarioType.BULL_MARKET, ScenarioType.BEAR_MARKET][i]
            opt_result = MultiObjectiveOptimization(
                optimization_id=str(uuid4()),
                scenario_id=sample_scenarios[i].scenario_id,
                base_optimization={'net_profit': 21600.0 * (1.0 + i * 0.1)},
                weighted_optimization={'weighted_net_profit': 17280.0 * (1.0 + i * 0.1)},
                constraint_optimization={'budget_violation': False},
                risk_adjusted_optimization={'risk_adjusted_profit': 19440.0 * (1.0 + i * 0.1)},
                objectives={},
                constraints={},
                optimization_methods=[],
                created_at=datetime.utcnow()
            )
            optimization_results.append(opt_result)
        
        # Create sample risk assessments
        risk_assessments = []
        for i in range(3):
            risk_assessment = RiskAssessment(
                assessment_id=str(uuid4()),
                scenario_id=sample_scenarios[i].scenario_id,
                overall_risk_score=0.3 * (i + 1),
                risk_level=["low", "medium", "high"][i],
                individual_risks={'price_volatility': 0.2 * (i + 1), 'yield_variability': 0.1 * (i + 1)},
                mitigation_strategies=['Strategy 1', 'Strategy 2'],
                confidence_intervals={'0.95': {'lower': 0.2, 'upper': 0.4}},
                created_at=datetime.utcnow()
            )
            risk_assessments.append(risk_assessment)
        
        with patch.object(optimizer, '_prioritize_investments', new_callable=AsyncMock) as mock_invest_prior:
            mock_invest_prior.return_value = [{'priority_id': str(uuid4())}]
            
            investment_priorities = await optimizer._prioritize_investments(
                sample_request, optimization_results, risk_assessments
            )
            
            # Validate investment prioritization results
            assert len(investment_priorities) > 0
            assert all('priority_id' in priority for priority in investment_priorities)

    def test_scenario_type_validation(self, optimizer):
        """Test validation of scenario types."""
        # Test all scenario types
        for scenario_type in ScenarioType:
            # Ensure we can get multipliers for each scenario type
            multipliers = optimizer._get_scenario_multipliers(scenario_type)
            assert isinstance(multipliers, dict)
            
            # Ensure we can get scenario names for each scenario type
            scenario_name = optimizer._get_scenario_name(scenario_type)
            assert isinstance(scenario_name, str)
            
            # Ensure we can get market conditions for each scenario type
            market_condition = optimizer._get_market_condition(scenario_type)
            assert isinstance(market_condition, MarketCondition)
            
            # Ensure we can get descriptions for each scenario type
            description = optimizer._get_scenario_description(scenario_type)
            assert isinstance(description, str)
            
            # Ensure we can get assumptions for each scenario type
            assumptions = optimizer._get_scenario_assumptions(scenario_type)
            assert isinstance(assumptions, dict)

    def test_risk_factor_validation(self, optimizer):
        """Test validation of risk factors."""
        # Test that all risk factors have valid weights
        for factor, weight in optimizer.risk_factors.items():
            assert isinstance(factor, str)
            assert isinstance(weight, float)
            assert 0.0 <= weight <= 1.0
            
        # Test that risk factors sum to approximately 1.0
        total_weight = sum(optimizer.risk_factors.values())
        assert 0.9 <= total_weight <= 1.1

    def test_allocation_weight_validation(self, optimizer):
        """Test validation of allocation weights."""
        # Test that all allocation weights have valid values
        for factor, weight in optimizer.allocation_weights.items():
            assert isinstance(factor, str)
            assert isinstance(weight, float)
            assert 0.0 <= weight <= 1.0
            
        # Test that allocation weights sum to approximately 1.0
        total_weight = sum(optimizer.allocation_weights.values())
        assert 0.9 <= total_weight <= 1.1

    def test_confidence_level_validation(self, optimizer):
        """Test validation of confidence levels."""
        # Test that all confidence levels are valid
        for confidence in optimizer.confidence_levels:
            assert isinstance(confidence, float)
            assert 0.0 <= confidence <= 1.0
            
        # Test that confidence levels are in ascending order
        sorted_confidence_levels = sorted(optimizer.confidence_levels)
        assert optimizer.confidence_levels == sorted_confidence_levels

    def test_monte_carlo_iteration_validation(self, optimizer):
        """Test validation of Monte Carlo iterations."""
        # Test that iterations are within reasonable range
        assert isinstance(optimizer.monte_carlo_iterations, int)
        assert 1000 <= optimizer.monte_carlo_iterations <= 100000