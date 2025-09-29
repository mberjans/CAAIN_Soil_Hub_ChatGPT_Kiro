"""
Drought Management Database Models and Connection Handling

SQLAlchemy models and database connection management for drought management service.
"""

import logging
import os
from typing import Optional, List
from datetime import datetime, timedelta
from uuid import UUID
from decimal import Decimal

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, JSON, text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.types import DECIMAL

logger = logging.getLogger(__name__)

Base = declarative_base()

class DroughtAssessment(Base):
    """Database model for drought assessments."""
    __tablename__ = "drought_assessments"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=UUID)
    farm_location_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    field_id = Column(PostgresUUID(as_uuid=True), nullable=True)
    assessment_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    drought_risk_level = Column(String(20), nullable=False)
    soil_moisture_surface = Column(Float, nullable=False)
    soil_moisture_deep = Column(Float, nullable=False)
    available_water_capacity = Column(Float, nullable=False)
    moisture_level = Column(String(20), nullable=False)
    weather_impact_data = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=False)
    recommendations = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conservation_practices = relationship("ConservationPractice", back_populates="assessment")
    monitoring_data = relationship("DroughtMonitoring", back_populates="assessment")

class ConservationPractice(Base):
    """Database model for conservation practices."""
    __tablename__ = "conservation_practices"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=UUID)
    assessment_id = Column(PostgresUUID(as_uuid=True), ForeignKey("drought_assessments.id"), nullable=True)
    field_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    practice_name = Column(String(100), nullable=False)
    practice_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    implementation_cost = Column(DECIMAL(10, 2), nullable=False)
    water_savings_percent = Column(Float, nullable=False)
    soil_health_impact = Column(String(20), nullable=False)
    equipment_requirements = Column(JSON, nullable=True)
    implementation_time_days = Column(Integer, nullable=False)
    maintenance_cost_per_year = Column(DECIMAL(10, 2), nullable=False)
    effectiveness_rating = Column(Float, nullable=False)
    implementation_status = Column(String(20), default="planned")
    implementation_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assessment = relationship("DroughtAssessment", back_populates="conservation_practices")
    water_savings = relationship("WaterSavings", back_populates="practice")

class DroughtMonitoring(Base):
    """Database model for drought monitoring configurations."""
    __tablename__ = "drought_monitoring"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=UUID)
    farm_location_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    assessment_id = Column(PostgresUUID(as_uuid=True), ForeignKey("drought_assessments.id"), nullable=True)
    monitoring_frequency = Column(String(20), nullable=False)
    alert_thresholds = Column(JSON, nullable=True)
    notification_preferences = Column(JSON, nullable=True)
    integration_services = Column(JSON, nullable=True)
    status = Column(String(20), default="active")
    last_check_time = Column(DateTime, nullable=True)
    next_check_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assessment = relationship("DroughtAssessment", back_populates="monitoring_data")
    monitoring_data_points = relationship("MonitoringDataPoint", back_populates="monitoring")

class MonitoringDataPoint(Base):
    """Database model for individual monitoring data points."""
    __tablename__ = "monitoring_data_points"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=UUID)
    monitoring_id = Column(PostgresUUID(as_uuid=True), ForeignKey("drought_monitoring.id"), nullable=False)
    field_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    data_type = Column(String(50), nullable=False)  # soil_moisture, weather, crop_health
    data_value = Column(Float, nullable=False)
    data_unit = Column(String(20), nullable=True)
    additional_data = Column(JSON, nullable=True)
    collection_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    data_source = Column(String(50), nullable=True)
    quality_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    monitoring = relationship("DroughtMonitoring", back_populates="monitoring_data_points")

class WaterSavings(Base):
    """Database model for water savings calculations."""
    __tablename__ = "water_savings"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=UUID)
    field_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    practice_id = Column(PostgresUUID(as_uuid=True), ForeignKey("conservation_practices.id"), nullable=True)
    calculation_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    current_water_usage = Column(DECIMAL(12, 2), nullable=False)
    projected_savings = Column(DECIMAL(12, 2), nullable=False)
    savings_percentage = Column(Float, nullable=False)
    implementation_cost = Column(DECIMAL(10, 2), nullable=False)
    annual_savings_value = Column(DECIMAL(10, 2), nullable=False)
    roi_percentage = Column(Float, nullable=False)
    payback_period_years = Column(Float, nullable=False)
    effectiveness_assumptions = Column(JSON, nullable=True)
    calculation_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    practice = relationship("ConservationPractice", back_populates="water_savings")

