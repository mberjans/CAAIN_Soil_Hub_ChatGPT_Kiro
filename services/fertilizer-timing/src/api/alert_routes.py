"""
API routes for fertilizer timing alert generation.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from models import TimingAlertResponse, TimingOptimizationRequest
from timing_services import TimingResultRepository
from .timing_routes import get_adapter, get_repository
from services import ApplicationWindowAlertService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/fertilizer-alerts", tags=["fertilizer-alerts"])


def get_alert_service(adapter=Depends(get_adapter)) -> ApplicationWindowAlertService:
    return ApplicationWindowAlertService(timing_adapter=adapter)


@router.post(
    "/generate",
    response_model=TimingAlertResponse,
    status_code=status.HTTP_200_OK,
)
async def generate_alerts(
    request: TimingOptimizationRequest,
    alert_service: ApplicationWindowAlertService = Depends(get_alert_service),
    repository: TimingResultRepository = Depends(get_repository),
) -> TimingAlertResponse:
    """Generate alerts from a fresh optimization run."""
    try:
        alert_response, result = await alert_service.generate_alerts(request)
        await repository.save_result(request, result)
        records = alert_service.to_records(alert_response)
        await repository.save_alerts(result.request_id, records)
        return alert_response
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Alert generation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Alert generation failed: {exc}",
        ) from exc
