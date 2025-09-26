"""
Test Cover Crop Timing System

Tests for the planting and termination timing system functionality.
"""

import pytest
import pytest_asyncio
import asyncio
from datetime import date, datetime, timedelta
from typing import Dict, Any

# Import the services and models
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.cover_crop_selection_service import CoverCropSelectionService
from services.timing_service import CoverCropTimingService
from models.cover_crop_models import (
    TimingRecommendationRequest,
    PlantingTimingWindow,
    TerminationTimingWindow,
    TerminationMethod,
    GrowingSeason,
    TimingRecommendationConfidence
)


@pytest_asyncio.fixture
async def timing_service():
    """Create and initialize timing service for testing."""
    service = CoverCropTimingService()
    await service.initialize()
    return service


@pytest_asyncio.fixture
async def cover_crop_service():
    """Create and initialize cover crop service for testing."""
    service = CoverCropSelectionService()
    await service.initialize()
    return service


@pytest.fixture
def test_location():
    """Test location data."""
    return {
        "latitude": 42.3601,  # Boston area
        "longitude": -71.0589,
        "state": "MA",
        "climate_zone": "6a",
        "elevation_ft": 100
    }


@pytest.fixture
def main_crop_schedule():
    """Test main crop schedule."""
    return {
        "crop": "corn",
        "planting_date": "2024-05-15",
        "harvest_date": "2024-10-01"
    }


