# Parallel Job 4: Farm Location Services

**TICKET-008: Location Management API Endpoints**  
**Estimated Timeline**: 2-3 weeks  
**Priority**: Critical  
**Can Start**: Immediately (No blocking dependencies)

## Executive Summary

This job implements comprehensive farm location management including GPS coordinate validation, address geocoding, field boundary management, and geospatial queries using PostGIS. This work is **completely independent** of other parallel jobs.

## Related Tickets from Checklist

- **TICKET-008_farm-location-input-4.1**: Create location management API endpoints
- **TICKET-008_farm-location-input-4.2**: Implement GPS coordinate validation
- **TICKET-008_farm-location-input-4.3**: Add address geocoding with fallback providers
- **TICKET-008_farm-location-input-4.4**: Create geospatial query capabilities
- **TICKET-008_farm-location-input-5.1**: Implement field boundary management
- **TICKET-008_farm-location-input-5.2**: Add location validation against agricultural zones

## Technical Stack

```yaml
Languages: Python 3.11+
Framework: FastAPI
Database: PostgreSQL with PostGIS extension
ORM: SQLAlchemy 2.0+ with GeoAlchemy2
Geocoding: geopy (Google Maps, OpenStreetMap)
Validation: Pydantic v2 with custom validators
Testing: pytest, pytest-asyncio
```

## Service Architecture

**Service Location**: `services/location-management/`  
**Port**: 8009 (new service)  
**Reference Pattern**: Follow `services/recommendation-engine/` structure

```
services/location-management/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── location_models.py
│   │   └── field_models.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── location_service.py
│   │   ├── geocoding_service.py
│   │   ├── validation_service.py
│   │   └── geospatial_service.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── location_routes.py
│   │   └── field_routes.py
│   └── schemas/
│       ├── __init__.py
│       ├── location_schemas.py
│       └── field_schemas.py
├── tests/
│   ├── __init__.py
│   ├── test_location_service.py
│   ├── test_geocoding.py
│   └── test_api.py
├── requirements.txt
└── README.md
```

## Week 1: Database & Core Services (Days 1-7)

### Day 1: Setup and Dependencies

**requirements.txt**:
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
geoalchemy2==0.14.2
psycopg2-binary==2.9.9
pydantic==2.5.0
geopy==2.4.0
shapely==2.0.2
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.1
```

**Setup Commands**:
```bash
mkdir -p services/location-management/src/{models,services,api,schemas}
mkdir -p services/location-management/tests
cd services/location-management
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Enable PostGIS extension in PostgreSQL
psql -U postgres -d caain_soil_hub -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

### Day 2-3: Database Schema with PostGIS

**File**: `services/location-management/src/models/location_models.py`

```python
from sqlalchemy import Column, String, Integer, DECIMAL, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class FarmLocation(Base):
    """Farm location with geospatial data"""
    __tablename__ = 'farm_locations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String(200), nullable=False)
    address = Column(String(500))
    
    # PostGIS geometry column (POINT with SRID 4326 = WGS84)
    coordinates = Column(Geometry('POINT', srid=4326), nullable=False)
    
    elevation_meters = Column(Integer)
    usda_zone = Column(String(10))
    climate_zone = Column(String(50))
    county = Column(String(100))
    state = Column(String(50))
    country = Column(String(50), default='USA')
    total_acres = Column(DECIMAL(10, 2))
    is_primary = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    fields = relationship("Field", back_populates="farm_location", cascade="all, delete-orphan")

class Field(Base):
    """Individual field within a farm"""
    __tablename__ = 'fields'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_location_id = Column(UUID(as_uuid=True), ForeignKey('farm_locations.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(200), nullable=False)
    
    # PostGIS geometry column (POLYGON)
    boundary = Column(Geometry('POLYGON', srid=4326))
    
    acres = Column(DECIMAL(8, 2), nullable=False)
    soil_type = Column(String(100))
    drainage_class = Column(String(50))
    slope_percent = Column(DECIMAL(4, 1))
    irrigation_available = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    farm_location = relationship("FarmLocation", back_populates="fields")
```

