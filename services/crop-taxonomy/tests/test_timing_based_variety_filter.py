"""
Comprehensive Tests for Timing-Based Variety Filtering Service

Tests the sophisticated timing-based variety filtering functionality,
including season length compatibility, planting window flexibility,
harvest timing optimization, and succession planting coordination.
"""

import pytest
import asyncio
from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from typing import List, Dict, Any

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from services.timing_based_variety_filter import (
    TimingBasedVarietyFilter,
    TimingFilterCriteria,
    TimingCompatibilityScore,
    SeasonLengthCompatibility,
    PlantingWindowFlexibility,
    TimingFilterType
)
from models.crop_variety_models import EnhancedCropVariety, PlantingPopulationRecommendation
from models.service_models import LocationData


class TestTimingBasedVarietyFilter:
    """Test suite for timing-based variety filtering service."""
    
    @pytest.fixture
    def timing_filter(self):
        """Create timing filter service instance."""
        return TimingBasedVarietyFilter()
    
    @pytest.fixture
    def sample_varieties(self):
        """Create sample crop varieties for testing."""
        return [
            EnhancedCropVariety(
                id="variety-1",
                variety_name="Early Corn Hybrid",
                crop_id="corn",
                days_to_physiological_maturity=90,
                relative_maturity=90,
                recommended_planting_populations=[
                    PlantingPopulationRecommendation(
                        practice_type="conventional",
                        recommended_population=30000,
                        population_range_min=28000,
                        population_range_max=32000
                    )
                ]
            ),
            EnhancedCropVariety(
                id="variety-2",
                variety_name="Late Corn Hybrid",
                crop_id="corn",
                days_to_physiological_maturity=120,
                relative_maturity=120,
                recommended_planting_populations=[
                    PlantingPopulationRecommendation(
                        practice_type="conventional",
                        recommended_population=28000,
                        population_range_min=26000,
                        population_range_max=30000
                    )
                ]
            ),
            EnhancedCropVariety(
                id="variety-3",
                variety_name="Medium Corn Hybrid",
                crop_id="corn",
                days_to_physiological_maturity=105,
                relative_maturity=105,
                recommended_planting_populations=[
                    PlantingPopulationRecommendation(
                        practice_type="conventional",
                        recommended_population=29000,
                        population_range_min=27000,
                        population_range_max=31000
                    )
                ]
            )
        ]
    
    @pytest.fixture
    def sample_location(self):
        """Create sample location data for testing."""
        return LocationData(
            latitude=40.7128,
            longitude=-74.0060,
            climate_zone="6a",
            elevation_meters=10
        )
    
    @pytest.fixture
    def sample_timing_criteria(self):
        """Create sample timing criteria for testing."""
        return TimingFilterCriteria(
            available_growing_days=120,
            min_growing_days_required=100,
            preferred_planting_start=date(2024, 4, 15),
            preferred_planting_end=date(2024, 5, 15),
            planting_window_flexibility=PlantingWindowFlexibility.MODERATE,
            preferred_harvest_start=date(2024, 9, 1),
            preferred_harvest_end=date(2024, 10, 15),
            harvest_timing_constraints=["before_frost"],
            succession_planting_needed=False,
            target_growing_degree_days=2000,
            gdd_tolerance_percent=10.0,
            photoperiod_sensitive=False
        )
    
    @pytest.mark.asyncio
    async def test_filter_varieties_by_timing_success(self, timing_filter, sample_varieties, sample_location, sample_timing_criteria):
        """Test successful variety filtering by timing criteria."""
        
        # Mock the supporting services
        with patch.object(timing_filter.growing_season_service, 'analyze_growing_season') as mock_growing_season:
            mock_growing_season.return_value = {"season_length": 120, "gdd": 2000}
            
            # Test the filtering
            results = await timing_filter.filter_varieties_by_timing(
                sample_varieties, sample_timing_criteria, sample_location, "corn"
            )
            
            # Verify results
            assert len(results) == 3
            assert all(isinstance(result, TimingCompatibilityScore) for result in results)
            
            # Results should be sorted by overall score (descending)
            scores = [result.overall_score for result in results]
            assert scores == sorted(scores, reverse=True)
    
    @pytest.mark.asyncio
    async def test_season_length_compatibility_evaluation(self, timing_filter, sample_varieties, sample_location, sample_timing_criteria):
        """Test season length compatibility evaluation."""
        
        variety = sample_varieties[0]  # Early Corn Hybrid (90 days)
        
        # Test with sufficient season length
        score, analysis = await timing_filter._evaluate_season_length_compatibility(
            variety, sample_timing_criteria, sample_location
        )
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert "variety_maturity_days" in analysis
        assert "available_growing_days" in analysis
        assert "compatibility" in analysis
        assert analysis["variety_maturity_days"] == 90
        assert analysis["available_growing_days"] == 120
    
    @pytest.mark.asyncio
    async def test_season_length_insufficient_season(self, timing_filter, sample_location):
        """Test season length evaluation with insufficient season."""
        
        # Create variety with longer maturity than available season
        long_variety = EnhancedCropVariety(
            id="long-variety",
            variety_name="Long Season Variety",
            crop_id="corn",
            days_to_physiological_maturity=150
        )
        
        timing_criteria = TimingFilterCriteria(
            available_growing_days=120,
            min_growing_days_required=100
        )
        
        score, analysis = await timing_filter._evaluate_season_length_compatibility(
            long_variety, timing_criteria, sample_location
        )
        
        assert score == 0.0
        assert analysis["compatibility"] == "insufficient_season"
    
    @pytest.mark.asyncio
    async def test_planting_window_compatibility_evaluation(self, timing_filter, sample_varieties, sample_location, sample_timing_criteria):
        """Test planting window compatibility evaluation."""
        
        variety = sample_varieties[0]  # Early Corn Hybrid
        
        score, analysis = await timing_filter._evaluate_planting_window_compatibility(
            variety, sample_timing_criteria, sample_location
        )
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert "variety_flexibility" in analysis
        assert "farmer_requirements" in analysis
        assert "score" in analysis
    
    @pytest.mark.asyncio
    async def test_harvest_timing_compatibility_evaluation(self, timing_filter, sample_varieties, sample_location, sample_timing_criteria):
        """Test harvest timing compatibility evaluation."""
        
        variety = sample_varieties[0]  # Early Corn Hybrid
        
        # Mock harvest date calculation
        with patch.object(timing_filter, '_calculate_harvest_dates') as mock_harvest_dates:
            mock_harvest_dates.return_value = {
                "earliest": date(2024, 8, 15),
                "typical": date(2024, 8, 30),
                "latest": date(2024, 9, 15)
            }
            
            score, analysis = await timing_filter._evaluate_harvest_timing_compatibility(
                variety, sample_timing_criteria, sample_location
            )
            
            assert isinstance(score, float)
            assert 0.0 <= score <= 1.0
            assert "harvest_dates" in analysis
            assert "constraints_met" in analysis
            assert "constraints_failed" in analysis
    
    @pytest.mark.asyncio
    async def test_succession_planting_compatibility_evaluation(self, timing_filter, sample_varieties, sample_location):
        """Test succession planting compatibility evaluation."""
        
        variety = sample_varieties[0]  # Early Corn Hybrid (90 days)
        
        timing_criteria = TimingFilterCriteria(
            available_growing_days=120,
            succession_planting_needed=True,
            succession_interval_days=100
        )
        
        score, analysis = await timing_filter._evaluate_succession_compatibility(
            variety, timing_criteria, sample_location
        )
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert "variety_maturity_days" in analysis
        assert "succession_interval" in analysis
        assert "compatibility" in analysis
        assert analysis["variety_maturity_days"] == 90
        assert analysis["succession_interval"] == 100
    
    @pytest.mark.asyncio
    async def test_gdd_compatibility_evaluation(self, timing_filter, sample_varieties, sample_location):
        """Test growing degree day compatibility evaluation."""
        
        variety = sample_varieties[0]  # Early Corn Hybrid
        
        timing_criteria = TimingFilterCriteria(
            available_growing_days=120,
            target_growing_degree_days=2000,
            gdd_tolerance_percent=10.0
        )
        
        # Mock GDD calculation
        with patch.object(timing_filter, '_calculate_variety_gdd_requirements') as mock_gdd:
            mock_gdd.return_value = 1950  # Close to target
            
            score, analysis = await timing_filter._evaluate_gdd_compatibility(
                variety, timing_criteria, sample_location
            )
            
            assert isinstance(score, float)
            assert 0.0 <= score <= 1.0
            assert "variety_gdd_requirements" in analysis
            assert "target_gdd" in analysis
            assert "gdd_difference" in analysis
            assert analysis["variety_gdd_requirements"] == 1950
            assert analysis["target_gdd"] == 2000
    
    @pytest.mark.asyncio
    async def test_photoperiod_compatibility_evaluation(self, timing_filter, sample_varieties, sample_location):
        """Test photoperiod compatibility evaluation."""
        
        variety = sample_varieties[0]  # Early Corn Hybrid
        
        timing_criteria = TimingFilterCriteria(
            available_growing_days=120,
            photoperiod_sensitive=False,
            day_length_requirements=(12, 16)
        )
        
        # Mock photoperiod and day length calculations
        with patch.object(timing_filter, '_get_variety_photoperiod_response') as mock_photoperiod:
            mock_photoperiod.return_value = {
                "sensitive": False,
                "critical_day_length": None,
                "response_type": "day_neutral"
            }
            
            with patch.object(timing_filter, '_calculate_location_day_lengths') as mock_day_lengths:
                mock_day_lengths.return_value = {
                    "average": 14.5,
                    "summer_max": 16.0,
                    "winter_min": 9.0
                }
                
                score, analysis = await timing_filter._evaluate_photoperiod_compatibility(
                    variety, timing_criteria, sample_location
                )
                
                assert isinstance(score, float)
                assert 0.0 <= score <= 1.0
                assert "variety_photoperiod" in analysis
                assert "location_day_lengths" in analysis
                assert "farmer_requirements" in analysis
    
    def test_calculate_overall_timing_score(self, timing_filter):
        """Test overall timing score calculation."""
        
        # Test with all components
        score = timing_filter._calculate_overall_timing_score(
            season_length_score=0.8,
            planting_window_score=0.7,
            harvest_timing_score=0.9,
            succession_score=0.6,
            gdd_score=0.8,
            photoperiod_score=0.7
        )
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        
        # Test with only required components
        score_minimal = timing_filter._calculate_overall_timing_score(
            season_length_score=0.8,
            planting_window_score=0.7,
            harvest_timing_score=0.9
        )
        
        assert isinstance(score_minimal, float)
        assert 0.0 <= score_minimal <= 1.0
        assert score_minimal < score  # Should be lower without optional components
    
    def test_determine_compatibility_level(self, timing_filter):
        """Test compatibility level determination."""
        
        # Test different score ranges
        assert timing_filter._determine_compatibility_level(0.95) == SeasonLengthCompatibility.EXCELLENT
        assert timing_filter._determine_compatibility_level(0.8) == SeasonLengthCompatibility.GOOD
        assert timing_filter._determine_compatibility_level(0.6) == SeasonLengthCompatibility.MARGINAL
        assert timing_filter._determine_compatibility_level(0.4) == SeasonLengthCompatibility.POOR
        assert timing_filter._determine_compatibility_level(0.2) == SeasonLengthCompatibility.INCOMPATIBLE
    
    def test_calculate_planting_window_flexibility(self, timing_filter, sample_varieties, sample_location):
        """Test planting window flexibility calculation."""
        
        # Test early maturity variety
        early_variety = sample_varieties[0]  # 90 days
        flexibility = timing_filter._calculate_planting_window_flexibility(early_variety, sample_location)
        assert flexibility == PlantingWindowFlexibility.VERY_FLEXIBLE
        
        # Test late maturity variety
        late_variety = sample_varieties[1]  # 120 days
        flexibility = timing_filter._calculate_planting_window_flexibility(late_variety, sample_location)
        assert flexibility == PlantingWindowFlexibility.FLEXIBLE
    
    def test_flexibility_compatible(self, timing_filter):
        """Test flexibility compatibility checking."""
        
        # Test compatible scenarios
        assert timing_filter._flexibility_compatible(
            PlantingWindowFlexibility.VERY_FLEXIBLE,
            PlantingWindowFlexibility.FLEXIBLE
        ) == True
        
        assert timing_filter._flexibility_compatible(
            PlantingWindowFlexibility.FLEXIBLE,
            PlantingWindowFlexibility.FLEXIBLE
        ) == True
        
        # Test incompatible scenarios
        assert timing_filter._flexibility_compatible(
            PlantingWindowFlexibility.NARROW,
            PlantingWindowFlexibility.VERY_FLEXIBLE
        ) == False
        
        assert timing_filter._flexibility_compatible(
            PlantingWindowFlexibility.CRITICAL,
            PlantingWindowFlexibility.FLEXIBLE
        ) == False
    
    def test_generate_timing_recommendations(self, timing_filter, sample_varieties, sample_timing_criteria):
        """Test timing recommendations generation."""
        
        variety = sample_varieties[0]
        
        # Mock analysis data
        season_analysis = {"score": 0.6, "compatibility": "tight_fit"}
        planting_analysis = {"score": 0.8, "variety_flexibility": PlantingWindowFlexibility.MODERATE}
        harvest_analysis = {"score": 0.7, "constraints_failed": []}
        
        recommendations, risk_factors, optimizations = timing_filter._generate_timing_recommendations(
            variety, sample_timing_criteria, season_analysis, planting_analysis, harvest_analysis,
            None, None, None
        )
        
        assert isinstance(recommendations, list)
        assert isinstance(risk_factors, list)
        assert isinstance(optimizations, list)
        
        # Should have recommendations for tight fit
        assert len(recommendations) > 0
        assert any("weather" in rec.lower() for rec in recommendations)
    
    @pytest.mark.asyncio
    async def test_filter_varieties_empty_input(self, timing_filter, sample_location, sample_timing_criteria):
        """Test filtering with empty variety list."""
        
        results = await timing_filter.filter_varieties_by_timing(
            [], sample_timing_criteria, sample_location, "corn"
        )
        
        assert results == []
    
    @pytest.mark.asyncio
    async def test_filter_varieties_missing_maturity_data(self, timing_filter, sample_location, sample_timing_criteria):
        """Test filtering with varieties missing maturity data."""
        
        # Create variety without maturity data
        variety_no_maturity = EnhancedCropVariety(
            id="no-maturity",
            variety_name="No Maturity Data",
            crop_id="corn"
        )
        
        results = await timing_filter.filter_varieties_by_timing(
            [variety_no_maturity], sample_timing_criteria, sample_location, "corn"
        )
        
        # Should handle gracefully
        assert len(results) == 1
        assert results[0].overall_score < 1.0  # Should have lower score due to missing data
    
    @pytest.mark.asyncio
    async def test_filter_varieties_exception_handling(self, timing_filter, sample_varieties, sample_location, sample_timing_criteria):
        """Test exception handling during filtering."""
        
        # Mock an exception in one of the evaluation methods
        with patch.object(timing_filter, '_evaluate_season_length_compatibility') as mock_eval:
            mock_eval.side_effect = Exception("Test exception")
            
            results = await timing_filter.filter_varieties_by_timing(
                sample_varieties, sample_timing_criteria, sample_location, "corn"
            )
            
            # Should continue processing other varieties
            assert len(results) == 2  # One variety should be skipped due to exception


