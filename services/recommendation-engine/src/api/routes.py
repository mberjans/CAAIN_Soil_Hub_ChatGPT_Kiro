"""
Recommendation Engine API Routes

FastAPI routes for agricultural recommendations and calculations.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging

try:
    from ..models.agricultural_models import (
        RecommendationRequest,
        RecommendationResponse,
        RecommendationItem,
        ConfidenceFactors
    )
    from ..services.recommendation_engine import RecommendationEngine
    from .fertilizer_type_selection_routes import router as fertilizer_router
    from .market_price_routes import router as market_price_router
except ImportError:
    from models.agricultural_models import (
        RecommendationRequest,
        RecommendationResponse,
        RecommendationItem,
        ConfidenceFactors
    )
    from services.recommendation_engine import RecommendationEngine
    from fertilizer_type_selection_routes import router as fertilizer_router
    from market_price_routes import router as market_price_router

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["recommendation-engine"])

# Central recommendation engine
recommendation_engine = RecommendationEngine()


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
    - Auto-detects climate zone if not provided in request
    """
    try:
        logger.info(f"Processing crop selection request: {request.request_id}")
        
        # Validate location data for climate zone detection
        if not request.location:
            raise HTTPException(
                status_code=400,
                detail="Location data is required for crop selection recommendations"
            )
        
        # Log climate zone if available
        climate_zone = getattr(request.location, 'climate_zone', None)
        if climate_zone:
            logger.info(f"Request includes climate zone: {climate_zone}")
        else:
            logger.info("Climate zone will be auto-detected from coordinates")
        
        request.question_type = "crop_selection"
        return await recommendation_engine.generate_recommendations(request)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating crop recommendations: {str(e)}")
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
        logger.info(f"Processing fertilizer strategy request: {request.request_id}")
        request.question_type = "fertilizer_strategy"
        return await recommendation_engine.generate_recommendations(request)
        
    except Exception as e:
        logger.error(f"Error generating fertilizer recommendations: {str(e)}")
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
        logger.info(f"Processing soil management request: {request.request_id}")
        request.question_type = "soil_management"
        return await recommendation_engine.generate_recommendations(request)
        
    except Exception as e:
        logger.error(f"Error generating soil management recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating soil management recommendations: {str(e)}"
        )


# Add endpoints for the specific 5 questions

@router.post("/recommendations/soil-fertility", response_model=RecommendationResponse)
async def get_soil_fertility_recommendations(request: RecommendationRequest):
    """
    Get soil fertility improvement recommendations (Question 2).
    
    "How can I improve soil fertility without over-applying fertilizer?"
    """
    try:
        logger.info(f"Processing soil fertility request: {request.request_id}")
        request.question_type = "soil_fertility"
        return await recommendation_engine.generate_recommendations(request)
        
    except Exception as e:
        logger.error(f"Error generating soil fertility recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating soil fertility recommendations: {str(e)}"
        )


@router.post("/recommendations/crop-rotation", response_model=RecommendationResponse)
async def get_crop_rotation_recommendations(request: RecommendationRequest):
    """
    Get crop rotation recommendations (Question 3).
    
    "What is the optimal crop rotation plan for my land?"
    """
    try:
        logger.info(f"Processing crop rotation request: {request.request_id}")
        request.question_type = "crop_rotation"
        return await recommendation_engine.generate_recommendations(request)
        
    except Exception as e:
        logger.error(f"Error generating crop rotation recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating crop rotation recommendations: {str(e)}"
        )


@router.post("/recommendations/nutrient-deficiency", response_model=RecommendationResponse)
async def get_nutrient_deficiency_recommendations(request: RecommendationRequest):
    """
    Get nutrient deficiency detection recommendations (Question 4).
    
    "How do I know if my soil is deficient in key nutrients?"
    """
    try:
        logger.info(f"Processing nutrient deficiency request: {request.request_id}")
        request.question_type = "nutrient_deficiency"
        return await recommendation_engine.generate_recommendations(request)
        
    except Exception as e:
        logger.error(f"Error generating nutrient deficiency recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating nutrient deficiency recommendations: {str(e)}"
        )


@router.post("/recommendations/fertilizer-selection", response_model=RecommendationResponse)
async def get_fertilizer_selection_recommendations(request: RecommendationRequest):
    """
    Get fertilizer type selection recommendations (Question 5).
    
    "Should I invest in organic, synthetic, or slow-release fertilizers?"
    """
    try:
        logger.info(f"Processing fertilizer selection request: {request.request_id}")
        request.question_type = "fertilizer_selection"
        return await recommendation_engine.generate_recommendations(request)
        
    except Exception as e:
        logger.error(f"Error generating fertilizer selection recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating fertilizer selection recommendations: {str(e)}"
        )


@router.post("/recommendations/generate", response_model=RecommendationResponse)
async def generate_recommendations(request: RecommendationRequest):
    """
    Generate recommendations for any question type.
    
    This is the main endpoint that can handle all agricultural questions
    based on the question_type field in the request.
    """
    try:
        logger.info(f"Processing general recommendation request: {request.request_id}, type: {request.question_type}")
        return await recommendation_engine.generate_recommendations(request)
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating recommendations: {str(e)}"
        )


# Include fertilizer type selection routes
router.include_router(fertilizer_router)

# Include market price routes
router.include_router(market_price_router)