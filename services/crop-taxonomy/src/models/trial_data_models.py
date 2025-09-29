"""
Trial Data Models
TICKET-005_crop-variety-recommendations-11.1

Pydantic models for university trial data API requests and responses.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
from enum import Enum
from uuid import UUID

from .service_models import DataSource

class TrialDataQuality(str, Enum):
    """Trial data quality assessment levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNVERIFIED = "unverified"

class StatisticalSignificance(str, Enum):
    """Statistical significance levels."""
    HIGHLY_SIGNIFICANT = "highly_significant"  # p < 0.01
    SIGNIFICANT = "significant"  # p < 0.05
    MARGINALLY_SIGNIFICANT = "marginally_significant"  # p < 0.10
    NOT_SIGNIFICANT = "not_significant"  # p >= 0.10

# ============================================================================
# REQUEST MODELS
# ============================================================================

class TrialDataRequest(BaseModel):
    """Request model for trial data queries."""
    
    source: Optional[str] = Field(None, description="Filter by data source")
    crop_type: Optional[str] = Field(None, description="Filter by crop type")
    year: Optional[int] = Field(None, ge=1900, le=2100, description="Filter by trial year")
    state: Optional[str] = Field(None, description="Filter by state")
    quality: Optional[TrialDataQuality] = Field(None, description="Filter by data quality")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of trials to return")
    offset: int = Field(0, ge=0, description="Number of trials to skip")

class VarietyPerformanceRequest(BaseModel):
    """Request model for variety performance analysis."""
    
    variety_name: str = Field(..., description="Name of the variety to analyze")
    crop_type: Optional[str] = Field(None, description="Optional crop type filter")
    years: Optional[List[int]] = Field(None, description="Optional list of years to include")
    include_regional_analysis: bool = Field(True, description="Include regional performance analysis")

class RegionalTrialRequest(BaseModel):
    """Request model for regional trial data queries."""
    
    state: str = Field(..., description="State to filter by")
    crop_type: Optional[str] = Field(None, description="Optional crop type filter")
    year: Optional[int] = Field(None, ge=1900, le=2100, description="Optional year filter")
    include_neighboring_states: bool = Field(False, description="Include trials from neighboring states")

class TrialIngestionRequest(BaseModel):
    """Request model for trial data ingestion."""
    
    source_names: List[str] = Field(..., description="List of data sources to ingest from")
    year: Optional[int] = Field(None, ge=1900, le=2100, description="Specific year to ingest")
    crop_type: Optional[str] = Field(None, description="Specific crop type to filter")
    run_in_background: bool = Field(False, description="Run ingestion in background")
    validate_data: bool = Field(True, description="Validate ingested data")

# ============================================================================
# RESPONSE MODELS
# ============================================================================

class TrialLocationInfo(BaseModel):
    """Trial location information for API responses."""
    
    location_id: Optional[str] = Field(None, description="Unique location identifier")
    location_name: str = Field(..., description="Location name")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude in decimal degrees")
    state: str = Field(..., description="State name")
    county: Optional[str] = Field(None, description="County name")
    climate_zone: Optional[str] = Field(None, description="Climate zone classification")
    soil_type: Optional[str] = Field(None, description="Primary soil type")
    elevation_meters: Optional[float] = Field(None, ge=0, description="Elevation in meters")
    irrigation_available: bool = Field(False, description="Irrigation availability")

class TrialDesignInfo(BaseModel):
    """Trial design information for API responses."""
    
    design_type: str = Field(..., description="Experimental design type")
    replications: int = Field(..., ge=1, description="Number of replications")
    plot_size_sq_meters: float = Field(..., ge=0, description="Plot size in square meters")
    planting_date: Optional[str] = Field(None, description="Planting date (ISO format)")
    harvest_date: Optional[str] = Field(None, description="Harvest date (ISO format)")
    growing_season_days: Optional[int] = Field(None, ge=0, description="Growing season length in days")
    management_practices: Optional[Dict[str, Any]] = Field(None, description="Management practices used")