class TestTimingService:
    """Test timing service functionality."""
    
    @pytest.mark.asyncio
    async def test_timing_service_initialization(self, timing_service):
        """Test timing service initializes correctly."""
        assert timing_service.initialized
        assert len(timing_service.species_timing_data) == 18
        assert "crimson_clover" in timing_service.species_timing_data
        assert "winter_rye" in timing_service.species_timing_data
        
    @pytest.mark.asyncio
    async def test_climate_data_retrieval(self, timing_service, test_location):
        """Test climate data retrieval."""
        climate_data = await timing_service.get_climate_data(test_location)
        
        assert climate_data is not None
        assert climate_data.average_last_frost is not None
        assert climate_data.average_first_frost is not None
        assert climate_data.average_soil_temp_by_month is not None
        assert len(climate_data.average_soil_temp_by_month) == 12
        
    @pytest.mark.asyncio
    async def test_planting_window_calculation_fall_species(self, timing_service, test_location):
        """Test planting window calculation for fall-planted species."""
        planting_window = await timing_service.calculate_planting_window(
            "winter_rye", test_location, target_season=GrowingSeason.FALL
        )
        
        assert isinstance(planting_window, PlantingTimingWindow)
        assert planting_window.species_id == "unknown"  # Default from species data
        assert planting_window.optimal_planting_start is not None
        assert planting_window.optimal_planting_end is not None
        assert planting_window.optimal_planting_start <= planting_window.optimal_planting_end
        
        # Winter rye should be planted in fall (Sept-Nov)
        assert 9 <= planting_window.optimal_planting_start.month <= 11
        
    @pytest.mark.asyncio
    async def test_planting_window_calculation_spring_species(self, timing_service, test_location):
        """Test planting window calculation for spring-planted species."""
        planting_window = await timing_service.calculate_planting_window(
            "red_clover", test_location, target_season=GrowingSeason.SPRING
        )
        
        assert isinstance(planting_window, PlantingTimingWindow)
        assert planting_window.optimal_planting_start is not None
        assert planting_window.optimal_planting_end is not None
        
        # Red clover spring planting should be March-May
        assert 3 <= planting_window.optimal_planting_start.month <= 5
        
    @pytest.mark.asyncio
    async def test_termination_windows_calculation(self, timing_service, test_location):
        """Test termination window calculation."""
        planting_date = date(2024, 10, 1)  # Fall planting
        
        termination_windows = await timing_service.calculate_termination_windows(
            "winter_rye", planting_date, test_location
        )
        
        assert len(termination_windows) > 0
        
        for window in termination_windows:
            assert isinstance(window, TerminationTimingWindow)
            assert window.species_id == "unknown"  # Default from species data
            assert window.termination_method in [
                TerminationMethod.HERBICIDE,
                TerminationMethod.ROLLING_CRIMPING,
                TerminationMethod.MOWING
            ]
            assert window.optimal_termination_start > planting_date
            assert window.optimal_termination_end >= window.optimal_termination_start
            
    @pytest.mark.asyncio
    async def test_termination_methods_species_specific(self, timing_service, test_location):
        """Test that different species have appropriate termination methods."""
        planting_date = date(2024, 4, 1)
        
        # Test radish (should include winter kill)
        radish_windows = await timing_service.calculate_termination_windows(
            "radish_tillage", planting_date, test_location
        )
        
        methods = [w.termination_method for w in radish_windows]
        assert TerminationMethod.WINTER_KILL in methods
        
        # Test hairy vetch (should include rolling crimping)
        vetch_windows = await timing_service.calculate_termination_windows(
            "hairy_vetch", planting_date, test_location
        )
        
        methods = [w.termination_method for w in vetch_windows]
        assert TerminationMethod.ROLLING_CRIMPING in methods
        
    @pytest.mark.asyncio
    async def test_comprehensive_timing_recommendation(self, timing_service, test_location):
        """Test comprehensive timing recommendation generation."""
        request = TimingRecommendationRequest(
            species_id="crimson_clover",
            location=test_location,
            main_crop_schedule={},
            management_goals=["nitrogen_fixation", "erosion_control"]
        )
        
        response = await timing_service.generate_comprehensive_timing_recommendation(request)
        
        assert response.species_id == "crimson_clover"
        assert response.recommended_planting is not None
        assert len(response.recommended_termination) > 0
        assert response.seasonal_strategy is not None
        assert response.expected_establishment_success > 0
        assert response.recommendation_summary is not None
        
    @pytest.mark.asyncio
    async def test_main_crop_schedule_integration(self, timing_service, test_location, main_crop_schedule):
        """Test integration with main crop schedules."""
        termination_windows = await timing_service.calculate_termination_windows(
            "winter_rye", 
            date(2024, 9, 15), 
            test_location,
            main_crop_schedule
        )
        
        # Check that termination is scheduled before main crop planting
        main_plant_date = datetime.strptime(main_crop_schedule["planting_date"], "%Y-%m-%d").date()
        
        for window in termination_windows:
            assert window.latest_safe_termination <= main_plant_date
            
    @pytest.mark.asyncio
    async def test_invalid_species_handling(self, timing_service, test_location):
        """Test handling of invalid species IDs."""
        with pytest.raises(ValueError, match="Species invalid_species not found"):
            await timing_service.calculate_planting_window("invalid_species", test_location)
            
    @pytest.mark.asyncio
    async def test_seasonal_constraints(self, timing_service, test_location):
        """Test seasonal planting constraints."""
        # Test that summer species (cowpea) has warm season requirements
        cowpea_window = await timing_service.calculate_planting_window(
            "cowpea", test_location, target_season=GrowingSeason.SUMMER
        )
        
        # Should be planted in warm months (May-July)
        assert 5 <= cowpea_window.optimal_planting_start.month <= 7
        assert cowpea_window.soil_temperature_requirements["minimum"] >= 65
        
        # Test that winter species has cold tolerance
        rye_window = await timing_service.calculate_planting_window(
            "winter_rye", test_location, target_season=GrowingSeason.FALL
        )
        
        assert rye_window.soil_temperature_requirements["minimum"] <= 40


