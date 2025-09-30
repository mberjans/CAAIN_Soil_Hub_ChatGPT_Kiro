"""
Production Monitoring Models

Data models for production monitoring, analytics, and reporting.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from uuid import UUID, uuid4
from decimal import Decimal
from enum import Enum

class AlertSeverity(str, Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class MetricType(str, Enum):
    """Types of metrics being monitored."""
    SYSTEM_PERFORMANCE = "system_performance"
    USER_ENGAGEMENT = "user_engagement"
    RECOMMENDATION_EFFECTIVENESS = "recommendation_effectiveness"
    AGRICULTURAL_IMPACT = "agricultural_impact"
    DATABASE_HEALTH = "database_health"
    EXTERNAL_SERVICE_HEALTH = "external_service_health"

class ComparisonOperator(str, Enum):
    """Comparison operators for alert conditions."""
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"

class TrendDirection(str, Enum):
    """Trend direction options."""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"

class HealthStatus(str, Enum):
    """Health status options."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

# System Performance Models
class SystemResourceUsage(BaseModel):
    """System resource usage metrics."""
    cpu_usage_percent: float = Field(..., ge=0, le=100, description="CPU usage percentage")
    memory_usage_percent: float = Field(..., ge=0, le=100, description="Memory usage percentage")
    disk_usage_percent: float = Field(..., ge=0, le=100, description="Disk usage percentage")
    network_bytes_sent: int = Field(..., ge=0, description="Network bytes sent")
    network_bytes_received: int = Field(..., ge=0, description="Network bytes received")
    process_count: int = Field(..., ge=0, description="Number of running processes")
    python_memory_bytes: int = Field(..., ge=0, description="Python memory usage in bytes")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SystemPerformanceMetrics(BaseModel):
    """System performance metrics."""
    cpu_usage_percent: float = Field(..., ge=0, le=100, description="Average CPU usage percentage")
    memory_usage_percent: float = Field(..., ge=0, le=100, description="Average memory usage percentage")
    disk_usage_percent: float = Field(..., ge=0, le=100, description="Average disk usage percentage")
    network_bytes_sent: int = Field(..., ge=0, description="Total network bytes sent")
    network_bytes_received: int = Field(..., ge=0, description="Total network bytes received")
    process_count: float = Field(..., ge=0, description="Average process count")
    python_memory_bytes: float = Field(..., ge=0, description="Average Python memory usage")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# User Engagement Models
class UserActivityMetrics(BaseModel):
    """User activity metrics."""
    daily_active_users: float = Field(..., ge=0, description="Daily active users")
    weekly_active_users: float = Field(..., ge=0, description="Weekly active users")
    monthly_active_users: float = Field(..., ge=0, description="Monthly active users")
    avg_session_duration_minutes: float = Field(..., ge=0, description="Average session duration")
    requests_per_minute: float = Field(..., ge=0, description="Requests per minute")
    feature_usage_stats: Dict[str, float] = Field(default_factory=dict, description="Feature usage statistics")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class UserEngagementMetrics(BaseModel):
    """User engagement metrics."""
    daily_active_users: float = Field(..., ge=0, description="Daily active users")
    avg_session_duration_minutes: float = Field(..., ge=0, description="Average session duration in minutes")
    requests_per_minute: float = Field(..., ge=0, description="Requests per minute")
    feature_usage_stats: Dict[str, float] = Field(default_factory=dict, description="Feature usage statistics")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Recommendation Effectiveness Models
