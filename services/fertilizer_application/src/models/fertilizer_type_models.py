from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, func, Enum, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class FertilizerTypeEnum(enum.Enum):
    ORGANIC = "organic"
    SYNTHETIC = "synthetic"
    SLOW_RELEASE = "slow_release"
    LIQUID = "liquid"
    GRANULAR = "granular"
    FOLIAR = "foliar"
    GASEOUS = "gaseous"

class EnvironmentalImpactEnum(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class FertilizerType(Base):
    __tablename__ = "fertilizer_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    type = Column(Enum(FertilizerTypeEnum), nullable=False)
    npk_ratio = Column(JSONB, nullable=False, comment="NPK ratio as JSONB, e.g., {'N': 10, 'P': 10, 'K': 10}")
    micronutrients = Column(JSONB, default={}, comment="Micronutrients as JSONB, e.g., {'Zn': 1, 'B': 0.5}")
    cost_per_unit = Column(Float, nullable=False)
    unit = Column(String, nullable=False, default="kg")
    environmental_impact_score = Column(Enum(EnvironmentalImpactEnum), nullable=False)
    release_rate = Column(String, comment="e.g., 'fast', 'medium', 'slow'")
    organic_certified = Column(Boolean, default=False)
    application_methods = Column(JSONB, default=[], comment="List of suitable application methods")
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())