class TrialStatistics(BaseModel):
    """Trial statistics for API responses."""
    
    varieties_tested: int = Field(..., ge=1, description="Number of varieties tested")
    check_variety: Optional[str] = Field(None, description="Check variety used")
    mean_yield: Optional[float] = Field(None, ge=0, description="Mean yield across varieties")
    std_dev_yield: Optional[float] = Field(None, ge=0, description="Standard deviation of yield")
    cv_percent: Optional[float] = Field(None, ge=0, description="Coefficient of variation percentage")
    lsd_05: Optional[float] = Field(None, ge=0, description="Least Significant Difference at 5%")
    f_statistic: Optional[float] = Field(None, description="F-statistic from ANOVA")
    p_value: Optional[float] = Field(None, ge=0, le=1, description="P-value from statistical test")

class TrialQualityInfo(BaseModel):
    """Trial data quality information for API responses."""
    
    data_quality: TrialDataQuality = Field(..., description="Overall data quality assessment")
    outliers_detected: int = Field(0, ge=0, description="Number of outliers detected")
    missing_data_percent: float = Field(0, ge=0, le=100, description="Percentage of missing data")
    validation_notes: Optional[str] = Field(None, description="Validation notes and warnings")

class TrialMetadata(BaseModel):
    """Trial metadata for API responses."""
    
    data_source: DataSource = Field(..., description="Source of the trial data")
    source_url: Optional[str] = Field(None, description="URL to original data source")
    last_updated: Optional[str] = Field(None, description="Last update timestamp (ISO format)")
    ingestion_date: Optional[str] = Field(None, description="Date when data was ingested")

class TrialSummaryInfo(BaseModel):
    """Trial summary information for API responses."""
    
    trial_id: str = Field(..., description="Unique trial identifier")
    trial_name: str = Field(..., description="Trial name")
    crop_type: str = Field(..., description="Crop type tested")
    trial_year: int = Field(..., ge=1900, le=2100, description="Year of the trial")
    location: TrialLocationInfo = Field(..., description="Trial location information")
    design: TrialDesignInfo = Field(..., description="Trial design information")
    statistics: TrialStatistics = Field(..., description="Trial statistics")
    quality: TrialQualityInfo = Field(..., description="Data quality information")
    metadata: TrialMetadata = Field(..., description="Trial metadata")

class TrialDataResponse(BaseModel):
    """Response model for trial data queries."""
    
    trials: List[TrialSummaryInfo] = Field(..., description="List of trial summaries")
    total_count: int = Field(..., ge=0, description="Total number of trials matching criteria")
    limit: int = Field(..., ge=1, description="Maximum number of trials returned")
    offset: int = Field(..., ge=0, description="Number of trials skipped")
    filters_applied: Dict[str, Any] = Field(..., description="Filters applied to the query")

class VarietyPerformanceMetrics(BaseModel):
    """Performance metrics for variety analysis."""
    
    average_yield: Optional[float] = Field(None, ge=0, description="Average yield across trials")
    yield_stability: Optional[float] = Field(None, ge=0, description="Yield stability (standard deviation)")
    adaptation_regions: List[str] = Field(default_factory=list, description="Regions where variety performed well")
    performance_trend: Optional[str] = Field(None, description="Performance trend over time")
    regional_performance: Optional[Dict[str, float]] = Field(None, description="Performance by region")

class VarietyPerformanceResponse(BaseModel):
    """Response model for variety performance analysis."""
    
    variety_name: str = Field(..., description="Name of the analyzed variety")
    crop_type: Optional[str] = Field(None, description="Crop type")
    trials_found: int = Field(..., ge=0, description="Number of trials found")
    years_covered: List[int] = Field(..., description="Years covered in analysis")
    states_covered: List[str] = Field(..., description="States covered in analysis")
    performance_metrics: VarietyPerformanceMetrics = Field(..., description="Performance metrics")
    data_quality_summary: Dict[str, int] = Field(..., description="Summary of data quality by level")

