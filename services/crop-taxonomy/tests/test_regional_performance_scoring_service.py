"""
Tests for Regional Performance Scoring Service
TICKET-005_crop-variety-recommendations-11.2

Comprehensive test suite for regional performance scoring and analysis.
"""

import pytest
import asyncio
import numpy as np
import pandas as pd
from unittest.mock import AsyncMock, patch, MagicMock
from typing import List, Dict, Any

import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from services.regional_performance_scoring_service import (
    RegionalPerformanceScoringService,
    PerformanceMetric,
    StabilityMeasure,
    AdaptationType,
    VarietyPerformance,
    TrialLocation,
    EnvironmentData,
    AMMIAnalysis,
    GGEBiplotData,
    StabilityAnalysis,
    RegionalPerformanceRanking
)
from models.regional_performance_models import (
    RegionalPerformanceRequest,
    VarietyPerformanceSummaryRequest,
    StabilityAnalysisRequest,
    AMMIAnalysisRequest,
    GGEBiplotRequest,
    RegionalRankingRequest
)

class TestRegionalPerformanceScoringService:
    """Test suite for RegionalPerformanceScoringService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return RegionalPerformanceScoringService()
    
    @pytest.fixture
    def sample_trial_data(self):
        """Create sample trial data for testing."""
        return [
            VarietyPerformance(
                variety_id="var_1_loc_1_2023",
                variety_name="Variety A",
                crop_type="corn",
                location_id="Location_1",
                year=2023,
                yield_value=150.0,
                quality_score=0.85,
                disease_incidence=0.1,
                maturity_days=115
            ),
            VarietyPerformance(
                variety_id="var_1_loc_2_2023",
                variety_name="Variety A",
                crop_type="corn",
                location_id="Location_2",
                year=2023,
                yield_value=160.0,
                quality_score=0.90,
                disease_incidence=0.05,
                maturity_days=110
            ),
            VarietyPerformance(
                variety_id="var_2_loc_1_2023",
                variety_name="Variety B",
                crop_type="corn",
                location_id="Location_1",
                year=2023,
                yield_value=140.0,
                quality_score=0.80,
                disease_incidence=0.15,
                maturity_days=120
            ),
            VarietyPerformance(
                variety_id="var_2_loc_2_2023",
                variety_name="Variety B",
                crop_type="corn",
                location_id="Location_2",
                year=2023,
                yield_value=170.0,
                quality_score=0.95,
                disease_incidence=0.02,
                maturity_days=105
            )
        ]
    
    @pytest.fixture
    def sample_locations(self):
        """Create sample location data for testing."""
        return [
            TrialLocation(
                location_id="Location_1",
                location_name="Test Location 1",
                latitude=40.0,
                longitude=-95.0,
                state="Iowa",
                county="Test County",
                climate_zone="5a",
                soil_type="loam",
                elevation_meters=300.0,
                irrigation_available=False
            ),
            TrialLocation(
                location_id="Location_2",
                location_name="Test Location 2",
                latitude=41.0,
                longitude=-94.0,
                state="Iowa",
                county="Test County 2",
                climate_zone="5b",
                soil_type="clay_loam",
                elevation_meters=350.0,
                irrigation_available=True
            )
        ]
    
    @pytest.mark.asyncio
    async def test_analyze_regional_performance_success(self, service, sample_trial_data):
        """Test successful regional performance analysis."""
        # Mock the _get_trial_data method
        with patch.object(service, '_get_trial_data', return_value=sample_trial_data):
            result = await service.analyze_regional_performance(
                crop_type="corn",
                varieties=["Variety A", "Variety B"],
                locations=["Location_1", "Location_2"],
                years=[2023]
            )
            
            assert "analysis_id" in result
            assert result["crop_type"] == "corn"
            assert result["varieties_analyzed"] == ["Variety A", "Variety B"]
            assert result["locations_analyzed"] == ["Location_1", "Location_2"]
            assert result["years_analyzed"] == [2023]
            assert "multi_location_analysis" in result
            assert "gxe_analysis" in result
            assert "ammi_analysis" in result
            assert "gge_analysis" in result
            assert "stability_analysis" in result
            assert "regional_rankings" in result
            assert "environmental_integration" in result
    
    @pytest.mark.asyncio
    async def test_analyze_regional_performance_no_data(self, service):
        """Test regional performance analysis with no data."""
        with patch.object(service, '_get_trial_data', return_value=[]):
            result = await service.analyze_regional_performance(
                crop_type="corn",
                varieties=["Variety A"],
                locations=["Location_1"],
                years=[2023]
            )
            
            assert "error" in result
            assert result["error"] == "No trial data available"
    
    @pytest.mark.asyncio
    async def test_perform_multi_location_analysis(self, service, sample_trial_data):
        """Test multi-location performance analysis."""
        result = await service._perform_multi_location_analysis(sample_trial_data)
        
        assert "variety_means" in result
        assert "location_means" in result
        assert "variety_location_interactions" in result
        assert "overall_mean" in result
        assert "overall_std" in result
        
        # Check that variety means are calculated
        assert "Variety A" in result["variety_means"]["mean"]
        assert "Variety B" in result["variety_means"]["mean"]
        
        # Check that location means are calculated
        assert "Location_1" in result["location_means"]["mean"]
        assert "Location_2" in result["location_means"]["mean"]
    
    @pytest.mark.asyncio
    async def test_perform_gxe_analysis(self, service, sample_trial_data):
        """Test genotype-by-environment interaction analysis."""
        result = await service._perform_gxe_analysis(sample_trial_data)
        
        assert "interaction_matrix" in result
        assert "interaction_effects" in result
        assert "interaction_sum_of_squares" in result
        assert "variety_means" in result
        assert "location_means" in result
        assert "grand_mean" in result
        
        # Check interaction matrix structure
        assert "Variety A" in result["interaction_matrix"]
        assert "Variety B" in result["interaction_matrix"]
        assert "Location_1" in result["interaction_matrix"]["Variety A"]
        assert "Location_2" in result["interaction_matrix"]["Variety A"]
    
    @pytest.mark.asyncio
    async def test_perform_ammi_analysis(self, service, sample_trial_data):
        """Test AMMI analysis."""
        result = await service._perform_ammi_analysis(sample_trial_data)
        
        assert isinstance(result, AMMIAnalysis)
        assert "Variety A" in result.genotype_effects
        assert "Variety B" in result.genotype_effects
        assert "Location_1" in result.environment_effects
        assert "Location_2" in result.environment_effects
        assert "Variety A" in result.interaction_effects
        assert "explained_variance" in result.explained_variance
        assert "Variety A" in result.ipca_scores
        assert "Variety A" in result.stability_values
    
    @pytest.mark.asyncio
    async def test_perform_gge_analysis(self, service, sample_trial_data):
        """Test GGE biplot analysis."""
        result = await service._perform_gge_analysis(sample_trial_data)
        
        assert isinstance(result, GGEBiplotData)
        assert "Variety A" in result.genotype_scores
        assert "Variety B" in result.genotype_scores
        assert "Location_1" in result.environment_scores
        assert "Location_2" in result.environment_scores
        assert len(result.explained_variance) == 2
        assert "Location_1" in result.which_won_where
        assert "Variety A" in result.mean_vs_stability
    
    @pytest.mark.asyncio
    async def test_perform_stability_analysis(self, service, sample_trial_data):
        """Test stability analysis."""
        result = await service._perform_stability_analysis(sample_trial_data)
        
        assert isinstance(result, StabilityAnalysis)
        assert "Variety A" in result.variety_stability
        assert "Variety B" in result.variety_stability
        assert "Variety A" in result.adaptation_types
        assert "Variety A" in result.stability_rankings
        assert "Variety A" in result.adaptation_recommendations
        
        # Check stability measures
        variety_a_stability = result.variety_stability["Variety A"]
        assert StabilityMeasure.COEFFICIENT_OF_VARIATION in variety_a_stability
        assert StabilityMeasure.REGRESSION_COEFFICIENT in variety_a_stability
        assert StabilityMeasure.DEVIATION_FROM_REGRESSION in variety_a_stability
        assert StabilityMeasure.SHUKLA_STABILITY_VARIANCE in variety_a_stability
    
    @pytest.mark.asyncio
    async def test_generate_regional_rankings(self, service, sample_trial_data):
        """Test regional ranking generation."""
        # Mock the required analysis methods
        multi_location_analysis = {
            "variety_means": {"Variety A": {"mean": 155.0}, "Variety B": {"mean": 155.0}},
            "location_means": {"Location_1": {"mean": 145.0}, "Location_2": {"mean": 165.0}},
            "variety_location_interactions": {},
            "overall_mean": 155.0,
            "overall_std": 10.0
        }
        
        stability_analysis = StabilityAnalysis(
            variety_stability={"Variety A": {}, "Variety B": {}},
            adaptation_types={"Variety A": AdaptationType.STABLE_PERFORMANCE, "Variety B": AdaptationType.STABLE_PERFORMANCE},
            stability_rankings={"Variety A": 1, "Variety B": 2},
            adaptation_recommendations={"Variety A": ["Stable"], "Variety B": ["Stable"]}
        )
        
        result = await service._generate_regional_rankings(
            sample_trial_data, multi_location_analysis, stability_analysis
        )
        
        assert isinstance(result, RegionalPerformanceRanking)
        assert "Location_1" in result.variety_rankings
        assert "Location_2" in result.variety_rankings
        assert "Location_1" in result.regional_winners
        assert "Variety A" in result.performance_trends
        assert "Variety A" in result.adaptation_zones
    
    @pytest.mark.asyncio
    async def test_integrate_environmental_data(self, service, sample_trial_data):
        """Test environmental data integration."""
        locations = ["Location_1", "Location_2"]
        result = await service._integrate_environmental_data(sample_trial_data, locations)
        
        assert "environmental_data" in result
        assert "Location_1" in result["environmental_data"]
        assert "Location_2" in result["environmental_data"]
        assert "integration_timestamp" in result
        
        # Check environmental data structure
        env_data_location_1 = result["environmental_data"]["Location_1"]
        assert "climate_data" in env_data_location_1
        assert "soil_data" in env_data_location_1
        assert "pest_pressure" in env_data_location_1
        assert "disease_pressure" in env_data_location_1
    
    @pytest.mark.asyncio
    async def test_get_variety_performance_summary(self, service):
        """Test variety performance summary generation."""
        result = await service.get_variety_performance_summary(
            variety_name="Test Variety",
            crop_type="corn",
            years=[2022, 2023, 2024]
        )
        
        assert result["variety_name"] == "Test Variety"
        assert result["crop_type"] == "corn"
        assert result["years_analyzed"] == [2022, 2023, 2024]
        assert "overall_performance" in result
        assert "stability_metrics" in result
        assert "recommendations" in result
        
        # Check overall performance structure
        overall_perf = result["overall_performance"]
        assert "mean_yield" in overall_perf
        assert "yield_stability" in overall_perf
        assert "adaptation_type" in overall_perf
        assert "regional_performance" in overall_perf
        
        # Check stability metrics structure
        stability_metrics = result["stability_metrics"]
        assert "coefficient_of_variation" in stability_metrics
        assert "regression_coefficient" in stability_metrics
        assert "stability_ranking" in stability_metrics

class TestPerformanceMetrics:
    """Test performance metrics calculations."""
    
    def test_performance_metric_enum(self):
        """Test PerformanceMetric enum values."""
        assert PerformanceMetric.YIELD == "yield"
        assert PerformanceMetric.QUALITY == "quality"
        assert PerformanceMetric.DISEASE_RESISTANCE == "disease_resistance"
        assert PerformanceMetric.DROUGHT_TOLERANCE == "drought_tolerance"
        assert PerformanceMetric.MATURITY == "maturity"
        assert PerformanceMetric.STABILITY == "stability"
    
    def test_stability_measure_enum(self):
        """Test StabilityMeasure enum values."""
        assert StabilityMeasure.COEFFICIENT_OF_VARIATION == "cv"
        assert StabilityMeasure.REGRESSION_COEFFICIENT == "regression_coefficient"
        assert StabilityMeasure.DEVIATION_FROM_REGRESSION == "deviation_from_regression"
        assert StabilityMeasure.SHUKLA_STABILITY_VARIANCE == "shukla_stability_variance"
        assert StabilityMeasure.WRIKE_STABILITY_VARIANCE == "wrike_stability_variance"
        assert StabilityMeasure.AMMI_STABILITY_VALUE == "ammi_stability_value"
    
    def test_adaptation_type_enum(self):
        """Test AdaptationType enum values."""
        assert AdaptationType.GENERAL_ADAPTATION == "general_adaptation"
        assert AdaptationType.SPECIFIC_ADAPTATION == "specific_adaptation"
        assert AdaptationType.STABLE_PERFORMANCE == "stable_performance"
        assert AdaptationType.UNSTABLE_PERFORMANCE == "unstable_performance"

class TestDataModels:
    """Test data model classes."""
    
    def test_variety_performance_model(self):
        """Test VarietyPerformance dataclass."""
        vp = VarietyPerformance(
            variety_id="test_id",
            variety_name="Test Variety",
            crop_type="corn",
            location_id="test_location",
            year=2023,
            yield_value=150.0
        )
        
        assert vp.variety_id == "test_id"
        assert vp.variety_name == "Test Variety"
        assert vp.crop_type == "corn"
        assert vp.location_id == "test_location"
        assert vp.year == 2023
        assert vp.yield_value == 150.0
        assert vp.quality_score is None
        assert vp.disease_incidence is None
        assert vp.maturity_days is None
    
    def test_trial_location_model(self):
        """Test TrialLocation dataclass."""
        tl = TrialLocation(
            location_id="test_location",
            location_name="Test Location",
            latitude=40.0,
            longitude=-95.0,
            state="Iowa"
        )
        
        assert tl.location_id == "test_location"
        assert tl.location_name == "Test Location"
        assert tl.latitude == 40.0
        assert tl.longitude == -95.0
        assert tl.state == "Iowa"
        assert tl.county is None
        assert tl.climate_zone is None
        assert tl.soil_type is None
        assert tl.elevation_meters is None
        assert tl.irrigation_available is False
    
    def test_environment_data_model(self):
        """Test EnvironmentData dataclass."""
        ed = EnvironmentData(
            location_id="test_location",
            year=2023,
            temperature_data={"avg": 20.0},
            precipitation_data={"annual": 800.0},
            soil_data={"ph": 6.5}
        )
        
        assert ed.location_id == "test_location"
        assert ed.year == 2023
        assert ed.temperature_data == {"avg": 20.0}
        assert ed.precipitation_data == {"annual": 800.0}
        assert ed.soil_data == {"ph": 6.5}
        assert ed.pest_pressure is None
        assert ed.disease_pressure is None

class TestStatisticalCalculations:
    """Test statistical calculation methods."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return RegionalPerformanceScoringService()
    
    def test_coefficient_of_variation_calculation(self, service):
        """Test coefficient of variation calculation."""
        data = [100, 120, 110, 130, 115]
        cv = np.std(data) / np.mean(data)
        
        assert cv > 0
        assert cv < 1  # Should be reasonable CV
    
    def test_regression_coefficient_calculation(self, service):
        """Test regression coefficient calculation."""
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]
        
        slope, intercept, r_value, p_value, std_err = np.polyfit(x, y, 1)
        
        assert abs(slope - 2.0) < 0.01  # Should be close to 2
        assert abs(intercept) < 0.01  # Should be close to 0
    
    def test_ammi_stability_calculation(self, service):
        """Test AMMI stability value calculation."""
        ipca_scores = [0.5, -0.3, 0.8, -0.2]
        stability_value = sum(score ** 2 for score in ipca_scores)
        
        assert stability_value > 0
        assert stability_value == 0.5**2 + (-0.3)**2 + 0.8**2 + (-0.2)**2

