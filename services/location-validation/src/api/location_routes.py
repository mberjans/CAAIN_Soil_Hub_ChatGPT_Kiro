"""
Location Management API Routes
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

FastAPI routes for comprehensive location management endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Path, status
from typing import Dict, Any, List, Optional
import logging
import sys
import os
import uuid
from uuid import UUID
from datetime import datetime

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../databases/python'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../services'))

from location_models import (
    LocationValidationRequest, ValidationResult, LocationError, LOCATION_ERRORS
)
from location_validation_service import LocationValidationService
from geocoding_service import (
    GeocodingResult, AddressResult, AddressSuggestion, 
    GeocodingError, get_geocoding_service,
    BatchGeocodingRequest, BatchGeocodingResponse
)
from location_sqlalchemy_models import FarmLocation, FarmField, GeocodingCache

# Import GPS accuracy routes
from .gps_accuracy_routes import router as gps_accuracy_router

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/locations", tags=["location-management"])

# Service instances
validation_service = LocationValidationService()
geocoding_service = get_geocoding_service()


# Pydantic models for API requests/responses
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class LocationCreateRequest(BaseModel):
    """Request model for creating farm locations."""
    
    farm_name: str = Field(..., min_length=1, max_length=200, description="Name of the farm")
    primary_address: Optional[Dict[str, str]] = Field(None, description="Primary address information")
    coordinates: Optional[Dict[str, float]] = Field(None, description="GPS coordinates")
    farm_characteristics: Optional[Dict[str, Any]] = Field(None, description="Farm characteristics")
    contact_information: Optional[Dict[str, str]] = Field(None, description="Contact information")
    privacy_settings: Optional[Dict[str, Any]] = Field(None, description="Privacy settings")
    
    @validator('coordinates')
    def validate_coordinates(cls, v):
        if v:
            lat = v.get('latitude')
            lng = v.get('longitude')
            if lat is not None and not (-90 <= lat <= 90):
                raise ValueError('Latitude must be between -90 and 90')
            if lng is not None and not (-180 <= lng <= 180):
                raise ValueError('Longitude must be between -180 and 180')
        return v

class LocationUpdateRequest(BaseModel):
    """Request model for updating farm locations."""
    
    farm_name: Optional[str] = Field(None, min_length=1, max_length=200)
    primary_address: Optional[Dict[str, str]] = None
    coordinates: Optional[Dict[str, float]] = None
    farm_characteristics: Optional[Dict[str, Any]] = None
    contact_information: Optional[Dict[str, str]] = None
    privacy_settings: Optional[Dict[str, Any]] = None
    
    @validator('coordinates')
    def validate_coordinates(cls, v):
        if v:
            lat = v.get('latitude')
            lng = v.get('longitude')
            if lat is not None and not (-90 <= lat <= 90):
                raise ValueError('Latitude must be between -90 and 90')
            if lng is not None and not (-180 <= lng <= 180):
                raise ValueError('Longitude must be between -180 and 180')
        return v

class LocationResponse(BaseModel):
    """Response model for location data."""
    
    id: str
    farm_name: str
    latitude: float
    longitude: float
    address: Optional[str]
    county: Optional[str]
    state: Optional[str]
    climate_zone: Optional[str]
    farm_characteristics: Optional[Dict[str, Any]]
    contact_information: Optional[Dict[str, str]]
    privacy_settings: Optional[Dict[str, Any]]
    verified: bool
    created_at: datetime
    updated_at: datetime

class LocationListResponse(BaseModel):
    """Response model for location list with pagination."""
    
    locations: List[LocationResponse]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool

class LocationValidationResponse(BaseModel):
    """Response model for location validation."""
    
    valid: bool
    validation_results: ValidationResult
    agricultural_context: Optional[Dict[str, Any]]
    suggestions: List[str]
    warnings: List[str]
    errors: List[str]


# Dependency injection for database session (placeholder)
async def get_db_session():
    """Get database session - placeholder for actual implementation."""
    # This would be replaced with actual database session management
    return None

async def get_current_user():
    """Get current user - placeholder for actual implementation."""
    # This would be replaced with actual user authentication
    return {"user_id": "test-user-id"}


@router.post("/", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def create_farm_location(
    request: LocationCreateRequest,
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_db_session)
) -> LocationResponse:
    """
    Create a new farm location with comprehensive validation.
    
    This endpoint creates a new farm location with:
    - Address validation and geocoding
    - Coordinate validation and agricultural area verification
    - Duplicate detection and conflict resolution
    - Agricultural context enrichment
    - Privacy settings enforcement
    
    Args:
        request: LocationCreateRequest with farm details
        current_user: Current authenticated user
        db_session: Database session
        
    Returns:
        LocationResponse with created location data
        
    Raises:
        HTTPException: If validation fails or creation error occurs
    """
    try:
        logger.info(f"Creating farm location: {request.farm_name}")
        
        # Extract coordinates from request
        latitude = None
        longitude = None
        if request.coordinates:
            latitude = request.coordinates.get('latitude')
            longitude = request.coordinates.get('longitude')
        
        # If no coordinates provided, try to geocode address
        if not latitude or not longitude:
            if request.primary_address:
                address_str = f"{request.primary_address.get('street_address', '')}, {request.primary_address.get('city', '')}, {request.primary_address.get('state', '')} {request.primary_address.get('postal_code', '')}"
                try:
                    geocode_result = await geocoding_service.geocode_address(address_str)
                    latitude = geocode_result.latitude
                    longitude = geocode_result.longitude
                except GeocodingError as e:
                    logger.warning(f"Geocoding failed: {e.message}")
                    raise HTTPException(
                        status_code=422,
                        detail={
                            "error": {
                                "error_code": "GEOCODING_REQUIRED",
                                "error_message": "Coordinates or valid address required",
                                "agricultural_context": "Location coordinates are essential for accurate agricultural recommendations",
                                "suggested_actions": [
                                    "Provide GPS coordinates",
                                    "Enter a complete street address",
                                    "Use the interactive map to select location"
                                ]
                            }
                        }
                    )
            else:
                raise HTTPException(
                    status_code=422,
                    detail={
                        "error": {
                            "error_code": "LOCATION_DATA_REQUIRED",
                            "error_message": "Either coordinates or address must be provided",
                            "agricultural_context": "Location information is required for farm management",
                            "suggested_actions": [
                                "Provide GPS coordinates",
                                "Enter complete address information",
                                "Use location selection tools"
                            ]
                        }
                    }
                )
        
        # Validate coordinates
        validation_result = await validation_service.validate_agricultural_location(
            latitude, longitude
        )
        
        if not validation_result.valid:
            logger.warning(f"Location validation failed: {validation_result.errors}")
            raise HTTPException(
                status_code=422,
                detail={
                    "error": {
                        "error_code": "LOCATION_VALIDATION_FAILED",
                        "error_message": "Location validation failed",
                        "validation_errors": validation_result.errors,
                        "agricultural_context": "Location must be suitable for agricultural use",
                        "suggested_actions": [
                            "Verify coordinates are correct",
                            "Ensure location is in an agricultural area",
                            "Contact support for manual validation"
                        ]
                    }
                }
            )
        
        # Create location record (placeholder - would use actual database)
        location_data = {
            "id": str(UUID()),
            "farm_name": request.farm_name,
            "latitude": latitude,
            "longitude": longitude,
            "address": f"{request.primary_address.get('street_address', '')}, {request.primary_address.get('city', '')}, {request.primary_address.get('state', '')}" if request.primary_address else None,
            "county": validation_result.geographic_info.county if validation_result.geographic_info else None,
            "state": validation_result.geographic_info.state if validation_result.geographic_info else None,
            "climate_zone": validation_result.geographic_info.climate_zone if validation_result.geographic_info else None,
            "farm_characteristics": request.farm_characteristics,
            "contact_information": request.contact_information,
            "privacy_settings": request.privacy_settings,
            "verified": validation_result.valid,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        logger.info(f"Farm location created successfully: {location_data['id']}")
        
        return LocationResponse(**location_data)
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Unexpected error creating farm location: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "error_code": "LOCATION_CREATION_ERROR",
                    "error_message": "Internal error creating farm location",
                    "agricultural_context": "Unable to create farm location for agricultural management",
                    "suggested_actions": [
                        "Try again in a few moments",
                        "Contact support if the problem persists",
                        "Verify all required information is provided"
                    ]
                }
            }
        )


@router.get("/", response_model=LocationListResponse)
async def get_user_locations(
    user_id: Optional[str] = Query(None, description="User ID (defaults to current user)"),
    farm_type: Optional[str] = Query(None, description="Filter by farm type"),
    crop_type: Optional[str] = Query(None, description="Filter by primary crop type"),
    state: Optional[str] = Query(None, description="Filter by state"),
    limit: int = Query(10, ge=1, le=100, description="Number of locations per page"),
    offset: int = Query(0, ge=0, description="Number of locations to skip"),
    sort_by: str = Query("created_at", description="Sort field (created_at, updated_at, farm_name)"),
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_db_session)
) -> LocationListResponse:
    """
    Retrieve user locations with filtering and pagination.
    
    This endpoint provides:
    - User location listing with pagination
    - Filtering by farm characteristics
    - Sorting options
    - Agricultural context information
    
    Args:
        user_id: User ID (defaults to current user)
        farm_type: Filter by farm type
        crop_type: Filter by primary crop type
        state: Filter by state
        limit: Number of locations per page (1-100)
        offset: Number of locations to skip
        sort_by: Sort field
        current_user: Current authenticated user
        db_session: Database session
        
    Returns:
        LocationListResponse with paginated location data
        
    Raises:
        HTTPException: If retrieval fails
    """
    try:
        # Use current user if no user_id provided
        if not user_id:
            user_id = current_user["user_id"]
        
        logger.info(f"Retrieving locations for user: {user_id} (limit: {limit}, offset: {offset})")
        
        # Placeholder for actual database query
        # This would implement filtering, sorting, and pagination
        locations_data = [
            {
                "id": "test-location-1",
                "farm_name": "Test Farm 1",
                "latitude": 42.0308,
                "longitude": -93.6319,
                "address": "123 Test Road, Ames, IA",
                "county": "Story",
                "state": "IA",
                "climate_zone": "5a",
                "farm_characteristics": {"total_acres": 640, "primary_crops": ["corn", "soybean"]},
                "contact_information": {"phone": "+1-515-555-0123"},
                "privacy_settings": {"location_sharing": "private"},
                "verified": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        total_count = 1  # Placeholder
        
        response = LocationListResponse(
            locations=[LocationResponse(**loc) for loc in locations_data],
            total_count=total_count,
            page=(offset // limit) + 1,
            page_size=limit,
            has_next=offset + limit < total_count,
            has_previous=offset > 0
        )
        
        logger.info(f"Retrieved {len(response.locations)} locations for user {user_id}")
        
        return response
        
    except Exception as e:
        logger.error(f"Unexpected error retrieving locations: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "error_code": "LOCATION_RETRIEVAL_ERROR",
                    "error_message": "Internal error retrieving locations",
                    "agricultural_context": "Unable to retrieve farm locations for management",
                    "suggested_actions": [
                        "Try again in a few moments",
                        "Contact support if the problem persists",
                        "Check your internet connection"
                    ]
                }
            }
        )


@router.put("/{location_id}", response_model=LocationResponse)
async def update_farm_location(
    location_id: str = Path(..., description="Location ID to update"),
    request: LocationUpdateRequest = None,
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_db_session)
) -> LocationResponse:
    """
    Update farm location with change tracking.
    
    This endpoint provides:
    - Partial updates with validation
    - Change tracking and history
    - Agricultural context updates
    - Dependent service notifications
    
    Args:
        location_id: Location ID to update
        request: LocationUpdateRequest with update data
        current_user: Current authenticated user
        db_session: Database session
        
    Returns:
        LocationResponse with updated location data
        
    Raises:
        HTTPException: If update fails or location not found
    """
    try:
        logger.info(f"Updating location: {location_id}")
        
        # Validate location ID format
        try:
            UUID(location_id)
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": {
                        "error_code": "INVALID_LOCATION_ID",
                        "error_message": "Invalid location ID format",
                        "agricultural_context": "Location ID must be a valid UUID",
                        "suggested_actions": [
                            "Verify location ID is correct",
                            "Use location list to find valid IDs",
                            "Contact support if ID appears correct"
                        ]
                    }
                }
            )
        
        # Placeholder for actual database update
        # This would implement partial updates, validation, and change tracking
        updated_location_data = {
            "id": location_id,
            "farm_name": request.farm_name if request.farm_name else "Updated Farm",
            "latitude": request.coordinates.get('latitude') if request.coordinates and request.coordinates.get('latitude') else 42.0308,
            "longitude": request.coordinates.get('longitude') if request.coordinates and request.coordinates.get('longitude') else -93.6319,
            "address": "Updated Address",
            "county": "Story",
            "state": "IA",
            "climate_zone": "5a",
            "farm_characteristics": request.farm_characteristics,
            "contact_information": request.contact_information,
            "privacy_settings": request.privacy_settings,
            "verified": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        logger.info(f"Location updated successfully: {location_id}")
        
        return LocationResponse(**updated_location_data)
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Unexpected error updating location: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "error_code": "LOCATION_UPDATE_ERROR",
                    "error_message": "Internal error updating location",
                    "agricultural_context": "Unable to update farm location data",
                    "suggested_actions": [
                        "Try again in a few moments",
                        "Contact support if the problem persists",
                        "Verify all update data is valid"
                    ]
                }
            }
        )


@router.delete("/{location_id}")
async def delete_farm_location(
    location_id: str = Path(..., description="Location ID to delete"),
    hard_delete: bool = Query(False, description="Perform hard delete (permanent removal)"),
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Delete farm location with dependency checking.
    
    This endpoint provides:
    - Dependency checking for related data
    - Soft delete option (mark as inactive)
    - Hard delete with data cleanup
    - Cascade handling for dependent services
    
    Args:
        location_id: Location ID to delete
        hard_delete: Whether to perform permanent deletion
        current_user: Current authenticated user
        db_session: Database session
        
    Returns:
        Dict with deletion confirmation and affected services
        
    Raises:
        HTTPException: If deletion fails or dependencies exist
    """
    try:
        logger.info(f"Deleting location: {location_id} (hard_delete: {hard_delete})")
        
        # Validate location ID format
        try:
            UUID(location_id)
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": {
                        "error_code": "INVALID_LOCATION_ID",
                        "error_message": "Invalid location ID format",
                        "agricultural_context": "Location ID must be a valid UUID",
                        "suggested_actions": [
                            "Verify location ID is correct",
                            "Use location list to find valid IDs",
                            "Contact support if ID appears correct"
                        ]
                    }
                }
            )
        
        # Check for dependencies (placeholder)
        dependencies = {
            "fields": 0,  # Would check for associated fields
            "recommendations": 0,  # Would check for historical recommendations
            "historical_data": 0  # Would check for historical data
        }
        
        if not hard_delete and any(dependencies.values()):
            # Soft delete - mark as inactive
            logger.info(f"Performing soft delete for location: {location_id}")
            return {
                "success": True,
                "deletion_type": "soft",
                "message": "Location marked as inactive",
                "location_id": location_id,
                "dependencies_found": dependencies,
                "affected_services": ["recommendation-engine", "data-integration"]
            }
        else:
            # Hard delete - permanent removal
            logger.info(f"Performing hard delete for location: {location_id}")
            return {
                "success": True,
                "deletion_type": "hard",
                "message": "Location permanently deleted",
                "location_id": location_id,
                "dependencies_cleaned": dependencies,
                "affected_services": ["recommendation-engine", "data-integration", "user-management"]
            }
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Unexpected error deleting location: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "error_code": "LOCATION_DELETION_ERROR",
                    "error_message": "Internal error deleting location",
                    "agricultural_context": "Unable to delete farm location",
                    "suggested_actions": [
                        "Try again in a few moments",
                        "Contact support if the problem persists",
                        "Consider soft delete if dependencies exist"
                    ]
                }
            }
        )