class TestTimingFilterCriteria:
    """Test suite for timing filter criteria model."""
    
    def test_timing_filter_criteria_creation(self):
        """Test creation of timing filter criteria."""
        
        criteria = TimingFilterCriteria(
            available_growing_days=120,
            min_growing_days_required=100,
            preferred_planting_start=date(2024, 4, 15),
            planting_window_flexibility=PlantingWindowFlexibility.MODERATE
        )
        
        assert criteria.available_growing_days == 120
        assert criteria.min_growing_days_required == 100
        assert criteria.preferred_planting_start == date(2024, 4, 15)
        assert criteria.planting_window_flexibility == PlantingWindowFlexibility.MODERATE
        assert criteria.succession_planting_needed == False  # Default value
        assert criteria.gdd_tolerance_percent == 10.0  # Default value
    
    def test_timing_filter_criteria_defaults(self):
        """Test default values for timing filter criteria."""
        
        criteria = TimingFilterCriteria(available_growing_days=120)
        
        assert criteria.available_growing_days == 120
        assert criteria.min_growing_days_required is None
        assert criteria.max_growing_days_tolerated is None
        assert criteria.preferred_planting_start is None
        assert criteria.preferred_planting_end is None
        assert criteria.planting_window_flexibility is None
        assert criteria.preferred_harvest_start is None
        assert criteria.preferred_harvest_end is None
        assert criteria.harvest_timing_constraints is None
        assert criteria.succession_planting_needed == False
        assert criteria.succession_interval_days is None
        assert criteria.multiple_plantings_per_season == False
        assert criteria.target_growing_degree_days is None
        assert criteria.gdd_tolerance_percent == 10.0
        assert criteria.photoperiod_sensitive is None
        assert criteria.day_length_requirements is None


