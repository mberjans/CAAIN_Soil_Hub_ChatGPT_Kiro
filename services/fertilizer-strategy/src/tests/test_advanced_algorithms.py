"""
Unit Tests for Advanced Timing Optimization Algorithms

Tests cover:
- Dynamic Programming Optimizer
- Genetic Algorithm Optimizer
- Machine Learning Optimizer
- Multi-Objective Optimizer
- Uncertainty Handler
- Algorithm Integration
"""

import pytest
import asyncio
from datetime import date, timedelta
from typing import List, Dict

from ..algorithms.dynamic_programming_optimizer import (
    DynamicProgrammingOptimizer,
    State,
    Action
)
from ..algorithms.genetic_algorithm_optimizer import (
    GeneticAlgorithmOptimizer,
    Chromosome,
    ApplicationGene
)
from ..algorithms.ml_optimizer import (
    MLOptimizer,
    FeatureVector,
    HistoricalRecord
)
from ..algorithms.multi_objective_optimizer import (
    MultiObjectiveOptimizer,
    ObjectiveValues,
    Solution
)
from ..algorithms.uncertainty_handler import (
    UncertaintyHandler,
    UncertaintyParameters,
    Scenario
)

from ..models.timing_optimization_models import (
    TimingOptimizationRequest,
    WeatherWindow,
    CropGrowthStage,
    ApplicationMethod,
    WeatherCondition
)
from ..services.timing_optimization_service import FertilizerTimingOptimizer


class TestDynamicProgrammingOptimizer:
    """Test cases for Dynamic Programming Optimizer."""

    def setup_method(self):
        """Setup test fixtures."""
        self.optimizer = DynamicProgrammingOptimizer(
            discount_factor=0.95,
            max_horizon_days=90,
            state_discretization=5
        )

    def test_optimizer_initialization(self):
        """Test optimizer initializes correctly."""
        assert self.optimizer.discount_factor == 0.95
        assert self.optimizer.max_horizon_days == 90
        assert self.optimizer.state_discretization == 5
        assert len(self.optimizer.value_cache) == 0
        assert len(self.optimizer.policy_cache) == 0

    def test_state_creation(self):
        """Test state creation and hashing."""
        state1 = State(
            date=date(2024, 5, 1),
            crop_stage=CropGrowthStage.V4,
            soil_moisture=0.6,
            available_budget=1000.0,
            applied_fertilizers={"nitrogen": 50.0},
            weather_condition=WeatherCondition.OPTIMAL
        )

        state2 = State(
            date=date(2024, 5, 1),
            crop_stage=CropGrowthStage.V4,
            soil_moisture=0.6,
            available_budget=1000.0,
            applied_fertilizers={"nitrogen": 50.0},
            weather_condition=WeatherCondition.OPTIMAL
        )

        # States with same values should be equal
        assert state1 == state2
        assert hash(state1) == hash(state2)

    def test_action_creation(self):
        """Test action creation."""
        action = Action(
            fertilizer_type="nitrogen",
            amount=50.0,
            method=ApplicationMethod.BROADCAST,
            apply=True
        )

        assert action.fertilizer_type == "nitrogen"
        assert action.amount == 50.0
        assert action.apply is True

    def test_optimize_basic(self):
        """Test basic optimization."""
        request = self._create_test_request()
        weather_windows = self._create_test_weather_windows(request.planting_date)
        crop_stages = self._create_test_crop_stages(request.planting_date)

        result = self.optimizer.optimize(request, weather_windows, crop_stages)

        assert result is not None
        assert result.total_value >= 0
        assert len(result.optimal_schedule) > 0
        assert 0 <= result.confidence_score <= 1.0

    def test_value_function_memoization(self):
        """Test that value function uses memoization."""
        request = self._create_test_request()
        weather_windows = self._create_test_weather_windows(request.planting_date)
        crop_stages = self._create_test_crop_stages(request.planting_date)

        # Run optimization
        result = self.optimizer.optimize(request, weather_windows, crop_stages)

        # Check that cache was populated
        assert len(self.optimizer.value_cache) > 0
        assert len(self.optimizer.policy_cache) > 0

    def _create_test_request(self) -> TimingOptimizationRequest:
        """Create a test optimization request."""
        return TimingOptimizationRequest(
            field_id="test-field-001",
            crop_type="corn",
            planting_date=date(2024, 5, 1),
            expected_harvest_date=date(2024, 10, 1),
            fertilizer_requirements={"nitrogen": 150.0, "phosphorus": 50.0},
            application_methods=[ApplicationMethod.BROADCAST, ApplicationMethod.SIDE_DRESS],
            soil_type="loam",
            soil_moisture_capacity=0.6,
            location={"lat": 40.7128, "lng": -74.0060},
            optimization_horizon_days=120
        )

    def _create_test_weather_windows(self, start_date: date) -> List[WeatherWindow]:
        """Create test weather windows."""
        windows = []
        for i in range(30):
            window_date = start_date + timedelta(days=i)
            window = WeatherWindow(
                start_date=window_date,
                end_date=window_date,
                condition=WeatherCondition.OPTIMAL if i % 3 == 0 else WeatherCondition.ACCEPTABLE,
                temperature_f=70.0 + i * 0.5,
                precipitation_probability=0.2,
                wind_speed_mph=8.0,
                soil_moisture=0.6,
                suitability_score=0.9 if i % 3 == 0 else 0.8
            )
            windows.append(window)
        return windows

    def _create_test_crop_stages(self, planting_date: date) -> Dict[date, CropGrowthStage]:
        """Create test crop growth stages."""
        stages = {
            planting_date: CropGrowthStage.PLANTING,
            planting_date + timedelta(days=7): CropGrowthStage.EMERGENCE,
            planting_date + timedelta(days=14): CropGrowthStage.V2,
            planting_date + timedelta(days=21): CropGrowthStage.V4,
            planting_date + timedelta(days=28): CropGrowthStage.V6,
            planting_date + timedelta(days=35): CropGrowthStage.V8,
            planting_date + timedelta(days=42): CropGrowthStage.V10
        }
        return stages


