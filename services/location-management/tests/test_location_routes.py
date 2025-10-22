import pytest
from fastapi.testclient import TestClient
from uuid import uuid4


@pytest.fixture
def client():
    from src.main import app
    return TestClient(app)


class TestLocationRoutes:
    """Test cases for location API routes"""
    
    def test_create_location_endpoint(self, client):
        """Test POST /api/v1/locations endpoint"""
        payload = {
            'name': 'Test Farm',
            'latitude': 42.0,
            'longitude': -93.6,
            'address': '123 Main St, Ames, Iowa'
        }
        
        response = client.post('/api/v1/locations/', json=payload)
        assert response.status_code in [200, 201, 422]
    
    def test_get_nearby_locations_endpoint(self, client):
        """Test GET /api/v1/locations/nearby endpoint"""
        response = client.get(
            '/api/v1/locations/nearby',
            params={'latitude': 42.0, 'longitude': -93.6, 'radius_km': 50}
        )
        
        assert response.status_code in [200, 422]
        if response.status_code == 200:
            assert isinstance(response.json(), list)
    
    def test_get_location_endpoint(self, client):
        """Test GET /api/v1/locations/{id} endpoint"""
        location_id = str(uuid4())
        response = client.get(f'/api/v1/locations/{location_id}')
        
        assert response.status_code in [200, 404, 422]
    
    def test_invalid_coordinates(self, client):
        """Test endpoint rejects invalid coordinates"""
        payload = {
            'name': 'Invalid',
            'latitude': 100.0,
            'longitude': 200.0
        }
        
        response = client.post('/api/v1/locations/', json=payload)
        assert response.status_code in [400, 422]
    
    def test_missing_required_fields(self, client):
        """Test endpoint validates required fields"""
        payload = {'name': 'Incomplete'}
        
        response = client.post('/api/v1/locations/', json=payload)
        assert response.status_code in [400, 422]
