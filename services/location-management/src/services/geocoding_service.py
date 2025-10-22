from geopy.geocoders import Nominatim, GoogleV3
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import logging
from typing import Optional, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeocodingService:
    """Service for geocoding and reverse geocoding using geopy"""
    
    def __init__(self, user_agent: str = "caain-location-service"):
        """Initialize geocoding service with Nominatim provider"""
        self.geocoder = Nominatim(user_agent=user_agent)
        self._fallback_geocoders = [
            Nominatim(user_agent=f"{user_agent}-fallback-1"),
        ]
        self.timeout = 10
        self.max_retries = 3
    
    def geocode_address(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Forward geocode an address to coordinates.
        
        Args:
            address: Address string to geocode
            
        Returns:
            Dictionary with latitude, longitude, and other location details, or None if not found
        """
        if not address or not isinstance(address, str):
            logger.warning(f"Invalid address: {address}")
            return None
        
        try:
            location = self.geocoder.geocode(address, timeout=self.timeout)
            if location:
                return {
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'address': location.address,
                    'raw': location.raw
                }
        except GeocoderTimedOut:
            logger.warning(f"Geocoder timed out for address: {address}")
            return self._fallback_geocode(address)
        except GeocoderServiceError as e:
            logger.error(f"Geocoder service error: {str(e)}")
            return self._fallback_geocode(address)
        except Exception as e:
            logger.error(f"Error geocoding address '{address}': {str(e)}")
            return self._fallback_geocode(address)
        
        return None
    
    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """
        Reverse geocode coordinates to address.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Dictionary with address and other location details, or None if not found
        """
        if not self._validate_coordinates(latitude, longitude):
            logger.warning(f"Invalid coordinates: ({latitude}, {longitude})")
            return None
        
        try:
            location = self.geocoder.reverse(f"{latitude}, {longitude}", timeout=self.timeout)
            if location:
                return {
                    'address': location.address,
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'raw': location.raw
                }
        except GeocoderTimedOut:
            logger.warning(f"Geocoder timed out for coordinates: ({latitude}, {longitude})")
            return self._fallback_reverse_geocode(latitude, longitude)
        except GeocoderServiceError as e:
            logger.error(f"Geocoder service error: {str(e)}")
            return self._fallback_reverse_geocode(latitude, longitude)
        except Exception as e:
            logger.error(f"Error reverse geocoding ({latitude}, {longitude}): {str(e)}")
            return self._fallback_reverse_geocode(latitude, longitude)
        
        return None
    
    def _fallback_geocode(self, address: str) -> Optional[Dict[str, Any]]:
        """Fallback geocoding using alternative providers"""
        for fallback_geocoder in self._fallback_geocoders:
            try:
                location = fallback_geocoder.geocode(address, timeout=self.timeout)
                if location:
                    logger.info(f"Fallback geocoding successful for: {address}")
                    return {
                        'latitude': location.latitude,
                        'longitude': location.longitude,
                        'address': location.address,
                        'raw': location.raw
                    }
            except Exception as e:
                logger.debug(f"Fallback geocoder error: {str(e)}")
                continue
        
        return None
    
    def _fallback_reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """Fallback reverse geocoding using alternative providers"""
        for fallback_geocoder in self._fallback_geocoders:
            try:
                location = fallback_geocoder.reverse(f"{latitude}, {longitude}", timeout=self.timeout)
                if location:
                    logger.info(f"Fallback reverse geocoding successful for: ({latitude}, {longitude})")
                    return {
                        'address': location.address,
                        'latitude': location.latitude,
                        'longitude': location.longitude,
                        'raw': location.raw
                    }
            except Exception as e:
                logger.debug(f"Fallback reverse geocoder error: {str(e)}")
                continue
        
        return None
    
    def _validate_coordinates(self, latitude: float, longitude: float) -> bool:
        """
        Validate latitude and longitude values.
        
        Args:
            latitude: Latitude value to validate
            longitude: Longitude value to validate
            
        Returns:
            True if coordinates are valid, False otherwise
        """
        try:
            lat_float = float(latitude)
            lon_float = float(longitude)
            
            if not (-90 <= lat_float <= 90):
                logger.warning(f"Latitude out of range: {lat_float}")
                return False
            
            if not (-180 <= lon_float <= 180):
                logger.warning(f"Longitude out of range: {lon_float}")
                return False
            
            return True
        except (TypeError, ValueError) as e:
            logger.warning(f"Invalid coordinate types: {str(e)}")
            return False
    
    def batch_geocode(self, addresses: list) -> list:
        """
        Geocode multiple addresses.
        
        Args:
            addresses: List of address strings
            
        Returns:
            List of geocoding results
        """
        results = []
        for address in addresses:
            result = self.geocode_address(address)
            results.append(result)
        return results
    
    def batch_reverse_geocode(self, coordinates: list) -> list:
        """
        Reverse geocode multiple coordinates.
        
        Args:
            coordinates: List of (latitude, longitude) tuples
            
        Returns:
            List of reverse geocoding results
        """
        results = []
        for lat, lon in coordinates:
            result = self.reverse_geocode(lat, lon)
            results.append(result)
        return results
