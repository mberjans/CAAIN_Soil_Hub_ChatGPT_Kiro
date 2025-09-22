"""
Unit Tests for Data Integration Services

Tests weather service, soil service, and data validation components
for accuracy, reliability, and agricultural data handling.
"""

import pytest
import sys
import os
from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch, AsyncMock
import json

# Add services to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'services', 'data-integration', 'src'))

from services.weather_service import WeatherService, NOAAWeatherService, OpenWeatherMapService
from services.soil_service import SoilDataService, USDAWebSoilSurvey, SoilGridsService
from services.data_validation_pipeline import DataValidationPipeline, WeatherDataCleaner, SoilDataCleaner
from services.enhanced_cache_manager import EnhancedCacheManager


class TestWeatherService:
    """Test weather service functionality."""
    
    @pytest.fixture
    def weather_service(self):
        """Create weather service instance."""
        return WeatherService()
    
    @pytest.fixture
    def noaa_service(self):
        """Create NOAA weather service instance."""
        return NOAAWeatherService()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_current_weather_success(self, weather_service, sample_weather_data, mock_http_client):
        """Test successful weather data retrieval."""
        location = {'latitude': 42.0308, 'longitude': -93.6319}
        
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'current': {
                'temp_f': 72.5,
                'humidity': 65,
                'precip_in': 0.0,
                'wind_mph': 8.2,
                'pressure_mb': 1013.2
            }
        })
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await weather_service.get_current_weather(location)
            
            assert result is not None
            assert 'temperature_f' in result
            assert 'humidity_percent' in result
            assert result['temperature_f'] > 0
            assert 0 <= result['humidity_percent'] <= 100
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_weather_api_fallback(self, weather_service):
        """Test weather API fallback mechanism."""
        location = {'latitude': 42.0308, 'longitude': -93.6319}
        
        # Mock primary API failure
        with patch.object(weather_service, 'primary_service') as mock_primary:
            mock_primary.get_current_weather.side_effect = Exception("API Error")
            
            with patch.object(weather_service, 'fallback_service') as mock_fallback:
                mock_fallback.get_current_weather.return_value = {
                    'temperature_f': 70.0,
                    'humidity_percent': 60,
                    'source': 'fallback_api'
                }
                
                result = await weather_service.get_current_weather(location)
                
                assert result is not None
                assert result['source'] == 'fallback_api'
                mock_fallback.get_current_weather.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_weather_forecast_validation(self, weather_service):
        """Test weather forecast data validation."""
        location = {'latitude': 42.0308, 'longitude': -93.6319}
        
        mock_forecast_data = [
            {
                'date': (date.today() + timedelta(days=i)).isoformat(),
                'high_f': 75 + i,
                'low_f': 55 + i,
                'precipitation_chance': min(20 + (i * 10), 100),
                'conditions': 'partly_cloudy'
            }
            for i in range(7)
        ]
        
        with patch.object(weather_service, 'get_forecast') as mock_forecast:
            mock_forecast.return_value = mock_forecast_data
            
            result = await weather_service.get_forecast(location, days=7)
            
            assert len(result) == 7
            for day in result:
                assert 'date' in day
                assert 'high_f' in day
                assert 'low_f' in day
                assert day['high_f'] >= day['low_f']
                assert 0 <= day['precipitation_chance'] <= 100
    
    @pytest.mark.unit
    @pytest.mark.agricultural
    def test_agricultural_weather_metrics(self, weather_service, sample_weather_data):
        """Test agricultural weather metrics calculation."""
        weather_data = sample_weather_data['current']
        forecast_data = sample_weather_data['forecast']
        
        metrics = weather_service.calculate_agricultural_metrics(weather_data, forecast_data)
        
        # Validate agricultural metrics
        assert 'growing_degree_days' in metrics
        assert 'precipitation_total_7day' in metrics
        assert 'stress_indicators' in metrics
        
        # GDD should be reasonable for crop growth
        assert metrics['growing_degree_days'] >= 0
        assert metrics['precipitation_total_7day'] >= 0
        
        # Stress indicators should be boolean or numeric
        for indicator, value in metrics['stress_indicators'].items():
            assert isinstance(value, (bool, int, float))


