"""
Test Suite for Production Monitoring System
TICKET-008_farm-location-input-15.2: Implement production monitoring and optimization

Comprehensive tests for the production monitoring, analytics, and optimization system.
"""

import pytest
import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
import json

from src.services.production_monitoring_service import (
    LocationProductionMonitoringService,
    MonitoringLevel,
    LocationAccuracyLevel,
    LocationAccuracyMetrics,
    ServicePerformanceMetrics,
    UserExperienceMetrics,
    OptimizationRecommendation,
    Alert
)
from src.services.production_analytics_service import (
    LocationProductionAnalyticsService,
    AnalyticsPeriod,
    AnalyticsReport,
    UsagePattern,
    BusinessMetric
)
from src.services.prometheus_metrics_collector import (
    LocationPrometheusMetricsCollector,
    MetricType
)
from src.services.monitoring_integration_service import (
    LocationMonitoringIntegrationService,
    ServiceIntegration
)

class TestLocationProductionMonitoringService:
    """Test suite for LocationProductionMonitoringService."""
    
    @pytest.fixture
    def monitoring_service(self):
        """Create monitoring service instance for testing."""
        return LocationProductionMonitoringService()
    
    @pytest.fixture
    def sample_accuracy_metrics(self):
        """Sample accuracy metrics for testing."""
        return LocationAccuracyMetrics(
            timestamp=datetime.utcnow(),
            location_id="test_location_1",
            expected_coordinates=(40.7128, -74.0060),
            actual_coordinates=(40.7130, -74.0058),
            accuracy_meters=25.5,
            accuracy_level=LocationAccuracyLevel.MEDIUM,
            validation_method="gps",
            confidence_score=0.85,
            processing_time_ms=150.0,
            user_feedback=0.9
        )
    
    @pytest.fixture
    def sample_performance_metrics(self):
        """Sample performance metrics for testing."""
        return ServicePerformanceMetrics(
            timestamp=datetime.utcnow(),
            service_name="location_validation",
            endpoint="/api/v1/locations/validate",
            response_time_ms=245.7,
            status_code=200,
            cpu_usage_percent=45.2,
            memory_usage_percent=62.8,
            cache_hit_rate=0.75
        )
    
    @pytest.fixture
    def sample_ux_metrics(self):
        """Sample user experience metrics for testing."""
        return UserExperienceMetrics(
            timestamp=datetime.utcnow(),
            user_id="user_123",
            session_id="session_456",
            action_type="location_input",
            success=True,
            time_to_complete_ms=1200.0,
            user_satisfaction=0.87,
            retry_count=0
        )
    
    @pytest.mark.asyncio
    async def test_monitoring_service_initialization(self, monitoring_service):
        """Test monitoring service initialization."""
        assert monitoring_service is not None
        assert monitoring_service.thresholds is not None
        assert len(monitoring_service.thresholds) > 0
        assert not monitoring_service.monitoring_active
    
    @pytest.mark.asyncio
    async def test_record_location_accuracy(self, monitoring_service, sample_accuracy_metrics):
        """Test recording location accuracy metrics."""
        await monitoring_service.record_location_accuracy(
            location_id=sample_accuracy_metrics.location_id,
            expected_coordinates=sample_accuracy_metrics.expected_coordinates,
            actual_coordinates=sample_accuracy_metrics.actual_coordinates,
            validation_method=sample_accuracy_metrics.validation_method,
            processing_time_ms=sample_accuracy_metrics.processing_time_ms,
            user_feedback=sample_accuracy_metrics.user_feedback
        )
        
        assert len(monitoring_service.location_accuracy_metrics) == 1
        recorded_metrics = monitoring_service.location_accuracy_metrics[0]
        assert recorded_metrics.location_id == sample_accuracy_metrics.location_id
        assert recorded_metrics.accuracy_meters > 0
        assert recorded_metrics.confidence_score > 0
    
    @pytest.mark.asyncio
    async def test_record_service_performance(self, monitoring_service, sample_performance_metrics):
        """Test recording service performance metrics."""
        await monitoring_service.record_service_performance(
            service_name=sample_performance_metrics.service_name,
            endpoint=sample_performance_metrics.endpoint,
            response_time_ms=sample_performance_metrics.response_time_ms,
            status_code=sample_performance_metrics.status_code,
            cache_hit_rate=sample_performance_metrics.cache_hit_rate
        )
        
        assert len(monitoring_service.service_performance_metrics) == 1
        recorded_metrics = monitoring_service.service_performance_metrics[0]
        assert recorded_metrics.service_name == sample_performance_metrics.service_name
        assert recorded_metrics.response_time_ms == sample_performance_metrics.response_time_ms
    
    @pytest.mark.asyncio
    async def test_record_user_experience(self, monitoring_service, sample_ux_metrics):
        """Test recording user experience metrics."""
        await monitoring_service.record_user_experience(
            user_id=sample_ux_metrics.user_id,
            session_id=sample_ux_metrics.session_id,
            action_type=sample_ux_metrics.action_type,
            success=sample_ux_metrics.success,
            time_to_complete_ms=sample_ux_metrics.time_to_complete_ms,
            user_satisfaction=sample_ux_metrics.user_satisfaction,
            retry_count=sample_ux_metrics.retry_count
        )
        
        assert len(monitoring_service.user_experience_metrics) == 1
        recorded_metrics = monitoring_service.user_experience_metrics[0]
        assert recorded_metrics.user_id == sample_ux_metrics.user_id
        assert recorded_metrics.success == sample_ux_metrics.success
    
    @pytest.mark.asyncio
    async def test_alert_generation(self, monitoring_service):
        """Test alert generation for threshold violations."""
        # Record metrics that should trigger alerts
        await monitoring_service.record_location_accuracy(
            location_id="test_location",
            expected_coordinates=(40.7128, -74.0060),
            actual_coordinates=(40.7200, -74.0000),  # Large distance to trigger alert
            validation_method="gps",
            processing_time_ms=100.0
        )
        
        # Check if alert was generated
        assert len(monitoring_service.active_alerts) > 0
        alert = monitoring_service.active_alerts[0]
        assert alert.level in [MonitoringLevel.WARNING, MonitoringLevel.CRITICAL]
        assert alert.category == "location_accuracy"
    
    @pytest.mark.asyncio
    async def test_optimization_recommendation_generation(self, monitoring_service):
        """Test optimization recommendation generation."""
        # Record multiple metrics to trigger recommendations
        for i in range(60):  # More than threshold for recommendation generation
            await monitoring_service.record_location_accuracy(
                location_id=f"test_location_{i}",
                expected_coordinates=(40.7128, -74.0060),
                actual_coordinates=(40.7130, -74.0058),
                validation_method="gps",
                processing_time_ms=100.0
            )
        
        # Generate recommendations
        await monitoring_service._generate_optimization_recommendations()
        
        # Check if recommendations were generated
        assert len(monitoring_service.optimization_recommendations) > 0
        recommendation = monitoring_service.optimization_recommendations[0]
        assert recommendation.category in ["accuracy", "performance", "user_experience"]
        assert recommendation.potential_improvement_percent > 0
    
    @pytest.mark.asyncio
    async def test_dashboard_data_generation(self, monitoring_service):
        """Test dashboard data generation."""
        # Record some sample data
        await monitoring_service.record_location_accuracy(
            location_id="test_location",
            expected_coordinates=(40.7128, -74.0060),
            actual_coordinates=(40.7130, -74.0058),
            validation_method="gps",
            processing_time_ms=100.0
        )
        
        dashboard_data = await monitoring_service.get_monitoring_dashboard_data()
        
        assert "timestamp" in dashboard_data
        assert "location_accuracy" in dashboard_data
        assert "service_performance" in dashboard_data
        assert "user_experience" in dashboard_data
        assert "alerts" in dashboard_data
        assert "optimization_recommendations" in dashboard_data
    
    @pytest.mark.asyncio
    async def test_alert_resolution(self, monitoring_service):
        """Test alert resolution."""
        # Generate an alert
        alert = Alert(
            alert_id="test_alert_1",
            level=MonitoringLevel.WARNING,
            category="test_category",
            title="Test Alert",
            message="Test alert message",
            timestamp=datetime.utcnow()
        )
        
        monitoring_service.active_alerts.append(alert)
        
        # Resolve the alert
        success = await monitoring_service.resolve_alert("test_alert_1")
        
        assert success
        assert alert.resolved
        assert alert.resolved_at is not None
    
    @pytest.mark.asyncio
    async def test_threshold_updates(self, monitoring_service):
        """Test threshold updates."""
        original_threshold = monitoring_service.thresholds["response_time_warning_ms"]
        new_thresholds = {"response_time_warning_ms": 3000.0}
        
        monitoring_service.update_thresholds(new_thresholds)
        
        assert monitoring_service.thresholds["response_time_warning_ms"] == 3000.0
        assert monitoring_service.thresholds["response_time_warning_ms"] != original_threshold
    
    @pytest.mark.asyncio
    async def test_cleanup_old_metrics(self, monitoring_service):
        """Test cleanup of old metrics."""
        # Add old metrics
        old_time = datetime.utcnow() - timedelta(days=35)
        old_metrics = LocationAccuracyMetrics(
            timestamp=old_time,
            location_id="old_location",
            expected_coordinates=(40.7128, -74.0060),
            actual_coordinates=(40.7130, -74.0058),
            accuracy_meters=25.5,
            accuracy_level=LocationAccuracyLevel.MEDIUM,
            validation_method="gps",
            confidence_score=0.85,
            processing_time_ms=150.0
        )
        
        monitoring_service.location_accuracy_metrics.append(old_metrics)
        
        # Clean up metrics older than 30 days
        await monitoring_service.cleanup_old_metrics(30)
        
        # Check that old metrics were removed
        assert len(monitoring_service.location_accuracy_metrics) == 0

