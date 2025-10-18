"""
Data models for mobile fertilizer strategy tracking and monitoring.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class MobileGpsCoordinate(BaseModel):
    """GPS coordinate payload captured from the mobile device."""

    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    accuracy: Optional[float] = Field(None, ge=0.0, description="Accuracy in meters")


class MobileStrategyPhotoMetadata(BaseModel):
    """Metadata for photos captured during strategy tracking."""

    photo_id: str = Field(..., description="Unique identifier for the captured photo")
    uri: Optional[str] = Field(None, description="Device or server URI for the photo")
    captured_at: datetime = Field(default_factory=datetime.utcnow)
    file_size_bytes: Optional[int] = Field(None, ge=0, description="Photo file size in bytes")
    notes: Optional[str] = Field(None, description="Operator notes for the photo")
    synced: bool = Field(default=False, description="Indicates if the photo has been synchronized")

    @field_validator("photo_id")
    @classmethod
    def validate_photo_id(cls, value: str) -> str:
        if not value:
            raise ValueError("Photo identifier cannot be blank")
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Photo identifier cannot be blank")
        return trimmed


class StrategyApplicationDetail(BaseModel):
    """Application specific details captured during progress tracking."""

    product_name: Optional[str] = Field(None, description="Fertilizer product applied")
    application_rate: Optional[float] = Field(None, ge=0.0, description="Application rate per acre")
    rate_unit: Optional[str] = Field(None, description="Unit for application rate")
    equipment: Optional[str] = Field(None, description="Equipment used during application")
    status: Optional[str] = Field(None, description="Application status (planned, completed, delayed)")
    notes: Optional[str] = Field(None, description="Operator notes for the application event")


class StrategyCostSummary(BaseModel):
    """Cost metrics recorded from the field."""

    input_cost: Optional[float] = Field(None, ge=0.0, description="Actual input cost recorded")
    labor_cost: Optional[float] = Field(None, ge=0.0, description="Labor cost for the activity")
    equipment_cost: Optional[float] = Field(None, ge=0.0, description="Equipment operating cost")
    total_cost: Optional[float] = Field(None, ge=0.0, description="Total cost for the tracked period")
    currency: Optional[str] = Field(None, description="Currency code for the cost values")


class StrategyYieldSummary(BaseModel):
    """Yield metrics or projections recorded from the field."""

    observed_yield: Optional[float] = Field(None, ge=0.0, description="Observed yield value")
    expected_yield: Optional[float] = Field(None, ge=0.0, description="Updated expectation")
    yield_unit: Optional[str] = Field(None, description="Unit for the yield values")
    notes: Optional[str] = Field(None, description="Field observations that affect yield")


class MobileStrategyProgressEntry(BaseModel):
    """Progress entry reported from a mobile device."""

    client_event_id: str = Field(..., description="Client generated identifier for conflict resolution")
    strategy_id: str = Field(..., description="Associated strategy identifier")
    version_number: int = Field(..., ge=1, description="Strategy version referenced by the event")
    user_id: str = Field(..., description="Identifier for the operator capturing the entry")
    field_id: Optional[str] = Field(None, description="Field identifier if available")
    activity_type: str = Field(..., description="Type of activity performed")
    status: str = Field(default="recorded", description="Status of the tracked activity")
    activity_timestamp: datetime = Field(default_factory=datetime.utcnow)
    device_identifier: Optional[str] = Field(None, description="Mobile device identifier")
    notes: Optional[str] = Field(None, description="Operator notes from the field")
    captured_offline: bool = Field(default=False, description="Indicates if the entry was captured offline")
    gps: Optional[MobileGpsCoordinate] = Field(None, description="GPS coordinate metadata")
    application: Optional[StrategyApplicationDetail] = Field(None, description="Application-specific details")
    cost_summary: Optional[StrategyCostSummary] = Field(None, description="Recorded cost metrics")
    yield_summary: Optional[StrategyYieldSummary] = Field(None, description="Recorded yield metrics")
    photos: List[MobileStrategyPhotoMetadata] = Field(default_factory=list, description="Captured photos metadata")
    attachments: Dict[str, Any] = Field(default_factory=dict, description="Additional attachment payloads")

    @field_validator("client_event_id", "strategy_id", "user_id", "activity_type")
    @classmethod
    def validate_required_strings(cls, value: str) -> str:
        if value is None:
            raise ValueError("Required string value cannot be None")
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Required string value cannot be blank")
        return trimmed

    @field_validator("photos")
    @classmethod
    def validate_photos(cls, value: List[MobileStrategyPhotoMetadata]) -> List[MobileStrategyPhotoMetadata]:
        validated: List[MobileStrategyPhotoMetadata] = []
        if value is None:
            return validated
        index = 0
        while index < len(value):
            photo = value[index]
            if photo is None:
                index += 1
                continue
            validated.append(photo)
            index += 1
        return validated


class MobileStrategyProgressResponse(BaseModel):
    """Response payload after recording a progress entry."""

    activity_id: str = Field(..., description="Server generated activity identifier")
    status: str = Field(..., description="Processing status")
    conflict_resolved: bool = Field(default=False, description="Indicates if conflict resolution was applied")
    created: bool = Field(default=True, description="Indicates if the record was created")
    synced: bool = Field(default=False, description="Indicates if the entry was synchronized with analytics")


class MobileStrategySyncResult(BaseModel):
    """Individual result for synced entries."""

    client_event_id: str = Field(..., description="Client event identifier echoed back")
    activity_id: Optional[str] = Field(None, description="Server activity identifier if stored")
    status: str = Field(..., description="Result status for the entry")
    conflict_resolved: bool = Field(default=False, description="Whether a conflict was resolved for the entry")


class MobileStrategySyncRequest(BaseModel):
    """Batch synchronization request from mobile devices."""

    entries: List[MobileStrategyProgressEntry] = Field(default_factory=list, description="Entries awaiting sync")

    @field_validator("entries")
    @classmethod
    def validate_entries(cls, value: List[MobileStrategyProgressEntry]) -> List[MobileStrategyProgressEntry]:
        if value is None:
            return []
        index = 0
        sanitized: List[MobileStrategyProgressEntry] = []
        while index < len(value):
            entry = value[index]
            if entry is not None:
                sanitized.append(entry)
            index += 1
        return sanitized


class MobileStrategySyncResponse(BaseModel):
    """Response payload for batch synchronization."""

    results: List[MobileStrategySyncResult] = Field(default_factory=list)
    conflicts_detected: bool = Field(default=False)
    processed_count: int = Field(default=0, ge=0)


class MobileStrategySummaryActivity(BaseModel):
    """Activity entry included in summary response."""

    activity_id: str = Field(..., description="Stored activity identifier")
    activity_type: str = Field(..., description="Type of activity")
    status: str = Field(..., description="Current status for the activity")
    recorded_at: datetime = Field(..., description="Timestamp when activity was recorded")
    notes: Optional[str] = Field(None, description="Notes provided by the operator")
    user_id: Optional[str] = Field(None, description="Operator identifier")
    field_id: Optional[str] = Field(None, description="Field identifier if available")
    cost_summary: Optional[StrategyCostSummary] = Field(None)
    yield_summary: Optional[StrategyYieldSummary] = Field(None)


class MobileStrategyPerformanceSnapshot(BaseModel):
    """Performance snapshot derived from analytics."""

    total_events_recorded: int = Field(default=0, ge=0)
    last_synced_at: Optional[datetime] = Field(None)
    roi_projection: Optional[float] = Field(None, description="Latest ROI projection value")
    realized_cost: Optional[float] = Field(None, description="Latest recorded cost")
    realized_yield: Optional[float] = Field(None, description="Latest recorded yield")


class MobileStrategySummaryResponse(BaseModel):
    """Aggregated mobile tracking summary for a strategy."""

    strategy_id: str = Field(..., description="Strategy identifier")
    version_number: int = Field(..., ge=1, description="Strategy version number")
    progress_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    pending_actions: int = Field(default=0, ge=0)
    recent_activities: List[MobileStrategySummaryActivity] = Field(default_factory=list)
    performance_snapshot: MobileStrategyPerformanceSnapshot = Field(
        default_factory=MobileStrategyPerformanceSnapshot
    )
