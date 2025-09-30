"""
Pydantic models for dynamic price adjustment system.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
from uuid import UUID

from .price_models import FertilizerType, FertilizerProduct, PriceSource


class AdjustmentStrategy(str, Enum):
    """Types of adjustment strategies."""
    CONSERVATIVE = "conservative"
    AGGRESSIVE = "aggressive"
    BALANCED = "balanced"
    CUSTOM = "custom"


class NotificationMethod(str, Enum):
    """Methods for sending notifications."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class ApprovalStatus(str, Enum):
    """Status of approval workflows."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class PriceAdjustmentRequest(BaseModel):
    """Request model for dynamic price adjustment monitoring."""
    
    # Request identification
    request_id: Optional[str] = Field(None, description="Unique request identifier")
    user_id: UUID = Field(..., description="User requesting monitoring")
    
    # Monitoring parameters
    fertilizer_types: List[FertilizerType] = Field(..., description="Types of fertilizers to monitor")
    fields: List[Dict[str, Any]] = Field(..., description="Fields to monitor")
    region: str = Field(default="US", description="Geographic region")
    
    # Thresholds and triggers
    price_change_threshold: float = Field(default=5.0, ge=0.1, le=50.0, description="Price change threshold percentage")
    volatility_threshold: float = Field(default=15.0, ge=5.0, le=100.0, description="Volatility threshold percentage")
    check_interval_minutes: int = Field(default=30, ge=5, le=1440, description="Check interval in minutes")
    
    # Monitoring duration
    monitoring_duration_hours: int = Field(default=168, ge=1, le=8760, description="Monitoring duration in hours")
    
    # Adjustment settings
    auto_adjust_enabled: bool = Field(default=True, description="Enable automatic adjustments")
    adjustment_strategy: AdjustmentStrategy = Field(default=AdjustmentStrategy.BALANCED, description="Adjustment strategy")
    max_adjustment_percent: float = Field(default=20.0, ge=1.0, le=100.0, description="Maximum adjustment percentage")
    
    # Notification settings
    notification_enabled: bool = Field(default=True, description="Enable notifications")
    notification_methods: List[NotificationMethod] = Field(default=[NotificationMethod.EMAIL], description="Notification methods")
    notification_threshold: float = Field(default=10.0, ge=1.0, le=50.0, description="Notification threshold percentage")
    
    # Approval settings
    require_approval: bool = Field(default=True, description="Require approval for adjustments")
    approval_timeout_hours: int = Field(default=24, ge=1, le=168, description="Approval timeout in hours")
    
    # Additional parameters
    baseline_prices: Optional[Dict[str, float]] = Field(None, description="Baseline prices for comparison")
    custom_thresholds: Optional[Dict[str, float]] = Field(None, description="Custom thresholds by fertilizer type")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('fertilizer_types')
    @classmethod
    def validate_fertilizer_types(cls, v):
        if not v:
            raise ValueError('At least one fertilizer type must be specified')
        return v
    
    @field_validator('fields')
    @classmethod
    def validate_fields(cls, v):
        if not v:
            raise ValueError('At least one field must be specified')
        return v


class PriceThreshold(BaseModel):
    """Model for price monitoring thresholds."""
    
    fertilizer_type: FertilizerType = Field(..., description="Fertilizer type")
    price_change_percent: float = Field(..., ge=0.1, le=50.0, description="Price change threshold")
    volatility_threshold: float = Field(..., ge=5.0, le=100.0, description="Volatility threshold")
    trend_strength_threshold: float = Field(..., ge=0.1, le=1.0, description="Trend strength threshold")
    
    # Monitoring settings
    check_interval_minutes: int = Field(default=30, ge=5, le=1440, description="Check interval")
    alert_enabled: bool = Field(default=True, description="Enable alerts")
    auto_adjust_enabled: bool = Field(default=True, description="Enable auto-adjustment")
    
    # Additional thresholds
    volume_threshold: Optional[float] = Field(None, description="Volume threshold")
    seasonal_adjustment: Optional[float] = Field(None, description="Seasonal adjustment factor")


class AdjustmentAlert(BaseModel):
    """Model for price adjustment alerts."""
    
    alert_id: str = Field(..., description="Unique alert identifier")
    request_id: str = Field(..., description="Associated request ID")
    trigger_type: str = Field(..., description="Type of trigger")
    priority: str = Field(..., description="Alert priority")
    
    # Alert content
    message: str = Field(..., description="Alert message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional alert details")
    
    # Action requirements
    requires_action: bool = Field(default=True, description="Whether action is required")
    action_deadline: Optional[datetime] = Field(None, description="Action deadline")
    
    # Status tracking
    status: str = Field(default="active", description="Alert status")
    acknowledged: bool = Field(default=False, description="Whether alert was acknowledged")
    acknowledged_at: Optional[datetime] = Field(None, description="Acknowledgment timestamp")
    
    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Alert expiration time")


class EconomicImpactAnalysis(BaseModel):
    """Model for economic impact analysis."""
    
    # Cost impacts
    cost_impact_per_acre: float = Field(..., description="Cost impact per acre")
    total_cost_impact: Optional[float] = Field(None, description="Total cost impact")
    
    # ROI impacts
    roi_impact_percent: float = Field(..., description="ROI impact percentage")
    break_even_impact_percent: float = Field(..., description="Break-even impact percentage")
    
    # Yield impacts
    yield_impact_percent: float = Field(default=0.0, description="Yield impact percentage")
    yield_risk_assessment: Optional[str] = Field(None, description="Yield risk assessment")
    
    # Analysis metadata
    analysis_method: str = Field(default="standard", description="Analysis method used")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Analysis confidence score")
    data_sources_used: List[str] = Field(default_factory=list, description="Data sources used")
    
    # Timestamps
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)


class StrategyModification(BaseModel):
    """Model for strategy modifications."""
    
    modification_id: str = Field(default_factory=lambda: str(UUID()), description="Unique modification identifier")
    modification_type: str = Field(..., description="Type of modification")
    fertilizer_type: FertilizerType = Field(..., description="Affected fertilizer type")
    
    # Modification details
    adjustment_percent: float = Field(..., ge=-100.0, le=100.0, description="Adjustment percentage")
    new_rate: Optional[float] = Field(None, description="New application rate")
    reason: str = Field(..., description="Reason for modification")
    
    # Economic impact
    economic_impact: Optional[EconomicImpactAnalysis] = Field(None, description="Economic impact analysis")
    expected_roi_change: Optional[float] = Field(None, description="Expected ROI change")
    
    # Approval workflow
    requires_approval: bool = Field(default=True, description="Whether approval is required")
    approval_status: ApprovalStatus = Field(default=ApprovalStatus.PENDING, description="Approval status")
    approved_by: Optional[UUID] = Field(None, description="User who approved")
    approved_at: Optional[datetime] = Field(None, description="Approval timestamp")
    
    # Implementation
    implemented: bool = Field(default=False, description="Whether modification was implemented")
    implemented_at: Optional[datetime] = Field(None, description="Implementation timestamp")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ApprovalWorkflow(BaseModel):
    """Model for approval workflows."""
    
    workflow_id: str = Field(default_factory=lambda: str(UUID()), description="Unique workflow identifier")
    modification_id: str = Field(..., description="Associated modification ID")
    request_id: str = Field(..., description="Associated request ID")
    
    # Workflow details
    approver_id: UUID = Field(..., description="User who must approve")
    approval_type: str = Field(default="manual", description="Type of approval required")
    
    # Status tracking
    status: ApprovalStatus = Field(default=ApprovalStatus.PENDING, description="Workflow status")
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    deadline: datetime = Field(..., description="Approval deadline")
    
    # Approval details
    approved_at: Optional[datetime] = Field(None, description="Approval timestamp")
    rejection_reason: Optional[str] = Field(None, description="Rejection reason")
    comments: Optional[str] = Field(None, description="Approval comments")
    
    # Notifications
    notifications_sent: List[str] = Field(default_factory=list, description="Notifications sent")
    reminder_count: int = Field(default=0, description="Number of reminders sent")


class NotificationSettings(BaseModel):
    """Model for notification settings."""
    
    user_id: UUID = Field(..., description="User ID")
    
    # Notification methods
    email_enabled: bool = Field(default=True, description="Enable email notifications")
    sms_enabled: bool = Field(default=False, description="Enable SMS notifications")
    push_enabled: bool = Field(default=True, description="Enable push notifications")
    in_app_enabled: bool = Field(default=True, description="Enable in-app notifications")
    
    # Notification preferences
    immediate_alerts: bool = Field(default=True, description="Send immediate alerts")
    daily_summary: bool = Field(default=True, description="Send daily summary")
    weekly_report: bool = Field(default=True, description="Send weekly report")
    
    # Thresholds
    alert_threshold_percent: float = Field(default=5.0, ge=1.0, le=50.0, description="Alert threshold")
    summary_threshold_percent: float = Field(default=2.0, ge=0.1, le=20.0, description="Summary threshold")
    
    # Contact information
    email_address: Optional[str] = Field(None, description="Email address")
    phone_number: Optional[str] = Field(None, description="Phone number")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PriceAdjustmentResponse(BaseModel):
    """Response model for price adjustment operations."""
    
    request_id: str = Field(..., description="Request identifier")
    success: bool = Field(..., description="Whether operation was successful")
    
    # Monitoring status
    monitoring_active: bool = Field(default=False, description="Whether monitoring is active")
    
    # Analysis results
    initial_analysis: Optional[Dict[str, Any]] = Field(None, description="Initial price analysis")
    current_analysis: Optional[Dict[str, Any]] = Field(None, description="Current price analysis")
    
    # Thresholds and triggers
    thresholds: Optional[List[PriceThreshold]] = Field(None, description="Monitoring thresholds")
    triggers_detected: Optional[List[str]] = Field(None, description="Triggers detected")
    
    # Adjustments and alerts
    adjustments_made: Optional[List[StrategyModification]] = Field(None, description="Adjustments made")
    alerts_sent: Optional[List[AdjustmentAlert]] = Field(None, description="Alerts sent")
    
    # Reports
    final_report: Optional[Dict[str, Any]] = Field(None, description="Final monitoring report")
    
    # Performance metrics
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    
    # Status messages
    message: Optional[str] = Field(None, description="Status message")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PriceAdjustmentStatus(BaseModel):
    """Model for price adjustment status."""
    
    request_id: str = Field(..., description="Request identifier")
    status: str = Field(..., description="Current status")
    
    # Session information
    start_time: datetime = Field(..., description="Session start time")
    last_check: datetime = Field(..., description="Last check time")
    uptime_seconds: float = Field(..., description="Session uptime in seconds")
    
    # Statistics
    adjustments_made: int = Field(default=0, description="Number of adjustments made")
    alerts_sent: int = Field(default=0, description="Number of alerts sent")
    checks_performed: int = Field(default=0, description="Number of checks performed")
    
    # Performance metrics
    average_check_time_ms: float = Field(default=0.0, description="Average check time")
    success_rate_percent: float = Field(default=100.0, description="Success rate percentage")
    
    # Current state
    active_thresholds: List[PriceThreshold] = Field(default_factory=list, description="Active thresholds")
    pending_approvals: List[ApprovalWorkflow] = Field(default_factory=list, description="Pending approvals")
    
    # Timestamps
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class PriceAdjustmentHistory(BaseModel):
    """Model for price adjustment history."""
    
    history_id: str = Field(default_factory=lambda: str(UUID()), description="Unique history identifier")
    request_id: str = Field(..., description="Associated request ID")
    
    # Event details
    event_type: str = Field(..., description="Type of event")
    event_description: str = Field(..., description="Event description")
    
    # Data
    event_data: Dict[str, Any] = Field(default_factory=dict, description="Event data")
    
    # Impact
    price_impact: Optional[float] = Field(None, description="Price impact")
    economic_impact: Optional[EconomicImpactAnalysis] = Field(None, description="Economic impact")
    
    # Timestamps
    event_timestamp: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PriceAdjustmentConfiguration(BaseModel):
    """Model for price adjustment configuration."""
    
    config_id: str = Field(default_factory=lambda: str(UUID()), description="Unique configuration identifier")
    user_id: UUID = Field(..., description="User ID")
    
    # Default settings
    default_price_threshold: float = Field(default=5.0, description="Default price threshold")
    default_volatility_threshold: float = Field(default=15.0, description="Default volatility threshold")
    default_check_interval: int = Field(default=30, description="Default check interval in minutes")
    
    # Adjustment settings
    max_adjustment_percent: float = Field(default=20.0, description="Maximum adjustment percentage")
    auto_adjust_enabled: bool = Field(default=True, description="Enable auto-adjustment")
    require_approval: bool = Field(default=True, description="Require approval")
    
    # Notification settings
    notification_enabled: bool = Field(default=True, description="Enable notifications")
    alert_threshold: float = Field(default=10.0, description="Alert threshold")
    
    # Advanced settings
    seasonal_adjustments: Dict[str, float] = Field(default_factory=dict, description="Seasonal adjustments")
    custom_thresholds: Dict[str, Dict[str, float]] = Field(default_factory=dict, description="Custom thresholds")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)