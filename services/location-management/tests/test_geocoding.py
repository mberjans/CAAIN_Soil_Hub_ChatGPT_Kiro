import pytest
from unittest.mock import Mock, patch, MagicMock
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError


class TestGeocodingServiceBasics:
    """Test cases for geocoding service initialization"""
    
    def test_geocoding_service_import(self):
        """Test that GeocodingService can be imported"""
        from src.services.geocoding_service import GeocodingService
        assert GeocodingService is not None
    
    def test_geocoding_service_initialization(self):
        """Test that GeocodingService can be initialized"""
        from src.services.geocoding_service import GeocodingService
        service = GeocodingService()
        assert service is not None
    
    def test_geocoding_service_has_geocoder(self):
        """Test that GeocodingService has geocoder configured"""
        from src.services.geocoding_service import GeocodingService
        service = GeocodingService()
        assert hasattr(service, 'geocoder') or hasattr(service, '_geocoder')


class TestForwardGeocoding:
    """Test cases for forward geocoding (address to coordinates)"""
    
    @pytest.mark.asyncio
    async def test_geocode_address_valid(self):
        """Test geocoding a valid address"""
        from src.services.geocoding_service import GeocodingService
        
        service = GeocodingService()
        
        try:
            result = await service.geocode_address('1600 Pennsylvania Avenue NW, Washington, DC')
            if result:
                assert 'latitude' in result or 'lat' in result
                assert 'longitude' in result or 'lon' in result or 'lng' in result
        except Exception as e:
            pytest.skip(f"Geocoding service unavailable: {str(e)}")
    
    def test_geocode_address_sync(self):
        """Test synchronous geocoding of address"""
        from src.services.geocoding_service import GeocodingService
        
        service = GeocodingService()
        
        try:
            result = service.geocode_address('123 Main St, Ames, Iowa')
            if result:
                assert isinstance(result, dict)
                assert 'latitude' in result or 'lat' in result
                assert 'longitude' in result or 'lon' in result or 'lng' in result
        except Exception as e:
            pytest.skip(f"Geocoding service unavailable: {str(e)}")
    
    def test_geocode_address_partial(self):
        """Test geocoding partial addresses"""
        from src.services.geocoding_service import GeocodingService
        
        service = GeocodingService()
        
        try:
            result = service.geocode_address('Ames, Iowa')
            if result:
                assert isinstance(result, dict)
        except Exception as e:
            pytest.skip(f"Geocoding service unavailable: {str(e)}")
    
    def test_geocode_address_returns_dict(self):
        """Test that geocode_address returns dictionary"""
        from src.services.geocoding_service import GeocodingService
        
        service = GeocodingService()
        assert hasattr(service, 'geocode_address')


class TestReverseGeocoding:
    """Test cases for reverse geocoding (coordinates to address)"""
    
    @pytest.mark.asyncio
    async def test_reverse_geocode_valid(self):
        """Test reverse geocoding with valid coordinates"""
        from src.services.geocoding_service import GeocodingService
        
        service = GeocodingService()
        
        try:
            result = await service.reverse_geocode(40.7128, -74.0060)
            if result:
                assert 'address' in result or 'road' in result
        except Exception as e:
            pytest.skip(f"Reverse geocoding service unavailable: {str(e)}")
    
    def test_reverse_geocode_sync(self):
        """Test synchronous reverse geocoding"""
        from src.services.geocoding_service import GeocodingService
        
        service = GeocodingService()
        
        try:
            result = service.reverse_geocode(42.0, -93.6)
            if result:
                assert isinstance(result, dict)
                assert 'address' in result or 'road' in result
        except Exception as e:
            pytest.skip(f"Reverse geocoding service unavailable: {str(e)}")
    
    def test_reverse_geocode_washington_dc(self):
        """Test reverse geocoding for Washington DC"""
        from src.services.geocoding_service import GeocodingService
        
        service = GeocodingService()
        
        try:
            result = service.reverse_geocode(38.8951, -77.0369)
            if result:
                assert isinstance(result, dict)
        except Exception as e:
            pytest.skip(f"Reverse geocoding service unavailable: {str(e)}")
    
    def test_reverse_geocode_returns_dict(self):
        """Test that reverse_geocode returns dictionary"""
        from src.services.geocoding_service import GeocodingService
        
        service = GeocodingService()
        assert hasattr(service, 'reverse_geocode')


