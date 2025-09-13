"""
AFAS Database Configuration and Connection Management
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024
"""

import os
import logging
from typing import Optional, Dict, Any
from urllib.parse import quote_plus
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import pymongo
from pymongo import MongoClient
import redis
from redis import Redis
import asyncio
import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLAlchemy Base
Base = declarative_base()

class DatabaseConfig:
    """Database configuration management."""
    
    def __init__(self):
        self.load_config()
    
    def load_config(self):
        """Load database configuration from environment variables."""
        # PostgreSQL Configuration
        self.postgres_host = os.getenv('POSTGRES_HOST', 'localhost')
        self.postgres_port = int(os.getenv('POSTGRES_PORT', 5432))
        self.postgres_db = os.getenv('POSTGRES_DB', 'afas_db')
        self.postgres_user = os.getenv('POSTGRES_USER', 'afas_user')
        self.postgres_password = os.getenv('POSTGRES_PASSWORD', 'afas_password_2024')
        
        # MongoDB Configuration
        self.mongodb_host = os.getenv('MONGODB_HOST', 'localhost')
        self.mongodb_port = int(os.getenv('MONGODB_PORT', 27017))
        self.mongodb_db = os.getenv('MONGODB_DB', 'afas_db')
        self.mongodb_username = os.getenv('MONGODB_USERNAME', '')
        self.mongodb_password = os.getenv('MONGODB_PASSWORD', '')
        
        # Redis Configuration
        self.redis_host = os.getenv('REDIS_HOST', 'localhost')
        self.redis_port = int(os.getenv('REDIS_PORT', 6379))
        self.redis_password = os.getenv('REDIS_PASSWORD', '')
        self.redis_db = int(os.getenv('REDIS_DB', 0))
        
        # Connection Pool Settings
        self.db_pool_size = int(os.getenv('DB_POOL_SIZE', 20))
        self.db_max_overflow = int(os.getenv('DB_MAX_OVERFLOW', 30))
        self.db_pool_timeout = int(os.getenv('DB_POOL_TIMEOUT', 30))
        self.db_pool_recycle = int(os.getenv('DB_POOL_RECYCLE', 3600))
        
        # Cache Settings
        self.cache_ttl_default = int(os.getenv('CACHE_TTL_DEFAULT', 3600))
        self.cache_ttl_weather = int(os.getenv('CACHE_TTL_WEATHER', 3600))
        self.cache_ttl_soil = int(os.getenv('CACHE_TTL_SOIL', 86400))
        self.cache_ttl_recommendations = int(os.getenv('CACHE_TTL_RECOMMENDATIONS', 21600))
    
    @property
    def postgres_url(self) -> str:
        """Get PostgreSQL connection URL."""
        password = quote_plus(self.postgres_password)
        return f"postgresql://{self.postgres_user}:{password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def postgres_async_url(self) -> str:
        """Get PostgreSQL async connection URL."""
        password = quote_plus(self.postgres_password)
        return f"postgresql+asyncpg://{self.postgres_user}:{password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def mongodb_url(self) -> str:
        """Get MongoDB connection URL."""
        if self.mongodb_username and self.mongodb_password:
            username = quote_plus(self.mongodb_username)
            password = quote_plus(self.mongodb_password)
            return f"mongodb://{username}:{password}@{self.mongodb_host}:{self.mongodb_port}/{self.mongodb_db}"
        else:
            return f"mongodb://{self.mongodb_host}:{self.mongodb_port}/{self.mongodb_db}"


