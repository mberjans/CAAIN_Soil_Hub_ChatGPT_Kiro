"""
Farm Location Input Models
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

Pydantic models for location validation and serialization.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum
import re


class LocationSource(str, Enum):
    """Source of location data."""
    GPS = "gps"
    ADDRESS = "address"
    MAP = "map"
    CURRENT = "current"


class FieldType(str, Enum):
    """Type of farm field."""
    CROP = "crop"
    PASTURE = "pasture"
    OTHER = "other"


class FarmLocationBase(BaseModel):
    """Base model for farm location data."""
    
    name: str = Field(..., min_length=1, max_length=100, description="Location name")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    address: Optional[str] = Field(None, description="Street address")
    source: LocationSource = Field(..., description="How the location was input")
    
    @field_validator('latitude')
    @classmethod
    def validate_latitude(cls, v):
        """Validate latitude is within valid range."""
        if not -90 <= v <= 90:
            raise ValueError('Latitude must be between -90 and 90 degrees')
        return v
    
    @field_validator('longitude')
    @classmethod
    def validate_longitude(cls, v):
        """Validate longitude is within valid range."""
        if not -180 <= v <= 180:
            raise ValueError('Longitude must be between -180 and 180 degrees')
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate location name."""
        if not v or not v.strip():
            raise ValueError('Location name cannot be empty')
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\';\\]', '', v.strip())
        if len(sanitized) > 100:
            raise ValueError('Location name too long')
        return sanitized
    
    @field_validator('address')
    @classmethod
    def validate_address(cls, v):
        """Validate and sanitize address."""
        if v is not None:
            # Remove potentially dangerous characters
            sanitized = re.sub(r'[<>"\';\\]', '', v.strip())
            if len(sanitized) > 500:
                raise ValueError('Address too long')
            return sanitized if sanitized else None
        return v


class FarmLocationCreate(FarmLocationBase):
    """Model for creating a new farm location."""
    pass


class FarmLocationUpdate(BaseModel):
    """Model for updating an existing farm location."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    address: Optional[str] = None
    county: Optional[str] = None
    state: Optional[str] = None
    climate_zone: Optional[str] = None
    verified: Optional[bool] = None
    
    @field_validator('latitude')
    @classmethod
    def validate_latitude(cls, v):
        """Validate latitude if provided."""
        if v is not None and not -90 <= v <= 90:
            raise ValueError('Latitude must be between -90 and 90 degrees')
        return v
    
    @field_validator('longitude')
    @classmethod
    def validate_longitude(cls, v):
        """Validate longitude if provided."""
        if v is not None and not -180 <= v <= 180:
            raise ValueError('Longitude must be between -180 and 180 degrees')
        return v


class FarmLocation(FarmLocationBase):
    """Complete farm location model with all fields."""
    
    id: str = Field(..., description="Unique location identifier")
    user_id: str = Field(..., description="User who owns this location")
    county: Optional[str] = Field(None, description="County name")
    state: Optional[str] = Field(None, description="State name")
    climate_zone: Optional[str] = Field(None, description="Climate zone")
    verified: bool = Field(False, description="Whether location has been verified")
    accuracy_meters: Optional[int] = Field(None, description="GPS accuracy in meters")
    created_at: datetime = Field(..., description="When location was created")
    updated_at: datetime = Field(..., description="When location was last updated")
    
    model_config = ConfigDict(from_attributes=True)


class FarmFieldBase(BaseModel):
    """Base model for farm field data."""
    
    field_name: str = Field(..., min_length=1, max_length=100, description="Field name")
    field_type: FieldType = Field(FieldType.CROP, description="Type of field")
    size_acres: Optional[float] = Field(None, gt=0, description="Field size in acres")
    soil_type: Optional[str] = Field(None, max_length=50, description="Soil type")
    notes: Optional[str] = Field(None, description="Additional notes")
    
    @field_validator('field_name')
    @classmethod
    def validate_field_name(cls, v):
        """Validate and sanitize field name."""
        if not v or not v.strip():
            raise ValueError('Field name cannot be empty')
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\';\\]', '', v.strip())
        if len(sanitized) > 100:
            raise ValueError('Field name too long')
        return sanitized
    
    @field_validator('soil_type')
    @classmethod
    def validate_soil_type(cls, v):
        """Validate soil type."""
        if v is not None:
            sanitized = re.sub(r'[<>"\';\\]', '', v.strip())
            return sanitized if sanitized else None
        return v
    
    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v):
        """Validate notes field."""
        if v is not None:
            sanitized = re.sub(r'[<>"\';\\]', '', v.strip())
            if len(sanitized) > 1000:
                raise ValueError('Notes too long')
            return sanitized if sanitized else None
        return v


class FarmFieldCreate(FarmFieldBase):
    """Model for creating a new farm field."""
    
    location_id: str = Field(..., description="ID of the associated farm location")


class FarmFieldUpdate(BaseModel):
    """Model for updating an existing farm field."""
    
    field_name: Optional[str] = Field(None, min_length=1, max_length=100)
    field_type: Optional[FieldType] = None
    size_acres: Optional[float] = Field(None, gt=0)
    soil_type: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None


class FarmField(FarmFieldBase):
    """Complete farm field model with all fields."""
    
    id: str = Field(..., description="Unique field identifier")
    location_id: str = Field(..., description="Associated farm location ID")
    created_at: datetime = Field(..., description="When field was created")
    updated_at: datetime = Field(..., description="When field was last updated")
    
    model_config = ConfigDict(from_attributes=True)


class GeographicInfo(BaseModel):
    """Geographic information for a location."""
    
    county: Optional[str] = Field(None, description="County name")
    state: Optional[str] = Field(None, description="State name")
    climate_zone: Optional[str] = Field(None, description="Climate zone")
    is_agricultural: bool = Field(..., description="Whether location is in agricultural area")
    climate_analysis: Optional[dict] = Field(None, description="Comprehensive climate analysis data")


class ValidationResult(BaseModel):
    """Result of location validation."""
    
    valid: bool = Field(..., description="Whether location is valid")
    warnings: List[str] = Field(default=[], description="Validation warnings")
    errors: List[str] = Field(default=[], description="Validation errors")
    geographic_info: Optional[GeographicInfo] = Field(None, description="Geographic context")


class LocationValidationRequest(BaseModel):
    """Request for location validation."""
    
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class GeocodingRequest(BaseModel):
    """Request for geocoding an address."""
    
    address: str = Field(..., min_length=1, max_length=500, description="Address to geocode")
    
    @field_validator('address')
    @classmethod
    def validate_address(cls, v):
        """Validate and sanitize address."""
        if not v or not v.strip():
            raise ValueError('Address cannot be empty')
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\';\\]', '', v.strip())
        if len(sanitized) > 500:
            raise ValueError('Address too long')
        return sanitized


class ReverseGeocodingRequest(BaseModel):
    """Request for reverse geocoding coordinates."""
    
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class GeocodingResult(BaseModel):
    """Result of geocoding operation."""
    
    latitude: float = Field(..., description="Latitude in decimal degrees")
    longitude: float = Field(..., description="Longitude in decimal degrees")
    address: str = Field(..., description="Formatted address")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")
    provider: str = Field(..., description="Geocoding provider used")


class AddressResult(BaseModel):
    """Result of reverse geocoding operation."""
    
    address: str = Field(..., description="Formatted address")
    county: Optional[str] = Field(None, description="County name")
    state: Optional[str] = Field(None, description="State name")
    country: Optional[str] = Field(None, description="Country name")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")


class AddressSuggestion(BaseModel):
    """Address autocomplete suggestion."""
    
    address: str = Field(..., description="Suggested address")
    latitude: Optional[float] = Field(None, description="Latitude if available")
    longitude: Optional[float] = Field(None, description="Longitude if available")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")


class LocationError(BaseModel):
    """Location-specific error response."""
    
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Human-readable error message")
    field: Optional[str] = Field(None, description="Field that caused the error")
    agricultural_context: Optional[str] = Field(None, description="Agricultural context for the error")
    suggested_actions: List[str] = Field(default=[], description="Suggested actions to resolve")


# Common error responses
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
    ),
    "LOCATION_NOT_FOUND": LocationError(
        error_code="LOCATION_NOT_FOUND",
        error_message="Location not found",
        agricultural_context="Cannot provide recommendations without valid location data",
        suggested_actions=[
            "Check that the location ID is correct",
            "Verify you have permission to access this location",
            "Create a new location if needed"
        ]
    ),
    "INSUFFICIENT_PERMISSIONS": LocationError(
        error_code="INSUFFICIENT_PERMISSIONS",
        error_message="Insufficient permissions to access location data",
        agricultural_context="Location data is protected for privacy and security",
        suggested_actions=[
            "Contact the farm owner for access",
            "Verify you are logged in with the correct account",
            "Request consultant access if appropriate"
        ]
    )
}


# Export all models
__all__ = [
    'LocationSource', 'FieldType',
    'FarmLocationBase', 'FarmLocationCreate', 'FarmLocationUpdate', 'FarmLocation',
    'FarmFieldBase', 'FarmFieldCreate', 'FarmFieldUpdate', 'FarmField',
    'GeographicInfo', 'ValidationResult',
    'LocationValidationRequest', 'GeocodingRequest', 'ReverseGeocodingRequest',
    'GeocodingResult', 'AddressResult', 'AddressSuggestion',
    'LocationError', 'LOCATION_ERRORS'
]