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
# ENHANCED CROP TAXONOMY MODELS (TICKET-005)
# ============================================================================

class CropTaxonomicHierarchy(Base):
    """Botanical taxonomic hierarchy for crops following Linnaean classification."""
    
    __tablename__ = 'crop_taxonomic_hierarchy'
    
    taxonomy_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kingdom = Column(String(50), nullable=False, default='Plantae')
    phylum = Column(String(50), nullable=False, default='Magnoliophyta')
    class_ = Column('class', String(50), nullable=False)
    order_name = Column(String(50), nullable=False)
    family = Column(String(100), nullable=False)
    genus = Column(String(100), nullable=False)
    species = Column(String(100), nullable=False)
    subspecies = Column(String(100))
    variety = Column(String(100))
    cultivar = Column(String(100))
    common_synonyms = Column(ARRAY(Text))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    crops = relationship("Crop", back_populates="taxonomic_hierarchy")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('kingdom', 'phylum', 'class', 'order_name', 'family', 'genus', 'species', 'subspecies', 'variety', 
                        name='uq_taxonomic_classification'),
        Index('idx_crop_taxonomy_family', 'family'),
        Index('idx_crop_taxonomy_genus', 'genus'),
        Index('idx_crop_taxonomy_species', 'species'),
        Index('idx_crop_taxonomy_full_name', 'genus', 'species'),
        Index('idx_crop_taxonomy_name_search', 'genus', 'species', postgresql_using='gin', 
              postgresql_ops={'genus': 'gin_trgm_ops', 'species': 'gin_trgm_ops'}),
    )
    
    def __repr__(self):
        return f"<CropTaxonomicHierarchy(genus='{self.genus}', species='{self.species}')>"


class CropAgriculturalClassification(Base):
    """Agricultural classification and characteristics for crops."""
    
    __tablename__ = 'crop_agricultural_classification'
    
    classification_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Primary agricultural categories
    crop_category = Column(String(50), nullable=False)
    crop_subcategory = Column(String(100))
    
    # Agricultural use classifications
    primary_use = Column(String(50))
    secondary_uses = Column(ARRAY(Text))
    
    # Growth characteristics
    growth_habit = Column(String(50))
    plant_type = Column(String(50))
    growth_form = Column(String(50))
    
    # Size classifications
    mature_height_min_inches = Column(Integer)
    mature_height_max_inches = Column(Integer)
    mature_width_min_inches = Column(Integer)
    mature_width_max_inches = Column(Integer)
    root_system_type = Column(String(50))
    
    # Photosynthesis and metabolic characteristics
    photosynthesis_type = Column(String(10))
    nitrogen_fixing = Column(Boolean, default=False)
    mycorrhizal_associations = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    crops = relationship("Crop", back_populates="agricultural_classification")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("crop_category IN ('grain', 'oilseed', 'forage', 'vegetable', 'fruit', 'specialty', 'legume', 'cereal', 'root_crop', 'leafy_green', 'herb_spice', 'fiber', 'sugar_crop', 'cover_crop', 'ornamental', 'medicinal')", name='check_ag_crop_category'),
        CheckConstraint("primary_use IN ('food_human', 'feed_livestock', 'industrial', 'soil_improvement', 'ornamental', 'medicinal', 'fiber', 'biofuel', 'dual_purpose')", name='check_primary_use'),
        CheckConstraint("growth_habit IN ('annual', 'biennial', 'perennial', 'semi_perennial')", name='check_growth_habit'),
        CheckConstraint("plant_type IN ('grass', 'herb', 'shrub', 'tree', 'vine', 'succulent')", name='check_plant_type'),
        CheckConstraint("growth_form IN ('upright', 'spreading', 'climbing', 'trailing', 'rosette', 'bushy')", name='check_growth_form'),
        CheckConstraint("root_system_type IN ('fibrous', 'taproot', 'rhizome', 'bulb', 'tuber', 'corm')", name='check_root_system_type'),
        CheckConstraint("photosynthesis_type IN ('C3', 'C4', 'CAM')", name='check_photosynthesis_type'),
        Index('idx_ag_classification_category', 'crop_category'),
        Index('idx_ag_classification_use', 'primary_use'),
        Index('idx_ag_classification_habit', 'growth_habit'),
        Index('idx_ag_classification_type', 'plant_type'),
    )
    
    def __repr__(self):
        return f"<CropAgriculturalClassification(category='{self.crop_category}', use='{self.primary_use}')>"


