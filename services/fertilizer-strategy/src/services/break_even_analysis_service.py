"""
Advanced Break-Even Analysis Service for Fertilizer Strategy Optimization.

This service provides comprehensive break-even analysis including:
- Stochastic modeling with Monte Carlo simulation
- Scenario analysis with multiple price/yield combinations
- Sensitivity analysis for key variables
- Risk assessment and probability distributions
- Integration with cost databases and yield models
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from uuid import uuid4
from datetime import datetime, date
from dataclasses import dataclass
from enum import Enum
import statistics
from scipy import stats
from scipy.optimize import minimize_scalar

from ..models.roi_models import (
    ROIOptimizationRequest, 
    FieldData, 
    FertilizerProduct,
    OptimizationResult
)
# PriceData import removed - not needed for break-even analysis
from .roi_optimizer import FertilizerROIOptimizer
from .price_tracking_service import FertilizerPriceTrackingService

logger = logging.getLogger(__name__)


class ScenarioType(str, Enum):
    """Types of break-even scenarios."""
    OPTIMISTIC = "optimistic"
    REALISTIC = "realistic"
    PESSIMISTIC = "pessimistic"
    STRESS_TEST = "stress_test"


class RiskLevel(str, Enum):
    """Risk levels for break-even analysis."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class CostStructure:
    """Detailed cost structure for break-even analysis."""
    fixed_costs: float
    variable_costs: float
    fertilizer_costs: float
    application_costs: float
    opportunity_costs: float
    total_costs: float


@dataclass
class YieldResponseCurve:
    """Yield response curve parameters."""
    base_yield: float
    max_yield: float
    response_rate: float
    plateau_yield: float
    diminishing_returns_factor: float


@dataclass
class PriceDistribution:
    """Price distribution parameters for stochastic modeling."""
    mean_price: float
    std_deviation: float
    min_price: float
    max_price: float
    distribution_type: str  # normal, lognormal, triangular


@dataclass
class BreakEvenScenario:
    """Individual break-even scenario."""
    scenario_id: str
    scenario_type: ScenarioType
    crop_price: float
    fertilizer_price: float
    expected_yield: float
    break_even_yield: float
    break_even_price: float
    break_even_cost: float
    probability: float
    risk_level: RiskLevel
    safety_margin: float


@dataclass
class SensitivityAnalysis:
    """Sensitivity analysis results."""
    variable_name: str
    base_value: float
    sensitivity_range: Tuple[float, float]
    break_even_impact: Dict[str, float]
    elasticity: float


@dataclass
class MonteCarloResult:
    """Monte Carlo simulation results."""
    simulation_id: str
    iterations: int
    break_even_probabilities: Dict[str, float]
    confidence_intervals: Dict[str, Tuple[float, float]]
    risk_metrics: Dict[str, float]
    probability_distributions: Dict[str, List[float]]


