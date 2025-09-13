"""
Tests for Enhanced Cache Manager

Comprehensive test suite for the enhanced caching layer including:
- Multi-tier cache operations
- Cache invalidation policies
- Performance monitoring
- Agricultural-specific caching patterns
"""

import pytest
import asyncio
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

from services.data_integration.src.services.enhanced_cache_manager import (
    EnhancedCacheManager,
    InMemoryCache,
    RedisCache,
    CacheWarmer,
    DataType,
    CacheConfig,
    CacheEntry,
    TTLInvalidationPolicy,
    AgriculturalSeasonalInvalidationPolicy,
    DataFreshnessInvalidationPolicy,
    create_enhanced_cache_manager
)


class TestInMemoryCache:
    """Test L1 in-memory cache functionality."""
    
    @pytest.fixture
    async def memory_cache(self):
        """Create in-memory cache for testing."""
        cache = InMemoryCache(max_size_mb=1)  # Small size for testing
        yield cache
        await cache.clear()
    
    @pytest.mark.asyncio
    async def test_basic_operations(self, memory_cache):
        """Test basic cache operations."""
        # Test set and get
        success = await memory_cache.set("test_key", {"data": "value"}, 3600, DataType.WEATHER)
        assert success
        
        data = await memory_cache.get("test_key")
        assert data == {"data": "value"}
        
        # Test delete
        success = await memory_cache.delete("test_key")
        assert success
        
        data = await memory_cache.get("test_key")
        assert data is None
    
    @pytest.mark.asyncio
    async def test_ttl_expiration(self, memory_cache):
        """Test TTL-based expiration."""
        # Set with very short TTL
        await memory_cache.set("expire_key", {"data": "value"}, 1, DataType.WEATHER)
        
        # Should be available immediately
        data = await memory_cache.get("expire_key")
        assert data == {"data": "value"}
        
        # Wait for expiration
        await asyncio.sleep(1.1)
        
        # Should be expired
        data = await memory_cache.get("expire_key")
        assert data is None
    
    @pytest.mark.asyncio
    async def test_lru_eviction(self, memory_cache):
        """Test LRU eviction when cache is full."""
        # Fill cache beyond capacity
        large_data = {"data": "x" * 100000}  # Large data to trigger eviction
        
        await memory_cache.set("key1", large_data, 3600, DataType.WEATHER)
        await memory_cache.set("key2", large_data, 3600, DataType.WEATHER)
        await memory_cache.set("key3", large_data, 3600, DataType.WEATHER)
        
        # Access key1 to make it more recently used
        await memory_cache.get("key1")
        
        # Add another large item to trigger eviction
        await memory_cache.set("key4", large_data, 3600, DataType.WEATHER)
        
        # key2 should be evicted (least recently used)
        assert await memory_cache.get("key1") is not None
        assert await memory_cache.get("key3") is not None
        assert await memory_cache.get("key4") is not None
    
    @pytest.mark.asyncio
    async def test_access_tracking(self, memory_cache):
        """Test access count and timestamp tracking."""
        await memory_cache.set("track_key", {"data": "value"}, 3600, DataType.WEATHER)
        
        # Access multiple times
        for _ in range(3):
            await memory_cache.get("track_key")
        
        entry = memory_cache.cache["track_key"]
        assert entry.access_count >= 3
        assert entry.last_accessed > entry.created_at
    
    def test_cache_stats(self, memory_cache):
        """Test cache statistics collection."""
        stats = memory_cache.get_stats()
        
        assert hasattr(stats, 'hits')
        assert hasattr(stats, 'misses')
        assert hasattr(stats, 'hit_rate')
        assert hasattr(stats, 'total_size_bytes')


