# Database Integration Guide

## Overview

This guide covers integrating the crop variety recommendations system with the database layer, including schema design, data models, and database operations.

## Database Architecture

### Database Schema

The variety recommendations system uses PostgreSQL with the following main tables:

```sql
-- Crop varieties table
CREATE TABLE crop_varieties (
    id SERIAL PRIMARY KEY,
    variety_name VARCHAR(150) NOT NULL,
    crop_id INTEGER REFERENCES crops(id),
    company VARCHAR(100),
    maturity_days INTEGER,
    yield_potential_min DECIMAL(8,2),
    yield_potential_max DECIMAL(8,2),
    yield_unit VARCHAR(20),
    climate_zones TEXT[],
    soil_ph_min DECIMAL(3,1),
    soil_ph_max DECIMAL(3,1),
    soil_types TEXT[],
    disease_resistance JSONB,
    characteristics JSONB,
    seed_companies JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Variety recommendations table
CREATE TABLE variety_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    farm_id UUID NOT NULL,
    crop_id INTEGER NOT NULL,
    variety_ids TEXT[] NOT NULL,
    recommendation_data JSONB NOT NULL,
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

-- Variety comparisons table
CREATE TABLE variety_comparisons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    comparison_name VARCHAR(200),
    variety_ids TEXT[] NOT NULL,
    comparison_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- User preferences table
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    preference_type VARCHAR(50) NOT NULL,
    preference_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_crop_varieties_crop_id ON crop_varieties(crop_id);
CREATE INDEX idx_crop_varieties_climate_zones ON crop_varieties USING GIN(climate_zones);
CREATE INDEX idx_crop_varieties_soil_types ON crop_varieties USING GIN(soil_types);
CREATE INDEX idx_variety_recommendations_user_id ON variety_recommendations(user_id);
CREATE INDEX idx_variety_recommendations_farm_id ON variety_recommendations(farm_id);
CREATE INDEX idx_variety_recommendations_created_at ON variety_recommendations(created_at);
CREATE INDEX idx_variety_comparisons_user_id ON variety_comparisons(user_id);
CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX idx_user_preferences_type ON user_preferences(preference_type);
```

## Data Models

### Pydantic Models

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum

class CropType(str, Enum):
    CORN = "corn"
    SOYBEAN = "soybean"
    WHEAT = "wheat"
    COTTON = "cotton"
    RICE = "rice"

class DiseaseResistance(BaseModel):
    northern_corn_leaf_blight: Optional[str] = None
    gray_leaf_spot: Optional[str] = None
    common_rust: Optional[str] = None
    anthracnose: Optional[str] = None
    southern_corn_leaf_blight: Optional[str] = None

class VarietyCharacteristics(BaseModel):
    plant_height: Optional[str] = None
    ear_height: Optional[str] = None
    stalk_strength: Optional[str] = None
    root_strength: Optional[str] = None
    drought_tolerance: Optional[str] = None
    heat_tolerance: Optional[str] = None

class CropVariety(BaseModel):
    id: Optional[int] = None
    variety_name: str = Field(..., min_length=1, max_length=150)
    crop_id: int
    company: Optional[str] = Field(None, max_length=100)
    maturity_days: Optional[int] = Field(None, ge=60, le=200)
    yield_potential_min: Optional[float] = Field(None, ge=0)
    yield_potential_max: Optional[float] = Field(None, ge=0)
    yield_unit: Optional[str] = Field(None, max_length=20)
    climate_zones: Optional[List[str]] = None
    soil_ph_min: Optional[float] = Field(None, ge=0, le=14)
    soil_ph_max: Optional[float] = Field(None, ge=0, le=14)
    soil_types: Optional[List[str]] = None
    disease_resistance: Optional[DiseaseResistance] = None
    characteristics: Optional[VarietyCharacteristics] = None
    seed_companies: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @validator('yield_potential_max')
    def validate_yield_range(cls, v, values):
        if v and 'yield_potential_min' in values and values['yield_potential_min']:
            if v < values['yield_potential_min']:
                raise ValueError('yield_potential_max must be greater than yield_potential_min')
        return v

    @validator('soil_ph_max')
    def validate_ph_range(cls, v, values):
        if v and 'soil_ph_min' in values and values['soil_ph_min']:
            if v < values['soil_ph_min']:
                raise ValueError('soil_ph_max must be greater than soil_ph_min')
        return v

