"""
Geocoding service for converting addresses to coordinates and vice versa.

This service implements the geocoding functionality required for the farm location input system,
providing address-to-coordinates conversion, reverse geocoding, and address autocomplete
with caching and fallback providers for reliability.
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from urllib.parse import quote

import aiohttp
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class GeocodingResult(BaseModel):
    """Result from geocoding an address."""
    
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: str
    display_name: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    provider: str
    components: Dict[str, str] = Field(default_factory=dict)
    
    @field_validator('latitude')
    @classmethod
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Latitude must be between -90 and 90 degrees')
        return v
    
    @field_validator('longitude')
    @classmethod
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Longitude must be between -180 and 180 degrees')
        return v


class AddressResult(BaseModel):
    """Result from reverse geocoding coordinates."""
    
    address: str
    display_name: str
    components: Dict[str, str] = Field(default_factory=dict)
    confidence: float = Field(..., ge=0.0, le=1.0)
    provider: str


class AddressSuggestion(BaseModel):
    """Address suggestion for autocomplete."""
    
    display_name: str
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    relevance: float = Field(..., ge=0.0, le=1.0)
    components: Dict[str, str] = Field(default_factory=dict)


class GeocodingError(Exception):
    """Exception raised when geocoding fails."""
    
    def __init__(self, message: str, provider: str = None, original_error: Exception = None):
        self.message = message
        self.provider = provider
        self.original_error = original_error
        super().__init__(message)


class GeocodingCache:
    """Simple in-memory cache for geocoding results."""
    
    def __init__(self, max_size: int = 1000, ttl_hours: int = 24):
        self._cache: Dict[str, Dict] = {}
        self.max_size = max_size
        self.ttl = timedelta(hours=ttl_hours)
    
    def _generate_key(self, query: str) -> str:
        """Generate cache key from query."""
        return hashlib.md5(query.lower().encode()).hexdigest()
    
    async def get(self, query: str) -> Optional[Union[GeocodingResult, AddressResult, List[AddressSuggestion]]]:
        """Get cached result."""
        key = self._generate_key(query)
        
        if key in self._cache:
            entry = self._cache[key]
            if datetime.now() - entry['timestamp'] < self.ttl:
                logger.debug(f"Cache hit for query: {query}")
                return entry['result']
            else:
                # Remove expired entry
                del self._cache[key]
        
        return None
    
    async def set(self, query: str, result: Union[GeocodingResult, AddressResult, List[AddressSuggestion]]):
        """Cache result."""
        key = self._generate_key(query)
        
        # Remove oldest entries if cache is full
        if len(self._cache) >= self.max_size:
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k]['timestamp'])
            del self._cache[oldest_key]
        
        self._cache[key] = {
            'result': result,
            'timestamp': datetime.now()
        }
        logger.debug(f"Cached result for query: {query}")


class NominatimProvider:
    """Nominatim (OpenStreetMap) geocoding provider."""
    
    def __init__(self, user_agent: str = "AFAS-Location-Service/1.0"):
        self.user_agent = user_agent
        self.base_url = "https://nominatim.openstreetmap.org"
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get a new HTTP session for each request."""
        timeout = aiohttp.ClientTimeout(total=10)
        return aiohttp.ClientSession(
            timeout=timeout,
            headers={'User-Agent': self.user_agent}
        )
    
    async def geocode(self, address: str) -> GeocodingResult:
        """Geocode an address using Nominatim."""
        session = await self._get_session()
        
        params = {
            'q': address,
            'format': 'json',
            'addressdetails': '1',
            'limit': '1',
            'countrycodes': 'us,ca'  # Focus on North America for agricultural use
        }
        
        url = f"{self.base_url}/search"
        
        try:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    raise GeocodingError(f"Nominatim API returned status {response.status}", "nominatim")
                
                data = await response.json()
                
                if not data:
                    raise GeocodingError(f"No results found for address: {address}", "nominatim")
                
                result = data[0]
                
                # Extract address components
                components = result.get('address', {})
                
                return GeocodingResult(
                    latitude=float(result['lat']),
                    longitude=float(result['lon']),
                    address=self._format_address(components),
                    display_name=result['display_name'],
                    confidence=self._calculate_confidence(result),
                    provider="nominatim",
                    components=components
                )
        
        except aiohttp.ClientError as e:
            raise GeocodingError(f"Network error: {str(e)}", "nominatim", e)
        except (KeyError, ValueError, TypeError) as e:
            raise GeocodingError(f"Invalid response format: {str(e)}", "nominatim", e)
        finally:
            await session.close()
    
    async def reverse_geocode(self, latitude: float, longitude: float) -> AddressResult:
        """Reverse geocode coordinates using Nominatim."""
        session = await self._get_session()
        
        params = {
            'lat': str(latitude),
            'lon': str(longitude),
            'format': 'json',
            'addressdetails': '1'
        }
        
        url = f"{self.base_url}/reverse"
        
        try:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    raise GeocodingError(f"Nominatim reverse API returned status {response.status}", "nominatim")
                
                data = await response.json()
                
                if 'error' in data:
                    raise GeocodingError(f"Reverse geocoding failed: {data['error']}", "nominatim")
                
                # Extract address components
                components = data.get('address', {})
                
                return AddressResult(
                    address=self._format_address(components),
                    display_name=data['display_name'],
                    components=components,
                    confidence=self._calculate_confidence(data),
                    provider="nominatim"
                )
        
        except aiohttp.ClientError as e:
            raise GeocodingError(f"Network error: {str(e)}", "nominatim", e)
        except (KeyError, ValueError, TypeError) as e:
            raise GeocodingError(f"Invalid response format: {str(e)}", "nominatim", e)
        finally:
            await session.close()
    
    async def search_suggestions(self, query: str, limit: int = 5) -> List[AddressSuggestion]:
        """Get address suggestions for autocomplete."""
        session = await self._get_session()
        
        params = {
            'q': query,
            'format': 'json',
            'addressdetails': '1',
            'limit': str(limit),
            'countrycodes': 'us,ca'
        }
        
        url = f"{self.base_url}/search"
        
        try:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    raise GeocodingError(f"Nominatim search API returned status {response.status}", "nominatim")
                
                data = await response.json()
                
                suggestions = []
                for i, result in enumerate(data):
                    components = result.get('address', {})
                    
                    suggestion = AddressSuggestion(
                        display_name=result['display_name'],
                        address=self._format_address(components),
                        latitude=float(result['lat']),
                        longitude=float(result['lon']),
                        relevance=max(0.1, 1.0 - (i * 0.1)),  # Decrease relevance by position
                        components=components
                    )
                    suggestions.append(suggestion)
                
                return suggestions
        
        except aiohttp.ClientError as e:
            raise GeocodingError(f"Network error: {str(e)}", "nominatim", e)
        except (KeyError, ValueError, TypeError) as e:
            raise GeocodingError(f"Invalid response format: {str(e)}", "nominatim", e)
        finally:
            await session.close()
    
    def _format_address(self, components: Dict[str, str]) -> str:
        """Format address components into a readable address."""
        parts = []
        
        # House number and street
        if 'house_number' in components and 'road' in components:
            parts.append(f"{components['house_number']} {components['road']}")
        elif 'road' in components:
            parts.append(components['road'])
        
        # City
        city = components.get('city') or components.get('town') or components.get('village')
        if city:
            parts.append(city)
        
        # State
        if 'state' in components:
            parts.append(components['state'])
        
        # Postal code
        if 'postcode' in components:
            parts.append(components['postcode'])
        
        return ', '.join(parts) if parts else components.get('display_name', '')
    
    def _calculate_confidence(self, result: Dict) -> float:
        """Calculate confidence score based on result quality."""
        confidence = 0.7  # Base confidence for Nominatim
        
        # Increase confidence if we have detailed address components
        address = result.get('address', {})
        if 'house_number' in address:
            confidence += 0.2
        if 'road' in address:
            confidence += 0.1
        
        # Decrease confidence for very general results
        if result.get('class') == 'place' and result.get('type') in ['country', 'state']:
            confidence -= 0.3
        
        return min(1.0, max(0.1, confidence))
    
    async def close(self):
        """Close method for compatibility."""
        pass


