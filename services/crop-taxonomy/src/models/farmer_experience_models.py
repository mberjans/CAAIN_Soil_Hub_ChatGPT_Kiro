"""
Farmer Experience Data Models

Data models for farmer experience collection, validation, and aggregation
in crop variety recommendations.
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel, Field, validator
from enum import Enum


class ExperienceConfidenceLevel(str, Enum):
    """Confidence levels for farmer experience data."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ValidationStatus(str, Enum):
    """Validation status for farmer experience entries."""
    PENDING = "pending"
    VALIDATED = "validated"
    INVALID = "invalid"
    REQUIRES_REVIEW = "requires_review"


class BiasType(str, Enum):
    """Types of bias that can be detected in farmer experience data."""
    OPTIMISM_BIAS = "optimism_bias"
    RECENCY_BIAS = "recency_bias"
    EXPERIENCE_BIAS = "experience_bias"
    REGIONAL_BIAS = "regional_bias"
    CONFIRMATION_BIAS = "confirmation_bias"


class FarmerFeedbackSurvey(BaseModel):
    """Structured survey for farmer feedback collection."""
    
    # Performance ratings (1-5 scale)
    yield_rating: float = Field(..., ge=1.0, le=5.0, description="Yield performance rating")
    disease_resistance_rating: float = Field(..., ge=1.0, le=5.0, description="Disease resistance rating")
    management_ease_rating: Optional[float] = Field(None, ge=1.0, le=5.0, description="Management ease rating")
    overall_satisfaction: float = Field(..., ge=1.0, le=5.0, description="Overall satisfaction rating")
    market_performance_rating: Optional[float] = Field(None, ge=1.0, le=5.0, description="Market performance rating")
    
    # Qualitative feedback
    comments: Optional[str] = Field(None, max_length=1000, description="General comments about the variety")
    additional_notes: Optional[str] = Field(None, max_length=1000, description="Additional notes or observations")
    
    # Context information
    growing_season: Optional[str] = Field(None, description="Growing season (e.g., '2024')")
    field_conditions: Optional[str] = Field(None, description="Field conditions during growing season")
    
    @validator('yield_rating', 'disease_resistance_rating', 'overall_satisfaction')
    def validate_required_ratings(cls, v):
        """Validate that required ratings are provided."""
        if v is None:
            raise ValueError("Required rating cannot be None")
        return v


class FieldPerformanceData(BaseModel):
    """Field performance data for validation."""
    
    # Yield data
    actual_yield: Optional[float] = Field(None, ge=0.0, description="Actual yield achieved (bushels/acre)")
    expected_yield: Optional[float] = Field(None, ge=0.0, description="Expected yield based on variety characteristics")
    yield_variance: Optional[float] = Field(None, description="Yield variance from expected")
    
    # Field conditions
    soil_type: Optional[str] = Field(None, description="Soil type")
    planting_date: Optional[date] = Field(None, description="Planting date")
    harvest_date: Optional[date] = Field(None, description="Harvest date")
    field_size_acres: Optional[float] = Field(None, ge=0.0, description="Field size in acres")
    
    # Management practices
    irrigation_used: Optional[bool] = Field(None, description="Whether irrigation was used")
    fertilizer_applications: Optional[int] = Field(None, ge=0, description="Number of fertilizer applications")
    pesticide_applications: Optional[int] = Field(None, ge=0, description="Number of pesticide applications")
    
    # Weather conditions
    weather_conditions: Optional[str] = Field(None, description="Weather conditions during growing season")
    drought_stress: Optional[bool] = Field(None, description="Whether drought stress occurred")
    disease_pressure: Optional[str] = Field(None, description="Disease pressure level")
    
    # Quality metrics
    grain_quality: Optional[str] = Field(None, description="Grain quality assessment")
    test_weight: Optional[float] = Field(None, ge=0.0, description="Test weight")
    protein_content: Optional[float] = Field(None, ge=0.0, le=100.0, description="Protein content percentage")


