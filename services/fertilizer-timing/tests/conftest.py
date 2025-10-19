"""
Pytest configuration and shared fixtures for fertilizer timing tests.

This module provides reusable test fixtures, mock services, and helper
functions for comprehensive testing of the fertilizer timing optimization
system.
"""

import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, Mock
import types

import pytest

# Setup path imports
_SRC_DIR = Path(__file__).resolve().parents[1] / "src"
_SRC_PATH = str(_SRC_DIR)
if _SRC_PATH not in sys.path:
    sys.path.insert(0, _SRC_PATH)

_SERVICES_DIR = _SRC_DIR / "services"
_SERVICES_PATH = str(_SERVICES_DIR)
if _SERVICES_PATH not in sys.path:
    sys.path.insert(0, _SERVICES_PATH)


# ==============================================================================
# PYTEST CONFIGURATION
# ==============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


# ==============================================================================
# MOCK SERVICES
# ==============================================================================

class MockWeatherService:
    """Mock weather service for testing."""

    def __init__(self):
        self._forecast_data = []
        self._metrics_data = None

    def set_forecast(self, forecast: List[Any]) -> None:
        """Set forecast data for testing."""
        self._forecast_data = forecast

    def set_metrics(self, metrics: Any) -> None:
        """Set agricultural metrics for testing."""
        self._metrics_data = metrics

    async def get_forecast(
        self,
        lat: float,
        lng: float,
        days: int,
    ) -> List[Any]:
        """Return mock forecast data."""
        return self._forecast_data

    async def get_agricultural_metrics(
        self,
        lat: float,
        lng: float,
    ) -> Optional[Any]:
        """Return mock agricultural metrics."""
        return self._metrics_data


class MockSoilService:
    """Mock soil service for testing."""

    def __init__(self):
        self._soil_characteristics = None
        self._should_fail = False

    def set_soil_characteristics(self, characteristics: Any) -> None:
        """Set soil characteristics for testing."""
        self._soil_characteristics = characteristics

    def set_should_fail(self, should_fail: bool) -> None:
        """Control whether service should fail."""
        self._should_fail = should_fail

    async def get_soil_characteristics(
        self,
        lat: float,
        lng: float,
    ) -> Any:
        """Return mock soil characteristics or raise error."""
        if self._should_fail:
            raise Exception("Mock soil service failure")
        return self._soil_characteristics


class MockForecastDay:
    """Mock forecast day for testing."""

    def __init__(
        self,
        day_str: str,
        high: float = 72.0,
        low: float = 55.0,
        precip_chance: float = 0.2,
        precip_amount: float = 0.0,
        wind_speed: float = 8.0,
        humidity: float = 60.0,
    ):
        self.date = day_str
        self.high_temp_f = high
        self.low_temp_f = low
        self.precipitation_chance = precip_chance
        self.precipitation_amount = precip_amount
        self.conditions = "Partly Cloudy"
        self.wind_speed_mph = wind_speed
        self.humidity_percent = humidity


class MockAgriculturalMetrics:
    """Mock agricultural weather metrics."""

    def __init__(
        self,
        soil_temp: Optional[float] = 55.0,
        days_since_rain: int = 3,
        accumulated_precip: float = 0.5,
    ):
        self.soil_temperature_f = soil_temp
        self.days_since_rain = days_since_rain
        self.accumulated_precipitation = accumulated_precip


class MockSoilCharacteristics:
    """Mock soil characteristics."""

    def __init__(
        self,
        texture: str = "silt loam",
        drainage: str = "well drained",
    ):
        self.soil_series = "Test Series"
        self.soil_texture = texture
        self.drainage_class = drainage
        self.typical_ph_range = {"min": 6.0, "max": 7.0}
        self.organic_matter_typical = 3.0
        self.slope_range = "2-5%"
        self.parent_material = "Glacial till"
        self.depth_to_bedrock = None
        self.flooding_frequency = "None"
        self.ponding_frequency = "None"
        self.hydrologic_group = "B"
        self.available_water_capacity = 0.65
        self.permeability = "Moderate"
        self.erosion_factor_k = 0.32


# ==============================================================================
# PYTEST FIXTURES
# ==============================================================================

