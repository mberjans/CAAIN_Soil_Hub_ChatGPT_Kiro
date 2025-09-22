"""
Shared pytest fixtures and configuration for AFAS testing.

This module provides common fixtures and utilities for testing
the Autonomous Farm Advisory System components.
"""

import pytest
import asyncio
import os
import sys
from datetime import date, datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import AsyncMock, MagicMock
import tempfile
import json

# Add services to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services'))

# Test data constants
TEST_FARM_ID = "test_farm_12345"
TEST_USER_ID = "test_user_67890"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_database():
    """Mock database connection for testing."""
    db_mock = MagicMock()
    db_mock.execute = AsyncMock()
    db_mock.fetch_one = AsyncMock()
    db_mock.fetch_all = AsyncMock()
    return db_mock


@pytest.fixture
def mock_redis():
    """Mock Redis connection for testing."""
    redis_mock = MagicMock()
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.set = AsyncMock(return_value=True)
    redis_mock.delete = AsyncMock(return_value=True)
    redis_mock.exists = AsyncMock(return_value=False)
    return redis_mock


# Agricultural Test Data Fixtures
@pytest.fixture
def iowa_corn_farm_data():
    """Standard Iowa corn/soybean farm test data."""
    return {
        'farm_id': TEST_FARM_ID,
        'farmer_name': 'Test Farmer',
        'location': {
            'latitude': 42.0308,
            'longitude': -93.6319,
            'address': 'Ames, Iowa, USA',
            'state': 'Iowa',
            'county': 'Story'
        },
        'farm_size_acres': 320,
        'primary_crops': ['corn', 'soybean'],
        'soil_data': {
            'ph': 6.4,
            'organic_matter_percent': 3.5,
            'phosphorus_ppm': 28,
            'potassium_ppm': 165,
            'soil_texture': 'silt_loam',
            'drainage_class': 'well_drained',
            'test_date': date(2024, 3, 15),
            'lab_name': 'Iowa State Soil Testing Lab'
        },
        'management_history': {
            'tillage_system': 'no_till',
            'cover_crops': True,
            'rotation': ['corn', 'soybean'],
            'previous_crop': 'soybean'
        }
    }


@pytest.fixture
def california_vegetable_farm_data():
    """California vegetable farm test data."""
    return {
        'farm_id': 'test_farm_ca_001',
        'farmer_name': 'CA Test Farmer',
        'location': {
            'latitude': 36.7783,
            'longitude': -119.4179,
            'address': 'Fresno, California, USA',
            'state': 'California',
            'county': 'Fresno'
        },
        'farm_size_acres': 80,
        'primary_crops': ['tomatoes', 'lettuce', 'broccoli'],
        'soil_data': {
            'ph': 7.2,
            'organic_matter_percent': 2.8,
            'phosphorus_ppm': 45,
            'potassium_ppm': 220,
            'soil_texture': 'sandy_loam',
            'drainage_class': 'well_drained',
            'test_date': date(2024, 2, 20)
        },
        'irrigation': {
            'type': 'drip',
            'available': True
        }
    }


@pytest.fixture
def problematic_soil_data():
    """Challenging soil conditions for testing edge cases."""
    return {
        'farm_id': 'test_farm_problem_001',
        'soil_data': {
            'ph': 5.1,  # Very acidic
            'organic_matter_percent': 1.2,  # Very low
            'phosphorus_ppm': 4,  # Deficient
            'potassium_ppm': 65,  # Low
            'bulk_density': 1.7,  # Compacted
            'drainage_class': 'poorly_drained',
            'test_date': date(2024, 1, 10)
        },
        'field_observations': {
            'compaction_issues': True,
            'erosion_signs': 'severe',
            'standing_water': True
        }
    }


@pytest.fixture
def sample_weather_data():
    """Sample weather data for testing."""
    return {
        'current': {
            'temperature_f': 72.5,
            'humidity_percent': 65,
            'precipitation_inches': 0.0,
            'wind_speed_mph': 8.2,
            'wind_direction': 'SW',
            'pressure_mb': 1013.2,
            'timestamp': datetime.utcnow()
        },
        'forecast': [
            {
                'date': date.today() + timedelta(days=i),
                'high_f': 75 + i,
                'low_f': 55 + i,
                'precipitation_chance': 20 + (i * 10),
                'precipitation_inches': 0.1 if i > 2 else 0.0,
                'conditions': 'partly_cloudy'
            }
            for i in range(7)
        ]
    }


@pytest.fixture
def sample_crop_recommendations():
    """Sample crop recommendation data."""
    return [
        {
            'crop_name': 'corn',
            'variety_suggestions': [
                {
                    'variety_name': 'Pioneer P1197AM',
                    'maturity_days': 111,
                    'yield_potential_bu_per_acre': 185,
                    'drought_tolerance': 'good',
                    'disease_resistance': ['gray_leaf_spot', 'northern_corn_leaf_blight'],
                    'suitability_score': 0.92
                }
            ],
            'suitability_score': 0.89,
            'confidence_factors': {
                'soil_suitability': 0.95,
                'climate_match': 0.88,
                'economic_viability': 0.85
            },
            'explanation': 'Corn is highly suitable for your silt loam soil with pH 6.4.',
            'planting_recommendations': {
                'optimal_planting_window': {
                    'start_date': date(2024, 4, 20),
                    'end_date': date(2024, 5, 15)
                },
                'seeding_rate_seeds_per_acre': 32000,
                'planting_depth_inches': 2.0
            }
        },
        {
            'crop_name': 'soybean',
            'variety_suggestions': [
                {
                    'variety_name': 'Asgrow AG2834',
                    'maturity_group': 2.8,
                    'yield_potential_bu_per_acre': 58,
                    'suitability_score': 0.87
                }
            ],
            'suitability_score': 0.85,
            'confidence_factors': {
                'soil_suitability': 0.90,
                'climate_match': 0.85,
                'economic_viability': 0.80
            },
            'explanation': 'Soybean provides excellent rotation benefits after corn.'
        }
    ]


