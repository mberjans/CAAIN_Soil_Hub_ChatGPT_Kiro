"""
Pytest Configuration for Location Input Testing Suite
TICKET-008_farm-location-input-15.1 - Automated testing configuration

This module provides pytest configuration, fixtures, and utilities for the comprehensive
location input testing suite including CI/CD integration and automated regression testing.
"""

import pytest
import asyncio
import os
import sys
import tempfile
import json
from typing import Dict, Any, List
from unittest.mock import Mock, patch
import logging
from datetime import datetime

# Add service paths
sys.path.append(os.path.join(os.path.dirname(__file__), '../services/location-validation/src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../services/frontend/src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../databases/python'))

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_environment():
    """Set up test environment variables and configuration."""
    # Set test environment variables
    test_env = {
        'TESTING': 'true',
        'DATABASE_URL': os.getenv('TEST_DATABASE_URL', 'sqlite:///test.db'),
        'REDIS_URL': os.getenv('TEST_REDIS_URL', 'redis://localhost:6379/1'),
        'GEOCODING_API_KEY': os.getenv('TEST_GEOCODING_API_KEY', 'test_key'),
        'MAPS_API_KEY': os.getenv('TEST_MAPS_API_KEY', 'test_key'),
        'LOG_LEVEL': 'INFO'
    }
    
    # Set environment variables
    for key, value in test_env.items():
        os.environ[key] = value
    
    yield test_env
    
    # Cleanup
    for key in test_env.keys():
        if key in os.environ:
            del os.environ[key]


