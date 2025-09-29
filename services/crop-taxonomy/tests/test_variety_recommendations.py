"""
Comprehensive Variety Recommendation Testing Suite

This test suite provides extensive testing for the variety recommendation system including:
- Unit tests for all recommendation components
- Integration tests with external services
- Performance testing with concurrent users
- Agricultural scenario validation
- Test data with 1000+ varieties and diverse scenarios

Test Coverage Areas:
- Variety scoring and ranking algorithms
- Regional adaptation analysis
- Market intelligence integration
- Economic viability assessment
- Seed company integration
- Confidence calculation
- Risk assessment
- Performance prediction
- Agricultural validation scenarios
"""

import pytest
import asyncio
import time
import statistics
from unittest.mock import AsyncMock, patch, MagicMock, Mock
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
import concurrent.futures
import threading
import random

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.variety_recommendation_service import VarietyRecommendationService
from models.crop_variety_models import (
    EnhancedCropVariety,
    VarietyRecommendation,
    VarietyComparisonRequest,
    VarietyComparisonResponse,
    RegionalPerformanceEntry,
    QualityCharacteristic,
    RiskLevel,
    SeedAvailabilityStatus,
    SeedCompanyOffering,
    DiseaseResistanceEntry,
    PestResistanceEntry
)
from models.suitability_models import AdaptationStrategy
from models.crop_taxonomy_models import (
    ComprehensiveCropData,
    CropCategory,
    CropAgriculturalClassification
)
from models.service_models import ConfidenceLevel


@pytest.fixture
def service():
    """Create service instance for testing."""
    return VarietyRecommendationService()

@pytest.fixture
def mock_crop_data():
    """Create mock crop data for testing."""
    from models.crop_taxonomy_models import PrimaryUse, GrowthHabit, PlantType
    
    return ComprehensiveCropData(
        crop_id=uuid4(),
        crop_name="Wheat",
        agricultural_classification=CropAgriculturalClassification(
            crop_category=CropCategory.GRAIN,
            primary_use=PrimaryUse.FOOD_HUMAN,
            growth_habit=GrowthHabit.ANNUAL,
            plant_type=PlantType.GRASS
        )
    )

@pytest.fixture
def mock_regional_context():
    """Create mock regional context for testing."""
    return {
        "region": "Great Plains",
        "climate_zone": "5a",
        "soil_type": "clay_loam",
        "regional_yield_modifier": 0.1,
        "climate_risks": {
            "drought_risk": 0.3,
            "heat_risk": 0.2,
            "disease_pressure": 0.4
        },
        "market_preferences": ["hard_red_winter", "high_protein"],
        "regions": ["US", "Great Plains"]
    }

@pytest.fixture
def mock_farmer_preferences():
    """Create mock farmer preferences for testing."""
    return {
        "primary_goals": ["yield_maximization", "disease_resistance"],
        "risk_tolerance": "moderate",
        "quality_priorities": {
            "protein_content": "high",
            "test_weight": "good"
        },
        "management_preferences": {
            "input_intensity": "moderate",
            "technology_adoption": "high"
        }
    }

@pytest.fixture
def sample_varieties():
    """Create sample varieties for testing."""
    varieties = []
    
    # High yield variety
    varieties.append(EnhancedCropVariety(
        variety_id=uuid4(),
        crop_id=uuid4(),
        variety_name="High Yield Wheat",
        variety_code="HYW-2024",
        breeder_company="University Research Station",
        relative_maturity=120,
        maturity_group="medium",
        yield_potential_percentile=85,
        yield_stability_rating=4.2,
        market_acceptance_score=3.2,
        standability_rating=8,
        disease_resistances=[
            DiseaseResistanceEntry(
                disease_name="stripe_rust",
                resistance_level="tolerant"
            ),
            DiseaseResistanceEntry(
                disease_name="leaf_rust",
                resistance_level="resistant"
            )
        ],
        pest_resistances=[
            PestResistanceEntry(
                pest_name="aphids",
                resistance_level="tolerant"
            )
        ],
        quality_characteristics=[
            QualityCharacteristic(
                characteristic_name="protein_content",
                value="11.5-14.2%",
                market_significance="high"
            )
        ],
        adapted_regions=["Great Plains", "Midwest"],
        seed_availability_status=SeedAvailabilityStatus.IN_STOCK
    ))
    
    # Disease resistant variety
    varieties.append(EnhancedCropVariety(
        variety_id=uuid4(),
        crop_id=uuid4(),
        variety_name="Disease Resistant Wheat",
        variety_code="DRW-Elite",
        breeder_company="Agricultural Research Center",
        relative_maturity=115,
        maturity_group="medium",
        yield_potential_percentile=75,
        yield_stability_rating=4.7,
        market_acceptance_score=4.0,
        standability_rating=9,
        disease_resistances=[
            DiseaseResistanceEntry(
                disease_name="stripe_rust",
                resistance_level="immune"
            ),
            DiseaseResistanceEntry(
                disease_name="leaf_rust",
                resistance_level="immune"
            ),
            DiseaseResistanceEntry(
                disease_name="powdery_mildew",
                resistance_level="immune"
            )
        ],
        pest_resistances=[
            PestResistanceEntry(
                pest_name="aphids",
                resistance_level="resistant"
            )
        ],
        quality_characteristics=[
            QualityCharacteristic(
                characteristic_name="protein_content",
                value="12.0-14.5%",
                market_significance="high"
            )
        ],
        adapted_regions=["Great Plains", "Midwest", "Northeast"],
        seed_availability_status=SeedAvailabilityStatus.IN_STOCK
    ))
    
    # Premium quality variety
    varieties.append(EnhancedCropVariety(
        variety_id=uuid4(),
        crop_id=uuid4(),
        variety_name="Premium Quality Wheat",
        variety_code="PQW-Premium",
        breeder_company="Premium Seed Company",
        relative_maturity=125,
        maturity_group="medium-late",
        yield_potential_percentile=70,
        yield_stability_rating=4.5,
        market_acceptance_score=4.5,
        standability_rating=7,
        disease_resistances=[
            DiseaseResistanceEntry(
                disease_name="stripe_rust",
                resistance_level="resistant"
            ),
            DiseaseResistanceEntry(
                disease_name="leaf_rust",
                resistance_level="resistant"
            ),
            DiseaseResistanceEntry(
                disease_name="powdery_mildew",
                resistance_level="resistant"
            )
        ],
        pest_resistances=[
            PestResistanceEntry(
                pest_name="aphids",
                resistance_level="tolerant"
            )
        ],
        quality_characteristics=[
            QualityCharacteristic(
                characteristic_name="protein_content",
                value="13.0-15.5%",
                market_significance="very_high"
            ),
            QualityCharacteristic(
                characteristic_name="test_weight",
                value="80-86 lb/bu",
                market_significance="high"
            )
        ],
        adapted_regions=["Pacific Northwest", "Northeast"],
        seed_availability_status=SeedAvailabilityStatus.LIMITED
    ))
    
    return varieties


class TestVarietyRecommendationService:
    """Comprehensive test suite for VarietyRecommendationService."""
    
    
    @pytest.fixture
    def large_variety_dataset(self):
        """Create large dataset of varieties for performance testing."""
        varieties = []
        
        # Generate 1000+ varieties with diverse characteristics
        for i in range(1000):
            variety = EnhancedCropVariety(
                variety_id=uuid4(),
                crop_id=uuid4(),
                variety_name=f"Test Variety {i:04d}",
                variety_code=f"TV{i:04d}-2024",
                breeder_company=f"Research Station {i % 10}",
                relative_maturity=random.randint(100, 140),
                maturity_group=random.choice(["early", "medium", "late"]),
                yield_potential_percentile=random.randint(50, 95),
                yield_stability_rating=3.0 + random.random() * 2.0,
                market_acceptance_score=2.0 + random.random() * 3.0,
                standability_rating=random.randint(5, 10),
                disease_resistances=[
                    DiseaseResistanceEntry(
                        disease_name="stripe_rust",
                        resistance_level=random.choice(["immune", "resistant", "tolerant", "susceptible"])
                    ),
                    DiseaseResistanceEntry(
                        disease_name="leaf_rust",
                        resistance_level=random.choice(["immune", "resistant", "tolerant", "susceptible"])
                    )
                ],
                pest_resistances=[
                    PestResistanceEntry(
                        pest_name="aphids",
                        resistance_level=random.choice(["immune", "resistant", "tolerant", "susceptible"])
                    )
                ],
                quality_characteristics=[
                    QualityCharacteristic(
                        characteristic_name="protein_content",
                        value=f"{10.0 + random.random() * 5.0:.1f}-{12.0 + random.random() * 5.0:.1f}%",
                        market_significance=random.choice(["low", "medium", "high", "very_high"])
                    )
                ],
                adapted_regions=random.sample(["Great Plains", "Midwest", "Northeast", "Pacific Northwest", "Southern Plains"], 2),
                seed_availability_status=random.choice(list(SeedAvailabilityStatus))
            )
            varieties.append(variety)
        
        return varieties


