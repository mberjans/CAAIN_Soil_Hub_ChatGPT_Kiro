from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional
from decimal import Decimal
from uuid import UUID


class CoordinateBase(BaseModel):
    """Base coordinates for location data"""
    latitude: float
    longitude: float
    
    @field_validator('latitude')
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('latitude must be between -90 and 90')
        return v
    
    @field_validator('longitude')
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('longitude must be between -180 and 180')
        return v


class LocationCreate(CoordinateBase):
    """Schema for creating a new location"""
    name: str
    address: Optional[str] = None
    elevation_meters: Optional[int] = None
    usda_zone: Optional[str] = None
    climate_zone: Optional[str] = None
    county: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = 'USA'
    total_acres: Optional[Decimal] = None


class LocationUpdate(BaseModel):
    """Schema for updating a location"""
    name: Optional[str] = None
    address: Optional[str] = None
    elevation_meters: Optional[int] = None
    usda_zone: Optional[str] = None
    climate_zone: Optional[str] = None
    county: Optional[str] = None
    state: Optional[str] = None
    total_acres: Optional[Decimal] = None


class LocationResponse(CoordinateBase):
    """Schema for location response"""
    id: UUID
    user_id: UUID
    name: str
    address: Optional[str] = None
    elevation_meters: Optional[int] = None
    usda_zone: Optional[str] = None
    climate_zone: Optional[str] = None
    county: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = 'USA'
    total_acres: Optional[Decimal] = None
    is_primary: Optional[bool] = False
    
    model_config = ConfigDict(from_attributes=True)


class NearbySearchRequest(CoordinateBase):
    """Schema for nearby location search"""
    radius_km: float = 50.0
    
    @field_validator('radius_km')
    def validate_radius(cls, v):
        if not 1 <= v <= 500:
            raise ValueError('radius_km must be between 1 and 500')
        return v


class NearbySearchResponse(BaseModel):
    """Schema for nearby search response"""
    locations: list
    count: int
    search_center: CoordinateBase
    radius_km: float


class FieldCreate(BaseModel):
    """Schema for creating a new field"""
    farm_location_id: UUID
    name: str
    acres: Decimal
    soil_type: Optional[str] = None
    drainage_class: Optional[str] = None
    slope_percent: Optional[Decimal] = None
    irrigation_available: Optional[bool] = False


class FieldResponse(BaseModel):
    """Schema for field response"""
    id: UUID
    farm_location_id: UUID
    name: str
    acres: Decimal
    soil_type: Optional[str] = None
    drainage_class: Optional[str] = None
    slope_percent: Optional[Decimal] = None
    irrigation_available: Optional[bool] = False
    
    model_config = ConfigDict(from_attributes=True)
