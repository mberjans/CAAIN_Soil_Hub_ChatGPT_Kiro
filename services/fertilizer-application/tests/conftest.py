"""
Test Configuration and Fixtures
TICKET-023_fertilizer-application-method-11.1

This module provides shared test configuration, fixtures, and utilities
for the comprehensive fertilizer application testing suite.
"""

import pytest
import asyncio
import os
import sys
from typing import Dict, Any, List
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.main_minimal import app
from src.services.application_method_service import ApplicationMethodService
from src.services.equipment_assessment_service import EquipmentAssessmentService
from src.services.cost_analysis_service import CostAnalysisService
from src.services.guidance_service import GuidanceService
from src.services.decision_support_service import DecisionSupportService
from src.services.comparison_service import MethodComparisonService
from src.services.algorithm_validation_service import AlgorithmValidationService


# Test Configuration
@pytest.fixture(scope="session")
def test_config():
    """Test configuration for the comprehensive test suite."""
    return {
        "max_response_time_ms": 3000.0,
        "max_memory_usage_mb": 512.0,
        "concurrent_request_limit": 10,
        "performance_test_iterations": 10,
        "agricultural_validation_enabled": True,
        "expert_review_enabled": True,
        "load_test_enabled": True,
        "stress_test_enabled": False,  # Disabled by default for CI
        "test_data_dir": os.path.join(os.path.dirname(__file__), "test_data"),
        "coverage_threshold": 80.0,
        "performance_thresholds": {
            "avg_response_time_ms": 2000.0,
            "p95_response_time_ms": 3000.0,
            "p99_response_time_ms": 4000.0,
            "max_response_time_ms": 5000.0,
            "success_rate": 95.0,
            "avg_memory_mb": 256.0,
            "max_memory_mb": 512.0,
            "requests_per_second": 10.0
        }
    }