class BreakEvenAnalysisService:
    """
    Advanced break-even analysis service with comprehensive financial modeling.
    
    Features:
    - Stochastic modeling with Monte Carlo simulation
    - Scenario analysis with multiple price/yield combinations
    - Sensitivity analysis for key variables
    - Risk assessment and probability distributions
    - Integration with cost databases and yield models
    """
    
    def __init__(self):
        self.roi_optimizer = FertilizerROIOptimizer()
        self.price_service = FertilizerPriceTrackingService()
        self.logger = logging.getLogger(__name__)
        
        # Default parameters for stochastic modeling
        self.default_iterations = 10000
        self.confidence_levels = [0.05, 0.25, 0.5, 0.75, 0.95]
        
    async def perform_comprehensive_break_even_analysis(
        self,
        request: ROIOptimizationRequest,
        include_stochastic: bool = True,
        include_scenarios: bool = True,
        include_sensitivity: bool = True,
        monte_carlo_iterations: int = 10000
    ) -> Dict[str, Any]:
        """
        Perform comprehensive break-even analysis with all advanced features.
        
        Args:
            request: ROI optimization request with field and product data
            include_stochastic: Include Monte Carlo simulation
            include_scenarios: Include scenario analysis
            include_sensitivity: Include sensitivity analysis
            monte_carlo_iterations: Number of Monte Carlo iterations
            
        Returns:
            Comprehensive break-even analysis results
        """
        try:
            self.logger.info("Starting comprehensive break-even analysis")
            
            # Get base optimization results
            base_result = await self.roi_optimizer.optimize_fertilizer_roi(request)
            
            # Calculate detailed cost structure
            cost_structure = await self._calculate_detailed_cost_structure(request, base_result)
            
            # Perform basic break-even calculations
            basic_analysis = await self._calculate_basic_break_even(request, cost_structure)
            
            results = {
                "analysis_id": str(uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "basic_analysis": basic_analysis,
                "cost_structure": cost_structure,
                "field_summary": await self._summarize_fields(request.fields),
                "product_summary": await self._summarize_products(request.products)
            }
            
            # Add stochastic analysis if requested
            if include_stochastic:
                self.logger.info("Performing Monte Carlo simulation")
                stochastic_results = await self._perform_monte_carlo_simulation(
                    request, cost_structure, monte_carlo_iterations
                )
                results["stochastic_analysis"] = stochastic_results
            
            # Add scenario analysis if requested
            if include_scenarios:
                self.logger.info("Performing scenario analysis")
                scenario_results = await self._perform_scenario_analysis(request, cost_structure)
                results["scenario_analysis"] = scenario_results
            
            # Add sensitivity analysis if requested
            if include_sensitivity:
                self.logger.info("Performing sensitivity analysis")
                sensitivity_results = await self._perform_sensitivity_analysis(request, cost_structure)
                results["sensitivity_analysis"] = sensitivity_results
            
            # Calculate risk assessment
            risk_assessment = await self._assess_break_even_risk(results)
            results["risk_assessment"] = risk_assessment
            
            # Generate recommendations
            recommendations = await self._generate_break_even_recommendations(results)
            results["recommendations"] = recommendations
            
            self.logger.info("Comprehensive break-even analysis completed")
            return results
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive break-even analysis: {e}")
            raise
    
    async def _calculate_detailed_cost_structure(
        self, 
        request: ROIOptimizationRequest, 
        optimization_result: OptimizationResult
    ) -> CostStructure:
        """Calculate detailed cost structure for break-even analysis."""
        
        total_acres = sum(field.acres for field in request.fields)
        
        # Fixed costs (per acre)
        fixed_costs_per_acre = 150.0  # Base fixed costs
        fixed_costs = fixed_costs_per_acre * total_acres
        
        # Variable costs (per acre)
        variable_costs_per_acre = 200.0  # Base variable costs
        variable_costs = variable_costs_per_acre * total_acres
        
        # Fertilizer costs (from optimization)
        fertilizer_costs = optimization_result.total_fertilizer_cost
        
        # Application costs (labor, equipment, fuel)
        application_costs_per_acre = 25.0
        application_costs = application_costs_per_acre * total_acres
        
        # Opportunity costs (alternative crop returns)
        opportunity_costs_per_acre = 100.0
        opportunity_costs = opportunity_costs_per_acre * total_acres
        
        total_costs = (fixed_costs + variable_costs + fertilizer_costs + 
                      application_costs + opportunity_costs)
        
        return CostStructure(
            fixed_costs=fixed_costs,
            variable_costs=variable_costs,
            fertilizer_costs=fertilizer_costs,
            application_costs=application_costs,
            opportunity_costs=opportunity_costs,
            total_costs=total_costs
        )
    
    async def _calculate_basic_break_even(
        self, 
        request: ROIOptimizationRequest, 
        cost_structure: CostStructure
    ) -> Dict[str, Any]:
        """Calculate basic break-even metrics."""
        
        total_acres = sum(field.acres for field in request.fields)
        crop_price = request.fields[0].crop_price if request.fields else 0
        total_expected_yield = sum(field.target_yield * field.acres for field in request.fields)
        
        # Break-even yield per acre
        break_even_yield_per_acre = cost_structure.total_costs / (total_acres * crop_price) if crop_price > 0 else 0
        
        # Break-even price per unit
        break_even_price_per_unit = cost_structure.total_costs / total_expected_yield if total_expected_yield > 0 else 0
        
        # Break-even fertilizer cost per acre
        break_even_fertilizer_cost = cost_structure.total_costs / total_acres if total_acres > 0 else 0
        
        # Safety margin
        total_revenue = total_expected_yield * crop_price
        safety_margin = ((total_revenue - cost_structure.total_costs) / cost_structure.total_costs * 100) if cost_structure.total_costs > 0 else 0
        
        # Probability of profitability (simplified)
        probability_of_profitability = min(0.95, max(0.05, 0.5 + (safety_margin / 100) * 0.3))
        
        return {
            "break_even_yield_per_acre": break_even_yield_per_acre,
            "break_even_price_per_unit": break_even_price_per_unit,
            "break_even_fertilizer_cost_per_acre": break_even_fertilizer_cost,
            "safety_margin_percentage": safety_margin,
            "probability_of_profitability": probability_of_profitability,
            "total_costs": cost_structure.total_costs,
            "total_revenue": total_revenue,
            "net_profit": total_revenue - cost_structure.total_costs
        }
    
    async def _perform_monte_carlo_simulation(
        self,
        request: ROIOptimizationRequest,
        cost_structure: CostStructure,
        iterations: int
    ) -> MonteCarloResult:
        """Perform Monte Carlo simulation for break-even analysis."""
        
        self.logger.info(f"Running Monte Carlo simulation with {iterations} iterations")
        
        # Get price distributions
        crop_price_dist = await self._get_crop_price_distribution(request)
        fertilizer_price_dist = await self._get_fertilizer_price_distribution(request)
        yield_dist = await self._get_yield_distribution(request)
        
        # Initialize results storage
        break_even_yields = []
        break_even_prices = []
        break_even_costs = []
        profits = []
        safety_margins = []
        
        total_acres = sum(field.acres for field in request.fields)
        
        # Run Monte Carlo simulation
        for i in range(iterations):
            # Sample from distributions
            crop_price = self._sample_from_distribution(crop_price_dist)
            fertilizer_price_multiplier = self._sample_from_distribution(fertilizer_price_dist)
            yield_multiplier = self._sample_from_distribution(yield_dist)
            
            # Adjust costs based on fertilizer price
            adjusted_fertilizer_cost = cost_structure.fertilizer_costs * fertilizer_price_multiplier
            adjusted_total_cost = (cost_structure.fixed_costs + cost_structure.variable_costs + 
                                 adjusted_fertilizer_cost + cost_structure.application_costs + 
                                 cost_structure.opportunity_costs)
            
            # Calculate break-even metrics
            break_even_yield = adjusted_total_cost / (total_acres * crop_price) if crop_price > 0 else 0
            total_yield = sum(field.target_yield * field.acres * yield_multiplier for field in request.fields)
            break_even_price = adjusted_total_cost / total_yield if total_yield > 0 else 0
            break_even_cost = adjusted_total_cost / total_acres if total_acres > 0 else 0
            
            # Calculate profit and safety margin
            total_revenue = total_yield * crop_price
            profit = total_revenue - adjusted_total_cost
            safety_margin = (profit / adjusted_total_cost * 100) if adjusted_total_cost > 0 else 0
            
            # Store results
            break_even_yields.append(break_even_yield)
            break_even_prices.append(break_even_price)
            break_even_costs.append(break_even_cost)
            profits.append(profit)
            safety_margins.append(safety_margin)
        
        # Calculate probabilities and confidence intervals
        break_even_probabilities = {
            "profitable": len([p for p in profits if p > 0]) / iterations,
            "break_even_yield_achievable": len([y for y in break_even_yields if y <= max(field.target_yield for field in request.fields)]) / iterations,
            "safety_margin_adequate": len([s for s in safety_margins if s > 20]) / iterations
        }
        
        confidence_intervals = {
            "break_even_yield": (np.percentile(break_even_yields, 5), np.percentile(break_even_yields, 95)),
            "break_even_price": (np.percentile(break_even_prices, 5), np.percentile(break_even_prices, 95)),
            "profit": (np.percentile(profits, 5), np.percentile(profits, 95)),
            "safety_margin": (np.percentile(safety_margins, 5), np.percentile(safety_margins, 95))
        }
        
        risk_metrics = {
            "value_at_risk_5pct": np.percentile(profits, 5),
            "expected_shortfall": np.mean([p for p in profits if p <= np.percentile(profits, 5)]),
            "volatility": np.std(profits),
            "sharpe_ratio": np.mean(profits) / np.std(profits) if np.std(profits) > 0 else 0
        }
        
        return MonteCarloResult(
            simulation_id=str(uuid4()),
            iterations=iterations,
            break_even_probabilities=break_even_probabilities,
            confidence_intervals=confidence_intervals,
            risk_metrics=risk_metrics,
            probability_distributions={
                "break_even_yields": break_even_yields,
                "break_even_prices": break_even_prices,
                "profits": profits,
                "safety_margins": safety_margins
            }
        )
    
    async def _perform_scenario_analysis(
        self,
        request: ROIOptimizationRequest,
        cost_structure: CostStructure
    ) -> List[BreakEvenScenario]:
        """Perform scenario analysis with different price/yield combinations."""
        
        scenarios = []
        total_acres = sum(field.acres for field in request.fields)
        base_crop_price = request.fields[0].crop_price if request.fields else 0
        base_yield = sum(field.target_yield * field.acres for field in request.fields)
        
        # Define scenario parameters
        scenario_params = {
            ScenarioType.OPTIMISTIC: {"price_mult": 1.2, "yield_mult": 1.15, "cost_mult": 0.9, "probability": 0.2},
            ScenarioType.REALISTIC: {"price_mult": 1.0, "yield_mult": 1.0, "cost_mult": 1.0, "probability": 0.5},
            ScenarioType.PESSIMISTIC: {"price_mult": 0.8, "yield_mult": 0.85, "cost_mult": 1.1, "probability": 0.2},
            ScenarioType.STRESS_TEST: {"price_mult": 0.6, "yield_mult": 0.7, "cost_mult": 1.3, "probability": 0.1}
        }
        
        for scenario_type, params in scenario_params.items():
            # Adjust parameters
            crop_price = base_crop_price * params["price_mult"]
            expected_yield = base_yield * params["yield_mult"]
            adjusted_cost = cost_structure.total_costs * params["cost_mult"]
            
            # Calculate break-even metrics
            break_even_yield = adjusted_cost / (total_acres * crop_price) if crop_price > 0 else 0
            break_even_price = adjusted_cost / expected_yield if expected_yield > 0 else 0
            break_even_cost = adjusted_cost / total_acres if total_acres > 0 else 0
            
            # Calculate safety margin
            total_revenue = expected_yield * crop_price
            safety_margin = ((total_revenue - adjusted_cost) / adjusted_cost * 100) if adjusted_cost > 0 else 0
            
            # Determine risk level
            risk_level = self._determine_risk_level(safety_margin, break_even_yield, expected_yield / total_acres)
            
            scenario = BreakEvenScenario(
                scenario_id=str(uuid4()),
                scenario_type=scenario_type,
                crop_price=crop_price,
                fertilizer_price=0,  # Would need fertilizer price data
                expected_yield=expected_yield,
                break_even_yield=break_even_yield,
                break_even_price=break_even_price,
                break_even_cost=break_even_cost,
                probability=params["probability"],
                risk_level=risk_level,
                safety_margin=safety_margin
            )
            scenarios.append(scenario)
        
        return scenarios
    
    async def _perform_sensitivity_analysis(
        self,
        request: ROIOptimizationRequest,
        cost_structure: CostStructure
    ) -> List[SensitivityAnalysis]:
        """Perform sensitivity analysis for key variables."""
        
        sensitivity_variables = [
            ("crop_price", request.fields[0].crop_price if request.fields else 0, 0.1),
            ("fertilizer_cost", cost_structure.fertilizer_costs, 0.1),
            ("yield", sum(field.target_yield * field.acres for field in request.fields), 0.1),
            ("fixed_costs", cost_structure.fixed_costs, 0.1),
            ("variable_costs", cost_structure.variable_costs, 0.1)
        ]
        
        sensitivity_results = []
        base_break_even = await self._calculate_basic_break_even(request, cost_structure)
        
        for var_name, base_value, variation in sensitivity_variables:
            # Calculate sensitivity range
            min_value = base_value * (1 - variation)
            max_value = base_value * (1 + variation)
            
            # Calculate break-even impact
            break_even_impact = {}
            
            for multiplier in [0.9, 1.0, 1.1]:
                adjusted_value = base_value * multiplier
                
                # Create adjusted request/cost structure
                if var_name == "crop_price":
                    adjusted_request = self._adjust_crop_price(request, adjusted_value)
                elif var_name == "fertilizer_cost":
                    adjusted_cost_structure = self._adjust_fertilizer_cost(cost_structure, adjusted_value)
                else:
                    adjusted_request = request
                    adjusted_cost_structure = cost_structure
                
                # Calculate break-even with adjusted value
                adjusted_analysis = await self._calculate_basic_break_even(adjusted_request, adjusted_cost_structure)
                
                break_even_impact[f"{multiplier}x"] = {
                    "break_even_yield": adjusted_analysis["break_even_yield_per_acre"],
                    "break_even_price": adjusted_analysis["break_even_price_per_unit"],
                    "safety_margin": adjusted_analysis["safety_margin_percentage"]
                }
            
            # Calculate elasticity
            elasticity = self._calculate_elasticity(base_value, base_break_even["break_even_yield_per_acre"], 
                                                 break_even_impact["1.1x"]["break_even_yield"])
            
            sensitivity_analysis = SensitivityAnalysis(
                variable_name=var_name,
                base_value=base_value,
                sensitivity_range=(min_value, max_value),
                break_even_impact=break_even_impact,
                elasticity=elasticity
            )
            sensitivity_results.append(sensitivity_analysis)
        
        return sensitivity_results
    
    async def _assess_break_even_risk(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall risk level for break-even analysis."""
        
        basic_analysis = analysis_results["basic_analysis"]
        safety_margin = basic_analysis["safety_margin_percentage"]
        probability_of_profitability = basic_analysis["probability_of_profitability"]
        
        # Risk factors
        risk_factors = []
        risk_score = 0
        
        if safety_margin < 10:
            risk_factors.append("Very low safety margin")
            risk_score += 3
        elif safety_margin < 20:
            risk_factors.append("Low safety margin")
            risk_score += 2
        elif safety_margin < 30:
            risk_factors.append("Moderate safety margin")
            risk_score += 1
        
        if probability_of_profitability < 0.6:
            risk_factors.append("Low probability of profitability")
            risk_score += 2
        elif probability_of_profitability < 0.8:
            risk_factors.append("Moderate probability of profitability")
            risk_score += 1
        
        # Check if stochastic analysis is available
        if "stochastic_analysis" in analysis_results:
            stochastic = analysis_results["stochastic_analysis"]
            if stochastic.break_even_probabilities["profitable"] < 0.7:
                risk_factors.append("Low probability of profit in stochastic analysis")
                risk_score += 2
            
            if stochastic.risk_metrics["value_at_risk_5pct"] < -1000:
                risk_factors.append("High downside risk")
                risk_score += 2
        
        # Determine overall risk level
        if risk_score >= 6:
            overall_risk = RiskLevel.CRITICAL
        elif risk_score >= 4:
            overall_risk = RiskLevel.HIGH
        elif risk_score >= 2:
            overall_risk = RiskLevel.MEDIUM
        else:
            overall_risk = RiskLevel.LOW
        
        return {
            "overall_risk_level": overall_risk,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "risk_mitigation_recommendations": self._get_risk_mitigation_recommendations(risk_factors)
        }
    
    async def _generate_break_even_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on break-even analysis."""
        
        recommendations = []
        basic_analysis = analysis_results["basic_analysis"]
        risk_assessment = analysis_results["risk_assessment"]
        
        safety_margin = basic_analysis["safety_margin_percentage"]
        break_even_yield = basic_analysis["break_even_yield_per_acre"]
        
        # Safety margin recommendations
        if safety_margin < 20:
            recommendations.append("Consider reducing fertilizer costs or increasing yield targets to improve safety margin")
        
        if break_even_yield > 200:  # Assuming bushels per acre
            recommendations.append("Break-even yield is high - consider optimizing fertilizer efficiency or reducing costs")
        
        # Risk-based recommendations
        if risk_assessment["overall_risk_level"] in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.append("High risk detected - consider hedging strategies or insurance products")
        
        # Stochastic analysis recommendations
        if "stochastic_analysis" in analysis_results:
            stochastic = analysis_results["stochastic_analysis"]
            if stochastic.break_even_probabilities["profitable"] < 0.7:
                recommendations.append("Low probability of profitability - consider alternative strategies")
        
        # Scenario analysis recommendations
        if "scenario_analysis" in analysis_results:
            scenarios = analysis_results["scenario_analysis"]
            pessimistic_scenarios = [s for s in scenarios if s.scenario_type == ScenarioType.PESSIMISTIC]
            if pessimistic_scenarios and pessimistic_scenarios[0].safety_margin < 0:
                recommendations.append("Pessimistic scenario shows losses - develop contingency plans")
        
        return recommendations
    
    # Helper methods
    async def _get_crop_price_distribution(self, request: ROIOptimizationRequest) -> PriceDistribution:
        """Get crop price distribution for stochastic modeling."""
        base_price = request.fields[0].crop_price if request.fields else 0
        return PriceDistribution(
            mean_price=base_price,
            std_deviation=base_price * 0.15,  # 15% volatility
            min_price=base_price * 0.5,
            max_price=base_price * 1.5,
            distribution_type="normal"
        )
    
    async def _get_fertilizer_price_distribution(self, request: ROIOptimizationRequest) -> PriceDistribution:
        """Get fertilizer price distribution for stochastic modeling."""
        return PriceDistribution(
            mean_price=1.0,
            std_deviation=0.1,  # 10% volatility
            min_price=0.7,
            max_price=1.3,
            distribution_type="normal"
        )
    
    async def _get_yield_distribution(self, request: ROIOptimizationRequest) -> PriceDistribution:
        """Get yield distribution for stochastic modeling."""
        return PriceDistribution(
            mean_price=1.0,
            std_deviation=0.15,  # 15% yield volatility
            min_price=0.6,
            max_price=1.4,
            distribution_type="normal"
        )
    
    def _sample_from_distribution(self, distribution: PriceDistribution) -> float:
        """Sample a value from the given distribution."""
        if distribution.distribution_type == "normal":
            return max(distribution.min_price, 
                      min(distribution.max_price, 
                         np.random.normal(distribution.mean_price, distribution.std_deviation)))
        elif distribution.distribution_type == "lognormal":
            return max(distribution.min_price, 
                      min(distribution.max_price, 
                         np.random.lognormal(np.log(distribution.mean_price), distribution.std_deviation)))
        else:  # triangular
            return np.random.triangular(distribution.min_price, distribution.mean_price, distribution.max_price)
    
    def _determine_risk_level(self, safety_margin: float, break_even_yield: float, target_yield: float) -> RiskLevel:
        """Determine risk level based on safety margin and yield metrics."""
        if safety_margin < 0 or break_even_yield > target_yield * 1.2:
            return RiskLevel.CRITICAL
        elif safety_margin < 10 or break_even_yield > target_yield * 1.1:
            return RiskLevel.HIGH
        elif safety_margin < 20 or break_even_yield > target_yield:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _adjust_crop_price(self, request: ROIOptimizationRequest, new_price: float) -> ROIOptimizationRequest:
        """Create adjusted request with new crop price."""
        adjusted_fields = []
        for field in request.fields:
            adjusted_field = FieldData(
                field_id=field.field_id,
                acres=field.acres,
                soil_type=field.soil_type,
                current_ph=field.current_ph,
                organic_matter_percent=field.organic_matter_percent,
                target_yield=field.target_yield,
                crop_price=new_price,
                previous_crop=field.previous_crop,
                tillage_system=field.tillage_system,
                irrigation_available=field.irrigation_available
            )
            adjusted_fields.append(adjusted_field)
        
        return ROIOptimizationRequest(
            fields=adjusted_fields,
            products=request.products,
            optimization_method=request.optimization_method,
            budget_constraints=request.budget_constraints,
            farm_context=request.farm_context
        )
    
    def _adjust_fertilizer_cost(self, cost_structure: CostStructure, new_cost: float) -> CostStructure:
        """Create adjusted cost structure with new fertilizer cost."""
        return CostStructure(
            fixed_costs=cost_structure.fixed_costs,
            variable_costs=cost_structure.variable_costs,
            fertilizer_costs=new_cost,
            application_costs=cost_structure.application_costs,
            opportunity_costs=cost_structure.opportunity_costs,
            total_costs=cost_structure.fixed_costs + cost_structure.variable_costs + 
                       new_cost + cost_structure.application_costs + cost_structure.opportunity_costs
        )
    
    def _calculate_elasticity(self, base_value: float, base_break_even: float, adjusted_break_even: float) -> float:
        """Calculate elasticity of break-even yield to variable changes."""
        if base_value == 0 or base_break_even == 0:
            return 0
        return ((adjusted_break_even - base_break_even) / base_break_even) / 0.1  # 10% change
    
    def _get_risk_mitigation_recommendations(self, risk_factors: List[str]) -> List[str]:
        """Get risk mitigation recommendations based on risk factors."""
        recommendations = []
        
        for factor in risk_factors:
            if "safety margin" in factor.lower():
                recommendations.append("Consider cost reduction strategies or yield improvement techniques")
            elif "profitability" in factor.lower():
                recommendations.append("Evaluate alternative crop or fertilizer strategies")
            elif "downside risk" in factor.lower():
                recommendations.append("Consider hedging or insurance products")
        
        return recommendations
    
    async def _summarize_fields(self, fields: List[FieldData]) -> Dict[str, Any]:
        """Summarize field data for analysis."""
        return {
            "total_fields": len(fields),
            "total_acres": sum(field.acres for field in fields),
            "average_yield_target": sum(field.target_yield for field in fields) / len(fields) if fields else 0,
            "crop_types": list(set(field.previous_crop for field in fields if field.previous_crop)),
            "soil_types": list(set(field.soil_type for field in fields if field.soil_type))
        }
    
    async def _summarize_products(self, products: List[FertilizerProduct]) -> Dict[str, Any]:
        """Summarize fertilizer products for analysis."""
        return {
            "total_products": len(products),
            "nutrient_types": list(set(product.nutrient_type for product in products)),
            "average_cost_per_unit": sum(product.cost_per_unit for product in products) / len(products) if products else 0,
            "product_names": [product.product_name for product in products]
        }