#!/usr/bin/env python3
"""
Weather Routes
Weather Impact Analysis Service
Version: 1.0
Date: October 2025
"""

from fastapi import APIRouter, Query, HTTPException, Body
from typing import Optional
from pydantic import BaseModel
from src.schemas.weather_schemas import WeatherRequest, WeatherResponse, ForecastResponse
from src.providers.mock_weather_provider import MockWeatherProvider
from src.services.impact_analyzer import WeatherImpactAnalyzer

# Create router instance
router = APIRouter(
    prefix="/api/v1/weather",
    tags=["weather"],
    responses={404: {"description": "Not found"}},
)


class PlantingAnalysisRequest(BaseModel):
    """Request schema for planting analysis."""
    latitude: float
    longitude: float
    crop_type: str


@router.get("/current", response_model=WeatherResponse)
async def get_current_weather(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude in decimal degrees"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude in decimal degrees")
):
    """Get current weather for a specific location.
    
    Args:
        latitude: Latitude in decimal degrees (-90 to 90)
        longitude: Longitude in decimal degrees (-180 to 180)
        
    Returns:
        WeatherResponse with current weather data
    """
    try:
        # Create weather request
        request = WeatherRequest(latitude=latitude, longitude=longitude)
        
        # Use mock provider for now
        provider = MockWeatherProvider()
        weather_data = provider.get_current_weather(request)
        
        return weather_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching weather data: {str(e)}")


@router.get("/forecast", response_model=ForecastResponse)
async def get_forecast(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude in decimal degrees"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude in decimal degrees"),
    days: int = Query(7, ge=1, le=14, description="Number of days to forecast (1-14)")
):
    """Get weather forecast for a specific location.
    
    Args:
        latitude: Latitude in decimal degrees (-90 to 90)
        longitude: Longitude in decimal degrees (-180 to 180)
        days: Number of days to forecast (1-14, default: 7)
        
    Returns:
        ForecastResponse with forecast data
    """
    try:
        # Create weather request
        request = WeatherRequest(latitude=latitude, longitude=longitude)
        
        # Use mock provider for now
        provider = MockWeatherProvider()
        forecast_data = provider.get_forecast(request, days)
        
        return ForecastResponse(
            station_id=f"MOCK_{int(latitude * 1000)}_{int(longitude * 1000)}",
            forecasts=forecast_data,
            source=provider.provider_name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching forecast data: {str(e)}")


@router.post("/analyze-planting")
async def analyze_planting(request: PlantingAnalysisRequest = Body(...)):
    """Analyze planting conditions for a specific location and crop.
    
    Args:
        request: PlantingAnalysisRequest with location and crop type
        
    Returns:
        Planting conditions analysis
    """
    try:
        # Create weather request
        weather_request = WeatherRequest(
            latitude=request.latitude,
            longitude=request.longitude
        )
        
        # Get current weather data
        provider = MockWeatherProvider()
        weather_data = provider.get_current_weather(weather_request)
        
        # Analyze planting conditions
        analyzer = WeatherImpactAnalyzer()
        analysis = analyzer.analyze_planting_conditions(weather_data, request.crop_type)
        
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing planting conditions: {str(e)}")