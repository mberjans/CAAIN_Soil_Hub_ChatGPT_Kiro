from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class Nutrient(str, Enum):
    NITROGEN = "nitrogen"
    PHOSPHORUS = "phosphorus"
    POTASSIUM = "potassium"
    CALCIUM = "calcium"
    MAGNESIUM = "magnesium"
    SULFUR = "sulfur"
    IRON = "iron"
    MANGANESE = "manganese"
    ZINC = "zinc"
    COPPER = "copper"
    BORON = "boron"
    MOLYBDENUM = "molybdenum"
    CHLORINE = "chlorine"
    NICKEL = "nickel"
    # Add other nutrients as needed

class GrowthStage(str, Enum):
    SEEDLING = "seedling"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    FRUITING = "fruiting"
    MATURITY = "maturity"
    # Add other growth stages as needed

class SymptomSeverity(str, Enum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"

class VisualCharacteristic(str, Enum):
    YELLOWING_LEAVES = "yellowing_leaves"
    PURPLE_TINTS = "purple_tints"
    STUNTED_GROWTH = "stunted_growth"
    NECROSIS = "necrosis"
    CHLOROSIS = "chlorosis"
    INTERVEINAL_CHLOROSIS = "interveinal_chlorosis"
    SPOTTING = "spotting"
    WILTING = "wilting"
    DEFORMED_FRUIT = "deformed_fruit"
    THIN_STEMS = "thin_stems"
    DARK_GREEN_LEAVES = "dark_green_leaves"
    # Add other visual characteristics as needed

class NutrientDeficiencySymptom(BaseModel):
    id: Optional[str] = Field(None, description="Unique identifier for the symptom")
    nutrient: Nutrient = Field(..., description="The nutrient associated with the deficiency")
    crop_type: str = Field(..., description="The type of crop (e.g., 'corn', 'soybean')")
    growth_stages: List[GrowthStage] = Field(..., description="Growth stages where the symptom typically appears")
    symptom_description: str = Field(..., description="A detailed description of the symptom")
    visual_characteristics: List[VisualCharacteristic] = Field(..., description="Key visual characteristics of the symptom")
    severity: SymptomSeverity = Field(..., description="Typical severity of the symptom")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score for the symptom definition")
    management_recommendations: Optional[str] = Field(None, description="General management recommendations")

    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "nutrient": "nitrogen",
                "crop_type": "corn",
                "growth_stages": ["vegetative", "flowering"],
                "symptom_description": "General yellowing of older leaves, starting from the tip and moving along the midrib.",
                "visual_characteristics": ["yellowing_leaves", "chlorosis"],
                "severity": "moderate",
                "confidence_score": 0.95,
                "management_recommendations": "Apply nitrogen fertilizer, consider split application."
            }
        }