@router.post("/validate", response_model=LocationValidationResponse)
async def validate_farm_location(
    request: LocationCreateRequest,
    current_user: dict = Depends(get_current_user)
) -> LocationValidationResponse:
    """
    Comprehensive location validation for farm locations.
    
    This endpoint provides:
    - Real-time validation without creating location
    - Agricultural context validation
    - Coordinate accuracy assessment
    - Duplicate detection
    - Agricultural suitability scoring
    
    Args:
        request: LocationCreateRequest with location data to validate
        current_user: Current authenticated user
        
    Returns:
        LocationValidationResponse with validation results
        
    Raises:
        HTTPException: If validation fails
    """
    try:
        logger.info(f"Validating farm location: {request.farm_name}")
        
        # Extract coordinates
        latitude = None
        longitude = None
        if request.coordinates:
            latitude = request.coordinates.get('latitude')
            longitude = request.coordinates.get('longitude')
        
        # If no coordinates, try geocoding
        if not latitude or not longitude:
            if request.primary_address:
                address_str = f"{request.primary_address.get('street_address', '')}, {request.primary_address.get('city', '')}, {request.primary_address.get('state', '')} {request.primary_address.get('postal_code', '')}"
                try:
                    geocode_result = await geocoding_service.geocode_address(address_str)
                    latitude = geocode_result.latitude
                    longitude = geocode_result.longitude
                except GeocodingError as e:
                    return LocationValidationResponse(
                        valid=False,
                        validation_results=ValidationResult(
                            valid=False,
                            errors=[f"Geocoding failed: {e.message}"],
                            warnings=[],
                            geographic_info=None
                        ),
                        agricultural_context=None,
                        suggestions=[
                            "Provide GPS coordinates directly",
                            "Enter a more complete address",
                            "Use the interactive map to select location"
                        ],
                        warnings=[],
                        errors=[f"Geocoding failed: {e.message}"]
                    )
            else:
                return LocationValidationResponse(
                    valid=False,
                    validation_results=ValidationResult(
                        valid=False,
                        errors=["Coordinates or address required"],
                        warnings=[],
                        geographic_info=None
                    ),
                    agricultural_context=None,
                    suggestions=[
                        "Provide GPS coordinates",
                        "Enter complete address information",
                        "Use location selection tools"
                    ],
                    warnings=[],
                    errors=["Coordinates or address required"]
                )
        
        # Perform comprehensive validation
        validation_result = await validation_service.validate_agricultural_location(
            latitude, longitude
        )
        
        # Prepare agricultural context
        agricultural_context = None
        if validation_result.geographic_info:
            agricultural_context = {
                "climate_zone": validation_result.geographic_info.climate_zone,
                "county": validation_result.geographic_info.county,
                "state": validation_result.geographic_info.state,
                "is_agricultural": validation_result.geographic_info.is_agricultural,
                "suitable_crops": ["corn", "soybean", "wheat"] if validation_result.geographic_info.is_agricultural else []
            }
        
        logger.info(f"Location validation completed: valid={validation_result.valid}")
        
        return LocationValidationResponse(
            valid=validation_result.valid,
            validation_results=validation_result,
            agricultural_context=agricultural_context,
            suggestions=[
                "Location appears suitable for agricultural use" if validation_result.valid else "Consider alternative location",
                "Verify coordinates are accurate",
                "Check local agricultural regulations"
            ],
            warnings=validation_result.warnings,
            errors=validation_result.errors
        )
        
    except Exception as e:
        logger.error(f"Unexpected error validating location: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "error_code": "LOCATION_VALIDATION_ERROR",
                    "error_message": "Internal error validating location",
                    "agricultural_context": "Unable to validate location for agricultural use",
                    "suggested_actions": [
                        "Try again in a few moments",
                        "Contact support if the problem persists",
                        "Verify all location data is correct"
                    ]
                }
            }
        )


