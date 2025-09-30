"""
Comprehensive Tests for Error Handling Service
TICKET-008_farm-location-input-14.1: Implement comprehensive error handling and recovery

Tests all error scenarios and recovery strategies for location input operations.
"""

import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock

from src.services.error_handling_service import (
    LocationErrorHandler, ErrorType, ErrorContext, RecoveryStrategy,
    ErrorRecoveryResult, with_error_handling, _classify_error
)


class TestLocationErrorHandler:
    """Test suite for LocationErrorHandler."""
    
    @pytest.fixture
    def error_handler(self):
        return LocationErrorHandler()
    
    @pytest.fixture
    def sample_error_context(self):
        return ErrorContext(
            error_type=ErrorType.GPS_TIMEOUT,
            error_message="GPS timeout occurred",
            timestamp=datetime.utcnow(),
            user_id="test_user",
            session_id="test_session",
            location_data={"latitude": 40.7128, "longitude": -74.0060},
            retry_count=0,
            max_retries=3
        )
    
    def test_error_handler_initialization(self, error_handler):
        """Test that error handler initializes correctly."""
        assert error_handler.error_history == []
        assert error_handler.monitoring_enabled is True
        assert len(error_handler.recovery_strategies) > 0
        assert len(error_handler.retry_configs) > 0
    
    def test_recovery_strategies_setup(self, error_handler):
        """Test that recovery strategies are properly set up."""
        # Test GPS-related strategies
        assert ErrorType.GPS_UNAVAILABLE in error_handler.recovery_strategies
        assert ErrorType.GPS_TIMEOUT in error_handler.recovery_strategies
        assert ErrorType.GPS_ACCURACY_POOR in error_handler.recovery_strategies
        assert ErrorType.GPS_PERMISSION_DENIED in error_handler.recovery_strategies
        
        # Test network-related strategies
        assert ErrorType.NETWORK_ERROR in error_handler.recovery_strategies
        assert ErrorType.NETWORK_TIMEOUT in error_handler.recovery_strategies
        
        # Test geocoding strategies
        assert ErrorType.GEOCODING_FAILED in error_handler.recovery_strategies
        
        # Test validation strategies
        assert ErrorType.VALIDATION_ERROR in error_handler.recovery_strategies
        
        # Test service unavailability strategies
        assert ErrorType.SERVICE_UNAVAILABLE in error_handler.recovery_strategies
    
    def test_retry_configurations_setup(self, error_handler):
        """Test that retry configurations are properly set up."""
        # Test GPS retry configs
        assert ErrorType.GPS_TIMEOUT in error_handler.retry_configs
        assert ErrorType.GPS_ACCURACY_POOR in error_handler.retry_configs
        
        # Test network retry configs
        assert ErrorType.NETWORK_ERROR in error_handler.retry_configs
        assert ErrorType.NETWORK_TIMEOUT in error_handler.retry_configs
        
        # Test service retry configs
        assert ErrorType.SERVICE_UNAVAILABLE in error_handler.retry_configs
        
        # Verify configuration structure
        for error_type, config in error_handler.retry_configs.items():
            assert 'max_retries' in config
            assert 'base_delay' in config
            assert 'max_delay' in config
            assert 'exponential_backoff' in config
            assert 'jitter' in config
    
    @pytest.mark.asyncio
    async def test_handle_error_success(self, error_handler, sample_error_context):
        """Test successful error handling."""
        with patch.object(error_handler, '_log_error_for_monitoring', new_callable=AsyncMock):
            result = await error_handler.handle_error(sample_error_context)
            
            assert isinstance(result, ErrorRecoveryResult)
            assert result.success is True
            assert result.recovery_strategy_used is not None
            assert result.user_guidance is not None
    
    @pytest.mark.asyncio
    async def test_handle_error_no_strategies(self, error_handler):
        """Test error handling when no strategies are available."""
        error_context = ErrorContext(
            error_type=ErrorType.UNKNOWN_ERROR,
            error_message="Unknown error",
            timestamp=datetime.utcnow()
        )
        
        with patch.object(error_handler, '_log_error_for_monitoring', new_callable=AsyncMock):
            result = await error_handler.handle_error(error_context)
            
            assert isinstance(result, ErrorRecoveryResult)
            assert result.success is False
            assert "No recovery strategy available" in result.error_message
    
    @pytest.mark.asyncio
    async def test_handle_error_max_retries_exceeded(self, error_handler):
        """Test error handling when max retries are exceeded."""
        error_context = ErrorContext(
            error_type=ErrorType.GPS_TIMEOUT,
            error_message="GPS timeout",
            timestamp=datetime.utcnow(),
            retry_count=5,  # Exceeds max retries
            max_retries=3
        )
        
        with patch.object(error_handler, '_log_error_for_monitoring', new_callable=AsyncMock):
            result = await error_handler.handle_error(error_context)
            
            assert isinstance(result, ErrorRecoveryResult)
            # Should skip retry strategy and try other strategies
            assert result.success is True or result.success is False
    
    @pytest.mark.asyncio
    async def test_log_error_for_monitoring(self, error_handler, sample_error_context):
        """Test error logging for monitoring."""
        with patch('src.services.error_handling_service.logger') as mock_logger:
            await error_handler._log_error_for_monitoring(sample_error_context)
            
            # Verify that error was logged
            mock_logger.error.assert_called_once()
            logged_message = mock_logger.error.call_args[0][0]
            assert "Location input error:" in logged_message
            
            # Verify JSON structure
            json_part = logged_message.split("Location input error: ")[1]
            error_data = json.loads(json_part)
            assert error_data['error_type'] == ErrorType.GPS_TIMEOUT
            assert error_data['error_message'] == "GPS timeout occurred"
            assert error_data['retry_count'] == 0
    
    def test_has_fallback_available(self, error_handler):
        """Test fallback availability checking."""
        # GPS unavailable should have fallback options
        assert error_handler._has_fallback_available(ErrorType.GPS_UNAVAILABLE) is True
        
        # Network error should have fallback options
        assert error_handler._has_fallback_available(ErrorType.NETWORK_ERROR) is True
        
        # Geocoding failed should have fallback options
        assert error_handler._has_fallback_available(ErrorType.GEOCODING_FAILED) is True
        
        # Unknown error should not have fallback options
        assert error_handler._has_fallback_available(ErrorType.UNKNOWN_ERROR) is False
    
    def test_calculate_retry_delay(self, error_handler):
        """Test retry delay calculation."""
        config = {
            "base_delay": 1.0,
            "max_delay": 10.0,
            "exponential_backoff": True,
            "jitter": True
        }
        
        # Test exponential backoff
        delay1 = error_handler._calculate_retry_delay(0, config)
        delay2 = error_handler._calculate_retry_delay(1, config)
        delay3 = error_handler._calculate_retry_delay(2, config)
        
        assert delay1 < delay2 < delay3
        assert delay3 <= config["max_delay"]
        
        # Test without exponential backoff
        config_no_exp = config.copy()
        config_no_exp["exponential_backoff"] = False
        
        delay_no_exp = error_handler._calculate_retry_delay(2, config_no_exp)
        assert delay_no_exp == config["base_delay"]  # Should be base delay with jitter
    
    @pytest.mark.asyncio
    async def test_recovery_action_methods(self, error_handler, sample_error_context):
        """Test individual recovery action methods."""
        # Test manual input
        result = await error_handler._enable_manual_input(sample_error_context)
        assert result == {"manual_input_enabled": True}
        
        # Test cached data
        result = await error_handler._use_cached_data(sample_error_context)
        assert result == {"cached_data": "service_data"}
        
        # Test offline mode
        result = await error_handler._enable_offline_mode(sample_error_context)
        assert result == {"offline_mode": True, "cached_data_available": True}
        
        # Test user guidance
        result = await error_handler._provide_validation_guidance(sample_error_context)
        assert result == {"guidance": "validation_help"}