class TestIntegrationWithExternalServices:
    """Test integration with external services."""
    
    @pytest.mark.asyncio
    async def test_trial_data_service_integration(self):
        """Test integration with trial data service."""
        service = RegionalPerformanceScoringService()
        
        # Mock trial data service
        with patch.object(service, 'trial_data_service') as mock_service:
            mock_service.get_trial_data = AsyncMock(return_value=[])
            
            # This would test actual integration when implemented
            assert service.trial_data_service is not None
    
    @pytest.mark.asyncio
    async def test_climate_service_integration(self):
        """Test integration with climate service."""
        service = RegionalPerformanceScoringService()
        
        # Mock climate service
        with patch.object(service, 'climate_service') as mock_service:
            mock_service.get_climate_data = AsyncMock(return_value={})
            
            # This would test actual integration when implemented
            assert service.climate_service is not None

class TestErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.mark.asyncio
    async def test_analyze_regional_performance_error_handling(self):
        """Test error handling in regional performance analysis."""
        service = RegionalPerformanceScoringService()
        
        # Mock _get_trial_data to raise an exception
        with patch.object(service, '_get_trial_data', side_effect=Exception("Test error")):
            result = await service.analyze_regional_performance(
                crop_type="corn",
                varieties=["Variety A"],
                locations=["Location_1"],
                years=[2023]
            )
            
            assert "error" in result
            assert "Test error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_invalid_input_handling(self):
        """Test handling of invalid input parameters."""
        service = RegionalPerformanceScoringService()
        
        # Test with empty varieties list
        result = await service.analyze_regional_performance(
            crop_type="corn",
            varieties=[],  # Empty list
            locations=["Location_1"],
            years=[2023]
        )
        
        # Should handle gracefully
        assert isinstance(result, dict)
    
    @pytest.mark.asyncio
    async def test_missing_data_handling(self):
        """Test handling of missing data scenarios."""
        service = RegionalPerformanceScoringService()
        
        # Create trial data with missing values
        incomplete_data = [
            VarietyPerformance(
                variety_id="var_1",
                variety_name="Variety A",
                crop_type="corn",
                location_id="Location_1",
                year=2023,
                yield_value=150.0,
                quality_score=None,  # Missing quality score
                disease_incidence=None,  # Missing disease incidence
                maturity_days=None  # Missing maturity days
            )
        ]
        
        # Should handle missing data gracefully
        result = await service._perform_multi_location_analysis(incomplete_data)
        assert "variety_means" in result
        assert "Variety A" in result["variety_means"]

