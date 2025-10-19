"""
Multi-Objective Optimizer for Fertilizer Timing

This module implements a multi-objective optimization framework for fertilizer
timing that balances competing objectives using Pareto optimization. It generates
multiple non-dominated solutions representing different trade-offs between
objectives.

Objectives:
    1. Maximize yield potential
    2. Minimize application costs
    3. Minimize environmental impact
    4. Minimize risk (weather, timing, operational)

Approach:
    - NSGA-II inspired algorithm for Pareto front discovery
    - Weighted sum methods for preference-based optimization
    - Constraint handling for practical applicability
"""

import logging
import numpy as np
from datetime import date, timedelta
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
import copy

from ..models.timing_optimization_models import (
    TimingOptimizationRequest,
    WeatherWindow,
    CropGrowthStage,
    ApplicationMethod,
    WeatherCondition
)

logger = logging.getLogger(__name__)


@dataclass
class ObjectiveValues:
    """Objective function values for a solution."""
    yield_score: float
    cost_score: float
    environmental_score: float
    risk_score: float

    def dominates(self, other: 'ObjectiveValues') -> bool:
        """Check if this solution Pareto-dominates another."""
        # For maximization objectives
        better_in_any = False
        worse_in_any = False

        if self.yield_score > other.yield_score:
            better_in_any = True
        elif self.yield_score < other.yield_score:
            worse_in_any = True

        if self.cost_score > other.cost_score:
            better_in_any = True
        elif self.cost_score < other.cost_score:
            worse_in_any = True

        if self.environmental_score > other.environmental_score:
            better_in_any = True
        elif self.environmental_score < other.environmental_score:
            worse_in_any = True

        if self.risk_score > other.risk_score:
            better_in_any = True
        elif self.risk_score < other.risk_score:
            worse_in_any = True

        return better_in_any and not worse_in_any

    def to_array(self) -> np.ndarray:
        """Convert to numpy array."""
        return np.array([self.yield_score, self.cost_score, self.environmental_score, self.risk_score])


@dataclass
class Solution:
    """Represents a complete solution with timing schedule and objectives."""
    schedule: List[Tuple[date, str, float, ApplicationMethod]]
    objectives: ObjectiveValues
    crowding_distance: float = 0.0
    rank: int = 0
    is_feasible: bool = True

    def __repr__(self):
        return (f"Solution(rank={self.rank}, "
                f"yield={self.objectives.yield_score:.2f}, "
                f"cost={self.objectives.cost_score:.2f}, "
                f"env={self.objectives.environmental_score:.2f}, "
                f"risk={self.objectives.risk_score:.2f})")


@dataclass
class MOResult:
    """Result from multi-objective optimization."""
    pareto_front: List[Solution]
    all_solutions: List[Solution]
    recommended_solution: Solution
    trade_off_analysis: Dict[str, Any]
    objective_ranges: Dict[str, Tuple[float, float]]
    preference_weights: Dict[str, float]


