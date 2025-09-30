"""
Location Validation API Routes
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

FastAPI routes for location validation endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any
import logging
import sys
import os

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../databases/python'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../services'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../utils'))

from location_models import (
    LocationValidationRequest, ValidationResult, LocationError, LOCATION_ERRORS
)
from location_validation_service import LocationValidationService
from geocoding_service import (
    GeocodingResult, AddressResult, AddressSuggestion, 
    GeocodingError, get_geocoding_service,
    BatchGeocodingRequest, BatchGeocodingResponse
)
from coordinate_utils import CoordinateValidator, CoordinateConverter, CoordinateParser

# Import address validation routes
from .address_validation_routes import router as address_validation_router

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/validation", tags=["location-validation"])

# Service instances
validation_service = LocationValidationService()
geocoding_service = get_geocoding_service()


@router.post("/coordinates", response_model=ValidationResult)
async def validate_coordinates(request: LocationValidationRequest) -> ValidationResult:
    """
    Validate GPS coordinates for basic range and agricultural suitability.
    
    This endpoint validates coordinates for:
    - Valid coordinate ranges (-90 to 90 for latitude, -180 to 180 for longitude)
    - Ocean/water body detection
    - Basic agricultural area assessment
    - Geographic information (county, state, climate zone)
    
    Args:
        request: LocationValidationRequest with latitude and longitude
        
    Returns:
        ValidationResult with validation status and geographic information
        
    Raises:
        HTTPException: If validation fails due to invalid input
    """
    try:
        logger.info(f"Validating coordinates: {request.latitude}, {request.longitude}")
        
        result = await validation_service.validate_coordinates(
            request.latitude, 
            request.longitude
        )
        
        logger.info(f"Validation result: valid={result.valid}, warnings={len(result.warnings)}, errors={len(result.errors)}")
        
        return result
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=422,
            detail={
                "error": LOCATION_ERRORS["INVALID_COORDINATES"].dict(),
                "details": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error during coordinate validation: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "error_code": "VALIDATION_SERVICE_ERROR",
                    "error_message": "Internal validation service error",
                    "agricultural_context": "Unable to validate location for agricultural recommendations",
                    "suggested_actions": [
                        "Try again in a few moments",
                        "Contact support if the problem persists",
                        "Use alternative location input methods"
                    ]
                }
            }
        )


@router.post("/coordinate-format", response_model=Dict[str, Any])
async def validate_coordinate_format(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate coordinates in different formats (decimal, DMS, UTM, MGRS).
    
    This endpoint validates coordinates in various formats and provides
    conversion between formats for agricultural applications.
    
    Args:
        request: Dictionary with format type and coordinate data
        
    Returns:
        Dictionary with validation results and converted coordinates
    """
    try:
        format_type = request.get('format_type', 'decimal')
        coordinate_data = request.get('coordinate_data', {})
        
        logger.info(f"Validating {format_type} coordinates: {coordinate_data}")
        
        validation_result = None
        converted_coordinates = None
        
        if format_type == 'decimal':
            latitude = coordinate_data.get('latitude')
            longitude = coordinate_data.get('longitude')
            
            if latitude is None or longitude is None:
                raise ValueError("Missing latitude or longitude for decimal format")
            
            validation_result = CoordinateValidator.validate_decimal_coordinates(latitude, longitude)
            
            if validation_result['valid']:
                # Convert to other formats
                converted_coordinates = {
                    'decimal': {'latitude': latitude, 'longitude': longitude},
                    'dms': {
                        'latitude': CoordinateConverter.decimal_to_dms(latitude, True),
                        'longitude': CoordinateConverter.decimal_to_dms(longitude, False)
                    },
                    'utm': CoordinateConverter.decimal_to_utm(latitude, longitude),
                    'mgrs': CoordinateConverter.decimal_to_mgrs(latitude, longitude)
                }
        
        elif format_type == 'dms':
            lat_data = coordinate_data.get('latitude', {})
            lon_data = coordinate_data.get('longitude', {})
            
            # Validate latitude DMS
            lat_validation = CoordinateValidator.validate_dms_coordinates(
                lat_data.get('degrees', 0),
                lat_data.get('minutes', 0),
                lat_data.get('seconds', 0),
                lat_data.get('direction', 'N'),
                True
            )
            
            # Validate longitude DMS
            lon_validation = CoordinateValidator.validate_dms_coordinates(
                lon_data.get('degrees', 0),
                lon_data.get('minutes', 0),
                lon_data.get('seconds', 0),
                lon_data.get('direction', 'E'),
                False
            )
            
            validation_result = {
                'valid': lat_validation['valid'] and lon_validation['valid'],
                'errors': lat_validation['errors'] + lon_validation['errors'],
                'warnings': lat_validation['warnings'] + lon_validation['warnings']
            }
            
            if validation_result['valid']:
                # Convert to decimal
                lat_decimal = CoordinateConverter.dms_to_decimal(
                    lat_data['degrees'], lat_data['minutes'], lat_data['seconds'], lat_data['direction']
                )
                lon_decimal = CoordinateConverter.dms_to_decimal(
                    lon_data['degrees'], lon_data['minutes'], lon_data['seconds'], lon_data['direction']
                )
                
                converted_coordinates = {
                    'decimal': {'latitude': lat_decimal, 'longitude': lon_decimal},
                    'dms': {'latitude': lat_data, 'longitude': lon_data},
                    'utm': CoordinateConverter.decimal_to_utm(lat_decimal, lon_decimal),
                    'mgrs': CoordinateConverter.decimal_to_mgrs(lat_decimal, lon_decimal)
                }
        
        elif format_type == 'utm':
            zone = coordinate_data.get('zone')
            easting = coordinate_data.get('easting')
            northing = coordinate_data.get('northing')
            hemisphere = coordinate_data.get('hemisphere', 'N')
            
            if zone is None or easting is None or northing is None:
                raise ValueError("Missing zone, easting, or northing for UTM format")
            
            validation_result = CoordinateValidator.validate_utm_coordinates(zone, easting, northing, hemisphere)
            
            if validation_result['valid']:
                # Convert to decimal
                lat_decimal, lon_decimal = CoordinateConverter.utm_to_decimal(zone, easting, northing, hemisphere)
                
                converted_coordinates = {
                    'decimal': {'latitude': lat_decimal, 'longitude': lon_decimal},
                    'dms': {
                        'latitude': CoordinateConverter.decimal_to_dms(lat_decimal, True),
                        'longitude': CoordinateConverter.decimal_to_dms(lon_decimal, False)
                    },
                    'utm': {'zone': zone, 'easting': easting, 'northing': northing, 'hemisphere': hemisphere},
                    'mgrs': CoordinateConverter.decimal_to_mgrs(lat_decimal, lon_decimal)
                }
        
        elif format_type == 'mgrs':
            mgrs_coordinate = coordinate_data.get('coordinate')
            
            if not mgrs_coordinate:
                raise ValueError("Missing MGRS coordinate string")
            
            validation_result = CoordinateValidator.validate_mgrs_coordinate(mgrs_coordinate)
            
            if validation_result['valid']:
                # Convert to decimal
                lat_decimal, lon_decimal = CoordinateConverter.mgrs_to_decimal(mgrs_coordinate)
                
                converted_coordinates = {
                    'decimal': {'latitude': lat_decimal, 'longitude': lon_decimal},
                    'dms': {
                        'latitude': CoordinateConverter.decimal_to_dms(lat_decimal, True),
                        'longitude': CoordinateConverter.decimal_to_dms(lon_decimal, False)
                    },
                    'utm': CoordinateConverter.decimal_to_utm(lat_decimal, lon_decimal),
                    'mgrs': mgrs_coordinate
                }
        
        else:
            raise ValueError(f"Unsupported coordinate format: {format_type}")
        
        response = {
            'valid': validation_result['valid'],
            'format_type': format_type,
            'errors': validation_result.get('errors', []),
            'warnings': validation_result.get('warnings', []),
            'converted_coordinates': converted_coordinates
        }
        
        logger.info(f"Coordinate format validation result: valid={response['valid']}")
        return response
        
    except ValueError as e:
        logger.error(f"Coordinate format validation error: {e}")
        raise HTTPException(
            status_code=422,
            detail={
                "error": "INVALID_COORDINATE_FORMAT",
                "message": str(e),
                "suggested_actions": [
                    "Check coordinate format and values",
                    "Ensure all required fields are provided",
                    "Use decimal degrees format for simplicity"
                ]
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error during coordinate format validation: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "COORDINATE_VALIDATION_SERVICE_ERROR",
                "message": "Internal coordinate validation service error",
                "suggested_actions": [
                    "Try again in a few moments",
                    "Contact support if the problem persists",
                    "Use decimal degrees format as fallback"
                ]
            }
        )


