"""
Comprehensive tests for crop response and application method optimization service.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from typing import Dict, List, Any

from src.services.crop_response_service import (
    CropResponseService, CropResponseData, MethodEffectivenessRanking, 
    YieldImpactPrediction, ResponseMetric
)
from src.models.application_models import ApplicationMethodType, CropRequirements
from src.services.crop_integration_service import CropType, GrowthStage


class TestCropResponseService:
    """Test suite for crop response service."""
    
    @pytest.fixture
    def service(self):
        return CropResponseService()
    
    @pytest.fixture
    def sample_field_conditions(self):
        return {
            "weather": {
                "temperature_celsius": 22.0,
                "humidity_percent": 65.0,
                "wind_speed_kmh": 8.0,
                "precipitation_mm": 5.0
            },
            "soil": {
                "ph": 6.5,
                "organic_matter_percent": 3.2,
                "slope_percent": 2.0,
                "drainage_class": "well_drained"
            }
        }
    
    @pytest.fixture
    def sample_crop_requirements(self):
        return CropRequirements(
            crop_type="corn",
            growth_stage="V6",
            target_yield=180.0,
            nutrient_requirements={
                "nitrogen": 150.0,
                "phosphorus": 60.0,
                "potassium": 120.0
            },
            application_timing_preferences=["early_morning", "evening"]
        )
    
    @pytest.mark.asyncio
    async def test_analyze_crop_response_success(self, service, sample_field_conditions):
        """Test successful crop response analysis."""
        result = await service.analyze_crop_response(
            CropType.CORN,
            ApplicationMethodType.BAND,
            GrowthStage.V6,
            150.0,
            sample_field_conditions
        )
        
        assert result.method_type == ApplicationMethodType.BAND
        assert result.crop_type == CropType.CORN
        assert result.growth_stage == GrowthStage.V6
        assert 0.0 <= result.yield_response <= 1.0
        assert 0.0 <= result.nutrient_efficiency <= 1.0
        assert 0.0 <= result.confidence_score <= 1.0
        assert result.validation_status == "analyzed"
    
    @pytest.mark.asyncio
    async def test_analyze_crop_response_invalid_crop(self, service, sample_field_conditions):
        """Test crop response analysis with invalid crop."""
        with pytest.raises(ValueError):
            await service.analyze_crop_response(
                "invalid_crop",  # Invalid crop type
                ApplicationMethodType.BAND,
                GrowthStage.V6,
                150.0,
                sample_field_conditions
            )
    
    @pytest.mark.asyncio
    async def test_rank_method_effectiveness(self, service, sample_field_conditions, sample_crop_requirements):
        """Test method effectiveness ranking."""
        available_methods = [
            ApplicationMethodType.BROADCAST,
            ApplicationMethodType.BAND,
            ApplicationMethodType.SIDEDRESS
        ]
        
        rankings = await service.rank_method_effectiveness(
            CropType.CORN,
            available_methods,
            sample_field_conditions,
            sample_crop_requirements
        )
        
        assert len(rankings) == 3
        assert all(isinstance(ranking, MethodEffectivenessRanking) for ranking in rankings)
        
        # Check that rankings are sorted by overall score (descending)
        scores = [ranking.overall_score for ranking in rankings]
        assert scores == sorted(scores, reverse=True)
        
        # Check that all methods are included
        method_types = [ranking.method_type for ranking in rankings]
        assert set(method_types) == set(available_methods)
    
    @pytest.mark.asyncio
    async def test_predict_yield_impact(self, service, sample_field_conditions):
        """Test yield impact prediction."""
        prediction = await service.predict_yield_impact(
            CropType.CORN,
            ApplicationMethodType.BAND,
            150.0,  # baseline yield
            120.0,  # application rate
            sample_field_conditions
        )
        
        assert prediction.method_type == ApplicationMethodType.BAND
        assert prediction.crop_type == CropType.CORN
        assert prediction.baseline_yield == 150.0
        assert prediction.predicted_yield > prediction.baseline_yield
        assert prediction.yield_increase_percent > 0
        assert prediction.confidence > 0
        assert len(prediction.yield_range) == 2
        assert prediction.yield_range[0] <= prediction.predicted_yield <= prediction.yield_range[1]
    
    @pytest.mark.asyncio
    async def test_predict_yield_impact_soybean(self, service, sample_field_conditions):
        """Test yield impact prediction for soybean."""
        prediction = await service.predict_yield_impact(
            CropType.SOYBEAN,
            ApplicationMethodType.BROADCAST,
            50.0,  # baseline yield
            80.0,  # application rate
            sample_field_conditions
        )
        
        assert prediction.crop_type == CropType.SOYBEAN
        assert prediction.baseline_yield == 50.0
        assert prediction.predicted_yield >= prediction.baseline_yield
    
    def test_get_base_response_data(self, service):
        """Test getting base response data."""
        # Test existing data
        data = service._get_base_response_data(CropType.CORN, ApplicationMethodType.BAND)
        assert data is not None
        assert data.crop_type == CropType.CORN
        assert data.method_type == ApplicationMethodType.BAND
        
        # Test non-existing data
        data = service._get_base_response_data(CropType.CORN, ApplicationMethodType.DRIP)
        assert data is None
    
    def test_calculate_growth_stage_adjustment(self, service):
        """Test growth stage adjustment calculation."""
        adjustment = service._calculate_growth_stage_adjustment(
            CropType.CORN, ApplicationMethodType.BAND, GrowthStage.V6
        )
        
        assert isinstance(adjustment, dict)
        assert "yield" in adjustment
        assert "efficiency" in adjustment
        assert "growth" in adjustment
        assert "stress" in adjustment
        assert "quality" in adjustment
        assert "confidence" in adjustment
        
        # All adjustments should be positive
        for value in adjustment.values():
            assert value > 0
    
    def test_calculate_rate_adjustment(self, service):
        """Test application rate adjustment calculation."""
        # Test optimal rate
        adjustment = service._calculate_rate_adjustment(ApplicationMethodType.BAND, 120.0)
        assert adjustment["yield"] == 1.0  # Should be optimal
        
        # Test under-application
        adjustment = service._calculate_rate_adjustment(ApplicationMethodType.BAND, 50.0)
        assert adjustment["yield"] < 1.0  # Should be reduced
        
        # Test over-application
        adjustment = service._calculate_rate_adjustment(ApplicationMethodType.BAND, 300.0)
        assert adjustment["yield"] < 1.0  # Should be reduced
    
    def test_calculate_field_condition_adjustment(self, service):
        """Test field condition adjustment calculation."""
        field_conditions = {
            "weather": {"temperature_celsius": 35.0, "humidity_percent": 20.0},
            "soil": {"ph": 5.0, "organic_matter_percent": 1.0}
        }
        
        adjustment = service._calculate_field_condition_adjustment(
            field_conditions, ApplicationMethodType.BAND
        )
        
        assert isinstance(adjustment, dict)
        assert "yield" in adjustment
        assert "efficiency" in adjustment
        assert "stress" in adjustment
        
        # Stress should be reduced due to high temperature and low humidity
        assert adjustment["stress"] < 1.0
    
    def test_adjust_metric(self, service):
        """Test metric adjustment function."""
        # Test normal adjustment
        result = service._adjust_metric(0.8, 1.1, 0.9)
        assert result == 0.8 * 1.1 * 0.9
        
        # Test clamping to [0, 1]
        result = service._adjust_metric(0.5, 2.0, 2.0)
        assert result == 1.0
        
        result = service._adjust_metric(0.5, -1.0, -1.0)
        assert result == 0.0
    
    def test_calculate_cost_effectiveness(self, service):
        """Test cost effectiveness calculation."""
        response_data = CropResponseData(
            method_type=ApplicationMethodType.BAND,
            crop_type=CropType.CORN,
            growth_stage=GrowthStage.V6,
            yield_response=0.9,
            nutrient_efficiency=0.85
        )
        
        effectiveness = service._calculate_cost_effectiveness(ApplicationMethodType.BAND, response_data)
        assert 0.0 <= effectiveness <= 1.0
    
    def test_calculate_environmental_score(self, service, sample_field_conditions):
        """Test environmental score calculation."""
        score = service._calculate_environmental_score(ApplicationMethodType.BAND, sample_field_conditions)
        assert 0.0 <= score <= 1.0
        
        # Test with high slope (should reduce score)
        high_slope_conditions = sample_field_conditions.copy()
        high_slope_conditions["soil"]["slope_percent"] = 10.0
        score_high_slope = service._calculate_environmental_score(ApplicationMethodType.BAND, high_slope_conditions)
        assert score_high_slope < score
    
    def test_calculate_labor_efficiency(self, service, sample_field_conditions):
        """Test labor efficiency calculation."""
        efficiency = service._calculate_labor_efficiency(ApplicationMethodType.BAND, sample_field_conditions)
        assert 0.0 <= efficiency <= 1.0
    
    def test_get_method_limitations(self, service, sample_field_conditions):
        """Test method limitations identification."""
        limitations = service._get_method_limitations(ApplicationMethodType.FOLIAR, sample_field_conditions)
        assert isinstance(limitations, list)
        assert "Limited nutrient capacity" in limitations
        assert "Weather dependent" in limitations
    
    def test_get_method_advantages(self, service, sample_field_conditions):
        """Test method advantages identification."""
        advantages = service._get_method_advantages(ApplicationMethodType.BAND, sample_field_conditions)
        assert isinstance(advantages, list)
        assert "High nutrient use efficiency" in advantages
        assert "Reduced environmental impact" in advantages
    
    def test_get_optimal_conditions(self, service):
        """Test optimal conditions identification."""
        conditions = service._get_optimal_conditions(ApplicationMethodType.FOLIAR, CropType.CORN)
        assert isinstance(conditions, dict)
        assert "soil_ph_range" in conditions
        assert "temperature_range" in conditions
        assert "wind_speed_max" in conditions
    
    def test_get_application_guidance(self, service):
        """Test application guidance generation."""
        guidance = service._get_application_guidance(ApplicationMethodType.BAND, CropType.CORN)
        assert isinstance(guidance, list)
        assert len(guidance) > 0
    
    def test_get_yield_prediction_model(self, service):
        """Test yield prediction model retrieval."""
        model = service._get_yield_prediction_model(CropType.CORN, ApplicationMethodType.BAND)
        assert model is not None
        assert "base_yield" in model
        assert "response_coefficient" in model
        assert "efficiency_factor" in model
        
        # Test non-existing model
        model = service._get_yield_prediction_model(CropType.CORN, ApplicationMethodType.DRIP)
        assert model is None
    
    def test_calculate_timing_factor(self, service, sample_field_conditions):
        """Test timing factor calculation."""
        factor = service._calculate_timing_factor(ApplicationMethodType.BAND, sample_field_conditions)
        assert 0.0 <= factor <= 1.0
        
        # Test with cold conditions
        cold_conditions = sample_field_conditions.copy()
        cold_conditions["weather"]["temperature_celsius"] = 5.0
        cold_factor = service._calculate_timing_factor(ApplicationMethodType.BAND, cold_conditions)
        assert cold_factor < factor
    
    def test_calculate_field_yield_factor(self, service, sample_field_conditions):
        """Test field yield factor calculation."""
        factor = service._calculate_field_yield_factor(sample_field_conditions)
        assert 0.0 <= factor <= 1.0
        
        # Test with poor soil conditions
        poor_conditions = sample_field_conditions.copy()
        poor_conditions["soil"]["ph"] = 4.0
        poor_conditions["soil"]["organic_matter_percent"] = 1.0
        poor_factor = service._calculate_field_yield_factor(poor_conditions)
        assert poor_factor < factor
    
    def test_get_crop_price(self, service):
        """Test crop price retrieval."""
        corn_price = service._get_crop_price(CropType.CORN)
        assert corn_price > 0
        
        soybean_price = service._get_crop_price(CropType.SOYBEAN)
        assert soybean_price > 0
        
        wheat_price = service._get_crop_price(CropType.WHEAT)
        assert wheat_price > 0
    
    def test_get_method_cost(self, service):
        """Test method cost retrieval."""
        cost = service._get_method_cost(ApplicationMethodType.BAND)
        assert cost > 0
        
        # Test different methods have different costs
        broadcast_cost = service._get_method_cost(ApplicationMethodType.BROADCAST)
        injection_cost = service._get_method_cost(ApplicationMethodType.INJECTION)
        assert broadcast_cost != injection_cost
    
    def test_identify_yield_risk_factors(self, service, sample_field_conditions):
        """Test yield risk factor identification."""
        risks = service._identify_yield_risk_factors(ApplicationMethodType.BAND, sample_field_conditions)
        assert isinstance(risks, list)
        
        # Test with high temperature
        hot_conditions = sample_field_conditions.copy()
        hot_conditions["weather"]["temperature_celsius"] = 40.0
        hot_risks = service._identify_yield_risk_factors(ApplicationMethodType.BAND, hot_conditions)
        assert "High temperature stress" in hot_risks
        
        # Test with high slope
        steep_conditions = sample_field_conditions.copy()
        steep_conditions["soil"]["slope_percent"] = 10.0
        steep_risks = service._identify_yield_risk_factors(ApplicationMethodType.BAND, steep_conditions)
        assert "High slope increases runoff risk" in steep_risks


class TestAgriculturalValidation:
    """Agricultural validation tests for crop response service."""
    
    @pytest.fixture
    def service(self):
        return CropResponseService()
    
    @pytest.mark.asyncio
    async def test_corn_band_method_superiority(self, service):
        """Test that band application is superior to broadcast for corn."""
        field_conditions = {
            "weather": {"temperature_celsius": 22.0, "humidity_percent": 65.0},
            "soil": {"ph": 6.5, "organic_matter_percent": 3.2}
        }
        
        crop_requirements = CropRequirements(
            crop_type="corn",
            growth_stage="V6",
            nutrient_requirements={"nitrogen": 150.0}
        )
        
        rankings = await service.rank_method_effectiveness(
            CropType.CORN,
            [ApplicationMethodType.BROADCAST, ApplicationMethodType.BAND],
            field_conditions,
            crop_requirements
        )
        
        # Band method should rank higher than broadcast
        band_ranking = next(r for r in rankings if r.method_type == ApplicationMethodType.BAND)
        broadcast_ranking = next(r for r in rankings if r.method_type == ApplicationMethodType.BROADCAST)
        
        assert band_ranking.overall_score > broadcast_ranking.overall_score
        assert band_ranking.efficiency_score > broadcast_ranking.efficiency_score
    
    @pytest.mark.asyncio
    async def test_soybean_nitrogen_fixation_consideration(self, service):
        """Test that soybean recommendations consider nitrogen fixation."""
        field_conditions = {
            "weather": {"temperature_celsius": 22.0, "humidity_percent": 65.0},
            "soil": {"ph": 6.5, "organic_matter_percent": 3.2}
        }
        
        crop_requirements = CropRequirements(
            crop_type="soybean",
            growth_stage="R1",
            nutrient_requirements={"nitrogen": 0.0}  # Soybeans fix their own N
        )
        
        rankings = await service.rank_method_effectiveness(
            CropType.SOYBEAN,
            [ApplicationMethodType.BROADCAST, ApplicationMethodType.BAND],
            field_conditions,
            crop_requirements
        )
        
        # Both methods should have lower nitrogen efficiency scores for soybeans
        for ranking in rankings:
            assert ranking.efficiency_score < 0.9  # Lower than corn due to N fixation
    
    @pytest.mark.asyncio
    async def test_wheat_broadcast_suitability(self, service):
        """Test that broadcast application is suitable for wheat."""
        field_conditions = {
            "weather": {"temperature_celsius": 15.0, "humidity_percent": 70.0},
            "soil": {"ph": 6.8, "organic_matter_percent": 2.8}
        }
        
        crop_requirements = CropRequirements(
            crop_type="wheat",
            growth_stage="tillering",
            nutrient_requirements={"nitrogen": 120.0}
        )
        
        rankings = await service.rank_method_effectiveness(
            CropType.WHEAT,
            [ApplicationMethodType.BROADCAST, ApplicationMethodType.BAND],
            field_conditions,
            crop_requirements
        )
        
        # Broadcast should be competitive for wheat
        broadcast_ranking = next(r for r in rankings if r.method_type == ApplicationMethodType.BROADCAST)
        assert broadcast_ranking.overall_score > 0.7  # Should be reasonably effective
    
    @pytest.mark.asyncio
    async def test_foliar_application_limitations(self, service):
        """Test that foliar application has appropriate limitations."""
        field_conditions = {
            "weather": {"temperature_celsius": 22.0, "humidity_percent": 65.0, "wind_speed_kmh": 20.0},
            "soil": {"ph": 6.5, "organic_matter_percent": 3.2}
        }
        
        crop_requirements = CropRequirements(
            crop_type="corn",
            growth_stage="V6",
            nutrient_requirements={"nitrogen": 150.0}
        )
        
        rankings = await service.rank_method_effectiveness(
            CropType.CORN,
            [ApplicationMethodType.FOLIAR, ApplicationMethodType.BAND],
            field_conditions,
            crop_requirements
        )
        
        foliar_ranking = next(r for r in rankings if r.method_type == ApplicationMethodType.FOLIAR)
        
        # Foliar should rank lower due to limitations
        assert foliar_ranking.overall_score < 0.8
        assert "Weather dependent" in foliar_ranking.limitations
        assert "Limited nutrient capacity" in foliar_ranking.limitations


class TestPerformanceRequirements:
    """Performance and reliability tests."""
    
    @pytest.fixture
    def service(self):
        return CropResponseService()
    
    @pytest.mark.asyncio
    async def test_response_time_requirement(self, service):
        """Test that response time is under 2 seconds."""
        import time
        
        field_conditions = {
            "weather": {"temperature_celsius": 22.0, "humidity_percent": 65.0},
            "soil": {"ph": 6.5, "organic_matter_percent": 3.2}
        }
        
        crop_requirements = CropRequirements(
            crop_type="corn",
            growth_stage="V6",
            nutrient_requirements={"nitrogen": 150.0}
        )
        
        start_time = time.time()
        
        rankings = await service.rank_method_effectiveness(
            CropType.CORN,
            [ApplicationMethodType.BROADCAST, ApplicationMethodType.BAND, ApplicationMethodType.SIDEDRESS],
            field_conditions,
            crop_requirements
        )
        
        elapsed = time.time() - start_time
        assert elapsed < 2.0, f"Response time {elapsed}s exceeds 2s requirement"
        assert len(rankings) == 3
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, service):
        """Test handling of concurrent requests."""
        field_conditions = {
            "weather": {"temperature_celsius": 22.0, "humidity_percent": 65.0},
            "soil": {"ph": 6.5, "organic_matter_percent": 3.2}
        }
        
        crop_requirements = CropRequirements(
            crop_type="corn",
            growth_stage="V6",
            nutrient_requirements={"nitrogen": 150.0}
        )
        
        # Create multiple concurrent requests
        tasks = []
        for i in range(5):
            task = service.rank_method_effectiveness(
                CropType.CORN,
                [ApplicationMethodType.BROADCAST, ApplicationMethodType.BAND],
                field_conditions,
                crop_requirements
            )
            tasks.append(task)
        
        # Execute all requests concurrently
        results = await asyncio.gather(*tasks)
        
        # All requests should complete successfully
        assert len(results) == 5
        for result in results:
            assert len(result) == 2
            assert all(isinstance(ranking, MethodEffectivenessRanking) for ranking in result)
    
    @pytest.mark.asyncio
    async def test_error_handling(self, service):
        """Test error handling for invalid inputs."""
        field_conditions = {
            "weather": {"temperature_celsius": 22.0, "humidity_percent": 65.0},
            "soil": {"ph": 6.5, "organic_matter_percent": 3.2}
        }
        
        crop_requirements = CropRequirements(
            crop_type="corn",
            growth_stage="V6",
            nutrient_requirements={"nitrogen": 150.0}
        )
        
        # Test with empty method list
        with pytest.raises(Exception):
            await service.rank_method_effectiveness(
                CropType.CORN,
                [],  # Empty list
                field_conditions,
                crop_requirements
            )
        
        # Test with invalid field conditions
        with pytest.raises(Exception):
            await service.rank_method_effectiveness(
                CropType.CORN,
                [ApplicationMethodType.BAND],
                {},  # Empty field conditions
                crop_requirements
            )