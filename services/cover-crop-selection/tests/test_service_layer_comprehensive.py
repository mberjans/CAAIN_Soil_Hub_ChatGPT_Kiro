"""
Comprehensive Service Layer Tests for Cover Crop Selection Service

This module provides extensive unit tests for the core service layer business logic,
focusing on algorithms, calculations, and service interactions that were identified
as undertested in the coverage analysis.

Test Coverage:
1. Core selection algorithms and scoring
2. Species matching and filtering logic  
3. Climate integration and adaptation
4. Soil suitability calculations
5. Economic analysis and optimization
6. Service integration and error handling
7. Edge cases and boundary conditions
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
    GoalBasedObjectives
)


@pytest.fixture
def service():
    """Cover crop selection service fixture."""
    return CoverCropSelectionService()


@pytest.fixture
def sample_species_database():
    """Sample species database for testing."""
    return {
        "crimson_clover": CoverCropSpecies(
            species_id="crimson_clover",
            common_name="Crimson Clover",
            scientific_name="Trifolium incarnatum",
            cover_crop_type=CoverCropType.LEGUME,
            hardiness_zones=["6a", "6b", "7a", "7b", "8a"],
            growing_season=GrowingSeason.WINTER,
            ph_range={"min": 5.5, "max": 7.5},
            drainage_tolerance=["well_drained", "moderately_well_drained"],
            seeding_rate_lbs_acre={"broadcast": 15.0, "drill": 12.0},
            planting_depth_inches=0.25,
            days_to_establishment=14,
            biomass_production="moderate",
            primary_benefits=[SoilBenefit.NITROGEN_FIXATION, SoilBenefit.EROSION_CONTROL],
            nitrogen_fixation_lbs_acre=120.0,
            termination_methods=["frost_kill", "herbicide", "mowing"],
            cash_crop_compatibility=["corn", "soybean", "wheat"],
            seed_cost_per_acre=52.5
        ),
        "winter_rye": CoverCropSpecies(
            species_id="winter_rye",
            common_name="Winter Rye",
            scientific_name="Secale cereale",
            cover_crop_type=CoverCropType.GRASS,
            hardiness_zones=["3a", "3b", "4a", "4b", "5a", "5b", "6a", "6b", "7a", "7b", "8a"],
            growing_season=GrowingSeason.WINTER,
            ph_range={"min": 5.0, "max": 8.0},
            drainage_tolerance=["well_drained", "moderately_well_drained", "somewhat_poorly_drained"],
            seeding_rate_lbs_acre={"broadcast": 90.0, "drill": 70.0},
            planting_depth_inches=1.0,
            days_to_establishment=7,
            biomass_production="high",
            primary_benefits=[SoilBenefit.EROSION_CONTROL, SoilBenefit.ORGANIC_MATTER],
            nitrogen_fixation_lbs_acre=0.0,
            termination_methods=["herbicide", "mowing", "tillage"],
            cash_crop_compatibility=["corn", "soybean", "cotton"],
            seed_cost_per_acre=32.0
        ),
        "radish": CoverCropSpecies(
            species_id="radish",
            common_name="Forage Radish",
            scientific_name="Raphanus sativus",
            cover_crop_type=CoverCropType.BRASSICA,
            hardiness_zones=["5a", "5b", "6a", "6b", "7a", "7b", "8a", "8b"],
            growing_season=GrowingSeason.FALL,
            ph_range={"min": 6.0, "max": 7.5},
            drainage_tolerance=["well_drained", "moderately_well_drained"],
            seeding_rate_lbs_acre={"broadcast": 12.0, "drill": 8.0},
            planting_depth_inches=0.5,
            days_to_establishment=5,
            biomass_production="moderate",
            primary_benefits=[SoilBenefit.COMPACTION_RELIEF, SoilBenefit.NUTRIENT_SCAVENGING],
            nitrogen_fixation_lbs_acre=0.0,
            termination_methods=["frost_kill", "tillage"],
            cash_crop_compatibility=["corn", "soybean"],
            seed_cost_per_acre=48.0
        )
    }


@pytest.fixture
def sample_selection_request():
    """Sample cover crop selection request."""
    return CoverCropSelectionRequest(
        request_id="test_service_001",
        location={
            "latitude": 40.7128,
            "longitude": -74.0060
        },
        soil_conditions=SoilConditions(
            ph=6.2,
            organic_matter_percent=2.8,
            drainage_class="moderately_well_drained",
            erosion_risk="moderate",
            compaction_level="slight",
            test_date=date(2024, 3, 15)
        ),
        objectives=CoverCropObjectives(
            primary_goals=[SoilBenefit.NITROGEN_FIXATION, SoilBenefit.EROSION_CONTROL],
            nitrogen_needs=True,
            budget_per_acre=75.0,
            organic_matter_goal=False,
            erosion_control_priority=True
        ),
        planting_window={
            "start": date(2024, 9, 15),
            "end": date(2024, 10, 15)
        },
        field_size_acres=25.0
    )


@pytest.fixture  
def sample_climate_data():
    """Sample climate data for testing."""
    return {
        "climate_zone": "7a",
        "average_annual_precipitation_inches": 42.5,
        "frost_dates": {
            "first_fall_frost": "2024-11-01",
            "last_spring_frost": "2024-04-15"
        },
        "growing_season_length_days": 200,
        "temperature_ranges": {
            "winter": {"min": 15, "max": 45},
            "spring": {"min": 35, "max": 70},
            "summer": {"min": 60, "max": 85},
            "fall": {"min": 40, "max": 70}
        }
    }


class TestCoverCropSelectionAlgorithms:
    """Test core selection algorithms and scoring logic."""
    
    @pytest.mark.asyncio
    async def test_species_scoring_algorithm(self, service, sample_species_database, sample_selection_request):
        """Test the species scoring algorithm for different species types."""
        # Mock the species database
        service.species_database = sample_species_database
        
        # Test scoring for different species
        crimson_clover = sample_species_database["crimson_clover"]
        winter_rye = sample_species_database["winter_rye"]
        radish = sample_species_database["radish"]
        
        # Calculate scores using the service's internal scoring method
        clover_score = await service._calculate_species_score(crimson_clover, sample_selection_request)
        rye_score = await service._calculate_species_score(winter_rye, sample_selection_request)
        radish_score = await service._calculate_species_score(radish, sample_selection_request)
        
        # Assertions based on request objectives (nitrogen fixation + erosion control)
        # Crimson clover should score highest (legume with nitrogen fixation)
        assert clover_score > rye_score, "Clover should score higher than rye for nitrogen fixation needs"
        assert clover_score > radish_score, "Clover should score higher than radish for nitrogen fixation needs"
        
        # All scores should be between 0 and 1
        for score in [clover_score, rye_score, radish_score]:
            assert 0.0 <= score <= 1.0, f"Score {score} should be between 0 and 1"
            
    @pytest.mark.asyncio
    async def test_soil_ph_compatibility_scoring(self, service, sample_species_database, sample_selection_request):
        """Test soil pH compatibility scoring algorithm."""
        service.species_database = sample_species_database
        
        # Test with optimal pH for crimson clover (6.2 is within 5.5-7.5 range)
        clover = sample_species_database["crimson_clover"]
        optimal_score = await service._calculate_ph_compatibility_score(clover, sample_selection_request.soil_conditions.ph)
        
        # Test with suboptimal pH
        sample_selection_request.soil_conditions.ph = 4.5  # Too acidic for clover
        suboptimal_score = await service._calculate_ph_compatibility_score(clover, sample_selection_request.soil_conditions.ph)
        
        assert optimal_score > suboptimal_score, "Optimal pH should score higher than suboptimal pH"
        assert optimal_score > 0.8, "Optimal pH should score highly"
        assert suboptimal_score < 0.5, "Suboptimal pH should score poorly"
        
    @pytest.mark.asyncio
    async def test_objective_alignment_scoring(self, service, sample_species_database, sample_selection_request):
        """Test objective alignment scoring algorithm."""
        service.species_database = sample_species_database
        
        # Test nitrogen fixation objective alignment
        clover = sample_species_database["crimson_clover"]  # Nitrogen fixer
        rye = sample_species_database["winter_rye"]  # Non-nitrogen fixer
        
        clover_n_score = await service._calculate_objective_alignment_score(clover, sample_selection_request.objectives)
        rye_n_score = await service._calculate_objective_alignment_score(rye, sample_selection_request.objectives)
        
        assert clover_n_score > rye_n_score, "Nitrogen-fixing species should score higher for nitrogen objectives"
        
        # Test with different objectives
        sample_selection_request.objectives.primary_goals = [SoilBenefit.COMPACTION_RELIEF]
        sample_selection_request.objectives.nitrogen_needs = False
        
        radish = sample_species_database["radish"]  # Good for compaction relief
        radish_score = await service._calculate_objective_alignment_score(radish, sample_selection_request.objectives)
        clover_compaction_score = await service._calculate_objective_alignment_score(clover, sample_selection_request.objectives)
        
        assert radish_score > clover_compaction_score, "Radish should score higher for compaction relief objectives"
        
    @pytest.mark.asyncio
    async def test_economic_feasibility_scoring(self, service, sample_species_database, sample_selection_request):
        """Test economic feasibility scoring algorithm."""
        service.species_database = sample_species_database
        
        # Test with different budget constraints
        clover = sample_species_database["crimson_clover"]
        
        # High budget scenario
        high_budget_score = await service._calculate_economic_feasibility_score(
            clover, 
            sample_selection_request.field_size_acres, 
            budget_per_acre=150.0
        )
        
        # Low budget scenario  
        low_budget_score = await service._calculate_economic_feasibility_score(
            clover,
            sample_selection_request.field_size_acres,
            budget_per_acre=25.0
        )
        
        assert high_budget_score > low_budget_score, "Higher budget should result in higher feasibility score"
        
        # Test cost calculation accuracy
        expected_cost = clover.seeding_rate_lbs_per_acre * 3.50  # Assume $3.50/lb seed cost
        calculated_cost = await service._calculate_species_cost_per_acre(clover)
        
        assert abs(calculated_cost - expected_cost) < 5.0, "Cost calculation should be reasonably accurate"


class TestSpeciesMatchingAndFiltering:
    """Test species matching and filtering algorithms."""
    
    @pytest.mark.asyncio
    async def test_climate_zone_filtering(self, service, sample_species_database, sample_climate_data):
        """Test climate zone compatibility filtering."""
        service.species_database = sample_species_database
        
        # Mock climate data retrieval
        with patch.object(service, '_get_climate_data', return_value=sample_climate_data):
            # Test filtering for zone 7a climate
            compatible_species = await service._filter_by_climate_compatibility(
                list(sample_species_database.values()),
                sample_climate_data
            )
            
            # All test species should be compatible with zone 7a
            species_ids = [s.species_id for s in compatible_species]
            assert "crimson_clover" in species_ids, "Crimson clover should be compatible with zone 7a"
            assert "winter_rye" in species_ids, "Winter rye should be compatible with zone 7a"
            assert "radish" in species_ids, "Radish should be compatible with zone 7a"
            
            # Test with extreme climate
            extreme_climate = sample_climate_data.copy()
            extreme_climate["climate_zone"] = "2a"  # Very cold zone
            
            cold_compatible = await service._filter_by_climate_compatibility(
                list(sample_species_database.values()),
                extreme_climate
            )
            
            # Only winter rye should survive zone 2a
            cold_species_ids = [s.species_id for s in cold_compatible]
            assert "winter_rye" in cold_species_ids, "Winter rye should survive zone 2a"
            assert "crimson_clover" not in cold_species_ids, "Crimson clover should not survive zone 2a"
            
    @pytest.mark.asyncio
    async def test_growing_season_filtering(self, service, sample_species_database):
        """Test growing season compatibility filtering."""
        service.species_database = sample_species_database
        
        # Test winter planting window
        winter_planting = {
            "start": date(2024, 9, 15),
            "end": date(2024, 10, 15)
        }
        
        winter_species = await service._filter_by_growing_season(
            list(sample_species_database.values()),
            winter_planting
        )
        
        winter_ids = [s.species_id for s in winter_species]
        assert "crimson_clover" in winter_ids, "Crimson clover should be suitable for winter planting"
        assert "winter_rye" in winter_ids, "Winter rye should be suitable for winter planting"
        
        # Test fall planting window
        fall_planting = {
            "start": date(2024, 8, 1),
            "end": date(2024, 9, 30)
        }
        
        fall_species = await service._filter_by_growing_season(
            list(sample_species_database.values()),
            fall_planting
        )
        
        fall_ids = [s.species_id for s in fall_species]
        assert "radish" in fall_ids, "Radish should be suitable for fall planting"
        
    @pytest.mark.asyncio
    async def test_soil_suitability_filtering(self, service, sample_species_database, sample_selection_request):
        """Test soil suitability filtering algorithms."""
        service.species_database = sample_species_database
        
        # Test with optimal soil conditions
        suitable_species = await service._filter_by_soil_suitability(
            list(sample_species_database.values()),
            sample_selection_request.soil_conditions
        )
        
        # All species should be suitable for moderate conditions
        assert len(suitable_species) >= 2, "Multiple species should be suitable for moderate soil conditions"
        
        # Test with extreme pH
        extreme_soil = sample_selection_request.soil_conditions.copy()
        extreme_soil.ph = 4.0  # Very acidic
        
        acid_suitable = await service._filter_by_soil_suitability(
            list(sample_species_database.values()),
            extreme_soil
        )
        
        # Winter rye should be more tolerant of extreme pH
        acid_ids = [s.species_id for s in acid_suitable]
        assert "winter_rye" in acid_ids, "Winter rye should tolerate acidic soil"
        
    @pytest.mark.asyncio
    async def test_drainage_compatibility_filtering(self, service, sample_species_database):
        """Test drainage compatibility filtering."""
        service.species_database = sample_species_database
        
        # Test with poor drainage
        poor_drainage_soil = SoilConditions(
            ph=6.5,
            organic_matter_percent=3.0,
            drainage_class="poorly_drained",
            erosion_risk="low"
        )
        
        drainage_suitable = await service._filter_by_drainage_compatibility(
            list(sample_species_database.values()),
            poor_drainage_soil
        )
        
        # Species with poor flood tolerance should be filtered out
        suitable_ids = [s.species_id for s in drainage_suitable]
        
        # Winter rye has moderate flood tolerance, should survive
        assert "winter_rye" in suitable_ids, "Winter rye should handle poor drainage"
        
        # Crimson clover and radish have poor flood tolerance
        for species_id in ["crimson_clover", "radish"]:
            if species_id in suitable_ids:
                # If they pass, it should be with a low suitability score
                species = sample_species_database[species_id]
                score = await service._calculate_drainage_compatibility_score(species, poor_drainage_soil)
                assert score < 0.5, f"{species_id} should have low score for poor drainage"


class TestClimateIntegration:
    """Test climate data integration and adaptation algorithms."""
    
    @pytest.mark.asyncio
    async def test_climate_data_retrieval(self, service, sample_selection_request):
        """Test climate data retrieval and caching."""
        mock_climate_response = {
            "climate_zone": "7a",
            "average_annual_precipitation_inches": 42.5,
            "frost_dates": {
                "first_fall_frost": "2024-11-01",
                "last_spring_frost": "2024-04-15"
            }
        }
        
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_climate_response
            mock_get.return_value = mock_response
            
            # First call should retrieve from API
            climate_data = await service._get_climate_data(
                sample_selection_request.location["latitude"],
                sample_selection_request.location["longitude"]
            )
            
            assert climate_data["climate_zone"] == "7a"
            assert mock_get.called, "Should call external climate API"
            
            # Test error handling
            mock_get.side_effect = Exception("Network error")
            
            # Should handle gracefully and return default data
            default_climate = await service._get_climate_data(40.0, -74.0)
            assert default_climate is not None, "Should return default climate data on error"
            
    @pytest.mark.asyncio
    async def test_frost_date_adaptation(self, service, sample_species_database, sample_climate_data):
        """Test frost date adaptation for planting recommendations."""
        service.species_database = sample_species_database
        
        # Test early frost scenario
        early_frost_climate = sample_climate_data.copy()
        early_frost_climate["frost_dates"]["first_fall_frost"] = "2024-10-15"  # Early frost
        
        adapted_recommendations = await service._adapt_for_frost_dates(
            list(sample_species_database.values()),
            early_frost_climate
        )
        
        # Should prioritize cold-hardy species
        hardy_ids = [r.species_id for r in adapted_recommendations]
        winter_rye_rank = hardy_ids.index("winter_rye") if "winter_rye" in hardy_ids else 999
        clover_rank = hardy_ids.index("crimson_clover") if "crimson_clover" in hardy_ids else 999
        
        assert winter_rye_rank < clover_rank, "Winter rye should rank higher with early frost"
        
    @pytest.mark.asyncio
    async def test_precipitation_adaptation(self, service, sample_species_database, sample_climate_data):
        """Test precipitation-based adaptation algorithms."""
        service.species_database = sample_species_database
        
        # Test drought scenario
        drought_climate = sample_climate_data.copy()
        drought_climate["average_annual_precipitation_inches"] = 15.0  # Very dry
        
        drought_adapted = await service._adapt_for_precipitation(
            list(sample_species_database.values()),
            drought_climate
        )
        
        # Should prioritize drought-tolerant species
        adapted_ids = [s.species_id for s in drought_adapted]
        
        # Winter rye has high drought tolerance
        assert "winter_rye" in adapted_ids, "Winter rye should be recommended for drought conditions"
        
        # Test wet scenario
        wet_climate = sample_climate_data.copy()
        wet_climate["average_annual_precipitation_inches"] = 80.0  # Very wet
        
        wet_adapted = await service._adapt_for_precipitation(
            list(sample_species_database.values()),
            wet_climate
        )
        
        # Should consider flood tolerance
        wet_ids = [s.species_id for s in wet_adapted]
        assert len(wet_ids) > 0, "Should have recommendations for wet conditions"


class TestEconomicAnalysis:
    """Test economic analysis and optimization algorithms."""
    
    @pytest.mark.asyncio
    async def test_cost_benefit_analysis(self, service, sample_species_database, sample_selection_request):
        """Test cost-benefit analysis calculations."""
        service.species_database = sample_species_database
        
        clover = sample_species_database["crimson_clover"]
        
        # Calculate cost-benefit for nitrogen fixation
        cost_benefit = await service._calculate_cost_benefit_analysis(
            clover,
            sample_selection_request.field_size_acres,
            sample_selection_request.objectives
        )
        
        assert "total_cost" in cost_benefit, "Should include total cost"
        assert "total_benefits" in cost_benefit, "Should include total benefits"
        assert "roi" in cost_benefit, "Should include ROI calculation"
        assert "payback_period_years" in cost_benefit, "Should include payback period"
        
        # ROI should be positive for nitrogen-fixing crop with nitrogen needs
        assert cost_benefit["roi"] > 0, "ROI should be positive for aligned objectives"
        
        # Test with misaligned objectives
        misaligned_objectives = sample_selection_request.objectives.copy()
        misaligned_objectives.primary_goals = [SoilBenefit.COMPACTION_RELIEF]
        misaligned_objectives.nitrogen_needs = False
        
        misaligned_analysis = await service._calculate_cost_benefit_analysis(
            clover,
            sample_selection_request.field_size_acres,
            misaligned_objectives
        )
        
        # ROI should be lower for misaligned objectives
        assert misaligned_analysis["roi"] < cost_benefit["roi"], "Misaligned objectives should have lower ROI"
        
    @pytest.mark.asyncio
    async def test_budget_optimization(self, service, sample_species_database, sample_selection_request):
        """Test budget constraint optimization."""
        service.species_database = sample_species_database
        
        # Test with tight budget
        tight_budget_request = sample_selection_request.copy()
        tight_budget_request.objectives.budget_per_acre = 30.0  # Very tight budget
        
        optimized_recommendations = await service._optimize_for_budget(
            list(sample_species_database.values()),
            tight_budget_request
        )
        
        # Should prioritize cost-effective options
        assert len(optimized_recommendations) > 0, "Should return some recommendations even with tight budget"
        
        # Calculate costs for verification
        for rec in optimized_recommendations:
            species = sample_species_database[rec.species_id]
            estimated_cost = await service._calculate_species_cost_per_acre(species)
            assert estimated_cost <= tight_budget_request.objectives.budget_per_acre * 1.1, \
                "Recommendations should respect budget constraints (with small tolerance)"
                
    @pytest.mark.asyncio
    async def test_value_per_dollar_optimization(self, service, sample_species_database, sample_selection_request):
        """Test value-per-dollar optimization algorithm."""
        service.species_database = sample_species_database
        
        # Calculate value per dollar for each species
        value_rankings = []
        
        for species in sample_species_database.values():
            cost = await service._calculate_species_cost_per_acre(species)
            benefits_value = await service._calculate_benefits_monetary_value(
                species, 
                sample_selection_request.objectives
            )
            
            if cost > 0:
                value_per_dollar = benefits_value / cost
                value_rankings.append((species.species_id, value_per_dollar))
        
        # Sort by value per dollar
        value_rankings.sort(key=lambda x: x[1], reverse=True)
        
        assert len(value_rankings) > 0, "Should calculate value rankings for species"
        
        # Best value species should have reasonable value/cost ratio
        best_species_id, best_ratio = value_rankings[0]
        assert best_ratio > 1.0, "Best value species should have positive return"


class TestServiceIntegration:
    """Test integration between different service components."""
    
    @pytest.mark.asyncio
    async def test_timing_service_integration(self, service, sample_selection_request):
        """Test integration with timing service."""
        # Mock timing service
        service.timing_service = MagicMock()
        mock_timing_response = {
            "species_id": "crimson_clover",
            "optimal_planting_window": {
                "start": "2024-09-01",
                "end": "2024-10-15"
            },
            "termination_recommendations": []
        }
        service.timing_service.generate_comprehensive_timing_recommendation.return_value = mock_timing_response
        
        # Test timing integration in selection process
        recommendations = await service._integrate_timing_recommendations(
            ["crimson_clover"],
            sample_selection_request
        )
        
        assert len(recommendations) > 0, "Should return timing-integrated recommendations"
        assert service.timing_service.generate_comprehensive_timing_recommendation.called, \
            "Should call timing service"
            
    @pytest.mark.asyncio
    async def test_goal_based_service_integration(self, service, sample_selection_request):
        """Test integration with goal-based recommendation service."""
        # Mock goal-based service
        service.goal_based_service = MagicMock()
        mock_goal_response = {
            "goal_optimized_recommendations": [
                {
                    "species_id": "crimson_clover",
                    "goal_achievement_scores": {"production": 0.8},
                    "priority_weighted_score": 0.85
                }
            ]
        }
        service.goal_based_service.generate_goal_based_recommendations.return_value = mock_goal_response
        
        # Test goal-based integration
        goal_objectives = GoalBasedObjectives(
            farmer_goals=[
                {
                    "category": "production",
                    "specific_goal": "yield_optimization",
                    "priority_weight": 1.0
                }
            ]
        )
        
        goal_recommendations = await service.get_goal_based_recommendations(
            sample_selection_request,
            goal_objectives
        )
        
        assert "goal_optimized_recommendations" in goal_recommendations, \
            "Should return goal-based recommendations"
        assert service.goal_based_service.generate_goal_based_recommendations.called, \
            "Should call goal-based service"
            
    @pytest.mark.asyncio
    async def test_main_crop_integration_service(self, service, sample_selection_request):
        """Test integration with main crop integration service."""
        # Mock main crop integration service
        service.main_crop_integration_service = MagicMock()
        mock_integration_response = {
            "compatibility_analysis": {
                "crimson_clover": {
                    "compatibility_score": 0.9,
                    "benefits": ["nitrogen_fixation"],
                    "risks": []
                }
            }
        }
        service.main_crop_integration_service.analyze_rotation_compatibility.return_value = mock_integration_response
        
        # Test main crop integration
        rotation_recommendations = await service.get_rotation_integration_recommendations(
            "corn_soybean",
            sample_selection_request
        )
        
        assert "rotation_specific_recommendations" in rotation_recommendations, \
            "Should return rotation-specific recommendations"
            
    @pytest.mark.asyncio
    async def test_benefit_tracking_integration(self, service, sample_selection_request):
        """Test integration with benefit tracking service."""
        # Mock benefit tracking service
        service.benefit_tracking_service = MagicMock()
        mock_tracking_response = {
            "tracking_id": "track_001",
            "predicted_benefits": {
                "nitrogen_fixation": {"value": 120, "confidence": 0.8}
            }
        }
        service.benefit_tracking_service.setup_field_tracking.return_value = mock_tracking_response
        
        # Test benefit tracking integration
        response, tracking_data = await service.select_cover_crops_with_benefit_tracking(
            sample_selection_request,
            enable_benefit_tracking=True
        )
        
        assert tracking_data is not None, "Should return tracking data"
        assert "tracking_id" in tracking_data, "Should include tracking ID"


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.mark.asyncio
    async def test_empty_species_database_handling(self, service, sample_selection_request):
        """Test handling of empty species database."""
        service.species_database = {}  # Empty database
        
        with pytest.raises(Exception) as exc_info:
            await service.select_cover_crops(sample_selection_request)
        
        assert "no species available" in str(exc_info.value).lower() or \
               "empty database" in str(exc_info.value).lower() or \
               len(str(exc_info.value)) > 0, "Should raise meaningful error for empty database"
               
    @pytest.mark.asyncio
    async def test_invalid_coordinates_handling(self, service, sample_selection_request):
        """Test handling of invalid coordinates."""
        # Set invalid coordinates
        sample_selection_request.location["latitude"] = 95.0  # Invalid latitude
        sample_selection_request.location["longitude"] = 185.0  # Invalid longitude
        
        with pytest.raises(Exception) as exc_info:
            await service._get_climate_data(95.0, 185.0)
        
        # Should raise validation error or handle gracefully
        assert len(str(exc_info.value)) > 0, "Should raise error for invalid coordinates"
        
    @pytest.mark.asyncio
    async def test_network_failure_handling(self, service, sample_selection_request):
        """Test handling of network failures."""
        with patch('httpx.AsyncClient.get', side_effect=Exception("Network timeout")):
            # Should handle network failures gracefully
            try:
                climate_data = await service._get_climate_data(40.0, -74.0)
                # If it doesn't raise, should return default/fallback data
                assert climate_data is not None, "Should return fallback data on network failure"
            except Exception as e:
                # If it raises, should be a meaningful error
                assert "network" in str(e).lower() or "timeout" in str(e).lower() or \
                       "connection" in str(e).lower(), "Should raise meaningful network error"
                       
    @pytest.mark.asyncio
    async def test_extreme_input_values_handling(self, service, sample_species_database, sample_selection_request):
        """Test handling of extreme input values."""
        service.species_database = sample_species_database
        
        # Test extremely large field size
        sample_selection_request.field_size_acres = 100000.0  # 100,000 acres
        
        # Should handle without crashing
        recommendations = await service.select_cover_crops(sample_selection_request)
        assert recommendations is not None, "Should handle large field sizes"
        
        # Test extremely small field size
        sample_selection_request.field_size_acres = 0.01  # Very small field
        
        small_field_recommendations = await service.select_cover_crops(sample_selection_request)
        assert small_field_recommendations is not None, "Should handle small field sizes"
        
        # Test extreme pH values
        sample_selection_request.soil_conditions.ph = 2.0  # Extremely acidic
        
        extreme_ph_recommendations = await service.select_cover_crops(sample_selection_request)
        assert extreme_ph_recommendations is not None, "Should handle extreme pH values"
        
    @pytest.mark.asyncio
    async def test_missing_optional_data_handling(self, service, sample_species_database, sample_selection_request):
        """Test handling of missing optional data."""
        service.species_database = sample_species_database
        
        # Remove optional budget constraint
        sample_selection_request.objectives.budget_per_acre = None
        
        # Should handle missing budget gracefully
        recommendations = await service.select_cover_crops(sample_selection_request)
        assert recommendations is not None, "Should handle missing budget constraint"
        
        # Remove optional soil test date
        sample_selection_request.soil_conditions.test_date = None
        
        no_date_recommendations = await service.select_cover_crops(sample_selection_request)
        assert no_date_recommendations is not None, "Should handle missing test date"


class TestBoundaryConditions:
    """Test boundary conditions and edge cases."""
    
    @pytest.mark.asyncio
    async def test_boundary_ph_values(self, service, sample_species_database):
        """Test pH boundary value handling."""
        service.species_database = sample_species_database
        
        clover = sample_species_database["crimson_clover"]
        
        # Test at exact pH boundaries
        min_ph_score = await service._calculate_ph_compatibility_score(clover, 5.5)  # Minimum
        max_ph_score = await service._calculate_ph_compatibility_score(clover, 7.5)  # Maximum
        optimal_ph_score = await service._calculate_ph_compatibility_score(clover, 6.5)  # Optimal
        
        # Boundary values should score reasonably well
        assert min_ph_score > 0.7, "Minimum pH boundary should score well"
        assert max_ph_score > 0.7, "Maximum pH boundary should score well"
        assert optimal_ph_score >= min_ph_score, "Optimal pH should score as well as boundaries"
        assert optimal_ph_score >= max_ph_score, "Optimal pH should score as well as boundaries"
        
    @pytest.mark.asyncio
    async def test_zero_budget_constraint(self, service, sample_species_database, sample_selection_request):
        """Test zero budget constraint handling."""
        service.species_database = sample_species_database
        
        # Set zero budget
        sample_selection_request.objectives.budget_per_acre = 0.0
        
        # Should either return low-cost options or handle gracefully
        try:
            recommendations = await service.select_cover_crops(sample_selection_request)
            assert recommendations is not None, "Should handle zero budget"
            
            # If it returns recommendations, they should be minimal cost
            if hasattr(recommendations, 'single_species_recommendations') and recommendations.single_species_recommendations:
                for rec in recommendations.single_species_recommendations:
                    species = sample_species_database[rec.species_id]
                    cost = await service._calculate_species_cost_per_acre(species)
                    assert cost <= 10.0, "Zero budget should return very low-cost options"
                    
        except Exception as e:
            # If it raises an exception, should be budget-related
            assert "budget" in str(e).lower() or "cost" in str(e).lower(), \
                "Zero budget error should be budget-related"
                
    @pytest.mark.asyncio
    async def test_very_short_planting_window(self, service, sample_species_database, sample_selection_request):
        """Test very short planting window handling."""
        service.species_database = sample_species_database
        
        # Set very short planting window (1 day)
        sample_selection_request.planting_window = {
            "start": date(2024, 9, 15),
            "end": date(2024, 9, 15)  # Same day
        }
        
        recommendations = await service.select_cover_crops(sample_selection_request)
        assert recommendations is not None, "Should handle very short planting windows"
        
        # Should prefer fast-establishing species
        if hasattr(recommendations, 'single_species_recommendations') and recommendations.single_species_recommendations:
            for rec in recommendations.single_species_recommendations:
                species = sample_species_database[rec.species_id]
                assert species.days_to_establishment <= 14, \
                    "Short window should prefer fast-establishing species"
                    
    @pytest.mark.asyncio
    async def test_conflicting_objectives_handling(self, service, sample_species_database, sample_selection_request):
        """Test handling of conflicting objectives."""
        service.species_database = sample_species_database
        
        # Set conflicting objectives
        sample_selection_request.objectives.primary_goals = [
            SoilBenefit.NITROGEN_FIXATION,  # Typically legumes
            SoilBenefit.COMPACTION_RELIEF   # Typically brassicas
        ]
        sample_selection_request.objectives.nitrogen_needs = True
        sample_selection_request.objectives.budget_per_acre = 25.0  # Low budget
        
        # Should handle conflicting objectives and find best compromise
        recommendations = await service.select_cover_crops(sample_selection_request)
        assert recommendations is not None, "Should handle conflicting objectives"
        
        # Should provide balanced recommendations or clear prioritization
        if hasattr(recommendations, 'single_species_recommendations'):
            assert len(recommendations.single_species_recommendations) > 0, \
                "Should provide some recommendations despite conflicts"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])