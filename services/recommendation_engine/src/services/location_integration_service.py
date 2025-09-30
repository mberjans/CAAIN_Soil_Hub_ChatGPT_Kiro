"""
Location Integration Service for Recommendation Engine
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

Deep integration between location services and recommendation systems with:
- Automatic location detection for recommendations
- Location-based filtering and regional adaptation
- Real-time location updates and change notifications
- Seamless location data sharing between services
"""

import logging
import asyncio
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import aiohttp
import json
from uuid import uuid4

# Initialize logger
logger = logging.getLogger(__name__)

# Import existing models
from ..models.agricultural_models import LocationData, RecommendationRequest
from ..services.climate_integration_service import ClimateIntegrationService

# Import location validation services
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../../../'))
location_validation_path = os.path.join(project_root, 'services', 'location-validation', 'src')

if location_validation_path not in sys.path:
    sys.path.insert(0, location_validation_path)

try:
    from services.location_validation_service import LocationValidationService
    from services.current_location_detection_service import CurrentLocationDetectionService
    from services.geocoding_service import GeocodingService
    LOCATION_SERVICES_AVAILABLE = True
    logger.info("Location validation services successfully imported")
except ImportError as e:
    logger.warning(f"Location validation services not available: {e}")
    LOCATION_SERVICES_AVAILABLE = False


@dataclass
class LocationIntegrationResult:
    """Result of location integration process."""
    success: bool
    enhanced_location: Optional[LocationData]
    validation_result: Optional[Dict[str, Any]]
    agricultural_suitability: Optional[str]
    regional_adaptations: List[str]
    warnings: List[str]
    errors: List[str]
    processing_time_ms: float


@dataclass
class LocationChangeNotification:
    """Notification for location changes affecting recommendations."""
    notification_id: str
    user_id: str
    old_location: LocationData
    new_location: LocationData
    affected_recommendations: List[str]
    impact_assessment: Dict[str, Any]
    timestamp: datetime


