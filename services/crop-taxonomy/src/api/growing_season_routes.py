"""
Growing Season Analysis API Routes

FastAPI routes for comprehensive variety growing season analysis,
including phenology modeling, critical growth stage timing, and risk assessment.

TICKET-005_crop-variety-recommendations-8.2 Implementation:
- API endpoints for growing season analysis
- Phenology prediction endpoints
- Critical date calculation endpoints
- Risk assessment endpoints
- Integration with existing crop taxonomy API structure
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import logging
from datetime import date, datetime
import asyncio

try:
    from ..services.variety_growing_season_service import (
        VarietyGrowingSeasonService,
        variety_growing_season_service
    )
    from ..models.growing_season_models import (
        GrowingSeasonAnalysisRequest,
        GrowingSeasonAnalysisResponse,
        PhenologyPredictionRequest,
        PhenologyPredictionResponse,
        GrowingSeasonAnalysis,
        CriticalDatePrediction
    )
    from ..models.crop_variety_models import EnhancedCropVariety
except ImportError:
    from services.variety_growing_season_service import (
        VarietyGrowingSeasonService,
        variety_growing_season_service
    )
    from models.growing_season_models import (
        GrowingSeasonAnalysisRequest,
        GrowingSeasonAnalysisResponse,
        PhenologyPredictionRequest,
        PhenologyPredictionResponse,
        GrowingSeasonAnalysis,
        CriticalDatePrediction
    )
    from models.crop_variety_models import EnhancedCropVariety

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/v1/growing-season",
    tags=["growing-season-analysis"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)


# Dependency injection
async def get_growing_season_service() -> VarietyGrowingSeasonService:
    """Get growing season service instance."""
    return variety_growing_season_service


@router.post("/analyze", response_model=GrowingSeasonAnalysisResponse)
async def analyze_growing_season(
    request: GrowingSeasonAnalysisRequest,
    service: VarietyGrowingSeasonService = Depends(get_growing_season_service)
):
    """
    Perform comprehensive growing season analysis for a variety.
    
    This endpoint provides detailed analysis of growing seasons including:
    - Phenology modeling and critical growth stage timing
    - Season length requirements analysis
    - Temperature sensitivity analysis
    - Photoperiod response analysis
    - Growing season calendars and critical date predictions
    - Risk assessments for growing season challenges
    
    **Agricultural Use Cases:**
    - Variety selection based on growing season compatibility
    - Planting date optimization for specific varieties
    - Risk assessment for crop production planning
    - Management timing recommendations
    - Climate adaptation strategies
    """
    try:
        logger.info(f"Starting growing season analysis for variety {request.variety_id}")
        
        # Validate request
        if not request.variety_id or not request.crop_name:
            raise HTTPException(
                status_code=400,
                detail="variety_id and crop_name are required"
            )
        
        if not request.location or not request.location.get("latitude") or not request.location.get("longitude"):
            raise HTTPException(
                status_code=400,
                detail="Location with latitude and longitude is required"
            )
        
        # Perform analysis
        result = await service.analyze_growing_season(request)
        
        logger.info(f"Growing season analysis completed for variety {request.variety_id}")
        return result
        
    except ValueError as e:
        logger.warning(f"Invalid request for growing season analysis: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in growing season analysis: {e}")
        raise HTTPException(status_code=500, detail="Growing season analysis failed")


@router.post("/phenology/predict", response_model=PhenologyPredictionResponse)
async def predict_phenology(
    request: PhenologyPredictionRequest,
    service: VarietyGrowingSeasonService = Depends(get_growing_season_service)
):
    """
    Predict phenology stages and critical dates for a variety.
    
    This endpoint predicts growth stages and critical dates based on:
    - Variety-specific phenology characteristics
    - Planting date and location
    - Weather data (if provided)
    - Growing degree day calculations
    
    **Agricultural Use Cases:**
    - Planning field operations timing
    - Predicting harvest windows
    - Scheduling irrigation and fertilization
    - Monitoring crop development progress
    """
    try:
        logger.info(f"Predicting phenology for variety {request.variety_id}")
        
        # Validate request
        if not request.variety_id or not request.planting_date or not request.location:
            raise HTTPException(
                status_code=400,
                detail="variety_id, planting_date, and location are required"
            )
        
        # Create analysis request for phenology prediction
        analysis_request = GrowingSeasonAnalysisRequest(
            variety_id=request.variety_id,
            variety_name=None,
            crop_name="",  # Will be determined from variety data
            location=request.location,
            planting_date=request.planting_date,
            analysis_options=request.prediction_options
        )
        
        # Perform analysis
        analysis_result = await service.analyze_growing_season(analysis_request)
        
        # Extract phenology predictions
        critical_dates = analysis_result.analysis.growing_calendar.critical_dates
        predicted_stages = analysis_result.analysis.growing_calendar.growth_stages
        
        # Calculate confidence scores
        confidence_scores = {
            "overall": analysis_result.confidence_score,
            "phenology": 0.8,  # Based on model accuracy
            "weather": 0.7 if request.weather_data else 0.5
        }
        
        response = PhenologyPredictionResponse(
            variety_id=request.variety_id,
            planting_date=request.planting_date,
            predicted_stages=predicted_stages,
            critical_dates=critical_dates,
            confidence_scores=confidence_scores,
            processing_time_ms=analysis_result.processing_time_ms
        )
        
        logger.info(f"Phenology prediction completed for variety {request.variety_id}")
        return response
        
    except ValueError as e:
        logger.warning(f"Invalid request for phenology prediction: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in phenology prediction: {e}")
        raise HTTPException(status_code=500, detail="Phenology prediction failed")


@router.get("/varieties/{variety_id}/calendar")
async def get_growing_calendar(
    variety_id: str,
    crop_name: str = Query(..., description="Crop name"),
    latitude: float = Query(..., ge=-90, le=90, description="Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude"),
    planting_date: Optional[date] = Query(None, description="Planting date (YYYY-MM-DD)"),
    service: VarietyGrowingSeasonService = Depends(get_growing_season_service)
):
    """
    Get growing season calendar for a specific variety and location.
    
    This endpoint generates a comprehensive growing season calendar including:
    - Critical growth stage dates
    - Management windows
    - Risk periods
    - Harvest timing
    - Season summary
    
    **Agricultural Use Cases:**
    - Planning seasonal field operations
    - Scheduling crop management activities
    - Identifying critical timing windows
    - Risk period awareness
    """
    try:
        logger.info(f"Generating calendar for variety {variety_id}")
        
        # Create analysis request
        request = GrowingSeasonAnalysisRequest(
            variety_id=variety_id,
            variety_name=None,
            crop_name=crop_name,
            location={"latitude": latitude, "longitude": longitude},
            planting_date=planting_date
        )
        
        # Perform analysis
        result = await service.analyze_growing_season(request)
        
        # Return calendar data
        calendar_data = {
            "variety_id": variety_id,
            "variety_name": result.analysis.variety_name,
            "crop_name": crop_name,
            "location": {"latitude": latitude, "longitude": longitude},
            "planting_date": result.analysis.growing_calendar.planting_date.isoformat(),
            "critical_dates": [
                {
                    "date_type": cd.date_type,
                    "predicted_date": cd.predicted_date.isoformat(),
                    "confidence_level": cd.confidence_level,
                    "management_recommendations": cd.management_recommendations
                }
                for cd in result.analysis.growing_calendar.critical_dates
            ],
            "growth_stages": result.analysis.growing_calendar.growth_stages,
            "management_windows": result.analysis.growing_calendar.management_windows,
            "risk_periods": result.analysis.growing_calendar.risk_periods,
            "harvest_window": result.analysis.growing_calendar.harvest_window,
            "season_summary": result.analysis.growing_calendar.season_summary,
            "confidence_score": result.confidence_score,
            "processing_time_ms": result.processing_time_ms
        }
        
        logger.info(f"Calendar generated for variety {variety_id}")
        return calendar_data
        
    except ValueError as e:
        logger.warning(f"Invalid request for calendar generation: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating calendar: {e}")
        raise HTTPException(status_code=500, detail="Calendar generation failed")


@router.get("/varieties/{variety_id}/risk-assessment")
async def get_risk_assessment(
    variety_id: str,
    crop_name: str = Query(..., description="Crop name"),
    latitude: float = Query(..., ge=-90, le=90, description="Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude"),
    service: VarietyGrowingSeasonService = Depends(get_growing_season_service)
):
    """
    Get risk assessment for growing a variety at a specific location.
    
    This endpoint provides comprehensive risk assessment including:
    - Overall risk level and score
    - Identified risks and their probabilities
    - Mitigation strategies
    - Contingency plans
    - Monitoring recommendations
    
    **Agricultural Use Cases:**
    - Risk-based variety selection
    - Production planning and insurance
    - Risk mitigation planning
    - Decision support for crop management
    """
    try:
        logger.info(f"Assessing risks for variety {variety_id}")
        
        # Create analysis request
        request = GrowingSeasonAnalysisRequest(
            variety_id=variety_id,
            variety_name=None,
            crop_name=crop_name,
            location={"latitude": latitude, "longitude": longitude}
        )
        
        # Perform analysis
        result = await service.analyze_growing_season(request)
        
        # Return risk assessment data
        risk_data = {
            "variety_id": variety_id,
            "variety_name": result.analysis.variety_name,
            "crop_name": crop_name,
            "location": {"latitude": latitude, "longitude": longitude},
            "overall_risk_level": result.analysis.risk_assessment.overall_risk_level.value,
            "risk_score": result.analysis.risk_assessment.risk_score,
            "identified_risks": result.analysis.risk_assessment.identified_risks,
            "mitigation_strategies": result.analysis.risk_assessment.mitigation_strategies,
            "contingency_plans": result.analysis.risk_assessment.contingency_plans,
            "monitoring_recommendations": result.analysis.risk_assessment.monitoring_recommendations,
            "suitability_score": result.analysis.suitability_score,
            "success_probability": result.analysis.success_probability,
            "warnings": result.analysis.warnings,
            "confidence_score": result.confidence_score,
            "processing_time_ms": result.processing_time_ms
        }
        
        logger.info(f"Risk assessment completed for variety {variety_id}")
        return risk_data
        
    except ValueError as e:
        logger.warning(f"Invalid request for risk assessment: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in risk assessment: {e}")
        raise HTTPException(status_code=500, detail="Risk assessment failed")


@router.get("/varieties/{variety_id}/season-length")
async def get_season_length_analysis(
    variety_id: str,
    crop_name: str = Query(..., description="Crop name"),
    latitude: float = Query(..., ge=-90, le=90, description="Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude"),
    service: VarietyGrowingSeasonService = Depends(get_growing_season_service)
):
    """
    Get season length analysis for a variety at a specific location.
    
    This endpoint analyzes season length requirements including:
    - Minimum and optimal season length requirements
    - Frost-free period analysis
    - Heat unit requirements
    - Season length sufficiency assessment
    - Risk factors identification
    
    **Agricultural Use Cases:**
    - Variety selection based on season length
    - Planting date optimization
    - Climate adaptation planning
    - Risk assessment for short seasons
    """
    try:
        logger.info(f"Analyzing season length for variety {variety_id}")
        
        # Create analysis request
        request = GrowingSeasonAnalysisRequest(
            variety_id=variety_id,
            variety_name=None,
            crop_name=crop_name,
            location={"latitude": latitude, "longitude": longitude}
        )
        
        # Perform analysis
        result = await service.analyze_growing_season(request)
        
        # Return season length analysis data
        season_data = {
            "variety_id": variety_id,
            "variety_name": result.analysis.variety_name,
            "crop_name": crop_name,
            "location": {"latitude": latitude, "longitude": longitude},
            "minimum_season_length_days": result.analysis.season_length_analysis.minimum_season_length_days,
            "optimal_season_length_days": result.analysis.season_length_analysis.optimal_season_length_days,
            "frost_free_period_required_days": result.analysis.season_length_analysis.frost_free_period_required_days,
            "heat_unit_requirement": result.analysis.season_length_analysis.heat_unit_requirement,
            "season_length_sufficiency": result.analysis.season_length_analysis.season_length_sufficiency,
            "risk_factors": result.analysis.season_length_analysis.risk_factors,
            "total_gdd_requirement": result.analysis.phenology_profile.total_gdd_requirement,
            "days_to_maturity": result.analysis.phenology_profile.days_to_maturity,
            "confidence_score": result.confidence_score,
            "processing_time_ms": result.processing_time_ms
        }
        
        logger.info(f"Season length analysis completed for variety {variety_id}")
        return season_data
        
    except ValueError as e:
        logger.warning(f"Invalid request for season length analysis: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in season length analysis: {e}")
        raise HTTPException(status_code=500, detail="Season length analysis failed")


@router.get("/varieties/{variety_id}/temperature-analysis")
async def get_temperature_analysis(
    variety_id: str,
    crop_name: str = Query(..., description="Crop name"),
    latitude: float = Query(..., ge=-90, le=90, description="Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude"),
    service: VarietyGrowingSeasonService = Depends(get_growing_season_service)
):
    """
    Get temperature sensitivity analysis for a variety at a specific location.
    
    This endpoint analyzes temperature sensitivity including:
    - Optimal temperature ranges
    - Minimum and maximum growth temperatures
    - Heat and cold stress thresholds
    - Temperature adaptation score
    - Stress tolerance characteristics
    
    **Agricultural Use Cases:**
    - Temperature-based variety selection
    - Climate adaptation strategies
    - Stress management planning
    - Microclimate considerations
    """
    try:
        logger.info(f"Analyzing temperature sensitivity for variety {variety_id}")
        
        # Create analysis request
        request = GrowingSeasonAnalysisRequest(
            variety_id=variety_id,
            variety_name=None,
            crop_name=crop_name,
            location={"latitude": latitude, "longitude": longitude}
        )
        
        # Perform analysis
        result = await service.analyze_growing_season(request)
        
        # Return temperature analysis data
        temp_data = {
            "variety_id": variety_id,
            "variety_name": result.analysis.variety_name,
            "crop_name": crop_name,
            "location": {"latitude": latitude, "longitude": longitude},
            "optimal_temperature_range_c": result.analysis.temperature_analysis.optimal_temperature_range_c,
            "minimum_growth_temperature_c": result.analysis.temperature_analysis.minimum_growth_temperature_c,
            "maximum_growth_temperature_c": result.analysis.temperature_analysis.maximum_growth_temperature_c,
            "heat_stress_threshold_c": result.analysis.temperature_analysis.heat_stress_threshold_c,
            "cold_stress_threshold_c": result.analysis.temperature_analysis.cold_stress_threshold_c,
            "temperature_adaptation_score": result.analysis.temperature_analysis.temperature_adaptation_score,
            "stress_tolerance_notes": result.analysis.temperature_analysis.stress_tolerance_notes,
            "temperature_sensitivity": result.analysis.phenology_profile.temperature_sensitivity.value,
            "confidence_score": result.confidence_score,
            "processing_time_ms": result.processing_time_ms
        }
        
        logger.info(f"Temperature analysis completed for variety {variety_id}")
        return temp_data
        
    except ValueError as e:
        logger.warning(f"Invalid request for temperature analysis: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in temperature analysis: {e}")
        raise HTTPException(status_code=500, detail="Temperature analysis failed")


@router.get("/varieties/{variety_id}/photoperiod-analysis")
async def get_photoperiod_analysis(
    variety_id: str,
    crop_name: str = Query(..., description="Crop name"),
    latitude: float = Query(..., ge=-90, le=90, description="Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude"),
    service: VarietyGrowingSeasonService = Depends(get_growing_season_service)
):
    """
    Get photoperiod response analysis for a variety at a specific location.
    
    This endpoint analyzes photoperiod response including:
    - Photoperiod response type (short day, long day, day neutral)
    - Day length sensitivity
    - Optimal latitude range
    - Flowering response characteristics
    - Adaptation considerations
    
    **Agricultural Use Cases:**
    - Photoperiod-based variety selection
    - Latitude adaptation planning
    - Flowering timing predictions
    - Regional variety recommendations
    """
    try:
        logger.info(f"Analyzing photoperiod response for variety {variety_id}")
        
        # Create analysis request
        request = GrowingSeasonAnalysisRequest(
            variety_id=variety_id,
            variety_name=None,
            crop_name=crop_name,
            location={"latitude": latitude, "longitude": longitude}
        )
        
        # Perform analysis
        result = await service.analyze_growing_season(request)
        
        # Return photoperiod analysis data
        photoperiod_data = {
            "variety_id": variety_id,
            "variety_name": result.analysis.variety_name,
            "crop_name": crop_name,
            "location": {"latitude": latitude, "longitude": longitude},
            "photoperiod_response_type": result.analysis.photoperiod_analysis.photoperiod_response_type.value,
            "day_length_sensitivity": result.analysis.photoperiod_analysis.day_length_sensitivity,
            "adaptation_latitude_range": result.analysis.photoperiod_analysis.adaptation_latitude_range,
            "photoperiod_notes": result.analysis.photoperiod_analysis.photoperiod_notes,
            "max_day_length_hours": result.analysis.photoperiod_analysis.adaptation_latitude_range[1] if result.analysis.photoperiod_analysis.adaptation_latitude_range else None,
            "min_day_length_hours": result.analysis.photoperiod_analysis.adaptation_latitude_range[0] if result.analysis.photoperiod_analysis.adaptation_latitude_range else None,
            "confidence_score": result.confidence_score,
            "processing_time_ms": result.processing_time_ms
        }
        
        logger.info(f"Photoperiod analysis completed for variety {variety_id}")
        return photoperiod_data
        
    except ValueError as e:
        logger.warning(f"Invalid request for photoperiod analysis: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in photoperiod analysis: {e}")
        raise HTTPException(status_code=500, detail="Photoperiod analysis failed")


@router.get("/health")
async def health_check():
    """Health check endpoint for growing season service."""
    return {
        "status": "healthy",
        "service": "growing-season-analysis",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@router.get("/crops/{crop_name}/phenology-data")
async def get_crop_phenology_data(
    crop_name: str,
    service: VarietyGrowingSeasonService = Depends(get_growing_season_service)
):
    """
    Get phenology data for a specific crop.
    
    This endpoint provides phenology information including:
    - Growth stages and their characteristics
    - GDD requirements
    - Temperature sensitivity
    - Photoperiod response
    
    **Agricultural Use Cases:**
    - Understanding crop phenology characteristics
    - Planning crop management activities
    - Educational and reference purposes
    """
    try:
        logger.info(f"Retrieving phenology data for crop {crop_name}")
        
        # Get phenology data from service
        phenology_data = service.phenology_database.get(crop_name.lower())
        
        if not phenology_data:
            raise HTTPException(
                status_code=404,
                detail=f"No phenology data available for crop: {crop_name}"
            )
        
        # Return phenology data
        return {
            "crop_name": crop_name,
            "phenology_data": phenology_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving phenology data: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve phenology data")


@router.get("/varieties/{variety_id}/summary")
async def get_variety_summary(
    variety_id: str,
    crop_name: str = Query(..., description="Crop name"),
    latitude: float = Query(..., ge=-90, le=90, description="Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude"),
    service: VarietyGrowingSeasonService = Depends(get_growing_season_service)
):
    """
    Get comprehensive summary for a variety at a specific location.
    
    This endpoint provides a summary of all growing season analyses including:
    - Overall suitability score
    - Key recommendations
    - Warnings and risks
    - Success probability
    - Quick reference data
    
    **Agricultural Use Cases:**
    - Quick variety assessment
    - Decision support summaries
    - Comparative analysis preparation
    - Risk overview
    """
    try:
        logger.info(f"Generating summary for variety {variety_id}")
        
        # Create analysis request
        request = GrowingSeasonAnalysisRequest(
            variety_id=variety_id,
            variety_name=None,
            crop_name=crop_name,
            location={"latitude": latitude, "longitude": longitude}
        )
        
        # Perform analysis
        result = await service.analyze_growing_season(request)
        
        # Return summary data
        summary_data = {
            "variety_id": variety_id,
            "variety_name": result.analysis.variety_name,
            "crop_name": crop_name,
            "location": {"latitude": latitude, "longitude": longitude},
            "suitability_score": result.analysis.suitability_score,
            "success_probability": result.analysis.success_probability,
            "overall_risk_level": result.analysis.risk_assessment.overall_risk_level.value,
            "risk_score": result.analysis.risk_assessment.risk_score,
            "key_recommendations": result.analysis.key_recommendations,
            "warnings": result.analysis.warnings,
            "season_length_sufficiency": result.analysis.season_length_analysis.season_length_sufficiency,
            "temperature_adaptation_score": result.analysis.temperature_analysis.temperature_adaptation_score,
            "photoperiod_response": result.analysis.photoperiod_analysis.photoperiod_response_type.value,
            "total_gdd_requirement": result.analysis.phenology_profile.total_gdd_requirement,
            "days_to_maturity": result.analysis.phenology_profile.days_to_maturity,
            "confidence_score": result.confidence_score,
            "processing_time_ms": result.processing_time_ms,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Summary generated for variety {variety_id}")
        return summary_data
        
    except ValueError as e:
        logger.warning(f"Invalid request for variety summary: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating variety summary: {e}")
        raise HTTPException(status_code=500, detail="Summary generation failed")