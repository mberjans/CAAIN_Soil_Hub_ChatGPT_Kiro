"""
Test Location Integration Service
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

Comprehensive tests for location integration with recommendation engine.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from uuid import uuid4

# Import the services to test
from src.services.location_integration_service import (
    LocationIntegrationService,
    LocationIntegrationResult,
    LocationChangeNotification
)
from src.models.agricultural_models import LocationData, RecommendationRequest
from src.services.recommendation_engine import RecommendationEngine


class TestLocationIntegrationService:
    """Test suite for location integration service."""
    
    @pytest.fixture
    def location_service(self):
        """Create location integration service instance."""
        return LocationIntegrationService()
    
    @pytest.fixture
    def sample_location_data(self):
        """Create sample location data for testing."""
        return LocationData(
            latitude=42.0308,
            longitude=-93.6319,
            elevation_ft=1000,
            address="Ames, IA",
            state="Iowa",
            county="Story County"
        )
    
    @pytest.fixture
    def sample_recommendation_request(self, sample_location_data):
        """Create sample recommendation request for testing."""
        return RecommendationRequest(
            request_id=str(uuid4()),
            question_type="crop_selection",
            location=sample_location_data,
            soil_data=None,
            farm_profile=None
        )
    
    @pytest.mark.asyncio
    async def test_integrate_location_with_recommendation_success(self, location_service, sample_recommendation_request):
        """Test successful location integration with recommendation request."""
        
        with patch.object(location_service, '_ensure_location_data', return_value=sample_recommendation_request.location):
            with patch.object(location_service, '_validate_location', return_value={"valid": True}):
                with patch.object(location_service, '_enhance_location_data', return_value=sample_recommendation_request.location):
                    with patch.object(location_service, '_assess_agricultural_suitability', return_value="excellent"):
                        with patch.object(location_service, '_get_regional_adaptations', return_value=["Consider corn-soybean rotations"]):
                            
                            result = await location_service.integrate_location_with_recommendation(
                                request=sample_recommendation_request,
                                auto_detect_location=False,
                                validate_location=True
                            )
                            
                            assert result.success is True
                            assert result.enhanced_location is not None
                            assert result.agricultural_suitability == "excellent"
                            assert len(result.regional_adaptations) > 0
                            assert result.processing_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_integrate_location_with_recommendation_no_location(self, location_service, sample_recommendation_request):
        """Test location integration when no location data is available."""
        
        # Remove location from request
        sample_recommendation_request.location = None
        
        with patch.object(location_service, '_ensure_location_data', return_value=None):
            
            result = await location_service.integrate_location_with_recommendation(
                request=sample_recommendation_request,
                auto_detect_location=False,
                validate_location=True
            )
            
            assert result.success is False
            assert result.enhanced_location is None
            assert "No location data available" in result.warnings
            assert "Location data required" in result.errors
    
    @pytest.mark.asyncio
    async def test_auto_detect_location(self, location_service, sample_recommendation_request):
        """Test automatic location detection."""
        
        # Remove location from request
        sample_recommendation_request.location = None
        
        mock_detected_location = LocationData(
            latitude=41.8781,
            longitude=-87.6298,
            elevation_ft=600,
            address="Chicago, IL",
            state="Illinois",
            county="Cook County"
        )
        
        with patch.object(location_service.current_location_detection, 'detect_current_location', 
                         return_value=MagicMock(success=True, location=mock_detected_location)):
            with patch.object(location_service, '_validate_location', return_value={"valid": True}):
                with patch.object(location_service, '_enhance_location_data', return_value=mock_detected_location):
                    with patch.object(location_service, '_assess_agricultural_suitability', return_value="good"):
                        with patch.object(location_service, '_get_regional_adaptations', return_value=[]):
                            
                            result = await location_service.integrate_location_with_recommendation(
                                request=sample_recommendation_request,
                                auto_detect_location=True,
                                validate_location=True
                            )
                            
                            assert result.success is True
                            assert result.enhanced_location is not None
                            assert result.enhanced_location.latitude == 41.8781
                            assert result.enhanced_location.longitude == -87.6298
    
    @pytest.mark.asyncio
    async def test_assess_agricultural_suitability(self, location_service):
        """Test agricultural suitability assessment."""
        
        # Test excellent suitability (Midwest)
        midwest_location = LocationData(latitude=42.0308, longitude=-93.6319)
        suitability = await location_service._assess_agricultural_suitability(midwest_location)
        assert suitability == "excellent"
        
        # Test challenging suitability (High latitude)
        high_lat_location = LocationData(latitude=65.0, longitude=-150.0)
        suitability = await location_service._assess_agricultural_suitability(high_lat_location)
        assert suitability == "challenging"
        
        # Test limited suitability (Polar region)
        polar_location = LocationData(latitude=75.0, longitude=-150.0)
        suitability = await location_service._assess_agricultural_suitability(polar_location)
        assert suitability == "limited"
    
    @pytest.mark.asyncio
    async def test_get_regional_adaptations(self, location_service):
        """Test regional adaptations retrieval."""
        
        # Test Midwest adaptations
        midwest_location = LocationData(
            latitude=42.0308, 
            longitude=-93.6319,
            climate_zone="5a"
        )
        adaptations = await location_service._get_regional_adaptations(midwest_location)
        assert len(adaptations) > 0
        assert any("corn-soybean" in adaptation.lower() for adaptation in adaptations)
        
        # Test Southeast adaptations
        southeast_location = LocationData(
            latitude=35.0, 
            longitude=-85.0,
            climate_zone="7a"
        )
        adaptations = await location_service._get_regional_adaptations(southeast_location)
        assert len(adaptations) > 0
        assert any("warm-season" in adaptation.lower() for adaptation in adaptations)
    
    @pytest.mark.asyncio
    async def test_notify_location_change(self, location_service):
        """Test location change notification."""
        
        old_location = LocationData(latitude=42.0308, longitude=-93.6319)
        new_location = LocationData(latitude=41.8781, longitude=-87.6298)
        
        with patch.object(location_service, '_assess_location_change_impact', 
                         return_value={"climate_zone_changed": True, "impact_severity": "high"}):
            
            notification = await location_service.notify_location_change(
                user_id="test_user",
                old_location=old_location,
                new_location=new_location,
                affected_recommendations=["crop_selection", "fertilizer_strategy"]
            )
            
            assert notification.user_id == "test_user"
            assert notification.old_location.latitude == 42.0308
            assert notification.new_location.latitude == 41.8781
            assert len(notification.affected_recommendations) == 2
            assert notification.impact_assessment["impact_severity"] == "high"
    
    def test_calculate_distance(self, location_service):
        """Test distance calculation between coordinates."""
        
        # Test distance between Ames, IA and Chicago, IL
        distance = location_service._calculate_distance(42.0308, -93.6319, 41.8781, -87.6298)
        assert 300 < distance < 400  # Should be approximately 350 km
        
        # Test distance between same coordinates
        distance = location_service._calculate_distance(42.0308, -93.6319, 42.0308, -93.6319)
        assert distance == 0.0
    
    @pytest.mark.asyncio
    async def test_get_location_based_recommendations(self, location_service, sample_location_data):
        """Test location-based recommendations retrieval."""
        
        with patch.object(location_service, '_get_regional_adaptations', 
                         return_value=["Consider corn-soybean rotations"]):
            with patch.object(location_service, '_assess_agricultural_suitability', 
                             return_value="excellent"):
                
                recommendations = await location_service.get_location_based_recommendations(
                    location_data=sample_location_data,
                    recommendation_type="crop_selection"
                )
                
                assert "location_specific" in recommendations
                assert "recommendations" in recommendations
                assert recommendations["location_specific"]["agricultural_suitability"] == "excellent"
                assert len(recommendations["recommendations"]["crop_selection"]) > 0


class TestRecommendationEngineLocationIntegration:
    """Test suite for recommendation engine with location integration."""
    
    @pytest.fixture
    def recommendation_engine(self):
        """Create recommendation engine instance."""
        return RecommendationEngine()
    
    @pytest.fixture
    def sample_request_with_location(self):
        """Create sample request with location data."""
        location_data = LocationData(
            latitude=42.0308,
            longitude=-93.6319,
            elevation_ft=1000,
            address="Ames, IA",
            state="Iowa",
            county="Story County"
        )
        
        return RecommendationRequest(
            request_id=str(uuid4()),
            question_type="crop_selection",
            location=location_data,
            soil_data=None,
            farm_profile=None
        )
    
    @pytest.mark.asyncio
    async def test_recommendation_engine_with_location_integration(self, recommendation_engine, sample_request_with_location):
        """Test recommendation engine with location integration."""
        
        with patch('src.services.recommendation_engine.location_integration_service') as mock_location_service:
            # Mock successful location integration
            mock_integration_result = LocationIntegrationResult(
                success=True,
                enhanced_location=sample_request_with_location.location,
                validation_result={"valid": True},
                agricultural_suitability="excellent",
                regional_adaptations=["Consider corn-soybean rotations"],
                warnings=[],
                errors=[],
                processing_time_ms=100.0
            )
            
            mock_location_service.integrate_location_with_recommendation.return_value = mock_integration_result
            
            # Mock the recommendation generation
            with patch.object(recommendation_engine, '_get_rule_based_recommendations', 
                             return_value=[]):
                
                response = await recommendation_engine.generate_recommendations(sample_request_with_location)
                
                # Verify location integration was called
                mock_location_service.integrate_location_with_recommendation.assert_called_once()
                
                # Verify response structure
                assert response.request_id == sample_request_with_location.request_id
                assert response.question_type == sample_request_with_location.question_type
    
    @pytest.mark.asyncio
    async def test_apply_regional_adaptations(self, recommendation_engine):
        """Test applying regional adaptations to recommendations."""
        
        from src.models.agricultural_models import RecommendationItem
        
        # Create sample recommendations
        recommendations = [
            RecommendationItem(
                recommendation_id=str(uuid4()),
                title="Corn Variety Selection",
                description="Select appropriate corn varieties",
                confidence=0.8,
                implementation_steps=["Step 1", "Step 2"]
            )
        ]
        
        regional_adaptations = ["Consider corn-soybean rotations", "Plan for variable weather patterns"]
        
        enhanced_recommendations = recommendation_engine._apply_regional_adaptations(
            recommendations, regional_adaptations
        )
        
        assert len(enhanced_recommendations) == 1
        assert "Regional considerations" in enhanced_recommendations[0].description
        assert len(enhanced_recommendations[0].implementation_steps) > 2
    
    @pytest.mark.asyncio
    async def test_apply_agricultural_suitability_adjustments(self, recommendation_engine):
        """Test applying agricultural suitability adjustments to recommendations."""
        
        from src.models.agricultural_models import RecommendationItem
        
        # Create sample recommendations
        recommendations = [
            RecommendationItem(
                recommendation_id=str(uuid4()),
                title="Corn Variety Selection",
                description="Select appropriate corn varieties",
                confidence=0.8,
                implementation_steps=["Step 1", "Step 2"]
            )
        ]
        
        # Test excellent suitability
        enhanced_recommendations = recommendation_engine._apply_agricultural_suitability_adjustments(
            recommendations, "excellent"
        )
        
        assert len(enhanced_recommendations) == 1
        assert enhanced_recommendations[0].confidence > 0.8  # Should be boosted
        assert "excellent agricultural potential" in enhanced_recommendations[0].description
        
        # Test challenging suitability
        enhanced_recommendations = recommendation_engine._apply_agricultural_suitability_adjustments(
            recommendations, "challenging"
        )
        
        assert len(enhanced_recommendations) == 1
        assert enhanced_recommendations[0].confidence < 0.8  # Should be reduced
        assert "challenging agricultural conditions" in enhanced_recommendations[0].description


class TestLocationIntegrationPerformance:
    """Performance tests for location integration."""
    
    @pytest.mark.asyncio
    async def test_location_integration_performance(self):
        """Test that location integration meets performance requirements."""
        
        location_service = LocationIntegrationService()
        
        location_data = LocationData(
            latitude=42.0308,
            longitude=-93.6319,
            elevation_ft=1000,
            address="Ames, IA",
            state="Iowa",
            county="Story County"
        )
        
        request = RecommendationRequest(
            request_id=str(uuid4()),
            question_type="crop_selection",
            location=location_data,
            soil_data=None,
            farm_profile=None
        )
        
        start_time = datetime.now()
        
        with patch.object(location_service, '_ensure_location_data', return_value=location_data):
            with patch.object(location_service, '_validate_location', return_value={"valid": True}):
                with patch.object(location_service, '_enhance_location_data', return_value=location_data):
                    with patch.object(location_service, '_assess_agricultural_suitability', return_value="excellent"):
                        with patch.object(location_service, '_get_regional_adaptations', return_value=[]):
                            
                            result = await location_service.integrate_location_with_recommendation(
                                request=request,
                                auto_detect_location=False,
                                validate_location=True
                            )
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Should complete within 1 second as specified in requirements
        assert processing_time < 1.0, f"Location integration took {processing_time}s, exceeds 1s requirement"
        assert result.success is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])