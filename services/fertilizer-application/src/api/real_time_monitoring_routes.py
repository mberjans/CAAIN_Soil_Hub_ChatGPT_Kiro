"""
API routes for real-time application monitoring and adjustment.

This module provides REST API endpoints for real-time monitoring of fertilizer
application processes, including data collection, adjustment recommendations,
alert management, and quality control.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta

from src.services.real_time_monitoring_service import RealTimeMonitoringService
from src.models.application_monitoring_models import (
    ApplicationSession, MonitoringConfiguration, ApplicationMonitoringData,
    RealTimeAdjustment, MonitoringAlert, SensorData, QualityControlCheck,
    MonitoringSummary, ApplicationStatus, AdjustmentType, MonitoringMetric,
    AlertSeverity, SensorType
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/real-time-monitoring", tags=["real-time-monitoring"])


# Dependency injection
async def get_monitoring_service() -> RealTimeMonitoringService:
    return RealTimeMonitoringService()


@router.post("/sessions/start")
async def start_monitoring_session(
    session_data: Dict[str, Any],
    config_data: Dict[str, Any],
    service: RealTimeMonitoringService = Depends(get_monitoring_service)
):
    """
    Start real-time monitoring for a fertilizer application session.
    
    This endpoint initiates comprehensive real-time monitoring including:
    - Application rate monitoring
    - Coverage uniformity tracking
    - Environmental condition monitoring
    - Equipment status monitoring
    - Real-time adjustment recommendations
    - Quality control checks
    
    **Request Body:**
    ```json
    {
        "session_data": {
            "field_id": "field_123",
            "equipment_id": "equipment_456",
            "operator_id": "operator_789",
            "fertilizer_type": "Urea",
            "target_rate": 150.0,
            "application_method": "broadcast",
            "planned_start": "2024-01-15T08:00:00Z",
            "planned_end": "2024-01-15T12:00:00Z",
            "total_area": 40.0
        },
        "config_data": {
            "monitoring_enabled": true,
            "update_frequency_seconds": 5,
            "alert_thresholds": {
                "rate_deviation": {"high": 10.0, "critical": 20.0},
                "coverage_uniformity": {"medium": 0.8, "high": 0.75},
                "wind_speed": {"medium": 10.0, "high": 15.0}
            },
            "adjustment_thresholds": {
                "rate_deviation": 5.0,
                "coverage_uniformity": 0.85,
                "wind_speed": 10.0
            },
            "enabled_sensors": ["flow_meter", "pressure_sensor", "weather_station", "gps_sensor"],
            "quality_checks_enabled": true,
            "quality_check_frequency": 300,
            "notification_methods": ["log", "email", "sms"]
        }
    }
    ```
    
    **Response:**
    - Monitoring session confirmation
    - Initial configuration
    - Monitoring status
    """
    try:
        logger.info("Starting real-time monitoring session")
        
        # Create application session
        session = ApplicationSession(**session_data)
        
        # Create monitoring configuration
        config = MonitoringConfiguration(**config_data)
        
        # Start monitoring
        success = await service.start_monitoring(session, config)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to start monitoring session")
        
        # Get initial monitoring status
        status = await service.get_monitoring_status(session.session_id)
        
        return {
            "session_id": session.session_id,
            "monitoring_started": success,
            "session": session.dict(),
            "configuration": config.dict(),
            "status": status,
            "message": "Real-time monitoring session started successfully"
        }
        
    except Exception as e:
        logger.error(f"Error starting monitoring session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start monitoring session: {str(e)}")


@router.post("/sessions/{session_id}/stop")
async def stop_monitoring_session(
    session_id: str,
    service: RealTimeMonitoringService = Depends(get_monitoring_service)
):
    """
    Stop real-time monitoring for a session.
    
    This endpoint stops all monitoring activities and provides a final summary
    of the monitoring session including performance metrics and recommendations.
    
    **Response:**
    - Monitoring stop confirmation
    - Final monitoring summary
    - Performance metrics
    - Recommendations for future applications
    """
    try:
        logger.info(f"Stopping monitoring session {session_id}")
        
        # Get final summary before stopping
        summary = await service.get_monitoring_summary(session_id)
        
        # Stop monitoring
        success = await service.stop_monitoring(session_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to stop monitoring session")
        
        return {
            "session_id": session_id,
            "monitoring_stopped": success,
            "final_summary": summary.dict() if summary else None,
            "message": "Real-time monitoring session stopped successfully"
        }
        
    except Exception as e:
        logger.error(f"Error stopping monitoring session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop monitoring session: {str(e)}")


@router.get("/sessions/{session_id}/status")
async def get_session_status(
    session_id: str,
    service: RealTimeMonitoringService = Depends(get_monitoring_service)
):
    """
    Get current monitoring status for a session.
    
    Returns comprehensive status information including:
    - Monitoring state
    - Data collection statistics
    - Active adjustments and alerts
    - Quality control status
    - Equipment status
    """
    try:
        status = await service.get_monitoring_status(session_id)
        return status
        
    except Exception as e:
        logger.error(f"Error getting session status for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get session status: {str(e)}")


@router.get("/sessions/{session_id}/current-data")
async def get_current_monitoring_data(
    session_id: str,
    service: RealTimeMonitoringService = Depends(get_monitoring_service)
):
    """
    Get current real-time monitoring data for a session.
    
    Returns the most recent monitoring data including:
    - Application rate and deviation
    - Coverage uniformity
    - Environmental conditions
    - Equipment status
    - Quality indicators
    """
    try:
        data = await service.get_current_monitoring_data(session_id)
        
        if not data:
            raise HTTPException(status_code=404, detail="No monitoring data available")
        
        return data.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current monitoring data for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get current monitoring data: {str(e)}")


@router.get("/sessions/{session_id}/history")
async def get_monitoring_history(
    session_id: str,
    minutes: int = Query(60, ge=1, le=1440, description="History period in minutes"),
    service: RealTimeMonitoringService = Depends(get_monitoring_service)
):
    """
    Get monitoring history for a session.
    
    Returns historical monitoring data for the specified time period including:
    - Time series data points
    - Performance trends
    - Environmental condition changes
    - Equipment status history
    
    **Time Period Options:**
    - 1-60 minutes: Recent data
    - 60-240 minutes: Short-term trends
    - 240-1440 minutes: Long-term analysis
    """
    try:
        history = await service.get_monitoring_history(session_id, minutes)
        
        return {
            "session_id": session_id,
            "time_period_minutes": minutes,
            "data_points": len(history),
            "history": [data.dict() for data in history]
        }
        
    except Exception as e:
        logger.error(f"Error getting monitoring history for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get monitoring history: {str(e)}")


@router.get("/sessions/{session_id}/adjustments")
async def get_active_adjustments(
    session_id: str,
    adjustment_type: Optional[AdjustmentType] = Query(None, description="Filter by adjustment type"),
    priority: Optional[int] = Query(None, ge=1, le=5, description="Filter by priority level"),
    service: RealTimeMonitoringService = Depends(get_monitoring_service)
):
    """
    Get active adjustment recommendations for a session.
    
    Returns current adjustment recommendations with optional filtering by:
    - Adjustment type (rate, coverage, weather, etc.)
    - Priority level (1-5)
    - Implementation status
    
    **Adjustment Types:**
    - RATE_ADJUSTMENT: Application rate modifications
    - COVERAGE_ADJUSTMENT: Coverage uniformity improvements
    - WEATHER_ADJUSTMENT: Weather-related adjustments
    - METHOD_ADJUSTMENT: Application method changes
    - QUALITY_ADJUSTMENT: Quality control adjustments
    """
    try:
        adjustments = await service.get_active_adjustments(session_id)
        
        # Apply filters
        if adjustment_type:
            adjustments = [adj for adj in adjustments if adj.adjustment_type == adjustment_type]
        
        if priority:
            adjustments = [adj for adj in adjustments if adj.priority == priority]
        
        return {
            "session_id": session_id,
            "adjustment_count": len(adjustments),
            "adjustments": [adj.dict() for adj in adjustments]
        }
        
    except Exception as e:
        logger.error(f"Error getting active adjustments for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get active adjustments: {str(e)}")


@router.post("/sessions/{session_id}/adjustments/{adjustment_id}/implement")
async def implement_adjustment(
    session_id: str,
    adjustment_id: str,
    service: RealTimeMonitoringService = Depends(get_monitoring_service)
):
    """
    Implement an adjustment recommendation.
    
    Marks an adjustment as implemented and records the implementation timestamp.
    This endpoint is typically called by the operator or automated system when
    an adjustment recommendation is acted upon.
    
    **Response:**
    - Implementation confirmation
    - Updated adjustment status
    - Implementation timestamp
    """
    try:
        success = await service.implement_adjustment(session_id, adjustment_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Adjustment not found")
        
        return {
            "session_id": session_id,
            "adjustment_id": adjustment_id,
            "implemented": success,
            "implemented_at": datetime.now().isoformat(),
            "message": "Adjustment implemented successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error implementing adjustment {adjustment_id} for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to implement adjustment: {str(e)}")


@router.get("/sessions/{session_id}/alerts")
async def get_active_alerts(
    session_id: str,
    severity: Optional[AlertSeverity] = Query(None, description="Filter by alert severity"),
    acknowledged: Optional[bool] = Query(None, description="Filter by acknowledgment status"),
    resolved: Optional[bool] = Query(None, description="Filter by resolution status"),
    service: RealTimeMonitoringService = Depends(get_monitoring_service)
):
    """
    Get active alerts for a session.
    
    Returns current alerts with optional filtering by:
    - Alert severity (low, medium, high, critical)
    - Acknowledgment status
    - Resolution status
    - Alert type
    
    **Alert Severity Levels:**
    - LOW: Informational alerts
    - MEDIUM: Performance below optimal
    - HIGH: Significant performance issues
    - CRITICAL: Immediate attention required
    """
    try:
        alerts = await service.get_active_alerts(session_id)
        
        # Apply filters
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
        
        if acknowledged is not None:
            alerts = [alert for alert in alerts if alert.acknowledged == acknowledged]
        
        if resolved is not None:
            alerts = [alert for alert in alerts if alert.resolved == resolved]
        
        return {
            "session_id": session_id,
            "alert_count": len(alerts),
            "alerts": [alert.dict() for alert in alerts]
        }
        
    except Exception as e:
        logger.error(f"Error getting active alerts for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get active alerts: {str(e)}")


@router.post("/sessions/{session_id}/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    session_id: str,
    alert_id: str,
    service: RealTimeMonitoringService = Depends(get_monitoring_service)
):
    """
    Acknowledge an alert.
    
    Marks an alert as acknowledged to indicate that it has been reviewed
    and appropriate action is being taken.
    """
    try:
        success = await service.acknowledge_alert(session_id, alert_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {
            "session_id": session_id,
            "alert_id": alert_id,
            "acknowledged": success,
            "acknowledged_at": datetime.now().isoformat(),
            "message": "Alert acknowledged successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error acknowledging alert {alert_id} for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge alert: {str(e)}")


@router.post("/sessions/{session_id}/alerts/{alert_id}/resolve")
async def resolve_alert(
    session_id: str,
    alert_id: str,
    service: RealTimeMonitoringService = Depends(get_monitoring_service)
):
    """
    Resolve an alert.
    
    Marks an alert as resolved to indicate that the underlying issue
    has been addressed.
    """
    try:
        success = await service.resolve_alert(session_id, alert_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {
            "session_id": session_id,
            "alert_id": alert_id,
            "resolved": success,
            "resolved_at": datetime.now().isoformat(),
            "message": "Alert resolved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving alert {alert_id} for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to resolve alert: {str(e)}")


@router.get("/sessions/{session_id}/quality-checks")
async def get_quality_checks(
    session_id: str,
    passed_only: Optional[bool] = Query(None, description="Filter by pass/fail status"),
    service: RealTimeMonitoringService = Depends(get_monitoring_service)
):
    """
    Get quality control check results for a session.
    
    Returns quality control check history including:
    - Check results and scores
    - Quality deviations
    - Recommendations
    - Corrective actions
    
    **Quality Check Types:**
    - Rate accuracy checks
    - Coverage uniformity checks
    - Environmental compliance checks
    - Equipment performance checks
    """
    try:
        # Get quality checks from service (this would need to be implemented)
        # For now, return empty list as placeholder
        quality_checks = []
        
        # Apply filters
        if passed_only is not None:
            quality_checks = [qc for qc in quality_checks if qc.passed == passed_only]
        
        return {
            "session_id": session_id,
            "quality_check_count": len(quality_checks),
            "quality_checks": [qc.dict() for qc in quality_checks]
        }
        
    except Exception as e:
        logger.error(f"Error getting quality checks for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get quality checks: {str(e)}")


@router.get("/sessions/{session_id}/summary")
async def get_monitoring_summary(
    session_id: str,
    service: RealTimeMonitoringService = Depends(get_monitoring_service)
):
    """
    Get comprehensive monitoring summary for a session.
    
    Returns detailed summary including:
    - Monitoring duration and statistics
    - Performance metrics
    - Adjustment and alert summaries
    - Quality control results
    - Environmental compliance
    - Recommendations for improvement
    
    This endpoint provides all the data needed for comprehensive reporting
    and analysis of the application session.
    """
    try:
        summary = await service.get_monitoring_summary(session_id)
        
        if not summary:
            raise HTTPException(status_code=404, detail="No monitoring data available for session")
        
        return summary.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting monitoring summary for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get monitoring summary: {str(e)}")


@router.get("/sessions/{session_id}/dashboard")
async def get_monitoring_dashboard(
    session_id: str,
    service: RealTimeMonitoringService = Depends(get_monitoring_service)
):
    """
    Get comprehensive monitoring dashboard for a session.
    
    Returns a complete dashboard view including:
    - Current monitoring status
    - Real-time data
    - Active adjustments and alerts
    - Performance trends
    - Quality control status
    - Environmental conditions
    
    This endpoint provides all the data needed for a real-time monitoring dashboard UI.
    """
    try:
        # Get current data
        current_data = await service.get_current_monitoring_data(session_id)
        
        # Get recent history (last hour)
        history = await service.get_monitoring_history(session_id, 60)
        
        # Get active adjustments
        adjustments = await service.get_active_adjustments(session_id)
        
        # Get active alerts
        alerts = await service.get_active_alerts(session_id)
        
        # Get monitoring status
        status = await service.get_monitoring_status(session_id)
        
        # Get summary
        summary = await service.get_monitoring_summary(session_id)
        
        return {
            "session_id": session_id,
            "monitoring_status": status,
            "current_data": current_data.dict() if current_data else None,
            "recent_history": {
                "time_period_minutes": 60,
                "data_points": len(history),
                "data": [data.dict() for data in history]
            },
            "active_adjustments": {
                "count": len(adjustments),
                "high_priority": len([adj for adj in adjustments if adj.priority <= 2]),
                "adjustments": [adj.dict() for adj in adjustments]
            },
            "active_alerts": {
                "total_count": len(alerts),
                "critical_count": len([a for a in alerts if a.severity == AlertSeverity.CRITICAL]),
                "high_count": len([a for a in alerts if a.severity == AlertSeverity.HIGH]),
                "medium_count": len([a for a in alerts if a.severity == AlertSeverity.MEDIUM]),
                "low_count": len([a for a in alerts if a.severity == AlertSeverity.LOW]),
                "alerts": [alert.dict() for alert in alerts]
            },
            "summary": summary.dict() if summary else None,
            "dashboard_summary": {
                "monitoring_active": status.get("monitoring_enabled", False),
                "session_status": status.get("session_status", "unknown"),
                "data_points": status.get("data_points", 0),
                "last_update": status.get("last_update"),
                "overall_quality": summary.average_quality_score if summary else 0,
                "rate_accuracy": summary.average_rate_accuracy if summary else 0,
                "coverage_uniformity": summary.average_coverage_uniformity if summary else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting monitoring dashboard for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get monitoring dashboard: {str(e)}")


@router.post("/sessions/{session_id}/data")
async def submit_monitoring_data(
    session_id: str,
    data: Dict[str, Any],
    service: RealTimeMonitoringService = Depends(get_monitoring_service)
):
    """
    Submit external monitoring data for a session.
    
    This endpoint allows external systems (IoT sensors, equipment telemetry)
    to submit monitoring data for real-time processing and analysis.
    
    **Request Body:**
    ```json
    {
        "application_rate": 150.5,
        "target_rate": 150.0,
        "coverage_uniformity": 0.92,
        "speed": 6.5,
        "pressure": 32.5,
        "temperature": 72.0,
        "humidity": 65.0,
        "wind_speed": 8.5,
        "wind_direction": 180.0,
        "soil_moisture": 45.0,
        "latitude": 40.123456,
        "longitude": -95.654321,
        "elevation": 950.0,
        "equipment_status": "operational"
    }
    ```
    
    **Response:**
    - Data submission confirmation
    - Processing status
    - Generated adjustments/alerts (if any)
    """
    try:
        logger.info(f"Submitting external monitoring data for session {session_id}")
        
        # Create monitoring data object
        monitoring_data = ApplicationMonitoringData(
            application_session_id=session_id,
            equipment_id=data.get("equipment_id", "unknown"),
            field_id=data.get("field_id", "unknown"),
            **data
        )
        
        # Process the data (this would integrate with the monitoring service)
        # For now, we'll just return a confirmation
        
        return {
            "session_id": session_id,
            "data_submitted": True,
            "monitoring_data_id": monitoring_data.monitoring_id,
            "timestamp": monitoring_data.timestamp.isoformat(),
            "message": "Monitoring data submitted successfully"
        }
        
    except Exception as e:
        logger.error(f"Error submitting monitoring data for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit monitoring data: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for real-time monitoring service."""
    return {"status": "healthy", "service": "real-time-monitoring"}