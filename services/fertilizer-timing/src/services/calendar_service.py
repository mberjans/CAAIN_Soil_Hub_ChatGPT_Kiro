"""
Seasonal calendar service for the fertilizer timing microservice.
"""

from datetime import datetime
from typing import List

from ..models import (
    ApplicationTiming,
    SeasonalCalendarEntry,
    SeasonalCalendarResponse,
    TimingOptimizationResult,
    WeatherWindow,
)


class SeasonalCalendarService:
    """Builds human-friendly seasonal calendars from optimization results."""

    def build_calendar(self, result: TimingOptimizationResult) -> SeasonalCalendarResponse:
        entries: List[SeasonalCalendarEntry] = []

        for timing in result.optimal_timings:
            entries.append(self._build_application_entry(result.request_id, timing))

        for window in result.weather_windows:
            entries.append(self._build_weather_entry(result.request_id, window))

        entries.sort(key=lambda entry: entry.start_date)

        response = SeasonalCalendarResponse(
            request_id=result.request_id,
            generated_at=datetime.utcnow(),
            entries=entries,
        )
        return response

    def _build_application_entry(
        self,
        request_id: str,
        timing: ApplicationTiming,
    ) -> SeasonalCalendarEntry:
        description_parts: List[str] = []
        description_parts.append(f"Apply {timing.amount_lbs_per_acre:.1f} lbs/acre.")

        if timing.crop_stage:
            description_parts.append(f"Target stage: {timing.crop_stage.value.upper()}.")

        description_parts.append(
            f"Weather suitability score {timing.weather_score:.2f}, "
            f"risk {timing.weather_risk:.2f}."
        )

        description = " ".join(description_parts)

        entry = SeasonalCalendarEntry(
            request_id=request_id,
            event_type="fertilizer_application",
            name=f"{timing.fertilizer_type.title()} application",
            description=description,
            start_date=timing.recommended_date,
            end_date=timing.recommended_date,
            fertilizer_type=timing.fertilizer_type,
            application_method=timing.application_method.value,
            crop_stage=timing.crop_stage.value,
            weather_condition=timing.application_window.condition.value,
            priority=self._determine_priority(timing),
        )
        return entry

    def _build_weather_entry(
        self,
        request_id: str,
        window: WeatherWindow,
    ) -> SeasonalCalendarEntry:
        description = (
            f"Weather window rated {window.condition.value.upper()} "
            f"with suitability {window.suitability_score:.2f}. "
            f"Rain probability {window.precipitation_probability:.0%} "
            f"and wind {window.wind_speed_mph:.1f} mph."
        )

        entry = SeasonalCalendarEntry(
            request_id=request_id,
            event_type="weather_window",
            name=f"Weather window {window.condition.value}",
            description=description,
            start_date=window.start_date,
            end_date=window.end_date,
            weather_condition=window.condition.value,
            priority=self._priority_from_condition(window),
        )
        return entry

    def _determine_priority(self, timing: ApplicationTiming) -> str:
        if timing.timing_score >= 0.85:
            return "high"
        if timing.timing_score >= 0.6:
            return "normal"
        return "low"

    def _priority_from_condition(self, window: WeatherWindow) -> str:
        if window.condition.value == "optimal":
            return "high"
        if window.condition.value == "acceptable":
            return "normal"
        return "low"


__all__ = ["SeasonalCalendarService"]
