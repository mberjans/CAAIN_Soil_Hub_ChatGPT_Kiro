from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class MicronutrientApplicationTimingBase(BaseModel):
    micronutrient_id: UUID = Field(..., description="ID of the micronutrient")
    crop_id: UUID = Field(..., description="ID of the crop")
    growth_stage: str = Field(..., description="Growth stage (e.g., vegetative, flowering)")
    timing_window_start: int = Field(..., ge=0, description="Start of timing window (e.g., days after planting)")
    timing_window_end: int = Field(..., ge=0, description="End of timing window (e.g., days after planting)")
    environmental_conditions: Dict[str, Any] = Field(..., description="Environmental conditions for optimal timing")
    efficiency_impact: float = Field(..., ge=0.0, le=1.0, description="Efficiency impact (0.0 to 1.0)")
    notes: Optional[str] = Field(None, description="Additional notes on timing")

class MicronutrientApplicationTimingCreate(MicronutrientApplicationTimingBase):
    pass

class MicronutrientApplicationTimingUpdate(MicronutrientApplicationTimingBase):
    micronutrient_id: Optional[UUID] = None
    crop_id: Optional[UUID] = None
    growth_stage: Optional[str] = None
    timing_window_start: Optional[int] = None
    timing_window_end: Optional[int] = None
    environmental_conditions: Optional[Dict[str, Any]] = None
    efficiency_impact: Optional[float] = None

class MicronutrientApplicationTimingResponse(MicronutrientApplicationTimingBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True