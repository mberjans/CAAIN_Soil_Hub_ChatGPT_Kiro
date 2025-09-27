"""
Core Crop Taxonomy Models

Pydantic models for botanical classification, agricultural categorization,
and comprehensive crop data following agricultural science standards.
"""

from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, List, Dict, Any, Union
from datetime import date, datetime
from enum import Enum
from uuid import UUID


def _ensure_model_dump_compatibility():
    """Add model_dump helpers when running on Pydantic v1."""
    if hasattr(BaseModel, "model_dump"):
        return

    def _model_dump(self, *args, **kwargs):
        return self.dict(*args, **kwargs)

    def _model_dump_json(self, *args, **kwargs):
        return self.json(*args, **kwargs)

    setattr(BaseModel, "model_dump", _model_dump)
    setattr(BaseModel, "model_dump_json", _model_dump_json)


_ensure_model_dump_compatibility()


# ============================================================================
# ENUMERATIONS AND CONSTANTS
# ============================================================================

class CropCategory(str, Enum):
    """Primary agricultural crop categories."""
    GRAIN = "grain"
    OILSEED = "oilseed" 
    FORAGE = "forage"
    VEGETABLE = "vegetable"
    FRUIT = "fruit"
    SPECIALTY = "specialty"
    LEGUME = "legume"
    CEREAL = "cereal"
    ROOT_CROP = "root_crop"
    LEAFY_GREEN = "leafy_green"
    HERB_SPICE = "herb_spice"
    FIBER = "fiber"
    SUGAR_CROP = "sugar_crop"
    COVER_CROP = "cover_crop"
    ORNAMENTAL = "ornamental"
    MEDICINAL = "medicinal"


class PrimaryUse(str, Enum):
    """Primary agricultural uses."""
    FOOD_HUMAN = "food_human"
    FEED_LIVESTOCK = "feed_livestock"
    INDUSTRIAL = "industrial"
    SOIL_IMPROVEMENT = "soil_improvement"
    ORNAMENTAL = "ornamental"
    MEDICINAL = "medicinal"
    FIBER = "fiber"
    BIOFUEL = "biofuel"
    DUAL_PURPOSE = "dual_purpose"


class GrowthHabit(str, Enum):
    """Plant growth habit classifications."""
    ANNUAL = "annual"
    BIENNIAL = "biennial"
    PERENNIAL = "perennial"
    SEMI_PERENNIAL = "semi_perennial"


class PlantType(str, Enum):
    """Basic plant type classifications."""
    GRASS = "grass"
    HERB = "herb"
    SHRUB = "shrub"
    TREE = "tree"
    VINE = "vine"
    SUCCULENT = "succulent"


class GrowthForm(str, Enum):
    """Plant growth form characteristics."""
    UPRIGHT = "upright"
    SPREADING = "spreading"
    CLIMBING = "climbing"
    TRAILING = "trailing"
    ROSETTE = "rosette"
    BUSHY = "bushy"


class PhotosynthesisType(str, Enum):
    """Photosynthesis pathway types."""
    C3 = "C3"
    C4 = "C4"
    CAM = "CAM"


class RootSystemType(str, Enum):
    """Root system type classifications."""
    FIBROUS = "fibrous"
    TAPROOT = "taproot"
    RHIZOME = "rhizome"
    BULB = "bulb"
    TUBER = "tuber"
    CORM = "corm"


class FrostTolerance(str, Enum):
    """Frost tolerance levels."""
    NONE = "none"
    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"


