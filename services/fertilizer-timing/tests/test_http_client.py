"""
Unit tests for HTTP client infrastructure.

Tests cover:
- Circuit breaker functionality
- Retry logic with exponential backoff
- Error handling
- Request/response processing
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import httpx

from clients.base_http_client import (
    BaseHTTPClient,
    CircuitBreaker,
    CircuitState,
    ServiceError,
    ServiceUnavailableError,
)
from config.integration_config import ServiceConfig


class TestCircuitBreaker:
    """Test circuit breaker functionality."""

    def test_initial_state_closed(self):
        """Test circuit breaker starts in closed state."""
        cb = CircuitBreaker(failure_threshold=3, timeout=60)
        assert cb.state == CircuitState.CLOSED
        assert cb.can_request() is True

    def test_open_after_threshold_failures(self):
        """Test circuit opens after reaching failure threshold."""
        cb = CircuitBreaker(failure_threshold=3, timeout=60)

        # Record failures
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED

        cb.record_failure()
        assert cb.state == CircuitState.CLOSED

        cb.record_failure()
        assert cb.state == CircuitState.OPEN
        assert cb.can_request() is False

    def test_reset_on_success(self):
        """Test failure count resets on successful request."""
        cb = CircuitBreaker(failure_threshold=3, timeout=60)

        cb.record_failure()
        cb.record_failure()
        assert cb.failure_count == 2

        cb.record_success()
        assert cb.failure_count == 0

    def test_half_open_after_timeout(self):
        """Test circuit enters half-open state after timeout."""
        cb = CircuitBreaker(failure_threshold=2, timeout=1)

        # Open circuit
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.OPEN

        # Wait for timeout
        import time
        time.sleep(1.1)

        # Should allow request in half-open state
        assert cb.can_request() is True
        assert cb.state == CircuitState.HALF_OPEN

    def test_close_after_successful_half_open(self):
        """Test circuit closes after successful requests in half-open."""
        cb = CircuitBreaker(failure_threshold=2, timeout=1, half_open_max_calls=2)

        # Open circuit
        cb.record_failure()
        cb.record_failure()

        # Wait and enter half-open
        import time
        time.sleep(1.1)
        cb.can_request()

        # Successful requests in half-open
        cb.record_success()
        assert cb.state == CircuitState.HALF_OPEN

        cb.record_success()
        assert cb.state == CircuitState.CLOSED

    def test_reopen_on_half_open_failure(self):
        """Test circuit reopens on failure in half-open state."""
        cb = CircuitBreaker(failure_threshold=2, timeout=1)

        # Open circuit
        cb.record_failure()
        cb.record_failure()

        # Enter half-open
        import time
        time.sleep(1.1)
        cb.can_request()
        assert cb.state == CircuitState.HALF_OPEN

        # Failure in half-open reopens circuit
        cb.record_failure()
        assert cb.state == CircuitState.OPEN


class TestBaseHTTPClient:
    """Test base HTTP client functionality."""

    @pytest.fixture
    def service_config(self):
        """Create test service configuration."""
        return ServiceConfig(
            name="test-service",
            base_url="http://localhost:8000",
            timeout=5,
            max_retries=2,
            retry_delay=0.1,
            circuit_breaker_threshold=3,
        )

    @pytest.fixture
    def http_client(self, service_config):
        """Create HTTP client instance."""
        return BaseHTTPClient(config=service_config, enable_circuit_breaker=True)

    @pytest.mark.asyncio
    async def test_successful_get_request(self, http_client):
        """Test successful GET request."""
        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}

        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await http_client.get("/test", params={"key": "value"})

            assert result == {"status": "ok"}
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_successful_post_request(self, http_client):
        """Test successful POST request."""
        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 123}

        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await http_client.post(
                "/create",
                json_data={"name": "test"}
            )

            assert result == {"id": 123}

    @pytest.mark.asyncio
    async def test_retry_on_server_error(self, http_client):
        """Test retry logic on server errors."""
        # First call fails, second succeeds
        fail_response = MagicMock()
        fail_response.is_success = False
        fail_response.status_code = 500
        fail_response.request = MagicMock()

        success_response = MagicMock()
        success_response.is_success = True
        success_response.status_code = 200
        success_response.json.return_value = {"status": "ok"}

        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = [
                httpx.HTTPStatusError("Server error", request=MagicMock(), response=fail_response),
                success_response
            ]

            result = await http_client.get("/test")

            assert result == {"status": "ok"}
            assert mock_request.call_count == 2

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_on_failures(self, http_client):
        """Test circuit breaker opens after multiple failures."""
        fail_response = MagicMock()
        fail_response.is_success = False
        fail_response.status_code = 500
        fail_response.request = MagicMock()

        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = httpx.HTTPStatusError(
                "Server error",
                request=MagicMock(),
                response=fail_response
            )

            # Make requests until circuit opens
            for _ in range(3):
                try:
                    await http_client.get("/test")
                except ServiceError:
                    pass

            # Circuit should be open now
            assert http_client.circuit_breaker.state == CircuitState.OPEN

            # Next request should fail fast
            with pytest.raises(ServiceUnavailableError):
                await http_client.get("/test")

    @pytest.mark.asyncio
    async def test_health_check_success(self, http_client):
        """Test successful health check."""
        mock_response = MagicMock()
        mock_response.is_success = True

        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await http_client.health_check()

            assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, http_client):
        """Test failed health check."""
        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = httpx.ConnectError("Connection failed")

            result = await http_client.health_check()

            assert result is False

    @pytest.mark.asyncio
    async def test_client_cleanup(self, http_client):
        """Test HTTP client cleanup."""
        # Create a client connection
        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json.return_value = {}

        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock):
            await http_client.get("/test")

        # Close should work without errors
        await http_client.close()
        assert http_client._client is None


class TestExponentialBackoff:
    """Test exponential backoff retry logic."""

    @pytest.mark.asyncio
    async def test_exponential_delay_calculation(self):
        """Test exponential backoff delay calculation."""
        config = ServiceConfig(
            name="test",
            base_url="http://localhost:8000",
            max_retries=3,
            retry_delay=1.0,
        )
        client = BaseHTTPClient(config=config, enable_circuit_breaker=False)

        delays = []

        async def mock_sleep(delay):
            delays.append(delay)

        fail_response = MagicMock()
        fail_response.is_success = False
        fail_response.status_code = 500
        fail_response.request = MagicMock()

        with patch.object(httpx.AsyncClient, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = httpx.HTTPStatusError(
                "Server error",
                request=MagicMock(),
                response=fail_response
            )

            with patch('asyncio.sleep', new=mock_sleep):
                try:
                    await client.get("/test")
                except ServiceError:
                    pass

        # Check exponential backoff: 1.0, 2.0, 4.0
        assert len(delays) == 3
        assert delays[0] == 1.0
        assert delays[1] == 2.0
        assert delays[2] == 4.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
