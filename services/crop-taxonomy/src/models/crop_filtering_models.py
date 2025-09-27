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

    _RESISTANCE_RANKINGS = {
        "none": 0,
        "susceptible": 0,
        "low": 1,
        "limited": 1,
        "moderate": 2,
        "medium": 2,
        "intermediate": 2,
        "good": 3,
        "high": 3,
        "strong": 3,
        "very high": 4,
        "very strong": 4,
        "excellent": 4,
        "exceptional": 4
    }

    _AFFIRMATIVE_TERMS = (
        "yes",
        "true",
        "available",
        "approved",
        "active",
        "certified",
        "granted",
        "enabled"
    )

    _NEGATIVE_TERMS = (
        "no",
        "false",
        "unavailable",
        "denied",
        "inactive",
        "not certified",
        "not available",
        "disabled"
    )

    @validator('pest_resistance_traits', pre=True, always=True)
    def _validate_pest_resistance_traits(cls, value):
        """Ensure pest resistance traits are stored as a dictionary with string keys."""
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise ValueError('pest_resistance_traits must be a dictionary')
        sanitized = {}
        for key, trait_value in value.items():
            if key is None:
                continue
            key_str = str(key)
            sanitized[key_str] = trait_value
        return sanitized

    @validator('market_class_filters', pre=True, always=True)
    def _validate_market_class_filters(cls, value):
        """Ensure market class filters use string keys."""
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise ValueError('market_class_filters must be a dictionary')
        sanitized = {}
        for key, filter_value in value.items():
            if key is None:
                continue
            key_str = str(key)
            sanitized[key_str] = filter_value
        return sanitized

    @validator('certification_filters', pre=True, always=True)
    def _validate_certification_filters(cls, value):
        """Ensure certification filters use string keys."""
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise ValueError('certification_filters must be a dictionary')
        sanitized = {}
        for key, filter_value in value.items():
            if key is None:
                continue
            key_str = str(key)
            sanitized[key_str] = filter_value
        return sanitized

    @validator('seed_availability_filters', pre=True, always=True)
    def _validate_seed_availability_filters(cls, value):
        """Ensure seed availability filters are stored as a dictionary with canonical keys."""
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise ValueError('seed_availability_filters must be a dictionary')
        sanitized = {}
        for key, seed_value in value.items():
            if key is None:
                continue
            key_str = str(key)
            if key_str in ('regions', 'suppliers'):
                normalized_list = []
                if isinstance(seed_value, (list, tuple, set)):
                    for item in seed_value:
                        if item is None:
                            continue
                        normalized_list.append(str(item))
                elif seed_value is None:
                    normalized_list = []
                else:
                    normalized_list.append(str(seed_value))
                sanitized[key_str] = normalized_list
            else:
                sanitized[key_str] = seed_value
        return sanitized

    @staticmethod
    def _normalize_term(term: Optional[str]) -> str:
        """Normalize terms for comparison without using regular expressions."""
        if term is None:
            return ''
        cleaned_characters = []
        for character in term:
            if character.isalnum():
                cleaned_characters.append(character.lower())
            elif character in (' ', '-', '_', '/'):  # treat separators as spaces
                cleaned_characters.append(' ')
        collapsed = []
        previous_space = False
        for character in cleaned_characters:
            if character == ' ':
                if not previous_space:
                    collapsed.append(character)
                previous_space = True
            else:
                collapsed.append(character)
                previous_space = False
        normalized = ''.join(collapsed).strip()
        return normalized

    @classmethod
    def _terms_match(cls, candidate: str, target: str) -> bool:
        """Case-insensitive comparison that tolerates separators."""
        normalized_candidate = cls._normalize_term(candidate)
        normalized_target = cls._normalize_term(target)
        if not normalized_candidate or not normalized_target:
            return False
        if normalized_candidate == normalized_target:
            return True
        if normalized_candidate.find(normalized_target) != -1 and len(normalized_target) >= 3:
            return True
        if normalized_target.find(normalized_candidate) != -1 and len(normalized_candidate) >= 3:
            return True
        return False

    @classmethod
    def _resistance_rank(cls, level: Any) -> int:
        """Convert various resistance descriptors to ranked numeric values."""
        if level is None:
            return 0
        if isinstance(level, (int, float)):
            if level < 0:
                return 0
            if level > 4:
                return 4
            return int(level)
        normalized_level = cls._normalize_term(str(level))
        if normalized_level in cls._RESISTANCE_RANKINGS:
            return cls._RESISTANCE_RANKINGS[normalized_level]
        return 0

    @classmethod
    def _interpret_affirmative(cls, value: Any) -> Optional[bool]:
        """Interpret diverse values as boolean indicators."""
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            if value == 0:
                return False
            return True
        if isinstance(value, str):
            normalized_value = cls._normalize_term(value)
            for positive_term in cls._AFFIRMATIVE_TERMS:
                if normalized_value == positive_term:
                    return True
            for negative_term in cls._NEGATIVE_TERMS:
                if normalized_value == negative_term:
                    return False
        return None

    @classmethod
    def _matches_in_structure(cls, structure: Any, target: str) -> bool:
        """Search a nested structure for a string that matches the target."""
        if structure is None:
            return False
        if isinstance(structure, str):
            return cls._terms_match(structure, target)
        if isinstance(structure, dict):
            for nested_key, nested_value in structure.items():
                if isinstance(nested_key, str) and cls._terms_match(nested_key, target):
                    interpreted = cls._interpret_affirmative(nested_value)
                    if interpreted is None:
                        if nested_value:
                            return True
                    elif interpreted:
                        return True
                if cls._matches_in_structure(nested_value, target):
                    return True
            return False
        if isinstance(structure, (list, tuple, set)):
            for item in structure:
                if cls._matches_in_structure(item, target):
                    return True
            return False
        interpreted_value = cls._interpret_affirmative(structure)
        if interpreted_value is None:
            return False
        return interpreted_value

    def get_pest_resistance_level(self, pest_name: str) -> Optional[str]:
        """Get the resistance descriptor for a specific pest."""
        normalized_target = self._normalize_term(pest_name)
        if not normalized_target:
            return None
        for trait_name, trait_value in self.pest_resistance_traits.items():
            if not isinstance(trait_name, str):
                continue
            if not self._terms_match(trait_name, normalized_target):
                continue
            if isinstance(trait_value, dict):
                if 'level' in trait_value and trait_value['level'] is not None:
                    return str(trait_value['level'])
                if 'rating' in trait_value and trait_value['rating'] is not None:
                    return str(trait_value['rating'])
            if isinstance(trait_value, (str, int, float)):
                return str(trait_value)
        return None

    def resists_pest_at_least(self, pest_name: str, minimum_level: str) -> bool:
        """Determine if resistance meets or exceeds the requested level."""
        current_level = self.get_pest_resistance_level(pest_name)
        if current_level is None:
            return False
        current_rank = self._resistance_rank(current_level)
        required_rank = self._resistance_rank(minimum_level)
        return current_rank >= required_rank

    def supports_market_class(self, market_class: str) -> bool:
        """Check whether the crop supports a requested market class."""
        normalized_target = self._normalize_term(market_class)
        if not normalized_target:
            return False
        for key, value in self.market_class_filters.items():
            if isinstance(key, str) and self._terms_match(key, normalized_target):
                interpreted = self._interpret_affirmative(value)
                if interpreted is None:
                    return True
                return interpreted
            if self._matches_in_structure(value, normalized_target):
                return True
        return False

    def has_certification(self, certification: str) -> bool:
        """Verify whether the crop aligns with a specific certification."""
        normalized_target = self._normalize_term(certification)
        if not normalized_target:
            return False
        for key, value in self.certification_filters.items():
            if isinstance(key, str) and self._terms_match(key, normalized_target):
                if isinstance(value, dict):
                    status_value = self._interpret_affirmative(value.get('status'))
                    if status_value is None:
                        status_value = self._interpret_affirmative(value.get('value'))
                    if status_value is not None:
                        return status_value
                    return True
                interpreted = self._interpret_affirmative(value)
                if interpreted is not None:
                    return interpreted
                return bool(value)
            if isinstance(value, dict):
                name_value = value.get('name')
                if isinstance(name_value, str) and self._terms_match(name_value, normalized_target):
                    status_value = self._interpret_affirmative(value.get('status'))
                    if status_value is None:
                        status_value = self._interpret_affirmative(value.get('value'))
                    if status_value is not None:
                        return status_value
                    return True
                if self._matches_in_structure(value, normalized_target):
                    return True
            elif isinstance(value, (list, tuple, set)):
                if self._matches_in_structure(value, normalized_target):
                    return True
            elif isinstance(value, str):
                if self._terms_match(value, normalized_target):
                    interpreted = self._interpret_affirmative(value)
                    if interpreted is not None:
                        return interpreted
                    return True
        return False

    def is_seed_available(self, region: Optional[str] = None, supplier: Optional[str] = None) -> bool:
        """Determine seed availability with optional regional and supplier filters."""
        availability = self.seed_availability_filters or {}
        if not availability:
            return False
        status_value = self._interpret_affirmative(availability.get('status'))
        if status_value is False:
            return False
        if region:
            region_match = False
            if self._matches_in_structure(availability.get('regions'), region):
                region_match = True
            else:
                regional_status = availability.get('regional_status')
                if isinstance(regional_status, dict):
                    for region_name, region_value in regional_status.items():
                        if not isinstance(region_name, str):
                            continue
                        if not self._terms_match(region_name, region):
                            continue
                        interpreted_region = self._interpret_affirmative(region_value)
                        if interpreted_region is None or interpreted_region:
                            region_match = True
                            break
            if not region_match:
                return False
        if supplier:
            supplier_match = False
            if self._matches_in_structure(availability.get('suppliers'), supplier):
                supplier_match = True
            else:
                supplier_status = availability.get('supplier_status')
                if isinstance(supplier_status, dict):
                    for supplier_name, supplier_value in supplier_status.items():
                        if not isinstance(supplier_name, str):
                            continue
                        if not self._terms_match(supplier_name, supplier):
                            continue
                        interpreted_supplier = self._interpret_affirmative(supplier_value)
                        if interpreted_supplier is None or interpreted_supplier:
                            supplier_match = True
                            break
            if not supplier_match:
                return False
        if status_value is None:
            return True
        return status_value


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
    score_breakdown: Dict[str, float] = Field(
        default_factory=dict,
        description="Per-filter score contributions for visualization"
    )
    ranking_details: Optional[ResultRankingDetails] = Field(
        None,
        description="Detailed breakdown of ranking metrics"
    )
    
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