@pytest.fixture(scope="session")
def test_data_directory():
    """Create temporary directory for test data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture(scope="session")
def test_locations_data():
    """Comprehensive test locations data."""
    return [
        {
            "name": "Ames, Iowa",
            "latitude": 42.0308,
            "longitude": -93.6319,
            "address": "123 Farm Road, Ames, IA 50010",
            "expected_zone": "5a",
            "expected_country": "United States",
            "region": "North America",
            "agricultural_suitability": True,
            "precision_requirement": 0.0001
        },
        {
            "name": "Fargo, North Dakota",
            "latitude": 46.8772,
            "longitude": -96.7898,
            "address": "456 Wheat Field Lane, Fargo, ND 58102",
            "expected_zone": "4a",
            "expected_country": "United States",
            "region": "North America",
            "agricultural_suitability": True,
            "precision_requirement": 0.0001
        },
        {
            "name": "Lubbock, Texas",
            "latitude": 33.5779,
            "longitude": -101.8552,
            "address": "789 Cotton Farm, Lubbock, TX 79401",
            "expected_zone": "7b",
            "expected_country": "United States",
            "region": "North America",
            "agricultural_suitability": True,
            "precision_requirement": 0.0001
        },
        {
            "name": "Fresno, California",
            "latitude": 36.7378,
            "longitude": -119.7871,
            "address": "321 Almond Orchard, Fresno, CA 93701",
            "expected_zone": "9a",
            "expected_country": "United States",
            "region": "North America",
            "agricultural_suitability": True,
            "precision_requirement": 0.0001
        },
        {
            "name": "Buenos Aires, Argentina",
            "latitude": -34.6037,
            "longitude": -58.3816,
            "address": "Estancia San Juan, Buenos Aires",
            "expected_zone": "9b",
            "expected_country": "Argentina",
            "region": "South America",
            "agricultural_suitability": True,
            "precision_requirement": 0.0001
        },
        {
            "name": "Melbourne, Australia",
            "latitude": -37.8136,
            "longitude": 144.9631,
            "address": "Sheep Station, Melbourne",
            "expected_zone": "9a",
            "expected_country": "Australia",
            "region": "Australia",
            "agricultural_suitability": True,
            "precision_requirement": 0.0001
        },
        {
            "name": "North Pole",
            "latitude": 90.0,
            "longitude": 0.0,
            "address": "North Pole",
            "expected_zone": "1a",
            "expected_country": "International Waters",
            "region": "Arctic",
            "agricultural_suitability": False,
            "precision_requirement": 0.01
        },
        {
            "name": "South Pole",
            "latitude": -90.0,
            "longitude": 0.0,
            "address": "South Pole",
            "expected_zone": "1a",
            "expected_country": "Antarctica",
            "region": "Antarctic",
            "agricultural_suitability": False,
            "precision_requirement": 0.01
        },
        {
            "name": "International Date Line",
            "latitude": 0.0,
            "longitude": 180.0,
            "address": "Date Line",
            "expected_zone": "11a",
            "expected_country": "International Waters",
            "region": "Pacific",
            "agricultural_suitability": False,
            "precision_requirement": 0.01
        },
        {
            "name": "Equator Prime Meridian",
            "latitude": 0.0,
            "longitude": 0.0,
            "address": "Greenwich",
            "expected_zone": "11a",
            "expected_country": "International Waters",
            "region": "Atlantic",
            "agricultural_suitability": False,
            "precision_requirement": 0.01
        }
    ]


@pytest.fixture(scope="session")
def test_addresses_data():
    """Test addresses for geocoding tests."""
    return [
        "123 Farm Road, Ames, IA 50010",
        "456 Broadway, New York, NY 10013",
        "789 Sunset Blvd, Los Angeles, CA 90028",
        "RR 1 Box 123, Rural County, IA 50010",
        "12345 Highway 61, Rural Township, IL 60000",
        "PO Box 789, Mountain View, CO 80000",
        "HC 1 Box 456, Remote Valley, MT 59000"
    ]


@pytest.fixture
def mock_validation_service():
    """Create mock validation service for testing."""
    class MockValidationService:
        async def validate_coordinates(self, lat, lng):
            # Basic validation logic
            if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                return Mock(valid=False, errors=["Invalid coordinate range"])
            
            return Mock(
                valid=True,
                latitude=lat,
                longitude=lng,
                climate_zone="5a",
                region="North America",
                agricultural_suitability=True,
                errors=[]
            )
    
    return MockValidationService()


@pytest.fixture
def mock_geocoding_service():
    """Create mock geocoding service for testing."""
    class MockGeocodingService:
        async def geocode_address(self, address):
            # Mock geocoding based on address patterns
            if "Ames" in address:
                return Mock(
                    latitude=42.0308,
                    longitude=-93.6319,
                    address=address,
                    country="United States",
                    state="Iowa",
                    city="Ames"
                )
            elif "New York" in address:
                return Mock(
                    latitude=40.7128,
                    longitude=-74.0060,
                    address=address,
                    country="United States",
                    state="New York",
                    city="New York"
                )
            elif "Los Angeles" in address:
                return Mock(
                    latitude=34.0522,
                    longitude=-118.2437,
                    address=address,
                    country="United States",
                    state="California",
                    city="Los Angeles"
                )
            else:
                return Mock(
                    latitude=42.0308,
                    longitude=-93.6319,
                    address=address,
                    country="United States",
                    state="Iowa",
                    city="Ames"
                )
        
        async def reverse_geocode(self, lat, lng):
            return Mock(
                address="123 Farm Road, Ames, IA 50010",
                country="United States",
                state="Iowa",
                city="Ames"
            )
    
    return MockGeocodingService()


@pytest.fixture
def mock_location_service():
    """Create mock location management service for testing."""
    class MockLocationService:
        def __init__(self):
            self.locations = {}
        
        async def create_location(self, location_data):
            location_id = f"loc_{len(self.locations) + 1}"
            location = Mock(
                id=location_id,
                name=location_data.get("name"),
                latitude=location_data.get("latitude"),
                longitude=location_data.get("longitude"),
                address=location_data.get("address"),
                user_id=location_data.get("user_id")
            )
            self.locations[location_id] = location
            return location
        
        async def get_location(self, location_id, user_id):
            location = self.locations.get(location_id)
            if location and location.user_id == user_id:
                return location
            return None
        
        async def update_location(self, location_id, update_data, user_id):
            location = self.locations.get(location_id)
            if location and location.user_id == user_id:
                for key, value in update_data.items():
                    setattr(location, key, value)
                return location
            return None
        
        async def delete_location(self, location_id, user_id):
            location = self.locations.get(location_id)
            if location and location.user_id == user_id:
                del self.locations[location_id]
                return True
            return False
        
        async def validate_location(self, location_data):
            return Mock(valid=True)
    
    return MockLocationService()


@pytest.fixture
def performance_test_config():
    """Configuration for performance tests."""
    return {
        'max_response_time_ms': 2000,
        'min_throughput_ops_per_sec': 100,
        'max_memory_usage_mb': 500,
        'max_cpu_usage_percent': 80,
        'max_error_rate_percent': 5,
        'concurrent_users_target': 1000,
        'mobile_response_time_ms': 3000,
        'geocoding_accuracy_percent': 95.0,
        'validation_accuracy_percent': 98.0
    }


@pytest.fixture
def geographic_test_config():
    """Configuration for geographic accuracy tests."""
    return {
        'coordinate_precision': 0.000001,
        'climate_zone_accuracy': 0.95,
        'regional_accuracy': 0.98,
        'boundary_tolerance': 0.01,
        'distance_tolerance_meters': 1000
    }


@pytest.fixture
def integration_test_config():
    """Configuration for integration tests."""
    return {
        'api_timeout_seconds': 30,
        'retry_attempts': 3,
        'retry_delay_seconds': 1,
        'batch_size': 100,
        'max_concurrent_requests': 50
    }


@pytest.fixture(autouse=True)
def setup_test_logging():
    """Set up logging for each test."""
    # Create test-specific logger
    test_logger = logging.getLogger(f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    test_logger.setLevel(logging.DEBUG)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    test_logger.addHandler(console_handler)
    
    yield test_logger
    
    # Cleanup
    test_logger.removeHandler(console_handler)


@pytest.fixture
def test_report_config():
    """Configuration for test reporting."""
    return {
        'report_format': 'html',
        'report_file': 'location_input_test_report.html',
        'include_coverage': True,
        'include_performance': True,
        'include_geographic': True,
        'include_integration': True
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers and options."""
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "geographic: mark test as geographic accuracy test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "ci: mark test as CI/CD test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add markers based on test file names
        if "performance" in item.nodeid:
            item.add_marker(pytest.mark.performance)
        if "geographic" in item.nodeid:
            item.add_marker(pytest.mark.geographic)
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        if "comprehensive" in item.nodeid:
            item.add_marker(pytest.mark.slow)


