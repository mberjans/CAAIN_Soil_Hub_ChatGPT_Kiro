"""Tests for the WeatherSoilIntegrationService."""

import sys
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional
import types

import pytest

_SRC_DIR = Path(__file__).resolve().parents[1] / "src"
_SRC_PATH = str(_SRC_DIR)
if _SRC_PATH not in sys.path:
    sys.path.insert(0, _SRC_PATH)

_SERVICES_DIR = _SRC_DIR / "services"
_SERVICES_PATH = str(_SERVICES_DIR)
if _SERVICES_PATH not in sys.path:
    sys.path.insert(0, _SERVICES_PATH)

_stub_timing_services = types.ModuleType("timing_services")


class _ImportedAdapterStub:
    async def analyze_weather_windows(self, request):
        return []


_stub_timing_services.TimingOptimizationAdapter = _ImportedAdapterStub
sys.modules["timing_services"] = _stub_timing_services

from models import (  # pylint: disable=import-error
    ApplicationMethod,
    TimingOptimizationRequest,
    WeatherCondition,
    WeatherWindow,
)
from weather_integration_service import WeatherSoilIntegrationService  # pylint: disable=import-error


class _StubForecastDay:
    def __init__(
        self,
        day_str: str,
        high: float,
        low: float,
        precip_chance: float,
        precip_amount: float,
        wind_speed: float,
        humidity: float,
    ) -> None:
        self.date = day_str
        self.high_temp_f = high
        self.low_temp_f = low
        self.precipitation_chance = precip_chance
        self.precipitation_amount = precip_amount
        self.conditions = "Partly Cloudy"
        self.wind_speed_mph = wind_speed
        self.humidity_percent = humidity


class _StubMetrics:
    def __init__(
        self,
        soil_temperature: Optional[float],
        days_since_rain: int,
        accumulated_precipitation: float,
    ) -> None:
        self.soil_temperature_f = soil_temperature
        self.days_since_rain = days_since_rain
        self.accumulated_precipitation = accumulated_precipitation


class _StubSoilCharacteristics:
    def __init__(self) -> None:
        self.soil_series = "Sample"
        self.soil_texture = "silt loam"
        self.drainage_class = "well drained"
        self.typical_ph_range = {"min": 6.2, "max": 6.8}
        self.organic_matter_typical = 3.2
        self.slope_range = "2%"
        self.parent_material = None
        self.depth_to_bedrock = None
        self.flooding_frequency = None
        self.ponding_frequency = None
        self.hydrologic_group = None
        self.available_water_capacity = 0.62
        self.permeability = None
        self.erosion_factor_k = None


class _StubWeatherService:
    def __init__(self) -> None:
        self._forecast: List[_StubForecastDay] = []
        self._metrics: Optional[_StubMetrics] = None

    def set_forecast(self, items: List[_StubForecastDay]) -> None:
        self._forecast = items

    def set_metrics(self, metrics: Optional[_StubMetrics]) -> None:
        self._metrics = metrics

    async def get_forecast(self, latitude: float, longitude: float, days: int) -> List[_StubForecastDay]:
        return self._forecast

    async def get_agricultural_metrics(self, latitude: float, longitude: float) -> Optional[_StubMetrics]:
        return self._metrics


class _StubSoilService:
    def __init__(self, characteristics: _StubSoilCharacteristics) -> None:
        self._characteristics = characteristics

    async def get_soil_characteristics(self, latitude: float, longitude: float) -> _StubSoilCharacteristics:
        return self._characteristics


class _StubTimingAdapter:
    def __init__(self, windows: List[WeatherWindow]) -> None:
        self._windows = windows

    async def analyze_weather_windows(self, request: TimingOptimizationRequest) -> List[WeatherWindow]:
        return self._windows


def _build_request() -> TimingOptimizationRequest:
    fertilizer_requirements: Dict[str, float] = {}
    fertilizer_requirements["nitrogen"] = 180.0

    application_methods: List[ApplicationMethod] = []
    application_methods.append(ApplicationMethod.BROADCAST)

    equipment_availability: Dict[str, List[str]] = {}
    labor_availability: Dict[str, int] = {}

    location: Dict[str, float] = {}
    location["lat"] = 41.5
    location["lng"] = -93.4

    request = TimingOptimizationRequest(
        field_id="field-100",
        crop_type="corn",
        planting_date=date(2025, 4, 20),
        expected_harvest_date=date(2025, 10, 10),
        fertilizer_requirements=fertilizer_requirements,
        application_methods=application_methods,
        soil_type="silt loam",
        soil_moisture_capacity=0.6,
        drainage_class="well drained",
        slope_percent=3.0,
        weather_data_source="stub",
        location=location,
        equipment_availability=equipment_availability,
        labor_availability=labor_availability,
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
        temperature_f=65.0,
        precipitation_probability=0.2,
        wind_speed_mph=8.0,
        soil_moisture=0.55,
        suitability_score=0.85,
    )
    return window


@pytest.mark.asyncio
async def test_generate_integration_report_produces_combined_windows():
    request = _build_request()
    forecast: List[_StubForecastDay] = []
    forecast.append(_StubForecastDay("2025-05-05", 68.0, 50.0, 0.3, 0.2, 10.0, 55.0))
    forecast.append(_StubForecastDay("2025-05-06", 70.0, 51.0, 0.15, 0.05, 12.0, 52.0))
    metrics = _StubMetrics(soil_temperature=52.0, days_since_rain=2, accumulated_precipitation=0.8)

    weather_service = _StubWeatherService()
    weather_service.set_forecast(forecast)
    weather_service.set_metrics(metrics)

    soil_characteristics = _StubSoilCharacteristics()
    soil_service = _StubSoilService(soil_characteristics)

    windows: List[WeatherWindow] = []
    windows.append(_build_weather_window())
    timing_adapter = _StubTimingAdapter(windows)

    service = WeatherSoilIntegrationService(
        weather_service=weather_service,  # type: ignore[arg-type]
        soil_service=soil_service,  # type: ignore[arg-type]
        timing_adapter=timing_adapter,
    )

    report = await service.generate_integration_report(request, forecast_days=2)

    assert report.request_id == request.request_id
    assert report.weather_summary.forecast_days == 2
    assert report.soil_summary.trafficability in ("favorable", "cautious", "limited")
    assert len(report.application_windows) == 1

    first_window = report.application_windows[0]
    assert 0.0 <= first_window.combined_score <= 1.0
    assert 0.0 <= first_window.confidence <= 1.0
    assert isinstance(first_window.recommended_action, str)


@pytest.mark.asyncio
async def test_generate_integration_report_handles_missing_forecast():
    request = _build_request()

    weather_service = _StubWeatherService()
    weather_service.set_forecast([])
    weather_service.set_metrics(None)

    soil_characteristics = _StubSoilCharacteristics()
    soil_service = _StubSoilService(soil_characteristics)

    windows: List[WeatherWindow] = []
    windows.append(_build_weather_window())
    timing_adapter = _StubTimingAdapter(windows)

    service = WeatherSoilIntegrationService(
        weather_service=weather_service,  # type: ignore[arg-type]
        soil_service=soil_service,  # type: ignore[arg-type]
        timing_adapter=timing_adapter,
    )

    report = await service.generate_integration_report(request, forecast_days=2)

    assert report.weather_summary.forecast_days == 0
    assert "unavailable" in report.weather_summary.advisory_notes[0].lower()
    first_window = report.application_windows[0]
    assert isinstance(first_window.recommended_action, str)
    assert first_window.window.suitability_score == 0.85