@router.post("/parse-coordinate-string", response_model=Dict[str, Any])
async def parse_coordinate_string(request: Dict[str, str]) -> Dict[str, Any]:
    """
    Parse a coordinate string and determine its format.
    
    This endpoint automatically detects the format of a coordinate string
    and parses it into structured data for validation.
    
    Args:
        request: Dictionary with coordinate_string field
        
    Returns:
        Dictionary with parsed coordinate data and format information
    """
    try:
        coordinate_string = request.get('coordinate_string', '').strip()
        
        if not coordinate_string:
            raise ValueError("Empty coordinate string")
        
        logger.info(f"Parsing coordinate string: {coordinate_string}")
        
        parsed_data = CoordinateParser.parse_coordinate_string(coordinate_string)
        
        if not parsed_data:
            raise ValueError(f"Unable to parse coordinate string: {coordinate_string}")
        
        # Validate the parsed coordinates
        if parsed_data['format'] == 'decimal':
            validation_result = CoordinateValidator.validate_decimal_coordinates(
                parsed_data['latitude'], parsed_data['longitude']
            )
        elif parsed_data['format'] == 'dms':
            lat_data = parsed_data['latitude']
            lon_data = parsed_data['longitude']
            
            lat_validation = CoordinateValidator.validate_dms_coordinates(
                lat_data['degrees'], lat_data['minutes'], lat_data['seconds'], lat_data['direction'], True
            )
            lon_validation = CoordinateValidator.validate_dms_coordinates(
                lon_data['degrees'], lon_data['minutes'], lon_data['seconds'], lon_data['direction'], False
            )
            
            validation_result = {
                'valid': lat_validation['valid'] and lon_validation['valid'],
                'errors': lat_validation['errors'] + lon_validation['errors'],
                'warnings': lat_validation['warnings'] + lon_validation['warnings']
            }
        else:
            validation_result = {'valid': True, 'errors': [], 'warnings': []}
        
        response = {
            'parsed_data': parsed_data,
            'validation_result': validation_result,
            'original_string': coordinate_string
        }
        
        logger.info(f"Coordinate string parsing result: format={parsed_data['format']}, valid={validation_result['valid']}")
        return response
        
    except ValueError as e:
        logger.error(f"Coordinate string parsing error: {e}")
        raise HTTPException(
            status_code=422,
            detail={
                "error": "INVALID_COORDINATE_STRING",
                "message": str(e),
                "suggested_actions": [
                    "Check coordinate string format",
                    "Ensure proper spacing and punctuation",
                    "Try decimal degrees format: 'latitude, longitude'"
                ]
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error during coordinate string parsing: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "COORDINATE_PARSING_SERVICE_ERROR",
                "message": "Internal coordinate parsing service error",
                "suggested_actions": [
                    "Try again in a few moments",
                    "Contact support if the problem persists",
                    "Use a simpler coordinate format"
                ]
            }
        )


