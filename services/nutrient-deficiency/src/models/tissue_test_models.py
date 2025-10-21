from pydantic import BaseModel, Field, UUID4
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class Nutrient(str, Enum):
    NITROGEN = "N"
    PHOSPHORUS = "P"
    POTASSIUM = "K"
    CALCIUM = "Ca"
    MAGNESIUM = "Mg"
    SULFUR = "S"
    BORON = "B"
    COPPER = "Cu"
    IRON = "Fe"
    MANGANESE = "Mn"
    ZINC = "Zn"
    MOLYBDENUM = "Mo"
    CHLORINE = "Cl"

class DeficiencySeverity(str, Enum):
    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"

class TissueTestResult(BaseModel):
    nutrient: Nutrient = Field(..., description="The nutrient being tested.")
    value: float = Field(..., description="The measured value of the nutrient in the tissue sample.")
    unit: str = Field(..., description="The unit of measurement (e.g., ppm, % dry weight).")
    optimal_min: Optional[float] = Field(None, description="Optimal minimum value for the nutrient for the given crop/stage.")
    optimal_max: Optional[float] = Field(None, description="Optimal maximum value for the nutrient for the given crop/stage.")

class TissueTestRequest(BaseModel):
    farm_id: UUID4 = Field(..., description="ID of the farm where the tissue test was conducted.")
    field_id: UUID4 = Field(..., description="ID of the field where the tissue test was conducted.")
    crop_type: str = Field(..., description="Type of crop (e.g., 'corn', 'soybean').")
    growth_stage: str = Field(..., description="Growth stage of the crop (e.g., 'V6', 'R1').")
    test_date: datetime = Field(..., description="Date the tissue test was performed.")
    results: List[TissueTestResult] = Field(..., description="List of individual nutrient test results.")
    notes: Optional[str] = Field(None, description="Any additional notes about the test.")

class NutrientDeficiency(BaseModel):
    nutrient: Nutrient = Field(..., description="The nutrient that is deficient.")
    severity: DeficiencySeverity = Field(..., description="The severity of the deficiency.")
    measured_value: float = Field(..., description="The measured value of the deficient nutrient.")
    optimal_range: Optional[Dict[str, float]] = Field(None, description="The optimal range for the nutrient.")
    recommendation: Optional[str] = Field(None, description="Specific recommendation for addressing the deficiency.")

class TissueTestAnalysisResponse(BaseModel):
    analysis_id: UUID4 = Field(..., description="Unique ID for this analysis.")
    farm_id: UUID4 = Field(..., description="ID of the farm.")
    field_id: UUID4 = Field(..., description="ID of the field.")
    crop_type: str = Field(..., description="Type of crop.")
    growth_stage: str = Field(..., description="Growth stage of the crop.")
    test_date: datetime = Field(..., description="Date the tissue test was performed.")
    deficiencies: List[NutrientDeficiency] = Field(..., description="List of detected nutrient deficiencies.")
    overall_status: str = Field(..., description="Overall status of the tissue test (e.g., 'Healthy', 'Deficiencies Detected').")
    recommendations_summary: Optional[str] = Field(None, description="A summary of all recommendations.")
    raw_results: List[TissueTestResult] = Field(..., description="The raw tissue test results submitted.")