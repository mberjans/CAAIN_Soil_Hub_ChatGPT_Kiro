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
class TestLocationRoutesErrorHandling:
    """Test cases for error handling in location routes"""

    def test_create_location_with_invalid_data(self, client):
        """Test POST endpoint with invalid data types"""
        payload = {
            'name': 123,  # Should be string
            'latitude': 'invalid',
            'longitude': 'invalid'
        }

        response = client.post('/api/v1/locations/', json=payload)
        assert response.status_code in [400, 422]

    def test_nearby_locations_with_invalid_params(self, client):
        """Test nearby endpoint with invalid parameters"""
        response = client.get(
            '/api/v1/locations/nearby',
            params={'latitude': 'abc', 'longitude': 'def', 'radius_km': -10}
        )

        assert response.status_code in [400, 422]

    def test_get_location_with_invalid_uuid(self, client):
        """Test GET endpoint with invalid UUID"""
        response = client.get('/api/v1/locations/invalid-uuid')

        assert response.status_code in [400, 422]

    def test_create_location_with_extreme_coordinates(self, client):
        """Test endpoint with extreme coordinate values"""
        payload = {
            'name': 'Extreme Location',
            'latitude': 91.0,  # Invalid latitude
            'longitude': -93.6
        }

        response = client.post('/api/v1/locations/', json=payload)
        assert response.status_code in [400, 422]

    def test_nearby_locations_with_large_radius(self, client):
        """Test nearby endpoint with very large radius"""
        response = client.get(
            '/api/v1/locations/nearby',
            params={'latitude': 42.0, 'longitude': -93.6, 'radius_km': 10000}
        )

        assert response.status_code in [200, 422]
class TestLocationRoutesErrorHandling:
    """Test cases for error handling in location routes"""

    def test_create_location_with_invalid_data(self, client):
        """Test POST endpoint with invalid data types"""
        payload = {
            'name': 123,  # Should be string
            'latitude': 'invalid',
            'longitude': 'invalid'
        }

        response = client.post('/api/v1/locations/', json=payload)
        assert response.status_code in [400, 422]

    def test_nearby_locations_with_invalid_params(self, client):
        """Test nearby endpoint with invalid parameters"""
        response = client.get(
            '/api/v1/locations/nearby',
            params={'latitude': 'abc', 'longitude': 'def', 'radius_km': -10}
        )

        assert response.status_code in [400, 422]

    def test_get_location_with_invalid_uuid(self, client):
        """Test GET endpoint with invalid UUID"""
        response = client.get('/api/v1/locations/invalid-uuid')

        assert response.status_code in [400, 422]

    def test_create_location_with_extreme_coordinates(self, client):
        """Test endpoint with extreme coordinate values"""
        payload = {
            'name': 'Extreme Location',
            'latitude': 91.0,  # Invalid latitude
            'longitude': -93.6
        }

        response = client.post('/api/v1/locations/', json=payload)
        assert response.status_code in [400, 422]

    def test_nearby_locations_with_large_radius(self, client):
        """Test nearby endpoint with very large radius"""
        response = client.get(
            '/api/v1/locations/nearby',
            params={'latitude': 42.0, 'longitude': -93.6, 'radius_km': 10000}
        )

        assert response.status_code in [200, 422]
    """Test cases for error handling in location routes"""

    def test_create_location_with_invalid_data(self, client):
        """Test POST endpoint with invalid data types"""
        payload = {
            'name': 123,  # Should be string
            'latitude': 'invalid',
            'longitude': 'invalid'
        }

        response = client.post('/api/v1/locations/', json=payload)
        assert response.status_code in [400, 422]

    def test_nearby_locations_with_invalid_params(self, client):
        """Test nearby endpoint with invalid parameters"""
        response = client.get(
            '/api/v1/locations/nearby',
            params={'latitude': 'abc', 'longitude': 'def', 'radius_km': -10}
        )

        assert response.status_code in [400, 422]

    def test_get_location_with_invalid_uuid(self, client):
        """Test GET endpoint with invalid UUID"""
        response = client.get('/api/v1/locations/invalid-uuid')

        assert response.status_code in [400, 422]

    def test_create_location_with_extreme_coordinates(self, client):
        """Test endpoint with extreme coordinate values"""
        payload = {
            'name': 'Extreme Location',
            'latitude': 91.0,  # Invalid latitude
            'longitude': -93.6
        }

        response = client.post('/api/v1/locations/', json=payload)
        assert response.status_code in [400, 422]

    def test_nearby_locations_with_large_radius(self, client):
        """Test nearby endpoint with very large radius"""
        response = client.get(
            '/api/v1/locations/nearby',
            params={'latitude': 42.0, 'longitude': -93.6, 'radius_km': 10000}
        )

        assert response.status_code in [200, 422]

    """Test cases for error handling in location routes"""

    def test_create_location_with_invalid_data(self, client):
        """Test POST endpoint with invalid data types"""
        payload = {
            'name': 123,  # Should be string
            'latitude': 'invalid',
            'longitude': 'invalid'
        }

        response = client.post('/api/v1/locations/', json=payload)
        assert response.status_code in [400, 422]

    def test_nearby_locations_with_invalid_params(self, client):
        """Test nearby endpoint with invalid parameters"""
        response = client.get(
            '/api/v1/locations/nearby',
            params={'latitude': 'abc', 'longitude': 'def', 'radius_km': -10}
        )

        assert response.status_code in [400, 422]

    def test_get_location_with_invalid_uuid(self, client):
        """Test GET endpoint with invalid UUID"""
        response = client.get('/api/v1/locations/invalid-uuid')

        assert response.status_code in [400, 422]

    def test_create_location_with_extreme_coordinates(self, client):
        """Test endpoint with extreme coordinate values"""
        payload = {
            'name': 'Extreme Location',
            'latitude': 91.0,  # Invalid latitude
            'longitude': -93.6
        }

        response = client.post('/api/v1/locations/', json=payload)
        assert response.status_code in [400, 422]

    def test_nearby_locations_with_large_radius(self, client):
        """Test nearby endpoint with very large radius"""
        response = client.get(
            '/api/v1/locations/nearby',
            params={'latitude': 42.0, 'longitude': -93.6, 'radius_km': 10000}
        )

        assert response.status_code in [200, 422]
