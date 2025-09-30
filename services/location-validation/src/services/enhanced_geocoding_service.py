"""
Enhanced Geocoding Service with Comprehensive Error Handling
TICKET-008_farm-location-input-14.1: Implement comprehensive error handling and recovery

This enhanced service integrates with the error handling service to provide:
- Automatic retry mechanisms with exponential backoff
- Fallback provider support
- Graceful degradation
- Comprehensive error recovery
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import aiohttp
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

from .geocoding_service import (
    GeocodingResult, AddressResult, AddressSuggestion, 
    AgriculturalContext, AgriculturalEnhancementService,
    GeocodingCache, GeocodingError
)
from .error_handling_service import (
    LocationErrorHandler, ErrorType, ErrorContext, 
    ErrorRecoveryResult, RecoveryStrategy, with_error_handling
)

logger = logging.getLogger(__name__)


class EnhancedGeocodingService:
    """
    Enhanced geocoding service with comprehensive error handling and recovery.
    
    Provides robust geocoding with automatic retries, fallback providers,
    and graceful degradation for all error scenarios.
    """
    
    def __init__(self):
        self.primary_provider = NominatimProvider()
        self.fallback_providers = [
            MapBoxProvider(),
            GoogleMapsProvider()
        ]
        self.cache = GeocodingCache()
        self.agricultural_enhancement = AgriculturalEnhancementService()
        self.error_handler = LocationErrorHandler()
        
        # Retry configuration
        self.retry_config = {
            "max_retries": 3,
            "base_delay": 1.0,
            "max_delay": 10.0,
            "exponential_backoff": True,
            "jitter": True
        }
        
        logger.info("Enhanced geocoding service initialized with error handling")
    
    @with_error_handling
    async def geocode_address(
        self, 
        address: str, 
        include_agricultural_context: bool = True,
        retry_count: int = 0
    ) -> GeocodingResult:
        """
        Convert address to GPS coordinates with comprehensive error handling.
        
        Args:
            address: Street address to geocode
            include_agricultural_context: Whether to include agricultural context data
            retry_count: Current retry attempt (for internal use)
            
        Returns:
            GeocodingResult with coordinates, address details, and agricultural context
            
        Raises:
            GeocodingError: If geocoding fails with all providers and recovery strategies
        """
        if not address or not address.strip():
            raise GeocodingError("Address cannot be empty")
        
        address = address.strip()
        
        # Check cache first
        cache_key = f"geocode:{address}:{include_agricultural_context}"
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            logger.debug(f"Returning cached geocoding result for: {address}")
            return cached_result
        
        # Try primary provider with retry logic
        try:
            result = await self._geocode_with_retry(
                address, 
                include_agricultural_context,
                provider=self.primary_provider,
                retry_count=retry_count
            )
            
            if result:
                await self.cache.set(cache_key, result)
                logger.info(f"Successfully geocoded address: {address}")
                return result
        
        except Exception as e:
            logger.warning(f"Primary provider failed for address '{address}': {e}")
            
            # Try fallback providers
            for fallback_provider in self.fallback_providers:
                try:
                    logger.info(f"Trying fallback provider: {fallback_provider.__class__.__name__}")
                    result = await self._geocode_with_retry(
                        address,
                        include_agricultural_context,
                        provider=fallback_provider,
                        retry_count=0  # Reset retry count for fallback
                    )
                    
                    if result:
                        await self.cache.set(cache_key, result)
                        logger.info(f"Successfully geocoded address with fallback: {address}")
                        return result
                
                except Exception as fallback_error:
                    logger.warning(f"Fallback provider {fallback_provider.__class__.__name__} failed: {fallback_error}")
                    continue
            
            # All providers failed - create error context for recovery
            error_context = ErrorContext(
                error_type=ErrorType.GEOCODING_FAILED,
                error_message=f"All geocoding providers failed for address '{address}': {str(e)}",
                timestamp=datetime.utcnow(),
                location_data={"address": address},
                retry_count=retry_count,
                additional_context={
                    "include_agricultural_context": include_agricultural_context,
                    "providers_tried": [self.primary_provider.__class__.__name__] + 
                                     [p.__class__.__name__ for p in self.fallback_providers]
                }
            )
            
            # Handle error with recovery strategies
            recovery_result = await self.error_handler.handle_error(error_context)
            
            if recovery_result.success:
                logger.info(f"Recovery successful: {recovery_result.recovery_strategy_used}")
                return recovery_result.recovered_data
            else:
                raise GeocodingError(f"Failed to geocode address '{address}': {recovery_result.error_message}")
    
    async def _geocode_with_retry(
        self,
        address: str,
        include_agricultural_context: bool,
        provider,
        retry_count: int = 0
    ) -> Optional[GeocodingResult]:
        """
        Geocode address with automatic retry mechanism.
        
        Args:
            address: Address to geocode
            include_agricultural_context: Whether to include agricultural context
            provider: Geocoding provider to use
            retry_count: Current retry attempt
            
        Returns:
            GeocodingResult if successful, None if failed
        """
        max_retries = self.retry_config["max_retries"]
        
        for attempt in range(max_retries + 1):
            try:
                logger.debug(f"Geocoding attempt {attempt + 1}/{max_retries + 1} for: {address}")
                
                # Attempt geocoding
                result = await provider.geocode(address)
                
                if result:
                    # Enhance with agricultural context if requested
                    if include_agricultural_context:
                        agricultural_context = await self.agricultural_enhancement.enhance_with_agricultural_context(
                            result.latitude, result.longitude, result.components
                        )
                        result.agricultural_context = agricultural_context
                    
                    return result
                else:
                    raise GeocodingError(f"No results found for address: {address}")
            
            except (GeocoderTimedOut, asyncio.TimeoutError) as e:
                logger.warning(f"Timeout on attempt {attempt + 1} for address '{address}': {e}")
                
                if attempt < max_retries:
                    delay = self._calculate_retry_delay(attempt)
                    logger.info(f"Retrying in {delay:.2f} seconds...")
                    await asyncio.sleep(delay)
                    continue
                else:
                    raise GeocodingError(f"Geocoding timeout after {max_retries + 1} attempts: {e}")
            
            except (GeocoderServiceError, aiohttp.ClientError) as e:
                logger.warning(f"Service error on attempt {attempt + 1} for address '{address}': {e}")
                
                if attempt < max_retries:
                    delay = self._calculate_retry_delay(attempt)
                    logger.info(f"Retrying in {delay:.2f} seconds...")
                    await asyncio.sleep(delay)
                    continue
                else:
                    raise GeocodingError(f"Geocoding service error after {max_retries + 1} attempts: {e}")
            
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1} for address '{address}': {e}")
                raise GeocodingError(f"Unexpected geocoding error: {e}")
        
        return None
    
    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate retry delay with exponential backoff and jitter."""
        base_delay = self.retry_config["base_delay"]
        max_delay = self.retry_config["max_delay"]
        exponential_backoff = self.retry_config["exponential_backoff"]
        jitter = self.retry_config["jitter"]
        
        if exponential_backoff:
            delay = base_delay * (2 ** attempt)
        else:
            delay = base_delay
        
        delay = min(delay, max_delay)
        
        if jitter:
            # Add random jitter (±25%)
            import random
            jitter_factor = random.uniform(0.75, 1.25)
            delay *= jitter_factor
        
        return delay


