"""
Tests for IoT sensor integration service.

This module contains comprehensive tests for the IoT sensor service,
including unit tests, integration tests, and performance tests.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from typing import List, Dict, Any

from src.services.iot_sensor_service import (
    IoTSensorService, SensorConfiguration, SensorHealth, SensorStatus, DataQuality,
    MQTTSensorConnector, HTTPSensorConnector, WebSocketSensorConnector
)
from src.models.application_monitoring_models import SensorData, SensorType, IoTProtocol


class TestIoTSensorService:
    """Test suite for IoTSensorService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return IoTSensorService()
    
    @pytest.fixture
    def sample_config(self):
        """Create sample sensor configuration."""
        return SensorConfiguration(
            sensor_id="test_sensor_001",
            sensor_type=SensorType.FLOW_METER,
            equipment_id="equipment_456",
            location={"latitude": 40.123456, "longitude": -95.654321, "elevation": 950.0},
            calibration_data={"flow_factor": 1.0, "pressure_offset": 0.0},
            update_frequency_seconds=5,
            data_retention_hours=24,
            alert_thresholds={"flow_rate": 50.0, "pressure": 45.0},
            connection_params={
                "protocol": "mqtt",
                "broker_url": "mqtt://localhost:1883",
                "topic": "sensors/test_sensor_001"
            }
        )
    
    @pytest.fixture
    def sample_sensor_data(self):
        """Create sample sensor data."""
        return SensorData(
            sensor_id="test_sensor_001",
            sensor_type=SensorType.FLOW_METER,
            equipment_id="equipment_456",
            readings={
                "flow_rate": 25.5,
                "total_volume": 150.0,
                "pressure": 32.5,
                "temperature": 72.0
            },
            data_quality=0.95,
            battery_level=85.0,
            signal_strength=92.0
        )
    
    @pytest.mark.asyncio
    async def test_start_service(self, service):
        """Test service startup."""
        success = await service.start_service()
        
        assert success is True
        assert service.is_running is True
        assert service.health_monitoring_task is not None
    
    @pytest.mark.asyncio
    async def test_stop_service(self, service):
        """Test service shutdown."""
        # Start service first
        await service.start_service()
        
        success = await service.stop_service()
        
        assert success is True
        assert service.is_running is False
        assert service.health_monitoring_task is None
    
    @pytest.mark.asyncio
    async def test_register_sensor_success(self, service, sample_config):
        """Test successful sensor registration."""
        # Start service first
        await service.start_service()
        
        success = await service.register_sensor(sample_config)
        
        assert success is True
        assert sample_config.sensor_id in service.sensor_connectors
        assert sample_config.sensor_id in service.sensor_configs
        assert sample_config.sensor_id in service.sensor_data_cache
        assert sample_config.sensor_id in service.data_collection_tasks
        
        # Clean up
        await service.stop_service()
    
    @pytest.mark.asyncio
    async def test_register_sensor_invalid_protocol(self, service):
        """Test sensor registration with invalid protocol."""
        config = SensorConfiguration(
            sensor_id="test_sensor_002",
            sensor_type=SensorType.FLOW_METER,
            equipment_id="equipment_456",
            location={"latitude": 40.0, "longitude": -95.0, "elevation": 900.0},
            calibration_data={},
            update_frequency_seconds=5,
            data_retention_hours=24,
            alert_thresholds={},
            connection_params={"protocol": "invalid_protocol"}
        )
        
        await service.start_service()
        
        success = await service.register_sensor(config)
        
        assert success is False
        assert config.sensor_id not in service.sensor_connectors
        
        await service.stop_service()
    
    @pytest.mark.asyncio
    async def test_unregister_sensor(self, service, sample_config):
        """Test sensor unregistration."""
        await service.start_service()
        await service.register_sensor(sample_config)
        
        success = await service.unregister_sensor(sample_config.sensor_id)
        
        assert success is True
        assert sample_config.sensor_id not in service.sensor_connectors
        assert sample_config.sensor_id not in service.sensor_configs
        assert sample_config.sensor_id not in service.sensor_data_cache
        assert sample_config.sensor_id not in service.data_collection_tasks
        
        await service.stop_service()
    
    @pytest.mark.asyncio
    async def test_get_sensor_data(self, service, sample_config, sample_sensor_data):
        """Test getting sensor data."""
        await service.start_service()
        await service.register_sensor(sample_config)
        
        # Add some sensor data
        service.sensor_data_cache[sample_config.sensor_id] = [sample_sensor_data]
        
        data = await service.get_sensor_data(sample_config.sensor_id, 60)
        
        assert len(data) == 1
        assert data[0].sensor_id == sample_config.sensor_id
        
        await service.stop_service()
    
    @pytest.mark.asyncio
    async def test_get_latest_sensor_data(self, service, sample_config, sample_sensor_data):
        """Test getting latest sensor data."""
        await service.start_service()
        await service.register_sensor(sample_config)
        
        # Add some sensor data
        service.sensor_data_cache[sample_config.sensor_id] = [sample_sensor_data]
        
        latest_data = await service.get_latest_sensor_data(sample_config.sensor_id)
        
        assert latest_data is not None
        assert latest_data.sensor_id == sample_config.sensor_id
        
        await service.stop_service()
    
    @pytest.mark.asyncio
    async def test_get_sensor_health(self, service, sample_config):
        """Test getting sensor health."""
        await service.start_service()
        await service.register_sensor(sample_config)
        
        health = await service.get_sensor_health(sample_config.sensor_id)
        
        assert health is not None
        assert health.sensor_id == sample_config.sensor_id
        assert health.status in [SensorStatus.ONLINE, SensorStatus.OFFLINE, SensorStatus.ERROR]
        
        await service.stop_service()
    
    @pytest.mark.asyncio
    async def test_get_all_sensor_health(self, service, sample_config):
        """Test getting all sensor health."""
        await service.start_service()
        await service.register_sensor(sample_config)
        
        all_health = await service.get_all_sensor_health()
        
        assert len(all_health) == 1
        assert sample_config.sensor_id in all_health
        
        await service.stop_service()
    
    @pytest.mark.asyncio
    async def test_send_sensor_command(self, service, sample_config):
        """Test sending command to sensor."""
        await service.start_service()
        await service.register_sensor(sample_config)
        
        success = await service.send_sensor_command(
            sample_config.sensor_id, 
            "calibrate", 
            {"factor": 1.05}
        )
        
        assert success is True
        
        await service.stop_service()
    
    @pytest.mark.asyncio
    async def test_calibrate_sensor(self, service, sample_config):
        """Test sensor calibration."""
        await service.start_service()
        await service.register_sensor(sample_config)
        
        calibration_data = {"flow_factor": 1.05, "pressure_offset": 0.1}
        
        success = await service.calibrate_sensor(sample_config.sensor_id, calibration_data)
        
        assert success is True
        
        # Check that calibration data was updated
        config = service.sensor_configs[sample_config.sensor_id]
        assert config.calibration_data["flow_factor"] == 1.05
        assert config.calibration_data["pressure_offset"] == 0.1
        
        await service.stop_service()
    
    @pytest.mark.asyncio
    async def test_aggregate_sensor_data(self, service, sample_config, sample_sensor_data):
        """Test sensor data aggregation."""
        await service.start_service()
        await service.register_sensor(sample_config)
        
        # Add some sensor data
        service.sensor_data_cache[sample_config.sensor_id] = [sample_sensor_data]
        
        aggregated = await service.aggregate_sensor_data(
            sample_config.equipment_id,
            [SensorType.FLOW_METER],
            5
        )
        
        assert len(aggregated) == 1
        assert sample_config.sensor_id in aggregated
        
        sensor_data = aggregated[sample_config.sensor_id]
        assert sensor_data["sensor_type"] == SensorType.FLOW_METER.value
        assert "statistics" in sensor_data
        
        await service.stop_service()
    
    @pytest.mark.asyncio
    async def test_get_sensor_status(self, service, sample_config):
        """Test getting sensor service status."""
        await service.start_service()
        await service.register_sensor(sample_config)
        
        status = await service.get_sensor_status()
        
        assert status["service_running"] is True
        assert status["total_sensors"] == 1
        assert status["online_sensors"] >= 0
        assert SensorType.FLOW_METER.value in status["sensor_types"]
        
        await service.stop_service()
    
    @pytest.mark.asyncio
    async def test_data_quality_assessment(self, service, sample_config):
        """Test data quality assessment."""
        await service.start_service()
        await service.register_sensor(sample_config)
        
        # Test with complete data
        complete_data = {
            "flow_rate": 25.5,
            "total_volume": 150.0,
            "pressure": 32.5,
            "temperature": 72.0
        }
        
        quality = service._assess_data_quality(complete_data, sample_config)
        assert quality > 0.8
        
        # Test with incomplete data
        incomplete_data = {
            "flow_rate": 25.5,
            "pressure": 32.5
            # Missing total_volume and temperature
        }
        
        quality = service._assess_data_quality(incomplete_data, sample_config)
        assert quality < 0.8
        
        await service.stop_service()
    
    @pytest.mark.asyncio
    async def test_cleanup_old_data(self, service, sample_config):
        """Test cleanup of old sensor data."""
        await service.start_service()
        await service.register_sensor(sample_config)
        
        # Add old data
        old_data = SensorData(
            sensor_id=sample_config.sensor_id,
            sensor_type=SensorType.FLOW_METER,
            equipment_id=sample_config.equipment_id,
            readings={"flow_rate": 25.0},
            timestamp=datetime.now() - timedelta(hours=25),  # Older than retention
            data_quality=0.9
        )
        
        # Add recent data
        recent_data = SensorData(
            sensor_id=sample_config.sensor_id,
            sensor_type=SensorType.FLOW_METER,
            equipment_id=sample_config.equipment_id,
            readings={"flow_rate": 25.5},
            timestamp=datetime.now() - timedelta(hours=1),  # Within retention
            data_quality=0.95
        )
        
        service.sensor_data_cache[sample_config.sensor_id] = [old_data, recent_data]
        
        # Cleanup old data
        await service._cleanup_old_data(sample_config.sensor_id, 24)
        
        remaining_data = service.sensor_data_cache[sample_config.sensor_id]
        assert len(remaining_data) == 1
        assert remaining_data[0].timestamp == recent_data.timestamp
        
        await service.stop_service()


class TestSensorConnectors:
    """Test suite for sensor connectors."""
    
    @pytest.fixture
    def sample_config(self):
        """Create sample sensor configuration."""
        return SensorConfiguration(
            sensor_id="test_sensor_001",
            sensor_type=SensorType.FLOW_METER,
            equipment_id="equipment_456",
            location={"latitude": 40.0, "longitude": -95.0, "elevation": 900.0},
            calibration_data={},
            update_frequency_seconds=5,
            data_retention_hours=24,
            alert_thresholds={},
            connection_params={"protocol": "mqtt"}
        )
    
    @pytest.mark.asyncio
    async def test_mqtt_connector_connect(self, sample_config):
        """Test MQTT connector connection."""
        connector = MQTTSensorConnector(sample_config.sensor_id, sample_config)
        
        success = await connector.connect()
        
        assert success is True
        assert connector.status == SensorStatus.ONLINE
    
    @pytest.mark.asyncio
    async def test_mqtt_connector_read_data(self, sample_config):
        """Test MQTT connector data reading."""
        connector = MQTTSensorConnector(sample_config.sensor_id, sample_config)
        await connector.connect()
        
        data = await connector.read_data()
        
        assert data is not None
        assert "flow_rate" in data
        assert "total_volume" in data
        assert "pressure" in data
        assert "temperature" in data
    
    @pytest.mark.asyncio
    async def test_mqtt_connector_send_command(self, sample_config):
        """Test MQTT connector command sending."""
        connector = MQTTSensorConnector(sample_config.sensor_id, sample_config)
        await connector.connect()
        
        success = await connector.send_command("calibrate", {"factor": 1.05})
        
        assert success is True
    
    @pytest.mark.asyncio
    async def test_mqtt_connector_health_status(self, sample_config):
        """Test MQTT connector health status."""
        connector = MQTTSensorConnector(sample_config.sensor_id, sample_config)
        await connector.connect()
        
        health = connector.get_health_status()
        
        assert health.sensor_id == sample_config.sensor_id
        assert health.status == SensorStatus.ONLINE
        assert health.data_quality == DataQuality.GOOD
        assert health.uptime_percentage == 100.0
    
    @pytest.mark.asyncio
    async def test_http_connector_connect(self, sample_config):
        """Test HTTP connector connection."""
        config = SensorConfiguration(
            sensor_id="test_sensor_002",
            sensor_type=SensorType.CAMERA_SENSOR,
            equipment_id="equipment_456",
            location={"latitude": 40.0, "longitude": -95.0, "elevation": 900.0},
            calibration_data={},
            update_frequency_seconds=5,
            data_retention_hours=24,
            alert_thresholds={},
            connection_params={
                "protocol": "http",
                "base_url": "http://sensor.example.com",
                "api_key": "test_key"
            }
        )
        
        connector = HTTPSensorConnector(config.sensor_id, config)
        
        success = await connector.connect()
        
        assert success is True
        assert connector.status == SensorStatus.ONLINE
        assert connector.session is not None
    
    @pytest.mark.asyncio
    async def test_http_connector_read_data(self, sample_config):
        """Test HTTP connector data reading."""
        config = SensorConfiguration(
            sensor_id="test_sensor_003",
            sensor_type=SensorType.CAMERA_SENSOR,
            equipment_id="equipment_456",
            location={"latitude": 40.0, "longitude": -95.0, "elevation": 900.0},
            calibration_data={},
            update_frequency_seconds=5,
            data_retention_hours=24,
            alert_thresholds={},
            connection_params={"protocol": "http"}
        )
        
        connector = HTTPSensorConnector(config.sensor_id, config)
        await connector.connect()
        
        data = await connector.read_data()
        
        assert data is not None
        assert "image_url" in data
        assert "image_quality" in data
        assert "detected_objects" in data
        assert "coverage_analysis" in data
    
    @pytest.mark.asyncio
    async def test_websocket_connector_connect(self, sample_config):
        """Test WebSocket connector connection."""
        config = SensorConfiguration(
            sensor_id="test_sensor_004",
            sensor_type=SensorType.SPEED_SENSOR,
            equipment_id="equipment_456",
            location={"latitude": 40.0, "longitude": -95.0, "elevation": 900.0},
            calibration_data={},
            update_frequency_seconds=5,
            data_retention_hours=24,
            alert_thresholds={},
            connection_params={
                "protocol": "websocket",
                "websocket_url": "ws://sensor.example.com"
            }
        )
        
        connector = WebSocketSensorConnector(config.sensor_id, config)
        
        success = await connector.connect()
        
        assert success is True
        assert connector.status == SensorStatus.ONLINE
    
    @pytest.mark.asyncio
    async def test_websocket_connector_read_data(self, sample_config):
        """Test WebSocket connector data reading."""
        config = SensorConfiguration(
            sensor_id="test_sensor_005",
            sensor_type=SensorType.SPEED_SENSOR,
            equipment_id="equipment_456",
            location={"latitude": 40.0, "longitude": -95.0, "elevation": 900.0},
            calibration_data={},
            update_frequency_seconds=5,
            data_retention_hours=24,
            alert_thresholds={},
            connection_params={"protocol": "websocket"}
        )
        
        connector = WebSocketSensorConnector(config.sensor_id, config)
        await connector.connect()
        
        data = await connector.read_data()
        
        assert data is not None
        assert "speed" in data
        assert "distance" in data
        assert "acceleration" in data
        assert "direction" in data


class TestIoTSensorIntegration:
    """Integration tests for IoT sensor service."""
    
    @pytest.mark.asyncio
    async def test_full_sensor_workflow(self):
        """Test complete sensor workflow from registration to data collection."""
        service = IoTSensorService()
        
        # Create sensor configuration
        config = SensorConfiguration(
            sensor_id="integration_test_sensor",
            sensor_type=SensorType.WEATHER_STATION,
            equipment_id="equipment_456",
            location={"latitude": 40.123456, "longitude": -95.654321, "elevation": 950.0},
            calibration_data={"temperature_offset": 0.0, "humidity_calibration": 1.0},
            update_frequency_seconds=1,  # Fast for testing
            data_retention_hours=1,  # Short for testing
            alert_thresholds={"wind_speed": 15.0, "temperature": 100.0},
            connection_params={"protocol": "mqtt"}
        )
        
        # Start service
        await service.start_service()
        
        # Register sensor
        success = await service.register_sensor(config)
        assert success is True
        
        # Wait for data collection
        await asyncio.sleep(2)
        
        # Check that data is being collected
        data = await service.get_sensor_data(config.sensor_id, 5)
        assert len(data) > 0
        
        # Check sensor health
        health = await service.get_sensor_health(config.sensor_id)
        assert health is not None
        assert health.status == SensorStatus.ONLINE
        
        # Send command
        command_success = await service.send_sensor_command(
            config.sensor_id, 
            "calibrate", 
            {"temperature_offset": 0.5}
        )
        assert command_success is True
        
        # Get aggregated data
        aggregated = await service.aggregate_sensor_data(
            config.equipment_id,
            [SensorType.WEATHER_STATION],
            5
        )
        assert len(aggregated) == 1
        
        # Unregister sensor
        unregister_success = await service.unregister_sensor(config.sensor_id)
        assert unregister_success is True
        
        # Stop service
        await service.stop_service()
    
    @pytest.mark.asyncio
    async def test_multiple_sensor_types(self):
        """Test handling multiple sensor types simultaneously."""
        service = IoTSensorService()
        
        # Create multiple sensor configurations
        configs = [
            SensorConfiguration(
                sensor_id=f"sensor_{i}",
                sensor_type=sensor_type,
                equipment_id="equipment_456",
                location={"latitude": 40.0, "longitude": -95.0, "elevation": 900.0},
                calibration_data={},
                update_frequency_seconds=1,
                data_retention_hours=1,
                alert_thresholds={},
                connection_params={"protocol": "mqtt"}
            )
            for i, sensor_type in enumerate([
                SensorType.FLOW_METER,
                SensorType.PRESSURE_SENSOR,
                SensorType.WEATHER_STATION,
                SensorType.SOIL_MOISTURE_SENSOR,
                SensorType.GPS_SENSOR
            ])
        ]
        
        await service.start_service()
        
        # Register all sensors
        for config in configs:
            success = await service.register_sensor(config)
            assert success is True
        
        # Wait for data collection
        await asyncio.sleep(2)
        
        # Check all sensors are collecting data
        for config in configs:
            data = await service.get_sensor_data(config.sensor_id, 5)
            assert len(data) > 0
        
        # Check service status
        status = await service.get_sensor_status()
        assert status["total_sensors"] == 5
        assert status["online_sensors"] >= 0
        
        # Unregister all sensors
        for config in configs:
            success = await service.unregister_sensor(config.sensor_id)
            assert success is True
        
        await service.stop_service()