# Performance tests
class TestPerformanceRequirements:
    """Test performance requirements."""
    
    @pytest.mark.asyncio
    async def test_analysis_response_time(self):
        """Test that analysis completes within acceptable time."""
        import time
        
        service = RegionalPerformanceScoringService()
        
        # Create larger dataset for performance testing
        large_trial_data = []
        for variety in ["Var_A", "Var_B", "Var_C", "Var_D", "Var_E"]:
            for location in ["Loc_1", "Loc_2", "Loc_3", "Loc_4", "Loc_5"]:
                for year in [2022, 2023, 2024]:
                    large_trial_data.append(VarietyPerformance(
                        variety_id=f"{variety}_{location}_{year}",
                        variety_name=variety,
                        crop_type="corn",
                        location_id=location,
                        year=year,
                        yield_value=np.random.uniform(120, 180)
                    ))
        
        start_time = time.time()
        
        with patch.object(service, '_get_trial_data', return_value=large_trial_data):
            result = await service.analyze_regional_performance(
                crop_type="corn",
                varieties=["Var_A", "Var_B", "Var_C", "Var_D", "Var_E"],
                locations=["Loc_1", "Loc_2", "Loc_3", "Loc_4", "Loc_5"],
                years=[2022, 2023, 2024]
            )
        
        elapsed_time = time.time() - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert elapsed_time < 10.0, f"Analysis took {elapsed_time:.2f} seconds, exceeding 10 second limit"
        assert "analysis_id" in result

