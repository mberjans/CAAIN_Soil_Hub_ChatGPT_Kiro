"""
AFAS SQLAlchemy Models
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024
"""

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Date, Text, 
    ForeignKey, CheckConstraint, UniqueConstraint, Index, ARRAY, JSON
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geography
import uuid
from datetime import datetime, date
from typing import Optional, List, Dict, Any

Base = declarative_base()

# ============================================================================
# USER AND AUTHENTICATION MODELS
# ============================================================================

class User(Base):
    """User model for farmers, consultants, and administrators."""
    
    __tablename__ = 'users'
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    role = Column(String(50), default='farmer', nullable=False)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    farms = relationship("Farm", back_populates="owner", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("role IN ('farmer', 'consultant', 'admin', 'expert')", name='check_user_role'),
    )
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email
    
    def __repr__(self):
        return f"<User(email='{self.email}', role='{self.role}')>"


class UserSession(Base):
    """User session model for authentication tracking."""
    
    __tablename__ = 'user_sessions'
    
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    token_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(INET)
    user_agent = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self):
        return f"<UserSession(user_id='{self.user_id}', expires_at='{self.expires_at}')>"


# ============================================================================
# FARM AND LOCATION MODELS
# ============================================================================

class Farm(Base):
    """Farm model representing a farming operation."""
    
    __tablename__ = 'farms'
    
    farm_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    farm_name = Column(String(255), nullable=False)
    farm_size_acres = Column(Float, nullable=False)
    location = Column(Geography('POINT', srid=4326), nullable=False)
    address = Column(Text)
    state = Column(String(50))
    county = Column(String(100))
    climate_zone = Column(String(20))
    usda_hardiness_zone = Column(String(10))
    elevation_feet = Column(Integer)
    irrigation_available = Column(Boolean, default=False)
    organic_certified = Column(Boolean, default=False)
    certification_body = Column(String(100))
    certification_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="farms")
    fields = relationship("Field", back_populates="farm", cascade="all, delete-orphan")
    equipment = relationship("FarmEquipment", back_populates="farm", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="farm")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("farm_size_acres > 0", name='check_positive_farm_size'),
        Index('idx_farms_location', 'location', postgresql_using='gist'),
    )
    
    def __repr__(self):
        return f"<Farm(name='{self.farm_name}', size={self.farm_size_acres} acres)>"


class Field(Base):
    """Field model representing individual fields within a farm."""
    
    __tablename__ = 'fields'
    
    field_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id = Column(UUID(as_uuid=True), ForeignKey('farms.farm_id', ondelete='CASCADE'), nullable=False)
    field_name = Column(String(255), nullable=False)
    field_size_acres = Column(Float, nullable=False)
    field_boundary = Column(Geography('POLYGON', srid=4326))
    soil_type = Column(String(100))
    drainage_class = Column(String(50))
    slope_percent = Column(Float)
    erosion_risk = Column(String(20))
    conservation_practices = Column(ARRAY(Text))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    farm = relationship("Farm", back_populates="fields")
    soil_tests = relationship("SoilTest", back_populates="field", cascade="all, delete-orphan")
    crop_history = relationship("CropHistory", back_populates="field", cascade="all, delete-orphan")
    fertilizer_applications = relationship("FertilizerApplication", back_populates="field", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("field_size_acres > 0", name='check_positive_field_size'),
        CheckConstraint("drainage_class IN ('well_drained', 'moderately_well_drained', 'somewhat_poorly_drained', 'poorly_drained', 'very_poorly_drained')", name='check_drainage_class'),
        CheckConstraint("erosion_risk IN ('low', 'moderate', 'high', 'severe')", name='check_erosion_risk'),
        Index('idx_fields_boundary', 'field_boundary', postgresql_using='gist'),
    )
    
    def __repr__(self):
        return f"<Field(name='{self.field_name}', size={self.field_size_acres} acres)>"


# ============================================================================
# SOIL DATA MODELS
# ============================================================================