class VarietyRecommendation(BaseModel):
    id: Optional[UUID] = None
    user_id: UUID
    farm_id: UUID
    crop_id: int
    variety_ids: List[str]
    recommendation_data: Dict[str, Any]
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

class VarietyComparison(BaseModel):
    id: Optional[UUID] = None
    user_id: UUID
    comparison_name: Optional[str] = Field(None, max_length=200)
    variety_ids: List[str]
    comparison_data: Dict[str, Any]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UserPreference(BaseModel):
    id: Optional[UUID] = None
    user_id: UUID
    preference_type: str = Field(..., max_length=50)
    preference_data: Dict[str, Any]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

## Database Operations

### 1. Variety CRUD Operations

```python
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

Base = declarative_base()

class CropVarietyDB(Base):
    __tablename__ = 'crop_varieties'
    
    id = Column(Integer, primary_key=True)
    variety_name = Column(String(150), nullable=False)
    crop_id = Column(Integer, nullable=False)
    company = Column(String(100))
    maturity_days = Column(Integer)
    yield_potential_min = Column(Numeric(8, 2))
    yield_potential_max = Column(Numeric(8, 2))
    yield_unit = Column(String(20))
    climate_zones = Column(ARRAY(String))
    soil_ph_min = Column(Numeric(3, 1))
    soil_ph_max = Column(Numeric(3, 1))
    soil_types = Column(ARRAY(String))
    disease_resistance = Column(JSON)
    characteristics = Column(JSON)
    seed_companies = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class VarietyRepository:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_variety(self, variety: CropVariety) -> CropVariety:
        """Create a new crop variety."""
        db_variety = CropVarietyDB(
            variety_name=variety.variety_name,
            crop_id=variety.crop_id,
            company=variety.company,
            maturity_days=variety.maturity_days,
            yield_potential_min=variety.yield_potential_min,
            yield_potential_max=variety.yield_potential_max,
            yield_unit=variety.yield_unit,
            climate_zones=variety.climate_zones,
            soil_ph_min=variety.soil_ph_min,
            soil_ph_max=variety.soil_ph_max,
            soil_types=variety.soil_types,
            disease_resistance=variety.disease_resistance.dict() if variety.disease_resistance else None,
            characteristics=variety.characteristics.dict() if variety.characteristics else None,
            seed_companies=variety.seed_companies
        )
        
        with self.SessionLocal() as session:
            session.add(db_variety)
            session.commit()
            session.refresh(db_variety)
            
            return CropVariety(
                id=db_variety.id,
                variety_name=db_variety.variety_name,
                crop_id=db_variety.crop_id,
                company=db_variety.company,
                maturity_days=db_variety.maturity_days,
                yield_potential_min=db_variety.yield_potential_min,
                yield_potential_max=db_variety.yield_potential_max,
                yield_unit=db_variety.yield_unit,
                climate_zones=db_variety.climate_zones,
                soil_ph_min=db_variety.soil_ph_min,
                soil_ph_max=db_variety.soil_ph_max,
                soil_types=db_variety.soil_types,
                disease_resistance=DiseaseResistance(**db_variety.disease_resistance) if db_variety.disease_resistance else None,
                characteristics=VarietyCharacteristics(**db_variety.characteristics) if db_variety.characteristics else None,
                seed_companies=db_variety.seed_companies,
                created_at=db_variety.created_at,
                updated_at=db_variety.updated_at
            )
    
    def get_variety_by_id(self, variety_id: int) -> Optional[CropVariety]:
        """Get a variety by ID."""
        with self.SessionLocal() as session:
            db_variety = session.query(CropVarietyDB).filter(CropVarietyDB.id == variety_id).first()
            if not db_variety:
                return None
            
            return CropVariety(
                id=db_variety.id,
                variety_name=db_variety.variety_name,
                crop_id=db_variety.crop_id,
                company=db_variety.company,
                maturity_days=db_variety.maturity_days,
                yield_potential_min=db_variety.yield_potential_min,
                yield_potential_max=db_variety.yield_potential_max,
                yield_unit=db_variety.yield_unit,
                climate_zones=db_variety.climate_zones,
                soil_ph_min=db_variety.soil_ph_min,
                soil_ph_max=db_variety.soil_ph_max,
                soil_types=db_variety.soil_types,
                disease_resistance=DiseaseResistance(**db_variety.disease_resistance) if db_variety.disease_resistance else None,
                characteristics=VarietyCharacteristics(**db_variety.characteristics) if db_variety.characteristics else None,
                seed_companies=db_variety.seed_companies,
                created_at=db_variety.created_at,
                updated_at=db_variety.updated_at
            )
    
    def get_varieties_by_crop(self, crop_id: int, limit: int = 100, offset: int = 0) -> List[CropVariety]:
        """Get varieties by crop ID."""
        with self.SessionLocal() as session:
            db_varieties = session.query(CropVarietyDB).filter(
                CropVarietyDB.crop_id == crop_id
            ).offset(offset).limit(limit).all()
            
            return [
                CropVariety(
                    id=db_variety.id,
                    variety_name=db_variety.variety_name,
                    crop_id=db_variety.crop_id,
                    company=db_variety.company,
                    maturity_days=db_variety.maturity_days,
                    yield_potential_min=db_variety.yield_potential_min,
                    yield_potential_max=db_variety.yield_potential_max,
                    yield_unit=db_variety.yield_unit,
                    climate_zones=db_variety.climate_zones,
                    soil_ph_min=db_variety.soil_ph_min,
                    soil_ph_max=db_variety.soil_ph_max,
                    soil_types=db_variety.soil_types,
                    disease_resistance=DiseaseResistance(**db_variety.disease_resistance) if db_variety.disease_resistance else None,
                    characteristics=VarietyCharacteristics(**db_variety.characteristics) if db_variety.characteristics else None,
                    seed_companies=db_variety.seed_companies,
                    created_at=db_variety.created_at,
                    updated_at=db_variety.updated_at
                )
                for db_variety in db_varieties
            ]
    
    def update_variety(self, variety_id: int, variety: CropVariety) -> Optional[CropVariety]:
        """Update a variety."""
        with self.SessionLocal() as session:
            db_variety = session.query(CropVarietyDB).filter(CropVarietyDB.id == variety_id).first()
            if not db_variety:
                return None
            
            db_variety.variety_name = variety.variety_name
            db_variety.crop_id = variety.crop_id
            db_variety.company = variety.company
            db_variety.maturity_days = variety.maturity_days
            db_variety.yield_potential_min = variety.yield_potential_min
            db_variety.yield_potential_max = variety.yield_potential_max
            db_variety.yield_unit = variety.yield_unit
            db_variety.climate_zones = variety.climate_zones
            db_variety.soil_ph_min = variety.soil_ph_min
            db_variety.soil_ph_max = variety.soil_ph_max
            db_variety.soil_types = variety.soil_types
            db_variety.disease_resistance = variety.disease_resistance.dict() if variety.disease_resistance else None
            db_variety.characteristics = variety.characteristics.dict() if variety.characteristics else None
            db_variety.seed_companies = variety.seed_companies
            db_variety.updated_at = datetime.utcnow()
            
            session.commit()
            session.refresh(db_variety)
            
            return CropVariety(
                id=db_variety.id,
                variety_name=db_variety.variety_name,
                crop_id=db_variety.crop_id,
                company=db_variety.company,
                maturity_days=db_variety.maturity_days,
                yield_potential_min=db_variety.yield_potential_min,
                yield_potential_max=db_variety.yield_potential_max,
                yield_unit=db_variety.yield_unit,
                climate_zones=db_variety.climate_zones,
                soil_ph_min=db_variety.soil_ph_min,
                soil_ph_max=db_variety.soil_ph_max,
                soil_types=db_variety.soil_types,
                disease_resistance=DiseaseResistance(**db_variety.disease_resistance) if db_variety.disease_resistance else None,
                characteristics=VarietyCharacteristics(**db_variety.characteristics) if db_variety.characteristics else None,
                seed_companies=db_variety.seed_companies,
                created_at=db_variety.created_at,
                updated_at=db_variety.updated_at
            )
    
    def delete_variety(self, variety_id: int) -> bool:
        """Delete a variety."""
        with self.SessionLocal() as session:
            db_variety = session.query(CropVarietyDB).filter(CropVarietyDB.id == variety_id).first()
            if not db_variety:
                return False
            
            session.delete(db_variety)
            session.commit()
            return True
```

