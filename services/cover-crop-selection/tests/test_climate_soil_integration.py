"""
Tests for Climate Zone and Soil Type Integration
Tests the enhanced climate and soil matching capabilities for cover crop selection.
"""

import pytest
from datetime import date
from unittest.mock import AsyncMock, patch

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.cover_crop_models import (
    CoverCropSelectionRequest,
    SoilConditions,
    ClimateData,
    CoverCropSpecies,
    CoverCropType,
    GrowingSeason,
    SoilBenefit
)
from services.cover_crop_selection_service import CoverCropSelectionService


class TestClimateZoneIntegration:
    """Test climate zone integration features."""
    
    @pytest.fixture
    def service(self):
        """Create cover crop selection service."""
        service = CoverCropSelectionService()
        service.initialized = True
        return service
    
    @pytest.fixture
    def sample_species(self):
        """Create sample cover crop species for testing."""
        return CoverCropSpecies(
            species_id="test_001",
            common_name="Test Clover",
            scientific_name="Trifolium testensis",
            cover_crop_type=CoverCropType.LEGUME,
            hardiness_zones=["6a", "6b", "7a", "7b"],
            min_temp_f=15.0,
            max_temp_f=85.0,
            growing_season=GrowingSeason.WINTER,
            ph_range={"min": 6.0, "max": 7.5},
            drainage_tolerance=["well_drained", "moderately_well_drained"],
            salt_tolerance="moderate",
            seeding_rate_lbs_acre={"broadcast": 15.0, "drilled": 12.0},
            planting_depth_inches=0.5,
            days_to_establishment=14,
            biomass_production="high",
            primary_benefits=[SoilBenefit.NITROGEN_FIXATION, SoilBenefit.ORGANIC_MATTER],
            termination_methods=["winter_kill", "herbicide"],
            cash_crop_compatibility=["corn", "soybeans"],
            seed_cost_per_acre=45.0,
            establishment_cost_per_acre=65.0
        )
    
    @pytest.fixture
    def climate_request(self):
        """Create request with climate data."""
        return CoverCropSelectionRequest(
            request_id="test_climate_001",
            location={"latitude": 40.0, "longitude": -85.0},
            field_size_acres=100.0,
            soil_conditions=SoilConditions(
                ph=6.8,
                organic_matter_percent=3.5,
                drainage_class="well_drained",
                texture="loam"
            ),
            climate_data=ClimateData(
                hardiness_zone="7a",
                min_temp_f=10.0,
                max_temp_f=90.0,
                growing_season_length=180,
                average_annual_precipitation=35.0
            ),
            planting_window={"start": date(2024, 10, 15), "end": date(2024, 11, 15)}
        )
    
    async def test_enhanced_climate_data_enrichment(self, service):
        """Test enhanced climate data enrichment from climate service."""
        request = CoverCropSelectionRequest(
            request_id="test_enrich_001",
            location={"latitude": 40.0, "longitude": -85.0},
            field_size_acres=50.0,
            soil_conditions=SoilConditions(
                ph=6.5,
                organic_matter_percent=2.8,
                drainage_class="moderately_well_drained"
            ),
            planting_window={"start": date(2024, 9, 15), "end": date(2024, 10, 15)}
        )
        
        # Mock climate service response
        mock_response = {
            "primary_zone": {
                "zone_id": "6b",
                "min_temp_f": 5.0,
                "max_temp_f": 85.0,
                "growing_season_days": 165
            },
            "precipitation_inches": 42.0,
            "confidence_score": 0.9
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post = AsyncMock()
            mock_client.return_value.__aenter__.return_value.post.return_value.status_code = 200
            mock_client.return_value.__aenter__.return_value.post.return_value.json.return_value = mock_response
            
            enriched_request = await service._enrich_climate_data(request)
            
            assert enriched_request.climate_data is not None
            assert enriched_request.climate_data.hardiness_zone == "6b"
            assert enriched_request.climate_data.min_temp_f == 5.0
            assert enriched_request.climate_data.max_temp_f == 85.0
            assert enriched_request.climate_data.growing_season_length == 165
            assert enriched_request.climate_data.average_annual_precipitation == 42.0
    
    async def test_hardiness_zone_compatibility(self, service, sample_species, climate_request):
        """Test hardiness zone compatibility scoring."""
        # Test exact match
        sample_species.hardiness_zones = ["7a", "7b", "8a"]
        climate_request.climate_data.hardiness_zone = "7a"
        
        score = await service._calculate_climate_soil_compatibility_score(sample_species, climate_request)
        assert score > 0.8  # Should be high score for exact match
        
        # Test nearby zone
        climate_request.climate_data.hardiness_zone = "8a"
        score_nearby = await service._calculate_climate_soil_compatibility_score(sample_species, climate_request)
        assert score_nearby > 0.8  # Still good for nearby zone
        
        # Test incompatible zone
        climate_request.climate_data.hardiness_zone = "4a"
        score_incompatible = await service._calculate_climate_soil_compatibility_score(sample_species, climate_request)
        assert score_incompatible < 0.6  # Should be lower for distant zone
    
    async def test_temperature_tolerance_scoring(self, service, sample_species, climate_request):
        """Test temperature tolerance compatibility scoring."""
        # Test within tolerance
        sample_species.min_temp_f = 10.0
        sample_species.max_temp_f = 85.0
        climate_request.climate_data.min_temp_f = 15.0
        climate_request.climate_data.max_temp_f = 80.0
        
        score = await service._calculate_climate_soil_compatibility_score(sample_species, climate_request)
        assert score > 0.7  # Should be good score
        
        # Test cold tolerance exceeded
        climate_request.climate_data.min_temp_f = 0.0  # Colder than species tolerance
        score_cold = await service._calculate_climate_soil_compatibility_score(sample_species, climate_request)
        assert score_cold < score  # Should be lower
        
        # Test heat tolerance exceeded
        climate_request.climate_data.min_temp_f = 15.0  # Reset
        climate_request.climate_data.max_temp_f = 95.0  # Hotter than species tolerance
        score_hot = await service._calculate_climate_soil_compatibility_score(sample_species, climate_request)
        assert score_hot < score  # Should be lower
    
    async def test_enhanced_species_suitability_check(self, service, sample_species, climate_request):
        """Test enhanced species suitability check with climate integration."""
        # Should be suitable with good conditions
        is_suitable = await service._is_species_suitable(sample_species, climate_request)
        assert is_suitable
        
        # Test with incompatible hardiness zone
        climate_request.climate_data.hardiness_zone = "3a"
        is_suitable_zone = await service._is_species_suitable(sample_species, climate_request)
        assert not is_suitable_zone
        
        # Test with temperature extremes
        climate_request.climate_data.hardiness_zone = "7a"  # Reset
        climate_request.climate_data.min_temp_f = -20.0  # Too cold
        is_suitable_temp = await service._is_species_suitable(sample_species, climate_request)
        assert not is_suitable_temp


class TestSoilTypeIntegration:
    """Test soil type integration and compatibility scoring."""
    
    @pytest.fixture
    def service(self):
        """Create cover crop selection service."""
        service = CoverCropSelectionService()
        service.initialized = True
        return service
    
    @pytest.fixture
    def sample_species(self):
        """Create sample species with specific soil requirements."""
        return CoverCropSpecies(
            species_id="soil_test_001",
            common_name="Test Radish",
            scientific_name="Raphanus soilensis",
            cover_crop_type=CoverCropType.BRASSICA,
            hardiness_zones=["5a", "6a", "7a"],
            min_temp_f=20.0,
            max_temp_f=80.0,
            growing_season=GrowingSeason.FALL,
            ph_range={"min": 6.0, "max": 7.5},
            drainage_tolerance=["well_drained", "moderately_well_drained"],
            salt_tolerance="low",
            seeding_rate_lbs_acre={"broadcast": 10.0},
            planting_depth_inches=0.75,
            days_to_establishment=7,
            biomass_production="medium",
            primary_benefits=[SoilBenefit.COMPACTION_RELIEF, SoilBenefit.SCAVENGING],
            termination_methods=["winter_kill", "mechanical"],
            cash_crop_compatibility=["corn", "soybeans"]
        )
    
    @pytest.fixture
    def soil_request(self):
        """Create request with specific soil conditions."""
        return CoverCropSelectionRequest(
            request_id="soil_test_001",
            location={"latitude": 41.0, "longitude": -88.0},
            field_size_acres=80.0,
            soil_conditions=SoilConditions(
                ph=6.8,
                organic_matter_percent=2.5,
                drainage_class="well_drained",
                texture="silt_loam",
                compaction_issues=True,
                erosion_risk="moderate"
            ),
            climate_data=ClimateData(
                hardiness_zone="6a",
                min_temp_f=15.0,
                max_temp_f=85.0
            ),
            planting_window={"start": date(2024, 8, 15), "end": date(2024, 9, 15)}
        )
    
    async def test_ph_compatibility_scoring(self, service, sample_species, soil_request):
        """Test pH compatibility scoring with tolerance buffer."""
        # Test optimal pH
        soil_request.soil_conditions.ph = 6.8  # Within range
        score_optimal = await service._calculate_climate_soil_compatibility_score(sample_species, soil_request)
        
        # Test slightly outside range (should still be acceptable with buffer)
        soil_request.soil_conditions.ph = 5.9  # Slightly below min (6.0)
        score_buffer = await service._calculate_climate_soil_compatibility_score(sample_species, soil_request)
        assert score_buffer > 0.5  # Should still be acceptable
        
        # Test well outside range
        soil_request.soil_conditions.ph = 5.0  # Well below min
        score_outside = await service._calculate_climate_soil_compatibility_score(sample_species, soil_request)
        assert score_outside < score_buffer  # Should be lower
    
    async def test_drainage_compatibility_scoring(self, service, sample_species, soil_request):
        """Test drainage compatibility scoring."""
        # Test exact match
        soil_request.soil_conditions.drainage_class = "well_drained"
        score_exact = await service._calculate_climate_soil_compatibility_score(sample_species, soil_request)
        
        # Test compatible but not exact
        soil_request.soil_conditions.drainage_class = "moderately_well_drained"
        score_compatible = await service._calculate_climate_soil_compatibility_score(sample_species, soil_request)
        assert score_compatible > 0.7  # Should still be good
        
        # Test somewhat compatible
        soil_request.soil_conditions.drainage_class = "somewhat_poorly_drained"
        score_somewhat = await service._calculate_climate_soil_compatibility_score(sample_species, soil_request)
        assert score_somewhat < score_compatible  # Should be lower but not zero
        
        # Test incompatible
        soil_request.soil_conditions.drainage_class = "very_poorly_drained"
        score_incompatible = await service._calculate_climate_soil_compatibility_score(sample_species, soil_request)
        assert score_incompatible < score_somewhat  # Should be lowest
    
    async def test_salt_tolerance_integration(self, service, sample_species, soil_request):
        """Test salt tolerance compatibility scoring."""
        # Add salinity level to soil conditions
        soil_request.soil_conditions.salinity_level = "low"
        sample_species.salt_tolerance = "moderate"
        
        # Species can handle more salt than soil has - should be good
        score_good = await service._calculate_climate_soil_compatibility_score(sample_species, soil_request)
        
        # Soil has more salt than species can handle
        soil_request.soil_conditions.salinity_level = "high"
        sample_species.salt_tolerance = "low"
        score_poor = await service._calculate_climate_soil_compatibility_score(sample_species, soil_request)
        
        assert score_poor < score_good  # High salinity should lower score
    
    def test_drainage_compatibility_score_calculation(self, service):
        """Test drainage compatibility score calculation method."""
        # Test exact match
        score_exact = service._calculate_drainage_compatibility_score(
            "well_drained", ["well_drained", "moderately_well_drained"]
        )
        assert score_exact == 1.0
        
        # Test one step away
        score_close = service._calculate_drainage_compatibility_score(
            "moderately_well_drained", ["well_drained"]
        )
        assert score_close == 0.8
        
        # Test two steps away
        score_medium = service._calculate_drainage_compatibility_score(
            "somewhat_poorly_drained", ["well_drained"]
        )
        assert score_medium == 0.6
        
        # Test very different
        score_poor = service._calculate_drainage_compatibility_score(
            "very_poorly_drained", ["well_drained"]
        )
        assert score_poor == 0.3


class TestIntegratedClimateAndSoilScoring:
    """Test integrated climate and soil scoring system."""
    
    @pytest.fixture
    def service(self):
        """Create cover crop selection service."""
        service = CoverCropSelectionService()
        service.initialized = True
        return service
    
    @pytest.fixture
    def optimal_request(self):
        """Create request with optimal conditions."""
        return CoverCropSelectionRequest(
            request_id="optimal_001",
            location={"latitude": 42.0, "longitude": -84.0},
            field_size_acres=120.0,
            soil_conditions=SoilConditions(
                ph=6.5,
                organic_matter_percent=4.0,
                drainage_class="well_drained",
                texture="loam"
            ),
            climate_data=ClimateData(
                hardiness_zone="6b",
                min_temp_f=8.0,
                max_temp_f=82.0,
                growing_season_length=170,
                average_annual_precipitation=32.0
            ),
            planting_window={"start": date(2024, 9, 20), "end": date(2024, 10, 20)}
        )
    
    @pytest.fixture
    def optimal_species(self):
        """Create species perfectly matched to optimal conditions."""
        return CoverCropSpecies(
            species_id="optimal_001",
            common_name="Optimal Clover",
            scientific_name="Trifolium optimalis",
            cover_crop_type=CoverCropType.LEGUME,
            hardiness_zones=["6a", "6b", "7a"],
            min_temp_f=5.0,
            max_temp_f=85.0,
            growing_season=GrowingSeason.WINTER,
            ph_range={"min": 6.0, "max": 7.0},
            drainage_tolerance=["well_drained", "moderately_well_drained"],
            salt_tolerance="moderate",
            seeding_rate_lbs_acre={"broadcast": 12.0},
            planting_depth_inches=0.5,
            days_to_establishment=10,
            biomass_production="high",
            primary_benefits=[SoilBenefit.NITROGEN_FIXATION, SoilBenefit.ORGANIC_MATTER],
            termination_methods=["winter_kill"],
            cash_crop_compatibility=["corn", "soybeans"]
        )
    
    async def test_comprehensive_compatibility_scoring(self, service, optimal_species, optimal_request):
        """Test comprehensive climate and soil compatibility scoring."""
        score = await service._calculate_climate_soil_compatibility_score(optimal_species, optimal_request)
        
        # Should get high score for optimal match
        assert score > 0.9
        
        # Test individual component scoring
        assert score <= 1.0  # Should not exceed maximum
    
    async def test_enhanced_species_scoring_integration(self, service, optimal_species, optimal_request):
        """Test enhanced species scoring with climate and soil integration."""
        # Add objectives to request
        from models.cover_crop_models import CoverCropObjectives, SoilBenefit
        optimal_request.objectives = CoverCropObjectives(
            primary_goals=[SoilBenefit.NITROGEN_FIXATION, SoilBenefit.ORGANIC_MATTER],
            budget_per_acre=100.0
        )
        
        score = await service._calculate_species_score(optimal_species, optimal_request)
        
        # Should get very high score for optimal match
        assert score > 0.8
        assert score <= 1.0
    
    async def test_climate_suitability_assessment(self, service, optimal_request):
        """Test enhanced climate suitability assessment."""
        suitability = await service._assess_climate_suitability(optimal_request)
        
        assert suitability["hardiness_zone"] == "6b"
        assert suitability["suitability"] in ["Good", "Excellent"]
        assert len(suitability["considerations"]) > 0
        
        # Test with challenging conditions
        optimal_request.climate_data.min_temp_f = -15.0
        challenging_suitability = await service._assess_climate_suitability(optimal_request)
        
        assert challenging_suitability["suitability"] == "Challenging"
        assert any("cold" in consideration.lower() 
                  for consideration in challenging_suitability["considerations"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])