class TestGeneticAlgorithmOptimizer:
    """Test cases for Genetic Algorithm Optimizer."""

    def setup_method(self):
        """Setup test fixtures."""
        self.optimizer = GeneticAlgorithmOptimizer(
            population_size=50,
            max_generations=50,
            crossover_rate=0.8,
            mutation_rate=0.1
        )

    def test_optimizer_initialization(self):
        """Test optimizer initializes correctly."""
        assert self.optimizer.population_size == 50
        assert self.optimizer.max_generations == 50
        assert self.optimizer.crossover_rate == 0.8
        assert self.optimizer.mutation_rate == 0.1

    def test_chromosome_creation(self):
        """Test chromosome creation."""
        genes = [
            ApplicationGene(
                fertilizer_type="nitrogen",
                application_date=date(2024, 5, 15),
                amount=75.0,
                method=ApplicationMethod.BROADCAST
            )
        ]

        chromosome = Chromosome(genes=genes, fitness=0.85)

        assert len(chromosome.genes) == 1
        assert chromosome.fitness == 0.85

    def test_optimize_basic(self):
        """Test basic GA optimization."""
        request = self._create_test_request()
        weather_windows = self._create_test_weather_windows(request.planting_date)
        crop_stages = self._create_test_crop_stages(request.planting_date)

        result = self.optimizer.optimize(request, weather_windows, crop_stages)

        assert result is not None
        assert result.best_schedule is not None
        assert result.best_schedule.fitness > 0
        assert len(result.fitness_history) > 0
        assert len(result.final_population) == self.optimizer.population_size

    def test_population_initialization(self):
        """Test that population is initialized correctly."""
        request = self._create_test_request()
        weather_windows = self._create_test_weather_windows(request.planting_date)
        crop_stages = self._create_test_crop_stages(request.planting_date)

        population = self.optimizer._initialize_population(request, weather_windows, crop_stages)

        assert len(population) == self.optimizer.population_size
        assert all(len(ind.genes) > 0 for ind in population)

    def test_fitness_evaluation(self):
        """Test fitness evaluation."""
        request = self._create_test_request()
        weather_windows = self._create_test_weather_windows(request.planting_date)
        crop_stages = self._create_test_crop_stages(request.planting_date)

        genes = [
            ApplicationGene(
                fertilizer_type="nitrogen",
                application_date=request.planting_date + timedelta(days=21),
                amount=150.0,
                method=ApplicationMethod.BROADCAST
            )
        ]
        chromosome = Chromosome(genes=genes)

        fitness = self.optimizer._evaluate_fitness(chromosome, request, weather_windows, crop_stages)

        assert fitness >= 0
        assert chromosome.objectives is not None

    def _create_test_request(self) -> TimingOptimizationRequest:
        """Create test request."""
        return TimingOptimizationRequest(
            field_id="test-field-001",
            crop_type="corn",
            planting_date=date(2024, 5, 1),
            fertilizer_requirements={"nitrogen": 150.0},
            application_methods=[ApplicationMethod.BROADCAST],
            soil_type="loam",
            soil_moisture_capacity=0.6,
            location={"lat": 40.7128, "lng": -74.0060},
            optimization_horizon_days=120
        )

    def _create_test_weather_windows(self, start_date: date) -> List[WeatherWindow]:
        """Create test weather windows."""
        windows = []
        for i in range(30):
            window_date = start_date + timedelta(days=i)
            window = WeatherWindow(
                start_date=window_date,
                end_date=window_date,
                condition=WeatherCondition.OPTIMAL,
                temperature_f=70.0,
                precipitation_probability=0.2,
                wind_speed_mph=8.0,
                soil_moisture=0.6,
                suitability_score=0.9
            )
            windows.append(window)
        return windows

    def _create_test_crop_stages(self, planting_date: date) -> Dict[date, CropGrowthStage]:
        """Create test crop stages."""
        return {
            planting_date: CropGrowthStage.PLANTING,
            planting_date + timedelta(days=21): CropGrowthStage.V4
        }


