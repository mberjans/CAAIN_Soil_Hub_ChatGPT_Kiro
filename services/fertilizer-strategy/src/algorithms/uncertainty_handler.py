"""
Uncertainty Handler for Fertilizer Timing Optimization

This module handles uncertainty in fertilizer timing optimization by modeling
stochastic elements including weather forecasts, crop growth predictions, and
market conditions. It provides probabilistic optimization and confidence intervals.

Uncertainty Sources:
    1. Weather forecast uncertainty (increases with time horizon)
    2. Crop growth stage prediction uncertainty
    3. Yield response uncertainty
    4. Price and cost uncertainty

Approaches:
    - Monte Carlo simulation for uncertainty propagation
    - Stochastic programming for robust optimization
    - Scenario-based analysis
    - Confidence interval estimation
"""

import logging
import numpy as np
from datetime import date, timedelta
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from scipy import stats

from ..models.timing_optimization_models import (
    TimingOptimizationRequest,
    WeatherWindow,
    CropGrowthStage,
    ApplicationMethod,
    WeatherCondition
)

logger = logging.getLogger(__name__)


@dataclass
class UncertaintyParameters:
    """Parameters for uncertainty modeling."""
    weather_forecast_uncertainty: float  # Std dev for weather predictions
    crop_growth_uncertainty: float  # Std dev for growth stage timing (days)
    yield_response_uncertainty: float  # Std dev for yield predictions
    price_uncertainty: float  # Std dev for price variations
    weather_correlation: float  # Temporal correlation in weather


@dataclass
class ProbabilisticOutcome:
    """Probabilistic outcome with confidence intervals."""
    mean_value: float
    std_dev: float
    confidence_95: Tuple[float, float]
    confidence_90: Tuple[float, float]
    confidence_80: Tuple[float, float]
    probability_success: float


@dataclass
class Scenario:
    """A scenario representing one possible future state."""
    scenario_id: int
    weather_realization: List[WeatherWindow]
    crop_stage_delays: Dict[CropGrowthStage, int]  # Delays in days
    yield_multiplier: float
    cost_multiplier: float
    probability: float


@dataclass
class UncertaintyResult:
    """Result from uncertainty analysis."""
    mean_outcome: Dict[str, float]
    confidence_intervals: Dict[str, ProbabilisticOutcome]
    scenarios: List[Scenario]
    risk_metrics: Dict[str, float]
    robust_recommendation: List[Tuple[date, str, float, ApplicationMethod]]
    sensitivity_analysis: Dict[str, float]


