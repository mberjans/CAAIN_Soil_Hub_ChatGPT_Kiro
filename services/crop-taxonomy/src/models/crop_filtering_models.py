"""
Crop Filtering and Search Models

Pydantic models for advanced crop search, filtering, and discovery functionality.
Provides comprehensive search capabilities across taxonomic, agricultural, and environmental criteria.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import date, datetime
from enum import Enum
from uuid import UUID

from .crop_taxonomy_models import (
    CropCategory, PrimaryUse, GrowthHabit, PlantType, PhotosynthesisType,
    FrostTolerance, DroughtTolerance, WaterRequirement, ToleranceLevel,
    ComprehensiveCropData
)


# ============================================================================
# FILTERING AND SEARCH ENUMERATIONS
# ============================================================================

class ManagementComplexity(str, Enum):
    """Management complexity levels."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class InputRequirements(str, Enum):
    """Input requirement levels."""
    MINIMAL = "minimal"
    MODERATE = "moderate"
    INTENSIVE = "intensive"


class LaborRequirements(str, Enum):
    """Labor requirement levels."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class CarbonSequestrationPotential(str, Enum):
    """Carbon sequestration potential levels."""
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class BiodiversitySupport(str, Enum):
    """Biodiversity support levels."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class PollinatorValue(str, Enum):
    """Pollinator support value levels."""
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class WaterUseEfficiency(str, Enum):
    """Water use efficiency levels."""
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"


class MarketStability(str, Enum):
    """Market stability levels."""
    VOLATILE = "volatile"
    MODERATE = "moderate"
    STABLE = "stable"


class SearchOperator(str, Enum):
    """Search operators for combining criteria."""
    AND = "and"
    OR = "or"
    NOT = "not"


class SortOrder(str, Enum):
    """Sort order options."""
    ASC = "asc"
    DESC = "desc"


class SortField(str, Enum):
    """Available fields for sorting search results."""
    NAME = "name"
    CATEGORY = "category"
    SCIENTIFIC_NAME = "scientific_name"
    SUITABILITY_SCORE = "suitability_score"
    POPULARITY = "popularity"
    UPDATED_DATE = "updated_date"
    ALPHABETICAL = "alphabetical"


# ============================================================================
# FILTERING ATTRIBUTES MODEL
# ============================================================================

class CropFilteringAttributes(BaseModel):
    """Comprehensive filtering attributes for advanced crop search."""
    
    filter_id: Optional[UUID] = Field(None, description="Unique filter attributes identifier")
    crop_id: UUID = Field(..., description="Associated crop identifier")
    
    # Seasonality attributes
    planting_season: List[str] = Field(default_factory=lambda: ["spring"], description="Planting seasons")
    growing_season: List[str] = Field(default_factory=lambda: ["summer"], description="Growing seasons")
    harvest_season: List[str] = Field(default_factory=lambda: ["fall"], description="Harvest seasons")
    
    # Agricultural system compatibility
    farming_systems: List[str] = Field(default_factory=lambda: ["conventional"], description="Compatible farming systems")
    rotation_compatibility: List[str] = Field(default_factory=list, description="Rotation-compatible crops")
    intercropping_compatible: bool = Field(default=False, description="Suitable for intercropping")
    cover_crop_compatible: bool = Field(default=True, description="Works with cover crops")
    
    # Management characteristics
    management_complexity: Optional[ManagementComplexity] = Field(None, description="Management complexity level")
    input_requirements: Optional[InputRequirements] = Field(None, description="Input requirement level")
    labor_requirements: Optional[LaborRequirements] = Field(None, description="Labor requirement level")
    
    # Technology compatibility
    precision_ag_compatible: bool = Field(default=True, description="Precision agriculture compatible")
    gps_guidance_recommended: bool = Field(default=False, description="GPS guidance recommended")
    sensor_monitoring_beneficial: bool = Field(default=False, description="Benefits from sensor monitoring")
    
    # Sustainability attributes
    carbon_sequestration_potential: Optional[CarbonSequestrationPotential] = Field(None, description="Carbon sequestration potential")
    biodiversity_support: Optional[BiodiversitySupport] = Field(None, description="Biodiversity support level")
    pollinator_value: Optional[PollinatorValue] = Field(None, description="Pollinator support value")
    water_use_efficiency: Optional[WaterUseEfficiency] = Field(None, description="Water use efficiency")
    
    # Market and economic attributes
    market_stability: Optional[MarketStability] = Field(None, description="Market stability level")
    price_premium_potential: bool = Field(default=False, description="Potential for price premiums")
    value_added_opportunities: List[str] = Field(default_factory=list, description="Value-added processing opportunities")
    
    # Advanced filtering attributes
    pest_resistance_traits: Dict[str, Any] = Field(
        default_factory=dict,
        description="Pest resistance traits available for filtering"
    )
    market_class_filters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Market class filters supporting specialty segmentation"
    )
    certification_filters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Certification-based filters such as organic or non-GMO"
    )
    seed_availability_filters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Seed availability filters across suppliers and regions"
    )
    
    # Metadata
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


