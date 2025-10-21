"""
Analytics data models for comprehensive fertilizer application system analysis.

This module defines Pydantic models for analytics data structures including:
- User engagement metrics
- Recommendation effectiveness tracking
- Agricultural impact assessment
- System performance analytics
- Usage pattern analysis
- Comprehensive reporting models
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class AnalyticsMetricType(str, Enum):
    """Types of analytics metrics."""
    USER_ENGAGEMENT = "user_engagement"
    RECOMMENDATION_ACCURACY = "recommendation_accuracy"
    AGRICULTURAL_IMPACT = "agricultural_impact"
    SYSTEM_PERFORMANCE = "system_performance"
    USAGE_PATTERNS = "usage_patterns"
    SUCCESS_RATE = "success_rate"
    COST_EFFECTIVENESS = "cost_effectiveness"
    ENVIRONMENTAL_IMPACT = "environmental_impact"


class AnalyticsPeriod(str, Enum):
    """Analytics time periods."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class ReportType(str, Enum):
    """Types of analytics reports."""
    SUMMARY = "summary"
    DETAILED = "detailed"
    EXECUTIVE = "executive"
    TECHNICAL = "technical"
    AGRICULTURAL = "agricultural"


class UserEngagementMetrics(BaseModel):
    """User engagement analytics data model."""
    
    user_id: str = Field(..., description="User identifier")
    session_count: int = Field(..., ge=0, description="Total number of user sessions")
    total_time_minutes: float = Field(..., ge=0, description="Total time spent in minutes")
    recommendations_requested: int = Field(..., ge=0, description="Number of recommendations requested")
    recommendations_implemented: int = Field(..., ge=0, description="Number of recommendations implemented")
    feedback_provided: int = Field(..., ge=0, description="Number of feedback instances provided")
    features_used: List[str] = Field(default_factory=list, description="List of features used")
    last_activity: str = Field(..., description="Last activity timestamp")
    engagement_score: float = Field(..., ge=0, le=1, description="Overall engagement score (0-1)")
    
    @validator('engagement_score')
    def validate_engagement_score(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Engagement score must be between 0 and 1')
        return v


class RecommendationEffectiveness(BaseModel):
    """Recommendation effectiveness analysis model."""
    
    recommendation_id: str = Field(..., description="Recommendation identifier")
    method_recommended: str = Field(..., description="Recommended application method")
    method_implemented: Optional[str] = Field(None, description="Actually implemented method")
    farmer_satisfaction: Optional[float] = Field(None, ge=1, le=5, description="Farmer satisfaction rating (1-5)")
    yield_impact: Optional[float] = Field(None, description="Yield impact percentage")
    cost_savings: Optional[float] = Field(None, ge=0, description="Cost savings in dollars")
    implementation_rate: float = Field(..., ge=0, le=1, description="Implementation rate (0-1)")
    success_score: float = Field(..., ge=0, le=1, description="Overall success score (0-1)")
    
    @validator('farmer_satisfaction')
    def validate_farmer_satisfaction(cls, v):
        if v is not None and not 1 <= v <= 5:
            raise ValueError('Farmer satisfaction must be between 1 and 5')
        return v


class EnvironmentalBenefits(BaseModel):
    """Environmental benefits assessment model."""
    
    fertilizer_reduction: float = Field(..., ge=0, description="Fertilizer reduction percentage")
    water_conservation: float = Field(..., ge=0, description="Water conservation in gallons")
    soil_health_improvement: float = Field(..., ge=0, description="Soil health improvement score")
    carbon_sequestration: float = Field(..., ge=0, description="Carbon sequestration in tons")


class AgriculturalImpactMetrics(BaseModel):
    """Agricultural impact assessment model."""
    
    period: str = Field(..., description="Analysis period")
    total_recommendations: int = Field(..., ge=0, description="Total recommendations made")
    implemented_recommendations: int = Field(..., ge=0, description="Recommendations implemented")
    estimated_yield_increase: float = Field(..., description="Estimated yield increase percentage")
    estimated_cost_savings: float = Field(..., ge=0, description="Estimated cost savings in dollars")
    environmental_benefits: EnvironmentalBenefits = Field(..., description="Environmental benefits")
    farmer_satisfaction_avg: float = Field(..., ge=0, le=5, description="Average farmer satisfaction")
    adoption_rate: float = Field(..., ge=0, le=1, description="Recommendation adoption rate")
    
    @validator('adoption_rate')
    def validate_adoption_rate(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Adoption rate must be between 0 and 1')
        return v


class ResourceUtilization(BaseModel):
    """Resource utilization metrics model."""
    
    cpu_usage: float = Field(..., ge=0, le=100, description="CPU utilization percentage")
    memory_usage: float = Field(..., ge=0, le=100, description="Memory utilization percentage")
    disk_usage: float = Field(..., ge=0, le=100, description="Disk utilization percentage")
    network_usage: float = Field(..., ge=0, le=100, description="Network utilization percentage")


class SystemPerformanceMetrics(BaseModel):
    """System performance analytics model."""
    
    period: str = Field(..., description="Analysis period")
    total_requests: int = Field(..., ge=0, description="Total number of requests")
    average_response_time_ms: float = Field(..., ge=0, description="Average response time in milliseconds")
    error_rate: float = Field(..., ge=0, le=1, description="Error rate (0-1)")
    uptime_percentage: float = Field(..., ge=0, le=100, description="System uptime percentage")
    throughput_per_hour: float = Field(..., ge=0, description="Requests per hour")
    resource_utilization: ResourceUtilization = Field(..., description="Resource utilization metrics")
    
    @validator('error_rate')
    def validate_error_rate(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Error rate must be between 0 and 1')
        return v


class UsagePatternAnalysis(BaseModel):
    """Usage pattern analysis model."""
    
    period: str = Field(..., description="Analysis period")
    peak_usage_hours: List[int] = Field(..., description="Peak usage hours (0-23)")
    most_used_features: List[str] = Field(..., description="Most frequently used features")
    seasonal_patterns: Dict[str, int] = Field(..., description="Seasonal usage patterns")
    geographic_distribution: Dict[str, int] = Field(..., description="Geographic usage distribution")
    user_segments: Dict[str, int] = Field(..., description="User segment distribution")
    
    @validator('peak_usage_hours')
    def validate_peak_hours(cls, v):
        for hour in v:
            if not 0 <= hour <= 23:
                raise ValueError('Peak usage hours must be between 0 and 23')
        return v


class AnalyticsReport(BaseModel):
    """Comprehensive analytics report model."""
    
    report_id: str = Field(..., description="Unique report identifier")
    report_type: ReportType = Field(..., description="Type of report")
    period: str = Field(..., description="Analysis period")
    generated_at: str = Field(..., description="Report generation timestamp")
    user_engagement: UserEngagementMetrics = Field(..., description="User engagement metrics")
    recommendation_effectiveness: List[RecommendationEffectiveness] = Field(..., description="Recommendation effectiveness data")
    agricultural_impact: AgriculturalImpactMetrics = Field(..., description="Agricultural impact metrics")
    system_performance: SystemPerformanceMetrics = Field(..., description="System performance metrics")
    usage_patterns: UsagePatternAnalysis = Field(..., description="Usage pattern analysis")
    key_insights: List[str] = Field(..., description="Key insights from analysis")
    recommendations: List[str] = Field(..., description="Actionable recommendations")


class AnalyticsSummary(BaseModel):
    """Analytics summary model for quick overview."""
    
    period: str = Field(..., description="Summary period")
    total_users: int = Field(..., ge=0, description="Total active users")
    total_recommendations: int = Field(..., ge=0, description="Total recommendations made")
    implementation_rate: float = Field(..., ge=0, le=1, description="Overall implementation rate")
    average_satisfaction: float = Field(..., ge=0, le=5, description="Average farmer satisfaction")
    system_uptime: float = Field(..., ge=0, le=100, description="System uptime percentage")
    key_metrics: Dict[str, float] = Field(..., description="Key performance metrics")
    summary_generated_at: str = Field(..., description="Summary generation timestamp")


class UserSessionData(BaseModel):
    """User session data model for tracking."""
    
    session_id: str = Field(..., description="Session identifier")
    user_id: str = Field(..., description="User identifier")
    start_time: str = Field(..., description="Session start timestamp")
    end_time: Optional[str] = Field(None, description="Session end timestamp")
    duration_minutes: float = Field(..., ge=0, description="Session duration in minutes")
    actions: List[str] = Field(default_factory=list, description="Actions performed")
    features_used: List[str] = Field(default_factory=list, description="Features used")
    region: Optional[str] = Field(None, description="User region")
    user_type: Optional[str] = Field(None, description="User type")


class RecommendationOutcomeData(BaseModel):
    """Recommendation outcome data model."""
    
    recommendation_id: str = Field(..., description="Recommendation identifier")
    user_id: str = Field(..., description="User identifier")
    method_recommended: str = Field(..., description="Recommended method")
    method_implemented: Optional[str] = Field(None, description="Implemented method")
    implementation_date: Optional[str] = Field(None, description="Implementation date")
    farmer_satisfaction: Optional[float] = Field(None, ge=1, le=5, description="Farmer satisfaction")
    yield_impact: Optional[float] = Field(None, description="Yield impact percentage")
    cost_savings: Optional[float] = Field(None, ge=0, description="Cost savings")
    environmental_benefits: Optional[EnvironmentalBenefits] = Field(None, description="Environmental benefits")
    feedback_notes: Optional[str] = Field(None, description="Additional feedback")
    outcome_timestamp: str = Field(..., description="Outcome recording timestamp")


class SystemMetricData(BaseModel):
    """System metric data model."""
    
    metric_id: str = Field(..., description="Metric identifier")
    timestamp: str = Field(..., description="Metric timestamp")
    requests: int = Field(..., ge=0, description="Number of requests")
    response_time_ms: float = Field(..., ge=0, description="Response time in milliseconds")
    errors: int = Field(..., ge=0, description="Number of errors")
    uptime_percentage: float = Field(..., ge=0, le=100, description="Uptime percentage")
    resource_utilization: ResourceUtilization = Field(..., description="Resource utilization")
    throughput_per_hour: float = Field(..., ge=0, description="Throughput per hour")


class AnalyticsQuery(BaseModel):
    """Analytics query model for filtering data."""
    
    start_date: str = Field(..., description="Query start date")
    end_date: str = Field(..., description="Query end date")
    period: AnalyticsPeriod = Field(default=AnalyticsPeriod.MONTHLY, description="Analysis period")
    user_ids: Optional[List[str]] = Field(None, description="Filter by user IDs")
    regions: Optional[List[str]] = Field(None, description="Filter by regions")
    user_types: Optional[List[str]] = Field(None, description="Filter by user types")
    metrics: Optional[List[AnalyticsMetricType]] = Field(None, description="Specific metrics to include")


class AnalyticsResponse(BaseModel):
    """Analytics API response model."""
    
    success: bool = Field(..., description="Request success status")
    data: Optional[Dict[str, Any]] = Field(None, description="Analytics data")
    message: str = Field(..., description="Response message")
    timestamp: str = Field(..., description="Response timestamp")
    query_id: Optional[str] = Field(None, description="Query identifier for tracking")


class AlertConfiguration(BaseModel):
    """Alert configuration model for analytics monitoring."""
    
    alert_id: str = Field(..., description="Alert identifier")
    metric_type: AnalyticsMetricType = Field(..., description="Metric type to monitor")
    threshold_value: float = Field(..., description="Alert threshold value")
    comparison_operator: str = Field(..., description="Comparison operator (>, <, >=, <=, ==)")
    alert_frequency: str = Field(..., description="Alert frequency")
    notification_methods: List[str] = Field(..., description="Notification methods")
    enabled: bool = Field(default=True, description="Alert enabled status")


class AnalyticsDashboard(BaseModel):
    """Analytics dashboard model."""
    
    dashboard_id: str = Field(..., description="Dashboard identifier")
    title: str = Field(..., description="Dashboard title")
    widgets: List[Dict[str, Any]] = Field(..., description="Dashboard widgets")
    refresh_interval: int = Field(default=300, description="Refresh interval in seconds")
    user_permissions: List[str] = Field(..., description="User permissions")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")