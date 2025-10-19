"""Tests for the ApplicationWindowAlertService."""

import importlib.util
import sys
from datetime import date, datetime
from pathlib import Path

import pytest

_SRC_DIR = Path(__file__).resolve().parents[1] / "src"
_SRC_PATH = str(_SRC_DIR)
if _SRC_PATH not in sys.path:
    sys.path.insert(0, _SRC_PATH)

_SERVICES_DIR = _SRC_DIR / "services"
_MODULE_PATH = _SERVICES_DIR / "alert_service.py"
_MODULE_SPEC = importlib.util.spec_from_file_location("fertilizer_timing.alert_service", _MODULE_PATH)
if _MODULE_SPEC is None or _MODULE_SPEC.loader is None:
    raise RuntimeError("Unable to load alert_service module for testing")
_ALERT_MODULE = importlib.util.module_from_spec(_MODULE_SPEC)
_MODULE_SPEC.loader.exec_module(_ALERT_MODULE)
ApplicationWindowAlertService = _ALERT_MODULE.ApplicationWindowAlertService

from models import (  # pylint: disable=import-error
    ApplicationMethod,
    ApplicationTiming,
    CropGrowthStage,
    SoilConditionSnapshot,
    TimingAlertResponse,
    TimingOptimizationRequest,
    TimingOptimizationResult,
    WeatherCondition,
    WeatherConditionSummary,
    WeatherSoilIntegrationReport,
    WeatherSoilWindow,
    WeatherWindow,
)


class _StubBaseAlertService:
    def generate_alerts(self, result: TimingOptimizationResult) -> TimingAlertResponse:
        response = TimingAlertResponse(request_id=result.request_id, alerts=[])
        return response

    def to_records(self, response: TimingAlertResponse):
        return []


class _StubWeatherService:
    def __init__(self, report: WeatherSoilIntegrationReport) -> None:
        self._report = report

    async def generate_integration_report(self, request: TimingOptimizationRequest, forecast_days: int = 10):
        return self._report


def _fixed_now() -> datetime:
    return datetime(2025, 5, 1, 6, 0, 0)


def _build_request() -> TimingOptimizationRequest:
    fertilizer_requirements = {}
    fertilizer_requirements["nitrogen"] = 180.0

    methods = []
    methods.append(ApplicationMethod.BROADCAST)

    location = {}
    location["lat"] = 41.6
    location["lng"] = -93.5

    equipment = {}
    labor = {}

    request = TimingOptimizationRequest(
        field_id="field-200",
        crop_type="corn",
        planting_date=date(2025, 4, 20),
        expected_harvest_date=date(2025, 10, 12),
        fertilizer_requirements=fertilizer_requirements,
        application_methods=methods,
        soil_type="silt loam",
        soil_moisture_capacity=0.6,
        drainage_class="well drained",
        slope_percent=2.5,
        weather_data_source="stub",
        location=location,
        equipment_availability=equipment,
        labor_availability=labor,
        optimization_horizon_days=120,
        risk_tolerance=0.5,
        prioritize_yield=True,
        prioritize_cost=False,
        split_application_allowed=True,
        weather_dependent_timing=True,
        soil_temperature_threshold=48.0,
    )
    return request


def _build_weather_window() -> WeatherWindow:
    window = WeatherWindow(
        start_date=date(2025, 5, 5),
        end_date=date(2025, 5, 5),
        condition=WeatherCondition.OPTIMAL,
        temperature_f=66.0,
        precipitation_probability=0.2,
        wind_speed_mph=8.0,
        soil_moisture=0.55,
        suitability_score=0.9,
    )
    return window


def _build_timing(window: WeatherWindow) -> ApplicationTiming:
    alt_dates = []
    alt_dates.append(date(2025, 5, 6))
    timing = ApplicationTiming(
        fertilizer_type="nitrogen",
        application_method=ApplicationMethod.BROADCAST,
        recommended_date=window.start_date,
        application_window=window,
        crop_stage=CropGrowthStage.V6,
        amount_lbs_per_acre=160.0,
        timing_score=0.92,
        weather_score=0.91,
        crop_score=0.88,
        soil_score=0.84,
        weather_risk=0.35,
        timing_risk=0.32,
        equipment_risk=0.28,
        estimated_cost_per_acre=45.0,
        yield_impact_percent=6.0,
        alternative_dates=alt_dates,
        backup_window=None,
    )
    return timing


