"""
Models for intelligent price optimization alerts system.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from uuid import UUID
from enum import Enum

from .price_models import FertilizerType, FertilizerProduct


class AlertType(str, Enum):
    """Types of price optimization alerts."""
    PRICE_THRESHOLD = "price_threshold"
    OPPORTUNITY = "opportunity"
    RISK = "risk"
    TIMING = "timing"
    VOLATILITY = "volatility"
    TREND_REVERSAL = "trend_reversal"
    MARKET_SHOCK = "market_shock"


class AlertPriority(str, Enum):
    """Alert priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertChannel(str, Enum):
    """Alert delivery channels."""
    EMAIL = "email"
    SMS = "sms"
    APP_NOTIFICATION = "app_notification"
    WEBHOOK = "webhook"
    DASHBOARD = "dashboard"


class AlertStatus(str, Enum):
    """Alert status."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    DISMISSED = "dismissed"
    EXPIRED = "expired"
    RESOLVED = "resolved"


class AlertThresholdConfig(BaseModel):
    """Configuration for alert thresholds."""
    
    fertilizer_type: FertilizerType = Field(..., description="Type of fertilizer")
    price_change_percent: float = Field(5.0, ge=0.1, le=50.0, description="Price change threshold percentage")
    volatility_threshold: float = Field(15.0, ge=1.0, le=100.0, description="Volatility threshold percentage")
    trend_strength_threshold: float = Field(0.7, ge=0.1, le=1.0, description="Trend strength threshold")
    opportunity_threshold: float = Field(10.0, ge=1.0, le=50.0, description="Opportunity detection threshold")
    risk_threshold: float = Field(20.0, ge=1.0, le=100.0, description="Risk assessment threshold")
    timing_threshold_days: int = Field(7, ge=1, le=30, description="Timing threshold in days")
    
    @validator('price_change_percent')
    def validate_price_change_percent(cls, v):
        if v <= 0:
            raise ValueError('Price change percent must be positive')
        return v


class UserAlertPreferences(BaseModel):
    """User preferences for alerts."""
    
    user_id: str = Field(..., description="User identifier")
    enabled_alert_types: List[AlertType] = Field(default_factory=list, description="Enabled alert types")
    enabled_channels: List[AlertChannel] = Field(default_factory=list, description="Enabled delivery channels")
    alert_thresholds: Dict[str, AlertThresholdConfig] = Field(default_factory=dict, description="Alert thresholds by fertilizer type")
    notification_settings: Dict[str, Any] = Field(default_factory=dict, description="Notification settings")
    quiet_hours: Optional[Dict[str, str]] = Field(None, description="Quiet hours (start_time, end_time)")
    max_alerts_per_day: int = Field(10, ge=1, le=100, description="Maximum alerts per day")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class IntelligentAlert(BaseModel):
    """Intelligent price optimization alert."""
    
    alert_id: str = Field(..., description="Unique alert identifier")
    user_id: str = Field(..., description="User identifier")
    alert_type: AlertType = Field(..., description="Type of alert")
    priority: AlertPriority = Field(..., description="Alert priority")
    status: AlertStatus = Field(default=AlertStatus.ACTIVE, description="Alert status")
    
    # Alert content
    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Alert message")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional alert details")
    
    # ML analysis
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="ML confidence score")
    pattern_analysis: Dict[str, Any] = Field(default_factory=dict, description="Pattern analysis results")
    ml_model_used: str = Field(..., description="ML model used for analysis")
    
    # Action requirements
    requires_action: bool = Field(default=True, description="Whether action is required")
    action_deadline: Optional[datetime] = Field(None, description="Action deadline")
    recommended_actions: List[str] = Field(default_factory=list, description="Recommended actions")
    
    # Delivery
    channels_sent: List[AlertChannel] = Field(default_factory=list, description="Channels alert was sent to")
    delivery_status: Dict[str, str] = Field(default_factory=dict, description="Delivery status by channel")
    
    # User interaction
    acknowledged: bool = Field(default=False, description="Whether alert was acknowledged")
    acknowledged_at: Optional[datetime] = Field(None, description="Acknowledgment timestamp")
    user_response: Optional[str] = Field(None, description="User response to alert")
    dismissed: bool = Field(default=False, description="Whether alert was dismissed")
    dismissed_at: Optional[datetime] = Field(None, description="Dismissal timestamp")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Alert expiration time")
    resolved_at: Optional[datetime] = Field(None, description="Resolution timestamp")


class AlertCreationRequest(BaseModel):
    """Request to create an intelligent alert."""
    
    user_id: str = Field(..., description="User identifier")
    fertilizer_type: FertilizerType = Field(..., description="Type of fertilizer")
    alert_type: AlertType = Field(..., description="Type of alert to create")
    user_preferences: Optional[UserAlertPreferences] = Field(None, description="User preferences")
    monitoring_duration_hours: int = Field(24, ge=1, le=168, description="Monitoring duration in hours")
    custom_thresholds: Optional[AlertThresholdConfig] = Field(None, description="Custom thresholds")


class AlertCreationResponse(BaseModel):
    """Response from alert creation."""
    
    request_id: str = Field(..., description="Request identifier")
    alerts_created: int = Field(..., description="Number of alerts created")
    alerts: List[IntelligentAlert] = Field(default_factory=list, description="Created alerts")
    monitoring_session_id: str = Field(..., description="Monitoring session identifier")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    success: bool = Field(..., description="Whether request was successful")
    message: str = Field(..., description="Response message")


class AlertMonitoringSession(BaseModel):
    """Alert monitoring session."""
    
    session_id: str = Field(..., description="Session identifier")
    user_id: str = Field(..., description="User identifier")
    fertilizer_types: List[FertilizerType] = Field(..., description="Monitored fertilizer types")
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = Field(None, description="Session end time")
    duration_hours: int = Field(..., description="Session duration in hours")
    status: str = Field("active", description="Session status")
    alerts_generated: int = Field(0, description="Number of alerts generated")
    preferences: UserAlertPreferences = Field(..., description="User preferences")


class AlertStatistics(BaseModel):
    """Alert statistics for a user."""
    
    user_id: str = Field(..., description="User identifier")
    total_alerts: int = Field(0, description="Total alerts generated")
    false_positive_rate: float = Field(0.0, ge=0.0, le=1.0, description="False positive rate")
    response_rate: float = Field(0.0, ge=0.0, le=1.0, description="User response rate")
    average_response_time_hours: float = Field(0.0, description="Average response time in hours")
    alert_types: Dict[str, int] = Field(default_factory=dict, description="Count by alert type")
    priority_distribution: Dict[str, int] = Field(default_factory=dict, description="Count by priority")
    channel_effectiveness: Dict[str, float] = Field(default_factory=dict, description="Effectiveness by channel")
    period_start: datetime = Field(..., description="Statistics period start")
    period_end: datetime = Field(..., description="Statistics period end")


class MLModelPerformance(BaseModel):
    """ML model performance metrics."""
    
    model_id: str = Field(..., description="Model identifier")
    model_type: str = Field(..., description="Type of model")
    accuracy_score: float = Field(..., ge=0.0, le=1.0, description="Model accuracy")
    false_positive_rate: float = Field(..., ge=0.0, le=1.0, description="False positive rate")
    false_negative_rate: float = Field(..., ge=0.0, le=1.0, description="False negative rate")
    precision: float = Field(..., ge=0.0, le=1.0, description="Precision score")
    recall: float = Field(..., ge=0.0, le=1.0, description="Recall score")
    f1_score: float = Field(..., ge=0.0, le=1.0, description="F1 score")
    last_trained: datetime = Field(..., description="Last training timestamp")
    training_samples: int = Field(..., description="Number of training samples")
    features_used: List[str] = Field(default_factory=list, description="Features used in model")


class AlertOptimizationRequest(BaseModel):
    """Request to optimize alert settings."""
    
    user_id: str = Field(..., description="User identifier")
    optimization_goal: str = Field(..., description="Optimization goal (reduce_false_positives, increase_response_rate, etc.)")
    historical_period_days: int = Field(30, ge=7, le=365, description="Historical period for optimization")
    target_metrics: Dict[str, float] = Field(default_factory=dict, description="Target metrics")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Optimization constraints")


class AlertOptimizationResponse(BaseModel):
    """Response from alert optimization."""
    
    optimization_id: str = Field(..., description="Optimization identifier")
    user_id: str = Field(..., description="User identifier")
    optimized_preferences: UserAlertPreferences = Field(..., description="Optimized preferences")
    performance_improvement: Dict[str, float] = Field(default_factory=dict, description="Performance improvements")
    recommendations: List[str] = Field(default_factory=list, description="Optimization recommendations")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Optimization confidence")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class AlertDeliveryRequest(BaseModel):
    """Request to deliver alerts."""
    
    alert_id: str = Field(..., description="Alert identifier")
    channels: List[AlertChannel] = Field(..., description="Delivery channels")
    priority_override: Optional[AlertPriority] = Field(None, description="Priority override")
    custom_message: Optional[str] = Field(None, description="Custom message")
    delivery_time: Optional[datetime] = Field(None, description="Scheduled delivery time")


class AlertDeliveryResponse(BaseModel):
    """Response from alert delivery."""
    
    delivery_id: str = Field(..., description="Delivery identifier")
    alert_id: str = Field(..., description="Alert identifier")
    channels_sent: List[AlertChannel] = Field(default_factory=list, description="Channels successfully sent")
    delivery_status: Dict[str, str] = Field(default_factory=dict, description="Status by channel")
    delivery_time: datetime = Field(default_factory=datetime.utcnow)
    success: bool = Field(..., description="Whether delivery was successful")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class AlertFeedback(BaseModel):
    """User feedback on alerts."""
    
    alert_id: str = Field(..., description="Alert identifier")
    user_id: str = Field(..., description="User identifier")
    feedback_type: str = Field(..., description="Type of feedback (helpful, not_helpful, false_positive, etc.)")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating 1-5")
    comments: Optional[str] = Field(None, description="Additional comments")
    action_taken: Optional[str] = Field(None, description="Action taken based on alert")
    outcome: Optional[str] = Field(None, description="Outcome of action")
    submitted_at: datetime = Field(default_factory=datetime.utcnow)


class AlertBatchRequest(BaseModel):
    """Request to process multiple alerts."""
    
    user_id: str = Field(..., description="User identifier")
    fertilizer_types: List[FertilizerType] = Field(..., description="Fertilizer types to monitor")
    alert_types: List[AlertType] = Field(default_factory=list, description="Specific alert types to check")
    batch_size: int = Field(10, ge=1, le=100, description="Maximum alerts per batch")
    monitoring_duration_hours: int = Field(24, ge=1, le=168, description="Monitoring duration")


class AlertBatchResponse(BaseModel):
    """Response from batch alert processing."""
    
    batch_id: str = Field(..., description="Batch identifier")
    user_id: str = Field(..., description="User identifier")
    alerts_generated: int = Field(..., description="Number of alerts generated")
    alerts: List[IntelligentAlert] = Field(default_factory=list, description="Generated alerts")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    success: bool = Field(..., description="Whether batch processing was successful")
    errors: List[str] = Field(default_factory=list, description="Any errors encountered")


class MobilePriceAlert(BaseModel):
    """Mobile-optimized price alert payload."""
    
    alert_id: str = Field(..., description="Unique alert identifier")
    user_id: str = Field(..., description="User identifier")
    fertilizer_type: FertilizerType = Field(..., description="Fertilizer type for the alert")
    alert_type: AlertType = Field(..., description="Alert trigger type")
    priority: AlertPriority = Field(..., description="Alert urgency level")
    
    title: str = Field(..., description="Alert title for display")
    summary: str = Field(..., description="Concise alert summary message")
    details: Dict[str, Any] = Field(default_factory=dict, description="Detailed alert context")
    
    price_per_unit: Optional[float] = Field(None, description="Current price per unit")
    price_unit: Optional[str] = Field(None, description="Unit for the price information")
    price_change_percent: Optional[float] = Field(None, description="Price change percentage compared to baseline")
    region: str = Field(..., description="Region the alert applies to")
    
    confidence_score: float = Field(0.0, ge=0.0, le=1.0, description="Alert confidence score")
    recommended_actions: List[str] = Field(default_factory=list, description="Suggested actions for the user")
    notification_channel: AlertChannel = Field(AlertChannel.APP_NOTIFICATION, description="Recommended delivery channel")
    
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Alert creation timestamp")
    action_deadline: Optional[datetime] = Field(None, description="Suggested deadline for acting on the alert")
    requires_action: bool = Field(default=True, description="Whether the alert requires user action")


class MobilePriceAlertRequest(BaseModel):
    """Mobile alert request parameters with location context."""
    
    user_id: str = Field(..., description="User requesting alerts")
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, description="Latitude for location-based alerts")
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, description="Longitude for location-based alerts")
    location_accuracy: Optional[float] = Field(None, ge=0.0, description="Location accuracy in meters")
    region: Optional[str] = Field(None, description="Fallback region identifier")
    
    fertilizer_types: List[FertilizerType] = Field(default_factory=list, description="Target fertilizer types")
    alert_types: List[AlertType] = Field(default_factory=list, description="Alert types to evaluate")
    max_alerts: int = Field(5, ge=1, le=20, description="Maximum number of alerts to return")
    history_days: int = Field(30, ge=7, le=120, description="Historical window in days")
    
    user_preferences: Optional[UserAlertPreferences] = Field(None, description="User alert preferences")
    delivery_channel: AlertChannel = Field(AlertChannel.APP_NOTIFICATION, description="Preferred delivery channel")
    include_price_details: bool = Field(True, description="Include price information in alert response")
    include_recommendations: bool = Field(True, description="Include recommendation messages")


class MobilePriceAlertResponse(BaseModel):
    """Response payload for mobile alert requests."""
    
    user_id: str = Field(..., description="User identifier")
    region: str = Field(..., description="Resolved region for the alerts")
    alerts: List[MobilePriceAlert] = Field(default_factory=list, description="Generated mobile alerts")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Response generation timestamp")
    fallback_used: bool = Field(False, description="Indicates if fallback data was required")
    insights: Dict[str, Any] = Field(default_factory=dict, description="Aggregated insight data")
    recommendations: List[str] = Field(default_factory=list, description="High-level recommendations for the user")
