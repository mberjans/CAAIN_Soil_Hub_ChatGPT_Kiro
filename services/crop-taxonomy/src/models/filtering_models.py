"""
SQLAlchemy Models for Crop Filtering System

Database models for advanced crop filtering functionality including
pest resistance, market classes, certifications, seed availability,
farmer preferences, and popular filter combinations tracking.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class CropFilteringAttributes(Base):
    """
    Extended filtering attributes for crop varieties.
    
    Stores advanced filtering data for crop varieties including pest resistance,
    disease resistance, market classes, certifications, and performance metrics.
    """
    __tablename__ = 'crop_filtering_attributes'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    variety_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    
    # Pest and disease resistance (JSONB for flexibility)
    pest_resistance_traits = Column(JSONB, default={})
    disease_resistance_traits = Column(JSONB, default={})
    
    # Market and certification filters
    market_class_filters = Column(JSONB, default={})
    certification_filters = Column(JSONB, default={})
    
    # Seed availability
    seed_availability_filters = Column(JSONB, default={})
    
    # Performance metrics
    yield_stability_score = Column(Integer)
    drought_tolerance_score = Column(Integer)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Indexes for JSONB queries
    __table_args__ = (
        Index('idx_pest_resistance_gin', 'pest_resistance_traits', postgresql_using='gin'),
        Index('idx_disease_resistance_gin', 'disease_resistance_traits', postgresql_using='gin'),
        Index('idx_market_class_gin', 'market_class_filters', postgresql_using='gin'),
        Index('idx_certification_gin', 'certification_filters', postgresql_using='gin'),
    )


class FarmerPreference(Base):
    """
    Farmer filtering preferences and history.
    
    Stores farmer preferences and learning data to improve future recommendations.
    """
    __tablename__ = 'farmer_preferences'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Preference data
    preferred_filters = Column(JSONB, default={})
    filter_weights = Column(JSONB, default={})
    
    # Learning data
    selected_varieties = Column(JSONB, default=[])
    rejected_varieties = Column(JSONB, default=[])
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_preferred_filters_gin', 'preferred_filters', postgresql_using='gin'),
    )


class FilterCombination(Base):
    """
    Tracks popular filter combinations for optimization.
    
    Stores frequently used filter combinations with performance metrics
    to enable caching and optimization of common search patterns.
    """
    __tablename__ = 'filter_combinations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    combination_hash = Column(String(64), unique=True, nullable=False, index=True)
    filters = Column(JSONB, nullable=False)
    usage_count = Column(Integer, default=1)
    avg_result_count = Column(Integer)
    avg_response_time_ms = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    last_used_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<FilterCombination(hash='{self.combination_hash}', usage_count={self.usage_count})>"
        
    def __str__(self):
        return f"FilterCombination(id={self.id}, hash={self.combination_hash})"