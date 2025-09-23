# Farm Location Input - Design Document

## Overview

The Farm Location Input system provides multiple intuitive methods for farmers to specify their farm and field locations. The design prioritizes accuracy, usability, and security while supporting various input preferences and technical capabilities. The system integrates with mapping services, geocoding APIs, and the browser's geolocation API to provide a comprehensive location input experience.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend Components                          │
├─────────────────────────────────────────────────────────────────┤
│  Location Input UI  │  Map Interface  │  Field Management      │
│  - GPS Coordinates  │  - Interactive  │  - Multiple Fields     │
│  - Address Search   │    Map Display  │  - Field Names         │
│  - Current Location │  - Marker Drag  │  - Location List       │
│  - Validation UI    │  - Zoom/Pan     │  - Edit/Delete         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API Gateway Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  Location Validation │  Geocoding      │  Security Middleware   │
│  - Coordinate Range  │  - Address→GPS  │  - Input Sanitization  │
│  - Agricultural Area │  - GPS→Address  │  - Rate Limiting       │
│  - Data Consistency  │  - Autocomplete │  - Authentication      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Service Layer                                │
├─────────────────────────────────────────────────────────────────┤
│  Location Service    │  Geocoding      │  Validation Service    │
│  - CRUD Operations   │  Service        │  - Agricultural Areas  │
│  - Field Management  │  - External API │  - Coordinate Ranges   │
│  - Data Encryption   │  - Caching      │  - Data Quality        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Storage Layer                           │
├─────────────────────────────────────────────────────────────────┤
│  Encrypted Database  │  Cache Layer    │  Geographic Data       │
│  - Farm Locations    │  - Geocoding    │  - Climate Zones       │
│  - Field Coordinates │  - Address      │  - County Boundaries   │
│  - User Permissions  │  - Validation   │  - Agricultural Areas  │
└─────────────────────────────────────────────────────────────────┘
```

### External Integrations

```
┌─────────────────────────────────────────────────────────────────┐
│                    External Services                            │
├─────────────────────────────────────────────────────────────────┤
│  Mapping Services    │  Geocoding APIs │  Geographic Data       │
│  - OpenStreetMap     │  - Google Maps  │  - USDA Climate Zones  │
│  - Mapbox           │  - Nominatim    │  - County Boundaries   │
│  - Leaflet          │  - MapBox       │  - Agricultural Areas  │
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### Frontend Components

#### LocationInputComponent
```typescript
interface LocationInputProps {
  onLocationSelected: (location: FarmLocation) => void;
  initialLocation?: FarmLocation;
  allowMultipleFields: boolean;
  validationRules: LocationValidationRules;
}

interface FarmLocation {
  id?: string;
  name: string;
  latitude: number;
  longitude: number;
  address?: string;
  accuracy?: number;
  source: 'gps' | 'address' | 'map' | 'current';
  verified: boolean;
  createdAt: Date;
  updatedAt: Date;
}

class LocationInputComponent {
  // GPS Coordinate Input
  renderGPSInput(): JSX.Element;
  validateCoordinates(lat: number, lon: number): ValidationResult;
  
  // Address Input with Autocomplete
  renderAddressInput(): JSX.Element;
  handleAddressAutocomplete(query: string): Promise<AddressSuggestion[]>;
  
  // Interactive Map
  renderMapInterface(): JSX.Element;
  handleMapClick(coordinates: [number, number]): void;
  handleMarkerDrag(coordinates: [number, number]): void;
  
  // Current Location Detection
  handleCurrentLocationRequest(): Promise<GeolocationResult>;
  
  // Validation and Confirmation
  validateLocation(location: FarmLocation): ValidationResult;
  showConfirmationDialog(location: FarmLocation): void;
}
```

#### MapInterfaceComponent
```typescript
interface MapConfig {
  center: [number, number];
  zoom: number;
  maxZoom: number;
  minZoom: number;
  enableSearch: boolean;
  enableCurrentLocation: boolean;
}

class MapInterfaceComponent {
  private map: L.Map;
  private marker: L.Marker;
  
  initializeMap(config: MapConfig): void;
  addLocationMarker(coordinates: [number, number]): void;
  enableMarkerDragging(): void;
  handleLocationSearch(query: string): void;
  getCurrentMapCenter(): [number, number];
  setMapView(coordinates: [number, number], zoom: number): void;
}
```

