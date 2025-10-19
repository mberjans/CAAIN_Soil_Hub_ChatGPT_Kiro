"""
Genetic Algorithm Optimizer for Fertilizer Timing

This module implements a genetic algorithm for optimizing fertilizer application
timing using evolutionary computation principles. The GA evolves a population of
timing schedules to find near-optimal solutions through selection, crossover,
and mutation operations.

Mathematical Formulation:
    Fitness(schedule) = w1*Yield + w2*Cost + w3*Environment + w4*Risk

    Evolution Process:
    1. Selection: Tournament or roulette wheel
    2. Crossover: Single-point or multi-point
    3. Mutation: Random date/amount adjustment
    4. Elitism: Preserve best solutions
"""

import logging
import numpy as np
from datetime import date, timedelta
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
import random

from ..models.timing_optimization_models import (
    TimingOptimizationRequest,
    WeatherWindow,
    CropGrowthStage,
    ApplicationMethod,
    WeatherCondition
)

logger = logging.getLogger(__name__)


@dataclass
class ApplicationGene:
    """Represents a single application (gene) in the schedule (chromosome)."""
    fertilizer_type: str
    application_date: date
    amount: float
    method: ApplicationMethod

    def __repr__(self):
        return f"{self.fertilizer_type}: {self.amount} lbs on {self.application_date}"


@dataclass
class Chromosome:
    """Represents a complete fertilizer application schedule (chromosome)."""
    genes: List[ApplicationGene]
    fitness: float = 0.0
    objectives: Dict[str, float] = None

    def __post_init__(self):
        if self.objectives is None:
            self.objectives = {}

    def __repr__(self):
        return f"Chromosome(fitness={self.fitness:.2f}, applications={len(self.genes)})"


@dataclass
class GAResult:
    """Result from genetic algorithm optimization."""
    best_schedule: Chromosome
    population_history: List[List[Chromosome]]
    fitness_history: List[float]
    diversity_history: List[float]
    convergence_generation: int
    final_population: List[Chromosome]


