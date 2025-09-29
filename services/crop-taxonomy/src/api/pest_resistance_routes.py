"""
Pest Resistance Analysis API Routes

FastAPI routes for pest resistance analysis, recommendations, and integrated pest management.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
import logging
from uuid import UUID

from models.pest_resistance_models import (
    PestResistanceRequest,
    PestResistanceResponse,
    PestType,
    PestSeverity,
    PestRiskLevel,
    DataSource
)
from services.pest_resistance_service import PestResistanceAnalysisService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/pest-resistance", tags=["pest-resistance"])

# Service instance
pest_resistance_service = PestResistanceAnalysisService()


@router.post("/analyze", response_model=PestResistanceResponse)
async def analyze_pest_resistance(
    request: PestResistanceRequest,
    background_tasks: BackgroundTasks
):
    """
    Perform comprehensive pest resistance analysis.
    
    This endpoint provides:
    - Regional pest pressure analysis
    - Variety-specific pest resistance evaluation
    - Integrated Pest Management (IPM) recommendations
    - Resistance durability and stacking analysis
    - Timing guidance and management strategies
    - Pest pressure forecasting
    - Historical trend analysis
    
    **Agricultural Use Cases:**
    - Crop variety selection based on pest resistance
    - Pest management strategy development
    - Resistance management planning
    - IPM program implementation
    - Risk assessment and mitigation
    """
    try:
        logger.info(f"Starting pest resistance analysis for crop {request.crop_type}")
        
        # Perform analysis
        response = await pest_resistance_service.analyze_pest_resistance(request)
        
        # Log analysis completion
        logger.info(f"Completed pest resistance analysis: {response.request_id}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in pest resistance analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Pest resistance analysis failed: {str(e)}")


@router.get("/regional-pressure")
async def get_regional_pest_pressure(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude in decimal degrees"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude in decimal degrees"),
    crop_type: str = Query(..., description="Crop type for analysis"),
    radius_km: float = Query(50.0, ge=1.0, le=500.0, description="Analysis radius in kilometers"),
    analysis_period_days: int = Query(30, ge=1, le=365, description="Analysis period in days")
):
    """
    Get regional pest pressure data for a specific location and crop.
    
    **Parameters:**
    - **latitude**: Latitude coordinate (-90 to 90)
    - **longitude**: Longitude coordinate (-180 to 180)
    - **crop_type**: Type of crop (corn, soybean, wheat, etc.)
    - **radius_km**: Analysis radius in kilometers (1-500)
    - **analysis_period_days**: Analysis period in days (1-365)
    
    **Returns:**
    Regional pest pressure data including:
    - Active pest pressures
    - Risk levels and trends
    - Environmental factors
    - Management recommendations
    """
    try:
        # Create request object
        request = PestResistanceRequest(
            coordinates=(latitude, longitude),
            region_radius_km=radius_km,
            crop_type=crop_type,
            analysis_period_days=analysis_period_days,
            include_forecast=True,
            include_historical=True,
            include_management_recommendations=True,
            include_variety_recommendations=False,
            include_timing_guidance=True,
            include_resistance_analysis=False
        )
        
        # Get regional pressure
        response = await pest_resistance_service.analyze_pest_resistance(request)
        
        return {
            "region": response.analysis_region,
            "overall_risk_level": response.overall_risk_level,
            "active_pests": response.active_pests,
            "emerging_threats": response.emerging_threats,
            "data_quality_score": response.data_quality_score,
            "confidence_level": response.confidence_level
        }
        
    except Exception as e:
        logger.error(f"Error getting regional pest pressure: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get regional pest pressure: {str(e)}")


@router.post("/variety-analysis")
async def analyze_variety_pest_resistance(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude in decimal degrees"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude in decimal degrees"),
    crop_type: str = Query(..., description="Crop type for analysis"),
    variety_ids: Optional[List[UUID]] = Query(None, description="Specific varieties to analyze"),
    radius_km: float = Query(50.0, ge=1.0, le=500.0, description="Analysis radius in kilometers")
):
    """
    Analyze pest resistance for specific crop varieties.
    
    **Parameters:**
    - **latitude**: Latitude coordinate (-90 to 90)
    - **longitude**: Longitude coordinate (-180 to 180)
    - **crop_type**: Type of crop (corn, soybean, wheat, etc.)
    - **variety_ids**: Optional list of specific variety IDs to analyze
    - **radius_km**: Analysis radius in kilometers (1-500)
    
    **Returns:**
    Variety-specific pest resistance analysis including:
    - Pest resistance ratings
    - Vulnerability assessments
    - Performance predictions
    - Management requirements
    - Suitability scores
    """
    try:
        # Create request object
        request = PestResistanceRequest(
            coordinates=(latitude, longitude),
            region_radius_km=radius_km,
            crop_type=crop_type,
            variety_ids=variety_ids,
            include_forecast=False,
            include_historical=False,
            include_management_recommendations=False,
            include_variety_recommendations=True,
            include_timing_guidance=False,
            include_resistance_analysis=True
        )
        
        # Perform analysis
        response = await pest_resistance_service.analyze_pest_resistance(request)
        
        return {
            "variety_analysis": response.variety_analysis,
            "recommended_varieties": response.recommended_varieties,
            "resistance_analysis": response.resistance_analysis,
            "data_quality_score": response.data_quality_score,
            "confidence_level": response.confidence_level
        }
        
    except Exception as e:
        logger.error(f"Error analyzing variety pest resistance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze variety pest resistance: {str(e)}")


@router.post("/management-recommendations")
async def get_pest_management_recommendations(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude in decimal degrees"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude in decimal degrees"),
    crop_type: str = Query(..., description="Crop type for analysis"),
    radius_km: float = Query(50.0, ge=1.0, le=500.0, description="Analysis radius in kilometers"),
    pest_types: Optional[List[PestType]] = Query(None, description="Filter by pest types"),
    severity_threshold: Optional[PestSeverity] = Query(None, description="Minimum severity threshold")
):
    """
    Get comprehensive pest management recommendations.
    
    **Parameters:**
    - **latitude**: Latitude coordinate (-90 to 90)
    - **longitude**: Longitude coordinate (-180 to 180)
    - **crop_type**: Type of crop (corn, soybean, wheat, etc.)
    - **radius_km**: Analysis radius in kilometers (1-500)
    - **pest_types**: Optional filter by pest types
    - **severity_threshold**: Optional minimum severity threshold
    
    **Returns:**
    Comprehensive pest management recommendations including:
    - IPM strategies
    - Cultural practices
    - Chemical controls
    - Biological controls
    - Monitoring recommendations
    - Resistance management
    - Cost-benefit analysis
    """
    try:
        # Create request object
        request = PestResistanceRequest(
            coordinates=(latitude, longitude),
            region_radius_km=radius_km,
            crop_type=crop_type,
            pest_types=pest_types,
            severity_threshold=severity_threshold,
            include_forecast=False,
            include_historical=False,
            include_management_recommendations=True,
            include_variety_recommendations=False,
            include_timing_guidance=True,
            include_resistance_analysis=True
        )
        
        # Perform analysis
        response = await pest_resistance_service.analyze_pest_resistance(request)
        
        return {
            "management_recommendations": response.management_recommendations,
            "timing_guidance": response.timing_guidance,
            "resistance_analysis": response.resistance_analysis,
            "data_quality_score": response.data_quality_score,
            "confidence_level": response.confidence_level
        }
        
    except Exception as e:
        logger.error(f"Error getting pest management recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get pest management recommendations: {str(e)}")


@router.get("/forecast")
async def get_pest_forecast(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude in decimal degrees"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude in decimal degrees"),
    crop_type: str = Query(..., description="Crop type for analysis"),
    forecast_period_days: int = Query(30, ge=1, le=90, description="Forecast period in days"),
    radius_km: float = Query(50.0, ge=1.0, le=500.0, description="Analysis radius in kilometers")
):
    """
    Get pest pressure forecast for a specific location and crop.
    
    **Parameters:**
    - **latitude**: Latitude coordinate (-90 to 90)
    - **longitude**: Longitude coordinate (-180 to 180)
    - **crop_type**: Type of crop (corn, soybean, wheat, etc.)
    - **forecast_period_days**: Forecast period in days (1-90)
    - **radius_km**: Analysis radius in kilometers (1-500)
    
    **Returns:**
    Pest pressure forecast including:
    - Predicted pest pressures
    - Risk trends
    - Timing predictions
    - Confidence levels
    - Weather dependencies
    """
    try:
        # Create request object
        request = PestResistanceRequest(
            coordinates=(latitude, longitude),
            region_radius_km=radius_km,
            crop_type=crop_type,
            analysis_period_days=forecast_period_days,
            include_forecast=True,
            include_historical=False,
            include_management_recommendations=False,
            include_variety_recommendations=False,
            include_timing_guidance=False,
            include_resistance_analysis=False
        )
        
        # Perform analysis
        response = await pest_resistance_service.analyze_pest_resistance(request)
        
        return {
            "pest_forecast": response.pest_forecast,
            "data_quality_score": response.data_quality_score,
            "confidence_level": response.confidence_level
        }
        
    except Exception as e:
        logger.error(f"Error getting pest forecast: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get pest forecast: {str(e)}")


@router.get("/trends")
async def get_pest_trends(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude in decimal degrees"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude in decimal degrees"),
    crop_type: str = Query(..., description="Crop type for analysis"),
    analysis_period_years: int = Query(5, ge=1, le=10, description="Analysis period in years"),
    radius_km: float = Query(50.0, ge=1.0, le=500.0, description="Analysis radius in kilometers")
):
    """
    Get historical pest trends for a specific location and crop.
    
    **Parameters:**
    - **latitude**: Latitude coordinate (-90 to 90)
    - **longitude**: Longitude coordinate (-180 to 180)
    - **crop_type**: Type of crop (corn, soybean, wheat, etc.)
    - **analysis_period_years**: Analysis period in years (1-10)
    - **radius_km**: Analysis radius in kilometers (1-500)
    
    **Returns:**
    Historical pest trends including:
    - Trend directions and magnitudes
    - Seasonal patterns
    - Long-term changes
    - Climate impacts
    - Management implications
    """
    try:
        # Create request object
        request = PestResistanceRequest(
            coordinates=(latitude, longitude),
            region_radius_km=radius_km,
            crop_type=crop_type,
            analysis_period_days=analysis_period_years * 365,
            include_forecast=False,
            include_historical=True,
            include_management_recommendations=False,
            include_variety_recommendations=False,
            include_timing_guidance=False,
            include_resistance_analysis=False
        )
        
        # Perform analysis
        response = await pest_resistance_service.analyze_pest_resistance(request)
        
        return {
            "historical_trends": response.historical_trends,
            "data_quality_score": response.data_quality_score,
            "confidence_level": response.confidence_level
        }
        
    except Exception as e:
        logger.error(f"Error getting pest trends: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get pest trends: {str(e)}")


@router.get("/pest-types")
async def get_available_pest_types():
    """
    Get list of available pest types for filtering.
    
    **Returns:**
    List of available pest types with descriptions.
    """
    return {
        "pest_types": [
            {"value": pest_type.value, "description": pest_type.value.replace("_", " ").title()}
            for pest_type in PestType
        ]
    }


@router.get("/severity-levels")
async def get_severity_levels():
    """
    Get list of available pest severity levels.
    
    **Returns:**
    List of available severity levels with descriptions.
    """
    return {
        "severity_levels": [
            {"value": severity.value, "description": severity.value.title()}
            for severity in PestSeverity
        ]
    }


@router.get("/risk-levels")
async def get_risk_levels():
    """
    Get list of available pest risk levels.
    
    **Returns:**
    List of available risk levels with descriptions.
    """
    return {
        "risk_levels": [
            {"value": risk.value, "description": risk.value.replace("_", " ").title()}
            for risk in PestRiskLevel
        ]
    }


@router.get("/data-sources")
async def get_data_sources():
    """
    Get list of available data sources.
    
    **Returns:**
    List of available data sources with descriptions.
    """
    return {
        "data_sources": [
            {"value": source.value, "description": source.value.replace("_", " ").title()}
            for source in DataSource
        ]
    }


@router.get("/health")
async def health_check():
    """Health check endpoint for service monitoring."""
    return {
        "status": "healthy",
        "service": "pest-resistance-analysis",
        "version": "1.0.0",
        "features": [
            "regional_pest_pressure",
            "variety_resistance_analysis",
            "management_recommendations",
            "timing_guidance",
            "resistance_durability_analysis",
            "pest_forecasting",
            "historical_trends"
        ]
    }