class TestLocationProductionAnalyticsService:
    """Test suite for LocationProductionAnalyticsService."""
    
    @pytest.fixture
    def analytics_service(self):
        """Create analytics service instance for testing."""
        return LocationProductionAnalyticsService()
    
    @pytest.mark.asyncio
    async def test_analytics_service_initialization(self, analytics_service):
        """Test analytics service initialization."""
        assert analytics_service is not None
        assert analytics_service.analytics_config is not None
        assert len(analytics_service.analytics_config["thresholds"]) > 0
    
    @pytest.mark.asyncio
    async def test_usage_patterns_analysis(self, analytics_service):
        """Test usage patterns analysis."""
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()
        
        patterns = await analytics_service.analyze_usage_patterns(start_date, end_date)
        
        assert "peak_hours" in patterns
        assert "geographic_distribution" in patterns
        assert "user_behavior" in patterns
        assert "service_usage" in patterns
        assert "error_patterns" in patterns
    
    @pytest.mark.asyncio
    async def test_accuracy_report_generation(self, analytics_service):
        """Test accuracy report generation."""
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()
        
        report = await analytics_service.generate_accuracy_report(start_date, end_date)
        
        assert report.report_id is not None
        assert report.report_type == "accuracy_analysis"
        assert report.summary is not None
        assert report.detailed_metrics is not None
        assert len(report.insights) > 0
        assert len(report.recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_performance_report_generation(self, analytics_service):
        """Test performance report generation."""
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()
        
        report = await analytics_service.generate_performance_report(start_date, end_date)
        
        assert report.report_id is not None
        assert report.report_type == "performance_analysis"
        assert report.summary is not None
        assert report.detailed_metrics is not None
        assert len(report.insights) > 0
        assert len(report.recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_user_experience_report_generation(self, analytics_service):
        """Test user experience report generation."""
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()
        
        report = await analytics_service.generate_user_experience_report(start_date, end_date)
        
        assert report.report_id is not None
        assert report.report_type == "user_experience_analysis"
        assert report.summary is not None
        assert report.detailed_metrics is not None
        assert len(report.insights) > 0
        assert len(report.recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_business_metrics_calculation(self, analytics_service):
        """Test business metrics calculation."""
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
        
        metrics = await analytics_service.calculate_business_metrics(start_date, end_date)
        
        assert len(metrics) > 0
        for metric in metrics:
            assert metric.metric_id is not None
            assert metric.metric_name is not None
            assert metric.value >= 0
            assert metric.unit is not None
            assert metric.trend in ["increasing", "decreasing", "stable"]
    
    @pytest.mark.asyncio
    async def test_analytics_dashboard_data(self, analytics_service):
        """Test analytics dashboard data generation."""
        dashboard_data = await analytics_service.get_analytics_dashboard_data()
        
        assert "timestamp" in dashboard_data
        assert "summary" in dashboard_data
        assert "recent_reports" in dashboard_data
        assert "key_metrics" in dashboard_data
        assert "usage_insights" in dashboard_data
    
    @pytest.mark.asyncio
    async def test_report_export(self, analytics_service):
        """Test report export functionality."""
        # Generate a report first
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()
        report = await analytics_service.generate_accuracy_report(start_date, end_date)
        
        # Export the report
        exported_data = await analytics_service.export_report(report.report_id, "json")
        
        assert "report_id" in exported_data
        assert "report_type" in exported_data
        assert "summary" in exported_data
        assert "detailed_metrics" in exported_data

class TestLocationPrometheusMetricsCollector:
    """Test suite for LocationPrometheusMetricsCollector."""
    
    @pytest.fixture
    def prometheus_collector(self):
        """Create Prometheus metrics collector for testing."""
        try:
            return LocationPrometheusMetricsCollector()
        except ImportError:
            pytest.skip("Prometheus client not available")
    
    def test_prometheus_collector_initialization(self, prometheus_collector):
        """Test Prometheus metrics collector initialization."""
        assert prometheus_collector is not None
        assert prometheus_collector.registry is not None
        assert len(prometheus_collector.metrics) > 0
    
    def test_location_accuracy_recording(self, prometheus_collector):
        """Test location accuracy metrics recording."""
        prometheus_collector.record_location_accuracy(
            accuracy_meters=25.5,
            validation_method="gps",
            accuracy_level="medium",
            confidence_score=0.85
        )
        
        # Check that metrics were recorded (this would require accessing internal state)
        assert prometheus_collector.metrics["location_accuracy_meters"] is not None
    
    def test_service_request_recording(self, prometheus_collector):
        """Test service request metrics recording."""
        prometheus_collector.record_service_request(
            service_name="location_validation",
            endpoint="/api/v1/locations/validate",
            method="POST",
            status_code=200,
            duration_seconds=0.245
        )
        
        assert prometheus_collector.metrics["location_service_request_duration_seconds"] is not None
        assert prometheus_collector.metrics["location_service_requests_total"] is not None
    
    def test_cache_metrics_recording(self, prometheus_collector):
        """Test cache metrics recording."""
        prometheus_collector.record_cache_metrics(
            cache_type="location_cache",
            service_name="location_validation",
            hit=True
        )
        
        prometheus_collector.record_cache_metrics(
            cache_type="location_cache",
            service_name="location_validation",
            hit=False
        )
        
        assert prometheus_collector.metrics["location_cache_hits_total"] is not None
        assert prometheus_collector.metrics["location_cache_misses_total"] is not None
        assert prometheus_collector.metrics["location_cache_hit_rate"] is not None
    
    def test_user_action_recording(self, prometheus_collector):
        """Test user action metrics recording."""
        prometheus_collector.record_user_action(
            action_type="location_input",
            result="success",
            satisfaction=0.87,
            session_duration_seconds=120.0
        )
        
        assert prometheus_collector.metrics["location_user_actions_total"] is not None
        assert prometheus_collector.metrics["location_user_satisfaction"] is not None
        assert prometheus_collector.metrics["location_user_session_duration_seconds"] is not None
    
    def test_business_metrics_recording(self, prometheus_collector):
        """Test business metrics recording."""
        prometheus_collector.record_business_metric("revenue_impact", 12500.0, "monthly")
        prometheus_collector.record_business_metric("cost_savings", 8500.0, "monthly")
        prometheus_collector.record_business_metric("user_growth", 12.5, "monthly")
        
        assert prometheus_collector.metrics["location_business_revenue_impact"] is not None
        assert prometheus_collector.metrics["location_business_cost_savings"] is not None
        assert prometheus_collector.metrics["location_business_user_growth"] is not None
    
    def test_system_resource_recording(self, prometheus_collector):
        """Test system resource metrics recording."""
        prometheus_collector.record_system_resource(
            service_name="location_validation",
            cpu_percent=45.2,
            memory_percent=62.8,
            disk_percent=35.5
        )
        
        assert prometheus_collector.metrics["location_system_cpu_usage_percent"] is not None
        assert prometheus_collector.metrics["location_system_memory_usage_percent"] is not None
        assert prometheus_collector.metrics["location_system_disk_usage_percent"] is not None
    
    def test_error_recording(self, prometheus_collector):
        """Test error metrics recording."""
        prometheus_collector.record_error(
            error_type="ValidationError",
            service_name="location_validation",
            severity="warning"
        )
        
        assert prometheus_collector.metrics["location_errors_total"] is not None
    
    def test_alert_recording(self, prometheus_collector):
        """Test alert metrics recording."""
        prometheus_collector.record_alert(
            alert_level="warning",
            category="location_accuracy",
            active=True
        )
        
        assert prometheus_collector.metrics["location_alerts_active"] is not None
    
    def test_geocoding_metrics_recording(self, prometheus_collector):
        """Test geocoding metrics recording."""
        prometheus_collector.record_geocoding_request(
            provider="nominatim",
            result="success",
            response_time_seconds=0.320
        )
        
        assert prometheus_collector.metrics["geocoding_requests_total"] is not None
        assert prometheus_collector.metrics["geocoding_response_time_seconds"] is not None
    
    def test_gps_metrics_recording(self, prometheus_collector):
        """Test GPS metrics recording."""
        prometheus_collector.record_gps_metrics(
            accuracy_meters=8.5,
            fix_time_seconds=3.2,
            device_type="mobile",
            environment="outdoor"
        )
        
        assert prometheus_collector.metrics["gps_accuracy_meters"] is not None
        assert prometheus_collector.metrics["gps_fix_time_seconds"] is not None
    
    def test_metrics_generation(self, prometheus_collector):
        """Test metrics generation in Prometheus format."""
        metrics_text = prometheus_collector.get_metrics()
        
        assert isinstance(metrics_text, str)
        assert len(metrics_text) > 0
        assert "# HELP" in metrics_text  # Prometheus help text
        assert "# TYPE" in metrics_text  # Prometheus type text
    
    def test_metric_summary(self, prometheus_collector):
        """Test metric summary generation."""
        summary = prometheus_collector.get_metric_summary()
        
        assert isinstance(summary, dict)
        assert len(summary) > 0
        
        for metric_name, metric_info in summary.items():
            assert "type" in metric_info
            assert "description" in metric_info
            assert "labels" in metric_info

class TestLocationMonitoringIntegrationService:
    """Test suite for LocationMonitoringIntegrationService."""
    
    @pytest.fixture
    def integration_service(self):
        """Create integration service instance for testing."""
        return LocationMonitoringIntegrationService()
    
    @pytest.mark.asyncio
    async def test_integration_service_initialization(self, integration_service):
        """Test integration service initialization."""
        assert integration_service is not None
        assert integration_service.monitoring_service is not None
        assert integration_service.analytics_service is not None
        assert not integration_service.integration_active
    
    @pytest.mark.asyncio
    async def test_service_registration(self, integration_service):
        """Test service registration for monitoring."""
        service_name = "test_service"
        endpoints = ["/api/v1/test", "/api/v1/test/validate"]
        
        integration_service.register_service(
            service_name=service_name,
            endpoints=endpoints,
            monitoring_enabled=True,
            analytics_enabled=True,
            prometheus_enabled=True
        )
        
        assert service_name in integration_service.integrations
        integration = integration_service.integrations[service_name]
        assert integration.service_name == service_name
        assert integration.endpoints == endpoints
        assert integration.monitoring_enabled
        assert integration.analytics_enabled
        assert integration.prometheus_enabled
    
    @pytest.mark.asyncio
    async def test_service_unregistration(self, integration_service):
        """Test service unregistration."""
        service_name = "test_service"
        endpoints = ["/api/v1/test"]
        
        # Register service
        integration_service.register_service(service_name, endpoints)
        assert service_name in integration_service.integrations
        
        # Unregister service
        integration_service.unregister_service(service_name)
        assert service_name not in integration_service.integrations
    
    @pytest.mark.asyncio
    async def test_location_accuracy_recording_with_monitoring(self, integration_service):
        """Test location accuracy recording with full monitoring integration."""
        await integration_service.record_location_accuracy_with_monitoring(
            location_id="test_location",
            expected_coordinates=(40.7128, -74.0060),
            actual_coordinates=(40.7130, -74.0058),
            validation_method="gps",
            processing_time_ms=150.0,
            user_feedback=0.9
        )
        
        # Check that metrics were recorded in monitoring service
        assert len(integration_service.monitoring_service.location_accuracy_metrics) == 1
    
    @pytest.mark.asyncio
    async def test_user_experience_recording_with_monitoring(self, integration_service):
        """Test user experience recording with full monitoring integration."""
        await integration_service.record_user_experience_with_monitoring(
            user_id="user_123",
            session_id="session_456",
            action_type="location_input",
            success=True,
            time_to_complete_ms=1200.0,
            user_satisfaction=0.87,
            retry_count=0
        )
        
        # Check that metrics were recorded in monitoring service
        assert len(integration_service.monitoring_service.user_experience_metrics) == 1
    
    @pytest.mark.asyncio
    async def test_monitoring_decorator_creation(self, integration_service):
        """Test monitoring decorator creation."""
        decorator = integration_service.create_monitoring_decorator(
            "test_service", "/api/v1/test"
        )
        
        assert callable(decorator)
        
        # Test decorator with async function
        @decorator
        async def test_async_function():
            return "success"
        
        result = await test_async_function()
        assert result == "success"
        
        # Check that metrics were recorded
        assert len(integration_service.monitoring_service.service_performance_metrics) == 1
    
    @pytest.mark.asyncio
    async def test_integration_status(self, integration_service):
        """Test integration status retrieval."""
        status = await integration_service.get_integration_status()
        
        assert "integration_active" in status
        assert "monitoring_active" in status
        assert "prometheus_enabled" in status
        assert "registered_services" in status
        assert "service_count" in status
        assert "timestamp" in status
    
    @pytest.mark.asyncio
    async def test_combined_dashboard_data(self, integration_service):
        """Test combined dashboard data generation."""
        dashboard_data = await integration_service.get_combined_dashboard_data()
        
        assert "timestamp" in dashboard_data
        assert "monitoring" in dashboard_data
        assert "analytics" in dashboard_data
        assert "integration_status" in dashboard_data
    
    @pytest.mark.asyncio
    async def test_comprehensive_report_generation(self, integration_service):
        """Test comprehensive report generation."""
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()
        
        report = await integration_service.generate_comprehensive_report(start_date, end_date)
        
        assert "report_id" in report
        assert "report_type" in report
        assert "reports" in report
        assert "current_monitoring" in report
        assert "business_metrics" in report
        assert "integration_status" in report
        assert "summary" in report
    
    def test_service_integrations_info(self, integration_service):
        """Test service integrations information retrieval."""
        # Register a test service
        integration_service.register_service(
            "test_service",
            ["/api/v1/test"],
            monitoring_enabled=True,
            analytics_enabled=True,
            prometheus_enabled=True
        )
        
        integrations_info = integration_service.get_service_integrations()
        
        assert "test_service" in integrations_info
        service_info = integrations_info["test_service"]
        assert service_info["service_name"] == "test_service"
        assert service_info["monitoring_enabled"]
        assert service_info["analytics_enabled"]
        assert service_info["prometheus_enabled"]
    
    def test_distance_calculation(self, integration_service):
        """Test distance calculation between coordinates."""
        # Test distance between New York and Philadelphia (approximately 95 km)
        ny_coords = (40.7128, -74.0060)
        philly_coords = (39.9526, -75.1652)
        
        distance = integration_service._calculate_distance(ny_coords, philly_coords)
        
        # Should be approximately 95,000 meters (95 km)
        assert 90000 < distance < 100000  # Allow some tolerance
    
    @pytest.mark.asyncio
    async def test_cleanup_all_data(self, integration_service):
        """Test cleanup of all monitoring data."""
        # Add some test data
        await integration_service.monitoring_service.record_location_accuracy(
            location_id="test_location",
            expected_coordinates=(40.7128, -74.0060),
            actual_coordinates=(40.7130, -74.0058),
            validation_method="gps",
            processing_time_ms=150.0
        )
        
        # Clean up data
        await integration_service.cleanup_all_data(0)  # Clean up all data
        
        # Check that data was cleaned up
        assert len(integration_service.monitoring_service.location_accuracy_metrics) == 0

# Integration tests
class TestProductionMonitoringIntegration:
    """Integration tests for the complete production monitoring system."""
    
    @pytest.fixture
    def full_monitoring_system(self):
        """Create a complete monitoring system for integration testing."""
        return LocationMonitoringIntegrationService()
    
    @pytest.mark.asyncio
    async def test_end_to_end_monitoring_workflow(self, full_monitoring_system):
        """Test complete end-to-end monitoring workflow."""
        # Start the monitoring system
        await full_monitoring_system.start_integration()
        
        # Register a service
        full_monitoring_system.register_service(
            "location_validation",
            ["/api/v1/locations/validate", "/api/v1/locations/create"],
            monitoring_enabled=True,
            analytics_enabled=True,
            prometheus_enabled=True
        )
        
        # Record various metrics
        await full_monitoring_system.record_location_accuracy_with_monitoring(
            location_id="integration_test_location",
            expected_coordinates=(40.7128, -74.0060),
            actual_coordinates=(40.7130, -74.0058),
            validation_method="gps",
            processing_time_ms=150.0,
            user_feedback=0.9
        )
        
        await full_monitoring_system.record_user_experience_with_monitoring(
            user_id="integration_test_user",
            session_id="integration_test_session",
            action_type="location_input",
            success=True,
            time_to_complete_ms=1200.0,
            user_satisfaction=0.87
        )
        
        # Wait a bit for background processing
        await asyncio.sleep(1)
        
        # Get dashboard data
        dashboard_data = await full_monitoring_system.get_combined_dashboard_data()
        
        # Verify data is present
        assert "monitoring" in dashboard_data
        assert "analytics" in dashboard_data
        assert "integration_status" in dashboard_data
        
        # Stop the monitoring system
        await full_monitoring_system.stop_integration()
        
        # Verify it's stopped
        status = await full_monitoring_system.get_integration_status()
        assert not status["integration_active"]
    
    @pytest.mark.asyncio
    async def test_prometheus_metrics_integration(self, full_monitoring_system):
        """Test Prometheus metrics integration."""
        if not full_monitoring_system.prometheus_enabled:
            pytest.skip("Prometheus not available")
        
        # Start monitoring
        await full_monitoring_system.start_integration()
        
        # Record metrics
        await full_monitoring_system.record_location_accuracy_with_monitoring(
            location_id="prometheus_test_location",
            expected_coordinates=(40.7128, -74.0060),
            actual_coordinates=(40.7130, -74.0058),
            validation_method="gps",
            processing_time_ms=150.0
        )
        
        # Get Prometheus metrics
        metrics_text = full_monitoring_system.get_prometheus_metrics()
        content_type = full_monitoring_system.get_prometheus_content_type()
        
        assert isinstance(metrics_text, str)
        assert len(metrics_text) > 0
        assert content_type == "text/plain; version=0.0.4; charset=utf-8"
        
        # Stop monitoring
        await full_monitoring_system.stop_integration()
    
    @pytest.mark.asyncio
    async def test_analytics_report_generation_integration(self, full_monitoring_system):
        """Test analytics report generation in integrated system."""
        # Generate comprehensive report
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()
        
        report = await full_monitoring_system.generate_comprehensive_report(start_date, end_date)
        
        # Verify report structure
        assert "report_id" in report
        assert "reports" in report
        assert "accuracy" in report["reports"]
        assert "performance" in report["reports"]
        assert "user_experience" in report["reports"]
        assert "current_monitoring" in report
        assert "business_metrics" in report
        assert "integration_status" in report

# Performance tests
class TestProductionMonitoringPerformance:
    """Performance tests for the production monitoring system."""
    
    @pytest.fixture
    def monitoring_service(self):
        """Create monitoring service for performance testing."""
        return LocationProductionMonitoringService()
    
    @pytest.mark.asyncio
    async def test_high_volume_metrics_recording(self, monitoring_service):
        """Test recording high volume of metrics."""
        start_time = time.time()
        
        # Record 1000 metrics
        for i in range(1000):
            await monitoring_service.record_location_accuracy(
                location_id=f"perf_test_location_{i}",
                expected_coordinates=(40.7128, -74.0060),
                actual_coordinates=(40.7130, -74.0058),
                validation_method="gps",
                processing_time_ms=150.0
            )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within reasonable time (less than 10 seconds)
        assert duration < 10.0
        assert len(monitoring_service.location_accuracy_metrics) == 1000
    
    @pytest.mark.asyncio
    async def test_dashboard_data_performance(self, monitoring_service):
        """Test dashboard data generation performance."""
        # Add some test data
        for i in range(100):
            await monitoring_service.record_location_accuracy(
                location_id=f"dashboard_test_location_{i}",
                expected_coordinates=(40.7128, -74.0060),
                actual_coordinates=(40.7130, -74.0058),
                validation_method="gps",
                processing_time_ms=150.0
            )
        
        start_time = time.time()
        dashboard_data = await monitoring_service.get_monitoring_dashboard_data()
        end_time = time.time()
        
        duration = end_time - start_time
        
        # Should generate dashboard data quickly (less than 1 second)
        assert duration < 1.0
        assert "timestamp" in dashboard_data
        assert "location_accuracy" in dashboard_data