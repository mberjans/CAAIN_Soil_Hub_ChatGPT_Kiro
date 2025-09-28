"""
Crop Suitability Matrix Models

Pydantic models for comprehensive crop suitability matrices and scoring
within the crop taxonomy system.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union, Tuple
from datetime import date, datetime
from enum import Enum
from uuid import UUID


# ============================================================================
# SUITABILITY SCORING ENUMERATIONS
# ============================================================================

class SuitabilityLevel(str, Enum):
    """Suitability scoring levels."""
    EXCELLENT = "excellent"      # 90-100%
    GOOD = "good"               # 70-89%
    MODERATE = "moderate"       # 50-69%
    POOR = "poor"              # 30-49%
    UNSUITABLE = "unsuitable"   # 0-29%


class RiskLevel(str, Enum):
    """Risk assessment levels."""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class EnvironmentalFactor(str, Enum):
    """Environmental factors affecting crop suitability."""
    CLIMATE_TEMPERATURE = "climate_temperature"
    CLIMATE_PRECIPITATION = "climate_precipitation"
    CLIMATE_HUMIDITY = "climate_humidity"
    CLIMATE_WIND = "climate_wind"
    SOIL_PH = "soil_ph"
    SOIL_TEXTURE = "soil_texture"
    SOIL_DRAINAGE = "soil_drainage"
    SOIL_FERTILITY = "soil_fertility"
    SOIL_SALINITY = "soil_salinity"
    PEST_PRESSURE = "pest_pressure"
    DISEASE_PRESSURE = "disease_pressure"
    WEED_PRESSURE = "weed_pressure"


class ManagementFactor(str, Enum):
    """Management factors affecting crop suitability."""
    IRRIGATION_AVAILABILITY = "irrigation_availability"
    FERTILIZER_ACCESS = "fertilizer_access"
    EQUIPMENT_AVAILABILITY = "equipment_availability"
    LABOR_AVAILABILITY = "labor_availability"
    MARKET_ACCESS = "market_access"
    TRANSPORTATION = "transportation"
    STORAGE_FACILITIES = "storage_facilities"
    PROCESSING_FACILITIES = "processing_facilities"


class EconomicFactor(str, Enum):
    """Economic factors affecting crop suitability."""
    SEED_COST = "seed_cost"
    INPUT_COSTS = "input_costs"
    LABOR_COSTS = "labor_costs"
    MARKET_PRICE = "market_price"
    TRANSPORTATION_COSTS = "transportation_costs"
    STORAGE_COSTS = "storage_costs"
    PROCESSING_COSTS = "processing_costs"
    PROFIT_MARGIN = "profit_margin"


# ============================================================================
# SUITABILITY SCORING MODELS
# ============================================================================

class SuitabilityScore(BaseModel):
    """Individual suitability score for a specific factor."""
    
    factor: Union[EnvironmentalFactor, ManagementFactor, EconomicFactor] = Field(
        ..., description="Factor being scored"
    )
    score: float = Field(..., ge=0.0, le=1.0, description="Suitability score (0-1)")
    level: SuitabilityLevel = Field(..., description="Qualitative suitability level")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the score")
    weight: float = Field(default=1.0, ge=0.0, le=1.0, description="Weight for this factor in overall scoring")
    explanation: Optional[str] = Field(None, description="Explanation of the score")
    data_sources: List[str] = Field(default_factory=list, description="Sources of data used for scoring")


class EnvironmentalSuitabilityMatrix(BaseModel):
    """Environmental suitability matrix for a crop."""
    
    crop_id: UUID = Field(..., description="Crop identifier")
    crop_name: str = Field(..., description="Crop name")
    
    # Climate suitability scores
    temperature_suitability: SuitabilityScore = Field(..., description="Temperature suitability")
    precipitation_suitability: SuitabilityScore = Field(..., description="Precipitation suitability")
    humidity_suitability: SuitabilityScore = Field(..., description="Humidity suitability")
    wind_suitability: SuitabilityScore = Field(..., description="Wind suitability")
    
    # Soil suitability scores
    ph_suitability: SuitabilityScore = Field(..., description="Soil pH suitability")
    texture_suitability: SuitabilityScore = Field(..., description="Soil texture suitability")
    drainage_suitability: SuitabilityScore = Field(..., description="Soil drainage suitability")
    fertility_suitability: SuitabilityScore = Field(..., description="Soil fertility suitability")
    salinity_suitability: SuitabilityScore = Field(..., description="Soil salinity suitability")
    
    # Pest and disease suitability scores
    pest_pressure_suitability: SuitabilityScore = Field(..., description="Pest pressure suitability")
    disease_pressure_suitability: SuitabilityScore = Field(..., description="Disease pressure suitability")
    weed_pressure_suitability: SuitabilityScore = Field(..., description="Weed pressure suitability")
    
    # Overall environmental score
    overall_environmental_score: float = Field(..., ge=0.0, le=1.0, description="Overall environmental suitability")
    environmental_level: SuitabilityLevel = Field(..., description="Overall environmental suitability level")


class ManagementSuitabilityMatrix(BaseModel):
    """Management suitability matrix for a crop."""
    
    crop_id: UUID = Field(..., description="Crop identifier")
    crop_name: str = Field(..., description="Crop name")
    
    # Infrastructure suitability scores
    irrigation_suitability: SuitabilityScore = Field(..., description="Irrigation availability suitability")
    fertilizer_suitability: SuitabilityScore = Field(..., description="Fertilizer access suitability")
    equipment_suitability: SuitabilityScore = Field(..., description="Equipment availability suitability")
    labor_suitability: SuitabilityScore = Field(..., description="Labor availability suitability")
    
    # Market and logistics suitability scores
    market_access_suitability: SuitabilityScore = Field(..., description="Market access suitability")
    transportation_suitability: SuitabilityScore = Field(..., description="Transportation suitability")
    storage_suitability: SuitabilityScore = Field(..., description="Storage facilities suitability")
    processing_suitability: SuitabilityScore = Field(..., description="Processing facilities suitability")
    
    # Overall management score
    overall_management_score: float = Field(..., ge=0.0, le=1.0, description="Overall management suitability")
    management_level: SuitabilityLevel = Field(..., description="Overall management suitability level")


class EconomicSuitabilityMatrix(BaseModel):
    """Economic suitability matrix for a crop."""
    
    crop_id: UUID = Field(..., description="Crop identifier")
    crop_name: str = Field(..., description="Crop name")
    
    # Cost suitability scores
    seed_cost_suitability: SuitabilityScore = Field(..., description="Seed cost suitability")
    input_cost_suitability: SuitabilityScore = Field(..., description="Input cost suitability")
    labor_cost_suitability: SuitabilityScore = Field(..., description="Labor cost suitability")
    transportation_cost_suitability: SuitabilityScore = Field(..., description="Transportation cost suitability")
    storage_cost_suitability: SuitabilityScore = Field(..., description="Storage cost suitability")
    processing_cost_suitability: SuitabilityScore = Field(..., description="Processing cost suitability")
    
    # Revenue suitability scores
    market_price_suitability: SuitabilityScore = Field(..., description="Market price suitability")
    profit_margin_suitability: SuitabilityScore = Field(..., description="Profit margin suitability")
    
    # Overall economic score
    overall_economic_score: float = Field(..., ge=0.0, le=1.0, description="Overall economic suitability")
    economic_level: SuitabilityLevel = Field(..., description="Overall economic suitability level")


class ComprehensiveSuitabilityMatrix(BaseModel):
    """Comprehensive suitability matrix combining all factors."""
    
    crop_id: UUID = Field(..., description="Crop identifier")
    crop_name: str = Field(..., description="Crop name")
    variety_id: Optional[UUID] = Field(None, description="Specific variety identifier")
    variety_name: Optional[str] = Field(None, description="Specific variety name")
    
    # Component matrices
    environmental_matrix: EnvironmentalSuitabilityMatrix = Field(..., description="Environmental suitability")
    management_matrix: ManagementSuitabilityMatrix = Field(..., description="Management suitability")
    economic_matrix: EconomicSuitabilityMatrix = Field(..., description="Economic suitability")
    
    # Overall scores
    overall_suitability_score: float = Field(..., ge=0.0, le=1.0, description="Overall suitability score")
    overall_suitability_level: SuitabilityLevel = Field(..., description="Overall suitability level")
    
    # Risk assessment
    risk_level: RiskLevel = Field(..., description="Overall risk level")
    risk_factors: List[str] = Field(default_factory=list, description="Key risk factors")
    mitigation_strategies: List[str] = Field(default_factory=list, description="Recommended mitigation strategies")
    
    # Confidence and metadata
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Overall confidence in the assessment")
    data_completeness: float = Field(..., ge=0.0, le=1.0, description="Completeness of underlying data")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    # Recommendations
    recommendations: List[str] = Field(default_factory=list, description="Specific recommendations")
    adaptation_strategies: List[str] = Field(default_factory=list, description="Adaptation strategies")


# ============================================================================
# REQUEST AND RESPONSE MODELS
# ============================================================================

class SuitabilityMatrixRequest(BaseModel):
    """Request model for generating suitability matrices."""
    
    crop_id: Optional[UUID] = Field(None, description="Specific crop identifier")
    variety_id: Optional[UUID] = Field(None, description="Specific variety identifier")
    crop_name: Optional[str] = Field(None, description="Crop name for search")
    
    # Location context
    location: Optional[Dict[str, Any]] = Field(None, description="Location information")
    climate_zone: Optional[str] = Field(None, description="Climate zone")
    soil_conditions: Optional[Dict[str, Any]] = Field(None, description="Soil conditions")
    
    # Environmental context
    pest_pressure: Optional[Dict[str, Any]] = Field(None, description="Pest pressure levels")
    disease_pressure: Optional[Dict[str, Any]] = Field(None, description="Disease pressure levels")
    weather_patterns: Optional[Dict[str, Any]] = Field(None, description="Weather patterns")
    
    # Management context
    management_capabilities: Optional[Dict[str, Any]] = Field(None, description="Management capabilities")
    infrastructure: Optional[Dict[str, Any]] = Field(None, description="Infrastructure availability")
    
    # Economic context
    market_conditions: Optional[Dict[str, Any]] = Field(None, description="Market conditions")
    cost_structure: Optional[Dict[str, Any]] = Field(None, description="Cost structure")
    
    # Scoring preferences
    include_environmental: bool = Field(default=True, description="Include environmental scoring")
    include_management: bool = Field(default=True, description="Include management scoring")
    include_economic: bool = Field(default=True, description="Include economic scoring")
    
    # Weighting preferences
    environmental_weight: float = Field(default=0.4, ge=0.0, le=1.0, description="Weight for environmental factors")
    management_weight: float = Field(default=0.3, ge=0.0, le=1.0, description="Weight for management factors")
    economic_weight: float = Field(default=0.3, ge=0.0, le=1.0, description="Weight for economic factors")
    
    @validator('environmental_weight', 'management_weight', 'economic_weight')
    def validate_weights(cls, v, values):
        """Ensure weights sum to 1.0."""
        total_weight = sum([
            values.get('environmental_weight', 0.4),
            values.get('management_weight', 0.3),
            values.get('economic_weight', 0.3)
        ])
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError("Weights must sum to 1.0")
        return v


class SuitabilityMatrixResponse(BaseModel):
    """Response model for suitability matrix queries."""
    
    request_id: str = Field(..., description="Unique request identifier")
    matrices: List[ComprehensiveSuitabilityMatrix] = Field(..., description="Generated suitability matrices")
    
    # Summary information
    total_crops_evaluated: int = Field(..., description="Total number of crops evaluated")
    top_suitable_crops: List[Dict[str, Any]] = Field(default_factory=list, description="Top suitable crops")
    
    # Metadata
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    data_sources_used: List[str] = Field(default_factory=list, description="Data sources used")
    confidence_summary: Dict[str, float] = Field(default_factory=dict, description="Confidence summary by category")
    
    # Recommendations
    overall_recommendations: List[str] = Field(default_factory=list, description="Overall recommendations")
    risk_warnings: List[str] = Field(default_factory=list, description="Risk warnings")


class SuitabilityComparisonRequest(BaseModel):
    """Request model for comparing suitability matrices."""
    
    crop_ids: List[UUID] = Field(..., min_items=2, max_items=10, description="Crop identifiers to compare")
    variety_ids: Optional[List[UUID]] = Field(None, description="Specific variety identifiers")
    
    # Context (same as SuitabilityMatrixRequest)
    location: Optional[Dict[str, Any]] = Field(None, description="Location information")
    climate_zone: Optional[str] = Field(None, description="Climate zone")
    soil_conditions: Optional[Dict[str, Any]] = Field(None, description="Soil conditions")
    pest_pressure: Optional[Dict[str, Any]] = Field(None, description="Pest pressure levels")
    disease_pressure: Optional[Dict[str, Any]] = Field(None, description="Disease pressure levels")
    management_capabilities: Optional[Dict[str, Any]] = Field(None, description="Management capabilities")
    market_conditions: Optional[Dict[str, Any]] = Field(None, description="Market conditions")
    
    # Comparison preferences
    include_detailed_scores: bool = Field(default=True, description="Include detailed factor scores")
    include_recommendations: bool = Field(default=True, description="Include recommendations")
    include_risk_assessment: bool = Field(default=True, description="Include risk assessment")


class SuitabilityComparisonResponse(BaseModel):
    """Response model for suitability matrix comparisons."""
    
    request_id: str = Field(..., description="Unique request identifier")
    comparison_results: List[ComprehensiveSuitabilityMatrix] = Field(..., description="Comparison results")
    
    # Comparison summary
    ranking: List[Dict[str, Any]] = Field(..., description="Ranked comparison results")
    key_differences: List[Dict[str, Any]] = Field(default_factory=list, description="Key differences between crops")
    
    # Metadata
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    comparison_criteria: List[str] = Field(default_factory=list, description="Criteria used for comparison")


# ============================================================================
# RISK ASSESSMENT MODELS
# ============================================================================

class RiskFactor(BaseModel):
    """Individual risk factor assessment."""
    
    factor_name: str = Field(..., description="Risk factor name")
    risk_level: RiskLevel = Field(..., description="Risk level")
    probability: float = Field(..., ge=0.0, le=1.0, description="Probability of occurrence")
    impact: float = Field(..., ge=0.0, le=1.0, description="Impact if it occurs")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Combined risk score")
    description: str = Field(..., description="Risk description")
    mitigation_strategies: List[str] = Field(default_factory=list, description="Mitigation strategies")
    monitoring_indicators: List[str] = Field(default_factory=list, description="Monitoring indicators")


class RiskAssessmentMatrix(BaseModel):
    """Comprehensive risk assessment matrix."""
    
    crop_id: UUID = Field(..., description="Crop identifier")
    crop_name: str = Field(..., description="Crop name")
    
    # Risk factors
    climate_risks: List[RiskFactor] = Field(default_factory=list, description="Climate-related risks")
    soil_risks: List[RiskFactor] = Field(default_factory=list, description="Soil-related risks")
    pest_disease_risks: List[RiskFactor] = Field(default_factory=list, description="Pest and disease risks")
    market_risks: List[RiskFactor] = Field(default_factory=list, description="Market-related risks")
    management_risks: List[RiskFactor] = Field(default_factory=list, description="Management-related risks")
    
    # Overall risk assessment
    overall_risk_level: RiskLevel = Field(..., description="Overall risk level")
    overall_risk_score: float = Field(..., ge=0.0, le=1.0, description="Overall risk score")
    
    # Risk management
    risk_tolerance: RiskLevel = Field(..., description="Recommended risk tolerance")
    risk_mitigation_priority: List[str] = Field(default_factory=list, description="Priority mitigation strategies")
    
    # Metadata
    assessment_date: datetime = Field(default_factory=datetime.utcnow, description="Assessment date")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="Confidence in risk assessment")


# ============================================================================
# ADAPTATION STRATEGY MODELS
# ============================================================================

class AdaptationStrategy(BaseModel):
    """Adaptation strategy for improving crop suitability."""
    
    strategy_name: str = Field(..., description="Strategy name")
    strategy_type: str = Field(..., description="Type of strategy")
    description: str = Field(..., description="Strategy description")
    
    # Implementation details
    implementation_cost: Optional[str] = Field(None, description="Implementation cost level")
    implementation_time: Optional[str] = Field(None, description="Implementation time required")
    complexity: str = Field(..., description="Implementation complexity")
    
    # Expected benefits
    suitability_improvement: float = Field(..., ge=0.0, le=1.0, description="Expected suitability improvement")
    risk_reduction: float = Field(..., ge=0.0, le=1.0, description="Expected risk reduction")
    
    # Requirements
    requirements: List[str] = Field(default_factory=list, description="Implementation requirements")
    constraints: List[str] = Field(default_factory=list, description="Implementation constraints")
    
    # Success factors
    success_factors: List[str] = Field(default_factory=list, description="Key success factors")
    monitoring_metrics: List[str] = Field(default_factory=list, description="Monitoring metrics")


class AdaptationPlan(BaseModel):
    """Comprehensive adaptation plan for crop suitability improvement."""
    
    crop_id: UUID = Field(..., description="Crop identifier")
    crop_name: str = Field(..., description="Crop name")
    
    # Current state
    current_suitability_score: float = Field(..., ge=0.0, le=1.0, description="Current suitability score")
    current_risk_level: RiskLevel = Field(..., description="Current risk level")
    
    # Adaptation strategies
    strategies: List[AdaptationStrategy] = Field(..., description="Adaptation strategies")
    
    # Implementation plan
    implementation_phases: List[Dict[str, Any]] = Field(default_factory=list, description="Implementation phases")
    timeline: Dict[str, Any] = Field(default_factory=dict, description="Implementation timeline")
    
    # Expected outcomes
    target_suitability_score: float = Field(..., ge=0.0, le=1.0, description="Target suitability score")
    target_risk_level: RiskLevel = Field(..., description="Target risk level")
    
    # Investment requirements
    total_investment: Optional[str] = Field(None, description="Total investment required")
    payback_period: Optional[str] = Field(None, description="Expected payback period")
    roi_estimate: Optional[str] = Field(None, description="Expected ROI")
    
    # Success metrics
    success_metrics: List[str] = Field(default_factory=list, description="Success metrics")
    monitoring_plan: List[str] = Field(default_factory=list, description="Monitoring plan")