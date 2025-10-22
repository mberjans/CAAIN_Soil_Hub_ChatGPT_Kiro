#!/usr/bin/env python3
"""
Weather Schemas
Weather Impact Analysis Service
Version: 1.0
Date: October 2025
"""

from pydantic import BaseModel, Field, validator
from datetime import datetime
from decimal import Decimal
from typing import Optional, List


class WeatherRequest(BaseModel):
    """Request schema for current weather data."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    
    @validator('latitude')
    def latitude_must_be_valid(cls, v):
        if v < -90 or v > 90:
            raise ValueError('Latitude must be between -90 and 90 degrees')
        return v
    
    @validator('longitude')
    def longitude_must_be_valid(cls, v):
        if v < -180 or v > 180:
            raise ValueError('Longitude must be between -180 and 180 degrees')
        return v


class WeatherData(BaseModel):
    """Base weather data schema."""
    temperature_c: Optional[float] = Field(None, description="Temperature in Celsius")
    temperature_min_c: Optional[float] = Field(None, description="Minimum temperature in Celsius")
    temperature_max_c: Optional[float] = Field(None, description="Maximum temperature in Celsius")
    precipitation_mm: Optional[float] = Field(None, description="Precipitation in millimeters")
    humidity_percent: Optional[int] = Field(None, ge=0, le=100, description="Humidity percentage")
    wind_speed_kmh: Optional[float] = Field(None, ge=0, description="Wind speed in km/h")
    wind_direction_degrees: Optional[int] = Field(None, ge=0, le=360, description="Wind direction in degrees")
    pressure_hpa: Optional[float] = Field(None, ge=0, description="Atmospheric pressure in hPa")
    conditions: Optional[str] = Field(None, max_length=100, description="Weather conditions description")
    cloud_cover_percent: Optional[int] = Field(None, ge=0, le=100, description="Cloud cover percentage")
    solar_radiation: Optional[float] = Field(None, ge=0, description="Solar radiation in W/m²")


class WeatherResponse(WeatherData):
    """Response schema for current weather data."""
    station_id: str = Field(..., description="Weather station identifier")
    observation_time: datetime = Field(..., description="Time of observation")
    source: str = Field(..., description="Data source")


class ForecastData(WeatherData):
    """Forecast data schema."""
    forecast_time: datetime = Field(..., description="Time when forecast was made")
    forecast_for: datetime = Field(..., description="Time for which forecast is valid")


class ForecastResponse(BaseModel):
    """Response schema for weather forecast data."""
    station_id: str = Field(..., description="Weather station identifier")
    forecasts: List[ForecastData] = Field(..., description="List of forecast data points")
    source: str = Field(..., description="Data source")