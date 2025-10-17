"""
Comprehensive tests for yield goal management service.

This module provides comprehensive test coverage for:
- Yield goal analysis and recommendations
- Historical trend analysis
- Potential yield assessment
- Risk assessment and validation
- Service integration and error handling
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from uuid import uuid4
from datetime import date

from ..models.yield_goal_models import (
    YieldGoalRequest, YieldGoalAnalysis, YieldGoalRecommendation,
    YieldTrendAnalysis, PotentialYieldAssessment, YieldGoalValidationResult,
    YieldGoalComparison, YieldGoalType, YieldTrendDirection, YieldRiskLevel,
    HistoricalYieldData, SoilCharacteristic, WeatherPattern, ManagementPractice
)
from ..services.yield_goal_service import YieldGoalManagementService


class TestYieldGoalManagementService:
    """Comprehensive test suite for yield goal management service."""
    
    @pytest.fixture
    def service(self):
        """Create yield goal management service instance."""
        return YieldGoalManagementService()
    
    @pytest.fixture
    def sample_historical_yields(self):
        """Create sample historical yield data."""
        return [
            HistoricalYieldData(
                year=2020,
                yield_per_acre=165.0,
                crop_type="corn",
                variety="test_variety"
            ),
            HistoricalYieldData(
                year=2021,
                yield_per_acre=172.0,
                crop_type="corn",
                variety="test_variety"
            ),
            HistoricalYieldData(
                year=2022,
                yield_per_acre=178.0,
                crop_type="corn",
                variety="test_variety"
            ),
            HistoricalYieldData(
                year=2023,
                yield_per_acre=185.0,
                crop_type="corn",
                variety="test_variety"
            )
        ]
    
    @pytest.fixture
    def sample_soil_characteristics(self):
        """Create sample soil characteristics."""
        return SoilCharacteristic(
            soil_type="clay_loam",
            ph_level=6.5,
            organic_matter_percent=3.2,
            cation_exchange_capacity=18.5,
            drainage_class="well_drained",
            slope_percent=2.0,
            water_holding_capacity=1.8
        )
    
    @pytest.fixture
    def sample_weather_patterns(self):
        """Create sample weather patterns."""
        return WeatherPattern(
            growing_season_precipitation=22.5,
            growing_degree_days=2750,
            drought_stress_days=15,
            heat_stress_days=8,
            frost_risk_days=3,
            optimal_growing_days=125
        )
    
    @pytest.fixture
    def sample_management_practices(self):
        """Create sample management practices."""
        return ManagementPractice(
            tillage_system="reduced_till",
            irrigation_available=True,
            precision_agriculture=True,
            cover_crop_usage=True,
            crop_rotation="corn_soybean",
            planting_date=date(2024, 4, 15),
            harvest_date=date(2024, 10, 15)
        )
    
    @pytest.fixture
    def sample_yield_goal_request(
        self,
        sample_historical_yields,
        sample_soil_characteristics,
        sample_weather_patterns,
        sample_management_practices
    ):
        """Create sample yield goal request."""
        return YieldGoalRequest(
            field_id=uuid4(),
            crop_type="corn",
            variety="test_variety",
            target_year=2024,
            historical_yields=sample_historical_yields,
            soil_characteristics=sample_soil_characteristics,
            weather_patterns=sample_weather_patterns,
            management_practices=sample_management_practices,
            goal_preference=YieldGoalType.REALISTIC,
            risk_tolerance=YieldRiskLevel.MEDIUM
        )
    
    @pytest.mark.asyncio
    async def test_analyze_yield_goals_comprehensive(self, service, sample_yield_goal_request):
        """Test comprehensive yield goal analysis."""
        analysis = await service.analyze_yield_goals(sample_yield_goal_request)
        
        # Validate analysis structure
        assert analysis.analysis_id is not None
        assert analysis.field_id == sample_yield_goal_request.field_id
        assert analysis.crop_type == "corn"
        assert analysis.analysis_date is not None
        
        # Validate historical trend analysis
        assert analysis.historical_trend is not None
        assert analysis.historical_trend.trend_direction in YieldTrendDirection
        assert analysis.historical_trend.trend_slope is not None
        assert analysis.historical_trend.r_squared >= 0.0
        assert analysis.historical_trend.volatility >= 0.0
        assert analysis.historical_trend.average_yield > 0
        assert analysis.historical_trend.min_yield > 0
        assert analysis.historical_trend.max_yield > 0
        assert analysis.historical_trend.trend_confidence >= 0.0
        
        # Validate potential assessment
        assert analysis.potential_assessment is not None
        assert analysis.potential_assessment.soil_potential > 0
        assert analysis.potential_assessment.weather_potential > 0
        assert analysis.potential_assessment.management_potential > 0
        assert analysis.potential_assessment.variety_potential > 0
        assert analysis.potential_assessment.combined_potential > 0
        assert isinstance(analysis.potential_assessment.limiting_factors, list)
        assert isinstance(analysis.potential_assessment.improvement_opportunities, list)
        
        # Validate goal recommendations
        assert len(analysis.goal_recommendations) == 4  # All goal types
        for recommendation in analysis.goal_recommendations:
            assert recommendation.goal_type in YieldGoalType
            assert recommendation.recommended_yield > 0
            assert 0.0 <= recommendation.confidence_level <= 1.0
            assert 0.0 <= recommendation.achievement_probability <= 1.0
            assert recommendation.risk_level in YieldRiskLevel
            assert recommendation.rationale is not None
            assert isinstance(recommendation.supporting_factors, list)
            assert isinstance(recommendation.risk_factors, list)
        
        # Validate risk assessment
        assert analysis.overall_risk_level in YieldRiskLevel
        assert isinstance(analysis.risk_factors, list)
        assert isinstance(analysis.mitigation_strategies, list)
        
        # Validate metadata
        assert 0.0 <= analysis.analysis_confidence <= 1.0
        assert 0.0 <= analysis.data_quality_score <= 1.0
        assert isinstance(analysis.supporting_data, dict)
    
    @pytest.mark.asyncio
    async def test_historical_trend_analysis_increasing(self, service):
        """Test historical trend analysis with increasing yields."""
        historical_yields = [
            HistoricalYieldData(year=2020, yield_per_acre=160.0, crop_type="corn"),
            HistoricalYieldData(year=2021, yield_per_acre=165.0, crop_type="corn"),
            HistoricalYieldData(year=2022, yield_per_acre=170.0, crop_type="corn"),
            HistoricalYieldData(year=2023, yield_per_acre=175.0, crop_type="corn")
        ]
        
        trend = await service._analyze_historical_trends(historical_yields)
        
        assert trend.trend_direction == YieldTrendDirection.INCREASING
        assert trend.trend_slope > 0
        assert trend.average_yield == 167.5
        assert trend.min_yield == 160.0
        assert trend.max_yield == 175.0
        assert trend.r_squared > 0.8  # Strong correlation
    
    @pytest.mark.asyncio
    async def test_historical_trend_analysis_decreasing(self, service):
        """Test historical trend analysis with decreasing yields."""
        historical_yields = [
            HistoricalYieldData(year=2020, yield_per_acre=180.0, crop_type="corn"),
            HistoricalYieldData(year=2021, yield_per_acre=175.0, crop_type="corn"),
            HistoricalYieldData(year=2022, yield_per_acre=170.0, crop_type="corn"),
            HistoricalYieldData(year=2023, yield_per_acre=165.0, crop_type="corn")
        ]
        
        trend = await service._analyze_historical_trends(historical_yields)
        
        assert trend.trend_direction == YieldTrendDirection.DECREASING
        assert trend.trend_slope < 0
        assert trend.average_yield == 172.5
        assert trend.min_yield == 165.0
        assert trend.max_yield == 180.0
    
    @pytest.mark.asyncio
    async def test_historical_trend_analysis_volatile(self, service):
        """Test historical trend analysis with volatile yields."""
        historical_yields = [
            HistoricalYieldData(year=2020, yield_per_acre=250.0, crop_type="corn"),
            HistoricalYieldData(year=2021, yield_per_acre=120.0, crop_type="corn"),
            HistoricalYieldData(year=2022, yield_per_acre=220.0, crop_type="corn"),
            HistoricalYieldData(year=2023, yield_per_acre=130.0, crop_type="corn")
        ]
        
        trend = await service._analyze_historical_trends(historical_yields)
        
        assert trend.trend_direction == YieldTrendDirection.VOLATILE
        assert trend.volatility > 0.2  # High volatility
        assert trend.average_yield == 180.0
        assert trend.min_yield == 120.0
        assert trend.max_yield == 250.0
    
    @pytest.mark.asyncio
    async def test_historical_trend_analysis_insufficient_data(self, service):
        """Test historical trend analysis with insufficient data."""
        historical_yields = [
            HistoricalYieldData(year=2023, yield_per_acre=175.0, crop_type="corn")
        ]
        
        trend = await service._analyze_historical_trends(historical_yields)
        
        assert trend.trend_direction == YieldTrendDirection.STABLE
        assert trend.trend_slope == 0.0
        assert trend.r_squared == 0.0
        assert trend.trend_confidence == 0.3
        assert trend.average_yield == 175.0
        assert trend.min_yield == 175.0
        assert trend.max_yield == 175.0
    
    @pytest.mark.asyncio
    async def test_soil_potential_calculation(self, service):
        """Test soil potential calculation."""
        soil = SoilCharacteristic(
            soil_type="clay_loam",
            ph_level=6.5,
            organic_matter_percent=3.5,
            cation_exchange_capacity=20.0,
            drainage_class="well_drained",
            slope_percent=1.0,
            water_holding_capacity=2.0
        )
        
        potential = await service._calculate_soil_potential(soil, "corn")
        
        assert potential > 0
        assert potential > 150.0  # Should be above baseline
        assert potential < 250.0  # Should be reasonable
    
    @pytest.mark.asyncio
    async def test_weather_potential_calculation(self, service):
        """Test weather potential calculation."""
        weather = WeatherPattern(
            growing_season_precipitation=25.0,
            growing_degree_days=2800,
            drought_stress_days=5,
            heat_stress_days=3,
            frost_risk_days=1,
            optimal_growing_days=130
        )
        
        potential = await service._calculate_weather_potential(weather, "corn")
        
        assert potential > 0
        assert potential > 150.0  # Should be above baseline
        assert potential < 250.0  # Should be reasonable
    
    @pytest.mark.asyncio
    async def test_management_potential_calculation(self, service):
        """Test management potential calculation."""
        management = ManagementPractice(
            tillage_system="no_till",
            irrigation_available=True,
            precision_agriculture=True,
            cover_crop_usage=True,
            crop_rotation="diverse_rotation"
        )
        
        potential = await service._calculate_management_potential(management, "corn")
        
        assert potential > 0
        assert potential > 150.0  # Should be above baseline
        assert potential < 250.0  # Should be reasonable
    
    @pytest.mark.asyncio
    async def test_variety_potential_calculation(self, service):
        """Test variety potential calculation."""
        # Test with known variety
        potential_high_yield = await service._calculate_variety_potential("high_yield_corn", "corn")
        assert potential_high_yield > 150.0
        
        # Test with unknown variety
        potential_unknown = await service._calculate_variety_potential(None, "corn")
        assert potential_unknown > 0
        assert potential_unknown < 180.0  # Should be below baseline (180 * 0.95 = 171)
    
    @pytest.mark.asyncio
    async def test_limiting_factors_identification(self, service):
        """Test limiting factors identification."""
        soil = SoilCharacteristic(
            soil_type="clay_loam",
            ph_level=5.0,  # Low pH
            organic_matter_percent=1.0,  # Low OM
            cation_exchange_capacity=8.0,  # Low CEC
            drainage_class="poorly_drained",  # Poor drainage
            slope_percent=15.0,  # High slope
            water_holding_capacity=1.0
        )
        
        weather = WeatherPattern(
            growing_season_precipitation=10.0,  # Low precipitation
            growing_degree_days=2000,
            drought_stress_days=40,  # High drought stress
            heat_stress_days=25,  # High heat stress
            frost_risk_days=15,  # High frost risk
            optimal_growing_days=80
        )
        
        management = ManagementPractice(
            tillage_system="conventional_till",
            irrigation_available=False,
            precision_agriculture=False,
            cover_crop_usage=False,
            crop_rotation="continuous_corn"
        )
        
        limiting_factors = await service._identify_limiting_factors(soil, weather, management, "corn")
        
        assert len(limiting_factors) > 0
        assert "Suboptimal soil pH" in limiting_factors
        assert "Low organic matter content" in limiting_factors
        assert "Low cation exchange capacity" in limiting_factors
        assert "Poor drainage" in limiting_factors
        assert "Excessive slope" in limiting_factors
        assert "Drought stress" in limiting_factors
        assert "Heat stress" in limiting_factors
        assert "Continuous corn rotation" in limiting_factors
    
    @pytest.mark.asyncio
    async def test_improvement_opportunities_identification(self, service):
        """Test improvement opportunities identification."""
        soil = SoilCharacteristic(
            soil_type="clay_loam",
            ph_level=5.5,
            organic_matter_percent=1.5,
            cation_exchange_capacity=12.0,
            drainage_class="well_drained",
            slope_percent=2.0,
            water_holding_capacity=1.5
        )
        
        weather = WeatherPattern(
            growing_season_precipitation=15.0,
            growing_degree_days=2500,
            drought_stress_days=25,
            heat_stress_days=10,
            frost_risk_days=5,
            optimal_growing_days=100
        )
        
        management = ManagementPractice(
            tillage_system="conventional_till",
            irrigation_available=False,
            precision_agriculture=False,
            cover_crop_usage=False,
            crop_rotation="continuous_corn"
        )
        
        opportunities = await service._identify_improvement_opportunities(soil, weather, management, "corn")
        
        assert len(opportunities) > 0
        assert "Increase organic matter through cover crops or manure" in opportunities
        assert "Adjust soil pH with lime or sulfur" in opportunities
        assert "Adopt precision agriculture technologies" in opportunities
        assert "Implement cover crop system" in opportunities
        assert "Consider reduced tillage or no-till" in opportunities
        assert "Implement crop rotation" in opportunities
    
    @pytest.mark.asyncio
    async def test_goal_recommendations_generation(self, service):
        """Test goal recommendations generation."""
        historical_trend = YieldTrendAnalysis(
            trend_direction=YieldTrendDirection.INCREASING,
            trend_slope=2.5,
            r_squared=0.85,
            volatility=0.12,
            average_yield=175.0,
            min_yield=160.0,
            max_yield=190.0,
            trend_confidence=0.8
        )
        
        potential_assessment = PotentialYieldAssessment(
            soil_potential=185.0,
            weather_potential=180.0,
            management_potential=190.0,
            variety_potential=175.0,
            combined_potential=182.5,
            limiting_factors=["Low organic matter"],
            improvement_opportunities=["Increase organic matter"]
        )
        
        recommendations = await service._generate_goal_recommendations(
            historical_trend,
            potential_assessment,
            YieldGoalType.REALISTIC,
            YieldRiskLevel.MEDIUM
        )
        
        assert len(recommendations) == 4
        
        # Check that recommendations are ordered by risk level
        conservative = next(r for r in recommendations if r.goal_type == YieldGoalType.CONSERVATIVE)
        realistic = next(r for r in recommendations if r.goal_type == YieldGoalType.REALISTIC)
        optimistic = next(r for r in recommendations if r.goal_type == YieldGoalType.OPTIMISTIC)
        stretch = next(r for r in recommendations if r.goal_type == YieldGoalType.STRETCH)
        
        assert conservative.recommended_yield < realistic.recommended_yield
        assert realistic.recommended_yield < optimistic.recommended_yield
        assert optimistic.recommended_yield < stretch.recommended_yield
        
        assert conservative.risk_level == YieldRiskLevel.LOW
        assert realistic.risk_level == YieldRiskLevel.MEDIUM
        assert optimistic.risk_level == YieldRiskLevel.HIGH
        assert stretch.risk_level == YieldRiskLevel.CRITICAL
        
        assert conservative.achievement_probability > realistic.achievement_probability
        assert realistic.achievement_probability > optimistic.achievement_probability
        assert optimistic.achievement_probability > stretch.achievement_probability
    
    @pytest.mark.asyncio
    async def test_yield_goal_validation(self, service, sample_yield_goal_request):
        """Test yield goal validation."""
        analysis = await service.analyze_yield_goals(sample_yield_goal_request)
        
        # Test valid goal
        valid_goal = analysis.historical_trend.average_yield * 1.05  # 5% above average
        validation = await service.validate_yield_goal(valid_goal, analysis)
        
        assert validation.is_valid is True
        assert validation.validation_score > 0.7
        assert len(validation.issues) == 0
        
        # Test invalid goal (too high)
        invalid_goal = analysis.historical_trend.max_yield * 1.5  # 50% above max
        validation = await service.validate_yield_goal(invalid_goal, analysis)
        
        assert validation.is_valid is False
        assert validation.validation_score < 0.5
        assert len(validation.issues) > 0
        assert len(validation.recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_yield_goal_comparison(self, service, sample_yield_goal_request):
        """Test yield goal comparison."""
        analysis = await service.analyze_yield_goals(sample_yield_goal_request)
        comparison = await service.compare_yield_goals(analysis)
        
        assert comparison.conservative_goal is not None
        assert comparison.realistic_goal is not None
        assert comparison.optimistic_goal is not None
        assert comparison.stretch_goal is not None
        
        assert comparison.goal_range > 0
        assert len(comparison.risk_progression) == 4
        assert len(comparison.achievement_probabilities) == 4
        
        # Verify goal ordering
        assert comparison.conservative_goal.recommended_yield < comparison.realistic_goal.recommended_yield
        assert comparison.realistic_goal.recommended_yield < comparison.optimistic_goal.recommended_yield
        assert comparison.optimistic_goal.recommended_yield < comparison.stretch_goal.recommended_yield
    
    @pytest.mark.asyncio
    async def test_analysis_confidence_calculation(self, service, sample_yield_goal_request):
        """Test analysis confidence calculation."""
        confidence = await service._calculate_analysis_confidence(sample_yield_goal_request)
        
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.5  # Should have good confidence with sample data
    
    @pytest.mark.asyncio
    async def test_data_quality_assessment(self, service, sample_yield_goal_request):
        """Test data quality assessment."""
        quality = await service._assess_data_quality(sample_yield_goal_request)
        
        assert 0.0 <= quality <= 1.0
        assert quality > 0.5  # Should have good quality with sample data
    
    @pytest.mark.asyncio
    async def test_error_handling(self, service):
        """Test error handling in service methods."""
        # Test with invalid historical data
        invalid_yields = []  # Empty list
        
        trend = await service._analyze_historical_trends(invalid_yields)
        assert trend.trend_direction == YieldTrendDirection.STABLE
        assert trend.trend_confidence == 0.3
        
        # Test with None weather patterns
        soil = SoilCharacteristic(
            soil_type="clay_loam",
            ph_level=6.5,
            organic_matter_percent=3.0,
            cation_exchange_capacity=15.0,
            drainage_class="well_drained",
            slope_percent=2.0,
            water_holding_capacity=1.5
        )
        
        management = ManagementPractice(
            tillage_system="conventional_till",
            irrigation_available=False,
            precision_agriculture=False,
            cover_crop_usage=False,
            crop_rotation="corn_soybean"
        )
        
        assessment = await service._assess_yield_potential(soil, None, management, "corn", None)
        assert assessment.weather_potential == 0.0  # No weather data
        assert assessment.combined_potential > 0  # Should still calculate other factors
    
    @pytest.mark.asyncio
    async def test_crop_specific_calculations(self, service):
        """Test crop-specific calculations."""
        soil = SoilCharacteristic(
            soil_type="clay_loam",
            ph_level=6.5,
            organic_matter_percent=3.0,
            cation_exchange_capacity=15.0,
            drainage_class="well_drained",
            slope_percent=2.0,
            water_holding_capacity=1.5
        )
        
        # Test different crops
        corn_potential = await service._calculate_soil_potential(soil, "corn")
        soybean_potential = await service._calculate_soil_potential(soil, "soybean")
        wheat_potential = await service._calculate_soil_potential(soil, "wheat")
        
        assert corn_potential > 0
        assert soybean_potential > 0
        assert wheat_potential > 0
        
        # Different crops should have different baselines
        assert corn_potential != soybean_potential
        assert corn_potential != wheat_potential
    
    @pytest.mark.asyncio
    async def test_edge_cases(self, service):
        """Test edge cases and boundary conditions."""
        # Test with extreme soil values
        extreme_soil = SoilCharacteristic(
            soil_type="sand",
            ph_level=3.0,  # Very acidic
            organic_matter_percent=0.5,  # Very low
            cation_exchange_capacity=5.0,  # Very low
            drainage_class="excessively_drained",
            slope_percent=25.0,  # Very steep
            water_holding_capacity=0.5  # Very low
        )
        
        potential = await service._calculate_soil_potential(extreme_soil, "corn")
        assert potential > 0  # Should still return positive value
        assert potential < 150.0  # Should be below baseline
        
        # Test with optimal soil values
        optimal_soil = SoilCharacteristic(
            soil_type="loam",
            ph_level=6.8,  # Optimal
            organic_matter_percent=4.5,  # High
            cation_exchange_capacity=25.0,  # High
            drainage_class="well_drained",
            slope_percent=0.5,  # Minimal slope
            water_holding_capacity=2.5  # High
        )
        
        potential = await service._calculate_soil_potential(optimal_soil, "corn")
        assert potential > 150.0  # Should be above baseline
        assert potential < 300.0  # Should be reasonable


class TestYieldGoalServiceIntegration:
    """Integration tests for yield goal service."""
    
    @pytest.fixture
    def service(self):
        """Create yield goal management service instance."""
        return YieldGoalManagementService()
    
    @pytest.mark.asyncio
    async def test_end_to_end_analysis(self, service):
        """Test complete end-to-end yield goal analysis."""
        # Create comprehensive test data
        historical_yields = [
            HistoricalYieldData(year=2019, yield_per_acre=158.0, crop_type="corn"),
            HistoricalYieldData(year=2020, yield_per_acre=162.0, crop_type="corn"),
            HistoricalYieldData(year=2021, yield_per_acre=168.0, crop_type="corn"),
            HistoricalYieldData(year=2022, yield_per_acre=175.0, crop_type="corn"),
            HistoricalYieldData(year=2023, yield_per_acre=182.0, crop_type="corn")
        ]
        
        soil = SoilCharacteristic(
            soil_type="clay_loam",
            ph_level=6.7,
            organic_matter_percent=3.8,
            cation_exchange_capacity=22.0,
            drainage_class="well_drained",
            slope_percent=1.5,
            water_holding_capacity=2.2
        )
        
        weather = WeatherPattern(
            growing_season_precipitation=24.0,
            growing_degree_days=2850,
            drought_stress_days=8,
            heat_stress_days=5,
            frost_risk_days=2,
            optimal_growing_days=135
        )
        
        management = ManagementPractice(
            tillage_system="strip_till",
            irrigation_available=True,
            precision_agriculture=True,
            cover_crop_usage=True,
            crop_rotation="corn_soybean_wheat",
            planting_date=date(2024, 4, 10),
            harvest_date=date(2024, 10, 20)
        )
        
        request = YieldGoalRequest(
            field_id=uuid4(),
            crop_type="corn",
            variety="high_yield_corn",
            target_year=2024,
            historical_yields=historical_yields,
            soil_characteristics=soil,
            weather_patterns=weather,
            management_practices=management,
            goal_preference=YieldGoalType.REALISTIC,
            risk_tolerance=YieldRiskLevel.MEDIUM
        )
        
        # Perform analysis
        analysis = await service.analyze_yield_goals(request)
        
        # Validate comprehensive results
        assert analysis.analysis_confidence > 0.7
        assert analysis.data_quality_score > 0.8
        assert analysis.overall_risk_level in [YieldRiskLevel.LOW, YieldRiskLevel.MEDIUM]
        
        # Validate trend analysis
        assert analysis.historical_trend.trend_direction == YieldTrendDirection.INCREASING
        assert analysis.historical_trend.trend_slope > 0
        assert analysis.historical_trend.r_squared > 0.8
        
        # Validate potential assessment
        assert analysis.potential_assessment.combined_potential > analysis.historical_trend.average_yield
        
        # Validate recommendations
        assert len(analysis.goal_recommendations) == 4
        for rec in analysis.goal_recommendations:
            assert rec.recommended_yield > 0
            assert rec.confidence_level > 0.2  # Lower threshold for stretch goals
            assert rec.achievement_probability >= 0.1  # Lower threshold for optimistic goals
        
        # Test goal validation
        realistic_goal = next(r for r in analysis.goal_recommendations if r.goal_type == YieldGoalType.REALISTIC)
        validation = await service.validate_yield_goal(realistic_goal.recommended_yield, analysis)
        assert validation.is_valid is True
        
        # Test goal comparison
        comparison = await service.compare_yield_goals(analysis)
        assert comparison.goal_range > 0
        assert len(comparison.risk_progression) == 4
    
    @pytest.mark.asyncio
    async def test_minimal_data_analysis(self, service):
        """Test analysis with minimal input data."""
        # Minimal historical data
        historical_yields = [
            HistoricalYieldData(year=2023, yield_per_acre=175.0, crop_type="corn")
        ]
        
        # Basic soil data
        soil = SoilCharacteristic(
            soil_type="unknown",
            ph_level=6.5,
            organic_matter_percent=2.5,
            cation_exchange_capacity=15.0,
            drainage_class="well_drained",
            slope_percent=2.0,
            water_holding_capacity=1.5
        )
        
        # Basic management
        management = ManagementPractice(
            tillage_system="conventional_till",
            irrigation_available=False,
            precision_agriculture=False,
            cover_crop_usage=False,
            crop_rotation="continuous_corn"
        )
        
        request = YieldGoalRequest(
            field_id=uuid4(),
            crop_type="corn",
            target_year=2024,
            historical_yields=historical_yields,
            soil_characteristics=soil,
            weather_patterns=None,  # No weather data
            management_practices=management,
            goal_preference=YieldGoalType.CONSERVATIVE,
            risk_tolerance=YieldRiskLevel.HIGH
        )
        
        # Should still work with minimal data
        analysis = await service.analyze_yield_goals(request)
        
        assert analysis.analysis_confidence < 0.9  # Lower confidence with minimal data
        assert analysis.data_quality_score < 0.8  # Lower quality score
        assert analysis.potential_assessment.weather_potential == 0.0  # No weather data
        
        # Should still generate recommendations
        assert len(analysis.goal_recommendations) == 4
        for rec in analysis.goal_recommendations:
            assert rec.recommended_yield > 0
            assert rec.confidence_level > 0.1