"""
Tests for the Data Ingestion Service

Tests for the main ingestion service that orchestrates the framework.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from src.services.ingestion_service import DataIngestionService
from src.services.data_ingestion_framework import IngestionResult


class TestDataIngestionService:
    """Test the main data ingestion service."""
    
    @pytest.fixture
    async def mock_ingestion_service(self):
        """Create a mock ingestion service for testing."""
        service = DataIngestionService("redis://localhost:6379")
        
        # Mock all the components
        service.cache_manager = AsyncMock()
        service.cache_manager.connect = AsyncMock()
        service.cache_manager.redis_client = AsyncMock()
        service.cache_manager.redis_client.ping = AsyncMock(return_value=True)
        
        service.pipeline = AsyncMock()
        service.orchestrator = AsyncMock()
        service.orchestrator.start_scheduler = AsyncMock()
        
        # Mock adapters
        service.weather_adapter = AsyncMock()
        service.soil_adapter = AsyncMock()
        service.crop_adapter = AsyncMock()
        service.market_adapter = AsyncMock()
        
        return service
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, mock_ingestion_service):
        """Test service initialization."""
        service = mock_ingestion_service
        
        await service.initialize()
        
        assert service.initialized
        service.cache_manager.connect.assert_called_once()
        service.orchestrator.start_scheduler.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_weather_data(self, mock_ingestion_service):
        """Test weather data retrieval."""
        service = mock_ingestion_service
        await service.initialize()
        
        # Mock successful ingestion result
        mock_result = IngestionResult(
            source_name="weather_service",
            success=True,
            data={
                "temperature_f": 75.0,
                "humidity_percent": 65.0,
                "conditions": "clear"
            },
            quality_score=0.9
        )
        service.pipeline.ingest_data.return_value = mock_result
        
        result = await service.get_weather_data(42.0, -93.6, "current_weather")
        
        assert result.success
        assert result.data["temperature_f"] == 75.0
        service.pipeline.ingest_data.assert_called_once_with(
            "weather_service", "current_weather", latitude=42.0, longitude=-93.6
        )
    
    @pytest.mark.asyncio
    async def test_get_soil_data(self, mock_ingestion_service):
        """Test soil data retrieval."""
        service = mock_ingestion_service
        await service.initialize()
        
        # Mock successful ingestion result
        mock_result = IngestionResult(
            source_name="soil_service",
            success=True,
            data={
                "soil_series": "Clarion",
                "soil_texture": "loam",
                "ph": 6.5
            },
            quality_score=0.85
        )
        service.pipeline.ingest_data.return_value = mock_result
        
        result = await service.get_soil_data(42.0, -93.6, "soil_characteristics")
        
        assert result.success
        assert result.data["soil_series"] == "Clarion"
        service.pipeline.ingest_data.assert_called_once_with(
            "soil_service", "soil_characteristics", latitude=42.0, longitude=-93.6
        )
    
    @pytest.mark.asyncio
    async def test_get_crop_data(self, mock_ingestion_service):
        """Test crop data retrieval."""
        service = mock_ingestion_service
        await service.initialize()
        
        # Mock successful ingestion result
        mock_result = IngestionResult(
            source_name="crop_database",
            success=True,
            data={
                "crop_name": "corn",
                "varieties": [
                    {"variety_name": "Pioneer P1197AM", "yield_potential": 185}
                ]
            },
            quality_score=0.95
        )
        service.pipeline.ingest_data.return_value = mock_result
        
        result = await service.get_crop_data("corn", "crop_varieties")
        
        assert result.success
        assert result.data["crop_name"] == "corn"
        service.pipeline.ingest_data.assert_called_once_with(
            "crop_database", "crop_varieties", crop_name="corn"
        )
    
    @pytest.mark.asyncio
    async def test_get_market_data(self, mock_ingestion_service):
        """Test market data retrieval."""
        service = mock_ingestion_service
        await service.initialize()
        
        # Mock successful ingestion result
        mock_result = IngestionResult(
            source_name="market_data",
            success=True,
            data={
                "commodities": {"corn_per_bushel": 4.25},
                "fertilizers": {"urea_per_ton": 420.00}
            },
            quality_score=0.8
        )
        service.pipeline.ingest_data.return_value = mock_result
        
        result = await service.get_market_data("all_prices")
        
        assert result.success
        assert result.data["commodities"]["corn_per_bushel"] == 4.25
        service.pipeline.ingest_data.assert_called_once_with(
            "market_data", "all_prices"
        )
    
    @pytest.mark.asyncio
    async def test_batch_ingest_data(self, mock_ingestion_service):
        """Test batch data ingestion."""
        service = mock_ingestion_service
        await service.initialize()
        
        # Mock batch ingestion results
        mock_results = [
            IngestionResult(
                source_name="weather_service",
                success=True,
                data={"temperature_f": 75.0},
                quality_score=0.9
            ),
            IngestionResult(
                source_name="soil_service",
                success=True,
                data={"ph": 6.5},
                quality_score=0.85
            )
        ]
        service.pipeline.batch_ingest.return_value = mock_results
        
        requests = [
            {
                "source_name": "weather_service",
                "operation": "current_weather",
                "params": {"latitude": 42.0, "longitude": -93.6}
            },
            {
                "source_name": "soil_service",
                "operation": "soil_characteristics",
                "params": {"latitude": 42.0, "longitude": -93.6}
            }
        ]
        
        results = await service.batch_ingest_data(requests)
        
        assert len(results) == 2
        assert all(result.success for result in results)
        service.pipeline.batch_ingest.assert_called_once_with(requests)
    
    @pytest.mark.asyncio
    async def test_health_check_healthy(self, mock_ingestion_service):
        """Test health check when service is healthy."""
        service = mock_ingestion_service
        await service.initialize()
        
        # Mock healthy pipeline
        service.pipeline.health_check.return_value = {
            "pipeline_status": "healthy",
            "cache_status": "healthy",
            "sources": {}
        }
        
        # Mock healthy scheduler
        service.orchestrator.scheduler = MagicMock()
        service.orchestrator.scheduler.running = True
        service.orchestrator.jobs = {"test_job": MagicMock()}
        
        # Mock metrics
        service.pipeline.get_metrics.return_value = {"total_requests": 100}
        service.orchestrator.get_metrics.return_value = {"total_jobs_run": 10}
        
        health = await service.health_check()
        
        assert health["status"] == "healthy"
        assert health["pipeline"]["pipeline_status"] == "healthy"
        assert health["etl"]["scheduler_running"] is True
    
    @pytest.mark.asyncio
    async def test_health_check_degraded(self, mock_ingestion_service):
        """Test health check when service is degraded."""
        service = mock_ingestion_service
        await service.initialize()
        
        # Mock degraded pipeline
        service.pipeline.health_check.return_value = {
            "pipeline_status": "degraded",
            "cache_status": "unhealthy",
            "sources": {}
        }
        
        # Mock healthy scheduler
        service.orchestrator.scheduler = MagicMock()
        service.orchestrator.scheduler.running = True
        service.orchestrator.jobs = {}
        
        # Mock metrics
        service.pipeline.get_metrics.return_value = {"total_requests": 100}
        service.orchestrator.get_metrics.return_value = {"total_jobs_run": 10}
        
        health = await service.health_check()
        
        assert health["status"] == "degraded"
        assert health["pipeline"]["pipeline_status"] == "degraded"
    
    @pytest.mark.asyncio
    async def test_etl_job_management(self, mock_ingestion_service):
        """Test ETL job management functions."""
        service = mock_ingestion_service
        await service.initialize()
        
        # Mock job status
        service.orchestrator.get_job_status.return_value = {
            "job_id": "test_job",
            "enabled": True,
            "is_running": False
        }
        
        # Mock all jobs status
        service.orchestrator.get_all_jobs_status.return_value = {
            "jobs": {"test_job": {"enabled": True}},
            "scheduler_running": True
        }
        
        # Test get job status
        status = service.get_job_status("test_job")
        assert status["job_id"] == "test_job"
        
        # Test get all jobs status
        all_status = service.get_all_jobs_status()
        assert "jobs" in all_status
        assert all_status["scheduler_running"] is True
        
        # Test enable/disable job
        service.enable_etl_job("test_job")
        service.orchestrator.enable_job.assert_called_once_with("test_job")
        
        service.disable_etl_job("test_job")
        service.orchestrator.disable_job.assert_called_once_with("test_job")
    
    @pytest.mark.asyncio
    async def test_cache_refresh(self, mock_ingestion_service):
        """Test cache refresh functionality."""
        service = mock_ingestion_service
        await service.initialize()
        
        # Test refresh specific source
        await service.refresh_cache("weather_service")
        service.pipeline.refresh_cache.assert_called_with("weather_service")
        
        # Test refresh all sources
        await service.refresh_cache()
        service.pipeline.refresh_cache.assert_called_with(None)
    
    @pytest.mark.asyncio
    async def test_service_shutdown(self, mock_ingestion_service):
        """Test service shutdown."""
        service = mock_ingestion_service
        await service.initialize()
        
        # Mock shutdown methods
        service.orchestrator.stop_scheduler = AsyncMock()
        service.weather_adapter.close = AsyncMock()
        service.cache_manager.close = AsyncMock()
        
        await service.shutdown()
        
        assert not service.initialized
        service.orchestrator.stop_scheduler.assert_called_once()
        service.weather_adapter.close.assert_called_once()
        service.cache_manager.close.assert_called_once()


@pytest.mark.asyncio
async def test_global_service_instance():
    """Test global service instance management."""
    from src.services.ingestion_service import get_ingestion_service, shutdown_ingestion_service, _ingestion_service
    
    # Ensure clean state
    await shutdown_ingestion_service()
    
    with patch('src.services.ingestion_service.DataIngestionService') as MockService:
        mock_instance = AsyncMock()
        mock_instance.initialize = AsyncMock()
        MockService.return_value = mock_instance
        
        # Test getting service instance
        service1 = await get_ingestion_service()
        service2 = await get_ingestion_service()
        
        # Should return same instance
        assert service1 is service2
        mock_instance.initialize.assert_called_once()
        
        # Test shutdown
        mock_instance.shutdown = AsyncMock()
        await shutdown_ingestion_service()
        mock_instance.shutdown.assert_called_once()