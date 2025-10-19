"""
Advanced weather and soil integration service for fertilizer timing.
"""

import logging
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple

from models import (
    TimingOptimizationRequest,
    WeatherCondition,
    WeatherWindow,
)
from models import (
    SoilConditionSnapshot,
    WeatherConditionSummary,
    WeatherSoilIntegrationReport,
    WeatherSoilWindow,
)
from timing_services import TimingOptimizationAdapter
from utils.module_loader import ensure_service_packages, get_services_root

logger = logging.getLogger(__name__)

_SERVICES_ROOT = get_services_root()
_DATA_INTEGRATION_SRC = _SERVICES_ROOT / "data-integration" / "src"

ensure_service_packages(
    "data_integration",
    {
        "services": _DATA_INTEGRATION_SRC / "services",
        "models": _DATA_INTEGRATION_SRC / "models",
    },
    filesystem_name="data-integration",
)

# pylint: disable=wrong-import-position,import-error
from services.data_integration.src.services.weather_service import (  # type: ignore
    AgriculturalWeatherMetrics,
    ForecastDay,
    WeatherAPIError,
    WeatherService,
)
from services.data_integration.src.services.soil_service import (  # type: ignore
    SoilCharacteristics,
    SoilService,
    SoilDataError,
)
# pylint: enable=wrong-import-position,import-error


