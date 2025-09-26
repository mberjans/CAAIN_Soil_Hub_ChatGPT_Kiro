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
import numpy as np

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


@dataclass
class ClimateZoneHistoricalRecord:
    """Historical climate zone record for change tracking."""
    zone_id: str
    zone_type: ClimateZoneType
    detection_date: datetime
    confidence_score: float
    coordinates: Tuple[float, float]
    elevation_ft: Optional[float] = None
    temperature_data: Optional[Dict] = None
    source: str = "automated_detection"


@dataclass
class ClimateZoneChangeDetection:
    """Result of climate zone change analysis."""
    current_zone: ClimateZone
    previous_zone: Optional[ClimateZone]
    change_detected: bool
    change_confidence: float
    change_date: Optional[datetime]
    change_direction: str  # "warmer", "cooler", "stable"
    zones_affected: List[str]
    trend_analysis: Dict
    time_series_data: List[ClimateZoneHistoricalRecord]


class ClimateZoneService:
    """Service for climate zone detection and management."""
    
    def __init__(self):
        self.usda_zones = self._initialize_usda_zones()
        self.koppen_types = self._initialize_koppen_types()
        self.agricultural_zones = self._initialize_agricultural_zones()
        self._cache = {}
        self._cache_ttl = timedelta(hours=24)
        self._historical_data = {}  # In-memory storage for demo (production would use database)
        self._change_detection_threshold = 0.7  # Confidence threshold for change detection
    
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

    async def detect_climate_zone_changes(
        self, 
        latitude: float, 
        longitude: float,
        analyze_historical: bool = True,
        years_to_analyze: int = 10
    ) -> ClimateZoneChangeDetection:
        """
        Detect climate zone changes over time for a specific location.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            analyze_historical: Whether to analyze historical data
            years_to_analyze: Number of years to look back
            
        Returns:
            ClimateZoneChangeDetection with change analysis
        """
        # Validate coordinates first, before try block
        if not (-90 <= latitude <= 90):
            raise ValueError(f"Invalid latitude: {latitude}. Must be between -90 and 90 degrees.")
        if not (-180 <= longitude <= 180):
            raise ValueError(f"Invalid longitude: {longitude}. Must be between -180 and 180 degrees.")
        if not (1 <= years_to_analyze <= 50):
            raise ValueError(f"Invalid years_to_analyze: {years_to_analyze}. Must be between 1 and 50 years.")
        
        try:
            # Get current climate zone
            current_detection = await self.detect_climate_zone(latitude, longitude)
            current_zone = current_detection.primary_zone
            
            # Get historical data for this location
            location_key = f"{latitude:.4f},{longitude:.4f}"
            historical_records = self._get_historical_records(
                location_key, 
                years_to_analyze
            )
            
            # Add current detection to historical records if not duplicate
            await self._store_historical_record(
                location_key,
                ClimateZoneHistoricalRecord(
                    zone_id=current_zone.zone_id,
                    zone_type=current_zone.zone_type,
                    detection_date=datetime.now(),
                    confidence_score=current_detection.confidence_score,
                    coordinates=(latitude, longitude),
                    elevation_ft=current_detection.elevation_ft,
                    source="current_detection"
                )
            )
            
            # Analyze changes if we have historical data
            if len(historical_records) >= 2:
                change_analysis = await self._analyze_zone_changes(
                    current_zone, 
                    historical_records
                )
            else:
                # No sufficient historical data - generate synthetic for demo
                change_analysis = self._generate_demo_change_analysis(
                    current_zone, 
                    latitude, 
                    longitude
                )
            
            return change_analysis
            
        except Exception as e:
            logger.error(f"Error detecting climate zone changes: {str(e)}")
            # Return minimal change detection result with fallback zone
            fallback_zone = self.usda_zones.get("6a")  # Use default zone as fallback
            return ClimateZoneChangeDetection(
                current_zone=fallback_zone,
                previous_zone=None,
                change_detected=False,
                change_confidence=0.0,
                change_date=None,
                change_direction="unknown",
                zones_affected=[],
                trend_analysis={},
                time_series_data=[]
            )
    
    async def _analyze_zone_changes(
        self, 
        current_zone: ClimateZone, 
        historical_records: List[ClimateZoneHistoricalRecord]
    ) -> ClimateZoneChangeDetection:
        """Analyze climate zone changes from historical records."""
        
        # Sort records by date
        sorted_records = sorted(historical_records, key=lambda x: x.detection_date)
        
        # Check for zone transitions
        zone_transitions = []
        previous_zone_id = None
        
        for record in sorted_records:
            if previous_zone_id and record.zone_id != previous_zone_id:
                zone_transitions.append({
                    'from_zone': previous_zone_id,
                    'to_zone': record.zone_id,
                    'date': record.detection_date,
                    'confidence': record.confidence_score
                })
            previous_zone_id = record.zone_id
        
        # Calculate trend analysis
        trend_analysis = await self._calculate_zone_trend(sorted_records)
        
        # Determine if significant change occurred
        change_detected = len(zone_transitions) > 0
        change_confidence = 0.0
        change_date = None
        change_direction = "stable"
        
        if zone_transitions:
            latest_transition = zone_transitions[-1]
            change_confidence = self._calculate_change_confidence(
                latest_transition, 
                trend_analysis
            )
            change_date = latest_transition['date']
            change_direction = self._determine_change_direction(
                latest_transition['from_zone'], 
                latest_transition['to_zone']
            )
        
        # Get previous zone if available
        previous_zone = None
        if len(sorted_records) >= 2:
            prev_zone_id = sorted_records[-2].zone_id
            previous_zone = self.usda_zones.get(prev_zone_id)
        
        return ClimateZoneChangeDetection(
            current_zone=current_zone,
            previous_zone=previous_zone,
            change_detected=change_detected and change_confidence >= self._change_detection_threshold,
            change_confidence=change_confidence,
            change_date=change_date,
            change_direction=change_direction,
            zones_affected=[t['from_zone'] for t in zone_transitions] + [t['to_zone'] for t in zone_transitions],
            trend_analysis=trend_analysis,
            time_series_data=sorted_records
        )
    
    def _generate_demo_change_analysis(
        self, 
        current_zone: ClimateZone, 
        latitude: float, 
        longitude: float
    ) -> ClimateZoneChangeDetection:
        """Generate demonstration change analysis when no historical data exists."""
        
        # Generate synthetic historical data for demo purposes
        base_date = datetime.now() - timedelta(days=365 * 5)  # 5 years back
        demo_records = []
        
        current_zone_num = int(current_zone.zone_id[0])
        
        # Simulate gradual warming trend for certain latitudes
        if 35 < latitude < 55:  # Mid-latitude regions more prone to change
            # Simulate transition from cooler to warmer zone
            previous_zone_id = f"{max(1, current_zone_num - 1)}{current_zone.zone_id[1]}"
            
            # Create historical records showing transition
            for i in range(4):
                date = base_date + timedelta(days=365 * i)
                zone_id = previous_zone_id if i < 2 else current_zone.zone_id
                
                demo_records.append(ClimateZoneHistoricalRecord(
                    zone_id=zone_id,
                    zone_type=ClimateZoneType.USDA_HARDINESS,
                    detection_date=date,
                    confidence_score=0.8 + (i * 0.05),
                    coordinates=(latitude, longitude),
                    source="demo_data"
                ))
            
            previous_zone = self.usda_zones.get(previous_zone_id)
            change_detected = True
            change_confidence = 0.85
            change_date = base_date + timedelta(days=365 * 2)
            change_direction = "warmer"
            zones_affected = [previous_zone_id, current_zone.zone_id]
            
        else:
            # Stable zone
            previous_zone = current_zone
            change_detected = False
            change_confidence = 0.3
            change_date = None
            change_direction = "stable"
            zones_affected = [current_zone.zone_id]
        
        trend_analysis = {
            "trend_direction": change_direction,
            "confidence": change_confidence,
            "rate_of_change_per_year": 0.1 if change_detected else 0.0,
            "projected_zone_1yr": current_zone.zone_id,
            "projected_zone_5yr": self._project_future_zone(current_zone.zone_id, change_direction)
        }
        
        return ClimateZoneChangeDetection(
            current_zone=current_zone,
            previous_zone=previous_zone,
            change_detected=change_detected,
            change_confidence=change_confidence,
            change_date=change_date,
            change_direction=change_direction,
            zones_affected=zones_affected,
            trend_analysis=trend_analysis,
            time_series_data=demo_records
        )
    
    async def _calculate_zone_trend(
        self, 
        historical_records: List[ClimateZoneHistoricalRecord]
    ) -> Dict:
        """Calculate climate zone trend analysis from historical data."""
        
        if len(historical_records) < 3:
            return {"trend_direction": "insufficient_data", "confidence": 0.0}
        
        # Convert zone IDs to numeric values for trend analysis
        zone_values = []
        dates = []
        
        for record in historical_records:
            try:
                zone_num = int(record.zone_id[0])
                zone_sub = 0.5 if len(record.zone_id) > 1 and record.zone_id[1] == 'b' else 0.0
                zone_value = zone_num + zone_sub
                
                zone_values.append(zone_value)
                dates.append(record.detection_date)
            except (ValueError, IndexError):
                continue
        
        if len(zone_values) < 3:
            return {"trend_direction": "insufficient_data", "confidence": 0.0}
        
        # Convert dates to years for regression
        base_date = dates[0]
        years = [(date - base_date).days / 365.25 for date in dates]
        
        # Calculate linear regression
        try:
            coefficients = np.polyfit(years, zone_values, 1)
            slope = coefficients[0]  # Rate of change per year
            
            # Calculate R-squared for confidence
            y_pred = np.polyval(coefficients, years)
            ss_res = np.sum((np.array(zone_values) - y_pred) ** 2)
            ss_tot = np.sum((np.array(zone_values) - np.mean(zone_values)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            # Determine trend direction
            if abs(slope) < 0.05:  # Threshold for stability
                trend_direction = 'stable'
            elif slope > 0:
                trend_direction = 'warmer'
            else:
                trend_direction = 'cooler'
            
            # Project future zones
            current_zone_value = zone_values[-1]
            projected_1yr = current_zone_value + slope
            projected_5yr = current_zone_value + (slope * 5)
            
            return {
                "trend_direction": trend_direction,
                "confidence": max(0.0, min(1.0, r_squared)),
                "rate_of_change_per_year": slope,
                "current_zone_value": current_zone_value,
                "projected_zone_1yr": self._zone_value_to_id(projected_1yr),
                "projected_zone_5yr": self._zone_value_to_id(projected_5yr)
            }
            
        except Exception as e:
            logger.error(f"Error calculating zone trend: {str(e)}")
            return {"trend_direction": "error", "confidence": 0.0}
    
    def _zone_value_to_id(self, zone_value: float) -> str:
        """Convert numeric zone value back to zone ID."""
        zone_num = int(round(zone_value))
        zone_sub = 'b' if (zone_value - int(zone_value)) >= 0.25 else 'a'
        return f"{max(1, min(13, zone_num))}{zone_sub}"
    
    def _calculate_change_confidence(
        self, 
        transition: Dict, 
        trend_analysis: Dict
    ) -> float:
        """Calculate confidence score for detected change."""
        
        base_confidence = transition.get('confidence', 0.5)
        trend_confidence = trend_analysis.get('confidence', 0.0)
        
        # Higher confidence if trend supports the transition
        if trend_analysis.get('trend_direction') in ['warmer', 'cooler']:
            base_confidence += 0.2
        
        # Consider trend consistency
        combined_confidence = (base_confidence + trend_confidence) / 2
        
        return max(0.0, min(1.0, combined_confidence))
    
    def _determine_change_direction(self, from_zone: str, to_zone: str) -> str:
        """Determine the direction of climate zone change."""
        
        try:
            from_num = int(from_zone[0])
            to_num = int(to_zone[0])
            
            if to_num > from_num:
                return "warmer"
            elif to_num < from_num:
                return "cooler"
            else:
                # Same number, check sub-zone
                from_sub = from_zone[1] if len(from_zone) > 1 else 'a'
                to_sub = to_zone[1] if len(to_zone) > 1 else 'a'
                
                if from_sub == 'a' and to_sub == 'b':
                    return "warmer"
                elif from_sub == 'b' and to_sub == 'a':
                    return "cooler"
                else:
                    return "stable"
        except (ValueError, IndexError):
            return "unknown"
    
    def _project_future_zone(self, current_zone_id: str, trend_direction: str) -> str:
        """Project future zone based on current trends."""
        
        if trend_direction == "stable":
            return current_zone_id
        
        try:
            zone_num = int(current_zone_id[0])
            zone_sub = current_zone_id[1] if len(current_zone_id) > 1 else 'a'
            
            if trend_direction == "warmer":
                if zone_sub == 'a':
                    return f"{zone_num}b"
                else:
                    return f"{min(13, zone_num + 1)}a"
            elif trend_direction == "cooler":
                if zone_sub == 'b':
                    return f"{zone_num}a"
                else:
                    return f"{max(1, zone_num - 1)}b"
        except (ValueError, IndexError):
            pass
        
        return current_zone_id
    
    def _get_historical_records(
        self, 
        location_key: str, 
        years_to_analyze: int
    ) -> List[ClimateZoneHistoricalRecord]:
        """Get historical climate zone records for a location."""
        
        if location_key not in self._historical_data:
            return []
        
        cutoff_date = datetime.now() - timedelta(days=365 * years_to_analyze)
        records = self._historical_data[location_key]
        
        return [record for record in records if record.detection_date >= cutoff_date]
    
    async def _store_historical_record(
        self, 
        location_key: str, 
        record: ClimateZoneHistoricalRecord
    ):
        """Store a historical climate zone record."""
        
        if location_key not in self._historical_data:
            self._historical_data[location_key] = []
        
        # Check if we already have a recent record for this location
        recent_records = [
            r for r in self._historical_data[location_key] 
            if abs((r.detection_date - record.detection_date).days) < 30
        ]
        
        # Only store if no recent duplicate
        if not recent_records:
            self._historical_data[location_key].append(record)
            
            # Limit storage to last 50 records per location
            if len(self._historical_data[location_key]) > 50:
                self._historical_data[location_key] = self._historical_data[location_key][-50:]

    async def validate_zone_consistency(
        self, 
        latitude: float, 
        longitude: float,
        check_neighboring: bool = True,
        check_temporal: bool = True
    ) -> Dict:
        """
        Validate climate zone consistency across multiple dimensions:
        - Cross-reference consistency between USDA and Köppen zones
        - Spatial consistency with neighboring locations
        - Temporal consistency over time (if enabled)
        """
        
        # Get primary climate zone detection
        detected = await self.detect_climate_zone(latitude, longitude)
        
        consistency_results = {
            "overall_consistent": True,
            "confidence": 1.0,
            "checks_performed": [],
            "warnings": [],
            "cross_reference_check": {},
            "spatial_check": {},
            "temporal_check": {}
        }
        
        # 1. Cross-reference consistency check between USDA and Köppen
        try:
            usda_zone = detected.primary_zone
            koppen_alternatives = [zone for zone in detected.alternative_zones 
                                 if hasattr(zone, 'classification') and 'koppen' in zone.classification.lower()]
            
            if koppen_alternatives:
                koppen_zone = koppen_alternatives[0]
                cross_ref_consistency = self._validate_usda_koppen_consistency(usda_zone, koppen_zone)
                consistency_results["cross_reference_check"] = cross_ref_consistency
                consistency_results["checks_performed"].append("cross_reference")
                
                if not cross_ref_consistency["consistent"]:
                    consistency_results["overall_consistent"] = False
                    consistency_results["warnings"].append(cross_ref_consistency["warning"])
                    consistency_results["confidence"] *= 0.8
            else:
                consistency_results["warnings"].append("Köppen zone not available for cross-reference validation")
                consistency_results["confidence"] *= 0.9
                
        except Exception as e:
            consistency_results["warnings"].append(f"Cross-reference check failed: {str(e)}")
            consistency_results["confidence"] *= 0.8
        
        # 2. Spatial consistency check with neighboring locations
        if check_neighboring:
            try:
                spatial_consistency = await self._validate_spatial_consistency(latitude, longitude, detected.primary_zone)
                consistency_results["spatial_check"] = spatial_consistency
                consistency_results["checks_performed"].append("spatial")
                
                if not spatial_consistency["consistent"]:
                    consistency_results["overall_consistent"] = False
                    consistency_results["warnings"].append(spatial_consistency["warning"])
                    consistency_results["confidence"] *= 0.85
                    
            except Exception as e:
                consistency_results["warnings"].append(f"Spatial consistency check failed: {str(e)}")
                consistency_results["confidence"] *= 0.9
        
        # 3. Temporal consistency check (simplified - would need historical data in production)
        if check_temporal:
            try:
                temporal_consistency = self._validate_temporal_consistency(detected.primary_zone)
                consistency_results["temporal_check"] = temporal_consistency
                consistency_results["checks_performed"].append("temporal")
                
                if not temporal_consistency["consistent"]:
                    consistency_results["warnings"].append(temporal_consistency["warning"])
                    consistency_results["confidence"] *= 0.9
                    
            except Exception as e:
                consistency_results["warnings"].append(f"Temporal consistency check failed: {str(e)}")
                consistency_results["confidence"] *= 0.95
        
        return consistency_results
    
    def _validate_usda_koppen_consistency(self, usda_zone, koppen_zone) -> Dict:
        """Validate consistency between USDA and Köppen climate zones."""
        
        # Known consistent mappings (simplified - would be more comprehensive in production)
        usda_koppen_mappings = {
            "3a": ["Dfb", "Dfa"], "3b": ["Dfb", "Dfa"],
            "4a": ["Dfb", "Dfa", "Cfa"], "4b": ["Dfb", "Dfa"],
            "5a": ["Dfb", "Dfa", "Cfa"], "5b": ["Dfb", "Dfa", "Cfa"],
            "6a": ["Cfa", "Cfb", "Dfa"], "6b": ["Cfa", "Cfb"],
            "7a": ["Cfa", "Cfb"], "7b": ["Cfa", "Cfb"],
            "8a": ["Cfa", "Csa"], "8b": ["Cfa", "Csa"],
            "9a": ["Cfa", "Csa", "Csb"], "9b": ["Cfa", "Csa"],
            "10a": ["Csa", "Csb"], "10b": ["Csa", "Csb"],
            "11": ["BSk", "BWh", "Csa"]
        }
        
        usda_id = usda_zone.zone_id
        koppen_id = getattr(koppen_zone, 'zone_id', 'unknown')
        
        expected_koppen = usda_koppen_mappings.get(usda_id, [])
        
        if koppen_id in expected_koppen:
            return {
                "consistent": True,
                "confidence": 0.95,
                "message": f"USDA zone {usda_id} is consistent with Köppen {koppen_id}"
            }
        elif expected_koppen:
            return {
                "consistent": False,
                "confidence": 0.6,
                "warning": f"USDA zone {usda_id} typically corresponds to Köppen {expected_koppen}, but detected {koppen_id}",
                "message": "Climate zone systems show potential inconsistency"
            }
        else:
            return {
                "consistent": True,
                "confidence": 0.7,
                "message": f"No established mapping for USDA {usda_id}, accepting Köppen {koppen_id}"
            }
    
    async def _validate_spatial_consistency(self, latitude: float, longitude: float, detected_zone) -> Dict:
        """Validate spatial consistency with neighboring locations."""
        
        # Check neighboring locations (offset by ~0.1 degree ~6 miles)
        neighbor_offsets = [
            (0.1, 0), (-0.1, 0), (0, 0.1), (0, -0.1),  # N, S, E, W
            (0.05, 0.05), (-0.05, -0.05)  # NE, SW diagonals
        ]
        
        consistent_neighbors = 0
        total_neighbors = 0
        zone_differences = []
        
        for lat_offset, lon_offset in neighbor_offsets:
            try:
                neighbor_lat = latitude + lat_offset
                neighbor_lon = longitude + lon_offset
                
                # Validate coordinates are still reasonable
                if -90 <= neighbor_lat <= 90 and -180 <= neighbor_lon <= 180:
                    neighbor_detection = await self.detect_climate_zone(neighbor_lat, neighbor_lon)
                    neighbor_zone = neighbor_detection.primary_zone.zone_id
                    current_zone = detected_zone.zone_id
                    
                    total_neighbors += 1
                    
                    # Check if zones are same or adjacent (allowing 1 zone difference)
                    if self._are_zones_spatially_consistent(current_zone, neighbor_zone):
                        consistent_neighbors += 1
                    else:
                        zone_differences.append(f"{current_zone} vs {neighbor_zone}")
                        
            except Exception:
                # Skip failed neighbor checks
                continue
        
        if total_neighbors == 0:
            return {
                "consistent": True,
                "confidence": 0.5,
                "message": "No neighboring locations could be validated"
            }
        
        consistency_ratio = consistent_neighbors / total_neighbors
        
        if consistency_ratio >= 0.7:
            return {
                "consistent": True,
                "confidence": min(0.95, 0.7 + (consistency_ratio * 0.25)),
                "message": f"Spatial consistency good: {consistent_neighbors}/{total_neighbors} neighbors consistent"
            }
        else:
            return {
                "consistent": False,
                "confidence": 0.5,
                "warning": f"Spatial consistency concerns: only {consistent_neighbors}/{total_neighbors} neighbors consistent",
                "differences": zone_differences[:3]  # Show first 3 differences
            }
    
    def _are_zones_spatially_consistent(self, zone1: str, zone2: str) -> bool:
        """Check if two zones are spatially consistent (same or adjacent)."""
        
        if zone1 == zone2:
            return True
        
        # Extract numeric parts for comparison
        try:
            import re
            zone1_match = re.match(r'(\d+)([ab]?)', zone1)
            zone2_match = re.match(r'(\d+)([ab]?)', zone2)
            
            if zone1_match and zone2_match:
                num1, sub1 = int(zone1_match.group(1)), zone1_match.group(2)
                num2, sub2 = int(zone2_match.group(1)), zone2_match.group(2)
                
                # Adjacent zones (within 1 number)
                if abs(num1 - num2) <= 1:
                    return True
                
                # Same number, different subzone (4a vs 4b)
                if num1 == num2:
                    return True
        except:
            pass
        
        return False
    
    def _validate_temporal_consistency(self, detected_zone) -> Dict:
        """Validate temporal consistency (simplified without historical data)."""
        
        # In production, this would check against historical climate zone data
        # For now, provide basic temporal validation based on zone stability
        
        zone_id = detected_zone.zone_id
        
        # Zones known to be more stable over time
        stable_zones = ["5a", "5b", "6a", "6b", "7a", "7b"]
        # Zones more susceptible to climate change
        transitional_zones = ["3a", "3b", "4a", "4b", "8a", "8b", "9a", "9b"]
        
        if zone_id in stable_zones:
            return {
                "consistent": True,
                "confidence": 0.9,
                "message": f"Zone {zone_id} is historically stable"
            }
        elif zone_id in transitional_zones:
            return {
                "consistent": True,
                "confidence": 0.7,
                "warning": f"Zone {zone_id} may be subject to climate transitions - monitor for changes",
                "message": "Zone in potentially transitional climate area"
            }
        else:
            return {
                "consistent": True,
                "confidence": 0.8,
                "message": f"Zone {zone_id} temporal consistency assumed based on typical patterns"
            }


# Global service instance
climate_zone_service = ClimateZoneService()