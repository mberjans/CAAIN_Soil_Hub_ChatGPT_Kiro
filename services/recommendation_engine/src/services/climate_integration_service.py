"""
Climate Zone Integration Service

Helper service to integrate climate zone data into agricultural recommendations.
"""

import logging
import asyncio
import aiohttp
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class ClimateIntegrationService:
    """
    Service to fetch and integrate climate zone data into recommendation workflows.
    
    This service acts as a bridge between the recommendation engine and the 
    climate zone detection service.
    """
    
    def __init__(self, climate_api_base_url: str = "http://localhost:8001"):
        """
        Initialize climate integration service.
        
        Args:
            climate_api_base_url: Base URL for the data-integration service climate API
        """
        self.climate_api_base_url = climate_api_base_url.rstrip('/')
        self._session = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self._session
    
    async def detect_climate_zone(
        self, 
        latitude: float, 
        longitude: float, 
        elevation_ft: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Detect climate zone from coordinates using the climate zone service.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees  
            elevation_ft: Elevation in feet (optional)
            
        Returns:
            Climate zone detection result or None if detection fails
        """
        try:
            session = await self._get_session()
            
            # Prepare request payload
            payload = {
                "latitude": latitude,
                "longitude": longitude
            }
            if elevation_ft is not None:
                payload["elevation_ft"] = elevation_ft
            
            # Call climate zone detection API
            url = f"{self.climate_api_base_url}/api/v1/climate/detect-zone"
            
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Successfully detected climate zone: {result['primary_zone']['zone_id']}")
                    return result
                else:
                    error_text = await response.text()
                    logger.warning(f"Climate zone detection failed: {response.status} - {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error detecting climate zone: {str(e)}")
            return None
    
    def enhance_location_with_climate(
        self, 
        location_data: Dict[str, Any], 
        climate_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhance location data with climate zone information.
        
        Args:
            location_data: Original location data
            climate_result: Climate zone detection result
            
        Returns:
            Enhanced location data with climate zone information
        """
        enhanced_location = location_data.copy()
        
        if climate_result and 'primary_zone' in climate_result:
            primary_zone = climate_result['primary_zone']
            
            # Add primary climate zone info
            enhanced_location.update({
                'climate_zone': primary_zone.get('zone_id'),
                'climate_zone_name': primary_zone.get('name'),
                'climate_zone_description': primary_zone.get('description'),
                'temperature_range_f': primary_zone.get('temperature_range_f'),
                'climate_confidence': climate_result.get('confidence_score', 0.7)
            })
            
            # Add Köppen climate info if available
            alternative_zones = climate_result.get('alternative_zones', [])
            koppen_zone = next((zone for zone in alternative_zones if zone.get('zone_type') == 'koppen'), None)
            if koppen_zone:
                enhanced_location.update({
                    'koppen_zone': koppen_zone.get('zone_id'),
                    'koppen_description': koppen_zone.get('description'),
                    'agricultural_suitability': koppen_zone.get('agricultural_suitability'),
                    'growing_season_months': koppen_zone.get('growing_season_months')
                })
        
        return enhanced_location
    
    def get_climate_adjusted_crop_recommendations(
        self, 
        base_recommendations: list, 
        climate_data: Dict[str, Any]
    ) -> list:
        """
        Adjust crop recommendations based on climate zone.
        
        Args:
            base_recommendations: Original crop recommendations
            climate_data: Climate zone information
            
        Returns:
            Climate-adjusted recommendations
        """
        if not climate_data or 'primary_zone' not in climate_data:
            return base_recommendations
        
        primary_zone = climate_data['primary_zone']
        usda_zone = primary_zone.get('zone_id', '')
        
        # Adjust recommendations based on USDA zone
        adjusted_recommendations = []
        
        for rec in base_recommendations:
            adjusted_rec = rec.copy()
            
            # Add climate-specific context to descriptions
            if 'description' in adjusted_rec:
                climate_note = self._get_climate_note_for_crop(rec.get('title', ''), usda_zone)
                if climate_note:
                    adjusted_rec['description'] += f"\n\nClimate Consideration: {climate_note}"
            
            # Adjust confidence based on climate suitability
            if 'confidence_score' in adjusted_rec:
                climate_factor = self._get_climate_suitability_factor(rec.get('title', ''), usda_zone)
                adjusted_rec['confidence_score'] = min(1.0, adjusted_rec['confidence_score'] * climate_factor)
            
            # Add climate zone to agricultural sources
            if 'agricultural_sources' in adjusted_rec:
                adjusted_rec['agricultural_sources'].append(f"USDA Hardiness Zone {usda_zone} Analysis")
            
            adjusted_recommendations.append(adjusted_rec)
        
        return adjusted_recommendations
    
    def get_climate_adjusted_fertilizer_recommendations(
        self, 
        base_recommendations: list, 
        climate_data: Dict[str, Any]
    ) -> list:
        """
        Adjust fertilizer recommendations based on climate zone.
        
        Args:
            base_recommendations: Original fertilizer recommendations
            climate_data: Climate zone information
            
        Returns:
            Climate-adjusted recommendations
        """
        if not climate_data or 'primary_zone' not in climate_data:
            return base_recommendations
        
        primary_zone = climate_data['primary_zone']
        usda_zone = primary_zone.get('zone_id', '')
        temp_range = primary_zone.get('temperature_range_f')
        
        adjusted_recommendations = []
        
        for rec in base_recommendations:
            adjusted_rec = rec.copy()
            
            # Add climate-specific timing adjustments
            if 'timing' in adjusted_rec and temp_range:
                climate_timing = self._get_climate_adjusted_timing(adjusted_rec['timing'], usda_zone)
                adjusted_rec['timing'] = climate_timing
            
            # Add climate-specific implementation steps
            if 'implementation_steps' in adjusted_rec:
                climate_steps = self._get_climate_specific_steps(usda_zone)
                adjusted_rec['implementation_steps'].extend(climate_steps)
            
            # Add climate zone to agricultural sources
            if 'agricultural_sources' in adjusted_rec:
                adjusted_rec['agricultural_sources'].append(f"Climate Zone {usda_zone} Fertilizer Guidelines")
            
            adjusted_recommendations.append(adjusted_rec)
        
        return adjusted_recommendations
    
    def _get_climate_note_for_crop(self, crop_name: str, usda_zone: str) -> str:
        """Get climate-specific note for crop recommendation."""
        zone_num = int(usda_zone[0]) if usda_zone and usda_zone[0].isdigit() else 6
        
        crop_lower = crop_name.lower()
        
        if 'corn' in crop_lower or 'maize' in crop_lower:
            if zone_num < 4:
                return "Short-season varieties recommended for northern climate"
            elif zone_num > 8:
                return "Heat-tolerant varieties preferred for warm climate"
        elif 'tomato' in crop_lower:
            if zone_num < 5:
                return "Consider greenhouse production or cold-hardy varieties"
            elif zone_num > 9:
                return "Provide shade protection during hottest months"
        elif 'wheat' in crop_lower:
            if zone_num < 5:
                return "Winter wheat varieties suitable for cold hardiness"
            elif zone_num > 7:
                return "Spring wheat varieties may perform better"
        
        return f"Well-suited for USDA Zone {usda_zone}"
    
    def _get_climate_suitability_factor(self, crop_name: str, usda_zone: str) -> float:
        """Get climate suitability adjustment factor for crop confidence."""
        zone_num = int(usda_zone[0]) if usda_zone and usda_zone[0].isdigit() else 6
        
        crop_lower = crop_name.lower()
        
        # Define optimal zones for common crops
        optimal_zones = {
            'corn': (4, 8),
            'soybean': (4, 8), 
            'wheat': (3, 7),
            'cotton': (8, 10),
            'rice': (8, 11),
            'tomato': (6, 9),
            'potato': (3, 7),
            'apple': (3, 7),
            'citrus': (9, 11)
        }
        
        for crop, (min_zone, max_zone) in optimal_zones.items():
            if crop in crop_lower:
                if min_zone <= zone_num <= max_zone:
                    return 1.0  # Optimal
                elif min_zone - 1 <= zone_num <= max_zone + 1:
                    return 0.9  # Good
                else:
                    return 0.7  # Challenging but possible
        
        return 0.95  # Default for unknown crops
    
    def _get_climate_adjusted_timing(self, base_timing: str, usda_zone: str) -> str:
        """Adjust timing based on climate zone."""
        zone_num = int(usda_zone[0]) if usda_zone and usda_zone[0].isdigit() else 6
        
        if zone_num < 5:
            return f"{base_timing} (Adjust for shorter growing season in Zone {usda_zone})"
        elif zone_num > 8:
            return f"{base_timing} (Consider heat stress periods in Zone {usda_zone})"
        else:
            return f"{base_timing} (Zone {usda_zone} timing)"
    
    def _get_climate_specific_steps(self, usda_zone: str) -> list:
        """Get climate-specific implementation steps."""
        zone_num = int(usda_zone[0]) if usda_zone and usda_zone[0].isdigit() else 6
        
        steps = [f"Consider USDA Zone {usda_zone} temperature patterns"]
        
        if zone_num < 5:
            steps.append("Monitor soil temperature before application")
            steps.append("Consider frost protection measures")
        elif zone_num > 8:
            steps.append("Apply during cooler parts of the day")
            steps.append("Ensure adequate irrigation after application")
        
        return steps
    
    async def close(self):
        """Close HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()


# Global service instance
climate_integration_service = ClimateIntegrationService()