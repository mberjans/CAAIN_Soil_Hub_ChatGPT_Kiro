"""
Dynamic Programming Optimizer for Fertilizer Timing

This module implements a dynamic programming algorithm for optimal fertilizer
application timing that considers state transitions, weather conditions, crop
growth stages, and resource constraints.

Mathematical Formulation:
    V(t, s) = max_{a in A(t,s)} [R(t, s, a) + γ * V(t+1, s')]

    Where:
    - V(t, s) is the value function at time t and state s
    - A(t, s) is the set of feasible actions (application decisions)
    - R(t, s, a) is the immediate reward for action a
    - γ is the discount factor
    - s' is the next state after applying action a
"""

import logging
import numpy as np
from datetime import date, timedelta
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass

from ..models.timing_optimization_models import (
    TimingOptimizationRequest,
    WeatherWindow,
    CropGrowthStage,
    ApplicationMethod,
    WeatherCondition
)

logger = logging.getLogger(__name__)


@dataclass
class State:
    """Represents the state of the system at a given time."""
    date: date
    crop_stage: CropGrowthStage
    soil_moisture: float
    available_budget: float
    applied_fertilizers: Dict[str, float]
    weather_condition: WeatherCondition

    def __hash__(self):
        """Make state hashable for memoization."""
        return hash((
            self.date,
            self.crop_stage,
            round(self.soil_moisture, 2),
            round(self.available_budget, 2),
            tuple(sorted(self.applied_fertilizers.items())),
            self.weather_condition
        ))

    def __eq__(self, other):
        """State equality for memoization."""
        if not isinstance(other, State):
            return False
        return self.__hash__() == other.__hash__()


@dataclass
class Action:
    """Represents an action (fertilizer application decision)."""
    fertilizer_type: str
    amount: float
    method: ApplicationMethod
    apply: bool  # True to apply, False to wait

    def __repr__(self):
        if not self.apply:
            return "Wait"
        return f"Apply {self.amount} lbs/acre of {self.fertilizer_type} via {self.method}"


@dataclass
class DPResult:
    """Result from dynamic programming optimization."""
    optimal_schedule: List[Tuple[date, Action]]
    total_value: float
    value_breakdown: Dict[str, float]
    state_trajectory: List[State]
    confidence_score: float