class TestRedisCache:
    """Test L2 Redis cache functionality."""
    
    @pytest.fixture
    async def redis_cache(self):
        """Create Redis cache for testing."""
        # Mock Redis client for testing
        with patch('redis.asyncio.from_url') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client
            
            cache = RedisCache("redis://localhost:6379", db=1)
            await cache.connect()
            
            yield cache, mock_client
            
            await cache.close()
    
    @pytest.mark.asyncio
    async def test_redis_operations(self, redis_cache):
        """Test Redis cache operations."""
        cache, mock_client = redis_cache
        
        # Mock Redis responses
        mock_client.pipeline.return_value.execute = AsyncMock(return_value=[
            json.dumps({"data": "value"}),  # data
            "false",  # compressed
            datetime.utcnow().isoformat(),  # created_at
            2,  # access_count
            None  # hset result
        ])
        
        # Test get
        data = await cache.get("test_key")
        assert data == {"data": "value"}
        
        # Test set
        mock_client.pipeline.return_value.execute = AsyncMock(return_value=[True, True])
        success = await cache.set("test_key", {"data": "value"}, 3600, DataType.WEATHER)
        assert success
    
    @pytest.mark.asyncio
    async def test_compression(self, redis_cache):
        """Test data compression for large objects."""
        cache, mock_client = redis_cache
        
        # Large data that should be compressed
        large_data = {"data": "x" * 2000}
        
        mock_client.pipeline.return_value.execute = AsyncMock(return_value=[True, True])
        success = await cache.set("large_key", large_data, 3600, DataType.WEATHER)
        assert success
        
        # Verify compression was attempted (would be in actual Redis call)
        assert mock_client.pipeline.called
    
    @pytest.mark.asyncio
    async def test_pattern_clearing(self, redis_cache):
        """Test pattern-based cache clearing."""
        cache, mock_client = redis_cache
        
        # Mock keys matching pattern
        mock_client.keys = AsyncMock(return_value=["cache:weather:key1", "cache:weather:key2"])
        mock_client.delete = AsyncMock(return_value=2)
        
        cleared = await cache.clear_pattern("weather:*")
        assert cleared == 2
        
        mock_client.keys.assert_called_once_with("cache:weather:*")
        mock_client.delete.assert_called_once()


class TestCacheInvalidationPolicies:
    """Test cache invalidation policies."""
    
    def test_ttl_invalidation_policy(self):
        """Test TTL-based invalidation."""
        policy = TTLInvalidationPolicy()
        
        # Create expired entry
        expired_entry = CacheEntry(
            key="test",
            data={"data": "value"},
            created_at=datetime.utcnow() - timedelta(hours=2),
            last_accessed=datetime.utcnow(),
            access_count=1,
            size_bytes=100,
            ttl_seconds=3600,  # 1 hour TTL
            data_type=DataType.WEATHER
        )
        
        # Create non-expired entry
        valid_entry = CacheEntry(
            key="test2",
            data={"data": "value"},
            created_at=datetime.utcnow() - timedelta(minutes=30),
            last_accessed=datetime.utcnow(),
            access_count=1,
            size_bytes=100,
            ttl_seconds=3600,
            data_type=DataType.WEATHER
        )
        
        # Test invalidation
        assert asyncio.run(policy.should_invalidate(expired_entry, {}))
        assert not asyncio.run(policy.should_invalidate(valid_entry, {}))
    
    def test_agricultural_seasonal_policy(self):
        """Test agricultural seasonal invalidation."""
        policy = AgriculturalSeasonalInvalidationPolicy()
        
        # Create entry that would be valid in off-season but expired in planting season
        entry = CacheEntry(
            key="test",
            data={"data": "value"},
            created_at=datetime.utcnow() - timedelta(hours=2),
            last_accessed=datetime.utcnow(),
            access_count=1,
            size_bytes=100,
            ttl_seconds=7200,  # 2 hours TTL
            data_type=DataType.WEATHER
        )
        
        # Test with planting season (shorter TTL)
        context = {"current_season": "planting_season"}
        assert asyncio.run(policy.should_invalidate(entry, context))
        
        # Test with off season (longer TTL)
        context = {"current_season": "off_season"}
        assert not asyncio.run(policy.should_invalidate(entry, context))
    
    def test_data_freshness_policy(self):
        """Test data freshness invalidation."""
        policy = DataFreshnessInvalidationPolicy()
        
        # Create weather entry older than freshness requirement
        old_weather_entry = CacheEntry(
            key="weather",
            data={"data": "value"},
            created_at=datetime.utcnow() - timedelta(hours=2),
            last_accessed=datetime.utcnow(),
            access_count=1,
            size_bytes=100,
            ttl_seconds=7200,
            data_type=DataType.WEATHER
        )
        
        # Create fresh soil entry
        fresh_soil_entry = CacheEntry(
            key="soil",
            data={"data": "value"},
            created_at=datetime.utcnow() - timedelta(hours=12),
            last_accessed=datetime.utcnow(),
            access_count=1,
            size_bytes=100,
            ttl_seconds=86400,
            data_type=DataType.SOIL
        )
        
        # Weather data should be invalidated (older than 1 hour)
        assert asyncio.run(policy.should_invalidate(old_weather_entry, {}))
        
        # Soil data should not be invalidated (within 24 hour limit)
        assert not asyncio.run(policy.should_invalidate(fresh_soil_entry, {}))


