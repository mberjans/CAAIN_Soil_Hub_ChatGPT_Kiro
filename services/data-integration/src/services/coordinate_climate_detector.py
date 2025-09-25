"""
Coordinate-based Climate Zone Detection
Provides accurate climate zone detection from GPS coordinates.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import math
import asyncio
from datetime import datetime

from .climate_zone_service import ClimateZone, ClimateZoneType, ClimateDetectionResult
from .usda_zone_api import USDAZoneAPI, USDAZoneData
from .koppen_climate_service import KoppenClimateService, ClimateAnalysis
from .weather_climate_inference import WeatherClimateInference, ClimateInference
from .weather_service import WeatherService

logger = logging.getLogger(__name__)


@dataclass
class ElevationData:
    """Elevation data structure."""
    elevation_ft: float
    elevation_m: float
    source: str
    accuracy: str


@dataclass
class CoordinateClimateData:
    """Complete climate data for coordinates."""
    coordinates: Tuple[float, float]
    usda_zone: Optional[USDAZoneData]
    koppen_analysis: Optional[ClimateAnalysis]
    elevation_data: Optional[ElevationData]
    climate_adjustments: Dict
    confidence_factors: Dict
    detection_metadata: Dict


class CoordinateClimateDetector:
    """Service for detecting climate zones from coordinates."""
    
    def __init__(self):
        self.usda_api = USDAZoneAPI()
        self.koppen_service = KoppenClimateService()
        self.weather_inference = WeatherClimateInference()
        self.weather_service = WeatherService()
        self.elevation_cache = {}
        self.climate_cache = {}
        
        # Climate adjustment factors
        self.elevation_temp_lapse = -3.5  # °F per 1000 ft
        self.latitude_temp_gradient = 1.0  # °F per degree latitude
        self.coastal_moderation = 2.0     # °F moderation near coast
        
        # Boundary detection parameters
        self.zone_boundary_tolerance = 0.1  # degrees
        self.elevation_significance = 500   # ft minimum for adjustment
    
    async def detect_climate_from_coordinates(
        self,
        latitude: float,
        longitude: float,
        elevation_ft: Optional[float] = None,
        include_detailed_analysis: bool = True
    ) -> CoordinateClimateData:
        """
        Detect comprehensive climate data from coordinates.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            elevation_ft: Elevation in feet (optional, will be estimated if not provided)
            include_detailed_analysis: Whether to include detailed Köppen analysis
            
        Returns:
            CoordinateClimateData with comprehensive climate information
        """
        
        try:
            logger.info(f"Detecting climate for coordinates {latitude}, {longitude}")
            
            # Validate coordinates
            self._validate_coordinates(latitude, longitude)
            
            # Get or estimate elevation
            if elevation_ft is None:
                elevation_data = await self._estimate_elevation(latitude, longitude)
                elevation_ft = elevation_data.elevation_ft if elevation_data else 0
            else:
                elevation_data = ElevationData(
                    elevation_ft=elevation_ft,
                    elevation_m=elevation_ft * 0.3048,
                    source="provided",
                    accuracy="unknown"
                )
            
            # Detect USDA hardiness zone with weather fallback
            usda_zone = await self._detect_usda_zone_with_weather_fallback(
                latitude, longitude, elevation_ft
            )
            
            # Perform Köppen climate analysis if requested
            koppen_analysis = None
            if include_detailed_analysis:
                koppen_analysis = await self._perform_koppen_analysis(
                    latitude, longitude, elevation_ft
                )
            
            # Calculate climate adjustments
            climate_adjustments = self._calculate_climate_adjustments(
                latitude, longitude, elevation_ft, usda_zone
            )
            
            # Assess confidence factors
            confidence_factors = self._assess_confidence_factors(
                latitude, longitude, usda_zone, koppen_analysis, elevation_data
            )
            
            # Create detection metadata
            detection_metadata = {
                "detection_time": datetime.utcnow().isoformat(),
                "methods_used": self._get_detection_methods_used(usda_zone, koppen_analysis),
                "data_sources": self._get_data_sources_used(usda_zone, koppen_analysis),
                "boundary_proximity": self._assess_boundary_proximity(latitude, longitude),
                "microclimate_factors": self._identify_microclimate_factors(
                    latitude, longitude, elevation_ft
                )
            }
            
            result = CoordinateClimateData(
                coordinates=(latitude, longitude),
                usda_zone=usda_zone,
                koppen_analysis=koppen_analysis,
                elevation_data=elevation_data,
                climate_adjustments=climate_adjustments,
                confidence_factors=confidence_factors,
                detection_metadata=detection_metadata
            )
            
            logger.info(f"Successfully detected climate data for {latitude}, {longitude}")
            return result
            
        except Exception as e:
            logger.error(f"Error detecting climate from coordinates: {str(e)}")
            return self._get_fallback_climate_data(latitude, longitude)
    
    def _validate_coordinates(self, latitude: float, longitude: float):
        """Validate coordinate values."""
        
        if not -90 <= latitude <= 90:
            raise ValueError(f"Invalid latitude: {latitude}. Must be between -90 and 90.")
        
        if not -180 <= longitude <= 180:
            raise ValueError(f"Invalid longitude: {longitude}. Must be between -180 and 180.")
    
    async def _estimate_elevation(self, latitude: float, longitude: float) -> Optional[ElevationData]:
        """Estimate elevation from coordinates."""
        
        try:
            # Check cache first
            cache_key = f"elev_{latitude:.4f}_{longitude:.4f}"
            if cache_key in self.elevation_cache:
                return self.elevation_cache[cache_key]
            
            # In production, this would use a real elevation API
            # For now, we'll use a simplified estimation
            estimated_elevation = self._estimate_elevation_from_geography(latitude, longitude)
            
            elevation_data = ElevationData(
                elevation_ft=estimated_elevation,
                elevation_m=estimated_elevation * 0.3048,
                source="estimated",
                accuracy="approximate"
            )
            
            # Cache the result
            self.elevation_cache[cache_key] = elevation_data
            
            return elevation_data
            
        except Exception as e:
            logger.warning(f"Could not estimate elevation for {latitude}, {longitude}: {str(e)}")
            return None
    
    def _estimate_elevation_from_geography(self, latitude: float, longitude: float) -> float:
        """Estimate elevation based on geographic location."""
        
        # Simplified elevation estimation based on known geographic features
        # In production, this would use detailed elevation APIs or datasets
        
        # North America elevation patterns
        if -170 < longitude < -50 and 20 < latitude < 70:
            # Rocky Mountains
            if -125 < longitude < -100 and 35 < latitude < 50:
                return 3000 + abs(longitude + 110) * 200
            # Appalachian Mountains
            elif -85 < longitude < -75 and 35 < latitude < 45:
                return 1000 + abs(latitude - 40) * 100
            # Great Plains
            elif -105 < longitude < -95 and 30 < latitude < 50:
                return 1500 + abs(longitude + 100) * 50
            # Coastal areas
            elif longitude > -90 or longitude < -120:
                return 200 + abs(latitude - 40) * 10
            else:
                return 800  # Default for interior
        
        # Default elevation for other regions
        return 500
    
    async def _detect_usda_zone_with_weather_fallback(
        self,
        latitude: float,
        longitude: float,
        elevation_ft: float
    ) -> Optional[USDAZoneData]:
        """Detect USDA zone with weather data fallback when API fails."""
        
        try:
            # First try the standard USDA zone detection with adjustments
            usda_zone = await self._detect_usda_zone_with_adjustments(latitude, longitude, elevation_ft)
            
            # If we get a low-confidence result or the API fails, try weather inference
            if not usda_zone or (hasattr(usda_zone, 'confidence') and usda_zone.confidence < 0.6):
                logger.info(f"USDA API result has low confidence, attempting weather-based inference")
                weather_zone = await self._infer_zone_from_weather(latitude, longitude)
                
                if weather_zone and weather_zone.confidence_score > 0.8:
                    # Convert weather inference to USDAZoneData format
                    usda_zone = self._convert_weather_inference_to_usda(weather_zone, latitude, longitude)
                    logger.info(f"Using weather-inferred USDA zone: {usda_zone.zone}")
            
            return usda_zone
            
        except Exception as e:
            logger.error(f"Error in weather fallback detection: {str(e)}")
            # Try weather inference as last resort
            try:
                weather_zone = await self._infer_zone_from_weather(latitude, longitude)
                if weather_zone:
                    return self._convert_weather_inference_to_usda(weather_zone, latitude, longitude)
            except Exception as weather_e:
                logger.error(f"Weather inference also failed: {str(weather_e)}")
            
            return self._get_fallback_usda_zone(latitude, longitude)
    
    async def _infer_zone_from_weather(
        self,
        latitude: float,
        longitude: float
    ) -> Optional[ClimateInference]:
        """Infer climate zone from historical weather data."""
        
        try:
            # Get historical weather data for the location
            weather_data = await self.weather_service.get_historical_weather(
                latitude, longitude, years=3
            )
            
            if not weather_data or len(weather_data) < 365:  # Need at least 1 year of data
                logger.warning(f"Insufficient weather data for location {latitude}, {longitude}")
                return None
            
            # Use weather climate inference service
            climate_inference = await self.weather_inference.infer_climate_from_weather(
                weather_data, latitude, longitude
            )
            
            return climate_inference
            
        except Exception as e:
            logger.error(f"Error inferring climate from weather: {str(e)}")
            return None
    
    def _convert_weather_inference_to_usda(
        self,
        weather_inference: ClimateInference,
        latitude: float,
        longitude: float
    ) -> USDAZoneData:
        """Convert weather climate inference to USDA zone format."""
        
        zone = weather_inference.inferred_usda_zone
        temp_range = self._get_zone_temperature_range(zone)
        
        return USDAZoneData(
            zone=zone,
            temperature_range=temp_range,
            description=f"USDA Hardiness Zone {zone} (Weather-inferred)",
            coordinates=(latitude, longitude),
            confidence=weather_inference.confidence_score,
            source="weather_inference"
        )

    async def _detect_usda_zone_with_adjustments(
        self,
        latitude: float,
        longitude: float,
        elevation_ft: float
    ) -> Optional[USDAZoneData]:
        """Detect USDA zone with elevation and geographic adjustments."""
        
        try:
            # Get base USDA zone
            async with self.usda_api as api:
                base_zone = await api.get_zone_by_coordinates(latitude, longitude)
            
            if not base_zone:
                # Fallback to coordinate-based estimation
                base_zone = self._estimate_usda_zone_from_coordinates(latitude, longitude)
            
            # Apply elevation adjustments
            if elevation_ft > self.elevation_significance:
                adjusted_zone = self._adjust_zone_for_elevation(base_zone, elevation_ft)
            else:
                adjusted_zone = base_zone
            
            # Apply coastal moderation if applicable
            if self._is_coastal_location(latitude, longitude):
                adjusted_zone = self._apply_coastal_moderation(adjusted_zone, latitude, longitude)
            
            # Apply microclimate adjustments
            adjusted_zone = self._apply_microclimate_adjustments(
                adjusted_zone, latitude, longitude, elevation_ft
            )
            
            return adjusted_zone
            
        except Exception as e:
            logger.error(f"Error detecting USDA zone with adjustments: {str(e)}")
            return self._get_fallback_usda_zone(latitude, longitude)
    
    def _estimate_usda_zone_from_coordinates(
        self,
        latitude: float,
        longitude: float
    ) -> USDAZoneData:
        """Estimate USDA zone from coordinates as fallback."""
        
        # Simplified zone estimation based on latitude
        zone = self._latitude_to_usda_zone(latitude)
        temp_range = self._get_zone_temperature_range(zone)
        
        return USDAZoneData(
            zone=zone,
            temperature_range=temp_range,
            description=f"USDA Hardiness Zone {zone} (Estimated)",
            coordinates=(latitude, longitude),
            confidence=0.6,
            source="coordinate_estimation"
        )
    
    def _latitude_to_usda_zone(self, latitude: float) -> str:
        """Convert latitude to approximate USDA zone."""
        
        # Rough latitude to zone mapping for North America
        abs_lat = abs(latitude)
        
        if abs_lat > 65:
            return "1a"
        elif abs_lat > 60:
            return "2a"
        elif abs_lat > 55:
            return "3a"
        elif abs_lat > 50:
            return "4a"
        elif abs_lat > 45:
            return "5a"
        elif abs_lat > 40:
            return "6a"
        elif abs_lat > 35:
            return "7a"
        elif abs_lat > 30:
            return "8a"
        elif abs_lat > 25:
            return "9a"
        else:
            return "10a"
    
    def _get_zone_temperature_range(self, zone: str) -> Tuple[float, float]:
        """Get temperature range for USDA zone."""
        
        zone_temps = {
            "1a": (-60, -55), "1b": (-55, -50),
            "2a": (-50, -45), "2b": (-45, -40),
            "3a": (-40, -35), "3b": (-35, -30),
            "4a": (-30, -25), "4b": (-25, -20),
            "5a": (-20, -15), "5b": (-15, -10),
            "6a": (-10, -5), "6b": (-5, 0),
            "7a": (0, 5), "7b": (5, 10),
            "8a": (10, 15), "8b": (15, 20),
            "9a": (20, 25), "9b": (25, 30),
            "10a": (30, 35), "10b": (35, 40),
        }
        
        return zone_temps.get(zone, (0, 10))
    
    def _adjust_zone_for_elevation(self, base_zone: USDAZoneData, elevation_ft: float) -> USDAZoneData:
        """Adjust USDA zone based on elevation."""
        
        # Calculate temperature adjustment
        temp_adjustment = (elevation_ft / 1000) * self.elevation_temp_lapse
        
        # Adjust zone based on temperature change
        adjusted_zone_id = self._adjust_zone_id_for_temperature(base_zone.zone, temp_adjustment)
        adjusted_temp_range = (
            base_zone.temperature_range[0] + temp_adjustment,
            base_zone.temperature_range[1] + temp_adjustment
        )
        
        return USDAZoneData(
            zone=adjusted_zone_id,
            temperature_range=adjusted_temp_range,
            description=f"{base_zone.description} (Elevation Adjusted)",
            coordinates=base_zone.coordinates,
            confidence=base_zone.confidence * 0.9,  # Slightly lower confidence
            source=f"{base_zone.source}_elevation_adjusted"
        )
    
    def _adjust_zone_id_for_temperature(self, base_zone_id: str, temp_change: float) -> str:
        """Adjust zone ID based on temperature change."""
        
        # Each zone represents about 5°F difference
        zone_steps = int(temp_change / 5)
        
        if zone_steps == 0:
            return base_zone_id
        
        # Parse current zone
        try:
            zone_num = int(base_zone_id[0])
            zone_letter = base_zone_id[1]
            
            # Adjust zone number
            if zone_steps < 0:  # Colder (higher zone number)
                new_zone_num = min(13, zone_num - zone_steps)
            else:  # Warmer (lower zone number)
                new_zone_num = max(1, zone_num - zone_steps)
            
            return f"{new_zone_num}{zone_letter}"
            
        except (ValueError, IndexError):
            return base_zone_id  # Return original if parsing fails
    
    def _is_coastal_location(self, latitude: float, longitude: float) -> bool:
        """Determine if location is coastal (simplified)."""
        
        # Simplified coastal detection
        # In production, this would use detailed coastline data
        
        # North American coasts
        if -170 < longitude < -50 and 20 < latitude < 70:
            # Pacific coast
            if longitude < -120:
                return True
            # Atlantic coast
            elif longitude > -85:
                return True
            # Gulf coast
            elif latitude < 32 and longitude > -100:
                return True
        
        return False
    
    def _apply_coastal_moderation(
        self,
        zone_data: USDAZoneData,
        latitude: float,
        longitude: float
    ) -> USDAZoneData:
        """Apply coastal temperature moderation."""
        
        # Coastal areas have more moderate temperatures
        moderated_temp_range = (
            zone_data.temperature_range[0] + self.coastal_moderation,
            zone_data.temperature_range[1] - self.coastal_moderation
        )
        
        # This might shift the zone slightly warmer
        moderated_zone_id = self._get_zone_for_temperature_range(moderated_temp_range)
        
        return USDAZoneData(
            zone=moderated_zone_id,
            temperature_range=moderated_temp_range,
            description=f"{zone_data.description} (Coastal Moderated)",
            coordinates=zone_data.coordinates,
            confidence=zone_data.confidence,
            source=f"{zone_data.source}_coastal_moderated"
        )
    
    def _get_zone_for_temperature_range(self, temp_range: Tuple[float, float]) -> str:
        """Get USDA zone ID for temperature range."""
        
        avg_min_temp = temp_range[0]
        
        if avg_min_temp >= 65:
            return "13a"
        elif avg_min_temp >= 60:
            return "12a"
        elif avg_min_temp >= 55:
            return "11a"
        elif avg_min_temp >= 50:
            return "10b"
        elif avg_min_temp >= 45:
            return "10a"
        elif avg_min_temp >= 40:
            return "9b"
        elif avg_min_temp >= 35:
            return "9a"
        elif avg_min_temp >= 30:
            return "8b"
        elif avg_min_temp >= 25:
            return "8a"
        elif avg_min_temp >= 20:
            return "7b"
        elif avg_min_temp >= 15:
            return "7a"
        elif avg_min_temp >= 10:
            return "6b"
        elif avg_min_temp >= 5:
            return "6a"
        elif avg_min_temp >= 0:
            return "5b"
        elif avg_min_temp >= -5:
            return "5a"
        elif avg_min_temp >= -10:
            return "4b"
        elif avg_min_temp >= -15:
            return "4a"
        elif avg_min_temp >= -20:
            return "3b"
        elif avg_min_temp >= -25:
            return "3a"
        elif avg_min_temp >= -30:
            return "2b"
        elif avg_min_temp >= -35:
            return "2a"
        elif avg_min_temp >= -40:
            return "1b"
        else:
            return "1a"
    
    def _apply_microclimate_adjustments(
        self,
        zone_data: USDAZoneData,
        latitude: float,
        longitude: float,
        elevation_ft: float
    ) -> USDAZoneData:
        """Apply microclimate adjustments."""
        
        # Identify microclimate factors
        microclimate_factors = self._identify_microclimate_factors(latitude, longitude, elevation_ft)
        
        # Apply adjustments based on factors
        temp_adjustment = 0
        confidence_adjustment = 1.0
        
        for factor in microclimate_factors:
            if factor == "urban_heat_island":
                temp_adjustment += 2.0  # Cities are warmer
            elif factor == "valley_cold_pool":
                temp_adjustment -= 3.0  # Valleys can be colder
            elif factor == "slope_aspect":
                temp_adjustment += 1.0  # South-facing slopes warmer
            elif factor == "water_body_proximity":
                confidence_adjustment *= 0.9  # More variable near water
        
        if abs(temp_adjustment) > 1.0:
            adjusted_temp_range = (
                zone_data.temperature_range[0] + temp_adjustment,
                zone_data.temperature_range[1] + temp_adjustment
            )
            adjusted_zone_id = self._get_zone_for_temperature_range(adjusted_temp_range)
            
            return USDAZoneData(
                zone=adjusted_zone_id,
                temperature_range=adjusted_temp_range,
                description=f"{zone_data.description} (Microclimate Adjusted)",
                coordinates=zone_data.coordinates,
                confidence=zone_data.confidence * confidence_adjustment,
                source=f"{zone_data.source}_microclimate_adjusted"
            )
        
        return zone_data
    
    def _identify_microclimate_factors(
        self,
        latitude: float,
        longitude: float,
        elevation_ft: float
    ) -> List[str]:
        """Identify microclimate factors affecting the location."""
        
        factors = []
        
        # Urban heat island (simplified detection)
        if self._is_likely_urban(latitude, longitude):
            factors.append("urban_heat_island")
        
        # Valley location (based on elevation patterns)
        if elevation_ft < 1000 and self._is_likely_valley(latitude, longitude):
            factors.append("valley_cold_pool")
        
        # High elevation
        if elevation_ft > 3000:
            factors.append("high_elevation_effects")
        
        # Slope aspect (simplified)
        if self._has_significant_slope(latitude, longitude):
            factors.append("slope_aspect")
        
        # Water body proximity
        if self._near_large_water_body(latitude, longitude):
            factors.append("water_body_proximity")
        
        return factors
    
    def _is_likely_urban(self, latitude: float, longitude: float) -> bool:
        """Determine if location is likely urban (simplified)."""
        
        # Major US cities (simplified detection)
        urban_centers = [
            (40.7128, -74.0060),  # New York
            (34.0522, -118.2437), # Los Angeles
            (41.8781, -87.6298),  # Chicago
            (29.7604, -95.3698),  # Houston
            (33.4484, -112.0740), # Phoenix
        ]
        
        for city_lat, city_lon in urban_centers:
            distance = math.sqrt((latitude - city_lat)**2 + (longitude - city_lon)**2)
            if distance < 0.5:  # Within ~50km
                return True
        
        return False
    
    def _is_likely_valley(self, latitude: float, longitude: float) -> bool:
        """Determine if location is likely in a valley (simplified)."""
        
        # Known valley regions (simplified)
        # Central Valley, California
        if -122 < longitude < -119 and 35 < latitude < 40:
            return True
        
        # Mississippi River Valley
        if -95 < longitude < -89 and 30 < latitude < 45:
            return True
        
        return False
    
    def _has_significant_slope(self, latitude: float, longitude: float) -> bool:
        """Determine if location has significant slope (simplified)."""
        
        # Mountain regions likely have slopes
        # Rocky Mountains
        if -115 < longitude < -105 and 35 < latitude < 50:
            return True
        
        # Appalachian Mountains
        if -85 < longitude < -75 and 35 < latitude < 45:
            return True
        
        return False
    
    def _near_large_water_body(self, latitude: float, longitude: float) -> bool:
        """Determine if location is near large water body (simplified)."""
        
        # Great Lakes region
        if -90 < longitude < -75 and 40 < latitude < 50:
            return True
        
        # Coastal areas
        if self._is_coastal_location(latitude, longitude):
            return True
        
        return False
    
    async def _perform_koppen_analysis(
        self,
        latitude: float,
        longitude: float,
        elevation_ft: float
    ) -> Optional[ClimateAnalysis]:
        """Perform Köppen climate analysis."""
        
        try:
            return await self.koppen_service.classify_climate(latitude, longitude)
        except Exception as e:
            logger.warning(f"Köppen analysis failed for {latitude}, {longitude}: {str(e)}")
            return None
    
    def _calculate_climate_adjustments(
        self,
        latitude: float,
        longitude: float,
        elevation_ft: float,
        usda_zone: Optional[USDAZoneData]
    ) -> Dict:
        """Calculate climate adjustments applied."""
        
        adjustments = {
            "elevation_adjustment_f": 0,
            "coastal_moderation_f": 0,
            "microclimate_adjustment_f": 0,
            "total_adjustment_f": 0
        }
        
        if elevation_ft > self.elevation_significance:
            adjustments["elevation_adjustment_f"] = (elevation_ft / 1000) * self.elevation_temp_lapse
        
        if self._is_coastal_location(latitude, longitude):
            adjustments["coastal_moderation_f"] = self.coastal_moderation
        
        # Calculate total adjustment
        adjustments["total_adjustment_f"] = (
            adjustments["elevation_adjustment_f"] + 
            adjustments["coastal_moderation_f"] + 
            adjustments["microclimate_adjustment_f"]
        )
        
        return adjustments
    
    def _assess_confidence_factors(
        self,
        latitude: float,
        longitude: float,
        usda_zone: Optional[USDAZoneData],
        koppen_analysis: Optional[ClimateAnalysis],
        elevation_data: Optional[ElevationData]
    ) -> Dict:
        """Assess confidence factors for climate detection."""
        
        factors = {
            "overall_confidence": 0.7,
            "usda_zone_confidence": usda_zone.confidence if usda_zone else 0.3,
            "koppen_confidence": koppen_analysis.confidence if koppen_analysis else 0.5,
            "elevation_confidence": 0.8 if elevation_data and elevation_data.source != "estimated" else 0.5,
            "boundary_proximity_impact": 0,
            "data_source_quality": 0.7
        }
        
        # Assess boundary proximity impact
        boundary_proximity = self._assess_boundary_proximity(latitude, longitude)
        if boundary_proximity["near_zone_boundary"]:
            factors["boundary_proximity_impact"] = -0.1
        
        # Calculate overall confidence
        factors["overall_confidence"] = min(1.0, max(0.1, 
            (factors["usda_zone_confidence"] + 
             factors["koppen_confidence"] + 
             factors["elevation_confidence"]) / 3 + 
            factors["boundary_proximity_impact"]
        ))
        
        return factors
    
    def _assess_boundary_proximity(self, latitude: float, longitude: float) -> Dict:
        """Assess proximity to climate zone boundaries."""
        
        # Simplified boundary detection
        # In production, this would use detailed zone boundary data
        
        return {
            "near_zone_boundary": False,
            "boundary_distance_km": None,
            "boundary_uncertainty": 0.0,
            "note": "Boundary detection not implemented in simplified version"
        }
    
    def _get_detection_methods_used(
        self,
        usda_zone: Optional[USDAZoneData],
        koppen_analysis: Optional[ClimateAnalysis]
    ) -> List[str]:
        """Get list of detection methods used."""
        
        methods = ["coordinate_based_estimation"]
        
        if usda_zone and usda_zone.source != "coordinate_estimation":
            methods.append("usda_api_lookup")
        
        if koppen_analysis:
            methods.append("koppen_classification")
        
        methods.append("elevation_adjustment")
        methods.append("microclimate_analysis")
        
        return methods
    
    def _get_data_sources_used(
        self,
        usda_zone: Optional[USDAZoneData],
        koppen_analysis: Optional[ClimateAnalysis]
    ) -> List[str]:
        """Get list of data sources used."""
        
        sources = []
        
        if usda_zone:
            sources.append(usda_zone.source)
        
        if koppen_analysis:
            sources.append("koppen_climate_database")
        
        sources.extend(["elevation_estimation", "geographic_analysis"])
        
        return sources
    
    def _get_fallback_usda_zone(self, latitude: float, longitude: float) -> USDAZoneData:
        """Get fallback USDA zone when detection fails."""
        
        return USDAZoneData(
            zone="6a",
            temperature_range=(-10, -5),
            description="USDA Hardiness Zone 6a (Fallback)",
            coordinates=(latitude, longitude),
            confidence=0.3,
            source="fallback"
        )
    
    def _get_fallback_climate_data(
        self,
        latitude: float,
        longitude: float
    ) -> CoordinateClimateData:
        """Get fallback climate data when detection fails."""
        
        fallback_usda = self._get_fallback_usda_zone(latitude, longitude)
        
        return CoordinateClimateData(
            coordinates=(latitude, longitude),
            usda_zone=fallback_usda,
            koppen_analysis=None,
            elevation_data=None,
            climate_adjustments={"note": "fallback_data"},
            confidence_factors={"overall_confidence": 0.3},
            detection_metadata={
                "detection_time": datetime.utcnow().isoformat(),
                "methods_used": ["fallback"],
                "data_sources": ["fallback"],
                "note": "Fallback data due to detection failure"
            }
        )


# Global detector instance
coordinate_climate_detector = CoordinateClimateDetector()