class CropClimateAdaptations(Base):
    """Climate and environmental adaptations for crops."""
    
    __tablename__ = 'crop_climate_adaptations'
    
    adaptation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Temperature requirements and tolerances
    optimal_temp_min_f = Column(Float)
    optimal_temp_max_f = Column(Float)
    absolute_temp_min_f = Column(Float)
    absolute_temp_max_f = Column(Float)
    frost_tolerance = Column(String(20))
    heat_tolerance = Column(String(20))
    
    # USDA hardiness zones
    hardiness_zone_min = Column(String(5))
    hardiness_zone_max = Column(String(5))
    hardiness_zones = Column(ARRAY(Text))
    
    # Precipitation and water requirements
    annual_precipitation_min_inches = Column(Float)
    annual_precipitation_max_inches = Column(Float)
    water_requirement = Column(String(20))
    drought_tolerance = Column(String(20))
    flooding_tolerance = Column(String(20))
    
    # Seasonal adaptations
    photoperiod_sensitivity = Column(String(20))
    vernalization_requirement = Column(Boolean, default=False)
    vernalization_days = Column(Integer)
    
    # Altitude and geographic adaptations
    elevation_min_feet = Column(Integer)
    elevation_max_feet = Column(Integer)
    latitude_range_min = Column(Float)
    latitude_range_max = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    crops = relationship("Crop", back_populates="climate_adaptations")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("frost_tolerance IN ('none', 'light', 'moderate', 'heavy')", name='check_frost_tolerance'),
        CheckConstraint("heat_tolerance IN ('low', 'moderate', 'high', 'extreme')", name='check_heat_tolerance'),
        CheckConstraint("water_requirement IN ('very_low', 'low', 'moderate', 'high', 'very_high')", name='check_water_requirement'),
        CheckConstraint("drought_tolerance IN ('none', 'low', 'moderate', 'high', 'extreme')", name='check_drought_tolerance'),
        CheckConstraint("flooding_tolerance IN ('none', 'brief', 'moderate', 'extended')", name='check_flooding_tolerance'),
        CheckConstraint("photoperiod_sensitivity IN ('none', 'short_day', 'long_day', 'day_neutral')", name='check_photoperiod_sensitivity'),
        Index('idx_climate_hardiness_zones', 'hardiness_zones', postgresql_using='gin'),
        Index('idx_climate_temp_range', 'optimal_temp_min_f', 'optimal_temp_max_f'),
        Index('idx_climate_precipitation', 'annual_precipitation_min_inches', 'annual_precipitation_max_inches'),
        Index('idx_climate_drought_tolerance', 'drought_tolerance'),
    )
    
    def __repr__(self):
        return f"<CropClimateAdaptations(drought_tolerance='{self.drought_tolerance}', zones={self.hardiness_zones})>"


