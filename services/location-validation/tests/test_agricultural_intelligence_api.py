"""
Agricultural Intelligence API Tests
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

Comprehensive test suite for agricultural intelligence API endpoints.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os
import json

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../databases/python'))

from main import app
from agricultural_intelligence_service import (
    AgriculturalIntelligenceResponse, RegionalBestPractice, ExpertRecommendation,
    PeerFarmerInsight, MarketInsight, SuccessPattern, IntelligenceType,
    RecommendationSource
)
from datetime import datetime


class TestAgriculturalIntelligenceAPI:
    """Test suite for agricultural intelligence API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_intelligence_response(self):
        """Sample intelligence response for testing."""
        return AgriculturalIntelligenceResponse(
            location={"lat": 42.0308, "lng": -93.6319},
            region="corn_belt",
            intelligence_summary={
                "region": "corn_belt",
                "total_recommendations": 3,
                "top_categories": [("soil_management", 2)],
                "key_insights": [
                    {
                        "type": "best_practice",
                        "title": "No-Till Corn Production",
                        "description": "No-till corn production system...",
                        "effectiveness": 0.85
                    }
                ],
                "market_opportunities": [],
                "risk_factors": [],
                "success_indicators": []
            },
            regional_best_practices=[
                RegionalBestPractice(
                    practice_id="cb_001",
                    title="No-Till Corn Production",
                    description="No-till corn production system for soil health",
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
            ],
            expert_recommendations=[
                ExpertRecommendation(
                    recommendation_id="cb_expert_001",
                    expert_name="Dr. Sarah Johnson",
                    expert_title="Extension Specialist",
                    organization="Iowa State University",
                    expertise_area="Soil Health",
                    recommendation="Implement cover crops in corn-soybean rotation",
                    rationale="Cover crops improve soil organic matter",
                    confidence_level=0.92,
                    applicable_conditions={"soil_type": "loam"},
                    contact_info={"email": "sjohnson@iastate.edu"},
                    last_updated=datetime.utcnow(),
                    validation_status="validated"
                )
            ],
            peer_insights=[
                PeerFarmerInsight(
                    insight_id="peer_001",
                    farmer_name="John Smith",
                    farm_size_acres=500.0,
                    farm_type="crop",
                    location_region="corn_belt",
                    insight_type="success_story",
                    title="Cover Crop Success Story",
                    description="Successfully integrated cover crops",
                    crop_type="corn",
                    practice_used="Cover crop integration",
                    results={"yield_improvement": 0.15},
                    lessons_learned=["Timing is critical"],
                    recommendations=["Start small"],
                    year=2024,
                    season="fall",
                    validation_status="validated",
                    peer_rating=4.2
                )
            ],
            market_insights=[
                MarketInsight(
                    insight_id="market_cb_001",
                    market_type="commodity",
                    crop_type="corn",
                    region="corn_belt",
                    price_trend="stable",
                    demand_level="high",
                    seasonal_patterns={"spring": "planting"},
                    competition_level="high",
                    market_access=["grain_elevator"],
                    premium_opportunities=["organic"],
                    last_updated=datetime.utcnow(),
                    data_source="USDA_NASS"
                )
            ],
            success_patterns=[
                SuccessPattern(
                    pattern_id="pattern_cb_001",
                    pattern_name="High-Yield Corn Production",
                    region="corn_belt",
                    crop_type="corn",
                    success_factors=["soil_health", "timing"],
                    common_practices=["no_till", "cover_crops"],
                    average_yield=180.0,
                    profitability_metrics={"roi": 0.25},
                    risk_factors=["weather"],
                    mitigation_strategies=["crop_insurance"],
                    farmer_count=1250,
                    success_rate=0.78,
                    last_analyzed=datetime.utcnow()
                )
            ],
            local_adaptations=[
                {
                    "practice_id": "cb_001",
                    "original_practice": "No-Till Corn Production",
                    "regional_adaptation": "No-Till Corn Production adapted for corn_belt",
                    "adaptation_rationale": "Modified for temperate_continental conditions",
                    "specific_modifications": [
                        "Timing adjusted for moderate growing season",
                        "Application rates modified for fertile_loam soils"
                    ],
                    "expected_benefits": "No-till corn production system for soil health",
                    "implementation_timeline": "1-2 seasons",
                    "cost_considerations": "Similar to original practice with standard regional adjustments"
                }
            ],
            confidence_scores={
                "regional_best_practices": 0.75,
                "expert_recommendations": 0.92,
                "peer_insights": 0.84,
                "overall": 0.84
            },
            last_updated=datetime.utcnow(),
            data_sources=["university_extension", "local_experts", "peer_network"]
        )
    
    @pytest.mark.asyncio
    async def test_get_location_intelligence_success(self, client, sample_intelligence_response):
        """Test successful location intelligence retrieval."""
        with patch('api.agricultural_intelligence_routes.intelligence_service.get_location_intelligence') as mock_service:
            mock_service.return_value = sample_intelligence_response
            
            response = client.post(
                "/api/v1/agricultural-intelligence/location-intelligence",
                json={
                    "latitude": 42.0308,
                    "longitude": -93.6319
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["location"]["lat"] == 42.0308
            assert data["location"]["lng"] == -93.6319
            assert data["region"] == "corn_belt"
            assert isinstance(data["regional_best_practices"], list)
            assert isinstance(data["expert_recommendations"], list)
            assert isinstance(data["peer_insights"], list)
            assert isinstance(data["market_insights"], list)
            assert isinstance(data["success_patterns"], list)
            assert isinstance(data["local_adaptations"], list)
            assert isinstance(data["confidence_scores"], dict)
            assert isinstance(data["intelligence_summary"], dict)
            assert data["data_sources"] is not None
    
    @pytest.mark.asyncio
    async def test_get_location_intelligence_with_filters(self, client, sample_intelligence_response):
        """Test location intelligence retrieval with filters."""
        with patch('api.agricultural_intelligence_routes.intelligence_service.get_location_intelligence') as mock_service:
            mock_service.return_value = sample_intelligence_response
            
            response = client.post(
                "/api/v1/agricultural-intelligence/location-intelligence",
                json={
                    "latitude": 42.0308,
                    "longitude": -93.6319,
                    "intelligence_types": ["regional_best_practices"],
                    "crop_type": "corn",
                    "farm_size_acres": 500.0
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["region"] == "corn_belt"
    
    def test_get_location_intelligence_invalid_coordinates(self, client):
        """Test location intelligence with invalid coordinates."""
        response = client.post(
            "/api/v1/agricultural-intelligence/location-intelligence",
            json={
                "latitude": 200.0,  # Invalid latitude
                "longitude": -93.6319
            }
        )
        
        assert response.status_code == 422
    
    def test_get_location_intelligence_missing_coordinates(self, client):
        """Test location intelligence with missing coordinates."""
        response = client.post(
            "/api/v1/agricultural-intelligence/location-intelligence",
            json={
                "latitude": 42.0308
                # Missing longitude
            }
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_get_regional_best_practices_success(self, client, sample_intelligence_response):
        """Test successful regional best practices retrieval."""
        with patch('api.agricultural_intelligence_routes.intelligence_service.get_location_intelligence') as mock_service:
            mock_service.return_value = sample_intelligence_response
            
            response = client.get(
                "/api/v1/agricultural-intelligence/regional-best-practices",
                params={
                    "latitude": 42.0308,
                    "longitude": -93.6319
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert isinstance(data, list)
            if data:
                practice = data[0]
                assert "practice_id" in practice
                assert "title" in practice
                assert "description" in practice
                assert "category" in practice
                assert "region" in practice
                assert "effectiveness_score" in practice
                assert "adoption_rate" in practice
                assert "cost_benefit_ratio" in practice
                assert "environmental_impact" in practice
                assert "implementation_difficulty" in practice
                assert "seasonal_timing" in practice
                assert "crop_compatibility" in practice
                assert "soil_type_compatibility" in practice
                assert "source" in practice
                assert "validation_status" in practice
    
    def test_get_regional_best_practices_invalid_coordinates(self, client):
        """Test regional best practices with invalid coordinates."""
        response = client.get(
            "/api/v1/agricultural-intelligence/regional-best-practices",
            params={
                "latitude": 200.0,  # Invalid latitude
                "longitude": -93.6319
            }
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_get_expert_recommendations_success(self, client, sample_intelligence_response):
        """Test successful expert recommendations retrieval."""
        with patch('api.agricultural_intelligence_routes.intelligence_service.get_location_intelligence') as mock_service:
            mock_service.return_value = sample_intelligence_response
            
            response = client.get(
                "/api/v1/agricultural-intelligence/expert-recommendations",
                params={
                    "latitude": 42.0308,
                    "longitude": -93.6319
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert isinstance(data, list)
            if data:
                recommendation = data[0]
                assert "recommendation_id" in recommendation
                assert "expert_name" in recommendation
                assert "expert_title" in recommendation
                assert "organization" in recommendation
                assert "expertise_area" in recommendation
                assert "recommendation" in recommendation
                assert "rationale" in recommendation
                assert "confidence_level" in recommendation
                assert "applicable_conditions" in recommendation
                assert "validation_status" in recommendation
    
    def test_get_expert_recommendations_invalid_coordinates(self, client):
        """Test expert recommendations with invalid coordinates."""
        response = client.get(
            "/api/v1/agricultural-intelligence/expert-recommendations",
            params={
                "latitude": 42.0308,
                "longitude": 200.0  # Invalid longitude
            }
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_get_peer_insights_success(self, client, sample_intelligence_response):
        """Test successful peer insights retrieval."""
        with patch('api.agricultural_intelligence_routes.intelligence_service.get_location_intelligence') as mock_service:
            mock_service.return_value = sample_intelligence_response
            
            response = client.get(
                "/api/v1/agricultural-intelligence/peer-insights",
                params={
                    "latitude": 42.0308,
                    "longitude": -93.6319
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert isinstance(data, list)
            if data:
                insight = data[0]
                assert "insight_id" in insight
                assert "farm_type" in insight
                assert "location_region" in insight
                assert "insight_type" in insight
                assert "title" in insight
                assert "description" in insight
                assert "practice_used" in insight
                assert "results" in insight
                assert "lessons_learned" in insight
                assert "recommendations" in insight
                assert "year" in insight
                assert "season" in insight
                assert "validation_status" in insight
                assert "peer_rating" in insight
    
    def test_get_peer_insights_with_radius(self, client, sample_intelligence_response):
        """Test peer insights with custom radius."""
        with patch('api.agricultural_intelligence_routes.intelligence_service.get_location_intelligence') as mock_service:
            mock_service.return_value = sample_intelligence_response
            
            response = client.get(
                "/api/v1/agricultural-intelligence/peer-insights",
                params={
                    "latitude": 42.0308,
                    "longitude": -93.6319,
                    "radius_km": 100.0
                }
            )
            
            assert response.status_code == 200
    
    def test_get_peer_insights_invalid_radius(self, client):
        """Test peer insights with invalid radius."""
        response = client.get(
            "/api/v1/agricultural-intelligence/peer-insights",
            params={
                "latitude": 42.0308,
                "longitude": -93.6319,
                "radius_km": 500.0  # Too large
            }
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_get_market_insights_success(self, client, sample_intelligence_response):
        """Test successful market insights retrieval."""
        with patch('api.agricultural_intelligence_routes.intelligence_service.get_location_intelligence') as mock_service:
            mock_service.return_value = sample_intelligence_response
            
            response = client.get(
                "/api/v1/agricultural-intelligence/market-insights",
                params={
                    "latitude": 42.0308,
                    "longitude": -93.6319
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert isinstance(data, list)
            if data:
                insight = data[0]
                assert "insight_id" in insight
                assert "market_type" in insight
                assert "crop_type" in insight
                assert "region" in insight
                assert "price_trend" in insight
                assert "demand_level" in insight
                assert "seasonal_patterns" in insight
                assert "competition_level" in insight
                assert "market_access" in insight
                assert "premium_opportunities" in insight
                assert "data_source" in insight
    
    def test_get_market_insights_with_crop_filter(self, client, sample_intelligence_response):
        """Test market insights with crop type filter."""
        with patch('api.agricultural_intelligence_routes.intelligence_service.get_location_intelligence') as mock_service:
            mock_service.return_value = sample_intelligence_response
            
            response = client.get(
                "/api/v1/agricultural-intelligence/market-insights",
                params={
                    "latitude": 42.0308,
                    "longitude": -93.6319,
                    "crop_type": "corn"
                }
            )
            
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_get_success_patterns_success(self, client, sample_intelligence_response):
        """Test successful success patterns retrieval."""
        with patch('api.agricultural_intelligence_routes.intelligence_service.get_location_intelligence') as mock_service:
            mock_service.return_value = sample_intelligence_response
            
            response = client.get(
                "/api/v1/agricultural-intelligence/success-patterns",
                params={
                    "latitude": 42.0308,
                    "longitude": -93.6319
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert isinstance(data, list)
            if data:
                pattern = data[0]
                assert "pattern_id" in pattern
                assert "pattern_name" in pattern
                assert "region" in pattern
                assert "crop_type" in pattern
                assert "success_factors" in pattern
                assert "common_practices" in pattern
                assert "average_yield" in pattern
                assert "profitability_metrics" in pattern
                assert "risk_factors" in pattern
                assert "mitigation_strategies" in pattern
                assert "farmer_count" in pattern
                assert "success_rate" in pattern
    
    def test_get_success_patterns_with_crop_filter(self, client, sample_intelligence_response):
        """Test success patterns with crop type filter."""
        with patch('api.agricultural_intelligence_routes.intelligence_service.get_location_intelligence') as mock_service:
            mock_service.return_value = sample_intelligence_response
            
            response = client.get(
                "/api/v1/agricultural-intelligence/success-patterns",
                params={
                    "latitude": 42.0308,
                    "longitude": -93.6319,
                    "crop_type": "corn"
                }
            )
            
            assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_get_intelligence_summary_success(self, client, sample_intelligence_response):
        """Test successful intelligence summary retrieval."""
        with patch('api.agricultural_intelligence_routes.intelligence_service.get_location_intelligence') as mock_service:
            mock_service.return_value = sample_intelligence_response
            
            response = client.get(
                "/api/v1/agricultural-intelligence/intelligence-summary",
                params={
                    "latitude": 42.0308,
                    "longitude": -93.6319
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            assert "intelligence_summary" in data
            assert "confidence_scores" in data
            assert "total_recommendations" in data
            assert "data_sources" in data
            assert "last_updated" in data
            assert "region" in data
            
            # Verify intelligence summary structure
            summary = data["intelligence_summary"]
            assert "region" in summary
            assert "total_recommendations" in summary
            assert "top_categories" in summary
            assert "key_insights" in summary
            assert "market_opportunities" in summary
            assert "risk_factors" in summary
            assert "success_indicators" in summary
            
            # Verify confidence scores structure
            scores = data["confidence_scores"]
            assert "regional_best_practices" in scores
            assert "expert_recommendations" in scores
            assert "peer_insights" in scores
            assert "overall" in scores
    
    def test_get_intelligence_summary_with_filters(self, client, sample_intelligence_response):
        """Test intelligence summary with filters."""
        with patch('api.agricultural_intelligence_routes.intelligence_service.get_location_intelligence') as mock_service:
            mock_service.return_value = sample_intelligence_response
            
            response = client.get(
                "/api/v1/agricultural-intelligence/intelligence-summary",
                params={
                    "latitude": 42.0308,
                    "longitude": -93.6319,
                    "crop_type": "corn",
                    "farm_size_acres": 500.0
                }
            )
            
            assert response.status_code == 200
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/v1/agricultural-intelligence/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["service"] == "agricultural-intelligence"
        assert data["version"] == "1.0"
        assert "features" in data
        assert isinstance(data["features"], list)
        
        expected_features = [
            "regional_best_practices",
            "expert_recommendations",
            "peer_insights",
            "market_insights",
            "success_patterns",
            "local_adaptations"
        ]
        
        for feature in expected_features:
            assert feature in data["features"]
    
    @pytest.mark.asyncio
    async def test_service_error_handling(self, client):
        """Test service error handling."""
        with patch('api.agricultural_intelligence_routes.intelligence_service.get_location_intelligence') as mock_service:
            mock_service.side_effect = Exception("Service error")
            
            response = client.post(
                "/api/v1/agricultural-intelligence/location-intelligence",
                json={
                    "latitude": 42.0308,
                    "longitude": -93.6319
                }
            )
            
            assert response.status_code == 500
            data = response.json()
            
            assert "error" in data
            assert data["error"]["error"] == "INTELLIGENCE_SERVICE_ERROR"
            assert "agricultural_context" in data["error"]
            assert "suggested_actions" in data["error"]
    
    def test_limit_parameters(self, client, sample_intelligence_response):
        """Test limit parameters for all endpoints."""
        with patch('api.agricultural_intelligence_routes.intelligence_service.get_location_intelligence') as mock_service:
            mock_service.return_value = sample_intelligence_response
            
            endpoints = [
                "/api/v1/agricultural-intelligence/regional-best-practices",
                "/api/v1/agricultural-intelligence/expert-recommendations",
                "/api/v1/agricultural-intelligence/peer-insights",
                "/api/v1/agricultural-intelligence/market-insights",
                "/api/v1/agricultural-intelligence/success-patterns"
            ]
            
            for endpoint in endpoints:
                response = client.get(
                    endpoint,
                    params={
                        "latitude": 42.0308,
                        "longitude": -93.6319,
                        "limit": 5
                    }
                )
                
                assert response.status_code == 200
    
    def test_invalid_limit_parameters(self, client):
        """Test invalid limit parameters."""
        endpoints = [
            "/api/v1/agricultural-intelligence/regional-best-practices",
            "/api/v1/agricultural-intelligence/expert-recommendations",
            "/api/v1/agricultural-intelligence/peer-insights",
            "/api/v1/agricultural-intelligence/market-insights",
            "/api/v1/agricultural-intelligence/success-patterns"
        ]
        
        for endpoint in endpoints:
            # Test limit too high
            response = client.get(
                endpoint,
                params={
                    "latitude": 42.0308,
                    "longitude": -93.6319,
                    "limit": 100  # Too high
                }
            )
            
            assert response.status_code == 422
            
            # Test limit too low
            response = client.get(
                endpoint,
                params={
                    "latitude": 42.0308,
                    "longitude": -93.6319,
                    "limit": 0  # Too low
                }
            )
            
            assert response.status_code == 422


class TestAgriculturalIntelligenceAPIIntegration:
    """Integration tests for agricultural intelligence API."""
    
    def test_api_documentation(self, client):
        """Test that API documentation is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_api_root_endpoint(self, client):
        """Test root endpoint includes agricultural intelligence."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "endpoints" in data
        assert "agricultural_intelligence" in data["endpoints"]
        assert data["endpoints"]["agricultural_intelligence"] == "/api/v1/agricultural-intelligence/"
        
        assert "agricultural_features" in data
        features = data["agricultural_features"]
        assert "Location-based agricultural intelligence and insights" in features
        assert "Regional best practices and recommendations" in features
        assert "Local expert recommendations and insights" in features
        assert "Peer farmer insights and experiences" in features
        assert "Market insights and opportunities" in features
        assert "Success patterns and regional adaptations" in features
        assert "Location-specific personalization and optimization" in features
    
    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.options("/api/v1/agricultural-intelligence/health")
        assert response.status_code == 200
        
        # Check for CORS headers
        headers = response.headers
        assert "access-control-allow-origin" in headers
        assert "access-control-allow-methods" in headers
        assert "access-control-allow-headers" in headers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])