class FilterScoreBreakdown(BaseModel):
    """Score contribution details for an individual filter dimension."""

    name: str = Field(..., description="Filter dimension name")
    weight: float = Field(..., ge=0.0, description="Weight applied during scoring")
    score: float = Field(..., ge=0.0, le=1.0, description="Normalized score for the filter")
    matched: bool = Field(..., description="Indicates the filter fully matched")
    partial: bool = Field(..., description="Indicates the filter partially matched")
    notes: List[str] = Field(default_factory=list, description="Relevant notes for the filter evaluation")


class ResultRankingDetails(BaseModel):
    """Detailed ranking insight for an individual search result."""

    active_filters: int = Field(0, ge=0, description="Number of filters applied to this result")
    matched_filters: int = Field(0, ge=0, description="Number of filters fully matched")
    partial_filters: int = Field(0, ge=0, description="Number of filters partially matched")
    missing_filters: int = Field(0, ge=0, description="Number of filters not satisfied")
    coverage: float = Field(0.0, ge=0.0, le=1.0, description="Ratio of matched filters to active filters")
    filter_scores: List[FilterScoreBreakdown] = Field(
        default_factory=list,
        description="Score contributions for each filter dimension"
    )


class ScoreBucket(BaseModel):
    """Bucket representing a range of scores for visualization."""

    label: str = Field(..., description="Bucket label for display")
    count: int = Field(..., ge=0, description="Number of results within the bucket")
    minimum: float = Field(..., ge=0.0, le=1.0, description="Minimum score for the bucket")
    maximum: float = Field(..., ge=0.0, le=1.0, description="Maximum score for the bucket")