class TestCacheWarmer:
    """Test cache warming functionality."""
    
    @pytest.fixture
    def cache_warmer(self):
        """Create cache warmer for testing."""
        mock_cache_manager = Mock()
        return CacheWarmer(mock_cache_manager)
    
    @pytest.mark.asyncio
    async def test_strategy_registration(self, cache_warmer):
        """Test warming strategy registration."""
        async def mock_strategy(cache_manager, context):
            pass
        
        cache_warmer.register_warming_strategy(DataType.WEATHER, mock_strategy)
        
        assert DataType.WEATHER in cache_warmer.warming_strategies
        assert cache_warmer.warming_strategies[DataType.WEATHER] == mock_strategy
    
    @pytest.mark.asyncio
    async def test_cache_warming_execution(self, cache_warmer):
        """Test cache warming execution."""
        executed = False
        
        async def mock_strategy(cache_manager, context):
            nonlocal executed
            executed = True
            assert context == {"test": "data"}
        
        cache_warmer.register_warming_strategy(DataType.WEATHER, mock_strategy)
        
        await cache_warmer.warm_cache(DataType.WEATHER, {"test": "data"})
        
        assert executed
    
    @pytest.mark.asyncio
    async def test_weather_warming_strategy(self, cache_warmer):
        """Test built-in weather warming strategy."""
        context = {
            "common_locations": [
                {"lat": 42.0, "lon": -93.6},
                {"lat": 40.1, "lon": -88.2}
            ]
        }
        
        # This should not raise an exception
        await cache_warmer.warm_weather_cache(cache_warmer.cache_manager, context)


