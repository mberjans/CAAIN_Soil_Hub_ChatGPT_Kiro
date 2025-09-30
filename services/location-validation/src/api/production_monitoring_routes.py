"""
Production Monitoring API Routes
TICKET-008_farm-location-input-15.2: Implement production monitoring and optimization

API endpoints for production monitoring, analytics, and optimization of location services.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..services.production_monitoring_service import (
    LocationProductionMonitoringService,
    MonitoringLevel,
    LocationAccuracyLevel
)
from ..services.production_analytics_service import (
    LocationProductionAnalyticsService,
    AnalyticsPeriod
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/monitoring", tags=["production-monitoring"])

# Dependency injection
async def get_monitoring_service() -> LocationProductionMonitoringService:
    """Get monitoring service instance."""
    return LocationProductionMonitoringService()

async def get_analytics_service() -> LocationProductionAnalyticsService:
    """Get analytics service instance."""
    return LocationProductionAnalyticsService()

# Pydantic models for API requests/responses
class LocationAccuracyRequest(BaseModel):
    """Request model for recording location accuracy."""
    location_id: str = Field(..., description="Location identifier")
    expected_coordinates: List[float] = Field(..., description="Expected coordinates [lat, lng]")
    actual_coordinates: List[float] = Field(..., description="Actual coordinates [lat, lng]")
    validation_method: str = Field(..., description="Validation method used")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    user_feedback: Optional[float] = Field(None, ge=0.0, le=1.0, description="User satisfaction rating")

class ServicePerformanceRequest(BaseModel):
    """Request model for recording service performance."""
    service_name: str = Field(..., description="Service name")
    endpoint: str = Field(..., description="API endpoint")
    response_time_ms: float = Field(..., description="Response time in milliseconds")
    status_code: int = Field(..., description="HTTP status code")
    error_type: Optional[str] = Field(None, description="Error type if applicable")
    cache_hit_rate: float = Field(0.0, ge=0.0, le=1.0, description="Cache hit rate")

class UserExperienceRequest(BaseModel):
    """Request model for recording user experience."""
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session identifier")
    action_type: str = Field(..., description="Action type performed")
    success: bool = Field(..., description="Whether action was successful")
    time_to_complete_ms: float = Field(..., description="Time to complete action")
    user_satisfaction: Optional[float] = Field(None, ge=0.0, le=1.0, description="User satisfaction rating")
    error_message: Optional[str] = Field(None, description="Error message if applicable")
    retry_count: int = Field(0, ge=0, description="Number of retries")

class AlertResolutionRequest(BaseModel):
    """Request model for resolving alerts."""
    alert_id: str = Field(..., description="Alert identifier")

class RecommendationUpdateRequest(BaseModel):
    """Request model for updating recommendation status."""
    recommendation_id: str = Field(..., description="Recommendation identifier")
    status: str = Field(..., description="New status")

class ThresholdsUpdateRequest(BaseModel):
    """Request model for updating monitoring thresholds."""
    thresholds: Dict[str, float] = Field(..., description="Updated thresholds")

class AnalyticsReportRequest(BaseModel):
    """Request model for generating analytics reports."""
    start_date: datetime = Field(..., description="Report start date")
    end_date: datetime = Field(..., description="Report end date")
    period: AnalyticsPeriod = Field(AnalyticsPeriod.DAILY, description="Analytics period")
    report_type: str = Field("comprehensive", description="Type of report to generate")

# API Endpoints

@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring service."""
    return {"status": "healthy", "service": "production-monitoring", "timestamp": datetime.utcnow().isoformat()}

@router.get("/dashboard")
async def get_monitoring_dashboard(
    service: LocationProductionMonitoringService = Depends(get_monitoring_service)
):
    """
    Get comprehensive monitoring dashboard data.
    
    Returns real-time monitoring data including:
    - Location accuracy metrics
    - Service performance metrics
    - User experience metrics
    - Active alerts
    - Optimization recommendations
    """
    try:
        dashboard_data = await service.get_monitoring_dashboard_data()
        return JSONResponse(content=dashboard_data)
    except Exception as e:
        logger.error(f"Error getting monitoring dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/metrics/location-accuracy")
async def record_location_accuracy(
    request: LocationAccuracyRequest,
    service: LocationProductionMonitoringService = Depends(get_monitoring_service)
):
    """
    Record location accuracy metrics.
    
    This endpoint is used to track the accuracy of location services
    for monitoring and optimization purposes.
    """
    try:
        await service.record_location_accuracy(
            location_id=request.location_id,
            expected_coordinates=(request.expected_coordinates[0], request.expected_coordinates[1]),
            actual_coordinates=(request.actual_coordinates[0], request.actual_coordinates[1]),
            validation_method=request.validation_method,
            processing_time_ms=request.processing_time_ms,
            user_feedback=request.user_feedback
        )
        
        return {"status": "success", "message": "Location accuracy recorded"}
    except Exception as e:
        logger.error(f"Error recording location accuracy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/metrics/service-performance")
