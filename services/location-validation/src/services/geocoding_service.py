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
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from urllib.parse import quote

import aiohttp
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from pydantic import BaseModel, Field, field_validator

from .agricultural_autocomplete_service import AgriculturalAutocompleteService, AgriculturalAddressSuggestion

logger = logging.getLogger(__name__)


class AgriculturalContext(BaseModel):
    """Agricultural context data for a location."""
    
    usda_zone: Optional[str] = Field(None, description="USDA Plant Hardiness Zone")
    climate_zone: Optional[str] = Field(None, description="Climate zone classification")
    soil_survey_area: Optional[str] = Field(None, description="USDA Soil Survey Area")
    agricultural_district: Optional[str] = Field(None, description="Agricultural district or region")
    county: Optional[str] = Field(None, description="County name")
    state: Optional[str] = Field(None, description="State or province")
    elevation_meters: Optional[float] = Field(None, description="Elevation in meters")
    growing_season_days: Optional[int] = Field(None, description="Typical growing season length")
    frost_free_days: Optional[int] = Field(None, description="Frost-free days")
    agricultural_suitability: Optional[str] = Field(None, description="Agricultural suitability rating")


class AgriculturalEnhancementService:
    """Service for enhancing geocoding results with agricultural context data."""
    
    def __init__(self):
        self.climate_service_url = "http://localhost:8003/api/v1/climate-zones/by-coordinates"
        self.soil_service_url = "http://localhost:8003/api/v1/soil/characteristics"
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get HTTP session for API calls."""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=5)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def enhance_with_agricultural_context(
        self, 
        latitude: float, 
        longitude: float,
        components: Dict[str, str]
    ) -> AgriculturalContext:
        """
        Enhance coordinates with agricultural context data.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            components: Address components from geocoding
            
        Returns:
            AgriculturalContext with enhanced data
        """
        try:
            # Get climate zone data
            climate_data = await self._get_climate_zone_data(latitude, longitude)
            
            # Get soil survey area data
            soil_data = await self._get_soil_survey_data(latitude, longitude)
            
            # Extract agricultural district from components
            agricultural_district = self._extract_agricultural_district(components)
            
            return AgriculturalContext(
                usda_zone=climate_data.get('usda_zone'),
                climate_zone=climate_data.get('climate_zone'),
                soil_survey_area=soil_data.get('soil_survey_area'),
                agricultural_district=agricultural_district,
                county=components.get('county'),
                state=components.get('state'),
                elevation_meters=climate_data.get('elevation_meters'),
                growing_season_days=climate_data.get('growing_season_days'),
                frost_free_days=climate_data.get('frost_free_days'),
                agricultural_suitability=climate_data.get('agricultural_suitability')
            )
            
        except Exception as e:
            logger.warning(f"Failed to enhance with agricultural context: {e}")
            # Return basic context from components
            return AgriculturalContext(
                county=components.get('county'),
                state=components.get('state')
            )
    
    async def _get_climate_zone_data(self, latitude: float, longitude: float) -> Dict[str, any]:
        """Get climate zone data from the climate service."""
        try:
            session = await self._get_session()
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'include_koppen': True
            }
            
            async with session.get(self.climate_service_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    primary_zone = data.get('primary_zone', {})
                    
                    return {
                        'usda_zone': primary_zone.get('hardiness_zone'),
                        'climate_zone': primary_zone.get('koppen_class'),
                        'elevation_meters': data.get('metadata', {}).get('elevation'),
                        'growing_season_days': data.get('metadata', {}).get('growing_season_days'),
                        'frost_free_days': data.get('metadata', {}).get('frost_free_days'),
                        'agricultural_suitability': data.get('metadata', {}).get('agricultural_suitability')
                    }
                else:
                    logger.warning(f"Climate service returned status {response.status}")
                    return {}
                    
        except Exception as e:
            logger.warning(f"Failed to get climate zone data: {e}")
            return {}
    
    async def _get_soil_survey_data(self, latitude: float, longitude: float) -> Dict[str, any]:
        """Get soil survey area data from the soil service."""
        try:
            session = await self._get_session()
            payload = {
                'latitude': latitude,
                'longitude': longitude
            }
            
            async with session.post(self.soil_service_url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'soil_survey_area': data.get('soil_survey_area'),
                        'soil_type': data.get('soil_type'),
                        'drainage_class': data.get('drainage_class')
                    }
                else:
                    logger.warning(f"Soil service returned status {response.status}")
                    return {}
                    
        except Exception as e:
            logger.warning(f"Failed to get soil survey data: {e}")
            return {}
    
    def _extract_agricultural_district(self, components: Dict[str, str]) -> Optional[str]:
        """Extract agricultural district information from address components."""
        # This is a simplified implementation
        # In production, this would integrate with USDA agricultural district databases
        
        state = components.get('state', '').lower()
        county = components.get('county', '').lower()
        
        # Map major agricultural regions
        agricultural_districts = {
            'iowa': 'Corn Belt',
            'illinois': 'Corn Belt', 
            'indiana': 'Corn Belt',
            'ohio': 'Corn Belt',
            'nebraska': 'Corn Belt',
            'minnesota': 'Corn Belt',
            'kansas': 'Wheat Belt',
            'north dakota': 'Wheat Belt',
            'south dakota': 'Wheat Belt',
            'montana': 'Wheat Belt',
            'california': 'Central Valley',
            'texas': 'Southern Plains',
            'florida': 'Southeast',
            'georgia': 'Southeast'
        }
        
        return agricultural_districts.get(state)
    
    async def close(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()


class GeocodingResult(BaseModel):
    """Result from geocoding an address."""
    
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: str
    display_name: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    provider: str
    components: Dict[str, str] = Field(default_factory=dict)
    agricultural_context: Optional[AgriculturalContext] = Field(None, description="Agricultural context data")
    
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
    agricultural_context: Optional[AgriculturalContext] = Field(None, description="Agricultural context data")


class AddressSuggestion(BaseModel):
    """Address suggestion for autocomplete."""
    
    display_name: str
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    relevance: float = Field(..., ge=0.0, le=1.0)
    components: Dict[str, str] = Field(default_factory=dict)


class BatchGeocodingRequest(BaseModel):
    """Request for batch geocoding multiple addresses."""
    
    addresses: List[str] = Field(..., min_items=1, max_items=100, description="List of addresses to geocode")
    include_agricultural_context: bool = Field(True, description="Include agricultural context data")


class BatchGeocodingResponse(BaseModel):
    """Response for batch geocoding requests."""
    
    results: List[GeocodingResult] = Field(..., description="Geocoding results for each address")
    failed_addresses: List[str] = Field(default_factory=list, description="Addresses that failed to geocode")
    processing_time_ms: float = Field(..., description="Total processing time in milliseconds")
    success_count: int = Field(..., description="Number of successfully geocoded addresses")
    failure_count: int = Field(..., description="Number of failed geocoding attempts")


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
    Enhanced with agricultural context data integration and comprehensive
    agricultural address autocomplete functionality.
    """
    
    def __init__(self):
        self.primary_provider = NominatimProvider()
        self.fallback_provider = None  # Can add MapBox or other providers later
        self.cache = GeocodingCache()
        self.agricultural_enhancement = AgriculturalEnhancementService()
        self.agricultural_autocomplete = AgriculturalAutocompleteService()
        self.agricultural_autocomplete.set_nominatim_provider(self.primary_provider)
        logger.info("Geocoding service initialized with Nominatim provider, agricultural enhancement, and agricultural autocomplete")
    
    async def geocode_address(self, address: str, include_agricultural_context: bool = True) -> GeocodingResult:
        """
        Convert address to GPS coordinates with optional agricultural context enhancement.
        
        Args:
            address: Street address to geocode
            include_agricultural_context: Whether to include agricultural context data
            
        Returns:
            GeocodingResult with coordinates, address details, and agricultural context
            
        Raises:
            GeocodingError: If geocoding fails with all providers
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
        
        # Try primary provider
        try:
            result = await self.primary_provider.geocode(address)
            
            # Enhance with agricultural context if requested
            if include_agricultural_context:
                agricultural_context = await self.agricultural_enhancement.enhance_with_agricultural_context(
                    result.latitude, result.longitude, result.components
                )
                result.agricultural_context = agricultural_context
            
            await self.cache.set(cache_key, result)
            logger.info(f"Successfully geocoded address: {address}")
            return result
        
        except GeocodingError as e:
            logger.warning(f"Primary provider failed for address '{address}': {e.message}")
            
            # Try fallback provider if available
            if self.fallback_provider:
                try:
                    result = await self.fallback_provider.geocode(address)
                    
                    # Enhance with agricultural context if requested
                    if include_agricultural_context:
                        agricultural_context = await self.agricultural_enhancement.enhance_with_agricultural_context(
                            result.latitude, result.longitude, result.components
                        )
                        result.agricultural_context = agricultural_context
                    
                    await self.cache.set(cache_key, result)
                    logger.info(f"Successfully geocoded address with fallback: {address}")
                    return result
                except GeocodingError as fallback_error:
                    logger.error(f"Fallback provider also failed for address '{address}': {fallback_error.message}")
            
            # All providers failed
            raise GeocodingError(f"Failed to geocode address '{address}': {e.message}")
    
    async def reverse_geocode(self, latitude: float, longitude: float, include_agricultural_context: bool = True) -> AddressResult:
        """
        Convert GPS coordinates to address with optional agricultural context enhancement.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            include_agricultural_context: Whether to include agricultural context data
            
        Returns:
            AddressResult with formatted address and agricultural context
            
        Raises:
            GeocodingError: If reverse geocoding fails
        """
        # Validate coordinates
        if not -90 <= latitude <= 90:
            raise GeocodingError(f"Invalid latitude: {latitude}")
        if not -180 <= longitude <= 180:
            raise GeocodingError(f"Invalid longitude: {longitude}")
        
        cache_key = f"reverse:{latitude:.6f},{longitude:.6f}:{include_agricultural_context}"
        
        # Check cache first
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            logger.debug(f"Returning cached reverse geocoding result for: {latitude}, {longitude}")
            return cached_result
        
        # Try primary provider
        try:
            result = await self.primary_provider.reverse_geocode(latitude, longitude)
            
            # Enhance with agricultural context if requested
            if include_agricultural_context:
                agricultural_context = await self.agricultural_enhancement.enhance_with_agricultural_context(
                    latitude, longitude, result.components
                )
                result.agricultural_context = agricultural_context
            
            await self.cache.set(cache_key, result)
            logger.info(f"Successfully reverse geocoded coordinates: {latitude}, {longitude}")
            return result
        
        except GeocodingError as e:
            logger.warning(f"Primary provider failed for coordinates {latitude}, {longitude}: {e.message}")
            
            # Try fallback provider if available
            if self.fallback_provider:
                try:
                    result = await self.fallback_provider.reverse_geocode(latitude, longitude)
                    
                    # Enhance with agricultural context if requested
                    if include_agricultural_context:
                        agricultural_context = await self.agricultural_enhancement.enhance_with_agricultural_context(
                            latitude, longitude, result.components
                        )
                        result.agricultural_context = agricultural_context
                    
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
    
    async def get_agricultural_address_suggestions(
        self, 
        query: str, 
        limit: int = 5,
        prioritize_agricultural: bool = True
    ) -> List[AgriculturalAddressSuggestion]:
        """
        Get comprehensive agricultural address autocomplete suggestions.
        
        This method provides enhanced address autocomplete functionality specifically
        designed for agricultural and rural addresses, integrating multiple data sources
        including USGS GNIS, USDA farm service agency, and postal service databases.
        
        Args:
            query: Address query string
            limit: Maximum number of suggestions to return
            prioritize_agricultural: Whether to prioritize agricultural locations
            
        Returns:
            List of AgriculturalAddressSuggestion objects with agricultural context
            
        Features:
            - Real-time address suggestions with agricultural focus
            - Rural address support (RR, HC, PO Box patterns)
            - Agricultural area prioritization
            - Farm-specific address patterns
            - Integration with agricultural databases
        """
        if not query or not query.strip():
            return []
        
        query = query.strip()
        if len(query) < 3:  # Don't search for very short queries
            return []
        
        cache_key = f"ag_suggestions:{query}:{limit}:{prioritize_agricultural}"
        
        # Check cache first
        cached_result = await self.cache.get(cache_key)
        if cached_result:
            logger.debug(f"Returning cached agricultural suggestions for: {query}")
            return cached_result
        
        try:
            # Get agricultural suggestions
            suggestions = await self.agricultural_autocomplete.get_agricultural_suggestions(
                query, limit, prioritize_agricultural
            )
            
            # Cache results
            await self.cache.set(cache_key, suggestions)
            
            logger.info(f"Successfully retrieved {len(suggestions)} agricultural suggestions for: {query}")
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting agricultural suggestions for '{query}': {e}")
            # Fallback to regular suggestions
            try:
                regular_suggestions = await self.get_address_suggestions(query, limit)
                # Convert to agricultural suggestions
                ag_suggestions = []
                for suggestion in regular_suggestions:
                    ag_suggestion = AgriculturalAddressSuggestion(
                        display_name=suggestion.display_name,
                        address=suggestion.address,
                        latitude=suggestion.latitude,
                        longitude=suggestion.longitude,
                        relevance=suggestion.relevance,
                        components=suggestion.components,
                        agricultural_type='general',
                        data_sources=['Nominatim_Fallback'],
                        confidence=0.6
                    )
                    ag_suggestions.append(ag_suggestion)
                return ag_suggestions
            except Exception as fallback_error:
                logger.error(f"Fallback suggestions also failed: {fallback_error}")
                return []
    
    async def batch_geocode(self, request: BatchGeocodingRequest) -> BatchGeocodingResponse:
        """
        Geocode multiple addresses in batch with agricultural context enhancement.
        
        Args:
            request: BatchGeocodingRequest with addresses and options
            
        Returns:
            BatchGeocodingResponse with results and statistics
        """
        start_time = time.time()
        results = []
        failed_addresses = []
        
        # Process addresses concurrently with semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(10)  # Limit to 10 concurrent requests
        
        async def geocode_single_address(address: str) -> Optional[GeocodingResult]:
            async with semaphore:
                try:
                    return await self.geocode_address(address, request.include_agricultural_context)
                except GeocodingError as e:
                    logger.warning(f"Failed to geocode address '{address}': {e.message}")
                    return None
        
        # Process all addresses concurrently
        tasks = [geocode_single_address(address) for address in request.addresses]
        geocoding_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(geocoding_results):
            address = request.addresses[i]
            
            if isinstance(result, Exception):
                failed_addresses.append(address)
                logger.error(f"Exception during geocoding of '{address}': {result}")
            elif result is None:
                failed_addresses.append(address)
            else:
                results.append(result)
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        return BatchGeocodingResponse(
            results=results,
            failed_addresses=failed_addresses,
            processing_time_ms=processing_time_ms,
            success_count=len(results),
            failure_count=len(failed_addresses)
        )
    
    async def close(self):
        """Close all provider connections."""
        await self.primary_provider.close()
        if self.fallback_provider:
            await self.fallback_provider.close()
        await self.agricultural_enhancement.close()
        logger.info("Geocoding service closed")


def get_geocoding_service() -> GeocodingService:
    """Get a new geocoding service instance."""
    return GeocodingService()


async def cleanup_geocoding_service():
    """Cleanup function for compatibility."""
    pass