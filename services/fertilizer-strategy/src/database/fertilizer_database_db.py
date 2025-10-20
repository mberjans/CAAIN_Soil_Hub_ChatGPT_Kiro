"""
Database models and repository for comprehensive fertilizer database system.
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from sqlalchemy import (
    create_engine, Column, String, Float, DateTime, Date, Boolean,
    Integer, Text, JSON, Enum as SQLEnum, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func, and_, or_
import uuid
import os
from dotenv import load_dotenv

from ..models.fertilizer_database_models import (
    FertilizerTypeEnum, NutrientReleasePattern, CompatibilityLevel,
    ClassificationType, FertilizerSearchFilters
)

load_dotenv()

logger = logging.getLogger(__name__)

Base = declarative_base()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/fertilizer_strategy")
engine = None
async_session = None


class FertilizerProductDB(Base):
    """Database model for fertilizer products."""
    __tablename__ = "fertilizer_products"

    product_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_name = Column(String(255), nullable=False)
    manufacturer = Column(String(255))
    fertilizer_type = Column(SQLEnum(FertilizerTypeEnum), nullable=False)

    # Nutrient Analysis
    nitrogen_percent = Column(Float, default=0.0)
    phosphorus_percent = Column(Float, default=0.0)
    potassium_percent = Column(Float, default=0.0)
    sulfur_percent = Column(Float, default=0.0)
    calcium_percent = Column(Float, default=0.0)
    magnesium_percent = Column(Float, default=0.0)
    micronutrients = Column(JSON, default={})

    # Physical Properties
    physical_form = Column(String(50))
    particle_size = Column(String(50))
    bulk_density = Column(Float)
    solubility = Column(String(50))
    release_pattern = Column(SQLEnum(NutrientReleasePattern), default=NutrientReleasePattern.IMMEDIATE)

    # Application Methods
    application_methods = Column(ARRAY(Text), default=[])
    compatible_equipment = Column(ARRAY(Text), default=[])
    mixing_compatibility = Column(JSON, default={})

    # Environmental Impact
    environmental_impact = Column(JSON, default={})
    organic_certified = Column(Boolean, default=False)
    sustainability_rating = Column(Float, default=5.0)

    # Cost Data
    average_cost_per_unit = Column(Float)
    cost_unit = Column(String(50), default="ton")
    price_volatility = Column(Float, default=0.0)
    availability_score = Column(Float, default=7.0)

    # Regulatory and Safety
    regulatory_status = Column(String(100))
    safety_data = Column(JSON, default={})
    handling_requirements = Column(ARRAY(Text), default=[])
    storage_requirements = Column(ARRAY(Text), default=[])

    # Crop Compatibility
    recommended_crops = Column(ARRAY(Text), default=[])
    not_recommended_crops = Column(ARRAY(Text), default=[])
    growth_stage_suitability = Column(JSON, default={})

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    data_source = Column(String(100))
    last_verified = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Constraints
    __table_args__ = (
        CheckConstraint('nitrogen_percent >= 0 AND nitrogen_percent <= 100', name='valid_nitrogen_percent'),
        CheckConstraint('phosphorus_percent >= 0 AND phosphorus_percent <= 100', name='valid_phosphorus_percent'),
        CheckConstraint('potassium_percent >= 0 AND potassium_percent <= 100', name='valid_potassium_percent'),
        CheckConstraint('sustainability_rating >= 0 AND sustainability_rating <= 10', name='valid_sustainability_rating'),
        CheckConstraint('availability_score >= 0 AND availability_score <= 10', name='valid_availability_score'),
    )


class FertilizerClassificationDB(Base):
    """Database model for fertilizer classifications."""
    __tablename__ = "fertilizer_classifications"

    classification_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    classification_type = Column(SQLEnum(ClassificationType), nullable=False)
    classification_name = Column(String(100), nullable=False)
    description = Column(Text)
    criteria = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('classification_type', 'classification_name', name='unique_classification'),
    )


class FertilizerCompatibilityDB(Base):
    """Database model for fertilizer compatibility."""
    __tablename__ = "fertilizer_compatibility"

    compatibility_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id_1 = Column(UUID(as_uuid=True), nullable=False)
    product_id_2 = Column(UUID(as_uuid=True), nullable=False)
    compatibility_level = Column(SQLEnum(CompatibilityLevel), nullable=False)
    mixing_ratio_limits = Column(JSON, default={})
    notes = Column(Text)
    test_date = Column(DateTime)
    verified_by = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint('product_id_1 != product_id_2', name='different_products'),
    )


class NutrientAnalysisHistoryDB(Base):
    """Database model for nutrient analysis history."""
    __tablename__ = "fertilizer_nutrient_analysis_history"

    analysis_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), nullable=False)
    analysis_date = Column(Date, nullable=False)
    nitrogen_percent = Column(Float, default=0.0)
    phosphorus_percent = Column(Float, default=0.0)
    potassium_percent = Column(Float, default=0.0)
    sulfur_percent = Column(Float, default=0.0)
    calcium_percent = Column(Float, default=0.0)
    magnesium_percent = Column(Float, default=0.0)
    micronutrients = Column(JSON, default={})
    analysis_method = Column(String(100))
    lab_name = Column(String(255))
    certified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ApplicationRecommendationDB(Base):
    """Database model for application recommendations."""
    __tablename__ = "fertilizer_application_recommendations"

    recommendation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), nullable=False)
    crop_type = Column(String(100), nullable=False)
    growth_stage = Column(String(100))
    recommended_rate_min = Column(Float)
    recommended_rate_max = Column(Float)
    rate_unit = Column(String(50), default="lbs/acre")
    application_method = Column(String(100))
    application_timing = Column(String(255))
    soil_condition_requirements = Column(JSON, default={})
    expected_response = Column(JSON, default={})
    notes = Column(Text)
    research_source = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


async def initialize_database():
    """Initialize database connection and create tables."""
    global engine, async_session

    try:
        # Create async engine
        engine = create_async_engine(
            DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=300
        )

        # Create async session factory
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Fertilizer database initialized successfully")

    except Exception as e:
        logger.error(f"Error initializing fertilizer database: {e}")
        engine = None
        async_session = None
        logger.warning("Continuing without database connection - using in-memory fallback")


async def shutdown_database():
    """Shutdown database connections."""
    global engine

    if engine:
        await engine.dispose()
        logger.info("Fertilizer database connections closed")
    else:
        logger.info("No fertilizer database connection to close")


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


class FertilizerDatabaseRepository:
    """Repository for fertilizer database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_product(self, product_data: Dict[str, Any]) -> FertilizerProductDB:
        """Create a new fertilizer product."""
        try:
            product = FertilizerProductDB(**product_data)
            self.session.add(product)
            await self.session.commit()
            await self.session.refresh(product)
            return product
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating fertilizer product: {e}")
            raise

    async def get_product_by_id(self, product_id: uuid.UUID) -> Optional[FertilizerProductDB]:
        """Get a fertilizer product by ID."""
        try:
            result = await self.session.get(FertilizerProductDB, product_id)
            return result
        except Exception as e:
            logger.error(f"Error getting fertilizer product: {e}")
            raise

    async def get_product_by_name(self, product_name: str) -> Optional[FertilizerProductDB]:
        """Get a fertilizer product by name."""
        try:
            from sqlalchemy import select
            stmt = select(FertilizerProductDB).where(FertilizerProductDB.product_name == product_name)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting fertilizer product by name: {e}")
            raise

    async def update_product(
        self,
        product_id: uuid.UUID,
        update_data: Dict[str, Any]
    ) -> Optional[FertilizerProductDB]:
        """Update a fertilizer product."""
        try:
            product = await self.get_product_by_id(product_id)
            if not product:
                return None

            for key, value in update_data.items():
                if value is not None and hasattr(product, key):
                    setattr(product, key, value)

            product.updated_at = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(product)
            return product
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating fertilizer product: {e}")
            raise

    async def delete_product(self, product_id: uuid.UUID) -> bool:
        """Delete a fertilizer product (soft delete by setting is_active=False)."""
        try:
            product = await self.get_product_by_id(product_id)
            if not product:
                return False

            product.is_active = False
            product.updated_at = datetime.utcnow()
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting fertilizer product: {e}")
            raise

    async def search_products(
        self,
        filters: FertilizerSearchFilters
    ) -> tuple[List[FertilizerProductDB], int]:
        """Search fertilizer products with filters."""
        try:
            from sqlalchemy import select

            # Build base query
            stmt = select(FertilizerProductDB)

            # Apply filters
            conditions = []

            if filters.fertilizer_types:
                conditions.append(FertilizerProductDB.fertilizer_type.in_(filters.fertilizer_types))

            if filters.min_nitrogen is not None:
                conditions.append(FertilizerProductDB.nitrogen_percent >= filters.min_nitrogen)

            if filters.max_nitrogen is not None:
                conditions.append(FertilizerProductDB.nitrogen_percent <= filters.max_nitrogen)

            if filters.min_phosphorus is not None:
                conditions.append(FertilizerProductDB.phosphorus_percent >= filters.min_phosphorus)

            if filters.max_phosphorus is not None:
                conditions.append(FertilizerProductDB.phosphorus_percent <= filters.max_phosphorus)

            if filters.min_potassium is not None:
                conditions.append(FertilizerProductDB.potassium_percent >= filters.min_potassium)

            if filters.max_potassium is not None:
                conditions.append(FertilizerProductDB.potassium_percent <= filters.max_potassium)

            if filters.organic_only is not None:
                conditions.append(FertilizerProductDB.organic_certified == filters.organic_only)

            if filters.release_pattern is not None:
                conditions.append(FertilizerProductDB.release_pattern == filters.release_pattern)

            if filters.min_sustainability_rating is not None:
                conditions.append(FertilizerProductDB.sustainability_rating >= filters.min_sustainability_rating)

            if filters.manufacturer is not None:
                conditions.append(FertilizerProductDB.manufacturer.ilike(f"%{filters.manufacturer}%"))

            conditions.append(FertilizerProductDB.is_active == filters.is_active)

            # Apply all conditions
            if conditions:
                stmt = stmt.where(and_(*conditions))

            # Get total count
            from sqlalchemy import select as select_func
            count_stmt = select_func(func.count()).select_from(FertilizerProductDB)
            if conditions:
                count_stmt = count_stmt.where(and_(*conditions))
            total_result = await self.session.execute(count_stmt)
            total_count = total_result.scalar()

            # Apply pagination
            stmt = stmt.offset(filters.offset).limit(filters.limit)

            # Execute query
            result = await self.session.execute(stmt)
            products = result.scalars().all()

            return list(products), total_count

        except Exception as e:
            logger.error(f"Error searching fertilizer products: {e}")
            raise

    async def get_all_products(
        self,
        is_active: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[FertilizerProductDB]:
        """Get all fertilizer products."""
        try:
            from sqlalchemy import select
            stmt = select(FertilizerProductDB).where(
                FertilizerProductDB.is_active == is_active
            ).offset(offset).limit(limit)

            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting all fertilizer products: {e}")
            raise

    async def create_classification(
        self,
        classification_data: Dict[str, Any]
    ) -> FertilizerClassificationDB:
        """Create a new fertilizer classification."""
        try:
            classification = FertilizerClassificationDB(**classification_data)
            self.session.add(classification)
            await self.session.commit()
            await self.session.refresh(classification)
            return classification
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating classification: {e}")
            raise

    async def get_classifications_by_type(
        self,
        classification_type: ClassificationType
    ) -> List[FertilizerClassificationDB]:
        """Get all classifications of a specific type."""
        try:
            from sqlalchemy import select
            stmt = select(FertilizerClassificationDB).where(
                FertilizerClassificationDB.classification_type == classification_type
            )
            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting classifications by type: {e}")
            raise

    async def create_compatibility(
        self,
        compatibility_data: Dict[str, Any]
    ) -> FertilizerCompatibilityDB:
        """Create a new compatibility record."""
        try:
            compatibility = FertilizerCompatibilityDB(**compatibility_data)
            self.session.add(compatibility)
            await self.session.commit()
            await self.session.refresh(compatibility)
            return compatibility
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating compatibility record: {e}")
            raise

    async def get_compatibility(
        self,
        product_id_1: uuid.UUID,
        product_id_2: uuid.UUID
    ) -> Optional[FertilizerCompatibilityDB]:
        """Get compatibility between two products."""
        try:
            from sqlalchemy import select
            stmt = select(FertilizerCompatibilityDB).where(
                or_(
                    and_(
                        FertilizerCompatibilityDB.product_id_1 == product_id_1,
                        FertilizerCompatibilityDB.product_id_2 == product_id_2
                    ),
                    and_(
                        FertilizerCompatibilityDB.product_id_1 == product_id_2,
                        FertilizerCompatibilityDB.product_id_2 == product_id_1
                    )
                )
            )
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting compatibility: {e}")
            raise

    async def create_nutrient_analysis(
        self,
        analysis_data: Dict[str, Any]
    ) -> NutrientAnalysisHistoryDB:
        """Create a nutrient analysis record."""
        try:
            analysis = NutrientAnalysisHistoryDB(**analysis_data)
            self.session.add(analysis)
            await self.session.commit()
            await self.session.refresh(analysis)
            return analysis
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating nutrient analysis: {e}")
            raise

    async def create_application_recommendation(
        self,
        recommendation_data: Dict[str, Any]
    ) -> ApplicationRecommendationDB:
        """Create an application recommendation."""
        try:
            recommendation = ApplicationRecommendationDB(**recommendation_data)
            self.session.add(recommendation)
            await self.session.commit()
            await self.session.refresh(recommendation)
            return recommendation
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating application recommendation: {e}")
            raise

    async def get_recommendations_for_product(
        self,
        product_id: uuid.UUID,
        crop_type: Optional[str] = None
    ) -> List[ApplicationRecommendationDB]:
        """Get application recommendations for a product."""
        try:
            from sqlalchemy import select
            stmt = select(ApplicationRecommendationDB).where(
                ApplicationRecommendationDB.product_id == product_id
            )

            if crop_type:
                stmt = stmt.where(ApplicationRecommendationDB.crop_type.ilike(f"%{crop_type}%"))

            result = await self.session.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting application recommendations: {e}")
            raise
