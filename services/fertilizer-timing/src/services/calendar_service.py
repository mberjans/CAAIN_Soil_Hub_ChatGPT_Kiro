"""
Comprehensive seasonal fertilizer calendar orchestration service.

This module builds on the core calendar builder within ``timing_services`` to
provide richer scheduling intelligence that accounts for equipment planning,
labor coordination, split applications, and multi-crop management.
"""

import logging
from datetime import date, datetime
from typing import Dict, Iterable, List, Optional, Sequence

from models import (
    ApplicationTiming,
    SeasonalCalendarEntry,
    SeasonalCalendarResponse,
    SplitApplicationPlan,
    TimingOptimizationRequest,
    TimingOptimizationResult,
)
from timing_services import SeasonalCalendarService as _CoreCalendarBuilder
from timing_services import TimingOptimizationAdapter

logger = logging.getLogger(__name__)


class SeasonalCalendarService:
    """
    High-level seasonal calendar coordinator.

    Responsibilities:
    - Execute timing optimization for fertilizer programs
    - Generate calendar entries using the established core builder
    - Enhance entries with farm-specific operational context
    - Expand schedules with split application planning support
    - Aggregate multiple crop calendars for whole-farm management
    """

    def __init__(
        self,
        adapter: Optional[TimingOptimizationAdapter] = None,
        calendar_builder: Optional[_CoreCalendarBuilder] = None,
    ) -> None:
        self._adapter = adapter or TimingOptimizationAdapter()
        self._calendar_builder = calendar_builder or _CoreCalendarBuilder()
        logger.info("SeasonalCalendarService initialized with comprehensive scheduler")

    async def generate_calendar(
        self,
        request: TimingOptimizationRequest,
    ) -> SeasonalCalendarResponse:
        """
        Run optimization and generate an enhanced seasonal calendar.
        """
        logger.info("Generating seasonal fertilizer calendar for request %s", request.request_id)
        result = await self._adapter.optimize(request)
        return self.assemble_calendar(request, result)

    def assemble_calendar(
        self,
        request: TimingOptimizationRequest,
        result: TimingOptimizationResult,
    ) -> SeasonalCalendarResponse:
        """
        Assemble an enhanced calendar from a precomputed optimization result.
        """
        base_response = self._calendar_builder.build_calendar(result)
        enhanced_entries = self._build_enhanced_entries(base_response.entries, request, result)

        response = SeasonalCalendarResponse(
            request_id=base_response.request_id,
            generated_at=datetime.utcnow(),
            entries=enhanced_entries,
        )
        return response

    async def generate_multi_crop_calendar(
        self,
        requests: Sequence[TimingOptimizationRequest],
    ) -> Dict[str, SeasonalCalendarResponse]:
        """
        Generate calendars for multiple crops or fields in sequence.
        """
        aggregated: Dict[str, SeasonalCalendarResponse] = {}

        for request in requests:
            calendar = await self.generate_calendar(request)
            aggregated[request.request_id] = calendar

        return aggregated

    def _build_enhanced_entries(
        self,
        base_entries: Iterable[SeasonalCalendarEntry],
        request: TimingOptimizationRequest,
        result: TimingOptimizationResult,
    ) -> List[SeasonalCalendarEntry]:
        entries: List[SeasonalCalendarEntry] = []

        equipment_index = self._build_equipment_index(request.equipment_availability)
        labor_index = self._build_labor_index(request.labor_availability)

        for entry in base_entries:
            enhanced_entry = self._apply_operational_context(entry, request, equipment_index, labor_index)
            entries.append(enhanced_entry)

        self._add_split_plan_entries(entries, result, request, equipment_index, labor_index)
        self._sort_entries(entries)
        return entries

    def _apply_operational_context(
        self,
        entry: SeasonalCalendarEntry,
        request: TimingOptimizationRequest,
        equipment_index: Dict[date, List[str]],
        labor_index: Dict[date, int],
    ) -> SeasonalCalendarEntry:
        entry_payload = entry.model_dump()
        description = entry_payload.get("description", "")
        priority = entry_payload.get("priority", "normal")
        notes: List[str] = []

        field_note = f"Field focus: {request.field_id}."
        notes.append(field_note)

        event_date: Optional[date] = entry_payload.get("start_date")
        if event_date is None and hasattr(entry, "start_date"):
            event_date = entry.start_date

        equipment_available = self._resolve_equipment_for_date(event_date, equipment_index)
        if equipment_available:
            equipment_list = self._join_values(equipment_available)
            notes.append(f"Equipment ready: {equipment_list}.")
        else:
            notes.append("Coordinate equipment scheduling.")
            if priority == "high":
                priority = "normal"

        workers_available = self._resolve_labor_for_date(event_date, labor_index)
        if workers_available is None:
            notes.append("Schedule labor support.")
            priority = "low"
        else:
            notes.append(f"Labor capacity: {workers_available} workers.")

        description = self._augment_description(description, notes)

        if event_date is not None and entry_payload.get("event_type") == "weather_window":
            description = self._augment_weather_guidance(description, request.crop_type)

        entry_payload["description"] = description
        entry_payload["priority"] = priority
        enhanced_entry = SeasonalCalendarEntry(**entry_payload)
        return enhanced_entry

    def _augment_description(self, original: str, notes: Sequence[str]) -> str:
        parts: List[str] = []
        if original:
            parts.append(original)

        for note in notes:
            parts.append(note)

        joined_notes = " ".join(parts)
        return joined_notes.strip()

    def _augment_weather_guidance(self, description: str, crop_type: str) -> str:
        guidance = f" Monitor microclimate for {crop_type} response."
        if guidance not in description:
            description = f"{description}{guidance}"
        return description

    def _add_split_plan_entries(
        self,
        entries: List[SeasonalCalendarEntry],
        result: TimingOptimizationResult,
        request: TimingOptimizationRequest,
        equipment_index: Dict[date, List[str]],
        labor_index: Dict[date, int],
    ) -> None:
        if not result.split_plans:
            return

        for plan in result.split_plans:
            application_count = len(plan.applications)
            index = 0
            while index < application_count:
                application = plan.applications[index]
                ratio_text = self._build_ratio_text(plan.split_ratio, index)
                description = (
                    f"Split application {index + 1} of {application_count} "
                    f"for {plan.fertilizer_type}. Apply {application.amount_lbs_per_acre:.1f} lbs/acre. "
                    f"Target stage {application.crop_stage.value.upper()}. {ratio_text}"
                )
                split_entry = SeasonalCalendarEntry(
                    request_id=result.request_id,
                    event_type="split_application",
                    name=f"{plan.fertilizer_type.title()} split #{index + 1}",
                    description=description,
                    start_date=application.recommended_date,
                    end_date=application.recommended_date,
                    fertilizer_type=plan.fertilizer_type,
                    application_method=application.application_method.value,
                    crop_stage=application.crop_stage.value,
                    weather_condition=application.application_window.condition.value,
                    priority=self._determine_priority(application),
                )
                split_entry = self._apply_operational_context(split_entry, request, equipment_index, labor_index)
                entries.append(split_entry)
                index += 1

    def _build_ratio_text(self, ratios: Sequence[float], position: int) -> str:
        if not ratios:
            return "Balanced split ratio."

        segments: List[str] = []
        index = 0
        while index < len(ratios):
            part = ratios[index] * 100.0
            formatted = f"{part:.0f}%"
            segments.append(formatted)
            index += 1

        ratio_summary = "/".join(segments)
        if position < len(ratios):
            focus = f"Focus portion: {segments[position]}."
        else:
            focus = "Balanced split execution."
        return f"Ratios {ratio_summary}. {focus}"

    def _build_equipment_index(self, availability: Dict[str, Sequence[str]]) -> Dict[date, List[str]]:
        index: Dict[date, List[str]] = {}
        for equipment, raw_dates in availability.items():
            for raw in raw_dates:
                parsed = self._parse_date(raw)
                if parsed is None:
                    continue

                if parsed not in index:
                    index[parsed] = []
                index[parsed].append(equipment)
        return index

    def _build_labor_index(self, availability: Dict[str, int]) -> Dict[date, int]:
        index: Dict[date, int] = {}
        for raw_date, workers in availability.items():
            parsed = self._parse_date(raw_date)
            if parsed is None:
                continue
            index[parsed] = workers
        return index

    def _resolve_equipment_for_date(self, event_date: Optional[date], index: Dict[date, List[str]]) -> List[str]:
        if event_date is None:
            return []
        if event_date not in index:
            return []
        return index[event_date]

    def _resolve_labor_for_date(self, event_date: Optional[date], index: Dict[date, int]) -> Optional[int]:
        if event_date is None:
            return None
        if event_date not in index:
            return None
        return index[event_date]

    def _join_values(self, values: Sequence[str]) -> str:
        parts: List[str] = []
        for value in values:
            parts.append(value)
        return ", ".join(parts)

    def _determine_priority(self, timing: ApplicationTiming) -> str:
        if timing.timing_score >= 0.85:
            return "high"
        if timing.timing_score >= 0.6:
            return "normal"
        return "low"

    def _parse_date(self, raw: object) -> Optional[date]:
        if isinstance(raw, date):
            return raw

        if isinstance(raw, datetime):
            return raw.date()

        if not isinstance(raw, str):
            return None

        try:
            parsed_datetime = datetime.fromisoformat(raw)
            return parsed_datetime.date()
        except ValueError:
            pass

        try:
            parsed_datetime = datetime.strptime(raw, "%Y-%m-%d")
            return parsed_datetime.date()
        except ValueError:
            logger.debug("Unable to parse date string '%s'", raw)
            return None

    def _sort_entries(self, entries: List[SeasonalCalendarEntry]) -> None:
        entries.sort(key=lambda entry: entry.start_date)


__all__ = ["SeasonalCalendarService"]