class TestMLOptimizer:
    """Test cases for Machine Learning Optimizer."""

    def setup_method(self):
        """Setup test fixtures."""
        self.optimizer = MLOptimizer(
            learning_rate=0.01,
            exploration_rate=0.1,
            discount_factor=0.95
        )

    def test_optimizer_initialization(self):
        """Test optimizer initializes correctly."""
        assert self.optimizer.learning_rate == 0.01
        assert self.optimizer.exploration_rate == 0.1
        assert self.optimizer.discount_factor == 0.95
        assert self.optimizer.weights_input_hidden.shape == (11, 20)
        assert self.optimizer.weights_hidden_output.shape == (20, 1)

    def test_feature_vector_creation(self):
        """Test feature vector creation and conversion."""
        feature = FeatureVector(
            day_of_year=150,
            days_from_planting=30,
            crop_stage_index=3,
            temperature=70.0,
            soil_moisture=0.6,
            weather_condition_index=4,
            cumulative_nitrogen=50.0,
            cumulative_phosphorus=20.0,
            cumulative_potassium=30.0,
            application_amount=50.0,
            slope_percent=2.0
        )

        array = feature.to_array()
        assert len(array) == 11
        assert all(0 <= x <= 1.5 for x in array)  # All normalized

    def test_optimize_without_historical_data(self):
        """Test optimization without historical data."""
        request = self._create_test_request()
        weather_windows = self._create_test_weather_windows(request.planting_date)
        crop_stages = self._create_test_crop_stages(request.planting_date)

        result = self.optimizer.optimize(request, weather_windows, crop_stages, None)

        assert result is not None
        assert len(result.recommended_schedule) > 0
        assert result.predicted_yield > 0
        assert result.model_confidence >= 0

    def test_optimize_with_historical_data(self):
        """Test optimization with historical data."""
        request = self._create_test_request()
        weather_windows = self._create_test_weather_windows(request.planting_date)
        crop_stages = self._create_test_crop_stages(request.planting_date)
        historical_data = self._create_historical_data()

        result = self.optimizer.optimize(request, weather_windows, crop_stages, historical_data)

        assert result is not None
        assert len(result.recommended_schedule) > 0
        assert result.model_confidence > 0.5  # Should be higher with data

    def test_feature_importance(self):
        """Test feature importance calculation."""
        request = self._create_test_request()
        weather_windows = self._create_test_weather_windows(request.planting_date)
        crop_stages = self._create_test_crop_stages(request.planting_date)

        result = self.optimizer.optimize(request, weather_windows, crop_stages, None)

        assert len(result.feature_importance) == 11
        assert all(v >= 0 for v in result.feature_importance.values())
        # Sum of importances should be approximately 1.0
        assert abs(sum(result.feature_importance.values()) - 1.0) < 0.01

    def _create_test_request(self) -> TimingOptimizationRequest:
        """Create test request."""
        return TimingOptimizationRequest(
            field_id="test-field-001",
            crop_type="corn",
            planting_date=date(2024, 5, 1),
            fertilizer_requirements={"nitrogen": 150.0},
            application_methods=[ApplicationMethod.BROADCAST],
            soil_type="loam",
            soil_moisture_capacity=0.6,
            location={"lat": 40.7128, "lng": -74.0060},
            optimization_horizon_days=120,
            slope_percent=2.0
        )

    def _create_test_weather_windows(self, start_date: date) -> List[WeatherWindow]:
        """Create test weather windows."""
        windows = []
        for i in range(30):
            window_date = start_date + timedelta(days=i)
            window = WeatherWindow(
                start_date=window_date,
                end_date=window_date,
                condition=WeatherCondition.OPTIMAL,
                temperature_f=70.0,
                precipitation_probability=0.2,
                wind_speed_mph=8.0,
                soil_moisture=0.6,
                suitability_score=0.9
            )
            windows.append(window)
        return windows

    def _create_test_crop_stages(self, planting_date: date) -> Dict[date, CropGrowthStage]:
        """Create test crop stages."""
        return {
            planting_date: CropGrowthStage.PLANTING,
            planting_date + timedelta(days=21): CropGrowthStage.V4
        }

    def _create_historical_data(self) -> List[Dict]:
        """Create sample historical data."""
        data = []
        base_date = date(2023, 5, 1)

        for i in range(20):
            record = {
                "field_id": f"field-{i}",
                "crop_type": "corn",
                "application_date": base_date + timedelta(days=i * 5),
                "fertilizer_type": "nitrogen",
                "amount": 75.0,
                "method": "broadcast",
                "weather_condition": "optimal",
                "crop_stage": "v4",
                "soil_moisture": 0.6,
                "yield_outcome": 180.0 + i * 2,
                "cost": 100.0
            }
            data.append(record)

        return data


