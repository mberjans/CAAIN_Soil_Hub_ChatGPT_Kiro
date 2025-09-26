"""
Planting Date Calculator Service

Calculates optimal planting dates based on climate zone, frost dates, 
and crop-specific requirements for agricultural planning.
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, date, timedelta
from dataclasses import dataclass, field
import logging

try:
    from ..models.agricultural_models import LocationData, CropData
except ImportError:
    from models.agricultural_models import LocationData, CropData

logger = logging.getLogger(__name__)


@dataclass
class PlantingWindow:
    """Represents a planting window with date ranges and recommendations."""
    
    crop_name: str
    optimal_date: date
    earliest_safe_date: date
    latest_safe_date: date
    planting_season: str  # "spring", "summer", "fall", "winter"
    safety_margin_days: int
    confidence_score: float = field(default=0.8)
    frost_considerations: List[str] = field(default_factory=list)
    climate_warnings: List[str] = field(default_factory=list)
    growing_degree_days_required: Optional[int] = None
    expected_harvest_date: Optional[date] = None


@dataclass 
class FrostDateInfo:
    """Frost date information for a location."""
    
    last_frost_date: Optional[date] = None
    first_frost_date: Optional[date] = None
    growing_season_length: Optional[int] = None
    frost_free_days: Optional[int] = None
    confidence_level: str = "estimated"  # "historical", "estimated", "default"


@dataclass
class CropTimingProfile:
    """Crop-specific timing and growth characteristics."""
    
    crop_name: str
    crop_category: str  # "cool_season", "warm_season", "heat_sensitive" 
    frost_tolerance: str  # "tolerant", "sensitive", "very_sensitive"
    days_to_maturity: int
    growing_degree_days: Optional[int] = None
    planting_depth_inches: float = 1.0
    soil_temp_min_f: Optional[int] = None
    succession_interval_days: Optional[int] = None
    fall_planting_possible: bool = False
    winter_hardy: bool = False


class PlantingDateCalculatorService:
    """Service for calculating optimal planting dates based on climate and crop requirements."""
    
    def __init__(self):
        """Initialize the planting date calculator service."""
        self.crop_timing_database = self._build_crop_timing_database()
        
        # Import weather/climate services for frost date analysis
        try:
            from .weather_service import WeatherService
            self.weather_service = WeatherService()
        except ImportError:
            try:
                from ..services.weather_service import WeatherService  
                self.weather_service = WeatherService()
            except ImportError:
                logger.warning("Weather service not available for frost date analysis")
                self.weather_service = None
                
        # Import data integration weather service
        try:
            import sys
            import os
            # Add data-integration service path for imports
            data_integration_path = os.path.join(
                os.path.dirname(__file__), '..', '..', '..', '..', 'data-integration', 'src'
            )
            if data_integration_path not in sys.path:
                sys.path.append(data_integration_path)
            
            from services.weather_service import EnhancedWeatherService
            self.enhanced_weather_service = EnhancedWeatherService()
        except ImportError:
            try:
                # Alternative import path
                from ....data_integration.src.services.weather_service import EnhancedWeatherService
                self.enhanced_weather_service = EnhancedWeatherService()
            except ImportError:
                logger.warning("Enhanced weather service not available")
                self.enhanced_weather_service = None
    
    def _build_crop_timing_database(self) -> Dict[str, CropTimingProfile]:
        """Build database of crop timing characteristics."""
        return {
            "corn": CropTimingProfile(
                crop_name="corn",
                crop_category="warm_season", 
                frost_tolerance="very_sensitive",
                days_to_maturity=120,
                growing_degree_days=2500,
                soil_temp_min_f=50,
                succession_interval_days=14,
                fall_planting_possible=False,
                winter_hardy=False
            ),
            "soybean": CropTimingProfile(
                crop_name="soybean", 
                crop_category="warm_season",
                frost_tolerance="sensitive", 
                days_to_maturity=110,
                growing_degree_days=2200,
                soil_temp_min_f=50,
                succession_interval_days=None,
                fall_planting_possible=False,
                winter_hardy=False
            ),
            "wheat": CropTimingProfile(
                crop_name="wheat",
                crop_category="cool_season",
                frost_tolerance="tolerant",
                days_to_maturity=120,
                growing_degree_days=2000,
                soil_temp_min_f=35,
                succession_interval_days=None,
                fall_planting_possible=True,  # Winter wheat
                winter_hardy=True
            ),
            "peas": CropTimingProfile(
                crop_name="peas", 
                crop_category="cool_season",
                frost_tolerance="tolerant",
                days_to_maturity=65,
                growing_degree_days=1200,
                soil_temp_min_f=35,
                succession_interval_days=10,
                fall_planting_possible=True,
                winter_hardy=False
            ),
            "lettuce": CropTimingProfile(
                crop_name="lettuce",
                crop_category="cool_season", 
                frost_tolerance="sensitive",
                days_to_maturity=45,
                growing_degree_days=900,
                soil_temp_min_f=35,
                succession_interval_days=7,
                fall_planting_possible=True,
                winter_hardy=False
            ),
            "spinach": CropTimingProfile(
                crop_name="spinach",
                crop_category="cool_season",
                frost_tolerance="tolerant", 
                days_to_maturity=40,
                growing_degree_days=800,
                soil_temp_min_f=32,
                succession_interval_days=10,
                fall_planting_possible=True,
                winter_hardy=True
            ),
            "tomato": CropTimingProfile(
                crop_name="tomato",
                crop_category="heat_sensitive",
                frost_tolerance="very_sensitive",
                days_to_maturity=85,
                growing_degree_days=2000,
                soil_temp_min_f=60,
                succession_interval_days=None,
                fall_planting_possible=False,
                winter_hardy=False
            ),
            "potato": CropTimingProfile(
                crop_name="potato", 
                crop_category="cool_season",
                frost_tolerance="sensitive",
                days_to_maturity=90,
                growing_degree_days=1500,
                soil_temp_min_f=45,
                succession_interval_days=14, 
                fall_planting_possible=True,
                winter_hardy=False
            ),
            "onion": CropTimingProfile(
                crop_name="onion",
                crop_category="cool_season",
                frost_tolerance="tolerant",
                days_to_maturity=120,
                growing_degree_days=1800,
                soil_temp_min_f=35,
                succession_interval_days=None,
                fall_planting_possible=True,
                winter_hardy=True
            )
        }
    
    async def calculate_planting_dates(
        self,
        crop_name: str,
        location: LocationData,
        planting_season: str = "spring"
    ) -> PlantingWindow:
        """
        Calculate optimal planting dates for a specific crop and location.
        
        Args:
            crop_name: Name of the crop to plant
            location: Location data with coordinates and climate info
            planting_season: Target planting season ("spring", "summer", "fall")
            
        Returns:
            PlantingWindow with optimal dates and recommendations
        """
        logger.info(f"Calculating planting dates for {crop_name} at {location.latitude}, {location.longitude}")
        
        # Get crop timing profile
        crop_profile = self.crop_timing_database.get(crop_name.lower())
        if not crop_profile:
            raise ValueError(f"No timing data available for crop: {crop_name}")
        
        # Get frost date information
        frost_info = await self._get_frost_date_info(location)
        
        # Calculate planting window based on season and crop type
        if planting_season == "spring":
            planting_window = self._calculate_spring_planting(crop_profile, frost_info, location)
        elif planting_season == "fall":
            planting_window = self._calculate_fall_planting(crop_profile, frost_info, location)
        elif planting_season == "summer":
            planting_window = self._calculate_summer_planting(crop_profile, frost_info, location)
        else:
            raise ValueError(f"Invalid planting season: {planting_season}")
        
        # Add climate zone specific adjustments
        planting_window = self._apply_climate_zone_adjustments(planting_window, location)
        
        # Validate growing degree day requirements
        await self._validate_growing_degree_days(planting_window, location)
        
        return planting_window
    
    async def _get_frost_date_info(self, location: LocationData) -> FrostDateInfo:
        """Get frost date information for a location."""
        
        # Try to get from enhanced weather service first
        if self.enhanced_weather_service:
            try:
                climate_data = await self.enhanced_weather_service.get_climate_zone_data(
                    latitude=location.latitude,
                    longitude=location.longitude,
                    elevation_ft=location.elevation_ft
                )
                
                if climate_data:
                    last_frost = self._parse_frost_date(climate_data.last_frost_date) if climate_data.last_frost_date else None
                    first_frost = self._parse_frost_date(climate_data.first_frost_date) if climate_data.first_frost_date else None
                    
                    return FrostDateInfo(
                        last_frost_date=last_frost,
                        first_frost_date=first_frost,
                        growing_season_length=climate_data.growing_season_length,
                        frost_free_days=climate_data.growing_season_length,
                        confidence_level="historical"
                    )
            except Exception as e:
                logger.warning(f"Could not get frost dates from enhanced weather service: {e}")
        
        # Fallback to estimated frost dates based on climate zone
        return self._estimate_frost_dates(location)
    
    def _parse_frost_date(self, frost_date_str: str) -> Optional[date]:
        """Parse frost date string (MM-DD format) to date object for current year."""
        if not frost_date_str:
            return None
        
        try:
            month, day = map(int, frost_date_str.split('-'))
            current_year = datetime.now().year
            return date(current_year, month, day)
        except (ValueError, AttributeError):
            logger.warning(f"Could not parse frost date: {frost_date_str}")
            return None
    
    def _estimate_frost_dates(self, location: LocationData) -> FrostDateInfo:
        """Estimate frost dates based on location and climate zone."""
        
        # Get climate zone from location data
        climate_zone = getattr(location, 'climate_zone', None)
        
        # Default frost date estimates by USDA zone
        zone_frost_estimates = {
            "3a": {"last_frost": "05-15", "first_frost": "09-30", "growing_days": 137},
            "3b": {"last_frost": "05-10", "first_frost": "10-05", "growing_days": 148}, 
            "4a": {"last_frost": "05-01", "first_frost": "10-15", "growing_days": 167},
            "4b": {"last_frost": "04-25", "first_frost": "10-20", "growing_days": 178},
            "5a": {"last_frost": "04-15", "first_frost": "10-25", "growing_days": 193},
            "5b": {"last_frost": "04-10", "first_frost": "10-30", "growing_days": 203},
            "6a": {"last_frost": "04-05", "first_frost": "11-05", "growing_days": 214},
            "6b": {"last_frost": "03-30", "first_frost": "11-10", "growing_days": 225},
            "7a": {"last_frost": "03-25", "first_frost": "11-15", "growing_days": 235},
            "7b": {"last_frost": "03-20", "first_frost": "11-20", "growing_days": 245}
        }
        
        # Use zone-specific estimates if available
        if climate_zone and climate_zone in zone_frost_estimates:
            estimates = zone_frost_estimates[climate_zone]
            last_frost = self._parse_frost_date(estimates["last_frost"])
            first_frost = self._parse_frost_date(estimates["first_frost"])
            growing_days = estimates["growing_days"]
            confidence = "estimated"
        else:
            # Rough latitude-based estimates for unknown zones
            lat = location.latitude
            if lat >= 48:  # Northern regions
                last_frost = self._parse_frost_date("05-15")
                first_frost = self._parse_frost_date("09-15") 
                growing_days = 123
            elif lat >= 42:  # Northern temperate
                last_frost = self._parse_frost_date("04-15")
                first_frost = self._parse_frost_date("10-15")
                growing_days = 183
            elif lat >= 35:  # Central temperate  
                last_frost = self._parse_frost_date("03-30")
                first_frost = self._parse_frost_date("11-01")
                growing_days = 216
            else:  # Southern regions
                last_frost = self._parse_frost_date("03-01")
                first_frost = self._parse_frost_date("11-30")
                growing_days = 274
            confidence = "default"
        
        return FrostDateInfo(
            last_frost_date=last_frost,
            first_frost_date=first_frost,
            growing_season_length=growing_days,
            frost_free_days=growing_days,
            confidence_level=confidence
        )
    
    def _calculate_spring_planting(
        self, 
        crop_profile: CropTimingProfile, 
        frost_info: FrostDateInfo,
        location: LocationData
    ) -> PlantingWindow:
        """Calculate spring planting window for a crop."""
        
        if not frost_info.last_frost_date:
            raise ValueError("Last frost date required for spring planting calculation")
        
        # Determine safety margin based on crop frost tolerance
        safety_margins = {
            "tolerant": -14,      # Can plant 2 weeks before last frost
            "sensitive": 7,       # Plant 1 week after last frost  
            "very_sensitive": 14  # Plant 2 weeks after last frost
        }
        
        safety_days = safety_margins.get(crop_profile.frost_tolerance, 7)
        
        # Calculate optimal planting date
        optimal_date = frost_info.last_frost_date + timedelta(days=safety_days)
        
        # Calculate planting window (2 weeks before to 3 weeks after optimal)
        earliest_safe = optimal_date - timedelta(days=14)
        latest_safe = optimal_date + timedelta(days=21)
        
        # Adjust for cool-season crops (can plant earlier)
        if crop_profile.crop_category == "cool_season":
            earliest_safe = frost_info.last_frost_date - timedelta(days=28)
            if crop_profile.frost_tolerance == "tolerant":
                earliest_safe = frost_info.last_frost_date - timedelta(days=35)
        
        # Calculate expected harvest date
        harvest_date = optimal_date + timedelta(days=crop_profile.days_to_maturity)
        
        # Generate frost considerations and warnings
        frost_considerations = []
        climate_warnings = []
        
        if crop_profile.frost_tolerance == "very_sensitive":
            frost_considerations.append("Wait for soil temperature to consistently reach 50°F+")
            frost_considerations.append("Monitor weather forecasts for late frost risk")
        elif crop_profile.frost_tolerance == "sensitive": 
            frost_considerations.append("Light frost after planting may damage seedlings")
        
        # Check if harvest will complete before first frost
        if frost_info.first_frost_date and harvest_date > frost_info.first_frost_date:
            climate_warnings.append(f"Harvest may not complete before first frost ({frost_info.first_frost_date.strftime('%B %d')})")
        
        return PlantingWindow(
            crop_name=crop_profile.crop_name,
            optimal_date=optimal_date,
            earliest_safe_date=earliest_safe,
            latest_safe_date=latest_safe,
            planting_season="spring",
            safety_margin_days=safety_days,
            frost_considerations=frost_considerations,
            climate_warnings=climate_warnings,
            growing_degree_days_required=crop_profile.growing_degree_days,
            expected_harvest_date=harvest_date
        )
    
    def _calculate_fall_planting(
        self,
        crop_profile: CropTimingProfile,
        frost_info: FrostDateInfo, 
        location: LocationData
    ) -> PlantingWindow:
        """Calculate fall planting window for a crop."""
        
        if not crop_profile.fall_planting_possible:
            raise ValueError(f"{crop_profile.crop_name} is not suitable for fall planting")
        
        if not frost_info.first_frost_date:
            raise ValueError("First frost date required for fall planting calculation")
        
        # Calculate planting date working backwards from first frost
        # Need crop to mature before killing frost
        optimal_date = frost_info.first_frost_date - timedelta(days=crop_profile.days_to_maturity)
        
        # Adjust for frost tolerance
        if crop_profile.frost_tolerance == "tolerant":
            # Can harvest closer to or even after light frost
            optimal_date = frost_info.first_frost_date - timedelta(days=crop_profile.days_to_maturity - 14)
        elif crop_profile.winter_hardy:
            # Winter hardy crops can be planted later for spring harvest
            optimal_date = frost_info.first_frost_date - timedelta(days=45)
        
        # Calculate planting window
        earliest_safe = optimal_date - timedelta(days=10)
        latest_safe = optimal_date + timedelta(days=14)
        
        # Calculate expected harvest date  
        harvest_date = optimal_date + timedelta(days=crop_profile.days_to_maturity)
        
        frost_considerations = []
        climate_warnings = []
        
        if crop_profile.winter_hardy:
            frost_considerations.append("Crop will overwinter and resume growth in spring")
            harvest_date = date(harvest_date.year + 1, 4, 15)  # Estimate spring harvest
        else:
            frost_considerations.append("Must harvest before hard frost")
        
        # Add heat stress considerations for fall planting
        current_date = date.today()
        if optimal_date.month in [7, 8]:  # Hot summer planting
            climate_warnings.append("Provide shade and extra water during hot summer establishment")
        
        return PlantingWindow(
            crop_name=crop_profile.crop_name,
            optimal_date=optimal_date,
            earliest_safe_date=earliest_safe,
            latest_safe_date=latest_safe, 
            planting_season="fall",
            safety_margin_days=0,
            frost_considerations=frost_considerations,
            climate_warnings=climate_warnings,
            growing_degree_days_required=crop_profile.growing_degree_days,
            expected_harvest_date=harvest_date
        )
    
    def _calculate_summer_planting(
        self,
        crop_profile: CropTimingProfile,
        frost_info: FrostDateInfo,
        location: LocationData
    ) -> PlantingWindow:
        """Calculate summer planting window (succession crops or heat-tolerant varieties)."""
        
        # Summer planting is primarily for succession crops
        if not crop_profile.succession_interval_days:
            raise ValueError(f"{crop_profile.crop_name} is not suitable for succession planting")
        
        # Use mid-summer as base (July 1st)
        current_year = datetime.now().year
        base_date = date(current_year, 7, 1)
        
        # Calculate optimal summer planting date
        optimal_date = base_date
        
        # For cool-season crops in summer, plant later to avoid peak heat
        if crop_profile.crop_category == "cool_season":
            optimal_date = date(current_year, 8, 1)  # August planting
        
        # Calculate planting window
        earliest_safe = optimal_date - timedelta(days=7)
        latest_safe = optimal_date + timedelta(days=14)
        
        # Calculate expected harvest date
        harvest_date = optimal_date + timedelta(days=crop_profile.days_to_maturity)
        
        frost_considerations = []
        climate_warnings = []
        
        # Heat stress warnings
        if crop_profile.crop_category == "cool_season":
            climate_warnings.append("Provide afternoon shade and consistent moisture")
            climate_warnings.append("Consider heat-resistant varieties")
        
        # Check harvest timing vs first frost
        if frost_info.first_frost_date and harvest_date > frost_info.first_frost_date:
            climate_warnings.append("Harvest before first frost - consider faster-maturing varieties")
        
        return PlantingWindow(
            crop_name=crop_profile.crop_name,
            optimal_date=optimal_date,
            earliest_safe_date=earliest_safe,
            latest_safe_date=latest_safe,
            planting_season="summer", 
            safety_margin_days=0,
            frost_considerations=frost_considerations,
            climate_warnings=climate_warnings,
            growing_degree_days_required=crop_profile.growing_degree_days,
            expected_harvest_date=harvest_date
        )
    
    def _apply_climate_zone_adjustments(self, planting_window: PlantingWindow, location: LocationData) -> PlantingWindow:
        """Apply climate zone specific adjustments to planting window."""
        
        climate_zone = getattr(location, 'climate_zone', None)
        
        if not climate_zone:
            return planting_window
        
        # Northern zones (3-4): conservative adjustments
        if climate_zone and climate_zone.startswith(('3', '4')):
            # Shorter growing season - be more conservative
            if planting_window.planting_season == "spring":
                planting_window.optimal_date += timedelta(days=7)
                planting_window.climate_warnings.append("Northern climate: monitor soil temperature before planting")
            
            planting_window.confidence_score *= 0.9
        
        # Southern zones (7+): heat adjustments
        elif climate_zone and climate_zone.startswith(('7', '8', '9')):
            if planting_window.planting_season == "summer":
                planting_window.climate_warnings.append("Hot climate: ensure adequate irrigation")
            
            # Can plant earlier in spring
            if planting_window.planting_season == "spring":
                planting_window.earliest_safe_date -= timedelta(days=7)
        
        return planting_window
    
    async def _validate_growing_degree_days(self, planting_window: PlantingWindow, location: LocationData) -> None:
        """Validate that location has sufficient growing degree days for crop."""
        
        if not planting_window.growing_degree_days_required:
            return
        
        # This would ideally use historical weather data to calculate GDD
        # For now, we'll use rough climate zone estimates
        climate_zone = getattr(location, 'climate_zone', None)
        
        # Rough GDD estimates by climate zone (base 50°F)
        zone_gdd_estimates = {
            "3a": 1800, "3b": 2000, "4a": 2200, "4b": 2400,
            "5a": 2600, "5b": 2800, "6a": 3000, "6b": 3200,
            "7a": 3400, "7b": 3600, "8a": 3800, "8b": 4000
        }
        
        if climate_zone in zone_gdd_estimates:
            available_gdd = zone_gdd_estimates[climate_zone]
            required_gdd = planting_window.growing_degree_days_required
            
            if available_gdd < required_gdd:
                planting_window.climate_warnings.append(
                    f"Climate may not provide sufficient heat units ({required_gdd} GDD required, ~{available_gdd} available)"
                )
                planting_window.confidence_score *= 0.7
            elif available_gdd < required_gdd * 1.2:  # Marginal
                planting_window.climate_warnings.append(
                    f"Marginal growing degree days available - monitor season length"
                )
                planting_window.confidence_score *= 0.9
    
    def get_succession_planting_schedule(
        self,
        crop_name: str,
        location: LocationData,
        start_date: date,
        end_date: date,
        max_plantings: int = 5
    ) -> List[PlantingWindow]:
        """
        Generate succession planting schedule for continuous harvest.
        
        Args:
            crop_name: Name of the crop
            location: Location data
            start_date: First planting date
            end_date: Latest acceptable planting date
            max_plantings: Maximum number of succession plantings
            
        Returns:
            List of PlantingWindow objects for succession plantings
        """
        
        crop_profile = self.crop_timing_database.get(crop_name.lower())
        if not crop_profile or not crop_profile.succession_interval_days:
            raise ValueError(f"Crop {crop_name} is not suitable for succession planting")
        
        succession_schedule = []
        current_planting_date = start_date
        planting_number = 1
        
        while (current_planting_date <= end_date and 
               len(succession_schedule) < max_plantings):
            
            # Create a planting window for this date
            planting_window = PlantingWindow(
                crop_name=crop_profile.crop_name,
                optimal_date=current_planting_date,
                earliest_safe_date=current_planting_date - timedelta(days=3),
                latest_safe_date=current_planting_date + timedelta(days=7),
                planting_season="succession",
                safety_margin_days=0,
                confidence_score=0.8,
                frost_considerations=[f"Succession planting #{planting_number}"],
                climate_warnings=[],
                growing_degree_days_required=crop_profile.growing_degree_days,
                expected_harvest_date=current_planting_date + timedelta(days=crop_profile.days_to_maturity)
            )
            
            succession_schedule.append(planting_window)
            
            # Calculate next planting date
            current_planting_date += timedelta(days=crop_profile.succession_interval_days)
            planting_number += 1
        
        return succession_schedule
    
    async def get_multiple_season_plantings(
        self,
        crop_name: str,
        location: LocationData
    ) -> List[PlantingWindow]:
        """
        Get all possible planting windows for a crop (spring, summer, fall).
        
        Args:
            crop_name: Name of the crop
            location: Location data
            
        Returns:
            List of PlantingWindow objects for different seasons
        """
        
        crop_profile = self.crop_timing_database.get(crop_name.lower())
        if not crop_profile:
            raise ValueError(f"No timing data available for crop: {crop_name}")
        
        planting_windows = []
        
        try:
            # Spring planting (always possible)
            spring_window = await self.calculate_planting_dates(crop_name, location, "spring")
            planting_windows.append(spring_window)
        except Exception as e:
            logger.warning(f"Could not calculate spring planting for {crop_name}: {e}")
        
        try:
            # Summer planting (succession crops)
            if crop_profile.succession_interval_days:
                summer_window = await self.calculate_planting_dates(crop_name, location, "summer")
                planting_windows.append(summer_window)
        except Exception as e:
            logger.debug(f"Summer planting not available for {crop_name}: {e}")
        
        try:
            # Fall planting
            if crop_profile.fall_planting_possible:
                fall_window = await self.calculate_planting_dates(crop_name, location, "fall")
                planting_windows.append(fall_window)
        except Exception as e:
            logger.debug(f"Fall planting not available for {crop_name}: {e}")
        
        return planting_windows


# Create singleton instance
planting_date_service = PlantingDateCalculatorService()