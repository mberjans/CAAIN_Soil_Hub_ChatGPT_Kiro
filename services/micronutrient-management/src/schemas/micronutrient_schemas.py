from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class MicronutrientType(str, Enum):
    BORON = "Boron"
    COPPER = "Copper"
    IRON = "Iron"
    MANGANESE = "Manganese"
    MOLYBDENUM = "Molybdenum"
    ZINC = "Zinc"
    CHLORINE = "Chlorine"
    NICKEL = "Nickel"

class MicronutrientLevel(BaseModel):
    nutrient_type: MicronutrientType = Field(..., description="Type of micronutrient")
    level_ppm: float = Field(..., ge=0, description="Current level in parts per million (ppm)")
    unit: str = Field("ppm", description="Unit of measurement for the level")

class RecommendationPriority(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    OPTIMAL = "Optimal"

class MicronutrientRecommendation(BaseModel):
    nutrient_type: MicronutrientType = Field(..., description="Type of micronutrient")
    priority: RecommendationPriority = Field(..., description="Priority level for the recommendation")
    recommended_amount: Optional[float] = Field(None, ge=0, description="Recommended amount to apply")
    unit: Optional[str] = Field(None, description="Unit of measurement for the recommended amount (e.g., kg/ha, lb/acre)")
    application_method: Optional[str] = Field(None, description="Suggested application method (e.g., foliar, soil)")
    justification: str = Field(..., description="Explanation for the recommendation")
    crop_impact: Optional[str] = Field(None, description="Expected impact on crop health/yield")

class MicronutrientRecommendationRequest(BaseModel):
    farm_location_id: str = Field(..., description="ID of the farm location")
    crop_type: str = Field(..., description="Type of crop being grown")
    growth_stage: Optional[str] = Field(None, description="Current growth stage of the crop")
    soil_type: str = Field(..., description="Soil type (e.g., sandy, clay, loam)")
    soil_ph: float = Field(..., ge=0, le=14, description="Current soil pH")
    organic_matter_percent: float = Field(..., ge=0, le=100, description="Organic matter percentage in soil")
    current_micronutrient_levels: List[MicronutrientLevel] = Field(..., description="Current levels of micronutrients in the soil")
    yield_goal_bushels_per_acre: Optional[float] = Field(None, ge=0, description="Target yield goal in bushels per acre")

class MicronutrientRecommendationResponse(BaseModel):
    request_id: str = Field(..., description="Unique ID for the recommendation request")
    recommendations: List[MicronutrientRecommendation] = Field(..., description="List of micronutrient recommendations")
    overall_status: str = Field(..., description="Overall status of micronutrient levels (e.g., 'Deficient', 'Optimal', 'Excess')")
    warnings: List[str] = Field(default_factory=list, description="List of warnings or alerts")
    metadata: dict = Field(default_factory=dict, description="Additional metadata about the recommendation")