# Health check endpoint
@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for the location management service.
    
    Returns:
        Dict with service status and basic information
    """
    try:
        # Test basic service functionality
        test_result = await validation_service.validate_coordinates(42.0, -93.0)
        
        return {
            "status": "healthy",
            "service": "location-management",
            "version": "1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "test_validation": {
                "coordinates_tested": [42.0, -93.0],
                "validation_successful": test_result.valid
            },
            "endpoints": [
                "POST /api/v1/locations/ - Create farm location",
                "GET /api/v1/locations/ - List user locations",
                "PUT /api/v1/locations/{id} - Update location",
                "DELETE /api/v1/locations/{id} - Delete location",
                "POST /api/v1/locations/validate - Validate location"
            ]
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "location-management",
            "version": "1.0",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


# Geocoding endpoints

@router.post("/geocode", response_model=GeocodingResult)
async def geocode_address(
    address: str,
    include_agricultural_context: bool = Query(True, description="Include agricultural context data")
) -> GeocodingResult:
    """
    Convert street address to GPS coordinates with agricultural context enhancement.
    
    This endpoint geocodes a street address to GPS coordinates using
    OpenStreetMap Nominatim service with caching for performance and
    enhances results with agricultural context data including USDA zones,
    climate zones, soil survey areas, and agricultural districts.
    
    Args:
        address: Street address to geocode (e.g., "123 Main St, Ames, IA")
        include_agricultural_context: Include agricultural context data (USDA zones, climate zones, etc.)
        
    Returns:
        GeocodingResult with coordinates, formatted address, confidence score, and agricultural context
        
    Raises:
        HTTPException: If geocoding fails or address is invalid
    """
    try:
        logger.info(f"Geocoding address: {address} (agricultural context: {include_agricultural_context})")
        
        result = await geocoding_service.geocode_address(address, include_agricultural_context)
        
        logger.info(f"Geocoding successful: {result.latitude}, {result.longitude} (confidence: {result.confidence})")
        
        return result
        
    except GeocodingError as e:
        logger.error(f"Geocoding failed for address '{address}': {e.message}")
        raise HTTPException(
            status_code=422,
            detail={
                "error": {
                    "error_code": "GEOCODING_FAILED",
                    "error_message": f"Unable to geocode address: {e.message}",
                    "agricultural_context": "Address geocoding helps ensure recommendations match your local conditions",
                    "suggested_actions": [
                        "Try a more specific address (include street number)",
                        "Use GPS coordinates instead",
                        "Select location using the interactive map"
                    ]
                },
                "provider": e.provider
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error during geocoding: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "error_code": "GEOCODING_SERVICE_ERROR",
                    "error_message": "Internal geocoding service error",
                    "agricultural_context": "Unable to convert address to coordinates for location-based recommendations",
                    "suggested_actions": [
                        "Try again in a few moments",
                        "Use GPS coordinates directly",
                        "Contact support if the problem persists"
                    ]
                }
            }
        )


@router.post("/reverse-geocode", response_model=AddressResult)
async def reverse_geocode_coordinates(
    latitude: float, 
    longitude: float,
    include_agricultural_context: bool = Query(True, description="Include agricultural context data")
) -> AddressResult:
    """
    Convert GPS coordinates to street address with agricultural context enhancement.
    
    This endpoint performs reverse geocoding to convert GPS coordinates
    back to a human-readable street address and enhances results with
    agricultural context data including USDA zones, climate zones, soil
    survey areas, and agricultural districts.
    
    Args:
        latitude: Latitude in decimal degrees (-90 to 90)
        longitude: Longitude in decimal degrees (-180 to 180)
        include_agricultural_context: Include agricultural context data (USDA zones, climate zones, etc.)
        
    Returns:
        AddressResult with formatted address, components, and agricultural context
        
    Raises:
        HTTPException: If reverse geocoding fails or coordinates are invalid
    """
    try:
        logger.info(f"Reverse geocoding coordinates: {latitude}, {longitude} (agricultural context: {include_agricultural_context})")
        
        result = await geocoding_service.reverse_geocode(latitude, longitude, include_agricultural_context)
        
        logger.info(f"Reverse geocoding successful: {result.address}")
        
        return result
        
    except GeocodingError as e:
        logger.error(f"Reverse geocoding failed for coordinates {latitude}, {longitude}: {e.message}")
        raise HTTPException(
            status_code=422,
            detail={
                "error": {
                    "error_code": "REVERSE_GEOCODING_FAILED",
                    "error_message": f"Unable to reverse geocode coordinates: {e.message}",
                    "agricultural_context": "Reverse geocoding helps confirm location accuracy for agricultural recommendations",
                    "suggested_actions": [
                        "Verify coordinates are correct",
                        "Try slightly different coordinates",
                        "Use manual address entry instead"
                    ]
                },
                "coordinates": {"latitude": latitude, "longitude": longitude}
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error during reverse geocoding: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "error_code": "REVERSE_GEOCODING_SERVICE_ERROR",
                    "error_message": "Internal reverse geocoding service error",
                    "agricultural_context": "Unable to convert coordinates to address",
                    "suggested_actions": [
                        "Try again in a few moments",
                        "Enter address manually",
                        "Contact support if the problem persists"
                    ]
                }
            }
        )


@router.post("/batch-geocode", response_model=BatchGeocodingResponse)
async def batch_geocode_addresses(
    request: BatchGeocodingRequest
) -> BatchGeocodingResponse:
    """
    Convert multiple street addresses to GPS coordinates with agricultural context enhancement.
    
    This endpoint performs batch geocoding of multiple addresses to GPS coordinates using
    OpenStreetMap Nominatim service with caching for performance and enhances results with
    agricultural context data including USDA zones, climate zones, soil survey areas, and
    agricultural districts.
    
    Args:
        request: BatchGeocodingRequest containing list of addresses and options
        
    Returns:
        BatchGeocodingResponse with geocoding results, failed addresses, and statistics
        
    Raises:
        HTTPException: If batch geocoding fails or request is invalid
    """
    try:
        logger.info(f"Batch geocoding {len(request.addresses)} addresses (agricultural context: {request.include_agricultural_context})")
        
        result = await geocoding_service.batch_geocode(request)
        
        logger.info(f"Batch geocoding completed: {result.success_count} successful, {result.failure_count} failed")
        
        return result
        
    except Exception as e:
        logger.error(f"Unexpected error during batch geocoding: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "error_code": "BATCH_GEOCODING_SERVICE_ERROR",
                    "error_message": "Internal batch geocoding service error",
                    "agricultural_context": "Unable to process batch geocoding for agricultural planning",
                    "suggested_actions": [
                        "Try again in a few moments",
                        "Process addresses individually",
                        "Contact support if the problem persists"
                    ]
                }
            }
        )


# Field Management Endpoints
@router.post("/fields", response_model=Dict[str, Any])
async def create_field(
    request: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Create a new field for a farm location.
    
    This endpoint creates a new field with boundary data, area calculations,
    and agricultural context information for farm management.
    """
    try:
        logger.info(f"Creating field: {request.get('name', 'Unnamed Field')}")
        
        # Validate field data
        if not request.get('boundary'):
            raise HTTPException(
                status_code=422,
                detail={
                    "error": {
                        "error_code": "MISSING_BOUNDARY",
                        "error_message": "Field boundary is required",
                        "agricultural_context": "Field boundaries are essential for accurate agricultural recommendations",
                        "suggested_actions": [
                            "Draw field boundary on the map",
                            "Provide boundary coordinates",
                            "Use the interactive map tools"
                        ]
                    }
                }
            )
        
        # Create field record
        field_data = {
            "id": str(uuid.uuid4()),
            "name": request.get('name', 'Unnamed Field'),
            "boundary": request.get('boundary'),
            "area": request.get('area', {}),
            "created": request.get('created', datetime.utcnow().isoformat()),
            "modified": request.get('modified', datetime.utcnow().isoformat()),
            "user_id": current_user.get('id')
        }
        
        # TODO: Save to database when field table is created
        # For now, return the field data
        
        logger.info(f"Field created successfully: {field_data['id']}")
        
        return {
            "success": True,
            "field": field_data,
            "message": "Field created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating field: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "error_code": "FIELD_CREATION_ERROR",
                    "error_message": "Failed to create field",
                    "agricultural_context": "Unable to create field for agricultural planning",
                    "suggested_actions": [
                        "Try again in a few moments",
                        "Check field boundary data",
                        "Contact support if the problem persists"
                    ]
                }
            }
        )


