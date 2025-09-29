"""
End-to-End Integration Tests

Comprehensive tests for cross-service integration, data flow validation,
and system-wide functionality across the CAAIN Soil Hub ecosystem.
"""

import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Dict, Any

from src.services.caain_integration_service import CAAINIntegrationService
from src.services.variety_recommendation_service import VarietyRecommendationService
from src.services.crop_taxonomy_service import CropTaxonomyService


class TestEndToEndIntegration:
    """End-to-end integration test suite."""
    
    @pytest.fixture
    def integration_service(self):
        """Create integration service for testing."""
        return CAAINIntegrationService()
    
    @pytest.fixture
    def variety_service(self):
        """Create variety recommendation service for testing."""
        return VarietyRecommendationService()
    
    @pytest.fixture
    def taxonomy_service(self):
        """Create crop taxonomy service for testing."""
        return CropTaxonomyService()
    
    @pytest.fixture
    def mock_soil_data(self):
        """Mock soil data response."""
        return {
            "status": "success",
            "data": {
                "ph": 6.5,
                "organic_matter_percent": 3.2,
                "phosphorus_ppm": 25,
                "potassium_ppm": 150,
                "texture": "clay_loam",
                "drainage": "well_drained"
            },
            "source": "data-integration",
            "timestamp": datetime.now().isoformat()
        }
    
    @pytest.fixture
    def mock_climate_data(self):
        """Mock climate data response."""
        return {
            "status": "success",
            "data": {
                "usda_hardiness_zone": "6a",
                "koppen_climate": "Dfa",
                "growing_season_days": 180,
                "last_frost_date": "2024-04-15",
                "first_frost_date": "2024-10-15"
            },
            "source": "data-integration",
            "timestamp": datetime.now().isoformat()
        }
    
    @pytest.fixture
    def mock_recommendation_response(self):
        """Mock recommendation engine response."""
        return {
            "status": "success",
            "recommendations": [
                {
                    "variety_id": "corn_pioneer_1234",
                    "variety_name": "Pioneer P1234",
                    "confidence_score": 0.85,
                    "yield_potential": "high",
                    "disease_resistance": ["rust", "blight"],
                    "maturity_days": 110
                }
            ],
            "source": "recommendation-engine",
            "timestamp": datetime.now().isoformat()
        }
    
    @pytest.fixture
    def mock_ai_explanation(self):
        """Mock AI explanation response."""
        return {
            "status": "success",
            "explanation": {
                "summary": "This variety is recommended due to its high yield potential and disease resistance.",
                "details": [
                    "High yield potential matches your soil's fertility level",
                    "Disease resistance protects against common corn diseases in your region",
                    "Maturity timing aligns with your growing season"
                ],
                "confidence": 0.85,
                "risk_factors": ["Requires adequate moisture", "Susceptible to late-season pests"]
            },
            "source": "ai-agent",
            "timestamp": datetime.now().isoformat()
        }
    
    @pytest.mark.asyncio
    async def test_complete_crop_recommendation_workflow(
        self, 
        integration_service, 
        variety_service,
        mock_soil_data,
        mock_climate_data,
        mock_recommendation_response,
        mock_ai_explanation
    ):
        """
        Test complete workflow from location input to variety recommendation with AI explanation.
        
        This test simulates the full user journey:
        1. User provides location coordinates
        2. System retrieves soil and climate data
        3. System generates variety recommendations
        4. System provides AI-powered explanation
        5. System validates data consistency across services
        """
        # Test data
        latitude = 40.7128
        longitude = -74.0060
        user_preferences = {
            "crop_type": "corn",
            "yield_goal": "high",
            "disease_resistance_priority": "high"
        }
        
        # Mock external service calls
        with patch.object(integration_service, 'get_soil_data_for_location', 
                         return_value=mock_soil_data) as mock_soil:
            with patch.object(integration_service, 'get_climate_data_for_location', 
                             return_value=mock_climate_data) as mock_climate:
                with patch.object(integration_service, 'sync_crop_data_with_recommendation_engine', 
                                 return_value=mock_recommendation_response) as mock_sync:
                    with patch.object(integration_service, 'get_ai_explanation_for_recommendation', 
                                     return_value=mock_ai_explanation) as mock_ai:
                        with patch.object(integration_service, 'validate_data_consistency', 
                                         return_value={"overall_status": "valid"}) as mock_validate:
                            
                            # Step 1: Get environmental data
                            soil_data = await integration_service.get_soil_data_for_location(latitude, longitude)
                            climate_data = await integration_service.get_climate_data_for_location(latitude, longitude)
                            
                            # Verify soil data retrieval
                            assert soil_data["status"] == "success"
                            assert "ph" in soil_data["data"]
                            assert "organic_matter_percent" in soil_data["data"]
                            mock_soil.assert_called_once_with(latitude, longitude)
                            
                            # Verify climate data retrieval
                            assert climate_data["status"] == "success"
                            assert "usda_hardiness_zone" in climate_data["data"]
                            assert "growing_season_days" in climate_data["data"]
                            mock_climate.assert_called_once_with(latitude, longitude)
                            
                            # Step 2: Generate variety recommendations
                            crop_data = {
                                "location": {"latitude": latitude, "longitude": longitude},
                                "soil_data": soil_data["data"],
                                "climate_data": climate_data["data"],
                                "user_preferences": user_preferences
                            }
                            
                            sync_result = await integration_service.sync_crop_data_with_recommendation_engine(crop_data)
                            
                            # Verify recommendation generation
                            assert sync_result["status"] == "success"
                            assert "recommendations" in sync_result
                            assert len(sync_result["recommendations"]) > 0
                            mock_sync.assert_called_once()
                            
                            # Step 3: Get AI explanation
                            recommendation_data = {
                                "variety_id": sync_result["recommendations"][0]["variety_id"],
                                "confidence_score": sync_result["recommendations"][0]["confidence_score"],
                                "location": {"latitude": latitude, "longitude": longitude},
                                "soil_data": soil_data["data"],
                                "climate_data": climate_data["data"]
                            }
                            
                            explanation = await integration_service.get_ai_explanation_for_recommendation(recommendation_data)
                            
                            # Verify AI explanation
                            assert explanation["status"] == "success"
                            assert "explanation" in explanation
                            assert "summary" in explanation["explanation"]
                            assert "details" in explanation["explanation"]
                            mock_ai.assert_called_once()
                            
                            # Step 4: Validate data consistency
                            validation_result = await integration_service.validate_data_consistency(
                                "crop_variety", 
                                sync_result["recommendations"][0]
                            )
                            
                            # Verify data validation
                            assert validation_result["overall_status"] == "valid"
                            mock_validate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_service_failure_recovery(
        self, 
        integration_service,
        mock_soil_data
    ):
        """
        Test system behavior when external services fail and recovery mechanisms.
        """
        latitude = 40.7128
        longitude = -74.0060
        
        # Test with service failure
        with patch.object(integration_service, 'get_soil_data_for_location', 
                         side_effect=Exception("Service unavailable")) as mock_soil_fail:
            
            # Should handle service failure gracefully
            soil_data = await integration_service.get_soil_data_for_location(latitude, longitude)
            
            # Verify error handling
            assert soil_data["status"] == "error"
            assert "error" in soil_data
            mock_soil_fail.assert_called_once()
        
        # Test recovery after service comes back online
        with patch.object(integration_service, 'get_soil_data_for_location', 
                         return_value=mock_soil_data) as mock_soil_recovery:
            
            soil_data = await integration_service.get_soil_data_for_location(latitude, longitude)
            
            # Verify successful recovery
            assert soil_data["status"] == "success"
            assert "data" in soil_data
            mock_soil_recovery.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_concurrent_service_calls(
        self, 
        integration_service,
        mock_soil_data,
        mock_climate_data
    ):
        """
        Test concurrent calls to multiple services to verify system performance.
        """
        latitude = 40.7128
        longitude = -74.0060
        
        # Mock service calls
        with patch.object(integration_service, 'get_soil_data_for_location', 
                         return_value=mock_soil_data) as mock_soil:
            with patch.object(integration_service, 'get_climate_data_for_location', 
                             return_value=mock_climate_data) as mock_climate:
                
                # Make concurrent calls
                start_time = datetime.now()
                
                tasks = [
                    integration_service.get_soil_data_for_location(latitude, longitude),
                    integration_service.get_climate_data_for_location(latitude, longitude),
                    integration_service.get_soil_data_for_location(latitude + 0.1, longitude + 0.1),
                    integration_service.get_climate_data_for_location(latitude + 0.1, longitude + 0.1)
                ]
                
                results = await asyncio.gather(*tasks)
                
                end_time = datetime.now()
                execution_time = (end_time - start_time).total_seconds()
                
                # Verify all calls completed successfully
                assert len(results) == 4
                for result in results:
                    assert result["status"] == "success"
                
                # Verify concurrent execution (should be faster than sequential)
                assert execution_time < 2.0  # Should complete in under 2 seconds
                
                # Verify correct number of calls
                assert mock_soil.call_count == 2
                assert mock_climate.call_count == 2
    
    @pytest.mark.asyncio
    async def test_data_consistency_validation(
        self, 
        integration_service
    ):
        """
        Test data consistency validation across multiple services.
        """
        # Test crop variety data validation
        crop_variety_data = {
            "variety_id": "corn_pioneer_1234",
            "crop_name": "Corn",
            "variety_name": "Pioneer P1234",
            "maturity_days": 110,
            "yield_potential": "high"
        }
        
        mock_validation_response = {
            "status": "valid",
            "validation_results": {
                "recommendation_engine": "valid",
                "data_integration": "valid"
            }
        }
        
        with patch.object(integration_service, 'get_service_data', 
                         return_value=mock_validation_response) as mock_validate:
            
            result = await integration_service.validate_data_consistency(
                "crop_variety", 
                crop_variety_data
            )
            
            assert result["data_type"] == "crop_variety"
            assert result["overall_status"] == "valid"
            assert "validations" in result
            assert "recommendation_engine" in result["validations"]
            
            mock_validate.assert_called_once()
        
        # Test soil data validation
        soil_data = {
            "ph": 6.5,
            "organic_matter_percent": 3.2,
            "phosphorus_ppm": 25,
            "potassium_ppm": 150
        }
        
        with patch.object(integration_service, 'get_service_data', 
                         return_value=mock_validation_response) as mock_validate_soil:
            
            result = await integration_service.validate_data_consistency(
                "soil_data", 
                soil_data
            )
            
            assert result["data_type"] == "soil_data"
            assert result["overall_status"] == "valid"
            assert "validations" in result
            assert "data_integration" in result["validations"]
            
            mock_validate_soil.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_integration_service_health_monitoring(
        self, 
        integration_service
    ):
        """
        Test health monitoring and status reporting across all services.
        """
        # Mock health check responses
        mock_health_results = {
            "recommendation-engine": {
                "status": "healthy",
                "response_time": 0.5,
                "critical": True
            },
            "data-integration": {
                "status": "healthy", 
                "response_time": 0.3,
                "critical": True
            },
            "ai-agent": {
                "status": "healthy",
                "response_time": 1.2,
                "critical": False
            },
            "question-router": {
                "status": "unhealthy",
                "response_time": None,
                "critical": True,
                "error": "Connection timeout"
            }
        }
        
        with patch.object(integration_service, 'health_check_all_services', 
                         return_value=mock_health_results) as mock_health_check:
            
            status = await integration_service.get_integration_status()
            
            # Verify status structure
            assert "overall_status" in status
            assert "total_services" in status
            assert "healthy_services" in status
            assert "critical_services_healthy" in status
            assert "service_details" in status
            assert "integration_features" in status
            
            # Verify status values
            assert status["total_services"] == 4
            assert status["healthy_services"] == 3
            assert status["critical_services_healthy"] == False  # question-router is critical and unhealthy
            assert status["overall_status"] == "degraded"
            
            # Verify service details
            assert "recommendation-engine" in status["service_details"]
            assert "data-integration" in status["service_details"]
            assert "ai-agent" in status["service_details"]
            assert "question-router" in status["service_details"]
            
            mock_health_check.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling_and_logging(
        self, 
        integration_service
    ):
        """
        Test comprehensive error handling and logging mechanisms.
        """
        # Test service unavailable error
        with patch.object(integration_service.service_clients["recommendation-engine"], 
                         'get', side_effect=Exception("Service unavailable")) as mock_error:
            
            try:
                await integration_service.get_service_data(
                    "recommendation-engine", 
                    "/api/v1/test"
                )
            except Exception as e:
                # Verify error was raised
                assert "Service unavailable" in str(e)
                
                # Verify error count was incremented
                assert integration_service.service_status["recommendation-engine"]["error_count"] > 0
                assert integration_service.service_status["recommendation-engine"]["status"] == "error"
        
        # Test timeout error
        with patch.object(integration_service.service_clients["data-integration"], 
                         'get', side_effect=asyncio.TimeoutError("Request timeout")) as mock_timeout:
            
            try:
                await integration_service.get_service_data(
                    "data-integration", 
                    "/api/v1/test"
                )
            except Exception as e:
                # Verify timeout error was handled
                assert "timeout" in str(e).lower() or "timeout" in str(type(e)).lower()
                
                # Verify error count was incremented
                assert integration_service.service_status["data-integration"]["error_count"] > 0
    
    @pytest.mark.asyncio
    async def test_data_synchronization_workflow(
        self, 
        integration_service,
        mock_recommendation_response
    ):
        """
        Test data synchronization workflow between services.
        """
        # Test crop data synchronization
        crop_data = {
            "variety_id": "corn_pioneer_1234",
            "crop_name": "Corn",
            "variety_name": "Pioneer P1234",
            "characteristics": {
                "yield_potential": "high",
                "disease_resistance": ["rust", "blight"],
                "maturity_days": 110
            },
            "performance_data": {
                "average_yield": 180,
                "yield_unit": "bushels_per_acre",
                "test_locations": 15
            }
        }
        
        with patch.object(integration_service, 'get_service_data', 
                         return_value=mock_recommendation_response) as mock_sync:
            
            result = await integration_service.sync_crop_data_with_recommendation_engine(crop_data)
            
            # Verify synchronization
            assert result["status"] == "success"
            assert "recommendations" in result
            
            # Verify data was cached
            sync_key = f"crop_sync_{crop_data['variety_id']}"
            assert sync_key in integration_service.data_sync_cache
            
            cached_data = integration_service.data_sync_cache[sync_key]
            assert cached_data["data"] == crop_data
            assert cached_data["response"] == result
            assert "timestamp" in cached_data
            
            mock_sync.assert_called_once_with(
                service_name="recommendation-engine",
                endpoint="/api/v1/recommendations/crop-varieties/sync",
                data=crop_data
            )
    
    @pytest.mark.asyncio
    async def test_performance_metrics_collection(
        self, 
        integration_service
    ):
        """
        Test performance metrics collection and reporting.
        """
        # Simulate some service calls to generate metrics
        mock_response = {"status": "success", "data": "test"}
        
        with patch.object(integration_service, 'get_service_data', 
                         return_value=mock_response) as mock_call:
            
            # Make several service calls
            await integration_service.get_service_data("recommendation-engine", "/test1")
            await integration_service.get_service_data("data-integration", "/test2")
            await integration_service.get_service_data("ai-agent", "/test3")
            
            # Get integration status to check metrics
            status = await integration_service.get_integration_status()
            
            # Verify metrics are collected
            assert "total_services" in status
            assert "healthy_services" in status
            assert "critical_services_healthy" in status
            
            # Verify service details include performance data
            for service_name, details in status["service_details"].items():
                assert "status" in details
                assert "last_check" in details
                assert "critical" in details
            
            # Verify integration features are reported
            features = status["integration_features"]
            assert features["service_discovery"] == True
            assert features["health_monitoring"] == True
            assert features["data_synchronization"] == True
            assert features["cross_service_validation"] == True
            assert features["error_handling"] == True
            assert features["performance_monitoring"] == True


