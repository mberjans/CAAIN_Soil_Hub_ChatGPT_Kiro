"""
Tests for the geocoding service.

This module tests the geocoding functionality including:
- Address to coordinates conversion
- Reverse geocoding (coordinates to address)
- Address autocomplete suggestions
- Caching functionality
- Error handling and fallback mechanisms
"""

import pytest
pytest_plugins = ('pytest_asyncio',)
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Dict, Any

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../src/services'))

from geocoding_service import (
    GeocodingService, NominatimProvider, GeocodingCache,
    GeocodingResult, AddressResult, AddressSuggestion, GeocodingError,
    AgriculturalEnhancementService, AgriculturalContext,
    BatchGeocodingRequest, BatchGeocodingResponse
)


class TestGeocodingCache:
    """Test the geocoding cache functionality."""
    
    def setup_method(self):
        """Set up test cache."""
        self.cache = GeocodingCache(max_size=10, ttl_hours=1)
    
    @pytest.mark.asyncio
    async def test_cache_set_and_get(self):
        """Test basic cache set and get operations."""
        result = GeocodingResult(
            latitude=42.0308,
            longitude=-93.6319,
            address="Ames, Iowa",
            display_name="Ames, Story County, Iowa, USA",
            confidence=0.9,
            provider="test"
        )
        
        # Cache the result
        await self.cache.set("test_query", result)
        
        # Retrieve from cache
        cached_result = await self.cache.get("test_query")
        
        assert cached_result is not None
        assert cached_result.latitude == 42.0308
        assert cached_result.longitude == -93.6319
        assert cached_result.address == "Ames, Iowa"
    
    @pytest.mark.asyncio
    async def test_cache_miss(self):
        """Test cache miss for non-existent key."""
        result = await self.cache.get("non_existent_key")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_cache_max_size_limit(self):
        """Test that cache respects max size limit."""
        # Fill cache beyond max size
        for i in range(15):  # max_size is 10
            result = GeocodingResult(
                latitude=42.0 + i * 0.001,
                longitude=-93.6,
                address=f"Address {i}",
                display_name=f"Display {i}",
                confidence=0.8,
                provider="test"
            )
            await self.cache.set(f"query_{i}", result)
        
        # Cache should only contain 10 items
        assert len(self.cache._cache) == 10
        
        # First items should be evicted
        assert await self.cache.get("query_0") is None
        assert await self.cache.get("query_14") is not None