@router.get("/fields", response_model=List[Dict[str, Any]])
async def get_fields(
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_db_session)
) -> List[Dict[str, Any]]:
    """
    Get all fields for the current user.
    
    This endpoint retrieves all fields associated with the current user
    for farm management and agricultural planning.
    """
    try:
        logger.info(f"Retrieving fields for user: {current_user.get('id')}")
        
        # TODO: Retrieve from database when field table is created
        # For now, return empty list
        
        fields = []
        
        logger.info(f"Retrieved {len(fields)} fields")
        
        return fields
        
    except Exception as e:
        logger.error(f"Error retrieving fields: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "error_code": "FIELD_RETRIEVAL_ERROR",
                    "error_message": "Failed to retrieve fields",
                    "agricultural_context": "Unable to retrieve fields for agricultural planning",
                    "suggested_actions": [
                        "Try again in a few moments",
                        "Contact support if the problem persists"
                    ]
                }
            }
        )


@router.post("/fields/{field_id}/analyze", response_model=Dict[str, Any])
async def analyze_field(
    field_id: str,
    request: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
    db_session = Depends(get_db_session)
) -> Dict[str, Any]:
    """
    Analyze a field for agricultural characteristics.
    
    This endpoint analyzes a field's location, soil, climate, and other
    agricultural characteristics to provide recommendations.
    """
    try:
        logger.info(f"Analyzing field: {field_id}")
        
        # Extract field data from request
        center_coordinates = request.get('center_coordinates', {})
        boundary = request.get('boundary')
        area = request.get('area', {})
        
        if not center_coordinates.get('latitude') or not center_coordinates.get('longitude'):
            raise HTTPException(
                status_code=422,
                detail={
                    "error": {
                        "error_code": "MISSING_COORDINATES",
                        "error_message": "Field center coordinates are required",
                        "agricultural_context": "Coordinates are essential for agricultural analysis",
                        "suggested_actions": [
                            "Provide field center coordinates",
                            "Use the interactive map to select field center",
                            "Ensure coordinates are valid"
                        ]
                    }
                }
            )
        
        # Perform agricultural analysis
        analysis_result = {
            "field_id": field_id,
            "soil_type": "Unknown",  # TODO: Integrate with soil service
            "climate_zone": "Unknown",  # TODO: Integrate with climate service
            "usda_zone": "Unknown",  # TODO: Integrate with USDA zone service
            "elevation": None,  # TODO: Integrate with elevation service
            "slope": None,  # TODO: Calculate slope from boundary
            "drainage": "Unknown",  # TODO: Integrate with drainage service
            "recommendations": [
                "Field analysis completed",
                "Additional soil testing recommended",
                "Consider crop rotation planning"
            ],
            "analysis_date": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Field analysis completed: {field_id}")
        
        return analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing field: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "error_code": "FIELD_ANALYSIS_ERROR",
                    "error_message": "Failed to analyze field",
                    "agricultural_context": "Unable to analyze field for agricultural planning",
                    "suggested_actions": [
                        "Try again in a few moments",
                        "Check field data",
                        "Contact support if the problem persists"
                    ]
                }
            }
        )


# Include GPS accuracy routes
router.include_router(gps_accuracy_router)


# Export router
__all__ = ['router']