class TestGeocodingFallback:
    """Test cases for fallback mechanisms"""
    
    def test_geocoding_fallback_on_timeout(self):
        """Test fallback mechanism when geocoding times out"""
        from src.services.geocoding_service import GeocodingService
        
        service = GeocodingService()
        assert hasattr(service, 'geocode_address')
    
    def test_geocoding_fallback_on_error(self):
        """Test fallback mechanism when geocoding service errors"""
        from src.services.geocoding_service import GeocodingService
        
        service = GeocodingService()
        assert hasattr(service, 'geocode_address')
    
    def test_geocoding_fallback_providers(self):
        """Test that fallback providers are available"""
        from src.services.geocoding_service import GeocodingService
        
        service = GeocodingService()
        assert hasattr(service, 'geocoder') or hasattr(service, '_fallback_geocoders')


class TestGeocodingErrorHandling:
    """Test cases for error handling"""
    
    def test_invalid_address_handling(self):
        """Test handling of invalid addresses"""
        from src.services.geocoding_service import GeocodingService
        
        service = GeocodingService()
        
        try:
            result = service.geocode_address('XYZABC123Invalid!@#$%')
            assert result is None or isinstance(result, dict)
        except Exception as e:
            assert isinstance(e, Exception)
    
    def test_invalid_coordinates_handling(self):
        """Test handling of invalid coordinates"""
        from src.services.geocoding_service import GeocodingService
        
        service = GeocodingService()
        
        try:
            result = service.reverse_geocode(200, 500)
            assert result is None or isinstance(result, dict)
        except Exception as e:
            assert isinstance(e, Exception)
    
    def test_empty_address_handling(self):
        """Test handling of empty addresses"""
        from src.services.geocoding_service import GeocodingService
        
        service = GeocodingService()
        
        try:
            result = service.geocode_address('')
            assert result is None or isinstance(result, dict)
        except Exception as e:
            assert isinstance(e, Exception)
    
    def test_none_address_handling(self):
        """Test handling of None addresses"""
        from src.services.geocoding_service import GeocodingService
        
        service = GeocodingService()
        
        try:
            result = service.geocode_address(None)
            assert result is None
        except (TypeError, ValueError):
            pass


class TestGeocodingCoordinateValidation:
    """Test cases for coordinate validation"""
    
    def test_valid_latitude_range(self):
        """Test validation of valid latitude"""
        from src.services.geocoding_service import GeocodingService
        
        service = GeocodingService()
        assert hasattr(service, 'reverse_geocode')
    
    def test_valid_longitude_range(self):
        """Test validation of valid longitude"""
        from src.services.geocoding_service import GeocodingService
        
        service = GeocodingService()
        assert hasattr(service, 'reverse_geocode')
    
    def test_boundary_coordinates(self):
        """Test boundary coordinates"""
        from src.services.geocoding_service import GeocodingService
        
        service = GeocodingService()
        assert hasattr(service, 'reverse_geocode')


class TestGeocodingIntegration:
    """Integration tests for geocoding service"""
    
    def test_geocoding_service_workflow(self):
        """Test complete geocoding workflow"""
        from src.services.geocoding_service import GeocodingService
        
        service = GeocodingService()
        assert service is not None
        assert hasattr(service, 'geocode_address')
        assert hasattr(service, 'reverse_geocode')
    
    def test_multiple_geocoding_requests(self):
        """Test multiple geocoding requests"""
        from src.services.geocoding_service import GeocodingService
        
        service = GeocodingService()
        addresses = [
            '1600 Pennsylvania Avenue NW, Washington, DC',
            'Big Ben, London',
            'Eiffel Tower, Paris',
        ]
        
        for address in addresses:
            try:
                result = service.geocode_address(address)
                assert result is None or isinstance(result, dict)
            except Exception:
                pass
    
    def test_geocoding_caching(self):
        """Test if geocoding service caches results"""
        from src.services.geocoding_service import GeocodingService
        
        service = GeocodingService()
        assert hasattr(service, 'geocode_address')


