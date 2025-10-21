from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON, UUID as SQL_UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4

from ..database import Base # Import Base from the shared database.py

class NutrientLevelORM(Base):
    __tablename__ = "nutrient_levels"

    id = Column(SQL_UUID, primary_key=True, default=uuid4)
    tissue_test_id = Column(SQL_UUID, ForeignKey("tissue_test_results.id"), nullable=False)
    nutrient_name = Column(String, nullable=False)
    level = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    sufficiency_range_min = Column(Float, nullable=True)
    sufficiency_range_max = Column(Float, nullable=True)

    tissue_test = relationship("TissueTestResultORM", back_populates="nutrients")

class TissueTestResultORM(Base):
    __tablename__ = "tissue_test_results"

    id = Column(SQL_UUID, primary_key=True, default=uuid4)
    farm_id = Column(SQL_UUID, nullable=False)
    field_id = Column(SQL_UUID, nullable=False)
    crop_type = Column(String, nullable=False)
    growth_stage = Column(String, nullable=False)
    test_date = Column(DateTime, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    nutrients = relationship("NutrientLevelORM", back_populates="tissue_test", cascade="all, delete-orphan")