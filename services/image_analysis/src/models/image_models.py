from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class Severity(str, Enum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"

class ImageQualityIssue(str, Enum):
    BLURRY = "blurry"
    POOR_LIGHTING = "poor_lighting"
    OVEREXPOSED = "overexposed"
    UNDEREXPOSED = "underexposed"
    WRONG_ANGLE = "wrong_angle"
    TOO_FAR = "too_far"
    TOO_CLOSE = "too_close"
    OTHER_OBJECTS = "other_objects"
    TOO_SMALL = "too_small"
    INVALID_FORMAT = "invalid_format"

class ImageQuality(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0, description="Overall image quality score (0-1)")
    issues: List[ImageQualityIssue] = Field(default_factory=list, description="List of detected image quality issues")
    feedback: str = Field(default="", description="Human-readable feedback on image quality")

class DeficiencyDetail(BaseModel):
    nutrient: str = Field(..., description="Name of the nutrient (e.g., Nitrogen, Phosphorus)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the detected deficiency (0-1)")
    severity: Severity = Field(..., description="Severity of the deficiency")
    affected_area_percent: Optional[float] = Field(None, ge=0.0, le=100.0, description="Percentage of crop affected by the deficiency")
    symptoms_detected: List[str] = Field(default_factory=list, description="List of specific symptoms identified")
    visual_cues: List[str] = Field(default_factory=list, description="Visual cues from the image supporting the detection")

class RecommendationAction(BaseModel):
    action: str = Field(..., description="Recommended action (e.g., Apply Nitrogen, Adjust pH)")
    priority: str = Field(..., description="Priority of the action (e.g., high, medium, low)")
    timing: str = Field(..., description="Recommended timing for the action (e.g., immediate, within 7 days)")
    details: Optional[str] = Field(None, description="Further details or explanation for the action")

class DeficiencyAnalysis(BaseModel):
    analysis_id: str = Field(..., description="Unique ID for this analysis")
    crop_type: str = Field(..., description="Type of crop analyzed")
    growth_stage: Optional[str] = Field(None, description="Growth stage of the crop at the time of photo")
    image_quality: ImageQuality = Field(..., description="Assessment of the input image quality")
    deficiencies: List[DeficiencyDetail] = Field(default_factory=list, description="List of detected nutrient deficiencies")
    recommendations: List[RecommendationAction] = Field(default_factory=list, description="List of recommended actions")
    overall_confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence of the analysis (0-1)")
    message: str = Field(default="", description="Overall message or summary of the analysis")
