"""
Crop Variety and Regional Adaptation Models

Pydantic models for enhanced crop varieties, regional adaptations,
and variety-specific recommendations within the crop taxonomy system.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union, Tuple
from datetime import date, datetime
from enum import Enum
from uuid import UUID


# ============================================================================
# VARIETY AND ADAPTATION ENUMERATIONS
# ============================================================================

class SeedAvailability(str, Enum):
    """Seed availability levels."""
    WIDELY_AVAILABLE = "widely_available"
    LIMITED = "limited"
    SPECIALTY = "specialty"
    RESEARCH_ONLY = "research_only"


class RelativeSeedCost(str, Enum):
    """Relative seed cost levels."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    PREMIUM = "premium"


class SeedAvailabilityStatus(str, Enum):
    """Detailed seed availability status values."""
    IN_STOCK = "in_stock"
    LIMITED = "limited"
    PREORDER = "preorder"
    RETIRED = "retired"
    DISCONTINUED = "discontinued"


class PatentStatus(str, Enum):
    """Patent lifecycle states for varieties."""
    NONE = "none"
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    WAIVED = "waived"


class SeedCompanyOffering(BaseModel):
    """Seed company offering information for a variety."""

    company_name: str = Field(..., description="Seed company name")
    product_code: Optional[str] = Field(None, description="Company-specific product identifier")
    availability_status: SeedAvailabilityStatus = Field(
        SeedAvailabilityStatus.IN_STOCK, description="Detailed availability status"
    )
    distribution_regions: List[str] = Field(default_factory=list, description="Regions where seed is offered")
    price_per_unit: Optional[float] = Field(None, ge=0.0, description="Price per standard unit")
    price_unit: Optional[str] = Field(None, description="Unit used for pricing (e.g., bag, unit)")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")
    notes: Optional[str] = Field(None, description="Additional notes about availability")


class TraitStackEntry(BaseModel):
    """Stacked trait information for a variety."""

    trait_name: str = Field(..., description="Trait or technology name")
    trait_category: Optional[str] = Field(None, description="Trait category (herbicide tolerance, insect resistance, etc.)")
    trait_description: Optional[str] = Field(None, description="Description of the trait benefits")
    trait_source: Optional[str] = Field(None, description="Source or provider of the trait")


class RegionalPerformanceEntry(BaseModel):
    """Regional performance information for a variety."""

    region_name: str = Field(..., description="Region name or code")
    climate_zone: Optional[str] = Field(None, description="Primary climate zone")
    soil_types: List[str] = Field(default_factory=list, description="Supported soil types")
    performance_index: Optional[float] = Field(None, ge=0.0, le=1.0, description="Normalized performance index")
    average_yield: Optional[float] = Field(None, ge=0.0, description="Average yield in regional trials")
    trials_count: Optional[int] = Field(None, ge=0, description="Number of supporting trials")
    last_validation: Optional[datetime] = Field(None, description="Last validation timestamp")
    notes: Optional[str] = Field(None, description="Additional performance notes")


class RegionType(str, Enum):
    """Types of regional classifications."""
    STATE = "state"
    MULTI_STATE = "multi_state"
    COUNTY = "county"
    CLIMATE_ZONE = "climate_zone"
    ECOREGION = "ecoregion"
    CUSTOM = "custom"


class ProductionPotential(str, Enum):
    """Production potential levels."""
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"


class RiskLevel(str, Enum):
    """Risk assessment levels."""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class MarketDemand(str, Enum):
    """Market demand levels."""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class InfrastructureSupport(str, Enum):
    """Infrastructure support levels."""
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"


# ============================================================================
# ENHANCED CROP VARIETY MODELS
# ============================================================================

class DiseaseResistanceEntry(BaseModel):
    """Individual disease resistance entry."""
    
    disease_name: str = Field(..., description="Disease name")
    pathogen_type: Optional[str] = Field(None, description="Pathogen type (fungal, bacterial, viral, etc.)")
    resistance_level: str = Field(..., description="Resistance level (immune, resistant, tolerant, susceptible)")
    resistance_genes: Optional[List[str]] = Field(None, description="Known resistance genes")
    field_effectiveness: Optional[float] = Field(None, ge=0.0, le=1.0, description="Field effectiveness score")
    
    @validator('resistance_level')
    def validate_resistance_level(cls, v):
        """Validate resistance level values."""
        valid_levels = {'immune', 'resistant', 'tolerant', 'susceptible'}
        if v.lower() not in valid_levels:
            raise ValueError(f"Resistance level must be one of: {valid_levels}")
        return v.lower()