#### FieldManagementComponent
```typescript
interface FieldManagementProps {
  farmId: string;
  fields: FarmField[];
  onFieldAdded: (field: FarmField) => void;
  onFieldUpdated: (field: FarmField) => void;
  onFieldDeleted: (fieldId: string) => void;
}

interface FarmField extends FarmLocation {
  farmId: string;
  fieldType: 'crop' | 'pasture' | 'other';
  size?: number; // acres
  soilType?: string;
  notes?: string;
}

class FieldManagementComponent {
  renderFieldList(): JSX.Element;
  renderAddFieldForm(): JSX.Element;
  handleFieldSelection(fieldId: string): void;
  validateFieldData(field: FarmField): ValidationResult;
}
```

### Backend API Endpoints

#### Location Management API
```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, validator
from typing import List, Optional

class LocationRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    source: str = Field(..., regex="^(gps|address|map|current)$")
    
    @validator('latitude', 'longitude')
    def validate_coordinates(cls, v, field):
        if field.name == 'latitude' and not -90 <= v <= 90:
            raise ValueError('Latitude must be between -90 and 90')
        if field.name == 'longitude' and not -180 <= v <= 180:
            raise ValueError('Longitude must be between -180 and 180')
        return v

class LocationResponse(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float
    address: Optional[str]
    county: Optional[str]
    state: Optional[str]
    climate_zone: Optional[str]
    verified: bool
    created_at: datetime
    updated_at: datetime

router = APIRouter(prefix="/api/v1/locations")

@router.post("/", response_model=LocationResponse)
async def create_location(
    location: LocationRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new farm location."""
    pass

@router.get("/", response_model=List[LocationResponse])
async def get_locations(
    current_user: User = Depends(get_current_user)
):
    """Get all locations for the current user."""
    pass

@router.put("/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: str,
    location: LocationRequest,
    current_user: User = Depends(get_current_user)
):
    """Update an existing location."""
    pass

@router.delete("/{location_id}")
async def delete_location(
    location_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a location."""
    pass
```

#### Geocoding API
```python
class GeocodingService:
    def __init__(self):
        self.primary_provider = "nominatim"  # OpenStreetMap
        self.fallback_provider = "mapbox"
        self.cache = GeocodingCache()
    
    async def geocode_address(self, address: str) -> GeocodingResult:
        """Convert address to coordinates."""
        # Check cache first
        cached_result = await self.cache.get(address)
        if cached_result:
            return cached_result
        
        try:
            result = await self._geocode_with_provider(address, self.primary_provider)
        except GeocodingError:
            result = await self._geocode_with_provider(address, self.fallback_provider)
        
        # Cache successful results
        await self.cache.set(address, result)
        return result
    
    async def reverse_geocode(self, lat: float, lon: float) -> AddressResult:
        """Convert coordinates to address."""
        pass
    
    async def get_address_suggestions(self, query: str) -> List[AddressSuggestion]:
        """Get autocomplete suggestions for address input."""
        pass

@router.post("/geocode")
async def geocode_address(request: GeocodingRequest):
    """Convert address to GPS coordinates."""
    pass

@router.post("/reverse-geocode")
async def reverse_geocode(request: ReverseGeocodingRequest):
    """Convert GPS coordinates to address."""
    pass

@router.get("/address-suggestions")
async def get_address_suggestions(query: str):
    """Get address autocomplete suggestions."""
    pass
```

#### Validation API
```python
class LocationValidationService:
    def __init__(self):
        self.agricultural_areas = AgriculturalAreasData()
        self.climate_zones = ClimateZoneData()
    
    async def validate_agricultural_location(self, lat: float, lon: float) -> ValidationResult:
        """Validate that coordinates are in agricultural areas."""
        # Check if location is in known agricultural regions
        is_agricultural = await self.agricultural_areas.is_agricultural_area(lat, lon)
        
        # Get geographic context
        county = await self.get_county(lat, lon)
        state = await self.get_state(lat, lon)
        climate_zone = await self.climate_zones.get_zone(lat, lon)
        
        warnings = []
        if not is_agricultural:
            warnings.append("Location may not be in a typical agricultural area")
        
        return ValidationResult(
            valid=True,
            warnings=warnings,
            geographic_info={
                'county': county,
                'state': state,
                'climate_zone': climate_zone,
                'is_agricultural': is_agricultural
            }
        )

@router.post("/validate")
async def validate_location(request: LocationValidationRequest):
    """Validate location for agricultural use."""
    pass
```