@router.post("/agricultural", response_model=ValidationResult)
async def validate_agricultural_location(request: LocationValidationRequest) -> ValidationResult:
    """
    Comprehensive agricultural location validation.
    
    This endpoint provides detailed validation for agricultural use including:
    - All basic coordinate validation
    - Detailed agricultural area analysis
    - Climate zone assessment with agricultural context
    - Soil region information
    - Agricultural suitability scoring
    
    Args:
        request: LocationValidationRequest with latitude and longitude
        
    Returns:
        ValidationResult with comprehensive agricultural validation
        
    Raises:
        HTTPException: If validation fails or service error occurs
    """
    try:
        logger.info(f"Performing agricultural validation for coordinates: {request.latitude}, {request.longitude}")
        
        result = await validation_service.validate_agricultural_location(
            request.latitude,
            request.longitude
        )
        
        logger.info(f"Agricultural validation result: valid={result.valid}, agricultural={result.geographic_info.is_agricultural if result.geographic_info else 'unknown'}")
        
        return result
        
    except ValueError as e:
        logger.error(f"Agricultural validation error: {e}")
        raise HTTPException(
            status_code=422,
            detail={
                "error": LOCATION_ERRORS["INVALID_COORDINATES"].dict(),
                "details": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error during agricultural validation: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "error_code": "AGRICULTURAL_VALIDATION_ERROR",
                    "error_message": "Internal agricultural validation service error",
                    "agricultural_context": "Unable to assess agricultural suitability for location",
                    "suggested_actions": [
                        "Try again in a few moments",
                        "Use basic coordinate validation instead",
                        "Contact agricultural support for manual assessment"
                    ]
                }
            }
        )


