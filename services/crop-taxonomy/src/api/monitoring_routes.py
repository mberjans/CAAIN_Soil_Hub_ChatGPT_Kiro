"""
Monitoring API Routes for Crop Variety Recommendations

This module provides REST API endpoints for accessing monitoring data,
alerts, and system health information for the crop variety recommendation system.

Author: AI Coding Agent
Date: 2024
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field

from ..services.comprehensive_monitoring_alerting_service import (
    ComprehensiveMonitoringAlertingService,
    AlertLevel,
    get_monitoring_service
)
from ..services.monitoring_integration_service import (
    MonitoringIntegrationService,
    get_monitoring_integration_service
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/monitoring", tags=["monitoring"])


# Pydantic models for API requests/responses
class AlertResponse(BaseModel):
    """Alert response model."""
    id: str
    level: str
    title: str
    message: str
    metric_name: str
    threshold_value: float
    current_value: float
    timestamp: str
    resolved: bool
    resolved_at: Optional[str] = None
    tags: Dict[str, str] = Field(default_factory=dict)


class MetricsSummaryResponse(BaseModel):
    """Metrics summary response model."""
    timestamp: str
    recommendation_metrics: Dict[str, Any]
    system_health: Dict[str, Any]
    alerts: Dict[str, Any]


class UserFeedbackRequest(BaseModel):
    """User feedback request model."""
    request_id: str
    satisfaction_score: float = Field(..., ge=0.0, le=1.0, description="Satisfaction score from 0.0 to 1.0")
    feedback_text: Optional[str] = None
    crop_type: Optional[str] = None
    region: Optional[str] = None


class AgriculturalOutcomeRequest(BaseModel):
    """Agricultural outcome request model."""
    request_id: str
    outcome: str
    yield_improvement: Optional[float] = None
    cost_savings: Optional[float] = None
    crop_type: Optional[str] = None
    region: Optional[str] = None


class AlertChannelRequest(BaseModel):
    """Alert channel configuration request."""
    channel_type: str = Field(..., description="Type of alert channel (email, slack, webhook, sms)")
    endpoint: str = Field(..., description="Endpoint URL or configuration")


# Dependency injection
async def get_monitoring_service_dependency() -> ComprehensiveMonitoringAlertingService:
    """Get monitoring service dependency."""
    return await get_monitoring_service()


async def get_integration_service_dependency() -> MonitoringIntegrationService:
    """Get monitoring integration service dependency."""
    return await get_monitoring_integration_service()


@router.get("/health", response_model=Dict[str, Any])
async def health_check(
    monitoring_service: ComprehensiveMonitoringAlertingService = Depends(get_monitoring_service_dependency),
    integration_service: MonitoringIntegrationService = Depends(get_integration_service_dependency)
):
    """
    Health check endpoint for monitoring system.
    
    Returns the current health status of the monitoring system including
    service availability, active monitoring status, and recent metrics.
    """
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "monitoring_service": {
                "available": monitoring_service is not None,
                "monitoring_active": monitoring_service.monitoring_active if monitoring_service else False,
                "prometheus_available": monitoring_service.registry is not None if monitoring_service else False,
                "redis_available": monitoring_service.redis_client is not None if monitoring_service else False,
                "database_available": monitoring_service.db_session is not None if monitoring_service else False
            },
            "integration_service": {
                "available": integration_service is not None,
                "integration_active": integration_service.integration_active if integration_service else False
            }
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/metrics/summary", response_model=MetricsSummaryResponse)
async def get_metrics_summary(
    monitoring_service: ComprehensiveMonitoringAlertingService = Depends(get_monitoring_service_dependency)
):
    """
    Get comprehensive metrics summary.
    
    Returns a summary of all monitoring metrics including recommendation
    performance, system health, and alert status.
    """
    try:
        if not monitoring_service:
            raise HTTPException(status_code=503, detail="Monitoring service not available")
        
        summary = await monitoring_service.get_metrics_summary()
        return MetricsSummaryResponse(**summary)
        
    except Exception as e:
        logger.error(f"Error getting metrics summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics summary: {str(e)}")


@router.get("/metrics/prometheus")
async def get_prometheus_metrics(
    monitoring_service: ComprehensiveMonitoringAlertingService = Depends(get_monitoring_service_dependency)
):
    """
    Get Prometheus metrics in text format.
    
    Returns metrics in Prometheus exposition format for scraping by Prometheus server.
    """
    try:
        if not monitoring_service:
            raise HTTPException(status_code=503, detail="Monitoring service not available")
        
        metrics_text = await monitoring_service.get_prometheus_metrics()
        return PlainTextResponse(content=metrics_text, media_type="text/plain")
        
    except Exception as e:
        logger.error(f"Error getting Prometheus metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get Prometheus metrics: {str(e)}")


@router.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(
    level: Optional[str] = Query(None, description="Filter by alert level (info, warning, critical)"),
    resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of alerts to return"),
    monitoring_service: ComprehensiveMonitoringAlertingService = Depends(get_monitoring_service_dependency)
):
    """
    Get system alerts.
    
    Returns a list of system alerts with optional filtering by level and resolution status.
    """
    try:
        if not monitoring_service:
            raise HTTPException(status_code=503, detail="Monitoring service not available")
        
        with monitoring_service.lock:
            alerts = list(monitoring_service.alerts)
        
        # Apply filters
        if level:
            try:
                alert_level = AlertLevel(level)
                alerts = [alert for alert in alerts if alert.level == alert_level]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid alert level: {level}")
        
        if resolved is not None:
            alerts = [alert for alert in alerts if alert.resolved == resolved]
        
        # Limit results
        alerts = alerts[-limit:] if limit else alerts
        
        # Convert to response format
        alert_responses = []
        for alert in alerts:
            alert_responses.append(AlertResponse(
                id=alert.id,
                level=alert.level.value,
                title=alert.title,
                message=alert.message,
                metric_name=alert.metric_name,
                threshold_value=alert.threshold_value,
                current_value=alert.current_value,
                timestamp=alert.timestamp.isoformat(),
                resolved=alert.resolved,
                resolved_at=alert.resolved_at.isoformat() if alert.resolved_at else None,
                tags=alert.tags
            ))
        
        return alert_responses
        
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    monitoring_service: ComprehensiveMonitoringAlertingService = Depends(get_monitoring_service_dependency)
):
    """
    Resolve an alert.
    
    Marks the specified alert as resolved.
    """
    try:
        if not monitoring_service:
            raise HTTPException(status_code=503, detail="Monitoring service not available")
        
        success = await monitoring_service.resolve_alert(alert_id)
        
        if success:
            return {"message": f"Alert {alert_id} resolved successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving alert: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to resolve alert: {str(e)}")


@router.post("/feedback")
async def record_user_feedback(
    feedback_request: UserFeedbackRequest,
    background_tasks: BackgroundTasks,
    integration_service: MonitoringIntegrationService = Depends(get_integration_service_dependency)
):
    """
    Record user feedback for a recommendation.
    
    Records user satisfaction feedback for a specific recommendation request.
    """
    try:
        if not integration_service:
            raise HTTPException(status_code=503, detail="Integration service not available")
        
        # Record feedback in background
        background_tasks.add_task(
            integration_service.record_user_feedback,
            feedback_request.request_id,
            feedback_request.crop_type or "unknown",
            feedback_request.region or "unknown",
            feedback_request.satisfaction_score,
            feedback_request.feedback_text
        )
        
        return {"message": "User feedback recorded successfully"}
        
    except Exception as e:
        logger.error(f"Error recording user feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to record user feedback: {str(e)}")


@router.post("/outcomes")
async def record_agricultural_outcome(
    outcome_request: AgriculturalOutcomeRequest,
    background_tasks: BackgroundTasks,
    integration_service: MonitoringIntegrationService = Depends(get_integration_service_dependency)
):
    """
    Record agricultural outcome for a recommendation.
    
    Records the actual agricultural outcome (success/failure) and any
    measurable improvements from following a recommendation.
    """
    try:
        if not integration_service:
            raise HTTPException(status_code=503, detail="Integration service not available")
        
        # Record outcome in background
        background_tasks.add_task(
            integration_service.record_agricultural_outcome,
            outcome_request.request_id,
            outcome_request.crop_type or "unknown",
            outcome_request.region or "unknown",
            outcome_request.outcome,
            outcome_request.yield_improvement,
            outcome_request.cost_savings
        )
        
        return {"message": "Agricultural outcome recorded successfully"}
        
    except Exception as e:
        logger.error(f"Error recording agricultural outcome: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to record agricultural outcome: {str(e)}")


@router.get("/performance", response_model=Dict[str, Any])
async def get_performance_summary(
    integration_service: MonitoringIntegrationService = Depends(get_integration_service_dependency)
):
    """
    Get operation performance summary.
    
    Returns performance metrics for all monitored operations including
    response times, error rates, and throughput.
    """
    try:
        if not integration_service:
            raise HTTPException(status_code=503, detail="Integration service not available")
        
        performance_summary = await integration_service.get_operation_performance_summary()
        return performance_summary
        
    except Exception as e:
        logger.error(f"Error getting performance summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get performance summary: {str(e)}")


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_dashboard_data(
    integration_service: MonitoringIntegrationService = Depends(get_integration_service_dependency)
):
    """
    Get comprehensive monitoring dashboard data.
    
    Returns all data needed for the monitoring dashboard including
    metrics, alerts, performance data, and system status.
    """
    try:
        if not integration_service:
            raise HTTPException(status_code=503, detail="Integration service not available")
        
        dashboard_data = await integration_service.get_monitoring_dashboard_data()
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")


@router.post("/channels")
async def add_alert_channel(
    channel_request: AlertChannelRequest,
    monitoring_service: ComprehensiveMonitoringAlertingService = Depends(get_monitoring_service_dependency)
):
    """
    Add an alert notification channel.
    
    Configures a new alert notification channel for sending alerts
    to external systems (email, Slack, webhooks, SMS).
    """
    try:
        if not monitoring_service:
            raise HTTPException(status_code=503, detail="Monitoring service not available")
        
        monitoring_service.add_alert_channel(
            channel_request.channel_type,
            channel_request.endpoint
        )
        
        return {"message": f"Alert channel {channel_request.channel_type} added successfully"}
        
    except Exception as e:
        logger.error(f"Error adding alert channel: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add alert channel: {str(e)}")


@router.get("/status", response_model=Dict[str, Any])
async def get_system_status(
    monitoring_service: ComprehensiveMonitoringAlertingService = Depends(get_monitoring_service_dependency),
    integration_service: MonitoringIntegrationService = Depends(get_integration_service_dependency)
):
    """
    Get comprehensive system status.
    
    Returns the current status of all monitoring components and services.
    """
    try:
        status = {
            "timestamp": datetime.utcnow().isoformat(),
            "monitoring_service": {
                "available": monitoring_service is not None,
                "monitoring_active": monitoring_service.monitoring_active if monitoring_service else False,
                "prometheus_available": monitoring_service.registry is not None if monitoring_service else False,
                "redis_available": monitoring_service.redis_client is not None if monitoring_service else False,
                "database_available": monitoring_service.db_session is not None if monitoring_service else False,
                "alert_channels": len(monitoring_service.alert_channels.get("webhook", [])) if monitoring_service else 0
            },
            "integration_service": {
                "available": integration_service is not None,
                "integration_active": integration_service.integration_active if integration_service else False,
                "monitored_operations": len(integration_service.operation_times) if integration_service else 0
            },
            "thresholds": monitoring_service.thresholds if monitoring_service else {}
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")


@router.post("/initialize")
async def initialize_monitoring(
    background_tasks: BackgroundTasks,
    integration_service: MonitoringIntegrationService = Depends(get_integration_service_dependency)
):
    """
    Initialize monitoring services.
    
    Initializes the monitoring integration service and starts background monitoring.
    """
    try:
        if not integration_service:
            raise HTTPException(status_code=503, detail="Integration service not available")
        
        # Initialize in background
        background_tasks.add_task(integration_service.initialize)
        
        return {"message": "Monitoring initialization started"}
        
    except Exception as e:
        logger.error(f"Error initializing monitoring: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize monitoring: {str(e)}")


# Health check endpoint for load balancers
@router.get("/ping")
async def ping():
    """Simple ping endpoint for health checks."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}