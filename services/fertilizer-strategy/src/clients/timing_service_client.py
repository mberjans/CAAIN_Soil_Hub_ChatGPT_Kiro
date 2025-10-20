"""
HTTP client for fertilizer-timing service communication.

This module provides async HTTP client for interacting with the fertilizer-timing
service REST API, enabling loose coupling between services.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import date

from clients.base_http_client import BaseHTTPClient, ServiceError
from config.integration_config import integration_config

logger = logging.getLogger(__name__)


class TimingServiceClient(BaseHTTPClient):
    """
    HTTP client for fertilizer-timing service.

    Provides methods for:
    - Timing optimization requests
    - Seasonal calendar generation
    - Alert management
    - Weather and soil integration
    - Constraint checking
    """

    def __init__(self):
        """Initialize fertilizer-timing HTTP client."""
        config = integration_config.services.get("fertilizer-timing")
        if not config:
            raise ValueError("Fertilizer-timing service configuration not found")

        super().__init__(
            config=config,
            enable_circuit_breaker=integration_config.enable_circuit_breaker,
        )

    async def optimize_timing(
        self,
        crop_type: str,
        location: Dict[str, float],
        planting_date: str,
        soil_characteristics: Dict[str, Any],
        nutrient_requirements: Dict[str, float],
        available_equipment: Optional[List[str]] = None,
        labor_availability: Optional[Dict[str, Any]] = None,
        constraints: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Request timing optimization from fertilizer-timing service.

        Args:
            crop_type: Type of crop being grown
            location: Location dict with latitude and longitude
            planting_date: ISO format planting date
            soil_characteristics: Soil properties
            nutrient_requirements: Required nutrients (N, P, K, etc.)
            available_equipment: Optional list of available equipment IDs
            labor_availability: Optional labor availability constraints
            constraints: Optional list of timing constraints

        Returns:
            Dict containing timing optimization results

        Raises:
            ServiceError: On communication or processing errors
        """
        try:
            logger.info(
                f"Requesting timing optimization for {crop_type} "
                f"at location ({location.get('latitude')}, {location.get('longitude')})"
            )

            # Build request payload
            request_data = {
                "crop_type": crop_type,
                "location": location,
                "planting_date": planting_date,
                "soil_characteristics": soil_characteristics,
                "nutrient_requirements": nutrient_requirements,
            }

            if available_equipment:
                request_data["available_equipment"] = available_equipment

            if labor_availability:
                request_data["labor_availability"] = labor_availability

            if constraints:
                request_data["constraints"] = constraints

            response_data = await self.post(
                path="/api/v1/timing/optimize",
                json_data=request_data,
            )

            logger.info(
                f"Received timing optimization with "
                f"{len(response_data.get('optimal_timings', []))} recommendations"
            )

            return response_data

        except Exception as e:
            logger.error(f"Failed to get timing optimization: {e}")
            raise ServiceError(f"Timing optimization request failed: {e}")

    async def generate_seasonal_calendar(
        self,
        crop_type: str,
        location: Dict[str, float],
        planting_date: str,
        fertilizer_strategy: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate seasonal fertilizer calendar.

        Args:
            crop_type: Type of crop
            location: Location coordinates
            planting_date: ISO format planting date
            fertilizer_strategy: Complete fertilizer strategy

        Returns:
            Dict containing seasonal calendar

        Raises:
            ServiceError: On communication errors
        """
        try:
            logger.debug(f"Generating seasonal calendar for {crop_type}")

            response_data = await self.post(
                path="/api/v1/calendar/generate",
                json_data={
                    "crop_type": crop_type,
                    "location": location,
                    "planting_date": planting_date,
                    "fertilizer_strategy": fertilizer_strategy,
                },
            )

            return response_data

        except Exception as e:
            logger.error(f"Failed to generate seasonal calendar: {e}")
            raise ServiceError(f"Seasonal calendar generation failed: {e}")

    async def get_timing_alerts(
        self,
        crop_type: str,
        location: Dict[str, float],
        upcoming_applications: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Get timing alerts for upcoming applications.

        Args:
            crop_type: Type of crop
            location: Location coordinates
            upcoming_applications: List of planned applications

        Returns:
            Dict containing timing alerts

        Raises:
            ServiceError: On communication errors
        """
        try:
            logger.debug(f"Getting timing alerts for {crop_type}")

            response_data = await self.post(
                path="/api/v1/alerts/timing",
                json_data={
                    "crop_type": crop_type,
                    "location": location,
                    "upcoming_applications": upcoming_applications,
                },
            )

            return response_data

        except Exception as e:
            logger.error(f"Failed to get timing alerts: {e}")
            raise ServiceError(f"Timing alerts request failed: {e}")

    async def check_weather_window(
        self,
        location: Dict[str, float],
        start_date: str,
        end_date: str,
        application_method: str,
    ) -> Dict[str, Any]:
        """
        Check weather window suitability for application.

        Args:
            location: Location coordinates
            start_date: ISO format start date
            end_date: ISO format end date
            application_method: Application method type

        Returns:
            Dict containing weather window analysis

        Raises:
            ServiceError: On communication errors
        """
        try:
            logger.debug(
                f"Checking weather window from {start_date} to {end_date}"
            )

            response_data = await self.post(
                path="/api/v1/timing/weather-window",
                json_data={
                    "location": location,
                    "start_date": start_date,
                    "end_date": end_date,
                    "application_method": application_method,
                },
            )

            return response_data

        except Exception as e:
            logger.error(f"Failed to check weather window: {e}")
            raise ServiceError(f"Weather window check failed: {e}")

    async def analyze_constraints(
        self,
        equipment_availability: Optional[List[Dict[str, Any]]] = None,
        labor_availability: Optional[Dict[str, Any]] = None,
        budget_constraints: Optional[Dict[str, float]] = None,
        field_accessibility: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Analyze operational constraints for timing.

        Args:
            equipment_availability: Equipment availability windows
            labor_availability: Labor availability constraints
            budget_constraints: Budget limitations
            field_accessibility: Field accessibility constraints

        Returns:
            Dict containing constraint analysis

        Raises:
            ServiceError: On communication errors
        """
        try:
            logger.debug("Analyzing operational constraints")

            request_data = {}
            if equipment_availability:
                request_data["equipment_availability"] = equipment_availability
            if labor_availability:
                request_data["labor_availability"] = labor_availability
            if budget_constraints:
                request_data["budget_constraints"] = budget_constraints
            if field_accessibility:
                request_data["field_accessibility"] = field_accessibility

            response_data = await self.post(
                path="/api/v1/timing/constraints",
                json_data=request_data,
            )

            return response_data

        except Exception as e:
            logger.error(f"Failed to analyze constraints: {e}")
            raise ServiceError(f"Constraint analysis failed: {e}")

    async def get_split_application_plan(
        self,
        crop_type: str,
        total_n_rate: float,
        location: Dict[str, float],
        planting_date: str,
        soil_characteristics: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Get split application plan for nitrogen.

        Args:
            crop_type: Type of crop
            total_n_rate: Total nitrogen rate
            location: Location coordinates
            planting_date: ISO format planting date
            soil_characteristics: Soil properties

        Returns:
            Dict containing split application plan

        Raises:
            ServiceError: On communication errors
        """
        try:
            logger.debug(f"Getting split application plan for {crop_type}")

            response_data = await self.post(
                path="/api/v1/timing/split-application",
                json_data={
                    "crop_type": crop_type,
                    "total_n_rate": total_n_rate,
                    "location": location,
                    "planting_date": planting_date,
                    "soil_characteristics": soil_characteristics,
                },
            )

            return response_data

        except Exception as e:
            logger.error(f"Failed to get split application plan: {e}")
            raise ServiceError(f"Split application plan request failed: {e}")

    async def explain_timing_decision(
        self,
        crop_type: str,
        recommended_date: str,
        application_type: str,
        location: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Get explanation for timing decision.

        Args:
            crop_type: Type of crop
            recommended_date: ISO format recommended date
            application_type: Type of application
            location: Location coordinates

        Returns:
            Dict containing timing explanation

        Raises:
            ServiceError: On communication errors
        """
        try:
            logger.debug(f"Getting timing explanation for {crop_type}")

            response_data = await self.post(
                path="/api/v1/explanation/timing",
                json_data={
                    "crop_type": crop_type,
                    "recommended_date": recommended_date,
                    "application_type": application_type,
                    "location": location,
                },
            )

            return response_data

        except Exception as e:
            logger.error(f"Failed to get timing explanation: {e}")
            raise ServiceError(f"Timing explanation request failed: {e}")


__all__ = ["TimingServiceClient"]
