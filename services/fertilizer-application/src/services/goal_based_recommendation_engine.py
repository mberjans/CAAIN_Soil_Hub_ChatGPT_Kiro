"""
Goal-Based Recommendation Engine for fertilizer application method optimization.

This module implements a comprehensive goal-based recommendation system that uses
multi-objective optimization to balance multiple farmer goals including yield
maximization, cost minimization, environmental protection, and labor efficiency.
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from uuid import uuid4
from dataclasses import dataclass
from enum import Enum
import numpy as np
from scipy.optimize import minimize
from scipy.spatial.distance import pdist, squareform

from src.models.application_models import (
    ApplicationRequest, ApplicationResponse, ApplicationMethod,
    FieldConditions, CropRequirements, FertilizerSpecification,
    ApplicationMethodType, FertilizerForm, EquipmentType
)
from src.models.application_models import EquipmentSpecification
from src.services.application_method_service import ApplicationMethodService

logger = logging.getLogger(__name__)


class OptimizationGoal(Enum):
    """Enumeration of optimization goals."""
    YIELD_MAXIMIZATION = "yield_maximization"
    COST_MINIMIZATION = "cost_minimization"
    ENVIRONMENTAL_PROTECTION = "environmental_protection"
    LABOR_EFFICIENCY = "labor_efficiency"
    EQUIPMENT_UTILIZATION = "equipment_utilization"
    NUTRIENT_EFFICIENCY = "nutrient_efficiency"


class ConstraintType(Enum):
    """Enumeration of constraint types."""
    EQUIPMENT_AVAILABILITY = "equipment_availability"
    FIELD_SIZE = "field_size"
    BUDGET_LIMIT = "budget_limit"
    LABOR_CAPACITY = "labor_capacity"
    ENVIRONMENTAL_REGULATIONS = "environmental_regulations"
    TIMING_CONSTRAINTS = "timing_constraints"


@dataclass
class GoalWeight:
    """Represents the weight/priority of an optimization goal."""
    goal: OptimizationGoal
    weight: float  # 0.0 to 1.0
    priority: int  # 1 = highest priority


@dataclass
class OptimizationConstraint:
    """Represents a constraint in the optimization problem."""
    constraint_type: ConstraintType
    constraint_value: Any
    operator: str  # "le", "ge", "eq" (less than or equal, greater than or equal, equal)
    penalty_weight: float = 1.0


@dataclass
class OptimizationResult:
    """Result of the multi-objective optimization."""
    method_scores: Dict[str, float]
    pareto_front: List[Dict[str, Any]]
    goal_achievements: Dict[OptimizationGoal, float]
    constraint_violations: List[Dict[str, Any]]
    optimization_time_ms: float
    convergence_info: Dict[str, Any]


class GoalBasedRecommendationEngine:
    """
    Comprehensive goal-based recommendation engine for fertilizer application methods.
    
    This engine implements multi-objective optimization using Pareto optimization
    and constraint satisfaction to balance multiple farmer goals while respecting
    operational constraints.
    """
    
    def __init__(self):
        """Initialize the goal-based recommendation engine."""
        self.application_service = ApplicationMethodService()
        self.goal_weights = self._initialize_default_goal_weights()
        self.constraint_handlers = self._initialize_constraint_handlers()
        self.optimization_algorithms = self._initialize_optimization_algorithms()
        
    def _initialize_default_goal_weights(self) -> Dict[OptimizationGoal, GoalWeight]:
        """Initialize default goal weights based on agricultural best practices."""
        return {
            OptimizationGoal.YIELD_MAXIMIZATION: GoalWeight(
                goal=OptimizationGoal.YIELD_MAXIMIZATION,
                weight=0.35,
                priority=1
            ),
            OptimizationGoal.COST_MINIMIZATION: GoalWeight(
                goal=OptimizationGoal.COST_MINIMIZATION,
                weight=0.25,
                priority=2
            ),
            OptimizationGoal.ENVIRONMENTAL_PROTECTION: GoalWeight(
                goal=OptimizationGoal.ENVIRONMENTAL_PROTECTION,
                weight=0.20,
                priority=3
            ),
            OptimizationGoal.LABOR_EFFICIENCY: GoalWeight(
                goal=OptimizationGoal.LABOR_EFFICIENCY,
                weight=0.15,
                priority=4
            ),
            OptimizationGoal.NUTRIENT_EFFICIENCY: GoalWeight(
                goal=OptimizationGoal.NUTRIENT_EFFICIENCY,
                weight=0.05,
                priority=5
            )
        }
    
    def _initialize_constraint_handlers(self) -> Dict[ConstraintType, callable]:
        """Initialize constraint handling functions."""
        return {
            ConstraintType.EQUIPMENT_AVAILABILITY: self._handle_equipment_constraint,
            ConstraintType.FIELD_SIZE: self._handle_field_size_constraint,
            ConstraintType.BUDGET_LIMIT: self._handle_budget_constraint,
            ConstraintType.LABOR_CAPACITY: self._handle_labor_constraint,
            ConstraintType.ENVIRONMENTAL_REGULATIONS: self._handle_environmental_constraint,
            ConstraintType.TIMING_CONSTRAINTS: self._handle_timing_constraint
        }
    
    def _initialize_optimization_algorithms(self) -> Dict[str, callable]:
        """Initialize optimization algorithms."""
        return {
            "pareto_optimization": self._pareto_optimization,
            "weighted_sum": self._weighted_sum_optimization,
            "constraint_satisfaction": self._constraint_satisfaction_optimization,
            "genetic_algorithm": self._genetic_algorithm_optimization
        }
    
    async def optimize_application_methods(
        self,
        request: ApplicationRequest,
        farmer_goals: Optional[Dict[OptimizationGoal, float]] = None,
        constraints: Optional[List[OptimizationConstraint]] = None,
        optimization_method: str = "pareto_optimization"
    ) -> OptimizationResult:
        """
        Optimize fertilizer application methods using goal-based multi-objective optimization.
        
        Args:
            request: Application request with field conditions and requirements
            farmer_goals: Custom goal weights (optional)
            constraints: List of optimization constraints (optional)
            optimization_method: Optimization algorithm to use
            
        Returns:
            OptimizationResult with optimized method recommendations
        """
        start_time = time.time()
        
        try:
            logger.info("Starting goal-based optimization for application methods")
            
            # Update goal weights if provided
            if farmer_goals:
                self._update_goal_weights(farmer_goals)
            
            # Initialize constraints if not provided
            if constraints is None:
                constraints = self._generate_default_constraints(request)
            
            # Get base method recommendations
            base_response = await self.application_service.select_application_methods(request)
            available_methods = base_response.recommended_methods
            
            if not available_methods:
                raise ValueError("No application methods available for optimization")
            
            # Calculate objective functions for each method
            objective_matrix = await self._calculate_objective_matrix(available_methods, request)
            
            # Apply constraints
            feasible_methods = await self._apply_constraints(available_methods, constraints, request)
            
            if not feasible_methods:
                logger.warning("No methods satisfy all constraints, relaxing constraints")
                feasible_methods = await self._relax_constraints(available_methods, constraints, request)
            
            # Perform optimization
            optimization_algorithm = self.optimization_algorithms.get(optimization_method)
            if not optimization_algorithm:
                raise ValueError(f"Unknown optimization method: {optimization_method}")
            
            optimization_result = await optimization_algorithm(feasible_methods, objective_matrix, constraints)
            
            # Calculate goal achievements
            goal_achievements = await self._calculate_goal_achievements(
                optimization_result.method_scores, objective_matrix
            )
            
            # Check constraint violations
            constraint_violations = await self._check_constraint_violations(
                optimization_result.method_scores, constraints, request
            )
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            result = OptimizationResult(
                method_scores=optimization_result.method_scores,
                pareto_front=optimization_result.pareto_front,
                goal_achievements=goal_achievements,
                constraint_violations=constraint_violations,
                optimization_time_ms=processing_time_ms,
                convergence_info=optimization_result.convergence_info
            )
            
            logger.info(f"Goal-based optimization completed in {processing_time_ms:.2f}ms")
            return result
            
        except Exception as e:
            logger.error(f"Error in goal-based optimization: {e}")
            raise
    
    async def _calculate_objective_matrix(
        self, 
        methods: List[ApplicationMethod], 
        request: ApplicationRequest
    ) -> np.ndarray:
        """Calculate objective function values for all methods."""
        objectives = []
        
        for method in methods:
            method_objectives = []
            
            # Yield maximization objective (higher is better)
            yield_score = await self._calculate_yield_objective(method, request)
            method_objectives.append(yield_score)
            
            # Cost minimization objective (lower is better, so we negate)
            cost_score = await self._calculate_cost_objective(method, request)
            method_objectives.append(-cost_score)  # Negate for maximization
            
            # Environmental protection objective (higher is better)
            env_score = await self._calculate_environmental_objective(method, request)
            method_objectives.append(env_score)
            
            # Labor efficiency objective (higher is better)
            labor_score = await self._calculate_labor_objective(method, request)
            method_objectives.append(labor_score)
            
            # Nutrient efficiency objective (higher is better)
            nutrient_score = await self._calculate_nutrient_objective(method, request)
            method_objectives.append(nutrient_score)
            
            objectives.append(method_objectives)
        
        return np.array(objectives)
    
    async def _calculate_yield_objective(self, method: ApplicationMethod, request: ApplicationRequest) -> float:
        """Calculate yield maximization objective."""
        # Base efficiency score
        base_score = method.efficiency_score or 0.5
        
        # Adjust based on crop requirements
        crop_requirements = request.crop_requirements
        if crop_requirements.target_yield:
            # Higher target yield increases importance of efficiency
            yield_factor = min(crop_requirements.target_yield / 200, 1.5)  # Normalize to reasonable range
            base_score *= yield_factor
        
        # Adjust based on crop type
        crop_type = crop_requirements.crop_type.lower()
        crop_efficiency_factors = {
            "corn": 1.0,
            "soybean": 0.9,
            "wheat": 0.95,
            "tomato": 1.1,
            "potato": 1.05
        }
        crop_factor = crop_efficiency_factors.get(crop_type, 1.0)
        
        return base_score * crop_factor
    
    async def _calculate_cost_objective(self, method: ApplicationMethod, request: ApplicationRequest) -> float:
        """Calculate cost minimization objective."""
        # Base cost per acre
        base_cost = method.cost_per_acre or 20.0
        
        # Adjust based on field size (economies of scale)
        field_size = request.field_conditions.field_size_acres
        if field_size > 100:
            cost_factor = 0.9  # 10% discount for large fields
        elif field_size > 50:
            cost_factor = 0.95  # 5% discount for medium fields
        else:
            cost_factor = 1.0
        
        # Adjust based on fertilizer cost
        fertilizer_cost = request.fertilizer_specification.cost_per_unit or 0.5
        fertilizer_factor = min(fertilizer_cost / 0.5, 2.0)  # Normalize fertilizer cost
        
        return base_cost * cost_factor * fertilizer_factor
    
    async def _calculate_environmental_objective(self, method: ApplicationMethod, request: ApplicationRequest) -> float:
        """Calculate environmental protection objective."""
        # Base environmental impact score
        env_impact = method.environmental_impact or "moderate"
        impact_scores = {
            "very_low": 1.0,
            "low": 0.8,
            "moderate": 0.6,
            "high": 0.4,
            "very_high": 0.2
        }
        base_score = impact_scores.get(env_impact, 0.6)
        
        # Adjust based on field conditions
        field_conditions = request.field_conditions
        
        # Slope increases environmental risk
        if field_conditions.slope_percent and field_conditions.slope_percent > 5:
            base_score *= 0.8
        
        # Poor drainage increases environmental risk
        if field_conditions.drainage_class == "poorly_drained":
            base_score *= 0.7
        
        # Irrigation availability reduces environmental risk
        if field_conditions.irrigation_available:
            base_score *= 1.1
        
        return min(base_score, 1.0)
    
    async def _calculate_labor_objective(self, method: ApplicationMethod, request: ApplicationRequest) -> float:
        """Calculate labor efficiency objective."""
        # Base labor intensity score
        labor_intensity = method.labor_requirements or "medium"
        intensity_scores = {
            "low": 1.0,
            "medium": 0.7,
            "high": 0.4
        }
        base_score = intensity_scores.get(labor_intensity, 0.7)
        
        # Adjust based on available equipment
        available_equipment = request.available_equipment
        if available_equipment:
            # More equipment options increase labor efficiency
            equipment_factor = min(len(available_equipment) / 3, 1.2)
            base_score *= equipment_factor
        
        # Adjust based on field size (larger fields may require more labor)
        field_size = request.field_conditions.field_size_acres
        if field_size > 200:
            base_score *= 0.9
        elif field_size < 10:
            base_score *= 1.1  # Small fields are more labor efficient
        
        return min(base_score, 1.0)
    
    async def _calculate_nutrient_objective(self, method: ApplicationMethod, request: ApplicationRequest) -> float:
        """Calculate nutrient efficiency objective."""
        # Base efficiency score
        base_score = method.efficiency_score or 0.5
        
        # Adjust based on fertilizer form
        fertilizer_form = request.fertilizer_specification.form
        form_efficiency = {
            FertilizerForm.LIQUID: 1.1,
            FertilizerForm.GRANULAR: 1.0,
            FertilizerForm.ORGANIC: 0.9
        }
        form_factor = form_efficiency.get(fertilizer_form, 1.0)
        
        # Adjust based on release rate
        release_rate = request.fertilizer_specification.release_rate or "medium"
        rate_efficiency = {
            "slow": 1.2,
            "medium": 1.0,
            "fast": 0.8
        }
        rate_factor = rate_efficiency.get(release_rate, 1.0)
        
        return base_score * form_factor * rate_factor
    
    async def _pareto_optimization(
        self, 
        methods: List[ApplicationMethod], 
        objective_matrix: np.ndarray,
        constraints: List[OptimizationConstraint]
    ) -> OptimizationResult:
        """Perform Pareto optimization to find non-dominated solutions."""
        logger.info("Performing Pareto optimization")
        
        # Calculate Pareto front
        pareto_indices = self._calculate_pareto_front(objective_matrix)
        pareto_front = []
        
        for idx in pareto_indices:
            method = methods[idx]
            pareto_solution = {
                "method_id": method.method_id,
                "method_type": method.method_type,
                "objectives": objective_matrix[idx].tolist(),
                "domination_count": 0,
                "crowding_distance": 0.0
            }
            pareto_front.append(pareto_solution)
        
        # Calculate crowding distance for diversity
        pareto_front = self._calculate_crowding_distance(pareto_front, objective_matrix[pareto_indices])
        
        # Sort by crowding distance (higher is better for diversity)
        pareto_front.sort(key=lambda x: x["crowding_distance"], reverse=True)
        
        # Generate method scores based on Pareto ranking
        method_scores = {}
        for i, idx in enumerate(pareto_indices):
            method = methods[idx]
            # Score based on Pareto ranking and crowding distance
            pareto_score = 1.0 / (i + 1)  # Higher rank = higher score
            crowding_score = pareto_front[i]["crowding_distance"]
            method_scores[method.method_type] = pareto_score * (1 + crowding_score)
        
        return OptimizationResult(
            method_scores=method_scores,
            pareto_front=pareto_front,
            goal_achievements={},
            constraint_violations=[],
            optimization_time_ms=0.0,
            convergence_info={"algorithm": "pareto_optimization", "solutions_found": len(pareto_front)}
        )
    
    def _calculate_pareto_front(self, objective_matrix: np.ndarray) -> List[int]:
        """Calculate Pareto front indices."""
        n_methods, n_objectives = objective_matrix.shape
        pareto_indices = []
        
        for i in range(n_methods):
            is_dominated = False
            for j in range(n_methods):
                if i != j:
                    # Check if solution j dominates solution i
                    if self._dominates(objective_matrix[j], objective_matrix[i]):
                        is_dominated = True
                        break
            
            if not is_dominated:
                pareto_indices.append(i)
        
        return pareto_indices
    
    def _dominates(self, solution_a: np.ndarray, solution_b: np.ndarray) -> bool:
        """Check if solution A dominates solution B."""
        # A dominates B if A is better in at least one objective and not worse in any
        better_in_some = np.any(solution_a > solution_b)
        worse_in_none = np.all(solution_a >= solution_b)
        return better_in_some and worse_in_none
    
    def _calculate_crowding_distance(self, pareto_front: List[Dict], objective_matrix: np.ndarray) -> List[Dict]:
        """Calculate crowding distance for Pareto front solutions."""
        n_solutions, n_objectives = objective_matrix.shape
        
        # Initialize crowding distances
        for solution in pareto_front:
            solution["crowding_distance"] = 0.0
        
        # Calculate crowding distance for each objective
        for obj_idx in range(n_objectives):
            # Sort solutions by this objective
            sorted_indices = np.argsort(objective_matrix[:, obj_idx])
            
            # Set boundary solutions to infinite distance
            pareto_front[sorted_indices[0]]["crowding_distance"] = float('inf')
            pareto_front[sorted_indices[-1]]["crowding_distance"] = float('inf')
            
            # Calculate distance for intermediate solutions
            obj_range = objective_matrix[sorted_indices[-1], obj_idx] - objective_matrix[sorted_indices[0], obj_idx]
            if obj_range > 0:
                for i in range(1, len(sorted_indices) - 1):
                    distance = (objective_matrix[sorted_indices[i + 1], obj_idx] - 
                              objective_matrix[sorted_indices[i - 1], obj_idx]) / obj_range
                    pareto_front[sorted_indices[i]]["crowding_distance"] += distance
        
        return pareto_front
    
    async def _weighted_sum_optimization(
        self, 
        methods: List[ApplicationMethod], 
        objective_matrix: np.ndarray,
        constraints: List[OptimizationConstraint]
    ) -> OptimizationResult:
        """Perform weighted sum optimization."""
        logger.info("Performing weighted sum optimization")
        
        # Normalize objectives to [0, 1] range
        normalized_objectives = self._normalize_objectives(objective_matrix)
        
        # Calculate weighted scores
        method_scores = {}
        goal_weights = [weight.weight for weight in self.goal_weights.values()]
        
        for i, method in enumerate(methods):
            weighted_score = np.dot(normalized_objectives[i], goal_weights)
            method_scores[method.method_type] = weighted_score
        
        return OptimizationResult(
            method_scores=method_scores,
            pareto_front=[],
            goal_achievements={},
            constraint_violations=[],
            optimization_time_ms=0.0,
            convergence_info={"algorithm": "weighted_sum", "solutions_evaluated": len(methods)}
        )
    
    def _normalize_objectives(self, objective_matrix: np.ndarray) -> np.ndarray:
        """Normalize objectives to [0, 1] range."""
        normalized = np.zeros_like(objective_matrix)
        
        for j in range(objective_matrix.shape[1]):
            col = objective_matrix[:, j]
            min_val, max_val = np.min(col), np.max(col)
            
            if max_val > min_val:
                normalized[:, j] = (col - min_val) / (max_val - min_val)
            else:
                normalized[:, j] = 0.5  # All values are the same
        
        return normalized
    
    async def _constraint_satisfaction_optimization(
        self, 
        methods: List[ApplicationMethod], 
        objective_matrix: np.ndarray,
        constraints: List[OptimizationConstraint]
    ) -> OptimizationResult:
        """Perform constraint satisfaction optimization."""
        logger.info("Performing constraint satisfaction optimization")
        
        # Filter methods that satisfy all constraints
        feasible_methods = []
        constraint_violations = []
        
        for i, method in enumerate(methods):
            method_violations = []
            is_feasible = True
            
            for constraint in constraints:
                handler = self.constraint_handlers.get(constraint.constraint_type)
                if handler:
                    violation = await handler(method, constraint)
                    if violation:
                        method_violations.append(violation)
                        is_feasible = False
            
            if is_feasible:
                feasible_methods.append((i, method))
            else:
                constraint_violations.extend(method_violations)
        
        # If no methods satisfy all constraints, find least violated
        if not feasible_methods:
            logger.warning("No methods satisfy all constraints, finding least violated")
            violation_counts = {}
            for i, method in enumerate(methods):
                count = 0
                for constraint in constraints:
                    handler = self.constraint_handlers.get(constraint.constraint_type)
                    if handler:
                        violation = await handler(method, constraint)
                        if violation:
                            count += 1
                violation_counts[i] = count
            
            # Select methods with minimum violations
            min_violations = min(violation_counts.values())
            feasible_methods = [(i, methods[i]) for i, count in violation_counts.items() 
                              if count == min_violations]
        
        # Score feasible methods
        method_scores = {}
        for i, method in feasible_methods:
            # Use weighted sum of objectives for feasible methods
            normalized_objectives = self._normalize_objectives(objective_matrix)
            goal_weights = [weight.weight for weight in self.goal_weights.values()]
            weighted_score = np.dot(normalized_objectives[i], goal_weights)
            method_scores[method.method_type] = weighted_score
        
        return OptimizationResult(
            method_scores=method_scores,
            pareto_front=[],
            goal_achievements={},
            constraint_violations=constraint_violations,
            optimization_time_ms=0.0,
            convergence_info={"algorithm": "constraint_satisfaction", "feasible_solutions": len(feasible_methods)}
        )
    
    async def _genetic_algorithm_optimization(
        self, 
        methods: List[ApplicationMethod], 
        objective_matrix: np.ndarray,
        constraints: List[OptimizationConstraint]
    ) -> OptimizationResult:
        """Perform genetic algorithm optimization (simplified implementation)."""
        logger.info("Performing genetic algorithm optimization")
        
        # Simplified GA implementation
        population_size = min(20, len(methods))
        generations = 10
        
        # Initialize population
        population = np.random.choice(len(methods), size=population_size, replace=True)
        
        best_scores = {}
        
        for generation in range(generations):
            # Evaluate fitness
            fitness_scores = []
            for individual in population:
                method_idx = individual
                method = methods[method_idx]
                
                # Calculate fitness (weighted sum of objectives)
                normalized_objectives = self._normalize_objectives(objective_matrix)
                goal_weights = [weight.weight for weight in self.goal_weights.values()]
                fitness = np.dot(normalized_objectives[method_idx], goal_weights)
                fitness_scores.append(fitness)
            
            # Select best individuals
            sorted_indices = np.argsort(fitness_scores)[::-1]  # Descending order
            elite_size = population_size // 2
            
            # Keep elite
            elite = population[sorted_indices[:elite_size]]
            
            # Generate new population through crossover and mutation
            new_population = list(elite)
            
            while len(new_population) < population_size:
                # Simple crossover: select random parent from elite
                parent = np.random.choice(elite)
                # Simple mutation: randomly select a method
                offspring = np.random.choice(len(methods))
                new_population.append(offspring)
            
            population = np.array(new_population)
        
        # Calculate final scores
        for i, method in enumerate(methods):
            if i in population:
                normalized_objectives = self._normalize_objectives(objective_matrix)
                goal_weights = [weight.weight for weight in self.goal_weights.values()]
                score = np.dot(normalized_objectives[i], goal_weights)
                method_scores[method.method_type] = score
        
        return OptimizationResult(
            method_scores=method_scores,
            pareto_front=[],
            goal_achievements={},
            constraint_violations=[],
            optimization_time_ms=0.0,
            convergence_info={"algorithm": "genetic_algorithm", "generations": generations, "population_size": population_size}
        )
    
    def _update_goal_weights(self, farmer_goals: Dict[OptimizationGoal, float]):
        """Update goal weights based on farmer preferences."""
        total_weight = sum(farmer_goals.values())
        
        for goal, weight in farmer_goals.items():
            normalized_weight = weight / total_weight if total_weight > 0 else 1.0 / len(farmer_goals)
            self.goal_weights[goal] = GoalWeight(
                goal=goal,
                weight=normalized_weight,
                priority=self.goal_weights[goal].priority
            )
    
    def _generate_default_constraints(self, request: ApplicationRequest) -> List[OptimizationConstraint]:
        """Generate default constraints based on request."""
        constraints = []
        
        # Equipment availability constraint
        if request.available_equipment:
            constraints.append(OptimizationConstraint(
                constraint_type=ConstraintType.EQUIPMENT_AVAILABILITY,
                constraint_value=request.available_equipment,
                operator="eq"
            ))
        
        # Field size constraint
        field_size = request.field_conditions.field_size_acres
        constraints.append(OptimizationConstraint(
            constraint_type=ConstraintType.FIELD_SIZE,
            constraint_value=field_size,
            operator="le"
        ))
        
        # Budget constraint (default $50/acre)
        constraints.append(OptimizationConstraint(
            constraint_type=ConstraintType.BUDGET_LIMIT,
            constraint_value=50.0,
            operator="le"
        ))
        
        return constraints
    
    async def _apply_constraints(
        self, 
        methods: List[ApplicationMethod], 
        constraints: List[OptimizationConstraint],
        request: ApplicationRequest
    ) -> List[ApplicationMethod]:
        """Apply constraints to filter feasible methods."""
        feasible_methods = []
        
        for method in methods:
            is_feasible = True
            
            for constraint in constraints:
                handler = self.constraint_handlers.get(constraint.constraint_type)
                if handler:
                    violation = await handler(method, constraint)
                    if violation:
                        is_feasible = False
                        break
            
            if is_feasible:
                feasible_methods.append(method)
        
        return feasible_methods
    
    async def _relax_constraints(
        self, 
        methods: List[ApplicationMethod], 
        constraints: List[OptimizationConstraint],
        request: ApplicationRequest
    ) -> List[ApplicationMethod]:
        """Relax constraints to find feasible solutions."""
        # Start with all methods and gradually relax constraints
        relaxed_methods = methods.copy()
        
        # Sort constraints by penalty weight (relax high-penalty constraints first)
        sorted_constraints = sorted(constraints, key=lambda c: c.penalty_weight, reverse=True)
        
        for constraint in sorted_constraints:
            if not relaxed_methods:
                break
            
            # Try removing this constraint
            temp_methods = []
            for method in relaxed_methods:
                is_feasible = True
                for other_constraint in constraints:
                    if other_constraint != constraint:
                        handler = self.constraint_handlers.get(other_constraint.constraint_type)
                        if handler:
                            violation = await handler(method, other_constraint)
                            if violation:
                                is_feasible = False
                                break
                
                if is_feasible:
                    temp_methods.append(method)
            
            if temp_methods:
                relaxed_methods = temp_methods
                logger.info(f"Relaxed constraint {constraint.constraint_type}, {len(relaxed_methods)} methods feasible")
        
        return relaxed_methods
    
    # Constraint handlers
    async def _handle_equipment_constraint(self, method: ApplicationMethod, constraint: OptimizationConstraint) -> Optional[Dict[str, Any]]:
        """Handle equipment availability constraint."""
        required_equipment = method.recommended_equipment
        available_equipment = constraint.constraint_value
        
        if required_equipment and available_equipment:
            equipment_type = required_equipment.equipment_type
            available_types = [eq.equipment_type for eq in available_equipment]
            
            if equipment_type not in available_types:
                return {
                    "constraint_type": constraint.constraint_type,
                    "violation": f"Required equipment {equipment_type} not available",
                    "penalty": constraint.penalty_weight
                }
        
        return None
    
    async def _handle_field_size_constraint(self, method: ApplicationMethod, constraint: OptimizationConstraint) -> Optional[Dict[str, Any]]:
        """Handle field size constraint."""
        # This would need to be implemented based on method database field size ranges
        # For now, return None (no violation)
        return None
    
    async def _handle_budget_constraint(self, method: ApplicationMethod, constraint: OptimizationConstraint) -> Optional[Dict[str, Any]]:
        """Handle budget constraint."""
        method_cost = method.cost_per_acre or 0
        budget_limit = constraint.constraint_value
        
        if method_cost > budget_limit:
            return {
                "constraint_type": constraint.constraint_type,
                "violation": f"Method cost ${method_cost}/acre exceeds budget ${budget_limit}/acre",
                "penalty": constraint.penalty_weight
            }
        
        return None
    
    async def _handle_labor_constraint(self, method: ApplicationMethod, constraint: OptimizationConstraint) -> Optional[Dict[str, Any]]:
        """Handle labor capacity constraint."""
        # This would need labor capacity data
        # For now, return None (no violation)
        return None
    
    async def _handle_environmental_constraint(self, method: ApplicationMethod, constraint: OptimizationConstraint) -> Optional[Dict[str, Any]]:
        """Handle environmental regulations constraint."""
        # This would need environmental regulation data
        # For now, return None (no violation)
        return None
    
    async def _handle_timing_constraint(self, method: ApplicationMethod, constraint: OptimizationConstraint) -> Optional[Dict[str, Any]]:
        """Handle timing constraints."""
        # This would need timing constraint data
        # For now, return None (no violation)
        return None
    
    async def _calculate_goal_achievements(
        self, 
        method_scores: Dict[str, float], 
        objective_matrix: np.ndarray
    ) -> Dict[OptimizationGoal, float]:
        """Calculate how well each goal is achieved."""
        goal_achievements = {}
        
        # This would calculate actual goal achievement percentages
        # For now, return placeholder values
        for goal in OptimizationGoal:
            goal_achievements[goal] = 0.8  # 80% achievement placeholder
        
        return goal_achievements
    
    async def _check_constraint_violations(
        self, 
        method_scores: Dict[str, float], 
        constraints: List[OptimizationConstraint],
        request: ApplicationRequest
    ) -> List[Dict[str, Any]]:
        """Check for constraint violations in the final solution."""
        violations = []
        
        # This would check actual constraint violations
        # For now, return empty list
        
        return violations