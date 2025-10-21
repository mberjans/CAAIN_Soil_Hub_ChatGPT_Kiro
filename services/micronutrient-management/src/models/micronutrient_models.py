from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class ApplicationMethod(str, Enum):
    """Enum for different micronutrient application methods."""
    FOLIAR = "foliar"
    SOIL_BROADCAST = "soil_broadcast"
    SOIL_BANDED = "soil_banded"
    FERTIGATION = "fertigation"
    SEED_TREATMENT = "seed_treatment"
    CHEMIGATION = "chemigation"

class TimingStage(str, Enum):
    """Enum for different crop growth stages for timing recommendations."""
    PRE_PLANT = "pre_plant"
    PLANTING = "planting"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    FRUITING = "fruiting"
    GRAIN_FILL = "grain_fill"
    POST_HARVEST = "post_harvest"

class MicronutrientApplication(BaseModel):
    """Model for a recommended micronutrient application."""
    micronutrient: str = Field(..., description="Name of the micronutrient (e.g., 'Boron', 'Zinc')")
    method: ApplicationMethod = Field(..., description="Recommended application method")
    timing: TimingStage = Field(..., description="Recommended growth stage for application")
    rate: float = Field(..., gt=0, description="Recommended application rate")
    unit: str = Field(..., description="Unit of the application rate (e.g., 'kg/ha', 'lb/acre', 'ppm')")
    notes: Optional[str] = Field(None, description="Additional notes or considerations for the application")
    efficiency_score: Optional[float] = Field(None, ge=0, le=1, description="Estimated efficiency of this method/timing combination (0-1)")

class MicronutrientApplicationRequest(BaseModel):
    """Request model for micronutrient application recommendations."""
    crop_type: str = Field(..., description="Type of crop (e.g., 'Corn', 'Soybean')")
    growth_stage: TimingStage = Field(..., description="Current or target growth stage of the crop")
    soil_type: str = Field(..., description="Soil type (e.g., 'loam', 'sandy_loam')")
    current_micronutrient_levels: dict = Field(..., description="Current levels of micronutrients in soil or tissue (e.g., {'Boron': 0.5, 'Zinc': 1.2})")
    target_micronutrient_levels: dict = Field(..., description="Target levels of micronutrients (e.g., {'Boron': 1.0, 'Zinc': 2.0})")
    application_goals: List[str] = Field(..., description="Goals for application (e.g., ['maximize_yield', 'minimize_cost', 'improve_quality'])")
    farm_location_id: Optional[str] = Field(None, description="ID of the farm location for regional context")
    equipment_available: Optional[List[ApplicationMethod]] = Field(None, description="List of available application equipment")

class MicronutrientApplicationResponse(BaseModel):
    """Response model for micronutrient application recommendations."""
    recommendations: List[MicronutrientApplication] = Field(..., description="List of recommended micronutrient applications")
    overall_efficiency: Optional[float] = Field(None, ge=0, le=1, description="Overall estimated efficiency of the recommended plan")
    notes: Optional[str] = Field(None, description="General notes or warnings for the entire recommendation plan")
