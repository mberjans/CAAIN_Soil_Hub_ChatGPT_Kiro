"""
Production Monitoring API Routes

FastAPI router for production monitoring, analytics, alerting, and reporting endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta
from uuid import UUID

from ..models.production_monitoring_models import (
    ProductionMonitoringRequest,
    ProductionMonitoringResponse,
    SystemPerformanceMetrics,
    UserEngagementMetrics,
    RecommendationEffectivenessMetrics,
    AgriculturalImpactMetrics,
    ProductionHealthStatus,
    RealTimeMetrics,
    HistoricalMetrics,
    ProductionMonitoringReport,
    AlertConfigurationRequest,
    AlertConfigurationResponse,
    PerformanceThresholdRequest,
    PerformanceThresholdResponse,
    MonitoringConfigurationRequest,
    MonitoringConfigurationResponse,
    ReportGenerationRequest,
    ReportGenerationResponse
)
from ..models.production_analytics_models import (
    AnalyticsRequest,
    AnalyticsResponse,
    UsagePatternAnalysis,
    SuccessMetricsAnalysis,
    AgriculturalImpactAnalysis,
    AnalyticsReport
)
from ..models.production_alerting_models import (
    AlertRuleRequest,
    AlertRuleResponse,
    AlertMetricsRequest,
    AlertMetricsResponse,
    AlertSearchRequest,
    AlertSearchResponse
)
from ..models.production_reporting_models import (
    ReportGenerationRequest as ReportingRequest,
    ReportGenerationResponse as ReportingResponse,
    ReportHistory,
    ReportMetrics
)
from ..services.production_monitoring_service import ProductionMonitoringService
from ..services.production_analytics_service import ProductionAnalyticsService
from ..services.production_alerting_service import ProductionAlertingService
from ..services.production_reporting_service import ProductionReportingService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/production", tags=["production-monitoring"])

# Service dependency injection
async def get_production_monitoring_service() -> ProductionMonitoringService:
    """Get production monitoring service instance."""
    service = ProductionMonitoringService()
    await service.initialize()
    return service

async def get_production_analytics_service() -> ProductionAnalyticsService:
    """Get production analytics service instance."""
    service = ProductionAnalyticsService()
    await service.initialize()
    return service

async def get_production_alerting_service() -> ProductionAlertingService:
    """Get production alerting service instance."""
    service = ProductionAlertingService()
    await service.initialize()
    return service

async def get_production_reporting_service() -> ProductionReportingService:
    """Get production reporting service instance."""
    service = ProductionReportingService()
    await service.initialize()
    return service

# Production Monitoring Endpoints
@router.get("/health", response_model=ProductionHealthStatus)
async def get_production_health(
    service: ProductionMonitoringService = Depends(get_production_monitoring_service)
):
    """
    Get overall production health status.
    
    Returns comprehensive health status including:
    - System performance metrics
    - User engagement metrics
    - Recommendation effectiveness metrics
    - Active alerts
    - Overall health score
    """
    try:
        logger.info("Getting production health status")
        
        health_status = await service.get_production_health_status()
        
        logger.info("Production health status retrieved successfully")
        return health_status
        
    except Exception as e:
        logger.error(f"Error getting production health: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get production health: {str(e)}")

@router.get("/metrics/system-performance", response_model=SystemPerformanceMetrics)
async def get_system_performance_metrics(
    time_range_hours: int = Query(24, ge=1, le=168, description="Time range in hours"),
    service: ProductionMonitoringService = Depends(get_production_monitoring_service)
):
    """
    Get system performance metrics.
    
    Returns system performance data including:
    - CPU usage percentage
    - Memory usage percentage
    - Disk usage percentage
    - Network I/O statistics
    - Process count
    - Python memory usage
    """
    try:
        logger.info(f"Getting system performance metrics for {time_range_hours} hours")
        
        metrics = await service.get_system_performance_metrics(time_range_hours)
        
        logger.info("System performance metrics retrieved successfully")
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting system performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get system performance metrics: {str(e)}")

@router.get("/metrics/user-engagement", response_model=UserEngagementMetrics)
async def get_user_engagement_metrics(
    time_range_hours: int = Query(24, ge=1, le=168, description="Time range in hours"),
    service: ProductionMonitoringService = Depends(get_production_monitoring_service)
):
    """
    Get user engagement metrics.
    
    Returns user engagement data including:
    - Daily active users
    - Average session duration
    - Requests per minute
    - Feature usage statistics
    """
    try:
        logger.info(f"Getting user engagement metrics for {time_range_hours} hours")
        
        metrics = await service.get_user_engagement_metrics(time_range_hours)
        
        logger.info("User engagement metrics retrieved successfully")
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting user engagement metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get user engagement metrics: {str(e)}")

@router.get("/metrics/recommendation-effectiveness", response_model=RecommendationEffectivenessMetrics)
async def get_recommendation_effectiveness_metrics(
    time_range_hours: int = Query(24, ge=1, le=168, description="Time range in hours"),
    service: ProductionMonitoringService = Depends(get_production_monitoring_service)
):
    """
    Get recommendation effectiveness metrics.
    
    Returns recommendation effectiveness data including:
    - Recommendation accuracy percentage
    - Recommendations per day
    - User satisfaction score
    - Implementation rate percentage
    """
    try:
        logger.info(f"Getting recommendation effectiveness metrics for {time_range_hours} hours")
        
        metrics = await service.get_recommendation_effectiveness_metrics(time_range_hours)
        
        logger.info("Recommendation effectiveness metrics retrieved successfully")
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting recommendation effectiveness metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get recommendation effectiveness metrics: {str(e)}")

@router.get("/metrics/agricultural-impact", response_model=AgriculturalImpactMetrics)
async def get_agricultural_impact_metrics(
    time_range_hours: int = Query(24, ge=1, le=168, description="Time range in hours"),
    service: ProductionMonitoringService = Depends(get_production_monitoring_service)
):
    """
    Get agricultural impact metrics.
    
    Returns agricultural impact data including:
    - Total water savings in gallons
    - Number of farms with conservation practices
    - Drought risk reduction percentage
    - Total cost savings in dollars
    """
    try:
        logger.info(f"Getting agricultural impact metrics for {time_range_hours} hours")
        
        metrics = await service.get_agricultural_impact_metrics(time_range_hours)
        
        logger.info("Agricultural impact metrics retrieved successfully")
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting agricultural impact metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get agricultural impact metrics: {str(e)}")

@router.get("/metrics/real-time", response_model=RealTimeMetrics)
async def get_real_time_metrics(
    service: ProductionMonitoringService = Depends(get_production_monitoring_service)
):
    """
    Get real-time metrics.
    
    Returns current real-time metrics including:
    - Current metric values
    - Collection status
    - Timestamp
    """
    try:
        logger.info("Getting real-time metrics")
        
        metrics = await service.get_real_time_metrics()
        
        logger.info("Real-time metrics retrieved successfully")
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting real-time metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get real-time metrics: {str(e)}")

@router.get("/metrics/historical/{metric_name}", response_model=HistoricalMetrics)
async def get_historical_metrics(
    metric_name: str,
    hours: int = Query(24, ge=1, le=168, description="Time range in hours"),
    service: ProductionMonitoringService = Depends(get_production_monitoring_service)
):
    """
    Get historical metrics for a specific metric.
    
    Returns historical data points for the specified metric including:
    - Data points with timestamps
    - Time range
    - Total points count
    """
    try:
        logger.info(f"Getting historical metrics for {metric_name} over {hours} hours")
        
        metrics = await service.get_historical_metrics(metric_name, hours)
        
        logger.info(f"Historical metrics for {metric_name} retrieved successfully")
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting historical metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get historical metrics: {str(e)}")

@router.post("/report/generate", response_model=ProductionMonitoringReport)
async def generate_production_report(
    start_date: datetime = Body(..., description="Report start date"),
    end_date: datetime = Body(..., description="Report end date"),
    service: ProductionMonitoringService = Depends(get_production_monitoring_service)
):
    """
    Generate comprehensive production monitoring report.
    
    Generates a detailed report covering:
    - System performance analysis
    - User engagement trends
    - Recommendation effectiveness
    - Agricultural impact assessment
    - Performance trends
    - Summary and recommendations
    """
    try:
        logger.info(f"Generating production report from {start_date} to {end_date}")
        
        report = await service.generate_production_report(start_date, end_date)
        
        logger.info("Production report generated successfully")
        return report
        
    except Exception as e:
        logger.error(f"Error generating production report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate production report: {str(e)}")

# Production Analytics Endpoints
@router.post("/analytics/usage-patterns", response_model=UsagePatternAnalysis)
async def analyze_usage_patterns(
    start_date: datetime = Body(..., description="Analysis start date"),
    end_date: datetime = Body(..., description="Analysis end date"),
    granularity: str = Body("daily", description="Analysis granularity"),
    service: ProductionAnalyticsService = Depends(get_production_analytics_service)
):
    """
    Analyze usage patterns.
    
    Performs comprehensive usage pattern analysis including:
    - Peak usage times
    - Usage trends
    - Seasonal patterns
    - User behavior patterns
    """
    try:
        logger.info(f"Analyzing usage patterns from {start_date} to {end_date}")
        
        analysis = await service.analyze_usage_patterns(start_date, end_date, granularity)
        
        logger.info("Usage patterns analysis completed successfully")
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing usage patterns: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze usage patterns: {str(e)}")

@router.post("/analytics/success-metrics", response_model=SuccessMetricsAnalysis)
async def analyze_success_metrics(
    start_date: datetime = Body(..., description="Analysis start date"),
    end_date: datetime = Body(..., description="Analysis end date"),
    service: ProductionAnalyticsService = Depends(get_production_analytics_service)
):
    """
    Analyze success metrics.
    
    Performs comprehensive success metrics analysis including:
    - User satisfaction analysis
    - Recommendation effectiveness analysis
    - System reliability analysis
    - Business metrics analysis
    """
    try:
        logger.info(f"Analyzing success metrics from {start_date} to {end_date}")
        
        analysis = await service.analyze_success_metrics(start_date, end_date)
        
        logger.info("Success metrics analysis completed successfully")
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing success metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze success metrics: {str(e)}")

@router.post("/analytics/agricultural-impact", response_model=AgriculturalImpactAnalysis)
async def analyze_agricultural_impact(
    start_date: datetime = Body(..., description="Analysis start date"),
    end_date: datetime = Body(..., description="Analysis end date"),
    service: ProductionAnalyticsService = Depends(get_production_analytics_service)
):
    """
    Analyze agricultural impact.
    
    Performs comprehensive agricultural impact analysis including:
    - Water savings analysis
    - Cost savings analysis
    - Environmental impact analysis
    - Farm productivity analysis
    """
    try:
        logger.info(f"Analyzing agricultural impact from {start_date} to {end_date}")
        
        analysis = await service.analyze_agricultural_impact(start_date, end_date)
        
        logger.info("Agricultural impact analysis completed successfully")
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing agricultural impact: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze agricultural impact: {str(e)}")

@router.post("/analytics/comprehensive", response_model=AnalyticsReport)
async def generate_comprehensive_analytics_report(
    start_date: datetime = Body(..., description="Report start date"),
    end_date: datetime = Body(..., description="Report end date"),
    service: ProductionAnalyticsService = Depends(get_production_analytics_service)
):
    """
    Generate comprehensive analytics report.
    
    Generates a comprehensive analytics report including:
    - Usage pattern analysis
    - Success metrics analysis
    - Agricultural impact analysis
    - Generated insights
    - Report summary
    """
    try:
        logger.info(f"Generating comprehensive analytics report from {start_date} to {end_date}")
        
        report = await service.generate_comprehensive_analytics_report(start_date, end_date)
        
        logger.info("Comprehensive analytics report generated successfully")
        return report
        
    except Exception as e:
        logger.error(f"Error generating comprehensive analytics report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate comprehensive analytics report: {str(e)}")

# Production Alerting Endpoints
@router.post("/alerts/rules", response_model=AlertRuleResponse)
async def create_alert_rule(
    request: AlertRuleRequest = Body(..., description="Alert rule configuration"),
    service: ProductionAlertingService = Depends(get_production_alerting_service)
):
    """
    Create a new alert rule.
    
    Creates a new alert rule with specified conditions and actions.
    """
    try:
        logger.info(f"Creating alert rule: {request.name}")
        
        response = await service.create_alert_rule(request)
        
        logger.info(f"Alert rule creation {'successful' if response.success else 'failed'}")
        return response
        
    except Exception as e:
        logger.error(f"Error creating alert rule: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create alert rule: {str(e)}")

@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    acknowledged_by: str = Body(..., description="Who acknowledged the alert"),
    service: ProductionAlertingService = Depends(get_production_alerting_service)
):
    """
    Acknowledge an alert.
    
    Marks an alert as acknowledged by the specified user.
    """
    try:
        logger.info(f"Acknowledging alert: {alert_id}")
        
        success = await service.acknowledge_alert(alert_id, acknowledged_by)
        
        if success:
            logger.info(f"Alert {alert_id} acknowledged successfully")
            return {"success": True, "message": "Alert acknowledged successfully"}
        else:
            logger.warning(f"Failed to acknowledge alert: {alert_id}")
            raise HTTPException(status_code=404, detail="Alert not found")
        
    except Exception as e:
        logger.error(f"Error acknowledging alert: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge alert: {str(e)}")

@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    resolved_by: str = Body(..., description="Who resolved the alert"),
    service: ProductionAlertingService = Depends(get_production_alerting_service)
):
    """
    Resolve an alert.
    
    Marks an alert as resolved by the specified user.
    """
    try:
        logger.info(f"Resolving alert: {alert_id}")
        
        success = await service.resolve_alert(alert_id, resolved_by)
        
        if success:
            logger.info(f"Alert {alert_id} resolved successfully")
            return {"success": True, "message": "Alert resolved successfully"}
        else:
            logger.warning(f"Failed to resolve alert: {alert_id}")
            raise HTTPException(status_code=404, detail="Alert not found")
        
    except Exception as e:
        logger.error(f"Error resolving alert: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to resolve alert: {str(e)}")

@router.get("/alerts/active")
async def get_active_alerts(
    service: ProductionAlertingService = Depends(get_production_alerting_service)
):
    """
    Get all active alerts.
    
    Returns a list of all currently active alerts.
    """
    try:
        logger.info("Getting active alerts")
        
        alerts = await service.get_active_alerts()
        
        logger.info(f"Retrieved {len(alerts)} active alerts")
        return {"alerts": alerts, "count": len(alerts)}
        
    except Exception as e:
        logger.error(f"Error getting active alerts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get active alerts: {str(e)}")

@router.get("/alerts/metrics", response_model=AlertMetricsResponse)
async def get_alert_metrics(
    request: AlertMetricsRequest = Depends(),
    service: ProductionAlertingService = Depends(get_production_alerting_service)
):
    """
    Get alert metrics.
    
    Returns comprehensive alert metrics including:
    - Total alerts count
    - Active alerts count
    - Acknowledged alerts count
    - Resolved alerts count
    - Severity distribution
    - Rule distribution
    """
    try:
        logger.info("Getting alert metrics")
        
        response = await service.get_alert_metrics(request)
        
        logger.info("Alert metrics retrieved successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error getting alert metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get alert metrics: {str(e)}")

# Production Reporting Endpoints
@router.post("/reports/generate", response_model=ReportingResponse)
async def generate_report(
    request: ReportingRequest = Body(..., description="Report generation request"),
    service: ProductionReportingService = Depends(get_production_reporting_service)
):
    """
    Generate a report on demand.
    
    Generates a report based on the specified request including:
    - Report type and time period
    - Output format preferences
    - Recipients
    - Custom sections
    """
    try:
        logger.info(f"Generating report: {request.report_type}")
        
        response = await service.generate_report(request)
        
        logger.info(f"Report generation {'successful' if response.success else 'failed'}")
        return response
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

@router.get("/reports/history")
async def get_report_history(
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of reports to return"),
    service: ProductionReportingService = Depends(get_production_reporting_service)
):
    """
    Get report generation history.
    
    Returns a list of recently generated reports with their status and metadata.
    """
    try:
        logger.info(f"Getting report history (limit: {limit})")
        
        history = await service.get_report_history(limit)
        
        logger.info(f"Retrieved {len(history)} report history entries")
        return {"reports": history, "count": len(history)}
        
    except Exception as e:
        logger.error(f"Error getting report history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get report history: {str(e)}")

@router.get("/reports/metrics", response_model=ReportMetrics)
async def get_report_metrics(
    service: ProductionReportingService = Depends(get_production_reporting_service)
):
    """
    Get report generation metrics.
    
    Returns comprehensive report metrics including:
    - Total reports generated
    - Success rate
    - Reports by type
    - Average generation time
    """
    try:
        logger.info("Getting report metrics")
        
        metrics = await service.get_report_metrics()
        
        logger.info("Report metrics retrieved successfully")
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting report metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get report metrics: {str(e)}")

# Health Check Endpoint
@router.get("/health")
async def production_monitoring_health():
    """Health check endpoint for production monitoring service."""
    return {
        "status": "healthy",
        "service": "production-monitoring",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }