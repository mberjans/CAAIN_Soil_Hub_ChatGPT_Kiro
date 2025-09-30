"""
Agricultural Intelligence Service Tests
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

Comprehensive test suite for agricultural intelligence service.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import sys
import os

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../src/services'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../databases/python'))

from agricultural_intelligence_service import (
    AgriculturalIntelligenceService, AgriculturalIntelligenceResponse,
    IntelligenceType, RegionalBestPractice, ExpertRecommendation,
    PeerFarmerInsight, MarketInsight, SuccessPattern,
    RecommendationSource
)


class TestAgriculturalIntelligenceService:
    """Test suite for AgriculturalIntelligenceService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return AgriculturalIntelligenceService()
    
    @pytest.fixture
    def sample_coordinates(self):
        """Sample coordinates for testing."""
        return {
            'corn_belt': (42.0308, -93.6319),  # Iowa
            'southern_plains': (35.4676, -97.5164),  # Oklahoma
            'pacific_northwest': (47.6062, -122.3321),  # Seattle
            'california_central_valley': (36.7378, -119.7871),  # Fresno
            'southeast': (33.7490, -84.3880)  # Atlanta
        }
    
    @pytest.fixture
    def sample_regional_best_practice(self):
        """Sample regional best practice for testing."""
        return RegionalBestPractice(
            practice_id="test_001",
            title="Test Practice",
            description="Test practice description",
            category="soil_management",
            region="corn_belt",
            effectiveness_score=0.85,
            adoption_rate=0.65,
            cost_benefit_ratio=2.3,
            environmental_impact="positive",
            implementation_difficulty="medium",
            seasonal_timing=["spring", "fall"],
            crop_compatibility=["corn", "soybean"],
            soil_type_compatibility=["loam", "clay_loam"],
            source=RecommendationSource.UNIVERSITY_EXTENSION,
            last_updated=datetime.utcnow(),
            validation_status="validated"
        )
    
    @pytest.fixture
    def sample_expert_recommendation(self):
        """Sample expert recommendation for testing."""
        return ExpertRecommendation(
            recommendation_id="expert_001",
            expert_name="Dr. Test Expert",
            expert_title="Extension Specialist",
            organization="Test University",
            expertise_area="Soil Health",
            recommendation="Test recommendation",
            rationale="Test rationale",
            confidence_level=0.92,
            applicable_conditions={"soil_type": "loam"},
            contact_info={"email": "test@university.edu"},
            last_updated=datetime.utcnow(),
            validation_status="validated"
        )
    
    @pytest.fixture
    def sample_peer_insight(self):
        """Sample peer farmer insight for testing."""
        return PeerFarmerInsight(
            insight_id="peer_001",
            farmer_name="Test Farmer",
            farm_size_acres=500.0,
            farm_type="crop",
            location_region="corn_belt",
            insight_type="success_story",
            title="Test Success Story",
            description="Test description",
            crop_type="corn",
            practice_used="Test practice",
            results={"yield_improvement": 0.15},
            lessons_learned=["Test lesson"],
            recommendations=["Test recommendation"],
            year=2024,
            season="fall",
            validation_status="validated",
            peer_rating=4.2
        )
    
    @pytest.mark.asyncio
    async def test_get_location_intelligence_success(self, service, sample_coordinates):
        """Test successful location intelligence retrieval."""
        lat, lng = sample_coordinates['corn_belt']
        
        result = await service.get_location_intelligence(lat, lng)
        
        assert isinstance(result, AgriculturalIntelligenceResponse)
        assert result.location["lat"] == lat
        assert result.location["lng"] == lng
        assert result.region == "corn_belt"
        assert isinstance(result.regional_best_practices, list)
        assert isinstance(result.expert_recommendations, list)
        assert isinstance(result.peer_insights, list)
        assert isinstance(result.market_insights, list)
        assert isinstance(result.success_patterns, list)
        assert isinstance(result.local_adaptations, list)
        assert isinstance(result.confidence_scores, dict)
        assert isinstance(result.intelligence_summary, dict)
        assert result.last_updated is not None
        assert isinstance(result.data_sources, list)
    
    @pytest.mark.asyncio
    async def test_get_location_intelligence_with_filters(self, service, sample_coordinates):
        """Test location intelligence retrieval with filters."""
        lat, lng = sample_coordinates['corn_belt']
        
        result = await service.get_location_intelligence(
            lat, lng,
            intelligence_types=[IntelligenceType.REGIONAL_BEST_PRACTICES],
            crop_type="corn",
            farm_size_acres=500.0
        )
        
        assert isinstance(result, AgriculturalIntelligenceResponse)
        assert result.location["lat"] == lat
        assert result.location["lng"] == lng
        assert result.region == "corn_belt"
    
    @pytest.mark.asyncio
    async def test_determine_region_corn_belt(self, service):
        """Test region determination for corn belt."""
        region = await service._determine_region(42.0308, -93.6319)
        assert region == "corn_belt"
    
    @pytest.mark.asyncio
    async def test_determine_region_southern_plains(self, service):
        """Test region determination for southern plains."""
        region = await service._determine_region(35.4676, -97.5164)
        assert region == "southern_plains"
    
    @pytest.mark.asyncio
    async def test_determine_region_pacific_northwest(self, service):
        """Test region determination for pacific northwest."""
        region = await service._determine_region(47.6062, -122.3321)
        assert region == "pacific_northwest"
    
    @pytest.mark.asyncio
    async def test_determine_region_california_central_valley(self, service):
        """Test region determination for California central valley."""
        region = await service._determine_region(36.7378, -119.7871)
        assert region == "california_central_valley"
    
    @pytest.mark.asyncio
    async def test_determine_region_southeast(self, service):
        """Test region determination for southeast."""
        region = await service._determine_region(33.7490, -84.3880)
        assert region == "southeast"
    
    @pytest.mark.asyncio
    async def test_determine_region_general_agricultural(self, service):
        """Test region determination for general agricultural."""
        region = await service._determine_region(20.0, -60.0)  # Caribbean - outside all defined regions
        assert region == "general_agricultural"
    
    @pytest.mark.asyncio
    async def test_get_regional_best_practices(self, service):
        """Test regional best practices retrieval."""
        practices = await service._get_regional_best_practices("corn_belt")
        
        assert isinstance(practices, list)
        if practices:  # If data is available
            practice = practices[0]
            assert isinstance(practice, RegionalBestPractice)
            assert practice.region == "corn_belt"
            assert 0.0 <= practice.effectiveness_score <= 1.0
            assert 0.0 <= practice.adoption_rate <= 1.0
            assert practice.cost_benefit_ratio > 0
            assert practice.environmental_impact in ["positive", "neutral", "negative"]
            assert practice.implementation_difficulty in ["easy", "medium", "hard"]
            assert isinstance(practice.seasonal_timing, list)
            assert isinstance(practice.crop_compatibility, list)
            assert isinstance(practice.soil_type_compatibility, list)
            assert isinstance(practice.source, RecommendationSource)
            assert isinstance(practice.last_updated, datetime)
            assert practice.validation_status in ["validated", "pending", "experimental"]
    
    @pytest.mark.asyncio
    async def test_get_regional_best_practices_with_crop_filter(self, service):
        """Test regional best practices with crop type filter."""
        practices = await service._get_regional_best_practices("corn_belt", crop_type="corn")
        
        assert isinstance(practices, list)
        # All practices should be compatible with corn
        for practice in practices:
            assert "corn" in practice.crop_compatibility
    
    @pytest.mark.asyncio
    async def test_get_regional_best_practices_with_farm_size_filter(self, service):
        """Test regional best practices with farm size filter."""
        practices = await service._get_regional_best_practices("corn_belt", farm_size_acres=500.0)
        
        assert isinstance(practices, list)
        # Practices should be filtered by farm size compatibility
    
    @pytest.mark.asyncio
    async def test_get_expert_recommendations(self, service):
        """Test expert recommendations retrieval."""
        recommendations = await service._get_expert_recommendations("corn_belt")
        
        assert isinstance(recommendations, list)
        if recommendations:  # If data is available
            rec = recommendations[0]
            assert isinstance(rec, ExpertRecommendation)
            assert rec.recommendation_id is not None
            assert rec.expert_name is not None
            assert rec.expert_title is not None
            assert rec.organization is not None
            assert rec.expertise_area is not None
            assert rec.recommendation is not None
            assert rec.rationale is not None
            assert 0.0 <= rec.confidence_level <= 1.0
            assert isinstance(rec.applicable_conditions, dict)
            assert isinstance(rec.last_updated, datetime)
            assert rec.validation_status in ["validated", "pending", "experimental"]
    
    @pytest.mark.asyncio
    async def test_get_peer_farmer_insights(self, service):
        """Test peer farmer insights retrieval."""
        insights = await service._get_peer_farmer_insights(42.0308, -93.6319)
        
        assert isinstance(insights, list)
        if insights:  # If data is available
            insight = insights[0]
            assert isinstance(insight, PeerFarmerInsight)
            assert insight.insight_id is not None
            assert insight.farm_type is not None
            assert insight.location_region is not None
            assert insight.insight_type is not None
            assert insight.title is not None
            assert insight.description is not None
            assert insight.practice_used is not None
            assert isinstance(insight.results, dict)
            assert isinstance(insight.lessons_learned, list)
            assert isinstance(insight.recommendations, list)
            assert isinstance(insight.year, int)
            assert insight.season is not None
            assert insight.validation_status in ["validated", "pending", "experimental"]
            assert 0.0 <= insight.peer_rating <= 5.0
    
    @pytest.mark.asyncio
    async def test_get_peer_farmer_insights_with_distance_filter(self, service):
        """Test peer farmer insights with distance filtering."""
        # Test with coordinates far from any peer insights
        insights = await service._get_peer_farmer_insights(0.0, 0.0)  # Null island
        
        assert isinstance(insights, list)
        # Should be empty or filtered by distance
    
    @pytest.mark.asyncio
    async def test_get_market_insights(self, service):
        """Test market insights retrieval."""
        insights = await service._get_market_insights("corn_belt")
        
        assert isinstance(insights, list)
        if insights:  # If data is available
            insight = insights[0]
            assert isinstance(insight, MarketInsight)
            assert insight.insight_id is not None
            assert insight.market_type is not None
            assert insight.crop_type is not None
            assert insight.region == "corn_belt"
            assert insight.price_trend in ["increasing", "decreasing", "stable"]
            assert insight.demand_level in ["high", "medium", "low"]
            assert isinstance(insight.seasonal_patterns, dict)
            assert insight.competition_level in ["high", "medium", "low"]
            assert isinstance(insight.market_access, list)
            assert isinstance(insight.premium_opportunities, list)
            assert isinstance(insight.last_updated, datetime)
            assert insight.data_source is not None
    
    @pytest.mark.asyncio
    async def test_get_success_patterns(self, service):
        """Test success patterns retrieval."""
        patterns = await service._get_success_patterns("corn_belt")
        
        assert isinstance(patterns, list)
        if patterns:  # If data is available
            pattern = patterns[0]
            assert isinstance(pattern, SuccessPattern)
            assert pattern.pattern_id is not None
            assert pattern.pattern_name is not None
            assert pattern.region == "corn_belt"
            assert pattern.crop_type is not None
            assert isinstance(pattern.success_factors, list)
            assert isinstance(pattern.common_practices, list)
            assert pattern.average_yield >= 0
            assert isinstance(pattern.profitability_metrics, dict)
            assert isinstance(pattern.risk_factors, list)
            assert isinstance(pattern.mitigation_strategies, list)
            assert pattern.farmer_count >= 0
            assert 0.0 <= pattern.success_rate <= 1.0
            assert isinstance(pattern.last_analyzed, datetime)
    
    @pytest.mark.asyncio
    async def test_generate_local_adaptations(self, service, sample_regional_best_practice, sample_expert_recommendation):
        """Test local adaptations generation."""
        adaptations = await service._generate_local_adaptations(
            "corn_belt",
            "corn",
            500.0,
            [sample_regional_best_practice],
            [sample_expert_recommendation]
        )
        
        assert isinstance(adaptations, list)
        if adaptations:
            adaptation = adaptations[0]
            assert isinstance(adaptation, dict)
            assert "practice_id" in adaptation
            assert "original_practice" in adaptation
            assert "regional_adaptation" in adaptation
            assert "adaptation_rationale" in adaptation
            assert "specific_modifications" in adaptation
            assert "expected_benefits" in adaptation
            assert "implementation_timeline" in adaptation
            assert "cost_considerations" in adaptation
            assert isinstance(adaptation["specific_modifications"], list)
    
    @pytest.mark.asyncio
    async def test_calculate_confidence_scores(self, service, sample_regional_best_practice, sample_expert_recommendation, sample_peer_insight):
        """Test confidence scores calculation."""
        scores = await service._calculate_confidence_scores(
            "corn_belt",
            [sample_regional_best_practice],
            [sample_expert_recommendation],
            [sample_peer_insight]
        )
        
        assert isinstance(scores, dict)
        assert "regional_best_practices" in scores
        assert "expert_recommendations" in scores
        assert "peer_insights" in scores
        assert "overall" in scores
        
        for score in scores.values():
            assert 0.0 <= score <= 1.0
    
    @pytest.mark.asyncio
    async def test_create_intelligence_summary(self, service, sample_regional_best_practice, sample_expert_recommendation, sample_peer_insight):
        """Test intelligence summary creation."""
        summary = await service._create_intelligence_summary(
            "corn_belt",
            [sample_regional_best_practice],
            [sample_expert_recommendation],
            [sample_peer_insight],
            [],
            []
        )
        
        assert isinstance(summary, dict)
        assert "region" in summary
        assert "total_recommendations" in summary
        assert "top_categories" in summary
        assert "key_insights" in summary
        assert "market_opportunities" in summary
        assert "risk_factors" in summary
        assert "success_indicators" in summary
        
        assert summary["region"] == "corn_belt"
        assert isinstance(summary["total_recommendations"], int)
        assert isinstance(summary["top_categories"], list)
        assert isinstance(summary["key_insights"], list)
        assert isinstance(summary["market_opportunities"], list)
        assert isinstance(summary["risk_factors"], list)
        assert isinstance(summary["success_indicators"], list)
    
    def test_calculate_distance(self, service):
        """Test distance calculation between coordinates."""
        # Test distance between Iowa and Oklahoma
        distance = service._calculate_distance(42.0308, -93.6319, 35.4676, -97.5164)
        assert isinstance(distance, float)
        assert distance > 0
        assert distance < 1000  # Should be less than 1000 km
    
    def test_calculate_distance_same_location(self, service):
        """Test distance calculation for same location."""
        distance = service._calculate_distance(42.0308, -93.6319, 42.0308, -93.6319)
        assert distance == 0.0
    
    @pytest.mark.asyncio
    async def test_cache_functionality(self, service):
        """Test caching functionality."""
        cache_key = "test_cache_key"
        
        # Test cache miss
        cached_result = await service._get_cached_intelligence(cache_key)
        assert cached_result is None
        
        # Test cache set and get
        test_data = AgriculturalIntelligenceResponse(
            location={"lat": 42.0308, "lng": -93.6319},
            region="corn_belt",
            intelligence_summary={},
            regional_best_practices=[],
            expert_recommendations=[],
            peer_insights=[],
            market_insights=[],
            success_patterns=[],
            local_adaptations=[],
            confidence_scores={},
            last_updated=datetime.utcnow(),
            data_sources=[]
        )
        
        await service._cache_intelligence(cache_key, test_data)
        
        cached_result = await service._get_cached_intelligence(cache_key)
        assert cached_result is not None
        assert cached_result.region == "corn_belt"
    
    @pytest.mark.asyncio
    async def test_error_handling(self, service):
        """Test error handling in service methods."""
        # Test with invalid coordinates - should return general_agricultural region
        result = await service.get_location_intelligence(200.0, 200.0)  # Invalid coordinates
        assert result.region == "general_agricultural"
    
    def test_regional_boundaries_loading(self, service):
        """Test regional boundaries loading."""
        boundaries = service._load_regional_boundaries()
        
        assert isinstance(boundaries, dict)
        assert "corn_belt" in boundaries
        assert "southern_plains" in boundaries
        assert "pacific_northwest" in boundaries
        assert "california_central_valley" in boundaries
        assert "southeast" in boundaries
        
        for region, bounds in boundaries.items():
            assert "lat_range" in bounds
            assert "lng_range" in bounds
            assert isinstance(bounds["lat_range"], tuple)
            assert isinstance(bounds["lng_range"], tuple)
            assert len(bounds["lat_range"]) == 2
            assert len(bounds["lng_range"]) == 2
    
    def test_regional_characteristics_loading(self, service):
        """Test regional characteristics loading."""
        characteristics = service._load_regional_characteristics()
        
        assert isinstance(characteristics, dict)
        assert "corn_belt" in characteristics
        assert "southern_plains" in characteristics
        assert "pacific_northwest" in characteristics
        assert "california_central_valley" in characteristics
        assert "southeast" in characteristics
        
        for region, chars in characteristics.items():
            assert "climate_type" in chars
            assert "growing_season" in chars
            assert "soil_type" in chars
            assert "farm_size_category" in chars
            assert "cost_modifier" in chars


