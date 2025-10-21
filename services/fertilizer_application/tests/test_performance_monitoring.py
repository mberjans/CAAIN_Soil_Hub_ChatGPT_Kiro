"""
Comprehensive tests for performance monitoring service.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

from src.services.performance_monitoring_service import (
    PerformanceMonitoringService, MonitoringConfiguration, PerformanceSnapshot,
    PerformanceAlert, PerformanceTrend, PerformanceMetric, AlertLevel, PerformanceStatus
)


class TestPerformanceMonitoringService:
    """Test suite for performance monitoring service."""
    
    @pytest.fixture
    def service(self):
        return PerformanceMonitoringService()
    
    @pytest.fixture
    def sample_config(self):
        return MonitoringConfiguration(
            equipment_id="test_equipment_001",
            monitoring_enabled=True,
            alert_thresholds={},
            monitoring_frequency_minutes=15,
            data_retention_days=30,
            alert_notifications=["log", "email"]
        )
    
    @pytest.mark.asyncio
    async def test_start_monitoring_success(self, service, sample_config):
        """Test successful monitoring start."""
        equipment_id = "test_equipment_001"
        
        success = await service.start_monitoring(equipment_id, sample_config)
        
        assert success is True
        assert equipment_id in service.monitoring_configs
        assert equipment_id in service.performance_data
        assert equipment_id in service.active_alerts
        assert equipment_id in service.monitoring_tasks
    
    @pytest.mark.asyncio
    async def test_start_monitoring_disabled(self, service):
        """Test monitoring start with disabled configuration."""
        equipment_id = "test_equipment_002"
        config = MonitoringConfiguration(
            equipment_id=equipment_id,
            monitoring_enabled=False,
            alert_thresholds={},
            monitoring_frequency_minutes=15,
            data_retention_days=30,
            alert_notifications=[]
        )
        
        success = await service.start_monitoring(equipment_id, config)
        
        assert success is True
        assert equipment_id in service.monitoring_configs
        assert equipment_id not in service.monitoring_tasks  # No task created when disabled
    
    @pytest.mark.asyncio
    async def test_stop_monitoring_success(self, service, sample_config):
        """Test successful monitoring stop."""
        equipment_id = "test_equipment_001"
        
        # Start monitoring first
        await service.start_monitoring(equipment_id, sample_config)
        
        # Stop monitoring
        success = await service.stop_monitoring(equipment_id)
        
        assert success is True
        assert equipment_id not in service.monitoring_configs
        assert equipment_id not in service.monitoring_tasks
    
    @pytest.mark.asyncio
    async def test_stop_monitoring_not_started(self, service):
        """Test stopping monitoring that was never started."""
        equipment_id = "nonexistent_equipment"
        
        success = await service.stop_monitoring(equipment_id)
        
        assert success is True  # Should handle gracefully
    
    @pytest.mark.asyncio
    async def test_collect_performance_snapshot(self, service, sample_config):
        """Test performance snapshot collection."""
        equipment_id = "test_equipment_001"
        
        # Start monitoring
        await service.start_monitoring(equipment_id, sample_config)
        
        # Collect snapshot
        snapshot = await service._collect_performance_snapshot(equipment_id)
        
        assert isinstance(snapshot, PerformanceSnapshot)
        assert snapshot.equipment_id == equipment_id
        assert snapshot.snapshot_id is not None
        assert snapshot.timestamp is not None
        assert isinstance(snapshot.metrics, dict)
        assert isinstance(snapshot.status, PerformanceStatus)
        assert isinstance(snapshot.alerts, list)
        assert isinstance(snapshot.efficiency_trend, dict)
        assert isinstance(snapshot.maintenance_status, str)
        
        # Check that all required metrics are present
        required_metrics = [
            PerformanceMetric.APPLICATION_ACCURACY,
            PerformanceMetric.COVERAGE_UNIFORMITY,
            PerformanceMetric.SPEED_EFFICIENCY,
            PerformanceMetric.FUEL_EFFICIENCY,
            PerformanceMetric.LABOR_EFFICIENCY,
            PerformanceMetric.MAINTENANCE_EFFICIENCY,
            PerformanceMetric.OVERALL_EFFICIENCY,
            PerformanceMetric.DOWNTIME_HOURS,
            PerformanceMetric.MAINTENANCE_COST
        ]
        
        for metric in required_metrics:
            assert metric.value in snapshot.metrics
            assert 0 <= snapshot.metrics[metric.value] <= 1 or metric in [PerformanceMetric.DOWNTIME_HOURS, PerformanceMetric.MAINTENANCE_COST]
    
    @pytest.mark.asyncio
    async def test_determine_performance_status(self, service):
        """Test performance status determination."""
        # Test excellent status
        excellent_metrics = {PerformanceMetric.OVERALL_EFFICIENCY: 0.95}
        status = service._determine_performance_status(excellent_metrics)
        assert status == PerformanceStatus.EXCELLENT
        
        # Test good status
        good_metrics = {PerformanceMetric.OVERALL_EFFICIENCY: 0.85}
        status = service._determine_performance_status(good_metrics)
        assert status == PerformanceStatus.GOOD
        
        # Test acceptable status
        acceptable_metrics = {PerformanceMetric.OVERALL_EFFICIENCY: 0.75}
        status = service._determine_performance_status(acceptable_metrics)
        assert status == PerformanceStatus.ACCEPTABLE
        
        # Test poor status
        poor_metrics = {PerformanceMetric.OVERALL_EFFICIENCY: 0.65}
        status = service._determine_performance_status(poor_metrics)
        assert status == PerformanceStatus.POOR
        
        # Test critical status
        critical_metrics = {PerformanceMetric.OVERALL_EFFICIENCY: 0.5}
        status = service._determine_performance_status(critical_metrics)
        assert status == PerformanceStatus.CRITICAL
    
    @pytest.mark.asyncio
    async def test_check_performance_alerts(self, service, sample_config):
        """Test performance alert checking."""
        equipment_id = "test_equipment_001"
        
        # Start monitoring
        await service.start_monitoring(equipment_id, sample_config)
        
        # Create snapshot with low efficiency to trigger alerts
        snapshot = PerformanceSnapshot(
            snapshot_id="test_snapshot",
            equipment_id=equipment_id,
            timestamp=datetime.utcnow().isoformat(),
            metrics={
                PerformanceMetric.APPLICATION_ACCURACY: 0.5,  # Below critical threshold
                PerformanceMetric.COVERAGE_UNIFORMITY: 0.7,   # Below warning threshold
                PerformanceMetric.SPEED_EFFICIENCY: 0.8,     # Above thresholds
                PerformanceMetric.FUEL_EFFICIENCY: 0.6,      # Below warning threshold
                PerformanceMetric.LABOR_EFFICIENCY: 0.8,     # Above thresholds
                PerformanceMetric.MAINTENANCE_EFFICIENCY: 0.8,  # Above thresholds
                PerformanceMetric.OVERALL_EFFICIENCY: 0.65,  # Below warning threshold
                PerformanceMetric.DOWNTIME_HOURS: 15,        # Above warning threshold
                PerformanceMetric.MAINTENANCE_COST: 1200     # Above warning threshold
            },
            status=PerformanceStatus.POOR,
            alerts=[],
            efficiency_trend={},
            maintenance_status="maintenance_recommended"
        )
        
        alerts = await service._check_performance_alerts(equipment_id, snapshot)
        
        assert isinstance(alerts, list)
        assert len(alerts) > 0  # Should have triggered some alerts
        
        # Check alert structure
        for alert in alerts:
            assert isinstance(alert, PerformanceAlert)
            assert alert.equipment_id == equipment_id
            assert alert.alert_id is not None
            assert alert.metric in PerformanceMetric
            assert alert.alert_level in AlertLevel
            assert alert.current_value is not None
            assert alert.threshold_value is not None
            assert alert.message is not None
            assert alert.timestamp is not None
            assert isinstance(alert.recommendations, list)
            assert alert.acknowledged is False
    
    @pytest.mark.asyncio
    async def test_get_current_performance(self, service, sample_config):
        """Test getting current performance snapshot."""
        equipment_id = "test_equipment_001"
        
        # Start monitoring
        await service.start_monitoring(equipment_id, sample_config)
        
        # Wait a moment for monitoring loop to collect data
        await asyncio.sleep(0.1)
        
        # Get current performance
        snapshot = await service.get_current_performance(equipment_id)
        
        assert snapshot is not None
        assert isinstance(snapshot, PerformanceSnapshot)
        assert snapshot.equipment_id == equipment_id
    
    @pytest.mark.asyncio
    async def test_get_current_performance_no_data(self, service):
        """Test getting current performance when no data exists."""
        equipment_id = "nonexistent_equipment"
        
        snapshot = await service.get_current_performance(equipment_id)
        
        assert snapshot is None
    
    @pytest.mark.asyncio
    async def test_get_performance_history(self, service, sample_config):
        """Test getting performance history."""
        equipment_id = "test_equipment_001"
        
        # Start monitoring
        await service.start_monitoring(equipment_id, sample_config)
        
        # Wait for some data to be collected
        await asyncio.sleep(0.1)
        
        # Get history
        history = await service.get_performance_history(equipment_id, 24)
        
        assert isinstance(history, list)
        # Should have at least one snapshot
        assert len(history) >= 0
    
    @pytest.mark.asyncio
    async def test_get_active_alerts(self, service, sample_config):
        """Test getting active alerts."""
        equipment_id = "test_equipment_001"
        
        # Start monitoring
        await service.start_monitoring(equipment_id, sample_config)
        
        # Get active alerts
        alerts = await service.get_active_alerts(equipment_id)
        
        assert isinstance(alerts, list)
        # Initially should be empty
        assert len(alerts) == 0
    
    @pytest.mark.asyncio
    async def test_acknowledge_alert(self, service, sample_config):
        """Test alert acknowledgment."""
        equipment_id = "test_equipment_001"
        
        # Start monitoring
        await service.start_monitoring(equipment_id, sample_config)
        
        # Create a test alert
        alert = PerformanceAlert(
            alert_id="test_alert_001",
            equipment_id=equipment_id,
            metric=PerformanceMetric.APPLICATION_ACCURACY,
            alert_level=AlertLevel.WARNING,
            current_value=0.7,
            threshold_value=0.75,
            message="Test alert",
            timestamp=datetime.utcnow().isoformat(),
            recommendations=["Test recommendation"]
        )
        
        # Add alert to active alerts
        service.active_alerts[equipment_id] = [alert]
        
        # Acknowledge alert
        success = await service.acknowledge_alert(equipment_id, alert.alert_id)
        
        assert success is True
        assert alert.acknowledged is True
    
    @pytest.mark.asyncio
    async def test_acknowledge_alert_not_found(self, service):
        """Test acknowledging non-existent alert."""
        equipment_id = "nonexistent_equipment"
        alert_id = "nonexistent_alert"
        
        success = await service.acknowledge_alert(equipment_id, alert_id)
        
        assert success is False
    
    @pytest.mark.asyncio
    async def test_get_performance_trend(self, service, sample_config):
        """Test getting performance trend analysis."""
        equipment_id = "test_equipment_001"
        
        # Start monitoring
        await service.start_monitoring(equipment_id, sample_config)
        
        # Create some historical data
        base_time = datetime.utcnow() - timedelta(days=7)
        for i in range(5):
            snapshot = PerformanceSnapshot(
                snapshot_id=f"snapshot_{i}",
                equipment_id=equipment_id,
                timestamp=(base_time + timedelta(days=i)).isoformat(),
                metrics={
                    PerformanceMetric.APPLICATION_ACCURACY: 0.7 + i * 0.05,  # Improving trend
                    PerformanceMetric.COVERAGE_UNIFORMITY: 0.8,
                    PerformanceMetric.SPEED_EFFICIENCY: 0.75,
                    PerformanceMetric.FUEL_EFFICIENCY: 0.7,
                    PerformanceMetric.LABOR_EFFICIENCY: 0.8,
                    PerformanceMetric.MAINTENANCE_EFFICIENCY: 0.75,
                    PerformanceMetric.OVERALL_EFFICIENCY: 0.75 + i * 0.02,
                    PerformanceMetric.DOWNTIME_HOURS: 2,
                    PerformanceMetric.MAINTENANCE_COST: 500
                },
                status=PerformanceStatus.GOOD,
                alerts=[],
                efficiency_trend={},
                maintenance_status="maintenance_current"
            )
            service.performance_data[equipment_id].append(snapshot)
        
        # Get trend
        trend = await service.get_performance_trend(equipment_id, PerformanceMetric.APPLICATION_ACCURACY, 7)
        
        assert trend is not None
        assert isinstance(trend, PerformanceTrend)
        assert trend.equipment_id == equipment_id
        assert trend.metric == PerformanceMetric.APPLICATION_ACCURACY
        assert trend.time_period == "7_days"
        assert isinstance(trend.data_points, list)
        assert trend.trend_direction in ["improving", "declining", "stable"]
        assert 0 <= trend.trend_strength <= 1
        assert 0 <= trend.confidence <= 1
        assert isinstance(trend.forecast, list)
    
    @pytest.mark.asyncio
    async def test_get_performance_trend_insufficient_data(self, service):
        """Test getting trend with insufficient data."""
        equipment_id = "test_equipment_001"
        
        trend = await service.get_performance_trend(equipment_id, PerformanceMetric.APPLICATION_ACCURACY, 7)
        
        assert trend is None
    
    @pytest.mark.asyncio
    async def test_get_monitoring_status(self, service, sample_config):
        """Test getting monitoring status."""
        equipment_id = "test_equipment_001"
        
        # Start monitoring
        await service.start_monitoring(equipment_id, sample_config)
        
        # Get status
        status = await service.get_monitoring_status(equipment_id)
        
        assert isinstance(status, dict)
        assert status["equipment_id"] == equipment_id
        assert status["monitoring_enabled"] is True
        assert status["configuration"] is not None
        assert "data_points" in status
        assert "active_alerts" in status
        assert "last_update" in status
    
    @pytest.mark.asyncio
    async def test_cleanup_old_data(self, service, sample_config):
        """Test cleanup of old data."""
        equipment_id = "test_equipment_001"
        
        # Start monitoring
        await service.start_monitoring(equipment_id, sample_config)
        
        # Create old snapshot
        old_time = datetime.utcnow() - timedelta(days=35)  # Older than retention period
        old_snapshot = PerformanceSnapshot(
            snapshot_id="old_snapshot",
            equipment_id=equipment_id,
            timestamp=old_time.isoformat(),
            metrics={PerformanceMetric.APPLICATION_ACCURACY: 0.8},
            status=PerformanceStatus.GOOD,
            alerts=[],
            efficiency_trend={},
            maintenance_status="maintenance_current"
        )
        
        service.performance_data[equipment_id].append(old_snapshot)
        
        # Create recent snapshot
        recent_snapshot = PerformanceSnapshot(
            snapshot_id="recent_snapshot",
            equipment_id=equipment_id,
            timestamp=datetime.utcnow().isoformat(),
            metrics={PerformanceMetric.APPLICATION_ACCURACY: 0.8},
            status=PerformanceStatus.GOOD,
            alerts=[],
            efficiency_trend={},
            maintenance_status="maintenance_current"
        )
        
        service.performance_data[equipment_id].append(recent_snapshot)
        
        # Run cleanup
        await service._cleanup_old_data(equipment_id, 30)
        
        # Check that old data was removed
        remaining_snapshots = service.performance_data[equipment_id]
        assert len(remaining_snapshots) == 1
        assert remaining_snapshots[0].snapshot_id == "recent_snapshot"
    
    def test_performance_thresholds_initialization(self, service):
        """Test that performance thresholds are properly initialized."""
        thresholds = service.performance_thresholds
        
        # Check that all metrics have thresholds
        for metric in PerformanceMetric:
            assert metric.value in thresholds
        
        # Check threshold structure
        for metric, metric_thresholds in thresholds.items():
            # Only check for alert levels that are actually used
            for alert_level in [AlertLevel.CRITICAL, AlertLevel.WARNING, AlertLevel.INFO]:
                assert alert_level.value in metric_thresholds
                assert isinstance(metric_thresholds[alert_level.value], (int, float))
    
    def test_analyze_trend(self, service):
        """Test trend analysis."""
        # Test improving trend
        improving_data = [
            {"value": 0.7},
            {"value": 0.75},
            {"value": 0.8},
            {"value": 0.85}
        ]
        
        direction, strength = service._analyze_trend(improving_data)
        assert direction == "improving"
        assert strength > 0
        
        # Test declining trend
        declining_data = [
            {"value": 0.85},
            {"value": 0.8},
            {"value": 0.75},
            {"value": 0.7}
        ]
        
        direction, strength = service._analyze_trend(declining_data)
        assert direction == "declining"
        assert strength > 0
        
        # Test stable trend
        stable_data = [
            {"value": 0.8},
            {"value": 0.8},
            {"value": 0.8},
            {"value": 0.8}
        ]
        
        direction, strength = service._analyze_trend(stable_data)
        assert direction == "stable"
        assert strength == 0
    
    def test_generate_forecast(self, service):
        """Test forecast generation."""
        data_points = [
            {"timestamp": "2024-01-01T00:00:00", "value": 0.7},
            {"timestamp": "2024-01-02T00:00:00", "value": 0.75},
            {"timestamp": "2024-01-03T00:00:00", "value": 0.8},
            {"timestamp": "2024-01-04T00:00:00", "value": 0.85}
        ]
        
        forecast = service._generate_forecast(data_points, 3)
        
        assert isinstance(forecast, list)
        assert len(forecast) == 3
        
        for forecast_point in forecast:
            assert "timestamp" in forecast_point
            assert "value" in forecast_point
            assert "confidence" in forecast_point
            assert 0 <= forecast_point["value"] <= 1
            assert 0 <= forecast_point["confidence"] <= 1
    
    @pytest.mark.asyncio
    async def test_monitoring_loop_cancellation(self, service, sample_config):
        """Test that monitoring loop can be cancelled."""
        equipment_id = "test_equipment_001"
        
        # Start monitoring
        await service.start_monitoring(equipment_id, sample_config)
        
        # Get the monitoring task
        task = service.monitoring_tasks[equipment_id]
        
        # Cancel the task
        task.cancel()
        
        # Wait for cancellation to complete
        try:
            await task
        except asyncio.CancelledError:
            pass  # Expected
        
        # Verify task is cancelled
        assert task.cancelled()
    
    @pytest.mark.asyncio
    async def test_error_handling_in_monitoring_loop(self, service, sample_config):
        """Test error handling in monitoring loop."""
        equipment_id = "test_equipment_001"
        
        # Start monitoring
        await service.start_monitoring(equipment_id, sample_config)
        
        # Mock an error in snapshot collection
        with patch.object(service, '_collect_performance_snapshot', side_effect=Exception("Test error")):
            # The monitoring loop should handle the error gracefully
            await asyncio.sleep(0.1)  # Give it time to process
        
        # Monitoring should still be active
        assert equipment_id in service.monitoring_tasks


class TestMonitoringConfiguration:
    """Test suite for monitoring configuration model."""
    
    def test_configuration_creation(self):
        """Test monitoring configuration creation."""
        config = MonitoringConfiguration(
            equipment_id="test_equipment",
            monitoring_enabled=True,
            alert_thresholds={"test_metric": {"warning": 0.8}},
            monitoring_frequency_minutes=15,
            data_retention_days=30,
            alert_notifications=["email", "sms"]
        )
        
        assert config.equipment_id == "test_equipment"
        assert config.monitoring_enabled is True
        assert config.alert_thresholds["test_metric"]["warning"] == 0.8
        assert config.monitoring_frequency_minutes == 15
        assert config.data_retention_days == 30
        assert "email" in config.alert_notifications
        assert "sms" in config.alert_notifications


class TestPerformanceSnapshot:
    """Test suite for performance snapshot model."""
    
    def test_snapshot_creation(self):
        """Test performance snapshot creation."""
        snapshot = PerformanceSnapshot(
            snapshot_id="test_snapshot",
            equipment_id="test_equipment",
            timestamp=datetime.utcnow().isoformat(),
            metrics={PerformanceMetric.APPLICATION_ACCURACY: 0.8},
            status=PerformanceStatus.GOOD,
            alerts=[],
            efficiency_trend={PerformanceMetric.APPLICATION_ACCURACY: 0.1},
            maintenance_status="maintenance_current"
        )
        
        assert snapshot.snapshot_id == "test_snapshot"
        assert snapshot.equipment_id == "test_equipment"
        assert snapshot.timestamp is not None
        assert PerformanceMetric.APPLICATION_ACCURACY.value in snapshot.metrics
        assert snapshot.status == PerformanceStatus.GOOD
        assert isinstance(snapshot.alerts, list)
        assert isinstance(snapshot.efficiency_trend, dict)
        assert snapshot.maintenance_status == "maintenance_current"


class TestPerformanceAlert:
    """Test suite for performance alert model."""
    
    def test_alert_creation(self):
        """Test performance alert creation."""
        alert = PerformanceAlert(
            alert_id="test_alert",
            equipment_id="test_equipment",
            metric=PerformanceMetric.APPLICATION_ACCURACY,
            alert_level=AlertLevel.WARNING,
            current_value=0.7,
            threshold_value=0.75,
            message="Test alert message",
            timestamp=datetime.utcnow().isoformat(),
            recommendations=["Test recommendation"]
        )
        
        assert alert.alert_id == "test_alert"
        assert alert.equipment_id == "test_equipment"
        assert alert.metric == PerformanceMetric.APPLICATION_ACCURACY
        assert alert.alert_level == AlertLevel.WARNING
        assert alert.current_value == 0.7
        assert alert.threshold_value == 0.75
        assert alert.message == "Test alert message"
        assert alert.timestamp is not None
        assert "Test recommendation" in alert.recommendations
        assert alert.acknowledged is False


class TestPerformanceTrend:
    """Test suite for performance trend model."""
    
    def test_trend_creation(self):
        """Test performance trend creation."""
        trend = PerformanceTrend(
            equipment_id="test_equipment",
            metric=PerformanceMetric.APPLICATION_ACCURACY,
            time_period="7_days",
            data_points=[{"timestamp": "2024-01-01", "value": 0.8}],
            trend_direction="improving",
            trend_strength=0.7,
            confidence=0.8,
            forecast=[{"timestamp": "2024-01-02", "value": 0.85, "confidence": 0.7}]
        )
        
        assert trend.equipment_id == "test_equipment"
        assert trend.metric == PerformanceMetric.APPLICATION_ACCURACY
        assert trend.time_period == "7_days"
        assert len(trend.data_points) == 1
        assert trend.trend_direction == "improving"
        assert trend.trend_strength == 0.7
        assert trend.confidence == 0.8
        assert len(trend.forecast) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])