class FarmerProfile(BaseModel):
    """Farmer profile for bias correction and personalization."""
    
    farmer_id: UUID = Field(..., description="Unique farmer identifier")
    
    # Basic information
    farm_size_acres: Optional[float] = Field(None, ge=0.0, description="Total farm size in acres")
    farming_experience_years: Optional[int] = Field(None, ge=0, description="Years of farming experience")
    primary_crops: Optional[List[str]] = Field(None, description="Primary crops grown")
    
    # Location and climate
    region: Optional[str] = Field(None, description="Farming region")
    climate_zone: Optional[str] = Field(None, description="Climate zone")
    
    # Management style
    management_style: Optional[str] = Field(None, description="Management style (conventional, organic, etc.)")
    technology_adoption: Optional[str] = Field(None, description="Technology adoption level")
    risk_tolerance: Optional[str] = Field(None, description="Risk tolerance level")
    
    # Experience history
    total_varieties_tested: Optional[int] = Field(None, ge=0, description="Total number of varieties tested")
    average_rating_tendency: Optional[float] = Field(None, ge=1.0, le=5.0, description="Average rating tendency")
    feedback_frequency: Optional[str] = Field(None, description="Frequency of providing feedback")
    
    # Bias indicators
    optimism_bias_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Optimism bias score")
    experience_bias_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Experience bias score")
    
    # Profile metadata
    profile_created: datetime = Field(default_factory=datetime.utcnow, description="Profile creation date")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last profile update")
    profile_completeness: float = Field(default=0.0, ge=0.0, le=1.0, description="Profile completeness score")


class FarmerExperienceEntry(BaseModel):
    """Individual farmer experience entry."""
    
    id: UUID = Field(..., description="Unique entry identifier")
    farmer_id: UUID = Field(..., description="Farmer identifier")
    variety_id: UUID = Field(..., description="Variety identifier")
    
    # Survey data
    survey_data: FarmerFeedbackSurvey = Field(..., description="Structured survey responses")
    field_performance: Optional[FieldPerformanceData] = Field(None, description="Field performance data")
    
    # Validation and quality
    collection_date: datetime = Field(default_factory=datetime.utcnow, description="Data collection date")
    validation_status: ValidationStatus = Field(default=ValidationStatus.PENDING, description="Validation status")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score")
    data_quality_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Data quality score")
    
    # Metadata
    collection_method: Optional[str] = Field(None, description="Data collection method")
    validation_notes: Optional[str] = Field(None, description="Validation notes")
    requires_review: bool = Field(default=False, description="Whether entry requires manual review")


class PerformanceValidationResult(BaseModel):
    """Result of performance data validation."""
    
    total_entries: int = Field(..., ge=0, description="Total number of entries processed")
    validated_entries: int = Field(..., ge=0, description="Number of validated entries")
    confidence_scores: List[float] = Field(default_factory=list, description="Individual confidence scores")
    validation_errors: List[str] = Field(default_factory=list, description="Validation errors")
    
    # Statistical analysis
    statistical_analysis: Dict[str, Any] = Field(default_factory=dict, description="Statistical analysis results")
    trial_data_comparison: Dict[str, Any] = Field(default_factory=dict, description="Comparison with trial data")
    
    # Overall assessment
    overall_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall validation confidence")
    validation_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Validation timestamp")


class BiasCorrectionResult(BaseModel):
    """Result of bias correction analysis."""
    
    correction_applied: bool = Field(default=False, description="Whether bias correction was applied")
    corrected_entries: List[FarmerExperienceEntry] = Field(default_factory=list, description="Corrected entries")
    details: Dict[str, Any] = Field(default_factory=dict, description="Correction details")
    
    # Bias detection results
    biases_detected: List[BiasType] = Field(default_factory=list, description="Types of bias detected")
    correction_factors: Dict[str, float] = Field(default_factory=dict, description="Applied correction factors")
    correction_method: Optional[str] = Field(None, description="Method used for correction")
    
    # Quality assessment
    correction_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence in correction")
    impact_assessment: Dict[str, Any] = Field(default_factory=dict, description="Impact of correction")


class ExperienceAggregationResult(BaseModel):
    """Result of farmer experience data aggregation."""
    
    variety_id: UUID = Field(..., description="Variety identifier")
    aggregated_data: Dict[str, Any] = Field(default_factory=dict, description="Aggregated performance data")
    confidence_level: ExperienceConfidenceLevel = Field(..., description="Confidence level")
    
    # Sample information
    sample_size: int = Field(..., ge=0, description="Number of samples aggregated")
    bias_correction_applied: bool = Field(default=False, description="Whether bias correction was applied")
    bias_correction_details: Optional[Dict[str, Any]] = Field(None, description="Bias correction details")
    
    # Statistical significance
    statistical_significance: Dict[str, Any] = Field(default_factory=dict, description="Statistical significance")
    aggregation_errors: List[str] = Field(default_factory=list, description="Aggregation errors")
    
    # Metadata
    aggregation_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Aggregation timestamp")
    aggregation_method: str = Field(default="weighted_average", description="Method used for aggregation")