class TestMultiObjectiveOptimizer:
    """Test cases for Multi-Objective Optimizer."""

    def setup_method(self):
        """Setup test fixtures."""
        self.optimizer = MultiObjectiveOptimizer(
            population_size=50,
            max_generations=50
        )

    def test_optimizer_initialization(self):
        """Test optimizer initializes correctly."""
        assert self.optimizer.population_size == 50
        assert self.optimizer.max_generations == 50

    def test_objective_values_domination(self):
        """Test Pareto domination check."""
        obj1 = ObjectiveValues(
            yield_score=80.0,
            cost_score=75.0,
            environmental_score=85.0,
            risk_score=70.0
        )

        obj2 = ObjectiveValues(
            yield_score=75.0,
            cost_score=70.0,
            environmental_score=80.0,
            risk_score=65.0
        )

        assert obj1.dominates(obj2) is True
        assert obj2.dominates(obj1) is False

    def test_optimize_basic(self):
        """Test basic MO optimization."""
        request = self._create_test_request()
        weather_windows = self._create_test_weather_windows(request.planting_date)
        crop_stages = self._create_test_crop_stages(request.planting_date)

        result = self.optimizer.optimize(request, weather_windows, crop_stages)

        assert result is not None
        assert len(result.pareto_front) > 0
        assert result.recommended_solution is not None
        assert len(result.all_solutions) == self.optimizer.population_size

    def test_pareto_front_non_dominated(self):
        """Test that Pareto front contains only non-dominated solutions."""
        request = self._create_test_request()
        weather_windows = self._create_test_weather_windows(request.planting_date)
        crop_stages = self._create_test_crop_stages(request.planting_date)

        result = self.optimizer.optimize(request, weather_windows, crop_stages)

        # Check that no solution in Pareto front dominates another
        pareto = result.pareto_front
        for i, sol1 in enumerate(pareto):
            for j, sol2 in enumerate(pareto):
                if i != j:
                    assert not sol1.objectives.dominates(sol2.objectives)

    def test_trade_off_analysis(self):
        """Test trade-off analysis."""
        request = self._create_test_request()
        weather_windows = self._create_test_weather_windows(request.planting_date)
        crop_stages = self._create_test_crop_stages(request.planting_date)

        result = self.optimizer.optimize(request, weather_windows, crop_stages)

        assert "pareto_size" in result.trade_off_analysis
        assert "yield_range" in result.trade_off_analysis
        assert "cost_range" in result.trade_off_analysis
        assert result.trade_off_analysis["pareto_size"] > 0

    def _create_test_request(self) -> TimingOptimizationRequest:
        """Create test request."""
        return TimingOptimizationRequest(
            field_id="test-field-001",
            crop_type="corn",
            planting_date=date(2024, 5, 1),
            fertilizer_requirements={"nitrogen": 150.0},
            application_methods=[ApplicationMethod.BROADCAST],
            soil_type="loam",
            soil_moisture_capacity=0.6,
            location={"lat": 40.7128, "lng": -74.0060},
            optimization_horizon_days=120,
            prioritize_yield=True,
            prioritize_cost=True
        )

    def _create_test_weather_windows(self, start_date: date) -> List[WeatherWindow]:
        """Create test weather windows."""
        windows = []
        for i in range(30):
            window_date = start_date + timedelta(days=i)
            window = WeatherWindow(
                start_date=window_date,
                end_date=window_date,
                condition=WeatherCondition.OPTIMAL,
                temperature_f=70.0,
                precipitation_probability=0.2,
                wind_speed_mph=8.0,
                soil_moisture=0.6,
                suitability_score=0.9
            )
            windows.append(window)
        return windows

    def _create_test_crop_stages(self, planting_date: date) -> Dict[date, CropGrowthStage]:
        """Create test crop stages."""
        return {
            planting_date: CropGrowthStage.PLANTING,
            planting_date + timedelta(days=21): CropGrowthStage.V4
        }


