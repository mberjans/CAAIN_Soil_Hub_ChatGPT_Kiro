"""
Recommendation Engine API Routes

FastAPI routes for agricultural recommendations and calculations.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
import logging

logger = logging.getLogger(__name__)

try:
    from ..models.agricultural_models import (
        RecommendationRequest,
        RecommendationResponse,
        RecommendationItem,
        ConfidenceFactors
    )
    from ..services.recommendation_engine import RecommendationEngine
except ImportError:
    from models.agricultural_models import (
        RecommendationRequest,
        RecommendationResponse,
        RecommendationItem,
        ConfidenceFactors
    )
    from services.recommendation_engine import RecommendationEngine

logger = logging.getLogger(__name__)

# Import sub-routers with error handling
try:
    from .fertilizer_type_selection_routes import router as fertilizer_router
except ImportError:
    try:
        from fertilizer_type_selection_routes import router as fertilizer_router
    except ImportError:
        logger.warning("Fertilizer type selection routes not available")
        fertilizer_router = None

try:
    from .market_price_routes import router as market_price_router
except ImportError:
    try:
        from market_price_routes import router as market_price_router
    except ImportError:
        logger.warning("Market price routes not available")
        market_price_router = None

# Import filtering routes
try:
    from .recommendation_filtering_routes import router as filtering_router
except ImportError:
    try:
        from recommendation_filtering_routes import router as filtering_router
    except ImportError:
        logger.warning("Recommendation filtering routes not available")
        filtering_router = None

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


@router.post("/recommendations/crop-selection-with-filtering", response_model=RecommendationResponse)
async def get_crop_recommendations_with_filtering(request: RecommendationRequest):
    """
    Get crop selection recommendations with advanced filtering integration.
    
    This endpoint enhances the basic crop selection with multi-criteria filtering
    capabilities from the crop taxonomy service.
    
    Features:
    - Pre-filter crops before recommendation generation 
    - Apply complex multi-dimensional filtering criteria
    - Rank recommendations based on filter compatibility
    - Provide detailed explanations of filter impact
    """
    try:
        logger.info(f"Processing crop selection with filtering request: {request.request_id}")
        
        # Validate location data for climate zone detection
        if not request.location:
            raise HTTPException(
                status_code=400,
                detail="Location data is required for crop selection recommendations"
            )
        
        # Check if request has filter criteria
        has_filters = hasattr(request, 'filter_criteria') and request.filter_criteria is not None
        
        if has_filters:
            logger.info(f"Applying filter criteria to request: {request.request_id}")
            request.question_type = "crop_selection_with_filtering"
        else:
            # Fallback to standard processing if no filters provided
            logger.info(f"No filters found, using standard processing for request: {request.request_id}")
            request.question_type = "crop_selection"
        
        return await recommendation_engine.generate_recommendations(request)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating crop recommendations with filtering: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating crop recommendations with filtering: {str(e)}"
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
if fertilizer_router:
    router.include_router(fertilizer_router)

# Include market price routes
if market_price_router:
    router.include_router(market_price_router)

# Include planting date routes
try:
    from .planting_date_routes import router as planting_router
    router.include_router(planting_router)
except ImportError:
    logger.warning("Planting date routes not available")

# Include pH management routes
try:
    from .ph_management_routes import router as ph_router
    router.include_router(ph_router)
    logger.info("pH management routes included successfully")
except ImportError as e:
    logger.warning(f"pH management routes not available: {e}")
    try:
        from ph_management_routes import router as ph_router
        router.include_router(ph_router)
        logger.info("pH management routes included successfully (fallback import)")
    except ImportError as e2:
        logger.warning(f"pH management routes completely unavailable: {e2}")

# Include rotation planning routes
try:
    from .rotation_routes import router as rotation_router, fields_router
    router.include_router(rotation_router)
    router.include_router(fields_router)
    logger.info("Rotation planning and fields routes included successfully")
except ImportError as e:
    logger.warning(f"Rotation planning routes not available: {e}")
    try:
        from rotation_routes import router as rotation_router, fields_router
        router.include_router(rotation_router)
        router.include_router(fields_router)
        logger.info("Rotation planning and fields routes included successfully (fallback import)")
    except ImportError as e2:
        logger.warning(f"Rotation planning routes completely unavailable: {e2}")