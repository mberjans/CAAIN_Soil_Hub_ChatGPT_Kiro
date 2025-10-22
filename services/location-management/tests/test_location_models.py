import pytest
from uuid import uuid4
from datetime import datetime
from decimal import Decimal
from geoalchemy2.elements import WKTElement
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


pytest_plugins = ('pytest_asyncio',)


@pytest.fixture(scope='function')
def db_engine():
    db_url = 'postgresql://Mark@localhost:5432/caain_soil_hub'
    engine = create_engine(db_url, echo=False)
    return engine


@pytest.fixture(scope='function')
def db_session(db_engine):
    Session = sessionmaker(bind=db_engine)
    session = Session()
    
    yield session
    
    session.close()


class TestFarmLocationModel:
    """Test cases for FarmLocation model"""
    
    def test_farm_location_creation(self, db_session):
        """Test creating a FarmLocation instance"""
        from src.models.location_models import FarmLocation
        
        user_id = uuid4()
        farm_id = uuid4()
        
        farm = FarmLocation(
            id=farm_id,
            user_id=user_id,
            name='Test Farm',
            address='123 Main Street, Ames, Iowa',
            coordinates=WKTElement('POINT(-93.6 42.0)', srid=4326),
            elevation_meters=300,
            usda_zone='5b',
            climate_zone='Humid Continental',
            county='Story',
            state='Iowa',
            country='USA',
            total_acres=Decimal('100.50'),
            is_primary=True,
        )
        
        db_session.add(farm)
        db_session.commit()
        
        retrieved = db_session.query(FarmLocation).filter_by(id=farm_id).first()
        assert retrieved is not None
        assert retrieved.name == 'Test Farm'
        assert retrieved.user_id == user_id
        assert retrieved.state == 'Iowa'
        assert retrieved.is_primary is True
    
    def test_farm_location_required_fields(self):
        """Test that FarmLocation requires essential fields"""
        from src.models.location_models import FarmLocation
        
        farm = FarmLocation(
            user_id=uuid4(),
            name='Test Farm',
            coordinates=WKTElement('POINT(-93.6 42.0)', srid=4326),
        )
        
        assert farm.user_id is not None
        assert farm.name == 'Test Farm'
        assert farm.coordinates is not None
    
    def test_farm_location_default_values(self, db_session):
        """Test default values for FarmLocation after database insertion"""
        from src.models.location_models import FarmLocation
        
        user_id = uuid4()
        farm = FarmLocation(
            user_id=user_id,
            name='Test Farm',
            coordinates=WKTElement('POINT(-93.6 42.0)', srid=4326),
        )
        
        db_session.add(farm)
        db_session.commit()
        
        retrieved = db_session.query(FarmLocation).filter_by(user_id=user_id).first()
        assert retrieved.country == 'USA'
        assert retrieved.is_primary is False
    
    def test_farm_location_timestamps(self, db_session):
        """Test that created_at and updated_at timestamps are set"""
        from src.models.location_models import FarmLocation
        
        user_id = uuid4()
        farm = FarmLocation(
            user_id=user_id,
            name='Test Farm',
            coordinates=WKTElement('POINT(-93.6 42.0)', srid=4326),
        )
        
        db_session.add(farm)
        db_session.commit()
        
        retrieved = db_session.query(FarmLocation).filter_by(user_id=user_id).first()
        assert retrieved.created_at is not None
        assert retrieved.updated_at is not None


