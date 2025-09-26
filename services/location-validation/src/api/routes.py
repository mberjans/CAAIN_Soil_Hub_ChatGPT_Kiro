"""
Location Validation API Routes
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

FastAPI routes for location validation endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging
import sys
import os

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../databases/python'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../services'))

from location_models import (
    LocationValidationRequest, ValidationResult, LocationError, LOCATION_ERRORS
)
from location_validation_service import LocationValidationService
from geocoding_service import (
    GeocodingResult, AddressResult, AddressSuggestion, 
    GeocodingError, get_geocoding_service
)

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
async def geocode_address(address: str) -> GeocodingResult:
    """
    Convert street address to GPS coordinates.
    
    This endpoint geocodes a street address to GPS coordinates using
    OpenStreetMap Nominatim service with caching for performance.
    
    Args:
        address: Street address to geocode (e.g., "123 Main St, Ames, IA")
        
    Returns:
        GeocodingResult with coordinates, formatted address, and confidence score
        
    Raises:
        HTTPException: If geocoding fails or address is invalid
    """
    try:
        logger.info(f"Geocoding address: {address}")
        
        result = await geocoding_service.geocode_address(address)
        
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
async def reverse_geocode_coordinates(latitude: float, longitude: float) -> AddressResult:
    """
    Convert GPS coordinates to street address.
    
    This endpoint performs reverse geocoding to convert GPS coordinates
    back to a human-readable street address.
    
    Args:
        latitude: Latitude in decimal degrees (-90 to 90)
        longitude: Longitude in decimal degrees (-180 to 180)
        
    Returns:
        AddressResult with formatted address and components
        
    Raises:
        HTTPException: If reverse geocoding fails or coordinates are invalid
    """
    try:
        logger.info(f"Reverse geocoding coordinates: {latitude}, {longitude}")
        
        result = await geocoding_service.reverse_geocode(latitude, longitude)
        
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


# Export router
__all__ = ['router']