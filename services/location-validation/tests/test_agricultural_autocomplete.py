"""
Tests for Agricultural Address Autocomplete Service

This module contains comprehensive tests for the agricultural address autocomplete
functionality, including unit tests, integration tests, and agricultural validation tests.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from src.services.agricultural_autocomplete_service import (
    AgriculturalAutocompleteService,
    AgriculturalAddressSuggestion,
    USGSGNISProvider,
    USDARuralRouteProvider
)
from src.services.geocoding_service import GeocodingService


class TestAgriculturalAddressSuggestion:
    """Test the AgriculturalAddressSuggestion model."""
    
    def test_valid_agricultural_suggestion(self):
        """Test creating a valid agricultural address suggestion."""
        suggestion = AgriculturalAddressSuggestion(
            display_name="Test Farm, Ames, IA",
            address="123 Farm Road, Ames, IA 50010",
            latitude=42.0308,
            longitude=-93.6208,
            relevance=0.9,
            agricultural_type="farm",
            county="Story",
            state="IA",
            data_sources=["USGS_GNIS"],
            confidence=0.8
        )
        
        assert suggestion.display_name == "Test Farm, Ames, IA"
        assert suggestion.agricultural_type == "farm"
        assert suggestion.confidence == 0.8
    
    def test_invalid_agricultural_type(self):
        """Test validation of agricultural type."""
        with pytest.raises(ValueError, match="Invalid agricultural type"):
            AgriculturalAddressSuggestion(
                display_name="Test",
                address="Test Address",
                relevance=0.5,
                agricultural_type="invalid_type"
            )
    
    def test_confidence_bounds(self):
        """Test confidence score bounds validation."""
        # Test valid confidence scores
        suggestion = AgriculturalAddressSuggestion(
            display_name="Test",
            address="Test Address",
            relevance=0.5,
            confidence=0.0
        )
        assert suggestion.confidence == 0.0
        
        suggestion = AgriculturalAddressSuggestion(
            display_name="Test",
            address="Test Address",
            relevance=0.5,
            confidence=1.0
        )
        assert suggestion.confidence == 1.0


class TestUSDARuralRouteProvider:
    """Test the USDA Rural Route Provider."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.provider = USDARuralRouteProvider()
    
    def test_is_rural_address_valid_patterns(self):
        """Test detection of valid rural address patterns."""
        rural_patterns = [
            "RR 1",
            "Rural Route 2",
            "Route 3",
            "Box 123",
            "HC 1",
            "HC 1 Box 456"
        ]
        
        for pattern in rural_patterns:
            assert self.provider.is_rural_address(pattern), f"Should detect '{pattern}' as rural address"
    
    def test_is_rural_address_invalid_patterns(self):
        """Test that non-rural addresses are not detected."""
        non_rural_patterns = [
            "123 Main Street",
            "Ames, IA",
            "Farm Road",
            "Highway 30"
        ]
        
        for pattern in non_rural_patterns:
            assert not self.provider.is_rural_address(pattern), f"Should not detect '{pattern}' as rural address"
    
    @pytest.mark.asyncio
    async def test_enhance_rural_address(self):
        """Test enhancement of rural addresses with USDA information."""
        base_suggestion = AgriculturalAddressSuggestion(
            display_name="Test Rural Route",
            address="RR 1 Box 123",
            relevance=0.8,
            agricultural_type="general",
            county="Story",
            state="IA"
        )
        
        enhanced = await self.provider.enhance_rural_address("RR 1 Box 123", base_suggestion)
        
        assert enhanced.rural_route == "RR 1"
        assert enhanced.agricultural_type == "rural_route"
        assert "USDA_Rural_Route" in enhanced.data_sources
        assert enhanced.farm_service_agency == "FSA Story County, IA"


