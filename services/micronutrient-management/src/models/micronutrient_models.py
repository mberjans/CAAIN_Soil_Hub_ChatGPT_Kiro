from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class MicronutrientName(str, Enum):
    BORON = "Boron"
    COPPER = "Copper"
    IRON = "Iron"
    MANGANESE = "Manganese"
    MOLYBDENUM = "Molybdenum"
    ZINC = "Zinc"
    CHLORINE = "Chlorine"
    NICKEL = "Nickel"

class DeficiencySeverity(str, Enum):
    NONE = "None"
    MILD = "Mild"
    MODERATE = "Moderate"
    SEVERE = "Severe"

class Micronutrient(BaseModel):
    name: MicronutrientName = Field(..., description="Name of the micronutrient")
    symbol: str = Field(..., description="Chemical symbol of the micronutrient")
    role_in_plant: str = Field(..., description="Primary role of the micronutrient in plant physiology")
    optimal_soil_range_ppm: Optional[str] = Field(None, description="Optimal soil concentration range in ppm")
    toxicity_threshold_ppm: Optional[str] = Field(None, description="Toxicity threshold in soil in ppm")

class DeficiencySymptom(BaseModel):
    micronutrient: MicronutrientName = Field(..., description="Micronutrient associated with the symptom")
    symptom_name: str = Field(..., description="Name of the symptom (e.g., 'Chlorosis', 'Necrosis')")
    description: str = Field(..., description="Detailed description of the symptom")
    affected_plant_part: str = Field(..., description="Part of the plant typically affected (e.g., 'Young leaves', 'Older leaves')")
    severity_indicator: DeficiencySeverity = Field(..., description="Severity level at which this symptom is typically observed")
    image_url: Optional[str] = Field(None, description="URL to an image illustrating the symptom")

class CropMicronutrientRequirement(BaseModel):
    crop_name: str = Field(..., description="Name of the crop")
    micronutrient: MicronutrientName = Field(..., description="Micronutrient required by the crop")
    required_amount_per_ton_yield_g: Optional[float] = Field(None, description="Required amount per ton of yield in grams")
    critical_soil_level_ppm: Optional[float] = Field(None, description="Critical soil level for the crop in ppm")
    sensitivity_to_deficiency: DeficiencySeverity = Field(..., description="How sensitive the crop is to this micronutrient's deficiency")
    sensitivity_to_toxicity: DeficiencySeverity = Field(..., description="How sensitive the crop is to this micronutrient's toxicity")

class MicronutrientRecommendation(BaseModel):
    nutrient: MicronutrientName
    recommendation: str
    priority: int
    confidence: float
    details: Optional[str] = None
    severity: DeficiencySeverity = Field(DeficiencySeverity.NONE, description="Detected severity of the deficiency")
    application_method: Optional[str] = Field(None, description="Recommended application method (e.g., foliar, soil)")
    timing: Optional[str] = Field(None, description="Recommended timing for application (e.g., pre-plant, vegetative stage)")
    economic_impact: Optional[str] = Field(None, description="Potential economic impact of applying/not applying")