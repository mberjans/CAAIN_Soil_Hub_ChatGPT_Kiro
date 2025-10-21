from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from uuid import UUID, uuid4

class MicronutrientName(str, Enum):
    """Enum for common micronutrient names."""
    BORON = "Boron"
    COPPER = "Copper"
    IRON = "Iron"
    MANGANESE = "Manganese"
    MOLYBDENUM = "Molybdenum"
    ZINC = "Zinc"
    CHLORINE = "Chlorine"
    NICKEL = "Nickel"

class MicronutrientSource(str, Enum):
    """Enum for the source of micronutrient data."""
    SOIL_TEST = "Soil Test"
    TISSUE_TEST = "Tissue Test"
    VISUAL_ASSESSMENT = "Visual Assessment"

class DeficiencySeverity(str, Enum):
    """Enum for the severity of a deficiency."""
    NONE = "None"
    MILD = "Mild"
    MODERATE = "Moderate"
    SEVERE = "Severe"

class MicronutrientLevel(BaseModel):
    """Represents the measured level of a micronutrient."""
    micronutrient: MicronutrientName
    value: float = Field(..., description="Measured value of the micronutrient")
    unit: str = Field(..., description="Unit of measurement (e.g., ppm, mg/kg, %)")
    source: MicronutrientSource
    optimal_min: Optional[float] = Field(None, description="Optimal minimum level for the crop/soil type")
    optimal_max: Optional[float] = Field(None, description="Optimal maximum level for the crop/soil type")

class DeficiencySymptom(BaseModel):
    """Describes a visual symptom of micronutrient deficiency."""
    symptom_id: UUID = Field(default_factory=uuid4)
    micronutrient: MicronutrientName
    description: str = Field(..., description="Description of the visual symptom")
    severity: DeficiencySeverity
    location_on_plant: str = Field(..., description="Where on the plant the symptom is observed (e.g., 'new leaves', 'old leaves', 'whole plant')")
    image_url: Optional[str] = Field(None, description="URL to an image illustrating the symptom")

class MicronutrientDeficiencyAssessment(BaseModel):
    """The result of a micronutrient deficiency assessment."""
    assessment_id: UUID = Field(default_factory=uuid4)
    farm_id: UUID
    field_id: UUID
    crop_type: str = Field(..., description="Type of crop being assessed")
    growth_stage: str = Field(..., description="Current growth stage of the crop")
    soil_type: str = Field(..., description="Soil type of the field")
    assessed_micronutrients: List[MicronutrientLevel] = Field(..., description="List of micronutrient levels assessed")
    identified_deficiencies: List[MicronutrientName] = Field(default_factory=list, description="List of micronutrients identified as deficient")
    visual_symptoms: List[DeficiencySymptom] = Field(default_factory=list, description="List of visual symptoms observed")
    overall_severity: DeficiencySeverity
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the assessment")
    assessment_date: str = Field(..., description="Date of the assessment (YYYY-MM-DD)")

class Recommendation(BaseModel):
    """A recommendation for correcting a micronutrient deficiency."""
    recommendation_id: UUID = Field(default_factory=uuid4)
    assessment_id: UUID
    micronutrient: MicronutrientName
    action: str = Field(..., description="Recommended action (e.g., 'Foliar application', 'Soil amendment')")
    product: str = Field(..., description="Recommended product (e.g., 'Zinc Sulfate', 'Chelated Iron')")
    rate: str = Field(..., description="Recommended application rate (e.g., '5 kg/ha', '2 lb/acre')")
    unit: str = Field(..., description="Unit for the application rate")
    timing: str = Field(..., description="Recommended application timing (e.g., 'Pre-plant', 'Early vegetative stage')")
    method: str = Field(..., description="Application method (e.g., 'Broadcast', 'Banded', 'Foliar spray')")
    notes: Optional[str] = Field(None, description="Additional notes or considerations")
    expected_response: Optional[str] = Field(None, description="Expected crop response")
    cost_estimate: Optional[float] = Field(None, description="Estimated cost of the recommendation")
    environmental_impact: Optional[str] = Field(None, description="Potential environmental impact")
