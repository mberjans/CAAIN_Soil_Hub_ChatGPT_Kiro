"""
Production Alerting Models

Data models for production alerting system, including alert rules,
notifications, escalation policies, and suppression rules.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID, uuid4
from decimal import Decimal
from enum import Enum

class AlertSeverity(str, Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    """Alert status options."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ESCALATED = "escalated"

class NotificationChannel(str, Enum):
    """Notification channel types."""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    PUSH = "push"

class NotificationStatus(str, Enum):
    """Notification status options."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"

class ComparisonOperator(str, Enum):
    """Comparison operators for alert conditions."""
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN_OR_EQUALS = "greater_than_or_equals"
    LESS_THAN_OR_EQUALS = "less_than_or_equals"

# Alert Rule Models
class AlertCondition(BaseModel):
    """Alert condition definition."""
    metric_name: str = Field(..., description="Name of the metric to monitor")
    operator: ComparisonOperator = Field(..., description="Comparison operator")
    threshold_value: float = Field(..., description="Threshold value for comparison")
    evaluation_window_minutes: int = Field(default=5, ge=1, description="Evaluation window in minutes")
    aggregation_function: str = Field(default="avg", description="Aggregation function (avg, max, min, sum)")

class AlertAction(BaseModel):
    """Alert action definition."""
    action_type: str = Field(..., description="Type of action to take")
    action_config: Dict[str, Any] = Field(default_factory=dict, description="Action configuration")
    delay_seconds: int = Field(default=0, ge=0, description="Delay before executing action")

class AlertRule(BaseModel):
    """Alert rule definition."""
    rule_id: str = Field(..., description="Unique rule identifier")
    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    conditions: List[AlertCondition] = Field(..., description="Alert conditions")
    severity: AlertSeverity = Field(..., description="Alert severity level")
    enabled: bool = Field(default=True, description="Whether the rule is enabled")
    cooldown_minutes: int = Field(default=15, ge=0, description="Cooldown period in minutes")
    actions: List[AlertAction] = Field(default_factory=list, description="Actions to take when alert triggers")
    tags: List[str] = Field(default_factory=list, description="Rule tags for categorization")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Rule creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Rule last update timestamp")

# Alert History Models
class AlertHistory(BaseModel):
    """Alert history record."""
    alert_id: str = Field(..., description="Unique alert identifier")
    rule_id: str = Field(..., description="Rule that triggered the alert")
    alert_name: str = Field(..., description="Alert name")
    severity: AlertSeverity = Field(..., description="Alert severity")
    status: AlertStatus = Field(..., description="Alert status")
    triggered_at: datetime = Field(..., description="When the alert was triggered")
    description: str = Field(..., description="Alert description")
    conditions_met: List[AlertCondition] = Field(..., description="Conditions that were met")
    current_values: Dict[str, float] = Field(..., description="Current metric values")
    acknowledged: bool = Field(default=False, description="Whether alert has been acknowledged")
    acknowledged_by: Optional[str] = Field(None, description="Who acknowledged the alert")
    acknowledged_at: Optional[datetime] = Field(None, description="When alert was acknowledged")
    resolved: bool = Field(default=False, description="Whether alert has been resolved")
    resolved_by: Optional[str] = Field(None, description="Who resolved the alert")
    resolved_at: Optional[datetime] = Field(None, description="When alert was resolved")
    escalation_level: int = Field(default=0, ge=0, description="Current escalation level")
    suppression_reason: Optional[str] = Field(None, description="Reason for suppression if suppressed")

# Notification Models
class AlertChannel(BaseModel):
    """Alert notification channel."""
    channel_id: str = Field(..., description="Unique channel identifier")
    channel_type: NotificationChannel = Field(..., description="Channel type")
    name: str = Field(..., description="Channel name")
    configuration: Dict[str, Any] = Field(..., description="Channel configuration")
    enabled: bool = Field(default=True, description="Whether channel is enabled")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Channel creation timestamp")

class AlertTemplate(BaseModel):
    """Alert notification template."""
    template_id: str = Field(..., description="Unique template identifier")
    name: str = Field(..., description="Template name")
    subject: str = Field(..., description="Notification subject template")
    body: str = Field(..., description="Notification body template")
    channel_type: NotificationChannel = Field(..., description="Channel type this template is for")
    variables: List[str] = Field(default_factory=list, description="Available template variables")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Template creation timestamp")

class AlertNotification(BaseModel):
    """Alert notification record."""
    notification_id: str = Field(..., description="Unique notification identifier")
    alert_id: str = Field(..., description="Associated alert ID")
    channel_id: str = Field(..., description="Notification channel ID")
    channel_type: NotificationChannel = Field(..., description="Channel type")
    subject: str = Field(..., description="Notification subject")
    body: str = Field(..., description="Notification body")
    status: NotificationStatus = Field(default=NotificationStatus.PENDING, description="Notification status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Notification creation timestamp")
    sent_at: Optional[datetime] = Field(None, description="When notification was sent")
    delivered_at: Optional[datetime] = Field(None, description="When notification was delivered")
    error_message: Optional[str] = Field(None, description="Error message if notification failed")

# Escalation Models
class EscalationPolicy(BaseModel):
    """Alert escalation policy."""
    policy_id: str = Field(..., description="Unique policy identifier")
    name: str = Field(..., description="Policy name")
    description: str = Field(..., description="Policy description")
    escalation_steps: List[Dict[str, Any]] = Field(..., description="Escalation steps")
    max_escalation_steps: int = Field(default=3, ge=1, description="Maximum escalation steps")
    enabled: bool = Field(default=True, description="Whether policy is enabled")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Policy creation timestamp")

class AlertEscalation(BaseModel):
    """Alert escalation record."""
    escalation_id: str = Field(..., description="Unique escalation identifier")
    alert_id: str = Field(..., description="Associated alert ID")
    policy_id: str = Field(..., description="Escalation policy ID")
    current_step: int = Field(default=1, ge=1, description="Current escalation step")
    max_steps: int = Field(..., ge=1, description="Maximum escalation steps")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="Escalation start time")
    completed_at: Optional[datetime] = Field(None, description="Escalation completion time")
    status: str = Field(default="active", description="Escalation status")

# Suppression Models
class SuppressionRule(BaseModel):
    """Alert suppression rule."""
    rule_id: str = Field(..., description="Unique suppression rule identifier")
    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    conditions: Dict[str, Any] = Field(..., description="Suppression conditions")
    enabled: bool = Field(default=True, description="Whether rule is enabled")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Rule creation timestamp")

class AlertSuppression(BaseModel):
    """Alert suppression record."""
    suppression_id: str = Field(..., description="Unique suppression identifier")
    alert_id: str = Field(..., description="Suppressed alert ID")
    rule_id: str = Field(..., description="Suppression rule ID")
    reason: str = Field(..., description="Suppression reason")
    suppressed_at: datetime = Field(default_factory=datetime.utcnow, description="Suppression timestamp")
    suppressed_by: str = Field(..., description="Who/what suppressed the alert")

# Metrics Models
class AlertMetrics(BaseModel):
    """Alert metrics summary."""
    total_alerts: int = Field(..., ge=0, description="Total number of alerts")
    active_alerts: int = Field(..., ge=0, description="Number of active alerts")
    acknowledged_alerts: int = Field(..., ge=0, description="Number of acknowledged alerts")
    resolved_alerts: int = Field(..., ge=0, description="Number of resolved alerts")
    severity_distribution: Dict[str, int] = Field(default_factory=dict, description="Alert count by severity")
    rule_distribution: Dict[str, int] = Field(default_factory=dict, description="Alert count by rule")
    avg_resolution_time_minutes: float = Field(default=0, ge=0, description="Average resolution time in minutes")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Metrics generation timestamp")

# Configuration Models
class AlertConfiguration(BaseModel):
    """Alert system configuration."""
    default_cooldown_minutes: int = Field(default=15, ge=0, description="Default cooldown period")
    max_alerts_per_hour: int = Field(default=100, ge=1, description="Maximum alerts per hour")
    escalation_enabled: bool = Field(default=True, description="Whether escalation is enabled")
    suppression_enabled: bool = Field(default=True, description="Whether suppression is enabled")
    notification_retry_attempts: int = Field(default=3, ge=0, description="Notification retry attempts")
    notification_retry_delay_seconds: int = Field(default=60, ge=0, description="Retry delay in seconds")

# Request/Response Models
class AlertRuleRequest(BaseModel):
    """Request to create an alert rule."""
    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    conditions: List[AlertCondition] = Field(..., description="Alert conditions")
    severity: AlertSeverity = Field(..., description="Alert severity")
    enabled: bool = Field(default=True, description="Whether rule is enabled")
    cooldown_minutes: int = Field(default=15, ge=0, description="Cooldown period")
    actions: List[AlertAction] = Field(default_factory=list, description="Actions to take")
    tags: List[str] = Field(default_factory=list, description="Rule tags")

class AlertRuleResponse(BaseModel):
    """Response for alert rule creation."""
    success: bool = Field(..., description="Whether creation was successful")
    rule_id: Optional[str] = Field(None, description="Created rule ID")
    errors: List[str] = Field(default_factory=list, description="Any errors")

class NotificationRequest(BaseModel):
    """Request to send notification."""
    alert_id: str = Field(..., description="Alert ID")
    channel_ids: List[str] = Field(..., description="Channel IDs to send to")
    template_id: Optional[str] = Field(None, description="Template ID to use")
    custom_subject: Optional[str] = Field(None, description="Custom subject")
    custom_body: Optional[str] = Field(None, description="Custom body")

class NotificationResponse(BaseModel):
    """Response for notification sending."""
    success: bool = Field(..., description="Whether sending was successful")
    notification_ids: List[str] = Field(default_factory=list, description="Sent notification IDs")
    errors: List[str] = Field(default_factory=list, description="Any errors")

class AlertMetricsRequest(BaseModel):
    """Request for alert metrics."""
    time_range_hours: int = Field(default=24, ge=1, le=168, description="Time range in hours")
    include_severity_breakdown: bool = Field(default=True, description="Include severity breakdown")
    include_rule_breakdown: bool = Field(default=True, description="Include rule breakdown")
    include_resolution_times: bool = Field(default=True, description="Include resolution times")

class AlertMetricsResponse(BaseModel):
    """Response for alert metrics."""
    metrics: Optional[AlertMetrics] = Field(None, description="Alert metrics")
    success: bool = Field(..., description="Whether request was successful")
    errors: List[str] = Field(default_factory=list, description="Any errors")

# Advanced Models
class AlertRuleUpdate(BaseModel):
    """Request to update an alert rule."""
    rule_id: str = Field(..., description="Rule ID to update")
    name: Optional[str] = Field(None, description="New rule name")
    description: Optional[str] = Field(None, description="New rule description")
    conditions: Optional[List[AlertCondition]] = Field(None, description="New conditions")
    severity: Optional[AlertSeverity] = Field(None, description="New severity")
    enabled: Optional[bool] = Field(None, description="New enabled status")
    cooldown_minutes: Optional[int] = Field(None, ge=0, description="New cooldown period")
    actions: Optional[List[AlertAction]] = Field(None, description="New actions")
    tags: Optional[List[str]] = Field(None, description="New tags")

class AlertRuleDelete(BaseModel):
    """Request to delete an alert rule."""
    rule_id: str = Field(..., description="Rule ID to delete")
    force: bool = Field(default=False, description="Force deletion even if alerts exist")

class AlertBulkAction(BaseModel):
    """Request for bulk alert actions."""
    alert_ids: List[str] = Field(..., description="Alert IDs to act on")
    action: str = Field(..., description="Action to perform (acknowledge, resolve, suppress)")
    reason: Optional[str] = Field(None, description="Reason for action")
    performed_by: str = Field(..., description="Who performed the action")

class AlertSearchRequest(BaseModel):
    """Request to search alerts."""
    query: Optional[str] = Field(None, description="Search query")
    severity: Optional[AlertSeverity] = Field(None, description="Filter by severity")
    status: Optional[AlertStatus] = Field(None, description="Filter by status")
    rule_id: Optional[str] = Field(None, description="Filter by rule ID")
    start_date: Optional[datetime] = Field(None, description="Start date filter")
    end_date: Optional[datetime] = Field(None, description="End date filter")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum results")
    offset: int = Field(default=0, ge=0, description="Result offset")

class AlertSearchResponse(BaseModel):
    """Response for alert search."""
    alerts: List[AlertHistory] = Field(..., description="Matching alerts")
    total_count: int = Field(..., ge=0, description="Total number of matching alerts")
    has_more: bool = Field(..., description="Whether there are more results")
    success: bool = Field(..., description="Whether search was successful")
    errors: List[str] = Field(default_factory=list, description="Any errors")