"""Tests for the YieldPotentialCalculator."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Dict

import pytest

from src.services.yield_calculator import YieldPotentialCalculator, YieldPotentialResult


class StubYieldPotential:
    """Simple stub for variety yield potential information."""

    def __init__(self, average_range, potential_range=None, stability=None) -> None:
        self.average_yield_range = average_range
        self.potential_yield_range = potential_range
        self.yield_stability_rating = stability


class StubDiseaseResistance:
    """Stub disease resistance with rust values."""

    def __init__(self, values: Dict[str, int]) -> None:
        self.rust_resistance = values


class StubAbioticTolerance:
    """Stub abiotic stress tolerance information."""

    def __init__(self, drought: int) -> None:
        self.drought_tolerance = drought


class StubRegionalEntry:
    """Stub regional performance entry."""

    def __init__(self, region: str, zone: str, performance_index: float, trials: int) -> None:
        self.region_name = region
        self.climate_zone = zone
        self.performance_index = performance_index
        self.trials_count = trials
        self.average_yield = None


def _build_variety() -> Any:
    variety = SimpleNamespace()
    variety.yield_potential = StubYieldPotential((4.0, 6.0), (4.5, 7.0), 4.2)
    variety.disease_resistance = StubDiseaseResistance({"leaf_rust": 4, "stem_rust": 3})
    variety.abiotic_stress_tolerances = StubAbioticTolerance(4)
    variety.trait_stack = ["trait_one", "trait_two"]
    variety.variety_id = "variety-test-001"
    entries = []
    entries.append(StubRegionalEntry("prairie", "zone_3", 0.65, 6))
    entries.append(StubRegionalEntry("prairie", "zone_4", 0.6, 3))
    variety.regional_performance_data = entries
    variety.quality_attributes = ["protein"]
    return variety


def test_positive_factors_increase_expected_yield() -> None:
    calculator = YieldPotentialCalculator()
    variety = _build_variety()
    context: Dict[str, Any] = {}
    context["region"] = "prairie"
    forecast: Dict[str, Any] = {}
    forecast["precipitation_outlook"] = 0.15
    forecast["temperature_outlook"] = 0.05
    forecast["gdd_outlook"] = 0.02
    context["seasonal_forecast"] = forecast
    context["climate_risks"] = {"drought_risk": 0.7, "extreme_event_risk": 0.5}
    context["soil_profile"] = {"organic_matter": 4.5, "drainage": "well"}

    result = calculator.calculate(variety, context)

    assert result.expected_yield > result.baseline_yield
    assert result.confidence > 0.4
    assert "regional_trials" in result.data_sources


def test_adverse_weather_reduces_expected_yield() -> None:
    calculator = YieldPotentialCalculator()
    variety = _build_variety()
    context: Dict[str, Any] = {}
    context["region"] = "prairie"
    forecast: Dict[str, Any] = {}
    forecast["precipitation_outlook"] = -0.25
    forecast["temperature_outlook"] = 0.2
    forecast["weather_risk_index"] = 0.6
    context["seasonal_forecast"] = forecast
    context["climate_risks"] = {"drought_risk": 0.7, "extreme_event_risk": 0.5}

    baseline_context: Dict[str, Any] = {}
    baseline_context["region"] = "prairie"
    baseline_result = calculator.calculate(variety, baseline_context)

    result = calculator.calculate(variety, context)

    assert result.component_breakdown.get("weather_outlook", 0.0) < 0
    assert result.risk_index > baseline_result.risk_index


def test_score_from_result_accounts_for_risk() -> None:
    calculator = YieldPotentialCalculator()

    low_risk = YieldPotentialResult(
        baseline_yield=5.0,
        expected_yield=5.5,
        yield_range=(4.8, 6.2),
        stability_score=0.8,
        risk_index=0.2,
        confidence=0.75
    )

    high_risk = YieldPotentialResult(
        baseline_yield=5.0,
        expected_yield=5.5,
        yield_range=(4.2, 6.8),
        stability_score=0.5,
        risk_index=0.7,
        confidence=0.45
    )

    low_risk_score = calculator.score_from_result(low_risk)
    high_risk_score = calculator.score_from_result(high_risk)

    assert 0.0 <= high_risk_score <= 1.0
    assert low_risk_score > high_risk_score


def test_prediction_payload_includes_contributors() -> None:
    calculator = YieldPotentialCalculator()
    variety = _build_variety()
    context: Dict[str, Any] = {}
    result = calculator.calculate(variety, context)

    payload = calculator.build_prediction_payload(result)

    assert "predicted_yield_range" in payload
    assert "contributing_factors" in payload
    assert isinstance(payload["contributing_factors"], dict)
    assert "notes" in payload
