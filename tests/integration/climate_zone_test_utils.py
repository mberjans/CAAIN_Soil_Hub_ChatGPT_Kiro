"""
Climate Zone Integration Test Configuration and Utilities
Supporting utilities and configuration for comprehensive climate zone testing.
"""

import pytest
import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from unittest.mock import AsyncMock, MagicMock
import tempfile
import logging

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClimateZoneTestConfig:
    """Configuration for climate zone integration tests."""
    
    # Test data directories
    TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data', 'climate_zones')
    
    # Mock API endpoints
    MOCK_ENDPOINTS = {
        'usda_api': 'https://mock-usda-api.example.com',
        'koppen_api': 'https://mock-koppen-api.example.com',
        'weather_api': 'https://mock-weather-api.example.com'
    }
    
    # Test timeout settings
    DEFAULT_TIMEOUT = 10.0
    INTEGRATION_TIMEOUT = 30.0
    PERFORMANCE_TIMEOUT = 5.0
    
    # Database configuration for tests
    TEST_DATABASE_CONFIG = {
        'host': 'localhost',
        'port': 5432,
        'database': 'afas_test',
        'user': 'test_user',
        'password': 'test_password'
    }
    
    # Redis configuration for tests
    TEST_REDIS_CONFIG = {
        'host': 'localhost',
        'port': 6379,
        'db': 1  # Use different DB for tests
    }


