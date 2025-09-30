"""
Coordinate Format Utilities
CAAIN Soil Hub - Location Validation Service

Handles conversion between different coordinate formats and validation.
"""

import math
import re
from typing import Dict, Tuple, Optional, Union
from dataclasses import dataclass


@dataclass
class CoordinateFormat:
    """Represents a coordinate in a specific format."""
    format_type: str  # 'decimal', 'dms', 'utm', 'mgrs'
    value: Union[Dict, str, Tuple]
    precision: Optional[int] = None


class CoordinateConverter:
    """Handles conversion between different coordinate formats."""
    
    @staticmethod
    def decimal_to_dms(decimal: float, is_latitude: bool = True) -> Dict[str, Union[int, float]]:
        """
        Convert decimal degrees to degrees, minutes, seconds format.
        
        Args:
            decimal: Decimal degrees
            is_latitude: True for latitude, False for longitude
            
        Returns:
            Dictionary with degrees, minutes, seconds, and direction
        """
        abs_decimal = abs(decimal)
        degrees = int(abs_decimal)
        minutes_float = (abs_decimal - degrees) * 60
        minutes = int(minutes_float)
        seconds = (minutes_float - minutes) * 60
        
        # Determine direction
        if is_latitude:
            direction = 'N' if decimal >= 0 else 'S'
        else:
            direction = 'E' if decimal >= 0 else 'W'
        
        return {
            'degrees': degrees,
            'minutes': minutes,
            'seconds': seconds,
            'direction': direction
        }
    
    @staticmethod
    def dms_to_decimal(degrees: int, minutes: int, seconds: float, direction: str) -> float:
        """
        Convert degrees, minutes, seconds to decimal degrees.
        
        Args:
            degrees: Degrees
            minutes: Minutes
            seconds: Seconds
            direction: Direction (N, S, E, W)
            
        Returns:
            Decimal degrees
        """
        decimal = degrees + minutes / 60.0 + seconds / 3600.0
        
        if direction in ['S', 'W']:
            decimal = -decimal
            
        return decimal
    
    @staticmethod
    def decimal_to_utm(latitude: float, longitude: float) -> Dict[str, Union[int, float]]:
        """
        Convert decimal degrees to UTM coordinates.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            
        Returns:
            Dictionary with zone, easting, northing, and hemisphere
        """
        # Simplified UTM conversion (in production, use proper UTM library like pyproj)
        zone = int((longitude + 180) / 6) + 1
        
        # Convert to radians
        lat_rad = math.radians(latitude)
        lon_rad = math.radians(longitude)
        
        # UTM zone central meridian
        lon0 = math.radians((zone - 1) * 6 - 180 + 3)
        
        # Simplified UTM conversion (not accurate for production use)
        easting = (longitude + 180) * 100000
        northing = latitude * 100000
        
        hemisphere = 'N' if latitude >= 0 else 'S'
        
        return {
            'zone': zone,
            'easting': easting,
            'northing': northing,
            'hemisphere': hemisphere
        }
    
    @staticmethod
    def utm_to_decimal(zone: int, easting: float, northing: float, hemisphere: str = 'N') -> Tuple[float, float]:
        """
        Convert UTM coordinates to decimal degrees.
        
        Args:
            zone: UTM zone
            easting: UTM easting
            northing: UTM northing
            hemisphere: Hemisphere (N or S)
            
        Returns:
            Tuple of (latitude, longitude) in decimal degrees
        """
        # Simplified UTM to decimal conversion (not accurate for production use)
        # This is a rough approximation for testing purposes
        longitude = ((zone - 1) * 6) - 180 + 3 + (easting - 500000) / 100000
        latitude = northing / 100000
        
        if hemisphere == 'S':
            latitude = -latitude
            
        return latitude, longitude
    
    @staticmethod
    def decimal_to_mgrs(latitude: float, longitude: float) -> str:
        """
        Convert decimal degrees to MGRS format.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            
        Returns:
            MGRS coordinate string
        """
        # Simplified MGRS conversion (in production, use proper MGRS library)
        zone = int((longitude + 180) / 6) + 1
        
        # Determine latitude band
        band_index = int((latitude + 80) / 8)
        band = chr(65 + band_index)  # A-Z
        
        # Simplified grid square calculation
        easting = int((longitude + 180) * 1000)
        northing = int((latitude + 80) * 1000)
        
        return f"{zone:02d}{band} {easting:05d} {northing:07d}"
    
    @staticmethod
    def mgrs_to_decimal(mgrs: str) -> Tuple[float, float]:
        """
        Convert MGRS coordinate to decimal degrees.
        
        Args:
            mgrs: MGRS coordinate string
            
        Returns:
            Tuple of (latitude, longitude) in decimal degrees
        """
        # Parse MGRS format: "18T VK 83000 5070000"
        parts = mgrs.strip().split()
        if len(parts) != 4:  # Changed from 3 to 4 to handle grid square
            raise ValueError("Invalid MGRS format")
        
        zone_band = parts[0]
        grid_square = parts[1]
        easting = float(parts[2])
        northing = float(parts[3])
        
        # Extract zone and band
        zone = int(zone_band[:2])
        band = zone_band[2]
        
        # Simplified conversion (not accurate for production use)
        # Convert to UTM-like coordinates first, then to decimal
        longitude = ((zone - 1) * 6) - 180 + 3 + (easting - 500000) / 100000
        latitude = (northing - 10000000) / 100000  # Adjust for UTM false northing
        
        return latitude, longitude


