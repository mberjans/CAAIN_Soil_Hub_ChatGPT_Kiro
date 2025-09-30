"""
Integration tests for real-time monitoring system.

This module contains comprehensive integration tests that verify the
real-time monitoring system works correctly with existing services
and IoT sensor integration.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from typing import List, Dict, Any

from src.services.real_time_monitoring_service import RealTimeMonitoringService
from src.services.iot_sensor_service import IoTSensorService, SensorConfiguration
from src.models.application_monitoring_models import (
    ApplicationSession, MonitoringConfiguration, ApplicationMonitoringData,
    SensorType, ApplicationStatus, AdjustmentType, MonitoringMetric,
    AlertSeverity
)


class TestRealTimeMonitoringIntegration:
    """Integration tests for real-time monitoring system."""
    
    @pytest.fixture
    def monitoring_service(self):
        """Create monitoring service instance."""
        return RealTimeMonitoringService()
    
    @pytest.fixture
    def iot_service(self):
        """Create IoT service instance."""
        return IoTSensorService()
    
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
    def sample_monitoring_config(self):
        """Create sample monitoring configuration."""
        return MonitoringConfiguration(
            session_id="session_123",
            monitoring_enabled=True,
            update_frequency_seconds=1,  # Fast for testing
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
            quality_check_frequency=5,  # Fast for testing
            notification_methods=["log", "email"]
        )
    
    @pytest.fixture
    def sample_sensor_configs(self):
        """Create sample sensor configurations."""
        return [
            SensorConfiguration(
                sensor_id="flow_meter_001",
                sensor_type=SensorType.FLOW_METER,
                equipment_id="equipment_456",
                location={"latitude": 40.123456, "longitude": -95.654321, "elevation": 950.0},
                calibration_data={"flow_factor": 1.0, "pressure_offset": 0.0},
                update_frequency_seconds=1,
                data_retention_hours=1,
                alert_thresholds={"flow_rate": 50.0, "pressure": 45.0},
                connection_params={"protocol": "mqtt"}
            ),
            SensorConfiguration(
                sensor_id="weather_station_001",
                sensor_type=SensorType.WEATHER_STATION,
                equipment_id="equipment_456",
                location={"latitude": 40.123456, "longitude": -95.654321, "elevation": 950.0},
                calibration_data={"temperature_offset": 0.0, "humidity_calibration": 1.0},
                update_frequency_seconds=1,
                data_retention_hours=1,
                alert_thresholds={"wind_speed": 15.0, "temperature": 100.0},
                connection_params={"protocol": "mqtt"}
            ),
            SensorConfiguration(
                sensor_id="pressure_sensor_001",
                sensor_type=SensorType.PRESSURE_SENSOR,
                equipment_id="equipment_456",
                location={"latitude": 40.123456, "longitude": -95.654321, "elevation": 950.0},
                calibration_data={"pressure_offset": 0.0},
                update_frequency_seconds=1,
                data_retention_hours=1,
                alert_thresholds={"pressure": 45.0},
                connection_params={"protocol": "mqtt"}
            )
        ]
    
    @pytest.mark.asyncio
    async def test_full_monitoring_workflow_with_sensors(
        self, 
        monitoring_service, 
        iot_service, 
        sample_session, 
        sample_monitoring_config, 
        sample_sensor_configs
    ):
        """Test complete monitoring workflow with IoT sensor integration."""
        
        # Start IoT service
        await iot_service.start_service()
        
        # Register sensors
        for config in sample_sensor_configs:
            success = await iot_service.register_sensor(config)
            assert success is True
        
        # Start monitoring session
        success = await monitoring_service.start_monitoring(sample_session, sample_monitoring_config)
        assert success is True
        
        # Wait for data collection
        await asyncio.sleep(3)
        
        # Check that monitoring data is being collected
        current_data = await monitoring_service.get_current_monitoring_data(sample_session.session_id)
        assert current_data is not None
        assert current_data.application_session_id == sample_session.session_id
        
        # Check that sensor data is being collected
        for config in sample_sensor_configs:
            sensor_data = await iot_service.get_latest_sensor_data(config.sensor_id)
            assert sensor_data is not None
            assert sensor_data.sensor_type == config.sensor_type
        
        # Check monitoring status
        status = await monitoring_service.get_monitoring_status(sample_session.session_id)
        assert status["monitoring_enabled"] is True
        assert status["data_points"] > 0
        
        # Check IoT service status
        iot_status = await iot_service.get_sensor_status()
        assert iot_status["total_sensors"] == 3
        assert iot_status["online_sensors"] >= 0
        
        # Stop monitoring
        await monitoring_service.stop_monitoring(sample_session.session_id)
        
        # Unregister sensors
        for config in sample_sensor_configs:
            await iot_service.unregister_sensor(config.sensor_id)
        
        # Stop IoT service
        await iot_service.stop_service()
    
    @pytest.mark.asyncio
    async def test_real_time_adjustments_with_sensor_data(
        self, 
        monitoring_service, 
        iot_service, 
        sample_session, 
        sample_monitoring_config, 
        sample_sensor_configs
    ):
        """Test real-time adjustments based on sensor data."""
        
        # Start services
        await iot_service.start_service()
        await monitoring_service.start_monitoring(sample_session, sample_monitoring_config)
        
        # Register sensors
        for config in sample_sensor_configs:
            await iot_service.register_sensor(config)
        
        # Wait for initial data collection
        await asyncio.sleep(2)
        
        # Simulate sensor data that should trigger adjustments
        # This would normally come from actual sensors, but we'll simulate it
        with patch.object(monitoring_service, '_simulate_monitoring_data') as mock_simulate:
            # Create monitoring data that should trigger rate adjustment
            mock_data = ApplicationMonitoringData(
                application_session_id=sample_session.session_id,
                equipment_id=sample_session.equipment_id,
                field_id=sample_session.field_id,
                application_rate=165.0,  # 10% above target (should trigger adjustment)
                target_rate=150.0,
                rate_deviation=10.0,
                coverage_uniformity=0.75,  # Below threshold (should trigger adjustment)
                coverage_area=0.5,
                overlap_percentage=10.0,
                speed=6.0,
                pressure=30.0,
                temperature=70.0,
                humidity=60.0,
                wind_speed=12.0,  # Above threshold (should trigger adjustment)
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
            mock_simulate.return_value = mock_data
            
            # Trigger data collection
            data = await monitoring_service._collect_monitoring_data(sample_session.session_id)
            assert data is not None
            
            # Check for adjustments
            adjustments = await monitoring_service._check_adjustment_needs(sample_session.session_id, data)
            assert len(adjustments) > 0
            
            # Verify adjustment types
            adjustment_types = [adj.adjustment_type for adj in adjustments]
            assert AdjustmentType.RATE_ADJUSTMENT in adjustment_types
            assert AdjustmentType.COVERAGE_ADJUSTMENT in adjustment_types
            assert AdjustmentType.WEATHER_ADJUSTMENT in adjustment_types
        
        # Clean up
        await monitoring_service.stop_monitoring(sample_session.session_id)
        for config in sample_sensor_configs:
            await iot_service.unregister_sensor(config.sensor_id)
        await iot_service.stop_service()
    
    @pytest.mark.asyncio
    async def test_alert_generation_with_sensor_data(
        self, 
        monitoring_service, 
        iot_service, 
        sample_session, 
        sample_monitoring_config, 
        sample_sensor_configs
    ):
        """Test alert generation based on sensor data."""
        
        # Start services
        await iot_service.start_service()
        await monitoring_service.start_monitoring(sample_session, sample_monitoring_config)
        
        # Register sensors
        for config in sample_sensor_configs:
            await iot_service.register_sensor(config)
        
        # Wait for initial data collection
        await asyncio.sleep(2)
        
        # Simulate sensor data that should trigger alerts
        with patch.object(monitoring_service, '_simulate_monitoring_data') as mock_simulate:
            # Create monitoring data that should trigger alerts
            mock_data = ApplicationMonitoringData(
                application_session_id=sample_session.session_id,
                equipment_id=sample_session.equipment_id,
                field_id=sample_session.field_id,
                application_rate=180.0,  # 20% above target (should trigger critical alert)
                target_rate=150.0,
                rate_deviation=20.0,
                coverage_uniformity=0.7,  # Below threshold (should trigger alert)
                coverage_area=0.5,
                overlap_percentage=10.0,
                speed=6.0,
                pressure=30.0,
                temperature=70.0,
                humidity=60.0,
                wind_speed=18.0,  # Above critical threshold (should trigger critical alert)
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
            mock_simulate.return_value = mock_data
            
            # Trigger data collection
            data = await monitoring_service._collect_monitoring_data(sample_session.session_id)
            assert data is not None
            
            # Check for alerts
            alerts = await monitoring_service._check_alerts(sample_session.session_id, data)
            assert len(alerts) > 0
            
            # Verify alert types and severities
            alert_types = [alert.alert_type for alert in alerts]
            alert_severities = [alert.severity for alert in alerts]
            
            assert "rate_deviation" in alert_types
            assert "high_wind" in alert_types
            assert AlertSeverity.HIGH in alert_severities or AlertSeverity.CRITICAL in alert_severities
        
        # Clean up
        await monitoring_service.stop_monitoring(sample_session.session_id)
        for config in sample_sensor_configs:
            await iot_service.unregister_sensor(config.sensor_id)
        await iot_service.stop_service()
    
    @pytest.mark.asyncio
    async def test_quality_control_with_sensor_data(
        self, 
        monitoring_service, 
        iot_service, 
        sample_session, 
        sample_monitoring_config, 
        sample_sensor_configs
    ):
        """Test quality control checks with sensor data."""
        
        # Start services
        await iot_service.start_service()
        await monitoring_service.start_monitoring(sample_session, sample_monitoring_config)
        
        # Register sensors
        for config in sample_sensor_configs:
            await iot_service.register_sensor(config)
        
        # Wait for initial data collection
        await asyncio.sleep(2)
        
        # Add some monitoring data for quality control
        for i in range(10):
            data = ApplicationMonitoringData(
                application_session_id=sample_session.session_id,
                equipment_id=sample_session.equipment_id,
                field_id=sample_session.field_id,
                application_rate=150.0 + i,  # Varying rates
                target_rate=150.0,
                rate_deviation=i * 2,  # Increasing deviation
                coverage_uniformity=0.9 - (i * 0.01),  # Decreasing uniformity
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
            monitoring_service.monitoring_data[sample_session.session_id].append(data)
        
        # Perform quality control check
        quality_check = await monitoring_service._perform_quality_check(sample_session.session_id)
        
        assert quality_check is not None
        assert quality_check.session_id == sample_session.session_id
        assert quality_check.check_type == "comprehensive_quality_check"
        assert 0 <= quality_check.score <= 1
        assert len(quality_check.deviations) > 0  # Should have some deviations
        assert len(quality_check.recommendations) > 0  # Should have recommendations
        
        # Clean up
        await monitoring_service.stop_monitoring(sample_session.session_id)
        for config in sample_sensor_configs:
            await iot_service.unregister_sensor(config.sensor_id)
        await iot_service.stop_service()
    
    @pytest.mark.asyncio
    async def test_sensor_data_aggregation_for_monitoring(
        self, 
        monitoring_service, 
        iot_service, 
        sample_session, 
        sample_monitoring_config, 
        sample_sensor_configs
    ):
        """Test sensor data aggregation for monitoring purposes."""
        
        # Start services
        await iot_service.start_service()
        await monitoring_service.start_monitoring(sample_session, sample_monitoring_config)
        
        # Register sensors
        for config in sample_sensor_configs:
            await iot_service.register_sensor(config)
        
        # Wait for data collection
        await asyncio.sleep(2)
        
        # Get aggregated sensor data
        aggregated_data = await iot_service.aggregate_sensor_data(
            sample_session.equipment_id,
            [SensorType.FLOW_METER, SensorType.PRESSURE_SENSOR, SensorType.WEATHER_STATION],
            5
        )
        
        assert len(aggregated_data) > 0
        
        # Verify aggregated data structure
        for sensor_id, data in aggregated_data.items():
            assert "sensor_type" in data
            assert "data_quality" in data
            assert "statistics" in data
            assert "last_update" in data
            
            # Verify statistics structure
            stats = data["statistics"]
            for metric, stat_data in stats.items():
                assert "latest" in stat_data
                assert "average" in stat_data
                assert "min" in stat_data
                assert "max" in stat_data
                assert "count" in stat_data
        
        # Clean up
        await monitoring_service.stop_monitoring(sample_session.session_id)
        for config in sample_sensor_configs:
            await iot_service.unregister_sensor(config.sensor_id)
        await iot_service.stop_service()
    
    @pytest.mark.asyncio
    async def test_monitoring_summary_with_sensor_integration(
        self, 
        monitoring_service, 
        iot_service, 
        sample_session, 
        sample_monitoring_config, 
        sample_sensor_configs
    ):
        """Test monitoring summary generation with sensor integration."""
        
        # Start services
        await iot_service.start_service()
        await monitoring_service.start_monitoring(sample_session, sample_monitoring_config)
        
        # Register sensors
        for config in sample_sensor_configs:
            await iot_service.register_sensor(config)
        
        # Wait for data collection
        await asyncio.sleep(2)
        
        # Add some monitoring data
        for i in range(5):
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
            monitoring_service.monitoring_data[sample_session.session_id].append(data)
        
        # Add some adjustments
        from src.models.application_monitoring_models import RealTimeAdjustment
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
        monitoring_service.active_adjustments[sample_session.session_id] = [adjustment]
        
        # Add some alerts
        from src.models.application_monitoring_models import MonitoringAlert
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
        monitoring_service.active_alerts[sample_session.session_id] = [alert]
        
        # Get monitoring summary
        summary = await monitoring_service.get_monitoring_summary(sample_session.session_id)
        
        assert summary is not None
        assert summary.session_id == sample_session.session_id
        assert summary.total_data_points == 5
        assert summary.total_adjustments == 1
        assert summary.successful_adjustments == 1
        assert summary.total_alerts == 1
        assert summary.resolved_alerts == 1
        assert summary.adjustment_success_rate == 1.0
        
        # Clean up
        await monitoring_service.stop_monitoring(sample_session.session_id)
        for config in sample_sensor_configs:
            await iot_service.unregister_sensor(config.sensor_id)
        await iot_service.stop_service()
    
    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(
        self, 
        monitoring_service, 
        iot_service, 
        sample_session, 
        sample_monitoring_config, 
        sample_sensor_configs
    ):
        """Test error handling and recovery in integrated system."""
        
        # Start services
        await iot_service.start_service()
        await monitoring_service.start_monitoring(sample_session, sample_monitoring_config)
        
        # Register sensors
        for config in sample_sensor_configs:
            await iot_service.register_sensor(config)
        
        # Wait for initial data collection
        await asyncio.sleep(2)
        
        # Simulate sensor disconnection
        await iot_service.unregister_sensor(sample_sensor_configs[0].sensor_id)
        
        # Wait a bit
        await asyncio.sleep(1)
        
        # Verify monitoring continues despite sensor disconnection
        status = await monitoring_service.get_monitoring_status(sample_session.session_id)
        assert status["monitoring_enabled"] is True
        
        # Verify IoT service status reflects disconnection
        iot_status = await iot_service.get_sensor_status()
        assert iot_status["total_sensors"] == 2  # One sensor removed
        
        # Re-register sensor
        await iot_service.register_sensor(sample_sensor_configs[0])
        
        # Wait for recovery
        await asyncio.sleep(1)
        
        # Verify sensor is back online
        iot_status = await iot_service.get_sensor_status()
        assert iot_status["total_sensors"] == 3
        
        # Clean up
        await monitoring_service.stop_monitoring(sample_session.session_id)
        for config in sample_sensor_configs:
            await iot_service.unregister_sensor(config.sensor_id)
        await iot_service.stop_service()
    
    @pytest.mark.asyncio
    async def test_concurrent_monitoring_sessions(
        self, 
        monitoring_service, 
        iot_service
    ):
        """Test handling multiple concurrent monitoring sessions."""
        
        # Create multiple sessions
        sessions = []
        configs = []
        
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
        
        # Start services
        await iot_service.start_service()
        
        # Start all monitoring sessions concurrently
        tasks = [monitoring_service.start_monitoring(session, config) for session, config in zip(sessions, configs)]
        results = await asyncio.gather(*tasks)
        
        assert all(results)
        
        # Wait for data collection
        await asyncio.sleep(2)
        
        # Verify all sessions are monitoring
        for session in sessions:
            status = await monitoring_service.get_monitoring_status(session.session_id)
            assert status["monitoring_enabled"] is True
            assert status["data_points"] > 0
        
        # Stop all sessions concurrently
        tasks = [monitoring_service.stop_monitoring(session.session_id) for session in sessions]
        results = await asyncio.gather(*tasks)
        
        assert all(results)
        
        # Verify all sessions stopped
        for session in sessions:
            status = await monitoring_service.get_monitoring_status(session.session_id)
            assert status["monitoring_enabled"] is False
        
        await iot_service.stop_service()