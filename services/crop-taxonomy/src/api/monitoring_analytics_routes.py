"""
Comprehensive Monitoring and Analytics API Routes

FastAPI routes for comprehensive monitoring and analytics functionality.
Implements endpoints for TICKET-005_crop-variety-recommendations-15.2.

Features:
- Real-time dashboard data
- System health monitoring
- User engagement analytics
- Recommendation effectiveness metrics
- Business metrics and KPIs
- Alert management
- Metrics export and reporting
"""

from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID

from ..services.comprehensive_monitoring_analytics_service import (
    ComprehensiveMonitoringAnalyticsService,
    get_comprehensive_monitoring_analytics,
    AlertLevel
)

# Initialize router
router = APIRouter(prefix="/api/v1/crop-taxonomy", tags=["monitoring-analytics"])

# Initialize service
monitoring_service = get_comprehensive_monitoring_analytics()


@router.get("/monitoring/dashboard", response_model=Dict[str, Any])
async def get_dashboard_data():
    """
    GET /api/v1/crop-taxonomy/monitoring/dashboard - Real-time dashboard data
    
    **Features**:
    - System health metrics (CPU, memory, response time, error rate)
    - User engagement metrics (active users, satisfaction, session duration)
    - Recommendation effectiveness metrics (confidence, success rate, cache hit rate)
    - Business metrics (revenue impact, cost savings, environmental impact)
    - Active alerts and notifications
    - Real-time updates for monitoring dashboards
    
    **Response Schema**:
    ```json
    {
      "system_health": {
        "cpu_percent": 45.2,
        "memory_percent": 67.8,
        "response_time_ms": 1250.5,
        "error_rate": 0.02,
        "active_connections": 15
      },
      "user_engagement": {
        "active_users": 125,
        "new_users": 8,
        "session_duration_minutes": 12.5,
        "user_satisfaction_score": 0.87
      },
      "recommendation_effectiveness": {
        "total_recommendations": 1250,
        "average_confidence_score": 0.89,
        "cache_hit_rate": 0.75,
        "farmer_feedback_score": 0.84
      },
      "business_metrics": {
        "total_revenue_impact": 125000.0,
        "cost_savings_estimated": 45000.0,
        "environmental_impact_score": 0.78
      },
      "alerts": [
        {
          "id": "alert-123",
          "level": "warning",
          "title": "High CPU Usage",
          "message": "CPU usage is 85.2%",
          "timestamp": "2023-12-01T10:30:00Z"
        }
      ]
    }
    ```
    
    Returns comprehensive real-time dashboard data for system monitoring.
    """
    try:
        dashboard_data = monitoring_service.get_dashboard_data()
        
        # Convert to response format
        response = {
            "timestamp": dashboard_data.timestamp.isoformat(),
            "system_health": {
                "cpu_percent": dashboard_data.system_health.cpu_percent if dashboard_data.system_health else 0,
                "memory_percent": dashboard_data.system_health.memory_percent if dashboard_data.system_health else 0,
                "memory_used_mb": dashboard_data.system_health.memory_used_mb if dashboard_data.system_health else 0,
                "memory_available_mb": dashboard_data.system_health.memory_available_mb if dashboard_data.system_health else 0,
                "disk_usage_percent": dashboard_data.system_health.disk_usage_percent if dashboard_data.system_health else 0,
                "network_io_bytes": dashboard_data.system_health.network_io_bytes if dashboard_data.system_health else 0,
                "active_connections": dashboard_data.system_health.active_connections if dashboard_data.system_health else 0,
                "response_time_ms": dashboard_data.system_health.response_time_ms if dashboard_data.system_health else 0,
                "error_rate": dashboard_data.system_health.error_rate if dashboard_data.system_health else 0
            },
            "user_engagement": {
                "active_users": dashboard_data.user_engagement.active_users if dashboard_data.user_engagement else 0,
                "new_users": dashboard_data.user_engagement.new_users if dashboard_data.user_engagement else 0,
                "returning_users": dashboard_data.user_engagement.returning_users if dashboard_data.user_engagement else 0,
                "session_duration_minutes": dashboard_data.user_engagement.session_duration_minutes if dashboard_data.user_engagement else 0,
                "recommendations_requested": dashboard_data.user_engagement.recommendations_requested if dashboard_data.user_engagement else 0,
                "recommendations_accepted": dashboard_data.user_engagement.recommendations_accepted if dashboard_data.user_engagement else 0,
                "recommendations_rejected": dashboard_data.user_engagement.recommendations_rejected if dashboard_data.user_engagement else 0,
                "user_satisfaction_score": dashboard_data.user_engagement.user_satisfaction_score if dashboard_data.user_engagement else 0
            },
            "recommendation_effectiveness": {
                "total_recommendations": dashboard_data.recommendation_effectiveness.total_recommendations if dashboard_data.recommendation_effectiveness else 0,
                "successful_recommendations": dashboard_data.recommendation_effectiveness.successful_recommendations if dashboard_data.recommendation_effectiveness else 0,
                "failed_recommendations": dashboard_data.recommendation_effectiveness.failed_recommendations if dashboard_data.recommendation_effectiveness else 0,
                "average_confidence_score": dashboard_data.recommendation_effectiveness.average_confidence_score if dashboard_data.recommendation_effectiveness else 0,
                "average_response_time_ms": dashboard_data.recommendation_effectiveness.average_response_time_ms if dashboard_data.recommendation_effectiveness else 0,
                "cache_hit_rate": dashboard_data.recommendation_effectiveness.cache_hit_rate if dashboard_data.recommendation_effectiveness else 0,
                "expert_validation_rate": dashboard_data.recommendation_effectiveness.expert_validation_rate if dashboard_data.recommendation_effectiveness else 0,
                "farmer_feedback_score": dashboard_data.recommendation_effectiveness.farmer_feedback_score if dashboard_data.recommendation_effectiveness else 0
            },
            "business_metrics": {
                "total_revenue_impact": dashboard_data.business_metrics.total_revenue_impact if dashboard_data.business_metrics else 0,
                "cost_savings_estimated": dashboard_data.business_metrics.cost_savings_estimated if dashboard_data.business_metrics else 0,
                "environmental_impact_score": dashboard_data.business_metrics.environmental_impact_score if dashboard_data.business_metrics else 0,
                "user_retention_rate": dashboard_data.business_metrics.user_retention_rate if dashboard_data.business_metrics else 0,
                "market_penetration": dashboard_data.business_metrics.market_penetration if dashboard_data.business_metrics else 0,
                "customer_acquisition_cost": dashboard_data.business_metrics.customer_acquisition_cost if dashboard_data.business_metrics else 0,
                "lifetime_value": dashboard_data.business_metrics.lifetime_value if dashboard_data.business_metrics else 0
            },
            "alerts": [
                {
                    "id": alert.id,
                    "level": alert.level.value,
                    "title": alert.title,
                    "message": alert.message,
                    "metric_name": alert.metric_name,
                    "threshold_value": alert.threshold_value,
                    "current_value": alert.current_value,
                    "timestamp": alert.timestamp.isoformat(),
                    "resolved": alert.resolved
                }
                for alert in dashboard_data.alerts
            ]
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard data error: {str(e)}")


@router.get("/monitoring/metrics-summary", response_model=Dict[str, Any])
async def get_metrics_summary(
    hours: int = Query(24, ge=1, le=168, description="Time period in hours (1-168)")
):
    """
    GET /api/v1/crop-taxonomy/monitoring/metrics-summary - Metrics summary for specified time period
    
    **Features**:
    - Aggregated metrics over specified time period
    - Statistical analysis (averages, totals, trends)
    - Performance indicators and KPIs
    - Alert summary and status
    - Historical data analysis
    
    **Parameters**:
    - hours: Time period in hours (1-168, default: 24)
    
    **Response Schema**:
    ```json
    {
      "period_hours": 24,
      "timestamp": "2023-12-01T10:30:00Z",
      "system_health": {
        "avg_cpu_percent": 45.2,
        "avg_memory_percent": 67.8,
        "avg_response_time_ms": 1250.5,
        "avg_error_rate": 0.02,
        "data_points": 48
      },
      "user_engagement": {
        "avg_active_users": 125,
        "avg_new_users": 8,
        "avg_session_duration_minutes": 12.5,
        "avg_satisfaction_score": 0.87,
        "data_points": 48
      },
      "recommendation_effectiveness": {
        "total_recommendations": 1250,
        "avg_confidence_score": 0.89,
        "avg_response_time_ms": 1250.5,
        "avg_cache_hit_rate": 0.75,
        "data_points": 48
      },
      "business_metrics": {
        "total_revenue_impact": 125000.0,
        "total_cost_savings": 45000.0,
        "avg_environmental_score": 0.78,
        "avg_retention_rate": 0.85,
        "data_points": 48
      },
      "alerts": {
        "total_alerts": 15,
        "unresolved_alerts": 3,
        "critical_alerts": 1,
        "warning_alerts": 2
      }
    }
    ```
    
    Returns comprehensive metrics summary for the specified time period.
    """
    try:
        summary = monitoring_service.get_metrics_summary(hours)
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics summary error: {str(e)}")


@router.get("/monitoring/alerts", response_model=List[Dict[str, Any]])
async def get_alerts(
    level: Optional[str] = Query(None, description="Filter by alert level (info, warning, critical, emergency)"),
    resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of alerts to return")
):
    """
    GET /api/v1/crop-taxonomy/monitoring/alerts - Get system alerts
    
    **Features**:
    - Filter alerts by level and resolution status
    - Real-time alert monitoring
    - Alert history and trends
    - Performance threshold violations
    - System health notifications
    
    **Parameters**:
    - level: Filter by alert level (info, warning, critical, emergency)
    - resolved: Filter by resolved status (true/false)
    - limit: Maximum number of alerts to return (1-200, default: 50)
    
    **Response Schema**:
    ```json
    [
      {
        "id": "alert-123",
        "level": "warning",
        "title": "High CPU Usage",
        "message": "CPU usage is 85.2%, exceeding warning threshold of 80%",
        "metric_name": "cpu_percent",
        "threshold_value": 80.0,
        "current_value": 85.2,
        "timestamp": "2023-12-01T10:30:00Z",
        "resolved": false,
        "resolved_at": null
      }
    ]
    ```
    
    Returns list of system alerts with filtering options.
    """
    try:
        dashboard_data = monitoring_service.get_dashboard_data()
        alerts = dashboard_data.alerts
        
        # Apply filters
        if level:
            try:
                alert_level = AlertLevel(level.lower())
                alerts = [a for a in alerts if a.level == alert_level]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid alert level: {level}")
        
        if resolved is not None:
            alerts = [a for a in alerts if a.resolved == resolved]
        
        # Apply limit
        alerts = alerts[:limit]
        
        # Convert to response format
        response = [
            {
                "id": alert.id,
                "level": alert.level.value,
                "title": alert.title,
                "message": alert.message,
                "metric_name": alert.metric_name,
                "threshold_value": alert.threshold_value,
                "current_value": alert.current_value,
                "timestamp": alert.timestamp.isoformat(),
                "resolved": alert.resolved,
                "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None
            }
            for alert in alerts
        ]
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alerts error: {str(e)}")


@router.post("/monitoring/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """
    POST /api/v1/crop-taxonomy/monitoring/alerts/{alert_id}/resolve - Resolve an alert
    
    **Features**:
    - Mark alerts as resolved
    - Alert management and tracking
    - Resolution timestamp recording
    - Alert status updates
    
    **Parameters**:
    - alert_id: Unique identifier of the alert to resolve
    
    **Response Schema**:
    ```json
    {
      "success": true,
      "message": "Alert resolved successfully",
      "alert_id": "alert-123",
      "resolved_at": "2023-12-01T10:35:00Z"
    }
    ```
    
    Resolves the specified alert and updates its status.
    """
    try:
        success = monitoring_service.resolve_alert(alert_id)
        
        if success:
            return {
                "success": True,
                "message": "Alert resolved successfully",
                "alert_id": alert_id,
                "resolved_at": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alert resolution error: {str(e)}")


@router.get("/monitoring/export", response_model=Dict[str, Any])
async def export_metrics(
    format: str = Query("json", description="Export format (json, csv)"),
    hours: int = Query(24, ge=1, le=168, description="Time period in hours (1-168)")
):
    """
    GET /api/v1/crop-taxonomy/monitoring/export - Export metrics data
    
    **Features**:
    - Export metrics in multiple formats (JSON, CSV)
    - Historical data export
    - Comprehensive metrics collection
    - Data analysis and reporting
    - Integration with external tools
    
    **Parameters**:
    - format: Export format (json, csv, default: json)
    - hours: Time period in hours (1-168, default: 24)
    
    **Response Schema**:
    ```json
    {
      "export_timestamp": "2023-12-01T10:30:00Z",
      "period_hours": 24,
      "system_health_metrics": [...],
      "user_engagement_metrics": [...],
      "recommendation_effectiveness_metrics": [...],
      "business_metrics": [...],
      "alerts": [...],
      "metrics_summary": {...}
    }
    ```
    
    Exports comprehensive metrics data for analysis and reporting.
    """
    try:
        if format not in ["json", "csv"]:
            raise HTTPException(status_code=400, detail="Invalid format. Supported formats: json, csv")
        
        # Get metrics summary for the specified period
        summary = monitoring_service.get_metrics_summary(hours)
        
        # Export all metrics
        exported_data = await monitoring_service.export_metrics(format)
        
        # Add period information
        if isinstance(exported_data, dict):
            exported_data["period_hours"] = hours
            exported_data["metrics_summary"] = summary
        
        return exported_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics export error: {str(e)}")


@router.post("/monitoring/start")
async def start_monitoring(
    interval_seconds: int = Query(30, ge=10, le=300, description="Monitoring interval in seconds (10-300)")
):
    """
    POST /api/v1/crop-taxonomy/monitoring/start - Start background monitoring
    
    **Features**:
    - Start comprehensive background monitoring
    - Configurable monitoring intervals
    - Real-time metrics collection
    - Automated alert generation
    - System health tracking
    
    **Parameters**:
    - interval_seconds: Monitoring interval in seconds (10-300, default: 30)
    
    **Response Schema**:
    ```json
    {
      "success": true,
      "message": "Background monitoring started",
      "interval_seconds": 30,
      "started_at": "2023-12-01T10:30:00Z"
    }
    ```
    
    Starts comprehensive background monitoring with specified interval.
    """
    try:
        monitoring_service.start_monitoring(interval_seconds)
        
        return {
            "success": True,
            "message": "Background monitoring started",
            "interval_seconds": interval_seconds,
            "started_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Monitoring start error: {str(e)}")


@router.post("/monitoring/stop")
async def stop_monitoring():
    """
    POST /api/v1/crop-taxonomy/monitoring/stop - Stop background monitoring
    
    **Features**:
    - Stop background monitoring
    - Graceful shutdown
    - Resource cleanup
    - Monitoring status update
    
    **Response Schema**:
    ```json
    {
      "success": true,
      "message": "Background monitoring stopped",
      "stopped_at": "2023-12-01T10:35:00Z"
    }
    ```
    
    Stops comprehensive background monitoring.
    """
    try:
        monitoring_service.stop_monitoring()
        
        return {
            "success": True,
            "message": "Background monitoring stopped",
            "stopped_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Monitoring stop error: {str(e)}")


@router.get("/monitoring/health")
async def monitoring_health_check():
    """
    GET /api/v1/crop-taxonomy/monitoring/health - Health check for monitoring service
    
    **Features**:
    - Service health status
    - Monitoring system status
    - Database connectivity
    - Redis connectivity
    - Background task status
    
    **Response Schema**:
    ```json
    {
      "status": "healthy",
      "monitoring_active": true,
      "database_connected": true,
      "redis_connected": true,
      "last_update": "2023-12-01T10:30:00Z",
      "metrics_count": {
        "system_health": 100,
        "user_engagement": 100,
        "recommendation_effectiveness": 100,
        "business_metrics": 100,
        "alerts": 15
      }
    }
    ```
    
    Returns health status of the monitoring and analytics service.
    """
    try:
        dashboard_data = monitoring_service.get_dashboard_data()
        
        # Check service status
        status = "healthy"
        if not monitoring_service.monitoring_active:
            status = "monitoring_inactive"
        
        # Check database connectivity
        database_connected = monitoring_service.db_session is not None
        
        # Check Redis connectivity
        redis_connected = monitoring_service.redis_client is not None
        
        # Get metrics counts
        metrics_count = {
            "system_health": len(monitoring_service.system_health_metrics),
            "user_engagement": len(monitoring_service.user_engagement_metrics),
            "recommendation_effectiveness": len(monitoring_service.recommendation_effectiveness_metrics),
            "business_metrics": len(monitoring_service.business_metrics),
            "alerts": len(monitoring_service.alerts)
        }
        
        return {
            "status": status,
            "monitoring_active": monitoring_service.monitoring_active,
            "database_connected": database_connected,
            "redis_connected": redis_connected,
            "last_update": dashboard_data.timestamp.isoformat(),
            "metrics_count": metrics_count
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "monitoring_active": False,
            "database_connected": False,
            "redis_connected": False,
            "last_update": datetime.utcnow().isoformat(),
            "metrics_count": {}
        }