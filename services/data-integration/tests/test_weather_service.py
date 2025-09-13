"""
Tests for Weather Service Integration

Tests the weather API integration with NOAA and OpenWeatherMap,
including fallback mechanisms and agricultural metrics calculation.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from src.services.weather_service import (
    WeatherService, NOAAWeatherService, OpenWeatherMapService,
    WeatherData, ForecastDay, AgriculturalWeatherMetrics, WeatherAPIError
)


class TestNOAAWeatherService:
    """Test NOAA Weather Service integration."""
    
    @pytest.fixture
    def noaa_service(self):
        return NOAAWeatherService()
    
    @pytest.mark.asyncio
    async def test_get_grid_point_success(self, noaa_service):
        """Test successful NOAA grid point retrieval."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "properties": {
                "forecast": "https://api.weather.gov/gridpoints/DMX/34,42/forecast",
                "forecastHourly": "https://api.weather.gov/gridpoints/DMX/34,42/forecast/hourly"
            }
        })
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await noaa_service.get_grid_point(42.0308, -93.6319)
            
            assert "forecast" in result
            assert "gridpoints" in result["forecast"]
    
    @pytest.mark.asyncio
    async def test_get_current_weather_success(self, noaa_service):
        """Test successful current weather retrieval from NOAA."""
        # Mock grid point response
        grid_response = MagicMock()
        grid_response.status = 200
        grid_response.json = AsyncMock(return_value={
            "properties": {
                "forecast": "https://api.weather.gov/gridpoints/DMX/34,42/forecast"
            }
        })
        
        # Mock forecast response
        forecast_response = MagicMock()
        forecast_response.status = 200
        forecast_response.json = AsyncMock(return_value={
            "properties": {
                "periods": [
                    {
                        "temperature": 72,
                        "windSpeed": "10 mph",
                        "windDirection": "SW",
                        "shortForecast": "Partly Cloudy"
                    }
                ]
            }
        })
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.side_effect = [grid_response, forecast_response]
            
            result = await noaa_service.get_current_weather(42.0308, -93.6319)
            
            assert isinstance(result, WeatherData)
            assert result.temperature_f == 72
            assert result.wind_speed_mph == 10.0
            assert result.conditions == "Partly Cloudy"
    
    @pytest.mark.asyncio
    async def test_get_forecast_success(self, noaa_service):
        """Test successful forecast retrieval from NOAA."""
        # Mock grid point response
        grid_response = MagicMock()
        grid_response.status = 200
        grid_response.json = AsyncMock(return_value={
            "properties": {
                "forecast": "https://api.weather.gov/gridpoints/DMX/34,42/forecast"
            }
        })
        
        # Mock forecast response with multiple periods
        forecast_response = MagicMock()
        forecast_response.status = 200
        forecast_response.json = AsyncMock(return_value={
            "properties": {
                "periods": [
                    {
                        "startTime": "2024-12-09T12:00:00-06:00",
                        "temperature": 75,
                        "windSpeed": "8 mph",
                        "shortForecast": "Sunny"
                    },
                    {
                        "startTime": "2024-12-09T18:00:00-06:00",
                        "temperature": 55,
                        "windSpeed": "5 mph",
                        "shortForecast": "Clear"
                    },
                    {
                        "startTime": "2024-12-10T12:00:00-06:00",
                        "temperature": 78,
                        "windSpeed": "12 mph",
                        "shortForecast": "Partly Cloudy"
                    },
                    {
                        "startTime": "2024-12-10T18:00:00-06:00",
                        "temperature": 58,
                        "windSpeed": "8 mph",
                        "shortForecast": "Cloudy"
                    }
                ]
            }
        })
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.side_effect = [grid_response, forecast_response]
            
            result = await noaa_service.get_forecast(42.0308, -93.6319, 2)
            
            assert len(result) == 2
            assert isinstance(result[0], ForecastDay)
            assert result[0].high_temp_f == 75
            assert result[0].low_temp_f == 55
    
    def test_parse_wind_speed(self, noaa_service):
        """Test wind speed parsing from NOAA format."""
        assert noaa_service._parse_wind_speed("10 mph") == 10.0
        assert noaa_service._parse_wind_speed("15 to 20 mph") == 15.0
        assert noaa_service._parse_wind_speed("invalid") == 0.0


