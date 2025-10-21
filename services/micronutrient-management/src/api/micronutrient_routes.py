from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...schemas.micronutrient_schemas import MicronutrientRecommendationRequest, MicronutrientRecommendationResponse
from ...services.micronutrient_recommendation_service import MicronutrientRecommendationService
from ...database.database import get_db

router = APIRouter(prefix="/api/v1/micronutrients", tags=["micronutrients"])

@router.post("/recommendations", response_model=MicronutrientRecommendationResponse)
async def get_micronutrient_recommendations(
    request: MicronutrientRecommendationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generates prioritized micronutrient recommendations based on soil test data, crop type, and farm context.

    This endpoint takes current micronutrient levels, soil characteristics (pH, type, organic matter),
    crop information (type, growth stage), and an optional yield goal to provide tailored recommendations.
    Recommendations include priority levels, suggested amounts, application methods, justifications,
    and expected crop impacts.
    """
    try:
        service = MicronutrientRecommendationService(db)
        response = await service.generate_recommendations(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))