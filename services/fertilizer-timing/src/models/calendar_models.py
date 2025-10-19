"""
Calendar response models for the fertilizer timing microservice.
"""

from datetime import date, datetime
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class SeasonalCalendarEntry(BaseModel):
    """Represents a single calendar entry for fertilizer operations."""

    event_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique event identifier")
    request_id: str = Field(..., description="Associated timing request identifier")
    event_type: str = Field(..., description="Type of calendar event")
    name: str = Field(..., description="Short display name")
    description: str = Field(..., description="Detailed description")
    start_date: date = Field(..., description="Event start date")
    end_date: Optional[date] = Field(None, description="Event end date")
    fertilizer_type: Optional[str] = Field(None, description="Associated fertilizer type")
    application_method: Optional[str] = Field(None, description="Application method")
    crop_stage: Optional[str] = Field(None, description="Crop growth stage")
    weather_condition: Optional[str] = Field(None, description="Weather condition summary")
    priority: str = Field(default="normal", description="Priority level (low, normal, high)")


class SeasonalCalendarResponse(BaseModel):
    """Aggregated calendar for a timing optimization result."""

    request_id: str = Field(..., description="Timing request identifier")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    entries: List[SeasonalCalendarEntry] = Field(default_factory=list, description="Calendar entries")
