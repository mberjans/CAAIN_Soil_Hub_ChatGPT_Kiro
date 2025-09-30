"""
Comprehensive Price Scenario Modeling Service for fertilizer strategy optimization.

This service provides advanced price scenario modeling including:
- Multiple price scenarios (bull market, bear market, volatile market, seasonal patterns, supply disruptions)
- Monte Carlo simulation for price forecasting
- Stochastic modeling and sensitivity analysis
- Decision trees for scenario planning
- Probability modeling and risk assessment
- Integration with historical data and market intelligence
"""

import asyncio
import logging
import time
import random
import statistics
import math
from typing import Optional, List, Dict, Any, Tuple, Union
from datetime import datetime, date, timedelta
from uuid import uuid4
from enum import Enum
import json

from ..models.price_scenario_models import (
    PriceScenarioModelingRequest, PriceScenarioModelingResponse,
    PriceScenario, ScenarioType, MarketCondition, PriceForecast,
    MonteCarloSimulation, StochasticModel, SensitivityAnalysis,
    DecisionTreeNode, ProbabilityDistribution, RiskAssessment,
    SeasonalPattern, SupplyDisruptionScenario
)
from ..models.price_models import FertilizerPriceData, FertilizerProduct
from ..services.price_tracking_service import FertilizerPriceTrackingService
from ..services.commodity_price_service import CommodityPriceService
from ..database.fertilizer_price_db import FertilizerPriceRepository

logger = logging.getLogger(__name__)


