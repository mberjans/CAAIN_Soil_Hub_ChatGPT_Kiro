from fastapi import APIRouter, Depends, HTTPException
from typing import List

from ..models.micronutrient_models import (
    MicronutrientData,
    ToxicityRiskAssessment,
    OverApplicationAssessment,
    MicronutrientRecommendation,
    Micronutrient,
    MicronutrientThresholds
)
from ..services.micronutrient_service import MicronutrientService

router = APIRouter(prefix="/api/v1/micronutrients", tags=["Micronutrient Management"])

async def get_micronutrient_service() -> MicronutrientService:
    return MicronutrientService()

@router.post(
    "/assess-toxicity-risk",
    response_model=ToxicityRiskAssessment,
    summary="Assess micronutrient toxicity risk",
    description="Provides a toxicity risk assessment for a given micronutrient concentration."
)
async def assess_toxicity_risk_endpoint(
    micronutrient_data: MicronutrientData,
    service: MicronutrientService = Depends(get_micronutrient_service)
):
    try:
        return service.assess_toxicity_risk(micronutrient_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post(
    "/assess-over-application",
    response_model=OverApplicationAssessment,
    summary="Assess micronutrient over-application warning",
    description="Provides a warning level for potential micronutrient over-application."
)
async def assess_over_application_endpoint(
    micronutrient_data: MicronutrientData,
    service: MicronutrientService = Depends(get_micronutrient_service)
):
    try:
        return service.assess_over_application_warning(micronutrient_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post(
    "/recommendation",
    response_model=MicronutrientRecommendation,
    summary="Get micronutrient application recommendation",
    description="Provides a general recommendation for micronutrient application based on current levels."
)
async def get_recommendation_endpoint(
    micronutrient_data: MicronutrientData,
    crop_type: str = "general",
    service: MicronutrientService = Depends(get_micronutrient_service)
):
    try:
        return service.get_micronutrient_recommendation(micronutrient_data, crop_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(
    "/thresholds/{micronutrient_name}",
    response_model=MicronutrientThresholds,
    summary="Get micronutrient thresholds",
    description="Retrieves optimal ranges, toxicity, and over-application thresholds for a specific micronutrient."
)
async def get_thresholds_endpoint(
    micronutrient_name: Micronutrient,
    service: MicronutrientService = Depends(get_micronutrient_service)
):
    try:
        return service.get_thresholds_for_micronutrient(micronutrient_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
