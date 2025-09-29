"""
Water Usage Monitoring Models

Data models for water usage tracking, monitoring, and reporting in agricultural systems.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from uuid import UUID
from decimal import Decimal
from enum import Enum


class WaterSourceType(str, Enum):
    """Types of water sources for monitoring."""
    IRRIGATION = "irrigation"
    RAINFALL = "rainfall"
    GROUNDWATER = "groundwater"
    SURFACE_WATER = "surface_water"
    RECYCLED_WATER = "recycled_water"
    MUNICIPAL = "municipal"


class WaterUsageType(str, Enum):
    """Types of water usage."""
    CROP_IRRIGATION = "crop_irrigation"
    LIVESTOCK = "livestock"
    DOMESTIC = "domestic"
    PROCESSING = "processing"
    CLEANING = "cleaning"
    OTHER = "other"


class MonitoringFrequency(str, Enum):
    """Monitoring frequency options."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    SEASONAL = "seasonal"
    ANNUAL = "annual"


class WaterUsageRecord(BaseModel):
    """Individual water usage record."""
    record_id: UUID = Field(..., description="Unique record identifier")
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    field_id: Optional[UUID] = Field(None, description="Specific field identifier")
    timestamp: datetime = Field(..., description="Record timestamp")
    water_source: WaterSourceType = Field(..., description="Source of water")
    usage_type: WaterUsageType = Field(..., description="Type of water usage")
    volume_gallons: Decimal = Field(..., gt=0, description="Water volume in gallons")
    duration_minutes: Optional[int] = Field(None, ge=0, description="Usage duration in minutes")
    flow_rate_gpm: Optional[Decimal] = Field(None, gt=0, description="Flow rate in gallons per minute")
    cost_per_gallon: Optional[Decimal] = Field(None, ge=0, description="Cost per gallon")
    total_cost: Optional[Decimal] = Field(None, ge=0, description="Total cost for this usage")
    efficiency_rating: Optional[float] = Field(None, ge=0, le=1, description="Efficiency rating (0-1)")
    notes: Optional[str] = Field(None, description="Additional notes")
    recorded_by: Optional[str] = Field(None, description="Who recorded this data")
    data_source: str = Field(..., description="Source of data (manual, sensor, api)")
    
    @field_validator('efficiency_rating')
    @classmethod
    def validate_efficiency_rating(cls, v):
        if v is not None and (v < 0 or v > 1):
            raise ValueError('Efficiency rating must be between 0 and 1')
        return v


class WaterUsageSummary(BaseModel):
    """Summary of water usage for a time period."""
    summary_id: UUID = Field(..., description="Unique summary identifier")
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    field_id: Optional[UUID] = Field(None, description="Specific field identifier")
    period_start: datetime = Field(..., description="Period start time")
    period_end: datetime = Field(..., description="Period end time")
    total_volume_gallons: Decimal = Field(..., ge=0, description="Total water volume")
    total_cost: Decimal = Field(..., ge=0, description="Total cost")
    average_daily_usage: Decimal = Field(..., ge=0, description="Average daily usage")
    peak_usage_day: Optional[date] = Field(None, description="Day with highest usage")
    peak_usage_volume: Optional[Decimal] = Field(None, ge=0, description="Peak usage volume")
    usage_by_source: Dict[WaterSourceType, Decimal] = Field(default_factory=dict)
    usage_by_type: Dict[WaterUsageType, Decimal] = Field(default_factory=dict)
    efficiency_score: Optional[float] = Field(None, ge=0, le=1, description="Overall efficiency score")
    cost_per_gallon: Optional[Decimal] = Field(None, ge=0, description="Average cost per gallon")
    water_savings_gallons: Optional[Decimal] = Field(None, ge=0, description="Water savings achieved")
    savings_percentage: Optional[float] = Field(None, ge=0, le=100, description="Percentage savings")
    
    @field_validator('efficiency_score')
    @classmethod
    def validate_efficiency_score(cls, v):
        if v is not None and (v < 0 or v > 1):
            raise ValueError('Efficiency score must be between 0 and 1')
        return v
    
    @field_validator('savings_percentage')
    @classmethod
    def validate_savings_percentage(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Savings percentage must be between 0 and 100')
        return v


class WaterUsageAlert(BaseModel):
    """Water usage alert for monitoring."""
    alert_id: UUID = Field(..., description="Unique alert identifier")
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    field_id: Optional[UUID] = Field(None, description="Specific field identifier")
    alert_type: str = Field(..., description="Type of alert")
    severity: str = Field(..., description="Alert severity (low, medium, high, critical)")
    message: str = Field(..., description="Alert message")
    threshold_value: Optional[Decimal] = Field(None, description="Threshold that triggered alert")
    actual_value: Optional[Decimal] = Field(None, description="Actual value that triggered alert")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = Field(default=False, description="Whether alert has been acknowledged")
    acknowledged_by: Optional[str] = Field(None, description="Who acknowledged the alert")
    acknowledged_at: Optional[datetime] = Field(None, description="When alert was acknowledged")
    resolved: bool = Field(default=False, description="Whether alert has been resolved")
    resolved_at: Optional[datetime] = Field(None, description="When alert was resolved")
    resolution_notes: Optional[str] = Field(None, description="Resolution notes")


class WaterUsageReport(BaseModel):
    """Comprehensive water usage report."""
    report_id: UUID = Field(..., description="Unique report identifier")
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    report_period_start: datetime = Field(..., description="Report period start")
    report_period_end: datetime = Field(..., description="Report period end")
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    report_type: str = Field(..., description="Type of report (daily, weekly, monthly, annual)")
    
    # Summary data
    total_water_usage: WaterUsageSummary = Field(..., description="Total usage summary")
    field_summaries: List[WaterUsageSummary] = Field(default_factory=list)
    
    # Analysis data
    usage_trends: Dict[str, Any] = Field(default_factory=dict)
    efficiency_analysis: Dict[str, Any] = Field(default_factory=dict)
    cost_analysis: Dict[str, Any] = Field(default_factory=dict)
    savings_analysis: Dict[str, Any] = Field(default_factory=dict)
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list)
    alerts_generated: List[WaterUsageAlert] = Field(default_factory=list)
    
    # Performance metrics
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)


