from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID, uuid4

class ImageQuality(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0, description="Overall image quality score")
    issues: List[str] = Field(default_factory=list, description="List of identified image quality issues")

class DeficiencySymptom(BaseModel):
    nutrient: str = Field(..., description="Nutrient potentially deficient")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for this deficiency")
    severity: str = Field(..., description="Severity of the deficiency (e.g., mild, moderate, severe)")
    affected_area_percent: Optional[float] = Field(None, ge=0.0, le=100.0, description="Percentage of plant affected")
    symptoms_detected: List[str] = Field(default_factory=list, description="List of visual symptoms detected")

class Recommendation(BaseModel):
    action: str = Field(..., description="Recommended action to address the deficiency")
    priority: str = Field(..., description="Priority of the recommendation (e.g., low, medium, high)")
    timing: str = Field(..., description="Recommended timing for the action")
    details: Optional[str] = Field(None, description="Additional details for the recommendation")

class DeficiencyAnalysisResponse(BaseModel):
    analysis_id: UUID = Field(default_factory=uuid4, description="Unique identifier for this analysis")
    image_quality: ImageQuality
    deficiencies: List[DeficiencySymptom]
    recommendations: List[Recommendation]
    metadata: dict = Field(default_factory=dict, description="Additional metadata about the analysis")
