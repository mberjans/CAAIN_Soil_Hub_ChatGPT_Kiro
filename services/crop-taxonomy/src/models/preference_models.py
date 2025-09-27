"""
Crop Preference Models

Pydantic models supporting farmer crop preference profiles, preference
weighting, constraint management, and learning inputs.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field, validator


class PreferenceType(str, Enum):
    """Types of crop preference profiles."""

    USER_DEFINED = "user_defined"
    SYSTEM_SUGGESTED = "system_suggested"
    LEARNED = "learned"


class PreferenceDimension(str, Enum):
    """Dimensions that can carry explicit weighting."""

    CROP_CATEGORY = "crop_category"
    MANAGEMENT = "management"
    MARKET = "market"
    SUSTAINABILITY = "sustainability"
    CLIMATE = "climate"
    SOIL = "soil"
    CUSTOM = "custom"


class ConstraintType(str, Enum):
    """Types of constraints influencing filtering outcomes."""

    EXCLUDE = "exclude"
    LIMIT = "limit"
    REQUIRE = "require"


class RiskTolerance(str, Enum):
    """Farmer risk tolerance options for preference profiles."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class ManagementStyle(str, Enum):
    """Management style preferences."""

    LOW_INPUT = "low_input"
    BALANCED = "balanced"
    HIGH_INTENSITY = "high_intensity"


class PreferenceWeight(BaseModel):
    """Weight assigned to a specific preference dimension and key."""

    dimension: PreferenceDimension = Field(..., description="Target preference dimension")
    key: str = Field(..., min_length=1, description="Identifier within the dimension")
    weight: float = Field(..., ge=0.0, le=1.0, description="Relative importance weighting")

    @validator("key")
    def validate_key(cls, value: str) -> str:
        cleaned = value.strip()
        if cleaned == "":
            raise ValueError("Preference key cannot be empty")
        return cleaned


class PreferenceConstraint(BaseModel):
    """Constraint applied to filtering or recommendation outputs."""

    constraint_type: ConstraintType = Field(..., description="Constraint category")
    dimension: PreferenceDimension = Field(..., description="Dimension impacted by constraint")
    key: str = Field(..., min_length=1, description="Target identifier")
    limit_value: Optional[float] = Field(None, ge=0.0, description="Numeric limit if applicable")
    notes: Optional[str] = Field(None, description="Free-form explanation")

    @validator("key")
    def validate_key(cls, value: str) -> str:
        cleaned = value.strip()
        if cleaned == "":
            raise ValueError("Constraint key cannot be empty")
        return cleaned


class PreferenceConfidence(str, Enum):
    """Confidence level representing how reliable a preference value is."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PreferenceSignal(BaseModel):
    """Signal captured when a farmer interacts with crop content."""

    crop_id: UUID = Field(..., description="Crop identifier referenced by the signal")
    signal_type: str = Field(..., description="Type of interaction")
    weight: float = Field(default=1.0, ge=-1.0, le=1.0, description="Impact weight of the signal")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional context payload")

    @validator("signal_type")
    def validate_signal_type(cls, value: str) -> str:
        cleaned = value.strip()
        if cleaned == "":
            raise ValueError("Signal type cannot be empty")
        return cleaned


class PreferenceLearningRequest(BaseModel):
    """Request payload for preference learning operation."""

    user_id: UUID = Field(..., description="User identifier")
    signals: List[PreferenceSignal] = Field(default_factory=list, description="Interaction signals")
    learning_rate: float = Field(default=0.1, ge=0.0, le=1.0, description="Learning rate applied")
    decay_factor: float = Field(default=0.9, ge=0.0, le=1.0, description="Decay factor for existing weights")

    @validator("signals")
    def validate_signals(cls, value: List[PreferenceSignal]) -> List[PreferenceSignal]:
        if value is None or len(value) == 0:
            raise ValueError("At least one preference signal is required for learning")
        return value


class PreferenceProfile(BaseModel):
    """Comprehensive crop preference profile."""

    preference_id: Optional[UUID] = Field(None, description="Unique identifier for the preference profile")
    user_id: UUID = Field(..., description="User identifier")
    preference_type: PreferenceType = Field(default=PreferenceType.USER_DEFINED, description="Profile type")
    title: Optional[str] = Field(None, description="Human-readable title")

    crop_categories: List[str] = Field(default_factory=list, description="Preferred crop categories")
    management_style: Optional[ManagementStyle] = Field(None, description="Management style preference")
    risk_tolerance: Optional[RiskTolerance] = Field(None, description="Risk tolerance setting")
    market_focus: List[str] = Field(default_factory=list, description="Target market focus areas")
    sustainability_focus: List[str] = Field(default_factory=list, description="Sustainability goals")

    weights: List[PreferenceWeight] = Field(default_factory=list, description="Preference weights")
    constraints: List[PreferenceConstraint] = Field(default_factory=list, description="Preference constraints")
    priority_notes: Dict[str, str] = Field(default_factory=dict, description="Additional priority notes")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata values")

    confidence: PreferenceConfidence = Field(default=PreferenceConfidence.MEDIUM, description="Confidence level")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    @validator("crop_categories", "market_focus", "sustainability_focus", pre=True)
    def normalize_string_lists(cls, value: Optional[List[str]]) -> List[str]:
        normalized: List[str] = []
        if value is None:
            return normalized
        for item in value:
            if item is None:
                continue
            cleaned = str(item).strip()
            if cleaned == "":
                continue
            normalized.append(cleaned)
        return normalized

    @validator("weights")
    def validate_weights(cls, value: List[PreferenceWeight]) -> List[PreferenceWeight]:
        if value is None:
            return []
        total_weight = 0.0
        for weight_record in value:
            total_weight += weight_record.weight
        if total_weight > 0:
            if total_weight < 0.5 or total_weight > 5.0:
                raise ValueError("Total preference weights must be between 0.5 and 5.0 for stability")
        seen_keys: Dict[str, bool] = {}
        for weight_record in value:
            composite_key = f"{weight_record.dimension.value}:{weight_record.key}"
            if composite_key in seen_keys:
                raise ValueError("Duplicate preference weighting detected")
            seen_keys[composite_key] = True
        return value


class PreferenceProfileResponse(BaseModel):
    """API response representation of a preference profile."""

    profile: PreferenceProfile = Field(..., description="Preference profile data")
    sources: List[str] = Field(default_factory=list, description="Sources contributing to this profile")
    derived_recommendations: List[str] = Field(default_factory=list, description="Derived recommendations")
    conflict_notes: List[str] = Field(default_factory=list, description="Detected conflicts")

    @validator("sources", "derived_recommendations", "conflict_notes", pre=True)
    def normalize_strings(cls, value: Optional[List[str]]) -> List[str]:
        normalized: List[str] = []
        if value is None:
            return normalized
        for item in value:
            if item is None:
                continue
            cleaned = str(item).strip()
            if cleaned == "":
                continue
            normalized.append(cleaned)
        return normalized


class PreferenceUpdateRequest(BaseModel):
    """Update request for a preference profile."""

    profile: PreferenceProfile = Field(..., description="Profile to upsert")
    replace_existing: bool = Field(default=False, description="Replace existing profile data")


__all__ = [
    "PreferenceType",
    "PreferenceDimension",
    "ConstraintType",
    "RiskTolerance",
    "ManagementStyle",
    "PreferenceWeight",
    "PreferenceConstraint",
    "PreferenceConfidence",
    "PreferenceSignal",
    "PreferenceLearningRequest",
    "PreferenceProfile",
    "PreferenceProfileResponse",
    "PreferenceUpdateRequest",
]
