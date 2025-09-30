"""
Tests for Timing Optimization Service

This module contains comprehensive tests for the fertilizer timing optimization service,
including weather integration, crop growth stage analysis, and multi-objective optimization.
"""

import pytest
import asyncio
import logging
from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock

from ..services.timing_optimization_service import FertilizerTimingOptimizer
from ..models.timing_optimization_models import (
    TimingOptimizationRequest,
    TimingOptimizationResult,
    ApplicationTiming,
    SplitApplicationPlan,
    WeatherWindow,
    WeatherCondition,
    CropGrowthStage,
    ApplicationMethod,
    FertilizerType,
    TimingConstraint,
    EquipmentAvailability,
    LaborAvailability
)


class TestFertilizerTimingOptimizer:
    """Test suite for FertilizerTimingOptimizer service."""
    
    @pytest.fixture
    def optimizer(self):
        """Create timing optimizer instance."""
        return FertilizerTimingOptimizer()
    
    @pytest.fixture
    def sample_request(self):
        """Create sample timing optimization request."""
        return TimingOptimizationRequest(
            field_id="test_field_001",
            crop_type="corn",
            planting_date=date(2024, 4, 15),
            fertilizer_requirements={
                "nitrogen": 150.0,
                "phosphorus": 60.0,
                "potassium": 80.0
            },
            application_methods=[ApplicationMethod.BROADCAST, ApplicationMethod.SIDE_DRESS],
            soil_type="clay_loam",
            soil_moisture_capacity=0.7,
            location={"lat": 40.0, "lng": -95.0},
            optimization_horizon_days=180,
            risk_tolerance=0.5,
            split_application_allowed=True,
            weather_dependent_timing=True,
            soil_temperature_threshold=50.0
        )
    
    @pytest.fixture
    def mock_weather_windows(self):
        """Create mock weather windows."""
        return [
            WeatherWindow(
                start_date=date(2024, 4, 15),
                end_date=date(2024, 4, 15),
                condition=WeatherCondition.OPTIMAL,
                temperature_f=65.0,
                precipitation_probability=0.1,
                wind_speed_mph=8.0,
                soil_moisture=0.6,
                suitability_score=1.0
            ),
            WeatherWindow(
                start_date=date(2024, 5, 15),
                end_date=date(2024, 5, 15),
                condition=WeatherCondition.ACCEPTABLE,
                temperature_f=70.0,
                precipitation_probability=0.2,
                wind_speed_mph=10.0,
                soil_moisture=0.65,
                suitability_score=0.8
            ),
            WeatherWindow(
                start_date=date(2024, 6, 15),
                end_date=date(2024, 6, 15),
                condition=WeatherCondition.MARGINAL,
                temperature_f=75.0,
                precipitation_probability=0.3,
                wind_speed_mph=12.0,
                soil_moisture=0.7,
                suitability_score=0.6
            )
        ]
    
    @pytest.mark.asyncio
    async def test_optimize_timing_success(self, optimizer, sample_request):
        """Test successful timing optimization."""
        with patch.object(optimizer, '_analyze_weather_windows') as mock_weather:
            with patch.object(optimizer, '_determine_crop_growth_stages') as mock_stages:
                with patch.object(optimizer, '_optimize_fertilizer_timing') as mock_timing:
                    with patch.object(optimizer, '_generate_split_plans') as mock_split:
                        with patch.object(optimizer, '_calculate_optimization_metrics') as mock_metrics:
                            with patch.object(optimizer, '_generate_recommendations') as mock_recommendations:
                                with patch.object(optimizer, '_calculate_economic_analysis') as mock_economic:
                                    
                                    # Setup mocks
                                    mock_weather.return_value = []
                                    mock_stages.return_value = {
                                        date(2024, 4, 15): CropGrowthStage.PLANTING,
                                        date(2024, 5, 15): CropGrowthStage.V6
                                    }
                                    mock_timing.return_value = []
                                    mock_split.return_value = []
                                    mock_metrics.return_value = {
                                        "overall_score": 0.85,
                                        "weather_score": 0.8,
                                        "crop_score": 0.9,
                                        "risk_score": 0.3,
                                        "confidence": 0.8
                                    }
                                    mock_recommendations.return_value = ["Test recommendation"]
                                    mock_economic.return_value = {
                                        "total_cost": 150.0,
                                        "cost_per_acre": 150.0,
                                        "yield_impact": 5.0,
                                        "roi": 0.15
                                    }
                                    
                                    # Execute test
                                    result = await optimizer.optimize_timing(sample_request)
                                    
                                    # Assertions
                                    assert isinstance(result, TimingOptimizationResult)
                                    assert result.request_id == sample_request.request_id
                                    assert result.overall_timing_score == 0.85
                                    assert result.weather_suitability_score == 0.8
                                    assert result.crop_stage_alignment_score == 0.9
                                    assert result.risk_score == 0.3
                                    assert result.confidence_score == 0.8
                                    assert result.total_estimated_cost == 150.0
                                    assert result.cost_per_acre == 150.0
                                    assert result.expected_yield_impact == 5.0
                                    assert result.roi_estimate == 0.15
                                    assert len(result.recommendations) > 0
                                    assert result.processing_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_analyze_weather_windows(self, optimizer, sample_request):
        """Test weather window analysis."""
        weather_windows = await optimizer._analyze_weather_windows(sample_request)
        
        assert isinstance(weather_windows, list)
        assert len(weather_windows) > 0
        
        for window in weather_windows:
            assert isinstance(window, WeatherWindow)
            assert window.start_date >= sample_request.planting_date
            assert window.end_date <= sample_request.planting_date + timedelta(days=sample_request.optimization_horizon_days)
            assert 0.0 <= window.suitability_score <= 1.0
            assert 0.0 <= window.precipitation_probability <= 1.0
            assert 0.0 <= window.soil_moisture <= 1.0
    
    @pytest.mark.asyncio
    async def test_determine_crop_growth_stages_corn(self, optimizer, sample_request):
        """Test crop growth stage determination for corn."""
        crop_stages = await optimizer._determine_crop_growth_stages(sample_request)
        
        assert isinstance(crop_stages, dict)
        assert len(crop_stages) > 0
        
        # Check that planting date is included
        assert sample_request.planting_date in crop_stages
        assert crop_stages[sample_request.planting_date] == CropGrowthStage.PLANTING
        
        # Check that key growth stages are included
        stage_values = list(crop_stages.values())
        assert CropGrowthStage.EMERGENCE in stage_values
        assert CropGrowthStage.V6 in stage_values
        assert CropGrowthStage.VT in stage_values
        assert CropGrowthStage.R1 in stage_values
        assert CropGrowthStage.HARVEST in stage_values
    
    @pytest.mark.asyncio
    async def test_determine_crop_growth_stages_soybean(self, optimizer):
        """Test crop growth stage determination for soybean."""
        soybean_request = TimingOptimizationRequest(
            field_id="test_field_002",
            crop_type="soybean",
            planting_date=date(2024, 5, 1),
            fertilizer_requirements={"nitrogen": 50.0},
            application_methods=[ApplicationMethod.BROADCAST],
            soil_type="loam",
            soil_moisture_capacity=0.6,
            location={"lat": 40.0, "lng": -95.0}
        )
        
        crop_stages = await optimizer._determine_crop_growth_stages(soybean_request)
        
        assert isinstance(crop_stages, dict)
        assert len(crop_stages) > 0
        
        # Check soybean-specific stages
        stage_values = list(crop_stages.values())
        assert CropGrowthStage.PLANTING in stage_values
        assert CropGrowthStage.EMERGENCE in stage_values
        assert CropGrowthStage.R1 in stage_values
        assert CropGrowthStage.HARVEST in stage_values
    
    @pytest.mark.asyncio
    async def test_optimize_fertilizer_timing_nitrogen(self, optimizer, sample_request, mock_weather_windows):
        """Test nitrogen timing optimization."""
        crop_stages = {
            date(2024, 4, 15): CropGrowthStage.PLANTING,
            date(2024, 5, 15): CropGrowthStage.V6
        }
        
        timings = await optimizer._optimize_fertilizer_timing(
            "nitrogen", 150.0, sample_request, mock_weather_windows, crop_stages
        )
        
        assert isinstance(timings, list)
        assert len(timings) > 0
        
        for timing in timings:
            assert isinstance(timing, ApplicationTiming)
            assert timing.fertilizer_type == "nitrogen"
            assert timing.amount_lbs_per_acre == 150.0
            assert 0.0 <= timing.timing_score <= 1.0
            assert 0.0 <= timing.weather_score <= 1.0
            assert 0.0 <= timing.crop_score <= 1.0
            assert 0.0 <= timing.soil_score <= 1.0
            assert 0.0 <= timing.weather_risk <= 1.0
            assert 0.0 <= timing.timing_risk <= 1.0
            assert 0.0 <= timing.equipment_risk <= 1.0
            assert timing.estimated_cost_per_acre >= 0.0
    
    @pytest.mark.asyncio
    async def test_generate_split_plans(self, optimizer, sample_request):
        """Test split application plan generation."""
        # Create mock timings
        mock_timings = [
            ApplicationTiming(
                fertilizer_type="nitrogen",
                application_method=ApplicationMethod.BROADCAST,
                recommended_date=date(2024, 4, 15),
                application_window=WeatherWindow(
                    start_date=date(2024, 4, 15),
                    end_date=date(2024, 4, 15),
                    condition=WeatherCondition.OPTIMAL,
                    temperature_f=65.0,
                    precipitation_probability=0.1,
                    wind_speed_mph=8.0,
                    soil_moisture=0.6,
                    suitability_score=1.0
                ),
                crop_stage=CropGrowthStage.PLANTING,
                amount_lbs_per_acre=90.0,
                timing_score=0.9,
                weather_score=1.0,
                crop_score=1.0,
                soil_score=0.9,
                weather_risk=0.1,
                timing_risk=0.2,
                equipment_risk=0.1,
                estimated_cost_per_acre=45.0,
                yield_impact_percent=3.0
            ),
            ApplicationTiming(
                fertilizer_type="nitrogen",
                application_method=ApplicationMethod.SIDE_DRESS,
                recommended_date=date(2024, 5, 15),
                application_window=WeatherWindow(
                    start_date=date(2024, 5, 15),
                    end_date=date(2024, 5, 15),
                    condition=WeatherCondition.ACCEPTABLE,
                    temperature_f=70.0,
                    precipitation_probability=0.2,
                    wind_speed_mph=10.0,
                    soil_moisture=0.65,
                    suitability_score=0.8
                ),
                crop_stage=CropGrowthStage.V6,
                amount_lbs_per_acre=60.0,
                timing_score=0.8,
                weather_score=0.8,
                crop_score=1.0,
                soil_score=0.8,
                weather_risk=0.2,
                timing_risk=0.3,
                equipment_risk=0.2,
                estimated_cost_per_acre=30.0,
                yield_impact_percent=2.0
            )
        ]
        
        split_plans = await optimizer._generate_split_plans(sample_request, mock_timings)
        
        assert isinstance(split_plans, list)
        
        for plan in split_plans:
            assert isinstance(plan, SplitApplicationPlan)
            assert plan.fertilizer_type in sample_request.fertilizer_requirements
            assert plan.total_amount_lbs_per_acre > 0
            assert len(plan.applications) > 1  # Split applications
            assert len(plan.split_ratio) == len(plan.applications)
            assert abs(sum(plan.split_ratio) - 1.0) < 0.01  # Ratios should sum to 1
            assert 0.0 <= plan.total_timing_score <= 1.0
            assert plan.risk_reduction_percent >= 0.0
    
    @pytest.mark.asyncio
    async def test_calculate_optimization_metrics(self, optimizer, sample_request):
        """Test optimization metrics calculation."""
        mock_timings = [
            ApplicationTiming(
                fertilizer_type="nitrogen",
                application_method=ApplicationMethod.BROADCAST,
                recommended_date=date(2024, 4, 15),
                application_window=WeatherWindow(
                    start_date=date(2024, 4, 15),
                    end_date=date(2024, 4, 15),
                    condition=WeatherCondition.OPTIMAL,
                    temperature_f=65.0,
                    precipitation_probability=0.1,
                    wind_speed_mph=8.0,
                    soil_moisture=0.6,
                    suitability_score=1.0
                ),
                crop_stage=CropGrowthStage.PLANTING,
                amount_lbs_per_acre=150.0,
                timing_score=0.9,
                weather_score=1.0,
                crop_score=1.0,
                soil_score=0.9,
                weather_risk=0.1,
                timing_risk=0.2,
                equipment_risk=0.1,
                estimated_cost_per_acre=75.0,
                yield_impact_percent=5.0
            )
        ]
        
        mock_weather_windows = []
        
        metrics = await optimizer._calculate_optimization_metrics(
            sample_request, mock_timings, mock_weather_windows
        )
        
        assert isinstance(metrics, dict)
        assert "overall_score" in metrics
        assert "weather_score" in metrics
        assert "crop_score" in metrics
        assert "risk_score" in metrics
        assert "confidence" in metrics
        
        assert 0.0 <= metrics["overall_score"] <= 1.0
        assert 0.0 <= metrics["weather_score"] <= 1.0
        assert 0.0 <= metrics["crop_score"] <= 1.0
        assert 0.0 <= metrics["risk_score"] <= 1.0
        assert 0.0 <= metrics["confidence"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_generate_recommendations(self, optimizer, sample_request):
        """Test recommendation generation."""
        mock_timings = []
        mock_split_plans = []
        mock_metrics = {
            "overall_score": 0.85,
            "weather_score": 0.8,
            "crop_score": 0.9,
            "risk_score": 0.3,
            "confidence": 0.8
        }
        
        recommendations = await optimizer._generate_recommendations(
            sample_request, mock_timings, mock_split_plans, mock_metrics
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        for recommendation in recommendations:
            assert isinstance(recommendation, str)
            assert len(recommendation) > 0
    
    @pytest.mark.asyncio
    async def test_calculate_economic_analysis(self, optimizer, sample_request):
        """Test economic analysis calculation."""
        mock_timings = [
            ApplicationTiming(
                fertilizer_type="nitrogen",
                application_method=ApplicationMethod.BROADCAST,
                recommended_date=date(2024, 4, 15),
                application_window=WeatherWindow(
                    start_date=date(2024, 4, 15),
                    end_date=date(2024, 4, 15),
                    condition=WeatherCondition.OPTIMAL,
                    temperature_f=65.0,
                    precipitation_probability=0.1,
                    wind_speed_mph=8.0,
                    soil_moisture=0.6,
                    suitability_score=1.0
                ),
                crop_stage=CropGrowthStage.PLANTING,
                amount_lbs_per_acre=150.0,
                timing_score=0.9,
                weather_score=1.0,
                crop_score=1.0,
                soil_score=0.9,
                weather_risk=0.1,
                timing_risk=0.2,
                equipment_risk=0.1,
                estimated_cost_per_acre=75.0,
                yield_impact_percent=5.0
            )
        ]
        
        mock_split_plans = []
        
        economic_analysis = await optimizer._calculate_economic_analysis(
            sample_request, mock_timings, mock_split_plans
        )
        
        assert isinstance(economic_analysis, dict)
        assert "total_cost" in economic_analysis
        assert "cost_per_acre" in economic_analysis
        assert "yield_impact" in economic_analysis
        assert "roi" in economic_analysis
        
        assert economic_analysis["total_cost"] >= 0.0
        assert economic_analysis["cost_per_acre"] >= 0.0
        assert economic_analysis["yield_impact"] >= 0.0
    
    @pytest.mark.asyncio
    async def test_assess_weather_condition(self, optimizer, sample_request):
        """Test weather condition assessment."""
        test_date = date(2024, 4, 15)
        condition = await optimizer._assess_weather_condition(test_date, sample_request)
        
        assert isinstance(condition, WeatherCondition)
        assert condition in [
            WeatherCondition.OPTIMAL,
            WeatherCondition.ACCEPTABLE,
            WeatherCondition.MARGINAL,
            WeatherCondition.POOR,
            WeatherCondition.UNACCEPTABLE
        ]
    
    @pytest.mark.asyncio
    async def test_find_best_weather_window(self, optimizer, sample_request, mock_weather_windows):
        """Test best weather window finding."""
        target_date = date(2024, 4, 15)
        
        best_window = await optimizer._find_best_weather_window(
            target_date, mock_weather_windows, sample_request
        )
        
        if best_window:
            assert isinstance(best_window, WeatherWindow)
            days_diff = abs((best_window.start_date - target_date).days)
            assert days_diff <= 7  # Within 7 days
    
    def test_crop_timing_params(self, optimizer):
        """Test crop timing parameters."""
        assert "corn" in optimizer.crop_timing_params
        assert "soybean" in optimizer.crop_timing_params
        assert "wheat" in optimizer.crop_timing_params
        
        corn_params = optimizer.crop_timing_params["corn"]
        assert "critical_stages" in corn_params
        assert "nitrogen_timing" in corn_params
        assert "phosphorus_timing" in corn_params
        assert "potassium_timing" in corn_params
        assert "temperature_threshold" in corn_params
        assert "soil_moisture_optimal" in corn_params
    
    def test_weather_scores(self, optimizer):
        """Test weather condition scoring."""
        assert optimizer.weather_scores[WeatherCondition.OPTIMAL] == 1.0
        assert optimizer.weather_scores[WeatherCondition.ACCEPTABLE] == 0.8
        assert optimizer.weather_scores[WeatherCondition.MARGINAL] == 0.6
        assert optimizer.weather_scores[WeatherCondition.POOR] == 0.3
        assert optimizer.weather_scores[WeatherCondition.UNACCEPTABLE] == 0.0


class TestTimingOptimizationModels:
    """Test suite for timing optimization models."""
    
    def test_timing_optimization_request_validation(self):
        """Test timing optimization request validation."""
        # Valid request
        request = TimingOptimizationRequest(
            field_id="test_field",
            crop_type="corn",
            planting_date=date(2024, 4, 15),
            fertilizer_requirements={"nitrogen": 150.0},
            application_methods=[ApplicationMethod.BROADCAST],
            soil_type="loam",
            soil_moisture_capacity=0.6,
            location={"lat": 40.0, "lng": -95.0}
        )
        
        assert request.field_id == "test_field"
        assert request.crop_type == "corn"
        assert request.planting_date == date(2024, 4, 15)
        assert request.fertilizer_requirements["nitrogen"] == 150.0
        assert ApplicationMethod.BROADCAST in request.application_methods
        assert request.soil_type == "loam"
        assert request.location["lat"] == 40.0
        assert request.location["lng"] == -95.0
    
    def test_timing_optimization_request_invalid_fertilizer(self):
        """Test invalid fertilizer requirements."""
        with pytest.raises(ValueError):
            TimingOptimizationRequest(
                field_id="test_field",
                crop_type="corn",
                planting_date=date(2024, 4, 15),
                fertilizer_requirements={},  # Empty requirements
                application_methods=[ApplicationMethod.BROADCAST],
                soil_type="loam",
                location={"lat": 40.0, "lng": -95.0}
            )
    
    def test_timing_optimization_request_invalid_location(self):
        """Test invalid location coordinates."""
        with pytest.raises(ValueError):
            TimingOptimizationRequest(
                field_id="test_field",
                crop_type="corn",
                planting_date=date(2024, 4, 15),
                fertilizer_requirements={"nitrogen": 150.0},
                application_methods=[ApplicationMethod.BROADCAST],
                soil_type="loam",
                location={"lat": 200.0, "lng": -95.0}  # Invalid latitude
            )
    
    def test_weather_window_creation(self):
        """Test weather window creation."""
        window = WeatherWindow(
            start_date=date(2024, 4, 15),
            end_date=date(2024, 4, 15),
            condition=WeatherCondition.OPTIMAL,
            temperature_f=65.0,
            precipitation_probability=0.1,
            wind_speed_mph=8.0,
            soil_moisture=0.6,
            suitability_score=1.0
        )
        
        assert window.start_date == date(2024, 4, 15)
        assert window.end_date == date(2024, 4, 15)
        assert window.condition == WeatherCondition.OPTIMAL
        assert window.temperature_f == 65.0
        assert window.precipitation_probability == 0.1
        assert window.wind_speed_mph == 8.0
        assert window.soil_moisture == 0.6
        assert window.suitability_score == 1.0
    
    def test_application_timing_creation(self):
        """Test application timing creation."""
        timing = ApplicationTiming(
            fertilizer_type="nitrogen",
            application_method=ApplicationMethod.BROADCAST,
            recommended_date=date(2024, 4, 15),
            application_window=WeatherWindow(
                start_date=date(2024, 4, 15),
                end_date=date(2024, 4, 15),
                condition=WeatherCondition.OPTIMAL,
                temperature_f=65.0,
                precipitation_probability=0.1,
                wind_speed_mph=8.0,
                soil_moisture=0.6,
                suitability_score=1.0
            ),
            crop_stage=CropGrowthStage.PLANTING,
            amount_lbs_per_acre=150.0,
            timing_score=0.9,
            weather_score=1.0,
            crop_score=1.0,
            soil_score=0.9,
            weather_risk=0.1,
            timing_risk=0.2,
            equipment_risk=0.1,
            estimated_cost_per_acre=75.0,
            yield_impact_percent=5.0
        )
        
        assert timing.fertilizer_type == "nitrogen"
        assert timing.application_method == ApplicationMethod.BROADCAST
        assert timing.recommended_date == date(2024, 4, 15)
        assert timing.crop_stage == CropGrowthStage.PLANTING
        assert timing.amount_lbs_per_acre == 150.0
        assert timing.timing_score == 0.9
        assert timing.weather_score == 1.0
        assert timing.crop_score == 1.0
        assert timing.soil_score == 0.9
        assert timing.weather_risk == 0.1
        assert timing.timing_risk == 0.2
        assert timing.equipment_risk == 0.1
        assert timing.estimated_cost_per_acre == 75.0
        assert timing.yield_impact_percent == 5.0


class TestTimingOptimizationIntegration:
    """Integration tests for timing optimization."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_timing_optimization(self):
        """Test end-to-end timing optimization workflow."""
        optimizer = FertilizerTimingOptimizer()
        
        request = TimingOptimizationRequest(
            field_id="integration_test_field",
            crop_type="corn",
            planting_date=date(2024, 4, 15),
            fertilizer_requirements={
                "nitrogen": 150.0,
                "phosphorus": 60.0,
                "potassium": 80.0
            },
            application_methods=[ApplicationMethod.BROADCAST, ApplicationMethod.SIDE_DRESS],
            soil_type="clay_loam",
            soil_moisture_capacity=0.7,
            location={"lat": 40.0, "lng": -95.0},
            optimization_horizon_days=180,
            risk_tolerance=0.5,
            split_application_allowed=True,
            weather_dependent_timing=True,
            soil_temperature_threshold=50.0
        )
        
        result = await optimizer.optimize_timing(request)
        
        # Verify result structure
        assert isinstance(result, TimingOptimizationResult)
        assert result.request_id == request.request_id
        assert len(result.optimal_timings) > 0
        assert len(result.weather_windows) > 0
        assert len(result.recommendations) > 0
        
        # Verify timing scores
        assert 0.0 <= result.overall_timing_score <= 1.0
        assert 0.0 <= result.weather_suitability_score <= 1.0
        assert 0.0 <= result.crop_stage_alignment_score <= 1.0
        assert 0.0 <= result.risk_score <= 1.0
        assert 0.0 <= result.confidence_score <= 1.0
        
        # Verify economic analysis
        assert result.total_estimated_cost >= 0.0
        assert result.cost_per_acre >= 0.0
        assert result.expected_yield_impact >= 0.0
        
        # Verify processing time
        assert result.processing_time_ms > 0.0
        
        logging.info(f"Integration test completed successfully: {len(result.optimal_timings)} timings optimized")


if __name__ == "__main__":
    pytest.main([__file__])