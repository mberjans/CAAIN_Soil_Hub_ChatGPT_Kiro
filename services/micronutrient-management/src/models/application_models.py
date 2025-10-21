from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ..database.micronutrient_db import Base

class MicronutrientApplicationMethod(Base):
    __tablename__ = "micronutrient_application_methods"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    method_type = Column(String)  # e.g., 'foliar', 'soil', 'seed_treatment'
    efficiency_rate = Column(Float) # e.g., 0.7 for 70% efficiency
    equipment_requirements = Column(ARRAY(String)) # e.g., ['sprayer', 'fertilizer_spreader']
    cost_per_unit_area = Column(Float) # e.g., cost per acre
    environmental_impact = Column(JSON) # e.g., {'runoff_risk': 'low', 'leaching_risk': 'medium'}
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships (if any, e.g., to specific micronutrients or crops)
    # micronutrients = relationship("Micronutrient", secondary="method_micronutrient_association", back_populates="application_methods")
