"""
Rotation Goal and Constraint Management Service
Handles rotation objectives, goal prioritization, and constraint management.
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from ..models.rotation_models import (
    RotationGoal, RotationConstraint, RotationGoalType, ConstraintType,
    FieldProfile
)


@dataclass
class GoalConflictResolution:
    """Resolution for conflicting goals."""
    conflicting_goals: List[str]
    resolution_strategy: str
    weight_adjustments: Dict[str, float]
    explanation: str


@dataclass
class GoalAchievementMeasurement:
    """Measurement of goal achievement."""
    goal_id: str
    target_value: float
    achieved_value: float
    achievement_percentage: float
    confidence_level: float
    measurement_date: datetime


@dataclass
class ConstraintValidationResult:
    """Result of constraint validation."""
    constraint_id: str
    is_feasible: bool
    conflicts: List[str]
    suggestions: List[str]
    impact_assessment: Dict[str, float]


class GoalPriorityStrategy(Enum):
    """Strategies for goal prioritization."""
    WEIGHTED_AVERAGE = "weighted_average"
    LEXICOGRAPHIC = "lexicographic"
    PARETO_OPTIMAL = "pareto_optimal"
    FARMER_PREFERENCE = "farmer_preference"


class RotationGoalService:
    """Service for managing rotation goals and constraints."""
    
    def __init__(self):
        self.goal_templates = self._initialize_goal_templates()
        self.constraint_templates = self._initialize_constraint_templates()
        self.goal_compatibility_matrix = self._initialize_goal_compatibility()
        
    def _initialize_goal_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize predefined goal templates."""
        return {
            'soil_health_improvement': {
                'type': RotationGoalType.SOIL_HEALTH,
                'description': 'Improve soil health through diverse rotation',
                'default_weight': 0.3,
                'measurement_criteria': [
                    'organic_matter_increase',
                    'erosion_reduction',
                    'soil_structure_improvement'
                ],
                'target_metrics': {
                    'organic_matter_increase_percent': 10.0,
                    'erosion_reduction_percent': 25.0,
                    'soil_compaction_reduction': 15.0
                }
            },
            'profit_maximization': {
                'type': RotationGoalType.PROFIT_MAXIMIZATION,
                'description': 'Maximize long-term profitability',
                'default_weight': 0.4,
                'measurement_criteria': [
                    'net_profit_per_acre',
                    'roi_percentage',
                    'cost_reduction'
                ],
                'target_metrics': {
                    'min_roi_percent': 15.0,
                    'profit_increase_percent': 20.0,
                    'cost_reduction_percent': 10.0
                }
            },
            'pest_disease_management': {
                'type': RotationGoalType.PEST_MANAGEMENT,
                'description': 'Reduce pest and disease pressure',
                'default_weight': 0.2,
                'measurement_criteria': [
                    'pest_pressure_reduction',
                    'pesticide_use_reduction',
                    'beneficial_insect_habitat'
                ],
                'target_metrics': {
                    'pest_pressure_reduction_percent': 30.0,
                    'pesticide_reduction_percent': 25.0,
                    'beneficial_habitat_increase': 40.0
                }
            },
            'environmental_sustainability': {
                'type': RotationGoalType.SUSTAINABILITY,
                'description': 'Enhance environmental sustainability',
                'default_weight': 0.25,
                'measurement_criteria': [
                    'carbon_sequestration',
                    'water_conservation',
                    'biodiversity_enhancement'
                ],
                'target_metrics': {
                    'carbon_sequestration_tons_per_acre': 0.5,
                    'water_use_reduction_percent': 15.0,
                    'biodiversity_index_increase': 25.0
                }
            },
            'risk_reduction': {
                'type': RotationGoalType.RISK_MANAGEMENT,
                'description': 'Minimize production and market risks',
                'default_weight': 0.15,
                'measurement_criteria': [
                    'yield_stability',
                    'market_diversification',
                    'weather_resilience'
                ],
                'target_metrics': {
                    'yield_coefficient_variation': 0.15,
                    'market_correlation_reduction': 0.3,
                    'drought_tolerance_improvement': 20.0
                }
            },
            'labor_efficiency': {
                'type': RotationGoalType.OPERATIONAL_EFFICIENCY,
                'description': 'Optimize labor and equipment efficiency',
                'default_weight': 0.1,
                'measurement_criteria': [
                    'labor_hour_reduction',
                    'equipment_utilization',
                    'timing_optimization'
                ],
                'target_metrics': {
                    'labor_reduction_percent': 15.0,
                    'equipment_efficiency_increase': 20.0,
                    'timing_conflict_reduction': 30.0
                }
            }
        }
    
    def _initialize_constraint_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize predefined constraint templates."""
        return {
            'required_crop_inclusion': {
                'type': ConstraintType.REQUIRED_CROP,
                'description': 'Must include specific crop in rotation',
                'parameters': ['crop_name', 'minimum_frequency'],
                'validation_rules': ['crop_availability', 'field_suitability']
            },
            'crop_exclusion': {
                'type': ConstraintType.EXCLUDED_CROP,
                'description': 'Exclude specific crop from rotation',
                'parameters': ['crop_name', 'exclusion_reason'],
                'validation_rules': ['alternative_availability']
            },
            'maximum_consecutive': {
                'type': ConstraintType.MAX_CONSECUTIVE,
                'description': 'Limit consecutive years of same crop',
                'parameters': ['crop_name', 'max_consecutive_years'],
                'validation_rules': ['rotation_length_compatibility']
            },
            'minimum_diversity': {
                'type': ConstraintType.MIN_DIVERSITY,
                'description': 'Ensure minimum crop diversity',
                'parameters': ['min_unique_crops', 'diversity_index_threshold'],
                'validation_rules': ['available_crop_count']
            },
            'seasonal_timing': {
                'type': ConstraintType.TIMING_CONSTRAINT,
                'description': 'Manage seasonal timing conflicts',
                'parameters': ['operation_type', 'time_window', 'resource_limits'],
                'validation_rules': ['equipment_availability', 'labor_capacity']
            },
            'economic_threshold': {
                'type': ConstraintType.ECONOMIC_CONSTRAINT,
                'description': 'Meet minimum economic thresholds',
                'parameters': ['min_profit_per_acre', 'max_cost_per_acre'],
                'validation_rules': ['market_price_validation']
            },
            'regulatory_compliance': {
                'type': ConstraintType.REGULATORY_CONSTRAINT,
                'description': 'Comply with regulatory requirements',
                'parameters': ['regulation_type', 'compliance_requirements'],
                'validation_rules': ['regulation_applicability']
            }
        }
    
    def _initialize_goal_compatibility(self) -> Dict[str, Dict[str, float]]:
        """Initialize goal compatibility matrix."""
        return {
            'soil_health_improvement': {
                'profit_maximization': 0.7,  # Generally compatible
                'pest_disease_management': 0.9,  # Highly compatible
                'environmental_sustainability': 0.95,  # Very compatible
                'risk_reduction': 0.8,
                'labor_efficiency': 0.6
            },
            'profit_maximization': {
                'soil_health_improvement': 0.7,
                'pest_disease_management': 0.6,
                'environmental_sustainability': 0.5,  # Potential conflict
                'risk_reduction': 0.8,
                'labor_efficiency': 0.9
            },
            'pest_disease_management': {
                'soil_health_improvement': 0.9,
                'profit_maximization': 0.6,
                'environmental_sustainability': 0.85,
                'risk_reduction': 0.9,
                'labor_efficiency': 0.7
            },
            'environmental_sustainability': {
                'soil_health_improvement': 0.95,
                'profit_maximization': 0.5,
                'pest_disease_management': 0.85,
                'risk_reduction': 0.8,
                'labor_efficiency': 0.6
            },
            'risk_reduction': {
                'soil_health_improvement': 0.8,
                'profit_maximization': 0.8,
                'pest_disease_management': 0.9,
                'environmental_sustainability': 0.8,
                'labor_efficiency': 0.7
            },
            'labor_efficiency': {
                'soil_health_improvement': 0.6,
                'profit_maximization': 0.9,
                'pest_disease_management': 0.7,
                'environmental_sustainability': 0.6,
                'risk_reduction': 0.7
            }
        }
    
    async def create_rotation_goal(
        self,
        goal_type: RotationGoalType,
        priority: int,
        weight: float,
        description: str,
        target_metrics: Optional[Dict[str, float]] = None,
        custom_parameters: Optional[Dict[str, Any]] = None
    ) -> RotationGoal:
        """Create a new rotation goal."""
        
        goal_id = f"goal_{goal_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Get template if available
        template_key = self._get_template_key_for_goal_type(goal_type)
        template = self.goal_templates.get(template_key, {})
        
        # Merge target metrics
        final_target_metrics = template.get('target_metrics', {}).copy()
        if target_metrics:
            final_target_metrics.update(target_metrics)
        
        goal = RotationGoal(
            goal_id=goal_id,
            goal_type=goal_type,
            priority=priority,
            weight=weight,
            description=description,
            target_metrics=final_target_metrics,
            measurement_criteria=template.get('measurement_criteria', []),
            created_at=datetime.now(),
            is_active=True,
            custom_parameters=custom_parameters or {}
        )
        
        return goal
    
    async def create_rotation_constraint(
        self,
        constraint_type: ConstraintType,
        description: str,
        parameters: Dict[str, Any],
        is_hard_constraint: bool = True,
        priority: int = 5
    ) -> RotationConstraint:
        """Create a new rotation constraint."""
        
        constraint_id = f"constraint_{constraint_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Validate constraint parameters
        validation_result = await self._validate_constraint_parameters(
            constraint_type, parameters
        )
        
        if not validation_result.is_feasible:
            raise ValueError(f"Invalid constraint parameters: {validation_result.conflicts}")
        
        constraint = RotationConstraint(
            constraint_id=constraint_id,
            constraint_type=constraint_type,
            description=description,
            parameters=parameters,
            is_hard_constraint=is_hard_constraint,
            priority=priority,
            created_at=datetime.now(),
            is_active=True
        )
        
        return constraint
    
    async def prioritize_goals(
        self,
        goals: List[RotationGoal],
        strategy: GoalPriorityStrategy = GoalPriorityStrategy.WEIGHTED_AVERAGE,
        farmer_preferences: Optional[Dict[str, float]] = None
    ) -> List[RotationGoal]:
        """Prioritize goals based on strategy."""
        
        if strategy == GoalPriorityStrategy.WEIGHTED_AVERAGE:
            return self._prioritize_by_weighted_average(goals)
        
        elif strategy == GoalPriorityStrategy.LEXICOGRAPHIC:
            return self._prioritize_lexicographically(goals)
        
        elif strategy == GoalPriorityStrategy.PARETO_OPTIMAL:
            return await self._prioritize_pareto_optimal(goals)
        
        elif strategy == GoalPriorityStrategy.FARMER_PREFERENCE:
            return self._prioritize_by_farmer_preference(goals, farmer_preferences)
        
        else:
            return sorted(goals, key=lambda g: (g.priority, g.weight), reverse=True)
    
    async def resolve_goal_conflicts(
        self,
        goals: List[RotationGoal]
    ) -> List[GoalConflictResolution]:
        """Identify and resolve conflicts between goals."""
        
        conflicts = []
        
        # Check pairwise compatibility
        for i, goal1 in enumerate(goals):
            for j, goal2 in enumerate(goals[i+1:], i+1):
                compatibility = self._get_goal_compatibility(goal1, goal2)
                
                if compatibility < 0.6:  # Threshold for conflict
                    resolution = await self._resolve_goal_conflict(goal1, goal2, compatibility)
                    conflicts.append(resolution)
        
        return conflicts
    
    async def measure_goal_achievement(
        self,
        goal: RotationGoal,
        rotation_results: Dict[str, Any],
        field_profile: FieldProfile
    ) -> GoalAchievementMeasurement:
        """Measure achievement of a specific goal."""
        
        achieved_value = 0.0
        target_value = 0.0
        confidence_level = 0.8
        
        if goal.goal_type == RotationGoalType.SOIL_HEALTH:
            achieved_value, target_value = self._measure_soil_health_achievement(
                goal, rotation_results
            )
        
        elif goal.goal_type == RotationGoalType.PROFIT_MAXIMIZATION:
            achieved_value, target_value = self._measure_profit_achievement(
                goal, rotation_results
            )
        
        elif goal.goal_type == RotationGoalType.PEST_MANAGEMENT:
            achieved_value, target_value = self._measure_pest_management_achievement(
                goal, rotation_results
            )
        
        elif goal.goal_type == RotationGoalType.SUSTAINABILITY:
            achieved_value, target_value = self._measure_sustainability_achievement(
                goal, rotation_results
            )
        
        elif goal.goal_type == RotationGoalType.RISK_MANAGEMENT:
            achieved_value, target_value = self._measure_risk_management_achievement(
                goal, rotation_results
            )
        
        # Calculate achievement percentage
        if target_value > 0:
            achievement_percentage = min(100, (achieved_value / target_value) * 100)
        else:
            achievement_percentage = 0
        
        return GoalAchievementMeasurement(
            goal_id=goal.goal_id,
            target_value=target_value,
            achieved_value=achieved_value,
            achievement_percentage=achievement_percentage,
            confidence_level=confidence_level,
            measurement_date=datetime.now()
        )
    
    async def validate_constraints(
        self,
        constraints: List[RotationConstraint],
        field_profile: FieldProfile,
        available_crops: List[str]
    ) -> List[ConstraintValidationResult]:
        """Validate feasibility of constraints."""
        
        validation_results = []
        
        for constraint in constraints:
            result = await self._validate_single_constraint(
                constraint, field_profile, available_crops
            )
            validation_results.append(result)
        
        # Check for constraint conflicts
        conflict_results = await self._check_constraint_conflicts(constraints)
        validation_results.extend(conflict_results)
        
        return validation_results
    
    async def suggest_goal_adjustments(
        self,
        goals: List[RotationGoal],
        constraints: List[RotationConstraint],
        field_profile: FieldProfile
    ) -> List[Dict[str, Any]]:
        """Suggest adjustments to goals based on constraints and field conditions."""
        
        suggestions = []
        
        # Analyze goal feasibility
        for goal in goals:
            feasibility = await self._analyze_goal_feasibility(
                goal, constraints, field_profile
            )
            
            if feasibility['is_feasible']:
                continue
            
            # Generate adjustment suggestions
            adjustments = await self._generate_goal_adjustments(
                goal, feasibility['limiting_factors']
            )
            
            suggestions.append({
                'goal_id': goal.goal_id,
                'current_target': goal.target_metrics,
                'suggested_adjustments': adjustments,
                'reasoning': feasibility['reasoning'],
                'impact_assessment': feasibility['impact_assessment']
            })
        
        return suggestions
    
    async def optimize_goal_weights(
        self,
        goals: List[RotationGoal],
        constraints: List[RotationConstraint],
        field_profile: FieldProfile,
        optimization_criteria: str = 'balanced'
    ) -> Dict[str, float]:
        """Optimize goal weights for better rotation outcomes."""
        
        current_weights = {goal.goal_id: goal.weight for goal in goals}
        
        if optimization_criteria == 'balanced':
            optimized_weights = await self._optimize_for_balance(goals, constraints)
        
        elif optimization_criteria == 'profit_focused':
            optimized_weights = await self._optimize_for_profit(goals, constraints)
        
        elif optimization_criteria == 'sustainability_focused':
            optimized_weights = await self._optimize_for_sustainability(goals, constraints)
        
        else:
            optimized_weights = current_weights
        
        # Ensure weights sum to 1.0
        total_weight = sum(optimized_weights.values())
        if total_weight > 0:
            optimized_weights = {
                goal_id: weight / total_weight 
                for goal_id, weight in optimized_weights.items()
            }
        
        return optimized_weights
    
    def _get_template_key_for_goal_type(self, goal_type: RotationGoalType) -> str:
        """Get template key for goal type."""
        mapping = {
            RotationGoalType.SOIL_HEALTH: 'soil_health_improvement',
            RotationGoalType.PROFIT_MAXIMIZATION: 'profit_maximization',
            RotationGoalType.PEST_MANAGEMENT: 'pest_disease_management',
            RotationGoalType.SUSTAINABILITY: 'environmental_sustainability',
            RotationGoalType.RISK_MANAGEMENT: 'risk_reduction',
            RotationGoalType.OPERATIONAL_EFFICIENCY: 'labor_efficiency'
        }
        return mapping.get(goal_type, 'soil_health_improvement')
    
    async def _validate_constraint_parameters(
        self,
        constraint_type: ConstraintType,
        parameters: Dict[str, Any]
    ) -> ConstraintValidationResult:
        """Validate constraint parameters."""
        
        conflicts = []
        suggestions = []
        is_feasible = True
        
        if constraint_type == ConstraintType.REQUIRED_CROP:
            crop_name = parameters.get('crop_name')
            if not crop_name:
                conflicts.append("Missing required parameter: crop_name")
                is_feasible = False
            
            # Check if crop is available (simplified validation)
            available_crops = ['corn', 'soybean', 'wheat', 'oats', 'alfalfa', 'barley']
            if crop_name and crop_name not in available_crops:
                conflicts.append(f"Crop '{crop_name}' not available in this region")
                suggestions.append(f"Consider alternative crops: {', '.join(available_crops[:3])}")
        
        elif constraint_type == ConstraintType.MAX_CONSECUTIVE:
            crop_name = parameters.get('crop_name')
            max_consecutive = parameters.get('max_consecutive')
            
            if not crop_name:
                conflicts.append("Missing required parameter: crop_name")
                is_feasible = False
            
            if max_consecutive is None or max_consecutive < 1:
                conflicts.append("max_consecutive must be a positive integer")
                is_feasible = False
        
        elif constraint_type == ConstraintType.MIN_DIVERSITY:
            min_unique_crops = parameters.get('min_unique_crops')
            if min_unique_crops is None or min_unique_crops < 2:
                conflicts.append("min_unique_crops must be at least 2")
                is_feasible = False
        
        return ConstraintValidationResult(
            constraint_id="validation",
            is_feasible=is_feasible,
            conflicts=conflicts,
            suggestions=suggestions,
            impact_assessment={}
        )
    
    def _prioritize_by_weighted_average(self, goals: List[RotationGoal]) -> List[RotationGoal]:
        """Prioritize goals using weighted average approach."""
        
        # Calculate composite scores
        for goal in goals:
            goal.composite_score = goal.priority * 0.6 + goal.weight * 40
        
        return sorted(goals, key=lambda g: g.composite_score, reverse=True)
    
    def _prioritize_lexicographically(self, goals: List[RotationGoal]) -> List[RotationGoal]:
        """Prioritize goals lexicographically (priority first, then weight)."""
        return sorted(goals, key=lambda g: (g.priority, g.weight), reverse=True)
    
    async def _prioritize_pareto_optimal(self, goals: List[RotationGoal]) -> List[RotationGoal]:
        """Find Pareto optimal goal configuration."""
        
        # Simplified Pareto optimization
        # In practice, this would involve more complex multi-objective optimization
        
        pareto_goals = []
        
        for goal in goals:
            is_dominated = False
            
            for other_goal in goals:
                if (other_goal.priority >= goal.priority and 
                    other_goal.weight >= goal.weight and
                    (other_goal.priority > goal.priority or other_goal.weight > goal.weight)):
                    is_dominated = True
                    break
            
            if not is_dominated:
                pareto_goals.append(goal)
        
        return sorted(pareto_goals, key=lambda g: g.priority, reverse=True)
    
    def _prioritize_by_farmer_preference(
        self,
        goals: List[RotationGoal],
        farmer_preferences: Optional[Dict[str, float]]
    ) -> List[RotationGoal]:
        """Prioritize goals based on farmer preferences."""
        
        if not farmer_preferences:
            return self._prioritize_by_weighted_average(goals)
        
        # Adjust goal weights based on farmer preferences
        for goal in goals:
            goal_type_key = goal.goal_type.value
            preference_multiplier = farmer_preferences.get(goal_type_key, 1.0)
            goal.adjusted_weight = goal.weight * preference_multiplier
        
        return sorted(goals, key=lambda g: g.adjusted_weight, reverse=True)
    
    def _get_goal_compatibility(self, goal1: RotationGoal, goal2: RotationGoal) -> float:
        """Get compatibility score between two goals."""
        
        goal1_key = self._get_template_key_for_goal_type(goal1.goal_type)
        goal2_key = self._get_template_key_for_goal_type(goal2.goal_type)
        
        compatibility_matrix = self.goal_compatibility_matrix.get(goal1_key, {})
        return compatibility_matrix.get(goal2_key, 0.5)  # Default neutral compatibility
    
    async def _resolve_goal_conflict(
        self,
        goal1: RotationGoal,
        goal2: RotationGoal,
        compatibility: float
    ) -> GoalConflictResolution:
        """Resolve conflict between two goals."""
        
        # Determine resolution strategy based on compatibility level
        if compatibility < 0.3:
            strategy = "weight_rebalancing"
            explanation = f"Significant conflict between {goal1.description} and {goal2.description}. Recommend rebalancing weights."
        elif compatibility < 0.6:
            strategy = "sequential_optimization"
            explanation = f"Moderate conflict detected. Consider sequential optimization approach."
        else:
            strategy = "minor_adjustment"
            explanation = f"Minor conflict. Small weight adjustments may improve compatibility."
        
        # Calculate weight adjustments
        weight_adjustments = {}
        
        if strategy == "weight_rebalancing":
            # Reduce weights proportionally
            total_weight = goal1.weight + goal2.weight
            weight_adjustments[goal1.goal_id] = goal1.weight * 0.8
            weight_adjustments[goal2.goal_id] = goal2.weight * 0.8
        
        elif strategy == "sequential_optimization":
            # Prioritize higher priority goal
            if goal1.priority > goal2.priority:
                weight_adjustments[goal1.goal_id] = goal1.weight * 1.1
                weight_adjustments[goal2.goal_id] = goal2.weight * 0.9
            else:
                weight_adjustments[goal1.goal_id] = goal1.weight * 0.9
                weight_adjustments[goal2.goal_id] = goal2.weight * 1.1
        
        return GoalConflictResolution(
            conflicting_goals=[goal1.goal_id, goal2.goal_id],
            resolution_strategy=strategy,
            weight_adjustments=weight_adjustments,
            explanation=explanation
        )
    
    def _measure_soil_health_achievement(
        self,
        goal: RotationGoal,
        rotation_results: Dict[str, Any]
    ) -> Tuple[float, float]:
        """Measure soil health goal achievement."""
        
        target_om_increase = goal.target_metrics.get('organic_matter_increase_percent', 10.0)
        achieved_om_increase = rotation_results.get('soil_health', {}).get('organic_matter_improvement', 0.0)
        
        return achieved_om_increase, target_om_increase
    
    def _measure_profit_achievement(
        self,
        goal: RotationGoal,
        rotation_results: Dict[str, Any]
    ) -> Tuple[float, float]:
        """Measure profit goal achievement."""
        
        target_roi = goal.target_metrics.get('min_roi_percent', 15.0)
        achieved_roi = rotation_results.get('economics', {}).get('roi_percent', 0.0)
        
        return achieved_roi, target_roi
    
    def _measure_pest_management_achievement(
        self,
        goal: RotationGoal,
        rotation_results: Dict[str, Any]
    ) -> Tuple[float, float]:
        """Measure pest management goal achievement."""
        
        target_reduction = goal.target_metrics.get('pest_pressure_reduction_percent', 30.0)
        achieved_reduction = rotation_results.get('benefits', {}).get('pest_pressure_reduction', 0.0)
        
        return achieved_reduction, target_reduction
    
    def _measure_sustainability_achievement(
        self,
        goal: RotationGoal,
        rotation_results: Dict[str, Any]
    ) -> Tuple[float, float]:
        """Measure sustainability goal achievement."""
        
        target_carbon = goal.target_metrics.get('carbon_sequestration_tons_per_acre', 0.5)
        achieved_carbon = rotation_results.get('sustainability', {}).get('carbon_sequestration_tons', 0.0)
        
        return achieved_carbon, target_carbon
    
    def _measure_risk_management_achievement(
        self,
        goal: RotationGoal,
        rotation_results: Dict[str, Any]
    ) -> Tuple[float, float]:
        """Measure risk management goal achievement."""
        
        target_cv = goal.target_metrics.get('yield_coefficient_variation', 0.15)
        achieved_cv = rotation_results.get('risks', {}).get('yield_variability_risk', 100.0) / 100.0
        
        # Lower coefficient of variation is better
        return max(0, target_cv - achieved_cv), target_cv
    
    async def _validate_single_constraint(
        self,
        constraint: RotationConstraint,
        field_profile: FieldProfile,
        available_crops: List[str]
    ) -> ConstraintValidationResult:
        """Validate a single constraint."""
        
        conflicts = []
        suggestions = []
        is_feasible = True
        impact_assessment = {}
        
        if constraint.constraint_type == ConstraintType.REQUIRED_CROP:
            crop_name = constraint.parameters.get('crop_name')
            
            if crop_name not in available_crops:
                conflicts.append(f"Required crop '{crop_name}' not available for this field")
                is_feasible = False
                suggestions.append(f"Consider alternative crops: {', '.join(available_crops[:3])}")
            
            # Check field suitability (simplified)
            if hasattr(field_profile, 'soil_type'):
                if crop_name == 'alfalfa' and field_profile.soil_type == 'poorly_drained':
                    conflicts.append("Alfalfa not suitable for poorly drained soils")
                    suggestions.append("Improve drainage or select alternative legume")
        
        elif constraint.constraint_type == ConstraintType.MIN_DIVERSITY:
            min_crops = constraint.parameters.get('min_unique_crops', 2)
            
            if len(available_crops) < min_crops:
                conflicts.append(f"Only {len(available_crops)} crops available, but {min_crops} required")
                is_feasible = False
                suggestions.append("Expand available crop options or reduce diversity requirement")
        
        return ConstraintValidationResult(
            constraint_id=constraint.constraint_id,
            is_feasible=is_feasible,
            conflicts=conflicts,
            suggestions=suggestions,
            impact_assessment=impact_assessment
        )
    
    async def _check_constraint_conflicts(
        self,
        constraints: List[RotationConstraint]
    ) -> List[ConstraintValidationResult]:
        """Check for conflicts between constraints."""
        
        conflict_results = []
        
        # Check for conflicting requirements
        required_crops = []
        excluded_crops = []
        
        for constraint in constraints:
            if constraint.constraint_type == ConstraintType.REQUIRED_CROP:
                crop_name = constraint.parameters.get('crop_name')
                if crop_name:
                    required_crops.append((crop_name, constraint.constraint_id))
            
            elif constraint.constraint_type == ConstraintType.EXCLUDED_CROP:
                crop_name = constraint.parameters.get('crop_name')
                if crop_name:
                    excluded_crops.append((crop_name, constraint.constraint_id))
        
        # Check for direct conflicts (required and excluded same crop)
        for req_crop, req_id in required_crops:
            for exc_crop, exc_id in excluded_crops:
                if req_crop == exc_crop:
                    conflict_result = ConstraintValidationResult(
                        constraint_id=f"conflict_{req_id}_{exc_id}",
                        is_feasible=False,
                        conflicts=[f"Crop '{req_crop}' is both required and excluded"],
                        suggestions=[f"Remove either requirement or exclusion for '{req_crop}'"],
                        impact_assessment={'severity': 'high'}
                    )
                    conflict_results.append(conflict_result)
        
        return conflict_results
    
    async def _analyze_goal_feasibility(
        self,
        goal: RotationGoal,
        constraints: List[RotationConstraint],
        field_profile: FieldProfile
    ) -> Dict[str, Any]:
        """Analyze feasibility of a goal given constraints and field conditions."""
        
        feasibility_analysis = {
            'is_feasible': True,
            'limiting_factors': [],
            'reasoning': '',
            'impact_assessment': {}
        }
        
        # Check if goal targets are realistic for field conditions
        if goal.goal_type == RotationGoalType.SOIL_HEALTH:
            target_om_increase = goal.target_metrics.get('organic_matter_increase_percent', 10.0)
            
            if target_om_increase > 25.0:  # Unrealistic target
                feasibility_analysis['is_feasible'] = False
                feasibility_analysis['limiting_factors'].append('unrealistic_organic_matter_target')
                feasibility_analysis['reasoning'] = f"Target organic matter increase of {target_om_increase}% is unrealistic for typical rotation periods"
        
        elif goal.goal_type == RotationGoalType.PROFIT_MAXIMIZATION:
            target_roi = goal.target_metrics.get('min_roi_percent', 15.0)
            
            if target_roi > 50.0:  # Very high ROI target
                feasibility_analysis['is_feasible'] = False
                feasibility_analysis['limiting_factors'].append('unrealistic_roi_target')
                feasibility_analysis['reasoning'] = f"Target ROI of {target_roi}% is very ambitious for agricultural operations"
        
        # Check constraint compatibility
        constraint_conflicts = 0
        for constraint in constraints:
            if constraint.constraint_type == ConstraintType.REQUIRED_CROP:
                crop_name = constraint.parameters.get('crop_name')
                
                # Check if required crop supports goal
                if goal.goal_type == RotationGoalType.SUSTAINABILITY and crop_name == 'corn':
                    constraint_conflicts += 1
                    feasibility_analysis['limiting_factors'].append('sustainability_crop_conflict')
        
        if constraint_conflicts > 0:
            feasibility_analysis['is_feasible'] = False
            feasibility_analysis['reasoning'] += f" {constraint_conflicts} constraint(s) conflict with goal objectives."
        
        return feasibility_analysis
    
    async def _generate_goal_adjustments(
        self,
        goal: RotationGoal,
        limiting_factors: List[str]
    ) -> Dict[str, Any]:
        """Generate adjustment suggestions for a goal."""
        
        adjustments = {
            'target_metric_adjustments': {},
            'weight_adjustments': {},
            'alternative_approaches': []
        }
        
        for factor in limiting_factors:
            if factor == 'unrealistic_organic_matter_target':
                current_target = goal.target_metrics.get('organic_matter_increase_percent', 10.0)
                adjusted_target = min(15.0, current_target * 0.7)
                adjustments['target_metric_adjustments']['organic_matter_increase_percent'] = adjusted_target
                adjustments['alternative_approaches'].append('Focus on erosion reduction as primary soil health metric')
            
            elif factor == 'unrealistic_roi_target':
                current_target = goal.target_metrics.get('min_roi_percent', 15.0)
                adjusted_target = min(25.0, current_target * 0.8)
                adjustments['target_metric_adjustments']['min_roi_percent'] = adjusted_target
                adjustments['alternative_approaches'].append('Consider risk-adjusted returns instead of absolute ROI')
            
            elif factor == 'sustainability_crop_conflict':
                adjustments['weight_adjustments']['reduce_weight'] = 0.8
                adjustments['alternative_approaches'].append('Balance sustainability with economic constraints')
        
        return adjustments
    
    async def _optimize_for_balance(
        self,
        goals: List[RotationGoal],
        constraints: List[RotationConstraint]
    ) -> Dict[str, float]:
        """Optimize goal weights for balanced performance."""
        
        # Equal weighting adjusted for goal compatibility
        base_weight = 1.0 / len(goals)
        optimized_weights = {}
        
        for goal in goals:
            # Adjust weight based on goal type importance in balanced approach
            if goal.goal_type == RotationGoalType.SOIL_HEALTH:
                weight_multiplier = 1.1  # Slightly favor soil health
            elif goal.goal_type == RotationGoalType.PROFIT_MAXIMIZATION:
                weight_multiplier = 1.0  # Neutral
            elif goal.goal_type == RotationGoalType.SUSTAINABILITY:
                weight_multiplier = 1.05  # Slightly favor sustainability
            else:
                weight_multiplier = 0.95
            
            optimized_weights[goal.goal_id] = base_weight * weight_multiplier
        
        return optimized_weights
    
    async def _optimize_for_profit(
        self,
        goals: List[RotationGoal],
        constraints: List[RotationConstraint]
    ) -> Dict[str, float]:
        """Optimize goal weights for profit focus."""
        
        optimized_weights = {}
        
        for goal in goals:
            if goal.goal_type == RotationGoalType.PROFIT_MAXIMIZATION:
                optimized_weights[goal.goal_id] = 0.5  # High weight for profit
            elif goal.goal_type == RotationGoalType.RISK_MANAGEMENT:
                optimized_weights[goal.goal_id] = 0.2  # Risk management supports profit
            elif goal.goal_type == RotationGoalType.OPERATIONAL_EFFICIENCY:
                optimized_weights[goal.goal_id] = 0.15  # Efficiency supports profit
            else:
                optimized_weights[goal.goal_id] = 0.15 / (len(goals) - 3)  # Distribute remaining
        
        return optimized_weights
    
    async def _optimize_for_sustainability(
        self,
        goals: List[RotationGoal],
        constraints: List[RotationConstraint]
    ) -> Dict[str, float]:
        """Optimize goal weights for sustainability focus."""
        
        optimized_weights = {}
        
        for goal in goals:
            if goal.goal_type == RotationGoalType.SUSTAINABILITY:
                optimized_weights[goal.goal_id] = 0.4  # High weight for sustainability
            elif goal.goal_type == RotationGoalType.SOIL_HEALTH:
                optimized_weights[goal.goal_id] = 0.3  # Soil health supports sustainability
            elif goal.goal_type == RotationGoalType.PEST_MANAGEMENT:
                optimized_weights[goal.goal_id] = 0.2  # Natural pest management
            else:
                optimized_weights[goal.goal_id] = 0.1 / (len(goals) - 3)  # Distribute remaining
        
        return optimized_weights