## Data Models

### Database Schema

```sql
-- Farm Locations Table
CREATE TABLE farm_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    address TEXT,
    county VARCHAR(100),
    state VARCHAR(50),
    climate_zone VARCHAR(20),
    source VARCHAR(20) NOT NULL CHECK (source IN ('gps', 'address', 'map', 'current')),
    verified BOOLEAN DEFAULT FALSE,
    accuracy_meters INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_latitude CHECK (latitude >= -90 AND latitude <= 90),
    CONSTRAINT valid_longitude CHECK (longitude >= -180 AND longitude <= 180),
    
    -- Indexes
    INDEX idx_farm_locations_user_id (user_id),
    INDEX idx_farm_locations_coordinates (latitude, longitude),
    INDEX idx_farm_locations_state_county (state, county)
);

-- Farm Fields Table (extends locations for multiple fields per farm)
CREATE TABLE farm_fields (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location_id UUID NOT NULL REFERENCES farm_locations(id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL,
    field_type VARCHAR(20) DEFAULT 'crop' CHECK (field_type IN ('crop', 'pasture', 'other')),
    size_acres DECIMAL(10, 2),
    soil_type VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes
    INDEX idx_farm_fields_location_id (location_id)
);

-- Geocoding Cache Table
CREATE TABLE geocoding_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_hash VARCHAR(64) UNIQUE NOT NULL,
    query_text TEXT NOT NULL,
    result_json JSONB NOT NULL,
    provider VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Indexes
    INDEX idx_geocoding_cache_hash (query_hash),
    INDEX idx_geocoding_cache_expires (expires_at)
);
```

### Pydantic Models

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class LocationSource(str, Enum):
    GPS = "gps"
    ADDRESS = "address"
    MAP = "map"
    CURRENT = "current"

class FieldType(str, Enum):
    CROP = "crop"
    PASTURE = "pasture"
    OTHER = "other"

class FarmLocationBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    source: LocationSource
    
    @validator('latitude')
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Latitude must be between -90 and 90 degrees')
        return v
    
    @validator('longitude')
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Longitude must be between -180 and 180 degrees')
        return v

class FarmLocationCreate(FarmLocationBase):
    pass

class FarmLocationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    address: Optional[str] = None

class FarmLocation(FarmLocationBase):
    id: str
    user_id: str
    county: Optional[str]
    state: Optional[str]
    climate_zone: Optional[str]
    verified: bool
    accuracy_meters: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class FarmFieldBase(BaseModel):
    field_name: str = Field(..., min_length=1, max_length=100)
    field_type: FieldType = FieldType.CROP
    size_acres: Optional[float] = Field(None, gt=0)
    soil_type: Optional[str] = None
    notes: Optional[str] = None

class FarmFieldCreate(FarmFieldBase):
    location_id: str

class FarmField(FarmFieldBase):
    id: str
    location_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class GeographicInfo(BaseModel):
    county: Optional[str]
    state: Optional[str]
    climate_zone: Optional[str]
    is_agricultural: bool

class ValidationResult(BaseModel):
    valid: bool
    warnings: List[str] = []
    errors: List[str] = []
    geographic_info: Optional[GeographicInfo] = None
```

## Error Handling

### Validation Errors
```python
class LocationValidationError(Exception):
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(message)

class GeocodingError(Exception):
    def __init__(self, message: str, provider: str = None):
        self.message = message
        self.provider = provider
        super().__init__(message)

# Error response models
class LocationError(BaseModel):
    error_code: str
    error_message: str
    field: Optional[str] = None
    agricultural_context: Optional[str] = None
    suggested_actions: List[str] = []

