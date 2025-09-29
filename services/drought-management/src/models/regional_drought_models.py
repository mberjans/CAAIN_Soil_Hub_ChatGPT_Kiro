"""
Regional Drought Analysis Data Models

Pydantic models for regional drought pattern analysis,
forecasting, and climate change impact assessment.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal
from enum import Enum

class DroughtSeverity(str, Enum):
    """Drought severity levels."""
    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    EXTREME = "extreme"
    EXCEPTIONAL = "exceptional"

class DroughtCategory(str, Enum):
    """Drought categories based on duration and impact."""
    METEOROLOGICAL = "meteorological"
    AGRICULTURAL = "agricultural"
    HYDROLOGICAL = "hydrological"
    SOCIOECONOMIC = "socioeconomic"

class TrendDirection(str, Enum):
    """Trend direction indicators."""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VARIABLE = "variable"

class ConfidenceLevel(str, Enum):
    """Confidence level indicators."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"

class DroughtPattern(BaseModel):
    """Drought pattern data model."""
    pattern_id: str = Field(..., description="Unique pattern identifier")
    region: str = Field(..., description="Geographic region identifier")
    start_date: date = Field(..., description="Drought start date")
    end_date: date = Field(..., description="Drought end date")
    duration_days: int = Field(..., ge=1, description="Duration in days")
    severity: DroughtSeverity = Field(..., description="Drought severity level")
    category: DroughtCategory = Field(..., description="Drought category")
    peak_intensity: float = Field(..., ge=0, le=10, description="Peak intensity (0-10 scale)")
    affected_area_percent: float = Field(..., ge=0, le=100, description="Affected area percentage")
    precipitation_deficit_mm: float = Field(..., description="Precipitation deficit in mm")
    temperature_anomaly_celsius: float = Field(..., description="Temperature anomaly in Celsius")
    soil_moisture_deficit_percent: float = Field(..., ge=0, le=100, description="Soil moisture deficit percentage")
    crop_yield_impact_percent: float = Field(..., ge=0, le=100, description="Crop yield impact percentage")
    
    @field_validator('duration_days')
    @classmethod
    def validate_duration(cls, v):
        if v < 1:
            raise ValueError('Duration must be at least 1 day')
        return v