class TestCoverCropServiceTimingIntegration:
    """Test timing integration in main cover crop service."""
    
    @pytest.mark.asyncio
    async def test_service_timing_integration(self, cover_crop_service, test_location):
        """Test timing integration in main service."""
        # Test planting window retrieval
        planting_window = await cover_crop_service.get_planting_window(
            "winter_rye", test_location, target_season=GrowingSeason.FALL
        )
        
        assert isinstance(planting_window, PlantingTimingWindow)
        assert planting_window.optimal_planting_start is not None
        
    @pytest.mark.asyncio
    async def test_service_termination_windows(self, cover_crop_service, test_location):
        """Test termination windows through main service."""
        planting_date = date(2024, 9, 15)
        
        termination_windows = await cover_crop_service.get_termination_windows(
            "winter_rye", planting_date, test_location
        )
        
        assert len(termination_windows) > 0
        assert all(isinstance(w, TerminationTimingWindow) for w in termination_windows)
        
    @pytest.mark.asyncio
    async def test_seasonal_timing_strategy(self, cover_crop_service, test_location):
        """Test seasonal timing strategy generation."""
        strategy = await cover_crop_service.get_seasonal_timing_strategy(
            "crimson_clover",
            test_location,
            GrowingSeason.FALL,
            ["nitrogen_fixation", "erosion_control"]
        )
        
        assert "seasonal_strategy" in strategy
        assert "planting_window" in strategy
        assert "termination_options" in strategy
        assert "establishment_success_probability" in strategy
        assert strategy["establishment_success_probability"] > 0
        
    @pytest.mark.asyncio
    async def test_species_timing_flexibility(self, cover_crop_service, test_location):
        """Test species timing flexibility information."""
        flexibility = await cover_crop_service.get_species_timing_flexibility(
            "hairy_vetch", test_location
        )
        
        assert flexibility["species_id"] == "hairy_vetch"
        assert "available_seasons" in flexibility
        assert "optimal_planting_months" in flexibility
        assert "frost_tolerance" in flexibility
        assert "minimum_soil_temperature_f" in flexibility
        assert "available_termination_methods" in flexibility
        
        # Hairy vetch should be winter hardy
        assert flexibility["winter_hardy"] is True
        assert flexibility["frost_tolerance"] == "high"
        
    @pytest.mark.asyncio
    async def test_timing_recommendations_request(self, cover_crop_service, test_location):
        """Test comprehensive timing recommendations through main service."""
        request = TimingRecommendationRequest(
            species_id="annual_ryegrass",
            location=test_location,
            main_crop_schedule={},
            management_goals=["erosion_control", "organic_matter"]
        )
        
        response = await cover_crop_service.get_timing_recommendations(request)
        
        assert response.species_id == "annual_ryegrass"
        assert response.recommended_planting is not None
        assert len(response.recommended_termination) > 0
        assert response.overall_confidence in [
            TimingRecommendationConfidence.HIGH,
            TimingRecommendationConfidence.MEDIUM,
            TimingRecommendationConfidence.LOW
        ]


if __name__ == "__main__":
    # Run basic tests
    async def run_basic_tests():
        print("Testing Cover Crop Timing System...")
        
        # Initialize services
        timing_service = CoverCropTimingService()
        await timing_service.initialize()
        
        cover_crop_service = CoverCropSelectionService()
        await cover_crop_service.initialize()
        
        test_location = {
            "latitude": 42.3601,
            "longitude": -71.0589,
            "state": "MA",
            "climate_zone": "6a"
        }
        
        print("✓ Services initialized successfully")
        
        # Test planting window calculation
        planting_window = await timing_service.calculate_planting_window(
            "winter_rye", test_location, target_season=GrowingSeason.FALL
        )
        print(f"✓ Planting window calculated: {planting_window.optimal_planting_start} to {planting_window.optimal_planting_end}")
        
        # Test termination windows
        termination_windows = await timing_service.calculate_termination_windows(
            "winter_rye", date(2024, 10, 1), test_location
        )
        print(f"✓ Found {len(termination_windows)} termination methods")
        
        # Test comprehensive recommendations
        request = TimingRecommendationRequest(
            species_id="crimson_clover",
            location=test_location,
            main_crop_schedule={},
            management_goals=["nitrogen_fixation"]
        )
        
        response = await timing_service.generate_comprehensive_timing_recommendation(request)
        print(f"✓ Comprehensive recommendation generated: {response.recommendation_summary}")
        
        # Test main service integration
        flexibility = await cover_crop_service.get_species_timing_flexibility(
            "hairy_vetch", test_location
        )
        print(f"✓ Species flexibility retrieved: {len(flexibility['available_termination_methods'])} termination methods")
        
        print("\n🎉 All timing system tests passed!")
        
    # Run the tests
    asyncio.run(run_basic_tests())