"""
Tests for variety-specific planting date calculations.

This module tests the enhanced planting date service with variety-specific
timing calculations, maturity adjustments, and harvest predictions.
"""

import pytest
import asyncio
from datetime import date, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Dict, Any, List

# Import the service and models
try:
    from src.services.planting_date_service import (
        PlantingDateCalculatorService,
        VarietyTimingProfile,
        VarietyPlantingWindow,
        PlantingWindow,
        FrostDateInfo,
        LocationData
    )
except ImportError:
    # Alternative import path for testing
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
    from services.planting_date_service import (
        PlantingDateCalculatorService,
        VarietyTimingProfile,
        VarietyPlantingWindow,
        PlantingWindow,
        FrostDateInfo,
        LocationData
    )


class TestVarietyPlantingDateCalculations:
    """Test suite for variety-specific planting date calculations."""
    
    @pytest.fixture
    def service(self):
        """Create planting date service instance for testing."""
        return PlantingDateCalculatorService()
    
    @pytest.fixture
    def sample_location(self):
        """Create sample location data for testing."""
        return LocationData(
            latitude=40.0,
            longitude=-95.0,
            address="Test Farm, Iowa",
            state="Iowa",
            county="Test County",
            climate_zone="5a",
            elevation_ft=1000
        )
    
    @pytest.fixture
    def sample_variety_profile(self):
        """Create sample variety timing profile."""
        return VarietyTimingProfile(
            variety_id="test-variety-001",
            variety_name="Test Corn Variety",
            crop_name="corn",
            relative_maturity=105,
            maturity_group="5.5",
            days_to_emergence=7,
            days_to_flowering=60,
            days_to_physiological_maturity=115,
            heat_unit_requirements=2400,
            frost_sensitivity_adjustment=3,
            market_timing_preference="mid",
            harvest_window_days=21,
            stress_tolerances=["drought", "heat"],
            special_planting_notes=["High yielding variety", "Good standability"]
        )
    
    @pytest.fixture
    def sample_frost_info(self):
        """Create sample frost date information."""
        return FrostDateInfo(
            last_frost_date=date(2024, 4, 15),
            first_frost_date=date(2024, 10, 15),
            growing_season_length=183,
            frost_free_days=183,
            confidence_level="historical"
        )
    
    @pytest.mark.asyncio
    async def test_variety_specific_planting_calculation(self, service, sample_location, sample_variety_profile):
        """Test variety-specific planting date calculation."""
        
        # Mock the variety profile retrieval
        with patch.object(service, '_get_variety_timing_profile', return_value=sample_variety_profile):
            with patch.object(service, '_get_frost_date_info', return_value=sample_frost_info()):
                with patch.object(service, 'calculate_planting_dates') as mock_base_calc:
                    # Mock base planting window
                    mock_base_window = PlantingWindow(
                        crop_name="corn",
                        optimal_date=date(2024, 4, 22),
                        earliest_safe_date=date(2024, 4, 8),
                        latest_safe_date=date(2024, 5, 13),
                        planting_season="spring",
                        safety_margin_days=7,
                        confidence_score=0.9,
                        frost_considerations=["Wait for soil temperature to reach 50°F+"],
                        climate_warnings=[],
                        growing_degree_days_required=2500,
                        expected_harvest_date=date(2024, 8, 15)
                    )
                    mock_base_calc.return_value = mock_base_window
                    
                    # Calculate variety-specific planting dates
                    result = await service.calculate_variety_specific_planting_dates(
                        variety_id="test-variety-001",
                        variety_name="Test Corn Variety",
                        crop_name="corn",
                        location=sample_location,
                        planting_season="spring"
                    )
                    
                    # Verify result is VarietyPlantingWindow
                    assert isinstance(result, VarietyPlantingWindow)
                    assert result.variety_id == "test-variety-001"
                    assert result.variety_name == "Test Corn Variety"
                    assert result.relative_maturity == 105
                    assert result.maturity_group == "5.5"
                    
                    # Verify variety-specific adjustments were applied
                    assert len(result.variety_specific_notes) > 0
                    assert len(result.market_timing_considerations) > 0
                    assert result.harvest_timing_flexibility == 21
                    
                    # Verify frost sensitivity adjustment was applied
                    assert "Variety-specific delay: 3 days later planting recommended" in result.frost_considerations
    
    @pytest.mark.asyncio
    async def test_variety_maturity_adjustments(self, service, sample_location):
        """Test variety maturity adjustments."""
        
        # Create variety with longer maturity
        long_maturity_variety = VarietyTimingProfile(
            variety_id="long-maturity-001",
            variety_name="Long Maturity Corn",
            crop_name="corn",
            days_to_physiological_maturity=130,  # Longer than default
            heat_unit_requirements=2800,
            frost_sensitivity_adjustment=0,
            market_timing_preference="late"
        )
        
        with patch.object(service, '_get_variety_timing_profile', return_value=long_maturity_variety):
            with patch.object(service, '_get_frost_date_info', return_value=sample_frost_info()):
                with patch.object(service, 'calculate_planting_dates') as mock_base_calc:
                    mock_base_window = PlantingWindow(
                        crop_name="corn",
                        optimal_date=date(2024, 4, 22),
                        earliest_safe_date=date(2024, 4, 8),
                        latest_safe_date=date(2024, 5, 13),
                        planting_season="spring",
                        safety_margin_days=7,
                        confidence_score=0.9,
                        frost_considerations=[],
                        climate_warnings=[],
                        growing_degree_days_required=2500,
                        expected_harvest_date=date(2024, 8, 15)
                    )
                    mock_base_calc.return_value = mock_base_window
                    
                    result = await service.calculate_variety_specific_planting_dates(
                        variety_id="long-maturity-001",
                        variety_name="Long Maturity Corn",
                        crop_name="corn",
                        location=sample_location,
                        planting_season="spring"
                    )
                    
                    # Verify maturity adjustment was applied
                    assert "Longer maturity variety: 300 additional days to harvest" in result.frost_considerations
                    assert result.growing_degree_days_required == 2800
    
    @pytest.mark.asyncio
    async def test_heat_unit_validation(self, service, sample_location):
        """Test heat unit requirements validation."""
        
        # Create variety requiring high heat units
        high_heat_variety = VarietyTimingProfile(
            variety_id="high-heat-001",
            variety_name="High Heat Corn",
            crop_name="corn",
            heat_unit_requirements=3500,  # High heat requirement
            frost_sensitivity_adjustment=0
        )
        
        with patch.object(service, '_get_variety_timing_profile', return_value=high_heat_variety):
            with patch.object(service, '_get_frost_date_info', return_value=sample_frost_info()):
                with patch.object(service, 'calculate_planting_dates') as mock_base_calc:
                    mock_base_window = PlantingWindow(
                        crop_name="corn",
                        optimal_date=date(2024, 4, 22),
                        earliest_safe_date=date(2024, 4, 8),
                        latest_safe_date=date(2024, 5, 13),
                        planting_season="spring",
                        safety_margin_days=7,
                        confidence_score=0.9,
                        frost_considerations=[],
                        climate_warnings=[],
                        growing_degree_days_required=2500,
                        expected_harvest_date=date(2024, 8, 15)
                    )
                    mock_base_calc.return_value = mock_base_window
                    
                    result = await service.calculate_variety_specific_planting_dates(
                        variety_id="high-heat-001",
                        variety_name="High Heat Corn",
                        crop_name="corn",
                        location=sample_location,
                        planting_season="spring"
                    )
                    
                    # Verify heat unit warning was added
                    assert "Variety requires 3500 heat units, but only ~2600 available in this zone" in result.climate_warnings
                    assert result.confidence_score < 0.9  # Confidence should be reduced
    
    @pytest.mark.asyncio
    async def test_stress_tolerance_considerations(self, service, sample_location):
        """Test stress tolerance considerations."""
        
        # Create variety with stress tolerances
        stress_tolerant_variety = VarietyTimingProfile(
            variety_id="stress-tolerant-001",
            variety_name="Stress Tolerant Corn",
            crop_name="corn",
            stress_tolerances=["drought", "heat", "cold"],
            frost_sensitivity_adjustment=0
        )
        
        with patch.object(service, '_get_variety_timing_profile', return_value=stress_tolerant_variety):
            with patch.object(service, '_get_frost_date_info', return_value=sample_frost_info()):
                with patch.object(service, 'calculate_planting_dates') as mock_base_calc:
                    mock_base_window = PlantingWindow(
                        crop_name="corn",
                        optimal_date=date(2024, 4, 22),
                        earliest_safe_date=date(2024, 4, 8),
                        latest_safe_date=date(2024, 5, 13),
                        planting_season="spring",
                        safety_margin_days=7,
                        confidence_score=0.9,
                        frost_considerations=[],
                        climate_warnings=[],
                        growing_degree_days_required=2500,
                        expected_harvest_date=date(2024, 8, 15)
                    )
                    mock_base_calc.return_value = mock_base_window
                    
                    result = await service.calculate_variety_specific_planting_dates(
                        variety_id="stress-tolerant-001",
                        variety_name="Stress Tolerant Corn",
                        crop_name="corn",
                        location=sample_location,
                        planting_season="spring"
                    )
                    
                    # Verify stress tolerance considerations were added
                    assert "Drought-tolerant variety - suitable for dry conditions" in result.climate_warnings
                    assert "Heat-tolerant variety - good for hot climates" in result.climate_warnings
                    assert "Cold-tolerant variety - can handle cooler conditions" in result.frost_considerations
    
    def test_create_default_variety_profile(self, service):
        """Test creation of default variety profile."""
        
        result = service._create_default_variety_profile(
            variety_id="default-001",
            variety_name="Default Corn",
            crop_name="corn"
        )
        
        assert isinstance(result, VarietyTimingProfile)
        assert result.variety_id == "default-001"
        assert result.variety_name == "Default Corn"
        assert result.crop_name == "corn"
        assert result.days_to_emergence == 7
        assert result.market_timing_preference == "mid"
        assert result.harvest_window_days == 14
        assert "Default profile for Default Corn" in result.special_planting_notes
    
    def test_market_timing_preference_determination(self, service):
        """Test market timing preference determination."""
        
        # Early maturity variety
        early_variety_data = {"days_to_physiological_maturity": 95}
        assert service._determine_market_timing_preference(early_variety_data) == "early"
        
        # Late maturity variety
        late_variety_data = {"days_to_physiological_maturity": 135}
        assert service._determine_market_timing_preference(late_variety_data) == "late"
        
        # Mid maturity variety
        mid_variety_data = {"days_to_physiological_maturity": 115}
        assert service._determine_market_timing_preference(mid_variety_data) == "mid"
    
    def test_special_planting_notes_generation(self, service):
        """Test generation of special planting notes."""
        
        variety_data = {
            "disease_resistance": ["rust", "blight"],
            "herbicide_tolerance": ["glyphosate"],
            "special_traits": ["high_yield", "drought_tolerant"]
        }
        
        notes = service._generate_special_planting_notes(variety_data)
        
        assert len(notes) == 3
        assert "Disease resistance: rust, blight" in notes
        assert "Herbicide tolerance: glyphosate" in notes
        assert "Special traits: high_yield, drought_tolerant" in notes
    
    def test_default_frost_adjustment(self, service):
        """Test default frost adjustment calculation."""
        
        # Tolerant crop
        tolerant_crop = MagicMock()
        tolerant_crop.frost_tolerance = "tolerant"
        assert service._get_default_frost_adjustment(tolerant_crop) == -7
        
        # Sensitive crop
        sensitive_crop = MagicMock()
        sensitive_crop.frost_tolerance = "sensitive"
        assert service._get_default_frost_adjustment(sensitive_crop) == 0
        
        # Very sensitive crop
        very_sensitive_crop = MagicMock()
        very_sensitive_crop.frost_tolerance = "very_sensitive"
        assert service._get_default_frost_adjustment(very_sensitive_crop) == 7
    
    def test_market_timing_considerations(self, service, sample_variety_profile):
        """Test market timing considerations generation."""
        
        # Early variety
        early_variety = VarietyTimingProfile(
            variety_id="early-001",
            variety_name="Early Corn",
            crop_name="corn",
            market_timing_preference="early"
        )
        considerations = service._get_market_timing_considerations(early_variety)
        assert "Early season variety - plant early for early harvest" in considerations
        
        # Late variety
        late_variety = VarietyTimingProfile(
            variety_id="late-001",
            variety_name="Late Corn",
            crop_name="corn",
            market_timing_preference="late"
        )
        considerations = service._get_market_timing_considerations(late_variety)
        assert "Late season variety - plant later for late harvest" in considerations
        
        # Mid variety
        mid_variety = VarietyTimingProfile(
            variety_id="mid-001",
            variety_name="Mid Corn",
            crop_name="corn",
            market_timing_preference="mid"
        )
        considerations = service._get_market_timing_considerations(mid_variety)
        assert "Mid-season variety - flexible planting timing" in considerations
    
    def test_variety_performance_factors(self, service, sample_variety_profile):
        """Test variety performance factors extraction."""
        
        factors = service._get_variety_performance_factors(sample_variety_profile)
        
        assert factors["relative_maturity"] == 105
        assert factors["maturity_group"] == "5.5"
        assert factors["heat_unit_requirements"] == 2400
        assert factors["stress_tolerances"] == ["drought", "heat"]
        assert factors["harvest_window_days"] == 21