class TestSoilDataService:
    """Test soil data service functionality."""
    
    @pytest.fixture
    def soil_service(self):
        """Create soil data service instance."""
        return SoilDataService()
    
    @pytest.fixture
    def usda_service(self):
        """Create USDA soil survey service instance."""
        return USDAWebSoilSurvey()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_soil_survey_data_success(self, soil_service):
        """Test successful soil survey data retrieval."""
        location = {'latitude': 42.0308, 'longitude': -93.6319}
        
        mock_soil_data = {
            'soil_series': 'Clarion',
            'drainage_class': 'well_drained',
            'typical_ph_range': {'min': 6.0, 'max': 7.5},
            'organic_matter_range': {'min': 2.5, 'max': 4.0},
            'texture_class': 'loam'
        }
        
        with patch.object(soil_service, 'usda_service') as mock_usda:
            mock_usda.get_soil_data.return_value = mock_soil_data
            
            result = await soil_service.get_soil_survey_data(location)
            
            assert result is not None
            assert 'soil_series' in result
            assert 'drainage_class' in result
            assert 'typical_ph_range' in result
            
            # Validate pH range is reasonable
            ph_range = result['typical_ph_range']
            assert 3.0 <= ph_range['min'] <= 10.0
            assert 3.0 <= ph_range['max'] <= 10.0
            assert ph_range['min'] <= ph_range['max']
    
    @pytest.mark.unit
    @pytest.mark.agricultural
    def test_soil_interpretation_accuracy(self, soil_service):
        """Test soil data interpretation for agricultural use."""
        raw_soil_data = {
            'mukey': '123456',
            'cokey': '789012',
            'chkey': '345678',
            'hzdept_l': 0,
            'hzdept_h': 6,
            'ph1to1h2o_l': 6.0,
            'ph1to1h2o_h': 7.0,
            'om_l': 2.5,
            'om_h': 4.0,
            'texture': 'Silt loam'
        }
        
        interpreted = soil_service.interpret_soil_data(raw_soil_data)
        
        # Should convert to agricultural-friendly format
        assert 'ph_range' in interpreted
        assert 'organic_matter_range' in interpreted
        assert 'texture_class' in interpreted
        
        # Values should be in agricultural ranges
        assert 3.0 <= interpreted['ph_range']['typical'] <= 10.0
        assert 0.0 <= interpreted['organic_matter_range']['typical'] <= 15.0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_soil_data_caching(self, soil_service, mock_redis):
        """Test soil data caching mechanism."""
        location = {'latitude': 42.0308, 'longitude': -93.6319}
        cache_key = f"soil_data:{location['latitude']:.4f}:{location['longitude']:.4f}"
        
        # Mock cache miss, then hit
        mock_redis.get.side_effect = [None, json.dumps({'cached': True, 'soil_series': 'Clarion'})]
        
        with patch.object(soil_service, 'cache', mock_redis):
            # First call - cache miss
            with patch.object(soil_service, 'usda_service') as mock_usda:
                mock_usda.get_soil_data.return_value = {'soil_series': 'Clarion'}
                
                result1 = await soil_service.get_soil_survey_data(location)
                
                # Should call external service and cache result
                mock_usda.get_soil_data.assert_called_once()
                mock_redis.set.assert_called_once()
            
            # Second call - cache hit
            result2 = await soil_service.get_soil_survey_data(location)
            
            assert result2['cached'] is True
            assert result2['soil_series'] == 'Clarion'


