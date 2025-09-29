"""
Pest Resistance Analysis Models

Pydantic models for pest resistance analysis, recommendations, and integrated pest management
within the crop taxonomy system.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union, Tuple
from datetime import date, datetime
from enum import Enum
from uuid import UUID


# ============================================================================
# PEST RESISTANCE ENUMERATIONS
# ============================================================================

class PestType(str, Enum):
    """Pest type classifications."""
    INSECT = "insect"
    NEMATODE = "nematode"
    MITE = "mite"
    APHID = "aphid"
    BEETLE = "beetle"
    MOTH = "moth"
    WEEVIL = "weevil"
    THRIP = "thrip"
    WHITEFLY = "whitefly"
    SPIDER_MITE = "spider_mite"
    ROOT_WORM = "root_worm"
    CUTWORM = "cutworm"
    ARMYWORM = "armyworm"
    CORN_BORER = "corn_borer"
    SOYBEAN_APHID = "soybean_aphid"
    WHEAT_MIDGE = "wheat_midge"
    OTHER = "other"


class PestSeverity(str, Enum):
    """Pest severity levels."""
    NONE = "none"
    TRACE = "trace"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"


class PestRiskLevel(str, Enum):
    """Pest risk assessment levels."""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"
    CRITICAL = "critical"


class ResistanceMechanism(str, Enum):
    """Pest resistance mechanism types."""
    ANTIBIOSIS = "antibiosis"
    ANTIXENOSIS = "antixenosis"
    TOLERANCE = "tolerance"
    SYSTEMIC = "systemic"
    CONTACT = "contact"
    BEHAVIORAL = "behavioral"
    PHYSICAL = "physical"
    CHEMICAL = "chemical"


class ResistanceDurability(str, Enum):
    """Resistance durability classifications."""
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    VARIABLE = "variable"


class IPMStrategy(str, Enum):
    """Integrated Pest Management strategy types."""
    PREVENTIVE = "preventive"
    SUPPRESSIVE = "suppressive"
    CURATIVE = "curative"
    COMBINED = "combined"


class DataSource(str, Enum):
    """Pest data source types."""
    UNIVERSITY_EXTENSION = "university_extension"
    USDA_SURVEY = "usda_survey"
    FIELD_OBSERVATION = "field_observation"
    RESEARCH_TRIAL = "research_trial"
    FARMER_REPORT = "farmer_report"
    BIOLOGICAL_CONTROL = "biological_control"
    RESISTANCE_DATABASE = "resistance_database"
    WEATHER_MODEL = "weather_model"


# ============================================================================
# PEST RESISTANCE DATA MODELS
# ============================================================================

class PestData(BaseModel):
    """Individual pest data entry."""
    
    pest_id: str = Field(..., description="Unique pest identifier")
    pest_name: str = Field(..., description="Pest common name")
    scientific_name: Optional[str] = Field(None, description="Pest scientific name")
    pest_type: PestType = Field(..., description="Type of pest")
    crop_affected: str = Field(..., description="Primary crop affected")
    
    # Pest characteristics
    life_stages: List[str] = Field(default_factory=list, description="Life stages that cause damage")
    damage_symptoms: List[str] = Field(default_factory=list, description="Damage symptoms")
    feeding_behavior: List[str] = Field(default_factory=list, description="Feeding behavior patterns")
    environmental_factors: Dict[str, Any] = Field(default_factory=dict, description="Environmental conditions favoring pest")
    
    # Geographic and temporal data
    geographic_distribution: List[str] = Field(default_factory=list, description="Regions where pest occurs")
    seasonal_patterns: Dict[str, Any] = Field(default_factory=dict, description="Seasonal occurrence patterns")
    generation_per_year: Optional[int] = Field(None, description="Number of generations per year")
    
    # Economic impact
    yield_loss_potential: Optional[float] = Field(None, ge=0.0, le=1.0, description="Potential yield loss (0-1)")
    quality_impact: Optional[str] = Field(None, description="Impact on crop quality")
    economic_threshold: Optional[float] = Field(None, description="Economic threshold for control")
    
    # Management information
    cultural_controls: List[str] = Field(default_factory=list, description="Cultural management practices")
    chemical_controls: List[str] = Field(default_factory=list, description="Chemical control options")
    biological_controls: List[str] = Field(default_factory=list, description="Biological control options")
    resistance_management: List[str] = Field(default_factory=list, description="Resistance management practices")
    
    # Data metadata
    data_source: DataSource = Field(..., description="Source of pest data")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0, description="Data confidence score")


class RegionalPestPressure(BaseModel):
    """Regional pest pressure data."""
    
    region_id: str = Field(..., description="Region identifier")
    region_name: str = Field(..., description="Human-readable region name")
    coordinates: Tuple[float, float] = Field(..., description="Region center coordinates (lat, lng)")
    radius_km: float = Field(..., description="Region radius in kilometers")
    
    # Pest pressure data
    pests: List["PestPressureEntry"] = Field(default_factory=list, description="Pest pressure entries")
    overall_risk_level: PestRiskLevel = Field(..., description="Overall pest risk for region")
    
    # Environmental factors
    climate_zone: Optional[str] = Field(None, description="Climate zone classification")
    soil_types: List[str] = Field(default_factory=list, description="Dominant soil types")
    weather_patterns: Dict[str, Any] = Field(default_factory=dict, description="Weather patterns affecting pests")
    
    # Temporal data
    pressure_period: Tuple[date, date] = Field(..., description="Period of pest pressure data")
    seasonal_trends: Dict[str, Any] = Field(default_factory=dict, description="Seasonal pest trends")
    
    # Data quality
    data_sources: List[DataSource] = Field(default_factory=list, description="Sources of pressure data")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0, description="Overall data confidence")


class PestPressureEntry(BaseModel):
    """Individual pest pressure entry for a region."""
    
    pest_id: str = Field(..., description="Pest identifier")
    pest_name: str = Field(..., description="Pest name")
    
    # Pressure metrics
    current_severity: PestSeverity = Field(..., description="Current pest severity")
    historical_average: PestSeverity = Field(..., description="Historical average severity")
    trend_direction: str = Field(..., description="Trend direction (increasing, decreasing, stable)")
    
    # Risk assessment
    risk_level: PestRiskLevel = Field(..., description="Current risk level")
    risk_factors: List[str] = Field(default_factory=list, description="Contributing risk factors")
    
    # Environmental conditions
    favorable_conditions: Dict[str, Any] = Field(default_factory=dict, description="Current favorable conditions")
    unfavorable_conditions: Dict[str, Any] = Field(default_factory=dict, description="Current unfavorable conditions")
    
    # Predictive data
    forecast_severity: Optional[PestSeverity] = Field(None, description="Forecasted severity")
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


class VarietyPestResistance(BaseModel):
    """Pest resistance information for a specific variety."""
    
    variety_id: UUID = Field(..., description="Variety identifier")
    variety_name: str = Field(..., description="Variety name")
    
    # Resistance data
    pest_resistances: List["PestResistanceEntry"] = Field(default_factory=list, description="Pest resistance entries")
    overall_resistance_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Overall resistance score")
    
    # Resistance mechanisms
    resistance_genes: List[str] = Field(default_factory=list, description="Known resistance genes")
    resistance_mechanisms: List[ResistanceMechanism] = Field(default_factory=list, description="Resistance mechanisms")
    
    # Field validation
    field_tested: bool = Field(default=False, description="Field tested resistance")
    validation_years: List[int] = Field(default_factory=list, description="Years of field validation")
    validation_locations: List[str] = Field(default_factory=list, description="Validation locations")
    
    # Durability and stability
    resistance_durability: Optional[ResistanceDurability] = Field(None, description="Resistance durability assessment")
    stability_under_stress: Optional[str] = Field(None, description="Stability under environmental stress")
    
    # Data metadata
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    data_sources: List[DataSource] = Field(default_factory=list, description="Data sources")


class PestResistanceEntry(BaseModel):
    """Individual pest resistance entry for a variety."""
    
    pest_id: str = Field(..., description="Pest identifier")
    pest_name: str = Field(..., description="Pest name")
    
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
    performance_under_pressure: Optional[str] = Field(None, description="Performance under pest pressure")
    yield_protection: Optional[float] = Field(None, ge=0.0, le=1.0, description="Yield protection level")
    
    # Data metadata
    data_source: DataSource = Field(..., description="Data source")
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0, description="Data confidence score")


# ============================================================================
# PEST RESISTANCE ANALYSIS REQUEST/RESPONSE MODELS
# ============================================================================

class PestResistanceRequest(BaseModel):
    """Request model for pest resistance analysis."""
    
    # Location information
    coordinates: Tuple[float, float] = Field(..., description="Coordinates (latitude, longitude)")
    region_radius_km: float = Field(default=50.0, ge=1.0, le=500.0, description="Analysis radius in kilometers")
    
    # Crop and variety information
    crop_type: str = Field(..., description="Crop type for analysis")
    variety_ids: Optional[List[UUID]] = Field(None, description="Specific varieties to analyze")
    growth_stage: Optional[str] = Field(None, description="Current growth stage")
    
    # Analysis parameters
    analysis_period_days: int = Field(default=30, ge=1, le=365, description="Analysis period in days")
    include_forecast: bool = Field(default=True, description="Include pest forecast")
    include_historical: bool = Field(default=True, description="Include historical data")
    
    # Filtering options
    pest_types: Optional[List[PestType]] = Field(None, description="Filter by pest types")
    severity_threshold: Optional[PestSeverity] = Field(None, description="Minimum severity threshold")
    risk_level_threshold: Optional[PestRiskLevel] = Field(None, description="Minimum risk level threshold")
    
    # Output preferences
    include_management_recommendations: bool = Field(default=True, description="Include management recommendations")
    include_variety_recommendations: bool = Field(default=True, description="Include variety recommendations")
    include_timing_guidance: bool = Field(default=True, description="Include timing guidance")
    include_resistance_analysis: bool = Field(default=True, description="Include resistance durability analysis")


class PestResistanceResponse(BaseModel):
    """Response model for pest resistance analysis."""
    
    # Request metadata
    request_id: str = Field(..., description="Unique request identifier")
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    analysis_period: Tuple[date, date] = Field(..., description="Analysis period")
    
    # Location and region data
    analysis_location: Tuple[float, float] = Field(..., description="Analysis coordinates")
    analysis_region: RegionalPestPressure = Field(..., description="Regional pest pressure data")
    
    # Pest pressure summary
    overall_risk_level: PestRiskLevel = Field(..., description="Overall pest risk level")
    active_pests: List["PestPressureEntry"] = Field(default_factory=list, description="Active pest pressures")
    emerging_threats: List["PestPressureEntry"] = Field(default_factory=list, description="Emerging pest threats")
    
    # Variety-specific analysis
    variety_analysis: Optional[List["VarietyPestAnalysis"]] = Field(None, description="Variety-specific pest analysis")
    recommended_varieties: Optional[List["VarietyRecommendation"]] = Field(None, description="Pest-resistant variety recommendations")
    
    # Management recommendations
    management_recommendations: Optional["PestManagementRecommendations"] = Field(None, description="Management recommendations")
    timing_guidance: Optional["PestTimingGuidance"] = Field(None, description="Timing guidance")
    
    # Resistance analysis
    resistance_analysis: Optional["ResistanceAnalysis"] = Field(None, description="Resistance durability and stacking analysis")
    
    # Forecast and trends
    pest_forecast: Optional["PestForecast"] = Field(None, description="Pest pressure forecast")
    historical_trends: Optional["PestTrends"] = Field(None, description="Historical pest trends")
    
    # Data quality and confidence
    data_quality_score: float = Field(default=0.8, ge=0.0, le=1.0, description="Overall data quality score")
    confidence_level: str = Field(default="moderate", description="Confidence level in analysis")
    data_sources: List[DataSource] = Field(default_factory=list, description="Data sources used")
    
    # Processing metadata
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    cache_status: str = Field(default="miss", description="Cache status (hit/miss)")


class VarietyPestAnalysis(BaseModel):
    """Pest analysis for a specific variety."""
    
    variety_id: UUID = Field(..., description="Variety identifier")
    variety_name: str = Field(..., description="Variety name")
    
    # Pest resistance assessment
    pest_resistances: List["PestResistanceEntry"] = Field(default_factory=list, description="Pest resistance data")
    overall_resistance_score: float = Field(..., ge=0.0, le=1.0, description="Overall resistance score")
    
    # Risk assessment
    pest_risk_level: PestRiskLevel = Field(..., description="Pest risk level for this variety")
    vulnerable_pests: List[str] = Field(default_factory=list, description="Pests this variety is vulnerable to")
    resistant_pests: List[str] = Field(default_factory=list, description="Pests this variety is resistant to")
    
    # Performance predictions
    expected_yield_impact: Optional[float] = Field(None, ge=0.0, le=1.0, description="Expected yield impact from pests")
    management_requirements: List[str] = Field(default_factory=list, description="Additional management requirements")
    
    # Recommendations
    suitability_score: float = Field(..., ge=0.0, le=1.0, description="Suitability score for current conditions")
    recommendation_priority: str = Field(..., description="Recommendation priority (high, medium, low)")
    specific_recommendations: List[str] = Field(default_factory=list, description="Specific recommendations for this variety")


class VarietyRecommendation(BaseModel):
    """Pest-resistant variety recommendation."""
    
    variety_id: UUID = Field(..., description="Variety identifier")
    variety_name: str = Field(..., description="Variety name")
    
    # Recommendation details
    recommendation_score: float = Field(..., ge=0.0, le=1.0, description="Recommendation score")
    recommendation_reason: str = Field(..., description="Reason for recommendation")
    pest_advantages: List[str] = Field(default_factory=list, description="Pest resistance advantages")
    
    # Risk mitigation
    pests_protected_against: List[str] = Field(default_factory=list, description="Pests protected against")
    risk_reduction_percentage: Optional[float] = Field(None, ge=0.0, le=100.0, description="Risk reduction percentage")
    
    # Additional considerations
    management_complexity: str = Field(..., description="Management complexity (low, medium, high)")
    additional_requirements: List[str] = Field(default_factory=list, description="Additional management requirements")
    
    # Economic considerations
    seed_cost_impact: Optional[str] = Field(None, description="Seed cost impact")
    potential_yield_benefit: Optional[str] = Field(None, description="Potential yield benefit")


class PestManagementRecommendations(BaseModel):
    """Pest management recommendations."""
    
    # Overall strategy
    management_strategy: str = Field(..., description="Overall management strategy")
    priority_level: str = Field(..., description="Management priority level")
    ipm_strategy: IPMStrategy = Field(..., description="Integrated Pest Management strategy")
    
    # Cultural practices
    cultural_practices: List[str] = Field(default_factory=list, description="Cultural management practices")
    cultural_timing: List[str] = Field(default_factory=list, description="Cultural practice timing")
    
    # Chemical controls
    chemical_recommendations: List["ChemicalControlRecommendation"] = Field(default_factory=list, description="Chemical control recommendations")
    application_timing: List[str] = Field(default_factory=list, description="Application timing recommendations")
    
    # Biological controls
    biological_options: List[str] = Field(default_factory=list, description="Biological control options")
    beneficial_organisms: List[str] = Field(default_factory=list, description="Beneficial organisms")
    
    # Monitoring and scouting
    monitoring_recommendations: List[str] = Field(default_factory=list, description="Monitoring recommendations")
    scouting_schedule: List[str] = Field(default_factory=list, description="Scouting schedule")
    
    # Resistance management
    resistance_management: List[str] = Field(default_factory=list, description="Resistance management practices")
    refuge_requirements: Optional[str] = Field(None, description="Refuge requirements")
    
    # Economic considerations
    cost_benefit_analysis: Optional[str] = Field(None, description="Cost-benefit analysis")
    roi_estimate: Optional[float] = Field(None, description="Estimated return on investment")


class ChemicalControlRecommendation(BaseModel):
    """Chemical control recommendation."""
    
    product_name: str = Field(..., description="Product name")
    active_ingredient: str = Field(..., description="Active ingredient")
    target_pests: List[str] = Field(default_factory=list, description="Target pests")
    
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


class PestTimingGuidance(BaseModel):
    """Pest timing guidance."""
    
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
    """Critical timing period for pest management."""
    
    period_name: str = Field(..., description="Period name")
    start_date: date = Field(..., description="Period start date")
    end_date: date = Field(..., description="Period end date")
    importance_level: str = Field(..., description="Importance level")
    activities: List[str] = Field(default_factory=list, description="Recommended activities")
    pests_of_concern: List[str] = Field(default_factory=list, description="Pests of concern")


class MonitoringPeriod(BaseModel):
    """Monitoring period definition."""
    
    period_name: str = Field(..., description="Period name")
    frequency: str = Field(..., description="Monitoring frequency")
    duration_days: int = Field(..., description="Duration in days")
    focus_areas: List[str] = Field(default_factory=list, description="Areas to focus on")
    indicators: List[str] = Field(default_factory=list, description="Key indicators to monitor")


class ActionThreshold(BaseModel):
    """Action threshold definition."""
    
    pest_name: str = Field(..., description="Pest name")
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
    pests_addressed: List[str] = Field(default_factory=list, description="Pests addressed")


class ResistanceAnalysis(BaseModel):
    """Resistance durability and stacking analysis."""
    
    # Resistance durability
    resistance_durability: Dict[str, ResistanceDurability] = Field(default_factory=dict, description="Resistance durability by pest")
    durability_factors: List[str] = Field(default_factory=list, description="Factors affecting durability")
    
    # Resistance stacking
    resistance_stacking: List["ResistanceStack"] = Field(default_factory=list, description="Resistance stacking combinations")
    stacking_benefits: List[str] = Field(default_factory=list, description="Benefits of resistance stacking")
    
    # Refuge requirements
    refuge_requirements: Optional["RefugeRequirements"] = Field(None, description="Refuge requirements")
    refuge_strategies: List[str] = Field(default_factory=list, description="Refuge strategies")
    
    # Management implications
    management_implications: List[str] = Field(default_factory=list, description="Management implications")
    long_term_considerations: List[str] = Field(default_factory=list, description="Long-term considerations")


class ResistanceStack(BaseModel):
    """Resistance stacking combination."""
    
    stack_name: str = Field(..., description="Stack name")
    resistance_genes: List[str] = Field(default_factory=list, description="Genes in the stack")
    target_pests: List[str] = Field(default_factory=list, description="Target pests")
    effectiveness: float = Field(..., ge=0.0, le=1.0, description="Stack effectiveness")
    durability: ResistanceDurability = Field(..., description="Stack durability")
    management_requirements: List[str] = Field(default_factory=list, description="Management requirements")


class RefugeRequirements(BaseModel):
    """Refuge requirements for resistance management."""
    
    refuge_percentage: float = Field(..., ge=0.0, le=100.0, description="Required refuge percentage")
    refuge_type: str = Field(..., description="Type of refuge (structured, unstructured)")
    refuge_location: str = Field(..., description="Refuge location requirements")
    refuge_management: List[str] = Field(default_factory=list, description="Refuge management requirements")
    compliance_requirements: List[str] = Field(default_factory=list, description="Compliance requirements")


class PestForecast(BaseModel):
    """Pest pressure forecast."""
    
    forecast_period_days: int = Field(..., description="Forecast period in days")
    forecast_date: date = Field(..., description="Forecast date")
    
    # Forecast data
    predicted_pests: List["PestForecastEntry"] = Field(default_factory=list, description="Predicted pest pressures")
    overall_risk_trend: str = Field(..., description="Overall risk trend")
    
    # Confidence and accuracy
    forecast_confidence: float = Field(..., ge=0.0, le=1.0, description="Forecast confidence")
    accuracy_metrics: Optional[Dict[str, float]] = Field(None, description="Historical accuracy metrics")
    
    # Weather dependencies
    weather_dependencies: List[str] = Field(default_factory=list, description="Weather dependencies")
    weather_sensitivity: str = Field(..., description="Weather sensitivity level")


class PestForecastEntry(BaseModel):
    """Individual pest forecast entry."""
    
    pest_id: str = Field(..., description="Pest identifier")
    pest_name: str = Field(..., description="Pest name")
    
    # Forecast predictions
    predicted_severity: PestSeverity = Field(..., description="Predicted severity")
    predicted_risk_level: PestRiskLevel = Field(..., description="Predicted risk level")
    probability_of_occurrence: float = Field(..., ge=0.0, le=1.0, description="Probability of occurrence")
    
    # Timing predictions
    predicted_onset_date: Optional[date] = Field(None, description="Predicted onset date")
    predicted_peak_date: Optional[date] = Field(None, description="Predicted peak date")
    
    # Confidence and factors
    forecast_confidence: float = Field(..., ge=0.0, le=1.0, description="Forecast confidence")
    key_factors: List[str] = Field(default_factory=list, description="Key influencing factors")
    uncertainty_factors: List[str] = Field(default_factory=list, description="Uncertainty factors")


class PestTrends(BaseModel):
    """Historical pest trends."""
    
    analysis_period_years: int = Field(..., description="Analysis period in years")
    trend_data: List["PestTrendEntry"] = Field(default_factory=list, description="Trend data entries")
    
    # Overall trends
    overall_trend_direction: str = Field(..., description="Overall trend direction")
    trend_significance: str = Field(..., description="Trend significance level")
    
    # Seasonal patterns
    seasonal_patterns: Dict[str, Any] = Field(default_factory=dict, description="Seasonal patterns")
    peak_seasons: List[str] = Field(default_factory=list, description="Peak pest seasons")
    
    # Long-term changes
    long_term_changes: List[str] = Field(default_factory=list, description="Long-term changes")
    climate_impacts: List[str] = Field(default_factory=list, description="Climate change impacts")


class PestTrendEntry(BaseModel):
    """Individual pest trend entry."""
    
    pest_id: str = Field(..., description="Pest identifier")
    pest_name: str = Field(..., description="Pest name")
    
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