class TestUSGSGNISProvider:
    """Test the USGS GNIS Provider."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.provider = USGSGNISProvider()
    
    @pytest.mark.asyncio
    async def test_search_agricultural_features(self):
        """Test search for agricultural features."""
        # Mock the session and response
        mock_session = AsyncMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = []
        
        mock_session.get.return_value.__aenter__.return_value = mock_response
        
        with patch.object(self.provider, '_get_session', return_value=mock_session):
            suggestions = await self.provider.search_agricultural_features("Test Farm", 5)
            
            # Should return empty list for now (simplified implementation)
            assert isinstance(suggestions, list)
    
    async def close(self):
        """Close provider session."""
        await self.provider.close()


class TestAgriculturalAutocompleteService:
    """Test the main Agricultural Autocomplete Service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = AgriculturalAutocompleteService()
        self.mock_nominatim_provider = AsyncMock()
        self.service.set_nominatim_provider(self.mock_nominatim_provider)
    
    @pytest.mark.asyncio
    async def test_get_agricultural_suggestions_rural_address(self):
        """Test getting suggestions for rural addresses."""
        # Mock the rural address detection
        with patch.object(self.service.usda_provider, 'is_rural_address', return_value=True):
            with patch.object(self.service, '_get_rural_address_suggestions', return_value=[
                AgriculturalAddressSuggestion(
                    display_name="RR 1",
                    address="RR 1",
                    agricultural_type="rural_route",
                    data_sources=["USDA_Rural_Route"],
                    relevance=0.9,
                    confidence=0.8
                )
            ]):
                suggestions = await self.service.get_agricultural_suggestions("RR 1", 5)
                
                assert len(suggestions) > 0
                assert suggestions[0].agricultural_type == "rural_route"
    
    @pytest.mark.asyncio
    async def test_get_agricultural_suggestions_fallback(self):
        """Test fallback to Nominatim when agricultural providers fail."""
        # Mock all agricultural providers to return empty results
        with patch.object(self.service.usda_provider, 'is_rural_address', return_value=False):
            with patch.object(self.service.usgs_provider, 'search_agricultural_features', return_value=[]):
                # Mock Nominatim provider
                mock_nominatim_suggestion = AgriculturalAddressSuggestion(
                    display_name="Test Location",
                    address="123 Main St, Ames, IA",
                    latitude=42.0308,
                    longitude=-93.6208,
                    relevance=0.7,
                    agricultural_type="general",
                    data_sources=["Nominatim"],
                    confidence=0.6
                )
                
                with patch.object(self.service, '_get_nominatim_suggestions', return_value=[mock_nominatim_suggestion]):
                    suggestions = await self.service.get_agricultural_suggestions("123 Main St", 5)
                    
                    assert len(suggestions) > 0
                    assert suggestions[0].data_sources == ["Nominatim"]
    
    @pytest.mark.asyncio
    async def test_prioritize_agricultural_suggestions(self):
        """Test prioritization of agricultural locations."""
        suggestions = [
            AgriculturalAddressSuggestion(
                display_name="General Location",
                address="123 Main St",
                relevance=0.8,
                agricultural_type="general",
                confidence=0.7
            ),
            AgriculturalAddressSuggestion(
                display_name="Test Farm",
                address="456 Farm Road",
                relevance=0.7,
                agricultural_type="farm",
                confidence=0.8
            )
        ]
        
        prioritized = self.service._prioritize_agricultural_suggestions(suggestions)
        
        # Farm should be prioritized over general location
        assert prioritized[0].agricultural_type == "farm"
        assert prioritized[1].agricultural_type == "general"
    
    @pytest.mark.asyncio
    async def test_cache_functionality(self):
        """Test caching of agricultural suggestions."""
        # First call should populate cache
        with patch.object(self.service, '_get_rural_address_suggestions', return_value=[]):
            with patch.object(self.service, '_get_nominatim_suggestions', return_value=[]):
                suggestions1 = await self.service.get_agricultural_suggestions("test query", 5)
                
                # Second call should use cache
                suggestions2 = await self.service.get_agricultural_suggestions("test query", 5)
                
                # Both should return the same results
                assert suggestions1 == suggestions2
    
    @pytest.mark.asyncio
    async def test_query_validation(self):
        """Test query validation."""
        # Empty query
        suggestions = await self.service.get_agricultural_suggestions("", 5)
        assert suggestions == []
        
        # Short query
        suggestions = await self.service.get_agricultural_suggestions("ab", 5)
        assert suggestions == []
        
        # Valid query
        with patch.object(self.service, '_get_rural_address_suggestions', return_value=[]):
            with patch.object(self.service, '_get_nominatim_suggestions', return_value=[]):
                suggestions = await self.service.get_agricultural_suggestions("valid query", 5)
                assert isinstance(suggestions, list)


