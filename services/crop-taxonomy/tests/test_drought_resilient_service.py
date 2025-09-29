"""
Tests for Drought-Resilient Crop Recommendation Service

Comprehensive test suite for drought-tolerant crop variety recommendations,
water use efficiency analysis, and drought risk assessment.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from uuid import uuid4
from typing import Dict, Any, List

from src.services.drought_resilient_crop_service import DroughtResilientCropService
from src.models.drought_resilient_models import (
    DroughtRecommendationRequest,
    DroughtRecommendationResponse,
    DroughtRiskAssessment,
    DroughtRiskLevel,
    DroughtToleranceLevel,
    WaterUseEfficiencyLevel,
    AlternativeCropRecommendation,
    DiversificationStrategy,
    WaterConservationPotential
)
from src.models.crop_variety_models import (
    EnhancedCropVariety,
    VarietyRecommendation,
    YieldPotential,
    DiseaseResistanceProfile,
    MarketAttributes
)


class TestDroughtResilientCropService:
    """Test suite for drought-resilient crop recommendation service."""

    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return DroughtResilientCropService()

    @pytest.fixture
    def sample_location(self):
        """Sample location data for testing."""
        return {
            "latitude": 40.0,
            "longitude": -95.0,
            "climate_zone": "humid_continental",
            "soil_type": "clay_loam",
            "irrigation_available": True,
            "region": "Midwest"
        }

    @pytest.fixture
    def sample_request(self, sample_location):
        """Sample drought recommendation request."""
        return DroughtRecommendationRequest(
            request_id=str(uuid4()),
            location=sample_location,
            crop_type="corn",
            drought_risk_level=DroughtRiskLevel.MODERATE,
            irrigation_available=True,
            include_alternative_crops=True,
            include_diversification_strategies=True,
            include_water_conservation_analysis=True
        )

    @pytest.fixture
    def sample_variety(self):
        """Sample crop variety for testing."""
        return EnhancedCropVariety(
            variety_id=uuid4(),
            variety_name="Drought-Tolerant Corn",
            variety_code="DT-Corn-2024",
            crop_id=uuid4(),
            relative_maturity=105,
            yield_potential_percentile=75,
            yield_stability_rating=8.0,
            stress_tolerances=["drought", "heat", "water_efficient"],
            disease_resistances=[
                DiseaseResistanceEntry(
                    disease_name="rust",
                    resistance_rating=4,
                    resistance_type="partial"
                )
            ],
            adapted_regions=["Midwest", "Great Plains"],
            market_attributes=MarketAttributes(
                market_class="feed_corn",
                end_use_suitability=["feed", "ethanol"],
                premium_potential=3.5
            )
        )

    @pytest.fixture
    def sample_variety_recommendation(self, sample_variety):
        """Sample variety recommendation for testing."""
        return VarietyRecommendation(
            variety=sample_variety,
            variety_id=sample_variety.variety_id,
            variety_name=sample_variety.variety_name,
            variety_code=sample_variety.variety_code,
            overall_score=0.8,
            suitability_factors={
                "yield_potential": 0.7,
                "disease_resistance": 0.8,
                "climate_adaptation": 0.6
            },
            individual_scores={
                "yield_potential": 0.7,
                "disease_resistance": 0.8,
                "climate_adaptation": 0.6
            },
            weighted_contributions={
                "yield_potential": 0.14,
                "disease_resistance": 0.16,
                "climate_adaptation": 0.12
            },
            score_details={
                "yield_potential": "Good yield potential",
                "disease_resistance": "Excellent disease resistance",
                "climate_adaptation": "Moderate climate adaptation"
            },
            confidence_level=0.8,
            data_quality_score=0.8
        )


class TestDroughtRiskAssessment:
    """Test drought risk assessment functionality."""

    @pytest.mark.asyncio
    async def test_assess_drought_risk_moderate(self, service, sample_location):
        """Test drought risk assessment for moderate risk location."""
        risk_assessment = await service._assess_drought_risk(sample_location, "moderate")
        
        assert isinstance(risk_assessment, DroughtRiskAssessment)
        assert risk_assessment.location == sample_location
        assert risk_assessment.overall_risk_level in ["low", "moderate", "high"]
        assert risk_assessment.confidence_score > 0.0
        assert len(risk_assessment.risk_factors) > 0

    @pytest.mark.asyncio
    async def test_assess_drought_risk_high(self, service, sample_location):
        """Test drought risk assessment for high risk location."""
        # Modify location to simulate high drought risk
        high_risk_location = sample_location.copy()
        high_risk_location["climate_zone"] = "arid"
        high_risk_location["irrigation_available"] = False
        
        risk_assessment = await service._assess_drought_risk(high_risk_location, "high")
        
        assert risk_assessment.overall_risk_level in ["moderate", "high", "severe"]
        assert risk_assessment.risk_factors["climate_zone_drought_tendency"] > 0.5

    @pytest.mark.asyncio
    async def test_calculate_location_risk_factors(self, service, sample_location):
        """Test calculation of location-specific risk factors."""
        risk_factors = await service._calculate_location_risk_factors(sample_location)
        
        assert isinstance(risk_factors, dict)
        assert "historical_drought_frequency" in risk_factors
        assert "soil_water_holding_capacity" in risk_factors
        assert "irrigation_availability" in risk_factors
        assert "climate_zone_drought_tendency" in risk_factors
        
        # All risk factors should be between 0 and 1
        for factor, value in risk_factors.items():
            assert 0.0 <= value <= 1.0

    def test_determine_overall_risk_level(self, service):
        """Test overall risk level determination."""
        # Test different risk factor combinations
        low_risk_factors = {"factor1": 0.2, "factor2": 0.3, "factor3": 0.1}
        moderate_risk_factors = {"factor1": 0.5, "factor2": 0.6, "factor3": 0.4}
        high_risk_factors = {"factor1": 0.8, "factor2": 0.7, "factor3": 0.9}
        
        assert service._determine_overall_risk_level("low", low_risk_factors) in ["very_low", "low"]
        assert service._determine_overall_risk_level("moderate", moderate_risk_factors) in ["low", "moderate"]
        assert service._determine_overall_risk_level("high", high_risk_factors) in ["moderate", "high"]


class TestDroughtScoring:
    """Test drought-specific scoring algorithms."""

    @pytest.mark.asyncio
    async def test_calculate_drought_resilience_score(self, service, sample_variety, sample_request):
        """Test drought resilience score calculation."""
        drought_risk = DroughtRiskAssessment(
            location=sample_request.location,
            overall_risk_level=DroughtRiskLevel.MODERATE,
            risk_factors={"drought_risk": 0.5},
            confidence_score=0.8
        )
        
        score = await service._calculate_drought_resilience_score(
            sample_variety, drought_risk, sample_request
        )
        
        assert 0.0 <= score <= 1.0
        assert isinstance(score, float)

    @pytest.mark.asyncio
    async def test_calculate_water_efficiency_score(self, service, sample_variety, sample_request):
        """Test water use efficiency score calculation."""
        drought_risk = DroughtRiskAssessment(
            location=sample_request.location,
            overall_risk_level=DroughtRiskLevel.MODERATE,
            risk_factors={"drought_risk": 0.5},
            confidence_score=0.8
        )
        
        score = await service._calculate_water_efficiency_score(
            sample_variety, drought_risk, sample_request
        )
        
        assert 0.0 <= score <= 1.0
        assert isinstance(score, float)

    @pytest.mark.asyncio
    async def test_calculate_stress_recovery_score(self, service, sample_variety, sample_request):
        """Test stress recovery score calculation."""
        drought_risk = DroughtRiskAssessment(
            location=sample_request.location,
            overall_risk_level=DroughtRiskLevel.MODERATE,
            risk_factors={"drought_risk": 0.5},
            confidence_score=0.8
        )
        
        score = await service._calculate_stress_recovery_score(
            sample_variety, drought_risk, sample_request
        )
        
        assert 0.0 <= score <= 1.0
        assert isinstance(score, float)

    def test_determine_drought_tolerance_level(self, service):
        """Test drought tolerance level determination."""
        assert service._determine_drought_tolerance_level(0.9) == "high"
        assert service._determine_drought_tolerance_level(0.7) == "moderate"
        assert service._determine_drought_tolerance_level(0.5) == "low"
        assert service._determine_drought_tolerance_level(0.2) == "poor"

    def test_risk_level_to_numeric(self, service):
        """Test risk level to numeric conversion."""
        assert service._risk_level_to_numeric("very_low") == 0.1
        assert service._risk_level_to_numeric("low") == 0.3
        assert service._risk_level_to_numeric("moderate") == 0.5
        assert service._risk_level_to_numeric("high") == 0.7
        assert service._risk_level_to_numeric("severe") == 0.9
        assert service._risk_level_to_numeric("unknown") == 0.5  # Default


class TestAlternativeCropRecommendations:
    """Test alternative crop recommendation functionality."""

    @pytest.mark.asyncio
    async def test_get_alternative_crop_recommendations(self, service, sample_request):
        """Test alternative crop recommendations."""
        drought_risk = DroughtRiskAssessment(
            location=sample_request.location,
            overall_risk_level=DroughtRiskLevel.MODERATE,
            risk_factors={"drought_risk": 0.5},
            confidence_score=0.8
        )
        
        alternative_crops = await service._get_alternative_crop_recommendations(
            sample_request, drought_risk
        )
        
        assert isinstance(alternative_crops, list)
        assert len(alternative_crops) > 0
        
        for crop in alternative_crops:
            assert isinstance(crop, AlternativeCropRecommendation)
            assert crop.crop_name is not None
            assert crop.scientific_name is not None
            assert crop.drought_tolerance_level is not None
            assert crop.water_use_efficiency is not None
            assert 0.0 <= crop.suitability_score <= 1.0

    def test_calculate_alternative_crop_suitability(self, service):
        """Test alternative crop suitability calculation."""
        drought_risk = DroughtRiskAssessment(
            location={"latitude": 40.0, "longitude": -95.0},
            overall_risk_level=DroughtRiskLevel.MODERATE,
            risk_factors={"drought_risk": 0.5},
            confidence_score=0.8
        )
        
        crop_data = {
            "drought_tolerance": "high",
            "water_use_efficiency": "very_high",
            "market_demand": "moderate",
            "management_complexity": "low"
        }
        
        suitability = service._calculate_alternative_crop_suitability(
            crop_data, drought_risk, None
        )
        
        assert 0.0 <= suitability <= 1.0
        assert isinstance(suitability, float)

    def test_get_alternative_crop_advantages(self, service):
        """Test alternative crop advantages generation."""
        crop_data = {
            "drought_tolerance": "very_high",
            "water_use_efficiency": "high",
            "management_complexity": "low",
            "market_demand": "high"
        }
        
        advantages = service._get_alternative_crop_advantages(crop_data)
        
        assert isinstance(advantages, list)
        assert len(advantages) > 0
        assert "Excellent drought tolerance" in advantages
        assert "High water use efficiency" in advantages

    def test_get_alternative_crop_considerations(self, service):
        """Test alternative crop considerations generation."""
        crop_data = {
            "yield_potential": "low",
            "market_demand": "low",
            "management_complexity": "high"
        }
        
        considerations = service._get_alternative_crop_considerations(crop_data)
        
        assert isinstance(considerations, list)
        assert "Lower yield potential compared to traditional crops" in considerations

    def test_get_transition_requirements(self, service):
        """Test transition requirements generation."""
        crop_data = {"management_complexity": "high"}
        
        requirements = service._get_transition_requirements(crop_data)
        
        assert isinstance(requirements, list)
        assert len(requirements) > 0
        assert "Evaluate equipment compatibility" in requirements
        assert "Assess market access and contracts" in requirements


class TestDiversificationStrategies:
    """Test diversification strategy functionality."""

    @pytest.mark.asyncio
    async def test_generate_diversification_strategies(self, service, sample_request):
        """Test diversification strategy generation."""
        drought_risk = DroughtRiskAssessment(
            location=sample_request.location,
            overall_risk_level=DroughtRiskLevel.MODERATE,
            risk_factors={"drought_risk": 0.5},
            confidence_score=0.8
        )
        
        strategies = await service._generate_diversification_strategies(
            sample_request, drought_risk
        )
        
        assert isinstance(strategies, list)
        assert len(strategies) > 0
        
        for strategy in strategies:
            assert isinstance(strategy, DiversificationStrategy)
            assert strategy.strategy_type is not None
            assert strategy.description is not None
            assert len(strategy.implementation_steps) > 0
            assert len(strategy.expected_benefits) > 0
            assert 0.0 <= strategy.risk_reduction_potential <= 1.0


class TestWaterConservationAnalysis:
    """Test water conservation analysis functionality."""

    @pytest.mark.asyncio
    async def test_calculate_water_conservation_potential(self, service, sample_request):
        """Test water conservation potential calculation."""
        # Create sample recommendations
        sample_recommendations = [
            VarietyRecommendation(
                variety=None,
                variety_id=uuid4(),
                variety_name="Test Variety",
                variety_code="TEST-001",
                overall_score=0.8,
                suitability_factors={"water_efficiency_score": 0.7},
                individual_scores={},
                weighted_contributions={},
                score_details={},
                confidence_level=0.8,
                data_quality_score=0.8
            )
        ]
        
        sample_alternative_crops = [
            AlternativeCropRecommendation(
                crop_name="Sorghum",
                scientific_name="Sorghum bicolor",
                drought_tolerance_level=DroughtToleranceLevel.HIGH,
                water_use_efficiency=WaterUseEfficiencyLevel.VERY_HIGH,
                yield_potential="moderate",
                market_demand="moderate",
                management_complexity="low",
                suitability_score=0.8,
                advantages=[],
                considerations=[],
                transition_requirements=[]
            )
        ]
        
        water_conservation = await service._calculate_water_conservation_potential(
            sample_recommendations, sample_alternative_crops, sample_request
        )
        
        assert isinstance(water_conservation, WaterConservationPotential)
        assert water_conservation.variety_based_savings >= 0.0
        assert water_conservation.alternative_crop_savings >= 0.0
        assert water_conservation.total_potential_savings >= 0.0
        assert 0.0 <= water_conservation.savings_percentage <= 100.0

    def test_efficiency_to_numeric(self, service):
        """Test efficiency string to numeric conversion."""
        assert service._efficiency_to_numeric("very_high") == 0.9
        assert service._efficiency_to_numeric("high") == 0.7
        assert service._efficiency_to_numeric("moderate") == 0.5
        assert service._efficiency_to_numeric("low") == 0.3
        assert service._efficiency_to_numeric("very_low") == 0.1
        assert service._efficiency_to_numeric("unknown") == 0.5  # Default

    def test_calculate_savings_percentage(self, service):
        """Test water savings percentage calculation."""
        # Test with different savings amounts
        assert service._calculate_savings_percentage(50.0) == 10.0  # 50/500 * 100
        assert service._calculate_savings_percentage(250.0) == 50.0  # Capped at 50%
        assert service._calculate_savings_percentage(0.0) == 0.0

    def test_calculate_cost_benefit_ratio(self, service):
        """Test cost-benefit ratio calculation."""
        # Test with positive savings
        ratio = service._calculate_cost_benefit_ratio(100.0)
        assert ratio == 0.5  # 100 * 0.50 / 100
        
        # Test with zero savings
        ratio_zero = service._calculate_cost_benefit_ratio(0.0)
        assert ratio_zero == 0.0


class TestDroughtManagementPractices:
    """Test drought management practice functionality."""

    @pytest.mark.asyncio
    async def test_generate_drought_management_practices(self, service, sample_variety, sample_request):
        """Test drought management practice generation."""
        drought_risk = DroughtRiskAssessment(
            location=sample_request.location,
            overall_risk_level=DroughtRiskLevel.MODERATE,
            risk_factors={"drought_risk": 0.5},
            confidence_score=0.8
        )
        
        practices = await service._generate_drought_management_practices(
            sample_variety, drought_risk, sample_request
        )
        
        assert isinstance(practices, list)
        assert len(practices) > 0
        
        # Check for common drought management practices
        practice_text = " ".join(practices).lower()
        assert "conservation" in practice_text or "moisture" in practice_text
        assert "monitor" in practice_text or "irrigation" in practice_text

    @pytest.mark.asyncio
    async def test_calculate_drought_economics(self, service, sample_variety, sample_request):
        """Test drought economics calculation."""
        drought_risk = DroughtRiskAssessment(
            location=sample_request.location,
            overall_risk_level=DroughtRiskLevel.MODERATE,
            risk_factors={"drought_risk": 0.5},
            confidence_score=0.8
        )
        
        economics = await service._calculate_drought_economics(
            sample_variety, drought_risk, sample_request
        )
        
        assert isinstance(economics, dict)
        assert "drought_premium" in economics
        assert "water_cost_savings" in economics
        assert "risk_adjustment" in economics
        assert "insurance_considerations" in economics
        
        assert economics["drought_premium"] >= 0.0
        assert economics["water_cost_savings"] >= 0.0


class TestMainRecommendationFlow:
    """Test main recommendation flow integration."""

    @pytest.mark.asyncio
    async def test_get_drought_resilient_recommendations_success(self, service, sample_request):
        """Test successful drought-resilient recommendation generation."""
        with patch.object(service, '_get_base_drought_recommendations') as mock_base:
            with patch.object(service, '_get_alternative_crop_recommendations') as mock_alt:
                with patch.object(service, '_generate_diversification_strategies') as mock_div:
                    with patch.object(service, '_calculate_water_conservation_potential') as mock_water:
                        # Mock the methods to return sample data
                        mock_base.return_value = []
                        mock_alt.return_value = []
                        mock_div.return_value = []
                        mock_water.return_value = WaterConservationPotential(
                            variety_based_savings=50.0,
                            alternative_crop_savings=75.0,
                            total_potential_savings=125.0,
                            savings_percentage=25.0,
                            implementation_timeline="1-3 years",
                            cost_benefit_ratio=0.5
                        )
                        
                        response = await service.get_drought_resilient_recommendations(sample_request)
                        
                        assert isinstance(response, DroughtRecommendationResponse)
                        assert response.request_id == sample_request.request_id
                        assert response.location == sample_request.location
                        assert response.confidence_score > 0.0
                        assert response.generated_at is not None

    @pytest.mark.asyncio
    async def test_get_drought_resilient_recommendations_error(self, service, sample_request):
        """Test error handling in drought-resilient recommendation generation."""
        with patch.object(service, '_assess_drought_risk', side_effect=Exception("Test error")):
            response = await service.get_drought_resilient_recommendations(sample_request)
            
            assert isinstance(response, DroughtRecommendationResponse)
            assert response.error_message is not None
            assert "Test error" in response.error_message

    def test_calculate_overall_confidence(self, service):
        """Test overall confidence calculation."""
        sample_recommendations = [
            VarietyRecommendation(
                variety=None,
                variety_id=uuid4(),
                variety_name="Test Variety",
                variety_code="TEST-001",
                overall_score=0.8,
                suitability_factors={},
                individual_scores={},
                weighted_contributions={},
                score_details={},
                confidence_level=0.8,
                data_quality_score=0.8
            )
        ]
        
        sample_alternative_crops = [
            AlternativeCropRecommendation(
                crop_name="Sorghum",
                scientific_name="Sorghum bicolor",
                drought_tolerance_level=DroughtToleranceLevel.HIGH,
                water_use_efficiency=WaterUseEfficiencyLevel.VERY_HIGH,
                yield_potential="moderate",
                market_demand="moderate",
                management_complexity="low",
                suitability_score=0.8,
                advantages=[],
                considerations=[],
                transition_requirements=[]
            )
        ]
        
        drought_risk = DroughtRiskAssessment(
            location={"latitude": 40.0, "longitude": -95.0},
            overall_risk_level=DroughtRiskLevel.MODERATE,
            risk_factors={"drought_risk": 0.5},
            confidence_score=0.8
        )
        
        confidence = service._calculate_overall_confidence(
            sample_recommendations, sample_alternative_crops, drought_risk
        )
        
        assert 0.0 <= confidence <= 1.0
        assert isinstance(confidence, float)


class TestServiceInitialization:
    """Test service initialization and configuration."""

    def test_service_initialization(self):
        """Test service initialization."""
        service = DroughtResilientCropService()
        
        assert service is not None
        assert hasattr(service, 'variety_service')
        assert hasattr(service, 'confidence_service')
        assert hasattr(service, 'drought_scoring_weights')
        assert hasattr(service, 'drought_tolerance_thresholds')
        assert hasattr(service, 'water_efficiency_categories')

    def test_drought_scoring_weights(self):
        """Test drought scoring weights configuration."""
        service = DroughtResilientCropService()
        
        weights = service.drought_scoring_weights
        
        assert "drought_tolerance" in weights
        assert "water_use_efficiency" in weights
        assert "root_depth_adaptation" in weights
        assert "stress_recovery" in weights
        assert "yield_stability" in weights
        
        # Check that weights sum to approximately 1.0
        total_weight = sum(weights.values())
        assert 0.9 <= total_weight <= 1.1

    def test_drought_tolerance_thresholds(self):
        """Test drought tolerance thresholds configuration."""
        service = DroughtResilientCropService()
        
        thresholds = service.drought_tolerance_thresholds
        
        assert "high" in thresholds
        assert "moderate" in thresholds
        assert "low" in thresholds
        assert "poor" in thresholds
        
        # Check that thresholds are in ascending order
        threshold_values = list(thresholds.values())
        assert threshold_values == sorted(threshold_values)

    def test_water_efficiency_categories(self):
        """Test water efficiency categories configuration."""
        service = DroughtResilientCropService()
        
        categories = service.water_efficiency_categories
        
        assert "very_high" in categories
        assert "high" in categories
        assert "moderate" in categories
        assert "low" in categories
        assert "very_low" in categories
        
        # Check that categories are in descending order
        category_values = list(categories.values())
        assert category_values == sorted(category_values, reverse=True)


# Agricultural validation tests
class TestAgriculturalValidation:
    """Agricultural validation tests for drought recommendations."""

    @pytest.mark.asyncio
    async def test_corn_belt_drought_recommendations(self, service):
        """Test drought recommendations for corn belt region."""
        corn_belt_location = {
            "latitude": 41.0,
            "longitude": -94.0,
            "climate_zone": "humid_continental",
            "soil_type": "loam",
            "irrigation_available": False,
            "region": "Corn Belt"
        }
        
        request = DroughtRecommendationRequest(
            request_id=str(uuid4()),
            location=corn_belt_location,
            crop_type="corn",
            drought_risk_level=DroughtRiskLevel.MODERATE
        )
        
        response = await service.get_drought_resilient_recommendations(request)
        
        assert response.drought_risk_assessment.overall_risk_level in ["low", "moderate", "high"]
        assert len(response.recommended_varieties) >= 0
        assert len(response.alternative_crops) >= 0

    @pytest.mark.asyncio
    async def test_southwest_drought_recommendations(self, service):
        """Test drought recommendations for southwest region."""
        southwest_location = {
            "latitude": 33.0,
            "longitude": -112.0,
            "climate_zone": "arid",
            "soil_type": "sandy_loam",
            "irrigation_available": True,
            "region": "Southwest"
        }
        
        request = DroughtRecommendationRequest(
            request_id=str(uuid4()),
            location=southwest_location,
            drought_risk_level=DroughtRiskLevel.HIGH
        )
        
        response = await service.get_drought_resilient_recommendations(request)
        
        assert response.drought_risk_assessment.overall_risk_level in ["moderate", "high", "severe"]
        assert len(response.alternative_crops) > 0
        
        # Check that alternative crops are drought-tolerant
        for crop in response.alternative_crops:
            assert crop.drought_tolerance_level in ["moderate", "high", "very_high"]

    @pytest.mark.asyncio
    async def test_water_efficiency_validation(self, service, sample_request):
        """Test water efficiency validation for recommendations."""
        response = await service.get_drought_resilient_recommendations(sample_request)
        
        if response.water_conservation_potential:
            assert response.water_conservation_potential.total_potential_savings >= 0.0
            assert 0.0 <= response.water_conservation_potential.savings_percentage <= 100.0
            
            # Water savings should be reasonable (not exceeding 100% of baseline)
            assert response.water_conservation_potential.savings_percentage <= 50.0

    @pytest.mark.asyncio
    async def test_drought_tolerance_validation(self, service, sample_request):
        """Test drought tolerance validation for recommendations."""
        response = await service.get_drought_resilient_recommendations(sample_request)
        
        # Check that recommended varieties have drought-related characteristics
        for variety_rec in response.recommended_varieties:
            if hasattr(variety_rec, 'suitability_factors'):
                drought_score = variety_rec.suitability_factors.get('drought_resilience_score', 0.0)
                assert 0.0 <= drought_score <= 1.0
                
                water_efficiency = variety_rec.suitability_factors.get('water_efficiency_score', 0.0)
                assert 0.0 <= water_efficiency <= 1.0


# Performance tests
class TestPerformance:
    """Performance tests for drought recommendation service."""

    @pytest.mark.asyncio
    async def test_recommendation_response_time(self, service, sample_request):
        """Test that recommendations are generated within acceptable time."""
        import time
        
        start_time = time.time()
        response = await service.get_drought_resilient_recommendations(sample_request)
        elapsed_time = time.time() - start_time
        
        # Should complete within 5 seconds
        assert elapsed_time < 5.0
        assert response.generated_at is not None

    @pytest.mark.asyncio
    async def test_concurrent_recommendations(self, service, sample_location):
        """Test concurrent recommendation generation."""
        requests = []
        for i in range(5):
            request = DroughtRecommendationRequest(
                request_id=str(uuid4()),
                location=sample_location,
                crop_type="corn"
            )
            requests.append(request)
        
        # Generate recommendations concurrently
        tasks = [
            service.get_drought_resilient_recommendations(req) 
            for req in requests
        ]
        
        responses = await asyncio.gather(*tasks)
        
        assert len(responses) == 5
        for response in responses:
            assert isinstance(response, DroughtRecommendationResponse)
            assert response.generated_at is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])