class PostgreSQLManager:
    """PostgreSQL database manager."""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine = None
        self.SessionLocal = None
        self._setup_engine()
    
    def _setup_engine(self):
        """Setup SQLAlchemy engine with connection pooling."""
        self.engine = create_engine(
            self.config.postgres_url,
            poolclass=QueuePool,
            pool_size=self.config.db_pool_size,
            max_overflow=self.config.db_max_overflow,
            pool_timeout=self.config.db_pool_timeout,
            pool_recycle=self.config.db_pool_recycle,
            pool_pre_ping=True,  # Verify connections before use
            echo=os.getenv('SQL_ECHO', 'false').lower() == 'true'
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        logger.info(f"PostgreSQL engine created: {self.config.postgres_host}:{self.config.postgres_port}")
    
    def get_session(self) -> Session:
        """Get a database session."""
        return self.SessionLocal()
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                logger.info(f"PostgreSQL connection successful: {version}")
                return True
        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {e}")
            return False
    
    def create_tables(self):
        """Create all tables defined in models."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("PostgreSQL tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create PostgreSQL tables: {e}")
            raise
    
    def close(self):
        """Close database connections."""
        if self.engine:
            self.engine.dispose()
            logger.info("PostgreSQL connections closed")


class MongoDBManager:
    """MongoDB database manager."""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.client = None
        self.database = None
        self._setup_client()
    
    def _setup_client(self):
        """Setup MongoDB client."""
        try:
            self.client = MongoClient(
                self.config.mongodb_url,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000,
                maxPoolSize=50,
                minPoolSize=5
            )
            
            self.database = self.client[self.config.mongodb_db]
            logger.info(f"MongoDB client created: {self.config.mongodb_host}:{self.config.mongodb_port}")
            
        except Exception as e:
            logger.error(f"Failed to create MongoDB client: {e}")
            raise
    
    def get_collection(self, collection_name: str):
        """Get a MongoDB collection."""
        return self.database[collection_name]
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            # Ping the database
            self.client.admin.command('ping')
            logger.info("MongoDB connection successful")
            return True
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            return False
    
    def create_indexes(self):
        """Create indexes for collections."""
        try:
            # Question responses indexes
            question_responses = self.get_collection('question_responses')
            question_responses.create_index([("user_id", 1)])
            question_responses.create_index([("farm_id", 1)])
            question_responses.create_index([("question_type", 1)])
            question_responses.create_index([("timestamp", -1)])
            
            # External data cache indexes
            external_cache = self.get_collection('external_data_cache')
            external_cache.create_index([("cache_key", 1)], unique=True)
            external_cache.create_index([("data_source", 1)])
            external_cache.create_index([("expires_at", 1)])
            
            # Agricultural knowledge indexes
            knowledge = self.get_collection('agricultural_knowledge')
            knowledge.create_index([("knowledge_id", 1)], unique=True)
            knowledge.create_index([("category", 1), ("subcategory", 1)])
            knowledge.create_index([("tags", 1)])
            
            logger.info("MongoDB indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create MongoDB indexes: {e}")
            raise
    
    def close(self):
        """Close database connections."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connections closed")


class AsyncMongoDBManager:
    """Async MongoDB database manager."""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.client = None
        self.database = None
    
    async def connect(self):
        """Connect to MongoDB."""
        try:
            self.client = AsyncIOMotorClient(
                self.config.mongodb_url,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000,
                maxPoolSize=50,
                minPoolSize=5
            )
            
            self.database = self.client[self.config.mongodb_db]
            logger.info(f"Async MongoDB client created: {self.config.mongodb_host}:{self.config.mongodb_port}")
            
        except Exception as e:
            logger.error(f"Failed to create async MongoDB client: {e}")
            raise
    
    def get_collection(self, collection_name: str):
        """Get a MongoDB collection."""
        return self.database[collection_name]
    
    async def test_connection(self) -> bool:
        """Test database connection."""
        try:
            await self.client.admin.command('ping')
            logger.info("Async MongoDB connection successful")
            return True
        except Exception as e:
            logger.error(f"Async MongoDB connection failed: {e}")
            return False
    
    async def close(self):
        """Close database connections."""
        if self.client:
            self.client.close()
            logger.info("Async MongoDB connections closed")