class GeneticAlgorithmOptimizer:
    """
    Genetic Algorithm optimizer for fertilizer timing.

    This optimizer uses evolutionary computation to find near-optimal timing
    schedules through iterative selection, crossover, and mutation operations.
    It supports multi-objective optimization with configurable fitness functions.
    """

    def __init__(
        self,
        population_size: int = 100,
        max_generations: int = 200,
        crossover_rate: float = 0.8,
        mutation_rate: float = 0.1,
        elitism_count: int = 5,
        tournament_size: int = 3,
        convergence_threshold: float = 0.001
    ):
        """
        Initialize the GA optimizer.

        Args:
            population_size: Number of individuals in population
            max_generations: Maximum number of generations
            crossover_rate: Probability of crossover
            mutation_rate: Probability of mutation
            elitism_count: Number of elite solutions to preserve
            tournament_size: Size of tournament for selection
            convergence_threshold: Fitness improvement threshold for convergence
        """
        self.population_size = population_size
        self.max_generations = max_generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elitism_count = elitism_count
        self.tournament_size = tournament_size
        self.convergence_threshold = convergence_threshold

        # Fitness function weights (multi-objective)
        self.fitness_weights = {
            "yield": 0.35,
            "cost": 0.25,
            "environment": 0.25,
            "risk": 0.15
        }

    def optimize(
        self,
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow],
        crop_stages: Dict[date, CropGrowthStage]
    ) -> GAResult:
        """
        Optimize fertilizer timing using genetic algorithm.

        Args:
            request: Optimization request with field and crop data
            weather_windows: Available weather windows for application
            crop_stages: Crop growth stages by date

        Returns:
            GAResult with best schedule and evolution history
        """
        logger.info(f"Starting GA optimization with population={self.population_size}, "
                   f"generations={self.max_generations}")

        # Initialize population
        population = self._initialize_population(request, weather_windows, crop_stages)

        # Evaluate initial fitness
        for individual in population:
            individual.fitness = self._evaluate_fitness(individual, request, weather_windows, crop_stages)

        # Evolution history
        population_history = []
        fitness_history = []
        diversity_history = []
        convergence_generation = self.max_generations

        best_individual = max(population, key=lambda x: x.fitness)
        previous_best_fitness = best_individual.fitness

        # Evolution loop
        for generation in range(self.max_generations):
            # Record history
            population_history.append(population.copy())
            current_best = max(population, key=lambda x: x.fitness)
            fitness_history.append(current_best.fitness)
            diversity = self._calculate_diversity(population)
            diversity_history.append(diversity)

            logger.debug(f"Generation {generation}: Best fitness={current_best.fitness:.4f}, "
                        f"Diversity={diversity:.4f}")

            # Check convergence
            improvement = current_best.fitness - previous_best_fitness
            if abs(improvement) < self.convergence_threshold and generation > 50:
                convergence_generation = generation
                logger.info(f"Converged at generation {generation}")
                break

            previous_best_fitness = current_best.fitness

            # Create next generation
            new_population = []

            # Elitism: preserve best solutions
            elite = sorted(population, key=lambda x: x.fitness, reverse=True)[:self.elitism_count]
            new_population.extend(elite)

            # Generate offspring
            while len(new_population) < self.population_size:
                # Selection
                parent1 = self._tournament_selection(population)
                parent2 = self._tournament_selection(population)

                # Crossover
                if random.random() < self.crossover_rate:
                    offspring1, offspring2 = self._crossover(parent1, parent2, request)
                else:
                    offspring1, offspring2 = parent1, parent2

                # Mutation
                if random.random() < self.mutation_rate:
                    offspring1 = self._mutate(offspring1, request, weather_windows, crop_stages)
                if random.random() < self.mutation_rate:
                    offspring2 = self._mutate(offspring2, request, weather_windows, crop_stages)

                # Evaluate offspring
                offspring1.fitness = self._evaluate_fitness(offspring1, request, weather_windows, crop_stages)
                offspring2.fitness = self._evaluate_fitness(offspring2, request, weather_windows, crop_stages)

                new_population.append(offspring1)
                if len(new_population) < self.population_size:
                    new_population.append(offspring2)

            population = new_population

        # Final evaluation
        best_individual = max(population, key=lambda x: x.fitness)

        logger.info(f"GA optimization complete. Best fitness: {best_individual.fitness:.4f}")

        return GAResult(
            best_schedule=best_individual,
            population_history=population_history,
            fitness_history=fitness_history,
            diversity_history=diversity_history,
            convergence_generation=convergence_generation,
            final_population=population
        )

    def _initialize_population(
        self,
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow],
        crop_stages: Dict[date, CropGrowthStage]
    ) -> List[Chromosome]:
        """Initialize random population of timing schedules."""
        population = []

        for _ in range(self.population_size):
            genes = []

            # Create genes for each fertilizer type
            for fertilizer_type, total_amount in request.fertilizer_requirements.items():
                # Randomly decide number of splits (1-3)
                num_splits = random.randint(1, 3) if request.split_application_allowed else 1

                # Generate random application dates within growing season
                application_dates = self._generate_random_dates(
                    num_splits, request.planting_date, request.optimization_horizon_days
                )

                # Distribute amount across splits
                if num_splits == 1:
                    amounts = [total_amount]
                else:
                    # Random distribution with some preference for early applications
                    amounts = []
                    remaining = total_amount
                    for i in range(num_splits - 1):
                        fraction = random.uniform(0.2, 0.5)
                        amount = remaining * fraction
                        amounts.append(amount)
                        remaining -= amount
                    amounts.append(remaining)

                # Create genes
                for app_date, amount in zip(application_dates, amounts):
                    method = random.choice(request.application_methods)
                    gene = ApplicationGene(fertilizer_type, app_date, amount, method)
                    genes.append(gene)

            chromosome = Chromosome(genes=genes)
            population.append(chromosome)

        return population

    def _generate_random_dates(
        self,
        num_dates: int,
        start_date: date,
        horizon_days: int
    ) -> List[date]:
        """Generate sorted random dates within the horizon."""
        dates = []
        for _ in range(num_dates):
            offset = random.randint(0, min(horizon_days, 120))  # Limit to ~4 months
            dates.append(start_date + timedelta(days=offset))

        dates.sort()
        return dates

    def _evaluate_fitness(
        self,
        individual: Chromosome,
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow],
        crop_stages: Dict[date, CropGrowthStage]
    ) -> float:
        """
        Evaluate fitness of a chromosome.

        Fitness = w1*Yield + w2*Cost + w3*Environment + w4*Risk
        """
        # Calculate individual objectives
        yield_score = self._calculate_yield_objective(individual, request, crop_stages)
        cost_score = self._calculate_cost_objective(individual, request)
        environment_score = self._calculate_environment_objective(individual, request, weather_windows)
        risk_score = self._calculate_risk_objective(individual, request, weather_windows)

        # Store objectives
        individual.objectives = {
            "yield": yield_score,
            "cost": cost_score,
            "environment": environment_score,
            "risk": risk_score
        }

        # Weighted fitness
        fitness = (
            self.fitness_weights["yield"] * yield_score +
            self.fitness_weights["cost"] * cost_score +
            self.fitness_weights["environment"] * environment_score +
            self.fitness_weights["risk"] * risk_score
        )

        # Penalty for constraint violations
        penalty = self._calculate_constraint_penalty(individual, request)
        fitness -= penalty

        return max(0.0, fitness)

    def _calculate_yield_objective(
        self,
        individual: Chromosome,
        request: TimingOptimizationRequest,
        crop_stages: Dict[date, CropGrowthStage]
    ) -> float:
        """Calculate yield optimization objective (0-100)."""
        total_score = 0.0

        for gene in individual.genes:
            # Get crop stage at application date
            crop_stage = self._get_crop_stage_for_date(gene.application_date, crop_stages)

            # Stage-specific yield response
            stage_scores = {
                CropGrowthStage.PLANTING: 0.95,
                CropGrowthStage.EMERGENCE: 0.90,
                CropGrowthStage.V2: 0.85,
                CropGrowthStage.V4: 1.00,
                CropGrowthStage.V6: 0.95,
                CropGrowthStage.V8: 0.85,
                CropGrowthStage.V10: 0.75,
                CropGrowthStage.VT: 0.70,
                CropGrowthStage.R1: 0.60
            }
            stage_score = stage_scores.get(crop_stage, 0.5)

            # Amount factor (normalized)
            amount_factor = min(1.0, gene.amount / 100.0)

            gene_score = 100.0 * stage_score * amount_factor
            total_score += gene_score

        # Normalize by number of applications
        return total_score / max(1, len(individual.genes))

    def _calculate_cost_objective(
        self,
        individual: Chromosome,
        request: TimingOptimizationRequest
    ) -> float:
        """Calculate cost optimization objective (0-100, higher is better)."""
        total_cost = 0.0

        base_costs = {
            "nitrogen": 0.5,
            "phosphorus": 0.8,
            "potassium": 0.6,
            "complete": 0.7
        }

        for gene in individual.genes:
            cost_per_lb = base_costs.get(gene.fertilizer_type.lower(), 0.6)
            total_cost += gene.amount * cost_per_lb

        # Application cost per pass
        total_cost += len(individual.genes) * 10.0

        # Normalize and invert (lower cost = higher score)
        # Assume typical cost range is $100-500
        cost_score = 100.0 * (1.0 - min(1.0, total_cost / 500.0))

        return max(0.0, cost_score)

    def _calculate_environment_objective(
        self,
        individual: Chromosome,
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow]
    ) -> float:
        """Calculate environmental optimization objective (0-100)."""
        total_score = 0.0

        for gene in individual.genes:
            # Get weather for application date
            weather = self._get_weather_for_date(gene.application_date, weather_windows)

            if weather:
                # Weather condition score
                condition_scores = {
                    WeatherCondition.OPTIMAL: 1.0,
                    WeatherCondition.ACCEPTABLE: 0.8,
                    WeatherCondition.MARGINAL: 0.5,
                    WeatherCondition.POOR: 0.2,
                    WeatherCondition.UNACCEPTABLE: 0.0
                }
                weather_score = condition_scores.get(weather.condition, 0.5)

                # Soil moisture score (optimal range: 0.4-0.7)
                if 0.4 <= weather.soil_moisture <= 0.7:
                    moisture_score = 1.0
                else:
                    moisture_score = 0.5

                # Precipitation risk (lower is better)
                precip_score = 1.0 - weather.precipitation_probability

                gene_score = 100.0 * (0.5 * weather_score + 0.3 * moisture_score + 0.2 * precip_score)
            else:
                gene_score = 50.0  # Neutral score if no weather data

            total_score += gene_score

        return total_score / max(1, len(individual.genes))

    def _calculate_risk_objective(
        self,
        individual: Chromosome,
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow]
    ) -> float:
        """Calculate risk mitigation objective (0-100)."""
        # Split application bonus (reduces risk)
        fertilizer_applications = {}
        for gene in individual.genes:
            fertilizer_applications[gene.fertilizer_type] = fertilizer_applications.get(gene.fertilizer_type, 0) + 1

        split_score = 0.0
        for fert_type, count in fertilizer_applications.items():
            if count >= 2:
                split_score += 20.0  # Bonus for splitting
            elif count >= 3:
                split_score += 30.0  # Extra bonus for multiple splits

        # Timing spread (applications spread out reduce risk)
        if len(individual.genes) > 1:
            dates = sorted([g.application_date for g in individual.genes])
            total_spread = (dates[-1] - dates[0]).days
            spread_score = min(30.0, total_spread / 2.0)  # Up to 30 points for 60-day spread
        else:
            spread_score = 0.0

        # Weather certainty (earlier applications have more certain weather)
        certainty_score = 0.0
        for gene in individual.genes:
            days_from_planting = (gene.application_date - request.planting_date).days
            # Earlier applications (within 30 days) get higher scores
            if days_from_planting <= 30:
                certainty_score += 20.0
            elif days_from_planting <= 60:
                certainty_score += 10.0

        certainty_score /= max(1, len(individual.genes))

        total_risk_score = split_score + spread_score + certainty_score

        return min(100.0, total_risk_score)

    def _calculate_constraint_penalty(
        self,
        individual: Chromosome,
        request: TimingOptimizationRequest
    ) -> float:
        """Calculate penalty for constraint violations."""
        penalty = 0.0

        # Budget constraint
        if request.budget_constraints:
            total_budget = request.budget_constraints.get("total", float('inf'))
            total_cost = sum(gene.amount * 0.6 for gene in individual.genes)  # Approximate cost
            if total_cost > total_budget:
                penalty += 50.0 * (total_cost - total_budget) / total_budget

        # Fertilizer amount constraint (must apply required amounts)
        for fertilizer_type, required_amount in request.fertilizer_requirements.items():
            applied_amount = sum(g.amount for g in individual.genes if g.fertilizer_type == fertilizer_type)
            difference = abs(applied_amount - required_amount)
            if difference > required_amount * 0.1:  # More than 10% difference
                penalty += 30.0 * (difference / required_amount)

        return penalty

    def _tournament_selection(self, population: List[Chromosome]) -> Chromosome:
        """Select individual using tournament selection."""
        tournament = random.sample(population, min(self.tournament_size, len(population)))
        return max(tournament, key=lambda x: x.fitness)

    def _crossover(
        self,
        parent1: Chromosome,
        parent2: Chromosome,
        request: TimingOptimizationRequest
    ) -> Tuple[Chromosome, Chromosome]:
        """Perform single-point crossover between two parents."""
        # Determine crossover point
        min_length = min(len(parent1.genes), len(parent2.genes))
        if min_length <= 1:
            return parent1, parent2

        crossover_point = random.randint(1, min_length - 1)

        # Create offspring
        offspring1_genes = parent1.genes[:crossover_point] + parent2.genes[crossover_point:]
        offspring2_genes = parent2.genes[:crossover_point] + parent1.genes[crossover_point:]

        offspring1 = Chromosome(genes=offspring1_genes)
        offspring2 = Chromosome(genes=offspring2_genes)

        return offspring1, offspring2

    def _mutate(
        self,
        individual: Chromosome,
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow],
        crop_stages: Dict[date, CropGrowthStage]
    ) -> Chromosome:
        """Apply mutation to an individual."""
        mutated_genes = []

        for gene in individual.genes:
            # Randomly decide if this gene mutates
            if random.random() < 0.3:  # 30% chance per gene
                mutation_type = random.choice(["date", "amount", "method"])

                if mutation_type == "date":
                    # Adjust date by +/- 7 days
                    offset = random.randint(-7, 7)
                    new_date = gene.application_date + timedelta(days=offset)
                    # Ensure date is within valid range
                    earliest = request.planting_date
                    latest = request.planting_date + timedelta(days=request.optimization_horizon_days)
                    new_date = max(earliest, min(latest, new_date))
                    mutated_gene = ApplicationGene(
                        gene.fertilizer_type, new_date, gene.amount, gene.method
                    )

                elif mutation_type == "amount":
                    # Adjust amount by +/- 20%
                    adjustment = random.uniform(0.8, 1.2)
                    new_amount = gene.amount * adjustment
                    mutated_gene = ApplicationGene(
                        gene.fertilizer_type, gene.application_date, new_amount, gene.method
                    )

                else:  # method
                    # Change application method
                    new_method = random.choice(request.application_methods)
                    mutated_gene = ApplicationGene(
                        gene.fertilizer_type, gene.application_date, gene.amount, new_method
                    )

                mutated_genes.append(mutated_gene)
            else:
                mutated_genes.append(gene)

        return Chromosome(genes=mutated_genes)

    def _calculate_diversity(self, population: List[Chromosome]) -> float:
        """Calculate population diversity based on fitness variance."""
        if len(population) < 2:
            return 0.0

        fitness_values = [ind.fitness for ind in population]
        mean_fitness = sum(fitness_values) / len(fitness_values)
        variance = sum((f - mean_fitness) ** 2 for f in fitness_values) / len(fitness_values)

        # Normalize diversity
        diversity = min(1.0, variance / max(1.0, mean_fitness))

        return diversity

    def _get_crop_stage_for_date(
        self,
        target_date: date,
        crop_stages: Dict[date, CropGrowthStage]
    ) -> CropGrowthStage:
        """Get crop growth stage for a specific date."""
        # Find the closest stage date
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
