
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
import logging

try:
    from ..services.personalization_service import PersonalizationService
except ImportError:
    from services.personalization_service import PersonalizationService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/personalization", tags=["personalization"])

# Dependency injection
async def get_personalization_service() -> PersonalizationService:
    return PersonalizationService()

@router.post("/learn")
async def learn_user_preferences(
    user_id: str,
    user_data: Dict[str, Any],
    service: PersonalizationService = Depends(get_personalization_service)
):
    """
    Endpoint to learn and update user preferences.
    """
    try:
        result = await service.learn_user_preferences(user_id, user_data)
        return result
    except Exception as e:
        logger.error(f"Error learning user preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/adapt")
async def adapt_recommendations(
    recommendations: List[Dict[str, Any]],
    user_preferences: Dict[str, Any],
    service: PersonalizationService = Depends(get_personalization_service)
):
    """
    Endpoint to adapt recommendations based on user preferences.
    """
    try:
        result = await service.adapt_recommendations(recommendations, user_preferences)
        return result
    except Exception as e:
        logger.error(f"Error adapting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback")
async def integrate_feedback(
    feedback_data: Dict[str, Any],
    service: PersonalizationService = Depends(get_personalization_service)
):
    """
    Endpoint to integrate user feedback.
    """
    try:
        result = await service.integrate_feedback(feedback_data)
        return result
    except Exception as e:
        logger.error(f"Error integrating feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))
