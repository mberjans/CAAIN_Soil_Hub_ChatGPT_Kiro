"""
Data models for Expert Validation System

This module contains Pydantic models for the agricultural expert validation
and field testing system for drought management recommendations.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field, validator
from decimal import Decimal


class ValidationStatus(str, Enum):
    """Status of expert validation process."""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_REVISION = "requires_revision"
    EXPERT_REVIEW_REQUIRED = "expert_review_required"


class ExpertType(str, Enum):
    """Types of agricultural experts."""
    DROUGHT_SPECIALIST = "drought_specialist"
    EXTENSION_AGENT = "extension_agent"
    CONSERVATION_PROFESSIONAL = "conservation_professional"
    IRRIGATION_SPECIALIST = "irrigation_specialist"
    SOIL_SCIENTIST = "soil_scientist"
    CROP_SPECIALIST = "crop_specialist"


class ValidationCriteria(str, Enum):
    """Validation criteria for drought management recommendations."""
    AGRICULTURAL_SOUNDNESS = "agricultural_soundness"
    REGIONAL_APPLICABILITY = "regional_applicability"
    ECONOMIC_FEASIBILITY = "economic_feasibility"
    ENVIRONMENTAL_IMPACT = "environmental_impact"
    PRACTICALITY = "practicality"
    SAFETY = "safety"
    EFFECTIVENESS = "effectiveness"


class ExpertProfile(BaseModel):
    """Profile of an agricultural expert."""
    expert_id: UUID
    name: str = Field(..., min_length=1, max_length=200)
    credentials: str = Field(..., min_length=1)
    expertise_areas: List[ExpertType] = Field(..., min_items=1)
    regions: List[str] = Field(..., min_items=1)
    years_experience: int = Field(..., ge=0, le=50)
    certifications: List[str] = Field(default_factory=list)
    contact_info: Dict[str, str] = Field(..., min_items=1)
    availability_status: str = Field(default="available")
    review_count: int = Field(default=0, ge=0)
    approval_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    average_review_time_hours: float = Field(default=0.0, ge=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)

    @validator('contact_info')
    def validate_contact_info(cls, v):
        """Validate contact information contains required fields."""
        required_fields = ['email']
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Contact info must include {field}")
        return v

    @validator('regions')
    def validate_regions(cls, v):
        """Validate region codes are valid US state abbreviations."""
        valid_states = {
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
            'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
            'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
            'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
        }
        for region in v:
            if region not in valid_states:
                raise ValueError(f"Invalid region code: {region}")
        return v


class ValidationRequest(BaseModel):
    """Request for expert validation of drought management recommendations."""
    validation_id: UUID
    recommendation_id: UUID
    farm_location: Dict[str, Any]
    field_conditions: Dict[str, Any]
    drought_assessment: Dict[str, Any]
    conservation_recommendations: List[Dict[str, Any]]
    water_savings_estimates: List[Dict[str, Any]]
    validation_criteria: List[ValidationCriteria]
    priority_level: str = Field(..., regex="^(low|normal|high|critical)$")
    requested_expert_types: List[ExpertType]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    deadline: datetime

    @validator('deadline')
    def validate_deadline(cls, v, values):
        """Validate deadline is in the future."""
        if 'created_at' in values and v <= values['created_at']:
            raise ValueError("Deadline must be in the future")
        return v


class ExpertReview(BaseModel):
    """Expert review of drought management recommendations."""
    review_id: UUID
    validation_id: UUID
    expert_id: UUID
    expert_type: ExpertType
    review_status: ValidationStatus
    criteria_scores: Dict[ValidationCriteria, float] = Field(..., min_items=1)
    overall_score: float = Field(..., ge=0.0, le=1.0)
    comments: str = Field(..., min_length=10)
    recommendations: List[str] = Field(default_factory=list)
    concerns: List[str] = Field(default_factory=list)
    approval_status: bool
    review_time_hours: float = Field(..., ge=0.0, le=168.0)  # Max 1 week
    submitted_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('criteria_scores')
    def validate_criteria_scores(cls, v):
        """Validate criteria scores are within valid range."""
        for score in v.values():
            if not (0.0 <= score <= 1.0):
                raise ValueError("Criteria scores must be between 0.0 and 1.0")
        return v

    @validator('comments')
    def validate_comments(cls, v):
        """Validate comments provide meaningful feedback."""
        if len(v.strip()) < 10:
            raise ValueError("Comments must provide meaningful feedback (minimum 10 characters)")
        return v


class FieldTestResult(BaseModel):
    """Results from field testing of drought management practices."""
    test_id: UUID
    farm_id: UUID
    field_id: UUID
    practice_implemented: str = Field(..., min_length=1, max_length=200)
    implementation_date: datetime
    baseline_conditions: Dict[str, Any] = Field(..., min_items=1)
    monitoring_data: Dict[str, Any] = Field(default_factory=dict)
    outcome_metrics: Dict[str, float] = Field(default_factory=dict)
    farmer_feedback: Dict[str, Any] = Field(default_factory=dict)
    expert_observations: List[str] = Field(default_factory=list)
    effectiveness_score: float = Field(default=0.0, ge=0.0, le=1.0)
    farmer_satisfaction_score: float = Field(default=0.0, ge=0.0, le=1.0)
    test_duration_days: int = Field(..., ge=1, le=365)
    completed_at: Optional[datetime] = None

    @validator('baseline_conditions')
    def validate_baseline_conditions(cls, v):
        """Validate baseline conditions include required fields."""
        required_fields = ['soil_moisture', 'soil_type', 'crop_type']
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Baseline conditions must include {field}")
        return v


class ValidationMetrics(BaseModel):
    """Metrics for validation system performance."""
    total_validations: int = Field(default=0, ge=0)
    expert_approval_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    recommendation_accuracy: float = Field(default=0.0, ge=0.0, le=1.0)
    farmer_satisfaction: float = Field(default=0.0, ge=0.0, le=1.0)
    average_review_time_hours: float = Field(default=0.0, ge=0.0)
    field_test_success_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    expert_panel_size: int = Field(default=0, ge=0)
    active_field_tests: int = Field(default=0, ge=0)
    validation_period_days: int = Field(default=30, ge=1, le=365)


class ExpertAssignmentRequest(BaseModel):
    """Request to assign experts to validation."""
    validation_id: UUID
    expert_types: List[ExpertType] = Field(..., min_items=1)
    priority_level: str = Field(..., regex="^(low|normal|high|critical)$")
    deadline_hours: int = Field(..., ge=1, le=168)


class FieldTestRequest(BaseModel):
    """Request to start field test."""
    farm_id: UUID
    field_id: UUID
    practice_implemented: str = Field(..., min_length=1, max_length=200)
    baseline_conditions: Dict[str, Any] = Field(..., min_items=1)
    test_duration_days: int = Field(default=90, ge=1, le=365)
    monitoring_frequency_days: int = Field(default=7, ge=1, le=30)


class FieldTestUpdateRequest(BaseModel):
    """Request to update field test monitoring data."""
    test_id: UUID
    monitoring_data: Dict[str, Any] = Field(..., min_items=1)
    expert_observations: List[str] = Field(default_factory=list)


class FieldTestCompletionRequest(BaseModel):
    """Request to complete field test."""
    test_id: UUID
    outcome_metrics: Dict[str, float] = Field(..., min_items=1)
    farmer_feedback: Dict[str, Any] = Field(..., min_items=1)
    effectiveness_score: float = Field(..., ge=0.0, le=1.0)
    farmer_satisfaction_score: float = Field(..., ge=0.0, le=1.0)

    @validator('outcome_metrics')
    def validate_outcome_metrics(cls, v):
        """Validate outcome metrics include required fields."""
        required_fields = ['water_savings_percent', 'yield_impact_percent', 'cost_benefit_ratio']
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Outcome metrics must include {field}")
        return v

    @validator('farmer_feedback')
    def validate_farmer_feedback(cls, v):
        """Validate farmer feedback includes required fields."""
        required_fields = ['satisfaction_rating', 'implementation_difficulty', 'recommendation']
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Farmer feedback must include {field}")
        return v


class ValidationReport(BaseModel):
    """Comprehensive validation report."""
    validation_id: UUID
    recommendation_id: UUID
    validation_summary: Dict[str, Any]
    expert_reviews: List[Dict[str, Any]]
    overall_assessment: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    water_savings_estimates: List[Dict[str, Any]]
    field_test_results: Optional[List[Dict[str, Any]]] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class ExpertPanelStatus(BaseModel):
    """Status of expert panel."""
    total_experts: int = Field(..., ge=0)
    available_experts: int = Field(..., ge=0)
    assigned_experts: int = Field(..., ge=0)
    expert_types_distribution: Dict[str, int] = Field(..., min_items=1)
    average_approval_rate: float = Field(..., ge=0.0, le=1.0)
    average_experience_years: float = Field(..., ge=0.0)


class ValidationStatusResponse(BaseModel):
    """Response for validation status query."""
    validation_id: UUID
    status: ValidationStatus
    progress_percentage: float = Field(..., ge=0.0, le=100.0)
    expert_reviews: int = Field(..., ge=0)
    total_experts_assigned: int = Field(..., ge=0)
    deadline: datetime
    overall_approval: Optional[bool] = None
    estimated_completion: Optional[datetime] = None


class ExpertReviewSubmission(BaseModel):
    """Submission of expert review."""
    validation_id: UUID
    expert_id: UUID
    criteria_scores: Dict[ValidationCriteria, float] = Field(..., min_items=1)
    overall_score: float = Field(..., ge=0.0, le=1.0)
    comments: str = Field(..., min_length=10)
    recommendations: List[str] = Field(default_factory=list)
    concerns: List[str] = Field(default_factory=list)
    approval_status: bool
    review_time_hours: float = Field(..., ge=0.0, le=168.0)

    @validator('criteria_scores')
    def validate_criteria_scores(cls, v):
        """Validate criteria scores are within valid range."""
        for score in v.values():
            if not (0.0 <= score <= 1.0):
                raise ValueError("Criteria scores must be between 0.0 and 1.0")
        return v


class FieldTestMonitoringData(BaseModel):
    """Field test monitoring data."""
    test_id: UUID
    monitoring_date: datetime = Field(default_factory=datetime.utcnow)
    soil_moisture_percent: float = Field(..., ge=0.0, le=100.0)
    crop_health_score: float = Field(..., ge=0.0, le=1.0)
    water_applied_inches: Optional[float] = Field(None, ge=0.0)
    precipitation_inches: Optional[float] = Field(None, ge=0.0)
    temperature_fahrenheit: Optional[float] = Field(None, ge=-50.0, le=150.0)
    humidity_percent: Optional[float] = Field(None, ge=0.0, le=100.0)
    expert_observations: List[str] = Field(default_factory=list)
    photos: List[str] = Field(default_factory=list)  # URLs to photos


class ValidationMetricsResponse(BaseModel):
    """Response for validation metrics query."""
    metrics: ValidationMetrics
    period_start: datetime
    period_end: datetime
    trend_analysis: Dict[str, Any] = Field(default_factory=dict)
    performance_targets: Dict[str, float] = Field(default_factory=dict)
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }