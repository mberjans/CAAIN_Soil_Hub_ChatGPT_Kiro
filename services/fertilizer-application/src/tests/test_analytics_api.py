"""
Tests for analytics API endpoints.

This module tests all analytics API endpoints including:
- User engagement tracking endpoints
- Recommendation effectiveness endpoints
- Agricultural impact endpoints
- System performance endpoints
- Usage pattern analysis endpoints
- Comprehensive reporting endpoints
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from src.main import app
from src.models.analytics_models import (
    UserSessionData, RecommendationOutcomeData, SystemMetricData,
    AnalyticsQuery, AlertConfiguration
)


class TestAnalyticsAPI:
    """Test suite for analytics API endpoints."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def sample_session_data(self):
        return {
            "session_id": str(uuid4()),
            "user_id": "test_user_123",
            "start_time": datetime.now().isoformat(),
            "end_time": (datetime.now() + timedelta(minutes=30)).isoformat(),
            "duration_minutes": 30.0,
            "actions": ["recommendation_requested", "feedback_provided"],
            "features_used": ["method_selection", "equipment_assessment"],
            "region": "midwest",
            "user_type": "farmer"
        }
    
    @pytest.fixture
    def sample_outcome_data(self):
        return {
            "recommendation_id": str(uuid4()),
            "user_id": "test_user_123",
            "method_recommended": "broadcast_spreading",
            "method_implemented": "broadcast_spreading",
            "implementation_date": datetime.now().isoformat(),
            "farmer_satisfaction": 4.5,
            "yield_impact": 12.5,
            "cost_savings": 250.0,
            "feedback_notes": "Excellent recommendation, saved time and money",
            "outcome_timestamp": datetime.now().isoformat()
        }
    
    @pytest.fixture
    def sample_system_metric(self):
        return {
            "metric_id": str(uuid4()),
            "timestamp": datetime.now().isoformat(),
            "requests": 1000,
            "response_time_ms": 1500.0,
            "errors": 5,
            "uptime_percentage": 99.5,
            "resource_utilization": {
                "cpu_usage": 45.0,
                "memory_usage": 60.0,
                "disk_usage": 30.0,
                "network_usage": 25.0
            },
            "throughput_per_hour": 1000.0
        }


