"""
Location Validation Service
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

Core location validation service with coordinate range validation,
agricultural area detection, and climate zone detection.
"""

import logging
import asyncio
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum
import math
import json
import aiohttp
from datetime import datetime, timedelta

# Import the Pydantic models
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../databases/python'))

from location_models import (
    ValidationResult, GeographicInfo, LocationError, LOCATION_ERRORS
)

logger = logging.getLogger(__name__)


class ValidationSeverity(str, Enum):
    """Severity levels for validation issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """Represents a validation issue."""
    severity: ValidationSeverity
    message: str
    field: Optional[str] = None
    agricultural_context: Optional[str] = None
    suggested_actions: List[str] = None


class LocationValidationService:
    """
    Core location validation service for farm location input.
    
    Provides coordinate range validation, agricultural area detection,
    climate zone detection, and comprehensive location validation.
    """
    
    def __init__(self):
        """Initialize the location validation service."""
        self.logger = logging.getLogger(__name__)
        
        # Agricultural area boundaries (simplified for initial implementation)
        # In production, this would use actual USDA/NASS agricultural land data
        self.agricultural_regions = self._load_agricultural_regions()
        
        # Climate zone data (USDA Hardiness Zones)
        self.climate_zones = self._load_climate_zones()
        
        # County/state boundary data
        self.geographic_boundaries = self._load_geographic_boundaries()
        
        # Validation thresholds
        self.validation_config = {
            'coordinate_precision': 6,  # Decimal places for coordinates
            'max_accuracy_meters': 10000,  # Maximum GPS accuracy to accept
            'agricultural_confidence_threshold': 0.7,
            'ocean_detection_enabled': True,
            'urban_area_warnings': True
        }
    
    async def validate_coordinates(self, latitude: float, longitude: float) -> ValidationResult:
        """
        Validate GPS coordinates for basic range and agricultural suitability.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            
        Returns:
            ValidationResult with validation status and geographic information
        """
        issues = []
        
        # Basic coordinate range validation
        if not self._is_valid_coordinate_range(latitude, longitude):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message="Coordinates are outside valid ranges",
                field="coordinates",
                agricultural_context="Invalid coordinates cannot be used for agricultural recommendations",
                suggested_actions=[
                    "Verify latitude is between -90 and 90 degrees",
                    "Verify longitude is between -180 and 180 degrees",
                    "Use the map interface to visually select location"
                ]
            ))
            return ValidationResult(
                valid=False,
                errors=[issue.message for issue in issues if issue.severity == ValidationSeverity.ERROR],
                warnings=[issue.message for issue in issues if issue.severity == ValidationSeverity.WARNING]
            )
        
        # Check for obviously invalid locations (oceans, poles, etc.)
        ocean_check = await self._check_ocean_location(latitude, longitude)
        if ocean_check:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message="Location appears to be in an ocean or large water body",
                agricultural_context="Agricultural recommendations cannot be provided for water locations",
                suggested_actions=[
                    "Verify the coordinates are correct",
                    "Use the map interface to visually confirm location",
                    "Check for coordinate system confusion (e.g., degrees vs. decimal degrees)"
                ]
            ))
        
        # Get geographic information
        geographic_info = await self._get_geographic_info(latitude, longitude)
        
        # Check agricultural area suitability
        agricultural_check = await self._check_agricultural_area(latitude, longitude)
        if not agricultural_check['is_agricultural']:
            if agricultural_check['confidence'] > 0.8:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message="Location may not be in a typical agricultural area",
                    agricultural_context="Recommendations may be less accurate for non-agricultural areas",
                    suggested_actions=[
                        "Verify the location is correct",
                        "Proceed with caution as recommendations may be less accurate",
                        "Consult local agricultural experts for validation"
                    ]
                ))
            else:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    message="Agricultural area status uncertain for this location",
                    agricultural_context="Limited data available for agricultural area classification",
                    suggested_actions=[
                        "Provide additional context about your farming operation",
                        "Consult local extension services for area-specific guidance"
                    ]
                ))
        
        # Check for extreme climate conditions
        climate_warnings = await self._check_climate_extremes(latitude, longitude)
        issues.extend(climate_warnings)
        
        # Compile results
        has_errors = any(issue.severity == ValidationSeverity.ERROR for issue in issues)
        
        return ValidationResult(
            valid=not has_errors,
            warnings=[issue.message for issue in issues if issue.severity in [ValidationSeverity.WARNING, ValidationSeverity.INFO]],
            errors=[issue.message for issue in issues if issue.severity == ValidationSeverity.ERROR],
            geographic_info=geographic_info
        )
    
    async def validate_agricultural_location(self, latitude: float, longitude: float) -> ValidationResult:
        """
        Comprehensive agricultural location validation.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            
        Returns:
            ValidationResult with detailed agricultural context
        """
        # Start with basic coordinate validation
        basic_validation = await self.validate_coordinates(latitude, longitude)
        
        if not basic_validation.valid:
            return basic_validation
        
        # Enhanced agricultural validation
        issues = []
        
        # Get detailed geographic information
        geographic_info = await self._get_detailed_geographic_info(latitude, longitude)
        
        # Agricultural area analysis
        agricultural_analysis = await self._analyze_agricultural_suitability(latitude, longitude)
        
        if agricultural_analysis['suitability_score'] < 0.3:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message=f"Low agricultural suitability score: {agricultural_analysis['suitability_score']:.2f}",
                agricultural_context="This location may not be suitable for typical agricultural operations",
                suggested_actions=[
                    "Consider specialized agricultural practices for this area",
                    "Consult local agricultural extension services",
                    "Verify location accuracy"
                ]
            ))
        
        # Climate zone validation
        climate_validation = await self._validate_climate_zone(latitude, longitude)
        if climate_validation['warnings']:
            for warning in climate_validation['warnings']:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message=warning,
                    agricultural_context="Climate conditions may limit crop options and growing practices"
                ))
        
        # Soil region analysis
        soil_region = await self._get_soil_region_info(latitude, longitude)
        if soil_region and soil_region.get('limitations'):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                message=f"Soil limitations identified: {', '.join(soil_region['limitations'])}",
                agricultural_context="Soil characteristics may require specific management practices"
            ))
        
        # Update geographic info with agricultural analysis
        if geographic_info:
            geographic_info.is_agricultural = agricultural_analysis['is_agricultural']
        
        return ValidationResult(
            valid=True,
            warnings=[issue.message for issue in issues if issue.severity in [ValidationSeverity.WARNING, ValidationSeverity.INFO]],
            errors=[issue.message for issue in issues if issue.severity == ValidationSeverity.ERROR],
            geographic_info=geographic_info
        )
    
    def _is_valid_coordinate_range(self, latitude: float, longitude: float) -> bool:
        """Check if coordinates are within valid ranges."""
        return -90 <= latitude <= 90 and -180 <= longitude <= 180
    
    async def _check_ocean_location(self, latitude: float, longitude: float) -> bool:
        """
        Check if coordinates are in an ocean or large water body.
        
        This is a simplified implementation. In production, this would use
        actual geographic data services or datasets.
        """
        # Simple heuristic checks for obvious ocean locations
        
        # Check for coordinates in major oceans
        ocean_regions = [
            # Atlantic Ocean (simplified)
            {'lat_range': (-60, 70), 'lon_range': (-80, 20)},
            # Pacific Ocean (simplified)
            {'lat_range': (-60, 70), 'lon_range': (-180, -80)},
            {'lat_range': (-60, 70), 'lon_range': (120, 180)},
            # Indian Ocean (simplified)
            {'lat_range': (-60, 30), 'lon_range': (20, 120)},
        ]
        
        for region in ocean_regions:
            if (region['lat_range'][0] <= latitude <= region['lat_range'][1] and
                region['lon_range'][0] <= longitude <= region['lon_range'][1]):
                
                # Additional check: if it's near coastlines, it might be valid
                # This is a very simplified check
                if not await self._is_near_coastline(latitude, longitude):
                    return True
        
        return False
    
    async def _is_near_coastline(self, latitude: float, longitude: float) -> bool:
        """
        Check if coordinates are near a coastline.
        
        Simplified implementation - in production would use actual coastline data.
        """
        # For now, assume locations within certain distance of known land masses are valid
        # This is a placeholder implementation
        return True
    
    async def _get_geographic_info(self, latitude: float, longitude: float) -> Optional[GeographicInfo]:
        """Get basic geographic information for coordinates."""
        try:
            # Get county and state information
            county, state = await self._get_county_state(latitude, longitude)
            
            # Get climate zone
            climate_zone = await self._get_climate_zone(latitude, longitude)
            
            # Determine if agricultural area
            agricultural_check = await self._check_agricultural_area(latitude, longitude)
            
            return GeographicInfo(
                county=county,
                state=state,
                climate_zone=climate_zone,
                is_agricultural=agricultural_check['is_agricultural']
            )
        
        except Exception as e:
            self.logger.error(f"Error getting geographic info: {e}")
            return None
    
    async def _get_detailed_geographic_info(self, latitude: float, longitude: float) -> Optional[GeographicInfo]:
        """Get detailed geographic information including agricultural context."""
        basic_info = await self._get_geographic_info(latitude, longitude)
        
        if not basic_info:
            return None
        
        # Add more detailed agricultural analysis
        agricultural_analysis = await self._analyze_agricultural_suitability(latitude, longitude)
        basic_info.is_agricultural = agricultural_analysis['is_agricultural']
        
        return basic_info
    
    async def _get_county_state(self, latitude: float, longitude: float) -> Tuple[Optional[str], Optional[str]]:
        """
        Get county and state for given coordinates.
        
        This is a simplified implementation. In production, this would use
        actual geographic boundary data or reverse geocoding services.
        """
        # Simplified mapping based on coordinate ranges
        # This would be replaced with actual boundary data in production
        
        state_mappings = {
            # Iowa (approximate)
            (40.375, 43.501, -96.639, -90.140): "Iowa",
            # Illinois (approximate)
            (36.970, 42.508, -91.513, -87.494): "Illinois",
            # Nebraska (approximate)
            (39.999, 43.001, -104.053, -95.308): "Nebraska",
            # Add more states as needed
        }
        
        state = None
        for (min_lat, max_lat, min_lon, max_lon), state_name in state_mappings.items():
            if min_lat <= latitude <= max_lat and min_lon <= longitude <= max_lon:
                state = state_name
                break
        
        # County determination would require more detailed boundary data
        # For now, return None for county
        county = None
        
        return county, state
    
    async def _get_climate_zone(self, latitude: float, longitude: float) -> Optional[str]:
        """
        Get USDA hardiness zone for coordinates.
        
        Simplified implementation based on latitude. In production, this would
        use actual USDA hardiness zone data.
        """
        # Simplified zone mapping based on latitude
        # This is a rough approximation and should be replaced with actual data
        
        if latitude >= 48:
            return "3a-4b"
        elif latitude >= 45:
            return "4a-5b"
        elif latitude >= 42:
            return "5a-6a"
        elif latitude >= 39:
            return "6a-7a"
        elif latitude >= 36:
            return "7a-8a"
        elif latitude >= 33:
            return "8a-9a"
        elif latitude >= 30:
            return "9a-10a"
        else:
            return "10a+"
    
    async def _check_agricultural_area(self, latitude: float, longitude: float) -> Dict:
        """
        Check if coordinates are in an agricultural area.
        
        Returns dict with 'is_agricultural' boolean and 'confidence' score.
        """
        # Simplified agricultural area detection
        # In production, this would use USDA NASS Cropland Data Layer or similar
        
        # Basic heuristic: most of the continental US between certain latitudes
        # is potentially agricultural, with higher confidence in known agricultural regions
        
        confidence = 0.5  # Default confidence
        is_agricultural = False
        
        # Check if in continental US agricultural regions
        if 25 <= latitude <= 49 and -125 <= longitude <= -66:
            is_agricultural = True
            
            # Higher confidence for known agricultural states
            agricultural_states = [
                # Corn Belt states (high confidence)
                (40.375, 43.501, -96.639, -90.140),  # Iowa
                (36.970, 42.508, -91.513, -87.494),  # Illinois  
                (37.913, 41.761, -95.774, -89.098),  # Missouri
                (38.403, 41.977, -88.097, -84.784),  # Indiana
                (41.222, 48.306, -90.639, -82.413),  # Michigan
                (38.758, 42.327, -84.820, -80.519),  # Ohio
            ]
            
            for min_lat, max_lat, min_lon, max_lon in agricultural_states:
                if min_lat <= latitude <= max_lat and min_lon <= longitude <= max_lon:
                    confidence = 0.9
                    break
            else:
                confidence = 0.7  # Moderate confidence for other continental US areas
        
        # Check for non-agricultural areas
        non_agricultural_areas = [
            # Major urban areas (simplified)
            (41.8, 42.0, -87.8, -87.5),  # Chicago area
            (40.6, 40.9, -74.1, -73.9),  # NYC area
            # Mountain regions
            (39.0, 41.0, -109.0, -102.0),  # Rocky Mountains (partial)
        ]
        
        for min_lat, max_lat, min_lon, max_lon in non_agricultural_areas:
            if min_lat <= latitude <= max_lat and min_lon <= longitude <= max_lon:
                is_agricultural = False
                confidence = 0.8
                break
        
        return {
            'is_agricultural': is_agricultural,
            'confidence': confidence,
            'reasoning': self._get_agricultural_reasoning(latitude, longitude, is_agricultural, confidence)
        }
    
    def _get_agricultural_reasoning(self, latitude: float, longitude: float, 
                                  is_agricultural: bool, confidence: float) -> str:
        """Generate reasoning for agricultural area classification."""
        if is_agricultural:
            if confidence > 0.8:
                return "Location is in a known agricultural region with high crop production"
            else:
                return "Location appears to be in an area suitable for agriculture"
        else:
            return "Location may not be suitable for typical agricultural operations"
    
    async def _check_climate_extremes(self, latitude: float, longitude: float) -> List[ValidationIssue]:
        """Check for extreme climate conditions that may affect agriculture."""
        issues = []
        
        # Check for extreme latitudes
        if latitude > 55:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                message="Location is at high latitude with short growing season",
                agricultural_context="Short growing seasons limit crop options and may require specialized varieties",
                suggested_actions=[
                    "Consider cold-hardy crop varieties",
                    "Plan for shorter growing seasons",
                    "Investigate season extension techniques"
                ]
            ))
        elif latitude < 25:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                message="Location is at low latitude with tropical/subtropical climate",
                agricultural_context="Tropical conditions may require different agricultural practices",
                suggested_actions=[
                    "Consider heat-tolerant varieties",
                    "Plan for year-round growing potential",
                    "Account for different pest and disease pressures"
                ]
            ))
        
        return issues
    
    async def _analyze_agricultural_suitability(self, latitude: float, longitude: float) -> Dict:
        """Analyze overall agricultural suitability for location."""
        basic_check = await self._check_agricultural_area(latitude, longitude)
        
        # Calculate suitability score based on multiple factors
        suitability_factors = {
            'agricultural_area': basic_check['confidence'] if basic_check['is_agricultural'] else 0.2,
            'climate_suitability': await self._calculate_climate_suitability(latitude, longitude),
            'geographic_factors': await self._calculate_geographic_suitability(latitude, longitude)
        }
        
        # Weighted average
        weights = {'agricultural_area': 0.5, 'climate_suitability': 0.3, 'geographic_factors': 0.2}
        suitability_score = sum(suitability_factors[factor] * weights[factor] 
                               for factor in suitability_factors)
        
        return {
            'is_agricultural': basic_check['is_agricultural'],
            'suitability_score': suitability_score,
            'factors': suitability_factors,
            'reasoning': f"Agricultural suitability score: {suitability_score:.2f} based on area classification, climate, and geographic factors"
        }
    
    async def _calculate_climate_suitability(self, latitude: float, longitude: float) -> float:
        """Calculate climate suitability score (0-1)."""
        # Simplified climate suitability based on latitude
        # Optimal agricultural latitudes are roughly 30-50 degrees
        
        if 30 <= abs(latitude) <= 50:
            return 1.0
        elif 25 <= abs(latitude) <= 55:
            return 0.8
        elif 20 <= abs(latitude) <= 60:
            return 0.6
        else:
            return 0.3
    
    async def _calculate_geographic_suitability(self, latitude: float, longitude: float) -> float:
        """Calculate geographic suitability score (0-1)."""
        # Simplified geographic suitability
        # Continental areas generally more suitable than islands or extreme locations
        
        # Check if in continental regions
        if -125 <= longitude <= -66 and 25 <= latitude <= 49:  # Continental US
            return 0.9
        elif -141 <= longitude <= -52 and 41 <= latitude <= 83:  # Canada
            return 0.8
        else:
            return 0.6  # Other regions
    
    async def _validate_climate_zone(self, latitude: float, longitude: float) -> Dict:
        """Validate climate zone and return warnings if needed."""
        climate_zone = await self._get_climate_zone(latitude, longitude)
        warnings = []
        
        if climate_zone:
            if climate_zone.startswith("3") or climate_zone.startswith("4"):
                warnings.append("Very cold climate zone - limited growing season and crop options")
            elif climate_zone.startswith("10"):
                warnings.append("Very warm climate zone - may require specialized tropical agriculture practices")
        
        return {
            'climate_zone': climate_zone,
            'warnings': warnings
        }
    
    async def _get_soil_region_info(self, latitude: float, longitude: float) -> Optional[Dict]:
        """
        Get soil region information for location.
        
        Simplified implementation - would use actual soil survey data in production.
        """
        # Placeholder implementation
        # In production, this would query USDA soil survey data
        
        return {
            'soil_region': 'Unknown',
            'limitations': [],
            'characteristics': []
        }
    
    def _load_agricultural_regions(self) -> Dict:
        """Load agricultural region data."""
        # Placeholder for loading actual agricultural region data
        # In production, this would load from USDA NASS or similar datasets
        return {}
    
    def _load_climate_zones(self) -> Dict:
        """Load climate zone data."""
        # Placeholder for loading actual climate zone data
        # In production, this would load USDA hardiness zone data
        return {}
    
    def _load_geographic_boundaries(self) -> Dict:
        """Load geographic boundary data."""
        # Placeholder for loading actual boundary data
        # In production, this would load county/state boundary data
        return {}
    
    async def get_validation_error(self, error_code: str) -> LocationError:
        """Get a predefined validation error by code."""
        return LOCATION_ERRORS.get(error_code, LOCATION_ERRORS["LOCATION_NOT_FOUND"])


# Export the service
__all__ = ['LocationValidationService', 'ValidationSeverity', 'ValidationIssue']