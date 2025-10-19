"""
API routes for fertilizer timing alert generation.
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from ..models import TimingAlertResponse, TimingOptimizationRequest
from ..services import TimingAlertService, TimingResultRepository
from .timing_routes import get_adapter, get_repository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/fertilizer-alerts", tags=["fertilizer-alerts"])


def get_alert_service() -> TimingAlertService:
    return TimingAlertService()


@router.post(
    "/generate",
    response_model=TimingAlertResponse,
    status_code=status.HTTP_200_OK,
)
async def generate_alerts(
    request: TimingOptimizationRequest,
    alert_service: TimingAlertService = Depends(get_alert_service),
    adapter=Depends(get_adapter),
    repository: TimingResultRepository = Depends(get_repository),
) -> TimingAlertResponse:
    """Generate alerts from a fresh optimization run."""
    try:
        result = await adapter.optimize(request)
        await repository.save_result(request, result)
        alert_response = alert_service.generate_alerts(result)
        records = alert_service.to_records(alert_response)
        await repository.save_alerts(result.request_id, records)
        return alert_response
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Alert generation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Alert generation failed: {exc}",
        ) from exc