@pytest.fixture
def sample_fertilizer_recommendations():
    """Sample fertilizer recommendation data."""
    return {
        'nitrogen_program': {
            'total_n_rate_lbs_per_acre': 160,
            'legume_credit_lbs_per_acre': 40,
            'fertilizer_n_needed_lbs_per_acre': 120,
            'recommended_source': 'anhydrous_ammonia',
            'application_timing': [
                {
                    'timing': 'pre_plant',
                    'rate_lbs_n_per_acre': 80,
                    'application_date': date(2024, 4, 25)
                },
                {
                    'timing': 'side_dress_v6',
                    'rate_lbs_n_per_acre': 40,
                    'application_date': date(2024, 6, 15)
                }
            ],
            'cost_per_acre': 52.80
        },
        'phosphorus_program': {
            'recommendation': 'maintenance_only',
            'rate_lbs_p2o5_per_acre': 25,
            'source': 'dap_at_planting',
            'reasoning': 'Soil test P at adequate range',
            'cost_per_acre': 18.50
        },
        'potassium_program': {
            'recommendation': 'build_up',
            'rate_lbs_k2o_per_acre': 60,
            'source': 'muriate_of_potash',
            'timing': 'fall_application',
            'reasoning': 'Soil test K below optimum for high-yield corn',
            'cost_per_acre': 22.40
        }
    }


@pytest.fixture
def mock_external_apis():
    """Mock external API responses."""
    return {
        'weather_api': {
            'current': {
                'temperature': 72.5,
                'humidity': 65,
                'conditions': 'clear'
            },
            'forecast': [
                {'date': '2024-12-10', 'high': 75, 'low': 55, 'precipitation': 0.0}
            ]
        },
        'soil_survey_api': {
            'soil_series': 'Clarion',
            'drainage_class': 'well_drained',
            'typical_ph_range': {'min': 6.0, 'max': 7.5},
            'organic_matter_range': {'min': 2.5, 'max': 4.0}
        }
    }


# Test utilities
class AgriculturalTestValidator:
    """Utility class for validating agricultural test results."""
    
    @staticmethod
    def validate_nutrient_rate(rate: float, nutrient: str, crop: str) -> bool:
        """Validate that nutrient rates are within reasonable ranges."""
        ranges = {
            'nitrogen': {'corn': (80, 220), 'soybean': (0, 40)},
            'phosphorus': {'corn': (20, 80), 'soybean': (15, 60)},
            'potassium': {'corn': (40, 120), 'soybean': (30, 100)}
        }
        
        if nutrient in ranges and crop in ranges[nutrient]:
            min_rate, max_rate = ranges[nutrient][crop]
            return min_rate <= rate <= max_rate
        return True  # Unknown combinations pass validation
    
    @staticmethod
    def validate_confidence_score(score: float) -> bool:
        """Validate confidence score is in valid range."""
        return 0.0 <= score <= 1.0
    
    @staticmethod
    def validate_soil_ph(ph: float) -> bool:
        """Validate soil pH is in reasonable range."""
        return 3.0 <= ph <= 10.0


@pytest.fixture
def agricultural_validator():
    """Agricultural test validation utilities."""
    return AgriculturalTestValidator()


# Mock HTTP client for API testing
@pytest.fixture
def mock_http_client():
    """Mock HTTP client for testing API calls."""
    client_mock = MagicMock()
    client_mock.get = AsyncMock()
    client_mock.post = AsyncMock()
    client_mock.put = AsyncMock()
    client_mock.delete = AsyncMock()
    return client_mock


# Temporary file fixtures for testing file operations
@pytest.fixture
def temp_file():
    """Create a temporary file for testing."""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


# Performance testing fixtures
@pytest.fixture
def performance_timer():
    """Timer for performance testing."""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return Timer()


# Database fixtures for integration testing
@pytest.fixture
async def test_database():
    """Test database connection."""
    # This would be implemented with actual test database setup
    # For now, return a mock
    return MagicMock()


# Authentication fixtures for API testing
@pytest.fixture
def authenticated_user():
    """Mock authenticated user for API testing."""
    return {
        'user_id': TEST_USER_ID,
        'username': 'test_farmer',
        'email': 'test@example.com',
        'farm_ids': [TEST_FARM_ID],
        'headers': {
            'Authorization': 'Bearer test_token_12345'
        }
    }


# Seasonal testing fixtures
@pytest.fixture
def planting_season_context():
    """Context for planting season testing (March-May)."""
    return {
        'season': 'planting',
        'current_date': date(2024, 4, 15),
        'critical_operations': ['soil_preparation', 'planting', 'early_fertilizer'],
        'weather_sensitivity': 'high'
    }


@pytest.fixture
def growing_season_context():
    """Context for growing season testing (June-August)."""
    return {
        'season': 'growing',
        'current_date': date(2024, 7, 15),
        'critical_operations': ['pest_monitoring', 'nutrient_management', 'irrigation'],
        'weather_sensitivity': 'very_high'
    }


@pytest.fixture
def harvest_season_context():
    """Context for harvest season testing (September-November)."""
    return {
        'season': 'harvest',
        'current_date': date(2024, 10, 15),
        'critical_operations': ['harvest_timing', 'grain_drying', 'field_cleanup'],
        'weather_sensitivity': 'high'
    }