"""
HTTP client for fertilizer-strategy service communication.

This module provides async HTTP client for interacting with the fertilizer-strategy
service REST API, enabling loose coupling between services.
"""

import logging
from typing import Dict, List, Optional

from clients.base_http_client import BaseHTTPClient, ServiceError
from config.integration_config import integration_config
from models import (
    TimingOptimizationRequest,
    TimingOptimizationResult,
    ApplicationMethod,
    FertilizerType,
)

logger = logging.getLogger(__name__)


class FertilizerStrategyClient(BaseHTTPClient):
    """
    HTTP client for fertilizer-strategy service.

    Provides methods for:
    - Timing optimization requests
    - Equipment compatibility checking
    - Fertilizer pricing data retrieval
    - Type selection recommendations
    """

    def __init__(self):
        """Initialize fertilizer-strategy HTTP client."""
        config = integration_config.services.get("fertilizer-strategy")
        if not config:
            raise ValueError("Fertilizer-strategy service configuration not found")

        super().__init__(
            config=config,
            enable_circuit_breaker=integration_config.enable_circuit_breaker,
        )

    async def optimize_timing(
        self, request: TimingOptimizationRequest
    ) -> TimingOptimizationResult:
        """
        Request timing optimization from fertilizer-strategy service.

        Args:
            request: Timing optimization request parameters

        Returns:
            TimingOptimizationResult: Optimization results

        Raises:
            ServiceError: On communication or processing errors
        """
        try:
            logger.info(
                f"Requesting timing optimization for crop {request.crop_type} "
                f"at location ({request.location.latitude}, {request.location.longitude})"
            )

            response_data = await self.post(
                path="/api/v1/strategy/timing-recommendations",
                json_data=request.model_dump(mode="json"),
            )

            result = TimingOptimizationResult(**response_data)
            logger.info(
                f"Received {len(result.optimal_timings)} timing recommendations "
                f"with confidence score {result.confidence_score:.2f}"
            )

            return result

        except Exception as e:
            logger.error(f"Failed to get timing optimization: {e}")
            raise ServiceError(f"Timing optimization request failed: {e}")

    async def check_equipment_compatibility(
        self,
        fertilizer_type: str,
        application_method: str,
        available_equipment: List[str],
    ) -> Dict[str, List[str]]:
        """
        Check equipment compatibility for fertilizer application.

        Args:
            fertilizer_type: Type of fertilizer
            application_method: Application method
            available_equipment: List of available equipment IDs

        Returns:
            Dict with compatible_equipment and incompatible_equipment lists

        Raises:
            ServiceError: On communication errors
        """
        try:
            logger.debug(
                f"Checking equipment compatibility for {fertilizer_type} "
                f"using {application_method}"
            )

            response_data = await self.post(
                path="/api/v1/strategy/equipment-compatibility",
                json_data={
                    "fertilizer_type": fertilizer_type,
                    "application_method": application_method,
                    "equipment_list": available_equipment,
                },
            )

            return {
                "compatible_equipment": response_data.get("compatible_equipment", []),
                "incompatible_equipment": response_data.get("incompatible_equipment", []),
            }

        except Exception as e:
            logger.error(f"Equipment compatibility check failed: {e}")
            raise ServiceError(f"Equipment compatibility request failed: {e}")

    async def get_current_prices(
        self,
        fertilizer_type: Optional[str] = None,
        location: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Dict[str, any]]:
        """
        Get current fertilizer prices.

        Args:
            fertilizer_type: Optional specific fertilizer type
            location: Optional location dict with lat/lng for regional pricing

        Returns:
            Dict mapping fertilizer types to price information

        Raises:
            ServiceError: On communication errors
        """
        try:
            params = {}
            if fertilizer_type:
                params["fertilizer_type"] = fertilizer_type
            if location:
                params["latitude"] = location.get("latitude")
                params["longitude"] = location.get("longitude")

            logger.debug(f"Fetching current fertilizer prices: {params}")

            response_data = await self.get(
                path="/api/v1/strategy/pricing-data",
                params=params,
            )

            return response_data.get("prices", {})

        except Exception as e:
            logger.error(f"Failed to retrieve fertilizer prices: {e}")
            raise ServiceError(f"Pricing data request failed: {e}")

    async def recommend_fertilizer_type(
        self,
        nutrient_requirements: Dict[str, float],
        soil_characteristics: Dict[str, any],
        crop_type: str,
    ) -> List[Dict[str, any]]:
        """
        Get fertilizer type recommendations based on requirements.

        Args:
            nutrient_requirements: Required nutrients (N, P, K, etc.)
            soil_characteristics: Soil properties
            crop_type: Type of crop

        Returns:
            List of recommended fertilizer types with compatibility scores

        Raises:
            ServiceError: On communication errors
        """
        try:
            logger.debug(f"Requesting fertilizer type recommendations for {crop_type}")

            response_data = await self.post(
                path="/api/v1/strategy/type-selection",
                json_data={
                    "nutrient_requirements": nutrient_requirements,
                    "soil_characteristics": soil_characteristics,
                    "crop_type": crop_type,
                },
            )

            return response_data.get("recommended_types", [])

        except Exception as e:
            logger.error(f"Fertilizer type recommendation failed: {e}")
            raise ServiceError(f"Type selection request failed: {e}")


__all__ = ["FertilizerStrategyClient"]