**Database Migration SQL**:
```sql
-- Ensure PostGIS extension is enabled
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create farm_locations table
CREATE TABLE IF NOT EXISTS farm_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    name VARCHAR(200) NOT NULL,
    address TEXT,
    coordinates GEOMETRY(POINT, 4326) NOT NULL,
    elevation_meters INTEGER,
    usda_zone VARCHAR(10),
    climate_zone VARCHAR(50),
    county VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(50) DEFAULT 'USA',
    total_acres DECIMAL(10,2),
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create spatial index on coordinates
CREATE INDEX idx_farm_locations_coordinates ON farm_locations USING GIST(coordinates);
CREATE INDEX idx_farm_locations_user_id ON farm_locations(user_id);
CREATE INDEX idx_farm_locations_usda_zone ON farm_locations(usda_zone);

-- Create fields table
CREATE TABLE IF NOT EXISTS fields (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    farm_location_id UUID REFERENCES farm_locations(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    boundary GEOMETRY(POLYGON, 4326),
    acres DECIMAL(8,2) NOT NULL,
    soil_type VARCHAR(100),
    drainage_class VARCHAR(50),
    slope_percent DECIMAL(4,1),
    irrigation_available BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create spatial index on field boundaries
CREATE INDEX idx_fields_boundary ON fields USING GIST(boundary);
CREATE INDEX idx_fields_farm_location_id ON fields(farm_location_id);
```

### Day 4-5: Geocoding Service

**File**: `services/location-management/src/services/geocoding_service.py`

```python
from geopy.geocoders import GoogleV3, Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class GeocodingService:
    """Address geocoding with fallback providers (TICKET-008_farm-location-input-4.3)"""
    
    def __init__(self):
        self.geocoders = [
            Nominatim(user_agent="caain_soil_hub"),  # Free, no API key needed
            # GoogleV3(api_key="YOUR_API_KEY"),  # Enable for production
        ]
    
    async def geocode_address(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Convert address to coordinates with fallback
        
        Returns:
            {
                "latitude": float,
                "longitude": float,
                "formatted_address": str,
                "county": str,
                "state": str,
                "country": str,
                "source": str
            }
        """
        for geocoder in self.geocoders:
            try:
                location = geocoder.geocode(address, timeout=10)
                
                if location:
                    # Extract address components
                    result = {
                        "latitude": location.latitude,
                        "longitude": location.longitude,
                        "formatted_address": location.address,
                        "source": geocoder.__class__.__name__
                    }
                    
                    # Parse address components
                    if hasattr(location, 'raw'):
                        raw = location.raw
                        if 'address' in raw:
                            addr = raw['address']
                            result["county"] = addr.get('county', '')
                            result["state"] = addr.get('state', '')
                            result["country"] = addr.get('country', 'USA')
                    
                    logger.info(f"Geocoded address using {geocoder.__class__.__name__}")
                    return result
                    
            except (GeocoderTimedOut, GeocoderServiceError) as e:
                logger.warning(f"Geocoder {geocoder.__class__.__name__} failed: {e}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error in geocoding: {e}")
                continue
        
        logger.error(f"All geocoders failed for address: {address}")
        return None
    
    async def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """Convert coordinates to address"""
        for geocoder in self.geocoders:
            try:
                location = geocoder.reverse(f"{latitude}, {longitude}", timeout=10)
                
                if location:
                    return {
                        "address": location.address,
                        "latitude": latitude,
                        "longitude": longitude,
                        "source": geocoder.__class__.__name__
                    }
                    
            except Exception as e:
                logger.warning(f"Reverse geocoding failed with {geocoder.__class__.__name__}: {e}")
                continue
        
        return None
```

### Day 6-7: Location Service with Validation

**File**: `services/location-management/src/services/location_service.py`