async def record_service_performance(
    request: ServicePerformanceRequest,
    service: LocationProductionMonitoringService = Depends(get_monitoring_service)
):
    """
    Record service performance metrics.
    
    This endpoint tracks service performance including response times,
    error rates, and resource utilization.
    """
    try:
        await service.record_service_performance(
            service_name=request.service_name,
            endpoint=request.endpoint,
            response_time_ms=request.response_time_ms,
            status_code=request.status_code,
            error_type=request.error_type,
            cache_hit_rate=request.cache_hit_rate
        )
        
        return {"status": "success", "message": "Service performance recorded"}
    except Exception as e:
        logger.error(f"Error recording service performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/metrics/user-experience")
async def record_user_experience(
    request: UserExperienceRequest,
    service: LocationProductionMonitoringService = Depends(get_monitoring_service)
):
    """
    Record user experience metrics.
    
    This endpoint tracks user interactions, satisfaction, and experience
    with location services.
    """
    try:
        await service.record_user_experience(
            user_id=request.user_id,
            session_id=request.session_id,
            action_type=request.action_type,
            success=request.success,
            time_to_complete_ms=request.time_to_complete_ms,
            user_satisfaction=request.user_satisfaction,
            error_message=request.error_message,
            retry_count=request.retry_count
        )
        
        return {"status": "success", "message": "User experience recorded"}
    except Exception as e:
        logger.error(f"Error recording user experience: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts")
async def get_active_alerts(
    level: Optional[MonitoringLevel] = Query(None, description="Filter by alert level"),
    category: Optional[str] = Query(None, description="Filter by alert category"),
    service: LocationProductionMonitoringService = Depends(get_monitoring_service)
):
    """
    Get active monitoring alerts.
    
    Returns currently active alerts with optional filtering by level and category.
    """
    try:
        with service.lock:
            alerts = service.active_alerts
            
            # Apply filters
            if level:
                alerts = [a for a in alerts if a.level == level]
            if category:
                alerts = [a for a in alerts if a.category == category]
            
            # Convert to response format
            alert_data = [
                {
                    "alert_id": alert.alert_id,
                    "level": alert.level,
                    "category": alert.category,
                    "title": alert.title,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "resolved": alert.resolved,
                    "metadata": alert.metadata
                } for alert in alerts
            ]
            
            return {
                "alerts": alert_data,
                "total_count": len(alert_data),
                "critical_count": sum(1 for a in alert_data if a["level"] == MonitoringLevel.CRITICAL),
                "warning_count": sum(1 for a in alert_data if a["level"] == MonitoringLevel.WARNING)
            }
    except Exception as e:
        logger.error(f"Error getting active alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alerts/resolve")
async def resolve_alert(
    request: AlertResolutionRequest,
    service: LocationProductionMonitoringService = Depends(get_monitoring_service)
):
    """
    Resolve a monitoring alert.
    
    Marks the specified alert as resolved.
    """
    try:
        success = await service.resolve_alert(request.alert_id)
        if success:
            return {"status": "success", "message": f"Alert {request.alert_id} resolved"}
        else:
            raise HTTPException(status_code=404, detail="Alert not found")
    except Exception as e:
        logger.error(f"Error resolving alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations")
async def get_optimization_recommendations(
    status: Optional[str] = Query(None, description="Filter by recommendation status"),
    category: Optional[str] = Query(None, description="Filter by recommendation category"),
    service: LocationProductionMonitoringService = Depends(get_monitoring_service)
):
    """
    Get optimization recommendations.
    
    Returns current optimization recommendations with optional filtering.
    """
    try:
        with service.lock:
            recommendations = service.optimization_recommendations
            
            # Apply filters
            if status:
                recommendations = [r for r in recommendations if r.status == status]
            if category:
                recommendations = [r for r in recommendations if r.category == category]
            
            # Convert to response format
            recommendation_data = [
                {
                    "recommendation_id": rec.recommendation_id,
                    "category": rec.category,
                    "priority": rec.priority,
                    "title": rec.title,
                    "description": rec.description,
                    "current_value": rec.current_value,
                    "target_value": rec.target_value,
                    "potential_improvement_percent": rec.potential_improvement_percent,
                    "implementation_effort": rec.implementation_effort,
                    "estimated_impact": rec.estimated_impact,
                    "created_at": rec.created_at.isoformat(),
                    "status": rec.status
                } for rec in recommendations
            ]
            
            return {
                "recommendations": recommendation_data,
                "total_count": len(recommendation_data),
                "pending_count": sum(1 for r in recommendation_data if r["status"] == "pending"),
                "in_progress_count": sum(1 for r in recommendation_data if r["status"] == "in_progress")
            }
    except Exception as e:
        logger.error(f"Error getting optimization recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/recommendations/update-status")
async def update_recommendation_status(
    request: RecommendationUpdateRequest,
    service: LocationProductionMonitoringService = Depends(get_monitoring_service)
):
    """
    Update optimization recommendation status.
    
    Updates the status of a specific optimization recommendation.
    """
    try:
        success = await service.update_recommendation_status(request.recommendation_id, request.status)
        if success:
            return {"status": "success", "message": f"Recommendation {request.recommendation_id} status updated to {request.status}"}
        else:
            raise HTTPException(status_code=404, detail="Recommendation not found")
    except Exception as e:
        logger.error(f"Error updating recommendation status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/thresholds")
async def get_monitoring_thresholds(
    service: LocationProductionMonitoringService = Depends(get_monitoring_service)
):
    """
    Get current monitoring thresholds.
    
    Returns the current thresholds used for monitoring alerts and recommendations.
    """
    try:
        thresholds = service.get_thresholds()
        return {"thresholds": thresholds}
    except Exception as e:
        logger.error(f"Error getting monitoring thresholds: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/thresholds")
async def update_monitoring_thresholds(
    request: ThresholdsUpdateRequest,
    service: LocationProductionMonitoringService = Depends(get_monitoring_service)
):
    """
    Update monitoring thresholds.
    
    Updates the thresholds used for monitoring alerts and recommendations.
    """
    try:
        service.update_thresholds(request.thresholds)
        return {"status": "success", "message": "Monitoring thresholds updated"}
    except Exception as e:
        logger.error(f"Error updating monitoring thresholds: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cleanup")
