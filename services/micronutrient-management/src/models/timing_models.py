from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ..database.micronutrient_db import Base

class MicronutrientApplicationTiming(Base):
    __tablename__ = "micronutrient_application_timings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    micronutrient_id = Column(UUID(as_uuid=True), nullable=False) # Reference to a Micronutrient model (not yet defined)
    crop_id = Column(UUID(as_uuid=True), nullable=False) # Reference to a Crop model (not yet defined)
    growth_stage = Column(String) # e.g., 'vegetative', 'flowering', 'grain_fill'
    timing_window_start = Column(Integer) # Days after planting or specific growth stage code
    timing_window_end = Column(Integer) # Days after planting or specific growth stage code
    environmental_conditions = Column(JSON) # e.g., {'min_temp': 15, 'max_temp': 30, 'soil_moisture': 'adequate'}
    efficiency_impact = Column(Float) # Multiplier for efficiency based on timing
    notes = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships (if any, e.g., to specific micronutrients or crops)