class RecommendationMetrics(BaseModel):
    """Recommendation effectiveness metrics."""
    recommendation_accuracy_percent: float = Field(..., ge=0, le=100, description="Recommendation accuracy percentage")
    recommendations_per_day: float = Field(..., ge=0, description="Recommendations generated per day")
    user_satisfaction_score: float = Field(..., ge=0, le=5, description="User satisfaction score (1-5)")
    implementation_rate_percent: float = Field(..., ge=0, le=100, description="Recommendation implementation rate")
    feedback_count: int = Field(..., ge=0, description="Number of user feedback responses")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class RecommendationEffectivenessMetrics(BaseModel):
    """Recommendation effectiveness metrics."""
    recommendation_accuracy_percent: float = Field(..., ge=0, le=100, description="Recommendation accuracy percentage")
    recommendations_per_day: float = Field(..., ge=0, description="Recommendations generated per day")
    user_satisfaction_score: float = Field(..., ge=0, le=5, description="User satisfaction score (1-5)")
    implementation_rate_percent: float = Field(..., ge=0, le=100, description="Recommendation implementation rate")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Agricultural Impact Models
class AgriculturalImpactMetrics(BaseModel):
    """Agricultural impact metrics."""
    total_water_savings_gallons: float = Field(..., ge=0, description="Total water savings in gallons")
    farms_with_conservation_practices: int = Field(..., ge=0, description="Number of farms using conservation practices")
    drought_risk_reduction_percent: float = Field(..., ge=0, le=100, description="Drought risk reduction percentage")
    total_cost_savings_dollars: float = Field(..., ge=0, description="Total cost savings in dollars")
    environmental_impact_score: float = Field(..., ge=0, le=100, description="Environmental impact score")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Health Status Models
class ServiceHealthStatus(BaseModel):
    """Service health status."""
    service_name: str = Field(..., description="Name of the service")
    status: HealthStatus = Field(..., description="Health status")
    response_time_ms: float = Field(..., ge=0, description="Response time in milliseconds")
    error_rate_percent: float = Field(..., ge=0, le=100, description="Error rate percentage")
    last_check: datetime = Field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional health details")

class DatabaseHealthStatus(BaseModel):
    """Database health status."""
    connection_count: int = Field(..., ge=0, description="Number of active connections")
    query_response_time_ms: float = Field(..., ge=0, description="Average query response time")
    error_rate_percent: float = Field(..., ge=0, le=100, description="Database error rate")
    disk_usage_percent: float = Field(..., ge=0, le=100, description="Database disk usage")
    last_backup: Optional[datetime] = Field(None, description="Last backup timestamp")
    status: HealthStatus = Field(..., description="Database health status")

class ExternalServiceHealthStatus(BaseModel):
    """External service health status."""
    service_name: str = Field(..., description="External service name")
    status: HealthStatus = Field(..., description="Service health status")
    response_time_ms: float = Field(..., ge=0, description="Response time in milliseconds")
    availability_percent: float = Field(..., ge=0, le=100, description="Service availability percentage")
    last_check: datetime = Field(default_factory=datetime.utcnow)
    error_message: Optional[str] = Field(None, description="Error message if any")

# Alert Models
class AlertConfiguration(BaseModel):
    """Alert configuration."""
    alert_id: str = Field(..., description="Unique alert identifier")
    metric_name: str = Field(..., description="Name of the metric to monitor")
    threshold_value: float = Field(..., description="Threshold value for the alert")
    comparison_operator: ComparisonOperator = Field(..., description="Comparison operator")
    severity: AlertSeverity = Field(..., description="Alert severity level")
    enabled: bool = Field(default=True, description="Whether the alert is enabled")
    cooldown_minutes: int = Field(default=15, ge=0, description="Cooldown period in minutes")
    notification_channels: List[str] = Field(default_factory=list, description="Notification channels")
    description: Optional[str] = Field(None, description="Alert description")