class RegionalTrialInfo(BaseModel):
    """Regional trial information for API responses."""
    
    trial_id: str = Field(..., description="Unique trial identifier")
    trial_name: str = Field(..., description="Trial name")
    crop_type: str = Field(..., description="Crop type tested")
    trial_year: int = Field(..., ge=1900, le=2100, description="Year of the trial")
    location: TrialLocationInfo = Field(..., description="Trial location information")
    statistics: TrialStatistics = Field(..., description="Trial statistics")
    data_quality: TrialDataQuality = Field(..., description="Data quality assessment")

class RegionalTrialResponse(BaseModel):
    """Response model for regional trial data queries."""
    
    state: str = Field(..., description="State filtered by")
    crop_type: Optional[str] = Field(None, description="Crop type filtered by")
    year: Optional[int] = Field(None, description="Year filtered by")
    trials: List[RegionalTrialInfo] = Field(..., description="List of regional trials")
    total_count: int = Field(..., ge=0, description="Total number of trials found")

class TrialIngestionResult(BaseModel):
    """Result of trial data ingestion."""
    
    source_name: str = Field(..., description="Name of the data source")
    trials_ingested: int = Field(..., ge=0, description="Number of trials ingested")
    status: str = Field(..., description="Ingestion status")
    error: Optional[str] = Field(None, description="Error message if failed")

class TrialIngestionResponse(BaseModel):
    """Response model for trial data ingestion."""
    
    status: str = Field(..., description="Overall ingestion status")
    message: str = Field(..., description="Status message")
    ingestion_id: str = Field(..., description="Unique ingestion identifier")
    results: Optional[Dict[str, Any]] = Field(None, description="Detailed ingestion results")

# ============================================================================
# VALIDATION MODELS
# ============================================================================

class TrialDataValidation(BaseModel):
    """Model for trial data validation."""
    
    trial_id: str = Field(..., description="Trial identifier to validate")
    validation_rules: List[str] = Field(default_factory=list, description="Validation rules to apply")
    include_statistical_tests: bool = Field(True, description="Include statistical validation tests")

class TrialDataValidationResult(BaseModel):
    """Result of trial data validation."""
    
    trial_id: str = Field(..., description="Validated trial identifier")
    is_valid: bool = Field(..., description="Whether trial data is valid")
    validation_score: float = Field(..., ge=0, le=1, description="Validation score (0-1)")
    issues_found: List[str] = Field(default_factory=list, description="Issues found during validation")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for improvement")
    statistical_tests: Optional[Dict[str, Any]] = Field(None, description="Results of statistical tests")

# ============================================================================
# UTILITY MODELS
# ============================================================================

class TrialDataFilter(BaseModel):
    """Model for filtering trial data."""
    
    field: str = Field(..., description="Field to filter by")
    operator: str = Field(..., description="Filter operator (eq, gt, lt, contains, etc.)")
    value: Union[str, int, float, bool] = Field(..., description="Filter value")
    case_sensitive: bool = Field(False, description="Whether filter is case sensitive")

class TrialDataSort(BaseModel):
    """Model for sorting trial data."""
    
    field: str = Field(..., description="Field to sort by")
    direction: str = Field("asc", description="Sort direction (asc or desc)")
    
    @validator('direction')
    def validate_direction(cls, v):
        if v not in ['asc', 'desc']:
            raise ValueError('Direction must be "asc" or "desc"')
        return v

class TrialDataAggregation(BaseModel):
    """Model for aggregating trial data."""
    
    field: str = Field(..., description="Field to aggregate")
    function: str = Field(..., description="Aggregation function (sum, avg, min, max, count)")
    group_by: Optional[List[str]] = Field(None, description="Fields to group by")
    
    @validator('function')
    def validate_function(cls, v):
        if v not in ['sum', 'avg', 'min', 'max', 'count']:
            raise ValueError('Function must be one of: sum, avg, min, max, count')
        return v