"""
API routes for mobile fertilizer strategy tracking and monitoring.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..models.mobile_strategy_tracking_models import (
    MobileStrategyProgressEntry,
    MobileStrategyProgressResponse,
    MobileStrategySummaryResponse,
    MobileStrategySyncRequest,
    MobileStrategySyncResponse,
)
from ..services.mobile_strategy_tracking_service import MobileStrategyTrackingService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mobile-strategy", tags=["mobile-strategy-tracking"])


async def get_mobile_tracking_service() -> MobileStrategyTrackingService:
    """Dependency provider for tracking service."""
    return MobileStrategyTrackingService()


@router.post(
    "/progress",
    response_model=MobileStrategyProgressResponse,
    status_code=status.HTTP_200_OK,
)
async def record_mobile_progress(
    entry: MobileStrategyProgressEntry,
    service: MobileStrategyTrackingService = Depends(get_mobile_tracking_service),
) -> MobileStrategyProgressResponse:
    """Record a mobile strategy progress update."""
    try:
        response = await service.record_progress(entry)
        return response
    except ValueError as error:
        logger.warning("Validation error recording progress: %s", error)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    except Exception as error:
        logger.error("Failed to record mobile progress: %s", error)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to record progress") from error


@router.post(
    "/sync",
    response_model=MobileStrategySyncResponse,
    status_code=status.HTTP_200_OK,
)
async def sync_mobile_progress(
    request: MobileStrategySyncRequest,
    service: MobileStrategyTrackingService = Depends(get_mobile_tracking_service),
) -> MobileStrategySyncResponse:
    """Synchronize offline strategy progress entries."""
    try:
        response = await service.sync_progress(request)
        return response
    except ValueError as error:
        logger.warning("Validation error synchronizing progress: %s", error)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    except Exception as error:
        logger.error("Failed to synchronize mobile progress: %s", error)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to synchronize progress") from error


@router.get(
    "/summary",
    response_model=MobileStrategySummaryResponse,
    status_code=status.HTTP_200_OK,
)
async def get_mobile_tracking_summary(
    strategy_id: str = Query(..., description="Strategy identifier"),
    version_number: int = Query(..., ge=1, description="Strategy version number"),
    limit: Optional[int] = Query(10, ge=1, le=50, description="Maximum number of recent activities"),
    service: MobileStrategyTrackingService = Depends(get_mobile_tracking_service),
) -> MobileStrategySummaryResponse:
    """Retrieve mobile tracking summary for a strategy."""
    try:
        response = await service.get_tracking_summary(strategy_id, version_number, limit or 10)
        return response
    except ValueError as error:
        logger.warning("Validation error retrieving summary: %s", error)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    except Exception as error:
        logger.error("Failed to retrieve mobile tracking summary: %s", error)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch summary") from error
