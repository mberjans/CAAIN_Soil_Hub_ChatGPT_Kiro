"""
Climate Zone Detection API Routes
FastAPI routes for climate zone detection and management.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator
import logging
from datetime import datetime

from ..services.climate_zone_service import climate_zone_service, ClimateZoneType
from ..services.coordinate_climate_detector import coordinate_climate_detector
from ..services.usda_zone_api import usda_zone_api
from ..services.koppen_climate_service import koppen_climate_service, KoppenGroup
from ..services.address_climate_lookup import address_climate_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/climate", tags=["climate"])


# Request/Response Models
class LocationRequest(BaseModel):
    """Location data for climate detection."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    elevation_ft: Optional[float] = Field(None, description="Elevation in feet")
    
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


class ClimateZoneResponse(BaseModel):
    """Climate zone detection response."""
    primary_zone: Dict
    alternative_zones: List[Dict]
    confidence_score: float
    detection_method: str
    coordinates: tuple
    elevation_ft: Optional[float]
    climate_adjustments: Dict
    detection_metadata: Dict


class ZoneValidationRequest(BaseModel):
    """Zone validation request."""
    zone_id: str = Field(..., description="Climate zone ID to validate")
    zone_type: str = Field(..., description="Type of climate zone")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class ZoneValidationResponse(BaseModel):
    """Zone validation response."""
    valid: bool
    confidence: float
    message: str
    detected_zone: str
    specified_zone: str
    recommendations: Optional[List[str]] = None


class AddressClimateResponse(BaseModel):
    """Address-based climate zone detection response."""
    address: str
    geocoded_coordinates: Optional[tuple]
    climate_data: Optional[Dict]
    geocoding_confidence: float
    address_components: Dict
    lookup_method: str
    success: bool = True
    message: Optional[str] = None


# API Endpoints

@router.post("/detect-zone", response_model=ClimateZoneResponse)
async def detect_climate_zone(location: LocationRequest):
    """
    Auto-detect climate zone from coordinates.
    
    Detects USDA hardiness zone, Köppen climate type, and agricultural zone
    based on GPS coordinates with elevation adjustments.
    """
    try:
        logger.info(f"Detecting climate zone for {location.latitude}, {location.longitude}")
        
        # Detect comprehensive climate data
        climate_data = await coordinate_climate_detector.detect_climate_from_coordinates(
            latitude=location.latitude,
            longitude=location.longitude,
            elevation_ft=location.elevation_ft,
            include_detailed_analysis=True
        )
        
        # Format primary zone
        primary_zone = {
            "zone_id": climate_data.usda_zone.zone if climate_data.usda_zone else "unknown",
            "zone_type": "usda_hardiness",
            "name": f"USDA Zone {climate_data.usda_zone.zone}" if climate_data.usda_zone else "Unknown",
            "description": climate_data.usda_zone.description if climate_data.usda_zone else "Unknown zone",
            "temperature_range_f": climate_data.usda_zone.temperature_range if climate_data.usda_zone else None,
            "source": climate_data.usda_zone.source if climate_data.usda_zone else "unknown"
        }
        
        # Format alternative zones
        alternative_zones = []
        if climate_data.koppen_analysis:
            alternative_zones.append({
                "zone_id": climate_data.koppen_analysis.koppen_type.code,
                "zone_type": "koppen",
                "name": climate_data.koppen_analysis.koppen_type.name,
                "description": climate_data.koppen_analysis.koppen_type.description,
                "agricultural_suitability": climate_data.koppen_analysis.koppen_type.agricultural_suitability,
                "growing_season_months": climate_data.koppen_analysis.koppen_type.growing_season_months
            })
        
        response = ClimateZoneResponse(
            primary_zone=primary_zone,
            alternative_zones=alternative_zones,
            confidence_score=climate_data.confidence_factors.get("overall_confidence", 0.7),
            detection_method="coordinate_based_comprehensive",
            coordinates=(location.latitude, location.longitude),
            elevation_ft=climate_data.elevation_data.elevation_ft if climate_data.elevation_data else location.elevation_ft,
            climate_adjustments=climate_data.climate_adjustments,
            detection_metadata=climate_data.detection_metadata
        )
        
        logger.info(f"Successfully detected climate zone {primary_zone['zone_id']} for {location.latitude}, {location.longitude}")
        return response
        
    except Exception as e:
        logger.error(f"Error detecting climate zone: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Climate zone detection failed: {str(e)}")


