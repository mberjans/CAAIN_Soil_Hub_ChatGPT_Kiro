#!/usr/bin/env python3
"""
Simple validation script for advanced timing optimization algorithms.
This script performs basic smoke tests to verify all algorithms are functional.
"""

import sys
import os
from datetime import date, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.algorithms.dynamic_programming_optimizer import DynamicProgrammingOptimizer
from src.algorithms.genetic_algorithm_optimizer import GeneticAlgorithmOptimizer
from src.algorithms.ml_optimizer import MLOptimizer
from src.algorithms.multi_objective_optimizer import MultiObjectiveOptimizer
from src.algorithms.uncertainty_handler import UncertaintyHandler

from src.models.timing_optimization_models import (
    TimingOptimizationRequest,
    WeatherWindow,
    CropGrowthStage,
    ApplicationMethod,
    WeatherCondition
)


def create_test_request():
    """Create a test optimization request."""
    return TimingOptimizationRequest(
        field_id="test-field-001",
        crop_type="corn",
        planting_date=date(2024, 5, 1),
        expected_harvest_date=date(2024, 10, 1),
        fertilizer_requirements={"nitrogen": 150.0},
        application_methods=[ApplicationMethod.BROADCAST],
        soil_type="loam",
        soil_moisture_capacity=0.6,
        location={"lat": 40.7128, "lng": -74.0060},
        optimization_horizon_days=90
    )


def create_test_weather_windows(start_date):
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


def create_test_crop_stages(planting_date):
    """Create test crop growth stages."""
    return {
        planting_date: CropGrowthStage.PLANTING,
        planting_date + timedelta(days=7): CropGrowthStage.EMERGENCE,
        planting_date + timedelta(days=21): CropGrowthStage.V4,
        planting_date + timedelta(days=28): CropGrowthStage.V6
    }


def test_dynamic_programming():
    """Test Dynamic Programming optimizer."""
    print("\n1. Testing Dynamic Programming Optimizer...")

    try:
        optimizer = DynamicProgrammingOptimizer(
            discount_factor=0.95,
            max_horizon_days=60,
            state_discretization=5
        )

        request = create_test_request()
        weather_windows = create_test_weather_windows(request.planting_date)
        crop_stages = create_test_crop_stages(request.planting_date)

        result = optimizer.optimize(request, weather_windows, crop_stages)

        assert result is not None, "DP result is None"
        assert result.total_value >= 0, "DP total value is negative"
        assert len(result.optimal_schedule) > 0, "DP schedule is empty"

        print("   ✓ DP Optimizer works correctly")
        print(f"   - Total Value: {result.total_value:.2f}")
        print(f"   - Schedule Length: {len(result.optimal_schedule)}")
        print(f"   - Confidence: {result.confidence_score:.2f}")
        return True

    except Exception as e:
        print(f"   ✗ DP Optimizer failed: {e}")
        return False


def test_genetic_algorithm():
    """Test Genetic Algorithm optimizer."""
    print("\n2. Testing Genetic Algorithm Optimizer...")

    try:
        optimizer = GeneticAlgorithmOptimizer(
            population_size=30,
            max_generations=20,
            crossover_rate=0.8,
            mutation_rate=0.1
        )

        request = create_test_request()
        weather_windows = create_test_weather_windows(request.planting_date)
        crop_stages = create_test_crop_stages(request.planting_date)

        result = optimizer.optimize(request, weather_windows, crop_stages)

        assert result is not None, "GA result is None"
        assert result.best_schedule is not None, "GA best schedule is None"
        assert result.best_schedule.fitness > 0, "GA fitness is zero or negative"

        print("   ✓ GA Optimizer works correctly")
        print(f"   - Best Fitness: {result.best_schedule.fitness:.2f}")
        print(f"   - Schedule Length: {len(result.best_schedule.schedule)}")
        print(f"   - Generations: {len(result.fitness_history)}")
        return True

    except Exception as e:
        print(f"   ✗ GA Optimizer failed: {e}")
        return False


