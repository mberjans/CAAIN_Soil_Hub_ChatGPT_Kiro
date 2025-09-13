"""
Enhanced Cache Manager for AFAS Data Integration Service

Provides advanced caching capabilities including:
- Multi-tier caching strategies
- Cache warming and preloading
- Intelligent invalidation policies
- Performance monitoring and metrics
- Agricultural-specific cache optimization
- Distributed cache coordination
"""

import asyncio
import redis.asyncio as aioredis
import json
import hashlib
import zlib
import pickle
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Callable, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import structlog
from abc import ABC, abstractmethod
import time
import statistics
from collections import defaultdict, deque

logger = structlog.get_logger(__name__)


class CacheStrategy(Enum):
    """Cache strategy types."""
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    WRITE_AROUND = "write_around"
    READ_THROUGH = "read_through"
    CACHE_ASIDE = "cache_aside"


class CacheTier(Enum):
    """Cache tier levels."""
    L1_MEMORY = "l1_memory"      # In-memory cache (fastest)
    L2_REDIS = "l2_redis"        # Redis cache (fast)
    L3_PERSISTENT = "l3_persistent"  # Persistent storage (slower)


class DataType(Enum):
    """Agricultural data types for cache optimization."""
    WEATHER = "weather"
    SOIL = "soil"
    CROP = "crop"
    MARKET = "market"
    RECOMMENDATION = "recommendation"
    IMAGE_ANALYSIS = "image_analysis"
    USER_SESSION = "user_session"


@dataclass
class CacheConfig:
    """Cache configuration for different data types."""
    data_type: DataType
    ttl_seconds: int
    max_size_mb: int
    compression_enabled: bool = False
    preload_enabled: bool = False
    invalidation_strategy: str = "ttl"
    cache_strategy: CacheStrategy = CacheStrategy.CACHE_ASIDE
    priority: int = 1  # 1=highest, 5=lowest


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    key: str
    data: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    size_bytes: int
    ttl_seconds: int
    data_type: DataType
    compressed: bool = False
    
    @property
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return datetime.utcnow() > self.created_at + timedelta(seconds=self.ttl_seconds)
    
    @property
    def age_seconds(self) -> float:
        """Get age of cache entry in seconds."""
        return (datetime.utcnow() - self.created_at).total_seconds()


@dataclass
class CacheStats:
    """Cache performance statistics."""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    errors: int = 0
    total_size_bytes: int = 0
    avg_response_time_ms: float = 0.0
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0
    
    @property
    def total_operations(self) -> int:
        """Get total cache operations."""
        return self.hits + self.misses + self.sets + self.deletes


class CacheInvalidationPolicy(ABC):
    """Abstract base class for cache invalidation policies."""
    
    @abstractmethod
    async def should_invalidate(self, entry: CacheEntry, context: Dict[str, Any]) -> bool:
        """Determine if cache entry should be invalidated."""
        pass


class TTLInvalidationPolicy(CacheInvalidationPolicy):
    """Time-to-live based invalidation policy."""
    
    async def should_invalidate(self, entry: CacheEntry, context: Dict[str, Any]) -> bool:
        """Invalidate based on TTL expiration."""
        return entry.is_expired


class AgriculturalSeasonalInvalidationPolicy(CacheInvalidationPolicy):
    """Agricultural seasonal invalidation policy."""
    
    def __init__(self):
        self.seasonal_multipliers = {
            "planting_season": 0.5,    # Shorter TTL during planting
            "growing_season": 0.7,     # Moderate TTL during growing
            "harvest_season": 0.6,     # Shorter TTL during harvest
            "off_season": 1.5          # Longer TTL during off season
        }
    
    async def should_invalidate(self, entry: CacheEntry, context: Dict[str, Any]) -> bool:
        """Invalidate based on agricultural seasonality."""
        current_season = context.get("current_season", "off_season")
        multiplier = self.seasonal_multipliers.get(current_season, 1.0)
        adjusted_ttl = entry.ttl_seconds * multiplier
        
        return entry.age_seconds > adjusted_ttl