class PestResistanceEntry(BaseModel):
    """Individual pest resistance entry."""
    
    pest_name: str = Field(..., description="Pest name")
    pest_type: Optional[str] = Field(None, description="Pest type (insect, nematode, mite, etc.)")
    resistance_mechanism: Optional[str] = Field(None, description="Resistance mechanism")
    effectiveness_rating: Optional[int] = Field(None, ge=1, le=5, description="Effectiveness rating (1-5)")
    field_validation: Optional[bool] = Field(None, description="Field validated resistance")


class QualityCharacteristic(BaseModel):
    """Quality characteristic entry."""
    
    characteristic_name: str = Field(..., description="Quality characteristic name")
    value: Optional[str] = Field(None, description="Characteristic value")
    measurement_unit: Optional[str] = Field(None, description="Unit of measurement")
    grade_or_rating: Optional[str] = Field(None, description="Quality grade or rating")
    market_significance: Optional[str] = Field(None, description="Market significance level")


class PlantingPopulationRecommendation(BaseModel):
    """Planting population recommendation for specific conditions."""
    
    condition_type: str = Field(..., description="Condition type (region, soil_type, etc.)")
    condition_value: str = Field(..., description="Specific condition value")
    recommended_population: int = Field(..., ge=0, description="Recommended plants per acre")
    population_range_min: Optional[int] = Field(None, ge=0, description="Minimum population")
    population_range_max: Optional[int] = Field(None, ge=0, description="Maximum population")
    notes: Optional[str] = Field(None, description="Additional planting notes")


class EnhancedCropVariety(BaseModel):
    """Enhanced crop variety with comprehensive characteristics."""
    
    variety_id: Optional[UUID] = Field(None, description="Unique variety identifier")
    crop_id: UUID = Field(..., description="Associated crop identifier")
    
    # Variety identification
    variety_name: str = Field(..., description="Variety name")
    variety_code: Optional[str] = Field(None, description="Variety code or number")
    breeder_company: Optional[str] = Field(None, description="Breeding company")
    parent_varieties: List[str] = Field(default_factory=list, description="Parent variety names")
    seed_companies: List[SeedCompanyOffering] = Field(default_factory=list, description="Seed company offerings")

    
    # Maturity and timing characteristics
    relative_maturity: Optional[int] = Field(None, description="Relative maturity (days or units)")
    maturity_group: Optional[str] = Field(None, description="Maturity group classification")
    days_to_emergence: Optional[int] = Field(None, ge=0, description="Days to emergence")
    days_to_flowering: Optional[int] = Field(None, ge=0, description="Days to flowering")
    days_to_physiological_maturity: Optional[int] = Field(None, ge=0, description="Days to physiological maturity")
    
    # Performance characteristics
    yield_potential_percentile: Optional[int] = Field(None, ge=0, le=100, description="Yield potential percentile")
    yield_stability_rating: Optional[float] = Field(None, ge=0.0, le=10.0, description="Yield stability (0-10)")
    market_acceptance_score: Optional[float] = Field(None, ge=0.0, le=5.0, description="Market acceptance score (0-5)")
    standability_rating: Optional[int] = Field(None, ge=1, le=10, description="Standability rating (1-10)")
    
    # Resistance and tolerance traits
    disease_resistances: List[DiseaseResistanceEntry] = Field(default_factory=list, description="Disease resistance data")
    pest_resistances: List[PestResistanceEntry] = Field(default_factory=list, description="Pest resistance data")
    herbicide_tolerances: List[str] = Field(default_factory=list, description="Herbicide tolerance traits")
    stress_tolerances: List[str] = Field(default_factory=list, description="Abiotic stress tolerances")
    
    # Quality traits
    quality_characteristics: List[QualityCharacteristic] = Field(default_factory=list, description="Quality traits")
    protein_content_range: Optional[str] = Field(None, description="Protein content range")
    oil_content_range: Optional[str] = Field(None, description="Oil content range")
    
    # Adaptation and recommendations
    adapted_regions: List[str] = Field(default_factory=list, description="Adapted geographic regions")
    recommended_planting_populations: List[PlantingPopulationRecommendation] = Field(
        default_factory=list, description="Planting population recommendations"
    )
    special_management_notes: Optional[str] = Field(None, description="Special management requirements")
    trait_stack: List[TraitStackEntry] = Field(default_factory=list, description="Stacked trait packages")
    regional_performance_data: List[RegionalPerformanceEntry] = Field(default_factory=list, description="Regional performance metrics")
    
    # Commercial information
    seed_availability: Optional[SeedAvailability] = Field(None, description="Seed availability level")
    seed_availability_status: Optional[SeedAvailabilityStatus] = Field(None, description="Detailed seed availability status")
    relative_seed_cost: Optional[RelativeSeedCost] = Field(None, description="Relative seed cost")
    technology_package: Optional[str] = Field(None, description="Associated technology package")
    
    # Regulatory and certification status
    organic_approved: Optional[bool] = Field(None, description="Approved for organic production")
    non_gmo_certified: Optional[bool] = Field(None, description="Non-GMO certified")
    registration_year: Optional[int] = Field(None, ge=1900, description="Year of registration")
    release_year: Optional[int] = Field(None, ge=1900, description="Year of commercial release")
    patent_protected: bool = Field(default=False, description="Under patent protection")
    patent_status: Optional[PatentStatus] = Field(None, description="Patent lifecycle status")
    
    # Status and metadata
    is_active: bool = Field(default=True, description="Variety is actively available")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    @validator('variety_name')
    def validate_variety_name(cls, v):
        """Validate variety name is not empty."""
        if not v or len(v.strip()) < 1:
            raise ValueError("Variety name cannot be empty")
        return v.strip()
    
    @validator('registration_year', 'release_year')
    def validate_year_fields(cls, v, field):
        """Validate registration and release year ranges."""
        current_year = datetime.now().year
        if v is not None and (v < 1900 or v > current_year + 5):
            field_label = field.name.replace('_', ' ')
            raise ValueError(f"{field_label.capitalize()} must be between 1900 and {current_year + 5}")
        return v

    def get_disease_resistance_summary(self) -> Dict[str, str]:
        """Get summary of disease resistances."""
        summary = {}
        for resistance in self.disease_resistances:
            summary[resistance.disease_name] = resistance.resistance_level
        return summary

    def get_stress_tolerance_list(self) -> List[str]:
        """Get list of stress tolerances."""
        return self.stress_tolerances

    def is_herbicide_tolerant(self, herbicide: str) -> bool:
        """Check if variety is tolerant to specific herbicide."""
        return herbicide.lower() in [h.lower() for h in self.herbicide_tolerances]