class SoilTest(Base):
    """Soil test results model."""
    
    __tablename__ = 'soil_tests'
    
    test_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(UUID(as_uuid=True), ForeignKey('fields.field_id', ondelete='CASCADE'), nullable=False)
    test_date = Column(Date, nullable=False)
    lab_name = Column(String(255))
    lab_id = Column(String(100))
    sampling_depth_inches = Column(Integer, default=6)
    sample_count = Column(Integer, default=1)
    
    # Primary nutrients
    ph = Column(Float, nullable=False)
    organic_matter_percent = Column(Float)
    phosphorus_ppm = Column(Float)
    potassium_ppm = Column(Float)
    nitrogen_ppm = Column(Float)
    
    # Secondary nutrients
    calcium_ppm = Column(Float)
    magnesium_ppm = Column(Float)
    sulfur_ppm = Column(Float)
    
    # Micronutrients
    iron_ppm = Column(Float)
    manganese_ppm = Column(Float)
    zinc_ppm = Column(Float)
    copper_ppm = Column(Float)
    boron_ppm = Column(Float)
    molybdenum_ppm = Column(Float)
    
    # Soil properties
    cec_meq_per_100g = Column(Float)
    base_saturation_percent = Column(Float)
    soil_texture = Column(String(50))
    sand_percent = Column(Float)
    silt_percent = Column(Float)
    clay_percent = Column(Float)
    bulk_density = Column(Float)
    
    # Test method information
    extraction_method = Column(String(100), default='Mehlich-3')
    test_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    field = relationship("Field", back_populates="soil_tests")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("ph >= 3.0 AND ph <= 10.0", name='check_ph_range'),
        CheckConstraint("organic_matter_percent >= 0 AND organic_matter_percent <= 15", name='check_om_range'),
        CheckConstraint("phosphorus_ppm >= 0 AND phosphorus_ppm <= 200", name='check_p_range'),
        CheckConstraint("potassium_ppm >= 0 AND potassium_ppm <= 800", name='check_k_range'),
        CheckConstraint("nitrogen_ppm >= 0 AND nitrogen_ppm <= 100", name='check_n_range'),
        CheckConstraint("cec_meq_per_100g >= 0 AND cec_meq_per_100g <= 50", name='check_cec_range'),
        Index('idx_soil_tests_field_date', 'field_id', 'test_date'),
    )
    
    def __repr__(self):
        return f"<SoilTest(field_id='{self.field_id}', date='{self.test_date}', pH={self.ph})>"


# ============================================================================
# CROP AND ROTATION MODELS
# ============================================================================

class Crop(Base):
    """Crop type model with characteristics and requirements."""
    
    __tablename__ = 'crops'
    
    crop_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_name = Column(String(100), unique=True, nullable=False)
    scientific_name = Column(String(150))
    crop_category = Column(String(50))
    crop_family = Column(String(100))
    nitrogen_fixing = Column(Boolean, default=False)
    typical_yield_range_min = Column(Float)
    typical_yield_range_max = Column(Float)
    yield_units = Column(String(20), default='bu/acre')
    growing_degree_days = Column(Integer)
    maturity_days_min = Column(Integer)
    maturity_days_max = Column(Integer)
    optimal_ph_min = Column(Float)
    optimal_ph_max = Column(Float)
    drought_tolerance = Column(String(20))
    cold_tolerance = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    varieties = relationship("CropVariety", back_populates="crop", cascade="all, delete-orphan")
    crop_history = relationship("CropHistory", back_populates="crop")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("crop_category IN ('grain', 'oilseed', 'forage', 'vegetable', 'fruit', 'specialty')", name='check_crop_category'),
        CheckConstraint("drought_tolerance IN ('low', 'moderate', 'high')", name='check_drought_tolerance'),
        CheckConstraint("cold_tolerance IN ('low', 'moderate', 'high')", name='check_cold_tolerance'),
        Index('idx_crops_name_trgm', 'crop_name', postgresql_using='gin', postgresql_ops={'crop_name': 'gin_trgm_ops'}),
    )
    
    def __repr__(self):
        return f"<Crop(name='{self.crop_name}', category='{self.crop_category}')>"


