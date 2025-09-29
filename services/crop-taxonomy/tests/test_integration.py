"""
Integration Tests for CAAIN Soil Hub Service Integration

Tests for cross-service communication, data synchronization,
and integration functionality.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
import json

from src.services.caain_integration_service import (
    CAAINIntegrationService,
    ServiceClientError
)


class TestCAAINIntegrationService:
    """Test suite for CAAIN integration service."""
    
    @pytest.fixture
    def integration_service(self):
        """Create integration service instance for testing."""
        return CAAINIntegrationService()
    
    @pytest.fixture
    def mock_service_response(self):
        """Mock service response data."""
        return {
            "status": "healthy",
            "data": {"test": "data"},
            "timestamp": datetime.now().isoformat()
        }
    
    def test_service_initialization(self, integration_service):
        """Test that integration service initializes correctly."""
        assert integration_service is not None
        assert len(integration_service.service_clients) > 0
        assert len(integration_service.integration_config) > 0
        
        # Check that critical services are configured
        critical_services = ["recommendation-engine", "data-integration", "question-router"]
        for service in critical_services:
            assert service in integration_service.integration_config
            assert integration_service.integration_config[service]["critical"] is True
    
    def test_integration_config_loading(self, integration_service):
        """Test that integration configuration is loaded correctly."""
        config = integration_service.integration_config
        
        # Check required services are configured
        required_services = [
            "recommendation-engine",
            "data-integration", 
            "ai-agent",
            "question-router",
            "cover-crop-selection",
            "user-management",
            "image-analysis"
        ]
        
        for service in required_services:
            assert service in config
            assert "base_url" in config[service]
            assert "endpoints" in config[service]
            assert "timeout" in config[service]
            assert "retry_attempts" in config[service]
    
    @pytest.mark.asyncio
    async def test_health_check_all_services(self, integration_service, mock_service_response):
        """Test health check functionality for all services."""
        # Mock the service client health check
        with patch.object(integration_service.service_clients["recommendation-engine"], 
                         'health_check', return_value=True):
            with patch.object(integration_service.service_clients["data-integration"], 
                             'health_check', return_value=True):
                
                health_results = await integration_service.health_check_all_services()
                
                assert "recommendation-engine" in health_results
                assert "data-integration" in health_results
                assert health_results["recommendation-engine"]["status"] == "healthy"
                assert health_results["data-integration"]["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_get_service_data_success(self, integration_service, mock_service_response):
        """Test successful service data retrieval."""
        service_name = "recommendation-engine"
        endpoint = "/api/v1/test"
        
        # Mock the service client
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_service_response)
        
        integration_service.service_clients[service_name] = mock_client
        
        result = await integration_service.get_service_data(service_name, endpoint)
        
        assert result == mock_service_response
        mock_client.get.assert_called_once_with(endpoint, params=None)
    
    @pytest.mark.asyncio
    async def test_get_service_data_failure(self, integration_service):
        """Test service data retrieval failure handling."""
        service_name = "recommendation-engine"
        endpoint = "/api/v1/test"
        
        # Mock the service client to raise an exception
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(side_effect=Exception("Service unavailable"))
        
        integration_service.service_clients[service_name] = mock_client
        
        with pytest.raises(ServiceClientError):
            await integration_service.get_service_data(service_name, endpoint)
        
        # Check that error count was incremented
        assert integration_service.service_status[service_name]["error_count"] > 0
    
    @pytest.mark.asyncio
    async def test_sync_crop_data_with_recommendation_engine(self, integration_service, mock_service_response):
        """Test crop data synchronization with recommendation engine."""
        crop_data = {
            "variety_id": "test_variety_123",
            "crop_name": "Corn",
            "variety_name": "Test Variety",
            "characteristics": {"yield_potential": "high"}
        }
        
        # Mock the service call
        with patch.object(integration_service, 'get_service_data', 
                         return_value=mock_service_response) as mock_get_data:
            
            result = await integration_service.sync_crop_data_with_recommendation_engine(crop_data)
            
            assert result == mock_service_response
            mock_get_data.assert_called_once_with(
                service_name="recommendation-engine",
                endpoint="/api/v1/recommendations/crop-varieties/sync",
                data=crop_data
            )
            
            # Check that data was cached
            sync_key = f"crop_sync_{crop_data['variety_id']}"
            assert sync_key in integration_service.data_sync_cache
    
    @pytest.mark.asyncio
    async def test_get_soil_data_for_location(self, integration_service, mock_service_response):
        """Test soil data retrieval for a location."""
        latitude = 40.7128
        longitude = -74.0060
        
        # Mock the service call
        with patch.object(integration_service, 'get_service_data', 
                         return_value=mock_service_response) as mock_get_data:
            
            result = await integration_service.get_soil_data_for_location(latitude, longitude)
            
            assert result == mock_service_response
            mock_get_data.assert_called_once_with(
                service_name="data-integration",
                endpoint="/api/v1/soil/characteristics",
                data={"latitude": latitude, "longitude": longitude}
            )
    
    @pytest.mark.asyncio
    async def test_get_climate_data_for_location(self, integration_service, mock_service_response):
        """Test climate data retrieval for a location."""
        latitude = 40.7128
        longitude = -74.0060
        
        # Mock the service call
        with patch.object(integration_service, 'get_service_data', 
                         return_value=mock_service_response) as mock_get_data:
            
            result = await integration_service.get_climate_data_for_location(latitude, longitude)
            
            assert result == mock_service_response
            mock_get_data.assert_called_once_with(
                service_name="data-integration",
                endpoint="/api/v1/climate-zones/by-coordinates",
                params={"latitude": latitude, "longitude": longitude}
            )
    
    @pytest.mark.asyncio
    async def test_get_ai_explanation_for_recommendation(self, integration_service, mock_service_response):
        """Test AI explanation retrieval for recommendations."""
        recommendation_data = {
            "variety_id": "test_variety_123",
            "confidence_score": 0.85,
            "recommendation_reason": "High yield potential"
        }
        
        # Mock the service call
        with patch.object(integration_service, 'get_service_data', 
                         return_value=mock_service_response) as mock_get_data:
            
            result = await integration_service.get_ai_explanation_for_recommendation(recommendation_data)
            
            assert result == mock_service_response
            mock_get_data.assert_called_once_with(
                service_name="ai-agent",
                endpoint="/api/v1/ai/explain",
                data={
                    "type": "variety_recommendation",
                    "data": recommendation_data
                }
            )
    
    @pytest.mark.asyncio
    async def test_validate_data_consistency_crop_variety(self, integration_service):
        """Test data consistency validation for crop variety data."""
        data_type = "crop_variety"
        data = {
            "variety_id": "test_variety_123",
            "crop_name": "Corn",
            "variety_name": "Test Variety"
        }
        
        mock_validation_response = {
            "status": "valid",
            "validation_results": {"recommendation_engine": "valid"}
        }
        
        # Mock the service call
        with patch.object(integration_service, 'get_service_data', 
                         return_value=mock_validation_response) as mock_get_data:
            
            result = await integration_service.validate_data_consistency(data_type, data)
            
            assert result["data_type"] == data_type
            assert result["overall_status"] == "valid"
            assert "validations" in result
            assert "recommendation_engine" in result["validations"]
            
            mock_get_data.assert_called_once_with(
                service_name="recommendation-engine",
                endpoint="/api/v1/validation/crop-variety",
                data=data
            )
    
    @pytest.mark.asyncio
    async def test_validate_data_consistency_soil_data(self, integration_service):
        """Test data consistency validation for soil data."""
        data_type = "soil_data"
        data = {
            "ph": 6.5,
            "organic_matter": 3.2,
            "phosphorus": 25,
            "potassium": 150
        }
        
        mock_validation_response = {
            "status": "valid",
            "validation_results": {"data_integration": "valid"}
        }
        
        # Mock the service call
        with patch.object(integration_service, 'get_service_data', 
                         return_value=mock_validation_response) as mock_get_data:
            
            result = await integration_service.validate_data_consistency(data_type, data)
            
            assert result["data_type"] == data_type
            assert result["overall_status"] == "valid"
            assert "validations" in result
            assert "data_integration" in result["validations"]
            
            mock_get_data.assert_called_once_with(
                service_name="data-integration",
                endpoint="/api/v1/validation/soil-data",
                data=data
            )
    
    @pytest.mark.asyncio
    async def test_get_integration_status(self, integration_service):
        """Test integration status retrieval."""
        # Mock health check results
        mock_health_results = {
            "recommendation-engine": {"status": "healthy", "response_time": 0.5},
            "data-integration": {"status": "healthy", "response_time": 0.3},
            "ai-agent": {"status": "healthy", "response_time": 1.2}
        }
        
        with patch.object(integration_service, 'health_check_all_services', 
                         return_value=mock_health_results) as mock_health_check:
            
            result = await integration_service.get_integration_status()
            
            assert "overall_status" in result
            assert "total_services" in result
            assert "healthy_services" in result
            assert "critical_services_healthy" in result
            assert "service_details" in result
            assert "integration_features" in result
            
            assert result["total_services"] > 0
            assert result["healthy_services"] >= 0
            assert isinstance(result["integration_features"], dict)
    
    @pytest.mark.asyncio
    async def test_service_error_handling(self, integration_service):
        """Test error handling when services are unavailable."""
        service_name = "recommendation-engine"
        endpoint = "/api/v1/test"
        
        # Mock service client that raises connection error
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(side_effect=ConnectionError("Service unavailable"))
        
        integration_service.service_clients[service_name] = mock_client
        
        with pytest.raises(ServiceClientError):
            await integration_service.get_service_data(service_name, endpoint)
        
        # Verify error count was incremented
        assert integration_service.service_status[service_name]["error_count"] > 0
        assert integration_service.service_status[service_name]["status"] == "error"
    
    def test_service_configuration_validation(self, integration_service):
        """Test that all service configurations are valid."""
        config = integration_service.integration_config
        
        for service_name, service_config in config.items():
            # Check required fields
            assert "base_url" in service_config, f"Missing base_url for {service_name}"
            assert "endpoints" in service_config, f"Missing endpoints for {service_name}"
            assert "timeout" in service_config, f"Missing timeout for {service_name}"
            assert "retry_attempts" in service_config, f"Missing retry_attempts for {service_name}"
            
            # Validate URL format
            base_url = service_config["base_url"]
            assert base_url.startswith("http"), f"Invalid URL format for {service_name}: {base_url}"
            
            # Validate timeout and retry values
            assert isinstance(service_config["timeout"], int), f"Invalid timeout for {service_name}"
            assert isinstance(service_config["retry_attempts"], int), f"Invalid retry_attempts for {service_name}"
            assert service_config["timeout"] > 0, f"Timeout must be positive for {service_name}"
            assert service_config["retry_attempts"] >= 0, f"Retry attempts must be non-negative for {service_name}"
    
    @pytest.mark.asyncio
    async def test_concurrent_service_calls(self, integration_service, mock_service_response):
        """Test concurrent calls to multiple services."""
        # Mock multiple service calls
        with patch.object(integration_service, 'get_service_data', 
                         return_value=mock_service_response) as mock_get_data:
            
            # Make concurrent calls to different services
            tasks = [
                integration_service.get_soil_data_for_location(40.0, -95.0),
                integration_service.get_climate_data_for_location(40.0, -95.0),
                integration_service.get_ai_explanation_for_recommendation({"test": "data"})
            ]
            
            results = await asyncio.gather(*tasks)
            
            # Verify all calls completed successfully
            assert len(results) == 3
            for result in results:
                assert result == mock_service_response
            
            # Verify the correct number of service calls were made
            assert mock_get_data.call_count == 3


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
        assert "service" in data
        assert "status" in data
        assert "integration_status" in data
    
    def test_services_status_endpoint(self, client):
        """Test services status endpoint."""
        response = client.get("/api/v1/integration/services/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert "integration_summary" in data
        assert "services" in data
    
    def test_health_checks_endpoint(self, client):
        """Test health checks endpoint."""
        response = client.post("/api/v1/integration/services/health-check")
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert "health_checks" in data
        assert "summary" in data
    
    def test_soil_data_endpoint(self, client):
        """Test soil data endpoint."""
        response = client.get("/api/v1/integration/data/soil/40.7128/-74.0060")
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert "location" in data
        assert "soil_data" in data
    
    def test_climate_data_endpoint(self, client):
        """Test climate data endpoint."""
        response = client.get("/api/v1/integration/data/climate/40.7128/-74.0060")
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert "location" in data
        assert "climate_data" in data
    
    def test_crop_data_sync_endpoint(self, client):
        """Test crop data sync endpoint."""
        crop_data = {
            "variety_id": "test_123",
            "crop_name": "Corn",
            "variety_name": "Test Variety"
        }
        
        response = client.post(
            "/api/v1/integration/data/sync-crop-data",
            json=crop_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert "sync_results" in data
        assert "status" in data
    
    def test_data_consistency_validation_endpoint(self, client):
        """Test data consistency validation endpoint."""
        validation_data = {
            "data_type": "crop_variety",
            "data": {
                "variety_id": "test_123",
                "crop_name": "Corn"
            }
        }
        
        response = client.post(
            "/api/v1/integration/data/validate-consistency",
            json=validation_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert "validation_result" in data
    
    def test_ai_explanation_endpoint(self, client):
        """Test AI explanation endpoint."""
        recommendation_data = {
            "variety_id": "test_123",
            "confidence_score": 0.85
        }
        
        response = client.post(
            "/api/v1/integration/ai/explain-recommendation",
            json=recommendation_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert "explanation" in data
    
    def test_service_status_endpoint(self, client):
        """Test service status endpoint."""
        response = client.get("/api/v1/integration/services/recommendation-engine/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert "service_name" in data
        assert "status" in data
        assert "configuration" in data
    
    def test_service_call_endpoint(self, client):
        """Test service call endpoint."""
        call_data = {
            "endpoint": "/health",
            "method": "GET"
        }
        
        response = client.post(
            "/api/v1/integration/services/recommendation-engine/call",
            json=call_data
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert "service" in data
        assert "endpoint" in data
        assert "method" in data
        assert "response" in data
    
    def test_integration_metrics_endpoint(self, client):
        """Test integration metrics endpoint."""
        response = client.get("/api/v1/integration/monitoring/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert "metrics" in data
        assert "service_details" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])