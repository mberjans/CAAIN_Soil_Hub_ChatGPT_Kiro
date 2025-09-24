"""
Tests for Climate Zone Detection Service
Comprehensive test suite for climate zone detection functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from ..src.services.climate_zone_service import (
    ClimateZoneService, ClimateZone, ClimateZoneType, ClimateDetectionResult
)
from ..src.services.coordinate_climate_detector import (
    CoordinateClimateDetector, CoordinateClimateData
)
from ..src.services.usda_zone_api import USDAZoneAPI, USDAZoneData
from ..src.services.koppen_climate_service import (
    KoppenClimateService, KoppenClimate, ClimateAnalysis, KoppenGroup
)


class TestClimateZoneService:
    """Test climate zone service functionality."""
    
    @pytest.fixture
    def climate_service(self):
        """Create climate zone service instance."""
        return ClimateZoneService()
    
    def test_usda_zones_initialization(self, climate_service):
        """Test USDA zones are properly initialized."""
        usda_zones = climate_service.usda_zones
        
        # Should have all major USDA zones
        assert "1a" in usda_zones
        assert "6a" in usda_zones
        assert "10a" in usda_zones
        assert "13a" in usda_zones
        
        # Check zone properties
        zone_6a = usda_zones["6a"]
        assert zone_6a.zone_type == ClimateZoneType.USDA_HARDINESS
        assert zone_6a.min_temp_f == -10
        assert zone_6a.max_temp_f == -5
        assert "suitable_for" in zone_6a.characteristics
    
    def test_koppen_types_initialization(self, climate_service):
        """Test Köppen climate types are properly initialized."""
        koppen_types = climate_service.koppen_types
        
        # Should have major Köppen types
        assert "Af" in koppen_types  # Tropical rainforest
        assert "BWh" in koppen_types  # Hot desert
        assert "Cfa" in koppen_types  # Humid subtropical
        assert "Dfb" in koppen_types  # Warm continental
        assert "ET" in koppen_types   # Tundra
        
        # Check type properties
        cfa_type = koppen_types["Cfa"]
        assert cfa_type.zone_type == ClimateZoneType.KOPPEN
        assert cfa_type.name == "Köppen Cfa - Humid Subtropical"
        assert "agricultural_suitability" in cfa_type.characteristics
    
    def test_agricultural_zones_initialization(self, climate_service):
        """Test agricultural zones are properly initialized."""
        ag_zones = climate_service.agricultural_zones
        
        # Should have major agricultural zones
        assert "corn_belt" in ag_zones
        assert "wheat_belt" in ag_zones
        assert "cotton_belt" in ag_zones
        
        # Check zone properties
        corn_belt = ag_zones["corn_belt"]
        assert corn_belt.zone_type == ClimateZoneType.AGRICULTURAL
        assert corn_belt.growing_season_days > 0
        assert "primary_crops" in corn_belt.characteristics
    
    @pytest.mark.asyncio
    async def test_detect_climate_zone_iowa(self, climate_service):
        """Test climate zone detection for Iowa coordinates."""
        # Ames, Iowa coordinates
        latitude, longitude = 42.0308, -93.6319
        
        result = await climate_service.detect_climate_zone(latitude, longitude)
        
        assert isinstance(result, ClimateDetectionResult)
        assert result.coordinates == (latitude, longitude)
        assert result.confidence_score > 0.5
        
        # Should detect appropriate zone for Iowa
        assert result.primary_zone.zone_id in ["5a", "5b", "6a"]
        assert len(result.alternative_zones) > 0
    
    @pytest.mark.asyncio
    async def test_detect_climate_zone_with_elevation(self, climate_service):
        """Test climate zone detection with elevation adjustment."""
        # Denver, Colorado (high elevation)
        latitude, longitude, elevation = 39.7392, -104.9903, 5280
        
        result = await climate_service.detect_climate_zone(latitude, longitude, elevation)
        
        assert result.elevation_ft == elevation
        # High elevation should result in colder zone than latitude alone would suggest
        assert result.primary_zone.zone_id in ["4a", "4b", "5a", "5b"]
    
    def test_get_zone_by_id(self, climate_service):
        """Test getting zone by ID and type."""
        # Test USDA zone
        usda_zone = climate_service.get_zone_by_id("6a", ClimateZoneType.USDA_HARDINESS)
        assert usda_zone is not None
        assert usda_zone.zone_id == "6a"
        
        # Test Köppen type
        koppen_zone = climate_service.get_zone_by_id("Cfa", ClimateZoneType.KOPPEN)
        assert koppen_zone is not None
        assert koppen_zone.zone_id == "Cfa"
        
        # Test non-existent zone
        invalid_zone = climate_service.get_zone_by_id("invalid", ClimateZoneType.USDA_HARDINESS)
        assert invalid_zone is None
    
    def test_list_zones(self, climate_service):
        """Test listing zones by type."""
        # List USDA zones
        usda_zones = climate_service.list_zones(ClimateZoneType.USDA_HARDINESS)
        assert len(usda_zones) > 20  # Should have many USDA zones
        assert all(zone.zone_type == ClimateZoneType.USDA_HARDINESS for zone in usda_zones)
        
        # List all zones
        all_zones = climate_service.list_zones()
        assert len(all_zones) > len(usda_zones)  # Should include all types
    
    @pytest.mark.asyncio
    async def test_validate_zone_for_location(self, climate_service):
        """Test zone validation for location."""
        # Test valid zone for Iowa
        result = await climate_service.validate_zone_for_location(
            zone_id="5a",
            zone_type=ClimateZoneType.USDA_HARDINESS,
            latitude=42.0308,
            longitude=-93.6319
        )
        
        assert "valid" in result
        assert "confidence" in result
        assert "message" in result
        assert "detected_zone" in result
        
        # Test invalid zone for Iowa (tropical zone)
        result = await climate_service.validate_zone_for_location(
            zone_id="10a",
            zone_type=ClimateZoneType.USDA_HARDINESS,
            latitude=42.0308,
            longitude=-93.6319
        )
        
        assert result["valid"] is False
        assert result["confidence"] < 0.5


class TestUSDAZoneAPI:
    """Test USDA Zone API functionality."""
    
    @pytest.fixture
    def usda_api(self):
        """Create USDA API instance."""
        return USDAZoneAPI()
    
    @pytest.mark.asyncio
    async def test_get_zone_by_coordinates(self, usda_api):
        """Test getting USDA zone by coordinates."""
        # Test with Iowa coordinates
        latitude, longitude = 42.0308, -93.6319
        
        async with usda_api as api:
            zone_data = await api.get_zone_by_coordinates(latitude, longitude)
        
        assert zone_data is not None
        assert isinstance(zone_data, USDAZoneData)
        assert zone_data.coordinates == (latitude, longitude)
        assert zone_data.zone in ["4a", "4b", "5a", "5b", "6a"]  # Reasonable for Iowa
        assert zone_data.confidence > 0.0
    
    @pytest.mark.asyncio
    async def test_get_zone_details(self, usda_api):
        """Test getting detailed zone information."""
        zone_details = await usda_api.get_zone_details("6a")
        
        assert zone_details is not None
        assert zone_details["zone"] == "6a"
        assert "temperature_range_f" in zone_details
        assert "temperature_range_c" in zone_details
        assert "description" in zone_details
        assert "suitable_plants" in zone_details
    
    def test_estimate_zone_from_coordinates(self, usda_api):
        """Test zone estimation from coordinates."""
        # Test various latitudes
        test_cases = [
            (25.0, "9a"),   # Florida
            (35.0, "7a"),   # North Carolina
            (45.0, "5a"),   # Minnesota
            (55.0, "3a"),   # Northern Canada
        ]
        
        for latitude, expected_zone_range in test_cases:
            zone = usda_api._estimate_zone_from_coordinates(latitude, -100)
            # Zone should be in reasonable range
            assert zone[0] in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
    
    def test_temperature_range_for_zone(self, usda_api):
        """Test temperature range calculation for zones."""
        temp_range = usda_api._get_temperature_range_for_zone("6a")
        assert temp_range == (-10, -5)
        
        temp_range = usda_api._get_temperature_range_for_zone("9a")
        assert temp_range == (20, 25)
    
    def test_zone_description(self, usda_api):
        """Test zone description generation."""
        description = usda_api._get_zone_description("6a")
        assert "temperate" in description.lower()
        assert "growing" in description.lower()
    
    def test_suitable_plants(self, usda_api):
        """Test suitable plants for zones."""
        plants = usda_api._get_suitable_plants("6a")
        assert isinstance(plants, list)
        assert len(plants) > 0
        assert "vegetables" in plants or "fruit_trees" in plants
    
    def test_frost_dates(self, usda_api):
        """Test frost date estimation."""
        frost_dates = usda_api._estimate_frost_dates("6a")
        assert "last_spring" in frost_dates
        assert "first_fall" in frost_dates
        assert isinstance(frost_dates["last_spring"], str)


class TestKoppenClimateService:
    """Test Köppen climate service functionality."""
    
    @pytest.fixture
    def koppen_service(self):
        """Create Köppen climate service instance."""
        return KoppenClimateService()
    
    def test_climate_types_initialization(self, koppen_service):
        """Test Köppen climate types initialization."""
        climate_types = koppen_service.climate_types
        
        # Should have all major Köppen types
        assert len(climate_types) > 25
        assert "Af" in climate_types
        assert "BWh" in climate_types
        assert "Cfa" in climate_types
        assert "Dfb" in climate_types
        assert "ET" in climate_types
        
        # Check type properties
        af_type = climate_types["Af"]
        assert af_type.group == KoppenGroup.TROPICAL
        assert af_type.growing_season_months > 10
    
    @pytest.mark.asyncio
    async def test_classify_climate_tropical(self, koppen_service):
        """Test Köppen classification for tropical location."""
        # Miami, Florida
        latitude, longitude = 25.7617, -80.1918
        
        analysis = await koppen_service.classify_climate(latitude, longitude)
        
        assert isinstance(analysis, ClimateAnalysis)
        assert analysis.koppen_type.group == KoppenGroup.TROPICAL
        assert analysis.confidence > 0.5
        assert analysis.koppen_type.code in ["Af", "Am", "Aw"]
    
    @pytest.mark.asyncio
    async def test_classify_climate_continental(self, koppen_service):
        """Test Köppen classification for continental location."""
        # Minneapolis, Minnesota
        latitude, longitude = 44.9778, -93.2650
        
        analysis = await koppen_service.classify_climate(latitude, longitude)
        
        assert analysis.koppen_type.group in [KoppenGroup.CONTINENTAL, KoppenGroup.TEMPERATE]
        assert analysis.confidence > 0.5
    
    @pytest.mark.asyncio
    async def test_classify_climate_arid(self, koppen_service):
        """Test Köppen classification for arid location."""
        # Phoenix, Arizona
        latitude, longitude = 33.4484, -112.0740
        
        analysis = await koppen_service.classify_climate(latitude, longitude)
        
        assert analysis.koppen_type.group == KoppenGroup.ARID
        assert analysis.koppen_type.code in ["BWh", "BSh"]
    
    def test_estimate_climate_data(self, koppen_service):
        """Test climate data estimation from coordinates."""
        # Test tropical location
        temp_data, precip_data = koppen_service._estimate_climate_data(10.0, -80.0)
        assert temp_data["coldest_month"] > 18  # Tropical threshold
        assert precip_data["annual_total"] > 1000
        
        # Test polar location
        temp_data, precip_data = koppen_service._estimate_climate_data(70.0, -100.0)
        assert temp_data["warmest_month"] < 10  # Polar threshold
    
    def test_determine_koppen_code(self, koppen_service):
        """Test Köppen code determination from climate data."""
        # Tropical rainforest conditions
        temp_data = {"coldest_month": 24, "warmest_month": 28, "annual_mean": 26}
        precip_data = {"annual_total": 2000, "driest_month": 100, "wettest_month": 300}
        
        code = koppen_service._determine_koppen_code(temp_data, precip_data)
        assert code == "Af"
        
        # Desert conditions
        temp_data = {"coldest_month": 10, "warmest_month": 40, "annual_mean": 25}
        precip_data = {"annual_total": 200, "driest_month": 5, "wettest_month": 30}
        
        code = koppen_service._determine_koppen_code(temp_data, precip_data)
        assert code in ["BWh", "BWk"]
    
    def test_get_climate_type_by_code(self, koppen_service):
        """Test getting climate type by code."""
        climate_type = koppen_service.get_climate_type_by_code("Cfa")
        assert climate_type is not None
        assert climate_type.code == "Cfa"
        assert climate_type.name == "Köppen Cfa - Humid Subtropical"
        
        # Test invalid code
        invalid_type = koppen_service.get_climate_type_by_code("invalid")
        assert invalid_type is None
    
    def test_list_climate_types(self, koppen_service):
        """Test listing climate types."""
        # List all types
        all_types = koppen_service.list_climate_types()
        assert len(all_types) > 25
        
        # List tropical types only
        tropical_types = koppen_service.list_climate_types(KoppenGroup.TROPICAL)
        assert len(tropical_types) > 0
        assert all(t.group == KoppenGroup.TROPICAL for t in tropical_types)


class TestCoordinateClimateDetector:
    """Test coordinate-based climate detection."""
    
    @pytest.fixture
    def detector(self):
        """Create coordinate climate detector instance."""
        return CoordinateClimateDetector()
    
    @pytest.mark.asyncio
    async def test_detect_climate_comprehensive(self, detector):
        """Test comprehensive climate detection."""
        # Test with Iowa coordinates
        latitude, longitude = 42.0308, -93.6319
        
        climate_data = await detector.detect_climate_from_coordinates(
            latitude, longitude, include_detailed_analysis=True
        )
        
        assert isinstance(climate_data, CoordinateClimateData)
        assert climate_data.coordinates == (latitude, longitude)
        assert climate_data.usda_zone is not None
        assert climate_data.koppen_analysis is not None
        assert climate_data.confidence_factors["overall_confidence"] > 0.5
    
    @pytest.mark.asyncio
    async def test_detect_climate_with_elevation(self, detector):
        """Test climate detection with elevation."""
        # Denver coordinates with elevation
        latitude, longitude, elevation = 39.7392, -104.9903, 5280
        
        climate_data = await detector.detect_climate_from_coordinates(
            latitude, longitude, elevation_ft=elevation
        )
        
        assert climate_data.elevation_data is not None
        assert climate_data.elevation_data.elevation_ft == elevation
        assert climate_data.climate_adjustments["elevation_adjustment_f"] < 0  # Colder at elevation
    
    def test_validate_coordinates(self, detector):
        """Test coordinate validation."""
        # Valid coordinates
        detector._validate_coordinates(42.0, -93.6)  # Should not raise
        
        # Invalid latitude
        with pytest.raises(ValueError):
            detector._validate_coordinates(91.0, -93.6)
        
        # Invalid longitude
        with pytest.raises(ValueError):
            detector._validate_coordinates(42.0, 181.0)
    
    def test_estimate_elevation_from_geography(self, detector):
        """Test elevation estimation."""
        # Rocky Mountains (should be high)
        elevation = detector._estimate_elevation_from_geography(40.0, -110.0)
        assert elevation > 2000
        
        # Coastal area (should be low)
        elevation = detector._estimate_elevation_from_geography(40.0, -75.0)
        assert elevation < 1000
    
    def test_latitude_to_usda_zone(self, detector):
        """Test latitude to USDA zone conversion."""
        # Test various latitudes
        assert detector._latitude_to_usda_zone(25) == "9a"  # Florida
        assert detector._latitude_to_usda_zone(35) == "7a"  # North Carolina
        assert detector._latitude_to_usda_zone(45) == "5a"  # Minnesota
        assert detector._latitude_to_usda_zone(65) == "1a"  # Alaska
    
    def test_adjust_zone_for_elevation(self, detector):
        """Test zone adjustment for elevation."""
        base_zone = USDAZoneData(
            zone="6a",
            temperature_range=(-10, -5),
            description="Base zone",
            coordinates=(40.0, -100.0),
            confidence=0.8,
            source="test"
        )
        
        # High elevation should make it colder (higher zone number)
        adjusted = detector._adjust_zone_for_elevation(base_zone, 3000)
        assert adjusted.zone != "6a"  # Should be different
        assert adjusted.temperature_range[0] < base_zone.temperature_range[0]  # Colder
    
    def test_is_coastal_location(self, detector):
        """Test coastal location detection."""
        # Pacific coast
        assert detector._is_coastal_location(37.7749, -122.4194)  # San Francisco
        
        # Atlantic coast
        assert detector._is_coastal_location(40.7128, -74.0060)   # New York
        
        # Interior location
        assert not detector._is_coastal_location(41.8781, -87.6298)  # Chicago
    
    def test_identify_microclimate_factors(self, detector):
        """Test microclimate factor identification."""
        # Urban location
        factors = detector._identify_microclimate_factors(40.7128, -74.0060, 100)  # NYC
        assert "urban_heat_island" in factors
        
        # High elevation location
        factors = detector._identify_microclimate_factors(39.7392, -104.9903, 5280)  # Denver
        assert "high_elevation_effects" in factors


class TestClimateZoneIntegration:
    """Integration tests for climate zone detection system."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_detection_iowa(self):
        """Test end-to-end climate detection for Iowa farm."""
        detector = CoordinateClimateDetector()
        
        # Typical Iowa farm coordinates
        latitude, longitude = 42.0308, -93.6319
        
        climate_data = await detector.detect_climate_from_coordinates(
            latitude, longitude, include_detailed_analysis=True
        )
        
        # Validate comprehensive results
        assert climate_data.usda_zone is not None
        assert climate_data.usda_zone.zone in ["4b", "5a", "5b", "6a"]  # Reasonable for Iowa
        
        assert climate_data.koppen_analysis is not None
        assert climate_data.koppen_analysis.koppen_type.group in [
            KoppenGroup.TEMPERATE, KoppenGroup.CONTINENTAL
        ]
        
        assert climate_data.confidence_factors["overall_confidence"] > 0.6
        
        # Should have agricultural implications
        if climate_data.koppen_analysis:
            ag_implications = climate_data.koppen_analysis.agricultural_implications
            assert "crop_suitability" in ag_implications
            assert "growing_challenges" in ag_implications
    
    @pytest.mark.asyncio
    async def test_end_to_end_detection_california(self):
        """Test end-to-end climate detection for California farm."""
        detector = CoordinateClimateDetector()
        
        # Central Valley, California coordinates
        latitude, longitude = 36.7783, -119.4179
        
        climate_data = await detector.detect_climate_from_coordinates(
            latitude, longitude, include_detailed_analysis=True
        )
        
        # Validate results for California
        assert climate_data.usda_zone is not None
        assert climate_data.usda_zone.zone in ["8a", "8b", "9a", "9b"]  # Reasonable for Central Valley
        
        assert climate_data.koppen_analysis is not None
        # Central Valley should be Mediterranean or semi-arid
        assert climate_data.koppen_analysis.koppen_type.code in ["Csa", "BSh", "BSk"]
    
    @pytest.mark.asyncio
    async def test_multiple_location_consistency(self):
        """Test consistency across multiple locations."""
        detector = CoordinateClimateDetector()
        
        test_locations = [
            (42.0308, -93.6319),   # Iowa
            (36.7783, -119.4179),  # California
            (44.9778, -93.2650),   # Minnesota
            (29.7604, -95.3698),   # Texas
        ]
        
        results = []
        for lat, lon in test_locations:
            climate_data = await detector.detect_climate_from_coordinates(lat, lon)
            results.append(climate_data)
        
        # All should have valid results
        for result in results:
            assert result.usda_zone is not None
            assert result.confidence_factors["overall_confidence"] > 0.3
            assert result.detection_metadata["detection_time"] is not None
        
        # Results should be different for different locations
        zones = [r.usda_zone.zone for r in results]
        assert len(set(zones)) > 1  # Should have different zones