@pytest.fixture
def sample_planting_date() -> date:
    """Provide a standard planting date for tests."""
    return date(2024, 5, 1)


@pytest.fixture
def sample_location() -> Dict[str, Any]:
    """Provide a standard location for tests."""
    return {
        "lat": 42.0,
        "lng": -93.5,
        "state": "IA",
        "county": "Story County",
    }


@pytest.fixture
def sample_fertilizer_requirements() -> Dict[str, float]:
    """Provide standard fertilizer requirements for tests."""
    return {
        "nitrogen": 150.0,
        "phosphorus": 50.0,
        "potassium": 60.0,
    }


@pytest.fixture
def sample_equipment_availability(sample_planting_date: date) -> Dict[str, List[str]]:
    """Provide standard equipment availability for tests."""
    return {
        "spreader": [
            (sample_planting_date + timedelta(days=i)).isoformat()
            for i in range(7, 21, 3)
        ],
        "applicator": [
            (sample_planting_date + timedelta(days=i)).isoformat()
            for i in range(10, 25, 4)
        ],
    }


@pytest.fixture
def sample_labor_availability(sample_planting_date: date) -> Dict[str, int]:
    """Provide standard labor availability for tests."""
    return {
        (sample_planting_date + timedelta(days=i)).isoformat(): 2
        for i in range(7, 30, 2)
    }


@pytest.fixture
def mock_weather_service() -> MockWeatherService:
    """Provide a mock weather service for testing."""
    service = MockWeatherService()

    # Set default forecast
    forecast = [
        MockForecastDay(
            day_str=(date.today() + timedelta(days=i)).isoformat(),
            high=70.0 + i,
            low=50.0 + i,
            precip_chance=0.1 + (i * 0.05),
            precip_amount=0.0,
            wind_speed=8.0 + i,
            humidity=60.0,
        )
        for i in range(10)
    ]
    service.set_forecast(forecast)

    # Set default metrics
    metrics = MockAgriculturalMetrics()
    service.set_metrics(metrics)

    return service


@pytest.fixture
def mock_soil_service() -> MockSoilService:
    """Provide a mock soil service for testing."""
    service = MockSoilService()

    # Set default soil characteristics
    characteristics = MockSoilCharacteristics()
    service.set_soil_characteristics(characteristics)

    return service


@pytest.fixture
def high_precipitation_forecast() -> List[MockForecastDay]:
    """Provide a forecast with high precipitation for testing."""
    return [
        MockForecastDay(
            day_str=(date.today() + timedelta(days=i)).isoformat(),
            high=65.0,
            low=55.0,
            precip_chance=0.8,
            precip_amount=1.5,
            wind_speed=15.0,
            humidity=85.0,
        )
        for i in range(7)
    ]


@pytest.fixture
def dry_forecast() -> List[MockForecastDay]:
    """Provide a dry forecast for testing."""
    return [
        MockForecastDay(
            day_str=(date.today() + timedelta(days=i)).isoformat(),
            high=80.0,
            low=60.0,
            precip_chance=0.05,
            precip_amount=0.0,
            wind_speed=5.0,
            humidity=45.0,
        )
        for i in range(7)
    ]


@pytest.fixture
def windy_forecast() -> List[MockForecastDay]:
    """Provide a windy forecast for testing."""
    return [
        MockForecastDay(
            day_str=(date.today() + timedelta(days=i)).isoformat(),
            high=70.0,
            low=55.0,
            precip_chance=0.2,
            precip_amount=0.0,
            wind_speed=25.0,
            humidity=50.0,
        )
        for i in range(7)
    ]


@pytest.fixture
def clay_soil_characteristics() -> MockSoilCharacteristics:
    """Provide clay soil characteristics for testing."""
    return MockSoilCharacteristics(
        texture="silty clay",
        drainage="somewhat poorly drained",
    )


@pytest.fixture
def sandy_soil_characteristics() -> MockSoilCharacteristics:
    """Provide sandy soil characteristics for testing."""
    return MockSoilCharacteristics(
        texture="sandy loam",
        drainage="excessively drained",
    )


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def create_test_date_range(
    start_date: date,
    num_days: int,
) -> List[date]:
    """
    Create a list of dates for testing.

    Args:
        start_date: Starting date
        num_days: Number of days to generate

    Returns:
        List of dates
    """
    return [start_date + timedelta(days=i) for i in range(num_days)]