### 2. Advanced Queries

```python
from sqlalchemy import and_, or_, func, desc, asc
from sqlalchemy.orm import Session

class AdvancedVarietyQueries:
    def __init__(self, session: Session):
        self.session = session
    
    def search_varieties(self, 
                        crop_id: Optional[int] = None,
                        climate_zone: Optional[str] = None,
                        soil_type: Optional[str] = None,
                        min_yield: Optional[float] = None,
                        max_maturity: Optional[int] = None,
                        limit: int = 100) -> List[CropVariety]:
        """Search varieties with multiple criteria."""
        query = self.session.query(CropVarietyDB)
        
        if crop_id:
            query = query.filter(CropVarietyDB.crop_id == crop_id)
        
        if climate_zone:
            query = query.filter(CropVarietyDB.climate_zones.contains([climate_zone]))
        
        if soil_type:
            query = query.filter(CropVarietyDB.soil_types.contains([soil_type]))
        
        if min_yield:
            query = query.filter(CropVarietyDB.yield_potential_min >= min_yield)
        
        if max_maturity:
            query = query.filter(CropVarietyDB.maturity_days <= max_maturity)
        
        db_varieties = query.limit(limit).all()
        
        return [
            self._convert_db_to_model(db_variety)
            for db_variety in db_varieties
        ]
    
    def get_top_yielding_varieties(self, crop_id: int, limit: int = 10) -> List[CropVariety]:
        """Get top yielding varieties for a crop."""
        db_varieties = self.session.query(CropVarietyDB).filter(
            CropVarietyDB.crop_id == crop_id
        ).order_by(desc(CropVarietyDB.yield_potential_max)).limit(limit).all()
        
        return [
            self._convert_db_to_model(db_variety)
            for db_variety in db_varieties
        ]
    
    def get_varieties_by_company(self, company: str) -> List[CropVariety]:
        """Get varieties by company."""
        db_varieties = self.session.query(CropVarietyDB).filter(
            CropVarietyDB.company.ilike(f"%{company}%")
        ).all()
        
        return [
            self._convert_db_to_model(db_variety)
            for db_variety in db_varieties
        ]
    
    def get_variety_statistics(self, crop_id: int) -> Dict[str, Any]:
        """Get statistics for varieties of a crop."""
        stats = self.session.query(
            func.count(CropVarietyDB.id).label('total_varieties'),
            func.avg(CropVarietyDB.yield_potential_max).label('avg_yield'),
            func.min(CropVarietyDB.maturity_days).label('min_maturity'),
            func.max(CropVarietyDB.maturity_days).label('max_maturity'),
            func.count(func.distinct(CropVarietyDB.company)).label('unique_companies')
        ).filter(CropVarietyDB.crop_id == crop_id).first()
        
        return {
            'total_varieties': stats.total_varieties,
            'average_yield': float(stats.avg_yield) if stats.avg_yield else 0,
            'min_maturity_days': stats.min_maturity,
            'max_maturity_days': stats.max_maturity,
            'unique_companies': stats.unique_companies
        }
    
    def _convert_db_to_model(self, db_variety: CropVarietyDB) -> CropVariety:
        """Convert database model to Pydantic model."""
        return CropVariety(
            id=db_variety.id,
            variety_name=db_variety.variety_name,
            crop_id=db_variety.crop_id,
            company=db_variety.company,
            maturity_days=db_variety.maturity_days,
            yield_potential_min=db_variety.yield_potential_min,
            yield_potential_max=db_variety.yield_potential_max,
            yield_unit=db_variety.yield_unit,
            climate_zones=db_variety.climate_zones,
            soil_ph_min=db_variety.soil_ph_min,
            soil_ph_max=db_variety.soil_ph_max,
            soil_types=db_variety.soil_types,
            disease_resistance=DiseaseResistance(**db_variety.disease_resistance) if db_variety.disease_resistance else None,
            characteristics=VarietyCharacteristics(**db_variety.characteristics) if db_variety.characteristics else None,
            seed_companies=db_variety.seed_companies,
            created_at=db_variety.created_at,
            updated_at=db_variety.updated_at
        )
```

