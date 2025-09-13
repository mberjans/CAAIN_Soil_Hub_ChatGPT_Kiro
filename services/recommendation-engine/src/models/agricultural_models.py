"""
Agricultural Data Models

Pydantic models for agricultural data and recommendations.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import date, datetime
from enum import Enum


class SoilTestData(BaseModel):
    """Soil test data with agricultural validation."""
    
    ph: float = Field(..., ge=3.0, le=10.0, description="Soil pH (3.0-10.0)")
    organic_matter_percent: float = Field(..., ge=0.0, le=15.0, description="Organic matter %")
    phosphorus_ppm: float = Field(..., ge=0.0, le=200.0, description="Phosphorus (Mehlich-3)")
    potassium_ppm: float = Field(..., ge=0.0, le=800.0, description="Potassium (Mehlich-3)")
    nitrogen_ppm: Optional[float] = Field(None, ge=0.0, le=100.0, description="Nitrate-N (ppm)")
    cec_meq_per_100g: Optional[float] = Field(None, ge=0.0, le=50.0, description="Cation Exchange Capacity")
    soil_texture: Optional[str] = Field(None, description="Soil texture class")
    drainage_class: Optional[str] = Field(None, description="Soil drainage classification")
    test_date: date = Field(..., description="Date of soil test")
    lab_name: Optional[str] = Field(None, description="Testing laboratory")
    
    @validator('test_date')
    def validate_test_date(cls, v):
        """Ensure soil test is not too old."""
        from datetime import date, timedelta
        max_age = date.today() - timedelta(days=3*365)  # 3 years
        if v < max_age:
            raise ValueError(f"Soil test date {v} is older than 3 years")
        return v


class LocationData(BaseModel):
    """Geographic location data."""
    
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    address: Optional[str] = Field(None, description="Human-readable address")
    climate_zone: Optional[str] = Field(None, description="USDA Hardiness Zone")
    state: Optional[str] = Field(None, description="State/Province")
    county: Optional[str] = Field(None, description="County/Region")


class CropData(BaseModel):
    """Crop information and requirements."""
    
    crop_name: str = Field(..., description="Common crop name")
    variety: Optional[str] = Field(None, description="Specific variety name")
    planting_date: Optional[date] = Field(None, description="Planned/actual planting date")
    harvest_date: Optional[date] = Field(None, description="Expected/actual harvest date")
    yield_goal: Optional[float] = Field(None, ge=0, description="Target yield (bu/acre or tons/acre)")
    previous_crop: Optional[str] = Field(None, description="Previous year's crop")
    rotation_history: Optional[List[str]] = Field(None, description="Crop rotation history")


class FarmProfile(BaseModel):
    """Farm profile and characteristics."""
    
    farm_id: str = Field(..., description="Unique farm identifier")
    farm_size_acres: float = Field(..., gt=0, description="Total farm size in acres")
    primary_crops: List[str] = Field(..., description="Primary crops grown")
    equipment_available: Optional[List[str]] = Field(None, description="Available equipment")
    irrigation_available: bool = Field(default=False, description="Irrigation system available")
    organic_certified: bool = Field(default=False, description="Organic certification status")
    conservation_practices: Optional[List[str]] = Field(None, description="Current conservation practices")


class ConfidenceFactors(BaseModel):
    """Factors affecting recommendation confidence."""
    
    soil_data_quality: float = Field(..., ge=0.0, le=1.0, description="Quality of soil data")
    regional_data_availability: float = Field(..., ge=0.0, le=1.0, description="Regional data coverage")
    seasonal_appropriateness: float = Field(..., ge=0.0, le=1.0, description="Seasonal timing relevance")
    expert_validation: float = Field(..., ge=0.0, le=1.0, description="Expert validation level")


class RecommendationRequest(BaseModel):
    """Request for agricultural recommendations."""
    
    request_id: str = Field(..., description="Unique request identifier")
    question_type: str = Field(..., description="Type of agricultural question")
    location: LocationData = Field(..., description="Farm location")
    soil_data: Optional[SoilTestData] = Field(None, description="Soil test results")
    crop_data: Optional[CropData] = Field(None, description="Crop information")
    farm_profile: Optional[FarmProfile] = Field(None, description="Farm profile")
    additional_context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    user_preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences")


class RecommendationItem(BaseModel):
    """Individual recommendation item."""
    
    recommendation_type: str = Field(..., description="Type of recommendation")
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="Detailed recommendation")
    priority: int = Field(..., ge=1, le=5, description="Priority level (1=highest)")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in recommendation")
    implementation_steps: List[str] = Field(..., description="Steps to implement")
    expected_outcomes: List[str] = Field(..., description="Expected results")
    cost_estimate: Optional[float] = Field(None, description="Estimated cost")
    roi_estimate: Optional[float] = Field(None, description="Expected ROI percentage")
    timing: Optional[str] = Field(None, description="Recommended timing")
    agricultural_sources: List[str] = Field(..., description="Supporting agricultural sources")


class RecommendationResponse(BaseModel):
    """Response containing agricultural recommendations."""
    
    request_id: str = Field(..., description="Original request identifier")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    question_type: str = Field(..., description="Type of question answered")
    overall_confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score")
    confidence_factors: ConfidenceFactors = Field(..., description="Confidence breakdown")
    recommendations: List[RecommendationItem] = Field(..., description="List of recommendations")
    warnings: Optional[List[str]] = Field(None, description="Important warnings or limitations")
    next_steps: Optional[List[str]] = Field(None, description="Suggested next actions")
    follow_up_questions: Optional[List[str]] = Field(None, description="Suggested follow-up questions")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }