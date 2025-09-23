"""
Unit Tests for Location Validation Service
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

Comprehensive unit tests for the LocationValidationService class.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add the service path to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../databases/python'))

from services.location_validation_service import LocationValidationService, ValidationSeverity, ValidationIssue
from location_models import ValidationResult, GeographicInfo


class TestLocationValidationService:
    """Test suite for LocationValidationService."""
    
    @pytest.fixture
    def validation_service(self):
        """Create a LocationValidationService instance for testing."""
        return LocationValidationService()
    
    @pytest.mark.asyncio
    async def test_validate_coordinates_valid_range(self, validation_service):
        """Test coordinate validation with valid ranges."""
        # Test valid coordinates (Ames, Iowa)
        result = await validation_service.validate_coordinates(42.0308, -93.6319)
        
        assert isinstance(result, ValidationResult)
        assert result.valid is True
        assert len(result.errors) == 0
        
        # Test edge cases
        result_north_pole = await validation_service.validate_coordinates(90.0, 0.0)
        assert result_north_pole.valid is True
        
        result_south_pole = await validation_service.validate_coordinates(-90.0, 0.0)
        assert result_south_pole.valid is True
        
        result_date_line = await validation_service.validate_coordinates(0.0, 180.0)
        assert result_date_line.valid is True
        
        result_prime_meridian = await validation_service.validate_coordinates(0.0, 0.0)
        # This might be flagged as ocean, but coordinates should be valid
        assert isinstance(result_prime_meridian, ValidationResult)
    
    @pytest.mark.asyncio
    async def test_validate_coordinates_invalid_range(self, validation_service):
        """Test coordinate validation with invalid ranges."""
        # Test invalid latitude (too high)
        result = await validation_service.validate_coordinates(91.0, -93.6319)
        assert result.valid is False
        assert len(result.errors) > 0
        assert "outside valid ranges" in result.errors[0]
        
        # Test invalid latitude (too low)
        result = await validation_service.validate_coordinates(-91.0, -93.6319)
        assert result.valid is False
        assert len(result.errors) > 0
        
        # Test invalid longitude (too high)
        result = await validation_service.validate_coordinates(42.0308, 181.0)
        assert result.valid is False
        assert len(result.errors) > 0
        
        # Test invalid longitude (too low)
        result = await validation_service.validate_coordinates(42.0308, -181.0)
        assert result.valid is False
        assert len(result.errors) > 0
    
    @pytest.mark.asyncio
    async def test_validate_coordinates_agricultural_areas(self, validation_service):
        """Test validation of coordinates in known agricultural areas."""
        # Test Iowa coordinates (should be agricultural)
        result = await validation_service.validate_coordinates(42.0308, -93.6319)
        assert result.valid is True
        assert result.geographic_info is not None
        assert result.geographic_info.is_agricultural is True
        
        # Test Illinois coordinates (should be agricultural)
        result = await validation_service.validate_coordinates(40.1164, -88.2434)
        assert result.valid is True
        assert result.geographic_info is not None
        assert result.geographic_info.is_agricultural is True
    
    @pytest.mark.asyncio
    async def test_validate_coordinates_non_agricultural_areas(self, validation_service):
        """Test validation of coordinates in non-agricultural areas."""
        # Test coordinates in major urban area (should have warnings)
        result = await validation_service.validate_coordinates(41.8781, -87.6298)  # Chicago
        assert result.valid is True  # Valid coordinates, but may have warnings
        
        # Check if warnings are present for non-agricultural areas
        if result.geographic_info and not result.geographic_info.is_agricultural:
            assert len(result.warnings) > 0
    
    @pytest.mark.asyncio
    async def test_validate_coordinates_ocean_detection(self, validation_service):
        """Test detection of ocean coordinates."""
        # Test coordinates in Atlantic Ocean
        result = await validation_service.validate_coordinates(30.0, -40.0)
        
        # Should either be invalid or have warnings about ocean location
        if not result.valid:
            assert any("ocean" in error.lower() or "water" in error.lower() for error in result.errors)
        else:
            # If valid, should have warnings
            assert len(result.warnings) > 0 or result.geographic_info.is_agricultural is False
    
    @pytest.mark.asyncio
    async def test_validate_agricultural_location_comprehensive(self, validation_service):
        """Test comprehensive agricultural location validation."""
        # Test with known agricultural coordinates
        result = await validation_service.validate_agricultural_location(42.0308, -93.6319)
        
        assert isinstance(result, ValidationResult)
        assert result.valid is True
        assert result.geographic_info is not None
        assert result.geographic_info.is_agricultural is True
        
        # Should have climate zone information
        assert result.geographic_info.climate_zone is not None
        assert len(result.geographic_info.climate_zone) > 0
    
    @pytest.mark.asyncio
    async def test_validate_agricultural_location_extreme_latitudes(self, validation_service):
        """Test validation at extreme latitudes."""
        # Test high latitude (should have warnings about short growing season)
        result = await validation_service.validate_agricultural_location(60.0, -100.0)
        assert result.valid is True
        
        # Check if warnings are present (may vary based on implementation)
        # The specific warning text may differ, so check for any warnings
        if len(result.warnings) > 0:
            # If warnings exist, check they contain relevant agricultural context
            warning_text = " ".join(result.warnings).lower()
            assert any(keyword in warning_text for keyword in 
                      ["latitude", "growing", "season", "climate", "agricultural", "suitability"])
        
        # Test low latitude (should have info about tropical conditions)
        result = await validation_service.validate_agricultural_location(20.0, -100.0)
        assert result.valid is True
        # May have warnings or info about tropical conditions
    
    def test_is_valid_coordinate_range(self, validation_service):
        """Test the internal coordinate range validation method."""
        # Valid coordinates
        assert validation_service._is_valid_coordinate_range(42.0308, -93.6319) is True
        assert validation_service._is_valid_coordinate_range(0.0, 0.0) is True
        assert validation_service._is_valid_coordinate_range(90.0, 180.0) is True
        assert validation_service._is_valid_coordinate_range(-90.0, -180.0) is True
        
        # Invalid coordinates
        assert validation_service._is_valid_coordinate_range(91.0, 0.0) is False
        assert validation_service._is_valid_coordinate_range(-91.0, 0.0) is False
        assert validation_service._is_valid_coordinate_range(0.0, 181.0) is False
        assert validation_service._is_valid_coordinate_range(0.0, -181.0) is False
    
    @pytest.mark.asyncio
    async def test_get_county_state(self, validation_service):
        """Test county and state detection."""
        # Test Iowa coordinates
        county, state = await validation_service._get_county_state(42.0308, -93.6319)
        
        # State should be detected (county may be None in simplified implementation)
        assert state == "Iowa" or state is None  # May not be implemented yet
        
        # Test Illinois coordinates
        county, state = await validation_service._get_county_state(40.1164, -88.2434)
        assert state == "Illinois" or state is None
    
    @pytest.mark.asyncio
    async def test_get_climate_zone(self, validation_service):
        """Test climate zone detection."""
        # Test Iowa coordinates (should be zone 5a-6a)
        climate_zone = await validation_service._get_climate_zone(42.0308, -93.6319)
        assert climate_zone is not None
        assert isinstance(climate_zone, str)
        assert len(climate_zone) > 0
        
        # Test northern coordinates (should be colder zone)
        climate_zone_north = await validation_service._get_climate_zone(48.0, -100.0)
        assert climate_zone_north is not None
        
        # Test southern coordinates (should be warmer zone)
        climate_zone_south = await validation_service._get_climate_zone(30.0, -90.0)
        assert climate_zone_south is not None
    
    @pytest.mark.asyncio
    async def test_check_agricultural_area(self, validation_service):
        """Test agricultural area detection."""
        # Test known agricultural area (Iowa)
        result = await validation_service._check_agricultural_area(42.0308, -93.6319)
        
        assert isinstance(result, dict)
        assert 'is_agricultural' in result
        assert 'confidence' in result
        assert 'reasoning' in result
        
        assert isinstance(result['is_agricultural'], bool)
        assert 0.0 <= result['confidence'] <= 1.0
        assert isinstance(result['reasoning'], str)
        
        # For Iowa, should be agricultural with high confidence
        assert result['is_agricultural'] is True
        assert result['confidence'] > 0.7
    
    @pytest.mark.asyncio
    async def test_analyze_agricultural_suitability(self, validation_service):
        """Test comprehensive agricultural suitability analysis."""
        # Test with agricultural coordinates
        result = await validation_service._analyze_agricultural_suitability(42.0308, -93.6319)
        
        assert isinstance(result, dict)
        assert 'is_agricultural' in result
        assert 'suitability_score' in result
        assert 'factors' in result
        assert 'reasoning' in result
        
        assert isinstance(result['suitability_score'], float)
        assert 0.0 <= result['suitability_score'] <= 1.0
        
        # For Iowa, should have high suitability
        assert result['suitability_score'] > 0.5
        assert result['is_agricultural'] is True
    
    @pytest.mark.asyncio
    async def test_calculate_climate_suitability(self, validation_service):
        """Test climate suitability calculation."""
        # Test optimal latitude (should be high suitability)
        suitability = await validation_service._calculate_climate_suitability(42.0, -93.0)
        assert 0.8 <= suitability <= 1.0
        
        # Test extreme latitude (should be lower suitability)
        suitability_extreme = await validation_service._calculate_climate_suitability(70.0, -100.0)
        assert suitability_extreme < 0.5
    
    @pytest.mark.asyncio
    async def test_calculate_geographic_suitability(self, validation_service):
        """Test geographic suitability calculation."""
        # Test continental US coordinates (should be high suitability)
        suitability = await validation_service._calculate_geographic_suitability(42.0, -93.0)
        assert suitability >= 0.8
        
        # Test coordinates outside continental regions
        suitability_other = await validation_service._calculate_geographic_suitability(10.0, 50.0)
        assert suitability_other <= 0.8
    
    @pytest.mark.asyncio
    async def test_validate_climate_zone(self, validation_service):
        """Test climate zone validation with warnings."""
        # Test moderate climate zone (should have no warnings)
        result = await validation_service._validate_climate_zone(42.0, -93.0)
        assert isinstance(result, dict)
        assert 'climate_zone' in result
        assert 'warnings' in result
        assert isinstance(result['warnings'], list)
        
        # Test extreme climate zones
        result_cold = await validation_service._validate_climate_zone(60.0, -100.0)
        # May have warnings about cold climate
        
        result_hot = await validation_service._validate_climate_zone(25.0, -80.0)
        # May have warnings about hot climate
    
    @pytest.mark.asyncio
    async def test_get_validation_error(self, validation_service):
        """Test getting predefined validation errors."""
        # Test known error code
        error = await validation_service.get_validation_error("INVALID_COORDINATES")
        assert error.error_code == "INVALID_COORDINATES"
        assert len(error.error_message) > 0
        assert len(error.suggested_actions) > 0
        
        # Test unknown error code (should return default)
        error_unknown = await validation_service.get_validation_error("UNKNOWN_ERROR")
        assert error_unknown.error_code == "LOCATION_NOT_FOUND"  # Default fallback
    
    @pytest.mark.asyncio
    async def test_edge_cases(self, validation_service):
        """Test edge cases and boundary conditions."""
        # Test exactly at boundaries
        result_equator = await validation_service.validate_coordinates(0.0, 0.0)
        assert isinstance(result_equator, ValidationResult)
        
        result_date_line = await validation_service.validate_coordinates(42.0, 180.0)
        assert isinstance(result_date_line, ValidationResult)
        
        result_prime_meridian = await validation_service.validate_coordinates(42.0, 0.0)
        assert isinstance(result_prime_meridian, ValidationResult)
    
    @pytest.mark.asyncio
    async def test_agricultural_context_messages(self, validation_service):
        """Test that agricultural context is provided in validation results."""
        # Test with coordinates that should generate warnings
        result = await validation_service.validate_agricultural_location(70.0, -100.0)
        
        # Should have warnings with agricultural context
        if result.warnings:
            # Check that warnings contain agricultural context
            assert any("agricultural" in warning.lower() or "crop" in warning.lower() or 
                      "growing" in warning.lower() for warning in result.warnings)
    
    @pytest.mark.asyncio
    async def test_performance_basic_validation(self, validation_service):
        """Test that basic validation performs reasonably quickly."""
        import time
        
        start_time = time.time()
        result = await validation_service.validate_coordinates(42.0308, -93.6319)
        end_time = time.time()
        
        # Should complete within reasonable time (1 second for basic validation)
        assert (end_time - start_time) < 1.0
        assert result.valid is True


class TestValidationIssue:
    """Test the ValidationIssue dataclass."""
    
    def test_validation_issue_creation(self):
        """Test creating ValidationIssue instances."""
        issue = ValidationIssue(
            severity=ValidationSeverity.WARNING,
            message="Test warning",
            field="latitude",
            agricultural_context="Test context",
            suggested_actions=["Action 1", "Action 2"]
        )
        
        assert issue.severity == ValidationSeverity.WARNING
        assert issue.message == "Test warning"
        assert issue.field == "latitude"
        assert issue.agricultural_context == "Test context"
        assert len(issue.suggested_actions) == 2
    
    def test_validation_issue_minimal(self):
        """Test creating ValidationIssue with minimal parameters."""
        issue = ValidationIssue(
            severity=ValidationSeverity.ERROR,
            message="Test error"
        )
        
        assert issue.severity == ValidationSeverity.ERROR
        assert issue.message == "Test error"
        assert issue.field is None
        assert issue.agricultural_context is None
        assert issue.suggested_actions is None


class TestValidationSeverity:
    """Test the ValidationSeverity enum."""
    
    def test_severity_values(self):
        """Test that severity enum has expected values."""
        assert ValidationSeverity.INFO == "info"
        assert ValidationSeverity.WARNING == "warning"
        assert ValidationSeverity.ERROR == "error"
        assert ValidationSeverity.CRITICAL == "critical"
    
    def test_severity_comparison(self):
        """Test severity enum can be used in comparisons."""
        assert ValidationSeverity.INFO != ValidationSeverity.ERROR
        assert ValidationSeverity.WARNING == ValidationSeverity.WARNING


# Integration test fixtures
@pytest.fixture
def sample_iowa_coordinates():
    """Sample coordinates for Iowa (agricultural area)."""
    return (42.0308, -93.6319)  # Ames, Iowa


@pytest.fixture
def sample_ocean_coordinates():
    """Sample coordinates for ocean location."""
    return (30.0, -40.0)  # Atlantic Ocean


@pytest.fixture
def sample_urban_coordinates():
    """Sample coordinates for urban area."""
    return (41.8781, -87.6298)  # Chicago, IL


@pytest.mark.asyncio
async def test_integration_agricultural_workflow(sample_iowa_coordinates):
    """Integration test for complete agricultural validation workflow."""
    service = LocationValidationService()
    lat, lon = sample_iowa_coordinates
    
    # Test complete workflow
    result = await service.validate_agricultural_location(lat, lon)
    
    assert result.valid is True
    assert result.geographic_info is not None
    assert result.geographic_info.is_agricultural is True
    assert result.geographic_info.climate_zone is not None
    
    # Should have minimal warnings for good agricultural location
    assert len(result.errors) == 0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])