### 3. Recommendation Storage

```python
class RecommendationRepository:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def save_recommendation(self, recommendation: VarietyRecommendation) -> VarietyRecommendation:
        """Save a variety recommendation."""
        db_recommendation = VarietyRecommendationDB(
            id=recommendation.id or uuid.uuid4(),
            user_id=recommendation.user_id,
            farm_id=recommendation.farm_id,
            crop_id=recommendation.crop_id,
            variety_ids=recommendation.variety_ids,
            recommendation_data=recommendation.recommendation_data,
            confidence_score=recommendation.confidence_score,
            expires_at=recommendation.expires_at
        )
        
        with self.SessionLocal() as session:
            session.add(db_recommendation)
            session.commit()
            session.refresh(db_recommendation)
            
            return VarietyRecommendation(
                id=db_recommendation.id,
                user_id=db_recommendation.user_id,
                farm_id=db_recommendation.farm_id,
                crop_id=db_recommendation.crop_id,
                variety_ids=db_recommendation.variety_ids,
                recommendation_data=db_recommendation.recommendation_data,
                confidence_score=db_recommendation.confidence_score,
                created_at=db_recommendation.created_at,
                expires_at=db_recommendation.expires_at
            )
    
    def get_user_recommendations(self, user_id: UUID, limit: int = 50) -> List[VarietyRecommendation]:
        """Get recommendations for a user."""
        with self.SessionLocal() as session:
            db_recommendations = session.query(VarietyRecommendationDB).filter(
                VarietyRecommendationDB.user_id == user_id
            ).order_by(desc(VarietyRecommendationDB.created_at)).limit(limit).all()
            
            return [
                VarietyRecommendation(
                    id=db_rec.id,
                    user_id=db_rec.user_id,
                    farm_id=db_rec.farm_id,
                    crop_id=db_rec.crop_id,
                    variety_ids=db_rec.variety_ids,
                    recommendation_data=db_rec.recommendation_data,
                    confidence_score=db_rec.confidence_score,
                    created_at=db_rec.created_at,
                    expires_at=db_rec.expires_at
                )
                for db_rec in db_recommendations
            ]
    
    def get_farm_recommendations(self, farm_id: UUID, limit: int = 20) -> List[VarietyRecommendation]:
        """Get recommendations for a farm."""
        with self.SessionLocal() as session:
            db_recommendations = session.query(VarietyRecommendationDB).filter(
                VarietyRecommendationDB.farm_id == farm_id
            ).order_by(desc(VarietyRecommendationDB.created_at)).limit(limit).all()
            
            return [
                VarietyRecommendation(
                    id=db_rec.id,
                    user_id=db_rec.user_id,
                    farm_id=db_rec.farm_id,
                    crop_id=db_rec.crop_id,
                    variety_ids=db_rec.variety_ids,
                    recommendation_data=db_rec.recommendation_data,
                    confidence_score=db_rec.confidence_score,
                    created_at=db_rec.created_at,
                    expires_at=db_rec.expires_at
                )
                for db_rec in db_recommendations
            ]
```

