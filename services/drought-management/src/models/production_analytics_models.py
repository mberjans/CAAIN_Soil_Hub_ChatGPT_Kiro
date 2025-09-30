"""
Production Analytics Models

Data models for production analytics, usage pattern analysis,
success metrics calculation, and agricultural impact assessment.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from uuid import UUID, uuid4
from decimal import Decimal
from enum import Enum

class AnalyticsTimeframe(str, Enum):
    """Analytics timeframe options."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class AnalyticsGranularity(str, Enum):
    """Analytics granularity options."""
    FARM_LEVEL = "farm_level"
    FIELD_LEVEL = "field_level"
    USER_LEVEL = "user_level"
    REGIONAL_LEVEL = "regional_level"
    SYSTEM_LEVEL = "system_level"

class TrendDirection(str, Enum):
    """Trend direction options."""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"

class InsightImpact(str, Enum):
    """Insight impact levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class InsightType(str, Enum):
    """Types of analytics insights."""
    USAGE_PATTERN = "usage_pattern"
    USER_SATISFACTION = "user_satisfaction"
    RECOMMENDATION_EFFECTIVENESS = "recommendation_effectiveness"
    AGRICULTURAL_IMPACT = "agricultural_impact"
    SYSTEM_PERFORMANCE = "system_performance"
    BUSINESS_METRICS = "business_metrics"

# Usage Pattern Analysis Models
class PeakUsageAnalysis(BaseModel):
    """Peak usage analysis."""
    peak_hours: List[int] = Field(..., description="Hours with peak usage")
    hourly_averages: Dict[int, float] = Field(..., description="Average usage per hour")
    peak_usage_value: float = Field(..., description="Peak usage value")

class UsageTrendAnalysis(BaseModel):
    """Usage trend analysis."""
    trend: str = Field(..., description="Trend direction")
    change_percent: float = Field(..., description="Percentage change")
    first_value: float = Field(..., description="First value in period")
    last_value: float = Field(..., description="Last value in period")

class SeasonalPatternAnalysis(BaseModel):
    """Seasonal pattern analysis."""
    monthly_averages: Dict[int, float] = Field(..., description="Average usage per month")
    peak_month: int = Field(..., description="Month with peak usage")
    low_month: int = Field(..., description="Month with lowest usage")
    seasonal_variation: float = Field(..., description="Seasonal variation amount")

class UserBehaviorAnalysis(BaseModel):
    """User behavior analysis."""
    user_activity_levels: Dict[str, Dict[str, Any]] = Field(..., description="User activity levels")
    feature_popularity: Dict[str, int] = Field(..., description="Feature usage popularity")
    device_preferences: Dict[str, int] = Field(..., description="Device type preferences")
    most_active_users: List[Tuple[str, Dict[str, Any]]] = Field(..., description="Most active users")

class UsagePatternAnalysis(BaseModel):
    """Comprehensive usage pattern analysis."""
    analysis_id: UUID = Field(default_factory=uuid4, description="Unique analysis identifier")
    start_date: datetime = Field(..., description="Analysis start date")
    end_date: datetime = Field(..., description="Analysis end date")
    granularity: AnalyticsGranularity = Field(..., description="Analysis granularity")
    total_users: int = Field(..., ge=0, description="Total number of users")
    total_requests: int = Field(..., ge=0, description="Total number of requests")
    avg_requests_per_user: float = Field(..., ge=0, description="Average requests per user")
    peak_usage_times: Dict[str, Any] = Field(..., description="Peak usage time analysis")
    usage_trends: Dict[str, Any] = Field(..., description="Usage trend analysis")
    seasonal_patterns: Dict[str, Any] = Field(..., description="Seasonal pattern analysis")
    user_behavior_patterns: Dict[str, Any] = Field(..., description="User behavior pattern analysis")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Analysis generation timestamp")

# Success Metrics Analysis Models
class UserSatisfactionAnalysis(BaseModel):
    """User satisfaction analysis."""
    avg_satisfaction: float = Field(..., ge=0, le=5, description="Average satisfaction score")
    trend: str = Field(..., description="Satisfaction trend")
    min_satisfaction: float = Field(..., ge=0, le=5, description="Minimum satisfaction score")
    max_satisfaction: float = Field(..., ge=0, le=5, description="Maximum satisfaction score")
    satisfaction_distribution: Dict[str, float] = Field(..., description="Satisfaction distribution statistics")

class RecommendationEffectivenessAnalysis(BaseModel):
    """Recommendation effectiveness analysis."""
    avg_accuracy: float = Field(..., ge=0, le=100, description="Average recommendation accuracy")
    trend: str = Field(..., description="Accuracy trend")
    min_accuracy: float = Field(..., ge=0, le=100, description="Minimum accuracy")
    max_accuracy: float = Field(..., ge=0, le=100, description="Maximum accuracy")
    accuracy_distribution: Dict[str, float] = Field(..., description="Accuracy distribution statistics")

class SystemReliabilityAnalysis(BaseModel):
    """System reliability analysis."""
    avg_uptime: float = Field(..., ge=0, le=100, description="Average system uptime percentage")
    trend: str = Field(..., description="Uptime trend")
    min_uptime: float = Field(..., ge=0, le=100, description="Minimum uptime")
    max_uptime: float = Field(..., ge=0, le=100, description="Maximum uptime")
    downtime_percent: float = Field(..., ge=0, le=100, description="Downtime percentage")

class BusinessMetricsAnalysis(BaseModel):
    """Business metrics analysis."""
    user_retention_rate: float = Field(..., ge=0, le=100, description="User retention rate")
    feature_adoption_rate: float = Field(..., ge=0, le=100, description="Feature adoption rate")
    conversion_rate: float = Field(..., ge=0, le=100, description="Conversion rate")
    customer_lifetime_value: float = Field(..., ge=0, description="Customer lifetime value")
    churn_rate: float = Field(..., ge=0, le=100, description="Customer churn rate")

class SuccessMetricsAnalysis(BaseModel):
    """Comprehensive success metrics analysis."""
    analysis_id: UUID = Field(default_factory=uuid4, description="Unique analysis identifier")
    start_date: datetime = Field(..., description="Analysis start date")
    end_date: datetime = Field(..., description="Analysis end date")
    user_satisfaction: Dict[str, Any] = Field(..., description="User satisfaction analysis")
    recommendation_effectiveness: Dict[str, Any] = Field(..., description="Recommendation effectiveness analysis")
    system_reliability: Dict[str, Any] = Field(..., description="System reliability analysis")
    business_metrics: Dict[str, Any] = Field(..., description="Business metrics analysis")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Analysis generation timestamp")

# Agricultural Impact Analysis Models
class WaterSavingsAnalysis(BaseModel):
    """Water savings analysis."""
    total_savings: float = Field(..., ge=0, description="Total water savings")
    avg_daily_savings: float = Field(..., ge=0, description="Average daily savings")
    max_daily_savings: float = Field(..., ge=0, description="Maximum daily savings")
    min_daily_savings: float = Field(..., ge=0, description="Minimum daily savings")
    savings_trend: str = Field(..., description="Savings trend")

class CostSavingsAnalysis(BaseModel):
    """Cost savings analysis."""
    total_savings: float = Field(..., ge=0, description="Total cost savings")
    avg_daily_savings: float = Field(..., ge=0, description="Average daily savings")
    max_daily_savings: float = Field(..., ge=0, description="Maximum daily savings")
    min_daily_savings: float = Field(..., ge=0, description="Minimum daily savings")
    savings_trend: str = Field(..., description="Savings trend")
    roi_percentage: float = Field(..., ge=0, description="Return on investment percentage")

class EnvironmentalImpactAnalysis(BaseModel):
    """Environmental impact analysis."""
    avg_score: float = Field(..., ge=0, le=100, description="Average environmental impact score")
    trend: str = Field(..., description="Environmental impact trend")
    min_score: float = Field(..., ge=0, le=100, description="Minimum impact score")
    max_score: float = Field(..., ge=0, le=100, description="Maximum impact score")
    environmental_benefits: Dict[str, float] = Field(..., description="Environmental benefits breakdown")

class FarmProductivityAnalysis(BaseModel):
    """Farm productivity analysis."""
    yield_improvement_percent: float = Field(..., ge=0, description="Yield improvement percentage")
    efficiency_gains: float = Field(..., ge=0, description="Efficiency gains percentage")
    resource_optimization: float = Field(..., ge=0, description="Resource optimization percentage")
    sustainability_score: float = Field(..., ge=0, le=100, description="Sustainability score")

class AgriculturalImpactAnalysis(BaseModel):
    """Comprehensive agricultural impact analysis."""
    analysis_id: UUID = Field(default_factory=uuid4, description="Unique analysis identifier")
    start_date: datetime = Field(..., description="Analysis start date")
    end_date: datetime = Field(..., description="Analysis end date")
    water_savings_analysis: Dict[str, Any] = Field(..., description="Water savings analysis")
    cost_savings_analysis: Dict[str, Any] = Field(..., description="Cost savings analysis")
    environmental_impact: Dict[str, Any] = Field(..., description="Environmental impact analysis")
    farm_productivity: Dict[str, Any] = Field(..., description="Farm productivity analysis")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Analysis generation timestamp")

# Analytics Insights Models
class AnalyticsInsight(BaseModel):
    """Analytics insight."""
    insight_type: InsightType = Field(..., description="Type of insight")
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Insight description")
    impact: InsightImpact = Field(..., description="Impact level")
    recommendation: str = Field(..., description="Recommendation based on insight")
    confidence: float = Field(..., ge=0, le=1, description="Confidence level (0-1)")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Insight generation timestamp")

# Comprehensive Analytics Report Models
class AnalyticsReport(BaseModel):
    """Comprehensive analytics report."""
    report_id: UUID = Field(default_factory=uuid4, description="Unique report identifier")
    start_date: datetime = Field(..., description="Report start date")
    end_date: datetime = Field(..., description="Report end date")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Report generation timestamp")
    usage_patterns: UsagePatternAnalysis = Field(..., description="Usage pattern analysis")
    success_metrics: SuccessMetricsAnalysis = Field(..., description="Success metrics analysis")
    agricultural_impact: AgriculturalImpactAnalysis = Field(..., description="Agricultural impact analysis")
    insights: List[AnalyticsInsight] = Field(default_factory=list, description="Generated insights")
    summary: Dict[str, Any] = Field(default_factory=dict, description="Report summary")

# Request/Response Models
class AnalyticsRequest(BaseModel):
    """Request for analytics data."""
    start_date: datetime = Field(..., description="Analysis start date")
    end_date: datetime = Field(..., description="Analysis end date")
    granularity: AnalyticsGranularity = Field(default=AnalyticsGranularity.DAILY, description="Analysis granularity")
    include_usage_patterns: bool = Field(default=True, description="Include usage pattern analysis")
    include_success_metrics: bool = Field(default=True, description="Include success metrics analysis")
    include_agricultural_impact: bool = Field(default=True, description="Include agricultural impact analysis")
    include_insights: bool = Field(default=True, description="Include generated insights")

class AnalyticsResponse(BaseModel):
    """Response containing analytics data."""
    report: AnalyticsReport = Field(..., description="Generated analytics report")
    success: bool = Field(..., description="Whether analysis was successful")
    errors: List[str] = Field(default_factory=list, description="Any analysis errors")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Response generation timestamp")

# Advanced Analytics Models
class MetricCorrelation(BaseModel):
    """Metric correlation analysis."""
    metric1: str = Field(..., description="First metric name")
    metric2: str = Field(..., description="Second metric name")
    correlation_coefficient: float = Field(..., ge=-1, le=1, description="Correlation coefficient")
    significance: float = Field(..., ge=0, le=1, description="Statistical significance")
    interpretation: str = Field(..., description="Correlation interpretation")

class PerformanceBenchmark(BaseModel):
    """Performance benchmark."""
    metric_name: str = Field(..., description="Metric name")
    current_value: float = Field(..., description="Current metric value")
    benchmark_value: float = Field(..., description="Benchmark value")
    performance_percentile: float = Field(..., ge=0, le=100, description="Performance percentile")
    benchmark_source: str = Field(..., description="Benchmark data source")

class UserSegmentAnalysis(BaseModel):
    """User segment analysis."""
    segment_name: str = Field(..., description="User segment name")
    segment_size: int = Field(..., ge=0, description="Number of users in segment")
    avg_usage: float = Field(..., ge=0, description="Average usage for segment")
    satisfaction_score: float = Field(..., ge=0, le=5, description="Average satisfaction score")
    characteristics: Dict[str, Any] = Field(default_factory=dict, description="Segment characteristics")

class FeatureAdoptionAnalysis(BaseModel):
    """Feature adoption analysis."""
    feature_name: str = Field(..., description="Feature name")
    adoption_rate: float = Field(..., ge=0, le=100, description="Adoption rate percentage")
    time_to_adoption_days: float = Field(..., ge=0, description="Average time to adoption")
    user_satisfaction: float = Field(..., ge=0, le=5, description="User satisfaction with feature")
    retention_rate: float = Field(..., ge=0, le=100, description="Feature retention rate")

class ROI_Analysis(BaseModel):
    """Return on investment analysis."""
    investment_amount: float = Field(..., ge=0, description="Investment amount")
    returns_amount: float = Field(..., ge=0, description="Returns amount")
    roi_percentage: float = Field(..., description="ROI percentage")
    payback_period_months: float = Field(..., ge=0, description="Payback period in months")
    net_present_value: float = Field(..., description="Net present value")

class CostBenefitAnalysis(BaseModel):
    """Cost-benefit analysis."""
    total_costs: float = Field(..., ge=0, description="Total costs")
    total_benefits: float = Field(..., ge=0, description="Total benefits")
    net_benefit: float = Field(..., description="Net benefit")
    benefit_cost_ratio: float = Field(..., ge=0, description="Benefit-cost ratio")
    break_even_point_months: float = Field(..., ge=0, description="Break-even point in months")

class EnvironmentalImpactAnalysis(BaseModel):
    """Environmental impact analysis."""
    carbon_footprint_reduction: float = Field(..., ge=0, description="Carbon footprint reduction")
    water_conservation: float = Field(..., ge=0, description="Water conservation amount")
    soil_health_improvement: float = Field(..., ge=0, description="Soil health improvement score")
    biodiversity_impact: float = Field(..., ge=0, description="Biodiversity impact score")
    sustainability_rating: str = Field(..., description="Overall sustainability rating")

class DataQualityMetrics(BaseModel):
    """Data quality metrics."""
    completeness_score: float = Field(..., ge=0, le=100, description="Data completeness score")
    accuracy_score: float = Field(..., ge=0, le=100, description="Data accuracy score")
    consistency_score: float = Field(..., ge=0, le=100, description="Data consistency score")
    timeliness_score: float = Field(..., ge=0, le=100, description="Data timeliness score")
    overall_quality_score: float = Field(..., ge=0, le=100, description="Overall data quality score")

# Specific Insight Types
class RecommendationInsight(BaseModel):
    """Recommendation-specific insight."""
    recommendation_type: str = Field(..., description="Type of recommendation")
    effectiveness_score: float = Field(..., ge=0, le=100, description="Effectiveness score")
    implementation_rate: float = Field(..., ge=0, le=100, description="Implementation rate")
    user_satisfaction: float = Field(..., ge=0, le=5, description="User satisfaction")
    improvement_suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")

class PerformanceInsight(BaseModel):
    """Performance-specific insight."""
    performance_metric: str = Field(..., description="Performance metric")
    current_performance: float = Field(..., description="Current performance value")
    target_performance: float = Field(..., description="Target performance value")
    performance_gap: float = Field(..., description="Performance gap")
    improvement_opportunities: List[str] = Field(default_factory=list, description="Improvement opportunities")

class UserInsight(BaseModel):
    """User-specific insight."""
    user_segment: str = Field(..., description="User segment")
    behavior_pattern: str = Field(..., description="Behavior pattern")
    engagement_level: str = Field(..., description="Engagement level")
    satisfaction_trend: str = Field(..., description="Satisfaction trend")
    recommendations: List[str] = Field(default_factory=list, description="User-specific recommendations")

class AgriculturalInsight(BaseModel):
    """Agricultural-specific insight."""
    impact_area: str = Field(..., description="Impact area")
    impact_magnitude: float = Field(..., description="Impact magnitude")
    sustainability_benefit: float = Field(..., ge=0, description="Sustainability benefit")
    economic_benefit: float = Field(..., ge=0, description="Economic benefit")
    scalability_potential: str = Field(..., description="Scalability potential")