class HeatTolerance(str, Enum):
    """Heat tolerance levels."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"


class WaterRequirement(str, Enum):
    """Water requirement levels."""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class DroughtTolerance(str, Enum):
    """Drought tolerance levels."""
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    EXTREME = "extreme"


class FloodingTolerance(str, Enum):
    """Flooding tolerance levels."""
    NONE = "none"
    BRIEF = "brief"
    MODERATE = "moderate"
    EXTENDED = "extended"


class PhotoperiodSensitivity(str, Enum):
    """Photoperiod sensitivity types."""
    NONE = "none"
    SHORT_DAY = "short_day"
    LONG_DAY = "long_day"
    DAY_NEUTRAL = "day_neutral"


class DrainageRequirement(str, Enum):
    """Soil drainage requirements."""
    WELL_DRAINED = "well_drained"
    MODERATELY_WELL_DRAINED = "moderately_well_drained"
    SOMEWHAT_POORLY_DRAINED = "somewhat_poorly_drained"
    POORLY_DRAINED = "poorly_drained"
    VERY_POORLY_DRAINED = "very_poorly_drained"
    EXCESSIVE_DRAINED = "excessive_drained"


class ToleranceLevel(str, Enum):
    """General tolerance levels."""
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class NutrientRequirement(str, Enum):
    """Nutrient requirement levels."""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


# ============================================================================
# CORE TAXONOMY MODELS
# ============================================================================

class CropTaxonomicHierarchy(BaseModel):
    """Botanical classification hierarchy following Linnaean taxonomy."""

    taxonomy_id: Optional[UUID] = Field(None, description="Unique taxonomy identifier")
    
    # Botanical hierarchy (following scientific classification)
    kingdom: str = Field(default="Plantae", description="Taxonomic kingdom")
    phylum: str = Field(default="Magnoliophyta", description="Taxonomic phylum")
    class_name: str = Field(..., alias="class", description="Taxonomic class")
    order_name: str = Field(..., description="Taxonomic order")
    family: str = Field(..., description="Taxonomic family")
    genus: str = Field(..., description="Taxonomic genus")
    species: str = Field(..., description="Taxonomic species")
    
    # Optional subspecific classifications
    subspecies: Optional[str] = Field(None, description="Subspecies classification")
    variety: Optional[str] = Field(None, description="Botanical variety")
    cultivar: Optional[str] = Field(None, description="Cultivated variety")
    
    # Common names and synonyms
    common_synonyms: List[str] = Field(default_factory=list, description="Common synonym names")
    
    # Metadata
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    @validator('genus')
    def validate_genus(cls, value):
        """Validate and normalize genus names."""
        if not value or len(value.strip()) < 2:
            raise ValueError("Scientific names must be at least 2 characters")
        cleaned = value.strip()
        return cleaned[0].upper() + cleaned[1:].lower() if len(cleaned) > 1 else cleaned.upper()

    @validator('species')
    def validate_species(cls, value):
        """Validate and normalize species names."""
        if not value or len(value.strip()) < 2:
            raise ValueError("Scientific names must be at least 2 characters")
        return value.strip().lower()
    
    @validator('family', 'order_name')
    def validate_higher_taxonomy(cls, v):
        """Validate higher taxonomy names."""
        if not v or len(v.strip()) < 3:
            raise ValueError("Taxonomic names must be at least 3 characters")
        return v.strip().title()

    @property
    def scientific_name(self) -> str:
        """Generate full scientific name."""
        base_name = f"{self.genus} {self.species}"
        if self.subspecies:
            base_name += f" subsp. {self.subspecies}"
        if self.variety:
            base_name += f" var. {self.variety}"
        return base_name

    @property
    def binomial_name(self) -> str:
        """Generate binomial name (genus + species)."""
        return f"{self.genus} {self.species}"

    class Config:
        allow_population_by_field_name = True
        allow_population_by_alias = True


class CropAgriculturalClassification(BaseModel):
    """Agricultural classification and characteristics for crop categorization."""
    
    classification_id: Optional[UUID] = Field(None, description="Unique classification identifier")
    
    # Primary agricultural categories
    crop_category: CropCategory = Field(..., description="Primary crop category")
    crop_subcategory: Optional[str] = Field(None, description="Specific subcategory")
    
    # Agricultural use classifications  
    primary_use: PrimaryUse = Field(..., description="Primary agricultural use")
    secondary_uses: List[PrimaryUse] = Field(default_factory=list, description="Secondary uses")
    
    # Growth characteristics
    growth_habit: GrowthHabit = Field(..., description="Growth habit classification")
    plant_type: PlantType = Field(..., description="Basic plant type")
    growth_form: Optional[GrowthForm] = Field(None, description="Growth form characteristics")
    
    # Physical characteristics for space planning
    mature_height_min_inches: Optional[int] = Field(None, ge=0, description="Minimum mature height (inches)")
    mature_height_max_inches: Optional[int] = Field(None, ge=0, description="Maximum mature height (inches)")
    mature_width_min_inches: Optional[int] = Field(None, ge=0, description="Minimum mature width (inches)")
    mature_width_max_inches: Optional[int] = Field(None, ge=0, description="Maximum mature width (inches)")
    root_system_type: Optional[RootSystemType] = Field(None, description="Root system type")
    
    # Physiological characteristics
    photosynthesis_type: Optional[PhotosynthesisType] = Field(None, description="Photosynthesis pathway")
    nitrogen_fixing: bool = Field(default=False, description="Nitrogen fixation capability")
    mycorrhizal_associations: bool = Field(default=True, description="Forms mycorrhizal associations")
    
    # Metadata
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    @validator('mature_height_min_inches', 'mature_height_max_inches')
    def validate_height_range(cls, v, values):
        """Validate height ranges are logical."""
        if v is not None and v > 1200:  # 100 feet seems unreasonable for crops
            raise ValueError("Mature height seems unreasonably large")
        return v
    
    @validator('mature_width_min_inches', 'mature_width_max_inches')
    def validate_width_range(cls, v, values):
        """Validate width ranges are logical."""
        if v is not None and v > 1200:  # 100 feet seems unreasonable for crops
            raise ValueError("Mature width seems unreasonably large")
        return v


class CropClimateAdaptations(BaseModel):
    """Climate and environmental adaptation characteristics."""
    
    adaptation_id: Optional[UUID] = Field(None, description="Unique adaptation identifier")
    
    # Temperature requirements and tolerances
    optimal_temp_min_f: Optional[float] = Field(None, description="Optimal minimum temperature (°F)")
    optimal_temp_max_f: Optional[float] = Field(None, description="Optimal maximum temperature (°F)")
    absolute_temp_min_f: Optional[float] = Field(None, description="Absolute minimum temperature (°F)")
    absolute_temp_max_f: Optional[float] = Field(None, description="Absolute maximum temperature (°F)")
    frost_tolerance: Optional[FrostTolerance] = Field(None, description="Frost tolerance level")
    heat_tolerance: Optional[HeatTolerance] = Field(None, description="Heat tolerance level")
    
    # USDA hardiness zones
    hardiness_zone_min: Optional[str] = Field(None, description="Minimum hardiness zone")
    hardiness_zone_max: Optional[str] = Field(None, description="Maximum hardiness zone")
    hardiness_zones: List[str] = Field(default_factory=list, description="Suitable hardiness zones")
    
    # Precipitation and water requirements
    annual_precipitation_min_inches: Optional[float] = Field(None, ge=0, description="Minimum annual precipitation")
    annual_precipitation_max_inches: Optional[float] = Field(None, ge=0, description="Maximum annual precipitation")
    water_requirement: Optional[WaterRequirement] = Field(None, description="Water requirement level")
    drought_tolerance: Optional[DroughtTolerance] = Field(None, description="Drought tolerance level")
    flooding_tolerance: Optional[FloodingTolerance] = Field(None, description="Flooding tolerance level")
    
    # Seasonal adaptations
    photoperiod_sensitivity: Optional[PhotoperiodSensitivity] = Field(None, description="Photoperiod sensitivity")
    vernalization_requirement: bool = Field(default=False, description="Requires vernalization")
    vernalization_days: Optional[int] = Field(None, ge=0, description="Days of vernalization needed")
    
    # Geographic adaptations
    elevation_min_feet: Optional[int] = Field(None, ge=0, description="Minimum elevation (feet)")
    elevation_max_feet: Optional[int] = Field(None, ge=0, description="Maximum elevation (feet)")
    latitude_range_min: Optional[float] = Field(None, ge=-90, le=90, description="Minimum latitude")
    latitude_range_max: Optional[float] = Field(None, ge=-90, le=90, description="Maximum latitude")
    
    # Metadata
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    @validator('optimal_temp_min_f', 'optimal_temp_max_f')
    def validate_temp_ranges(cls, v):
        """Validate temperature values are reasonable."""
        if v is not None:
            if v < -50 or v > 150:  # Reasonable crop temperature range
                raise ValueError("Temperature values should be between -50°F and 150°F")
        return v
    
    @validator('annual_precipitation_min_inches', 'annual_precipitation_max_inches')
    def validate_precipitation(cls, v):
        """Validate precipitation values."""
        if v is not None and v > 200:  # 200 inches is extremely high
            raise ValueError("Annual precipitation seems unreasonably high")
        return v


class CropSoilRequirements(BaseModel):
    """Soil requirements and tolerances for crop growth."""
    
    soil_req_id: Optional[UUID] = Field(None, description="Unique soil requirements identifier")
    
    # pH requirements
    optimal_ph_min: Optional[float] = Field(None, ge=3.0, le=10.0, description="Optimal minimum pH")
    optimal_ph_max: Optional[float] = Field(None, ge=3.0, le=10.0, description="Optimal maximum pH")
    tolerable_ph_min: Optional[float] = Field(None, ge=3.0, le=10.0, description="Tolerable minimum pH")
    tolerable_ph_max: Optional[float] = Field(None, ge=3.0, le=10.0, description="Tolerable maximum pH")
    
    # Soil texture preferences
    preferred_textures: List[str] = Field(
        default_factory=lambda: ["loam", "sandy_loam", "clay_loam"],
        description="Preferred soil textures"
    )
    tolerable_textures: List[str] = Field(default_factory=list, description="Tolerable soil textures")
    
    # Drainage requirements
    drainage_requirement: Optional[DrainageRequirement] = Field(None, description="Primary drainage requirement")
    drainage_tolerance: List[DrainageRequirement] = Field(default_factory=list, description="Acceptable drainage classes")
    
    # Chemical tolerances
    salinity_tolerance: Optional[ToleranceLevel] = Field(None, description="Salinity tolerance level")
    alkalinity_tolerance: Optional[ToleranceLevel] = Field(None, description="Alkalinity tolerance level")
    acidity_tolerance: Optional[ToleranceLevel] = Field(None, description="Acidity tolerance level")
    
    # Nutrient preferences
    nitrogen_requirement: Optional[NutrientRequirement] = Field(None, description="Nitrogen requirement level")
    phosphorus_requirement: Optional[NutrientRequirement] = Field(None, description="Phosphorus requirement level")
    potassium_requirement: Optional[NutrientRequirement] = Field(None, description="Potassium requirement level")
    
    # Soil structure preferences
    compaction_tolerance: Optional[ToleranceLevel] = Field(None, description="Soil compaction tolerance")
    organic_matter_preference: Optional[ToleranceLevel] = Field(None, description="Organic matter preference level")
    
    # Metadata
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    @validator('optimal_ph_min', 'optimal_ph_max', 'tolerable_ph_min', 'tolerable_ph_max')
    def validate_ph_values(cls, v):
        """Validate pH values are in acceptable range."""
        if v is not None:
            if not (3.0 <= v <= 10.0):
                raise ValueError("pH values must be between 3.0 and 10.0")
        return v
    
    def validate_ph_ranges(self):
        """Validate pH ranges are logical."""
        if (self.optimal_ph_min is not None and self.optimal_ph_max is not None and 
            self.optimal_ph_min >= self.optimal_ph_max):
            raise ValueError("Optimal pH minimum must be less than maximum")
        
        if (self.tolerable_ph_min is not None and self.tolerable_ph_max is not None and
            self.tolerable_ph_min >= self.tolerable_ph_max):
            raise ValueError("Tolerable pH minimum must be less than maximum")


class CropNutritionalProfile(BaseModel):
    """Nutritional composition and feed value data."""
    
    nutrition_id: Optional[UUID] = Field(None, description="Unique nutritional profile identifier")
    
    # Macronutrients (per 100g fresh weight)
    calories_per_100g: Optional[float] = Field(None, ge=0, description="Calories per 100g")
    protein_g_per_100g: Optional[float] = Field(None, ge=0, description="Protein content (g/100g)")
    carbohydrates_g_per_100g: Optional[float] = Field(None, ge=0, description="Carbohydrate content (g/100g)")
    fiber_g_per_100g: Optional[float] = Field(None, ge=0, description="Fiber content (g/100g)")
    fat_g_per_100g: Optional[float] = Field(None, ge=0, description="Fat content (g/100g)")
    sugar_g_per_100g: Optional[float] = Field(None, ge=0, description="Sugar content (g/100g)")
    
    # Minerals (mg per 100g unless specified)
    calcium_mg: Optional[float] = Field(None, ge=0, description="Calcium content (mg/100g)")
    iron_mg: Optional[float] = Field(None, ge=0, description="Iron content (mg/100g)")
    magnesium_mg: Optional[float] = Field(None, ge=0, description="Magnesium content (mg/100g)")
    phosphorus_mg: Optional[float] = Field(None, ge=0, description="Phosphorus content (mg/100g)")
    potassium_mg: Optional[float] = Field(None, ge=0, description="Potassium content (mg/100g)")
    sodium_mg: Optional[float] = Field(None, ge=0, description="Sodium content (mg/100g)")
    zinc_mg: Optional[float] = Field(None, ge=0, description="Zinc content (mg/100g)")
    
    # Vitamins
    vitamin_c_mg: Optional[float] = Field(None, ge=0, description="Vitamin C content (mg/100g)")
    vitamin_a_iu: Optional[int] = Field(None, ge=0, description="Vitamin A content (IU/100g)")
    vitamin_k_mcg: Optional[float] = Field(None, ge=0, description="Vitamin K content (mcg/100g)")
    folate_mcg: Optional[float] = Field(None, ge=0, description="Folate content (mcg/100g)")
    
    # Specialized compounds
    antioxidant_capacity_orac: Optional[int] = Field(None, ge=0, description="ORAC antioxidant capacity")
    phenolic_compounds_mg: Optional[float] = Field(None, ge=0, description="Phenolic compounds (mg/100g)")
    
    # Feed value (for livestock crops)
    crude_protein_percent: Optional[float] = Field(None, ge=0, le=100, description="Crude protein percentage")
    digestible_energy_mcal_kg: Optional[float] = Field(None, ge=0, description="Digestible energy (Mcal/kg)")
    neutral_detergent_fiber_percent: Optional[float] = Field(None, ge=0, le=100, description="NDF percentage")
    
    # Industrial/commercial values  
    oil_content_percent: Optional[float] = Field(None, ge=0, le=100, description="Oil content percentage")
    starch_content_percent: Optional[float] = Field(None, ge=0, le=100, description="Starch content percentage")
    cellulose_content_percent: Optional[float] = Field(None, ge=0, le=100, description="Cellulose content percentage")
    
    # Metadata
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    @validator('crude_protein_percent', 'oil_content_percent', 'starch_content_percent', 'cellulose_content_percent')
    def validate_percentages(cls, v):
        """Validate percentage values are reasonable."""
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Percentage values must be between 0 and 100")
        return v


# ============================================================================
# COMPREHENSIVE CROP DATA MODEL
# ============================================================================

class ComprehensiveCropData(BaseModel):
    """Complete crop data combining all taxonomic and agricultural information."""
    
    # Core identification
    crop_id: Optional[UUID] = Field(None, description="Unique crop identifier")
    crop_name: str = Field(..., description="Primary common name")
    crop_code: Optional[str] = Field(None, description="Standardized crop code")
    
    # External classification codes
    fao_crop_code: Optional[str] = Field(None, description="FAO crop classification code")
    usda_crop_code: Optional[str] = Field(None, description="USDA crop classification code")
    
    # Taxonomic data
    taxonomic_hierarchy: Optional[CropTaxonomicHierarchy] = Field(None, description="Botanical classification")
    agricultural_classification: Optional[CropAgriculturalClassification] = Field(None, description="Agricultural classification")
    climate_adaptations: Optional[CropClimateAdaptations] = Field(None, description="Climate adaptation data")
    soil_requirements: Optional[CropSoilRequirements] = Field(None, description="Soil requirements")
    nutritional_profile: Optional[CropNutritionalProfile] = Field(None, description="Nutritional composition")
    
    # Search and categorization
    search_keywords: List[str] = Field(default_factory=list, description="Search keywords")
    tags: List[str] = Field(default_factory=list, description="Categorization tags")

    # Data quality metadata
    data_source: Optional[str] = Field(None, description="Source system for the crop data")
    confidence_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence score for the crop data"
    )

    # Special classifications
    is_cover_crop: bool = Field(default=False, description="Is primarily used as cover crop")
    is_companion_crop: bool = Field(default=False, description="Suitable as companion crop")

    # Status and metadata
    crop_status: str = Field(default="active", description="Crop status (active, deprecated, experimental, regional)")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    last_updated: Optional[datetime] = Field(None, description="Alias for updated timestamp")

    @root_validator(pre=True)
    def synchronize_last_updated(cls, values):
        """Keep updated timestamps synchronized."""
        updated_value = values.get('updated_at')
        last_value = values.get('last_updated')
        if last_value is None and updated_value is not None:
            values['last_updated'] = updated_value
        elif updated_value is None and last_value is not None:
            values['updated_at'] = last_value
        return values

    @validator('crop_status')
    def validate_crop_status(cls, v):
        """Validate crop status values."""
        valid_statuses = {'active', 'deprecated', 'experimental', 'regional'}
        if v not in valid_statuses:
            raise ValueError(f"Crop status must be one of: {valid_statuses}")
        return v
    
    @validator('crop_name')
    def validate_crop_name(cls, v):
        """Validate crop name is not empty."""
        if not v or len(v.strip()) < 2:
            raise ValueError("Crop name must be at least 2 characters")
        return v.strip()

    @property
    def scientific_name(self) -> Optional[str]:
        """Get scientific name if taxonomic data exists."""
        if self.taxonomic_hierarchy:
            return self.taxonomic_hierarchy.scientific_name
        return None

    @property
    def primary_category(self) -> Optional[str]:
        """Get primary agricultural category if classification exists."""
        if self.agricultural_classification:
            return self.agricultural_classification.crop_category.value
        return None

    def get_suitable_zones(self) -> List[str]:
        """Get list of suitable hardiness zones."""
        if self.climate_adaptations and self.climate_adaptations.hardiness_zones:
            return self.climate_adaptations.hardiness_zones
        return []

    def get_temperature_range(self) -> Dict[str, Optional[float]]:
        """Get temperature tolerance range."""
        if not self.climate_adaptations:
            return {"min": None, "max": None}
        
        return {
            "optimal_min": self.climate_adaptations.optimal_temp_min_f,
            "optimal_max": self.climate_adaptations.optimal_temp_max_f,
            "absolute_min": self.climate_adaptations.absolute_temp_min_f,
            "absolute_max": self.climate_adaptations.absolute_temp_max_f
        }

    def get_ph_range(self) -> Dict[str, Optional[float]]:
        """Get pH tolerance range."""
        if not self.soil_requirements:
            return {"optimal_min": None, "optimal_max": None, "tolerable_min": None, "tolerable_max": None}
        
        return {
            "optimal_min": self.soil_requirements.optimal_ph_min,
            "optimal_max": self.soil_requirements.optimal_ph_max,
            "tolerable_min": self.soil_requirements.tolerable_ph_min,
            "tolerable_max": self.soil_requirements.tolerable_ph_max
        }


# ============================================================================
# BULK OPERATIONS AND VALIDATION MODELS  
# ============================================================================

class CropTaxonomyValidationResult(BaseModel):
    """Results of crop taxonomy validation."""
    
    crop_identifier: str = Field(..., description="Crop identifier being validated")
    is_valid: bool = Field(..., description="Overall validation result")
    validation_errors: List[str] = Field(default_factory=list, description="Validation error messages")
    validation_warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    
    # Specific validation results
    taxonomic_validation: Dict[str, bool] = Field(default_factory=dict, description="Taxonomic field validation")
    agricultural_validation: Dict[str, bool] = Field(default_factory=dict, description="Agricultural field validation")
    climate_validation: Dict[str, bool] = Field(default_factory=dict, description="Climate data validation")
    soil_validation: Dict[str, bool] = Field(default_factory=dict, description="Soil data validation")
    
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Validation confidence score")


class BulkCropImportRequest(BaseModel):
    """Request for importing multiple crops in bulk."""
    
    crops_data: List[ComprehensiveCropData] = Field(..., description="List of crops to import")
    validation_level: str = Field(default="standard", description="Validation strictness (basic, standard, strict)")
    skip_duplicates: bool = Field(default=True, description="Skip crops that already exist")
    update_existing: bool = Field(default=False, description="Update existing crops with new data")
    
    @validator('crops_data')
    def validate_crop_count(cls, v):
        """Validate reasonable crop count for bulk operations."""
        if len(v) > 1000:
            raise ValueError("Bulk import limited to 1000 crops per request")
        return v


class BulkCropImportResponse(BaseModel):
    """Response from bulk crop import operation."""
    
    import_id: str = Field(..., description="Unique import operation identifier")
    total_submitted: int = Field(..., description="Total crops submitted for import")
    successfully_imported: int = Field(..., description="Crops successfully imported")
    failed_imports: int = Field(..., description="Crops that failed import")
    skipped_duplicates: int = Field(..., description="Crops skipped as duplicates")
    updated_existing: int = Field(..., description="Existing crops updated")
    
    # Detailed results
    import_results: List[CropTaxonomyValidationResult] = Field(..., description="Detailed import results per crop")
    error_summary: Dict[str, int] = Field(default_factory=dict, description="Summary of error types")
    
    # Processing metadata
    processing_time_seconds: float = Field(..., description="Total processing time")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Response generation time")