# ============================================================================
# SEARCH CRITERIA AND FILTERS
# ============================================================================

class GeographicFilter(BaseModel):
    """Geographic filtering criteria."""
    
    # Location-based filters
    latitude_range: Optional[Dict[str, float]] = Field(None, description="Latitude range (min, max)")
    longitude_range: Optional[Dict[str, float]] = Field(None, description="Longitude range (min, max)")
    states: Optional[List[str]] = Field(None, description="Specific states/provinces")
    countries: Optional[List[str]] = Field(None, description="Specific countries")
    
    # Climate zones
    hardiness_zones: Optional[List[str]] = Field(None, description="USDA hardiness zones")
    koppen_zones: Optional[List[str]] = Field(None, description="Köppen climate zones")
    
    # Elevation constraints
    elevation_min_feet: Optional[int] = Field(None, description="Minimum elevation (feet)")
    elevation_max_feet: Optional[int] = Field(None, description="Maximum elevation (feet)")


class ClimateFilter(BaseModel):
    """Climate-based filtering criteria."""
    
    # Temperature filters
    temperature_range_f: Optional[Dict[str, float]] = Field(None, description="Temperature range (min, max)")
    frost_tolerance_required: Optional[FrostTolerance] = Field(None, description="Minimum frost tolerance required")
    heat_tolerance_required: Optional[str] = Field(None, description="Minimum heat tolerance required")
    
    # Precipitation filters
    annual_precipitation_range: Optional[Dict[str, float]] = Field(None, description="Annual precipitation range (inches)")
    drought_tolerance_required: Optional[DroughtTolerance] = Field(None, description="Minimum drought tolerance")
    
    # Seasonal constraints
    growing_season_length_days: Optional[Dict[str, int]] = Field(None, description="Growing season length range")
    photoperiod_requirements: Optional[List[str]] = Field(None, description="Photoperiod sensitivities")


class SoilFilter(BaseModel):
    """Soil-based filtering criteria."""
    
    # pH constraints
    ph_range: Optional[Dict[str, float]] = Field(None, description="Soil pH range")
    ph_tolerance_strict: bool = Field(default=False, description="Apply strict pH tolerance")
    
    # Soil physical properties
    texture_classes: Optional[List[str]] = Field(None, description="Acceptable soil textures")
    drainage_classes: Optional[List[str]] = Field(None, description="Acceptable drainage classes")
    
    # Chemical tolerances
    salinity_tolerance_required: Optional[ToleranceLevel] = Field(None, description="Minimum salinity tolerance")
    acidity_tolerance_required: Optional[ToleranceLevel] = Field(None, description="Minimum acidity tolerance")
    
    # Nutrient considerations
    low_fertility_tolerance: Optional[bool] = Field(None, description="Must tolerate low fertility")
    high_fertility_requirement: Optional[bool] = Field(None, description="Requires high fertility")