# Service Fixtures
@pytest.fixture
def client():
    """Create FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def application_service():
    """Create application method service instance."""
    return ApplicationMethodService()


@pytest.fixture
def equipment_service():
    """Create equipment assessment service instance."""
    return EquipmentAssessmentService()


@pytest.fixture
def cost_service():
    """Create cost analysis service instance."""
    return CostAnalysisService()


@pytest.fixture
def guidance_service():
    """Create guidance service instance."""
    return GuidanceService()


@pytest.fixture
def decision_service():
    """Create decision support service instance."""
    return DecisionSupportService()


@pytest.fixture
def comparison_service():
    """Create method comparison service instance."""
    return MethodComparisonService()


@pytest.fixture
def validation_service():
    """Create algorithm validation service instance."""
    return AlgorithmValidationService()


# Test Data Fixtures
@pytest.fixture
def sample_field_conditions():
    """Create sample field conditions for testing."""
    from src.models.application_models import FieldConditions
    
    return FieldConditions(
        field_size_acres=100.0,
        soil_type="loam",
        drainage_class="well_drained",
        slope_percent=2.5,
        irrigation_available=True,
        field_shape="rectangular",
        access_roads=["north", "south"]
    )


@pytest.fixture
def sample_crop_requirements():
    """Create sample crop requirements for testing."""
    from src.models.application_models import CropRequirements
    
    return CropRequirements(
        crop_type="corn",
        growth_stage="vegetative",
        target_yield=180.0,
        nutrient_requirements={
            "nitrogen": 150.0,
            "phosphorus": 60.0,
            "potassium": 120.0
        },
        application_timing_preferences=["early_morning", "late_evening"]
    )


@pytest.fixture
def sample_fertilizer_specification():
    """Create sample fertilizer specification for testing."""
    from src.models.application_models import FertilizerSpecification
    
    return FertilizerSpecification(
        fertilizer_type="liquid",
        npk_ratio="28-0-0",
        form="liquid",
        solubility=100.0,
        release_rate="immediate",
        cost_per_unit=0.85,
        unit="lbs"
    )


@pytest.fixture
def sample_equipment_specification():
    """Create sample equipment specification for testing."""
    from src.models.application_models import EquipmentSpecification
    
    return EquipmentSpecification(
        equipment_type="sprayer",
        capacity=500.0,
        capacity_unit="gallons",
        application_width=60.0,
        application_rate_range={"min": 10.0, "max": 50.0},
        fuel_efficiency=0.8,
        maintenance_cost_per_hour=15.0
    )


@pytest.fixture
def sample_application_request(sample_field_conditions, sample_crop_requirements, 
                              sample_fertilizer_specification, sample_equipment_specification):
    """Create sample application request for testing."""
    from src.models.application_models import ApplicationRequest
    
    return ApplicationRequest(
        field_conditions=sample_field_conditions,
        crop_requirements=sample_crop_requirements,
        fertilizer_specification=sample_fertilizer_specification,
        available_equipment=[sample_equipment_specification],
        application_goals=["maximize_efficiency", "minimize_cost"],
        constraints={
            "budget_limit": 5000.0,
            "time_constraint": "3_days"
        },
        budget_limit=5000.0
    )


# Mock Fixtures
@pytest.fixture
def mock_external_apis():
    """Mock external API calls for testing."""
    with patch('src.services.weather_service.WeatherService.get_current_weather') as mock_weather, \
         patch('src.services.soil_service.SoilService.get_soil_data') as mock_soil, \
         patch('src.services.market_service.MarketService.get_fertilizer_prices') as mock_market:
        
        # Configure mock responses
        mock_weather.return_value = {
            "temperature_celsius": 22.0,
            "humidity_percent": 65.0,
            "wind_speed_kmh": 8.0,
            "precipitation_mm": 0.0
        }
        
        mock_soil.return_value = {
            "ph": 6.5,
            "organic_matter_percent": 3.2,
            "cec": 15.0,
            "nutrient_levels": {
                "nitrogen": 25.0,
                "phosphorus": 15.0,
                "potassium": 120.0
            }
        }
        
        mock_market.return_value = {
            "nitrogen_price_per_lb": 0.45,
            "phosphorus_price_per_lb": 0.55,
            "potassium_price_per_lb": 0.35
        }
        
        yield {
            "weather": mock_weather,
            "soil": mock_soil,
            "market": mock_market
        }


@pytest.fixture
def mock_database():
    """Mock database operations for testing."""
    with patch('src.database.session') as mock_session, \
         patch('src.database.get_db') as mock_get_db:
        
        mock_session_instance = AsyncMock()
        mock_session.return_value = mock_session_instance
        mock_get_db.return_value = mock_session_instance
        
        yield {
            "session": mock_session,
            "get_db": mock_get_db,
            "session_instance": mock_session_instance
        }


# Test Utilities
class TestDataFactory:
    """Factory class for creating test data."""
    
    @staticmethod
    def create_field_conditions(
        field_size_acres: float = 100.0,
        soil_type: str = "loam",
        drainage_class: str = "well_drained",
        slope_percent: float = 2.5,
        irrigation_available: bool = True,
        field_shape: str = "rectangular",
        access_roads: List[str] = None
    ):
        """Create field conditions for testing."""
        from src.models.application_models import FieldConditions
        
        if access_roads is None:
            access_roads = ["north", "south"]
        
        return FieldConditions(
            field_size_acres=field_size_acres,
            soil_type=soil_type,
            drainage_class=drainage_class,
            slope_percent=slope_percent,
            irrigation_available=irrigation_available,
            field_shape=field_shape,
            access_roads=access_roads
        )
    
    @staticmethod
    def create_crop_requirements(
        crop_type: str = "corn",
        growth_stage: str = "vegetative",
        target_yield: float = 180.0,
        nutrient_requirements: Dict[str, float] = None,
        application_timing_preferences: List[str] = None
    ):
        """Create crop requirements for testing."""
        from src.models.application_models import CropRequirements
        
        if nutrient_requirements is None:
            nutrient_requirements = {
                "nitrogen": 150.0,
                "phosphorus": 60.0,
                "potassium": 120.0
            }
        
        if application_timing_preferences is None:
            application_timing_preferences = ["early_morning", "late_evening"]
        
        return CropRequirements(
            crop_type=crop_type,
            growth_stage=growth_stage,
            target_yield=target_yield,
            nutrient_requirements=nutrient_requirements,
            application_timing_preferences=application_timing_preferences
        )
    
    @staticmethod
    def create_fertilizer_specification(
        fertilizer_type: str = "liquid",
        npk_ratio: str = "28-0-0",
        form: str = "liquid",
        solubility: float = 100.0,
        release_rate: str = "immediate",
        cost_per_unit: float = 0.85,
        unit: str = "lbs"
    ):
        """Create fertilizer specification for testing."""
        from src.models.application_models import FertilizerSpecification
        
        return FertilizerSpecification(
            fertilizer_type=fertilizer_type,
            npk_ratio=npk_ratio,
            form=form,
            solubility=solubility,
            release_rate=release_rate,
            cost_per_unit=cost_per_unit,
            unit=unit
        )
    
    @staticmethod
    def create_equipment_specification(
        equipment_type: str = "sprayer",
        capacity: float = 500.0,
        capacity_unit: str = "gallons",
        application_width: float = 60.0,
        application_rate_range: Dict[str, float] = None,
        fuel_efficiency: float = 0.8,
        maintenance_cost_per_hour: float = 15.0
    ):
        """Create equipment specification for testing."""
        from src.models.application_models import EquipmentSpecification
        
        if application_rate_range is None:
            application_rate_range = {"min": 10.0, "max": 50.0}
        
        return EquipmentSpecification(
            equipment_type=equipment_type,
            capacity=capacity,
            capacity_unit=capacity_unit,
            application_width=application_width,
            application_rate_range=application_rate_range,
            fuel_efficiency=fuel_efficiency,
            maintenance_cost_per_hour=maintenance_cost_per_hour
        )


# Test Markers and Configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "comprehensive: mark test as part of comprehensive test suite"
    )
    config.addinivalue_line(
        "markers", "agricultural_validation: mark test as agricultural validation test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "load_test: mark test as load test"
    )
    config.addinivalue_line(
        "markers", "stress_test: mark test as stress test"
    )
    config.addinivalue_line(
        "markers", "expert_review: mark test as requiring expert review"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add markers based on test file names
        if "comprehensive" in item.nodeid:
            item.add_marker(pytest.mark.comprehensive)
        if "agricultural_validation" in item.nodeid:
            item.add_marker(pytest.mark.agricultural_validation)
        if "performance" in item.nodeid or "load" in item.nodeid:
            item.add_marker(pytest.mark.performance)
        if "stress" in item.nodeid:
            item.add_marker(pytest.mark.stress_test)
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        if "unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)


# Async Test Support
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Test Environment Setup
@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment before each test."""
    # Set test environment variables
    os.environ["TESTING"] = "true"
    os.environ["LOG_LEVEL"] = "WARNING"  # Reduce log noise during tests
    
    yield
    
    # Cleanup after test
    if "TESTING" in os.environ:
        del os.environ["TESTING"]


