"""
Recommendation Engine API Routes

FastAPI routes for agricultural recommendations and calculations.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List

try:
    from ..models.agricultural_models import (
        RecommendationRequest,
        RecommendationResponse,
        RecommendationItem,
        ConfidenceFactors
    )
    from ..services.crop_recommendation_service import CropRecommendationService
except ImportError:
    from models.agricultural_models import (
        RecommendationRequest,
        RecommendationResponse,
        RecommendationItem,
        ConfidenceFactors
    )
    from services.crop_recommendation_service import CropRecommendationService

router = APIRouter(prefix="/api/v1", tags=["recommendation-engine"])

# Service dependencies
crop_service = CropRecommendationService()


@router.post("/recommendations/crop-selection", response_model=RecommendationResponse)
async def get_crop_recommendations(request: RecommendationRequest):
    """
    Get crop selection recommendations based on farm conditions.
    
    This endpoint implements Question 1 of the AFAS system:
    "What crop varieties are best suited to my soil type and climate?"
    
    Agricultural Logic:
    - Matches crop requirements to soil pH, drainage, and fertility
    - Considers climate zone, frost dates, and precipitation
    - Ranks varieties by suitability score and yield potential
    """
    try:
        # Get crop recommendations
        recommendations = await crop_service.get_crop_recommendations(request)
        
        # Calculate overall confidence
        if recommendations:
            overall_confidence = sum(rec.confidence_score for rec in recommendations) / len(recommendations)
        else:
            overall_confidence = 0.0
        
        # Build confidence factors
        confidence_factors = ConfidenceFactors(
            soil_data_quality=0.9 if request.soil_data else 0.3,
            regional_data_availability=0.8,  # Would be calculated based on location
            seasonal_appropriateness=0.9,    # Would be calculated based on timing
            expert_validation=0.85           # Based on validation level of algorithms
        )
        
        return RecommendationResponse(
            request_id=request.request_id,
            question_type=request.question_type,
            overall_confidence=overall_confidence,
            confidence_factors=confidence_factors,
            recommendations=recommendations,
            warnings=_generate_warnings(request),
            next_steps=[
                "Consider soil testing for micronutrients",
                "Review crop insurance options", 
                "Plan nitrogen application strategy",
                "Consult local extension service for variety trials"
            ],
            follow_up_questions=[
                "What fertilizer strategy should I use for this crop?",
                "When is the optimal planting time?",
                "What are the expected input costs?"
            ]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating crop recommendations: {str(e)}"
        )


@router.post("/recommendations/fertilizer-strategy", response_model=RecommendationResponse)
async def get_fertilizer_recommendations(request: RecommendationRequest):
    """
    Get fertilizer strategy recommendations.
    
    This endpoint implements multiple AFAS questions related to fertilization:
    - Question 2: How can I improve soil fertility without over-applying fertilizer?
    - Question 5: Should I invest in organic, synthetic, or slow-release fertilizers?
    - Question 16: What is the most cost-effective fertilizer strategy?
    """
    try:
        # Placeholder implementation - would integrate with fertilizer service
        recommendations = [
            RecommendationItem(
                recommendation_type="fertilizer_strategy",
                title="Balanced NPK Approach",
                description="Based on your soil test results, a balanced approach with split nitrogen applications is recommended.",
                priority=1,
                confidence_score=0.85,
                implementation_steps=[
                    "Apply phosphorus and potassium at planting",
                    "Split nitrogen application: 60% pre-plant, 40% side-dress",
                    "Consider slow-release nitrogen for sandy soils",
                    "Monitor crop response and adjust rates"
                ],
                expected_outcomes=[
                    "Improved nutrient use efficiency",
                    "Reduced environmental impact",
                    "Optimized crop yields",
                    "Cost-effective fertilizer use"
                ],
                cost_estimate=85.50,  # per acre
                roi_estimate=250.0,   # percentage
                timing="Apply 2-3 weeks before planting",
                agricultural_sources=[
                    "Iowa State University Extension PM 1688",
                    "4R Nutrient Stewardship Guidelines",
                    "Regional Fertilizer Recommendations"
                ]
            )
        ]
        
        confidence_factors = ConfidenceFactors(
            soil_data_quality=0.9 if request.soil_data else 0.3,
            regional_data_availability=0.8,
            seasonal_appropriateness=0.9,
            expert_validation=0.85
        )
        
        return RecommendationResponse(
            request_id=request.request_id,
            question_type=request.question_type,
            overall_confidence=0.85,
            confidence_factors=confidence_factors,
            recommendations=recommendations,
            warnings=_generate_fertilizer_warnings(request),
            next_steps=[
                "Obtain current fertilizer prices",
                "Schedule soil testing for next year",
                "Consider precision application equipment",
                "Plan application timing with weather"
            ]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating fertilizer recommendations: {str(e)}"
        )


@router.post("/recommendations/soil-management", response_model=RecommendationResponse)
async def get_soil_management_recommendations(request: RecommendationRequest):
    """
    Get soil health and management recommendations.
    
    This endpoint implements soil-related AFAS questions:
    - Question 3: What is the optimal crop rotation plan for my land?
    - Question 10: How do I manage soil pH to optimize nutrient availability?
    - Question 15: Should I adopt no-till or reduced-till practices?
    """
    try:
        # Placeholder implementation - would integrate with soil management service
        recommendations = []
        
        # pH management recommendation
        if request.soil_data and request.soil_data.ph:
            if request.soil_data.ph < 6.0:
                recommendations.append(
                    RecommendationItem(
                        recommendation_type="soil_ph_management",
                        title="Lime Application Needed",
                        description=f"Your soil pH of {request.soil_data.ph} is below optimal range. Lime application will improve nutrient availability.",
                        priority=1,
                        confidence_score=0.9,
                        implementation_steps=[
                            "Apply agricultural limestone at 2-3 tons per acre",
                            "Incorporate lime 6 months before planting",
                            "Retest soil pH after 12 months",
                            "Consider annual maintenance applications"
                        ],
                        expected_outcomes=[
                            "Improved phosphorus availability",
                            "Enhanced microbial activity",
                            "Better crop nutrient uptake",
                            "Increased yield potential"
                        ],
                        cost_estimate=45.00,
                        timing="Fall application preferred",
                        agricultural_sources=[
                            "USDA Soil pH Management Guidelines",
                            "State Extension Lime Recommendations"
                        ]
                    )
                )
        
        confidence_factors = ConfidenceFactors(
            soil_data_quality=0.9 if request.soil_data else 0.3,
            regional_data_availability=0.8,
            seasonal_appropriateness=0.9,
            expert_validation=0.85
        )
        
        return RecommendationResponse(
            request_id=request.request_id,
            question_type=request.question_type,
            overall_confidence=0.8,
            confidence_factors=confidence_factors,
            recommendations=recommendations,
            warnings=_generate_soil_warnings(request),
            next_steps=[
                "Schedule comprehensive soil testing",
                "Develop long-term soil health plan",
                "Consider cover crop integration",
                "Evaluate tillage practices"
            ]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating soil management recommendations: {str(e)}"
        )


def _generate_warnings(request: RecommendationRequest) -> List[str]:
    """Generate warnings based on request data."""
    warnings = []
    
    if not request.soil_data:
        warnings.append("Recommendations are based on general conditions. Soil testing is strongly recommended for accurate advice.")
    
    if request.soil_data and request.soil_data.ph:
        if request.soil_data.ph < 5.0:
            warnings.append("Extremely acidic soil may limit crop options and require significant lime application.")
        elif request.soil_data.ph > 8.5:
            warnings.append("Very alkaline soil may cause micronutrient deficiencies.")
    
    return warnings


def _generate_fertilizer_warnings(request: RecommendationRequest) -> List[str]:
    """Generate fertilizer-specific warnings."""
    warnings = []
    
    warnings.append("Always follow label instructions and local regulations for fertilizer application.")
    warnings.append("Consider environmental conditions and weather forecasts before application.")
    
    if request.location and request.location.latitude > 45:
        warnings.append("Northern locations may have shorter application windows due to weather.")
    
    return warnings


def _generate_soil_warnings(request: RecommendationRequest) -> List[str]:
    """Generate soil management warnings."""
    warnings = []
    
    warnings.append("Soil management changes take time to show results. Plan for multi-year improvements.")
    
    if request.soil_data and request.soil_data.organic_matter_percent:
        if request.soil_data.organic_matter_percent < 2.0:
            warnings.append("Low organic matter may require significant management changes and time to improve.")
    
    return warnings