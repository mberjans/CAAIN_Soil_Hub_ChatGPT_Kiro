"""
Validation Models

This module defines Pydantic models for agricultural validation,
expert review management, and metrics tracking.

Author: AI Assistant
Date: 2024-12-28
Version: 1.0
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from enum import Enum

from pydantic import BaseModel, Field, validator


class ValidationSeverity(str, Enum):
    """Severity levels for validation issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ValidationStatus(str, Enum):
    """Status of validation process."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPERT_REVIEW_REQUIRED = "expert_review_required"


class ExpertReviewStatus(str, Enum):
    """Status of expert review."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"
    EXPERT_CONSULTATION = "expert_consultation"


class ReviewPriority(str, Enum):
    """Priority levels for expert reviews."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ReviewAssignmentStatus(str, Enum):
    """Status of review assignments."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class MetricsPeriod(str, Enum):
    """Metrics reporting periods."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class ValidationIssue(BaseModel):
    """Individual validation issue."""
    severity: ValidationSeverity = Field(..., description="Issue severity level")
    category: str = Field(..., description="Issue category")
    message: str = Field(..., description="Issue description")
    recommendation_id: Optional[UUID] = Field(None, description="Associated recommendation ID")
    variety_id: Optional[UUID] = Field(None, description="Associated variety ID")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional issue details")
    suggested_action: Optional[str] = Field(None, description="Suggested corrective action")


class ValidationResult(BaseModel):
    """Result of agricultural validation."""
    validation_id: UUID = Field(default_factory=uuid4, description="Unique validation ID")
    status: ValidationStatus = Field(..., description="Validation status")
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Overall validation score")
    issues: List[ValidationIssue] = Field(default_factory=list, description="Validation issues found")
    expert_review_required: bool = Field(default=False, description="Whether expert review is required")
    validation_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Validation timestamp")
    validation_duration_ms: float = Field(default=0.0, description="Validation duration in milliseconds")
    regional_context: Dict[str, Any] = Field(default_factory=dict, description="Regional context data")
    crop_context: Dict[str, Any] = Field(default_factory=dict, description="Crop context data")
    expert_review_status: Optional[ExpertReviewStatus] = Field(None, description="Expert review status")
    expert_feedback: Optional[str] = Field(None, description="Expert review feedback")
    expert_reviewer_id: Optional[UUID] = Field(None, description="Expert reviewer ID")
    expert_review_timestamp: Optional[datetime] = Field(None, description="Expert review timestamp")


class ExpertReviewer(BaseModel):
    """Expert reviewer profile."""
    reviewer_id: UUID = Field(default_factory=uuid4, description="Unique reviewer ID")
    name: str = Field(..., description="Expert reviewer name")
    credentials: str = Field(..., description="Professional credentials")
    specialization: List[str] = Field(..., description="Areas of expertise")
    region: str = Field(..., description="Primary region of expertise")
    institution: str = Field(..., description="Affiliated institution")
    contact_email: str = Field(..., description="Contact email")
    is_active: bool = Field(default=True, description="Active reviewer status")
    review_count: int = Field(default=0, description="Number of reviews completed")
    average_rating: float = Field(default=0.0, ge=0.0, le=1.0, description="Average rating from farmers")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    last_review_at: Optional[datetime] = Field(None, description="Last review timestamp")

    @validator('contact_email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v


class ExpertReview(BaseModel):
    """Expert review record."""
    review_id: UUID = Field(default_factory=uuid4, description="Unique review ID")
    validation_id: UUID = Field(..., description="Associated validation ID")
    reviewer_id: UUID = Field(..., description="Expert reviewer ID")
    status: ExpertReviewStatus = Field(default=ExpertReviewStatus.PENDING, description="Review status")
    review_score: float = Field(..., ge=0.0, le=1.0, description="Overall review score")
    agricultural_soundness: float = Field(..., ge=0.0, le=1.0, description="Agricultural soundness rating")
    regional_applicability: float = Field(..., ge=0.0, le=1.0, description="Regional applicability rating")
    economic_feasibility: float = Field(..., ge=0.0, le=1.0, description="Economic feasibility rating")
    farmer_practicality: float = Field(..., ge=0.0, le=1.0, description="Farmer practicality rating")
    comments: str = Field(..., min_length=10, description="Expert review comments")
    recommendations: List[str] = Field(default_factory=list, description="Expert recommendations")
    concerns: List[str] = Field(default_factory=list, description="Expert concerns")
    approval_conditions: List[str] = Field(default_factory=list, description="Conditions for approval")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")


class ReviewAssignment(BaseModel):
    """Expert review assignment."""
    assignment_id: UUID = Field(default_factory=uuid4, description="Unique assignment ID")
    validation_id: UUID = Field(..., description="Validation ID to review")
    reviewer_id: UUID = Field(..., description="Assigned expert reviewer")
    priority: ReviewPriority = Field(default=ReviewPriority.NORMAL, description="Review priority")
    status: ReviewAssignmentStatus = Field(default=ReviewAssignmentStatus.PENDING, description="Assignment status")
    assigned_at: datetime = Field(default_factory=datetime.utcnow, description="Assignment timestamp")
    due_date: datetime = Field(..., description="Review due date")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    review_notes: Optional[str] = Field(None, description="Review notes")
    escalation_reason: Optional[str] = Field(None, description="Escalation reason")
    created_by: UUID = Field(..., description="User who created the assignment")


class ExpertReviewWorkflow(BaseModel):
    """Expert review workflow configuration."""
    workflow_id: UUID = Field(default_factory=uuid4, description="Unique workflow ID")
    name: str = Field(..., description="Workflow name")
    description: str = Field(..., description="Workflow description")
    region: str = Field(..., description="Applicable region")
    crop_types: List[str] = Field(..., description="Applicable crop types")
    required_specializations: List[str] = Field(..., description="Required expert specializations")
    review_criteria: Dict[str, Any] = Field(..., description="Review criteria and weights")
    auto_assignment_rules: Dict[str, Any] = Field(..., description="Auto-assignment rules")
    escalation_rules: Dict[str, Any] = Field(..., description="Escalation rules")
    is_active: bool = Field(default=True, description="Workflow active status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


class ValidationMetricsReport(BaseModel):
    """Comprehensive validation metrics report."""
    report_id: UUID = Field(default_factory=uuid4, description="Unique report ID")
    period_start: datetime = Field(..., description="Report period start")
    period_end: datetime = Field(..., description="Report period end")
    period_type: MetricsPeriod = Field(..., description="Report period type")
    
    # Validation metrics
    total_validations: int = Field(default=0, description="Total validations performed")
    successful_validations: int = Field(default=0, description="Successful validations")
    failed_validations: int = Field(default=0, description="Failed validations")
    validation_success_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Validation success rate")
    average_validation_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Average validation score")
    average_validation_duration_ms: float = Field(default=0.0, description="Average validation duration")
    
    # Expert review metrics
    expert_reviews_required: int = Field(default=0, description="Expert reviews required")
    expert_reviews_completed: int = Field(default=0, description="Expert reviews completed")
    expert_reviews_pending: int = Field(default=0, description="Expert reviews pending")
    expert_reviews_overdue: int = Field(default=0, description="Expert reviews overdue")
    expert_review_completion_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Expert review completion rate")
    average_expert_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Average expert review score")
    average_expert_review_duration_hours: float = Field(default=0.0, description="Average expert review duration")
    
    # Quality metrics
    agricultural_soundness_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Average agricultural soundness score")
    regional_applicability_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Average regional applicability score")
    economic_feasibility_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Average economic feasibility score")
    farmer_practicality_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Average farmer practicality score")
    
    # Regional and crop coverage
    regional_coverage: Dict[str, int] = Field(default_factory=dict, description="Validations by region")
    crop_coverage: Dict[str, int] = Field(default_factory=dict, description="Validations by crop type")
    
    # Farmer satisfaction
    farmer_feedback_count: int = Field(default=0, description="Number of farmer feedback responses")
    average_farmer_satisfaction: float = Field(default=0.0, ge=0.0, le=1.0, description="Average farmer satisfaction score")
    farmer_satisfaction_distribution: Dict[str, int] = Field(default_factory=dict, description="Satisfaction score distribution")
    
    # Performance trends
    validation_trend: str = Field(default="stable", description="Validation performance trend")
    expert_review_trend: str = Field(default="stable", description="Expert review performance trend")
    farmer_satisfaction_trend: str = Field(default="stable", description="Farmer satisfaction trend")
    
    # Issues and concerns
    common_validation_issues: List[Dict[str, Any]] = Field(default_factory=list, description="Most common validation issues")
    expert_concerns: List[Dict[str, Any]] = Field(default_factory=list, description="Common expert concerns")
    farmer_complaints: List[Dict[str, Any]] = Field(default_factory=list, description="Common farmer complaints")
    
    # Recommendations
    improvement_recommendations: List[str] = Field(default_factory=list, description="System improvement recommendations")
    
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Report generation timestamp")


class ValidationRequest(BaseModel):
    """Request for agricultural validation."""
    request_id: UUID = Field(default_factory=uuid4, description="Unique request ID")
    recommendations: List[Dict[str, Any]] = Field(..., description="Recommendations to validate")
    request_context: Dict[str, Any] = Field(..., description="Request context")
    regional_context: Dict[str, Any] = Field(..., description="Regional context")
    crop_context: Dict[str, Any] = Field(..., description="Crop context")
    validation_options: Dict[str, Any] = Field(default_factory=dict, description="Validation options")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Request timestamp")


class ValidationResponse(BaseModel):
    """Response from agricultural validation."""
    response_id: UUID = Field(default_factory=uuid4, description="Unique response ID")
    request_id: UUID = Field(..., description="Associated request ID")
    validation_result: ValidationResult = Field(..., description="Validation result")
    expert_review_assignment: Optional[ReviewAssignment] = Field(None, description="Expert review assignment if required")
    recommendations: List[Dict[str, Any]] = Field(default_factory=list, description="Validated recommendations")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class ExpertReviewRequest(BaseModel):
    """Request for expert review."""
    request_id: UUID = Field(default_factory=uuid4, description="Unique request ID")
    validation_id: UUID = Field(..., description="Validation ID to review")
    reviewer_id: UUID = Field(..., description="Expert reviewer ID")
    priority: ReviewPriority = Field(default=ReviewPriority.NORMAL, description="Review priority")
    review_criteria: Dict[str, Any] = Field(default_factory=dict, description="Review criteria")
    additional_context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Request timestamp")


class ExpertReviewResponse(BaseModel):
    """Response from expert review."""
    response_id: UUID = Field(default_factory=uuid4, description="Unique response ID")
    request_id: UUID = Field(..., description="Associated request ID")
    expert_review: ExpertReview = Field(..., description="Expert review result")
    validation_updates: Dict[str, Any] = Field(default_factory=dict, description="Validation updates")
    follow_up_actions: List[str] = Field(default_factory=list, description="Follow-up actions required")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class FarmerFeedback(BaseModel):
    """Farmer feedback on recommendations."""
    feedback_id: UUID = Field(default_factory=uuid4, description="Unique feedback ID")
    recommendation_id: UUID = Field(..., description="Recommendation ID")
    farmer_id: UUID = Field(..., description="Farmer ID")
    satisfaction_score: float = Field(..., ge=0.0, le=1.0, description="Satisfaction score")
    feedback: Optional[str] = Field(None, description="Text feedback")
    recommendation_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0, description="Perceived accuracy")
    implementation_ease: Optional[float] = Field(None, ge=0.0, le=1.0, description="Implementation ease")
    economic_outcome: Optional[float] = Field(None, ge=0.0, le=1.0, description="Economic outcome")
    additional_comments: Optional[str] = Field(None, description="Additional comments")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Feedback timestamp")


class ValidationMetricsSummary(BaseModel):
    """Summary of validation metrics."""
    summary_id: UUID = Field(default_factory=uuid4, description="Unique summary ID")
    period_start: datetime = Field(..., description="Summary period start")
    period_end: datetime = Field(..., description="Summary period end")
    
    # Key performance indicators
    validation_accuracy: float = Field(..., ge=0.0, le=1.0, description="Validation accuracy")
    expert_approval_rate: float = Field(..., ge=0.0, le=1.0, description="Expert approval rate")
    farmer_satisfaction_rate: float = Field(..., ge=0.0, le=1.0, description="Farmer satisfaction rate")
    
    # System performance
    average_response_time_ms: float = Field(..., description="Average response time")
    system_uptime_percentage: float = Field(..., ge=0.0, le=100.0, description="System uptime percentage")
    
    # Quality metrics
    recommendation_quality_score: float = Field(..., ge=0.0, le=1.0, description="Overall recommendation quality")
    agricultural_soundness_score: float = Field(..., ge=0.0, le=1.0, description="Agricultural soundness score")
    
    # Coverage metrics
    regional_coverage_percentage: float = Field(..., ge=0.0, le=100.0, description="Regional coverage percentage")
    crop_coverage_count: int = Field(..., description="Number of crop types covered")
    
    # Improvement indicators
    improvement_trend: str = Field(..., description="Improvement trend")
    critical_issues_count: int = Field(..., description="Number of critical issues")
    recommendations_count: int = Field(..., description="Number of improvement recommendations")
    
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Summary generation timestamp")