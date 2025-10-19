"""Tests for the comprehensive seasonal calendar service."""

import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List

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
    CropGrowthStage,
    SplitApplicationPlan,
    TimingOptimizationRequest,
    TimingOptimizationResult,
    WeatherCondition,
    WeatherWindow,
)
from calendar_service import SeasonalCalendarService  # pylint: disable=import-error


class _StubTimingAdapter:
    """Stub timing adapter returning predefined results per request."""

    def __init__(self, results: Dict[str, TimingOptimizationResult]) -> None:
        self._results = results

    async def optimize(self, request: TimingOptimizationRequest) -> TimingOptimizationResult:
        if request.request_id in self._results:
            return self._results[request.request_id]
        raise RuntimeError("No stubbed result provided for request")


def _build_weather_window(start: date) -> WeatherWindow:
    return WeatherWindow(
        start_date=start,
        end_date=start,
        condition=WeatherCondition.OPTIMAL,
        temperature_f=64.0,
        precipitation_probability=0.15,
        wind_speed_mph=9.0,
        soil_moisture=0.55,
        suitability_score=0.86,
    )


def _build_application_timing(target_date: date, fertilizer: str) -> ApplicationTiming:
    weather_window = _build_weather_window(target_date)
    return ApplicationTiming(
        fertilizer_type=fertilizer,
        application_method=ApplicationMethod.SIDE_DRESS,
        recommended_date=target_date,
        application_window=weather_window,
        crop_stage=CropGrowthStage.V6,
        amount_lbs_per_acre=110.0,
        timing_score=0.9,
        weather_score=0.8,
        crop_score=0.82,
        soil_score=0.75,
        weather_risk=0.2,
        timing_risk=0.15,
        equipment_risk=0.1,
        estimated_cost_per_acre=72.0,
        yield_impact_percent=6.0,
        alternative_dates=[],
        backup_window=None,
    )


def _build_split_plan(target_date: date) -> SplitApplicationPlan:
    base_application = _build_application_timing(target_date, "nitrogen")
    second_application = _build_application_timing(target_date + timedelta(days=10), "nitrogen")
    applications: List[ApplicationTiming] = []
    applications.append(base_application)
    applications.append(second_application)

    ratios: List[float] = []
    ratios.append(0.6)
    ratios.append(0.4)

    return SplitApplicationPlan(
        fertilizer_type="nitrogen",
        total_amount_lbs_per_acre=180.0,
        applications=applications,
        split_ratio=ratios,
        total_timing_score=0.82,
        risk_reduction_percent=12.0,
        cost_impact_percent=3.0,
    )


def _build_timing_result(request_id: str, target_date: date) -> TimingOptimizationResult:
    applications: List[ApplicationTiming] = []
    applications.append(_build_application_timing(target_date, "nitrogen"))

    weather_windows: List[WeatherWindow] = []
    weather_windows.append(_build_weather_window(target_date))

    split_plans: List[SplitApplicationPlan] = []
    split_plans.append(_build_split_plan(target_date))

    recommendations: List[str] = []
    recommendations.append("Follow nitrogen sidedress window.")

    return TimingOptimizationResult(
        request_id=request_id,
        optimal_timings=applications,
        split_plans=split_plans,
        weather_windows=weather_windows,
        weather_forecast_days=14,
        overall_timing_score=0.88,
        weather_suitability_score=0.81,
        crop_stage_alignment_score=0.83,
        risk_score=0.28,
        total_estimated_cost=12500.0,
        cost_per_acre=90.0,
        expected_yield_impact=5.0,
        roi_estimate=0.21,
        recommendations=recommendations,
        risk_mitigation_strategies=[],
        alternative_strategies=[],
        optimization_method="multi_objective",
        confidence_score=0.72,
        processing_time_ms=245.0,
        created_at=datetime.utcnow(),
    )


def _build_request(request_id: str, equipment: Dict[str, List[str]], labor: Dict[str, int]) -> TimingOptimizationRequest:
    application_methods: List[ApplicationMethod] = []
    application_methods.append(ApplicationMethod.SIDE_DRESS)

    fertilizer_requirements: Dict[str, float] = {}
    fertilizer_requirements["nitrogen"] = 180.0

    return TimingOptimizationRequest(
        request_id=request_id,
        field_id="field-001",
        crop_type="corn",
        planting_date=date(2024, 4, 10),
        expected_harvest_date=date(2024, 10, 1),
        fertilizer_requirements=fertilizer_requirements,
        application_methods=application_methods,
        soil_type="silty clay loam",
        soil_moisture_capacity=0.58,
        drainage_class="moderate",
        slope_percent=4.0,
        weather_data_source="noaa",
        location={"lat": 41.0, "lng": -93.0},
        equipment_availability=equipment,
        labor_availability=labor,
        optimization_horizon_days=120,
        risk_tolerance=0.4,
        prioritize_yield=True,
        prioritize_cost=False,
        split_application_allowed=True,
        weather_dependent_timing=True,
        soil_temperature_threshold=50.0,
    )


@pytest.mark.asyncio
async def test_generate_calendar_includes_split_entries():
    request = _build_request(
        "req-split",
        {"toolbar": ["2024-05-10", "2024-05-20"]},
        {"2024-05-10": 3, "2024-05-20": 2},
    )
    result = _build_timing_result(request.request_id, date(2024, 5, 10))
    adapter = _StubTimingAdapter({request.request_id: result})
    service = SeasonalCalendarService(adapter=adapter)

    calendar = await service.generate_calendar(request)

    split_found = False
    for entry in calendar.entries:
        if entry.event_type == "split_application":
            split_found = True
            break

    assert split_found, "Expected at least one split application entry"


@pytest.mark.asyncio
async def test_generate_calendar_applies_operational_notes():
    request = _build_request("req-ops", {}, {})
    result = _build_timing_result(request.request_id, date(2024, 5, 12))
    adapter = _StubTimingAdapter({request.request_id: result})
    service = SeasonalCalendarService(adapter=adapter)

    calendar = await service.generate_calendar(request)

    description_found = False
    for entry in calendar.entries:
        if entry.event_type == "fertilizer_application":
            if "Coordinate equipment scheduling." in entry.description:
                if "Schedule labor support." in entry.description:
                    description_found = True
                    break

    assert description_found, "Expected operational guidance in calendar entry description"


@pytest.mark.asyncio
async def test_generate_multi_crop_calendar_produces_multiple_calendars():
    first_request = _build_request(
        "req-1",
        {"applicator": ["2024-05-10"]},
        {"2024-05-10": 4},
    )
    second_request = _build_request(
        "req-2",
        {"boom": ["2024-05-15"]},
        {"2024-05-15": 2},
    )

    first_result = _build_timing_result(first_request.request_id, date(2024, 5, 10))
    second_result = _build_timing_result(second_request.request_id, date(2024, 5, 15))

    results: Dict[str, TimingOptimizationResult] = {}
    results[first_request.request_id] = first_result
    results[second_request.request_id] = second_result

    adapter = _StubTimingAdapter(results)
    service = SeasonalCalendarService(adapter=adapter)

    requests_list: List[TimingOptimizationRequest] = []
    requests_list.append(first_request)
    requests_list.append(second_request)

    calendars = await service.generate_multi_crop_calendar(requests_list)

    assert isinstance(calendars, dict)
    assert len(calendars) == 2
    assert first_request.request_id in calendars
    assert second_request.request_id in calendars