class TestTimingCompatibilityScore:
    """Test suite for timing compatibility score model."""
    
    def test_timing_compatibility_score_creation(self):
        """Test creation of timing compatibility score."""
        
        score = TimingCompatibilityScore(
            variety_id="test-variety",
            variety_name="Test Variety",
            overall_score=0.8,
            compatibility_level=SeasonLengthCompatibility.GOOD,
            season_length_score=0.9,
            planting_window_score=0.7,
            harvest_timing_score=0.8,
            season_length_analysis={"test": "data"},
            planting_window_analysis={"test": "data"},
            harvest_timing_analysis={"test": "data"},
            timing_recommendations=["Test recommendation"],
            risk_factors=["Test risk"],
            optimization_suggestions=["Test optimization"]
        )
        
        assert score.variety_id == "test-variety"
        assert score.variety_name == "Test Variety"
        assert score.overall_score == 0.8
        assert score.compatibility_level == SeasonLengthCompatibility.GOOD
        assert score.season_length_score == 0.9
        assert score.planting_window_score == 0.7
        assert score.harvest_timing_score == 0.8
        assert score.succession_score is None
        assert score.gdd_compatibility_score is None
        assert score.photoperiod_score is None
        assert len(score.timing_recommendations) == 1
        assert len(score.risk_factors) == 1
        assert len(score.optimization_suggestions) == 1


