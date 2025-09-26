"""
Cover Crop Timing Service

Comprehensive service for calculating optimal planting and termination timing
for cover crops based on climate, soil, and management factors.
"""

import logging
import httpx
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import date, datetime, timedelta
from dataclasses import dataclass
import math

try:
    from models.cover_crop_models import (
        TimingRecommendationRequest,
        TimingRecommendationResponse,
        PlantingTimingWindow,
        TerminationTimingWindow,
        SeasonalTimingStrategy,
        TimingFactorType,
        TerminationMethod,
        TimingRecommendationConfidence,
        GrowingSeason,
        SoilBenefit,
        CoverCropSpecies
    )
except ImportError:
    from models.cover_crop_models import (
        TimingRecommendationRequest,
        TimingRecommendationResponse,
        PlantingTimingWindow,
        TerminationTimingWindow,
        SeasonalTimingStrategy,
        TimingFactorType,
        TerminationMethod,
        TimingRecommendationConfidence,
        GrowingSeason,
        SoilBenefit,
        CoverCropSpecies
    )

logger = logging.getLogger(__name__)


@dataclass
class ClimateTimingData:
    """Climate data for timing calculations."""
    average_first_frost: Optional[date] = None
    average_last_frost: Optional[date] = None
    growing_degree_days: Dict[str, float] = None
    average_soil_temp_by_month: Dict[int, float] = None
    precipitation_patterns: Dict[int, float] = None
    temperature_ranges: Dict[int, Tuple[float, float]] = None
    
    def __post_init__(self):
        if self.growing_degree_days is None:
            self.growing_degree_days = {}
        if self.average_soil_temp_by_month is None:
            self.average_soil_temp_by_month = {}
        if self.precipitation_patterns is None:
            self.precipitation_patterns = {}
        if self.temperature_ranges is None:
            self.temperature_ranges = {}


class CoverCropTimingService:
    """Service for calculating optimal cover crop planting and termination timing."""
    
    def __init__(self):
        """Initialize the timing service."""
        self.climate_service_url = "http://localhost:8003"
        self.initialized = False
        
        # Species timing database - will be populated during initialization
        self.species_timing_data = {}
        
        # Default timing constraints by species type
        self.default_timing_constraints = {
            "legume": {
                "min_soil_temp_f": 50,
                "optimal_soil_temp_f": 60,
                "days_to_establishment": 14,
                "minimum_growing_days": 45,
                "optimal_growing_days": 90,
                "frost_tolerance": "moderate"
            },
            "grass": {
                "min_soil_temp_f": 45,
                "optimal_soil_temp_f": 55,
                "days_to_establishment": 10,
                "minimum_growing_days": 30,
                "optimal_growing_days": 75,
                "frost_tolerance": "high"
            },
            "brassica": {
                "min_soil_temp_f": 40,
                "optimal_soil_temp_f": 50,
                "days_to_establishment": 7,
                "minimum_growing_days": 30,
                "optimal_growing_days": 60,
                "frost_tolerance": "high"
            },
            "forb": {
                "min_soil_temp_f": 55,
                "optimal_soil_temp_f": 65,
                "days_to_establishment": 14,
                "minimum_growing_days": 45,
                "optimal_growing_days": 75,
                "frost_tolerance": "low"
            }
        }
        
    async def initialize(self):
        """Initialize the timing service with species-specific timing data."""
        try:
            await self._load_species_timing_data()
            self.initialized = True
            logger.info("Cover Crop Timing Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Cover Crop Timing Service: {e}")
            raise
            
    async def _load_species_timing_data(self):
        """Load species-specific timing data."""
        # This would typically load from a database or configuration
        # For now, we'll define timing data for our 18 species
        
        self.species_timing_data = {
            # Legumes
            "crimson_clover": {
                "species_type": "legume",
                "planting_seasons": [GrowingSeason.FALL, GrowingSeason.SPRING],
                "optimal_planting_months": {"fall": [9, 10], "spring": [3, 4]},
                "frost_tolerance": "moderate",
                "min_soil_temp_f": 50,
                "days_to_establishment": 14,
                "minimum_growing_days": 60,
                "optimal_growing_days": 120,
                "termination_methods": [
                    TerminationMethod.HERBICIDE,
                    TerminationMethod.MOWING,
                    TerminationMethod.MECHANICAL_TILLAGE
                ],
                "winter_hardy": True,
                "seed_production_risk": "medium"
            },
            
            "red_clover": {
                "species_type": "legume",
                "planting_seasons": [GrowingSeason.SPRING, GrowingSeason.FALL],
                "optimal_planting_months": {"spring": [3, 4, 5], "fall": [8, 9]},
                "frost_tolerance": "high",
                "min_soil_temp_f": 45,
                "days_to_establishment": 21,
                "minimum_growing_days": 75,
                "optimal_growing_days": 150,
                "termination_methods": [
                    TerminationMethod.HERBICIDE,
                    TerminationMethod.MOWING,
                    TerminationMethod.MECHANICAL_TILLAGE
                ],
                "winter_hardy": True,
                "seed_production_risk": "high"
            },
            
            "white_clover": {
                "species_type": "legume",
                "planting_seasons": [GrowingSeason.SPRING, GrowingSeason.FALL],
                "optimal_planting_months": {"spring": [3, 4, 5], "fall": [8, 9, 10]},
                "frost_tolerance": "high",
                "min_soil_temp_f": 45,
                "days_to_establishment": 21,
                "minimum_growing_days": 60,
                "optimal_growing_days": 120,
                "termination_methods": [
                    TerminationMethod.HERBICIDE,
                    TerminationMethod.MOWING,
                    TerminationMethod.GRAZING
                ],
                "winter_hardy": True,
                "seed_production_risk": "high"
            },
            
            "austrian_winter_pea": {
                "species_type": "legume",
                "planting_seasons": [GrowingSeason.FALL],
                "optimal_planting_months": {"fall": [9, 10, 11]},
                "frost_tolerance": "high",
                "min_soil_temp_f": 40,
                "days_to_establishment": 14,
                "minimum_growing_days": 90,
                "optimal_growing_days": 180,
                "termination_methods": [
                    TerminationMethod.HERBICIDE,
                    TerminationMethod.ROLLING_CRIMPING,
                    TerminationMethod.MECHANICAL_TILLAGE
                ],
                "winter_hardy": True,
                "seed_production_risk": "medium"
            },
            
            "hairy_vetch": {
                "species_type": "legume",
                "planting_seasons": [GrowingSeason.FALL, GrowingSeason.SPRING],
                "optimal_planting_months": {"fall": [8, 9, 10], "spring": [3, 4]},
                "frost_tolerance": "high",
                "min_soil_temp_f": 40,
                "days_to_establishment": 21,
                "minimum_growing_days": 90,
                "optimal_growing_days": 210,
                "termination_methods": [
                    TerminationMethod.HERBICIDE,
                    TerminationMethod.ROLLING_CRIMPING,
                    TerminationMethod.MOWING
                ],
                "winter_hardy": True,
                "seed_production_risk": "high"
            },
            
            "cowpea": {
                "species_type": "legume",
                "planting_seasons": [GrowingSeason.SUMMER],
                "optimal_planting_months": {"summer": [5, 6, 7]},
                "frost_tolerance": "low",
                "min_soil_temp_f": 65,
                "days_to_establishment": 10,
                "minimum_growing_days": 60,
                "optimal_growing_days": 90,
                "termination_methods": [
                    TerminationMethod.HERBICIDE,
                    TerminationMethod.MOWING,
                    TerminationMethod.WINTER_KILL
                ],
                "winter_hardy": False,
                "seed_production_risk": "medium"
            },
            
            "berseem_clover": {
                "species_type": "legume",
                "planting_seasons": [GrowingSeason.FALL, GrowingSeason.SPRING],
                "optimal_planting_months": {"fall": [9, 10], "spring": [3, 4]},
                "frost_tolerance": "moderate",
                "min_soil_temp_f": 50,
                "days_to_establishment": 14,
                "minimum_growing_days": 60,
                "optimal_growing_days": 120,
                "termination_methods": [
                    TerminationMethod.HERBICIDE,
                    TerminationMethod.MOWING,
                    TerminationMethod.WINTER_KILL
                ],
                "winter_hardy": False,
                "seed_production_risk": "low"
            },
            
            # Grasses
            "winter_rye": {
                "species_type": "grass",
                "planting_seasons": [GrowingSeason.FALL],
                "optimal_planting_months": {"fall": [9, 10, 11]},
                "frost_tolerance": "high",
                "min_soil_temp_f": 35,
                "days_to_establishment": 7,
                "minimum_growing_days": 45,
                "optimal_growing_days": 180,
                "termination_methods": [
                    TerminationMethod.HERBICIDE,
                    TerminationMethod.ROLLING_CRIMPING,
                    TerminationMethod.MOWING
                ],
                "winter_hardy": True,
                "seed_production_risk": "high"
            },
            
            "winter_wheat": {
                "species_type": "grass",
                "planting_seasons": [GrowingSeason.FALL],
                "optimal_planting_months": {"fall": [9, 10, 11]},
                "frost_tolerance": "high",
                "min_soil_temp_f": 40,
                "days_to_establishment": 10,
                "minimum_growing_days": 60,
                "optimal_growing_days": 210,
                "termination_methods": [
                    TerminationMethod.HERBICIDE,
                    TerminationMethod.ROLLING_CRIMPING,
                    TerminationMethod.MECHANICAL_TILLAGE
                ],
                "winter_hardy": True,
                "seed_production_risk": "high"
            },
            
            "oats": {
                "species_type": "grass",
                "planting_seasons": [GrowingSeason.SPRING, GrowingSeason.FALL],
                "optimal_planting_months": {"spring": [3, 4, 5], "fall": [8, 9]},
                "frost_tolerance": "moderate",
                "min_soil_temp_f": 40,
                "days_to_establishment": 7,
                "minimum_growing_days": 45,
                "optimal_growing_days": 90,
                "termination_methods": [
                    TerminationMethod.HERBICIDE,
                    TerminationMethod.MOWING,
                    TerminationMethod.WINTER_KILL
                ],
                "winter_hardy": False,
                "seed_production_risk": "medium"
            },
            
            "annual_ryegrass": {
                "species_type": "grass",
                "planting_seasons": [GrowingSeason.FALL, GrowingSeason.SPRING],
                "optimal_planting_months": {"fall": [8, 9, 10], "spring": [3, 4]},
                "frost_tolerance": "moderate",
                "min_soil_temp_f": 45,
                "days_to_establishment": 7,
                "minimum_growing_days": 60,
                "optimal_growing_days": 150,
                "termination_methods": [
                    TerminationMethod.HERBICIDE,
                    TerminationMethod.MOWING,
                    TerminationMethod.GRAZING
                ],
                "winter_hardy": True,
                "seed_production_risk": "high"
            },
            
            "sorghum_sudan": {
                "species_type": "grass",
                "planting_seasons": [GrowingSeason.SUMMER],
                "optimal_planting_months": {"summer": [5, 6, 7]},
                "frost_tolerance": "low",
                "min_soil_temp_f": 65,
                "days_to_establishment": 7,
                "minimum_growing_days": 45,
                "optimal_growing_days": 90,
                "termination_methods": [
                    TerminationMethod.HERBICIDE,
                    TerminationMethod.MOWING,
                    TerminationMethod.WINTER_KILL
                ],
                "winter_hardy": False,
                "seed_production_risk": "medium"
            },
            
            # Brassicas
            "radish_tillage": {
                "species_type": "brassica",
                "planting_seasons": [GrowingSeason.FALL, GrowingSeason.SUMMER],
                "optimal_planting_months": {"fall": [8, 9], "summer": [7, 8]},
                "frost_tolerance": "high",
                "min_soil_temp_f": 40,
                "days_to_establishment": 5,
                "minimum_growing_days": 45,
                "optimal_growing_days": 75,
                "termination_methods": [
                    TerminationMethod.WINTER_KILL,
                    TerminationMethod.HERBICIDE,
                    TerminationMethod.MOWING
                ],
                "winter_hardy": False,
                "seed_production_risk": "low"
            },
            
            "turnip": {
                "species_type": "brassica",
                "planting_seasons": [GrowingSeason.FALL, GrowingSeason.SUMMER],
                "optimal_planting_months": {"fall": [8, 9], "summer": [7, 8]},
                "frost_tolerance": "high",
                "min_soil_temp_f": 40,
                "days_to_establishment": 7,
                "minimum_growing_days": 45,
                "optimal_growing_days": 90,
                "termination_methods": [
                    TerminationMethod.WINTER_KILL,
                    TerminationMethod.HERBICIDE,
                    TerminationMethod.GRAZING
                ],
                "winter_hardy": False,
                "seed_production_risk": "low"
            },
            
            "mustard": {
                "species_type": "brassica",
                "planting_seasons": [GrowingSeason.FALL, GrowingSeason.SPRING],
                "optimal_planting_months": {"fall": [8, 9], "spring": [3, 4]},
                "frost_tolerance": "moderate",
                "min_soil_temp_f": 45,
                "days_to_establishment": 5,
                "minimum_growing_days": 45,
                "optimal_growing_days": 75,
                "termination_methods": [
                    TerminationMethod.HERBICIDE,
                    TerminationMethod.MOWING,
                    TerminationMethod.INCORPORATION
                ],
                "winter_hardy": False,
                "seed_production_risk": "high"
            },
            
            # Forbs
            "sunflower": {
                "species_type": "forb",
                "planting_seasons": [GrowingSeason.SUMMER],
                "optimal_planting_months": {"summer": [5, 6, 7]},
                "frost_tolerance": "low",
                "min_soil_temp_f": 60,
                "days_to_establishment": 10,
                "minimum_growing_days": 60,
                "optimal_growing_days": 90,
                "termination_methods": [
                    TerminationMethod.HERBICIDE,
                    TerminationMethod.MOWING,
                    TerminationMethod.WINTER_KILL
                ],
                "winter_hardy": False,
                "seed_production_risk": "high"
            },
            
            "buckwheat": {
                "species_type": "forb",
                "planting_seasons": [GrowingSeason.SUMMER, GrowingSeason.SPRING],
                "optimal_planting_months": {"summer": [6, 7, 8], "spring": [4, 5]},
                "frost_tolerance": "low",
                "min_soil_temp_f": 55,
                "days_to_establishment": 7,
                "minimum_growing_days": 40,
                "optimal_growing_days": 75,
                "termination_methods": [
                    TerminationMethod.HERBICIDE,
                    TerminationMethod.MOWING,
                    TerminationMethod.WINTER_KILL
                ],
                "winter_hardy": False,
                "seed_production_risk": "high"
            },
            
            "phacelia": {
                "species_type": "forb",
                "planting_seasons": [GrowingSeason.SPRING, GrowingSeason.FALL],
                "optimal_planting_months": {"spring": [3, 4, 5], "fall": [8, 9]},
                "frost_tolerance": "moderate",
                "min_soil_temp_f": 50,
                "days_to_establishment": 10,
                "minimum_growing_days": 60,
                "optimal_growing_days": 90,
                "termination_methods": [
                    TerminationMethod.HERBICIDE,
                    TerminationMethod.MOWING,
                    TerminationMethod.WINTER_KILL
                ],
                "winter_hardy": False,
                "seed_production_risk": "medium"
            }
        }
        
        logger.info(f"Loaded timing data for {len(self.species_timing_data)} cover crop species")
    
    async def get_climate_data(self, location) -> ClimateTimingData:
        """Retrieve climate data for timing calculations."""
        try:
            # Handle both Location objects and dictionaries
            if hasattr(location, 'latitude'):
                # Location object
                lat, lon = location.latitude, location.longitude
            else:
                # Dictionary
                lat, lon = location.get("latitude"), location.get("longitude")
                
            climate_data = ClimateTimingData()
            
            # Try to get data from climate service
            async with httpx.AsyncClient(timeout=10.0) as client:
                try:
                    # Get climate zone data
                    zone_response = await client.post(
                        f"{self.climate_service_url}/api/climate/detect-zone",
                        json={"latitude": lat, "longitude": lon}
                    )
                    
                    if zone_response.status_code == 200:
                        zone_data = zone_response.json()
                        climate_zone = zone_data.get("climate_zone")
                        
                        # Use climate zone to estimate timing data
                        climate_data = self._estimate_climate_timing_from_zone(climate_zone, location)
                    
                except Exception as e:
                    logger.warning(f"Could not retrieve climate data from service: {e}")
                    # Fall back to location-based estimates
                    climate_data = self._estimate_climate_timing_from_location(location)
                    
            return climate_data
            
        except Exception as e:
            logger.error(f"Error retrieving climate data: {e}")
            # Return default climate data based on location
            return self._estimate_climate_timing_from_location(location)
    
    def _estimate_climate_timing_from_zone(self, climate_zone: str, location) -> ClimateTimingData:
        """Estimate climate timing data from climate zone."""
        # Handle both Location objects and dictionaries
        if hasattr(location, 'latitude'):
            latitude = location.latitude
        else:
            latitude = location.get("latitude", 40.0)
        
        # Base climate data on zone and latitude
        climate_data = ClimateTimingData()
        
        # Estimate frost dates based on climate zone and latitude
        if climate_zone and "zone" in climate_zone.lower():
            try:
                zone_num = int(''.join(filter(str.isdigit, climate_zone)))
                # Estimate based on USDA hardiness zones
                base_last_frost = self._estimate_last_frost_by_zone(zone_num)
                base_first_frost = self._estimate_first_frost_by_zone(zone_num)
                
                climate_data.average_last_frost = base_last_frost
                climate_data.average_first_frost = base_first_frost
                
            except ValueError:
                climate_data = self._estimate_climate_timing_from_location(location)
        else:
            climate_data = self._estimate_climate_timing_from_location(location)
            
        # Estimate soil temperatures by month
        climate_data.average_soil_temp_by_month = self._estimate_soil_temperatures(latitude)
        
        return climate_data
    
    def _estimate_climate_timing_from_location(self, location) -> ClimateTimingData:
        """Estimate climate timing data from location."""
        # Handle both Location objects and dictionaries
        if hasattr(location, 'latitude'):
            latitude = location.latitude
        else:
            latitude = location.get("latitude", 40.0)
        
        climate_data = ClimateTimingData()
        
        # Rough estimates based on latitude
        if latitude > 45:  # Northern regions
            climate_data.average_last_frost = date(2024, 5, 15)
            climate_data.average_first_frost = date(2024, 9, 15)
        elif latitude > 35:  # Temperate regions
            climate_data.average_last_frost = date(2024, 4, 15)
            climate_data.average_first_frost = date(2024, 10, 15)
        else:  # Southern regions
            climate_data.average_last_frost = date(2024, 3, 15)
            climate_data.average_first_frost = date(2024, 11, 15)
            
        # Estimate soil temperatures
        climate_data.average_soil_temp_by_month = self._estimate_soil_temperatures(latitude)
        
        return climate_data
    
    def _estimate_last_frost_by_zone(self, zone: int) -> date:
        """Estimate last frost date by USDA hardiness zone."""
        frost_dates = {
            3: date(2024, 5, 30),
            4: date(2024, 5, 15),
            5: date(2024, 4, 30),
            6: date(2024, 4, 15),
            7: date(2024, 4, 1),
            8: date(2024, 3, 15),
            9: date(2024, 3, 1),
            10: date(2024, 2, 15),
            11: date(2024, 2, 1)
        }
        return frost_dates.get(zone, date(2024, 4, 15))
    
    def _estimate_first_frost_by_zone(self, zone: int) -> date:
        """Estimate first frost date by USDA hardiness zone."""
        frost_dates = {
            3: date(2024, 9, 1),
            4: date(2024, 9, 15),
            5: date(2024, 10, 1),
            6: date(2024, 10, 15),
            7: date(2024, 11, 1),
            8: date(2024, 11, 15),
            9: date(2024, 12, 1),
            10: date(2024, 12, 15),
            11: date(2025, 1, 1)
        }
        return frost_dates.get(zone, date(2024, 10, 15))
    
    def _estimate_soil_temperatures(self, latitude: float) -> Dict[int, float]:
        """Estimate average soil temperatures by month based on latitude."""
        # Base temperatures for temperate climate (40°N)
        base_temps = {
            1: 35, 2: 38, 3: 45, 4: 55, 5: 65, 6: 75,
            7: 80, 8: 78, 9: 70, 10: 60, 11: 50, 12: 40
        }
        
        # Adjust for latitude
        adjustment = (latitude - 40) * -1.5  # Cooler as you go north
        
        return {month: temp + adjustment for month, temp in base_temps.items()}
    
    async def calculate_planting_window(
        self, 
        species_id: str, 
        location: Dict[str, Any],
        main_crop_schedule: Optional[Dict[str, Any]] = None,
        target_season: Optional[GrowingSeason] = None
    ) -> PlantingTimingWindow:
        """Calculate optimal planting timing window for a species."""
        
        if species_id not in self.species_timing_data:
            raise ValueError(f"Species {species_id} not found in timing database")
            
        species_data = self.species_timing_data[species_id]
        climate_data = await self.get_climate_data(location)
        
        # Determine target season
        if target_season is None:
            target_season = species_data["planting_seasons"][0]  # Default to first available season
            
        # Calculate planting window based on season and climate
        planting_window = self._calculate_seasonal_planting_window(
            species_data, climate_data, target_season, location
        )
        
        # Apply main crop constraints if provided
        if main_crop_schedule:
            planting_window = self._apply_main_crop_constraints(
                planting_window, main_crop_schedule, species_data
            )
            
        return planting_window
    
    def _calculate_seasonal_planting_window(
        self, 
        species_data: Dict[str, Any],
        climate_data: ClimateTimingData,
        target_season: GrowingSeason,
        location: Dict[str, Any]
    ) -> PlantingTimingWindow:
        """Calculate planting window for specific season."""
        
        current_year = datetime.now().year
        season_key = target_season.value
        
        # Get optimal months for this season
        optimal_months = species_data["optimal_planting_months"].get(season_key, [])
        if not optimal_months:
            raise ValueError(f"Species {species_data} not suitable for {target_season} planting")
            
        # Calculate dates based on optimal months
        optimal_start_month = optimal_months[0]
        optimal_end_month = optimal_months[-1]
        
        # Adjust for climate constraints
        min_soil_temp = species_data["min_soil_temp_f"]
        frost_tolerance = species_data["frost_tolerance"]
        
        # Calculate optimal planting window
        optimal_start = self._calculate_date_from_constraints(
            current_year, optimal_start_month, 1, climate_data, min_soil_temp, frost_tolerance
        )
        
        optimal_end = self._calculate_date_from_constraints(
            current_year, optimal_end_month, 28, climate_data, min_soil_temp, frost_tolerance
        )
        
        # Calculate acceptable range (extend window by 2 weeks each direction)
        acceptable_early = optimal_start - timedelta(days=14)
        acceptable_late = optimal_end + timedelta(days=14)
        
        # Apply climate-based limitations
        if climate_data.average_last_frost and target_season in [GrowingSeason.SPRING]:
            if frost_tolerance != "high":
                optimal_start = max(optimal_start, climate_data.average_last_frost + timedelta(days=7))
                
        if climate_data.average_first_frost and target_season in [GrowingSeason.FALL]:
            # Only apply frost constraints for non-winter-hardy species
            if not species_data.get("winter_hardy", False):
                # Ensure enough growing time before frost for non-winter-hardy crops
                min_growing_days = species_data["minimum_growing_days"]
                latest_plant_for_growth = climate_data.average_first_frost - timedelta(days=min_growing_days)
                optimal_end = min(optimal_end, latest_plant_for_growth)
        
        # Determine limiting factors
        limiting_factors = []
        if min_soil_temp > 50:
            limiting_factors.append(TimingFactorType.SOIL_CONDITION)
        if frost_tolerance == "low":
            limiting_factors.append(TimingFactorType.CLIMATE)
        limiting_factors.append(TimingFactorType.SPECIES_CHARACTERISTIC)
        
        return PlantingTimingWindow(
            species_id=species_data.get("species_id", "unknown"),
            location=location,
            climate_zone=getattr(climate_data, 'climate_zone', None),
            optimal_planting_start=optimal_start,
            optimal_planting_end=optimal_end,
            acceptable_early_date=acceptable_early,
            acceptable_late_date=acceptable_late,
            primary_limiting_factors=limiting_factors,
            climate_constraints={
                "min_soil_temp_f": min_soil_temp,
                "frost_tolerance": frost_tolerance
            },
            soil_temperature_requirements={
                "minimum": min_soil_temp,
                "optimal": species_data.get("optimal_soil_temp_f", min_soil_temp + 10)
            },
            frost_considerations={
                "tolerance": frost_tolerance,
                "last_frost_date": climate_data.average_last_frost.isoformat() if climate_data.average_last_frost else None,
                "first_frost_date": climate_data.average_first_frost.isoformat() if climate_data.average_first_frost else None
            },
            days_to_establishment=species_data["days_to_establishment"],
            minimum_growing_days=species_data["minimum_growing_days"],
            optimal_growing_days=species_data["optimal_growing_days"],
            confidence_level=TimingRecommendationConfidence.MEDIUM,
            recommendation_notes=[
                f"Optimal for {target_season.value} planting",
                f"Requires minimum {min_soil_temp}°F soil temperature",
                f"Frost tolerance: {frost_tolerance}"
            ]
        )
    
    def _calculate_date_from_constraints(
        self, 
        year: int, 
        month: int, 
        day: int,
        climate_data: ClimateTimingData,
        min_soil_temp: float,
        frost_tolerance: str
    ) -> date:
        """Calculate actual date considering climate constraints."""
        
        base_date = date(year, month, day)
        
        # Check soil temperature constraints
        if climate_data.average_soil_temp_by_month:
            soil_temp = climate_data.average_soil_temp_by_month.get(month, min_soil_temp)
            if soil_temp < min_soil_temp:
                # Find next month with adequate temperature
                for next_month in range(month + 1, 13):
                    if climate_data.average_soil_temp_by_month.get(next_month, 0) >= min_soil_temp:
                        return date(year, next_month, 1)
                # If not found in current year, try next year
                return date(year + 1, 3, 1)  # Default to March next year
                
        return base_date
    
    def _apply_main_crop_constraints(
        self,
        planting_window: PlantingTimingWindow,
        main_crop_schedule: Dict[str, Any],
        species_data: Dict[str, Any]
    ) -> PlantingTimingWindow:
        """Apply main crop scheduling constraints to planting window."""
        
        # This would integrate with main crop planting/harvest schedules
        # For now, return the window unchanged
        # In a full implementation, this would adjust timing based on:
        # - Main crop harvest dates
        # - Pre-plant timing requirements
        # - Equipment availability
        # - Field preparation time
        
        return planting_window
    
    async def calculate_termination_windows(
        self,
        species_id: str,
        planting_date: date,
        location: Dict[str, Any],
        main_crop_schedule: Optional[Dict[str, Any]] = None,
        preferred_methods: Optional[List[TerminationMethod]] = None
    ) -> List[TerminationTimingWindow]:
        """Calculate termination timing windows for different methods."""
        
        if species_id not in self.species_timing_data:
            raise ValueError(f"Species {species_id} not found in timing database")
            
        species_data = self.species_timing_data[species_id]
        climate_data = await self.get_climate_data(location)
        
        # Get available termination methods
        available_methods = species_data["termination_methods"]
        if preferred_methods:
            methods_to_calculate = [m for m in preferred_methods if m in available_methods]
        else:
            methods_to_calculate = available_methods
            
        termination_windows = []
        
        for method in methods_to_calculate:
            window = self._calculate_method_specific_termination_window(
                species_data, method, planting_date, climate_data, location, main_crop_schedule
            )
            termination_windows.append(window)
            
        return termination_windows
    
    def _calculate_method_specific_termination_window(
        self,
        species_data: Dict[str, Any],
        method: TerminationMethod,
        planting_date: date,
        climate_data: ClimateTimingData,
        location: Dict[str, Any],
        main_crop_schedule: Optional[Dict[str, Any]] = None
    ) -> TerminationTimingWindow:
        """Calculate termination window for specific method."""
        
        # Calculate minimum and optimal termination dates based on species growth
        min_growing_days = species_data["minimum_growing_days"]
        optimal_growing_days = species_data["optimal_growing_days"]
        
        min_termination_date = planting_date + timedelta(days=min_growing_days)
        optimal_termination_start = planting_date + timedelta(days=optimal_growing_days - 14)
        optimal_termination_end = planting_date + timedelta(days=optimal_growing_days + 14)
        
        # Method-specific adjustments
        weather_requirements = {}
        equipment_requirements = []
        timing_flexibility = 7
        
        if method == TerminationMethod.HERBICIDE:
            weather_requirements = {
                "wind_speed_max_mph": 10,
                "temperature_range_f": [40, 85],
                "no_rain_hours": 6
            }
            equipment_requirements = ["sprayer", "herbicide"]
            timing_flexibility = 14
            
        elif method == TerminationMethod.MECHANICAL_TILLAGE:
            weather_requirements = {
                "soil_moisture": "workable",
                "no_recent_rain_days": 2
            }
            equipment_requirements = ["tractor", "tillage_implement"]
            timing_flexibility = 7
            
        elif method == TerminationMethod.MOWING:
            weather_requirements = {
                "no_rain_hours": 4
            }
            equipment_requirements = ["mower"]
            timing_flexibility = 10
            
        elif method == TerminationMethod.ROLLING_CRIMPING:
            weather_requirements = {
                "growth_stage": "flowering_to_early_seed"
            }
            equipment_requirements = ["roller_crimper"]
            timing_flexibility = 5
            # Adjust timing for proper growth stage
            optimal_termination_start = planting_date + timedelta(days=max(60, optimal_growing_days - 21))
            optimal_termination_end = planting_date + timedelta(days=optimal_growing_days)
            
        elif method == TerminationMethod.WINTER_KILL:
            # Natural termination - no equipment needed
            if climate_data.average_first_frost:
                optimal_termination_start = climate_data.average_first_frost
                optimal_termination_end = climate_data.average_first_frost + timedelta(days=30)
            timing_flexibility = 0  # Nature determines timing
            
        elif method == TerminationMethod.GRAZING:
            weather_requirements = {
                "soil_conditions": "firm",
                "growth_stage": "vegetative_to_early_flower"
            }
            equipment_requirements = ["fencing", "water_system"]
            timing_flexibility = 21
            
        # Apply main crop schedule constraints
        latest_safe_termination = optimal_termination_end + timedelta(days=30)
        if main_crop_schedule and "planting_date" in main_crop_schedule:
            main_plant_date = datetime.strptime(main_crop_schedule["planting_date"], "%Y-%m-%d").date()
            # Ensure termination is completed 2-3 weeks before main crop planting
            required_clearance = 21
            latest_safe_termination = min(latest_safe_termination, main_plant_date - timedelta(days=required_clearance))
            
        # Growth stage and seed production considerations
        growth_stage_targets = []
        seed_production_risk = species_data.get("seed_production_risk", "medium")
        
        if method == TerminationMethod.ROLLING_CRIMPING:
            growth_stage_targets = ["flowering", "early_seed_set"]
        elif method == TerminationMethod.GRAZING:
            growth_stage_targets = ["vegetative", "early_flowering"]
        else:
            growth_stage_targets = ["any_stage"]
            
        return TerminationTimingWindow(
            species_id=species_data.get("species_id", "unknown"),
            termination_method=method,
            location=location,
            optimal_termination_start=optimal_termination_start,
            optimal_termination_end=optimal_termination_end,
            latest_safe_termination=latest_safe_termination,
            earliest_effective_termination=min_termination_date,
            weather_requirements=weather_requirements,
            equipment_requirements=equipment_requirements,
            timing_flexibility_days=timing_flexibility,
            growth_stage_targets=growth_stage_targets,
            seed_production_risk=seed_production_risk,
            regrowth_potential="low" if method in [TerminationMethod.HERBICIDE, TerminationMethod.MECHANICAL_TILLAGE] else "medium",
            pre_planting_clearance_days=21,
            residue_decomposition_time=30 if method == TerminationMethod.MECHANICAL_TILLAGE else 45,
            confidence_level=TimingRecommendationConfidence.MEDIUM,
            method_specific_notes=[
                f"Method: {method.value.replace('_', ' ').title()}",
                f"Flexibility: ±{timing_flexibility} days",
                f"Seed production risk: {seed_production_risk}"
            ]
        )
    
    async def generate_comprehensive_timing_recommendation(
        self,
        request: TimingRecommendationRequest
    ) -> TimingRecommendationResponse:
        """Generate comprehensive timing recommendations."""
        
        # Calculate planting window
        planting_window = await self.calculate_planting_window(
            request.species_id,
            request.location,
            request.main_crop_schedule
        )
        
        # Calculate termination windows
        termination_windows = await self.calculate_termination_windows(
            request.species_id,
            planting_window.optimal_planting_start,
            request.location,
            request.main_crop_schedule,
            request.preferred_termination_methods
        )
        
        # Create seasonal strategy
        seasonal_strategy = self._create_seasonal_strategy(
            request, planting_window, termination_windows
        )
        
        # Generate alternative strategies
        alternative_windows = await self._generate_alternative_planting_windows(
            request, planting_window
        )
        
        # Assess risks
        timing_risks = self._assess_timing_risks(
            request, planting_window, termination_windows
        )
        
        # Calculate success probabilities
        establishment_success = self._calculate_establishment_success_probability(
            request, planting_window
        )
        
        return TimingRecommendationResponse(
            request_id=f"timing_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            species_id=request.species_id,
            recommended_planting=planting_window,
            recommended_termination=termination_windows,
            seasonal_strategy=seasonal_strategy,
            alternative_planting_windows=alternative_windows,
            timing_risks=timing_risks,
            expected_establishment_success=establishment_success,
            overall_confidence=TimingRecommendationConfidence.MEDIUM,
            recommendation_summary=self._generate_recommendation_summary(
                request, planting_window, termination_windows
            )
        )
    
    def _create_seasonal_strategy(
        self,
        request: TimingRecommendationRequest,
        planting_window: PlantingTimingWindow,
        termination_windows: List[TerminationTimingWindow]
    ) -> SeasonalTimingStrategy:
        """Create seasonal timing strategy."""
        
        # Determine target season from planting window
        planting_month = planting_window.optimal_planting_start.month
        if planting_month in [3, 4, 5]:
            target_season = GrowingSeason.SPRING
        elif planting_month in [6, 7, 8]:
            target_season = GrowingSeason.SUMMER
        elif planting_month in [9, 10, 11]:
            target_season = GrowingSeason.FALL
        else:
            target_season = GrowingSeason.WINTER
            
        return SeasonalTimingStrategy(
            strategy_id=f"seasonal_{request.species_id}_{target_season.value}",
            target_season=target_season,
            species_recommendations=[request.species_id],
            planting_strategies=[planting_window],
            termination_strategies=termination_windows,
            success_probability=0.8,
            optimization_score=0.75
        )
    
    async def _generate_alternative_planting_windows(
        self,
        request: TimingRecommendationRequest,
        primary_window: PlantingTimingWindow
    ) -> List[PlantingTimingWindow]:
        """Generate alternative planting windows."""
        # For now, return empty list
        # In full implementation, would calculate alternative seasons/timing
        return []
    
    def _assess_timing_risks(
        self,
        request: TimingRecommendationRequest,
        planting_window: PlantingTimingWindow,
        termination_windows: List[TerminationTimingWindow]
    ) -> List[Dict[str, Any]]:
        """Assess timing-related risks."""
        
        risks = []
        
        # Weather risks
        if TimingFactorType.CLIMATE in planting_window.primary_limiting_factors:
            risks.append({
                "risk_type": "weather",
                "severity": "medium",
                "description": "Climate-sensitive timing window",
                "mitigation": "Monitor weather forecasts closely"
            })
            
        # Equipment risks
        for window in termination_windows:
            if window.equipment_requirements:
                risks.append({
                    "risk_type": "equipment",
                    "severity": "low",
                    "description": f"Requires {', '.join(window.equipment_requirements)}",
                    "mitigation": "Ensure equipment availability and maintenance"
                })
                
        return risks
    
    def _calculate_establishment_success_probability(
        self,
        request: TimingRecommendationRequest,
        planting_window: PlantingTimingWindow
    ) -> float:
        """Calculate probability of successful establishment."""
        
        base_probability = 0.8
        
        # Adjust based on timing factors
        if TimingFactorType.CLIMATE in planting_window.primary_limiting_factors:
            base_probability -= 0.1
            
        if planting_window.confidence_level == TimingRecommendationConfidence.HIGH:
            base_probability += 0.1
        elif planting_window.confidence_level == TimingRecommendationConfidence.LOW:
            base_probability -= 0.1
            
        return max(0.0, min(1.0, base_probability))
    
    def _generate_recommendation_summary(
        self,
        request: TimingRecommendationRequest,
        planting_window: PlantingTimingWindow,
        termination_windows: List[TerminationTimingWindow]
    ) -> str:
        """Generate executive summary of timing recommendations."""
        
        planting_start = planting_window.optimal_planting_start.strftime("%B %d")
        planting_end = planting_window.optimal_planting_end.strftime("%B %d")
        
        termination_methods = [w.termination_method.value.replace('_', ' ').title() 
                             for w in termination_windows[:2]]
        
        summary = f"Optimal planting window: {planting_start} - {planting_end}. "
        summary += f"Recommended termination methods: {', '.join(termination_methods)}. "
        summary += f"Minimum growing period: {planting_window.minimum_growing_days} days."
        
        return summary