class ProductionAlert(BaseModel):
    """Production alert."""
    alert_id: UUID = Field(default_factory=uuid4, description="Unique alert identifier")
    alert_type: str = Field(..., description="Type of alert")
    severity: str = Field(..., description="Alert severity")
    message: str = Field(..., description="Alert message")
    metric_name: str = Field(..., description="Name of the metric that triggered the alert")
    current_value: float = Field(..., description="Current value of the metric")
    threshold_value: float = Field(..., description="Threshold value")
    triggered_at: datetime = Field(default_factory=datetime.utcnow, description="When the alert was triggered")
    acknowledged: bool = Field(default=False, description="Whether the alert has been acknowledged")
    acknowledged_by: Optional[str] = Field(None, description="Who acknowledged the alert")
    acknowledged_at: Optional[datetime] = Field(None, description="When the alert was acknowledged")
    resolved: bool = Field(default=False, description="Whether the alert has been resolved")
    resolved_at: Optional[datetime] = Field(None, description="When the alert was resolved")

# Performance Threshold Models
class PerformanceThreshold(BaseModel):
    """Performance threshold configuration."""
    metric_name: str = Field(..., description="Name of the metric")
    warning_threshold: float = Field(..., description="Warning threshold value")
    critical_threshold: float = Field(..., description="Critical threshold value")
    target_value: float = Field(..., description="Target value")
    unit: str = Field(default="", description="Unit of measurement")

# Monitoring Configuration Models
class MonitoringConfiguration(BaseModel):
    """Monitoring configuration."""
    collection_interval_seconds: int = Field(default=60, ge=1, description="Metrics collection interval in seconds")
    retention_days: int = Field(default=90, ge=1, description="Data retention period in days")
    alert_cooldown_minutes: int = Field(default=15, ge=0, description="Alert cooldown period in minutes")
    metrics_buffer_size: int = Field(default=10000, ge=1000, description="Metrics buffer size")
    enable_real_time_alerts: bool = Field(default=True, description="Enable real-time alerts")
    enable_performance_tracking: bool = Field(default=True, description="Enable performance tracking")
    enable_user_engagement_tracking: bool = Field(default=True, description="Enable user engagement tracking")
    enable_recommendation_tracking: bool = Field(default=True, description="Enable recommendation tracking")
    enable_agricultural_impact_tracking: bool = Field(default=True, description="Enable agricultural impact tracking")

# Production Health Status Models
class ProductionHealthStatus(BaseModel):
    """Overall production health status."""
    overall_health_score: float = Field(..., ge=0, le=100, description="Overall health score (0-100)")
    system_performance: SystemPerformanceMetrics = Field(..., description="System performance metrics")
    user_engagement: UserEngagementMetrics = Field(..., description="User engagement metrics")
    recommendation_effectiveness: RecommendationEffectivenessMetrics = Field(..., description="Recommendation effectiveness metrics")
    active_alerts: List[ProductionAlert] = Field(default_factory=list, description="Active alerts")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

# Real-time Metrics Models
class RealTimeMetrics(BaseModel):
    """Real-time metrics data."""
    metrics: Dict[str, float] = Field(..., description="Current metric values")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of the metrics")
    collection_active: bool = Field(..., description="Whether metrics collection is active")

# Historical Metrics Models
class HistoricalMetrics(BaseModel):
    """Historical metrics data."""
    metric_name: str = Field(..., description="Name of the metric")
    data_points: List[Dict[str, Any]] = Field(..., description="Historical data points")
    time_range_hours: int = Field(..., description="Time range in hours")
    total_points: int = Field(..., description="Total number of data points")

# Performance Trend Models
class PerformanceTrend(BaseModel):
    """Performance trend analysis."""
    metric_name: str = Field(..., description="Name of the metric")
    trend_direction: TrendDirection = Field(..., description="Trend direction")
    change_percent: float = Field(..., description="Percentage change")
    first_value: float = Field(..., description="First value in the period")
    last_value: float = Field(..., description="Last value in the period")
    data_points: int = Field(..., description="Number of data points")

