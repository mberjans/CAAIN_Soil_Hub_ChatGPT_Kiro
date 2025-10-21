from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

class PriorityCategory(str, Enum):
    """Categories for fertilizer priorities."""
    ENVIRONMENTAL = "environmental"
    ECONOMIC = "economic"
    AGRONOMIC = "agronomic"
    OPERATIONAL = "operational"

class ConstraintType(str, Enum):
    """Types of fertilizer constraints."""
    ENVIRONMENTAL = "environmental"
    REGULATORY = "regulatory"
    ECONOMIC = "economic"
    AGRONOMIC = "agronomic"
    OPERATIONAL = "operational"
    SAFETY = "safety"

class AppliesTo(str, Enum):
    """What the constraint applies to."""
    FERTILIZER_TYPE = "fertilizer_type"
    NUTRIENT = "nutrient"
    APPLICATION_METHOD = "application_method"
    TIMING = "timing"
    COST = "cost"
    ENVIRONMENTAL_IMPACT = "environmental_impact"

class FertilizerPriorityBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Name of the priority (e.g., 'Environmental Impact')")
    description: Optional[str] = Field(None, max_length=500, description="Detailed description of the priority")
    weight: float = Field(..., ge=0.0, le=1.0, description="Importance weight of the priority (0.0 to 1.0)")
    category: PriorityCategory = Field(..., description="Category of the priority")

class FertilizerPriorityCreate(FertilizerPriorityBase):
    user_id: UUID = Field(..., description="ID of the user who owns this priority")

class FertilizerPriorityUpdate(FertilizerPriorityBase):
    name: Optional[str] = Field(None, min_length=3, max_length=100, description="Name of the priority (e.g., 'Environmental Impact')")
    weight: Optional[float] = Field(None, ge=0.0, le=1.0, description="Importance weight of the priority (0.0 to 1.0)")
    category: Optional[PriorityCategory] = Field(None, description="Category of the priority")

class FertilizerPriority(FertilizerPriorityBase):
    priority_id: UUID = Field(default_factory=uuid4, description="Unique identifier for the priority")
    user_id: UUID = Field(..., description="ID of the user who owns this priority")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True

class FertilizerConstraintBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Name of the constraint (e.g., 'Organic Certification')")
    description: Optional[str] = Field(None, max_length=500, description="Detailed description of the constraint")
    type: ConstraintType = Field(..., description="Type of the constraint")
    value: Any = Field(..., description="The constraint value (e.g., a number, a boolean, a list of allowed types)")
    unit: Optional[str] = Field(None, max_length=20, description="Unit of the constraint value (e.g., 'kg/ha', '%')")
    applies_to: AppliesTo = Field(..., description="What the constraint applies to")

class FertilizerConstraintCreate(FertilizerConstraintBase):
    user_id: UUID = Field(..., description="ID of the user who owns this constraint")

class FertilizerConstraintUpdate(FertilizerConstraintBase):
    name: Optional[str] = Field(None, min_length=3, max_length=100, description="Name of the constraint (e.g., 'Organic Certification')")
    type: Optional[ConstraintType] = Field(None, description="Type of the constraint")
    value: Optional[Any] = Field(None, description="The constraint value (e.g., a number, a boolean, a list of allowed types)")
    unit: Optional[str] = Field(None, max_length=20, description="Unit of the constraint value (e.g., 'kg/ha', '%')")
    applies_to: Optional[AppliesTo] = Field(None, description="What the constraint applies to")

class FertilizerConstraint(FertilizerConstraintBase):
    constraint_id: UUID = Field(default_factory=uuid4, description="Unique identifier for the constraint")
    user_id: UUID = Field(..., description="ID of the user who owns this constraint")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True
