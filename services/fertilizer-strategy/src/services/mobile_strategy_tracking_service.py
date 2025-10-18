"""
Mobile strategy tracking service for fertilizer strategy monitoring.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..database.strategy_management_db import (
    MobileStrategyActivityRecord,
    StrategyPerformanceRecord,
    StrategyRepository,
)
from ..models.mobile_strategy_tracking_models import (
    MobileStrategyProgressEntry,
    MobileStrategyProgressResponse,
    MobileStrategySummaryActivity,
    MobileStrategySummaryResponse,
    MobileStrategyPerformanceSnapshot,
    MobileStrategySyncRequest,
    MobileStrategySyncResponse,
    MobileStrategySyncResult,
)
from ..models.strategy_management_models import (
    PerformanceMetric,
    StrategyPerformanceRequest,
)
from .strategy_management_service import StrategyManagementService


class MobileStrategyTrackingService:
    """Coordinate mobile strategy tracking operations."""

    def __init__(
        self,
        repository: Optional[StrategyRepository] = None,
        management_service: Optional[StrategyManagementService] = None,
    ):
        if repository is None:
            repository = StrategyRepository()
        self.repository = repository

        if management_service is None:
            management_service = StrategyManagementService(repository=self.repository)
        self.management_service = management_service

        self.logger = logging.getLogger(__name__)

    async def record_progress(
        self,
        entry: MobileStrategyProgressEntry,
    ) -> MobileStrategyProgressResponse:
        """Record a mobile strategy progress entry."""
        result = await asyncio.to_thread(self.repository.log_mobile_activity, entry)
        record: MobileStrategyActivityRecord = result["record"]
        created = result["created"]
        conflict_resolved = result["conflict_resolved"]

        synced = False
        try:
            performance_request = self._build_performance_request(entry)
            if performance_request:
                await self.management_service.track_performance(performance_request)
                await asyncio.to_thread(self.repository.mark_activity_synced, record.activity_id, "synced")
                synced = True
        except Exception as error:
            self.logger.warning("Performance synchronization failed for strategy %s: %s", entry.strategy_id, error)

        response = MobileStrategyProgressResponse(
            activity_id=record.activity_id,
            status=record.status,
            conflict_resolved=conflict_resolved,
            created=created,
            synced=synced,
        )
        return response

    async def sync_progress(
        self,
        request: MobileStrategySyncRequest,
    ) -> MobileStrategySyncResponse:
        """Synchronize multiple mobile progress entries."""
        results: List[MobileStrategySyncResult] = []
        conflicts_detected = False
        processed_count = 0

        if request.entries:
            index = 0
            while index < len(request.entries):
                entry = request.entries[index]
                try:
                    progress_response = await self.record_progress(entry)
                    sync_result = MobileStrategySyncResult(
                        client_event_id=entry.client_event_id,
                        activity_id=progress_response.activity_id,
                        status=progress_response.status,
                        conflict_resolved=progress_response.conflict_resolved,
                    )
                    results.append(sync_result)
                    processed_count += 1
                    if progress_response.conflict_resolved:
                        conflicts_detected = True
                except Exception as error:
                    self.logger.error(
                        "Failed to synchronize entry %s: %s",
                        entry.client_event_id,
                        error,
                    )
                    failure_result = MobileStrategySyncResult(
                        client_event_id=entry.client_event_id,
                        activity_id=None,
                        status="failed",
                        conflict_resolved=False,
                    )
                    results.append(failure_result)
                index += 1

        response = MobileStrategySyncResponse(
            results=results,
            conflicts_detected=conflicts_detected,
            processed_count=processed_count,
        )
        return response

    async def get_tracking_summary(
        self,
        strategy_id: str,
        version_number: int,
        limit: int = 10,
    ) -> MobileStrategySummaryResponse:
        """Return aggregated tracking summary for a strategy."""
        progress_metrics = await asyncio.to_thread(
            self.repository.calculate_mobile_progress,
            strategy_id,
            version_number,
        )

        recent_records = await asyncio.to_thread(
            self.repository.fetch_recent_mobile_activities,
            strategy_id,
            limit,
        )

        activities: List[MobileStrategySummaryActivity] = []
        if recent_records:
            index = 0
            while index < len(recent_records):
                record = recent_records[index]
                summary_activity = self._map_activity_record(record)
                activities.append(summary_activity)
                index += 1

        performance_record = await asyncio.to_thread(
            self.repository.fetch_latest_performance,
            strategy_id,
        )

        performance_snapshot = self._build_performance_snapshot(
            performance_record,
            progress_metrics,
        )

        progress_percent = progress_metrics.get("progress_percent", 0.0)
        pending_actions = progress_metrics.get("pending_actions", 0)

        summary = MobileStrategySummaryResponse(
            strategy_id=strategy_id,
            version_number=version_number,
            progress_percent=progress_percent,
            pending_actions=pending_actions,
            recent_activities=activities,
            performance_snapshot=performance_snapshot,
        )
        return summary

    def _build_performance_request(
        self,
        entry: MobileStrategyProgressEntry,
    ) -> Optional[StrategyPerformanceRequest]:
        """Construct performance request from mobile entry."""
        has_cost = entry.cost_summary is not None and entry.cost_summary.total_cost is not None
        has_yield = entry.yield_summary is not None and entry.yield_summary.observed_yield is not None

        if not has_cost and not has_yield:
            return None

        metrics: List[PerformanceMetric] = []

        if entry.cost_summary:
            if entry.cost_summary.total_cost is not None:
                metrics.append(
                    PerformanceMetric(
                        metric_name="total_cost",
                        metric_value=entry.cost_summary.total_cost,
                    )
                )
            if entry.cost_summary.input_cost is not None:
                metrics.append(
                    PerformanceMetric(
                        metric_name="input_cost",
                        metric_value=entry.cost_summary.input_cost,
                    )
                )
            if entry.cost_summary.labor_cost is not None:
                metrics.append(
                    PerformanceMetric(
                        metric_name="labor_cost",
                        metric_value=entry.cost_summary.labor_cost,
                    )
                )

        if entry.yield_summary:
            if entry.yield_summary.observed_yield is not None:
                metrics.append(
                    PerformanceMetric(
                        metric_name="observed_yield",
                        metric_value=entry.yield_summary.observed_yield,
                    )
                )
            if entry.yield_summary.expected_yield is not None:
                metrics.append(
                    PerformanceMetric(
                        metric_name="expected_yield",
                        metric_value=entry.yield_summary.expected_yield,
                    )
                )

        reporting_start = entry.activity_timestamp
        reporting_end = entry.activity_timestamp

        performance_request = StrategyPerformanceRequest(
            strategy_id=entry.strategy_id,
            version_number=entry.version_number,
            reporting_period_start=reporting_start,
            reporting_period_end=reporting_end,
            realized_yield=entry.yield_summary.observed_yield if entry.yield_summary else None,
            realized_cost=entry.cost_summary.total_cost if entry.cost_summary else None,
            realized_revenue=None,
            performance_metrics=metrics,
            observations=entry.notes,
        )

        return performance_request

    def _map_activity_record(
        self,
        record: MobileStrategyActivityRecord,
    ) -> MobileStrategySummaryActivity:
        """Convert database record to summary activity."""
        cost_summary = None
        if record.cost_summary:
            cost_summary = self._convert_cost_summary(record.cost_summary)

        yield_summary = None
        if record.yield_summary:
            yield_summary = self._convert_yield_summary(record.yield_summary)

        note_value = None
        if record.attachments:
            raw_notes = record.attachments.get("notes")
            if isinstance(raw_notes, str):
                note_value = raw_notes

        activity = MobileStrategySummaryActivity(
            activity_id=record.activity_id,
            activity_type=record.activity_type,
            status=record.status,
            recorded_at=record.activity_timestamp,
            notes=note_value,
            user_id=record.user_id,
            field_id=record.field_id,
            cost_summary=cost_summary,
            yield_summary=yield_summary,
        )
        return activity

    def _convert_cost_summary(self, payload: Dict[str, Any]):
        """Convert dictionary payload to StrategyCostSummary."""
        from ..models.mobile_strategy_tracking_models import StrategyCostSummary

        summary = StrategyCostSummary()
        if payload is None:
            return summary

        if "input_cost" in payload and payload["input_cost"] is not None:
            summary.input_cost = payload["input_cost"]
        if "labor_cost" in payload and payload["labor_cost"] is not None:
            summary.labor_cost = payload["labor_cost"]
        if "equipment_cost" in payload and payload["equipment_cost"] is not None:
            summary.equipment_cost = payload["equipment_cost"]
        if "total_cost" in payload and payload["total_cost"] is not None:
            summary.total_cost = payload["total_cost"]
        if "currency" in payload and payload["currency"]:
            summary.currency = payload["currency"]
        return summary

    def _convert_yield_summary(self, payload: Dict[str, Any]):
        """Convert dictionary payload to StrategyYieldSummary."""
        from ..models.mobile_strategy_tracking_models import StrategyYieldSummary

        summary = StrategyYieldSummary()
        if payload is None:
            return summary

        if "observed_yield" in payload and payload["observed_yield"] is not None:
            summary.observed_yield = payload["observed_yield"]
        if "expected_yield" in payload and payload["expected_yield"] is not None:
            summary.expected_yield = payload["expected_yield"]
        if "yield_unit" in payload and payload["yield_unit"]:
            summary.yield_unit = payload["yield_unit"]
        if "notes" in payload and payload["notes"]:
            summary.notes = payload["notes"]
        return summary

    def _build_performance_snapshot(
        self,
        performance_record: Optional[StrategyPerformanceRecord],
        progress_metrics: Dict[str, Any],
    ) -> MobileStrategyPerformanceSnapshot:
        """Construct performance snapshot for summary response."""
        snapshot = MobileStrategyPerformanceSnapshot()

        snapshot.total_events_recorded = progress_metrics.get("total_events", 0)
        snapshot.last_synced_at = progress_metrics.get("last_synced_at")

        if performance_record:
            snapshot.realized_cost = performance_record.realized_cost
            snapshot.realized_yield = performance_record.realized_yield

            roi_candidate = None
            if performance_record.performance_metrics:
                index = 0
                while index < len(performance_record.performance_metrics):
                    metric_entry = performance_record.performance_metrics[index]
                    metric_name = metric_entry.get("metric_name")
                    metric_value = metric_entry.get("metric_value")
                    if metric_name and metric_value is not None:
                        if metric_name == "roi_projection":
                            roi_candidate = metric_value
                            break
                    index += 1
            snapshot.roi_projection = roi_candidate

        return snapshot