# ============================================================================
# REGIONAL ADAPTATION MODELS
# ============================================================================

class RegionalPlantingDate(BaseModel):
    """Regional planting date information."""
    
    practice_type: str = Field(..., description="Practice type (conventional, no-till, etc.)")
    earliest_date: Optional[date] = Field(None, description="Earliest planting date")
    optimal_start: date = Field(..., description="Optimal planting window start")
    optimal_end: date = Field(..., description="Optimal planting window end")
    latest_date: Optional[date] = Field(None, description="Latest planting date")
    notes: Optional[str] = Field(None, description="Additional planting notes")


class RegionalHarvestDate(BaseModel):
    """Regional harvest date information."""
    
    harvest_type: str = Field(..., description="Harvest type (grain, silage, etc.)")
    earliest_date: Optional[date] = Field(None, description="Earliest harvest date")
    typical_start: date = Field(..., description="Typical harvest window start")
    typical_end: date = Field(..., description="Typical harvest window end")
    latest_date: Optional[date] = Field(None, description="Latest harvest date")
    notes: Optional[str] = Field(None, description="Harvest timing notes")


class CropRegionalAdaptation(BaseModel):
    """Regional adaptation data for crops."""
    
    adaptation_id: Optional[UUID] = Field(None, description="Unique adaptation identifier")
    crop_id: UUID = Field(..., description="Associated crop identifier")
    
    # Geographic scope
    region_name: str = Field(..., description="Region name")
    region_type: RegionType = Field(..., description="Type of regional classification")
    country_code: str = Field(default="USA", description="Country code")
    
    # Geographic boundaries (simplified - could be enhanced with PostGIS)
    latitude_range: Optional[Dict[str, float]] = Field(None, description="Latitude range (min, max)")
    longitude_range: Optional[Dict[str, float]] = Field(None, description="Longitude range (min, max)")
    
    # Adaptation ratings
    adaptation_score: Optional[int] = Field(None, ge=1, le=10, description="Adaptation score (1-10)")
    production_potential: Optional[ProductionPotential] = Field(None, description="Production potential")
    risk_level: Optional[RiskLevel] = Field(None, description="Production risk level")
    
    # Regional timing information
    typical_planting_dates: List[RegionalPlantingDate] = Field(
        default_factory=list, description="Regional planting date information"
    )
    typical_harvest_dates: List[RegionalHarvestDate] = Field(
        default_factory=list, description="Regional harvest date information"
    )
    
    # Regional characteristics
    common_varieties: List[str] = Field(default_factory=list, description="Commonly grown varieties")
    regional_challenges: List[str] = Field(default_factory=list, description="Common production challenges")
    management_considerations: List[str] = Field(default_factory=list, description="Regional management considerations")
    
    # Economic factors
    market_demand: Optional[MarketDemand] = Field(None, description="Regional market demand")
    infrastructure_support: Optional[InfrastructureSupport] = Field(None, description="Infrastructure support level")
    
    # Metadata
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    @validator('region_name')
    def validate_region_name(cls, v):
        """Validate region name is not empty."""
        if not v or len(v.strip()) < 1:
            raise ValueError("Region name cannot be empty")
        return v.strip()

    def get_planting_window(self, practice_type: str = "conventional") -> Optional[Dict[str, date]]:
        """Get planting window for specific practice type."""
        for planting_info in self.typical_planting_dates:
            if planting_info.practice_type.lower() == practice_type.lower():
                return {
                    "optimal_start": planting_info.optimal_start,
                    "optimal_end": planting_info.optimal_end,
                    "earliest": planting_info.earliest_date,
                    "latest": planting_info.latest_date
                }
        return None

    def get_harvest_window(self, harvest_type: str = "grain") -> Optional[Dict[str, date]]:
        """Get harvest window for specific harvest type."""
        for harvest_info in self.typical_harvest_dates:
            if harvest_info.harvest_type.lower() == harvest_type.lower():
                return {
                    "typical_start": harvest_info.typical_start,
                    "typical_end": harvest_info.typical_end,
                    "earliest": harvest_info.earliest_date,
                    "latest": harvest_info.latest_date
                }
        return None


