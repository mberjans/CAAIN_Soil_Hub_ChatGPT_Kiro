from sqlalchemy import Column, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class SoilNutrientAnalysis(Base):
    __tablename__ = "soil_nutrient_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id = Column(UUID(as_uuid=True), nullable=False)
    field_id = Column(UUID(as_uuid=True), nullable=False)
    analysis_date = Column(Date, nullable=False)
    lab_name = Column(String)
    sample_id = Column(String)

    macro_nutrients = Column(JSONB)
    micro_nutrients = Column(JSONB)
    other_properties = Column(JSONB)

    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<SoilNutrientAnalysis(id='{self.id}', farm_id='{self.farm_id}', analysis_date='{self.analysis_date}')>"
