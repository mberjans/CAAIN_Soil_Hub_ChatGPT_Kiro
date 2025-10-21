from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class Micronutrient(str, Enum):
    """Enum for common micronutrients."""
    BORON = "Boron"
    CHLORINE = "Chlorine"
    COPPER = "Copper"
    IRON = "Iron"
    MANGANESE = "Manganese"
    MOLYBDENUM = "Molybdenum"
    ZINC = "Zinc"
    NICKEL = "Nickel"

class ToxicityRiskLevel(str, Enum):
    """Enum for micronutrient toxicity risk levels."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class OverApplicationWarning(str, Enum):
    """Enum for over-application warning levels."""
    NONE = "None"
    CAUTION = "Caution"
    WARNING = "Warning"
    CRITICAL = "Critical"

class MicronutrientThresholds(BaseModel):
    """Defines optimal ranges and toxicity thresholds for a micronutrient."""
    micronutrient: Micronutrient
    optimal_min_ppm: float = Field(..., description="Optimal minimum concentration in ppm")
    optimal_max_ppm: float = Field(..., description="Optimal maximum concentration in ppm")
    toxicity_threshold_ppm: float = Field(..., description="Concentration in ppm above which toxicity risk is high")
    over_application_threshold_ppm: float = Field(..., description="Concentration in ppm above which over-application is warned")
    unit: str = Field("ppm", description="Unit of concentration")

class MicronutrientData(BaseModel):
    """Represents current micronutrient levels in soil or tissue."""
    micronutrient: Micronutrient
    concentration: float = Field(..., description="Current concentration in ppm")
    unit: str = Field("ppm", description="Unit of concentration")

class ToxicityRiskAssessment(BaseModel):
    """Result of a micronutrient toxicity risk assessment."""
    micronutrient: Micronutrient
    current_concentration: float
    toxicity_threshold: float
    risk_level: ToxicityRiskLevel
    message: str

class OverApplicationAssessment(BaseModel):
    """Result of an over-application warning assessment."""
    micronutrient: Micronutrient
    current_concentration: float
    over_application_threshold: float
    warning_level: OverApplicationWarning
    message: str
    recommended_action: Optional[str] = None

class MicronutrientRecommendation(BaseModel):
    """Recommendation for micronutrient application."""
    micronutrient: Micronutrient
    required_amount: float = Field(..., description="Amount of micronutrient required")
    unit: str = Field(..., description="Unit of required amount (e.g., kg/ha, lb/acre)")
    application_method: Optional[str] = None
    timing: Optional[str] = None
    notes: Optional[str] = None
