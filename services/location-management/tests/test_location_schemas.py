import pytest
from decimal import Decimal
from uuid import uuid4
from pydantic import ValidationError


class TestLocationCreateSchema:
    """Test cases for LocationCreate schema"""
    
    def test_location_create_valid(self):
        """Test creating a valid LocationCreate instance"""
        from src.schemas.location_schemas import LocationCreate
        
        location_data = {
            'name': 'Test Farm',
            'address': '123 Main Street, Ames, Iowa',
            'latitude': 42.0,
            'longitude': -93.6,
            'elevation_meters': 300,
            'usda_zone': '5b',
            'climate_zone': 'Humid Continental',
            'county': 'Story',
            'state': 'Iowa',
            'total_acres': Decimal('100.50'),
        }
        
        location = LocationCreate(**location_data)
        assert location.name == 'Test Farm'
        assert location.latitude == 42.0
        assert location.longitude == -93.6
        assert location.state == 'Iowa'
    
    def test_location_create_minimal_required(self):
        """Test creating LocationCreate with only required fields"""
        from src.schemas.location_schemas import LocationCreate
        
        location_data = {
            'name': 'Test Farm',
            'latitude': 42.0,
            'longitude': -93.6,
        }
        
        location = LocationCreate(**location_data)
        assert location.name == 'Test Farm'
        assert location.latitude == 42.0
        assert location.longitude == -93.6
    
    def test_location_create_with_optional_address(self):
        """Test LocationCreate with optional address field"""
        from src.schemas.location_schemas import LocationCreate
        
        location_data = {
            'name': 'Test Farm',
            'latitude': 42.0,
            'longitude': -93.6,
            'address': 'Ames, Iowa',
        }
        
        location = LocationCreate(**location_data)
        assert location.address == 'Ames, Iowa'


class TestCoordinateValidation:
    """Test cases for coordinate validation"""
    
    def test_valid_latitude_range(self):
        """Test valid latitude values"""
        from src.schemas.location_schemas import LocationCreate
        
        test_cases = [
            {'name': 'North Pole', 'latitude': 90.0, 'longitude': 0.0},
            {'name': 'South Pole', 'latitude': -90.0, 'longitude': 0.0},
            {'name': 'Equator', 'latitude': 0.0, 'longitude': 0.0},
            {'name': 'Iowa', 'latitude': 42.0, 'longitude': -93.6},
        ]
        
        for case in test_cases:
            location = LocationCreate(**case)
            assert -90 <= location.latitude <= 90
    
    def test_valid_longitude_range(self):
        """Test valid longitude values"""
        from src.schemas.location_schemas import LocationCreate
        
        test_cases = [
            {'name': 'Prime Meridian', 'latitude': 0.0, 'longitude': 0.0},
            {'name': 'Date Line', 'latitude': 0.0, 'longitude': 180.0},
            {'name': 'Date Line West', 'latitude': 0.0, 'longitude': -180.0},
            {'name': 'Iowa', 'latitude': 42.0, 'longitude': -93.6},
        ]
        
        for case in test_cases:
            location = LocationCreate(**case)
            assert -180 <= location.longitude <= 180
    
    def test_invalid_latitude_too_high(self):
        """Test that latitude > 90 raises validation error"""
        from src.schemas.location_schemas import LocationCreate
        
        with pytest.raises(ValidationError) as exc_info:
            LocationCreate(
                name='Invalid',
                latitude=91.0,
                longitude=0.0,
            )
        
        assert 'latitude' in str(exc_info.value).lower() or 'constraint' in str(exc_info.value).lower()
    
    def test_invalid_latitude_too_low(self):
        """Test that latitude < -90 raises validation error"""
        from src.schemas.location_schemas import LocationCreate
        
        with pytest.raises(ValidationError) as exc_info:
            LocationCreate(
                name='Invalid',
                latitude=-91.0,
                longitude=0.0,
            )
        
        assert 'latitude' in str(exc_info.value).lower() or 'constraint' in str(exc_info.value).lower()
    
    def test_invalid_longitude_too_high(self):
        """Test that longitude > 180 raises validation error"""
        from src.schemas.location_schemas import LocationCreate
        
        with pytest.raises(ValidationError) as exc_info:
            LocationCreate(
                name='Invalid',
                latitude=0.0,
                longitude=181.0,
            )
        
        assert 'longitude' in str(exc_info.value).lower() or 'constraint' in str(exc_info.value).lower()
    
    def test_invalid_longitude_too_low(self):
        """Test that longitude < -180 raises validation error"""
        from src.schemas.location_schemas import LocationCreate
        
        with pytest.raises(ValidationError) as exc_info:
            LocationCreate(
                name='Invalid',
                latitude=0.0,
                longitude=-181.0,
            )
        
        assert 'longitude' in str(exc_info.value).lower() or 'constraint' in str(exc_info.value).lower()


