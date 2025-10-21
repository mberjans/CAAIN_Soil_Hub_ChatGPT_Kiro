from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
import uuid

from ..schemas.micronutrient_schemas import MicronutrientType, RecommendationPriority

Base = declarative_base()

class MicronutrientLevelModel(Base):
    __tablename__ = "micronutrient_levels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_location_id = Column(UUID(as_uuid=True), nullable=False)
    nutrient_type = Column(SQLEnum(MicronutrientType), nullable=False)
    level_ppm = Column(Float, nullable=False)
    unit = Column(String, default="ppm")
    test_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    recommendations = relationship("MicronutrientRecommendationModel", back_populates="micronutrient_level")

class MicronutrientRecommendationModel(Base):
    __tablename__ = "micronutrient_recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    micronutrient_level_id = Column(UUID(as_uuid=True), ForeignKey("micronutrient_levels.id"), nullable=False)
    nutrient_type = Column(SQLEnum(MicronutrientType), nullable=False)
    priority = Column(SQLEnum(RecommendationPriority), nullable=False)
    recommended_amount = Column(Float)
    unit = Column(String)
    application_method = Column(String)
    justification = Column(String, nullable=False)
    crop_impact = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    micronutrient_level = relationship("MicronutrientLevelModel", back_populates="recommendations")

class MicronutrientCropThresholdsModel(Base):
    __tablename__ = "micronutrient_crop_thresholds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_type = Column(String, nullable=False)
    nutrient_type = Column(SQLEnum(MicronutrientType), nullable=False)
    min_optimal_ppm = Column(Float, nullable=False)
    max_optimal_ppm = Column(Float, nullable=False)
    deficiency_threshold_ppm = Column(Float, nullable=False)
    toxicity_threshold_ppm = Column(Float, nullable=False)
    soil_ph_min = Column(Float, nullable=False)
    soil_ph_max = Column(Float, nullable=False)
    soil_type_impact = Column(JSONB, default={})
    growth_stage_impact = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (UniqueConstraint('crop_type', 'nutrient_type', name='_crop_nutrient_uc'),)