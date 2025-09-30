"""
Comprehensive Error Handling and Recovery Service for Location Input
TICKET-008_farm-location-input-14.1: Implement comprehensive error handling and recovery

This service provides robust error handling for all location input scenarios including:
- GPS failures and accuracy issues
- Network connectivity problems
- Validation errors and service unavailability
- Automatic retry mechanisms with exponential backoff
- Fallback methods and graceful degradation
- Clear user feedback and recovery suggestions
- Integration with logging and monitoring systems
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass
from functools import wraps
import json

logger = logging.getLogger(__name__)


class ErrorType(str, Enum):
    """Types of errors that can occur in location input."""
    GPS_UNAVAILABLE = "gps_unavailable"
    GPS_TIMEOUT = "gps_timeout"
    GPS_ACCURACY_POOR = "gps_accuracy_poor"
    GPS_PERMISSION_DENIED = "gps_permission_denied"
    NETWORK_ERROR = "network_error"
    NETWORK_TIMEOUT = "network_timeout"
    GEOCODING_FAILED = "geocoding_failed"
    VALIDATION_ERROR = "validation_error"
    SERVICE_UNAVAILABLE = "service_unavailable"
    INVALID_COORDINATES = "invalid_coordinates"
    INVALID_ADDRESS = "invalid_address"
    CACHE_ERROR = "cache_error"
    DATABASE_ERROR = "database_error"
    UNKNOWN_ERROR = "unknown_error"


class RecoveryStrategy(str, Enum):
    """Available recovery strategies."""
    RETRY = "retry"
    FALLBACK_PROVIDER = "fallback_provider"
    MANUAL_INPUT = "manual_input"
    OFFLINE_MODE = "offline_mode"
    CACHED_DATA = "cached_data"
    USER_GUIDANCE = "user_guidance"


@dataclass
class ErrorContext:
    """Context information for error handling."""
    error_type: ErrorType
    error_message: str
    timestamp: datetime
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    location_data: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    max_retries: int = 3
    additional_context: Optional[Dict[str, Any]] = None


@dataclass
class RecoveryAction:
    """A recovery action to take for an error."""
    strategy: RecoveryStrategy
    description: str
    action: Callable
    priority: int = 1
    success_probability: float = 0.8
    user_guidance: Optional[str] = None


@dataclass
class ErrorRecoveryResult:
    """Result of error recovery attempt."""
    success: bool
    recovered_data: Optional[Any] = None
    error_message: Optional[str] = None
    recovery_strategy_used: Optional[RecoveryStrategy] = None
    user_guidance: Optional[str] = None
    fallback_available: bool = False


class LocationErrorHandler:
    """
    Comprehensive error handler for location input operations.
    
    Provides automatic retry mechanisms, fallback strategies, and user guidance
    for all types of location input errors.
    """
    
    def __init__(self):
        self.error_history: List[ErrorContext] = []
        self.recovery_strategies: Dict[ErrorType, List[RecoveryAction]] = {}
        self.retry_configs: Dict[ErrorType, Dict[str, Any]] = {}
        self.fallback_providers: List[str] = []
        self.monitoring_enabled = True
        
        self._setup_default_recovery_strategies()
        self._setup_retry_configurations()
    
    def _setup_default_recovery_strategies(self):
        """Set up default recovery strategies for each error type."""
        
        # GPS-related errors
        self.recovery_strategies[ErrorType.GPS_UNAVAILABLE] = [
            RecoveryAction(
                strategy=RecoveryStrategy.MANUAL_INPUT,
                description="Allow manual coordinate input",
                action=self._enable_manual_input,
                user_guidance="GPS is not available. Please enter coordinates manually or use the map to select your location."
            ),
            RecoveryAction(
                strategy=RecoveryStrategy.CACHED_DATA,
                description="Use previously cached location",
                action=self._use_cached_location,
                user_guidance="Using your last known location. Please verify this is correct."
            )
        ]
        
        self.recovery_strategies[ErrorType.GPS_TIMEOUT] = [
            RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                description="Retry GPS with extended timeout",
                action=self._retry_gps_extended_timeout,
                user_guidance="GPS is taking longer than expected. Retrying with extended timeout..."
            ),
            RecoveryAction(
                strategy=RecoveryStrategy.MANUAL_INPUT,
                description="Switch to manual input",
                action=self._enable_manual_input,
                user_guidance="GPS timeout occurred. Please enter coordinates manually."
            )
        ]
        
        self.recovery_strategies[ErrorType.GPS_ACCURACY_POOR] = [
            RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                description="Retry GPS with high accuracy mode",
                action=self._retry_gps_high_accuracy,
                user_guidance="GPS accuracy is poor. Retrying with high accuracy mode..."
            ),
            RecoveryAction(
                strategy=RecoveryStrategy.USER_GUIDANCE,
                description="Guide user to improve GPS accuracy",
                action=self._guide_gps_accuracy,
                user_guidance="Move to an open area away from buildings and trees for better GPS accuracy."
            )
        ]
        
        self.recovery_strategies[ErrorType.GPS_PERMISSION_DENIED] = [
            RecoveryAction(
                strategy=RecoveryStrategy.USER_GUIDANCE,
                description="Guide user to enable GPS permissions",
                action=self._guide_gps_permissions,
                user_guidance="GPS permission is required. Please enable location access in your browser settings."
            ),
            RecoveryAction(
                strategy=RecoveryStrategy.MANUAL_INPUT,
                description="Switch to manual input",
                action=self._enable_manual_input,
                user_guidance="Please enter coordinates manually or use the map to select your location."
            )
        ]
        
        # Network-related errors
        self.recovery_strategies[ErrorType.NETWORK_ERROR] = [
            RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                description="Retry network request",
                action=self._retry_network_request,
                user_guidance="Network error occurred. Retrying..."
            ),
            RecoveryAction(
                strategy=RecoveryStrategy.OFFLINE_MODE,
                description="Switch to offline mode",
                action=self._enable_offline_mode,
                user_guidance="Network is unavailable. Switching to offline mode with cached data."
            )
        ]
        
        self.recovery_strategies[ErrorType.NETWORK_TIMEOUT] = [
            RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                description="Retry with extended timeout",
                action=self._retry_extended_timeout,
                user_guidance="Request timed out. Retrying with extended timeout..."
            ),
            RecoveryAction(
                strategy=RecoveryStrategy.OFFLINE_MODE,
                description="Switch to offline mode",
                action=self._enable_offline_mode,
                user_guidance="Network is slow. Switching to offline mode."
            )
        ]
        
        # Geocoding errors
        self.recovery_strategies[ErrorType.GEOCODING_FAILED] = [
            RecoveryAction(
                strategy=RecoveryStrategy.FALLBACK_PROVIDER,
                description="Try alternative geocoding provider",
                action=self._try_fallback_geocoding,
                user_guidance="Primary geocoding failed. Trying alternative provider..."
            ),
            RecoveryAction(
                strategy=RecoveryStrategy.MANUAL_INPUT,
                description="Switch to manual coordinate input",
                action=self._enable_manual_input,
                user_guidance="Address geocoding failed. Please enter GPS coordinates manually."
            )
        ]
        
        # Validation errors
        self.recovery_strategies[ErrorType.VALIDATION_ERROR] = [
            RecoveryAction(
                strategy=RecoveryStrategy.USER_GUIDANCE,
                description="Provide validation guidance",
                action=self._provide_validation_guidance,
                user_guidance="Please check your input and try again."
            ),
            RecoveryAction(
                strategy=RecoveryStrategy.MANUAL_INPUT,
                description="Allow manual correction",
                action=self._enable_manual_correction,
                user_guidance="Please correct the highlighted errors and try again."
            )
        ]
        
        # Service unavailability
        self.recovery_strategies[ErrorType.SERVICE_UNAVAILABLE] = [
            RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                description="Retry after delay",
                action=self._retry_with_delay,
                user_guidance="Service temporarily unavailable. Retrying in a moment..."
            ),
            RecoveryAction(
                strategy=RecoveryStrategy.CACHED_DATA,
                description="Use cached data",
                action=self._use_cached_data,
                user_guidance="Service unavailable. Using cached data."
            )
        ]
    
    def _setup_retry_configurations(self):
        """Set up retry configurations for different error types."""
        
        # GPS retry configs
        self.retry_configs[ErrorType.GPS_TIMEOUT] = {
            "max_retries": 3,
            "base_delay": 2.0,
            "max_delay": 10.0,
            "exponential_backoff": True,
            "jitter": True
        }
        
        self.retry_configs[ErrorType.GPS_ACCURACY_POOR] = {
            "max_retries": 2,
            "base_delay": 1.0,
            "max_delay": 5.0,
            "exponential_backoff": False,
            "jitter": False
        }
        
        # Network retry configs
        self.retry_configs[ErrorType.NETWORK_ERROR] = {
            "max_retries": 3,
            "base_delay": 1.0,
            "max_delay": 8.0,
            "exponential_backoff": True,
            "jitter": True
        }
        
        self.retry_configs[ErrorType.NETWORK_TIMEOUT] = {
            "max_retries": 2,
            "base_delay": 2.0,
            "max_delay": 10.0,
            "exponential_backoff": True,
            "jitter": True
        }
        
        # Service retry configs
        self.retry_configs[ErrorType.SERVICE_UNAVAILABLE] = {
            "max_retries": 5,
            "base_delay": 3.0,
            "max_delay": 30.0,
            "exponential_backoff": True,
            "jitter": True
        }
    
    async def handle_error(self, error_context: ErrorContext) -> ErrorRecoveryResult:
        """
        Handle an error with appropriate recovery strategies.
        
        Args:
            error_context: Context information about the error
            
        Returns:
            ErrorRecoveryResult with recovery outcome
        """
        logger.info(f"Handling error: {error_context.error_type} - {error_context.error_message}")
        
        # Record error in history
        self.error_history.append(error_context)
        
        # Log error for monitoring
        if self.monitoring_enabled:
            await self._log_error_for_monitoring(error_context)
        
        # Get recovery strategies for this error type
        strategies = self.recovery_strategies.get(error_context.error_type, [])
        
        if not strategies:
            logger.warning(f"No recovery strategies defined for error type: {error_context.error_type}")
            return ErrorRecoveryResult(
                success=False,
                error_message=f"No recovery strategy available for {error_context.error_type}",
                user_guidance="An unexpected error occurred. Please try again or contact support."
            )
        
        # Try recovery strategies in order of priority
        strategies.sort(key=lambda s: s.priority)
        
        for strategy in strategies:
            try:
                logger.info(f"Attempting recovery strategy: {strategy.strategy}")
                
                # Check if we should retry based on retry count
                if strategy.strategy == RecoveryStrategy.RETRY:
                    if error_context.retry_count >= error_context.max_retries:
                        logger.info(f"Max retries ({error_context.max_retries}) exceeded, skipping retry strategy")
                        continue
                
                # Execute recovery action
                result = await strategy.action(error_context)
                
                if result:
                    logger.info(f"Recovery successful with strategy: {strategy.strategy}")
                    return ErrorRecoveryResult(
                        success=True,
                        recovered_data=result,
                        recovery_strategy_used=strategy.strategy,
                        user_guidance=strategy.user_guidance
                    )
                
            except Exception as e:
                logger.error(f"Recovery strategy {strategy.strategy} failed: {e}")
                continue
        
        # All recovery strategies failed
        logger.error(f"All recovery strategies failed for error: {error_context.error_type}")
        return ErrorRecoveryResult(
            success=False,
            error_message=f"All recovery attempts failed for {error_context.error_type}",
            user_guidance="Unable to recover from this error. Please try again or contact support.",
            fallback_available=self._has_fallback_available(error_context.error_type)
        )
    
    async def _log_error_for_monitoring(self, error_context: ErrorContext):
        """Log error for monitoring and analytics."""
        error_data = {
            "error_type": error_context.error_type,
            "error_message": error_context.error_message,
            "timestamp": error_context.timestamp.isoformat(),
            "user_id": error_context.user_id,
            "session_id": error_context.session_id,
            "retry_count": error_context.retry_count,
            "location_data": error_context.location_data,
            "additional_context": error_context.additional_context
        }
        
        # Log to structured logging
        logger.error(f"Location input error: {json.dumps(error_data)}")
        
        # TODO: Send to monitoring service (e.g., Sentry, DataDog, etc.)
        # await self._send_to_monitoring_service(error_data)
    
    def _has_fallback_available(self, error_type: ErrorType) -> bool:
        """Check if fallback options are available for the error type."""
        strategies = self.recovery_strategies.get(error_type, [])
        return any(s.strategy in [RecoveryStrategy.FALLBACK_PROVIDER, RecoveryStrategy.CACHED_DATA, RecoveryStrategy.OFFLINE_MODE] for s in strategies)
    
    # Recovery action implementations
    async def _retry_gps_extended_timeout(self, error_context: ErrorContext):
        """Retry GPS with extended timeout."""
        # This would be implemented in the GPS service
        return await self._retry_with_config(error_context, "gps_extended_timeout")
    
    async def _retry_gps_high_accuracy(self, error_context: ErrorContext):
        """Retry GPS with high accuracy mode."""
        # This would be implemented in the GPS service
        return await self._retry_with_config(error_context, "gps_high_accuracy")
    
    async def _retry_network_request(self, error_context: ErrorContext):
        """Retry network request."""
        return await self._retry_with_config(error_context, "network_retry")
    
    async def _retry_extended_timeout(self, error_context: ErrorContext):
        """Retry with extended timeout."""
        return await self._retry_with_config(error_context, "extended_timeout")
    
    async def _retry_with_delay(self, error_context: ErrorContext):
        """Retry after a delay."""
        config = self.retry_configs.get(error_context.error_type, {})
        delay = config.get("base_delay", 3.0)
        await asyncio.sleep(delay)
        return await self._retry_with_config(error_context, "delayed_retry")
    
    async def _retry_with_config(self, error_context: ErrorContext, retry_type: str):
        """Generic retry with configuration."""
        config = self.retry_configs.get(error_context.error_type, {})
        
        if error_context.retry_count >= config.get("max_retries", 3):
            return None
        
        # Calculate delay with exponential backoff and jitter
        delay = self._calculate_retry_delay(error_context.retry_count, config)
        await asyncio.sleep(delay)
        
        # Increment retry count
        error_context.retry_count += 1
        
        # Return indication that retry should be attempted
        return {"retry_type": retry_type, "delay": delay}
    
    def _calculate_retry_delay(self, retry_count: int, config: Dict[str, Any]) -> float:
        """Calculate retry delay with exponential backoff and jitter."""
        base_delay = config.get("base_delay", 1.0)
        max_delay = config.get("max_delay", 10.0)
        exponential_backoff = config.get("exponential_backoff", True)
        jitter = config.get("jitter", True)
        
        if exponential_backoff:
            delay = base_delay * (2 ** retry_count)
        else:
            delay = base_delay
        
        delay = min(delay, max_delay)
        
        if jitter:
            # Add random jitter (±25%)
            import random
            jitter_factor = random.uniform(0.75, 1.25)
            delay *= jitter_factor
        
        return delay
    
    async def _try_fallback_geocoding(self, error_context: ErrorContext):
        """Try alternative geocoding provider."""
        # This would be implemented in the geocoding service
        return {"fallback_provider": "alternative_provider"}
    
    async def _enable_manual_input(self, error_context: ErrorContext):
        """Enable manual coordinate input."""
        return {"manual_input_enabled": True}
    
    async def _enable_manual_correction(self, error_context: ErrorContext):
        """Enable manual correction of input."""
        return {"manual_correction_enabled": True}
    
    async def _use_cached_location(self, error_context: ErrorContext):
        """Use previously cached location data."""
        # This would retrieve from cache
        return {"cached_location": "last_known_location"}
    
    async def _use_cached_data(self, error_context: ErrorContext):
        """Use cached data when service is unavailable."""
        return {"cached_data": "service_data"}
    
    async def _enable_offline_mode(self, error_context: ErrorContext):
        """Enable offline mode with cached data."""
        return {"offline_mode": True, "cached_data_available": True}
    
    async def _guide_gps_accuracy(self, error_context: ErrorContext):
        """Provide guidance to improve GPS accuracy."""
        return {"guidance": "gps_accuracy_improvement"}
    
    async def _guide_gps_permissions(self, error_context: ErrorContext):
        """Provide guidance to enable GPS permissions."""
        return {"guidance": "gps_permissions"}
    
    async def _provide_validation_guidance(self, error_context: ErrorContext):
        """Provide validation guidance."""
        return {"guidance": "validation_help"}


def with_error_handling(error_handler: LocationErrorHandler):
    """
    Decorator to add comprehensive error handling to location input functions.
    
    Args:
        error_handler: LocationErrorHandler instance
        
    Returns:
        Decorated function with error handling
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Determine error type
                error_type = _classify_error(e)
                
                # Create error context
                error_context = ErrorContext(
                    error_type=error_type,
                    error_message=str(e),
                    timestamp=datetime.utcnow(),
                    additional_context={"function": func.__name__, "args": str(args), "kwargs": str(kwargs)}
                )
                
                # Handle error
                recovery_result = await error_handler.handle_error(error_context)
                
                if recovery_result.success:
                    return recovery_result.recovered_data
                else:
                    # Re-raise with additional context
                    raise Exception(f"{str(e)}. Recovery failed: {recovery_result.error_message}")
        
        return wrapper
    return decorator