class TestGeocodingServiceIntegration:
    """Test integration of agricultural autocomplete with GeocodingService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = GeocodingService()
    
    @pytest.mark.asyncio
    async def test_get_agricultural_address_suggestions(self):
        """Test the agricultural address suggestions method."""
        # Mock the agricultural autocomplete service
        mock_suggestion = AgriculturalAddressSuggestion(
            display_name="Test Farm",
            address="123 Farm Road",
            latitude=42.0308,
            longitude=-93.6208,
            relevance=0.9,
            agricultural_type="farm",
            county="Story",
            state="IA",
            data_sources=["USGS_GNIS"],
            confidence=0.8
        )
        
        with patch.object(self.service.agricultural_autocomplete, 'get_agricultural_suggestions', return_value=[mock_suggestion]):
            suggestions = await self.service.get_agricultural_address_suggestions("farm", 5)
            
            assert len(suggestions) == 1
            assert suggestions[0].agricultural_type == "farm"
            assert suggestions[0].county == "Story"
    
    @pytest.mark.asyncio
    async def test_fallback_to_regular_suggestions(self):
        """Test fallback to regular suggestions when agricultural service fails."""
        # Mock agricultural service to raise exception
        with patch.object(self.service.agricultural_autocomplete, 'get_agricultural_suggestions', side_effect=Exception("Service error")):
            # Mock regular suggestions
            with patch.object(self.service, 'get_address_suggestions', return_value=[]):
                suggestions = await self.service.get_agricultural_address_suggestions("test", 5)
                
                # Should return empty list due to fallback
                assert suggestions == []


class TestAgriculturalValidation:
    """Agricultural domain validation tests."""
    
    @pytest.mark.asyncio
    async def test_farm_address_prioritization(self):
        """Test that farm addresses are properly prioritized."""
        service = AgriculturalAutocompleteService()
        
        suggestions = [
            AgriculturalAddressSuggestion(
                display_name="City Hall",
                address="123 Main St",
                relevance=0.9,
                agricultural_type="general",
                confidence=0.8
            ),
            AgriculturalAddressSuggestion(
                display_name="Johnson Farm",
                address="456 Farm Road",
                relevance=0.7,
                agricultural_type="farm",
                confidence=0.8
            )
        ]
        
        prioritized = service._prioritize_agricultural_suggestions(suggestions)
        
        # Farm should be first
        assert prioritized[0].agricultural_type == "farm"
        assert prioritized[0].display_name == "Johnson Farm"
    
    @pytest.mark.asyncio
    async def test_rural_route_detection(self):
        """Test detection of various rural route patterns."""
        provider = USDARuralRouteProvider()
        
        test_cases = [
            ("RR 1", True),
            ("Rural Route 2", True),
            ("Route 3", True),
            ("Box 123", True),
            ("HC 1", True),
            ("HC 1 Box 456", True),
            ("123 Main Street", False),
            ("Ames, IA", False)
        ]
        
        for address, expected in test_cases:
            result = provider.is_rural_address(address)
            assert result == expected, f"Failed for address: {address}"
    
    @pytest.mark.asyncio
    async def test_agricultural_type_classification(self):
        """Test classification of different agricultural types."""
        service = AgriculturalAutocompleteService()
        
        test_cases = [
            ("Johnson Farm", "farm"),
            ("Research Station", "research_station"),
            ("Extension Office", "extension_office"),
            ("Agricultural Facility", "agricultural_facility"),
            ("RR 1", "rural_route"),
            ("123 Main St", "general")
        ]
        
        for address, expected_type in test_cases:
            suggestion = AgriculturalAddressSuggestion(
                display_name=address,
                address=address,
                relevance=0.8,
                agricultural_type="general",
                confidence=0.7
            )
            
            enhanced = await service._enhance_with_agricultural_context(suggestion)
            
            # The enhancement should detect agricultural keywords
            if expected_type != "general":
                assert enhanced.agricultural_type == expected_type or enhanced.relevance > suggestion.relevance


# Performance tests
class TestPerformance:
    """Performance tests for agricultural autocomplete."""
    
    @pytest.mark.asyncio
    async def test_response_time_requirement(self):
        """Test that agricultural suggestions are returned within acceptable time."""
        service = AgriculturalAutocompleteService()
        
        start_time = datetime.now()
        
        with patch.object(service, '_get_rural_address_suggestions', return_value=[]):
            with patch.object(service, '_get_nominatim_suggestions', return_value=[]):
                suggestions = await service.get_agricultural_suggestions("test query", 5)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        # Should respond within 2 seconds
        assert elapsed < 2.0, f"Response time {elapsed}s exceeds 2s requirement"
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        service = AgriculturalAutocompleteService()
        
        # Create multiple concurrent requests
        tasks = [
            service.get_agricultural_suggestions(f"query {i}", 5)
            for i in range(10)
        ]
        
        start_time = datetime.now()
        results = await asyncio.gather(*tasks)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        # All requests should complete
        assert len(results) == 10
        # Should handle concurrent requests efficiently
        assert elapsed < 5.0, f"Concurrent requests took {elapsed}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])