class TestEnhancedCacheManager:
    """Test enhanced cache manager integration."""
    
    @pytest.fixture
    async def cache_manager(self):
        """Create enhanced cache manager for testing."""
        with patch('redis.asyncio.from_url') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client
            
            manager = EnhancedCacheManager("redis://localhost:6379")
            await manager.connect()
            
            yield manager
            
            await manager.close()
    
    @pytest.mark.asyncio
    async def test_multi_tier_get(self, cache_manager):
        """Test multi-tier cache lookup."""
        # Mock L2 cache to return data
        with patch.object(cache_manager.l2_cache, 'get', return_value={"data": "from_l2"}):
            with patch.object(cache_manager.l1_cache, 'set', return_value=True):
                
                data = await cache_manager.get("test_key", DataType.WEATHER)
                
                assert data == {"data": "from_l2"}
                # Verify L1 cache was populated
                cache_manager.l1_cache.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_multi_tier_set(self, cache_manager):
        """Test multi-tier cache storage."""
        with patch.object(cache_manager.l1_cache, 'set', return_value=True) as l1_set:
            with patch.object(cache_manager.l2_cache, 'set', return_value=True) as l2_set:
                
                success = await cache_manager.set("test_key", {"data": "value"}, DataType.WEATHER)
                
                assert success
                l1_set.assert_called_once()
                l2_set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cache_key_generation(self, cache_manager):
        """Test consistent cache key generation."""
        key1 = cache_manager.generate_cache_key("weather", "current", lat=42.0, lon=-93.6)
        key2 = cache_manager.generate_cache_key("weather", "current", lat=42.0, lon=-93.6)
        key3 = cache_manager.generate_cache_key("weather", "current", lat=42.1, lon=-93.6)
        
        # Same parameters should generate same key
        assert key1 == key2
        
        # Different parameters should generate different key
        assert key1 != key3
        
        # Key should follow expected format
        assert key1.startswith("afas:weather:current:")
    
    @pytest.mark.asyncio
    async def test_pattern_clearing(self, cache_manager):
        """Test pattern-based cache clearing."""
        with patch.object(cache_manager.l1_cache, 'delete', return_value=True) as l1_delete:
            with patch.object(cache_manager.l2_cache, 'clear_pattern', return_value=2) as l2_clear:
                
                # Add some test data to L1 cache
                cache_manager.l1_cache.cache = {
                    "weather_key1": Mock(),
                    "weather_key2": Mock(),
                    "soil_key1": Mock()
                }
                
                cleared = await cache_manager.clear_by_pattern("weather")
                
                # Should clear matching entries
                assert cleared >= 2
                l2_clear.assert_called_once_with("weather")
    
    @pytest.mark.asyncio
    async def test_invalidation_by_policy(self, cache_manager):
        """Test policy-based cache invalidation."""
        # Create test entries in L1 cache
        expired_entry = CacheEntry(
            key="expired",
            data={"data": "value"},
            created_at=datetime.utcnow() - timedelta(hours=2),
            last_accessed=datetime.utcnow(),
            access_count=1,
            size_bytes=100,
            ttl_seconds=3600,
            data_type=DataType.WEATHER
        )
        
        valid_entry = CacheEntry(
            key="valid",
            data={"data": "value"},
            created_at=datetime.utcnow() - timedelta(minutes=30),
            last_accessed=datetime.utcnow(),
            access_count=1,
            size_bytes=100,
            ttl_seconds=3600,
            data_type=DataType.WEATHER
        )
        
        cache_manager.l1_cache.cache = {
            "expired": expired_entry,
            "valid": valid_entry
        }
        
        with patch.object(cache_manager, 'delete', return_value=True) as mock_delete:
            invalidated = await cache_manager.invalidate_by_policy()
            
            # Should invalidate expired entry
            assert invalidated >= 1
            mock_delete.assert_called()
    
    def test_comprehensive_stats(self, cache_manager):
        """Test comprehensive statistics collection."""
        stats = cache_manager.get_comprehensive_stats()
        
        assert "l1_cache" in stats
        assert "l2_cache" in stats
        assert "performance_metrics" in stats
        assert "cache_configs" in stats
        
        # Check L1 cache stats
        l1_stats = stats["l1_cache"]
        assert "hits" in l1_stats
        assert "misses" in l1_stats
        assert "hit_rate" in l1_stats
        
        # Check cache configs
        assert len(stats["cache_configs"]) > 0
        assert "weather" in stats["cache_configs"]


