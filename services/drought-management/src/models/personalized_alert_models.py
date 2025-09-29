"""
Personalized Alert and Response Models

Pydantic models for personalized drought alert configuration,
automated response recommendations, and emergency protocols.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date, timedelta
from uuid import UUID
from decimal import Decimal
from enum import Enum

class AlertSeverity(str, Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AlertType(str, Enum):
    """Types of drought alerts."""
    DROUGHT_ONSET = "drought_onset"
    SEVERITY_ESCALATION = "severity_escalation"
    SOIL_MOISTURE_CRITICAL = "soil_moisture_critical"
    CROP_STRESS = "crop_stress"
    WATER_SHORTAGE = "water_shortage"
    IRRIGATION_EFFICIENCY = "irrigation_efficiency"
    CONSERVATION_OPPORTUNITY = "conservation_opportunity"
    RECOVERY_NOTIFICATION = "recovery_notification"

class NotificationChannel(str, Enum):
    """Notification delivery channels."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    DASHBOARD = "dashboard"

class ResponseActionType(str, Enum):
    """Types of automated response actions."""
    IRRIGATION_ADJUSTMENT = "irrigation_adjustment"
    CONSERVATION_PRACTICE = "conservation_practice"
    CROP_MANAGEMENT = "crop_management"
    WATER_SOURCE_ACTIVATION = "water_source_activation"
    EMERGENCY_PROTOCOL = "emergency_protocol"
    RESOURCE_MOBILIZATION = "resource_mobilization"

class EmergencyProtocolType(str, Enum):
    """Types of emergency protocols."""
    WATER_RESTRICTION = "water_restriction"
    CROP_ABANDONMENT = "crop_abandonment"
    EMERGENCY_IRRIGATION = "emergency_irrigation"
    DISASTER_ASSISTANCE = "disaster_assistance"
    RESOURCE_SHARING = "resource_sharing"

class PersonalizedAlertThreshold(BaseModel):
    """Personalized alert threshold configuration."""
    threshold_id: UUID = Field(..., description="Unique threshold identifier")
    alert_type: AlertType = Field(..., description="Type of alert")
    metric_name: str = Field(..., description="Metric being monitored")
    threshold_value: float = Field(..., description="Threshold value")
    comparison_operator: str = Field(..., description="Comparison operator (>, <, >=, <=, ==)")
    severity_level: AlertSeverity = Field(..., description="Severity when threshold is exceeded")
    enabled: bool = Field(default=True, description="Whether threshold is active")
    crop_specific: Optional[str] = Field(None, description="Specific crop this applies to")
    growth_stage_specific: Optional[str] = Field(None, description="Specific growth stage")
    
    @field_validator('comparison_operator')
    @classmethod
    def validate_operator(cls, v):
        valid_operators = ['>', '<', '>=', '<=', '==', '!=']
        if v not in valid_operators:
            raise ValueError(f'Comparison operator must be one of: {valid_operators}')
        return v

class NotificationPreference(BaseModel):
    """Notification delivery preferences."""
    channel: NotificationChannel = Field(..., description="Notification channel")
    enabled: bool = Field(default=True, description="Whether channel is enabled")
    severity_levels: List[AlertSeverity] = Field(..., description="Severity levels for this channel")
    frequency_limit: Optional[int] = Field(None, description="Maximum notifications per hour")
    quiet_hours_start: Optional[str] = Field(None, description="Quiet hours start time (HH:MM)")
    quiet_hours_end: Optional[str] = Field(None, description="Quiet hours end time (HH:MM)")
    escalation_delay_minutes: int = Field(default=30, description="Minutes before escalation")

