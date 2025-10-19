"""
Operational constraint models for the fertilizer timing microservice.

These models capture constraint status, alternative schedules, and resource
allocation guidance produced by the operational constraint accommodation
service.
"""

from datetime import date, datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .strategy_integration import TimingConstraint, TimingConstraintType


class ConstraintStatus(BaseModel):
    """Detailed status for an operational constraint impacting timing."""

    constraint_type: TimingConstraintType = Field(
        ..., description="Type of constraint that requires accommodation"
    )
    name: str = Field(..., description="Human-friendly identifier for the constraint")
    affected_date: Optional[date] = Field(
        default=None,
        description="Date affected by the constraint when applicable",
    )
    severity: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Constraint severity where 1.0 represents a hard stop",
    )
    blocking: bool = Field(
        False,
        description="Indicates whether the constraint prevents execution on the primary date",
    )
    impacted_timings: List[str] = Field(
        default_factory=list,
        description="Identifiers of impacted fertilizer timings",
    )
    notes: List[str] = Field(
        default_factory=list,
        description="Observations describing the constraint context",
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Actions that accommodate or relieve the constraint",
    )


class AlternativeScheduleOption(BaseModel):
    """Alternative schedule option when the primary timing is obstructed."""

    fertilizer_type: str = Field(..., description="Fertilizer type impacted by the constraint")
    primary_date: date = Field(..., description="Original recommended date")
    alternative_date: date = Field(..., description="Proposed alternative date")
    reason: str = Field(..., description="Reason the alternative is considered viable")
    suitability_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Suitability score for the alternative timing",
    )


class ResourceAllocationPlan(BaseModel):
    """Resource allocation guidance aligned with constraint accommodation."""

    plan_date: date = Field(..., description="Date requiring resource coordination")
    equipment: List[str] = Field(
        default_factory=list,
        description="Equipment assignments or reservations for the date",
    )
    labor_required: int = Field(
        ..., ge=0, description="Estimated labor required to execute the application"
    )
    labor_available: int = Field(
        ..., ge=0, description="Known labor availability for the date"
    )
    readiness_actions: List[str] = Field(
        default_factory=list,
        description="Actions that close readiness gaps for the resources",
    )


class OperationalConstraintReport(BaseModel):
    """Aggregated constraint accommodation report for fertilizer timing."""

    request_id: str = Field(..., description="Identifier of the originating optimization request")
    generated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the report was generated",
    )
    constraint_status: List[ConstraintStatus] = Field(
        default_factory=list,
        description="Collection of evaluated operational constraints",
    )
    alternative_options: List[AlternativeScheduleOption] = Field(
        default_factory=list,
        description="Alternative schedules that respect operational limits",
    )
    resource_plans: List[ResourceAllocationPlan] = Field(
        default_factory=list,
        description="Resource allocation plans aligned with accommodations",
    )
    regulatory_notes: List[str] = Field(
        default_factory=list,
        description="Regulatory observations or compliance requirements",
    )
    generated_constraints: List[TimingConstraint] = Field(
        default_factory=list,
        description="Structured constraints suitable for downstream optimizers",
    )
    summary: str = Field(
        "",
        description="Narrative summary describing key constraint findings",
    )
    metadata: Dict[str, str] = Field(
        default_factory=dict,
        description="Additional metadata for downstream services",
    )


__all__ = [
    "ConstraintStatus",
    "AlternativeScheduleOption",
    "ResourceAllocationPlan",
    "OperationalConstraintReport",
]
