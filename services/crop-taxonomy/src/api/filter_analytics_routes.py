"""
Filter Analytics API Routes

FastAPI routes for comprehensive filter analytics, insights, and dashboard functionality.
Implements endpoints specifically at /api/v1/crop-taxonomy/ as required in the checklist.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID

from ..services.filter_analytics_service import FilterAnalyticsService
from ..models.filter_analytics_models import (
    FilterAnalyticsRequest, FilterAnalyticsResponse,
    FilterAnalyticsInsightsResponse, FilterABTestResult
)

# Initialize router
router = APIRouter(prefix="/api/v1/crop-taxonomy", tags=["filter-analytics"])

# Initialize service
analytics_service = FilterAnalyticsService()


@router.post("/analytics/filter-usage", response_model=FilterAnalyticsResponse)
async def get_filter_analytics(
    request: FilterAnalyticsRequest
):
    """
    POST /api/v1/crop-taxonomy/analytics/filter-usage - Comprehensive filter usage analytics
    
    **Features**:
    - Filter usage statistics over time
    - User behavior analysis and patterns
    - Popular filter identification and trends
    - Performance metrics for different filter types
    - Conversion rates and effectiveness analysis
    - Detailed user interaction tracking
    
    **Request Schema**:
    ```json
    {
      "request_id": "unique-request-id",
      "start_date": "2023-01-01T00:00:00Z",
      "end_date": "2023-12-31T23:59:59Z",
      "filter_criteria": {"climate_zones": ["5a", "5b"]},
      "user_id": "uuid-string",
      "limit": 100
    }
    ```
    
    Returns comprehensive filter usage analytics with insights and trends.
    """
    try:
        result = await analytics_service.get_filter_analytics(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Filter analytics error: {str(e)}")


@router.post("/analytics/filter-insights", response_model=FilterAnalyticsInsightsResponse)
async def get_filter_insights(
    request: FilterAnalyticsRequest
):
    """
    POST /api/v1/crop-taxonomy/analytics/filter-insights - AI-powered filter insights
    
    **Features**:
    - Actionable insights from filter usage data
    - Performance optimization recommendations
    - User behavior pattern identification
    - Filter effectiveness analysis
    - Predictive insights for filter improvements
    - Business intelligence for filter strategy
    
    **Request Schema**:
    ```json
    {
      "request_id": "unique-request-id",
      "start_date": "2023-01-01T00:00:00Z",
      "end_date": "2023-12-31T23:59:59Z",
      "filter_criteria": {"climate_zones": ["5a", "5b"]},
      "user_id": "uuid-string",
      "limit": 100
    }
    ```
    
    Returns actionable insights based on filter usage analytics.
    """
    try:
        result = await analytics_service.get_filter_insights(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Filter insights error: {str(e)}")


@router.get("/analytics/popular-filters", response_model=List[Dict[str, Any]])
async def get_popular_filters(
    start_date: datetime = Query(..., description="Start date for analysis"),
    end_date: datetime = Query(..., description="End date for analysis"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results to return"),
    user_id: Optional[UUID] = Query(None, description="Optional user ID to filter by user")
):
    """
    GET /api/v1/crop-taxonomy/analytics/popular-filters - Get popular filter statistics
    
    **Features**:
    - Most frequently used filters
    - Filter usage ranking and statistics
    - Time-based popularity trends
    - User-specific popular filters
    - Performance metrics for popular filters
    
    **Response includes**:
    - Filter type and value
    - Usage count
    - Success rate
    - Average result count
    - User engagement metrics
    """
    try:
        # Create a temporary request
        temp_request = FilterAnalyticsRequest(
            request_id=f"temp_{datetime.now().isoformat()}",
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
            limit=limit
        )
        
        analytics = await analytics_service.get_filter_analytics(temp_request)
        return analytics.popular_filters
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Popular filters error: {str(e)}")


@router.get("/analytics/filter-trends", response_model=List[Dict[str, Any]])
async def get_filter_trends(
    start_date: datetime = Query(..., description="Start date for trend analysis"),
    end_date: datetime = Query(..., description="End date for trend analysis"),
    filter_type: Optional[str] = Query(None, description="Optional filter type to analyze"),
    user_id: Optional[UUID] = Query(None, description="Optional user ID to filter by user")
):
    """
    GET /api/v1/crop-taxonomy/analytics/filter-trends - Get filter usage trends over time
    
    **Features**:
    - Filter usage trends by date
    - Seasonal pattern analysis
    - Growth and decline patterns
    - Comparative trend analysis
    - Predictive trend modeling
    
    **Response includes**:
    - Date-based trend data
    - Filter type and value
    - Usage count on each date
    - Average result count
    - Trend direction indicators
    """
    try:
        # Create a temporary request
        temp_request = FilterAnalyticsRequest(
            request_id=f"temp_{datetime.now().isoformat()}",
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
            limit=500  # Higher limit for trend data
        )
        
        analytics = await analytics_service.get_filter_analytics(temp_request)
        
        trends = analytics.trends
        if filter_type:
            trends = [t for t in trends if t.filter_type == filter_type]
        
        # Convert to dict format for response
        return [
            {
                "date": t.date.isoformat(),
                "filter_type": t.filter_type,
                "filter_value": t.filter_value,
                "usage_count": t.usage_count,
                "average_result_count": t.average_result_count
            }
            for t in trends
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Filter trends error: {str(e)}")


@router.get("/analytics/user-behavior", response_model=List[Dict[str, Any]])
async def get_user_behavior_patterns(
    start_date: datetime = Query(..., description="Start date for analysis"),
    end_date: datetime = Query(..., description="End date for analysis"),
    user_id: Optional[UUID] = Query(None, description="Optional user ID to analyze specific user"),
    pattern_type: Optional[str] = Query(None, description="Optional pattern type to filter")
):
    """
    GET /api/v1/crop-taxonomy/analytics/user-behavior - Get user behavior patterns in filtering
    
    **Features**:
    - Filter combination patterns
    - Progressive refinement behaviors
    - Common user workflows
    - Filter abandonment patterns
    - User journey analysis
    
    **Response includes**:
    - Pattern type and description
    - Frequency of pattern
    - Associated filters
    - Success metrics
    - Time-based patterns
    """
    try:
        # Create a temporary request
        temp_request = FilterAnalyticsRequest(
            request_id=f"temp_{datetime.now().isoformat()}",
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
            limit=100
        )
        
        analytics = await analytics_service.get_filter_analytics(temp_request)
        patterns = analytics.user_behavior_patterns
        
        if pattern_type:
            patterns = [p for p in patterns if p.get('pattern_type') == pattern_type]
        
        return patterns
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User behavior error: {str(e)}")


@router.get("/analytics/effectiveness", response_model=List[Dict[str, Any]])
async def get_filter_effectiveness(
    start_date: datetime = Query(..., description="Start date for analysis"),
    end_date: datetime = Query(..., description="End date for analysis"),
    filter_type: Optional[str] = Query(None, description="Optional filter type to analyze")
):
    """
    GET /api/v1/crop-taxonomy/analytics/effectiveness - Get filter effectiveness metrics
    
    **Features**:
    - Success rate by filter type/value
    - Conversion effectiveness
    - Result quality analysis
    - Performance comparison
    - Effectiveness trend analysis
    
    **Response includes**:
    - Filter type and value
    - Application count
    - Success count
    - Average result count
    - Conversion rate
    - Quality metrics
    """
    try:
        # Create a temporary request
        temp_request = FilterAnalyticsRequest(
            request_id=f"temp_{datetime.now().isoformat()}",
            start_date=start_date,
            end_date=end_date,
            limit=100
        )
        
        analytics = await analytics_service.get_filter_analytics(temp_request)
        effectiveness = analytics.effectiveness_metrics
        
        if filter_type:
            effectiveness = [e for e in effectiveness if e.filter_type == filter_type]
        
        # Convert to dict format for response
        return [
            {
                "filter_type": e.filter_type,
                "filter_value": e.filter_value,
                "application_count": e.application_count,
                "success_count": e.success_count,
                "average_result_count": e.average_result_count,
                "conversion_rate": e.conversion_rate
            }
            for e in effectiveness
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Filter effectiveness error: {str(e)}")


@router.post("/analytics/a-b-test", response_model=FilterABTestResult)
async def run_filter_ab_test(
    test_id: str = Query(..., description="Unique identifier for the A/B test"),
    filter_a: str = Query(..., description="JSON string of filter configuration A"),
    filter_b: str = Query(..., description="JSON string of filter configuration B"),
    metric: str = Query("result_quality", description="Metric to compare (result_quality, user_satisfaction, etc.)")
):
    """
    POST /api/v1/crop-taxonomy/analytics/a-b-test - Run A/B test between filter configurations
    
    **Features**:
    - Compare two filter configurations
    - Statistical significance analysis
    - Effect size calculation
    - Confidence interval reporting
    - Winner determination
    
    **Parameters**:
    - test_id: Unique identifier for the test
    - filter_a: JSON string of filter configuration A
    - filter_b: JSON string of filter configuration B  
    - metric: Metric to compare (result_quality, user_satisfaction, etc.)
    
    **Response includes**:
    - Test configuration
    - Results for each version
    - Statistical significance
    - Winner determination
    - Confidence level
    """
    try:
        import json
        
        # Parse JSON strings for filter configurations
        filter_config_a = json.loads(filter_a)
        filter_config_b = json.loads(filter_b)
        
        result = await analytics_service.run_filter_ab_test(
            test_id=test_id,
            filter_a=filter_config_a,
            filter_b=filter_config_b,
            metric=metric
        )
        
        return result
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON in filter configuration: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"A/B test error: {str(e)}")


@router.get("/analytics/dashboard-summary", response_model=Dict[str, Any])
async def get_dashboard_summary(
    days: int = Query(30, description="Number of days to analyze"),
    user_id: Optional[UUID] = Query(None, description="Optional user ID for user-specific analytics")
):
    """
    GET /api/v1/crop-taxonomy/analytics/dashboard-summary - Get dashboard summary metrics
    
    **Features**:
    - Key performance indicators
    - Usage trend summary
    - Top performing filters
    - System performance metrics
    - Quick insights overview
    
    **Response includes**:
    - Total filter applications
    - Unique users
    - Average results per filter
    - System performance metrics
    - Top filters of the period
    - Trend indicators
    """
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Create a request for analytics
        temp_request = FilterAnalyticsRequest(
            request_id=f"dashboard_{datetime.now().isoformat()}",
            start_date=start_date,
            end_date=end_date,
            user_id=user_id,
            limit=100
        )
        
        analytics = await analytics_service.get_filter_analytics(temp_request)
        
        # Format dashboard summary
        summary = {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "key_metrics": {
                "total_filter_applications": analytics.usage_summary.total_applications,
                "unique_users": analytics.usage_summary.unique_users,
                "average_results_per_filter": analytics.usage_summary.average_result_count,
                "filter_success_rate": analytics.usage_summary.filter_efficiency_score,
                "average_search_time_ms": analytics.usage_summary.average_search_duration
            },
            "top_filters": analytics.popular_filters[:5],  # Top 5 filters
            "insights_count": len(analytics.user_behavior_patterns),  # Number of behavior patterns
            "peak_usage_times": analytics.usage_summary.peak_usage_times[:3],  # Top 3 peak hours
            "recommendations_count": len(analytics.recommendations)
        }
        
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard summary error: {str(e)}")


@router.post("/analytics/record-usage", response_model=Dict[str, bool])
async def record_filter_usage(
    user_id: UUID = Query(..., description="User ID"),
    session_id: str = Query(..., description="Session ID"),
    filter_config: str = Query(..., description="JSON string of filter configuration applied"),
    result_count: int = Query(..., description="Number of results returned"),
    search_duration_ms: float = Query(..., description="Search duration in milliseconds"),
    interaction_type: str = Query("search", description="Type of interaction")
):
    """
    POST /api/v1/crop-taxonomy/analytics/record-usage - Record filter usage for analytics
    
    **Features**:
    - Record individual filter usage events
    - Track user interactions with filters
    - Capture performance metrics
    - Store usage context
    - Update real-time analytics
    
    **Parameters**:
    - user_id: User ID applying the filter
    - session_id: Session ID for tracking
    - filter_config: JSON string of the filter configuration
    - result_count: Number of results returned
    - search_duration_ms: Duration of the search in milliseconds
    - interaction_type: Type of interaction (search, refine, etc.)
    
    **Response**:
    - Success status
    """
    try:
        import json
        
        # Parse the filter configuration JSON
        filter_config_obj = json.loads(filter_config)
        
        success = await analytics_service.record_filter_usage(
            user_id=user_id,
            session_id=session_id,
            filter_config=filter_config_obj,
            result_count=result_count,
            search_duration_ms=search_duration_ms,
            interaction_type=interaction_type
        )
        
        return {"success": success}
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON in filter_config: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Record usage error: {str(e)}")


@router.get("/analytics/health")
async def analytics_health_check():
    """
    Health check endpoint for the filter analytics service.
    """
    return {
        "status": "healthy",
        "service": "filter-analytics",
        "features": [
            "filter_usage_analytics",
            "filter_insights",
            "trend_analysis",
            "effectiveness_metrics",
            "user_behavior_patterns"
        ],
        "timestamp": datetime.now().isoformat()
    }