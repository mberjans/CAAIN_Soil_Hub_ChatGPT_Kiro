"""
Pytest configuration and fixtures for drought management tests.

This module provides shared fixtures and configuration for all drought management tests.
"""

import pytest
import asyncio
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from decimal import Decimal

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock the models module to avoid import issues
sys.modules['models'] = MagicMock()
sys.modules['models.drought_models'] = MagicMock()

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_farm_location_id():
    """Create a mock farm location ID."""
    return uuid4()

@pytest.fixture
def mock_field_id():
    """Create a mock field ID."""
    return uuid4()

@pytest.fixture
def mock_user_id():
    """Create a mock user ID."""
    return uuid4()

@pytest.fixture
def sample_weather_data():
    """Sample weather data for testing."""
    return {
        "temperature": 25.5,
        "humidity": 65.0,
        "precipitation": 5.2,
        "wind_speed": 12.3,
        "solar_radiation": 850.0,
        "timestamp": datetime.utcnow()
    }

@pytest.fixture
def sample_soil_data():
    """Sample soil data for testing."""
    return {
        "soil_type": "clay_loam",
        "moisture_content": 0.25,
        "field_capacity": 0.35,
        "wilting_point": 0.15,
        "bulk_density": 1.3,
        "organic_matter": 3.2,
        "ph": 6.5,
        "timestamp": datetime.utcnow()
    }

@pytest.fixture
def sample_crop_data():
    """Sample crop data for testing."""
    return {
        "crop_type": "corn",
        "variety": "Pioneer P1234",
        "growth_stage": "V6",
        "planting_date": datetime.utcnow() - timedelta(days=45),
        "expected_harvest_date": datetime.utcnow() + timedelta(days=90),
        "water_requirement": 25.0,  # inches per season
        "drought_tolerance": "moderate"
    }

@pytest.fixture
def sample_drought_assessment_request(mock_farm_location_id, mock_field_id):
    """Sample drought assessment request."""
    return {
        "farm_location_id": mock_farm_location_id,
        "field_id": mock_field_id,
        "crop_type": "corn",
        "growth_stage": "V6",
        "soil_type": "clay_loam",
        "irrigation_available": True,
        "include_forecast": True,
        "assessment_depth_days": 30
    }

@pytest.fixture
def sample_conservation_practices():
    """Sample conservation practices for testing."""
    return [
        {
            "practice_type": "cover_crops",
            "name": "Winter Rye Cover Crop",
            "water_savings_percent": 15.0,
            "implementation_cost_per_acre": 25.0,
            "maintenance_cost_per_acre": 5.0,
            "soil_health_benefits": ["erosion_control", "organic_matter"],
            "implementation_timeline_days": 30
        },
        {
            "practice_type": "mulching",
            "name": "Organic Mulch Application",
            "water_savings_percent": 20.0,
            "implementation_cost_per_acre": 40.0,
            "maintenance_cost_per_acre": 10.0,
            "soil_health_benefits": ["moisture_retention", "temperature_regulation"],
            "implementation_timeline_days": 7
        },
        {
            "practice_type": "tillage_reduction",
            "name": "No-Till Transition",
            "water_savings_percent": 25.0,
            "implementation_cost_per_acre": 100.0,
            "maintenance_cost_per_acre": 0.0,
            "soil_health_benefits": ["structure_improvement", "water_infiltration"],
            "implementation_timeline_days": 90
        }
    ]

@pytest.fixture
def sample_irrigation_data():
    """Sample irrigation system data."""
    return {
        "system_type": "center_pivot",
        "efficiency": 0.85,
        "flow_rate": 1000.0,  # gallons per minute
        "coverage_area": 130.0,  # acres
        "energy_cost_per_gallon": 0.05,
        "maintenance_cost_per_year": 5000.0,
        "installation_cost": 150000.0
    }

@pytest.fixture
def sample_water_source_data():
    """Sample water source data."""
    return {
        "source_type": "groundwater",
        "well_depth": 150.0,  # feet
        "water_quality": "good",
        "sustainability_rating": 0.8,
        "recharge_rate": 0.5,  # inches per month
        "usage_rate": 2.0,  # inches per month
        "cost_per_gallon": 0.02
    }

@pytest.fixture
def mock_external_services():
    """Mock external service dependencies."""
    with patch('src.services.drought_assessment_service.WeatherServiceClient') as mock_weather, \
         patch('src.services.drought_assessment_service.SoilServiceClient') as mock_soil, \
         patch('src.services.drought_assessment_service.CropServiceClient') as mock_crop:
        
        # Configure weather service mock
        mock_weather.return_value.get_current_weather = AsyncMock(return_value={
            "temperature": 25.5,
            "humidity": 65.0,
            "precipitation": 5.2,
            "wind_speed": 12.3
        })
        
        # Configure soil service mock
        mock_soil.return_value.get_soil_data = AsyncMock(return_value={
            "moisture_content": 0.25,
            "field_capacity": 0.35,
            "wilting_point": 0.15
        })
        
        # Configure crop service mock
        mock_crop.return_value.get_crop_requirements = AsyncMock(return_value={
            "water_requirement": 25.0,
            "drought_tolerance": "moderate"
        })
        
        yield {
            "weather": mock_weather,
            "soil": mock_soil,
            "crop": mock_crop
        }

@pytest.fixture
def agricultural_validation_data():
    """Agricultural validation test data."""
    return {
        "known_drought_scenarios": [
            {
                "scenario": "severe_drought_2012",
                "location": {"lat": 40.0, "lng": -95.0},
                "conditions": {
                    "precipitation_deficit": -8.5,  # inches
                    "temperature_anomaly": 3.2,  # degrees F
                    "soil_moisture_deficit": 0.15
                },
                "expected_impacts": {
                    "yield_reduction_percent": 25.0,
                    "water_stress_level": "severe",
                    "recommended_actions": ["irrigation", "drought_tolerant_varieties"]
                }
            },
            {
                "scenario": "moderate_drought_2017",
                "location": {"lat": 42.0, "lng": -93.0},
                "conditions": {
                    "precipitation_deficit": -4.2,
                    "temperature_anomaly": 1.8,
                    "soil_moisture_deficit": 0.08
                },
                "expected_impacts": {
                    "yield_reduction_percent": 12.0,
                    "water_stress_level": "moderate",
                    "recommended_actions": ["conservation_practices", "timing_adjustments"]
                }
            }
        ],
        "conservation_practice_effectiveness": {
            "cover_crops": {
                "water_savings_range": (10.0, 20.0),  # percent
                "soil_health_improvement": 0.15,
                "implementation_success_rate": 0.85
            },
            "no_till": {
                "water_savings_range": (20.0, 30.0),
                "soil_health_improvement": 0.25,
                "implementation_success_rate": 0.75
            },
            "mulching": {
                "water_savings_range": (15.0, 25.0),
                "soil_health_improvement": 0.20,
                "implementation_success_rate": 0.90
            }
        }
    }

@pytest.fixture
def performance_test_data():
    """Performance test data."""
    return {
        "concurrent_users": 500,
        "response_time_threshold": 3.0,  # seconds
        "throughput_threshold": 100,  # requests per second
        "memory_threshold": 1024,  # MB
        "cpu_threshold": 80.0  # percent
    }

# Agricultural validation markers
pytest.mark.agricultural = pytest.mark.agricultural
pytest.mark.performance = pytest.mark.performance
pytest.mark.integration = pytest.mark.integration
pytest.mark.unit = pytest.mark.unit