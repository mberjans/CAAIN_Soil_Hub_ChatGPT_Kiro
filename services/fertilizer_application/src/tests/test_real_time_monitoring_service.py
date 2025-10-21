"""
Tests for real-time application monitoring and adjustment service.

This module contains comprehensive tests for the real-time monitoring service,
including unit tests, integration tests, and performance tests.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from typing import List, Dict, Any

from src.services.real_time_monitoring_service import (
    RealTimeMonitoringService, MonitoringState, AdjustmentRule
)
from src.models.application_monitoring_models import (
    ApplicationSession, MonitoringConfiguration, ApplicationMonitoringData,
    RealTimeAdjustment, MonitoringAlert, SensorData, QualityControlCheck,
    MonitoringSummary, ApplicationStatus, AdjustmentType, MonitoringMetric,
    AlertSeverity, SensorType
)


class TestRealTimeMonitoringService:
    """Test suite for RealTimeMonitoringService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return RealTimeMonitoringService()
    
    @pytest.fixture
    def sample_session(self):
        """Create sample application session."""
        return ApplicationSession(
            field_id="field_123",
            equipment_id="equipment_456",
            operator_id="operator_789",
            fertilizer_type="Urea",
            target_rate=150.0,
            application_method="broadcast",
            planned_start=datetime.now(),
            planned_end=datetime.now() + timedelta(hours=4),
            total_area=40.0
        )
    
    @pytest.fixture
    def sample_config(self):
        """Create sample monitoring configuration."""
        return MonitoringConfiguration(
            session_id="session_123",
            monitoring_enabled=True,
            update_frequency_seconds=5,
            alert_thresholds={
                "rate_deviation": {"high": 10.0, "critical": 20.0},
                "coverage_uniformity": {"medium": 0.8, "high": 0.75},
                "wind_speed": {"medium": 10.0, "high": 15.0}
            },
            adjustment_thresholds={
                "rate_deviation": 5.0,
                "coverage_uniformity": 0.85,
                "wind_speed": 10.0
            },
            enabled_sensors=[SensorType.FLOW_METER, SensorType.PRESSURE_SENSOR, SensorType.WEATHER_STATION],
            quality_checks_enabled=True,
            quality_check_frequency=300,
            notification_methods=["log", "email"]
        )
    
    @pytest.fixture
    def sample_monitoring_data(self, sample_session):
        """Create sample monitoring data."""
        return ApplicationMonitoringData(
            application_session_id=sample_session.session_id,
            equipment_id=sample_session.equipment_id,
            field_id=sample_session.field_id,
            application_rate=155.0,
            target_rate=150.0,
            rate_deviation=3.33,
            coverage_uniformity=0.92,
            coverage_area=0.5,
            overlap_percentage=10.0,
            speed=6.5,
            pressure=32.5,
            nozzle_status={"nozzle_1": True, "nozzle_2": True, "nozzle_3": True},
            temperature=72.0,
            humidity=65.0,
            wind_speed=8.5,
            wind_direction=180.0,
            soil_moisture=45.0,
            latitude=40.123456,
            longitude=-95.654321,
            elevation=950.0,
            quality_score=0.95,
            drift_potential=0.3,
            application_efficiency=0.92,
            equipment_status="operational",
            maintenance_alerts=[]
        )
    
    @pytest.mark.asyncio
    async def test_start_monitoring_success(self, service, sample_session, sample_config):
        """Test successful monitoring start."""
        success = await service.start_monitoring(sample_session, sample_config)
        
        assert success is True
        assert sample_session.session_id in service.monitoring_sessions
        assert sample_session.session_id in service.monitoring_configs
        assert sample_session.session_id in service.active_monitoring
        assert service.active_monitoring[sample_session.session_id] is True
        assert service.state == MonitoringState.MONITORING
    
    @pytest.mark.asyncio
    async def test_start_monitoring_disabled(self, service, sample_session, sample_config):
        """Test monitoring start with monitoring disabled."""
        sample_config.monitoring_enabled = False
        
        success = await service.start_monitoring(sample_session, sample_config)
        
        assert success is True
        assert sample_session.session_id in service.monitoring_sessions
        assert sample_session.session_id in service.monitoring_configs
        assert service.active_monitoring.get(sample_session.session_id, False) is False
    
    @pytest.mark.asyncio
    async def test_stop_monitoring_success(self, service, sample_session, sample_config):
        """Test successful monitoring stop."""
        # Start monitoring first
        await service.start_monitoring(sample_session, sample_config)
        
        # Stop monitoring
        success = await service.stop_monitoring(sample_session.session_id)
        
        assert success is True
        assert service.active_monitoring.get(sample_session.session_id, False) is False
        assert sample_session.session_id not in service.monitoring_tasks
    
    @pytest.mark.asyncio
    async def test_stop_monitoring_nonexistent_session(self, service):
        """Test stopping monitoring for non-existent session."""
        success = await service.stop_monitoring("nonexistent_session")
        
        assert success is True  # Should not raise exception
    
    @pytest.mark.asyncio
    async def test_collect_monitoring_data(self, service, sample_session, sample_config):
        """Test monitoring data collection."""
        await service.start_monitoring(sample_session, sample_config)
        
        # Mock the monitoring data collection
        with patch.object(service, '_simulate_monitoring_data') as mock_simulate:
            mock_simulate.return_value = ApplicationMonitoringData(
                application_session_id=sample_session.session_id,
                equipment_id=sample_session.equipment_id,
                field_id=sample_session.field_id,
                application_rate=150.0,
                target_rate=150.0,
                rate_deviation=0.0,
                coverage_uniformity=0.9,
                coverage_area=0.5,
                overlap_percentage=10.0,
                speed=6.0,
                pressure=30.0,
                temperature=70.0,
                humidity=60.0,
                wind_speed=5.0,
                wind_direction=180.0,
                soil_moisture=40.0,
                latitude=40.0,
                longitude=-95.0,
                elevation=900.0,
                quality_score=0.9,
                drift_potential=0.2,
                application_efficiency=0.9,
                equipment_status="operational",
                maintenance_alerts=[]
            )
            
            data = await service._collect_monitoring_data(sample_session.session_id)
            
            assert data is not None
            assert data.application_session_id == sample_session.session_id
            assert data.equipment_id == sample_session.equipment_id
    
    @pytest.mark.asyncio
    async def test_check_adjustment_needs(self, service, sample_session, sample_config, sample_monitoring_data):
        """Test adjustment needs checking."""
        await service.start_monitoring(sample_session, sample_config)
        
        # Test with data that should trigger adjustments
        sample_monitoring_data.rate_deviation = 8.0  # 8% deviation
        sample_monitoring_data.coverage_uniformity = 0.75  # Below threshold
        
        adjustments = await service._check_adjustment_needs(sample_session.session_id, sample_monitoring_data)
        
        assert len(adjustments) > 0
        assert any(adj.adjustment_type == AdjustmentType.RATE_ADJUSTMENT for adj in adjustments)
        assert any(adj.adjustment_type == AdjustmentType.COVERAGE_ADJUSTMENT for adj in adjustments)
    
    @pytest.mark.asyncio
    async def test_check_alerts(self, service, sample_session, sample_config, sample_monitoring_data):
        """Test alert checking."""
        await service.start_monitoring(sample_session, sample_config)
        
        # Test with data that should trigger alerts
        sample_monitoring_data.rate_deviation = 15.0  # High deviation
        sample_monitoring_data.wind_speed = 12.0  # High wind speed
        
        alerts = await service._check_alerts(sample_session.session_id, sample_monitoring_data)
        
        assert len(alerts) > 0
        assert any(alert.alert_type == "rate_deviation" for alert in alerts)
        assert any(alert.alert_type == "high_wind" for alert in alerts)
    
    @pytest.mark.asyncio
    async def test_perform_quality_check(self, service, sample_session, sample_config):
        """Test quality control check."""
        await service.start_monitoring(sample_session, sample_config)
        
        # Add some monitoring data
        for i in range(10):
            data = ApplicationMonitoringData(
                application_session_id=sample_session.session_id,
                equipment_id=sample_session.equipment_id,
                field_id=sample_session.field_id,
                application_rate=150.0 + i,
                target_rate=150.0,
                rate_deviation=i * 2,
                coverage_uniformity=0.9 - (i * 0.01),
                coverage_area=0.5,
                overlap_percentage=10.0,
                speed=6.0,
                pressure=30.0,
                temperature=70.0,
                humidity=60.0,
                wind_speed=5.0,
                wind_direction=180.0,
                soil_moisture=40.0,
                latitude=40.0,
                longitude=-95.0,
                elevation=900.0,
                quality_score=0.9,
                drift_potential=0.2,
                application_efficiency=0.9,
                equipment_status="operational",
                maintenance_alerts=[]
            )
            service.monitoring_data[sample_session.session_id].append(data)
        
        quality_check = await service._perform_quality_check(sample_session.session_id)
        
        assert quality_check is not None
        assert quality_check.session_id == sample_session.session_id
        assert quality_check.check_type == "comprehensive_quality_check"
        assert 0 <= quality_check.score <= 1
    
    @pytest.mark.asyncio
    async def test_get_current_monitoring_data(self, service, sample_session, sample_config, sample_monitoring_data):
        """Test getting current monitoring data."""
        await service.start_monitoring(sample_session, sample_config)
        
        # Add monitoring data
        service.monitoring_data[sample_session.session_id] = [sample_monitoring_data]
        
        current_data = await service.get_current_monitoring_data(sample_session.session_id)
        
        assert current_data is not None
        assert current_data.monitoring_id == sample_monitoring_data.monitoring_id
    
    @pytest.mark.asyncio
    async def test_get_monitoring_history(self, service, sample_session, sample_config):
        """Test getting monitoring history."""
        await service.start_monitoring(sample_session, sample_config)
        
        # Add historical data
        now = datetime.now()
        for i in range(5):
            data = ApplicationMonitoringData(
                application_session_id=sample_session.session_id,
                equipment_id=sample_session.equipment_id,
                field_id=sample_session.field_id,
                application_rate=150.0,
                target_rate=150.0,
                rate_deviation=0.0,
                coverage_uniformity=0.9,
                coverage_area=0.5,
                overlap_percentage=10.0,
                speed=6.0,
                pressure=30.0,
                temperature=70.0,
                humidity=60.0,
                wind_speed=5.0,
                wind_direction=180.0,
                soil_moisture=40.0,
                latitude=40.0,
                longitude=-95.0,
                elevation=900.0,
                quality_score=0.9,
                drift_potential=0.2,
                application_efficiency=0.9,
                equipment_status="operational",
                maintenance_alerts=[]
            )
            data.timestamp = now - timedelta(minutes=i * 10)
            service.monitoring_data[sample_session.session_id].append(data)
        
        history = await service.get_monitoring_history(sample_session.session_id, 30)
        
        assert len(history) >= 3  # Should get last 3 data points (30 minutes)
    
    @pytest.mark.asyncio
    async def test_get_active_adjustments(self, service, sample_session, sample_config):
        """Test getting active adjustments."""
        await service.start_monitoring(sample_session, sample_config)
        
        # Add some adjustments
        adjustment = RealTimeAdjustment(
            monitoring_data_id="data_123",
            adjustment_type=AdjustmentType.RATE_ADJUSTMENT,
            priority=2,
            current_value=155.0,
            target_value=150.0,
            adjustment_amount=5.0,
            reason="Rate deviation detected",
            impact_assessment="Rate adjustment to improve accuracy",
            implementation_time=5,
            confidence=0.9,
            risk_level=AlertSeverity.MEDIUM
        )
        service.active_adjustments[sample_session.session_id] = [adjustment]
        
        adjustments = await service.get_active_adjustments(sample_session.session_id)
        
        assert len(adjustments) == 1
        assert adjustments[0].adjustment_id == adjustment.adjustment_id
    
    @pytest.mark.asyncio
    async def test_implement_adjustment(self, service, sample_session, sample_config):
        """Test implementing an adjustment."""
        await service.start_monitoring(sample_session, sample_config)
        
        # Add an adjustment
        adjustment = RealTimeAdjustment(
            monitoring_data_id="data_123",
            adjustment_type=AdjustmentType.RATE_ADJUSTMENT,
            priority=2,
            current_value=155.0,
            target_value=150.0,
            adjustment_amount=5.0,
            reason="Rate deviation detected",
            impact_assessment="Rate adjustment to improve accuracy",
            implementation_time=5,
            confidence=0.9,
            risk_level=AlertSeverity.MEDIUM
        )
        service.active_adjustments[sample_session.session_id] = [adjustment]
        
        success = await service.implement_adjustment(sample_session.session_id, adjustment.adjustment_id)
        
        assert success is True
        assert adjustment.implemented is True
        assert adjustment.implemented_at is not None
    
    @pytest.mark.asyncio
    async def test_acknowledge_alert(self, service, sample_session, sample_config):
        """Test acknowledging an alert."""
        await service.start_monitoring(sample_session, sample_config)
        
        # Add an alert
        alert = MonitoringAlert(
            monitoring_data_id="data_123",
            alert_type="rate_deviation",
            severity=AlertSeverity.HIGH,
            metric=MonitoringMetric.APPLICATION_RATE,
            current_value=165.0,
            threshold_value=150.0,
            deviation_percentage=10.0,
            title="High Rate Deviation",
            message="Application rate is 10% above target",
            recommendations=["Check equipment calibration"]
        )
        service.active_alerts[sample_session.session_id] = [alert]
        
        success = await service.acknowledge_alert(sample_session.session_id, alert.alert_id)
        
        assert success is True
        assert alert.acknowledged is True
        assert alert.acknowledged_at is not None
    
    @pytest.mark.asyncio
    async def test_resolve_alert(self, service, sample_session, sample_config):
        """Test resolving an alert."""
        await service.start_monitoring(sample_session, sample_config)
        
        # Add an alert
        alert = MonitoringAlert(
            monitoring_data_id="data_123",
            alert_type="rate_deviation",
            severity=AlertSeverity.HIGH,
            metric=MonitoringMetric.APPLICATION_RATE,
            current_value=165.0,
            threshold_value=150.0,
            deviation_percentage=10.0,
            title="High Rate Deviation",
            message="Application rate is 10% above target",
            recommendations=["Check equipment calibration"]
        )
        service.active_alerts[sample_session.session_id] = [alert]
        
        success = await service.resolve_alert(sample_session.session_id, alert.alert_id)
        
        assert success is True
        assert alert.resolved is True
        assert alert.resolved_at is not None
    
    @pytest.mark.asyncio
    async def test_get_monitoring_summary(self, service, sample_session, sample_config):
        """Test getting monitoring summary."""
        await service.start_monitoring(sample_session, sample_config)
        
        # Add some monitoring data
        for i in range(10):
            data = ApplicationMonitoringData(
                application_session_id=sample_session.session_id,
                equipment_id=sample_session.equipment_id,
                field_id=sample_session.field_id,
                application_rate=150.0 + i,
                target_rate=150.0,
                rate_deviation=i * 2,
                coverage_uniformity=0.9 - (i * 0.01),
                coverage_area=0.5,
                overlap_percentage=10.0,
                speed=6.0,
                pressure=30.0,
                temperature=70.0,
                humidity=60.0,
                wind_speed=5.0,
                wind_direction=180.0,
                soil_moisture=40.0,
                latitude=40.0,
                longitude=-95.0,
                elevation=900.0,
                quality_score=0.9,
                drift_potential=0.2,
                application_efficiency=0.9,
                equipment_status="operational",
                maintenance_alerts=[]
            )
            service.monitoring_data[sample_session.session_id].append(data)
        
        # Add some adjustments
        adjustment = RealTimeAdjustment(
            monitoring_data_id="data_123",
            adjustment_type=AdjustmentType.RATE_ADJUSTMENT,
            priority=2,
            current_value=155.0,
            target_value=150.0,
            adjustment_amount=5.0,
            reason="Rate deviation detected",
            impact_assessment="Rate adjustment to improve accuracy",
            implementation_time=5,
            confidence=0.9,
            risk_level=AlertSeverity.MEDIUM,
            implemented=True,
            implemented_at=datetime.now()
        )
        service.active_adjustments[sample_session.session_id] = [adjustment]
        
        # Add some alerts
        alert = MonitoringAlert(
            monitoring_data_id="data_123",
            alert_type="rate_deviation",
            severity=AlertSeverity.HIGH,
            metric=MonitoringMetric.APPLICATION_RATE,
            current_value=165.0,
            threshold_value=150.0,
            deviation_percentage=10.0,
            title="High Rate Deviation",
            message="Application rate is 10% above target",
            recommendations=["Check equipment calibration"],
            resolved=True,
            resolved_at=datetime.now()
        )
        service.active_alerts[sample_session.session_id] = [alert]
        
        summary = await service.get_monitoring_summary(sample_session.session_id)
        
        assert summary is not None
        assert summary.session_id == sample_session.session_id
        assert summary.total_data_points == 10
        assert summary.total_adjustments == 1
        assert summary.successful_adjustments == 1
        assert summary.total_alerts == 1
        assert summary.resolved_alerts == 1
    
    @pytest.mark.asyncio
    async def test_get_monitoring_status(self, service, sample_session, sample_config):
        """Test getting monitoring status."""
        await service.start_monitoring(sample_session, sample_config)
        
        status = await service.get_monitoring_status(sample_session.session_id)
        
        assert status["session_id"] == sample_session.session_id
        assert status["monitoring_enabled"] is True
        assert status["session_status"] == ApplicationStatus.PLANNED.value
        assert status["data_points"] == 0
        assert status["monitoring_state"] == MonitoringState.MONITORING.value
    
    @pytest.mark.asyncio
    async def test_adjustment_rules_initialization(self, service):
        """Test that adjustment rules are properly initialized."""
        assert len(service.adjustment_rules) > 0
        
        # Check that we have rules for key metrics
        rule_metrics = [rule.metric for rule in service.adjustment_rules]
        assert MonitoringMetric.APPLICATION_RATE in rule_metrics
        assert MonitoringMetric.COVERAGE_UNIFORMITY in rule_metrics
        assert MonitoringMetric.WIND_SPEED in rule_metrics
        assert MonitoringMetric.PRESSURE in rule_metrics
    
    @pytest.mark.asyncio
    async def test_evaluate_rule_conditions(self, service, sample_session, sample_config, sample_monitoring_data):
        """Test rule condition evaluation."""
        await service.start_monitoring(sample_session, sample_config)
        
        # Test rate deviation rule
        rate_rule = next(rule for rule in service.adjustment_rules if rule.metric == MonitoringMetric.APPLICATION_RATE)
        sample_monitoring_data.rate_deviation = 8.0  # Above threshold
        
        # Add some historical data to meet min_samples condition
        for i in range(5):
            data = ApplicationMonitoringData(
                application_session_id=sample_session.session_id,
                equipment_id=sample_session.equipment_id,
                field_id=sample_session.field_id,
                application_rate=150.0,
                target_rate=150.0,
                rate_deviation=0.0,
                coverage_uniformity=0.9,
                coverage_area=0.5,
                overlap_percentage=10.0,
                speed=6.0,
                pressure=30.0,
                temperature=70.0,
                humidity=60.0,
                wind_speed=5.0,
                wind_direction=180.0,
                soil_moisture=40.0,
                latitude=40.0,
                longitude=-95.0,
                elevation=900.0,
                quality_score=0.9,
                drift_potential=0.2,
                application_efficiency=0.9,
                equipment_status="operational",
                maintenance_alerts=[]
            )
            service.monitoring_data[sample_session.session_id].append(data)
        
        conditions_met = await service._evaluate_rule_conditions(rate_rule, sample_session.session_id, sample_monitoring_data)
        
        assert conditions_met is True
    
    @pytest.mark.asyncio
    async def test_create_adjustment(self, service, sample_monitoring_data):
        """Test adjustment creation."""
        rate_rule = next(rule for rule in service.adjustment_rules if rule.metric == MonitoringMetric.APPLICATION_RATE)
        
        adjustment = await service._create_adjustment(rate_rule, sample_monitoring_data)
        
        assert adjustment is not None
        assert adjustment.adjustment_type == AdjustmentType.RATE_ADJUSTMENT
        assert adjustment.priority == rate_rule.priority
        assert adjustment.confidence > 0
        assert adjustment.risk_level in [AlertSeverity.LOW, AlertSeverity.MEDIUM, AlertSeverity.HIGH]
    
    @pytest.mark.asyncio
    async def test_simulate_monitoring_data(self, service, sample_session):
        """Test monitoring data simulation."""
        data = await service._simulate_monitoring_data(sample_session)
        
        assert data is not None
        assert data.application_session_id == sample_session.session_id
        assert data.equipment_id == sample_session.equipment_id
        assert data.field_id == sample_session.field_id
        assert data.application_rate > 0
        assert data.target_rate == sample_session.target_rate
        assert 0 <= data.coverage_uniformity <= 1
        assert data.speed > 0
        assert data.pressure > 0
        assert data.temperature > 0
        assert 0 <= data.humidity <= 100
        assert data.wind_speed >= 0
        assert 0 <= data.wind_direction <= 360
        assert 0 <= data.soil_moisture <= 100
        assert -90 <= data.latitude <= 90
        assert -180 <= data.longitude <= 180
        assert data.elevation > 0
        assert 0 <= data.quality_score <= 1
        assert 0 <= data.drift_potential <= 1
        assert 0 <= data.application_efficiency <= 1
    
    @pytest.mark.asyncio
    async def test_simulate_sensor_reading(self, service, sample_session):
        """Test sensor reading simulation."""
        sensor_data = await service._simulate_sensor_reading(SensorType.FLOW_METER, sample_session.session_id)
        
        assert sensor_data is not None
        assert sensor_data.sensor_type == SensorType.FLOW_METER
        assert sensor_data.equipment_id == sample_session.equipment_id
        assert "flow_rate" in sensor_data.readings
        assert "total_volume" in sensor_data.readings
        assert 0 <= sensor_data.data_quality <= 1
        assert sensor_data.status == "active"
    
    @pytest.mark.asyncio
    async def test_update_session_progress(self, service, sample_session, sample_config, sample_monitoring_data):
        """Test session progress update."""
        await service.start_monitoring(sample_session, sample_config)
        
        # Add some adjustments and alerts
        adjustment = RealTimeAdjustment(
            monitoring_data_id="data_123",
            adjustment_type=AdjustmentType.RATE_ADJUSTMENT,
            priority=2,
            current_value=155.0,
            target_value=150.0,
            adjustment_amount=5.0,
            reason="Rate deviation detected",
            impact_assessment="Rate adjustment to improve accuracy",
            implementation_time=5,
            confidence=0.9,
            risk_level=AlertSeverity.MEDIUM
        )
        service.active_adjustments[sample_session.session_id] = [adjustment]
        
        alert = MonitoringAlert(
            monitoring_data_id="data_123",
            alert_type="rate_deviation",
            severity=AlertSeverity.HIGH,
            metric=MonitoringMetric.APPLICATION_RATE,
            current_value=165.0,
            threshold_value=150.0,
            deviation_percentage=10.0,
            title="High Rate Deviation",
            message="Application rate is 10% above target",
            recommendations=["Check equipment calibration"]
        )
        service.active_alerts[sample_session.session_id] = [alert]
        
        await service._update_session_progress(sample_session.session_id, sample_monitoring_data)
        
        assert sample_session.completed_area > 0
        assert sample_session.progress_percentage > 0
        assert sample_session.total_adjustments == 1
        assert sample_session.active_alerts == 1


