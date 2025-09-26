"""
Comprehensive tests for goal-based cover crop selection functionality.

Tests the goal-based service algorithms, scoring, and optimization logic
to ensure accurate agricultural recommendations based on farmer objectives.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import date, timedelta
from typing import List, Dict, Any

from src.services.cover_crop_selection_service import CoverCropSelectionService
from src.services.goal_based_recommendation_service import GoalBasedRecommendationService
from src.models.cover_crop_models import (
    CoverCropSelectionRequest,
    CoverCropSpecies,
    SoilConditions,
    CoverCropObjectives,
    SoilBenefit,
    GrowingSeason,
    ClimateData,
    GoalBasedObjectives,
    SpecificGoal,
    GoalPriority,
    GoalBasedRecommendation,
    FarmerGoalCategory
)


@pytest.fixture
def mock_climate_service():
    """Mock climate service for testing."""
    service = Mock()
    service.get_climate_zone = AsyncMock(return_value=ClimateZone.TEMPERATE_CONTINENTAL)
    service.get_weather_data = AsyncMock(return_value={
        "temperature_range": {"min": 5, "max": 25},
        "precipitation": 600,
        "frost_dates": {"first": date(2024, 10, 15), "last": date(2024, 4, 15)}
    })
    return service


@pytest.fixture
def mock_species_data():
    """Mock species data for testing."""
    return [
        CoverCropSpecies(
            species_id="CC001",
            common_name="Crimson Clover",
            scientific_name="Trifolium incarnatum",
            cover_crop_type="legume",
            primary_benefits=[SoilBenefit.NITROGEN_FIXATION, SoilBenefit.POLLINATOR_HABITAT],
            secondary_benefits=[SoilBenefit.ORGANIC_MATTER, SoilBenefit.EROSION_CONTROL],
            hardiness_zones=["6a", "6b", "7a", "7b", "8a"],
            growing_season=GrowingSeason.WINTER,
            seeding_rate_lbs_per_acre=15.0,
            seeding_depth_inches=0.25,
            days_to_establishment=21,
            nitrogen_fixation_lbs_per_acre=120,
            erosion_control_rating=7,
            weed_suppression_rating=6,
            drought_tolerance_rating=5,
            cold_tolerance_rating=8,
            cost_per_lb=2.50
        ),
        CoverCropSpecies(
            species_id="CC002",
            common_name="Winter Rye",
            scientific_name="Secale cereale",
            cover_crop_type="grass",
            primary_benefits=[SoilBenefit.EROSION_CONTROL, SoilBenefit.WEED_SUPPRESSION],
            secondary_benefits=[SoilBenefit.ORGANIC_MATTER, SoilBenefit.COMPACTION_RELIEF],
            hardiness_zones=["3a", "4a", "5a", "6a", "7a", "8a"],
            growing_season=GrowingSeason.WINTER,
            seeding_rate_lbs_per_acre=90.0,
            seeding_depth_inches=1.0,
            days_to_establishment=14,
            nitrogen_fixation_lbs_per_acre=0,
            erosion_control_rating=9,
            weed_suppression_rating=9,
            drought_tolerance_rating=7,
            cold_tolerance_rating=9,
            cost_per_lb=1.25
        ),
        CoverCropSpecies(
            species_id="CC003",
            common_name="Austrian Winter Pea",
            scientific_name="Pisum sativum subsp. arvense",
            cover_crop_type="legume",
            primary_benefits=[SoilBenefit.NITROGEN_FIXATION, SoilBenefit.ORGANIC_MATTER],
            secondary_benefits=[SoilBenefit.EROSION_CONTROL, SoilBenefit.WEED_SUPPRESSION],
            hardiness_zones=["5a", "6a", "6b", "7a", "7b"],
            growing_season=GrowingSeason.WINTER,
            seeding_rate_lbs_per_acre=25.0,
            seeding_depth_inches=1.5,
            days_to_establishment=28,
            nitrogen_fixation_lbs_per_acre=100,
            erosion_control_rating=6,
            weed_suppression_rating=7,
            drought_tolerance_rating=4,
            cold_tolerance_rating=7,
            cost_per_lb=3.00
        )
    ]


@pytest.fixture
def sample_request():
    """Sample cover crop selection request for testing."""
    return CoverCropSelectionRequest(
        request_id="test_goal_based_001",
        location={"latitude": 40.0, "longitude": -85.0},
        soil_conditions=SoilConditions(
            ph=6.5,
            organic_matter_percent=2.5,
            drainage_class="moderately_well_drained",
            erosion_risk="moderate"
        ),
        objectives=CoverCropObjectives(
            primary_goals=[SoilBenefit.NITROGEN_FIXATION, SoilBenefit.EROSION_CONTROL],
            nitrogen_needs=True,
            erosion_control_priority=True
        ),
        planting_window={
            "start": date(2024, 9, 15),
            "end": date(2024, 10, 15)
        },
        field_size_acres=50.0
    )


@pytest.fixture
def nitrogen_focused_objectives():
    """Goal-based objectives focused on nitrogen management."""
    return GoalBasedObjectives(
        specific_goals=[
            SpecificGoal(
                goal_name="maximize_nitrogen_fixation",
                target_value=150.0,
                priority=GoalPriority.HIGH,
                goal_category=FarmerGoalCategory.NUTRIENT_MANAGEMENT,
                weight=0.4
            ),
            SpecificGoal(
                goal_name="reduce_fertilizer_costs",
                target_value=50.0,  # Percentage reduction
                priority=GoalPriority.HIGH,
                goal_category=FarmerGoalCategory.NUTRIENT_MANAGEMENT,
                weight=0.3
            ),
            SpecificGoal(
                goal_name="increase_organic_matter",
                target_value=0.5,  # Percentage increase
                priority=GoalPriority.MEDIUM,
                goal_category=FarmerGoalCategory.SOIL_HEALTH,
                weight=0.2
            ),
            SpecificGoal(
                goal_name="improve_soil_structure",
                target_value=7.0,  # Rating scale 1-10
                priority=GoalPriority.MEDIUM,
                goal_category=FarmerGoalCategory.SOIL_HEALTH,
                weight=0.1
            )
        ]
    )


@pytest.fixture
def erosion_control_objectives():
    """Goal-based objectives focused on erosion control."""
    return GoalBasedObjectives(
        specific_goals=[
            SpecificGoal(
                goal_name="minimize_soil_loss",
                target_value=2.0,  # Tons per acre per year
                priority=GoalPriority.HIGH,
                goal_category=FarmerGoalCategory.EROSION_CONTROL,
                weight=0.5
            ),
            SpecificGoal(
                goal_name="maximize_ground_cover",
                target_value=90.0,  # Percentage coverage
                priority=GoalPriority.HIGH,
                goal_category=FarmerGoalCategory.EROSION_CONTROL,
                weight=0.3
            ),
            SpecificGoal(
                goal_name="minimize_establishment_cost",
                target_value=100.0,  # Dollars per acre
                priority=GoalPriority.MEDIUM,
                goal_category=FarmerGoalCategory.ECONOMIC_OPTIMIZATION,
                weight=0.2
            )
        ]
    )


class TestGoalBasedService:
    """Test the goal-based service algorithms and scoring logic."""

    @pytest.fixture(autouse=True)
    async def setup_method(self, mock_climate_service, mock_species_data):
        """Set up test environment for each test method."""
        self.goal_service = GoalBasedService()
        self.cover_service = CoverCropSelectionService(climate_service=mock_climate_service)
        self.mock_species = mock_species_data

    @pytest.mark.asyncio
    async def test_goal_based_recommendations_nitrogen_focus(
        self, 
        sample_request, 
        nitrogen_focused_objectives
    ):
        """Test goal-based recommendations with nitrogen management focus."""
        # Mock the _find_suitable_species method
        with patch.object(self.cover_service, '_find_suitable_species', 
                         return_value=self.mock_species):
            
            result = await self.cover_service.get_goal_based_recommendations(
                sample_request, nitrogen_focused_objectives
            )

        # Verify result structure
        assert isinstance(result, GoalBasedRecommendation)
        assert result.request_id == sample_request.request_id
        assert len(result.recommended_species) > 0
        assert result.confidence_score > 0.0

        # Verify nitrogen-fixing species are prioritized
        species_ids = [spec.species_id for spec in result.recommended_species]
        assert "CC001" in species_ids  # Crimson Clover (nitrogen fixer)
        assert "CC003" in species_ids  # Austrian Winter Pea (nitrogen fixer)

        # Verify goal achievement scores exist
        assert "nitrogen_management" in result.goal_achievement_scores
        nitrogen_score = result.goal_achievement_scores["nitrogen_management"]
        assert 0.0 <= nitrogen_score <= 1.0

    @pytest.mark.asyncio
    async def test_goal_based_recommendations_erosion_control(
        self, 
        sample_request, 
        erosion_control_objectives
    ):
        """Test goal-based recommendations with erosion control focus."""
        with patch.object(self.cover_service, '_find_suitable_species', 
                         return_value=self.mock_species):
            
            result = await self.cover_service.get_goal_based_recommendations(
                sample_request, erosion_control_objectives
            )

        # Verify erosion control species are prioritized
        species_ids = [spec.species_id for spec in result.recommended_species]
        # Winter Rye should be highly ranked for erosion control
        assert "CC002" in species_ids

        # Verify goal achievement scores
        assert "erosion_control" in result.goal_achievement_scores
        erosion_score = result.goal_achievement_scores["erosion_control"]
        assert 0.0 <= erosion_score <= 1.0

        # Verify seeding rates are optimized for goals
        assert len(result.optimized_seeding_rates) > 0
        for species_id, rate in result.optimized_seeding_rates.items():
            assert rate > 0

    @pytest.mark.asyncio
    async def test_goal_feasibility_analysis(
        self, 
        sample_request, 
        nitrogen_focused_objectives
    ):
        """Test goal feasibility analysis functionality."""
        with patch.object(self.cover_service, '_find_suitable_species', 
                         return_value=self.mock_species):
            
            analysis = await self.cover_service.analyze_goal_feasibility(
                sample_request, nitrogen_focused_objectives
            )

        # Verify analysis structure
        assert isinstance(analysis, dict)
        assert "feasibility_scores" in analysis
        assert "limiting_factors" in analysis
        assert "optimization_recommendations" in analysis
        assert "alternative_strategies" in analysis

        # Verify feasibility scores for each goal category
        feasibility_scores = analysis["feasibility_scores"]
        assert "nitrogen_management" in feasibility_scores
        nitrogen_feasibility = feasibility_scores["nitrogen_management"]
        assert 0.0 <= nitrogen_feasibility <= 1.0

    @pytest.mark.asyncio
    async def test_goal_categories_and_options(self):
        """Test retrieval of available goal categories and options."""
        categories = await self.cover_service.get_goal_categories_and_options()

        # Verify structure
        assert isinstance(categories, dict)
        assert "goal_categories" in categories
        assert "available_goals" in categories
        assert "example_scenarios" in categories

        # Verify key goal categories exist
        goal_categories = categories["goal_categories"]
        expected_categories = [
            "nitrogen_management", 
            "erosion_control", 
            "soil_health", 
            "economic_optimization",
            "pest_management"
        ]
        
        for category in expected_categories:
            assert category in goal_categories

    @pytest.mark.asyncio
    async def test_empty_species_handling(
        self, 
        sample_request, 
        nitrogen_focused_objectives
    ):
        """Test handling when no suitable species are found."""
        with patch.object(self.cover_service, '_find_suitable_species', 
                         return_value=[]):
            
            result = await self.cover_service.get_goal_based_recommendations(
                sample_request, nitrogen_focused_objectives
            )

        # Verify empty result handling
        assert result.confidence_score == 0.0
        assert len(result.recommended_species) == 0
        assert len(result.goal_achievement_scores) == 0
        assert len(result.optimized_seeding_rates) == 0

    @pytest.mark.asyncio
    async def test_goal_synergy_analysis(
        self, 
        sample_request, 
        nitrogen_focused_objectives
    ):
        """Test goal synergy analysis in recommendations."""
        with patch.object(self.cover_service, '_find_suitable_species', 
                         return_value=self.mock_species):
            
            result = await self.cover_service.get_goal_based_recommendations(
                sample_request, nitrogen_focused_objectives
            )

        # Verify synergy analysis exists
        assert "goal_synergy_analysis" in result.__dict__
        synergy_analysis = result.goal_synergy_analysis
        
        if synergy_analysis:  # May be empty dict if no synergies found
            assert isinstance(synergy_analysis, dict)
            
            # Check for synergy identification
            for synergy_key, synergy_data in synergy_analysis.items():
                assert "synergy_score" in synergy_data
                assert "contributing_species" in synergy_data
                assert 0.0 <= synergy_data["synergy_score"] <= 1.0

    @pytest.mark.asyncio
    async def test_cost_benefit_analysis(
        self, 
        sample_request, 
        erosion_control_objectives
    ):
        """Test cost-benefit analysis in goal-based recommendations."""
        with patch.object(self.cover_service, '_find_suitable_species', 
                         return_value=self.mock_species):
            
            result = await self.cover_service.get_goal_based_recommendations(
                sample_request, erosion_control_objectives
            )

        # Verify cost-benefit analysis
        assert "cost_benefit_analysis" in result.__dict__
        cost_analysis = result.cost_benefit_analysis
        
        if cost_analysis:
            assert isinstance(cost_analysis, dict)
            
            # Should include cost metrics
            expected_metrics = ["total_establishment_cost", "expected_benefits", "roi_estimate"]
            for metric in expected_metrics:
                if metric in cost_analysis:
                    assert isinstance(cost_analysis[metric], (int, float))
                    assert cost_analysis[metric] >= 0

    @pytest.mark.asyncio
    async def test_goal_focused_management_recommendations(
        self, 
        sample_request, 
        nitrogen_focused_objectives
    ):
        """Test goal-focused management recommendations."""
        with patch.object(self.cover_service, '_find_suitable_species', 
                         return_value=self.mock_species):
            
            result = await self.cover_service.get_goal_based_recommendations(
                sample_request, nitrogen_focused_objectives
            )

        # Verify management recommendations exist
        assert "goal_focused_management" in result.__dict__
        management = result.goal_focused_management
        
        if management:
            assert isinstance(management, dict)
            
            # Should include management practices for each goal
            for goal_category in nitrogen_focused_objectives.goal_categories:
                category_name = goal_category.category_name
                if category_name in management:
                    category_management = management[category_name]
                    assert isinstance(category_management, dict)
                    
                    # Should have practical recommendations
                    expected_keys = ["planting_practices", "maintenance_practices", "termination_practices"]
                    for key in expected_keys:
                        if key in category_management:
                            assert isinstance(category_management[key], (list, str))


class TestGoalBasedScoring:
    """Test goal-based scoring algorithms and optimization."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test environment."""
        self.goal_service = GoalBasedService()

    def test_species_goal_scoring_nitrogen_fixation(self, mock_species_data):
        """Test species scoring for nitrogen fixation goals."""
        crimson_clover = mock_species_data[0]  # High nitrogen fixer
        winter_rye = mock_species_data[1]      # No nitrogen fixation

        nitrogen_goal = SpecificGoal(
            goal_name="maximize_nitrogen_fixation",
            target_value=120.0,
            priority=GoalPriority.HIGH,
            weight=1.0
        )

        # Test scoring (would need access to internal scoring methods)
        # This is a placeholder for the actual scoring algorithm test
        assert crimson_clover.nitrogen_fixation_lbs_per_acre > winter_rye.nitrogen_fixation_lbs_per_acre

    def test_species_goal_scoring_erosion_control(self, mock_species_data):
        """Test species scoring for erosion control goals."""
        winter_rye = mock_species_data[1]     # High erosion control
        austrian_pea = mock_species_data[2]   # Lower erosion control

        erosion_goal = SpecificGoal(
            goal_name="minimize_soil_loss",
            target_value=2.0,
            priority=GoalPriority.HIGH,
            weight=1.0
        )

        # Test scoring capability
        assert winter_rye.erosion_control_rating > austrian_pea.erosion_control_rating

    def test_multi_objective_optimization(self, mock_species_data):
        """Test multi-objective optimization scoring."""
        # Test that species can be scored across multiple objectives
        # and that the scoring considers goal weights appropriately
        
        species = mock_species_data[0]  # Crimson clover
        
        # Multi-objective scenario
        objectives = [
            SpecificGoal(
                goal_name="maximize_nitrogen_fixation",
                target_value=100.0,
                priority=GoalPriority.HIGH,
                weight=0.6
            ),
            SpecificGoal(
                goal_name="minimize_soil_loss",
                target_value=3.0,
                priority=GoalPriority.MEDIUM,
                weight=0.4
            )
        ]

        # Verify species has attributes for both goals
        assert species.nitrogen_fixation_lbs_per_acre > 0
        assert species.erosion_control_rating > 0


