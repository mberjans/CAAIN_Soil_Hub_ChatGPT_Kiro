"""
Database Configuration for Fertilizer Type Selection

Database connection and session management for fertilizer type selection service.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import logging

from .fertilizer_schema import Base

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "FERTILIZER_DATABASE_URL",
    "postgresql://afas_user:afas_password@localhost:5432/afas_fertilizer"
)

# For testing, use SQLite
if os.getenv("TESTING") == "true":
    DATABASE_URL = "sqlite:///./test_fertilizer.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool if "sqlite" in DATABASE_URL else None,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=os.getenv("SQL_DEBUG", "false").lower() == "true"
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    """Create all database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise


def drop_tables():
    """Drop all database tables (use with caution)."""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {str(e)}")
        raise


@contextmanager
def get_db_session() -> Session:
    """Get database session with automatic cleanup."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        session.close()


def get_db():
    """Dependency for FastAPI to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DatabaseManager:
    """Database manager for fertilizer type selection service."""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def initialize_database(self):
        """Initialize database with tables and seed data."""
        try:
            # Create tables
            create_tables()
            
            # Seed initial data if needed
            self.seed_initial_data()
            
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def seed_initial_data(self):
        """Seed database with initial fertilizer products and equipment data."""
        from .seed_data import seed_fertilizer_products, seed_equipment_compatibility
        
        with get_db_session() as session:
            try:
                # Check if data already exists
                from .fertilizer_schema import FertilizerProduct
                existing_products = session.query(FertilizerProduct).count()
                
                if existing_products == 0:
                    logger.info("Seeding initial fertilizer products...")
                    seed_fertilizer_products(session)
                    
                    logger.info("Seeding equipment compatibility data...")
                    seed_equipment_compatibility(session)
                    
                    logger.info("Initial data seeded successfully")
                else:
                    logger.info(f"Database already contains {existing_products} fertilizer products")
                    
            except Exception as e:
                logger.error(f"Error seeding initial data: {str(e)}")
                raise
    
    def health_check(self) -> bool:
        """Check database connection health."""
        try:
            with get_db_session() as session:
                session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False
    
    def get_connection_info(self) -> dict:
        """Get database connection information."""
        return {
            "database_url": DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else DATABASE_URL,
            "engine_info": str(self.engine.url),
            "pool_size": self.engine.pool.size() if hasattr(self.engine.pool, 'size') else "N/A",
            "checked_out_connections": self.engine.pool.checkedout() if hasattr(self.engine.pool, 'checkedout') else "N/A"
        }


# Global database manager instance
db_manager = DatabaseManager()


def init_database():
    """Initialize database (called at startup)."""
    db_manager.initialize_database()


def get_database_manager() -> DatabaseManager:
    """Get database manager instance."""
    return db_manager