class DroughtForecast(BaseModel):
    """Drought forecast data model."""
    forecast_id: str = Field(..., description="Unique forecast identifier")
    region: str = Field(..., description="Geographic region identifier")
    forecast_date: date = Field(default_factory=date.today, description="Forecast creation date")
    forecast_period_days: int = Field(..., ge=1, le=365, description="Forecast period in days")
    predicted_severity: DroughtSeverity = Field(..., description="Predicted drought severity")
    confidence_score: float = Field(..., ge=0, le=1, description="Forecast confidence score")
    probability_of_drought: float = Field(..., ge=0, le=1, description="Probability of drought occurrence")
    expected_duration_days: int = Field(..., ge=1, description="Expected drought duration in days")
    precipitation_outlook: str = Field(..., description="Precipitation outlook description")
    temperature_outlook: str = Field(..., description="Temperature outlook description")
    soil_moisture_outlook: str = Field(..., description="Soil moisture outlook description")
    agricultural_impact_prediction: str = Field(..., description="Agricultural impact prediction")
    mitigation_recommendations: List[str] = Field(default_factory=list, description="Mitigation recommendations")
    
    @field_validator('confidence_score', 'probability_of_drought')
    @classmethod
    def validate_probability(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Probability values must be between 0 and 1')
        return v

class TrendAnalysis(BaseModel):
    """Trend analysis data model."""
    trend_direction: TrendDirection = Field(..., description="Overall trend direction")
    trend_rate: float = Field(..., description="Trend rate per year")
    significance_level: float = Field(..., ge=0, le=1, description="Statistical significance level")
    confidence_level: ConfidenceLevel = Field(..., description="Confidence in trend")
    analysis_period: Dict[str, str] = Field(..., description="Analysis period start and end dates")
    data_points: int = Field(..., ge=1, description="Number of data points analyzed")
    
    @field_validator('significance_level')
    @classmethod
    def validate_significance(cls, v):
        if not 0 <= v <= 1:
            raise ValueError('Significance level must be between 0 and 1')
        return v

class SeasonalPattern(BaseModel):
    """Seasonal pattern data model."""
    season: str = Field(..., description="Season name")
    frequency_percent: float = Field(..., ge=0, le=100, description="Frequency percentage")
    average_severity: DroughtSeverity = Field(..., description="Average severity in season")
    average_duration_days: float = Field(..., ge=0, description="Average duration in days")
    peak_month: str = Field(..., description="Peak drought month")
    risk_level: str = Field(..., description="Risk level for season")
    
    @field_validator('frequency_percent')
    @classmethod
    def validate_frequency(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('Frequency percentage must be between 0 and 100')
        return v

class ClimateChangeImpact(BaseModel):
    """Climate change impact assessment model."""
    temperature_increase_celsius: float = Field(..., description="Temperature increase in Celsius")
    precipitation_change_percent: float = Field(..., description="Precipitation change percentage")
    drought_frequency_increase_percent: float = Field(..., description="Drought frequency increase percentage")
    drought_severity_increase_percent: float = Field(..., description="Drought severity increase percentage")
    confidence_level: ConfidenceLevel = Field(..., description="Confidence in climate change assessment")
    projection_period: str = Field(..., description="Projection period (e.g., '2020-2100')")
    adaptation_recommendations: List[str] = Field(default_factory=list, description="Adaptation recommendations")

class RiskAssessment(BaseModel):
    """Risk assessment data model."""
    overall_risk_level: str = Field(..., description="Overall risk level")
    risk_score: float = Field(..., ge=0, le=10, description="Risk score (0-10 scale)")
    risk_factors: List[str] = Field(default_factory=list, description="Identified risk factors")
    mitigation_potential: str = Field(..., description="Mitigation potential level")
    vulnerability_score: float = Field(..., ge=0, le=10, description="Vulnerability score (0-10 scale)")
    exposure_score: float = Field(..., ge=0, le=10, description="Exposure score (0-10 scale)")
    adaptive_capacity_score: float = Field(..., ge=0, le=10, description="Adaptive capacity score (0-10 scale)")
    
    @field_validator('risk_score', 'vulnerability_score', 'exposure_score', 'adaptive_capacity_score')
    @classmethod
    def validate_score(cls, v):
        if not 0 <= v <= 10:
            raise ValueError('Scores must be between 0 and 10')
        return v

class RegionalDroughtAnalysis(BaseModel):
    """Regional drought analysis results model."""
    region: str = Field(..., description="Geographic region identifier")
    analysis_date: date = Field(default_factory=date.today, description="Analysis date")
    current_status: DroughtSeverity = Field(..., description="Current drought status")
    historical_frequency: Dict[str, float] = Field(..., description="Historical frequency by severity")
    trend_analysis: Dict[str, Any] = Field(..., description="Trend analysis results")
    seasonal_patterns: Dict[str, Any] = Field(..., description="Seasonal pattern analysis")
    climate_change_impacts: Dict[str, Any] = Field(..., description="Climate change impact assessment")
    risk_assessment: Dict[str, Any] = Field(..., description="Risk assessment results")
    recommendations: List[str] = Field(default_factory=list, description="Management recommendations")
    analysis_confidence: ConfidenceLevel = Field(..., description="Overall analysis confidence")

# Request Models

class RegionalDroughtAnalysisRequest(BaseModel):
    """Request model for regional drought analysis."""
    region: str = Field(..., description="Geographic region identifier")
    start_date: date = Field(..., description="Analysis start date")
    end_date: date = Field(..., description="Analysis end date")
    include_forecast: bool = Field(True, description="Include forecast analysis")
    include_climate_change: bool = Field(True, description="Include climate change assessment")
    analysis_depth_years: int = Field(30, ge=1, le=100, description="Analysis depth in years")

class DroughtForecastRequest(BaseModel):
    """Request model for drought forecasting."""
    region: str = Field(..., description="Geographic region identifier")
    forecast_period_days: int = Field(90, ge=1, le=365, description="Forecast period in days")
    confidence_threshold: float = Field(0.7, ge=0, le=1, description="Minimum confidence threshold")
    include_agricultural_impact: bool = Field(True, description="Include agricultural impact prediction")
    include_mitigation_recommendations: bool = Field(True, description="Include mitigation recommendations")

class DroughtFrequencyAnalysisRequest(BaseModel):
    """Request model for drought frequency analysis."""
    region: str = Field(..., description="Geographic region identifier")
    start_date: date = Field(..., description="Analysis start date")
    end_date: date = Field(..., description="Analysis end date")
    include_seasonal_analysis: bool = Field(True, description="Include seasonal frequency analysis")
    include_decadal_analysis: bool = Field(True, description="Include decadal frequency analysis")
    include_return_periods: bool = Field(True, description="Include return period calculations")

class DroughtTrendAnalysisRequest(BaseModel):
    """Request model for drought trend analysis."""
    region: str = Field(..., description="Geographic region identifier")
    start_date: date = Field(..., description="Analysis start date")
    end_date: date = Field(..., description="Analysis end date")
    include_statistical_tests: bool = Field(True, description="Include statistical trend tests")
    trend_analysis_methods: List[str] = Field(
        default=["mann_kendall", "linear_regression"], 
        description="Trend analysis methods to use"
    )

class ClimateChangeImpactRequest(BaseModel):
    """Request model for climate change impact assessment."""
    region: str = Field(..., description="Geographic region identifier")
    start_date: date = Field(..., description="Historical analysis start date")
    end_date: date = Field(..., description="Historical analysis end date")
    projection_period: str = Field("2020-2100", description="Future projection period")
    include_adaptation_recommendations: bool = Field(True, description="Include adaptation recommendations")
    climate_scenarios: List[str] = Field(
        default=["RCP4.5", "RCP8.5"], 
        description="Climate scenarios to analyze"
    )

# Response Models

class RegionalDroughtAnalysisResponse(BaseModel):
    """Response model for regional drought analysis."""
    analysis: RegionalDroughtAnalysis = Field(..., description="Complete regional drought analysis")
    drought_events: List[DroughtPattern] = Field(default_factory=list, description="Identified drought events")
    forecast: Optional[DroughtForecast] = Field(None, description="Drought forecast if requested")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    data_sources: List[str] = Field(default_factory=list, description="Data sources used")

class DroughtForecastResponse(BaseModel):
    """Response model for drought forecasting."""
    forecast: DroughtForecast = Field(..., description="Drought forecast results")
    supporting_data: Dict[str, Any] = Field(..., description="Supporting forecast data")
    model_performance: Dict[str, Any] = Field(..., description="Model performance metrics")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")

class DroughtFrequencyAnalysisResponse(BaseModel):
    """Response model for drought frequency analysis."""
    region: str = Field(..., description="Geographic region identifier")
    analysis_period: Dict[str, str] = Field(..., description="Analysis period")
    frequency_by_severity: Dict[str, float] = Field(..., description="Frequency by severity level")
    seasonal_frequency: Dict[str, float] = Field(..., description="Seasonal frequency analysis")
    decadal_frequency: Dict[str, float] = Field(..., description="Decadal frequency analysis")
    duration_by_severity: Dict[str, float] = Field(..., description="Average duration by severity")
    return_periods: Dict[str, float] = Field(..., description="Return periods by severity")
    total_events: int = Field(..., description="Total drought events identified")
    analysis_confidence: ConfidenceLevel = Field(..., description="Analysis confidence level")

class DroughtTrendAnalysisResponse(BaseModel):
    """Response model for drought trend analysis."""
    region: str = Field(..., description="Geographic region identifier")
    analysis_period: Dict[str, str] = Field(..., description="Analysis period")
    severity_trends: TrendAnalysis = Field(..., description="Severity trend analysis")
    duration_trends: TrendAnalysis = Field(..., description="Duration trend analysis")
    frequency_trends: TrendAnalysis = Field(..., description="Frequency trend analysis")
    intensity_trends: TrendAnalysis = Field(..., description="Intensity trend analysis")
    statistical_tests: Dict[str, Any] = Field(..., description="Statistical test results")
    trend_summary: Dict[str, Any] = Field(..., description="Overall trend summary")
    analysis_confidence: ConfidenceLevel = Field(..., description="Analysis confidence level")

class ClimateChangeImpactResponse(BaseModel):
    """Response model for climate change impact assessment."""
    region: str = Field(..., description="Geographic region identifier")
    analysis_period: Dict[str, str] = Field(..., description="Historical analysis period")
    projection_period: str = Field(..., description="Future projection period")
    temperature_trends: TrendAnalysis = Field(..., description="Temperature trend analysis")
    precipitation_trends: TrendAnalysis = Field(..., description="Precipitation trend analysis")
    extreme_events: Dict[str, Any] = Field(..., description="Extreme weather event analysis")
    future_projections: Dict[str, Any] = Field(..., description="Future climate projections")
    drought_risk_changes: Dict[str, Any] = Field(..., description="Drought risk changes")
    adaptation_recommendations: List[str] = Field(..., description="Adaptation recommendations")
    confidence_level: ConfidenceLevel = Field(..., description="Assessment confidence level")

class DroughtPatternMapResponse(BaseModel):
    """Response model for drought pattern mapping."""
    region: str = Field(..., description="Geographic region identifier")
    map_data: Dict[str, Any] = Field(..., description="Geospatial drought pattern data")
    pattern_summary: Dict[str, Any] = Field(..., description="Pattern summary statistics")
    visualization_data: Dict[str, Any] = Field(..., description="Data for visualization")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")

class DroughtAlertResponse(BaseModel):
    """Response model for drought alerts."""
    alert_id: str = Field(..., description="Unique alert identifier")
    region: str = Field(..., description="Geographic region identifier")
    alert_type: str = Field(..., description="Type of drought alert")
    severity: DroughtSeverity = Field(..., description="Alert severity level")
    message: str = Field(..., description="Alert message")
    recommendations: List[str] = Field(default_factory=list, description="Recommended actions")
    valid_until: datetime = Field(..., description="Alert validity period")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Alert creation time")