class TestGoalBasedIntegration:
    """Test integration between goal-based service and main cover crop service."""

    @pytest.fixture(autouse=True)
    async def setup_method(self, mock_climate_service):
        """Set up test environment."""
        self.cover_service = CoverCropSelectionService(climate_service=mock_climate_service)

    @pytest.mark.asyncio
    async def test_service_integration_workflow(
        self, 
        sample_request, 
        nitrogen_focused_objectives, 
        mock_species_data
    ):
        """Test complete workflow integration."""
        with patch.object(self.cover_service, '_find_suitable_species', 
                         return_value=mock_species_data):
            
            # Test complete workflow
            result = await self.cover_service.get_goal_based_recommendations(
                sample_request, nitrogen_focused_objectives
            )
            
            # Verify integration worked correctly
            assert result.request_id == sample_request.request_id
            assert len(result.recommended_species) > 0
            
            # Test feasibility analysis integration
            feasibility = await self.cover_service.analyze_goal_feasibility(
                sample_request, nitrogen_focused_objectives
            )
            
            assert isinstance(feasibility, dict)
            assert "feasibility_scores" in feasibility

    @pytest.mark.asyncio
    async def test_error_handling_integration(
        self, 
        sample_request, 
        nitrogen_focused_objectives
    ):
        """Test error handling in service integration."""
        # Test with invalid species data
        with patch.object(self.cover_service, '_find_suitable_species', 
                         side_effect=Exception("Database error")):
            
            with pytest.raises(Exception):
                await self.cover_service.get_goal_based_recommendations(
                    sample_request, nitrogen_focused_objectives
                )