"""
Database connection and models for the Fertilizer Application Service.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

from src.config import settings

logger = logging.getLogger(__name__)

# Database setup
Base = declarative_base()
metadata = MetaData()

# Global database session
async_session: Optional[async_sessionmaker] = None
engine = None


class FertilizerApplicationRecord(Base):
    """Database model for fertilizer application records."""
    __tablename__ = "fertilizer_applications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id = Column(String(100), nullable=False)
    field_id = Column(String(100), nullable=False)
    crop_type = Column(String(100), nullable=False)
    fertilizer_type = Column(String(100), nullable=False)
    application_method = Column(String(100), nullable=False)
    application_rate = Column(Float, nullable=False)
    rate_unit = Column(String(20), nullable=False)
    application_date = Column(DateTime, nullable=False)
    equipment_used = Column(String(100))
    weather_conditions = Column(JSON)
    application_efficiency = Column(Float)
    cost_per_acre = Column(Float)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EquipmentRecord(Base):
    """Database model for equipment records."""
    __tablename__ = "equipment_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id = Column(String(100), nullable=False)
    equipment_type = Column(String(100), nullable=False)
    equipment_name = Column(String(200), nullable=False)
    manufacturer = Column(String(100))
    model = Column(String(100))
    year = Column(Integer)
    capacity = Column(Float)
    capacity_unit = Column(String(20))
    purchase_date = Column(DateTime)
    purchase_price = Column(Float)
    current_value = Column(Float)
    status = Column(String(50), default="operational")
    maintenance_level = Column(String(50), default="basic")
    specifications = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ApplicationMethodRecord(Base):
    """Database model for application method records."""
    __tablename__ = "application_methods"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    method_name = Column(String(200), nullable=False)
    method_type = Column(String(100), nullable=False)
    description = Column(Text)
    application_timing = Column(JSON)
    precision_level = Column(String(50))
    environmental_impact = Column(String(50))
    equipment_requirements = Column(JSON)
    labor_intensity = Column(String(50))
    skill_requirements = Column(String(50))
    cost_per_acre = Column(Float)
    efficiency_rating = Column(Float)
    suitability_factors = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MethodRecommendationRecord(Base):
    """Database model for method recommendation records."""
    __tablename__ = "method_recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(String(100), nullable=False)
    farm_id = Column(String(100), nullable=False)
    field_id = Column(String(100), nullable=False)
    recommended_method_id = Column(UUID(as_uuid=True), nullable=False)
    alternative_methods = Column(JSON)
    recommendation_reasoning = Column(Text)
    confidence_score = Column(Float)
    field_conditions = Column(JSON)
    crop_requirements = Column(JSON)
    fertilizer_specification = Column(JSON)
    processing_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class EquipmentAssessmentRecord(Base):
    """Database model for equipment assessment records."""
    __tablename__ = "equipment_assessments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(String(100), nullable=False)
    farm_id = Column(String(100), nullable=False)
    assessment_date = Column(DateTime, nullable=False)
    farm_size_acres = Column(Float, nullable=False)
    field_count = Column(Integer, nullable=False)
    average_field_size = Column(Float, nullable=False)
    equipment_inventory = Column(JSON)
    compatibility_assessments = Column(JSON)
    efficiency_assessments = Column(JSON)
    upgrade_recommendations = Column(JSON)
    capacity_analysis = Column(JSON)
    cost_benefit_analysis = Column(JSON)
    overall_score = Column(Float)
    processing_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


class ApplicationGuidanceRecord(Base):
    """Database model for application guidance records."""
    __tablename__ = "application_guidance"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(String(100), nullable=False)
    method_id = Column(UUID(as_uuid=True), nullable=False)
    field_conditions = Column(JSON)
    weather_conditions = Column(JSON)
    application_date = Column(DateTime)
    experience_level = Column(String(50))
    guidance_content = Column(JSON)
    weather_advisories = Column(JSON)
    equipment_preparation = Column(JSON)
    quality_control_measures = Column(JSON)
    processing_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


async def initialize_database():
    """Initialize database connections."""
    global async_session, engine
    
    try:
        # Create async engine
        engine = create_async_engine(
            settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
            echo=False,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        
        # Create async session maker
        async_session = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def shutdown_database():
    """Shutdown database connections."""
    global engine
    
    try:
        if engine:
            await engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")


async def get_db_session() -> AsyncSession:
    """Get database session."""
    if not async_session:
        raise RuntimeError("Database not initialized")
    
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


class DatabaseManager:
    """Database manager for fertilizer application service."""
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        if not async_session:
            raise RuntimeError("Database not initialized")
        self.session = async_session()
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            if exc_type:
                await self.session.rollback()
            await self.session.close()


async def create_fertilizer_application_record(
    farm_id: str,
    field_id: str,
    crop_type: str,
    fertilizer_type: str,
    application_method: str,
    application_rate: float,
    rate_unit: str,
    application_date: datetime,
    equipment_used: Optional[str] = None,
    weather_conditions: Optional[Dict[str, Any]] = None,
    application_efficiency: Optional[float] = None,
    cost_per_acre: Optional[float] = None,
    notes: Optional[str] = None
) -> FertilizerApplicationRecord:
    """Create a new fertilizer application record."""
    async with DatabaseManager() as session:
        record = FertilizerApplicationRecord(
            farm_id=farm_id,
            field_id=field_id,
            crop_type=crop_type,
            fertilizer_type=fertilizer_type,
            application_method=application_method,
            application_rate=application_rate,
            rate_unit=rate_unit,
            application_date=application_date,
            equipment_used=equipment_used,
            weather_conditions=weather_conditions,
            application_efficiency=application_efficiency,
            cost_per_acre=cost_per_acre,
            notes=notes
        )
        session.add(record)
        await session.commit()
        await session.refresh(record)
        return record


async def create_equipment_record(
    farm_id: str,
    equipment_type: str,
    equipment_name: str,
    manufacturer: Optional[str] = None,
    model: Optional[str] = None,
    year: Optional[int] = None,
    capacity: Optional[float] = None,
    capacity_unit: Optional[str] = None,
    purchase_date: Optional[datetime] = None,
    purchase_price: Optional[float] = None,
    current_value: Optional[float] = None,
    status: str = "operational",
    maintenance_level: str = "basic",
    specifications: Optional[Dict[str, Any]] = None
) -> EquipmentRecord:
    """Create a new equipment record."""
    async with DatabaseManager() as session:
        record = EquipmentRecord(
            farm_id=farm_id,
            equipment_type=equipment_type,
            equipment_name=equipment_name,
            manufacturer=manufacturer,
            model=model,
            year=year,
            capacity=capacity,
            capacity_unit=capacity_unit,
            purchase_date=purchase_date,
            purchase_price=purchase_price,
            current_value=current_value,
            status=status,
            maintenance_level=maintenance_level,
            specifications=specifications
        )
        session.add(record)
        await session.commit()
        await session.refresh(record)
        return record


async def get_application_methods_by_type(method_type: str) -> list[ApplicationMethodRecord]:
    """Get application methods by type."""
    async with DatabaseManager() as session:
        result = await session.execute(
            ApplicationMethodRecord.__table__.select().where(
                ApplicationMethodRecord.method_type == method_type
            )
        )
        return result.fetchall()


async def get_equipment_by_farm(farm_id: str) -> list[EquipmentRecord]:
    """Get equipment records by farm ID."""
    async with DatabaseManager() as session:
        result = await session.execute(
            EquipmentRecord.__table__.select().where(
                EquipmentRecord.farm_id == farm_id
            )
        )
        return result.fetchall()