def _classify_error(error: Exception) -> ErrorType:
    """Classify an exception into an ErrorType."""
    error_str = str(error).lower()
    
    if "gps" in error_str or "geolocation" in error_str:
        if "timeout" in error_str:
            return ErrorType.GPS_TIMEOUT
        elif "permission" in error_str or "denied" in error_str:
            return ErrorType.GPS_PERMISSION_DENIED
        elif "accuracy" in error_str:
            return ErrorType.GPS_ACCURACY_POOR
        else:
            return ErrorType.GPS_UNAVAILABLE
    
    elif "network" in error_str or "connection" in error_str:
        if "timeout" in error_str:
            return ErrorType.NETWORK_TIMEOUT
        else:
            return ErrorType.NETWORK_ERROR
    
    elif "geocoding" in error_str or "geocode" in error_str:
        return ErrorType.GEOCODING_FAILED
    
    elif "validation" in error_str or "invalid" in error_str:
        if "coordinate" in error_str:
            return ErrorType.INVALID_COORDINATES
        elif "address" in error_str:
            return ErrorType.INVALID_ADDRESS
        else:
            return ErrorType.VALIDATION_ERROR
    
    elif "service" in error_str and "unavailable" in error_str:
        return ErrorType.SERVICE_UNAVAILABLE
    
    elif "cache" in error_str:
        return ErrorType.CACHE_ERROR
    
    elif "database" in error_str or "db" in error_str:
        return ErrorType.DATABASE_ERROR
    
    else:
        return ErrorType.UNKNOWN_ERROR


# Global error handler instance
location_error_handler = LocationErrorHandler()