@router.get("/agricultural-address-suggestions")
async def get_agricultural_address_suggestions(
    query: str, 
    limit: int = 5,
    prioritize_agricultural: bool = Query(True, description="Prioritize agricultural locations")
) -> Dict[str, Any]:
    """
    Get comprehensive agricultural address autocomplete suggestions.
    
    This endpoint provides enhanced address autocomplete functionality specifically
    designed for agricultural and rural addresses, integrating multiple data sources
    including USGS GNIS, USDA farm service agency, and postal service databases.
    
    Features:
    - Real-time address suggestions with agricultural focus
    - Rural address support (RR, HC, PO Box patterns)
    - Agricultural area prioritization
    - Farm-specific address patterns
    - Integration with agricultural databases
    
    Args:
        query: Address query string (minimum 3 characters)
        limit: Maximum number of suggestions to return (default: 5, max: 10)
        prioritize_agricultural: Whether to prioritize agricultural locations
        
    Returns:
        Dict with agricultural suggestions list and metadata
        
    Raises:
        HTTPException: If query is invalid
    """
    try:
        # Validate query length
        if not query or len(query.strip()) < 3:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": {
                        "error_code": "QUERY_TOO_SHORT",
                        "error_message": "Query must be at least 3 characters long",
                        "agricultural_context": "Longer queries provide more accurate agricultural address suggestions",
                        "suggested_actions": [
                            "Enter at least 3 characters",
                            "Include street name or city",
                            "Try farm name or rural route number"
                        ]
                    }
                }
            )
        
        # Limit the maximum number of suggestions
        limit = min(max(1, limit), 10)
        
        logger.info(f"Getting agricultural address suggestions for query: {query} (limit: {limit}, prioritize: {prioritize_agricultural})")
        
        suggestions = await geocoding_service.get_agricultural_address_suggestions(
            query, limit, prioritize_agricultural
        )
        
        logger.info(f"Retrieved {len(suggestions)} agricultural suggestions for query: {query}")
        
        return {
            "query": query,
            "suggestions": [suggestion.dict() for suggestion in suggestions],
            "count": len(suggestions),
            "limit": limit,
            "prioritize_agricultural": prioritize_agricultural,
            "features": {
                "rural_address_support": True,
                "agricultural_area_prioritization": prioritize_agricultural,
                "usgs_gnis_integration": True,
                "usda_farm_service_integration": True,
                "postal_service_integration": True
            }
        }
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Unexpected error getting agricultural address suggestions: {e}")
        # Don't fail hard for suggestions - return empty list
        return {
            "query": query,
            "suggestions": [],
            "count": 0,
            "limit": limit,
            "prioritize_agricultural": prioritize_agricultural,
            "error": "Agricultural address service temporarily unavailable"
        }


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for the location validation service.
    
    Returns:
        Dict with service status and basic information
    """
    try:
        # Test basic service functionality
        test_result = await validation_service.validate_coordinates(42.0, -93.0)
        
        return {
            "status": "healthy",
            "service": "location-validation",
            "version": "1.0",
            "timestamp": "2024-12-09T10:30:00Z",
            "test_validation": {
                "coordinates_tested": [42.0, -93.0],
                "validation_successful": test_result.valid
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "location-validation",
            "version": "1.0",
            "timestamp": "2024-12-09T10:30:00Z",
            "error": str(e)
        }


@router.get("/errors/{error_code}")
async def get_validation_error(error_code: str) -> LocationError:
    """
    Get information about a specific validation error code.
    
    Args:
        error_code: The error code to look up
        
    Returns:
        LocationError with details about the error
        
    Raises:
        HTTPException: If error code is not found
    """
    try:
        error = await validation_service.get_validation_error(error_code)
        return error
    except Exception as e:
        logger.error(f"Error retrieving validation error info: {e}")
        raise HTTPException(
            status_code=404,
            detail={
                "error": LOCATION_ERRORS["LOCATION_NOT_FOUND"].dict(),
                "details": f"Error code '{error_code}' not found"
            }
        )


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


@router.get("/address-suggestions")
async def get_address_suggestions(query: str, limit: int = 5) -> Dict[str, Any]:
    """
    Get address autocomplete suggestions.
    
    This endpoint provides address autocomplete suggestions for user input,
    helping users find and select valid addresses quickly.
    
    Args:
        query: Partial address query (minimum 3 characters)
        limit: Maximum number of suggestions to return (default: 5, max: 10)
        
    Returns:
        Dict with suggestions list and metadata
        
    Raises:
        HTTPException: If query is invalid
    """
    try:
        # Validate query length
        if not query or len(query.strip()) < 3:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": {
                        "error_code": "QUERY_TOO_SHORT",
                        "error_message": "Query must be at least 3 characters long",
                        "agricultural_context": "Longer queries provide more accurate address suggestions",
                        "suggested_actions": [
                            "Enter at least 3 characters",
                            "Include street name or city",
                            "Be more specific with your search"
                        ]
                    }
                }
            )
        
        # Limit the maximum number of suggestions
        limit = min(max(1, limit), 10)
        
        logger.info(f"Getting address suggestions for query: {query} (limit: {limit})")
        
        suggestions = await geocoding_service.get_address_suggestions(query, limit)
        
        logger.info(f"Retrieved {len(suggestions)} suggestions for query: {query}")
        
        return {
            "query": query,
            "suggestions": [suggestion.dict() for suggestion in suggestions],
            "count": len(suggestions),
            "limit": limit
        }
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Unexpected error getting address suggestions: {e}")
        # Don't fail hard for suggestions - return empty list
        return {
            "query": query,
            "suggestions": [],
            "count": 0,
            "limit": limit,
            "error": "Service temporarily unavailable"
        }


@router.post("/climate-analysis", response_model=Dict[str, Any])
async def get_climate_analysis(request: LocationValidationRequest) -> Dict[str, Any]:
    """
    Get comprehensive climate analysis for coordinates.
    
    This endpoint provides detailed climate information including:
    - USDA Hardiness Zone with historical weather data analysis
    - Köppen climate classification
    - Growing season details (length, frost dates)
    - Temperature and precipitation patterns
    - Agricultural suitability assessment
    - Climate-based crop recommendations
    
    Args:
        request: LocationValidationRequest with latitude and longitude
        
    Returns:
        Dict with comprehensive climate analysis data
        
    Raises:
        HTTPException: If analysis fails or coordinates are invalid
    """
    try:
        logger.info(f"Performing climate analysis for coordinates: {request.latitude}, {request.longitude}")
        
        analysis = await validation_service.get_comprehensive_climate_analysis(
            request.latitude,
            request.longitude
        )
        
        # Check if analysis was successful
        if analysis.get('error'):
            logger.warning(f"Climate analysis returned error: {analysis['error']}")
            return {
                "success": False,
                "error": analysis['error'],
                "basic_climate_zone": analysis.get('basic_zone'),
                "message": "Enhanced climate analysis not available, basic zone provided"
            }
        
        logger.info(f"Climate analysis successful: USDA Zone {analysis.get('usda_zone')}, Köppen {analysis.get('koppen_classification')}")
        
        return {
            "success": True,
            "coordinates": {
                "latitude": request.latitude,
                "longitude": request.longitude
            },
            "climate_data": analysis
        }
        
    except ValueError as e:
        logger.error(f"Climate analysis validation error: {e}")
        raise HTTPException(
            status_code=422,
            detail={
                "error": LOCATION_ERRORS["INVALID_COORDINATES"].dict(),
                "details": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error during climate analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "error_code": "CLIMATE_ANALYSIS_ERROR",
                    "error_message": "Internal climate analysis service error",
                    "agricultural_context": "Unable to analyze climate conditions for agricultural planning",
                    "suggested_actions": [
                        "Try again in a few moments",
                        "Use basic coordinate validation instead",
                        "Contact support for manual climate assessment"
                    ]
                }
            }
        )


@router.post("/batch-geocode", response_model=BatchGeocodingResponse)
async def batch_geocode_addresses(request: BatchGeocodingRequest) -> BatchGeocodingResponse:
    """
    Geocode multiple addresses in batch with agricultural context enhancement.
    
    This endpoint processes multiple addresses concurrently for efficient
    geocoding with agricultural context data including USDA zones, climate
    zones, soil survey areas, and agricultural districts.
    
    Args:
        request: BatchGeocodingRequest with addresses list and options
        
    Returns:
        BatchGeocodingResponse with results, failed addresses, and statistics
        
    Raises:
        HTTPException: If request is invalid or processing fails
    """
    try:
        logger.info(f"Batch geocoding {len(request.addresses)} addresses (agricultural context: {request.include_agricultural_context})")
        
        # Validate request
        if not request.addresses:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": {
                        "error_code": "EMPTY_ADDRESS_LIST",
                        "error_message": "Address list cannot be empty",
                        "agricultural_context": "At least one address is required for batch geocoding",
                        "suggested_actions": [
                            "Provide at least one address",
                            "Check address format",
                            "Ensure addresses are valid"
                        ]
                    }
                }
            )
        
        if len(request.addresses) > 100:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": {
                        "error_code": "TOO_MANY_ADDRESSES",
                        "error_message": "Maximum 100 addresses allowed per batch request",
                        "agricultural_context": "Large batches may impact performance and agricultural data accuracy",
                        "suggested_actions": [
                            "Split into smaller batches",
                            "Use individual geocoding for critical addresses",
                            "Contact support for bulk processing"
                        ]
                    }
                }
            )
        
        result = await geocoding_service.batch_geocode(request)
        
        logger.info(f"Batch geocoding completed: {result.success_count} successful, {result.failure_count} failed")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during batch geocoding: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "error_code": "BATCH_GEOCODING_ERROR",
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


# Import location management routes
from .location_routes import router as location_management_router

# Include address validation routes
router.include_router(address_validation_router)

# Export routers
__all__ = ['router', 'location_management_router', 'address_validation_router']