class TestLocationResponseSchema:
    """Test cases for LocationResponse schema"""
    
    def test_location_response_creation(self):
        """Test creating a LocationResponse instance"""
        from src.schemas.location_schemas import LocationResponse
        
        response_data = {
            'id': str(uuid4()),
            'user_id': str(uuid4()),
            'name': 'Test Farm',
            'latitude': 42.0,
            'longitude': -93.6,
            'state': 'Iowa',
            'country': 'USA',
        }
        
        response = LocationResponse(**response_data)
        assert response.name == 'Test Farm'
        assert response.state == 'Iowa'
    
    def test_location_response_with_all_fields(self):
        """Test LocationResponse with all optional fields"""
        from src.schemas.location_schemas import LocationResponse
        
        response_data = {
            'id': str(uuid4()),
            'user_id': str(uuid4()),
            'name': 'Test Farm',
            'address': '123 Main Street',
            'latitude': 42.0,
            'longitude': -93.6,
            'elevation_meters': 300,
            'usda_zone': '5b',
            'climate_zone': 'Humid Continental',
            'county': 'Story',
            'state': 'Iowa',
            'country': 'USA',
            'total_acres': 100.50,
            'is_primary': True,
        }
        
        response = LocationResponse(**response_data)
        assert response.address == '123 Main Street'
        assert response.elevation_meters == 300
        assert response.is_primary is True


class TestNearbySearchRequestSchema:
    """Test cases for NearbySearchRequest schema"""
    
    def test_nearby_search_valid(self):
        """Test creating a valid NearbySearchRequest"""
        from src.schemas.location_schemas import NearbySearchRequest
        
        search_data = {
            'latitude': 42.0,
            'longitude': -93.6,
            'radius_km': 50.0,
        }
        
        request = NearbySearchRequest(**search_data)
        assert request.latitude == 42.0
        assert request.longitude == -93.6
        assert request.radius_km == 50.0
    
    def test_nearby_search_default_radius(self):
        """Test NearbySearchRequest with default radius"""
        from src.schemas.location_schemas import NearbySearchRequest
        
        search_data = {
            'latitude': 42.0,
            'longitude': -93.6,
        }
        
        request = NearbySearchRequest(**search_data)
        assert request.latitude == 42.0
        assert request.longitude == -93.6
        assert request.radius_km == 50.0
    
    def test_nearby_search_coordinate_validation(self):
        """Test NearbySearchRequest coordinate validation"""
        from src.schemas.location_schemas import NearbySearchRequest
        
        with pytest.raises(ValidationError):
            NearbySearchRequest(
                latitude=91.0,
                longitude=-93.6,
                radius_km=50.0,
            )
    
    def test_nearby_search_radius_min(self):
        """Test NearbySearchRequest with minimum radius"""
        from src.schemas.location_schemas import NearbySearchRequest
        
        request = NearbySearchRequest(
            latitude=42.0,
            longitude=-93.6,
            radius_km=1.0,
        )
        assert request.radius_km == 1.0
    
    def test_nearby_search_radius_max(self):
        """Test NearbySearchRequest with maximum radius"""
        from src.schemas.location_schemas import NearbySearchRequest
        
        request = NearbySearchRequest(
            latitude=42.0,
            longitude=-93.6,
            radius_km=500.0,
        )
        assert request.radius_km == 500.0


class TestFieldSchema:
    """Test cases for Field-related schemas"""
    
    def test_field_create_valid(self):
        """Test creating a valid FieldCreate schema"""
        from src.schemas.location_schemas import FieldCreate
        
        field_data = {
            'farm_location_id': str(uuid4()),
            'name': 'North Field',
            'acres': Decimal('25.75'),
            'soil_type': 'Loam',
            'drainage_class': 'Well Drained',
            'slope_percent': Decimal('2.5'),
            'irrigation_available': True,
        }
        
        field = FieldCreate(**field_data)
        assert field.name == 'North Field'
        assert field.acres == Decimal('25.75')
    
    def test_field_create_minimal(self):
        """Test FieldCreate with minimal required fields"""
        from src.schemas.location_schemas import FieldCreate
        
        field_data = {
            'farm_location_id': str(uuid4()),
            'name': 'Test Field',
            'acres': Decimal('10.0'),
        }
        
        field = FieldCreate(**field_data)
        assert field.name == 'Test Field'
        assert field.acres == Decimal('10.0')


class TestSchemaIntegration:
    """Integration tests for schemas"""
    
    def test_location_create_then_response(self):
        """Test creating LocationCreate and converting to LocationResponse"""
        from src.schemas.location_schemas import LocationCreate, LocationResponse
        
        create_data = {
            'name': 'Test Farm',
            'latitude': 42.0,
            'longitude': -93.6,
            'state': 'Iowa',
            'country': 'USA',
        }
        
        created = LocationCreate(**create_data)
        
        response_data = {
            'id': str(uuid4()),
            'user_id': str(uuid4()),
            **create_data,
        }
        
        response = LocationResponse(**response_data)
        assert response.name == created.name
        assert response.latitude == created.latitude
        assert response.longitude == created.longitude
    
    def test_multiple_schemas_compatibility(self):
        """Test that schemas work together coherently"""
        from src.schemas.location_schemas import LocationCreate, NearbySearchRequest
        
        location = LocationCreate(
            name='Test',
            latitude=42.0,
            longitude=-93.6,
        )
        
        search = NearbySearchRequest(
            latitude=location.latitude,
            longitude=location.longitude,
            radius_km=50.0,
        )
        
        assert location.latitude == search.latitude
        assert location.longitude == search.longitude