class TestFieldModel:
    """Test cases for Field model"""
    
    def test_field_creation(self, db_session):
        """Test creating a Field instance"""
        from src.models.location_models import FarmLocation, Field
        
        user_id = uuid4()
        farm_id = uuid4()
        field_id = uuid4()
        
        farm = FarmLocation(
            id=farm_id,
            user_id=user_id,
            name='Test Farm',
            coordinates=WKTElement('POINT(-93.6 42.0)', srid=4326),
        )
        
        db_session.add(farm)
        db_session.commit()
        
        polygon_wkt = 'POLYGON((-93.6 42.0, -93.5 42.0, -93.5 42.1, -93.6 42.1, -93.6 42.0))'
        
        field = Field(
            id=field_id,
            farm_location_id=farm_id,
            name='North Field',
            boundary=WKTElement(polygon_wkt, srid=4326),
            acres=Decimal('25.75'),
            soil_type='Loam',
            drainage_class='Well Drained',
            slope_percent=Decimal('2.5'),
            irrigation_available=True,
        )
        
        db_session.add(field)
        db_session.commit()
        
        retrieved = db_session.query(Field).filter_by(id=field_id).first()
        assert retrieved is not None
        assert retrieved.name == 'North Field'
        assert retrieved.farm_location_id == farm_id
        assert retrieved.acres == Decimal('25.75')
        assert retrieved.irrigation_available is True
    
    def test_field_required_fields(self):
        """Test that Field requires essential fields"""
        from src.models.location_models import Field
        
        field = Field(
            farm_location_id=uuid4(),
            name='Test Field',
            acres=Decimal('10.0'),
        )
        
        assert field.farm_location_id is not None
        assert field.name == 'Test Field'
        assert field.acres == Decimal('10.0')
    
    def test_field_default_values(self, db_session):
        """Test default values for Field after database insertion"""
        from src.models.location_models import FarmLocation, Field
        
        user_id = uuid4()
        farm_id = uuid4()
        
        farm = FarmLocation(
            id=farm_id,
            user_id=user_id,
            name='Test Farm',
            coordinates=WKTElement('POINT(-93.6 42.0)', srid=4326),
        )
        
        db_session.add(farm)
        db_session.commit()
        
        field = Field(
            farm_location_id=farm_id,
            name='Test Field',
            acres=Decimal('10.0'),
        )
        
        db_session.add(field)
        db_session.commit()
        
        retrieved = db_session.query(Field).filter_by(farm_location_id=farm_id).first()
        assert retrieved.irrigation_available is False
    
    def test_field_polygon_geometry(self):
        """Test that Field can store POLYGON geometry"""
        from src.models.location_models import Field
        
        polygon_wkt = 'POLYGON((-93.6 42.0, -93.5 42.0, -93.5 42.1, -93.6 42.1, -93.6 42.0))'
        
        field = Field(
            farm_location_id=uuid4(),
            name='Test Field',
            boundary=WKTElement(polygon_wkt, srid=4326),
            acres=Decimal('10.0'),
        )
        
        assert field.boundary is not None
    
    def test_field_timestamps(self, db_session):
        """Test that created_at and updated_at timestamps are set"""
        from src.models.location_models import FarmLocation, Field
        
        user_id = uuid4()
        farm_id = uuid4()
        field_id = uuid4()
        
        farm = FarmLocation(
            id=farm_id,
            user_id=user_id,
            name='Test Farm',
            coordinates=WKTElement('POINT(-93.6 42.0)', srid=4326),
        )
        
        db_session.add(farm)
        db_session.commit()
        
        field = Field(
            id=field_id,
            farm_location_id=farm_id,
            name='Test Field',
            acres=Decimal('10.0'),
        )
        
        db_session.add(field)
        db_session.commit()
        
        retrieved = db_session.query(Field).filter_by(id=field_id).first()
        assert retrieved.created_at is not None
        assert retrieved.updated_at is not None


class TestFarmLocationFieldRelationship:
    """Test cases for FarmLocation and Field relationships"""
    
    def test_farm_has_many_fields(self, db_session):
        """Test that a FarmLocation can have multiple Fields"""
        from src.models.location_models import FarmLocation, Field
        
        user_id = uuid4()
        farm_id = uuid4()
        
        farm = FarmLocation(
            id=farm_id,
            user_id=user_id,
            name='Test Farm',
            coordinates=WKTElement('POINT(-93.6 42.0)', srid=4326),
        )
        
        db_session.add(farm)
        db_session.commit()
        
        field1 = Field(
            farm_location_id=farm_id,
            name='North Field',
            acres=Decimal('25.0'),
        )
        
        field2 = Field(
            farm_location_id=farm_id,
            name='South Field',
            acres=Decimal('30.0'),
        )
        
        db_session.add(field1)
        db_session.add(field2)
        db_session.commit()
        
        retrieved_farm = db_session.query(FarmLocation).filter_by(id=farm_id).first()
        assert len(retrieved_farm.fields) == 2
    
    def test_field_belongs_to_farm(self, db_session):
        """Test that a Field belongs to a FarmLocation"""
        from src.models.location_models import FarmLocation, Field
        
        user_id = uuid4()
        farm_id = uuid4()
        
        farm = FarmLocation(
            id=farm_id,
            user_id=user_id,
            name='Test Farm',
            coordinates=WKTElement('POINT(-93.6 42.0)', srid=4326),
        )
        
        db_session.add(farm)
        db_session.commit()
        
        field = Field(
            farm_location_id=farm_id,
            name='Test Field',
            acres=Decimal('10.0'),
        )
        
        db_session.add(field)
        db_session.commit()
        
        retrieved_field = db_session.query(Field).filter_by(farm_location_id=farm_id).first()
        assert retrieved_field is not None
        assert retrieved_field.farm_location_id == farm_id
