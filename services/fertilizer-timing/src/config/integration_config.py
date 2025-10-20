"""
Integration configuration for service-to-service communication.

This module provides configuration settings for HTTP-based communication
between the fertilizer-timing service and other CAAIN Soil Hub services.
"""

import os
from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel, Field


class IntegrationMode(str, Enum):
    """Integration mode for service communication."""
    DIRECT_IMPORT = "direct_import"  # Legacy mode using Python imports
    REST_API = "rest_api"  # Modern mode using HTTP REST APIs
    HYBRID = "hybrid"  # Try REST API first, fallback to direct import


class ServiceConfig(BaseModel):
    """Configuration for a single external service."""
    name: str = Field(..., description="Service name")
    base_url: str = Field(..., description="Base URL for the service API")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum number of retry attempts")
    retry_delay: float = Field(default=1.0, description="Initial retry delay in seconds")
    circuit_breaker_threshold: int = Field(
        default=5, description="Number of failures before opening circuit"
    )
    circuit_breaker_timeout: int = Field(
        default=60, description="Circuit breaker timeout in seconds"
    )
    health_check_path: str = Field(
        default="/health", description="Health check endpoint path"
    )


class IntegrationConfig(BaseModel):
    """Main integration configuration."""
    mode: IntegrationMode = Field(
        default=IntegrationMode.HYBRID,
        description="Integration mode for service communication"
    )
    enable_request_logging: bool = Field(
        default=True, description="Enable request/response logging"
    )
    enable_circuit_breaker: bool = Field(
        default=True, description="Enable circuit breaker pattern"
    )
    enable_retry: bool = Field(
        default=True, description="Enable retry logic with exponential backoff"
    )
    services: Dict[str, ServiceConfig] = Field(
        default_factory=dict, description="Service-specific configurations"
    )


def load_integration_config() -> IntegrationConfig:
    """
    Load integration configuration from environment variables.

    Returns:
        IntegrationConfig: Configured integration settings
    """
    # Get integration mode from environment
    mode_str = os.getenv("INTEGRATION_MODE", "hybrid")
    try:
        mode = IntegrationMode(mode_str.lower())
    except ValueError:
        mode = IntegrationMode.HYBRID

    # Configure fertilizer-strategy service
    fertilizer_strategy_config = ServiceConfig(
        name="fertilizer-strategy",
        base_url=os.getenv(
            "FERTILIZER_STRATEGY_URL",
            "http://localhost:8009"
        ),
        timeout=int(os.getenv("FERTILIZER_STRATEGY_TIMEOUT", "30")),
        max_retries=int(os.getenv("FERTILIZER_STRATEGY_MAX_RETRIES", "3")),
        retry_delay=float(os.getenv("FERTILIZER_STRATEGY_RETRY_DELAY", "1.0")),
        circuit_breaker_threshold=int(
            os.getenv("FERTILIZER_STRATEGY_CIRCUIT_BREAKER_THRESHOLD", "5")
        ),
        circuit_breaker_timeout=int(
            os.getenv("FERTILIZER_STRATEGY_CIRCUIT_BREAKER_TIMEOUT", "60")
        ),
        health_check_path=os.getenv("FERTILIZER_STRATEGY_HEALTH_PATH", "/health")
    )

    # Configure weather service
    weather_service_config = ServiceConfig(
        name="weather-service",
        base_url=os.getenv("WEATHER_SERVICE_URL", "http://localhost:8001"),
        timeout=int(os.getenv("WEATHER_SERVICE_TIMEOUT", "15")),
        max_retries=int(os.getenv("WEATHER_SERVICE_MAX_RETRIES", "3")),
    )

    # Configure soil service
    soil_service_config = ServiceConfig(
        name="soil-service",
        base_url=os.getenv("SOIL_SERVICE_URL", "http://localhost:8002"),
        timeout=int(os.getenv("SOIL_SERVICE_TIMEOUT", "15")),
        max_retries=int(os.getenv("SOIL_SERVICE_MAX_RETRIES", "3")),
    )

    # Configure crop management service
    crop_service_config = ServiceConfig(
        name="crop-management",
        base_url=os.getenv("CROP_SERVICE_URL", "http://localhost:8003"),
        timeout=int(os.getenv("CROP_SERVICE_TIMEOUT", "15")),
        max_retries=int(os.getenv("CROP_SERVICE_MAX_RETRIES", "3")),
    )

    return IntegrationConfig(
        mode=mode,
        enable_request_logging=os.getenv("ENABLE_REQUEST_LOGGING", "true").lower() == "true",
        enable_circuit_breaker=os.getenv("ENABLE_CIRCUIT_BREAKER", "true").lower() == "true",
        enable_retry=os.getenv("ENABLE_RETRY", "true").lower() == "true",
        services={
            "fertilizer-strategy": fertilizer_strategy_config,
            "weather-service": weather_service_config,
            "soil-service": soil_service_config,
            "crop-management": crop_service_config,
        }
    )


# Global configuration instance
integration_config = load_integration_config()


__all__ = [
    "IntegrationMode",
    "ServiceConfig",
    "IntegrationConfig",
    "load_integration_config",
    "integration_config",
]
