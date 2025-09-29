"""
Water Usage Monitoring API Routes

FastAPI router for water usage monitoring, tracking, and reporting endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import List, Optional, Dict, Any
import logging
import uuid
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal

from ..models.water_usage_models import (
    WaterUsageRecord,
    WaterUsageRequest,
    WaterUsageResponse,
    WaterUsageSummary,
    WaterUsageReport,
    WaterUsageEfficiencyMetrics,
    WaterUsageMonitoringConfig,
    WaterSourceType,
    WaterUsageType,
    MonitoringFrequency
)
from services.water_usage_monitoring_service import WaterUsageMonitoringService
from services.water_usage_reporting_service import WaterUsageReportingService

logger = logging.getLogger(__name__)

# Create router for water usage monitoring
water_usage_router = APIRouter(prefix="/api/v1/water-usage", tags=["water-usage-monitoring"])

# Service dependencies for water usage monitoring
async def get_water_usage_monitoring_service():
    """Get water usage monitoring service instance."""
    from services.water_usage_monitoring_service import WaterUsageMonitoringService
    return WaterUsageMonitoringService()

async def get_water_usage_reporting_service():
    """Get water usage reporting service instance."""
    from services.water_usage_reporting_service import WaterUsageReportingService
    return WaterUsageReportingService()

@water_usage_router.post("/record", response_model=WaterUsageRecord)
async def record_water_usage(
    farm_location_id: UUID = Body(..., description="Farm location identifier"),
    water_source: WaterSourceType = Body(..., description="Source of water"),
    usage_type: WaterUsageType = Body(..., description="Type of water usage"),
    volume_gallons: float = Body(..., gt=0, description="Water volume in gallons"),
    field_id: Optional[UUID] = Body(None, description="Specific field identifier"),
    duration_minutes: Optional[int] = Body(None, ge=0, description="Usage duration in minutes"),
    flow_rate_gpm: Optional[float] = Body(None, gt=0, description="Flow rate in gallons per minute"),
    cost_per_gallon: Optional[float] = Body(None, ge=0, description="Cost per gallon"),
    efficiency_rating: Optional[float] = Body(None, ge=0, le=1, description="Efficiency rating (0-1)"),
    notes: Optional[str] = Body(None, description="Additional notes"),
    recorded_by: Optional[str] = Body(None, description="Who recorded this data"),
    data_source: str = Body("manual", description="Source of data"),
    service: WaterUsageMonitoringService = Depends(get_water_usage_monitoring_service)
):
    """
    Record a new water usage event.
    
    This endpoint allows recording water usage events with comprehensive tracking
    including volume, cost, efficiency, and source information.
    
    Agricultural Use Cases:
    - Track irrigation water usage by field and crop
    - Monitor livestock water consumption
    - Record domestic and processing water usage
    - Track water costs and efficiency metrics
    """
    try:
        record = await service.record_water_usage(
            farm_location_id=farm_location_id,
            water_source=water_source,
            usage_type=usage_type,
            volume_gallons=Decimal(str(volume_gallons)),
            field_id=field_id,
            duration_minutes=duration_minutes,
            flow_rate_gpm=Decimal(str(flow_rate_gpm)) if flow_rate_gpm else None,
            cost_per_gallon=Decimal(str(cost_per_gallon)) if cost_per_gallon else None,
            efficiency_rating=efficiency_rating,
            notes=notes,
            recorded_by=recorded_by,
            data_source=data_source
        )
        return record
    except Exception as e:
        logger.error(f"Error recording water usage: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@water_usage_router.get("/summary", response_model=WaterUsageSummary)
async def get_water_usage_summary(
    farm_location_id: UUID = Query(..., description="Farm location identifier"),
    start_date: datetime = Query(..., description="Start date for summary"),
    end_date: datetime = Query(..., description="End date for summary"),
    field_id: Optional[UUID] = Query(None, description="Specific field identifier"),
    service: WaterUsageMonitoringService = Depends(get_water_usage_monitoring_service)
):
    """
    Get water usage summary for a specific period.
    
    Provides comprehensive summary of water usage including total volume,
    costs, efficiency metrics, and breakdown by source and usage type.
    
    Agricultural Use Cases:
    - Monthly water usage reports for farm management
    - Field-specific usage analysis for irrigation planning
    - Cost analysis for budget planning
    - Efficiency tracking for conservation goals
    """
    try:
        summary = await service.get_water_usage_summary(
            farm_location_id=farm_location_id,
            start_date=start_date,
            end_date=end_date,
            field_id=field_id
        )
        return summary
    except Exception as e:
        logger.error(f"Error getting water usage summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@water_usage_router.post("/query", response_model=WaterUsageResponse)
async def query_water_usage(
    request: WaterUsageRequest,
    service: WaterUsageMonitoringService = Depends(get_water_usage_monitoring_service)
):
    """
    Query water usage data with comprehensive response.
    
    Provides detailed water usage data with optional reporting, alerts,
    and analytics based on query parameters.
    
    Agricultural Use Cases:
    - Comprehensive farm water usage analysis
    - Detailed reporting for conservation programs
    - Alert monitoring for unusual usage patterns
    - Performance tracking and benchmarking
    """
    try:
        response = await service.get_water_usage_response(request)
        return response
    except Exception as e:
        logger.error(f"Error querying water usage: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@water_usage_router.get("/efficiency-metrics", response_model=WaterUsageEfficiencyMetrics)
async def get_efficiency_metrics(
    farm_location_id: UUID = Query(..., description="Farm location identifier"),
    field_id: Optional[UUID] = Query(None, description="Specific field identifier"),
    period_days: int = Query(30, ge=1, le=365, description="Period for calculation in days"),
    service: WaterUsageMonitoringService = Depends(get_water_usage_monitoring_service)
):
    """
    Get comprehensive water usage efficiency metrics.
    
    Calculates detailed efficiency metrics including irrigation efficiency,
    water use efficiency, cost efficiency, and environmental efficiency.
    
    Agricultural Use Cases:
    - Performance benchmarking against industry standards
    - Efficiency optimization planning
    - ROI analysis for water management investments
    - Sustainability reporting and compliance
    """
    try:
        metrics = await service.calculate_efficiency_metrics(
            farm_location_id=farm_location_id,
            field_id=field_id,
            period_days=period_days
        )
        return metrics
    except Exception as e:
        logger.error(f"Error calculating efficiency metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@water_usage_router.post("/configure-monitoring", response_model=WaterUsageMonitoringConfig)
async def configure_monitoring(
    config: WaterUsageMonitoringConfig,
    service: WaterUsageMonitoringService = Depends(get_water_usage_monitoring_service)
):
    """
    Configure water usage monitoring for a farm location.
    
    Sets up monitoring parameters including alert thresholds, notification
    preferences, and data collection settings.
    
    Agricultural Use Cases:
    - Set up automated monitoring for irrigation systems
    - Configure alerts for unusual usage patterns
    - Customize reporting frequency and recipients
    - Integrate with existing farm management systems
    """
    try:
        updated_config = await service.configure_monitoring(config)
        return updated_config
    except Exception as e:
        logger.error(f"Error configuring monitoring: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@water_usage_router.post("/reports/comprehensive", response_model=WaterUsageReport)
async def generate_comprehensive_report(
    farm_location_id: UUID = Body(..., description="Farm location identifier"),
    start_date: datetime = Body(..., description="Report period start date"),
    end_date: datetime = Body(..., description="Report period end date"),
    field_id: Optional[UUID] = Body(None, description="Specific field identifier"),
    report_type: str = Body("monthly", description="Type of report"),
    include_benchmarks: bool = Body(True, description="Include benchmarking data"),
    include_recommendations: bool = Body(True, description="Include recommendations"),
    service: WaterUsageReportingService = Depends(get_water_usage_reporting_service)
):
    """
    Generate comprehensive water usage report.
    
    Creates detailed reports with analytics, trends, benchmarking,
    and recommendations for water usage optimization.
    
    Agricultural Use Cases:
    - Annual water usage reports for farm planning
    - Conservation program compliance reporting
    - Performance benchmarking and improvement planning
    - Stakeholder reporting and transparency
    """
    try:
        report = await service.generate_comprehensive_report(
            farm_location_id=farm_location_id,
            start_date=start_date,
            end_date=end_date,
            field_id=field_id,
            report_type=report_type,
            include_benchmarks=include_benchmarks,
            include_recommendations=include_recommendations
        )
        return report
    except Exception as e:
        logger.error(f"Error generating comprehensive report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@water_usage_router.post("/reports/trend-analysis")
async def generate_trend_analysis(
    farm_location_id: UUID = Body(..., description="Farm location identifier"),
    start_date: datetime = Body(..., description="Analysis period start date"),
    end_date: datetime = Body(..., description="Analysis period end date"),
    field_id: Optional[UUID] = Body(None, description="Specific field identifier"),
    trend_period: str = Body("monthly", description="Period for trend analysis"),
    service: WaterUsageReportingService = Depends(get_water_usage_reporting_service)
):
    """
    Generate detailed trend analysis for water usage.
    
    Analyzes usage patterns, seasonal variations, and predicts
    future trends for better planning and optimization.
    
    Agricultural Use Cases:
    - Seasonal water usage planning
    - Long-term trend analysis for farm development
    - Predictive modeling for water resource management
    - Anomaly detection for early problem identification
    """
    try:
        trend_analysis = await service.generate_trend_analysis(
            farm_location_id=farm_location_id,
            start_date=start_date,
            end_date=end_date,
            field_id=field_id,
            trend_period=trend_period
        )
        return trend_analysis
    except Exception as e:
        logger.error(f"Error generating trend analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@water_usage_router.post("/reports/benchmark")
async def generate_benchmark_report(
    farm_location_id: UUID = Body(..., description="Farm location identifier"),
    start_date: datetime = Body(..., description="Benchmark period start date"),
    end_date: datetime = Body(..., description="Benchmark period end date"),
    field_id: Optional[UUID] = Body(None, description="Specific field identifier"),
    service: WaterUsageReportingService = Depends(get_water_usage_reporting_service)
):
    """
    Generate benchmarking report comparing farm performance.
    
    Compares farm water usage performance against industry standards,
    regional averages, and peer farms for performance improvement.
    
    Agricultural Use Cases:
    - Performance benchmarking against industry standards
    - Regional comparison for competitive analysis
    - Peer benchmarking for best practice identification
    - Improvement opportunity identification
    """
    try:
        benchmark_report = await service.generate_benchmark_report(
            farm_location_id=farm_location_id,
            start_date=start_date,
            end_date=end_date,
            field_id=field_id
        )
        return benchmark_report
    except Exception as e:
        logger.error(f"Error generating benchmark report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@water_usage_router.post("/reports/efficiency")
async def generate_efficiency_report(
    farm_location_id: UUID = Body(..., description="Farm location identifier"),
    start_date: datetime = Body(..., description="Analysis period start date"),
    end_date: datetime = Body(..., description="Analysis period end date"),
    field_id: Optional[UUID] = Body(None, description="Specific field identifier"),
    service: WaterUsageReportingService = Depends(get_water_usage_reporting_service)
):
    """
    Generate detailed efficiency analysis report.
    
    Provides comprehensive efficiency analysis including bottlenecks,
    optimization opportunities, and improvement recommendations.
    
    Agricultural Use Cases:
    - Efficiency optimization planning
    - Bottleneck identification and resolution
    - Technology investment decision support
    - Performance improvement tracking
    """
    try:
        efficiency_report = await service.generate_efficiency_report(
            farm_location_id=farm_location_id,
            start_date=start_date,
            end_date=end_date,
            field_id=field_id
        )
        return efficiency_report
    except Exception as e:
        logger.error(f"Error generating efficiency report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@water_usage_router.post("/reports/export")
async def export_report_data(
    report_id: UUID = Body(..., description="Report identifier"),
    export_format: str = Body("json", description="Export format (json, csv, pdf, excel)"),
    include_charts: bool = Body(False, description="Include chart data"),
    service: WaterUsageReportingService = Depends(get_water_usage_reporting_service)
):
    """
    Export report data in various formats.
    
    Exports water usage reports in multiple formats for sharing,
    analysis, and integration with other systems.
    
    Agricultural Use Cases:
    - Report sharing with stakeholders and consultants
    - Data integration with farm management software
    - Regulatory compliance documentation
    - Historical data archiving and analysis
    """
    try:
        # In a real implementation, this would fetch the report from storage
        # For now, we'll create a placeholder report
        placeholder_report = WaterUsageReport(
            report_id=report_id,
            farm_location_id=UUID("00000000-0000-0000-0000-000000000000"),
            report_period_start=datetime.utcnow(),
            report_period_end=datetime.utcnow(),
            report_type="export",
            total_water_usage=WaterUsageSummary(
                summary_id=UUID("00000000-0000-0000-0000-000000000000"),
                farm_location_id=UUID("00000000-0000-0000-0000-000000000000"),
                period_start=datetime.utcnow(),
                period_end=datetime.utcnow(),
                total_volume_gallons=Decimal('0'),
                total_cost=Decimal('0'),
                average_daily_usage=Decimal('0'),
                usage_by_source={},
                usage_by_type={}
            )
        )
        
        export_data = await service.export_report_data(
            report=placeholder_report,
            export_format=export_format,
            include_charts=include_charts
        )
        return export_data
    except Exception as e:
        logger.error(f"Error exporting report data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@water_usage_router.get("/health")
async def water_usage_health_check():
    """Health check endpoint for water usage monitoring service."""
    return {
        "status": "healthy",
        "service": "water-usage-monitoring",
        "timestamp": datetime.utcnow().isoformat(),
        "features": [
            "usage_tracking",
            "efficiency_monitoring",
            "reporting",
            "alerting",
            "benchmarking"
        ]
    }