# ============================================================================
# VARIETY RECOMMENDATION MODELS
# ============================================================================

class VarietyRecommendationCriteria(BaseModel):
    """Criteria for variety selection and recommendations."""
    
    # Location and environment
    target_region: Optional[str] = Field(None, description="Target growing region")
    hardiness_zone: Optional[str] = Field(None, description="USDA hardiness zone")
    soil_conditions: Optional[Dict[str, Any]] = Field(None, description="Soil condition requirements")
    climate_conditions: Optional[Dict[str, Any]] = Field(None, description="Climate requirements")
    
    # Performance requirements
    yield_priority: bool = Field(default=True, description="Prioritize high yield potential")
    quality_priority: bool = Field(default=False, description="Prioritize quality characteristics")
    stability_priority: bool = Field(default=True, description="Prioritize yield stability")
    
    # Disease and pest management
    required_disease_resistances: List[str] = Field(default_factory=list, description="Required disease resistances")
    required_pest_resistances: List[str] = Field(default_factory=list, description="Required pest resistances")
    herbicide_program: Optional[List[str]] = Field(None, description="Planned herbicide program")
    
    # Management constraints
    maturity_requirements: Optional[Dict[str, int]] = Field(None, description="Maturity timing requirements")
    planting_population_constraints: Optional[Dict[str, int]] = Field(None, description="Population constraints")
    
    # Economic considerations
    seed_cost_budget: Optional[str] = Field(None, description="Seed cost budget level")
    market_requirements: Optional[List[str]] = Field(None, description="Market quality requirements")
    
    # Certification requirements
    organic_production: bool = Field(default=False, description="Organic production system")
    non_gmo_required: bool = Field(default=False, description="Non-GMO requirement")