class NominatimProvider:
    """Enhanced Nominatim provider with error handling."""
    
    def __init__(self):
        self.geocoder = Nominatim(user_agent="CAAIN-Soil-Hub/1.0")
        self.timeout = 10
    
    async def geocode(self, address: str) -> GeocodingResult:
        """Geocode address using Nominatim."""
        try:
            location = self.geocoder.geocode(address, timeout=self.timeout)
            
            if location:
                return GeocodingResult(
                    latitude=location.latitude,
                    longitude=location.longitude,
                    formatted_address=location.address,
                    confidence=0.8,  # Nominatim confidence
                    source="Nominatim",
                    components=self._extract_components(location.raw)
                )
            else:
                raise GeocodingError(f"No results found for address: {address}")
        
        except Exception as e:
            raise GeocodingError(f"Nominatim geocoding failed: {str(e)}")
    
    async def reverse_geocode(self, latitude: float, longitude: float) -> AddressResult:
        """Reverse geocode coordinates using Nominatim."""
        try:
            location = self.geocoder.reverse(f"{latitude}, {longitude}", timeout=self.timeout)
            
            if location:
                return AddressResult(
                    formatted_address=location.address,
                    confidence=0.8,
                    source="Nominatim",
                    components=self._extract_components(location.raw)
                )
            else:
                raise GeocodingError(f"No results found for coordinates: {latitude}, {longitude}")
        
        except Exception as e:
            raise GeocodingError(f"Nominatim reverse geocoding failed: {str(e)}")
    
    async def search_suggestions(self, query: str, limit: int) -> List[AddressSuggestion]:
        """Search for address suggestions using Nominatim."""
        try:
            locations = self.geocoder.geocode(query, exactly_one=False, limit=limit)
            
            suggestions = []
            for location in locations or []:
                suggestions.append(AddressSuggestion(
                    address=location.address,
                    latitude=location.latitude,
                    longitude=location.longitude,
                    confidence=0.7,
                    source="Nominatim"
                ))
            
            return suggestions
        
        except Exception as e:
            raise GeocodingError(f"Nominatim suggestions failed: {str(e)}")
    
    def _extract_components(self, raw_data: dict) -> dict:
        """Extract address components from Nominatim raw data."""
        components = {}
        
        if 'address' in raw_data:
            address_data = raw_data['address']
            components.update({
                'house_number': address_data.get('house_number'),
                'road': address_data.get('road'),
                'city': address_data.get('city') or address_data.get('town') or address_data.get('village'),
                'state': address_data.get('state'),
                'postal_code': address_data.get('postcode'),
                'country': address_data.get('country')
            })
        
        return components