def pytest_runtest_setup(item):
    """Set up each test run."""
    # Skip slow tests unless explicitly requested
    if item.get_closest_marker("slow") and not item.config.getoption("--runslow"):
        pytest.skip("Slow test skipped. Use --runslow to run.")


def pytest_runtest_teardown(item, nextitem):
    """Clean up after each test."""
    # Clean up any test-specific resources
    pass


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Generate terminal summary report."""
    if terminalreporter.config.getoption("--verbose"):
        terminalreporter.write_sep("=", "Location Input Test Suite Summary")
        
        # Count tests by category
        passed = len(terminalreporter.stats.get("passed", []))
        failed = len(terminalreporter.stats.get("failed", []))
        skipped = len(terminalreporter.stats.get("skipped", []))
        
        terminalreporter.write(f"Total tests: {passed + failed + skipped}\n")
        terminalreporter.write(f"Passed: {passed}\n")
        terminalreporter.write(f"Failed: {failed}\n")
        terminalreporter.write(f"Skipped: {skipped}\n")
        
        if failed > 0:
            terminalreporter.write_sep("-", "Failed Tests")
            for test in terminalreporter.stats.get("failed", []):
                terminalreporter.write(f"FAILED: {test.nodeid}\n")


# Custom pytest options
def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--runslow", action="store_true", default=False,
        help="run slow tests"
    )
    parser.addoption(
        "--performance", action="store_true", default=False,
        help="run performance tests only"
    )
    parser.addoption(
        "--geographic", action="store_true", default=False,
        help="run geographic accuracy tests only"
    )
    parser.addoption(
        "--integration", action="store_true", default=False,
        help="run integration tests only"
    )
    parser.addoption(
        "--ci", action="store_true", default=False,
        help="run CI/CD tests only"
    )


# Test utilities
class TestUtilities:
    """Utility functions for tests."""
    
    @staticmethod
    def create_test_location_data(name: str, lat: float, lng: float, **kwargs) -> Dict[str, Any]:
        """Create test location data."""
        return {
            "name": name,
            "latitude": lat,
            "longitude": lng,
            "address": kwargs.get("address", f"{name} Address"),
            "user_id": kwargs.get("user_id", "test_user"),
            **kwargs
        }
    
    @staticmethod
    def validate_coordinate_ranges(lat: float, lng: float) -> bool:
        """Validate coordinate ranges."""
        return -90 <= lat <= 90 and -180 <= lng <= 180
    
    @staticmethod
    def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two coordinates in meters."""
        import math
        
        R = 6371000  # Earth's radius in meters
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    @staticmethod
    def is_agricultural_location(lat: float, lng: float) -> bool:
        """Check if location is likely agricultural."""
        # Simple heuristic based on latitude and known agricultural regions
        agricultural_regions = [
            (25, 70, -170, -50),   # North America
            (35, 80, -10, 180),    # Europe/Asia
            (-35, 40, -20, 55),    # Africa
            (-60, 15, -85, -30),   # South America
            (-45, -10, 110, 160)   # Australia
        ]
        
        for min_lat, max_lat, min_lng, max_lng in agricultural_regions:
            if min_lat <= lat <= max_lat and min_lng <= lng <= max_lng:
                return True
        return False


@pytest.fixture
def test_utilities():
    """Provide test utilities."""
    return TestUtilities()