class TestUserEngagementAPI(TestAnalyticsAPI):
    """Test user engagement API endpoints."""
    
    def test_track_user_engagement_success(self, client, sample_session_data):
        """Test successful user engagement tracking."""
        response = client.post(
            "/api/v1/analytics/user-engagement/track",
            json=sample_session_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["user_id"] == sample_session_data["user_id"]
        assert data["data"]["session_count"] == 1
        assert data["data"]["total_time_minutes"] == 30.0
        assert data["message"] == "User engagement tracked successfully"
    
    def test_track_user_engagement_invalid_data(self, client):
        """Test user engagement tracking with invalid data."""
        invalid_data = {
            "session_id": "invalid",
            "user_id": "",  # Empty user ID
            "duration_minutes": -10  # Negative duration
        }
        
        response = client.post(
            "/api/v1/analytics/user-engagement/track",
            json=invalid_data
        )
        
        # Should still process but with validation
        assert response.status_code in [200, 422]  # 422 for validation error
    
    def test_track_user_engagement_missing_fields(self, client):
        """Test user engagement tracking with missing required fields."""
        incomplete_data = {
            "session_id": str(uuid4()),
            "user_id": "test_user"
            # Missing other required fields
        }
        
        response = client.post(
            "/api/v1/analytics/user-engagement/track",
            json=incomplete_data
        )
        
        # Should handle missing fields gracefully
        assert response.status_code in [200, 422]


class TestRecommendationEffectivenessAPI(TestAnalyticsAPI):
    """Test recommendation effectiveness API endpoints."""
    
    def test_track_recommendation_outcome_success(self, client, sample_outcome_data):
        """Test successful recommendation outcome tracking."""
        response = client.post(
            "/api/v1/analytics/recommendations/track-outcome",
            json=sample_outcome_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["recommendation_id"] == sample_outcome_data["recommendation_id"]
        assert data["data"]["method_recommended"] == "broadcast_spreading"
        assert data["data"]["method_implemented"] == "broadcast_spreading"
        assert data["data"]["farmer_satisfaction"] == 4.5
        assert data["data"]["implementation_rate"] == 1.0
        assert data["message"] == "Recommendation outcome tracked successfully"
    
    def test_track_recommendation_outcome_not_implemented(self, client):
        """Test tracking recommendation that wasn't implemented."""
        outcome_data = {
            "recommendation_id": str(uuid4()),
            "user_id": "test_user",
            "method_recommended": "precision_application",
            "method_implemented": None,
            "farmer_satisfaction": None,
            "yield_impact": None,
            "cost_savings": None,
            "outcome_timestamp": datetime.now().isoformat()
        }
        
        response = client.post(
            "/api/v1/analytics/recommendations/track-outcome",
            json=outcome_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["implementation_rate"] == 0.0
        assert data["data"]["success_score"] < 0.5


class TestSystemMetricsAPI(TestAnalyticsAPI):
    """Test system metrics API endpoints."""
    
    def test_track_system_metric_success(self, client, sample_system_metric):
        """Test successful system metric tracking."""
        response = client.post(
            "/api/v1/analytics/system-metrics/track",
            json=sample_system_metric
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["metric_id"] == sample_system_metric["metric_id"]
        assert data["message"] == "System metric tracked successfully"
    
    def test_track_system_metric_invalid_data(self, client):
        """Test system metric tracking with invalid data."""
        invalid_data = {
            "metric_id": str(uuid4()),
            "timestamp": datetime.now().isoformat(),
            "requests": -100,  # Negative requests
            "response_time_ms": -500,  # Negative response time
            "errors": -10,  # Negative errors
            "uptime_percentage": 150.0,  # Over 100%
            "resource_utilization": {
                "cpu_usage": 150.0,  # Over 100%
                "memory_usage": -50.0,  # Negative
                "disk_usage": 30.0,
                "network_usage": 25.0
            },
            "throughput_per_hour": -1000.0  # Negative throughput
        }
        
        response = client.post(
            "/api/v1/analytics/system-metrics/track",
            json=invalid_data
        )
        
        # Should handle validation errors
        assert response.status_code in [200, 422]


class TestAgriculturalImpactAPI(TestAnalyticsAPI):
    """Test agricultural impact API endpoints."""
    
    def test_get_agricultural_impact_success(self, client):
        """Test successful agricultural impact retrieval."""
        response = client.get("/api/v1/analytics/agricultural-impact/daily?days=30")
        
        assert response.status_code == 200
        data = response.json()
        assert "period" in data
        assert "total_recommendations" in data
        assert "implemented_recommendations" in data
        assert "estimated_yield_increase" in data
        assert "estimated_cost_savings" in data
        assert "environmental_benefits" in data
        assert "farmer_satisfaction_avg" in data
        assert "adoption_rate" in data
    
    def test_get_agricultural_impact_different_periods(self, client):
        """Test agricultural impact for different periods."""
        periods = ["daily", "weekly", "monthly", "quarterly"]
        
        for period in periods:
            response = client.get(f"/api/v1/analytics/agricultural-impact/{period}?days=30")
            assert response.status_code == 200
            data = response.json()
            assert data["period"] == period
    
    def test_get_agricultural_impact_invalid_period(self, client):
        """Test agricultural impact with invalid period."""
        response = client.get("/api/v1/analytics/agricultural-impact/invalid?days=30")
        
        # Should still work but with default handling
        assert response.status_code == 200


class TestSystemPerformanceAPI(TestAnalyticsAPI):
    """Test system performance API endpoints."""
    
    def test_get_system_performance_success(self, client):
        """Test successful system performance retrieval."""
        response = client.get("/api/v1/analytics/system-performance/daily?days=30")
        
        assert response.status_code == 200
        data = response.json()
        assert "period" in data
        assert "total_requests" in data
        assert "average_response_time_ms" in data
        assert "error_rate" in data
        assert "uptime_percentage" in data
        assert "throughput_per_hour" in data
        assert "resource_utilization" in data
    
    def test_get_system_performance_different_periods(self, client):
        """Test system performance for different periods."""
        periods = ["daily", "weekly", "monthly"]
        
        for period in periods:
            response = client.get(f"/api/v1/analytics/system-performance/{period}?days=30")
            assert response.status_code == 200
            data = response.json()
            assert data["period"] == period


class TestUsagePatternsAPI(TestAnalyticsAPI):
    """Test usage patterns API endpoints."""
    
    def test_get_usage_patterns_success(self, client):
        """Test successful usage patterns retrieval."""
        response = client.get("/api/v1/analytics/usage-patterns/daily?days=30")
        
        assert response.status_code == 200
        data = response.json()
        assert "period" in data
        assert "peak_usage_hours" in data
        assert "most_used_features" in data
        assert "seasonal_patterns" in data
        assert "geographic_distribution" in data
        assert "user_segments" in data
    
    def test_get_usage_patterns_different_periods(self, client):
        """Test usage patterns for different periods."""
        periods = ["daily", "weekly", "monthly"]
        
        for period in periods:
            response = client.get(f"/api/v1/analytics/usage-patterns/{period}?days=30")
            assert response.status_code == 200
            data = response.json()
            assert data["period"] == period


class TestComprehensiveReportingAPI(TestAnalyticsAPI):
    """Test comprehensive reporting API endpoints."""
    
    def test_generate_comprehensive_report_success(self, client):
        """Test successful comprehensive report generation."""
        response = client.post(
            "/api/v1/analytics/reports/generate",
            params={
                "report_type": "detailed",
                "period": "monthly",
                "days": 30
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "report_id" in data
        assert "report_type" in data
        assert "period" in data
        assert "generated_at" in data
        assert "user_engagement" in data
        assert "recommendation_effectiveness" in data
        assert "agricultural_impact" in data
        assert "system_performance" in data
        assert "usage_patterns" in data
        assert "key_insights" in data
        assert "recommendations" in data
    
    def test_generate_comprehensive_report_different_types(self, client):
        """Test comprehensive report generation with different report types."""
        report_types = ["summary", "detailed", "executive", "technical", "agricultural"]
        
        for report_type in report_types:
            response = client.post(
                "/api/v1/analytics/reports/generate",
                params={
                    "report_type": report_type,
                    "period": "monthly",
                    "days": 30
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["report_type"] == report_type
    
    def test_generate_comprehensive_report_different_periods(self, client):
        """Test comprehensive report generation for different periods."""
        periods = ["daily", "weekly", "monthly", "quarterly"]
        
        for period in periods:
            response = client.post(
                "/api/v1/analytics/reports/generate",
                params={
                    "report_type": "detailed",
                    "period": period,
                    "days": 30
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["period"] == period


class TestAnalyticsSummaryAPI(TestAnalyticsAPI):
    """Test analytics summary API endpoints."""
    
    def test_get_analytics_summary_success(self, client):
        """Test successful analytics summary retrieval."""
        response = client.get("/api/v1/analytics/summary/monthly")
        
        assert response.status_code == 200
        data = response.json()
        assert "period" in data
        assert "total_users" in data
        assert "total_recommendations" in data
        assert "implementation_rate" in data
        assert "average_satisfaction" in data
        assert "system_uptime" in data
        assert "key_metrics" in data
        assert "summary_generated_at" in data
    
    def test_get_analytics_summary_different_periods(self, client):
        """Test analytics summary for different periods."""
        periods = ["daily", "weekly", "monthly", "quarterly"]
        
        for period in periods:
            response = client.get(f"/api/v1/analytics/summary/{period}")
            assert response.status_code == 200
            data = response.json()
            assert data["period"] == period


class TestAnalyticsDashboardAPI(TestAnalyticsAPI):
    """Test analytics dashboard API endpoints."""
    
    def test_get_analytics_dashboard_success(self, client):
        """Test successful analytics dashboard retrieval."""
        dashboard_id = "test_dashboard"
        response = client.get(f"/api/v1/analytics/dashboard/{dashboard_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "dashboard_id" in data
        assert "title" in data
        assert "widgets" in data
        assert "refresh_interval" in data
        assert "user_permissions" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_get_analytics_dashboard_different_ids(self, client):
        """Test analytics dashboard with different IDs."""
        dashboard_ids = ["executive_dashboard", "technical_dashboard", "farmer_dashboard"]
        
        for dashboard_id in dashboard_ids:
            response = client.get(f"/api/v1/analytics/dashboard/{dashboard_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["dashboard_id"] == dashboard_id


class TestAnalyticsAlertsAPI(TestAnalyticsAPI):
    """Test analytics alerts API endpoints."""
    
    def test_configure_analytics_alert_success(self, client):
        """Test successful analytics alert configuration."""
        alert_config = {
            "alert_id": str(uuid4()),
            "metric_type": "user_engagement",
            "threshold_value": 0.5,
            "comparison_operator": "<",
            "alert_frequency": "daily",
            "notification_methods": ["email", "dashboard"],
            "enabled": True
        }
        
        response = client.post(
            "/api/v1/analytics/alerts/configure",
            json=alert_config
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["alert_id"] == alert_config["alert_id"]
        assert data["message"] == "Analytics alert configured successfully"
    
    def test_configure_analytics_alert_invalid_data(self, client):
        """Test analytics alert configuration with invalid data."""
        invalid_config = {
            "alert_id": "",  # Empty alert ID
            "metric_type": "invalid_metric",
            "threshold_value": -1.0,  # Negative threshold
            "comparison_operator": "invalid_operator",
            "alert_frequency": "invalid_frequency",
            "notification_methods": [],  # Empty methods
            "enabled": "invalid_boolean"  # Invalid boolean
        }
        
        response = client.post(
            "/api/v1/analytics/alerts/configure",
            json=invalid_config
        )
        
        # Should handle validation errors
        assert response.status_code in [200, 422]


class TestAnalyticsHealthAPI(TestAnalyticsAPI):
    """Test analytics health API endpoints."""
    
    def test_analytics_health_check(self, client):
        """Test analytics service health check."""
        response = client.get("/api/v1/analytics/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "analytics"


class TestAnalyticsErrorHandling(TestAnalyticsAPI):
    """Test analytics API error handling."""
    
    def test_invalid_endpoint(self, client):
        """Test invalid endpoint handling."""
        response = client.get("/api/v1/analytics/invalid-endpoint")
        
        assert response.status_code == 404
    
    def test_missing_parameters(self, client):
        """Test missing required parameters."""
        response = client.get("/api/v1/analytics/agricultural-impact/")
        
        # Should handle missing parameters gracefully
        assert response.status_code in [200, 404, 422]
    
    def test_invalid_json(self, client):
        """Test invalid JSON handling."""
        response = client.post(
            "/api/v1/analytics/user-engagement/track",
            data="invalid json"
        )
        
        assert response.status_code == 422
    
    def test_large_data_handling(self, client):
        """Test handling of large data payloads."""
        large_session_data = {
            "session_id": str(uuid4()),
            "user_id": "test_user",
            "start_time": datetime.now().isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration_minutes": 30.0,
            "actions": ["action"] * 1000,  # Large actions list
            "features_used": ["feature"] * 1000,  # Large features list
            "region": "midwest",
            "user_type": "farmer"
        }
        
        response = client.post(
            "/api/v1/analytics/user-engagement/track",
            json=large_session_data
        )
        
        # Should handle large data gracefully
        assert response.status_code in [200, 413, 422]


class TestAnalyticsPerformance(TestAnalyticsAPI):
    """Test analytics API performance."""
    
    def test_response_time_requirements(self, client):
        """Test that API responses meet time requirements."""
        import time
        
        start_time = time.time()
        response = client.get("/api/v1/analytics/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < 1.0  # Should respond within 1 second
        assert response.status_code == 200
    
    def test_concurrent_requests(self, client):
        """Test handling of concurrent requests."""
        import threading
        import time
        
        results = []
        
        def make_request():
            start_time = time.time()
            response = client.get("/api/v1/analytics/health")
            end_time = time.time()
            results.append({
                "status_code": response.status_code,
                "response_time": end_time - start_time
            })
        
        # Make 10 concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all requests succeeded
        assert len(results) == 10
        for result in results:
            assert result["status_code"] == 200
            assert result["response_time"] < 2.0  # Should respond within 2 seconds