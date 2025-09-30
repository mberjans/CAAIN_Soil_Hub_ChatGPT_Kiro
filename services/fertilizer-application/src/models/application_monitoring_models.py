"""
Data models for real-time application monitoring and adjustment.

This module defines the data structures for monitoring fertilizer application
in real-time, including application rates, coverage, weather conditions,
and adjustment recommendations.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from uuid import UUID, uuid4
import json


class ApplicationStatus(str, Enum):
    """Status of fertilizer application."""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


class AdjustmentType(str, Enum):
    """Types of real-time adjustments."""
    RATE_ADJUSTMENT = "rate_adjustment"
    TIMING_ADJUSTMENT = "timing_adjustment"
    METHOD_ADJUSTMENT = "method_adjustment"
    COVERAGE_ADJUSTMENT = "coverage_adjustment"
    WEATHER_ADJUSTMENT = "weather_adjustment"
    QUALITY_ADJUSTMENT = "quality_adjustment"


class MonitoringMetric(str, Enum):
    """Real-time monitoring metrics."""
    APPLICATION_RATE = "application_rate"
    COVERAGE_UNIFORMITY = "coverage_uniformity"
    SPEED = "speed"
    PRESSURE = "pressure"
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    WIND_SPEED = "wind_speed"
    WIND_DIRECTION = "wind_direction"
    SOIL_MOISTURE = "soil_moisture"
    EQUIPMENT_STATUS = "equipment_status"


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SensorType(str, Enum):
    """Types of IoT sensors."""
    FLOW_METER = "flow_meter"
    PRESSURE_SENSOR = "pressure_sensor"
    SPEED_SENSOR = "speed_sensor"
    WEATHER_STATION = "weather_station"
    SOIL_MOISTURE_SENSOR = "soil_moisture_sensor"
    GPS_SENSOR = "gps_sensor"
    CAMERA_SENSOR = "camera_sensor"


class IoTProtocol(str, Enum):
    """IoT communication protocols."""
    MQTT = "mqtt"
    HTTP = "http"
    WEBSOCKET = "websocket"
    MODBUS = "modbus"
    LORA = "lora"
    NB_IOT = "nb_iot"


class ApplicationMonitoringData(BaseModel):
    """Real-time application monitoring data."""
    
    monitoring_id: str = Field(default_factory=lambda: str(uuid4()))
    application_session_id: str = Field(..., description="Application session identifier")
    equipment_id: str = Field(..., description="Equipment identifier")
    field_id: str = Field(..., description="Field identifier")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Application metrics
    application_rate: float = Field(..., ge=0, description="Current application rate (lbs/acre)")
    target_rate: float = Field(..., ge=0, description="Target application rate (lbs/acre)")
    rate_deviation: float = Field(..., description="Deviation from target rate (%)")
    
    # Coverage metrics
    coverage_uniformity: float = Field(..., ge=0, le=1, description="Coverage uniformity (0-1)")
    coverage_area: float = Field(..., ge=0, description="Covered area (acres)")
    overlap_percentage: float = Field(..., ge=0, le=100, description="Overlap percentage")
    
    # Equipment metrics
    speed: float = Field(..., ge=0, description="Ground speed (mph)")
    pressure: float = Field(..., ge=0, description="System pressure (psi)")
    nozzle_status: Dict[str, bool] = Field(default_factory=dict, description="Nozzle status by position")
    
    # Environmental conditions
    temperature: float = Field(..., description="Air temperature (°F)")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity (%)")
    wind_speed: float = Field(..., ge=0, description="Wind speed (mph)")
    wind_direction: float = Field(..., ge=0, le=360, description="Wind direction (degrees)")
    soil_moisture: float = Field(..., ge=0, le=100, description="Soil moisture content (%)")
    
    # Location data
    latitude: float = Field(..., ge=-90, le=90, description="GPS latitude")
    longitude: float = Field(..., ge=-180, le=180, description="GPS longitude")
    elevation: float = Field(..., description="Elevation (feet)")
    
    # Quality indicators
    quality_score: float = Field(..., ge=0, le=1, description="Overall quality score (0-1)")
    drift_potential: float = Field(..., ge=0, le=1, description="Drift potential (0-1)")
    application_efficiency: float = Field(..., ge=0, le=1, description="Application efficiency (0-1)")
    
    # Equipment status
    equipment_status: str = Field(..., description="Current equipment status")
    maintenance_alerts: List[str] = Field(default_factory=list, description="Active maintenance alerts")
    
    @validator('rate_deviation')
    def validate_rate_deviation(cls, v, values):
        """Calculate rate deviation from target and actual rates."""
        if 'application_rate' in values and 'target_rate' in values:
            target = values['target_rate']
            actual = values['application_rate']
            if target > 0:
                return ((actual - target) / target) * 100
        return v


class RealTimeAdjustment(BaseModel):
    """Real-time adjustment recommendation."""
    
    adjustment_id: str = Field(default_factory=lambda: str(uuid4()))
    monitoring_data_id: str = Field(..., description="Associated monitoring data ID")
    adjustment_type: AdjustmentType = Field(..., description="Type of adjustment")
    priority: int = Field(..., ge=1, le=5, description="Adjustment priority (1-5)")
    
    # Current vs target values
    current_value: float = Field(..., description="Current parameter value")
    target_value: float = Field(..., description="Target parameter value")
    adjustment_amount: float = Field(..., description="Required adjustment amount")
    
    # Adjustment details
    reason: str = Field(..., description="Reason for adjustment")
    impact_assessment: str = Field(..., description="Expected impact of adjustment")
    implementation_time: int = Field(..., ge=0, description="Time to implement (seconds)")
    
    # Validation
    confidence: float = Field(..., ge=0, le=1, description="Confidence in adjustment (0-1)")
    risk_level: AlertSeverity = Field(..., description="Risk level of adjustment")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = Field(None, description="Adjustment expiration time")
    implemented: bool = Field(default=False, description="Whether adjustment was implemented")
    implemented_at: Optional[datetime] = Field(None, description="Implementation timestamp")


class MonitoringAlert(BaseModel):
    """Real-time monitoring alert."""
    
    alert_id: str = Field(default_factory=lambda: str(uuid4()))
    monitoring_data_id: str = Field(..., description="Associated monitoring data ID")
    alert_type: str = Field(..., description="Type of alert")
    severity: AlertSeverity = Field(..., description="Alert severity")
    
    # Alert details
    metric: MonitoringMetric = Field(..., description="Monitored metric")
    current_value: float = Field(..., description="Current metric value")
    threshold_value: float = Field(..., description="Threshold value")
    deviation_percentage: float = Field(..., description="Deviation from threshold (%)")
    
    # Alert content
    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Alert message")
    recommendations: List[str] = Field(default_factory=list, description="Recommended actions")
    
    # Status
    acknowledged: bool = Field(default=False, description="Whether alert is acknowledged")
    resolved: bool = Field(default=False, description="Whether alert is resolved")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = Field(None, description="Acknowledgment timestamp")
    resolved_at: Optional[datetime] = Field(None, description="Resolution timestamp")


class SensorData(BaseModel):
    """IoT sensor data."""
    
    sensor_id: str = Field(..., description="Sensor identifier")
    sensor_type: SensorType = Field(..., description="Type of sensor")
    equipment_id: str = Field(..., description="Associated equipment ID")
    
    # Sensor readings
    readings: Dict[str, float] = Field(..., description="Sensor readings")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Sensor status
    status: str = Field(default="active", description="Sensor status")
    battery_level: Optional[float] = Field(None, ge=0, le=100, description="Battery level (%)")
    signal_strength: Optional[float] = Field(None, ge=0, le=100, description="Signal strength (%)")
    
    # Data quality
    data_quality: float = Field(..., ge=0, le=1, description="Data quality score (0-1)")
    calibration_status: str = Field(default="calibrated", description="Calibration status")


class ApplicationSession(BaseModel):
    """Fertilizer application session."""
    
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    field_id: str = Field(..., description="Field identifier")
    equipment_id: str = Field(..., description="Equipment identifier")
    operator_id: str = Field(..., description="Operator identifier")
    
    # Session details
    fertilizer_type: str = Field(..., description="Type of fertilizer")
    target_rate: float = Field(..., ge=0, description="Target application rate (lbs/acre)")
    application_method: str = Field(..., description="Application method")
    
    # Timing
    planned_start: datetime = Field(..., description="Planned start time")
    actual_start: Optional[datetime] = Field(None, description="Actual start time")
    planned_end: datetime = Field(..., description="Planned end time")
    actual_end: Optional[datetime] = Field(None, description="Actual end time")
    
    # Status
    status: ApplicationStatus = Field(default=ApplicationStatus.PLANNED, description="Session status")
    
    # Progress tracking
    total_area: float = Field(..., ge=0, description="Total field area (acres)")
    completed_area: float = Field(default=0, ge=0, description="Completed area (acres)")
    progress_percentage: float = Field(default=0, ge=0, le=100, description="Progress percentage")
    
    # Quality metrics
    average_rate: float = Field(default=0, ge=0, description="Average application rate")
    rate_variability: float = Field(default=0, ge=0, description="Rate variability (%)")
    coverage_score: float = Field(default=0, ge=0, le=1, description="Coverage quality score")
    
    # Adjustments and alerts
    total_adjustments: int = Field(default=0, ge=0, description="Total adjustments made")
    active_alerts: int = Field(default=0, ge=0, description="Active alerts count")
    
    # Environmental conditions
    weather_conditions: Dict[str, Any] = Field(default_factory=dict, description="Weather conditions")
    
    @validator('progress_percentage')
    def validate_progress_percentage(cls, v, values):
        """Calculate progress percentage from completed and total area."""
        if 'completed_area' in values and 'total_area' in values:
            completed = values['completed_area']
            total = values['total_area']
            if total > 0:
                return (completed / total) * 100
        return v


class QualityControlCheck(BaseModel):
    """Quality control check result."""
    
    check_id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str = Field(..., description="Application session ID")
    check_type: str = Field(..., description="Type of quality check")
    
    # Check parameters
    parameters: Dict[str, Any] = Field(..., description="Check parameters")
    thresholds: Dict[str, float] = Field(..., description="Quality thresholds")
    
    # Results
    passed: bool = Field(..., description="Whether check passed")
    score: float = Field(..., ge=0, le=1, description="Quality score (0-1)")
    deviations: List[Dict[str, Any]] = Field(default_factory=list, description="Quality deviations")
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list, description="Quality recommendations")
    corrective_actions: List[str] = Field(default_factory=list, description="Corrective actions")
    
    # Metadata
    performed_at: datetime = Field(default_factory=datetime.now)
    performed_by: str = Field(..., description="Who performed the check")


class MonitoringConfiguration(BaseModel):
    """Configuration for real-time monitoring."""
    
    session_id: str = Field(..., description="Application session ID")
    monitoring_enabled: bool = Field(default=True, description="Whether monitoring is enabled")
    
    # Monitoring parameters
    update_frequency_seconds: int = Field(default=5, ge=1, le=60, description="Update frequency")
    alert_thresholds: Dict[str, Dict[str, float]] = Field(default_factory=dict, description="Alert thresholds")
    adjustment_thresholds: Dict[str, float] = Field(default_factory=dict, description="Adjustment thresholds")
    
    # Sensor configuration
    enabled_sensors: List[SensorType] = Field(default_factory=list, description="Enabled sensor types")
    sensor_configs: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Sensor configurations")
    
    # Quality control
    quality_checks_enabled: bool = Field(default=True, description="Whether quality checks are enabled")
    quality_check_frequency: int = Field(default=300, ge=1, description="Quality check frequency (seconds)")
    
    # Notifications
    notification_methods: List[str] = Field(default_factory=list, description="Notification methods")
    notification_thresholds: Dict[str, AlertSeverity] = Field(default_factory=dict, description="Notification thresholds")


class MonitoringSummary(BaseModel):
    """Summary of monitoring session."""
    
    session_id: str = Field(..., description="Application session ID")
    monitoring_duration_minutes: float = Field(..., description="Total monitoring duration")
    
    # Data collection
    total_data_points: int = Field(..., ge=0, description="Total data points collected")
    data_quality_average: float = Field(..., ge=0, le=1, description="Average data quality")
    
    # Adjustments
    total_adjustments: int = Field(..., ge=0, description="Total adjustments made")
    successful_adjustments: int = Field(..., ge=0, description="Successful adjustments")
    adjustment_success_rate: float = Field(..., ge=0, le=1, description="Adjustment success rate")
    
    # Alerts
    total_alerts: int = Field(..., ge=0, description="Total alerts generated")
    critical_alerts: int = Field(..., ge=0, description="Critical alerts")
    resolved_alerts: int = Field(..., ge=0, description="Resolved alerts")
    
    # Quality
    average_quality_score: float = Field(..., ge=0, le=1, description="Average quality score")
    quality_checks_performed: int = Field(..., ge=0, description="Quality checks performed")
    quality_checks_passed: int = Field(..., ge=0, description="Quality checks passed")
    
    # Performance metrics
    average_rate_accuracy: float = Field(..., ge=0, le=1, description="Average rate accuracy")
    average_coverage_uniformity: float = Field(..., ge=0, le=1, description="Average coverage uniformity")
    average_application_efficiency: float = Field(..., ge=0, le=1, description="Average application efficiency")
    
    # Environmental impact
    average_drift_potential: float = Field(..., ge=0, le=1, description="Average drift potential")
    environmental_compliance_score: float = Field(..., ge=0, le=1, description="Environmental compliance score")
    
    @validator('adjustment_success_rate')
    def validate_adjustment_success_rate(cls, v, values):
        """Calculate adjustment success rate."""
        if 'total_adjustments' in values and 'successful_adjustments' in values:
            total = values['total_adjustments']
            successful = values['successful_adjustments']
            if total > 0:
                return successful / total
        return v