class TestAgriculturalIntelligenceModels:
    """Test suite for agricultural intelligence models."""
    
    def test_regional_best_practice_creation(self):
        """Test RegionalBestPractice model creation."""
        practice = RegionalBestPractice(
            practice_id="test_001",
            title="Test Practice",
            description="Test description",
            category="soil_management",
            region="corn_belt",
            effectiveness_score=0.85,
            adoption_rate=0.65,
            cost_benefit_ratio=2.3,
            environmental_impact="positive",
            implementation_difficulty="medium",
            seasonal_timing=["spring", "fall"],
            crop_compatibility=["corn", "soybean"],
            soil_type_compatibility=["loam", "clay_loam"],
            source=RecommendationSource.UNIVERSITY_EXTENSION,
            last_updated=datetime.utcnow(),
            validation_status="validated"
        )
        
        assert practice.practice_id == "test_001"
        assert practice.title == "Test Practice"
        assert practice.category == "soil_management"
        assert practice.region == "corn_belt"
        assert practice.effectiveness_score == 0.85
        assert practice.adoption_rate == 0.65
        assert practice.cost_benefit_ratio == 2.3
        assert practice.environmental_impact == "positive"
        assert practice.implementation_difficulty == "medium"
        assert practice.seasonal_timing == ["spring", "fall"]
        assert practice.crop_compatibility == ["corn", "soybean"]
        assert practice.soil_type_compatibility == ["loam", "clay_loam"]
        assert practice.source == RecommendationSource.UNIVERSITY_EXTENSION
        assert practice.validation_status == "validated"
    
    def test_expert_recommendation_creation(self):
        """Test ExpertRecommendation model creation."""
        recommendation = ExpertRecommendation(
            recommendation_id="expert_001",
            expert_name="Dr. Test Expert",
            expert_title="Extension Specialist",
            organization="Test University",
            expertise_area="Soil Health",
            recommendation="Test recommendation",
            rationale="Test rationale",
            confidence_level=0.92,
            applicable_conditions={"soil_type": "loam"},
            contact_info={"email": "test@university.edu"},
            last_updated=datetime.utcnow(),
            validation_status="validated"
        )
        
        assert recommendation.recommendation_id == "expert_001"
        assert recommendation.expert_name == "Dr. Test Expert"
        assert recommendation.expert_title == "Extension Specialist"
        assert recommendation.organization == "Test University"
        assert recommendation.expertise_area == "Soil Health"
        assert recommendation.recommendation == "Test recommendation"
        assert recommendation.rationale == "Test rationale"
        assert recommendation.confidence_level == 0.92
        assert recommendation.applicable_conditions == {"soil_type": "loam"}
        assert recommendation.contact_info == {"email": "test@university.edu"}
        assert recommendation.validation_status == "validated"
    
    def test_peer_farmer_insight_creation(self):
        """Test PeerFarmerInsight model creation."""
        insight = PeerFarmerInsight(
            insight_id="peer_001",
            farmer_name="Test Farmer",
            farm_size_acres=500.0,
            farm_type="crop",
            location_region="corn_belt",
            insight_type="success_story",
            title="Test Success Story",
            description="Test description",
            crop_type="corn",
            practice_used="Test practice",
            results={"yield_improvement": 0.15},
            lessons_learned=["Test lesson"],
            recommendations=["Test recommendation"],
            year=2024,
            season="fall",
            validation_status="validated",
            peer_rating=4.2
        )
        
        assert insight.insight_id == "peer_001"
        assert insight.farmer_name == "Test Farmer"
        assert insight.farm_size_acres == 500.0
        assert insight.farm_type == "crop"
        assert insight.location_region == "corn_belt"
        assert insight.insight_type == "success_story"
        assert insight.title == "Test Success Story"
        assert insight.description == "Test description"
        assert insight.crop_type == "corn"
        assert insight.practice_used == "Test practice"
        assert insight.results == {"yield_improvement": 0.15}
        assert insight.lessons_learned == ["Test lesson"]
        assert insight.recommendations == ["Test recommendation"]
        assert insight.year == 2024
        assert insight.season == "fall"
        assert insight.validation_status == "validated"
        assert insight.peer_rating == 4.2