class TestUncertaintyHandler:
    """Test cases for Uncertainty Handler."""

    def setup_method(self):
        """Setup test fixtures."""
        self.handler = UncertaintyHandler(
            num_scenarios=100,
            confidence_level=0.95,
            risk_aversion=0.5
        )

    def test_handler_initialization(self):
        """Test handler initializes correctly."""
        assert self.handler.num_scenarios == 100
        assert self.handler.confidence_level == 0.95
        assert self.handler.risk_aversion == 0.5

    def test_analyze_uncertainty(self):
        """Test uncertainty analysis."""
        request = self._create_test_request()
        schedule = self._create_test_schedule()
        weather_windows = self._create_test_weather_windows(request.planting_date)
        crop_stages = self._create_test_crop_stages(request.planting_date)

        result = self.handler.analyze_uncertainty(
            request, schedule, weather_windows, crop_stages
        )

        assert result is not None
        assert len(result.scenarios) > 0
        assert "yield" in result.mean_outcome
        assert "yield" in result.confidence_intervals

    def test_scenario_generation(self):
        """Test scenario generation."""
        weather_windows = self._create_test_weather_windows(date(2024, 5, 1))
        crop_stages = self._create_test_crop_stages(date(2024, 5, 1))

        scenarios = self.handler._generate_scenarios(weather_windows, crop_stages)

        assert len(scenarios) == self.handler.num_scenarios
        assert all(s.probability > 0 for s in scenarios)
        assert all(s.yield_multiplier > 0 for s in scenarios)

    def test_confidence_intervals(self):
        """Test confidence interval calculation."""
        request = self._create_test_request()
        schedule = self._create_test_schedule()
        weather_windows = self._create_test_weather_windows(request.planting_date)
        crop_stages = self._create_test_crop_stages(request.planting_date)

        result = self.handler.analyze_uncertainty(
            request, schedule, weather_windows, crop_stages
        )

        for key, outcome in result.confidence_intervals.items():
            # Check that confidence intervals make sense
            lower_95, upper_95 = outcome.confidence_95
            lower_90, upper_90 = outcome.confidence_90
            lower_80, upper_80 = outcome.confidence_80

            assert lower_95 <= lower_90 <= lower_80
            assert upper_80 <= upper_90 <= upper_95
            assert lower_95 <= outcome.mean_value <= upper_95

    def test_risk_metrics(self):
        """Test risk metrics calculation."""
        request = self._create_test_request()
        schedule = self._create_test_schedule()
        weather_windows = self._create_test_weather_windows(request.planting_date)
        crop_stages = self._create_test_crop_stages(request.planting_date)

        result = self.handler.analyze_uncertainty(
            request, schedule, weather_windows, crop_stages
        )

        assert "value_at_risk_5" in result.risk_metrics
        assert "conditional_var_5" in result.risk_metrics
        assert "downside_risk" in result.risk_metrics
        assert "sharpe_ratio" in result.risk_metrics
        assert all(v >= 0 or v == result.risk_metrics["value_at_risk_5"] for v in result.risk_metrics.values())

    def _create_test_request(self) -> TimingOptimizationRequest:
        """Create test request."""
        return TimingOptimizationRequest(
            field_id="test-field-001",
            crop_type="corn",
            planting_date=date(2024, 5, 1),
            fertilizer_requirements={"nitrogen": 150.0},
            application_methods=[ApplicationMethod.BROADCAST],
            soil_type="loam",
            soil_moisture_capacity=0.6,
            location={"lat": 40.7128, "lng": -74.0060},
            optimization_horizon_days=120
        )

    def _create_test_schedule(self) -> List:
        """Create test schedule."""
        return [
            (date(2024, 5, 15), "nitrogen", 75.0, ApplicationMethod.BROADCAST),
            (date(2024, 6, 1), "nitrogen", 75.0, ApplicationMethod.SIDE_DRESS)
        ]

    def _create_test_weather_windows(self, start_date: date) -> List[WeatherWindow]:
        """Create test weather windows."""
        windows = []
        for i in range(60):
            window_date = start_date + timedelta(days=i)
            window = WeatherWindow(
                start_date=window_date,
                end_date=window_date,
                condition=WeatherCondition.OPTIMAL,
                temperature_f=70.0,
                precipitation_probability=0.2,
                wind_speed_mph=8.0,
                soil_moisture=0.6,
                suitability_score=0.9
            )
            windows.append(window)
        return windows

    def _create_test_crop_stages(self, planting_date: date) -> Dict[date, CropGrowthStage]:
        """Create test crop stages."""
        return {
            planting_date: CropGrowthStage.PLANTING,
            planting_date + timedelta(days=14): CropGrowthStage.V2,
            planting_date + timedelta(days=21): CropGrowthStage.V4,
            planting_date + timedelta(days=28): CropGrowthStage.V6
        }