# Production Monitoring Report Models
class ProductionMonitoringReport(BaseModel):
    """Comprehensive production monitoring report."""
    report_id: UUID = Field(default_factory=uuid4, description="Unique report identifier")
    start_date: datetime = Field(..., description="Report start date")
    end_date: datetime = Field(..., description="Report end date")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Report generation timestamp")
    system_performance: SystemPerformanceMetrics = Field(..., description="System performance metrics")
    user_engagement: UserEngagementMetrics = Field(..., description="User engagement metrics")
    recommendation_effectiveness: RecommendationEffectivenessMetrics = Field(..., description="Recommendation effectiveness metrics")
    agricultural_impact: AgriculturalImpactMetrics = Field(..., description="Agricultural impact metrics")
    performance_trends: List[PerformanceTrend] = Field(default_factory=list, description="Performance trends")
    summary: Dict[str, Any] = Field(default_factory=dict, description="Report summary")

# Request/Response Models
class ProductionMonitoringRequest(BaseModel):
    """Request for production monitoring data."""
    time_range_hours: int = Field(default=24, ge=1, le=168, description="Time range in hours")
    include_system_metrics: bool = Field(default=True, description="Include system performance metrics")
    include_user_metrics: bool = Field(default=True, description="Include user engagement metrics")
    include_recommendation_metrics: bool = Field(default=True, description="Include recommendation effectiveness metrics")
    include_agricultural_metrics: bool = Field(default=True, description="Include agricultural impact metrics")
    include_alerts: bool = Field(default=True, description="Include active alerts")

class ProductionMonitoringResponse(BaseModel):
    """Response containing production monitoring data."""
    health_status: ProductionHealthStatus = Field(..., description="Overall health status")
    real_time_metrics: RealTimeMetrics = Field(..., description="Real-time metrics")
    historical_metrics: List[HistoricalMetrics] = Field(default_factory=list, description="Historical metrics")
    active_alerts: List[ProductionAlert] = Field(default_factory=list, description="Active alerts")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Response generation timestamp")

class AlertConfigurationRequest(BaseModel):
    """Request to configure alerts."""
    alert_configurations: List[AlertConfiguration] = Field(..., description="Alert configurations")

class AlertConfigurationResponse(BaseModel):
    """Response for alert configuration."""
    success: bool = Field(..., description="Whether configuration was successful")
    configured_alerts: List[str] = Field(..., description="List of configured alert IDs")
    errors: List[str] = Field(default_factory=list, description="Any configuration errors")

class PerformanceThresholdRequest(BaseModel):
    """Request to configure performance thresholds."""
    thresholds: List[PerformanceThreshold] = Field(..., description="Performance thresholds")

class PerformanceThresholdResponse(BaseModel):
    """Response for performance threshold configuration."""
    success: bool = Field(..., description="Whether configuration was successful")
    configured_thresholds: List[str] = Field(..., description="List of configured threshold metric names")
    errors: List[str] = Field(default_factory=list, description="Any configuration errors")

class MonitoringConfigurationRequest(BaseModel):
    """Request to configure monitoring settings."""
    configuration: MonitoringConfiguration = Field(..., description="Monitoring configuration")

class MonitoringConfigurationResponse(BaseModel):
    """Response for monitoring configuration."""
    success: bool = Field(..., description="Whether configuration was successful")
    configuration: MonitoringConfiguration = Field(..., description="Applied configuration")
    errors: List[str] = Field(default_factory=list, description="Any configuration errors")

class ReportGenerationRequest(BaseModel):
    """Request to generate a production monitoring report."""
    start_date: datetime = Field(..., description="Report start date")
    end_date: datetime = Field(..., description="Report end date")
    include_trends: bool = Field(default=True, description="Include performance trends")
    include_recommendations: bool = Field(default=True, description="Include recommendations")

class ReportGenerationResponse(BaseModel):
    """Response for report generation."""
    report: ProductionMonitoringReport = Field(..., description="Generated report")
    success: bool = Field(..., description="Whether report generation was successful")
    errors: List[str] = Field(default_factory=list, description="Any generation errors")