class LocationIntegrationService:
    """
    Deep integration service between location services and recommendation systems.
    
    Features:
    - Automatic location detection and validation for recommendations
    - Location-based filtering and regional adaptation
    - Real-time location updates and change notifications
    - Seamless location data sharing between services
    - Agricultural suitability assessment
    - Regional best practices integration
    """
    
    def __init__(self):
        """Initialize the location integration service."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize climate integration service
        self.climate_service = ClimateIntegrationService()
        
        # Initialize location services if available
        if LOCATION_SERVICES_AVAILABLE:
            self.location_validation = LocationValidationService()
            self.current_location_detection = CurrentLocationDetectionService()
            self.geocoding_service = GeocodingService()
        else:
            self.location_validation = None
            self.current_location_detection = None
            self.geocoding_service = None
        
        # Location integration configuration
        self.config = {
            'auto_validate_locations': True,
            'auto_detect_climate_zones': True,
            'enable_regional_adaptations': True,
            'location_cache_ttl_seconds': 3600,  # 1 hour
            'validation_timeout_seconds': 10,
            'geocoding_timeout_seconds': 15,
            'enable_location_notifications': True,
            'regional_adaptation_radius_km': 50
        }
        
        # Location cache for performance
        self.location_cache: Dict[str, LocationIntegrationResult] = {}
        
        # Regional adaptation data
        self.regional_adaptations = self._load_regional_adaptations()
        
        # Location change notifications
        self.location_notifications: List[LocationChangeNotification] = []
    
    async def integrate_location_with_recommendation(
        self,
        request: RecommendationRequest,
        auto_detect_location: bool = False,
        validate_location: bool = True
    ) -> LocationIntegrationResult:
        """
        Integrate location services with recommendation request.
        
        Args:
            request: Recommendation request to enhance with location data
            auto_detect_location: Whether to auto-detect location if not provided
            validate_location: Whether to validate the location data
            
        Returns:
            LocationIntegrationResult with enhanced location data and validation
        """
        start_time = datetime.now()
        
        try:
            # Step 1: Ensure location data is available
            location_data = await self._ensure_location_data(request, auto_detect_location)
            
            if not location_data:
                return LocationIntegrationResult(
                    success=False,
                    enhanced_location=None,
                    validation_result=None,
                    agricultural_suitability=None,
                    regional_adaptations=[],
                    warnings=["No location data available"],
                    errors=["Location data required for recommendations"],
                    processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000
                )
            
            # Step 2: Validate location if requested
            validation_result = None
            if validate_location and self.location_validation:
                validation_result = await self._validate_location(location_data)
            
            # Step 3: Enhance location with climate and agricultural data
            enhanced_location = await self._enhance_location_data(location_data)
            
            # Step 4: Determine agricultural suitability
            agricultural_suitability = await self._assess_agricultural_suitability(enhanced_location)
            
            # Step 5: Get regional adaptations
            regional_adaptations = await self._get_regional_adaptations(enhanced_location)
            
            # Step 6: Update request with enhanced location
            if enhanced_location:
                request.location = enhanced_location
            
            # Step 7: Cache result for performance
            cache_key = self._generate_location_cache_key(enhanced_location)
            result = LocationIntegrationResult(
                success=True,
                enhanced_location=enhanced_location,
                validation_result=validation_result,
                agricultural_suitability=agricultural_suitability,
                regional_adaptations=regional_adaptations,
                warnings=[],
                errors=[],
                processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000
            )
            
            self.location_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error integrating location with recommendation: {e}")
            return LocationIntegrationResult(
                success=False,
                enhanced_location=None,
                validation_result=None,
                agricultural_suitability=None,
                regional_adaptations=[],
                warnings=[],
                errors=[f"Location integration failed: {str(e)}"],
                processing_time_ms=(datetime.now() - start_time).total_seconds() * 1000
            )
    
    async def _ensure_location_data(
        self,
        request: RecommendationRequest,
        auto_detect: bool
    ) -> Optional[LocationData]:
        """Ensure location data is available, auto-detect if needed."""
        
        # If location already exists, return it
        if request.location:
            return request.location
        
        # Auto-detect location if requested and service available
        if auto_detect and self.current_location_detection:
            try:
                detected_location = await self.current_location_detection.detect_current_location()
                if detected_location and detected_location.success:
                    return LocationData(
                        latitude=detected_location.location.latitude,
                        longitude=detected_location.location.longitude,
                        elevation_ft=getattr(detected_location.location, 'elevation_ft', None),
                        address=getattr(detected_location.location, 'address', None),
                        state=getattr(detected_location.location, 'state', None),
                        county=getattr(detected_location.location, 'county', None)
                    )
            except Exception as e:
                self.logger.warning(f"Auto-location detection failed: {e}")
        
        return None
    
    async def _validate_location(self, location_data: LocationData) -> Optional[Dict[str, Any]]:
        """Validate location data using location validation service."""
        if not self.location_validation:
            return None
        
        try:
            validation_result = await self.location_validation.validate_coordinates(
                location_data.latitude,
                location_data.longitude
            )
            
            return {
                'valid': validation_result.valid,
                'warnings': validation_result.warnings,
                'errors': validation_result.errors,
                'geographic_info': validation_result.geographic_info.dict() if validation_result.geographic_info else None,
                'agricultural_suitability_score': getattr(validation_result, 'agricultural_suitability_score', None)
            }
        except Exception as e:
            self.logger.warning(f"Location validation failed: {e}")
            return None
    
    async def _enhance_location_data(self, location_data: LocationData) -> LocationData:
        """Enhance location data with climate and agricultural information."""
        
        # Start with existing location data
        enhanced_data = location_data.dict()
        
        # Add climate zone information
        try:
            climate_data = await self.climate_service.detect_climate_zone(
                latitude=location_data.latitude,
                longitude=location_data.longitude,
                elevation_ft=location_data.elevation_ft
            )
            
            if climate_data:
                enhanced_data.update({
                    'climate_zone': climate_data.get('zone_id'),
                    'climate_zone_name': climate_data.get('zone_name'),
                    'climate_zone_description': climate_data.get('description'),
                    'temperature_range_f': climate_data.get('temperature_range_f'),
                    'climate_confidence': climate_data.get('confidence'),
                    'koppen_zone': climate_data.get('koppen_class'),
                    'koppen_description': climate_data.get('koppen_description')
                })
        except Exception as e:
            self.logger.warning(f"Climate zone detection failed: {e}")
        
        # Add geocoding information if not present
        if not location_data.address and self.geocoding_service:
            try:
                geocoding_result = await self.geocoding_service.reverse_geocode(
                    location_data.latitude,
                    location_data.longitude
                )
                
                if geocoding_result and geocoding_result.success:
                    enhanced_data.update({
                        'address': geocoding_result.address,
                        'state': geocoding_result.state,
                        'county': geocoding_result.county
                    })
            except Exception as e:
                self.logger.warning(f"Geocoding failed: {e}")
        
        # Add agricultural suitability assessment
        enhanced_data['agricultural_suitability'] = await self._assess_agricultural_suitability(
            LocationData(**enhanced_data)
        )
        
        return LocationData(**enhanced_data)
    
    async def _assess_agricultural_suitability(self, location_data: LocationData) -> str:
        """Assess agricultural suitability of the location."""
        
        # Basic assessment based on coordinates
        lat = location_data.latitude
        lng = location_data.longitude
        
        # Check for extreme latitudes
        if abs(lat) > 70:
            return "limited"  # Polar regions
        elif abs(lat) > 60:
            return "challenging"  # High latitude
        elif abs(lat) < 10:
            return "tropical"  # Tropical regions
        
        # Check for continental US agricultural regions
        if 25 <= lat <= 49 and -125 <= lng <= -66:  # Continental US
            if 40 <= lat <= 49 and -104 <= lng <= -80:  # Midwest
                return "excellent"
            elif 32 <= lat <= 40 and -104 <= lng <= -75:  # Southeast
                return "very_good"
            elif 25 <= lat <= 40 and -125 <= lng <= -104:  # Southwest
                return "good"
            elif 40 <= lat <= 49 and -125 <= lng <= -104:  # Northwest
                return "good"
            else:  # Northeast
                return "good"
        
        # Default assessment
        return "moderate"
    
    async def _get_regional_adaptations(self, location_data: LocationData) -> List[str]:
        """Get regional adaptations for the location."""
        adaptations = []
        
        # Climate-based adaptations
        if location_data.climate_zone:
            zone_num = int(location_data.climate_zone[0]) if location_data.climate_zone[0].isdigit() else 5
            
            if zone_num <= 3:
                adaptations.extend([
                    "Consider cold-hardy crop varieties",
                    "Plan for shorter growing seasons",
                    "Use season extension techniques"
                ])
            elif zone_num >= 8:
                adaptations.extend([
                    "Consider heat-tolerant varieties",
                    "Plan for extended growing seasons",
                    "Implement heat stress management"
                ])
        
        # Regional adaptations based on location
        lat = location_data.latitude
        lng = location_data.longitude
        
        if 40 <= lat <= 49 and -104 <= lng <= -80:  # Midwest
            adaptations.extend([
                "Optimize for corn-soybean rotations",
                "Consider cover crops for soil health",
                "Plan for variable weather patterns"
            ])
        elif 32 <= lat <= 40 and -104 <= lng <= -75:  # Southeast
            adaptations.extend([
                "Consider warm-season crops",
                "Plan for high humidity management",
                "Implement disease-resistant varieties"
            ])
        
        return adaptations
    
    def _generate_location_cache_key(self, location_data: LocationData) -> str:
        """Generate cache key for location data."""
        return f"loc_{location_data.latitude:.4f}_{location_data.longitude:.4f}"
    
    def _load_regional_adaptations(self) -> Dict[str, List[str]]:
        """Load regional adaptation data."""
        return {
            "midwest": [
                "Optimize for corn-soybean rotations",
                "Consider cover crops for soil health",
                "Plan for variable weather patterns"
            ],
            "southeast": [
                "Consider warm-season crops",
                "Plan for high humidity management",
                "Implement disease-resistant varieties"
            ],
            "southwest": [
                "Plan for water conservation",
                "Consider drought-tolerant varieties",
                "Implement efficient irrigation"
            ],
            "northwest": [
                "Plan for cool-season crops",
                "Consider moisture management",
                "Implement soil warming techniques"
            ],
            "northeast": [
                "Plan for shorter growing seasons",
                "Consider season extension",
                "Implement frost protection"
            ]
        }
    
    async def notify_location_change(
        self,
        user_id: str,
        old_location: LocationData,
        new_location: LocationData,
        affected_recommendations: List[str]
    ) -> LocationChangeNotification:
        """Create notification for location changes affecting recommendations."""
        
        notification = LocationChangeNotification(
            notification_id=str(uuid4()),
            user_id=user_id,
            old_location=old_location,
            new_location=new_location,
            affected_recommendations=affected_recommendations,
            impact_assessment=await self._assess_location_change_impact(old_location, new_location),
            timestamp=datetime.now()
        )
        
        self.location_notifications.append(notification)
        
        # Keep only recent notifications (last 100)
        if len(self.location_notifications) > 100:
            self.location_notifications = self.location_notifications[-100:]
        
        return notification
    
    async def _assess_location_change_impact(
        self,
        old_location: LocationData,
        new_location: LocationData
    ) -> Dict[str, Any]:
        """Assess the impact of location change on recommendations."""
        
        impact = {
            "climate_zone_changed": False,
            "agricultural_suitability_changed": False,
            "regional_adaptations_changed": False,
            "impact_severity": "low"
        }
        
        # Check if climate zone changed
        if (old_location.climate_zone != new_location.climate_zone):
            impact["climate_zone_changed"] = True
            impact["impact_severity"] = "high"
        
        # Check if agricultural suitability changed
        if (old_location.agricultural_suitability != new_location.agricultural_suitability):
            impact["agricultural_suitability_changed"] = True
            if impact["impact_severity"] == "low":
                impact["impact_severity"] = "medium"
        
        # Check distance between locations
        distance_km = self._calculate_distance(
            old_location.latitude, old_location.longitude,
            new_location.latitude, new_location.longitude
        )
        
        impact["distance_km"] = distance_km
        
        if distance_km > 100:  # Significant distance change
            impact["regional_adaptations_changed"] = True
            if impact["impact_severity"] == "low":
                impact["impact_severity"] = "medium"
        
        return impact
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in kilometers."""
        import math
        
        # Haversine formula
        R = 6371  # Earth's radius in kilometers
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat/2) * math.sin(dlat/2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon/2) * math.sin(dlon/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return distance
    
    async def get_location_based_recommendations(
        self,
        location_data: LocationData,
        recommendation_type: str
    ) -> Dict[str, Any]:
        """Get location-specific recommendations and adaptations."""
        
        # Get regional adaptations
        regional_adaptations = await self._get_regional_adaptations(location_data)
        
        # Get agricultural suitability
        agricultural_suitability = await self._assess_agricultural_suitability(location_data)
        
        # Get location-specific recommendations
        recommendations = {
            "location_specific": {
                "agricultural_suitability": agricultural_suitability,
                "climate_zone": location_data.climate_zone,
                "regional_adaptations": regional_adaptations
            },
            "recommendations": {
                "crop_selection": self._get_location_crop_recommendations(location_data),
                "timing": self._get_location_timing_recommendations(location_data),
                "practices": self._get_location_practice_recommendations(location_data)
            }
        }
        
        return recommendations
    
    def _get_location_crop_recommendations(self, location_data: LocationData) -> List[str]:
        """Get location-specific crop recommendations."""
        recommendations = []
        
        if location_data.climate_zone:
            zone_num = int(location_data.climate_zone[0]) if location_data.climate_zone[0].isdigit() else 5
            
            if zone_num <= 4:
                recommendations.extend([
                    "Consider cold-hardy crops like winter wheat, barley, and rye",
                    "Plan for short-season varieties of corn and soybeans"
                ])
            elif zone_num >= 7:
                recommendations.extend([
                    "Consider warm-season crops like cotton, peanuts, and sweet potatoes",
                    "Plan for extended growing seasons with multiple crops"
                ])
        
        return recommendations
    
    def _get_location_timing_recommendations(self, location_data: LocationData) -> List[str]:
        """Get location-specific timing recommendations."""
        recommendations = []
        
        lat = location_data.latitude
        
        if lat > 45:  # Northern regions
            recommendations.extend([
                "Plan for later planting dates",
                "Consider early-maturing varieties",
                "Implement season extension techniques"
            ])
        elif lat < 30:  # Southern regions
            recommendations.extend([
                "Plan for earlier planting dates",
                "Consider multiple cropping seasons",
                "Implement heat stress management"
            ])
        
        return recommendations
    
    def _get_location_practice_recommendations(self, location_data: LocationData) -> List[str]:
        """Get location-specific practice recommendations."""
        recommendations = []
        
        # Regional practice recommendations
        lat = location_data.latitude
        lng = location_data.longitude
        
        if 40 <= lat <= 49 and -104 <= lng <= -80:  # Midwest
            recommendations.extend([
                "Implement conservation tillage practices",
                "Consider cover crops for soil health",
                "Plan for variable rate applications"
            ])
        elif 32 <= lat <= 40 and -104 <= lng <= -75:  # Southeast
            recommendations.extend([
                "Implement disease management strategies",
                "Consider irrigation for drought periods",
                "Plan for high humidity crop management"
            ])
        
        return recommendations


# Global instance for use by recommendation engine
location_integration_service = LocationIntegrationService()