"""
Advanced Economic Optimization Service for fertilizer application method optimization.

This service implements sophisticated optimization algorithms including linear programming,
dynamic programming, and stochastic optimization to provide optimal economic solutions
for fertilizer application methods under various scenarios and constraints.
"""

import asyncio
import logging
import time
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
import json

# Optimization libraries
from scipy.optimize import linprog, minimize
from scipy.stats import norm, uniform

# Optional cvxpy import
try:
    import cvxpy as cp
    CVXPY_AVAILABLE = True
except ImportError:
    CVXPY_AVAILABLE = False
    cp = None

from src.models.application_models import (
    ApplicationMethod, FieldConditions, CropRequirements, 
    FertilizerSpecification, EquipmentSpecification
)
from src.services.cost_analysis_service import CostAnalysisService, EconomicScenario

logger = logging.getLogger(__name__)


class OptimizationAlgorithm(str, Enum):
    """Available optimization algorithms."""
    LINEAR_PROGRAMMING = "linear_programming"
    DYNAMIC_PROGRAMMING = "dynamic_programming"
    STOCHASTIC_OPTIMIZATION = "stochastic_optimization"
    GENETIC_ALGORITHM = "genetic_algorithm"
    SIMULATED_ANNEALING = "simulated_annealing"
    PARTICLE_SWARM = "particle_swarm"


class OptimizationObjective(str, Enum):
    """Optimization objectives."""
    MINIMIZE_COST = "minimize_cost"
    MAXIMIZE_PROFIT = "maximize_profit"
    MAXIMIZE_ROI = "maximize_roi"
    MINIMIZE_RISK = "minimize_risk"
    MAXIMIZE_EFFICIENCY = "maximize_efficiency"
    BALANCED_OPTIMIZATION = "balanced_optimization"


class ScenarioType(str, Enum):
    """Types of economic scenarios."""
    PRICE_SCENARIO = "price_scenario"
    WEATHER_SCENARIO = "weather_scenario"
    YIELD_SCENARIO = "yield_scenario"
    COST_SCENARIO = "cost_scenario"
    MARKET_SCENARIO = "market_scenario"
    COMPREHENSIVE_SCENARIO = "comprehensive_scenario"


@dataclass
class OptimizationConstraint:
    """Optimization constraint definition."""
    constraint_type: str
    variable: str
    operator: str  # '<=', '>=', '=='
    value: float
    description: str


@dataclass
class OptimizationResult:
    """Result of optimization analysis."""
    optimal_methods: List[Dict[str, Any]]
    objective_value: float
    constraint_violations: List[str]
    optimization_time_ms: float
    algorithm_used: str
    convergence_info: Dict[str, Any]
    sensitivity_analysis: Dict[str, Any]


@dataclass
class ScenarioParameters:
    """Parameters for scenario modeling."""
    scenario_type: ScenarioType
    parameters: Dict[str, Any]
    probability: float
    description: str