class FarmerExperienceInsights(BaseModel):
    """Insights derived from farmer experience data."""
    
    variety_id: UUID = Field(..., description="Variety identifier")
    
    # Key insights
    top_strengths: List[str] = Field(default_factory=list, description="Top variety strengths")
    top_weaknesses: List[str] = Field(default_factory=list, description="Top variety weaknesses")
    farmer_recommendations: List[str] = Field(default_factory=list, description="Farmer recommendations")
    
    # Performance insights
    yield_consistency: Optional[str] = Field(None, description="Yield consistency assessment")
    disease_performance: Optional[str] = Field(None, description="Disease performance assessment")
    management_requirements: Optional[str] = Field(None, description="Management requirements")
    
    # Market insights
    market_performance: Optional[str] = Field(None, description="Market performance assessment")
    profitability_assessment: Optional[str] = Field(None, description="Profitability assessment")
    
    # Regional insights
    regional_performance: Dict[str, Any] = Field(default_factory=dict, description="Regional performance data")
    climate_adaptation: Optional[str] = Field(None, description="Climate adaptation assessment")
    
    # Confidence and quality
    insight_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence in insights")
    data_quality_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Data quality score")
    
    # Metadata
    insights_generated: datetime = Field(default_factory=datetime.utcnow, description="Insights generation timestamp")
    sample_size: int = Field(default=0, ge=0, description="Sample size used for insights")


class FarmerExperienceRequest(BaseModel):
    """Request for farmer experience data collection."""
    
    farmer_id: UUID = Field(..., description="Farmer identifier")
    variety_id: UUID = Field(..., description="Variety identifier")
    survey_data: FarmerFeedbackSurvey = Field(..., description="Survey data")
    field_performance: Optional[FieldPerformanceData] = Field(None, description="Field performance data")
    
    # Request metadata
    request_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Request timestamp")
    collection_context: Optional[str] = Field(None, description="Collection context")
    validation_required: bool = Field(default=True, description="Whether validation is required")


class FarmerExperienceResponse(BaseModel):
    """Response for farmer experience data collection."""
    
    success: bool = Field(..., description="Whether request was successful")
    experience_entry_id: Optional[UUID] = Field(None, description="Created experience entry ID")
    validation_status: ValidationStatus = Field(..., description="Validation status")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score")
    
    # Response details
    message: Optional[str] = Field(None, description="Response message")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    
    # Next steps
    requires_additional_data: bool = Field(default=False, description="Whether additional data is required")
    follow_up_actions: List[str] = Field(default_factory=list, description="Recommended follow-up actions")
    
    # Response metadata
    response_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    processing_time_ms: float = Field(default=0.0, ge=0.0, description="Processing time in milliseconds")


class FarmerExperienceIntegrationRequest(BaseModel):
    """Request for integrating farmer experience with recommendations."""
    
    variety_recommendations: List[Dict[str, Any]] = Field(..., description="Variety recommendations to enhance")
    experience_data: Dict[str, ExperienceAggregationResult] = Field(..., description="Experience data by variety")
    
    # Integration options
    apply_bias_correction: bool = Field(default=True, description="Whether to apply bias correction")
    confidence_threshold: float = Field(default=0.6, ge=0.0, le=1.0, description="Minimum confidence threshold")
    include_insights: bool = Field(default=True, description="Whether to include farmer insights")
    
    # Request metadata
    request_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Request timestamp")
    integration_context: Optional[str] = Field(None, description="Integration context")


class FarmerExperienceIntegrationResponse(BaseModel):
    """Response for farmer experience integration."""
    
    success: bool = Field(..., description="Whether integration was successful")
    enhanced_recommendations: List[Dict[str, Any]] = Field(default_factory=list, description="Enhanced recommendations")
    
    # Integration results
    varieties_enhanced: int = Field(default=0, ge=0, description="Number of varieties enhanced")
    experience_data_used: int = Field(default=0, ge=0, description="Number of experience datasets used")
    bias_corrections_applied: int = Field(default=0, ge=0, description="Number of bias corrections applied")
    
    # Quality metrics
    average_confidence_improvement: float = Field(default=0.0, description="Average confidence improvement")
    data_quality_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall data quality score")
    
    # Response details
    message: Optional[str] = Field(None, description="Response message")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    
    # Response metadata
    response_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    processing_time_ms: float = Field(default=0.0, ge=0.0, description="Processing time in milliseconds")