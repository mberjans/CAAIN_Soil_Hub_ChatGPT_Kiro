"""
Unit Tests for Cover Crop Selection Service

Test cases for cover crop selection logic and agricultural algorithms.
"""

import pytest
import pytest_asyncio
from datetime import date, datetime
from unittest.mock import AsyncMock, patch
import sys
from pathlib import Path

# Add the src directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.cover_crop_selection_service import CoverCropSelectionService
from models.cover_crop_models import (
    CoverCropSelectionRequest,
    SoilConditions,
    CoverCropObjectives,
    ClimateData,
    CoverCropSpecies,
    CoverCropType,
    GrowingSeason,
    SoilBenefit
)


@pytest_asyncio.fixture
async def cover_crop_service():
    """Fixture for cover crop selection service."""
    service = CoverCropSelectionService()
    await service.initialize()
    return service


@pytest.fixture
def sample_request():
    """Fixture for sample cover crop selection request."""
    return CoverCropSelectionRequest(
        request_id="test_request_001",
        location={
            "latitude": 40.7128,
            "longitude": -74.0060
        },
        soil_conditions=SoilConditions(
            ph=6.2,
            organic_matter_percent=2.8,
            drainage_class="moderately_well_drained"
        ),
        objectives=CoverCropObjectives(
            primary_goals=[SoilBenefit.NITROGEN_FIXATION, SoilBenefit.EROSION_CONTROL],
            nitrogen_needs=True,
            budget_per_acre=75.0
        ),
        planting_window={
            "start": date(2024, 9, 15),
            "end": date(2024, 10, 15)
        },
        field_size_acres=25.0
    )


class TestCoverCropSelectionService:
    """Test cases for CoverCropSelectionService."""
    
    @pytest.mark.asyncio
    async def test_service_initialization(self):
        """Test service initialization."""
        service = CoverCropSelectionService()
        assert not service.initialized
        
        await service.initialize()
        assert service.initialized
        assert len(service.species_database) > 0
        
    @pytest.mark.asyncio
    async def test_health_check(self, cover_crop_service):
        """Test service health check."""
        health_status = await cover_crop_service.health_check()
        assert health_status is True
        
    @pytest.mark.asyncio
    async def test_species_lookup_no_filters(self, cover_crop_service):
        """Test species lookup without filters."""
        species_list = await cover_crop_service.lookup_species({})
        assert len(species_list) > 0
        assert all(isinstance(species, CoverCropSpecies) for species in species_list)
        
    @pytest.mark.asyncio
    async def test_species_lookup_with_filters(self, cover_crop_service):
        """Test species lookup with filters."""
        filters = {
            "cover_crop_type": CoverCropType.LEGUME,
            "hardiness_zone": "7a"
        }
        
        species_list = await cover_crop_service.lookup_species(filters)
        
        for species in species_list:
            assert species.cover_crop_type == CoverCropType.LEGUME
            assert "7a" in species.hardiness_zones
            
    @pytest.mark.asyncio
    async def test_species_suitability_check(self, cover_crop_service, sample_request):
        """Test species suitability checking."""
        # Get a species from the database
        species_id = list(cover_crop_service.species_database.keys())[0]
        species = cover_crop_service.species_database[species_id]
        
        # Test suitability with compatible conditions
        suitable = await cover_crop_service._is_species_suitable(species, sample_request)
        
        # The result should be boolean
        assert isinstance(suitable, bool)
        
    @pytest.mark.asyncio
    async def test_field_conditions_analysis(self, cover_crop_service, sample_request):
        """Test field conditions analysis."""
        analysis = await cover_crop_service._analyze_field_conditions(sample_request)
        
        assert "soil_health_score" in analysis
        assert "limiting_factors" in analysis
        assert "advantages" in analysis
        assert "recommendations" in analysis
        
        assert 0.0 <= analysis["soil_health_score"] <= 1.0
        assert isinstance(analysis["limiting_factors"], list)
        assert isinstance(analysis["advantages"], list)
        assert isinstance(analysis["recommendations"], list)
        
    @pytest.mark.asyncio
    async def test_species_scoring(self, cover_crop_service, sample_request):
        """Test species scoring algorithm."""
        # Get suitable species first
        suitable_species = await cover_crop_service._find_suitable_species(sample_request)
        
        if suitable_species:
            scored_species = await cover_crop_service._score_species_suitability(
                suitable_species, sample_request
            )
            
            assert len(scored_species) > 0
            
            for species, score in scored_species:
                assert isinstance(species, CoverCropSpecies)
                assert 0.0 <= score <= 1.0
                
            # Check that species are sorted by score (highest first)
            scores = [score for _, score in scored_species]
            assert scores == sorted(scores, reverse=True)
            
    @pytest.mark.asyncio
    async def test_roi_calculation(self, cover_crop_service, sample_request):
        """Test ROI calculation for cover crops."""
        # Get a species with cost data
        species = None
        for s in cover_crop_service.species_database.values():
            if s.establishment_cost_per_acre:
                species = s
                break
                
        if species:
            roi = cover_crop_service._calculate_roi_estimate(species, sample_request)
            
            if roi is not None:
                assert isinstance(roi, (int, float))
                
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_climate_data_enrichment(self, mock_client, cover_crop_service, sample_request):
        """Test climate data enrichment from external service."""
        # Mock successful climate service response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"zone_id": "7a"}
        
        mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        
        # Test enrichment
        enriched_request = await cover_crop_service._enrich_climate_data(sample_request)
        
        assert enriched_request.climate_data is not None
        assert enriched_request.climate_data.hardiness_zone == "7a"
        
    @pytest.mark.asyncio
    async def test_cover_crop_selection_complete(self, cover_crop_service, sample_request):
        """Test complete cover crop selection process."""
        # Mock climate service to avoid external dependency
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"zone_id": "7a"}
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
            
            response = await cover_crop_service.select_cover_crops(sample_request)
            
            assert response.request_id == sample_request.request_id
            assert response.overall_confidence > 0.0
            assert len(response.single_species_recommendations) > 0
            assert len(response.data_sources) > 0
            
            # Check that recommendations have required fields
            for rec in response.single_species_recommendations:
                assert rec.suitability_score > 0.0
                assert rec.confidence_level > 0.0
                assert len(rec.expected_benefits) > 0
                assert len(rec.management_notes) > 0
                assert len(rec.success_indicators) > 0


