"""
Rotation Optimization Engine
Implements advanced algorithms for multi-year crop rotation optimization.
"""

import asyncio
import random
import math
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date
from dataclasses import dataclass, field

from ..models.rotation_models import (
    FieldProfile, RotationGoal, RotationConstraint, CropRotationPlan,
    RotationYear, RotationGoalType, ConstraintType
)


@dataclass
class OptimizationContext:
    """Context for rotation optimization algorithms."""
    field_profile: FieldProfile
    goals: List[RotationGoal]
    constraints: List[RotationConstraint]
    planning_horizon: int
    available_crops: List[str]
    crop_compatibility_matrix: Dict[str, Dict[str, Any]]
    crop_benefits_database: Dict[str, Dict[str, float]]
    market_data: Dict[str, Dict[str, float]]
    climate_data: Dict[str, Any]


class RotationOptimizationEngine:
    """Advanced rotation optimization using multiple algorithms."""
    
    def __init__(self):
        self.crop_compatibility_matrix = self._initialize_crop_compatibility()
        self.crop_benefits_database = self._initialize_crop_benefits()
        self.optimization_parameters = self._initialize_optimization_parameters()
        
    def _initialize_crop_compatibility(self) -> Dict[str, Dict[str, Any]]:
        """Initialize crop compatibility matrix."""
        return {
            'corn': {
                'good_next': ['soybean', 'wheat', 'oats', 'alfalfa'],
                'avoid_next': ['corn'],  # Avoid continuous corn
                'nitrogen_demand': 'high',
                'pest_pressure': ['corn_borer', 'rootworm'],
                'disease_pressure': ['gray_leaf_spot', 'northern_corn_leaf_blight']
            },
            'soybean': {
                'good_next': ['corn', 'wheat', 'oats'],
                'avoid_next': ['soybean'],
                'nitrogen_demand': 'low',
                'nitrogen_fixation': 40,  # lbs N/acre
                'pest_pressure': ['soybean_aphid', 'bean_leaf_beetle'],
                'disease_pressure': ['sudden_death_syndrome', 'white_mold']
            },
            'wheat': {
                'good_next': ['corn', 'soybean', 'alfalfa'],
                'avoid_next': ['wheat', 'barley', 'oats'],
                'nitrogen_demand': 'medium',
                'pest_pressure': ['hessian_fly', 'wheat_midge'],
                'disease_pressure': ['fusarium_head_blight', 'stripe_rust']
            },
            'alfalfa': {
                'good_next': ['corn', 'wheat', 'oats'],
                'avoid_next': ['alfalfa'],
                'nitrogen_demand': 'low',
                'nitrogen_fixation': 150,  # lbs N/acre
                'soil_improvement': 'high',
                'pest_pressure': ['alfalfa_weevil'],
                'disease_pressure': ['bacterial_wilt', 'anthracnose']
            },
            'oats': {
                'good_next': ['corn', 'soybean', 'alfalfa'],
                'avoid_next': ['wheat', 'barley'],
                'nitrogen_demand': 'medium',
                'pest_pressure': ['crown_rust'],
                'disease_pressure': ['crown_rust', 'barley_yellow_dwarf']
            },
            'barley': {
                'good_next': ['corn', 'soybean', 'alfalfa'],
                'avoid_next': ['wheat', 'oats'],
                'nitrogen_demand': 'medium',
                'pest_pressure': ['barley_midge'],
                'disease_pressure': ['net_blotch', 'scald']
            }
        }
    
    def _initialize_crop_benefits(self) -> Dict[str, Dict[str, float]]:
        """Initialize crop benefits database."""
        return {
            'corn': {
                'nitrogen_fixation': 0,
                'soil_organic_matter': 2.5,
                'erosion_control': 3.0,
                'pest_management': 2.0,
                'weed_suppression': 3.5,
                'economic_value': 8.5
            },
            'soybean': {
                'nitrogen_fixation': 8.5,
                'soil_organic_matter': 4.0,
                'erosion_control': 2.5,
                'pest_management': 4.0,
                'weed_suppression': 2.0,
                'economic_value': 7.5
            },
            'wheat': {
                'nitrogen_fixation': 0,
                'soil_organic_matter': 3.5,
                'erosion_control': 6.0,
                'pest_management': 5.0,
                'weed_suppression': 7.0,
                'economic_value': 6.0
            },
            'alfalfa': {
                'nitrogen_fixation': 9.5,
                'soil_organic_matter': 8.5,
                'erosion_control': 9.0,
                'pest_management': 7.0,
                'weed_suppression': 8.0,
                'economic_value': 7.0
            },
            'oats': {
                'nitrogen_fixation': 0,
                'soil_organic_matter': 4.5,
                'erosion_control': 5.5,
                'pest_management': 6.0,
                'weed_suppression': 6.5,
                'economic_value': 5.0
            },
            'barley': {
                'nitrogen_fixation': 0,
                'soil_organic_matter': 4.0,
                'erosion_control': 5.0,
                'pest_management': 5.5,
                'weed_suppression': 6.0,
                'economic_value': 5.5
            }
        }
    
    def _initialize_optimization_parameters(self) -> Dict[str, Dict[str, Any]]:
        """Initialize optimization algorithm parameters."""
        return {
            'genetic_algorithm': {
                'population_size': 50,
                'generations': 100,
                'mutation_rate': 0.1,
                'crossover_rate': 0.8,
                'elite_size': 5
            },
            'simulated_annealing': {
                'initial_temperature': 1000.0,
                'cooling_rate': 0.95,
                'min_temperature': 0.01,
                'max_iterations': 1000
            },
            'multi_objective': {
                'pareto_front_size': 20,
                'diversity_threshold': 0.1,
                'convergence_threshold': 0.001
            }
        }
    
    async def generate_optimal_rotation(
        self,
        field_profile: FieldProfile,
        goals: List[RotationGoal],
        constraints: List[RotationConstraint],
        planning_horizon: int = 5
    ) -> CropRotationPlan:
        """Generate optimal crop rotation plan."""
        
        # Prepare optimization context
        context = self._prepare_optimization_context(
            field_profile, goals, constraints, planning_horizon
        )
        
        # Run multiple optimization algorithms
        ga_rotation = await self._genetic_algorithm_optimization(context)
        sa_rotation = await self._simulated_annealing_optimization(context)
        
        # Evaluate both rotations
        ga_fitness = await self.evaluate_rotation_fitness(ga_rotation, context)
        sa_fitness = await self.evaluate_rotation_fitness(sa_rotation, context)
        
        # Select best rotation
        best_rotation = ga_rotation if ga_fitness >= sa_fitness else sa_rotation
        best_fitness = max(ga_fitness, sa_fitness)
        
        # Create detailed rotation plan
        rotation_plan = await self._create_detailed_rotation_plan(
            best_rotation, best_fitness, context
        )
        
        return rotation_plan
    
    def _prepare_optimization_context(
        self,
        field_profile: FieldProfile,
        goals: List[RotationGoal],
        constraints: List[RotationConstraint],
        planning_horizon: int
    ) -> OptimizationContext:
        """Prepare context for optimization algorithms."""
        
        # Determine available crops based on field characteristics
        available_crops = self._get_available_crops(field_profile)
        
        # Get market data (mock for now)
        market_data = self._get_market_data()
        
        # Get climate data
        climate_data = self._get_climate_data(field_profile)
        
        return OptimizationContext(
            field_profile=field_profile,
            goals=goals,
            constraints=constraints,
            planning_horizon=planning_horizon,
            available_crops=available_crops,
            crop_compatibility_matrix=self.crop_compatibility_matrix,
            crop_benefits_database=self.crop_benefits_database,
            market_data=market_data,
            climate_data=climate_data
        )
    
    def _get_available_crops(self, field_profile: FieldProfile) -> List[str]:
        """Determine available crops based on field characteristics."""
        base_crops = ['corn', 'soybean', 'wheat', 'oats']
        
        # Add alfalfa for larger fields with good drainage
        if field_profile.size_acres > 40 and field_profile.drainage_class == 'well_drained':
            base_crops.append('alfalfa')
        
        # Add barley in suitable climate zones
        if hasattr(field_profile, 'climate_zone') and field_profile.climate_zone in ['3a', '3b', '4a', '4b']:
            base_crops.append('barley')
        
        return base_crops
    
    def _get_market_data(self) -> Dict[str, Dict[str, float]]:
        """Get market data for crops (mock implementation)."""
        return {
            'corn': {'price_per_bushel': 4.25, 'volatility': 0.15},
            'soybean': {'price_per_bushel': 12.50, 'volatility': 0.18},
            'wheat': {'price_per_bushel': 6.80, 'volatility': 0.22},
            'oats': {'price_per_bushel': 3.20, 'volatility': 0.25},
            'alfalfa': {'price_per_ton': 180.00, 'volatility': 0.12},
            'barley': {'price_per_bushel': 4.50, 'volatility': 0.20}
        }
    
    def _get_climate_data(self, field_profile: FieldProfile) -> Dict[str, Any]:
        """Get climate data for field location."""
        return {
            'growing_degree_days': 2800,
            'precipitation_annual': 34.5,
            'frost_free_days': 165,
            'climate_zone': getattr(field_profile, 'climate_zone', '5a')
        }
    
    async def _genetic_algorithm_optimization(self, context: OptimizationContext) -> List[str]:
        """Optimize rotation using genetic algorithm."""
        params = self.optimization_parameters['genetic_algorithm']
        
        # Initialize population
        population = []
        for _ in range(params['population_size']):
            rotation = await self._generate_random_rotation(context)
            population.append(rotation)
        
        # Evolution loop
        for generation in range(params['generations']):
            # Evaluate fitness for all individuals
            fitness_scores = []
            for rotation in population:
                fitness = await self.evaluate_rotation_fitness(rotation, context)
                fitness_scores.append(fitness)
            
            # Selection and reproduction
            new_population = []
            
            # Keep elite individuals
            elite_indices = sorted(range(len(fitness_scores)), 
                                 key=lambda i: fitness_scores[i], 
                                 reverse=True)[:params['elite_size']]
            for idx in elite_indices:
                new_population.append(population[idx].copy())
            
            # Generate offspring
            while len(new_population) < params['population_size']:
                # Tournament selection
                parent1 = self._tournament_selection(population, fitness_scores)
                parent2 = self._tournament_selection(population, fitness_scores)
                
                # Crossover
                if random.random() < params['crossover_rate']:
                    child1, child2 = self._crossover(parent1, parent2, context)
                else:
                    child1, child2 = parent1.copy(), parent2.copy()
                
                # Mutation
                if random.random() < params['mutation_rate']:
                    child1 = await self._mutate(child1, context)
                if random.random() < params['mutation_rate']:
                    child2 = await self._mutate(child2, context)
                
                new_population.extend([child1, child2])
            
            # Trim to population size
            population = new_population[:params['population_size']]
        
        # Return best individual
        final_fitness = []
        for rotation in population:
            fitness = await self.evaluate_rotation_fitness(rotation, context)
            final_fitness.append(fitness)
        
        best_idx = max(range(len(final_fitness)), key=lambda i: final_fitness[i])
        return population[best_idx]
    
    async def _simulated_annealing_optimization(self, context: OptimizationContext) -> List[str]:
        """Optimize rotation using simulated annealing."""
        params = self.optimization_parameters['simulated_annealing']
        
        # Initialize with random rotation
        current_rotation = await self._generate_random_rotation(context)
        current_fitness = await self.evaluate_rotation_fitness(current_rotation, context)
        
        best_rotation = current_rotation.copy()
        best_fitness = current_fitness
        
        temperature = params['initial_temperature']
        
        for iteration in range(params['max_iterations']):
            # Generate neighbor solution
            neighbor_rotation = await self._generate_neighbor(current_rotation, context)
            neighbor_fitness = await self.evaluate_rotation_fitness(neighbor_rotation, context)
            
            # Accept or reject neighbor
            if neighbor_fitness > current_fitness:
                # Accept better solution
                current_rotation = neighbor_rotation
                current_fitness = neighbor_fitness
                
                if current_fitness > best_fitness:
                    best_rotation = current_rotation.copy()
                    best_fitness = current_fitness
            else:
                # Accept worse solution with probability
                delta = current_fitness - neighbor_fitness
                probability = math.exp(-delta / temperature)
                
                if random.random() < probability:
                    current_rotation = neighbor_rotation
                    current_fitness = neighbor_fitness
            
            # Cool down
            temperature *= params['cooling_rate']
            
            if temperature < params['min_temperature']:
                break
        
        return best_rotation
    
    async def _generate_random_rotation(self, context: OptimizationContext) -> List[str]:
        """Generate random valid rotation."""
        rotation = []
        available_crops = context.available_crops.copy()
        
        for year in range(context.planning_horizon):
            # Filter crops based on constraints and compatibility
            valid_crops = self._get_valid_crops_for_position(
                rotation, year, context
            )
            
            if not valid_crops:
                valid_crops = available_crops
            
            crop = random.choice(valid_crops)
            rotation.append(crop)
        
        return rotation
    
    def _get_valid_crops_for_position(
        self, 
        rotation: List[str], 
        position: int, 
        context: OptimizationContext
    ) -> List[str]:
        """Get valid crops for specific position in rotation."""
        valid_crops = context.available_crops.copy()
        
        # Apply constraints
        for constraint in context.constraints:
            if constraint.constraint_type == ConstraintType.REQUIRED_CROP:
                crop_name = constraint.parameters.get('crop_name')
                if crop_name and crop_name not in rotation:
                    # Must include this crop somewhere
                    if position == context.planning_horizon - 1:
                        # Last position, must include if not already present
                        valid_crops = [crop_name] if crop_name in valid_crops else valid_crops
            
            elif constraint.constraint_type == ConstraintType.EXCLUDED_CROP:
                crop_name = constraint.parameters.get('crop_name')
                if crop_name in valid_crops:
                    valid_crops.remove(crop_name)
        
        # Apply compatibility rules
        if position > 0:
            previous_crop = rotation[position - 1]
            compatibility = self.crop_compatibility_matrix.get(previous_crop, {})
            avoid_next = compatibility.get('avoid_next', [])
            
            # Remove crops that should be avoided after previous crop
            valid_crops = [crop for crop in valid_crops if crop not in avoid_next]
        
        return valid_crops if valid_crops else context.available_crops
    
    def _tournament_selection(self, population: List[List[str]], fitness_scores: List[float]) -> List[str]:
        """Tournament selection for genetic algorithm."""
        tournament_size = 3
        tournament_indices = random.sample(range(len(population)), tournament_size)
        tournament_fitness = [fitness_scores[i] for i in tournament_indices]
        
        winner_idx = tournament_indices[max(range(len(tournament_fitness)), 
                                          key=lambda i: tournament_fitness[i])]
        return population[winner_idx]
    
    def _crossover(self, parent1: List[str], parent2: List[str], context: OptimizationContext) -> Tuple[List[str], List[str]]:
        """Single-point crossover for rotations."""
        if len(parent1) != len(parent2):
            return parent1.copy(), parent2.copy()
        
        crossover_point = random.randint(1, len(parent1) - 1)
        
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        
        return child1, child2
    
    async def _mutate(self, rotation: List[str], context: OptimizationContext) -> List[str]:
        """Mutate rotation by changing random position."""
        mutated = rotation.copy()
        position = random.randint(0, len(rotation) - 1)
        
        valid_crops = self._get_valid_crops_for_position(
            mutated[:position] + mutated[position+1:], position, context
        )
        
        if valid_crops:
            mutated[position] = random.choice(valid_crops)
        
        return mutated
    
    async def _generate_neighbor(self, rotation: List[str], context: OptimizationContext) -> List[str]:
        """Generate neighbor solution for simulated annealing."""
        return await self._mutate(rotation, context)
    
    async def evaluate_rotation_fitness(self, rotation: List[str], context: OptimizationContext) -> float:
        """Evaluate fitness of rotation based on goals and constraints."""
        
        # Calculate benefit scores
        benefit_scores = await self._calculate_detailed_benefit_scores(rotation, context)
        
        # Calculate goal satisfaction
        goal_satisfaction = self._calculate_goal_satisfaction(benefit_scores, context.goals)
        
        # Calculate constraint penalties
        constraint_penalties = self._calculate_constraint_penalties(rotation, context.constraints)
        
        # Calculate diversity bonus
        diversity_bonus = self._calculate_diversity_bonus(rotation)
        
        # Combine scores
        fitness = (
            goal_satisfaction * 0.6 +
            diversity_bonus * 0.2 +
            (100 - constraint_penalties) * 0.2
        )
        
        return max(0, fitness)
    
    async def _calculate_detailed_benefit_scores(
        self, 
        rotation: List[str], 
        context: OptimizationContext
    ) -> Dict[str, float]:
        """Calculate detailed benefit scores for rotation."""
        
        benefits = {
            'nitrogen_fixation': 0,
            'soil_organic_matter': 0,
            'erosion_control': 0,
            'pest_management': 0,
            'weed_suppression': 0,
            'economic_value': 0
        }
        
        # Calculate cumulative benefits
        for i, crop in enumerate(rotation):
            crop_benefits = self.crop_benefits_database.get(crop, {})
            
            for benefit_type in benefits:
                base_score = crop_benefits.get(benefit_type, 0)
                
                # Apply position-based modifiers
                if benefit_type == 'nitrogen_fixation' and i > 0:
                    # Nitrogen fixation benefits following crops
                    base_score *= 1.2
                
                if benefit_type == 'pest_management':
                    # Pest management improves with diversity
                    unique_crops = len(set(rotation[:i+1]))
                    base_score *= (1 + 0.1 * unique_crops)
                
                benefits[benefit_type] += base_score
        
        # Normalize scores
        for benefit_type in benefits:
            benefits[benefit_type] = min(100, benefits[benefit_type] / len(rotation) * 10)
        
        return benefits
    
    def _calculate_goal_satisfaction(
        self, 
        benefit_scores: Dict[str, float], 
        goals: List[RotationGoal]
    ) -> float:
        """Calculate how well rotation satisfies goals."""
        
        if not goals:
            return 50.0  # Neutral score if no goals
        
        total_satisfaction = 0
        total_weight = 0
        
        for goal in goals:
            satisfaction = 0
            
            if goal.goal_type == RotationGoalType.SOIL_HEALTH:
                satisfaction = (
                    benefit_scores.get('soil_organic_matter', 0) * 0.4 +
                    benefit_scores.get('erosion_control', 0) * 0.3 +
                    benefit_scores.get('nitrogen_fixation', 0) * 0.3
                )
            
            elif goal.goal_type == RotationGoalType.PROFIT_MAXIMIZATION:
                satisfaction = benefit_scores.get('economic_value', 0)
            
            elif goal.goal_type == RotationGoalType.PEST_MANAGEMENT:
                satisfaction = (
                    benefit_scores.get('pest_management', 0) * 0.6 +
                    benefit_scores.get('weed_suppression', 0) * 0.4
                )
            
            elif goal.goal_type == RotationGoalType.SUSTAINABILITY:
                satisfaction = (
                    benefit_scores.get('nitrogen_fixation', 0) * 0.3 +
                    benefit_scores.get('soil_organic_matter', 0) * 0.3 +
                    benefit_scores.get('erosion_control', 0) * 0.2 +
                    benefit_scores.get('pest_management', 0) * 0.2
                )
            
            total_satisfaction += satisfaction * goal.weight
            total_weight += goal.weight
        
        return total_satisfaction / total_weight if total_weight > 0 else 50.0
    
    def _calculate_constraint_penalties(
        self, 
        rotation: List[str], 
        constraints: List[RotationConstraint]
    ) -> float:
        """Calculate penalty for constraint violations."""
        
        total_penalty = 0
        
        for constraint in constraints:
            penalty = 0
            
            if constraint.constraint_type == ConstraintType.REQUIRED_CROP:
                crop_name = constraint.parameters.get('crop_name')
                if crop_name and crop_name not in rotation:
                    penalty = 50 if constraint.is_hard_constraint else 20
            
            elif constraint.constraint_type == ConstraintType.EXCLUDED_CROP:
                crop_name = constraint.parameters.get('crop_name')
                if crop_name and crop_name in rotation:
                    penalty = 30 if constraint.is_hard_constraint else 10
            
            elif constraint.constraint_type == ConstraintType.MAX_CONSECUTIVE:
                crop_name = constraint.parameters.get('crop_name')
                max_consecutive = constraint.parameters.get('max_consecutive', 1)
                
                if crop_name:
                    consecutive_count = 0
                    max_found = 0
                    
                    for crop in rotation:
                        if crop == crop_name:
                            consecutive_count += 1
                            max_found = max(max_found, consecutive_count)
                        else:
                            consecutive_count = 0
                    
                    if max_found > max_consecutive:
                        penalty = (max_found - max_consecutive) * 15
            
            total_penalty += penalty
        
        return min(100, total_penalty)
    
    def _calculate_diversity_bonus(self, rotation: List[str]) -> float:
        """Calculate bonus for crop diversity."""
        unique_crops = len(set(rotation))
        total_crops = len(rotation)
        
        diversity_ratio = unique_crops / total_crops
        return diversity_ratio * 100
    
    async def _create_detailed_rotation_plan(
        self,
        rotation: List[str],
        fitness_score: float,
        context: OptimizationContext
    ) -> CropRotationPlan:
        """Create detailed rotation plan from optimized sequence."""
        
        current_year = datetime.now().year
        rotation_years = []
        rotation_details = {}
        
        for i, crop in enumerate(rotation):
            year = current_year + i
            
            # Estimate yield for this crop in this position
            estimated_yield = await self._estimate_crop_yield(
                crop, context.field_profile, i, rotation
            )
            
            # Create rotation year
            rotation_year = RotationYear(
                year=year,
                crop_name=crop,
                estimated_yield=estimated_yield,
                confidence_score=min(1.0, fitness_score / 100)
            )
            rotation_years.append(rotation_year)
            
            # Add detailed information
            rotation_details[year] = {
                'crop_name': crop,
                'estimated_yield': estimated_yield,
                'planting_recommendations': self._get_planting_recommendations(crop),
                'management_notes': self._get_management_notes(crop, i, rotation),
                'expected_benefits': self._get_expected_benefits(crop, i, rotation)
            }
        
        # Calculate benefit scores
        benefit_scores = await self._calculate_detailed_benefit_scores(rotation, context)
        
        return CropRotationPlan(
            plan_id=f"rotation_{context.field_profile.field_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            field_id=context.field_profile.field_id,
            farm_id=context.field_profile.farm_id,
            planning_horizon=context.planning_horizon,
            rotation_years=rotation_years,
            overall_score=fitness_score,
            benefit_analysis=benefit_scores,
            rotation_details=rotation_details,
            created_at=datetime.now(),
            goals_addressed=[goal.goal_id for goal in context.goals],
            constraints_applied=[constraint.constraint_id for constraint in context.constraints]
        )
    
    async def _estimate_crop_yield(
        self,
        crop: str,
        field_profile: FieldProfile,
        position: int,
        rotation: List[str]
    ) -> float:
        """Estimate crop yield based on position in rotation."""
        
        # Base yields (simplified)
        base_yields = {
            'corn': 170.0,
            'soybean': 50.0,
            'wheat': 60.0,
            'oats': 80.0,
            'alfalfa': 4.5,  # tons/acre
            'barley': 70.0
        }
        
        base_yield = base_yields.get(crop, 100.0)
        
        # Adjust based on previous crops
        if position > 0:
            previous_crop = rotation[position - 1]
            
            # Nitrogen fixation benefit
            if crop == 'corn' and previous_crop in ['soybean', 'alfalfa']:
                if previous_crop == 'soybean':
                    base_yield *= 1.08  # 8% yield increase
                elif previous_crop == 'alfalfa':
                    base_yield *= 1.15  # 15% yield increase
            
            # Pest break benefit
            compatibility = self.crop_compatibility_matrix.get(previous_crop, {})
            if crop in compatibility.get('good_next', []):
                base_yield *= 1.05  # 5% yield increase
        
        # Field-specific adjustments
        if hasattr(field_profile, 'soil_type'):
            if field_profile.soil_type == 'silt_loam':
                base_yield *= 1.02  # Slight increase for good soil
            elif field_profile.soil_type == 'clay':
                base_yield *= 0.95  # Slight decrease for heavy soil
        
        return round(base_yield, 1)
    
    def _get_planting_recommendations(self, crop: str) -> Dict[str, Any]:
        """Get planting recommendations for crop."""
        recommendations = {
            'corn': {
                'planting_window': 'April 20 - May 15',
                'seeding_rate': '32,000 seeds/acre',
                'planting_depth': '2.0 inches',
                'row_spacing': '30 inches'
            },
            'soybean': {
                'planting_window': 'May 1 - May 25',
                'seeding_rate': '140,000 seeds/acre',
                'planting_depth': '1.5 inches',
                'row_spacing': '15-30 inches'
            },
            'wheat': {
                'planting_window': 'September 15 - October 15',
                'seeding_rate': '1.2 million seeds/acre',
                'planting_depth': '1.0 inches',
                'row_spacing': '7.5 inches'
            },
            'oats': {
                'planting_window': 'March 15 - April 15',
                'seeding_rate': '2.5 bushels/acre',
                'planting_depth': '1.0 inches',
                'row_spacing': '7.5 inches'
            },
            'alfalfa': {
                'planting_window': 'April 1 - May 1 or August 15 - September 15',
                'seeding_rate': '15-20 lbs/acre',
                'planting_depth': '0.25 inches',
                'row_spacing': '7.5 inches'
            }
        }
        
        return recommendations.get(crop, {
            'planting_window': 'Consult local extension',
            'seeding_rate': 'Follow seed company recommendations',
            'planting_depth': 'Standard for crop type',
            'row_spacing': 'Equipment dependent'
        })
    
    def _get_management_notes(self, crop: str, position: int, rotation: List[str]) -> List[str]:
        """Get management notes for crop in rotation context."""
        notes = []
        
        # Previous crop considerations
        if position > 0:
            previous_crop = rotation[position - 1]
            
            if crop == 'corn' and previous_crop == 'soybean':
                notes.append("Reduce nitrogen application by 30-40 lbs/acre due to soybean nitrogen credit")
            
            if previous_crop == 'alfalfa':
                notes.append("Excellent nitrogen availability from alfalfa termination")
                notes.append("Monitor for alfalfa weevil carryover")
        
        # Crop-specific notes
        crop_notes = {
            'corn': [
                "Monitor for corn rootworm if following corn",
                "Consider split nitrogen application for efficiency",
                "Scout for corn borer during tasseling"
            ],
            'soybean': [
                "Inoculate seed if field hasn't grown soybeans recently",
                "Monitor for soybean aphid mid-season",
                "Consider fungicide at R3 if conditions warrant"
            ],
            'wheat': [
                "Apply nitrogen in early spring",
                "Monitor for Fusarium head blight during flowering",
                "Consider fungicide for leaf diseases"
            ]
        }
        
        notes.extend(crop_notes.get(crop, []))
        
        return notes
    
    def _get_expected_benefits(self, crop: str, position: int, rotation: List[str]) -> Dict[str, str]:
        """Get expected benefits from crop in rotation."""
        benefits = {}
        
        crop_benefits = self.crop_benefits_database.get(crop, {})
        
        if crop_benefits.get('nitrogen_fixation', 0) > 0:
            benefits['nitrogen_fixation'] = f"Fixes approximately {crop_benefits['nitrogen_fixation']} lbs N/acre"
        
        if crop_benefits.get('soil_organic_matter', 0) > 5:
            benefits['soil_health'] = "Improves soil organic matter and structure"
        
        if crop_benefits.get('pest_management', 0) > 5:
            benefits['pest_management'] = "Breaks pest and disease cycles"
        
        if crop_benefits.get('weed_suppression', 0) > 5:
            benefits['weed_control'] = "Provides good weed suppression"
        
        return benefits