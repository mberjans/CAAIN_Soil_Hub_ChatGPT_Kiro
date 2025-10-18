"""
API routes for fertilizer strategy management endpoints.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..models.strategy_management_models import (
    SaveStrategyRequest,
    StrategyComparisonRequest,
    StrategyComparisonResponse,
    StrategySaveResponse,
)
from ..services.strategy_management_service import StrategyManagementService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/strategies", tags=["strategy-management"])


async def get_strategy_management_service() -> StrategyManagementService:
    """Dependency injection helper."""
    return StrategyManagementService()


@router.post("/save", response_model=StrategySaveResponse, status_code=status.HTTP_200_OK)
async def save_strategy(
    request: SaveStrategyRequest,
    service: StrategyManagementService = Depends(get_strategy_management_service),
) -> StrategySaveResponse:
    """
    Save fertilizer strategies with full version control support.

    Features:
    - Strategy persistence with automatic version numbering
    - Template support for reusable strategies
    - Sharing configuration for collaboration
    - ROI and economic summaries captured per version
    """
    try:
        response = await service.save_strategy(request)
        return response
    except ValueError as error:
        logger.warning("Strategy save validation error: %s", error)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    except Exception as error:
        logger.error("Strategy save failed: %s", error)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Strategy save failed") from error


@router.get("/compare", response_model=StrategyComparisonResponse, status_code=status.HTTP_200_OK)
async def compare_strategies(
    strategy_ids: List[str] = Query(..., description="Strategy identifiers to compare"),
    include_metrics: Optional[List[str]] = Query(None, description="Optional metrics to include"),
    comparison_window_days: Optional[int] = Query(
        None,
        ge=1,
        description="Historical window in days for performance-based metrics",
    ),
    service: StrategyManagementService = Depends(get_strategy_management_service),
) -> StrategyComparisonResponse:
    """
    Compare fertilizer strategies across economic and environmental metrics.

    Provides multi-strategy comparisons to support trade-off analysis and decision making.
    """
    strategy_id_list: List[str] = []
    for identifier in strategy_ids:
        strategy_id_list.append(identifier)

    metrics_list: List[str] = []
    if include_metrics is not None:
        for metric in include_metrics:
            metrics_list.append(metric)

    request = StrategyComparisonRequest(
        strategy_ids=strategy_id_list,
        include_metrics=metrics_list,
        comparison_window_days=comparison_window_days,
    )

    try:
        response = await service.compare_strategies(request)
        return response
    except ValueError as error:
        logger.warning("Strategy comparison validation error: %s", error)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    except LookupError as error:
        logger.warning("Strategy comparison missing data: %s", error)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except Exception as error:
        logger.error("Strategy comparison failed: %s", error)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Strategy comparison failed") from error
