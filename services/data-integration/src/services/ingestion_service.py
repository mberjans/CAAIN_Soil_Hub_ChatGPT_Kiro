"""
Data Ingestion Service

Main service that orchestrates the data ingestion framework, ETL jobs,
and provides a unified interface for agricultural data ingestion.
"""

import asyncio
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from .data_ingestion_framework import (
    DataIngestionPipeline, 
    CacheManager, 
    AgriculturalDataValidator,
    DataSourceConfig,
    DataSourceType,
    IngestionResult
)
from .etl_orchestrator import ETLOrchestrator, ETLJobConfig, JobPriority
from .data_source_adapters import (
    WeatherServiceAdapter,
    SoilServiceAdapter,
    CropDatabaseAdapter,
    MarketDataAdapter
)

logger = structlog.get_logger(__name__)


class DataIngestionService:
    """Main data ingestion service for AFAS."""
    
    def __init__(self, redis_url: str = None):
        # Initialize components
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self.cache_manager = CacheManager(self.redis_url)
        self.validator = AgriculturalDataValidator()
        self.pipeline = DataIngestionPipeline(self.cache_manager, self.validator)
        self.orchestrator = ETLOrchestrator(self.pipeline)
        
        # Initialize adapters
        self.weather_adapter = WeatherServiceAdapter()
        self.soil_adapter = SoilServiceAdapter()
        self.crop_adapter = CropDatabaseAdapter()
        self.market_adapter = MarketDataAdapter()
        
        self.initialized = False
    
    async def initialize(self):
        """Initialize the data ingestion service."""
        if self.initialized:
            return
        
        try:
            # Connect to cache
            await self.cache_manager.connect()
            
            # Register data sources
            await self._register_data_sources()
            
            # Register ETL jobs
            await self._register_etl_jobs()
            
            # Start ETL scheduler
            await self.orchestrator.start_scheduler()
            
            self.initialized = True
            logger.info("Data ingestion service initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize data ingestion service", error=str(e))
            raise
    
    async def _register_data_sources(self):
        """Register all data sources with the ingestion pipeline."""
        
        # Weather service
        weather_config = DataSourceConfig(
            name="weather_service",
            source_type=DataSourceType.WEATHER,
            base_url="https://api.weather.gov",
            rate_limit_per_minute=60,
            timeout_seconds=30,
            retry_attempts=3,
            cache_ttl_seconds=1800,  # 30 minutes for weather data
            quality_threshold=0.7,
            enabled=True
        )
        self.pipeline.register_data_source(weather_config, self.weather_adapter.handle_operation)
        
        # Soil service
        soil_config = DataSourceConfig(
            name="soil_service",
            source_type=DataSourceType.SOIL,
            base_url="https://sdmdataaccess.sc.egov.usda.gov",
            rate_limit_per_minute=30,
            timeout_seconds=45,
            retry_attempts=3,
            cache_ttl_seconds=86400,  # 24 hours for soil data
            quality_threshold=0.8,
            enabled=True
        )
        self.pipeline.register_data_source(soil_config, self.soil_adapter.handle_operation)
        
        # Crop database
        crop_config = DataSourceConfig(
            name="crop_database",
            source_type=DataSourceType.CROP,
            base_url="internal",
            rate_limit_per_minute=120,
            timeout_seconds=15,
            retry_attempts=2,
            cache_ttl_seconds=43200,  # 12 hours for crop data
            quality_threshold=0.9,
            enabled=True
        )
        self.pipeline.register_data_source(crop_config, self.crop_adapter.handle_operation)
        
        # Market data
        market_config = DataSourceConfig(
            name="market_data",
            source_type=DataSourceType.MARKET,
            base_url="internal",
            rate_limit_per_minute=60,
            timeout_seconds=20,
            retry_attempts=2,
            cache_ttl_seconds=3600,  # 1 hour for market data
            quality_threshold=0.8,
            enabled=True
        )
        self.pipeline.register_data_source(market_config, self.market_adapter.handle_operation)
        
        logger.info("Registered all data sources")
    
    async def _register_etl_jobs(self):
        """Register ETL jobs for scheduled data updates."""
        
        # Weather data refresh job - every 30 minutes
        weather_job = ETLJobConfig(
            job_id="weather_refresh",
            name="Weather Data Refresh",
            description="Refresh weather data for key agricultural regions",
            source_name="weather_service",
            operation="current_weather",
            parameters={
                "latitude": 42.0308,  # Ames, Iowa as default
                "longitude": -93.6319
            },
            schedule_interval_minutes=30,
            priority=JobPriority.HIGH,
            timeout_minutes=5,
            retry_attempts=3,
            enabled=True
        )
        self.orchestrator.register_job(weather_job)
        
        # Market data refresh job - every hour
        market_job = ETLJobConfig(
            job_id="market_data_refresh",
            name="Market Data Refresh",
            description="Refresh commodity and fertilizer prices",
            source_name="market_data",
            operation="all_prices",
            parameters={},
            schedule_interval_minutes=60,
            priority=JobPriority.MEDIUM,
            timeout_minutes=3,
            retry_attempts=2,
            enabled=True
        )
        self.orchestrator.register_job(market_job)
        
        # Soil data validation job - daily at 2 AM
        soil_validation_job = ETLJobConfig(
            job_id="soil_data_validation",
            name="Soil Data Validation",
            description="Validate and refresh soil database connections",
            source_name="soil_service",
            operation="soil_characteristics",
            parameters={
                "latitude": 42.0308,  # Test location
                "longitude": -93.6319
            },
            schedule_cron="0 2 * * *",  # Daily at 2 AM
            priority=JobPriority.LOW,
            timeout_minutes=10,
            retry_attempts=2,
            enabled=True
        )
        self.orchestrator.register_job(soil_validation_job)
        
        logger.info("Registered ETL jobs")
    
    async def get_weather_data(self, latitude: float, longitude: float, 
                              operation: str = "current_weather", **kwargs) -> IngestionResult:
        """Get weather data through the ingestion pipeline."""
        params = {"latitude": latitude, "longitude": longitude, **kwargs}
        return await self.pipeline.ingest_data("weather_service", operation, **params)
    
    async def get_soil_data(self, latitude: float, longitude: float, 
                           operation: str = "soil_characteristics", **kwargs) -> IngestionResult:
        """Get soil data through the ingestion pipeline."""
        params = {"latitude": latitude, "longitude": longitude, **kwargs}
        return await self.pipeline.ingest_data("soil_service", operation, **params)
    
    async def get_crop_data(self, crop_name: str, operation: str = "crop_varieties", 
                           **kwargs) -> IngestionResult:
        """Get crop data through the ingestion pipeline."""
        params = {"crop_name": crop_name, **kwargs}
        return await self.pipeline.ingest_data("crop_database", operation, **params)
    
    async def get_market_data(self, operation: str = "all_prices", **kwargs) -> IngestionResult:
        """Get market data through the ingestion pipeline."""
        return await self.pipeline.ingest_data("market_data", operation, **kwargs)
    
    async def batch_ingest_data(self, requests: List[Dict[str, Any]]) -> List[IngestionResult]:
        """Perform batch data ingestion."""
        return await self.pipeline.batch_ingest(requests)
    
    async def refresh_cache(self, source_name: Optional[str] = None):
        """Refresh cached data."""
        await self.pipeline.refresh_cache(source_name)
    
    async def run_etl_job(self, job_id: str):
        """Manually trigger an ETL job."""
        return await self.orchestrator.run_job_now(job_id)
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get ETL job status."""
        return self.orchestrator.get_job_status(job_id)
    
    def get_all_jobs_status(self) -> Dict[str, Any]:
        """Get status for all ETL jobs."""
        return self.orchestrator.get_all_jobs_status()
    
    def enable_etl_job(self, job_id: str):
        """Enable an ETL job."""
        self.orchestrator.enable_job(job_id)
    
    def disable_etl_job(self, job_id: str):
        """Disable an ETL job."""
        self.orchestrator.disable_job(job_id)
    
    def get_pipeline_metrics(self) -> Dict[str, Any]:
        """Get ingestion pipeline metrics."""
        return self.pipeline.get_metrics()
    
    def get_etl_metrics(self) -> Dict[str, Any]:
        """Get ETL orchestrator metrics."""
        return self.orchestrator.get_metrics()
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        if not self.initialized:
            return {
                "status": "unhealthy",
                "message": "Service not initialized"
            }
        
        try:
            # Check pipeline health
            pipeline_health = await self.pipeline.health_check()
            
            # Check ETL scheduler
            etl_health = {
                "scheduler_running": self.orchestrator.scheduler.running,
                "registered_jobs": len(self.orchestrator.jobs),
                "enabled_jobs": len([j for j in self.orchestrator.jobs.values() if j.enabled])
            }
            
            # Overall status
            overall_status = "healthy"
            if pipeline_health["pipeline_status"] != "healthy":
                overall_status = "degraded"
            if not etl_health["scheduler_running"]:
                overall_status = "degraded"
            
            return {
                "status": overall_status,
                "pipeline": pipeline_health,
                "etl": etl_health,
                "metrics": {
                    "pipeline": self.get_pipeline_metrics(),
                    "etl": self.get_etl_metrics()
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def shutdown(self):
        """Shutdown the data ingestion service."""
        try:
            # Stop ETL scheduler
            await self.orchestrator.stop_scheduler()
            
            # Close adapters
            await self.weather_adapter.close()
            
            # Close cache connection
            await self.cache_manager.close()
            
            self.initialized = False
            logger.info("Data ingestion service shutdown complete")
            
        except Exception as e:
            logger.error("Error during shutdown", error=str(e))
            raise


# Global service instance
_ingestion_service: Optional[DataIngestionService] = None


async def get_ingestion_service() -> DataIngestionService:
    """Get or create the global ingestion service instance."""
    global _ingestion_service
    
    if _ingestion_service is None:
        _ingestion_service = DataIngestionService()
        await _ingestion_service.initialize()
    
    return _ingestion_service


async def shutdown_ingestion_service():
    """Shutdown the global ingestion service instance."""
    global _ingestion_service
    
    if _ingestion_service:
        await _ingestion_service.shutdown()
        _ingestion_service = None