"""
Production Reporting Models

Data models for production reporting system, including report templates,
schedules, delivery mechanisms, and comprehensive report structures.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from uuid import UUID, uuid4
from decimal import Decimal
from enum import Enum

class ReportType(str, Enum):
    """Types of reports."""
    SYSTEM_PERFORMANCE = "system_performance"
    USER_ADOPTION = "user_adoption"
    AGRICULTURAL_OUTCOMES = "agricultural_outcomes"
    BUSINESS_METRICS = "business_metrics"
    COMPREHENSIVE = "comprehensive"
    CUSTOM = "custom"

class ReportFrequency(str, Enum):
    """Report generation frequencies."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    ON_DEMAND = "on_demand"

class ReportFormat(str, Enum):
    """Report output formats."""
    PDF = "pdf"
    HTML = "html"
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"
    POWERPOINT = "powerpoint"

class ReportStatus(str, Enum):
    """Report generation status."""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class ChartType(str, Enum):
    """Chart types for reports."""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    AREA = "area"
    DASHBOARD = "dashboard"
    TABLE = "table"

class InsightImpact(str, Enum):
    """Insight impact levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RecommendationPriority(str, Enum):
    """Recommendation priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class ImplementationEffort(str, Enum):
    """Implementation effort levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

# Report Template Models
class ReportTemplate(BaseModel):
    """Report template definition."""
    template_id: str = Field(..., description="Unique template identifier")
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    report_type: ReportType = Field(..., description="Type of report")
    sections: List[str] = Field(..., description="Report sections")
    charts: List[Dict[str, Any]] = Field(default_factory=list, description="Chart configurations")
    format: ReportFormat = Field(default=ReportFormat.HTML, description="Output format")
    variables: List[str] = Field(default_factory=list, description="Template variables")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Template creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Template last update timestamp")

# Report Configuration Models
class ReportConfiguration(BaseModel):
    """Report generation configuration."""
    config_id: str = Field(..., description="Unique configuration identifier")
    name: str = Field(..., description="Configuration name")
    default_format: ReportFormat = Field(default=ReportFormat.HTML, description="Default output format")
    include_charts: bool = Field(default=True, description="Include charts in reports")
    include_insights: bool = Field(default=True, description="Include insights in reports")
    include_recommendations: bool = Field(default=True, description="Include recommendations in reports")
    max_chart_points: int = Field(default=100, ge=10, description="Maximum points per chart")
    chart_width: int = Field(default=800, ge=200, description="Chart width in pixels")
    chart_height: int = Field(default=400, ge=200, description="Chart height in pixels")
    report_title_template: str = Field(default="Report - {report_type}", description="Report title template")
    report_footer_template: str = Field(default="Generated on {date}", description="Report footer template")

# Report Schedule Models
class ReportSchedule(BaseModel):
    """Report generation schedule."""
    schedule_id: str = Field(..., description="Unique schedule identifier")
    template_id: str = Field(..., description="Template to use")
    frequency: ReportFrequency = Field(..., description="Generation frequency")
    time_of_day: str = Field(default="09:00", description="Time of day to generate (HH:MM)")
    day_of_week: Optional[str] = Field(None, description="Day of week for weekly reports")
    day_of_month: Optional[int] = Field(None, ge=1, le=31, description="Day of month for monthly reports")
    timezone: str = Field(default="UTC", description="Timezone for scheduling")
    enabled: bool = Field(default=True, description="Whether schedule is enabled")
    recipients: List[str] = Field(default_factory=list, description="Report recipients")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Schedule creation timestamp")

# Report Delivery Models
class ReportDelivery(BaseModel):
    """Report delivery configuration."""
    delivery_id: str = Field(..., description="Unique delivery identifier")
    report_id: str = Field(..., description="Report ID")
    delivery_method: str = Field(..., description="Delivery method (email, webhook, etc.)")
    recipients: List[str] = Field(..., description="Delivery recipients")
    delivery_config: Dict[str, Any] = Field(default_factory=dict, description="Delivery configuration")
    scheduled_delivery: Optional[datetime] = Field(None, description="Scheduled delivery time")
    delivered_at: Optional[datetime] = Field(None, description="Actual delivery time")
    delivery_status: str = Field(default="pending", description="Delivery status")
    error_message: Optional[str] = Field(None, description="Error message if delivery failed")

# Report Subscription Models
class ReportSubscription(BaseModel):
    """Report subscription for users."""
    subscription_id: str = Field(..., description="Unique subscription identifier")
    user_id: str = Field(..., description="Subscribed user ID")
    report_type: ReportType = Field(..., description="Type of report to subscribe to")
    frequency: ReportFrequency = Field(..., description="Subscription frequency")
    format: ReportFormat = Field(default=ReportFormat.HTML, description="Preferred format")
    delivery_method: str = Field(default="email", description="Delivery method")
    enabled: bool = Field(default=True, description="Whether subscription is enabled")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Subscription creation timestamp")

# Report Section Models
class ReportSection(BaseModel):
    """Report section with data and analysis."""
    section_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique section identifier")
    section_name: str = Field(..., description="Section name")
    title: str = Field(..., description="Section title")
    data: Dict[str, Any] = Field(default_factory=dict, description="Section data")
    charts: List[Dict[str, Any]] = Field(default_factory=list, description="Section charts")
    insights: List[str] = Field(default_factory=list, description="Section insights")
    recommendations: List[str] = Field(default_factory=list, description="Section recommendations")
    order: int = Field(default=0, description="Section order in report")

# Report Chart Models
class ReportChart(BaseModel):
    """Report chart definition."""
    chart_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique chart identifier")
    chart_type: ChartType = Field(..., description="Chart type")
    title: str = Field(..., description="Chart title")
    data: List[Dict[str, Any]] = Field(..., description="Chart data points")
    x_axis_label: Optional[str] = Field(None, description="X-axis label")
    y_axis_label: Optional[str] = Field(None, description="Y-axis label")
    width: int = Field(default=800, ge=200, description="Chart width")
    height: int = Field(default=400, ge=200, description="Chart height")
    colors: List[str] = Field(default_factory=list, description="Chart colors")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional chart metadata")

# Report Metric Models
class ReportMetric(BaseModel):
    """Report metric definition."""
    metric_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique metric identifier")
    metric_name: str = Field(..., description="Metric name")
    metric_value: float = Field(..., description="Metric value")
    metric_unit: Optional[str] = Field(None, description="Metric unit")
    previous_value: Optional[float] = Field(None, description="Previous period value")
    change_percent: Optional[float] = Field(None, description="Percentage change")
    trend: Optional[str] = Field(None, description="Trend direction")
    target_value: Optional[float] = Field(None, description="Target value")
    status: str = Field(default="normal", description="Metric status")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metric metadata")

# Report Insight Models
class ReportInsight(BaseModel):
    """Report insight definition."""
    insight_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique insight identifier")
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Insight description")
    impact: InsightImpact = Field(default=InsightImpact.MEDIUM, description="Insight impact")
    confidence: float = Field(default=0.8, ge=0, le=1, description="Confidence level")
    supporting_data: Dict[str, Any] = Field(default_factory=dict, description="Supporting data")
    category: str = Field(default="general", description="Insight category")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Insight generation timestamp")

# Report Recommendation Models
class ReportRecommendation(BaseModel):
    """Report recommendation definition."""
    recommendation_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique recommendation identifier")
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="Recommendation description")
    priority: RecommendationPriority = Field(default=RecommendationPriority.MEDIUM, description="Recommendation priority")
    implementation_effort: ImplementationEffort = Field(default=ImplementationEffort.MEDIUM, description="Implementation effort")
    expected_impact: InsightImpact = Field(default=InsightImpact.MEDIUM, description="Expected impact")
    timeline: Optional[str] = Field(None, description="Implementation timeline")
    resources_required: List[str] = Field(default_factory=list, description="Required resources")
    success_metrics: List[str] = Field(default_factory=list, description="Success metrics")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Recommendation creation timestamp")

# Comprehensive Report Models
class SystemPerformanceReport(BaseModel):
    """System performance report."""
    report_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique report identifier")
    report_type: ReportType = Field(default=ReportType.SYSTEM_PERFORMANCE, description="Report type")
    title: str = Field(..., description="Report title")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Report generation timestamp")
    time_period: Dict[str, datetime] = Field(..., description="Report time period")
    system_metrics: Dict[str, Any] = Field(..., description="System performance metrics")
    resource_usage: Dict[str, Any] = Field(..., description="Resource usage data")
    error_analysis: Dict[str, Any] = Field(..., description="Error analysis")
    performance_trends: List[Dict[str, Any]] = Field(default_factory=list, description="Performance trends")
    recommendations: List[ReportRecommendation] = Field(default_factory=list, description="Recommendations")

class UserAdoptionReport(BaseModel):
    """User adoption report."""
    report_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique report identifier")
    report_type: ReportType = Field(default=ReportType.USER_ADOPTION, description="Report type")
    title: str = Field(..., description="Report title")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Report generation timestamp")
    time_period: Dict[str, datetime] = Field(..., description="Report time period")
    user_metrics: Dict[str, Any] = Field(..., description="User metrics")
    engagement_data: Dict[str, Any] = Field(..., description="User engagement data")
    feature_usage: Dict[str, Any] = Field(..., description="Feature usage data")
    growth_analysis: Dict[str, Any] = Field(..., description="Growth analysis")
    recommendations: List[ReportRecommendation] = Field(default_factory=list, description="Recommendations")

class AgriculturalOutcomesReport(BaseModel):
    """Agricultural outcomes report."""
    report_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique report identifier")
    report_type: ReportType = Field(default=ReportType.AGRICULTURAL_OUTCOMES, description="Report type")
    title: str = Field(..., description="Report title")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Report generation timestamp")
    time_period: Dict[str, datetime] = Field(..., description="Report time period")
    impact_metrics: Dict[str, Any] = Field(..., description="Impact metrics")
    water_savings: Dict[str, Any] = Field(..., description="Water savings data")
    cost_savings: Dict[str, Any] = Field(..., description="Cost savings data")
    environmental_impact: Dict[str, Any] = Field(..., description="Environmental impact data")
    farmer_feedback: Dict[str, Any] = Field(..., description="Farmer feedback data")
    recommendations: List[ReportRecommendation] = Field(default_factory=list, description="Recommendations")

class BusinessMetricsReport(BaseModel):
    """Business metrics report."""
    report_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique report identifier")
    report_type: ReportType = Field(default=ReportType.BUSINESS_METRICS, description="Report type")
    title: str = Field(..., description="Report title")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Report generation timestamp")
    time_period: Dict[str, datetime] = Field(..., description="Report time period")
    financial_metrics: Dict[str, Any] = Field(..., description="Financial metrics")
    customer_metrics: Dict[str, Any] = Field(..., description="Customer metrics")
    operational_metrics: Dict[str, Any] = Field(..., description="Operational metrics")
    market_metrics: Dict[str, Any] = Field(..., description="Market metrics")
    strategic_insights: List[ReportInsight] = Field(default_factory=list, description="Strategic insights")
    recommendations: List[ReportRecommendation] = Field(default_factory=list, description="Recommendations")

class ComprehensiveReport(BaseModel):
    """Comprehensive report covering all aspects."""
    report_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique report identifier")
    report_type: ReportType = Field(default=ReportType.COMPREHENSIVE, description="Report type")
    title: str = Field(..., description="Report title")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Report generation timestamp")
    time_period: Dict[str, datetime] = Field(..., description="Report time period")
    sections: List[ReportSection] = Field(..., description="Report sections")
    charts: List[ReportChart] = Field(default_factory=list, description="Report charts")
    insights: List[ReportInsight] = Field(default_factory=list, description="Report insights")
    recommendations: List[ReportRecommendation] = Field(default_factory=list, description="Report recommendations")
    summary: Dict[str, Any] = Field(default_factory=dict, description="Report summary")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional report metadata")

# Report History Models
class ReportHistory(BaseModel):
    """Report generation history."""
    report_id: str = Field(..., description="Unique report identifier")
    schedule_id: Optional[str] = Field(None, description="Schedule ID if scheduled")
    template_id: str = Field(..., description="Template used")
    report_type: ReportType = Field(..., description="Report type")
    status: ReportStatus = Field(..., description="Generation status")
    generated_at: datetime = Field(..., description="Generation timestamp")
    file_path: Optional[str] = Field(None, description="Generated file path")
    file_size_bytes: Optional[int] = Field(None, description="Generated file size")
    recipients: List[str] = Field(default_factory=list, description="Report recipients")
    delivery_status: Optional[str] = Field(None, description="Delivery status")
    error_message: Optional[str] = Field(None, description="Error message if failed")

# Report Metrics Models
class ReportMetrics(BaseModel):
    """Report generation metrics."""
    total_reports: int = Field(..., ge=0, description="Total reports generated")
    successful_reports: int = Field(..., ge=0, description="Successfully generated reports")
    failed_reports: int = Field(..., ge=0, description="Failed report generations")
    success_rate: float = Field(..., ge=0, le=100, description="Success rate percentage")
    reports_by_type: Dict[str, int] = Field(default_factory=dict, description="Report count by type")
    avg_generation_time_seconds: float = Field(default=0, ge=0, description="Average generation time")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Metrics generation timestamp")

# Request/Response Models
class ReportGenerationRequest(BaseModel):
    """Request to generate a report."""
    report_type: ReportType = Field(..., description="Type of report to generate")
    template_id: Optional[str] = Field(None, description="Specific template to use")
    time_period: Dict[str, datetime] = Field(..., description="Report time period")
    format: ReportFormat = Field(default=ReportFormat.HTML, description="Output format")
    include_charts: bool = Field(default=True, description="Include charts")
    include_insights: bool = Field(default=True, description="Include insights")
    include_recommendations: bool = Field(default=True, description="Include recommendations")
    recipients: Optional[List[str]] = Field(None, description="Report recipients")
    custom_sections: Optional[List[str]] = Field(None, description="Custom sections to include")

class ReportGenerationResponse(BaseModel):
    """Response for report generation."""
    success: bool = Field(..., description="Whether generation was successful")
    report: Optional[ComprehensiveReport] = Field(None, description="Generated report")
    report_id: Optional[str] = Field(None, description="Generated report ID")
    file_path: Optional[str] = Field(None, description="Generated file path")
    generation_time_seconds: Optional[float] = Field(None, description="Generation time")
    errors: List[str] = Field(default_factory=list, description="Any errors")

class ReportTemplateRequest(BaseModel):
    """Request to create a report template."""
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    report_type: ReportType = Field(..., description="Report type")
    sections: List[str] = Field(..., description="Report sections")
    charts: List[Dict[str, Any]] = Field(default_factory=list, description="Chart configurations")
    format: ReportFormat = Field(default=ReportFormat.HTML, description="Output format")
    variables: List[str] = Field(default_factory=list, description="Template variables")

class ReportTemplateResponse(BaseModel):
    """Response for report template creation."""
    success: bool = Field(..., description="Whether creation was successful")
    template_id: Optional[str] = Field(None, description="Created template ID")
    errors: List[str] = Field(default_factory=list, description="Any errors")

# Advanced Models
class ReportSubscriptionRequest(BaseModel):
    """Request to subscribe to reports."""
    user_id: str = Field(..., description="User ID")
    report_type: ReportType = Field(..., description="Report type to subscribe to")
    frequency: ReportFrequency = Field(..., description="Subscription frequency")
    format: ReportFormat = Field(default=ReportFormat.HTML, description="Preferred format")
    delivery_method: str = Field(default="email", description="Delivery method")

class ReportSubscriptionResponse(BaseModel):
    """Response for report subscription."""
    success: bool = Field(..., description="Whether subscription was successful")
    subscription_id: Optional[str] = Field(None, description="Created subscription ID")
    errors: List[str] = Field(default_factory=list, description="Any errors")

class ReportScheduleRequest(BaseModel):
    """Request to create a report schedule."""
    template_id: str = Field(..., description="Template to schedule")
    frequency: ReportFrequency = Field(..., description="Generation frequency")
    time_of_day: str = Field(default="09:00", description="Time of day")
    day_of_week: Optional[str] = Field(None, description="Day of week for weekly")
    day_of_month: Optional[int] = Field(None, description="Day of month for monthly")
    timezone: str = Field(default="UTC", description="Timezone")
    recipients: List[str] = Field(..., description="Report recipients")

class ReportScheduleResponse(BaseModel):
    """Response for report schedule creation."""
    success: bool = Field(..., description="Whether creation was successful")
    schedule_id: Optional[str] = Field(None, description="Created schedule ID")
    errors: List[str] = Field(default_factory=list, description="Any errors")