class TestRealTimeMonitoringIntegration:
    """Integration tests for real-time monitoring service."""
    
    @pytest.mark.asyncio
    async def test_full_monitoring_workflow(self):
        """Test complete monitoring workflow from start to finish."""
        service = RealTimeMonitoringService()
        
        # Create session and config
        session = ApplicationSession(
            field_id="field_123",
            equipment_id="equipment_456",
            operator_id="operator_789",
            fertilizer_type="Urea",
            target_rate=150.0,
            application_method="broadcast",
            planned_start=datetime.now(),
            planned_end=datetime.now() + timedelta(hours=4),
            total_area=40.0
        )
        
        config = MonitoringConfiguration(
            session_id=session.session_id,
            monitoring_enabled=True,
            update_frequency_seconds=1,  # Fast for testing
            quality_checks_enabled=True,
            quality_check_frequency=5  # Fast for testing
        )
        
        # Start monitoring
        success = await service.start_monitoring(session, config)
        assert success is True
        
        # Wait a bit for monitoring to collect data
        await asyncio.sleep(2)
        
        # Check that data is being collected
        current_data = await service.get_current_monitoring_data(session.session_id)
        assert current_data is not None
        
        # Check status
        status = await service.get_monitoring_status(session.session_id)
        assert status["monitoring_enabled"] is True
        assert status["data_points"] > 0
        
        # Stop monitoring
        success = await service.stop_monitoring(session.session_id)
        assert success is True
        
        # Verify monitoring stopped
        status = await service.get_monitoring_status(session.session_id)
        assert status["monitoring_enabled"] is False
    
    @pytest.mark.asyncio
    async def test_concurrent_sessions(self):
        """Test handling multiple concurrent monitoring sessions."""
        service = RealTimeMonitoringService()
        
        sessions = []
        configs = []
        
        # Create multiple sessions
        for i in range(3):
            session = ApplicationSession(
                field_id=f"field_{i}",
                equipment_id=f"equipment_{i}",
                operator_id=f"operator_{i}",
                fertilizer_type="Urea",
                target_rate=150.0 + i * 10,
                application_method="broadcast",
                planned_start=datetime.now(),
                planned_end=datetime.now() + timedelta(hours=4),
                total_area=40.0 + i * 10
            )
            
            config = MonitoringConfiguration(
                session_id=session.session_id,
                monitoring_enabled=True,
                update_frequency_seconds=1,
                quality_checks_enabled=True,
                quality_check_frequency=5
            )
            
            sessions.append(session)
            configs.append(config)
        
        # Start all sessions
        for session, config in zip(sessions, configs):
            success = await service.start_monitoring(session, config)
            assert success is True
        
        # Wait for data collection
        await asyncio.sleep(2)
        
        # Check all sessions are monitoring
        for session in sessions:
            status = await service.get_monitoring_status(session.session_id)
            assert status["monitoring_enabled"] is True
            assert status["data_points"] > 0
        
        # Stop all sessions
        for session in sessions:
            success = await service.stop_monitoring(session.session_id)
            assert success is True
        
        # Verify all stopped
        for session in sessions:
            status = await service.get_monitoring_status(session.session_id)
            assert status["monitoring_enabled"] is False