class TestLocationRoutesErrorHandling:
    """Test cases for error handling in location routes"""

    def test_create_location_with_invalid_data(self, client):
        """Test POST endpoint with invalid data types"""
        payload = {
            'name': 123,  # Should be string
            'latitude': 'invalid',
            'longitude': 'invalid'
        }

        response = client.post('/api/v1/locations/', json=payload)
        assert response.status_code in [400, 422]

    def test_nearby_locations_with_invalid_params(self, client):
        """Test nearby endpoint with invalid parameters"""
        response = client.get(
            '/api/v1/locations/nearby',
            params={'latitude': 'abc', 'longitude': 'def', 'radius_km': -10}
        )

        assert response.status_code in [400, 422]

    def test_get_location_with_invalid_uuid(self, client):
        """Test GET endpoint with invalid UUID"""
        response = client.get('/api/v1/locations/invalid-uuid')

        assert response.status_code in [400, 422]

    def test_create_location_with_extreme_coordinates(self, client):
        """Test endpoint with extreme coordinate values"""
        payload = {
            'name': 'Extreme Location',
            'latitude': 91.0,  # Invalid latitude
            'longitude': -93.6
        }

        response = client.post('/api/v1/locations/', json=payload)
        assert response.status_code in [400, 422]

    def test_nearby_locations_with_large_radius(self, client):
        """Test nearby endpoint with very large radius"""
        response = client.get(
            '/api/v1/locations/nearby',
            params={'latitude': 42.0, 'longitude': -93.6, 'radius_km': 10000}
        )

        assert response.status_code in [200, 422]
    """Test cases for error handling in location routes"""

    def test_create_location_with_invalid_data(self, client):
        """Test POST endpoint with invalid data types"""
        payload = {
            'name': 123,  # Should be string
            'latitude': 'invalid',
            'longitude': 'invalid'
        }

        response = client.post('/api/v1/locations/', json=payload)
        assert response.status_code in [400, 422]

    def test_nearby_locations_with_invalid_params(self, client):
        """Test nearby endpoint with invalid parameters"""
        response = client.get(
            '/api/v1/locations/nearby',
            params={'latitude': 'abc', 'longitude': 'def', 'radius_km': -10}
        )

        assert response.status_code in [400, 422]

    def test_get_location_with_invalid_uuid(self, client):
        """Test GET endpoint with invalid UUID"""
        response = client.get('/api/v1/locations/invalid-uuid')

        assert response.status_code in [400, 422]

    def test_create_location_with_extreme_coordinates(self, client):
        """Test endpoint with extreme coordinate values"""
        payload = {
            'name': 'Extreme Location',
            'latitude': 91.0,  # Invalid latitude
            'longitude': -93.6
        }

        response = client.post('/api/v1/locations/', json=payload)
        assert response.status_code in [400, 422]

    def test_nearby_locations_with_large_radius(self, client):
        """Test nearby endpoint with very large radius"""
        response = client.get(
            '/api/v1/locations/nearby',
            params={'latitude': 42.0, 'longitude': -93.6, 'radius_km': 10000}
        )

        assert response.status_code in [200, 422]