class CropSoilRequirements(Base):
    """Soil requirements and tolerances for crops."""
    
    __tablename__ = 'crop_soil_requirements'
    
    soil_req_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # pH requirements
    optimal_ph_min = Column(Float)
    optimal_ph_max = Column(Float)
    tolerable_ph_min = Column(Float)
    tolerable_ph_max = Column(Float)
    
    # Soil texture preferences
    preferred_textures = Column(ARRAY(Text), default=['loam', 'sandy_loam', 'clay_loam'])
    tolerable_textures = Column(ARRAY(Text))
    
    # Drainage requirements
    drainage_requirement = Column(String(30))
    drainage_tolerance = Column(ARRAY(Text))
    
    # Soil chemical tolerances
    salinity_tolerance = Column(String(20))
    alkalinity_tolerance = Column(String(20))
    acidity_tolerance = Column(String(20))
    
    # Nutrient preferences
    nitrogen_requirement = Column(String(20))
    phosphorus_requirement = Column(String(20))
    potassium_requirement = Column(String(20))
    
    # Soil structure preferences
    compaction_tolerance = Column(String(20))
    organic_matter_preference = Column(String(20))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    crops = relationship("Crop", back_populates="soil_requirements")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("optimal_ph_min >= 3.0 AND optimal_ph_min <= 10.0", name='check_optimal_ph_min'),
        CheckConstraint("optimal_ph_max >= 3.0 AND optimal_ph_max <= 10.0", name='check_optimal_ph_max'),
        CheckConstraint("tolerable_ph_min >= 3.0 AND tolerable_ph_min <= 10.0", name='check_tolerable_ph_min'),
        CheckConstraint("tolerable_ph_max >= 3.0 AND tolerable_ph_max <= 10.0", name='check_tolerable_ph_max'),
        CheckConstraint("optimal_ph_min <= optimal_ph_max", name='check_optimal_ph_range'),
        CheckConstraint("tolerable_ph_min <= tolerable_ph_max", name='check_tolerable_ph_range'),
        CheckConstraint("drainage_requirement IN ('well_drained', 'moderately_well_drained', 'somewhat_poorly_drained', 'poorly_drained', 'very_poorly_drained', 'excessive_drained')", name='check_drainage_requirement'),
        CheckConstraint("salinity_tolerance IN ('none', 'low', 'moderate', 'high')", name='check_salinity_tolerance'),
        CheckConstraint("alkalinity_tolerance IN ('none', 'low', 'moderate', 'high')", name='check_alkalinity_tolerance'),
        CheckConstraint("acidity_tolerance IN ('none', 'low', 'moderate', 'high')", name='check_acidity_tolerance'),
        CheckConstraint("nitrogen_requirement IN ('very_low', 'low', 'moderate', 'high', 'very_high')", name='check_nitrogen_requirement'),
        CheckConstraint("phosphorus_requirement IN ('very_low', 'low', 'moderate', 'high', 'very_high')", name='check_phosphorus_requirement'),
        CheckConstraint("potassium_requirement IN ('very_low', 'low', 'moderate', 'high', 'very_high')", name='check_potassium_requirement'),
        CheckConstraint("compaction_tolerance IN ('none', 'low', 'moderate', 'high')", name='check_compaction_tolerance'),
        CheckConstraint("organic_matter_preference IN ('low', 'moderate', 'high', 'very_high')", name='check_organic_matter_preference'),
        Index('idx_soil_ph_range', 'optimal_ph_min', 'optimal_ph_max'),
        Index('idx_soil_drainage', 'drainage_requirement'),
        Index('idx_soil_textures', 'preferred_textures', postgresql_using='gin'),
    )
    
    def __repr__(self):
        return f"<CropSoilRequirements(ph_range={self.optimal_ph_min}-{self.optimal_ph_max}, drainage='{self.drainage_requirement}')>"


class CropNutritionalProfiles(Base):
    """Nutritional and composition data for crops."""
    
    __tablename__ = 'crop_nutritional_profiles'
    
    nutrition_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Macronutrients (per 100g fresh weight)
    calories_per_100g = Column(Float)
    protein_g_per_100g = Column(Float)
    carbohydrates_g_per_100g = Column(Float)
    fiber_g_per_100g = Column(Float)
    fat_g_per_100g = Column(Float)
    sugar_g_per_100g = Column(Float)
    
    # Minerals (mg per 100g unless specified)
    calcium_mg = Column(Float)
    iron_mg = Column(Float)
    magnesium_mg = Column(Float)
    phosphorus_mg = Column(Float)
    potassium_mg = Column(Float)
    sodium_mg = Column(Float)
    zinc_mg = Column(Float)
    
    # Vitamins
    vitamin_c_mg = Column(Float)
    vitamin_a_iu = Column(Integer)
    vitamin_k_mcg = Column(Float)
    folate_mcg = Column(Float)
    
    # Specialized compounds
    antioxidant_capacity_orac = Column(Integer)
    phenolic_compounds_mg = Column(Float)
    
    # Feed value (for livestock crops)
    crude_protein_percent = Column(Float)
    digestible_energy_mcal_kg = Column(Float)
    neutral_detergent_fiber_percent = Column(Float)
    
    # Industrial/commercial values
    oil_content_percent = Column(Float)
    starch_content_percent = Column(Float)
    cellulose_content_percent = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    crops = relationship("Crop", back_populates="nutritional_profile")
    
    def __repr__(self):
        return f"<CropNutritionalProfiles(protein={self.protein_g_per_100g}g, calories={self.calories_per_100g})>"


