"""
Pydantic models for economic validation results.

These models structure the output of the economic validation framework,
capturing scenario-level metrics, aggregate accuracy, and any issues that
require review by agricultural economists.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


def get_current_utc_time() -> datetime:
    """Return timezone-aware UTC timestamp for validation records."""
    return datetime.now(timezone.utc)


class ValidationThresholds(BaseModel):
    """Threshold configuration for economic validation metrics."""

    price_accuracy: float = Field(default=0.90, ge=0.0, le=1.0, description="Minimum acceptable price accuracy")
    cost_accuracy: float = Field(default=0.95, ge=0.0, le=1.0, description="Minimum acceptable cost accuracy")
    roi_accuracy: float = Field(default=0.90, ge=0.0, le=1.0, description="Minimum acceptable ROI accuracy")

    @field_validator("price_accuracy", "cost_accuracy", "roi_accuracy")
    @classmethod
    def validate_threshold(cls, value: float) -> float:
        """Ensure threshold values lie within expected range."""
        if value < 0.0:
            raise ValueError("Validation threshold cannot be negative")
        if value > 1.0:
            raise ValueError("Validation threshold cannot exceed 1.0")
        return value


class EconomicScenarioMetrics(BaseModel):
    """Scenario-specific validation metrics."""

    scenario_id: str = Field(..., description="Unique scenario identifier")
    price_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0, description="Price model accuracy for the scenario")
    cost_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0, description="Cost model accuracy for the scenario")
    roi_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0, description="ROI prediction accuracy for the scenario")
    issues: List[str] = Field(default_factory=list, description="Critical issues requiring review")
    warnings: List[str] = Field(default_factory=list, description="Non-blocking warnings")
    passed: bool = Field(default=False, description="Whether the scenario meets all thresholds")


class EconomicValidationSummary(BaseModel):
    """Aggregate validation summary across all scenarios."""

    generated_at: datetime = Field(default_factory=get_current_utc_time, description="Timestamp when validation ran")
    price_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0, description="Aggregate price accuracy")
    cost_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0, description="Aggregate cost accuracy")
    roi_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0, description="Aggregate ROI accuracy")
    scenario_metrics: Dict[str, EconomicScenarioMetrics] = Field(default_factory=dict, description="Metrics by scenario")
    threshold_configuration: ValidationThresholds = Field(default_factory=ValidationThresholds, description="Validation thresholds used")
    passed: bool = Field(default=False, description="Whether aggregate metrics satisfy thresholds")
    issues: List[str] = Field(default_factory=list, description="Aggregate issues requiring expert review")
    warnings: List[str] = Field(default_factory=list, description="Aggregate warnings for monitoring")
