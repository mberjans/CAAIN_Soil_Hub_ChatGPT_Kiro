from sqlalchemy import Column, String, Text, Float, DateTime, JSON, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class NutrientDeficiencySymptom(Base):
    __tablename__ = "nutrient_deficiency_symptoms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nutrient = Column(String(50), nullable=False, index=True)
    crop_type = Column(String(100), nullable=False, index=True)
    symptom_name = Column(String(150), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    affected_parts = Column(ARRAY(Text), nullable=False)
    visual_characteristics = Column(ARRAY(Text), nullable=False)
    severity_levels = Column(JSON, nullable=False) # e.g., {"mild": "slight yellowing", "moderate": "pronounced yellowing"}
    growth_stages = Column(ARRAY(Text), nullable=False)
    confidence_score_threshold = Column(Float, default=0.7)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<NutrientDeficiencySymptom(symptom_name='{self.symptom_name}', nutrient='{self.nutrient}', crop_type='{self.crop_type}')>"