class DroughtAlert(Base):
    """Database model for drought alerts."""
    __tablename__ = "drought_alerts"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=UUID)
    farm_location_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    field_id = Column(PostgresUUID(as_uuid=True), nullable=True)
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=True)
    alert_data = Column(JSON, nullable=True)
    status = Column(String(20), default="active")
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FieldCharacteristics(Base):
    """Database model for field characteristics."""
    __tablename__ = "field_characteristics"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=UUID)
    field_id = Column(PostgresUUID(as_uuid=True), nullable=False, unique=True)
    farm_location_id = Column(PostgresUUID(as_uuid=True), nullable=False)
    field_name = Column(String(100), nullable=False)
    field_size_acres = Column(DECIMAL(8, 2), nullable=False)
    soil_type = Column(String(50), nullable=False)
    slope_percent = Column(Float, nullable=False)
    drainage_class = Column(String(50), nullable=False)
    organic_matter_percent = Column(Float, nullable=False)
    climate_zone = Column(String(50), nullable=False)
    current_irrigation_type = Column(String(50), nullable=True)
    water_source = Column(String(50), nullable=True)
    energy_cost_per_kwh = Column(DECIMAL(6, 4), nullable=True)
    additional_characteristics = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DroughtServiceDatabase:
    """Database connection and management class."""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize database connection and create tables."""
        try:
            logger.info("Initializing Drought Management Database...")
            
            # Create engine
            self.engine = create_engine(
                self.database_url,
                echo=False,  # Set to True for SQL debugging
                pool_pre_ping=True,
                pool_recycle=300
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Create tables
            Base.metadata.create_all(bind=self.engine)
            
            self.initialized = True
            logger.info("Drought Management Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    async def cleanup(self):
        """Clean up database connections."""
        try:
            logger.info("Cleaning up database connections...")
            if self.engine:
                self.engine.dispose()
            self.initialized = False
            logger.info("Database cleanup completed")
        except Exception as e:
            logger.error(f"Error during database cleanup: {str(e)}")
    
    def get_session(self):
        """Get database session."""
        if not self.initialized:
            raise RuntimeError("Database not initialized")
        return self.SessionLocal()
    
    async def health_check(self) -> bool:
        """Check database health."""
        try:
            if not self.initialized:
                return False
            
            # Test connection
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            return True
            
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False
    
    # Database operations
    async def create_drought_assessment(self, assessment_data: dict) -> DroughtAssessment:
        """Create a new drought assessment."""
        with self.get_session() as session:
            assessment = DroughtAssessment(**assessment_data)
            session.add(assessment)
            session.commit()
            session.refresh(assessment)
            return assessment
    
    async def get_drought_assessment(self, assessment_id: UUID) -> Optional[DroughtAssessment]:
        """Get drought assessment by ID."""
        with self.get_session() as session:
            return session.query(DroughtAssessment).filter(
                DroughtAssessment.id == assessment_id
            ).first()
    
    async def get_farm_assessments(self, farm_location_id: UUID, limit: int = 10) -> List[DroughtAssessment]:
        """Get recent drought assessments for a farm."""
        with self.get_session() as session:
            return session.query(DroughtAssessment).filter(
                DroughtAssessment.farm_location_id == farm_location_id
            ).order_by(DroughtAssessment.assessment_date.desc()).limit(limit).all()
    
    async def create_conservation_practice(self, practice_data: dict) -> ConservationPractice:
        """Create a new conservation practice."""
        with self.get_session() as session:
            practice = ConservationPractice(**practice_data)
            session.add(practice)
            session.commit()
            session.refresh(practice)
            return practice
    
    async def get_field_practices(self, field_id: UUID) -> List[ConservationPractice]:
        """Get conservation practices for a field."""
        with self.get_session() as session:
            return session.query(ConservationPractice).filter(
                ConservationPractice.field_id == field_id
            ).all()
    
    async def create_monitoring_config(self, monitoring_data: dict) -> DroughtMonitoring:
        """Create drought monitoring configuration."""
        with self.get_session() as session:
            monitoring = DroughtMonitoring(**monitoring_data)
            session.add(monitoring)
            session.commit()
            session.refresh(monitoring)
            return monitoring
    
    async def get_monitoring_config(self, farm_location_id: UUID) -> Optional[DroughtMonitoring]:
        """Get monitoring configuration for a farm."""
        with self.get_session() as session:
            return session.query(DroughtMonitoring).filter(
                DroughtMonitoring.farm_location_id == farm_location_id,
                DroughtMonitoring.status == "active"
            ).first()
    
    async def create_monitoring_data_point(self, data_point_data: dict) -> MonitoringDataPoint:
        """Create a monitoring data point."""
        with self.get_session() as session:
            data_point = MonitoringDataPoint(**data_point_data)
            session.add(data_point)
            session.commit()
            session.refresh(data_point)
            return data_point
    
    async def get_recent_monitoring_data(self, field_id: UUID, hours: int = 24) -> List[MonitoringDataPoint]:
        """Get recent monitoring data for a field."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        with self.get_session() as session:
            return session.query(MonitoringDataPoint).filter(
                MonitoringDataPoint.field_id == field_id,
                MonitoringDataPoint.collection_time >= cutoff_time
            ).order_by(MonitoringDataPoint.collection_time.desc()).all()
    
    async def create_water_savings_record(self, savings_data: dict) -> WaterSavings:
        """Create water savings calculation record."""
        with self.get_session() as session:
            savings = WaterSavings(**savings_data)
            session.add(savings)
            session.commit()
            session.refresh(savings)
            return savings
    
    async def get_field_water_savings_history(self, field_id: UUID, days: int = 365) -> List[WaterSavings]:
        """Get water savings history for a field."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        with self.get_session() as session:
            return session.query(WaterSavings).filter(
                WaterSavings.field_id == field_id,
                WaterSavings.calculation_date >= cutoff_date
            ).order_by(WaterSavings.calculation_date.desc()).all()
    
    async def create_drought_alert(self, alert_data: dict) -> DroughtAlert:
        """Create a drought alert."""
        with self.get_session() as session:
            alert = DroughtAlert(**alert_data)
            session.add(alert)
            session.commit()
            session.refresh(alert)
            return alert
    
    async def get_active_alerts(self, farm_location_id: UUID) -> List[DroughtAlert]:
        """Get active drought alerts for a farm."""
        with self.get_session() as session:
            return session.query(DroughtAlert).filter(
                DroughtAlert.farm_location_id == farm_location_id,
                DroughtAlert.status == "active"
            ).order_by(DroughtAlert.created_at.desc()).all()
    
    async def create_field_characteristics(self, characteristics_data: dict) -> FieldCharacteristics:
        """Create field characteristics record."""
        with self.get_session() as session:
            characteristics = FieldCharacteristics(**characteristics_data)
            session.add(characteristics)
            session.commit()
            session.refresh(characteristics)
            return characteristics
    
    async def get_field_characteristics(self, field_id: UUID) -> Optional[FieldCharacteristics]:
        """Get field characteristics by field ID."""
        with self.get_session() as session:
            return session.query(FieldCharacteristics).filter(
                FieldCharacteristics.field_id == field_id
            ).first()
    
    async def update_field_characteristics(self, field_id: UUID, update_data: dict) -> Optional[FieldCharacteristics]:
        """Update field characteristics."""
        with self.get_session() as session:
            characteristics = session.query(FieldCharacteristics).filter(
                FieldCharacteristics.field_id == field_id
            ).first()
            
            if characteristics:
                for key, value in update_data.items():
                    setattr(characteristics, key, value)
                characteristics.updated_at = datetime.utcnow()
                session.commit()
                session.refresh(characteristics)
            
            return characteristics


# Global database instance
drought_db = None

async def get_drought_database() -> DroughtServiceDatabase:
    """Get global drought database instance."""
    global drought_db
    if drought_db is None:
        database_url = os.getenv("DATABASE_URL", "postgresql://localhost:5432/afas_drought")
        drought_db = DroughtServiceDatabase(database_url)
        await drought_db.initialize()
    return drought_db