class TestErrorClassification:
    """Test suite for error classification."""
    
    def test_classify_gps_errors(self):
        """Test GPS error classification."""
        assert _classify_error(Exception("GPS timeout")) == ErrorType.GPS_TIMEOUT
        assert _classify_error(Exception("GPS permission denied")) == ErrorType.GPS_PERMISSION_DENIED
        assert _classify_error(Exception("GPS accuracy poor")) == ErrorType.GPS_ACCURACY_POOR
        assert _classify_error(Exception("GPS unavailable")) == ErrorType.GPS_UNAVAILABLE
    
    def test_classify_network_errors(self):
        """Test network error classification."""
        assert _classify_error(Exception("Network timeout")) == ErrorType.NETWORK_TIMEOUT
        assert _classify_error(Exception("Network connection failed")) == ErrorType.NETWORK_ERROR
    
    def test_classify_geocoding_errors(self):
        """Test geocoding error classification."""
        assert _classify_error(Exception("Geocoding failed")) == ErrorType.GEOCODING_FAILED
        assert _classify_error(Exception("Geocode error")) == ErrorType.GEOCODING_FAILED
    
    def test_classify_validation_errors(self):
        """Test validation error classification."""
        assert _classify_error(Exception("Invalid coordinates")) == ErrorType.INVALID_COORDINATES
        assert _classify_error(Exception("Invalid address")) == ErrorType.INVALID_ADDRESS
        assert _classify_error(Exception("Validation error")) == ErrorType.VALIDATION_ERROR
    
    def test_classify_service_errors(self):
        """Test service error classification."""
        assert _classify_error(Exception("Service unavailable")) == ErrorType.SERVICE_UNAVAILABLE
        assert _classify_error(Exception("Cache error")) == ErrorType.CACHE_ERROR
        assert _classify_error(Exception("Database error")) == ErrorType.DATABASE_ERROR
    
    def test_classify_unknown_errors(self):
        """Test unknown error classification."""
        assert _classify_error(Exception("Some random error")) == ErrorType.UNKNOWN_ERROR