class TestCoverCropModels:
    """Test cases for cover crop data models."""
    
    def test_soil_conditions_validation(self):
        """Test soil conditions model validation."""
        # Valid soil conditions
        soil = SoilConditions(
            ph=6.5,
            organic_matter_percent=3.2,
            drainage_class="well_drained",
            test_date=date(2024, 1, 15)
        )
        assert soil.ph == 6.5
        assert soil.organic_matter_percent == 3.2
        
        # Test pH validation
        with pytest.raises(ValueError):
            SoilConditions(
                ph=11.0,  # Invalid pH
                organic_matter_percent=3.0,
                drainage_class="well_drained",
                test_date=date(2024, 1, 15)
            )
            
    def test_cover_crop_objectives_validation(self):
        """Test cover crop objectives model validation."""
        objectives = CoverCropObjectives(
            primary_goals=[SoilBenefit.NITROGEN_FIXATION, SoilBenefit.EROSION_CONTROL],
            nitrogen_needs=True,
            budget_per_acre=100.0
        )
        
        assert len(objectives.primary_goals) == 2
        assert SoilBenefit.NITROGEN_FIXATION in objectives.primary_goals
        assert objectives.nitrogen_needs is True
        
    def test_cover_crop_species_ph_validation(self):
        """Test cover crop species pH range validation."""
        # Valid pH range
        species_data = {
            "species_id": "test_001",
            "common_name": "Test Clover",
            "scientific_name": "Trifolium testius",
            "cover_crop_type": CoverCropType.LEGUME,
            "hardiness_zones": ["7a"],
            "growing_season": GrowingSeason.WINTER,
            "ph_range": {"min": 6.0, "max": 7.5},
            "drainage_tolerance": ["well_drained"],
            "seeding_rate_lbs_acre": {"drilled": 15},
            "planting_depth_inches": 0.25,
            "days_to_establishment": 14,
            "biomass_production": "moderate",
            "primary_benefits": [SoilBenefit.NITROGEN_FIXATION],
            "termination_methods": ["herbicide"],
            "cash_crop_compatibility": ["corn"]
        }
        
        species = CoverCropSpecies(**species_data)
        assert species.ph_range["min"] == 6.0
        assert species.ph_range["max"] == 7.5
        
        # Invalid pH range (missing max)
        invalid_data = species_data.copy()
        invalid_data["ph_range"] = {"min": 6.0}
        
        with pytest.raises(ValueError):
            CoverCropSpecies(**invalid_data)
            
    def test_species_filters_matching(self):
        """Test species filter matching logic."""
        service = CoverCropSelectionService()
        
        species = CoverCropSpecies(
            species_id="test_001",
            common_name="Crimson Clover",
            scientific_name="Trifolium incarnatum",
            cover_crop_type=CoverCropType.LEGUME,
            hardiness_zones=["7a", "7b"],
            growing_season=GrowingSeason.WINTER,
            ph_range={"min": 6.0, "max": 7.5},
            drainage_tolerance=["well_drained"],
            seeding_rate_lbs_acre={"drilled": 15},
            planting_depth_inches=0.25,
            days_to_establishment=14,
            biomass_production="moderate",
            primary_benefits=[SoilBenefit.NITROGEN_FIXATION],
            termination_methods=["herbicide"],
            cash_crop_compatibility=["corn"]
        )
        
        # Test exact type match
        assert service._species_matches_filters(species, {"cover_crop_type": CoverCropType.LEGUME})
        assert not service._species_matches_filters(species, {"cover_crop_type": CoverCropType.GRASS})
        
        # Test zone match
        assert service._species_matches_filters(species, {"hardiness_zone": "7a"})
        assert not service._species_matches_filters(species, {"hardiness_zone": "5a"})
        
        # Test name partial match
        assert service._species_matches_filters(species, {"species_name": "crimson"})
        assert service._species_matches_filters(species, {"species_name": "Clover"})
        assert not service._species_matches_filters(species, {"species_name": "rye"})


if __name__ == "__main__":
    pytest.main([__file__])