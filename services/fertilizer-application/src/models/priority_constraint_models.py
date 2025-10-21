from enum import Enum
from typing import List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, String, Float
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PriorityType(str, Enum):
    """Enum for different types of priorities in fertilizer application."""
    YIELD_MAXIMIZATION = "yield_maximization"
    COST_MINIMIZATION = "cost_minimization"
    ENVIRONMENTAL_PROTECTION = "environmental_protection"
    SOIL_HEALTH_IMPROVEMENT = "soil_health_improvement"
    LABOR_EFFICIENCY = "labor_efficiency"
    NUTRIENT_USE_EFFICIENCY = "nutrient_use_efficiency"

class ConstraintType(str, Enum):
    """Enum for different types of constraints in fertilizer application."""
    BUDGET = "budget"
    EQUIPMENT_AVAILABILITY = "equipment_availability"
    ENVIRONMENTAL_REGULATION = "environmental_regulation"
    SOIL_TYPE_LIMITATION = "soil_type_limitation"
    CROP_ROTATION_REQUIREMENT = "crop_rotation_requirement"
    WEATHER_CONDITION = "weather_condition"
    TIME_WINDOW = "time_window"
    FERTILIZER_AVAILABILITY = "fertilizer_availability"

class Priority(BaseModel):
    """Pydantic model for a single priority."""
    priority_id: UUID = Field(default_factory=uuid4, description="Unique identifier for the priority")
    priority_type: PriorityType = Field(..., description="Type of priority")
    weight: float = Field(..., ge=0.0, le=1.0, description="Importance weight of the priority (0.0 to 1.0)")
    description: Optional[str] = Field(None, description="Detailed description of the priority")

    @validator('weight')
    def validate_weight(cls, v):
        if not (0.0 <= v <= 1.0):
            raise ValueError('Weight must be between 0.0 and 1.0')
        return v

class Constraint(BaseModel):
    """Pydantic model for a single constraint."""
    constraint_id: UUID = Field(default_factory=uuid4, description="Unique identifier for the constraint")
    constraint_type: ConstraintType = Field(..., description="Type of constraint")
    value: Union[float, str] = Field(..., description="Value of the constraint (e.g., budget amount, equipment name)")
    unit: Optional[str] = Field(None, description="Unit of the constraint value (e.g., 'USD', 'units')")
    description: Optional[str] = Field(None, description="Detailed description of the constraint")

class PriorityConstraintInput(BaseModel):
    """Pydantic model for inputting a list of priorities and constraints."""
    priorities: List[Priority] = Field(..., description="List of priorities for fertilizer application")
    constraints: List[Constraint] = Field(..., description="List of constraints for fertilizer application")

class PriorityDB(Base):
    """SQLAlchemy model for storing priorities in the database."""
    __tablename__ = "fertilizer_priorities"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    priority_type = Column(String, nullable=False)
    weight = Column(Float, nullable=False)
    description = Column(String, nullable=True)

class ConstraintDB(Base):
    """SQLAlchemy model for storing constraints in the database."""
    __tablename__ = "fertilizer_constraints"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    constraint_type = Column(String, nullable=False)
    value = Column(String, nullable=False)  # Store as string for flexibility
    unit = Column(String, nullable=True)
    description = Column(String, nullable=True)