class TestTimingFilterEnums:
    """Test suite for timing filter enumerations."""
    
    def test_timing_filter_type_enum(self):
        """Test timing filter type enumeration."""
        
        assert TimingFilterType.SEASON_LENGTH == "season_length"
        assert TimingFilterType.PLANTING_WINDOW == "planting_window"
        assert TimingFilterType.HARVEST_TIMING == "harvest_timing"
        assert TimingFilterType.SUCCESSION_PLANTING == "succession_planting"
        assert TimingFilterType.GROWING_DEGREE_DAYS == "growing_degree_days"
        assert TimingFilterType.PHOTOPERIOD_RESPONSE == "photoperiod_response"
    
    def test_season_length_compatibility_enum(self):
        """Test season length compatibility enumeration."""
        
        assert SeasonLengthCompatibility.EXCELLENT == "excellent"
        assert SeasonLengthCompatibility.GOOD == "good"
        assert SeasonLengthCompatibility.MARGINAL == "marginal"
        assert SeasonLengthCompatibility.POOR == "poor"
        assert SeasonLengthCompatibility.INCOMPATIBLE == "incompatible"
    
    def test_planting_window_flexibility_enum(self):
        """Test planting window flexibility enumeration."""
        
        assert PlantingWindowFlexibility.VERY_FLEXIBLE == "very_flexible"
        assert PlantingWindowFlexibility.FLEXIBLE == "flexible"
        assert PlantingWindowFlexibility.MODERATE == "moderate"
        assert PlantingWindowFlexibility.NARROW == "narrow"
        assert PlantingWindowFlexibility.CRITICAL == "critical"


