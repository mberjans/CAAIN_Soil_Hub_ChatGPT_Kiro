"""
Cache Integration Service for AFAS Data Integration

Integrates the enhanced cache manager with the existing data ingestion framework
and provides cache-aware data access patterns for agricultural services.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
import structlog
from dataclasses import dataclass

from .enhanced_cache_manager import (
    EnhancedCacheManager, 
    DataType, 
    CacheStrategy,
    create_enhanced_cache_manager
)
from .data_ingestion_framework import DataIngestionPipeline, IngestionResult

logger = structlog.get_logger(__name__)


@dataclass
class CacheableRequest:
    """Represents a cacheable data request."""
    source_name: str
    operation: str
    params: Dict[str, Any]
    data_type: DataType
    cache_strategy: CacheStrategy = CacheStrategy.CACHE_ASIDE
    force_refresh: bool = False


class CacheIntegrationService:
    """Service that integrates caching with data ingestion pipeline."""
    
    def __init__(self, 
                 cache_manager: EnhancedCacheManager,
                 ingestion_pipeline: DataIngestionPipeline):
        self.cache_manager = cache_manager
        self.ingestion_pipeline = ingestion_pipeline
        self.cache_hit_callbacks = {}
        self.cache_miss_callbacks = {}
        
    def register_cache_hit_callback(self, data_type: DataType, callback: Callable):
        """Register callback for cache hits."""
        self.cache_hit_callbacks[data_type] = callback
    
    def register_cache_miss_callback(self, data_type: DataType, callback: Callable):
        """Register callback for cache misses."""
        self.cache_miss_callbacks[data_type] = callback
    
    async def get_cached_data(self, request: CacheableRequest) -> IngestionResult:
        """Get data with cache-aware strategy."""
        cache_key = self.cache_manager.generate_cache_key(
            request.source_name, 
            request.operation, 
            **request.params
        )
        
        start_time = datetime.utcnow()
        
        # Check cache first (unless force refresh)
        if not request.force_refresh:
            cached_data = await self.cache_manager.get(cache_key, request.data_type)
            
            if cached_data is not None:
                # Cache hit
                processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                # Execute cache hit callback if registered
                if request.data_type in self.cache_hit_callbacks:
                    try:
                        await self.cache_hit_callbacks[request.data_type](cached_data, request)
                    except Exception as e:
                        logger.warning("Cache hit callback error", error=str(e))
                
                return IngestionResult(
                    source_name=request.source_name,
                    success=True,
                    data=cached_data,
                    quality_score=cached_data.get("_quality_score", 1.0),
                    cache_hit=True,
                    processing_time_ms=processing_time
                )
        
        # Cache miss or force refresh - fetch from source
        try:
            ingestion_result = await self.ingestion_pipeline.ingest_data(
                request.source_name,
                request.operation,
                **request.params
            )
            
            if ingestion_result.success and ingestion_result.data:
                # Cache the result
                await self.cache_manager.set(
                    cache_key,
                    ingestion_result.data,
                    request.data_type
                )
                
                # Execute cache miss callback if registered
                if request.data_type in self.cache_miss_callbacks:
                    try:
                        await self.cache_miss_callbacks[request.data_type](
                            ingestion_result.data, 
                            request
                        )
                    except Exception as e:
                        logger.warning("Cache miss callback error", error=str(e))
            
            return ingestion_result
            
        except Exception as e:
            logger.error("Data ingestion error", 
                        source=request.source_name, 
                        operation=request.operation,
                        error=str(e))
            
            return IngestionResult(
                source_name=request.source_name,
                success=False,
                error_message=f"Ingestion failed: {str(e)}"
            )
    
    async def batch_get_cached_data(self, requests: List[CacheableRequest]) -> List[IngestionResult]:
        """Get multiple data items with caching."""
        tasks = [self.get_cached_data(request) for request in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(IngestionResult(
                    source_name=requests[i].source_name,
                    success=False,
                    error_message=f"Batch processing error: {str(result)}"
                ))
            else:
                final_results.append(result)
        
        return final_results
    
    async def preload_common_data(self, context: Dict[str, Any] = None):
        """Preload commonly accessed data into cache."""
        context = context or {}
        
        # Define common data requests
        common_requests = []
        
        # Weather data for major agricultural regions
        if "weather_locations" in context:
            for location in context["weather_locations"]:
                common_requests.append(CacheableRequest(
                    source_name="weather",
                    operation="current",
                    params={"latitude": location["lat"], "longitude": location["lon"]},
                    data_type=DataType.WEATHER
                ))
        
        # Soil data for agricultural regions
        if "soil_locations" in context:
            for location in context["soil_locations"]:
                common_requests.append(CacheableRequest(
                    source_name="soil",
                    operation="characteristics",
                    params={"latitude": location["lat"], "longitude": location["lon"]},
                    data_type=DataType.SOIL
                ))
        
        # Market data for common commodities
        if "commodities" in context:
            for commodity in context["commodities"]:
                common_requests.append(CacheableRequest(
                    source_name="market",
                    operation="prices",
                    params={"commodity": commodity},
                    data_type=DataType.MARKET
                ))
        
        # Execute preload requests
        if common_requests:
            logger.info("Preloading common data", request_count=len(common_requests))
            results = await self.batch_get_cached_data(common_requests)
            
            successful_preloads = sum(1 for r in results if r.success)
            logger.info("Preload completed", 
                       successful=successful_preloads, 
                       total=len(common_requests))
    
    async def invalidate_related_cache(self, data_type: DataType, context: Dict[str, Any]):
        """Invalidate cache entries related to specific data changes."""
        patterns_to_clear = []
        
        if data_type == DataType.WEATHER:
            # Invalidate weather-related caches
            if "location" in context:
                lat, lon = context["location"]["lat"], context["location"]["lon"]
                patterns_to_clear.append(f"*weather*{lat}*{lon}*")
                patterns_to_clear.append(f"*forecast*{lat}*{lon}*")
        
        elif data_type == DataType.SOIL:
            # Invalidate soil-related caches
            if "location" in context:
                lat, lon = context["location"]["lat"], context["location"]["lon"]
                patterns_to_clear.append(f"*soil*{lat}*{lon}*")
        
        elif data_type == DataType.MARKET:
            # Invalidate market-related caches
            if "commodity" in context:
                commodity = context["commodity"]
                patterns_to_clear.append(f"*market*{commodity}*")
                patterns_to_clear.append(f"*price*{commodity}*")
        
        elif data_type == DataType.RECOMMENDATION:
            # Invalidate recommendation caches
            if "farm_id" in context:
                farm_id = context["farm_id"]
                patterns_to_clear.append(f"*recommendation*{farm_id}*")
        
        # Clear matching cache entries
        total_cleared = 0
        for pattern in patterns_to_clear:
            cleared = await self.cache_manager.clear_by_pattern(pattern)
            total_cleared += cleared
        
        if total_cleared > 0:
            logger.info("Cache invalidation completed", 
                       data_type=data_type.value,
                       patterns_cleared=len(patterns_to_clear),
                       entries_cleared=total_cleared)
    
    async def get_cache_health_status(self) -> Dict[str, Any]:
        """Get comprehensive cache health status."""
        stats = self.cache_manager.get_comprehensive_stats()
        
        # Calculate overall health score
        l1_hit_rate = stats["l1_cache"]["hit_rate"]
        l2_hit_rate = stats["l2_cache"]["hit_rate"]
        overall_hit_rate = (l1_hit_rate + l2_hit_rate) / 2
        
        # Determine health status
        if overall_hit_rate >= 80:
            health_status = "excellent"
        elif overall_hit_rate >= 60:
            health_status = "good"
        elif overall_hit_rate >= 40:
            health_status = "fair"
        else:
            health_status = "poor"
        
        return {
            "health_status": health_status,
            "overall_hit_rate": overall_hit_rate,
            "cache_stats": stats,
            "recommendations": self._generate_cache_recommendations(stats)
        }
    
    def _generate_cache_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """Generate cache optimization recommendations."""
        recommendations = []
        
        l1_stats = stats["l1_cache"]
        l2_stats = stats["l2_cache"]
        
        # Hit rate recommendations
        if l1_stats["hit_rate"] < 50:
            recommendations.append("Consider increasing L1 cache size or adjusting TTL values")
        
        if l2_stats["hit_rate"] < 60:
            recommendations.append("Review L2 cache configuration and data access patterns")
        
        # Performance recommendations
        if l1_stats["avg_response_time_ms"] > 5:
            recommendations.append("L1 cache response time is high - check memory pressure")
        
        if l2_stats["avg_response_time_ms"] > 50:
            recommendations.append("L2 cache response time is high - check Redis performance")
        
        # Eviction recommendations
        if l1_stats["evictions"] > l1_stats["hits"] * 0.1:
            recommendations.append("High L1 eviction rate - consider increasing cache size")
        
        # Size recommendations
        if l1_stats["size_bytes"] > 90 * 1024 * 1024:  # 90MB
            recommendations.append("L1 cache approaching size limit - monitor memory usage")
        
        return recommendations


class AgriculturalCacheService:
    """High-level cache service for agricultural data operations."""
    
    def __init__(self, cache_integration_service: CacheIntegrationService):
        self.cache_service = cache_integration_service
        self._setup_agricultural_callbacks()
    
    def _setup_agricultural_callbacks(self):
        """Setup agricultural-specific cache callbacks."""
        
        async def weather_cache_hit_callback(data: Dict[str, Any], request: CacheableRequest):
            """Handle weather data cache hits."""
            logger.debug("Weather cache hit", 
                        location=f"{request.params.get('latitude')},{request.params.get('longitude')}")
        
        async def weather_cache_miss_callback(data: Dict[str, Any], request: CacheableRequest):
            """Handle weather data cache misses."""
            logger.info("Weather cache miss - data fetched from source",
                       location=f"{request.params.get('latitude')},{request.params.get('longitude')}")
        
        async def soil_cache_hit_callback(data: Dict[str, Any], request: CacheableRequest):
            """Handle soil data cache hits."""
            logger.debug("Soil cache hit",
                        location=f"{request.params.get('latitude')},{request.params.get('longitude')}")
        
        async def recommendation_cache_miss_callback(data: Dict[str, Any], request: CacheableRequest):
            """Handle recommendation cache misses."""
            logger.info("Recommendation cache miss - new recommendation generated",
                       operation=request.operation)
        
        # Register callbacks
        self.cache_service.register_cache_hit_callback(DataType.WEATHER, weather_cache_hit_callback)
        self.cache_service.register_cache_miss_callback(DataType.WEATHER, weather_cache_miss_callback)
        self.cache_service.register_cache_hit_callback(DataType.SOIL, soil_cache_hit_callback)
        self.cache_service.register_cache_miss_callback(DataType.RECOMMENDATION, recommendation_cache_miss_callback)
    
    async def get_weather_data(self, latitude: float, longitude: float, 
                              force_refresh: bool = False) -> IngestionResult:
        """Get weather data with caching."""
        request = CacheableRequest(
            source_name="weather",
            operation="current",
            params={"latitude": latitude, "longitude": longitude},
            data_type=DataType.WEATHER,
            force_refresh=force_refresh
        )
        
        return await self.cache_service.get_cached_data(request)
    
    async def get_soil_data(self, latitude: float, longitude: float,
                           force_refresh: bool = False) -> IngestionResult:
        """Get soil data with caching."""
        request = CacheableRequest(
            source_name="soil",
            operation="characteristics",
            params={"latitude": latitude, "longitude": longitude},
            data_type=DataType.SOIL,
            force_refresh=force_refresh
        )
        
        return await self.cache_service.get_cached_data(request)
    
    async def get_crop_recommendations(self, farm_id: str, crop_type: str,
                                     soil_data: Dict[str, Any],
                                     force_refresh: bool = False) -> IngestionResult:
        """Get crop recommendations with caching."""
        request = CacheableRequest(
            source_name="recommendation_engine",
            operation="crop_selection",
            params={
                "farm_id": farm_id,
                "crop_type": crop_type,
                "soil_data": soil_data
            },
            data_type=DataType.RECOMMENDATION,
            force_refresh=force_refresh
        )
        
        return await self.cache_service.get_cached_data(request)
    
    async def get_market_prices(self, commodity: str, date: str = None,
                               force_refresh: bool = False) -> IngestionResult:
        """Get market prices with caching."""
        params = {"commodity": commodity}
        if date:
            params["date"] = date
        
        request = CacheableRequest(
            source_name="market",
            operation="prices",
            params=params,
            data_type=DataType.MARKET,
            force_refresh=force_refresh
        )
        
        return await self.cache_service.get_cached_data(request)
    
    async def preload_farm_data(self, farm_profile: Dict[str, Any]):
        """Preload cache with data relevant to a specific farm."""
        location = farm_profile.get("location", {})
        crops = farm_profile.get("primary_crops", [])
        
        preload_context = {
            "weather_locations": [location] if location else [],
            "soil_locations": [location] if location else [],
            "commodities": crops
        }
        
        await self.cache_service.preload_common_data(preload_context)
    
    async def invalidate_farm_cache(self, farm_id: str):
        """Invalidate all cache entries related to a farm."""
        await self.cache_service.invalidate_related_cache(
            DataType.RECOMMENDATION,
            {"farm_id": farm_id}
        )
    
    async def get_cache_performance_report(self) -> Dict[str, Any]:
        """Get detailed cache performance report."""
        health_status = await self.cache_service.get_cache_health_status()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cache_health": health_status,
            "agricultural_metrics": {
                "weather_cache_efficiency": "High priority data type with frequent access",
                "soil_cache_efficiency": "Medium priority with longer TTL",
                "recommendation_cache_efficiency": "High value cache with complex invalidation",
                "market_cache_efficiency": "High frequency updates with short TTL"
            }
        }


# Factory functions for easy setup
async def create_cache_integration_service(
    redis_url: str = "redis://localhost:6379",
    ingestion_pipeline: DataIngestionPipeline = None
) -> CacheIntegrationService:
    """Create cache integration service with enhanced cache manager."""
    
    cache_manager = await create_enhanced_cache_manager(redis_url)
    
    if not ingestion_pipeline:
        # Create a basic ingestion pipeline if none provided
        from .data_ingestion_framework import DataIngestionPipeline, AgriculturalDataValidator
        from .enhanced_cache_manager import EnhancedCacheManager
        
        # This would need the actual cache manager from the ingestion framework
        # For now, we'll assume it's provided
        pass
    
    return CacheIntegrationService(cache_manager, ingestion_pipeline)


async def create_agricultural_cache_service(
    redis_url: str = "redis://localhost:6379",
    ingestion_pipeline: DataIngestionPipeline = None
) -> AgriculturalCacheService:
    """Create agricultural cache service."""
    
    cache_integration = await create_cache_integration_service(redis_url, ingestion_pipeline)
    return AgriculturalCacheService(cache_integration)