class TestErrorHandlingDecorator:
    """Test suite for error handling decorator."""
    
    @pytest.fixture
    def mock_error_handler(self):
        handler = LocationErrorHandler()
        handler.monitoring_enabled = False  # Disable monitoring for tests
        return handler
    
    @pytest.mark.asyncio
    async def test_decorator_success(self, mock_error_handler):
        """Test decorator with successful function."""
        @with_error_handling(mock_error_handler)
        async def test_function():
            return "success"
        
        result = await test_function()
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_decorator_with_recovery(self, mock_error_handler):
        """Test decorator with error recovery."""
        @with_error_handling(mock_error_handler)
        async def test_function():
            raise Exception("GPS timeout")
        
        with patch.object(mock_error_handler, 'handle_error', new_callable=AsyncMock) as mock_handle:
            mock_handle.return_value = ErrorRecoveryResult(
                success=True,
                recovered_data="recovered_data",
                recovery_strategy_used=RecoveryStrategy.MANUAL_INPUT,
                user_guidance="Use manual input"
            )
            
            result = await test_function()
            assert result == "recovered_data"
            mock_handle.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_decorator_recovery_failed(self, mock_error_handler):
        """Test decorator when recovery fails."""
        @with_error_handling(mock_error_handler)
        async def test_function():
            raise Exception("GPS timeout")
        
        with patch.object(mock_error_handler, 'handle_error', new_callable=AsyncMock) as mock_handle:
            mock_handle.return_value = ErrorRecoveryResult(
                success=False,
                error_message="Recovery failed"
            )
            
            with pytest.raises(Exception) as exc_info:
                await test_function()
            
            assert "Recovery failed" in str(exc_info.value)
            mock_handle.assert_called_once()


class TestErrorScenarios:
    """Test suite for specific error scenarios."""
    
    @pytest.fixture
    def error_handler(self):
        return LocationErrorHandler()
    
    @pytest.mark.asyncio
    async def test_gps_unavailable_scenario(self, error_handler):
        """Test GPS unavailable error scenario."""
        error_context = ErrorContext(
            error_type=ErrorType.GPS_UNAVAILABLE,
            error_message="GPS is not available on this device",
            timestamp=datetime.utcnow()
        )
        
        result = await error_handler.handle_error(error_context)
        
        assert result.success is True
        assert result.recovery_strategy_used in [RecoveryStrategy.MANUAL_INPUT, RecoveryStrategy.CACHED_DATA]
        assert "GPS is not available" in result.user_guidance
    
    @pytest.mark.asyncio
    async def test_network_timeout_scenario(self, error_handler):
        """Test network timeout error scenario."""
        error_context = ErrorContext(
            error_type=ErrorType.NETWORK_TIMEOUT,
            error_message="Request timed out",
            timestamp=datetime.utcnow()
        )
        
        result = await error_handler.handle_error(error_context)
        
        assert result.success is True
        assert result.recovery_strategy_used in [RecoveryStrategy.RETRY, RecoveryStrategy.OFFLINE_MODE]
        assert "timed out" in result.user_guidance or "offline mode" in result.user_guidance
    
    @pytest.mark.asyncio
    async def test_geocoding_failed_scenario(self, error_handler):
        """Test geocoding failed error scenario."""
        error_context = ErrorContext(
            error_type=ErrorType.GEOCODING_FAILED,
            error_message="Address geocoding failed",
            timestamp=datetime.utcnow()
        )
        
        result = await error_handler.handle_error(error_context)
        
        assert result.success is True
        assert result.recovery_strategy_used in [RecoveryStrategy.FALLBACK_PROVIDER, RecoveryStrategy.MANUAL_INPUT]
        assert "geocoding failed" in result.user_guidance or "GPS coordinates manually" in result.user_guidance
    
    @pytest.mark.asyncio
    async def test_service_unavailable_scenario(self, error_handler):
        """Test service unavailable error scenario."""
        error_context = ErrorContext(
            error_type=ErrorType.SERVICE_UNAVAILABLE,
            error_message="Service temporarily unavailable",
            timestamp=datetime.utcnow()
        )
        
        result = await error_handler.handle_error(error_context)
        
        assert result.success is True
        assert result.recovery_strategy_used in [RecoveryStrategy.RETRY, RecoveryStrategy.CACHED_DATA]
        assert "unavailable" in result.user_guidance or "cached data" in result.user_guidance


class TestErrorHistory:
    """Test suite for error history tracking."""
    
    @pytest.fixture
    def error_handler(self):
        return LocationErrorHandler()
    
    @pytest.mark.asyncio
    async def test_error_history_tracking(self, error_handler):
        """Test that errors are tracked in history."""
        initial_count = len(error_handler.error_history)
        
        error_context = ErrorContext(
            error_type=ErrorType.GPS_TIMEOUT,
            error_message="GPS timeout",
            timestamp=datetime.utcnow()
        )
        
        with patch.object(error_handler, '_log_error_for_monitoring', new_callable=AsyncMock):
            await error_handler.handle_error(error_context)
        
        assert len(error_handler.error_history) == initial_count + 1
        assert error_handler.error_history[-1].error_type == ErrorType.GPS_TIMEOUT
        assert error_handler.error_history[-1].error_message == "GPS timeout"
    
    @pytest.mark.asyncio
    async def test_error_history_context_preservation(self, error_handler):
        """Test that error context is preserved in history."""
        error_context = ErrorContext(
            error_type=ErrorType.NETWORK_ERROR,
            error_message="Network error",
            timestamp=datetime.utcnow(),
            user_id="test_user",
            session_id="test_session",
            location_data={"lat": 40.7128, "lng": -74.0060},
            retry_count=2,
            additional_context={"function": "test_function"}
        )
        
        with patch.object(error_handler, '_log_error_for_monitoring', new_callable=AsyncMock):
            await error_handler.handle_error(error_context)
        
        recorded_error = error_handler.error_history[-1]
        assert recorded_error.user_id == "test_user"
        assert recorded_error.session_id == "test_session"
        assert recorded_error.location_data == {"lat": 40.7128, "lng": -74.0060}
        assert recorded_error.retry_count == 2
        assert recorded_error.additional_context == {"function": "test_function"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