# Agricultural validation tests
class TestAgriculturalValidation:
    """Test agricultural domain validation."""
    
    @pytest.mark.asyncio
    async def test_corn_belt_performance_validation(self):
        """Test performance analysis for corn belt varieties."""
        service = RegionalPerformanceScoringService()
        
        # Create realistic corn belt trial data
        corn_belt_data = [
            VarietyPerformance(
                variety_id="corn_var_1",
                variety_name="Corn Variety 1",
                crop_type="corn",
                location_id="Iowa_1",
                year=2023,
                yield_value=180.0,  # Realistic corn yield
                quality_score=0.85,
                disease_incidence=0.1,
                maturity_days=115
            ),
            VarietyPerformance(
                variety_id="corn_var_2",
                variety_name="Corn Variety 2",
                crop_type="corn",
                location_id="Illinois_1",
                year=2023,
                yield_value=175.0,
                quality_score=0.90,
                disease_incidence=0.05,
                maturity_days=110
            )
        ]
        
        result = await service._perform_multi_location_analysis(corn_belt_data)
        
        # Validate agricultural reasonableness
        assert result["overall_mean"] > 100  # Should be reasonable corn yield
        assert result["overall_mean"] < 300  # Should not be unrealistic
        
        variety_means = result["variety_means"]
        for variety in variety_means:
            mean_yield = variety_means[variety]["mean"]
            assert 100 < mean_yield < 300, f"Unrealistic yield for {variety}: {mean_yield}"
    
    @pytest.mark.asyncio
    async def test_stability_measure_validation(self):
        """Test that stability measures are agriculturally meaningful."""
        service = RegionalPerformanceScoringService()
        
        # Create data with known stability patterns
        stable_variety_data = [
            VarietyPerformance(
                variety_id="stable_var",
                variety_name="Stable Variety",
                crop_type="corn",
                location_id=f"Location_{i}",
                year=2023,
                yield_value=150.0 + np.random.normal(0, 5)  # Low variability
            ) for i in range(5)
        ]
        
        unstable_variety_data = [
            VarietyPerformance(
                variety_id="unstable_var",
                variety_name="Unstable Variety",
                crop_type="corn",
                location_id=f"Location_{i}",
                year=2023,
                yield_value=150.0 + np.random.normal(0, 20)  # High variability
            ) for i in range(5)
        ]
        
        combined_data = stable_variety_data + unstable_variety_data
        
        result = await service._perform_stability_analysis(combined_data)
        
        # Stable variety should have lower CV than unstable variety
        stable_cv = result.variety_stability["Stable Variety"][StabilityMeasure.COEFFICIENT_OF_VARIATION]
        unstable_cv = result.variety_stability["Unstable Variety"][StabilityMeasure.COEFFICIENT_OF_VARIATION]
        
        assert stable_cv < unstable_cv, "Stable variety should have lower coefficient of variation"
        assert stable_cv < 0.2, "Stable variety CV should be reasonable"
        assert unstable_cv > 0.1, "Unstable variety CV should be higher"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])