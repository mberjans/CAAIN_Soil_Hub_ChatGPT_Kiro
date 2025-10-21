from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging

from ..models.micronutrient_models import (
    MicronutrientApplicationRequest,
    MicronutrientApplicationResponse
)
from ..services.micronutrient_application_service import MicronutrientApplicationService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/micronutrients", tags=["micronutrients"])

# Dependency injection for the service
async def get_micronutrient_service() -> MicronutrientApplicationService:
    return MicronutrientApplicationService()

@router.post("/recommend-application", response_model=MicronutrientApplicationResponse)
async def recommend_micronutrient_application(
    request: MicronutrientApplicationRequest,
    service: MicronutrientApplicationService = Depends(get_micronutrient_service)
):
    """
    Provides comprehensive recommendations for micronutrient application methods and timing.

    This endpoint takes into account crop type, growth stage, soil conditions, current
    and target micronutrient levels, application goals, and available equipment to
    suggest optimal application strategies.

    Agricultural Use Cases:
    - Optimize micronutrient delivery for specific crop needs.
    - Improve nutrient use efficiency and reduce waste.
    - Tailor application methods based on farm equipment and environmental conditions.
    """
    try:
        logger.info(f"API Request: Recommend application for crop {request.crop_type}")
        response = await service.get_application_recommendations(request)
        return response
    except ValueError as e:
        logger.warning(f"Validation error in micronutrient recommendation: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in micronutrient recommendation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during recommendation generation.")

@router.get("/health")
async def health_check():
    """Health check endpoint for the micronutrient application service."""
    return {"status": "healthy", "service": "micronutrient-application"}