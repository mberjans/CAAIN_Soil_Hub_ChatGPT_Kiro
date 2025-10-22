from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class LocationValidationService:
    """Service for validating location data"""
    
    VALID_AGRICULTURAL_ZONES = {
        '1a', '1b', '2a', '2b', '3a', '3b', '4a', '4b', '5a', '5b',
        '6a', '6b', '7a', '7b', '8a', '8b', '9a', '9b', '10a', '10b',
        '11a', '11b', '12a', '12b'
    }
    
    def __init__(self):
        """Initialize validation service"""
        self.logger = logger
    
    def validate_agricultural_zone(self, zone: Optional[str]) -> bool:
        """
        Validate agricultural zone code.
        
        Valid zones: 1a-12b (USDA Hardiness Zones)
        
        Args:
            zone: Zone code (e.g., '5a', '7b')
            
        Returns:
            True if valid, False otherwise
        """
        if zone is None:
            self.logger.warning("Zone is None")
            return False
        
        if not isinstance(zone, str):
            self.logger.warning(f"Zone is not a string: {type(zone)}")
            return False
        
        zone_normalized = zone.strip().lower()
        
        if not zone_normalized:
            self.logger.warning("Zone is empty")
            return False
        
        is_valid = zone_normalized in self.VALID_AGRICULTURAL_ZONES
        
        if not is_valid:
            self.logger.warning(f"Invalid agricultural zone: {zone}")
        
        return is_valid
    
    def validate_location_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validate complete location data.
        
        Args:
            data: Location data dictionary
            
        Returns:
            Validated data or None if invalid
        """
        if not isinstance(data, dict):
            self.logger.warning("Location data is not a dictionary")
            return None
        
        try:
            required_fields = ['name', 'latitude', 'longitude']
            
            for field in required_fields:
                if field not in data:
                    self.logger.warning(f"Missing required field: {field}")
                    return None
            
            name = data.get('name')
            if not name or not isinstance(name, str):
                self.logger.warning("Invalid name")
                return None
            
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            
            try:
                lat_float = float(latitude)
                lon_float = float(longitude)
                
                if not (-90 <= lat_float <= 90):
                    self.logger.warning(f"Latitude out of range: {lat_float}")
                    return None
                
                if not (-180 <= lon_float <= 180):
                    self.logger.warning(f"Longitude out of range: {lon_float}")
                    return None
            except (TypeError, ValueError) as e:
                self.logger.warning(f"Invalid coordinates: {str(e)}")
                return None
            
            agricultural_zone = data.get('agricultural_zone')
            if agricultural_zone:
                if not self.validate_agricultural_zone(agricultural_zone):
                    self.logger.warning(f"Invalid agricultural zone: {agricultural_zone}")
                    return None
            
            validated_data = {
                'name': name,
                'latitude': lat_float,
                'longitude': lon_float
            }
            
            if agricultural_zone:
                validated_data['agricultural_zone'] = agricultural_zone
            
            self.logger.info(f"Location data validated: {name}")
            return validated_data
        
        except Exception as e:
            self.logger.error(f"Error validating location data: {str(e)}")
            return None
    
    def get_zone_info(self, zone: str) -> Optional[Dict[str, str]]:
        """
        Get information about a zone.
        
        Args:
            zone: Zone code
            
        Returns:
            Zone information or None
        """
        if not self.validate_agricultural_zone(zone):
            return None
        
        zone_num = zone[:-1]
        zone_letter = zone[-1]
        
        return {
            'zone': zone.lower(),
            'number': zone_num,
            'letter': zone_letter,
            'valid': True
        }
