"""
API routes for fertilizer timing optimization operations.
"""

import logging
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from models import (
    SplitApplicationPlan,
    TimingOptimizationRequest,
    TimingOptimizationResult,
    WeatherWindow,
)
from timing_services import TimingOptimizationAdapter, TimingResultRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/fertilizer-timing", tags=["fertilizer-timing"])


def get_adapter() -> TimingOptimizationAdapter:
    return TimingOptimizationAdapter()


def get_repository() -> TimingResultRepository:
    return TimingResultRepository()


@router.post(
    "/optimize",
    response_model=TimingOptimizationResult,
    status_code=status.HTTP_200_OK,
)
async def optimize_fertilizer_timing(
    request: TimingOptimizationRequest,
    adapter: TimingOptimizationAdapter = Depends(get_adapter),
    repository: TimingResultRepository = Depends(get_repository),
) -> TimingOptimizationResult:
    """
    Run comprehensive fertilizer timing optimization and persist the result.
    """
    try:
        result = await adapter.optimize(request)
        await repository.save_result(request, result)
        return result
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Timing optimization failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Timing optimization failed: {exc}",
        ) from exc


@router.post(
    "/quick-optimize",
    response_model=TimingOptimizationResult,
    status_code=status.HTTP_200_OK,
)
async def quick_optimize(
    request: TimingOptimizationRequest,
    adapter: TimingOptimizationAdapter = Depends(get_adapter),
) -> TimingOptimizationResult:
    """
    Provide a quick optimization without persistence.
    """
    try:
        return await adapter.quick_optimize(request)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Quick timing optimization failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quick optimization failed: {exc}",
        ) from exc


@router.post(
    "/weather-windows",
    response_model=List[WeatherWindow],
    status_code=status.HTTP_200_OK,
)
async def analyze_weather_windows(
    request: TimingOptimizationRequest,
    adapter: TimingOptimizationAdapter = Depends(get_adapter),
) -> List[WeatherWindow]:
    """
    Return available weather windows for the provided request.
    """
    try:
        return await adapter.analyze_weather_windows(request)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Weather window analysis failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Weather analysis failed: {exc}",
        ) from exc


@router.post(
    "/crop-stages",
    response_model=Dict[str, str],
    status_code=status.HTTP_200_OK,
)
async def forecast_crop_stages(
    request: TimingOptimizationRequest,
    adapter: TimingOptimizationAdapter = Depends(get_adapter),
) -> Dict[str, str]:
    """
    Forecast crop growth stages for the provided field and planting date.
    """
    try:
        return await adapter.determine_crop_stages(request)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Crop stage forecasting failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Crop stage forecasting failed: {exc}",
        ) from exc


@router.post(
    "/split-applications",
    response_model=List[SplitApplicationPlan],
    status_code=status.HTTP_200_OK,
)
async def generate_split_applications(
    request: TimingOptimizationRequest,
    adapter: TimingOptimizationAdapter = Depends(get_adapter),
) -> List[SplitApplicationPlan]:
    """
    Generate split application plans for the provided request.
    """
    try:
        return await adapter.optimize_split_applications(request)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Split application generation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Split application generation failed: {exc}",
        ) from exc
