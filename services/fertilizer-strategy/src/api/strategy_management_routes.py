"""
API routes for fertilizer strategy management endpoints.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status

from ..models.strategy_management_models import (
    SaveStrategyRequest,
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