class AgriculturalFilter(BaseModel):
    """Agricultural practice-based filtering criteria."""
    
    # Crop categories and uses
    categories: Optional[List[CropCategory]] = Field(None, description="Acceptable crop categories")
    primary_uses: Optional[List[PrimaryUse]] = Field(None, description="Acceptable primary uses")
    exclude_categories: Optional[List[CropCategory]] = Field(None, description="Categories to exclude")
    
    # Growth characteristics
    growth_habits: Optional[List[GrowthHabit]] = Field(None, description="Acceptable growth habits")
    plant_types: Optional[List[PlantType]] = Field(None, description="Acceptable plant types")
    photosynthesis_types: Optional[List[PhotosynthesisType]] = Field(None, description="Photosynthesis pathway preferences")
    
    # Special characteristics
    nitrogen_fixing_required: Optional[bool] = Field(None, description="Must be nitrogen fixing")
    cover_crop_only: Optional[bool] = Field(None, description="Cover crops only")
    companion_crop_suitable: Optional[bool] = Field(None, description="Must be suitable as companion crop")
    
    # Size constraints
    max_height_inches: Optional[int] = Field(None, description="Maximum mature height")
    min_height_inches: Optional[int] = Field(None, description="Minimum mature height")


class ManagementFilter(BaseModel):
    """Management and operational filtering criteria."""
    
    # Complexity and input requirements
    max_management_complexity: Optional[ManagementComplexity] = Field(None, description="Maximum management complexity")
    max_input_requirements: Optional[InputRequirements] = Field(None, description="Maximum input requirements")
    max_labor_requirements: Optional[LaborRequirements] = Field(None, description="Maximum labor requirements")
    
    # Technology requirements
    precision_ag_compatible_required: Optional[bool] = Field(None, description="Must be precision ag compatible")
    low_tech_suitable: Optional[bool] = Field(None, description="Must be suitable for low-tech operations")
    
    # Farming system compatibility
    farming_systems: Optional[List[str]] = Field(None, description="Compatible farming systems")
    organic_suitable: Optional[bool] = Field(None, description="Must be suitable for organic production")


class SustainabilityFilter(BaseModel):
    """Sustainability-focused filtering criteria."""
    
    # Environmental benefits
    min_carbon_sequestration: Optional[CarbonSequestrationPotential] = Field(None, description="Minimum carbon sequestration")
    min_biodiversity_support: Optional[BiodiversitySupport] = Field(None, description="Minimum biodiversity support")
    min_pollinator_value: Optional[PollinatorValue] = Field(None, description="Minimum pollinator value")
    
    # Resource efficiency
    min_water_efficiency: Optional[WaterUseEfficiency] = Field(None, description="Minimum water use efficiency")
    drought_resilient_only: Optional[bool] = Field(None, description="Drought resilient crops only")
    
    # Conservation practices
    erosion_control_capable: Optional[bool] = Field(None, description="Must provide erosion control")
    soil_building_capable: Optional[bool] = Field(None, description="Must build soil health")


class EconomicFilter(BaseModel):
    """Economic and market-based filtering criteria."""
    
    # Market characteristics
    market_stability_required: Optional[MarketStability] = Field(None, description="Required market stability")
    premium_market_potential: Optional[bool] = Field(None, description="Must have premium market potential")
    
    # Value-added opportunities
    processing_opportunities: Optional[List[str]] = Field(None, description="Required value-added opportunities")
    
    # Cost considerations
    low_establishment_cost: Optional[bool] = Field(None, description="Must have low establishment cost")
    high_roi_potential: Optional[bool] = Field(None, description="Must have high ROI potential")


# ============================================================================
# COMPREHENSIVE SEARCH REQUEST
# ============================================================================

