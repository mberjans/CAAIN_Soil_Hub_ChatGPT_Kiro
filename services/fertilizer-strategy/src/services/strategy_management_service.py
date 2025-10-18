"""
Service layer for fertilizer strategy management operations.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from ..database.strategy_management_db import (
    StrategyPerformanceRecord,
    StrategyRecord,
    StrategyRepository,
    StrategyVersionRecord,
)
from ..models.strategy_management_models import (
    PerformanceMetric,
    SaveStrategyRequest,
    StrategyComparisonMetric,
    StrategyComparisonRequest,
    StrategyComparisonResponse,
    StrategyPerformanceRequest,
    StrategyPerformanceResponse,
    StrategySaveResponse,
    StrategySummary,
    StrategyUpdateRequest,
    StrategyUpdateResponse,
    StrategyVersionInfo,
)

logger = logging.getLogger(__name__)


class StrategyManagementService:
    """High-level operations for fertilizer strategy management."""

    def __init__(self, repository: Optional[StrategyRepository] = None):
        if repository is None:
            repository = StrategyRepository()
        self.repository = repository

    async def save_strategy(self, request: SaveStrategyRequest) -> StrategySaveResponse:
        """Persist fertilizer strategy with versioning support."""
        strategy_id = request.strategy_id

        if strategy_id is None:
            strategy_id = str(uuid4())
        else:
            strategy_id = strategy_id.strip()
            if not strategy_id:
                raise ValueError("Strategy identifier cannot be blank")

        created, strategy_record, version_record = await asyncio.to_thread(
            self.repository.save_strategy,
            request,
            strategy_id,
        )

        version_info = self._map_version(version_record)

        message = "Strategy created successfully" if created else "Strategy updated with new version"

        return StrategySaveResponse(
            strategy_id=strategy_record.strategy_id,
            created=created,
            latest_version=version_info,
            message=message,
        )

    async def compare_strategies(
        self,
        request: StrategyComparisonRequest,
    ) -> StrategyComparisonResponse:
        """Compare stored strategies across configured metrics."""
        entries: List[Dict[str, Any]] = []
        missing: List[str] = []

        for strategy_id in request.strategy_ids:
            record = await asyncio.to_thread(self.repository.fetch_strategy, strategy_id)
            if record is None:
                missing.append(strategy_id)
                continue

            version_record = await asyncio.to_thread(self.repository.fetch_latest_version, strategy_id)
            if version_record is None:
                missing.append(strategy_id)
                continue

            summary = self._build_summary(record, version_record)
            entry: Dict[str, Any] = {}
            entry["summary"] = summary
            entry["version"] = version_record
            entries.append(entry)

        if missing:
            message = self._format_missing_strategies(missing)
            raise LookupError(message)

        metrics_map = self._build_comparison_metrics(entries, request.include_metrics)

        summaries: List[StrategySummary] = []
        for entry in entries:
            summaries.append(entry["summary"])

        metric_models: List[StrategyComparisonMetric] = []
        for metric_name in metrics_map:
            metric_detail = metrics_map[metric_name]
            metric_models.append(
                StrategyComparisonMetric(
                    metric_name=metric_name,
                    values=metric_detail["values"],
                    interpretation=metric_detail["interpretation"],
                )
            )

        response = StrategyComparisonResponse(
            strategies=summaries,
            metrics=metric_models,
        )
        return response

    async def update_strategy(
        self,
        strategy_id: str,
        request: StrategyUpdateRequest,
        user_id: str,
    ) -> StrategyUpdateResponse:
        """Update an existing strategy with a new version."""
        # Placeholder for upcoming implementation
        raise NotImplementedError("Strategy update is not implemented yet")

    async def track_performance(
        self,
        request: StrategyPerformanceRequest,
    ) -> StrategyPerformanceResponse:
        """Persist performance tracking data for a strategy."""
        # Placeholder for upcoming implementation
        raise NotImplementedError("Strategy performance tracking is not implemented yet")

    def _map_version(self, version_record: StrategyVersionRecord) -> StrategyVersionInfo:
        """Convert database version record to response model."""
        return StrategyVersionInfo(
            version_id=version_record.version_id,
            version_number=version_record.version_number,
            created_at=version_record.created_at,
            created_by=version_record.created_by,
            version_notes=version_record.version_notes,
        )

    def _build_summary(self, record: StrategyRecord, version_record: StrategyVersionRecord) -> StrategySummary:
        """Create strategy summary from metadata and version record."""
        roi_estimate = version_record.roi_estimate
        total_cost = None
        if isinstance(version_record.economic_summary, dict):
            if "total_cost" in version_record.economic_summary:
                total_cost = version_record.economic_summary.get("total_cost")

        return StrategySummary(
            strategy_id=record.strategy_id,
            strategy_name=record.strategy_name,
            latest_version=record.latest_version,
            roi_estimate=roi_estimate,
            total_cost=total_cost,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

    def _summarize_performance_metrics(
        self,
        records: List[StrategyPerformanceRecord],
    ) -> Dict[str, float]:
        """Aggregate performance metrics."""
        aggregated: Dict[str, float] = {}
        for record in records:
            for metric_entry in record.performance_metrics:
                metric_name = metric_entry.get("metric_name")
                metric_value = metric_entry.get("metric_value")
                if metric_name and metric_value is not None:
                    if metric_name in aggregated:
                        aggregated[metric_name] += metric_value
                    else:
                        aggregated[metric_name] = metric_value
        return aggregated

    def _build_comparison_metrics(
        self,
        entries: List[Dict[str, Any]],
        requested_metrics: List[str],
    ) -> Dict[str, Dict[str, Any]]:
        """Assemble comparison metrics across strategies."""
        metrics_to_use: List[str] = []
        if requested_metrics:
            for metric_name in requested_metrics:
                if metric_name and metric_name not in metrics_to_use:
                    metrics_to_use.append(metric_name)
        else:
            metrics_to_use.append("total_cost")
            metrics_to_use.append("roi_estimate")
            metrics_to_use.append("expected_yield")
            metrics_to_use.append("runoff_risk")

        metrics_map: Dict[str, Dict[str, Any]] = {}
        for metric_name in metrics_to_use:
            metric_values: Dict[str, float] = {}
            for entry in entries:
                summary = entry["summary"]
                version_record = entry["version"]
                value = self._extract_metric_value(metric_name, summary, version_record)
                if value is not None:
                    metric_values[summary.strategy_id] = value
            if metric_values:
                detail: Dict[str, Any] = {}
                detail["values"] = metric_values
                detail["interpretation"] = self._metric_interpretation(metric_name)
                metrics_map[metric_name] = detail
        return metrics_map

    def _extract_metric_value(
        self,
        metric_name: str,
        summary: StrategySummary,
        version_record: StrategyVersionRecord,
    ) -> Optional[float]:
        """Extract a metric value for comparison."""
        if metric_name == "total_cost":
            if isinstance(version_record.economic_summary, dict):
                value = version_record.economic_summary.get("total_cost")
                if value is not None:
                    try:
                        return float(value)
                    except (TypeError, ValueError):
                        return None
        elif metric_name == "roi_estimate":
            if version_record.roi_estimate is not None:
                try:
                    return float(version_record.roi_estimate)
                except (TypeError, ValueError):
                    return None
        elif metric_name == "expected_yield":
            yield_value = self._calculate_expected_yield(version_record)
            if yield_value is not None:
                return yield_value
        elif metric_name == "runoff_risk":
            metrics = version_record.environmental_metrics
            if isinstance(metrics, dict):
                risk_value = metrics.get("runoff_risk")
                if risk_value is not None:
                    try:
                        return float(risk_value)
                    except (TypeError, ValueError):
                        return None
        return None

    def _metric_interpretation(self, metric_name: str) -> str:
        """Provide interpretation guidance for metrics."""
        if metric_name == "total_cost":
            return "Lower total cost per strategy indicates reduced investment requirements."
        if metric_name == "roi_estimate":
            return "Higher ROI estimates indicate more profitable strategies."
        if metric_name == "expected_yield":
            return "Higher expected yields indicate better production outcomes."
        if metric_name == "runoff_risk":
            return "Lower runoff risk values indicate improved environmental stewardship."
        return "Metric interpretation unavailable."

    def _calculate_expected_yield(self, version_record: StrategyVersionRecord) -> Optional[float]:
        """Calculate weighted expected yield from field strategies."""
        field_data = version_record.field_strategies
        if not isinstance(field_data, list):
            return None

        total_acres = 0.0
        weighted_yield = 0.0
        for entry in field_data:
            if not isinstance(entry, dict):
                continue
            acres = entry.get("acres")
            expected_yield = entry.get("expected_yield")
            if acres is None or expected_yield is None:
                continue
            try:
                acres_value = float(acres)
                yield_value = float(expected_yield)
            except (TypeError, ValueError):
                continue
            if acres_value <= 0:
                continue
            total_acres += acres_value
            weighted_yield += acres_value * yield_value

        if total_acres <= 0:
            return None
        return weighted_yield / total_acres

    def _format_missing_strategies(self, missing: List[str]) -> str:
        """Format error message for missing strategies."""
        if not missing:
            return "Strategy not found"
        if len(missing) == 1:
            return f"Strategy not found: {missing[0]}"
        message = "Strategies not found: "
        index = 0
        while index < len(missing):
            strategy_id = missing[index]
            if index > 0:
                message = f"{message}, {strategy_id}"
            else:
                message = f"{message}{strategy_id}"
            index += 1
        return message
