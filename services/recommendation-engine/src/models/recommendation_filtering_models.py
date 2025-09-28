"""
Extended models for recommendation engine with filtering capabilities.

This module provides enhanced models that support advanced filtering 
integration with the crop taxonomy service.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from .agricultural_models import (
        RecommendationRequest as BaseRecommendationRequest,
        RecommendationResponse,
        RecommendationItem,
        LocationData,
        SoilData,
        FarmProfile,
        CropData,
        UserContext
    )
    from services.crop_taxonomy.src.models.crop_filtering_models import (
        TaxonomyFilterCriteria
    )
except ImportError:
    # Fallback imports
    from pydantic import BaseModel
    from typing import Optional
    class LocationData(BaseModel):
        latitude: float
        longitude: float
    class SoilData(BaseModel):
        ph: Optional[float] = None
    class FarmProfile(BaseModel):
        farm_size_acres: float
    class CropData(BaseModel):
        pass
    class UserContext(BaseModel):
        pass
    class RecommendationItem(BaseModel):
        title: str
        confidence_score: float
    class RecommendationResponse(BaseModel):
        request_id: str
        question_type: str
        overall_confidence: float
        recommendations: list = []
    class BaseRecommendationRequest(BaseModel):
        request_id: str
        question_type: str
        location: Optional[LocationData] = None
        soil_data: Optional[SoilData] = None
        farm_profile: Optional[FarmProfile] = None
        crop_data: Optional[CropData] = None
        user_context: Optional[UserContext] = None
    class TaxonomyFilterCriteria(BaseModel):
        pass


class RecommendationRequestWithFiltering(BaseRecommendationRequest):
    """
    Enhanced recommendation request that includes filtering criteria.
    
    This extends the base RecommendationRequest with fields for advanced
    filtering capabilities from the crop taxonomy service.
    """
    
    # Advanced filtering criteria from crop taxonomy service
    filter_criteria: Optional[TaxonomyFilterCriteria] = Field(
        None, 
        description="Advanced taxonomy filter criteria for crop selection"
    )
    
    # Preference-based filtering
    user_preferences: Optional[Dict[str, float]] = Field(
        None,
        description="User preferences mapping crop names to preference scores (0-1)"
    )
    
    # Include filter explanation in results
    include_filter_explanation: bool = Field(
        default=True,
        description="Include explanation of how filters affected recommendations"
    )
    
    # Filter impact analysis request
    request_filter_impact_analysis: bool = Field(
        default=False,
        description="Request filter impact analysis with recommendations"
    )
    
    # Preference weights for different filtering aspects
    preference_weights: Optional[Dict[str, float]] = Field(
        default_factory=dict,
        description="Weights for different preference categories in filtering"
    )
    
    class Config:
        # Allow extra fields for flexibility
        extra = "allow"


class FilterImpactAnalysis(BaseModel):
    """
    Model for filter impact analysis results.
    """
    
    original_count: int = Field(..., description="Number of recommendations before filtering")
    filtered_count: int = Field(..., description="Number of recommendations after filtering")
    filter_reduction_percentage: float = Field(..., description="Percentage reduction due to filtering")
    most_affected_criteria: list = Field(default_factory=list, description="Criteria that most affected recommendations")
    alternative_suggestions: list = Field(default_factory=list, description="Alternative crops suggested due to filtering")
    filter_optimization_recommendations: list = Field(default_factory=list, description="Recommendations for filter optimization")
    baseline_recommendations: list = Field(default_factory=list, description="Original recommendation titles before filtering")
    filtered_recommendations: list = Field(default_factory=list, description="Filtered recommendation titles")


class FilteredRecommendationResponse(RecommendationResponse):
    """
    Enhanced response that includes filtering information.
    """
    
    # Filter impact analysis if requested
    filter_impact_analysis: Optional[FilterImpactAnalysis] = Field(
        None,
        description="Analysis of how filters impacted recommendations"
    )
    
    # Applied filter summary
    applied_filters_summary: Optional[Dict[str, Any]] = Field(
        None,
        description="Summary of filters that were applied"
    )
    
    # Filter-specific warnings
    filter_warnings: list = Field(
        default_factory=list,
        description="Warnings related to filtering"
    )
    
    # Filter optimization suggestions
    filter_optimization_suggestions: list = Field(
        default_factory=list,
        description="Suggestions for optimizing filter criteria"
    )


# Import and extend existing enums if needed
try:
    from .agricultural_models import CropCategory, PrimaryUse, GrowthHabit
except ImportError:
    from enum import Enum
    class CropCategory(str, Enum):
        GRAIN_CROPS = "grain_crops"
        OILSEED_CROPS = "oilseed_crops"
        LEGUME_CROPS = "legume_crops"
        FORAGE_CROPS = "forage_crops"
        COVER_CROPS = "cover_crops"
    
    class PrimaryUse(str, Enum):
        FOOD_PRODUCTION = "food_production"
        FEED_PRODUCTION = "feed_production"
        INDUSTRIAL_USE = "industrial_use"
        SOIL_IMPROVEMENT = "soil_improvement"
    
    class GrowthHabit(str, Enum):
        ERECT = "erect"
        SPREADING = "spreading"
        VINE = "vine"
        BUSH = "bush"