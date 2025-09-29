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