class DataFreshnessInvalidationPolicy(CacheInvalidationPolicy):
    """Data freshness based invalidation policy."""
    
    def __init__(self):
        self.freshness_requirements = {
            DataType.WEATHER: 3600,        # 1 hour
            DataType.SOIL: 86400,          # 24 hours
            DataType.MARKET: 1800,         # 30 minutes
            DataType.RECOMMENDATION: 21600, # 6 hours
            DataType.IMAGE_ANALYSIS: 3600,  # 1 hour
            DataType.USER_SESSION: 1800     # 30 minutes
        }
    
    async def should_invalidate(self, entry: CacheEntry, context: Dict[str, Any]) -> bool:
        """Invalidate based on data freshness requirements."""
        required_freshness = self.freshness_requirements.get(entry.data_type, 3600)
        return entry.age_seconds > required_freshness


class InMemoryCache:
    """L1 in-memory cache implementation."""
    
    def __init__(self, max_size_mb: int = 100):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order = deque()  # For LRU eviction
        self.current_size_bytes = 0
        self.stats = CacheStats()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get item from memory cache."""
        start_time = time.time()
        
        try:
            if key in self.cache:
                entry = self.cache[key]
                
                if entry.is_expired:
                    await self.delete(key)
                    self.stats.misses += 1
                    return None
                
                # Update access metadata
                entry.last_accessed = datetime.utcnow()
                entry.access_count += 1
                
                # Move to end for LRU
                self.access_order.remove(key)
                self.access_order.append(key)
                
                self.stats.hits += 1
                return entry.data
            else:
                self.stats.misses += 1
                return None
                
        except Exception as e:
            logger.error("Memory cache get error", key=key, error=str(e))
            self.stats.errors += 1
            return None
        finally:
            response_time = (time.time() - start_time) * 1000
            self._update_avg_response_time(response_time)
    
    async def set(self, key: str, data: Any, ttl_seconds: int, data_type: DataType) -> bool:
        """Set item in memory cache."""
        try:
            # Calculate size
            size_bytes = len(pickle.dumps(data))
            
            # Check if we need to evict items
            await self._ensure_space(size_bytes)
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                data=data,
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow(),
                access_count=1,
                size_bytes=size_bytes,
                ttl_seconds=ttl_seconds,
                data_type=data_type
            )
            
            # Remove old entry if exists
            if key in self.cache:
                old_entry = self.cache[key]
                self.current_size_bytes -= old_entry.size_bytes
                self.access_order.remove(key)
            
            # Add new entry
            self.cache[key] = entry
            self.access_order.append(key)
            self.current_size_bytes += size_bytes
            self.stats.sets += 1
            
            return True
            
        except Exception as e:
            logger.error("Memory cache set error", key=key, error=str(e))
            self.stats.errors += 1
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete item from memory cache."""
        try:
            if key in self.cache:
                entry = self.cache[key]
                self.current_size_bytes -= entry.size_bytes
                del self.cache[key]
                self.access_order.remove(key)
                self.stats.deletes += 1
                return True
            return False
            
        except Exception as e:
            logger.error("Memory cache delete error", key=key, error=str(e))
            self.stats.errors += 1
            return False
    
    async def _ensure_space(self, required_bytes: int):
        """Ensure enough space by evicting LRU items if necessary."""
        while (self.current_size_bytes + required_bytes > self.max_size_bytes and 
               self.access_order):
            # Evict least recently used item
            lru_key = self.access_order.popleft()
            if lru_key in self.cache:
                entry = self.cache[lru_key]
                self.current_size_bytes -= entry.size_bytes
                del self.cache[lru_key]
                self.stats.evictions += 1
    
    def _update_avg_response_time(self, response_time_ms: float):
        """Update average response time using exponential moving average."""
        alpha = 0.1  # Smoothing factor
        if self.stats.avg_response_time_ms == 0:
            self.stats.avg_response_time_ms = response_time_ms
        else:
            self.stats.avg_response_time_ms = (
                alpha * response_time_ms + 
                (1 - alpha) * self.stats.avg_response_time_ms
            )
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        self.stats.total_size_bytes = self.current_size_bytes
        return self.stats
    
    async def clear(self):
        """Clear all cache entries."""
        self.cache.clear()
        self.access_order.clear()
        self.current_size_bytes = 0


