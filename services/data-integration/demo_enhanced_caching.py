"""
Enhanced Caching Layer Demonstration

This script demonstrates the capabilities of the enhanced caching layer
for the AFAS data integration service.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any

from src.services.enhanced_cache_manager import (
    create_enhanced_cache_manager,
    DataType,
    CacheConfig
)
from src.services.cache_integration_service import (
    create_agricultural_cache_service,
    CacheableRequest
)
from src.services.data_ingestion_framework import (
    DataIngestionPipeline,
    AgriculturalDataValidator,
    CacheManager,
    IngestionResult
)


class MockWeatherService:
    """Mock weather service for demonstration."""
    
    async def get_current_weather(self, operation: str, **params) -> Dict[str, Any]:
        """Mock weather data retrieval."""
        latitude = params.get("latitude", 0.0)
        longitude = params.get("longitude", 0.0)
        
        # Simulate API delay
        await asyncio.sleep(0.5)
        
        return {
            "temperature_f": 75.5 + (latitude - 40) * 0.5,
            "humidity_percent": 65.0,
            "wind_speed_mph": 8.0,
            "conditions": "Partly Cloudy",
            "location": f"{latitude},{longitude}",
            "timestamp": datetime.utcnow().isoformat(),
            "_quality_score": 0.92
        }


class MockSoilService:
    """Mock soil service for demonstration."""
    
    async def get_soil_characteristics(self, operation: str, **params) -> Dict[str, Any]:
        """Mock soil data retrieval."""
        latitude = params.get("latitude", 0.0)
        longitude = params.get("longitude", 0.0)
        
        # Simulate API delay
        await asyncio.sleep(1.0)
        
        return {
            "soil_series": "Webster",
            "ph": 6.2 + (latitude - 42) * 0.1,
            "organic_matter_percent": 3.5,
            "drainage_class": "somewhat_poorly_drained",
            "location": f"{latitude},{longitude}",
            "timestamp": datetime.utcnow().isoformat(),
            "_quality_score": 0.88
        }


async def demonstrate_basic_caching():
    """Demonstrate basic caching operations."""
    print("=== Basic Caching Operations Demo ===")
    
    # Create enhanced cache manager
    cache_manager = await create_enhanced_cache_manager("redis://localhost:6379")
    
    # Test data
    weather_data = {
        "temperature": 75.5,
        "humidity": 65,
        "conditions": "sunny"
    }
    
    print("1. Setting data in cache...")
    success = await cache_manager.set("demo_weather", weather_data, DataType.WEATHER)
    print(f"   Cache set success: {success}")
    
    print("2. Getting data from cache...")
    start_time = time.time()
    cached_data = await cache_manager.get("demo_weather", DataType.WEATHER)
    response_time = (time.time() - start_time) * 1000
    print(f"   Retrieved data: {cached_data}")
    print(f"   Response time: {response_time:.2f}ms")
    
    print("3. Cache statistics:")
    stats = cache_manager.get_comprehensive_stats()
    print(f"   L1 Hit Rate: {stats['l1_cache']['hit_rate']:.1f}%")
    print(f"   L2 Hit Rate: {stats['l2_cache']['hit_rate']:.1f}%")
    
    await cache_manager.close()
    print()


async def demonstrate_multi_tier_caching():
    """Demonstrate multi-tier cache behavior."""
    print("=== Multi-Tier Caching Demo ===")
    
    cache_manager = await create_enhanced_cache_manager("redis://localhost:6379")
    
    # Clear any existing data
    await cache_manager.clear_by_pattern("*")
    
    test_key = "multi_tier_test"
    test_data = {"value": "multi_tier_data", "timestamp": datetime.utcnow().isoformat()}
    
    print("1. Setting data (goes to both L1 and L2)...")
    await cache_manager.set(test_key, test_data, DataType.WEATHER)
    
    print("2. First get (L1 cache hit)...")
    start_time = time.time()
    data1 = await cache_manager.get(test_key, DataType.WEATHER)
    l1_time = (time.time() - start_time) * 1000
    print(f"   L1 response time: {l1_time:.2f}ms")
    
    print("3. Clearing L1 cache only...")
    await cache_manager.l1_cache.clear()
    
    print("4. Second get (L2 cache hit, promotes to L1)...")
    start_time = time.time()
    data2 = await cache_manager.get(test_key, DataType.WEATHER)
    l2_time = (time.time() - start_time) * 1000
    print(f"   L2 response time: {l2_time:.2f}ms")
    
    print("5. Third get (L1 cache hit again)...")
    start_time = time.time()
    data3 = await cache_manager.get(test_key, DataType.WEATHER)
    l1_time_2 = (time.time() - start_time) * 1000
    print(f"   L1 response time: {l1_time_2:.2f}ms")
    
    print(f"6. Performance comparison:")
    print(f"   L1 cache: ~{l1_time:.2f}ms")
    print(f"   L2 cache: ~{l2_time:.2f}ms")
    print(f"   L2 is ~{l2_time/l1_time:.1f}x slower than L1")
    
    await cache_manager.close()
    print()


async def demonstrate_cache_invalidation():
    """Demonstrate cache invalidation policies."""
    print("=== Cache Invalidation Demo ===")
    
    cache_manager = await create_enhanced_cache_manager("redis://localhost:6379")
    
    # Set data with short TTL for demo
    short_ttl_data = {"value": "expires_soon", "created": datetime.utcnow().isoformat()}
    await cache_manager.set("short_ttl", short_ttl_data, DataType.WEATHER)
    
    print("1. Data set with normal TTL")
    data = await cache_manager.get("short_ttl", DataType.WEATHER)
    print(f"   Retrieved: {data is not None}")
    
    print("2. Testing invalidation policies...")
    
    # Test seasonal invalidation
    context = {"current_season": "planting_season"}  # Shorter TTL during planting
    invalidated = await cache_manager.invalidate_by_policy(context)
    print(f"   Entries invalidated by seasonal policy: {invalidated}")
    
    # Test pattern-based clearing
    await cache_manager.set("weather_iowa", {"temp": 70}, DataType.WEATHER)
    await cache_manager.set("weather_illinois", {"temp": 72}, DataType.WEATHER)
    await cache_manager.set("soil_iowa", {"ph": 6.5}, DataType.SOIL)
    
    cleared = await cache_manager.clear_by_pattern("weather")
    print(f"   Weather entries cleared: {cleared}")
    
    # Verify soil data still exists
    soil_data = await cache_manager.get("soil_iowa", DataType.SOIL)
    print(f"   Soil data still cached: {soil_data is not None}")
    
    await cache_manager.close()
    print()


async def demonstrate_cache_warming():
    """Demonstrate cache warming functionality."""
    print("=== Cache Warming Demo ===")
    
    cache_manager = await create_enhanced_cache_manager("redis://localhost:6379")
    
    print("1. Cache warming for common agricultural locations...")
    
    # Define common agricultural locations
    warming_context = {
        "weather_locations": [
            {"lat": 42.0308, "lon": -93.6319},  # Ames, Iowa
            {"lat": 40.1164, "lon": -88.2434},  # Champaign, Illinois
            {"lat": 39.7391, "lon": -89.2661},  # Springfield, Illinois
        ],
        "commodities": ["corn", "soybean", "wheat"]
    }
    
    # Warm cache for weather and market data
    await cache_manager.warm_cache([DataType.WEATHER, DataType.MARKET], warming_context)
    print("   Cache warming completed")
    
    print("2. Cache statistics after warming:")
    stats = cache_manager.get_comprehensive_stats()
    print(f"   Total cache operations: {stats['l1_cache']['hits'] + stats['l1_cache']['misses']}")
    
    await cache_manager.close()
    print()


async def demonstrate_agricultural_cache_service():
    """Demonstrate agricultural-specific cache service."""
    print("=== Agricultural Cache Service Demo ===")
    
    # Create mock services
    weather_service = MockWeatherService()
    soil_service = MockSoilService()
    
    # Create ingestion pipeline with mock services
    cache_manager = CacheManager("redis://localhost:6379")
    await cache_manager.connect()
    
    validator = AgriculturalDataValidator()
    pipeline = DataIngestionPipeline(cache_manager, validator)
    
    # Register mock services
    pipeline.register_data_source(
        config=CacheConfig(
            data_type=DataType.WEATHER,
            ttl_seconds=3600,
            max_size_mb=50,
            compression_enabled=True,
            preload_enabled=True
        ),
        handler=weather_service.get_current_weather
    )
    
    pipeline.register_data_source(
        config=CacheConfig(
            data_type=DataType.SOIL,
            ttl_seconds=86400,
            max_size_mb=100,
            compression_enabled=True,
            preload_enabled=True
        ),
        handler=soil_service.get_soil_characteristics
    )
    
    # Create agricultural cache service
    agricultural_service = await create_agricultural_cache_service(
        "redis://localhost:6379",
        pipeline
    )
    
    # Test weather data retrieval
    print("1. Getting weather data (cache miss - will fetch from source)...")
    start_time = time.time()
    weather_result = await agricultural_service.get_weather_data(42.0308, -93.6319)
    first_time = (time.time() - start_time) * 1000
    
    print(f"   Success: {weather_result.success}")
    print(f"   Cache hit: {weather_result.cache_hit}")
    print(f"   Response time: {first_time:.0f}ms")
    print(f"   Temperature: {weather_result.data.get('temperature_f', 'N/A')}°F")
    
    print("2. Getting same weather data (cache hit)...")
    start_time = time.time()
    weather_result2 = await agricultural_service.get_weather_data(42.0308, -93.6319)
    second_time = (time.time() - start_time) * 1000
    
    print(f"   Cache hit: {weather_result2.cache_hit}")
    print(f"   Response time: {second_time:.0f}ms")
    print(f"   Speed improvement: {first_time/second_time:.1f}x faster")
    
    # Test soil data retrieval
    print("3. Getting soil data...")
    soil_result = await agricultural_service.get_soil_data(42.0308, -93.6319)
    print(f"   Success: {soil_result.success}")
    print(f"   Soil pH: {soil_result.data.get('ph', 'N/A')}")
    print(f"   Soil series: {soil_result.data.get('soil_series', 'N/A')}")
    
    # Test farm data preloading
    print("4. Preloading farm data...")
    farm_profile = {
        "location": {"lat": 42.0308, "lon": -93.6319},
        "primary_crops": ["corn", "soybean"]
    }
    await agricultural_service.preload_farm_data(farm_profile)
    print("   Farm data preloading completed")
    
    # Get cache performance report
    print("5. Cache performance report:")
    report = await agricultural_service.get_cache_performance_report()
    cache_health = report["cache_health"]
    print(f"   Overall health: {cache_health['health_status']}")
    print(f"   Hit rate: {cache_health['overall_hit_rate']:.1f}%")
    
    if cache_health["recommendations"]:
        print("   Recommendations:")
        for rec in cache_health["recommendations"]:
            print(f"   - {rec}")
    
    await cache_manager.close()
    print()


async def demonstrate_performance_monitoring():
    """Demonstrate cache performance monitoring."""
    print("=== Performance Monitoring Demo ===")
    
    cache_manager = await create_enhanced_cache_manager("redis://localhost:6379")
    
    # Generate some cache activity
    print("1. Generating cache activity...")
    
    for i in range(50):
        # Mix of hits and misses
        key = f"perf_test_{i % 10}"  # This creates some cache hits
        data = {"iteration": i, "timestamp": datetime.utcnow().isoformat()}
        
        await cache_manager.set(key, data, DataType.WEATHER)
        await cache_manager.get(key, DataType.WEATHER)
        
        # Some cache misses
        await cache_manager.get(f"nonexistent_{i}", DataType.WEATHER)
    
    print("2. Performance statistics:")
    stats = cache_manager.get_comprehensive_stats()
    
    l1_stats = stats["l1_cache"]
    l2_stats = stats["l2_cache"]
    perf_metrics = stats["performance_metrics"]
    
    print(f"   L1 Cache:")
    print(f"     Hits: {l1_stats['hits']}")
    print(f"     Misses: {l1_stats['misses']}")
    print(f"     Hit Rate: {l1_stats['hit_rate']:.1f}%")
    print(f"     Avg Response Time: {l1_stats['avg_response_time_ms']:.2f}ms")
    print(f"     Evictions: {l1_stats['evictions']}")
    
    print(f"   L2 Cache:")
    print(f"     Hits: {l2_stats['hits']}")
    print(f"     Misses: {l2_stats['misses']}")
    print(f"     Hit Rate: {l2_stats['hit_rate']:.1f}%")
    print(f"     Avg Response Time: {l2_stats['avg_response_time_ms']:.2f}ms")
    
    print(f"   Performance Metrics:")
    print(f"     L1 Hit Avg: {perf_metrics['l1_hit_avg_ms']:.2f}ms")
    print(f"     L2 Hit Avg: {perf_metrics['l2_hit_avg_ms']:.2f}ms")
    print(f"     Miss Avg: {perf_metrics['miss_avg_ms']:.2f}ms")
    
    await cache_manager.close()
    print()


async def main():
    """Run all demonstrations."""
    print("AFAS Enhanced Caching Layer Demonstration")
    print("=" * 50)
    print()
    
    try:
        await demonstrate_basic_caching()
        await demonstrate_multi_tier_caching()
        await demonstrate_cache_invalidation()
        await demonstrate_cache_warming()
        await demonstrate_performance_monitoring()
        
        # Note: Agricultural cache service demo requires actual ingestion pipeline
        # Uncomment the following line if you have the full pipeline set up
        # await demonstrate_agricultural_cache_service()
        
        print("All demonstrations completed successfully!")
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())