class TestIoTSensorPerformance:
    """Performance tests for IoT sensor service."""
    
    @pytest.mark.asyncio
    async def test_data_collection_performance(self):
        """Test performance of data collection."""
        service = IoTSensorService()
        
        config = SensorConfiguration(
            sensor_id="performance_test_sensor",
            sensor_type=SensorType.FLOW_METER,
            equipment_id="equipment_456",
            location={"latitude": 40.0, "longitude": -95.0, "elevation": 900.0},
            calibration_data={},
            update_frequency_seconds=1,
            data_retention_hours=1,
            alert_thresholds={},
            connection_params={"protocol": "mqtt"}
        )
        
        await service.start_service()
        await service.register_sensor(config)
        
        # Measure data collection time
        start_time = datetime.now()
        
        # Collect multiple data points
        for _ in range(10):
            data = await service.get_latest_sensor_data(config.sensor_id)
            assert data is not None
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Should be able to get 10 data points quickly
        assert duration < 2.0
        
        await service.stop_service()
    
    @pytest.mark.asyncio
    async def test_concurrent_sensor_operations(self):
        """Test concurrent operations on multiple sensors."""
        service = IoTSensorService()
        
        # Create multiple sensors
        configs = [
            SensorConfiguration(
                sensor_id=f"concurrent_sensor_{i}",
                sensor_type=SensorType.FLOW_METER,
                equipment_id="equipment_456",
                location={"latitude": 40.0, "longitude": -95.0, "elevation": 900.0},
                calibration_data={},
                update_frequency_seconds=1,
                data_retention_hours=1,
                alert_thresholds={},
                connection_params={"protocol": "mqtt"}
            )
            for i in range(5)
        ]
        
        await service.start_service()
        
        # Register all sensors concurrently
        tasks = [service.register_sensor(config) for config in configs]
        results = await asyncio.gather(*tasks)
        
        assert all(results)
        
        # Wait for data collection
        await asyncio.sleep(2)
        
        # Get data from all sensors concurrently
        tasks = [service.get_sensor_data(config.sensor_id, 5) for config in configs]
        data_results = await asyncio.gather(*tasks)
        
        for data in data_results:
            assert len(data) > 0
        
        # Get health from all sensors concurrently
        tasks = [service.get_sensor_health(config.sensor_id) for config in configs]
        health_results = await asyncio.gather(*tasks)
        
        for health in health_results:
            assert health is not None
        
        await service.stop_service()