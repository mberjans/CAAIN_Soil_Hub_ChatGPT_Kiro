"""
Comprehensive Integration Tests for CAAIN Fertilizer Application Service

Tests cross-service communication, data synchronization, and system integration.
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any

from src.services.caain_integration_service import CAAINFertilizerIntegrationService
from src.api.integration_routes import router


class TestCAAINFertilizerIntegrationService:
    """Test suite for CAAIN fertilizer integration service."""
    
    @pytest.fixture
    def integration_service(self):
        """Create integration service instance for testing."""
        return CAAINFertilizerIntegrationService()
    
    @pytest.fixture
    def mock_service_client(self):
        """Mock service client for testing."""
        client = AsyncMock()
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=None)
        client.health_check = AsyncMock(return_value=True)
        client.get = AsyncMock()
        client.post = AsyncMock()
        return client
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, integration_service):
        """Test that integration service initializes correctly."""
        assert integration_service is not None
        assert len(integration_service.service_clients) > 0
        assert len(integration_service.integration_config) > 0
        assert "recommendation-engine" in integration_service.integration_config
        assert "data-integration" in integration_service.integration_config
        assert "ai-agent" in integration_service.integration_config
    
    @pytest.mark.asyncio
    async def test_service_health_check_success(self, integration_service, mock_service_client):
        """Test successful service health check."""
        mock_service_client.health_check.return_value = True
        
        with patch.object(integration_service, 'service_clients', {
            "test-service": mock_service_client
        }):
            result = await integration_service.check_service_health("test-service")
            
            assert result["status"] == "healthy"
            assert "response_time" in result
            assert "last_check" in result
    
    @pytest.mark.asyncio
    async def test_service_health_check_failure(self, integration_service, mock_service_client):
        """Test service health check failure handling."""
        mock_service_client.health_check.side_effect = Exception("Connection failed")
        
        with patch.object(integration_service, 'service_clients', {
            "test-service": mock_service_client
        }):
            result = await integration_service.check_service_health("test-service")
            
            assert result["status"] == "error"
            assert "error" in result
            assert "error_count" in result
    
    @pytest.mark.asyncio
    async def test_get_soil_data_success(self, integration_service, mock_service_client):
        """Test successful soil data retrieval."""
        mock_response = {
            "field_id": "test-field",
            "soil_type": "clay_loam",
            "ph": 6.5,
            "organic_matter": 3.2,
            "nutrients": {
                "nitrogen": 45,
                "phosphorus": 25,
                "potassium": 180
            }
        }
        mock_service_client.get.return_value = mock_response
        
        with patch.object(integration_service, 'service_clients', {
            "data-integration": mock_service_client
        }):
            result = await integration_service.get_soil_data("test-field", "test-user")
            
            assert result == mock_response
            mock_service_client.get.assert_called_once_with(
                "/api/v1/soil/characteristics",
                params={"field_id": "test-field", "user_id": "test-user"}
            )
    
    @pytest.mark.asyncio
    async def test_get_soil_data_failure(self, integration_service, mock_service_client):
        """Test soil data retrieval failure handling."""
        mock_service_client.get.side_effect = Exception("Service unavailable")
        
        with patch.object(integration_service, 'service_clients', {
            "data-integration": mock_service_client
        }):
            result = await integration_service.get_soil_data("test-field", "test-user")
            
            assert result["error"] == "Service unavailable"
            assert result["status"] == "failed"
    
    @pytest.mark.asyncio
    async def test_get_fertilizer_prices_success(self, integration_service, mock_service_client):
        """Test successful fertilizer price retrieval."""
        mock_response = {
            "prices": [
                {"fertilizer_type": "urea", "price_per_ton": 450.0, "unit": "ton"},
                {"fertilizer_type": "dap", "price_per_ton": 520.0, "unit": "ton"}
            ],
            "region": "midwest",
            "last_updated": datetime.utcnow().isoformat()
        }
        mock_service_client.get.return_value = mock_response
        
        with patch.object(integration_service, 'service_clients', {
            "data-integration": mock_service_client
        }):
            result = await integration_service.get_fertilizer_prices(["urea", "dap"], "midwest")
            
            assert result == mock_response
            mock_service_client.get.assert_called_once_with(
                "/api/v1/market/fertilizer-prices",
                params={"fertilizer_types": ["urea", "dap"], "region": "midwest"}
            )
    
    @pytest.mark.asyncio
    async def test_get_weather_data_success(self, integration_service, mock_service_client):
        """Test successful weather data retrieval."""
        mock_response = {
            "temperature_celsius": 22.5,
            "humidity_percent": 65,
            "precipitation_mm": 0.0,
            "wind_speed_kmh": 12.0,
            "conditions": "clear"
        }
        mock_service_client.get.return_value = mock_response
        
        with patch.object(integration_service, 'service_clients', {
            "data-integration": mock_service_client
        }):
            result = await integration_service.get_weather_data(40.0, -95.0)
            
            assert result == mock_response
            mock_service_client.get.assert_called_once_with(
                "/api/v1/weather/current",
                params={"latitude": 40.0, "longitude": -95.0}
            )
    
    @pytest.mark.asyncio
    async def test_get_crop_recommendations_success(self, integration_service, mock_service_client):
        """Test successful crop recommendations retrieval."""
        mock_response = {
            "recommendations": [
                {
                    "crop": "corn",
                    "variety": "Pioneer P1234",
                    "yield_potential": 180,
                    "maturity_days": 110
                }
            ],
            "confidence": 0.85
        }
        mock_service_client.post.return_value = mock_response
        
        location_data = {"latitude": 40.0, "longitude": -95.0}
        soil_data = {"ph": 6.5, "organic_matter": 3.2}
        
        with patch.object(integration_service, 'service_clients', {
            "recommendation-engine": mock_service_client
        }):
            result = await integration_service.get_crop_recommendations(location_data, soil_data)
            
            assert result == mock_response
            mock_service_client.post.assert_called_once_with(
                "/api/v1/recommendations/crop-varieties",
                data={"location": location_data, "soil_data": soil_data}
            )
    
    @pytest.mark.asyncio
    async def test_explain_fertilizer_recommendation_success(self, integration_service, mock_service_client):
        """Test successful AI explanation retrieval."""
        mock_response = {
            "explanation": "Based on your soil analysis, broadcast application is recommended because...",
            "confidence": 0.92,
            "key_factors": ["soil_type", "field_size", "equipment_availability"]
        }
        mock_service_client.post.return_value = mock_response
        
        recommendation_data = {"method": "broadcast", "fertilizer": "urea"}
        user_context = {"experience_level": "intermediate", "farm_size": "large"}
        
        with patch.object(integration_service, 'service_clients', {
            "ai-agent": mock_service_client
        }):
            result = await integration_service.explain_fertilizer_recommendation(
                recommendation_data, user_context
            )
            
            assert result == mock_response
            mock_service_client.post.assert_called_once_with(
                "/api/v1/ai/fertilizer/explain",
                data={"recommendation": recommendation_data, "context": user_context}
            )
    
    @pytest.mark.asyncio
    async def test_sync_fertilizer_data_success(self, integration_service):
        """Test successful fertilizer data synchronization."""
        mock_soil_data = {"ph": 6.5, "nutrients": {"N": 45}}
        mock_weather_data = {"temperature": 22.5, "humidity": 65}
        
        with patch.object(integration_service, 'get_soil_data', return_value=mock_soil_data):
            with patch.object(integration_service, 'get_weather_data', return_value=mock_weather_data):
                result = await integration_service.sync_fertilizer_data("test-field", "test-user")
                
                assert result["field_id"] == "test-field"
                assert result["user_id"] == "test-user"
                assert result["soil_data"] == mock_soil_data
                assert result["weather_data"] == mock_weather_data
                assert result["status"] == "success"
                assert "sync_timestamp" in result
    
    @pytest.mark.asyncio
    async def test_validate_fertilizer_recommendation_success(self, integration_service):
        """Test successful recommendation validation."""
        recommendation = {
            "id": "rec-123",
            "field_id": "field-456",
            "user_id": "user-789",
            "location": {"latitude": 40.0, "longitude": -95.0}
        }
        
        mock_soil_data = {"ph": 6.5, "status": "valid"}
        mock_weather_data = {"temperature": 22.5, "status": "valid"}
        
        with patch.object(integration_service, 'get_soil_data', return_value=mock_soil_data):
            with patch.object(integration_service, 'get_weather_data', return_value=mock_weather_data):
                result = await integration_service.validate_fertilizer_recommendation(recommendation)
                
                assert result["recommendation_id"] == "rec-123"
                assert result["overall_status"] == "valid"
                assert "validations" in result
                assert "soil_data" in result["validations"]
                assert "weather_data" in result["validations"]
    
    @pytest.mark.asyncio
    async def test_validate_fertilizer_recommendation_invalid(self, integration_service):
        """Test recommendation validation with invalid data."""
        recommendation = {
            "id": "rec-123",
            "field_id": "field-456",
            "user_id": "user-789",
            "location": {"latitude": 40.0, "longitude": -95.0}
        }
        
        mock_soil_data = {"error": "Service unavailable", "status": "invalid"}
        mock_weather_data = {"temperature": 22.5, "status": "valid"}
        
        with patch.object(integration_service, 'get_soil_data', return_value=mock_soil_data):
            with patch.object(integration_service, 'get_weather_data', return_value=mock_weather_data):
                result = await integration_service.validate_fertilizer_recommendation(recommendation)
                
                assert result["recommendation_id"] == "rec-123"
                assert result["overall_status"] == "invalid"
                assert result["validations"]["soil_data"]["status"] == "invalid"
                assert result["validations"]["weather_data"]["status"] == "valid"
    
    def test_get_service_status_summary(self, integration_service):
        """Test service status summary generation."""
        # Set up mock service status
        integration_service.service_status = {
            "service1": {"status": "healthy", "critical": True},
            "service2": {"status": "healthy", "critical": False},
            "service3": {"status": "error", "critical": True},
            "service4": {"status": "unhealthy", "critical": False}
        }
        
        summary = integration_service.get_service_status_summary()
        
        assert summary["total_services"] == 4
        assert summary["healthy_services"] == 2
        assert summary["unhealthy_services"] == 2
        assert summary["critical_services_down"] == ["service3"]
        assert summary["overall_status"] == "degraded"
        assert "last_updated" in summary
    
    @pytest.mark.asyncio
    async def test_cleanup(self, integration_service):
        """Test service cleanup."""
        mock_client = AsyncMock()
        mock_client._session = AsyncMock()
        integration_service.service_clients = {"test": mock_client}
        
        await integration_service.cleanup()
        
        mock_client._session.close.assert_called_once()


class TestIntegrationAPIEndpoints:
    """Test suite for integration API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from src.main import app
        return TestClient(app)
    
    def test_integration_health_endpoint(self, client):
        """Test integration health endpoint."""
        response = client.get("/api/v1/integration/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "fertilizer-application-integration"
        assert data["status"] == "healthy"
        assert "connected_services" in data
        assert "summary" in data
    
    def test_service_health_endpoint(self, client):
        """Test specific service health endpoint."""
        response = client.get("/api/v1/integration/health/recommendation-engine")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "recommendation-engine"
        assert "timestamp" in data
    
    def test_integration_status_endpoint(self, client):
        """Test integration status endpoint."""
        response = client.get("/api/v1/integration/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_services" in data
        assert "healthy_services" in data
        assert "overall_status" in data
    
    def test_soil_data_endpoint(self, client):
        """Test soil data endpoint."""
        response = client.get(
            "/api/v1/integration/soil-data",
            params={"field_id": "test-field", "user_id": "test-user"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["field_id"] == "test-field"
        assert data["user_id"] == "test-user"
        assert "soil_data" in data
    
    def test_weather_data_endpoint(self, client):
        """Test weather data endpoint."""
        response = client.get(
            "/api/v1/integration/weather-data",
            params={"latitude": 40.0, "longitude": -95.0}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["location"]["latitude"] == 40.0
        assert data["location"]["longitude"] == -95.0
        assert "weather_data" in data
    
    def test_fertilizer_prices_endpoint(self, client):
        """Test fertilizer prices endpoint."""
        request_data = {
            "fertilizer_types": ["urea", "dap"],
            "region": "midwest"
        }
        
        response = client.post("/api/v1/integration/fertilizer-prices", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["fertilizer_types"] == ["urea", "dap"]
        assert data["region"] == "midwest"
        assert "prices" in data
    
    def test_crop_recommendations_endpoint(self, client):
        """Test crop recommendations endpoint."""
        request_data = {
            "location_data": {"latitude": 40.0, "longitude": -95.0},
            "soil_data": {"ph": 6.5, "organic_matter": 3.2}
        }
        
        response = client.post("/api/v1/integration/crop-recommendations", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "location" in data
        assert "soil_data" in data
        assert "recommendations" in data
    
    def test_ai_explanation_endpoint(self, client):
        """Test AI explanation endpoint."""
        request_data = {
            "recommendation_data": {"method": "broadcast", "fertilizer": "urea"},
            "user_context": {"experience_level": "intermediate"}
        }
        
        response = client.post("/api/v1/integration/ai-explanation", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "recommendation_id" in data
        assert "explanation" in data
    
    def test_sync_fertilizer_data_endpoint(self, client):
        """Test fertilizer data sync endpoint."""
        request_data = {
            "field_id": "test-field",
            "user_id": "test-user",
            "force_sync": False
        }
        
        response = client.post("/api/v1/integration/sync-fertilizer-data", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["field_id"] == "test-field"
        assert data["user_id"] == "test-user"
        assert "sync_data" in data
    
    def test_validate_recommendation_endpoint(self, client):
        """Test recommendation validation endpoint."""
        request_data = {
            "recommendation": {
                "id": "rec-123",
                "field_id": "field-456",
                "location": {"latitude": 40.0, "longitude": -95.0}
            }
        }
        
        response = client.post("/api/v1/integration/validate-recommendation", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["recommendation_id"] == "rec-123"
        assert "validations" in data
        assert "overall_status" in data
    
    def test_list_services_endpoint(self, client):
        """Test list connected services endpoint."""
        response = client.get("/api/v1/integration/services")
        assert response.status_code == 200
        
        data = response.json()
        assert "connected_services" in data
        assert "total_services" in data
        assert data["total_services"] > 0
    
    def test_service_test_endpoint(self, client):
        """Test service connection test endpoint."""
        response = client.post("/api/v1/integration/services/recommendation-engine/test")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "recommendation-engine"
        assert "test_result" in data
    
    def test_metrics_endpoint(self, client):
        """Test integration metrics endpoint."""
        response = client.get("/api/v1/integration/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "service_status" in data
        assert "cache_stats" in data
    
    def test_clear_cache_endpoint(self, client):
        """Test clear cache endpoint."""
        response = client.get("/api/v1/integration/cache/clear")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "cleared_items" in data
    
    def test_fallback_data_endpoint(self, client):
        """Test fallback data endpoint."""
        response = client.get(
            "/api/v1/integration/fallback-data",
            params={"data_type": "soil_data"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["data_type"] == "soil_data"
        assert data["source"] == "fallback"


class TestIntegrationErrorHandling:
    """Test suite for integration error handling."""
    
    @pytest.fixture
    def integration_service(self):
        """Create integration service instance for testing."""
        return CAAINFertilizerIntegrationService()
    
    @pytest.mark.asyncio
    async def test_service_unavailable_error(self, integration_service):
        """Test handling of service unavailable errors."""
        with patch.object(integration_service, 'service_clients', {}):
            result = await integration_service.check_service_health("nonexistent-service")
            
            assert result["status"] == "not_found"
            assert "error" in result
    
    @pytest.mark.asyncio
    async def test_network_timeout_error(self, integration_service):
        """Test handling of network timeout errors."""
        mock_client = AsyncMock()
        mock_client.health_check.side_effect = asyncio.TimeoutError("Request timeout")
        
        with patch.object(integration_service, 'service_clients', {
            "test-service": mock_client
        }):
            result = await integration_service.check_service_health("test-service")
            
            assert result["status"] == "error"
            assert "error" in result
            assert "timeout" in result["error"].lower()
    
    @pytest.mark.asyncio
    async def test_data_validation_error(self, integration_service):
        """Test handling of data validation errors."""
        invalid_recommendation = {"invalid": "data"}
        
        result = await integration_service.validate_fertilizer_recommendation(invalid_recommendation)
        
        assert result["status"] == "failed"
        assert "error" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])