class FilterContributionAggregate(BaseModel):
    """Aggregate statistics for a filter dimension across all results."""

    name: str = Field(..., description="Filter dimension name")
    average_score: float = Field(..., ge=0.0, le=1.0, description="Average normalized score")
    matched_results: int = Field(..., ge=0, description="Results with full matches")
    partial_results: int = Field(..., ge=0, description="Results with partial matches")
    weight: float = Field(..., ge=0.0, description="Weight applied to the filter during scoring")


class SearchRankingOverview(BaseModel):
    """High-level ranking indicators for the search execution."""

    best_score: float = Field(0.0, ge=0.0, le=1.0, description="Highest relevance score returned")
    worst_score: float = Field(0.0, ge=0.0, le=1.0, description="Lowest relevance score returned")
    median_score: float = Field(0.0, ge=0.0, le=1.0, description="Median relevance score")
    average_coverage: float = Field(0.0, ge=0.0, le=1.0, description="Average matched filter coverage")


class SearchVisualizationSummary(BaseModel):
    """Visualization-friendly summary of search ranking data."""

    score_distribution: List[ScoreBucket] = Field(
        default_factory=list,
        description="Distribution of scores for charting"
    )
    filter_contributions: List[FilterContributionAggregate] = Field(
        default_factory=list,
        description="Average filter performance for stacked visualizations"
    )
    match_summary: Dict[str, int] = Field(
        default_factory=dict,
        description="Counts of perfect, partial, and missing matches"
    )
    highlights: List[str] = Field(
        default_factory=list,
        description="Narrative highlights for presenting the ranking"
    )




# ============================================================================
# FILTER COMBINATION AND SUGGESTION MODELS
# ============================================================================

class FilterDirective(BaseModel):
    """Directive describing a single filter adjustment."""

    category: str = Field(..., description="Target filter category (climate, soil, etc.)")
    attribute: str = Field(..., description="Attribute within the filter category")
    value: Any = Field(..., description="Desired value for the attribute")
    priority: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Priority weight for applying the directive"
    )
    rationale: Optional[str] = Field(None, description="Reason for applying the directive")