# Integration tests
class TestTimingFilterIntegration:
    """Integration tests for timing-based variety filtering."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_timing_filtering(self):
        """Test end-to-end timing-based variety filtering."""
        
        # Create comprehensive test data
        varieties = [
            EnhancedCropVariety(
                id="early-corn",
                variety_name="Early Season Corn",
                crop_id="corn",
                days_to_physiological_maturity=85,
                relative_maturity=85,
                recommended_planting_populations=[
                    PlantingPopulationRecommendation(
                        practice_type="conventional",
                        recommended_population=30000
                    )
                ]
            ),
            EnhancedCropVariety(
                id="late-corn",
                variety_name="Late Season Corn",
                crop_id="corn",
                days_to_physiological_maturity=130,
                relative_maturity=130,
                recommended_planting_populations=[
                    PlantingPopulationRecommendation(
                        practice_type="conventional",
                        recommended_population=28000
                    )
                ]
            )
        ]
        
        location = LocationData(
            latitude=40.7128,
            longitude=-74.0060,
            climate_zone="6a"
        )
        
        timing_criteria = TimingFilterCriteria(
            available_growing_days=110,
            min_growing_days_required=100,
            planting_window_flexibility=PlantingWindowFlexibility.MODERATE,
            harvest_timing_constraints=["before_frost"],
            succession_planting_needed=False
        )
        
        # Create timing filter service
        timing_filter = TimingBasedVarietyFilter()
        
        # Run the filtering
        results = await timing_filter.filter_varieties_by_timing(
            varieties, timing_criteria, location, "corn"
        )
        
        # Verify results
        assert len(results) == 2
        
        # Early variety should score higher (fits better in short season)
        early_result = next(r for r in results if r.variety_id == "early-corn")
        late_result = next(r for r in results if r.variety_id == "late-corn")
        
        assert early_result.overall_score > late_result.overall_score
        assert early_result.compatibility_level in [SeasonLengthCompatibility.EXCELLENT, SeasonLengthCompatibility.GOOD]
        assert late_result.compatibility_level in [SeasonLengthCompatibility.MARGINAL, SeasonLengthCompatibility.POOR]


# Performance tests
class TestTimingFilterPerformance:
    """Performance tests for timing-based variety filtering."""
    
    @pytest.mark.asyncio
    async def test_large_variety_list_performance(self):
        """Test performance with large variety list."""
        
        # Create large list of varieties
        varieties = []
        for i in range(100):
            variety = EnhancedCropVariety(
                id=f"variety-{i}",
                variety_name=f"Test Variety {i}",
                crop_id="corn",
                days_to_physiological_maturity=90 + (i % 40),  # 90-130 days
                relative_maturity=90 + (i % 40),
                recommended_planting_populations=[
                    PlantingPopulationRecommendation(
                        practice_type="conventional",
                        recommended_population=30000
                    )
                ]
            )
            varieties.append(variety)
        
        location = LocationData(latitude=40.7128, longitude=-74.0060)
        timing_criteria = TimingFilterCriteria(available_growing_days=120)
        
        timing_filter = TimingBasedVarietyFilter()
        
        # Time the filtering operation
        import time
        start_time = time.time()
        
        results = await timing_filter.filter_varieties_by_timing(
            varieties, timing_criteria, location, "corn"
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert execution_time < 5.0  # 5 seconds for 100 varieties
        assert len(results) == 100
        
        # Results should be sorted by score
        scores = [r.overall_score for r in results]
        assert scores == sorted(scores, reverse=True)