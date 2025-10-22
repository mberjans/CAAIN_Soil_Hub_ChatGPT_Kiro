from sqlalchemy import Column, String, Integer, DECIMAL, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class FarmLocation(Base):
    """Farm location with geospatial data"""
    __tablename__ = 'farm_locations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String(200), nullable=False)
    address = Column(String(500))
    
    # PostGIS geometry column (POINT with SRID 4326 = WGS84)
    coordinates = Column(Geometry('POINT', srid=4326), nullable=False)
    
    elevation_meters = Column(Integer)
    usda_zone = Column(String(10))
    climate_zone = Column(String(50))
    county = Column(String(100))
    state = Column(String(50))
    country = Column(String(50), default='USA')
    total_acres = Column(DECIMAL(10, 2))
    is_primary = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    fields = relationship("Field", back_populates="farm_location", cascade="all, delete-orphan")


class Field(Base):
    """Individual field within a farm"""
    __tablename__ = 'fields'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_location_id = Column(UUID(as_uuid=True), ForeignKey('farm_locations.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(200), nullable=False)
    
    # PostGIS geometry column (POLYGON)
    boundary = Column(Geometry('POLYGON', srid=4326))
    
    acres = Column(DECIMAL(8, 2), nullable=False)
    soil_type = Column(String(100))
    drainage_class = Column(String(50))
    slope_percent = Column(DECIMAL(4, 1))
    irrigation_available = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    farm_location = relationship("FarmLocation", back_populates="fields")
