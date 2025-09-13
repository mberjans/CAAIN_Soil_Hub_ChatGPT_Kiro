"""
Tests for the Data Ingestion Framework

Comprehensive tests for the data ingestion pipeline, validation,
caching, and ETL orchestration components.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import json

from src.services.data_ingestion_framework import (
    DataIngestionPipeline,
    CacheManager,
    AgriculturalDataValidator,
    DataSourceConfig,
    DataSourceType,
    IngestionResult,
    ValidationResult
)
from src.services.etl_orchestrator import (
    ETLOrchestrator,
    ETLJobConfig,
    JobPriority,
    JobStatus
)


class TestAgriculturalDataValidator:
    """Test the agricultural data validator."""
    
    @pytest.fixture
    def validator(self):
        return AgriculturalDataValidator()
    
    @pytest.fixture
    def weather_config(self):
        return DataSourceConfig(
            name="test_weather",
            source_type=DataSourceType.WEATHER,
            base_url="https://test.weather.api",
            quality_threshold=0.8
        )
    
    @pytest.fixture
    def soil_config(self):
        return DataSourceConfig(
            name="test_soil",
            source_type=DataSourceType.SOIL,
            base_url="https://test.soil.api",
            quality_threshold=0.8
        )
    
    @pytest.mark.asyncio
    async def test_validate_good_weather_data(self, validator, weather_config):
        """Test validation of good weather data."""
        weather_data = {
            "temperature_f": 75.0,
            "humidity_percent": 65.0,
            "precipitation_inches": 0.1,
            "wind_speed_mph": 8.0,
            "conditions": "partly cloudy",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        result = await validator.validate(weather_data, weather_config)
        
        assert result.is_valid
        assert len(result.errors) == 0
        assert result.quality_score >= 0.8
        assert result.normalized_data == weather_data
    
    @pytest.mark.asyncio
    async def test_validate_bad_weather_data(self, validator, weather_config):
        """Test validation of invalid weather data."""
        weather_data = {
            "temperature_f": 200.0,  # Invalid temperature
            "humidity_percent": 150.0,  # Invalid humidity
            "precipitation_inches": -1.0,  # Invalid precipitation
            "wind_speed_mph": "not_a_number"  # Invalid type
        }
        
        result = await validator.validate(weather_data, weather_config)
        
        assert not result.is_valid
        assert len(result.errors) > 0
        assert result.quality_score < 0.8
    
    @pytest.mark.asyncio
    async def test_validate_good_soil_data(self, validator, soil_config):
        """Test validation of good soil data."""
        soil_data = {
            "ph": 6.5,
            "organic_matter_percent": 3.2,
            "phosphorus_ppm": 25.0,
            "potassium_ppm": 180.0,
            "soil_texture": "silt_loam",
            "drainage_class": "well_drained"
        }
        
        result = await validator.validate(soil_data, soil_config)
        
        assert result.is_valid
        assert len(result.errors) == 0
        assert result.quality_score >= 0.8
    
    @pytest.mark.asyncio
    async def test_validate_bad_soil_data(self, validator, soil_config):
        """Test validation of invalid soil data."""
        soil_data = {
            "ph": 15.0,  # Invalid pH
            "organic_matter_percent": -5.0,  # Invalid negative value
            "phosphorus_ppm": "not_a_number",  # Invalid type
            "potassium_ppm": 2000.0  # Extremely high value
        }
        
        result = await validator.validate(soil_data, soil_config)
        
        assert not result.is_valid
        assert len(result.errors) > 0
        assert result.quality_score < 0.8


class TestCacheManager:
    """Test the Redis cache manager."""
    
    @pytest.fixture
    async def cache_manager(self):
        # Use a mock Redis client for testing
        cache = CacheManager("redis://localhost:6379")
        cache.redis_client = AsyncMock()
        return cache
    
    @pytest.mark.asyncio
    async def test_cache_set_get(self, cache_manager):
        """Test setting and getting cache data."""
        test_data = {"temperature": 75.0, "humidity": 65.0}
        cache_key = "test_key"
        
        # Mock Redis operations
        cache_manager.redis_client.setex.return_value = True
        cache_manager.redis_client.get.return_value = json.dumps(test_data)
        
        # Test set
        result = await cache_manager.set(cache_key, test_data, 3600)
        assert result is True
        
        # Test get
        cached_data = await cache_manager.get(cache_key)
        assert cached_data == test_data
    
    @pytest.mark.asyncio
    async def test_cache_miss(self, cache_manager):
        """Test cache miss scenario."""
        cache_manager.redis_client.get.return_value = None
        
        result = await cache_manager.get("nonexistent_key")
        assert result is None
    
    def test_generate_cache_key(self, cache_manager):
        """Test cache key generation."""
        key = cache_manager.generate_cache_key(
            "weather_service", 
            "current_weather",
            latitude=42.0,
            longitude=-93.6
        )
        
        assert key.startswith("afas:data:weather_service:current_weather:")
        assert len(key.split(":")) == 5  # afas:data:source:operation:hash


class TestDataIngestionPipeline:
    """Test the data ingestion pipeline."""
    
    @pytest.fixture
    async def mock_cache_manager(self):
        cache = AsyncMock(spec=CacheManager)
        cache.get.return_value = None  # Default to cache miss
        cache.set.return_value = True
        cache.generate_cache_key.return_value = "test_cache_key"
        return cache
    
    @pytest.fixture
    def mock_validator(self):
        validator = AsyncMock(spec=AgriculturalDataValidator)
        validator.validate.return_value = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            quality_score=0.9,
            normalized_data={"test": "data"}
        )
        return validator
    
    @pytest.fixture
    def pipeline(self, mock_cache_manager, mock_validator):
        return DataIngestionPipeline(mock_cache_manager, mock_validator)
    
    @pytest.fixture
    def test_config(self):
        return DataSourceConfig(
            name="test_source",
            source_type=DataSourceType.WEATHER,
            base_url="https://test.api",
            quality_threshold=0.8
        )
    
    @pytest.mark.asyncio
    async def test_successful_ingestion(self, pipeline, test_config, mock_cache_manager, mock_validator):
        """Test successful data ingestion."""
        # Mock handler
        async def mock_handler(operation, **params):
            return {"temperature": 75.0, "humidity": 65.0}
        
        pipeline.register_data_source(test_config, mock_handler)
        
        result = await pipeline.ingest_data("test_source", "current_weather", latitude=42.0)
        
        assert result.success
        assert result.source_name == "test_source"
        assert result.quality_score == 0.9
        assert result.data is not None
        assert not result.cache_hit
    
    @pytest.mark.asyncio
    async def test_cache_hit(self, pipeline, test_config, mock_cache_manager):
        """Test cache hit scenario."""
        cached_data = {"temperature": 75.0, "_quality_score": 0.9}
        mock_cache_manager.get.return_value = cached_data
        
        async def mock_handler(operation, **params):
            return {"temperature": 75.0}
        
        pipeline.register_data_source(test_config, mock_handler)
        
        result = await pipeline.ingest_data("test_source", "current_weather", latitude=42.0)
        
        assert result.success
        assert result.cache_hit
        assert result.quality_score == 0.9
    
    @pytest.mark.asyncio
    async def test_validation_failure(self, pipeline, test_config, mock_validator):
        """Test validation failure scenario."""
        mock_validator.validate.return_value = ValidationResult(
            is_valid=False,
            errors=["Invalid data"],
            warnings=[],
            quality_score=0.3
        )
        
        async def mock_handler(operation, **params):
            return {"invalid": "data"}
        
        pipeline.register_data_source(test_config, mock_handler)
        
        result = await pipeline.ingest_data("test_source", "current_weather", latitude=42.0)
        
        assert not result.success
        assert "Validation failed" in result.error_message
        assert result.quality_score == 0.3
    
    @pytest.mark.asyncio
    async def test_handler_exception(self, pipeline, test_config):
        """Test handler exception scenario."""
        async def failing_handler(operation, **params):
            raise Exception("Handler failed")
        
        pipeline.register_data_source(test_config, failing_handler)
        
        result = await pipeline.ingest_data("test_source", "current_weather", latitude=42.0)
        
        assert not result.success
        assert "Ingestion failed" in result.error_message
    
    @pytest.mark.asyncio
    async def test_batch_ingestion(self, pipeline, test_config, mock_cache_manager, mock_validator):
        """Test batch data ingestion."""
        async def mock_handler(operation, **params):
            return {"data": f"result_{params.get('id', 'default')}"}
        
        pipeline.register_data_source(test_config, mock_handler)
        
        requests = [
            {"source_name": "test_source", "operation": "test_op", "params": {"id": 1}},
            {"source_name": "test_source", "operation": "test_op", "params": {"id": 2}},
        ]
        
        results = await pipeline.batch_ingest(requests)
        
        assert len(results) == 2
        assert all(result.success for result in results)
        assert results[0].data["data"] == "result_1"
        assert results[1].data["data"] == "result_2"


class TestETLOrchestrator:
    """Test the ETL orchestrator."""
    
    @pytest.fixture
    def mock_pipeline(self):
        pipeline = AsyncMock(spec=DataIngestionPipeline)
        pipeline.ingest_data.return_value = IngestionResult(
            source_name="test_source",
            success=True,
            data={"test": "data"},
            quality_score=0.9
        )
        return pipeline
    
    @pytest.fixture
    def orchestrator(self, mock_pipeline):
        return ETLOrchestrator(mock_pipeline)
    
    @pytest.fixture
    def test_job_config(self):
        return ETLJobConfig(
            job_id="test_job",
            name="Test Job",
            description="Test ETL job",
            source_name="test_source",
            operation="test_operation",
            parameters={"param1": "value1"},
            schedule_interval_minutes=60,
            priority=JobPriority.MEDIUM,
            enabled=True
        )
    
    def test_register_job(self, orchestrator, test_job_config):
        """Test job registration."""
        orchestrator.register_job(test_job_config)
        
        assert test_job_config.job_id in orchestrator.jobs
        assert orchestrator.jobs[test_job_config.job_id] == test_job_config
    
    @pytest.mark.asyncio
    async def test_manual_job_execution(self, orchestrator, test_job_config, mock_pipeline):
        """Test manual job execution."""
        orchestrator.register_job(test_job_config)
        
        # Mock scheduler to avoid actual scheduling
        orchestrator.scheduler = MagicMock()
        orchestrator.scheduler.running = False
        
        job_run = await orchestrator.run_job_now(test_job_config.job_id)
        
        assert job_run.job_id == test_job_config.job_id
        assert job_run.status == JobStatus.SUCCESS
        mock_pipeline.ingest_data.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_job_with_dependencies(self, orchestrator):
        """Test job dependency handling."""
        # Create dependent jobs
        parent_job = ETLJobConfig(
            job_id="parent_job",
            name="Parent Job",
            description="Parent job",
            source_name="test_source",
            operation="test_op",
            parameters={},
            enabled=True
        )
        
        child_job = ETLJobConfig(
            job_id="child_job",
            name="Child Job", 
            description="Child job",
            source_name="test_source",
            operation="test_op",
            parameters={},
            depends_on=["parent_job"],
            enabled=True
        )
        
        orchestrator.register_job(parent_job)
        orchestrator.register_job(child_job)
        
        # Check dependency tracking
        assert "parent_job" in orchestrator.job_dependencies
        assert "child_job" in orchestrator.job_dependencies["parent_job"]
    
    def test_job_status_tracking(self, orchestrator, test_job_config):
        """Test job status tracking."""
        orchestrator.register_job(test_job_config)
        
        status = orchestrator.get_job_status(test_job_config.job_id)
        
        assert status["job_id"] == test_job_config.job_id
        assert status["name"] == test_job_config.name
        assert status["enabled"] == test_job_config.enabled
        assert "recent_runs" in status
    
    def test_enable_disable_job(self, orchestrator, test_job_config):
        """Test enabling and disabling jobs."""
        test_job_config.enabled = False
        orchestrator.register_job(test_job_config)
        
        # Test enable
        orchestrator.enable_job(test_job_config.job_id)
        assert orchestrator.jobs[test_job_config.job_id].enabled
        
        # Test disable
        orchestrator.disable_job(test_job_config.job_id)
        assert not orchestrator.jobs[test_job_config.job_id].enabled
    
    def test_metrics_collection(self, orchestrator):
        """Test metrics collection."""
        metrics = orchestrator.get_metrics()
        
        assert "total_jobs_run" in metrics
        assert "successful_jobs" in metrics
        assert "failed_jobs" in metrics
        assert "average_duration_seconds" in metrics


@pytest.mark.integration
class TestIngestionFrameworkIntegration:
    """Integration tests for the complete ingestion framework."""
    
    @pytest.fixture
    async def integration_setup(self):
        """Set up integration test environment."""
        # Use real components but with mocked external dependencies
        cache_manager = CacheManager("redis://localhost:6379")
        
        # Mock Redis for integration tests
        cache_manager.redis_client = AsyncMock()
        cache_manager.redis_client.ping.return_value = True
        cache_manager.redis_client.get.return_value = None
        cache_manager.redis_client.setex.return_value = True
        
        validator = AgriculturalDataValidator()
        pipeline = DataIngestionPipeline(cache_manager, validator)
        orchestrator = ETLOrchestrator(pipeline)
        
        return {
            "cache_manager": cache_manager,
            "validator": validator,
            "pipeline": pipeline,
            "orchestrator": orchestrator
        }
    
    @pytest.mark.asyncio
    async def test_end_to_end_weather_ingestion(self, integration_setup):
        """Test end-to-end weather data ingestion."""
        pipeline = integration_setup["pipeline"]
        
        # Register weather source
        config = DataSourceConfig(
            name="weather_test",
            source_type=DataSourceType.WEATHER,
            base_url="https://test.weather.api",
            quality_threshold=0.7
        )
        
        async def weather_handler(operation, **params):
            return {
                "temperature_f": 75.0,
                "humidity_percent": 65.0,
                "precipitation_inches": 0.0,
                "wind_speed_mph": 8.0,
                "conditions": "clear",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        pipeline.register_data_source(config, weather_handler)
        
        # Test ingestion
        result = await pipeline.ingest_data(
            "weather_test", 
            "current_weather",
            latitude=42.0,
            longitude=-93.6
        )
        
        assert result.success
        assert result.quality_score >= 0.7
        assert "temperature_f" in result.data
        assert result.data["temperature_f"] == 75.0
    
    @pytest.mark.asyncio
    async def test_etl_job_execution_flow(self, integration_setup):
        """Test complete ETL job execution flow."""
        pipeline = integration_setup["pipeline"]
        orchestrator = integration_setup["orchestrator"]
        
        # Register data source
        config = DataSourceConfig(
            name="test_etl_source",
            source_type=DataSourceType.MARKET,
            base_url="internal",
            quality_threshold=0.8
        )
        
        async def market_handler(operation, **params):
            return {
                "corn_price": 4.25,
                "soybean_price": 12.80,
                "last_updated": datetime.utcnow().isoformat()
            }
        
        pipeline.register_data_source(config, market_handler)
        
        # Register ETL job
        job_config = ETLJobConfig(
            job_id="market_refresh_test",
            name="Market Refresh Test",
            description="Test market data refresh",
            source_name="test_etl_source",
            operation="prices",
            parameters={},
            priority=JobPriority.MEDIUM,
            enabled=True
        )
        
        orchestrator.register_job(job_config)
        
        # Mock scheduler
        orchestrator.scheduler = MagicMock()
        orchestrator.scheduler.running = False
        
        # Execute job
        job_run = await orchestrator.run_job_now("market_refresh_test")
        
        assert job_run.status == JobStatus.SUCCESS
        assert job_run.ingestion_result.success
        assert "corn_price" in job_run.ingestion_result.data