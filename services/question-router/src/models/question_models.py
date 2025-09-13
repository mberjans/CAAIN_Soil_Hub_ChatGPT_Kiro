"""
Question Router Pydantic Models

Models for handling farmer questions and routing decisions.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class QuestionType(str, Enum):
    """The 20 key farmer question types."""
    CROP_SELECTION = "crop_selection"
    SOIL_FERTILITY = "soil_fertility"
    CROP_ROTATION = "crop_rotation"
    NUTRIENT_DEFICIENCY = "nutrient_deficiency"
    FERTILIZER_TYPE = "fertilizer_type"
    FERTILIZER_APPLICATION = "fertilizer_application"
    FERTILIZER_TIMING = "fertilizer_timing"
    ENVIRONMENTAL_IMPACT = "environmental_impact"
    COVER_CROPS = "cover_crops"
    SOIL_PH = "soil_ph"
    MICRONUTRIENTS = "micronutrients"
    PRECISION_AGRICULTURE = "precision_agriculture"
    DROUGHT_MANAGEMENT = "drought_management"
    DEFICIENCY_DETECTION = "deficiency_detection"
    TILLAGE_PRACTICES = "tillage_practices"
    COST_EFFECTIVE_STRATEGY = "cost_effective_strategy"
    WEATHER_IMPACT = "weather_impact"
    TESTING_INTEGRATION = "testing_integration"
    SUSTAINABLE_YIELD = "sustainable_yield"
    GOVERNMENT_PROGRAMS = "government_programs"


class QuestionRequest(BaseModel):
    """Request model for farmer questions."""
    
    question_text: str = Field(..., description="The farmer's question in natural language")
    user_id: Optional[str] = Field(None, description="User identifier")
    farm_id: Optional[str] = Field(None, description="Farm identifier")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")
    location: Optional[Dict[str, float]] = Field(None, description="GPS coordinates")
    
    @validator('question_text')
    def validate_question_text(cls, v):
        if len(v.strip()) < 10:
            raise ValueError("Question must be at least 10 characters long")
        if len(v) > 1000:
            raise ValueError("Question must be less than 1000 characters")
        return v.strip()


class ClassificationResult(BaseModel):
    """Result of question classification."""
    
    question_type: QuestionType = Field(..., description="Classified question type")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Classification confidence")
    alternative_types: List[QuestionType] = Field(default_factory=list, description="Alternative classifications")
    reasoning: str = Field(..., description="Explanation of classification decision")


class RoutingDecision(BaseModel):
    """Routing decision for processing the question."""
    
    primary_service: str = Field(..., description="Primary service to handle the question")
    secondary_services: List[str] = Field(default_factory=list, description="Additional services needed")
    processing_priority: int = Field(default=1, ge=1, le=5, description="Processing priority (1=highest)")
    estimated_processing_time: int = Field(..., description="Estimated processing time in seconds")


class QuestionResponse(BaseModel):
    """Response model for question routing."""
    
    request_id: str = Field(..., description="Unique request identifier")
    classification: ClassificationResult = Field(..., description="Question classification result")
    routing: RoutingDecision = Field(..., description="Routing decision")
    status: str = Field(default="routed", description="Processing status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }