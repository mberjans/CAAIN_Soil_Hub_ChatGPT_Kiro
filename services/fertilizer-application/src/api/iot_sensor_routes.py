"""
API routes for IoT sensor integration service.

This module provides REST API endpoints for managing IoT sensors,
collecting real-time data, monitoring sensor health, and sending commands.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta

from src.services.iot_sensor_service import (
    IoTSensorService, SensorConfiguration, SensorHealth, SensorStatus, DataQuality
)
from src.models.application_monitoring_models import SensorData, SensorType, IoTProtocol

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/iot-sensors", tags=["iot-sensors"])


# Dependency injection
async def get_iot_service() -> IoTSensorService:
    return IoTSensorService()


@router.post("/service/start")
async def start_iot_service(
    service: IoTSensorService = Depends(get_iot_service)
):
    """
    Start the IoT sensor service.
    
    This endpoint initializes the IoT sensor service and begins
    health monitoring for all registered sensors.
    
    **Response:**
    - Service start confirmation
    - Initial status
    """
    try:
        logger.info("Starting IoT sensor service")
        
        success = await service.start_service()
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to start IoT sensor service")
        
        status = await service.get_sensor_status()
        
        return {
            "service_started": success,
            "status": status,
            "message": "IoT sensor service started successfully"
        }
        
    except Exception as e:
        logger.error(f"Error starting IoT sensor service: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start IoT sensor service: {str(e)}")


@router.post("/service/stop")
async def stop_iot_service(
    service: IoTSensorService = Depends(get_iot_service)
):
    """
    Stop the IoT sensor service.
    
    This endpoint stops all sensor connections, data collection tasks,
    and health monitoring.
    
    **Response:**
    - Service stop confirmation
    - Final status
    """
    try:
        logger.info("Stopping IoT sensor service")
        
        success = await service.stop_service()
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to stop IoT sensor service")
        
        status = await service.get_sensor_status()
        
        return {
            "service_stopped": success,
            "status": status,
            "message": "IoT sensor service stopped successfully"
        }
        
    except Exception as e:
        logger.error(f"Error stopping IoT sensor service: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop IoT sensor service: {str(e)}")


@router.get("/service/status")
async def get_service_status(
    service: IoTSensorService = Depends(get_iot_service)
):
    """
    Get IoT sensor service status.
    
    Returns comprehensive status information including:
    - Service running state
    - Sensor counts and status
    - Active data collection tasks
    - Supported sensor types
    """
    try:
        status = await service.get_sensor_status()
        return status
        
    except Exception as e:
        logger.error(f"Error getting IoT service status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get service status: {str(e)}")


@router.post("/sensors/register")
async def register_sensor(
    sensor_config: Dict[str, Any],
    service: IoTSensorService = Depends(get_iot_service)
):
    """
    Register a new IoT sensor.
    
    This endpoint registers a new sensor with the IoT service and
    begins data collection.
    
    **Request Body:**
    ```json
    {
        "sensor_id": "flow_meter_001",
        "sensor_type": "flow_meter",
        "equipment_id": "equipment_456",
        "location": {
            "latitude": 40.123456,
            "longitude": -95.654321,
            "elevation": 950.0
        },
        "calibration_data": {
            "flow_factor": 1.0,
            "pressure_offset": 0.0
        },
        "update_frequency_seconds": 5,
        "data_retention_hours": 24,
        "alert_thresholds": {
            "flow_rate": 50.0,
            "pressure": 45.0
        },
        "connection_params": {
            "protocol": "mqtt",
            "broker_url": "mqtt://localhost:1883",
            "topic": "sensors/flow_meter_001",
            "username": "sensor_user",
            "password": "sensor_pass"
        }
    }
    ```
    
    **Response:**
    - Sensor registration confirmation
    - Connection status
    - Initial health status
    """
    try:
        logger.info(f"Registering sensor {sensor_config.get('sensor_id')}")
        
        # Create sensor configuration
        config = SensorConfiguration(**sensor_config)
        
        # Register sensor
        success = await service.register_sensor(config)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to register sensor")
        
        # Get initial health status
        health = await service.get_sensor_health(config.sensor_id)
        
        return {
            "sensor_id": config.sensor_id,
            "registered": success,
            "sensor_type": config.sensor_type.value,
            "equipment_id": config.equipment_id,
            "health_status": health.dict() if health else None,
            "message": "Sensor registered successfully"
        }
        
    except Exception as e:
        logger.error(f"Error registering sensor: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to register sensor: {str(e)}")


@router.post("/sensors/{sensor_id}/unregister")
async def unregister_sensor(
    sensor_id: str,
    service: IoTSensorService = Depends(get_iot_service)
):
    """
    Unregister an IoT sensor.
    
    This endpoint stops data collection, disconnects the sensor,
    and removes it from the service.
    
    **Response:**
    - Sensor unregistration confirmation
    - Final status
    """
    try:
        logger.info(f"Unregistering sensor {sensor_id}")
        
        success = await service.unregister_sensor(sensor_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to unregister sensor")
        
        return {
            "sensor_id": sensor_id,
            "unregistered": success,
            "message": "Sensor unregistered successfully"
        }
        
    except Exception as e:
        logger.error(f"Error unregistering sensor {sensor_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to unregister sensor: {str(e)}")


@router.get("/sensors/{sensor_id}/data")
async def get_sensor_data(
    sensor_id: str,
    minutes: int = Query(60, ge=1, le=1440, description="Data period in minutes"),
    service: IoTSensorService = Depends(get_iot_service)
):
    """
    Get sensor data for specified time period.
    
    Returns historical sensor data including:
    - Raw sensor readings
    - Data quality scores
    - Timestamps
    - Sensor metadata
    
    **Time Period Options:**
    - 1-60 minutes: Recent data
    - 60-240 minutes: Short-term history
    - 240-1440 minutes: Long-term history
    """
    try:
        data = await service.get_sensor_data(sensor_id, minutes)
        
        return {
            "sensor_id": sensor_id,
            "time_period_minutes": minutes,
            "data_points": len(data),
            "data": [sensor_data.dict() for sensor_data in data]
        }
        
    except Exception as e:
        logger.error(f"Error getting sensor data for {sensor_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get sensor data: {str(e)}")


@router.get("/sensors/{sensor_id}/latest")
async def get_latest_sensor_data(
    sensor_id: str,
    service: IoTSensorService = Depends(get_iot_service)
):
    """
    Get latest sensor data.
    
    Returns the most recent sensor reading including:
    - Current sensor values
    - Data quality
    - Timestamp
    - Sensor status
    """
    try:
        data = await service.get_latest_sensor_data(sensor_id)
        
        if not data:
            raise HTTPException(status_code=404, detail="No sensor data available")
        
        return data.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting latest sensor data for {sensor_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get latest sensor data: {str(e)}")


@router.get("/sensors/{sensor_id}/health")
async def get_sensor_health(
    sensor_id: str,
    service: IoTSensorService = Depends(get_iot_service)
):
    """
    Get sensor health status.
    
    Returns comprehensive health information including:
    - Connection status
    - Data quality
    - Error counts
    - Uptime percentage
    - Maintenance status
    """
    try:
        health = await service.get_sensor_health(sensor_id)
        
        if not health:
            raise HTTPException(status_code=404, detail="Sensor not found")
        
        return health.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sensor health for {sensor_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get sensor health: {str(e)}")


@router.get("/sensors/health")
async def get_all_sensor_health(
    status_filter: Optional[SensorStatus] = Query(None, description="Filter by sensor status"),
    service: IoTSensorService = Depends(get_iot_service)
):
    """
    Get health status for all sensors.
    
    Returns health information for all registered sensors with optional
    filtering by status.
    
    **Status Options:**
    - ONLINE: Sensor is connected and operational
    - OFFLINE: Sensor is disconnected
    - ERROR: Sensor has errors
    - CALIBRATING: Sensor is being calibrated
    - MAINTENANCE: Sensor requires maintenance
    """
    try:
        health_data = await service.get_all_sensor_health()
        
        # Apply status filter
        if status_filter:
            health_data = {
                sensor_id: health for sensor_id, health in health_data.items()
                if health.status == status_filter
            }
        
        return {
            "total_sensors": len(health_data),
            "health_data": {sensor_id: health.dict() for sensor_id, health in health_data.items()}
        }
        
    except Exception as e:
        logger.error(f"Error getting all sensor health: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get sensor health: {str(e)}")


@router.post("/sensors/{sensor_id}/command")
async def send_sensor_command(
    sensor_id: str,
    command_data: Dict[str, Any],
    service: IoTSensorService = Depends(get_iot_service)
):
    """
    Send command to sensor.
    
    This endpoint allows sending commands to sensors for:
    - Calibration
    - Configuration changes
    - Maintenance operations
    - Data collection control
    
    **Request Body:**
    ```json
    {
        "command": "calibrate",
        "parameters": {
            "calibration_factor": 1.05,
            "zero_offset": 0.1
        }
    }
    ```
    
    **Response:**
    - Command execution confirmation
    - Result status
    """
    try:
        command = command_data.get("command")
        params = command_data.get("parameters", {})
        
        if not command:
            raise HTTPException(status_code=400, detail="Command is required")
        
        logger.info(f"Sending command {command} to sensor {sensor_id}")
        
        success = await service.send_sensor_command(sensor_id, command, params)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to send command to sensor")
        
        return {
            "sensor_id": sensor_id,
            "command": command,
            "parameters": params,
            "executed": success,
            "timestamp": datetime.now().isoformat(),
            "message": "Command sent successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending command to sensor {sensor_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send command: {str(e)}")


@router.post("/sensors/{sensor_id}/calibrate")
async def calibrate_sensor(
    sensor_id: str,
    calibration_data: Dict[str, Any],
    service: IoTSensorService = Depends(get_iot_service)
):
    """
    Calibrate sensor.
    
    This endpoint performs sensor calibration with provided
    calibration parameters.
    
    **Request Body:**
    ```json
    {
        "flow_factor": 1.05,
        "pressure_offset": 0.1,
        "temperature_compensation": 0.02,
        "zero_point": 0.0
    }
    ```
    
    **Response:**
    - Calibration confirmation
    - Updated calibration data
    """
    try:
        logger.info(f"Calibrating sensor {sensor_id}")
        
        success = await service.calibrate_sensor(sensor_id, calibration_data)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to calibrate sensor")
        
        return {
            "sensor_id": sensor_id,
            "calibrated": success,
            "calibration_data": calibration_data,
            "timestamp": datetime.now().isoformat(),
            "message": "Sensor calibrated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error calibrating sensor {sensor_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to calibrate sensor: {str(e)}")


@router.get("/equipment/{equipment_id}/aggregated-data")
async def get_aggregated_equipment_data(
    equipment_id: str,
    sensor_types: List[SensorType] = Query(..., description="Sensor types to include"),
    minutes: int = Query(5, ge=1, le=60, description="Aggregation period in minutes"),
    service: IoTSensorService = Depends(get_iot_service)
):
    """
    Get aggregated sensor data for equipment.
    
    Returns aggregated sensor data for specified equipment and sensor types
    including statistical analysis of recent readings.
    
    **Response includes:**
    - Latest values
    - Average values
    - Min/max values
    - Data point counts
    - Data quality scores
    """
    try:
        aggregated_data = await service.aggregate_sensor_data(equipment_id, sensor_types, minutes)
        
        return {
            "equipment_id": equipment_id,
            "sensor_types": [st.value for st in sensor_types],
            "aggregation_period_minutes": minutes,
            "sensors": len(aggregated_data),
            "aggregated_data": aggregated_data
        }
        
    except Exception as e:
        logger.error(f"Error getting aggregated data for equipment {equipment_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get aggregated data: {str(e)}")


@router.get("/sensors/types")
async def get_supported_sensor_types():
    """
    Get supported sensor types.
    
    Returns list of all supported sensor types and their capabilities.
    """
    return {
        "supported_sensor_types": [
            {
                "type": "flow_meter",
                "description": "Measures liquid flow rate and volume",
                "typical_readings": ["flow_rate", "total_volume", "pressure", "temperature"],
                "protocols": ["mqtt", "modbus", "http"]
            },
            {
                "type": "pressure_sensor",
                "description": "Measures system pressure and temperature",
                "typical_readings": ["pressure", "temperature", "vibration"],
                "protocols": ["mqtt", "modbus", "http"]
            },
            {
                "type": "speed_sensor",
                "description": "Measures ground speed and distance",
                "typical_readings": ["speed", "distance", "acceleration", "direction"],
                "protocols": ["websocket", "mqtt", "http"]
            },
            {
                "type": "weather_station",
                "description": "Measures environmental conditions",
                "typical_readings": ["temperature", "humidity", "wind_speed", "wind_direction", "pressure", "precipitation", "solar_radiation"],
                "protocols": ["mqtt", "http", "websocket"]
            },
            {
                "type": "soil_moisture_sensor",
                "description": "Measures soil moisture and conditions",
                "typical_readings": ["moisture", "temperature", "conductivity", "ph"],
                "protocols": ["lora", "nb_iot", "mqtt"]
            },
            {
                "type": "gps_sensor",
                "description": "Provides location and navigation data",
                "typical_readings": ["latitude", "longitude", "elevation", "accuracy", "speed", "heading"],
                "protocols": ["mqtt", "http", "websocket"]
            },
            {
                "type": "camera_sensor",
                "description": "Captures images and performs analysis",
                "typical_readings": ["image_url", "image_quality", "detected_objects", "coverage_analysis"],
                "protocols": ["http", "websocket"]
            }
        ],
        "supported_protocols": [
            {
                "protocol": "mqtt",
                "description": "Message Queuing Telemetry Transport",
                "use_cases": ["real-time data", "low power", "reliable delivery"]
            },
            {
                "protocol": "http",
                "description": "Hypertext Transfer Protocol",
                "use_cases": ["web-based sensors", "REST APIs", "image data"]
            },
            {
                "protocol": "websocket",
                "description": "WebSocket Protocol",
                "use_cases": ["real-time communication", "bidirectional data"]
            },
            {
                "protocol": "modbus",
                "description": "Modbus Protocol",
                "use_cases": ["industrial sensors", "PLC integration"]
            },
            {
                "protocol": "lora",
                "description": "LoRaWAN Protocol",
                "use_cases": ["long-range", "low power", "outdoor sensors"]
            },
            {
                "protocol": "nb_iot",
                "description": "Narrowband IoT",
                "use_cases": ["cellular connectivity", "wide area coverage"]
            }
        ]
    }


@router.get("/health")
async def health_check():
    """Health check endpoint for IoT sensor service."""
    return {"status": "healthy", "service": "iot-sensors"}