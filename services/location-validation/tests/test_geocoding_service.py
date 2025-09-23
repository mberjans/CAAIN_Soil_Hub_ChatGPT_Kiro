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
    GeocodingResult, AddressResult, AddressSuggestion, GeocodingError
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


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])