class CropFilteringAttributes(Base):
    """Crop filtering and search attributes for advanced queries."""
    
    __tablename__ = 'crop_filtering_attributes'
    
    filter_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_id = Column(UUID(as_uuid=True), ForeignKey('crops.crop_id', ondelete='CASCADE'), nullable=False)
    
    # Seasonality attributes
    planting_season = Column(ARRAY(Text), default=['spring'])
    growing_season = Column(ARRAY(Text), default=['summer'])
    harvest_season = Column(ARRAY(Text), default=['fall'])
    
    # Agricultural system compatibility
    farming_systems = Column(ARRAY(Text), default=['conventional'])
    rotation_compatibility = Column(ARRAY(Text))
    intercropping_compatible = Column(Boolean, default=False)
    cover_crop_compatible = Column(Boolean, default=True)
    
    # Management intensity
    management_complexity = Column(String(20))
    input_requirements = Column(String(20))
    labor_requirements = Column(String(20))
    
    # Technology compatibility
    precision_ag_compatible = Column(Boolean, default=True)
    gps_guidance_recommended = Column(Boolean, default=False)
    sensor_monitoring_beneficial = Column(Boolean, default=False)
    
    # Sustainability attributes
    carbon_sequestration_potential = Column(String(20))
    biodiversity_support = Column(String(20))
    pollinator_value = Column(String(20))
    water_use_efficiency = Column(String(20))
    
    # Market and economic attributes
    market_stability = Column(String(20))
    price_premium_potential = Column(Boolean, default=False)
    value_added_opportunities = Column(ARRAY(Text))

    # Advanced filtering attributes stored as JSONB for flexibility
    pest_resistance_traits = Column(JSONB, default=dict)
    market_class_filters = Column(JSONB, default=dict)
    certification_filters = Column(JSONB, default=dict)
    seed_availability_filters = Column(JSONB, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    crop = relationship("Crop", back_populates="filtering_attributes")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("management_complexity IN ('low', 'moderate', 'high')", name='check_management_complexity'),
        CheckConstraint("input_requirements IN ('minimal', 'moderate', 'intensive')", name='check_input_requirements'),
        CheckConstraint("labor_requirements IN ('low', 'moderate', 'high')", name='check_labor_requirements'),
        CheckConstraint("carbon_sequestration_potential IN ('none', 'low', 'moderate', 'high')", name='check_carbon_sequestration'),
        CheckConstraint("biodiversity_support IN ('low', 'moderate', 'high')", name='check_biodiversity_support'),
        CheckConstraint("pollinator_value IN ('none', 'low', 'moderate', 'high')", name='check_pollinator_value'),
        CheckConstraint("water_use_efficiency IN ('poor', 'fair', 'good', 'excellent')", name='check_water_use_efficiency'),
        CheckConstraint("market_stability IN ('volatile', 'moderate', 'stable')", name='check_market_stability'),
        Index('idx_filtering_crop_id', 'crop_id'),
        Index('idx_filtering_seasons', 'planting_season', postgresql_using='gin'),
        Index('idx_filtering_systems', 'farming_systems', postgresql_using='gin'),
        Index('idx_filtering_complexity', 'management_complexity'),
    )
    
    def __repr__(self):
        return f"<CropFilteringAttributes(crop_id='{self.crop_id}', complexity='{self.management_complexity}')>"


class EnhancedCropVarieties(Base):
    """Enhanced crop varieties with detailed characteristics."""
    
    __tablename__ = 'enhanced_crop_varieties'
    
    variety_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_id = Column(UUID(as_uuid=True), ForeignKey('crops.crop_id', ondelete='CASCADE'), nullable=False)
    
    # Variety identification
    variety_name = Column(String(200), nullable=False)
    variety_code = Column(String(50))
    breeder_company = Column(String(150))
    parent_varieties = Column(ARRAY(Text))
    
    # Maturity and timing
    relative_maturity = Column(Integer)
    maturity_group = Column(String(10))
    days_to_emergence = Column(Integer)
    days_to_flowering = Column(Integer)
    days_to_physiological_maturity = Column(Integer)
    
    # Performance characteristics
    yield_potential_percentile = Column(Integer)
    yield_stability_rating = Column(Integer)
    standability_rating = Column(Integer)
    
    # Resistance and tolerance traits
    disease_resistances = Column(JSONB)
    pest_resistances = Column(JSONB)
    herbicide_tolerances = Column(ARRAY(Text))
    stress_tolerances = Column(ARRAY(Text))
    
    # Quality traits
    quality_characteristics = Column(JSONB)
    protein_content_range = Column(String(20))
    oil_content_range = Column(String(20))
    
    # Adaptation and recommendations
    adapted_regions = Column(ARRAY(Text))
    recommended_planting_populations = Column(JSONB)
    special_management_notes = Column(Text)
    
    # Commercial information
    seed_availability = Column(String(20))
    relative_seed_cost = Column(String(20))
    technology_package = Column(String(100))
    
    # Regulatory and certification
    organic_approved = Column(Boolean)
    non_gmo_certified = Column(Boolean)
    registration_year = Column(Integer)
    patent_protected = Column(Boolean, default=False)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    crop = relationship("Crop", back_populates="enhanced_varieties")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("yield_potential_percentile >= 0 AND yield_potential_percentile <= 100", name='check_yield_percentile'),
        CheckConstraint("yield_stability_rating >= 1 AND yield_stability_rating <= 10", name='check_yield_stability'),
        CheckConstraint("standability_rating >= 1 AND standability_rating <= 10", name='check_standability'),
        CheckConstraint("seed_availability IN ('widely_available', 'limited', 'specialty', 'research_only')", name='check_seed_availability'),
        CheckConstraint("relative_seed_cost IN ('low', 'moderate', 'high', 'premium')", name='check_seed_cost'),
        UniqueConstraint('crop_id', 'variety_name', 'breeder_company', name='uq_crop_variety_company'),
        Index('idx_enhanced_varieties_crop_id', 'crop_id'),
        Index('idx_enhanced_varieties_maturity', 'relative_maturity'),
        Index('idx_enhanced_varieties_active', 'is_active'),
        Index('idx_enhanced_varieties_regions', 'adapted_regions', postgresql_using='gin'),
        Index('idx_enhanced_varieties_name_search', 'variety_name', postgresql_using='gin', 
              postgresql_ops={'variety_name': 'gin_trgm_ops'}),
    )
    
    def __repr__(self):
        return f"<EnhancedCropVarieties(name='{self.variety_name}', company='{self.breeder_company}')>"


