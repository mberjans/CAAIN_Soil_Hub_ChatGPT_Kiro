"""
API routes for performance monitoring service.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from typing import List, Dict, Any, Optional
import logging

from src.services.performance_monitoring_service import (
    PerformanceMonitoringService, MonitoringConfiguration, PerformanceSnapshot,
    PerformanceAlert, PerformanceTrend, PerformanceMetric, AlertLevel
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/monitoring", tags=["performance-monitoring"])


# Dependency injection
async def get_monitoring_service() -> PerformanceMonitoringService:
    return PerformanceMonitoringService()


@router.post("/start")
async def start_monitoring(
    equipment_id: str = Query(..., description="Equipment identifier"),
    monitoring_frequency_minutes: int = Query(15, ge=1, le=1440, description="Monitoring frequency in minutes"),
    data_retention_days: int = Query(30, ge=1, le=365, description="Data retention period in days"),
    service: PerformanceMonitoringService = Depends(get_monitoring_service)
):
    """
    Start performance monitoring for equipment.
    
    This endpoint initiates real-time performance monitoring for specified equipment
    with configurable parameters for monitoring frequency, data retention, and alerting.
    
    **Monitoring Features:**
    - Real-time performance data collection
    - Automated alert generation based on thresholds
    - Performance trend analysis
    - Maintenance status tracking
    - Efficiency monitoring
    
    **Configurable Parameters:**
    - Monitoring frequency (1-1440 minutes)
    - Data retention period (1-365 days)
    - Custom alert thresholds
    - Notification methods
    
    **Default Alert Thresholds:**
    - Application Accuracy: Critical < 0.6, Warning < 0.75, Info < 0.85
    - Coverage Uniformity: Critical < 0.6, Warning < 0.75, Info < 0.85
    - Speed Efficiency: Critical < 0.5, Warning < 0.65, Info < 0.8
    - Fuel Efficiency: Critical < 0.5, Warning < 0.65, Info < 0.8
    - Labor Efficiency: Critical < 0.5, Warning < 0.65, Info < 0.8
    - Maintenance Efficiency: Critical < 0.5, Warning < 0.65, Info < 0.8
    - Overall Efficiency: Critical < 0.6, Warning < 0.75, Info < 0.85
    - Downtime Hours: Critical > 24, Warning > 12, Info > 4
    - Maintenance Cost: Critical > 2000, Warning > 1000, Info > 500
    
    **Response:**
    - Monitoring status confirmation
    - Configuration details
    - Initial performance snapshot
    """
    try:
        logger.info(f"Starting performance monitoring for equipment {equipment_id}")
        
        # Create monitoring configuration
        config = MonitoringConfiguration(
            equipment_id=equipment_id,
            monitoring_enabled=True,
            alert_thresholds=alert_thresholds or {},
            monitoring_frequency_minutes=monitoring_frequency_minutes,
            data_retention_days=data_retention_days,
            alert_notifications=alert_notifications or ["log", "email"]
        )
        
        # Start monitoring
        success = await service.start_monitoring(equipment_id, config)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to start monitoring")
        
        # Get initial performance snapshot
        initial_snapshot = await service.get_current_performance(equipment_id)
        
        return {
            "equipment_id": equipment_id,
            "monitoring_started": success,
            "configuration": {
                "monitoring_frequency_minutes": monitoring_frequency_minutes,
                "data_retention_days": data_retention_days,
                "alert_thresholds": alert_thresholds,
                "alert_notifications": alert_notifications
            },
            "initial_snapshot": initial_snapshot.dict() if initial_snapshot else None,
            "message": "Performance monitoring started successfully"
        }
        
    except Exception as e:
        logger.error(f"Error starting monitoring for equipment {equipment_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start monitoring: {str(e)}")


@router.post("/stop")
async def stop_monitoring(
    equipment_id: str = Query(..., description="Equipment identifier"),
    service: PerformanceMonitoringService = Depends(get_monitoring_service)
):
    """
    Stop performance monitoring for equipment.
    
    This endpoint stops real-time performance monitoring for the specified equipment
    and cleans up associated resources.
    
    **Response:**
    - Monitoring stop confirmation
    - Final performance summary
    - Data retention information
    """
    try:
        logger.info(f"Stopping performance monitoring for equipment {equipment_id}")
        
        # Get final performance snapshot
        final_snapshot = await service.get_current_performance(equipment_id)
        
        # Stop monitoring
        success = await service.stop_monitoring(equipment_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to stop monitoring")
        
        return {
            "equipment_id": equipment_id,
            "monitoring_stopped": success,
            "final_snapshot": final_snapshot.dict() if final_snapshot else None,
            "message": "Performance monitoring stopped successfully"
        }
        
    except Exception as e:
        logger.error(f"Error stopping monitoring for equipment {equipment_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop monitoring: {str(e)}")


@router.get("/status/{equipment_id}")
async def get_monitoring_status(
    equipment_id: str,
    service: PerformanceMonitoringService = Depends(get_monitoring_service)
):
    """
    Get monitoring status for equipment.
    
    Returns current monitoring status including configuration, data points,
    active alerts, and last update timestamp.
    """
    try:
        status = await service.get_monitoring_status(equipment_id)
        return status
        
    except Exception as e:
        logger.error(f"Error getting monitoring status for equipment {equipment_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get monitoring status: {str(e)}")


@router.get("/performance/{equipment_id}")
async def get_current_performance(
    equipment_id: str,
    service: PerformanceMonitoringService = Depends(get_monitoring_service)
):
    """
    Get current performance snapshot for equipment.
    
    Returns the most recent performance snapshot including:
    - Current efficiency metrics
    - Performance status
    - Active alerts
    - Efficiency trends
    - Maintenance status
    """
    try:
        snapshot = await service.get_current_performance(equipment_id)
        
        if not snapshot:
            raise HTTPException(status_code=404, detail="No performance data available")
        
        return snapshot.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current performance for equipment {equipment_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get current performance: {str(e)}")


@router.get("/history/{equipment_id}")
async def get_performance_history(
    equipment_id: str,
    hours: int = Query(24, ge=1, le=168, description="History period in hours (1-168)"),
    service: PerformanceMonitoringService = Depends(get_monitoring_service)
):
    """
    Get performance history for equipment.
    
    Returns performance snapshots for the specified time period including:
    - Historical efficiency metrics
    - Performance trends over time
    - Alert history
    - Status changes
    
    **Time Period Options:**
    - 1-24 hours: Recent performance
    - 24-72 hours: Short-term trends
    - 72-168 hours: Weekly analysis
    """
    try:
        history = await service.get_performance_history(equipment_id, hours)
        
        return {
            "equipment_id": equipment_id,
            "time_period_hours": hours,
            "snapshot_count": len(history),
            "snapshots": [snapshot.dict() for snapshot in history]
        }
        
    except Exception as e:
        logger.error(f"Error getting performance history for equipment {equipment_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get performance history: {str(e)}")


@router.get("/alerts/{equipment_id}")
async def get_active_alerts(
    equipment_id: str,
    alert_level: Optional[AlertLevel] = Query(None, description="Filter by alert level"),
    acknowledged: Optional[bool] = Query(None, description="Filter by acknowledgment status"),
    service: PerformanceMonitoringService = Depends(get_monitoring_service)
):
    """
    Get active alerts for equipment.
    
    Returns current active alerts with optional filtering by:
    - Alert level (info, warning, critical, emergency)
    - Acknowledgment status
    - Metric type
    
    **Alert Levels:**
    - INFO: Informational alerts for monitoring
    - WARNING: Performance below optimal levels
    - CRITICAL: Performance significantly degraded
    - EMERGENCY: Immediate attention required
    """
    try:
        alerts = await service.get_active_alerts(equipment_id)
        
        # Apply filters
        if alert_level:
            alerts = [alert for alert in alerts if alert.alert_level == alert_level]
        
        if acknowledged is not None:
            alerts = [alert for alert in alerts if alert.acknowledged == acknowledged]
        
        return {
            "equipment_id": equipment_id,
            "alert_count": len(alerts),
            "alerts": [alert.dict() for alert in alerts]
        }
        
    except Exception as e:
        logger.error(f"Error getting active alerts for equipment {equipment_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get active alerts: {str(e)}")


@router.post("/alerts/{equipment_id}/acknowledge")
async def acknowledge_alert(
    equipment_id: str,
    alert_id: str = Query(..., description="Alert identifier"),
    service: PerformanceMonitoringService = Depends(get_monitoring_service)
):
    """
    Acknowledge an alert.
    
    Marks an alert as acknowledged to indicate that it has been reviewed
    and appropriate action is being taken.
    """
    try:
        success = await service.acknowledge_alert(equipment_id, alert_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {
            "equipment_id": equipment_id,
            "alert_id": alert_id,
            "acknowledged": success,
            "message": "Alert acknowledged successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error acknowledging alert {alert_id} for equipment {equipment_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge alert: {str(e)}")


@router.get("/trends/{equipment_id}")
async def get_performance_trend(
    equipment_id: str,
    metric: PerformanceMetric = Query(..., description="Performance metric to analyze"),
    days: int = Query(7, ge=1, le=30, description="Trend analysis period in days"),
    service: PerformanceMonitoringService = Depends(get_monitoring_service)
):
    """
    Get performance trend analysis for a specific metric.
    
    Provides detailed trend analysis including:
    - Historical data points
    - Trend direction (improving, declining, stable)
    - Trend strength (0-1)
    - Confidence level
    - Short-term forecast
    
    **Available Metrics:**
    - APPLICATION_ACCURACY: Application precision
    - COVERAGE_UNIFORMITY: Coverage consistency
    - SPEED_EFFICIENCY: Operational speed
    - FUEL_EFFICIENCY: Fuel consumption efficiency
    - LABOR_EFFICIENCY: Labor utilization
    - MAINTENANCE_EFFICIENCY: Maintenance effectiveness
    - OVERALL_EFFICIENCY: Overall performance
    - DOWNTIME_HOURS: Equipment downtime
    - MAINTENANCE_COST: Maintenance expenses
    """
    try:
        trend = await service.get_performance_trend(equipment_id, metric, days)
        
        if not trend:
            raise HTTPException(status_code=404, detail="Insufficient data for trend analysis")
        
        return trend.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting performance trend for equipment {equipment_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get performance trend: {str(e)}")


@router.get("/dashboard/{equipment_id}")
async def get_monitoring_dashboard(
    equipment_id: str,
    service: PerformanceMonitoringService = Depends(get_monitoring_service)
):
    """
    Get comprehensive monitoring dashboard for equipment.
    
    Returns a complete dashboard view including:
    - Current performance status
    - Recent performance history
    - Active alerts summary
    - Performance trends
    - Maintenance status
    - Efficiency metrics overview
    
    This endpoint provides all the data needed for a monitoring dashboard UI.
    """
    try:
        # Get current performance
        current_performance = await service.get_current_performance(equipment_id)
        
        # Get performance history (last 24 hours)
        performance_history = await service.get_performance_history(equipment_id, 24)
        
        # Get active alerts
        active_alerts = await service.get_active_alerts(equipment_id)
        
        # Get monitoring status
        monitoring_status = await service.get_monitoring_status(equipment_id)
        
        # Get trends for key metrics
        key_metrics = [
            PerformanceMetric.OVERALL_EFFICIENCY,
            PerformanceMetric.APPLICATION_ACCURACY,
            PerformanceMetric.FUEL_EFFICIENCY,
            PerformanceMetric.MAINTENANCE_EFFICIENCY
        ]
        
        trends = {}
        for metric in key_metrics:
            trend = await service.get_performance_trend(equipment_id, metric, 7)
            if trend:
                trends[metric.value] = trend.dict()
        
        return {
            "equipment_id": equipment_id,
            "monitoring_status": monitoring_status,
            "current_performance": current_performance.dict() if current_performance else None,
            "performance_history": {
                "time_period_hours": 24,
                "snapshot_count": len(performance_history),
                "snapshots": [snapshot.dict() for snapshot in performance_history]
            },
            "active_alerts": {
                "total_count": len(active_alerts),
                "critical_count": len([a for a in active_alerts if a.alert_level == AlertLevel.CRITICAL]),
                "warning_count": len([a for a in active_alerts if a.alert_level == AlertLevel.WARNING]),
                "info_count": len([a for a in active_alerts if a.alert_level == AlertLevel.INFO]),
                "alerts": [alert.dict() for alert in active_alerts]
            },
            "performance_trends": trends,
            "dashboard_summary": {
                "overall_status": current_performance.status.value if current_performance else "unknown",
                "monitoring_active": monitoring_status["monitoring_enabled"],
                "data_points": monitoring_status["data_points"],
                "last_update": monitoring_status["last_update"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting monitoring dashboard for equipment {equipment_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get monitoring dashboard: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for performance monitoring service."""
    return {"status": "healthy", "service": "performance-monitoring"}