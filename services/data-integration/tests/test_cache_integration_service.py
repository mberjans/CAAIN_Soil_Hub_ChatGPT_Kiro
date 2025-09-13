"""
Tests for Cache Integration Service

Tests the integration between the enhanced cache manager and the data ingestion pipeline.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from services.data_integration.src.services.cache_integration_service import (
    CacheIntegrationService,
    AgriculturalCacheService,
    CacheableRequest,
    create_cache_integration_service,
    create_agricultural_cache_service
)
from services.data_integration.src.services.enhanced_cache_manager import (
    DataType,
    CacheStrategy
)
from services.data_integration.src.services.data_ingestion_framework import (
    IngestionResult
)


class TestCacheableRequest:
    """Test CacheableRequest data structure."""
    
    def test_cacheable_request_creation(self):
        """Test creating cacheable request."""
        request = CacheableRequest(
            source_name="weather",
            operation="current",
            params={"lat": 42.0, "lon": -93.6},
            data_type=DataType.WEATHER,
            cache_strategy=CacheStrategy.CACHE_ASIDE,
            force_refresh=False
        )
        
        assert request.source_name == "weather"
        assert request.operation == "current"
        assert request.params == {"lat": 42.0, "lon": -93.6}
        assert request.data_type == DataType.WEATHER
        assert request.cache_strategy == CacheStrategy.CACHE_ASIDE
        assert request.force_refresh is False
    
    def test_default_values(self):
        """Test default values in CacheableRequest."""
        request = CacheableRequest(
            source_name="soil",
            operation="characteristics",
            params={"lat": 42.0, "lon": -93.6},
            data_type=DataType.SOIL
        )
        
        assert request.cache_strategy == CacheStrategy.CACHE_ASIDE
        assert request.force_refresh is False


class TestCacheIntegrationService:
    """Test cache integration service functionality."""
    
    @pytest.fixture
    def mock_cache_manager(self):
        """Create mock cache manager."""
        manager = Mock()
        manager.get = AsyncMock()
        manager.set = AsyncMock()
        manager.generate_cache_key = Mock(return_value="test_cache_key")
        manager.clear_by_pattern = AsyncMock()
        manager.get_comprehensive_stats = Mock()
        return manager
    
    @pytest.fixture
    def mock_ingestion_pipeline(self):
        """Create mock ingestion pipeline."""
        pipeline = Mock()
        pipeline.ingest_data = AsyncMock()
        return pipeline
    
    @pytest.fixture
    def cache_service(self, mock_cache_manager, mock_ingestion_pipeline):
        """Create cache integration service."""
        return CacheIntegrationService(mock_cache_manager, mock_ingestion_pipeline)
    
    @pytest.mark.asyncio
    async def test_cache_hit_scenario(self, cache_service, mock_cache_manager):
        """Test successful cache hit scenario."""
        # Setup cache hit
        cached_data = {
            "temperature": 75.5,
            "humidity": 65,
            "_quality_score": 0.95
        }
        mock_cache_manager.get.return_value = cached_data
        
        request = CacheableRequest(
            source_name="weather",
            operation="current",
            params={"lat": 42.0, "lon": -93.6},
            data_type=DataType.WEATHER
        )
        
        result = await cache_service.get_cached_data(request)
        
        assert result.success is True
        assert result.cache_hit is True
        assert result.data == cached_data
        assert result.quality_score == 0.95
        assert result.processing_time_ms > 0
        
        # Verify cache was checked
        mock_cache_manager.get.assert_called_once()
        
        # Verify ingestion pipeline was not called
        cache_service.ingestion_pipeline.ingest_data.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_cache_miss_scenario(self, cache_service, mock_cache_manager, mock_ingestion_pipeline):
        """Test cache miss scenario with successful data ingestion."""
        # Setup cache miss
        mock_cache_manager.get.return_value = None
        
        # Setup successful ingestion
        ingestion_data = {
            "temperature": 72.0,
            "humidity": 70,
            "_quality_score": 0.88
        }
        mock_ingestion_pipeline.ingest_data.return_value = IngestionResult(
            source_name="weather",
            success=True,
            data=ingestion_data,
            quality_score=0.88
        )
        
        request = CacheableRequest(
            source_name="weather",
            operation="current",
            params={"lat": 42.0, "lon": -93.6},
            data_type=DataType.WEATHER
        )
        
        result = await cache_service.get_cached_data(request)
        
        assert result.success is True
        assert result.cache_hit is False
        assert result.data == ingestion_data
        assert result.quality_score == 0.88
        
        # Verify cache was checked and data was cached
        mock_cache_manager.get.assert_called_once()
        mock_cache_manager.set.assert_called_once()
        
        # Verify ingestion pipeline was called
        mock_ingestion_pipeline.ingest_data.assert_called_once_with(
            "weather", "current", lat=42.0, lon=-93.6
        )
    
    @pytest.mark.asyncio
    async def test_force_refresh_scenario(self, cache_service, mock_cache_manager, mock_ingestion_pipeline):
        """Test force refresh bypasses cache."""
        # Setup cache data (should be ignored)
        mock_cache_manager.get.return_value = {"old": "data"}
        
        # Setup fresh ingestion data
        fresh_data = {"fresh": "data", "_quality_score": 0.92}
        mock_ingestion_pipeline.ingest_data.return_value = IngestionResult(
            source_name="weather",
            success=True,
            data=fresh_data,
            quality_score=0.92
        )
        
        request = CacheableRequest(
            source_name="weather",
            operation="current",
            params={"lat": 42.0, "lon": -93.6},
            data_type=DataType.WEATHER,
            force_refresh=True
        )
        
        result = await cache_service.get_cached_data(request)
        
        assert result.success is True
        assert result.cache_hit is False
        assert result.data == fresh_data
        
        # Verify cache was not checked due to force refresh
        mock_cache_manager.get.assert_not_called()
        
        # Verify ingestion pipeline was called
        mock_ingestion_pipeline.ingest_data.assert_called_once()
        
        # Verify fresh data was cached
        mock_cache_manager.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_ingestion_failure_scenario(self, cache_service, mock_cache_manager, mock_ingestion_pipeline):
        """Test handling of ingestion failures."""
        # Setup cache miss
        mock_cache_manager.get.return_value = None
        
        # Setup ingestion failure
        mock_ingestion_pipeline.ingest_data.return_value = IngestionResult(
            source_name="weather",
            success=False,
            error_message="API unavailable"
        )
        
        request = CacheableRequest(
            source_name="weather",
            operation="current",
            params={"lat": 42.0, "lon": -93.6},
            data_type=DataType.WEATHER
        )
        
        result = await cache_service.get_cached_data(request)
        
        assert result.success is False
        assert result.error_message == "API unavailable"
        
        # Verify cache was not updated on failure
        mock_cache_manager.set.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_batch_operations(self, cache_service, mock_cache_manager, mock_ingestion_pipeline):
        """Test batch cache operations."""
        # Setup mixed cache hits and misses
        def cache_get_side_effect(key, data_type):
            if "weather" in key:
                return {"temperature": 75.5}
            return None
        
        mock_cache_manager.get.side_effect = cache_get_side_effect
        
        # Setup ingestion for cache misses
        mock_ingestion_pipeline.ingest_data.return_value = IngestionResult(
            source_name="soil",
            success=True,
            data={"ph": 6.5},
            quality_score=0.9
        )
        
        requests = [
            CacheableRequest(
                source_name="weather",
                operation="current",
                params={"lat": 42.0, "lon": -93.6},
                data_type=DataType.WEATHER
            ),
            CacheableRequest(
                source_name="soil",
                operation="characteristics",
                params={"lat": 42.0, "lon": -93.6},
                data_type=DataType.SOIL
            )
        ]
        
        results = await cache_service.batch_get_cached_data(requests)
        
        assert len(results) == 2
        assert results[0].cache_hit is True  # Weather from cache
        assert results[1].cache_hit is False  # Soil from ingestion
    
    @pytest.mark.asyncio
    async def test_cache_callbacks(self, cache_service):
        """Test cache hit/miss callbacks."""
        hit_callback_called = False
        miss_callback_called = False
        
        async def hit_callback(data, request):
            nonlocal hit_callback_called
            hit_callback_called = True
            assert data is not None
            assert isinstance(request, CacheableRequest)
        
        async def miss_callback(data, request):
            nonlocal miss_callback_called
            miss_callback_called = True
            assert data is not None
            assert isinstance(request, CacheableRequest)
        
        # Register callbacks
        cache_service.register_cache_hit_callback(DataType.WEATHER, hit_callback)
        cache_service.register_cache_miss_callback(DataType.WEATHER, miss_callback)
        
        # Test cache hit scenario
        cache_service.cache_manager.get.return_value = {"temperature": 75.5}
        
        request = CacheableRequest(
            source_name="weather",
            operation="current",
            params={"lat": 42.0, "lon": -93.6},
            data_type=DataType.WEATHER
        )
        
        await cache_service.get_cached_data(request)
        
        assert hit_callback_called is True
        
        # Test cache miss scenario
        cache_service.cache_manager.get.return_value = None
        cache_service.ingestion_pipeline.ingest_data.return_value = IngestionResult(
            source_name="weather",
            success=True,
            data={"temperature": 72.0},
            quality_score=0.9
        )
        
        await cache_service.get_cached_data(request)
        
        assert miss_callback_called is True
    
    @pytest.mark.asyncio
    async def test_preload_common_data(self, cache_service):
        """Test preloading common data."""
        context = {
            "weather_locations": [
                {"lat": 42.0, "lon": -93.6},
                {"lat": 40.1, "lon": -88.2}
            ],
            "soil_locations": [
                {"lat": 42.0, "lon": -93.6}
            ],
            "commodities": ["corn", "soybean"]
        }
        
        # Mock successful ingestion for all preload requests
        cache_service.ingestion_pipeline.ingest_data.return_value = IngestionResult(
            source_name="test",
            success=True,
            data={"test": "data"},
            quality_score=0.9
        )
        
        await cache_service.preload_common_data(context)
        
        # Verify multiple ingestion calls were made
        assert cache_service.ingestion_pipeline.ingest_data.call_count >= 4
    
    @pytest.mark.asyncio
    async def test_cache_invalidation(self, cache_service, mock_cache_manager):
        """Test cache invalidation by data type."""
        mock_cache_manager.clear_by_pattern.return_value = 3
        
        # Test weather invalidation
        await cache_service.invalidate_related_cache(
            DataType.WEATHER,
            {"location": {"lat": 42.0, "lon": -93.6}}
        )
        
        # Verify pattern clearing was called
        mock_cache_manager.clear_by_pattern.assert_called()
        
        # Test recommendation invalidation
        await cache_service.invalidate_related_cache(
            DataType.RECOMMENDATION,
            {"farm_id": "farm123"}
        )
        
        # Should have been called multiple times
        assert mock_cache_manager.clear_by_pattern.call_count >= 2
    
    @pytest.mark.asyncio
    async def test_cache_health_status(self, cache_service, mock_cache_manager):
        """Test cache health status reporting."""
        # Mock comprehensive stats
        mock_stats = {
            "l1_cache": {"hit_rate": 85.0},
            "l2_cache": {"hit_rate": 75.0},
            "performance_metrics": {}
        }
        mock_cache_manager.get_comprehensive_stats.return_value = mock_stats
        
        health_status = await cache_service.get_cache_health_status()
        
        assert "health_status" in health_status
        assert "overall_hit_rate" in health_status
        assert "cache_stats" in health_status
        assert "recommendations" in health_status
        
        # Should be excellent with 80% hit rate
        assert health_status["health_status"] == "excellent"
        assert health_status["overall_hit_rate"] == 80.0


class TestAgriculturalCacheService:
    """Test agricultural-specific cache service."""
    
    @pytest.fixture
    def mock_cache_integration(self):
        """Create mock cache integration service."""
        service = Mock()
        service.get_cached_data = AsyncMock()
        service.preload_common_data = AsyncMock()
        service.invalidate_related_cache = AsyncMock()
        service.get_cache_health_status = AsyncMock()
        service.register_cache_hit_callback = Mock()
        service.register_cache_miss_callback = Mock()
        return service
    
    @pytest.fixture
    def agricultural_service(self, mock_cache_integration):
        """Create agricultural cache service."""
        return AgriculturalCacheService(mock_cache_integration)
    
    @pytest.mark.asyncio
    async def test_get_weather_data(self, agricultural_service, mock_cache_integration):
        """Test getting weather data through agricultural service."""
        # Mock successful weather data retrieval
        mock_cache_integration.get_cached_data.return_value = IngestionResult(
            source_name="weather",
            success=True,
            data={"temperature": 75.5, "humidity": 65},
            quality_score=0.9
        )
        
        result = await agricultural_service.get_weather_data(42.0, -93.6)
        
        assert result.success is True
        assert "temperature" in result.data
        
        # Verify correct request was made
        mock_cache_integration.get_cached_data.assert_called_once()
        call_args = mock_cache_integration.get_cached_data.call_args[0][0]
        assert call_args.source_name == "weather"
        assert call_args.operation == "current"
        assert call_args.data_type == DataType.WEATHER
        assert call_args.params == {"latitude": 42.0, "longitude": -93.6}
    
    @pytest.mark.asyncio
    async def test_get_soil_data(self, agricultural_service, mock_cache_integration):
        """Test getting soil data through agricultural service."""
        mock_cache_integration.get_cached_data.return_value = IngestionResult(
            source_name="soil",
            success=True,
            data={"ph": 6.5, "organic_matter": 3.2},
            quality_score=0.85
        )
        
        result = await agricultural_service.get_soil_data(42.0, -93.6, force_refresh=True)
        
        assert result.success is True
        assert "ph" in result.data
        
        # Verify force refresh was passed through
        call_args = mock_cache_integration.get_cached_data.call_args[0][0]
        assert call_args.force_refresh is True
        assert call_args.data_type == DataType.SOIL
    
    @pytest.mark.asyncio
    async def test_get_crop_recommendations(self, agricultural_service, mock_cache_integration):
        """Test getting crop recommendations through agricultural service."""
        mock_cache_integration.get_cached_data.return_value = IngestionResult(
            source_name="recommendation_engine",
            success=True,
            data={"recommended_varieties": ["Pioneer P1197AM"]},
            quality_score=0.92
        )
        
        soil_data = {"ph": 6.2, "organic_matter": 3.5}
        result = await agricultural_service.get_crop_recommendations(
            "farm123", "corn", soil_data
        )
        
        assert result.success is True
        assert "recommended_varieties" in result.data
        
        # Verify correct parameters
        call_args = mock_cache_integration.get_cached_data.call_args[0][0]
        assert call_args.source_name == "recommendation_engine"
        assert call_args.operation == "crop_selection"
        assert call_args.data_type == DataType.RECOMMENDATION
        assert call_args.params["farm_id"] == "farm123"
        assert call_args.params["crop_type"] == "corn"
        assert call_args.params["soil_data"] == soil_data
    
    @pytest.mark.asyncio
    async def test_get_market_prices(self, agricultural_service, mock_cache_integration):
        """Test getting market prices through agricultural service."""
        mock_cache_integration.get_cached_data.return_value = IngestionResult(
            source_name="market",
            success=True,
            data={"price_per_bushel": 4.25, "currency": "USD"},
            quality_score=0.95
        )
        
        result = await agricultural_service.get_market_prices("corn", "2024-12-09")
        
        assert result.success is True
        assert "price_per_bushel" in result.data
        
        # Verify correct parameters
        call_args = mock_cache_integration.get_cached_data.call_args[0][0]
        assert call_args.source_name == "market"
        assert call_args.operation == "prices"
        assert call_args.data_type == DataType.MARKET
        assert call_args.params["commodity"] == "corn"
        assert call_args.params["date"] == "2024-12-09"
    
    @pytest.mark.asyncio
    async def test_preload_farm_data(self, agricultural_service, mock_cache_integration):
        """Test preloading farm-specific data."""
        farm_profile = {
            "location": {"lat": 42.0, "lon": -93.6},
            "primary_crops": ["corn", "soybean"]
        }
        
        await agricultural_service.preload_farm_data(farm_profile)
        
        # Verify preload was called with correct context
        mock_cache_integration.preload_common_data.assert_called_once()
        call_args = mock_cache_integration.preload_common_data.call_args[0][0]
        
        assert "weather_locations" in call_args
        assert "soil_locations" in call_args
        assert "commodities" in call_args
        assert call_args["commodities"] == ["corn", "soybean"]
    
    @pytest.mark.asyncio
    async def test_invalidate_farm_cache(self, agricultural_service, mock_cache_integration):
        """Test invalidating farm-specific cache."""
        await agricultural_service.invalidate_farm_cache("farm123")
        
        # Verify invalidation was called
        mock_cache_integration.invalidate_related_cache.assert_called_once_with(
            DataType.RECOMMENDATION,
            {"farm_id": "farm123"}
        )
    
    @pytest.mark.asyncio
    async def test_cache_performance_report(self, agricultural_service, mock_cache_integration):
        """Test generating cache performance report."""
        mock_health_status = {
            "health_status": "excellent",
            "overall_hit_rate": 85.0,
            "cache_stats": {},
            "recommendations": []
        }
        mock_cache_integration.get_cache_health_status.return_value = mock_health_status
        
        report = await agricultural_service.get_cache_performance_report()
        
        assert "timestamp" in report
        assert "cache_health" in report
        assert "agricultural_metrics" in report
        
        # Verify agricultural metrics are included
        ag_metrics = report["agricultural_metrics"]
        assert "weather_cache_efficiency" in ag_metrics
        assert "soil_cache_efficiency" in ag_metrics
        assert "recommendation_cache_efficiency" in ag_metrics
        assert "market_cache_efficiency" in ag_metrics
    
    def test_callback_registration(self, agricultural_service, mock_cache_integration):
        """Test that agricultural callbacks are registered."""
        # Verify callbacks were registered during initialization
        assert mock_cache_integration.register_cache_hit_callback.call_count >= 2
        assert mock_cache_integration.register_cache_miss_callback.call_count >= 2
        
        # Verify specific data types were registered
        registered_data_types = []
        for call in mock_cache_integration.register_cache_hit_callback.call_args_list:
            registered_data_types.append(call[0][0])
        
        assert DataType.WEATHER in registered_data_types
        assert DataType.SOIL in registered_data_types


class TestFactoryFunctions:
    """Test factory functions for service creation."""
    
    @pytest.mark.asyncio
    async def test_create_cache_integration_service(self):
        """Test cache integration service factory."""
        with patch('services.data_integration.src.services.cache_integration_service.create_enhanced_cache_manager') as mock_create:
            mock_cache_manager = Mock()
            mock_create.return_value = mock_cache_manager
            
            mock_pipeline = Mock()
            
            service = await create_cache_integration_service(
                "redis://localhost:6379",
                mock_pipeline
            )
            
            assert isinstance(service, CacheIntegrationService)
            assert service.cache_manager == mock_cache_manager
            assert service.ingestion_pipeline == mock_pipeline
    
    @pytest.mark.asyncio
    async def test_create_agricultural_cache_service(self):
        """Test agricultural cache service factory."""
        with patch('services.data_integration.src.services.cache_integration_service.create_cache_integration_service') as mock_create:
            mock_integration_service = Mock()
            mock_create.return_value = mock_integration_service
            
            service = await create_agricultural_cache_service("redis://localhost:6379")
            
            assert isinstance(service, AgriculturalCacheService)
            assert service.cache_service == mock_integration_service


@pytest.mark.integration
class TestCacheIntegrationIntegration:
    """Integration tests for cache integration service."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_cache_flow(self):
        """Test complete end-to-end cache flow."""
        with patch('redis.asyncio.from_url') as mock_redis:
            mock_client = AsyncMock()
            mock_redis.return_value = mock_client
            
            # Mock ingestion pipeline
            mock_pipeline = Mock()
            mock_pipeline.ingest_data = AsyncMock(return_value=IngestionResult(
                source_name="weather",
                success=True,
                data={"temperature": 75.5},
                quality_score=0.9
            ))
            
            # Create service
            service = await create_cache_integration_service(
                "redis://localhost:6379",
                mock_pipeline
            )
            
            # Test cache miss -> ingestion -> cache set
            request = CacheableRequest(
                source_name="weather",
                operation="current",
                params={"lat": 42.0, "lon": -93.6},
                data_type=DataType.WEATHER
            )
            
            result = await service.get_cached_data(request)
            
            assert result.success is True
            assert result.data["temperature"] == 75.5
            
            # Clean up
            await service.cache_manager.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])