class PriceScenarioModelingService:
    """Comprehensive price scenario modeling service for fertilizer strategy optimization."""
    
    def __init__(self):
        self.price_tracking_service = FertilizerPriceTrackingService()
        self.commodity_price_service = CommodityPriceService()
        
        # Scenario modeling configuration
        self.scenario_types = [
            ScenarioType.BULL_MARKET,
            ScenarioType.BEAR_MARKET,
            ScenarioType.VOLATILE_MARKET,
            ScenarioType.SEASONAL_PATTERNS,
            ScenarioType.SUPPLY_DISRUPTION,
            ScenarioType.BASELINE
        ]
        
        # Monte Carlo simulation parameters
        self.monte_carlo_iterations = 10000
        self.confidence_levels = [0.5, 0.75, 0.9, 0.95, 0.99]
        
        # Stochastic modeling parameters
        self.volatility_factors = {
            ScenarioType.BULL_MARKET: 0.15,
            ScenarioType.BEAR_MARKET: 0.20,
            ScenarioType.VOLATILE_MARKET: 0.35,
            ScenarioType.SEASONAL_PATTERNS: 0.25,
            ScenarioType.SUPPLY_DISRUPTION: 0.40,
            ScenarioType.BASELINE: 0.10
        }
        
        # Seasonal pattern coefficients
        self.seasonal_coefficients = {
            'spring': 1.15,  # Higher demand in spring
            'summer': 0.95,  # Lower demand in summer
            'fall': 1.05,    # Moderate demand in fall
            'winter': 0.85   # Lowest demand in winter
        }
    
    async def create_comprehensive_scenario_model(
        self,
        request: PriceScenarioModelingRequest
    ) -> PriceScenarioModelingResponse:
        """
        Create comprehensive price scenario model with advanced forecasting.
        
        Args:
            request: Price scenario modeling request
            
        Returns:
            Comprehensive scenario modeling response
        """
        logger.info(f"Creating comprehensive scenario model for analysis {request.analysis_id}")
        start_time = time.time()
        
        try:
            # Get current market data
            market_data = await self._get_market_data(request)
            
            # Generate multiple scenarios
            scenarios = await self._generate_all_scenarios(request, market_data)
            
            # Perform Monte Carlo simulation
            monte_carlo_results = await self._perform_monte_carlo_simulation(
                request, market_data, scenarios
            )
            
            # Perform stochastic modeling
            stochastic_results = await self._perform_stochastic_modeling(
                request, market_data, scenarios
            )
            
            # Perform sensitivity analysis
            sensitivity_results = await self._perform_sensitivity_analysis(
                request, market_data, scenarios
            )
            
            # Create decision tree
            decision_tree = await self._create_decision_tree(
                request, scenarios, monte_carlo_results
            )
            
            # Generate recommendations
            recommendations = await self._generate_scenario_recommendations(
                scenarios, monte_carlo_results, stochastic_results, sensitivity_results
            )
            
            # Calculate processing time
            processing_time_ms = (time.time() - start_time) * 1000
            
            response = PriceScenarioModelingResponse(
                analysis_id=request.analysis_id,
                scenarios=scenarios,
                monte_carlo_simulation=monte_carlo_results,
                stochastic_model=stochastic_results,
                sensitivity_analysis=sensitivity_results,
                decision_tree=decision_tree,
                recommendations=recommendations,
                processing_time_ms=processing_time_ms,
                created_at=datetime.utcnow()
            )
            
            logger.info(f"Scenario modeling completed in {processing_time_ms:.2f}ms")
            return response
            
        except Exception as e:
            logger.error(f"Error in scenario modeling: {e}")
            raise
    
    async def _get_market_data(self, request: PriceScenarioModelingRequest) -> Dict[str, Any]:
        """Get current market data for scenario modeling."""
        market_data = {
            'current_prices': {},
            'historical_data': {},
            'market_conditions': {},
            'economic_indicators': {}
        }
        
        # Get current fertilizer prices
        for fertilizer_req in request.fertilizer_requirements:
            product = FertilizerProduct(
                name=fertilizer_req['product'],
                fertilizer_type=fertilizer_req.get('type', 'unknown')
            )
            
            current_price = await self.price_tracking_service.get_current_price(
                product, request.region or "US"
            )
            
            if current_price:
                market_data['current_prices'][fertilizer_req['product']] = current_price
        
        # Get historical price data for trend analysis
        for fertilizer_req in request.fertilizer_requirements:
            product = FertilizerProduct(
                name=fertilizer_req['product'],
                fertilizer_type=fertilizer_req.get('type', 'unknown')
            )
            
            historical_data = await self.price_tracking_service.get_price_history(
                product, request.region or "US", days=365
            )
            
            if historical_data:
                market_data['historical_data'][fertilizer_req['product']] = historical_data
        
        # Get commodity prices
        commodity_prices = await self.commodity_price_service.get_current_prices(
            ['corn', 'soybeans', 'wheat'], request.region or "US"
        )
        
        if commodity_prices:
            market_data['economic_indicators']['commodity_prices'] = commodity_prices
        
        return market_data
    
    async def _generate_all_scenarios(
        self,
        request: PriceScenarioModelingRequest,
        market_data: Dict[str, Any]
    ) -> List[PriceScenario]:
        """Generate all price scenarios for analysis."""
        scenarios = []
        
        # Generate each scenario type
        for scenario_type in self.scenario_types:
            scenario = await self._generate_scenario(
                scenario_type, request, market_data
            )
            scenarios.append(scenario)
        
        # Generate custom scenarios if provided
        if request.custom_scenarios:
            for custom_scenario in request.custom_scenarios:
                scenario = await self._generate_custom_scenario(
                    custom_scenario, request, market_data
                )
                scenarios.append(scenario)
        
        return scenarios
    
    async def _generate_scenario(
        self,
        scenario_type: ScenarioType,
        request: PriceScenarioModelingRequest,
        market_data: Dict[str, Any]
    ) -> PriceScenario:
        """Generate individual scenario based on type."""
        scenario_id = str(uuid4())
        
        # Get base prices
        base_prices = market_data['current_prices']
        
        # Calculate scenario multipliers
        multipliers = self._get_scenario_multipliers(scenario_type)
        
        # Generate price forecasts
        price_forecasts = []
        for fertilizer_req in request.fertilizer_requirements:
            product_name = fertilizer_req['product']
            base_price = base_prices.get(product_name)
            
            if base_price:
                forecast = await self._generate_price_forecast(
                    base_price, multipliers, scenario_type, request
                )
                price_forecasts.append(forecast)
        
        # Calculate scenario metrics
        scenario_metrics = await self._calculate_scenario_metrics(
            request, price_forecasts, multipliers
        )
        
        # Generate probability distribution
        probability_dist = await self._generate_probability_distribution(
            scenario_type, request
        )
        
        # Generate risk assessment
        risk_assessment = await self._generate_risk_assessment(
            scenario_type, scenario_metrics, request
        )
        
        scenario = PriceScenario(
            scenario_id=scenario_id,
            scenario_name=self._get_scenario_name(scenario_type),
            scenario_type=scenario_type,
            market_condition=self._get_market_condition(scenario_type),
            price_forecasts=price_forecasts,
            scenario_metrics=scenario_metrics,
            probability_distribution=probability_dist,
            risk_assessment=risk_assessment,
            description=self._get_scenario_description(scenario_type),
            assumptions=self._get_scenario_assumptions(scenario_type),
            created_at=datetime.utcnow()
        )
        
        return scenario
    
    async def _generate_custom_scenario(
        self,
        custom_scenario: Dict[str, Any],
        request: PriceScenarioModelingRequest,
        market_data: Dict[str, Any]
    ) -> PriceScenario:
        """Generate custom scenario from user-defined parameters."""
        scenario_id = str(uuid4())
        
        # Extract custom parameters
        scenario_name = custom_scenario.get('name', 'Custom Scenario')
        fertilizer_multipliers = custom_scenario.get('fertilizer_multipliers', {})
        crop_multiplier = custom_scenario.get('crop_multiplier', 1.0)
        probability = custom_scenario.get('probability', 0.1)
        risk_level = custom_scenario.get('risk_level', 'medium')
        
        # Generate price forecasts
        price_forecasts = []
        for fertilizer_req in request.fertilizer_requirements:
            product_name = fertilizer_req['product']
            base_price = market_data['current_prices'].get(product_name)
            
            if base_price:
                multiplier = fertilizer_multipliers.get(product_name, 1.0)
                forecast = PriceForecast(
                    product_name=product_name,
                    current_price=base_price.price_per_unit,
                    forecasted_price=base_price.price_per_unit * multiplier,
                    price_change_percent=(multiplier - 1.0) * 100,
                    confidence_level=0.8,
                    forecast_horizon_days=request.analysis_horizon_days,
                    volatility_factor=0.2
                )
                price_forecasts.append(forecast)
        
        # Calculate scenario metrics
        scenario_metrics = await self._calculate_scenario_metrics(
            request, price_forecasts, {'fertilizer': 1.0, 'crop': crop_multiplier}
        )
        
        # Generate probability distribution
        probability_dist = ProbabilityDistribution(
            mean_probability=probability,
            standard_deviation=0.05,
            confidence_intervals={
                '0.5': probability - 0.02,
                '0.75': probability - 0.01,
                '0.9': probability + 0.01,
                '0.95': probability + 0.02,
                '0.99': probability + 0.03
            }
        )
        
        # Generate risk assessment
        risk_assessment = RiskAssessment(
            overall_risk_level=risk_level,
            price_volatility_risk=0.3,
            supply_chain_risk=0.2,
            market_demand_risk=0.25,
            economic_risk=0.2,
            risk_factors=['Custom scenario parameters']
        )
        
        scenario = PriceScenario(
            scenario_id=scenario_id,
            scenario_name=scenario_name,
            scenario_type=ScenarioType.CUSTOM,
            market_condition=MarketCondition.CUSTOM,
            price_forecasts=price_forecasts,
            scenario_metrics=scenario_metrics,
            probability_distribution=probability_dist,
            risk_assessment=risk_assessment,
            description=f"Custom scenario: {scenario_name}",
            assumptions=custom_scenario.get('assumptions', {}),
            created_at=datetime.utcnow()
        )
        
        return scenario
    
    async def _perform_monte_carlo_simulation(
        self,
        request: PriceScenarioModelingRequest,
        market_data: Dict[str, Any],
        scenarios: List[PriceScenario]
    ) -> MonteCarloSimulation:
        """Perform Monte Carlo simulation for price forecasting."""
        logger.info("Performing Monte Carlo simulation")
        
        simulation_results = []
        
        for scenario in scenarios:
            scenario_results = []
            
            for _ in range(self.monte_carlo_iterations):
                # Generate random price variations
                random_prices = {}
                
                for forecast in scenario.price_forecasts:
                    # Generate random price based on volatility
                    volatility = self.volatility_factors.get(scenario.scenario_type, 0.2)
                    random_factor = random.gauss(1.0, volatility)
                    random_price = forecast.forecasted_price * random_factor
                    random_prices[forecast.product_name] = random_price
                
                # Calculate profit for this iteration
                profit = await self._calculate_profit_for_prices(
                    request, random_prices
                )
                
                scenario_results.append(profit)
            
            # Calculate statistics for this scenario
            scenario_stats = {
                'scenario_id': scenario.scenario_id,
                'scenario_name': scenario.scenario_name,
                'mean_profit': statistics.mean(scenario_results),
                'median_profit': statistics.median(scenario_results),
                'std_deviation': statistics.stdev(scenario_results),
                'min_profit': min(scenario_results),
                'max_profit': max(scenario_results),
                'confidence_intervals': self._calculate_confidence_intervals(scenario_results)
            }
            
            simulation_results.append(scenario_stats)
        
        return MonteCarloSimulation(
            simulation_id=str(uuid4()),
            iterations=self.monte_carlo_iterations,
            confidence_levels=self.confidence_levels,
            scenario_results=simulation_results,
            overall_statistics=self._calculate_overall_statistics(simulation_results),
            created_at=datetime.utcnow()
        )
    
    async def _perform_stochastic_modeling(
        self,
        request: PriceScenarioModelingRequest,
        market_data: Dict[str, Any],
        scenarios: List[PriceScenario]
    ) -> StochasticModel:
        """Perform stochastic modeling for price forecasting."""
        logger.info("Performing stochastic modeling")
        
        stochastic_results = []
        
        for scenario in scenarios:
            # Generate stochastic price paths
            price_paths = []
            
            for forecast in scenario.price_forecasts:
                # Generate multiple price paths using geometric Brownian motion
                price_path = self._generate_stochastic_price_path(
                    forecast.current_price,
                    forecast.forecasted_price,
                    self.volatility_factors.get(scenario.scenario_type, 0.2),
                    request.analysis_horizon_days
                )
                price_paths.append({
                    'product_name': forecast.product_name,
                    'price_path': price_path
                })
            
            # Calculate stochastic metrics
            stochastic_metrics = self._calculate_stochastic_metrics(
                price_paths, request
            )
            
            stochastic_results.append({
                'scenario_id': scenario.scenario_id,
                'scenario_name': scenario.scenario_name,
                'price_paths': price_paths,
                'stochastic_metrics': stochastic_metrics
            })
        
        return StochasticModel(
            model_id=str(uuid4()),
            model_type='geometric_brownian_motion',
            scenarios=stochastic_results,
            model_parameters={
                'drift_rate': 0.05,
                'volatility_factors': self.volatility_factors
            },
            created_at=datetime.utcnow()
        )
    
    async def _perform_sensitivity_analysis(
        self,
        request: PriceScenarioModelingRequest,
        market_data: Dict[str, Any],
        scenarios: List[PriceScenario]
    ) -> SensitivityAnalysis:
        """Perform sensitivity analysis for price changes."""
        logger.info("Performing sensitivity analysis")
        
        sensitivity_results = []
        
        # Test different price change percentages
        price_change_percentages = [-50, -25, -10, -5, 0, 5, 10, 25, 50]
        
        for scenario in scenarios:
            scenario_sensitivity = []
            
            for price_change_pct in price_change_percentages:
                # Calculate profit with modified prices
                modified_prices = {}
                
                for forecast in scenario.price_forecasts:
                    modified_price = forecast.forecasted_price * (1 + price_change_pct / 100)
                    modified_prices[forecast.product_name] = modified_price
                
                profit = await self._calculate_profit_for_prices(
                    request, modified_prices
                )
                
                scenario_sensitivity.append({
                    'price_change_percent': price_change_pct,
                    'profit': profit,
                    'profit_change': profit - scenario.scenario_metrics.net_profit
                })
            
            sensitivity_results.append({
                'scenario_id': scenario.scenario_id,
                'scenario_name': scenario.scenario_name,
                'sensitivity_data': scenario_sensitivity
            })
        
        return SensitivityAnalysis(
            analysis_id=str(uuid4()),
            price_change_percentages=price_change_percentages,
            scenario_results=sensitivity_results,
            sensitivity_metrics=self._calculate_sensitivity_metrics(sensitivity_results),
            created_at=datetime.utcnow()
        )
    
    async def _create_decision_tree(
        self,
        request: PriceScenarioModelingRequest,
        scenarios: List[PriceScenario],
        monte_carlo_results: MonteCarloSimulation
    ) -> DecisionTreeNode:
        """Create decision tree for scenario planning."""
        logger.info("Creating decision tree")
        
        # Root node
        root_node = DecisionTreeNode(
            node_id=str(uuid4()),
            node_type='root',
            decision_criteria='price_scenario_selection',
            description='Select optimal price scenario',
            children=[]
        )
        
        # Add scenario nodes
        for scenario in scenarios:
            scenario_node = DecisionTreeNode(
                node_id=str(uuid4()),
                node_type='scenario',
                decision_criteria=f'scenario_{scenario.scenario_type.value}',
                description=f"Scenario: {scenario.scenario_name}",
                expected_value=scenario.scenario_metrics.net_profit,
                probability=scenario.probability_distribution.mean_probability,
                risk_level=scenario.risk_assessment.overall_risk_level,
                children=[]
            )
            
            # Add action nodes for each scenario
            action_node = DecisionTreeNode(
                node_id=str(uuid4()),
                node_type='action',
                decision_criteria='fertilizer_purchase_timing',
                description='Optimal fertilizer purchase timing',
                expected_value=scenario.scenario_metrics.net_profit * 0.95,  # 5% discount for timing
                probability=0.8,
                risk_level='low',
                children=[]
            )
            
            scenario_node.children.append(action_node)
            root_node.children.append(scenario_node)
        
        return root_node
    
    async def _generate_scenario_recommendations(
        self,
        scenarios: List[PriceScenario],
        monte_carlo_results: MonteCarloSimulation,
        stochastic_results: StochasticModel,
        sensitivity_results: SensitivityAnalysis
    ) -> List[str]:
        """Generate comprehensive recommendations based on scenario analysis."""
        recommendations = []
        
        # Find best and worst scenarios
        best_scenario = max(scenarios, key=lambda s: s.scenario_metrics.net_profit)
        worst_scenario = min(scenarios, key=lambda s: s.scenario_metrics.net_profit)
        
        recommendations.append(f"Best case scenario: {best_scenario.scenario_name} with ${best_scenario.scenario_metrics.net_profit:,.2f} expected profit")
        recommendations.append(f"Worst case scenario: {worst_scenario.scenario_name} with ${worst_scenario.scenario_metrics.net_profit:,.2f} expected profit")
        
        # Risk-based recommendations
        high_risk_scenarios = [s for s in scenarios if s.risk_assessment.overall_risk_level in ['high', 'critical']]
        if high_risk_scenarios:
            recommendations.append(f"High risk scenarios identified: {', '.join([s.scenario_name for s in high_risk_scenarios])}")
            recommendations.append("Consider implementing risk mitigation strategies such as forward contracts or price hedging")
        
        # Monte Carlo recommendations
        best_monte_carlo = max(monte_carlo_results.scenario_results, key=lambda r: r['mean_profit'])
        recommendations.append(f"Monte Carlo simulation recommends: {best_monte_carlo['scenario_name']} with ${best_monte_carlo['mean_profit']:,.2f} mean profit")
        
        # Sensitivity analysis recommendations
        most_sensitive_scenario = max(sensitivity_results.scenario_results, 
                                   key=lambda r: max([abs(d['profit_change']) for d in r['sensitivity_data']]))
        recommendations.append(f"Most sensitive scenario to price changes: {most_sensitive_scenario['scenario_name']}")
        
        # Seasonal recommendations
        seasonal_scenarios = [s for s in scenarios if s.scenario_type == ScenarioType.SEASONAL_PATTERNS]
        if seasonal_scenarios:
            recommendations.append("Consider seasonal timing for fertilizer purchases to optimize costs")
        
        # Supply disruption recommendations
        supply_disruption_scenarios = [s for s in scenarios if s.scenario_type == ScenarioType.SUPPLY_DISRUPTION]
        if supply_disruption_scenarios:
            recommendations.append("Develop contingency plans for supply disruptions including alternative suppliers")
        
        return recommendations
    
    def _get_scenario_multipliers(self, scenario_type: ScenarioType) -> Dict[str, float]:
        """Get price multipliers for scenario type."""
        multipliers = {
            ScenarioType.BULL_MARKET: {'fertilizer': 1.2, 'crop': 1.3},
            ScenarioType.BEAR_MARKET: {'fertilizer': 0.8, 'crop': 0.7},
            ScenarioType.VOLATILE_MARKET: {'fertilizer': 1.1, 'crop': 0.9},
            ScenarioType.SEASONAL_PATTERNS: {'fertilizer': 1.05, 'crop': 1.0},
            ScenarioType.SUPPLY_DISRUPTION: {'fertilizer': 1.4, 'crop': 1.0},
            ScenarioType.BASELINE: {'fertilizer': 1.0, 'crop': 1.0}
        }
        return multipliers.get(scenario_type, {'fertilizer': 1.0, 'crop': 1.0})
    
    def _get_scenario_name(self, scenario_type: ScenarioType) -> str:
        """Get human-readable scenario name."""
        names = {
            ScenarioType.BULL_MARKET: "Bull Market Scenario",
            ScenarioType.BEAR_MARKET: "Bear Market Scenario",
            ScenarioType.VOLATILE_MARKET: "Volatile Market Scenario",
            ScenarioType.SEASONAL_PATTERNS: "Seasonal Patterns Scenario",
            ScenarioType.SUPPLY_DISRUPTION: "Supply Disruption Scenario",
            ScenarioType.BASELINE: "Baseline Scenario"
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
            ScenarioType.BASELINE: MarketCondition.STABLE
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
            ScenarioType.BASELINE: "Current market conditions with moderate price stability"
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
            }
        }
        return assumptions.get(scenario_type, {})
    
    async def _generate_price_forecast(
        self,
        base_price: FertilizerPriceData,
        multipliers: Dict[str, float],
        scenario_type: ScenarioType,
        request: PriceScenarioModelingRequest
    ) -> PriceForecast:
        """Generate price forecast for a product."""
        forecasted_price = base_price.price_per_unit * multipliers['fertilizer']
        price_change_percent = (multipliers['fertilizer'] - 1.0) * 100
        
        # Adjust confidence based on scenario type
        confidence_levels = {
            ScenarioType.BULL_MARKET: 0.8,
            ScenarioType.BEAR_MARKET: 0.8,
            ScenarioType.VOLATILE_MARKET: 0.6,
            ScenarioType.SEASONAL_PATTERNS: 0.9,
            ScenarioType.SUPPLY_DISRUPTION: 0.5,
            ScenarioType.BASELINE: 0.95
        }
        
        confidence = confidence_levels.get(scenario_type, 0.8)
        volatility = self.volatility_factors.get(scenario_type, 0.2)
        
        return PriceForecast(
            product_name=base_price.product.name,
            current_price=base_price.price_per_unit,
            forecasted_price=forecasted_price,
            price_change_percent=price_change_percent,
            confidence_level=confidence,
            forecast_horizon_days=request.analysis_horizon_days,
            volatility_factor=volatility
        )
    
    async def _calculate_scenario_metrics(
        self,
        request: PriceScenarioModelingRequest,
        price_forecasts: List[PriceForecast],
        multipliers: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calculate scenario metrics."""
        # Calculate fertilizer costs
        total_fertilizer_cost = 0
        for fertilizer_req in request.fertilizer_requirements:
            product_name = fertilizer_req['product']
            rate_lbs_per_acre = fertilizer_req['rate_lbs_per_acre']
            
            # Find corresponding price forecast
            forecast = next((f for f in price_forecasts if f.product_name == product_name), None)
            if forecast:
                cost_per_acre = (rate_lbs_per_acre / 2000) * forecast.forecasted_price  # Convert to tons
                total_fertilizer_cost += cost_per_acre
        
        total_fertilizer_cost *= request.field_size_acres
        
        # Calculate crop revenue
        total_crop_revenue = (
            request.expected_yield_bu_per_acre * 
            request.crop_price_per_bu * 
            multipliers['crop'] * 
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
        scenario_type: ScenarioType,
        request: PriceScenarioModelingRequest
    ) -> ProbabilityDistribution:
        """Generate probability distribution for scenario."""
        # Base probabilities for different scenario types
        base_probabilities = {
            ScenarioType.BULL_MARKET: 0.15,
            ScenarioType.BEAR_MARKET: 0.15,
            ScenarioType.VOLATILE_MARKET: 0.20,
            ScenarioType.SEASONAL_PATTERNS: 0.30,
            ScenarioType.SUPPLY_DISRUPTION: 0.10,
            ScenarioType.BASELINE: 0.10
        }
        
        mean_probability = base_probabilities.get(scenario_type, 0.1)
        std_deviation = 0.05
        
        # Calculate confidence intervals
        confidence_intervals = {}
        for confidence in self.confidence_levels:
            z_score = self._get_z_score(confidence)
            margin_of_error = z_score * std_deviation
            confidence_intervals[str(confidence)] = mean_probability + margin_of_error
        
        return ProbabilityDistribution(
            mean_probability=mean_probability,
            standard_deviation=std_deviation,
            confidence_intervals=confidence_intervals
        )
    
    async def _generate_risk_assessment(
        self,
        scenario_type: ScenarioType,
        scenario_metrics: Dict[str, Any],
        request: PriceScenarioModelingRequest
    ) -> RiskAssessment:
        """Generate risk assessment for scenario."""
        # Risk levels based on scenario type
        risk_levels = {
            ScenarioType.BULL_MARKET: 'low',
            ScenarioType.BEAR_MARKET: 'high',
            ScenarioType.VOLATILE_MARKET: 'high',
            ScenarioType.SEASONAL_PATTERNS: 'medium',
            ScenarioType.SUPPLY_DISRUPTION: 'critical',
            ScenarioType.BASELINE: 'low'
        }
        
        overall_risk = risk_levels.get(scenario_type, 'medium')
        
        # Calculate individual risk factors
        price_volatility_risk = self.volatility_factors.get(scenario_type, 0.2)
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
        
        return RiskAssessment(
            overall_risk_level=overall_risk,
            price_volatility_risk=price_volatility_risk,
            supply_chain_risk=supply_chain_risk,
            market_demand_risk=market_demand_risk,
            economic_risk=economic_risk,
            risk_factors=risk_factors
        )
    
    def _generate_stochastic_price_path(
        self,
        current_price: float,
        target_price: float,
        volatility: float,
        horizon_days: int
    ) -> List[float]:
        """Generate stochastic price path using geometric Brownian motion."""
        price_path = [current_price]
        dt = 1.0 / 365  # Daily time step
        drift = math.log(target_price / current_price) / (horizon_days / 365)
        
        for _ in range(horizon_days):
            # Generate random shock
            random_shock = random.gauss(0, 1)
            
            # Calculate price change
            price_change = drift * dt + volatility * math.sqrt(dt) * random_shock
            
            # Update price
            new_price = price_path[-1] * math.exp(price_change)
            price_path.append(new_price)
        
        return price_path
    
    def _calculate_stochastic_metrics(
        self,
        price_paths: List[Dict[str, Any]],
        request: PriceScenarioModelingRequest
    ) -> Dict[str, Any]:
        """Calculate stochastic modeling metrics."""
        metrics = {
            'price_paths_count': len(price_paths),
            'average_final_price': 0,
            'price_volatility': 0,
            'price_trend': 'stable'
        }
        
        if price_paths:
            # Calculate average final price across all paths
            final_prices = [path['price_path'][-1] for path in price_paths]
            metrics['average_final_price'] = statistics.mean(final_prices)
            metrics['price_volatility'] = statistics.stdev(final_prices)
            
            # Determine trend
            if metrics['average_final_price'] > price_paths[0]['price_path'][0] * 1.05:
                metrics['price_trend'] = 'increasing'
            elif metrics['average_final_price'] < price_paths[0]['price_path'][0] * 0.95:
                metrics['price_trend'] = 'decreasing'
        
        return metrics
    
    def _calculate_sensitivity_metrics(
        self,
        sensitivity_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate sensitivity analysis metrics."""
        metrics = {
            'most_sensitive_scenario': None,
            'average_sensitivity': 0,
            'sensitivity_range': 0
        }
        
        if sensitivity_results:
            sensitivities = []
            for result in sensitivity_results:
                scenario_sensitivity = max([abs(d['profit_change']) for d in result['sensitivity_data']])
                sensitivities.append(scenario_sensitivity)
            
            if sensitivities:
                metrics['average_sensitivity'] = statistics.mean(sensitivities)
                metrics['sensitivity_range'] = max(sensitivities) - min(sensitivities)
                
                # Find most sensitive scenario
                most_sensitive_idx = sensitivities.index(max(sensitivities))
                metrics['most_sensitive_scenario'] = sensitivity_results[most_sensitive_idx]['scenario_name']
        
        return metrics
    
    def _calculate_confidence_intervals(self, results: List[float]) -> Dict[str, float]:
        """Calculate confidence intervals for Monte Carlo results."""
        sorted_results = sorted(results)
        n = len(sorted_results)
        
        intervals = {}
        for confidence in self.confidence_levels:
            alpha = 1 - confidence
            lower_idx = int(alpha / 2 * n)
            upper_idx = int((1 - alpha / 2) * n)
            
            intervals[str(confidence)] = {
                'lower': sorted_results[lower_idx],
                'upper': sorted_results[upper_idx]
            }
        
        return intervals
    
    def _calculate_overall_statistics(
        self,
        simulation_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate overall statistics for Monte Carlo simulation."""
        all_profits = []
        for result in simulation_results:
            all_profits.extend([result['mean_profit']] * 100)  # Weight by iterations
        
        return {
            'overall_mean_profit': statistics.mean(all_profits),
            'overall_std_deviation': statistics.stdev(all_profits),
            'overall_min_profit': min(all_profits),
            'overall_max_profit': max(all_profits),
            'total_scenarios': len(simulation_results)
        }
    
    async def _calculate_profit_for_prices(
        self,
        request: PriceScenarioModelingRequest,
        prices: Dict[str, float]
    ) -> float:
        """Calculate profit for given prices."""
        total_fertilizer_cost = 0
        
        for fertilizer_req in request.fertilizer_requirements:
            product_name = fertilizer_req['product']
            rate_lbs_per_acre = fertilizer_req['rate_lbs_per_acre']
            
            if product_name in prices:
                cost_per_acre = (rate_lbs_per_acre / 2000) * prices[product_name]
                total_fertilizer_cost += cost_per_acre
        
        total_fertilizer_cost *= request.field_size_acres
        
        total_crop_revenue = (
            request.expected_yield_bu_per_acre * 
            request.crop_price_per_bu * 
            request.field_size_acres
        )
        
        return total_crop_revenue - total_fertilizer_cost
    
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