class RedisManager:
    """Redis cache manager."""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.clients = {}
        self._setup_clients()
    
    def _setup_clients(self):
        """Setup Redis clients for different databases."""
        try:
            # Create clients for different Redis databases
            for db_num in range(8):  # 0-7 as defined in schema
                client = redis.Redis(
                    host=self.config.redis_host,
                    port=self.config.redis_port,
                    db=db_num,
                    password=self.config.redis_password if self.config.redis_password else None,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
                self.clients[db_num] = client
            
            logger.info(f"Redis clients created: {self.config.redis_host}:{self.config.redis_port}")
            
        except Exception as e:
            logger.error(f"Failed to create Redis clients: {e}")
            raise
    
    def get_client(self, db: int = 0) -> Redis:
        """Get Redis client for specific database."""
        if db not in self.clients:
            raise ValueError(f"Redis database {db} not configured")
        return self.clients[db]
    
    def get_session_client(self) -> Redis:
        """Get Redis client for user sessions (DB 0)."""
        return self.get_client(0)
    
    def get_cache_client(self) -> Redis:
        """Get Redis client for API caching (DB 1)."""
        return self.get_client(1)
    
    def get_realtime_client(self) -> Redis:
        """Get Redis client for real-time data (DB 2)."""
        return self.get_client(2)
    
    def get_rate_limit_client(self) -> Redis:
        """Get Redis client for rate limiting (DB 3)."""
        return self.get_client(3)
    
    def test_connection(self) -> bool:
        """Test Redis connection."""
        try:
            client = self.get_client(0)
            response = client.ping()
            if response:
                logger.info("Redis connection successful")
                return True
            return False
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            return False
    
    def close(self):
        """Close Redis connections."""
        for client in self.clients.values():
            client.close()
        logger.info("Redis connections closed")


class DatabaseManager:
    """Main database manager that coordinates all database connections."""
    
    def __init__(self):
        self.config = DatabaseConfig()
        self.postgres = None
        self.mongodb = None
        self.redis = None
        self._initialize()
    
    def _initialize(self):
        """Initialize all database managers."""
        try:
            self.postgres = PostgreSQLManager(self.config)
            self.mongodb = MongoDBManager(self.config)
            self.redis = RedisManager(self.config)
            logger.info("Database managers initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database managers: {e}")
            raise
    
    def test_all_connections(self) -> Dict[str, bool]:
        """Test all database connections."""
        results = {}
        
        try:
            results['postgresql'] = self.postgres.test_connection()
        except Exception as e:
            logger.error(f"PostgreSQL test failed: {e}")
            results['postgresql'] = False
        
        try:
            results['mongodb'] = self.mongodb.test_connection()
        except Exception as e:
            logger.error(f"MongoDB test failed: {e}")
            results['mongodb'] = False
        
        try:
            results['redis'] = self.redis.test_connection()
        except Exception as e:
            logger.error(f"Redis test failed: {e}")
            results['redis'] = False
        
        return results
    
    def setup_databases(self):
        """Setup all databases (create tables, indexes, etc.)."""
        try:
            # Create PostgreSQL tables
            self.postgres.create_tables()
            
            # Create MongoDB indexes
            self.mongodb.create_indexes()
            
            logger.info("Database setup completed successfully")
            
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            raise
    
    def close_all(self):
        """Close all database connections."""
        if self.postgres:
            self.postgres.close()
        if self.mongodb:
            self.mongodb.close()
        if self.redis:
            self.redis.close()
        logger.info("All database connections closed")


# Global database manager instance
db_manager = None

def get_database_manager() -> DatabaseManager:
    """Get the global database manager instance."""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager

def get_postgres_session() -> Session:
    """Get a PostgreSQL session."""
    return get_database_manager().postgres.get_session()

def get_mongodb_collection(collection_name: str):
    """Get a MongoDB collection."""
    return get_database_manager().mongodb.get_collection(collection_name)

def get_redis_client(db: int = 0) -> Redis:
    """Get a Redis client."""
    return get_database_manager().redis.get_client(db)

# Context managers for database sessions
class PostgreSQLSession:
    """Context manager for PostgreSQL sessions."""
    
    def __init__(self):
        self.session = None
    
    def __enter__(self) -> Session:
        self.session = get_postgres_session()
        return self.session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            if exc_type is not None:
                self.session.rollback()
            else:
                self.session.commit()
            self.session.close()


# Utility functions
def init_databases():
    """Initialize and setup all databases."""
    manager = get_database_manager()
    
    # Test connections
    results = manager.test_all_connections()
    
    failed_connections = [db for db, success in results.items() if not success]
    if failed_connections:
        raise Exception(f"Failed to connect to: {', '.join(failed_connections)}")
    
    # Setup databases
    manager.setup_databases()
    
    logger.info("Database initialization completed successfully")

def close_databases():
    """Close all database connections."""
    global db_manager
    if db_manager:
        db_manager.close_all()
        db_manager = None


if __name__ == "__main__":
    # Test script
    try:
        print("Testing AFAS Database Connections...")
        
        manager = get_database_manager()
        results = manager.test_all_connections()
        
        print("\nConnection Results:")
        for db_name, success in results.items():
            status = "✓ SUCCESS" if success else "✗ FAILED"
            print(f"  {db_name}: {status}")
        
        if all(results.values()):
            print("\n🎉 All database connections successful!")
        else:
            print("\n❌ Some database connections failed!")
            
    except Exception as e:
        print(f"\n❌ Database test failed: {e}")
    finally:
        close_databases()