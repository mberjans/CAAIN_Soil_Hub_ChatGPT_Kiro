"""
API Routes for Timing-Based Variety Filtering

Provides endpoints for sophisticated timing-based variety filtering,
including season length compatibility, planting window flexibility,
harvest timing optimization, and succession planting coordination.
"""

from fastapi import APIRouter, HTTPException, Query, Depends, Body
from typing import List, Optional, Dict, Any
from datetime import date
import logging

from models.crop_variety_models import EnhancedCropVariety
from services.timing_based_variety_filter import (
    TimingBasedVarietyFilter, 
    TimingFilterCriteria, 
    TimingCompatibilityScore,
    SeasonLengthCompatibility,
    PlantingWindowFlexibility,
    LocationData
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/timing-filter", tags=["timing-filter"])


# Dependency injection
async def get_timing_filter_service() -> TimingBasedVarietyFilter:
    """Get timing-based variety filter service instance."""
    return TimingBasedVarietyFilter()


@router.post("/filter-by-timing", response_model=List[TimingCompatibilityScore])
async def filter_varieties_by_timing(
    crop_name: str = Body(..., description="Name of the crop to filter"),
    location: LocationData = Body(..., description="Geographic location data"),
    timing_criteria: TimingFilterCriteria = Body(..., description="Timing-based filtering criteria"),
    variety_ids: Optional[List[str]] = Body(None, description="Specific variety IDs to evaluate (optional)"),
    min_compatibility_score: float = Body(0.5, ge=0.0, le=1.0, description="Minimum compatibility score threshold"),
    max_results: int = Body(50, ge=1, le=200, description="Maximum number of results to return"),
    service: TimingBasedVarietyFilter = Depends(get_timing_filter_service)
):
    """
    Filter crop varieties based on sophisticated timing criteria.
    
    **Timing Filter Features:**
    - **Season Length Compatibility**: Evaluates if variety fits within available growing season
    - **Planting Window Flexibility**: Assesses planting timing flexibility and farmer requirements
    - **Harvest Timing Optimization**: Optimizes harvest timing for market and weather constraints
    - **Succession Planting Coordination**: Evaluates suitability for multiple plantings per season
    - **Growing Degree Day Compatibility**: Matches variety GDD requirements with location conditions
    - **Photoperiod Response Analysis**: Considers day length requirements and sensitivity
    
    **Request Body Schema:**
    ```json
    {
      "crop_name": "corn",
      "location": {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "climate_zone": "6a",
        "elevation_meters": 10
      },
      "timing_criteria": {
        "available_growing_days": 150,
        "min_growing_days_required": 120,
        "preferred_planting_start": "2024-04-15",
        "preferred_planting_end": "2024-05-15",
        "planting_window_flexibility": "moderate",
        "preferred_harvest_start": "2024-09-01",
        "preferred_harvest_end": "2024-10-15",
        "harvest_timing_constraints": ["before_frost", "market_timing"],
        "succession_planting_needed": false,
        "target_growing_degree_days": 2500,
        "gdd_tolerance_percent": 10.0,
        "photoperiod_sensitive": false
      },
      "variety_ids": ["uuid1", "uuid2"],
      "min_compatibility_score": 0.7,
      "max_results": 25
    }
    ```
    
    **Response Features:**
    - Comprehensive timing compatibility scores for each variety
    - Detailed analysis of season length, planting window, and harvest timing
    - Risk factors and optimization suggestions
    - Timing-specific recommendations for each variety
    
    **Use Cases:**
    - **Season Length Planning**: Find varieties that fit within available growing season
    - **Planting Window Optimization**: Match variety flexibility with farmer's timing constraints
    - **Harvest Timing Coordination**: Optimize harvest timing for market and weather conditions
    - **Succession Planting Planning**: Identify varieties suitable for multiple plantings
    - **Climate Adaptation**: Match variety requirements with local growing conditions
    
    Returns ranked list of varieties with timing compatibility scores and detailed analysis.
    """
    try:
        # Get varieties to evaluate
        if variety_ids:
            # Get specific varieties by ID
            varieties = await _get_varieties_by_ids(variety_ids, service)
        else:
            # Get all varieties for the crop
            varieties = await _get_varieties_for_crop(crop_name, service)
        
        if not varieties:
            raise HTTPException(
                status_code=404, 
                detail=f"No varieties found for crop: {crop_name}"
            )
        
        # Filter varieties by timing criteria
        compatibility_scores = await service.filter_varieties_by_timing(
            varieties, timing_criteria, location, crop_name
        )
        
        # Apply minimum compatibility score filter
        filtered_scores = [
            score for score in compatibility_scores 
            if score.overall_score >= min_compatibility_score
        ]
        
        # Limit results
        filtered_scores = filtered_scores[:max_results]
        
        logger.info(f"Timing filter returned {len(filtered_scores)} compatible varieties for {crop_name}")
        return filtered_scores
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in timing-based variety filtering: {e}")
        raise HTTPException(status_code=500, detail=f"Timing filter error: {str(e)}")


@router.post("/season-length-compatibility", response_model=Dict[str, Any])
async def analyze_season_length_compatibility(
    crop_name: str = Body(..., description="Name of the crop"),
    location: LocationData = Body(..., description="Geographic location data"),
    available_growing_days: int = Body(..., ge=1, description="Available growing days"),
    variety_ids: Optional[List[str]] = Body(None, description="Specific variety IDs to analyze"),
    service: TimingBasedVarietyFilter = Depends(get_timing_filter_service)
):
    """
    Analyze season length compatibility for crop varieties.
    
    **Season Length Analysis Features:**
    - **Maturity Assessment**: Evaluates variety maturity requirements against available season
    - **Buffer Calculation**: Determines safety buffer for weather delays and management flexibility
    - **Risk Assessment**: Identifies varieties with tight timing constraints
    - **Optimization Suggestions**: Recommends timing adjustments for better fit
    
    **Analysis Components:**
    - Variety maturity days vs. available growing season
    - Safety buffer calculations for weather delays
    - Risk factors for tight timing scenarios
    - Recommendations for timing optimization
    
    Returns detailed season length compatibility analysis for each variety.
    """
    try:
        # Create timing criteria focused on season length
        timing_criteria = TimingFilterCriteria(
            available_growing_days=available_growing_days,
            min_growing_days_required=available_growing_days * 0.8  # 80% of available season
        )
        
        # Get varieties to analyze
        if variety_ids:
            varieties = await _get_varieties_by_ids(variety_ids, service)
        else:
            varieties = await _get_varieties_for_crop(crop_name, service)
        
        if not varieties:
            raise HTTPException(
                status_code=404, 
                detail=f"No varieties found for crop: {crop_name}"
            )
        
        # Analyze season length compatibility
        compatibility_scores = await service.filter_varieties_by_timing(
            varieties, timing_criteria, location, crop_name
        )
        
        # Extract season length analysis
        season_analysis = {
            "available_growing_days": available_growing_days,
            "variety_analyses": [],
            "summary": {
                "total_varieties_analyzed": len(varieties),
                "excellent_fit_count": 0,
                "good_fit_count": 0,
                "marginal_fit_count": 0,
                "poor_fit_count": 0,
                "incompatible_count": 0
            }
        }
        
        for score in compatibility_scores:
            variety_analysis = {
                "variety_id": score.variety_id,
                "variety_name": score.variety_name,
                "season_length_score": score.season_length_score,
                "compatibility_level": score.compatibility_level,
                "season_length_analysis": score.season_length_analysis,
                "timing_recommendations": score.timing_recommendations,
                "risk_factors": score.risk_factors
            }
            season_analysis["variety_analyses"].append(variety_analysis)
            
            # Update summary counts
            if score.compatibility_level == SeasonLengthCompatibility.EXCELLENT:
                season_analysis["summary"]["excellent_fit_count"] += 1
            elif score.compatibility_level == SeasonLengthCompatibility.GOOD:
                season_analysis["summary"]["good_fit_count"] += 1
            elif score.compatibility_level == SeasonLengthCompatibility.MARGINAL:
                season_analysis["summary"]["marginal_fit_count"] += 1
            elif score.compatibility_level == SeasonLengthCompatibility.POOR:
                season_analysis["summary"]["poor_fit_count"] += 1
            else:
                season_analysis["summary"]["incompatible_count"] += 1
        
        return season_analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in season length compatibility analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Season length analysis error: {str(e)}")


@router.post("/planting-window-analysis", response_model=Dict[str, Any])
async def analyze_planting_window_compatibility(
    crop_name: str = Body(..., description="Name of the crop"),
    location: LocationData = Body(..., description="Geographic location data"),
    farmer_flexibility: PlantingWindowFlexibility = Body(..., description="Farmer's planting window flexibility requirements"),
    variety_ids: Optional[List[str]] = Body(None, description="Specific variety IDs to analyze"),
    service: TimingBasedVarietyFilter = Depends(get_timing_filter_service)
):
    """
    Analyze planting window compatibility for crop varieties.
    
    **Planting Window Analysis Features:**
    - **Flexibility Assessment**: Evaluates variety planting window flexibility
    - **Farmer Requirements Matching**: Matches variety flexibility with farmer constraints
    - **Timing Optimization**: Identifies optimal planting timing strategies
    - **Risk Management**: Assesses risks associated with narrow planting windows
    
    **Flexibility Levels:**
    - **Very Flexible**: 4+ weeks planting window
    - **Flexible**: 2-4 weeks planting window
    - **Moderate**: 1-2 weeks planting window
    - **Narrow**: <1 week planting window
    - **Critical**: Very narrow window requiring precise timing
    
    Returns detailed planting window compatibility analysis for each variety.
    """
    try:
        # Create timing criteria focused on planting window
        timing_criteria = TimingFilterCriteria(
            available_growing_days=150,  # Default value
            planting_window_flexibility=farmer_flexibility
        )
        
        # Get varieties to analyze
        if variety_ids:
            varieties = await _get_varieties_by_ids(variety_ids, service)
        else:
            varieties = await _get_varieties_for_crop(crop_name, service)
        
        if not varieties:
            raise HTTPException(
                status_code=404, 
                detail=f"No varieties found for crop: {crop_name}"
            )
        
        # Analyze planting window compatibility
        compatibility_scores = await service.filter_varieties_by_timing(
            varieties, timing_criteria, location, crop_name
        )
        
        # Extract planting window analysis
        planting_analysis = {
            "farmer_flexibility_requirement": farmer_flexibility,
            "variety_analyses": [],
            "summary": {
                "total_varieties_analyzed": len(varieties),
                "very_flexible_count": 0,
                "flexible_count": 0,
                "moderate_count": 0,
                "narrow_count": 0,
                "critical_count": 0
            }
        }
        
        for score in compatibility_scores:
            variety_analysis = {
                "variety_id": score.variety_id,
                "variety_name": score.variety_name,
                "planting_window_score": score.planting_window_score,
                "planting_window_analysis": score.planting_window_analysis,
                "timing_recommendations": score.timing_recommendations,
                "risk_factors": score.risk_factors
            }
            planting_analysis["variety_analyses"].append(variety_analysis)
        
        return planting_analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in planting window compatibility analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Planting window analysis error: {str(e)}")


@router.post("/harvest-timing-optimization", response_model=Dict[str, Any])
async def optimize_harvest_timing(
    crop_name: str = Body(..., description="Name of the crop"),
    location: LocationData = Body(..., description="Geographic location data"),
    harvest_constraints: List[str] = Body(..., description="Harvest timing constraints (e.g., 'before_frost', 'market_timing')"),
    preferred_harvest_start: Optional[date] = Body(None, description="Preferred harvest start date"),
    preferred_harvest_end: Optional[date] = Body(None, description="Preferred harvest end date"),
    variety_ids: Optional[List[str]] = Body(None, description="Specific variety IDs to analyze"),
    service: TimingBasedVarietyFilter = Depends(get_timing_filter_service)
):
    """
    Optimize harvest timing for crop varieties.
    
    **Harvest Timing Optimization Features:**
    - **Constraint Analysis**: Evaluates harvest timing against farmer constraints
    - **Market Coordination**: Optimizes harvest timing for market conditions
    - **Weather Risk Assessment**: Considers frost and weather risks
    - **Timing Flexibility**: Identifies varieties with flexible harvest windows
    
    **Harvest Constraints:**
    - **before_frost**: Harvest must complete before first frost
    - **market_timing**: Harvest timing optimized for market conditions
    - **equipment_availability**: Harvest timing constrained by equipment availability
    - **labor_availability**: Harvest timing constrained by labor availability
    - **storage_capacity**: Harvest timing optimized for storage capacity
    
    Returns detailed harvest timing optimization analysis for each variety.
    """
    try:
        # Create timing criteria focused on harvest timing
        timing_criteria = TimingFilterCriteria(
            available_growing_days=150,  # Default value
            preferred_harvest_start=preferred_harvest_start,
            preferred_harvest_end=preferred_harvest_end,
            harvest_timing_constraints=harvest_constraints
        )
        
        # Get varieties to analyze
        if variety_ids:
            varieties = await _get_varieties_by_ids(variety_ids, service)
        else:
            varieties = await _get_varieties_for_crop(crop_name, service)
        
        if not varieties:
            raise HTTPException(
                status_code=404, 
                detail=f"No varieties found for crop: {crop_name}"
            )
        
        # Analyze harvest timing optimization
        compatibility_scores = await service.filter_varieties_by_timing(
            varieties, timing_criteria, location, crop_name
        )
        
        # Extract harvest timing analysis
        harvest_analysis = {
            "harvest_constraints": harvest_constraints,
            "preferred_harvest_start": preferred_harvest_start,
            "preferred_harvest_end": preferred_harvest_end,
            "variety_analyses": [],
            "summary": {
                "total_varieties_analyzed": len(varieties),
                "constraints_met_count": 0,
                "constraints_failed_count": 0
            }
        }
        
        for score in compatibility_scores:
            variety_analysis = {
                "variety_id": score.variety_id,
                "variety_name": score.variety_name,
                "harvest_timing_score": score.harvest_timing_score,
                "harvest_timing_analysis": score.harvest_timing_analysis,
                "timing_recommendations": score.timing_recommendations,
                "risk_factors": score.risk_factors
            }
            harvest_analysis["variety_analyses"].append(variety_analysis)
            
            # Update summary counts
            constraints_met = len(score.harvest_timing_analysis.get("constraints_met", []))
            constraints_failed = len(score.harvest_timing_analysis.get("constraints_failed", []))
            
            if constraints_met > constraints_failed:
                harvest_analysis["summary"]["constraints_met_count"] += 1
            else:
                harvest_analysis["summary"]["constraints_failed_count"] += 1
        
        return harvest_analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in harvest timing optimization: {e}")
        raise HTTPException(status_code=500, detail=f"Harvest timing optimization error: {str(e)}")


@router.post("/succession-planting-analysis", response_model=Dict[str, Any])
async def analyze_succession_planting_compatibility(
    crop_name: str = Body(..., description="Name of the crop"),
    location: LocationData = Body(..., description="Geographic location data"),
    succession_interval_days: int = Body(..., ge=1, description="Days between succession plantings"),
    multiple_plantings_per_season: bool = Body(False, description="Whether multiple plantings per season are planned"),
    variety_ids: Optional[List[str]] = Body(None, description="Specific variety IDs to analyze"),
    service: TimingBasedVarietyFilter = Depends(get_timing_filter_service)
):
    """
    Analyze succession planting compatibility for crop varieties.
    
    **Succession Planting Analysis Features:**
    - **Maturity Assessment**: Evaluates variety maturity for succession planting
    - **Interval Compatibility**: Assesses fit within succession planting intervals
    - **Multiple Planting Suitability**: Identifies varieties suitable for multiple plantings
    - **Timing Coordination**: Optimizes timing for succession planting scenarios
    
    **Succession Planting Benefits:**
    - Extended harvest season
    - Risk mitigation through staggered planting
    - Market timing optimization
    - Labor and equipment efficiency
    
    Returns detailed succession planting compatibility analysis for each variety.
    """
    try:
        # Create timing criteria focused on succession planting
        timing_criteria = TimingFilterCriteria(
            available_growing_days=150,  # Default value
            succession_planting_needed=True,
            succession_interval_days=succession_interval_days,
            multiple_plantings_per_season=multiple_plantings_per_season
        )
        
        # Get varieties to analyze
        if variety_ids:
            varieties = await _get_varieties_by_ids(variety_ids, service)
        else:
            varieties = await _get_varieties_for_crop(crop_name, service)
        
        if not varieties:
            raise HTTPException(
                status_code=404, 
                detail=f"No varieties found for crop: {crop_name}"
            )
        
        # Analyze succession planting compatibility
        compatibility_scores = await service.filter_varieties_by_timing(
            varieties, timing_criteria, location, crop_name
        )
        
        # Extract succession planting analysis
        succession_analysis = {
            "succession_interval_days": succession_interval_days,
            "multiple_plantings_per_season": multiple_plantings_per_season,
            "variety_analyses": [],
            "summary": {
                "total_varieties_analyzed": len(varieties),
                "excellent_succession_fit_count": 0,
                "good_succession_fit_count": 0,
                "moderate_succession_fit_count": 0,
                "poor_succession_fit_count": 0
            }
        }
        
        for score in compatibility_scores:
            if score.succession_analysis:
                variety_analysis = {
                    "variety_id": score.variety_id,
                    "variety_name": score.variety_name,
                    "succession_score": score.succession_score,
                    "succession_analysis": score.succession_analysis,
                    "timing_recommendations": score.timing_recommendations,
                    "optimization_suggestions": score.optimization_suggestions
                }
                succession_analysis["variety_analyses"].append(variety_analysis)
                
                # Update summary counts based on succession compatibility
                compatibility = score.succession_analysis.get("compatibility", "")
                if "excellent" in compatibility:
                    succession_analysis["summary"]["excellent_succession_fit_count"] += 1
                elif "good" in compatibility:
                    succession_analysis["summary"]["good_succession_fit_count"] += 1
                elif "moderate" in compatibility:
                    succession_analysis["summary"]["moderate_succession_fit_count"] += 1
                else:
                    succession_analysis["summary"]["poor_succession_fit_count"] += 1
        
        return succession_analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in succession planting compatibility analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Succession planting analysis error: {str(e)}")


@router.get("/timing-filter-types", response_model=List[Dict[str, str]])
async def get_timing_filter_types():
    """
    Get available timing filter types and their descriptions.
    
    Returns list of timing filter types with descriptions for use in filtering criteria.
    """
    return [
        {
            "type": "season_length",
            "name": "Season Length Compatibility",
            "description": "Evaluates if variety fits within available growing season"
        },
        {
            "type": "planting_window",
            "name": "Planting Window Flexibility",
            "description": "Assesses planting timing flexibility and farmer requirements"
        },
        {
            "type": "harvest_timing",
            "name": "Harvest Timing Optimization",
            "description": "Optimizes harvest timing for market and weather constraints"
        },
        {
            "type": "succession_planting",
            "name": "Succession Planting Coordination",
            "description": "Evaluates suitability for multiple plantings per season"
        },
        {
            "type": "growing_degree_days",
            "name": "Growing Degree Day Compatibility",
            "description": "Matches variety GDD requirements with location conditions"
        },
        {
            "type": "photoperiod_response",
            "name": "Photoperiod Response Analysis",
            "description": "Considers day length requirements and sensitivity"
        }
    ]


@router.get("/planting-flexibility-levels", response_model=List[Dict[str, str]])
async def get_planting_flexibility_levels():
    """
    Get available planting window flexibility levels and their descriptions.
    
    Returns list of planting flexibility levels with descriptions for farmer requirements.
    """
    return [
        {
            "level": "very_flexible",
            "name": "Very Flexible",
            "description": "4+ weeks planting window - maximum flexibility"
        },
        {
            "level": "flexible",
            "name": "Flexible",
            "description": "2-4 weeks planting window - good flexibility"
        },
        {
            "level": "moderate",
            "name": "Moderate",
            "description": "1-2 weeks planting window - moderate flexibility"
        },
        {
            "level": "narrow",
            "name": "Narrow",
            "description": "<1 week planting window - limited flexibility"
        },
        {
            "level": "critical",
            "name": "Critical",
            "description": "Very narrow window requiring precise timing"
        }
    ]


# Helper functions
async def _get_varieties_by_ids(variety_ids: List[str], service: TimingBasedVarietyFilter) -> List[EnhancedCropVariety]:
    """Get varieties by their IDs."""
    # This would integrate with the database service
    # For now, return empty list
    return []


async def _get_varieties_for_crop(crop_name: str, service: TimingBasedVarietyFilter) -> List[EnhancedCropVariety]:
    """Get all varieties for a specific crop."""
    # This would integrate with the database service
    # For now, return empty list
    return []