class DynamicProgrammingOptimizer:
    """
    Dynamic Programming optimizer for fertilizer timing.

    This optimizer uses backward induction to find the optimal sequence of
    fertilizer applications that maximizes cumulative benefit while respecting
    constraints on budget, equipment, labor, and environmental factors.
    """

    def __init__(
        self,
        discount_factor: float = 0.98,
        max_horizon_days: int = 365,
        state_discretization: int = 10
    ):
        """
        Initialize the DP optimizer.

        Args:
            discount_factor: Temporal discount factor (γ) for future rewards
            max_horizon_days: Maximum optimization horizon in days
            state_discretization: Number of discrete levels for continuous states
        """
        self.discount_factor = discount_factor
        self.max_horizon_days = max_horizon_days
        self.state_discretization = state_discretization

        # Memoization cache for value function
        self.value_cache: Dict[State, float] = {}
        self.policy_cache: Dict[State, Action] = {}

        # Reward weights for multi-objective optimization
        self.reward_weights = {
            "yield_benefit": 0.40,
            "cost_efficiency": 0.25,
            "environmental_impact": 0.20,
            "risk_mitigation": 0.15
        }

    def optimize(
        self,
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow],
        crop_stages: Dict[date, CropGrowthStage]
    ) -> DPResult:
        """
        Optimize fertilizer timing using dynamic programming.

        Args:
            request: Optimization request with field and crop data
            weather_windows: Available weather windows for application
            crop_stages: Crop growth stages by date

        Returns:
            DPResult with optimal schedule and metrics
        """
        logger.info("Starting dynamic programming optimization")

        # Initialize state space
        initial_state = self._create_initial_state(request, weather_windows, crop_stages)

        # Clear caches for new optimization
        self.value_cache.clear()
        self.policy_cache.clear()

        # Solve using backward induction
        optimal_value = self._value_function(initial_state, request, weather_windows, crop_stages, 0)

        # Extract optimal policy by forward simulation
        optimal_schedule, state_trajectory = self._extract_optimal_policy(
            initial_state, request, weather_windows, crop_stages
        )

        # Calculate value breakdown
        value_breakdown = self._calculate_value_breakdown(
            optimal_schedule, state_trajectory, request
        )

        # Calculate confidence score
        confidence = self._calculate_confidence(optimal_value, state_trajectory)

        logger.info(f"DP optimization complete. Optimal value: {optimal_value:.2f}")

        return DPResult(
            optimal_schedule=optimal_schedule,
            total_value=optimal_value,
            value_breakdown=value_breakdown,
            state_trajectory=state_trajectory,
            confidence_score=confidence
        )

    def _create_initial_state(
        self,
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow],
        crop_stages: Dict[date, CropGrowthStage]
    ) -> State:
        """Create initial state from request."""
        initial_weather = weather_windows[0] if weather_windows else None
        initial_crop_stage = crop_stages.get(request.planting_date, CropGrowthStage.PLANTING)

        return State(
            date=request.planting_date,
            crop_stage=initial_crop_stage,
            soil_moisture=initial_weather.soil_moisture if initial_weather else request.soil_moisture_capacity,
            available_budget=request.budget_constraints.get("total", 10000.0) if request.budget_constraints else 10000.0,
            applied_fertilizers={},
            weather_condition=initial_weather.condition if initial_weather else WeatherCondition.ACCEPTABLE
        )

    def _value_function(
        self,
        state: State,
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow],
        crop_stages: Dict[date, CropGrowthStage],
        depth: int
    ) -> float:
        """
        Recursive value function with memoization.

        V(t, s) = max_{a in A(t,s)} [R(t, s, a) + γ * V(t+1, s')]
        """
        # Check memoization cache
        if state in self.value_cache:
            return self.value_cache[state]

        # Base case: end of horizon or maximum depth
        if depth >= self.max_horizon_days:
            return 0.0

        # Check if all fertilizers have been applied
        all_applied = True
        for fertilizer_type, required_amount in request.fertilizer_requirements.items():
            applied_amount = state.applied_fertilizers.get(fertilizer_type, 0.0)
            if applied_amount < required_amount:
                all_applied = False
                break

        if all_applied:
            return 0.0  # Terminal state

        # Generate feasible actions for current state
        feasible_actions = self._generate_feasible_actions(state, request, weather_windows)

        if not feasible_actions:
            # No feasible actions, move to next day with wait action
            next_state = self._transition(state, Action("", 0, ApplicationMethod.BROADCAST, False),
                                         request, weather_windows, crop_stages)
            future_value = self._value_function(next_state, request, weather_windows, crop_stages, depth + 1)
            self.value_cache[state] = self.discount_factor * future_value
            self.policy_cache[state] = Action("", 0, ApplicationMethod.BROADCAST, False)
            return self.value_cache[state]

        # Evaluate each action and select the best
        max_value = float('-inf')
        best_action = None

        for action in feasible_actions:
            # Calculate immediate reward
            immediate_reward = self._calculate_reward(state, action, request, weather_windows)

            # Calculate next state
            next_state = self._transition(state, action, request, weather_windows, crop_stages)

            # Recursive call for future value
            future_value = self._value_function(next_state, request, weather_windows, crop_stages, depth + 1)

            # Total value for this action
            total_value = immediate_reward + self.discount_factor * future_value

            if total_value > max_value:
                max_value = total_value
                best_action = action

        # Memoize and return
        self.value_cache[state] = max_value
        self.policy_cache[state] = best_action

        return max_value

    def _generate_feasible_actions(
        self,
        state: State,
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow]
    ) -> List[Action]:
        """Generate all feasible actions from current state."""
        actions = []

        # Always include wait action
        actions.append(Action("", 0, ApplicationMethod.BROADCAST, False))

        # Check if current conditions allow application
        if state.weather_condition == WeatherCondition.UNACCEPTABLE:
            return actions  # Can only wait

        # Generate application actions for each fertilizer type
        for fertilizer_type, total_required in request.fertilizer_requirements.items():
            applied_so_far = state.applied_fertilizers.get(fertilizer_type, 0.0)
            remaining = total_required - applied_so_far

            if remaining > 0:
                # Consider different application amounts
                for fraction in [0.25, 0.33, 0.5, 0.67, 1.0]:
                    amount = remaining * fraction

                    # Check budget constraint
                    estimated_cost = self._estimate_application_cost(fertilizer_type, amount, request)
                    if estimated_cost <= state.available_budget:
                        # Consider each application method
                        for method in request.application_methods:
                            action = Action(fertilizer_type, amount, method, True)
                            actions.append(action)

        return actions

    def _transition(
        self,
        state: State,
        action: Action,
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow],
        crop_stages: Dict[date, CropGrowthStage]
    ) -> State:
        """Calculate next state given current state and action."""
        next_date = state.date + timedelta(days=1)

        # Update applied fertilizers
        new_applied = state.applied_fertilizers.copy()
        if action.apply:
            current_amount = new_applied.get(action.fertilizer_type, 0.0)
            new_applied[action.fertilizer_type] = current_amount + action.amount

        # Update budget
        cost = self._estimate_application_cost(action.fertilizer_type, action.amount, request) if action.apply else 0.0
        new_budget = state.available_budget - cost

        # Get next crop stage
        next_crop_stage = crop_stages.get(next_date, state.crop_stage)

        # Get next weather condition
        next_weather = self._get_weather_for_date(next_date, weather_windows)
        next_condition = next_weather.condition if next_weather else WeatherCondition.ACCEPTABLE
        next_moisture = next_weather.soil_moisture if next_weather else state.soil_moisture

        return State(
            date=next_date,
            crop_stage=next_crop_stage,
            soil_moisture=next_moisture,
            available_budget=new_budget,
            applied_fertilizers=new_applied,
            weather_condition=next_condition
        )

    def _calculate_reward(
        self,
        state: State,
        action: Action,
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow]
    ) -> float:
        """
        Calculate immediate reward for taking action in state.

        Reward components:
        1. Yield benefit from proper timing
        2. Cost efficiency
        3. Environmental impact (negative for poor conditions)
        4. Risk mitigation
        """
        if not action.apply:
            return 0.0  # Wait action has zero immediate reward

        # 1. Yield benefit: higher for optimal crop stages
        yield_benefit = self._calculate_yield_benefit(state, action, request)

        # 2. Cost efficiency: penalize expensive applications
        cost_efficiency = self._calculate_cost_efficiency(state, action, request)

        # 3. Environmental impact: penalize applications in poor conditions
        env_impact = self._calculate_environmental_impact(state, action, request)

        # 4. Risk mitigation: reward for reducing future uncertainty
        risk_mitigation = self._calculate_risk_mitigation(state, action, request)

        # Combine weighted rewards
        total_reward = (
            self.reward_weights["yield_benefit"] * yield_benefit +
            self.reward_weights["cost_efficiency"] * cost_efficiency +
            self.reward_weights["environmental_impact"] * env_impact +
            self.reward_weights["risk_mitigation"] * risk_mitigation
        )

        return total_reward

    def _calculate_yield_benefit(
        self,
        state: State,
        action: Action,
        request: TimingOptimizationRequest
    ) -> float:
        """Calculate yield benefit from application at current crop stage."""
        # Crop stage alignment score
        optimal_stages = {
            CropGrowthStage.PLANTING: 1.0,
            CropGrowthStage.V4: 0.95,
            CropGrowthStage.V6: 0.90,
            CropGrowthStage.V8: 0.85,
            CropGrowthStage.VT: 0.80,
            CropGrowthStage.R1: 0.70
        }
        stage_score = optimal_stages.get(state.crop_stage, 0.5)

        # Weather condition multiplier
        weather_multipliers = {
            WeatherCondition.OPTIMAL: 1.0,
            WeatherCondition.ACCEPTABLE: 0.85,
            WeatherCondition.MARGINAL: 0.65,
            WeatherCondition.POOR: 0.40,
            WeatherCondition.UNACCEPTABLE: 0.0
        }
        weather_mult = weather_multipliers.get(state.weather_condition, 0.5)

        # Soil moisture factor
        optimal_moisture = 0.6
        moisture_factor = 1.0 - abs(state.soil_moisture - optimal_moisture)

        # Combine factors (normalized to 0-100)
        benefit = 100.0 * stage_score * weather_mult * moisture_factor * (action.amount / 100.0)

        return benefit

    def _calculate_cost_efficiency(
        self,
        state: State,
        action: Action,
        request: TimingOptimizationRequest
    ) -> float:
        """Calculate cost efficiency of application."""
        cost = self._estimate_application_cost(action.fertilizer_type, action.amount, request)

        # Normalize cost to 0-100 scale (higher is better, so invert)
        # Assume typical cost is around $50-200 per application
        efficiency = 100.0 * (1.0 - min(1.0, cost / 200.0))

        return efficiency

    def _calculate_environmental_impact(
        self,
        state: State,
        action: Action,
        request: TimingOptimizationRequest
    ) -> float:
        """Calculate environmental impact (negative for poor conditions)."""
        # Penalize applications in poor weather conditions
        condition_penalties = {
            WeatherCondition.OPTIMAL: 0.0,
            WeatherCondition.ACCEPTABLE: -5.0,
            WeatherCondition.MARGINAL: -20.0,
            WeatherCondition.POOR: -50.0,
            WeatherCondition.UNACCEPTABLE: -100.0
        }
        penalty = condition_penalties.get(state.weather_condition, -10.0)

        # Penalize large applications on slopes (runoff risk)
        if request.slope_percent > 5.0:
            slope_penalty = -10.0 * (request.slope_percent / 10.0) * (action.amount / 100.0)
        else:
            slope_penalty = 0.0

        # Reward for good soil moisture
        moisture_bonus = 10.0 if 0.4 <= state.soil_moisture <= 0.7 else 0.0

        impact = penalty + slope_penalty + moisture_bonus

        return impact

    def _calculate_risk_mitigation(
        self,
        state: State,
        action: Action,
        request: TimingOptimizationRequest
    ) -> float:
        """Calculate risk mitigation from application."""
        # Split applications reduce risk
        total_required = request.fertilizer_requirements.get(action.fertilizer_type, 0.0)
        if action.amount < total_required:
            split_bonus = 20.0
        else:
            split_bonus = 0.0

        # Early applications reduce weather uncertainty risk
        days_from_planting = (state.date - request.planting_date).days
        early_bonus = max(0.0, 10.0 * (1.0 - days_from_planting / 60.0))

        mitigation = split_bonus + early_bonus

        return mitigation

    def _extract_optimal_policy(
        self,
        initial_state: State,
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow],
        crop_stages: Dict[date, CropGrowthStage]
    ) -> Tuple[List[Tuple[date, Action]], List[State]]:
        """Extract optimal policy by forward simulation using cached policy."""
        schedule = []
        trajectory = [initial_state]

        current_state = initial_state

        for _ in range(self.max_horizon_days):
            # Check termination
            all_applied = True
            for fertilizer_type, required_amount in request.fertilizer_requirements.items():
                applied_amount = current_state.applied_fertilizers.get(fertilizer_type, 0.0)
                if applied_amount < required_amount * 0.99:  # 99% threshold
                    all_applied = False
                    break

            if all_applied:
                break

            # Get optimal action from policy cache
            if current_state in self.policy_cache:
                action = self.policy_cache[current_state]
            else:
                # Default to wait if not in cache
                action = Action("", 0, ApplicationMethod.BROADCAST, False)

            # Record action if it's an application
            if action.apply:
                schedule.append((current_state.date, action))

            # Transition to next state
            current_state = self._transition(current_state, action, request, weather_windows, crop_stages)
            trajectory.append(current_state)

        return schedule, trajectory

    def _calculate_value_breakdown(
        self,
        schedule: List[Tuple[date, Action]],
        trajectory: List[State],
        request: TimingOptimizationRequest
    ) -> Dict[str, float]:
        """Calculate breakdown of value components."""
        breakdown = {
            "yield_benefit": 0.0,
            "cost_efficiency": 0.0,
            "environmental_impact": 0.0,
            "risk_mitigation": 0.0
        }

        for i, (application_date, action) in enumerate(schedule):
            if i < len(trajectory):
                state = trajectory[i]

                breakdown["yield_benefit"] += self._calculate_yield_benefit(state, action, request)
                breakdown["cost_efficiency"] += self._calculate_cost_efficiency(state, action, request)
                breakdown["environmental_impact"] += self._calculate_environmental_impact(state, action, request)
                breakdown["risk_mitigation"] += self._calculate_risk_mitigation(state, action, request)

        return breakdown

    def _calculate_confidence(
        self,
        optimal_value: float,
        trajectory: List[State]
    ) -> float:
        """Calculate confidence score for the solution."""
        # Base confidence on value and trajectory stability
        value_confidence = min(1.0, max(0.0, optimal_value / 100.0))

        # Trajectory stability: penalize if many states are uncertain
        stable_states = sum(1 for s in trajectory if s.weather_condition in [
            WeatherCondition.OPTIMAL, WeatherCondition.ACCEPTABLE
        ])
        trajectory_confidence = stable_states / max(1, len(trajectory))

        confidence = 0.6 * value_confidence + 0.4 * trajectory_confidence

        return min(0.95, max(0.5, confidence))

    def _estimate_application_cost(
        self,
        fertilizer_type: str,
        amount: float,
        request: TimingOptimizationRequest
    ) -> float:
        """Estimate cost of fertilizer application."""
        base_costs = {
            "nitrogen": 0.5,  # $/lb
            "phosphorus": 0.8,
            "potassium": 0.6,
            "complete": 0.7
        }

        cost_per_lb = base_costs.get(fertilizer_type.lower(), 0.6)
        return amount * cost_per_lb

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