def _build_result(window: WeatherWindow, timing: ApplicationTiming) -> TimingOptimizationResult:
    weather_windows = []
    weather_windows.append(window)

    timings = []
    timings.append(timing)

    recommendations = []
    recommendations.append("Capitalize on early May window to minimize weather risk.")

    result = TimingOptimizationResult(
        request_id="req-200",
        optimal_timings=timings,
        split_plans=[],
        weather_windows=weather_windows,
        overall_timing_score=0.9,
        weather_suitability_score=0.88,
        crop_stage_alignment_score=0.86,
        risk_score=0.4,
        total_estimated_cost=12000.0,
        cost_per_acre=52.0,
        expected_yield_impact=5.5,
        roi_estimate=1.25,
        recommendations=recommendations,
        risk_mitigation_strategies=[],
        alternative_strategies=[],
        confidence_score=0.82,
        processing_time_ms=2150.0,
    )
    return result


def _build_report(window: WeatherWindow) -> WeatherSoilIntegrationReport:
    limiting = []
    limiting.append("none")
    actions = []
    actions.append("Proceed with standard traffic pattern.")
    soil_snapshot = SoilConditionSnapshot(
        soil_texture="silt loam",
        drainage_class="well drained",
        soil_moisture=0.56,
        soil_temperature_f=52.0,
        trafficability="favorable",
        compaction_risk="low",
        limiting_factors=limiting,
        recommended_actions=actions,
    )

    summary_notes = []
    summary_notes.append("Expect light winds and minimal rainfall.")
    summary = WeatherConditionSummary(
        forecast_days=10,
        precipitation_outlook="Below average rainfall probability",
        temperature_trend="Rising to seasonal norms",
        wind_risk="Low",
        humidity_trend="Moderate",
        advisory_notes=summary_notes,
    )

    windows = []
    window_report = WeatherSoilWindow(
        window=window,
        soil_snapshot=soil_snapshot,
        combined_score=0.9,
        limiting_factor="none",
        recommended_action="Schedule fertilizer tender deliveries one day prior.",
        confidence=0.87,
    )
    windows.append(window_report)

    report = WeatherSoilIntegrationReport(
        request_id="req-200",
        soil_summary=soil_snapshot,
        weather_summary=summary,
        application_windows=windows,
    )
    return report


@pytest.mark.asyncio
async def test_build_alerts_highlights_optimal_window():
    request = _build_request()
    window = _build_weather_window()
    timing = _build_timing(window)
    result = _build_result(window, timing)
    report = _build_report(window)

    base_service = _StubBaseAlertService()
    weather_service = _StubWeatherService(report)

    service = ApplicationWindowAlertService(
        base_alert_service=base_service,
        weather_service=weather_service,  # type: ignore[arg-type]
        timing_adapter=None,  # type: ignore[arg-type]
        now_provider=_fixed_now,
    )

    response = await service.build_alerts(request, result)

    found_optimal = False
    for alert in response.alerts:
        if alert.title == "Optimal window for Corn application":
            found_optimal = True
    assert found_optimal, "Expected optimal window alert was not generated"


@pytest.mark.asyncio
async def test_build_alerts_flags_operational_gaps():
    request = _build_request()
    iso_date = date(2025, 5, 2)
    request.equipment_availability[iso_date.isoformat()] = []
    request.labor_availability[iso_date.isoformat()] = 0

    window = WeatherWindow(
        start_date=iso_date,
        end_date=iso_date,
        condition=WeatherCondition.ACCEPTABLE,
        temperature_f=58.0,
        precipitation_probability=0.35,
        wind_speed_mph=14.0,
        soil_moisture=0.58,
        suitability_score=0.68,
    )

    timing = ApplicationTiming(
        fertilizer_type="nitrogen",
        application_method=ApplicationMethod.BROADCAST,
        recommended_date=iso_date,
        application_window=window,
        crop_stage=CropGrowthStage.V4,
        amount_lbs_per_acre=140.0,
        timing_score=0.78,
        weather_score=0.65,
        crop_score=0.7,
        soil_score=0.64,
        weather_risk=0.62,
        timing_risk=0.5,
        equipment_risk=0.6,
        estimated_cost_per_acre=47.0,
        yield_impact_percent=4.0,
        alternative_dates=[],
        backup_window=None,
    )

    result = _build_result(window, timing)
    report = _build_report(window)

    base_service = _StubBaseAlertService()
    weather_service = _StubWeatherService(report)

    service = ApplicationWindowAlertService(
        base_alert_service=base_service,
        weather_service=weather_service,  # type: ignore[arg-type]
        timing_adapter=None,  # type: ignore[arg-type]
        now_provider=_fixed_now,
    )

    response = await service.build_alerts(request, result)

    found_equipment = False
    found_labor = False
    found_weather = False

    for alert in response.alerts:
        if alert.title.startswith("Equipment readiness gap"):
            found_equipment = True
        if alert.title.startswith("Labor constraint"):
            found_labor = True
        if alert.title.startswith("Weather risk"):
            found_weather = True

    assert found_equipment, "Expected equipment gap alert missing"
    assert found_labor, "Expected labor constraint alert missing"
    assert found_weather, "Expected weather risk alert missing"