class EconomicOptimizationService:
    """Advanced economic optimization service for fertilizer application methods."""
    
    def __init__(self):
        """Initialize the economic optimization service."""
        self.cost_service = CostAnalysisService()
        self.optimization_algorithms = self._initialize_optimization_algorithms()
        self.scenario_templates = self._initialize_scenario_templates()
        self.market_data_cache = {}
        
    def _initialize_optimization_algorithms(self) -> Dict[str, callable]:
        """Initialize optimization algorithms."""
        return {
            OptimizationAlgorithm.LINEAR_PROGRAMMING: self._linear_programming_optimization,
            OptimizationAlgorithm.DYNAMIC_PROGRAMMING: self._dynamic_programming_optimization,
            OptimizationAlgorithm.STOCHASTIC_OPTIMIZATION: self._stochastic_optimization,
            OptimizationAlgorithm.GENETIC_ALGORITHM: self._genetic_algorithm_optimization,
            OptimizationAlgorithm.SIMULATED_ANNEALING: self._simulated_annealing_optimization,
            OptimizationAlgorithm.PARTICLE_SWARM: self._particle_swarm_optimization
        }
    
    def _initialize_scenario_templates(self) -> Dict[ScenarioType, Dict[str, Any]]:
        """Initialize scenario modeling templates."""
        return {
            ScenarioType.PRICE_SCENARIO: {
                "fertilizer_price_variation": 0.25,  # ±25% price variation
                "fuel_price_variation": 0.20,
                "labor_price_variation": 0.15,
                "equipment_price_variation": 0.10,
                "crop_price_variation": 0.30
            },
            ScenarioType.WEATHER_SCENARIO: {
                "drought_probability": 0.15,
                "excessive_rain_probability": 0.20,
                "optimal_weather_probability": 0.65,
                "weather_impact_on_yield": 0.20,
                "weather_impact_on_costs": 0.10
            },
            ScenarioType.YIELD_SCENARIO: {
                "low_yield_probability": 0.20,
                "average_yield_probability": 0.60,
                "high_yield_probability": 0.20,
                "yield_variation_factor": 0.25
            },
            ScenarioType.COST_SCENARIO: {
                "low_cost_probability": 0.20,
                "average_cost_probability": 0.60,
                "high_cost_probability": 0.20,
                "cost_variation_factor": 0.30
            },
            ScenarioType.MARKET_SCENARIO: {
                "bull_market_probability": 0.30,
                "bear_market_probability": 0.20,
                "stable_market_probability": 0.50,
                "market_volatility_factor": 0.25
            },
            ScenarioType.COMPREHENSIVE_SCENARIO: {
                "combines_all_scenarios": True,
                "correlation_matrix": self._generate_correlation_matrix(),
                "monte_carlo_iterations": 1000
            }
        }
    
    def _generate_correlation_matrix(self) -> np.ndarray:
        """Generate correlation matrix for comprehensive scenario analysis."""
        # Correlation between different economic factors
        factors = ['fertilizer_price', 'fuel_price', 'labor_price', 'crop_price', 'yield']
        n_factors = len(factors)
        
        # Create correlation matrix (symmetric, diagonal = 1)
        correlation_matrix = np.eye(n_factors)
        
        # Set correlations based on economic relationships
        correlation_matrix[0, 1] = 0.6  # fertilizer_price vs fuel_price
        correlation_matrix[0, 2] = 0.4  # fertilizer_price vs labor_price
        correlation_matrix[0, 3] = -0.3  # fertilizer_price vs crop_price (negative)
        correlation_matrix[0, 4] = 0.2  # fertilizer_price vs yield
        
        correlation_matrix[1, 2] = 0.5  # fuel_price vs labor_price
        correlation_matrix[1, 3] = -0.2  # fuel_price vs crop_price
        correlation_matrix[1, 4] = 0.1  # fuel_price vs yield
        
        correlation_matrix[2, 3] = -0.1  # labor_price vs crop_price
        correlation_matrix[2, 4] = 0.3  # labor_price vs yield
        
        correlation_matrix[3, 4] = 0.8  # crop_price vs yield (strong positive)
        
        # Make matrix symmetric
        correlation_matrix = correlation_matrix + correlation_matrix.T - np.eye(n_factors)
        
        return correlation_matrix
    
    async def optimize_application_methods(
        self,
        application_methods: List[ApplicationMethod],
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        fertilizer_specification: FertilizerSpecification,
        available_equipment: List[EquipmentSpecification],
        objective: OptimizationObjective = OptimizationObjective.BALANCED_OPTIMIZATION,
        algorithm: OptimizationAlgorithm = OptimizationAlgorithm.LINEAR_PROGRAMMING,
        constraints: Optional[List[OptimizationConstraint]] = None,
        scenarios: Optional[List[ScenarioParameters]] = None
    ) -> OptimizationResult:
        """
        Optimize fertilizer application methods using advanced economic optimization.
        
        Args:
            application_methods: Available application methods
            field_conditions: Field conditions
            crop_requirements: Crop requirements
            fertilizer_specification: Fertilizer specification
            available_equipment: Available equipment
            objective: Optimization objective
            algorithm: Optimization algorithm to use
            constraints: Optimization constraints
            scenarios: Economic scenarios to consider
            
        Returns:
            OptimizationResult with optimal solutions
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting economic optimization with {algorithm.value} algorithm")
            
            # Get cost analysis for all methods
            cost_analysis = await self.cost_service.analyze_application_costs(
                application_methods, field_conditions, crop_requirements,
                fertilizer_specification, available_equipment
            )
            
            # Prepare optimization problem
            optimization_problem = await self._prepare_optimization_problem(
                application_methods, cost_analysis, objective, constraints, scenarios
            )
            
            # Select and run optimization algorithm
            optimization_algorithm = self.optimization_algorithms.get(algorithm)
            if not optimization_algorithm:
                raise ValueError(f"Unknown optimization algorithm: {algorithm}")
            
            optimization_result = await optimization_algorithm(optimization_problem)
            
            # Perform sensitivity analysis
            sensitivity_analysis = await self._perform_sensitivity_analysis(
                optimization_problem, optimization_result
            )
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            result = OptimizationResult(
                optimal_methods=optimization_result["optimal_methods"],
                objective_value=optimization_result["objective_value"],
                constraint_violations=optimization_result["constraint_violations"],
                optimization_time_ms=processing_time_ms,
                algorithm_used=algorithm.value,
                convergence_info=optimization_result["convergence_info"],
                sensitivity_analysis=sensitivity_analysis
            )
            
            logger.info(f"Economic optimization completed in {processing_time_ms:.2f}ms")
            return result
            
        except Exception as e:
            logger.error(f"Error in economic optimization: {e}")
            raise
    
    async def _prepare_optimization_problem(
        self,
        application_methods: List[ApplicationMethod],
        cost_analysis: Dict[str, Any],
        objective: OptimizationObjective,
        constraints: Optional[List[OptimizationConstraint]],
        scenarios: Optional[List[ScenarioParameters]]
    ) -> Dict[str, Any]:
        """Prepare optimization problem for solving."""
        
        # Extract cost data for each method
        method_costs = cost_analysis["method_costs"]
        n_methods = len(application_methods)
        
        # Create objective function coefficients
        objective_coefficients = self._create_objective_coefficients(
            method_costs, objective, scenarios
        )
        
        # Create constraint matrix and bounds
        constraint_matrix, constraint_bounds = self._create_constraint_matrix(
            application_methods, constraints, scenarios
        )
        
        # Create variable bounds (method selection variables)
        variable_bounds = [(0, 1) for _ in range(n_methods)]  # Binary variables
        
        optimization_problem = {
            "objective_coefficients": objective_coefficients,
            "constraint_matrix": constraint_matrix,
            "constraint_bounds": constraint_bounds,
            "variable_bounds": variable_bounds,
            "method_costs": method_costs,
            "application_methods": application_methods,
            "objective": objective,
            "scenarios": scenarios
        }
        
        return optimization_problem
    
    def _create_objective_coefficients(
        self,
        method_costs: List[Dict[str, Any]],
        objective: OptimizationObjective,
        scenarios: Optional[List[ScenarioParameters]]
    ) -> np.ndarray:
        """Create objective function coefficients based on optimization objective."""
        
        coefficients = []
        
        for method_cost in method_costs:
            total_cost = method_cost["total_cost_per_acre"]
            
            if objective == OptimizationObjective.MINIMIZE_COST:
                coefficients.append(total_cost)
            elif objective == OptimizationObjective.MAXIMIZE_PROFIT:
                # Assume profit = revenue - cost, revenue estimated from yield
                estimated_revenue = method_cost.get("estimated_revenue_per_acre", total_cost * 2)
                profit = estimated_revenue - total_cost
                coefficients.append(-profit)  # Negative for maximization
            elif objective == OptimizationObjective.MAXIMIZE_ROI:
                # ROI = (revenue - cost) / cost
                estimated_revenue = method_cost.get("estimated_revenue_per_acre", total_cost * 2)
                roi = (estimated_revenue - total_cost) / total_cost if total_cost > 0 else 0
                coefficients.append(-roi)  # Negative for maximization
            elif objective == OptimizationObjective.BALANCED_OPTIMIZATION:
                # Weighted combination of multiple objectives
                estimated_revenue = method_cost.get("estimated_revenue_per_acre", total_cost * 2)
                profit = estimated_revenue - total_cost
                efficiency = method_cost.get("efficiency_score", 0.8)
                
                # Balanced score: 40% cost minimization, 40% profit maximization, 20% efficiency
                balanced_score = 0.4 * total_cost + 0.4 * (-profit) + 0.2 * (-efficiency)
                coefficients.append(balanced_score)
            else:
                coefficients.append(total_cost)
        
        # Apply scenario adjustments if provided
        if scenarios:
            coefficients = self._apply_scenario_adjustments(coefficients, scenarios)
        
        return np.array(coefficients)
    
    def _create_constraint_matrix(
        self,
        application_methods: List[ApplicationMethod],
        constraints: Optional[List[OptimizationConstraint]],
        scenarios: Optional[List[ScenarioParameters]]
    ) -> Tuple[np.ndarray, List[Tuple[float, float]]]:
        """Create constraint matrix and bounds for optimization."""
        
        n_methods = len(application_methods)
        
        # Default constraints
        default_constraints = [
            OptimizationConstraint(
                constraint_type="selection",
                variable="total_methods",
                operator=">=",
                value=1.0,
                description="At least one method must be selected"
            ),
            OptimizationConstraint(
                constraint_type="selection",
                variable="total_methods",
                operator="<=",
                value=n_methods,
                description="Cannot select more methods than available"
            )
        ]
        
        # Combine default and user constraints
        all_constraints = default_constraints + (constraints or [])
        
        # Create constraint matrix
        constraint_matrix = []
        constraint_bounds = []
        
        for constraint in all_constraints:
            if constraint.constraint_type == "selection":
                if constraint.variable == "total_methods":
                    # Sum of all method selection variables
                    constraint_row = [1.0] * n_methods
                    constraint_matrix.append(constraint_row)
                    
                    if constraint.operator == ">=":
                        constraint_bounds.append((constraint.value, np.inf))
                    elif constraint.operator == "<=":
                        constraint_bounds.append((-np.inf, constraint.value))
                    elif constraint.operator == "==":
                        constraint_bounds.append((constraint.value, constraint.value))
        
        # Add scenario-specific constraints
        if scenarios:
            scenario_constraints = self._create_scenario_constraints(scenarios, n_methods)
            constraint_matrix.extend(scenario_constraints["matrix"])
            constraint_bounds.extend(scenario_constraints["bounds"])
        
        return np.array(constraint_matrix) if constraint_matrix else np.array([]), constraint_bounds
    
    def _create_scenario_constraints(
        self,
        scenarios: List[ScenarioParameters],
        n_methods: int
    ) -> Dict[str, Any]:
        """Create constraints based on economic scenarios."""
        
        constraint_matrix = []
        constraint_bounds = []
        
        for scenario in scenarios:
            if scenario.scenario_type == ScenarioType.COST_SCENARIO:
                # Cost scenario constraints
                cost_limit = scenario.parameters.get("max_cost_per_acre", 1000.0)
                constraint_row = [1.0] * n_methods  # Sum of all method costs
                constraint_matrix.append(constraint_row)
                constraint_bounds.append((-np.inf, cost_limit))
            
            elif scenario.scenario_type == ScenarioType.WEATHER_SCENARIO:
                # Weather scenario constraints (e.g., drought-resistant methods only)
                weather_tolerance = scenario.parameters.get("weather_tolerance", 0.7)
                constraint_row = [weather_tolerance] * n_methods
                constraint_matrix.append(constraint_row)
                constraint_bounds.append((weather_tolerance, np.inf))
        
        return {
            "matrix": constraint_matrix,
            "bounds": constraint_bounds
        }
    
    def _apply_scenario_adjustments(
        self,
        coefficients: np.ndarray,
        scenarios: List[ScenarioParameters]
    ) -> np.ndarray:
        """Apply scenario-based adjustments to objective coefficients."""
        
        adjusted_coefficients = coefficients.copy()
        
        for scenario in scenarios:
            if scenario.scenario_type == ScenarioType.PRICE_SCENARIO:
                # Adjust coefficients based on price variations
                price_multiplier = scenario.parameters.get("price_variation_factor", 1.0)
                adjusted_coefficients *= price_multiplier
            
            elif scenario.scenario_type == ScenarioType.WEATHER_SCENARIO:
                # Adjust coefficients based on weather impact
                weather_impact = scenario.parameters.get("weather_impact_factor", 1.0)
                adjusted_coefficients *= weather_impact
        
        return adjusted_coefficients
    
    async def _linear_programming_optimization(
        self,
        optimization_problem: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Solve optimization problem using linear programming."""
        
        try:
            # Extract problem components
            c = optimization_problem["objective_coefficients"]
            A_ub = optimization_problem["constraint_matrix"]
            b_ub = [bound[1] for bound in optimization_problem["constraint_bounds"]]
            bounds = optimization_problem["variable_bounds"]
            
            # Solve linear programming problem
            result = linprog(
                c=c,
                A_ub=A_ub,
                b_ub=b_ub,
                bounds=bounds,
                method='highs'
            )
            
            # Process results
            optimal_methods = []
            if result.success:
                # Find selected methods (variables with value > 0.5)
                selected_indices = [i for i, val in enumerate(result.x) if val > 0.5]
                
                for idx in selected_indices:
                    method_data = {
                        "method_index": idx,
                        "selection_weight": result.x[idx],
                        "method": optimization_problem["application_methods"][idx],
                        "cost": optimization_problem["method_costs"][idx]
                    }
                    optimal_methods.append(method_data)
            
            return {
                "optimal_methods": optimal_methods,
                "objective_value": result.fun,
                "constraint_violations": [],
                "convergence_info": {
                    "success": result.success,
                    "message": result.message,
                    "iterations": getattr(result, 'nit', 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in linear programming optimization: {e}")
            return {
                "optimal_methods": [],
                "objective_value": float('inf'),
                "constraint_violations": [str(e)],
                "convergence_info": {"success": False, "message": str(e)}
            }
    
    async def _dynamic_programming_optimization(
        self,
        optimization_problem: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Solve optimization problem using dynamic programming."""
        
        try:
            # Dynamic programming for method selection
            n_methods = len(optimization_problem["application_methods"])
            costs = optimization_problem["objective_coefficients"]
            
            # DP table: dp[i][j] = minimum cost to select j methods from first i methods
            dp = np.full((n_methods + 1, n_methods + 1), float('inf'))
            dp[0][0] = 0
            
            # Fill DP table
            for i in range(1, n_methods + 1):
                for j in range(n_methods + 1):
                    # Don't select method i
                    dp[i][j] = dp[i-1][j]
                    
                    # Select method i
                    if j > 0:
                        dp[i][j] = min(dp[i][j], dp[i-1][j-1] + costs[i-1])
            
            # Find optimal solution
            min_cost = min(dp[n_methods])
            optimal_j = np.argmin(dp[n_methods])
            
            # Backtrack to find selected methods
            selected_methods = []
            i, j = n_methods, optimal_j
            
            while i > 0 and j > 0:
                if dp[i][j] == dp[i-1][j-1] + costs[i-1]:
                    selected_methods.append(i-1)
                    j -= 1
                i -= 1
            
            # Prepare results
            optimal_methods = []
            for idx in selected_methods:
                method_data = {
                    "method_index": idx,
                    "selection_weight": 1.0,
                    "method": optimization_problem["application_methods"][idx],
                    "cost": optimization_problem["method_costs"][idx]
                }
                optimal_methods.append(method_data)
            
            return {
                "optimal_methods": optimal_methods,
                "objective_value": min_cost,
                "constraint_violations": [],
                "convergence_info": {
                    "success": True,
                    "message": "Dynamic programming completed",
                    "iterations": n_methods * n_methods
                }
            }
            
        except Exception as e:
            logger.error(f"Error in dynamic programming optimization: {e}")
            return {
                "optimal_methods": [],
                "objective_value": float('inf'),
                "constraint_violations": [str(e)],
                "convergence_info": {"success": False, "message": str(e)}
            }
    
    async def _stochastic_optimization(
        self,
        optimization_problem: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Solve optimization problem using stochastic optimization."""
        
        try:
            # Monte Carlo simulation for stochastic optimization
            n_iterations = 1000
            n_methods = len(optimization_problem["application_methods"])
            costs = optimization_problem["objective_coefficients"]
            
            best_solution = None
            best_cost = float('inf')
            
            for iteration in range(n_iterations):
                # Generate random solution
                solution = np.random.random(n_methods)
                solution = (solution > 0.5).astype(int)  # Binary solution
                
                # Calculate cost for this solution
                total_cost = np.dot(solution, costs)
                
                # Check constraints (simplified)
                if np.sum(solution) >= 1 and np.sum(solution) <= n_methods:
                    if total_cost < best_cost:
                        best_cost = total_cost
                        best_solution = solution
            
            # Prepare results
            optimal_methods = []
            if best_solution is not None:
                selected_indices = np.where(best_solution)[0]
                
                for idx in selected_indices:
                    method_data = {
                        "method_index": idx,
                        "selection_weight": best_solution[idx],
                        "method": optimization_problem["application_methods"][idx],
                        "cost": optimization_problem["method_costs"][idx]
                    }
                    optimal_methods.append(method_data)
            
            return {
                "optimal_methods": optimal_methods,
                "objective_value": best_cost,
                "constraint_violations": [],
                "convergence_info": {
                    "success": True,
                    "message": "Stochastic optimization completed",
                    "iterations": n_iterations
                }
            }
            
        except Exception as e:
            logger.error(f"Error in stochastic optimization: {e}")
            return {
                "optimal_methods": [],
                "objective_value": float('inf'),
                "constraint_violations": [str(e)],
                "convergence_info": {"success": False, "message": str(e)}
            }
    
    async def _genetic_algorithm_optimization(
        self,
        optimization_problem: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Solve optimization problem using genetic algorithm."""
        
        try:
            # Genetic algorithm parameters
            population_size = 50
            generations = 100
            mutation_rate = 0.1
            crossover_rate = 0.8
            
            n_methods = len(optimization_problem["application_methods"])
            costs = optimization_problem["objective_coefficients"]
            
            # Initialize population
            population = np.random.randint(0, 2, (population_size, n_methods))
            
            best_solution = None
            best_cost = float('inf')
            
            for generation in range(generations):
                # Evaluate fitness
                fitness = []
                for individual in population:
                    if np.sum(individual) >= 1:  # Valid solution
                        cost = np.dot(individual, costs)
                        fitness.append(-cost)  # Negative cost for maximization
                    else:
                        fitness.append(-float('inf'))  # Invalid solution
                
                # Find best individual
                best_idx = np.argmax(fitness)
                if fitness[best_idx] > -best_cost:
                    best_cost = -fitness[best_idx]
                    best_solution = population[best_idx].copy()
                
                # Selection, crossover, and mutation
                new_population = []
                
                for _ in range(population_size):
                    # Selection (tournament selection)
                    parent1 = self._tournament_selection(population, fitness)
                    parent2 = self._tournament_selection(population, fitness)
                    
                    # Crossover
                    if np.random.random() < crossover_rate:
                        child = self._crossover(parent1, parent2)
                    else:
                        child = parent1.copy()
                    
                    # Mutation
                    if np.random.random() < mutation_rate:
                        child = self._mutate(child)
                    
                    new_population.append(child)
                
                population = np.array(new_population)
            
            # Prepare results
            optimal_methods = []
            if best_solution is not None:
                selected_indices = np.where(best_solution)[0]
                
                for idx in selected_indices:
                    method_data = {
                        "method_index": idx,
                        "selection_weight": best_solution[idx],
                        "method": optimization_problem["application_methods"][idx],
                        "cost": optimization_problem["method_costs"][idx]
                    }
                    optimal_methods.append(method_data)
            
            return {
                "optimal_methods": optimal_methods,
                "objective_value": best_cost,
                "constraint_violations": [],
                "convergence_info": {
                    "success": True,
                    "message": "Genetic algorithm completed",
                    "iterations": generations,
                    "population_size": population_size
                }
            }
            
        except Exception as e:
            logger.error(f"Error in genetic algorithm optimization: {e}")
            return {
                "optimal_methods": [],
                "objective_value": float('inf'),
                "constraint_violations": [str(e)],
                "convergence_info": {"success": False, "message": str(e)}
            }
    
    def _tournament_selection(self, population: np.ndarray, fitness: List[float]) -> np.ndarray:
        """Tournament selection for genetic algorithm."""
        tournament_size = 3
        tournament_indices = np.random.choice(len(population), tournament_size, replace=False)
        tournament_fitness = [fitness[i] for i in tournament_indices]
        winner_idx = tournament_indices[np.argmax(tournament_fitness)]
        return population[winner_idx]
    
    def _crossover(self, parent1: np.ndarray, parent2: np.ndarray) -> np.ndarray:
        """Single-point crossover for genetic algorithm."""
        crossover_point = np.random.randint(1, len(parent1))
        child = np.concatenate([parent1[:crossover_point], parent2[crossover_point:]])
        return child
    
    def _mutate(self, individual: np.ndarray) -> np.ndarray:
        """Bit-flip mutation for genetic algorithm."""
        mutation_point = np.random.randint(len(individual))
        individual[mutation_point] = 1 - individual[mutation_point]
        return individual
    
    async def _simulated_annealing_optimization(
        self,
        optimization_problem: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Solve optimization problem using simulated annealing."""
        
        try:
            # Simulated annealing parameters
            initial_temp = 1000.0
            final_temp = 0.1
            cooling_rate = 0.95
            max_iterations = 1000
            
            n_methods = len(optimization_problem["application_methods"])
            costs = optimization_problem["objective_coefficients"]
            
            # Initialize solution
            current_solution = np.random.randint(0, 2, n_methods)
            if np.sum(current_solution) == 0:  # Ensure at least one method selected
                current_solution[np.random.randint(n_methods)] = 1
            
            current_cost = np.dot(current_solution, costs)
            best_solution = current_solution.copy()
            best_cost = current_cost
            
            temperature = initial_temp
            iteration = 0
            
            while temperature > final_temp and iteration < max_iterations:
                # Generate neighbor solution
                neighbor = current_solution.copy()
                flip_idx = np.random.randint(n_methods)
                neighbor[flip_idx] = 1 - neighbor[flip_idx]
                
                # Ensure at least one method selected
                if np.sum(neighbor) == 0:
                    neighbor[np.random.randint(n_methods)] = 1
                
                neighbor_cost = np.dot(neighbor, costs)
                
                # Accept or reject neighbor
                if neighbor_cost < current_cost or np.random.random() < np.exp(-(neighbor_cost - current_cost) / temperature):
                    current_solution = neighbor
                    current_cost = neighbor_cost
                    
                    if current_cost < best_cost:
                        best_solution = current_solution.copy()
                        best_cost = current_cost
                
                temperature *= cooling_rate
                iteration += 1
            
            # Prepare results
            optimal_methods = []
            selected_indices = np.where(best_solution)[0]
            
            for idx in selected_indices:
                method_data = {
                    "method_index": idx,
                    "selection_weight": best_solution[idx],
                    "method": optimization_problem["application_methods"][idx],
                    "cost": optimization_problem["method_costs"][idx]
                }
                optimal_methods.append(method_data)
            
            return {
                "optimal_methods": optimal_methods,
                "objective_value": best_cost,
                "constraint_violations": [],
                "convergence_info": {
                    "success": True,
                    "message": "Simulated annealing completed",
                    "iterations": iteration,
                    "final_temperature": temperature
                }
            }
            
        except Exception as e:
            logger.error(f"Error in simulated annealing optimization: {e}")
            return {
                "optimal_methods": [],
                "objective_value": float('inf'),
                "constraint_violations": [str(e)],
                "convergence_info": {"success": False, "message": str(e)}
            }
    
    async def _particle_swarm_optimization(
        self,
        optimization_problem: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Solve optimization problem using particle swarm optimization."""
        
        try:
            # PSO parameters
            n_particles = 30
            n_iterations = 100
            w = 0.9  # inertia weight
            c1 = 2.0  # cognitive parameter
            c2 = 2.0  # social parameter
            
            n_methods = len(optimization_problem["application_methods"])
            costs = optimization_problem["objective_coefficients"]
            
            # Initialize particles
            particles = np.random.random((n_particles, n_methods))
            velocities = np.random.random((n_particles, n_methods)) * 0.1
            
            # Initialize best positions
            personal_best = particles.copy()
            personal_best_costs = [np.dot(p, costs) for p in particles]
            
            global_best_idx = np.argmin(personal_best_costs)
            global_best = personal_best[global_best_idx].copy()
            global_best_cost = personal_best_costs[global_best_idx]
            
            for iteration in range(n_iterations):
                for i in range(n_particles):
                    # Update velocity
                    r1, r2 = np.random.random(2)
                    velocities[i] = (w * velocities[i] + 
                                   c1 * r1 * (personal_best[i] - particles[i]) +
                                   c2 * r2 * (global_best - particles[i]))
                    
                    # Update position
                    particles[i] += velocities[i]
                    
                    # Ensure binary values
                    particles[i] = np.clip(particles[i], 0, 1)
                    particles[i] = (particles[i] > 0.5).astype(int)
                    
                    # Ensure at least one method selected
                    if np.sum(particles[i]) == 0:
                        particles[i][np.random.randint(n_methods)] = 1
                    
                    # Evaluate fitness
                    current_cost = np.dot(particles[i], costs)
                    
                    # Update personal best
                    if current_cost < personal_best_costs[i]:
                        personal_best[i] = particles[i].copy()
                        personal_best_costs[i] = current_cost
                        
                        # Update global best
                        if current_cost < global_best_cost:
                            global_best = particles[i].copy()
                            global_best_cost = current_cost
            
            # Prepare results
            optimal_methods = []
            selected_indices = np.where(global_best)[0]
            
            for idx in selected_indices:
                method_data = {
                    "method_index": idx,
                    "selection_weight": global_best[idx],
                    "method": optimization_problem["application_methods"][idx],
                    "cost": optimization_problem["method_costs"][idx]
                }
                optimal_methods.append(method_data)
            
            return {
                "optimal_methods": optimal_methods,
                "objective_value": global_best_cost,
                "constraint_violations": [],
                "convergence_info": {
                    "success": True,
                    "message": "Particle swarm optimization completed",
                    "iterations": n_iterations,
                    "particles": n_particles
                }
            }
            
        except Exception as e:
            logger.error(f"Error in particle swarm optimization: {e}")
            return {
                "optimal_methods": [],
                "objective_value": float('inf'),
                "constraint_violations": [str(e)],
                "convergence_info": {"success": False, "message": str(e)}
            }
    
    async def _perform_sensitivity_analysis(
        self,
        optimization_problem: Dict[str, Any],
        optimization_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform sensitivity analysis on optimization results."""
        
        try:
            sensitivity_results = {}
            
            # Cost sensitivity analysis
            base_costs = optimization_problem["objective_coefficients"]
            cost_variations = [0.8, 0.9, 1.0, 1.1, 1.2]  # ±20% cost variations
            
            cost_sensitivity = []
            for variation in cost_variations:
                adjusted_costs = base_costs * variation
                # Re-run optimization with adjusted costs (simplified)
                estimated_objective = np.dot(optimization_result["optimal_methods"][0]["selection_weight"], adjusted_costs)
                cost_sensitivity.append({
                    "cost_multiplier": variation,
                    "objective_value": estimated_objective,
                    "change_percent": (estimated_objective - optimization_result["objective_value"]) / optimization_result["objective_value"] * 100
                })
            
            sensitivity_results["cost_sensitivity"] = cost_sensitivity
            
            # Scenario sensitivity analysis
            if optimization_problem.get("scenarios"):
                scenario_sensitivity = []
                for scenario in optimization_problem["scenarios"]:
                    scenario_impact = self._calculate_scenario_impact(scenario, optimization_result)
                    scenario_sensitivity.append(scenario_impact)
                
                sensitivity_results["scenario_sensitivity"] = scenario_sensitivity
            
            return sensitivity_results
            
        except Exception as e:
            logger.error(f"Error in sensitivity analysis: {e}")
            return {"error": str(e)}
    
    def _calculate_scenario_impact(
        self,
        scenario: ScenarioParameters,
        optimization_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate impact of a specific scenario on optimization results."""
        
        impact_factors = {
            "scenario_type": scenario.scenario_type.value,
            "probability": scenario.probability,
            "description": scenario.description,
            "impact_on_objective": 0.0,  # Simplified calculation
            "risk_level": "medium"
        }
        
        # Calculate impact based on scenario type
        if scenario.scenario_type == ScenarioType.PRICE_SCENARIO:
            price_variation = scenario.parameters.get("price_variation_factor", 1.0)
            impact_factors["impact_on_objective"] = (price_variation - 1.0) * 100
            impact_factors["risk_level"] = "high" if abs(price_variation - 1.0) > 0.2 else "medium"
        
        elif scenario.scenario_type == ScenarioType.WEATHER_SCENARIO:
            weather_impact = scenario.parameters.get("weather_impact_factor", 1.0)
            impact_factors["impact_on_objective"] = (weather_impact - 1.0) * 100
            impact_factors["risk_level"] = "high" if abs(weather_impact - 1.0) > 0.3 else "medium"
        
        return impact_factors
    
    async def _generate_scenarios_for_type(
        self,
        scenario_type: ScenarioType,
        count: int
    ) -> List[ScenarioParameters]:
        """Generate scenarios for a specific scenario type."""
        scenarios = []
        
        for i in range(count):
            if scenario_type == ScenarioType.PRICE_SCENARIO:
                scenario = ScenarioParameters(
                    scenario_type=scenario_type,
                    parameters={
                        "fertilizer_price_variation": np.random.uniform(0.7, 1.3),
                        "fuel_price_variation": np.random.uniform(0.8, 1.2),
                        "labor_price_variation": np.random.uniform(0.85, 1.15),
                        "crop_price_variation": np.random.uniform(0.7, 1.3)
                    },
                    probability=1.0 / count,
                    description=f"Price scenario {i+1}"
                )
            elif scenario_type == ScenarioType.WEATHER_SCENARIO:
                scenario = ScenarioParameters(
                    scenario_type=scenario_type,
                    parameters={
                        "drought_probability": np.random.uniform(0.1, 0.3),
                        "excessive_rain_probability": np.random.uniform(0.1, 0.3),
                        "optimal_weather_probability": np.random.uniform(0.4, 0.8),
                        "weather_impact_on_yield": np.random.uniform(0.1, 0.3)
                    },
                    probability=1.0 / count,
                    description=f"Weather scenario {i+1}"
                )
            elif scenario_type == ScenarioType.YIELD_SCENARIO:
                scenario = ScenarioParameters(
                    scenario_type=scenario_type,
                    parameters={
                        "low_yield_probability": np.random.uniform(0.1, 0.3),
                        "average_yield_probability": np.random.uniform(0.5, 0.7),
                        "high_yield_probability": np.random.uniform(0.1, 0.3),
                        "yield_variation_factor": np.random.uniform(0.2, 0.4)
                    },
                    probability=1.0 / count,
                    description=f"Yield scenario {i+1}"
                )
            else:
                # Default scenario
                scenario = ScenarioParameters(
                    scenario_type=scenario_type,
                    parameters={"variation_factor": np.random.uniform(0.8, 1.2)},
                    probability=1.0 / count,
                    description=f"Scenario {i+1}"
                )
            
            scenarios.append(scenario)
        
        return scenarios
    
    async def _summarize_scenario_results(
        self,
        scenario_optimizations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Summarize results from multiple scenario optimizations."""
        if not scenario_optimizations:
            return {"error": "No scenario optimizations provided"}
        
        objective_values = [opt["optimization_result"]["objective_value"] for opt in scenario_optimizations]
        optimal_methods = [opt["optimization_result"]["optimal_methods"] for opt in scenario_optimizations]
        
        summary = {
            "scenario_count": len(scenario_optimizations),
            "objective_value_stats": {
                "min": min(objective_values),
                "max": max(objective_values),
                "mean": np.mean(objective_values),
                "std": np.std(objective_values)
            },
            "method_selection_frequency": self._calculate_method_frequency(optimal_methods),
            "risk_assessment": {
                "volatility": np.std(objective_values) / np.mean(objective_values) if np.mean(objective_values) > 0 else 0,
                "risk_level": "high" if np.std(objective_values) / np.mean(objective_values) > 0.2 else "medium" if np.std(objective_values) / np.mean(objective_values) > 0.1 else "low"
            }
        }
        
        return summary
    
    def _calculate_method_frequency(
        self,
        optimal_methods_list: List[List[Dict[str, Any]]]
    ) -> Dict[str, float]:
        """Calculate frequency of method selection across scenarios."""
        method_counts = {}
        total_scenarios = len(optimal_methods_list)
        
        for optimal_methods in optimal_methods_list:
            for method_data in optimal_methods:
                method_id = method_data.get("method", {}).get("method_id", "unknown")
                method_counts[method_id] = method_counts.get(method_id, 0) + 1
        
        # Convert counts to frequencies
        method_frequencies = {
            method_id: count / total_scenarios 
            for method_id, count in method_counts.items()
        }
        
        return method_frequencies
    
    async def _perform_monte_carlo_analysis(
        self,
        optimization_request: Dict[str, Any],
        iterations: int
    ) -> Dict[str, Any]:
        """Perform Monte Carlo analysis for uncertainty quantification."""
        results = []
        
        for i in range(iterations):
            # Generate random scenario parameters
            random_scenario = ScenarioParameters(
                scenario_type=ScenarioType.COMPREHENSIVE_SCENARIO,
                parameters={
                    "fertilizer_price_variation": np.random.normal(1.0, 0.1),
                    "fuel_price_variation": np.random.normal(1.0, 0.08),
                    "labor_price_variation": np.random.normal(1.0, 0.05),
                    "weather_impact_factor": np.random.normal(1.0, 0.15),
                    "yield_variation_factor": np.random.normal(1.0, 0.1)
                },
                probability=1.0 / iterations,
                description=f"Monte Carlo iteration {i+1}"
            )
            
            # Run optimization with random scenario
            try:
                result = await self.optimize_application_methods(
                    application_methods=optimization_request["application_methods"],
                    field_conditions=optimization_request["field_conditions"],
                    crop_requirements=optimization_request["crop_requirements"],
                    fertilizer_specification=optimization_request["fertilizer_specification"],
                    available_equipment=optimization_request["available_equipment"],
                    objective=optimization_request["objective"],
                    algorithm=optimization_request["algorithm"],
                    constraints=optimization_request["constraints"],
                    scenarios=[random_scenario]
                )
                results.append(result.objective_value)
            except Exception as e:
                logger.warning(f"Monte Carlo iteration {i+1} failed: {e}")
                continue
        
        if not results:
            return {"error": "All Monte Carlo iterations failed"}
        
        # Calculate statistics
        monte_carlo_stats = {
            "iterations_completed": len(results),
            "total_iterations": iterations,
            "objective_value_stats": {
                "min": min(results),
                "max": max(results),
                "mean": np.mean(results),
                "std": np.std(results),
                "percentile_5": np.percentile(results, 5),
                "percentile_95": np.percentile(results, 95)
            },
            "risk_metrics": {
                "value_at_risk_5": np.percentile(results, 5),
                "expected_shortfall": np.mean([r for r in results if r <= np.percentile(results, 5)]),
                "volatility": np.std(results) / np.mean(results) if np.mean(results) > 0 else 0
            }
        }
        
        return monte_carlo_stats
    
    async def _analyze_parameter_sensitivity(
        self,
        optimization_request: Dict[str, Any],
        param_name: str,
        param_range: Dict[str, float],
        base_result: OptimizationResult
    ) -> Dict[str, Any]:
        """Analyze sensitivity of a specific parameter."""
        param_values = np.linspace(param_range["min"], param_range["max"], 10)
        sensitivity_results = []
        
        for param_value in param_values:
            # Create modified request with parameter value
            modified_request = optimization_request.copy()
            
            # Apply parameter modification (simplified)
            if param_name in modified_request:
                modified_request[param_name] = param_value
            
            try:
                # Run optimization with modified parameter
                result = await self.optimize_application_methods(
                    application_methods=modified_request["application_methods"],
                    field_conditions=modified_request["field_conditions"],
                    crop_requirements=modified_request["crop_requirements"],
                    fertilizer_specification=modified_request["fertilizer_specification"],
                    available_equipment=modified_request["available_equipment"],
                    objective=modified_request["objective"],
                    algorithm=modified_request["algorithm"],
                    constraints=modified_request["constraints"],
                    scenarios=modified_request["scenarios"]
                )
                
                sensitivity_results.append({
                    "parameter_value": param_value,
                    "objective_value": result.objective_value,
                    "change_percent": (result.objective_value - base_result.objective_value) / base_result.objective_value * 100 if base_result.objective_value > 0 else 0
                })
            except Exception as e:
                logger.warning(f"Sensitivity analysis failed for {param_name}={param_value}: {e}")
                continue
        
        # Calculate sensitivity metrics
        if sensitivity_results:
            objective_values = [r["objective_value"] for r in sensitivity_results]
            sensitivity_metrics = {
                "parameter_name": param_name,
                "parameter_range": param_range,
                "sensitivity_results": sensitivity_results,
                "sensitivity_metrics": {
                    "max_change_percent": max([abs(r["change_percent"]) for r in sensitivity_results]),
                    "sensitivity_coefficient": np.std(objective_values) / np.mean(objective_values) if np.mean(objective_values) > 0 else 0,
                    "is_sensitive": max([abs(r["change_percent"]) for r in sensitivity_results]) > 10
                }
            }
        else:
            sensitivity_metrics = {
                "parameter_name": param_name,
                "parameter_range": param_range,
                "error": "All sensitivity analysis iterations failed"
            }
        
        return sensitivity_metrics
    
    async def _perform_risk_assessment(
        self,
        sensitivity_results: Dict[str, Any],
        base_result: OptimizationResult
    ) -> Dict[str, Any]:
        """Perform comprehensive risk assessment."""
        risk_factors = []
        
        for param_name, sensitivity_data in sensitivity_results.items():
            if "sensitivity_metrics" in sensitivity_data:
                metrics = sensitivity_data["sensitivity_metrics"]
                risk_level = "high" if metrics["max_change_percent"] > 20 else "medium" if metrics["max_change_percent"] > 10 else "low"
                
                risk_factors.append({
                    "parameter": param_name,
                    "risk_level": risk_level,
                    "max_impact_percent": metrics["max_change_percent"],
                    "sensitivity_coefficient": metrics["sensitivity_coefficient"]
                })
        
        # Calculate overall risk assessment
        high_risk_params = [rf for rf in risk_factors if rf["risk_level"] == "high"]
        medium_risk_params = [rf for rf in risk_factors if rf["risk_level"] == "medium"]
        
        overall_risk_level = "high" if len(high_risk_params) > 0 else "medium" if len(medium_risk_params) > 0 else "low"
        
        risk_assessment = {
            "overall_risk_level": overall_risk_level,
            "risk_factors": risk_factors,
            "risk_summary": {
                "high_risk_parameters": len(high_risk_params),
                "medium_risk_parameters": len(medium_risk_params),
                "low_risk_parameters": len(risk_factors) - len(high_risk_params) - len(medium_risk_params),
                "total_parameters_assessed": len(risk_factors)
            },
            "risk_mitigation": self._generate_risk_mitigation_recommendations(risk_factors)
        }
        
        return risk_assessment
    
    def _generate_risk_mitigation_recommendations(
        self,
        risk_factors: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate risk mitigation recommendations based on risk factors."""
        recommendations = []
        
        high_risk_params = [rf for rf in risk_factors if rf["risk_level"] == "high"]
        
        if high_risk_params:
            recommendations.append("Consider hedging strategies for high-risk parameters")
            recommendations.append("Implement monitoring systems for critical parameters")
            recommendations.append("Develop contingency plans for worst-case scenarios")
        
        if len(high_risk_params) > 2:
            recommendations.append("Consider diversifying approach to reduce overall risk")
        
        recommendations.append("Regular sensitivity analysis recommended for ongoing risk management")
        
        return recommendations
    
    async def _perform_investment_analysis(
        self,
        base_result: OptimizationResult,
        horizon_years: int,
        discount_rate: float,
        include_equipment: bool,
        include_maintenance: bool
    ) -> Dict[str, Any]:
        """Perform investment analysis for optimization results."""
        investment_analysis = {
            "investment_horizon_years": horizon_years,
            "discount_rate": discount_rate,
            "base_optimization": base_result,
            "investment_components": {},
            "financial_metrics": {}
        }
        
        # Calculate NPV for each optimal method
        for method_data in base_result.optimal_methods:
            method_id = method_data.get("method", {}).get("method_id", "unknown")
            cost_per_acre = method_data.get("cost", {}).get("total_cost_per_acre", 0)
            
            # Simplified NPV calculation
            annual_cash_flow = -cost_per_acre  # Negative for costs
            npv = sum(annual_cash_flow / (1 + discount_rate) ** year for year in range(1, horizon_years + 1))
            
            investment_analysis["investment_components"][method_id] = {
                "cost_per_acre": cost_per_acre,
                "npv": npv,
                "annual_cash_flow": annual_cash_flow
            }
        
        # Calculate overall financial metrics
        total_npv = sum(comp["npv"] for comp in investment_analysis["investment_components"].values())
        investment_analysis["financial_metrics"] = {
            "total_npv": total_npv,
            "average_npv_per_method": total_npv / len(base_result.optimal_methods) if base_result.optimal_methods else 0,
            "investment_horizon_years": horizon_years,
            "discount_rate": discount_rate
        }
        
        return investment_analysis
    
    async def _generate_financial_projections(
        self,
        investment_analysis: Dict[str, Any],
        horizon_years: int
    ) -> Dict[str, Any]:
        """Generate financial projections for investment analysis."""
        projections = {
            "yearly_projections": [],
            "cumulative_metrics": {},
            "sensitivity_analysis": {}
        }
        
        # Generate yearly projections
        for year in range(1, horizon_years + 1):
            year_data = {
                "year": year,
                "discount_factor": 1 / (1 + investment_analysis["discount_rate"]) ** year,
                "projected_cash_flows": {},
                "cumulative_npv": 0
            }
            
            # Calculate cash flows for each method
            for method_id, component in investment_analysis["investment_components"].items():
                year_data["projected_cash_flows"][method_id] = component["annual_cash_flow"]
                year_data["cumulative_npv"] += component["annual_cash_flow"] * year_data["discount_factor"]
            
            projections["yearly_projections"].append(year_data)
        
        # Calculate cumulative metrics
        total_npv = sum(year["cumulative_npv"] for year in projections["yearly_projections"])
        projections["cumulative_metrics"] = {
            "total_npv": total_npv,
            "payback_period_years": self._calculate_payback_period(projections["yearly_projections"]),
            "irr_estimate": self._estimate_irr(investment_analysis["discount_rate"], total_npv)
        }
        
        return projections
    
    def _calculate_payback_period(
        self,
        yearly_projections: List[Dict[str, Any]]
    ) -> float:
        """Calculate payback period from yearly projections."""
        cumulative_cash_flow = 0
        
        for year_data in yearly_projections:
            cumulative_cash_flow += sum(year_data["projected_cash_flows"].values())
            if cumulative_cash_flow >= 0:
                return year_data["year"]
        
        return float('inf')  # Never pays back
    
    def _estimate_irr(
        self,
        discount_rate: float,
        npv: float
    ) -> float:
        """Estimate Internal Rate of Return (simplified)."""
        # Simplified IRR estimation
        if npv > 0:
            return discount_rate * 1.1  # Assume 10% higher than discount rate
        elif npv < 0:
            return discount_rate * 0.9   # Assume 10% lower than discount rate
        else:
            return discount_rate
    
    async def _optimize_investment_timing(
        self,
        investment_analysis: Dict[str, Any],
        financial_projections: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize investment timing based on analysis."""
        optimization_result = {
            "optimal_investment_timing": "immediate",
            "investment_recommendations": [],
            "risk_assessment": {},
            "decision_factors": {}
        }
        
        # Analyze investment timing
        total_npv = financial_projections["cumulative_metrics"]["total_npv"]
        payback_period = financial_projections["cumulative_metrics"]["payback_period_years"]
        
        if total_npv > 0 and payback_period < 3:
            optimization_result["optimal_investment_timing"] = "immediate"
            optimization_result["investment_recommendations"].append("Strong positive NPV and quick payback - recommend immediate investment")
        elif total_npv > 0:
            optimization_result["optimal_investment_timing"] = "within_1_year"
            optimization_result["investment_recommendations"].append("Positive NPV - recommend investment within 1 year")
        else:
            optimization_result["optimal_investment_timing"] = "defer"
            optimization_result["investment_recommendations"].append("Negative NPV - consider deferring investment")
        
        # Risk assessment
        optimization_result["risk_assessment"] = {
            "npv_risk": "low" if total_npv > 0 else "high",
            "payback_risk": "low" if payback_period < 5 else "medium" if payback_period < 10 else "high",
            "overall_risk": "low" if total_npv > 0 and payback_period < 5 else "medium"
        }
        
        # Decision factors
        optimization_result["decision_factors"] = {
            "npv": total_npv,
            "payback_period_years": payback_period,
            "investment_horizon_years": investment_analysis["investment_horizon_years"],
            "discount_rate": investment_analysis["discount_rate"]
        }
        
        return optimization_result