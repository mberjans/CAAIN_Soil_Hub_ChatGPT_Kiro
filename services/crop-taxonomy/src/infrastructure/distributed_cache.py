"""
Distributed Caching System for Crop Variety Recommendations

This module implements distributed caching with intelligent cache invalidation,
data partitioning, and CDN integration for scalable data access.

TICKET-005_crop-variety-recommendations-14.2: Add comprehensive scalability improvements and infrastructure
"""

import asyncio
import logging
import time
import json
import hashlib
import pickle
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union, Callable, Set
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from enum import Enum
import aioredis
from aioredis import Redis
import aiohttp
from aiohttp import ClientSession, ClientTimeout

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """Cache strategies for different data types."""
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    WRITE_AROUND = "write_around"
    READ_THROUGH = "read_through"
    CACHE_ASIDE = "cache_aside"


class CacheLevel(Enum):
    """Cache levels in the hierarchy."""
    L1_LOCAL = "l1_local"      # In-memory cache
    L2_REDIS = "l2_redis"      # Redis distributed cache
    L3_DATABASE = "l3_database"  # Database cache
    L4_CDN = "l4_cdn"          # CDN cache


@dataclass
class CacheEntry:
    """Represents a cache entry with metadata."""
    key: str
    value: Any
    ttl: int
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    size_bytes: int = 0
    tags: Set[str] = field(default_factory=set)
    level: CacheLevel = CacheLevel.L2_REDIS


@dataclass
class CacheStats:
    """Cache performance statistics."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_size_bytes: int = 0
    hit_rate: float = 0.0
    miss_rate: float = 0.0
    avg_response_time_ms: float = 0.0


class LocalCache:
    """In-memory L1 cache with LRU eviction."""
    
    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []
        self.current_size_bytes = 0
        self.stats = CacheStats()
        
    async def get(self, key: str) -> Optional[Any]:
        """Get value from local cache."""
        if key in self.cache:
            entry = self.cache[key]
            
            # Check TTL
            if self._is_expired(entry):
                await self.delete(key)
                self.stats.misses += 1
                return None
                
            # Update access info
            entry.last_accessed = datetime.utcnow()
            entry.access_count += 1
            
            # Move to end of access order
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)
            
            self.stats.hits += 1
            return entry.value
            
        self.stats.misses += 1
        return None
        
    async def set(self, key: str, value: Any, ttl: int = 3600, tags: Set[str] = None):
        """Set value in local cache."""
        # Calculate size
        try:
            size_bytes = len(pickle.dumps(value))
        except:
            size_bytes = 1024  # Default size
            
        # Check if we need to evict
        await self._evict_if_needed(size_bytes)
        
        # Create entry
        entry = CacheEntry(
            key=key,
            value=value,
            ttl=ttl,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
            size_bytes=size_bytes,
            tags=tags or set(),
            level=CacheLevel.L1_LOCAL
        )
        
        # Remove old entry if exists
        if key in self.cache:
            old_entry = self.cache[key]
            self.current_size_bytes -= old_entry.size_bytes
            
        # Add new entry
        self.cache[key] = entry
        self.current_size_bytes += size_bytes
        
        # Update access order
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
        
    async def delete(self, key: str):
        """Delete key from local cache."""
        if key in self.cache:
            entry = self.cache[key]
            self.current_size_bytes -= entry.size_bytes
            del self.cache[key]
            
            if key in self.access_order:
                self.access_order.remove(key)
                
    async def delete_by_tags(self, tags: Set[str]):
        """Delete entries matching any of the tags."""
        keys_to_delete = []
        for key, entry in self.cache.items():
            if entry.tags.intersection(tags):
                keys_to_delete.append(key)
                
        for key in keys_to_delete:
            await self.delete(key)
            
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if cache entry is expired."""
        if entry.ttl <= 0:
            return False
        return datetime.utcnow() > entry.created_at + timedelta(seconds=entry.ttl)
        
    async def _evict_if_needed(self, new_size_bytes: int):
        """Evict entries if cache is full."""
        while (len(self.cache) >= self.max_size or 
               self.current_size_bytes + new_size_bytes > self.max_memory_bytes):
            if not self.access_order:
                break
                
            # Evict least recently used
            lru_key = self.access_order[0]
            await self.delete(lru_key)
            self.stats.evictions += 1
            
    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        total_requests = self.stats.hits + self.stats.misses
        if total_requests > 0:
            self.stats.hit_rate = self.stats.hits / total_requests
            self.stats.miss_rate = self.stats.misses / total_requests
        self.stats.total_size_bytes = self.current_size_bytes
        return self.stats