class TestOpenWeatherMapService:
    """Test OpenWeatherMap Service integration."""
    
    @pytest.fixture
    def owm_service(self):
        with patch.dict('os.environ', {'OPENWEATHER_API_KEY': 'test_api_key'}):
            return OpenWeatherMapService()
    
    @pytest.mark.asyncio
    async def test_get_current_weather_success(self, owm_service):
        """Test successful current weather retrieval from OpenWeatherMap."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "main": {
                "temp": 72.5,
                "humidity": 65,
                "pressure": 1013
            },
            "wind": {
                "speed": 8.5,
                "deg": 225
            },
            "weather": [
                {
                    "description": "partly cloudy"
                }
            ],
            "visibility": 16093,  # meters
            "rain": {
                "1h": 2.5  # mm
            }
        }
        
        with patch('httpx.AsyncClient.get', return_value=mock_response):
            result = await owm_service.get_current_weather(42.0308, -93.6319)
            
            assert isinstance(result, WeatherData)
            assert result.temperature_f == 72.5
            assert result.humidity_percent == 65
            assert result.wind_direction == "SW"
            assert abs(result.precipitation_inches - 0.098) < 0.01  # 2.5mm to inches
    
    @pytest.mark.asyncio
    async def test_get_forecast_success(self, owm_service):
        """Test successful forecast retrieval from OpenWeatherMap."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "list": [
                {
                    "dt": 1702134000,  # 2024-12-09 12:00:00
                    "main": {"temp": 75.0, "humidity": 60},
                    "wind": {"speed": 8.0},
                    "weather": [{"description": "sunny"}],
                    "rain": {"3h": 0.0}
                },
                {
                    "dt": 1702144800,  # 2024-12-09 15:00:00
                    "main": {"temp": 78.0, "humidity": 55},
                    "wind": {"speed": 10.0},
                    "weather": [{"description": "sunny"}],
                    "rain": {"3h": 0.0}
                },
                {
                    "dt": 1702220400,  # 2024-12-10 12:00:00
                    "main": {"temp": 70.0, "humidity": 70},
                    "wind": {"speed": 6.0},
                    "weather": [{"description": "cloudy"}],
                    "rain": {"3h": 5.0}
                }
            ]
        }
        
        with patch('httpx.AsyncClient.get', return_value=mock_response):
            result = await owm_service.get_forecast(42.0308, -93.6319, 2)
            
            assert len(result) >= 1
            assert isinstance(result[0], ForecastDay)
            assert result[0].high_temp_f >= result[0].low_temp_f
    
    def test_degrees_to_direction(self, owm_service):
        """Test wind direction conversion."""
        assert owm_service._degrees_to_direction(0) == "N"
        assert owm_service._degrees_to_direction(90) == "E"
        assert owm_service._degrees_to_direction(180) == "S"
        assert owm_service._degrees_to_direction(270) == "W"
        assert owm_service._degrees_to_direction(225) == "SW"


