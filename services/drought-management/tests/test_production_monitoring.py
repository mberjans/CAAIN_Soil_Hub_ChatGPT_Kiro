"""
Tests for Production Monitoring Service

Comprehensive test suite for production monitoring, analytics, alerting, and reporting.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from uuid import uuid4

from src.services.production_monitoring_service import ProductionMonitoringService
from src.services.production_analytics_service import ProductionAnalyticsService
from src.services.production_alerting_service import ProductionAlertingService
from src.services.production_reporting_service import ProductionReportingService
from src.models.production_monitoring_models import (
    SystemPerformanceMetrics,
    UserEngagementMetrics,
    RecommendationEffectivenessMetrics,
    AgriculturalImpactMetrics,
    ProductionHealthStatus,
    RealTimeMetrics,
    HistoricalMetrics
)
from src.models.production_analytics_models import (
    UsagePatternAnalysis,
    SuccessMetricsAnalysis,
    AgriculturalImpactAnalysis,
    AnalyticsReport
)
from src.models.production_alerting_models import (
    AlertRuleRequest,
    AlertCondition,
    AlertSeverity,
    ComparisonOperator
)
from src.models.production_reporting_models import (
    ReportGenerationRequest,
    ReportType,
    ReportFormat
)

class TestProductionMonitoringService:
    """Test suite for Production Monitoring Service."""
    
    @pytest.fixture
    def service(self):
        return ProductionMonitoringService()
    
    @pytest.mark.asyncio
    async def test_initialize(self, service):
        """Test service initialization."""
        await service.initialize()
        assert service.initialized is True
        assert service.monitoring_config is not None
        assert len(service.alert_configurations) > 0
        assert len(service.performance_thresholds) > 0
    
    @pytest.mark.asyncio
    async def test_cleanup(self, service):
        """Test service cleanup."""
        await service.initialize()
        await service.cleanup()
        # Service should be cleaned up without errors
    
    @pytest.mark.asyncio
    async def test_get_system_performance_metrics(self, service):
        """Test system performance metrics retrieval."""
        await service.initialize()
        
        metrics = await service.get_system_performance_metrics(time_range_hours=24)
        
        assert isinstance(metrics, SystemPerformanceMetrics)
        assert 0 <= metrics.cpu_usage_percent <= 100
        assert 0 <= metrics.memory_usage_percent <= 100
        assert 0 <= metrics.disk_usage_percent <= 100
        assert metrics.network_bytes_sent >= 0
        assert metrics.network_bytes_received >= 0
        assert metrics.process_count >= 0
        assert metrics.python_memory_bytes >= 0
    
    @pytest.mark.asyncio
    async def test_get_user_engagement_metrics(self, service):
        """Test user engagement metrics retrieval."""
        await service.initialize()
        
        metrics = await service.get_user_engagement_metrics(time_range_hours=24)
        
        assert isinstance(metrics, UserEngagementMetrics)
        assert metrics.daily_active_users >= 0
        assert metrics.avg_session_duration_minutes >= 0
        assert metrics.requests_per_minute >= 0
        assert isinstance(metrics.feature_usage_stats, dict)
    
    @pytest.mark.asyncio
    async def test_get_recommendation_effectiveness_metrics(self, service):
        """Test recommendation effectiveness metrics retrieval."""
        await service.initialize()
        
        metrics = await service.get_recommendation_effectiveness_metrics(time_range_hours=24)
        
        assert isinstance(metrics, RecommendationEffectivenessMetrics)
        assert 0 <= metrics.recommendation_accuracy_percent <= 100
        assert metrics.recommendations_per_day >= 0
        assert 0 <= metrics.user_satisfaction_score <= 5
        assert 0 <= metrics.implementation_rate_percent <= 100
    
    @pytest.mark.asyncio
    async def test_get_agricultural_impact_metrics(self, service):
        """Test agricultural impact metrics retrieval."""
        await service.initialize()
        
        metrics = await service.get_agricultural_impact_metrics(time_range_hours=24)
        
        assert isinstance(metrics, AgriculturalImpactMetrics)
        assert metrics.total_water_savings_gallons >= 0
        assert metrics.farms_with_conservation_practices >= 0
        assert 0 <= metrics.drought_risk_reduction_percent <= 100
        assert metrics.total_cost_savings_dollars >= 0
    
    @pytest.mark.asyncio
    async def test_get_production_health_status(self, service):
        """Test production health status retrieval."""
        await service.initialize()
        
        health_status = await service.get_production_health_status()
        
        assert isinstance(health_status, ProductionHealthStatus)
        assert 0 <= health_status.overall_health_score <= 100
        assert isinstance(health_status.system_performance, SystemPerformanceMetrics)
        assert isinstance(health_status.user_engagement, UserEngagementMetrics)
        assert isinstance(health_status.recommendation_effectiveness, RecommendationEffectivenessMetrics)
        assert isinstance(health_status.active_alerts, list)
    
    @pytest.mark.asyncio
    async def test_get_real_time_metrics(self, service):
        """Test real-time metrics retrieval."""
        await service.initialize()
        
        metrics = await service.get_real_time_metrics()
        
        assert isinstance(metrics, RealTimeMetrics)
        assert isinstance(metrics.metrics, dict)
        assert isinstance(metrics.timestamp, datetime)
        assert isinstance(metrics.collection_active, bool)
    
    @pytest.mark.asyncio
    async def test_get_historical_metrics(self, service):
        """Test historical metrics retrieval."""
        await service.initialize()
        
        metrics = await service.get_historical_metrics("cpu_usage_percent", hours=24)
        
        assert isinstance(metrics, HistoricalMetrics)
        assert metrics.metric_name == "cpu_usage_percent"
        assert metrics.time_range_hours == 24
        assert isinstance(metrics.data_points, list)
        assert metrics.total_points >= 0
    
    @pytest.mark.asyncio
    async def test_generate_production_report(self, service):
        """Test production report generation."""
        await service.initialize()
        
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()
        
        report = await service.generate_production_report(start_date, end_date)
        
        assert report.report_id is not None
        assert report.start_date == start_date
        assert report.end_date == end_date
        assert isinstance(report.system_performance, SystemPerformanceMetrics)
        assert isinstance(report.user_engagement, UserEngagementMetrics)
        assert isinstance(report.recommendation_effectiveness, RecommendationEffectivenessMetrics)
        assert isinstance(report.agricultural_impact, AgriculturalImpactMetrics)
        assert isinstance(report.performance_trends, list)
        assert isinstance(report.summary, dict)

class TestProductionAnalyticsService:
    """Test suite for Production Analytics Service."""
    
    @pytest.fixture
    def service(self):
        return ProductionAnalyticsService()
    
    @pytest.mark.asyncio
    async def test_initialize(self, service):
        """Test service initialization."""
        await service.initialize()
        assert service.initialized is True
        assert service.analytics_cache is not None
    
    @pytest.mark.asyncio
    async def test_cleanup(self, service):
        """Test service cleanup."""
        await service.initialize()
        await service.cleanup()
        # Service should be cleaned up without errors
    
    @pytest.mark.asyncio
    async def test_analyze_usage_patterns(self, service):
        """Test usage pattern analysis."""
        await service.initialize()
        
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()
        
        analysis = await service.analyze_usage_patterns(start_date, end_date)
        
        assert isinstance(analysis, UsagePatternAnalysis)
        assert analysis.start_date == start_date
        assert analysis.end_date == end_date
        assert analysis.total_users >= 0
        assert analysis.total_requests >= 0
        assert analysis.avg_requests_per_user >= 0
        assert isinstance(analysis.peak_usage_times, dict)
        assert isinstance(analysis.usage_trends, dict)
        assert isinstance(analysis.seasonal_patterns, dict)
        assert isinstance(analysis.user_behavior_patterns, dict)
    
    @pytest.mark.asyncio
    async def test_analyze_success_metrics(self, service):
        """Test success metrics analysis."""
        await service.initialize()
        
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()
        
        analysis = await service.analyze_success_metrics(start_date, end_date)
        
        assert isinstance(analysis, SuccessMetricsAnalysis)
        assert analysis.start_date == start_date
        assert analysis.end_date == end_date
        assert isinstance(analysis.user_satisfaction, dict)
        assert isinstance(analysis.recommendation_effectiveness, dict)
        assert isinstance(analysis.system_reliability, dict)
        assert isinstance(analysis.business_metrics, dict)
    
    @pytest.mark.asyncio
    async def test_analyze_agricultural_impact(self, service):
        """Test agricultural impact analysis."""
        await service.initialize()
        
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()
        
        analysis = await service.analyze_agricultural_impact(start_date, end_date)
        
        assert isinstance(analysis, AgriculturalImpactAnalysis)
        assert analysis.start_date == start_date
        assert analysis.end_date == end_date
        assert isinstance(analysis.water_savings_analysis, dict)
        assert isinstance(analysis.cost_savings_analysis, dict)
        assert isinstance(analysis.environmental_impact, dict)
        assert isinstance(analysis.farm_productivity, dict)
    
    @pytest.mark.asyncio
    async def test_generate_comprehensive_analytics_report(self, service):
        """Test comprehensive analytics report generation."""
        await service.initialize()
        
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()
        
        report = await service.generate_comprehensive_analytics_report(start_date, end_date)
        
        assert isinstance(report, AnalyticsReport)
        assert report.start_date == start_date
        assert report.end_date == end_date
        assert isinstance(report.usage_patterns, UsagePatternAnalysis)
        assert isinstance(report.success_metrics, SuccessMetricsAnalysis)
        assert isinstance(report.agricultural_impact, AgriculturalImpactAnalysis)
        assert isinstance(report.insights, list)
        assert isinstance(report.summary, dict)

class TestProductionAlertingService:
    """Test suite for Production Alerting Service."""
    
    @pytest.fixture
    def service(self):
        return ProductionAlertingService()
    
    @pytest.mark.asyncio
    async def test_initialize(self, service):
        """Test service initialization."""
        await service.initialize()
        assert service.initialized is True
        assert len(service.alert_rules) > 0
        assert len(service.notification_channels) > 0
        assert len(service.escalation_policies) > 0
        assert len(service.suppression_rules) > 0
        assert len(service.alert_templates) > 0
    
    @pytest.mark.asyncio
    async def test_cleanup(self, service):
        """Test service cleanup."""
        await service.initialize()
        await service.cleanup()
        # Service should be cleaned up without errors
    
    @pytest.mark.asyncio
    async def test_create_alert_rule(self, service):
        """Test alert rule creation."""
        await service.initialize()
        
        request = AlertRuleRequest(
            name="Test Alert Rule",
            description="Test alert rule for unit testing",
            conditions=[
                AlertCondition(
                    metric_name="cpu_usage_percent",
                    operator=ComparisonOperator.GREATER_THAN,
                    threshold_value=80.0,
                    evaluation_window_minutes=5
                )
            ],
            severity=AlertSeverity.HIGH,
            enabled=True,
            cooldown_minutes=15
        )
        
        response = await service.create_alert_rule(request)
        
        assert response.success is True
        assert response.rule_id is not None
        assert len(response.errors) == 0
    
    @pytest.mark.asyncio
    async def test_acknowledge_alert(self, service):
        """Test alert acknowledgment."""
        await service.initialize()
        
        # Create a test alert first
        alert_id = str(uuid4())
        service.active_alerts[alert_id] = MagicMock()
        service.active_alerts[alert_id].acknowledged = False
        
        success = await service.acknowledge_alert(alert_id, "test_user")
        
        assert success is True
    
    @pytest.mark.asyncio
    async def test_resolve_alert(self, service):
        """Test alert resolution."""
        await service.initialize()
        
        # Create a test alert first
        alert_id = str(uuid4())
        service.active_alerts[alert_id] = MagicMock()
        service.active_alerts[alert_id].resolved = False
        
        success = await service.resolve_alert(alert_id, "test_user")
        
        assert success is True
    
    @pytest.mark.asyncio
    async def test_get_active_alerts(self, service):
        """Test active alerts retrieval."""
        await service.initialize()
        
        alerts = await service.get_active_alerts()
        
        assert isinstance(alerts, list)
    
    @pytest.mark.asyncio
    async def test_get_alert_metrics(self, service):
        """Test alert metrics retrieval."""
        await service.initialize()
        
        from src.models.production_alerting_models import AlertMetricsRequest
        request = AlertMetricsRequest()
        
        response = await service.get_alert_metrics(request)
        
        assert response.success is True
        assert response.metrics is not None
        assert response.metrics.total_alerts >= 0
        assert response.metrics.active_alerts >= 0
        assert response.metrics.acknowledged_alerts >= 0
        assert response.metrics.resolved_alerts >= 0
        assert 0 <= response.metrics.success_rate <= 100

class TestProductionReportingService:
    """Test suite for Production Reporting Service."""
    
    @pytest.fixture
    def service(self):
        return ProductionReportingService()
    
    @pytest.mark.asyncio
    async def test_initialize(self, service):
        """Test service initialization."""
        await service.initialize()
        assert service.initialized is True
        assert len(service.report_templates) > 0
        assert len(service.report_schedules) > 0
        assert len(service.report_configurations) > 0
    
    @pytest.mark.asyncio
    async def test_cleanup(self, service):
        """Test service cleanup."""
        await service.initialize()
        await service.cleanup()
        # Service should be cleaned up without errors
    
    @pytest.mark.asyncio
    async def test_generate_report(self, service):
        """Test report generation."""
        await service.initialize()
        
        request = ReportGenerationRequest(
            report_type=ReportType.SYSTEM_PERFORMANCE,
            time_period={
                "start": datetime.utcnow() - timedelta(days=7),
                "end": datetime.utcnow()
            },
            format=ReportFormat.HTML,
            include_charts=True,
            include_insights=True,
            include_recommendations=True
        )
        
        response = await service.generate_report(request)
        
        assert response.success is True
        assert response.report is not None
        assert response.report_id is not None
    
    @pytest.mark.asyncio
    async def test_get_report_history(self, service):
        """Test report history retrieval."""
        await service.initialize()
        
        history = await service.get_report_history(limit=10)
        
        assert isinstance(history, list)
        assert len(history) <= 10
    
    @pytest.mark.asyncio
    async def test_get_report_metrics(self, service):
        """Test report metrics retrieval."""
        await service.initialize()
        
        metrics = await service.get_report_metrics()
        
        assert metrics.total_reports >= 0
        assert metrics.successful_reports >= 0
        assert metrics.failed_reports >= 0
        assert 0 <= metrics.success_rate <= 100
        assert isinstance(metrics.reports_by_type, dict)

# Integration Tests
class TestProductionMonitoringIntegration:
    """Integration tests for production monitoring components."""
    
    @pytest.mark.asyncio
    async def test_full_monitoring_workflow(self):
        """Test complete monitoring workflow."""
        # Initialize monitoring service
        monitoring_service = ProductionMonitoringService()
        await monitoring_service.initialize()
        
        # Get health status
        health_status = await monitoring_service.get_production_health_status()
        assert health_status.overall_health_score >= 0
        
        # Get various metrics
        system_metrics = await monitoring_service.get_system_performance_metrics()
        user_metrics = await monitoring_service.get_user_engagement_metrics()
        recommendation_metrics = await monitoring_service.get_recommendation_effectiveness_metrics()
        agricultural_metrics = await monitoring_service.get_agricultural_impact_metrics()
        
        assert system_metrics is not None
        assert user_metrics is not None
        assert recommendation_metrics is not None
        assert agricultural_metrics is not None
        
        # Generate report
        start_date = datetime.utcnow() - timedelta(days=1)
        end_date = datetime.utcnow()
        report = await monitoring_service.generate_production_report(start_date, end_date)
        
        assert report is not None
        assert report.report_id is not None
        
        # Cleanup
        await monitoring_service.cleanup()
    
    @pytest.mark.asyncio
    async def test_analytics_and_reporting_integration(self):
        """Test analytics and reporting integration."""
        # Initialize services
        analytics_service = ProductionAnalyticsService()
        reporting_service = ProductionReportingService()
        
        await analytics_service.initialize()
        await reporting_service.initialize()
        
        # Generate analytics report
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()
        
        analytics_report = await analytics_service.generate_comprehensive_analytics_report(start_date, end_date)
        assert analytics_report is not None
        
        # Generate production report
        report_request = ReportGenerationRequest(
            report_type=ReportType.COMPREHENSIVE,
            time_period={"start": start_date, "end": end_date},
            format=ReportFormat.HTML
        )
        
        report_response = await reporting_service.generate_report(report_request)
        assert report_response.success is True
        
        # Cleanup
        await analytics_service.cleanup()
        await reporting_service.cleanup()
    
    @pytest.mark.asyncio
    async def test_alerting_workflow(self):
        """Test alerting workflow."""
        # Initialize alerting service
        alerting_service = ProductionAlertingService()
        await alerting_service.initialize()
        
        # Create alert rule
        request = AlertRuleRequest(
            name="Integration Test Alert",
            description="Alert rule for integration testing",
            conditions=[
                AlertCondition(
                    metric_name="cpu_usage_percent",
                    operator=ComparisonOperator.GREATER_THAN,
                    threshold_value=90.0,
                    evaluation_window_minutes=5
                )
            ],
            severity=AlertSeverity.CRITICAL,
            enabled=True,
            cooldown_minutes=5
        )
        
        response = await alerting_service.create_alert_rule(request)
        assert response.success is True
        
        # Get alert metrics
        from src.models.production_alerting_models import AlertMetricsRequest
        metrics_request = AlertMetricsRequest()
        metrics_response = await alerting_service.get_alert_metrics(metrics_request)
        assert metrics_response.success is True
        
        # Cleanup
        await alerting_service.cleanup()

# Performance Tests
class TestProductionMonitoringPerformance:
    """Performance tests for production monitoring components."""
    
    @pytest.mark.asyncio
    async def test_metrics_collection_performance(self):
        """Test metrics collection performance."""
        service = ProductionMonitoringService()
        await service.initialize()
        
        # Test multiple concurrent metric requests
        tasks = []
        for _ in range(10):
            task = service.get_system_performance_metrics(time_range_hours=1)
            tasks.append(task)
        
        start_time = datetime.utcnow()
        results = await asyncio.gather(*tasks)
        end_time = datetime.utcnow()
        
        # All requests should complete successfully
        assert len(results) == 10
        for result in results:
            assert isinstance(result, SystemPerformanceMetrics)
        
        # Should complete within reasonable time (adjust threshold as needed)
        duration = (end_time - start_time).total_seconds()
        assert duration < 5.0  # 5 seconds for 10 concurrent requests
        
        await service.cleanup()
    
    @pytest.mark.asyncio
    async def test_report_generation_performance(self):
        """Test report generation performance."""
        service = ProductionReportingService()
        await service.initialize()
        
        request = ReportGenerationRequest(
            report_type=ReportType.SYSTEM_PERFORMANCE,
            time_period={
                "start": datetime.utcnow() - timedelta(days=1),
                "end": datetime.utcnow()
            },
            format=ReportFormat.HTML
        )
        
        start_time = datetime.utcnow()
        response = await service.generate_report(request)
        end_time = datetime.utcnow()
        
        assert response.success is True
        
        # Report generation should complete within reasonable time
        duration = (end_time - start_time).total_seconds()
        assert duration < 10.0  # 10 seconds for report generation
        
        await service.cleanup()

if __name__ == "__main__":
    pytest.main([__file__])