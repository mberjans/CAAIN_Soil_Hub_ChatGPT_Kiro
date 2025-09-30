"""
API tests for dynamic price adjustment system.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from uuid import uuid4, UUID
import json

from ..main import app
from ..models.price_adjustment_models import (
    PriceAdjustmentRequest, PriceAdjustmentResponse, PriceAdjustmentStatus,
    PriceAdjustmentConfiguration, NotificationSettings, AdjustmentAlert,
    StrategyModification, EconomicImpactAnalysis, ApprovalStatus
)
from ..models.price_models import FertilizerType, NotificationMethod

client = TestClient(app)


class TestPriceAdjustmentAPI:
    """Test suite for price adjustment API endpoints."""
    
    @pytest.fixture
    def sample_request_data(self):
        """Create sample request data for testing."""
        return {
            "user_id": "12345678-1234-5678-9012-123456789012",
            "fertilizer_types": ["nitrogen", "phosphorus"],
            "fields": [
                {
                    "field_id": "field_1",
                    "acres": 100.0,
                    "soil_type": "clay_loam",
                    "current_ph": 6.5,
                    "organic_matter_percent": 3.2,
                    "target_yield": 180.0,
                    "crop_price": 5.50,
                    "previous_crop": "corn",
                    "tillage_system": "no_till",
                    "irrigation_available": True
                }
            ],
            "region": "US",
            "price_change_threshold": 5.0,
            "volatility_threshold": 15.0,
            "check_interval_minutes": 30,
            "monitoring_duration_hours": 168,
            "auto_adjust_enabled": True,
            "adjustment_strategy": "balanced",
            "max_adjustment_percent": 20.0,
            "notification_enabled": True,
            "notification_methods": ["email"],
            "notification_threshold": 10.0,
            "require_approval": True,
            "approval_timeout_hours": 24
        }
    
    def test_start_price_monitoring_success(self, sample_request_data):
        """Test successful price monitoring start."""
        with patch('services.fertilizer_strategy.src.api.price_adjustment_routes.get_price_adjustment_service') as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.start_price_monitoring.return_value = PriceAdjustmentResponse(
                request_id="test-request-id",
                success=True,
                monitoring_active=True,
                processing_time_ms=150.0,
                message="Price monitoring started successfully"
            )
            mock_service.return_value = mock_service_instance
            
            response = client.post("/api/v1/price-adjustment/monitoring/start", json=sample_request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["monitoring_active"] is True
            assert data["request_id"] == "test-request-id"
            assert data["message"] == "Price monitoring started successfully"
    
    def test_start_price_monitoring_validation_error(self):
        """Test price monitoring start with validation error."""
        invalid_data = {
            "user_id": "12345678-1234-5678-9012-123456789012",
            "fertilizer_types": [],  # Invalid: empty list
            "fields": [],  # Invalid: empty list
            "region": "US"
        }
        
        with patch('services.fertilizer_strategy.src.api.price_adjustment_routes.get_price_adjustment_service') as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.start_price_monitoring.return_value = PriceAdjustmentResponse(
                request_id="test-request-id",
                success=False,
                monitoring_active=False,
                processing_time_ms=50.0,
                error_message="Validation error"
            )
            mock_service.return_value = mock_service_instance
            
            response = client.post("/api/v1/price-adjustment/monitoring/start", json=invalid_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert data["monitoring_active"] is False
            assert data["error_message"] is not None
    
    def test_check_price_adjustments_success(self):
        """Test successful price adjustment check."""
        request_id = "test-request-id"
        
        with patch('services.fertilizer_strategy.src.api.price_adjustment_routes.get_price_adjustment_service') as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.check_price_adjustments.return_value = PriceAdjustmentResponse(
                request_id=request_id,
                success=True,
                monitoring_active=True,
                processing_time_ms=200.0,
                message="Price check completed"
            )
            mock_service.return_value = mock_service_instance
            
            response = client.post(f"/api/v1/price-adjustment/monitoring/{request_id}/check")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["monitoring_active"] is True
            assert data["request_id"] == request_id
    
    def test_check_price_adjustments_session_not_found(self):
        """Test price adjustment check with non-existent session."""
        request_id = "non-existent-id"
        
        with patch('services.fertilizer_strategy.src.api.price_adjustment_routes.get_price_adjustment_service') as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.check_price_adjustments.side_effect = ValueError("Monitoring session not found")
            mock_service.return_value = mock_service_instance
            
            response = client.post(f"/api/v1/price-adjustment/monitoring/{request_id}/check")
            
            assert response.status_code == 404
            data = response.json()
            assert "Monitoring session not found" in data["detail"]
    
    def test_stop_price_monitoring_success(self):
        """Test successful price monitoring stop."""
        request_id = "test-request-id"
        
        with patch('services.fertilizer_strategy.src.api.price_adjustment_routes.get_price_adjustment_service') as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.stop_price_monitoring.return_value = PriceAdjustmentResponse(
                request_id=request_id,
                success=True,
                monitoring_active=False,
                processing_time_ms=100.0,
                message="Price monitoring stopped successfully"
            )
            mock_service.return_value = mock_service_instance
            
            response = client.post(f"/api/v1/price-adjustment/monitoring/{request_id}/stop")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["monitoring_active"] is False
            assert data["message"] == "Price monitoring stopped successfully"
    
    def test_get_monitoring_status_success(self):
        """Test successful monitoring status retrieval."""
        request_id = "test-request-id"
        
        with patch('services.fertilizer_strategy.src.api.price_adjustment_routes.get_price_adjustment_service') as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.get_monitoring_status.return_value = {
                "request_id": request_id,
                "status": "active",
                "start_time": "2024-01-01T00:00:00Z",
                "last_check": "2024-01-01T01:00:00Z",
                "adjustments_made": 2,
                "alerts_sent": 3,
                "uptime_seconds": 3600.0
            }
            mock_service.return_value = mock_service_instance
            
            response = client.get(f"/api/v1/price-adjustment/monitoring/{request_id}/status")
            
            assert response.status_code == 200
            data = response.json()
            assert data["request_id"] == request_id
            assert data["status"] == "active"
            assert data["adjustments_made"] == 2
            assert data["alerts_sent"] == 3
    
    def test_get_active_monitoring_sessions(self):
        """Test getting active monitoring sessions."""
        with patch('services.fertilizer_strategy.src.api.price_adjustment_routes.get_price_adjustment_service') as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.get_active_monitoring_sessions.return_value = []
            mock_service.return_value = mock_service_instance
            
            response = client.get("/api/v1/price-adjustment/monitoring/active")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_approve_strategy_modification(self):
        """Test strategy modification approval."""
        modification_id = "test-modification-id"
        approver_id = "12345678-1234-5678-9012-123456789012"
        
        with patch('services.fertilizer_strategy.src.api.price_adjustment_routes.get_price_adjustment_service') as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.approve_strategy_modification.return_value = {
                "success": True,
                "modification_id": modification_id,
                "approved_by": approver_id,
                "approved_at": "2024-01-01T00:00:00Z",
                "message": "Modification approved successfully"
            }
            mock_service.return_value = mock_service_instance
            
            response = client.post(
                f"/api/v1/price-adjustment/adjustments/{modification_id}/approve",
                params={"approver_id": approver_id, "comments": "Approved for testing"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["modification_id"] == modification_id
            assert data["approved_by"] == approver_id
    
    def test_reject_strategy_modification(self):
        """Test strategy modification rejection."""
        modification_id = "test-modification-id"
        approver_id = "12345678-1234-5678-9012-123456789012"
        reason = "Economic impact too high"
        
        with patch('services.fertilizer_strategy.src.api.price_adjustment_routes.get_price_adjustment_service') as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.reject_strategy_modification.return_value = {
                "success": True,
                "modification_id": modification_id,
                "rejected_by": approver_id,
                "rejected_at": "2024-01-01T00:00:00Z",
                "reason": reason,
                "message": "Modification rejected successfully"
            }
            mock_service.return_value = mock_service_instance
            
            response = client.post(
                f"/api/v1/price-adjustment/adjustments/{modification_id}/reject",
                params={
                    "approver_id": approver_id,
                    "reason": reason,
                    "comments": "Additional rejection comments"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["modification_id"] == modification_id
            assert data["reason"] == reason
    
    def test_get_pending_modifications(self):
        """Test getting pending modifications."""
        with patch('services.fertilizer_strategy.src.api.price_adjustment_routes.get_price_adjustment_service') as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.get_pending_modifications.return_value = []
            mock_service.return_value = mock_service_instance
            
            response = client.get("/api/v1/price-adjustment/adjustments/pending")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_get_adjustment_alerts(self):
        """Test getting adjustment alerts."""
        with patch('services.fertilizer_strategy.src.api.price_adjustment_routes.get_price_adjustment_service') as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.get_adjustment_alerts.return_value = []
            mock_service.return_value = mock_service_instance
            
            response = client.get("/api/v1/price-adjustment/alerts")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_acknowledge_alert(self):
        """Test alert acknowledgment."""
        alert_id = "test-alert-id"
        user_id = "12345678-1234-5678-9012-123456789012"
        
        with patch('services.fertilizer_strategy.src.api.price_adjustment_routes.get_price_adjustment_service') as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.acknowledge_alert.return_value = {
                "success": True,
                "alert_id": alert_id,
                "acknowledged_by": user_id,
                "acknowledged_at": "2024-01-01T00:00:00Z",
                "message": "Alert acknowledged successfully"
            }
            mock_service.return_value = mock_service_instance
            
            response = client.post(f"/api/v1/price-adjustment/alerts/{alert_id}/acknowledge", params={"user_id": user_id})
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["alert_id"] == alert_id
            assert data["acknowledged_by"] == user_id
    
    def test_get_user_configuration(self):
        """Test getting user configuration."""
        user_id = "12345678-1234-5678-9012-123456789012"
        
        with patch('services.fertilizer_strategy.src.api.price_adjustment_routes.get_price_adjustment_service') as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.get_user_configuration.return_value = {
                "user_id": user_id,
                "default_price_threshold": 5.0,
                "default_volatility_threshold": 15.0,
                "default_check_interval": 30,
                "max_adjustment_percent": 20.0,
                "auto_adjust_enabled": True,
                "require_approval": True,
                "notification_enabled": True,
                "alert_threshold": 10.0
            }
            mock_service.return_value = mock_service_instance
            
            response = client.get(f"/api/v1/price-adjustment/configuration/{user_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == user_id
            assert data["default_price_threshold"] == 5.0
            assert data["auto_adjust_enabled"] is True
    
    def test_update_user_configuration(self):
        """Test updating user configuration."""
        user_id = "12345678-1234-5678-9012-123456789012"
        configuration_data = {
            "default_price_threshold": 7.0,
            "default_volatility_threshold": 18.0,
            "default_check_interval": 45,
            "max_adjustment_percent": 25.0,
            "auto_adjust_enabled": False,
            "require_approval": True,
            "notification_enabled": True,
            "alert_threshold": 12.0
        }
        
        with patch('services.fertilizer_strategy.src.api.price_adjustment_routes.get_price_adjustment_service') as mock_service:
            mock_service_instance = AsyncMock()
            updated_config = configuration_data.copy()
            updated_config["user_id"] = user_id
            updated_config["updated_at"] = "2024-01-01T00:00:00Z"
            mock_service_instance.update_user_configuration.return_value = updated_config
            mock_service.return_value = mock_service_instance
            
            response = client.put(f"/api/v1/price-adjustment/configuration/{user_id}", json=configuration_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == user_id
            assert data["default_price_threshold"] == 7.0
            assert data["auto_adjust_enabled"] is False
    
    def test_get_notification_settings(self):
        """Test getting notification settings."""
        user_id = "12345678-1234-5678-9012-123456789012"
        
        with patch('services.fertilizer_strategy.src.api.price_adjustment_routes.get_price_adjustment_service') as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.get_notification_settings.return_value = {
                "user_id": user_id,
                "email_enabled": True,
                "sms_enabled": False,
                "push_enabled": True,
                "in_app_enabled": True,
                "immediate_alerts": True,
                "daily_summary": True,
                "weekly_report": True,
                "alert_threshold_percent": 5.0,
                "summary_threshold_percent": 2.0
            }
            mock_service.return_value = mock_service_instance
            
            response = client.get(f"/api/v1/price-adjustment/notifications/{user_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == user_id
            assert data["email_enabled"] is True
            assert data["sms_enabled"] is False
    
    def test_update_notification_settings(self):
        """Test updating notification settings."""
        user_id = "12345678-1234-5678-9012-123456789012"
        settings_data = {
            "email_enabled": True,
            "sms_enabled": True,
            "push_enabled": False,
            "in_app_enabled": True,
            "immediate_alerts": True,
            "daily_summary": False,
            "weekly_report": True,
            "alert_threshold_percent": 8.0,
            "summary_threshold_percent": 3.0
        }
        
        with patch('services.fertilizer_strategy.src.api.price_adjustment_routes.get_price_adjustment_service') as mock_service:
            mock_service_instance = AsyncMock()
            updated_settings = settings_data.copy()
            updated_settings["user_id"] = user_id
            updated_settings["updated_at"] = "2024-01-01T00:00:00Z"
            mock_service_instance.update_notification_settings.return_value = updated_settings
            mock_service.return_value = mock_service_instance
            
            response = client.put(f"/api/v1/price-adjustment/notifications/{user_id}", json=settings_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == user_id
            assert data["sms_enabled"] is True
            assert data["push_enabled"] is False
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/api/v1/price-adjustment/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "price-adjustment"
        assert "timestamp" in data
        assert "version" in data
    
    def test_get_service_metrics(self):
        """Test service metrics endpoint."""
        with patch('services.fertilizer_strategy.src.api.price_adjustment_routes.get_price_adjustment_service') as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.get_service_metrics.return_value = {
                "active_sessions": 5,
                "total_adjustments": 25,
                "successful_adjustments": 23,
                "average_processing_time_ms": 150.0,
                "success_rate_percent": 92.0,
                "uptime_seconds": 86400,
                "last_updated": "2024-01-01T00:00:00Z"
            }
            mock_service.return_value = mock_service_instance
            
            response = client.get("/api/v1/price-adjustment/metrics")
            
            assert response.status_code == 200
            data = response.json()
            assert data["active_sessions"] == 5
            assert data["total_adjustments"] == 25
            assert data["success_rate_percent"] == 92.0


class TestPriceAdjustmentAPIIntegration:
    """Integration tests for price adjustment API."""
    
    def test_complete_workflow(self):
        """Test complete API workflow from start to stop."""
        user_id = "12345678-1234-5678-9012-123456789012"
        
        # Request data
        request_data = {
            "user_id": user_id,
            "fertilizer_types": ["nitrogen"],
            "fields": [{"field_id": "field_1", "acres": 100.0}],
            "region": "US",
            "price_change_threshold": 5.0,
            "monitoring_duration_hours": 1
        }
        
        with patch('services.fertilizer_strategy.src.api.price_adjustment_routes.get_price_adjustment_service') as mock_service:
            mock_service_instance = AsyncMock()
            
            # Mock start monitoring
            mock_service_instance.start_price_monitoring.return_value = PriceAdjustmentResponse(
                request_id="test-request-id",
                success=True,
                monitoring_active=True,
                processing_time_ms=150.0,
                message="Price monitoring started successfully"
            )
            
            # Mock check adjustments
            mock_service_instance.check_price_adjustments.return_value = PriceAdjustmentResponse(
                request_id="test-request-id",
                success=True,
                monitoring_active=True,
                processing_time_ms=200.0,
                message="Price check completed"
            )
            
            # Mock get status
            mock_service_instance.get_monitoring_status.return_value = {
                "request_id": "test-request-id",
                "status": "active",
                "start_time": "2024-01-01T00:00:00Z",
                "last_check": "2024-01-01T01:00:00Z",
                "adjustments_made": 1,
                "alerts_sent": 2,
                "uptime_seconds": 3600.0
            }
            
            # Mock stop monitoring
            mock_service_instance.stop_price_monitoring.return_value = PriceAdjustmentResponse(
                request_id="test-request-id",
                success=True,
                monitoring_active=False,
                processing_time_ms=100.0,
                message="Price monitoring stopped successfully"
            )
            
            mock_service.return_value = mock_service_instance
            
            # Start monitoring
            start_response = client.post("/api/v1/price-adjustment/monitoring/start", json=request_data)
            assert start_response.status_code == 200
            start_data = start_response.json()
            assert start_data["success"] is True
            request_id = start_data["request_id"]
            
            # Check adjustments
            check_response = client.post(f"/api/v1/price-adjustment/monitoring/{request_id}/check")
            assert check_response.status_code == 200
            check_data = check_response.json()
            assert check_data["success"] is True
            
            # Get status
            status_response = client.get(f"/api/v1/price-adjustment/monitoring/{request_id}/status")
            assert status_response.status_code == 200
            status_data = status_response.json()
            assert status_data["status"] == "active"
            
            # Stop monitoring
            stop_response = client.post(f"/api/v1/price-adjustment/monitoring/{request_id}/stop")
            assert stop_response.status_code == 200
            stop_data = stop_response.json()
            assert stop_data["success"] is True
            assert stop_data["monitoring_active"] is False
    
    def test_error_handling(self):
        """Test API error handling."""
        # Test invalid request data
        invalid_data = {
            "user_id": "invalid-uuid",
            "fertilizer_types": [],
            "fields": []
        }
        
        with patch('services.fertilizer_strategy.src.api.price_adjustment_routes.get_price_adjustment_service') as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.start_price_monitoring.return_value = PriceAdjustmentResponse(
                request_id="test-request-id",
                success=False,
                monitoring_active=False,
                processing_time_ms=50.0,
                error_message="Validation error"
            )
            mock_service.return_value = mock_service_instance
            
            response = client.post("/api/v1/price-adjustment/monitoring/start", json=invalid_data)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
        
        # Test non-existent session
        with patch('services.fertilizer_strategy.src.api.price_adjustment_routes.get_price_adjustment_service') as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.check_price_adjustments.side_effect = ValueError("Monitoring session not found")
            mock_service.return_value = mock_service_instance
            
            response = client.post("/api/v1/price-adjustment/monitoring/non-existent-id/check")
            assert response.status_code == 404
            data = response.json()
            assert "Monitoring session not found" in data["detail"]


class TestPriceAdjustmentAPIPerformance:
    """Performance tests for price adjustment API."""
    
    def test_concurrent_requests(self):
        """Test concurrent API requests."""
        import threading
        import time
        
        request_data = {
            "user_id": "12345678-1234-5678-9012-123456789012",
            "fertilizer_types": ["nitrogen"],
            "fields": [{"field_id": "field_1", "acres": 100.0}],
            "region": "US"
        }
        
        results = []
        
        def make_request():
            with patch('services.fertilizer_strategy.src.api.price_adjustment_routes.get_price_adjustment_service') as mock_service:
                mock_service_instance = AsyncMock()
                mock_service_instance.start_price_monitoring.return_value = PriceAdjustmentResponse(
                    request_id=f"test-request-{threading.current_thread().ident}",
                    success=True,
                    monitoring_active=True,
                    processing_time_ms=150.0,
                    message="Price monitoring started successfully"
                )
                mock_service.return_value = mock_service_instance
                
                response = client.post("/api/v1/price-adjustment/monitoring/start", json=request_data)
                results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 5
        assert (end_time - start_time) < 5.0  # Should complete within 5 seconds