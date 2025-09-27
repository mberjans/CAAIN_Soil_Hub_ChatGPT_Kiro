"""Filter combination API routes."""

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query

try:
    from ..services.filter_engine import filter_combination_engine
    from ..models.crop_filtering_models import (
        FilterCombinationRequest,
        FilterCombinationResponse,
        FilterSuggestionRequest,
        FilterSuggestionResponse
    )
except ImportError:  # pragma: no cover - fallback for direct execution
    from services.filter_engine import filter_combination_engine  # type: ignore
    from models.crop_filtering_models import (  # type: ignore
        FilterCombinationRequest,
        FilterCombinationResponse,
        FilterSuggestionRequest,
        FilterSuggestionResponse
    )

router = APIRouter(prefix="/crop-taxonomy/filters", tags=["filter-engine"])


@router.post("/combine", response_model=FilterCombinationResponse)
async def combine_filters(request: FilterCombinationRequest) -> FilterCombinationResponse:
    """Combine filter directives and presets into actionable criteria."""
    try:
        result = filter_combination_engine.combine_filters(request)
        return result
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=f"Filter combination error: {str(exc)}")


@router.get("/suggestions", response_model=FilterSuggestionResponse)
async def get_filter_suggestions(
    request_id: str = Query(..., description="Unique request identifier"),
    climate_zone: Optional[str] = Query(None, description="Primary climate zone (e.g., 5b)"),
    latitude: Optional[float] = Query(None, description="Latitude for context-aware suggestions"),
    longitude: Optional[float] = Query(None, description="Longitude for context-aware suggestions"),
    soil_ph: Optional[float] = Query(None, description="Measured soil pH"),
    soil_drainage: Optional[str] = Query(None, description="Soil drainage class"),
    market_goal: Optional[str] = Query(None, description="Primary market goal"),
    sustainability_focus: Optional[str] = Query(None, description="Sustainability priority"),
    focus_areas: Optional[List[str]] = Query(None, description="Focus areas such as organic, drought, profit"),
    max_suggestions: int = Query(5, ge=0, le=20, description="Maximum number of suggestions to return"),
    include_presets: bool = Query(True, description="Include preset recommendations")
) -> FilterSuggestionResponse:
    """Return intelligent filter suggestions based on contextual signals."""
    try:
        context: Dict[str, object] = {}
        soil_profile: Dict[str, object] = {}
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
            index = 0
            while index < len(focus_areas):
                focus_area_values.append(focus_areas[index])
                index += 1

        location_coordinates: Optional[Dict[str, float]] = None
        if latitude is not None and longitude is not None:
            location_coordinates = {'latitude': latitude, 'longitude': longitude}

        suggestion_request = FilterSuggestionRequest(
            request_id=request_id,
            context=context,
            climate_zone=climate_zone,
            location_coordinates=location_coordinates,
            focus_areas=focus_area_values,
            max_suggestions=max_suggestions,
            include_presets=include_presets
        )

        result = filter_combination_engine.suggest_filters(suggestion_request)
        return result
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=f"Filter suggestion error: {str(exc)}")
