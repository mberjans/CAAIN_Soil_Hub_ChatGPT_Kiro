"""
Weather Service Module

Integrates with multiple weather APIs (NOAA, OpenWeatherMap, etc.) 
to provide comprehensive weather data for agricultural decision making.
"""

import asyncio
import aiohttp
import httpx
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os
from dataclasses import dataclass
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class WeatherData:
    """Standardized weather data structure."""
    temperature_f: float
    humidity_percent: float
    precipitation_inches: float
    wind_speed_mph: float
    wind_direction: str
    conditions: str
    pressure_mb: float
    visibility_miles: float
    uv_index: Optional[float] = None
    timestamp: datetime = None


@dataclass
class ForecastDay:
    """Daily forecast data structure."""
    date: str
    high_temp_f: float
    low_temp_f: float
    precipitation_chance: float
    precipitation_amount: float
    conditions: str
    wind_speed_mph: float
    humidity_percent: float


@dataclass
class AgriculturalWeatherMetrics:
    """Agricultural-specific weather calculations."""
    growing_degree_days: float
    accumulated_precipitation: float
    days_since_rain: int
    soil_temperature_f: Optional[float] = None
    evapotranspiration_inches: Optional[float] = None


class WeatherAPIError(Exception):
    """Custom exception for weather API errors."""
    pass