```python
from sqlalchemy.orm import Session
from geoalchemy2.functions import ST_MakePoint, ST_Distance, ST_DWithin
from geoalchemy2.elements import WKTElement
from typing import List, Dict, Any, Optional
from uuid import UUID
from ..models.location_models import FarmLocation, Field
from ..schemas.location_schemas import LocationCreate, LocationUpdate
from .geocoding_service import GeocodingService
from .validation_service import LocationValidationService

class LocationService:
    """Farm location management (TICKET-008_farm-location-input-4.1)"""
    
    def __init__(self, db: Session):
        self.db = db
        self.geocoding_service = GeocodingService()
        self.validation_service = LocationValidationService()
    
    async def create_location(self, user_id: UUID, location_data: LocationCreate) -> FarmLocation:
        """Create new farm location with validation"""
        
        # If address provided but no coordinates, geocode
        if location_data.address and not location_data.coordinates:
            geocode_result = await self.geocoding_service.geocode_address(location_data.address)
            if geocode_result:
                location_data.coordinates = {
                    "latitude": geocode_result["latitude"],
                    "longitude": geocode_result["longitude"]
                }
                location_data.county = geocode_result.get("county")
                location_data.state = geocode_result.get("state")
        
        # Validate coordinates
        if not location_data.coordinates:
            raise ValueError("Either address or coordinates must be provided")
        
        lat = location_data.coordinates["latitude"]
        lng = location_data.coordinates["longitude"]
        
        # Validate agricultural suitability
        validation = await self.validation_service.validate_agricultural_location(lat, lng)
        if not validation["valid"]:
            raise ValueError(f"Location validation failed: {validation['issues']}")
        
        # Create PostGIS point
        point = WKTElement(f'POINT({lng} {lat})', srid=4326)
        
        # Create database record
        db_location = FarmLocation(
            user_id=user_id,
            name=location_data.name,
            address=location_data.address,
            coordinates=point,
            total_acres=location_data.total_acres,
            county=location_data.county,
            state=location_data.state,
            usda_zone=validation.get("usda_zone"),
            climate_zone=validation.get("climate_zone")
        )
        
        self.db.add(db_location)
        self.db.commit()
        self.db.refresh(db_location)
        
        return db_location
    
    async def get_user_locations(self, user_id: UUID, include_fields: bool = False) -> List[FarmLocation]:
        """Get all locations for a user"""
        query = self.db.query(FarmLocation).filter(FarmLocation.user_id == user_id)
        
        if include_fields:
            query = query.options(joinedload(FarmLocation.fields))
        
        return query.all()
    
    async def find_nearby_locations(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 50
    ) -> List[Dict[str, Any]]:
        """Find farm locations within radius (geospatial query)"""
        
        # Create point for query
        point = WKTElement(f'POINT({longitude} {latitude})', srid=4326)
        
        # Query using PostGIS ST_DWithin (distance in meters)
        radius_meters = radius_km * 1000
        
        results = self.db.query(
            FarmLocation,
            ST_Distance(FarmLocation.coordinates, point).label('distance')
        ).filter(
            ST_DWithin(FarmLocation.coordinates, point, radius_meters)
        ).order_by('distance').all()
        
        return [
            {
                "location": location,
                "distance_km": distance / 1000
            }
            for location, distance in results
        ]
```

## Week 2: API & Testing (Days 8-14)

### API Implementation

**File**: `services/location-management/src/api/location_routes.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from ..schemas.location_schemas import LocationCreate, LocationResponse
from ..services.location_service import LocationService

router = APIRouter(prefix="/api/v1/locations", tags=["farm-locations"])

def get_db():
    # TODO: Implement database session dependency
    pass

@router.post("/", response_model=LocationResponse)
async def create_farm_location(
    location: LocationCreate,
    user_id: UUID = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Create new farm location
    
    Supports:
    - GPS coordinates
    - Address geocoding
    - Automatic climate zone detection
    - Agricultural suitability validation
    """
    try:
        service = LocationService(db)
        result = await service.create_location(user_id, location)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/nearby")
async def find_nearby_farms(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Find farms within radius using geospatial query"""
    service = LocationService(db)
    results = await service.find_nearby_locations(latitude, longitude, radius_km)
    return {"results": results, "count": len(results)}
```

## Definition of Done

### Functional Requirements
- [ ] PostGIS extension enabled
- [ ] Location CRUD operations working
- [ ] Geocoding with fallback functional
- [ ] Geospatial queries operational
- [ ] Field boundary management complete

### Testing Requirements
- [ ] Unit tests for geocoding
- [ ] Geospatial query tests
- [ ] API integration tests
- [ ] Validation tests

### Integration Points
- [ ] Mock climate zone service
- [ ] Mock user management service

## Common Pitfalls

1. **SRID Consistency**: Always use SRID 4326 (WGS84)
2. **Longitude/Latitude Order**: PostGIS uses (lng, lat) not (lat, lng)
3. **Distance Units**: ST_Distance returns meters
4. **Index Usage**: Ensure GIST indexes for performance

## Next Steps

Integrates with:
- **Climate Zone Service** (Job 5): For zone detection
- **User Management**: For user associations
- **All Services**: Provides location context

