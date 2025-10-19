"""
Alert response models for the fertilizer timing microservice.
"""

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class TimingAlert(BaseModel):
    """Represents a timing alert for agronomic or operational risks."""

    alert_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique alert identifier")
    request_id: str = Field(..., description="Associated timing request identifier")
    severity: str = Field(..., description="Alert severity (info, warning, critical)")
    title: str = Field(..., description="Alert title")
    message: str = Field(..., description="Alert message body")
    action: Optional[str] = Field(None, description="Recommended action")
    factors: List[str] = Field(default_factory=list, description="Factors contributing to alert")


class TimingAlertResponse(BaseModel):
    """Collection of generated alerts."""

    request_id: str = Field(..., description="Timing request identifier")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    alerts: List[TimingAlert] = Field(default_factory=list, description="Generated alerts")