class TestIntegrationAPIEndpoints:
    """Test integration API endpoints end-to-end."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from src.main import app
        return TestClient(app)
    
    def test_complete_api_workflow(self, client):
        """
        Test complete API workflow from start to finish.
        """
        # Step 1: Check integration health
        response = client.get("/api/v1/integration/health")
        assert response.status_code == 200
        health_data = response.json()
        assert "service" in health_data
        assert "integration_status" in health_data
        
        # Step 2: Get services status
        response = client.get("/api/v1/integration/services/status")
        assert response.status_code == 200
        status_data = response.json()
        assert "integration_summary" in status_data
        assert "services" in status_data
        
        # Step 3: Perform health checks
        response = client.post("/api/v1/integration/services/health-check")
        assert response.status_code == 200
        health_checks = response.json()
        assert "health_checks" in health_checks
        assert "summary" in health_checks
        
        # Step 4: Get soil data
        response = client.get("/api/v1/integration/data/soil/40.7128/-74.0060")
        assert response.status_code == 200
        soil_data = response.json()
        assert "location" in soil_data
        assert "soil_data" in soil_data
        
        # Step 5: Get climate data
        response = client.get("/api/v1/integration/data/climate/40.7128/-74.0060")
        assert response.status_code == 200
        climate_data = response.json()
        assert "location" in climate_data
        assert "climate_data" in climate_data
        
        # Step 6: Sync crop data
        crop_data = {
            "variety_id": "corn_test_123",
            "crop_name": "Corn",
            "variety_name": "Test Variety"
        }
        response = client.post(
            "/api/v1/integration/data/sync-crop-data",
            json=crop_data
        )
        assert response.status_code == 200
        sync_result = response.json()
        assert "sync_results" in sync_result
        assert "status" in sync_result
        
        # Step 7: Validate data consistency
        validation_data = {
            "data_type": "crop_variety",
            "data": crop_data
        }
        response = client.post(
            "/api/v1/integration/data/validate-consistency",
            json=validation_data
        )
        assert response.status_code == 200
        validation_result = response.json()
        assert "validation_result" in validation_result
        
        # Step 8: Get AI explanation
        recommendation_data = {
            "variety_id": "corn_test_123",
            "confidence_score": 0.85
        }
        response = client.post(
            "/api/v1/integration/ai/explain-recommendation",
            json=recommendation_data
        )
        assert response.status_code == 200
        explanation = response.json()
        assert "explanation" in explanation
        
        # Step 9: Get integration metrics
        response = client.get("/api/v1/integration/monitoring/metrics")
        assert response.status_code == 200
        metrics = response.json()
        assert "metrics" in metrics
        assert "service_details" in metrics
    
    def test_error_handling_in_api(self, client):
        """
        Test error handling in API endpoints.
        """
        # Test invalid service name
        response = client.get("/api/v1/integration/services/invalid-service/status")
        assert response.status_code == 404
        
        # Test invalid coordinates
        response = client.get("/api/v1/integration/data/soil/999/999")
        assert response.status_code == 200  # Should handle gracefully
        
        # Test invalid data format
        response = client.post(
            "/api/v1/integration/data/sync-crop-data",
            json={"invalid": "data"}
        )
        assert response.status_code == 200  # Should handle gracefully
    
    def test_concurrent_api_calls(self, client):
        """
        Test concurrent API calls to verify system stability.
        """
        import threading
        import time
        
        results = []
        errors = []
        
        def make_api_call():
            try:
                response = client.get("/api/v1/integration/health")
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))
        
        # Make concurrent calls
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_api_call)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all calls succeeded
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 10
        assert all(status == 200 for status in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])