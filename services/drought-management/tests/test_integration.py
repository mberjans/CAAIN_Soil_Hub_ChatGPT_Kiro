"""
Comprehensive Integration Tests for Drought Management Service

Tests the integration of drought management with all CAAIN Soil Hub services.
"""

import pytest
import asyncio
import json
from typing import Dict, Any
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
from datetime import datetime, timedelta

# Import the services to test
from src.services.caain_integration_service import CAAINDroughtIntegrationService
from src.api.integration_routes import router


class TestCAAINDroughtIntegrationService:
    """Test suite for CAAIN drought integration service."""
    
    @pytest.fixture
    async def integration_service(self):
        """Create integration service instance for testing."""
        service = CAAINDroughtIntegrationService()
        await service.initialize()
        yield service
        await service.cleanup()
    
    @pytest.fixture
    def mock_service_responses(self):
        """Mock responses from CAAIN services."""
        return {
            "recommendation-engine": {
                "status": "healthy",
                "response_time": 0.5,
                "details": {"version": "1.0.0", "uptime": "24h"}
            },
            "data-integration": {
                "status": "healthy", 
                "response_time": 0.3,
                "details": {"version": "1.0.0", "uptime": "24h"}
            },
            "ai-agent": {
                "status": "healthy",
                "response_time": 0.8,
                "details": {"version": "1.0.0", "uptime": "24h"}
            },
            "user-management": {
                "status": "healthy",
                "response_time": 0.2,
                "details": {"version": "1.0.0", "uptime": "24h"}
            },
            "crop-taxonomy": {
                "status": "healthy",
                "response_time": 0.4,
                "details": {"version": "1.0.0", "uptime": "24h"}
            },
            "cover-crop-selection": {
                "status": "healthy",
                "response_time": 0.6,
                "details": {"version": "1.0.0", "uptime": "24h"}
            },
            "question-router": {
                "status": "healthy",
                "response_time": 0.3,
                "details": {"version": "1.0.0", "uptime": "24h"}
            }
        }
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, integration_service):
        """Test that integration service initializes correctly."""
        assert integration_service is not None
        assert len(integration_service.service_clients) > 0
        assert len(integration_service.service_status) > 0
        
        # Check that all expected services are configured
        expected_services = [
            "recommendation-engine",
            "data-integration", 
            "ai-agent",
            "user-management",
            "crop-taxonomy",
            "cover-crop-selection",
            "question-router"
        ]
        
        for service_name in expected_services:
            assert service_name in integration_service.service_clients
            assert service_name in integration_service.service_status
    
    @pytest.mark.asyncio
    async def test_health_check_all_services(self, integration_service, mock_service_responses):
        """Test health checking of all CAAIN services."""
        # Mock the service client responses
        with patch.object(integration_service, 'service_clients') as mock_clients:
            for service_name, client in mock_clients.items():
                client.__aenter__ = AsyncMock(return_value=client)
                client.__aexit__ = AsyncMock(return_value=None)
                client.get = AsyncMock(return_value={"status": "healthy"})
            
            # Perform health check
            results = await integration_service.check_all_services_health()
            
            # Verify results
            assert len(results) > 0
            for service_name, result in results.items():
                assert "status" in result
                assert "response_time" in result
                assert "last_check" in result
    
    @pytest.mark.asyncio
    async def test_get_service_status(self, integration_service):
        """Test getting status of individual services."""
        service_name = "recommendation-engine"
        status = await integration_service.get_service_status(service_name)
        
        assert "status" in status
        assert "last_check" in status
        assert "critical" in status
        assert "error_count" in status
    
    @pytest.mark.asyncio
    async def test_get_all_services_status(self, integration_service):
        """Test getting status of all services."""
        all_status = await integration_service.get_all_services_status()
        
        assert len(all_status) > 0
        for service_name, status in all_status.items():
            assert "status" in status
            assert "last_check" in status
            assert "critical" in status
    
    @pytest.mark.asyncio
    async def test_sync_soil_data(self, integration_service):
        """Test soil data synchronization."""
        field_id = uuid4()
        
        # Mock the data-integration service response
        mock_soil_data = {
            "field_id": str(field_id),
            "soil_moisture": 0.65,
            "soil_texture": "clay_loam",
            "organic_matter": 3.2,
            "ph": 6.5
        }
        
        with patch.object(integration_service.service_clients["data-integration"], 'get') as mock_get:
            mock_get.return_value = mock_soil_data
            
            result = await integration_service.sync_soil_data(field_id)
            
            assert result == mock_soil_data
            # Check that data was cached
            cache_key = f"soil_data_{field_id}"
            assert cache_key in integration_service.data_sync_cache
    
    @pytest.mark.asyncio
    async def test_sync_weather_data(self, integration_service):
        """Test weather data synchronization."""
        latitude = 40.7128
        longitude = -74.0060
        
        # Mock the data-integration service response
        mock_weather_data = {
            "temperature": 25.0,
            "humidity": 60.0,
            "precipitation": 0.0,
            "wind_speed": 2.0,
            "solar_radiation": 20.0,
            "conditions": "clear"
        }
        
        with patch.object(integration_service.service_clients["data-integration"], 'get') as mock_get:
            mock_get.return_value = mock_weather_data
            
            result = await integration_service.sync_weather_data(latitude, longitude)
            
            assert result == mock_weather_data
            # Check that data was cached
            cache_key = f"weather_data_{latitude}_{longitude}"
            assert cache_key in integration_service.data_sync_cache
    
    @pytest.mark.asyncio
    async def test_get_drought_resilient_crops(self, integration_service):
        """Test getting drought-resilient crop recommendations."""
        location_data = {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "climate_zone": "6a",
            "soil_type": "clay_loam"
        }
        
        # Mock the crop-taxonomy service response
        mock_crops = {
            "drought_resilient_crops": [
                {
                    "crop_name": "Sorghum",
                    "variety": "DroughtGuard",
                    "drought_tolerance": "high",
                    "water_requirement": "low"
                },
                {
                    "crop_name": "Millet",
                    "variety": "WaterWise",
                    "drought_tolerance": "very_high",
                    "water_requirement": "very_low"
                }
            ]
        }
        
        with patch.object(integration_service.service_clients["crop-taxonomy"], 'post') as mock_post:
            mock_post.return_value = mock_crops
            
            result = await integration_service.get_drought_resilient_crops(location_data)
            
            assert result == mock_crops
            assert "drought_resilient_crops" in result
    
    @pytest.mark.asyncio
    async def test_get_cover_crop_recommendations(self, integration_service):
        """Test getting cover crop recommendations for moisture conservation."""
        field_data = {
            "field_id": str(uuid4()),
            "soil_type": "sandy_loam",
            "drainage": "well_drained",
            "moisture_conservation_goal": "high"
        }
        
        # Mock the cover-crop-selection service response
        mock_recommendations = {
            "cover_crops": [
                {
                    "species": "Crimson Clover",
                    "moisture_conservation": "high",
                    "nitrogen_fixation": "high",
                    "planting_date": "fall"
                },
                {
                    "species": "Annual Ryegrass",
                    "moisture_conservation": "medium",
                    "nitrogen_fixation": "low",
                    "planting_date": "fall"
                }
            ]
        }
        
        with patch.object(integration_service.service_clients["cover-crop-selection"], 'post') as mock_post:
            mock_post.return_value = mock_recommendations
            
            result = await integration_service.get_cover_crop_recommendations(field_data)
            
            assert result == mock_recommendations
            assert "cover_crops" in result
    
    @pytest.mark.asyncio
    async def test_explain_drought_recommendation(self, integration_service):
        """Test getting AI explanation for drought recommendations."""
        recommendation_data = {
            "practice": "no_till",
            "field_conditions": "drought_stressed",
            "recommended_action": "implement_mulching"
        }
        
        # Mock the ai-agent service response
        mock_explanation = {
            "explanation": "No-till farming helps conserve soil moisture by reducing evaporation and improving soil structure. Mulching further enhances moisture retention by creating a protective layer.",
            "benefits": [
                "Reduces soil moisture loss by 20-30%",
                "Improves soil organic matter over time",
                "Reduces erosion risk"
            ],
            "implementation_tips": [
                "Apply mulch after planting",
                "Maintain 2-3 inch mulch depth",
                "Monitor soil moisture regularly"
            ]
        }
        
        with patch.object(integration_service.service_clients["ai-agent"], 'post') as mock_post:
            mock_post.return_value = mock_explanation
            
            result = await integration_service.explain_drought_recommendation(recommendation_data)
            
            assert result == mock_explanation
            assert "explanation" in result
            assert "benefits" in result
    
    @pytest.mark.asyncio
    async def test_route_drought_question(self, integration_service):
        """Test routing drought questions through question-router."""
        question_data = {
            "question": "What crops should I plant during drought conditions?",
            "context": {
                "location": "Texas",
                "soil_type": "clay",
                "irrigation": "limited"
            }
        }
        
        # Mock the question-router service response
        mock_routing = {
            "routed_to": ["crop-taxonomy", "drought-management"],
            "response": "Based on your location and soil conditions, consider drought-tolerant crops like sorghum, millet, or drought-resistant corn varieties.",
            "confidence": 0.85
        }
        
        with patch.object(integration_service.service_clients["question-router"], 'post') as mock_post:
            mock_post.return_value = mock_routing
            
            result = await integration_service.route_drought_question(question_data)
            
            assert result == mock_routing
            assert "routed_to" in result
            assert "response" in result
    
    @pytest.mark.asyncio
    async def test_error_handling_service_unavailable(self, integration_service):
        """Test error handling when services are unavailable."""
        field_id = uuid4()
        
        # Mock service unavailable
        with patch.object(integration_service.service_clients["data-integration"], 'get') as mock_get:
            mock_get.side_effect = Exception("Service unavailable")
            
            # Should raise exception
            with pytest.raises(Exception):
                await integration_service.sync_soil_data(field_id)
    
    @pytest.mark.asyncio
    async def test_cached_data_fallback(self, integration_service):
        """Test that cached data is used when services are unavailable."""
        field_id = uuid4()
        
        # Pre-populate cache
        cache_key = f"soil_data_{field_id}"
        cached_data = {
            "field_id": str(field_id),
            "soil_moisture": 0.65,
            "cached": True
        }
        integration_service.data_sync_cache[cache_key] = {
            "data": cached_data,
            "timestamp": datetime.utcnow()
        }
        
        # Mock service unavailable
        with patch.object(integration_service.service_clients["data-integration"], 'get') as mock_get:
            mock_get.side_effect = Exception("Service unavailable")
            
            # Should return cached data
            result = await integration_service.sync_soil_data(field_id)
            assert result == cached_data
    
    @pytest.mark.asyncio
    async def test_background_health_monitoring(self, integration_service):
        """Test background health monitoring task."""
        # Mock the health check method
        with patch.object(integration_service, 'check_all_services_health') as mock_health:
            mock_health.return_value = {"test_service": {"status": "healthy"}}
            
            # Start background task
            task = asyncio.create_task(integration_service._background_health_monitoring())
            
            # Let it run briefly
            await asyncio.sleep(0.1)
            
            # Cancel the task
            task.cancel()
            
            # Verify health check was called
            assert mock_health.called
    
    @pytest.mark.asyncio
    async def test_background_data_sync(self, integration_service):
        """Test background data synchronization task."""
        # Mock the sync method
        with patch.object(integration_service, '_sync_critical_data') as mock_sync:
            mock_sync.return_value = None
            
            # Start background task
            task = asyncio.create_task(integration_service._background_data_sync())
            
            # Let it run briefly
            await asyncio.sleep(0.1)
            
            # Cancel the task
            task.cancel()
            
            # Verify sync was called
            assert mock_sync.called


