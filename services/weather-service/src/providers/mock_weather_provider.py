#!/usr/bin/env python3
"""
Mock Weather Provider
Weather Impact Analysis Service
Version: 1.0
Date: October 2025
"""

from datetime import datetime, timedelta
from src.schemas.weather_schemas import WeatherRequest, WeatherResponse
import random


class MockWeatherProvider:
    """Mock weather provider for testing purposes."""
    
    def __init__(self):
        """Initialize the mock weather provider."""
        self.provider_name = "MockWeatherProvider"
    
    def get_current_weather(self, request: WeatherRequest) -> WeatherResponse:
        """Get current weather data for the given location.
        
        Args:
            request: WeatherRequest with latitude and longitude
            
        Returns:
            WeatherResponse with current weather data
        """
        # Generate mock weather data based on location
        # In a real implementation, this would call an external API
        
        # Generate realistic weather data based on latitude
        # Northern latitudes tend to be cooler, southern warmer
        base_temp = 20 - abs(request.latitude) * 0.2
        
        # Add some random variation
        temperature = base_temp + random.uniform(-5, 5)
        humidity = random.randint(30, 90)
        precipitation = random.choice([0, 0, 0, 0, 0.5, 1.2, 2.0])
        wind_speed = random.uniform(0, 25)
        wind_direction = random.randint(0, 360)
        pressure = random.uniform(990, 1030)
        
        # Simple condition mapping
        if precipitation > 0:
            conditions = "Rainy" if precipitation > 1 else "Showers"
        elif humidity > 80:
            conditions = "Cloudy"
        elif humidity > 60:
            conditions = "Partly Cloudy"
        else:
            conditions = "Sunny"
        
        cloud_cover = random.randint(0, 100)
        solar_radiation = random.uniform(0, 1000) if "Sunny" in conditions else random.uniform(0, 300)
        
        return WeatherResponse(
            station_id=f"MOCK_{int(request.latitude * 1000)}_{int(request.longitude * 1000)}",
            observation_time=datetime.utcnow(),
            temperature_c=round(temperature, 1),
            temperature_min_c=round(temperature - random.uniform(2, 5), 1),
            temperature_max_c=round(temperature + random.uniform(2, 5), 1),
            precipitation_mm=round(precipitation, 1),
            humidity_percent=humidity,
            wind_speed_kmh=round(wind_speed, 1),
            wind_direction_degrees=wind_direction,
            pressure_hpa=round(pressure, 1),
            conditions=conditions,
            cloud_cover_percent=cloud_cover,
            solar_radiation=round(solar_radiation, 1),
            source=self.provider_name
        )
    
    def get_forecast(self, request: WeatherRequest, days: int = 7) -> list:
        """Get weather forecast for the given location.
        
        Args:
            request: WeatherRequest with latitude and longitude
            days: Number of days to forecast (default: 7)
            
        Returns:
            List of forecast data points
        """
        # Generate mock forecast data
        forecasts = []
        base_date = datetime.utcnow()
        
        for i in range(days):
            forecast_date = base_date + timedelta(days=i)
            
            # Generate mock weather data with some trend
            # Temperature tends to follow a weekly pattern
            base_temp = 20 - abs(request.latitude) * 0.2 + 3 * abs(i - 3) * 0.5
            
            # Add some random variation
            temperature = base_temp + random.uniform(-3, 3)
            humidity = random.randint(30, 90)
            precipitation = random.choice([0, 0, 0, 0, 0, 0.5, 1.2, 2.0])
            wind_speed = random.uniform(0, 25)
            wind_direction = random.randint(0, 360)
            pressure = random.uniform(990, 1030)
            
            # Simple condition mapping
            if precipitation > 0:
                conditions = "Rainy" if precipitation > 1 else "Showers"
            elif humidity > 80:
                conditions = "Cloudy"
            elif humidity > 60:
                conditions = "Partly Cloudy"
            else:
                conditions = "Sunny"
            
            cloud_cover = random.randint(0, 100)
            solar_radiation = random.uniform(0, 1000) if "Sunny" in conditions else random.uniform(0, 300)
            
            forecasts.append({
                "forecast_time": base_date,
                "forecast_for": forecast_date,
                "temperature_c": round(temperature, 1),
                "temperature_min_c": round(temperature - random.uniform(2, 5), 1),
                "temperature_max_c": round(temperature + random.uniform(2, 5), 1),
                "precipitation_mm": round(precipitation, 1),
                "humidity_percent": humidity,
                "wind_speed_kmh": round(wind_speed, 1),
                "wind_direction_degrees": wind_direction,
                "pressure_hpa": round(pressure, 1),
                "conditions": conditions,
                "cloud_cover_percent": cloud_cover,
                "solar_radiation": round(solar_radiation, 1),
                "source": self.provider_name
            })
        
        return forecasts