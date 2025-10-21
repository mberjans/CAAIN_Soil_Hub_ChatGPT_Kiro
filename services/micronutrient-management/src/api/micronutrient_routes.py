from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from datetime import date

from ..models.micronutrient_models import (
    MicronutrientLevel,
    DeficiencySymptom,
    MicronutrientDeficiencyAssessment,
    Recommendation
)
from ..services.micronutrient_assessment_service import MicronutrientAssessmentService
from ..services.micronutrient_recommendation_service import MicronutrientRecommendationService

router = APIRouter()

# Dependency injection for services
async def get_assessment_service() -> MicronutrientAssessmentService:
    return MicronutrientAssessmentService()

async def get_recommendation_service() -> MicronutrientRecommendationService:
    return MicronutrientRecommendationService()

@router.post(
    "/assess",
    response_model=MicronutrientDeficiencyAssessment,
    status_code=status.HTTP_200_OK,
    summary="Assess micronutrient deficiencies",
    description="Performs a comprehensive assessment of micronutrient deficiencies based on soil/tissue tests and visual symptoms."
)
async def assess_micronutrient_deficiencies(
    farm_id: UUID,
    field_id: UUID,
    crop_type: str,
    growth_stage: str,
    soil_type: str,
    micronutrient_levels: List[MicronutrientLevel],
    visual_symptoms: List[DeficiencySymptom] = [],
    assessment_service: MicronutrientAssessmentService = Depends(get_assessment_service)
):
    """Assess micronutrient deficiencies for a given farm and field."""
    try:
        assessment = await assessment_service.assess_deficiencies(
            farm_id=farm_id,
            field_id=field_id,
            crop_type=crop_type,
            growth_stage=growth_stage,
            soil_type=soil_type,
            micronutrient_levels=micronutrient_levels,
            visual_symptoms=visual_symptoms
        )
        return assessment
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post(
    "/recommendations",
    response_model=List[Recommendation],
    status_code=status.HTTP_200_OK,
    summary="Get micronutrient recommendations",
    description="Generates recommendations for correcting identified micronutrient deficiencies."
)
async def get_micronutrient_recommendations(
    assessment: MicronutrientDeficiencyAssessment,
    recommendation_service: MicronutrientRecommendationService = Depends(get_recommendation_service)
):
    """Get recommendations for a given micronutrient deficiency assessment."""
    try:
        recommendations = await recommendation_service.get_recommendations(assessment)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Checks the health of the micronutrient management service."
)
async def health_check():
    return {"status": "healthy", "service": "micronutrient-management"}