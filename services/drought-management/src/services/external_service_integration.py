"""
External Service Integration for Soil Moisture Monitoring

Integrates with weather service, crop data service, and field management systems
to provide real-time data for soil moisture monitoring and prediction.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from uuid import UUID
import httpx

logger = logging.getLogger(__name__)

class WeatherServiceIntegration:
    """Integration with weather service for meteorological data."""
    
    def __init__(self, weather_service_url: str = "http://localhost:8003"):
        self.weather_service_url = weather_service_url
        self.client = None
    
    async def initialize(self):
        """Initialize HTTP client for weather service."""
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info("Weather service integration initialized")
    
    async def cleanup(self):
        """Clean up HTTP client."""
        if self.client:
            await self.client.aclose()
        logger.info("Weather service integration cleaned up")
    
    async def get_current_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Get current weather data for coordinates."""
        try:
            url = f"{self.weather_service_url}/api/v1/weather/current"
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "include_agricultural": True
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Retrieved current weather for {latitude}, {longitude}")
            return data
            
        except Exception as e:
            logger.error(f"Error getting current weather: {str(e)}")
            # Return fallback data
            return {
                "temperature": 25.0,
                "humidity": 60.0,
                "precipitation": 0.0,
                "wind_speed": 2.0,
                "solar_radiation": 20.0,
                "conditions": "clear"
            }
    
    async def get_weather_forecast(self, latitude: float, longitude: float, days: int = 7) -> Dict[str, Any]:
        """Get weather forecast for coordinates."""
        try:
            url = f"{self.weather_service_url}/api/v1/weather/forecast"
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "days": days
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Retrieved {days}-day weather forecast for {latitude}, {longitude}")
            return data
            
        except Exception as e:
            logger.error(f"Error getting weather forecast: {str(e)}")
            # Return fallback forecast
            return {
                "forecast": [
                    {
                        "date": datetime.utcnow() + timedelta(days=i),
                        "temperature": 25.0 + i,
                        "humidity": 60.0 - i,
                        "precipitation": 0.0 if i % 3 == 0 else 2.0,
                        "wind_speed": 2.0,
                        "solar_radiation": 20.0,
                        "conditions": "clear"
                    }
                    for i in range(days)
                ]
            }
    
    async def get_historical_weather(self, latitude: float, longitude: float, 
                                   start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get historical weather data for coordinates."""
        try:
            url = f"{self.weather_service_url}/api/v1/weather/historical"
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Retrieved historical weather for {latitude}, {longitude}")
            return data
            
        except Exception as e:
            logger.error(f"Error getting historical weather: {str(e)}")
            # Return empty historical data
            return {"historical_data": []}


class CropServiceIntegration:
    """Integration with crop taxonomy service for crop data."""
    
    def __init__(self, crop_service_url: str = "http://localhost:8004"):
        self.crop_service_url = crop_service_url
        self.client = None
    
    async def initialize(self):
        """Initialize HTTP client for crop service."""
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info("Crop service integration initialized")
    
    async def cleanup(self):
        """Clean up HTTP client."""
        if self.client:
            await self.client.aclose()
        logger.info("Crop service integration cleaned up")
    
    async def get_crop_data(self, field_id: UUID, crop_type: str) -> Dict[str, Any]:
        """Get crop data for a field."""
        try:
            url = f"{self.crop_service_url}/api/v1/crops/varieties"
            params = {
                "crop_type": crop_type,
                "include_water_requirements": True,
                "include_growth_stages": True
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Retrieved crop data for {crop_type}")
            return data
            
        except Exception as e:
            logger.error(f"Error getting crop data: {str(e)}")
            # Return fallback crop data
            return {
                "crop_type": crop_type,
                "growth_stage": "vegetative",
                "water_requirements": {
                    "daily_mm": 5.0,
                    "seasonal_total_mm": 500.0
                },
                "growth_stages": {
                    "initial": {"kc": 0.4, "duration_days": 30},
                    "development": {"kc": 0.7, "duration_days": 40},
                    "mid_season": {"kc": 1.0, "duration_days": 50},
                    "late_season": {"kc": 0.8, "duration_days": 30}
                }
            }
    
    async def get_crop_water_requirements(self, crop_type: str, growth_stage: str) -> Dict[str, Any]:
        """Get crop water requirements for specific growth stage."""
        try:
            url = f"{self.crop_service_url}/api/v1/crops/water-requirements"
            params = {
                "crop_type": crop_type,
                "growth_stage": growth_stage
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Retrieved water requirements for {crop_type} - {growth_stage}")
            return data
            
        except Exception as e:
            logger.error(f"Error getting crop water requirements: {str(e)}")
            # Return fallback water requirements
            kc_values = {
                "initial": 0.4,
                "development": 0.7,
                "mid_season": 1.0,
                "late_season": 0.8,
                "harvest": 0.3
            }
            
            return {
                "crop_type": crop_type,
                "growth_stage": growth_stage,
                "crop_coefficient": kc_values.get(growth_stage, 0.7),
                "daily_water_requirement_mm": 5.0,
                "critical_periods": ["flowering", "grain_filling"]
            }


class FieldServiceIntegration:
    """Integration with field management service for field characteristics."""
    
    def __init__(self, field_service_url: str = "http://localhost:8005"):
        self.field_service_url = field_service_url
        self.client = None
    
    async def initialize(self):
        """Initialize HTTP client for field service."""
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info("Field service integration initialized")
    
    async def cleanup(self):
        """Clean up HTTP client."""
        if self.client:
            await self.client.aclose()
        logger.info("Field service integration cleaned up")
    
    async def get_field_characteristics(self, field_id: UUID) -> Dict[str, Any]:
        """Get field characteristics and soil properties."""
        try:
            url = f"{self.field_service_url}/api/v1/fields/{field_id}/characteristics"
            
            response = await self.client.get(url)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Retrieved field characteristics for {field_id}")
            return data
            
        except Exception as e:
            logger.error(f"Error getting field characteristics: {str(e)}")
            # Return fallback field characteristics
            return {
                "field_id": field_id,
                "soil_type": "clay_loam",
                "field_capacity": 0.35,
                "wilting_point": 0.15,
                "bulk_density": 1.3,
                "monitoring_depth": 100,
                "slope_percent": 2.0,
                "drainage_class": "well_drained",
                "organic_matter_percent": 3.5,
                "ph": 6.5,
                "coordinates": {
                    "latitude": 40.0,
                    "longitude": -95.0
                }
            }
    
    async def get_field_location(self, field_id: UUID) -> Dict[str, Any]:
        """Get field location coordinates."""
        try:
            url = f"{self.field_service_url}/api/v1/fields/{field_id}/location"
            
            response = await self.client.get(url)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Retrieved field location for {field_id}")
            return data
            
        except Exception as e:
            logger.error(f"Error getting field location: {str(e)}")
            # Return fallback location
            return {
                "field_id": field_id,
                "latitude": 40.0,
                "longitude": -95.0,
                "elevation_meters": 300
            }


class ExternalServiceManager:
    """Manager for all external service integrations."""
    
    def __init__(self):
        self.weather_service = WeatherServiceIntegration()
        self.crop_service = CropServiceIntegration()
        self.field_service = FieldServiceIntegration()
        self.initialized = False
    
    async def initialize(self):
        """Initialize all external service integrations."""
        try:
            logger.info("Initializing external service integrations...")
            
            await self.weather_service.initialize()
            await self.crop_service.initialize()
            await self.field_service.initialize()
            
            self.initialized = True
            logger.info("External service integrations initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize external service integrations: {str(e)}")
            raise
    
    async def cleanup(self):
        """Clean up all external service integrations."""
        try:
            logger.info("Cleaning up external service integrations...")
            
            await self.weather_service.cleanup()
            await self.crop_service.cleanup()
            await self.field_service.cleanup()
            
            self.initialized = False
            logger.info("External service integrations cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    async def get_comprehensive_field_data(self, field_id: UUID, crop_type: str) -> Dict[str, Any]:
        """Get comprehensive data for a field from all services."""
        try:
            logger.info(f"Getting comprehensive data for field: {field_id}")
            
            # Get field characteristics and location
            field_chars = await self.field_service.get_field_characteristics(field_id)
            field_location = await self.field_service.get_field_location(field_id)
            
            # Get crop data
            crop_data = await self.crop_service.get_crop_data(field_id, crop_type)
            
            # Get current weather
            coordinates = field_location.get("coordinates", field_location)
            current_weather = await self.weather_service.get_current_weather(
                coordinates["latitude"], coordinates["longitude"]
            )
            
            # Get weather forecast
            weather_forecast = await self.weather_service.get_weather_forecast(
                coordinates["latitude"], coordinates["longitude"], 7
            )
            
            comprehensive_data = {
                "field_id": field_id,
                "field_characteristics": field_chars,
                "field_location": field_location,
                "crop_data": crop_data,
                "current_weather": current_weather,
                "weather_forecast": weather_forecast,
                "timestamp": datetime.utcnow()
            }
            
            logger.info(f"Retrieved comprehensive data for field: {field_id}")
            return comprehensive_data
            
        except Exception as e:
            logger.error(f"Error getting comprehensive field data: {str(e)}")
            raise
    
    async def get_weather_data_for_field(self, field_id: UUID, date: datetime) -> Dict[str, Any]:
        """Get weather data for a field on a specific date."""
        try:
            # Get field location
            field_location = await self.field_service.get_field_location(field_id)
            coordinates = field_location.get("coordinates", field_location)
            
            # Get weather data
            if date.date() == datetime.utcnow().date():
                # Current weather
                weather_data = await self.weather_service.get_current_weather(
                    coordinates["latitude"], coordinates["longitude"]
                )
            else:
                # Historical weather
                weather_data = await self.weather_service.get_historical_weather(
                    coordinates["latitude"], coordinates["longitude"],
                    date, date + timedelta(days=1)
                )
            
            return weather_data
            
        except Exception as e:
            logger.error(f"Error getting weather data for field: {str(e)}")
            raise
    
    async def get_crop_water_requirements_for_field(self, field_id: UUID, crop_type: str, 
                                                  growth_stage: str) -> Dict[str, Any]:
        """Get crop water requirements for a field."""
        try:
            water_requirements = await self.crop_service.get_crop_water_requirements(
                crop_type, growth_stage
            )
            
            return water_requirements
            
        except Exception as e:
            logger.error(f"Error getting crop water requirements: {str(e)}")
            raise


# Service discovery and health checking
class ServiceHealthChecker:
    """Health checker for external services."""
    
    def __init__(self, service_manager: ExternalServiceManager):
        self.service_manager = service_manager
        self.health_status = {}
    
    async def check_all_services(self) -> Dict[str, bool]:
        """Check health of all external services."""
        health_status = {}
        
        try:
            # Check weather service
            weather_health = await self._check_weather_service()
            health_status["weather_service"] = weather_health
            
            # Check crop service
            crop_health = await self._check_crop_service()
            health_status["crop_service"] = crop_health
            
            # Check field service
            field_health = await self._check_field_service()
            health_status["field_service"] = field_health
            
            self.health_status = health_status
            logger.info(f"Service health check completed: {health_status}")
            return health_status
            
        except Exception as e:
            logger.error(f"Error checking service health: {str(e)}")
            return {"error": str(e)}
    
    async def _check_weather_service(self) -> bool:
        """Check weather service health."""
        try:
            url = f"{self.service_manager.weather_service.weather_service_url}/health"
            response = await self.service_manager.weather_service.client.get(url, timeout=5.0)
            return response.status_code == 200
        except:
            return False
    
    async def _check_crop_service(self) -> bool:
        """Check crop service health."""
        try:
            url = f"{self.service_manager.crop_service.crop_service_url}/health"
            response = await self.service_manager.crop_service.client.get(url, timeout=5.0)
            return response.status_code == 200
        except:
            return False
    
    async def _check_field_service(self) -> bool:
        """Check field service health."""
        try:
            url = f"{self.service_manager.field_service.field_service_url}/health"
            response = await self.service_manager.field_service.client.get(url, timeout=5.0)
            return response.status_code == 200
        except:
            return False