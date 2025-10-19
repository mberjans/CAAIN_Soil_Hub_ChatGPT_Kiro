"""API routes for seasonal calendar generation."""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from models import SeasonalCalendarResponse, TimingOptimizationRequest
from services.calendar_service import SeasonalCalendarService
from timing_services import TimingResultRepository
from .timing_routes import get_adapter, get_repository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/fertilizer-calendar", tags=["fertilizer-calendar"])


def get_calendar_service() -> SeasonalCalendarService:
    return SeasonalCalendarService()


@router.post(
    "/generate",
    response_model=SeasonalCalendarResponse,
    status_code=status.HTTP_200_OK,
)
async def generate_calendar(
    request: TimingOptimizationRequest,
    calendar_service: SeasonalCalendarService = Depends(get_calendar_service),
    adapter=Depends(get_adapter),
    repository: TimingResultRepository = Depends(get_repository),
) -> SeasonalCalendarResponse:
    """Generate a seasonal calendar and persist the underlying optimization."""
    try:
        result = await adapter.optimize(request)
        await repository.save_result(request, result)
        calendar = calendar_service.assemble_calendar(request, result)
        return calendar
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Calendar generation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Calendar generation failed: {exc}",
        ) from exc


@router.get(
    "/recent",
    response_model=List[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
)
async def list_recent_results(
    limit: int = Query(default=5, ge=1, le=25),
    repository: TimingResultRepository = Depends(get_repository),
) -> List[Dict[str, Any]]:
    """Return a summary of recently persisted optimization results."""
    records = await repository.list_results(limit)
    summaries: List[Dict[str, Any]] = []
    for record in records:
        summary: Dict[str, Any] = {}
        summary["record_id"] = record.id
        summary["request_id"] = record.request_id
        summary["created_at"] = record.created_at.isoformat() if record.created_at else None
        summary["has_result"] = record.result_payload is not None
        summaries.append(summary)
    return summaries