def test_ml_optimizer():
    """Test ML optimizer."""
    print("\n3. Testing ML Optimizer...")

    try:
        optimizer = MLOptimizer(
            learning_rate=0.01,
            exploration_rate=0.1,
            discount_factor=0.95
        )

        request = create_test_request()
        weather_windows = create_test_weather_windows(request.planting_date)
        crop_stages = create_test_crop_stages(request.planting_date)

        result = optimizer.optimize(request, weather_windows, crop_stages, None)

        assert result is not None, "ML result is None"
        assert len(result.recommended_schedule) > 0, "ML schedule is empty"
        assert result.predicted_yield > 0, "ML predicted yield is zero or negative"

        print("   ✓ ML Optimizer works correctly")
        print(f"   - Predicted Yield: {result.predicted_yield:.2f}")
        print(f"   - Schedule Length: {len(result.recommended_schedule)}")
        print(f"   - Model Confidence: {result.model_confidence:.2f}")
        return True

    except Exception as e:
        print(f"   ✗ ML Optimizer failed: {e}")
        return False


def test_multi_objective():
    """Test Multi-Objective optimizer."""
    print("\n4. Testing Multi-Objective Optimizer...")

    try:
        optimizer = MultiObjectiveOptimizer(
            population_size=30,
            max_generations=20
        )

        request = create_test_request()
        weather_windows = create_test_weather_windows(request.planting_date)
        crop_stages = create_test_crop_stages(request.planting_date)

        result = optimizer.optimize(request, weather_windows, crop_stages)

        assert result is not None, "MO result is None"
        assert len(result.pareto_front) > 0, "MO Pareto front is empty"
        assert result.recommended_solution is not None, "MO recommended solution is None"

        print("   ✓ MO Optimizer works correctly")
        print(f"   - Pareto Front Size: {len(result.pareto_front)}")
        print(f"   - Best Yield Score: {result.recommended_solution.objectives.yield_score:.2f}")
        print(f"   - Best Cost Score: {result.recommended_solution.objectives.cost_score:.2f}")
        return True

    except Exception as e:
        print(f"   ✗ MO Optimizer failed: {e}")
        return False


def test_uncertainty_handler():
    """Test Uncertainty Handler."""
    print("\n5. Testing Uncertainty Handler...")

    try:
        handler = UncertaintyHandler(
            num_scenarios=100,
            confidence_level=0.95,
            risk_aversion=0.5
        )

        request = create_test_request()
        schedule = [
            (date(2024, 5, 15), "nitrogen", 75.0, ApplicationMethod.BROADCAST),
            (date(2024, 6, 1), "nitrogen", 75.0, ApplicationMethod.BROADCAST)
        ]
        weather_windows = create_test_weather_windows(request.planting_date)
        crop_stages = create_test_crop_stages(request.planting_date)

        result = handler.analyze_uncertainty(request, schedule, weather_windows, crop_stages)

        assert result is not None, "Uncertainty result is None"
        assert len(result.scenarios) > 0, "No scenarios generated"
        assert "yield" in result.mean_outcome, "Mean outcome missing yield"

        print("   ✓ Uncertainty Handler works correctly")
        print(f"   - Scenarios Analyzed: {len(result.scenarios)}")
        print(f"   - Mean Yield Score: {result.mean_outcome.get('yield', 0):.2f}")
        print(f"   - VAR (5%): {result.risk_metrics.get('value_at_risk_5', 0):.2f}")
        return True

    except Exception as e:
        print(f"   ✗ Uncertainty Handler failed: {e}")
        return False


def main():
    """Run all validation tests."""
    print("="*70)
    print("ADVANCED TIMING OPTIMIZATION ALGORITHMS - VALIDATION")
    print("="*70)

    results = []

    # Run all tests
    results.append(("Dynamic Programming", test_dynamic_programming()))
    results.append(("Genetic Algorithm", test_genetic_algorithm()))
    results.append(("ML Optimizer", test_ml_optimizer()))
    results.append(("Multi-Objective", test_multi_objective()))
    results.append(("Uncertainty Handler", test_uncertainty_handler()))

    # Summary
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:.<50} {status}")

    print("="*70)
    print(f"Results: {passed}/{total} tests passed")
    print("="*70)

    if passed == total:
        print("\n✓ All algorithms validated successfully!")
        return 0
    else:
        print(f"\n✗ {total - passed} algorithm(s) failed validation")
        return 1


if __name__ == "__main__":
    sys.exit(main())
