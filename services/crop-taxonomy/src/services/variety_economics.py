"""
Variety Economic Analysis Service

Comprehensive economic viability scoring for crop varieties including:
- Net Present Value (NPV) calculations
- Internal Rate of Return (IRR) analysis
- Payback period calculations
- Break-even analysis
- Risk-adjusted returns
- Government program integration
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, date, timedelta
from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_HALF_UP
import statistics
import math
import random
import numpy as np
from enum import Enum

try:
    from ..models.crop_variety_models import (
        EnhancedCropVariety,
        VarietyRecommendation,
        RiskLevel,
        MarketDemand
    )
    from ..models.service_models import (
        ConfidenceLevel
    )
except ImportError:
    from models.crop_variety_models import (
        EnhancedCropVariety,
        VarietyRecommendation,
        RiskLevel,
        MarketDemand
    )
    from models.service_models import (
        ConfidenceLevel
    )

logger = logging.getLogger(__name__)


class ScenarioType(Enum):
    """Types of economic scenarios for analysis."""
    BASE_CASE = "base_case"
    OPTIMISTIC = "optimistic"
    PESSIMISTIC = "pessimistic"


class RiskLevel(Enum):
    """Risk levels for investment analysis."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class ScenarioAnalysis:
    """Analysis results for a specific scenario."""
    scenario_type: ScenarioType
    net_present_value: float
    internal_rate_of_return: float
    payback_period_years: float
    expected_profit_per_acre: float
    probability_of_profit: float
    confidence_interval_95: Tuple[float, float]


@dataclass
class MonteCarloResult:
    """Results from Monte Carlo simulation."""
    mean_npv: float
    median_npv: float
    std_deviation_npv: float
    probability_of_positive_npv: float
    value_at_risk_95: float
    expected_shortfall: float
    simulation_iterations: int
    confidence_intervals: Dict[str, Tuple[float, float]]


@dataclass
class InvestmentRecommendation:
    """Investment recommendation based on ROI analysis."""
    recommendation_type: str  # "strong_buy", "buy", "hold", "sell", "strong_sell"
    confidence_score: float
    risk_level: RiskLevel
    expected_return_percent: float
    payback_period_years: float
    key_factors: List[str]
    risk_factors: List[str]
    mitigation_strategies: List[str]


@dataclass
class SophisticatedROIAnalysis:
    """Comprehensive ROI and profitability analysis result."""
    variety_id: str
    variety_name: str
    
    # Multi-year analysis
    analysis_horizon_years: int
    annual_cash_flows: List[float]
    cumulative_cash_flows: List[float]
    
    # Scenario analysis
    base_case: ScenarioAnalysis
    optimistic: ScenarioAnalysis
    pessimistic: ScenarioAnalysis
    
    # Monte Carlo simulation
    monte_carlo_results: MonteCarloResult
    
    # Risk assessment
    weather_risk_score: float
    market_volatility_risk: float
    yield_volatility_risk: float
    overall_risk_score: float
    
    # Investment recommendation
    investment_recommendation: InvestmentRecommendation
    
    # Financial metrics
    net_present_value: float
    internal_rate_of_return: float
    modified_internal_rate_of_return: float
    profitability_index: float
    discounted_payback_period: float
    
    # Analysis metadata
    analysis_date: datetime
    assumptions_used: Dict[str, Any]
    data_sources: List[str]


@dataclass
class EconomicAnalysisResult:
    """Comprehensive economic analysis result for a variety."""
    
    variety_id: str
    variety_name: str
    
    # Financial Metrics
    net_present_value: float
    internal_rate_of_return: float
    payback_period_years: float
    break_even_yield: float
    break_even_price: float
    
    # Cost Analysis
    total_seed_cost_per_acre: float
    total_input_costs_per_acre: float
    total_operating_costs_per_acre: float
    
    # Revenue Analysis
    expected_revenue_per_acre: float
    expected_profit_per_acre: float
    profit_margin_percent: float
    
    # Risk Analysis
    risk_adjusted_return: float
    volatility_score: float
    downside_risk: float
    
    # Government Programs
    government_subsidies_per_acre: float
    insurance_coverage_percent: float
    
    # Overall Economic Score (0-1)
    economic_viability_score: float
    confidence_level: ConfidenceLevel
    
    # Analysis Metadata
    analysis_date: datetime
    market_data_source: str
    assumptions_used: Dict[str, Any]


@dataclass
class CostFactors:
    """Detailed cost factors for economic analysis."""
    
    seed_cost_per_unit: float
    seeding_rate_per_acre: float
    fertilizer_cost_per_acre: float
    pesticide_cost_per_acre: float
    fuel_cost_per_acre: float
    labor_cost_per_acre: float
    equipment_cost_per_acre: float
    insurance_cost_per_acre: float
    other_inputs_cost_per_acre: float
    
    def total_cost_per_acre(self) -> float:
        """Calculate total cost per acre."""
        return (
            self.seed_cost_per_unit * self.seeding_rate_per_acre +
            self.fertilizer_cost_per_acre +
            self.pesticide_cost_per_acre +
            self.fuel_cost_per_acre +
            self.labor_cost_per_acre +
            self.equipment_cost_per_acre +
            self.insurance_cost_per_acre +
            self.other_inputs_cost_per_acre
        )


@dataclass
class RevenueFactors:
    """Revenue factors for economic analysis."""
    
    expected_yield_per_acre: float
    market_price_per_unit: float
    premium_price_per_unit: Optional[float] = None
    premium_yield_percent: Optional[float] = None
    government_subsidies_per_acre: float = 0.0
    insurance_payout_per_acre: float = 0.0
    
    def total_revenue_per_acre(self) -> float:
        """Calculate total revenue per acre."""
        base_revenue = self.expected_yield_per_acre * self.market_price_per_unit
        
        # Add premium if applicable
        if self.premium_price_per_unit and self.premium_yield_percent:
            premium_revenue = (
                self.expected_yield_per_acre * 
                (self.premium_yield_percent / 100) * 
                self.premium_price_per_unit
            )
            base_revenue += premium_revenue
        
        # Add government subsidies
        base_revenue += self.government_subsidies_per_acre
        
        # Add insurance payouts
        base_revenue += self.insurance_payout_per_acre
        
        return base_revenue