class CropRegionalAdaptations(Base):
    """Regional crop adaptations and recommendations."""
    
    __tablename__ = 'crop_regional_adaptations'
    
    adaptation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_id = Column(UUID(as_uuid=True), ForeignKey('crops.crop_id', ondelete='CASCADE'), nullable=False)
    
    # Geographic scope
    region_name = Column(String(100), nullable=False)
    region_type = Column(String(50))
    country_code = Column(String(3), default='USA')
    
    # Geographic boundaries
    region_bounds = Column(Geography('POLYGON', srid=4326))
    latitude_range_min = Column(Float)
    latitude_range_max = Column(Float)
    longitude_range_min = Column(Float)
    longitude_range_max = Column(Float)
    
    # Adaptation ratings
    adaptation_score = Column(Integer)
    production_potential = Column(String(20))
    risk_level = Column(String(20))
    
    # Regional characteristics
    typical_planting_dates = Column(JSONB)
    typical_harvest_dates = Column(JSONB)
    common_varieties = Column(ARRAY(Text))
    regional_challenges = Column(ARRAY(Text))
    management_considerations = Column(ARRAY(Text))
    
    # Economic factors
    market_demand = Column(String(20))
    infrastructure_support = Column(String(20))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    crop = relationship("Crop", back_populates="regional_adaptations")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("region_type IN ('state', 'multi_state', 'county', 'climate_zone', 'ecoregion', 'custom')", name='check_region_type'),
        CheckConstraint("adaptation_score >= 1 AND adaptation_score <= 10", name='check_adaptation_score'),
        CheckConstraint("production_potential IN ('poor', 'fair', 'good', 'excellent')", name='check_production_potential'),
        CheckConstraint("risk_level IN ('very_low', 'low', 'moderate', 'high', 'very_high')", name='check_risk_level'),
        CheckConstraint("market_demand IN ('very_low', 'low', 'moderate', 'high', 'very_high')", name='check_market_demand'),
        CheckConstraint("infrastructure_support IN ('poor', 'fair', 'good', 'excellent')", name='check_infrastructure_support'),
        Index('idx_regional_adaptations_crop_id', 'crop_id'),
        Index('idx_regional_adaptations_region', 'region_name', 'region_type'),
        Index('idx_regional_adaptations_bounds', 'region_bounds', postgresql_using='gist'),
        Index('idx_regional_adaptations_score', 'adaptation_score'),
    )
    
    def __repr__(self):
        return f"<CropRegionalAdaptations(crop_id='{self.crop_id}', region='{self.region_name}', score={self.adaptation_score})>"


# ============================================================================
# ENHANCED CROP MODEL WITH TAXONOMY RELATIONSHIPS
# ============================================================================