def assert_date_in_range(
    test_date: date,
    start_date: date,
    end_date: date,
) -> None:
    """
    Assert that a date falls within a specified range.

    Args:
        test_date: Date to test
        start_date: Range start (inclusive)
        end_date: Range end (inclusive)
    """
    assert start_date <= test_date <= end_date, (
        f"Date {test_date} not in range [{start_date}, {end_date}]"
    )


def assert_timing_is_reasonable(
    application_date: date,
    planting_date: date,
    max_days_after_planting: int = 90,
) -> None:
    """
    Assert that application timing is reasonable relative to planting date.

    Args:
        application_date: Proposed application date
        planting_date: Crop planting date
        max_days_after_planting: Maximum reasonable days after planting
    """
    days_after_planting = (application_date - planting_date).days

    assert days_after_planting >= 0, (
        f"Application date {application_date} is before planting date {planting_date}"
    )

    assert days_after_planting <= max_days_after_planting, (
        f"Application date {application_date} is {days_after_planting} days after "
        f"planting, exceeds maximum of {max_days_after_planting} days"
    )


def assert_confidence_score_valid(score: float) -> None:
    """
    Assert that a confidence score is valid (between 0 and 1).

    Args:
        score: Confidence score to validate
    """
    assert 0.0 <= score <= 1.0, f"Confidence score {score} not in range [0.0, 1.0]"


def assert_application_rate_reasonable(
    rate: float,
    min_rate: float = 0.0,
    max_rate: float = 500.0,
) -> None:
    """
    Assert that application rate is reasonable.

    Args:
        rate: Application rate in lbs/acre
        min_rate: Minimum reasonable rate
        max_rate: Maximum reasonable rate
    """
    assert min_rate <= rate <= max_rate, (
        f"Application rate {rate} lbs/acre not in reasonable range "
        f"[{min_rate}, {max_rate}]"
    )


# ==============================================================================
# PERFORMANCE MONITORING
# ==============================================================================

class PerformanceMonitor:
    """Monitor and record performance metrics during tests."""

    def __init__(self):
        self.measurements = []

    def record(
        self,
        test_name: str,
        duration_seconds: float,
        request_count: int = 1,
    ) -> None:
        """Record a performance measurement."""
        self.measurements.append({
            "test_name": test_name,
            "duration_seconds": duration_seconds,
            "request_count": request_count,
            "avg_time": duration_seconds / request_count,
        })

    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if not self.measurements:
            return {}

        total_requests = sum(m["request_count"] for m in self.measurements)
        total_duration = sum(m["duration_seconds"] for m in self.measurements)

        return {
            "total_tests": len(self.measurements),
            "total_requests": total_requests,
            "total_duration": total_duration,
            "avg_duration": total_duration / len(self.measurements),
            "throughput": total_requests / total_duration if total_duration > 0 else 0,
        }


@pytest.fixture
def performance_monitor() -> PerformanceMonitor:
    """Provide a performance monitor for tests."""
    return PerformanceMonitor()


# ==============================================================================
# TEST DATA GENERATORS
# ==============================================================================

def generate_crop_rotation_scenarios() -> List[Dict[str, Any]]:
    """
    Generate test scenarios for different crop rotations.

    Returns:
        List of crop rotation scenarios
    """
    return [
        {
            "name": "corn-soybean",
            "current_crop": "corn",
            "previous_crop": "soybean",
            "nitrogen_credit": 30.0,
        },
        {
            "name": "corn-corn",
            "current_crop": "corn",
            "previous_crop": "corn",
            "nitrogen_credit": 0.0,
        },
        {
            "name": "soybean-corn",
            "current_crop": "soybean",
            "previous_crop": "corn",
            "nitrogen_credit": 0.0,
        },
    ]


