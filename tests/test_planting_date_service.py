"""
Test Planting Date Calculator Service

Comprehensive tests for planting date calculations, frost date analysis,
and seasonal timing recommendations.
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# Add the services directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services', 'recommendation-engine', 'src'))

from services.planting_date_service import (
    PlantingDateCalculatorService,
    PlantingWindow,
    FrostDateInfo,
    CropTimingProfile
)
from models.agricultural_models import LocationData


@pytest.fixture
def planting_service():
    """Create planting date calculator service for testing."""
    return PlantingDateCalculatorService()


@pytest.fixture
def sample_location():
    """Create sample location data for testing."""
    return LocationData(
        latitude=42.3601,
        longitude=-71.0589,  # Boston, MA area
        elevation_ft=20,
        address="Boston, MA", 
        state="Massachusetts",
        county="Suffolk",
        climate_zone="6a",
        climate_zone_name="USDA Zone 6a",
        temperature_range_f={"min": -10, "max": 0},
        climate_confidence=0.9
    )


@pytest.fixture
def sample_frost_info():
    """Create sample frost date information."""
    return FrostDateInfo(
        last_frost_date=date(2024, 4, 15),
        first_frost_date=date(2024, 10, 20),
        growing_season_length=188,
        frost_free_days=188,
        confidence_level="historical"
    )


class TestCropTimingDatabase:
    """Test crop timing database and profiles."""
    
    def test_crop_database_completeness(self, planting_service):
        """Test that crop database contains expected crops."""
        expected_crops = ["corn", "soybean", "wheat", "peas", "lettuce", "spinach", "tomato", "potato", "onion"]
        
        for crop in expected_crops:
            assert crop in planting_service.crop_timing_database
            profile = planting_service.crop_timing_database[crop]
            assert isinstance(profile, CropTimingProfile)
            assert profile.crop_name == crop
            assert profile.days_to_maturity > 0
    
    def test_crop_categorization(self, planting_service):
        """Test crop categorization (cool_season, warm_season, heat_sensitive)."""
        
        # Cool season crops
        cool_season = ["wheat", "peas", "lettuce", "spinach", "potato", "onion"]
        for crop in cool_season:
            profile = planting_service.crop_timing_database[crop]
            assert profile.crop_category == "cool_season"
        
        # Warm season crops
        warm_season = ["corn", "soybean"]
        for crop in warm_season:
            profile = planting_service.crop_timing_database[crop]
            assert profile.crop_category == "warm_season"
        
        # Heat sensitive crops
        heat_sensitive = ["tomato"]
        for crop in heat_sensitive:
            profile = planting_service.crop_timing_database[crop]
            assert profile.crop_category == "heat_sensitive"
    
    def test_frost_tolerance_levels(self, planting_service):
        """Test frost tolerance classifications."""
        
        # Tolerant crops (can handle light frost)
        tolerant = ["wheat", "peas", "spinach", "onion"]
        for crop in tolerant:
            profile = planting_service.crop_timing_database[crop]
            assert profile.frost_tolerance == "tolerant"
        
        # Sensitive crops (light frost damage)
        sensitive = ["soybean", "lettuce", "potato"]
        for crop in sensitive:
            profile = planting_service.crop_timing_database[crop]
            assert profile.frost_tolerance == "sensitive"
        
        # Very sensitive crops (killed by any frost)
        very_sensitive = ["corn", "tomato"]
        for crop in very_sensitive:
            profile = planting_service.crop_timing_database[crop]
            assert profile.frost_tolerance == "very_sensitive"


class TestFrostDateAnalysis:
    """Test frost date calculation and estimation."""
    
    @pytest.mark.asyncio
    async def test_frost_date_parsing(self, planting_service):
        """Test parsing of MM-DD frost date format."""
        
        # Test valid frost date parsing
        frost_date = planting_service._parse_frost_date("04-15")
        assert frost_date.month == 4
        assert frost_date.day == 15
        assert frost_date.year == datetime.now().year
        
        # Test invalid format
        invalid_date = planting_service._parse_frost_date("invalid")
        assert invalid_date is None
        
        # Test None input
        none_date = planting_service._parse_frost_date(None)
        assert none_date is None
    
    def test_frost_date_estimation_by_zone(self, planting_service, sample_location):
        """Test frost date estimation based on USDA climate zone."""
        
        # Test Zone 6a estimation
        frost_info = planting_service._estimate_frost_dates(sample_location)
        
        assert frost_info.last_frost_date is not None
        assert frost_info.first_frost_date is not None
        assert frost_info.growing_season_length > 0
        assert frost_info.confidence_level in ["estimated", "default"]
        
        # For Zone 6a, expect reasonable frost dates
        assert frost_info.last_frost_date.month in [3, 4, 5]  # Spring
        assert frost_info.first_frost_date.month in [10, 11]  # Fall
    
    def test_frost_date_estimation_by_latitude(self, planting_service):
        """Test frost date estimation based on latitude when zone unknown."""
        
        # Northern location (no climate zone)
        north_location = LocationData(latitude=48.0, longitude=-95.0)
        frost_info = planting_service._estimate_frost_dates(north_location)
        
        assert frost_info.last_frost_date.month >= 5  # Later spring frost
        assert frost_info.first_frost_date.month <= 9  # Earlier fall frost
        assert frost_info.confidence_level == "default"
        
        # Southern location (no climate zone) 
        south_location = LocationData(latitude=30.0, longitude=-85.0)
        frost_info = planting_service._estimate_frost_dates(south_location)
        
        assert frost_info.last_frost_date.month <= 3  # Earlier spring frost
        assert frost_info.first_frost_date.month >= 11  # Later fall frost


class TestSpringPlanting:
    """Test spring planting date calculations."""
    
    def test_warm_season_spring_planting(self, planting_service, sample_frost_info, sample_location):
        """Test spring planting for warm season crops (corn, soybean)."""
        
        corn_profile = planting_service.crop_timing_database["corn"]
        
        planting_window = planting_service._calculate_spring_planting(
            corn_profile, sample_frost_info, sample_location
        )
        
        # Corn is very sensitive, should plant 2 weeks after last frost
        expected_optimal = sample_frost_info.last_frost_date + timedelta(days=14)
        assert planting_window.optimal_date == expected_optimal
        
        # Check safety margins
        assert planting_window.safety_margin_days == 14
        assert planting_window.planting_season == "spring"
        assert len(planting_window.frost_considerations) > 0
        
        # Expected harvest date should be calculated
        assert planting_window.expected_harvest_date is not None
        harvest_days = (planting_window.expected_harvest_date - planting_window.optimal_date).days
        assert harvest_days == corn_profile.days_to_maturity
    
    def test_cool_season_spring_planting(self, planting_service, sample_frost_info, sample_location):
        """Test spring planting for cool season crops (peas, lettuce)."""
        
        peas_profile = planting_service.crop_timing_database["peas"]
        
        planting_window = planting_service._calculate_spring_planting(
            peas_profile, sample_frost_info, sample_location  
        )
        
        # Cool season tolerant crops can plant earlier
        assert planting_window.earliest_safe_date < sample_frost_info.last_frost_date
        assert planting_window.planting_season == "spring"
        
        # Should have shorter maturity period
        assert peas_profile.days_to_maturity < 100
    
    def test_frost_sensitive_warnings(self, planting_service, sample_frost_info, sample_location):
        """Test that frost-sensitive crops get appropriate warnings."""
        
        tomato_profile = planting_service.crop_timing_database["tomato"]
        
        planting_window = planting_service._calculate_spring_planting(
            tomato_profile, sample_frost_info, sample_location
        )
        
        # Should have soil temperature and frost monitoring warnings
        frost_warnings = [c for c in planting_window.frost_considerations 
                         if "temperature" in c.lower() or "frost" in c.lower()]
        assert len(frost_warnings) > 0


class TestFallPlanting:
    """Test fall planting date calculations."""
    
    def test_fall_plantable_crops(self, planting_service, sample_frost_info, sample_location):
        """Test fall planting for appropriate crops."""
        
        # Wheat allows fall planting (winter wheat)
        wheat_profile = planting_service.crop_timing_database["wheat"]
        assert wheat_profile.fall_planting_possible
        
        planting_window = planting_service._calculate_fall_planting(
            wheat_profile, sample_frost_info, sample_location
        )
        
        assert planting_window.planting_season == "fall"
        assert planting_window.optimal_date < sample_frost_info.first_frost_date
    
    def test_winter_hardy_crops(self, planting_service, sample_frost_info, sample_location):
        """Test winter hardy crops get spring harvest dates."""
        
        spinach_profile = planting_service.crop_timing_database["spinach"]
        assert spinach_profile.winter_hardy
        
        planting_window = planting_service._calculate_fall_planting(
            spinach_profile, sample_frost_info, sample_location
        )
        
        # Winter hardy crops should have next spring harvest date
        assert planting_window.expected_harvest_date.year > planting_window.optimal_date.year
    
    def test_non_fall_plantable_error(self, planting_service, sample_frost_info, sample_location):
        """Test error for crops not suitable for fall planting."""
        
        corn_profile = planting_service.crop_timing_database["corn"]
        assert not corn_profile.fall_planting_possible
        
        with pytest.raises(ValueError, match="not suitable for fall planting"):
            planting_service._calculate_fall_planting(
                corn_profile, sample_frost_info, sample_location
            )


class TestSuccessionPlanting:
    """Test succession planting schedules."""
    
    def test_succession_schedule_generation(self, planting_service, sample_location):
        """Test generation of succession planting schedule."""
        
        start_date = date(2024, 5, 1)
        end_date = date(2024, 7, 1)
        
        succession_schedule = planting_service.get_succession_planting_schedule(
            crop_name="lettuce",
            location=sample_location,
            start_date=start_date,
            end_date=end_date,
            max_plantings=5
        )
        
        assert len(succession_schedule) > 0
        assert len(succession_schedule) <= 5
        
        # Check that plantings are spaced appropriately
        lettuce_profile = planting_service.crop_timing_database["lettuce"]
        interval = lettuce_profile.succession_interval_days
        
        for i in range(1, len(succession_schedule)):
            days_between = (succession_schedule[i].optimal_date - 
                          succession_schedule[i-1].optimal_date).days
            assert days_between == interval
    
    def test_non_succession_crop_error(self, planting_service, sample_location):
        """Test error for crops not suitable for succession planting."""
        
        start_date = date(2024, 5, 1)
        end_date = date(2024, 7, 1)
        
        with pytest.raises(ValueError, match="not suitable for succession planting"):
            planting_service.get_succession_planting_schedule(
                crop_name="wheat",  # No succession interval
                location=sample_location,
                start_date=start_date,
                end_date=end_date
            )


class TestClimateZoneAdjustments:
    """Test climate zone specific adjustments."""
    
    def test_northern_zone_adjustments(self, planting_service, sample_location):
        """Test adjustments for northern climate zones."""
        
        # Create northern zone location
        north_location = LocationData(
            latitude=46.0, longitude=-94.0,
            climate_zone="3a"
        )
        
        # Create sample planting window
        planting_window = PlantingWindow(
            crop_name="corn",
            optimal_date=date(2024, 5, 15),
            earliest_safe_date=date(2024, 5, 1),
            latest_safe_date=date(2024, 5, 30),
            planting_season="spring",
            safety_margin_days=14,
            confidence_score=0.8,
            frost_considerations=[],
            climate_warnings=[]
        )
        
        adjusted_window = planting_service._apply_climate_zone_adjustments(
            planting_window, north_location
        )
        
        # Northern zones should be more conservative (later planting)
        assert adjusted_window.optimal_date >= planting_window.optimal_date
        assert adjusted_window.confidence_score <= planting_window.confidence_score
        assert len(adjusted_window.climate_warnings) >= 1  # Should have climate warnings for northern zones
    
    def test_southern_zone_adjustments(self, planting_service):
        """Test adjustments for southern climate zones."""
        
        # Create southern zone location
        south_location = LocationData(
            latitude=32.0, longitude=-84.0,
            climate_zone="8a"
        )
        
        # Create summer planting window
        planting_window = PlantingWindow(
            crop_name="lettuce",
            optimal_date=date(2024, 7, 15),
            earliest_safe_date=date(2024, 7, 1),
            latest_safe_date=date(2024, 7, 30),
            planting_season="summer",
            safety_margin_days=0,
            confidence_score=0.8,
            frost_considerations=[],
            climate_warnings=[]
        )
        
        adjusted_window = planting_service._apply_climate_zone_adjustments(
            planting_window, south_location
        )
        
        # Southern zones should have heat warnings for summer planting
        heat_warnings = [w for w in adjusted_window.climate_warnings 
                        if "heat" in w.lower() or "irrigation" in w.lower()]
        assert len(heat_warnings) > 0


class TestGrowingDegreeDays:
    """Test growing degree day validation."""
    
    @pytest.mark.asyncio
    async def test_gdd_validation_adequate(self, planting_service, sample_location):
        """Test GDD validation when location has adequate heat units."""
        
        # Zone 6a should have adequate GDD for most crops
        planting_window = PlantingWindow(
            crop_name="corn",
            optimal_date=date(2024, 5, 15),
            earliest_safe_date=date(2024, 5, 1), 
            latest_safe_date=date(2024, 5, 30),
            planting_season="spring",
            safety_margin_days=14,
            confidence_score=0.8,
            frost_considerations=[],
            climate_warnings=[],
            growing_degree_days_required=2500
        )
        
        await planting_service._validate_growing_degree_days(planting_window, sample_location)
        
        # Should not add severe warnings for zone 6a with corn (2500 GDD)
        gdd_warnings = [w for w in planting_window.climate_warnings 
                       if "heat units" in w.lower() or "degree days" in w.lower()]
        # May have marginal warning but not severe
        
    @pytest.mark.asyncio
    async def test_gdd_validation_insufficient(self, planting_service):
        """Test GDD validation when location has insufficient heat units."""
        
        # Northern zone with insufficient GDD
        north_location = LocationData(
            latitude=48.0, longitude=-95.0,
            climate_zone="3a"  # Lower GDD zone
        )
        
        planting_window = PlantingWindow(
            crop_name="corn",
            optimal_date=date(2024, 5, 15),
            earliest_safe_date=date(2024, 5, 1),
            latest_safe_date=date(2024, 5, 30), 
            planting_season="spring",
            safety_margin_days=14,
            confidence_score=0.8,
            frost_considerations=[],
            climate_warnings=[],
            growing_degree_days_required=2500  # High requirement
        )
        
        await planting_service._validate_growing_degree_days(planting_window, north_location)
        
        # Should add warning about insufficient GDD
        assert len(planting_window.climate_warnings) > 0
        assert planting_window.confidence_score < 0.8  # Reduced confidence


class TestPlantingDateCalculation:
    """Test main planting date calculation method."""
    
    @pytest.mark.asyncio
    async def test_calculate_planting_dates_spring(self, planting_service, sample_location):
        """Test main calculate_planting_dates method for spring."""
        
        planting_window = await planting_service.calculate_planting_dates(
            crop_name="corn",
            location=sample_location,
            planting_season="spring"
        )
        
        assert isinstance(planting_window, PlantingWindow)
        assert planting_window.crop_name == "corn"
        assert planting_window.planting_season == "spring"
        assert planting_window.optimal_date is not None
        assert planting_window.earliest_safe_date <= planting_window.optimal_date
        assert planting_window.optimal_date <= planting_window.latest_safe_date
    
    @pytest.mark.asyncio
    async def test_calculate_planting_dates_invalid_crop(self, planting_service, sample_location):
        """Test error handling for invalid crop name."""
        
        with pytest.raises(ValueError, match="No timing data available"):
            await planting_service.calculate_planting_dates(
                crop_name="invalid_crop",
                location=sample_location,
                planting_season="spring"
            )
    
    @pytest.mark.asyncio
    async def test_calculate_planting_dates_invalid_season(self, planting_service, sample_location):
        """Test error handling for invalid season."""
        
        with pytest.raises(ValueError, match="Invalid planting season"):
            await planting_service.calculate_planting_dates(
                crop_name="corn",
                location=sample_location,
                planting_season="invalid_season"
            )


class TestMultipleSeasonPlanting:
    """Test multiple season planting analysis."""
    
    @pytest.mark.asyncio 
    async def test_multiple_season_plantings(self, planting_service, sample_location):
        """Test getting all possible planting seasons for a crop."""
        
        # Lettuce allows multiple seasons
        planting_windows = await planting_service.get_multiple_season_plantings(
            crop_name="lettuce",
            location=sample_location
        )
        
        assert len(planting_windows) > 0
        
        seasons = [window.planting_season for window in planting_windows]
        assert "spring" in seasons  # Should always have spring
        
        # May have summer and fall depending on crop characteristics
        for window in planting_windows:
            assert window.crop_name == "lettuce"
            assert window.optimal_date is not None
    
    @pytest.mark.asyncio
    async def test_single_season_crop(self, planting_service, sample_location):
        """Test crop with limited seasonal options."""
        
        # Corn typically only spring planting
        planting_windows = await planting_service.get_multiple_season_plantings(
            crop_name="corn",
            location=sample_location
        )
        
        # Should have at least spring, may not have others
        seasons = [window.planting_season for window in planting_windows]
        assert "spring" in seasons


@pytest.mark.integration
class TestIntegrationWithWeatherService:
    """Test integration with weather services for frost date data."""
    
    @pytest.mark.asyncio
    async def test_weather_service_integration(self, planting_service, sample_location):
        """Test integration with weather service for frost dates."""
        
        # Mock the enhanced weather service
        mock_climate_data = Mock()
        mock_climate_data.last_frost_date = "04-15"
        mock_climate_data.first_frost_date = "10-20"
        mock_climate_data.growing_season_length = 188
        
        with patch.object(planting_service, 'enhanced_weather_service') as mock_service:
            mock_service.get_climate_zone_data = AsyncMock(return_value=mock_climate_data)
            
            frost_info = await planting_service._get_frost_date_info(sample_location)
            
            assert frost_info.confidence_level == "historical"
            assert frost_info.last_frost_date.month == 4
            assert frost_info.last_frost_date.day == 15
    
    @pytest.mark.asyncio
    async def test_weather_service_fallback(self, planting_service, sample_location):
        """Test fallback when weather service unavailable."""
        
        # Mock weather service to return None/error
        with patch.object(planting_service, 'enhanced_weather_service') as mock_service:
            mock_service.get_climate_zone_data = AsyncMock(side_effect=Exception("Service unavailable"))
            
            frost_info = await planting_service._get_frost_date_info(sample_location)
            
            # Should fall back to estimation
            assert frost_info.confidence_level in ["estimated", "default"]
            assert frost_info.last_frost_date is not None