class RedisCache:
    """L2 Redis cache implementation with advanced features."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", db: int = 1):
        self.redis_url = redis_url
        self.db = db
        self.redis_client = None
        self.stats = CacheStats()
        self.compression_threshold = 1024  # Compress data larger than 1KB
    
    async def connect(self):
        """Connect to Redis."""
        try:
            self.redis_client = aioredis.from_url(f"{self.redis_url}/{self.db}")
            await self.redis_client.ping()
            logger.info("Connected to Redis cache", db=self.db)
        except Exception as e:
            logger.error("Failed to connect to Redis", error=str(e), db=self.db)
            self.redis_client = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get item from Redis cache."""
        if not self.redis_client:
            return None
        
        start_time = time.time()
        
        try:
            # Get data and metadata
            pipe = self.redis_client.pipeline()
            pipe.hget(f"cache:{key}", "data")
            pipe.hget(f"cache:{key}", "compressed")
            pipe.hget(f"cache:{key}", "created_at")
            pipe.hincrby(f"cache:{key}", "access_count", 1)
            pipe.hset(f"cache:{key}", "last_accessed", datetime.utcnow().isoformat())
            
            results = await pipe.execute()
            
            if results[0] is None:
                self.stats.misses += 1
                return None
            
            # Deserialize data
            data = results[0]
            is_compressed = results[1] == "true"
            
            if is_compressed:
                data = zlib.decompress(data.encode('latin1'))
            
            deserialized_data = json.loads(data)
            self.stats.hits += 1
            
            return deserialized_data
            
        except Exception as e:
            logger.error("Redis cache get error", key=key, error=str(e))
            self.stats.errors += 1
            return None
        finally:
            response_time = (time.time() - start_time) * 1000
            self._update_avg_response_time(response_time)
    
    async def set(self, key: str, data: Any, ttl_seconds: int, data_type: DataType) -> bool:
        """Set item in Redis cache."""
        if not self.redis_client:
            return False
        
        try:
            # Serialize data
            serialized_data = json.dumps(data, default=str)
            
            # Compress if data is large
            compressed = False
            if len(serialized_data) > self.compression_threshold:
                compressed_data = zlib.compress(serialized_data.encode())
                if len(compressed_data) < len(serialized_data):
                    serialized_data = compressed_data.decode('latin1')
                    compressed = True
            
            # Store data with metadata
            cache_data = {
                "data": serialized_data,
                "compressed": str(compressed).lower(),
                "created_at": datetime.utcnow().isoformat(),
                "last_accessed": datetime.utcnow().isoformat(),
                "access_count": "1",
                "data_type": data_type.value,
                "size_bytes": str(len(serialized_data))
            }
            
            # Use pipeline for atomic operation
            pipe = self.redis_client.pipeline()
            pipe.hset(f"cache:{key}", mapping=cache_data)
            pipe.expire(f"cache:{key}", ttl_seconds)
            
            await pipe.execute()
            self.stats.sets += 1
            
            return True
            
        except Exception as e:
            logger.error("Redis cache set error", key=key, error=str(e))
            self.stats.errors += 1
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete item from Redis cache."""
        if not self.redis_client:
            return False
        
        try:
            result = await self.redis_client.delete(f"cache:{key}")
            if result > 0:
                self.stats.deletes += 1
                return True
            return False
            
        except Exception as e:
            logger.error("Redis cache delete error", key=key, error=str(e))
            self.stats.errors += 1
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear cache entries matching pattern."""
        if not self.redis_client:
            return 0
        
        try:
            keys = await self.redis_client.keys(f"cache:{pattern}")
            if keys:
                deleted = await self.redis_client.delete(*keys)
                self.stats.deletes += deleted
                return deleted
            return 0
        except Exception as e:
            logger.error("Redis cache clear pattern error", pattern=pattern, error=str(e))
            self.stats.errors += 1
            return 0
    
    async def get_cache_info(self) -> Dict[str, Any]:
        """Get cache information and statistics."""
        if not self.redis_client:
            return {}
        
        try:
            info = await self.redis_client.info()
            return {
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0)
            }
        except Exception as e:
            logger.error("Failed to get Redis info", error=str(e))
            return {}
    
    def _update_avg_response_time(self, response_time_ms: float):
        """Update average response time using exponential moving average."""
        alpha = 0.1
        if self.stats.avg_response_time_ms == 0:
            self.stats.avg_response_time_ms = response_time_ms
        else:
            self.stats.avg_response_time_ms = (
                alpha * response_time_ms + 
                (1 - alpha) * self.stats.avg_response_time_ms
            )
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        return self.stats
    
    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()