## Database Migrations

### Alembic Migration Setup

```python
# alembic.ini
[alembic]
script_location = migrations
sqlalchemy.url = postgresql://user:password@localhost/variety_recommendations

# migrations/env.py
from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig
import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from your_module import Base

config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Migration Commands

```bash
# Initialize Alembic
alembic init migrations

# Create a new migration
alembic revision --autogenerate -m "Add variety recommendations tables"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1

# Show migration history
alembic history

# Show current revision
alembic current
```

## Connection Pooling

### SQLAlchemy Connection Pool

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

class DatabaseManager:
    def __init__(self, database_url: str):
        self.engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=20,
            max_overflow=30,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def get_session(self):
        """Get a database session."""
        return self.SessionLocal()
    
    def close(self):
        """Close the database engine."""
        self.engine.dispose()
```

### Async Database Operations

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

class AsyncDatabaseManager:
    def __init__(self, database_url: str):
        self.engine = create_async_engine(
            database_url,
            pool_size=20,
            max_overflow=30,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False
        )
        self.AsyncSessionLocal = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def get_session(self):
        """Get an async database session."""
        return self.AsyncSessionLocal()
    
    async def close(self):
        """Close the async database engine."""
        await self.engine.dispose()

class AsyncVarietyRepository:
    def __init__(self, db_manager: AsyncDatabaseManager):
        self.db_manager = db_manager
    
    async def create_variety(self, variety: CropVariety) -> CropVariety:
        """Create a new crop variety asynchronously."""
        async with self.db_manager.get_session() as session:
            db_variety = CropVarietyDB(
                variety_name=variety.variety_name,
                crop_id=variety.crop_id,
                company=variety.company,
                maturity_days=variety.maturity_days,
                yield_potential_min=variety.yield_potential_min,
                yield_potential_max=variety.yield_potential_max,
                yield_unit=variety.yield_unit,
                climate_zones=variety.climate_zones,
                soil_ph_min=variety.soil_ph_min,
                soil_ph_max=variety.soil_ph_max,
                soil_types=variety.soil_types,
                disease_resistance=variety.disease_resistance.dict() if variety.disease_resistance else None,
                characteristics=variety.characteristics.dict() if variety.characteristics else None,
                seed_companies=variety.seed_companies
            )
            
            session.add(db_variety)
            await session.commit()
            await session.refresh(db_variety)
            
            return CropVariety(
                id=db_variety.id,
                variety_name=db_variety.variety_name,
                crop_id=db_variety.crop_id,
                company=db_variety.company,
                maturity_days=db_variety.maturity_days,
                yield_potential_min=db_variety.yield_potential_min,
                yield_potential_max=db_variety.yield_potential_max,
                yield_unit=db_variety.yield_unit,
                climate_zones=db_variety.climate_zones,
                soil_ph_min=db_variety.soil_ph_min,
                soil_ph_max=db_variety.soil_ph_max,
                soil_types=db_variety.soil_types,
                disease_resistance=DiseaseResistance(**db_variety.disease_resistance) if db_variety.disease_resistance else None,
                characteristics=VarietyCharacteristics(**db_variety.characteristics) if db_variety.characteristics else None,
                seed_companies=db_variety.seed_companies,
                created_at=db_variety.created_at,
                updated_at=db_variety.updated_at
            )