def generate_soil_type_scenarios() -> List[Dict[str, Any]]:
    """
    Generate test scenarios for different soil types.

    Returns:
        List of soil type scenarios
    """
    return [
        {
            "name": "sandy_loam",
            "texture": "sandy loam",
            "drainage": "well drained",
            "moisture_capacity": 0.55,
            "leaching_risk": "high",
        },
        {
            "name": "silt_loam",
            "texture": "silt loam",
            "drainage": "well drained",
            "moisture_capacity": 0.65,
            "leaching_risk": "moderate",
        },
        {
            "name": "clay_loam",
            "texture": "clay loam",
            "drainage": "moderately well drained",
            "moisture_capacity": 0.75,
            "leaching_risk": "low",
        },
        {
            "name": "silty_clay",
            "texture": "silty clay",
            "drainage": "somewhat poorly drained",
            "moisture_capacity": 0.80,
            "leaching_risk": "low",
        },
    ]


def generate_weather_scenarios() -> List[Dict[str, Any]]:
    """
    Generate test scenarios for different weather patterns.

    Returns:
        List of weather scenarios
    """
    return [
        {
            "name": "ideal_conditions",
            "description": "Ideal weather for application",
            "precip_chance": 0.1,
            "precip_amount": 0.0,
            "wind_speed": 5.0,
            "temperature": 68.0,
        },
        {
            "name": "high_precipitation",
            "description": "High precipitation risk",
            "precip_chance": 0.8,
            "precip_amount": 1.5,
            "wind_speed": 12.0,
            "temperature": 60.0,
        },
        {
            "name": "high_wind",
            "description": "High wind conditions",
            "precip_chance": 0.2,
            "precip_amount": 0.0,
            "wind_speed": 25.0,
            "temperature": 70.0,
        },
        {
            "name": "cold_conditions",
            "description": "Cold soil temperatures",
            "precip_chance": 0.3,
            "precip_amount": 0.1,
            "wind_speed": 10.0,
            "temperature": 42.0,
        },
    ]


# ==============================================================================
# AGRICULTURAL VALIDATION HELPERS
# ==============================================================================

def validate_corn_timing_rules(
    application_date: date,
    planting_date: date,
    growth_stage: str,
) -> bool:
    """
    Validate that corn timing follows agronomic principles.

    Args:
        application_date: Proposed application date
        planting_date: Planting date
        growth_stage: Target growth stage

    Returns:
        True if timing is valid for corn
    """
    days_after_planting = (application_date - planting_date).days

    # Corn growth stage timing guidelines
    stage_windows = {
        "planting": (0, 0),
        "emergence": (5, 10),
        "v2": (10, 18),
        "v4": (18, 25),
        "v6": (25, 35),
        "v10": (38, 50),
        "vt": (50, 65),
        "r1": (60, 75),
    }

    if growth_stage.lower() in stage_windows:
        min_days, max_days = stage_windows[growth_stage.lower()]
        return min_days <= days_after_planting <= max_days

    # For unknown stages, accept reasonable range
    return 0 <= days_after_planting <= 90


def validate_environmental_safety(
    slope_percent: float,
    drainage_class: str,
    soil_moisture: float,
    precipitation_forecast: float,
) -> Dict[str, Any]:
    """
    Validate environmental safety of timing recommendation.

    Args:
        slope_percent: Field slope percentage
        drainage_class: Soil drainage classification
        soil_moisture: Current soil moisture
        precipitation_forecast: Forecasted precipitation

    Returns:
        Dictionary with safety assessment
    """
    concerns = []
    risk_level = "low"

    # Check slope and runoff risk
    if slope_percent > 5.0:
        concerns.append("High slope increases runoff risk")
        risk_level = "moderate"

    if slope_percent > 8.0:
        concerns.append("Very high slope - critical runoff risk")
        risk_level = "high"

    # Check drainage and leaching risk
    if "poor" in drainage_class.lower() and soil_moisture > 0.7:
        concerns.append("Poor drainage with high moisture increases leaching risk")
        risk_level = "high" if risk_level != "high" else risk_level

    # Check precipitation risk
    if precipitation_forecast > 1.0:
        concerns.append("Heavy precipitation forecast increases loss risk")
        risk_level = "high"

    return {
        "risk_level": risk_level,
        "concerns": concerns,
        "safe_to_apply": risk_level != "high",
    }