class GeocodingService:
    """
    Main geocoding service with multiple providers and caching.
    
    Implements address-to-coordinates conversion, reverse geocoding,
    and address autocomplete with fallback providers for reliability.
    """
    
    def __init__(self):
        self.primary_provider = NominatimProvider()
        self.fallback_provider = None  # Can add MapBox or other providers later
        self.cache = GeocodingCache()
        logger.info("Geocoding service initialized with Nominatim provider")
    
    async def geocode_address(self, address: str) -> GeocodingResult:
        """
        Convert address to GPS coordinates.
        
        Args:
            address: Street address to geocode
            
        Returns:
            GeocodingResult with coordinates and address details
            
        Raises:
            GeocodingError: If geocoding fails with all providers
        """
        if not address or not address.strip():
            raise GeocodingError("Address cannot be empty")
        
        address = address.strip()
        
        # Check cache first
        cached_result = await self.cache.get(f"geocode:{address}")
        if cached_result:
            logger.debug(f"Returning cached geocoding result for: {address}")
            return cached_result
        
        # Try primary provider
        try:
            result = await self.primary_provider.geocode(address)
            await self.cache.set(f"geocode:{address}", result)
            logger.info(f"Successfully geocoded address: {address}")
            return result
        
        except GeocodingError as e:
            logger.warning(f"Primary provider failed for address '{address}': {e.message}")
            
            # Try fallback provider if available
            if self.fallback_provider:
                try:
                    result = await self.fallback_provider.geocode(address)
                    await self.cache.set(f"geocode:{address}", result)
                    logger.info(f"Successfully geocoded address with fallback: {address}")
                    return result
                except GeocodingError as fallback_error:
                    logger.error(f"Fallback provider also failed for address '{address}': {fallback_error.message}")
            
            # All providers failed
            raise GeocodingError(f"Failed to geocode address '{address}': {e.message}")
    
    async def reverse_geocode(self, latitude: float, longitude: float) -> AddressResult:
        """
        Convert GPS coordinates to address.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            
        Returns:
            AddressResult with formatted address
            
        Raises:
            GeocodingError: If reverse geocoding fails
        """
        # Validate coordinates
        if not -90 <= latitude <= 90:
            raise GeocodingError(f"Invalid latitude: {latitude}")
        if not -180 <= longitude <= 180:
            raise GeocodingError(f"Invalid longitude: {longitude}")
        
        cache_key = f"reverse:{latitude:.6f},{longitude:.6f}"
        
        # Check cache first
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            logger.debug(f"Returning cached reverse geocoding result for: {latitude}, {longitude}")
            return cached_result
        
        # Try primary provider
        try:
            result = await self.primary_provider.reverse_geocode(latitude, longitude)
            await self.cache.set(cache_key, result)
            logger.info(f"Successfully reverse geocoded coordinates: {latitude}, {longitude}")
            return result
        
        except GeocodingError as e:
            logger.warning(f"Primary provider failed for coordinates {latitude}, {longitude}: {e.message}")
            
            # Try fallback provider if available
            if self.fallback_provider:
                try:
                    result = await self.fallback_provider.reverse_geocode(latitude, longitude)
                    await self.cache.set(cache_key, result)
                    logger.info(f"Successfully reverse geocoded coordinates with fallback: {latitude}, {longitude}")
                    return result
                except GeocodingError as fallback_error:
                    logger.error(f"Fallback provider also failed for coordinates {latitude}, {longitude}: {fallback_error.message}")
            
            # All providers failed
            raise GeocodingError(f"Failed to reverse geocode coordinates {latitude}, {longitude}: {e.message}")
    
    async def get_address_suggestions(self, query: str, limit: int = 5) -> List[AddressSuggestion]:
        """
        Get address autocomplete suggestions.
        
        Args:
            query: Partial address query
            limit: Maximum number of suggestions to return
            
        Returns:
            List of AddressSuggestion objects
            
        Raises:
            GeocodingError: If suggestion lookup fails
        """
        if not query or not query.strip():
            return []
        
        query = query.strip()
        if len(query) < 3:  # Don't search for very short queries
            return []
        
        cache_key = f"suggestions:{query}:{limit}"
        
        # Check cache first
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            logger.debug(f"Returning cached suggestions for: {query}")
            return cached_result
        
        # Try primary provider
        try:
            suggestions = await self.primary_provider.search_suggestions(query, limit)
            await self.cache.set(cache_key, suggestions)
            logger.info(f"Successfully retrieved {len(suggestions)} suggestions for: {query}")
            return suggestions
        
        except GeocodingError as e:
            logger.warning(f"Failed to get suggestions for '{query}': {e.message}")
            
            # Try fallback provider if available
            if self.fallback_provider:
                try:
                    suggestions = await self.fallback_provider.search_suggestions(query, limit)
                    await self.cache.set(cache_key, suggestions)
                    logger.info(f"Successfully retrieved {len(suggestions)} suggestions with fallback for: {query}")
                    return suggestions
                except GeocodingError:
                    pass
            
            # Return empty list if all providers fail for suggestions
            logger.error(f"All providers failed for suggestions query: {query}")
            return []
    
    async def close(self):
        """Close all provider connections."""
        await self.primary_provider.close()
        if self.fallback_provider:
            await self.fallback_provider.close()
        logger.info("Geocoding service closed")


def get_geocoding_service() -> GeocodingService:
    """Get a new geocoding service instance."""
    return GeocodingService()


async def cleanup_geocoding_service():
    """Cleanup function for compatibility."""
    pass