class PersonalizedAlertConfig(BaseModel):
    """Personalized alert configuration for a farm."""
    config_id: UUID = Field(..., description="Unique configuration identifier")
    farm_id: UUID = Field(..., description="Farm identifier")
    user_id: UUID = Field(..., description="User identifier")
    thresholds: List[PersonalizedAlertThreshold] = Field(..., description="Alert thresholds")
    notification_preferences: List[NotificationPreference] = Field(..., description="Notification preferences")
    crop_types: List[str] = Field(..., description="Crop types for this farm")
    current_practices: List[str] = Field(default_factory=list, description="Current conservation practices")
    irrigation_system_type: Optional[str] = Field(None, description="Type of irrigation system")
    water_source_types: List[str] = Field(default_factory=list, description="Available water sources")
    emergency_contacts: List[Dict[str, str]] = Field(default_factory=list, description="Emergency contact information")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True, description="Whether configuration is active")

class AutomatedResponseRecommendation(BaseModel):
    """Automated response recommendation."""
    recommendation_id: UUID = Field(..., description="Unique recommendation identifier")
    alert_id: UUID = Field(..., description="Associated alert identifier")
    action_type: ResponseActionType = Field(..., description="Type of response action")
    action_name: str = Field(..., description="Name of the action")
    description: str = Field(..., description="Detailed description of the action")
    priority: int = Field(..., ge=1, le=5, description="Priority level (1=highest, 5=lowest)")
    estimated_cost: Optional[Decimal] = Field(None, description="Estimated cost of action")
    estimated_effectiveness: float = Field(..., ge=0, le=1, description="Estimated effectiveness (0-1)")
    implementation_time_hours: int = Field(..., ge=0, description="Hours required for implementation")
    required_resources: List[str] = Field(default_factory=list, description="Required resources")
    prerequisites: List[str] = Field(default_factory=list, description="Prerequisites for action")
    expected_outcome: str = Field(..., description="Expected outcome of the action")
    risk_assessment: str = Field(..., description="Risk assessment for the action")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EmergencyProtocol(BaseModel):
    """Emergency protocol definition."""
    protocol_id: UUID = Field(..., description="Unique protocol identifier")
    protocol_type: EmergencyProtocolType = Field(..., description="Type of emergency protocol")
    name: str = Field(..., description="Protocol name")
    description: str = Field(..., description="Detailed protocol description")
    trigger_conditions: List[Dict[str, Any]] = Field(..., description="Conditions that trigger this protocol")
    activation_threshold: AlertSeverity = Field(..., description="Minimum severity to activate")
    steps: List[Dict[str, Any]] = Field(..., description="Step-by-step protocol instructions")
    required_authorizations: List[str] = Field(default_factory=list, description="Required authorizations")
    estimated_duration_hours: int = Field(..., ge=0, description="Estimated duration in hours")
    resource_requirements: List[str] = Field(default_factory=list, description="Resource requirements")
    contact_information: List[Dict[str, str]] = Field(default_factory=list, description="Contact information")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PersonalizedAlert(BaseModel):
    """Personalized drought alert."""
    alert_id: UUID = Field(..., description="Unique alert identifier")
    farm_id: UUID = Field(..., description="Farm identifier")
    user_id: UUID = Field(..., description="User identifier")
    alert_type: AlertType = Field(..., description="Type of alert")
    severity: AlertSeverity = Field(..., description="Alert severity")
    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Alert message")
    triggered_threshold: PersonalizedAlertThreshold = Field(..., description="Threshold that was exceeded")
    current_metrics: Dict[str, Any] = Field(..., description="Current metric values")
    historical_context: Dict[str, Any] = Field(default_factory=dict, description="Historical context")
    crop_impact_assessment: Dict[str, Any] = Field(default_factory=dict, description="Crop impact assessment")
    automated_responses: List[AutomatedResponseRecommendation] = Field(default_factory=list, description="Automated response recommendations")
    emergency_protocols: List[EmergencyProtocol] = Field(default_factory=list, description="Applicable emergency protocols")
    notification_channels: List[NotificationChannel] = Field(..., description="Channels used for notification")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = Field(None, description="When alert was acknowledged")
    resolved_at: Optional[datetime] = Field(None, description="When alert was resolved")

class ResponseTracking(BaseModel):
    """Response action tracking."""
    tracking_id: UUID = Field(..., description="Unique tracking identifier")
    alert_id: UUID = Field(..., description="Associated alert identifier")
    recommendation_id: UUID = Field(..., description="Associated recommendation identifier")
    action_taken: str = Field(..., description="Action that was taken")
    action_type: ResponseActionType = Field(..., description="Type of action taken")
    implementation_status: str = Field(..., description="Implementation status")
    start_time: Optional[datetime] = Field(None, description="When action was started")
    completion_time: Optional[datetime] = Field(None, description="When action was completed")
    actual_cost: Optional[Decimal] = Field(None, description="Actual cost incurred")
    effectiveness_rating: Optional[float] = Field(None, ge=0, le=10, description="User rating of effectiveness")
    notes: Optional[str] = Field(None, description="Additional notes")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ResourceMobilization(BaseModel):
    """Resource mobilization for emergency response."""
    mobilization_id: UUID = Field(..., description="Unique mobilization identifier")
    alert_id: UUID = Field(..., description="Associated alert identifier")
    resource_type: str = Field(..., description="Type of resource")
    resource_name: str = Field(..., description="Name of the resource")
    quantity_needed: float = Field(..., description="Quantity needed")
    unit: str = Field(..., description="Unit of measurement")
    urgency_level: AlertSeverity = Field(..., description="Urgency level")
    source_location: str = Field(..., description="Source location")
    destination_location: str = Field(..., description="Destination location")
    estimated_arrival_time: Optional[datetime] = Field(None, description="Estimated arrival time")
    contact_information: Dict[str, str] = Field(..., description="Contact information")
    status: str = Field(default="requested", description="Mobilization status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AlertConfigurationRequest(BaseModel):
    """Request model for configuring personalized alerts."""
    farm_id: UUID = Field(..., description="Farm identifier")
    crop_types: List[str] = Field(..., description="Crop types")
    current_practices: List[str] = Field(default_factory=list, description="Current conservation practices")
    irrigation_system_type: Optional[str] = Field(None, description="Irrigation system type")
    water_source_types: List[str] = Field(default_factory=list, description="Water source types")
    notification_preferences: List[NotificationPreference] = Field(..., description="Notification preferences")
    emergency_contacts: List[Dict[str, str]] = Field(default_factory=list, description="Emergency contacts")
    custom_thresholds: Optional[List[PersonalizedAlertThreshold]] = Field(None, description="Custom thresholds")

class AlertConfigurationResponse(BaseModel):
    """Response model for alert configuration."""
    config_id: UUID = Field(..., description="Configuration identifier")
    farm_id: UUID = Field(..., description="Farm identifier")
    configured_thresholds: List[PersonalizedAlertThreshold] = Field(..., description="Configured thresholds")
    notification_preferences: List[NotificationPreference] = Field(..., description="Notification preferences")
    emergency_protocols: List[EmergencyProtocol] = Field(..., description="Applicable emergency protocols")
    configuration_summary: Dict[str, Any] = Field(..., description="Configuration summary")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AlertHistoryResponse(BaseModel):
    """Response model for alert history."""
    alerts: List[PersonalizedAlert] = Field(..., description="List of alerts")
    total_count: int = Field(..., description="Total number of alerts")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")
    has_next: bool = Field(..., description="Whether there are more pages")

class ResponseEffectivenessReport(BaseModel):
    """Response effectiveness report."""
    report_id: UUID = Field(..., description="Unique report identifier")
    farm_id: UUID = Field(..., description="Farm identifier")
    report_period_start: date = Field(..., description="Report period start date")
    report_period_end: date = Field(..., description="Report period end date")
    total_alerts: int = Field(..., description="Total number of alerts")
    alerts_with_responses: int = Field(..., description="Alerts with responses")
    average_response_time_hours: float = Field(..., description="Average response time in hours")
    average_effectiveness_rating: float = Field(..., description="Average effectiveness rating")
    total_cost_incurred: Decimal = Field(..., description="Total cost incurred")
    cost_savings_achieved: Decimal = Field(..., description="Cost savings achieved")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for improvement")
    created_at: datetime = Field(default_factory=datetime.utcnow)