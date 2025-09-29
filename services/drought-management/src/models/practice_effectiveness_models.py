"""
Practice Effectiveness Tracking Data Models

Pydantic models for tracking conservation practice effectiveness,
performance monitoring, and validation data structures.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from uuid import UUID, uuid4
from decimal import Decimal
from enum import Enum

# Enums for type safety
class EffectivenessStatus(str, Enum):
    """Practice effectiveness status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SUSPENDED = "suspended"

class PerformanceMetric(str, Enum):
    """Types of performance metrics."""
    WATER_SAVINGS = "water_savings"
    SOIL_HEALTH = "soil_health"
    COST_EFFECTIVENESS = "cost_effectiveness"
    YIELD_IMPACT = "yield_impact"
    ENVIRONMENTAL_BENEFIT = "environmental_benefit"
    FARMER_SATISFACTION = "farmer_satisfaction"

class ValidationStatus(str, Enum):
    """Validation status for practice effectiveness."""
    PENDING = "pending"
    VALIDATED = "validated"
    INVALID = "invalid"
    NEEDS_REVIEW = "needs_review"

class PracticeImplementation(BaseModel):
    """Model for tracking practice implementation."""
    implementation_id: UUID = Field(default_factory=uuid4, description="Unique implementation identifier")
    practice_id: UUID = Field(..., description="Reference to conservation practice")
    field_id: UUID = Field(..., description="Field where practice is implemented")
    farmer_id: UUID = Field(..., description="Farmer implementing the practice")
    start_date: date = Field(..., description="Implementation start date")
    planned_completion_date: Optional[date] = Field(None, description="Planned completion date")
    actual_completion_date: Optional[date] = Field(None, description="Actual completion date")
    status: EffectivenessStatus = Field(default=EffectivenessStatus.NOT_STARTED, description="Implementation status")
    implementation_notes: Optional[str] = Field(None, description="Implementation notes and observations")
    challenges_encountered: List[str] = Field(default_factory=list, description="Challenges during implementation")
    resources_used: Dict[str, Any] = Field(default_factory=dict, description="Resources utilized")
    cost_actual: Optional[Decimal] = Field(None, description="Actual implementation cost")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PerformanceMeasurement(BaseModel):
    """Model for tracking performance measurements."""
    measurement_id: UUID = Field(default_factory=uuid4, description="Unique measurement identifier")
    implementation_id: UUID = Field(..., description="Reference to practice implementation")
    measurement_date: date = Field(..., description="Date of measurement")
    metric_type: PerformanceMetric = Field(..., description="Type of metric being measured")
    metric_value: Decimal = Field(..., description="Measured value")
    metric_unit: str = Field(..., description="Unit of measurement")
    measurement_method: str = Field(..., description="Method used for measurement")
    measurement_source: str = Field(..., description="Source of measurement (sensor, manual, etc.)")
    confidence_level: float = Field(..., ge=0, le=1, description="Confidence in measurement accuracy")
    notes: Optional[str] = Field(None, description="Additional notes about the measurement")
    baseline_value: Optional[Decimal] = Field(None, description="Baseline value for comparison")
    improvement_percent: Optional[float] = Field(None, description="Percentage improvement from baseline")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('confidence_level')
    @classmethod
    def validate_confidence_level(cls, v):
        if v < 0 or v > 1:
            raise ValueError('Confidence level must be between 0 and 1')
        return v

class EffectivenessValidation(BaseModel):
    """Model for validating practice effectiveness."""
    validation_id: UUID = Field(default_factory=uuid4, description="Unique validation identifier")
    implementation_id: UUID = Field(..., description="Reference to practice implementation")
    validation_date: date = Field(..., description="Date of validation")
    validator_type: str = Field(..., description="Type of validator (expert, algorithm, farmer)")
    validator_id: Optional[UUID] = Field(None, description="ID of the validator")
    validation_status: ValidationStatus = Field(default=ValidationStatus.PENDING, description="Validation status")
    effectiveness_score: float = Field(..., ge=0, le=10, description="Overall effectiveness score (0-10)")
    water_savings_achieved: Optional[Decimal] = Field(None, description="Actual water savings achieved")
    soil_health_improvement: Optional[float] = Field(None, description="Soil health improvement score")
    cost_effectiveness_rating: Optional[float] = Field(..., ge=0, le=10, description="Cost effectiveness rating")
    farmer_satisfaction_score: Optional[float] = Field(..., ge=0, le=10, description="Farmer satisfaction score")
    validation_notes: Optional[str] = Field(None, description="Validation notes and comments")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for improvement")
    validated_at: datetime = Field(default_factory=datetime.utcnow)

