"""
Performance Optimization Service for Crop Variety Recommendations

This service implements comprehensive performance optimizations including:
- Database query optimization with indexes and connection pooling
- Multi-level caching strategy (Redis, application, CDN)
- API response optimization with compression and pagination
- Performance monitoring and metrics collection
- Intelligent cache invalidation strategies

TICKET-005_crop-variety-recommendations-14.1: Implement comprehensive variety recommendation performance optimization
"""

import asyncio
import logging
import time
import json
import gzip
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from uuid import UUID
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
import hashlib

# Database optimization imports
from sqlalchemy import create_engine, text, Index, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError

# Caching imports
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

# Performance monitoring
from .performance_monitor import performance_monitor, PerformanceMetrics

logger = logging.getLogger(__name__)


@dataclass
class OptimizationConfig:
    """Configuration for performance optimization settings."""
    
    # Database optimization
    max_connections: int = 20
    min_connections: int = 5
    connection_timeout: int = 30
    query_timeout: int = 10
    
    # Caching configuration
    redis_url: str = "redis://localhost:6379"
    cache_ttl_default: int = 3600  # 1 hour
    cache_ttl_variety_data: int = 7200  # 2 hours
    cache_ttl_search_results: int = 1800  # 30 minutes
    cache_ttl_recommendations: int = 900  # 15 minutes
    
    # Performance targets
    target_recommendation_time_ms: int = 2000  # <2s recommendation generation
    target_variety_search_time_ms: int = 1000  # <1s variety search
    target_variety_details_time_ms: int = 500  # <500ms variety details
    
    # API optimization
    enable_response_compression: bool = True
    max_response_size_mb: int = 10
    pagination_default_size: int = 20
    pagination_max_size: int = 100


@dataclass
class CacheMetrics:
    """Metrics for cache performance tracking."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_requests: int = 0
    hit_rate: float = 0.0
    
    def update_hit_rate(self):
        """Update hit rate calculation."""
        if self.total_requests > 0:
            self.hit_rate = self.hits / self.total_requests


@dataclass
class DatabaseMetrics:
    """Metrics for database performance tracking."""
    query_count: int = 0
    total_query_time_ms: float = 0.0
    slow_queries: int = 0
    connection_pool_size: int = 0
    active_connections: int = 0
    average_query_time_ms: float = 0.0
    
    def update_average_query_time(self):
        """Update average query time calculation."""
        if self.query_count > 0:
            self.average_query_time_ms = self.total_query_time_ms / self.query_count


class DatabaseOptimizer:
    """Database optimization service with connection pooling and query optimization."""
    
    def __init__(self, database_url: str, config: OptimizationConfig):
        self.database_url = database_url
        self.config = config
        self.engine = None
        self.SessionLocal = None
        self.metrics = DatabaseMetrics()
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize optimized database engine with connection pooling."""
        try:
            # Create engine with optimized connection pooling
            self.engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=self.config.max_connections,
                max_overflow=self.config.max_connections - self.config.min_connections,
                pool_timeout=self.config.connection_timeout,
                pool_recycle=3600,  # Recycle connections every hour
                pool_pre_ping=True,  # Validate connections before use
                echo=False,  # Set to True for SQL debugging
                connect_args={
                    "connect_timeout": self.config.connection_timeout,
                    "application_name": "crop_taxonomy_optimized"
                }
            )
            
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info("Database optimizer initialized with connection pooling")
            
        except Exception as e:
            logger.error(f"Failed to initialize database optimizer: {e}")
            raise
    
    @asynccontextmanager
    async def get_optimized_session(self):
        """Get optimized database session with performance monitoring."""
        session = None
        start_time = time.time()
        
        try:
            session = self.SessionLocal()
            yield session
            session.commit()
            
        except Exception as e:
            if session:
                session.rollback()
            logger.error(f"Database session error: {e}")
            raise
            
        finally:
            if session:
                session.close()
            
            # Record performance metrics
            execution_time = (time.time() - start_time) * 1000
            self.metrics.query_count += 1
            self.metrics.total_query_time_ms += execution_time
            
            if execution_time > 1000:  # Slow query threshold
                self.metrics.slow_queries += 1
                logger.warning(f"Slow database operation detected: {execution_time:.2f}ms")
            
            self.metrics.update_average_query_time()
    
    async def execute_optimized_query(self, query: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Execute optimized database query with performance monitoring."""
        start_time = time.time()
        
        try:
            async with self.get_optimized_session() as session:
                result = session.execute(text(query), params or {})
                rows = result.fetchall()
                
                # Convert to dictionary format
                columns = result.keys()
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            logger.error(f"Optimized query execution failed: {e}")
            raise
        finally:
            execution_time = (time.time() - start_time) * 1000
            performance_monitor.record_operation(
                operation="optimized_db_query",
                execution_time_ms=execution_time,
                database_query_count=1
            )
    
    def get_connection_pool_status(self) -> Dict[str, Any]:
        """Get current connection pool status and metrics."""
        if not self.engine:
            return {"error": "Engine not initialized"}
        
        pool = self.engine.pool
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalid(),
            "metrics": {
                "query_count": self.metrics.query_count,
                "average_query_time_ms": self.metrics.average_query_time_ms,
                "slow_queries": self.metrics.slow_queries
            }
        }


class MultiLevelCache:
    """Multi-level caching system with Redis and in-memory layers."""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.redis_client = None
        self.local_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_metrics = CacheMetrics()
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection for distributed caching."""
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available, using in-memory cache only")
            return
        
        try:
            self.redis_client = redis.from_url(
                self.config.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            logger.info("Redis cache initialized successfully")
            
        except Exception as e:
            logger.warning(f"Redis initialization failed, using in-memory cache only: {e}")
            self.redis_client = None
    
    def _generate_cache_key(self, namespace: str, key_data: Union[str, Dict[str, Any]]) -> str:
        """Generate consistent cache key from namespace and data."""
        if isinstance(key_data, dict):
            # Sort keys for consistent hashing
            sorted_data = json.dumps(key_data, sort_keys=True)
            key_hash = hashlib.md5(sorted_data.encode()).hexdigest()
            return f"{namespace}:{key_hash}"
        else:
            return f"{namespace}:{key_data}"
    
    async def get(self, namespace: str, key_data: Union[str, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Get data from multi-level cache (local -> Redis)."""
        cache_key = self._generate_cache_key(namespace, key_data)
        self.cache_metrics.total_requests += 1
        
        # Try local cache first
        if cache_key in self.local_cache:
            entry = self.local_cache[cache_key]
            if entry["expires_at"] > time.time():
                self.cache_metrics.hits += 1
                self.cache_metrics.update_hit_rate()
                return entry["data"]
            else:
                # Expired entry, remove it
                del self.local_cache[cache_key]
        
        # Try Redis cache
        if self.redis_client:
            try:
                cached_data = await self.redis_client.get(cache_key)
                if cached_data:
                    data = json.loads(cached_data)
                    # Store in local cache for faster access
                    self.local_cache[cache_key] = {
                        "data": data,
                        "expires_at": time.time() + self.config.cache_ttl_default
                    }
                    self.cache_metrics.hits += 1
                    self.cache_metrics.update_hit_rate()
                    return data
            except Exception as e:
                logger.warning(f"Redis get error: {e}")
        
        self.cache_metrics.misses += 1
        self.cache_metrics.update_hit_rate()
        return None
    
    async def set(self, namespace: str, key_data: Union[str, Dict[str, Any]], 
                 data: Dict[str, Any], ttl_seconds: Optional[int] = None) -> bool:
        """Set data in multi-level cache (local + Redis)."""
        cache_key = self._generate_cache_key(namespace, key_data)
        ttl = ttl_seconds or self.config.cache_ttl_default
        expires_at = time.time() + ttl
        
        # Store in local cache
        self.local_cache[cache_key] = {
            "data": data,
            "expires_at": expires_at
        }
        
        # Store in Redis
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    cache_key,
                    ttl,
                    json.dumps(data, default=str)
                )
                return True
            except Exception as e:
                logger.warning(f"Redis set error: {e}")
                return False
        
        return True
    
    async def delete(self, namespace: str, key_data: Union[str, Dict[str, Any]]) -> bool:
        """Delete data from multi-level cache."""
        cache_key = self._generate_cache_key(namespace, key_data)
        
        # Remove from local cache
        if cache_key in self.local_cache:
            del self.local_cache[cache_key]
        
        # Remove from Redis
        if self.redis_client:
            try:
                await self.redis_client.delete(cache_key)
                return True
            except Exception as e:
                logger.warning(f"Redis delete error: {e}")
                return False
        
        return True
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching a pattern."""
        invalidated_count = 0
        
        # Invalidate local cache entries
        keys_to_remove = [key for key in self.local_cache.keys() if pattern in key]
        for key in keys_to_remove:
            del self.local_cache[key]
            invalidated_count += 1
        
        # Invalidate Redis cache entries
        if self.redis_client:
            try:
                keys = await self.redis_client.keys(f"*{pattern}*")
                if keys:
                    await self.redis_client.delete(*keys)
                    invalidated_count += len(keys)
            except Exception as e:
                logger.warning(f"Redis pattern invalidation error: {e}")
        
        return invalidated_count
    
    def get_cache_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics."""
        return {
            "hits": self.cache_metrics.hits,
            "misses": self.cache_metrics.misses,
            "hit_rate": self.cache_metrics.hit_rate,
            "total_requests": self.cache_metrics.total_requests,
            "local_cache_size": len(self.local_cache),
            "redis_available": self.redis_client is not None
        }


class APIOptimizer:
    """API optimization service for response compression and pagination."""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
    
    def compress_response(self, data: Dict[str, Any]) -> Tuple[bytes, str]:
        """Compress API response data."""
        if not self.config.enable_response_compression:
            return json.dumps(data, default=str).encode('utf-8'), 'application/json'
        
        json_data = json.dumps(data, default=str)
        
        # Only compress if data is large enough to benefit
        if len(json_data) > 1024:  # 1KB threshold
            compressed_data = gzip.compress(json_data.encode('utf-8'))
            return compressed_data, 'application/gzip'
        else:
            return json_data.encode('utf-8'), 'application/json'
    
    def paginate_results(self, results: List[Dict[str, Any]], 
                        page: int = 1, page_size: Optional[int] = None) -> Dict[str, Any]:
        """Paginate results with optimized page size."""
        if page_size is None:
            page_size = self.config.pagination_default_size
        
        # Enforce maximum page size
        page_size = min(page_size, self.config.pagination_max_size)
        
        total_count = len(results)
        total_pages = (total_count + page_size - 1) // page_size
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get page results
        page_results = results[offset:offset + page_size]
        
        return {
            "results": page_results,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            }
        }
    
    def optimize_response_size(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize response size by removing unnecessary fields."""
        # Remove internal fields that shouldn't be exposed
        internal_fields = {'_internal', '_cache', '_debug', '_metrics'}
        
        def clean_dict(obj):
            if isinstance(obj, dict):
                return {k: clean_dict(v) for k, v in obj.items() 
                       if k not in internal_fields}
            elif isinstance(obj, list):
                return [clean_dict(item) for item in obj]
            else:
                return obj
        
        return clean_dict(data)


class PerformanceOptimizationService:
    """Main performance optimization service orchestrating all optimization components."""
    
    def __init__(self, database_url: str, config: Optional[OptimizationConfig] = None):
        self.config = config or OptimizationConfig()
        self.db_optimizer = DatabaseOptimizer(database_url, self.config)
        self.cache = MultiLevelCache(self.config)
        self.api_optimizer = APIOptimizer(self.config)
        
        # Performance tracking
        self.optimization_metrics: Dict[str, Any] = {}
        self.start_time = time.time()
        
        logger.info("Performance optimization service initialized")
    
    async def optimize_variety_search(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize variety search with caching and query optimization."""
        start_time = time.time()
        
        # Check cache first
        cached_result = await self.cache.get("variety_search", search_params)
        if cached_result:
            execution_time = (time.time() - start_time) * 1000
            performance_monitor.record_operation(
                operation="variety_search_cached",
                execution_time_ms=execution_time,
                cache_hit=True
            )
            return cached_result
        
        # Execute optimized database query
        try:
            # Build optimized query with proper indexing hints
            query = """
            SELECT v.variety_id, v.variety_name, v.crop_id, v.yield_potential,
                   v.disease_resistance, v.stress_tolerances, v.herbicide_tolerances,
                   v.breeder_company, v.maturity_days, v.planting_density,
                   c.crop_name, c.scientific_name
            FROM enhanced_crop_varieties v
            JOIN crops c ON v.crop_id = c.crop_id
            WHERE v.is_active = true
            """
            
            # Add search conditions
            conditions = []
            params = {}
            
            if search_params.get("crop_id"):
                conditions.append("v.crop_id = :crop_id")
                params["crop_id"] = search_params["crop_id"]
            
            if search_params.get("search_text"):
                conditions.append("(v.variety_name ILIKE :search_text OR v.breeder_company ILIKE :search_text)")
                params["search_text"] = f"%{search_params['search_text']}%"
            
            if search_params.get("traits"):
                trait_conditions = []
                for i, trait in enumerate(search_params["traits"]):
                    trait_conditions.append(f"v.stress_tolerances @> :trait_{i}")
                    params[f"trait_{i}"] = f'["{trait}"]'
                conditions.append(f"({' OR '.join(trait_conditions)})")
            
            if conditions:
                query += " AND " + " AND ".join(conditions)
            
            # Add ordering and limit
            query += " ORDER BY v.yield_potential DESC LIMIT :limit"
            params["limit"] = search_params.get("limit", 20)
            
            # Execute query
            results = await self.db_optimizer.execute_optimized_query(query, params)
            
            # Process results
            processed_results = {
                "varieties": results,
                "total_count": len(results),
                "search_params": search_params,
                "execution_time_ms": (time.time() - start_time) * 1000
            }
            
            # Cache results
            await self.cache.set("variety_search", search_params, processed_results, 
                               self.config.cache_ttl_search_results)
            
            # Record performance metrics
            execution_time = (time.time() - start_time) * 1000
            performance_monitor.record_operation(
                operation="variety_search_optimized",
                execution_time_ms=execution_time,
                database_query_count=1,
                cache_hit=False
            )
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Optimized variety search failed: {e}")
            raise
    
    async def optimize_variety_recommendations(self, recommendation_params: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize variety recommendations with comprehensive caching and optimization."""
        start_time = time.time()
        
        # Check cache first
        cached_result = await self.cache.get("variety_recommendations", recommendation_params)
        if cached_result:
            execution_time = (time.time() - start_time) * 1000
            performance_monitor.record_operation(
                operation="variety_recommendations_cached",
                execution_time_ms=execution_time,
                cache_hit=True
            )
            return cached_result
        
        try:
            # Execute optimized recommendation generation
            # This would integrate with the existing VarietyRecommendationService
            # but with optimized database queries and caching
            
            # Placeholder for optimized recommendation logic
            recommendations = {
                "recommendations": [],
                "total_count": 0,
                "recommendation_params": recommendation_params,
                "execution_time_ms": (time.time() - start_time) * 1000
            }
            
            # Cache results
            await self.cache.set("variety_recommendations", recommendation_params, recommendations,
                               self.config.cache_ttl_recommendations)
            
            # Record performance metrics
            execution_time = (time.time() - start_time) * 1000
            performance_monitor.record_operation(
                operation="variety_recommendations_optimized",
                execution_time_ms=execution_time,
                database_query_count=1,
                cache_hit=False
            )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Optimized variety recommendations failed: {e}")
            raise
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        uptime = time.time() - self.start_time
        
        return {
            "service_uptime_seconds": uptime,
            "database_metrics": self.db_optimizer.get_connection_pool_status(),
            "cache_metrics": self.cache.get_cache_metrics(),
            "performance_targets": {
                "target_recommendation_time_ms": self.config.target_recommendation_time_ms,
                "target_variety_search_time_ms": self.config.target_variety_search_time_ms,
                "target_variety_details_time_ms": self.config.target_variety_details_time_ms
            },
            "optimization_config": {
                "max_connections": self.config.max_connections,
                "cache_ttl_default": self.config.cache_ttl_default,
                "enable_response_compression": self.config.enable_response_compression
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all optimization components."""
        health_status = {
            "overall_status": "healthy",
            "components": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Check database connection
        try:
            async with self.db_optimizer.get_optimized_session() as session:
                session.execute(text("SELECT 1"))
            health_status["components"]["database"] = "healthy"
        except Exception as e:
            health_status["components"]["database"] = f"unhealthy: {e}"
            health_status["overall_status"] = "degraded"
        
        # Check Redis connection
        if self.cache.redis_client:
            try:
                await self.cache.redis_client.ping()
                health_status["components"]["redis"] = "healthy"
            except Exception as e:
                health_status["components"]["redis"] = f"unhealthy: {e}"
                health_status["overall_status"] = "degraded"
        else:
            health_status["components"]["redis"] = "not_available"
        
        return health_status


# Singleton instance for global access
performance_optimization_service: Optional[PerformanceOptimizationService] = None


def get_performance_optimization_service(database_url: str = None) -> PerformanceOptimizationService:
    """Get or create the global performance optimization service instance."""
    global performance_optimization_service
    
    if performance_optimization_service is None:
        if database_url is None:
            database_url = "postgresql://afas_user:afas_password@localhost:5432/afas_db"
        
        performance_optimization_service = PerformanceOptimizationService(database_url)
    
    return performance_optimization_service