class TestVarietyPlantingDateAPI:
    """Test suite for variety-specific planting date API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client for API testing."""
        from fastapi.testclient import TestClient
        from src.api.planting_date_routes import router
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        return TestClient(app)
    
    def test_variety_specific_planting_endpoint(self, client):
        """Test variety-specific planting date API endpoint."""
        
        request_data = {
            "variety_id": "test-variety-001",
            "variety_name": "Test Corn Variety",
            "crop_name": "corn",
            "location": {
                "latitude": 40.0,
                "longitude": -95.0,
                "address": "Test Farm, Iowa",
                "state": "Iowa",
                "county": "Test County",
                "climate_zone": "5a",
                "elevation_ft": 1000
            },
            "planting_season": "spring"
        }
        
        # Mock the service method
        with patch('src.services.planting_date_service.planting_date_service.calculate_variety_specific_planting_dates') as mock_calc:
            mock_result = VarietyPlantingWindow(
                variety_id="test-variety-001",
                variety_name="Test Corn Variety",
                crop_name="corn",
                optimal_date=date(2024, 4, 25),
                earliest_safe_date=date(2024, 4, 11),
                latest_safe_date=date(2024, 5, 16),
                planting_season="spring",
                safety_margin_days=7,
                confidence_score=0.9,
                frost_considerations=["Variety-specific delay: 3 days later planting recommended"],
                climate_warnings=["Drought-tolerant variety - suitable for dry conditions"],
                growing_degree_days_required=2400,
                expected_harvest_date=date(2024, 8, 18),
                relative_maturity=105,
                maturity_group="5.5",
                variety_specific_notes=["High yielding variety", "Good standability"],
                market_timing_considerations=["Mid-season variety - flexible planting timing"],
                harvest_timing_flexibility=21,
                variety_performance_factors={
                    "relative_maturity": 105,
                    "maturity_group": "5.5",
                    "heat_unit_requirements": 2400,
                    "stress_tolerances": ["drought", "heat"],
                    "harvest_window_days": 21
                }
            )
            mock_calc.return_value = mock_result
            
            response = client.post("/api/v1/planting/variety-specific-dates", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["variety_id"] == "test-variety-001"
            assert data["variety_name"] == "Test Corn Variety"
            assert data["crop_name"] == "corn"
            assert data["relative_maturity"] == 105
            assert data["maturity_group"] == "5.5"
            assert data["harvest_timing_flexibility"] == 21
            assert len(data["variety_specific_notes"]) > 0
            assert len(data["market_timing_considerations"]) > 0
    
    def test_variety_specific_planting_endpoint_validation(self, client):
        """Test variety-specific planting date API endpoint validation."""
        
        # Test invalid planting season
        request_data = {
            "variety_id": "test-variety-001",
            "variety_name": "Test Corn Variety",
            "crop_name": "corn",
            "location": {
                "latitude": 40.0,
                "longitude": -95.0,
                "address": "Test Farm, Iowa",
                "state": "Iowa",
                "county": "Test County",
                "climate_zone": "5a",
                "elevation_ft": 1000
            },
            "planting_season": "invalid_season"
        }
        
        response = client.post("/api/v1/planting/variety-specific-dates", json=request_data)
        assert response.status_code == 422  # Validation error


class TestVarietyPlantingDateIntegration:
    """Integration tests for variety-specific planting date calculations."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_variety_calculation(self):
        """Test end-to-end variety-specific planting date calculation."""
        
        service = PlantingDateCalculatorService()
        location = LocationData(
            latitude=41.5868,  # Iowa coordinates
            longitude=-93.6250,
            address="Central Iowa Farm",
            state="Iowa",
            county="Polk County",
            climate_zone="5a",
            elevation_ft=900
        )
        
        # Test with a real corn variety
        result = await service.calculate_variety_specific_planting_dates(
            variety_id="pioneer-1234",
            variety_name="Pioneer 1234",
            crop_name="corn",
            location=location,
            planting_season="spring"
        )
        
        # Verify basic structure
        assert isinstance(result, VarietyPlantingWindow)
        assert result.variety_id == "pioneer-1234"
        assert result.variety_name == "Pioneer 1234"
        assert result.crop_name == "corn"
        
        # Verify dates are reasonable for Iowa spring planting
        assert result.optimal_date.month in [4, 5]  # April or May
        assert result.earliest_safe_date < result.optimal_date
        assert result.latest_safe_date > result.optimal_date
        
        # Verify harvest date is reasonable
        assert result.expected_harvest_date.month in [8, 9, 10]  # Late summer/fall
        
        # Verify variety-specific information is present
        assert len(result.variety_specific_notes) > 0
        assert len(result.market_timing_considerations) > 0
        assert result.harvest_timing_flexibility > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])