class TestNominatimProvider:
    """Test the Nominatim geocoding provider."""
    
    def setup_method(self):
        """Set up test provider."""
        self.provider = NominatimProvider()
    
    async def teardown_method(self):
        """Clean up after tests."""
        await self.provider.close()
    
    @pytest.mark.asyncio
    async def test_geocode_success(self):
        """Test successful geocoding with mocked response."""
        mock_response_data = [{
            'lat': '42.0308',
            'lon': '-93.6319',
            'display_name': 'Ames, Story County, Iowa, United States',
            'address': {
                'city': 'Ames',
                'county': 'Story County',
                'state': 'Iowa',
                'country': 'United States',
                'postcode': '50010'
            }
        }]
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock the HTTP response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await self.provider.geocode("Ames, Iowa")
            
            assert result.latitude == 42.0308
            assert result.longitude == -93.6319
            assert "Ames" in result.address
            assert result.provider == "nominatim"
            assert 0.0 <= result.confidence <= 1.0
    
    @pytest.mark.asyncio
    async def test_geocode_no_results(self):
        """Test geocoding when no results are found."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock empty response
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=[])
            mock_get.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(GeocodingError) as exc_info:
                await self.provider.geocode("NonexistentPlace12345")
            
            assert "No results found" in str(exc_info.value)
            assert exc_info.value.provider == "nominatim"
    
    @pytest.mark.asyncio
    async def test_geocode_api_error(self):
        """Test geocoding when API returns error status."""
        with patch('aiohttp.ClientSession.get') as mock_get:
            # Mock error response
            mock_response = AsyncMock()
            mock_response.status = 500
            mock_get.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(GeocodingError) as exc_info:
                await self.provider.geocode("Test Address")
            
            assert "status 500" in str(exc_info.value)
            assert exc_info.value.provider == "nominatim"
    
    @pytest.mark.asyncio
    async def test_reverse_geocode_success(self):
        """Test successful reverse geocoding."""
        mock_response_data = {
            'display_name': 'Iowa State University, Ames, Story County, Iowa, United States',
            'address': {
                'university': 'Iowa State University',
                'city': 'Ames',
                'county': 'Story County',
                'state': 'Iowa',
                'country': 'United States',
                'postcode': '50011'
            }
        }
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await self.provider.reverse_geocode(42.0308, -93.6319)
            
            assert "Ames" in result.address
            assert result.provider == "nominatim"
            assert 0.0 <= result.confidence <= 1.0
    
    @pytest.mark.asyncio
    async def test_search_suggestions_success(self):
        """Test address suggestions functionality."""
        mock_response_data = [
            {
                'lat': '42.0308',
                'lon': '-93.6319',
                'display_name': 'Ames, Story County, Iowa, United States',
                'address': {
                    'city': 'Ames',
                    'county': 'Story County',
                    'state': 'Iowa'
                }
            },
            {
                'lat': '42.0275',
                'lon': '-93.6456',
                'display_name': 'Ames Municipal Airport, Ames, Iowa, United States',
                'address': {
                    'aeroway': 'Ames Municipal Airport',
                    'city': 'Ames',
                    'state': 'Iowa'
                }
            }
        ]
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_get.return_value.__aenter__.return_value = mock_response
            
            suggestions = await self.provider.search_suggestions("Ames", limit=5)
            
            assert len(suggestions) == 2
            assert all(isinstance(s, AddressSuggestion) for s in suggestions)
            assert suggestions[0].relevance > suggestions[1].relevance  # First should have higher relevance
            assert "Ames" in suggestions[0].address
    
    def test_format_address(self):
        """Test address formatting functionality."""
        # Test complete address
        components = {
            'house_number': '123',
            'road': 'Main Street',
            'city': 'Ames',
            'state': 'Iowa',
            'postcode': '50010'
        }
        
        formatted = self.provider._format_address(components)
        assert formatted == "123 Main Street, Ames, Iowa, 50010"
        
        # Test partial address
        components = {
            'city': 'Ames',
            'state': 'Iowa'
        }
        
        formatted = self.provider._format_address(components)
        assert formatted == "Ames, Iowa"
    
    def test_calculate_confidence(self):
        """Test confidence score calculation."""
        # High confidence result with house number and road
        result = {
            'address': {
                'house_number': '123',
                'road': 'Main Street',
                'city': 'Ames'
            }
        }
        confidence = self.provider._calculate_confidence(result)
        assert confidence >= 0.9
        
        # Lower confidence for general place
        result = {
            'class': 'place',
            'type': 'state',
            'address': {'state': 'Iowa'}
        }
        confidence = self.provider._calculate_confidence(result)
        assert confidence <= 0.5


class TestGeocodingService:
    """Test the main geocoding service."""
    
    def setup_method(self):
        """Set up test service."""
        self.service = GeocodingService()
    
    async def teardown_method(self):
        """Clean up after tests."""
        await self.service.close()
    
    @pytest.mark.asyncio
    async def test_geocode_address_success(self):
        """Test successful address geocoding."""
        # Mock the provider's geocode method
        mock_result = GeocodingResult(
            latitude=42.0308,
            longitude=-93.6319,
            address="Ames, Iowa",
            display_name="Ames, Story County, Iowa, USA",
            confidence=0.9,
            provider="nominatim"
        )
        
        with patch.object(self.service.primary_provider, 'geocode', return_value=mock_result):
            result = await self.service.geocode_address("Ames, Iowa")
            
            assert result.latitude == 42.0308
            assert result.longitude == -93.6319
            assert result.address == "Ames, Iowa"
            assert result.confidence == 0.9
    
    @pytest.mark.asyncio
    async def test_geocode_address_empty_input(self):
        """Test geocoding with empty address."""
        with pytest.raises(GeocodingError) as exc_info:
            await self.service.geocode_address("")
        
        assert "cannot be empty" in str(exc_info.value)
        
        with pytest.raises(GeocodingError) as exc_info:
            await self.service.geocode_address("   ")
        
        assert "cannot be empty" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_geocode_address_with_caching(self):
        """Test that geocoding results are cached."""
        mock_result = GeocodingResult(
            latitude=42.0308,
            longitude=-93.6319,
            address="Ames, Iowa",
            display_name="Ames, Story County, Iowa, USA",
            confidence=0.9,
            provider="nominatim"
        )
        
        with patch.object(self.service.primary_provider, 'geocode', return_value=mock_result) as mock_geocode:
            # First call should hit the provider
            result1 = await self.service.geocode_address("Ames, Iowa")
            assert mock_geocode.call_count == 1
            
            # Second call should use cache
            result2 = await self.service.geocode_address("Ames, Iowa")
            assert mock_geocode.call_count == 1  # Should not increase
            
            # Results should be identical
            assert result1.latitude == result2.latitude
            assert result1.longitude == result2.longitude
    
    @pytest.mark.asyncio
    async def test_reverse_geocode_success(self):
        """Test successful reverse geocoding."""
        mock_result = AddressResult(
            address="Ames, Iowa",
            display_name="Ames, Story County, Iowa, USA",
            confidence=0.9,
            provider="nominatim"
        )
        
        with patch.object(self.service.primary_provider, 'reverse_geocode', return_value=mock_result):
            result = await self.service.reverse_geocode(42.0308, -93.6319)
            
            assert result.address == "Ames, Iowa"
            assert result.confidence == 0.9
    
    @pytest.mark.asyncio
    async def test_reverse_geocode_invalid_coordinates(self):
        """Test reverse geocoding with invalid coordinates."""
        # Invalid latitude
        with pytest.raises(GeocodingError) as exc_info:
            await self.service.reverse_geocode(91.0, -93.6319)
        assert "Invalid latitude" in str(exc_info.value)
        
        # Invalid longitude
        with pytest.raises(GeocodingError) as exc_info:
            await self.service.reverse_geocode(42.0308, 181.0)
        assert "Invalid longitude" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_address_suggestions_success(self):
        """Test address suggestions functionality."""
        mock_suggestions = [
            AddressSuggestion(
                display_name="Ames, Iowa",
                address="Ames, Iowa",
                latitude=42.0308,
                longitude=-93.6319,
                relevance=1.0
            ),
            AddressSuggestion(
                display_name="Ames Municipal Airport",
                address="Ames Municipal Airport, Ames, Iowa",
                latitude=42.0275,
                longitude=-93.6456,
                relevance=0.9
            )
        ]
        
        with patch.object(self.service.primary_provider, 'search_suggestions', return_value=mock_suggestions):
            suggestions = await self.service.get_address_suggestions("Ames")
            
            assert len(suggestions) == 2
            assert suggestions[0].address == "Ames, Iowa"
            assert suggestions[0].relevance == 1.0
    
    @pytest.mark.asyncio
    async def test_get_address_suggestions_short_query(self):
        """Test address suggestions with short query."""
        # Empty query
        suggestions = await self.service.get_address_suggestions("")
        assert suggestions == []
        
        # Short query
        suggestions = await self.service.get_address_suggestions("Am")
        assert suggestions == []
    
    @pytest.mark.asyncio
    async def test_get_address_suggestions_provider_failure(self):
        """Test address suggestions when provider fails."""
        with patch.object(self.service.primary_provider, 'search_suggestions', 
                         side_effect=GeocodingError("Provider failed")):
            # Should return empty list instead of raising exception
            suggestions = await self.service.get_address_suggestions("Ames")
            assert suggestions == []


class TestGeocodingIntegration:
    """Integration tests for geocoding functionality."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_geocoding_ames_iowa(self):
        """Test real geocoding with Ames, Iowa (if network available)."""
        service = GeocodingService()
        
        try:
            result = await service.geocode_address("Ames, Iowa")
            
            # Verify result is reasonable for Ames, Iowa
            assert 41.5 <= result.latitude <= 42.5  # Approximate latitude range
            assert -94.0 <= result.longitude <= -93.0  # Approximate longitude range
            assert "Iowa" in result.address or "Iowa" in result.display_name
            assert result.confidence > 0.5
            assert result.provider == "nominatim"
            
        except GeocodingError:
            # Skip test if network/service unavailable
            pytest.skip("Geocoding service unavailable")
        finally:
            await service.close()
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_reverse_geocoding_iowa_state(self):
        """Test real reverse geocoding for Iowa State University coordinates."""
        service = GeocodingService()
        
        try:
            # Iowa State University coordinates
            result = await service.reverse_geocode(42.0308, -93.6319)
            
            # Should return something related to Ames/Iowa
            assert "Iowa" in result.address or "Ames" in result.address
            assert result.confidence > 0.5
            
        except GeocodingError:
            # Skip test if network/service unavailable
            pytest.skip("Geocoding service unavailable")
        finally:
            await service.close()
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_address_suggestions(self):
        """Test real address suggestions functionality."""
        service = GeocodingService()
        
        try:
            suggestions = await service.get_address_suggestions("Ames, Iowa")
            
            # Should get some suggestions
            assert len(suggestions) > 0
            
            # First suggestion should be relevant
            first_suggestion = suggestions[0]
            assert "Ames" in first_suggestion.address or "Ames" in first_suggestion.display_name
            assert first_suggestion.latitude is not None
            assert first_suggestion.longitude is not None
            
        except Exception:
            # Skip test if network/service unavailable
            pytest.skip("Geocoding service unavailable")
        finally:
            await service.close()


