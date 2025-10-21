from pydantic import BaseModel, Field
from typing import Optional, List
from ..models.image_models import DeficiencyAnalysis, ImageQualityIssue, Severity, RecommendationAction, DeficiencyDetail, ImageQuality

class ImageAnalysisRequest(BaseModel):
    crop_type: str = Field(..., description="Type of crop being analyzed (e.g., 'corn', 'soybean')")
    growth_stage: Optional[str] = Field(None, description="Growth stage of the crop (e.g., 'V6', 'Flowering')")
    field_conditions: Optional[dict] = Field(None, description="Additional field conditions (e.g., soil type, recent weather)")

class ImageAnalysisResponse(BaseModel):
    analysis_id: str = Field(..., description="Unique ID for this analysis")
    crop_type: str = Field(..., description="Type of crop analyzed")
    growth_stage: Optional[str] = Field(None, description="Growth stage of the crop at the time of photo")
    image_quality: ImageQuality = Field(..., description="Assessment of the input image quality")
    deficiencies: List[DeficiencyDetail] = Field(default_factory=list, description="List of detected nutrient deficiencies")
    recommendations: List[RecommendationAction] = Field(default_factory=list, description="List of recommended actions")
    overall_confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence of the analysis (0-1)")
    message: str = Field(default="", description="Overall message or summary of the analysis")
