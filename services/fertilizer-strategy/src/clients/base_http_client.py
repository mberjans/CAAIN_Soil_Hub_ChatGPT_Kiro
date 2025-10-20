"""
Base HTTP client with retry logic, circuit breaker, and error handling.

This module provides a foundational HTTP client that can be extended for
specific service integrations. It includes:
- Exponential backoff retry logic
- Circuit breaker pattern for resilience
- Request/response logging
- Standardized error handling
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from enum import Enum
from typing import Any, Dict, Optional, Type, TypeVar, Union

import httpx
from pydantic import BaseModel

from config.integration_config import ServiceConfig

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Circuit is open, requests fail fast
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker implementation for service resilience.

    The circuit breaker prevents cascading failures by temporarily blocking
    requests to a failing service.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        half_open_max_calls: int = 3,
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before attempting recovery
            half_open_max_calls: Max calls to allow in half-open state
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.half_open_max_calls = half_open_max_calls

        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = CircuitState.CLOSED
        self.half_open_calls = 0

    def record_success(self) -> None:
        """Record a successful request."""
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_calls += 1
            if self.half_open_calls >= self.half_open_max_calls:
                logger.info("Circuit breaker: Closing circuit after successful recovery")
                self._close()
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            if self.failure_count > 0:
                self.failure_count = 0

    def record_failure(self) -> None:
        """Record a failed request."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            logger.warning("Circuit breaker: Failure in half-open state, reopening circuit")
            self._open()
        elif self.failure_count >= self.failure_threshold:
            logger.warning(
                f"Circuit breaker: Opening circuit after {self.failure_count} failures"
            )
            self._open()

    def can_request(self) -> bool:
        """
        Check if a request can be made.

        Returns:
            bool: True if request is allowed, False otherwise
        """
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                logger.info("Circuit breaker: Entering half-open state to test recovery")
                self._half_open()
                return True
            return False

        # HALF_OPEN state
        return self.half_open_calls < self.half_open_max_calls

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time >= self.timeout

    def _open(self) -> None:
        """Open the circuit."""
        self.state = CircuitState.OPEN
        self.half_open_calls = 0

    def _close(self) -> None:
        """Close the circuit."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.half_open_calls = 0

    def _half_open(self) -> None:
        """Enter half-open state."""
        self.state = CircuitState.HALF_OPEN
        self.half_open_calls = 0


class ServiceUnavailableError(Exception):
    """Raised when a service is unavailable (circuit breaker open)."""
    pass


class ServiceError(Exception):
    """Base exception for service communication errors."""
    pass


class BaseHTTPClient:
    """
    Base HTTP client with resilience patterns.

    Features:
    - Async HTTP requests using httpx
    - Exponential backoff retry logic
    - Circuit breaker pattern
    - Request/response logging
    - Standardized error handling
    """

    def __init__(self, config: ServiceConfig, enable_circuit_breaker: bool = True):
        """
        Initialize HTTP client.

        Args:
            config: Service configuration
            enable_circuit_breaker: Whether to enable circuit breaker
        """
        self.config = config
        self.service_name = config.name
        self.base_url = config.base_url.rstrip("/")

        # Circuit breaker
        self.circuit_breaker: Optional[CircuitBreaker] = None
        if enable_circuit_breaker:
            self.circuit_breaker = CircuitBreaker(
                failure_threshold=config.circuit_breaker_threshold,
                timeout=config.circuit_breaker_timeout,
            )

        # HTTP client will be created in async context
        self._client: Optional[httpx.AsyncClient] = None

    @asynccontextmanager
    async def _get_client(self):
        """
        Get or create async HTTP client.

        Yields:
            httpx.AsyncClient: Configured HTTP client
        """
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.config.timeout),
                follow_redirects=True,
            )
        try:
            yield self._client
        finally:
            # Keep client alive for connection pooling
            pass

    async def close(self) -> None:
        """Close the HTTP client and release resources."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def _make_request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """
        Make an HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path (will be appended to base_url)
            params: Query parameters
            json_data: JSON request body
            headers: Additional headers

        Returns:
            httpx.Response: HTTP response

        Raises:
            ServiceUnavailableError: If circuit breaker is open
            ServiceError: On communication errors
        """
        # Check circuit breaker
        if self.circuit_breaker and not self.circuit_breaker.can_request():
            raise ServiceUnavailableError(
                f"Service {self.service_name} is unavailable (circuit breaker open)"
            )

        url = f"{self.base_url}{path}"
        retry_count = 0
        last_exception: Optional[Exception] = None

        while retry_count <= self.config.max_retries:
            try:
                async with self._get_client() as client:
                    logger.debug(
                        f"[{self.service_name}] {method} {url} "
                        f"(attempt {retry_count + 1}/{self.config.max_retries + 1})"
                    )

                    response = await client.request(
                        method=method,
                        url=url,
                        params=params,
                        json=json_data,
                        headers=headers,
                    )

                    # Check response status
                    if response.is_success:
                        # Record success with circuit breaker
                        if self.circuit_breaker:
                            self.circuit_breaker.record_success()

                        logger.debug(
                            f"[{self.service_name}] {method} {url} -> {response.status_code}"
                        )
                        return response

                    # Handle HTTP errors
                    if response.status_code >= 500:
                        # Server error - retry
                        raise httpx.HTTPStatusError(
                            f"Server error: {response.status_code}",
                            request=response.request,
                            response=response,
                        )
                    else:
                        # Client error - don't retry
                        logger.warning(
                            f"[{self.service_name}] Client error {response.status_code}: {response.text}"
                        )
                        response.raise_for_status()

            except (httpx.HTTPError, httpx.HTTPStatusError) as e:
                last_exception = e
                retry_count += 1

                if retry_count <= self.config.max_retries:
                    # Calculate exponential backoff delay
                    delay = self.config.retry_delay * (2 ** (retry_count - 1))
                    logger.warning(
                        f"[{self.service_name}] Request failed: {e}. "
                        f"Retrying in {delay:.2f}s (attempt {retry_count}/{self.config.max_retries})"
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"[{self.service_name}] Request failed after {retry_count} attempts: {e}"
                    )

        # All retries exhausted
        if self.circuit_breaker:
            self.circuit_breaker.record_failure()

        raise ServiceError(
            f"Failed to communicate with {self.service_name} after "
            f"{self.config.max_retries + 1} attempts: {last_exception}"
        )

    async def get(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        response_model: Optional[Type[T]] = None,
    ) -> Union[Dict[str, Any], T]:
        """
        Make a GET request.

        Args:
            path: API path
            params: Query parameters
            headers: Additional headers
            response_model: Pydantic model to parse response

        Returns:
            Parsed response data or model instance
        """
        response = await self._make_request("GET", path, params=params, headers=headers)
        data = response.json()

        if response_model:
            return response_model(**data)
        return data

    async def post(
        self,
        path: str,
        *,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        response_model: Optional[Type[T]] = None,
    ) -> Union[Dict[str, Any], T]:
        """
        Make a POST request.

        Args:
            path: API path
            json_data: JSON request body
            params: Query parameters
            headers: Additional headers
            response_model: Pydantic model to parse response

        Returns:
            Parsed response data or model instance
        """
        response = await self._make_request(
            "POST", path, params=params, json_data=json_data, headers=headers
        )
        data = response.json()

        if response_model:
            return response_model(**data)
        return data

    async def health_check(self) -> bool:
        """
        Check service health.

        Returns:
            bool: True if service is healthy, False otherwise
        """
        try:
            response = await self._make_request("GET", self.config.health_check_path)
            return response.is_success
        except (ServiceError, ServiceUnavailableError):
            return False


__all__ = [
    "BaseHTTPClient",
    "CircuitBreaker",
    "CircuitState",
    "ServiceError",
    "ServiceUnavailableError",
]