class CropVariety(Base):
    """Crop variety model with specific characteristics."""
    
    __tablename__ = 'crop_varieties'
    
    variety_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_id = Column(UUID(as_uuid=True), ForeignKey('crops.crop_id', ondelete='CASCADE'), nullable=False)
    variety_name = Column(String(150), nullable=False)
    company = Column(String(100))
    maturity_days = Column(Integer)
    yield_potential = Column(Float)
    disease_resistance = Column(ARRAY(Text))
    herbicide_tolerance = Column(ARRAY(Text))
    special_traits = Column(ARRAY(Text))
    regional_adaptation = Column(ARRAY(Text))
    release_year = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    crop = relationship("Crop", back_populates="varieties")
    
    def __repr__(self):
        return f"<CropVariety(name='{self.variety_name}', company='{self.company}')>"


class CropHistory(Base):
    """Crop history model tracking what was grown in each field by year."""
    
    __tablename__ = 'crop_history'
    
    history_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(UUID(as_uuid=True), ForeignKey('fields.field_id', ondelete='CASCADE'), nullable=False)
    crop_year = Column(Integer, nullable=False)
    crop_id = Column(UUID(as_uuid=True), ForeignKey('crops.crop_id'), nullable=False)
    variety_id = Column(UUID(as_uuid=True), ForeignKey('crop_varieties.variety_id'))
    planting_date = Column(Date)
    harvest_date = Column(Date)
    actual_yield = Column(Float)
    yield_units = Column(String(20), default='bu/acre')
    tillage_system = Column(String(50))
    cover_crop_used = Column(Boolean, default=False)
    cover_crop_species = Column(String(100))
    irrigation_used = Column(Boolean, default=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    field = relationship("Field", back_populates="crop_history")
    crop = relationship("Crop", back_populates="crop_history")
    variety = relationship("CropVariety")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('field_id', 'crop_year', name='uq_field_crop_year'),
        CheckConstraint("tillage_system IN ('conventional', 'reduced_till', 'no_till', 'strip_till')", name='check_tillage_system'),
        Index('idx_crop_history_field_year', 'field_id', 'crop_year'),
    )
    
    def __repr__(self):
        return f"<CropHistory(field_id='{self.field_id}', year={self.crop_year}, yield={self.actual_yield})>"


# ============================================================================
# FERTILIZER AND NUTRIENT MANAGEMENT MODELS
# ============================================================================

class FertilizerProduct(Base):
    """Fertilizer product model with nutrient analysis."""
    
    __tablename__ = 'fertilizer_products'
    
    product_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_name = Column(String(255), nullable=False)
    manufacturer = Column(String(150))
    product_type = Column(String(50))
    
    # Nutrient analysis (guaranteed analysis)
    nitrogen_percent = Column(Float, default=0)
    phosphorus_percent = Column(Float, default=0)  # P2O5
    potassium_percent = Column(Float, default=0)   # K2O
    sulfur_percent = Column(Float, default=0)
    calcium_percent = Column(Float, default=0)
    magnesium_percent = Column(Float, default=0)
    
    # Micronutrients
    iron_percent = Column(Float, default=0)
    manganese_percent = Column(Float, default=0)
    zinc_percent = Column(Float, default=0)
    copper_percent = Column(Float, default=0)
    boron_percent = Column(Float, default=0)
    
    # Physical properties
    bulk_density = Column(Float)  # lbs/cubic foot
    particle_size = Column(String(50))
    application_method = Column(ARRAY(Text))
    
    # Economic data
    typical_price_per_ton = Column(Float)
    price_currency = Column(String(3), default='USD')
    price_date = Column(Date)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    applications = relationship("FertilizerApplication", back_populates="product")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("product_type IN ('synthetic', 'organic', 'slow_release', 'liquid', 'granular')", name='check_product_type'),
        Index('idx_fertilizer_products_name_trgm', 'product_name', postgresql_using='gin', postgresql_ops={'product_name': 'gin_trgm_ops'}),
    )
    
    def __repr__(self):
        return f"<FertilizerProduct(name='{self.product_name}', type='{self.product_type}')>"