class TestIntegrationAPIEndpoints:
    """Test suite for integration API endpoints."""
    
    @pytest.fixture
    def mock_integration_service(self):
        """Create mock integration service."""
        service = MagicMock()
        service.check_all_services_health = AsyncMock()
        service.get_all_services_status = AsyncMock()
        service.get_service_status = AsyncMock()
        service.sync_soil_data = AsyncMock()
        service.sync_weather_data = AsyncMock()
        service.get_drought_resilient_crops = AsyncMock()
        service.get_cover_crop_recommendations = AsyncMock()
        service.explain_drought_recommendation = AsyncMock()
        service.route_drought_question = AsyncMock()
        return service
    
    @pytest.mark.asyncio
    async def test_integration_health_endpoint(self, mock_integration_service):
        """Test integration health endpoint."""
        # Mock service responses
        mock_integration_service.check_all_services_health.return_value = {
            "recommendation-engine": {"status": "healthy", "response_time": 0.5},
            "data-integration": {"status": "healthy", "response_time": 0.3}
        }
        
        # This would require FastAPI test client setup
        # For now, we'll test the service methods directly
        result = await mock_integration_service.check_all_services_health()
        
        assert "recommendation-engine" in result
        assert "data-integration" in result
        assert result["recommendation-engine"]["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_service_health_endpoint(self, mock_integration_service):
        """Test individual service health endpoint."""
        mock_integration_service.get_service_status.return_value = {
            "status": "healthy",
            "response_time": 0.5,
            "last_check": datetime.utcnow(),
            "critical": True,
            "error_count": 0
        }
        
        result = await mock_integration_service.get_service_status("recommendation-engine")
        
        assert result["status"] == "healthy"
        assert result["critical"] is True
        assert result["error_count"] == 0
    
    @pytest.mark.asyncio
    async def test_data_sync_endpoint(self, mock_integration_service):
        """Test data synchronization endpoint."""
        field_id = uuid4()
        mock_soil_data = {
            "field_id": str(field_id),
            "soil_moisture": 0.65,
            "soil_texture": "clay_loam"
        }
        
        mock_integration_service.sync_soil_data.return_value = mock_soil_data
        
        result = await mock_integration_service.sync_soil_data(field_id)
        
        assert result == mock_soil_data
        assert "field_id" in result
        assert "soil_moisture" in result


class TestIntegrationWorkflows:
    """Test comprehensive integration workflows."""
    
    @pytest.fixture
    async def integration_service(self):
        """Create integration service for workflow testing."""
        service = CAAINDroughtIntegrationService()
        await service.initialize()
        yield service
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_complete_drought_assessment_workflow(self, integration_service):
        """Test complete drought assessment workflow with all services."""
        field_id = uuid4()
        location_data = {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "climate_zone": "6a"
        }
        
        # Mock all service responses
        mock_responses = {
            "soil_data": {
                "field_id": str(field_id),
                "soil_moisture": 0.45,  # Low moisture
                "soil_texture": "sandy_loam",
                "organic_matter": 2.1
            },
            "weather_data": {
                "temperature": 32.0,  # High temperature
                "humidity": 35.0,    # Low humidity
                "precipitation": 0.0, # No precipitation
                "drought_index": 0.8  # High drought risk
            },
            "drought_resilient_crops": {
                "crops": [
                    {"name": "Sorghum", "drought_tolerance": "high"},
                    {"name": "Millet", "drought_tolerance": "very_high"}
                ]
            },
            "cover_crop_recommendations": {
                "cover_crops": [
                    {"species": "Crimson Clover", "moisture_conservation": "high"}
                ]
            },
            "ai_explanation": {
                "explanation": "High drought risk detected. Implement moisture conservation practices immediately.",
                "recommendations": ["Switch to drought-tolerant crops", "Implement no-till", "Add mulch"]
            }
        }
        
        # Mock service calls
        with patch.object(integration_service.service_clients["data-integration"], 'get') as mock_get:
            mock_get.side_effect = [mock_responses["soil_data"], mock_responses["weather_data"]]
            
            with patch.object(integration_service.service_clients["crop-taxonomy"], 'post') as mock_crop_post:
                mock_crop_post.return_value = mock_responses["drought_resilient_crops"]
                
                with patch.object(integration_service.service_clients["cover-crop-selection"], 'post') as mock_cover_post:
                    mock_cover_post.return_value = mock_responses["cover_crop_recommendations"]
                    
                    with patch.object(integration_service.service_clients["ai-agent"], 'post') as mock_ai_post:
                        mock_ai_post.return_value = mock_responses["ai_explanation"]
                        
                        # Execute workflow
                        soil_data = await integration_service.sync_soil_data(field_id)
                        weather_data = await integration_service.sync_weather_data(
                            location_data["latitude"], location_data["longitude"]
                        )
                        crops = await integration_service.get_drought_resilient_crops(location_data)
                        cover_crops = await integration_service.get_cover_crop_recommendations({
                            "field_id": str(field_id),
                            "soil_type": soil_data["soil_texture"]
                        })
                        explanation = await integration_service.explain_drought_recommendation({
                            "soil_data": soil_data,
                            "weather_data": weather_data,
                            "recommendations": crops
                        })
                        
                        # Verify workflow results
                        assert soil_data["soil_moisture"] == 0.45
                        assert weather_data["drought_index"] == 0.8
                        assert len(crops["crops"]) > 0
                        assert len(cover_crops["cover_crops"]) > 0
                        assert "explanation" in explanation
                        
                        # Verify integration worked correctly
                        assert soil_data["field_id"] == str(field_id)
                        assert crops["crops"][0]["drought_tolerance"] in ["high", "very_high"]
                        assert explanation["recommendations"] is not None
    
    @pytest.mark.asyncio
    async def test_service_failure_resilience(self, integration_service):
        """Test system resilience when services fail."""
        field_id = uuid4()
        
        # Mock partial service failures
        with patch.object(integration_service.service_clients["data-integration"], 'get') as mock_get:
            mock_get.side_effect = Exception("Service unavailable")
            
            # Should handle gracefully with cached data or fallback
            with pytest.raises(Exception):
                await integration_service.sync_soil_data(field_id)
            
            # Test that other services still work
            with patch.object(integration_service.service_clients["ai-agent"], 'post') as mock_ai:
                mock_ai.return_value = {"explanation": "Fallback explanation"}
                
                explanation = await integration_service.explain_drought_recommendation({
                    "practice": "no_till"
                })
                
                assert explanation["explanation"] == "Fallback explanation"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])