```

## Testing Database Operations

### Unit Tests

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from your_module import VarietyRepository, CropVariety, DiseaseResistance

class TestVarietyRepository:
    @pytest.fixture
    def test_db(self):
        """Create a test database."""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return SessionLocal()
    
    @pytest.fixture
    def variety_repository(self, test_db):
        """Create a variety repository with test database."""
        return VarietyRepository(test_db)
    
    def test_create_variety(self, variety_repository):
        """Test creating a variety."""
        variety = CropVariety(
            variety_name="Test Variety",
            crop_id=1,
            company="Test Company",
            maturity_days=105,
            yield_potential_min=180,
            yield_potential_max=200,
            yield_unit="bu/acre",
            climate_zones=["6a", "6b"],
            soil_ph_min=6.0,
            soil_ph_max=7.0,
            soil_types=["clay_loam"],
            disease_resistance=DiseaseResistance(
                northern_corn_leaf_blight="R",
                gray_leaf_spot="MR"
            )
        )
        
        created_variety = variety_repository.create_variety(variety)
        
        assert created_variety.id is not None
        assert created_variety.variety_name == "Test Variety"
        assert created_variety.crop_id == 1
        assert created_variety.company == "Test Company"
        assert created_variety.maturity_days == 105
        assert created_variety.yield_potential_min == 180
        assert created_variety.yield_potential_max == 200
        assert created_variety.yield_unit == "bu/acre"
        assert created_variety.climate_zones == ["6a", "6b"]
        assert created_variety.soil_ph_min == 6.0
        assert created_variety.soil_ph_max == 7.0
        assert created_variety.soil_types == ["clay_loam"]
        assert created_variety.disease_resistance.northern_corn_leaf_blight == "R"
        assert created_variety.disease_resistance.gray_leaf_spot == "MR"
    
    def test_get_variety_by_id(self, variety_repository):
        """Test getting a variety by ID."""
        variety = CropVariety(
            variety_name="Test Variety",
            crop_id=1,
            company="Test Company"
        )
        
        created_variety = variety_repository.create_variety(variety)
        retrieved_variety = variety_repository.get_variety_by_id(created_variety.id)
        
        assert retrieved_variety is not None
        assert retrieved_variety.id == created_variety.id
        assert retrieved_variety.variety_name == "Test Variety"
        assert retrieved_variety.crop_id == 1
        assert retrieved_variety.company == "Test Company"
    
    def test_get_varieties_by_crop(self, variety_repository):
        """Test getting varieties by crop ID."""
        variety1 = CropVariety(
            variety_name="Variety 1",
            crop_id=1,
            company="Company 1"
        )
        variety2 = CropVariety(
            variety_name="Variety 2",
            crop_id=1,
            company="Company 2"
        )
        variety3 = CropVariety(
            variety_name="Variety 3",
            crop_id=2,
            company="Company 3"
        )
        
        variety_repository.create_variety(variety1)
        variety_repository.create_variety(variety2)
        variety_repository.create_variety(variety3)
        
        crop1_varieties = variety_repository.get_varieties_by_crop(1)
        crop2_varieties = variety_repository.get_varieties_by_crop(2)
        
        assert len(crop1_varieties) == 2
        assert len(crop2_varieties) == 1
        assert crop1_varieties[0].variety_name in ["Variety 1", "Variety 2"]
        assert crop1_varieties[1].variety_name in ["Variety 1", "Variety 2"]
        assert crop2_varieties[0].variety_name == "Variety 3"
```