class Crop(Base):
    """Enhanced crop type model with comprehensive taxonomic relationships."""
    
    __tablename__ = 'crops'
    
    crop_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    crop_name = Column(String(100), unique=True, nullable=False)
    scientific_name = Column(String(150))
    crop_category = Column(String(50))
    crop_family = Column(String(100))
    
    # Enhanced classification fields
    crop_code = Column(String(20), unique=True)
    fao_crop_code = Column(String(10))
    usda_crop_code = Column(String(10))
    search_keywords = Column(ARRAY(Text))
    tags = Column(ARRAY(Text))
    is_cover_crop = Column(Boolean, default=False)
    is_companion_crop = Column(Boolean, default=False)
    crop_status = Column(String(20), default='active')
    
    # Legacy fields (kept for backward compatibility)
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
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Foreign keys to enhanced taxonomy tables
    taxonomy_id = Column(UUID(as_uuid=True), ForeignKey('crop_taxonomic_hierarchy.taxonomy_id'))
    agricultural_classification_id = Column(UUID(as_uuid=True), ForeignKey('crop_agricultural_classification.classification_id'))
    climate_adaptation_id = Column(UUID(as_uuid=True), ForeignKey('crop_climate_adaptations.adaptation_id'))
    soil_requirements_id = Column(UUID(as_uuid=True), ForeignKey('crop_soil_requirements.soil_req_id'))
    nutritional_profile_id = Column(UUID(as_uuid=True), ForeignKey('crop_nutritional_profiles.nutrition_id'))
    filtering_attributes_id = Column(UUID(as_uuid=True), ForeignKey('crop_filtering_attributes.filter_id'))
    
    # Relationships to enhanced taxonomy tables
    taxonomic_hierarchy = relationship("CropTaxonomicHierarchy", back_populates="crops")
    agricultural_classification = relationship("CropAgriculturalClassification", back_populates="crops")
    climate_adaptations = relationship("CropClimateAdaptations", back_populates="crops")
    soil_requirements = relationship("CropSoilRequirements", back_populates="crops")
    nutritional_profile = relationship("CropNutritionalProfiles", back_populates="crops")
    filtering_attributes = relationship("CropFilteringAttributes", back_populates="crop", uselist=False)
    
    # Relationships to varieties and history
    varieties = relationship("CropVariety", back_populates="crop", cascade="all, delete-orphan")
    enhanced_varieties = relationship("EnhancedCropVarieties", back_populates="crop", cascade="all, delete-orphan")
    regional_adaptations = relationship("CropRegionalAdaptations", back_populates="crop", cascade="all, delete-orphan")
    crop_history = relationship("CropHistory", back_populates="crop")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("crop_category IN ('grain', 'oilseed', 'forage', 'vegetable', 'fruit', 'specialty')", name='check_crop_category'),
        CheckConstraint("crop_status IN ('active', 'deprecated', 'experimental', 'regional')", name='check_crop_status'),
        CheckConstraint("drought_tolerance IN ('low', 'moderate', 'high')", name='check_drought_tolerance'),
        CheckConstraint("cold_tolerance IN ('low', 'moderate', 'high')", name='check_cold_tolerance'),
        Index('idx_crops_name_trgm', 'crop_name', postgresql_using='gin', postgresql_ops={'crop_name': 'gin_trgm_ops'}),
        Index('idx_crops_taxonomy_id', 'taxonomy_id'),
        Index('idx_crops_agricultural_classification', 'agricultural_classification_id'),
        Index('idx_crops_climate_adaptation', 'climate_adaptation_id'),
        Index('idx_crops_filtering_attributes', 'filtering_attributes_id'),
        Index('idx_crops_code', 'crop_code'),
        Index('idx_crops_tags', 'tags', postgresql_using='gin'),
        Index('idx_crops_keywords', 'search_keywords', postgresql_using='gin'),
        Index('idx_crops_cover_crop', 'is_cover_crop'),
        Index('idx_crops_status', 'crop_status'),
    )
    
    def __repr__(self):
        return f"<Crop(name='{self.crop_name}', category='{self.crop_category}', status='{self.crop_status}')>"


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
    # Enhanced Crop Taxonomy Models
    'CropTaxonomicHierarchy', 'CropAgriculturalClassification', 'CropClimateAdaptations',
    'CropSoilRequirements', 'CropNutritionalProfiles', 'CropFilteringAttributes',
    'EnhancedCropVarieties', 'CropRegionalAdaptations',
    'FertilizerProduct', 'FertilizerApplication',
    'QuestionType', 'Recommendation',
    'EquipmentType', 'FarmEquipment',
    'ClimateZoneData', 'HistoricalClimatePatterns', 'ClimateZoneCache',
    'WeatherStation', 'WeatherData',
    'create_all_tables', 'drop_all_tables'
]
