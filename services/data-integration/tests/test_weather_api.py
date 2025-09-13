"""
Integration Tests for Weather API Endpoints

Tests the FastAPI weather endpoints with real and mocked data.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from datetime import datetime

from src.main import app
from src.services.weather_service import WeatherData, ForecastDay, AgriculturalWeatherMetrics


@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_weather_data():
    """Mock weather data for testing."""
    return WeatherData(
        temperature_f=72.5,
        humidity_percent=65.0,
        precipitation_inches=0.1,
        wind_speed_mph=8.5,
        wind_direction="SW",
        conditions="Partly Cloudy",
        pressure_mb=1013.25,
        visibility_miles=10.0,
        uv_index=5.0,
        timestamp=datetime.now()
    )


@pytest.fixture
def mock_forecast_data():
    """Mock forecast data for testing."""
    return [
        ForecastDay(
            date="2024-12-09",
            high_temp_f=75.0,
            low_temp_f=55.0,
            precipitation_chance=20.0,
            precipitation_amount=0.0,
            conditions="Sunny",
            wind_speed_mph=8.0,
            humidity_percent=60.0
        ),
        ForecastDay(
            date="2024-12-10",
            high_temp_f=72.0,
            low_temp_f=52.0,
            precipitation_chance=40.0,
            precipitation_amount=0.2,
            conditions="Partly Cloudy",
            wind_speed_mph=10.0,
            humidity_percent=70.0
        )
    ]


@pytest.fixture
def mock_agricultural_metrics():
    """Mock agricultural weather metrics for testing."""
    return AgriculturalWeatherMetrics(
        growing_degree_days=22.5,
        accumulated_precipitation=0.8,
        days_since_rain=3,
        soil_temperature_f=67.5,
        evapotranspiration_inches=0.15
    )


class TestWeatherEndpoints:
    """Test weather API endpoints."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "data-integration"
        assert data["status"] == "healthy"
        assert "endpoints" in data
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "AFAS Data Integration Service" in data["message"]
        assert data["documentation"] == "/docs"
    
    @patch('src.api.routes.weather_service.get_current_weather')
    def test_get_current_weather_success(self, mock_get_weather, client, mock_weather_data):
        """Test successful current weather retrieval."""
        mock_get_weather.return_value = mock_weather_data
        
        request_data = {
            "latitude": 42.0308,
            "longitude": -93.6319
        }
        
        response = client.post("/api/v1/weather/current", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["temperature_f"] == 72.5
        assert data["humidity_percent"] == 65.0
        assert data["conditions"] == "Partly Cloudy"
        assert data["wind_direction"] == "SW"
        assert "timestamp" in data
    
    def test_get_current_weather_invalid_coordinates(self, client):
        """Test current weather with invalid coordinates."""
        request_data = {
            "latitude": 91.0,  # Invalid latitude
            "longitude": -93.6319
        }
        
        response = client.post("/api/v1/weather/current", json=request_data)
        assert response.status_code == 422  # Validation error
    
    @patch('src.api.routes.weather_service.get_forecast')
    def test_get_weather_forecast_success(self, mock_get_forecast, client, mock_forecast_data):
        """Test successful weather forecast retrieval."""
        mock_get_forecast.return_value = mock_forecast_data
        
        request_data = {
            "latitude": 42.0308,
            "longitude": -93.6319
        }
        
        response = client.post("/api/v1/weather/forecast?days=2", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
        assert data[0]["date"] == "2024-12-09"
        assert data[0]["high_temp_f"] == 75.0
        assert data[0]["low_temp_f"] == 55.0
        assert data[1]["precipitation_amount"] == 0.2
    
    def test_get_weather_forecast_invalid_days(self, client):
        """Test weather forecast with invalid days parameter."""
        request_data = {
            "latitude": 42.0308,
            "longitude": -93.6319
        }
        
        response = client.post("/api/v1/weather/forecast?days=20", json=request_data)
        assert response.status_code == 422  # Validation error - max 14 days
    
    @patch('src.api.routes.weather_service.get_agricultural_metrics')
    def test_get_agricultural_metrics_success(self, mock_get_metrics, client, mock_agricultural_metrics):
        """Test successful agricultural weather metrics retrieval."""
        mock_get_metrics.return_value = mock_agricultural_metrics
        
        request_data = {
            "latitude": 42.0308,
            "longitude": -93.6319
        }
        
        response = client.post("/api/v1/weather/agricultural-metrics?base_temp_f=50.0", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["growing_degree_days"] == 22.5
        assert data["accumulated_precipitation"] == 0.8
        assert data["days_since_rain"] == 3
        assert data["soil_temperature_f"] == 67.5
        assert isinstance(data["recommendations"], list)
    
    def test_get_agricultural_metrics_invalid_base_temp(self, client):
        """Test agricultural metrics with invalid base temperature."""
        request_data = {
            "latitude": 42.0308,
            "longitude": -93.6319
        }
        
        response = client.post("/api/v1/weather/agricultural-metrics?base_temp_f=100.0", json=request_data)
        assert response.status_code == 422  # Validation error - max 80°F
    
    @patch('src.api.routes.weather_service.get_current_weather')
    def test_weather_service_error_handling(self, mock_get_weather, client):
        """Test error handling when weather service fails."""
        mock_get_weather.side_effect = Exception("Weather service unavailable")
        
        request_data = {
            "latitude": 42.0308,
            "longitude": -93.6319
        }
        
        response = client.post("/api/v1/weather/current", json=request_data)
        assert response.status_code == 500
        
        data = response.json()
        assert "Error fetching weather data" in data["detail"]


class TestAgriculturalRecommendations:
    """Test agricultural recommendation generation based on weather data."""
    
    @patch('src.api.routes.weather_service.get_agricultural_metrics')
    def test_drought_recommendation(self, mock_get_metrics, client):
        """Test drought recommendation when no recent rain."""
        drought_metrics = AgriculturalWeatherMetrics(
            growing_degree_days=25.0,
            accumulated_precipitation=0.1,
            days_since_rain=10,  # Extended dry period
            soil_temperature_f=75.0,
            evapotranspiration_inches=0.3
        )
        mock_get_metrics.return_value = drought_metrics
        
        request_data = {
            "latitude": 42.0308,
            "longitude": -93.6319
        }
        
        response = client.post("/api/v1/weather/agricultural-metrics", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        recommendations = data["recommendations"]
        
        # Should recommend irrigation due to extended dry period
        assert any("irrigation" in rec.lower() for rec in recommendations)
        assert any("dry period" in rec.lower() for rec in recommendations)
    
    @patch('src.api.routes.weather_service.get_agricultural_metrics')
    def test_high_precipitation_recommendation(self, mock_get_metrics, client):
        """Test recommendations for high precipitation conditions."""
        wet_metrics = AgriculturalWeatherMetrics(
            growing_degree_days=15.0,
            accumulated_precipitation=4.5,  # High precipitation
            days_since_rain=0,
            soil_temperature_f=60.0,
            evapotranspiration_inches=0.1
        )
        mock_get_metrics.return_value = wet_metrics
        
        request_data = {
            "latitude": 42.0308,
            "longitude": -93.6319
        }
        
        response = client.post("/api/v1/weather/agricultural-metrics", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        recommendations = data["recommendations"]
        
        # Should warn about disease pressure and field access
        assert any("disease" in rec.lower() for rec in recommendations)
        assert any("field access" in rec.lower() for rec in recommendations)
    
    @patch('src.api.routes.weather_service.get_agricultural_metrics')
    def test_cold_soil_recommendation(self, mock_get_metrics, client):
        """Test recommendations for cold soil conditions."""
        cold_metrics = AgriculturalWeatherMetrics(
            growing_degree_days=5.0,
            accumulated_precipitation=1.0,
            days_since_rain=2,
            soil_temperature_f=45.0,  # Cold soil
            evapotranspiration_inches=0.05
        )
        mock_get_metrics.return_value = cold_metrics
        
        request_data = {
            "latitude": 42.0308,
            "longitude": -93.6319
        }
        
        response = client.post("/api/v1/weather/agricultural-metrics", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        recommendations = data["recommendations"]
        
        # Should warn about cold soil limiting nutrient uptake
        assert any("soil temperature" in rec.lower() for rec in recommendations)
        assert any("nutrient uptake" in rec.lower() for rec in recommendations)


@pytest.mark.integration
class TestRealWeatherAPIIntegration:
    """Integration tests with real weather APIs."""
    
    def test_real_noaa_integration_iowa(self, client):
        """Test with real NOAA API for Iowa location."""
        request_data = {
            "latitude": 42.0308,  # Ames, Iowa
            "longitude": -93.6319
        }
        
        response = client.post("/api/v1/weather/current", json=request_data)
        
        # Should succeed or gracefully fall back to default data
        assert response.status_code == 200
        
        data = response.json()
        assert "temperature_f" in data
        assert "conditions" in data
        assert "timestamp" in data
        
        # Validate reasonable temperature range for Iowa
        assert -40 <= data["temperature_f"] <= 110
        assert 0 <= data["humidity_percent"] <= 100
    
    def test_real_forecast_integration(self, client):
        """Test with real forecast API."""
        request_data = {
            "latitude": 42.0308,  # Ames, Iowa
            "longitude": -93.6319
        }
        
        response = client.post("/api/v1/weather/forecast?days=3", json=request_data)
        
        # Should succeed or gracefully fall back
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) <= 3
        
        for day in data:
            assert "date" in day
            assert "high_temp_f" in day
            assert "low_temp_f" in day
            assert day["high_temp_f"] >= day["low_temp_f"]
    
    def test_real_agricultural_metrics_integration(self, client):
        """Test with real agricultural metrics calculation."""
        request_data = {
            "latitude": 42.0308,  # Ames, Iowa
            "longitude": -93.6319
        }
        
        response = client.post("/api/v1/weather/agricultural-metrics?base_temp_f=50.0", json=request_data)
        
        # Should succeed or gracefully fall back
        assert response.status_code == 200
        
        data = response.json()
        assert "growing_degree_days" in data
        assert "accumulated_precipitation" in data
        assert "days_since_rain" in data
        assert isinstance(data["recommendations"], list)
        
        # Validate reasonable ranges
        assert 0 <= data["growing_degree_days"] <= 100
        assert 0 <= data["accumulated_precipitation"] <= 20
        assert 0 <= data["days_since_rain"] <= 365


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])