"""
Comprehensive application window alert orchestration service.

This module builds on the foundational ``TimingAlertService`` to deliver
personalized, weather-aware, and operationally-aware alerts that highlight
the best fertilizer application windows and surface emerging risks.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Callable, Dict, Iterable, List, Optional, Tuple

from database import TimingAlertRecord
from models import (
    ApplicationTiming,
    TimingAlert,
    TimingAlertResponse,
    TimingOptimizationRequest,
    TimingOptimizationResult,
    WeatherCondition,
    WeatherWindow,
    SoilConditionSnapshot,
    WeatherConditionSummary,
    WeatherSoilIntegrationReport,
    WeatherSoilWindow,
)
from timing_services import TimingAlertService, TimingOptimizationAdapter

if TYPE_CHECKING:
    from services.weather_integration_service import WeatherSoilIntegrationService  # pragma: no cover

logger = logging.getLogger(__name__)


class ApplicationWindowAlertService:
    """
    High-level alert coordinator for optimal fertilizer application windows.

    Responsibilities:
    - Run timing optimization (or accept a precomputed result)
    - Merge base optimization alerts with weather and soil intelligence
    - Highlight peak opportunity windows with channel recommendations
    - Surface equipment and labor readiness gaps ahead of key windows
    """

    def __init__(
        self,
        base_alert_service: Optional[TimingAlertService] = None,
        weather_service: Optional["WeatherSoilIntegrationService"] = None,
        timing_adapter: Optional[TimingOptimizationAdapter] = None,
        now_provider: Optional[Callable[[], datetime]] = None,
    ) -> None:
        self._base_alert_service = base_alert_service or TimingAlertService()
        self._weather_service = weather_service or self._load_weather_service()
        self._adapter = timing_adapter or TimingOptimizationAdapter()
        self._now_provider = now_provider or datetime.utcnow
        self._optimal_threshold = 0.82
        self._horizon_days = 10
        logger.info("ApplicationWindowAlertService initialized with enriched alerting workflow")

    async def generate_alerts(
        self,
        request: TimingOptimizationRequest,
    ) -> Tuple[TimingAlertResponse, TimingOptimizationResult]:
        """
        Run a fresh optimization and build comprehensive alerts.
        """
        logger.info("Generating comprehensive alerts for request %s", request.request_id)
        result = await self._adapter.optimize(request)
        enriched_response = await self.build_alerts(request, result)
        return enriched_response, result

    async def build_alerts(
        self,
        request: TimingOptimizationRequest,
        result: TimingOptimizationResult,
    ) -> TimingAlertResponse:
        """
        Build enriched alerts based on an existing optimization result.
        """
        base_response = self._base_alert_service.generate_alerts(result)
        alerts: List[TimingAlert] = []
        existing_titles: Dict[str, bool] = {}

        for base_alert in base_response.alerts:
            alerts.append(base_alert)
            existing_titles[base_alert.title] = True

        report: Optional[WeatherSoilIntegrationReport] = None
        try:
            report = await self._weather_service.generate_integration_report(
                request,
                forecast_days=self._horizon_days,
            )
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("Weather integration unavailable, proceeding with base alerts: %s", exc)

        self._append_optimal_window_alerts(alerts, existing_titles, result, report, request)
        self._append_operational_alerts(alerts, existing_titles, result, request, report)
        self._append_weather_gap_alert(result.request_id, alerts, existing_titles, result.weather_windows, report)

        enriched_response = TimingAlertResponse(
            request_id=result.request_id,
            generated_at=self._now_provider(),
            alerts=alerts,
        )
        return enriched_response

    def to_records(self, response: TimingAlertResponse) -> List[TimingAlertRecord]:
        """
        Convert alerts to database records using the base service implementation.
        """
        return self._base_alert_service.to_records(response)

    def _append_optimal_window_alerts(
        self,
        alerts: List[TimingAlert],
        existing_titles: Dict[str, bool],
        result: TimingOptimizationResult,
        report: Optional[WeatherSoilIntegrationReport],
        request: TimingOptimizationRequest,
    ) -> None:
        top_window: Optional[WeatherSoilWindow] = None
        if report is not None:
            for candidate in report.application_windows:
                if top_window is None:
                    top_window = candidate
                else:
                    if candidate.combined_score > top_window.combined_score:
                        top_window = candidate

        if top_window is None:
            top_window = self._select_best_window(result.weather_windows)

        if top_window is None:
            return

        combined_score = top_window.combined_score if report is not None else top_window.window.suitability_score
        if combined_score < self._optimal_threshold:
            return

        window = top_window.window
        summary = self._build_window_summary(window)
        title = f"Optimal window for {request.crop_type.title()} application"
        if title in existing_titles:
            return

        severity = "info"
        message_parts: List[str] = []
        message_parts.append(f"Upcoming window on {window.start_date.isoformat()} scored {combined_score:.2f}.")
        message_parts.append(summary)
        if report is not None:
            soil_text = self._build_soil_summary(report)
            if soil_text is not None:
                message_parts.append(soil_text)

        message = " ".join(message_parts)
        factors: List[str] = []
        channels = self._determine_channels(severity)
        for channel in channels:
            factors.append(f"Notify via {channel.upper()}")

        factors.append(f"Field: {request.field_id}")
        factors.append(f"Crop: {request.crop_type.title()}")

        alert = TimingAlert(
            request_id=result.request_id,
            severity=severity,
            title=title,
            message=message,
            action="Prepare equipment and labor to capitalize on the highlighted window.",
            factors=factors,
        )
        alerts.append(alert)
        existing_titles[title] = True

        if report is not None:
            self._append_closing_window_alert(alerts, existing_titles, top_window, result, request)

    def _append_closing_window_alert(
        self,
        alerts: List[TimingAlert],
        existing_titles: Dict[str, bool],
        window: WeatherSoilWindow,
        result: TimingOptimizationResult,
        request: TimingOptimizationRequest,
    ) -> None:
        now = self._now_provider().date()
        days_until_start = (window.window.start_date - now).days
        if days_until_start < 0:
            return

        if days_until_start > 2:
            return

        title = f"Application window closing soon for {request.field_id}"
        if title in existing_titles:
            return

        severity = "warning"
        message = (
            f"The optimal window beginning {window.window.start_date.isoformat()} is approaching quickly "
            f"with a combined readiness score of {window.combined_score:.2f}. Plan labor and equipment now."
        )
        action = "Confirm staffing and equipment availability within the next 24 hours."
        factors: List[str] = []
        channels = self._determine_channels(severity)
        for channel in channels:
            factors.append(f"Escalate via {channel.upper()}")
        factors.append(f"Soil trafficability: {window.soil_snapshot.trafficability}")
        factors.append(f"Compaction risk: {window.soil_snapshot.compaction_risk}")

        alert = TimingAlert(
            request_id=result.request_id,
            severity=severity,
            title=title,
            message=message,
            action=action,
            factors=factors,
        )
        alerts.append(alert)
        existing_titles[title] = True

    def _append_operational_alerts(
        self,
        alerts: List[TimingAlert],
        existing_titles: Dict[str, bool],
        result: TimingOptimizationResult,
        request: TimingOptimizationRequest,
        report: Optional[WeatherSoilIntegrationReport],
    ) -> None:
        best_timing: Optional[ApplicationTiming] = None
        best_score = -1.0
        for candidate in result.optimal_timings:
            candidate_score = self._compute_window_score(candidate)
            if candidate_score > best_score:
                best_score = candidate_score
                best_timing = candidate

        if best_timing is None:
            return

        iso_date = best_timing.recommended_date.isoformat()
        equipment_available = self._resolve_equipment(request.equipment_availability, iso_date)
        labor_capacity = self._resolve_labor(request.labor_availability, iso_date)

        soil_restriction = None
        if report is not None:
            soil_restriction = self._lookup_soil_restriction(report.application_windows, iso_date)

        equipment_missing = True
        if equipment_available is not None:
            if len(equipment_available) > 0:
                equipment_missing = False

        if equipment_missing:
            title = f"Equipment readiness gap on {iso_date}"
            if title not in existing_titles:
                alert = self._build_operational_alert(
                    result.request_id,
                    title,
                    "warning",
                    "No equipment scheduled for the priority window. Assign applicators and confirm readiness.",
                    "Assign equipment with proper capacity and verify maintenance status.",
                    equipment_available,
                    labor_capacity,
                    soil_restriction,
                )
                alerts.append(alert)
                existing_titles[title] = True

        labor_insufficient = True
        if labor_capacity is not None:
            if labor_capacity > 1:
                labor_insufficient = False

        if labor_insufficient:
            title = f"Labor constraint on {iso_date}"
            if title not in existing_titles:
                alert = self._build_operational_alert(
                    result.request_id,
                    title,
                    "warning",
                    "Insufficient labor scheduled to execute the fertilizer application window.",
                    "Reassign crew members or arrange contract labor support.",
                    equipment_available,
                    labor_capacity,
                    soil_restriction,
                )
                alerts.append(alert)
                existing_titles[title] = True

        if best_timing.weather_risk > 0.55:
            title = f"Weather risk for {best_timing.fertilizer_type}"
            if title not in existing_titles:
                message = (
                    f"Weather risk score of {best_timing.weather_risk:.2f} threatens the recommended window on {iso_date}."
                )
                action = "Monitor hourly forecasts, consider split application, and prepare for rapid deployment."
                alert = self._build_operational_alert(
                    result.request_id,
                    title,
                    "warning",
                    message,
                    action,
                    equipment_available,
                    labor_capacity,
                    soil_restriction,
                )
                alerts.append(alert)
                existing_titles[title] = True

    def _append_weather_gap_alert(
        self,
        request_id: str,
        alerts: List[TimingAlert],
        existing_titles: Dict[str, bool],
        windows: Iterable[WeatherWindow],
        report: Optional[WeatherSoilIntegrationReport],
    ) -> None:
        optimal_count = 0
        marginal_streak = 0
        longest_marginal_streak = 0

        for window in windows:
            if window.condition == WeatherCondition.OPTIMAL:
                optimal_count += 1
                if marginal_streak > longest_marginal_streak:
                    longest_marginal_streak = marginal_streak
                marginal_streak = 0
            else:
                marginal_streak += 1

        if marginal_streak > longest_marginal_streak:
            longest_marginal_streak = marginal_streak

        if optimal_count > 0 and longest_marginal_streak < 5:
            return

        title = "Limited optimal weather windows detected"
        if title in existing_titles:
            return

        severity = "warning"
        message_parts: List[str] = []
        message_parts.append("Only marginal or poor weather windows available in the current horizon.")
        message_parts.append("Prepare contingency plans such as split applications or stabilizers.")
        if report is not None:
            summary_text = self._summarize_weather_conditions(report)
            if summary_text is not None:
                message_parts.append(summary_text)

        message = " ".join(message_parts)
        action = "Coordinate agronomist review and monitor micro-forecasts twice daily."
        factors = self._determine_channels(severity)
        alert = TimingAlert(
            request_id=request_id,
            severity=severity,
            title=title,
            message=message,
            action=action,
            factors=self._uppercase_channels(factors),
        )
        alerts.append(alert)
        existing_titles[title] = True

    def _build_window_summary(self, window: WeatherWindow) -> str:
        text_parts: List[str] = []
        text_parts.append(f"Conditions: {window.condition.value}.")
        text_parts.append(f"Temperature near {window.temperature_f:.0f}°F.")
        text_parts.append(f"Precipitation probability {window.precipitation_probability:.0%}.")
        text_parts.append(f"Wind speeds around {window.wind_speed_mph:.0f} mph.")
        return " ".join(text_parts)

    def _build_soil_summary(self, report: WeatherSoilIntegrationReport) -> Optional[str]:
        snapshot = report.soil_summary
        if snapshot.trafficability is None:
            return None
        return (
            f"Soil trafficability rated {snapshot.trafficability} with moisture {snapshot.soil_moisture:.2f}."
        )

    def _build_operational_alert(
        self,
        request_id: str,
        title: str,
        severity: str,
        message: str,
        action: str,
        equipment_available: Optional[List[str]],
        labor_capacity: Optional[int],
        soil_restriction: Optional[str],
    ) -> TimingAlert:
        factors: List[str] = []
        channels = self._determine_channels(severity)
        for channel in channels:
            factors.append(f"Preferred channel: {channel.upper()}")

        if equipment_available is None or len(equipment_available) == 0:
            factors.append("Equipment readiness: unavailable")
        else:
            equipment_text = self._join_equipment(equipment_available)
            factors.append(f"Equipment readiness: {equipment_text}")

        if labor_capacity is None:
            factors.append("Labor readiness: unknown")
        else:
            factors.append(f"Labor readiness: {labor_capacity} workers")

        if soil_restriction is not None:
            factors.append(f"Soil constraint: {soil_restriction}")

        alert = TimingAlert(
            request_id=request_id,
            severity=severity,
            title=title,
            message=message,
            action=action,
            factors=factors,
        )
        return alert

    def _join_equipment(self, equipment_list: List[str]) -> str:
        if not equipment_list:
            return "none"
        joined = ""
        index = 0
        while index < len(equipment_list):
            item = equipment_list[index]
            if joined:
                joined = f"{joined}, {item}"
            else:
                joined = item
            index += 1
        return joined

    def _resolve_equipment(
        self,
        availability: Dict[str, List[str]],
        iso_date: str,
    ) -> Optional[List[str]]:
        if availability is None:
            return None
        if iso_date not in availability:
            return []
        equipment = availability[iso_date]
        return equipment

    def _resolve_labor(
        self,
        availability: Dict[str, int],
        iso_date: str,
    ) -> Optional[int]:
        if availability is None:
            return None
        if iso_date not in availability:
            return 0
        return availability[iso_date]

    def _lookup_soil_restriction(
        self,
        windows: Iterable[WeatherSoilWindow],
        iso_date: str,
    ) -> Optional[str]:
        for window in windows:
            if window.window.start_date.isoformat() == iso_date:
                return window.limiting_factor
        return None

    def _select_best_window(
        self,
        windows: Iterable[WeatherWindow],
    ) -> Optional[WeatherSoilWindow]:
        best_window: Optional[WeatherWindow] = None
        for window in windows:
            if best_window is None:
                best_window = window
            else:
                if window.suitability_score > best_window.suitability_score:
                    best_window = window
        if best_window is None:
            return None
        combined = WeatherSoilWindow(
            window=best_window,
            soil_snapshot=self._fallback_soil_snapshot(),
            combined_score=best_window.suitability_score,
            limiting_factor="weather",
            recommended_action="Monitor updated forecast to confirm suitability.",
            confidence=0.6,
        )
        return combined

    def _fallback_soil_snapshot(self) -> SoilConditionSnapshot:
        limiting: List[str] = []
        actions: List[str] = []
        snapshot = SoilConditionSnapshot(
            soil_texture=None,
            drainage_class=None,
            soil_moisture=0.5,
            trafficability="moderate",
            compaction_risk="medium",
            limiting_factors=limiting,
            recommended_actions=actions,
        )
        return snapshot

    def _determine_channels(self, severity: str) -> List[str]:
        channels: List[str] = []
        if severity == "critical":
            channels.append("sms")
            channels.append("phone")
            channels.append("dashboard")
        elif severity == "warning":
            channels.append("sms")
            channels.append("email")
            channels.append("dashboard")
        else:
            channels.append("email")
            channels.append("dashboard")
        return channels

    def _uppercase_channels(self, channels: List[str]) -> List[str]:
        uppercased: List[str] = []
        index = 0
        while index < len(channels):
            uppercased.append(channels[index].upper())
            index += 1
        return uppercased

    def _compute_window_score(self, timing: ApplicationTiming) -> float:
        score = 0.0
        score = score + timing.timing_score * 0.4
        score = score + timing.weather_score * 0.3
        score = score + timing.crop_score * 0.2
        score = score + timing.soil_score * 0.1

        risk_total = timing.weather_risk + timing.timing_risk + timing.equipment_risk
        risk_average = risk_total / 3.0
        score = score - risk_average * 0.3

        if score < 0.0:
            score = 0.0
        if score > 1.0:
            score = 1.0
        return score

    def _summarize_weather_conditions(
        self,
        report: WeatherSoilIntegrationReport,
    ) -> Optional[str]:
        summary = report.weather_summary
        advisory = None
        if summary.advisory_notes:
            advisory = summary.advisory_notes[0]
        text_parts: List[str] = []
        text_parts.append(f"Precipitation outlook: {summary.precipitation_outlook}.")
        text_parts.append(f"Wind risk: {summary.wind_risk}.")
        if advisory is not None:
            text_parts.append(f"Advisory: {advisory}")
        return " ".join(text_parts)

    def _load_weather_service(self):
        try:
            from services.weather_integration_service import WeatherSoilIntegrationService as _WeatherService  # type: ignore

            return _WeatherService()
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("Weather integration service unavailable, using fallback: %s", exc)
            return _WeatherServiceFallback()


class _WeatherServiceFallback:
    """
    Minimal fallback that returns empty weather integration data.
    """

    async def generate_integration_report(
        self,
        request: TimingOptimizationRequest,
        forecast_days: int = 10,
    ) -> WeatherSoilIntegrationReport:
        windows: List[WeatherSoilWindow] = []
        return WeatherSoilIntegrationReport(
            request_id=request.request_id,
            soil_summary=SoilConditionSnapshot(
                soil_texture=None,
                drainage_class=None,
                soil_moisture=0.5,
                soil_temperature_f=None,
                trafficability="unknown",
                compaction_risk="unknown",
                limiting_factors=[],
                recommended_actions=[],
            ),
            weather_summary=WeatherConditionSummary(
                forecast_days=forecast_days,
                precipitation_outlook="insufficient data",
                temperature_trend="unknown",
                wind_risk="unknown",
                humidity_trend="unknown",
                advisory_notes=[],
            ),
            application_windows=windows,
        )


__all__ = ["ApplicationWindowAlertService"]