# Coverage Configuration
@pytest.fixture(scope="session")
def coverage_config():
    """Coverage configuration for tests."""
    return {
        "source": ["src"],
        "omit": [
            "*/tests/*",
            "*/test_*",
            "*/__pycache__/*",
            "*/venv/*",
            "*/env/*"
        ],
        "fail_under": 80.0,
        "show_missing": True,
        "skip_covered": False
    }


# Test Data Directory
@pytest.fixture(scope="session")
def test_data_dir():
    """Test data directory path."""
    return os.path.join(os.path.dirname(__file__), "test_data")


# Performance Test Configuration
@pytest.fixture(scope="session")
def performance_config():
    """Performance test configuration."""
    return {
        "max_response_time_ms": 3000.0,
        "max_memory_usage_mb": 512.0,
        "concurrent_request_limit": 10,
        "performance_test_iterations": 10,
        "load_test_scenarios": [
            {"concurrent_users": 5, "requests_per_user": 10},
            {"concurrent_users": 10, "requests_per_user": 20},
            {"concurrent_users": 20, "requests_per_user": 30}
        ]
    }


# Agricultural Validation Configuration
@pytest.fixture(scope="session")
def agricultural_config():
    """Agricultural validation configuration."""
    return {
        "expert_review_enabled": True,
        "validation_rules_enabled": True,
        "crop_specific_validation": True,
        "soil_method_compatibility": True,
        "equipment_method_compatibility": True,
        "fertilizer_method_compatibility": True,
        "application_rate_validation": True,
        "timing_validation": True,
        "nutrient_requirement_validation": True
    }