class FilterCombinationRequest(BaseModel):
    """Request payload for dynamically combining filter directives."""

    request_id: str = Field(..., description="Unique request identifier")
    base_criteria: TaxonomyFilterCriteria = Field(
        default_factory=TaxonomyFilterCriteria,
        description="Existing filter criteria to extend"
    )
    directives: List[FilterDirective] = Field(
        default_factory=list,
        description="Directives to apply to the base criteria"
    )
    preset_keys: List[str] = Field(
        default_factory=list,
        description="Filter preset identifiers to apply"
    )
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Contextual information such as climate, soil, or goals"
    )
    include_suggestions: bool = Field(
        default=True,
        description="Include follow-up filter suggestions in the response"
    )


class FilterPresetSummary(BaseModel):
    """Summary details about a recommended filter preset."""

    key: str = Field(..., description="Preset identifier")
    name: str = Field(..., description="Human-readable preset name")
    description: str = Field(..., description="Description of the preset")
    rationale: List[str] = Field(
        default_factory=list,
        description="Reasons why the preset is relevant"
    )


class FilterCombinationResponse(BaseModel):
    """Response payload with combined filter criteria and guidance."""

    request_id: str = Field(..., description="Original request identifier")
    combined_criteria: TaxonomyFilterCriteria = Field(
        ..., description="Resulting combined filter criteria"
    )
    applied_presets: List[str] = Field(
        default_factory=list,
        description="Preset keys applied during combination"
    )
    dependency_notes: List[str] = Field(
        default_factory=list,
        description="Notes about dependency adjustments that were applied"
    )
    conflicts: List[str] = Field(
        default_factory=list,
        description="Detected conflicts between requested filters"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Additional warnings or cautions"
    )
    suggested_directives: List[FilterDirective] = Field(
        default_factory=list,
        description="Follow-up directives suggested by the engine"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the combination process"
    )


class FilterSuggestionRequest(BaseModel):
    """Request for intelligent filter suggestions."""

    request_id: str = Field(..., description="Unique request identifier")
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Context such as farm profile, crops, or goals"
    )
    climate_zone: Optional[str] = Field(
        None,
        description="Primary climate zone (e.g., USDA hardiness zone)"
    )
    location_coordinates: Optional[Dict[str, float]] = Field(
        None,
        description="Latitude and longitude for location-aware suggestions"
    )
    existing_criteria: Optional[TaxonomyFilterCriteria] = Field(
        None,
        description="Current criteria to consider when generating suggestions"
    )
    max_suggestions: int = Field(
        default=5,
        ge=0,
        le=20,
        description="Maximum number of suggestions to return"
    )
    include_presets: bool = Field(
        default=True,
        description="Whether to include preset recommendations"
    )
    focus_areas: List[str] = Field(
        default_factory=list,
        description="Optional focus areas such as sustainability or profitability"
    )


class FilterSuggestion(BaseModel):
    """Individual intelligent filter suggestion."""

    key: str = Field(..., description="Suggestion identifier")
    title: str = Field(..., description="Short title for the suggestion")
    description: str = Field(..., description="Detailed suggestion description")
    directives: List[FilterDirective] = Field(
        default_factory=list,
        description="Filter directives represented by this suggestion"
    )
    rationale: List[str] = Field(
        default_factory=list,
        description="Reasons supporting the suggestion"
    )
    score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Relevance score for ranking"
    )
    category: Optional[str] = Field(
        None,
        description="Suggestion category such as climate, soil, or market"
    )


class FilterSuggestionResponse(BaseModel):
    """Response containing intelligent filter suggestions."""

    request_id: str = Field(..., description="Original request identifier")
    suggestions: List[FilterSuggestion] = Field(
        default_factory=list,
        description="List of suggested filters"
    )
    preset_summaries: List[FilterPresetSummary] = Field(
        default_factory=list,
        description="Relevant preset summaries"
    )
    context_summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="Summary of interpreted context information"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about suggestion generation"
    )


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
    ranking_overview: Optional[SearchRankingOverview] = Field(
        None,
        description="High-level ranking metrics for the result set"
    )
    visualization_summary: SearchVisualizationSummary = Field(
        default_factory=SearchVisualizationSummary,
        description="Visualization-friendly summary of the ranking data"
    )
    
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


# Resolve forward references now that dependent models are loaded
try:  # pragma: no cover - defensive guard during import cycles
    ComprehensiveCropData.model_rebuild(
        _types_namespace={'CropFilteringAttributes': CropFilteringAttributes}
    )
except AttributeError:
    ComprehensiveCropData.update_forward_refs(CropFilteringAttributes=CropFilteringAttributes)
except Exception:
    pass
