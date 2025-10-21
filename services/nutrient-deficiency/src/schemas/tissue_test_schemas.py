from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import date
from uuid import UUID

class NutrientDeficiencyScore(BaseModel):
    nutrient: str
    deviation_percent: float
    severity_score: float  # e.g., 0-100, 100 is optimal
    category: str  # e.g., 'optimal', 'mild deficiency', 'severe toxicity'

class TissueTestInput(BaseModel):
    field_id: UUID = Field(..., description="UUID of the field where the tissue sample was taken")
    crop_type: str = Field(..., description="Type of crop (e.g., 'Corn', 'Soybean')")
    growth_stage: str = Field(..., description="Growth stage of the crop (e.g., 'V6', 'R1')")
    test_date: date = Field(..., description="Date the tissue test was performed")
    lab_id: Optional[str] = Field(None, description="Identifier from the testing laboratory")
    nutrient_levels: Dict[str, float] = Field(..., description="Dictionary of nutrient levels (e.g., {'N': 3.5, 'P': 0.3})")

class TissueTestResult(TissueTestInput):
    id: UUID = Field(..., description="UUID of the tissue test result")
    analysis_id: UUID = Field(..., description="UUID of the analysis result")
    deficiencies_identified: List[str] = Field(default_factory=list, description="List of nutrients identified as deficient")
    toxicities_identified: List[str] = Field(default_factory=list, description="List of nutrients identified as toxic")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the deficiency/toxicity identification")
    recommendations: List[str] = Field(default_factory=list, description="List of recommendations based on the analysis")
    nutrient_scores: Dict[str, NutrientDeficiencyScore] = Field(default_factory=dict, description="Detailed scores for each nutrient")
    overall_health_score: float = Field(..., ge=0.0, le=100.0, description="Overall nutrient health score for the crop/field")
