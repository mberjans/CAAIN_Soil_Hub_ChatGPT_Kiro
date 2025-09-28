"""
Filter Analytics Models

Pydantic models for comprehensive filter usage analytics and insights.
Provides data structures for tracking filter usage, effectiveness, and user behavior patterns.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID


class FilterUsageRecord(BaseModel):
    """Record of filter usage by a user."""
    
    record_id: UUID = Field(..., description="Unique identifier for this usage record")
    user_id: UUID = Field(..., description="User who applied the filter")
    session_id: str = Field(..., description="Session identifier")
    filter_config: Dict[str, Any] = Field(..., description="The filter configuration applied")
    applied_at: datetime = Field(default_factory=datetime.utcnow, description="When the filter was applied")
    result_count: int = Field(..., description="Number of results returned")
    search_duration_ms: float = Field(..., description="Duration of the search in milliseconds")
    interaction_type: str = Field(default="search", description="Type of interaction (search, filter, refine, etc.)")
    page_context: Optional[str] = Field(None, description="Context of the page where filter was applied")
    source: Optional[str] = Field(None, description="Source of the filter application")


class FilterUsageSummary(BaseModel):
    """Summary of filter usage for analytics."""
    
    total_applications: int = Field(..., description="Total number of filter applications")
    unique_users: int = Field(..., description="Number of unique users who applied filters")
    most_popular_filters: List[Dict[str, Any]] = Field(default_factory=list, description="Most popular filter types and values")
    average_result_count: float = Field(..., description="Average number of results returned per filter")
    average_search_duration: float = Field(..., description="Average search duration in milliseconds")
    filter_efficiency_score: float = Field(..., ge=0.0, le=1.0, description="Efficiency score for filters")
    peak_usage_times: List[Dict[str, int]] = Field(default_factory=list, description="Peak usage times by hour/day")


class FilterEffectiveness(BaseModel):
    """Effectiveness metrics for specific filter configurations."""
    
    filter_type: str = Field(..., description="Type of filter (climate, soil, agricultural, etc.)")
    filter_value: Any = Field(..., description="Value of the filter")
    application_count: int = Field(..., description="Number of times this filter was applied")
    success_count: int = Field(..., description="Number of successful applications (yielded results)")
    average_result_count: float = Field(..., description="Average number of results returned")
    user_satisfaction_score: Optional[float] = Field(None, ge=0.0, le=5.0, description="User satisfaction rating")
    conversion_rate: float = Field(..., ge=0.0, le=1.0, description="Rate of users taking action after filter")


class FilterTrend(BaseModel):
    """Trend analysis for filter usage over time."""
    
    filter_type: str = Field(..., description="Type of filter")
    filter_value: Any = Field(..., description="Value of the filter")
    date: datetime = Field(..., description="Date of the trend data point")
    usage_count: int = Field(..., description="Number of times filter was used on that date")
    average_result_count: float = Field(..., description="Average results for that date")


class FilterAnalyticsRequest(BaseModel):
    """Request model for filter analytics."""
    
    request_id: str = Field(..., description="Unique request identifier")
    start_date: datetime = Field(..., description="Start date for analytics")
    end_date: datetime = Field(..., description="End date for analytics")
    filter_criteria: Optional[Dict[str, Any]] = Field(None, description="Specific filters to analyze")
    user_id: Optional[UUID] = Field(None, description="Specific user to analyze")
    limit: int = Field(default=100, description="Maximum number of results to return")


class FilterAnalyticsResponse(BaseModel):
    """Response model for filter analytics."""
    
    request_id: str = Field(..., description="Original request identifier")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="When the report was generated")
    
    # Usage Summary
    usage_summary: FilterUsageSummary = Field(..., description="Summary of filter usage")
    
    # Effectiveness Analysis
    effectiveness_metrics: List[FilterEffectiveness] = Field(default_factory=list, description="Effectiveness metrics for various filters")
    
    # Popular Filters
    popular_filters: List[Dict[str, Any]] = Field(default_factory=list, description="Most popular filters")
    
    # User Behavior Patterns
    user_behavior_patterns: List[Dict[str, Any]] = Field(default_factory=list, description="Identified user behavior patterns")
    
    # Trend Analysis
    trends: List[FilterTrend] = Field(default_factory=list, description="Trend analysis data")
    
    # Recommendations
    recommendations: List[Dict[str, Any]] = Field(default_factory=list, description="Recommendations based on analytics")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class FilterInsight(BaseModel):
    """Individual insight derived from filter analytics."""
    
    insight_id: str = Field(..., description="Unique identifier for the insight")
    title: str = Field(..., description="Title of the insight")
    description: str = Field(..., description="Detailed description of the insight")
    impact_level: str = Field(..., description="Impact level (high, medium, low)")
    category: str = Field(..., description="Category of insight (usage, effectiveness, trends)")
    data: Dict[str, Any] = Field(default_factory=dict, description="Supporting data for the insight")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations based on the insight")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="When the insight was generated")


class FilterAnalyticsInsightsResponse(BaseModel):
    """Response model specifically for filter insights."""
    
    request_id: str = Field(..., description="Original request identifier")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="When the insights were generated")
    insights: List[FilterInsight] = Field(default_factory=list, description="List of insights")
    summary_metrics: Dict[str, Any] = Field(default_factory=dict, description="Summary metrics for the insights")
    visualization_data: Dict[str, Any] = Field(default_factory=dict, description="Data ready for visualization")


class FilterPerformanceMetrics(BaseModel):
    """Performance metrics for filter operations."""
    
    filter_config_hash: str = Field(..., description="Hash of the filter configuration for identification")
    execution_count: int = Field(..., description="Number of times this filter config was executed")
    average_execution_time_ms: float = Field(..., description="Average execution time in milliseconds")
    success_rate: float = Field(..., ge=0.0, le=1.0, description="Success rate of filter execution")
    cache_hit_rate: float = Field(..., ge=0.0, le=1.0, description="Cache hit rate for this filter config")
    result_quality_score: float = Field(..., ge=0.0, le=1.0, description="Quality score of results returned")
    user_engagement_score: float = Field(..., ge=0.0, le=1.0, description="Engagement score based on user actions")


class FilterA/BTestResult(BaseModel):  # Note: Python doesn't allow / in class name
    """A/B test results for comparing filter effectiveness."""
    
    test_id: str = Field(..., description="Unique identifier for the A/B test")
    filter_version_a: Dict[str, Any] = Field(..., description="Configuration for filter version A")
    filter_version_b: Dict[str, Any] = Field(..., description="Configuration for filter version B")
    metric: str = Field(..., description="Metric being tested (result_quality, user_satisfaction, etc.)")
    result_a: float = Field(..., description="Result for version A")
    result_b: float = Field(..., description="Result for version B")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="Confidence in the test result")
    winner: Optional[str] = Field(None, description="Winner of the test (A, B, or None for tie)")
    sample_size: int = Field(..., description="Number of samples in the test")


# Fix the class name that had illegal character
class FilterABTestResult(BaseModel):
    """A/B test results for comparing filter effectiveness."""
    
    test_id: str = Field(..., description="Unique identifier for the A/B test")
    filter_version_a: Dict[str, Any] = Field(..., description="Configuration for filter version A")
    filter_version_b: Dict[str, Any] = Field(..., description="Configuration for filter version B")
    metric: str = Field(..., description="Metric being tested (result_quality, user_satisfaction, etc.)")
    result_a: float = Field(..., description="Result for version A")
    result_b: float = Field(..., description="Result for version B")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="Confidence in the test result")
    winner: Optional[str] = Field(None, description="Winner of the test (A, B, or None for tie)")
    sample_size: int = Field(..., description="Number of samples in the test")