class ClimateZoneTestDataFactory:
    """Factory for generating test data for climate zone tests."""
    
    @staticmethod
    def create_climate_zone_response(zone_id: str = '6a', confidence: float = 0.85) -> Dict[str, Any]:
        """Create a mock climate zone API response."""
        return {
            'zone_id': zone_id,
            'zone_type': 'usda_hardiness',
            'name': f'USDA Zone {zone_id}',
            'description': f'USDA Hardiness Zone {zone_id}',
            'temperature_range': {
                'min_temp_f': -10 if zone_id == '6a' else -5,
                'max_temp_f': -5 if zone_id == '6a' else 0
            },
            'confidence': confidence,
            'source': 'usda_api',
            'detection_date': datetime.utcnow().isoformat(),
            'metadata': {
                'method': 'coordinate_lookup',
                'api_version': '1.0',
                'processing_time_ms': 125
            }
        }
    
    @staticmethod
    def create_koppen_climate_response(code: str = 'Dfa', confidence: float = 0.80) -> Dict[str, Any]:
        """Create a mock Köppen climate classification response."""
        return {
            'code': code,
            'name': 'Hot-summer humid continental' if code == 'Dfa' else f'Climate Type {code}',
            'description': 'Hot summer, cold winter, adequate precipitation',
            'group': code[0] if code else 'D',
            'temperature_pattern': 'continental',
            'precipitation_pattern': 'adequate_year_round',
            'agricultural_suitability': 'excellent',
            'growing_season_months': [4, 5, 6, 7, 8, 9, 10],
            'confidence': confidence,
            'source': 'koppen_api'
        }
    
    @staticmethod
    def create_weather_data(temperature_f: float = 72.5) -> Dict[str, Any]:
        """Create mock weather data."""
        return {
            'current': {
                'temperature_f': temperature_f,
                'humidity_percent': 65,
                'precipitation_inches': 0.0,
                'wind_speed_mph': 8.2,
                'pressure_mb': 1013.2,
                'timestamp': datetime.utcnow().isoformat()
            },
            'forecast': [
                {
                    'date': (datetime.now() + timedelta(days=i)).date().isoformat(),
                    'high_f': temperature_f + 5 + i,
                    'low_f': temperature_f - 10 + i,
                    'precipitation_chance': 20 + (i * 5),
                    'conditions': 'partly_cloudy'
                }
                for i in range(7)
            ],
            'historical': {
                'avg_annual_temp_f': temperature_f,
                'avg_min_temp_f': temperature_f - 15,
                'avg_max_temp_f': temperature_f + 15,
                'annual_precipitation_inches': 32.5,
                'growing_degree_days_base_50': 2800
            }
        }
    
    @staticmethod
    def create_location_validation_response(valid: bool = True, warnings: List[str] = None) -> Dict[str, Any]:
        """Create mock location validation response."""
        return {
            'valid': valid,
            'confidence': 0.9 if valid else 0.3,
            'warnings': warnings or [],
            'errors': [] if valid else ['Location validation failed'],
            'location_info': {
                'latitude': 42.0308,
                'longitude': -93.6319,
                'country': 'US',
                'state': 'Iowa',
                'county': 'Story',
                'agricultural_region': 'Corn Belt'
            } if valid else None,
            'validation_timestamp': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def create_historical_climate_records(zone_id: str = '6a', years: int = 5) -> List[Dict[str, Any]]:
        """Create mock historical climate zone records."""
        records = []
        base_date = datetime.now()
        
        for i in range(years):
            record_date = base_date - timedelta(days=365 * i)
            # Simulate gradual zone change
            current_zone = zone_id if i < 2 else '5b'
            
            records.append({
                'zone_id': current_zone,
                'zone_type': 'usda_hardiness',
                'detection_date': record_date.isoformat(),
                'confidence_score': 0.85 - (i * 0.05),  # Slightly decreasing confidence over time
                'coordinates': (42.0308, -93.6319),
                'source': 'historical_analysis',
                'metadata': {
                    'data_quality': 'high' if i < 3 else 'medium',
                    'method': 'temperature_analysis'
                }
            })
        
        return records


class ClimateZoneTestMockFactory:
    """Factory for creating mock objects for climate zone tests."""
    
    @staticmethod
    def create_mock_http_client():
        """Create a mock HTTP client with climate zone responses."""
        mock_client = AsyncMock()
        
        async def mock_get(*args, **kwargs):
            url = str(args[0]) if args else str(kwargs.get('url', ''))
            
            mock_response = MagicMock()
            mock_response.status = 200
            
            if 'usda' in url.lower():
                mock_response.json = AsyncMock(
                    return_value=ClimateZoneTestDataFactory.create_climate_zone_response()
                )
            elif 'koppen' in url.lower():
                mock_response.json = AsyncMock(
                    return_value=ClimateZoneTestDataFactory.create_koppen_climate_response()
                )
            elif 'weather' in url.lower():
                mock_response.json = AsyncMock(
                    return_value=ClimateZoneTestDataFactory.create_weather_data()
                )
            else:
                mock_response.json = AsyncMock(return_value={'status': 'success'})
            
            return mock_response
        
        mock_client.get = mock_get
        return mock_client
    
    @staticmethod
    def create_mock_database():
        """Create a mock database with climate zone data."""
        mock_db = AsyncMock()
        
        # Mock database operations
        mock_db.execute = AsyncMock(return_value=None)
        mock_db.fetch_one = AsyncMock(return_value={
            'id': 1,
            'zone_id': '6a',
            'zone_type': 'usda_hardiness',
            'confidence_score': 0.85,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        mock_db.fetch_all = AsyncMock(
            return_value=ClimateZoneTestDataFactory.create_historical_climate_records()
        )
        
        # Mock transaction support
        mock_transaction = AsyncMock()
        mock_transaction.__aenter__ = AsyncMock(return_value=mock_transaction)
        mock_transaction.__aexit__ = AsyncMock(return_value=None)
        mock_db.transaction = AsyncMock(return_value=mock_transaction)
        
        return mock_db
    
    @staticmethod
    def create_mock_redis():
        """Create a mock Redis client for caching tests."""
        mock_redis = AsyncMock()
        
        # Cache operations
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.set = AsyncMock(return_value=True)
        mock_redis.delete = AsyncMock(return_value=True)
        mock_redis.exists = AsyncMock(return_value=False)
        mock_redis.expire = AsyncMock(return_value=True)
        
        # Hash operations for structured data
        mock_redis.hget = AsyncMock(return_value=None)
        mock_redis.hset = AsyncMock(return_value=True)
        mock_redis.hdel = AsyncMock(return_value=True)
        
        return mock_redis


class ClimateZoneTestValidator:
    """Validator for climate zone test results."""
    
    @staticmethod
    def validate_zone_detection_result(result: Dict[str, Any]) -> bool:
        """Validate climate zone detection result structure."""
        required_fields = ['zone_id', 'confidence', 'source']
        
        for field in required_fields:
            if field not in result:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate confidence score
        if not 0.0 <= result['confidence'] <= 1.0:
            logger.error(f"Invalid confidence score: {result['confidence']}")
            return False
        
        # Validate zone ID format
        zone_id = result['zone_id']
        if not isinstance(zone_id, str) or len(zone_id) < 1:
            logger.error(f"Invalid zone ID: {zone_id}")
            return False
        
        return True
    
    @staticmethod
    def validate_integration_workflow_result(result: Dict[str, Any]) -> bool:
        """Validate complete integration workflow result."""
        required_sections = ['location_validation', 'climate_detection', 'recommendations']
        
        for section in required_sections:
            if section not in result:
                logger.error(f"Missing workflow section: {section}")
                return False
        
        # Validate each section
        if not result['location_validation'].get('valid', False):
            logger.warning("Location validation failed")
        
        if not result['climate_detection'].get('zone_id'):
            logger.error("Climate detection failed to return zone ID")
            return False
        
        if not result['recommendations'] or len(result['recommendations']) == 0:
            logger.warning("No recommendations generated")
        
        return True
    
    @staticmethod
    def validate_performance_metrics(metrics: Dict[str, float], thresholds: Dict[str, float]) -> bool:
        """Validate performance metrics against thresholds."""
        for metric, threshold in thresholds.items():
            if metric not in metrics:
                logger.error(f"Missing performance metric: {metric}")
                return False
            
            if metrics[metric] > threshold:
                logger.error(f"Performance metric {metric} ({metrics[metric]}) exceeds threshold ({threshold})")
                return False
        
        return True


class ClimateZoneTestUtilities:
    """Utility functions for climate zone tests."""
    
    @staticmethod
    def create_test_coordinates(region: str = 'midwest') -> Dict[str, float]:
        """Create test coordinates for different regions."""
        coordinate_sets = {
            'midwest': {'latitude': 42.0308, 'longitude': -93.6319},  # Iowa
            'southeast': {'latitude': 33.7490, 'longitude': -84.3880},  # Georgia
            'southwest': {'latitude': 32.7767, 'longitude': -96.7970},  # Texas
            'west': {'latitude': 37.7749, 'longitude': -122.4194},  # California
            'northeast': {'latitude': 42.3601, 'longitude': -71.0589},  # Massachusetts
            'invalid_ocean': {'latitude': 25.0, 'longitude': -70.0},  # Atlantic Ocean
            'invalid_arctic': {'latitude': 85.0, 'longitude': -45.0}  # Arctic
        }
        
        return coordinate_sets.get(region, coordinate_sets['midwest'])
    
    @staticmethod
    def generate_test_scenarios() -> List[Dict[str, Any]]:
        """Generate comprehensive test scenarios."""
        scenarios = [
            {
                'name': 'standard_iowa_farm',
                'coordinates': ClimateZoneTestUtilities.create_test_coordinates('midwest'),
                'expected_zone': '6a',
                'expected_confidence': 0.85,
                'agricultural_suitability': 'excellent'
            },
            {
                'name': 'california_vegetable_farm',
                'coordinates': ClimateZoneTestUtilities.create_test_coordinates('west'),
                'expected_zone': '10a',
                'expected_confidence': 0.80,
                'agricultural_suitability': 'good'
            },
            {
                'name': 'florida_citrus_farm',
                'coordinates': {'latitude': 27.9506, 'longitude': -82.4572},
                'expected_zone': '9b',
                'expected_confidence': 0.82,
                'agricultural_suitability': 'excellent'
            },
            {
                'name': 'edge_case_border',
                'coordinates': {'latitude': 49.0, 'longitude': -95.0},  # US-Canada border
                'expected_zone': '3a',
                'expected_confidence': 0.70,
                'agricultural_suitability': 'limited'
            },
            {
                'name': 'invalid_ocean_location',
                'coordinates': ClimateZoneTestUtilities.create_test_coordinates('invalid_ocean'),
                'expected_zone': None,
                'expected_confidence': 0.0,
                'agricultural_suitability': 'none',
                'should_fail': True
            }
        ]
        
        return scenarios
    
    @staticmethod
    async def setup_test_environment():
        """Set up test environment for climate zone integration tests."""
        # Create test data directory if it doesn't exist
        os.makedirs(ClimateZoneTestConfig.TEST_DATA_DIR, exist_ok=True)
        
        # Generate test data files
        test_scenarios = ClimateZoneTestUtilities.generate_test_scenarios()
        
        with open(os.path.join(ClimateZoneTestConfig.TEST_DATA_DIR, 'test_scenarios.json'), 'w') as f:
            json.dump(test_scenarios, f, indent=2, default=str)
        
        logger.info("Test environment setup completed")
    
    @staticmethod
    async def cleanup_test_environment():
        """Clean up test environment after tests."""
        # Clean up temporary files if needed
        import shutil
        if os.path.exists(ClimateZoneTestConfig.TEST_DATA_DIR):
            shutil.rmtree(ClimateZoneTestConfig.TEST_DATA_DIR, ignore_errors=True)
        
        logger.info("Test environment cleanup completed")
    
    @staticmethod
    def measure_integration_performance(func):
        """Decorator to measure integration test performance."""
        import time
        import functools
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                end_time = time.time()
                
                performance_data = {
                    'function': func.__name__,
                    'execution_time': end_time - start_time,
                    'success': True,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                logger.info(f"Performance: {func.__name__} completed in {performance_data['execution_time']:.2f}s")
                
                # Add performance data to result if it's a dict
                if isinstance(result, dict):
                    result['_performance'] = performance_data
                
                return result
                
            except Exception as e:
                end_time = time.time()
                
                performance_data = {
                    'function': func.__name__,
                    'execution_time': end_time - start_time,
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                logger.error(f"Performance: {func.__name__} failed after {performance_data['execution_time']:.2f}s: {e}")
                raise
        
        return wrapper


# Pytest fixtures for climate zone testing
@pytest.fixture(scope="session")
async def climate_zone_test_config():
    """Provide test configuration for climate zone tests."""
    await ClimateZoneTestUtilities.setup_test_environment()
    yield ClimateZoneTestConfig()
    await ClimateZoneTestUtilities.cleanup_test_environment()


@pytest.fixture
def climate_zone_test_data():
    """Provide test data factory for climate zone tests."""
    return ClimateZoneTestDataFactory()


@pytest.fixture
def climate_zone_mock_factory():
    """Provide mock factory for climate zone tests."""
    return ClimateZoneTestMockFactory()


@pytest.fixture
def climate_zone_validator():
    """Provide validator for climate zone test results."""
    return ClimateZoneTestValidator()


@pytest.fixture
def test_scenarios():
    """Provide comprehensive test scenarios."""
    return ClimateZoneTestUtilities.generate_test_scenarios()


@pytest.fixture
async def mock_integrated_services(climate_zone_mock_factory):
    """Provide mocked integrated services for testing."""
    return {
        'http_client': climate_zone_mock_factory.create_mock_http_client(),
        'database': climate_zone_mock_factory.create_mock_database(),
        'redis': climate_zone_mock_factory.create_mock_redis()
    }


if __name__ == "__main__":
    # Run basic test utilities validation
    asyncio.run(ClimateZoneTestUtilities.setup_test_environment())
    print("Climate zone test utilities initialized successfully")