class TestRealTimeMonitoringPerformance:
    """Performance tests for real-time monitoring service."""
    
    @pytest.mark.asyncio
    async def test_monitoring_data_collection_performance(self):
        """Test performance of monitoring data collection."""
        service = RealTimeMonitoringService()
        
        session = ApplicationSession(
            field_id="field_123",
            equipment_id="equipment_456",
            operator_id="operator_789",
            fertilizer_type="Urea",
            target_rate=150.0,
            application_method="broadcast",
            planned_start=datetime.now(),
            planned_end=datetime.now() + timedelta(hours=4),
            total_area=40.0
        )
        
        config = MonitoringConfiguration(
            session_id=session.session_id,
            monitoring_enabled=True,
            update_frequency_seconds=1
        )
        
        await service.start_monitoring(session, config)
        
        # Measure data collection time
        start_time = datetime.now()
        
        # Collect multiple data points
        for _ in range(10):
            data = await service._collect_monitoring_data(session.session_id)
            assert data is not None
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Should be able to collect 10 data points in under 1 second
        assert duration < 1.0
        
        await service.stop_monitoring(session.session_id)
    
    @pytest.mark.asyncio
    async def test_adjustment_processing_performance(self):
        """Test performance of adjustment processing."""
        service = RealTimeMonitoringService()
        
        session = ApplicationSession(
            field_id="field_123",
            equipment_id="equipment_456",
            operator_id="operator_789",
            fertilizer_type="Urea",
            target_rate=150.0,
            application_method="broadcast",
            planned_start=datetime.now(),
            planned_end=datetime.now() + timedelta(hours=4),
            total_area=40.0
        )
        
        config = MonitoringConfiguration(
            session_id=session.session_id,
            monitoring_enabled=True,
            update_frequency_seconds=1
        )
        
        await service.start_monitoring(session, config)
        
        # Create monitoring data that should trigger adjustments
        monitoring_data = ApplicationMonitoringData(
            application_session_id=session.session_id,
            equipment_id=session.equipment_id,
            field_id=session.field_id,
            application_rate=165.0,  # High deviation
            target_rate=150.0,
            rate_deviation=10.0,
            coverage_uniformity=0.75,  # Below threshold
            coverage_area=0.5,
            overlap_percentage=10.0,
            speed=6.0,
            pressure=30.0,
            temperature=70.0,
            humidity=60.0,
            wind_speed=12.0,  # High wind
            wind_direction=180.0,
            soil_moisture=40.0,
            latitude=40.0,
            longitude=-95.0,
            elevation=900.0,
            quality_score=0.9,
            drift_potential=0.2,
            application_efficiency=0.9,
            equipment_status="operational",
            maintenance_alerts=[]
        )
        
        # Measure adjustment processing time
        start_time = datetime.now()
        
        adjustments = await service._check_adjustment_needs(session.session_id, monitoring_data)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Should process adjustments in under 0.1 seconds
        assert duration < 0.1
        assert len(adjustments) > 0
        
        await service.stop_monitoring(session.session_id)