class MapBoxProvider:
    """MapBox provider implementation (placeholder)."""
    
    def __init__(self):
        self.api_key = None  # Would be configured from environment
        self.base_url = "https://api.mapbox.com/geocoding/v5/mapbox.places"
    
    async def geocode(self, address: str) -> GeocodingResult:
        """Geocode address using MapBox (placeholder implementation)."""
        # This would implement MapBox geocoding API
        raise GeocodingError("MapBox provider not implemented")
    
    async def reverse_geocode(self, latitude: float, longitude: float) -> AddressResult:
        """Reverse geocode coordinates using MapBox (placeholder implementation)."""
        # This would implement MapBox reverse geocoding API
        raise GeocodingError("MapBox provider not implemented")
    
    async def search_suggestions(self, query: str, limit: int) -> List[AddressSuggestion]:
        """Search for address suggestions using MapBox (placeholder implementation)."""
        # This would implement MapBox suggestions API
        raise GeocodingError("MapBox provider not implemented")


class GoogleMapsProvider:
    """Google Maps provider implementation (placeholder)."""
    
    def __init__(self):
        self.api_key = None  # Would be configured from environment
        self.base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    
    async def geocode(self, address: str) -> GeocodingResult:
        """Geocode address using Google Maps (placeholder implementation)."""
        # This would implement Google Maps geocoding API
        raise GeocodingError("Google Maps provider not implemented")
    
    async def reverse_geocode(self, latitude: float, longitude: float) -> AddressResult:
        """Reverse geocode coordinates using Google Maps (placeholder implementation)."""
        # This would implement Google Maps reverse geocoding API
        raise GeocodingError("Google Maps provider not implemented")
    
    async def search_suggestions(self, query: str, limit: int) -> List[AddressSuggestion]:
        """Search for address suggestions using Google Maps (placeholder implementation)."""
        # This would implement Google Maps suggestions API
        raise GeocodingError("Google Maps provider not implemented")


# Global enhanced geocoding service instance
enhanced_geocoding_service = EnhancedGeocodingService()