class VarietyRecommendation(BaseModel):
    """Individual variety recommendation with scoring and confidence context."""
    
    # Recommended variety identifiers
    variety: Optional[EnhancedCropVariety] = Field(None, description="Full variety record if available")
    variety_id: Optional[UUID] = Field(None, description="Unique identifier for the variety")
    variety_name: Optional[str] = Field(None, description="Display name for the variety")
    variety_code: Optional[str] = Field(None, description="Breeder or seed company code")
    
    # Recommendation scoring
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Overall recommendation score")
    suitability_factors: Dict[str, float] = Field(default_factory=dict, description="Suitability factors with scores")
    individual_scores: Dict[str, float] = Field(default_factory=dict, description="Raw factor scoring details")
    weighted_contributions: Dict[str, float] = Field(default_factory=dict, description="Weighted contribution of each factor")
    score_details: Dict[str, str] = Field(default_factory=dict, description="Narrative descriptions for each factor")
    
    # Specific assessments
    yield_expectation: Optional[str] = Field(None, description="Expected yield performance")
    risk_assessment: Optional[Any] = Field(None, description="Detailed risk assessment output")
    management_difficulty: Optional[str] = Field(None, description="Management difficulty level")
    performance_prediction: Optional[Dict[str, Any]] = Field(None, description="Performance prediction details")
    adaptation_strategies: List[Dict[str, Any]] = Field(default_factory=list, description="Adaptation strategy guidance")
    recommended_practices: List[str] = Field(default_factory=list, description="Recommended management practices")
    economic_analysis: Dict[str, Any] = Field(default_factory=dict, description="Economic analysis summary")
    
    # Advantages and considerations
    key_advantages: List[str] = Field(default_factory=list, description="Key advantages of this variety")
    potential_challenges: List[str] = Field(default_factory=list, description="Potential challenges")
    management_recommendations: List[str] = Field(default_factory=list, description="Management recommendations")
    
    # Economic analysis
    estimated_seed_cost_per_acre: Optional[float] = Field(None, description="Estimated seed cost per acre")
    cost_benefit_notes: Optional[str] = Field(None, description="Cost-benefit considerations")
    
    # Confidence and validation
    confidence_level: float = Field(default=0.8, ge=0.0, le=1.0, description="Recommendation confidence score")
    data_quality_score: float = Field(default=0.8, ge=0.0, le=1.0, description="Contribution from data quality")
    confidence_interval: Optional[Tuple[float, float]] = Field(None, description="Lower and upper bounds for confidence")
    uncertainty_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Overall uncertainty measure")
    confidence_breakdown: Dict[str, float] = Field(default_factory=dict, description="Confidence contribution by factor")
    confidence_explanations: List[str] = Field(default_factory=list, description="Narrative explanations for confidence scoring")
    reliability_indicators: Dict[str, str] = Field(default_factory=dict, description="Reliability indicators for UI display")

    class Config:
        extra = "allow"


class VarietyComparisonMatrix(BaseModel):
    """Matrix comparing multiple varieties across criteria."""
    
    comparison_id: str = Field(..., description="Unique comparison identifier")
    comparison_criteria: List[str] = Field(..., description="Criteria being compared")
    varieties: List[EnhancedCropVariety] = Field(..., description="Varieties being compared")
    
    # Comparison data
    performance_matrix: Dict[str, Dict[str, Any]] = Field(..., description="Performance data by variety and criteria")
    ranking_by_criteria: Dict[str, List[str]] = Field(..., description="Variety ranking by each criterion")
    
    # Summary analysis
    top_overall_varieties: List[str] = Field(..., description="Top varieties overall")
    best_for_criteria: Dict[str, str] = Field(..., description="Best variety for each criterion")
    
    # Trade-off analysis
    trade_off_analysis: Dict[str, str] = Field(default_factory=dict, description="Trade-off considerations")
    selection_guidance: List[str] = Field(default_factory=list, description="Selection guidance notes")


class VarietyComparisonDetail(BaseModel):
    """Detailed comparison metrics for a specific variety."""

    variety_id: Optional[UUID] = Field(None, description="Unique identifier for the variety")
    variety_name: str = Field(..., description="Display name for the variety")
    overall_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall comparison score")
    criteria_scores: Dict[str, float] = Field(default_factory=dict, description="Scores by evaluation criterion")
    qualitative_insights: Dict[str, str] = Field(default_factory=dict, description="Narrative insights by criterion")
    strengths: List[str] = Field(default_factory=list, description="Key strengths for the variety")
    considerations: List[str] = Field(default_factory=list, description="Considerations or watch-outs")
    best_fit_scenarios: List[str] = Field(default_factory=list, description="Scenarios where variety performs best")
    risk_rating: Optional[str] = Field(None, description="Risk profile description")


class VarietyTradeOff(BaseModel):
    """Trade-off guidance between varieties for specific focus areas."""

    focus_area: str = Field(..., description="Area of focus for the trade-off (yield, disease, etc.)")
    preferred_variety_name: str = Field(..., description="Variety preferred for this focus area")
    rationale: str = Field(..., description="Reason for the recommendation")


