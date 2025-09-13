"""
Integration Test for Data Validation and Cleaning Pipeline

Tests the integration of the enhanced validation pipeline with the
existing data ingestion framework.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from src.services.data_ingestion_framework import (
    DataIngestionPipeline,
    CacheManager,
    AgriculturalDataValidator,
    DataSourceConfig,
    DataSourceType
)
from src.services.data_validation_pipeline import DataValidationPipeline


class TestValidationIntegration:
    """Test integration of validation pipeline with ingestion framework."""
    
    @pytest.fixture
    def mock_cache_manager(self):
        cache = AsyncMock(spec=CacheManager)
        cache.get.return_value = None  # Default to cache miss
        cache.set.return_value = True
        cache.generate_cache_key.return_value = "test_cache_key"
        return cache
    
    @pytest.fixture
    def mock_validator(self):
        from src.services.data_ingestion_framework import ValidationResult
        validator = AsyncMock(spec=AgriculturalDataValidator)
        
        def validate_side_effect(data, source_config):
            # Return the input data as normalized data (pass-through)
            return ValidationResult(
                is_valid=True,
                errors=[],
                warnings=[],
                quality_score=0.9,
                normalized_data=data
            )
        
        validator.validate.side_effect = validate_side_effect
        return validator
    
    @pytest.fixture
    def enhanced_validator(self):
        return DataValidationPipeline()
    
    @pytest.fixture
    def integrated_pipeline(self, mock_cache_manager, mock_validator, enhanced_validator):
        return DataIngestionPipeline(mock_cache_manager, mock_validator, enhanced_validator)
    
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
    async def test_weather_data_integration(self, integrated_pipeline, weather_config):
        """Test weather data ingestion with enhanced validation."""
        
        # Mock weather handler that returns data with issues
        async def weather_handler(operation, **params):
            return {
                "temperature_f": "75.5",  # String that needs conversion
                "humidity_percent": 105.0,  # Invalid > 100%
                "precipitation_inches": -0.1,  # Invalid negative
                "wind_speed_mph": 8.0,
                "conditions": "clear",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        integrated_pipeline.register_data_source(weather_config, weather_handler)
        
        # Ingest data
        result = await integrated_pipeline.ingest_data(
            "test_weather", 
            "current_weather",
            latitude=42.0,
            longitude=-93.6
        )
        
        # Verify successful ingestion
        assert result.success
        assert result.source_name == "test_weather"
        
        # Verify data cleaning occurred
        cleaned_data = result.data
        assert cleaned_data["temperature_f"] == 75.5  # Converted from string
        assert cleaned_data["humidity_percent"] == 100.0  # Corrected from 105%
        assert cleaned_data["precipitation_inches"] == 0.0  # Corrected from negative
        
        # Verify metadata includes validation info
        assert "_validation_metadata" in cleaned_data
        assert cleaned_data["_validation_metadata"]["enhanced_cleaning"] is True
        assert cleaned_data["_validation_metadata"]["source_type"] == "weather"
        
        # Verify quality score reflects cleaning
        assert 0.7 <= result.quality_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_soil_data_integration(self, integrated_pipeline, soil_config):
        """Test soil data ingestion with enhanced validation."""
        
        # Mock soil handler that returns data with issues
        async def soil_handler(operation, **params):
            return {
                "ph": "6.2",  # String that needs conversion
                "organic_matter_percent": "1.8%",  # String with % sign, low value
                "phosphorus_ppm": -5.0,  # Invalid negative
                "potassium_ppm": 95.0,  # Low value
                "soil_texture": "sandy loam",  # Needs normalization
                "test_date": "2024-03-15"
            }
        
        integrated_pipeline.register_data_source(soil_config, soil_handler)
        
        # Ingest data
        result = await integrated_pipeline.ingest_data(
            "test_soil",
            "soil_characteristics",
            latitude=42.0,
            longitude=-93.6
        )
        
        # Verify successful ingestion
        assert result.success
        assert result.source_name == "test_soil"
        
        # Verify data cleaning occurred
        cleaned_data = result.data
        assert cleaned_data["ph"] == 6.2  # Converted from string
        assert cleaned_data["organic_matter_percent"] == 1.8  # Converted, % removed
        assert cleaned_data["phosphorus_ppm"] == 0.0  # Corrected from negative
        assert cleaned_data["soil_texture"] == "sandy_loam"  # Normalized
        
        # Verify metadata includes validation info
        assert "_validation_metadata" in cleaned_data
        assert cleaned_data["_validation_metadata"]["enhanced_cleaning"] is True
        assert cleaned_data["_validation_metadata"]["source_type"] == "soil"
    
    @pytest.mark.asyncio
    async def test_metrics_include_cleaning_actions(self, integrated_pipeline, weather_config):
        """Test that metrics include cleaning action counts."""
        
        # Mock handler with data that needs cleaning
        async def handler_with_issues(operation, **params):
            return {
                "temperature_f": "75.0",  # String conversion needed
                "humidity_percent": 110.0,  # Correction needed
                "precipitation_inches": -0.5  # Correction needed
            }
        
        integrated_pipeline.register_data_source(weather_config, handler_with_issues)
        
        # Perform multiple ingestions
        for _ in range(3):
            await integrated_pipeline.ingest_data("test_weather", "current_weather")
        
        # Check metrics
        metrics = integrated_pipeline.get_metrics()
        
        assert "cleaning_actions" in metrics
        assert metrics["cleaning_actions"] > 0  # Should have performed cleaning actions
        assert "enhanced_validation_metrics" in metrics
        assert metrics["enhanced_validation_metrics"]["total_validations"] == 3
    
    @pytest.mark.asyncio
    async def test_fallback_when_enhanced_validation_fails(self, integrated_pipeline, weather_config, mock_validator):
        """Test fallback to basic validation when enhanced validation fails."""
        
        # Mock enhanced validator to fail
        integrated_pipeline.enhanced_validator = AsyncMock()
        integrated_pipeline.enhanced_validator.validate_and_clean.side_effect = Exception("Enhanced validation failed")
        
        # Mock handler
        async def weather_handler(operation, **params):
            return {"temperature_f": 75.0, "humidity_percent": 65.0}
        
        integrated_pipeline.register_data_source(weather_config, weather_handler)
        
        # Ingest data
        result = await integrated_pipeline.ingest_data("test_weather", "current_weather")
        
        # Should still succeed with basic validation
        assert result.success
        assert result.data["temperature_f"] == 75.0
        
        # Metadata should indicate enhanced cleaning was attempted but failed
        assert result.data["_validation_metadata"]["enhanced_cleaning"] is False
    
    @pytest.mark.asyncio
    async def test_unsupported_data_type_uses_basic_validation(self, integrated_pipeline):
        """Test that unsupported data types use only basic validation."""
        
        # Create config for unsupported data type
        unsupported_config = DataSourceConfig(
            name="test_unsupported",
            source_type=DataSourceType.SATELLITE,  # Not supported by enhanced validator
            base_url="https://test.api",
            quality_threshold=0.8
        )
        
        async def handler(operation, **params):
            return {"satellite_data": "test_value"}
        
        integrated_pipeline.register_data_source(unsupported_config, handler)
        
        # Ingest data
        result = await integrated_pipeline.ingest_data("test_unsupported", "get_data")
        
        # Should succeed with basic validation only
        assert result.success
        assert result.data["satellite_data"] == "test_value"
        
        # Metadata should indicate no enhanced cleaning
        assert result.data["_validation_metadata"]["enhanced_cleaning"] is False
    
    @pytest.mark.asyncio
    async def test_batch_ingestion_with_validation(self, integrated_pipeline, weather_config, soil_config):
        """Test batch ingestion with enhanced validation."""
        
        # Register handlers
        async def weather_handler(operation, **params):
            return {"temperature_f": "75.0", "humidity_percent": 65.0}
        
        async def soil_handler(operation, **params):
            return {"ph": "6.5", "organic_matter_percent": 3.0}
        
        integrated_pipeline.register_data_source(weather_config, weather_handler)
        integrated_pipeline.register_data_source(soil_config, soil_handler)
        
        # Batch requests
        requests = [
            {"source_name": "test_weather", "operation": "current_weather", "params": {}},
            {"source_name": "test_soil", "operation": "soil_test", "params": {}},
            {"source_name": "test_weather", "operation": "forecast", "params": {}}
        ]
        
        # Perform batch ingestion
        results = await integrated_pipeline.batch_ingest(requests)
        
        # Verify all succeeded
        assert len(results) == 3
        assert all(result.success for result in results)
        
        # Verify enhanced validation was applied
        for result in results:
            assert "_validation_metadata" in result.data
            if result.source_name in ["test_weather", "test_soil"]:
                assert result.data["_validation_metadata"]["enhanced_cleaning"] is True
    
    @pytest.mark.asyncio
    async def test_cache_includes_validation_metadata(self, integrated_pipeline, weather_config):
        """Test that cached data includes validation metadata."""
        
        # Mock cache to return data with validation metadata
        cached_data = {
            "temperature_f": 75.0,
            "humidity_percent": 65.0,
            "_quality_score": 0.9,
            "_validation_metadata": {
                "basic_validation": True,
                "enhanced_cleaning": True,
                "source_type": "weather"
            }
        }
        
        integrated_pipeline.cache_manager.get.return_value = cached_data
        
        async def weather_handler(operation, **params):
            return {"temperature_f": 75.0}
        
        integrated_pipeline.register_data_source(weather_config, weather_handler)
        
        # Ingest data (should hit cache)
        result = await integrated_pipeline.ingest_data("test_weather", "current_weather")
        
        # Verify cache hit with validation metadata
        assert result.success
        assert result.cache_hit
        assert "_validation_metadata" in result.data
        assert result.data["_validation_metadata"]["enhanced_cleaning"] is True


@pytest.mark.integration
class TestEndToEndValidationWorkflow:
    """End-to-end tests for the complete validation workflow."""
    
    @pytest.mark.asyncio
    async def test_complete_weather_workflow(self):
        """Test complete weather data workflow with real components."""
        
        # Create real components
        cache_manager = CacheManager("redis://localhost:6379")
        cache_manager.redis_client = AsyncMock()  # Mock Redis for testing
        cache_manager.redis_client.ping.return_value = True
        cache_manager.redis_client.get.return_value = None
        cache_manager.redis_client.setex.return_value = True
        
        basic_validator = AgriculturalDataValidator()
        enhanced_validator = DataValidationPipeline()
        pipeline = DataIngestionPipeline(cache_manager, basic_validator, enhanced_validator)
        
        # Register weather source
        weather_config = DataSourceConfig(
            name="integration_weather",
            source_type=DataSourceType.WEATHER,
            base_url="https://test.api",
            quality_threshold=0.7
        )
        
        async def realistic_weather_handler(operation, **params):
            """Simulate realistic weather data with various issues."""
            return {
                "temperature_f": "78.5",  # String conversion needed
                "humidity_percent": 102.0,  # Needs correction
                "precipitation_inches": 0.0,
                "wind_speed_mph": 12.0,
                "conditions": "partly cloudy",
                "timestamp": datetime.utcnow().isoformat(),
                "pressure_mb": 1013.25,
                "visibility_miles": 10.0
            }
        
        pipeline.register_data_source(weather_config, realistic_weather_handler)
        
        # Ingest data
        result = await pipeline.ingest_data(
            "integration_weather",
            "current_weather",
            latitude=42.0308,
            longitude=-93.6319
        )
        
        # Verify complete workflow
        assert result.success
        assert result.quality_score > 0.7
        
        # Verify data transformations
        assert result.data["temperature_f"] == 78.5  # Converted from string
        assert result.data["humidity_percent"] == 100.0  # Corrected from 102%
        
        # Verify metadata
        assert "_validation_metadata" in result.data
        assert result.data["_validation_metadata"]["basic_validation"] is True
        assert result.data["_validation_metadata"]["enhanced_cleaning"] is True
        
        # Verify metrics
        metrics = pipeline.get_metrics()
        assert metrics["total_requests"] == 1
        assert metrics["successful_requests"] == 1
        assert metrics["cleaning_actions"] > 0
        assert metrics["enhanced_validation_metrics"]["total_validations"] == 1
    
    @pytest.mark.asyncio
    async def test_complete_soil_workflow(self):
        """Test complete soil data workflow with real components."""
        
        # Create real components
        cache_manager = CacheManager("redis://localhost:6379")
        cache_manager.redis_client = AsyncMock()  # Mock Redis for testing
        cache_manager.redis_client.ping.return_value = True
        cache_manager.redis_client.get.return_value = None
        cache_manager.redis_client.setex.return_value = True
        
        basic_validator = AgriculturalDataValidator()
        enhanced_validator = DataValidationPipeline()
        pipeline = DataIngestionPipeline(cache_manager, basic_validator, enhanced_validator)
        
        # Register soil source
        soil_config = DataSourceConfig(
            name="integration_soil",
            source_type=DataSourceType.SOIL,
            base_url="https://test.api",
            quality_threshold=0.8
        )
        
        async def realistic_soil_handler(operation, **params):
            """Simulate realistic soil data with various issues."""
            return {
                "ph": "6.3",  # String conversion needed
                "organic_matter_percent": "2.1%",  # String with % sign
                "phosphorus_ppm": 18.0,  # Low but valid
                "potassium_ppm": 145.0,  # Low but valid
                "soil_texture": "silt loam",  # Needs normalization
                "drainage_class": "well drained",  # Needs normalization
                "cec_meq_per_100g": 22.5,
                "test_date": "2024-02-15",
                "lab_name": "Iowa State Soil Testing Lab"
            }
        
        pipeline.register_data_source(soil_config, realistic_soil_handler)
        
        # Ingest data
        result = await pipeline.ingest_data(
            "integration_soil",
            "soil_characteristics",
            latitude=42.0308,
            longitude=-93.6319
        )
        
        # Verify complete workflow
        assert result.success
        assert result.quality_score > 0.8
        
        # Verify data transformations
        assert result.data["ph"] == 6.3  # Converted from string
        assert result.data["organic_matter_percent"] == 2.1  # Converted, % removed
        assert result.data["soil_texture"] == "silt_loam"  # Normalized
        assert result.data["drainage_class"] == "well_drained"  # Normalized
        
        # Verify metadata
        assert "_validation_metadata" in result.data
        assert result.data["_validation_metadata"]["basic_validation"] is True
        assert result.data["_validation_metadata"]["enhanced_cleaning"] is True
        
        # Verify metrics
        metrics = pipeline.get_metrics()
        assert metrics["total_requests"] == 1
        assert metrics["successful_requests"] == 1
        assert metrics["enhanced_validation_metrics"]["total_validations"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])