class TestDataValidationPipeline:
    """Test data validation pipeline functionality."""
    
    @pytest.fixture
    def validation_pipeline(self):
        """Create data validation pipeline instance."""
        return DataValidationPipeline()
    
    @pytest.fixture
    def weather_cleaner(self):
        """Create weather data cleaner instance."""
        return WeatherDataCleaner()
    
    @pytest.fixture
    def soil_cleaner(self):
        """Create soil data cleaner instance."""
        return SoilDataCleaner()
    
    @pytest.mark.unit
    def test_weather_data_validation_success(self, weather_cleaner):
        """Test successful weather data validation."""
        valid_weather_data = {
            'temperature_f': 72.5,
            'humidity_percent': 65,
            'precipitation_inches': 0.1,
            'wind_speed_mph': 8.2,
            'pressure_mb': 1013.2,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        result = weather_cleaner.validate_and_clean(valid_weather_data)
        
        assert result['is_valid'] is True
        assert result['cleaned_data']['temperature_f'] == 72.5
        assert len(result['validation_errors']) == 0
    
    @pytest.mark.unit
    def test_weather_data_validation_errors(self, weather_cleaner):
        """Test weather data validation with errors."""
        invalid_weather_data = {
            'temperature_f': 150.0,  # Too high
            'humidity_percent': 120,  # Over 100%
            'precipitation_inches': -0.5,  # Negative
            'wind_speed_mph': 'invalid',  # Wrong type
            'pressure_mb': 500  # Too low
        }
        
        result = weather_cleaner.validate_and_clean(invalid_weather_data)
        
        assert result['is_valid'] is False
        assert len(result['validation_errors']) > 0
        
        # Should identify specific errors
        error_types = [error['field'] for error in result['validation_errors']]
        assert 'temperature_f' in error_types
        assert 'humidity_percent' in error_types
        assert 'precipitation_inches' in error_types
    
    @pytest.mark.unit
    @pytest.mark.agricultural
    def test_soil_data_validation_agricultural_ranges(self, soil_cleaner, agricultural_validator):
        """Test soil data validation against agricultural ranges."""
        soil_test_data = {
            'ph': 6.2,
            'organic_matter_percent': 3.8,
            'phosphorus_ppm': 25,
            'potassium_ppm': 180,
            'test_date': date(2024, 3, 15).isoformat()
        }
        
        result = soil_cleaner.validate_and_clean(soil_test_data)
        
        assert result['is_valid'] is True
        
        # Validate against agricultural standards
        cleaned_data = result['cleaned_data']
        assert agricultural_validator.validate_soil_ph(cleaned_data['ph'])
        assert 0.0 <= cleaned_data['organic_matter_percent'] <= 15.0
        assert cleaned_data['phosphorus_ppm'] >= 0
        assert cleaned_data['potassium_ppm'] >= 0
    
    @pytest.mark.unit
    def test_soil_data_age_validation(self, soil_cleaner):
        """Test soil test age validation."""
        # Recent soil test - should pass
        recent_soil_data = {
            'ph': 6.2,
            'test_date': date.today().isoformat()
        }
        
        recent_result = soil_cleaner.validate_and_clean(recent_soil_data)
        assert recent_result['is_valid'] is True
        
        # Old soil test - should warn
        old_soil_data = {
            'ph': 6.2,
            'test_date': (date.today() - timedelta(days=4*365)).isoformat()  # 4 years old
        }
        
        old_result = soil_cleaner.validate_and_clean(old_soil_data)
        assert len(old_result['warnings']) > 0
        assert any('old' in warning.lower() for warning in old_result['warnings'])
    
    @pytest.mark.unit
    @pytest.mark.agricultural
    def test_extreme_soil_values_detection(self, soil_cleaner):
        """Test detection of extreme soil values."""
        extreme_soil_data = {
            'ph': 4.0,  # Very acidic
            'organic_matter_percent': 0.5,  # Very low
            'phosphorus_ppm': 2,  # Very low
            'potassium_ppm': 30,  # Very low
            'test_date': date.today().isoformat()
        }
        
        result = soil_cleaner.validate_and_clean(extreme_soil_data)
        
        # Should be valid but with warnings
        assert result['is_valid'] is True
        assert len(result['warnings']) > 0
        
        # Should flag extreme values
        warning_text = ' '.join(result['warnings']).lower()
        assert 'acidic' in warning_text or 'low' in warning_text
    
    @pytest.mark.unit
    async def test_pipeline_integration(self, validation_pipeline):
        """Test complete validation pipeline integration."""
        mixed_data = {
            'weather': {
                'temperature_f': 72.5,
                'humidity_percent': 65,
                'precipitation_inches': 0.1
            },
            'soil': {
                'ph': 6.2,
                'organic_matter_percent': 3.8,
                'phosphorus_ppm': 25,
                'test_date': date.today().isoformat()
            }
        }
        
        result = await validation_pipeline.validate_farm_data(mixed_data)
        
        assert result['overall_valid'] is True
        assert 'weather_validation' in result
        assert 'soil_validation' in result
        assert result['weather_validation']['is_valid'] is True
        assert result['soil_validation']['is_valid'] is True


class TestEnhancedCacheManager:
    """Test enhanced cache manager functionality."""
    
    @pytest.fixture
    def cache_manager(self, mock_redis):
        """Create cache manager instance."""
        return EnhancedCacheManager(redis_client=mock_redis)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_agricultural_data_caching(self, cache_manager, mock_redis):
        """Test caching of agricultural data with appropriate TTL."""
        # Mock Redis operations
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True
        
        # Cache soil test data
        soil_data = {
            'ph': 6.2,
            'organic_matter_percent': 3.8,
            'test_date': date.today().isoformat()
        }
        
        await cache_manager.cache_soil_data('test_location', soil_data)
        
        # Should use appropriate TTL for soil data (longer than weather)
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        ttl = call_args[0][1]  # Second argument is TTL
        assert ttl >= 86400  # At least 24 hours for soil data
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cache_invalidation_strategy(self, cache_manager, mock_redis):
        """Test cache invalidation for stale agricultural data."""
        # Mock cached data that's too old
        old_cached_data = {
            'data': {'ph': 6.2},
            'cached_at': (datetime.utcnow() - timedelta(days=30)).isoformat(),
            'data_age_days': 35
        }
        
        mock_redis.get.return_value = json.dumps(old_cached_data)
        
        result = await cache_manager.get_cached_soil_data('test_location')
        
        # Should return None for stale data and trigger cache invalidation
        assert result is None
        mock_redis.delete.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cache_performance_metrics(self, cache_manager, mock_redis):
        """Test cache performance metrics collection."""
        # Mock cache hit
        mock_redis.get.return_value = json.dumps({'cached_data': True})
        
        result = await cache_manager.get_cached_weather_data('test_location')
        
        # Should track cache metrics
        metrics = cache_manager.get_cache_metrics()
        assert 'hit_rate' in metrics
        assert 'total_requests' in metrics
        assert metrics['total_requests'] > 0