# Common error scenarios
LOCATION_ERRORS = {
    "INVALID_COORDINATES": LocationError(
        error_code="INVALID_COORDINATES",
        error_message="GPS coordinates are outside valid ranges",
        agricultural_context="Accurate location data is essential for climate-specific recommendations",
        suggested_actions=[
            "Verify latitude is between -90 and 90 degrees",
            "Verify longitude is between -180 and 180 degrees",
            "Use the map interface to visually select location"
        ]
    ),
    "GEOCODING_FAILED": LocationError(
        error_code="GEOCODING_FAILED",
        error_message="Unable to convert address to coordinates",
        agricultural_context="Address geocoding helps ensure recommendations match your local conditions",
        suggested_actions=[
            "Try a more specific address (include street number)",
            "Use GPS coordinates instead",
            "Select location using the interactive map"
        ]
    ),
    "NON_AGRICULTURAL_AREA": LocationError(
        error_code="NON_AGRICULTURAL_AREA",
        error_message="Location appears to be outside typical agricultural areas",
        agricultural_context="Recommendations are optimized for agricultural regions",
        suggested_actions=[
            "Verify the location is correct",
            "Proceed with caution as recommendations may be less accurate",
            "Consult local agricultural experts for validation"
        ]
    )
}
```

## Testing Strategy

### Unit Tests
```python
class TestLocationValidation:
    def test_valid_coordinates(self):
        """Test validation of valid GPS coordinates."""
        assert validate_coordinates(42.0308, -93.6319) == True
        
    def test_invalid_coordinates(self):
        """Test validation rejects invalid coordinates."""
        with pytest.raises(LocationValidationError):
            validate_coordinates(91.0, -93.6319)  # Invalid latitude
            
    def test_agricultural_area_detection(self):
        """Test detection of agricultural vs non-agricultural areas."""
        # Iowa farmland should be detected as agricultural
        result = validate_agricultural_location(42.0308, -93.6319)
        assert result.geographic_info.is_agricultural == True
        
        # Ocean coordinates should not be agricultural
        result = validate_agricultural_location(0.0, 0.0)
        assert result.geographic_info.is_agricultural == False

class TestGeocodingService:
    async def test_address_geocoding(self):
        """Test address to coordinates conversion."""
        service = GeocodingService()
        result = await service.geocode_address("Ames, Iowa")
        
        assert result.latitude is not None
        assert result.longitude is not None
        assert abs(result.latitude - 42.0308) < 0.1  # Approximate match
        
    async def test_reverse_geocoding(self):
        """Test coordinates to address conversion."""
        service = GeocodingService()
        result = await service.reverse_geocode(42.0308, -93.6319)
        
        assert "Iowa" in result.address
        assert result.county is not None

class TestLocationAPI:
    async def test_create_location(self, client, authenticated_user):
        """Test location creation endpoint."""
        location_data = {
            "name": "North Field",
            "latitude": 42.0308,
            "longitude": -93.6319,
            "source": "gps"
        }
        
        response = await client.post("/api/v1/locations/", json=location_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == "North Field"
        assert data["verified"] == False  # Should require verification
        
    async def test_location_validation(self, client):
        """Test location validation endpoint."""
        validation_data = {
            "latitude": 42.0308,
            "longitude": -93.6319
        }
        
        response = await client.post("/api/v1/locations/validate", json=validation_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] == True
        assert data["geographic_info"]["is_agricultural"] == True
```

### Integration Tests
```python
class TestLocationWorkflow:
    async def test_complete_location_input_workflow(self, client, authenticated_user):
        """Test complete location input and validation workflow."""
        
        # Step 1: Create location via GPS input
        location_data = {
            "name": "Main Farm",
            "latitude": 42.0308,
            "longitude": -93.6319,
            "source": "gps"
        }
        
        create_response = await client.post("/api/v1/locations/", json=location_data)
        assert create_response.status_code == 201
        location_id = create_response.json()["id"]
        
        # Step 2: Validate location
        validation_response = await client.post(
            "/api/v1/locations/validate",
            json={"latitude": 42.0308, "longitude": -93.6319}
        )
        assert validation_response.status_code == 200
        
        # Step 3: Add field to location
        field_data = {
            "location_id": location_id,
            "field_name": "Corn Field A",
            "field_type": "crop",
            "size_acres": 80.5
        }
        
        field_response = await client.post("/api/v1/fields/", json=field_data)
        assert field_response.status_code == 201
        
        # Step 4: Retrieve all locations
        locations_response = await client.get("/api/v1/locations/")
        assert locations_response.status_code == 200
        
        locations = locations_response.json()
        assert len(locations) == 1
        assert locations[0]["name"] == "Main Farm"
```

This design provides a comprehensive, secure, and user-friendly system for farm location input that meets all the requirements while following agricultural domain best practices and modern web development standards.