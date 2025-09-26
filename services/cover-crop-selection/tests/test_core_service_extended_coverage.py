"""
Extended Coverage Tests for Cover Crop Selection Service

Focused on improving test coverage for core service methods that are currently under-tested.
Target: Increase coverage from 37% to 80%+ for cover_crop_selection_service.py
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
    CoverCropRotationIntegration,
    CropTimingWindow,
    PlantingTimingWindow,
    TerminationTimingWindow,
    TerminationMethod
)


class TestCoreServiceExtendedCoverage:
    """Test class for extending coverage of core service methods."""
    
    @pytest.fixture
    async def service(self):
        """Create service instance for testing."""
        service = CoverCropSelectionService()
        # Mock the database loading to avoid file dependencies
        service.species_database = self._create_mock_species_database()
        service.mixture_database = self._create_mock_mixture_database()
        service.initialized = True
        return service
    
    def _create_mock_species_database(self) -> Dict[str, CoverCropSpecies]:
        """Create mock species database for testing."""
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
            )
        }
    
    def _create_mock_mixture_database(self) -> Dict[str, CoverCropMixture]:
        """Create mock mixture database for testing."""
        return {
            "clover_rye_mix": CoverCropMixture(
                mixture_id="clover_rye_mix",
                name="Crimson Clover + Winter Rye",
                species_composition=[
                    {"species_id": "crimson_clover", "percentage": 40.0, "seeding_rate_lbs_acre": 6.0},
                    {"species_id": "winter_rye", "percentage": 60.0, "seeding_rate_lbs_acre": 42.0}
                ],
                total_seeding_rate_lbs_acre=48.0,
                planting_method="broadcast",
                primary_benefits=[SoilBenefit.NITROGEN_FIXATION, SoilBenefit.EROSION_CONTROL],
                compatibility_score=0.95,
                mixture_type="balanced",
                establishment_timeline={"early_species": 7, "full_establishment": 28}
            )
        }

    @pytest.mark.asyncio
    async def test_cleanup_method(self, service):
        """Test cleanup method coverage."""
        # Mock the services that need cleanup
        service.main_crop_integration_service.cleanup = AsyncMock()
        service.timing_service.cleanup = AsyncMock()
        
        await service.cleanup()
        
        # Verify cleanup was called on sub-services
        service.main_crop_integration_service.cleanup.assert_called_once()
        service.timing_service.cleanup.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_healthy(self, service):
        """Test health check when service is healthy."""
        # Mock sub-services as healthy
        service.main_crop_integration_service.health_check = AsyncMock(return_value=True)
        service.timing_service.health_check = AsyncMock(return_value=True)
        
        result = await service.health_check()
        
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, service):
        """Test health check when service is unhealthy."""
        # Mock one sub-service as unhealthy
        service.main_crop_integration_service.health_check = AsyncMock(return_value=False)
        service.timing_service.health_check = AsyncMock(return_value=True)
        
        result = await service.health_check()
        
        assert result is False

    @pytest.mark.asyncio
    async def test_generate_rotation_specific_recommendations(self, service):
        """Test rotation-specific recommendation generation."""
        # Create test request with rotation plan
        rotation_plan = MainCropRotationPlan(
            plan_id="test_rotation_001",
            farmer_id="farmer_123",
            field_id="field_456",
            rotation_sequence=["corn", "soybeans", "wheat"],
            current_year=2024,
            current_position=0,
            field_history=[
                {
                    "year": 2023,
                    "crop": "soybeans",
                    "yield_bu_acre": 55.0,
                    "cover_crop_used": False
                }
            ]
        )
        
        request = CoverCropSelectionRequest(
            request_id="test_rotation_001",
            location={"latitude": 40.0, "longitude": -85.0},
            field_size_acres=100.0,
            soil_conditions=SoilConditions(
                ph=6.5,
                organic_matter_percent=3.5,
                drainage_class="well_drained",
                texture="loam"
            ),
            objectives=GoalBasedObjectives(
                specific_goals=[
                    SpecificGoal(
                        goal_id="goal_001",
                        goal_name="nitrogen_fixation",
                        category=FarmerGoalCategory.NUTRIENT_MANAGEMENT,
                        target_benefit=SoilBenefit.NITROGEN_FIXATION,
                        target_value=120.0,
                        priority=GoalPriority.HIGH,
                        weight=0.8
                    )
                ]
            ),
            planting_window={"start": date(2024, 9, 15), "end": date(2024, 10, 15)},
            rotation_plan=rotation_plan
        )
        
        # Mock integration service response
        integration_response = CoverCropRotationIntegration(
            plan_id="test_rotation_001",
            integration_strategy="nitrogen_focused",
            recommended_species=["crimson_clover"],
            planting_windows=[
                CropTimingWindow(
                    crop="corn",
                    planting_window={"start": date(2024, 4, 15), "end": date(2024, 5, 15)},
                    cover_crop_window={"start": date(2023, 9, 15), "end": date(2024, 4, 10)}
                )
            ],
            termination_recommendations=[
                {
                    "species": "crimson_clover",
                    "method": TerminationMethod.MECHANICAL,
                    "timing": "2-3 weeks before corn planting"
                }
            ]
        )
        
        service.main_crop_integration_service.analyze_rotation_integration = AsyncMock(
            return_value=integration_response
        )
        
        result = await service._generate_rotation_specific_recommendations(request)
        
        assert isinstance(result, CoverCropSelectionResponse)
        assert len(result.recommendations) > 0
        assert result.request_id == "test_rotation_001"

    @pytest.mark.asyncio
    async def test_analyze_field_conditions_with_rotation(self, service):
        """Test field condition analysis with rotation context."""
        rotation_plan = MainCropRotationPlan(
            plan_id="test_rotation_002",
            farmer_id="farmer_123",
            field_id="field_456",
            rotation_sequence=["corn", "soybeans"],
            current_year=2024,
            current_position=1,  # Currently soybeans
            field_history=[
                {
                    "year": 2023,
                    "crop": "corn",
                    "yield_bu_acre": 180.0,
                    "cover_crop_used": True,
                    "cover_crop_species": ["winter_rye"]
                }
            ]
        )
        
        soil_conditions = SoilConditions(
            ph=6.8,
            organic_matter_percent=4.2,
            drainage_class="well_drained",
            texture="clay_loam"
        )
        
        result = await service._analyze_field_conditions_with_rotation(
            soil_conditions, rotation_plan
        )
        
        assert isinstance(result, dict)
        assert "nutrient_needs" in result
        assert "soil_health_status" in result
        assert "historical_performance" in result

    @pytest.mark.asyncio
    async def test_create_rotation_integration_timeline(self, service):
        """Test creation of rotation integration timeline."""
        integration_plan = CoverCropRotationIntegration(
            plan_id="test_timeline_001",
            integration_strategy="erosion_control",
            recommended_species=["winter_rye"],
            planting_windows=[
                CropTimingWindow(
                    crop="soybeans",
                    planting_window={"start": date(2024, 5, 1), "end": date(2024, 5, 31)},
                    cover_crop_window={"start": date(2023, 10, 1), "end": date(2024, 4, 15)}
                )
            ],
            termination_recommendations=[
                {
                    "species": "winter_rye",
                    "method": TerminationMethod.HERBICIDE,
                    "timing": "2 weeks before soybean planting"
                }
            ]
        )
        
        result = await service._create_rotation_integration_timeline(integration_plan)
        
        assert isinstance(result, dict)
        assert "planting_timeline" in result
        assert "management_timeline" in result
        assert "termination_timeline" in result

    @pytest.mark.asyncio
    async def test_generate_rotation_mixtures(self, service):
        """Test generation of rotation-specific mixtures."""
        integration_plan = CoverCropRotationIntegration(
            plan_id="test_mixtures_001",
            integration_strategy="balanced_benefits",
            recommended_species=["crimson_clover", "winter_rye"],
            planting_windows=[],
            termination_recommendations=[]
        )
        
        result = await service._generate_rotation_mixtures(integration_plan)
        
        assert isinstance(result, list)
        if result:  # If mixtures were generated
            assert all(isinstance(mixture, CoverCropMixture) for mixture in result)

    @pytest.mark.asyncio
    async def test_get_rotation_seasonal_considerations(self, service):
        """Test rotation seasonal considerations."""
        integration_plan = CoverCropRotationIntegration(
            plan_id="test_seasonal_001",
            integration_strategy="season_extension",
            recommended_species=["winter_rye"],
            planting_windows=[
                CropTimingWindow(
                    crop="corn",
                    planting_window={"start": date(2024, 4, 20), "end": date(2024, 5, 20)},
                    cover_crop_window={"start": date(2023, 9, 1), "end": date(2024, 4, 10)}
                )
            ],
            termination_recommendations=[]
        )
        
        location = {"latitude": 42.0, "longitude": -84.0}
        
        result = await service._get_rotation_seasonal_considerations(integration_plan, location)
        
        assert isinstance(result, dict)
        assert "seasonal_factors" in result
        assert "timing_adjustments" in result

    @pytest.mark.asyncio
    async def test_get_rotation_monitoring_recommendations(self, service):
        """Test rotation monitoring recommendations."""
        integration_plan = CoverCropRotationIntegration(
            plan_id="test_monitoring_001",
            integration_strategy="nutrient_cycling",
            recommended_species=["crimson_clover"],
            planting_windows=[],
            termination_recommendations=[]
        )
        
        result = await service._get_rotation_monitoring_recommendations(integration_plan)
        
        assert isinstance(result, list)
        assert all(isinstance(rec, str) for rec in result)

    @pytest.mark.asyncio
    async def test_get_rotation_follow_up_actions(self, service):
        """Test rotation follow-up actions."""
        integration_plan = CoverCropRotationIntegration(
            plan_id="test_followup_001",
            integration_strategy="continuous_improvement",
            recommended_species=["winter_rye"],
            planting_windows=[],
            termination_recommendations=[]
        )
        
        result = await service._get_rotation_follow_up_actions(integration_plan)
        
        assert isinstance(result, list)
        assert all(isinstance(action, str) for action in result)

    @pytest.mark.asyncio
    async def test_calculate_rotation_confidence(self, service):
        """Test rotation confidence calculation."""
        integration_plan = CoverCropRotationIntegration(
            plan_id="test_confidence_001",
            integration_strategy="proven_system",
            recommended_species=["crimson_clover"],
            planting_windows=[
                CropTimingWindow(
                    crop="corn",
                    planting_window={"start": date(2024, 5, 1), "end": date(2024, 5, 31)},
                    cover_crop_window={"start": date(2023, 9, 15), "end": date(2024, 4, 20)}
                )
            ],
            termination_recommendations=[
                {
                    "species": "crimson_clover",
                    "method": TerminationMethod.MECHANICAL,
                    "timing": "at 50% bloom"
                }
            ]
        )
        
        request = CoverCropSelectionRequest(
            request_id="test_confidence_001",
            location={"latitude": 40.5, "longitude": -85.5},
            field_size_acres=150.0,
            soil_conditions=SoilConditions(
                ph=6.5,
                organic_matter_percent=3.8,
                drainage_class="well_drained",
                texture="silt_loam"
            ),
            objectives=GoalBasedObjectives(
                specific_goals=[
                    SpecificGoal(
                        goal_id="goal_002",
                        goal_name="soil_health",
                        category=FarmerGoalCategory.SOIL_HEALTH,
                        target_benefit=SoilBenefit.ORGANIC_MATTER,
                        target_value=100.0,
                        priority=GoalPriority.MEDIUM,
                        weight=0.6
                    )
                ]
            ),
            planting_window={"start": date(2024, 10, 1), "end": date(2024, 10, 31)}
        )
        
        result = await service._calculate_rotation_confidence(integration_plan, request)
        
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    @pytest.mark.asyncio 
    async def test_generate_species_specific_recommendations(self, service):
        """Test species-specific recommendation generation."""
        request = CoverCropSelectionRequest(
            request_id="test_species_001",
            location={"latitude": 41.0, "longitude": -86.0},
            field_size_acres=80.0,
            soil_conditions=SoilConditions(
                ph=6.2,
                organic_matter_percent=3.0,
                drainage_class="moderately_well_drained",
                texture="loam"
            ),
            objectives=GoalBasedObjectives(
                specific_goals=[
                    SpecificGoal(
                        goal_id="goal_003",
                        goal_name="erosion_prevention",
                        category=FarmerGoalCategory.ENVIRONMENTAL,
                        target_benefit=SoilBenefit.EROSION_CONTROL,
                        target_value=90.0,
                        priority=GoalPriority.HIGH,
                        weight=0.9
                    )
                ]
            ),
            planting_window={"start": date(2024, 8, 15), "end": date(2024, 9, 15)}
        )
        
        # Mock goal-based service response
        mock_goal_response = Mock()
        mock_goal_response.recommended_species = [
            service.species_database["winter_rye"]
        ]
        mock_goal_response.goal_achievement_scores = {"environmental": 0.85}
        mock_goal_response.confidence_score = 0.88
        
        service.goal_based_service.generate_goal_based_recommendations = AsyncMock(
            return_value=mock_goal_response
        )
        
        result = await service._generate_species_specific_recommendations(request)
        
        assert isinstance(result, CoverCropSelectionResponse)
        assert result.request_id == "test_species_001"
        assert len(result.recommendations) > 0

    @pytest.mark.asyncio
    async def test_analyze_compatibility_economics_error_handling(self, service):
        """Test error handling in compatibility economics analysis."""
        # Test with invalid/missing data
        recommendations = []
        request = CoverCropSelectionRequest(
            request_id="test_error_001",
            location={"latitude": 40.0, "longitude": -85.0},
            field_size_acres=100.0,
            soil_conditions=SoilConditions(
                ph=6.5,
                organic_matter_percent=3.5,
                drainage_class="well_drained",
                texture="loam"
            ),
            objectives=GoalBasedObjectives(specific_goals=[]),
            planting_window={"start": date(2024, 9, 1), "end": date(2024, 10, 1)}
        )
        
        # Should handle empty recommendations gracefully
        result = await service._analyze_compatibility_economics(recommendations, request)
        
        assert isinstance(result, tuple)
        assert len(result) == 2  # (economic_analysis, compatibility_scores)

    @pytest.mark.asyncio
    async def test_initialization_error_handling(self):
        """Test initialization error handling."""
        service = CoverCropSelectionService()
        
        # Mock database loading to fail
        with patch.object(service, '_load_cover_crop_database', side_effect=Exception("Database error")):
            with pytest.raises(Exception, match="Database error"):
                await service.initialize()
        
        # Service should not be marked as initialized
        assert service.initialized is False

    @pytest.mark.asyncio
    async def test_health_check_with_exceptions(self, service):
        """Test health check with sub-service exceptions."""
        # Mock sub-service to raise exception
        service.main_crop_integration_service.health_check = AsyncMock(
            side_effect=Exception("Service unavailable")
        )
        service.timing_service.health_check = AsyncMock(return_value=True)
        
        result = await service.health_check()
        
        # Should return False when any sub-service fails
        assert result is False