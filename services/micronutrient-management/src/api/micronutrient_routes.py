from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from ...schemas.micronutrient_schemas import (
    MicronutrientRecommendationRequest, 
    MicronutrientRecommendationResponse,
    ApplicationMethodRequest,
    TimingRecommendationRequest,
    ApplicationMethodAndTimingResponse
)
from ...services.micronutrient_recommendation_service import MicronutrientRecommendationService
from ...services.application_method_service import ApplicationMethodService
from ...services.timing_service import TimingService
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

@router.post("/application-method", response_model=ApplicationMethodAndTimingResponse)
async def get_application_method_recommendation(
    request: ApplicationMethodRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generates optimal application method recommendations based on crop type, growth stage,
    deficiency severity, equipment availability, and field conditions.

    This endpoint determines the best application method (soil, foliar, seed treatment, 
    fertigation, broadcast, banded) considering all relevant factors.
    """
    try:
        service = ApplicationMethodService(db)
        recommendation = await service.get_optimal_application_method(request)
        
        # For now, we'll call the timing service separately to get timing recommendation
        timing_service = TimingService(db)
        timing_request = TimingRecommendationRequest(
            crop_type=request.crop_type,
            growth_stage=request.growth_stage,
            nutrient_uptake_pattern=f"{request.nutrient_type.value} uptake pattern",
            weather_conditions="Clear",  # Default, should be provided by user
            nutrient_type=request.nutrient_type,
            application_method=recommendation.method,
            field_conditions=request.field_conditions
        )
        timing_recommendation = await timing_service.get_optimal_timing(timing_request)
        
        response = ApplicationMethodAndTimingResponse(
            request_id=str(uuid.uuid4()),
            application_method=recommendation,
            timing=timing_recommendation,
            economic_efficiency=0.8,  # Default value, could be calculated based on various factors
            risk_assessment="Medium",  # Default value, could be calculated based on various factors
            notes=["Follow recommended application method and timing for optimal results"]
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/timing", response_model=TimingRecommendationRequest)
async def get_timing_recommendation(
    request: TimingRecommendationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generates optimal timing recommendations based on crop growth stages, nutrient uptake patterns,
    weather conditions, and compatibility with other inputs.

    This endpoint determines the best timing for micronutrient application considering all relevant factors.
    """
    try:
        service = TimingService(db)
        response = await service.get_optimal_timing(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/application-method-and-timing", response_model=ApplicationMethodAndTimingResponse)
async def get_application_method_and_timing_recommendation(
    request: ApplicationMethodRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generates both application method and timing recommendations in a single request.

    This endpoint integrates both services to provide a comprehensive recommendation
    combining optimal application method and timing for micronutrient application.
    """
    try:
        # Get application method recommendation
        method_service = ApplicationMethodService(db)
        method_recommendation = await method_service.get_optimal_application_method(request)
        
        # Get timing recommendation based on the chosen application method
        timing_service = TimingService(db)
        timing_request = TimingRecommendationRequest(
            crop_type=request.crop_type,
            growth_stage=request.growth_stage,
            nutrient_uptake_pattern=f"{request.nutrient_type.value} uptake pattern",
            weather_conditions="Clear",  # Default, should come from additional input if available
            nutrient_type=request.nutrient_type,
            application_method=method_recommendation.method,
            field_conditions=request.field_conditions
        )
        timing_recommendation = await timing_service.get_optimal_timing(timing_request)
        
        # Calculate economic efficiency (this could be more sophisticated)
        economic_efficiency = min(1.0, (method_recommendation.confidence_score + timing_recommendation.expected_efficacy) / 2)
        
        # Determine risk assessment based on confidence scores
        risk_assessment = "Low" if method_recommendation.confidence_score > 0.8 and timing_recommendation.expected_efficacy > 0.8 else \
                         "Medium" if method_recommendation.confidence_score > 0.6 and timing_recommendation.expected_efficacy > 0.6 else "High"
        
        response = ApplicationMethodAndTimingResponse(
            request_id=str(uuid.uuid4()),
            application_method=method_recommendation,
            timing=timing_recommendation,
            economic_efficiency=economic_efficiency,
            risk_assessment=risk_assessment,
            notes=[
                f"Recommended application method: {method_recommendation.method.value}",
                f"Recommended timing: {timing_recommendation.timing.value}",
                f"Expected efficacy: {timing_recommendation.expected_efficacy:.2f}",
                f"Risk level: {risk_assessment}"
            ]
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))