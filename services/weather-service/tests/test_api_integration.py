#!/usr/bin/env python3
"""
API Integration Tests
Weather Impact Analysis Service
Version: 1.0
Date: October 2025
"""

import pytest
import requests
from fastapi.testclient import TestClient
from src.main import app


class TestAPIIntegration:
    """Test API integration and end-to-end workflows."""
    
    def test_weather_workflow(self):
        """Test complete weather workflow from data fetch to analysis."""
        client = TestClient(app)
        
        # Test 1: Get current weather
        response = client.get("/api/v1/weather/current?latitude=42.123456&longitude=-93.654321")
        assert response.status_code == 200
        current_weather = response.json()
        assert "temperature_c" in current_weather
        assert "station_id" in current_weather
        
        # Test 2: Get weather forecast
        response = client.get("/api/v1/weather/forecast?latitude=42.123456&longitude=-93.654321&days=3")
        assert response.status_code == 200
        forecast = response.json()
        assert "station_id" in forecast
        assert "forecasts" in forecast
        assert len(forecast["forecasts"]) > 0
        
        # Test 3: Analyze planting conditions
        planting_data = {
            "latitude": 42.123456,
            "longitude": -93.654321,
            "crop_type": "corn"
        }
        response = client.post("/api/v1/weather/analyze-planting", json=planting_data)
        assert response.status_code == 200
        analysis = response.json()
        assert "crop_type" in analysis
        assert "suitability" in analysis
        assert "factors" in analysis
    
    def test_service_health(self):
        """Test that the service health endpoint is working."""
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    def test_current_weather_endpoint(self):
        """Test the current weather endpoint."""
        client = TestClient(app)
        response = client.get("/api/v1/weather/current?latitude=42.123456&longitude=-93.654321")
        assert response.status_code == 200
        data = response.json()
        assert "temperature_c" in data
        assert "station_id" in data
        assert "observation_time" in data


class TestAPIIntegrationValidation:
    """Test validation in API integration."""
    
    def test_weather_workflow_validation(self):
        """Test validation in weather workflow."""
        # This will be implemented later
        pass


if __name__ == "__main__":
    # Run tests if script is executed directly
    pytest.main([__file__, "-v"])