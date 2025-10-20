"""
Unit tests for TimingOptimizationHTTPAdapter.

Tests cover:
- HTTP mode operation
- Hybrid mode with fallback
- Direct import mode
- Error handling and resilience
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date

from timing_services.timing_service_http import TimingOptimizationHTTPAdapter
from clients.base_http_client import ServiceError, ServiceUnavailableError
from config.integration_config import IntegrationMode
from models import (
    TimingOptimizationRequest,
    TimingOptimizationResult,
    ApplicationTiming,
    LocationData,
    FertilizerType,
    ApplicationMethod,
)


class TestTimingOptimizationHTTPAdapter:
    """Test HTTP-based timing optimization adapter."""

    @pytest.fixture
    def sample_request(self):
        """Create sample timing optimization request."""
        return TimingOptimizationRequest(
            crop_type="corn",
            location=LocationData(latitude=42.5, longitude=-92.5),
            planting_date=date(2024, 5, 15),
            fertilizer_types=[FertilizerType.UREA],
            application_methods=[ApplicationMethod.BROADCAST],
            target_yield=180.0,
        )

    @pytest.fixture
    def sample_result(self):
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
            optimization_notes="Test result",
        )

    @pytest.mark.asyncio
    async def test_http_mode_success(self, sample_request, sample_result):
        """Test successful optimization in HTTP mode."""
        with patch('config.integration_config.integration_config') as mock_config:
            mock_config.mode = IntegrationMode.REST_API
            mock_config.enable_circuit_breaker = True

            with patch('clients.fertilizer_strategy_client.FertilizerStrategyClient') as MockClient:
                mock_client_instance = MockClient.return_value
                mock_client_instance.optimize_timing = AsyncMock(return_value=sample_result)

                adapter = TimingOptimizationHTTPAdapter()
                result = await adapter.optimize(sample_request)

                assert result == sample_result
                mock_client_instance.optimize_timing.assert_called_once_with(sample_request)

    @pytest.mark.asyncio
    async def test_hybrid_mode_fallback(self, sample_request, sample_result):
        """Test fallback to direct import in hybrid mode."""
        with patch('config.integration_config.integration_config') as mock_config:
            mock_config.mode = IntegrationMode.HYBRID
            mock_config.enable_circuit_breaker = True

            # HTTP client fails
            with patch('clients.fertilizer_strategy_client.FertilizerStrategyClient') as MockClient:
                mock_client_instance = MockClient.return_value
                mock_client_instance.optimize_timing = AsyncMock(
                    side_effect=ServiceError("Connection failed")
                )

                # Direct import succeeds
                with patch('timing_services.timing_service.TimingOptimizationAdapter') as MockAdapter:
                    mock_adapter_instance = MockAdapter.return_value
                    mock_adapter_instance.optimize = AsyncMock(return_value=sample_result)

                    adapter = TimingOptimizationHTTPAdapter()
                    result = await adapter.optimize(sample_request)

                    assert result == sample_result
                    # Verify fallback was used
                    mock_adapter_instance.optimize.assert_called_once()

    @pytest.mark.asyncio
    async def test_rest_api_mode_no_fallback(self, sample_request):
        """Test no fallback in REST_API mode."""
        with patch('config.integration_config.integration_config') as mock_config:
            mock_config.mode = IntegrationMode.REST_API
            mock_config.enable_circuit_breaker = True

            with patch('clients.fertilizer_strategy_client.FertilizerStrategyClient') as MockClient:
                mock_client_instance = MockClient.return_value
                mock_client_instance.optimize_timing = AsyncMock(
                    side_effect=ServiceError("Connection failed")
                )

                adapter = TimingOptimizationHTTPAdapter()

                with pytest.raises(ServiceError):
                    await adapter.optimize(sample_request)

    @pytest.mark.asyncio
    async def test_analyze_weather_windows(self, sample_request, sample_result):
        """Test weather window analysis."""
        with patch('config.integration_config.integration_config') as mock_config:
            mock_config.mode = IntegrationMode.REST_API
            mock_config.enable_circuit_breaker = True

            with patch('clients.fertilizer_strategy_client.FertilizerStrategyClient') as MockClient:
                mock_client_instance = MockClient.return_value
                mock_client_instance.optimize_timing = AsyncMock(return_value=sample_result)

                adapter = TimingOptimizationHTTPAdapter()
                windows = await adapter.analyze_weather_windows(sample_request)

                # Should extract from full result
                assert isinstance(windows, list)

    @pytest.mark.asyncio
    async def test_determine_crop_stages(self, sample_request, sample_result):
        """Test crop stage determination."""
        with patch('config.integration_config.integration_config') as mock_config:
            mock_config.mode = IntegrationMode.REST_API
            mock_config.enable_circuit_breaker = True

            with patch('clients.fertilizer_strategy_client.FertilizerStrategyClient') as MockClient:
                mock_client_instance = MockClient.return_value
                mock_client_instance.optimize_timing = AsyncMock(return_value=sample_result)

                adapter = TimingOptimizationHTTPAdapter()
                stages = await adapter.determine_crop_stages(sample_request)

                assert isinstance(stages, dict)

    @pytest.mark.asyncio
    async def test_optimize_split_applications(self, sample_request, sample_result):
        """Test split application optimization."""
        with patch('config.integration_config.integration_config') as mock_config:
            mock_config.mode = IntegrationMode.REST_API
            mock_config.enable_circuit_breaker = True

            with patch('clients.fertilizer_strategy_client.FertilizerStrategyClient') as MockClient:
                mock_client_instance = MockClient.return_value
                mock_client_instance.optimize_timing = AsyncMock(return_value=sample_result)

                adapter = TimingOptimizationHTTPAdapter()
                plans = await adapter.optimize_split_applications(sample_request)

                assert isinstance(plans, list)
                assert plans == sample_result.split_plans

    @pytest.mark.asyncio
    async def test_quick_optimize(self, sample_request, sample_result):
        """Test quick optimization alias."""
        with patch('config.integration_config.integration_config') as mock_config:
            mock_config.mode = IntegrationMode.REST_API
            mock_config.enable_circuit_breaker = True

            with patch('clients.fertilizer_strategy_client.FertilizerStrategyClient') as MockClient:
                mock_client_instance = MockClient.return_value
                mock_client_instance.optimize_timing = AsyncMock(return_value=sample_result)

                adapter = TimingOptimizationHTTPAdapter()
                result = await adapter.quick_optimize(sample_request)

                assert result == sample_result

    @pytest.mark.asyncio
    async def test_summarize(self, sample_request, sample_result):
        """Test result summarization."""
        with patch('config.integration_config.integration_config') as mock_config:
            mock_config.mode = IntegrationMode.REST_API
            mock_config.enable_circuit_breaker = True

            with patch('clients.fertilizer_strategy_client.FertilizerStrategyClient') as MockClient:
                mock_client_instance = MockClient.return_value
                mock_client_instance.optimize_timing = AsyncMock(return_value=sample_result)

                adapter = TimingOptimizationHTTPAdapter()
                summary = await adapter.summarize(sample_request)

                assert isinstance(summary, dict)
                assert FertilizerType.UREA in summary

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_in_http_mode(self, sample_request):
        """Test circuit breaker functionality."""
        with patch('config.integration_config.integration_config') as mock_config:
            mock_config.mode = IntegrationMode.REST_API
            mock_config.enable_circuit_breaker = True

            with patch('clients.fertilizer_strategy_client.FertilizerStrategyClient') as MockClient:
                mock_client_instance = MockClient.return_value
                mock_client_instance.optimize_timing = AsyncMock(
                    side_effect=ServiceUnavailableError("Circuit breaker open")
                )

                adapter = TimingOptimizationHTTPAdapter()

                with pytest.raises(ServiceUnavailableError):
                    await adapter.optimize(sample_request)

    @pytest.mark.asyncio
    async def test_resource_cleanup(self):
        """Test proper resource cleanup."""
        with patch('config.integration_config.integration_config') as mock_config:
            mock_config.mode = IntegrationMode.REST_API
            mock_config.enable_circuit_breaker = True

            with patch('clients.fertilizer_strategy_client.FertilizerStrategyClient') as MockClient:
                mock_client_instance = MockClient.return_value
                mock_client_instance.close = AsyncMock()

                adapter = TimingOptimizationHTTPAdapter()
                await adapter.close()

                # Verify client cleanup was called
                mock_client_instance.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_direct_import_mode(self, sample_request, sample_result):
        """Test operation in direct import mode."""
        with patch('config.integration_config.integration_config') as mock_config:
            mock_config.mode = IntegrationMode.DIRECT_IMPORT
            mock_config.enable_circuit_breaker = False

            # Mock direct import adapter
            with patch('timing_services.timing_service.TimingOptimizationAdapter') as MockAdapter:
                mock_adapter_instance = MockAdapter.return_value
                mock_adapter_instance.optimize = AsyncMock(return_value=sample_result)

                adapter = TimingOptimizationHTTPAdapter()
                result = await adapter.optimize(sample_request)

                assert result == sample_result
                mock_adapter_instance.optimize.assert_called_once()


class TestHybridModeEdgeCases:
    """Test edge cases in hybrid mode."""

    @pytest.fixture
    def sample_request(self):
        """Create sample request."""
        return TimingOptimizationRequest(
            crop_type="corn",
            location=LocationData(latitude=42.5, longitude=-92.5),
            planting_date=date(2024, 5, 15),
            fertilizer_types=[FertilizerType.UREA],
            application_methods=[ApplicationMethod.BROADCAST],
        )

    @pytest.mark.asyncio
    async def test_hybrid_mode_both_methods_fail(self, sample_request):
        """Test when both HTTP and direct import fail."""
        with patch('config.integration_config.integration_config') as mock_config:
            mock_config.mode = IntegrationMode.HYBRID
            mock_config.enable_circuit_breaker = True

            # Both fail
            with patch('clients.fertilizer_strategy_client.FertilizerStrategyClient') as MockClient:
                mock_client_instance = MockClient.return_value
                mock_client_instance.optimize_timing = AsyncMock(
                    side_effect=ServiceError("HTTP failed")
                )

                # Adapter initialization fails (no fallback available)
                with patch('timing_services.timing_service.TimingOptimizationAdapter') as MockAdapter:
                    MockAdapter.side_effect = ImportError("Module not found")

                    adapter = TimingOptimizationHTTPAdapter()

                    with pytest.raises(ServiceError):
                        await adapter.optimize(sample_request)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
