"""
SQLAlchemy Models for Crop Filtering System

Database models for advanced crop filtering functionality including
popular filter combinations tracking and optimization.
"""

from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

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