@router.get("/zones")
async def list_climate_zones(
    zone_type: Optional[str] = Query(None, description="Filter by zone type (usda_hardiness, koppen, agricultural)"),
    group: Optional[str] = Query(None, description="Filter Köppen zones by group (A, B, C, D, E)")
):
    """
    List available climate zones.
    
    Returns all available climate zones, optionally filtered by type or group.
    """
    try:
        zones = []
        
        if not zone_type or zone_type == "usda_hardiness":
            usda_zones = climate_zone_service.list_zones(ClimateZoneType.USDA_HARDINESS)
            for zone in usda_zones:
                zones.append({
                    "zone_id": zone.zone_id,
                    "zone_type": "usda_hardiness",
                    "name": zone.name,
                    "description": zone.description,
                    "min_temp_f": zone.min_temp_f,
                    "max_temp_f": zone.max_temp_f,
                    "characteristics": zone.characteristics
                })
        
        if not zone_type or zone_type == "koppen":
            koppen_group = None
            if group:
                try:
                    koppen_group = KoppenGroup(group.upper())
                except ValueError:
                    raise HTTPException(status_code=400, detail=f"Invalid Köppen group: {group}")
            
            koppen_zones = koppen_climate_service.list_climate_types(koppen_group)
            for zone in koppen_zones:
                zones.append({
                    "zone_id": zone.code,
                    "zone_type": "koppen",
                    "name": zone.name,
                    "description": zone.description,
                    "group": zone.group.value,
                    "temperature_pattern": zone.temperature_pattern,
                    "precipitation_pattern": zone.precipitation_pattern,
                    "agricultural_suitability": zone.agricultural_suitability,
                    "growing_season_months": zone.growing_season_months
                })
        
        if not zone_type or zone_type == "agricultural":
            ag_zones = climate_zone_service.list_zones(ClimateZoneType.AGRICULTURAL)
            for zone in ag_zones:
                zones.append({
                    "zone_id": zone.zone_id,
                    "zone_type": "agricultural",
                    "name": zone.name,
                    "description": zone.description,
                    "growing_season_days": zone.growing_season_days,
                    "characteristics": zone.characteristics
                })
        
        return {
            "zones": zones,
            "total_count": len(zones),
            "filters_applied": {
                "zone_type": zone_type,
                "group": group
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing climate zones: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list climate zones: {str(e)}")


@router.get("/zone/{zone_id}")
async def get_zone_details(
    zone_id: str,
    zone_type: str = Query(..., description="Zone type (usda_hardiness, koppen, agricultural)")
):
    """
    Get detailed information about a specific climate zone.
    """
    try:
        # Validate zone type
        try:
            if zone_type == "usda_hardiness":
                zone_type_enum = ClimateZoneType.USDA_HARDINESS
            elif zone_type == "koppen":
                zone_type_enum = ClimateZoneType.KOPPEN
            elif zone_type == "agricultural":
                zone_type_enum = ClimateZoneType.AGRICULTURAL
            else:
                raise ValueError(f"Invalid zone type: {zone_type}")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Get zone details
        if zone_type == "usda_hardiness":
            zone = climate_zone_service.get_zone_by_id(zone_id, zone_type_enum)
            if not zone:
                # Try getting details from USDA API
                async with usda_zone_api as api:
                    zone_details = await api.get_zone_details(zone_id)
                if zone_details:
                    return zone_details
                else:
                    raise HTTPException(status_code=404, detail=f"USDA zone {zone_id} not found")
            
            return {
                "zone_id": zone.zone_id,
                "zone_type": "usda_hardiness",
                "name": zone.name,
                "description": zone.description,
                "temperature_range_f": (zone.min_temp_f, zone.max_temp_f),
                "temperature_range_c": (
                    round((zone.min_temp_f - 32) * 5/9, 1) if zone.min_temp_f else None,
                    round((zone.max_temp_f - 32) * 5/9, 1) if zone.max_temp_f else None
                ),
                "growing_season_days": zone.growing_season_days,
                "characteristics": zone.characteristics
            }
        
        elif zone_type == "koppen":
            zone = koppen_climate_service.get_climate_type_by_code(zone_id)
            if not zone:
                raise HTTPException(status_code=404, detail=f"Köppen zone {zone_id} not found")
            
            return {
                "zone_id": zone.code,
                "zone_type": "koppen",
                "name": zone.name,
                "description": zone.description,
                "group": zone.group.value,
                "temperature_pattern": zone.temperature_pattern,
                "precipitation_pattern": zone.precipitation_pattern,
                "agricultural_suitability": zone.agricultural_suitability,
                "typical_vegetation": zone.typical_vegetation,
                "growing_season_months": zone.growing_season_months,
                "water_balance": zone.water_balance
            }
        
        else:  # agricultural
            zone = climate_zone_service.get_zone_by_id(zone_id, zone_type_enum)
            if not zone:
                raise HTTPException(status_code=404, detail=f"Agricultural zone {zone_id} not found")
            
            return {
                "zone_id": zone.zone_id,
                "zone_type": "agricultural",
                "name": zone.name,
                "description": zone.description,
                "growing_season_days": zone.growing_season_days,
                "characteristics": zone.characteristics
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting zone details for {zone_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get zone details: {str(e)}")


@router.post("/validate-zone", response_model=ZoneValidationResponse)
async def validate_zone_selection(request: ZoneValidationRequest):
    """
    Validate if a climate zone selection is appropriate for a location.
    """
    try:
        # Validate zone type
        try:
            if request.zone_type == "usda_hardiness":
                zone_type_enum = ClimateZoneType.USDA_HARDINESS
            elif request.zone_type == "koppen":
                zone_type_enum = ClimateZoneType.KOPPEN
            elif request.zone_type == "agricultural":
                zone_type_enum = ClimateZoneType.AGRICULTURAL
            else:
                raise ValueError(f"Invalid zone type: {request.zone_type}")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Validate zone for location
        validation_result = await climate_zone_service.validate_zone_for_location(
            zone_id=request.zone_id,
            zone_type=zone_type_enum,
            latitude=request.latitude,
            longitude=request.longitude
        )
        
        # Add recommendations if zone is not optimal
        recommendations = []
        if not validation_result["valid"]:
            recommendations.extend([
                f"Consider using detected zone {validation_result['detected_zone']} for better accuracy",
                "Consult local agricultural extension service for zone confirmation",
                "Monitor local weather patterns to verify zone appropriateness"
            ])
        
        return ZoneValidationResponse(
            valid=validation_result["valid"],
            confidence=validation_result["confidence"],
            message=validation_result["message"],
            detected_zone=validation_result["detected_zone"],
            specified_zone=validation_result["specified_zone"],
            recommendations=recommendations if recommendations else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating zone selection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Zone validation failed: {str(e)}")


@router.get("/usda-zones")
async def get_usda_zones():
    """
    Get all USDA hardiness zones with details.
    """
    try:
        zones = climate_zone_service.list_zones(ClimateZoneType.USDA_HARDINESS)
        
        usda_zones = []
        for zone in zones:
            usda_zones.append({
                "zone": zone.zone_id,
                "name": zone.name,
                "description": zone.description,
                "temperature_range_f": (zone.min_temp_f, zone.max_temp_f),
                "temperature_range_c": (
                    round((zone.min_temp_f - 32) * 5/9, 1) if zone.min_temp_f else None,
                    round((zone.max_temp_f - 32) * 5/9, 1) if zone.max_temp_f else None
                ),
                "suitable_crops": zone.characteristics.get("suitable_for", []) if zone.characteristics else []
            })
        
        return {
            "usda_zones": sorted(usda_zones, key=lambda x: x["zone"]),
            "total_zones": len(usda_zones),
            "note": "USDA Plant Hardiness Zones for North America"
        }
        
    except Exception as e:
        logger.error(f"Error getting USDA zones: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get USDA zones: {str(e)}")


@router.get("/koppen-types")
async def get_koppen_types(group: Optional[str] = Query(None, description="Filter by Köppen group (A, B, C, D, E)")):
    """
    Get Köppen climate classification types.
    """
    try:
        koppen_group = None
        if group:
            try:
                koppen_group = KoppenGroup(group.upper())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid Köppen group: {group}")
        
        climate_types = koppen_climate_service.list_climate_types(koppen_group)
        
        types = []
        for climate_type in climate_types:
            types.append({
                "code": climate_type.code,
                "name": climate_type.name,
                "description": climate_type.description,
                "group": climate_type.group.value,
                "temperature_pattern": climate_type.temperature_pattern,
                "precipitation_pattern": climate_type.precipitation_pattern,
                "agricultural_suitability": climate_type.agricultural_suitability,
                "typical_vegetation": climate_type.typical_vegetation,
                "growing_season_months": climate_type.growing_season_months
            })
        
        return {
            "koppen_types": sorted(types, key=lambda x: x["code"]),
            "total_types": len(types),
            "group_filter": group,
            "note": "Köppen Climate Classification System"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting Köppen types: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get Köppen types: {str(e)}")


@router.post("/zone-from-address", response_model=AddressClimateResponse)
async def get_zone_from_address(
    address: str = Query(..., description="Address to geocode and detect climate zone"),
    include_koppen: bool = Query(False, description="Include Köppen climate analysis")
):
    """
    Detect climate zone from address using geocoding.
    
    This endpoint uses multiple lookup methods:
    1. Full geocoding (most accurate)
    2. ZIP code lookup 
    3. State/county lookup
    4. Fallback methods
    """
    try:
        logger.info(f"Getting climate zone from address: {address}")
        
        # Use the address climate service to get climate data
        result = await address_climate_service.get_climate_from_address(
            address=address,
            country="US"
        )
        
        # Format climate data for response
        climate_data = None
        if result.climate_data:
            climate_data = {
                "usda_zone": {
                    "zone": result.climate_data.usda_zone.zone if result.climate_data.usda_zone else None,
                    "description": result.climate_data.usda_zone.description if result.climate_data.usda_zone else None,
                    "temperature_range": result.climate_data.usda_zone.temperature_range if result.climate_data.usda_zone else None
                },
                "koppen_analysis": {
                    "koppen_type": {
                        "code": result.climate_data.koppen_analysis.koppen_type.code,
                        "name": result.climate_data.koppen_analysis.koppen_type.name,
                        "description": result.climate_data.koppen_analysis.koppen_type.description
                    }
                } if result.climate_data.koppen_analysis and include_koppen else None,
                "confidence_factors": result.climate_data.confidence_factors,
                "detection_metadata": result.climate_data.detection_metadata
            }
        
        # Determine success status and message
        success = result.geocoding_confidence > 0.3
        message = None
        if not success:
            message = "Low confidence in address geocoding. Consider using coordinates-based detection."
        elif result.lookup_method == "fallback":
            message = "Used fallback method for address lookup. Results may be less accurate."
        
        response = AddressClimateResponse(
            address=result.address,
            geocoded_coordinates=result.geocoded_coordinates,
            climate_data=climate_data,
            geocoding_confidence=result.geocoding_confidence,
            address_components=result.address_components,
            lookup_method=result.lookup_method,
            success=success,
            message=message
        )
        
        logger.info(f"Successfully detected climate zone from address {address} using method {result.lookup_method}")
        return response
        
    except Exception as e:
        logger.error(f"Error getting zone from address: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Address-based detection failed: {str(e)}")


@router.get("/zone-characteristics/{zone}")
async def get_zone_characteristics(
    zone: str,
    zone_type: str = Query("usda_hardiness", description="Zone type")
):
    """
    Get detailed characteristics of a climate zone.
    """
    try:
        # This endpoint provides detailed zone characteristics
        # including agricultural implications, suitable crops, etc.
        
        if zone_type == "usda_hardiness":
            async with usda_zone_api as api:
                details = await api.get_zone_details(zone)
            
            if details:
                return {
                    "zone": zone,
                    "zone_type": "usda_hardiness",
                    "characteristics": details,
                    "agricultural_implications": {
                        "suitable_crops": details.get("suitable_plants", []),
                        "growing_season": details.get("growing_season", "unknown"),
                        "frost_dates": details.get("frost_dates", {}),
                        "management_considerations": [
                            "Monitor frost dates for planting timing",
                            "Select varieties appropriate for zone",
                            "Consider microclimate variations"
                        ]
                    }
                }
            else:
                raise HTTPException(status_code=404, detail=f"Zone {zone} not found")
        
        elif zone_type == "koppen":
            climate_type = koppen_climate_service.get_climate_type_by_code(zone)
            if not climate_type:
                raise HTTPException(status_code=404, detail=f"Köppen type {zone} not found")
            
            return {
                "zone": zone,
                "zone_type": "koppen",
                "characteristics": {
                    "name": climate_type.name,
                    "description": climate_type.description,
                    "temperature_pattern": climate_type.temperature_pattern,
                    "precipitation_pattern": climate_type.precipitation_pattern,
                    "typical_vegetation": climate_type.typical_vegetation,
                    "water_balance": climate_type.water_balance
                },
                "agricultural_implications": {
                    "suitability": climate_type.agricultural_suitability,
                    "growing_season_months": climate_type.growing_season_months,
                    "management_considerations": [
                        f"Adapted to {climate_type.temperature_pattern} temperatures",
                        f"Precipitation pattern: {climate_type.precipitation_pattern}",
                        f"Water balance: {climate_type.water_balance}"
                    ]
                }
            }
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported zone type: {zone_type}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting zone characteristics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get zone characteristics: {str(e)}")


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check for climate service."""
    return {
        "status": "healthy",
        "service": "climate-zone-detection",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }