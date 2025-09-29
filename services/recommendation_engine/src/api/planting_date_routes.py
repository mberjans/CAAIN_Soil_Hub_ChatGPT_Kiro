"""
Planting Date API Routes

FastAPI routes for planting date calculations and timing recommendations.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date, datetime, timedelta
import logging

try:
    from ..models.agricultural_models import LocationData
    from ..services.planting_date_service import (
        planting_date_service,
        PlantingWindow,
        FrostDateInfo
    )
except ImportError:
    from models.agricultural_models import LocationData
    from services.planting_date_service import (
        planting_date_service, 
        PlantingWindow,
        FrostDateInfo
    )

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/planting", tags=["planting-dates"])


class PlantingDateRequest(BaseModel):
    """Request for planting date calculations."""
    
    crop_name: str = Field(..., description="Name of the crop to plant")
    location: LocationData = Field(..., description="Farm location data")
    planting_season: str = Field(
        default="spring", 
        description="Target planting season"
    )
    
    @validator('planting_season')
    def validate_season(cls, v):
        valid_seasons = {"spring", "summer", "fall", "winter"}
        if v.lower() not in valid_seasons:
            raise ValueError(f"Invalid season. Must be one of: {', '.join(valid_seasons)}")
        return v.lower()


class FrostDateRequest(BaseModel):
    """Request for frost date information."""
    
    location: LocationData = Field(..., description="Location for frost date lookup")


class PlantingWindowRequest(BaseModel):
    """Request for comprehensive planting window analysis."""
    
    crop_name: str = Field(..., description="Name of the crop")
    location: LocationData = Field(..., description="Farm location data")
    succession_planting: bool = Field(
        default=False, 
        description="Include succession planting schedule"
    )
    max_plantings: int = Field(
        default=5, 
        ge=1, 
        le=10, 
        description="Maximum succession plantings"
    )


class SuccessionPlantingRequest(BaseModel):
    """Request for succession planting schedule."""
    
    crop_name: str = Field(..., description="Name of the crop")
    location: LocationData = Field(..., description="Farm location")
    start_date: date = Field(..., description="First planting date")
    end_date: date = Field(..., description="Last acceptable planting date")
    max_plantings: int = Field(
        default=5,
        ge=1, 
        le=10,
        description="Maximum number of plantings"
    )
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError("End date must be after start date")
        return v


class PlantingWindowResponse(BaseModel):
    """Response containing planting window information."""
    
    crop_name: str
    optimal_date: date
    earliest_safe_date: date
    latest_safe_date: date
    planting_season: str
    safety_margin_days: int
    confidence_score: float
    frost_considerations: List[str]
    climate_warnings: List[str]
    growing_degree_days_required: Optional[int] = None
    expected_harvest_date: Optional[date] = None


class FrostDateResponse(BaseModel):
    """Response containing frost date information."""
    
    last_frost_date: Optional[date]
    first_frost_date: Optional[date]
    growing_season_length: Optional[int]
    frost_free_days: Optional[int]
    confidence_level: str
    location_summary: str


class ComprehensivePlantingResponse(BaseModel):
    """Response containing comprehensive planting analysis."""
    
    crop_name: str
    location_summary: str
    frost_dates: FrostDateResponse
    planting_windows: List[PlantingWindowResponse]
    succession_schedule: Optional[List[PlantingWindowResponse]] = None
    recommendations: List[str]
    warnings: List[str]


@router.post("/calculate-dates", response_model=PlantingWindowResponse)
async def calculate_planting_dates(request: PlantingDateRequest):
    """
    Calculate optimal planting dates for a specific crop and location.
    
    This endpoint provides:
    - Optimal planting date based on frost dates and crop requirements
    - Safe planting window (earliest to latest dates)  
    - Crop-specific timing considerations
    - Climate zone adjustments
    """
    try:
        logger.info(f"Calculating planting dates for {request.crop_name} at {request.location.latitude}, {request.location.longitude}")
        
        # Calculate planting window
        planting_window = await planting_date_service.calculate_planting_dates(
            crop_name=request.crop_name,
            location=request.location,
            planting_season=request.planting_season
        )
        
        # Convert to response model
        return PlantingWindowResponse(
            crop_name=planting_window.crop_name,
            optimal_date=planting_window.optimal_date,
            earliest_safe_date=planting_window.earliest_safe_date,
            latest_safe_date=planting_window.latest_safe_date,
            planting_season=planting_window.planting_season,
            safety_margin_days=planting_window.safety_margin_days,
            confidence_score=planting_window.confidence_score,
            frost_considerations=planting_window.frost_considerations,
            climate_warnings=planting_window.climate_warnings,
            growing_degree_days_required=planting_window.growing_degree_days_required,
            expected_harvest_date=planting_window.expected_harvest_date
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating planting dates: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating planting dates: {str(e)}"
        )


@router.post("/frost-dates", response_model=FrostDateResponse)
async def get_frost_dates(request: FrostDateRequest):
    """
    Get frost date information for a location.
    
    This endpoint provides:
    - Last spring frost date
    - First fall frost date  
    - Growing season length
    - Confidence level of frost date data
    """
    try:
        logger.info(f"Getting frost dates for {request.location.latitude}, {request.location.longitude}")
        
        # Get frost date info from planting service
        frost_info = await planting_date_service._get_frost_date_info(request.location)
        
        # Create location summary
        location_parts = []
        if request.location.address:
            location_parts.append(request.location.address)
        elif request.location.state and request.location.county:
            location_parts.append(f"{request.location.county}, {request.location.state}")
        else:
            location_parts.append(f"{request.location.latitude:.2f}, {request.location.longitude:.2f}")
        
        if hasattr(request.location, 'climate_zone') and request.location.climate_zone:
            location_parts.append(f"USDA Zone {request.location.climate_zone}")
            
        location_summary = " - ".join(location_parts)
        
        return FrostDateResponse(
            last_frost_date=frost_info.last_frost_date,
            first_frost_date=frost_info.first_frost_date,
            growing_season_length=frost_info.growing_season_length,
            frost_free_days=frost_info.frost_free_days,
            confidence_level=frost_info.confidence_level,
            location_summary=location_summary
        )
        
    except Exception as e:
        logger.error(f"Error getting frost dates: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting frost dates: {str(e)}"
        )


@router.post("/planting-window", response_model=ComprehensivePlantingResponse)
async def get_comprehensive_planting_window(request: PlantingWindowRequest):
    """
    Get comprehensive planting window analysis for a crop.
    
    This endpoint provides:
    - All possible planting seasons (spring, summer, fall)
    - Frost date analysis
    - Succession planting schedules
    - Climate-specific recommendations and warnings
    """
    try:
        logger.info(f"Getting comprehensive planting analysis for {request.crop_name}")
        
        # Get frost date information
        frost_info = await planting_date_service._get_frost_date_info(request.location)
        
        # Get all possible planting windows
        all_windows = await planting_date_service.get_multiple_season_plantings(
            request.crop_name, request.location
        )
        
        # Convert planting windows to response format
        planting_windows = [
            PlantingWindowResponse(
                crop_name=window.crop_name,
                optimal_date=window.optimal_date,
                earliest_safe_date=window.earliest_safe_date,
                latest_safe_date=window.latest_safe_date,
                planting_season=window.planting_season,
                safety_margin_days=window.safety_margin_days,
                confidence_score=window.confidence_score,
                frost_considerations=window.frost_considerations,
                climate_warnings=window.climate_warnings,
                growing_degree_days_required=window.growing_degree_days_required,
                expected_harvest_date=window.expected_harvest_date
            )
            for window in all_windows
        ]
        
        # Generate succession planting schedule if requested
        succession_schedule = None
        if request.succession_planting and all_windows:
            try:
                spring_window = next((w for w in all_windows if w.planting_season == "spring"), None)
                if spring_window:
                    succession_plantings = planting_date_service.get_succession_planting_schedule(
                        crop_name=request.crop_name,
                        location=request.location,
                        start_date=spring_window.optimal_date,
                        end_date=spring_window.latest_safe_date + timedelta(days=60),
                        max_plantings=request.max_plantings
                    )
                    
                    succession_schedule = [
                        PlantingWindowResponse(
                            crop_name=window.crop_name,
                            optimal_date=window.optimal_date,
                            earliest_safe_date=window.earliest_safe_date,
                            latest_safe_date=window.latest_safe_date,
                            planting_season=window.planting_season,
                            safety_margin_days=window.safety_margin_days,
                            confidence_score=window.confidence_score,
                            frost_considerations=window.frost_considerations,
                            climate_warnings=window.climate_warnings,
                            growing_degree_days_required=window.growing_degree_days_required,
                            expected_harvest_date=window.expected_harvest_date
                        )
                        for window in succession_plantings
                    ]
            except Exception as e:
                logger.warning(f"Could not generate succession schedule: {e}")
        
        # Generate recommendations
        recommendations = []
        warnings = []
        
        if planting_windows:
            # Primary season recommendation
            primary_window = planting_windows[0]
            recommendations.append(
                f"Primary planting window: {primary_window.optimal_date.strftime('%B %d')} "
                f"(safe range: {primary_window.earliest_safe_date.strftime('%m/%d')} - "
                f"{primary_window.latest_safe_date.strftime('%m/%d')})"
            )
            
            # Multiple season opportunities
            if len(planting_windows) > 1:
                seasons = [w.planting_season for w in planting_windows]
                recommendations.append(f"Multiple planting opportunities available: {', '.join(seasons)}")
            
            # Succession planting
            if succession_schedule:
                recommendations.append(f"Succession planting possible every 1-2 weeks for continuous harvest")
                
            # Collect warnings from all windows
            for window in planting_windows:
                warnings.extend(window.climate_warnings)
        
        # Create location summary
        location_parts = []
        if request.location.address:
            location_parts.append(request.location.address)
        else:
            if request.location.state and request.location.county:
                location_parts.append(f"{request.location.county}, {request.location.state}")
            location_parts.append(f"{request.location.latitude:.2f}, {request.location.longitude:.2f}")
        
        if hasattr(request.location, 'climate_zone') and request.location.climate_zone:
            location_parts.append(f"USDA Zone {request.location.climate_zone}")
        
        location_summary = " - ".join(location_parts)
        
        # Create frost date response
        frost_response = FrostDateResponse(
            last_frost_date=frost_info.last_frost_date,
            first_frost_date=frost_info.first_frost_date,
            growing_season_length=frost_info.growing_season_length,
            frost_free_days=frost_info.frost_free_days,
            confidence_level=frost_info.confidence_level,
            location_summary=location_summary
        )
        
        return ComprehensivePlantingResponse(
            crop_name=request.crop_name,
            location_summary=location_summary,
            frost_dates=frost_response,
            planting_windows=planting_windows,
            succession_schedule=succession_schedule,
            recommendations=recommendations,
            warnings=list(set(warnings))  # Remove duplicates
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting comprehensive planting window: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting comprehensive planting window: {str(e)}"
        )


@router.post("/succession-schedule", response_model=List[PlantingWindowResponse])
async def get_succession_planting_schedule(request: SuccessionPlantingRequest):
    """
    Get succession planting schedule for continuous harvest.
    
    This endpoint provides:
    - Multiple planting dates spaced at appropriate intervals
    - Expected harvest dates for each planting
    - Optimal timing for continuous production
    """
    try:
        logger.info(f"Getting succession planting schedule for {request.crop_name}")
        
        succession_plantings = planting_date_service.get_succession_planting_schedule(
            crop_name=request.crop_name,
            location=request.location,
            start_date=request.start_date,
            end_date=request.end_date,
            max_plantings=request.max_plantings
        )
        
        return [
            PlantingWindowResponse(
                crop_name=window.crop_name,
                optimal_date=window.optimal_date,
                earliest_safe_date=window.earliest_safe_date,
                latest_safe_date=window.latest_safe_date,
                planting_season=window.planting_season,
                safety_margin_days=window.safety_margin_days,
                confidence_score=window.confidence_score,
                frost_considerations=window.frost_considerations,
                climate_warnings=window.climate_warnings,
                growing_degree_days_required=window.growing_degree_days_required,
                expected_harvest_date=window.expected_harvest_date
            )
            for window in succession_plantings
        ]
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting succession schedule: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting succession schedule: {str(e)}"
        )


@router.get("/available-crops")
async def get_available_crops():
    """
    Get list of crops available for planting date calculations.
    
    Returns:
        List of crop names with basic planting characteristics
    """
    try:
        crops_info = []
        
        for crop_name, profile in planting_date_service.crop_timing_database.items():
            crop_info = {
                "crop_name": crop_name,
                "crop_category": profile.crop_category,
                "frost_tolerance": profile.frost_tolerance,
                "days_to_maturity": profile.days_to_maturity,
                "succession_planting": profile.succession_interval_days is not None,
                "fall_planting": profile.fall_planting_possible,
                "winter_hardy": profile.winter_hardy
            }
            crops_info.append(crop_info)
        
        return {
            "available_crops": crops_info,
            "total_crops": len(crops_info)
        }
        
    except Exception as e:
        logger.error(f"Error getting available crops: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting available crops: {str(e)}"
        )