class DistributedCache:
    """Distributed cache with multiple levels and intelligent routing."""
    
    def __init__(self, 
                 redis_url: str = "redis://localhost:6379",
                 cdn_url: str = None,
                 cache_strategy: CacheStrategy = CacheStrategy.CACHE_ASIDE):
        self.redis_url = redis_url
        self.cdn_url = cdn_url
        self.cache_strategy = cache_strategy
        self.local_cache = LocalCache()
        self.redis: Optional[Redis] = None
        self.cdn_session: Optional[ClientSession] = None
        self.partition_map: Dict[str, str] = {}
        self.cache_tags: Dict[str, Set[str]] = {}
        
    async def initialize(self):
        """Initialize the distributed cache."""
        try:
            # Initialize Redis connection
            self.redis = await aioredis.from_url(self.redis_url)
            await self.redis.ping()
            logger.info("Redis connection established for distributed cache")
            
            # Initialize CDN connection if available
            if self.cdn_url:
                self.cdn_session = ClientSession(
                    timeout=ClientTimeout(total=10),
                    connector=aiohttp.TCPConnector(limit=100)
                )
                logger.info(f"CDN connection established: {self.cdn_url}")
                
            # Initialize partition map
            await self._initialize_partitions()
            
            logger.info("Distributed cache initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize distributed cache: {e}")
            raise
            
    async def _initialize_partitions(self):
        """Initialize cache partitions for data distribution."""
        # Create partitions based on data types
        self.partition_map = {
            "variety_data": "partition_1",
            "soil_data": "partition_2", 
            "climate_data": "partition_3",
            "recommendations": "partition_4",
            "user_data": "partition_5"
        }
        
        # Set up Redis partitions
        for partition_name in self.partition_map.values():
            await self.redis.sadd("cache_partitions", partition_name)
            
    async def get(self, key: str, data_type: str = "general") -> Optional[Any]:
        """Get value from distributed cache."""
        start_time = time.time()
        
        try:
            # Try L1 cache first
            value = await self.local_cache.get(key)
            if value is not None:
                return value
                
            # Try L2 Redis cache
            value = await self._get_from_redis(key, data_type)
            if value is not None:
                # Populate L1 cache
                await self.local_cache.set(key, value, ttl=300)  # 5 min TTL for L1
                return value
                
            # Try L3 Database cache (if implemented)
            value = await self._get_from_database_cache(key, data_type)
            if value is not None:
                # Populate L2 and L1 caches
                await self._set_to_redis(key, value, data_type, ttl=3600)
                await self.local_cache.set(key, value, ttl=300)
                return value
                
            # Try L4 CDN cache
            if self.cdn_url:
                value = await self._get_from_cdn(key, data_type)
                if value is not None:
                    # Populate all cache levels
                    await self._set_to_redis(key, value, data_type, ttl=7200)
                    await self.local_cache.set(key, value, ttl=300)
                    return value
                    
            return None
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
        finally:
            response_time = (time.time() - start_time) * 1000
            logger.debug(f"Cache get for {key} took {response_time:.2f}ms")
            
    async def set(self, key: str, value: Any, ttl: int = 3600, 
                 data_type: str = "general", tags: Set[str] = None):
        """Set value in distributed cache."""
        try:
            # Set tags
            if tags:
                self.cache_tags[key] = tags
                
            # Apply cache strategy
            if self.cache_strategy == CacheStrategy.WRITE_THROUGH:
                # Write to all levels immediately
                await self.local_cache.set(key, value, ttl=min(ttl, 300), tags=tags)
                await self._set_to_redis(key, value, data_type, ttl)
                if self.cdn_url:
                    await self._set_to_cdn(key, value, data_type, ttl)
                    
            elif self.cache_strategy == CacheStrategy.WRITE_BEHIND:
                # Write to L1 immediately, others asynchronously
                await self.local_cache.set(key, value, ttl=min(ttl, 300), tags=tags)
                asyncio.create_task(self._set_to_redis(key, value, data_type, ttl))
                if self.cdn_url:
                    asyncio.create_task(self._set_to_cdn(key, value, data_type, ttl))
                    
            elif self.cache_strategy == CacheStrategy.WRITE_AROUND:
                # Write to database, invalidate caches
                await self._write_to_database(key, value, data_type)
                await self.invalidate_by_tags(tags or set())
                
            else:  # CACHE_ASIDE
                # Write to cache only
                await self.local_cache.set(key, value, ttl=min(ttl, 300), tags=tags)
                await self._set_to_redis(key, value, data_type, ttl)
                
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            
    async def delete(self, key: str, data_type: str = "general"):
        """Delete key from all cache levels."""
        try:
            # Delete from all levels
            await self.local_cache.delete(key)
            await self._delete_from_redis(key, data_type)
            if self.cdn_url:
                await self._delete_from_cdn(key, data_type)
                
            # Remove from tags
            if key in self.cache_tags:
                del self.cache_tags[key]
                
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            
    async def invalidate_by_tags(self, tags: Set[str]):
        """Invalidate cache entries by tags."""
        try:
            # Invalidate local cache
            await self.local_cache.delete_by_tags(tags)
            
            # Invalidate Redis cache
            await self._invalidate_redis_by_tags(tags)
            
            # Invalidate CDN cache
            if self.cdn_url:
                await self._invalidate_cdn_by_tags(tags)
                
        except Exception as e:
            logger.error(f"Cache invalidation error for tags {tags}: {e}")
            
    async def _get_from_redis(self, key: str, data_type: str) -> Optional[Any]:
        """Get value from Redis cache."""
        try:
            partition = self.partition_map.get(data_type, "default")
            redis_key = f"{partition}:{key}"
            
            data = await self.redis.get(redis_key)
            if data:
                return pickle.loads(data)
            return None
            
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {e}")
            return None
            
    async def _set_to_redis(self, key: str, value: Any, data_type: str, ttl: int):
        """Set value to Redis cache."""
        try:
            partition = self.partition_map.get(data_type, "default")
            redis_key = f"{partition}:{key}"
            
            data = pickle.dumps(value)
            await self.redis.setex(redis_key, ttl, data)
            
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {e}")
            
    async def _delete_from_redis(self, key: str, data_type: str):
        """Delete key from Redis cache."""
        try:
            partition = self.partition_map.get(data_type, "default")
            redis_key = f"{partition}:{key}"
            await self.redis.delete(redis_key)
            
        except Exception as e:
            logger.error(f"Redis delete error for key {key}: {e}")
            
    async def _invalidate_redis_by_tags(self, tags: Set[str]):
        """Invalidate Redis cache entries by tags."""
        try:
            # Find keys with matching tags
            for key, key_tags in self.cache_tags.items():
                if key_tags.intersection(tags):
                    # Delete from all partitions
                    for partition in self.partition_map.values():
                        redis_key = f"{partition}:{key}"
                        await self.redis.delete(redis_key)
                        
        except Exception as e:
            logger.error(f"Redis invalidation error for tags {tags}: {e}")
            
    async def _get_from_database_cache(self, key: str, data_type: str) -> Optional[Any]:
        """Get value from database cache (placeholder)."""
        # This would implement database-level caching
        # For now, return None to indicate cache miss
        return None
        
    async def _write_to_database(self, key: str, value: Any, data_type: str):
        """Write value to database (placeholder)."""
        # This would implement database writes
        pass
        
    async def _get_from_cdn(self, key: str, data_type: str) -> Optional[Any]:
        """Get value from CDN cache."""
        if not self.cdn_session:
            return None
            
        try:
            url = f"{self.cdn_url}/cache/{data_type}/{key}"
            async with self.cdn_session.get(url) as response:
                if response.status == 200:
                    data = await response.read()
                    return pickle.loads(data)
            return None
            
        except Exception as e:
            logger.error(f"CDN get error for key {key}: {e}")
            return None
            
    async def _set_to_cdn(self, key: str, value: Any, data_type: str, ttl: int):
        """Set value to CDN cache."""
        if not self.cdn_session:
            return
            
        try:
            url = f"{self.cdn_url}/cache/{data_type}/{key}"
            data = pickle.dumps(value)
            headers = {"Content-Type": "application/octet-stream", "Cache-Control": f"max-age={ttl}"}
            
            async with self.cdn_session.put(url, data=data, headers=headers) as response:
                if response.status not in [200, 201]:
                    logger.warning(f"CDN set failed for key {key}: {response.status}")
                    
        except Exception as e:
            logger.error(f"CDN set error for key {key}: {e}")
            
    async def _delete_from_cdn(self, key: str, data_type: str):
        """Delete key from CDN cache."""
        if not self.cdn_session:
            return
            
        try:
            url = f"{self.cdn_url}/cache/{data_type}/{key}"
            async with self.cdn_session.delete(url) as response:
                if response.status not in [200, 204]:
                    logger.warning(f"CDN delete failed for key {key}: {response.status}")
                    
        except Exception as e:
            logger.error(f"CDN delete error for key {key}: {e}")
            
    async def _invalidate_cdn_by_tags(self, tags: Set[str]):
        """Invalidate CDN cache entries by tags."""
        if not self.cdn_session:
            return
            
        try:
            # Send invalidation request to CDN
            url = f"{self.cdn_url}/cache/invalidate"
            data = {"tags": list(tags)}
            
            async with self.cdn_session.post(url, json=data) as response:
                if response.status != 200:
                    logger.warning(f"CDN invalidation failed: {response.status}")
                    
        except Exception as e:
            logger.error(f"CDN invalidation error for tags {tags}: {e}")
            
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        local_stats = self.local_cache.get_stats()
        
        # Get Redis stats
        redis_info = await self.redis.info("memory")
        redis_stats = {
            "used_memory": redis_info.get("used_memory", 0),
            "used_memory_peak": redis_info.get("used_memory_peak", 0),
            "keyspace_hits": redis_info.get("keyspace_hits", 0),
            "keyspace_misses": redis_info.get("keyspace_misses", 0)
        }
        
        return {
            "local_cache": {
                "hits": local_stats.hits,
                "misses": local_stats.misses,
                "hit_rate": local_stats.hit_rate,
                "size_bytes": local_stats.total_size_bytes,
                "entries": len(self.local_cache.cache)
            },
            "redis_cache": redis_stats,
            "partitions": list(self.partition_map.keys()),
            "total_tagged_keys": len(self.cache_tags)
        }
        
    async def shutdown(self):
        """Shutdown the distributed cache."""
        if self.redis:
            await self.redis.close()
            
        if self.cdn_session:
            await self.cdn_session.close()
            
        logger.info("Distributed cache shutdown complete")


# Global distributed cache instance
distributed_cache = DistributedCache()


async def get_distributed_cache() -> DistributedCache:
    """Get the global distributed cache instance."""
    if not distributed_cache.redis:
        await distributed_cache.initialize()
    return distributed_cache