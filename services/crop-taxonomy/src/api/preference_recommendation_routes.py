"""
TICKET-005_crop-type-filtering-3.3: API Routes for Preference Recommendation Engine

Exposes the preference-based recommendation enhancement engine through REST API endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Tuple, Any
import logging

from ..services.preference_recommendation_engine import (
    preference_recommendation_engine,
    FarmCharacteristics,
    FarmerProfile,
    RecommendationResult,
    RecommendationType
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/preference-recommendations", tags=["preference-recommendations"])


# Request Models
class FarmCharacteristicsRequest(BaseModel):
    """Request model for farm characteristics"""
    location: str = Field(..., description="Farm location")
    climate_zone: str = Field(..., description="Climate zone identifier")
    soil_type: str = Field(..., description="Primary soil type")
    farm_size_acres: float = Field(..., gt=0, description="Farm size in acres")
    precipitation_annual: float = Field(..., ge=0, description="Annual precipitation in inches")
    temperature_range: Tuple[float, float] = Field(..., description="Temperature range (min, max) in Fahrenheit")
    soil_ph: Optional[float] = Field(None, ge=0, le=14, description="Soil pH level")
    irrigation_available: bool = Field(False, description="Whether irrigation is available")
    organic_certification: bool = Field(False, description="Whether farm has organic certification")
    equipment_capabilities: List[str] = Field(default_factory=list, description="Available equipment")


class CropSuggestionRequest(BaseModel):
    """Request model for crop suggestions"""
    farm_characteristics: FarmCharacteristicsRequest
    max_suggestions: int = Field(5, ge=1, le=20, description="Maximum number of suggestions")


class FilterRecommendationRequest(BaseModel):
    """Request model for filter recommendations"""
    farm_characteristics: FarmCharacteristicsRequest
    max_recommendations: int = Field(3, ge=1, le=10, description="Maximum number of recommendations")


class PreferenceOptimizationRequest(BaseModel):
    """Request model for preference optimization"""
    current_preferences: Dict[str, float] = Field(..., description="Current crop preferences (crop -> score 0-1)")
    farm_characteristics: FarmCharacteristicsRequest


class ConflictResolutionRequest(BaseModel):
    """Request model for conflict resolution"""
    preferences: Dict[str, float] = Field(..., description="Crop preferences to analyze for conflicts")
    farm_characteristics: FarmCharacteristicsRequest


class FarmerProfileRequest(BaseModel):
    """Request model for farmer profile registration"""
    farmer_id: str = Field(..., description="Unique farmer identifier")
    experience_years: int = Field(..., ge=0, description="Years of farming experience")
    farm_characteristics: FarmCharacteristicsRequest
    crop_preferences: Dict[str, float] = Field(..., description="Crop preferences (crop -> score 0-1)")
    filter_usage_patterns: Dict[str, int] = Field(..., description="Filter usage patterns (filter -> count)")
    success_metrics: Dict[str, float] = Field(..., description="Success metrics (metric -> score)")


# Response Models
class CropSuggestion(BaseModel):
    """Individual crop suggestion"""
    crop_type: str
    suitability_score: float
    reasons: List[str]


class FilterRecommendation(BaseModel):
    """Individual filter recommendation"""
    filter_type: str
    usage_frequency: float
    effectiveness_score: float
    similar_farmers_count: int


class PreferenceOptimization(BaseModel):
    """Individual preference optimization"""
    optimization_type: str
    crop: str
    current_preference: float
    recommended_preference: float
    reason: str


class ConflictResolution(BaseModel):
    """Individual conflict resolution"""
    conflict_type: str
    crops_involved: Optional[List[str]] = None
    issue: Optional[str] = None
    recommended_action: str
    recommended_preferences: Optional[Dict[str, float]] = None
    suggested_crops: Optional[List[str]] = None


class RecommendationResponse(BaseModel):
    """Base response model for recommendations"""
    recommendation_type: str
    confidence_score: float
    reasoning: str
    conflicts_detected: List[str] = Field(default_factory=list)


class CropSuggestionResponse(RecommendationResponse):
    """Response model for crop suggestions"""
    suggestions: List[CropSuggestion]


class FilterRecommendationResponse(RecommendationResponse):
    """Response model for filter recommendations"""
    suggestions: List[FilterRecommendation]


class PreferenceOptimizationResponse(RecommendationResponse):
    """Response model for preference optimization"""
    suggestions: List[PreferenceOptimization]


class ConflictResolutionResponse(RecommendationResponse):
    """Response model for conflict resolution"""
    suggestions: List[ConflictResolution]


# Helper Functions
def _convert_farm_characteristics(request: FarmCharacteristicsRequest) -> FarmCharacteristics:
    """Convert request model to domain model"""
    return FarmCharacteristics(
        location=request.location,
        climate_zone=request.climate_zone,
        soil_type=request.soil_type,
        farm_size_acres=request.farm_size_acres,
        precipitation_annual=request.precipitation_annual,
        temperature_range=request.temperature_range,
        soil_ph=request.soil_ph,
        irrigation_available=request.irrigation_available,
        organic_certification=request.organic_certification,
        equipment_capabilities=request.equipment_capabilities
    )


def _convert_recommendation_result(result: RecommendationResult, 
                                 response_class) -> RecommendationResponse:
    """Convert domain result to response model"""
    base_data = {
        "recommendation_type": result.recommendation_type.value,
        "confidence_score": result.confidence_score,
        "reasoning": result.reasoning,
        "conflicts_detected": result.conflicts_detected,
        "suggestions": result.suggestions
    }
    return response_class(**base_data)


# API Endpoints
@router.post("/crop-suggestions", response_model=CropSuggestionResponse)
async def get_crop_suggestions(request: CropSuggestionRequest):
    """
    Get intelligent crop type suggestions based on farm characteristics
    
    This endpoint analyzes farm characteristics including climate zone, soil type,
    farm size, and other factors to suggest the most suitable crop types.
    """
    try:
        farm_characteristics = _convert_farm_characteristics(request.farm_characteristics)
        
        result = preference_recommendation_engine.suggest_crop_types(
            farm_characteristics=farm_characteristics,
            max_suggestions=request.max_suggestions
        )
        
        return _convert_recommendation_result(result, CropSuggestionResponse)
        
    except Exception as e:
        logger.error(f"Error generating crop suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate crop suggestions: {str(e)}")


@router.post("/filter-recommendations", response_model=FilterRecommendationResponse)
async def get_filter_recommendations(request: FilterRecommendationRequest):
    """
    Get filter recommendations based on similar farmers
    
    This endpoint analyzes farms with similar characteristics and recommends
    filters that have been effective for similar operations.
    """
    try:
        farm_characteristics = _convert_farm_characteristics(request.farm_characteristics)
        
        result = preference_recommendation_engine.recommend_filters_by_similarity(
            farm_characteristics=farm_characteristics,
            max_recommendations=request.max_recommendations
        )
        
        return _convert_recommendation_result(result, FilterRecommendationResponse)
        
    except Exception as e:
        logger.error(f"Error generating filter recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate filter recommendations: {str(e)}")


@router.post("/preference-optimization", response_model=PreferenceOptimizationResponse)
async def optimize_preferences(request: PreferenceOptimizationRequest):
    """
    Optimize crop preferences based on farm characteristics
    
    This endpoint analyzes current crop preferences against farm characteristics
    and suggests optimizations to improve alignment and identify opportunities.
    """
    try:
        # Validate preference scores
        for crop, score in request.current_preferences.items():
            if not 0.0 <= score <= 1.0:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid preference score for {crop}: {score}. Must be between 0.0 and 1.0"
                )
        
        farm_characteristics = _convert_farm_characteristics(request.farm_characteristics)
        
        result = preference_recommendation_engine.optimize_preferences(
            current_preferences=request.current_preferences,
            farm_characteristics=farm_characteristics
        )
        
        return _convert_recommendation_result(result, PreferenceOptimizationResponse)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error optimizing preferences: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to optimize preferences: {str(e)}")


@router.post("/conflict-resolution", response_model=ConflictResolutionResponse)
async def resolve_preference_conflicts(request: ConflictResolutionRequest):
    """
    Identify and resolve preference conflicts
    
    This endpoint analyzes crop preferences for conflicts such as mutually
    exclusive crops or resource constraints, and provides resolution strategies.
    """
    try:
        # Validate preference scores
        for crop, score in request.preferences.items():
            if not 0.0 <= score <= 1.0:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid preference score for {crop}: {score}. Must be between 0.0 and 1.0"
                )
        
        farm_characteristics = _convert_farm_characteristics(request.farm_characteristics)
        
        result = preference_recommendation_engine.resolve_preference_conflicts(
            preferences=request.preferences,
            farm_characteristics=farm_characteristics
        )
        
        return _convert_recommendation_result(result, ConflictResolutionResponse)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving conflicts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to resolve conflicts: {str(e)}")


@router.post("/register-farmer-profile", response_model=Dict[str, str])
async def register_farmer_profile(request: FarmerProfileRequest):
    """
    Register a farmer profile for similarity-based recommendations
    
    This endpoint registers a farmer's profile including farm characteristics,
    preferences, and usage patterns to improve similarity-based recommendations.
    """
    try:
        # Validate preference and success metric scores
        for crop, score in request.crop_preferences.items():
            if not 0.0 <= score <= 1.0:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid crop preference score for {crop}: {score}. Must be between 0.0 and 1.0"
                )
        
        for metric, score in request.success_metrics.items():
            if not 0.0 <= score <= 1.0:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid success metric score for {metric}: {score}. Must be between 0.0 and 1.0"
                )
        
        # Validate filter usage counts
        for filter_type, count in request.filter_usage_patterns.items():
            if count < 0:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid filter usage count for {filter_type}: {count}. Must be non-negative"
                )
        
        farm_characteristics = _convert_farm_characteristics(request.farm_characteristics)
        
        farmer_profile = FarmerProfile(
            farmer_id=request.farmer_id,
            experience_years=request.experience_years,
            farm_characteristics=farm_characteristics,
            crop_preferences=request.crop_preferences,
            filter_usage_patterns=request.filter_usage_patterns,
            success_metrics=request.success_metrics
        )
        
        preference_recommendation_engine.register_farmer_profile(farmer_profile)
        
        return {
            "status": "success",
            "message": f"Farmer profile {request.farmer_id} registered successfully",
            "farmer_id": request.farmer_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering farmer profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to register farmer profile: {str(e)}")


@router.get("/farmer-profiles", response_model=Dict[str, Any])
async def get_registered_farmer_profiles():
    """
    Get information about registered farmer profiles
    
    Returns summary information about currently registered farmer profiles
    for administrative purposes.
    """
    try:
        profiles = preference_recommendation_engine.farmer_profiles
        
        summary = {
            "total_profiles": len(profiles),
            "farmer_ids": list(profiles.keys()),
            "profiles_by_climate_zone": {},
            "profiles_by_soil_type": {},
            "average_farm_size": 0.0,
            "average_experience": 0.0
        }
        
        if profiles:
            # Calculate statistics
            farm_sizes = []
            experiences = []
            
            for farmer_id, profile in profiles.items():
                # Group by climate zone
                zone = profile.farm_characteristics.climate_zone
                if zone not in summary["profiles_by_climate_zone"]:
                    summary["profiles_by_climate_zone"][zone] = 0
                summary["profiles_by_climate_zone"][zone] += 1
                
                # Group by soil type
                soil = profile.farm_characteristics.soil_type
                if soil not in summary["profiles_by_soil_type"]:
                    summary["profiles_by_soil_type"][soil] = 0
                summary["profiles_by_soil_type"][soil] += 1
                
                # Collect for averages
                farm_sizes.append(profile.farm_characteristics.farm_size_acres)
                experiences.append(profile.experience_years)
            
            summary["average_farm_size"] = round(sum(farm_sizes) / len(farm_sizes), 1)
            summary["average_experience"] = round(sum(experiences) / len(experiences), 1)
        
        return summary
        
    except Exception as e:
        logger.error(f"Error retrieving farmer profiles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve farmer profiles: {str(e)}")


@router.get("/recommendation-capabilities", response_model=Dict[str, Any])
async def get_recommendation_capabilities():
    """
    Get information about the recommendation engine's capabilities
    
    Returns information about supported climate zones, soil types, crops,
    and other capabilities of the recommendation engine.
    """
    try:
        engine = preference_recommendation_engine
        
        capabilities = {
            "supported_climate_zones": [
                "zone_3", "zone_4", "zone_5", "zone_6", "zone_7", 
                "zone_8", "zone_9", "zone_10"
            ],
            "supported_soil_types": [
                "clay", "loam", "sandy", "silt", "peat", "rocky"
            ],
            "crop_categories": list(engine.crop_compatibility_matrix.keys()),
            "supported_crops_by_category": engine.crop_compatibility_matrix,
            "filter_types": list(engine.filter_effectiveness_scores.keys()),
            "recommendation_types": [rt.value for rt in RecommendationType],
            "max_suggestions_per_request": 20,
            "max_recommendations_per_request": 10,
            "similarity_threshold": 0.3,
            "version": "1.0.0"
        }
        
        return capabilities
        
    except Exception as e:
        logger.error(f"Error retrieving capabilities: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve capabilities: {str(e)}")


# Health check endpoint
@router.get("/health", response_model=Dict[str, str])
async def health_check():
    """Health check for the preference recommendation service"""
    return {
        "status": "healthy",
        "service": "preference-recommendation-engine",
        "version": "1.0.0"
    }