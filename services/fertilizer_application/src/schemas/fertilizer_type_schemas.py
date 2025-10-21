from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class FertilizerTypeEnum(str, Enum):
    ORGANIC = "organic"
    SYNTHETIC = "synthetic"
    SLOW_RELEASE = "slow_release"
    LIQUID = "liquid"
    GRANULAR = "granular"
    FOLIAR = "foliar"
    GASEOUS = "gaseous"

class EnvironmentalImpactEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class NPKRatio(BaseModel):
    N: float = Field(..., ge=0, description="Nitrogen percentage")
    P: float = Field(..., ge=0, description="Phosphorus percentage")
    K: float = Field(..., ge=0, description="Potassium percentage")

class FertilizerTypeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the fertilizer type")
    type: FertilizerTypeEnum = Field(..., description="Category of the fertilizer")
    npk_ratio: NPKRatio = Field(..., description="NPK ratio as a dictionary, e.g., {'N': 10, 'P': 10, 'K': 10}")
    micronutrients: Optional[Dict[str, float]] = Field(default_factory=dict, description="Micronutrients as a dictionary, e.g., {'Zn': 1, 'B': 0.5}")
    cost_per_unit: float = Field(..., gt=0, description="Cost per unit of the fertilizer")
    unit: str = Field(..., min_length=1, max_length=20, description="Unit of measurement for cost (e.g., 'kg', 'lb', 'gallon')")
    environmental_impact_score: EnvironmentalImpactEnum = Field(..., description="Environmental impact score")
    release_rate: Optional[str] = Field(None, max_length=50, description="Release rate (e.g., 'fast', 'medium', 'slow')")
    organic_certified: bool = Field(False, description="Whether the fertilizer is organic certified")
    application_methods: Optional[List[str]] = Field(default_factory=list, description="List of suitable application methods")
    description: Optional[str] = Field(None, description="Description of the fertilizer")

class FertilizerTypeCreate(FertilizerTypeBase):
    pass

class FertilizerTypeUpdate(FertilizerTypeBase):
    name: Optional[str] = None
    type: Optional[FertilizerTypeEnum] = None
    npk_ratio: Optional[NPKRatio] = None
    cost_per_unit: Optional[float] = None
    unit: Optional[str] = None
    environmental_impact_score: Optional[EnvironmentalImpactEnum] = None
    organic_certified: Optional[bool] = None

class FertilizerTypeInDB(FertilizerTypeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True