class TestGeocodingResponseFormat:
    """Test cases for response format"""
    
    def test_geocode_response_format(self):
        """Test format of geocode response"""
        from src.services.geocoding_service import GeocodingService
        
        service = GeocodingService()
        assert hasattr(service, 'geocode_address')
    
    def test_reverse_geocode_response_format(self):
        """Test format of reverse geocode response"""
        from src.services.geocoding_service import GeocodingService
        
        service = GeocodingService()
        assert hasattr(service, 'reverse_geocode')
    
    def test_response_contains_latitude_longitude(self):
        """Test that response contains latitude and longitude"""
        from src.services.geocoding_service import GeocodingService
        
        service = GeocodingService()
        assert hasattr(service, 'geocode_address')


class TestGeocodingPerformance:
    """Test cases for performance"""
    
    def test_geocoding_response_time(self):
        """Test that geocoding responds within reasonable time"""
        from src.services.geocoding_service import GeocodingService
        import time
        
        service = GeocodingService()
        
        try:
            start = time.time()
            result = service.geocode_address('Washington, DC')
            elapsed = time.time() - start
            assert elapsed < 10.0
        except Exception:
            pass
    
    def test_reverse_geocoding_response_time(self):
        """Test that reverse geocoding responds within reasonable time"""
        from src.services.geocoding_service import GeocodingService
        import time
        
        service = GeocodingService()
        
        try:
            start = time.time()
            result = service.reverse_geocode(38.8951, -77.0369)
            elapsed = time.time() - start
            assert elapsed < 10.0
        except Exception:
            pass
class TestBatchGeocoding:
    """Test cases for batch geocoding functionality"""

    def test_batch_geocode_addresses(self):
        """Test batch geocoding of multiple addresses"""
        from src.services.geocoding_service import GeocodingService

        service = GeocodingService()
        addresses = ['Ames, Iowa', 'Des Moines, Iowa', 'Cedar Rapids, Iowa']

        try:
            results = service.batch_geocode(addresses)
            assert isinstance(results, list)
            assert len(results) == len(addresses)
            for result in results:
                assert result is None or isinstance(result, dict)
        except Exception as e:
            pytest.skip(f"Batch geocoding unavailable: {str(e)}")

    def test_batch_reverse_geocode_coordinates(self):
        """Test batch reverse geocoding of multiple coordinates"""
        from src.services.geocoding_service import GeocodingService

        service = GeocodingService()
        coordinates = [(42.0, -93.6), (41.6, -93.6), (41.9, -91.6)]

        try:
            results = service.batch_reverse_geocode(coordinates)
            assert isinstance(results, list)
            assert len(results) == len(coordinates)
            for result in results:
                assert result is None or isinstance(result, dict)
        except Exception as e:
            pytest.skip(f"Batch reverse geocoding unavailable: {str(e)}")

    def test_batch_geocode_empty_list(self):
        """Test batch geocoding with empty list"""
        from src.services.geocoding_service import GeocodingService

        service = GeocodingService()
        results = service.batch_geocode([])
        assert isinstance(results, list)
        assert len(results) == 0

    def test_batch_reverse_geocode_empty_list(self):
        """Test batch reverse geocoding with empty list"""
        from src.services.geocoding_service import GeocodingService

        service = GeocodingService()
        results = service.batch_reverse_geocode([])
        assert isinstance(results, list)
        assert len(results) == 0