class TaxonomyFilterCriteria(BaseModel):
    """Comprehensive filtering criteria for crop taxonomy search."""
    
    # Basic text search
    text_search: Optional[str] = Field(None, description="General text search across names and descriptions")
    scientific_name_search: Optional[str] = Field(None, description="Scientific name search")
    common_name_search: Optional[str] = Field(None, description="Common name search")
    
    # Taxonomic filters
    families: Optional[List[str]] = Field(None, description="Taxonomic families to include")
    genera: Optional[List[str]] = Field(None, description="Taxonomic genera to include")
    
    # Location and environment
    geographic_filter: Optional[GeographicFilter] = Field(None, description="Geographic constraints")
    climate_filter: Optional[ClimateFilter] = Field(None, description="Climate requirements")
    soil_filter: Optional[SoilFilter] = Field(None, description="Soil requirements")
    
    # Agricultural characteristics
    agricultural_filter: Optional[AgriculturalFilter] = Field(None, description="Agricultural criteria")
    management_filter: Optional[ManagementFilter] = Field(None, description="Management criteria")
    
    # Sustainability and economics
    sustainability_filter: Optional[SustainabilityFilter] = Field(None, description="Sustainability criteria")
    economic_filter: Optional[EconomicFilter] = Field(None, description="Economic criteria")
    
    # Advanced options
    search_operator: SearchOperator = Field(default=SearchOperator.AND, description="Operator for combining criteria")
    include_experimental: bool = Field(default=False, description="Include experimental/research crops")
    include_deprecated: bool = Field(default=False, description="Include deprecated crops")


class CropSearchRequest(BaseModel):
    """Request for comprehensive crop search."""
    
    request_id: str = Field(..., description="Unique request identifier")
    
    # Search criteria
    filter_criteria: TaxonomyFilterCriteria = Field(..., description="Search and filter criteria")
    
    # Result options
    max_results: int = Field(default=50, ge=1, le=500, description="Maximum results to return")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")
    
    # Sorting and ranking
    sort_by: SortField = Field(default=SortField.SUITABILITY_SCORE, description="Field to sort by")
    sort_order: SortOrder = Field(default=SortOrder.DESC, description="Sort order")
    
    # Result detail level
    include_full_taxonomy: bool = Field(default=True, description="Include full taxonomic details")
    include_nutritional_data: bool = Field(default=False, description="Include nutritional profiles")
    include_regional_data: bool = Field(default=False, description="Include regional adaptation data")
    
    # Performance options
    use_fuzzy_matching: bool = Field(default=True, description="Use fuzzy text matching")
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Similarity threshold for fuzzy matching")
    
    @validator('max_results')
    def validate_max_results(cls, v):
        """Validate reasonable result limits."""
        if v > 500:
            raise ValueError("Maximum results limited to 500 per request")
        return v


# ============================================================================
# SEARCH RESULTS AND RESPONSES
# ============================================================================

class CropSearchResult(BaseModel):
    """Individual crop search result with relevance scoring."""
    
    # Basic crop information
    crop: ComprehensiveCropData = Field(..., description="Crop data")
    
    # Relevance and matching
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Overall relevance score")
    suitability_score: float = Field(..., ge=0.0, le=1.0, description="Suitability for criteria")
    
    # Matching details
    matching_criteria: List[str] = Field(default_factory=list, description="Criteria that matched")
    partial_matches: List[str] = Field(default_factory=list, description="Criteria with partial matches")
    missing_criteria: List[str] = Field(default_factory=list, description="Criteria not met")
    
    # Search-specific data
    search_highlights: Dict[str, List[str]] = Field(default_factory=dict, description="Search term highlights")
    similarity_factors: Dict[str, float] = Field(default_factory=dict, description="Similarity scores by factor")
    
    # Recommendations
    recommendation_notes: List[str] = Field(default_factory=list, description="Specific recommendation notes")
    potential_concerns: List[str] = Field(default_factory=list, description="Potential concerns or limitations")


class SearchFacets(BaseModel):
    """Search facets for refining results."""
    
    categories: Dict[str, int] = Field(default_factory=dict, description="Categories with counts")
    families: Dict[str, int] = Field(default_factory=dict, description="Taxonomic families with counts")
    growth_habits: Dict[str, int] = Field(default_factory=dict, description="Growth habits with counts")
    hardiness_zones: Dict[str, int] = Field(default_factory=dict, description="Hardiness zones with counts")
    primary_uses: Dict[str, int] = Field(default_factory=dict, description="Primary uses with counts")
    
    # Dynamic facets based on search criteria
    dynamic_facets: Dict[str, Dict[str, int]] = Field(default_factory=dict, description="Dynamic facets based on results")


