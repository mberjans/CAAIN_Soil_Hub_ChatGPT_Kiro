from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

class SymptomBase(BaseModel):
    nutrient: str = Field(..., description="The nutrient associated with the deficiency (e.g., Nitrogen, Potassium).")
    crop_type: str = Field(..., description="The type of crop this symptom applies to (e.g., Corn, Soybean).")
    symptom_name: str = Field(..., description="A unique name for the symptom (e.g., Nitrogen Deficiency in Corn).")
    description: str = Field(..., description="A detailed description of the symptom.")
    affected_parts: List[str] = Field(..., description="List of plant parts typically affected (e.g., Older leaves, Younger leaves).")
    visual_characteristics: List[str] = Field(..., description="List of visual characteristics of the symptom (e.g., Yellowing, Purpling, Stunted growth).")
    severity_levels: Dict[str, str] = Field(..., description="Dictionary describing severity levels (e.g., {'mild': 'slight yellowing'}).")
    growth_stages: List[str] = Field(..., description="List of growth stages when the symptom typically appears.")
    confidence_score_threshold: float = Field(0.7, ge=0.0, le=1.0, description="Minimum match score for this symptom to be considered a match.")

class SymptomCreate(SymptomBase):
    pass

class SymptomUpdate(SymptomBase):
    nutrient: Optional[str] = None
    crop_type: Optional[str] = None
    symptom_name: Optional[str] = None
    description: Optional[str] = None
    affected_parts: Optional[List[str]] = None
    visual_characteristics: Optional[List[str]] = None
    severity_levels: Optional[Dict[str, str]] = None
    growth_stages: Optional[List[str]] = None
    confidence_score_threshold: Optional[float] = None

class SymptomResponse(SymptomBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class SymptomMatchRequest(BaseModel):
    detected_characteristics: List[str] = Field(..., description="List of visual characteristics detected from an image.")
    crop_type: str = Field(..., description="The type of crop (e.g., Corn, Soybean).")

class SymptomMatchResponse(BaseModel):
    nutrient: str
    symptom_name: str
    description: str
    affected_parts: List[str]
    visual_characteristics: List[str]
    severity_levels: Dict[str, str]
    match_score: float
    confidence_threshold: float

class SymptomMatchResult(BaseModel):
    potential_deficiencies: List[SymptomMatchResponse]