class TestGeocodingErrorHandling:
    """Test error handling in geocoding service."""
    
    def setup_method(self):
        """Set up test service."""
        self.service = GeocodingService()
    
    async def teardown_method(self):
        """Clean up after tests."""
        await self.service.close()
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self):
        """Test handling of network errors."""
        with patch.object(self.service.primary_provider, 'geocode', 
                         side_effect=GeocodingError("Network error", "nominatim")):
            with pytest.raises(GeocodingError) as exc_info:
                await self.service.geocode_address("Test Address")
            
            assert "Network error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_invalid_response_handling(self):
        """Test handling of invalid API responses."""
        with patch.object(self.service.primary_provider, 'geocode', 
                         side_effect=GeocodingError("Invalid response", "nominatim")):
            with pytest.raises(GeocodingError) as exc_info:
                await self.service.geocode_address("Test Address")
            
            assert "Invalid response" in str(exc_info.value)


class TestAgriculturalEnhancementService:
    """Test the agricultural enhancement service functionality."""
    
    def setup_method(self):
        """Set up test agricultural enhancement service."""
        self.service = AgriculturalEnhancementService()
    
    @pytest.mark.asyncio
    async def test_enhance_with_agricultural_context_success(self):
        """Test successful agricultural context enhancement."""
        # Mock the HTTP session and responses
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            'primary_zone': {
                'hardiness_zone': '5a',
                'koppen_class': 'Dfa'
            },
            'metadata': {
                'elevation': 300,
                'growing_season_days': 180,
                'frost_free_days': 160,
                'agricultural_suitability': 'Good'
            }
        })
        
        mock_soil_response = AsyncMock()
        mock_soil_response.status = 200
        mock_soil_response.json = AsyncMock(return_value={
            'soil_survey_area': 'Story County',
            'soil_type': 'Clay Loam',
            'drainage_class': 'Well Drained'
        })
        
        mock_session.get.return_value.__aenter__.return_value = mock_response
        mock_session.post.return_value.__aenter__.return_value = mock_soil_response
        
        with patch.object(self.service, '_get_session', return_value=mock_session):
            components = {'county': 'Story', 'state': 'Iowa'}
            result = await self.service.enhance_with_agricultural_context(42.0308, -93.6319, components)
            
            assert isinstance(result, AgriculturalContext)
            assert result.usda_zone == '5a'
            assert result.climate_zone == 'Dfa'
            assert result.soil_survey_area == 'Story County'
            assert result.agricultural_district == 'Corn Belt'
            assert result.county == 'Story'
            assert result.state == 'Iowa'
            assert result.elevation_meters == 300
            assert result.growing_season_days == 180
            assert result.frost_free_days == 160
            assert result.agricultural_suitability == 'Good'
    
    @pytest.mark.asyncio
    async def test_enhance_with_agricultural_context_fallback(self):
        """Test agricultural context enhancement with service failures."""
        # Mock session that returns error responses
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_session.get.return_value.__aenter__.return_value = mock_response
        mock_session.post.return_value.__aenter__.return_value = mock_response
        
        with patch.object(self.service, '_get_session', return_value=mock_session):
            components = {'county': 'Story', 'state': 'Iowa'}
            result = await self.service.enhance_with_agricultural_context(42.0308, -93.6319, components)
            
            # Should return basic context from components
            assert isinstance(result, AgriculturalContext)
            assert result.county == 'Story'
            assert result.state == 'Iowa'
            assert result.usda_zone is None
            assert result.climate_zone is None
    
    def test_extract_agricultural_district(self):
        """Test agricultural district extraction."""
        # Test Corn Belt states
        components = {'state': 'Iowa', 'county': 'Story'}
        district = self.service._extract_agricultural_district(components)
        assert district == 'Corn Belt'
        
        # Test Wheat Belt states
        components = {'state': 'Kansas', 'county': 'Sedgwick'}
        district = self.service._extract_agricultural_district(components)
        assert district == 'Wheat Belt'
        
        # Test unknown state
        components = {'state': 'Unknown', 'county': 'Unknown'}
        district = self.service._extract_agricultural_district(components)
        assert district is None
    
    @pytest.mark.asyncio
    async def test_close_session(self):
        """Test session cleanup."""
        mock_session = AsyncMock()
        self.service.session = mock_session
        
        await self.service.close()
        
        mock_session.close.assert_called_once()


