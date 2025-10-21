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

# Dependency injection
async def get_micronutrient_service() -> MicronutrientApplicationService:
    return MicronutrientApplicationService()

@router.post("/recommend-application", response_model=MicronutrientApplicationResponse)
async def recommend_micronutrient_application(
    request: MicronutrientApplicationRequest,
    service: MicronutrientApplicationService = Depends(get_micronutrient_service)
):
    """
    Provides comprehensive recommendations for micronutrient application methods and timing.

    This endpoint takes into account crop type, growth stage, soil conditions, current and target
    micronutrient levels, application goals, and available equipment to suggest optimal
    application strategies.

    Agricultural Use Cases:
    - Optimize micronutrient delivery for specific crop needs.
    - Improve nutrient use efficiency and reduce waste.
    - Address micronutrient deficiencies effectively at critical growth stages.
    - Tailor recommendations based on farm-specific equipment and goals.
    """
    try:
        logger.info(f"Received request for micronutrient application: {request.crop_type} at {request.growth_stage}")
        response = await service.get_application_recommendations(request)
        return response
    except ValueError as e:
        logger.error(f"Validation error in recommend_micronutrient_application: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in recommend_micronutrient_application: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate micronutrient application recommendations.")

@router.get("/health")
async def health_check():
    """Health check endpoint for the micronutrient application service."""
    return {"status": "healthy", "service": "micronutrient-application"}
