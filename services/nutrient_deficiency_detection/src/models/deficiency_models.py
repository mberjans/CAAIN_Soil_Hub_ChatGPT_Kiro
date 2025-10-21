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
    UNKNOWN = "unknown"

class Severity(str, Enum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"

class Symptom(BaseModel):
    name: str = Field(..., description="Name of the symptom (e.g., 'chlorosis', 'necrosis')")
    location: str = Field(..., description="Location on the plant (e.g., 'older leaves', 'new growth')")
    description: Optional[str] = Field(None, description="Detailed description of the symptom")

class DetectedDeficiency(BaseModel):
    nutrient: Nutrient = Field(..., description="The nutrient identified as deficient")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the detection (0.0-1.0)")
    severity: Severity = Field(..., description="Severity of the deficiency")
    affected_area_percent: float = Field(..., ge=0.0, le=100.0, description="Percentage of plant/field affected")
    symptoms: List[Symptom] = Field(..., description="List of symptoms observed for this deficiency")
    source: str = Field(..., description="Source of detection (e.g., 'image_analysis', 'manual_input')")

class NutrientDeficiencyScore(BaseModel):
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Overall deficiency score (0-100)")
    nutrient_scores: dict[Nutrient, float] = Field(..., description="Scores for individual nutrients")
    highest_priority_nutrient: Optional[Nutrient] = Field(None, description="The nutrient with the highest priority for intervention")
    recommendation_priority: Severity = Field(..., description="Overall recommendation priority based on the highest score")
    detailed_analysis: str = Field(..., description="A brief summary of the scoring rationale")