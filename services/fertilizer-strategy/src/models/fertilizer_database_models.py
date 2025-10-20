"""
Pydantic models for comprehensive fertilizer database and classification system.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum
from uuid import UUID


class FertilizerTypeEnum(str, Enum):
    """Types of fertilizers based on form and release mechanism."""
    ORGANIC_SOLID = "organic_solid"
    ORGANIC_LIQUID = "organic_liquid"
    SYNTHETIC_GRANULAR = "synthetic_granular"
    SYNTHETIC_LIQUID = "synthetic_liquid"
    SLOW_RELEASE_COATED = "slow_release_coated"
    SLOW_RELEASE_MATRIX = "slow_release_matrix"
    SPECIALTY_MICRONUTRIENT = "specialty_micronutrient"
    BIO_STIMULANT = "bio_stimulant"
    CUSTOM_BLEND = "custom_blend"


class NutrientReleasePattern(str, Enum):
    """Nutrient release patterns for fertilizers."""
    IMMEDIATE = "immediate"
    SLOW_RELEASE_30_DAYS = "slow_release_30_days"
    SLOW_RELEASE_60_DAYS = "slow_release_60_days"
    SLOW_RELEASE_90_DAYS = "slow_release_90_days"
    CONTROLLED_RELEASE_TEMPERATURE = "controlled_release_temperature"
    CONTROLLED_RELEASE_MOISTURE = "controlled_release_moisture"
    STABILIZED = "stabilized"


class PhysicalForm(str, Enum):
    """Physical form of fertilizer."""
    GRANULAR = "granular"
    LIQUID = "liquid"
    POWDER = "powder"
    PELLET = "pellet"
    SUSPENSION = "suspension"
    SOLUTION = "solution"


class CompatibilityLevel(str, Enum):
    """Compatibility level for mixing fertilizers."""
    COMPATIBLE = "compatible"
    CAUTION = "caution"
    INCOMPATIBLE = "incompatible"


class ClassificationType(str, Enum):
    """Types of fertilizer classification systems."""
    NUTRIENT_BASED = "nutrient_based"
    SOURCE_BASED = "source_based"
    RELEASE_BASED = "release_based"
    APPLICATION_BASED = "application_based"


class NutrientAnalysis(BaseModel):
    """Model for fertilizer nutrient analysis."""
    nitrogen_percent: float = Field(default=0.0, ge=0.0, le=100.0, description="Nitrogen content (N)")
    phosphorus_percent: float = Field(default=0.0, ge=0.0, le=100.0, description="Phosphorus content (P2O5)")
    potassium_percent: float = Field(default=0.0, ge=0.0, le=100.0, description="Potassium content (K2O)")
    sulfur_percent: float = Field(default=0.0, ge=0.0, le=100.0, description="Sulfur content (S)")
    calcium_percent: float = Field(default=0.0, ge=0.0, le=100.0, description="Calcium content (Ca)")
    magnesium_percent: float = Field(default=0.0, ge=0.0, le=100.0, description="Magnesium content (Mg)")
    micronutrients: Dict[str, float] = Field(
        default_factory=dict,
        description="Micronutrient content (zinc, iron, manganese, copper, boron, molybdenum)"
    )

    def get_npk_ratio(self) -> str:
        """Get the NPK ratio as a string (e.g., '10-10-10')."""
        n = int(round(self.nitrogen_percent))
        p = int(round(self.phosphorus_percent))
        k = int(round(self.potassium_percent))
        return f"{n}-{p}-{k}"

    def get_total_nutrients(self) -> float:
        """Calculate total primary nutrients percentage."""
        return self.nitrogen_percent + self.phosphorus_percent + self.potassium_percent

    def is_balanced(self, tolerance: float = 5.0) -> bool:
        """Check if NPK is balanced within tolerance."""
        if self.nitrogen_percent == 0 and self.phosphorus_percent == 0 and self.potassium_percent == 0:
            return False

        avg = (self.nitrogen_percent + self.phosphorus_percent + self.potassium_percent) / 3
        n_diff = abs(self.nitrogen_percent - avg)
        p_diff = abs(self.phosphorus_percent - avg)
        k_diff = abs(self.potassium_percent - avg)

        return n_diff <= tolerance and p_diff <= tolerance and k_diff <= tolerance


class EnvironmentalImpact(BaseModel):
    """Model for environmental impact assessment."""
    runoff_risk: str = Field(default="medium", description="Risk of nutrient runoff (low/medium/high)")
    volatilization_risk: str = Field(default="medium", description="Risk of nitrogen volatilization")
    leaching_risk: str = Field(default="medium", description="Risk of nutrient leaching")
    carbon_footprint: float = Field(default=0.0, description="Carbon footprint (kg CO2e per unit)")
    environmental_notes: Optional[str] = Field(None, description="Additional environmental considerations")

    @field_validator('runoff_risk', 'volatilization_risk', 'leaching_risk')
    @classmethod
    def validate_risk_level(cls, v):
        valid_levels = ['low', 'medium', 'high']
        if v.lower() not in valid_levels:
            raise ValueError(f'Risk level must be one of: {valid_levels}')
        return v.lower()


class CostData(BaseModel):
    """Model for fertilizer cost information."""
    average_cost_per_unit: float = Field(..., gt=0, description="Average cost per unit")
    cost_unit: str = Field(default="ton", description="Unit of measurement (ton, gallon, lb, kg)")
    price_volatility: float = Field(default=0.0, ge=0.0, description="Price volatility (standard deviation)")
    availability_score: float = Field(default=7.0, ge=0.0, le=10.0, description="Product availability (0-10)")
    last_price_update: Optional[date] = Field(None, description="Date of last price update")

    @field_validator('cost_unit')
    @classmethod
    def validate_cost_unit(cls, v):
        valid_units = ['ton', 'gallon', 'lb', 'kg', 'metric_ton', 'liter']
        if v.lower() not in valid_units:
            raise ValueError(f'Cost unit must be one of: {valid_units}')
        return v.lower()


class FertilizerProduct(BaseModel):
    """Complete model for fertilizer product."""
    # Identification
    product_id: Optional[UUID] = Field(None, description="Unique product identifier")
    product_name: str = Field(..., min_length=1, max_length=255, description="Product name")
    manufacturer: Optional[str] = Field(None, max_length=255, description="Manufacturer name")
    fertilizer_type: FertilizerTypeEnum = Field(..., description="Fertilizer type classification")

    # Nutrient Analysis
    nitrogen_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    phosphorus_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    potassium_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    sulfur_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    calcium_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    magnesium_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    micronutrients: Dict[str, float] = Field(default_factory=dict)

    # Physical Properties
    physical_form: Optional[str] = Field(None, description="Physical form (granular, liquid, etc.)")
    particle_size: Optional[str] = Field(None, description="Particle size (SGN rating or mesh)")
    bulk_density: Optional[float] = Field(None, description="Bulk density (lbs/cubic foot)")
    solubility: Optional[str] = Field(None, description="Solubility characteristics")
    release_pattern: NutrientReleasePattern = Field(default=NutrientReleasePattern.IMMEDIATE)

    # Application Methods
    application_methods: List[str] = Field(default_factory=list, description="Compatible application methods")
    compatible_equipment: List[str] = Field(default_factory=list, description="Compatible equipment types")
    mixing_compatibility: Dict[str, Any] = Field(default_factory=dict, description="Mixing compatibility info")

    # Environmental Impact
    environmental_impact: Dict[str, Any] = Field(default_factory=dict)
    organic_certified: bool = Field(default=False, description="Organic certification status")
    sustainability_rating: float = Field(default=5.0, ge=0.0, le=10.0, description="Sustainability rating (0-10)")

    # Cost Data
    average_cost_per_unit: Optional[float] = Field(None, description="Average cost per unit")
    cost_unit: str = Field(default="ton", description="Cost unit")
    price_volatility: float = Field(default=0.0, ge=0.0, description="Price volatility")
    availability_score: float = Field(default=7.0, ge=0.0, le=10.0, description="Availability score")

    # Regulatory and Safety
    regulatory_status: Optional[str] = Field(None, description="Regulatory approval status")
    safety_data: Dict[str, Any] = Field(default_factory=dict, description="Safety data sheet info")
    handling_requirements: List[str] = Field(default_factory=list, description="Special handling requirements")
    storage_requirements: List[str] = Field(default_factory=list, description="Storage requirements")

    # Crop Compatibility
    recommended_crops: List[str] = Field(default_factory=list, description="Recommended crop types")
    not_recommended_crops: List[str] = Field(default_factory=list, description="Crops to avoid")
    growth_stage_suitability: Dict[str, bool] = Field(default_factory=dict, description="Suitable growth stages")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    data_source: Optional[str] = Field(None, description="Source of product data")
    last_verified: Optional[datetime] = Field(None, description="Last verification timestamp")
    is_active: bool = Field(default=True, description="Product active status")

    def get_nutrient_analysis(self) -> NutrientAnalysis:
        """Get nutrient analysis as a structured object."""
        return NutrientAnalysis(
            nitrogen_percent=self.nitrogen_percent,
            phosphorus_percent=self.phosphorus_percent,
            potassium_percent=self.potassium_percent,
            sulfur_percent=self.sulfur_percent,
            calcium_percent=self.calcium_percent,
            magnesium_percent=self.magnesium_percent,
            micronutrients=self.micronutrients
        )

    def get_npk_ratio(self) -> str:
        """Get NPK ratio string."""
        return self.get_nutrient_analysis().get_npk_ratio()

    def is_suitable_for_crop(self, crop: str, growth_stage: Optional[str] = None) -> bool:
        """Check if fertilizer is suitable for a specific crop and growth stage."""
        # Check if crop is in not_recommended list
        crop_lower = crop.lower()
        for not_rec in self.not_recommended_crops:
            if not_rec.lower() == crop_lower:
                return False

        # Check if crop is in recommended list
        is_recommended = False
        for rec in self.recommended_crops:
            if rec.lower() == crop_lower:
                is_recommended = True
                break

        # If growth stage specified, check suitability
        if growth_stage and self.growth_stage_suitability:
            stage_suitable = self.growth_stage_suitability.get(growth_stage.lower(), False)
            return is_recommended and stage_suitable

        return is_recommended

    model_config = {
        "json_schema_extra": {
            "example": {
                "product_name": "Urea 46-0-0",
                "manufacturer": "Acme Fertilizer Co.",
                "fertilizer_type": "synthetic_granular",
                "nitrogen_percent": 46.0,
                "phosphorus_percent": 0.0,
                "potassium_percent": 0.0,
                "physical_form": "granular",
                "application_methods": ["broadcast", "banded"],
                "recommended_crops": ["corn", "wheat", "rice"]
            }
        }
    }


class FertilizerProductCreate(BaseModel):
    """Model for creating a new fertilizer product."""
    product_name: str = Field(..., min_length=1, max_length=255)
    manufacturer: Optional[str] = Field(None, max_length=255)
    fertilizer_type: FertilizerTypeEnum

    # Nutrient Analysis
    nitrogen_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    phosphorus_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    potassium_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    sulfur_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    calcium_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    magnesium_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    micronutrients: Dict[str, float] = Field(default_factory=dict)

    # Physical Properties
    physical_form: Optional[str] = None
    particle_size: Optional[str] = None
    bulk_density: Optional[float] = None
    solubility: Optional[str] = None
    release_pattern: NutrientReleasePattern = Field(default=NutrientReleasePattern.IMMEDIATE)

    # Application Methods
    application_methods: List[str] = Field(default_factory=list)
    compatible_equipment: List[str] = Field(default_factory=list)
    mixing_compatibility: Dict[str, Any] = Field(default_factory=dict)

    # Environmental Impact
    environmental_impact: Dict[str, Any] = Field(default_factory=dict)
    organic_certified: bool = Field(default=False)
    sustainability_rating: float = Field(default=5.0, ge=0.0, le=10.0)

    # Cost Data
    average_cost_per_unit: Optional[float] = None
    cost_unit: str = Field(default="ton")
    price_volatility: float = Field(default=0.0, ge=0.0)
    availability_score: float = Field(default=7.0, ge=0.0, le=10.0)

    # Regulatory and Safety
    regulatory_status: Optional[str] = None
    safety_data: Dict[str, Any] = Field(default_factory=dict)
    handling_requirements: List[str] = Field(default_factory=list)
    storage_requirements: List[str] = Field(default_factory=list)

    # Crop Compatibility
    recommended_crops: List[str] = Field(default_factory=list)
    not_recommended_crops: List[str] = Field(default_factory=list)
    growth_stage_suitability: Dict[str, bool] = Field(default_factory=dict)

    # Metadata
    data_source: Optional[str] = None


class FertilizerProductUpdate(BaseModel):
    """Model for updating a fertilizer product."""
    product_name: Optional[str] = Field(None, min_length=1, max_length=255)
    manufacturer: Optional[str] = Field(None, max_length=255)
    fertilizer_type: Optional[FertilizerTypeEnum] = None

    # All fields optional for partial updates
    nitrogen_percent: Optional[float] = Field(None, ge=0.0, le=100.0)
    phosphorus_percent: Optional[float] = Field(None, ge=0.0, le=100.0)
    potassium_percent: Optional[float] = Field(None, ge=0.0, le=100.0)
    sulfur_percent: Optional[float] = Field(None, ge=0.0, le=100.0)
    calcium_percent: Optional[float] = Field(None, ge=0.0, le=100.0)
    magnesium_percent: Optional[float] = Field(None, ge=0.0, le=100.0)
    micronutrients: Optional[Dict[str, float]] = None

    physical_form: Optional[str] = None
    particle_size: Optional[str] = None
    bulk_density: Optional[float] = None
    solubility: Optional[str] = None
    release_pattern: Optional[NutrientReleasePattern] = None

    application_methods: Optional[List[str]] = None
    compatible_equipment: Optional[List[str]] = None
    mixing_compatibility: Optional[Dict[str, Any]] = None

    environmental_impact: Optional[Dict[str, Any]] = None
    organic_certified: Optional[bool] = None
    sustainability_rating: Optional[float] = Field(None, ge=0.0, le=10.0)

    average_cost_per_unit: Optional[float] = None
    cost_unit: Optional[str] = None
    price_volatility: Optional[float] = Field(None, ge=0.0)
    availability_score: Optional[float] = Field(None, ge=0.0, le=10.0)

    regulatory_status: Optional[str] = None
    safety_data: Optional[Dict[str, Any]] = None
    handling_requirements: Optional[List[str]] = None
    storage_requirements: Optional[List[str]] = None

    recommended_crops: Optional[List[str]] = None
    not_recommended_crops: Optional[List[str]] = None
    growth_stage_suitability: Optional[Dict[str, bool]] = None

    is_active: Optional[bool] = None


class FertilizerClassification(BaseModel):
    """Model for fertilizer classification."""
    classification_id: Optional[UUID] = None
    classification_type: ClassificationType = Field(..., description="Type of classification")
    classification_name: str = Field(..., min_length=1, max_length=100, description="Name of classification")
    description: Optional[str] = Field(None, description="Description of classification")
    criteria: Dict[str, Any] = Field(default_factory=dict, description="Classification criteria")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FertilizerCompatibility(BaseModel):
    """Model for fertilizer compatibility information."""
    compatibility_id: Optional[UUID] = None
    product_id_1: UUID = Field(..., description="First product ID")
    product_id_2: UUID = Field(..., description="Second product ID")
    compatibility_level: CompatibilityLevel = Field(..., description="Compatibility level")
    mixing_ratio_limits: Dict[str, float] = Field(
        default_factory=dict,
        description="Mixing ratio limits (max_ratio, recommended_ratio)"
    )
    notes: Optional[str] = Field(None, description="Additional compatibility notes")
    test_date: Optional[datetime] = Field(None, description="Date of compatibility testing")
    verified_by: Optional[str] = Field(None, description="Person/organization who verified")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('product_id_2')
    @classmethod
    def validate_different_products(cls, v, info):
        if 'product_id_1' in info.data and v == info.data['product_id_1']:
            raise ValueError('product_id_1 and product_id_2 must be different')
        return v


class NutrientAnalysisHistory(BaseModel):
    """Model for historical nutrient analysis records."""
    analysis_id: Optional[UUID] = None
    product_id: UUID = Field(..., description="Product being analyzed")
    analysis_date: date = Field(..., description="Date of analysis")
    nitrogen_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    phosphorus_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    potassium_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    sulfur_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    calcium_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    magnesium_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    micronutrients: Dict[str, float] = Field(default_factory=dict)
    analysis_method: Optional[str] = Field(None, description="Analysis method used")
    lab_name: Optional[str] = Field(None, description="Laboratory name")
    certified: bool = Field(default=False, description="Certified analysis")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ApplicationRecommendation(BaseModel):
    """Model for fertilizer application recommendations."""
    recommendation_id: Optional[UUID] = None
    product_id: UUID = Field(..., description="Product ID")
    crop_type: str = Field(..., description="Crop type")
    growth_stage: Optional[str] = Field(None, description="Growth stage")
    recommended_rate_min: float = Field(..., description="Minimum recommended rate")
    recommended_rate_max: float = Field(..., description="Maximum recommended rate")
    rate_unit: str = Field(default="lbs/acre", description="Rate unit")
    application_method: str = Field(..., description="Application method")
    application_timing: Optional[str] = Field(None, description="Application timing details")
    soil_condition_requirements: Dict[str, Any] = Field(
        default_factory=dict,
        description="Required soil conditions (pH, moisture, temperature)"
    )
    expected_response: Dict[str, Any] = Field(
        default_factory=dict,
        description="Expected crop response"
    )
    notes: Optional[str] = Field(None, description="Additional notes")
    research_source: Optional[str] = Field(None, description="Source of recommendation")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class FertilizerSearchFilters(BaseModel):
    """Model for fertilizer product search filters."""
    fertilizer_types: Optional[List[FertilizerTypeEnum]] = None
    min_nitrogen: Optional[float] = Field(None, ge=0.0, le=100.0)
    max_nitrogen: Optional[float] = Field(None, ge=0.0, le=100.0)
    min_phosphorus: Optional[float] = Field(None, ge=0.0, le=100.0)
    max_phosphorus: Optional[float] = Field(None, ge=0.0, le=100.0)
    min_potassium: Optional[float] = Field(None, ge=0.0, le=100.0)
    max_potassium: Optional[float] = Field(None, ge=0.0, le=100.0)
    organic_only: Optional[bool] = None
    crop_type: Optional[str] = None
    application_method: Optional[str] = None
    release_pattern: Optional[NutrientReleasePattern] = None
    min_sustainability_rating: Optional[float] = Field(None, ge=0.0, le=10.0)
    manufacturer: Optional[str] = None
    is_active: bool = Field(default=True)
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class FertilizerSearchResponse(BaseModel):
    """Model for fertilizer product search response."""
    products: List[FertilizerProduct] = Field(..., description="List of matching products")
    total_count: int = Field(..., description="Total number of matching products")
    limit: int = Field(..., description="Results limit")
    offset: int = Field(..., description="Results offset")
    filters_applied: Dict[str, Any] = Field(..., description="Filters that were applied")
