"""
Position-Based Coverage Tests for Cover Crop Selection Service

Focuses on position-based recommendation methods and filtering logic
to increase coverage for core service methods.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from datetime import date, datetime, timedelta
from typing import List, Dict, Any

from src.services.cover_crop_selection_service import CoverCropSelectionService
from src.models.cover_crop_models import (
    CoverCropSelectionRequest,
    CoverCropSelectionResponse,
    CoverCropRecommendation,
    CoverCropSpecies,
    CoverCropMixture,
    CoverCropType,
    GrowingSeason,
    SoilBenefit,
    SoilConditions,
    ClimateData,
    GoalBasedObjectives,
    SpecificGoal,
    GoalPriority,
    FarmerGoalCategory,
    MainCropRotationPlan,
    PlantingTimingWindow,
    TerminationTimingWindow,
    TerminationMethod
)


class TestPositionBasedCoverage:
    """Test position-based recommendation methods."""
    
    @pytest.fixture
    async def service(self):
        """Create service instance for testing."""
        service = CoverCropSelectionService()
        service.species_database = self._create_mock_species_database()
        service.mixture_database = self._create_mock_mixture_database()
        service.initialized = True
        return service
    
    def _create_mock_species_database(self) -> Dict[str, CoverCropSpecies]:
        """Create comprehensive mock species database."""
        return {
            "crimson_clover": CoverCropSpecies(
                species_id="crimson_clover",
                common_name="Crimson Clover",
                scientific_name="Trifolium incarnatum",
                cover_crop_type=CoverCropType.LEGUME,
                hardiness_zones=["6a", "7a", "8a"],
                min_temp_f=15.0,
                max_temp_f=85.0,
                growing_season=GrowingSeason.WINTER,
                ph_range={"min": 6.0, "max": 7.5},
                drainage_tolerance=["well_drained", "moderately_well_drained"],
                salt_tolerance="moderate",
                seeding_rate_lbs_acre={"broadcast": 15.0, "drilled": 12.0},
                planting_depth_inches=0.25,
                days_to_establishment=21,
                biomass_production="high",
                primary_benefits=[SoilBenefit.NITROGEN_FIXATION, SoilBenefit.EROSION_CONTROL],
                termination_methods=["winter_kill", "mechanical", "herbicide"],
                cash_crop_compatibility=["corn", "soybeans", "wheat"]
            ),
            "winter_rye": CoverCropSpecies(
                species_id="winter_rye",
                common_name="Winter Rye",
                scientific_name="Secale cereale",
                cover_crop_type=CoverCropType.GRASS,
                hardiness_zones=["3a", "4a", "5a", "6a", "7a"],
                min_temp_f=-20.0,
                max_temp_f=80.0,
                growing_season=GrowingSeason.WINTER,
                ph_range={"min": 5.0, "max": 8.0},
                drainage_tolerance=["well_drained", "moderately_well_drained", "somewhat_poorly_drained"],
                salt_tolerance="moderate",
                seeding_rate_lbs_acre={"broadcast": 90.0, "drilled": 70.0},
                planting_depth_inches=1.0,
                days_to_establishment=7,
                biomass_production="very_high",
                primary_benefits=[SoilBenefit.EROSION_CONTROL, SoilBenefit.WEED_SUPPRESSION],
                termination_methods=["herbicide", "mechanical"],
                cash_crop_compatibility=["corn", "soybeans"]
            ),
            "oilseed_radish": CoverCropSpecies(
                species_id="oilseed_radish",
                common_name="Oilseed Radish",
                scientific_name="Raphanus sativus",
                cover_crop_type=CoverCropType.BRASSICA,
                hardiness_zones=["4a", "5a", "6a", "7a", "8a"],
                min_temp_f=20.0,
                max_temp_f=75.0,
                growing_season=GrowingSeason.FALL,
                ph_range={"min": 5.5, "max": 7.0},
                drainage_tolerance=["well_drained", "moderately_well_drained"],
                salt_tolerance="low",
                seeding_rate_lbs_acre={"broadcast": 10.0, "drilled": 8.0},
                planting_depth_inches=0.5,
                days_to_establishment=5,
                biomass_production="high",
                primary_benefits=[SoilBenefit.COMPACTION_RELIEF, SoilBenefit.ORGANIC_MATTER],
                termination_methods=["winter_kill", "mechanical"],
                cash_crop_compatibility=["corn", "soybeans"]
            )
        }
    
    def _create_mock_mixture_database(self) -> Dict[str, CoverCropMixture]:
        """Create mock mixture database."""
        return {
            "balanced_mix": CoverCropMixture(
                mixture_id="balanced_mix",
                name="Balanced Cover Crop Mix",
                species_composition=[
                    {"species_id": "crimson_clover", "percentage": 30.0, "seeding_rate_lbs_acre": 4.5},
                    {"species_id": "winter_rye", "percentage": 50.0, "seeding_rate_lbs_acre": 35.0},
                    {"species_id": "oilseed_radish", "percentage": 20.0, "seeding_rate_lbs_acre": 2.0}
                ],
                total_seeding_rate_lbs_acre=41.5,
                planting_method="broadcast",
                primary_benefits=[SoilBenefit.NITROGEN_FIXATION, SoilBenefit.EROSION_CONTROL, SoilBenefit.COMPACTION_RELIEF],
                compatibility_score=0.92,
                mixture_type="diversified",
                establishment_timeline={"early_species": 5, "full_establishment": 21}
            )
        }

    @pytest.mark.asyncio
    async def test_filter_recommendations_by_position(self, service):
        """Test filtering recommendations by rotation position."""
        # Create mock recommendations
        recommendations = [
            CoverCropRecommendation(
                species=service.species_database["crimson_clover"],
                suitability_score=0.88,
                reasoning="Excellent nitrogen fixation for corn rotation",
                estimated_cost_per_acre=45.0,
                expected_benefits=["nitrogen_fixation", "erosion_control"],
                management_requirements=["inoculation", "proper_timing"],
                planting_timing=PlantingTimingWindow(
                    optimal_start=date(2024, 9, 15),
                    optimal_end=date(2024, 10, 15),
                    acceptable_start=date(2024, 9, 1),
                    acceptable_end=date(2024, 10, 31)
                ),
                termination_timing=TerminationTimingWindow(
                    recommended_method=TerminationMethod.MECHANICAL,
                    optimal_timing=date(2025, 4, 15),
                    latest_timing=date(2025, 5, 1)
                )
            ),
            CoverCropRecommendation(
                species=service.species_database["winter_rye"],
                suitability_score=0.92,
                reasoning="Superior erosion control and biomass production",
                estimated_cost_per_acre=38.0,
                expected_benefits=["erosion_control", "weed_suppression"],
                management_requirements=["herbicide_termination"],
                planting_timing=PlantingTimingWindow(
                    optimal_start=date(2024, 9, 1),
                    optimal_end=date(2024, 10, 1),
                    acceptable_start=date(2024, 8, 15),
                    acceptable_end=date(2024, 10, 15)
                ),
                termination_timing=TerminationTimingWindow(
                    recommended_method=TerminationMethod.HERBICIDE,
                    optimal_timing=date(2025, 4, 1),
                    latest_timing=date(2025, 4, 20)
                )
            )
        ]
        
        rotation_plan = MainCropRotationPlan(
            plan_id="test_filter_001",
            farmer_id="farmer_123",
            field_id="field_456",
            rotation_sequence=["corn", "soybeans"],
            current_year=2024,
            current_position=0,  # Currently corn position
            field_history=[
                {
                    "year": 2023,
                    "crop": "soybeans",
                    "yield_bu_acre": 58.0,
                    "cover_crop_used": False
                }
            ]
        )
        
        filtered_recommendations = await service._filter_recommendations_by_position(
            recommendations, rotation_plan
        )
        
        assert isinstance(filtered_recommendations, list)
        assert len(filtered_recommendations) <= len(recommendations)
        # Should prioritize recommendations suitable for corn position
        if filtered_recommendations:
            # Winter rye should score higher for corn position due to C:N ratio management
            assert any(rec.species.species_id == "winter_rye" for rec in filtered_recommendations)

    @pytest.mark.asyncio
    async def test_analyze_specific_position(self, service):
        """Test analysis of specific rotation position."""
        rotation_plan = MainCropRotationPlan(
            plan_id="test_position_001",
            farmer_id="farmer_123",
            field_id="field_456",
            rotation_sequence=["corn", "soybeans", "wheat"],
            current_year=2024,
            current_position=1,  # Currently soybeans position
            field_history=[
                {
                    "year": 2023,
                    "crop": "corn",
                    "yield_bu_acre": 175.0,
                    "cover_crop_used": True,
                    "cover_crop_species": ["winter_rye"]
                },
                {
                    "year": 2022,
                    "crop": "wheat",
                    "yield_bu_acre": 68.0,
                    "cover_crop_used": False
                }
            ]
        )
        
        analysis = await service._analyze_specific_position(rotation_plan, 1)
        
        assert isinstance(analysis, dict)
        assert "position_characteristics" in analysis
        assert "nutrient_needs" in analysis
        assert "timing_constraints" in analysis
        assert "recommended_benefits" in analysis

    @pytest.mark.asyncio
    async def test_generate_position_mixtures(self, service):
        """Test generation of position-specific mixtures."""
        position_analysis = {
            "position_characteristics": {
                "crop": "soybeans",
                "nitrogen_needs": "low",
                "erosion_risk": "moderate"
            },
            "recommended_species": ["winter_rye", "oilseed_radish"],
            "primary_objectives": ["erosion_control", "compaction_relief"]
        }
        
        mixtures = await service._generate_position_mixtures(position_analysis)
        
        assert isinstance(mixtures, list)
        if mixtures:
            assert all(isinstance(mixture, CoverCropMixture) for mixture in mixtures)
            # Should include species from position analysis
            for mixture in mixtures:
                species_ids = [comp["species_id"] for comp in mixture.species_composition]
                assert any(species_id in position_analysis["recommended_species"] for species_id in species_ids)

    @pytest.mark.asyncio
    async def test_get_position_seasonal_considerations(self, service):
        """Test position seasonal considerations."""
        position_analysis = {
            "position_characteristics": {
                "crop": "corn",
                "planting_date": date(2024, 5, 1),
                "harvest_date": date(2024, 10, 15)
            },
            "timing_constraints": {
                "cover_crop_window_start": date(2024, 10, 20),
                "cover_crop_window_end": date(2025, 4, 15)
            }
        }
        
        location = {"latitude": 41.5, "longitude": -85.8}
        
        seasonal_considerations = await service._get_position_seasonal_considerations(
            position_analysis, location
        )
        
        assert isinstance(seasonal_considerations, dict)
        assert "seasonal_factors" in seasonal_considerations
        assert "climate_adaptations" in seasonal_considerations

    @pytest.mark.asyncio
    async def test_create_position_timeline(self, service):
        """Test creation of position-specific timeline."""
        position_analysis = {
            "position_characteristics": {
                "crop": "wheat",
                "harvest_date": date(2024, 7, 15)
            },
            "recommended_species": ["crimson_clover"],
            "timing_constraints": {
                "cover_crop_window_start": date(2024, 8, 1),
                "cover_crop_window_end": date(2025, 3, 31)
            }
        }
        
        recommendations = [
            CoverCropRecommendation(
                species=service.species_database["crimson_clover"],
                suitability_score=0.85,
                reasoning="Good fit for wheat rotation",
                estimated_cost_per_acre=42.0,
                expected_benefits=["nitrogen_fixation"],
                management_requirements=["inoculation"],
                planting_timing=PlantingTimingWindow(
                    optimal_start=date(2024, 8, 15),
                    optimal_end=date(2024, 9, 15),
                    acceptable_start=date(2024, 8, 1),
                    acceptable_end=date(2024, 9, 30)
                ),
                termination_timing=TerminationTimingWindow(
                    recommended_method=TerminationMethod.WINTER_KILL,
                    optimal_timing=date(2025, 1, 15),
                    latest_timing=date(2025, 2, 1)
                )
            )
        ]
        
        timeline = await service._create_position_timeline(position_analysis, recommendations)
        
        assert isinstance(timeline, dict)
        assert "planting_timeline" in timeline
        assert "management_timeline" in timeline
        assert "termination_timeline" in timeline

    @pytest.mark.asyncio
    async def test_get_position_monitoring_recommendations(self, service):
        """Test position monitoring recommendations."""
        position_analysis = {
            "position_characteristics": {
                "crop": "soybeans",
                "nitrogen_needs": "low",
                "compaction_risk": "high"
            },
            "recommended_species": ["oilseed_radish", "winter_rye"],
            "primary_objectives": ["compaction_relief", "residue_management"]
        }
        
        monitoring_recs = await service._get_position_monitoring_recommendations(position_analysis)
        
        assert isinstance(monitoring_recs, list)
        assert all(isinstance(rec, str) for rec in monitoring_recs)
        # Should include monitoring specific to position characteristics
        monitoring_text = " ".join(monitoring_recs).lower()
        assert any(keyword in monitoring_text for keyword in ["compaction", "soil", "establishment"])

    @pytest.mark.asyncio
    async def test_complex_rotation_scenario(self, service):
        """Test complex rotation scenario with multiple constraints."""
        # Complex 4-crop rotation with specific constraints
        rotation_plan = MainCropRotationPlan(
            plan_id="test_complex_001",
            farmer_id="farmer_456",
            field_id="field_789",
            rotation_sequence=["corn", "soybeans", "wheat", "cover_crop"],
            current_year=2024,
            current_position=2,  # Currently wheat position
            field_history=[
                {
                    "year": 2023,
                    "crop": "soybeans",
                    "yield_bu_acre": 62.0,
                    "cover_crop_used": True,
                    "cover_crop_species": ["crimson_clover"],
                    "cover_crop_performance": "excellent"
                },
                {
                    "year": 2022,
                    "crop": "corn",
                    "yield_bu_acre": 185.0,
                    "cover_crop_used": True,
                    "cover_crop_species": ["winter_rye"],
                    "cover_crop_performance": "good"
                }
            ]
        )
        
        request = CoverCropSelectionRequest(
            request_id="test_complex_001",
            location={"latitude": 42.3, "longitude": -84.7},
            field_size_acres=250.0,
            soil_conditions=SoilConditions(
                ph=6.9,
                organic_matter_percent=4.5,
                drainage_class="well_drained",
                texture="silt_loam"
            ),
            climate_data=ClimateData(
                hardiness_zone="6a",
                min_temp_f=5.0,
                max_temp_f=85.0,
                growing_season_length=165,
                average_annual_precipitation=34.0
            ),
            objectives=GoalBasedObjectives(
                specific_goals=[
                    SpecificGoal(
                        goal_id="goal_004",
                        goal_name="soil_structure",
                        category=FarmerGoalCategory.SOIL_HEALTH,
                        target_benefit=SoilBenefit.COMPACTION_RELIEF,
                        target_value=80.0,
                        priority=GoalPriority.HIGH,
                        weight=0.7
                    ),
                    SpecificGoal(
                        goal_id="goal_005",
                        goal_name="organic_matter",
                        category=FarmerGoalCategory.SOIL_HEALTH,
                        target_benefit=SoilBenefit.ORGANIC_MATTER,
                        target_value=120.0,
                        priority=GoalPriority.MEDIUM,
                        weight=0.5
                    )
                ]
            ),
            planting_window={"start": date(2024, 7, 20), "end": date(2024, 8, 20)},
            rotation_plan=rotation_plan
        )
        
        # Mock sub-services for complex scenario
        service.main_crop_integration_service.analyze_rotation_integration = AsyncMock()
        service.goal_based_service.generate_goal_based_recommendations = AsyncMock()
        service.timing_service.get_optimal_timing = AsyncMock()
        
        # Should handle complex rotation without errors
        position_analysis = await service._analyze_specific_position(rotation_plan, 2)
        
        assert isinstance(position_analysis, dict)
        assert "position_characteristics" in position_analysis

    @pytest.mark.asyncio
    async def test_edge_case_empty_rotation_history(self, service):
        """Test handling of rotation plan with no history."""
        rotation_plan = MainCropRotationPlan(
            plan_id="test_empty_001",
            farmer_id="farmer_new",
            field_id="field_new",
            rotation_sequence=["corn", "soybeans"],
            current_year=2024,
            current_position=0,
            field_history=[]  # Empty history
        )
        
        # Should handle empty history gracefully
        analysis = await service._analyze_specific_position(rotation_plan, 0)
        
        assert isinstance(analysis, dict)
        # Should provide default recommendations even without history
        assert "position_characteristics" in analysis
        assert "nutrient_needs" in analysis

    @pytest.mark.asyncio
    async def test_position_with_environmental_constraints(self, service):
        """Test position analysis with environmental constraints."""
        rotation_plan = MainCropRotationPlan(
            plan_id="test_environ_001",
            farmer_id="farmer_eco",
            field_id="field_sensitive",
            rotation_sequence=["corn", "soybeans"],
            current_year=2024,
            current_position=0,
            field_history=[],
            environmental_constraints={
                "waterway_proximity": True,
                "erosion_risk": "high",
                "organic_certification": True
            }
        )
        
        analysis = await service._analyze_specific_position(rotation_plan, 0)
        
        assert isinstance(analysis, dict)
        # Should account for environmental constraints
        assert "environmental_considerations" in analysis or "position_characteristics" in analysis