class FertilizerApplication(Base):
    """Fertilizer application record model."""
    
    __tablename__ = 'fertilizer_applications'
    
    application_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    field_id = Column(UUID(as_uuid=True), ForeignKey('fields.field_id', ondelete='CASCADE'), nullable=False)
    crop_year = Column(Integer, nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey('fertilizer_products.product_id'))
    custom_product_name = Column(String(255))  # For products not in database
    
    application_date = Column(Date, nullable=False)
    application_method = Column(String(50))
    application_timing = Column(String(50))
    
    # Application rates
    rate_lbs_per_acre = Column(Float, nullable=False)
    actual_n_lbs_per_acre = Column(Float)
    actual_p_lbs_per_acre = Column(Float)
    actual_k_lbs_per_acre = Column(Float)
    
    # Application details
    incorporation_method = Column(String(50))
    incorporation_depth_inches = Column(Float)
    weather_conditions = Column(Text)
    soil_conditions = Column(Text)
    
    # Economic data
    cost_per_acre = Column(Float)
    total_cost = Column(Float)
    
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    field = relationship("Field", back_populates="fertilizer_applications")
    product = relationship("FertilizerProduct", back_populates="applications")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("rate_lbs_per_acre > 0", name='check_positive_rate'),
        CheckConstraint("application_method IN ('broadcast', 'banded', 'side_dress', 'foliar', 'fertigation', 'injection')", name='check_application_method'),
        CheckConstraint("application_timing IN ('pre_plant', 'at_plant', 'post_emerge', 'side_dress', 'split_application')", name='check_application_timing'),
        Index('idx_fertilizer_applications_field_year', 'field_id', 'crop_year'),
    )
    
    def __repr__(self):
        return f"<FertilizerApplication(field_id='{self.field_id}', date='{self.application_date}', rate={self.rate_lbs_per_acre})>"


# ============================================================================
# RECOMMENDATION SYSTEM MODELS
# ============================================================================

class QuestionType(Base):
    """Question type model for the 20 key farmer questions."""
    
    __tablename__ = 'question_types'
    
    question_id = Column(Integer, primary_key=True)
    question_text = Column(Text, nullable=False)
    question_category = Column(String(100), nullable=False)
    priority_level = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    recommendations = relationship("Recommendation", back_populates="question_type")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("priority_level BETWEEN 1 AND 5", name='check_priority_level'),
    )
    
    def __repr__(self):
        return f"<QuestionType(id={self.question_id}, category='{self.question_category}')>"


class Recommendation(Base):
    """Recommendation model storing AI-generated agricultural advice."""
    
    __tablename__ = 'recommendations'
    
    recommendation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    farm_id = Column(UUID(as_uuid=True), ForeignKey('farms.farm_id', ondelete='CASCADE'))
    field_id = Column(UUID(as_uuid=True), ForeignKey('fields.field_id', ondelete='CASCADE'))
    question_id = Column(Integer, ForeignKey('question_types.question_id'))
    
    # Request context
    request_data = Column(JSONB, nullable=False)  # Original request parameters
    location_data = Column(JSONB)  # Location context used
    soil_data = Column(JSONB)      # Soil data used
    crop_data = Column(JSONB)      # Crop data used
    
    # Recommendation results
    recommendations = Column(JSONB, nullable=False)  # Array of recommendation items
    overall_confidence = Column(Float, nullable=False)
    confidence_factors = Column(JSONB)  # Breakdown of confidence factors
    
    # Metadata
    processing_time_ms = Column(Integer)
    data_sources_used = Column(ARRAY(Text))  # Array of data sources
    agricultural_sources = Column(ARRAY(Text))  # Array of agricultural references
    warnings = Column(ARRAY(Text))  # Array of warnings
    
    # User interaction
    user_feedback = Column(Integer)  # 1-5 rating
    feedback_text = Column(Text)
    implemented = Column(Boolean)
    implementation_notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="recommendations")
    farm = relationship("Farm", back_populates="recommendations")
    field = relationship("Field")
    question_type = relationship("QuestionType", back_populates="recommendations")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("overall_confidence BETWEEN 0 AND 1", name='check_confidence_range'),
        CheckConstraint("user_feedback BETWEEN 1 AND 5", name='check_feedback_range'),
        Index('idx_recommendations_user_created', 'user_id', 'created_at'),
        Index('idx_recommendations_confidence', 'overall_confidence'),
    )
    
    def __repr__(self):
        return f"<Recommendation(user_id='{self.user_id}', confidence={self.overall_confidence})>"


