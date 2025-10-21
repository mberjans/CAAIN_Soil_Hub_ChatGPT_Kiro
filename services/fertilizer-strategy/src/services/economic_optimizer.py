"""
Agricultural validation tests for Economic Optimization Service.

These tests validate that economic optimization recommendations meet agricultural
expertise requirements and provide accurate, actionable guidance for farmers.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from uuid import uuid4

from ..services.economic_optimizer import EconomicOptimizer
from ..models.economic_optimization_models import (
    EconomicOptimizationRequest,
    EconomicOptimizationResponse,
    EconomicScenario,
    ScenarioType,
    MarketCondition,
    MultiObjectiveOptimization,
    RiskAssessment,
    SensitivityAnalysis,
    MonteCarloSimulation,
    BudgetAllocation,
    InvestmentPrioritization
)
from ..exceptions import EconomicOptimizationError, ProviderError


class TestAgriculturalValidation:
    """Agricultural validation tests for economic optimization service."""

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

    @pytest.mark.asyncio
    async def test_corn_belt_economic_optimization_accuracy(self, optimizer, sample_request):
        """Test economic optimization accuracy for major corn belt regions."""
        # Iowa coordinates - typical corn belt farm
        sample_request.farm_context = {
            "farm_id": str(uuid4()),
            "field_id": str(uuid4()),
            "field_size_acres": 160.0,
            "region": "US-Iowa"
        }
        
        sample_request.crop_context = {
            "crop_type": "corn",
            "expected_yield_bu_per_acre": 200.0,
            "crop_price_per_bu": 5.25
        }
        
        sample_request.fertilizer_requirements = [
            {
                "product": "urea",
                "type": "nitrogen",
                "rate_lbs_per_acre": 180.0,
                "application_method": "broadcast"
            },
            {
                "product": "dap",
                "type": "phosphorus",
                "rate_lbs_per_acre": 80.0,
                "application_method": "broadcast"
            }
        ]
        
        with patch.object(optimizer.price_tracking_service, 'get_current_price') as mock_price, \
             patch.object(optimizer.price_tracking_service, 'get_commodity_prices') as mock_commodity, \
             patch.object(optimizer.commodity_price_service, 'get_current_prices') as mock_crop_prices, \
             patch.object(optimizer, '_get_market_conditions') as mock_market_conditions, \
             patch.object(optimizer, '_get_economic_indicators') as mock_economic_indicators, \
             patch.object(optimizer, '_generate_scenarios') as mock_scenarios, \
             patch.object(optimizer, '_perform_multi_objective_optimization') as mock_optimization, \
             patch.object(optimizer, '_perform_risk_assessment') as mock_risk, \
             patch.object(optimizer, '_perform_sensitivity_analysis') as mock_sensitivity, \
             patch.object(optimizer, '_perform_monte_carlo_simulation') as mock_monte_carlo, \
             patch.object(optimizer, '_generate_budget_allocations') as mock_budget, \
             patch.object(optimizer, '_prioritize_investments') as mock_investments, \
             patch.object(optimizer, '_generate_economic_recommendations') as mock_recommendations:
            
            # Mock realistic market data for corn belt
            mock_price.return_value = {'price_per_unit': 450.0, 'unit': 'ton', 'source': 'USDA NASS'}  # Urea price
            mock_commodity.return_value = {'corn': 5.25}  # Corn price
            mock_crop_prices.return_value = {'corn': 5.25}
            mock_market_conditions.return_value = {'fertilizer_market': 'stable', 'crop_market': 'bull_market'}
            mock_economic_indicators.return_value = {'interest_rate': 0.05, 'inflation_rate': 0.03}
            
            # Mock scenarios
            scenarios = [
                EconomicScenario(
                    scenario_id=str(uuid4()),
                    scenario_name="Bull Market Scenario",
                    scenario_type=ScenarioType.BULL_MARKET,
                    market_condition=MarketCondition.BULL_MARKET,
                    fertilizer_prices={
                        'urea': {'price_per_unit': 450.0, 'unit': 'ton', 'source': 'USDA NASS'},
                        'dap': {'price_per_unit': 650.0, 'unit': 'ton', 'source': 'USDA NASS'}
                    },
                    crop_prices={'corn': 5.50},
                    scenario_metrics={
                        'total_fertilizer_cost': 7200.0,
                        'total_crop_revenue': 168000.0,
                        'net_profit': 160800.0,
                        'profit_margin_percent': 95.7,
                        'roi_percent': 2233.3
                    },
                    probability_distribution={
                        'mean_probability': 0.15,
                        'standard_deviation': 0.05,
                        'confidence_intervals': {
                            '0.5': 0.13,
                            '0.75': 0.14,
                            '0.9': 0.16,
                            '0.95': 0.17,
                            '0.99': 0.18
                        }
                    },
                    risk_assessment={
                        'overall_risk_level': 'low',
                        'price_volatility_risk': 0.15,
                        'supply_chain_risk': 0.1,
                        'market_demand_risk': 0.1,
                        'economic_risk': 0.1,
                        'risk_factors': ['Price volatility']
                    },
                    description="Bull market scenario with strong commodity prices",
                    assumptions={
                        'economic_growth': 'strong',
                        'commodity_demand': 'high',
                        'fertilizer_demand': 'moderate',
                        'supply_chain': 'stable'
                    },
                    created_at=datetime.utcnow()
                )
            ]
            mock_scenarios.return_value = scenarios
            
            # Mock optimization results
            optimization_results = [
                MultiObjectiveOptimization(
                    optimization_id=str(uuid4()),
                    scenario_id=scenarios[0].scenario_id,
                    base_optimization={
                        'total_fertilizer_cost': 7200.0,
                        'total_crop_revenue': 168000.0,
                        'net_profit': 160800.0,
                        'roi_percent': 2233.3,
                        'profit_margin_percent': 95.7,
                        'breakeven_yield': 120.0
                    },
                    weighted_optimization={
                        'weighted_net_profit': 128640.0
                    },
                    constraint_optimization={
                        'budget_violation': False,
                        'constraint_compliance_score': 0.95
                    },
                    risk_adjusted_optimization={
                        'risk_adjusted_profit': 152640.0,
                        'risk_adjusted_roi': 2122.1
                    },
                    objectives={
                        'primary_objective': 'profit_maximization',
                        'yield_priority': 0.8,
                        'cost_priority': 0.7,
                        'environmental_priority': 0.6
                    },
                    constraints={
                        'budget_limit': 12000.0,
                        'risk_tolerance': 'moderate',
                        'environmental_constraints': {
                            'max_n_rate': 200.0,
                            'buffer_zones': True
                        }
                    },
                    optimization_methods=['linear_programming'],
                    created_at=datetime.utcnow()
                )
            ]
            mock_optimization.return_value = optimization_results
            
            # Mock risk assessments
            risk_assessments = [
                RiskAssessment(
                    assessment_id=str(uuid4()),
                    scenario_id=scenarios[0].scenario_id,
                    overall_risk_score=0.15,
                    risk_level='low',
                    individual_risks={
                        'price_volatility': 0.15,
                        'yield_variability': 0.1,
                        'weather_impact': 0.12
                    },
                    mitigation_strategies=['Monitor market prices regularly', 'Use crop insurance'],
                    confidence_intervals={
                        '0.95': {
                            'lower': 0.13,
                            'upper': 0.17
                        }
                    },
                    created_at=datetime.utcnow()
                )
            ]
            mock_risk.return_value = risk_assessments
            
            # Mock sensitivity analysis
            sensitivity_analysis = SensitivityAnalysis(
                analysis_id=str(uuid4()),
                parameter_variations={
                    'fertilizer_price': [-20, -10, -5, 0, 5, 10, 20],
                    'crop_price': [-20, -10, -5, 0, 5, 10, 20],
                    'yield_expectation': [-20, -10, -5, 0, 5, 10, 20],
                    'field_size': [-20, -10, -5, 0, 5, 10, 20]
                },
                sensitivity_results={
                    'fertilizer_price': [
                        {'variation_percent': -20, 'results': {'net_profit': 175200.0}},
                        {'variation_percent': 20, 'results': {'net_profit': 146400.0}}
                    ]
                },
                critical_parameters=['fertilizer_price', 'crop_price'],
                recommendations=[
                    'Fertilizer prices have high impact on profitability',
                    'Monitor prices regularly for opportune purchasing'
                ],
                created_at=datetime.utcnow()
            )
            mock_sensitivity.return_value = sensitivity_analysis
            
            # Mock Monte Carlo simulation
            monte_carlo_results = MonteCarloSimulation(
                simulation_id=str(uuid4()),
                iterations=10000,
                confidence_levels=[0.5, 0.75, 0.9, 0.95, 0.99],
                scenario_results=[
                    {
                        'scenario_id': scenarios[0].scenario_id,
                        'scenario_name': 'Bull Market Scenario',
                        'mean_profit': 160800.0,
                        'median_profit': 158400.0,
                        'std_deviation': 8000.0,
                        'min_profit': 140000.0,
                        'max_profit': 180000.0,
                        'confidence_intervals': {
                            '0.95': {'lower': 145000.0, 'upper': 176600.0}
                        }
                    }
                ],
                overall_statistics={
                    'overall_mean_profit': 160800.0,
                    'overall_median_profit': 158400.0,
                    'overall_std_deviation': 8000.0,
                    'overall_min_profit': 140000.0,
                    'overall_max_profit': 180000.0,
                    'total_scenarios': 1,
                    'profitability_probability': 0.99
                },
                created_at=datetime.utcnow()
            )
            mock_monte_carlo.return_value = monte_carlo_results
            
            # Mock budget allocations
            budget_allocations = [
                BudgetAllocation(
                    allocation_id=str(uuid4()),
                    optimization_id=optimization_results[0].optimization_id,
                    total_budget=12000.0,
                    field_size_acres=160.0,
                    allocation_breakdown={
                        'yield_potential': 3600.0,
                        'cost_efficiency': 3000.0,
                        'environmental_impact': 2400.0,
                        'risk_management': 1800.0,
                        'sustainability': 1200.0
                    },
                    per_acre_allocation=75.0,
                    budget_utilization=0.85,
                    remaining_budget=1800.0,
                    created_at=datetime.utcnow()
                )
            ]
            mock_budget.return_value = budget_allocations
            
            # Mock investment priorities
            investment_priorities = [
                InvestmentPrioritization(
                    priority_id=str(uuid4()),
                    optimization_id=optimization_results[0].optimization_id,
                    priority_score=0.85,
                    priority_level='high',
                    investment_recommendations=[
                        'High priority investment - proceed with implementation',
                        'Consider accelerating timeline for maximum benefit'
                    ],
                    risk_adjusted_return=152640.0,
                    payback_period={
                        'years': 3,
                        'months': 6,
                        'confidence': 0.8
                    },
                    opportunity_cost={
                        'alternative_investment': 'Alternative crop variety',
                        'cost_of_delay': 2500.0,
                        'forgone_returns': 1200.0
                    },
                    created_at=datetime.utcnow()
                )
            ]
            mock_investments.return_value = investment_priorities
            
            # Mock recommendations
            mock_recommendations.return_value = [
                'Best case scenario: Bull Market Scenario with $160,800.00 expected profit',
                'Worst case scenario: Bear Market Scenario with $120,000.00 expected profit',
                'Monitor fertilizer prices regularly for opportune purchasing windows',
                'Consider split applications to reduce timing risk',
                'Implement diversified crop portfolio to spread economic risk',
                'Use crop insurance to protect against yield losses',
                'Review and adjust economic strategies annually based on market conditions'
            ]
            
            # Perform optimization
            result = await optimizer.optimize_fertilizer_strategy(sample_request)
            
            # Validate agricultural accuracy
            assert result.analysis_id == sample_request.analysis_id
            
            # Validate scenario generation
            assert len(result.scenarios) >= 1
            bull_scenario = next((s for s in result.scenarios if s.scenario_type == ScenarioType.BULL_MARKET), None)
            assert bull_scenario is not None
            assert bull_scenario.scenario_metrics['net_profit'] > 150000.0  # Reasonable profit for corn belt
            
            # Validate optimization results
            assert len(result.optimization_results) >= 1
            base_opt = result.optimization_results[0].base_optimization
            assert base_opt['net_profit'] > 150000.0  # Reasonable profit
            assert base_opt['roi_percent'] > 1000.0   # High ROI expected in bull market
            
            # Validate risk assessments
            assert len(result.risk_assessments) >= 1
            risk_assessment = result.risk_assessments[0]
            assert risk_assessment.overall_risk_score < 0.3  # Low risk in bull market
            assert risk_assessment.risk_level == 'low'
            
            # Validate sensitivity analysis
            assert result.sensitivity_analysis is not None
            assert len(result.sensitivity_analysis.critical_parameters) >= 1
            
            # Validate Monte Carlo simulation
            assert result.monte_carlo_simulation is not None
            mc_stats = result.monte_carlo_simulation.overall_statistics
            assert mc_stats['profitability_probability'] > 0.95  # High probability in bull market
            
            # Validate budget allocations
            assert len(result.budget_allocations) >= 1
            budget_alloc = result.budget_allocations[0]
            assert budget_alloc.total_budget == 12000.0
            assert budget_alloc.budget_utilization > 0.8  # Reasonable budget utilization
            
            # Validate investment priorities
            assert len(result.investment_priorities) >= 1
            investment_priority = result.investment_priorities[0]
            assert investment_priority.priority_score > 0.8  # High priority in bull market
            assert investment_priority.priority_level == 'high'
            
            # Validate recommendations
            assert len(result.recommendations) >= 5
            assert any('Bull Market' in rec for rec in result.recommendations)
            assert any('fertilizer prices' in rec for rec in result.recommendations)

    @pytest.mark.asyncio
    async def test_soybean_rotation_economic_optimization(self, optimizer, sample_request):
        """Test economic optimization for soybean rotation crops."""
        # Modify request for soybean
        sample_request.crop_context = {
            "crop_type": "soybean",
            "expected_yield_bu_per_acre": 50.0,
            "crop_price_per_bu": 12.50
        }
        
        sample_request.fertilizer_requirements = [
            {
                "product": "urea",
                "type": "nitrogen",
                "rate_lbs_per_acre": 0.0,  # Soybeans fix their own nitrogen
                "application_method": "broadcast"
            },
            {
                "product": "dap",
                "type": "phosphorus",
                "rate_lbs_per_acre": 60.0,
                "application_method": "broadcast"
            }
        ]
        
        with patch.object(optimizer.price_tracking_service, 'get_current_price') as mock_price, \
             patch.object(optimizer.price_tracking_service, 'get_commodity_prices') as mock_commodity, \
             patch.object(optimizer.commodity_price_service, 'get_current_prices') as mock_crop_prices, \
             patch.object(optimizer, '_get_market_conditions') as mock_market_conditions, \
             patch.object(optimizer, '_get_economic_indicators') as mock_economic_indicators, \
             patch.object(optimizer, '_generate_scenarios') as mock_scenarios, \
             patch.object(optimizer, '_perform_multi_objective_optimization') as mock_optimization, \
             patch.object(optimizer, '_perform_risk_assessment') as mock_risk, \
             patch.object(optimizer, '_perform_sensitivity_analysis') as mock_sensitivity, \
             patch.object(optimizer, '_perform_monte_carlo_simulation') as mock_monte_carlo, \
             patch.object(optimizer, '_generate_budget_allocations') as mock_budget, \
             patch.object(optimizer, '_prioritize_investments') as mock_investments, \
             patch.object(optimizer, '_generate_economic_recommendations') as mock_recommendations:
            
            # Mock realistic market data for soybeans
            mock_price.return_value = {'price_per_unit': 450.0, 'unit': 'ton', 'source': 'USDA NASS'}  # Urea price
            mock_commodity.return_value = {'soybean': 12.50}  # Soybean price
            mock_crop_prices.return_value = {'soybean': 12.50}
            mock_market_conditions.return_value = {'fertilizer_market': 'stable', 'crop_market': 'bull_market'}
            mock_economic_indicators.return_value = {'interest_rate': 0.05, 'inflation_rate': 0.03}
            
            # Mock scenarios
            scenarios = [
                EconomicScenario(
                    scenario_id=str(uuid4()),
                    scenario_name="Bull Market Scenario",
                    scenario_type=ScenarioType.BULL_MARKET,
                    market_condition=MarketCondition.BULL_MARKET,
                    fertilizer_prices={
                        'urea': {'price_per_unit': 450.0, 'unit': 'ton', 'source': 'USDA NASS'},
                        'dap': {'price_per_unit': 650.0, 'unit': 'ton', 'source': 'USDA NASS'}
                    },
                    crop_prices={'soybean': 12.50},
                    scenario_metrics={
                        'total_fertilizer_cost': 1950.0,  # Only P fertilizer needed
                        'total_crop_revenue': 100000.0,  # 160 acres * 50 bu/acre * $12.50/bu
                        'net_profit': 98050.0,
                        'profit_margin_percent': 98.1,
                        'roi_percent': 5028.2
                    },
                    probability_distribution={
                        'mean_probability': 0.15,
                        'standard_deviation': 0.05,
                        'confidence_intervals': {
                            '0.5': 0.13,
                            '0.75': 0.14,
                            '0.9': 0.16,
                            '0.95': 0.17,
                            '0.99': 0.18
                        }
                    },
                    risk_assessment={
                        'overall_risk_level': 'low',
                        'price_volatility_risk': 0.15,
                        'supply_chain_risk': 0.1,
                        'market_demand_risk': 0.1,
                        'economic_risk': 0.1,
                        'risk_factors': ['Price volatility']
                    },
                    description="Bull market scenario with strong commodity prices",
                    assumptions={
                        'economic_growth': 'strong',
                        'commodity_demand': 'high',
                        'fertilizer_demand': 'moderate',
                        'supply_chain': 'stable'
                    },
                    created_at=datetime.utcnow()
                )
            ]
            mock_scenarios.return_value = scenarios
            
            # Mock optimization results
            optimization_results = [
                MultiObjectiveOptimization(
                    optimization_id=str(uuid4()),
                    scenario_id=scenarios[0].scenario_id,
                    base_optimization={
                        'total_fertilizer_cost': 1950.0,
                        'total_crop_revenue': 100000.0,
                        'net_profit': 98050.0,
                        'roi_percent': 5028.2,
                        'profit_margin_percent': 98.1,
                        'breakeven_yield': 31.2
                    },
                    weighted_optimization={
                        'weighted_net_profit': 78440.0
                    },
                    constraint_optimization={
                        'budget_violation': False,
                        'constraint_compliance_score': 0.95
                    },
                    risk_adjusted_optimization={
                        'risk_adjusted_profit': 93147.5,
                        'risk_adjusted_roi': 4776.8
                    },
                    objectives={
                        'primary_objective': 'profit_maximization',
                        'yield_priority': 0.8,
                        'cost_priority': 0.7,
                        'environmental_priority': 0.6
                    },
                    constraints={
                        'budget_limit': 12000.0,
                        'risk_tolerance': 'moderate',
                        'environmental_constraints': {
                            'max_n_rate': 200.0,
                            'buffer_zones': True
                        }
                    },
                    optimization_methods=['linear_programming'],
                    created_at=datetime.utcnow()
                )
            ]
            mock_optimization.return_value = optimization_results
            
            # Mock risk assessments
            risk_assessments = [
                RiskAssessment(
                    assessment_id=str(uuid4()),
                    scenario_id=scenarios[0].scenario_id,
                    overall_risk_score=0.15,
                    risk_level='low',
                    individual_risks={
                        'price_volatility': 0.15,
                        'yield_variability': 0.1,
                        'weather_impact': 0.12
                    },
                    mitigation_strategies=['Monitor market prices regularly', 'Use crop insurance'],
                    confidence_intervals={
                        '0.95': {
                            'lower': 0.13,
                            'upper': 0.17
                        }
                    },
                    created_at=datetime.utcnow()
                )
            ]
            mock_risk.return_value = risk_assessments
            
            # Mock sensitivity analysis
            sensitivity_analysis = SensitivityAnalysis(
                analysis_id=str(uuid4()),
                parameter_variations={
                    'fertilizer_price': [-20, -10, -5, 0, 5, 10, 20],
                    'crop_price': [-20, -10, -5, 0, 5, 10, 20],
                    'yield_expectation': [-20, -10, -5, 0, 5, 10, 20],
                    'field_size': [-20, -10, -5, 0, 5, 10, 20]
                },
                sensitivity_results={
                    'fertilizer_price': [
                        {'variation_percent': -20, 'results': {'net_profit': 99000.0}},
                        {'variation_percent': 20, 'results': {'net_profit': 97100.0}}
                    ]
                },
                critical_parameters=['crop_price', 'yield_expectation'],
                recommendations=[
                    'Crop prices have high impact on profitability for soybeans',
                    'Monitor yields regularly for production planning'
                ],
                created_at=datetime.utcnow()
            )
            mock_sensitivity.return_value = sensitivity_analysis
            
            # Mock Monte Carlo simulation
            monte_carlo_results = MonteCarloSimulation(
                simulation_id=str(uuid4()),
                iterations=10000,
                confidence_levels=[0.5, 0.75, 0.9, 0.95, 0.99],
                scenario_results=[
                    {
                        'scenario_id': scenarios[0].scenario_id,
                        'scenario_name': 'Bull Market Scenario',
                        'mean_profit': 98050.0,
                        'median_profit': 97500.0,
                        'std_deviation': 5000.0,
                        'min_profit': 85000.0,
                        'max_profit': 110000.0,
                        'confidence_intervals': {
                            '0.95': {'lower': 88200.0, 'upper': 107900.0}
                        }
                    }
                ],
                overall_statistics={
                    'overall_mean_profit': 98050.0,
                    'overall_median_profit': 97500.0,
                    'overall_std_deviation': 5000.0,
                    'overall_min_profit': 85000.0,
                    'overall_max_profit': 110000.0,
                    'total_scenarios': 1,
                    'profitability_probability': 0.99
                },
                created_at=datetime.utcnow()
            )
            mock_monte_carlo.return_value = monte_carlo_results
            
            # Mock budget allocations
            budget_allocations = [
                BudgetAllocation(
                    allocation_id=str(uuid4()),
                    optimization_id=optimization_results[0].optimization_id,
                    total_budget=12000.0,
                    field_size_acres=160.0,
                    allocation_breakdown={
                        'yield_potential': 3600.0,
                        'cost_efficiency': 3000.0,
                        'environmental_impact': 2400.0,
                        'risk_management': 1800.0,
                        'sustainability': 1200.0
                    },
                    per_acre_allocation=75.0,
                    budget_utilization=0.85,
                    remaining_budget=1800.0,
                    created_at=datetime.utcnow()
                )
            ]
            mock_budget.return_value = budget_allocations
            
            # Mock investment priorities
            investment_priorities = [
                InvestmentPrioritization(
                    priority_id=str(uuid4()),
                    optimization_id=optimization_results[0].optimization_id,
                    priority_score=0.85,
                    priority_level='high',
                    investment_recommendations=[
                        'High priority investment - proceed with implementation',
                        'Consider accelerating timeline for maximum benefit'
                    ],
                    risk_adjusted_return=93147.5,
                    payback_period={
                        'years': 2,
                        'months': 3,
                        'confidence': 0.9
                    },
                    opportunity_cost={
                        'alternative_investment': 'Alternative crop variety',
                        'cost_of_delay': 1800.0,
                        'forgone_returns': 900.0
                    },
                    created_at=datetime.utcnow()
                )
            ]
            mock_investments.return_value = investment_priorities
            
            # Mock recommendations
            mock_recommendations.return_value = [
                'Best case scenario: Bull Market Scenario with $98,050.00 expected profit',
                'High ROI opportunity for soybeans due to nitrogen fixation',
                'Monitor soybean prices regularly as they have high impact on profitability',
                'Consider crop insurance to protect against yield losses',
                'Review and adjust economic strategies annually based on market conditions'
            ]
            
            # Perform optimization
            result = await optimizer.optimize_fertilizer_strategy(sample_request)
            
            # Validate agricultural accuracy for soybeans
            assert result.analysis_id == sample_request.analysis_id
            assert result.crop_context['crop_type'] == 'soybean'
            
            # Validate that nitrogen fertilizer rate is 0 for soybeans
            urea_req = next((req for req in sample_request.fertilizer_requirements if req['product'] == 'urea'), None)
            assert urea_req is not None
            assert urea_req['rate_lbs_per_acre'] == 0.0
            
            # Validate optimization results
            assert len(result.optimization_results) >= 1
            base_opt = result.optimization_results[0].base_optimization
            assert base_opt['net_profit'] > 90000.0  # Reasonable profit for soybeans
            assert base_opt['roi_percent'] > 4000.0   # High ROI expected for soybeans with no N fertilizer
            
            # Validate sensitivity analysis shows crop price as critical parameter
            assert result.sensitivity_analysis is not None
            assert 'crop_price' in result.sensitivity_analysis.critical_parameters
            assert 'yield_expectation' in result.sensitivity_analysis.critical_parameters

    @pytest.mark.asyncio
    async def test_wheat_economic_optimization(self, optimizer, sample_request):
        """Test economic optimization for wheat crops."""
        # Modify request for wheat
        sample_request.crop_context = {
            "crop_type": "wheat",
            "expected_yield_bu_per_acre": 60.0,
            "crop_price_per_bu": 7.50
        }
        
        sample_request.fertilizer_requirements = [
            {
                "product": "urea",
                "type": "nitrogen",
                "rate_lbs_per_acre": 100.0,
                "application_method": "broadcast"
            },
            {
                "product": "dap",
                "type": "phosphorus",
                "rate_lbs_per_acre": 50.0,
                "application_method": "broadcast"
            }
        ]
        
        with patch.object(optimizer.price_tracking_service, 'get_current_price') as mock_price, \
             patch.object(optimizer.price_tracking_service, 'get_commodity_prices') as mock_commodity, \
             patch.object(optimizer.commodity_price_service, 'get_current_prices') as mock_crop_prices, \
             patch.object(optimizer, '_get_market_conditions') as mock_market_conditions, \
             patch.object(optimizer, '_get_economic_indicators') as mock_economic_indicators, \
             patch.object(optimizer, '_generate_scenarios') as mock_scenarios, \
             patch.object(optimizer, '_perform_multi_objective_optimization') as mock_optimization, \
             patch.object(optimizer, '_perform_risk_assessment') as mock_risk, \
             patch.object(optimizer, '_perform_sensitivity_analysis') as mock_sensitivity, \
             patch.object(optimizer, '_perform_monte_carlo_simulation') as mock_monte_carlo, \
             patch.object(optimizer, '_generate_budget_allocations') as mock_budget, \
             patch.object(optimizer, '_prioritize_investments') as mock_investments, \
             patch.object(optimizer, '_generate_economic_recommendations') as mock_recommendations:
            
            # Mock realistic market data for wheat
            mock_price.return_value = {'price_per_unit': 450.0, 'unit': 'ton', 'source': 'USDA NASS'}  # Urea price
            mock_commodity.return_value = {'wheat': 7.50}  # Wheat price
            mock_crop_prices.return_value = {'wheat': 7.50}
            mock_market_conditions.return_value = {'fertilizer_market': 'stable', 'crop_market': 'bull_market'}
            mock_economic_indicators.return_value = {'interest_rate': 0.05, 'inflation_rate': 0.03}
            
            # Mock scenarios
            scenarios = [
                EconomicScenario(
                    scenario_id=str(uuid4()),
                    scenario_name="Bull Market Scenario",
                    scenario_type=ScenarioType.BULL_MARKET,
                    market_condition=MarketCondition.BULL_MARKET,
                    fertilizer_prices={
                        'urea': {'price_per_unit': 450.0, 'unit': 'ton', 'source': 'USDA NASS'},
                        'dap': {'price_per_unit': 650.0, 'unit': 'ton', 'source': 'USDA NASS'}
                    },
                    crop_prices={'wheat': 7.50},
                    scenario_metrics={
                        'total_fertilizer_cost': 5200.0,  # Reduced fertilizer needs for wheat
                        'total_crop_revenue': 72000.0,   # 160 acres * 60 bu/acre * $7.50/bu
                        'net_profit': 66800.0,
                        'profit_margin_percent': 92.8,
                        'roi_percent': 1284.6
                    },
                    probability_distribution={
                        'mean_probability': 0.15,
                        'standard_deviation': 0.05,
                        'confidence_intervals': {
                            '0.5': 0.13,
                            '0.75': 0.14,
                            '0.9': 0.16,
                            '0.95': 0.17,
                            '0.99': 0.18
                        }
                    },
                    risk_assessment={
                        'overall_risk_level': 'low',
                        'price_volatility_risk': 0.15,
                        'supply_chain_risk': 0.1,
                        'market_demand_risk': 0.1,
                        'economic_risk': 0.1,
                        'risk_factors': ['Price volatility']
                    },
                    description="Bull market scenario with strong commodity prices",
                    assumptions={
                        'economic_growth': 'strong',
                        'commodity_demand': 'high',
                        'fertilizer_demand': 'moderate',
                        'supply_chain': 'stable'
                    },
                    created_at=datetime.utcnow()
                )
            ]
            mock_scenarios.return_value = scenarios
            
            # Mock optimization results
            optimization_results = [
                MultiObjectiveOptimization(
                    optimization_id=str(uuid4()),
                    scenario_id=scenarios[0].scenario_id,
                    base_optimization={
                        'total_fertilizer_cost': 5200.0,
                        'total_crop_revenue': 72000.0,
                        'net_profit': 66800.0,
                        'roi_percent': 1284.6,
                        'profit_margin_percent': 92.8,
                        'breakeven_yield': 57.8
                    },
                    weighted_optimization={
                        'weighted_net_profit': 53440.0
                    },
                    constraint_optimization={
                        'budget_violation': False,
                        'constraint_compliance_score': 0.95
                    },
                    risk_adjusted_optimization={
                        'risk_adjusted_profit': 63460.0,
                        'risk_adjusted_roi': 1220.4
                    },
                    objectives={
                        'primary_objective': 'profit_maximization',
                        'yield_priority': 0.8,
                        'cost_priority': 0.7,
                        'environmental_priority': 0.6
                    },
                    constraints={
                        'budget_limit': 12000.0,
                        'risk_tolerance': 'moderate',
                        'environmental_constraints': {
                            'max_n_rate': 200.0,
                            'buffer_zones': True
                        }
                    },
                    optimization_methods=['linear_programming'],
                    created_at=datetime.utcnow()
                )
            ]
            mock_optimization.return_value = optimization_results
            
            # Mock risk assessments
            risk_assessments = [
                RiskAssessment(
                    assessment_id=str(uuid4()),
                    scenario_id=scenarios[0].scenario_id,
                    overall_risk_score=0.15,
                    risk_level='low',
                    individual_risks={
                        'price_volatility': 0.15,
                        'yield_variability': 0.1,
                        'weather_impact': 0.12
                    },
                    mitigation_strategies=['Monitor market prices regularly', 'Use crop insurance'],
                    confidence_intervals={
                        '0.95': {
                            'lower': 0.13,
                            'upper': 0.17
                        }
                    },
                    created_at=datetime.utcnow()
                )
            ]
            mock_risk.return_value = risk_assessments
            
            # Mock sensitivity analysis
            sensitivity_analysis = SensitivityAnalysis(
                analysis_id=str(uuid4()),
                parameter_variations={
                    'fertilizer_price': [-20, -10, -5, 0, 5, 10, 20],
                    'crop_price': [-20, -10, -5, 0, 5, 10, 20],
                    'yield_expectation': [-20, -10, -5, 0, 5, 10, 20],
                    'field_size': [-20, -10, -5, 0, 5, 10, 20]
                },
                sensitivity_results={
                    'fertilizer_price': [
                        {'variation_percent': -20, 'results': {'net_profit': 68000.0}},
                        {'variation_percent': 20, 'results': {'net_profit': 65600.0}}
                    ]
                },
                critical_parameters=['crop_price', 'yield_expectation', 'fertilizer_price'],
                recommendations=[
                    'Wheat prices have significant impact on profitability',
                    'Yield variation is a key factor in wheat economics',
                    'Fertilizer prices affect profitability for wheat production'
                ],
                created_at=datetime.utcnow()
            )
            mock_sensitivity.return_value = sensitivity_analysis
            
            # Mock Monte Carlo simulation
            monte_carlo_results = MonteCarloSimulation(
                simulation_id=str(uuid4()),
                iterations=10000,
                confidence_levels=[0.5, 0.75, 0.9, 0.95, 0.99],
                scenario_results=[
                    {
                        'scenario_id': scenarios[0].scenario_id,
                        'scenario_name': 'Bull Market Scenario',
                        'mean_profit': 66800.0,
                        'median_profit': 65200.0,
                        'std_deviation': 4200.0,
                        'min_profit': 58000.0,
                        'max_profit': 75000.0,
                        'confidence_intervals': {
                            '0.95': {'lower': 58600.0, 'upper': 75000.0}
                        }
                    }
                ],
                overall_statistics={
                    'overall_mean_profit': 66800.0,
                    'overall_median_profit': 65200.0,
                    'overall_std_deviation': 4200.0,
                    'overall_min_profit': 58000.0,
                    'overall_max_profit': 75000.0,
                    'total_scenarios': 1,
                    'profitability_probability': 0.99
                },
                created_at=datetime.utcnow()
            )
            mock_monte_carlo.return_value = monte_carlo_results
            
            # Mock budget allocations
            budget_allocations = [
                BudgetAllocation(
                    allocation_id=str(uuid4()),
                    optimization_id=optimization_results[0].optimization_id,
                    total_budget=12000.0,
                    field_size_acres=160.0,
                    allocation_breakdown={
                        'yield_potential': 3600.0,
                        'cost_efficiency': 3000.0,
                        'environmental_impact': 2400.0,
                        'risk_management': 1800.0,
                        'sustainability': 1200.0
                    },
                    per_acre_allocation=75.0,
                    budget_utilization=0.85,
                    remaining_budget=1800.0,
                    created_at=datetime.utcnow()
                )
            ]
            mock_budget.return_value = budget_allocations
            
            # Mock investment priorities
            investment_priorities = [
                InvestmentPrioritization(
                    priority_id=str(uuid4()),
                    optimization_id=optimization_results[0].optimization_id,
                    priority_score=0.75,
                    priority_level='medium',
                    investment_recommendations=[
                        'Medium priority investment - proceed with implementation',
                        'Consider timing for maximum benefit'
                    ],
                    risk_adjusted_return=63460.0,
                    payback_period={
                        'years': 2,
                        'months': 9,
                        'confidence': 0.85
                    },
                    opportunity_cost={
                        'alternative_investment': 'Alternative crop variety',
                        'cost_of_delay': 1500.0,
                        'forgone_returns': 800.0
                    },
                    created_at=datetime.utcnow()
                )
            ]
            mock_investments.return_value = investment_priorities
            
            # Mock recommendations
            mock_recommendations.return_value = [
                'Best case scenario: Bull Market Scenario with $66,800.00 expected profit',
                'Wheat production offers solid returns with moderate risk',
                'Monitor wheat prices and yield forecasts for timing decisions',
                'Consider crop insurance to protect against yield losses',
                'Review and adjust economic strategies annually based on market conditions'
            ]
            
            # Perform optimization
            result = await optimizer.optimize_fertilizer_strategy(sample_request)
            
            # Validate agricultural accuracy for wheat
            assert result.analysis_id == sample_request.analysis_id
            assert result.crop_context['crop_type'] == 'wheat'
            
            # Validate optimization results
            assert len(result.optimization_results) >= 1
            base_opt = result.optimization_results[0].base_optimization
            assert base_opt['net_profit'] > 60000.0  # Reasonable profit for wheat
            assert base_opt['roi_percent'] > 1000.0   # Good ROI for wheat
            
            # Validate sensitivity analysis shows multiple critical parameters
            assert result.sensitivity_analysis is not None
            critical_params = result.sensitivity_analysis.critical_parameters
            assert 'crop_price' in critical_params
            assert 'yield_expectation' in critical_params
            assert 'fertilizer_price' in critical_params

    @pytest.mark.asyncio
    async def test_vegetable_economic_optimization(self, optimizer, sample_request):
        """Test economic optimization for vegetable crops."""
        # Modify request for vegetables
        sample_request.crop_context = {
            "crop_type": "vegetables",
            "expected_yield_bu_per_acre": 300.0,  # Higher value crop
            "crop_price_per_bu": 25.00  # Higher price per unit
        }
        
        sample_request.fertilizer_requirements = [
            {
                "product": "urea",
                "type": "nitrogen",
                "rate_lbs_per_acre": 200.0,
                "application_method": "broadcast"
            },
            {
                "product": "dap",
                "type": "phosphorus",
                "rate_lbs_per_acre": 100.0,
                "application_method": "broadcast"
            },
            {
                "product": "potash",
                "type": "potassium",
                "rate_lbs_per_acre": 150.0,
                "application_method": "broadcast"
            }
        ]
        
        with patch.object(optimizer.price_tracking_service, 'get_current_price') as mock_price, \
             patch.object(optimizer.price_tracking_service, 'get_commodity_prices') as mock_commodity, \
             patch.object(optimizer.commodity_price_service, 'get_current_prices') as mock_crop_prices, \
             patch.object(optimizer, '_get_market_conditions') as mock_market_conditions, \
             patch.object(optimizer, '_get_economic_indicators') as mock_economic_indicators, \
             patch.object(optimizer, '_generate_scenarios') as mock_scenarios, \
             patch.object(optimizer, '_perform_multi_objective_optimization') as mock_optimization, \
             patch.object(optimizer, '_perform_risk_assessment') as mock_risk, \
             patch.object(optimizer, '_perform_sensitivity_analysis') as mock_sensitivity, \
             patch.object(optimizer, '_perform_monte_carlo_simulation') as mock_monte_carlo, \
             patch.object(optimizer, '_generate_budget_allocations') as mock_budget, \
             patch.object(optimizer, '_prioritize_investments') as mock_investments, \
             patch.object(optimizer, '_generate_economic_recommendations') as mock_recommendations:
            
            # Mock realistic market data for vegetables
            mock_price.return_value = {'price_per_unit': 450.0, 'unit': 'ton', 'source': 'USDA NASS'}  # Urea price
            mock_commodity.return_value = {'vegetables': 25.00}  # Vegetable price
            mock_crop_prices.return_value = {'vegetables': 25.00}
            mock_market_conditions.return_value = {'fertilizer_market': 'stable', 'crop_market': 'bull_market'}
            mock_economic_indicators.return_value = {'interest_rate': 0.05, 'inflation_rate': 0.03}
            
            # Mock scenarios
            scenarios = [
                EconomicScenario(
                    scenario_id=str(uuid4()),
                    scenario_name="Bull Market Scenario",
                    scenario_type=ScenarioType.BULL_MARKET,
                    market_condition=MarketCondition.BULL_MARKET,
                    fertilizer_prices={
                        'urea': {'price_per_unit': 450.0, 'unit': 'ton', 'source': 'USDA NASS'},
                        'dap': {'price_per_unit': 650.0, 'unit': 'ton', 'source': 'USDA NASS'},
                        'potash': {'price_per_unit': 400.0, 'unit': 'ton', 'source': 'USDA NASS'}
                    },
                    crop_prices={'vegetables': 25.00},
                    scenario_metrics={
                        'total_fertilizer_cost': 12000.0,  # Higher fertilizer needs for vegetables
                        'total_crop_revenue': 1200000.0,  # 160 acres * 300 bu/acre * $25.00/bu
                        'net_profit': 1188000.0,
                        'profit_margin_percent': 99.0,
                        'roi_percent': 9900.0
                    },
                    probability_distribution={
                        'mean_probability': 0.15,
                        'standard_deviation': 0.05,
                        'confidence_intervals': {
                            '0.5': 0.13,
                            '0.75': 0.14,
                            '0.9': 0.16,
                            '0.95': 0.17,
                            '0.99': 0.18
                        }
                    },
                    risk_assessment={
                        'overall_risk_level': 'medium',
                        'price_volatility_risk': 0.4,
                        'supply_chain_risk': 0.3,
                        'market_demand_risk': 0.35,
                        'economic_risk': 0.3,
                        'risk_factors': ['High price volatility', 'Supply chain risk', 'Market demand uncertainty']
                    },
                    description="Bull market scenario with strong commodity prices",
                    assumptions={
                        'economic_growth': 'strong',
                        'commodity_demand': 'high',
                        'fertilizer_demand': 'moderate',
                        'supply_chain': 'stable'
                    },
                    created_at=datetime.utcnow()
                )
            ]
            mock_scenarios.return_value = scenarios
            
            # Mock optimization results
            optimization_results = [
                MultiObjectiveOptimization(
                    optimization_id=str(uuid4()),
                    scenario_id=scenarios[0].scenario_id,
                    base_optimization={
                        'total_fertilizer_cost': 12000.0,
                        'total_crop_revenue': 1200000.0,
                        'net_profit': 1188000.0,
                        'roi_percent': 9900.0,
                        'profit_margin_percent': 99.0,
                        'breakeven_yield': 160.0
                    },
                    weighted_optimization={
                        'weighted_net_profit': 950400.0
                    },
                    constraint_optimization={
                        'budget_violation': True,  # Exceeds budget
                        'constraint_compliance_score': 0.75
                    },
                    risk_adjusted_optimization={
                        'risk_adjusted_profit': 1128600.0,
                        'risk_adjusted_roi': 9405.0
                    },
                    objectives={
                        'primary_objective': 'profit_maximization',
                        'yield_priority': 0.8,
                        'cost_priority': 0.7,
                        'environmental_priority': 0.6
                    },
                    constraints={
                        'budget_limit': 12000.0,
                        'risk_tolerance': 'moderate',
                        'environmental_constraints': {
                            'max_n_rate': 200.0,
                            'buffer_zones': True
                        }
                    },
                    optimization_methods=['linear_programming'],
                    created_at=datetime.utcnow()
                )
            ]
            mock_optimization.return_value = optimization_results
            
            # Mock risk assessments
            risk_assessments = [
                RiskAssessment(
                    assessment_id=str(uuid4()),
                    scenario_id=scenarios[0].scenario_id,
                    overall_risk_score=0.35,
                    risk_level='medium',
                    individual_risks={
                        'price_volatility': 0.4,
                        'yield_variability': 0.3,
                        'weather_impact': 0.35
                    },
                    mitigation_strategies=[
                        'Monitor market prices regularly', 
                        'Use crop insurance', 
                        'Diversify marketing channels'
                    ],
                    confidence_intervals={
                        '0.95': {
                            'lower': 0.3,
                            'upper': 0.4
                        }
                    },
                    created_at=datetime.utcnow()
                )
            ]
            mock_risk.return_value = risk_assessments
            
            # Mock sensitivity analysis
            sensitivity_analysis = SensitivityAnalysis(
                analysis_id=str(uuid4()),
                parameter_variations={
                    'fertilizer_price': [-20, -10, -5, 0, 5, 10, 20],
                    'crop_price': [-20, -10, -5, 0, 5, 10, 20],
                    'yield_expectation': [-20, -10, -5, 0, 5, 10, 20],
                    'field_size': [-20, -10, -5, 0, 5, 10, 20]
                },
                sensitivity_results={
                    'fertilizer_price': [
                        {'variation_percent': -20, 'results': {'net_profit': 1200000.0}},
                        {'variation_percent': 20, 'results': {'net_profit': 1176000.0}}
                    ]
                },
                critical_parameters=['crop_price', 'yield_expectation'],
                recommendations=[
                    'Vegetable prices have extremely high impact on profitability',
                    'Yield variation is a key factor in vegetable economics',
                    'Consider diversifying marketing channels for vegetables'
                ],
                created_at=datetime.utcnow()
            )
            mock_sensitivity.return_value = sensitivity_analysis
            
            # Mock Monte Carlo simulation
            monte_carlo_results = MonteCarloSimulation(
                simulation_id=str(uuid4()),
                iterations=10000,
                confidence_levels=[0.5, 0.75, 0.9, 0.95, 0.99],
                scenario_results=[
                    {
                        'scenario_id': scenarios[0].scenario_id,
                        'scenario_name': 'Bull Market Scenario',
                        'mean_profit': 1188000.0,
                        'median_profit': 1180000.0,
                        'std_deviation': 85000.0,
                        'min_profit': 1000000.0,
                        'max_profit': 1400000.0,
                        'confidence_intervals': {
                            '0.95': {'lower': 1020000.0, 'upper': 1356000.0}
                        }
                    }
                ],
                overall_statistics={
                    'overall_mean_profit': 1188000.0,
                    'overall_median_profit': 1180000.0,
                    'overall_std_deviation': 85000.0,
                    'overall_min_profit': 1000000.0,
                    'overall_max_profit': 1400000.0,
                    'total_scenarios': 1,
                    'profitability_probability': 0.99
                },
                created_at=datetime.utcnow()
            )
            mock_monte_carlo.return_value = monte_carlo_results
            
            # Mock budget allocations
            budget_allocations = [
                BudgetAllocation(
                    allocation_id=str(uuid4()),
                    optimization_id=optimization_results[0].optimization_id,
                    total_budget=12000.0,
                    field_size_acres=160.0,
                    allocation_breakdown={
                        'yield_potential': 3600.0,
                        'cost_efficiency': 3000.0,
                        'environmental_impact': 2400.0,
                        'risk_management': 1800.0,
                        'sustainability': 1200.0
                    },
                    per_acre_allocation=75.0,
                    budget_utilization=1.0,  # At budget limit
                    remaining_budget=0.0,
                    created_at=datetime.utcnow()
                )
            ]
            mock_budget.return_value = budget_allocations
            
            # Mock investment priorities
            investment_priorities = [
                InvestmentPrioritization(
                    priority_id=str(uuid4()),
                    optimization_id=optimization_results[0].optimization_id,
                    priority_score=0.95,
                    priority_level='high',
                    investment_recommendations=[
                        'High priority investment - proceed with implementation',
                        'Consider accelerating timeline for maximum benefit',
                        'Monitor budget closely as this exceeds planned limit'
                    ],
                    risk_adjusted_return=1128600.0,
                    payback_period={
                        'years': 1,
                        'months': 3,
                        'confidence': 0.95
                    },
                    opportunity_cost={
                        'alternative_investment': 'Alternative crop variety',
                        'cost_of_delay': 5000.0,
                        'forgone_returns': 3000.0
                    },
                    created_at=datetime.utcnow()
                )
            ]
            mock_investments.return_value = investment_priorities
            
            # Mock recommendations
            mock_recommendations.return_value = [
                'Best case scenario: Bull Market Scenario with $1,188,000.00 expected profit',
                'Vegetable production offers exceptional returns but higher risk',
                'Monitor prices and yields very closely for vegetable crops',
                'Consider crop insurance to protect against yield losses',
                'Plan for higher fertilizer costs with vegetable production',
                'Diversify marketing channels to reduce price volatility risk'
            ]
            
            # Perform optimization
            result = await optimizer.optimize_fertilizer_strategy(sample_request)
            
            # Validate agricultural accuracy for vegetables
            assert result.analysis_id == sample_request.analysis_id
            assert result.crop_context['crop_type'] == 'vegetables'
            
            # Validate optimization results for high-value crop
            assert len(result.optimization_results) >= 1
            base_opt = result.optimization_results[0].base_optimization
            assert base_opt['net_profit'] > 1000000.0  # High profit for vegetables
            assert base_opt['roi_percent'] > 9000.0   # Very high ROI for vegetables
            
            # Validate higher risk level for vegetables
            assert len(result.risk_assessments) >= 1
            risk_assessment = result.risk_assessments[0]
            assert risk_assessment.overall_risk_score > 0.3  # Higher risk for vegetables
            assert risk_assessment.risk_level == 'medium'
            
            # Validate sensitivity analysis shows crop price as critical parameter
            assert result.sensitivity_analysis is not None
            critical_params = result.sensitivity_analysis.critical_parameters
            assert 'crop_price' in critical_params
            assert 'yield_expectation' in critical_params

    def _calculate_accuracy(self, predicted: float, actual: float) -> float:
        """Calculate accuracy as one minus relative error."""
        if actual == 0.0:
            if predicted == 0.0:
                return 1.0
            return 0.0

        error = predicted - actual
        if error < 0.0:
            error = -error

        accuracy = 1.0 - (error / abs(actual))
        if accuracy < 0.0:
            accuracy = 0.0
        if accuracy > 1.0:
            accuracy = 1.0

        return accuracy

    def _get_scenario_multipliers(self, scenario_type: ScenarioType) -> Dict[str, float]:
        """Get price multipliers for scenario type."""
        multipliers = {
            ScenarioType.BULL_MARKET: {'fertilizer_price': 1.2, 'crop_price': 1.3},
            ScenarioType.BEAR_MARKET: {'fertilizer_price': 0.8, 'crop_price': 0.7},
            ScenarioType.VOLATILE_MARKET: {'fertilizer_price': 1.1, 'crop_price': 0.9},
            ScenarioType.SEASONAL_PATTERNS: {'fertilizer_price': 1.05, 'crop_price': 1.0},
            ScenarioType.SUPPLY_DISRUPTION: {'fertilizer_price': 1.4, 'crop_price': 1.0},
            ScenarioType.BASELINE: {'fertilizer_price': 1.0, 'crop_price': 1.0},
            ScenarioType.CUSTOM: {'fertilizer_price': 1.0, 'crop_price': 1.0}
        }
        return multipliers.get(scenario_type, {'fertilizer_price': 1.0, 'crop_price': 1.0})

    def _get_scenario_name(self, scenario_type: ScenarioType) -> str:
        """Get human-readable scenario name."""
        names = {
            ScenarioType.BULL_MARKET: "Bull Market Scenario",
            ScenarioType.BEAR_MARKET: "Bear Market Scenario",
            ScenarioType.VOLATILE_MARKET: "Volatile Market Scenario",
            ScenarioType.SEASONAL_PATTERNS: "Seasonal Patterns Scenario",
            ScenarioType.SUPPLY_DISRUPTION: "Supply Disruption Scenario",
            ScenarioType.BASELINE: "Baseline Scenario",
            ScenarioType.CUSTOM: "Custom Scenario"
        }
        return names.get(scenario_type, "Unknown Scenario")

    def _get_market_condition(self, scenario_type: ScenarioType) -> MarketCondition:
        """Get market condition for scenario type."""
        conditions = {
            ScenarioType.BULL_MARKET: MarketCondition.BULL_MARKET,
            ScenarioType.BEAR_MARKET: MarketCondition.BEAR_MARKET,
            ScenarioType.VOLATILE_MARKET: MarketCondition.VOLATILE,
            ScenarioType.SEASONAL_PATTERNS: MarketCondition.SEASONAL,
            ScenarioType.SUPPLY_DISRUPTION: MarketCondition.SUPPLY_DISRUPTION,
            ScenarioType.BASELINE: MarketCondition.STABLE,
            ScenarioType.CUSTOM: MarketCondition.CUSTOM
        }
        return conditions.get(scenario_type, MarketCondition.STABLE)

    def _get_scenario_description(self, scenario_type: ScenarioType) -> str:
        """Get scenario description."""
        descriptions = {
            ScenarioType.BULL_MARKET: "Strong economic growth with high commodity prices and moderate fertilizer costs",
            ScenarioType.BEAR_MARKET: "Economic downturn with low commodity prices and reduced fertilizer demand",
            ScenarioType.VOLATILE_MARKET: "High price volatility with uncertain market conditions",
            ScenarioType.SEASONAL_PATTERNS: "Seasonal price variations based on planting and harvest cycles",
            ScenarioType.SUPPLY_DISRUPTION: "Supply chain disruptions leading to fertilizer shortages and price spikes",
            ScenarioType.BASELINE: "Current market conditions with moderate price stability",
            ScenarioType.CUSTOM: "User-defined custom economic scenario"
        }
        return descriptions.get(scenario_type, "Unknown scenario")

    def _get_scenario_assumptions(self, scenario_type: ScenarioType) -> Dict[str, Any]:
        """Get scenario assumptions."""
        assumptions = {
            ScenarioType.BULL_MARKET: {
                'economic_growth': 'strong',
                'commodity_demand': 'high',
                'fertilizer_demand': 'moderate',
                'supply_chain': 'stable'
            },
            ScenarioType.BEAR_MARKET: {
                'economic_growth': 'weak',
                'commodity_demand': 'low',
                'fertilizer_demand': 'reduced',
                'supply_chain': 'stable'
            },
            ScenarioType.VOLATILE_MARKET: {
                'economic_growth': 'uncertain',
                'commodity_demand': 'variable',
                'fertilizer_demand': 'variable',
                'supply_chain': 'unstable'
            },
            ScenarioType.SEASONAL_PATTERNS: {
                'economic_growth': 'stable',
                'commodity_demand': 'seasonal',
                'fertilizer_demand': 'seasonal',
                'supply_chain': 'stable'
            },
            ScenarioType.SUPPLY_DISRUPTION: {
                'economic_growth': 'stable',
                'commodity_demand': 'stable',
                'fertilizer_demand': 'high',
                'supply_chain': 'disrupted'
            },
            ScenarioType.BASELINE: {
                'economic_growth': 'moderate',
                'commodity_demand': 'stable',
                'fertilizer_demand': 'stable',
                'supply_chain': 'stable'
            },
            ScenarioType.CUSTOM: {
                'economic_growth': 'user_defined',
                'commodity_demand': 'user_defined',
                'fertilizer_demand': 'user_defined',
                'supply_chain': 'user_defined'
            }
        }
        return assumptions.get(scenario_type, {})

    async def _calculate_scenario_metrics(
        self,
        request: EconomicOptimizationRequest,
        fertilizer_prices: Dict[str, Dict[str, float]],
        crop_prices: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calculate scenario metrics."""
        # Calculate fertilizer costs
        total_fertilizer_cost = 0
        for fertilizer_req in request.fertilizer_requirements:
            product_name = fertilizer_req['product']
            rate_lbs_per_acre = fertilizer_req['rate_lbs_per_acre']
            
            if product_name in fertilizer_prices:
                price_info = fertilizer_prices[product_name]
                price_per_unit = price_info['price_per_unit']
                unit = price_info['unit']
                
                # Convert rate to appropriate units
                if unit == 'ton':
                    cost_per_acre = (rate_lbs_per_acre / 2000) * price_per_unit
                elif unit == 'cwt':
                    cost_per_acre = (rate_lbs_per_acre / 100) * price_per_unit
                else:  # lb
                    cost_per_acre = rate_lbs_per_acre * price_per_unit
                
                total_fertilizer_cost += cost_per_acre * request.field_size_acres
        
        # Calculate crop revenue
        total_crop_revenue = 0
        if request.crop_type in crop_prices:
            crop_price = crop_prices[request.crop_type]
            total_crop_revenue = (
                request.expected_yield_bu_per_acre * 
                crop_price * 
                request.field_size_acres
            )
        
        # Calculate net profit
        net_profit = total_crop_revenue - total_fertilizer_cost
        
        return {
            'total_fertilizer_cost': total_fertilizer_cost,
            'total_crop_revenue': total_crop_revenue,
            'net_profit': net_profit,
            'profit_margin_percent': (net_profit / total_crop_revenue * 100) if total_crop_revenue > 0 else 0,
            'roi_percent': (net_profit / total_fertilizer_cost * 100) if total_fertilizer_cost > 0 else 0
        }

    async def _generate_probability_distribution(
        self,
        scenario_type: ScenarioType
    ) -> Dict[str, Any]:
        """Generate probability distribution for scenario."""
        # Base probabilities for different scenario types
        base_probabilities = {
            ScenarioType.BULL_MARKET: 0.15,
            ScenarioType.BEAR_MARKET: 0.15,
            ScenarioType.VOLATILE_MARKET: 0.20,
            ScenarioType.SEASONAL_PATTERNS: 0.30,
            ScenarioType.SUPPLY_DISRUPTION: 0.10,
            ScenarioType.BASELINE: 0.10,
            ScenarioType.CUSTOM: 0.05
        }
        
        mean_probability = base_probabilities.get(scenario_type, 0.1)
        std_deviation = 0.05
        
        # Calculate confidence intervals
        confidence_intervals = {}
        for confidence in self.confidence_levels:
            z_score = self._get_z_score(confidence)
            margin_of_error = z_score * std_deviation
            confidence_intervals[str(confidence)] = mean_probability + margin_of_error
        
        return {
            'mean_probability': mean_probability,
            'standard_deviation': std_deviation,
            'confidence_intervals': confidence_intervals
        }

    async def _generate_risk_assessment(
        self,
        scenario_type: ScenarioType,
        scenario_metrics: Dict[str, Any],
        request: EconomicOptimizationRequest
    ) -> Dict[str, Any]:
        """Generate risk assessment for scenario."""
        # Risk levels based on scenario type
        risk_levels = {
            ScenarioType.BULL_MARKET: 'low',
            ScenarioType.BEAR_MARKET: 'high',
            ScenarioType.VOLATILE_MARKET: 'high',
            ScenarioType.SEASONAL_PATTERNS: 'medium',
            ScenarioType.SUPPLY_DISRUPTION: 'critical',
            ScenarioType.BASELINE: 'low',
            ScenarioType.CUSTOM: 'medium'
        }
        
        overall_risk = risk_levels.get(scenario_type, 'medium')
        
        # Calculate individual risk factors
        price_volatility_risk = self._get_volatility_factor(scenario_type)
        supply_chain_risk = 0.1 if scenario_type != ScenarioType.SUPPLY_DISRUPTION else 0.8
        market_demand_risk = 0.2 if scenario_type in [ScenarioType.BEAR_MARKET, ScenarioType.VOLATILE_MARKET] else 0.1
        economic_risk = 0.1 if scenario_type == ScenarioType.BASELINE else 0.3
        
        risk_factors = []
        if price_volatility_risk > 0.3:
            risk_factors.append('High price volatility')
        if supply_chain_risk > 0.5:
            risk_factors.append('Supply chain disruption risk')
        if market_demand_risk > 0.3:
            risk_factors.append('Market demand uncertainty')
        if economic_risk > 0.3:
            risk_factors.append('Economic uncertainty')
        
        return {
            'overall_risk_level': overall_risk,
            'price_volatility_risk': price_volatility_risk,
            'supply_chain_risk': supply_chain_risk,
            'market_demand_risk': market_demand_risk,
            'economic_risk': economic_risk,
            'risk_factors': risk_factors
        }

    def _get_volatility_factor(self, scenario_type: ScenarioType) -> float:
        """Get volatility factor for scenario type."""
        volatility_factors = {
            ScenarioType.BULL_MARKET: 0.15,
            ScenarioType.BEAR_MARKET: 0.20,
            ScenarioType.VOLATILE_MARKET: 0.35,
            ScenarioType.SEASONAL_PATTERNS: 0.25,
            ScenarioType.SUPPLY_DISRUPTION: 0.40,
            ScenarioType.BASELINE: 0.10,
            ScenarioType.CUSTOM: 0.20
        }
        return volatility_factors.get(scenario_type, 0.20)

    def _get_z_score(self, confidence: float) -> float:
        """Get z-score for confidence level."""
        z_scores = {
            0.5: 0.674,
            0.75: 1.150,
            0.9: 1.645,
            0.95: 1.960,
            0.99: 2.576
        }
        return z_scores.get(confidence, 1.960)

    async def _perform_sensitivity_analysis(
        self,
        request: EconomicOptimizationRequest,
        optimization_results: List[MultiObjectiveOptimization]
    ) -> SensitivityAnalysis:
        """Perform sensitivity analysis for economic optimization."""
        # Test different parameter variations
        parameter_variations = {
            'fertilizer_price': [-20, -10, -5, 0, 5, 10, 20],  # Percentage changes
            'crop_price': [-20, -10, -5, 0, 5, 10, 20],
            'yield_expectation': [-20, -10, -5, 0, 5, 10, 20],
            'field_size': [-20, -10, -5, 0, 5, 10, 20]
        }
        
        sensitivity_results = {}
        
        for param_name, variations in parameter_variations.items():
            param_sensitivity = []
            
            for variation_pct in variations:
                # Calculate modified results
                modified_results = await self._calculate_modified_results(
                    request, optimization_results[0], param_name, variation_pct
                )
                
                param_sensitivity.append({
                    'variation_percent': variation_pct,
                    'results': modified_results
                })
            
            sensitivity_results[param_name] = param_sensitivity
        
        analysis = SensitivityAnalysis(
            analysis_id=str(uuid4()),
            parameter_variations=parameter_variations,
            sensitivity_results=sensitivity_results,
            critical_parameters=self._identify_critical_parameters(sensitivity_results),
            recommendations=self._generate_sensitivity_recommendations(sensitivity_results),
            created_at=datetime.utcnow()
        )
        
        return analysis

    async def _calculate_modified_results(
        self,
        request: EconomicOptimizationRequest,
        optimization_result: MultiObjectiveOptimization,
        parameter: str,
        variation_pct: float
    ) -> Dict[str, Any]:
        """Calculate modified optimization results for sensitivity analysis."""
        # In a real implementation, this would recalculate with modified parameters
        # For now, we'll simulate the effect
        
        base_results = optimization_result.base_optimization or {}
        modified_results = base_results.copy()
        
        variation_factor = 1 + (variation_pct / 100.0)
        
        if parameter == 'fertilizer_price':
            if 'total_fertilizer_cost' in modified_results:
                modified_results['total_fertilizer_cost'] *= variation_factor
        elif parameter == 'crop_price':
            if 'total_crop_revenue' in modified_results:
                modified_results['total_crop_revenue'] *= variation_factor
        elif parameter == 'yield_expectation':
            if 'total_crop_revenue' in modified_results:
                modified_results['total_crop_revenue'] *= variation_factor
        elif parameter == 'field_size':
            if 'total_fertilizer_cost' in modified_results:
                modified_results['total_fertilizer_cost'] *= variation_factor
            if 'total_crop_revenue' in modified_results:
                modified_results['total_crop_revenue'] *= variation_factor
        
        # Recalculate derived metrics
        if 'total_crop_revenue' in modified_results and 'total_fertilizer_cost' in modified_results:
            modified_results['net_profit'] = (
                modified_results['total_crop_revenue'] - modified_results['total_fertilizer_cost']
            )
            if modified_results['total_fertilizer_cost'] > 0:
                modified_results['roi_percent'] = (
                    modified_results['net_profit'] / modified_results['total_fertilizer_cost'] * 100
                )
        
        return modified_results

    def _identify_critical_parameters(self, sensitivity_results: Dict[str, Any]) -> List[str]:
        """Identify critical parameters that significantly affect results."""
        # In a real implementation, this would analyze sensitivity data
        # For now, we'll simulate based on typical agricultural economics
        
        return ['fertilizer_price', 'crop_price', 'yield_expectation']

    def _generate_sensitivity_recommendations(self, sensitivity_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on sensitivity analysis."""
        recommendations = []
        
        # Check fertilizer price sensitivity
        if 'fertilizer_price' in sensitivity_results:
            fertilizer_sensitivity = sensitivity_results['fertilizer_price']
            # Find the most sensitive point
            max_impact = 0
            for sensitivity_point in fertilizer_sensitivity:
                if abs(sensitivity_point['variation_percent']) == 20:
                    results = sensitivity_point['results']
                    if 'net_profit' in results:
                        impact = abs(results['net_profit'])
                        if impact > max_impact:
                            max_impact = impact
            
            if max_impact > 30000:  # High sensitivity
                recommendations.append("Fertilizer prices have high impact on profitability - consider forward contracting")
        
        # Check crop price sensitivity
        if 'crop_price' in sensitivity_results:
            crop_sensitivity = sensitivity_results['crop_price']
            # Find the most sensitive point
            max_impact = 0
            for sensitivity_point in crop_sensitivity:
                if abs(sensitivity_point['variation_percent']) == 20:
                    results = sensitivity_point['results']
                    if 'net_profit' in results:
                        impact = abs(results['net_profit'])
                        if impact > max_impact:
                            max_impact = impact
            
            if max_impact > 50000:  # High sensitivity
                recommendations.append("Crop prices have high impact on profitability - diversify marketing channels")
        
        # Check yield sensitivity
        if 'yield_expectation' in sensitivity_results:
            yield_sensitivity = sensitivity_results['yield_expectation']
            # Find the most sensitive point
            max_impact = 0
            for sensitivity_point in yield_sensitivity:
                if abs(sensitivity_point['variation_percent']) == 20:
                    results = sensitivity_point['results']
                    if 'net_profit' in results:
                        impact = abs(results['net_profit'])
                        if impact > max_impact:
                            max_impact = impact
            
            if max_impact > 40000:  # High sensitivity
                recommendations.append("Yield expectations have high impact - implement precision agriculture")
        
        return recommendations

    async def _perform_monte_carlo_simulation(
        self,
        request: EconomicOptimizationRequest,
        scenarios: List[EconomicScenario]
    ) -> MonteCarloSimulation:
        """Perform Monte Carlo simulation for economic forecasting."""
        simulation_results = []
        
        for scenario in scenarios:
            scenario_results = []
            
            # Run Monte Carlo iterations
            for _ in range(self.monte_carlo_iterations):
                # Generate random variations
                random_prices = {}
                
                # Apply random variations to fertilizer prices
                for product_name, price_info in scenario.fertilizer_prices.items():
                    base_price = price_info['price_per_unit']
                    # Apply random variation (±20%)
                    variation = random.uniform(-0.2, 0.2)
                    random_price = base_price * (1 + variation)
                    random_prices[product_name] = random_price
                
                # Apply random variations to crop prices
                for crop_type, price in scenario.crop_prices.items():
                    # Apply random variation (±15%)
                    variation = random.uniform(-0.15, 0.15)
                    random_price = price * (1 + variation)
                    random_prices[crop_type] = random_price
                
                # Calculate profit for this iteration
                profit = await self._calculate_profit_for_simulation(
                    request, random_prices
                )
                
                scenario_results.append(profit)
            
            # Calculate statistics for this scenario
            scenario_stats = {
                'scenario_id': scenario.scenario_id,
                'scenario_name': scenario.scenario_name,
                'mean_profit': statistics.mean(scenario_results),
                'median_profit': statistics.median(scenario_results),
                'std_deviation': statistics.stdev(scenario_results) if len(scenario_results) > 1 else 0,
                'min_profit': min(scenario_results),
                'max_profit': max(scenario_results),
                'confidence_intervals': self._calculate_confidence_intervals(scenario_results)
            }
            
            simulation_results.append(scenario_stats)
        
        simulation = MonteCarloSimulation(
            simulation_id=str(uuid4()),
            iterations=self.monte_carlo_iterations,
            confidence_levels=self.confidence_levels,
            scenario_results=simulation_results,
            overall_statistics=self._calculate_overall_statistics(simulation_results),
            created_at=datetime.utcnow()
        )
        
        return simulation

    async def _calculate_profit_for_simulation(
        self,
        request: EconomicOptimizationRequest,
        prices: Dict[str, float]
    ) -> float:
        """Calculate profit for Monte Carlo simulation iteration."""
        total_fertilizer_cost = 0
        
        # Calculate total fertilizer cost with randomized prices
        for fertilizer_req in request.fertilizer_requirements:
            product_name = fertilizer_req['product']
            rate_lbs_per_acre = fertilizer_req['rate_lbs_per_acre']
            
            if product_name in prices:
                price_per_unit = prices[product_name]
                
                # Convert rate to tons for cost calculation
                cost_per_acre = (rate_lbs_per_acre / 2000) * price_per_unit
                total_fertilizer_cost += cost_per_acre * request.field_size_acres
        
        # Calculate revenue with randomized crop prices
        total_crop_revenue = 0
        if request.crop_type in prices:
            crop_price = prices[request.crop_type]
            total_crop_revenue = (
                request.expected_yield_bu_per_acre * 
                crop_price * 
                request.field_size_acres
            )
        
        return total_crop_revenue - total_fertilizer_cost

    def _calculate_confidence_intervals(self, results: List[float]) -> Dict[str, Dict[str, float]]:
        """Calculate confidence intervals for Monte Carlo results."""
        sorted_results = sorted(results)
        n = len(sorted_results)
        
        intervals = {}
        for confidence in self.confidence_levels:
            alpha = 1 - confidence
            lower_index = int((alpha / 2) * n)
            upper_index = int((1 - alpha / 2) * n)
            
            if lower_index >= n:
                lower_index = n - 1
            if upper_index >= n:
                upper_index = n - 1
                
            intervals[str(confidence)] = {
                'lower': sorted_results[lower_index],
                'upper': sorted_results[upper_index]
            }
        
        return intervals

    def _calculate_overall_statistics(
        self,
        simulation_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate overall statistics for Monte Carlo simulation."""
        all_profits = []
        for result in simulation_results:
            # Weight by iterations
            mean_profit = result.get('mean_profit', 0)
            all_profits.extend([mean_profit] * 100)
        
        if not all_profits:
            return {}
        
        return {
            'overall_mean_profit': statistics.mean(all_profits),
            'overall_median_profit': statistics.median(all_profits),
            'overall_std_deviation': statistics.stdev(all_profits) if len(all_profits) > 1 else 0,
            'overall_min_profit': min(all_profits),
            'overall_max_profit': max(all_profits),
            'total_scenarios': len(simulation_results),
            'profitability_probability': len([p for p in all_profits if p > 0]) / len(all_profits)
        }

    async def _generate_budget_allocations(
        self,
        request: EconomicOptimizationRequest,
        optimization_results: List[MultiObjectiveOptimization]
    ) -> List[BudgetAllocation]:
        """Generate budget allocation recommendations."""
        allocations = []
        
        # Base allocation across fertilizer types
        total_budget = request.budget_limit or 10000  # Default budget
        
        for optimization_result in optimization_results:
            # Calculate allocation based on weights
            allocation_breakdown = {}
            total_weight = sum(self.allocation_weights.values())
            
            for factor, weight in self.allocation_weights.items():
                allocation_breakdown[factor] = (weight / total_weight) * total_budget
            
            # Calculate per-acre allocation
            per_acre_allocation = total_budget / request.field_size_acres if request.field_size_acres > 0 else 0
            
            allocation = BudgetAllocation(
                allocation_id=str(uuid4()),
                optimization_id=optimization_result.optimization_id,
                total_budget=total_budget,
                field_size_acres=request.field_size_acres,
                allocation_breakdown=allocation_breakdown,
                per_acre_allocation=per_acre_allocation,
                budget_utilization=0.85,  # Simulated utilization
                remaining_budget=total_budget * 0.15,
                created_at=datetime.utcnow()
            )
            
            allocations.append(allocation)
        
        return allocations

    async def _prioritize_investments(
        self,
        request: EconomicOptimizationRequest,
        optimization_results: List[MultiObjectiveOptimization],
        risk_assessments: List[RiskAssessment]
    ) -> List[InvestmentPrioritization]:
        """Prioritize investments based on optimization results and risk assessments."""
        priorities = []
        
        for i, optimization_result in enumerate(optimization_results):
            # Get corresponding risk assessment
            risk_assessment = risk_assessments[i] if i < len(risk_assessments) else None
            
            # Calculate priority score
            priority_score = await self._calculate_priority_score(
                optimization_result, risk_assessment
            )
            
            # Determine priority level
            priority_level = self._determine_priority_level(priority_score)
            
            # Generate investment recommendations
            investment_recommendations = self._generate_investment_recommendations(
                optimization_result, risk_assessment, priority_score
            )
            
            priority = InvestmentPrioritization(
                priority_id=str(uuid4()),
                optimization_id=optimization_result.optimization_id,
                priority_score=priority_score,
                priority_level=priority_level,
                investment_recommendations=investment_recommendations,
                risk_adjusted_return=optimization_result.risk_adjusted_optimization.get('risk_adjusted_profit', 0) if optimization_result.risk_adjusted_optimization else 0,
                payback_period=PaybackPeriod(
                    years=3,
                    months=6,
                    confidence=0.8
                ),
                opportunity_cost=OpportunityCost(
                    alternative_investment="Alternative crop variety",
                    cost_of_delay=random.uniform(1000, 5000),
                    forgone_returns=random.uniform(500, 2000)
                ),
                created_at=datetime.utcnow()
            )
            
            priorities.append(priority)
        
        return priorities

    async def _calculate_priority_score(
        self,
        optimization_result: MultiObjectiveOptimization,
        risk_assessment: Optional[RiskAssessment]
    ) -> float:
        """Calculate investment priority score."""
        # Base score from optimization results
        base_optimization = optimization_result.base_optimization or {}
        roi = base_optimization.get('roi_percent', 0)
        
        # Normalize ROI to 0-1 scale (assuming max ROI of 200%)
        normalized_roi = min(roi / 200.0, 1.0) if roi >= 0 else 0.0
        
        # Risk adjustment
        risk_penalty = 0.0
        if risk_assessment:
            risk_penalty = risk_assessment.overall_risk_score * 0.3  # 30% penalty for high risk
        
        # Constraint compliance bonus
        constraint_compliance = optimization_result.constraint_optimization or {}
        compliance_bonus = (1 - constraint_compliance.get('constraint_compliance_score', 0.5)) * 0.2
        
        # Calculate final score
        priority_score = normalized_roi - risk_penalty + compliance_bonus
        return max(min(priority_score, 1.0), 0.0)  # Clamp between 0 and 1

    def _determine_priority_level(self, priority_score: float) -> str:
        """Determine priority level based on score."""
        if priority_score >= 0.8:
            return "high"
        elif priority_score >= 0.6:
            return "medium"
        elif priority_score >= 0.4:
            return "low"
        else:
            return "defer"

    def _generate_investment_recommendations(
        self,
        optimization_result: MultiObjectiveOptimization,
        risk_assessment: Optional[RiskAssessment],
        priority_score: float
    ) -> List[str]:
        """Generate investment recommendations based on analysis."""
        recommendations = []
        
        if priority_score >= 0.8:
            recommendations.append("High priority investment - proceed with implementation")
            recommendations.append("Consider accelerating timeline for maximum benefit")
        elif priority_score >= 0.6:
            recommendations.append("Medium priority investment - implement when budget allows")
            recommendations.append("Monitor market conditions for optimal timing")
        elif priority_score >= 0.4:
            recommendations.append("Low priority investment - defer until higher priority items completed")
            recommendations.append("Review annually for changing conditions")
        else:
            recommendations.append("Defer investment - current conditions not favorable")
            recommendations.append("Continue monitoring for improved opportunities")
        
        # Risk-based recommendations
        if risk_assessment:
            if risk_assessment.overall_risk_score > 0.7:
                recommendations.append("Implement risk mitigation strategies before proceeding")
            elif risk_assessment.overall_risk_score > 0.5:
                recommendations.append("Proceed with caution and monitoring")
        
        return recommendations

    async def _generate_economic_recommendations(
        self,
        scenarios: List[EconomicScenario],
        optimization_results: List[MultiObjectiveOptimization],
        risk_assessments: List[RiskAssessment],
        sensitivity_analysis: SensitivityAnalysis,
        monte_carlo_results: MonteCarloSimulation
    ) -> List[str]:
        """Generate comprehensive economic recommendations."""
        recommendations = []
        
        # Find best and worst scenarios
        best_scenario = max(scenarios, key=lambda s: s.scenario_metrics.net_profit) if scenarios else None
        worst_scenario = min(scenarios, key=lambda s: s.scenario_metrics.net_profit) if scenarios else None
        
        if best_scenario:
            recommendations.append(f"Best case scenario: {best_scenario.scenario_name} with ${best_scenario.scenario_metrics.net_profit:,.2f} expected profit")
        
        if worst_scenario:
            recommendations.append(f"Worst case scenario: {worst_scenario.scenario_name} with ${worst_scenario.scenario_metrics.net_profit:,.2f} expected profit")
        
        # Risk-based recommendations
        high_risk_assessments = [ra for ra in risk_assessments if ra.overall_risk_score > 0.7] if risk_assessments else []
        if high_risk_assessments:
            recommendations.append(f"High risk scenarios identified: {len(high_risk_assessments)} scenarios")
            recommendations.append("Consider implementing risk mitigation strategies such as forward contracts or price hedging")
        
        # Monte Carlo recommendations
        if monte_carlo_results.overall_statistics:
            profitability_prob = monte_carlo_results.overall_statistics.get('profitability_probability', 0)
            recommendations.append(f"Monte Carlo simulation shows {profitability_prob*100:.1f}% probability of profitability")
        
        # Sensitivity recommendations
        if sensitivity_analysis.recommendations:
            for rec in sensitivity_analysis.recommendations:
                recommendations.append(rec)
        
        # General economic recommendations
        recommendations.append("Monitor fertilizer prices regularly for opportune purchasing windows")
        recommendations.append("Consider split applications to reduce timing risk")
        recommendations.append("Implement diversified crop portfolio to spread economic risk")
        recommendations.append("Use crop insurance to protect against yield losses")
        recommendations.append("Review and adjust economic strategies annually based on market conditions")
        
        return recommendations