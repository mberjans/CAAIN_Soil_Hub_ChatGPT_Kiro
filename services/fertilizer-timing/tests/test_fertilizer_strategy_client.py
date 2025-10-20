"""
Unit tests for FertilizerStrategyClient.

Tests cover:
- Timing optimization requests
- Equipment compatibility checks
- Pricing data retrieval
- Type selection recommendations
- Error handling and resilience
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, date

from clients.fertilizer_strategy_client import FertilizerStrategyClient
from clients.base_http_client import ServiceError
from models import (
    TimingOptimizationRequest,
    TimingOptimizationResult,
    ApplicationTiming,
    LocationData,
    FertilizerType,
    ApplicationMethod,
)


class TestFertilizerStrategyClient:
    """Test fertilizer-strategy HTTP client."""

    @pytest.fixture
    def strategy_client(self):
        """Create FertilizerStrategyClient instance."""
        with patch('config.integration_config.integration_config') as mock_config:
            from config.integration_config import ServiceConfig

            mock_config.services = {
                "fertilizer-strategy": ServiceConfig(
                    name="fertilizer-strategy",
                    base_url="http://localhost:8009",
                    timeout=30,
                    max_retries=3,
                )
            }
            mock_config.enable_circuit_breaker = True

            return FertilizerStrategyClient()

    @pytest.fixture
    def sample_timing_request(self):
        """Create sample timing optimization request."""
        return TimingOptimizationRequest(
            crop_type="corn",
            location=LocationData(latitude=42.5, longitude=-92.5),
            planting_date=date(2024, 5, 15),
            fertilizer_types=[FertilizerType.UREA, FertilizerType.MAP],
            application_methods=[ApplicationMethod.BROADCAST],
            target_yield=180.0,
        )

    @pytest.fixture
    def sample_timing_result(self):
        """Create sample timing optimization result."""
        return TimingOptimizationResult(
            optimal_timings=[
                ApplicationTiming(
                    fertilizer_type=FertilizerType.UREA,
                    application_method=ApplicationMethod.BROADCAST,
                    recommended_date=date(2024, 6, 10),
                    application_rate=150.0,
                    confidence_score=0.92,
                )
            ],
            split_plans=[],
            weather_windows=[],
            confidence_score=0.92,
            optimization_notes="Optimal timing based on crop stage and weather",
        )

    @pytest.mark.asyncio
    async def test_optimize_timing_success(
        self, strategy_client, sample_timing_request, sample_timing_result
    ):
        """Test successful timing optimization request."""
        mock_response = sample_timing_result.model_dump(mode="json")

        with patch.object(strategy_client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            result = await strategy_client.optimize_timing(sample_timing_request)

            assert isinstance(result, TimingOptimizationResult)
            assert len(result.optimal_timings) == 1
            assert result.confidence_score == 0.92

            # Verify API call
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[1]['path'] == "/api/v1/strategy/timing-recommendations"

    @pytest.mark.asyncio
    async def test_optimize_timing_error_handling(
        self, strategy_client, sample_timing_request
    ):
        """Test error handling in timing optimization."""
        with patch.object(strategy_client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = Exception("API Error")

            with pytest.raises(ServiceError) as exc_info:
                await strategy_client.optimize_timing(sample_timing_request)

            assert "Timing optimization request failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_check_equipment_compatibility(self, strategy_client):
        """Test equipment compatibility check."""
        mock_response = {
            "compatible_equipment": ["spreader_001", "spreader_002"],
            "incompatible_equipment": ["injector_001"],
        }

        with patch.object(strategy_client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            result = await strategy_client.check_equipment_compatibility(
                fertilizer_type="urea",
                application_method="broadcast",
                available_equipment=["spreader_001", "spreader_002", "injector_001"],
            )

            assert len(result["compatible_equipment"]) == 2
            assert len(result["incompatible_equipment"]) == 1
            assert "spreader_001" in result["compatible_equipment"]

    @pytest.mark.asyncio
    async def test_get_current_prices_no_filter(self, strategy_client):
        """Test fetching all current prices."""
        mock_response = {
            "prices": {
                "urea": {
                    "price_per_unit": 450.0,
                    "currency": "USD",
                    "unit": "ton",
                },
                "MAP": {
                    "price_per_unit": 620.0,
                    "currency": "USD",
                    "unit": "ton",
                }
            }
        }

        with patch.object(strategy_client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            result = await strategy_client.get_current_prices()

            assert "urea" in result
            assert "MAP" in result
            assert result["urea"]["price_per_unit"] == 450.0

    @pytest.mark.asyncio
    async def test_get_current_prices_with_location(self, strategy_client):
        """Test fetching prices with location filter."""
        mock_response = {
            "prices": {
                "urea": {
                    "price_per_unit": 455.0,
                    "currency": "USD",
                    "unit": "ton",
                }
            }
        }

        with patch.object(strategy_client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            result = await strategy_client.get_current_prices(
                fertilizer_type="urea",
                location={"latitude": 42.5, "longitude": -92.5}
            )

            # Verify params were passed
            call_args = mock_get.call_args
            params = call_args[1]['params']
            assert params['fertilizer_type'] == "urea"
            assert params['latitude'] == 42.5
            assert params['longitude'] == -92.5

    @pytest.mark.asyncio
    async def test_recommend_fertilizer_type(self, strategy_client):
        """Test fertilizer type recommendation."""
        mock_response = {
            "recommended_types": [
                {
                    "fertilizer_type": "Urea",
                    "compatibility_score": 0.9,
                    "nutrient_content": {"N": 46.0, "P": 0, "K": 0},
                    "pros": ["High nitrogen", "Cost-effective"],
                    "cons": ["Volatilization risk"],
                },
                {
                    "fertilizer_type": "MAP",
                    "compatibility_score": 0.85,
                    "nutrient_content": {"N": 11.0, "P": 52.0, "K": 0},
                    "pros": ["Good P source"],
                    "cons": ["Higher cost"],
                }
            ]
        }

        with patch.object(strategy_client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            result = await strategy_client.recommend_fertilizer_type(
                nutrient_requirements={"N": 150, "P": 50, "K": 40},
                soil_characteristics={"pH": 6.5, "organic_matter": 3.2},
                crop_type="corn"
            )

            assert len(result) == 2
            assert result[0]["fertilizer_type"] == "Urea"
            assert result[0]["compatibility_score"] == 0.9

    @pytest.mark.asyncio
    async def test_pricing_data_error_handling(self, strategy_client):
        """Test error handling in pricing data retrieval."""
        with patch.object(strategy_client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = Exception("Database error")

            with pytest.raises(ServiceError) as exc_info:
                await strategy_client.get_current_prices()

            assert "Pricing data request failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_equipment_compatibility_error_handling(self, strategy_client):
        """Test error handling in equipment compatibility check."""
        with patch.object(strategy_client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = Exception("Service unavailable")

            with pytest.raises(ServiceError) as exc_info:
                await strategy_client.check_equipment_compatibility(
                    fertilizer_type="urea",
                    application_method="broadcast",
                    available_equipment=["spreader_001"]
                )

            assert "Equipment compatibility request failed" in str(exc_info.value)


class TestClientIntegration:
    """Integration tests for client functionality."""

    @pytest.mark.asyncio
    async def test_client_resource_cleanup(self):
        """Test proper resource cleanup."""
        with patch('config.integration_config.integration_config') as mock_config:
            from config.integration_config import ServiceConfig

            mock_config.services = {
                "fertilizer-strategy": ServiceConfig(
                    name="fertilizer-strategy",
                    base_url="http://localhost:8009",
                )
            }
            mock_config.enable_circuit_breaker = True

            client = FertilizerStrategyClient()

            # Simulate some usage
            with patch.object(client, 'get', new_callable=AsyncMock):
                await client.get_current_prices()

            # Clean up
            await client.close()

            # Verify client is closed
            assert client._client is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
