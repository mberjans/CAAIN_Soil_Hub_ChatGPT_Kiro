from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class MicronutrientApplicationMethodBase(BaseModel):
    name: str = Field(..., description="Name of the application method")
    description: Optional[str] = Field(None, description="Description of the method")
    method_type: str = Field(..., description="Type of method (e.g., foliar, soil, seed_treatment)")
    efficiency_rate: float = Field(..., ge=0.0, le=1.0, description="Efficiency rate (0.0 to 1.0)")
    equipment_requirements: List[str] = Field(..., description="List of required equipment")
    cost_per_unit_area: float = Field(..., ge=0.0, description="Cost per unit area (e.g., per acre)")
    environmental_impact: Dict[str, Any] = Field(..., description="Environmental impact details")

class MicronutrientApplicationMethodCreate(MicronutrientApplicationMethodBase):
    pass

class MicronutrientApplicationMethodUpdate(MicronutrientApplicationMethodBase):
    name: Optional[str] = None
    method_type: Optional[str] = None
    efficiency_rate: Optional[float] = None
    equipment_requirements: Optional[List[str]] = None
    cost_per_unit_area: Optional[float] = None
    environmental_impact: Optional[Dict[str, Any]] = None

class MicronutrientApplicationMethodResponse(MicronutrientApplicationMethodBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
