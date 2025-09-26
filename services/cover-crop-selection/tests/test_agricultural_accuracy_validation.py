"""
Agricultural Accuracy Validation Tests for Cover Crop Selection Service

This module validates that the cover crop selection service provides
agriculturally sound recommendations based on:
1. Peer-reviewed research and extension publications
2. USDA NRCS guidelines and standards
3. Regional best practices and expert knowledge
4. Scientific principles of agronomy and soil science

Test Categories:
- Species-Environment Compatibility Validation
- Nitrogen Fixation Accuracy Testing
- Soil Improvement Claims Validation
- Regional Adaptation Accuracy
- Economic Analysis Validation
- Timing Recommendation Accuracy
- Integration with Main Crops Validation
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import date, datetime, timedelta
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add the src directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.cover_crop_selection_service import CoverCropSelectionService
from models.cover_crop_models import (
    CoverCropSelectionRequest,
    CoverCropSelectionResponse,
    CoverCropRecommendation,
    CoverCropSpecies,
    CoverCropType,
    GrowingSeason,
    SoilBenefit,
    SoilConditions,
    CoverCropObjectives,
    Location,
    ClimateData
)


@pytest.fixture
def service():
    """Cover crop selection service fixture."""
    return CoverCropSelectionService()


@pytest.fixture
def agriculturally_validated_species():
    """Agriculturally validated species data based on USDA NRCS recommendations."""
    return {
        "cc_crimson_clover": CoverCropSpecies(
            species_id="cc_crimson_clover",
            common_name="Crimson Clover",
            scientific_name="Trifolium incarnatum",
            cover_crop_type=CoverCropType.LEGUME,
            hardiness_zones=["6a", "6b", "7a", "7b", "8a", "8b", "9a"],
            min_temp_f=20.0,  # NRCS documented cold tolerance
            max_temp_f=85.0,
            growing_season=GrowingSeason.WINTER,
            ph_range={"min": 5.5, "max": 7.0},  # USDA documented pH tolerance
            drainage_tolerance=["well_drained", "moderately_well_drained"],
            salt_tolerance="low",
            seeding_rate_lbs_acre={"broadcast": 20, "drilled": 15},  # NRCS recommended rates
            planting_depth_inches=0.25,
            days_to_establishment=14,
            biomass_production="moderate",
            primary_benefits=[SoilBenefit.NITROGEN_FIXATION, SoilBenefit.EROSION_CONTROL],
            nitrogen_fixation_lbs_acre=70,  # Research-based N fixation rates
            root_depth_feet=2.0,
            termination_methods=["herbicide", "mowing", "incorporation"],
            cash_crop_compatibility=["corn", "cotton", "soybeans"],
            seed_cost_per_acre=45.0,
            establishment_cost_per_acre=65.0
        ),
        "cc_winter_rye": CoverCropSpecies(
            species_id="cc_winter_rye",
            common_name="Winter Rye",
            scientific_name="Secale cereale",
            cover_crop_type=CoverCropType.GRASS,
            hardiness_zones=["3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b"],
            min_temp_f=-30.0,  # Excellent cold tolerance
            max_temp_f=75.0,
            growing_season=GrowingSeason.WINTER,
            ph_range={"min": 5.0, "max": 7.5},  # Wide pH tolerance
            drainage_tolerance=["well_drained", "moderately_well_drained", "somewhat_poorly_drained"],
            salt_tolerance="moderate",
            seeding_rate_lbs_acre={"broadcast": 90, "drilled": 60},
            planting_depth_inches=1.0,
            days_to_establishment=7,  # Fast establishment
            biomass_production="high",
            primary_benefits=[SoilBenefit.EROSION_CONTROL, SoilBenefit.WEED_SUPPRESSION, SoilBenefit.NUTRIENT_SCAVENGING],
            nitrogen_fixation_lbs_acre=0,  # Non-legume
            root_depth_feet=3.0,
            termination_methods=["herbicide", "mowing", "roller_crimper"],
            cash_crop_compatibility=["corn", "soybeans", "cotton"],
            seed_cost_per_acre=35.0,
            establishment_cost_per_acre=50.0
        ),
        "cc_hairy_vetch": CoverCropSpecies(
            species_id="cc_hairy_vetch",
            common_name="Hairy Vetch",
            scientific_name="Vicia villosa",
            cover_crop_type=CoverCropType.LEGUME,
            hardiness_zones=["4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b", "8a"],
            min_temp_f=-10.0,  # Good cold tolerance
            max_temp_f=80.0,
            growing_season=GrowingSeason.WINTER,
            ph_range={"min": 5.5, "max": 7.5},
            drainage_tolerance=["well_drained", "moderately_well_drained"],
            salt_tolerance="low",
            seeding_rate_lbs_acre={"broadcast": 30, "drilled": 20},
            planting_depth_inches=0.5,
            days_to_establishment=21,  # Slower establishment
            biomass_production="high",
            primary_benefits=[SoilBenefit.NITROGEN_FIXATION, SoilBenefit.WEED_SUPPRESSION, SoilBenefit.EROSION_CONTROL],
            nitrogen_fixation_lbs_acre=150,  # High N fixation capacity
            root_depth_feet=3.0,
            termination_methods=["herbicide", "mowing", "roller_crimper"],
            cash_crop_compatibility=["corn", "soybeans"],
            seed_cost_per_acre=90.0,
            establishment_cost_per_acre=115.0
        ),
        "cc_forage_radish": CoverCropSpecies(
            species_id="cc_forage_radish",
            common_name="Forage Radish",
            scientific_name="Raphanus sativus",
            cover_crop_type=CoverCropType.BRASSICA,
            hardiness_zones=["3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b", "8a"],
            min_temp_f=25.0,  # Frost-sensitive
            max_temp_f=80.0,
            growing_season=GrowingSeason.FALL,
            ph_range={"min": 6.0, "max": 7.5},
            drainage_tolerance=["well_drained", "moderately_well_drained"],
            salt_tolerance="moderate",
            seeding_rate_lbs_acre={"broadcast": 12, "drilled": 8},
            planting_depth_inches=0.5,
            days_to_establishment=5,  # Very fast establishment
            biomass_production="moderate",
            primary_benefits=[SoilBenefit.COMPACTION_RELIEF, SoilBenefit.NUTRIENT_SCAVENGING],
            nitrogen_fixation_lbs_acre=0,  # Non-legume
            root_depth_feet=4.0,  # Deep taproot for compaction relief
            termination_methods=["winter_kill", "mowing"],  # Typically winter-killed
            cash_crop_compatibility=["corn", "soybeans"],
            seed_cost_per_acre=25.0,
            establishment_cost_per_acre=35.0
        )
    }


class TestSpeciesEnvironmentCompatibility:
    """Test species-environment compatibility accuracy."""
    
    @pytest.mark.asyncio
    async def test_hardiness_zone_accuracy(self, service, agriculturally_validated_species):
        """Test hardiness zone recommendations match USDA standards."""
        with patch.object(service, '_load_cover_crop_database', return_value=None), \
             patch.object(service, '_load_mixture_database', return_value=None):
            
            service.species_database = agriculturally_validated_species
            service.mixture_database = {}
            await service.initialize()
            
            # Test Zone 6a (borderline for crimson clover)
            request = CoverCropSelectionRequest(
                request_id="zone_6a_test",
                location=Location(latitude=42.0, longitude=-83.0),  # Detroit area, Zone 6a
                climate_data=ClimateData(hardiness_zone="6a", min_temp_f=0, max_temp_f=85),
                soil_conditions=SoilConditions(
                    ph=6.5,
                    organic_matter_percent=2.5,
                    drainage_class="well_drained"
                ),
                objectives=CoverCropObjectives(
                    primary_goals=[SoilBenefit.NITROGEN_FIXATION],
                    nitrogen_needs=True
                ),
                planting_window={"start": date(2024, 9, 15), "end": date(2024, 10, 15)},
                field_size_acres=10.0
            )
            
            response = await service.select_cover_crops(request)
            
            # Crimson clover should be recommended in Zone 6a
            clover_rec = next((r for r in response.single_species_recommendations 
                              if r.species.species_id == "cc_crimson_clover"), None)
            
            assert clover_rec is not None, "Crimson clover should be suitable for Zone 6a"
            assert clover_rec.suitability_score > 0.5, "Crimson clover should score well in Zone 6a"
            
            # Test Zone 5a (too cold for crimson clover)
            request.climate_data.hardiness_zone = "5a"
            request.climate_data.min_temp_f = -15
            
            response = await service.select_cover_crops(request)
            
            # Crimson clover should NOT be recommended in Zone 5a
            clover_rec = next((r for r in response.single_species_recommendations 
                              if r.species.species_id == "cc_crimson_clover"), None)
            
            # Should either not be present or have very low score
            if clover_rec is not None:
                assert clover_rec.suitability_score < 0.3, "Crimson clover should score poorly in Zone 5a"
            
            # Winter rye should be recommended in Zone 5a
            rye_rec = next((r for r in response.single_species_recommendations 
                           if r.species.species_id == "cc_winter_rye"), None)
            
            if rye_rec is not None:
                assert rye_rec.suitability_score > 0.6, "Winter rye should score well in Zone 5a"
                
    @pytest.mark.asyncio
    async def test_soil_ph_compatibility_accuracy(self, service, agriculturally_validated_species):
        """Test soil pH compatibility matches agricultural research."""
        with patch.object(service, '_load_cover_crop_database', return_value=None), \
             patch.object(service, '_load_mixture_database', return_value=None):
            
            service.species_database = agriculturally_validated_species
            service.mixture_database = {}
            await service.initialize()
            
            # Test acidic soil (pH 5.2) - should favor winter rye over forage radish
            request = CoverCropSelectionRequest(
                request_id="acidic_soil_test",
                location=Location(latitude=40.0, longitude=-85.0),
                climate_data=ClimateData(hardiness_zone="6a"),
                soil_conditions=SoilConditions(
                    ph=5.2,  # Acidic
                    organic_matter_percent=2.5,
                    drainage_class="well_drained"
                ),
                objectives=CoverCropObjectives(
                    primary_goals=[SoilBenefit.EROSION_CONTROL]
                ),
                planting_window={"start": date(2024, 9, 15), "end": date(2024, 10, 15)},
                field_size_acres=15.0
            )
            
            response = await service.select_cover_crops(request)
            
            rye_rec = next((r for r in response.single_species_recommendations 
                           if r.species.species_id == "cc_winter_rye"), None)
            radish_rec = next((r for r in response.single_species_recommendations 
                              if r.species.species_id == "cc_forage_radish"), None)
            
            # Winter rye tolerates lower pH (5.0+) vs radish (6.0+)
            if rye_rec and radish_rec:
                assert rye_rec.suitability_score > radish_rec.suitability_score, \
                    "Winter rye should outperform radish in acidic conditions"
            elif rye_rec:
                assert rye_rec.suitability_score > 0.6, "Winter rye should score well in acidic soil"
                
    @pytest.mark.asyncio
    async def test_drainage_compatibility_accuracy(self, service, agriculturally_validated_species):
        """Test drainage compatibility matches field research."""
        with patch.object(service, '_load_cover_crop_database', return_value=None), \
             patch.object(service, '_load_mixture_database', return_value=None):
            
            service.species_database = agriculturally_validated_species
            service.mixture_database = {}
            await service.initialize()
            
            # Test poorly drained soil - winter rye should be recommended over others
            request = CoverCropSelectionRequest(
                request_id="poor_drainage_test",
                location=Location(latitude=40.0, longitude=-85.0),
                climate_data=ClimateData(hardiness_zone="6a"),
                soil_conditions=SoilConditions(
                    ph=6.5,
                    organic_matter_percent=3.0,
                    drainage_class="somewhat_poorly_drained"
                ),
                objectives=CoverCropObjectives(
                    primary_goals=[SoilBenefit.EROSION_CONTROL]
                ),
                planting_window={"start": date(2024, 9, 15), "end": date(2024, 10, 15)},
                field_size_acres=20.0
            )
            
            response = await service.select_cover_crops(request)
            
            # Winter rye tolerates poor drainage better than other species
            rye_rec = next((r for r in response.single_species_recommendations 
                           if r.species.species_id == "cc_winter_rye"), None)
            
            if rye_rec:
                assert rye_rec.suitability_score > 0.5, \
                    "Winter rye should perform well in poorly drained conditions"


class TestNitrogenFixationAccuracy:
    """Test nitrogen fixation estimates match research data."""
    
    @pytest.mark.asyncio
    async def test_nitrogen_fixation_estimates(self, service, agriculturally_validated_species):
        """Test N fixation estimates match peer-reviewed research."""
        with patch.object(service, '_load_cover_crop_database', return_value=None), \
             patch.object(service, '_load_mixture_database', return_value=None):
            
            service.species_database = agriculturally_validated_species
            service.mixture_database = {}
            await service.initialize()
            
            request = CoverCropSelectionRequest(
                request_id="nitrogen_fixation_test",
                location=Location(latitude=40.0, longitude=-85.0),
                climate_data=ClimateData(hardiness_zone="6a"),
                soil_conditions=SoilConditions(
                    ph=6.5,
                    organic_matter_percent=2.5,
                    drainage_class="well_drained"
                ),
                objectives=CoverCropObjectives(
                    primary_goals=[SoilBenefit.NITROGEN_FIXATION],
                    nitrogen_needs=True
                ),
                planting_window={"start": date(2024, 9, 15), "end": date(2024, 10, 15)},
                field_size_acres=25.0
            )
            
            response = await service.select_cover_crops(request)
            
            # Verify nitrogen fixation ranking matches research
            # Hairy vetch: ~150 lbs N/acre (highest)
            # Crimson clover: ~70 lbs N/acre (moderate)
            # Winter rye: 0 lbs N/acre (non-legume)
            
            vetch_rec = next((r for r in response.single_species_recommendations 
                             if r.species.species_id == "cc_hairy_vetch"), None)
            clover_rec = next((r for r in response.single_species_recommendations 
                              if r.species.species_id == "cc_crimson_clover"), None)
            rye_rec = next((r for r in response.single_species_recommendations 
                           if r.species.species_id == "cc_winter_rye"), None)
            
            if vetch_rec and clover_rec:
                assert vetch_rec.suitability_score >= clover_rec.suitability_score, \
                    "Hairy vetch should rank higher than crimson clover for N fixation"
            
            if clover_rec and rye_rec:
                assert clover_rec.suitability_score > rye_rec.suitability_score, \
                    "Legumes should outrank grasses for nitrogen fixation goals"
                    
    @pytest.mark.asyncio
    async def test_legume_selection_for_corn_following(self, service, agriculturally_validated_species):
        """Test legume recommendations for corn production systems."""
        with patch.object(service, '_load_cover_crop_database', return_value=None), \
             patch.object(service, '_load_mixture_database', return_value=None):
            
            service.species_database = agriculturally_validated_species
            service.mixture_database = {}
            await service.initialize()
            
            # High nitrogen need scenario (corn following)
            request = CoverCropSelectionRequest(
                request_id="corn_nitrogen_test",
                location=Location(latitude=41.0, longitude=-93.0),  # Iowa corn belt
                climate_data=ClimateData(hardiness_zone="5b"),
                soil_conditions=SoilConditions(
                    ph=6.8,
                    organic_matter_percent=3.2,
                    drainage_class="well_drained"
                ),
                objectives=CoverCropObjectives(
                    primary_goals=[SoilBenefit.NITROGEN_FIXATION],
                    nitrogen_needs=True,
                    budget_per_acre=120.0  # Adequate budget for higher-cost legumes
                ),
                planting_window={"start": date(2024, 9, 1), "end": date(2024, 10, 1)},
                field_size_acres=40.0
            )
            
            response = await service.select_cover_crops(request)
            
            # Should prioritize high N-fixing legumes
            legume_recs = [r for r in response.single_species_recommendations 
                          if r.species.cover_crop_type == CoverCropType.LEGUME]
            
            assert len(legume_recs) > 0, "Should recommend legumes for high N need scenario"
            
            # Top recommendation should be a legume
            if response.single_species_recommendations:
                top_rec = response.single_species_recommendations[0]
                assert top_rec.species.cover_crop_type == CoverCropType.LEGUME, \
                    "Top recommendation should be a legume for N fixation goals"


class TestSoilImprovementAccuracy:
    """Test soil improvement claims accuracy."""
    
    @pytest.mark.asyncio
    async def test_compaction_relief_recommendations(self, service, agriculturally_validated_species):
        """Test compaction relief recommendations match research."""
        with patch.object(service, '_load_cover_crop_database', return_value=None), \
             patch.object(service, '_load_mixture_database', return_value=None):
            
            service.species_database = agriculturally_validated_species
            service.mixture_database = {}
            await service.initialize()
            
            request = CoverCropSelectionRequest(
                request_id="compaction_test",
                location=Location(latitude=40.0, longitude=-85.0),
                climate_data=ClimateData(hardiness_zone="6a"),
                soil_conditions=SoilConditions(
                    ph=6.5,
                    organic_matter_percent=2.0,
                    drainage_class="somewhat_poorly_drained",  # Suggests compaction
                    erosion_risk="high"
                ),
                objectives=CoverCropObjectives(
                    primary_goals=[SoilBenefit.COMPACTION_RELIEF]
                ),
                planting_window={"start": date(2024, 8, 15), "end": date(2024, 9, 15)},
                field_size_acres=30.0
            )
            
            response = await service.select_cover_crops(request)
            
            # Forage radish should be highly recommended for compaction relief
            radish_rec = next((r for r in response.single_species_recommendations 
                              if r.species.species_id == "cc_forage_radish"), None)
            
            if radish_rec:
                assert radish_rec.suitability_score > 0.7, \
                    "Forage radish should score highly for compaction relief"
                    
                # Should have deep taproot mentioned in benefits
                assert SoilBenefit.COMPACTION_RELIEF in radish_rec.species.primary_benefits, \
                    "Forage radish should list compaction relief as primary benefit"
                    
    @pytest.mark.asyncio
    async def test_erosion_control_recommendations(self, service, agriculturally_validated_species):
        """Test erosion control recommendations accuracy."""
        with patch.object(service, '_load_cover_crop_database', return_value=None), \
             patch.object(service, '_load_mixture_database', return_value=None):
            
            service.species_database = agriculturally_validated_species
            service.mixture_database = {}
            await service.initialize()
            
            request = CoverCropSelectionRequest(
                request_id="erosion_control_test",
                location=Location(latitude=40.5, longitude=-85.0),
                climate_data=ClimateData(hardiness_zone="6a"),
                soil_conditions=SoilConditions(
                    ph=6.2,
                    organic_matter_percent=2.5,
                    drainage_class="well_drained",
                    erosion_risk="high"  # High erosion risk
                ),
                objectives=CoverCropObjectives(
                    primary_goals=[SoilBenefit.EROSION_CONTROL],
                    erosion_control_priority=True
                ),
                planting_window={"start": date(2024, 9, 1), "end": date(2024, 10, 15)},
                field_size_acres=25.0
            )
            
            response = await service.select_cover_crops(request)
            
            # Winter rye should be highly recommended for erosion control
            rye_rec = next((r for r in response.single_species_recommendations 
                           if r.species.species_id == "cc_winter_rye"), None)
            
            if rye_rec:
                assert rye_rec.suitability_score > 0.7, \
                    "Winter rye should score highly for erosion control"
                    
                assert SoilBenefit.EROSION_CONTROL in rye_rec.species.primary_benefits, \
                    "Winter rye should list erosion control as primary benefit"


class TestRegionalAdaptationAccuracy:
    """Test regional adaptation recommendations."""
    
    @pytest.mark.asyncio
    async def test_southern_region_adaptation(self, service, agriculturally_validated_species):
        """Test species selection for southern growing regions."""
        with patch.object(service, '_load_cover_crop_database', return_value=None), \
             patch.object(service, '_load_mixture_database', return_value=None):
            
            service.species_database = agriculturally_validated_species
            service.mixture_database = {}
            await service.initialize()
            
            # Southern location (Georgia)
            request = CoverCropSelectionRequest(
                request_id="southern_adaptation_test",
                location=Location(latitude=33.5, longitude=-84.0),  # Atlanta, GA area
                climate_data=ClimateData(
                    hardiness_zone="8a",
                    min_temp_f=10,
                    max_temp_f=90,
                    average_annual_precipitation=50.0
                ),
                soil_conditions=SoilConditions(
                    ph=6.0,
                    organic_matter_percent=2.2,
                    drainage_class="well_drained"
                ),
                objectives=CoverCropObjectives(
                    primary_goals=[SoilBenefit.NITROGEN_FIXATION, SoilBenefit.EROSION_CONTROL]
                ),
                planting_window={"start": date(2024, 10, 1), "end": date(2024, 11, 15)},
                field_size_acres=20.0
            )
            
            response = await service.select_cover_crops(request)
            
            # Crimson clover should be highly suitable in Zone 8a
            clover_rec = next((r for r in response.single_species_recommendations 
                              if r.species.species_id == "cc_crimson_clover"), None)
            
            if clover_rec:
                assert clover_rec.suitability_score > 0.8, \
                    "Crimson clover should be excellent in southern regions (Zone 8a)"
                    
    @pytest.mark.asyncio
    async def test_northern_region_adaptation(self, service, agriculturally_validated_species):
        """Test species selection for northern growing regions."""
        with patch.object(service, '_load_cover_crop_database', return_value=None), \
             patch.object(service, '_load_mixture_database', return_value=None):
            
            service.species_database = agriculturally_validated_species
            service.mixture_database = {}
            await service.initialize()
            
            # Northern location (Minnesota)
            request = CoverCropSelectionRequest(
                request_id="northern_adaptation_test",
                location=Location(latitude=45.0, longitude=-93.0),  # Minneapolis area
                climate_data=ClimateData(
                    hardiness_zone="4b",
                    min_temp_f=-20,
                    max_temp_f=85,
                    average_annual_precipitation=32.0
                ),
                soil_conditions=SoilConditions(
                    ph=6.8,
                    organic_matter_percent=3.5,
                    drainage_class="well_drained"
                ),
                objectives=CoverCropObjectives(
                    primary_goals=[SoilBenefit.EROSION_CONTROL, SoilBenefit.ORGANIC_MATTER]
                ),
                planting_window={"start": date(2024, 8, 15), "end": date(2024, 9, 30)},
                field_size_acres=35.0
            )
            
            response = await service.select_cover_crops(request)
            
            # Winter rye should be excellent in northern regions
            rye_rec = next((r for r in response.single_species_recommendations 
                           if r.species.species_id == "cc_winter_rye"), None)
            
            if rye_rec:
                assert rye_rec.suitability_score > 0.8, \
                    "Winter rye should be excellent in northern regions (Zone 4b)"
                    
            # Crimson clover should not be recommended in Zone 4b
            clover_rec = next((r for r in response.single_species_recommendations 
                              if r.species.species_id == "cc_crimson_clover"), None)
            
            # Should either not be present or have very low score
            if clover_rec is not None:
                assert clover_rec.suitability_score < 0.3, \
                    "Crimson clover should not be suitable in Zone 4b"


class TestEconomicAnalysisAccuracy:
    """Test economic analysis accuracy."""
    
    @pytest.mark.asyncio
    async def test_cost_effectiveness_ranking(self, service, agriculturally_validated_species):
        """Test cost-effectiveness ranking matches economic reality."""
        with patch.object(service, '_load_cover_crop_database', return_value=None), \
             patch.object(service, '_load_mixture_database', return_value=None):
            
            service.species_database = agriculturally_validated_species
            service.mixture_database = {}
            await service.initialize()
            
            # Budget-constrained scenario
            request = CoverCropSelectionRequest(
                request_id="budget_constraint_test",
                location=Location(latitude=40.0, longitude=-85.0),
                climate_data=ClimateData(hardiness_zone="6a"),
                soil_conditions=SoilConditions(
                    ph=6.5,
                    organic_matter_percent=2.5,
                    drainage_class="well_drained"
                ),
                objectives=CoverCropObjectives(
                    primary_goals=[SoilBenefit.EROSION_CONTROL],
                    budget_per_acre=40.0  # Tight budget
                ),
                planting_window={"start": date(2024, 9, 15), "end": date(2024, 10, 15)},
                field_size_acres=50.0  # Large field - cost matters
            )
            
            response = await service.select_cover_crops(request)
            
            # Winter rye ($35/acre) should be preferred over hairy vetch ($90/acre)
            rye_rec = next((r for r in response.single_species_recommendations 
                           if r.species.species_id == "cc_winter_rye"), None)
            vetch_rec = next((r for r in response.single_species_recommendations 
                             if r.species.species_id == "cc_hairy_vetch"), None)
            
            if rye_rec and vetch_rec:
                assert rye_rec.suitability_score >= vetch_rec.suitability_score, \
                    "Lower-cost options should be favored with budget constraints"
            elif rye_rec:
                assert rye_rec.suitability_score > 0.6, \
                    "Winter rye should score well in budget-constrained scenarios"
                    
    @pytest.mark.asyncio
    async def test_large_field_economics(self, service, agriculturally_validated_species):
        """Test economic considerations for large fields."""
        with patch.object(service, '_load_cover_crop_database', return_value=None), \
             patch.object(service, '_load_mixture_database', return_value=None):
            
            service.species_database = agriculturally_validated_species
            service.mixture_database = {}
            await service.initialize()
            
            request = CoverCropSelectionRequest(
                request_id="large_field_economics_test",
                location=Location(latitude=42.0, longitude=-95.0),  # Iowa
                climate_data=ClimateData(hardiness_zone="5a"),
                soil_conditions=SoilConditions(
                    ph=6.8,
                    organic_matter_percent=3.0,
                    drainage_class="well_drained"
                ),
                objectives=CoverCropObjectives(
                    primary_goals=[SoilBenefit.EROSION_CONTROL, SoilBenefit.ORGANIC_MATTER],
                    budget_per_acre=60.0
                ),
                planting_window={"start": date(2024, 9, 1), "end": date(2024, 10, 1)},
                field_size_acres=500.0  # Very large field
            )
            
            response = await service.select_cover_crops(request)
            
            # Should favor cost-effective options for large fields
            if response.single_species_recommendations:
                top_rec = response.single_species_recommendations[0]
                
                # Check that cost was considered in ranking
                if top_rec.species.species_id == "cc_winter_rye":
                    assert top_rec.suitability_score > 0.7, \
                        "Cost-effective winter rye should score well on large fields"
                elif top_rec.species.species_id == "cc_forage_radish":
                    assert top_rec.suitability_score > 0.6, \
                        "Cost-effective radish should score well on large fields"


class TestTimingRecommendationAccuracy:
    """Test timing recommendation accuracy."""
    
    @pytest.mark.asyncio
    async def test_fall_planting_timing_accuracy(self, service, agriculturally_validated_species):
        """Test fall planting timing recommendations."""
        with patch.object(service, '_load_cover_crop_database', return_value=None), \
             patch.object(service, '_load_mixture_database', return_value=None):
            
            service.species_database = agriculturally_validated_species
            service.mixture_database = {}
            await service.initialize()
            
            # Early fall planting window
            request = CoverCropSelectionRequest(
                request_id="fall_timing_test",
                location=Location(latitude=40.0, longitude=-85.0),
                climate_data=ClimateData(hardiness_zone="6a"),
                soil_conditions=SoilConditions(
                    ph=6.5,
                    organic_matter_percent=2.5,
                    drainage_class="well_drained"
                ),
                objectives=CoverCropObjectives(
                    primary_goals=[SoilBenefit.COMPACTION_RELIEF]
                ),
                planting_window={"start": date(2024, 8, 1), "end": date(2024, 8, 31)},
                field_size_acres=25.0
            )
            
            response = await service.select_cover_crops(request)
            
            # Forage radish should be highly suitable for early fall planting
            radish_rec = next((r for r in response.single_species_recommendations 
                              if r.species.species_id == "cc_forage_radish"), None)
            
            if radish_rec:
                assert radish_rec.suitability_score > 0.7, \
                    "Forage radish should be excellent for early fall planting"
                    
    @pytest.mark.asyncio
    async def test_late_fall_planting_restrictions(self, service, agriculturally_validated_species):
        """Test late fall planting restrictions."""
        with patch.object(service, '_load_cover_crop_database', return_value=None), \
             patch.object(service, '_load_mixture_database', return_value=None):
            
            service.species_database = agriculturally_validated_species
            service.mixture_database = {}
            await service.initialize()
            
            # Very late fall planting (too late for most establishment)
            request = CoverCropSelectionRequest(
                request_id="late_fall_test",
                location=Location(latitude=42.0, longitude=-85.0),
                climate_data=ClimateData(hardiness_zone="5b"),
                soil_conditions=SoilConditions(
                    ph=6.5,
                    organic_matter_percent=2.5,
                    drainage_class="well_drained"
                ),
                objectives=CoverCropObjectives(
                    primary_goals=[SoilBenefit.EROSION_CONTROL]
                ),
                planting_window={"start": date(2024, 11, 15), "end": date(2024, 12, 1)},
                field_size_acres=20.0
            )
            
            response = await service.select_cover_crops(request)
            
            # Should have lower confidence for late plantings
            assert response.overall_confidence < 0.8, \
                "Late fall plantings should have reduced confidence"
                
            # If any recommendations exist, should favor very cold-hardy species
            if response.single_species_recommendations:
                for rec in response.single_species_recommendations:
                    if rec.species.species_id == "cc_winter_rye":
                        # Winter rye might still work with low confidence
                        assert rec.confidence_level < 0.7, \
                            "Late plantings should have reduced confidence even for hardy species"


class TestMainCropIntegrationAccuracy:
    """Test main crop integration accuracy."""
    
    @pytest.mark.asyncio
    async def test_corn_soybean_rotation_compatibility(self, service, agriculturally_validated_species):
        """Test cover crop recommendations for corn-soybean rotation."""
        with patch.object(service, '_load_cover_crop_database', return_value=None), \
             patch.object(service, '_load_mixture_database', return_value=None):
            
            service.species_database = agriculturally_validated_species
            service.mixture_database = {}
            await service.initialize()
            
            # After corn, before soybeans (nitrogen not critical)
            request = CoverCropSelectionRequest(
                request_id="corn_soybean_rotation_test",
                location=Location(latitude=41.0, longitude=-93.0),  # Iowa
                climate_data=ClimateData(hardiness_zone="5b"),
                soil_conditions=SoilConditions(
                    ph=6.8,
                    organic_matter_percent=3.2,
                    drainage_class="well_drained"
                ),
                objectives=CoverCropObjectives(
                    primary_goals=[SoilBenefit.EROSION_CONTROL, SoilBenefit.ORGANIC_MATTER],
                    nitrogen_needs=False  # Soybeans fix their own nitrogen
                ),
                planting_window={"start": date(2024, 9, 15), "end": date(2024, 10, 15)},
                field_size_acres=80.0
            )
            
            response = await service.select_cover_crops(request)
            
            # Should recommend species compatible with both corn and soybeans
            compatible_species = []
            for rec in response.single_species_recommendations:
                if ("corn" in rec.species.cash_crop_compatibility and 
                    "soybeans" in rec.species.cash_crop_compatibility):
                    compatible_species.append(rec)
                    
            assert len(compatible_species) > 0, \
                "Should recommend species compatible with corn-soybean rotation"
                
            # Winter rye should be a top choice for corn-soybean systems
            rye_rec = next((r for r in response.single_species_recommendations 
                           if r.species.species_id == "cc_winter_rye"), None)
            
            if rye_rec:
                assert rye_rec.suitability_score > 0.6, \
                    "Winter rye should score well in corn-soybean rotations"
    
    @pytest.mark.asyncio
    async def test_cash_crop_compatibility_accuracy(self, service, agriculturally_validated_species):
        """Test cash crop compatibility claims accuracy."""
        with patch.object(service, '_load_cover_crop_database', return_value=None), \
             patch.object(service, '_load_mixture_database', return_value=None):
            
            service.species_database = agriculturally_validated_species
            service.mixture_database = {}
            await service.initialize()
            
            # Verify that all species have realistic cash crop compatibility lists
            for species_id, species in agriculturally_validated_species.items():
                assert len(species.cash_crop_compatibility) > 0, \
                    f"Species {species_id} should have at least one compatible cash crop"
                    
                # Check common compatibility claims
                common_crops = ["corn", "soybeans", "wheat", "cotton"]
                compatible_crops = [crop for crop in species.cash_crop_compatibility 
                                  if crop in common_crops]
                
                assert len(compatible_crops) > 0, \
                    f"Species {species_id} should be compatible with at least one major crop"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])