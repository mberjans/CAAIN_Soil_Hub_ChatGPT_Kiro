"""
Disease Pressure Analysis Models

Pydantic models for disease pressure mapping, analysis, and recommendations
within the crop taxonomy system.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union, Tuple
from datetime import date, datetime
from enum import Enum
from uuid import UUID


# ============================================================================
# DISEASE PRESSURE ENUMERATIONS
# ============================================================================

class DiseaseSeverity(str, Enum):
    """Disease severity levels."""
    NONE = "none"
    TRACE = "trace"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"


class DiseaseRiskLevel(str, Enum):
    """Disease risk assessment levels."""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"
    CRITICAL = "critical"


class PathogenType(str, Enum):
    """Pathogen type classifications."""
    FUNGAL = "fungal"
    BACTERIAL = "bacterial"
    VIRAL = "viral"
    NEMATODE = "nematode"
    PHYTOPLASMA = "phytoplasma"
    VIROID = "viroid"
    OOMYCETE = "oomycete"


class DiseaseStage(str, Enum):
    """Disease development stages."""
    LATENT = "latent"
    INCUBATION = "incubation"
    SYMPTOMATIC = "symptomatic"
    SPORULATION = "sporulation"
    DISSEMINATION = "dissemination"


class ResistanceMechanism(str, Enum):
    """Resistance mechanism types."""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    QUANTITATIVE = "quantitative"
    QUALITATIVE = "qualitative"
    SYSTEMIC = "systemic"
    LOCALIZED = "localized"


class DataSource(str, Enum):
    """Disease data source types."""
    UNIVERSITY_EXTENSION = "university_extension"
    USDA_SURVEY = "usda_survey"
    WEATHER_MODEL = "weather_model"
    FIELD_OBSERVATION = "field_observation"
    LABORATORY_TEST = "laboratory_test"
    RESEARCH_TRIAL = "research_trial"
    FARMER_REPORT = "farmer_report"


# ============================================================================
# DISEASE PRESSURE DATA MODELS
# ============================================================================

class DiseaseData(BaseModel):
    """Individual disease data entry."""
    
    disease_id: str = Field(..., description="Unique disease identifier")
    disease_name: str = Field(..., description="Disease common name")
    scientific_name: Optional[str] = Field(None, description="Pathogen scientific name")
    pathogen_type: PathogenType = Field(..., description="Type of pathogen")
    crop_affected: str = Field(..., description="Primary crop affected")
    
    # Disease characteristics
    symptoms: List[str] = Field(default_factory=list, description="Common symptoms")
    transmission_methods: List[str] = Field(default_factory=list, description="How disease spreads")
    environmental_factors: Dict[str, Any] = Field(default_factory=dict, description="Environmental conditions favoring disease")
    
    # Geographic and temporal data
    geographic_distribution: List[str] = Field(default_factory=list, description="Regions where disease occurs")
    seasonal_patterns: Dict[str, Any] = Field(default_factory=dict, description="Seasonal occurrence patterns")
    
    # Economic impact
    yield_loss_potential: Optional[float] = Field(None, ge=0.0, le=1.0, description="Potential yield loss (0-1)")
    quality_impact: Optional[str] = Field(None, description="Impact on crop quality")
    
    # Management information
    cultural_controls: List[str] = Field(default_factory=list, description="Cultural management practices")
    chemical_controls: List[str] = Field(default_factory=list, description="Chemical control options")
    biological_controls: List[str] = Field(default_factory=list, description="Biological control options")
    
    # Data metadata
    data_source: DataSource = Field(..., description="Source of disease data")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0, description="Data confidence score")


class RegionalDiseasePressure(BaseModel):
    """Regional disease pressure data."""
    
    region_id: str = Field(..., description="Region identifier")
    region_name: str = Field(..., description="Human-readable region name")
    coordinates: Tuple[float, float] = Field(..., description="Region center coordinates (lat, lng)")
    radius_km: float = Field(..., description="Region radius in kilometers")
    
    # Disease pressure data
    diseases: List["DiseasePressureEntry"] = Field(default_factory=list, description="Disease pressure entries")
    overall_risk_level: DiseaseRiskLevel = Field(..., description="Overall disease risk for region")
    
    # Environmental factors
    climate_zone: Optional[str] = Field(None, description="Climate zone classification")
    soil_types: List[str] = Field(default_factory=list, description="Dominant soil types")
    weather_patterns: Dict[str, Any] = Field(default_factory=dict, description="Weather patterns affecting disease")
    
    # Temporal data
    pressure_period: Tuple[date, date] = Field(..., description="Period of disease pressure data")
    seasonal_trends: Dict[str, Any] = Field(default_factory=dict, description="Seasonal disease trends")
    
    # Data quality
    data_sources: List[DataSource] = Field(default_factory=list, description="Sources of pressure data")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0, description="Overall data confidence")


class DiseasePressureEntry(BaseModel):
    """Individual disease pressure entry for a region."""
    
    disease_id: str = Field(..., description="Disease identifier")
    disease_name: str = Field(..., description="Disease name")
    
    # Pressure metrics
    current_severity: DiseaseSeverity = Field(..., description="Current disease severity")
    historical_average: DiseaseSeverity = Field(..., description="Historical average severity")
    trend_direction: str = Field(..., description="Trend direction (increasing, decreasing, stable)")
    
    # Risk assessment
    risk_level: DiseaseRiskLevel = Field(..., description="Current risk level")
    risk_factors: List[str] = Field(default_factory=list, description="Contributing risk factors")
    
    # Environmental conditions
    favorable_conditions: Dict[str, Any] = Field(default_factory=dict, description="Current favorable conditions")
    unfavorable_conditions: Dict[str, Any] = Field(default_factory=dict, description="Current unfavorable conditions")
    
    # Predictive data
    forecast_severity: Optional[DiseaseSeverity] = Field(None, description="Forecasted severity")
    forecast_confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Forecast confidence")
    forecast_period_days: Optional[int] = Field(None, ge=1, description="Forecast period in days")
    
    # Management recommendations
    management_priority: str = Field(..., description="Management priority level")
    recommended_actions: List[str] = Field(default_factory=list, description="Recommended management actions")
    timing_recommendations: List[str] = Field(default_factory=list, description="Timing recommendations")
    
    # Data metadata
    data_source: DataSource = Field(..., description="Data source")
    measurement_date: date = Field(..., description="Date of pressure measurement")
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0, description="Data confidence score")


class VarietyDiseaseResistance(BaseModel):
    """Disease resistance information for a specific variety."""
    
    variety_id: UUID = Field(..., description="Variety identifier")
    variety_name: str = Field(..., description="Variety name")
    
    # Resistance data
    disease_resistances: List["DiseaseResistanceEntry"] = Field(default_factory=list, description="Disease resistance entries")
    overall_resistance_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Overall resistance score")
    
    # Resistance mechanisms
    resistance_genes: List[str] = Field(default_factory=list, description="Known resistance genes")
    resistance_mechanisms: List[ResistanceMechanism] = Field(default_factory=list, description="Resistance mechanisms")
    
    # Field validation
    field_tested: bool = Field(default=False, description="Field tested resistance")
    validation_years: List[int] = Field(default_factory=list, description="Years of field validation")
    validation_locations: List[str] = Field(default_factory=list, description="Validation locations")
    
    # Durability and stability
    resistance_durability: Optional[str] = Field(None, description="Resistance durability assessment")
    stability_under_stress: Optional[str] = Field(None, description="Stability under environmental stress")
    
    # Data metadata
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    data_sources: List[DataSource] = Field(default_factory=list, description="Data sources")


class DiseaseResistanceEntry(BaseModel):
    """Individual disease resistance entry for a variety."""
    
    disease_id: str = Field(..., description="Disease identifier")
    disease_name: str = Field(..., description="Disease name")
    
    # Resistance characteristics
    resistance_level: str = Field(..., description="Resistance level (immune, resistant, tolerant, susceptible)")
    resistance_rating: Optional[int] = Field(None, ge=1, le=9, description="Resistance rating (1-9 scale)")
    field_effectiveness: Optional[float] = Field(None, ge=0.0, le=1.0, description="Field effectiveness score")
    
    # Resistance details
    resistance_genes: List[str] = Field(default_factory=list, description="Specific resistance genes")
    resistance_mechanism: Optional[ResistanceMechanism] = Field(None, description="Resistance mechanism")
    
    # Testing and validation
    test_method: Optional[str] = Field(None, description="Testing method used")
    test_conditions: Optional[str] = Field(None, description="Test conditions")
    validation_status: Optional[str] = Field(None, description="Validation status")
    
    # Performance under pressure
    performance_under_pressure: Optional[str] = Field(None, description="Performance under disease pressure")
    yield_protection: Optional[float] = Field(None, ge=0.0, le=1.0, description="Yield protection level")
    
    # Data metadata
    data_source: DataSource = Field(..., description="Data source")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0, description="Data confidence score")


# ============================================================================
# DISEASE PRESSURE ANALYSIS REQUEST/RESPONSE MODELS
# ============================================================================

class DiseasePressureRequest(BaseModel):
    """Request model for disease pressure analysis."""
    
    # Location information
    coordinates: Tuple[float, float] = Field(..., description="Coordinates (latitude, longitude)")
    region_radius_km: float = Field(default=50.0, ge=1.0, le=500.0, description="Analysis radius in kilometers")
    
    # Crop and variety information
    crop_type: str = Field(..., description="Crop type for analysis")
    variety_ids: Optional[List[UUID]] = Field(None, description="Specific varieties to analyze")
    growth_stage: Optional[str] = Field(None, description="Current growth stage")
    
    # Analysis parameters
    analysis_period_days: int = Field(default=30, ge=1, le=365, description="Analysis period in days")
    include_forecast: bool = Field(default=True, description="Include disease forecast")
    include_historical: bool = Field(default=True, description="Include historical data")
    
    # Filtering options
    disease_types: Optional[List[PathogenType]] = Field(None, description="Filter by pathogen types")
    severity_threshold: Optional[DiseaseSeverity] = Field(None, description="Minimum severity threshold")
    risk_level_threshold: Optional[DiseaseRiskLevel] = Field(None, description="Minimum risk level threshold")
    
    # Output preferences
    include_management_recommendations: bool = Field(default=True, description="Include management recommendations")
    include_variety_recommendations: bool = Field(default=True, description="Include variety recommendations")
    include_timing_guidance: bool = Field(default=True, description="Include timing guidance")


class DiseasePressureResponse(BaseModel):
    """Response model for disease pressure analysis."""
    
    # Request metadata
    request_id: str = Field(..., description="Unique request identifier")
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    analysis_period: Tuple[date, date] = Field(..., description="Analysis period")
    
    # Location and region data
    analysis_location: Tuple[float, float] = Field(..., description="Analysis coordinates")
    analysis_region: RegionalDiseasePressure = Field(..., description="Regional disease pressure data")
    
    # Disease pressure summary
    overall_risk_level: DiseaseRiskLevel = Field(..., description="Overall disease risk level")
    active_diseases: List["DiseasePressureEntry"] = Field(default_factory=list, description="Active disease pressures")
    emerging_threats: List["DiseasePressureEntry"] = Field(default_factory=list, description="Emerging disease threats")
    
    # Variety-specific analysis
    variety_analysis: Optional[List["VarietyDiseaseAnalysis"]] = Field(None, description="Variety-specific disease analysis")
    recommended_varieties: Optional[List["VarietyRecommendation"]] = Field(None, description="Disease-resistant variety recommendations")
    
    # Management recommendations
    management_recommendations: Optional["DiseaseManagementRecommendations"] = Field(None, description="Management recommendations")
    timing_guidance: Optional["DiseaseTimingGuidance"] = Field(None, description="Timing guidance")
    
    # Forecast and trends
    disease_forecast: Optional["DiseaseForecast"] = Field(None, description="Disease pressure forecast")
    historical_trends: Optional["DiseaseTrends"] = Field(None, description="Historical disease trends")
    
    # Data quality and confidence
    data_quality_score: float = Field(default=0.8, ge=0.0, le=1.0, description="Overall data quality score")
    confidence_level: str = Field(default="moderate", description="Confidence level in analysis")
    data_sources: List[DataSource] = Field(default_factory=list, description="Data sources used")
    
    # Processing metadata
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    cache_status: str = Field(default="miss", description="Cache status (hit/miss)")


class VarietyDiseaseAnalysis(BaseModel):
    """Disease analysis for a specific variety."""
    
    variety_id: UUID = Field(..., description="Variety identifier")
    variety_name: str = Field(..., description="Variety name")
    
    # Disease resistance assessment
    disease_resistances: List["DiseaseResistanceEntry"] = Field(default_factory=list, description="Disease resistance data")
    overall_resistance_score: float = Field(..., ge=0.0, le=1.0, description="Overall resistance score")
    
    # Risk assessment
    disease_risk_level: DiseaseRiskLevel = Field(..., description="Disease risk level for this variety")
    vulnerable_diseases: List[str] = Field(default_factory=list, description="Diseases this variety is vulnerable to")
    resistant_diseases: List[str] = Field(default_factory=list, description="Diseases this variety is resistant to")
    
    # Performance predictions
    expected_yield_impact: Optional[float] = Field(None, ge=0.0, le=1.0, description="Expected yield impact from diseases")
    management_requirements: List[str] = Field(default_factory=list, description="Additional management requirements")
    
    # Recommendations
    suitability_score: float = Field(..., ge=0.0, le=1.0, description="Suitability score for current conditions")
    recommendation_priority: str = Field(..., description="Recommendation priority (high, medium, low)")
    specific_recommendations: List[str] = Field(default_factory=list, description="Specific recommendations for this variety")


class VarietyRecommendation(BaseModel):
    """Disease-resistant variety recommendation."""
    
    variety_id: UUID = Field(..., description="Variety identifier")
    variety_name: str = Field(..., description="Variety name")
    
    # Recommendation details
    recommendation_score: float = Field(..., ge=0.0, le=1.0, description="Recommendation score")
    recommendation_reason: str = Field(..., description="Reason for recommendation")
    disease_advantages: List[str] = Field(default_factory=list, description="Disease resistance advantages")
    
    # Risk mitigation
    diseases_protected_against: List[str] = Field(default_factory=list, description="Diseases protected against")
    risk_reduction_percentage: Optional[float] = Field(None, ge=0.0, le=100.0, description="Risk reduction percentage")
    
    # Additional considerations
    management_complexity: str = Field(..., description="Management complexity (low, medium, high)")
    additional_requirements: List[str] = Field(default_factory=list, description="Additional management requirements")
    
    # Economic considerations
    seed_cost_impact: Optional[str] = Field(None, description="Seed cost impact")
    potential_yield_benefit: Optional[str] = Field(None, description="Potential yield benefit")


class DiseaseManagementRecommendations(BaseModel):
    """Disease management recommendations."""
    
    # Overall strategy
    management_strategy: str = Field(..., description="Overall management strategy")
    priority_level: str = Field(..., description="Management priority level")
    
    # Cultural practices
    cultural_practices: List[str] = Field(default_factory=list, description="Cultural management practices")
    cultural_timing: List[str] = Field(default_factory=list, description="Cultural practice timing")
    
    # Chemical controls
    chemical_recommendations: List["ChemicalControlRecommendation"] = Field(default_factory=list, description="Chemical control recommendations")
    application_timing: List[str] = Field(default_factory=list, description="Application timing recommendations")
    
    # Biological controls
    biological_options: List[str] = Field(default_factory=list, description="Biological control options")
    
    # Monitoring and scouting
    monitoring_recommendations: List[str] = Field(default_factory=list, description="Monitoring recommendations")
    scouting_schedule: List[str] = Field(default_factory=list, description="Scouting schedule")
    
    # Economic considerations
    cost_benefit_analysis: Optional[str] = Field(None, description="Cost-benefit analysis")
    roi_estimate: Optional[float] = Field(None, description="Estimated return on investment")


class ChemicalControlRecommendation(BaseModel):
    """Chemical control recommendation."""
    
    product_name: str = Field(..., description="Product name")
    active_ingredient: str = Field(..., description="Active ingredient")
    target_diseases: List[str] = Field(default_factory=list, description="Target diseases")
    
    # Application details
    application_rate: str = Field(..., description="Application rate")
    application_method: str = Field(..., description="Application method")
    application_timing: str = Field(..., description="Application timing")
    
    # Effectiveness and safety
    effectiveness_rating: int = Field(..., ge=1, le=5, description="Effectiveness rating (1-5)")
    resistance_risk: str = Field(..., description="Resistance development risk")
    environmental_impact: str = Field(..., description="Environmental impact assessment")
    
    # Economic information
    cost_per_acre: Optional[float] = Field(None, description="Cost per acre")
    cost_benefit_ratio: Optional[float] = Field(None, description="Cost-benefit ratio")


class DiseaseTimingGuidance(BaseModel):
    """Disease timing guidance."""
    
    # Critical timing windows
    critical_periods: List["CriticalTimingPeriod"] = Field(default_factory=list, description="Critical timing periods")
    optimal_timing: List[str] = Field(default_factory=list, description="Optimal timing recommendations")
    
    # Weather considerations
    weather_dependencies: List[str] = Field(default_factory=list, description="Weather dependencies")
    weather_restrictions: List[str] = Field(default_factory=list, description="Weather restrictions")
    
    # Monitoring schedule
    monitoring_schedule: List["MonitoringPeriod"] = Field(default_factory=list, description="Monitoring schedule")
    action_thresholds: List["ActionThreshold"] = Field(default_factory=list, description="Action thresholds")
    
    # Long-term planning
    seasonal_calendar: List["SeasonalActivity"] = Field(default_factory=list, description="Seasonal activity calendar")
    multi_year_considerations: List[str] = Field(default_factory=list, description="Multi-year considerations")


class CriticalTimingPeriod(BaseModel):
    """Critical timing period for disease management."""
    
    period_name: str = Field(..., description="Period name")
    start_date: date = Field(..., description="Period start date")
    end_date: date = Field(..., description="Period end date")
    importance_level: str = Field(..., description="Importance level")
    activities: List[str] = Field(default_factory=list, description="Recommended activities")
    diseases_of_concern: List[str] = Field(default_factory=list, description="Diseases of concern")


class MonitoringPeriod(BaseModel):
    """Monitoring period definition."""
    
    period_name: str = Field(..., description="Period name")
    frequency: str = Field(..., description="Monitoring frequency")
    duration_days: int = Field(..., description="Duration in days")
    focus_areas: List[str] = Field(default_factory=list, description="Areas to focus on")
    indicators: List[str] = Field(default_factory=list, description="Key indicators to monitor")


class ActionThreshold(BaseModel):
    """Action threshold definition."""
    
    disease_name: str = Field(..., description="Disease name")
    threshold_type: str = Field(..., description="Threshold type")
    threshold_value: str = Field(..., description="Threshold value")
    action_required: str = Field(..., description="Action required when threshold is reached")
    urgency_level: str = Field(..., description="Urgency level")


class SeasonalActivity(BaseModel):
    """Seasonal activity definition."""
    
    activity_name: str = Field(..., description="Activity name")
    season: str = Field(..., description="Season")
    month_range: str = Field(..., description="Month range")
    description: str = Field(..., description="Activity description")
    diseases_addressed: List[str] = Field(default_factory=list, description="Diseases addressed")


class DiseaseForecast(BaseModel):
    """Disease pressure forecast."""
    
    forecast_period_days: int = Field(..., description="Forecast period in days")
    forecast_date: date = Field(..., description="Forecast date")
    
    # Forecast data
    predicted_diseases: List["DiseaseForecastEntry"] = Field(default_factory=list, description="Predicted disease pressures")
    overall_risk_trend: str = Field(..., description="Overall risk trend")
    
    # Confidence and accuracy
    forecast_confidence: float = Field(..., ge=0.0, le=1.0, description="Forecast confidence")
    accuracy_metrics: Optional[Dict[str, float]] = Field(None, description="Historical accuracy metrics")
    
    # Weather dependencies
    weather_dependencies: List[str] = Field(default_factory=list, description="Weather dependencies")
    weather_sensitivity: str = Field(..., description="Weather sensitivity level")


class DiseaseForecastEntry(BaseModel):
    """Individual disease forecast entry."""
    
    disease_id: str = Field(..., description="Disease identifier")
    disease_name: str = Field(..., description="Disease name")
    
    # Forecast predictions
    predicted_severity: DiseaseSeverity = Field(..., description="Predicted severity")
    predicted_risk_level: DiseaseRiskLevel = Field(..., description="Predicted risk level")
    probability_of_occurrence: float = Field(..., ge=0.0, le=1.0, description="Probability of occurrence")
    
    # Timing predictions
    predicted_onset_date: Optional[date] = Field(None, description="Predicted onset date")
    predicted_peak_date: Optional[date] = Field(None, description="Predicted peak date")
    
    # Confidence and factors
    forecast_confidence: float = Field(..., ge=0.0, le=1.0, description="Forecast confidence")
    key_factors: List[str] = Field(default_factory=list, description="Key influencing factors")
    uncertainty_factors: List[str] = Field(default_factory=list, description="Uncertainty factors")


class DiseaseTrends(BaseModel):
    """Historical disease trends."""
    
    analysis_period_years: int = Field(..., description="Analysis period in years")
    trend_data: List["DiseaseTrendEntry"] = Field(default_factory=list, description="Trend data entries")
    
    # Overall trends
    overall_trend_direction: str = Field(..., description="Overall trend direction")
    trend_significance: str = Field(..., description="Trend significance level")
    
    # Seasonal patterns
    seasonal_patterns: Dict[str, Any] = Field(default_factory=dict, description="Seasonal patterns")
    peak_seasons: List[str] = Field(default_factory=list, description="Peak disease seasons")
    
    # Long-term changes
    long_term_changes: List[str] = Field(default_factory=list, description="Long-term changes")
    climate_impacts: List[str] = Field(default_factory=list, description="Climate change impacts")


class DiseaseTrendEntry(BaseModel):
    """Individual disease trend entry."""
    
    disease_id: str = Field(..., description="Disease identifier")
    disease_name: str = Field(..., description="Disease name")
    
    # Trend metrics
    trend_direction: str = Field(..., description="Trend direction")
    trend_magnitude: float = Field(..., description="Trend magnitude")
    trend_significance: str = Field(..., description="Trend significance")
    
    # Temporal data
    start_year: int = Field(..., description="Trend start year")
    end_year: int = Field(..., description="Trend end year")
    data_points: int = Field(..., description="Number of data points")
    
    # Contributing factors
    contributing_factors: List[str] = Field(default_factory=list, description="Contributing factors")
    external_influences: List[str] = Field(default_factory=list, description="External influences")
    
    # Future implications
    future_implications: List[str] = Field(default_factory=list, description="Future implications")
    management_implications: List[str] = Field(default_factory=list, description="Management implications")