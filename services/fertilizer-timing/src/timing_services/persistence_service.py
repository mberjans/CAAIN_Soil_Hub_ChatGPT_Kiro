"""
Persistence helpers for fertilizer timing optimization microservice.

Provides repository-style helpers for storing optimization runs and alerts.
"""

import logging
from typing import Dict, List, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from database import (
    TimingAlertRecord,
    TimingOptimizationRecord,
    get_session_factory,
)
from models import TimingOptimizationRequest, TimingOptimizationResult

logger = logging.getLogger(__name__)


class TimingResultRepository:
    """Repository encapsulating persistence operations."""

    def __init__(self) -> None:
        self._session_factory = get_session_factory()

    async def save_result(
        self,
        request: TimingOptimizationRequest,
        result: TimingOptimizationResult,
        session: Optional[AsyncSession] = None,
    ) -> str:
        """Persist an optimization result and return the record identifier."""
        owns_session = session is None
        active_session = session or self._session_factory()

        try:
            record = TimingOptimizationRecord(
                request_id=request.request_id,
                request_payload=jsonable_encoder(request),
                result_payload=jsonable_encoder(result),
            )
            active_session.add(record)
            await active_session.commit()

            if owns_session:
                await active_session.close()

            return record.id
        except SQLAlchemyError as exc:
            logger.error("Failed to persist optimization result: %s", exc)
            if owns_session:
                await active_session.rollback()
                await active_session.close()
            raise

    async def list_results(self, limit: int = 10) -> List[TimingOptimizationRecord]:
        """Return the most recent optimization records."""
        session = self._session_factory()
        try:
            stmt = select(TimingOptimizationRecord).order_by(
                TimingOptimizationRecord.created_at.desc()
            ).limit(limit)
            result = await session.execute(stmt)
            records: List[TimingOptimizationRecord] = []
            for row in result.scalars():
                records.append(row)
            return records
        finally:
            await session.close()

    async def load_result(
        self,
        request_id: str,
    ) -> Optional[Dict[str, object]]:
        """
        Retrieve a persisted optimization result and request by request identifier.
        """
        session = self._session_factory()
        try:
            stmt = (
                select(TimingOptimizationRecord)
                .where(TimingOptimizationRecord.request_id == request_id)
                .order_by(TimingOptimizationRecord.created_at.desc())
                .limit(1)
            )
            query_result = await session.execute(stmt)
            record = query_result.scalars().first()

            if record is None:
                return None

            payload: Dict[str, object] = {}

            if record.result_payload is not None:
                parsed_result = TimingOptimizationResult.model_validate(record.result_payload)
                payload["result"] = parsed_result

            if record.request_payload is not None:
                parsed_request = TimingOptimizationRequest.model_validate(record.request_payload)
                payload["request"] = parsed_request

            if "result" not in payload:
                return None

            return payload
        except SQLAlchemyError as exc:
            logger.error("Failed to load optimization result: %s", exc)
            raise
        finally:
            await session.close()

    async def save_alerts(
        self,
        request_id: str,
        alerts: List[TimingAlertRecord],
        session: Optional[AsyncSession] = None,
    ) -> None:
        """Persist alert records for a request."""
        owns_session = session is None
        active_session = session or self._session_factory()

        try:
            for alert in alerts:
                alert.request_id = request_id  # type: ignore[assignment]
                active_session.add(alert)
            await active_session.commit()
        except SQLAlchemyError as exc:
            logger.error("Failed to persist alerts: %s", exc)
            await active_session.rollback()
            raise
        finally:
            if owns_session:
                await active_session.close()


__all__ = ["TimingResultRepository"]
