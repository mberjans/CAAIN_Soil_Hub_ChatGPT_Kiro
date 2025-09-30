"""
Current Location Detection Service
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

Comprehensive current location detection system with multiple fallback methods:
- GPS location detection with high-accuracy and assisted GPS
- IP-based geolocation fallback
- Manual location entry
- Location history management
- Privacy controls and location permission management
- Battery optimization and location caching
"""

import logging
import asyncio
import json
import time
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import aiohttp
import hashlib
from uuid import uuid4

# Initialize logger
logger = logging.getLogger(__name__)

# Import existing models and services
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../databases/python'))

from location_models import ValidationResult, GeographicInfo
from location_validation_service import LocationValidationService


class LocationSource(str, Enum):
    """Sources for location detection."""
    GPS = "gps"
    IP_GEOLOCATION = "ip_geolocation"
    MANUAL_ENTRY = "manual_entry"
    SAVED_LOCATION = "saved_location"
    NETWORK_LOCATION = "network_location"
    CELL_TOWER = "cell_tower"
    WIFI_NETWORK = "wifi_network"


class LocationAccuracy(str, Enum):
    """Location accuracy levels."""
    HIGH = "high"          # < 10 meters
    MEDIUM = "medium"      # 10-100 meters
    LOW = "low"           # 100-1000 meters
    VERY_LOW = "very_low"  # > 1000 meters


@dataclass
class LocationReading:
    """Represents a single location reading."""
    latitude: float
    longitude: float
    accuracy_meters: Optional[float] = None
    altitude: Optional[float] = None
    heading: Optional[float] = None
    speed: Optional[float] = None
    timestamp: datetime = None
    source: LocationSource = LocationSource.GPS
    confidence_score: float = 1.0
    battery_level: Optional[int] = None
    network_type: Optional[str] = None
    satellite_count: Optional[int] = None
    hdop: Optional[float] = None  # Horizontal Dilution of Precision
    vdop: Optional[float] = None  # Vertical Dilution of Precision
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class LocationDetectionResult:
    """Result of location detection process."""
    success: bool
    location: Optional[LocationReading] = None
    fallback_used: Optional[LocationSource] = None
    error_message: Optional[str] = None
    confidence_score: float = 0.0
    detection_time_ms: float = 0.0
    battery_impact: str = "low"
    privacy_level: str = "standard"
    validation_result: Optional[ValidationResult] = None


@dataclass
class LocationHistoryEntry:
    """Entry in location history."""
    id: str
    location: LocationReading
    user_id: str
    session_id: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_favorite: bool = False
    notes: Optional[str] = None