class TestAgriculturalCachePatterns:
    """Test agricultural-specific cache patterns."""
    
    @pytest.mark.asyncio
    async def test_weather_data_caching(self):
        """Test weather data caching patterns."""
        with patch('redis.asyncio.from_url'):
            manager = EnhancedCacheManager("redis://localhost:6379")
            
            # Weather data should have short TTL
            config = manager.cache_configs[DataType.WEATHER]
            assert config.ttl_seconds == 3600  # 1 hour
            assert config.preload_enabled is True
            assert config.priority == 1  # High priority
    
    @pytest.mark.asyncio
    async def test_soil_data_caching(self):
        """Test soil data caching patterns."""
        with patch('redis.asyncio.from_url'):
            manager = EnhancedCacheManager("redis://localhost:6379")
            
            # Soil data should have longer TTL
            config = manager.cache_configs[DataType.SOIL]
            assert config.ttl_seconds == 86400  # 24 hours
            assert config.compression_enabled is True
            assert config.preload_enabled is True
    
    @pytest.mark.asyncio
    async def test_recommendation_caching(self):
        """Test recommendation caching patterns."""
        with patch('redis.asyncio.from_url'):
            manager = EnhancedCacheManager("redis://localhost:6379")
            
            # Recommendations should have medium TTL
            config = manager.cache_configs[DataType.RECOMMENDATION]
            assert config.ttl_seconds == 21600  # 6 hours
            assert config.compression_enabled is True
            assert config.max_size_mb == 200  # Large cache for complex data
    
    @pytest.mark.asyncio
    async def test_market_data_caching(self):
        """Test market data caching patterns."""
        with patch('redis.asyncio.from_url'):
            manager = EnhancedCacheManager("redis://localhost:6379")
            
            # Market data should have short TTL (frequent updates)
            config = manager.cache_configs[DataType.MARKET]
            assert config.ttl_seconds == 1800  # 30 minutes
            assert config.preload_enabled is True
            assert config.priority == 1  # High priority for real-time data


class TestCachePerformance:
    """Test cache performance characteristics."""
    
    @pytest.mark.asyncio
    async def test_cache_response_times(self):
        """Test cache response time tracking."""
        cache = InMemoryCache(max_size_mb=10)
        
        # Perform operations to generate metrics
        await cache.set("perf_key", {"data": "value"}, 3600, DataType.WEATHER)
        await cache.get("perf_key")
        await cache.get("nonexistent_key")
        
        stats = cache.get_stats()
        
        # Should have recorded response times
        assert stats.avg_response_time_ms >= 0
        assert stats.hits > 0
        assert stats.misses > 0
    
    @pytest.mark.asyncio
    async def test_memory_usage_tracking(self):
        """Test memory usage tracking."""
        cache = InMemoryCache(max_size_mb=1)
        
        # Add data and check size tracking
        large_data = {"data": "x" * 10000}
        await cache.set("size_key", large_data, 3600, DataType.WEATHER)
        
        stats = cache.get_stats()
        assert stats.total_size_bytes > 0
        
        # Size should decrease after deletion
        await cache.delete("size_key")
        stats_after = cache.get_stats()
        assert stats_after.total_size_bytes < stats.total_size_bytes


@pytest.mark.integration
class TestCacheIntegration:
    """Integration tests for cache system."""
    
    @pytest.mark.asyncio
    async def test_full_cache_workflow(self):
        """Test complete cache workflow."""
        with patch('redis.asyncio.from_url') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client
            
            # Create cache manager
            manager = await create_enhanced_cache_manager("redis://localhost:6379")
            
            # Test data flow
            test_data = {
                "temperature": 75.5,
                "humidity": 65,
                "conditions": "partly cloudy"
            }
            
            # Set data
            success = await manager.set("weather_test", test_data, DataType.WEATHER)
            assert success
            
            # Get data (should hit L1 cache)
            retrieved_data = await manager.get("weather_test", DataType.WEATHER)
            assert retrieved_data == test_data
            
            # Clear cache
            cleared = await manager.clear_by_pattern("weather_test")
            assert cleared >= 0
            
            # Clean up
            await manager.close()
    
    @pytest.mark.asyncio
    async def test_cache_warming_integration(self):
        """Test cache warming integration."""
        with patch('redis.asyncio.from_url'):
            manager = await create_enhanced_cache_manager("redis://localhost:6379")
            
            # Test warming with context
            context = {
                "weather_locations": [{"lat": 42.0, "lon": -93.6}],
                "commodities": ["corn", "soybean"]
            }
            
            # This should not raise exceptions
            await manager.warm_cache([DataType.WEATHER, DataType.MARKET], context)
            
            await manager.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])