class NOAAWeatherService:
    """NOAA National Weather Service API integration."""
    
    BASE_URL = "https://api.weather.gov"
    
    def __init__(self):
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session."""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                headers={"User-Agent": "AFAS/1.0 (Agricultural Advisory System)"}
            )
        return self.session
    
    async def get_grid_point(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """Get NOAA grid point for coordinates."""
        session = await self._get_session()
        url = f"{self.BASE_URL}/points/{latitude},{longitude}"
        
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("properties", {})
                else:
                    raise WeatherAPIError(f"NOAA API error: {response.status}")
        except Exception as e:
            logger.error("NOAA grid point error", error=str(e))
            raise WeatherAPIError(f"Failed to get NOAA grid point: {str(e)}")
    
    async def get_current_weather(self, latitude: float, longitude: float) -> WeatherData:
        """Get current weather from NOAA."""
        try:
            grid_data = await self.get_grid_point(latitude, longitude)
            forecast_url = grid_data.get("forecast")
            
            if not forecast_url:
                raise WeatherAPIError("No forecast URL from NOAA")
            
            session = await self._get_session()
            async with session.get(forecast_url) as response:
                if response.status == 200:
                    data = await response.json()
                    current_period = data["properties"]["periods"][0]
                    
                    return WeatherData(
                        temperature_f=current_period.get("temperature", 0),
                        humidity_percent=50.0,  # NOAA doesn't provide humidity in basic forecast
                        precipitation_inches=0.0,  # Would need additional API call
                        wind_speed_mph=self._parse_wind_speed(current_period.get("windSpeed", "0 mph")),
                        wind_direction=current_period.get("windDirection", "N"),
                        conditions=current_period.get("shortForecast", "Unknown"),
                        pressure_mb=1013.25,  # Standard pressure as default
                        visibility_miles=10.0,  # Default visibility
                        timestamp=datetime.now()
                    )
                else:
                    raise WeatherAPIError(f"NOAA forecast error: {response.status}")
                    
        except Exception as e:
            logger.error("NOAA current weather error", error=str(e))
            raise WeatherAPIError(f"Failed to get NOAA current weather: {str(e)}")
    
    async def get_forecast(self, latitude: float, longitude: float, days: int = 7) -> List[ForecastDay]:
        """Get forecast from NOAA."""
        try:
            grid_data = await self.get_grid_point(latitude, longitude)
            forecast_url = grid_data.get("forecast")
            
            if not forecast_url:
                raise WeatherAPIError("No forecast URL from NOAA")
            
            session = await self._get_session()
            async with session.get(forecast_url) as response:
                if response.status == 200:
                    data = await response.json()
                    periods = data["properties"]["periods"]
                    
                    forecast_days = []
                    for i in range(0, min(len(periods), days * 2), 2):  # NOAA gives day/night periods
                        day_period = periods[i]
                        night_period = periods[i + 1] if i + 1 < len(periods) else periods[i]
                        
                        forecast_days.append(ForecastDay(
                            date=day_period.get("startTime", "")[:10],
                            high_temp_f=day_period.get("temperature", 0),
                            low_temp_f=night_period.get("temperature", 0),
                            precipitation_chance=0.0,  # Would need gridded forecast
                            precipitation_amount=0.0,
                            conditions=day_period.get("shortForecast", "Unknown"),
                            wind_speed_mph=self._parse_wind_speed(day_period.get("windSpeed", "0 mph")),
                            humidity_percent=50.0
                        ))
                    
                    return forecast_days[:days]
                else:
                    raise WeatherAPIError(f"NOAA forecast error: {response.status}")
                    
        except Exception as e:
            logger.error("NOAA forecast error", error=str(e))
            raise WeatherAPIError(f"Failed to get NOAA forecast: {str(e)}")
    
    def _parse_wind_speed(self, wind_speed_str: str) -> float:
        """Parse wind speed from NOAA format (e.g., '10 mph')."""
        try:
            return float(wind_speed_str.split()[0])
        except (ValueError, IndexError):
            return 0.0
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session:
            await self.session.close()


class OpenWeatherMapService:
    """OpenWeatherMap API integration as fallback service."""
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        if not self.api_key:
            logger.warning("OpenWeatherMap API key not found")
    
    async def get_current_weather(self, latitude: float, longitude: float) -> WeatherData:
        """Get current weather from OpenWeatherMap."""
        if not self.api_key:
            raise WeatherAPIError("OpenWeatherMap API key not configured")
        
        url = f"{self.BASE_URL}/weather"
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": self.api_key,
            "units": "imperial"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    return WeatherData(
                        temperature_f=data["main"]["temp"],
                        humidity_percent=data["main"]["humidity"],
                        precipitation_inches=data.get("rain", {}).get("1h", 0.0) * 0.0393701,  # mm to inches
                        wind_speed_mph=data["wind"]["speed"],
                        wind_direction=self._degrees_to_direction(data["wind"].get("deg", 0)),
                        conditions=data["weather"][0]["description"],
                        pressure_mb=data["main"]["pressure"],
                        visibility_miles=data.get("visibility", 10000) * 0.000621371,  # meters to miles
                        uv_index=None,  # Would need separate UV API call
                        timestamp=datetime.now()
                    )
                else:
                    raise WeatherAPIError(f"OpenWeatherMap error: {response.status_code}")
                    
        except Exception as e:
            logger.error("OpenWeatherMap current weather error", error=str(e))
            raise WeatherAPIError(f"Failed to get OpenWeatherMap current weather: {str(e)}")
    
    async def get_forecast(self, latitude: float, longitude: float, days: int = 7) -> List[ForecastDay]:
        """Get forecast from OpenWeatherMap."""
        if not self.api_key:
            raise WeatherAPIError("OpenWeatherMap API key not configured")
        
        url = f"{self.BASE_URL}/forecast"
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": self.api_key,
            "units": "imperial"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Group forecasts by day
                    daily_forecasts = {}
                    for item in data["list"]:
                        date = datetime.fromtimestamp(item["dt"]).date().isoformat()
                        
                        if date not in daily_forecasts:
                            daily_forecasts[date] = {
                                "temps": [],
                                "conditions": [],
                                "precipitation": 0.0,
                                "wind_speeds": [],
                                "humidity": []
                            }
                        
                        daily_forecasts[date]["temps"].append(item["main"]["temp"])
                        daily_forecasts[date]["conditions"].append(item["weather"][0]["description"])
                        daily_forecasts[date]["precipitation"] += item.get("rain", {}).get("3h", 0.0) * 0.0393701
                        daily_forecasts[date]["wind_speeds"].append(item["wind"]["speed"])
                        daily_forecasts[date]["humidity"].append(item["main"]["humidity"])
                    
                    # Convert to ForecastDay objects
                    forecast_days = []
                    for date, day_data in list(daily_forecasts.items())[:days]:
                        forecast_days.append(ForecastDay(
                            date=date,
                            high_temp_f=max(day_data["temps"]),
                            low_temp_f=min(day_data["temps"]),
                            precipitation_chance=50.0 if day_data["precipitation"] > 0 else 10.0,
                            precipitation_amount=day_data["precipitation"],
                            conditions=day_data["conditions"][0],  # Use first condition
                            wind_speed_mph=sum(day_data["wind_speeds"]) / len(day_data["wind_speeds"]),
                            humidity_percent=sum(day_data["humidity"]) / len(day_data["humidity"])
                        ))
                    
                    return forecast_days
                else:
                    raise WeatherAPIError(f"OpenWeatherMap forecast error: {response.status_code}")
                    
        except Exception as e:
            logger.error("OpenWeatherMap forecast error", error=str(e))
            raise WeatherAPIError(f"Failed to get OpenWeatherMap forecast: {str(e)}")
    
    def _degrees_to_direction(self, degrees: float) -> str:
        """Convert wind degrees to cardinal direction."""
        directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                     "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        index = round(degrees / 22.5) % 16
        return directions[index]


class WeatherService:
    """Main weather service with fallback capabilities."""
    
    def __init__(self):
        self.noaa_service = NOAAWeatherService()
        self.openweather_service = OpenWeatherMapService()
    
    async def get_current_weather(self, latitude: float, longitude: float) -> WeatherData:
        """Get current weather with fallback to multiple services."""
        # Try NOAA first (free, US-focused)
        try:
            return await self.noaa_service.get_current_weather(latitude, longitude)
        except WeatherAPIError as e:
            logger.warning("NOAA weather failed, trying OpenWeatherMap", error=str(e))
            
            # Fallback to OpenWeatherMap
            try:
                return await self.openweather_service.get_current_weather(latitude, longitude)
            except WeatherAPIError as e2:
                logger.error("All weather services failed", noaa_error=str(e), owm_error=str(e2))
                
                # Return default/historical data as last resort
                return self._get_default_weather()
    
    async def get_forecast(self, latitude: float, longitude: float, days: int = 7) -> List[ForecastDay]:
        """Get weather forecast with fallback to multiple services."""
        # Try NOAA first
        try:
            return await self.noaa_service.get_forecast(latitude, longitude, days)
        except WeatherAPIError as e:
            logger.warning("NOAA forecast failed, trying OpenWeatherMap", error=str(e))
            
            # Fallback to OpenWeatherMap
            try:
                return await self.openweather_service.get_forecast(latitude, longitude, days)
            except WeatherAPIError as e2:
                logger.error("All forecast services failed", noaa_error=str(e), owm_error=str(e2))
                
                # Return default forecast as last resort
                return self._get_default_forecast(days)
    
    async def get_agricultural_metrics(self, latitude: float, longitude: float, 
                                     base_temp_f: float = 50.0) -> AgriculturalWeatherMetrics:
        """Calculate agricultural-specific weather metrics."""
        try:
            # Get current weather and recent forecast for calculations
            current = await self.get_current_weather(latitude, longitude)
            forecast = await self.get_forecast(latitude, longitude, 7)
            
            # Calculate growing degree days (simplified)
            gdd = max(0, current.temperature_f - base_temp_f)
            
            # Calculate accumulated precipitation (last 7 days from forecast)
            accumulated_precip = sum(day.precipitation_amount for day in forecast)
            
            # Estimate days since rain (simplified)
            days_since_rain = 0
            for day in forecast:
                if day.precipitation_amount > 0.1:  # More than 0.1 inches
                    break
                days_since_rain += 1
            
            return AgriculturalWeatherMetrics(
                growing_degree_days=gdd,
                accumulated_precipitation=accumulated_precip,
                days_since_rain=days_since_rain,
                soil_temperature_f=current.temperature_f - 5.0,  # Rough estimate
                evapotranspiration_inches=0.2  # Simplified ET calculation
            )
            
        except Exception as e:
            logger.error("Agricultural metrics calculation failed", error=str(e))
            return AgriculturalWeatherMetrics(
                growing_degree_days=0.0,
                accumulated_precipitation=0.0,
                days_since_rain=7
            )
    
    def _get_default_weather(self) -> WeatherData:
        """Return default weather data when all services fail."""
        return WeatherData(
            temperature_f=70.0,
            humidity_percent=60.0,
            precipitation_inches=0.0,
            wind_speed_mph=5.0,
            wind_direction="SW",
            conditions="Unknown - Service Unavailable",
            pressure_mb=1013.25,
            visibility_miles=10.0,
            timestamp=datetime.now()
        )
    
    def _get_default_forecast(self, days: int) -> List[ForecastDay]:
        """Return default forecast when all services fail."""
        forecast = []
        base_date = datetime.now().date()
        
        for i in range(days):
            date = (base_date + timedelta(days=i)).isoformat()
            forecast.append(ForecastDay(
                date=date,
                high_temp_f=75.0,
                low_temp_f=55.0,
                precipitation_chance=30.0,
                precipitation_amount=0.0,
                conditions="Unknown - Service Unavailable",
                wind_speed_mph=8.0,
                humidity_percent=65.0
            ))
        
        return forecast
    
    async def close(self):
        """Close all weather service connections."""
        await self.noaa_service.close()