async def cleanup_old_metrics(
    days_to_keep: int = Query(30, ge=1, le=365, description="Number of days to keep metrics"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    service: LocationProductionMonitoringService = Depends(get_monitoring_service)
):
    """
    Clean up old monitoring metrics.
    
    Removes metrics older than the specified number of days to prevent memory issues.
    """
    try:
        background_tasks.add_task(service.cleanup_old_metrics, days_to_keep)
        return {"status": "success", "message": f"Cleanup scheduled for metrics older than {days_to_keep} days"}
    except Exception as e:
        logger.error(f"Error scheduling cleanup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Analytics endpoints

@router.get("/analytics/dashboard")
async def get_analytics_dashboard(
    analytics_service: LocationProductionAnalyticsService = Depends(get_analytics_service)
):
    """
    Get analytics dashboard data.
    
    Returns comprehensive analytics data including reports, metrics, and insights.
    """
    try:
        dashboard_data = await analytics_service.get_analytics_dashboard_data()
        return JSONResponse(content=dashboard_data)
    except Exception as e:
        logger.error(f"Error getting analytics dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analytics/reports/generate")
async def generate_analytics_report(
    request: AnalyticsReportRequest,
    analytics_service: LocationProductionAnalyticsService = Depends(get_analytics_service)
):
    """
    Generate analytics report.
    
    Generates a comprehensive analytics report for the specified period and type.
    """
    try:
        if request.report_type == "accuracy":
            report = await analytics_service.generate_accuracy_report(
                request.start_date, request.end_date, request.period
            )
        elif request.report_type == "performance":
            report = await analytics_service.generate_performance_report(
                request.start_date, request.end_date, request.period
            )
        elif request.report_type == "user_experience":
            report = await analytics_service.generate_user_experience_report(
                request.start_date, request.end_date, request.period
            )
        else:
            # Generate comprehensive report
            accuracy_report = await analytics_service.generate_accuracy_report(
                request.start_date, request.end_date, request.period
            )
            performance_report = await analytics_service.generate_performance_report(
                request.start_date, request.end_date, request.period
            )
            ux_report = await analytics_service.generate_user_experience_report(
                request.start_date, request.end_date, request.period
            )
            
            report = {
                "report_id": f"comprehensive_report_{request.start_date.strftime('%Y%m%d')}_{request.end_date.strftime('%Y%m%d')}",
                "report_type": "comprehensive",
                "period": request.period,
                "start_date": request.start_date,
                "end_date": request.end_date,
                "generated_at": datetime.utcnow(),
                "reports": {
                    "accuracy": accuracy_report,
                    "performance": performance_report,
                    "user_experience": ux_report
                }
            }
        
        return JSONResponse(content={
            "status": "success",
            "message": "Analytics report generated",
            "report_id": report.report_id if isinstance(report, dict) else report.report_id,
            "report_type": report.report_type if isinstance(report, dict) else report.report_type
        })
    except Exception as e:
        logger.error(f"Error generating analytics report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/reports/{report_id}")
async def get_analytics_report(
    report_id: str,
    format: str = Query("json", description="Export format"),
    analytics_service: LocationProductionAnalyticsService = Depends(get_analytics_service)
):
    """
    Get analytics report by ID.
    
    Returns the specified analytics report in the requested format.
    """
    try:
        report_data = await analytics_service.export_report(report_id, format)
        if "error" in report_data:
            raise HTTPException(status_code=404, detail=report_data["error"])
        
        return JSONResponse(content=report_data)
    except Exception as e:
        logger.error(f"Error getting analytics report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/usage-patterns")
async def get_usage_patterns(
    start_date: Optional[datetime] = Query(None, description="Start date for analysis"),
    end_date: Optional[datetime] = Query(None, description="End date for analysis"),
    period: AnalyticsPeriod = Query(AnalyticsPeriod.DAILY, description="Analysis period"),
    analytics_service: LocationProductionAnalyticsService = Depends(get_analytics_service)
):
    """
    Get usage patterns analysis.
    
    Returns analysis of usage patterns for the specified period.
    """
    try:
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=7)
        if not end_date:
            end_date = datetime.utcnow()
        
        patterns = await analytics_service.analyze_usage_patterns(start_date, end_date, period)
        return JSONResponse(content=patterns)
    except Exception as e:
        logger.error(f"Error getting usage patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/business-metrics")
async def get_business_metrics(
    start_date: Optional[datetime] = Query(None, description="Start date for metrics"),
    end_date: Optional[datetime] = Query(None, description="End date for metrics"),
    analytics_service: LocationProductionAnalyticsService = Depends(get_analytics_service)
):
    """
    Get business metrics.
    
    Returns key business metrics for the specified period.
    """
    try:
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        metrics = await analytics_service.calculate_business_metrics(start_date, end_date)
        
        metrics_data = [
            {
                "metric_id": metric.metric_id,
                "metric_name": metric.metric_name,
                "value": metric.value,
                "unit": metric.unit,
                "trend": metric.trend,
                "change_percent": metric.change_percent,
                "period": metric.period,
                "timestamp": metric.timestamp.isoformat()
            } for metric in metrics
        ]
        
        return {"business_metrics": metrics_data}
    except Exception as e:
        logger.error(f"Error getting business metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analytics/cleanup")
async def cleanup_analytics_data(
    days_to_keep: int = Query(90, ge=1, le=365, description="Number of days to keep analytics data"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    analytics_service: LocationProductionAnalyticsService = Depends(get_analytics_service)
):
    """
    Clean up old analytics data.
    
    Removes analytics data older than the specified number of days.
    """
    try:
        background_tasks.add_task(analytics_service.cleanup_old_data, days_to_keep)
        return {"status": "success", "message": f"Analytics cleanup scheduled for data older than {days_to_keep} days"}
    except Exception as e:
        logger.error(f"Error scheduling analytics cleanup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Integration endpoints

@router.post("/start-monitoring")
async def start_monitoring(
    service: LocationProductionMonitoringService = Depends(get_monitoring_service)
):
    """
    Start background monitoring.
    
    Starts the background monitoring tasks for real-time metrics collection.
    """
    try:
        await service.start_monitoring()
        return {"status": "success", "message": "Background monitoring started"}
    except Exception as e:
        logger.error(f"Error starting monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop-monitoring")
async def stop_monitoring(
    service: LocationProductionMonitoringService = Depends(get_monitoring_service)
):
    """
    Stop background monitoring.
    
    Stops the background monitoring tasks.
    """
    try:
        await service.stop_monitoring()
        return {"status": "success", "message": "Background monitoring stopped"}
    except Exception as e:
        logger.error(f"Error stopping monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_monitoring_status(
    service: LocationProductionMonitoringService = Depends(get_monitoring_service)
):
    """
    Get monitoring service status.
    
    Returns the current status of the monitoring service including
    whether background monitoring is active.
    """
    try:
        return {
            "monitoring_active": service.monitoring_active,
            "thresholds": service.get_thresholds(),
            "metrics_counts": {
                "location_accuracy": len(service.location_accuracy_metrics),
                "service_performance": len(service.service_performance_metrics),
                "user_experience": len(service.user_experience_metrics),
                "active_alerts": len([a for a in service.active_alerts if not a.resolved]),
                "optimization_recommendations": len(service.optimization_recommendations)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting monitoring status: {e}")
        raise HTTPException(status_code=500, detail=str(e))