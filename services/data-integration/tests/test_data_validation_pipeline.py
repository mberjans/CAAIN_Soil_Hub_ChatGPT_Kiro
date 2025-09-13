"""
Tests for Data Validation and Cleaning Pipeline

Comprehensive tests for agricultural data validation, cleaning,
and quality assurance with domain-specific validation rules.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import json

from src.services.data_validation_pipeline import (
    DataValidationPipeline,
    WeatherDataCleaner,
    SoilDataCleaner,
    ValidationSeverity,
    CleaningAction,
    ValidationIssue,
    CleaningResult
)


class TestWeatherDataCleaner:
    """Test the weather data cleaner."""
    
    @pytest.fixture
    def weather_cleaner(self):
        return WeatherDataCleaner()
    
    @pytest.mark.asyncio
    async def test_clean_valid_weather_data(self, weather_cleaner):
        """Test cleaning of valid weather data."""
        weather_data = {
            "temperature_f": 75.0,
            "humidity_percent": 65.0,
            "precipitation_inches": 0.1,
            "wind_speed_mph": 8.0,
            "conditions": "partly cloudy",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        result = await weather_cleaner.clean_data(weather_data)
        
        assert result.quality_score >= 0.8
        assert len(result.issues_found) == 0
        assert result.cleaned_data == weather_data
        assert result.cleaning_confidence == 1.0
    
    @pytest.mark.asyncio
    async def test_clean_temperature_conversion(self, weather_cleaner):
        """Test temperature type conversion and validation."""
        weather_data = {
            "temperature_f": "75.5",  # String temperature
            "humidity_percent": 65.0
        }
        
        result = await weather_cleaner.clean_data(weather_data)
        
        assert result.cleaned_data["temperature_f"] == 75.5
        assert "Converted temperature_f from string to float" in result.actions_taken
        assert result.quality_score > 0.8
    
    @pytest.mark.asyncio
    async def test_clean_extreme_temperature(self, weather_cleaner):
        """Test handling of extreme temperature values."""
        weather_data = {
            "temperature_f": 200.0,  # Extreme temperature
            "humidity_percent": 65.0
        }
        
        result = await weather_cleaner.clean_data(weather_data)
        
        # Extreme temperature should be removed
        assert "temperature_f" not in result.cleaned_data
        assert any(issue.severity == ValidationSeverity.CRITICAL for issue in result.issues_found)
        assert any("extreme temperature" in action.lower() for action in result.actions_taken)
    
    @pytest.mark.asyncio
    async def test_clean_humidity_validation(self, weather_cleaner):
        """Test humidity validation and correction."""
        weather_data = {
            "temperature_f": 75.0,
            "humidity_percent": 105.0  # Invalid humidity > 100%
        }
        
        result = await weather_cleaner.clean_data(weather_data)
        
        # Humidity should be corrected to 100%
        assert result.cleaned_data["humidity_percent"] == 100.0
        assert any(issue.cleaning_action == CleaningAction.CORRECT for issue in result.issues_found)
        assert "Corrected humidity from 105.0% to 100%" in result.actions_taken
    
    @pytest.mark.asyncio
    async def test_clean_negative_precipitation(self, weather_cleaner):
        """Test handling of negative precipitation."""
        weather_data = {
            "temperature_f": 75.0,
            "precipitation_inches": -0.5  # Invalid negative precipitation
        }
        
        result = await weather_cleaner.clean_data(weather_data)
        
        # Negative precipitation should be corrected to 0
        assert result.cleaned_data["precipitation_inches"] == 0.0
        assert any(issue.severity == ValidationSeverity.ERROR for issue in result.issues_found)
        assert "Corrected negative precipitation to 0" in result.actions_taken
    
    @pytest.mark.asyncio
    async def test_clean_wind_speed_validation(self, weather_cleaner):
        """Test wind speed validation."""
        weather_data = {
            "temperature_f": 75.0,
            "wind_speed_mph": 30.0  # High wind speed
        }
        
        result = await weather_cleaner.clean_data(weather_data)
        
        # High wind speed should generate warning
        wind_issues = [issue for issue in result.issues_found if "wind" in issue.field_name.lower()]
        assert len(wind_issues) > 0
        assert any(issue.severity == ValidationSeverity.WARNING for issue in wind_issues)
        assert any("crop" in issue.agricultural_context.lower() for issue in wind_issues)
    
    @pytest.mark.asyncio
    async def test_clean_timestamp_parsing(self, weather_cleaner):
        """Test timestamp parsing and validation."""
        weather_data = {
            "temperature_f": 75.0,
            "timestamp": "2024-12-09T10:30:00Z"
        }
        
        result = await weather_cleaner.clean_data(weather_data)
        
        # Timestamp should be normalized
        assert "timestamp" in result.cleaned_data
        assert "Normalized timestamp format" in result.actions_taken
    
    @pytest.mark.asyncio
    async def test_clean_old_weather_data(self, weather_cleaner):
        """Test handling of old weather data."""
        old_timestamp = (datetime.utcnow() - timedelta(hours=50)).isoformat()
        weather_data = {
            "temperature_f": 75.0,
            "timestamp": old_timestamp
        }
        
        result = await weather_cleaner.clean_data(weather_data)
        
        # Old data should generate warning
        timestamp_issues = [issue for issue in result.issues_found if "timestamp" in issue.field_name.lower()]
        assert len(timestamp_issues) > 0
        assert any("hours old" in issue.message for issue in timestamp_issues)
    
    @pytest.mark.asyncio
    async def test_weather_quality_score_calculation(self, weather_cleaner):
        """Test weather data quality score calculation."""
        # Complete, valid data should have high quality score
        complete_data = {
            "temperature_f": 75.0,
            "humidity_percent": 65.0,
            "precipitation_inches": 0.1,
            "wind_speed_mph": 8.0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        result = await weather_cleaner.clean_data(complete_data)
        assert result.quality_score >= 0.9
        
        # Incomplete data should have lower quality score
        incomplete_data = {
            "temperature_f": 75.0
        }
        
        result = await weather_cleaner.clean_data(incomplete_data)
        assert result.quality_score < 0.9


class TestSoilDataCleaner:
    """Test the soil data cleaner."""
    
    @pytest.fixture
    def soil_cleaner(self):
        return SoilDataCleaner()
    
    @pytest.mark.asyncio
    async def test_clean_valid_soil_data(self, soil_cleaner):
        """Test cleaning of valid soil data."""
        soil_data = {
            "ph": 6.5,
            "organic_matter_percent": 3.2,
            "phosphorus_ppm": 25.0,
            "potassium_ppm": 180.0,
            "soil_texture": "silt_loam",
            "drainage_class": "well_drained",
            "test_date": "2024-03-15"
        }
        
        result = await soil_cleaner.clean_data(soil_data)
        
        assert result.quality_score >= 0.8
        assert len([issue for issue in result.issues_found if issue.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR]]) == 0
        assert result.cleaning_confidence >= 0.8
    
    @pytest.mark.asyncio
    async def test_clean_ph_validation(self, soil_cleaner):
        """Test pH validation and correction."""
        # Test extreme pH values
        extreme_ph_data = {
            "ph": 15.0,  # Impossible pH
            "organic_matter_percent": 3.0
        }
        
        result = await soil_cleaner.clean_data(extreme_ph_data)
        
        # Extreme pH should be removed
        assert "ph" not in result.cleaned_data
        assert any(issue.severity == ValidationSeverity.CRITICAL for issue in result.issues_found)
        
        # Test acidic pH
        acidic_ph_data = {
            "ph": 4.5,  # Very acidic
            "organic_matter_percent": 3.0
        }
        
        result = await soil_cleaner.clean_data(acidic_ph_data)
        
        # Acidic pH should generate warning with agricultural advice
        ph_issues = [issue for issue in result.issues_found if issue.field_name == "ph"]
        assert len(ph_issues) > 0
        assert any("lime" in issue.agricultural_context.lower() for issue in ph_issues)
    
    @pytest.mark.asyncio
    async def test_clean_organic_matter_validation(self, soil_cleaner):
        """Test organic matter validation."""
        # Test negative organic matter
        negative_om_data = {
            "ph": 6.5,
            "organic_matter_percent": -2.0  # Invalid negative value
        }
        
        result = await soil_cleaner.clean_data(negative_om_data)
        
        # Negative OM should be corrected to 0
        assert result.cleaned_data["organic_matter_percent"] == 0.0
        assert any(issue.cleaning_action == CleaningAction.CORRECT for issue in result.issues_found)
        
        # Test low organic matter
        low_om_data = {
            "ph": 6.5,
            "organic_matter_percent": 1.5  # Low organic matter
        }
        
        result = await soil_cleaner.clean_data(low_om_data)
        
        # Low OM should generate warning with agricultural advice
        om_issues = [issue for issue in result.issues_found if "organic_matter" in issue.field_name]
        assert len(om_issues) > 0
        assert any("cover crops" in issue.agricultural_context.lower() for issue in om_issues)
    
    @pytest.mark.asyncio
    async def test_clean_nutrient_validation(self, soil_cleaner):
        """Test nutrient level validation."""
        # Test negative nutrients
        negative_nutrient_data = {
            "ph": 6.5,
            "phosphorus_ppm": -5.0,  # Invalid negative
            "potassium_ppm": 150.0
        }
        
        result = await soil_cleaner.clean_data(negative_nutrient_data)
        
        # Negative phosphorus should be corrected to 0
        assert result.cleaned_data["phosphorus_ppm"] == 0.0
        assert "Corrected negative phosphorus_ppm to 0" in result.actions_taken
        
        # Test low nutrients
        low_nutrient_data = {
            "ph": 6.5,
            "phosphorus_ppm": 8.0,  # Low phosphorus
            "potassium_ppm": 100.0  # Low potassium
        }
        
        result = await soil_cleaner.clean_data(low_nutrient_data)
        
        # Low nutrients should generate warnings with fertilizer advice
        nutrient_issues = [issue for issue in result.issues_found if "ppm" in issue.field_name]
        assert len(nutrient_issues) >= 2
        assert any("fertilizer" in issue.agricultural_context.lower() for issue in nutrient_issues)
    
    @pytest.mark.asyncio
    async def test_clean_soil_texture_normalization(self, soil_cleaner):
        """Test soil texture normalization."""
        texture_data = {
            "ph": 6.5,
            "soil_texture": "sandy loam"  # Space in texture name
        }
        
        result = await soil_cleaner.clean_data(texture_data)
        
        # Texture should be normalized
        assert result.cleaned_data["soil_texture"] == "sandy_loam"
        assert any("Normalized soil texture" in action for action in result.actions_taken)
    
    @pytest.mark.asyncio
    async def test_clean_test_date_validation(self, soil_cleaner):
        """Test soil test date validation."""
        # Test old soil test
        old_date = (datetime.utcnow() - timedelta(days=1200)).isoformat()  # Over 3 years old
        old_test_data = {
            "ph": 6.5,
            "test_date": old_date
        }
        
        result = await soil_cleaner.clean_data(old_test_data)
        
        # Old test should generate warning
        date_issues = [issue for issue in result.issues_found if "test_date" in issue.field_name]
        assert len(date_issues) > 0
        assert any("old" in issue.message.lower() for issue in date_issues)
        assert any("current conditions" in issue.agricultural_context.lower() for issue in date_issues)
    
    @pytest.mark.asyncio
    async def test_clean_ph_range_validation(self, soil_cleaner):
        """Test pH range validation and correction."""
        ph_range_data = {
            "ph": 6.5,
            "typical_ph_range": {
                "min": 7.0,  # Min > Max (incorrect)
                "max": 6.0
            }
        }
        
        result = await soil_cleaner.clean_data(ph_range_data)
        
        # pH range should be corrected
        corrected_range = result.cleaned_data["typical_ph_range"]
        assert corrected_range["min"] == 6.0
        assert corrected_range["max"] == 7.0
        assert "Corrected pH range order" in result.actions_taken
    
    @pytest.mark.asyncio
    async def test_soil_quality_score_calculation(self, soil_cleaner):
        """Test soil data quality score calculation."""
        # Complete, valid data should have high quality score
        complete_data = {
            "ph": 6.5,
            "organic_matter_percent": 3.2,
            "phosphorus_ppm": 25.0,
            "potassium_ppm": 180.0,
            "soil_texture": "silt_loam",
            "test_date": "2024-03-15"
        }
        
        result = await soil_cleaner.clean_data(complete_data)
        assert result.quality_score >= 0.9
        
        # Data with critical issues should have low quality score
        critical_issue_data = {
            "ph": 20.0,  # Impossible pH
            "organic_matter_percent": 3.0
        }
        
        result = await soil_cleaner.clean_data(critical_issue_data)
        assert result.quality_score < 0.7


class TestDataValidationPipeline:
    """Test the main data validation pipeline."""
    
    @pytest.fixture
    def validation_pipeline(self):
        return DataValidationPipeline()
    
    @pytest.mark.asyncio
    async def test_validate_weather_data(self, validation_pipeline):
        """Test weather data validation through pipeline."""
        weather_data = {
            "temperature_f": 75.0,
            "humidity_percent": 65.0,
            "precipitation_inches": 0.1
        }
        
        result = await validation_pipeline.validate_and_clean(weather_data, "weather")
        
        assert isinstance(result, CleaningResult)
        assert result.quality_score > 0.0
        assert result.metadata["cleaner_type"] == "weather"
    
    @pytest.mark.asyncio
    async def test_validate_soil_data(self, validation_pipeline):
        """Test soil data validation through pipeline."""
        soil_data = {
            "ph": 6.5,
            "organic_matter_percent": 3.2,
            "phosphorus_ppm": 25.0
        }
        
        result = await validation_pipeline.validate_and_clean(soil_data, "soil")
        
        assert isinstance(result, CleaningResult)
        assert result.quality_score > 0.0
        assert result.metadata["cleaner_type"] == "soil"
    
    @pytest.mark.asyncio
    async def test_validate_with_context(self, validation_pipeline):
        """Test validation with agricultural context."""
        weather_data = {
            "temperature_f": 75.0,
            "humidity_percent": 65.0
        }
        
        context = {
            "agricultural_context": "corn_growing_season",
            "season": "summer",
            "date": "2024-07-15"
        }
        
        result = await validation_pipeline.validate_and_clean(weather_data, "weather", context)
        
        assert result.metadata["agricultural_context"] == "corn_growing_season"
        assert result.metadata["season"] == "summer"
    
    @pytest.mark.asyncio
    async def test_invalid_data_type(self, validation_pipeline):
        """Test handling of invalid data type."""
        with pytest.raises(ValueError, match="No cleaner available for data type"):
            await validation_pipeline.validate_and_clean({}, "invalid_type")
    
    def test_validation_metrics_tracking(self, validation_pipeline):
        """Test validation metrics tracking."""
        # Initially no metrics
        metrics = validation_pipeline.get_validation_metrics()
        assert metrics["total_validations"] == 0
        
        # Add some validation history manually for testing
        validation_pipeline.validation_history = [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "data_type": "weather",
                "quality_score": 0.9,
                "issues_count": 1,
                "actions_count": 2
            },
            {
                "timestamp": datetime.utcnow().isoformat(),
                "data_type": "soil",
                "quality_score": 0.8,
                "issues_count": 2,
                "actions_count": 1
            }
        ]
        
        metrics = validation_pipeline.get_validation_metrics()
        
        assert metrics["total_validations"] == 2
        assert metrics["average_quality_score"] == 0.85
        assert "weather" in metrics["data_types"]
        assert "soil" in metrics["data_types"]
        assert metrics["data_types"]["weather"]["count"] == 1
        assert metrics["data_types"]["soil"]["count"] == 1
    
    def test_register_custom_cleaner(self, validation_pipeline):
        """Test registering custom data cleaner."""
        # Create mock cleaner
        mock_cleaner = AsyncMock()
        mock_cleaner.clean_data.return_value = CleaningResult(
            original_data={},
            cleaned_data={},
            issues_found=[],
            actions_taken=[],
            quality_score=1.0,
            cleaning_confidence=1.0
        )
        
        validation_pipeline.register_cleaner("custom_type", mock_cleaner)
        
        assert "custom_type" in validation_pipeline.cleaners
        assert validation_pipeline.cleaners["custom_type"] == mock_cleaner
    
    @pytest.mark.asyncio
    async def test_health_check(self, validation_pipeline):
        """Test pipeline health check."""
        health = await validation_pipeline.health_check()
        
        assert health["status"] in ["healthy", "degraded"]
        assert "registered_cleaners" in health
        assert "weather" in health["registered_cleaners"]
        assert "soil" in health["registered_cleaners"]
        assert "test_results" in health


@pytest.mark.integration
class TestValidationPipelineIntegration:
    """Integration tests for the validation pipeline."""
    
    @pytest.fixture
    def pipeline(self):
        return DataValidationPipeline()
    
    @pytest.mark.asyncio
    async def test_end_to_end_weather_validation(self, pipeline):
        """Test complete weather data validation workflow."""
        # Realistic weather data with various issues
        weather_data = {
            "temperature_f": "75.5",  # String that needs conversion
            "humidity_percent": 105.0,  # Invalid > 100%
            "precipitation_inches": -0.1,  # Invalid negative
            "wind_speed_mph": 35.0,  # High wind speed
            "conditions": "thunderstorm",
            "timestamp": "2024-12-09T10:30:00Z"
        }
        
        result = await pipeline.validate_and_clean(weather_data, "weather")
        
        # Check that issues were found and corrected
        assert len(result.issues_found) > 0
        assert len(result.actions_taken) > 0
        
        # Check specific corrections
        assert result.cleaned_data["temperature_f"] == 75.5  # Converted from string
        assert result.cleaned_data["humidity_percent"] == 100.0  # Corrected from 105%
        assert result.cleaned_data["precipitation_inches"] == 0.0  # Corrected from negative
        
        # Check agricultural context in issues
        wind_issues = [issue for issue in result.issues_found if "wind" in issue.field_name.lower()]
        assert len(wind_issues) > 0
        assert any("crop" in issue.agricultural_context.lower() for issue in wind_issues)
        
        # Quality score should reflect the corrections made
        assert 0.5 <= result.quality_score <= 0.9  # Some issues but correctable
    
    @pytest.mark.asyncio
    async def test_end_to_end_soil_validation(self, pipeline):
        """Test complete soil data validation workflow."""
        # Realistic soil data with various issues
        soil_data = {
            "ph": "6.2",  # String that needs conversion
            "organic_matter_percent": "1.8%",  # String with % sign, low value
            "phosphorus_ppm": -5.0,  # Invalid negative
            "potassium_ppm": 95.0,  # Low value
            "soil_texture": "sandy loam",  # Needs normalization
            "drainage_class": "well drained",  # Needs normalization
            "test_date": "2021-03-15",  # Old test date
            "lab_name": "Test Lab <script>alert('xss')</script>"  # Security issue
        }
        
        result = await pipeline.validate_and_clean(soil_data, "soil")
        
        # Check that issues were found and corrected
        assert len(result.issues_found) > 0
        assert len(result.actions_taken) > 0
        
        # Check specific corrections
        assert result.cleaned_data["ph"] == 6.2  # Converted from string
        assert result.cleaned_data["organic_matter_percent"] == 1.8  # Converted, % removed
        assert result.cleaned_data["phosphorus_ppm"] == 0.0  # Corrected from negative
        assert result.cleaned_data["soil_texture"] == "sandy_loam"  # Normalized
        assert result.cleaned_data["drainage_class"] == "well_drained"  # Normalized
        
        # Check security cleaning
        assert "<script>" not in result.cleaned_data["lab_name"]
        
        # Check agricultural context in issues
        nutrient_issues = [issue for issue in result.issues_found if "ppm" in issue.field_name]
        assert len(nutrient_issues) > 0
        assert any("fertilizer" in issue.agricultural_context.lower() for issue in nutrient_issues)
        
        om_issues = [issue for issue in result.issues_found if "organic_matter" in issue.field_name]
        assert len(om_issues) > 0
        assert any("cover crops" in issue.agricultural_context.lower() for issue in om_issues)
    
    @pytest.mark.asyncio
    async def test_validation_metrics_accumulation(self, pipeline):
        """Test that validation metrics accumulate correctly."""
        # Perform multiple validations
        weather_data = {"temperature_f": 75.0, "humidity_percent": 65.0}
        soil_data = {"ph": 6.5, "organic_matter_percent": 3.0}
        
        await pipeline.validate_and_clean(weather_data, "weather")
        await pipeline.validate_and_clean(soil_data, "soil")
        await pipeline.validate_and_clean(weather_data, "weather")
        
        metrics = pipeline.get_validation_metrics()
        
        assert metrics["total_validations"] == 3
        assert metrics["data_types"]["weather"]["count"] == 2
        assert metrics["data_types"]["soil"]["count"] == 1
        assert len(metrics["recent_validations"]) == 3
    
    @pytest.mark.asyncio
    async def test_agricultural_context_integration(self, pipeline):
        """Test integration with agricultural context."""
        # Test with growing season context
        weather_data = {
            "temperature_f": 95.0,  # High temperature
            "humidity_percent": 30.0,  # Low humidity
            "precipitation_inches": 0.0
        }
        
        growing_season_context = {
            "agricultural_context": "corn_tasseling_stage",
            "season": "summer",
            "crop_type": "corn",
            "growth_stage": "R1"
        }
        
        result = await pipeline.validate_and_clean(weather_data, "weather", growing_season_context)
        
        # High temperature during tasseling should be flagged
        temp_issues = [issue for issue in result.issues_found if "temperature" in issue.field_name.lower()]
        if temp_issues:  # May or may not generate issues depending on exact thresholds
            assert any("crop" in issue.agricultural_context.lower() for issue in temp_issues)
        
        # Check context is preserved in metadata
        assert result.metadata["agricultural_context"] == "corn_tasseling_stage"
        assert result.metadata["season"] == "summer"


@pytest.mark.performance
class TestValidationPerformance:
    """Performance tests for validation pipeline."""
    
    @pytest.fixture
    def pipeline(self):
        return DataValidationPipeline()
    
    @pytest.mark.asyncio
    async def test_validation_performance(self, pipeline):
        """Test validation performance with large datasets."""
        import time
        
        # Create test data
        weather_data = {
            "temperature_f": 75.0,
            "humidity_percent": 65.0,
            "precipitation_inches": 0.1,
            "wind_speed_mph": 8.0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Time multiple validations
        start_time = time.time()
        
        tasks = []
        for _ in range(100):
            task = pipeline.validate_and_clean(weather_data.copy(), "weather")
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete 100 validations in reasonable time
        assert total_time < 5.0  # Less than 5 seconds
        assert len(results) == 100
        assert all(result.quality_score > 0.8 for result in results)
        
        # Average time per validation should be reasonable
        avg_time_per_validation = total_time / 100
        assert avg_time_per_validation < 0.05  # Less than 50ms per validation
    
    @pytest.mark.asyncio
    async def test_memory_usage_with_history(self, pipeline):
        """Test memory usage with validation history."""
        # Perform many validations to test history management
        weather_data = {"temperature_f": 75.0}
        
        for i in range(1200):  # More than the 1000 limit
            await pipeline.validate_and_clean(weather_data, "weather")
        
        # History should be limited to 1000 entries
        assert len(pipeline.validation_history) == 1000
        
        # Should still function correctly
        metrics = pipeline.get_validation_metrics()
        assert metrics["total_validations"] == 1000