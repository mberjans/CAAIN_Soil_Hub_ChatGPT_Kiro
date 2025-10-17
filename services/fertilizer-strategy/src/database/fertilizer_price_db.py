"""
Database models and connection management for fertilizer price tracking.
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine, Column, String, Float, DateTime, Date, Boolean, Integer, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

Base = declarative_base()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/fertilizer_strategy")
engine = None
async_session = None


class FertilizerProduct(Base):
    """Database model for fertilizer products."""
    __tablename__ = "fertilizer_products"
    
    product_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_name = Column(String(255), nullable=False)
    fertilizer_type = Column(String(50), nullable=False)  # nitrogen, phosphorus, potassium, etc.
    specific_product = Column(String(100), nullable=False)  # urea, DAP, MAP, etc.
    
    # Product specifications
    nitrogen_percent = Column(Float, default=0.0)
    phosphorus_percent = Column(Float, default=0.0)  # P2O5
    potassium_percent = Column(Float, default=0.0)   # K2O
    sulfur_percent = Column(Float, default=0.0)
    
    # Physical properties
    bulk_density = Column(Float)  # lbs/cubic foot
    particle_size = Column(String(50))
    application_methods = Column(JSON)  # Array of application methods
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FertilizerPriceHistory(Base):
    """Database model for fertilizer price history."""
    __tablename__ = "fertilizer_price_history"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    product_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Price information
    price_per_unit = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)  # ton, cwt, lb
    currency = Column(String(3), default="USD")
    region = Column(String(50), nullable=False)
    state = Column(String(50))
    source = Column(String(100), nullable=False)
    
    # Price metadata
    price_date = Column(Date, nullable=False)
    is_spot_price = Column(Boolean, default=True)
    is_contract_price = Column(Boolean, default=False)
    
    # Market conditions
    market_conditions = Column(JSON)  # Market condition factors
    seasonal_factors = Column(JSON)  # Seasonal price factors
    
    # Quality metrics
    confidence = Column(Float, nullable=False)
    volatility = Column(Float, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PriceTrendCache(Base):
    """Database model for cached trend analysis."""
    __tablename__ = "price_trend_cache"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), nullable=False)
    region = Column(String(50), nullable=False)
    
    # Trend data
    trend_data = Column(JSON, nullable=False)  # Serialized trend analysis
    analysis_date = Column(DateTime, nullable=False)
    data_points_used = Column(Integer, nullable=False)
    
    # Cache metadata
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class MarketIntelligenceCache(Base):
    """Database model for cached market intelligence."""
    __tablename__ = "market_intelligence_cache"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    region = Column(String(50), nullable=False)
    report_date = Column(Date, nullable=False)
    
    # Report data
    report_data = Column(JSON, nullable=False)  # Serialized report
    confidence_score = Column(Float, nullable=False)
    data_sources = Column(JSON, nullable=False)  # Array of sources
    
    # Cache metadata
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


async def initialize_database():
    """Initialize database connection and create tables."""
    global engine, async_session
    
    try:
        # Create async engine
        engine = create_async_engine(
            DATABASE_URL,
            echo=False,  # Set to True for SQL debugging
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
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        # Set engine to None to indicate database is not available
        engine = None
        async_session = None
        logger.warning("Continuing without database connection - using in-memory fallback")


async def shutdown_database():
    """Shutdown database connections."""
    global engine
    
    if engine:
        await engine.dispose()
        logger.info("Database connections closed")
    else:
        logger.info("No database connection to close")


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


class FertilizerPriceRepository:
    """Repository for fertilizer price data operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_price_record(self, price_data: Dict[str, Any]) -> FertilizerPriceHistory:
        """Create a new price record."""
        try:
            price_record = FertilizerPriceHistory(**price_data)
            self.session.add(price_record)
            await self.session.commit()
            await self.session.refresh(price_record)
            return price_record
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating price record: {e}")
            raise
    
    async def get_price_history(
        self,
        product_id: str = None,
        region: str = None,
        start_date: date = None,
        end_date: date = None,
        limit: int = 100
    ) -> List[FertilizerPriceHistory]:
        """Get price history with filters."""
        try:
            query = self.session.query(FertilizerPriceHistory)
            
            if product_id:
                query = query.filter(FertilizerPriceHistory.product_id == product_id)
            if region:
                query = query.filter(FertilizerPriceHistory.region == region)
            if start_date:
                query = query.filter(FertilizerPriceHistory.price_date >= start_date)
            if end_date:
                query = query.filter(FertilizerPriceHistory.price_date <= end_date)
            
            query = query.order_by(FertilizerPriceHistory.price_date.desc())
            query = query.limit(limit)
            
            result = await query.all()
            return result
            
        except Exception as e:
            logger.error(f"Error getting price history: {e}")
            raise
    
    async def get_latest_price(
        self,
        product_id: str,
        region: str,
        max_age_hours: int = 24
    ) -> Optional[FertilizerPriceHistory]:
        """Get the latest price for a product in a region."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            
            query = self.session.query(FertilizerPriceHistory)
            query = query.filter(FertilizerPriceHistory.product_id == product_id)
            query = query.filter(FertilizerPriceHistory.region == region)
            query = query.filter(FertilizerPriceHistory.created_at >= cutoff_time)
            query = query.order_by(FertilizerPriceHistory.created_at.desc())
            query = query.limit(1)
            
            result = await query.first()
            return result
            
        except Exception as e:
            logger.error(f"Error getting latest price: {e}")
            raise
    
    async def get_price_trends(
        self,
        product_id: str,
        region: str,
        days: int = 30
    ) -> List[FertilizerPriceHistory]:
        """Get price trends for trend analysis."""
        try:
            cutoff_date = date.today() - timedelta(days=days)
            
            query = self.session.query(FertilizerPriceHistory)
            query = query.filter(FertilizerPriceHistory.product_id == product_id)
            query = query.filter(FertilizerPriceHistory.region == region)
            query = query.filter(FertilizerPriceHistory.price_date >= cutoff_date)
            query = query.order_by(FertilizerPriceHistory.price_date.asc())
            
            result = await query.all()
            return result
            
        except Exception as e:
            logger.error(f"Error getting price trends: {e}")
            raise
    
    async def cache_trend_analysis(
        self,
        product_id: str,
        region: str,
        trend_data: Dict[str, Any],
        data_points_used: int,
        expires_hours: int = 24
    ) -> PriceTrendCache:
        """Cache trend analysis results."""
        try:
            expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
            
            cache_record = PriceTrendCache(
                product_id=product_id,
                region=region,
                trend_data=trend_data,
                analysis_date=datetime.utcnow(),
                data_points_used=data_points_used,
                expires_at=expires_at
            )
            
            self.session.add(cache_record)
            await self.session.commit()
            await self.session.refresh(cache_record)
            return cache_record
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error caching trend analysis: {e}")
            raise
    
    async def get_cached_trend_analysis(
        self,
        product_id: str,
        region: str
    ) -> Optional[PriceTrendCache]:
        """Get cached trend analysis if still valid."""
        try:
            query = self.session.query(PriceTrendCache)
            query = query.filter(PriceTrendCache.product_id == product_id)
            query = query.filter(PriceTrendCache.region == region)
            query = query.filter(PriceTrendCache.expires_at > datetime.utcnow())
            query = query.order_by(PriceTrendCache.created_at.desc())
            query = query.limit(1)
            
            result = await query.first()
            return result
            
        except Exception as e:
            logger.error(f"Error getting cached trend analysis: {e}")
            raise