class VarietyComparisonSummary(BaseModel):
    """High-level summary of comparison insights."""

    best_overall_variety: Optional[str] = Field(None, description="Best overall variety name")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Overall confidence score")
    key_takeaways: List[str] = Field(default_factory=list, description="Key insights from the comparison")
    recommended_actions: List[str] = Field(default_factory=list, description="Recommended next actions")


class VarietyComparisonRequest(BaseModel):
    """Request payload for comparing multiple varieties."""

    request_id: str = Field(..., description="Unique request identifier")
    variety_ids: List[UUID] = Field(default_factory=list, description="Variety identifiers to compare")
    provided_varieties: List[EnhancedCropVariety] = Field(
        default_factory=list,
        description="Optional pre-fetched variety records to use directly"
    )
    crop_id: Optional[UUID] = Field(None, description="Associated crop identifier for context")
    comparison_context: Dict[str, Any] = Field(default_factory=dict, description="Environmental and management context")
    prioritized_factors: List[str] = Field(default_factory=list, description="Factors to prioritize in analysis")
    include_trade_offs: bool = Field(default=True, description="Include trade-off analysis in response")
    include_management_analysis: bool = Field(default=True, description="Include management requirement analysis")
    include_economic_analysis: bool = Field(default=True, description="Include economic considerations")

    @validator('request_id')
    def validate_request_id(cls, value: str) -> str:
        """Ensure request identifier is not empty."""
        if not value:
            raise ValueError("Request identifier cannot be empty")
        trimmed_value = value.strip()
        if len(trimmed_value) == 0:
            raise ValueError("Request identifier cannot be empty")
        return trimmed_value


class VarietyComparisonResponse(BaseModel):
    """Response containing comprehensive variety comparison analysis."""

    request_id: str = Field(..., description="Original request identifier")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when response was generated")
    success: bool = Field(default=True, description="Whether comparison succeeded")
    message: Optional[str] = Field(None, description="Status or error message")
    comparison_matrix: Optional[VarietyComparisonMatrix] = Field(
        None,
        description="Structured matrix of comparison metrics"
    )
    detailed_results: List[VarietyComparisonDetail] = Field(
        default_factory=list,
        description="Detailed comparison results for each variety"
    )
    trade_offs: List[VarietyTradeOff] = Field(default_factory=list, description="Identified trade-offs")
    summary: Optional[VarietyComparisonSummary] = Field(None, description="Summary of comparison insights")
    comparisons: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Legacy comparison entries for backward compatibility"
    )
    comparison_summary: Optional[Dict[str, Any]] = Field(
        None,
        description="Legacy summary data for backward compatibility"
    )
    context_used: Dict[str, Any] = Field(default_factory=dict, description="Context information applied in analysis")
    data_sources: List[str] = Field(default_factory=list, description="Data sources referenced in analysis")

    class Config:
        json_encoders = {
            datetime: lambda value: value.isoformat(),
            date: lambda value: value.isoformat()
        }


class VarietyRecommendationResponse(BaseModel):
    """Response containing variety recommendations."""
    
    request_id: str = Field(..., description="Request identifier")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    
    # Recommendations
    recommended_varieties: List[VarietyRecommendation] = Field(..., description="Recommended varieties")
    alternative_varieties: List[VarietyRecommendation] = Field(default_factory=list, description="Alternative options")
    
    # Analysis and guidance
    selection_criteria_met: Dict[str, bool] = Field(default_factory=dict, description="Criteria satisfaction")
    regional_considerations: List[str] = Field(default_factory=list, description="Regional adaptation notes")
    timing_recommendations: List[str] = Field(default_factory=list, description="Planting and management timing")
    
    # Comparison tools
    variety_comparison: Optional[VarietyComparisonMatrix] = Field(None, description="Variety comparison matrix")
    
    # Additional guidance
    management_calendar: Optional[Dict[str, List[str]]] = Field(None, description="Management calendar by month")
    resource_requirements: Dict[str, Any] = Field(default_factory=dict, description="Resource requirement summary")
    success_factors: List[str] = Field(default_factory=list, description="Key success factors")
    
    # Metadata
    total_varieties_considered: int = Field(..., description="Total varieties evaluated")
    recommendation_confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Overall confidence")
    data_sources: List[str] = Field(default_factory=list, description="Data sources used")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