class WaterUsageMonitoringConfig(BaseModel):
    """Configuration for water usage monitoring."""
    config_id: UUID = Field(..., description="Unique config identifier")
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    field_id: Optional[UUID] = Field(None, description="Specific field identifier")
    
    # Monitoring settings
    monitoring_enabled: bool = Field(default=True, description="Whether monitoring is enabled")
    monitoring_frequency: MonitoringFrequency = Field(default=MonitoringFrequency.DAILY)
    data_retention_days: int = Field(default=365, ge=1, description="Days to retain data")
    
    # Alert thresholds
    high_usage_threshold_gallons: Optional[Decimal] = Field(None, ge=0)
    high_cost_threshold_dollars: Optional[Decimal] = Field(None, ge=0)
    low_efficiency_threshold: Optional[float] = Field(None, ge=0, le=1)
    unusual_pattern_threshold: Optional[float] = Field(None, ge=0, le=1)
    
    # Notification settings
    email_alerts: bool = Field(default=True)
    sms_alerts: bool = Field(default=False)
    alert_recipients: List[str] = Field(default_factory=list)
    
    # Integration settings
    sensor_integration: bool = Field(default=False)
    api_integration: bool = Field(default=True)
    manual_entry: bool = Field(default=True)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WaterUsageRequest(BaseModel):
    """Request model for water usage operations."""
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    field_id: Optional[UUID] = Field(None, description="Specific field identifier")
    start_date: Optional[datetime] = Field(None, description="Start date for query")
    end_date: Optional[datetime] = Field(None, description="End date for query")
    water_source: Optional[WaterSourceType] = Field(None, description="Filter by water source")
    usage_type: Optional[WaterUsageType] = Field(None, description="Filter by usage type")
    include_details: bool = Field(default=False, description="Include detailed records")
    generate_report: bool = Field(default=False, description="Generate comprehensive report")


class WaterUsageResponse(BaseModel):
    """Response model for water usage queries."""
    request_id: UUID = Field(..., description="Unique request identifier")
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    query_period_start: datetime = Field(..., description="Query period start")
    query_period_end: datetime = Field(..., description="Query period end")
    
    # Data
    usage_summary: WaterUsageSummary = Field(..., description="Usage summary")
    detailed_records: Optional[List[WaterUsageRecord]] = Field(None, description="Detailed records")
    alerts: List[WaterUsageAlert] = Field(default_factory=list)
    report: Optional[WaterUsageReport] = Field(None, description="Generated report")
    
    # Metadata
    total_records: int = Field(..., description="Total number of records")
    data_quality_score: float = Field(..., ge=0, le=1, description="Data quality score")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class WaterUsageEfficiencyMetrics(BaseModel):
    """Water usage efficiency metrics."""
    metrics_id: UUID = Field(..., description="Unique metrics identifier")
    farm_location_id: UUID = Field(..., description="Farm location identifier")
    field_id: Optional[UUID] = Field(None, description="Specific field identifier")
    calculation_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Efficiency metrics
    overall_efficiency_score: float = Field(..., ge=0, le=1, description="Overall efficiency score")
    irrigation_efficiency: float = Field(..., ge=0, le=1, description="Irrigation efficiency")
    water_application_efficiency: float = Field(..., ge=0, le=1, description="Application efficiency")
    distribution_efficiency: float = Field(..., ge=0, le=1, description="Distribution efficiency")
    storage_efficiency: float = Field(..., ge=0, le=1, description="Storage efficiency")
    
    # Performance indicators
    water_use_efficiency: Decimal = Field(..., ge=0, description="Water use efficiency (crop yield per unit water)")
    cost_efficiency: Decimal = Field(..., ge=0, description="Cost efficiency (yield per dollar spent on water)")
    environmental_efficiency: float = Field(..., ge=0, le=1, description="Environmental efficiency score")
    
    # Benchmarking
    industry_average: Optional[float] = Field(None, description="Industry average efficiency")
    regional_average: Optional[float] = Field(None, description="Regional average efficiency")
    farm_ranking: Optional[int] = Field(None, ge=1, description="Farm ranking in region")
    
    # Recommendations
    improvement_opportunities: List[str] = Field(default_factory=list)
    best_practices: List[str] = Field(default_factory=list)
    target_efficiency: Optional[float] = Field(None, ge=0, le=1, description="Target efficiency score")