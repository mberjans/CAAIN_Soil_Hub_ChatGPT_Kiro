"""
Location Models for Location Validation Service
CAAIN Soil Hub - Location Validation Service

Data models for location validation requests and responses.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class LocationErrorType(str, Enum):
    """Types of location validation errors."""
    INVALID_COORDINATES = "INVALID_COORDINATES"
    OUT_OF_RANGE = "OUT_OF_RANGE"
    OCEAN_LOCATION = "OCEAN_LOCATION"
    INVALID_FORMAT = "INVALID_FORMAT"
    GEOCODING_FAILED = "GEOCODING_FAILED"
    AGRICULTURAL_UNSUITABLE = "AGRICULTURAL_UNSUITABLE"


class LocationError(BaseModel):
    """Location validation error model."""
    error_code: LocationErrorType
    error_message: str
    agricultural_context: Optional[str] = None
    suggested_actions: List[str] = Field(default_factory=list)


class GeographicInfo(BaseModel):
    """Geographic information model."""
    country: Optional[str] = None
    state: Optional[str] = None
    county: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    climate_zone: Optional[str] = None
    usda_zone: Optional[str] = None
    elevation_meters: Optional[float] = None
    timezone: Optional[str] = None


class ValidationResult(BaseModel):
    """Location validation result model."""
    valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    geographic_info: Optional[GeographicInfo] = None
    agricultural_suitability_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)


class LocationValidationRequest(BaseModel):
    """Location validation request model."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    include_agricultural_context: bool = Field(True, description="Include agricultural context data")
    include_geographic_info: bool = Field(True, description="Include geographic information")

    @validator('latitude', 'longitude')
    def validate_coordinates(cls, v):
        """Validate coordinate ranges."""
        if isinstance(v, (int, float)):
            return float(v)
        raise ValueError('Coordinates must be numeric')


class AgriculturalValidationRequest(BaseModel):
    """Agricultural validation request model."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    crop_type: Optional[str] = None
    field_size_acres: Optional[float] = Field(None, gt=0)
    soil_type: Optional[str] = None
    irrigation_available: Optional[bool] = None


class AgriculturalValidationResult(BaseModel):
    """Agricultural validation result model."""
    suitable_for_agriculture: bool
    suitability_score: float = Field(..., ge=0.0, le=1.0)
    recommended_crops: List[str] = Field(default_factory=list)
    soil_limitations: List[str] = Field(default_factory=list)
    climate_considerations: List[str] = Field(default_factory=list)
    management_recommendations: List[str] = Field(default_factory=list)


# Error definitions
LOCATION_ERRORS = {
    "INVALID_COORDINATES": LocationError(
        error_code=LocationErrorType.INVALID_COORDINATES,
        error_message="Invalid coordinate format or values",
        agricultural_context="Coordinates must be valid decimal degrees for agricultural applications",
        suggested_actions=[
            "Check coordinate format (decimal degrees)",
            "Ensure latitude is between -90 and 90",
            "Ensure longitude is between -180 and 180"
        ]
    ),
    "OUT_OF_RANGE": LocationError(
        error_code=LocationErrorType.OUT_OF_RANGE,
        error_message="Coordinates are outside valid ranges",
        agricultural_context="Coordinates outside valid ranges cannot be used for agricultural planning",
        suggested_actions=[
            "Verify latitude is between -90 and 90 degrees",
            "Verify longitude is between -180 and 180 degrees",
            "Check for coordinate system confusion"
        ]
    ),
    "OCEAN_LOCATION": LocationError(
        error_code=LocationErrorType.OCEAN_LOCATION,
        error_message="Location appears to be over water",
        agricultural_context="Ocean locations are not suitable for agricultural activities",
        suggested_actions=[
            "Verify coordinates are correct",
            "Use a location on land",
            "Check if coordinates are reversed"
        ]
    ),
    "INVALID_FORMAT": LocationError(
        error_code=LocationErrorType.INVALID_FORMAT,
        error_message="Invalid coordinate format",
        agricultural_context="Coordinate format must be compatible with agricultural mapping systems",
        suggested_actions=[
            "Use decimal degrees format",
            "Check for missing decimal points",
            "Verify coordinate separator"
        ]
    ),
    "GEOCODING_FAILED": LocationError(
        error_code=LocationErrorType.GEOCODING_FAILED,
        error_message="Unable to geocode address to coordinates",
        agricultural_context="Address geocoding failed, preventing agricultural analysis",
        suggested_actions=[
            "Provide GPS coordinates directly",
            "Enter a more complete address",
            "Use the interactive map to select location"
        ]
    ),
    "AGRICULTURAL_UNSUITABLE": LocationError(
        error_code=LocationErrorType.AGRICULTURAL_UNSUITABLE,
        error_message="Location is not suitable for agriculture",
        agricultural_context="Location has significant limitations for agricultural use",
        suggested_actions=[
            "Consider alternative locations",
            "Review soil and climate conditions",
            "Consult with agricultural experts"
        ]
    )
}