"""
Smart Filter Suggestion API Routes

FastAPI routes for AI-powered crop filtering suggestions.
Implements endpoints specifically at /api/v1/crop-taxonomy/ as required.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any

# Try direct relative imports first, then fallback absolute imports
try:
    from ..services.smart_filter_suggestion_service import smart_filter_suggestion_service
    from ..models.crop_filtering_models import (
        FilterSuggestionRequest,
        FilterSuggestionResponse
    )
except ImportError:
    # Fallback imports in case of circular dependencies
    try:
        from services.smart_filter_suggestion_service import smart_filter_suggestion_service
        from models.crop_filtering_models import (
            FilterSuggestionRequest,
            FilterSuggestionResponse
        )
    except ImportError:
        # If all imports fail, create mock objects for the server to start
        print("Warning: smart_filter_suggestion_service not available, using fallback")
        smart_filter_suggestion_service = None

        # Define minimal model classes as fallbacks if needed
        from pydantic import BaseModel
        class FilterSuggestionRequest(BaseModel):
            pass
        class FilterSuggestionResponse(BaseModel):
            pass

router = APIRouter(prefix="/api/v1/crop-taxonomy", tags=["smart-filtering"])

@router.post("/smart-filter-suggestions", response_model=FilterSuggestionResponse)
async def get_smart_filter_suggestions(
    request: FilterSuggestionRequest
):
    """
    POST /api/v1/crop-taxonomy/smart-filter-suggestions - AI-powered smart filtering suggestions
    
    **Features**:
    - Machine learning-based filter suggestions from user behavior
    - Contextual recommendations (seasonal, weather-based, market-driven)
    - Integration with existing AI agent service and preference learning
    - Performance optimization with cached ML model predictions
    - Agricultural constraint validation and optimization
    
    **Request Schema**:
    ```json
    {
      "request_id": "unique-request-id",
      "context": {
        "farm_location": {"latitude": 41.8781, "longitude": -87.6298},
        "soil_conditions": {"ph": 6.5, "organic_matter": 3.2, "texture": "loam"},
        "climate_data": {"zone": "5b", "precipitation": 35, "temperature": 22},
        "market_goals": ["premium_pricing", "organic_certification"],
        "sustainability_focus": "carbon_sequestration",
        "focus_areas": ["organic", "drought", "profit"]
      },
      "climate_zone": "5b",
      "location_coordinates": {"latitude": 41.8781, "longitude": -87.6298},
      "focus_areas": ["organic", "drought", "profit"],
      "max_suggestions": 5,
      "include_presets": true,
      "use_ml_enhancement": true
    }
    ```
    
    Returns intelligent filter suggestions with AI-powered insights.
    """
    if smart_filter_suggestion_service is None:
        raise HTTPException(status_code=503, detail="Smart filter suggestion service unavailable")
    try:
        result = await smart_filter_suggestion_service.generate_smart_suggestions(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Smart filter suggestion error: {str(e)}")

@router.get("/smart-filter-options", response_model=Dict[str, Any])
async def get_dynamic_smart_filter_options(
    request_id: str = Query(..., description="Unique request identifier"),
    climate_zone: Optional[str] = Query(None, description="Primary climate zone (e.g., 5b)"),
    latitude: Optional[float] = Query(None, description="Latitude for context-aware options"),
    longitude: Optional[float] = Query(None, description="Longitude for context-aware options"),
    soil_ph: Optional[float] = Query(None, description="Measured soil pH"),
    soil_drainage: Optional[str] = Query(None, description="Soil drainage class"),
    market_goal: Optional[str] = Query(None, description="Primary market goal"),
    sustainability_focus: Optional[str] = Query(None, description="Sustainability priority"),
    focus_areas: Optional[List[str]] = Query(None, description="Focus areas such as organic, drought, profit"),
    max_suggestions: int = Query(5, ge=0, le=20, description="Maximum number of suggestions to return"),
    include_presets: bool = Query(True, description="Include preset recommendations")
):
    """
    GET /api/v1/crop-taxonomy/smart-filter-options - Dynamic smart filter options
    
    **Features**:
    - AI-powered filter options based on machine learning models
    - Context-aware recommendations from seasonal and weather patterns
    - Integration with preference learning for personalized options
    - Location-based filter suggestions with agricultural validation
    - Performance optimization with cached ML predictions
    
    **Response Includes**:
    - AI-generated filter suggestions with confidence scoring
    - Context-aware recommendations (seasonal, weather-based)
    - Personalized options based on user preferences
    - Preset recommendations with explanations
    - Agricultural constraint validation
    
    **Caching**: Redis cache with 1-hour TTL, context-based cache keys
    """
    try:
        # Create a FilterSuggestionRequest from query parameters
        context: Dict[str, Any] = {}
        soil_profile: Dict[str, Any] = {}
        if soil_ph is not None:
            soil_profile['ph'] = soil_ph
        if soil_drainage is not None:
            soil_profile['drainage'] = soil_drainage
        if len(soil_profile) > 0:
            context['soil_profile'] = soil_profile

        if market_goal is not None:
            goals: List[str] = []
            goals.append(market_goal)
            context['market_goals'] = goals

        if sustainability_focus is not None:
            context['sustainability_focus'] = sustainability_focus

        focus_area_values: List[str] = []
        if focus_areas is not None:
            for item in focus_areas:
                focus_area_values.append(item)

        location_coordinates: Optional[Dict[str, float]] = None
        if latitude is not None and longitude is not None:
            location_coordinates = {'latitude': latitude, 'longitude': longitude}

        request = FilterSuggestionRequest(
            request_id=request_id,
            context=context,
            climate_zone=climate_zone,
            location_coordinates=location_coordinates,
            focus_areas=focus_area_values,
            max_suggestions=max_suggestions,
            include_presets=include_presets
        )

        if smart_filter_suggestion_service is None:
            raise HTTPException(status_code=503, detail="Smart filter suggestion service unavailable")
            
        result = await smart_filter_suggestion_service.generate_smart_suggestions(request)
        return result.dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Smart filter options error: {str(e)}")