"""
Data models for fertilizer strategy management.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class StrategySharingSettings(BaseModel):
    """Sharing configuration for stored strategies."""

    is_public: bool = Field(default=False, description="Whether strategy is publicly accessible")
    shared_with: List[str] = Field(default_factory=list, description="List of user IDs with access")

    @field_validator("shared_with")
    @classmethod
    def validate_shared_with(cls, value: List[str]) -> List[str]:
        """Ensure shared user identifiers are non-empty."""
        if value is None:
            return []
        cleaned: List[str] = []
        for identifier in value:
            if identifier is None:
                raise ValueError("Shared user identifiers must be non-empty")
            text = str(identifier).strip()
            if not text:
                raise ValueError("Shared user identifiers must be non-empty")
            cleaned.append(text)
        return cleaned


class FieldStrategyData(BaseModel):
    """Captured per-field fertilizer strategy details."""

    field_id: str = Field(..., description="Unique field identifier")
    acres: float = Field(..., gt=0, description="Field size in acres")
    crop_type: Optional[str] = Field(None, description="Crop planted on the field")
    recommended_rates: Dict[str, float] = Field(default_factory=dict, description="Recommended nutrient rates")
    application_schedule: List[str] = Field(default_factory=list, description="Application timing schedule")
    application_method: Optional[str] = Field(None, description="Preferred application method")
    expected_yield: Optional[float] = Field(None, ge=0, description="Expected yield per acre")
    total_cost: Optional[float] = Field(None, ge=0, description="Total cost for the field strategy")
    roi_projection: Optional[float] = Field(None, description="Projected ROI for the field strategy")

    @field_validator("field_id")
    @classmethod
    def validate_field_id(cls, value: str) -> str:
        """Ensure field identifier is not blank."""
        if not value or not value.strip():
            raise ValueError("Field identifier cannot be blank")
        return value


class SaveStrategyRequest(BaseModel):
    """Request payload for saving fertilizer strategies."""

    strategy_name: str = Field(..., description="Human-readable strategy name")
    description: Optional[str] = Field(None, description="Detailed strategy description")
    user_id: str = Field(..., description="User requesting persistence")
    farm_id: Optional[str] = Field(None, description="Associated farm identifier")
    is_template: bool = Field(default=False, description="Whether strategy can be reused as template")
    tags: List[str] = Field(default_factory=list, description="Categorization tags")
    sharing: StrategySharingSettings = Field(default_factory=StrategySharingSettings, description="Sharing preferences")
    field_strategies: List[FieldStrategyData] = Field(default_factory=list, description="Collection of field strategies")
    economic_summary: Dict[str, Any] = Field(default_factory=dict, description="Economic summary data")
    environmental_metrics: Dict[str, Any] = Field(default_factory=dict, description="Environmental impact metrics")
    roi_estimate: Optional[float] = Field(None, description="Overall ROI estimate")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    strategy_id: Optional[str] = Field(None, description="Existing strategy identifier for versioning")
    version_notes: Optional[str] = Field(None, description="Notes describing this version")

    @field_validator("strategy_name", "user_id", mode="before")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        """Ensure required textual fields are populated."""
        if not value or not value.strip():
            raise ValueError("Required text fields cannot be empty")
        return value

    @field_validator("field_strategies")
    @classmethod
    def validate_field_strategies(cls, value: List[FieldStrategyData]) -> List[FieldStrategyData]:
        """Ensure at least one field strategy is provided."""
        if not value:
            raise ValueError("At least one field strategy must be provided")
        return value


class StrategyVersionInfo(BaseModel):
    """Metadata about a stored strategy version."""

    version_id: str = Field(..., description="Unique identifier for the stored version")
    version_number: int = Field(..., ge=1, description="Incremental version number")
    created_at: datetime = Field(..., description="Timestamp when version was created")
    created_by: str = Field(..., description="User ID who created the version")
    version_notes: Optional[str] = Field(None, description="Version notes supplied during save")


class StrategySaveResponse(BaseModel):
    """Response returned after saving a strategy."""

    strategy_id: str = Field(..., description="Persistent strategy identifier")
    created: bool = Field(..., description="Indicates if strategy record was newly created")
    latest_version: StrategyVersionInfo = Field(..., description="Latest version metadata")
    message: str = Field(..., description="Status message for the operation")


class StrategySummary(BaseModel):
    """Summary information about a stored strategy."""

    strategy_id: str = Field(..., description="Persistent strategy identifier")
    strategy_name: str = Field(..., description="Human-readable strategy name")
    latest_version: int = Field(..., ge=1, description="Latest version number")
    roi_estimate: Optional[float] = Field(None, description="Latest ROI estimate")
    total_cost: Optional[float] = Field(None, description="Latest total cost estimate")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last updated timestamp")


class StrategyComparisonMetric(BaseModel):
    """Comparison metric across strategies."""

    metric_name: str = Field(..., description="Metric label")
    values: Dict[str, float] = Field(default_factory=dict, description="Metric values keyed by strategy ID")
    interpretation: Optional[str] = Field(None, description="Human-readable interpretation")


class StrategyComparisonRequest(BaseModel):
    """Request payload for strategy comparison."""

    strategy_ids: List[str] = Field(default_factory=list, description="Strategies to compare")
    include_metrics: List[str] = Field(default_factory=list, description="Requested metric names")
    comparison_window_days: Optional[int] = Field(None, ge=1, description="Window in days for performance metrics")

    @field_validator("strategy_ids")
    @classmethod
    def validate_strategy_ids(cls, value: List[str]) -> List[str]:
        """Ensure at least two strategies are requested."""
        if not value or len(value) < 2:
            raise ValueError("At least two strategy identifiers are required for comparison")
        return value


class StrategyComparisonResponse(BaseModel):
    """Comparison response for requested strategies."""

    strategies: List[StrategySummary] = Field(default_factory=list, description="Strategies included in comparison")
    metrics: List[StrategyComparisonMetric] = Field(default_factory=list, description="Comparison metrics")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Response generation timestamp")


class StrategyUpdateRequest(BaseModel):
    """Request payload for updating a stored strategy."""

    strategy_name: Optional[str] = Field(None, description="Updated strategy name")
    description: Optional[str] = Field(None, description="Updated description")
    field_strategies: Optional[List[FieldStrategyData]] = Field(
        None,
        description="Updated field strategies; replaces existing set if provided"
    )
    economic_summary: Optional[Dict[str, Any]] = Field(None, description="Updated economic summary")
    environmental_metrics: Optional[Dict[str, Any]] = Field(None, description="Updated environmental metrics")
    roi_estimate: Optional[float] = Field(None, description="Updated ROI estimate")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")
    version_notes: Optional[str] = Field(None, description="Notes associated with the update")


class StrategyUpdateResponse(BaseModel):
    """Response information for strategy updates."""

    strategy_id: str = Field(..., description="Persistent strategy identifier")
    latest_version: StrategyVersionInfo = Field(..., description="Metadata for the new version")
    message: str = Field(..., description="Status message for the update")


class PerformanceMetric(BaseModel):
    """Individual performance metric captured for strategies."""

    metric_name: str = Field(..., description="Metric label")
    metric_value: float = Field(..., description="Metric value as float")


class StrategyPerformanceRequest(BaseModel):
    """Request payload for logging strategy performance."""

    strategy_id: str = Field(..., description="Strategy identifier being tracked")
    version_number: int = Field(..., ge=1, description="Associated strategy version number")
    reporting_period_start: datetime = Field(..., description="Start of reporting period")
    reporting_period_end: datetime = Field(..., description="End of reporting period")
    realized_yield: Optional[float] = Field(None, ge=0, description="Observed yield outcome")
    realized_cost: Optional[float] = Field(None, ge=0, description="Observed cost outcome")
    realized_revenue: Optional[float] = Field(None, ge=0, description="Observed revenue outcome")
    performance_metrics: List[PerformanceMetric] = Field(default_factory=list, description="Additional metrics")
    observations: Optional[str] = Field(None, description="Qualitative observations or notes")


class StrategyPerformanceResponse(BaseModel):
    """Response after logging performance metrics."""

    strategy_id: str = Field(..., description="Strategy identifier")
    version_number: int = Field(..., ge=1, description="Version related to the performance data")
    metrics_recorded: int = Field(..., ge=0, description="Number of metrics captured")
    message: str = Field(..., description="Status message for the operation")
