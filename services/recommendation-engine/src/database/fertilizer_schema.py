"""
Database Schema for Fertilizer Type Selection

SQLAlchemy models for storing fertilizer products, recommendations, and comparisons.
Implements database structure for US-006: Fertilizer Type Selection.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

Base = declarative_base()


class FertilizerProduct(Base):
    """Fertilizer product database model."""
    __tablename__ = "fertilizer_products"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    manufacturer = Column(String(100))
    
    # Fertilizer characteristics
    fertilizer_type = Column(String(20), nullable=False)  # organic, synthetic, slow_release, etc.
    release_pattern = Column(String(20), nullable=False)  # immediate, slow, controlled, etc.
    
    # Nutrient content (stored as JSON for flexibility)
    nutrient_content = Column(JSON, nullable=False)  # {N: 46.0, P2O5: 0.0, K2O: 0.0, etc.}
    micronutrients = Column(JSON)  # {Fe: 0.1, Mn: 0.05, etc.}
    
    # Cost and availability
    cost_per_unit = Column(Float, nullable=False)
    unit_size = Column(Float, nullable=False)
    unit_type = Column(String(20), nullable=False)  # ton, bag, gallon
    
    # Application information
    application_methods = Column(JSON, nullable=False)  # [broadcast, banded, etc.]
    equipment_requirements = Column(JSON, nullable=False)  # [spreader, drill, etc.]
    application_rate_range = Column(JSON, nullable=False)  # {min: 100, max: 200}
    
    # Characteristics
    organic_certified = Column(Boolean, default=False)
    slow_release = Column(Boolean, default=False)
    water_soluble = Column(Boolean, default=False)
    
    # Impact scores
    environmental_impact_score = Column(Float, nullable=False)  # 0-1 scale
    soil_health_score = Column(Float, nullable=False)  # 0-1 scale
    
    # Benefits and limitations
    soil_health_benefits = Column(JSON)  # [benefit1, benefit2, etc.]
    pros = Column(JSON, nullable=False)  # [pro1, pro2, etc.]
    cons = Column(JSON, nullable=False)  # [con1, con2, etc.]
    application_notes = Column(JSON)  # [note1, note2, etc.]
    
    # Storage and handling
    storage_requirements = Column(Text)
    shelf_life_months = Column(Integer)
    safety_considerations = Column(JSON)  # [consideration1, consideration2, etc.]
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    recommendations = relationship("FertilizerRecommendation", back_populates="product")
    comparisons = relationship("FertilizerComparison", back_populates="product")


class FertilizerRecommendation(Base):
    """Fertilizer recommendation database model."""
    __tablename__ = "fertilizer_recommendations"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(String(100), nullable=False, index=True)
    
    # Foreign keys
    product_id = Column(UUID(as_uuid=True), ForeignKey("fertilizer_products.id"), nullable=False)
    farm_id = Column(String(100), index=True)  # Reference to farm (external)
    
    # Recommendation details
    suitability_score = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    recommended_rate_lbs_per_acre = Column(Float, nullable=False)
    application_timing = Column(String(100))
    application_method = Column(String(50))
    
    # Analysis results (stored as JSON)
    cost_analysis = Column(JSON, nullable=False)
    environmental_impact = Column(JSON, nullable=False)
    
    # Farmer-specific information
    pros_for_farmer = Column(JSON)  # [pro1, pro2, etc.]
    cons_for_farmer = Column(JSON)  # [con1, con2, etc.]
    equipment_needed = Column(JSON)  # [equipment1, equipment2, etc.]
    implementation_steps = Column(JSON)  # [step1, step2, etc.]
    
    # Supporting information
    agricultural_sources = Column(JSON)  # [source1, source2, etc.]
    expert_notes = Column(Text)
    
    # Farmer input context (stored as JSON)
    farmer_priorities = Column(JSON)  # Priority weights
    farmer_constraints = Column(JSON)  # Constraints and limitations
    soil_data = Column(JSON)  # Soil test data
    crop_data = Column(JSON)  # Crop information
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    is_implemented = Column(Boolean, default=False)
    implementation_date = Column(DateTime)
    feedback_score = Column(Float)  # User feedback on recommendation
    
    # Relationships
    product = relationship("FertilizerProduct", back_populates="recommendations")


class FertilizerComparison(Base):
    """Fertilizer comparison database model."""
    __tablename__ = "fertilizer_comparisons"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    comparison_id = Column(String(100), nullable=False, index=True)
    
    # Foreign keys
    product_id = Column(UUID(as_uuid=True), ForeignKey("fertilizer_products.id"), nullable=False)
    farm_id = Column(String(100), index=True)
    
    # Comparison details
    comparison_criteria = Column(JSON, nullable=False)  # [criterion1, criterion2, etc.]
    scores = Column(JSON, nullable=False)  # {criterion1: score1, criterion2: score2}
    overall_score = Column(Float, nullable=False)
    
    # Comparison results
    strengths = Column(JSON)  # [strength1, strength2, etc.]
    weaknesses = Column(JSON)  # [weakness1, weakness2, etc.]
    ranking = Column(Integer)  # Ranking among compared options
    
    # Context
    farm_context = Column(JSON)  # Farm-specific context for comparison
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("FertilizerProduct", back_populates="comparisons")


class FertilizerSelectionSession(Base):
    """Fertilizer selection session database model."""
    __tablename__ = "fertilizer_selection_sessions"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(100), nullable=False, unique=True, index=True)
    
    # Session details
    farm_id = Column(String(100), nullable=False, index=True)
    user_id = Column(String(100), index=True)
    
    # Input data
    farmer_priorities = Column(JSON, nullable=False)
    farmer_constraints = Column(JSON, nullable=False)
    soil_data = Column(JSON)
    crop_data = Column(JSON)
    farm_profile = Column(JSON)
    
    # Results
    recommendations_generated = Column(Integer, default=0)
    top_recommendation_id = Column(UUID(as_uuid=True), ForeignKey("fertilizer_recommendations.id"))
    overall_confidence_score = Column(Float)
    
    # Session metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    is_completed = Column(Boolean, default=False)
    
    # User feedback
    user_satisfaction_score = Column(Float)  # 1-5 scale
    user_feedback_text = Column(Text)
    selected_recommendation_id = Column(UUID(as_uuid=True))


class EquipmentCompatibility(Base):
    """Equipment compatibility database model."""
    __tablename__ = "equipment_compatibility"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    equipment_type = Column(String(50), nullable=False, unique=True, index=True)
    
    # Compatibility information
    compatible_fertilizer_types = Column(JSON, nullable=False)  # [type1, type2, etc.]
    compatible_application_methods = Column(JSON, nullable=False)  # [method1, method2, etc.]
    limitations = Column(JSON)  # [limitation1, limitation2, etc.]
    recommendations = Column(JSON)  # [recommendation1, recommendation2, etc.]
    
    # Cost information
    cost_range_min = Column(Float)
    cost_range_max = Column(Float)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FertilizerPriceHistory(Base):
    """Fertilizer price history database model."""
    __tablename__ = "fertilizer_price_history"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    product_id = Column(UUID(as_uuid=True), ForeignKey("fertilizer_products.id"), nullable=False)
    
    # Price information
    price_per_unit = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    region = Column(String(50))  # Geographic region for price
    supplier = Column(String(100))
    
    # Price metadata
    price_date = Column(DateTime, nullable=False)
    price_source = Column(String(100))  # Source of price information
    is_spot_price = Column(Boolean, default=True)
    is_contract_price = Column(Boolean, default=False)
    
    # Market conditions
    market_conditions = Column(JSON)  # Market condition factors
    seasonal_factors = Column(JSON)  # Seasonal price factors
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)


# Database indexes for performance
from sqlalchemy import Index

# Indexes for fertilizer products
Index('idx_fertilizer_products_type', FertilizerProduct.fertilizer_type)
Index('idx_fertilizer_products_organic', FertilizerProduct.organic_certified)
Index('idx_fertilizer_products_active', FertilizerProduct.is_active)

# Indexes for recommendations
Index('idx_fertilizer_recommendations_farm', FertilizerRecommendation.farm_id)
Index('idx_fertilizer_recommendations_request', FertilizerRecommendation.request_id)
Index('idx_fertilizer_recommendations_date', FertilizerRecommendation.created_at)

# Indexes for comparisons
Index('idx_fertilizer_comparisons_farm', FertilizerComparison.farm_id)
Index('idx_fertilizer_comparisons_comparison', FertilizerComparison.comparison_id)

# Indexes for sessions
Index('idx_fertilizer_sessions_farm', FertilizerSelectionSession.farm_id)
Index('idx_fertilizer_sessions_user', FertilizerSelectionSession.user_id)
Index('idx_fertilizer_sessions_date', FertilizerSelectionSession.created_at)

# Indexes for price history
Index('idx_fertilizer_prices_product', FertilizerPriceHistory.product_id)
Index('idx_fertilizer_prices_date', FertilizerPriceHistory.price_date)
Index('idx_fertilizer_prices_region', FertilizerPriceHistory.region)