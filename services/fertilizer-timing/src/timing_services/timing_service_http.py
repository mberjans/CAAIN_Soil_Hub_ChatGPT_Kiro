"""
HTTP-based timing optimization adapter for the fertilizer timing microservice.

This module provides an adapter that uses REST API calls to the fertilizer-strategy
service instead of direct Python imports, enabling loose coupling between services.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from clients.fertilizer_strategy_client import FertilizerStrategyClient
from clients.base_http_client import ServiceError, ServiceUnavailableError
from config.integration_config import integration_config, IntegrationMode
from models import (
    ApplicationTiming,
    SplitApplicationPlan,
    TimingOptimizationRequest,
    TimingOptimizationResult,
    WeatherWindow,
)

logger = logging.getLogger(__name__)


class TimingOptimizationHTTPAdapter:
    """
    HTTP-based adapter for timing optimization.

    This adapter communicates with the fertilizer-strategy service via REST API,
    providing the same interface as the direct import adapter but with loose coupling.

    Features:
    - REST API communication with fertilizer-strategy service
    - Automatic retry and circuit breaker support
    - Graceful degradation to direct import mode (if configured)
    - Request/response logging
    """

    def __init__(self) -> None:
        """Initialize HTTP-based timing optimization adapter."""
        self._http_client: Optional[FertilizerStrategyClient] = None
        self._direct_import_adapter: Optional[any] = None

        # Initialize HTTP client
        try:
            self._http_client = FertilizerStrategyClient()
            logger.info("Initialized HTTP-based timing optimization adapter")
        except Exception as e:
            logger.warning(f"Failed to initialize HTTP client: {e}")

        # Initialize fallback adapter if in hybrid mode
        if integration_config.mode == IntegrationMode.HYBRID:
            try:
                from timing_services.timing_service import TimingOptimizationAdapter
                self._direct_import_adapter = TimingOptimizationAdapter()
                logger.info("Initialized fallback direct import adapter for hybrid mode")
            except Exception as e:
                logger.warning(f"Failed to initialize fallback adapter: {e}")

    async def optimize(
        self, request: TimingOptimizationRequest
    ) -> TimingOptimizationResult:
        """
        Run full optimization for the provided request.

        Args:
            request: Timing optimization request parameters

        Returns:
            TimingOptimizationResult: Optimization results

        Raises:
            ServiceError: On communication or processing errors
        """
        # Try HTTP client first
        if self._http_client and integration_config.mode in [
            IntegrationMode.REST_API,
            IntegrationMode.HYBRID,
        ]:
            try:
                logger.debug("Attempting timing optimization via HTTP API")
                result = await self._http_client.optimize_timing(request)
                logger.info("Successfully obtained timing optimization via HTTP API")
                return result

            except (ServiceError, ServiceUnavailableError) as e:
                logger.warning(f"HTTP API optimization failed: {e}")

                # If in hybrid mode, fall back to direct import
                if integration_config.mode == IntegrationMode.HYBRID:
                    logger.info("Falling back to direct import mode")
                else:
                    # In REST_API mode, don't fallback - raise error
                    raise

        # Use direct import (either as primary mode or fallback)
        if self._direct_import_adapter:
            logger.debug("Using direct import adapter for timing optimization")
            return await self._direct_import_adapter.optimize(request)

        raise ServiceError(
            "No available timing optimization method (HTTP and direct import both unavailable)"
        )

    async def analyze_weather_windows(
        self, request: TimingOptimizationRequest
    ) -> List[WeatherWindow]:
        """
        Delegate to the optimizer's weather analysis.

        Args:
            request: Timing optimization request

        Returns:
            List of weather windows suitable for application

        Note:
            This method extracts weather windows from the full optimization result.
            In HTTP mode, we make a full optimization call as there's no dedicated
            weather window endpoint.
        """
        # Get full optimization result
        result = await self.optimize(request)

        # Extract weather windows from result
        return result.weather_windows if hasattr(result, "weather_windows") else []

    async def determine_crop_stages(
        self, request: TimingOptimizationRequest
    ) -> Dict[str, str]:
        """
        Return crop growth stage timeline as ISO date strings.

        Args:
            request: Timing optimization request

        Returns:
            Dict mapping stage names to ISO date strings

        Note:
            Extracts crop stage information from optimization results.
        """
        # Try HTTP mode first
        if self._http_client and integration_config.mode in [
            IntegrationMode.REST_API,
            IntegrationMode.HYBRID,
        ]:
            try:
                # Get full optimization to extract crop stages
                result = await self.optimize(request)

                # Extract crop stage timeline from result
                # This assumes the result includes crop stage information
                timeline: Dict[str, str] = {}

                # Extract from optimal timings
                for timing in result.optimal_timings:
                    if hasattr(timing, "crop_stage") and timing.crop_stage:
                        if hasattr(timing, "recommended_date"):
                            timeline[timing.crop_stage] = timing.recommended_date

                return timeline

            except (ServiceError, ServiceUnavailableError):
                if integration_config.mode != IntegrationMode.HYBRID:
                    raise

        # Fallback to direct import
        if self._direct_import_adapter:
            return await self._direct_import_adapter.determine_crop_stages(request)

        return {}

    async def optimize_split_applications(
        self, request: TimingOptimizationRequest
    ) -> List[SplitApplicationPlan]:
        """
        Generate split application plans.

        Args:
            request: Timing optimization request

        Returns:
            List of split application plans
        """
        result = await self.optimize(request)
        return result.split_plans if hasattr(result, "split_plans") else []

    async def quick_optimize(
        self, request: TimingOptimizationRequest
    ) -> TimingOptimizationResult:
        """
        Alias for optimize, kept for semantic clarity.

        Args:
            request: Timing optimization request

        Returns:
            TimingOptimizationResult: Optimization results
        """
        return await self.optimize(request)

    async def summarize(
        self, request: TimingOptimizationRequest
    ) -> Dict[str, ApplicationTiming]:
        """
        Provide a mapping of fertilizer type to primary application recommendation.

        Args:
            request: Timing optimization request

        Returns:
            Dict mapping fertilizer types to application timings
        """
        result = await self.optimize(request)
        summary: Dict[str, ApplicationTiming] = {}

        for timing in result.optimal_timings:
            fertilizer_key = timing.fertilizer_type
            if fertilizer_key not in summary:
                summary[fertilizer_key] = timing

        return summary

    async def close(self) -> None:
        """Close HTTP client and release resources."""
        if self._http_client:
            await self._http_client.close()
            logger.info("Closed HTTP client")


__all__ = ["TimingOptimizationHTTPAdapter"]
