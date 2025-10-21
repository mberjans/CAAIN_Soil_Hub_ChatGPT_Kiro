from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum
from uuid import UUID, uuid4

class FertilizerTypeEnum(str, Enum):
    ORGANIC = "organic"
    SYNTHETIC = "synthetic"

class FertilizerFormEnum(str, Enum):
    LIQUID = "liquid"
    GRANULAR = "granular"
    GASEOUS = "gaseous" # e.g., anhydrous ammonia

class FertilizerReleaseTypeEnum(str, Enum):
    QUICK = "quick"
    SLOW = "slow"
    CONTROLLED = "controlled" # e.g., coated fertilizers

class EnvironmentalImpactEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class SuitabilityCriteria(BaseModel):
    min_ph: Optional[float] = Field(None, ge=0.0, le=14.0)
    max_ph: Optional[float] = Field(None, ge=0.0, le=14.0)
    min_temperature_celsius: Optional[float] = None
    max_temperature_celsius: Optional[float] = None
    soil_types: Optional[List[str]] = None # e.g., ["loam", "sandy"]
    climate_zones: Optional[List[str]] = None # e.g., ["5a", "6b"]
    crop_types: Optional[List[str]] = None # e.g., ["corn", "soybean"]
    application_methods: Optional[List[str]] = None # e.g., ["broadcast", "banded"]

class FertilizerType(BaseModel):
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the fertilizer type")
    name: str = Field(..., min_length=1, max_length=100, description="Name of the fertilizer type")
    description: Optional[str] = Field(None, max_length=500, description="Description of the fertilizer")
    npk_ratio: str = Field(..., pattern=r"^\d+-\d+-\d+$", description="NPK ratio (e.g., '10-10-10')")
    fertilizer_type: FertilizerTypeEnum = Field(..., description="Organic or synthetic fertilizer")
    form: FertilizerFormEnum = Field(..., description="Physical form of the fertilizer (liquid, granular, gaseous)")
    release_type: FertilizerReleaseTypeEnum = Field(..., description="How quickly nutrients are released")
    cost_per_unit: float = Field(..., gt=0, description="Cost per unit of fertilizer (e.g., per kg, per liter)")
    unit: str = Field(..., min_length=1, max_length=20, description="Unit of cost (e.g., 'USD/kg', 'USD/L')")
    environmental_impact_score: EnvironmentalImpactEnum = Field(..., description="Environmental impact assessment")
    suitability_criteria: Optional[SuitabilityCriteria] = Field(None, description="Criteria for suitability based on environmental and crop factors")
    manufacturer: Optional[str] = Field(None, max_length=100, description="Manufacturer of the fertilizer")
    active_ingredients: Optional[List[str]] = Field(None, description="List of active ingredients")
    safety_precautions: Optional[str] = Field(None, max_length=1000, description="Safety precautions for handling")
    storage_recommendations: Optional[str] = Field(None, max_length=500, description="Storage recommendations")
    application_rate_guidelines: Optional[Dict[str, str]] = Field(None, description="Guidelines for application rates per crop/stage")