class TestVarietyRecommendationCore:
    """Test core variety recommendation functionality."""
    
    def test_sample_varieties_fixture(self, sample_varieties):
        """Test that the sample varieties fixture works correctly."""
        assert isinstance(sample_varieties, list)
        assert len(sample_varieties) == 3
        
        for variety in sample_varieties:
            assert isinstance(variety, EnhancedCropVariety)
            assert variety.variety_name is not None
            assert variety.variety_id is not None
            assert variety.crop_id is not None
            assert variety.breeder_company is not None
            assert variety.relative_maturity is not None
            assert variety.maturity_group is not None
            assert variety.yield_potential_percentile is not None
            assert variety.yield_stability_rating is not None
            assert variety.market_acceptance_score is not None
            assert variety.standability_rating is not None
            assert variety.disease_resistances is not None
            assert variety.pest_resistances is not None
            assert variety.quality_characteristics is not None
            assert variety.adapted_regions is not None
            assert variety.seed_availability_status is not None
    
    def test_mock_crop_data_fixture(self, mock_crop_data):
        """Test that the mock crop data fixture works correctly."""
        assert isinstance(mock_crop_data, ComprehensiveCropData)
        assert mock_crop_data.crop_id is not None
        assert mock_crop_data.crop_name == "Wheat"
        assert mock_crop_data.agricultural_classification is not None
        assert mock_crop_data.agricultural_classification.crop_category == CropCategory.GRAIN
    
    def test_mock_regional_context_fixture(self, mock_regional_context):
        """Test that the mock regional context fixture works correctly."""
        assert isinstance(mock_regional_context, dict)
        assert "region" in mock_regional_context
        assert "climate_zone" in mock_regional_context
        assert "soil_type" in mock_regional_context
        assert "regional_yield_modifier" in mock_regional_context
        assert "climate_risks" in mock_regional_context
        assert "market_preferences" in mock_regional_context
        assert "regions" in mock_regional_context
    
    def test_mock_farmer_preferences_fixture(self, mock_farmer_preferences):
        """Test that the mock farmer preferences fixture works correctly."""
        assert isinstance(mock_farmer_preferences, dict)
        assert "primary_goals" in mock_farmer_preferences
        assert "risk_tolerance" in mock_farmer_preferences
        assert "quality_priorities" in mock_farmer_preferences
        assert "management_preferences" in mock_farmer_preferences
    
    @pytest.mark.asyncio
    async def test_recommend_varieties_with_preferences(self, service, mock_crop_data, mock_regional_context, mock_farmer_preferences):
        """Test variety recommendations with farmer preferences."""
        recommendations = await service.recommend_varieties(
            mock_crop_data,
            mock_regional_context,
            mock_farmer_preferences
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Check that preferences influenced scoring
        for rec in recommendations:
            assert rec.individual_scores is not None
            assert "yield_potential" in rec.individual_scores
            assert "disease_resistance" in rec.individual_scores
    
    @pytest.mark.asyncio
    async def test_variety_scoring_components(self, service, sample_varieties, mock_regional_context):
        """Test individual scoring components."""
        variety = sample_varieties[0]
        
        # Test yield potential scoring
        yield_score = await service._score_yield_potential(variety, mock_regional_context)
        assert 0.0 <= yield_score <= 1.0
        
        # Test disease resistance scoring
        disease_score = await service._score_disease_resistance(variety, mock_regional_context)
        assert 0.0 <= disease_score <= 1.0
        
        # Test climate adaptation scoring
        climate_score = await service._score_climate_adaptation(variety, mock_regional_context)
        assert 0.0 <= climate_score <= 1.0
        
        # Test market desirability scoring
        market_score = await service._score_market_desirability(variety, mock_regional_context)
        assert 0.0 <= market_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_economic_viability_scoring(self, service, sample_varieties, mock_regional_context, mock_farmer_preferences):
        """Test economic viability scoring with market intelligence integration."""
        variety = sample_varieties[0]
        
        # Mock economic analysis service
        with patch.object(service, 'economic_analysis_service') as mock_econ:
            mock_econ.analyze_variety_economics = AsyncMock(return_value=Mock(
                economic_viability_score=0.85
            ))
            
            economic_score = await service._score_economic_viability(
                variety, mock_regional_context, mock_farmer_preferences
            )
            
            assert 0.0 <= economic_score <= 1.0
            assert economic_score == 0.85
    
    @pytest.mark.asyncio
    async def test_confidence_calculation(self, service, sample_varieties, mock_regional_context):
        """Test confidence calculation for recommendations."""
        variety = sample_varieties[0]
        
        # Create mock score data
        score_data = {
            "individual_scores": {
                "yield_potential": 0.8,
                "disease_resistance": 0.7,
                "climate_adaptation": 0.6,
                "market_desirability": 0.75
            },
            "overall_score": 0.75,
            "weighted_contributions": {
                "yield_potential": 0.16,
                "disease_resistance": 0.126,
                "climate_adaptation": 0.09,
                "market_desirability": 0.09
            }
        }
        
        # Mock performance prediction and risk assessment
        performance_prediction = {
            "predicted_yield_range": (5.0, 7.0),
            "yield_confidence": 0.8
        }
        
        risk_assessment = {
            "overall_risk_level": "MODERATE",
            "specific_risks": []
        }
        
        confidence_assessment = service.confidence_service.calculate(
            variety=variety,
            score_data=score_data,
            regional_context=mock_regional_context,
            performance_prediction=performance_prediction,
            risk_assessment=risk_assessment
        )
        
        assert confidence_assessment.overall_confidence is not None
        assert 0.0 <= confidence_assessment.overall_confidence <= 1.0
        assert confidence_assessment.data_quality_score is not None


class TestVarietyComparison:
    """Test variety comparison functionality."""
    
    @pytest.mark.asyncio
    async def test_variety_comparison_basic(self, service, sample_varieties):
        """Test basic variety comparison functionality."""
        variety_ids = [str(v.id) for v in sample_varieties[:2]]
        
        comparison_request = VarietyComparisonRequest(
            variety_ids=variety_ids,
            comparison_criteria=["yield_potential", "disease_resistance", "market_desirability"],
            include_economic_analysis=True,
            include_risk_assessment=True
        )
        
        # Mock the variety retrieval
        with patch.object(service, '_get_variety_by_id') as mock_get_variety:
            mock_get_variety.side_effect = sample_varieties[:2]
            
            comparison_response = await service.compare_varieties(comparison_request)
            
            assert isinstance(comparison_response, VarietyComparisonResponse)
            assert comparison_response.success is True
            assert len(comparison_response.comparisons) > 0
    
    @pytest.mark.asyncio
    async def test_variety_comparison_detailed(self, service, sample_varieties):
        """Test detailed variety comparison with all criteria."""
        variety_ids = [str(v.id) for v in sample_varieties]
        
        comparison_request = VarietyComparisonRequest(
            variety_ids=variety_ids,
            comparison_criteria=[
                "yield_potential", "disease_resistance", "climate_adaptation",
                "market_desirability", "economic_viability", "quality_attributes"
            ],
            include_economic_analysis=True,
            include_risk_assessment=True,
            include_performance_prediction=True
        )
        
        with patch.object(service, '_get_variety_by_id') as mock_get_variety:
            mock_get_variety.side_effect = sample_varieties
            
            comparison_response = await service.compare_varieties(comparison_request)
            
            assert comparison_response.success is True
            assert len(comparison_response.comparisons) >= 3  # At least 3 pairwise comparisons
            assert comparison_response.comparison_summary is not None


class TestSeedCompanyIntegration:
    """Test seed company integration functionality."""
    
    @pytest.mark.asyncio
    async def test_variety_availability_info(self, service):
        """Test variety availability information retrieval."""
        variety_name = "Test Wheat Variety"
        
        # Mock seed company service
        mock_offerings = [
            SeedCompanyOffering(
                company_name="Test Seed Co",
                product_code="TSC-001",
                availability_status=SeedAvailabilityStatus.IN_STOCK,
                distribution_regions=["Great Plains", "Midwest"],
                price_per_unit=45.50,
                price_unit="bag",
                last_updated=datetime.now(),
                notes="Limited quantity available"
            ),
            SeedCompanyOffering(
                company_name="Premium Seeds Inc",
                product_code="PSI-2024",
                availability_status=SeedAvailabilityStatus.LIMITED,
                distribution_regions=["Great Plains"],
                price_per_unit=52.75,
                price_unit="bag",
                last_updated=datetime.now(),
                notes="Premium quality seed"
            )
        ]
        
        with patch.object(service, 'seed_company_service') as mock_seed_service:
            mock_seed_service.get_variety_availability = AsyncMock(return_value=mock_offerings)
            
            availability_info = await service.get_variety_availability_info(variety_name)
            
            assert availability_info["variety_name"] == variety_name
            assert availability_info["total_companies"] == 2
            assert len(availability_info["companies"]) == 2
            assert availability_info["availability_summary"]["in_stock"] == 1
            assert availability_info["availability_summary"]["limited"] == 1
            assert availability_info["price_range"]["min"] == 45.50
            assert availability_info["price_range"]["max"] == 52.75
    
    @pytest.mark.asyncio
    async def test_seed_company_sync(self, service):
        """Test seed company data synchronization."""
        mock_sync_results = {
            "companies_synced": 5,
            "varieties_updated": 150,
            "errors": [],
            "sync_duration_seconds": 45.2
        }
        
        with patch.object(service, 'seed_company_service') as mock_seed_service:
            mock_seed_service.sync_all_companies = AsyncMock(return_value=mock_sync_results)
            
            sync_result = await service.sync_seed_company_data()
            
            assert sync_result["sync_completed"] is True
            assert sync_result["results"]["companies_synced"] == 5
            assert sync_result["results"]["varieties_updated"] == 150
    
    @pytest.mark.asyncio
    async def test_seed_company_sync_status(self, service):
        """Test seed company synchronization status."""
        mock_status = {
            "last_sync": "2024-01-15T10:30:00Z",
            "companies": [
                {"name": "Test Seed Co", "status": "synced", "last_update": "2024-01-15T10:25:00Z"},
                {"name": "Premium Seeds Inc", "status": "syncing", "last_update": "2024-01-15T10:28:00Z"}
            ],
            "overall_status": "partial"
        }
        
        with patch.object(service, 'seed_company_service') as mock_seed_service:
            mock_seed_service.get_company_sync_status = AsyncMock(return_value=mock_status)
            
            status_info = await service.get_seed_company_sync_status()
            
            assert status_info["overall_status"] == "partial"
            assert len(status_info["companies"]) == 2


class TestMarketIntelligenceIntegration:
    """Test market intelligence integration."""
    
    @pytest.mark.asyncio
    async def test_market_desirability_with_intelligence(self, service, sample_varieties, mock_regional_context):
        """Test market desirability scoring with market intelligence."""
        variety = sample_varieties[0]
        
        # Mock market intelligence service
        mock_market_report = Mock()
        mock_market_report.market_trends = Mock()
        mock_market_report.market_trends.trend_direction = 'up'
        mock_market_report.market_trends.trend_strength = 'moderate'
        mock_market_report.premium_discount_analysis = Mock()
        mock_market_report.premium_discount_analysis.current_premium_discount = 0.15
        mock_market_report.market_opportunities = ["Export market growth", "Premium baking demand"]
        mock_market_report.risk_factors = ["Weather volatility"]
        mock_market_report.confidence = 0.85
        
        mock_market_intelligence = Mock()
        mock_market_intelligence.reports = [mock_market_report]
        
        with patch.object(service, 'market_intelligence_service') as mock_market_service:
            mock_market_service.get_market_intelligence = AsyncMock(return_value=mock_market_intelligence)
            
            market_score = await service._score_market_desirability(variety, mock_regional_context)
            
            assert 0.0 <= market_score <= 1.0
            # Should be higher due to positive market trends and premium
            assert market_score > 0.6


class TestPerformanceAndScalability:
    """Test performance and scalability of the recommendation system."""
    
    @pytest.mark.asyncio
    async def test_large_dataset_performance(self, service, large_variety_dataset, mock_crop_data, mock_regional_context):
        """Test performance with large variety dataset."""
        start_time = time.time()
        
        # Mock the variety generation to return large dataset
        with patch.object(service, '_get_available_varieties') as mock_get_varieties:
            mock_get_varieties.return_value = large_variety_dataset[:100]  # Test with 100 varieties
            
            recommendations = await service.recommend_varieties(
                mock_crop_data,
                mock_regional_context
            )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        assert len(recommendations) > 0
        assert processing_time < 5.0  # Should process 100 varieties in under 5 seconds
        assert all(isinstance(rec, VarietyRecommendation) for rec in recommendations)
    
    @pytest.mark.asyncio
    async def test_concurrent_recommendation_requests(self, service, mock_crop_data, mock_regional_context):
        """Test concurrent recommendation requests."""
        async def make_recommendation():
            return await service.recommend_varieties(mock_crop_data, mock_regional_context)
        
        # Test with 50 concurrent requests
        start_time = time.time()
        tasks = [make_recommendation() for _ in range(50)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        total_time = end_time - start_time
        
        assert len(results) == 50
        assert all(len(result) > 0 for result in results)
        assert total_time < 10.0  # Should handle 50 concurrent requests in under 10 seconds
    
    @pytest.mark.asyncio
    async def test_memory_usage_with_large_datasets(self, service, large_variety_dataset, mock_crop_data, mock_regional_context):
        """Test memory usage with large datasets."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Process large dataset
        with patch.object(service, '_get_available_varieties') as mock_get_varieties:
            mock_get_varieties.return_value = large_variety_dataset[:500]  # Test with 500 varieties
            
            recommendations = await service.recommend_varieties(
                mock_crop_data,
                mock_regional_context
            )
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        assert len(recommendations) > 0
        assert memory_increase < 100  # Should not increase memory usage by more than 100MB


class TestAgriculturalValidation:
    """Test agricultural validation and real-world scenarios."""
    
    @pytest.mark.asyncio
    async def test_corn_belt_scenario(self, service, mock_crop_data, sample_varieties):
        """Test recommendations for Corn Belt scenario."""
        corn_belt_context = {
            "region": "Corn Belt",
            "climate_zone": "5b",
            "soil_type": "loam",
            "regional_yield_modifier": 0.15,
            "climate_risks": {
                "drought_risk": 0.2,
                "heat_risk": 0.3,
                "disease_pressure": 0.4
            },
            "market_preferences": ["high_yield", "disease_resistant"],
            "regions": ["US", "Corn Belt"]
        }
        
        corn_belt_preferences = {
            "primary_goals": ["yield_maximization", "profit_maximization"],
            "risk_tolerance": "low",
            "quality_priorities": {
                "protein_content": "medium",
                "test_weight": "good"
            }
        }
        
        recommendations = await service.recommend_varieties(
            mock_crop_data,
            corn_belt_context,
            corn_belt_preferences
        )
        
        assert len(recommendations) > 0
        
        # Check that high-yield varieties are prioritized
        top_recommendation = recommendations[0]
        assert top_recommendation.individual_scores["yield_potential"] >= 0.6
    
    @pytest.mark.asyncio
    async def test_drought_prone_scenario(self, service, mock_crop_data, sample_varieties):
        """Test recommendations for drought-prone scenario."""
        drought_context = {
            "region": "Southern Plains",
            "climate_zone": "6a",
            "soil_type": "sandy_loam",
            "regional_yield_modifier": -0.1,
            "climate_risks": {
                "drought_risk": 0.8,
                "heat_risk": 0.7,
                "disease_pressure": 0.2
            },
            "market_preferences": ["drought_tolerant", "heat_tolerant"],
            "regions": ["US", "Southern Plains"]
        }
        
        drought_preferences = {
            "primary_goals": ["risk_minimization", "water_efficiency"],
            "risk_tolerance": "high",
            "quality_priorities": {
                "protein_content": "medium",
                "test_weight": "acceptable"
            }
        }
        
        recommendations = await service.recommend_varieties(
            mock_crop_data,
            drought_context,
            drought_preferences
        )
        
        assert len(recommendations) > 0
        
        # Check that drought-tolerant varieties are prioritized
        top_recommendation = recommendations[0]
        assert top_recommendation.individual_scores["climate_adaptation"] >= 0.6
    
    @pytest.mark.asyncio
    async def test_premium_market_scenario(self, service, mock_crop_data, sample_varieties):
        """Test recommendations for premium market scenario."""
        premium_context = {
            "region": "Pacific Northwest",
            "climate_zone": "7a",
            "soil_type": "volcanic_loam",
            "regional_yield_modifier": 0.05,
            "climate_risks": {
                "drought_risk": 0.3,
                "heat_risk": 0.2,
                "disease_pressure": 0.5
            },
            "market_preferences": ["premium_quality", "artisan_baking"],
            "regions": ["US", "Pacific Northwest"]
        }
        
        premium_preferences = {
            "primary_goals": ["quality_maximization", "premium_pricing"],
            "risk_tolerance": "moderate",
            "quality_priorities": {
                "protein_content": "high",
                "test_weight": "excellent",
                "falling_number": "high"
            }
        }
        
        recommendations = await service.recommend_varieties(
            mock_crop_data,
            premium_context,
            premium_preferences
        )
        
        assert len(recommendations) > 0
        
        # Check that quality-focused varieties are prioritized
        top_recommendation = recommendations[0]
        assert top_recommendation.individual_scores["quality_attributes"] >= 0.6
        assert top_recommendation.individual_scores["market_desirability"] >= 0.6
    
    @pytest.mark.asyncio
    async def test_organic_farming_scenario(self, service, mock_crop_data, sample_varieties):
        """Test recommendations for organic farming scenario."""
        organic_context = {
            "region": "Northeast",
            "climate_zone": "5a",
            "soil_type": "clay_loam",
            "regional_yield_modifier": 0.0,
            "climate_risks": {
                "drought_risk": 0.4,
                "heat_risk": 0.3,
                "disease_pressure": 0.6
            },
            "market_preferences": ["organic", "disease_resistant"],
            "regions": ["US", "Northeast"],
            "farming_system": "organic"
        }
        
        organic_preferences = {
            "primary_goals": ["disease_resistance", "sustainability"],
            "risk_tolerance": "moderate",
            "quality_priorities": {
                "protein_content": "medium",
                "test_weight": "good"
            },
            "management_preferences": {
                "input_intensity": "low",
                "organic_certification": True
            }
        }
        
        recommendations = await service.recommend_varieties(
            mock_crop_data,
            organic_context,
            organic_preferences
        )
        
        assert len(recommendations) > 0
        
        # Check that disease-resistant varieties are prioritized for organic farming
        top_recommendation = recommendations[0]
        assert top_recommendation.individual_scores["disease_resistance"] >= 0.6


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases."""
    
    @pytest.mark.asyncio
    async def test_no_varieties_available(self, service, mock_crop_data, mock_regional_context):
        """Test handling when no varieties are available."""
        with patch.object(service, '_get_available_varieties') as mock_get_varieties:
            mock_get_varieties.return_value = []
            
            recommendations = await service.recommend_varieties(
                mock_crop_data,
                mock_regional_context
            )
            
            assert recommendations == []
    
    @pytest.mark.asyncio
    async def test_invalid_regional_context(self, service, mock_crop_data, sample_varieties):
        """Test handling of invalid regional context."""
        invalid_context = {
            "region": None,
            "climate_zone": "invalid_zone",
            "soil_type": "",
            "regional_yield_modifier": "invalid"
        }
        
        with patch.object(service, '_get_available_varieties') as mock_get_varieties:
            mock_get_varieties.return_value = sample_varieties
            
            recommendations = await service.recommend_varieties(
                mock_crop_data,
                invalid_context
            )
            
            # Should still return recommendations with default values
            assert len(recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_service_dependency_failures(self, service, mock_crop_data, mock_regional_context, sample_varieties):
        """Test handling when external services fail."""
        with patch.object(service, '_get_available_varieties') as mock_get_varieties:
            mock_get_varieties.return_value = sample_varieties
            
            # Mock all external services to fail
            service.market_intelligence_service = None
            service.economic_analysis_service = None
            service.seed_company_service = None
            
            recommendations = await service.recommend_varieties(
                mock_crop_data,
                mock_regional_context
            )
            
            # Should still return recommendations using fallback methods
            assert len(recommendations) > 0
            assert all(isinstance(rec, VarietyRecommendation) for rec in recommendations)
    
    @pytest.mark.asyncio
    async def test_malformed_variety_data(self, service, mock_crop_data, mock_regional_context):
        """Test handling of malformed variety data."""
        malformed_variety = EnhancedCropVariety(
            id=uuid4(),
            variety_name="",  # Empty name
            variety_code=None,  # None code
            parent_crop_id=uuid4(),
            release_year=None,  # None year
            breeding_institution="",
            yield_potential=None,  # None yield data
            disease_resistance=None,  # None disease data
            abiotic_stress_tolerances=None,  # None stress data
            quality_attributes=None,  # None quality data
            market_attributes=None  # None market data
        )
        
        with patch.object(service, '_get_available_varieties') as mock_get_varieties:
            mock_get_varieties.return_value = [malformed_variety]
            
            recommendations = await service.recommend_varieties(
                mock_crop_data,
                mock_regional_context
            )
            
            # Should handle gracefully and return recommendations with default scores
            assert len(recommendations) > 0
            assert all(0.0 <= rec.overall_score <= 1.0 for rec in recommendations)


class TestDataQualityAndValidation:
    """Test data quality and validation."""
    
    @pytest.mark.asyncio
    async def test_score_validation(self, service, sample_varieties, mock_regional_context):
        """Test that all scores are within valid ranges."""
        variety = sample_varieties[0]
        
        score_data = await service._score_variety_for_context(
            variety, mock_regional_context, None
        )
        
        assert score_data is not None
        assert "individual_scores" in score_data
        assert "overall_score" in score_data
        
        # Check individual scores are within valid range
        for factor, score in score_data["individual_scores"].items():
            assert 0.0 <= score <= 1.0, f"Score for {factor} is {score}, should be 0.0-1.0"
        
        # Check overall score is within valid range
        assert 0.0 <= score_data["overall_score"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_recommendation_data_integrity(self, service, mock_crop_data, mock_regional_context, sample_varieties):
        """Test data integrity of recommendations."""
        with patch.object(service, '_get_available_varieties') as mock_get_varieties:
            mock_get_varieties.return_value = sample_varieties
            
            recommendations = await service.recommend_varieties(
                mock_crop_data,
                mock_regional_context
            )
            
            for rec in recommendations:
                # Check required fields are present
                assert rec.variety_name is not None
                assert rec.variety_id is not None
                assert rec.overall_score is not None
                assert rec.confidence_level is not None
                
                # Check data types
                assert isinstance(rec.overall_score, (int, float))
                assert isinstance(rec.confidence_level, (int, float))
                assert isinstance(rec.suitability_factors, dict)
                assert isinstance(rec.individual_scores, dict)
                
                # Check score consistency
                assert 0.0 <= rec.overall_score <= 1.0
                assert 0.0 <= rec.confidence_level <= 1.0
    
    @pytest.mark.asyncio
    async def test_recommendation_ranking_consistency(self, service, mock_crop_data, mock_regional_context, sample_varieties):
        """Test that recommendations are properly ranked."""
        with patch.object(service, '_get_available_varieties') as mock_get_varieties:
            mock_get_varieties.return_value = sample_varieties
            
            recommendations = await service.recommend_varieties(
                mock_crop_data,
                mock_regional_context
            )
            
            # Check that recommendations are sorted by overall score (descending)
            scores = [rec.overall_score for rec in recommendations]
            assert scores == sorted(scores, reverse=True)
            
            # Check that top recommendation has highest score
            if len(recommendations) > 1:
                assert recommendations[0].overall_score >= recommendations[1].overall_score


# Performance benchmarking tests
class TestPerformanceBenchmarks:
    """Performance benchmarking tests."""
    
    @pytest.mark.asyncio
    async def test_recommendation_response_time(self, service, mock_crop_data, mock_regional_context, sample_varieties):
        """Test that recommendations are generated within acceptable time limits."""
        with patch.object(service, '_get_available_varieties') as mock_get_varieties:
            mock_get_varieties.return_value = sample_varieties
            
            start_time = time.time()
            recommendations = await service.recommend_varieties(
                mock_crop_data,
                mock_regional_context
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response_time < 2.0  # Should respond within 2 seconds
            assert len(recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_concurrent_user_simulation(self, service, mock_crop_data, mock_regional_context, sample_varieties):
        """Simulate 1000+ concurrent users making recommendations."""
        async def user_request():
            with patch.object(service, '_get_available_varieties') as mock_get_varieties:
                mock_get_varieties.return_value = sample_varieties[:10]  # Limit varieties per request
                
                return await service.recommend_varieties(
                    mock_crop_data,
                    mock_regional_context
                )
        
        # Simulate 1000 concurrent users
        start_time = time.time()
        tasks = [user_request() for _ in range(1000)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        total_time = end_time - start_time
        successful_requests = sum(1 for result in results if not isinstance(result, Exception))
        
        assert successful_requests >= 950  # At least 95% success rate
        assert total_time < 30.0  # Should handle 1000 requests in under 30 seconds
        assert total_time / 1000 < 0.05  # Average response time under 50ms per request


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])