class WeatherSoilIntegrationService:
    """
    Integrate advanced weather forecasts with soil conditions to inform timing.
    """

    def __init__(
        self,
        weather_service: Optional[WeatherService] = None,
        soil_service: Optional[SoilService] = None,
        timing_adapter: Optional[TimingOptimizationAdapter] = None,
    ) -> None:
        self._weather_service = weather_service or WeatherService()
        self._soil_service = soil_service or SoilService()
        self._timing_adapter = timing_adapter or TimingOptimizationAdapter()
        self._max_forecast_days = 14
        logger.info("WeatherSoilIntegrationService initialized")

    async def generate_integration_report(
        self,
        request: TimingOptimizationRequest,
        forecast_days: int = 10,
    ) -> WeatherSoilIntegrationReport:
        """
        Produce a comprehensive weather and soil integration report.
        """
        if forecast_days < 1:
            message = "forecast_days must be at least 1"
            raise ValueError(message)

        if forecast_days > self._max_forecast_days:
            forecast_days = self._max_forecast_days

        location = self._extract_location(request)
        forecast = await self._safe_fetch_forecast(location, forecast_days)
        metrics = await self._safe_fetch_agricultural_metrics(location)
        soil_characteristics = await self._safe_fetch_soil_characteristics(location, request)
        soil_snapshot = self._build_soil_snapshot(request, soil_characteristics, metrics, forecast)
        weather_summary = self._build_weather_summary(forecast)
        windows = await self._safe_fetch_weather_windows(request)
        combined_windows = self._build_combined_windows(
            windows,
            soil_snapshot,
            forecast,
        )

        report = WeatherSoilIntegrationReport(
            request_id=request.request_id,
            soil_summary=soil_snapshot,
            weather_summary=weather_summary,
            application_windows=combined_windows,
        )
        return report

    async def _safe_fetch_forecast(
        self,
        location: Dict[str, float],
        forecast_days: int,
    ) -> List[ForecastDay]:
        forecast: List[ForecastDay] = []
        try:
            forecast = await self._weather_service.get_forecast(
                location["lat"],
                location["lng"],
                forecast_days,
            )
        except WeatherAPIError as exc:
            logger.warning("Weather forecast unavailable: %s", exc)
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("Unexpected weather forecast error: %s", exc)
        return forecast

    async def _safe_fetch_agricultural_metrics(
        self,
        location: Dict[str, float],
    ) -> Optional[AgriculturalWeatherMetrics]:
        metrics: Optional[AgriculturalWeatherMetrics] = None
        try:
            metrics = await self._weather_service.get_agricultural_metrics(
                location["lat"],
                location["lng"],
            )
        except WeatherAPIError as exc:
            logger.warning("Agricultural metrics unavailable: %s", exc)
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("Unexpected metrics error: %s", exc)
        return metrics

    async def _safe_fetch_soil_characteristics(
        self,
        location: Dict[str, float],
        request: TimingOptimizationRequest,
    ) -> SoilCharacteristics:
        try:
            return await self._soil_service.get_soil_characteristics(
                location["lat"],
                location["lng"],
            )
        except SoilDataError as exc:
            logger.warning("Soil characteristics unavailable: %s", exc)
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("Unexpected soil data error: %s", exc)
        return self._build_fallback_soil_characteristics(request)

    async def _safe_fetch_weather_windows(
        self,
        request: TimingOptimizationRequest,
    ) -> List[WeatherWindow]:
        windows: List[WeatherWindow] = []
        try:
            windows = await self._timing_adapter.analyze_weather_windows(request)
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("Weather window analysis unavailable: %s", exc)
        return windows

    def _build_weather_summary(
        self,
        forecast: List[ForecastDay],
    ) -> WeatherConditionSummary:
        if not forecast:
            summary = WeatherConditionSummary(
                forecast_days=0,
                precipitation_outlook="insufficient forecast data",
                temperature_trend="unknown",
                wind_risk="unknown",
                humidity_trend="unknown",
                advisory_notes=["Weather forecast unavailable; rely on local observations."],
            )
            return summary

        forecast_length = len(forecast)
        total_precip = 0.0
        significant_precip_days = 0
        windy_days = 0
        first_high = forecast[0].high_temp_f
        last_high = forecast[-1].high_temp_f
        first_humidity = forecast[0].humidity_percent
        last_humidity = forecast[-1].humidity_percent
        advisory_notes: List[str] = []

        index = 0
        while index < forecast_length:
            day = forecast[index]
            total_precip += day.precipitation_amount
            if day.precipitation_chance >= 0.6:
                significant_precip_days += 1
            if day.wind_speed_mph >= 18.0:
                windy_days += 1
            index += 1

        precipitation_outlook = self._classify_precipitation_outlook(
            total_precip,
            significant_precip_days,
        )
        temperature_trend = self._classify_temperature_trend(first_high, last_high)
        wind_risk = self._classify_wind_risk(windy_days, forecast_length)
        humidity_trend = self._classify_humidity_trend(first_humidity, last_humidity)
        self._append_weather_advisories(
            advisory_notes,
            precipitation_outlook,
            wind_risk,
        )

        summary = WeatherConditionSummary(
            forecast_days=forecast_length,
            precipitation_outlook=precipitation_outlook,
            temperature_trend=temperature_trend,
            wind_risk=wind_risk,
            humidity_trend=humidity_trend,
            advisory_notes=advisory_notes,
        )
        return summary

    def _build_soil_snapshot(
        self,
        request: TimingOptimizationRequest,
        soil_characteristics: SoilCharacteristics,
        metrics: Optional[AgriculturalWeatherMetrics],
        forecast: List[ForecastDay],
    ) -> SoilConditionSnapshot:
        soil_texture = soil_characteristics.soil_texture
        moisture_estimate = self._estimate_soil_moisture(request, metrics, forecast)
        soil_temperature = None
        if metrics is not None and metrics.soil_temperature_f is not None:
            soil_temperature = metrics.soil_temperature_f

        trafficability, compaction_risk = self._assess_trafficability(
            soil_texture,
            soil_characteristics.drainage_class,
            moisture_estimate,
        )
        limiting_factors: List[str] = []
        recommended_actions: List[str] = []
        self._populate_soil_observations(
            limiting_factors,
            recommended_actions,
            moisture_estimate,
            trafficability,
            compaction_risk,
            soil_texture,
            metrics,
        )

        snapshot = SoilConditionSnapshot(
            soil_texture=soil_texture,
            drainage_class=soil_characteristics.drainage_class,
            soil_moisture=moisture_estimate,
            soil_temperature_f=soil_temperature,
            trafficability=trafficability,
            compaction_risk=compaction_risk,
            limiting_factors=limiting_factors,
            recommended_actions=recommended_actions,
        )
        return snapshot

    def _build_combined_windows(
        self,
        windows: List[WeatherWindow],
        base_snapshot: SoilConditionSnapshot,
        forecast: List[ForecastDay],
    ) -> List[WeatherSoilWindow]:
        combined: List[WeatherSoilWindow] = []
        forecast_map = self._build_forecast_map(forecast)

        index = 0
        count = len(windows)
        while index < count:
            window = windows[index]
            snapshot = self._adjust_snapshot_for_window(base_snapshot, window, forecast_map)
            soil_factor = self._score_soil_snapshot(snapshot)
            combined_score = self._combine_scores(window.suitability_score, soil_factor)
            limiting_factor = self._determine_limiting_factor(window, snapshot)
            recommended_action = self._determine_window_action(window, snapshot)
            confidence = self._calculate_confidence(window.suitability_score, soil_factor)

            record = WeatherSoilWindow(
                window=window,
                soil_snapshot=snapshot,
                combined_score=combined_score,
                limiting_factor=limiting_factor,
                recommended_action=recommended_action,
                confidence=confidence,
            )
            combined.append(record)
            index += 1

        return combined

    def _estimate_soil_moisture(
        self,
        request: TimingOptimizationRequest,
        metrics: Optional[AgriculturalWeatherMetrics],
        forecast: List[ForecastDay],
    ) -> float:
        moisture = request.soil_moisture_capacity

        if metrics is not None:
            if metrics.days_since_rain > 5:
                moisture -= 0.1
            if metrics.days_since_rain > 9:
                moisture -= 0.1
            if metrics.days_since_rain == 0 and metrics.accumulated_precipitation > 0.5:
                moisture += 0.1
            if metrics.days_since_rain <= 1 and metrics.accumulated_precipitation > 1.0:
                moisture += 0.05

        limit = min(3, len(forecast))
        index = 0
        while index < limit:
            day = forecast[index]
            if day.precipitation_chance >= 0.7:
                moisture += 0.06
            elif day.precipitation_chance <= 0.2 and day.precipitation_amount < 0.1:
                moisture -= 0.04
            index += 1

        moisture = self._clamp_value(moisture, 0.0, 1.0)
        return moisture

    def _assess_trafficability(
        self,
        soil_texture: str,
        drainage_class: str,
        moisture: float,
    ) -> Tuple[str, str]:
        moisture_threshold = 0.65
        trafficability = "favorable"
        compaction_risk = "moderate"

        if moisture >= 0.8:
            trafficability = "limited"
            compaction_risk = "high"
        elif moisture >= moisture_threshold:
            trafficability = "cautious"
            compaction_risk = "elevated"
        else:
            trafficability = "favorable"
            compaction_risk = "moderate"

        texture_lower = soil_texture.lower() if soil_texture else ""
        if self._contains_keyword(texture_lower, "clay") and moisture >= 0.6:
            trafficability = "cautious"
            compaction_risk = "high"

        drainage_lower = drainage_class.lower() if drainage_class else ""
        if self._contains_keyword(drainage_lower, "poor"):
            if moisture >= 0.5:
                trafficability = "limited"

        return trafficability, compaction_risk

    def _populate_soil_observations(
        self,
        limiting_factors: List[str],
        recommended_actions: List[str],
        moisture: float,
        trafficability: str,
        compaction_risk: str,
        soil_texture: str,
        metrics: Optional[AgriculturalWeatherMetrics],
    ) -> None:
        if moisture >= 0.8:
            limiting_factors.append("Soil moisture near saturation increases rutting risk.")
        elif moisture <= 0.35:
            limiting_factors.append("Soil moisture is low; nutrient uptake may be reduced.")

        if trafficability == "limited":
            limiting_factors.append("Field access is restricted due to soft conditions.")
        if compaction_risk == "high":
            limiting_factors.append("High compaction risk from heavy equipment.")

        if self._contains_keyword(soil_texture.lower() if soil_texture else "", "sand"):
            limiting_factors.append("Sandy soils can leach nutrients quickly after heavy rain.")

        if moisture >= 0.75:
            recommended_actions.append("Delay heavy equipment until soils firm up.")
        if moisture <= 0.4:
            recommended_actions.append("Consider irrigation or wait for moisture before application.")
        if compaction_risk == "high":
            recommended_actions.append("Use lighter equipment or reduced tire pressure to limit compaction.")

        if metrics is not None:
            if metrics.soil_temperature_f is not None and metrics.soil_temperature_f < 45.0:
                limiting_factors.append("Soil temperature below optimum for nutrient uptake.")
                recommended_actions.append("Delay nitrogen application until soils warm above 45°F.")

    def _adjust_snapshot_for_window(
        self,
        base_snapshot: SoilConditionSnapshot,
        window: WeatherWindow,
        forecast_map: Dict[date, ForecastDay],
    ) -> SoilConditionSnapshot:
        snapshot_dict = base_snapshot.model_dump()
        soil_moisture = snapshot_dict.get("soil_moisture", 0.5)
        forecast_day = forecast_map.get(window.start_date)

        if forecast_day is not None:
            if forecast_day.precipitation_chance >= 0.6 and forecast_day.precipitation_amount > 0.2:
                soil_moisture += 0.05
            if forecast_day.precipitation_chance <= 0.25 and forecast_day.precipitation_amount < 0.1:
                soil_moisture -= 0.03
            if forecast_day.wind_speed_mph >= 20.0:
                soil_moisture -= 0.02

        soil_moisture = self._clamp_value(soil_moisture, 0.0, 1.0)
        snapshot_dict["soil_moisture"] = soil_moisture

        texture = snapshot_dict.get("soil_texture") or ""
        trafficability, compaction_risk = self._assess_trafficability(
            texture,
            snapshot_dict.get("drainage_class") or "",
            soil_moisture,
        )
        snapshot_dict["trafficability"] = trafficability
        snapshot_dict["compaction_risk"] = compaction_risk

        limiting_factors: List[str] = []
        recommended_actions: List[str] = []
        metrics = None
        self._populate_soil_observations(
            limiting_factors,
            recommended_actions,
            soil_moisture,
            trafficability,
            compaction_risk,
            texture,
            metrics,
        )
        snapshot_dict["limiting_factors"] = limiting_factors
        snapshot_dict["recommended_actions"] = recommended_actions

        snapshot = SoilConditionSnapshot(**snapshot_dict)
        return snapshot

    def _score_soil_snapshot(
        self,
        snapshot: SoilConditionSnapshot,
    ) -> float:
        soil_factor = 0.7

        moisture = snapshot.soil_moisture
        if moisture < 0.35:
            soil_factor -= 0.25
        elif moisture > 0.75:
            soil_factor -= 0.2
        else:
            soil_factor += 0.05

        if snapshot.trafficability == "limited":
            soil_factor -= 0.25
        elif snapshot.trafficability == "cautious":
            soil_factor -= 0.1
        else:
            soil_factor += 0.05

        if snapshot.compaction_risk == "high":
            soil_factor -= 0.2
        elif snapshot.compaction_risk == "elevated":
            soil_factor -= 0.1

        soil_factor = self._clamp_value(soil_factor, 0.0, 1.0)
        return soil_factor

    def _combine_scores(
        self,
        weather_score: float,
        soil_score: float,
    ) -> float:
        combined = (weather_score * 0.6) + (soil_score * 0.4)
        combined = self._clamp_value(combined, 0.0, 1.0)
        return combined

    def _determine_limiting_factor(
        self,
        window: WeatherWindow,
        snapshot: SoilConditionSnapshot,
    ) -> str:
        if window.condition in (WeatherCondition.POOR, WeatherCondition.UNACCEPTABLE):
            return "weather_condition"
        if snapshot.trafficability == "limited":
            return "trafficability"
        if snapshot.compaction_risk == "high":
            return "compaction_risk"
        if snapshot.soil_moisture < 0.4:
            return "soil_moisture"
        return "balanced"

    def _determine_window_action(
        self,
        window: WeatherWindow,
        snapshot: SoilConditionSnapshot,
    ) -> str:
        if window.condition == WeatherCondition.OPTIMAL and snapshot.trafficability == "favorable":
            return "Proceed with planned application."

        if snapshot.trafficability == "limited":
            return "Delay application until soils support equipment traffic."
        if snapshot.compaction_risk == "high":
            return "Use low-impact equipment or wait for drier conditions."
        if snapshot.soil_moisture < 0.4:
            return "Supplement moisture or monitor crop stress before applying."

        if window.condition == WeatherCondition.MARGINAL:
            return "Monitor forecast closely; have contingency plan for weather delays."
        if window.condition == WeatherCondition.POOR:
            return "Identify alternate window to avoid weather losses."
        return "Proceed with caution and monitor on-site conditions."

    def _calculate_confidence(
        self,
        weather_score: float,
        soil_score: float,
    ) -> float:
        confidence = (weather_score + soil_score) / 2.0
        confidence = self._clamp_value(confidence, 0.0, 1.0)
        return confidence

    def _classify_precipitation_outlook(
        self,
        total_precip: float,
        significant_precip_days: int,
    ) -> str:
        if significant_precip_days >= 3 or total_precip > 2.0:
            return "frequent rainfall expected"
        if significant_precip_days >= 1 or total_precip > 0.75:
            return "scattered showers in forecast"
        return "minimal precipitation expected"

    def _classify_temperature_trend(
        self,
        first_high: float,
        last_high: float,
    ) -> str:
        difference = last_high - first_high
        if difference >= 6.0:
            return "warming trend"
        if difference <= -6.0:
            return "cooling trend"
        return "stable temperatures"

    def _classify_wind_risk(
        self,
        windy_days: int,
        forecast_length: int,
    ) -> str:
        if windy_days >= max(2, forecast_length // 3):
            return "high wind risk"
        if windy_days >= 1:
            return "moderate wind risk"
        return "low wind risk"

    def _classify_humidity_trend(
        self,
        first_value: float,
        last_value: float,
    ) -> str:
        difference = last_value - first_value
        if difference >= 10.0:
            return "increasing humidity"
        if difference <= -10.0:
            return "decreasing humidity"
        return "stable humidity"

    def _append_weather_advisories(
        self,
        notes: List[str],
        precipitation_outlook: str,
        wind_risk: str,
    ) -> None:
        if precipitation_outlook == "frequent rainfall expected":
            notes.append("Prepare contingency plan for rainfall delays.")
            notes.append("Avoid surface applications immediately before heavy rain.")
        elif precipitation_outlook == "scattered showers in forecast":
            notes.append("Monitor radar prior to application windows for pop-up showers.")

        if wind_risk == "high wind risk":
            notes.append("Consider postponing foliar or aerial applications due to wind drift.")
        elif wind_risk == "moderate wind risk":
            notes.append("Schedule applications for early morning when winds are calmer.")

    def _build_forecast_map(
        self,
        forecast: List[ForecastDay],
    ) -> Dict[date, ForecastDay]:
        mapping: Dict[date, ForecastDay] = {}
        index = 0
        count = len(forecast)
        while index < count:
            day = forecast[index]
            parsed_date = self._parse_forecast_date(day.date)
            if parsed_date is not None and parsed_date not in mapping:
                mapping[parsed_date] = day
            index += 1
        return mapping

    def _parse_forecast_date(
        self,
        date_str: str,
    ) -> Optional[date]:
        try:
            parsed = datetime.strptime(date_str, "%Y-%m-%d").date()
            return parsed
        except ValueError:
            logger.debug("Unable to parse forecast date: %s", date_str)
        return None

    def _build_fallback_soil_characteristics(
        self,
        request: TimingOptimizationRequest,
    ) -> SoilCharacteristics:
        texture = request.soil_type or "Loam"
        ph_range = {"min": 6.0, "max": 7.0}
        slope_description = f"{request.slope_percent:.1f}% slope"
        characteristics = SoilCharacteristics(
            soil_series="Unknown",
            soil_texture=texture,
            drainage_class=request.drainage_class or "moderate",
            typical_ph_range=ph_range,
            organic_matter_typical=3.0,
            slope_range=slope_description,
            parent_material=None,
            depth_to_bedrock=None,
            flooding_frequency=None,
            ponding_frequency=None,
            hydrologic_group=None,
            available_water_capacity=request.soil_moisture_capacity,
            permeability=None,
            erosion_factor_k=None,
        )
        return characteristics

    def _contains_keyword(
        self,
        value: str,
        keyword: str,
    ) -> bool:
        if value is None or keyword is None:
            return False
        return keyword in value

    def _clamp_value(
        self,
        value: float,
        minimum: float,
        maximum: float,
    ) -> float:
        if value < minimum:
            return minimum
        if value > maximum:
            return maximum
        return value

    def _extract_location(
        self,
        request: TimingOptimizationRequest,
    ) -> Dict[str, float]:
        location = request.location or {}
        if "lat" not in location or "lng" not in location:
            message = "Timing request must include location with 'lat' and 'lng'."
            raise ValueError(message)
        return location


__all__ = ["WeatherSoilIntegrationService"]