class UncertaintyHandler:
    """
    Handles uncertainty in fertilizer timing optimization.

    This class provides probabilistic optimization under uncertainty using
    Monte Carlo simulation, scenario analysis, and robust optimization
    techniques to generate reliable recommendations with quantified risk.
    """

    def __init__(
        self,
        num_scenarios: int = 1000,
        confidence_level: float = 0.95,
        risk_aversion: float = 0.5,
        forecast_horizon_days: int = 14
    ):
        """
        Initialize the uncertainty handler.

        Args:
            num_scenarios: Number of scenarios for Monte Carlo simulation
            confidence_level: Confidence level for intervals (0-1)
            risk_aversion: Risk aversion parameter (0=risk-neutral, 1=risk-averse)
            forecast_horizon_days: Weather forecast reliable horizon
        """
        self.num_scenarios = num_scenarios
        self.confidence_level = confidence_level
        self.risk_aversion = risk_aversion
        self.forecast_horizon_days = forecast_horizon_days

        # Default uncertainty parameters
        self.uncertainty_params = UncertaintyParameters(
            weather_forecast_uncertainty=0.15,  # 15% std dev
            crop_growth_uncertainty=2.0,  # 2 days std dev
            yield_response_uncertainty=0.10,  # 10% std dev
            price_uncertainty=0.08,  # 8% std dev
            weather_correlation=0.7  # 70% correlation across days
        )

    def analyze_uncertainty(
        self,
        request: TimingOptimizationRequest,
        base_schedule: List[Tuple[date, str, float, ApplicationMethod]],
        weather_windows: List[WeatherWindow],
        crop_stages: Dict[date, CropGrowthStage]
    ) -> UncertaintyResult:
        """
        Analyze uncertainty for a given schedule.

        Args:
            request: Optimization request
            base_schedule: Base timing schedule to analyze
            weather_windows: Deterministic weather windows
            crop_stages: Deterministic crop growth stages

        Returns:
            UncertaintyResult with probabilistic analysis
        """
        logger.info(f"Starting uncertainty analysis with {self.num_scenarios} scenarios")

        # Generate scenarios
        scenarios = self._generate_scenarios(weather_windows, crop_stages)

        # Evaluate schedule under each scenario
        scenario_outcomes = []
        for scenario in scenarios:
            outcome = self._evaluate_scenario(
                base_schedule, scenario, request
            )
            scenario_outcomes.append(outcome)

        # Calculate statistics
        mean_outcome = self._calculate_mean_outcome(scenario_outcomes, scenarios)
        confidence_intervals = self._calculate_confidence_intervals(scenario_outcomes)
        risk_metrics = self._calculate_risk_metrics(scenario_outcomes, scenarios)

        # Generate robust recommendation
        robust_schedule = self._generate_robust_schedule(
            request, scenarios, weather_windows, crop_stages
        )

        # Sensitivity analysis
        sensitivity = self._perform_sensitivity_analysis(
            base_schedule, request, weather_windows, crop_stages
        )

        logger.info("Uncertainty analysis complete")

        return UncertaintyResult(
            mean_outcome=mean_outcome,
            confidence_intervals=confidence_intervals,
            scenarios=scenarios[:100],  # Return subset for efficiency
            risk_metrics=risk_metrics,
            robust_recommendation=robust_schedule,
            sensitivity_analysis=sensitivity
        )

    def _generate_scenarios(
        self,
        base_weather: List[WeatherWindow],
        base_crop_stages: Dict[date, CropGrowthStage]
    ) -> List[Scenario]:
        """Generate scenarios using Monte Carlo sampling."""
        scenarios = []

        for i in range(self.num_scenarios):
            # Generate weather realizations with uncertainty
            weather_realization = self._generate_weather_realization(base_weather, i)

            # Generate crop stage delays
            crop_delays = self._generate_crop_delays(base_crop_stages)

            # Generate yield and cost multipliers
            yield_mult = np.random.normal(1.0, self.uncertainty_params.yield_response_uncertainty)
            cost_mult = np.random.normal(1.0, self.uncertainty_params.price_uncertainty)

            # Ensure multipliers are positive
            yield_mult = max(0.5, min(1.5, yield_mult))
            cost_mult = max(0.8, min(1.2, cost_mult))

            scenario = Scenario(
                scenario_id=i,
                weather_realization=weather_realization,
                crop_stage_delays=crop_delays,
                yield_multiplier=yield_mult,
                cost_multiplier=cost_mult,
                probability=1.0 / self.num_scenarios
            )
            scenarios.append(scenario)

        return scenarios

    def _generate_weather_realization(
        self,
        base_weather: List[WeatherWindow],
        seed: int
    ) -> List[WeatherWindow]:
        """Generate a weather realization with uncertainty."""
        np.random.seed(seed)

        realized_weather = []

        for i, base_window in enumerate(base_weather):
            # Uncertainty increases with forecast horizon
            days_ahead = i
            uncertainty_factor = 1.0 + (days_ahead / self.forecast_horizon_days) * 0.5

            # Temperature uncertainty
            temp_std = 5.0 * uncertainty_factor
            temp_noise = np.random.normal(0, temp_std)
            new_temp = base_window.temperature_f + temp_noise

            # Precipitation probability uncertainty
            precip_std = 0.1 * uncertainty_factor
            precip_noise = np.random.normal(0, precip_std)
            new_precip_prob = np.clip(base_window.precipitation_probability + precip_noise, 0.0, 1.0)

            # Wind speed uncertainty
            wind_std = 3.0 * uncertainty_factor
            wind_noise = np.random.normal(0, wind_std)
            new_wind = max(0.0, base_window.wind_speed_mph + wind_noise)

            # Soil moisture uncertainty
            moisture_std = 0.1 * uncertainty_factor
            moisture_noise = np.random.normal(0, moisture_std)
            new_moisture = np.clip(base_window.soil_moisture + moisture_noise, 0.0, 1.0)

            # Reassess weather condition based on new parameters
            new_condition = self._assess_weather_condition(
                new_temp, new_precip_prob, new_wind, new_moisture
            )

            # Recalculate suitability score
            new_suitability = self._calculate_suitability(new_condition, new_precip_prob)

            realized_window = WeatherWindow(
                start_date=base_window.start_date,
                end_date=base_window.end_date,
                condition=new_condition,
                temperature_f=new_temp,
                precipitation_probability=new_precip_prob,
                wind_speed_mph=new_wind,
                soil_moisture=new_moisture,
                suitability_score=new_suitability
            )
            realized_weather.append(realized_window)

        return realized_weather

    def _generate_crop_delays(
        self,
        base_crop_stages: Dict[date, CropGrowthStage]
    ) -> Dict[CropGrowthStage, int]:
        """Generate random delays for crop growth stages."""
        delays = {}

        for stage in base_crop_stages.values():
            delay = int(np.random.normal(0, self.uncertainty_params.crop_growth_uncertainty))
            delay = max(-5, min(5, delay))  # Limit delays to +/- 5 days
            delays[stage] = delay

        return delays

    def _evaluate_scenario(
        self,
        schedule: List[Tuple[date, str, float, ApplicationMethod]],
        scenario: Scenario,
        request: TimingOptimizationRequest
    ) -> Dict[str, float]:
        """Evaluate a schedule under a specific scenario."""
        total_yield = 0.0
        total_cost = 0.0
        total_env_impact = 0.0
        application_count = len(schedule)

        base_costs = {
            "nitrogen": 0.50,
            "phosphorus": 0.80,
            "potassium": 0.60,
            "complete": 0.70
        }

        for app_date, fertilizer_type, amount, method in schedule:
            # Get weather for this date in scenario
            weather = self._get_weather_for_date(app_date, scenario.weather_realization)

            if weather:
                # Yield impact (affected by weather and scenario multiplier)
                weather_yield_factor = {
                    WeatherCondition.OPTIMAL: 1.0,
                    WeatherCondition.ACCEPTABLE: 0.85,
                    WeatherCondition.MARGINAL: 0.65,
                    WeatherCondition.POOR: 0.40,
                    WeatherCondition.UNACCEPTABLE: 0.20
                }.get(weather.condition, 0.7)

                yield_contribution = amount * weather_yield_factor * scenario.yield_multiplier
                total_yield += yield_contribution

                # Environmental impact (worse in poor weather)
                env_penalty = {
                    WeatherCondition.OPTIMAL: 0.0,
                    WeatherCondition.ACCEPTABLE: 5.0,
                    WeatherCondition.MARGINAL: 15.0,
                    WeatherCondition.POOR: 30.0,
                    WeatherCondition.UNACCEPTABLE: 50.0
                }.get(weather.condition, 10.0)
                total_env_impact += env_penalty

            # Cost (affected by scenario multiplier)
            cost_per_lb = base_costs.get(fertilizer_type.lower(), 0.60)
            application_cost = 10.0
            total_cost += (amount * cost_per_lb + application_cost) * scenario.cost_multiplier

        # Normalize outcomes
        yield_score = min(100.0, total_yield / max(1, application_count))
        cost_score = max(0.0, 100.0 - total_cost / 2.0)
        env_score = max(0.0, 100.0 - total_env_impact)

        return {
            "yield": yield_score,
            "cost": cost_score,
            "environment": env_score,
            "total_benefit": yield_score + cost_score + env_score
        }

    def _calculate_mean_outcome(
        self,
        outcomes: List[Dict[str, float]],
        scenarios: List[Scenario]
    ) -> Dict[str, float]:
        """Calculate mean outcome across scenarios."""
        mean_outcome = {}

        for key in outcomes[0].keys():
            weighted_sum = sum(
                outcome[key] * scenario.probability
                for outcome, scenario in zip(outcomes, scenarios)
            )
            mean_outcome[key] = weighted_sum

        return mean_outcome

    def _calculate_confidence_intervals(
        self,
        outcomes: List[Dict[str, float]]
    ) -> Dict[str, ProbabilisticOutcome]:
        """Calculate confidence intervals for outcomes."""
        confidence_intervals = {}

        for key in outcomes[0].keys():
            values = [outcome[key] for outcome in outcomes]

            mean_val = np.mean(values)
            std_val = np.std(values)

            # Calculate confidence intervals
            ci_95 = stats.norm.interval(0.95, loc=mean_val, scale=std_val)
            ci_90 = stats.norm.interval(0.90, loc=mean_val, scale=std_val)
            ci_80 = stats.norm.interval(0.80, loc=mean_val, scale=std_val)

            # Probability of success (outcome > threshold)
            threshold = mean_val * 0.9  # 90% of mean
            prob_success = sum(1 for v in values if v > threshold) / len(values)

            confidence_intervals[key] = ProbabilisticOutcome(
                mean_value=mean_val,
                std_dev=std_val,
                confidence_95=ci_95,
                confidence_90=ci_90,
                confidence_80=ci_80,
                probability_success=prob_success
            )

        return confidence_intervals

    def _calculate_risk_metrics(
        self,
        outcomes: List[Dict[str, float]],
        scenarios: List[Scenario]
    ) -> Dict[str, float]:
        """Calculate risk metrics for the schedule."""
        benefits = [outcome["total_benefit"] for outcome in outcomes]

        # Value at Risk (VaR) - 5th percentile
        var_5 = np.percentile(benefits, 5)

        # Conditional Value at Risk (CVaR) - mean of worst 5%
        worst_5_percent = sorted(benefits)[:max(1, int(0.05 * len(benefits)))]
        cvar_5 = np.mean(worst_5_percent) if worst_5_percent else 0.0

        # Downside risk - std dev of outcomes below mean
        mean_benefit = np.mean(benefits)
        downside_deviations = [b - mean_benefit for b in benefits if b < mean_benefit]
        downside_risk = np.std(downside_deviations) if downside_deviations else 0.0

        # Sharpe-like ratio
        sharpe_ratio = mean_benefit / max(0.1, np.std(benefits))

        return {
            "value_at_risk_5": var_5,
            "conditional_var_5": cvar_5,
            "downside_risk": downside_risk,
            "sharpe_ratio": sharpe_ratio,
            "volatility": np.std(benefits)
        }

    def _generate_robust_schedule(
        self,
        request: TimingOptimizationRequest,
        scenarios: List[Scenario],
        base_weather: List[WeatherWindow],
        base_crop_stages: Dict[date, CropGrowthStage]
    ) -> List[Tuple[date, str, float, ApplicationMethod]]:
        """Generate robust schedule that performs well across scenarios."""
        # Evaluate multiple candidate schedules
        candidate_schedules = self._generate_candidate_schedules(
            request, base_weather, base_crop_stages
        )

        best_schedule = None
        best_robust_score = -float('inf')

        for schedule in candidate_schedules:
            # Evaluate across all scenarios
            scenario_outcomes = []
            for scenario in scenarios:
                outcome = self._evaluate_scenario(schedule, scenario, request)
                scenario_outcomes.append(outcome["total_benefit"])

            # Robust score considers mean and worst-case
            mean_score = np.mean(scenario_outcomes)
            worst_case = np.percentile(scenario_outcomes, 10)  # 10th percentile

            # Risk-adjusted score
            robust_score = (1.0 - self.risk_aversion) * mean_score + self.risk_aversion * worst_case

            if robust_score > best_robust_score:
                best_robust_score = robust_score
                best_schedule = schedule

        return best_schedule if best_schedule else []

    def _generate_candidate_schedules(
        self,
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow],
        crop_stages: Dict[date, CropGrowthStage]
    ) -> List[List[Tuple[date, str, float, ApplicationMethod]]]:
        """Generate candidate schedules for robust optimization."""
        import random

        candidates = []

        for _ in range(20):  # Generate 20 candidates
            schedule = []

            for fertilizer_type, total_amount in request.fertilizer_requirements.items():
                # Random split strategy
                num_splits = random.randint(1, 3) if request.split_application_allowed else 1

                # Generate dates
                dates = []
                for _ in range(num_splits):
                    offset = random.randint(0, min(90, request.optimization_horizon_days))
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
                        amount = remaining * random.uniform(0.25, 0.50)
                        amounts.append(amount)
                        remaining -= amount
                    amounts.append(remaining)

                # Add to schedule
                for app_date, amount in zip(dates, amounts):
                    method = random.choice(request.application_methods)
                    schedule.append((app_date, fertilizer_type, amount, method))

            candidates.append(schedule)

        return candidates

    def _perform_sensitivity_analysis(
        self,
        schedule: List[Tuple[date, str, float, ApplicationMethod]],
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow],
        crop_stages: Dict[date, CropGrowthStage]
    ) -> Dict[str, float]:
        """Perform sensitivity analysis on uncertainty parameters."""
        # Baseline evaluation
        base_scenarios = self._generate_scenarios(weather_windows, crop_stages)
        base_outcomes = [
            self._evaluate_scenario(schedule, scenario, request)
            for scenario in base_scenarios
        ]
        base_mean = np.mean([o["total_benefit"] for o in base_outcomes])

        sensitivity = {}

        # Test weather uncertainty sensitivity
        original_weather_unc = self.uncertainty_params.weather_forecast_uncertainty
        self.uncertainty_params.weather_forecast_uncertainty *= 1.5
        test_scenarios = self._generate_scenarios(weather_windows, crop_stages)
        test_outcomes = [
            self._evaluate_scenario(schedule, scenario, request)
            for scenario in test_scenarios
        ]
        test_mean = np.mean([o["total_benefit"] for o in test_outcomes])
        sensitivity["weather_uncertainty"] = abs(test_mean - base_mean) / base_mean if base_mean > 0 else 0.0
        self.uncertainty_params.weather_forecast_uncertainty = original_weather_unc

        # Test crop growth uncertainty sensitivity
        original_crop_unc = self.uncertainty_params.crop_growth_uncertainty
        self.uncertainty_params.crop_growth_uncertainty *= 1.5
        test_scenarios = self._generate_scenarios(weather_windows, crop_stages)
        test_outcomes = [
            self._evaluate_scenario(schedule, scenario, request)
            for scenario in test_scenarios
        ]
        test_mean = np.mean([o["total_benefit"] for o in test_outcomes])
        sensitivity["crop_growth_uncertainty"] = abs(test_mean - base_mean) / base_mean if base_mean > 0 else 0.0
        self.uncertainty_params.crop_growth_uncertainty = original_crop_unc

        # Test yield response uncertainty sensitivity
        original_yield_unc = self.uncertainty_params.yield_response_uncertainty
        self.uncertainty_params.yield_response_uncertainty *= 1.5
        test_scenarios = self._generate_scenarios(weather_windows, crop_stages)
        test_outcomes = [
            self._evaluate_scenario(schedule, scenario, request)
            for scenario in test_scenarios
        ]
        test_mean = np.mean([o["total_benefit"] for o in test_outcomes])
        sensitivity["yield_response_uncertainty"] = abs(test_mean - base_mean) / base_mean if base_mean > 0 else 0.0
        self.uncertainty_params.yield_response_uncertainty = original_yield_unc

        return sensitivity

    def _assess_weather_condition(
        self,
        temperature: float,
        precip_prob: float,
        wind_speed: float,
        soil_moisture: float
    ) -> WeatherCondition:
        """Assess weather condition from parameters."""
        score = 0

        # Temperature scoring (optimal 60-80°F)
        if 60 <= temperature <= 80:
            score += 2
        elif 50 <= temperature <= 90:
            score += 1

        # Precipitation scoring (lower is better)
        if precip_prob < 0.2:
            score += 2
        elif precip_prob < 0.4:
            score += 1

        # Wind scoring (lower is better for application)
        if wind_speed < 10:
            score += 2
        elif wind_speed < 15:
            score += 1

        # Soil moisture (optimal 0.4-0.7)
        if 0.4 <= soil_moisture <= 0.7:
            score += 2
        elif 0.3 <= soil_moisture <= 0.8:
            score += 1

        # Map score to condition
        if score >= 7:
            return WeatherCondition.OPTIMAL
        elif score >= 5:
            return WeatherCondition.ACCEPTABLE
        elif score >= 3:
            return WeatherCondition.MARGINAL
        elif score >= 1:
            return WeatherCondition.POOR
        else:
            return WeatherCondition.UNACCEPTABLE

    def _calculate_suitability(
        self,
        condition: WeatherCondition,
        precip_prob: float
    ) -> float:
        """Calculate suitability score."""
        condition_scores = {
            WeatherCondition.OPTIMAL: 1.0,
            WeatherCondition.ACCEPTABLE: 0.8,
            WeatherCondition.MARGINAL: 0.6,
            WeatherCondition.POOR: 0.3,
            WeatherCondition.UNACCEPTABLE: 0.0
        }

        base_score = condition_scores.get(condition, 0.5)
        precip_penalty = precip_prob * 0.2

        return max(0.0, base_score - precip_penalty)

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
