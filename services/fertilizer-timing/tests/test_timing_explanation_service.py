"""Tests for the timing explanation service."""

import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import List

import pytest

_SRC_DIR = Path(__file__).resolve().parents[1] / "src"
_SRC_PATH = str(_SRC_DIR)
if _SRC_PATH not in sys.path:
    sys.path.insert(0, _SRC_PATH)

_SERVICES_DIR = _SRC_DIR / "services"
_SERVICES_PATH = str(_SERVICES_DIR)
if _SERVICES_PATH not in sys.path:
    sys.path.insert(0, _SERVICES_PATH)

from models import (  # pylint: disable=import-error
    ApplicationMethod,
    ApplicationTiming,
    ProgramAnalysisContext,
    TimingAssessment,
    TimingExplanation,
    TimingOptimizationResult,
    WeatherCondition,
    WeatherWindow,
)
from models import CropGrowthStage  # pylint: disable=import-error
from timing_explanation_service import TimingExplanationService  # pylint: disable=import-error


def _build_weather_window() -> WeatherWindow:
    return WeatherWindow(
        start_date=date(2024, 5, 5),
        end_date=date(2024, 5, 12),
        condition=WeatherCondition.OPTIMAL,
        temperature_f=66.0,
        precipitation_probability=0.25,
        wind_speed_mph=9.0,
        soil_moisture=0.6,
        suitability_score=0.82,
    )


def _build_application_timings(window: WeatherWindow) -> List[ApplicationTiming]:
    timings: List[ApplicationTiming] = []

    nitrogen_timing = ApplicationTiming(
        fertilizer_type="nitrogen",
        application_method=ApplicationMethod.SIDE_DRESS,
        recommended_date=date(2024, 5, 10),
        application_window=window,
        crop_stage=CropGrowthStage.V6,
        amount_lbs_per_acre=120.0,
        timing_score=0.9,
        weather_score=0.85,
        crop_score=0.92,
        soil_score=0.75,
        weather_risk=0.2,
        timing_risk=0.15,
        equipment_risk=0.1,
        estimated_cost_per_acre=78.0,
        yield_impact_percent=8.5,
        alternative_dates=[],
        backup_window=None,
    )
    timings.append(nitrogen_timing)

    phosphorus_timing = ApplicationTiming(
        fertilizer_type="phosphorus",
        application_method=ApplicationMethod.BROADCAST,
        recommended_date=date(2024, 4, 22),
        application_window=window,
        crop_stage=CropGrowthStage.V4,
        amount_lbs_per_acre=60.0,
        timing_score=0.82,
        weather_score=0.74,
        crop_score=0.86,
        soil_score=0.72,
        weather_risk=0.26,
        timing_risk=0.21,
        equipment_risk=0.12,
        estimated_cost_per_acre=55.0,
        yield_impact_percent=4.2,
        alternative_dates=[],
        backup_window=None,
    )
    timings.append(phosphorus_timing)

    return timings


def _build_optimization_result() -> TimingOptimizationResult:
    window = _build_weather_window()
    timings = _build_application_timings(window)

    recommendations: List[str] = []
    recommendations.append("Prioritize sidedress nitrogen during optimal window.")
    recommendations.append("Broadcast phosphorus near planting for better availability.")

    result = TimingOptimizationResult(
        request_id="request-123",
        optimal_timings=timings,
        split_plans=[],
        weather_windows=[window],
        weather_forecast_days=14,
        overall_timing_score=0.86,
        weather_suitability_score=0.79,
        crop_stage_alignment_score=0.84,
        risk_score=0.28,
        total_estimated_cost=13500.0,
        cost_per_acre=96.0,
        expected_yield_impact=5.4,
        roi_estimate=0.24,
        recommendations=recommendations,
        risk_mitigation_strategies=[],
        alternative_strategies=[],
        optimization_method="multi_objective",
        confidence_score=0.72,
        processing_time_ms=320.0,
        created_at=datetime.now(timezone.utc),
    )
    return result


def _build_program_context() -> ProgramAnalysisContext:
    return ProgramAnalysisContext(
        field_id="field-123",
        crop_name="corn",
        planting_date=date(2024, 4, 15),
        expected_harvest_date=date(2024, 10, 5),
        fertilizer_requirements={"nitrogen": 180.0, "phosphorus": 60.0},
        soil_type="silty clay loam",
        soil_moisture_capacity=0.58,
        drainage_class="moderate",
        slope_percent=4.5,
        location={"lat": 41.0, "lng": -93.0},
    )


def _build_timing_assessment() -> TimingAssessment:
    return TimingAssessment(
        average_deviation_days=1.5,
        on_time_percentage=0.75,
        early_applications=1,
        late_applications=1,
        critical_risk_events=0,
        deviations=[],
    )


def test_build_explanation_with_context() -> None:
    service = TimingExplanationService()
    optimization_result = _build_optimization_result()
    context = _build_program_context()
    assessment = _build_timing_assessment()

    explanation = service.build_explanation(optimization_result, context, assessment)

    assert isinstance(explanation, TimingExplanation)
    assert "alignment score" in explanation.summary.lower()
    assert len(explanation.key_points) == 2

    has_weather_impact = len(explanation.weather_impacts) > 0
    assert has_weather_impact

    has_educational_guidance = len(explanation.educational_guidance) > 0
    assert has_educational_guidance


def test_build_explanation_without_context_uses_defaults() -> None:
    service = TimingExplanationService()
    optimization_result = _build_optimization_result()

    explanation = service.build_explanation(optimization_result, None, None)

    assert explanation.summary.startswith("Timing optimization achieved")
    weather_items_are_present = len(explanation.weather_impacts) > 0
    assert weather_items_are_present
    references_present = len(explanation.knowledge_references) > 0
    assert references_present