class CoordinateValidator:
    """Validates coordinates in different formats."""
    
    @staticmethod
    def validate_decimal_coordinates(latitude: float, longitude: float) -> Dict[str, Union[bool, str]]:
        """
        Validate decimal degree coordinates.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        # Range validation
        if not (-90 <= latitude <= 90):
            errors.append(f"Latitude {latitude} is outside valid range (-90 to 90)")
        
        if not (-180 <= longitude <= 180):
            errors.append(f"Longitude {longitude} is outside valid range (-180 to 180)")
        
        # Precision validation
        if abs(latitude) < 0.000001 and abs(longitude) < 0.000001:
            warnings.append("Coordinates appear to be at null island (0,0)")
        
        # Ocean detection (simplified)
        if CoordinateValidator._is_likely_ocean(latitude, longitude):
            warnings.append("Location appears to be over water")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def validate_dms_coordinates(degrees: int, minutes: int, seconds: float, direction: str, is_latitude: bool = True) -> Dict[str, Union[bool, str]]:
        """
        Validate DMS coordinates.
        
        Args:
            degrees: Degrees
            minutes: Minutes
            seconds: Seconds
            direction: Direction (N, S, E, W)
            is_latitude: True for latitude, False for longitude
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        # Range validation
        if is_latitude:
            if degrees < 0 or degrees > 90:
                errors.append(f"Latitude degrees {degrees} is outside valid range (0 to 90)")
            if direction not in ['N', 'S']:
                errors.append(f"Invalid latitude direction: {direction}")
        else:
            if degrees < 0 or degrees > 180:
                errors.append(f"Longitude degrees {degrees} is outside valid range (0 to 180)")
            if direction not in ['E', 'W']:
                errors.append(f"Invalid longitude direction: {direction}")
        
        if minutes < 0 or minutes >= 60:
            errors.append(f"Minutes {minutes} is outside valid range (0 to 59)")
        
        if seconds < 0 or seconds >= 60:
            errors.append(f"Seconds {seconds} is outside valid range (0 to 59.999)")
        
        # Convert to decimal for further validation
        try:
            decimal = CoordinateConverter.dms_to_decimal(degrees, minutes, seconds, direction)
            decimal_validation = CoordinateValidator.validate_decimal_coordinates(
                decimal if is_latitude else 0,
                0 if is_latitude else decimal
            )
            errors.extend(decimal_validation['errors'])
            warnings.extend(decimal_validation['warnings'])
        except Exception as e:
            errors.append(f"DMS conversion error: {str(e)}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def validate_utm_coordinates(zone: int, easting: float, northing: float, hemisphere: str = 'N') -> Dict[str, Union[bool, str]]:
        """
        Validate UTM coordinates.
        
        Args:
            zone: UTM zone
            easting: UTM easting
            northing: UTM northing
            hemisphere: Hemisphere (N or S)
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        # Zone validation
        if not (1 <= zone <= 60):
            errors.append(f"UTM zone {zone} is outside valid range (1 to 60)")
        
        # Hemisphere validation
        if hemisphere not in ['N', 'S']:
            errors.append(f"Invalid hemisphere: {hemisphere}")
        
        # Convert to decimal for further validation
        try:
            latitude, longitude = CoordinateConverter.utm_to_decimal(zone, easting, northing, hemisphere)
            decimal_validation = CoordinateValidator.validate_decimal_coordinates(latitude, longitude)
            errors.extend(decimal_validation['errors'])
            warnings.extend(decimal_validation['warnings'])
        except Exception as e:
            errors.append(f"UTM conversion error: {str(e)}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def validate_mgrs_coordinate(mgrs: str) -> Dict[str, Union[bool, str]]:
        """
        Validate MGRS coordinate.
        
        Args:
            mgrs: MGRS coordinate string
            
        Returns:
            Dictionary with validation results
        """
        errors = []
        warnings = []
        
        # Format validation - updated pattern to handle grid square
        mgrs_pattern = r'^\d{2}[A-Z]\s+[A-Z]{2}\s+\d{5}\s+\d{7}$'
        if not re.match(mgrs_pattern, mgrs.strip()):
            errors.append(f"Invalid MGRS format: {mgrs}")
            return {
                'valid': False,
                'errors': errors,
                'warnings': warnings
            }
        
        # Convert to decimal for further validation
        try:
            latitude, longitude = CoordinateConverter.mgrs_to_decimal(mgrs)
            decimal_validation = CoordinateValidator.validate_decimal_coordinates(latitude, longitude)
            errors.extend(decimal_validation['errors'])
            warnings.extend(decimal_validation['warnings'])
        except Exception as e:
            errors.append(f"MGRS conversion error: {str(e)}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def _is_likely_ocean(latitude: float, longitude: float) -> bool:
        """
        Simple ocean detection (in production, use proper coastline data).
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            
        Returns:
            True if location is likely over water
        """
        # Simplified ocean detection based on major land masses
        major_land_masses = [
            # North America
            (25, 70, -170, -50),
            # Europe/Asia
            (35, 80, -10, 180),
            # Africa
            (-35, 40, -20, 55),
            # South America
            (-60, 15, -85, -30),
            # Australia
            (-45, -10, 110, 160)
        ]
        
        for min_lat, max_lat, min_lng, max_lng in major_land_masses:
            if min_lat <= latitude <= max_lat and min_lng <= longitude <= max_lng:
                return False
        
        return True


class CoordinateParser:
    """Parses coordinate strings in various formats."""
    
    @staticmethod
    def parse_coordinate_string(coord_string: str) -> Optional[Dict[str, Union[str, float, int]]]:
        """
        Parse a coordinate string and determine its format.
        
        Args:
            coord_string: Coordinate string to parse
            
        Returns:
            Dictionary with parsed coordinate data or None if invalid
        """
        coord_string = coord_string.strip()
        
        # Try different formats
        formats = [
            CoordinateParser._parse_decimal,
            CoordinateParser._parse_dms,
            CoordinateParser._parse_utm,
            CoordinateParser._parse_mgrs
        ]
        
        for parse_func in formats:
            result = parse_func(coord_string)
            if result:
                return result
        
        return None
    
    @staticmethod
    def _parse_decimal(coord_string: str) -> Optional[Dict[str, Union[str, float]]]:
        """Parse decimal degree format."""
        # Pattern: "40.7128, -74.0060" or "40.7128 -74.0060"
        decimal_pattern = r'^(-?\d+\.?\d*)\s*[,;]\s*(-?\d+\.?\d*)$'
        match = re.match(decimal_pattern, coord_string)
        
        if match:
            try:
                lat = float(match.group(1))
                lng = float(match.group(2))
                return {
                    'format': 'decimal',
                    'latitude': lat,
                    'longitude': lng
                }
            except ValueError:
                return None
        
        # Try space-separated format
        space_pattern = r'^(-?\d+\.?\d*)\s+(-?\d+\.?\d*)$'
        match = re.match(space_pattern, coord_string)
        
        if match:
            try:
                lat = float(match.group(1))
                lng = float(match.group(2))
                return {
                    'format': 'decimal',
                    'latitude': lat,
                    'longitude': lng
                }
            except ValueError:
                return None
        
        return None
    
    @staticmethod
    def _parse_dms(coord_string: str) -> Optional[Dict[str, Union[str, int, float]]]:
        """Parse DMS format."""
        # Pattern: "40°42'46.08\"N, 74°0'21.6\"W"
        dms_pattern = r'(\d+)°\s*(\d+)\'\s*(\d+\.?\d*)"\s*([NS])\s*[,;]\s*(\d+)°\s*(\d+)\'\s*(\d+\.?\d*)"\s*([EW])'
        match = re.match(dms_pattern, coord_string)
        
        if match:
            try:
                lat_deg = int(match.group(1))
                lat_min = int(match.group(2))
                lat_sec = float(match.group(3))
                lat_dir = match.group(4)
                
                lon_deg = int(match.group(5))
                lon_min = int(match.group(6))
                lon_sec = float(match.group(7))
                lon_dir = match.group(8)
                
                return {
                    'format': 'dms',
                    'latitude': {
                        'degrees': lat_deg,
                        'minutes': lat_min,
                        'seconds': lat_sec,
                        'direction': lat_dir
                    },
                    'longitude': {
                        'degrees': lon_deg,
                        'minutes': lon_min,
                        'seconds': lon_sec,
                        'direction': lon_dir
                    }
                }
            except (ValueError, IndexError):
                return None
        
        return None
    
    @staticmethod
    def _parse_utm(coord_string: str) -> Optional[Dict[str, Union[str, int, float]]]:
        """Parse UTM format."""
        # Pattern: "18T 583000 4507000"
        utm_pattern = r'(\d{1,2})([A-Z])\s+(\d+\.?\d*)\s+(\d+\.?\d*)$'
        match = re.match(utm_pattern, coord_string)
        
        if match:
            try:
                zone = int(match.group(1))
                band = match.group(2)
                easting = float(match.group(3))
                northing = float(match.group(4))
                
                return {
                    'format': 'utm',
                    'zone': zone,
                    'band': band,
                    'easting': easting,
                    'northing': northing
                }
            except (ValueError, IndexError):
                return None
        
        return None
    
    @staticmethod
    def _parse_mgrs(coord_string: str) -> Optional[Dict[str, str]]:
        """Parse MGRS format."""
        # Pattern: "18T VK 83000 5070000"
        mgrs_pattern = r'^(\d{2}[A-Z])\s+([A-Z]{2})\s+(\d{5})\s+(\d{7})$'
        match = re.match(mgrs_pattern, coord_string.strip())
        
        if match:
            return {
                'format': 'mgrs',
                'zone_band': match.group(1),
                'grid_square': match.group(2),
                'easting': match.group(3),
                'northing': match.group(4),
                'full_coordinate': coord_string.strip()
            }
        
        return None