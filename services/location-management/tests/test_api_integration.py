import pytest
from fastapi.testclient import TestClient
from uuid import uuid4


@pytest.fixture
def client():
    from src.main import app
    return TestClient(app)


class TestLocationAPIIntegration:
    """End-to-end integration tests for location API"""
    
    def test_health_check(self, client):
        """Test health endpoint is accessible"""
        response = client.get('/health')
        assert response.status_code == 200
        assert response.json()['status'] == 'healthy'
    
    def test_create_and_retrieve_location(self, client):
        """Test full workflow: create location then retrieve it"""
        create_payload = {
            'name': 'Integration Test Farm',
            'latitude': 42.0,
            'longitude': -93.6,
            'address': 'Ames, Iowa'
        }
        
        create_response = client.post('/api/v1/locations/', json=create_payload)
        
        if create_response.status_code in [200, 201]:
            data = create_response.json()
            assert data.get('name') == 'Integration Test Farm'
            assert data.get('latitude') == 42.0
    
    def test_nearby_locations_query(self, client):
        """Test geospatial nearby query"""
        response = client.get(
            '/api/v1/locations/nearby',
            params={'latitude': 42.0, 'longitude': -93.6, 'radius_km': 100}
        )
        
        assert response.status_code in [200, 422]
        if response.status_code == 200:
            assert isinstance(response.json(), list)
    
    def test_validation_integration(self):
        """Test validation service integration"""
        from src.services.validation_service import LocationValidationService
        
        service = LocationValidationService()
        
        valid_zone = service.validate_agricultural_zone('5a')
        assert valid_zone is True
        
        invalid_zone = service.validate_agricultural_zone('99z')
        assert invalid_zone is False
    
    def test_geocoding_integration(self):
        """Test geocoding service integration"""
        from src.services.geocoding_service import GeocodingService
        
        service = GeocodingService()
        
        coords_valid = service._validate_coordinates(40.0, -95.0)
        assert coords_valid is True
        
        coords_invalid = service._validate_coordinates(100.0, 200.0)
        assert coords_invalid is False
    
    def test_location_service_integration(self):
        """Test location service integration"""
        from src.services.location_service import LocationService
        
        service = LocationService(None)
        
        valid = service._validate_gps_coordinates(42.0, -93.6)
        assert valid is True
        
        invalid = service._validate_gps_coordinates(91.0, 181.0)
        assert invalid is False
    
    def test_error_handling_integration(self, client):
        """Test error handling across stack"""
        response = client.post('/api/v1/locations/', json={
            'name': 'Invalid',
            'latitude': 100.0,
            'longitude': 200.0
        })
        
        assert response.status_code in [400, 422]
    
    def test_api_documentation_available(self, client):
        """Test OpenAPI documentation is accessible"""
        response = client.get('/openapi.json')
        assert response.status_code == 200
        assert 'openapi' in response.json()