class SearchStatistics(BaseModel):
    """Search execution statistics."""
    
    total_results: int = Field(..., description="Total matching results")
    search_time_ms: float = Field(..., description="Search execution time (milliseconds)")
    filtered_results: int = Field(..., description="Results after filtering")
    
    # Search optimization metrics
    index_hits: int = Field(default=0, description="Database index hits")
    full_scan_required: bool = Field(default=False, description="Required full table scan")
    cache_hit: bool = Field(default=False, description="Results served from cache")
    
    # Quality metrics
    average_relevance_score: float = Field(default=0.0, description="Average relevance score")
    result_quality_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall result quality")


class CropSearchResponse(BaseModel):
    """Response containing crop search results."""
    
    request_id: str = Field(..., description="Original request identifier")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Response generation time")
    
    # Results
    results: List[CropSearchResult] = Field(..., description="Search results")
    total_count: int = Field(..., description="Total results available")
    returned_count: int = Field(..., description="Number of results returned")
    
    # Search assistance
    facets: SearchFacets = Field(..., description="Search facets for refinement")
    suggested_refinements: List[str] = Field(default_factory=list, description="Suggested search refinements")
    alternative_searches: List[str] = Field(default_factory=list, description="Alternative search suggestions")
    
    # Metadata
    statistics: SearchStatistics = Field(..., description="Search execution statistics")
    applied_filters: Dict[str, Any] = Field(default_factory=dict, description="Summary of applied filters")
    
    # Pagination
    has_more_results: bool = Field(..., description="More results available")
    next_offset: Optional[int] = Field(None, description="Offset for next page")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }


# ============================================================================
# SPECIALIZED SEARCH MODELS
# ============================================================================

class CropRecommendationContext(BaseModel):
    """Context for crop recommendations within search."""
    
    # Farm context
    farm_location: Optional[Dict[str, Any]] = Field(None, description="Farm location details")
    soil_conditions: Optional[Dict[str, Any]] = Field(None, description="Current soil conditions")
    climate_data: Optional[Dict[str, Any]] = Field(None, description="Local climate information")
    
    # Farming context
    current_crops: Optional[List[str]] = Field(None, description="Currently grown crops")
    farming_system: Optional[str] = Field(None, description="Farming system type")
    available_equipment: Optional[List[str]] = Field(None, description="Available equipment")
    
    # Goals and constraints
    primary_goals: Optional[List[str]] = Field(None, description="Primary farming goals")
    budget_constraints: Optional[Dict[str, float]] = Field(None, description="Budget limitations")
    labor_constraints: Optional[Dict[str, Any]] = Field(None, description="Labor limitations")
    
    # Timeline
    planting_timeline: Optional[Dict[str, date]] = Field(None, description="Desired planting timeline")
    harvest_timeline: Optional[Dict[str, date]] = Field(None, description="Target harvest dates")


class ContextualCropSearchRequest(BaseModel):
    """Search request with farming context for personalized recommendations."""
    
    # Base search request
    base_search: CropSearchRequest = Field(..., description="Base search criteria")
    
    # Context for recommendations
    recommendation_context: Optional[CropRecommendationContext] = Field(None, description="Farming context")
    
    # Recommendation preferences
    prioritize_suitability: bool = Field(default=True, description="Prioritize local suitability")
    include_risk_assessment: bool = Field(default=True, description="Include risk analysis")
    provide_alternatives: bool = Field(default=True, description="Provide alternative recommendations")
    
    # Learning and personalization
    farmer_experience_level: Optional[str] = Field(None, description="Farmer experience level")
    previous_successes: Optional[List[str]] = Field(None, description="Previously successful crops")
    previous_challenges: Optional[List[str]] = Field(None, description="Previously challenging crops")