class MultiObjectiveOptimizer:
    """
    Multi-objective optimizer for fertilizer timing.

    This optimizer uses Pareto optimization to find a set of non-dominated
    solutions representing different trade-offs between yield, cost,
    environmental impact, and risk objectives.
    """

    def __init__(
        self,
        population_size: int = 100,
        max_generations: int = 150,
        crossover_rate: float = 0.9,
        mutation_rate: float = 0.1
    ):
        """
        Initialize the multi-objective optimizer.

        Args:
            population_size: Number of solutions in population
            max_generations: Maximum number of generations
            crossover_rate: Probability of crossover
            mutation_rate: Probability of mutation
        """
        self.population_size = population_size
        self.max_generations = max_generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate

    def optimize(
        self,
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow],
        crop_stages: Dict[date, CropGrowthStage],
        preference_weights: Optional[Dict[str, float]] = None
    ) -> MOResult:
        """
        Optimize fertilizer timing with multi-objective approach.

        Args:
            request: Optimization request with field and crop data
            weather_windows: Available weather windows for application
            crop_stages: Crop growth stages by date
            preference_weights: Optional weights for objectives

        Returns:
            MOResult with Pareto front and recommended solution
        """
        logger.info(f"Starting multi-objective optimization with {self.population_size} solutions")

        # Default preference weights
        if preference_weights is None:
            preference_weights = {
                "yield": 0.40,
                "cost": 0.25,
                "environment": 0.20,
                "risk": 0.15
            }

        # Initialize population
        population = self._initialize_population(request, weather_windows, crop_stages)

        # Evaluate objectives for initial population
        for solution in population:
            solution.objectives = self._evaluate_objectives(solution, request, weather_windows, crop_stages)

        # Evolution
        for generation in range(self.max_generations):
            # Non-dominated sorting
            fronts = self._non_dominated_sort(population)

            # Calculate crowding distance
            for front in fronts:
                self._calculate_crowding_distance(front)

            # Log progress
            if generation % 25 == 0:
                pareto_size = len(fronts[0]) if fronts else 0
                logger.debug(f"Generation {generation}: Pareto front size = {pareto_size}")

            # Create next generation
            offspring = []

            while len(offspring) < self.population_size:
                # Tournament selection
                parent1 = self._tournament_selection(population)
                parent2 = self._tournament_selection(population)

                # Crossover
                if np.random.random() < self.crossover_rate:
                    child1, child2 = self._crossover(parent1, parent2, request)
                else:
                    child1, child2 = copy.deepcopy(parent1), copy.deepcopy(parent2)

                # Mutation
                if np.random.random() < self.mutation_rate:
                    child1 = self._mutate(child1, request, weather_windows, crop_stages)
                if np.random.random() < self.mutation_rate:
                    child2 = self._mutate(child2, request, weather_windows, crop_stages)

                # Evaluate objectives
                child1.objectives = self._evaluate_objectives(child1, request, weather_windows, crop_stages)
                child2.objectives = self._evaluate_objectives(child2, request, weather_windows, crop_stages)

                offspring.append(child1)
                if len(offspring) < self.population_size:
                    offspring.append(child2)

            # Combine parent and offspring populations
            combined = population + offspring

            # Select next generation
            population = self._select_next_generation(combined, self.population_size)

        # Final non-dominated sorting
        fronts = self._non_dominated_sort(population)
        pareto_front = fronts[0] if fronts else []

        # Select recommended solution based on preferences
        recommended = self._select_preferred_solution(pareto_front, preference_weights)

        # Analyze trade-offs
        trade_off_analysis = self._analyze_trade_offs(pareto_front)

        # Calculate objective ranges
        objective_ranges = self._calculate_objective_ranges(population)

        logger.info(f"Multi-objective optimization complete. Pareto front size: {len(pareto_front)}")

        return MOResult(
            pareto_front=pareto_front,
            all_solutions=population,
            recommended_solution=recommended,
            trade_off_analysis=trade_off_analysis,
            objective_ranges=objective_ranges,
            preference_weights=preference_weights
        )

    def _initialize_population(
        self,
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow],
        crop_stages: Dict[date, CropGrowthStage]
    ) -> List[Solution]:
        """Initialize random population of solutions."""
        population = []

        for _ in range(self.population_size):
            schedule = self._generate_random_schedule(request, weather_windows, crop_stages)
            solution = Solution(schedule=schedule, objectives=ObjectiveValues(0, 0, 0, 0))
            population.append(solution)

        return population

    def _generate_random_schedule(
        self,
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow],
        crop_stages: Dict[date, CropGrowthStage]
    ) -> List[Tuple[date, str, float, ApplicationMethod]]:
        """Generate a random fertilizer application schedule."""
        import random

        schedule = []

        for fertilizer_type, total_amount in request.fertilizer_requirements.items():
            # Random number of splits
            num_splits = random.randint(1, 3) if request.split_application_allowed else 1

            # Generate random dates
            dates = []
            start_day = 0
            end_day = min(120, request.optimization_horizon_days)

            for _ in range(num_splits):
                offset = random.randint(start_day, end_day)
                app_date = request.planting_date + timedelta(days=offset)
                dates.append(app_date)

            dates.sort()

            # Distribute amount
            if num_splits == 1:
                amounts = [total_amount]
            else:
                amounts = []
                remaining = total_amount
                for i in range(num_splits - 1):
                    amount = remaining * random.uniform(0.2, 0.5)
                    amounts.append(amount)
                    remaining -= amount
                amounts.append(remaining)

            # Create schedule entries
            for app_date, amount in zip(dates, amounts):
                method = random.choice(request.application_methods)
                schedule.append((app_date, fertilizer_type, amount, method))

        return schedule

    def _evaluate_objectives(
        self,
        solution: Solution,
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow],
        crop_stages: Dict[date, CropGrowthStage]
    ) -> ObjectiveValues:
        """Evaluate all objectives for a solution."""
        yield_score = self._evaluate_yield_objective(solution, request, crop_stages)
        cost_score = self._evaluate_cost_objective(solution, request)
        env_score = self._evaluate_environmental_objective(solution, request, weather_windows)
        risk_score = self._evaluate_risk_objective(solution, request, weather_windows)

        return ObjectiveValues(yield_score, cost_score, env_score, risk_score)

    def _evaluate_yield_objective(
        self,
        solution: Solution,
        request: TimingOptimizationRequest,
        crop_stages: Dict[date, CropGrowthStage]
    ) -> float:
        """Evaluate yield maximization objective (0-100)."""
        total_score = 0.0

        for app_date, fertilizer_type, amount, method in solution.schedule:
            # Get crop stage
            crop_stage = self._get_crop_stage_for_date(app_date, crop_stages)

            # Stage-specific response
            stage_scores = {
                CropGrowthStage.PLANTING: 0.95,
                CropGrowthStage.EMERGENCE: 0.90,
                CropGrowthStage.V4: 1.00,
                CropGrowthStage.V6: 0.95,
                CropGrowthStage.V8: 0.85,
                CropGrowthStage.VT: 0.70,
                CropGrowthStage.R1: 0.60
            }
            stage_score = stage_scores.get(crop_stage, 0.5)

            # Method efficiency
            method_efficiency = {
                ApplicationMethod.BROADCAST_INCORPORATED: 0.95,
                ApplicationMethod.BANDED: 0.90,
                ApplicationMethod.SIDE_DRESS: 0.92,
                ApplicationMethod.FERTIGATION: 0.95,
                ApplicationMethod.BROADCAST: 0.85,
                ApplicationMethod.FOLIAR: 0.80,
                ApplicationMethod.INJECTION: 0.93
            }
            method_score = method_efficiency.get(method, 0.85)

            app_score = 100.0 * stage_score * method_score * (amount / 100.0)
            total_score += app_score

        return total_score / max(1, len(solution.schedule))

    def _evaluate_cost_objective(
        self,
        solution: Solution,
        request: TimingOptimizationRequest
    ) -> float:
        """Evaluate cost minimization objective (0-100, higher is better)."""
        base_costs = {
            "nitrogen": 0.50,
            "phosphorus": 0.80,
            "potassium": 0.60,
            "complete": 0.70
        }

        total_cost = 0.0

        for app_date, fertilizer_type, amount, method in solution.schedule:
            # Fertilizer cost
            cost_per_lb = base_costs.get(fertilizer_type.lower(), 0.60)
            total_cost += amount * cost_per_lb

            # Application cost
            application_costs = {
                ApplicationMethod.BROADCAST: 8.0,
                ApplicationMethod.BROADCAST_INCORPORATED: 12.0,
                ApplicationMethod.BANDED: 10.0,
                ApplicationMethod.SIDE_DRESS: 15.0,
                ApplicationMethod.FOLIAR: 20.0,
                ApplicationMethod.FERTIGATION: 18.0,
                ApplicationMethod.INJECTION: 22.0
            }
            total_cost += application_costs.get(method, 10.0)

        # Normalize and invert (lower cost = higher score)
        cost_score = 100.0 * (1.0 - min(1.0, total_cost / 400.0))

        return max(0.0, cost_score)

    def _evaluate_environmental_objective(
        self,
        solution: Solution,
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow]
    ) -> float:
        """Evaluate environmental impact minimization objective (0-100)."""
        total_score = 0.0

        for app_date, fertilizer_type, amount, method in solution.schedule:
            weather = self._get_weather_for_date(app_date, weather_windows)

            if weather:
                # Weather suitability
                condition_scores = {
                    WeatherCondition.OPTIMAL: 1.0,
                    WeatherCondition.ACCEPTABLE: 0.8,
                    WeatherCondition.MARGINAL: 0.5,
                    WeatherCondition.POOR: 0.2,
                    WeatherCondition.UNACCEPTABLE: 0.0
                }
                weather_score = condition_scores.get(weather.condition, 0.5)

                # Soil moisture (optimal 0.4-0.7)
                moisture_score = 1.0 if 0.4 <= weather.soil_moisture <= 0.7 else 0.6

                # Precipitation risk
                precip_score = 1.0 - weather.precipitation_probability

                # Slope factor (higher slope = higher runoff risk)
                slope_factor = max(0.5, 1.0 - request.slope_percent / 20.0)

                app_score = 100.0 * weather_score * moisture_score * precip_score * slope_factor
            else:
                app_score = 50.0

            total_score += app_score

        return total_score / max(1, len(solution.schedule))

    def _evaluate_risk_objective(
        self,
        solution: Solution,
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow]
    ) -> float:
        """Evaluate risk minimization objective (0-100)."""
        # Split application bonus
        fert_counts = {}
        for _, fertilizer_type, _, _ in solution.schedule:
            fert_counts[fertilizer_type] = fert_counts.get(fertilizer_type, 0) + 1

        split_score = sum(20.0 if count >= 2 else 0.0 for count in fert_counts.values())

        # Temporal diversification
        if len(solution.schedule) > 1:
            dates = sorted([d for d, _, _, _ in solution.schedule])
            spread_days = (dates[-1] - dates[0]).days
            spread_score = min(30.0, spread_days / 2.0)
        else:
            spread_score = 0.0

        # Early application bonus (less weather uncertainty)
        early_score = 0.0
        for app_date, _, _, _ in solution.schedule:
            days_from_planting = (app_date - request.planting_date).days
            if days_from_planting <= 30:
                early_score += 15.0
            elif days_from_planting <= 60:
                early_score += 5.0

        early_score /= max(1, len(solution.schedule))

        # Weather certainty
        certainty_score = 0.0
        for app_date, _, _, _ in solution.schedule:
            weather = self._get_weather_for_date(app_date, weather_windows)
            if weather and weather.condition in [WeatherCondition.OPTIMAL, WeatherCondition.ACCEPTABLE]:
                certainty_score += 10.0

        certainty_score /= max(1, len(solution.schedule))

        total_risk_score = split_score + spread_score + early_score + certainty_score

        return min(100.0, total_risk_score)

    def _non_dominated_sort(self, population: List[Solution]) -> List[List[Solution]]:
        """Perform non-dominated sorting (NSGA-II style)."""
        fronts = [[]]
        domination_count = {}
        dominated_solutions = {}

        # Initialize
        for solution in population:
            domination_count[id(solution)] = 0
            dominated_solutions[id(solution)] = []

        # Calculate domination
        for i, p in enumerate(population):
            for j, q in enumerate(population):
                if i != j:
                    if p.objectives.dominates(q.objectives):
                        dominated_solutions[id(p)].append(q)
                    elif q.objectives.dominates(p.objectives):
                        domination_count[id(p)] += 1

            # First front
            if domination_count[id(p)] == 0:
                p.rank = 0
                fronts[0].append(p)

        # Subsequent fronts
        i = 0
        while fronts[i]:
            next_front = []
            for p in fronts[i]:
                for q in dominated_solutions[id(p)]:
                    domination_count[id(q)] -= 1
                    if domination_count[id(q)] == 0:
                        q.rank = i + 1
                        next_front.append(q)

            i += 1
            if next_front:
                fronts.append(next_front)

        return fronts[:-1] if fronts[-1] == [] else fronts

    def _calculate_crowding_distance(self, front: List[Solution]) -> None:
        """Calculate crowding distance for solutions in a front."""
        if len(front) == 0:
            return

        # Initialize
        for solution in front:
            solution.crowding_distance = 0.0

        # For each objective
        for obj_index in range(4):
            # Sort by objective
            if obj_index == 0:
                front.sort(key=lambda s: s.objectives.yield_score)
            elif obj_index == 1:
                front.sort(key=lambda s: s.objectives.cost_score)
            elif obj_index == 2:
                front.sort(key=lambda s: s.objectives.environmental_score)
            else:
                front.sort(key=lambda s: s.objectives.risk_score)

            # Boundary solutions have infinite distance
            front[0].crowding_distance = float('inf')
            front[-1].crowding_distance = float('inf')

            # Get objective range
            obj_array = [s.objectives.to_array()[obj_index] for s in front]
            obj_range = max(obj_array) - min(obj_array)

            if obj_range == 0:
                continue

            # Calculate crowding distance
            for i in range(1, len(front) - 1):
                if front[i].crowding_distance != float('inf'):
                    distance = (obj_array[i + 1] - obj_array[i - 1]) / obj_range
                    front[i].crowding_distance += distance

    def _tournament_selection(self, population: List[Solution]) -> Solution:
        """Binary tournament selection based on rank and crowding distance."""
        import random

        candidate1 = random.choice(population)
        candidate2 = random.choice(population)

        # Compare ranks
        if candidate1.rank < candidate2.rank:
            return candidate1
        elif candidate1.rank > candidate2.rank:
            return candidate2
        else:
            # Same rank, compare crowding distance
            if candidate1.crowding_distance > candidate2.crowding_distance:
                return candidate1
            else:
                return candidate2

    def _crossover(
        self,
        parent1: Solution,
        parent2: Solution,
        request: TimingOptimizationRequest
    ) -> Tuple[Solution, Solution]:
        """Perform crossover between two parent solutions."""
        import random

        # Simple schedule crossover
        schedule1 = parent1.schedule.copy()
        schedule2 = parent2.schedule.copy()

        if len(schedule1) > 1 and len(schedule2) > 1:
            point = random.randint(1, min(len(schedule1), len(schedule2)) - 1)
            new_schedule1 = schedule1[:point] + schedule2[point:]
            new_schedule2 = schedule2[:point] + schedule1[point:]
        else:
            new_schedule1 = schedule1
            new_schedule2 = schedule2

        child1 = Solution(schedule=new_schedule1, objectives=ObjectiveValues(0, 0, 0, 0))
        child2 = Solution(schedule=new_schedule2, objectives=ObjectiveValues(0, 0, 0, 0))

        return child1, child2

    def _mutate(
        self,
        solution: Solution,
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow],
        crop_stages: Dict[date, CropGrowthStage]
    ) -> Solution:
        """Apply mutation to a solution."""
        import random

        mutated_schedule = []

        for app_date, fertilizer_type, amount, method in solution.schedule:
            if random.random() < 0.3:
                # Mutate date
                offset = random.randint(-7, 7)
                new_date = app_date + timedelta(days=offset)
                new_date = max(request.planting_date, new_date)
                new_date = min(request.planting_date + timedelta(days=120), new_date)

                # Mutate amount
                amount_mult = random.uniform(0.8, 1.2)
                new_amount = amount * amount_mult

                mutated_schedule.append((new_date, fertilizer_type, new_amount, method))
            else:
                mutated_schedule.append((app_date, fertilizer_type, amount, method))

        return Solution(schedule=mutated_schedule, objectives=ObjectiveValues(0, 0, 0, 0))

    def _select_next_generation(self, population: List[Solution], size: int) -> List[Solution]:
        """Select next generation based on rank and crowding distance."""
        fronts = self._non_dominated_sort(population)

        for front in fronts:
            self._calculate_crowding_distance(front)

        next_gen = []

        for front in fronts:
            if len(next_gen) + len(front) <= size:
                next_gen.extend(front)
            else:
                # Sort by crowding distance
                front.sort(key=lambda s: s.crowding_distance, reverse=True)
                remaining = size - len(next_gen)
                next_gen.extend(front[:remaining])
                break

        return next_gen

    def _select_preferred_solution(
        self,
        pareto_front: List[Solution],
        weights: Dict[str, float]
    ) -> Solution:
        """Select solution from Pareto front based on preference weights."""
        if not pareto_front:
            return Solution(schedule=[], objectives=ObjectiveValues(0, 0, 0, 0))

        best_solution = None
        best_score = -float('inf')

        for solution in pareto_front:
            weighted_score = (
                weights["yield"] * solution.objectives.yield_score +
                weights["cost"] * solution.objectives.cost_score +
                weights["environment"] * solution.objectives.environmental_score +
                weights["risk"] * solution.objectives.risk_score
            )

            if weighted_score > best_score:
                best_score = weighted_score
                best_solution = solution

        return best_solution

    def _analyze_trade_offs(self, pareto_front: List[Solution]) -> Dict[str, Any]:
        """Analyze trade-offs in the Pareto front."""
        if not pareto_front:
            return {}

        yield_scores = [s.objectives.yield_score for s in pareto_front]
        cost_scores = [s.objectives.cost_score for s in pareto_front]
        env_scores = [s.objectives.environmental_score for s in pareto_front]
        risk_scores = [s.objectives.risk_score for s in pareto_front]

        return {
            "pareto_size": len(pareto_front),
            "yield_range": (min(yield_scores), max(yield_scores)),
            "cost_range": (min(cost_scores), max(cost_scores)),
            "environmental_range": (min(env_scores), max(env_scores)),
            "risk_range": (min(risk_scores), max(risk_scores)),
            "diversity": np.std(yield_scores) + np.std(cost_scores) + np.std(env_scores) + np.std(risk_scores)
        }

    def _calculate_objective_ranges(self, population: List[Solution]) -> Dict[str, Tuple[float, float]]:
        """Calculate min-max ranges for each objective."""
        yield_scores = [s.objectives.yield_score for s in population]
        cost_scores = [s.objectives.cost_score for s in population]
        env_scores = [s.objectives.environmental_score for s in population]
        risk_scores = [s.objectives.risk_score for s in population]

        return {
            "yield": (min(yield_scores), max(yield_scores)),
            "cost": (min(cost_scores), max(cost_scores)),
            "environment": (min(env_scores), max(env_scores)),
            "risk": (min(risk_scores), max(risk_scores))
        }

    def _get_crop_stage_for_date(
        self,
        target_date: date,
        crop_stages: Dict[date, CropGrowthStage]
    ) -> CropGrowthStage:
        """Get crop growth stage for a specific date."""
        closest_stage = CropGrowthStage.PLANTING
        min_diff = float('inf')

        for stage_date, stage in crop_stages.items():
            diff = abs((target_date - stage_date).days)
            if diff < min_diff:
                min_diff = diff
                closest_stage = stage

        return closest_stage

    def _get_weather_for_date(
        self,
        target_date: date,
        weather_windows: List[WeatherWindow]
    ) -> Optional[WeatherWindow]:
        """Get weather window for specific date."""
        for window in weather_windows:
            if window.start_date <= target_date <= window.end_date:
                return window
        return None