class CurrentLocationDetectionService:
    """
    Comprehensive current location detection service with multiple fallback methods.
    
    Features:
    - GPS location detection with high-accuracy and assisted GPS
    - IP-based geolocation fallback
    - Manual location entry
    - Location history management
    - Privacy controls and location permission management
    - Battery optimization and location caching
    """
    
    def __init__(self):
        """Initialize the current location detection service."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize validation service
        self.validation_service = LocationValidationService()
        
        # Location detection configuration
        self.config = {
            'gps_timeout_seconds': 15,
            'gps_high_accuracy': True,
            'gps_maximum_age_seconds': 300,  # 5 minutes
            'ip_geolocation_timeout_seconds': 10,
            'location_cache_ttl_seconds': 3600,  # 1 hour
            'battery_optimization_enabled': True,
            'privacy_mode_enabled': True,
            'location_history_enabled': True,
            'max_location_history_entries': 50,
            'location_history_ttl_days': 30
        }
        
        # Location history storage (in production, this would be a database)
        self.location_history: List[LocationHistoryEntry] = []
        
        # Location cache
        self.location_cache: Dict[str, LocationReading] = {}
        
        # IP geolocation providers
        self.ip_geolocation_providers = [
            {
                'name': 'ipapi',
                'url': 'https://ipapi.co/{ip}/json/',
                'timeout': 5,
                'priority': 1
            },
            {
                'name': 'ipinfo',
                'url': 'https://ipinfo.io/{ip}/json',
                'timeout': 5,
                'priority': 2
            },
            {
                'name': 'freeipapi',
                'url': 'https://freeipapi.com/api/json/{ip}',
                'timeout': 5,
                'priority': 3
            }
        ]
        
        # Battery optimization settings
        self.battery_optimization = {
            'low_battery_threshold': 20,  # percentage
            'reduced_accuracy_mode': True,
            'reduced_frequency_mode': True,
            'background_location_disabled': True
        }
    
    async def detect_current_location(
        self,
        user_id: str,
        session_id: str,
        preferred_sources: List[LocationSource] = None,
        privacy_level: str = "standard",
        battery_level: Optional[int] = None
    ) -> LocationDetectionResult:
        """
        Detect current location using multiple fallback methods.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            preferred_sources: Preferred location sources in order
            privacy_level: Privacy level (minimal, standard, enhanced)
            battery_level: Current battery level percentage
            
        Returns:
            LocationDetectionResult with detection outcome
        """
        start_time = time.time()
        
        # Set default preferred sources if not provided
        if preferred_sources is None:
            preferred_sources = [
                LocationSource.GPS,
                LocationSource.IP_GEOLOCATION,
                LocationSource.SAVED_LOCATION,
                LocationSource.MANUAL_ENTRY
            ]
        
        # Check battery optimization
        if battery_level is not None and battery_level < self.battery_optimization['low_battery_threshold']:
            self.logger.info(f"Low battery detected ({battery_level}%), enabling battery optimization")
            preferred_sources = self._optimize_sources_for_battery(preferred_sources)
        
        # Try each source in order
        for source in preferred_sources:
            try:
                self.logger.info(f"Attempting location detection using {source.value}")
                
                if source == LocationSource.GPS:
                    result = await self._detect_gps_location(battery_level)
                elif source == LocationSource.IP_GEOLOCATION:
                    result = await self._detect_ip_location()
                elif source == LocationSource.SAVED_LOCATION:
                    result = await self._get_saved_location(user_id)
                elif source == LocationSource.MANUAL_ENTRY:
                    result = await self._get_manual_location()
                else:
                    continue
                
                if result and result.success:
                    # Validate the detected location
                    validation_result = await self.validation_service.validate_coordinates(
                        result.location.latitude,
                        result.location.longitude
                    )
                    
                    # Store in location history
                    if self.config['location_history_enabled']:
                        await self._store_location_history(
                            result.location, user_id, session_id, source
                        )
                    
                    # Cache the location
                    await self._cache_location(result.location, user_id)
                    
                    detection_time = (time.time() - start_time) * 1000
                    
                    return LocationDetectionResult(
                        success=True,
                        location=result.location,
                        fallback_used=source,
                        confidence_score=result.confidence_score,
                        detection_time_ms=detection_time,
                        battery_impact=self._assess_battery_impact(source, battery_level),
                        privacy_level=privacy_level,
                        validation_result=validation_result
                    )
                
            except Exception as e:
                self.logger.warning(f"Location detection failed for {source.value}: {e}")
                continue
        
        # All methods failed
        detection_time = (time.time() - start_time) * 1000
        
        return LocationDetectionResult(
            success=False,
            error_message="All location detection methods failed",
            detection_time_ms=detection_time,
            battery_impact="minimal"
        )
    
    async def _detect_gps_location(self, battery_level: Optional[int] = None) -> Optional[LocationDetectionResult]:
        """Detect location using GPS."""
        try:
            # This would integrate with browser geolocation API in the frontend
            # For backend service, we simulate GPS detection
            self.logger.info("GPS location detection requested")
            
            # In a real implementation, this would:
            # 1. Request GPS permission from user
            # 2. Use navigator.geolocation.getCurrentPosition()
            # 3. Handle various GPS accuracy levels
            # 4. Implement assisted GPS if available
            
            # For now, return a simulated result
            # In production, this would be handled by the frontend JavaScript
            
            return LocationDetectionResult(
                success=False,
                error_message="GPS detection requires frontend integration"
            )
            
        except Exception as e:
            self.logger.error(f"GPS detection error: {e}")
            return None
    
    async def _detect_ip_location(self) -> Optional[LocationDetectionResult]:
        """Detect location using IP geolocation."""
        try:
            # Get user's IP address (in production, this would come from request)
            user_ip = await self._get_user_ip()
            
            if not user_ip:
                return None
            
            # Try each IP geolocation provider
            for provider in sorted(self.ip_geolocation_providers, key=lambda x: x['priority']):
                try:
                    location_data = await self._query_ip_provider(provider, user_ip)
                    if location_data:
                        location_reading = self._parse_ip_location_data(location_data, provider['name'])
                        if location_reading:
                            return LocationDetectionResult(
                                success=True,
                                location=location_reading,
                                confidence_score=0.7  # IP geolocation is less accurate
                            )
                except Exception as e:
                    self.logger.warning(f"IP provider {provider['name']} failed: {e}")
                    continue
            
            return None
            
        except Exception as e:
            self.logger.error(f"IP geolocation error: {e}")
            return None
    
    async def _get_user_ip(self) -> Optional[str]:
        """Get user's IP address."""
        # In production, this would extract IP from request headers
        # For now, return a placeholder
        return "8.8.8.8"  # Google DNS as placeholder
    
    async def _query_ip_provider(self, provider: Dict, ip: str) -> Optional[Dict]:
        """Query an IP geolocation provider."""
        url = provider['url'].format(ip=ip)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=provider['timeout']) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    self.logger.warning(f"IP provider {provider['name']} returned status {response.status}")
                    return None
    
    def _parse_ip_location_data(self, data: Dict, provider: str) -> Optional[LocationReading]:
        """Parse IP geolocation data into LocationReading."""
        try:
            # Parse data based on provider format
            if provider == 'ipapi':
                latitude = float(data.get('latitude', 0))
                longitude = float(data.get('longitude', 0))
                city = data.get('city', '')
                region = data.get('region', '')
                country = data.get('country_name', '')
                
            elif provider == 'ipinfo':
                coords = data.get('loc', '').split(',')
                if len(coords) != 2:
                    return None
                latitude = float(coords[0])
                longitude = float(coords[1])
                city = data.get('city', '')
                region = data.get('region', '')
                country = data.get('country', '')
                
            elif provider == 'freeipapi':
                latitude = float(data.get('latitude', 0))
                longitude = float(data.get('longitude', 0))
                city = data.get('cityName', '')
                region = data.get('regionName', '')
                country = data.get('countryName', '')
                
            else:
                return None
            
            # Validate coordinates
            if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
                return None
            
            return LocationReading(
                latitude=latitude,
                longitude=longitude,
                accuracy_meters=1000.0,  # IP geolocation is typically accurate to ~1km
                source=LocationSource.IP_GEOLOCATION,
                confidence_score=0.7,
                timestamp=datetime.utcnow()
            )
            
        except (ValueError, KeyError, TypeError) as e:
            self.logger.error(f"Error parsing IP location data from {provider}: {e}")
            return None
    
    async def _get_saved_location(self, user_id: str) -> Optional[LocationDetectionResult]:
        """Get a saved/favorite location for the user."""
        try:
            # Look for recent saved locations
            recent_saved = [
                entry for entry in self.location_history
                if entry.user_id == user_id and entry.is_favorite
            ]
            
            if recent_saved:
                # Return the most recent favorite location
                latest_saved = max(recent_saved, key=lambda x: x.created_at)
                return LocationDetectionResult(
                    success=True,
                    location=latest_saved.location,
                    confidence_score=0.9  # Saved locations are highly trusted
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting saved location: {e}")
            return None
    
    async def _get_manual_location(self) -> Optional[LocationDetectionResult]:
        """Get manually entered location."""
        # This would typically be handled by the frontend
        # For backend service, we return None to indicate manual entry is needed
        return None
    
    def _optimize_sources_for_battery(self, sources: List[LocationSource]) -> List[LocationSource]:
        """Optimize location sources for battery conservation."""
        # Remove GPS and other battery-intensive sources when battery is low
        battery_friendly_sources = [
            LocationSource.IP_GEOLOCATION,
            LocationSource.SAVED_LOCATION,
            LocationSource.MANUAL_ENTRY
        ]
        
        return [source for source in sources if source in battery_friendly_sources]
    
    def _assess_battery_impact(self, source: LocationSource, battery_level: Optional[int]) -> str:
        """Assess battery impact of location detection method."""
        if source == LocationSource.GPS:
            return "high" if battery_level and battery_level < 50 else "medium"
        elif source == LocationSource.IP_GEOLOCATION:
            return "low"
        elif source == LocationSource.SAVED_LOCATION:
            return "minimal"
        else:
            return "low"
    
    async def _store_location_history(
        self,
        location: LocationReading,
        user_id: str,
        session_id: str,
        source: LocationSource
    ):
        """Store location in history."""
        try:
            entry = LocationHistoryEntry(
                id=str(uuid4()),
                location=location,
                user_id=user_id,
                session_id=session_id,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=self.config['location_history_ttl_days'])
            )
            
            self.location_history.append(entry)
            
            # Clean up old entries
            await self._cleanup_location_history()
            
        except Exception as e:
            self.logger.error(f"Error storing location history: {e}")
    
    async def _cleanup_location_history(self):
        """Clean up old location history entries."""
        try:
            current_time = datetime.utcnow()
            
            # Remove expired entries
            self.location_history = [
                entry for entry in self.location_history
                if not entry.expires_at or entry.expires_at > current_time
            ]
            
            # Limit number of entries per user
            user_counts = {}
            filtered_history = []
            
            for entry in self.location_history:
                user_id = entry.user_id
                if user_counts.get(user_id, 0) < self.config['max_location_history_entries']:
                    filtered_history.append(entry)
                    user_counts[user_id] = user_counts.get(user_id, 0) + 1
            
            self.location_history = filtered_history
            
        except Exception as e:
            self.logger.error(f"Error cleaning up location history: {e}")
    
    async def _cache_location(self, location: LocationReading, user_id: str):
        """Cache location for quick access."""
        try:
            cache_key = f"{user_id}:{location.latitude:.6f}:{location.longitude:.6f}"
            self.location_cache[cache_key] = location
            
            # Clean up old cache entries
            if len(self.location_cache) > 100:  # Limit cache size
                # Remove oldest entries
                cache_items = list(self.location_cache.items())
                cache_items.sort(key=lambda x: x[1].timestamp)
                self.location_cache = dict(cache_items[-50:])  # Keep only 50 most recent
            
        except Exception as e:
            self.logger.error(f"Error caching location: {e}")
    
    async def get_location_history(
        self,
        user_id: str,
        limit: int = 10,
        include_favorites_only: bool = False
    ) -> List[LocationHistoryEntry]:
        """Get location history for a user."""
        try:
            user_history = [
                entry for entry in self.location_history
                if entry.user_id == user_id
            ]
            
            if include_favorites_only:
                user_history = [entry for entry in user_history if entry.is_favorite]
            
            # Sort by creation time (most recent first)
            user_history.sort(key=lambda x: x.created_at, reverse=True)
            
            return user_history[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting location history: {e}")
            return []
    
    async def save_location_as_favorite(
        self,
        location: LocationReading,
        user_id: str,
        session_id: str,
        notes: Optional[str] = None
    ) -> bool:
        """Save a location as favorite."""
        try:
            entry = LocationHistoryEntry(
                id=str(uuid4()),
                location=location,
                user_id=user_id,
                session_id=session_id,
                created_at=datetime.utcnow(),
                is_favorite=True,
                notes=notes
            )
            
            self.location_history.append(entry)
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving favorite location: {e}")
            return False
    
    async def get_location_permissions_status(self) -> Dict[str, Any]:
        """Get current location permissions status."""
        # This would typically be handled by the frontend
        # For backend service, we return a placeholder
        return {
            'gps_available': True,
            'gps_permission_granted': False,
            'location_services_enabled': False,
            'privacy_mode_active': True,
            'battery_optimization_active': True
        }
    
    async def request_location_permission(self, user_id: str) -> Dict[str, Any]:
        """Request location permission from user."""
        # This would typically be handled by the frontend
        # For backend service, we return a placeholder
        return {
            'permission_requested': True,
            'requires_frontend_action': True,
            'message': 'Location permission request requires frontend interaction'
        }


# Export the service and models
__all__ = [
    'CurrentLocationDetectionService',
    'LocationReading',
    'LocationDetectionResult',
    'LocationHistoryEntry',
    'LocationSource',
    'LocationAccuracy'
]