class SmartCropRecommendation(BaseModel):
    """Smart recommendation with context-aware scoring."""
    
    # Base search result
    search_result: CropSearchResult = Field(..., description="Base search result")
    
    # Context-aware scoring
    context_suitability_score: float = Field(..., ge=0.0, le=1.0, description="Context-specific suitability")
    risk_assessment_score: float = Field(..., ge=0.0, le=1.0, description="Risk assessment score")
    success_probability: float = Field(..., ge=0.0, le=1.0, description="Predicted success probability")
    
    # Personalized recommendations
    implementation_difficulty: str = Field(..., description="Implementation difficulty level")
    resource_requirements: Dict[str, str] = Field(..., description="Resource requirement summary")
    timeline_fit: Dict[str, Any] = Field(..., description="Timeline compatibility analysis")
    
    # Risk factors and mitigations
    identified_risks: List[str] = Field(default_factory=list, description="Identified risk factors")
    risk_mitigation_strategies: List[str] = Field(default_factory=list, description="Risk mitigation approaches")
    
    # Alternative options
    similar_alternatives: List[str] = Field(default_factory=list, description="Similar crop alternatives")
    backup_options: List[str] = Field(default_factory=list, description="Backup crop options")


# Filter Suggestion Models
class FilterSuggestionRequest(BaseModel):
    """Request for intelligent filter suggestions based on context."""
    
    request_id: str = Field(..., description="Unique request identifier")
    
    # Context for suggestions
    context: Dict[str, Any] = Field(default_factory=dict, description="Contextual information for suggestions")
    climate_zone: Optional[str] = Field(None, description="Primary climate zone (e.g., 5b)")
    location_coordinates: Optional[Dict[str, float]] = Field(None, description="GPS coordinates (lat, lng)")
    focus_areas: List[str] = Field(default_factory=list, description="Focus areas such as organic, drought, profit")
    
    # Suggestion preferences
    max_suggestions: int = Field(default=5, ge=0, le=20, description="Maximum number of suggestions to return")
    include_presets: bool = Field(default=True, description="Include preset recommendations")
    suggestion_categories: List[str] = Field(default_factory=list, description="Specific suggestion categories to include")
    
    # AI enhancement options
    use_ml_enhancement: bool = Field(default=True, description="Use machine learning for enhanced suggestions")
    user_feedback_weight: float = Field(default=0.3, ge=0.0, le=1.0, description="Weight of user feedback in suggestions")
    seasonal_adjustment: bool = Field(default=True, description="Adjust suggestions based on seasonal factors")
    
    @validator('focus_areas')
    def validate_focus_areas(cls, v: List[str]) -> List[str]:
        """Validate focus areas list."""
        if v is None:
            return []
        validated: List[str] = []
        for item in v:
            if item is None:
                continue
            cleaned = str(item).strip().lower()
            if cleaned:
                validated.append(cleaned)
        return validated


class FilterSuggestion(BaseModel):
    """Intelligent filter suggestion with AI-powered insights."""
    
    key: str = Field(..., description="Unique identifier for the suggestion")
    title: str = Field(..., description="Display title for the suggestion")
    description: str = Field(..., description="Detailed description of the suggestion")
    
    # Suggestion content
    directives: List[FilterDirective] = Field(default_factory=list, description="Filter directives to apply")
    rationale: List[str] = Field(default_factory=list, description="Rationale for the suggestion")
    
    # AI scoring and categorization
    score: float = Field(..., ge=0.0, le=1.0, description="Confidence/relevance score")
    category: str = Field(..., description="Suggestion category (climate, soil, market, etc.)")
    priority: float = Field(default=0.5, ge=0.0, le=1.0, description="Suggestion priority level")
    
    # Context awareness
    context_relevance: Dict[str, float] = Field(default_factory=dict, description="Relevance to context factors")
    seasonal_appropriateness: Optional[float] = Field(None, ge=0.0, le=1.0, description="Seasonal appropriateness score")
    
    # Learning factors
    user_feedback_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="User feedback aggregation")
    historical_success_rate: Optional[float] = Field(None, ge=0.0, le=1.0, description="Historical success rate")
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    source: str = Field(default="ai_suggestion_engine", description="Source of the suggestion")


class FilterSuggestionResponse(BaseModel):
    """Response containing intelligent filter suggestions."""
    
    request_id: str = Field(..., description="Original request identifier")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Response generation time")
    
    # Suggestions
    suggestions: List[FilterSuggestion] = Field(default_factory=list, description="Filter suggestions")
    preset_summaries: List[FilterPresetSummary] = Field(default_factory=list, description="Relevant preset summaries")
    
    # Context analysis
    context_summary: Dict[str, Any] = Field(default_factory=dict, description="Summary of analyzed context")
    identified_patterns: List[str] = Field(default_factory=list, description="Patterns identified in context")
    
    # AI insights
    ml_confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Machine learning confidence score")
    suggestion_diversity: Optional[float] = Field(None, ge=0.0, le=1.0, description="Diversity of suggestion categories")
    
    # Metadata
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }


# Filter Directive Models
class FilterDirective(BaseModel):
    """Directive for applying specific filter adjustments."""
    
    category: str = Field(..., description="Filter category (climate, soil, management, etc.)")
    attribute: str = Field(..., description="Specific attribute within the category")
    value: Any = Field(..., description="Value to apply to the attribute")
    priority: float = Field(default=0.5, ge=0.0, le=1.0, description="Directive priority level")
    rationale: Optional[str] = Field(None, description="Reasoning behind the directive")


class FilterCombinationRequest(BaseModel):
    """Request for combining filter directives and presets."""
    
    request_id: str = Field(..., description="Unique request identifier")
    
    # Base criteria
    base_criteria: TaxonomyFilterCriteria = Field(..., description="Base filter criteria")
    
    # Combination inputs
    preset_keys: List[str] = Field(default_factory=list, description="Preset keys to apply")
    directives: List[FilterDirective] = Field(default_factory=list, description="Directives to apply")
    
    # Combination options
    search_operator: SearchOperator = Field(default=SearchOperator.AND, description="Operator for combining criteria")
    include_suggestions: bool = Field(default=True, description="Include follow-up suggestions")
    
    # Context
    context: Dict[str, Any] = Field(default_factory=dict, description="Contextual information")
    
    @validator('preset_keys')
    def validate_preset_keys(cls, v: List[str]) -> List[str]:
        """Validate preset keys list."""
        if v is None:
            return []
        validated: List[str] = []
        for item in v:
            if item is None:
                continue
            cleaned = str(item).strip()
            if cleaned:
                validated.append(cleaned)
        return validated

    @validator('directives')
    def validate_directives(cls, v: List[FilterDirective]) -> List[FilterDirective]:
        """Validate directives list."""
        if v is None:
            return []
        validated: List[FilterDirective] = []
        for item in v:
            if item is None:
                continue
            if not item.category or not item.attribute:
                continue
            validated.append(item)
        return validated


class FilterCombinationResponse(BaseModel):
    """Response containing combined filter criteria."""
    
    request_id: str = Field(..., description="Original request identifier")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Response generation time")
    
    # Combined results
    combined_criteria: TaxonomyFilterCriteria = Field(..., description="Combined filter criteria")
    applied_presets: List[str] = Field(default_factory=list, description="Preset keys that were applied")
    
    # Guidance and assistance
    dependency_notes: List[str] = Field(default_factory=list, description="Dependency resolution notes")
    conflicts: List[str] = Field(default_factory=list, description="Detected conflicts")
    warnings: List[str] = Field(default_factory=list, description="Processing warnings")
    suggested_directives: List[FilterDirective] = Field(default_factory=list, description="Follow-up suggestions")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }


# Filter Suggestion Models
class FilterSuggestionRequest(BaseModel):
    """Request for intelligent filter suggestions based on context."""
    
    request_id: str = Field(..., description="Unique request identifier")
    
    # Context for suggestions
    context: Dict[str, Any] = Field(default_factory=dict, description="Contextual information for suggestions")
    climate_zone: Optional[str] = Field(None, description="Primary climate zone (e.g., 5b)")
    location_coordinates: Optional[Dict[str, float]] = Field(None, description="GPS coordinates (lat, lng)")
    focus_areas: List[str] = Field(default_factory=list, description="Focus areas such as organic, drought, profit")
    
    # Suggestion preferences
    max_suggestions: int = Field(default=5, ge=0, le=20, description="Maximum number of suggestions to return")
    include_presets: bool = Field(default=True, description="Include preset recommendations")
    
    # AI enhancement options
    use_ml_enhancement: bool = Field(default=True, description="Use machine learning for enhanced suggestions")
    user_feedback_weight: float = Field(default=0.3, ge=0.0, le=1.0, description="Weight of user feedback in suggestions")
    seasonal_adjustment: bool = Field(default=True, description="Adjust suggestions based on seasonal factors")
    
    @validator('focus_areas')
    def validate_focus_areas(cls, v: List[str]) -> List[str]:
        """Validate focus areas list."""
        if v is None:
            return []
        validated: List[str] = []
        for item in v:
            if item is None:
                continue
            cleaned = str(item).strip().lower()
            if cleaned:
                validated.append(cleaned)
        return validated


