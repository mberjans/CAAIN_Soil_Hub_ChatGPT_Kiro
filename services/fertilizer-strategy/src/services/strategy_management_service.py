"""
Service layer for fertilizer strategy management operations.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
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
        # Placeholder implementation until comparison logic is added in later subtasks
        raise NotImplementedError("Strategy comparison is not implemented yet")

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

    def _map_strategy_record(self, record: StrategyRecord) -> StrategySummary:
        """Convert strategy metadata record into summary."""
        roi_estimate = None
        total_cost = None

        versions = self.repository.fetch_versions(record.strategy_id)
        if versions:
            latest_version = None
            for version in versions:
                if version.version_number == record.latest_version:
                    latest_version = version
                    break
            if latest_version:
                roi_estimate = latest_version.roi_estimate
                if isinstance(latest_version.economic_summary, dict):
                    total_cost = latest_version.economic_summary.get("total_cost")

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