class CacheWarmer:
    """Cache warming service for preloading frequently accessed data."""
    
    def __init__(self, cache_manager):
        self.cache_manager = cache_manager
        self.warming_strategies = {}
        self.warming_schedule = {}
    
    def register_warming_strategy(self, data_type: DataType, strategy: Callable):
        """Register a cache warming strategy for a data type."""
        self.warming_strategies[data_type] = strategy
        logger.info("Registered cache warming strategy", data_type=data_type.value)
    
    async def warm_cache(self, data_type: DataType, context: Dict[str, Any] = None):
        """Warm cache for specific data type."""
        if data_type not in self.warming_strategies:
            logger.warning("No warming strategy for data type", data_type=data_type.value)
            return
        
        try:
            strategy = self.warming_strategies[data_type]
            await strategy(self.cache_manager, context or {})
            logger.info("Cache warming completed", data_type=data_type.value)
        except Exception as e:
            logger.error("Cache warming failed", data_type=data_type.value, error=str(e))
    
    async def warm_weather_cache(self, cache_manager, context: Dict[str, Any]):
        """Warm weather data cache for common locations."""
        common_locations = context.get("common_locations", [
            {"lat": 42.0308, "lon": -93.6319},  # Ames, Iowa
            {"lat": 40.1164, "lon": -88.2434},  # Champaign, Illinois
            {"lat": 39.7391, "lon": -89.2661},  # Springfield, Illinois
        ])
        
        for location in common_locations:
            cache_key = f"weather:{location['lat']}_{location['lon']}"
            # This would call the actual weather service
            # For now, we'll just log the warming attempt
            logger.info("Warming weather cache", location=location)
    
    async def warm_soil_cache(self, cache_manager, context: Dict[str, Any]):
        """Warm soil data cache for agricultural regions."""
        agricultural_regions = context.get("agricultural_regions", [
            {"lat": 42.0, "lon": -93.6, "region": "Iowa Corn Belt"},
            {"lat": 40.1, "lon": -88.2, "region": "Illinois Prairie"},
        ])
        
        for region in agricultural_regions:
            cache_key = f"soil:{region['lat']}_{region['lon']}"
            logger.info("Warming soil cache", region=region)


class EnhancedCacheManager:
    """Enhanced multi-tier cache manager with advanced features."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        
        # Cache tiers
        self.l1_cache = InMemoryCache(max_size_mb=100)
        self.l2_cache = RedisCache(redis_url, db=1)
        
        # Cache configurations
        self.cache_configs = self._initialize_cache_configs()
        
        # Invalidation policies
        self.invalidation_policies = [
            TTLInvalidationPolicy(),
            AgriculturalSeasonalInvalidationPolicy(),
            DataFreshnessInvalidationPolicy()
        ]
        
        # Cache warmer
        self.cache_warmer = CacheWarmer(self)
        self._register_warming_strategies()
        
        # Metrics and monitoring
        self.global_stats = CacheStats()
        self.performance_metrics = defaultdict(list)
        
        # Background tasks
        self.cleanup_task = None
        self.warming_task = None
    
    def _initialize_cache_configs(self) -> Dict[DataType, CacheConfig]:
        """Initialize cache configurations for different data types."""
        return {
            DataType.WEATHER: CacheConfig(
                data_type=DataType.WEATHER,
                ttl_seconds=3600,  # 1 hour
                max_size_mb=50,
                compression_enabled=True,
                preload_enabled=True,
                priority=1
            ),
            DataType.SOIL: CacheConfig(
                data_type=DataType.SOIL,
                ttl_seconds=86400,  # 24 hours
                max_size_mb=100,
                compression_enabled=True,
                preload_enabled=True,
                priority=2
            ),
            DataType.CROP: CacheConfig(
                data_type=DataType.CROP,
                ttl_seconds=7200,  # 2 hours
                max_size_mb=30,
                compression_enabled=False,
                preload_enabled=False,
                priority=3
            ),
            DataType.MARKET: CacheConfig(
                data_type=DataType.MARKET,
                ttl_seconds=1800,  # 30 minutes
                max_size_mb=20,
                compression_enabled=False,
                preload_enabled=True,
                priority=1
            ),
            DataType.RECOMMENDATION: CacheConfig(
                data_type=DataType.RECOMMENDATION,
                ttl_seconds=21600,  # 6 hours
                max_size_mb=200,
                compression_enabled=True,
                preload_enabled=False,
                priority=2
            ),
            DataType.IMAGE_ANALYSIS: CacheConfig(
                data_type=DataType.IMAGE_ANALYSIS,
                ttl_seconds=3600,  # 1 hour
                max_size_mb=500,
                compression_enabled=True,
                preload_enabled=False,
                priority=4
            ),
            DataType.USER_SESSION: CacheConfig(
                data_type=DataType.USER_SESSION,
                ttl_seconds=1800,  # 30 minutes
                max_size_mb=10,
                compression_enabled=False,
                preload_enabled=False,
                priority=1
            )
        }
    
    def _register_warming_strategies(self):
        """Register cache warming strategies."""
        self.cache_warmer.register_warming_strategy(
            DataType.WEATHER, 
            self.cache_warmer.warm_weather_cache
        )
        self.cache_warmer.register_warming_strategy(
            DataType.SOIL, 
            self.cache_warmer.warm_soil_cache
        )
    
    async def connect(self):
        """Connect to cache backends."""
        await self.l2_cache.connect()
        
        # Start background tasks
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        self.warming_task = asyncio.create_task(self._warming_loop())
        
        logger.info("Enhanced cache manager connected and initialized")
    
    async def get(self, key: str, data_type: DataType = DataType.WEATHER) -> Optional[Any]:
        """Get data from cache with multi-tier lookup."""
        start_time = time.time()
        
        try:
            # Try L1 cache first
            data = await self.l1_cache.get(key)
            if data is not None:
                self._record_performance_metric("l1_hit", time.time() - start_time)
                return data
            
            # Try L2 cache
            data = await self.l2_cache.get(key)
            if data is not None:
                # Promote to L1 cache
                config = self.cache_configs.get(data_type)
                if config:
                    await self.l1_cache.set(key, data, config.ttl_seconds, data_type)
                
                self._record_performance_metric("l2_hit", time.time() - start_time)
                return data
            
            # Cache miss
            self._record_performance_metric("miss", time.time() - start_time)
            return None
            
        except Exception as e:
            logger.error("Cache get error", key=key, error=str(e))
            return None
    
    async def set(self, key: str, data: Any, data_type: DataType = DataType.WEATHER) -> bool:
        """Set data in cache with multi-tier storage."""
        config = self.cache_configs.get(data_type)
        if not config:
            logger.warning("No cache config for data type", data_type=data_type.value)
            return False
        
        try:
            # Set in both L1 and L2 caches
            l1_success = await self.l1_cache.set(key, data, config.ttl_seconds, data_type)
            l2_success = await self.l2_cache.set(key, data, config.ttl_seconds, data_type)
            
            return l1_success or l2_success
            
        except Exception as e:
            logger.error("Cache set error", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete data from all cache tiers."""
        try:
            l1_success = await self.l1_cache.delete(key)
            l2_success = await self.l2_cache.delete(key)
            
            return l1_success or l2_success
            
        except Exception as e:
            logger.error("Cache delete error", key=key, error=str(e))
            return False
    
    async def clear_by_pattern(self, pattern: str) -> int:
        """Clear cache entries matching pattern from all tiers."""
        try:
            # Clear L2 cache (Redis supports pattern matching)
            l2_cleared = await self.l2_cache.clear_pattern(pattern)
            
            # Clear L1 cache (need to check each key)
            l1_cleared = 0
            keys_to_delete = []
            for key in self.l1_cache.cache.keys():
                if pattern in key:
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                if await self.l1_cache.delete(key):
                    l1_cleared += 1
            
            logger.info("Cache cleared by pattern", pattern=pattern, 
                       l1_cleared=l1_cleared, l2_cleared=l2_cleared)
            
            return l1_cleared + l2_cleared
            
        except Exception as e:
            logger.error("Cache clear pattern error", pattern=pattern, error=str(e))
            return 0
    
    async def invalidate_by_policy(self, context: Dict[str, Any] = None):
        """Invalidate cache entries based on configured policies."""
        context = context or {}
        invalidated_count = 0
        
        try:
            # Check L1 cache entries
            keys_to_invalidate = []
            for key, entry in self.l1_cache.cache.items():
                for policy in self.invalidation_policies:
                    if await policy.should_invalidate(entry, context):
                        keys_to_invalidate.append(key)
                        break
            
            for key in keys_to_invalidate:
                if await self.delete(key):
                    invalidated_count += 1
            
            logger.info("Cache invalidation completed", invalidated_count=invalidated_count)
            return invalidated_count
            
        except Exception as e:
            logger.error("Cache invalidation error", error=str(e))
            return 0
    
    def generate_cache_key(self, source: str, operation: str, **params) -> str:
        """Generate consistent cache key."""
        param_str = json.dumps(params, sort_keys=True, default=str)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()[:8]
        return f"afas:{source}:{operation}:{param_hash}"
    
    async def warm_cache(self, data_types: List[DataType] = None, context: Dict[str, Any] = None):
        """Warm cache for specified data types."""
        data_types = data_types or [DataType.WEATHER, DataType.SOIL, DataType.MARKET]
        
        for data_type in data_types:
            config = self.cache_configs.get(data_type)
            if config and config.preload_enabled:
                await self.cache_warmer.warm_cache(data_type, context)
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        l1_stats = self.l1_cache.get_stats()
        l2_stats = self.l2_cache.get_stats()
        
        return {
            "l1_cache": {
                "hits": l1_stats.hits,
                "misses": l1_stats.misses,
                "hit_rate": l1_stats.hit_rate,
                "size_bytes": l1_stats.total_size_bytes,
                "avg_response_time_ms": l1_stats.avg_response_time_ms,
                "evictions": l1_stats.evictions
            },
            "l2_cache": {
                "hits": l2_stats.hits,
                "misses": l2_stats.misses,
                "hit_rate": l2_stats.hit_rate,
                "avg_response_time_ms": l2_stats.avg_response_time_ms
            },
            "performance_metrics": {
                "l1_hit_avg_ms": statistics.mean(self.performance_metrics.get("l1_hit", [0])),
                "l2_hit_avg_ms": statistics.mean(self.performance_metrics.get("l2_hit", [0])),
                "miss_avg_ms": statistics.mean(self.performance_metrics.get("miss", [0]))
            },
            "cache_configs": {
                dt.value: asdict(config) for dt, config in self.cache_configs.items()
            }
        }
    
    def _record_performance_metric(self, metric_type: str, duration: float):
        """Record performance metric."""
        self.performance_metrics[metric_type].append(duration * 1000)  # Convert to ms
        
        # Keep only last 1000 measurements
        if len(self.performance_metrics[metric_type]) > 1000:
            self.performance_metrics[metric_type] = self.performance_metrics[metric_type][-1000:]
    
    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                await self.invalidate_by_policy()
            except Exception as e:
                logger.error("Cache cleanup loop error", error=str(e))
    
    async def _warming_loop(self):
        """Background cache warming loop."""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                await self.warm_cache()
            except Exception as e:
                logger.error("Cache warming loop error", error=str(e))
    
    async def close(self):
        """Close cache manager and cleanup resources."""
        # Cancel background tasks
        if self.cleanup_task:
            self.cleanup_task.cancel()
        if self.warming_task:
            self.warming_task.cancel()
        
        # Close cache connections
        await self.l1_cache.clear()
        await self.l2_cache.close()
        
        logger.info("Enhanced cache manager closed")


# Factory function for easy instantiation
async def create_enhanced_cache_manager(redis_url: str = "redis://localhost:6379") -> EnhancedCacheManager:
    """Create and initialize enhanced cache manager."""
    cache_manager = EnhancedCacheManager(redis_url)
    await cache_manager.connect()
    return cache_manager