# Test Report Configuration
@pytest.fixture(scope="session")
def report_config():
    """Test report configuration."""
    return {
        "html_report": True,
        "xml_report": True,
        "json_report": True,
        "coverage_report": True,
        "performance_report": True,
        "agricultural_validation_report": True,
        "output_dir": "test_reports"
    }


# Error Handling Configuration
@pytest.fixture(scope="session")
def error_handling_config():
    """Error handling configuration for tests."""
    return {
        "max_retries": 3,
        "retry_delay": 1.0,
        "timeout": 30.0,
        "graceful_degradation": True,
        "error_logging": True,
        "error_reporting": True
    }


# Test Categories
TEST_CATEGORIES = {
    "unit": "Unit tests for individual components",
    "integration": "Integration tests for service interactions",
    "performance": "Performance and load tests",
    "agricultural_validation": "Agricultural domain validation tests",
    "comprehensive": "Comprehensive end-to-end tests",
    "stress": "Stress tests for system limits",
    "expert_review": "Tests requiring agricultural expert review"
}


# Test Execution Configuration
def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--run-comprehensive",
        action="store_true",
        default=False,
        help="Run comprehensive test suite"
    )
    parser.addoption(
        "--run-performance",
        action="store_true",
        default=False,
        help="Run performance tests"
    )
    parser.addoption(
        "--run-load-tests",
        action="store_true",
        default=False,
        help="Run load tests"
    )
    parser.addoption(
        "--run-stress-tests",
        action="store_true",
        default=False,
        help="Run stress tests"
    )
    parser.addoption(
        "--run-agricultural-validation",
        action="store_true",
        default=False,
        help="Run agricultural validation tests"
    )
    parser.addoption(
        "--expert-review",
        action="store_true",
        default=False,
        help="Enable expert review for agricultural tests"
    )
    parser.addoption(
        "--coverage-threshold",
        type=float,
        default=80.0,
        help="Minimum coverage threshold"
    )
    parser.addoption(
        "--performance-threshold",
        type=float,
        default=3000.0,
        help="Maximum response time threshold in milliseconds"
    )


def pytest_generate_tests(metafunc):
    """Generate test parameters dynamically."""
    if "test_scenario" in metafunc.fixturenames:
        scenarios = [
            {"name": "corn_liquid", "crop": "corn", "fertilizer": "liquid"},
            {"name": "soybean_granular", "crop": "soybean", "fertilizer": "granular"},
            {"name": "wheat_organic", "crop": "wheat", "fertilizer": "organic"}
        ]
        metafunc.parametrize("test_scenario", scenarios)


# Test Cleanup
@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Clean up after each test."""
    yield
    # Add any cleanup logic here
    pass


# Test Logging
@pytest.fixture(autouse=True)
def setup_test_logging():
    """Set up test logging."""
    import logging
    
    # Configure logging for tests
    logging.basicConfig(
        level=logging.WARNING,  # Reduce log noise during tests
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    yield
    
    # Cleanup logging
    logging.shutdown()


if __name__ == "__main__":
    # Run tests with this configuration
    pytest.main([__file__, "-v"])