class FilterSuggestion(BaseModel):
    """Intelligent filter suggestion with AI-powered insights."""
    
    key: str = Field(..., description="Unique identifier for the suggestion")
    title: str = Field(..., description="Display title for the suggestion")
    description: str = Field(..., description="Detailed description of the suggestion")
    
    # Suggestion content
    directives: List[FilterDirective] = Field(default_factory=list, description="Filter directives to apply")
    rationale: List[str] = Field(default_factory=list, description="Rationale for the suggestion")
    
    # AI scoring and categorization
    score: float = Field(..., ge=0.0, le=1.0, description="Confidence/relevance score")
    category: str = Field(..., description="Suggestion category (climate, soil, market, etc.)")
    priority: float = Field(default=0.5, ge=0.0, le=1.0, description="Suggestion priority level")
    
    # Context awareness
    context_relevance: Dict[str, float] = Field(default_factory=dict, description="Relevance to context factors")
    seasonal_appropriateness: Optional[float] = Field(None, ge=0.0, le=1.0, description="Seasonal appropriateness score")
    
    # Learning factors
    user_feedback_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="User feedback aggregation")
    historical_success_rate: Optional[float] = Field(None, ge=0.0, le=1.0, description="Historical success rate")
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    source: str = Field(default="ai_suggestion_engine", description="Source of the suggestion")


class FilterSuggestionResponse(BaseModel):
    """Response containing intelligent filter suggestions."""
    
    request_id: str = Field(..., description="Original request identifier")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Response generation time")
    
    # Suggestions
    suggestions: List[FilterSuggestion] = Field(default_factory=list, description="Filter suggestions")
    preset_summaries: List[FilterPresetSummary] = Field(default_factory=list, description="Relevant preset summaries")
    
    # Context analysis
    context_summary: Dict[str, Any] = Field(default_factory=dict, description="Summary of analyzed context")
    identified_patterns: List[str] = Field(default_factory=list, description="Patterns identified in context")
    
    # AI insights
    ml_confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Machine learning confidence score")
    suggestion_diversity: Optional[float] = Field(None, ge=0.0, le=1.0, description="Diversity of suggestion categories")
    
    # Metadata
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }


# Filter Preset Models
class FilterPresetSummary(BaseModel):
    """Summary information for a filter preset."""
    
    key: str = Field(..., description="Unique identifier for the preset")
    name: str = Field(..., description="Display name for the preset")
    description: str = Field(..., description="Description of what the preset does")
    rationale: List[str] = Field(default_factory=list, description="Rationale for the preset")


class FilterPreset(BaseModel):
    """Detailed filter preset for saving and sharing."""
    
    preset_id: Optional[UUID] = Field(None, description="Unique identifier for the preset")
    user_id: Optional[UUID] = Field(None, description="User who created the preset")
    name: str = Field(..., description="Display name for the preset")
    description: Optional[str] = Field(None, description="Detailed description of the preset")
    filter_config: TaxonomyFilterCriteria = Field(..., description="The filter configuration")
    is_public: bool = Field(default=False, description="Whether the preset is publicly visible")
    tags: List[str] = Field(default_factory=list, description="Tags for categorizing the preset")
    usage_count: int = Field(default=0, description="Number of times the preset has been used")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")


# Resolve forward references now that dependent models are loaded
try:  # pragma: no cover - defensive guard during import cycles
    ComprehensiveCropData.model_rebuild(
        _types_namespace={'CropFilteringAttributes': CropFilteringAttributes}
    )
except AttributeError:
    ComprehensiveCropData.update_forward_refs(CropFilteringAttributes=CropFilteringAttributes)
except Exception:
    pass