class TestWeatherService:
    """Test main Weather Service with fallback capabilities."""
    
    @pytest.fixture
    def weather_service(self):
        return WeatherService()
    
    @pytest.mark.asyncio
    async def test_get_current_weather_noaa_success(self, weather_service):
        """Test current weather with successful NOAA response."""
        mock_weather_data = WeatherData(
            temperature_f=72.0,
            humidity_percent=65.0,
            precipitation_inches=0.0,
            wind_speed_mph=8.0,
            wind_direction="SW",
            conditions="Partly Cloudy",
            pressure_mb=1013.25,
            visibility_miles=10.0,
            timestamp=datetime.now()
        )
        
        with patch.object(weather_service.noaa_service, 'get_current_weather', 
                         return_value=mock_weather_data):
            result = await weather_service.get_current_weather(42.0308, -93.6319)
            
            assert result.temperature_f == 72.0
            assert result.conditions == "Partly Cloudy"
    
    @pytest.mark.asyncio
    async def test_get_current_weather_fallback_to_owm(self, weather_service):
        """Test fallback to OpenWeatherMap when NOAA fails."""
        mock_weather_data = WeatherData(
            temperature_f=70.0,
            humidity_percent=60.0,
            precipitation_inches=0.1,
            wind_speed_mph=7.0,
            wind_direction="W",
            conditions="Cloudy",
            pressure_mb=1010.0,
            visibility_miles=8.0,
            timestamp=datetime.now()
        )
        
        with patch.object(weather_service.noaa_service, 'get_current_weather', 
                         side_effect=WeatherAPIError("NOAA failed")):
            with patch.object(weather_service.openweather_service, 'get_current_weather',
                             return_value=mock_weather_data):
                result = await weather_service.get_current_weather(42.0308, -93.6319)
                
                assert result.temperature_f == 70.0
                assert result.conditions == "Cloudy"
    
    @pytest.mark.asyncio
    async def test_get_current_weather_all_services_fail(self, weather_service):
        """Test default weather when all services fail."""
        with patch.object(weather_service.noaa_service, 'get_current_weather',
                         side_effect=WeatherAPIError("NOAA failed")):
            with patch.object(weather_service.openweather_service, 'get_current_weather',
                             side_effect=WeatherAPIError("OWM failed")):
                result = await weather_service.get_current_weather(42.0308, -93.6319)
                
                assert result.temperature_f == 70.0  # Default value
                assert "Unknown" in result.conditions
    
    @pytest.mark.asyncio
    async def test_get_agricultural_metrics(self, weather_service):
        """Test agricultural weather metrics calculation."""
        mock_weather_data = WeatherData(
            temperature_f=75.0,
            humidity_percent=65.0,
            precipitation_inches=0.0,
            wind_speed_mph=8.0,
            wind_direction="SW",
            conditions="Sunny",
            pressure_mb=1013.25,
            visibility_miles=10.0,
            timestamp=datetime.now()
        )
        
        mock_forecast = [
            ForecastDay(
                date="2024-12-09",
                high_temp_f=75.0,
                low_temp_f=55.0,
                precipitation_chance=10.0,
                precipitation_amount=0.0,
                conditions="Sunny",
                wind_speed_mph=8.0,
                humidity_percent=65.0
            ),
            ForecastDay(
                date="2024-12-10",
                high_temp_f=72.0,
                low_temp_f=52.0,
                precipitation_chance=30.0,
                precipitation_amount=0.2,
                conditions="Partly Cloudy",
                wind_speed_mph=10.0,
                humidity_percent=70.0
            )
        ]
        
        with patch.object(weather_service, 'get_current_weather', return_value=mock_weather_data):
            with patch.object(weather_service, 'get_forecast', return_value=mock_forecast):
                result = await weather_service.get_agricultural_metrics(42.0308, -93.6319, 50.0)
                
                assert isinstance(result, AgriculturalWeatherMetrics)
                assert result.growing_degree_days == 25.0  # 75 - 50
                assert result.accumulated_precipitation == 0.2
                assert result.soil_temperature_f == 70.0  # 75 - 5


@pytest.mark.integration
class TestWeatherAPIIntegration:
    """Integration tests with real APIs (requires API keys)."""
    
    @pytest.mark.asyncio
    async def test_noaa_integration_iowa(self):
        """Test NOAA integration with Iowa coordinates."""
        service = NOAAWeatherService()
        
        try:
            # Test with Ames, Iowa coordinates
            result = await service.get_current_weather(42.0308, -93.6319)
            
            assert isinstance(result, WeatherData)
            assert -50 <= result.temperature_f <= 120  # Reasonable temperature range
            assert 0 <= result.humidity_percent <= 100
            assert result.conditions is not None
            
        except WeatherAPIError:
            pytest.skip("NOAA API not available or rate limited")
        finally:
            await service.close()
    
    @pytest.mark.asyncio
    async def test_openweathermap_integration(self):
        """Test OpenWeatherMap integration (requires API key)."""
        import os
        
        if not os.getenv("OPENWEATHER_API_KEY"):
            pytest.skip("OpenWeatherMap API key not configured")
        
        service = OpenWeatherMapService()
        
        try:
            # Test with Ames, Iowa coordinates
            result = await service.get_current_weather(42.0308, -93.6319)
            
            assert isinstance(result, WeatherData)
            assert -50 <= result.temperature_f <= 120
            assert 0 <= result.humidity_percent <= 100
            assert result.conditions is not None
            
        except WeatherAPIError:
            pytest.skip("OpenWeatherMap API not available or rate limited")


if __name__ == "__main__":
    # Run specific tests
    pytest.main([__file__, "-v"])