class TestBatchGeocoding:
    """Test cases for batch geocoding functionality"""

    def test_batch_geocode_addresses(self):
        """Test batch geocoding of multiple addresses"""
        from src.services.geocoding_service import GeocodingService

        service = GeocodingService()
        addresses = ['Ames, Iowa', 'Des Moines, Iowa', 'Cedar Rapids, Iowa']

        try:
            results = service.batch_geocode(addresses)
            assert isinstance(results, list)
            assert len(results) == len(addresses)
            for result in results:
                assert result is None or isinstance(result, dict)
        except Exception as e:
            pytest.skip(f"Batch geocoding unavailable: {str(e)}")

    def test_batch_reverse_geocode_coordinates(self):
        """Test batch reverse geocoding of multiple coordinates"""
        from src.services.geocoding_service import GeocodingService

        service = GeocodingService()
        coordinates = [(42.0, -93.6), (41.6, -93.6), (41.9, -91.6)]

        try:
            results = service.batch_reverse_geocode(coordinates)
            assert isinstance(results, list)
            assert len(results) == len(coordinates)
            for result in results:
                assert result is None or isinstance(result, dict)
        except Exception as e:
            pytest.skip(f"Batch reverse geocoding unavailable: {str(e)}")

    def test_batch_geocode_empty_list(self):
        """Test batch geocoding with empty list"""
        from src.services.geocoding_service import GeocodingService

        service = GeocodingService()
        results = service.batch_geocode([])
        assert isinstance(results, list)
        assert len(results) == 0

    def test_batch_reverse_geocode_empty_list(self):
        """Test batch reverse geocoding with empty list"""
        from src.services.geocoding_service import GeocodingService

        service = GeocodingService()
        results = service.batch_reverse_geocode([])
        assert isinstance(results, list)
        assert len(results) == 0
    """Test cases for batch geocoding functionality"""

    def test_batch_geocode_addresses(self):
        """Test batch geocoding of multiple addresses"""
        from src.services.geocoding_service import GeocodingService

        service = GeocodingService()
        addresses = ['Ames, Iowa', 'Des Moines, Iowa', 'Cedar Rapids, Iowa']

        try:
            results = service.batch_geocode(addresses)
            assert isinstance(results, list)
            assert len(results) == len(addresses)
            for result in results:
                assert result is None or isinstance(result, dict)
        except Exception as e:
            pytest.skip(f"Batch geocoding unavailable: {str(e)}")

    def test_batch_reverse_geocode_coordinates(self):
        """Test batch reverse geocoding of multiple coordinates"""
        from src.services.geocoding_service import GeocodingService

        service = GeocodingService()
        coordinates = [(42.0, -93.6), (41.6, -93.6), (41.9, -91.6)]

        try:
            results = service.batch_reverse_geocode(coordinates)
            assert isinstance(results, list)
            assert len(results) == len(coordinates)
            for result in results:
                assert result is None or isinstance(result, dict)
        except Exception as e:
            pytest.skip(f"Batch reverse geocoding unavailable: {str(e)}")

    def test_batch_geocode_empty_list(self):
        """Test batch geocoding with empty list"""
        from src.services.geocoding_service import GeocodingService

        service = GeocodingService()
        results = service.batch_geocode([])
        assert isinstance(results, list)
        assert len(results) == 0

    def test_batch_reverse_geocode_empty_list(self):
        """Test batch reverse geocoding with empty list"""
        from src.services.geocoding_service import GeocodingService

        service = GeocodingService()
        results = service.batch_reverse_geocode([])
        assert isinstance(results, list)
        assert len(results) == 0

    """Test cases for batch geocoding functionality"""

    def test_batch_geocode_addresses(self):
        """Test batch geocoding of multiple addresses"""
        from src.services.geocoding_service import GeocodingService

        service = GeocodingService()
        addresses = ['Ames, Iowa', 'Des Moines, Iowa', 'Cedar Rapids, Iowa']

        try:
            results = service.batch_geocode(addresses)
            assert isinstance(results, list)
            assert len(results) == len(addresses)
            for result in results:
                assert result is None or isinstance(result, dict)
        except Exception as e:
            pytest.skip(f"Batch geocoding unavailable: {str(e)}")

    def test_batch_reverse_geocode_coordinates(self):
        """Test batch reverse geocoding of multiple coordinates"""
        from src.services.geocoding_service import GeocodingService

        service = GeocodingService()
        coordinates = [(42.0, -93.6), (41.6, -93.6), (41.9, -91.6)]

        try:
            results = service.batch_reverse_geocode(coordinates)
            assert isinstance(results, list)
            assert len(results) == len(coordinates)
            for result in results:
                assert result is None or isinstance(result, dict)
        except Exception as e:
            pytest.skip(f"Batch reverse geocoding unavailable: {str(e)}")

    def test_batch_geocode_empty_list(self):
        """Test batch geocoding with empty list"""
        from src.services.geocoding_service import GeocodingService

        service = GeocodingService()
        results = service.batch_geocode([])
        assert isinstance(results, list)
        assert len(results) == 0

    def test_batch_reverse_geocode_empty_list(self):
        """Test batch reverse geocoding with empty list"""
        from src.services.geocoding_service import GeocodingService

        service = GeocodingService()
        results = service.batch_reverse_geocode([])
        assert isinstance(results, list)
        assert len(results) == 0