class VarietyEconomicAnalysisService:
    """
    Service for comprehensive economic viability analysis of crop varieties.
    
    Provides advanced economic scoring including NPV, IRR, payback period,
    break-even analysis, and risk-adjusted returns with government program integration.
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize the economic analysis service."""
        self.database_url = database_url
        
        # Initialize market price service integration
        try:
            from ...recommendation_engine.src.services.market_price_service import MarketPriceService
            self.market_price_service = MarketPriceService()
            logger.info("Market price service integration successful")
        except ImportError:
            logger.warning("Market price service not available - using fallback pricing")
            self.market_price_service = None
        
        # Economic analysis parameters
        self.discount_rate = 0.08  # 8% default discount rate
        self.analysis_horizon_years = 5  # 5-year analysis period
        self.risk_free_rate = 0.03  # 3% risk-free rate
        
        # Cost factor defaults (per acre, in USD)
        self.default_cost_factors = {
            'corn': CostFactors(
                seed_cost_per_unit=0.35,
                seeding_rate_per_acre=32000,
                fertilizer_cost_per_acre=120.0,
                pesticide_cost_per_acre=45.0,
                fuel_cost_per_acre=25.0,
                labor_cost_per_acre=15.0,
                equipment_cost_per_acre=35.0,
                insurance_cost_per_acre=12.0,
                other_inputs_cost_per_acre=20.0
            ),
            'soybean': CostFactors(
                seed_cost_per_unit=0.55,
                seeding_rate_per_acre=140000,
                fertilizer_cost_per_acre=80.0,
                pesticide_cost_per_acre=35.0,
                fuel_cost_per_acre=20.0,
                labor_cost_per_acre=12.0,
                equipment_cost_per_acre=30.0,
                insurance_cost_per_acre=10.0,
                other_inputs_cost_per_acre=15.0
            ),
            'wheat': CostFactors(
                seed_cost_per_unit=0.25,
                seeding_rate_per_acre=1200000,
                fertilizer_cost_per_acre=60.0,
                pesticide_cost_per_acre=25.0,
                fuel_cost_per_acre=18.0,
                labor_cost_per_acre=10.0,
                equipment_cost_per_acre=25.0,
                insurance_cost_per_acre=8.0,
                other_inputs_cost_per_acre=12.0
            )
        }
        
        # Government program data (simplified)
        self.government_programs = {
            'corn': {
                'price_loss_coverage': 3.70,  # per bushel
                'agricultural_risk_coverage': 0.15,  # per acre
                'conservation_reserve_program': 0.0  # varies by region
            },
            'soybean': {
                'price_loss_coverage': 8.40,  # per bushel
                'agricultural_risk_coverage': 0.12,  # per acre
                'conservation_reserve_program': 0.0
            },
            'wheat': {
                'price_loss_coverage': 5.50,  # per bushel
                'agricultural_risk_coverage': 0.10,  # per acre
                'conservation_reserve_program': 0.0
            }
        }
    
    async def analyze_variety_economics(
        self,
        variety: EnhancedCropVariety,
        regional_context: Dict[str, Any],
        farmer_preferences: Optional[Dict[str, Any]] = None
    ) -> EconomicAnalysisResult:
        """
        Perform comprehensive economic analysis for a crop variety.
        
        Args:
            variety: The crop variety to analyze
            regional_context: Regional growing conditions and market data
            farmer_preferences: Optional farmer-specific preferences
            
        Returns:
            Comprehensive economic analysis result
        """
        try:
            # Get market data
            market_data = await self._get_market_data(variety, regional_context)
            
            # Calculate cost factors
            cost_factors = await self._calculate_cost_factors(variety, regional_context)
            
            # Calculate revenue factors
            revenue_factors = await self._calculate_revenue_factors(
                variety, regional_context, market_data
            )
            
            # Perform financial calculations
            npv = self._calculate_npv(cost_factors, revenue_factors)
            irr = self._calculate_irr(cost_factors, revenue_factors)
            payback_period = self._calculate_payback_period(cost_factors, revenue_factors)
            break_even_yield = self._calculate_break_even_yield(cost_factors, market_data)
            break_even_price = self._calculate_break_even_price(cost_factors, revenue_factors)
            
            # Calculate risk metrics
            risk_adjusted_return = self._calculate_risk_adjusted_return(
                revenue_factors, regional_context
            )
            volatility_score = self._calculate_volatility_score(market_data)
            downside_risk = self._calculate_downside_risk(revenue_factors, cost_factors)
            
            # Calculate government program benefits
            government_subsidies = await self._calculate_government_subsidies(
                variety, regional_context
            )
            
            # Calculate overall economic viability score
            economic_score = self._calculate_economic_viability_score(
                npv, irr, payback_period, risk_adjusted_return, volatility_score
            )
            
            # Determine confidence level
            confidence_level = self._determine_confidence_level(
                market_data, variety, regional_context
            )
            
            return EconomicAnalysisResult(
                variety_id=str(variety.variety_id) if variety.variety_id else variety.variety_name,
                variety_name=variety.variety_name,
                net_present_value=npv,
                internal_rate_of_return=irr,
                payback_period_years=payback_period,
                break_even_yield=break_even_yield,
                break_even_price=break_even_price,
                total_seed_cost_per_acre=cost_factors.seed_cost_per_unit * cost_factors.seeding_rate_per_acre,
                total_input_costs_per_acre=cost_factors.total_cost_per_acre(),
                total_operating_costs_per_acre=cost_factors.total_cost_per_acre(),
                expected_revenue_per_acre=revenue_factors.total_revenue_per_acre(),
                expected_profit_per_acre=revenue_factors.total_revenue_per_acre() - cost_factors.total_cost_per_acre(),
                profit_margin_percent=self._calculate_profit_margin(cost_factors, revenue_factors),
                risk_adjusted_return=risk_adjusted_return,
                volatility_score=volatility_score,
                downside_risk=downside_risk,
                government_subsidies_per_acre=government_subsidies,
                insurance_coverage_percent=self._calculate_insurance_coverage(variety, regional_context),
                economic_viability_score=economic_score,
                confidence_level=confidence_level,
                analysis_date=datetime.utcnow(),
                market_data_source=market_data.get('source', 'fallback'),
                assumptions_used=self._get_analysis_assumptions(variety, regional_context)
            )
            
        except Exception as e:
            logger.error(f"Error in economic analysis for variety {variety.variety_id}: {e}")
            raise
    
    async def _get_market_data(
        self, 
        variety: EnhancedCropVariety, 
        regional_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get current market data for the variety's crop."""
        crop_name = regional_context.get('crop_name', 'corn').lower()
        region = regional_context.get('region', 'US')
        
        # Try to get real-time market data
        if self.market_price_service:
            try:
                price_data = await self.market_price_service.get_current_price(crop_name, region)
                if price_data:
                    return {
                        'price_per_unit': price_data.price_per_unit,
                        'volatility': price_data.volatility,
                        'source': price_data.source,
                        'confidence': price_data.confidence
                    }
            except Exception as e:
                logger.warning(f"Market price service error: {e}")
        
        # Fallback to static pricing
        fallback_prices = {
            'corn': {'price_per_unit': 4.25, 'volatility': 0.15},
            'soybean': {'price_per_unit': 12.50, 'volatility': 0.18},
            'wheat': {'price_per_unit': 6.80, 'volatility': 0.22},
            'oats': {'price_per_unit': 3.20, 'volatility': 0.25},
            'alfalfa': {'price_per_unit': 180.0, 'volatility': 0.12},
            'barley': {'price_per_unit': 4.50, 'volatility': 0.20}
        }
        
        return {
            'price_per_unit': fallback_prices.get(crop_name, {}).get('price_per_unit', 5.0),
            'volatility': fallback_prices.get(crop_name, {}).get('volatility', 0.20),
            'source': 'fallback',
            'confidence': 0.5
        }
    
    async def _calculate_cost_factors(
        self, 
        variety: EnhancedCropVariety, 
        regional_context: Dict[str, Any]
    ) -> CostFactors:
        """Calculate detailed cost factors for the variety."""
        crop_name = regional_context.get('crop_name', 'corn').lower()
        
        # Get base cost factors
        base_costs = self.default_cost_factors.get(crop_name, self.default_cost_factors['corn'])
        
        # Adjust for variety-specific factors
        adjusted_costs = CostFactors(
            seed_cost_per_unit=self._adjust_seed_cost(variety, base_costs.seed_cost_per_unit),
            seeding_rate_per_acre=self._adjust_seeding_rate(variety, base_costs.seeding_rate_per_acre),
            fertilizer_cost_per_acre=self._adjust_fertilizer_cost(variety, base_costs.fertilizer_cost_per_acre),
            pesticide_cost_per_acre=self._adjust_pesticide_cost(variety, base_costs.pesticide_cost_per_acre),
            fuel_cost_per_acre=base_costs.fuel_cost_per_acre,
            labor_cost_per_acre=base_costs.labor_cost_per_acre,
            equipment_cost_per_acre=base_costs.equipment_cost_per_acre,
            insurance_cost_per_acre=self._adjust_insurance_cost(variety, base_costs.insurance_cost_per_acre),
            other_inputs_cost_per_acre=base_costs.other_inputs_cost_per_acre
        )
        
        return adjusted_costs
    
    def _adjust_seed_cost(self, variety: EnhancedCropVariety, base_cost: float) -> float:
        """Adjust seed cost based on variety characteristics."""
        multiplier = 1.0
        
        # Adjust for market acceptance score (higher score = premium variety)
        if variety.market_acceptance_score:
            if variety.market_acceptance_score > 4.0:
                multiplier = 1.3  # Premium variety
            elif variety.market_acceptance_score > 3.0:
                multiplier = 1.15  # High-end variety
            elif variety.market_acceptance_score < 2.0:
                multiplier = 0.85  # Lower-cost variety
        
        # Adjust for yield potential (higher potential = premium pricing)
        if variety.yield_potential_percentile:
            if variety.yield_potential_percentile > 90:
                multiplier *= 1.1
            elif variety.yield_potential_percentile < 50:
                multiplier *= 0.9
        
        return base_cost * multiplier
    
    def _adjust_seeding_rate(self, variety: EnhancedCropVariety, base_rate: float) -> float:
        """Adjust seeding rate based on variety characteristics."""
        # Most varieties use standard seeding rates
        return base_rate
    
    def _adjust_fertilizer_cost(self, variety: EnhancedCropVariety, base_cost: float) -> float:
        """Adjust fertilizer cost based on variety characteristics."""
        multiplier = 1.0
        
        # Adjust for yield potential (higher yield = more fertilizer)
        if variety.yield_potential_percentile:
            if variety.yield_potential_percentile > 90:
                multiplier = 1.15
            elif variety.yield_potential_percentile < 50:
                multiplier = 0.9
        
        return base_cost * multiplier
    
    def _adjust_pesticide_cost(self, variety: EnhancedCropVariety, base_cost: float) -> float:
        """Adjust pesticide cost based on disease resistance."""
        multiplier = 1.0
        
        # Better disease resistance = lower pesticide costs
        if variety.disease_resistances:
            # Count number of disease resistances
            resistance_count = len(variety.disease_resistances)
            if resistance_count > 5:
                multiplier = 0.8  # High resistance = lower costs
            elif resistance_count < 2:
                multiplier = 1.2  # Low resistance = higher costs
        
        return base_cost * multiplier
    
    def _adjust_insurance_cost(self, variety: EnhancedCropVariety, base_cost: float) -> float:
        """Adjust insurance cost based on variety risk profile."""
        multiplier = 1.0
        
        # Higher risk varieties = higher insurance costs
        # Use yield stability as proxy for risk
        if variety.yield_stability_rating:
            if variety.yield_stability_rating < 5.0:
                multiplier = 1.2  # Low stability = higher risk
            elif variety.yield_stability_rating > 8.0:
                multiplier = 0.9  # High stability = lower risk
        
        return base_cost * multiplier
    
    def _calculate_disease_resistance_score(self, disease_profile) -> float:
        """Calculate overall disease resistance score."""
        if not disease_profile:
            return 0.5
        
        # Simplified scoring - in production, would use detailed resistance data
        return 0.7  # Default moderate resistance
    
    async def _calculate_revenue_factors(
        self, 
        variety: EnhancedCropVariety, 
        regional_context: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> RevenueFactors:
        """Calculate revenue factors for the variety."""
        
        # Calculate expected yield
        expected_yield = await self._calculate_expected_yield(variety, regional_context)
        
        # Get market price
        market_price = market_data['price_per_unit']
        
        # Calculate premium potential
        premium_price = None
        premium_yield_percent = None
        if variety.market_acceptance_score and variety.market_acceptance_score > 3.0:
            premium_price = market_price * 1.1  # 10% premium
            premium_yield_percent = 5.0  # 5% of yield gets premium
        
        # Calculate government subsidies
        government_subsidies = await self._calculate_government_subsidies(variety, regional_context)
        
        return RevenueFactors(
            expected_yield_per_acre=expected_yield,
            market_price_per_unit=market_price,
            premium_price_per_unit=premium_price,
            premium_yield_percent=premium_yield_percent,
            government_subsidies_per_acre=government_subsidies
        )
    
    async def _calculate_expected_yield(
        self, 
        variety: EnhancedCropVariety, 
        regional_context: Dict[str, Any]
    ) -> float:
        """Calculate expected yield per acre for the variety."""
        
        # Base yield from variety data
        base_yield = 0.0
        if variety.yield_potential_percentile:
            # Convert percentile to actual yield estimate
            crop_name = regional_context.get('crop_name', 'corn').lower() if hasattr(variety, 'crop_name') else 'corn'
            regional_averages = {
                'corn': 175.0,  # bushels per acre
                'soybean': 50.0,  # bushels per acre
                'wheat': 65.0,  # bushels per acre
                'oats': 80.0,  # bushels per acre
                'alfalfa': 4.5,  # tons per acre
                'barley': 70.0  # bushels per acre
            }
            base_average = regional_averages.get(crop_name, 50.0)
            # Convert percentile to yield (simplified)
            base_yield = base_average * (variety.yield_potential_percentile / 100.0)
        
        # If no yield data, use regional averages
        if base_yield == 0.0:
            crop_name = regional_context.get('crop_name', 'corn').lower() if hasattr(variety, 'crop_name') else 'corn'
            regional_averages = {
                'corn': 175.0,  # bushels per acre
                'soybean': 50.0,  # bushels per acre
                'wheat': 65.0,  # bushels per acre
                'oats': 80.0,  # bushels per acre
                'alfalfa': 4.5,  # tons per acre
                'barley': 70.0  # bushels per acre
            }
            base_yield = regional_averages.get(crop_name, 50.0)
        
        # Adjust for regional conditions
        regional_multiplier = regional_context.get('yield_multiplier', 1.0)
        
        return base_yield * regional_multiplier
    
    def _calculate_npv(self, cost_factors: CostFactors, revenue_factors: RevenueFactors) -> float:
        """Calculate Net Present Value over analysis horizon."""
        annual_cash_flow = revenue_factors.total_revenue_per_acre() - cost_factors.total_cost_per_acre()
        
        npv = 0.0
        for year in range(1, self.analysis_horizon_years + 1):
            discounted_cash_flow = annual_cash_flow / ((1 + self.discount_rate) ** year)
            npv += discounted_cash_flow
        
        return npv
    
    def _calculate_irr(self, cost_factors: CostFactors, revenue_factors: RevenueFactors) -> float:
        """Calculate Internal Rate of Return."""
        annual_cash_flow = revenue_factors.total_revenue_per_acre() - cost_factors.total_cost_per_acre()
        
        # Simple IRR calculation (in production, would use more sophisticated method)
        if annual_cash_flow <= 0:
            return 0.0
        
        # Approximate IRR calculation
        initial_investment = cost_factors.total_cost_per_acre()
        irr = (annual_cash_flow / initial_investment) * 100
        
        return min(irr, 50.0)  # Cap at 50% for realism
    
    def _calculate_payback_period(self, cost_factors: CostFactors, revenue_factors: RevenueFactors) -> float:
        """Calculate payback period in years."""
        annual_cash_flow = revenue_factors.total_revenue_per_acre() - cost_factors.total_cost_per_acre()
        
        if annual_cash_flow <= 0:
            return float('inf')
        
        initial_investment = cost_factors.total_cost_per_acre()
        payback_period = initial_investment / annual_cash_flow
        
        return payback_period
    
    def _calculate_break_even_yield(self, cost_factors: CostFactors, market_data: Dict[str, Any]) -> float:
        """Calculate break-even yield per acre."""
        total_costs = cost_factors.total_cost_per_acre()
        market_price = market_data['price_per_unit']
        
        if market_price <= 0:
            return float('inf')
        
        return total_costs / market_price
    
    def _calculate_break_even_price(self, cost_factors: CostFactors, revenue_factors: RevenueFactors) -> float:
        """Calculate break-even price per unit."""
        total_costs = cost_factors.total_cost_per_acre()
        expected_yield = revenue_factors.expected_yield_per_acre
        
        if expected_yield <= 0:
            return float('inf')
        
        return total_costs / expected_yield
    
    def _calculate_risk_adjusted_return(
        self, 
        revenue_factors: RevenueFactors, 
        regional_context: Dict[str, Any]
    ) -> float:
        """Calculate risk-adjusted return using Sharpe ratio approach."""
        expected_return = revenue_factors.total_revenue_per_acre()
        volatility = regional_context.get('price_volatility', 0.15)
        
        if volatility <= 0:
            return expected_return
        
        # Simplified risk adjustment
        risk_adjusted_return = expected_return - (volatility * expected_return * 0.5)
        
        return max(0.0, risk_adjusted_return)
    
    def _calculate_volatility_score(self, market_data: Dict[str, Any]) -> float:
        """Calculate volatility score (0-1, lower is better)."""
        volatility = market_data.get('volatility', 0.20)
        
        # Convert volatility to score (invert so lower volatility = higher score)
        volatility_score = max(0.0, 1.0 - volatility)
        
        return volatility_score
    
    def _calculate_downside_risk(
        self, 
        revenue_factors: RevenueFactors, 
        cost_factors: CostFactors
    ) -> float:
        """Calculate downside risk (probability of loss)."""
        expected_profit = revenue_factors.total_revenue_per_acre() - cost_factors.total_cost_per_acre()
        
        if expected_profit <= 0:
            return 1.0  # 100% chance of loss
        
        # Simplified downside risk calculation
        # In production, would use historical data and Monte Carlo simulation
        downside_risk = max(0.0, min(1.0, 0.3 - (expected_profit / 1000)))
        
        return downside_risk
    
    async def _calculate_government_subsidies(
        self, 
        variety: EnhancedCropVariety, 
        regional_context: Dict[str, Any]
    ) -> float:
        """Calculate government subsidies per acre."""
        crop_name = regional_context.get('crop_name', 'corn').lower()
        
        if crop_name not in self.government_programs:
            return 0.0
        
        programs = self.government_programs[crop_name]
        
        # Calculate total subsidies (simplified)
        total_subsidies = 0.0
        for program, rate in programs.items():
            if program == 'price_loss_coverage':
                # Price loss coverage is per unit, not per acre
                continue
            total_subsidies += rate
        
        return total_subsidies
    
    def _calculate_insurance_coverage(
        self, 
        variety: EnhancedCropVariety, 
        regional_context: Dict[str, Any]
    ) -> float:
        """Calculate insurance coverage percentage."""
        # Simplified insurance calculation
        base_coverage = 0.75  # 75% base coverage
        
        # Adjust based on variety yield stability (proxy for risk)
        if variety.yield_stability_rating:
            if variety.yield_stability_rating < 5.0:
                base_coverage = 0.85  # Higher coverage for unstable varieties
            elif variety.yield_stability_rating > 8.0:
                base_coverage = 0.70  # Lower coverage for stable varieties
        
        return base_coverage
    
    def _calculate_profit_margin(self, cost_factors: CostFactors, revenue_factors: RevenueFactors) -> float:
        """Calculate profit margin percentage."""
        total_revenue = revenue_factors.total_revenue_per_acre()
        total_costs = cost_factors.total_cost_per_acre()
        
        if total_revenue <= 0:
            return 0.0
        
        profit_margin = ((total_revenue - total_costs) / total_revenue) * 100
        
        return max(0.0, profit_margin)
    
    def _calculate_economic_viability_score(
        self, 
        npv: float, 
        irr: float, 
        payback_period: float, 
        risk_adjusted_return: float, 
        volatility_score: float
    ) -> float:
        """Calculate overall economic viability score (0-1)."""
        
        # NPV score (0-1)
        npv_score = min(1.0, max(0.0, (npv + 1000) / 2000))  # Normalize around $1000 NPV
        
        # IRR score (0-1)
        irr_score = min(1.0, max(0.0, irr / 30.0))  # Normalize around 30% IRR
        
        # Payback period score (0-1, lower is better)
        payback_score = max(0.0, min(1.0, (5.0 - payback_period) / 5.0))
        
        # Risk-adjusted return score (0-1)
        risk_score = min(1.0, max(0.0, risk_adjusted_return / 1000))
        
        # Weighted combination
        economic_score = (
            npv_score * 0.3 +
            irr_score * 0.25 +
            payback_score * 0.2 +
            risk_score * 0.15 +
            volatility_score * 0.1
        )
        
        return max(0.0, min(1.0, economic_score))
    
    def _determine_confidence_level(
        self, 
        market_data: Dict[str, Any], 
        variety: EnhancedCropVariety, 
        regional_context: Dict[str, Any]
    ) -> ConfidenceLevel:
        """Determine confidence level for the economic analysis."""
        
        confidence_factors = []
        
        # Market data confidence
        market_confidence = market_data.get('confidence', 0.5)
        confidence_factors.append(market_confidence)
        
        # Variety data completeness
        variety_confidence = self._assess_variety_data_completeness(variety)
        confidence_factors.append(variety_confidence)
        
        # Regional data completeness
        regional_confidence = self._assess_regional_data_completeness(regional_context)
        confidence_factors.append(regional_confidence)
        
        # Calculate overall confidence
        overall_confidence = statistics.mean(confidence_factors)
        
        # Convert to confidence level
        if overall_confidence >= 0.8:
            return ConfidenceLevel.HIGH
        elif overall_confidence >= 0.6:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    def _assess_variety_data_completeness(self, variety: EnhancedCropVariety) -> float:
        """Assess completeness of variety data."""
        completeness_score = 0.0
        total_factors = 0
        
        # Check yield data
        total_factors += 1
        if variety.yield_potential_percentile:
            completeness_score += 1
        
        # Check market acceptance
        total_factors += 1
        if variety.market_acceptance_score:
            completeness_score += 1
        
        # Check disease resistance
        total_factors += 1
        if variety.disease_resistances:
            completeness_score += 1
        
        # Check yield stability
        total_factors += 1
        if variety.yield_stability_rating:
            completeness_score += 1
        
        return completeness_score / total_factors if total_factors > 0 else 0.5
    
    def _assess_regional_data_completeness(self, regional_context: Dict[str, Any]) -> float:
        """Assess completeness of regional data."""
        required_fields = ['region', 'climate_zone', 'soil_type']
        present_fields = sum(1 for field in required_fields if field in regional_context)
        
        return present_fields / len(required_fields)
    
    def _get_analysis_assumptions(
        self, 
        variety: EnhancedCropVariety, 
        regional_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get assumptions used in the economic analysis."""
        return {
            'discount_rate': self.discount_rate,
            'analysis_horizon_years': self.analysis_horizon_years,
            'risk_free_rate': self.risk_free_rate,
            'market_data_source': regional_context.get('market_data_source', 'fallback'),
            'cost_factors_source': 'default_regional_averages',
            'government_programs_included': True,
            'insurance_coverage_assumed': True,
            'premium_pricing_applied': variety.market_acceptance_score > 3.0 if variety.market_acceptance_score else False
        }
    
    async def compare_varieties_economics(
        self, 
        varieties: List[EnhancedCropVariety], 
        regional_context: Dict[str, Any],
        farmer_preferences: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[EnhancedCropVariety, EconomicAnalysisResult]]:
        """Compare economic viability of multiple varieties."""
        
        results = []
        
        for variety in varieties:
            try:
                analysis = await self.analyze_variety_economics(
                    variety, regional_context, farmer_preferences
                )
                results.append((variety, analysis))
            except Exception as e:
                logger.error(f"Error analyzing variety {variety.variety_id}: {e}")
                continue
        
        # Sort by economic viability score (descending)
        results.sort(key=lambda x: x[1].economic_viability_score, reverse=True)
        
        return results
    
    async def perform_sophisticated_roi_analysis(
        self,
        variety: EnhancedCropVariety,
        regional_context: Dict[str, Any],
        farmer_preferences: Optional[Dict[str, Any]] = None,
        analysis_horizon_years: int = 5
    ) -> SophisticatedROIAnalysis:
        """
        Perform sophisticated ROI and profitability analysis with advanced financial modeling.
        
        Features:
        - Multi-year ROI analysis
        - Scenario modeling (base case, optimistic, pessimistic)
        - Monte Carlo simulation for uncertainty quantification
        - Risk assessment with weather and market volatility
        - Investment recommendations
        
        Args:
            variety: The crop variety to analyze
            regional_context: Regional growing conditions and market data
            farmer_preferences: Optional farmer-specific preferences
            analysis_horizon_years: Number of years for analysis (default: 5)
            
        Returns:
            Comprehensive ROI and profitability analysis
        """
        try:
            logger.info(f"Starting sophisticated ROI analysis for variety {variety.variety_name}")
            
            # Get base economic analysis
            base_analysis = await self.analyze_variety_economics(
                variety, regional_context, farmer_preferences
            )
            
            # Perform scenario analysis
            scenario_results = await self._perform_scenario_analysis(
                variety, regional_context, farmer_preferences, analysis_horizon_years
            )
            
            # Perform Monte Carlo simulation
            monte_carlo_results = await self._perform_monte_carlo_simulation(
                variety, regional_context, farmer_preferences, analysis_horizon_years
            )
            
            # Calculate risk assessments
            risk_assessments = await self._calculate_comprehensive_risk_assessment(
                variety, regional_context, farmer_preferences
            )
            
            # Generate investment recommendation
            investment_recommendation = await self._generate_investment_recommendation(
                base_analysis, scenario_results, monte_carlo_results, risk_assessments
            )
            
            # Calculate advanced financial metrics
            advanced_metrics = await self._calculate_advanced_financial_metrics(
                variety, regional_context, farmer_preferences, analysis_horizon_years
            )
            
            # Generate annual cash flows
            annual_cash_flows = await self._generate_annual_cash_flows(
                variety, regional_context, farmer_preferences, analysis_horizon_years
            )
            
            return SophisticatedROIAnalysis(
                variety_id=str(variety.variety_id) if variety.variety_id else variety.variety_name,
                variety_name=variety.variety_name,
                analysis_horizon_years=analysis_horizon_years,
                annual_cash_flows=annual_cash_flows,
                cumulative_cash_flows=self._calculate_cumulative_cash_flows(annual_cash_flows),
                base_case=scenario_results['base_case'],
                optimistic=scenario_results['optimistic'],
                pessimistic=scenario_results['pessimistic'],
                monte_carlo_results=monte_carlo_results,
                weather_risk_score=risk_assessments['weather_risk'],
                market_volatility_risk=risk_assessments['market_volatility'],
                yield_volatility_risk=risk_assessments['yield_volatility'],
                overall_risk_score=risk_assessments['overall_risk'],
                investment_recommendation=investment_recommendation,
                net_present_value=advanced_metrics['npv'],
                internal_rate_of_return=advanced_metrics['irr'],
                modified_internal_rate_of_return=advanced_metrics['mirr'],
                profitability_index=advanced_metrics['pi'],
                discounted_payback_period=advanced_metrics['discounted_payback'],
                analysis_date=datetime.utcnow(),
                assumptions_used=self._get_sophisticated_analysis_assumptions(
                    variety, regional_context, analysis_horizon_years
                ),
                data_sources=self._get_data_sources_used(regional_context)
            )
            
        except Exception as e:
            logger.error(f"Error in sophisticated ROI analysis for variety {variety.variety_id}: {e}")
            raise
    
    async def _perform_scenario_analysis(
        self,
        variety: EnhancedCropVariety,
        regional_context: Dict[str, Any],
        farmer_preferences: Optional[Dict[str, Any]],
        analysis_horizon_years: int
    ) -> Dict[str, ScenarioAnalysis]:
        """Perform scenario analysis (base case, optimistic, pessimistic)."""
        
        scenarios = {}
        
        # Base case scenario
        base_case_data = await self._get_scenario_data(
            variety, regional_context, ScenarioType.BASE_CASE
        )
        scenarios['base_case'] = await self._analyze_scenario(
            variety, base_case_data, ScenarioType.BASE_CASE, analysis_horizon_years
        )
        
        # Optimistic scenario
        optimistic_data = await self._get_scenario_data(
            variety, regional_context, ScenarioType.OPTIMISTIC
        )
        scenarios['optimistic'] = await self._analyze_scenario(
            variety, optimistic_data, ScenarioType.OPTIMISTIC, analysis_horizon_years
        )
        
        # Pessimistic scenario
        pessimistic_data = await self._get_scenario_data(
            variety, regional_context, ScenarioType.PESSIMISTIC
        )
        scenarios['pessimistic'] = await self._analyze_scenario(
            variety, pessimistic_data, ScenarioType.PESSIMISTIC, analysis_horizon_years
        )
        
        return scenarios
    
    async def _get_scenario_data(
        self,
        variety: EnhancedCropVariety,
        regional_context: Dict[str, Any],
        scenario_type: ScenarioType
    ) -> Dict[str, Any]:
        """Get data adjusted for specific scenario."""
        
        base_data = regional_context.copy()
        
        if scenario_type == ScenarioType.OPTIMISTIC:
            # Optimistic: higher yields, better prices, lower costs
            base_data['yield_multiplier'] = base_data.get('yield_multiplier', 1.0) * 1.15
            base_data['price_multiplier'] = base_data.get('price_multiplier', 1.0) * 1.1
            base_data['cost_multiplier'] = base_data.get('cost_multiplier', 1.0) * 0.95
            base_data['weather_risk_multiplier'] = 0.7
            base_data['market_volatility_multiplier'] = 0.8
            
        elif scenario_type == ScenarioType.PESSIMISTIC:
            # Pessimistic: lower yields, worse prices, higher costs
            base_data['yield_multiplier'] = base_data.get('yield_multiplier', 1.0) * 0.85
            base_data['price_multiplier'] = base_data.get('price_multiplier', 1.0) * 0.9
            base_data['cost_multiplier'] = base_data.get('cost_multiplier', 1.0) * 1.1
            base_data['weather_risk_multiplier'] = 1.3
            base_data['market_volatility_multiplier'] = 1.2
            
        else:  # BASE_CASE
            # Base case: no adjustments
            base_data['yield_multiplier'] = base_data.get('yield_multiplier', 1.0)
            base_data['price_multiplier'] = base_data.get('price_multiplier', 1.0)
            base_data['cost_multiplier'] = base_data.get('cost_multiplier', 1.0)
            base_data['weather_risk_multiplier'] = 1.0
            base_data['market_volatility_multiplier'] = 1.0
        
        return base_data
    
    async def _analyze_scenario(
        self,
        variety: EnhancedCropVariety,
        scenario_data: Dict[str, Any],
        scenario_type: ScenarioType,
        analysis_horizon_years: int
    ) -> ScenarioAnalysis:
        """Analyze a specific scenario."""
        
        # Get market data for scenario
        market_data = await self._get_market_data(variety, scenario_data)
        
        # Calculate cost factors
        cost_factors = await self._calculate_cost_factors(variety, scenario_data)
        
        # Calculate revenue factors
        revenue_factors = await self._calculate_revenue_factors(
            variety, scenario_data, market_data
        )
        
        # Calculate financial metrics
        npv = self._calculate_npv(cost_factors, revenue_factors)
        irr = self._calculate_irr(cost_factors, revenue_factors)
        payback_period = self._calculate_payback_period(cost_factors, revenue_factors)
        
        # Calculate expected profit
        expected_profit = revenue_factors.total_revenue_per_acre() - cost_factors.total_cost_per_acre()
        
        # Calculate probability of profit (simplified)
        probability_of_profit = self._calculate_probability_of_profit(
            expected_profit, scenario_type
        )
        
        # Calculate confidence interval (simplified)
        confidence_interval = self._calculate_confidence_interval(
            expected_profit, scenario_type
        )
        
        return ScenarioAnalysis(
            scenario_type=scenario_type,
            net_present_value=npv,
            internal_rate_of_return=irr,
            payback_period_years=payback_period,
            expected_profit_per_acre=expected_profit,
            probability_of_profit=probability_of_profit,
            confidence_interval_95=confidence_interval
        )
    
    async def _perform_monte_carlo_simulation(
        self,
        variety: EnhancedCropVariety,
        regional_context: Dict[str, Any],
        farmer_preferences: Optional[Dict[str, Any]],
        analysis_horizon_years: int,
        iterations: int = 10000
    ) -> MonteCarloResult:
        """Perform Monte Carlo simulation for uncertainty quantification."""
        
        logger.info(f"Running Monte Carlo simulation with {iterations} iterations")
        
        npv_results = []
        
        for i in range(iterations):
            # Generate random scenario data
            random_scenario = await self._generate_random_scenario(
                variety, regional_context, farmer_preferences
            )
            
            # Calculate NPV for this iteration
            market_data = await self._get_market_data(variety, random_scenario)
            cost_factors = await self._calculate_cost_factors(variety, random_scenario)
            revenue_factors = await self._calculate_revenue_factors(
                variety, random_scenario, market_data
            )
            
            npv = self._calculate_npv(cost_factors, revenue_factors)
            npv_results.append(npv)
        
        # Calculate statistics
        npv_array = np.array(npv_results)
        
        mean_npv = float(np.mean(npv_array))
        median_npv = float(np.median(npv_array))
        std_deviation_npv = float(np.std(npv_array))
        
        # Calculate probability of positive NPV
        positive_npv_count = np.sum(npv_array > 0)
        probability_positive_npv = float(positive_npv_count / iterations)
        
        # Calculate Value at Risk (95%)
        var_95 = float(np.percentile(npv_array, 5))  # 5th percentile
        
        # Calculate Expected Shortfall (Conditional VaR)
        var_threshold = np.percentile(npv_array, 5)
        shortfall_values = npv_array[npv_array <= var_threshold]
        expected_shortfall = float(np.mean(shortfall_values)) if len(shortfall_values) > 0 else var_95
        
        # Calculate confidence intervals
        confidence_intervals = {
            '90%': (float(np.percentile(npv_array, 5)), float(np.percentile(npv_array, 95))),
            '95%': (float(np.percentile(npv_array, 2.5)), float(np.percentile(npv_array, 97.5))),
            '99%': (float(np.percentile(npv_array, 0.5)), float(np.percentile(npv_array, 99.5)))
        }
        
        return MonteCarloResult(
            mean_npv=mean_npv,
            median_npv=median_npv,
            std_deviation_npv=std_deviation_npv,
            probability_of_positive_npv=probability_positive_npv,
            value_at_risk_95=var_95,
            expected_shortfall=expected_shortfall,
            simulation_iterations=iterations,
            confidence_intervals=confidence_intervals
        )
    
    async def _generate_random_scenario(
        self,
        variety: EnhancedCropVariety,
        regional_context: Dict[str, Any],
        farmer_preferences: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate random scenario data for Monte Carlo simulation."""
        
        random_scenario = regional_context.copy()
        
        # Random yield multiplier (normal distribution around 1.0, std dev 0.15)
        random_scenario['yield_multiplier'] = max(0.5, np.random.normal(1.0, 0.15))
        
        # Random price multiplier (normal distribution around 1.0, std dev 0.1)
        random_scenario['price_multiplier'] = max(0.7, np.random.normal(1.0, 0.1))
        
        # Random cost multiplier (normal distribution around 1.0, std dev 0.08)
        random_scenario['cost_multiplier'] = max(0.8, np.random.normal(1.0, 0.08))
        
        # Random weather risk (uniform distribution)
        random_scenario['weather_risk_multiplier'] = np.random.uniform(0.7, 1.3)
        
        # Random market volatility (uniform distribution)
        random_scenario['market_volatility_multiplier'] = np.random.uniform(0.8, 1.2)
        
        return random_scenario
    
    async def _calculate_comprehensive_risk_assessment(
        self,
        variety: EnhancedCropVariety,
        regional_context: Dict[str, Any],
        farmer_preferences: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate comprehensive risk assessment."""
        
        # Weather risk assessment
        weather_risk = await self._calculate_weather_risk(variety, regional_context)
        
        # Market volatility risk
        market_volatility_risk = await self._calculate_market_volatility_risk(
            variety, regional_context
        )
        
        # Yield volatility risk
        yield_volatility_risk = await self._calculate_yield_volatility_risk(
            variety, regional_context
        )
        
        # Overall risk score (weighted average)
        overall_risk = (
            weather_risk * 0.4 +
            market_volatility_risk * 0.3 +
            yield_volatility_risk * 0.3
        )
        
        return {
            'weather_risk': weather_risk,
            'market_volatility': market_volatility_risk,
            'yield_volatility': yield_volatility_risk,
            'overall_risk': overall_risk
        }
    
    async def _calculate_weather_risk(
        self,
        variety: EnhancedCropVariety,
        regional_context: Dict[str, Any]
    ) -> float:
        """Calculate weather-related risk score."""
        
        # Base weather risk from regional context
        base_weather_risk = regional_context.get('weather_risk_score', 0.5)
        
        # Adjust based on variety characteristics
        variety_risk_adjustment = 0.0
        
        # Drought tolerance reduces weather risk
        if variety.stress_tolerances:
            if "drought_tolerance" in variety.stress_tolerances:
                variety_risk_adjustment -= 0.1  # Drought tolerance reduces risk
        
        # Heat tolerance reduces weather risk
        if variety.stress_tolerances:
            if "heat_tolerance" in variety.stress_tolerances:
                variety_risk_adjustment -= 0.05  # Heat tolerance reduces risk
        
        # Yield stability affects weather risk
        if variety.yield_stability_rating:
            stability_adjustment = (variety.yield_stability_rating - 5) * 0.02
            variety_risk_adjustment -= stability_adjustment
        
        final_weather_risk = max(0.0, min(1.0, base_weather_risk + variety_risk_adjustment))
        
        return final_weather_risk
    
    async def _calculate_market_volatility_risk(
        self,
        variety: EnhancedCropVariety,
        regional_context: Dict[str, Any]
    ) -> float:
        """Calculate market volatility risk score."""
        
        # Get market volatility from regional context
        market_volatility = regional_context.get('price_volatility', 0.15)
        
        # Adjust based on variety market characteristics
        variety_adjustment = 0.0
        
        # Market acceptance affects volatility risk
        if variety.market_acceptance_score:
            if variety.market_acceptance_score > 4.0:
                variety_adjustment -= 0.05  # High acceptance = lower risk
            elif variety.market_acceptance_score < 2.0:
                variety_adjustment += 0.05  # Low acceptance = higher risk
        
        # Premium potential affects volatility (simplified check)
        if variety.market_acceptance_score and variety.market_acceptance_score > 4.0:
            variety_adjustment += 0.03  # High market acceptance can indicate premium markets
        
        final_volatility_risk = max(0.0, min(1.0, market_volatility + variety_adjustment))
        
        return final_volatility_risk
    
    async def _calculate_yield_volatility_risk(
        self,
        variety: EnhancedCropVariety,
        regional_context: Dict[str, Any]
    ) -> float:
        """Calculate yield volatility risk score."""
        
        # Base yield volatility from variety characteristics
        base_volatility = 0.5  # Default moderate volatility
        
        # Adjust based on yield stability rating
        if variety.yield_stability_rating:
            # Convert stability rating (1-10) to volatility (0-1)
            # Higher stability = lower volatility
            base_volatility = 1.0 - (variety.yield_stability_rating / 10.0)
        
        # Adjust based on disease resistance
        disease_adjustment = 0.0
        if variety.disease_resistances:
            resistance_count = len(variety.disease_resistances)
            if resistance_count > 5:
                disease_adjustment -= 0.1  # High resistance = lower volatility
            elif resistance_count < 2:
                disease_adjustment += 0.1  # Low resistance = higher volatility
        
        # Adjust based on regional conditions
        regional_adjustment = regional_context.get('yield_volatility_adjustment', 0.0)
        
        final_yield_volatility = max(0.0, min(1.0, 
            base_volatility + disease_adjustment + regional_adjustment
        ))
        
        return final_yield_volatility
    
    async def _generate_investment_recommendation(
        self,
        base_analysis: EconomicAnalysisResult,
        scenario_results: Dict[str, ScenarioAnalysis],
        monte_carlo_results: MonteCarloResult,
        risk_assessments: Dict[str, float]
    ) -> InvestmentRecommendation:
        """Generate investment recommendation based on comprehensive analysis."""
        
        # Calculate recommendation score
        recommendation_score = self._calculate_recommendation_score(
            base_analysis, scenario_results, monte_carlo_results, risk_assessments
        )
        
        # Determine recommendation type
        if recommendation_score >= 0.8:
            recommendation_type = "strong_buy"
        elif recommendation_score >= 0.6:
            recommendation_type = "buy"
        elif recommendation_score >= 0.4:
            recommendation_type = "hold"
        elif recommendation_score >= 0.2:
            recommendation_type = "sell"
        else:
            recommendation_type = "strong_sell"
        
        # Determine risk level
        overall_risk = risk_assessments['overall_risk']
        if overall_risk <= 0.3:
            risk_level = RiskLevel.LOW
        elif overall_risk <= 0.5:
            risk_level = RiskLevel.MEDIUM
        elif overall_risk <= 0.7:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.VERY_HIGH
        
        # Calculate expected return
        expected_return = base_analysis.internal_rate_of_return
        
        # Generate key factors
        key_factors = self._generate_key_factors(base_analysis, scenario_results, monte_carlo_results)
        
        # Generate risk factors
        risk_factors = self._generate_risk_factors(risk_assessments, scenario_results)
        
        # Generate mitigation strategies
        mitigation_strategies = self._generate_mitigation_strategies(
            risk_factors, risk_level
        )
        
        return InvestmentRecommendation(
            recommendation_type=recommendation_type,
            confidence_score=recommendation_score,
            risk_level=risk_level,
            expected_return_percent=expected_return,
            payback_period_years=base_analysis.payback_period_years,
            key_factors=key_factors,
            risk_factors=risk_factors,
            mitigation_strategies=mitigation_strategies
        )
    
    def _calculate_recommendation_score(
        self,
        base_analysis: EconomicAnalysisResult,
        scenario_results: Dict[str, ScenarioAnalysis],
        monte_carlo_results: MonteCarloResult,
        risk_assessments: Dict[str, float]
    ) -> float:
        """Calculate overall recommendation score (0-1)."""
        
        # Economic viability score (40% weight)
        economic_score = base_analysis.economic_viability_score
        
        # Scenario analysis score (25% weight)
        scenario_score = (
            scenario_results['optimistic'].net_present_value * 0.3 +
            scenario_results['base_case'].net_present_value * 0.5 +
            scenario_results['pessimistic'].net_present_value * 0.2
        )
        # Normalize scenario score
        scenario_score = max(0.0, min(1.0, (scenario_score + 1000) / 2000))
        
        # Monte Carlo score (20% weight)
        monte_carlo_score = monte_carlo_results.probability_of_positive_npv
        
        # Risk-adjusted score (15% weight)
        risk_score = 1.0 - risk_assessments['overall_risk']
        
        # Weighted combination
        recommendation_score = (
            economic_score * 0.4 +
            scenario_score * 0.25 +
            monte_carlo_score * 0.2 +
            risk_score * 0.15
        )
        
        return max(0.0, min(1.0, recommendation_score))
    
    def _generate_key_factors(
        self,
        base_analysis: EconomicAnalysisResult,
        scenario_results: Dict[str, ScenarioAnalysis],
        monte_carlo_results: MonteCarloResult
    ) -> List[str]:
        """Generate key positive factors for the investment."""
        
        factors = []
        
        # Economic factors
        if base_analysis.internal_rate_of_return > 15:
            factors.append(f"Strong IRR of {base_analysis.internal_rate_of_return:.1f}%")
        
        if base_analysis.payback_period_years < 3:
            factors.append(f"Quick payback period of {base_analysis.payback_period_years:.1f} years")
        
        if base_analysis.profit_margin_percent > 20:
            factors.append(f"High profit margin of {base_analysis.profit_margin_percent:.1f}%")
        
        # Scenario factors
        if scenario_results['optimistic'].net_present_value > scenario_results['base_case'].net_present_value * 1.5:
            factors.append("Significant upside potential in optimistic scenario")
        
        # Monte Carlo factors
        if monte_carlo_results.probability_of_positive_npv > 0.8:
            factors.append(f"High probability ({monte_carlo_results.probability_of_positive_npv:.1%}) of positive returns")
        
        if monte_carlo_results.mean_npv > 500:
            factors.append(f"Strong expected NPV of ${monte_carlo_results.mean_npv:.0f}")
        
        return factors
    
    def _generate_risk_factors(
        self,
        risk_assessments: Dict[str, float],
        scenario_results: Dict[str, ScenarioAnalysis]
    ) -> List[str]:
        """Generate risk factors for the investment."""
        
        risk_factors = []
        
        # Weather risks
        if risk_assessments['weather_risk'] > 0.6:
            risk_factors.append("High weather-related yield variability")
        
        # Market risks
        if risk_assessments['market_volatility'] > 0.6:
            risk_factors.append("High market price volatility")
        
        # Yield risks
        if risk_assessments['yield_volatility'] > 0.6:
            risk_factors.append("High yield variability")
        
        # Scenario risks
        if scenario_results['pessimistic'].net_present_value < 0:
            risk_factors.append("Negative returns in pessimistic scenario")
        
        if scenario_results['pessimistic'].payback_period_years > 5:
            risk_factors.append("Long payback period in adverse conditions")
        
        return risk_factors
    
    def _generate_mitigation_strategies(
        self,
        risk_factors: List[str],
        risk_level: RiskLevel
    ) -> List[str]:
        """Generate mitigation strategies for identified risks."""
        
        strategies = []
        
        # General strategies based on risk level
        if risk_level in [RiskLevel.HIGH, RiskLevel.VERY_HIGH]:
            strategies.append("Consider crop insurance to mitigate yield risks")
            strategies.append("Diversify crop portfolio to reduce concentration risk")
            strategies.append("Implement hedging strategies for price risk management")
        
        # Specific strategies based on risk factors
        for risk_factor in risk_factors:
            if "weather" in risk_factor.lower():
                strategies.append("Implement irrigation systems for drought mitigation")
                strategies.append("Use weather derivatives for weather risk hedging")
            
            if "market" in risk_factor.lower():
                strategies.append("Enter forward contracts to lock in prices")
                strategies.append("Consider commodity futures for price protection")
            
            if "yield" in risk_factor.lower():
                strategies.append("Implement precision agriculture for yield optimization")
                strategies.append("Use multiple varieties to reduce yield concentration")
        
        return strategies
    
    async def _calculate_advanced_financial_metrics(
        self,
        variety: EnhancedCropVariety,
        regional_context: Dict[str, Any],
        farmer_preferences: Optional[Dict[str, Any]],
        analysis_horizon_years: int
    ) -> Dict[str, float]:
        """Calculate advanced financial metrics."""
        
        # Get base data
        market_data = await self._get_market_data(variety, regional_context)
        cost_factors = await self._calculate_cost_factors(variety, regional_context)
        revenue_factors = await self._calculate_revenue_factors(
            variety, regional_context, market_data
        )
        
        # Calculate NPV
        npv = self._calculate_npv(cost_factors, revenue_factors)
        
        # Calculate IRR
        irr = self._calculate_irr(cost_factors, revenue_factors)
        
        # Calculate Modified IRR (MIRR)
        mirr = self._calculate_modified_irr(cost_factors, revenue_factors)
        
        # Calculate Profitability Index (PI)
        pi = self._calculate_profitability_index(cost_factors, revenue_factors)
        
        # Calculate Discounted Payback Period
        discounted_payback = self._calculate_discounted_payback_period(
            cost_factors, revenue_factors
        )
        
        return {
            'npv': npv,
            'irr': irr,
            'mirr': mirr,
            'pi': pi,
            'discounted_payback': discounted_payback
        }
    
    def _calculate_modified_irr(
        self,
        cost_factors: CostFactors,
        revenue_factors: RevenueFactors
    ) -> float:
        """Calculate Modified Internal Rate of Return (MIRR)."""
        
        # Simplified MIRR calculation
        # In production, would use more sophisticated method
        annual_cash_flow = revenue_factors.total_revenue_per_acre() - cost_factors.total_cost_per_acre()
        
        if annual_cash_flow <= 0:
            return 0.0
        
        # Use reinvestment rate of 8% and finance rate of 6%
        reinvestment_rate = 0.08
        finance_rate = 0.06
        
        initial_investment = cost_factors.total_cost_per_acre()
        
        # Future value of positive cash flows
        future_value = annual_cash_flow * ((1 + reinvestment_rate) ** self.analysis_horizon_years - 1) / reinvestment_rate
        
        # MIRR calculation
        mirr = (future_value / initial_investment) ** (1 / self.analysis_horizon_years) - 1
        
        return min(mirr * 100, 50.0)  # Cap at 50% for realism
    
    def _calculate_profitability_index(
        self,
        cost_factors: CostFactors,
        revenue_factors: RevenueFactors
    ) -> float:
        """Calculate Profitability Index (PI)."""
        
        npv = self._calculate_npv(cost_factors, revenue_factors)
        initial_investment = cost_factors.total_cost_per_acre()
        
        if initial_investment <= 0:
            return 0.0
        
        pi = (npv + initial_investment) / initial_investment
        
        return max(0.0, pi)
    
    def _calculate_discounted_payback_period(
        self,
        cost_factors: CostFactors,
        revenue_factors: RevenueFactors
    ) -> float:
        """Calculate discounted payback period."""
        
        annual_cash_flow = revenue_factors.total_revenue_per_acre() - cost_factors.total_cost_per_acre()
        initial_investment = cost_factors.total_cost_per_acre()
        
        if annual_cash_flow <= 0:
            return float('inf')
        
        cumulative_discounted_cash_flow = 0.0
        year = 0
        
        while cumulative_discounted_cash_flow < initial_investment and year < self.analysis_horizon_years:
            year += 1
            discounted_cash_flow = annual_cash_flow / ((1 + self.discount_rate) ** year)
            cumulative_discounted_cash_flow += discounted_cash_flow
        
        if cumulative_discounted_cash_flow < initial_investment:
            return float('inf')
        
        # Interpolate for partial year
        if year > 1:
            prev_cumulative = sum(
                annual_cash_flow / ((1 + self.discount_rate) ** (y + 1))
                for y in range(year - 1)
            )
            remaining_investment = initial_investment - prev_cumulative
            final_discounted_cash_flow = annual_cash_flow / ((1 + self.discount_rate) ** year)
            partial_year = remaining_investment / final_discounted_cash_flow
            return year - 1 + partial_year
        
        return float(year)
    
    async def _generate_annual_cash_flows(
        self,
        variety: EnhancedCropVariety,
        regional_context: Dict[str, Any],
        farmer_preferences: Optional[Dict[str, Any]],
        analysis_horizon_years: int
    ) -> List[float]:
        """Generate annual cash flows for multi-year analysis."""
        
        # Get base economic data
        market_data = await self._get_market_data(variety, regional_context)
        cost_factors = await self._calculate_cost_factors(variety, regional_context)
        revenue_factors = await self._calculate_revenue_factors(
            variety, regional_context, market_data
        )
        
        annual_cash_flow = revenue_factors.total_revenue_per_acre() - cost_factors.total_cost_per_acre()
        
        # Generate cash flows for each year
        cash_flows = []
        for year in range(1, analysis_horizon_years + 1):
            # Apply small random variation to simulate year-to-year variability
            variation = np.random.normal(1.0, 0.05)  # 5% standard deviation
            year_cash_flow = annual_cash_flow * variation
            cash_flows.append(year_cash_flow)
        
        return cash_flows
    
    def _calculate_cumulative_cash_flows(self, annual_cash_flows: List[float]) -> List[float]:
        """Calculate cumulative cash flows."""
        
        cumulative = []
        running_total = 0.0
        
        for cash_flow in annual_cash_flows:
            running_total += cash_flow
            cumulative.append(running_total)
        
        return cumulative
    
    def _calculate_probability_of_profit(self, expected_profit: float, scenario_type: ScenarioType) -> float:
        """Calculate probability of profit for a scenario."""
        
        if scenario_type == ScenarioType.OPTIMISTIC:
            return min(0.95, max(0.7, 0.8 + (expected_profit / 1000)))
        elif scenario_type == ScenarioType.PESSIMISTIC:
            return max(0.05, min(0.3, 0.2 + (expected_profit / 1000)))
        else:  # BASE_CASE
            return max(0.1, min(0.9, 0.5 + (expected_profit / 2000)))
    
    def _calculate_confidence_interval(self, expected_profit: float, scenario_type: ScenarioType) -> Tuple[float, float]:
        """Calculate 95% confidence interval for expected profit."""
        
        # Simplified confidence interval calculation
        if scenario_type == ScenarioType.OPTIMISTIC:
            std_dev = abs(expected_profit) * 0.15  # 15% standard deviation
        elif scenario_type == ScenarioType.PESSIMISTIC:
            std_dev = abs(expected_profit) * 0.25  # 25% standard deviation
        else:  # BASE_CASE
            std_dev = abs(expected_profit) * 0.20  # 20% standard deviation
        
        # 95% confidence interval (±1.96 standard deviations)
        margin_of_error = 1.96 * std_dev
        
        return (
            expected_profit - margin_of_error,
            expected_profit + margin_of_error
        )
    
    def _get_sophisticated_analysis_assumptions(
        self,
        variety: EnhancedCropVariety,
        regional_context: Dict[str, Any],
        analysis_horizon_years: int
    ) -> Dict[str, Any]:
        """Get assumptions used in sophisticated analysis."""
        
        base_assumptions = self._get_analysis_assumptions(variety, regional_context)
        
        sophisticated_assumptions = {
            **base_assumptions,
            'analysis_horizon_years': analysis_horizon_years,
            'monte_carlo_iterations': 10000,
            'scenario_probabilities': {
                'optimistic': 0.2,
                'base_case': 0.6,
                'pessimistic': 0.2
            },
            'risk_free_rate': self.risk_free_rate,
            'reinvestment_rate': 0.08,
            'finance_rate': 0.06,
            'confidence_level': 0.95,
            'value_at_risk_percentile': 95,
            'yield_volatility_assumption': 0.15,
            'price_volatility_assumption': 0.20,
            'cost_volatility_assumption': 0.10
        }
        
        return sophisticated_assumptions
    
    def _get_data_sources_used(self, regional_context: Dict[str, Any]) -> List[str]:
        """Get list of data sources used in analysis."""
        
        sources = ['variety_database', 'regional_averages']
        
        if self.market_price_service:
            sources.append('market_price_service')
        else:
            sources.append('fallback_pricing')
        
        if 'weather_data' in regional_context:
            sources.append('weather_service')
        
        if 'soil_data' in regional_context:
            sources.append('soil_service')
        
        sources.extend([
            'government_programs_database',
            'insurance_data',
            'monte_carlo_simulation',
            'scenario_analysis'
        ])
        
        return sources