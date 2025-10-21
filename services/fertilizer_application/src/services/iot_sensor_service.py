"""
IoT Sensor Integration Service for real-time data collection.

This service provides integration with various IoT sensors for collecting
real-time data during fertilizer application, including flow meters,
pressure sensors, weather stations, GPS, and soil moisture sensors.
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from uuid import uuid4
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import aiohttp
import socketio

from src.models.application_monitoring_models import (
    SensorData, SensorType, ApplicationMonitoringData
)

logger = logging.getLogger(__name__)


class SensorStatus(str, Enum):
    """Sensor status levels."""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    CALIBRATING = "calibrating"
    MAINTENANCE = "maintenance"


class DataQuality(str, Enum):
    """Data quality levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    INVALID = "invalid"


@dataclass
class SensorConfiguration:
    """Configuration for IoT sensors."""
    sensor_id: str
    sensor_type: SensorType
    equipment_id: str
    location: Dict[str, float]  # lat, lng, elevation
    calibration_data: Dict[str, Any]
    update_frequency_seconds: int
    data_retention_hours: int
    alert_thresholds: Dict[str, float]
    connection_params: Dict[str, Any]


@dataclass
class SensorHealth:
    """Sensor health status."""
    sensor_id: str
    status: SensorStatus
    last_seen: datetime
    battery_level: Optional[float]
    signal_strength: Optional[float]
    data_quality: DataQuality
    error_count: int
    uptime_percentage: float
    maintenance_due: bool


class IoTProtocol(str, Enum):
    """IoT communication protocols."""
    MQTT = "mqtt"
    HTTP = "http"
    WEBSOCKET = "websocket"
    MODBUS = "modbus"
    LORA = "lora"
    NB_IOT = "nb_iot"


class SensorConnector:
    """Base class for sensor connectors."""
    
    def __init__(self, sensor_id: str, config: SensorConfiguration):
        self.sensor_id = sensor_id
        self.config = config
        self.status = SensorStatus.OFFLINE
        self.last_data_time = None
        self.error_count = 0
        self.connection = None
    
    async def connect(self) -> bool:
        """Connect to sensor."""
        raise NotImplementedError
    
    async def disconnect(self):
        """Disconnect from sensor."""
        raise NotImplementedError
    
    async def read_data(self) -> Optional[Dict[str, Any]]:
        """Read data from sensor."""
        raise NotImplementedError
    
    async def send_command(self, command: str, params: Dict[str, Any]) -> bool:
        """Send command to sensor."""
        raise NotImplementedError
    
    def get_health_status(self) -> SensorHealth:
        """Get sensor health status."""
        uptime_percentage = 100.0  # Simplified calculation
        if self.error_count > 10:
            uptime_percentage = max(0, 100 - (self.error_count * 5))
        
        return SensorHealth(
            sensor_id=self.sensor_id,
            status=self.status,
            last_seen=self.last_data_time or datetime.now(),
            battery_level=None,  # Would be set by specific sensor types
            signal_strength=None,  # Would be set by specific sensor types
            data_quality=DataQuality.GOOD if self.error_count < 5 else DataQuality.POOR,
            error_count=self.error_count,
            uptime_percentage=uptime_percentage,
            maintenance_due=self.error_count > 20
        )


class MQTTSensorConnector(SensorConnector):
    """MQTT-based sensor connector."""
    
    def __init__(self, sensor_id: str, config: SensorConfiguration):
        super().__init__(sensor_id, config)
        self.mqtt_client = None
        self.topic_prefix = f"sensors/{sensor_id}"
    
    async def connect(self) -> bool:
        """Connect to MQTT broker."""
        try:
            # In real implementation, would use actual MQTT client
            # For now, simulate connection
            self.status = SensorStatus.ONLINE
            logger.info(f"MQTT sensor {self.sensor_id} connected")
            return True
        except Exception as e:
            logger.error(f"Failed to connect MQTT sensor {self.sensor_id}: {e}")
            self.status = SensorStatus.ERROR
            self.error_count += 1
            return False
    
    async def disconnect(self):
        """Disconnect from MQTT broker."""
        self.status = SensorStatus.OFFLINE
        logger.info(f"MQTT sensor {self.sensor_id} disconnected")
    
    async def read_data(self) -> Optional[Dict[str, Any]]:
        """Read data from MQTT sensor."""
        try:
            if self.status != SensorStatus.ONLINE:
                return None
            
            # Simulate MQTT data reading
            data = await self._simulate_sensor_data()
            self.last_data_time = datetime.now()
            return data
            
        except Exception as e:
            logger.error(f"Error reading MQTT sensor {self.sensor_id}: {e}")
            self.error_count += 1
            return None
    
    async def send_command(self, command: str, params: Dict[str, Any]) -> bool:
        """Send command via MQTT."""
        try:
            # In real implementation, would publish to command topic
            logger.info(f"Sending command {command} to sensor {self.sensor_id}")
            return True
        except Exception as e:
            logger.error(f"Error sending command to sensor {self.sensor_id}: {e}")
            return False
    
    async def _simulate_sensor_data(self) -> Dict[str, Any]:
        """Simulate sensor data based on sensor type."""
        import random
        
        if self.config.sensor_type == SensorType.FLOW_METER:
            return {
                "flow_rate": random.uniform(10, 50),  # GPM
                "total_volume": random.uniform(100, 500),  # Gallons
                "pressure": random.uniform(25, 40),  # PSI
                "temperature": random.uniform(60, 80)  # °F
            }
        elif self.config.sensor_type == SensorType.PRESSURE_SENSOR:
            return {
                "pressure": random.uniform(25, 40),  # PSI
                "temperature": random.uniform(60, 80),  # °F
                "vibration": random.uniform(0, 10)  # mm/s
            }
        elif self.config.sensor_type == SensorType.WEATHER_STATION:
            return {
                "temperature": random.uniform(60, 85),  # °F
                "humidity": random.uniform(40, 80),  # %
                "wind_speed": random.uniform(2, 15),  # MPH
                "wind_direction": random.uniform(0, 360),  # Degrees
                "pressure": random.uniform(29.5, 30.5),  # inHg
                "precipitation": random.uniform(0, 0.5),  # inches
                "solar_radiation": random.uniform(200, 1000)  # W/m²
            }
        elif self.config.sensor_type == SensorType.SOIL_MOISTURE_SENSOR:
            return {
                "moisture": random.uniform(20, 60),  # %
                "temperature": random.uniform(55, 75),  # °F
                "conductivity": random.uniform(0.1, 2.0),  # mS/cm
                "ph": random.uniform(6.0, 7.5)
            }
        elif self.config.sensor_type == SensorType.GPS_SENSOR:
            return {
                "latitude": random.uniform(40.0, 41.0),
                "longitude": random.uniform(-95.0, -94.0),
                "elevation": random.uniform(800, 1200),  # Feet
                "accuracy": random.uniform(1, 5),  # Meters
                "speed": random.uniform(0, 10),  # MPH
                "heading": random.uniform(0, 360)  # Degrees
            }
        else:
            return {"value": random.uniform(0, 100)}


class HTTPSensorConnector(SensorConnector):
    """HTTP-based sensor connector."""
    
    def __init__(self, sensor_id: str, config: SensorConfiguration):
        super().__init__(sensor_id, config)
        self.base_url = config.connection_params.get("base_url", "")
        self.api_key = config.connection_params.get("api_key", "")
        self.session = None
    
    async def connect(self) -> bool:
        """Connect to HTTP sensor."""
        try:
            self.session = aiohttp.ClientSession()
            self.status = SensorStatus.ONLINE
            logger.info(f"HTTP sensor {self.sensor_id} connected")
            return True
        except Exception as e:
            logger.error(f"Failed to connect HTTP sensor {self.sensor_id}: {e}")
            self.status = SensorStatus.ERROR
            self.error_count += 1
            return False
    
    async def disconnect(self):
        """Disconnect from HTTP sensor."""
        if self.session:
            await self.session.close()
        self.status = SensorStatus.OFFLINE
        logger.info(f"HTTP sensor {self.sensor_id} disconnected")
    
    async def read_data(self) -> Optional[Dict[str, Any]]:
        """Read data from HTTP sensor."""
        try:
            if not self.session or self.status != SensorStatus.ONLINE:
                return None
            
            # In real implementation, would make HTTP request
            # For now, simulate data
            data = await self._simulate_sensor_data()
            self.last_data_time = datetime.now()
            return data
            
        except Exception as e:
            logger.error(f"Error reading HTTP sensor {self.sensor_id}: {e}")
            self.error_count += 1
            return None
    
    async def send_command(self, command: str, params: Dict[str, Any]) -> bool:
        """Send command via HTTP."""
        try:
            # In real implementation, would make HTTP POST request
            logger.info(f"Sending command {command} to sensor {self.sensor_id}")
            return True
        except Exception as e:
            logger.error(f"Error sending command to sensor {self.sensor_id}: {e}")
            return False
    
    async def _simulate_sensor_data(self) -> Dict[str, Any]:
        """Simulate sensor data."""
        import random
        
        if self.config.sensor_type == SensorType.CAMERA_SENSOR:
            return {
                "image_url": f"http://sensor/{self.sensor_id}/image.jpg",
                "image_timestamp": datetime.now().isoformat(),
                "image_quality": random.uniform(0.8, 1.0),
                "detected_objects": ["crop", "soil", "equipment"],
                "coverage_analysis": {
                    "coverage_percentage": random.uniform(85, 98),
                    "uniformity_score": random.uniform(0.8, 0.95)
                }
            }
        else:
            return {"value": random.uniform(0, 100)}


class WebSocketSensorConnector(SensorConnector):
    """WebSocket-based sensor connector."""
    
    def __init__(self, sensor_id: str, config: SensorConfiguration):
        super().__init__(sensor_id, config)
        self.websocket_url = config.connection_params.get("websocket_url", "")
        self.sio = None
    
    async def connect(self) -> bool:
        """Connect to WebSocket sensor."""
        try:
            # In real implementation, would use actual WebSocket client
            self.status = SensorStatus.ONLINE
            logger.info(f"WebSocket sensor {self.sensor_id} connected")
            return True
        except Exception as e:
            logger.error(f"Failed to connect WebSocket sensor {self.sensor_id}: {e}")
            self.status = SensorStatus.ERROR
            self.error_count += 1
            return False
    
    async def disconnect(self):
        """Disconnect from WebSocket sensor."""
        self.status = SensorStatus.OFFLINE
        logger.info(f"WebSocket sensor {self.sensor_id} disconnected")
    
    async def read_data(self) -> Optional[Dict[str, Any]]:
        """Read data from WebSocket sensor."""
        try:
            if self.status != SensorStatus.ONLINE:
                return None
            
            # Simulate WebSocket data reading
            data = await self._simulate_sensor_data()
            self.last_data_time = datetime.now()
            return data
            
        except Exception as e:
            logger.error(f"Error reading WebSocket sensor {self.sensor_id}: {e}")
            self.error_count += 1
            return None
    
    async def send_command(self, command: str, params: Dict[str, Any]) -> bool:
        """Send command via WebSocket."""
        try:
            # In real implementation, would emit WebSocket message
            logger.info(f"Sending command {command} to sensor {self.sensor_id}")
            return True
        except Exception as e:
            logger.error(f"Error sending command to sensor {self.sensor_id}: {e}")
            return False
    
    async def _simulate_sensor_data(self) -> Dict[str, Any]:
        """Simulate sensor data."""
        import random
        
        if self.config.sensor_type == SensorType.SPEED_SENSOR:
            return {
                "speed": random.uniform(4, 8),  # MPH
                "distance": random.uniform(0.1, 0.5),  # Miles
                "acceleration": random.uniform(-2, 2),  # m/s²
                "direction": random.uniform(0, 360)  # Degrees
            }
        else:
            return {"value": random.uniform(0, 100)}


class IoTSensorService:
    """Service for managing IoT sensor connections and data collection."""
    
    def __init__(self):
        self.sensor_connectors: Dict[str, SensorConnector] = {}
        self.sensor_configs: Dict[str, SensorConfiguration] = {}
        self.data_collection_tasks: Dict[str, asyncio.Task] = {}
        self.sensor_data_cache: Dict[str, List[SensorData]] = {}
        self.health_monitoring_task: Optional[asyncio.Task] = None
        self.is_running = False
        
        logger.info("IoT Sensor Service initialized")
    
    async def start_service(self):
        """Start the IoT sensor service."""
        try:
            self.is_running = True
            
            # Start health monitoring task
            self.health_monitoring_task = asyncio.create_task(self._health_monitoring_loop())
            
            logger.info("IoT Sensor Service started")
            return True
            
        except Exception as e:
            logger.error(f"Error starting IoT Sensor Service: {e}")
            return False
    
    async def stop_service(self):
        """Stop the IoT sensor service."""
        try:
            self.is_running = False
            
            # Stop all data collection tasks
            for task in self.data_collection_tasks.values():
                task.cancel()
            self.data_collection_tasks.clear()
            
            # Disconnect all sensors
            for connector in self.sensor_connectors.values():
                await connector.disconnect()
            
            # Stop health monitoring
            if self.health_monitoring_task:
                self.health_monitoring_task.cancel()
            
            logger.info("IoT Sensor Service stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping IoT Sensor Service: {e}")
            return False
    
    async def register_sensor(self, config: SensorConfiguration) -> bool:
        """Register a new sensor."""
        try:
            logger.info(f"Registering sensor {config.sensor_id} of type {config.sensor_type}")
            
            # Create appropriate connector based on connection params
            connector = await self._create_sensor_connector(config)
            
            if not connector:
                logger.error(f"Failed to create connector for sensor {config.sensor_id}")
                return False
            
            # Connect to sensor
            connected = await connector.connect()
            if not connected:
                logger.error(f"Failed to connect to sensor {config.sensor_id}")
                return False
            
            # Store connector and config
            self.sensor_connectors[config.sensor_id] = connector
            self.sensor_configs[config.sensor_id] = config
            self.sensor_data_cache[config.sensor_id] = []
            
            # Start data collection task
            if self.is_running:
                task = asyncio.create_task(
                    self._data_collection_loop(config.sensor_id, connector)
                )
                self.data_collection_tasks[config.sensor_id] = task
            
            logger.info(f"Sensor {config.sensor_id} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error registering sensor {config.sensor_id}: {e}")
            return False
    
    async def unregister_sensor(self, sensor_id: str) -> bool:
        """Unregister a sensor."""
        try:
            logger.info(f"Unregistering sensor {sensor_id}")
            
            # Stop data collection task
            if sensor_id in self.data_collection_tasks:
                self.data_collection_tasks[sensor_id].cancel()
                del self.data_collection_tasks[sensor_id]
            
            # Disconnect sensor
            if sensor_id in self.sensor_connectors:
                await self.sensor_connectors[sensor_id].disconnect()
                del self.sensor_connectors[sensor_id]
            
            # Remove config and cache
            if sensor_id in self.sensor_configs:
                del self.sensor_configs[sensor_id]
            
            if sensor_id in self.sensor_data_cache:
                del self.sensor_data_cache[sensor_id]
            
            logger.info(f"Sensor {sensor_id} unregistered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error unregistering sensor {sensor_id}: {e}")
            return False
    
    async def _create_sensor_connector(self, config: SensorConfiguration) -> Optional[SensorConnector]:
        """Create appropriate sensor connector based on configuration."""
        protocol = config.connection_params.get("protocol", "mqtt")
        
        if protocol == IoTProtocol.MQTT:
            return MQTTSensorConnector(config.sensor_id, config)
        elif protocol == IoTProtocol.HTTP:
            return HTTPSensorConnector(config.sensor_id, config)
        elif protocol == IoTProtocol.WEBSOCKET:
            return WebSocketSensorConnector(config.sensor_id, config)
        else:
            logger.error(f"Unsupported protocol: {protocol}")
            return None
    
    async def _data_collection_loop(self, sensor_id: str, connector: SensorConnector):
        """Data collection loop for a sensor."""
        config = self.sensor_configs[sensor_id]
        
        while self.is_running:
            try:
                # Read data from sensor
                raw_data = await connector.read_data()
                
                if raw_data:
                    # Create sensor data object
                    sensor_data = SensorData(
                        sensor_id=sensor_id,
                        sensor_type=config.sensor_type,
                        equipment_id=config.equipment_id,
                        readings=raw_data,
                        data_quality=self._assess_data_quality(raw_data, config),
                        battery_level=raw_data.get("battery_level"),
                        signal_strength=raw_data.get("signal_strength")
                    )
                    
                    # Store data
                    self.sensor_data_cache[sensor_id].append(sensor_data)
                    
                    # Clean up old data
                    await self._cleanup_old_data(sensor_id, config.data_retention_hours)
                    
                    logger.debug(f"Collected data from sensor {sensor_id}")
                
                # Wait for next collection cycle
                await asyncio.sleep(config.update_frequency_seconds)
                
            except asyncio.CancelledError:
                logger.info(f"Data collection loop cancelled for sensor {sensor_id}")
                break
            except Exception as e:
                logger.error(f"Error in data collection loop for sensor {sensor_id}: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _health_monitoring_loop(self):
        """Health monitoring loop for all sensors."""
        while self.is_running:
            try:
                for sensor_id, connector in self.sensor_connectors.items():
                    health = connector.get_health_status()
                    
                    # Check for health issues
                    if health.status == SensorStatus.ERROR:
                        logger.warning(f"Sensor {sensor_id} is in error state")
                    elif health.maintenance_due:
                        logger.warning(f"Sensor {sensor_id} requires maintenance")
                    elif health.data_quality == DataQuality.POOR:
                        logger.warning(f"Sensor {sensor_id} has poor data quality")
                
                # Wait before next health check
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                logger.info("Health monitoring loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(60)
    
    def _assess_data_quality(self, raw_data: Dict[str, Any], config: SensorConfiguration) -> float:
        """Assess data quality based on sensor readings."""
        quality_score = 1.0
        
        # Check for missing values
        required_fields = self._get_required_fields(config.sensor_type)
        for field in required_fields:
            if field not in raw_data:
                quality_score -= 0.2
        
        # Check for out-of-range values
        for field, value in raw_data.items():
            if isinstance(value, (int, float)):
                if value < 0 and field not in ["wind_direction", "heading"]:  # Some fields can be negative
                    quality_score -= 0.1
                elif value > 1000:  # Unreasonably high values
                    quality_score -= 0.1
        
        return max(0.0, min(1.0, quality_score))
    
    def _get_required_fields(self, sensor_type: SensorType) -> List[str]:
        """Get required fields for sensor type."""
        field_mapping = {
            SensorType.FLOW_METER: ["flow_rate", "total_volume"],
            SensorType.PRESSURE_SENSOR: ["pressure"],
            SensorType.SPEED_SENSOR: ["speed"],
            SensorType.WEATHER_STATION: ["temperature", "humidity", "wind_speed"],
            SensorType.SOIL_MOISTURE_SENSOR: ["moisture"],
            SensorType.GPS_SENSOR: ["latitude", "longitude"],
            SensorType.CAMERA_SENSOR: ["image_url"]
        }
        
        return field_mapping.get(sensor_type, [])
    
    async def _cleanup_old_data(self, sensor_id: str, retention_hours: int):
        """Clean up old sensor data."""
        cutoff_time = datetime.now() - timedelta(hours=retention_hours)
        
        if sensor_id in self.sensor_data_cache:
            self.sensor_data_cache[sensor_id] = [
                data for data in self.sensor_data_cache[sensor_id]
                if data.timestamp > cutoff_time
            ]
    
    # Public API methods
    
    async def get_sensor_data(
        self, 
        sensor_id: str, 
        minutes: int = 60
    ) -> List[SensorData]:
        """Get sensor data for specified time period."""
        if sensor_id not in self.sensor_data_cache:
            return []
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        return [
            data for data in self.sensor_data_cache[sensor_id]
            if data.timestamp > cutoff_time
        ]
    
    async def get_latest_sensor_data(self, sensor_id: str) -> Optional[SensorData]:
        """Get latest sensor data."""
        if sensor_id not in self.sensor_data_cache or not self.sensor_data_cache[sensor_id]:
            return None
        
        return self.sensor_data_cache[sensor_id][-1]
    
    async def get_sensor_health(self, sensor_id: str) -> Optional[SensorHealth]:
        """Get sensor health status."""
        if sensor_id not in self.sensor_connectors:
            return None
        
        return self.sensor_connectors[sensor_id].get_health_status()
    
    async def get_all_sensor_health(self) -> Dict[str, SensorHealth]:
        """Get health status for all sensors."""
        health_status = {}
        
        for sensor_id, connector in self.sensor_connectors.items():
            health_status[sensor_id] = connector.get_health_status()
        
        return health_status
    
    async def send_sensor_command(
        self, 
        sensor_id: str, 
        command: str, 
        params: Dict[str, Any]
    ) -> bool:
        """Send command to sensor."""
        if sensor_id not in self.sensor_connectors:
            return False
        
        return await self.sensor_connectors[sensor_id].send_command(command, params)
    
    async def calibrate_sensor(self, sensor_id: str, calibration_data: Dict[str, Any]) -> bool:
        """Calibrate sensor."""
        if sensor_id not in self.sensor_configs:
            return False
        
        # Update calibration data
        self.sensor_configs[sensor_id].calibration_data.update(calibration_data)
        
        # Send calibration command to sensor
        success = await self.send_sensor_command(sensor_id, "calibrate", calibration_data)
        
        if success:
            logger.info(f"Sensor {sensor_id} calibrated successfully")
        else:
            logger.error(f"Failed to calibrate sensor {sensor_id}")
        
        return success
    
    async def get_sensor_status(self) -> Dict[str, Any]:
        """Get overall sensor service status."""
        total_sensors = len(self.sensor_connectors)
        online_sensors = len([c for c in self.sensor_connectors.values() if c.status == SensorStatus.ONLINE])
        error_sensors = len([c for c in self.sensor_connectors.values() if c.status == SensorStatus.ERROR])
        
        return {
            "service_running": self.is_running,
            "total_sensors": total_sensors,
            "online_sensors": online_sensors,
            "error_sensors": error_sensors,
            "active_tasks": len(self.data_collection_tasks),
            "sensor_types": list(set(config.sensor_type.value for config in self.sensor_configs.values())),
            "last_update": datetime.now().isoformat()
        }
    
    async def aggregate_sensor_data(
        self, 
        equipment_id: str, 
        sensor_types: List[SensorType],
        minutes: int = 5
    ) -> Dict[str, Any]:
        """Aggregate sensor data for equipment and sensor types."""
        aggregated_data = {}
        
        for sensor_id, config in self.sensor_configs.items():
            if config.equipment_id != equipment_id:
                continue
            
            if config.sensor_type not in sensor_types:
                continue
            
            # Get recent data
            recent_data = await self.get_sensor_data(sensor_id, minutes)
            
            if recent_data:
                # Aggregate readings
                all_readings = {}
                for data in recent_data:
                    for key, value in data.readings.items():
                        if key not in all_readings:
                            all_readings[key] = []
                        all_readings[key].append(value)
                
                # Calculate statistics
                sensor_stats = {}
                for key, values in all_readings.items():
                    if values:
                        sensor_stats[key] = {
                            "latest": values[-1],
                            "average": sum(values) / len(values),
                            "min": min(values),
                            "max": max(values),
                            "count": len(values)
                        }
                
                aggregated_data[sensor_id] = {
                    "sensor_type": config.sensor_type.value,
                    "data_quality": recent_data[-1].data_quality,
                    "statistics": sensor_stats,
                    "last_update": recent_data[-1].timestamp.isoformat()
                }
        
        return aggregated_data