# Performance tests
class TestClimateZonePerformance:
    """Test performance requirements for climate zone detection."""
    
    @pytest.mark.asyncio
    async def test_detection_response_time(self):
        """Test that climate detection completes within time limits."""
        import time
        
        detector = CoordinateClimateDetector()
        
        start_time = time.time()
        climate_data = await detector.detect_climate_from_coordinates(42.0308, -93.6319)
        response_time = time.time() - start_time
        
        # Should complete within 3 seconds
        assert response_time < 3.0
        assert climate_data.usda_zone is not None
    
    @pytest.mark.asyncio
    async def test_concurrent_detections(self):
        """Test concurrent climate detections."""
        detector = CoordinateClimateDetector()
        
        # Test multiple concurrent requests
        tasks = []
        test_coords = [
            (42.0308, -93.6319),   # Iowa
            (36.7783, -119.4179),  # California
            (44.9778, -93.2650),   # Minnesota
            (29.7604, -95.3698),   # Texas
            (47.6062, -122.3321),  # Washington
        ]
        
        for lat, lon in test_coords:
            task = detector.detect_climate_from_coordinates(lat, lon)
            tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert len(results) == len(test_coords)
        for result in results:
            assert result.usda_zone is not None
            assert result.confidence_factors["overall_confidence"] > 0.3


# Fixtures for test data
@pytest.fixture
def sample_usda_zone_data():
    """Sample USDA zone data for testing."""
    return USDAZoneData(
        zone="6a",
        temperature_range=(-10, -5),
        description="USDA Hardiness Zone 6a",
        coordinates=(42.0, -93.6),
        confidence=0.8,
        source="test_data"
    )


@pytest.fixture
def sample_koppen_climate():
    """Sample Köppen climate data for testing."""
    return KoppenClimate(
        code="Cfa",
        group=KoppenGroup.TEMPERATE,
        name="Humid Subtropical",
        description="Hot humid summers, mild winters",
        temperature_pattern="hot_summer",
        precipitation_pattern="wet_year_round",
        agricultural_suitability="excellent_diverse",
        typical_vegetation=["deciduous_forest", "diverse_crops"],
        growing_season_months=8,
        water_balance="surplus"
    )


# Test configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])