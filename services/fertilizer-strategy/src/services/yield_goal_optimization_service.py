"""
Comprehensive Yield Goal Optimization Service.

This service provides advanced yield goal optimization including:
- Goal-oriented fertilizer planning with economic constraints
- Risk-adjusted optimization and scenario analysis
- Multi-criteria optimization (goal programming, robust optimization)
- Integration with yield response curves and economic analysis
- Optimal fertilizer strategies with goal achievement probability
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, date
from uuid import uuid4, UUID
from enum import Enum
from scipy.optimize import minimize, differential_evolution
from scipy.stats import norm
import pandas as pd
from pydantic import BaseModel, Field

from ..models.yield_goal_models import (
    YieldGoalRequest, YieldGoalAnalysis, YieldGoalRecommendation,
    YieldGoalType, YieldRiskLevel, HistoricalYieldData,
    SoilCharacteristic, WeatherPattern, ManagementPractice
)
from ..models.yield_response_models import (
    YieldResponseCurve, NutrientResponseData, ResponseModelType
)
from ..models.price_models import FertilizerPriceData


class OptimizationObjective(str, Enum):
    """Optimization objectives for yield goal optimization."""
    MAXIMIZE_PROFIT = "maximize_profit"
    MINIMIZE_COST = "minimize_cost"
    MAXIMIZE_YIELD = "maximize_yield"
    MINIMIZE_RISK = "minimize_risk"
    BALANCED = "balanced"


class OptimizationMethod(str, Enum):
    """Optimization methods for yield goal optimization."""
    GOAL_PROGRAMMING = "goal_programming"
    MULTI_CRITERIA = "multi_criteria"
    ROBUST_OPTIMIZATION = "robust_optimization"
    STOCHASTIC = "stochastic"
    GENETIC_ALGORITHM = "genetic_algorithm"


class ScenarioType(str, Enum):
    """Scenario types for optimization analysis."""
    BASELINE = "baseline"
    OPTIMISTIC = "optimistic"
    PESSIMISTIC = "pessimistic"
    STRESS_TEST = "stress_test"


class FertilizerStrategy(BaseModel):
    """Fertilizer application strategy."""
    nitrogen_rate: float = Field(..., ge=0.0, description="Nitrogen application rate (lbs/acre)")
    phosphorus_rate: float = Field(..., ge=0.0, description="Phosphorus application rate (lbs/acre)")
    potassium_rate: float = Field(..., ge=0.0, description="Potassium application rate (lbs/acre)")
    micronutrients: Dict[str, float] = Field(default_factory=dict, description="Micronutrient rates")
    application_timing: List[str] = Field(default_factory=list, description="Application timing")
    application_method: str = Field(..., description="Application method")
    total_cost: float = Field(..., ge=0.0, description="Total fertilizer cost ($/acre)")


class OptimizationConstraints(BaseModel):
    """Constraints for yield goal optimization."""
    max_nitrogen_rate: float = Field(default=300.0, ge=0.0, description="Maximum nitrogen rate")
    max_phosphorus_rate: float = Field(default=150.0, ge=0.0, description="Maximum phosphorus rate")
    max_potassium_rate: float = Field(default=200.0, ge=0.0, description="Maximum potassium rate")
    budget_limit: float = Field(default=200.0, ge=0.0, description="Budget limit ($/acre)")
    environmental_limits: Dict[str, float] = Field(default_factory=dict, description="Environmental limits")
    equipment_constraints: List[str] = Field(default_factory=list, description="Equipment constraints")


class OptimizationScenario(BaseModel):
    """Optimization scenario definition."""
    scenario_type: ScenarioType = Field(..., description="Type of scenario")
    yield_goal: float = Field(..., ge=0.0, description="Target yield goal")
    price_scenario: Dict[str, float] = Field(..., description="Price scenario (fertilizer and crop)")
    weather_scenario: Optional[WeatherPattern] = Field(None, description="Weather scenario")
    risk_tolerance: YieldRiskLevel = Field(..., description="Risk tolerance level")
    probability_weight: float = Field(default=1.0, ge=0.0, le=1.0, description="Scenario probability weight")


class OptimizationResult(BaseModel):
    """Result of yield goal optimization."""
    optimization_id: UUID = Field(..., description="Unique optimization identifier")
    scenario: OptimizationScenario = Field(..., description="Optimization scenario")
    optimal_strategy: FertilizerStrategy = Field(..., description="Optimal fertilizer strategy")
    expected_yield: float = Field(..., ge=0.0, description="Expected yield (bu/acre)")
    yield_probability: float = Field(..., ge=0.0, le=1.0, description="Probability of achieving yield")
    expected_profit: float = Field(..., description="Expected profit ($/acre)")
    profit_probability: float = Field(..., ge=0.0, le=1.0, description="Probability of positive profit")
    risk_metrics: Dict[str, float] = Field(default_factory=dict, description="Risk metrics")
    sensitivity_analysis: Dict[str, Any] = Field(default_factory=dict, description="Sensitivity analysis")
    optimization_metadata: Dict[str, Any] = Field(default_factory=dict, description="Optimization metadata")


class YieldGoalOptimizationRequest(BaseModel):
    """Request for yield goal optimization."""
    field_id: UUID = Field(..., description="Field identifier")
    crop_type: str = Field(..., description="Type of crop")
    yield_goal: float = Field(..., ge=0.0, description="Target yield goal")
    optimization_objective: OptimizationObjective = Field(default=OptimizationObjective.BALANCED)
    optimization_method: OptimizationMethod = Field(default=OptimizationMethod.MULTI_CRITERIA)
    constraints: OptimizationConstraints = Field(..., description="Optimization constraints")
    scenarios: List[OptimizationScenario] = Field(..., description="Optimization scenarios")
    yield_response_curves: List[YieldResponseCurve] = Field(..., description="Yield response curves")
    fertilizer_prices: List[FertilizerPriceData] = Field(..., description="Fertilizer price data")
    crop_price: float = Field(..., ge=0.0, description="Crop price ($/bu)")
    analysis_date: datetime = Field(default_factory=datetime.utcnow)


class YieldGoalOptimizationResponse(BaseModel):
    """Response for yield goal optimization."""
    success: bool = Field(..., description="Optimization success status")
    message: str = Field(..., description="Response message")
    optimization_results: List[OptimizationResult] = Field(..., description="Optimization results")
    best_strategy: Optional[FertilizerStrategy] = Field(None, description="Best overall strategy")
    risk_assessment: Dict[str, Any] = Field(default_factory=dict, description="Risk assessment")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class YieldGoalOptimizationService:
    """
    Comprehensive yield goal optimization service.
    
    Features:
    - Goal-oriented fertilizer planning with economic constraints
    - Risk-adjusted optimization and scenario analysis
    - Multi-criteria optimization (goal programming, robust optimization)
    - Integration with yield response curves and economic analysis
    - Optimal fertilizer strategies with goal achievement probability
    """
    
    def __init__(self):
        """Initialize the yield goal optimization service."""
        self.logger = logging.getLogger(__name__)
        
        # Optimization parameters
        self.optimization_tolerance = 1e-6
        self.max_iterations = 1000
        self.population_size = 50  # For genetic algorithm
        
        # Risk parameters
        self.confidence_levels = [0.5, 0.75, 0.9, 0.95]
        self.risk_free_rate = 0.02  # 2% risk-free rate
        
        # Economic parameters
        self.default_crop_prices = {
            'corn': 5.50,
            'soybean': 13.00,
            'wheat': 7.00,
            'cotton': 0.70,
            'rice': 0.12
        }
        
        self.default_fertilizer_prices = {
            'nitrogen': 0.80,  # $/lb N
            'phosphorus': 0.60,  # $/lb P2O5
            'potassium': 0.50,  # $/lb K2O
            'sulfur': 0.30,  # $/lb S
            'micronutrients': 2.00  # $/lb
        }
    
    async def optimize_yield_goals(self, request: YieldGoalOptimizationRequest) -> YieldGoalOptimizationResponse:
        """
        Perform comprehensive yield goal optimization.
        
        Args:
            request: Yield goal optimization request
            
        Returns:
            Comprehensive optimization results
        """
        try:
            optimization_id = uuid4()
            self.logger.info(f"Starting yield goal optimization {optimization_id}")
            
            # Validate input data
            await self._validate_optimization_request(request)
            
            # Perform optimization for each scenario
            optimization_results = []
            for scenario in request.scenarios:
                result = await self._optimize_scenario(request, scenario, optimization_id)
                optimization_results.append(result)
            
            # Determine best overall strategy
            best_strategy = await self._determine_best_strategy(optimization_results, request)
            
            # Perform risk assessment
            risk_assessment = await self._assess_optimization_risk(optimization_results, request)
            
            # Generate recommendations
            recommendations = await self._generate_optimization_recommendations(
                optimization_results, best_strategy, risk_assessment
            )
            
            # Prepare metadata
            metadata = await self._prepare_optimization_metadata(request, optimization_results)
            
            response = YieldGoalOptimizationResponse(
                success=True,
                message="Yield goal optimization completed successfully",
                optimization_results=optimization_results,
                best_strategy=best_strategy,
                risk_assessment=risk_assessment,
                recommendations=recommendations,
                metadata=metadata
            )
            
            self.logger.info(f"Yield goal optimization {optimization_id} completed")
            return response
            
        except Exception as e:
            self.logger.error(f"Error in yield goal optimization: {e}")
            raise
    
    async def _validate_optimization_request(self, request: YieldGoalOptimizationRequest):
        """Validate optimization request data."""
        if not request.scenarios:
            raise ValueError("At least one optimization scenario is required")
        
        if not request.yield_response_curves:
            raise ValueError("Yield response curves are required for optimization")
        
        if not request.fertilizer_prices:
            raise ValueError("Fertilizer price data is required")
        
        if request.crop_price <= 0:
            raise ValueError("Crop price must be positive")
        
        # Validate scenarios
        for scenario in request.scenarios:
            if scenario.yield_goal <= 0:
                raise ValueError("Scenario yield goal must be positive")
            
            if scenario.probability_weight <= 0 or scenario.probability_weight > 1:
                raise ValueError("Scenario probability weight must be between 0 and 1")
    
    async def _optimize_scenario(
        self,
        request: YieldGoalOptimizationRequest,
        scenario: OptimizationScenario,
        optimization_id: UUID
    ) -> OptimizationResult:
        """Optimize fertilizer strategy for a specific scenario."""
        
        # Select optimization method
        if request.optimization_method == OptimizationMethod.GOAL_PROGRAMMING:
            optimal_strategy = await self._goal_programming_optimization(request, scenario)
        elif request.optimization_method == OptimizationMethod.MULTI_CRITERIA:
            optimal_strategy = await self._multi_criteria_optimization(request, scenario)
        elif request.optimization_method == OptimizationMethod.ROBUST_OPTIMIZATION:
            optimal_strategy = await self._robust_optimization(request, scenario)
        elif request.optimization_method == OptimizationMethod.STOCHASTIC:
            optimal_strategy = await self._stochastic_optimization(request, scenario)
        elif request.optimization_method == OptimizationMethod.GENETIC_ALGORITHM:
            optimal_strategy = await self._genetic_algorithm_optimization(request, scenario)
        else:
            raise ValueError(f"Unsupported optimization method: {request.optimization_method}")
        
        # Calculate expected outcomes
        expected_yield = await self._calculate_expected_yield(optimal_strategy, request.yield_response_curves)
        yield_probability = await self._calculate_yield_probability(expected_yield, scenario.yield_goal)
        
        # Calculate economic outcomes
        expected_profit = await self._calculate_expected_profit(
            optimal_strategy, expected_yield, request.crop_price, scenario.price_scenario
        )
        profit_probability = await self._calculate_profit_probability(expected_profit)
        
        # Calculate risk metrics
        risk_metrics = await self._calculate_risk_metrics(optimal_strategy, expected_yield, expected_profit)
        
        # Perform sensitivity analysis
        sensitivity_analysis = await self._perform_sensitivity_analysis(
            optimal_strategy, request, scenario
        )
        
        # Prepare optimization metadata
        optimization_metadata = {
            "optimization_method": request.optimization_method,
            "optimization_objective": request.optimization_objective,
            "constraints_applied": request.constraints.dict(),
            "convergence_info": {
                "iterations": self.max_iterations,
                "tolerance": self.optimization_tolerance
            }
        }
        
        return OptimizationResult(
            optimization_id=optimization_id,
            scenario=scenario,
            optimal_strategy=optimal_strategy,
            expected_yield=expected_yield,
            yield_probability=yield_probability,
            expected_profit=expected_profit,
            profit_probability=profit_probability,
            risk_metrics=risk_metrics,
            sensitivity_analysis=sensitivity_analysis,
            optimization_metadata=optimization_metadata
        )
    
    async def _goal_programming_optimization(
        self,
        request: YieldGoalOptimizationRequest,
        scenario: OptimizationScenario
    ) -> FertilizerStrategy:
        """Perform goal programming optimization."""
        
        def objective_function(x):
            """Goal programming objective function."""
            n_rate, p_rate, k_rate = x
            
            # Calculate expected yield
            expected_yield = self._calculate_yield_from_rates(n_rate, p_rate, k_rate, request.yield_response_curves)
            
            # Calculate costs
            total_cost = self._calculate_fertilizer_cost(n_rate, p_rate, k_rate, scenario.price_scenario)
            
            # Goal programming: minimize deviations from goals
            yield_deviation = abs(expected_yield - scenario.yield_goal)
            cost_deviation = max(0, total_cost - request.constraints.budget_limit)
            
            # Weighted objective
            return yield_deviation + 0.1 * cost_deviation
        
        # Set up constraints
        constraints = self._setup_optimization_constraints(request.constraints)
        
        # Initial guess
        x0 = [100.0, 50.0, 75.0]  # Initial N, P, K rates
        
        # Bounds
        bounds = [
            (0, request.constraints.max_nitrogen_rate),
            (0, request.constraints.max_phosphorus_rate),
            (0, request.constraints.max_potassium_rate)
        ]
        
        # Optimize
        result = minimize(
            objective_function,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': self.max_iterations, 'ftol': self.optimization_tolerance}
        )
        
        if not result.success:
            self.logger.warning(f"Goal programming optimization did not converge: {result.message}")
            # Use initial guess as fallback
            n_rate, p_rate, k_rate = x0
        else:
            n_rate, p_rate, k_rate = result.x
        
        # Calculate total cost
        total_cost = self._calculate_fertilizer_cost(n_rate, p_rate, k_rate, scenario.price_scenario)
        
        return FertilizerStrategy(
            nitrogen_rate=n_rate,
            phosphorus_rate=p_rate,
            potassium_rate=k_rate,
            total_cost=total_cost,
            application_method="broadcast"
        )
    
    async def _multi_criteria_optimization(
        self,
        request: YieldGoalOptimizationRequest,
        scenario: OptimizationScenario
    ) -> FertilizerStrategy:
        """Perform multi-criteria optimization."""
        
        def multi_objective_function(x):
            """Multi-criteria objective function."""
            n_rate, p_rate, k_rate = x
            
            # Calculate expected yield
            expected_yield = self._calculate_yield_from_rates(n_rate, p_rate, k_rate, request.yield_response_curves)
            
            # Calculate costs
            total_cost = self._calculate_fertilizer_cost(n_rate, p_rate, k_rate, scenario.price_scenario)
            
            # Calculate profit
            expected_profit = (expected_yield * request.crop_price) - total_cost
            
            # Multi-criteria objectives (normalized)
            yield_objective = -expected_yield / scenario.yield_goal  # Negative for maximization
            profit_objective = -expected_profit / (scenario.yield_goal * request.crop_price)
            cost_objective = total_cost / request.constraints.budget_limit
            
            # Weighted combination based on optimization objective
            if request.optimization_objective == OptimizationObjective.MAXIMIZE_YIELD:
                return yield_objective
            elif request.optimization_objective == OptimizationObjective.MAXIMIZE_PROFIT:
                return profit_objective
            elif request.optimization_objective == OptimizationObjective.MINIMIZE_COST:
                return cost_objective
            else:  # BALANCED
                return 0.4 * yield_objective + 0.4 * profit_objective + 0.2 * cost_objective
        
        # Set up constraints
        constraints = self._setup_optimization_constraints(request.constraints)
        
        # Initial guess
        x0 = [100.0, 50.0, 75.0]
        
        # Bounds
        bounds = [
            (0, request.constraints.max_nitrogen_rate),
            (0, request.constraints.max_phosphorus_rate),
            (0, request.constraints.max_potassium_rate)
        ]
        
        # Optimize
        result = minimize(
            multi_objective_function,
            x0,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'maxiter': self.max_iterations, 'ftol': self.optimization_tolerance}
        )
        
        if not result.success:
            self.logger.warning(f"Multi-criteria optimization did not converge: {result.message}")
            n_rate, p_rate, k_rate = x0
        else:
            n_rate, p_rate, k_rate = result.x
        
        total_cost = self._calculate_fertilizer_cost(n_rate, p_rate, k_rate, scenario.price_scenario)
        
        return FertilizerStrategy(
            nitrogen_rate=n_rate,
            phosphorus_rate=p_rate,
            potassium_rate=k_rate,
            total_cost=total_cost,
            application_method="broadcast"
        )
    
    async def _robust_optimization(
        self,
        request: YieldGoalOptimizationRequest,
        scenario: OptimizationScenario
    ) -> FertilizerStrategy:
        """Perform robust optimization considering uncertainty."""
        
        def robust_objective_function(x):
            """Robust optimization objective function."""
            n_rate, p_rate, k_rate = x
            
            # Simulate multiple scenarios with uncertainty
            scenarios = self._generate_uncertainty_scenarios(scenario, num_scenarios=100)
            
            total_objective = 0
            for sim_scenario in scenarios:
                # Calculate yield with uncertainty
                expected_yield = self._calculate_yield_from_rates(
                    n_rate, p_rate, k_rate, request.yield_response_curves
                )
                
                # Add uncertainty
                yield_uncertainty = np.random.normal(0, expected_yield * 0.1)  # 10% uncertainty
                expected_yield += yield_uncertainty
                
                # Calculate profit
                total_cost = self._calculate_fertilizer_cost(n_rate, p_rate, k_rate, sim_scenario.price_scenario)
                expected_profit = (expected_yield * request.crop_price) - total_cost
                
                # Robust objective: minimize worst-case performance
                total_objective += expected_profit
            
            return -total_objective / len(scenarios)  # Negative for maximization
        
        # Use differential evolution for robust optimization
        bounds = [
            (0, request.constraints.max_nitrogen_rate),
            (0, request.constraints.max_phosphorus_rate),
            (0, request.constraints.max_potassium_rate)
        ]
        
        result = differential_evolution(
            robust_objective_function,
            bounds,
            maxiter=self.max_iterations,
            popsize=self.population_size,
            seed=42
        )
        
        n_rate, p_rate, k_rate = result.x
        total_cost = self._calculate_fertilizer_cost(n_rate, p_rate, k_rate, scenario.price_scenario)
        
        return FertilizerStrategy(
            nitrogen_rate=n_rate,
            phosphorus_rate=p_rate,
            potassium_rate=k_rate,
            total_cost=total_cost,
            application_method="broadcast"
        )
    
    async def _stochastic_optimization(
        self,
        request: YieldGoalOptimizationRequest,
        scenario: OptimizationScenario
    ) -> FertilizerStrategy:
        """Perform stochastic optimization."""
        
        def stochastic_objective_function(x):
            """Stochastic optimization objective function."""
            n_rate, p_rate, k_rate = x
            
            # Monte Carlo simulation
            num_simulations = 1000
            profits = []
            
            for _ in range(num_simulations):
                # Sample from yield distribution
                base_yield = self._calculate_yield_from_rates(n_rate, p_rate, k_rate, request.yield_response_curves)
                yield_sample = np.random.normal(base_yield, base_yield * 0.15)  # 15% CV
                
                # Sample from price distribution
                price_sample = np.random.normal(request.crop_price, request.crop_price * 0.2)  # 20% CV
                
                # Calculate profit
                total_cost = self._calculate_fertilizer_cost(n_rate, p_rate, k_rate, scenario.price_scenario)
                profit = (yield_sample * price_sample) - total_cost
                profits.append(profit)
            
            # Risk-adjusted return (Sharpe ratio approximation)
            mean_profit = np.mean(profits)
            std_profit = np.std(profits)
            
            if std_profit > 0:
                risk_adjusted_return = mean_profit / std_profit
            else:
                risk_adjusted_return = mean_profit
            
            return -risk_adjusted_return  # Negative for maximization
        
        bounds = [
            (0, request.constraints.max_nitrogen_rate),
            (0, request.constraints.max_phosphorus_rate),
            (0, request.constraints.max_potassium_rate)
        ]
        
        result = differential_evolution(
            stochastic_objective_function,
            bounds,
            maxiter=self.max_iterations,
            popsize=self.population_size,
            seed=42
        )
        
        n_rate, p_rate, k_rate = result.x
        total_cost = self._calculate_fertilizer_cost(n_rate, p_rate, k_rate, scenario.price_scenario)
        
        return FertilizerStrategy(
            nitrogen_rate=n_rate,
            phosphorus_rate=p_rate,
            potassium_rate=k_rate,
            total_cost=total_cost,
            application_method="broadcast"
        )
    
    async def _genetic_algorithm_optimization(
        self,
        request: YieldGoalOptimizationRequest,
        scenario: OptimizationScenario
    ) -> FertilizerStrategy:
        """Perform genetic algorithm optimization."""
        
        def ga_objective_function(x):
            """Genetic algorithm objective function."""
            n_rate, p_rate, k_rate = x
            
            # Calculate expected yield
            expected_yield = self._calculate_yield_from_rates(n_rate, p_rate, k_rate, request.yield_response_curves)
            
            # Calculate costs
            total_cost = self._calculate_fertilizer_cost(n_rate, p_rate, k_rate, scenario.price_scenario)
            
            # Calculate profit
            expected_profit = (expected_yield * request.crop_price) - total_cost
            
            # Fitness function (higher is better)
            fitness = expected_profit
            
            # Penalty for constraint violations
            if total_cost > request.constraints.budget_limit:
                fitness -= (total_cost - request.constraints.budget_limit) * 10
            
            if n_rate > request.constraints.max_nitrogen_rate:
                fitness -= (n_rate - request.constraints.max_nitrogen_rate) * 5
            
            if p_rate > request.constraints.max_phosphorus_rate:
                fitness -= (p_rate - request.constraints.max_phosphorus_rate) * 5
            
            if k_rate > request.constraints.max_potassium_rate:
                fitness -= (k_rate - request.constraints.max_potassium_rate) * 5
            
            return -fitness  # Negative for minimization
        
        bounds = [
            (0, request.constraints.max_nitrogen_rate),
            (0, request.constraints.max_phosphorus_rate),
            (0, request.constraints.max_potassium_rate)
        ]
        
        result = differential_evolution(
            ga_objective_function,
            bounds,
            maxiter=self.max_iterations,
            popsize=self.population_size,
            seed=42
        )
        
        n_rate, p_rate, k_rate = result.x
        total_cost = self._calculate_fertilizer_cost(n_rate, p_rate, k_rate, scenario.price_scenario)
        
        return FertilizerStrategy(
            nitrogen_rate=n_rate,
            phosphorus_rate=p_rate,
            potassium_rate=k_rate,
            total_cost=total_cost,
            application_method="broadcast"
        )
    
    def _setup_optimization_constraints(self, constraints: OptimizationConstraints) -> List[Dict]:
        """Set up optimization constraints."""
        constraint_list = []
        
        # Budget constraint
        def budget_constraint(x):
            n_rate, p_rate, k_rate = x
            total_cost = self._calculate_fertilizer_cost(n_rate, p_rate, k_rate, self.default_fertilizer_prices)
            return constraints.budget_limit - total_cost
        
        constraint_list.append({'type': 'ineq', 'fun': budget_constraint})
        
        return constraint_list
    
    def _calculate_yield_from_rates(
        self,
        n_rate: float,
        p_rate: float,
        k_rate: float,
        response_curves: List[YieldResponseCurve]
    ) -> float:
        """Calculate expected yield from fertilizer rates using response curves."""
        total_yield = 0.0
        
        for curve in response_curves:
            if curve.nutrient_type == "nitrogen":
                yield_contribution = self._evaluate_response_curve(curve, n_rate)
            elif curve.nutrient_type == "phosphorus":
                yield_contribution = self._evaluate_response_curve(curve, p_rate)
            elif curve.nutrient_type == "potassium":
                yield_contribution = self._evaluate_response_curve(curve, k_rate)
            else:
                continue
            
            total_yield += yield_contribution
        
        # Add base yield (yield with no fertilizer)
        base_yield = 100.0  # Default base yield
        return base_yield + total_yield
    
    def _evaluate_response_curve(self, curve: YieldResponseCurve, rate: float) -> float:
        """Evaluate response curve at given rate."""
        if curve.curve_type == ResponseModelType.MITSCHERLICH_BAULE:
            return self._mitscherlich_baule_response(curve, rate)
        elif curve.curve_type == ResponseModelType.QUADRATIC_PLATEAU:
            return self._quadratic_plateau_response(curve, rate)
        elif curve.curve_type == ResponseModelType.LINEAR_PLATEAU:
            return self._linear_plateau_response(curve, rate)
        elif curve.curve_type == ResponseModelType.EXPONENTIAL:
            return self._exponential_response(curve, rate)
        else:
            return 0.0
    
    def _mitscherlich_baule_response(self, curve: YieldResponseCurve, rate: float) -> float:
        """Calculate Mitscherlich-Baule response."""
        # Simplified Mitscherlich-Baule: Y = A * (1 - exp(-c * X))
        A = curve.max_yield_response
        c = curve.response_coefficient
        return A * (1 - np.exp(-c * rate))
    
    def _quadratic_plateau_response(self, curve: YieldResponseCurve, rate: float) -> float:
        """Calculate quadratic plateau response."""
        # Quadratic plateau: Y = min(A + b*X - c*X^2, plateau)
        A = curve.base_yield
        b = curve.response_coefficient
        c = curve.diminishing_returns_coefficient
        plateau = curve.max_yield_response
        
        quadratic_response = A + b * rate - c * rate**2
        return min(quadratic_response, plateau)
    
    def _linear_plateau_response(self, curve: YieldResponseCurve, rate: float) -> float:
        """Calculate linear plateau response."""
        # Linear plateau: Y = min(A + b*X, plateau)
        A = curve.base_yield
        b = curve.response_coefficient
        plateau = curve.max_yield_response
        
        linear_response = A + b * rate
        return min(linear_response, plateau)
    
    def _exponential_response(self, curve: YieldResponseCurve, rate: float) -> float:
        """Calculate exponential response."""
        # Exponential: Y = A * exp(b * X)
        A = curve.base_yield
        b = curve.response_coefficient
        return A * np.exp(b * rate)
    
    def _calculate_fertilizer_cost(
        self,
        n_rate: float,
        p_rate: float,
        k_rate: float,
        price_scenario: Dict[str, float]
    ) -> float:
        """Calculate total fertilizer cost."""
        n_cost = n_rate * price_scenario.get('nitrogen', self.default_fertilizer_prices['nitrogen'])
        p_cost = p_rate * price_scenario.get('phosphorus', self.default_fertilizer_prices['phosphorus'])
        k_cost = k_rate * price_scenario.get('potassium', self.default_fertilizer_prices['potassium'])
        
        return n_cost + p_cost + k_cost
    
    def _generate_uncertainty_scenarios(self, base_scenario: OptimizationScenario, num_scenarios: int) -> List[OptimizationScenario]:
        """Generate uncertainty scenarios for robust optimization."""
        scenarios = []
        
        for _ in range(num_scenarios):
            # Add uncertainty to prices
            price_scenario = {}
            for nutrient, base_price in base_scenario.price_scenario.items():
                uncertainty = np.random.normal(0, base_price * 0.1)  # 10% price uncertainty
                price_scenario[nutrient] = max(0.1, base_price + uncertainty)
            
            # Create new scenario
            scenario = OptimizationScenario(
                scenario_type=base_scenario.scenario_type,
                yield_goal=base_scenario.yield_goal,
                price_scenario=price_scenario,
                weather_scenario=base_scenario.weather_scenario,
                risk_tolerance=base_scenario.risk_tolerance,
                probability_weight=base_scenario.probability_weight
            )
            scenarios.append(scenario)
        
        return scenarios
    
    async def _calculate_expected_yield(self, strategy: FertilizerStrategy, response_curves: List[YieldResponseCurve]) -> float:
        """Calculate expected yield for a fertilizer strategy."""
        return self._calculate_yield_from_rates(
            strategy.nitrogen_rate,
            strategy.phosphorus_rate,
            strategy.potassium_rate,
            response_curves
        )
    
    async def _calculate_yield_probability(self, expected_yield: float, target_yield: float) -> float:
        """Calculate probability of achieving target yield."""
        # Assume normal distribution with 15% coefficient of variation
        std_dev = expected_yield * 0.15
        probability = 1 - norm.cdf(target_yield, expected_yield, std_dev)
        return max(0.0, min(1.0, probability))
    
    async def _calculate_expected_profit(
        self,
        strategy: FertilizerStrategy,
        expected_yield: float,
        crop_price: float,
        price_scenario: Dict[str, float]
    ) -> float:
        """Calculate expected profit."""
        revenue = expected_yield * crop_price
        cost = strategy.total_cost
        return revenue - cost
    
    async def _calculate_profit_probability(self, expected_profit: float) -> float:
        """Calculate probability of positive profit."""
        # Assume normal distribution with 20% coefficient of variation
        std_dev = abs(expected_profit) * 0.2
        probability = 1 - norm.cdf(0, expected_profit, std_dev)
        return max(0.0, min(1.0, probability))
    
    async def _calculate_risk_metrics(
        self,
        strategy: FertilizerStrategy,
        expected_yield: float,
        expected_profit: float
    ) -> Dict[str, float]:
        """Calculate risk metrics for the strategy."""
        return {
            "yield_volatility": expected_yield * 0.15,  # 15% CV
            "profit_volatility": abs(expected_profit) * 0.2,  # 20% CV
            "value_at_risk_95": expected_profit - 1.96 * abs(expected_profit) * 0.2,
            "conditional_value_at_risk": expected_profit - 2.33 * abs(expected_profit) * 0.2,
            "sharpe_ratio": expected_profit / (abs(expected_profit) * 0.2) if expected_profit != 0 else 0
        }
    
    async def _perform_sensitivity_analysis(
        self,
        strategy: FertilizerStrategy,
        request: YieldGoalOptimizationRequest,
        scenario: OptimizationScenario
    ) -> Dict[str, Any]:
        """Perform sensitivity analysis on the optimal strategy."""
        base_yield = await self._calculate_expected_yield(strategy, request.yield_response_curves)
        base_profit = await self._calculate_expected_profit(
            strategy, base_yield, request.crop_price, scenario.price_scenario
        )
        
        # Price sensitivity
        price_sensitivity = {}
        for price_change in [-0.1, -0.05, 0.05, 0.1]:  # ±5%, ±10%
            new_crop_price = request.crop_price * (1 + price_change)
            new_profit = await self._calculate_expected_profit(
                strategy, base_yield, new_crop_price, scenario.price_scenario
            )
            price_sensitivity[f"{price_change*100:+.0f}%"] = new_profit - base_profit
        
        # Yield sensitivity
        yield_sensitivity = {}
        for yield_change in [-0.1, -0.05, 0.05, 0.1]:  # ±5%, ±10%
            new_yield = base_yield * (1 + yield_change)
            new_profit = await self._calculate_expected_profit(
                strategy, new_yield, request.crop_price, scenario.price_scenario
            )
            yield_sensitivity[f"{yield_change*100:+.0f}%"] = new_profit - base_profit
        
        return {
            "price_sensitivity": price_sensitivity,
            "yield_sensitivity": yield_sensitivity,
            "base_yield": base_yield,
            "base_profit": base_profit
        }
    
    async def _determine_best_strategy(
        self,
        optimization_results: List[OptimizationResult],
        request: YieldGoalOptimizationRequest
    ) -> Optional[FertilizerStrategy]:
        """Determine the best overall strategy across all scenarios."""
        if not optimization_results:
            return None
        
        # Score each result based on multiple criteria
        scored_results = []
        for result in optimization_results:
            score = 0
            
            # Yield achievement (40% weight)
            yield_score = result.yield_probability * 0.4
            
            # Profit potential (40% weight)
            profit_score = result.profit_probability * 0.4
            
            # Risk adjustment (20% weight)
            risk_score = (1 - result.risk_metrics.get("yield_volatility", 0) / 50) * 0.2
            
            total_score = yield_score + profit_score + risk_score
            scored_results.append((total_score, result))
        
        # Return strategy with highest score
        best_result = max(scored_results, key=lambda x: x[0])[1]
        return best_result.optimal_strategy
    
    async def _assess_optimization_risk(
        self,
        optimization_results: List[OptimizationResult],
        request: YieldGoalOptimizationRequest
    ) -> Dict[str, Any]:
        """Assess overall risk across all optimization scenarios."""
        if not optimization_results:
            return {}
        
        # Aggregate risk metrics
        total_yield_probability = sum(r.yield_probability * r.scenario.probability_weight for r in optimization_results)
        total_profit_probability = sum(r.profit_probability * r.scenario.probability_weight for r in optimization_results)
        
        # Calculate portfolio risk metrics
        yields = [r.expected_yield for r in optimization_results]
        profits = [r.expected_profit for r in optimization_results]
        
        yield_volatility = np.std(yields) / np.mean(yields) if np.mean(yields) > 0 else 0
        profit_volatility = np.std(profits) / np.mean(profits) if np.mean(profits) > 0 else 0
        
        # Risk level assessment
        if total_yield_probability > 0.8 and total_profit_probability > 0.8:
            risk_level = "low"
        elif total_yield_probability > 0.6 and total_profit_probability > 0.6:
            risk_level = "medium"
        elif total_yield_probability > 0.4 and total_profit_probability > 0.4:
            risk_level = "high"
        else:
            risk_level = "critical"
        
        return {
            "overall_risk_level": risk_level,
            "weighted_yield_probability": total_yield_probability,
            "weighted_profit_probability": total_profit_probability,
            "yield_volatility": yield_volatility,
            "profit_volatility": profit_volatility,
            "scenario_count": len(optimization_results),
            "risk_factors": self._identify_risk_factors(optimization_results)
        }
    
    def _identify_risk_factors(self, optimization_results: List[OptimizationResult]) -> List[str]:
        """Identify key risk factors from optimization results."""
        risk_factors = []
        
        # Check for low yield probabilities
        low_yield_prob = any(r.yield_probability < 0.5 for r in optimization_results)
        if low_yield_prob:
            risk_factors.append("Low yield achievement probability")
        
        # Check for low profit probabilities
        low_profit_prob = any(r.profit_probability < 0.5 for r in optimization_results)
        if low_profit_prob:
            risk_factors.append("Low profit probability")
        
        # Check for high volatility
        high_volatility = any(r.risk_metrics.get("yield_volatility", 0) > 20 for r in optimization_results)
        if high_volatility:
            risk_factors.append("High yield volatility")
        
        # Check for budget constraints
        budget_constrained = any(r.optimal_strategy.total_cost > 150 for r in optimization_results)
        if budget_constrained:
            risk_factors.append("Budget constraints limiting optimization")
        
        return risk_factors
    
    async def _generate_optimization_recommendations(
        self,
        optimization_results: List[OptimizationResult],
        best_strategy: Optional[FertilizerStrategy],
        risk_assessment: Dict[str, Any]
    ) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        if not optimization_results:
            return ["No optimization results available for recommendations"]
        
        # Strategy recommendations
        if best_strategy:
            recommendations.append(f"Recommended nitrogen rate: {best_strategy.nitrogen_rate:.1f} lbs/acre")
            recommendations.append(f"Recommended phosphorus rate: {best_strategy.phosphorus_rate:.1f} lbs/acre")
            recommendations.append(f"Recommended potassium rate: {best_strategy.potassium_rate:.1f} lbs/acre")
            recommendations.append(f"Expected total cost: ${best_strategy.total_cost:.2f}/acre")
        
        # Risk-based recommendations
        risk_level = risk_assessment.get("overall_risk_level", "unknown")
        if risk_level == "high" or risk_level == "critical":
            recommendations.append("Consider risk mitigation strategies due to high uncertainty")
            recommendations.append("Diversify fertilizer application timing to reduce weather risk")
        
        # Yield probability recommendations
        avg_yield_prob = risk_assessment.get("weighted_yield_probability", 0)
        if avg_yield_prob < 0.6:
            recommendations.append("Yield goal may be too ambitious - consider more conservative targets")
        elif avg_yield_prob > 0.8:
            recommendations.append("High probability of achieving yield goals with current strategy")
        
        # Profit recommendations
        avg_profit_prob = risk_assessment.get("weighted_profit_probability", 0)
        if avg_profit_prob < 0.6:
            recommendations.append("Consider cost reduction strategies to improve profit probability")
        
        return recommendations
    
    async def _prepare_optimization_metadata(
        self,
        request: YieldGoalOptimizationRequest,
        optimization_results: List[OptimizationResult]
    ) -> Dict[str, Any]:
        """Prepare optimization metadata."""
        return {
            "optimization_summary": {
                "total_scenarios": len(request.scenarios),
                "optimization_method": request.optimization_method,
                "optimization_objective": request.optimization_objective,
                "target_yield": request.yield_goal,
                "crop_type": request.crop_type,
                "crop_price": request.crop_price
            },
            "constraints_applied": request.constraints.dict(),
            "scenario_summary": {
                "scenario_types": [s.scenario_type for s in request.scenarios],
                "risk_tolerances": [s.risk_tolerance for s in request.scenarios],
                "probability_weights": [s.probability_weight for s in request.scenarios]
            },
            "optimization_performance": {
                "total_results": len(optimization_results),
                "successful_optimizations": len([r for r in optimization_results if r.expected_profit > 0]),
                "average_yield_probability": np.mean([r.yield_probability for r in optimization_results]),
                "average_profit_probability": np.mean([r.profit_probability for r in optimization_results])
            }
        }