class TestAlgorithmIntegration:
    """Test cases for algorithm integration in timing optimization service."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return FertilizerTimingOptimizer()

    @pytest.mark.asyncio
    async def test_algorithm_selection_auto(self, service):
        """Test automatic algorithm selection."""
        request = self._create_test_request()

        # Test with no historical data - should select based on problem size
        selected = service._select_optimal_algorithm(request, None)
        assert selected in ["dp", "ga", "mo"]

        # Test with historical data - should select ML
        historical_data = [{"data": i} for i in range(60)]
        selected = service._select_optimal_algorithm(request, historical_data)
        assert selected == "ml"

    @pytest.mark.asyncio
    async def test_optimize_with_advanced_algorithms_auto(self, service):
        """Test optimization with auto algorithm selection."""
        request = self._create_test_request()

        result = await service.optimize_with_advanced_algorithms(request, algorithm="auto")

        assert result is not None
        assert len(result.optimal_timings) > 0
        assert result.optimization_method in ["dynamic_programming", "genetic_algorithm", "machine_learning", "multi_objective"]

    @pytest.mark.asyncio
    async def test_optimize_with_dp(self, service):
        """Test optimization with DP algorithm."""
        request = self._create_test_request()

        result = await service.optimize_with_advanced_algorithms(request, algorithm="dp")

        assert result is not None
        assert result.optimization_method == "dynamic_programming"
        assert len(result.optimal_timings) > 0

    @pytest.mark.asyncio
    async def test_optimize_with_ga(self, service):
        """Test optimization with GA algorithm."""
        request = self._create_test_request()

        result = await service.optimize_with_advanced_algorithms(request, algorithm="ga")

        assert result is not None
        assert result.optimization_method == "genetic_algorithm"
        assert len(result.optimal_timings) > 0

    @pytest.mark.asyncio
    async def test_optimize_with_mo(self, service):
        """Test optimization with MO algorithm."""
        request = self._create_test_request()

        result = await service.optimize_with_advanced_algorithms(request, algorithm="mo")

        assert result is not None
        assert result.optimization_method == "multi_objective"
        assert len(result.optimal_timings) > 0

    def _create_test_request(self) -> TimingOptimizationRequest:
        """Create test request."""
        return TimingOptimizationRequest(
            field_id="test-field-001",
            crop_type="corn",
            planting_date=date(2024, 5, 1),
            expected_harvest_date=date(2024, 10, 1),
            fertilizer_requirements={"nitrogen": 150.0},
            application_methods=[ApplicationMethod.BROADCAST, ApplicationMethod.SIDE_DRESS],
            soil_type="loam",
            soil_moisture_capacity=0.6,
            location={"lat": 40.7128, "lng": -74.0060},
            optimization_horizon_days=120,
            prioritize_yield=True
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
