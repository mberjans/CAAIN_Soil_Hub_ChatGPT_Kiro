"""
Current Location Detection API Routes
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

API endpoints for comprehensive current location detection system.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import List, Optional, Dict, Any
import logging
from uuid import uuid4

from ..services.current_location_detection_service import (
    CurrentLocationDetectionService,
    LocationReading,
    LocationDetectionResult,
    LocationHistoryEntry,
    LocationSource,
    LocationAccuracy
)

# Initialize logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/current-location", tags=["current-location"])

# Dependency injection
async def get_current_location_service() -> CurrentLocationDetectionService:
    return CurrentLocationDetectionService()


@router.post("/detect", response_model=LocationDetectionResult)
async def detect_current_location(
    user_id: str = Body(..., description="User identifier"),
    session_id: str = Body(..., description="Session identifier"),
    preferred_sources: Optional[List[LocationSource]] = Body(None, description="Preferred location sources in order"),
    privacy_level: str = Body("standard", description="Privacy level (minimal, standard, enhanced)"),
    battery_level: Optional[int] = Body(None, description="Current battery level percentage"),
    service: CurrentLocationDetectionService = Depends(get_current_location_service)
):
    """
    Detect current location using multiple fallback methods.
    
    This endpoint provides comprehensive location detection with:
    - GPS location detection with high-accuracy and assisted GPS
    - IP-based geolocation fallback
    - Manual location entry
    - Location history management
    - Privacy controls and location permission management
    - Battery optimization and location caching
    
    Agricultural Use Cases:
    - Automatic farm location detection for new users
    - Field location detection for mobile field mapping
    - Location-based climate zone auto-detection
    - GPS-assisted field boundary creation
    """
    try:
        result = await service.detect_current_location(
            user_id=user_id,
            session_id=session_id,
            preferred_sources=preferred_sources,
            privacy_level=privacy_level,
            battery_level=battery_level
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error detecting current location: {e}")
        raise HTTPException(status_code=500, detail=f"Location detection failed: {str(e)}")


@router.get("/history", response_model=List[LocationHistoryEntry])
async def get_location_history(
    user_id: str = Query(..., description="User identifier"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of entries to return"),
    include_favorites_only: bool = Query(False, description="Return only favorite locations"),
    service: CurrentLocationDetectionService = Depends(get_current_location_service)
):
    """
    Get location history for a user.
    
    Returns recent location history including:
    - GPS readings
    - IP geolocation results
    - Manual entries
    - Saved favorite locations
    
    Agricultural Use Cases:
    - Review previous farm visits
    - Access saved field locations
    - Track location accuracy over time
    - Manage multiple farm locations
    """
    try:
        history = await service.get_location_history(
            user_id=user_id,
            limit=limit,
            include_favorites_only=include_favorites_only
        )
        
        return history
        
    except Exception as e:
        logger.error(f"Error getting location history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get location history: {str(e)}")


@router.post("/favorite", response_model=Dict[str, Any])
async def save_location_as_favorite(
    location: LocationReading = Body(..., description="Location to save as favorite"),
    user_id: str = Body(..., description="User identifier"),
    session_id: str = Body(..., description="Session identifier"),
    notes: Optional[str] = Body(None, description="Optional notes about the location"),
    service: CurrentLocationDetectionService = Depends(get_current_location_service)
):
    """
    Save a location as favorite for quick access.
    
    Agricultural Use Cases:
    - Save frequently visited farm locations
    - Mark important field locations
    - Store home farm coordinates
    - Save supplier or equipment locations
    """
    try:
        success = await service.save_location_as_favorite(
            location=location,
            user_id=user_id,
            session_id=session_id,
            notes=notes
        )
        
        return {
            "success": success,
            "message": "Location saved as favorite" if success else "Failed to save location as favorite"
        }
        
    except Exception as e:
        logger.error(f"Error saving favorite location: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save favorite location: {str(e)}")


@router.get("/permissions", response_model=Dict[str, Any])
async def get_location_permissions_status(
    service: CurrentLocationDetectionService = Depends(get_current_location_service)
):
    """
    Get current location permissions status.
    
    Returns information about:
    - GPS availability
    - Permission status
    - Location services status
    - Privacy mode status
    - Battery optimization status
    
    Agricultural Use Cases:
    - Check if GPS is available for field mapping
    - Verify location permissions for mobile use
    - Monitor battery optimization settings
    - Ensure privacy compliance
    """
    try:
        status = await service.get_location_permissions_status()
        return status
        
    except Exception as e:
        logger.error(f"Error getting permissions status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get permissions status: {str(e)}")


@router.post("/permissions/request", response_model=Dict[str, Any])
async def request_location_permission(
    user_id: str = Body(..., description="User identifier"),
    service: CurrentLocationDetectionService = Depends(get_current_location_service)
):
    """
    Request location permission from user.
    
    This endpoint initiates the location permission request process.
    In a real implementation, this would trigger browser permission dialogs.
    
    Agricultural Use Cases:
    - Request GPS permission for field mapping
    - Enable location services for farm management
    - Allow location-based recommendations
    - Enable mobile field tracking
    """
    try:
        result = await service.request_location_permission(user_id=user_id)
        return result
        
    except Exception as e:
        logger.error(f"Error requesting location permission: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to request location permission: {str(e)}")


@router.get("/sources", response_model=List[Dict[str, Any]])
async def get_available_location_sources():
    """
    Get available location detection sources.
    
    Returns information about all available location detection methods:
    - GPS
    - IP geolocation
    - Manual entry
    - Saved locations
    - Network location
    - Cell tower
    - WiFi network
    
    Agricultural Use Cases:
    - Show available location options to users
    - Explain accuracy differences between methods
    - Help users choose appropriate detection method
    - Display fallback options when GPS fails
    """
    sources = [
        {
            "source": LocationSource.GPS.value,
            "name": "GPS",
            "description": "High-accuracy GPS location using satellite signals",
            "accuracy": "High (< 10 meters)",
            "battery_impact": "High",
            "privacy_level": "Standard",
            "requires_permission": True,
            "agricultural_suitability": "Excellent for field mapping and precision agriculture"
        },
        {
            "source": LocationSource.IP_GEOLOCATION.value,
            "name": "IP Geolocation",
            "description": "Location based on IP address",
            "accuracy": "Low (~1 km)",
            "battery_impact": "Low",
            "privacy_level": "Minimal",
            "requires_permission": False,
            "agricultural_suitability": "Good for general farm location, not suitable for field-level precision"
        },
        {
            "source": LocationSource.MANUAL_ENTRY.value,
            "name": "Manual Entry",
            "description": "User-entered coordinates or address",
            "accuracy": "Variable",
            "battery_impact": "Minimal",
            "privacy_level": "Minimal",
            "requires_permission": False,
            "agricultural_suitability": "Good for known locations, requires user knowledge"
        },
        {
            "source": LocationSource.SAVED_LOCATION.value,
            "name": "Saved Location",
            "description": "Previously saved favorite location",
            "accuracy": "High (from original source)",
            "battery_impact": "Minimal",
            "privacy_level": "Minimal",
            "requires_permission": False,
            "agricultural_suitability": "Excellent for frequently visited farm locations"
        },
        {
            "source": LocationSource.NETWORK_LOCATION.value,
            "name": "Network Location",
            "description": "Location based on network infrastructure",
            "accuracy": "Medium (~100 meters)",
            "battery_impact": "Low",
            "privacy_level": "Standard",
            "requires_permission": True,
            "agricultural_suitability": "Good for general farm location"
        },
        {
            "source": LocationSource.CELL_TOWER.value,
            "name": "Cell Tower",
            "description": "Location based on cellular tower triangulation",
            "accuracy": "Medium (~500 meters)",
            "battery_impact": "Medium",
            "privacy_level": "Standard",
            "requires_permission": True,
            "agricultural_suitability": "Good for rural farm locations"
        },
        {
            "source": LocationSource.WIFI_NETWORK.value,
            "name": "WiFi Network",
            "description": "Location based on WiFi network identification",
            "accuracy": "Medium (~50 meters)",
            "battery_impact": "Low",
            "privacy_level": "Standard",
            "requires_permission": True,
            "agricultural_suitability": "Good for farm buildings and structures"
        }
    ]
    
    return sources


@router.get("/health")
async def health_check():
    """Health check endpoint for current location detection service."""
    return {
        "status": "healthy",
        "service": "current-location-detection",
        "version": "1.0",
        "features": [
            "GPS location detection",
            "IP geolocation fallback",
            "Location history management",
            "Battery optimization",
            "Privacy controls",
            "Multiple fallback methods"
        ]
    }


# Additional utility endpoints

@router.post("/validate", response_model=Dict[str, Any])
async def validate_detected_location(
    location: LocationReading = Body(..., description="Location to validate"),
    service: CurrentLocationDetectionService = Depends(get_current_location_service)
):
    """
    Validate a detected location for agricultural suitability.
    
    This endpoint validates detected locations using the existing
    location validation service to ensure they are suitable for
    agricultural recommendations.
    
    Agricultural Use Cases:
    - Validate GPS readings before saving
    - Check IP geolocation accuracy
    - Ensure locations are in agricultural areas
    - Verify coordinates are valid for farming
    """
    try:
        # Use the validation service to validate the location
        validation_result = await service.validation_service.validate_coordinates(
            location.latitude,
            location.longitude
        )
        
        return {
            "location": {
                "latitude": location.latitude,
                "longitude": location.longitude,
                "source": location.source.value,
                "accuracy_meters": location.accuracy_meters,
                "confidence_score": location.confidence_score
            },
            "validation": {
                "valid": validation_result.valid,
                "warnings": validation_result.warnings,
                "errors": validation_result.errors,
                "geographic_info": validation_result.geographic_info
            },
            "agricultural_assessment": {
                "suitable_for_agriculture": validation_result.geographic_info.is_agricultural if validation_result.geographic_info else False,
                "recommendations": validation_result.warnings if validation_result.warnings else []
            }
        }
        
    except Exception as e:
        logger.error(f"Error validating location: {e}")
        raise HTTPException(status_code=500, detail=f"Location validation failed: {str(e)}")


@router.get("/accuracy-levels", response_model=List[Dict[str, Any]])
async def get_location_accuracy_levels():
    """
    Get information about location accuracy levels.
    
    Returns detailed information about different accuracy levels
    and their implications for agricultural use.
    """
    accuracy_levels = [
        {
            "level": LocationAccuracy.HIGH.value,
            "name": "High Accuracy",
            "range": "< 10 meters",
            "description": "Very precise location suitable for precision agriculture",
            "agricultural_uses": [
                "Field boundary mapping",
                "Precision planting",
                "Variable rate application",
                "Yield mapping",
                "Soil sampling"
            ],
            "typical_sources": ["GPS", "RTK GPS", "Assisted GPS"]
        },
        {
            "level": LocationAccuracy.MEDIUM.value,
            "name": "Medium Accuracy",
            "range": "10-100 meters",
            "description": "Good accuracy suitable for general farm management",
            "agricultural_uses": [
                "Field identification",
                "General farm mapping",
                "Equipment tracking",
                "Weather station placement",
                "Farm building location"
            ],
            "typical_sources": ["GPS", "Network location", "WiFi network"]
        },
        {
            "level": LocationAccuracy.LOW.value,
            "name": "Low Accuracy",
            "range": "100-1000 meters",
            "description": "Basic accuracy suitable for general location identification",
            "agricultural_uses": [
                "General farm location",
                "Regional climate assessment",
                "County-level analysis",
                "General recommendations"
            ],
            "typical_sources": ["IP geolocation", "Cell tower", "Network location"]
        },
        {
            "level": LocationAccuracy.VERY_LOW.value,
            "name": "Very Low Accuracy",
            "range": "> 1000 meters",
            "description": "Low accuracy suitable only for very general purposes",
            "agricultural_uses": [
                "State-level analysis",
                "General climate zone identification",
                "Broad regional recommendations"
            ],
            "typical_sources": ["IP geolocation", "Manual entry"]
        }
    ]
    
    return accuracy_levels


# Export the router
__all__ = ['router']
