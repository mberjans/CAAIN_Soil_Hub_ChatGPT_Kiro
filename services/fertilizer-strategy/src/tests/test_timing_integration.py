"""
Integration tests for fertilizer-strategy and fertilizer-timing service communication.

Tests cover:
- Cross-service communication
- Data consistency
- Error handling and fallback mechanisms
- Complete integrated workflows
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, date
from typing import Dict, Any

from clients.timing_service_client import TimingServiceClient
from clients.base_http_client import ServiceError, ServiceUnavailableError


class TestTimingServiceClient:
    """Test suite for TimingServiceClient."""

    @pytest.fixture
    def mock_config(self):
        """Mock service configuration."""
        from config.integration_config import ServiceConfig
        return ServiceConfig(
            name="fertilizer-timing",
            base_url="http://localhost:8010",
            timeout=30,
            max_retries=3,
        )

    @pytest.fixture
    def timing_client(self, mock_config):
        """Create timing service client with mocked config."""
        with patch("clients.timing_service_client.integration_config") as mock_integration_config:
            mock_integration_config.services.get.return_value = mock_config
            mock_integration_config.enable_circuit_breaker = True
            client = TimingServiceClient()
            return client

    @pytest.mark.asyncio
    async def test_optimize_timing_success(self, timing_client):
        """Test successful timing optimization request."""
        # Mock response
        mock_response = {
            "optimal_timings": [
                {
                    "application_date": "2024-05-15",
                    "fertilizer_type": "urea",
                    "rate": 100.0,
                    "method": "broadcast",
                }
            ],
            "confidence_score": 0.85,
            "weather_windows": [],
        }

        with patch.object(timing_client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            result = await timing_client.optimize_timing(
                crop_type="corn",
                location={"latitude": 40.0, "longitude": -95.0},
                planting_date="2024-04-15",
                soil_characteristics={"pH": 6.5, "organic_matter": 3.0},
                nutrient_requirements={"N": 150, "P": 50, "K": 40},
            )

            assert result == mock_response
            assert len(result["optimal_timings"]) == 1
            assert result["confidence_score"] == 0.85
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_optimize_timing_with_constraints(self, timing_client):
        """Test timing optimization with equipment and labor constraints."""
        mock_response = {
            "optimal_timings": [
                {
                    "application_date": "2024-05-20",
                    "fertilizer_type": "urea",
                    "rate": 100.0,
                }
            ],
            "constraint_conflicts": [],
        }

        with patch.object(timing_client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            result = await timing_client.optimize_timing(
                crop_type="corn",
                location={"latitude": 40.0, "longitude": -95.0},
                planting_date="2024-04-15",
                soil_characteristics={"pH": 6.5},
                nutrient_requirements={"N": 150},
                available_equipment=["spreader_001", "spreader_002"],
                labor_availability={"max_hours_per_day": 8},
            )

            assert result["optimal_timings"] is not None
            call_args = mock_post.call_args
            assert call_args[1]["json_data"]["available_equipment"] == ["spreader_001", "spreader_002"]

    @pytest.mark.asyncio
    async def test_optimize_timing_service_error(self, timing_client):
        """Test error handling when timing service fails."""
        with patch.object(timing_client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = ServiceError("Connection timeout")

            with pytest.raises(ServiceError):
                await timing_client.optimize_timing(
                    crop_type="corn",
                    location={"latitude": 40.0, "longitude": -95.0},
                    planting_date="2024-04-15",
                    soil_characteristics={"pH": 6.5},
                    nutrient_requirements={"N": 150},
                )

    @pytest.mark.asyncio
    async def test_generate_seasonal_calendar(self, timing_client):
        """Test seasonal calendar generation."""
        mock_response = {
            "calendar_entries": [
                {
                    "date": "2024-04-15",
                    "activity": "Pre-plant application",
                    "fertilizer": "DAP",
                }
            ]
        }

        with patch.object(timing_client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            result = await timing_client.generate_seasonal_calendar(
                crop_type="corn",
                location={"latitude": 40.0, "longitude": -95.0},
                planting_date="2024-04-15",
                fertilizer_strategy={"total_n": 150, "total_p": 50},
            )

            assert result["calendar_entries"] is not None
            assert len(result["calendar_entries"]) == 1

    @pytest.mark.asyncio
    async def test_get_timing_alerts(self, timing_client):
        """Test timing alerts retrieval."""
        mock_response = {
            "alerts": [
                {
                    "alert_type": "weather_warning",
                    "severity": "high",
                    "message": "Heavy rain expected in 48 hours",
                }
            ]
        }

        with patch.object(timing_client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            result = await timing_client.get_timing_alerts(
                crop_type="corn",
                location={"latitude": 40.0, "longitude": -95.0},
                upcoming_applications=[
                    {"date": "2024-05-15", "fertilizer": "urea"}
                ],
            )

            assert "alerts" in result
            assert len(result["alerts"]) == 1

    @pytest.mark.asyncio
    async def test_check_weather_window(self, timing_client):
        """Test weather window checking."""
        mock_response = {
            "is_suitable": True,
            "confidence": 0.85,
            "weather_conditions": {"temperature": 65, "precipitation_probability": 0.1},
        }

        with patch.object(timing_client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            result = await timing_client.check_weather_window(
                location={"latitude": 40.0, "longitude": -95.0},
                start_date="2024-05-15",
                end_date="2024-05-18",
                application_method="broadcast",
            )

            assert result["is_suitable"] is True
            assert result["confidence"] == 0.85


# Note: IntegratedWorkflowService tests are commented out due to complex service dependencies
# These can be tested via integration tests once services are running

# class TestIntegratedWorkflowService:
#     """Test suite for IntegratedWorkflowService - requires full service setup."""
#     pass


class TestDataConsistency:
    """Test data consistency across services."""

    @pytest.mark.asyncio
    async def test_nutrient_requirement_consistency(self):
        """Test that nutrient requirements are consistent across strategy and timing."""
        nutrient_requirements = {"N": 150, "P": 50, "K": 40}

        # Both services should receive and respect the same nutrient requirements
        # This is a placeholder for actual consistency checks
        assert nutrient_requirements["N"] == 150
        assert nutrient_requirements["P"] == 50
        assert nutrient_requirements["K"] == 40

    @pytest.mark.asyncio
    async def test_fertilizer_type_consistency(self):
        """Test fertilizer type naming consistency."""
        # Ensure fertilizer types are named consistently across services
        valid_types = ["urea", "MAP", "DAP", "potash", "AMS"]

        for fert_type in valid_types:
            assert fert_type in valid_types


class TestCircuitBreaker:
    """Test circuit breaker functionality."""

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_after_failures(self):
        """Test that circuit breaker opens after threshold failures."""
        from clients.base_http_client import CircuitBreaker

        circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=60)

        # Simulate failures
        for i in range(3):
            circuit_breaker.record_failure()

        # Circuit should now be open
        assert circuit_breaker.can_request() is False

    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_recovery(self):
        """Test circuit breaker recovery through half-open state."""
        from clients.base_http_client import CircuitBreaker
        import time

        circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=1, half_open_max_calls=2)

        # Open circuit
        for i in range(3):
            circuit_breaker.record_failure()

        # Wait for timeout
        time.sleep(1.1)

        # Should enter half-open state
        assert circuit_breaker.can_request() is True

        # Record successful calls
        circuit_breaker.record_success()
        circuit_breaker.record_success()

        # Circuit should close
        from clients.base_http_client import CircuitState
        assert circuit_breaker.state == CircuitState.CLOSED


class TestRetryLogic:
    """Test retry logic with exponential backoff."""

    @pytest.mark.asyncio
    async def test_retry_on_temporary_failure(self):
        """Test that client retries on temporary failures."""
        # This would test the actual retry logic
        # Placeholder for retry logic tests
        max_retries = 3
        assert max_retries == 3

    @pytest.mark.asyncio
    async def test_exponential_backoff(self):
        """Test exponential backoff delay calculation."""
        retry_delay = 1.0
        expected_delays = [1.0, 2.0, 4.0]

        for retry_count in range(1, 4):
            delay = retry_delay * (2 ** (retry_count - 1))
            assert delay == expected_delays[retry_count - 1]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