# ============================================================================
# EQUIPMENT AND FARM MANAGEMENT MODELS
# ============================================================================

class EquipmentType(Base):
    """Equipment type model for categorizing farm equipment."""
    
    __tablename__ = 'equipment_types'
    
    equipment_type_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipment_name = Column(String(150), nullable=False)
    equipment_category = Column(String(50))
    typical_capacity = Column(String(100))
    power_requirements = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    farm_equipment = relationship("FarmEquipment", back_populates="equipment_type")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("equipment_category IN ('tillage', 'planting', 'spraying', 'harvesting', 'fertilizer', 'other')", name='check_equipment_category'),
    )
    
    def __repr__(self):
        return f"<EquipmentType(name='{self.equipment_name}', category='{self.equipment_category}')>"


class FarmEquipment(Base):
    """Farm equipment model tracking equipment inventory."""
    
    __tablename__ = 'farm_equipment'
    
    equipment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id = Column(UUID(as_uuid=True), ForeignKey('farms.farm_id', ondelete='CASCADE'), nullable=False)
    equipment_type_id = Column(UUID(as_uuid=True), ForeignKey('equipment_types.equipment_type_id'))
    custom_equipment_name = Column(String(150))  # For equipment not in types table
    manufacturer = Column(String(100))
    model = Column(String(100))
    year_manufactured = Column(Integer)
    condition = Column(String(20))
    capacity = Column(String(100))
    is_operational = Column(Boolean, default=True)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    farm = relationship("Farm", back_populates="equipment")
    equipment_type = relationship("EquipmentType", back_populates="farm_equipment")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("condition IN ('excellent', 'good', 'fair', 'poor')", name='check_equipment_condition'),
    )
    
    def __repr__(self):
        return f"<FarmEquipment(farm_id='{self.farm_id}', name='{self.custom_equipment_name or 'N/A'}')>"


# ============================================================================
# CLIMATE ZONE DATA MODELS
# ============================================================================

class ClimateZoneData(Base):
    """Climate zone data model for storing detailed climate information."""
    
    __tablename__ = 'climate_zone_data'
    
    climate_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # USDA Hardiness Zone Information
    usda_zone = Column(String(10))
    usda_zone_confidence = Column(Float)
    
    # Köppen Climate Classification
    koppen_classification = Column(String(10))
    koppen_description = Column(Text)
    
    # Temperature Profile (Fahrenheit)
    average_min_temp_f = Column(Float)
    average_max_temp_f = Column(Float)
    extreme_min_temp_f = Column(Float)
    extreme_max_temp_f = Column(Float)
    
    # Precipitation Profile
    annual_precipitation_inches = Column(Float)
    wet_season_months = Column(ARRAY(Integer))
    dry_season_months = Column(ARRAY(Integer))
    
    # Growing Season Information
    growing_season_length = Column(Integer)
    last_frost_date = Column(Date)
    first_frost_date = Column(Date)
    frost_free_days = Column(Integer)
    
    # Agricultural Suitability
    agricultural_suitability_score = Column(Float)
    agricultural_category = Column(String(50))
    limiting_factors = Column(ARRAY(Text))
    recommendations = Column(ARRAY(Text))
    
    # Data Quality and Sources
    data_sources = Column(ARRAY(Text))
    historical_years_analyzed = Column(Integer)
    data_quality_score = Column(Float)
    
    # Timestamps
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    cache_expires_at = Column(DateTime(timezone=True))
    
    # Constraints
    __table_args__ = (
        CheckConstraint("latitude >= -90 AND latitude <= 90", name='check_latitude_range'),
        CheckConstraint("longitude >= -180 AND longitude <= 180", name='check_longitude_range'),
        CheckConstraint("usda_zone_confidence >= 0 AND usda_zone_confidence <= 1", name='check_usda_confidence'),
        CheckConstraint("agricultural_suitability_score >= 0 AND agricultural_suitability_score <= 1", name='check_ag_suitability'),
        CheckConstraint("data_quality_score >= 0 AND data_quality_score <= 1", name='check_data_quality'),
        CheckConstraint("growing_season_length >= 0 AND growing_season_length <= 365", name='check_growing_season'),
        CheckConstraint("frost_free_days >= 0 AND frost_free_days <= 365", name='check_frost_free_days'),
        Index('idx_climate_zone_location', 'latitude', 'longitude'),
        Index('idx_climate_zone_usda', 'usda_zone'),
        Index('idx_climate_zone_koppen', 'koppen_classification'),
    )
    
    def __repr__(self):
        return f"<ClimateZoneData(lat={self.latitude}, lon={self.longitude}, usda_zone='{self.usda_zone}')>"


class HistoricalClimatePatterns(Base):
    """Historical climate patterns model for storing historical weather analysis."""
    
    __tablename__ = 'historical_climate_patterns'
    
    pattern_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    climate_id = Column(UUID(as_uuid=True), ForeignKey('climate_zone_data.climate_id', ondelete='CASCADE'))
    
    # Monthly Temperature Arrays (12 elements, Jan-Dec, Fahrenheit)
    monthly_avg_temps = Column(ARRAY(Float))  # Average monthly temperatures
    monthly_min_temps = Column(ARRAY(Float))  # Monthly minimum temperatures
    monthly_max_temps = Column(ARRAY(Float))  # Monthly maximum temperatures
    
    # Monthly Precipitation Array (12 elements, Jan-Dec, inches)
    monthly_precipitation = Column(ARRAY(Float))
    
    # Monthly Growing Degree Days Arrays (12 elements, Jan-Dec)
    monthly_gdd_base_50 = Column(ARRAY(Float))  # GDD base 50°F
    monthly_gdd_base_86 = Column(ARRAY(Float))  # GDD base 86°F
    
    # Climate Event Frequencies
    heat_wave_frequency = Column(Float)  # Heat waves per year
    cold_snap_frequency = Column(Float)  # Cold snaps per year
    drought_frequency = Column(Float)    # Drought events per year
    
    # Analysis Period Information
    years_analyzed = Column(Integer)     # Number of years in analysis
    data_start_year = Column(Integer)    # First year of data
    data_end_year = Column(Integer)      # Last year of data
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    climate_zone = relationship("ClimateZoneData")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("years_analyzed > 0", name='check_years_analyzed'),
        CheckConstraint("data_start_year >= 1880 AND data_start_year <= 2030", name='check_start_year'),
        CheckConstraint("data_end_year >= 1880 AND data_end_year <= 2030", name='check_end_year'),
        CheckConstraint("data_end_year >= data_start_year", name='check_year_order'),
        CheckConstraint("heat_wave_frequency >= 0", name='check_heat_wave_freq'),
        CheckConstraint("cold_snap_frequency >= 0", name='check_cold_snap_freq'),
        CheckConstraint("drought_frequency >= 0", name='check_drought_freq'),
        Index('idx_historical_patterns_climate', 'climate_id'),
    )
    
    def __repr__(self):
        return f"<HistoricalClimatePatterns(climate_id='{self.climate_id}', years={self.years_analyzed})>"


class ClimateZoneCache(Base):
    """Climate zone cache model for storing API response cache."""
    
    __tablename__ = 'climate_zone_cache'
    
    cache_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_hash = Column(String(255), unique=True, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Cached Response Data
    climate_data_json = Column(JSONB, nullable=False)
    weather_service_response = Column(JSONB)
    
    # Cache Metadata
    access_count = Column(Integer, default=0)
    data_source = Column(String(100))
    generation_time_ms = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_accessed = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("latitude >= -90 AND latitude <= 90", name='check_cache_latitude_range'),
        CheckConstraint("longitude >= -180 AND longitude <= 180", name='check_cache_longitude_range'),
        CheckConstraint("access_count >= 0", name='check_cache_access_count'),
        CheckConstraint("generation_time_ms >= 0", name='check_generation_time'),
        Index('idx_climate_cache_location', 'latitude', 'longitude'),
        Index('idx_climate_cache_expires', 'expires_at'),
        Index('idx_climate_cache_hash', 'location_hash'),
    )
    
    def __repr__(self):
        return f"<ClimateZoneCache(lat={self.latitude}, lon={self.longitude}, accesses={self.access_count})>"


# ============================================================================
# WEATHER AND ENVIRONMENTAL DATA MODELS
# ============================================================================

class WeatherStation(Base):
    """Weather station model for tracking data sources."""
    
    __tablename__ = 'weather_stations'
    
    station_id = Column(String(50), primary_key=True)
    station_name = Column(String(255), nullable=False)
    location = Column(Geography('POINT', srid=4326), nullable=False)
    elevation_feet = Column(Integer)
    data_provider = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    weather_data = relationship("WeatherData", back_populates="station")
    
    # Constraints
    __table_args__ = (
        Index('idx_weather_stations_location', 'location', postgresql_using='gist'),
    )
    
    def __repr__(self):
        return f"<WeatherStation(id='{self.station_id}', name='{self.station_name}')>"


class WeatherData(Base):
    """Weather data model for storing historical and current weather information."""
    
    __tablename__ = 'weather_data'
    
    weather_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(String(50), ForeignKey('weather_stations.station_id'))
    location = Column(Geography('POINT', srid=4326))  # For location-specific data
    observation_date = Column(Date, nullable=False)
    
    # Temperature data (Fahrenheit)
    temp_max_f = Column(Float)
    temp_min_f = Column(Float)
    temp_avg_f = Column(Float)
    
    # Precipitation (inches)
    precipitation_inches = Column(Float)
    
    # Other weather parameters
    humidity_percent = Column(Float)
    wind_speed_mph = Column(Float)
    wind_direction_degrees = Column(Integer)
    solar_radiation = Column(Float)
    
    # Growing degree days
    gdd_base_50 = Column(Float)
    gdd_base_86 = Column(Float)
    
    data_source = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    station = relationship("WeatherStation", back_populates="weather_data")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('station_id', 'observation_date', name='uq_station_date'),
        Index('idx_weather_data_location', 'location', postgresql_using='gist'),
        Index('idx_weather_data_station_date', 'station_id', 'observation_date'),
    )
    
    def __repr__(self):
        return f"<WeatherData(station_id='{self.station_id}', date='{self.observation_date}')>"


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_all_tables(engine):
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)

def drop_all_tables(engine):
    """Drop all tables in the database."""
    Base.metadata.drop_all(bind=engine)

# Export all models for easy importing
__all__ = [
    'Base',
    'User', 'UserSession',
    'Farm', 'Field',
    'SoilTest',
    'Crop', 'CropVariety', 'CropHistory',
    'FertilizerProduct', 'FertilizerApplication',
    'QuestionType', 'Recommendation',
    'EquipmentType', 'FarmEquipment',
    'ClimateZoneData', 'HistoricalClimatePatterns', 'ClimateZoneCache',
    'WeatherStation', 'WeatherData',
    'create_all_tables', 'drop_all_tables'
]