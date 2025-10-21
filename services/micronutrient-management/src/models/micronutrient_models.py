from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class MicronutrientName(str, Enum):
    BORON = "Boron"
    CHLORINE = "Chlorine"
    COPPER = "Copper"
    IRON = "Iron"
    MANGANESE = "Manganese"
    MOLYBDENUM = "Molybdenum"
    ZINC = "Zinc"
    NICKEL = "Nickel"

class MicronutrientRole(str, Enum):
    ENZYME_ACTIVATION = "Enzyme Activation"
    CHLOROPHYLL_FORMATION = "Chlorophyll Formation"
    NITROGEN_METABOLISM = "Nitrogen Metabolism"
    CELL_WALL_INTEGRITY = "Cell Wall Integrity"
    PHOTOSYNTHESIS = "Photosynthesis"
    HORMONE_SYNTHESIS = "Hormone Synthesis"
    STRESS_TOLERANCE = "Stress Tolerance"

class DeficiencySymptom(BaseModel):
    description: str = Field(..., description="Description of the deficiency symptom")
    severity_level: str = Field(..., description="Severity level (e.g., mild, moderate, severe)")
    affected_parts: List[str] = Field(..., description="Parts of the plant affected (e.g., young leaves, old leaves, fruit)")
    visual_cues: List[str] = Field(..., description="Visual cues (e.g., chlorosis, necrosis, stunted growth)")

class ToxicitySymptom(BaseModel):
    description: str = Field(..., description="Description of the toxicity symptom")
    severity_level: str = Field(..., description="Severity level (e.g., mild, moderate, severe)")
    affected_parts: List[str] = Field(..., description="Parts of the plant affected (e.g., root tips, older leaves)")
    visual_cues: List[str] = Field(..., description="Visual cues (e.g., bronzing, scorching, reduced root growth)")

class Micronutrient(BaseModel):
    name: MicronutrientName = Field(..., description="Name of the micronutrient")
    symbol: str = Field(..., description="Chemical symbol of the micronutrient")
    roles: List[MicronutrientRole] = Field(..., description="Key roles in plant physiology")
    deficiency_symptoms: List[DeficiencySymptom] = Field(default_factory=list, description="Common deficiency symptoms")
    toxicity_symptoms: List[ToxicitySymptom] = Field(default_factory=list, description="Common toxicity symptoms")
    soil_concentration_ideal_ppm: Optional[float] = Field(None, description="Ideal soil concentration in ppm")
    soil_concentration_deficient_ppm: Optional[float] = Field(None, description="Deficient soil concentration in ppm")
    soil_concentration_toxic_ppm: Optional[float] = Field(None, description="Toxic soil concentration in ppm")

class MicronutrientRequirement(BaseModel):
    crop_name: str = Field(..., description="Name of the crop")
    micronutrient: MicronutrientName = Field(..., description="Name of the micronutrient")
    required_amount_per_ton_yield_g: Optional[float] = Field(None, description="Required amount per ton of yield in grams")
    critical_leaf_concentration_ppm: Optional[float] = Field(None, description="Critical leaf concentration in ppm")
    optimal_ph_range_min: Optional[float] = Field(None, description="Minimum optimal pH for availability")
    optimal_ph_range_max: Optional[float] = Field(None, description="Maximum optimal pH for availability")
    notes: Optional[str] = Field(None, description="Additional notes on crop-specific requirements")
