"""
Farm Location Input SQLAlchemy Models
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

SQLAlchemy models for farm location database tables.
"""

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, 
    ForeignKey, CheckConstraint, UniqueConstraint, Index, DECIMAL
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime
from typing import Optional

# Use the same base as the main models
try:
    from .models import Base
except ImportError:
    # Fallback if importing separately
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()


class FarmLocation(Base):
    """Farm location model for the location input feature."""
    
    __tablename__ = 'farm_locations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    name = Column(String(100), nullable=False)
    latitude = Column(DECIMAL(10, 8), nullable=False)
    longitude = Column(DECIMAL(11, 8), nullable=False)
    address = Column(Text)
    county = Column(String(100))
    state = Column(String(50))
    climate_zone = Column(String(20))
    source = Column(String(20), nullable=False)
    verified = Column(Boolean, default=False)
    accuracy_meters = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    fields = relationship("FarmField", back_populates="location", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("latitude >= -90 AND latitude <= 90", name='valid_latitude'),
        CheckConstraint("longitude >= -180 AND longitude <= 180", name='valid_longitude'),
        CheckConstraint("source IN ('gps', 'address', 'map', 'current')", name='valid_source'),
        Index('idx_farm_locations_user_id', 'user_id'),
        Index('idx_farm_locations_coordinates', 'latitude', 'longitude'),
        Index('idx_farm_locations_state_county', 'state', 'county'),
        Index('idx_farm_locations_source', 'source'),
        Index('idx_farm_locations_verified', 'verified'),
    )
    
    def __repr__(self):
        return f"<FarmLocation(id='{self.id}', name='{self.name}', lat={self.latitude}, lon={self.longitude})>"
    
    @property
    def coordinates(self) -> tuple:
        """Get coordinates as a tuple (latitude, longitude)."""
        return (float(self.latitude), float(self.longitude))
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'name': self.name,
            'latitude': float(self.latitude),
            'longitude': float(self.longitude),
            'address': self.address,
            'county': self.county,
            'state': self.state,
            'climate_zone': self.climate_zone,
            'source': self.source,
            'verified': self.verified,
            'accuracy_meters': self.accuracy_meters,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class FarmField(Base):
    """Farm field model extending locations for multiple fields per farm."""
    
    __tablename__ = 'farm_fields'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_id = Column(UUID(as_uuid=True), ForeignKey('farm_locations.id', ondelete='CASCADE'), nullable=False)
    field_name = Column(String(100), nullable=False)
    field_type = Column(String(20), default='crop')
    size_acres = Column(DECIMAL(10, 2))
    soil_type = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    location = relationship("FarmLocation", back_populates="fields")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("field_type IN ('crop', 'pasture', 'other')", name='valid_field_type'),
        CheckConstraint("size_acres IS NULL OR size_acres > 0", name='positive_size_acres'),
        Index('idx_farm_fields_location_id', 'location_id'),
        Index('idx_farm_fields_type', 'field_type'),
    )
    
    def __repr__(self):
        return f"<FarmField(id='{self.id}', name='{self.field_name}', type='{self.field_type}')>"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': str(self.id),
            'location_id': str(self.location_id),
            'field_name': self.field_name,
            'field_type': self.field_type,
            'size_acres': float(self.size_acres) if self.size_acres else None,
            'soil_type': self.soil_type,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class GeocodingCache(Base):
    """Geocoding cache model for storing API results."""
    
    __tablename__ = 'geocoding_cache'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_hash = Column(String(64), unique=True, nullable=False)
    query_text = Column(Text, nullable=False)
    result_json = Column(JSONB, nullable=False)
    provider = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Constraints
    __table_args__ = (
        Index('idx_geocoding_cache_hash', 'query_hash'),
        Index('idx_geocoding_cache_expires', 'expires_at'),
        Index('idx_geocoding_cache_provider', 'provider'),
    )
    
    def __repr__(self):
        return f"<GeocodingCache(hash='{self.query_hash[:8]}...', provider='{self.provider}')>"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': str(self.id),
            'query_hash': self.query_hash,
            'query_text': self.query_text,
            'result_json': self.result_json,
            'provider': self.provider,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
    
    @property
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return datetime.utcnow() > self.expires_at.replace(tzinfo=None)


# Export all models
__all__ = [
    'FarmLocation',
    'FarmField', 
    'GeocodingCache'
]