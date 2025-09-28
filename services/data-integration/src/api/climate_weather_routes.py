"""
Climate-Enhanced Weather API Routes

FastAPI routes for climate zone enhanced weather data and agricultural metrics.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
import structlog

from services.data_integration.src.services.ingestion_service import get_ingestion_service, DataIngestionService
from services.data_integration.src.api.routes import LocationRequest

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/v1/weather", tags=["climate-enhanced-weather"])

class ClimateZoneDataResponse(BaseModel):
    """Climate zone data response model."""
    usda_zone: str
    koppen_classification: str
    average_min_temp_f: float
    average_max_temp_f: float
    annual_precipitation_inches: float
    growing_season_length: int
    last_frost_date: Optional[str] = None
    first_frost_date: Optional[str] = None
    source: str = "weather_service_climate_analysis"

class ClimateEnhancedWeatherResponse(BaseModel):
    """Weather data with climate zone context."""
    temperature_f: float
    humidity_percent: float
    precipitation_inches: float
    wind_speed_mph: float
    wind_direction: str
    conditions: str
    pressure_mb: float
    visibility_miles: float
    uv_index: Optional[float] = None
    timestamp: datetime
    climate_zone: ClimateZoneDataResponse
    source: str = "weather_service_with_climate_enhancement"

class ClimateEnhancedAgriculturalMetricsResponse(BaseModel):
    """Agricultural weather metrics enhanced with climate zone data."""
    growing_degree_days: float
    accumulated_precipitation: float
    days_since_rain: int
    soil_temperature_f: Optional[float] = None
    evapotranspiration_inches: Optional[float] = None
    climate_zone: ClimateZoneDataResponse
    frost_risk_score: Optional[float] = None
    growing_season_progress: Optional[float] = None
    seasonal_recommendations: List[str] = []

class ClimateEnhancedForecastResponse(BaseModel):
    """Weather forecast enhanced with climate zone context."""
    date: str
    high_temp_f: float
    low_temp_f: float
    precipitation_chance: float
    precipitation_amount: float
    conditions: str
    wind_speed_mph: float
    humidity_percent: float
    climate_zone_context: Dict[str, Any]

@router.post("/climate-zone", response_model=ClimateZoneDataResponse)
async def get_climate_zone_data(
    location: LocationRequest,
    ingestion_service: DataIngestionService = Depends(get_ingestion_service)
):
    """
    Get climate zone data for a location based on historical weather analysis.
    
    Determines USDA Hardiness Zone, Köppen climate classification, and agricultural
    climate characteristics from long-term weather patterns.
    
    Args:
        location: GPS coordinates (latitude, longitude)
        
    Returns:
        Climate zone classifications and characteristics for agricultural planning
    """
    try:
        logger.info("Fetching climate zone data via ingestion framework", 
                   latitude=location.latitude, longitude=location.longitude)
        
        # Access the weather service directly to get climate zone data
        from ..services.weather_service import WeatherService
        weather_service = WeatherService()
        
        # Get climate zone data directly from the service
        climate_data = await weather_service.get_climate_zone_data(
            location.latitude, location.longitude
        )
        
        if not climate_data:
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve climate zone data"
            )
        
        return ClimateZoneDataResponse(
            usda_zone=climate_data.usda_zone,
            koppen_classification=climate_data.koppen_classification,
            average_min_temp_f=climate_data.average_min_temp_f,
            average_max_temp_f=climate_data.average_max_temp_f,
            annual_precipitation_inches=climate_data.annual_precipitation_inches,
            growing_season_length=climate_data.growing_season_length,
            last_frost_date=climate_data.last_frost_date,
            first_frost_date=climate_data.first_frost_date,
            source="weather_service_climate_analysis"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching climate zone data", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching climate zone data: {str(e)}"
        )

@router.post("/climate-enhanced", response_model=ClimateEnhancedWeatherResponse)
async def get_climate_enhanced_weather(
    location: LocationRequest,
    ingestion_service: DataIngestionService = Depends(get_ingestion_service)
):
    """
    Get current weather data enhanced with climate zone context.
    
    Combines current weather observations with long-term climate zone data
    for better agricultural decision making.
    
    Args:
        location: GPS coordinates (latitude, longitude)
        
    Returns:
        Current weather with climate zone context and agricultural implications
    """
    try:
        logger.info("Fetching climate-enhanced weather via ingestion framework", 
                   latitude=location.latitude, longitude=location.longitude)
        
        # Get current weather data
        weather_result = await ingestion_service.get_weather_data(
            location.latitude, location.longitude, "current_weather"
        )
        
        if not weather_result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Weather data ingestion failed: {weather_result.error_message}"
            )
        
        # Get climate zone data
        from ..services.weather_service import WeatherService
        weather_service = WeatherService()
        climate_data = await weather_service.get_climate_zone_data(
            location.latitude, location.longitude
        )
        
        if not climate_data:
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve climate zone data"
            )
        
        weather_data = weather_result.data
        
        return ClimateEnhancedWeatherResponse(
            temperature_f=weather_data["temperature_f"],
            humidity_percent=weather_data["humidity_percent"],
            precipitation_inches=weather_data["precipitation_inches"],
            wind_speed_mph=weather_data["wind_speed_mph"],
            wind_direction=weather_data["wind_direction"],
            conditions=weather_data["conditions"],
            pressure_mb=weather_data["pressure_mb"],
            visibility_miles=weather_data["visibility_miles"],
            uv_index=weather_data.get("uv_index"),
            timestamp=datetime.fromisoformat(weather_data["timestamp"].replace("Z", "+00:00")) if weather_data.get("timestamp") else datetime.utcnow(),
            climate_zone=ClimateZoneDataResponse(
                usda_zone=climate_data.usda_zone,
                koppen_classification=climate_data.koppen_classification,
                average_min_temp_f=climate_data.average_min_temp_f,
                average_max_temp_f=climate_data.average_max_temp_f,
                annual_precipitation_inches=climate_data.annual_precipitation_inches,
                growing_season_length=climate_data.growing_season_length,
                last_frost_date=climate_data.last_frost_date,
                first_frost_date=climate_data.first_frost_date
            ),
            source=f"{weather_data.get('data_source', 'weather_service')} with climate enhancement"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching climate-enhanced weather", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching climate-enhanced weather: {str(e)}"
        )

@router.post("/agricultural-metrics-climate-enhanced", response_model=ClimateEnhancedAgriculturalMetricsResponse)
async def get_climate_enhanced_agricultural_metrics(
    location: LocationRequest,
    base_temp_f: float = Query(50.0, ge=32.0, le=80.0, description="Base temperature for growing degree days calculation"),
    ingestion_service: DataIngestionService = Depends(get_ingestion_service)
):
    """
    Get agricultural weather metrics enhanced with climate zone data.
    
    Calculates growing degree days, precipitation accumulation, and other agricultural
    metrics with climate zone context for improved accuracy.
    
    Args:
        location: GPS coordinates (latitude, longitude)
        base_temp_f: Base temperature for growing degree days calculation
        
    Returns:
        Climate-enhanced agricultural weather metrics and recommendations
    """
    try:
        logger.info("Calculating climate-enhanced agricultural metrics", 
                   latitude=location.latitude, longitude=location.longitude, base_temp=base_temp_f)
        
        # Get agricultural metrics through ingestion service
        metrics_result = await ingestion_service.get_weather_data(
            location.latitude, location.longitude, "agricultural_metrics", base_temp_f=base_temp_f
        )
        
        if not metrics_result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Agricultural metrics ingestion failed: {metrics_result.error_message}"
            )
        
        # Get climate zone data for context
        from ..services.weather_service import WeatherService
        weather_service = WeatherService()
        climate_data = await weather_service.get_climate_zone_data(
            location.latitude, location.longitude
        )
        
        if not climate_data:
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve climate zone data"
            )
        
        metrics_data = metrics_result.data
        
        # Calculate growing season progress
        growing_season_progress = None
        if climate_data.growing_season_length and climate_data.growing_season_length > 0:
            # Simplified calculation - in a real implementation this would be more sophisticated
            growing_season_progress = min(1.0, max(0.0, metrics_data.get("growing_degree_days", 0) / 1000))
        
        # Generate climate-aware recommendations
        recommendations = []
        
        if metrics_data.get("frost_risk_score", 0) > 0.7:
            recommendations.append("High frost risk - protect sensitive crops")
        
        if climate_data.annual_precipitation_inches < 20:
            recommendations.append("Arid climate zone - prioritize water conservation")
        elif climate_data.annual_precipitation_inches > 50:
            recommendations.append("High precipitation climate - monitor drainage and disease pressure")
        
        if climate_data.koppen_classification and climate_data.koppen_classification.startswith('B'):
            recommendations.append("Arid/semi-arid climate - consider drought-tolerant varieties")
        
        return ClimateEnhancedAgriculturalMetricsResponse(
            growing_degree_days=metrics_data.get("growing_degree_days", 0.0),
            accumulated_precipitation=metrics_data.get("accumulated_precipitation", 0.0),
            days_since_rain=metrics_data.get("days_since_rain", 0),
            soil_temperature_f=metrics_data.get("soil_temperature_f"),
            evapotranspiration_inches=metrics_data.get("evapotranspiration_inches"),
            climate_zone=ClimateZoneDataResponse(
                usda_zone=climate_data.usda_zone,
                koppen_classification=climate_data.koppen_classification,
                average_min_temp_f=climate_data.average_min_temp_f,
                average_max_temp_f=climate_data.average_max_temp_f,
                annual_precipitation_inches=climate_data.annual_precipitation_inches,
                growing_season_length=climate_data.growing_season_length,
                last_frost_date=climate_data.last_frost_date,
                first_frost_date=climate_data.first_frost_date
            ),
            frost_risk_score=metrics_data.get("frost_risk_score"),
            growing_season_progress=growing_season_progress,
            seasonal_recommendations=recommendations
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error calculating climate-enhanced agricultural metrics", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating climate-enhanced agricultural metrics: {str(e)}"
        )

@router.post("/climate-forecast", response_model=List[ClimateEnhancedForecastResponse])
async def get_climate_enhanced_forecast(
    location: LocationRequest,
    days: int = Query(7, ge=1, le=14, description="Number of forecast days"),
    ingestion_service: DataIngestionService = Depends(get_ingestion_service)
):
    """
    Get weather forecast enhanced with climate zone context.
    
    Provides daily weather forecast with long-term climate zone implications
    for agricultural planning.
    
    Args:
        location: GPS coordinates (latitude, longitude)
        days: Number of forecast days (1-14)
        
    Returns:
        Climate-enhanced daily weather forecast
    """
    try:
        logger.info("Fetching climate-enhanced forecast", 
                   latitude=location.latitude, longitude=location.longitude, days=days)
        
        # Get forecast through ingestion service
        forecast_result = await ingestion_service.get_weather_data(
            location.latitude, location.longitude, "forecast", days=days
        )
        
        if not forecast_result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Forecast ingestion failed: {forecast_result.error_message}"
            )
        
        # Get climate zone data for context
        from ..services.weather_service import WeatherService
        weather_service = WeatherService()
        climate_data = await weather_service.get_climate_zone_data(
            location.latitude, location.longitude
        )
        
        if not climate_data:
            raise HTTPException(
                status_code=500,
                detail="Failed to retrieve climate zone data"
            )
        
        forecast_data = forecast_result.data["forecast"]
        
        # Prepare climate context for each forecast day
        climate_zone_context = {
            "usda_zone": climate_data.usda_zone,
            "koppen_classification": climate_data.koppen_classification,
            "seasonal_expectations": {
                "average_min_temp_f": climate_data.average_min_temp_f,
                "average_max_temp_f": climate_data.average_max_temp_f,
                "growing_season_length": climate_data.growing_season_length
            },
            "frost_dates": {
                "last_spring_frost": climate_data.last_frost_date,
                "first_fall_frost": climate_data.first_frost_date
            }
        }
        
        enhanced_forecast = []
        for day in forecast_data:
            enhanced_forecast.append(ClimateEnhancedForecastResponse(
                date=day["date"],
                high_temp_f=day["high_temp_f"],
                low_temp_f=day["low_temp_f"],
                precipitation_chance=day["precipitation_chance"],
                precipitation_amount=day["precipitation_amount"],
                conditions=day["conditions"],
                wind_speed_mph=day["wind_speed_mph"],
                humidity_percent=day["humidity_percent"],
                climate_zone_context=climate_zone_context
            ))
        
        return enhanced_forecast
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching climate-enhanced forecast", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching climate-enhanced forecast: {str(e)}"
        )