class TestEnhancedGeocodingService:
    """Test the enhanced geocoding service with agricultural context."""
    
    def setup_method(self):
        """Set up test enhanced geocoding service."""
        self.service = GeocodingService()
    
    def teardown_method(self):
        """Clean up after tests."""
        asyncio.create_task(self.service.close())
    
    @pytest.mark.asyncio
    async def test_geocode_with_agricultural_context(self):
        """Test geocoding with agricultural context enhancement."""
        # Mock the provider and agricultural enhancement
        mock_result = GeocodingResult(
            latitude=42.0308,
            longitude=-93.6319,
            address="Ames, Iowa",
            display_name="Ames, Story County, Iowa, USA",
            confidence=0.9,
            provider="nominatim",
            components={'county': 'Story', 'state': 'Iowa'}
        )
        
        mock_agricultural_context = AgriculturalContext(
            usda_zone='5a',
            climate_zone='Dfa',
            soil_survey_area='Story County',
            agricultural_district='Corn Belt',
            county='Story',
            state='Iowa',
            elevation_meters=300,
            growing_season_days=180,
            frost_free_days=160,
            agricultural_suitability='Good'
        )
        
        with patch.object(self.service.primary_provider, 'geocode', return_value=mock_result):
            with patch.object(self.service.agricultural_enhancement, 'enhance_with_agricultural_context', 
                            return_value=mock_agricultural_context):
                with patch.object(self.service.cache, 'get', return_value=None):
                    with patch.object(self.service.cache, 'set', return_value=None):
                        result = await self.service.geocode_address("Ames, Iowa", include_agricultural_context=True)
                        
                        assert result.agricultural_context is not None
                        assert result.agricultural_context.usda_zone == '5a'
                        assert result.agricultural_context.climate_zone == 'Dfa'
                        assert result.agricultural_context.agricultural_district == 'Corn Belt'
    
    @pytest.mark.asyncio
    async def test_geocode_without_agricultural_context(self):
        """Test geocoding without agricultural context enhancement."""
        mock_result = GeocodingResult(
            latitude=42.0308,
            longitude=-93.6319,
            address="Ames, Iowa",
            display_name="Ames, Story County, Iowa, USA",
            confidence=0.9,
            provider="nominatim",
            components={'county': 'Story', 'state': 'Iowa'}
        )
        
        with patch.object(self.service.primary_provider, 'geocode', return_value=mock_result):
            with patch.object(self.service.cache, 'get', return_value=None):
                with patch.object(self.service.cache, 'set', return_value=None):
                    result = await self.service.geocode_address("Ames, Iowa", include_agricultural_context=False)
                    
                    assert result.agricultural_context is None
    
    @pytest.mark.asyncio
    async def test_reverse_geocode_with_agricultural_context(self):
        """Test reverse geocoding with agricultural context enhancement."""
        mock_result = AddressResult(
            address="Ames, Iowa",
            display_name="Ames, Story County, Iowa, USA",
            components={'county': 'Story', 'state': 'Iowa'},
            confidence=0.9,
            provider="nominatim"
        )
        
        mock_agricultural_context = AgriculturalContext(
            usda_zone='5a',
            climate_zone='Dfa',
            soil_survey_area='Story County',
            agricultural_district='Corn Belt',
            county='Story',
            state='Iowa'
        )
        
        with patch.object(self.service.primary_provider, 'reverse_geocode', return_value=mock_result):
            with patch.object(self.service.agricultural_enhancement, 'enhance_with_agricultural_context', 
                            return_value=mock_agricultural_context):
                with patch.object(self.service.cache, 'get', return_value=None):
                    with patch.object(self.service.cache, 'set', return_value=None):
                        result = await self.service.reverse_geocode(42.0308, -93.6319, include_agricultural_context=True)
                        
                        assert result.agricultural_context is not None
                        assert result.agricultural_context.usda_zone == '5a'
                        assert result.agricultural_context.climate_zone == 'Dfa'
    
    @pytest.mark.asyncio
    async def test_batch_geocode_success(self):
        """Test successful batch geocoding."""
        addresses = ["Ames, Iowa", "Des Moines, Iowa", "Cedar Rapids, Iowa"]
        
        mock_results = [
            GeocodingResult(
                latitude=42.0308, longitude=-93.6319, address="Ames, Iowa",
                display_name="Ames, Story County, Iowa, USA", confidence=0.9,
                provider="nominatim", components={'county': 'Story', 'state': 'Iowa'}
            ),
            GeocodingResult(
                latitude=41.5868, longitude=-93.6250, address="Des Moines, Iowa",
                display_name="Des Moines, Polk County, Iowa, USA", confidence=0.9,
                provider="nominatim", components={'county': 'Polk', 'state': 'Iowa'}
            ),
            GeocodingResult(
                latitude=41.9778, longitude=-91.6656, address="Cedar Rapids, Iowa",
                display_name="Cedar Rapids, Linn County, Iowa, USA", confidence=0.9,
                provider="nominatim", components={'county': 'Linn', 'state': 'Iowa'}
            )
        ]
        
        mock_agricultural_context = AgriculturalContext(
            usda_zone='5a', climate_zone='Dfa', agricultural_district='Corn Belt'
        )
        
        request = BatchGeocodingRequest(
            addresses=addresses,
            include_agricultural_context=True
        )
        
        with patch.object(self.service, 'geocode_address', side_effect=mock_results):
            with patch.object(self.service.agricultural_enhancement, 'enhance_with_agricultural_context', 
                            return_value=mock_agricultural_context):
                result = await self.service.batch_geocode(request)
                
                assert isinstance(result, BatchGeocodingResponse)
                assert result.success_count == 3
                assert result.failure_count == 0
                assert len(result.results) == 3
                assert len(result.failed_addresses) == 0
                assert result.processing_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_batch_geocode_with_failures(self):
        """Test batch geocoding with some failures."""
        addresses = ["Ames, Iowa", "Invalid Address", "Des Moines, Iowa"]
        
        mock_results = [
            GeocodingResult(
                latitude=42.0308, longitude=-93.6319, address="Ames, Iowa",
                display_name="Ames, Story County, Iowa, USA", confidence=0.9,
                provider="nominatim", components={'county': 'Story', 'state': 'Iowa'}
            ),
            None,  # Simulate failure
            GeocodingResult(
                latitude=41.5868, longitude=-93.6250, address="Des Moines, Iowa",
                display_name="Des Moines, Polk County, Iowa, USA", confidence=0.9,
                provider="nominatim", components={'county': 'Polk', 'state': 'Iowa'}
            )
        ]
        
        request = BatchGeocodingRequest(
            addresses=addresses,
            include_agricultural_context=False
        )
        
        with patch.object(self.service, 'geocode_address', side_effect=mock_results):
            result = await self.service.batch_geocode(request)
            
            assert isinstance(result, BatchGeocodingResponse)
            assert result.success_count == 2
            assert result.failure_count == 1
            assert len(result.results) == 2
            assert len(result.failed_addresses) == 1
            assert "Invalid Address" in result.failed_addresses


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])