## Performance Optimization

### Database Indexing

```sql
-- Create indexes for common queries
CREATE INDEX idx_crop_varieties_crop_id ON crop_varieties(crop_id);
CREATE INDEX idx_crop_varieties_climate_zones ON crop_varieties USING GIN(climate_zones);
CREATE INDEX idx_crop_varieties_soil_types ON crop_varieties USING GIN(soil_types);
CREATE INDEX idx_crop_varieties_yield_potential ON crop_varieties(yield_potential_max);
CREATE INDEX idx_crop_varieties_maturity_days ON crop_varieties(maturity_days);
CREATE INDEX idx_crop_varieties_company ON crop_varieties(company);
CREATE INDEX idx_crop_varieties_created_at ON crop_varieties(created_at);

-- Composite indexes for complex queries
CREATE INDEX idx_crop_varieties_crop_climate ON crop_varieties(crop_id, climate_zones);
CREATE INDEX idx_crop_varieties_crop_yield ON crop_varieties(crop_id, yield_potential_max);
CREATE INDEX idx_crop_varieties_crop_maturity ON crop_varieties(crop_id, maturity_days);
```

### Query Optimization

```python
from sqlalchemy import text

class OptimizedQueries:
    def __init__(self, session: Session):
        self.session = session
    
    def get_varieties_with_filters_optimized(self, 
                                           crop_id: int,
                                           climate_zone: str,
                                           min_yield: float,
                                           limit: int = 100) -> List[CropVariety]:
        """Optimized query with proper indexing."""
        query = text("""
            SELECT cv.*
            FROM crop_varieties cv
            WHERE cv.crop_id = :crop_id
            AND :climate_zone = ANY(cv.climate_zones)
            AND cv.yield_potential_max >= :min_yield
            ORDER BY cv.yield_potential_max DESC
            LIMIT :limit
        """)
        
        result = self.session.execute(query, {
            'crop_id': crop_id,
            'climate_zone': climate_zone,
            'min_yield': min_yield,
            'limit': limit
        })
        
        return [
            self._convert_row_to_model(row)
            for row in result
        ]
    
    def _convert_row_to_model(self, row) -> CropVariety:
        """Convert database row to Pydantic model."""
        return CropVariety(
            id=row.id,
            variety_name=row.variety_name,
            crop_id=row.crop_id,
            company=row.company,
            maturity_days=row.maturity_days,
            yield_potential_min=row.yield_potential_min,
            yield_potential_max=row.yield_potential_max,
            yield_unit=row.yield_unit,
            climate_zones=row.climate_zones,
            soil_ph_min=row.soil_ph_min,
            soil_ph_max=row.soil_ph_max,
            soil_types=row.soil_types,
            disease_resistance=DiseaseResistance(**row.disease_resistance) if row.disease_resistance else None,
            characteristics=VarietyCharacteristics(**row.characteristics) if row.characteristics else None,
            seed_companies=row.seed_companies,
            created_at=row.created_at,
            updated_at=row.updated_at
        )
```

## Best Practices

### 1. Database Design

- Use appropriate data types for each field
- Implement proper constraints and validations
- Use indexes strategically for performance
- Normalize data to avoid redundancy
- Use JSONB for flexible data structures

### 2. Query Optimization

- Use prepared statements for repeated queries
- Implement proper indexing
- Avoid N+1 queries
- Use connection pooling
- Monitor query performance

### 3. Data Integrity

- Implement proper constraints
- Use transactions for data consistency
- Validate data at the application level
- Implement proper error handling
- Use database triggers sparingly

### 4. Security

- Use parameterized queries to prevent SQL injection
- Implement proper access controls
- Encrypt sensitive data
- Use secure connections
- Implement audit logging

### 5. Maintenance

- Regular database backups
- Monitor database performance
- Update database statistics
- Clean up old data
- Implement proper logging