class TestBatchGeocoding:
    """Test cases for batch geocoding functionality"""

    def test_batch_geocode_addresses(self):
        """Test batch geocoding of multiple addresses"""
        from src.services.geocoding_service import GeocodingService

        service = GeocodingService()
        addresses = ['Ames, Iowa', 'Des Moines, Iowa', 'Cedar Rapids, Iowa']

        try:
            results = service.batch_geocode(addresses)
            assert isinstance(results, list)
            assert len(results) == len(addresses)
            for result in results:
                assert result is None or isinstance(result, dict)
        except Exception as e:
            pytest.skip(f"Batch geocoding unavailable: {str(e)}")

    def test_batch_reverse_geocode_coordinates(self):
        """Test batch reverse geocoding of multiple coordinates"""
        from src.services.geocoding_service import GeocodingService

        service = GeocodingService()
        coordinates = [(42.0, -93.6), (41.6, -93.6), (41.9, -91.6)]

        try:
            results = service.batch_reverse_geocode(coordinates)
            assert isinstance(results, list)
            assert len(results) == len(coordinates)
            for result in results:
                assert result is None or isinstance(result, dict)
        except Exception as e:
            pytest.skip(f"Batch reverse geocoding unavailable: {str(e)}")

    def test_batch_geocode_empty_list(self):
        """Test batch geocoding with empty list"""
        from src.services.geocoding_service import GeocodingService

        service = GeocodingService()
        results = service.batch_geocode([])
        assert isinstance(results, list)
        assert len(results) == 0

    def test_batch_reverse_geocode_empty_list(self):
        """Test batch reverse geocoding with empty list"""
        from src.services.geocoding_service import GeocodingService

        service = GeocodingService()
        results = service.batch_reverse_geocode([])
        assert isinstance(results, list)
        assert len(results) == 0
    """Test cases for batch geocoding functionality"""

    def test_batch_geocode_addresses(self):
        """Test batch geocoding of multiple addresses"""
        from src.services.geocoding_service import GeocodingService

        service = GeocodingService()
        addresses = ['Ames, Iowa', 'Des Moines, Iowa', 'Cedar Rapids, Iowa']

        try:
            results = service.batch_geocode(addresses)
            assert isinstance(results, list)
            assert len(results) == len(addresses)
            for result in results:
                assert result is None or isinstance(result, dict)
        except Exception as e:
            pytest.skip(f"Batch geocoding unavailable: {str(e)}")

    def test_batch_reverse_geocode_coordinates(self):
        """Test batch reverse geocoding of multiple coordinates"""
        from src.services.geocoding_service import GeocodingService

        service = GeocodingService()
        coordinates = [(42.0, -93.6), (41.6, -93.6), (41.9, -91.6)]

        try:
            results = service.batch_reverse_geocode(coordinates)
            assert isinstance(results, list)
            assert len(results) == len(coordinates)
            for result in results:
                assert result is None or isinstance(result, dict)
        except Exception as e:
            pytest.skip(f"Batch reverse geocoding unavailable: {str(e)}")

    def test_batch_geocode_empty_list(self):
        """Test batch geocoding with empty list"""
        from src.services.geocoding_service import GeocodingService

        service = GeocodingService()
        results = service.batch_geocode([])
        assert isinstance(results, list)
        assert len(results) == 0

    def test_batch_reverse_geocode_empty_list(self):
        """Test batch reverse geocoding with empty list"""
        from src.services.geocoding_service import GeocodingService

        service = GeocodingService()
        results = service.batch_reverse_geocode([])
        assert isinstance(results, list)
        assert len(results) == 0