class TestAgriculturalIntelligenceIntegration:
    """Integration tests for agricultural intelligence service."""
    
    @pytest.mark.asyncio
    async def test_full_intelligence_workflow(self):
        """Test complete intelligence workflow."""
        service = AgriculturalIntelligenceService()
        
        # Test with corn belt coordinates
        result = await service.get_location_intelligence(42.0308, -93.6319)
        
        # Verify response structure
        assert isinstance(result, AgriculturalIntelligenceResponse)
        assert result.location["lat"] == 42.0308
        assert result.location["lng"] == -93.6319
        assert result.region == "corn_belt"
        
        # Verify all components are present
        assert isinstance(result.regional_best_practices, list)
        assert isinstance(result.expert_recommendations, list)
        assert isinstance(result.peer_insights, list)
        assert isinstance(result.market_insights, list)
        assert isinstance(result.success_patterns, list)
        assert isinstance(result.local_adaptations, list)
        assert isinstance(result.confidence_scores, dict)
        assert isinstance(result.intelligence_summary, dict)
        
        # Verify confidence scores
        assert "regional_best_practices" in result.confidence_scores
        assert "expert_recommendations" in result.confidence_scores
        assert "peer_insights" in result.confidence_scores
        assert "overall" in result.confidence_scores
        
        # Verify intelligence summary
        assert "region" in result.intelligence_summary
        assert "total_recommendations" in result.intelligence_summary
        assert "top_categories" in result.intelligence_summary
        assert "key_insights" in result.intelligence_summary
    
    @pytest.mark.asyncio
    async def test_caching_workflow(self):
        """Test caching workflow."""
        service = AgriculturalIntelligenceService()
        
        # First request (cache miss)
        result1 = await service.get_location_intelligence(42.0308, -93.6319)
        
        # Second request (cache hit)
        result2 = await service.get_location_intelligence(42.0308, -93.6319)
        
        # Results should be identical
        assert result1.region == result2.region
        assert result1.location == result2.location
        assert len(result1.regional_best_practices) == len(result2.regional_best_practices)
        assert len(result1.expert_recommendations) == len(result2.expert_recommendations)
        assert len(result1.peer_insights) == len(result2.peer_insights)
    
    @pytest.mark.asyncio
    async def test_filtering_workflow(self):
        """Test filtering workflow."""
        service = AgriculturalIntelligenceService()
        
        # Test with crop type filter
        result = await service.get_location_intelligence(
            42.0308, -93.6319,
            crop_type="corn",
            farm_size_acres=500.0
        )
        
        # Verify filtering worked
        assert isinstance(result, AgriculturalIntelligenceResponse)
        assert result.region == "corn_belt"
        
        # Verify best practices are filtered by crop compatibility
        for practice in result.regional_best_practices:
            assert "corn" in practice.crop_compatibility
    
    @pytest.mark.asyncio
    async def test_multiple_regions(self):
        """Test intelligence gathering for multiple regions."""
        service = AgriculturalIntelligenceService()
        
        regions = [
            (42.0308, -93.6319, "corn_belt"),
            (35.4676, -97.5164, "southern_plains"),
            (47.6062, -122.3321, "pacific_northwest"),
            (36.7378, -119.7871, "california_central_valley"),
            (33.7490, -84.3880, "southeast")
        ]
        
        for lat, lng, expected_region in regions:
            result = await service.get_location_intelligence(lat, lng)
            assert result.region == expected_region
            assert isinstance(result.intelligence_summary, dict)
            assert isinstance(result.confidence_scores, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])