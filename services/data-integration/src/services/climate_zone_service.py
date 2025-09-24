"""
Climate Zone Service for AFAS
Provides climate zone detection and validation functionality.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import asyncio
import aiohttp
from datetime import datetime, timedelta
import json
import math

logger = logging.getLogger(__name__)


class ClimateZoneType(Enum):
    """Types of climate zone classifications."""
    USDA_HARDINESS = "usda_hardiness"
    KOPPEN = "koppen"
    AGRICULTURAL = "agricultural"


@dataclass
class ClimateZone:
    """Climate zone data structure."""
    zone_id: str
    zone_type: ClimateZoneType
    name: str
    description: str
    min_temp_f: Optional[float] = None
    max_temp_f: Optional[float] = None
    growing_season_days: Optional[int] = None
    frost_free_days: Optional[int] = None
    precipitation_inches: Optional[float] = None
    characteristics: Optional[Dict] = None


@dataclass
class ClimateDetectionResult:
    """Result of climate zone detection."""
    primary_zone: ClimateZone
    alternative_zones: List[ClimateZone]
    confidence_score: float
    detection_method: str
    coordinates: Tuple[float, float]
    elevation_ft: Optional[float] = None


class ClimateZoneService:
    """Service for climate zone detection and management."""
    
    def __init__(self):
        self.usda_zones = self._initialize_usda_zones()
        self.koppen_types = self._initialize_koppen_types()
        self.agricultural_zones = self._initialize_agricultural_zones()
        self._cache = {}
        self._cache_ttl = timedelta(hours=24)
    
    def _initialize_usda_zones(self) -> Dict[str, ClimateZone]:
        """Initialize USDA Hardiness Zone data."""
        zones = {}
        
        # USDA Hardiness Zones 1-13 with temperature ranges
        usda_data = [
            ("1a", "Extreme Cold", -60, -55),
            ("1b", "Extreme Cold", -55, -50),
            ("2a", "Very Cold", -50, -45),
            ("2b", "Very Cold", -45, -40),
            ("3a", "Cold", -40, -35),
            ("3b", "Cold", -35, -30),
            ("4a", "Cold", -30, -25),
            ("4b", "Cold", -25, -20),
            ("5a", "Cool", -20, -15),
            ("5b", "Cool", -15, -10),
            ("6a", "Moderate", -10, -5),
            ("6b", "Moderate", -5, 0),
            ("7a", "Moderate", 0, 5),
            ("7b", "Moderate", 5, 10),
            ("8a", "Warm", 10, 15),
            ("8b", "Warm", 15, 20),
            ("9a", "Hot", 20, 25),
            ("9b", "Hot", 25, 30),
            ("10a", "Very Hot", 30, 35),
            ("10b", "Very Hot", 35, 40),
            ("11a", "Tropical", 40, 45),
            ("11b", "Tropical", 45, 50),
            ("12a", "Tropical", 50, 55),
            ("12b", "Tropical", 55, 60),
            ("13a", "Tropical", 60, 65),
            ("13b", "Tropical", 65, 70),
        ]
        
        for zone_id, description, min_temp, max_temp in usda_data:
            zones[zone_id] = ClimateZone(
                zone_id=zone_id,
                zone_type=ClimateZoneType.USDA_HARDINESS,
                name=f"USDA Zone {zone_id}",
                description=f"{description} ({min_temp}°F to {max_temp}°F)",
                min_temp_f=min_temp,
                max_temp_f=max_temp,
                characteristics={
                    "suitable_for": self._get_zone_crops(zone_id),
                    "growing_season": self._estimate_growing_season(min_temp, max_temp)
                }
            )
        
        return zones
    
    def _initialize_koppen_types(self) -> Dict[str, ClimateZone]:
        """Initialize Köppen climate classification data."""
        types = {}
        
        koppen_data = [
            ("Af", "Tropical Rainforest", "Hot and wet year-round"),
            ("Am", "Tropical Monsoon", "Hot with distinct wet/dry seasons"),
            ("Aw", "Tropical Savanna", "Hot with dry winter"),
            ("BWh", "Hot Desert", "Hot and arid year-round"),
            ("BWk", "Cold Desert", "Cold and arid"),
            ("BSh", "Hot Semi-Arid", "Hot and semi-arid"),
            ("BSk", "Cold Semi-Arid", "Cold and semi-arid"),
            ("Cfa", "Humid Subtropical", "Hot humid summers, mild winters"),
            ("Cfb", "Oceanic", "Mild temperatures, wet year-round"),
            ("Cfc", "Subpolar Oceanic", "Cool summers, mild winters"),
            ("Csa", "Mediterranean", "Hot dry summers, mild wet winters"),
            ("Csb", "Warm Mediterranean", "Warm dry summers, mild wet winters"),
            ("Csc", "Cool Mediterranean", "Cool dry summers, mild wet winters"),
            ("Cwa", "Monsoon Subtropical", "Hot wet summers, dry winters"),
            ("Cwb", "Subtropical Highland", "Mild wet summers, dry winters"),
            ("Cwc", "Cold Subtropical Highland", "Cool wet summers, dry winters"),
            ("Dfa", "Hot Continental", "Hot summers, cold winters"),
            ("Dfb", "Warm Continental", "Warm summers, cold winters"),
            ("Dfc", "Subarctic", "Cool summers, very cold winters"),
            ("Dfd", "Extremely Cold Subarctic", "Cool summers, extremely cold winters"),
            ("Dsa", "Mediterranean Continental", "Hot dry summers, cold winters"),
            ("Dsb", "Warm Mediterranean Continental", "Warm dry summers, cold winters"),
            ("Dsc", "Cool Mediterranean Continental", "Cool dry summers, cold winters"),
            ("Dwa", "Monsoon Continental", "Hot wet summers, cold dry winters"),
            ("Dwb", "Warm Monsoon Continental", "Warm wet summers, cold dry winters"),
            ("Dwc", "Cool Monsoon Continental", "Cool wet summers, cold dry winters"),
            ("Dwd", "Extremely Cold Monsoon Continental", "Cool wet summers, extremely cold dry winters"),
            ("ET", "Tundra", "Very cold, short growing season"),
            ("EF", "Ice Cap", "Permanently frozen"),
        ]
        
        for code, name, description in koppen_data:
            types[code] = ClimateZone(
                zone_id=code,
                zone_type=ClimateZoneType.KOPPEN,
                name=f"Köppen {code} - {name}",
                description=description,
                characteristics={
                    "agricultural_suitability": self._get_koppen_agriculture(code),
                    "precipitation_pattern": self._get_precipitation_pattern(code),
                    "temperature_pattern": self._get_temperature_pattern(code)
                }
            )
        
        return types
    
    def _initialize_agricultural_zones(self) -> Dict[str, ClimateZone]:
        """Initialize agricultural climate zones."""
        zones = {}
        
        ag_zones = [
            ("corn_belt", "Corn Belt", "Ideal for corn and soybean production", 140, 180),
            ("wheat_belt", "Wheat Belt", "Suitable for wheat production", 120, 160),
            ("cotton_belt", "Cotton Belt", "Warm climate for cotton", 180, 220),
            ("rice_belt", "Rice Belt", "Hot humid climate for rice", 200, 240),
            ("vegetable_zone", "Vegetable Zone", "Moderate climate for vegetables", 160, 200),
            ("fruit_zone", "Fruit Zone", "Temperate climate for fruit trees", 150, 190),
            ("dairy_zone", "Dairy Zone", "Cool climate suitable for dairy farming", 120, 160),
            ("rangeland", "Rangeland", "Semi-arid climate for grazing", 100, 140),
        ]
        
        for zone_id, name, description, min_season, max_season in ag_zones:
            zones[zone_id] = ClimateZone(
                zone_id=zone_id,
                zone_type=ClimateZoneType.AGRICULTURAL,
                name=name,
                description=description,
                growing_season_days=(min_season + max_season) // 2,
                characteristics={
                    "primary_crops": self._get_agricultural_zone_crops(zone_id),
                    "management_practices": self._get_zone_practices(zone_id)
                }
            )
        
        return zones
    
    async def detect_climate_zone(
        self, 
        latitude: float, 
        longitude: float,
        elevation_ft: Optional[float] = None
    ) -> ClimateDetectionResult:
        """
        Detect climate zone from coordinates.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            elevation_ft: Elevation in feet (optional)
            
        Returns:
            ClimateDetectionResult with detected zones and confidence
        """
        try:
            # Check cache first
            cache_key = f"{latitude:.4f},{longitude:.4f}"
            if cache_key in self._cache:
                cached_result, timestamp = self._cache[cache_key]
                if datetime.now() - timestamp < self._cache_ttl:
                    logger.info(f"Returning cached climate zone for {cache_key}")
                    return cached_result
            
            # Detect USDA hardiness zone
            usda_zone = await self._detect_usda_zone(latitude, longitude, elevation_ft)
            
            # Detect Köppen climate type
            koppen_type = await self._detect_koppen_type(latitude, longitude)
            
            # Detect agricultural zone
            ag_zone = await self._detect_agricultural_zone(latitude, longitude, usda_zone)
            
            # Calculate confidence based on data quality and consistency
            confidence = self._calculate_confidence(usda_zone, koppen_type, ag_zone)
            
            # Create result
            result = ClimateDetectionResult(
                primary_zone=usda_zone,
                alternative_zones=[koppen_type, ag_zone] if koppen_type and ag_zone else [],
                confidence_score=confidence,
                detection_method="coordinate_based",
                coordinates=(latitude, longitude),
                elevation_ft=elevation_ft
            )
            
            # Cache result
            self._cache[cache_key] = (result, datetime.now())
            
            logger.info(f"Detected climate zone {usda_zone.zone_id} for coordinates {latitude}, {longitude}")
            return result
            
        except Exception as e:
            logger.error(f"Error detecting climate zone: {str(e)}")
            # Return fallback zone
            return self._get_fallback_zone(latitude, longitude)
    
    async def _detect_usda_zone(
        self, 
        latitude: float, 
        longitude: float, 
        elevation_ft: Optional[float] = None
    ) -> ClimateZone:
        """Detect USDA hardiness zone from coordinates."""
        
        # Simplified USDA zone detection based on latitude and elevation
        # In production, this would use actual USDA zone shapefiles or API
        
        base_zone = self._estimate_zone_from_latitude(latitude)
        
        # Adjust for elevation (approximately 3.5°F per 1000 ft elevation)
        if elevation_ft:
            temp_adjustment = -(elevation_ft / 1000) * 3.5
            base_zone = self._adjust_zone_for_temperature(base_zone, temp_adjustment)
        
        return self.usda_zones.get(base_zone, self.usda_zones["6a"])
    
    async def _detect_koppen_type(self, latitude: float, longitude: float) -> Optional[ClimateZone]:
        """Detect Köppen climate type from coordinates."""
        
        # Simplified Köppen detection based on latitude
        # In production, this would use detailed climate data
        
        abs_lat = abs(latitude)
        
        if abs_lat < 23.5:  # Tropical
            if longitude < -60:  # Americas
                return self.koppen_types.get("Aw")  # Tropical savanna
            else:
                return self.koppen_types.get("Af")  # Tropical rainforest
        elif abs_lat < 35:  # Subtropical
            if -125 < longitude < -65:  # North America
                return self.koppen_types.get("Cfa")  # Humid subtropical
            else:
                return self.koppen_types.get("Csa")  # Mediterranean
        elif abs_lat < 50:  # Temperate
            return self.koppen_types.get("Cfb")  # Oceanic
        else:  # Cold
            return self.koppen_types.get("Dfc")  # Subarctic
    
    async def _detect_agricultural_zone(
        self, 
        latitude: float, 
        longitude: float, 
        usda_zone: ClimateZone
    ) -> Optional[ClimateZone]:
        """Detect agricultural zone from coordinates and USDA zone."""
        
        # Map USDA zones to agricultural zones
        zone_mapping = {
            "3a": "dairy_zone", "3b": "dairy_zone",
            "4a": "dairy_zone", "4b": "dairy_zone",
            "5a": "corn_belt", "5b": "corn_belt",
            "6a": "corn_belt", "6b": "corn_belt",
            "7a": "corn_belt", "7b": "vegetable_zone",
            "8a": "cotton_belt", "8b": "cotton_belt",
            "9a": "cotton_belt", "9b": "rice_belt",
            "10a": "rice_belt", "10b": "rice_belt",
        }
        
        ag_zone_id = zone_mapping.get(usda_zone.zone_id, "vegetable_zone")
        return self.agricultural_zones.get(ag_zone_id)
    
    def _estimate_zone_from_latitude(self, latitude: float) -> str:
        """Estimate USDA zone from latitude (simplified)."""
        
        # Rough latitude to USDA zone mapping for North America
        if latitude > 60:
            return "1a"
        elif latitude > 55:
            return "2a"
        elif latitude > 50:
            return "3a"
        elif latitude > 45:
            return "4a"
        elif latitude > 40:
            return "5a"
        elif latitude > 35:
            return "6a"
        elif latitude > 30:
            return "7a"
        elif latitude > 25:
            return "8a"
        elif latitude > 20:
            return "9a"
        else:
            return "10a"
    
    def _adjust_zone_for_temperature(self, base_zone: str, temp_adjustment: float) -> str:
        """Adjust USDA zone based on temperature change."""
        
        # Each USDA zone represents about 10°F difference
        zone_adjustment = int(temp_adjustment / 10)
        
        # Extract zone number and letter
        zone_num = int(base_zone[0])
        zone_letter = base_zone[1]
        
        # Adjust zone
        if zone_adjustment < 0:  # Colder
            if zone_letter == 'a':
                zone_num = max(1, zone_num + zone_adjustment)
                zone_letter = 'b'
            else:
                zone_num = max(1, zone_num + zone_adjustment)
                zone_letter = 'a'
        elif zone_adjustment > 0:  # Warmer
            if zone_letter == 'b':
                zone_num = min(13, zone_num + zone_adjustment)
                zone_letter = 'a'
            else:
                zone_num = min(13, zone_num + zone_adjustment)
                zone_letter = 'b'
        
        return f"{zone_num}{zone_letter}"
    
    def _calculate_confidence(
        self, 
        usda_zone: ClimateZone, 
        koppen_type: Optional[ClimateZone], 
        ag_zone: Optional[ClimateZone]
    ) -> float:
        """Calculate confidence score for climate zone detection."""
        
        base_confidence = 0.7  # Base confidence for coordinate-based detection
        
        # Increase confidence if multiple zone types are consistent
        if koppen_type and ag_zone:
            base_confidence += 0.2
        elif koppen_type or ag_zone:
            base_confidence += 0.1
        
        return min(1.0, base_confidence)
    
    def _get_fallback_zone(self, latitude: float, longitude: float) -> ClimateDetectionResult:
        """Get fallback climate zone when detection fails."""
        
        fallback_zone = self.usda_zones["6a"]  # Moderate zone as fallback
        
        return ClimateDetectionResult(
            primary_zone=fallback_zone,
            alternative_zones=[],
            confidence_score=0.3,  # Low confidence for fallback
            detection_method="fallback",
            coordinates=(latitude, longitude)
        )
    
    def _get_zone_crops(self, zone_id: str) -> List[str]:
        """Get suitable crops for USDA zone."""
        
        crop_mapping = {
            "1a": ["hardy_grasses"], "1b": ["hardy_grasses"],
            "2a": ["barley", "oats"], "2b": ["barley", "oats", "rye"],
            "3a": ["wheat", "barley", "oats"], "3b": ["wheat", "barley", "oats", "canola"],
            "4a": ["corn", "wheat", "soybeans"], "4b": ["corn", "wheat", "soybeans"],
            "5a": ["corn", "soybeans", "wheat"], "5b": ["corn", "soybeans", "wheat"],
            "6a": ["corn", "soybeans", "vegetables"], "6b": ["corn", "soybeans", "vegetables"],
            "7a": ["corn", "soybeans", "vegetables"], "7b": ["vegetables", "fruits"],
            "8a": ["cotton", "vegetables", "fruits"], "8b": ["cotton", "vegetables", "fruits"],
            "9a": ["cotton", "rice", "citrus"], "9b": ["cotton", "rice", "citrus"],
            "10a": ["rice", "citrus", "tropical_fruits"], "10b": ["rice", "citrus", "tropical_fruits"],
        }
        
        return crop_mapping.get(zone_id, ["vegetables"])
    
    def _estimate_growing_season(self, min_temp: float, max_temp: float) -> int:
        """Estimate growing season length from temperature range."""
        
        # Rough estimate: warmer zones have longer growing seasons
        avg_temp = (min_temp + max_temp) / 2
        
        if avg_temp < -40:
            return 60
        elif avg_temp < -20:
            return 90
        elif avg_temp < 0:
            return 120
        elif avg_temp < 20:
            return 150
        elif avg_temp < 40:
            return 180
        else:
            return 220
    
    def _get_koppen_agriculture(self, code: str) -> str:
        """Get agricultural suitability for Köppen type."""
        
        agriculture_mapping = {
            "Af": "tropical_crops", "Am": "tropical_crops", "Aw": "tropical_crops",
            "BWh": "limited_irrigation", "BWk": "limited_grazing", 
            "BSh": "drought_tolerant", "BSk": "drought_tolerant",
            "Cfa": "diverse_crops", "Cfb": "temperate_crops", "Cfc": "cool_crops",
            "Csa": "mediterranean_crops", "Csb": "mediterranean_crops", "Csc": "cool_mediterranean",
            "Cwa": "monsoon_crops", "Cwb": "highland_crops", "Cwc": "cool_highland",
            "Dfa": "continental_crops", "Dfb": "continental_crops", "Dfc": "short_season",
            "Dfd": "very_short_season", "Dsa": "continental_dry", "Dsb": "continental_dry",
            "Dsc": "cool_continental", "Dwa": "monsoon_continental", "Dwb": "monsoon_continental",
            "Dwc": "cool_monsoon", "Dwd": "very_cool_monsoon", "ET": "no_agriculture", "EF": "no_agriculture"
        }
        
        return agriculture_mapping.get(code, "limited")
    
    def _get_precipitation_pattern(self, code: str) -> str:
        """Get precipitation pattern for Köppen type."""
        
        if 'f' in code:
            return "wet_year_round"
        elif 's' in code:
            return "dry_summer"
        elif 'w' in code:
            return "dry_winter"
        elif 'W' in code:
            return "arid"
        elif 'S' in code:
            return "semi_arid"
        else:
            return "variable"
    
    def _get_temperature_pattern(self, code: str) -> str:
        """Get temperature pattern for Köppen type."""
        
        if code.startswith('A'):
            return "tropical"
        elif code.startswith('B'):
            return "arid"
        elif code.startswith('C'):
            return "temperate"
        elif code.startswith('D'):
            return "continental"
        elif code.startswith('E'):
            return "polar"
        else:
            return "unknown"
    
    def _get_agricultural_zone_crops(self, zone_id: str) -> List[str]:
        """Get primary crops for agricultural zone."""
        
        crop_mapping = {
            "corn_belt": ["corn", "soybeans", "wheat"],
            "wheat_belt": ["wheat", "barley", "oats"],
            "cotton_belt": ["cotton", "peanuts", "tobacco"],
            "rice_belt": ["rice", "sugarcane", "soybeans"],
            "vegetable_zone": ["vegetables", "fruits", "herbs"],
            "fruit_zone": ["apples", "peaches", "berries"],
            "dairy_zone": ["hay", "pasture", "feed_corn"],
            "rangeland": ["native_grasses", "forage"]
        }
        
        return crop_mapping.get(zone_id, ["mixed_crops"])
    
    def _get_zone_practices(self, zone_id: str) -> List[str]:
        """Get management practices for agricultural zone."""
        
        practice_mapping = {
            "corn_belt": ["no_till", "crop_rotation", "precision_agriculture"],
            "wheat_belt": ["conservation_tillage", "fallow_rotation", "drought_management"],
            "cotton_belt": ["integrated_pest_management", "irrigation", "cover_crops"],
            "rice_belt": ["flood_irrigation", "levee_management", "rotation_with_soybeans"],
            "vegetable_zone": ["intensive_management", "succession_planting", "pest_monitoring"],
            "fruit_zone": ["orchard_management", "pruning", "pest_control"],
            "dairy_zone": ["pasture_management", "forage_quality", "rotational_grazing"],
            "rangeland": ["grazing_management", "native_plant_conservation", "fire_management"]
        }
        
        return practice_mapping.get(zone_id, ["sustainable_practices"])
    
    def get_zone_by_id(self, zone_id: str, zone_type: ClimateZoneType) -> Optional[ClimateZone]:
        """Get climate zone by ID and type."""
        
        if zone_type == ClimateZoneType.USDA_HARDINESS:
            return self.usda_zones.get(zone_id)
        elif zone_type == ClimateZoneType.KOPPEN:
            return self.koppen_types.get(zone_id)
        elif zone_type == ClimateZoneType.AGRICULTURAL:
            return self.agricultural_zones.get(zone_id)
        
        return None
    
    def list_zones(self, zone_type: Optional[ClimateZoneType] = None) -> List[ClimateZone]:
        """List available climate zones."""
        
        if zone_type == ClimateZoneType.USDA_HARDINESS:
            return list(self.usda_zones.values())
        elif zone_type == ClimateZoneType.KOPPEN:
            return list(self.koppen_types.values())
        elif zone_type == ClimateZoneType.AGRICULTURAL:
            return list(self.agricultural_zones.values())
        else:
            # Return all zones
            all_zones = []
            all_zones.extend(self.usda_zones.values())
            all_zones.extend(self.koppen_types.values())
            all_zones.extend(self.agricultural_zones.values())
            return all_zones
    
    async def validate_zone_for_location(
        self, 
        zone_id: str, 
        zone_type: ClimateZoneType,
        latitude: float, 
        longitude: float
    ) -> Dict:
        """Validate if a climate zone is appropriate for a location."""
        
        # Detect actual climate zone for location
        detected = await self.detect_climate_zone(latitude, longitude)
        
        # Get the specified zone
        specified_zone = self.get_zone_by_id(zone_id, zone_type)
        
        if not specified_zone:
            return {
                "valid": False,
                "confidence": 0.0,
                "message": f"Unknown zone: {zone_id}",
                "detected_zone": detected.primary_zone.zone_id
            }
        
        # Compare zones
        if zone_type == ClimateZoneType.USDA_HARDINESS:
            is_match = detected.primary_zone.zone_id == zone_id
            confidence = 1.0 if is_match else self._calculate_zone_similarity(
                detected.primary_zone.zone_id, zone_id
            )
        else:
            # For other zone types, check if they're in alternatives
            is_match = any(zone.zone_id == zone_id for zone in detected.alternative_zones)
            confidence = 0.8 if is_match else 0.3
        
        return {
            "valid": confidence > 0.5,
            "confidence": confidence,
            "message": self._get_validation_message(is_match, detected.primary_zone, specified_zone),
            "detected_zone": detected.primary_zone.zone_id,
            "specified_zone": zone_id
        }
    
    def _calculate_zone_similarity(self, zone1: str, zone2: str) -> float:
        """Calculate similarity between two USDA zones."""
        
        # Extract zone numbers
        try:
            num1 = int(zone1[0])
            num2 = int(zone2[0])
            
            # Zones within 1 number are similar
            diff = abs(num1 - num2)
            if diff == 0:
                return 1.0
            elif diff == 1:
                return 0.7
            elif diff == 2:
                return 0.4
            else:
                return 0.2
        except:
            return 0.2
    
    def _get_validation_message(
        self, 
        is_match: bool, 
        detected_zone: ClimateZone, 
        specified_zone: ClimateZone
    ) -> str:
        """Get validation message for zone comparison."""
        
        if is_match:
            return f"Zone {specified_zone.zone_id} matches detected zone for this location."
        else:
            return (f"Specified zone {specified_zone.zone_id} differs from detected zone "
                   f"{detected_zone.zone_id}. Consider using the detected zone for better accuracy.")


# Global service instance
climate_zone_service = ClimateZoneService()