class PracticeEffectivenessReport(BaseModel):
    """Comprehensive effectiveness report for a practice implementation."""
    report_id: UUID = Field(default_factory=uuid4, description="Unique report identifier")
    implementation_id: UUID = Field(..., description="Reference to practice implementation")
    report_period_start: date = Field(..., description="Report period start date")
    report_period_end: date = Field(..., description="Report period end date")
    overall_effectiveness_score: float = Field(..., ge=0, le=10, description="Overall effectiveness score")
    water_savings_summary: Dict[str, Any] = Field(..., description="Water savings summary")
    soil_health_summary: Dict[str, Any] = Field(..., description="Soil health impact summary")
    cost_benefit_summary: Dict[str, Any] = Field(..., description="Cost-benefit analysis summary")
    farmer_feedback: Optional[str] = Field(None, description="Farmer feedback and observations")
    challenges_summary: List[str] = Field(default_factory=list, description="Summary of challenges")
    success_factors: List[str] = Field(default_factory=list, description="Key success factors")
    improvement_recommendations: List[str] = Field(default_factory=list, description="Recommendations for improvement")
    next_steps: List[str] = Field(default_factory=list, description="Recommended next steps")
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class AdaptiveRecommendation(BaseModel):
    """Model for adaptive recommendations based on effectiveness data."""
    recommendation_id: UUID = Field(default_factory=uuid4, description="Unique recommendation identifier")
    implementation_id: UUID = Field(..., description="Reference to practice implementation")
    recommendation_type: str = Field(..., description="Type of adaptive recommendation")
    priority: str = Field(..., description="Priority level (high, medium, low)")
    description: str = Field(..., description="Detailed recommendation description")
    rationale: str = Field(..., description="Rationale for the recommendation")
    expected_impact: str = Field(..., description="Expected impact of the recommendation")
    implementation_timeline: str = Field(..., description="Recommended implementation timeline")
    resources_required: List[str] = Field(default_factory=list, description="Required resources")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in recommendation")
    based_on_data_points: int = Field(..., description="Number of data points used for recommendation")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PracticeEffectivenessRequest(BaseModel):
    """Request model for practice effectiveness tracking."""
    field_id: UUID = Field(..., description="Field identifier")
    practice_id: Optional[UUID] = Field(None, description="Specific practice to track (optional)")
    start_date: Optional[date] = Field(None, description="Start date for tracking period")
    end_date: Optional[date] = Field(None, description="End date for tracking period")
    include_validation: bool = Field(default=True, description="Include validation data")
    include_adaptive_recommendations: bool = Field(default=True, description="Include adaptive recommendations")

class PracticeEffectivenessResponse(BaseModel):
    """Response model for practice effectiveness tracking."""
    request_id: UUID = Field(default_factory=uuid4, description="Unique request identifier")
    field_id: UUID = Field(..., description="Field identifier")
    tracking_period: Dict[str, date] = Field(..., description="Tracking period dates")
    implementations: List[PracticeImplementation] = Field(default_factory=list, description="Practice implementations")
    performance_measurements: List[PerformanceMeasurement] = Field(default_factory=list, description="Performance measurements")
    effectiveness_validations: List[EffectivenessValidation] = Field(default_factory=list, description="Effectiveness validations")
    effectiveness_reports: List[PracticeEffectivenessReport] = Field(default_factory=list, description="Effectiveness reports")
    adaptive_recommendations: List[AdaptiveRecommendation] = Field(default_factory=list, description="Adaptive recommendations")
    overall_effectiveness_summary: Dict[str, Any] = Field(..., description="Overall effectiveness summary")
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class PracticeOptimizationInsight(BaseModel):
    """Model for machine learning insights and optimization recommendations."""
    insight_id: UUID = Field(default_factory=uuid4, description="Unique insight identifier")
    practice_type: str = Field(..., description="Type of conservation practice")
    region: str = Field(..., description="Geographic region")
    soil_type: str = Field(..., description="Soil type")
    insight_type: str = Field(..., description="Type of insight (optimization, prediction, etc.)")
    insight_description: str = Field(..., description="Description of the insight")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence in the insight")
    supporting_data_points: int = Field(..., description="Number of supporting data points")
    expected_improvement: str = Field(..., description="Expected improvement from applying insight")
    implementation_complexity: str = Field(..., description="Implementation complexity (low, medium, high)")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class RegionalEffectivenessAnalysis(BaseModel):
    """Model for regional effectiveness analysis."""
    analysis_id: UUID = Field(default_factory=uuid4, description="Unique analysis identifier")
    region: str = Field(..., description="Geographic region")
    analysis_period_start: date = Field(..., description="Analysis period start")
    analysis_period_end: date = Field(..., description="Analysis period end")
    practice_types_analyzed: List[str] = Field(..., description="Types of practices analyzed")
    total_implementations: int = Field(..., description="Total number of implementations analyzed")
    average_effectiveness_score: float = Field(..., description="Average effectiveness score")
    most_effective_practices: List[str] = Field(..., description="Most effective practices in region")
    regional_challenges: List[str] = Field(default_factory=list, description="Common regional challenges")
    regional_success_factors: List[str] = Field(default_factory=list, description="Regional success factors")
    optimization_opportunities: List[str] = Field(default_factory=list, description="Optimization opportunities")
    generated_at: datetime = Field(default_factory=datetime.utcnow)