"""
Köppen Climate Classification Service
Provides Köppen climate type detection and analysis.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import math

logger = logging.getLogger(__name__)


class KoppenGroup(Enum):
    """Köppen climate groups."""
    TROPICAL = "A"
    ARID = "B"
    TEMPERATE = "C"
    CONTINENTAL = "D"
    POLAR = "E"


@dataclass
class KoppenClimate:
    """Köppen climate classification data."""
    code: str
    group: KoppenGroup
    name: str
    description: str
    temperature_pattern: str
    precipitation_pattern: str
    agricultural_suitability: str
    typical_vegetation: List[str]
    growing_season_months: int
    water_balance: str


@dataclass
class ClimateAnalysis:
    """Climate analysis result."""
    koppen_type: KoppenClimate
    confidence: float
    temperature_data: Dict
    precipitation_data: Dict
    seasonal_patterns: Dict
    agricultural_implications: Dict


class KoppenClimateService:
    """Service for Köppen climate classification."""
    
    def __init__(self):
        self.climate_types = self._initialize_koppen_types()
        self.temperature_thresholds = self._initialize_temperature_thresholds()
        self.precipitation_thresholds = self._initialize_precipitation_thresholds()
    
    def _initialize_koppen_types(self) -> Dict[str, KoppenClimate]:
        """Initialize Köppen climate type definitions."""
        
        types = {}
        
        # Tropical climates (A)
        tropical_types = [
            ("Af", "Tropical Rainforest", "Hot and wet year-round", "hot_humid", "wet_year_round", 
             "excellent_tropical", ["rainforest", "tropical_crops"], 12, "surplus"),
            ("Am", "Tropical Monsoon", "Hot with distinct wet/dry seasons", "hot_humid", "monsoon", 
             "good_tropical", ["monsoon_forest", "rice", "tropical_fruits"], 10, "seasonal_surplus"),
            ("Aw", "Tropical Savanna", "Hot with dry winter", "hot_humid", "dry_winter", 
             "moderate_tropical", ["savanna", "grassland", "seasonal_crops"], 8, "seasonal_deficit"),
            ("As", "Tropical Savanna", "Hot with dry summer", "hot_humid", "dry_summer", 
             "moderate_tropical", ["savanna", "drought_tolerant_crops"], 8, "seasonal_deficit"),
        ]
        
        for code, name, desc, temp, precip, ag_suit, veg, season, water in tropical_types:
            types[code] = KoppenClimate(
                code=code, group=KoppenGroup.TROPICAL, name=name, description=desc,
                temperature_pattern=temp, precipitation_pattern=precip,
                agricultural_suitability=ag_suit, typical_vegetation=veg,
                growing_season_months=season, water_balance=water
            )
        
        # Arid climates (B)
        arid_types = [
            ("BWh", "Hot Desert", "Hot and arid year-round", "hot_arid", "very_dry", 
             "limited_irrigation", ["desert_scrub", "drought_crops"], 4, "severe_deficit"),
            ("BWk", "Cold Desert", "Cold and arid", "cold_arid", "very_dry", 
             "limited_grazing", ["desert_scrub", "hardy_grasses"], 3, "severe_deficit"),
            ("BSh", "Hot Semi-Arid", "Hot and semi-arid", "hot_semi_arid", "dry", 
             "drought_tolerant", ["grassland", "drought_crops"], 6, "deficit"),
            ("BSk", "Cold Semi-Arid", "Cold and semi-arid", "cold_semi_arid", "dry", 
             "drought_tolerant", ["grassland", "hardy_crops"], 5, "deficit"),
        ]
        
        for code, name, desc, temp, precip, ag_suit, veg, season, water in arid_types:
            types[code] = KoppenClimate(
                code=code, group=KoppenGroup.ARID, name=name, description=desc,
                temperature_pattern=temp, precipitation_pattern=precip,
                agricultural_suitability=ag_suit, typical_vegetation=veg,
                growing_season_months=season, water_balance=water
            )
        
        # Temperate climates (C)
        temperate_types = [
            ("Cfa", "Humid Subtropical", "Hot humid summers, mild winters", "hot_summer", "wet_year_round", 
             "excellent_diverse", ["deciduous_forest", "diverse_crops"], 8, "surplus"),
            ("Cfb", "Oceanic", "Mild temperatures, wet year-round", "warm_summer", "wet_year_round", 
             "good_temperate", ["temperate_forest", "cool_crops"], 7, "surplus"),
            ("Cfc", "Subpolar Oceanic", "Cool summers, mild winters", "cool_summer", "wet_year_round", 
             "limited_cool", ["coniferous_forest", "hardy_crops"], 5, "surplus"),
            ("Csa", "Mediterranean", "Hot dry summers, mild wet winters", "hot_summer", "dry_summer", 
             "excellent_mediterranean", ["mediterranean_scrub", "mediterranean_crops"], 7, "seasonal"),
            ("Csb", "Warm Mediterranean", "Warm dry summers, mild wet winters", "warm_summer", "dry_summer", 
             "good_mediterranean", ["mediterranean_forest", "mediterranean_crops"], 6, "seasonal"),
            ("Csc", "Cool Mediterranean", "Cool dry summers, mild wet winters", "cool_summer", "dry_summer", 
             "limited_mediterranean", ["mountain_forest", "cool_mediterranean"], 5, "seasonal"),
            ("Cwa", "Monsoon Subtropical", "Hot wet summers, dry winters", "hot_summer", "dry_winter", 
             "good_monsoon", ["mixed_forest", "monsoon_crops"], 7, "seasonal_surplus"),
            ("Cwb", "Subtropical Highland", "Mild wet summers, dry winters", "warm_summer", "dry_winter", 
             "moderate_highland", ["highland_forest", "highland_crops"], 6, "seasonal"),
            ("Cwc", "Cold Subtropical Highland", "Cool wet summers, dry winters", "cool_summer", "dry_winter", 
             "limited_highland", ["mountain_forest", "hardy_highland"], 4, "seasonal"),
        ]
        
        for code, name, desc, temp, precip, ag_suit, veg, season, water in temperate_types:
            types[code] = KoppenClimate(
                code=code, group=KoppenGroup.TEMPERATE, name=name, description=desc,
                temperature_pattern=temp, precipitation_pattern=precip,
                agricultural_suitability=ag_suit, typical_vegetation=veg,
                growing_season_months=season, water_balance=water
            )
        
        # Continental climates (D)
        continental_types = [
            ("Dfa", "Hot Continental", "Hot summers, cold winters", "hot_summer", "wet_year_round", 
             "good_continental", ["mixed_forest", "continental_crops"], 6, "seasonal_surplus"),
            ("Dfb", "Warm Continental", "Warm summers, cold winters", "warm_summer", "wet_year_round", 
             "good_continental", ["boreal_forest", "continental_crops"], 5, "seasonal_surplus"),
            ("Dfc", "Subarctic", "Cool summers, very cold winters", "cool_summer", "wet_year_round", 
             "limited_short_season", ["boreal_forest", "hardy_crops"], 4, "seasonal"),
            ("Dfd", "Extremely Cold Subarctic", "Cool summers, extremely cold winters", "cool_summer", "wet_year_round", 
             "very_limited", ["sparse_forest", "very_hardy"], 3, "seasonal"),
            ("Dsa", "Mediterranean Continental", "Hot dry summers, cold winters", "hot_summer", "dry_summer", 
             "moderate_continental", ["steppe", "drought_tolerant"], 5, "seasonal_deficit"),
            ("Dsb", "Warm Mediterranean Continental", "Warm dry summers, cold winters", "warm_summer", "dry_summer", 
             "moderate_continental", ["steppe", "drought_tolerant"], 4, "seasonal_deficit"),
            ("Dsc", "Cool Mediterranean Continental", "Cool dry summers, cold winters", "cool_summer", "dry_summer", 
             "limited_continental", ["sparse_forest", "hardy_drought"], 3, "deficit"),
            ("Dwa", "Monsoon Continental", "Hot wet summers, cold dry winters", "hot_summer", "dry_winter", 
             "moderate_monsoon", ["mixed_forest", "monsoon_continental"], 5, "seasonal"),
            ("Dwb", "Warm Monsoon Continental", "Warm wet summers, cold dry winters", "warm_summer", "dry_winter", 
             "moderate_monsoon", ["boreal_forest", "hardy_monsoon"], 4, "seasonal"),
            ("Dwc", "Cool Monsoon Continental", "Cool wet summers, cold dry winters", "cool_summer", "dry_winter", 
             "limited_monsoon", ["sparse_forest", "very_hardy"], 3, "seasonal"),
            ("Dwd", "Extremely Cold Monsoon Continental", "Cool wet summers, extremely cold dry winters", "cool_summer", "dry_winter", 
             "very_limited", ["sparse_forest", "extremely_hardy"], 2, "severe_seasonal"),
        ]
        
        for code, name, desc, temp, precip, ag_suit, veg, season, water in continental_types:
            types[code] = KoppenClimate(
                code=code, group=KoppenGroup.CONTINENTAL, name=name, description=desc,
                temperature_pattern=temp, precipitation_pattern=precip,
                agricultural_suitability=ag_suit, typical_vegetation=veg,
                growing_season_months=season, water_balance=water
            )
        
        # Polar climates (E)
        polar_types = [
            ("ET", "Tundra", "Very cold, short growing season", "tundra", "low_precipitation", 
             "no_agriculture", ["tundra", "mosses"], 2, "frozen"),
            ("EF", "Ice Cap", "Permanently frozen", "ice_cap", "very_low", 
             "no_agriculture", ["ice", "no_vegetation"], 0, "permanently_frozen"),
        ]
        
        for code, name, desc, temp, precip, ag_suit, veg, season, water in polar_types:
            types[code] = KoppenClimate(
                code=code, group=KoppenGroup.POLAR, name=name, description=desc,
                temperature_pattern=temp, precipitation_pattern=precip,
                agricultural_suitability=ag_suit, typical_vegetation=veg,
                growing_season_months=season, water_balance=water
            )
        
        return types
    
    def _initialize_temperature_thresholds(self) -> Dict:
        """Initialize temperature thresholds for Köppen classification."""
        
        return {
            "tropical_threshold": 18.0,  # °C, coldest month average
            "polar_threshold": 10.0,     # °C, warmest month average
            "hot_summer": 22.0,          # °C, warmest month average
            "warm_summer": 10.0,         # °C, at least 4 months above this
            "cold_winter": -3.0,         # °C, coldest month average
            "very_cold_winter": -38.0,   # °C, coldest month average
        }
    
    def _initialize_precipitation_thresholds(self) -> Dict:
        """Initialize precipitation thresholds for Köppen classification."""
        
        return {
            "arid_threshold_factor": 20,    # mm, used in arid calculations
            "dry_month_threshold": 60,      # mm, threshold for dry month
            "wet_month_threshold": 100,     # mm, threshold for wet month
            "monsoon_threshold": 100,       # mm, difference between wettest and driest
        }
    
    async def classify_climate(
        self,
        latitude: float,
        longitude: float,
        temperature_data: Optional[Dict] = None,
        precipitation_data: Optional[Dict] = None
    ) -> ClimateAnalysis:
        """
        Classify climate using Köppen system.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            temperature_data: Monthly temperature data (optional)
            precipitation_data: Monthly precipitation data (optional)
            
        Returns:
            ClimateAnalysis with Köppen classification
        """
        
        try:
            # If no climate data provided, estimate from coordinates
            if not temperature_data or not precipitation_data:
                temperature_data, precipitation_data = self._estimate_climate_data(latitude, longitude)
            
            # Classify using Köppen criteria
            koppen_code = self._determine_koppen_code(temperature_data, precipitation_data)
            koppen_type = self.climate_types.get(koppen_code)
            
            if not koppen_type:
                # Fallback to estimated type
                koppen_type = self._get_fallback_climate_type(latitude)
                confidence = 0.3
            else:
                confidence = self._calculate_classification_confidence(
                    temperature_data, precipitation_data, koppen_code
                )
            
            # Analyze seasonal patterns
            seasonal_patterns = self._analyze_seasonal_patterns(temperature_data, precipitation_data)
            
            # Determine agricultural implications
            agricultural_implications = self._analyze_agricultural_implications(
                koppen_type, temperature_data, precipitation_data
            )
            
            return ClimateAnalysis(
                koppen_type=koppen_type,
                confidence=confidence,
                temperature_data=temperature_data,
                precipitation_data=precipitation_data,
                seasonal_patterns=seasonal_patterns,
                agricultural_implications=agricultural_implications
            )
            
        except Exception as e:
            logger.error(f"Error classifying climate for {latitude}, {longitude}: {str(e)}")
            return self._get_fallback_analysis(latitude, longitude)
    
    def _estimate_climate_data(self, latitude: float, longitude: float) -> Tuple[Dict, Dict]:
        """Estimate climate data from coordinates."""
        
        # Simplified climate estimation based on latitude
        # In production, this would use detailed climate databases
        
        abs_lat = abs(latitude)
        
        # Temperature estimation
        if abs_lat < 23.5:  # Tropical
            temp_data = {
                "annual_mean": 26.0,
                "coldest_month": 24.0,
                "warmest_month": 28.0,
                "temperature_range": 4.0
            }
        elif abs_lat < 35:  # Subtropical
            temp_data = {
                "annual_mean": 18.0,
                "coldest_month": 8.0,
                "warmest_month": 28.0,
                "temperature_range": 20.0
            }
        elif abs_lat < 50:  # Temperate
            temp_data = {
                "annual_mean": 12.0,
                "coldest_month": 2.0,
                "warmest_month": 22.0,
                "temperature_range": 20.0
            }
        elif abs_lat < 66.5:  # Continental
            temp_data = {
                "annual_mean": 5.0,
                "coldest_month": -15.0,
                "warmest_month": 20.0,
                "temperature_range": 35.0
            }
        else:  # Polar
            temp_data = {
                "annual_mean": -10.0,
                "coldest_month": -25.0,
                "warmest_month": 5.0,
                "temperature_range": 30.0
            }
        
        # Precipitation estimation
        if -125 < longitude < -60:  # Americas
            if abs_lat < 10:
                precip_data = {"annual_total": 2000, "driest_month": 100, "wettest_month": 300}
            elif abs_lat < 30:
                precip_data = {"annual_total": 1200, "driest_month": 30, "wettest_month": 150}
            else:
                precip_data = {"annual_total": 800, "driest_month": 40, "wettest_month": 100}
        else:  # Other regions
            if abs_lat < 30:
                precip_data = {"annual_total": 1000, "driest_month": 20, "wettest_month": 200}
            else:
                precip_data = {"annual_total": 600, "driest_month": 30, "wettest_month": 80}
        
        return temp_data, precip_data
    
    def _determine_koppen_code(self, temp_data: Dict, precip_data: Dict) -> str:
        """Determine Köppen code from climate data."""
        
        coldest_month = temp_data.get("coldest_month", 0)
        warmest_month = temp_data.get("warmest_month", 20)
        annual_precip = precip_data.get("annual_total", 800)
        driest_month = precip_data.get("driest_month", 40)
        wettest_month = precip_data.get("wettest_month", 100)
        
        # First letter (main climate group)
        if coldest_month >= 18:
            # Tropical (A)
            if driest_month >= 60:
                return "Af"  # Tropical rainforest
            elif driest_month >= (100 - annual_precip/25):
                return "Am"  # Tropical monsoon
            else:
                return "Aw"  # Tropical savanna
        
        elif warmest_month < 10:
            # Polar (E)
            if warmest_month >= 0:
                return "ET"  # Tundra
            else:
                return "EF"  # Ice cap
        
        else:
            # Check if arid (B)
            arid_threshold = self._calculate_arid_threshold(temp_data, precip_data)
            if annual_precip < arid_threshold:
                if annual_precip < arid_threshold / 2:
                    # Desert (BW)
                    if temp_data.get("annual_mean", 15) >= 18:
                        return "BWh"  # Hot desert
                    else:
                        return "BWk"  # Cold desert
                else:
                    # Semi-arid (BS)
                    if temp_data.get("annual_mean", 15) >= 18:
                        return "BSh"  # Hot semi-arid
                    else:
                        return "BSk"  # Cold semi-arid
            
            # Temperate (C) or Continental (D)
            if coldest_month >= -3:
                # Temperate (C)
                return self._determine_temperate_subtype(temp_data, precip_data)
            else:
                # Continental (D)
                return self._determine_continental_subtype(temp_data, precip_data)
    
    def _calculate_arid_threshold(self, temp_data: Dict, precip_data: Dict) -> float:
        """Calculate arid threshold for Köppen classification."""
        
        annual_temp = temp_data.get("annual_mean", 15)
        
        # Simplified arid threshold calculation
        # Actual Köppen uses more complex seasonal precipitation patterns
        
        base_threshold = 20 * annual_temp
        
        # Adjust based on precipitation pattern
        # This is a simplified version
        return base_threshold
    
    def _determine_temperate_subtype(self, temp_data: Dict, precip_data: Dict) -> str:
        """Determine temperate climate subtype."""
        
        warmest_month = temp_data.get("warmest_month", 20)
        driest_month = precip_data.get("driest_month", 40)
        wettest_month = precip_data.get("wettest_month", 100)
        
        # Second letter (precipitation pattern)
        if driest_month >= 60:
            precip_code = "f"  # Wet year-round
        elif driest_month < wettest_month / 3:
            # Determine if dry season is summer or winter
            # Simplified: assume dry winter for most temperate climates
            precip_code = "w"  # Dry winter
        else:
            precip_code = "s"  # Dry summer
        
        # Third letter (temperature)
        if warmest_month >= 22:
            temp_code = "a"  # Hot summer
        elif warmest_month >= 10:
            # Count months above 10°C (simplified)
            temp_code = "b"  # Warm summer
        else:
            temp_code = "c"  # Cool summer
        
        return f"C{precip_code}{temp_code}"
    
    def _determine_continental_subtype(self, temp_data: Dict, precip_data: Dict) -> str:
        """Determine continental climate subtype."""
        
        warmest_month = temp_data.get("warmest_month", 20)
        coldest_month = temp_data.get("coldest_month", -10)
        driest_month = precip_data.get("driest_month", 40)
        wettest_month = precip_data.get("wettest_month", 100)
        
        # Second letter (precipitation pattern)
        if driest_month >= 60:
            precip_code = "f"  # Wet year-round
        elif driest_month < wettest_month / 3:
            precip_code = "w"  # Dry winter
        else:
            precip_code = "s"  # Dry summer
        
        # Third letter (temperature)
        if warmest_month >= 22:
            temp_code = "a"  # Hot summer
        elif warmest_month >= 10:
            temp_code = "b"  # Warm summer
        elif coldest_month < -38:
            temp_code = "d"  # Very cold winter
        else:
            temp_code = "c"  # Cool summer
        
        return f"D{precip_code}{temp_code}"
    
    def _calculate_classification_confidence(
        self, 
        temp_data: Dict, 
        precip_data: Dict, 
        koppen_code: str
    ) -> float:
        """Calculate confidence in Köppen classification."""
        
        # Base confidence depends on data quality
        base_confidence = 0.7 if temp_data and precip_data else 0.4
        
        # Increase confidence for clear classifications
        coldest_month = temp_data.get("coldest_month", 0)
        warmest_month = temp_data.get("warmest_month", 20)
        
        # Clear tropical
        if coldest_month > 20:
            base_confidence += 0.2
        # Clear polar
        elif warmest_month < 5:
            base_confidence += 0.2
        # Clear continental
        elif coldest_month < -10 and warmest_month > 15:
            base_confidence += 0.1
        
        return min(1.0, base_confidence)
    
    def _analyze_seasonal_patterns(self, temp_data: Dict, precip_data: Dict) -> Dict:
        """Analyze seasonal climate patterns."""
        
        return {
            "temperature_seasonality": self._assess_temperature_seasonality(temp_data),
            "precipitation_seasonality": self._assess_precipitation_seasonality(precip_data),
            "growing_season": self._estimate_growing_season_length(temp_data),
            "water_balance": self._assess_water_balance(temp_data, precip_data)
        }
    
    def _assess_temperature_seasonality(self, temp_data: Dict) -> str:
        """Assess temperature seasonality."""
        
        temp_range = temp_data.get("temperature_range", 10)
        
        if temp_range < 5:
            return "minimal_seasonal_variation"
        elif temp_range < 15:
            return "moderate_seasonal_variation"
        elif temp_range < 25:
            return "strong_seasonal_variation"
        else:
            return "extreme_seasonal_variation"
    
    def _assess_precipitation_seasonality(self, precip_data: Dict) -> str:
        """Assess precipitation seasonality."""
        
        driest = precip_data.get("driest_month", 40)
        wettest = precip_data.get("wettest_month", 100)
        
        if wettest / driest < 2:
            return "even_distribution"
        elif wettest / driest < 5:
            return "moderate_seasonality"
        else:
            return "strong_seasonality"
    
    def _estimate_growing_season_length(self, temp_data: Dict) -> int:
        """Estimate growing season length in months."""
        
        warmest = temp_data.get("warmest_month", 20)
        coldest = temp_data.get("coldest_month", 0)
        
        if coldest > 10:
            return 12  # Year-round growing
        elif coldest > 0:
            return 8   # Long growing season
        elif coldest > -10:
            return 6   # Moderate growing season
        elif coldest > -20:
            return 4   # Short growing season
        else:
            return 2   # Very short growing season
    
    def _assess_water_balance(self, temp_data: Dict, precip_data: Dict) -> str:
        """Assess water balance for agriculture."""
        
        annual_precip = precip_data.get("annual_total", 800)
        annual_temp = temp_data.get("annual_mean", 15)
        
        # Simplified water balance assessment
        # Higher temperatures increase evapotranspiration
        
        if annual_precip > 1500:
            return "water_surplus"
        elif annual_precip > 800:
            if annual_temp < 20:
                return "adequate_water"
            else:
                return "seasonal_water_stress"
        elif annual_precip > 400:
            return "water_limited"
        else:
            return "severe_water_deficit"
    
    def _analyze_agricultural_implications(
        self, 
        koppen_type: KoppenClimate, 
        temp_data: Dict, 
        precip_data: Dict
    ) -> Dict:
        """Analyze agricultural implications of climate type."""
        
        return {
            "crop_suitability": self._assess_crop_suitability(koppen_type, temp_data),
            "growing_challenges": self._identify_growing_challenges(koppen_type, temp_data, precip_data),
            "management_recommendations": self._get_management_recommendations(koppen_type),
            "irrigation_needs": self._assess_irrigation_needs(koppen_type, precip_data),
            "seasonal_planning": self._get_seasonal_planning_advice(koppen_type, temp_data)
        }
    
    def _assess_crop_suitability(self, koppen_type: KoppenClimate, temp_data: Dict) -> Dict:
        """Assess crop suitability for climate type."""
        
        suitability_map = {
            "excellent_tropical": ["rice", "sugarcane", "tropical_fruits", "vegetables"],
            "good_tropical": ["rice", "corn", "tropical_fruits", "legumes"],
            "moderate_tropical": ["corn", "sorghum", "cotton", "drought_tolerant_crops"],
            "excellent_diverse": ["corn", "soybeans", "wheat", "vegetables", "fruits"],
            "good_temperate": ["wheat", "barley", "vegetables", "temperate_fruits"],
            "good_continental": ["wheat", "corn", "soybeans", "hardy_crops"],
            "limited_short_season": ["barley", "oats", "hardy_vegetables", "berries"],
            "drought_tolerant": ["wheat", "sorghum", "millet", "drought_crops"],
            "limited_irrigation": ["drought_resistant_crops", "cacti", "desert_plants"],
            "no_agriculture": []
        }
        
        suitable_crops = suitability_map.get(koppen_type.agricultural_suitability, ["hardy_crops"])
        
        return {
            "highly_suitable": suitable_crops[:2] if suitable_crops else [],
            "moderately_suitable": suitable_crops[2:4] if len(suitable_crops) > 2 else [],
            "challenging": suitable_crops[4:] if len(suitable_crops) > 4 else [],
            "not_recommended": self._get_unsuitable_crops(koppen_type)
        }
    
    def _identify_growing_challenges(
        self, 
        koppen_type: KoppenClimate, 
        temp_data: Dict, 
        precip_data: Dict
    ) -> List[str]:
        """Identify main growing challenges for climate type."""
        
        challenges = []
        
        if koppen_type.group == KoppenGroup.ARID:
            challenges.extend(["water_scarcity", "high_evaporation", "soil_salinity"])
        
        if koppen_type.group == KoppenGroup.POLAR:
            challenges.extend(["short_growing_season", "frost_risk", "permafrost"])
        
        if "monsoon" in koppen_type.precipitation_pattern:
            challenges.extend(["flooding_risk", "seasonal_drought", "disease_pressure"])
        
        if temp_data.get("temperature_range", 10) > 30:
            challenges.append("extreme_temperature_variation")
        
        if precip_data.get("annual_total", 800) < 400:
            challenges.append("drought_stress")
        
        return challenges
    
    def _get_management_recommendations(self, koppen_type: KoppenClimate) -> List[str]:
        """Get management recommendations for climate type."""
        
        recommendations = []
        
        if koppen_type.group == KoppenGroup.TROPICAL:
            recommendations.extend([
                "disease_and_pest_monitoring",
                "drainage_management",
                "nutrient_leaching_prevention"
            ])
        
        elif koppen_type.group == KoppenGroup.ARID:
            recommendations.extend([
                "water_conservation",
                "drought_resistant_varieties",
                "soil_moisture_retention"
            ])
        
        elif koppen_type.group == KoppenGroup.CONTINENTAL:
            recommendations.extend([
                "frost_protection",
                "seasonal_planning",
                "soil_temperature_management"
            ])
        
        elif koppen_type.group == KoppenGroup.TEMPERATE:
            recommendations.extend([
                "integrated_pest_management",
                "crop_rotation",
                "soil_health_maintenance"
            ])
        
        return recommendations
    
    def _assess_irrigation_needs(self, koppen_type: KoppenClimate, precip_data: Dict) -> str:
        """Assess irrigation needs for climate type."""
        
        annual_precip = precip_data.get("annual_total", 800)
        
        if koppen_type.group == KoppenGroup.ARID:
            return "essential"
        elif annual_precip < 500:
            return "highly_recommended"
        elif annual_precip < 800:
            return "supplemental"
        elif "dry_summer" in koppen_type.precipitation_pattern:
            return "seasonal"
        else:
            return "minimal"
    
    def _get_seasonal_planning_advice(self, koppen_type: KoppenClimate, temp_data: Dict) -> Dict:
        """Get seasonal planning advice for climate type."""
        
        return {
            "planting_season": self._get_optimal_planting_season(koppen_type, temp_data),
            "harvest_timing": self._get_harvest_timing(koppen_type),
            "critical_periods": self._identify_critical_periods(koppen_type),
            "risk_management": self._get_seasonal_risk_management(koppen_type)
        }
    
    def _get_optimal_planting_season(self, koppen_type: KoppenClimate, temp_data: Dict) -> str:
        """Get optimal planting season for climate type."""
        
        if koppen_type.group == KoppenGroup.TROPICAL:
            if "monsoon" in koppen_type.precipitation_pattern:
                return "beginning_of_wet_season"
            else:
                return "year_round_possible"
        
        elif koppen_type.group == KoppenGroup.TEMPERATE:
            return "spring_after_frost_risk"
        
        elif koppen_type.group == KoppenGroup.CONTINENTAL:
            return "late_spring_early_summer"
        
        elif koppen_type.group == KoppenGroup.ARID:
            return "cooler_months_if_water_available"
        
        else:
            return "very_short_summer_window"
    
    def _get_harvest_timing(self, koppen_type: KoppenClimate) -> str:
        """Get harvest timing for climate type."""
        
        if koppen_type.growing_season_months >= 10:
            return "multiple_harvests_possible"
        elif koppen_type.growing_season_months >= 6:
            return "single_main_harvest"
        else:
            return "short_harvest_window"
    
    def _identify_critical_periods(self, koppen_type: KoppenClimate) -> List[str]:
        """Identify critical periods for climate type."""
        
        critical_periods = []
        
        if "monsoon" in koppen_type.precipitation_pattern:
            critical_periods.extend(["monsoon_onset", "dry_season_transition"])
        
        if koppen_type.group in [KoppenGroup.TEMPERATE, KoppenGroup.CONTINENTAL]:
            critical_periods.extend(["frost_dates", "growing_season_start"])
        
        if koppen_type.group == KoppenGroup.ARID:
            critical_periods.extend(["water_availability", "extreme_heat_periods"])
        
        return critical_periods
    
    def _get_seasonal_risk_management(self, koppen_type: KoppenClimate) -> List[str]:
        """Get seasonal risk management strategies."""
        
        strategies = []
        
        if "dry" in koppen_type.precipitation_pattern:
            strategies.append("drought_contingency_planning")
        
        if koppen_type.group == KoppenGroup.CONTINENTAL:
            strategies.append("frost_protection_measures")
        
        if "monsoon" in koppen_type.precipitation_pattern:
            strategies.append("flood_and_disease_management")
        
        return strategies
    
    def _get_unsuitable_crops(self, koppen_type: KoppenClimate) -> List[str]:
        """Get crops not suitable for climate type."""
        
        unsuitable = []
        
        if koppen_type.group == KoppenGroup.ARID:
            unsuitable.extend(["rice", "water_intensive_crops"])
        
        if koppen_type.group == KoppenGroup.POLAR:
            unsuitable.extend(["tropical_crops", "heat_loving_crops"])
        
        if koppen_type.group == KoppenGroup.TROPICAL:
            unsuitable.extend(["temperate_fruits", "cold_season_crops"])
        
        return unsuitable
    
    def _get_fallback_climate_type(self, latitude: float) -> KoppenClimate:
        """Get fallback climate type based on latitude."""
        
        abs_lat = abs(latitude)
        
        if abs_lat < 23.5:
            return self.climate_types["Aw"]  # Tropical savanna
        elif abs_lat < 35:
            return self.climate_types["Cfa"]  # Humid subtropical
        elif abs_lat < 50:
            return self.climate_types["Cfb"]  # Oceanic
        elif abs_lat < 66.5:
            return self.climate_types["Dfb"]  # Warm continental
        else:
            return self.climate_types["ET"]   # Tundra
    
    def _get_fallback_analysis(self, latitude: float, longitude: float) -> ClimateAnalysis:
        """Get fallback climate analysis when classification fails."""
        
        fallback_type = self._get_fallback_climate_type(latitude)
        temp_data, precip_data = self._estimate_climate_data(latitude, longitude)
        
        return ClimateAnalysis(
            koppen_type=fallback_type,
            confidence=0.3,  # Low confidence for fallback
            temperature_data=temp_data,
            precipitation_data=precip_data,
            seasonal_patterns={"note": "estimated_patterns"},
            agricultural_implications={"note": "general_recommendations"}
        )
    
    def get_climate_type_by_code(self, code: str) -> Optional[KoppenClimate]:
        """Get Köppen climate type by code."""
        return self.climate_types.get(code)
    
    def list_climate_types(self, group: Optional[KoppenGroup] = None) -> List[KoppenClimate]:
        """List Köppen climate types, optionally filtered by group."""
        
        if group:
            return [climate for climate in self.climate_types.values() 
                   if climate.group == group]
        else:
            return list(self.climate_types.values())


# Global service instance
koppen_climate_service = KoppenClimateService()