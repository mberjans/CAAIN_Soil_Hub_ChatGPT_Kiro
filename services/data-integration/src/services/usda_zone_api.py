"""
USDA Plant Hardiness Zone API Integration
Provides integration with USDA zone data sources and APIs.
"""

import asyncio
import aiohttp
import logging
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class USDAZoneData:
    """USDA zone data structure."""
    zone: str
    temperature_range: Tuple[float, float]
    description: str
    coordinates: Tuple[float, float]
    confidence: float
    source: str


class USDAZoneAPI:
    """USDA Plant Hardiness Zone API client."""
    
    def __init__(self):
        self.base_url = "https://planthardiness.ars.usda.gov"
        self.api_key = os.getenv("USDA_API_KEY")  # Optional API key
        self.session = None
        self.cache = {}
        self.cache_ttl = timedelta(hours=24)
        self.rate_limit_delay = 1.0  # Seconds between requests
        self.last_request_time = None
        
        # Load local zone data as fallback
        self.local_zone_data = self._load_local_zone_data()
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                "User-Agent": "AFAS-Climate-Service/1.0",
                "Accept": "application/json"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def get_zone_by_coordinates(
        self, 
        latitude: float, 
        longitude: float
    ) -> Optional[USDAZoneData]:
        """
        Get USDA hardiness zone for given coordinates.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            
        Returns:
            USDAZoneData if found, None otherwise
        """
        try:
            # Check cache first
            cache_key = f"usda_{latitude:.4f}_{longitude:.4f}"
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if datetime.now() - timestamp < self.cache_ttl:
                    logger.debug(f"Returning cached USDA zone data for {cache_key}")
                    return cached_data
            
            # Rate limiting
            await self._rate_limit()
            
            # Try USDA API first
            zone_data = await self._fetch_from_usda_api(latitude, longitude)
            
            if not zone_data:
                # Fallback to local data
                zone_data = self._get_zone_from_local_data(latitude, longitude)
            
            if zone_data:
                # Cache the result
                self.cache[cache_key] = (zone_data, datetime.now())
                logger.info(f"Retrieved USDA zone {zone_data.zone} for coordinates {latitude}, {longitude}")
            
            return zone_data
            
        except Exception as e:
            logger.error(f"Error getting USDA zone for coordinates {latitude}, {longitude}: {str(e)}")
            # Return fallback data
            return self._get_fallback_zone(latitude, longitude)
    
    async def _fetch_from_usda_api(
        self, 
        latitude: float, 
        longitude: float
    ) -> Optional[USDAZoneData]:
        """Fetch zone data from USDA API."""
        
        if not self.session:
            logger.warning("No active session for USDA API")
            return None
        
        try:
            # USDA Plant Hardiness Zone API endpoint
            # Note: This is a simplified example - actual USDA API may have different endpoints
            url = f"{self.base_url}/api/zone"
            params = {
                "lat": latitude,
                "lon": longitude,
                "format": "json"
            }
            
            if self.api_key:
                params["api_key"] = self.api_key
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_usda_response(data, latitude, longitude)
                elif response.status == 429:
                    logger.warning("USDA API rate limit exceeded")
                    await asyncio.sleep(5)  # Wait before retry
                    return None
                else:
                    logger.warning(f"USDA API returned status {response.status}")
                    return None
                    
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error fetching USDA zone data: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching USDA zone data: {str(e)}")
            return None
    
    def _parse_usda_response(
        self, 
        data: Dict, 
        latitude: float, 
        longitude: float
    ) -> Optional[USDAZoneData]:
        """Parse USDA API response."""
        
        try:
            # Parse response based on expected USDA API format
            if "zone" in data:
                zone = data["zone"]
                temp_min = data.get("temp_min", 0)
                temp_max = data.get("temp_max", 10)
                description = data.get("description", f"USDA Zone {zone}")
                confidence = data.get("confidence", 0.9)
                
                return USDAZoneData(
                    zone=zone,
                    temperature_range=(temp_min, temp_max),
                    description=description,
                    coordinates=(latitude, longitude),
                    confidence=confidence,
                    source="usda_api"
                )
            
        except Exception as e:
            logger.error(f"Error parsing USDA API response: {str(e)}")
        
        return None
    
    def _load_local_zone_data(self) -> Dict:
        """Load local USDA zone data as fallback."""
        
        # This would typically load from a local database or file
        # For now, we'll use a simplified coordinate-based mapping
        
        return {
            # Simplified US zone mapping by state/region
            "alaska": {"zone": "1a", "temp_range": (-60, -50)},
            "northern_maine": {"zone": "3a", "temp_range": (-40, -30)},
            "minnesota": {"zone": "4a", "temp_range": (-30, -20)},
            "iowa": {"zone": "5a", "temp_range": (-20, -10)},
            "missouri": {"zone": "6a", "temp_range": (-10, 0)},
            "arkansas": {"zone": "7a", "temp_range": (0, 10)},
            "texas": {"zone": "8a", "temp_range": (10, 20)},
            "florida": {"zone": "9a", "temp_range": (20, 30)},
            "hawaii": {"zone": "11a", "temp_range": (40, 50)},
        }
    
    def _get_zone_from_local_data(
        self, 
        latitude: float, 
        longitude: float
    ) -> Optional[USDAZoneData]:
        """Get zone from local data based on coordinates."""
        
        try:
            # Simplified zone detection based on latitude
            # In production, this would use detailed shapefiles or lookup tables
            
            zone = self._estimate_zone_from_coordinates(latitude, longitude)
            temp_range = self._get_temperature_range_for_zone(zone)
            
            return USDAZoneData(
                zone=zone,
                temperature_range=temp_range,
                description=f"USDA Hardiness Zone {zone}",
                coordinates=(latitude, longitude),
                confidence=0.7,  # Lower confidence for estimated data
                source="local_estimation"
            )
            
        except Exception as e:
            logger.error(f"Error getting zone from local data: {str(e)}")
            return None
    
    def _estimate_zone_from_coordinates(self, latitude: float, longitude: float) -> str:
        """Estimate USDA zone from coordinates."""
        
        # Simplified zone estimation for North America
        # This is a rough approximation - production would use detailed data
        
        if latitude > 64:
            return "1a"
        elif latitude > 60:
            return "2a"
        elif latitude > 56:
            return "3a"
        elif latitude > 52:
            return "4a"
        elif latitude > 48:
            return "4b"
        elif latitude > 44:
            return "5a"
        elif latitude > 40:
            return "5b"
        elif latitude > 36:
            return "6a"
        elif latitude > 32:
            return "7a"
        elif latitude > 28:
            return "8a"
        elif latitude > 24:
            return "9a"
        elif latitude > 20:
            return "10a"
        else:
            return "11a"
    
    def _get_temperature_range_for_zone(self, zone: str) -> Tuple[float, float]:
        """Get temperature range for USDA zone."""
        
        zone_temps = {
            "1a": (-60, -55), "1b": (-55, -50),
            "2a": (-50, -45), "2b": (-45, -40),
            "3a": (-40, -35), "3b": (-35, -30),
            "4a": (-30, -25), "4b": (-25, -20),
            "5a": (-20, -15), "5b": (-15, -10),
            "6a": (-10, -5), "6b": (-5, 0),
            "7a": (0, 5), "7b": (5, 10),
            "8a": (10, 15), "8b": (15, 20),
            "9a": (20, 25), "9b": (25, 30),
            "10a": (30, 35), "10b": (35, 40),
            "11a": (40, 45), "11b": (45, 50),
            "12a": (50, 55), "12b": (55, 60),
            "13a": (60, 65), "13b": (65, 70),
        }
        
        return zone_temps.get(zone, (0, 10))
    
    def _get_fallback_zone(self, latitude: float, longitude: float) -> USDAZoneData:
        """Get fallback zone when all other methods fail."""
        
        # Default to zone 6a (moderate zone) as fallback
        return USDAZoneData(
            zone="6a",
            temperature_range=(-10, -5),
            description="USDA Hardiness Zone 6a (Fallback)",
            coordinates=(latitude, longitude),
            confidence=0.3,  # Low confidence for fallback
            source="fallback"
        )
    
    async def _rate_limit(self):
        """Implement rate limiting for API requests."""
        
        if self.last_request_time:
            elapsed = datetime.now() - self.last_request_time
            if elapsed.total_seconds() < self.rate_limit_delay:
                wait_time = self.rate_limit_delay - elapsed.total_seconds()
                await asyncio.sleep(wait_time)
        
        self.last_request_time = datetime.now()
    
    async def get_zone_details(self, zone: str) -> Optional[Dict]:
        """Get detailed information about a USDA zone."""
        
        try:
            temp_range = self._get_temperature_range_for_zone(zone)
            
            return {
                "zone": zone,
                "name": f"USDA Hardiness Zone {zone}",
                "temperature_range_f": temp_range,
                "temperature_range_c": (
                    round((temp_range[0] - 32) * 5/9, 1),
                    round((temp_range[1] - 32) * 5/9, 1)
                ),
                "description": self._get_zone_description(zone),
                "suitable_plants": self._get_suitable_plants(zone),
                "growing_season": self._estimate_growing_season(temp_range),
                "frost_dates": self._estimate_frost_dates(zone)
            }
            
        except Exception as e:
            logger.error(f"Error getting zone details for {zone}: {str(e)}")
            return None
    
    def _get_zone_description(self, zone: str) -> str:
        """Get description for USDA zone."""
        
        descriptions = {
            "1a": "Extremely cold zone with very short growing season",
            "1b": "Extremely cold zone with very short growing season",
            "2a": "Very cold zone suitable for hardy plants only",
            "2b": "Very cold zone suitable for hardy plants only",
            "3a": "Cold zone with moderate growing season",
            "3b": "Cold zone with moderate growing season",
            "4a": "Cool zone suitable for many temperate crops",
            "4b": "Cool zone suitable for many temperate crops",
            "5a": "Moderate zone ideal for diverse agriculture",
            "5b": "Moderate zone ideal for diverse agriculture",
            "6a": "Temperate zone with good growing conditions",
            "6b": "Temperate zone with good growing conditions",
            "7a": "Warm temperate zone with long growing season",
            "7b": "Warm temperate zone with long growing season",
            "8a": "Warm zone suitable for heat-loving crops",
            "8b": "Warm zone suitable for heat-loving crops",
            "9a": "Hot zone with year-round growing potential",
            "9b": "Hot zone with year-round growing potential",
            "10a": "Very hot zone suitable for tropical crops",
            "10b": "Very hot zone suitable for tropical crops",
            "11a": "Tropical zone with no frost",
            "11b": "Tropical zone with no frost",
        }
        
        return descriptions.get(zone, f"USDA Hardiness Zone {zone}")
    
    def _get_suitable_plants(self, zone: str) -> List[str]:
        """Get suitable plants for USDA zone."""
        
        plant_mapping = {
            "1a": ["arctic_willow", "labrador_tea"],
            "1b": ["arctic_willow", "labrador_tea", "dwarf_birch"],
            "2a": ["white_spruce", "paper_birch", "hardy_grasses"],
            "2b": ["white_spruce", "paper_birch", "hardy_grasses", "blueberries"],
            "3a": ["maple", "oak", "apple", "hardy_vegetables"],
            "3b": ["maple", "oak", "apple", "hardy_vegetables", "strawberries"],
            "4a": ["corn", "wheat", "soybeans", "deciduous_trees"],
            "4b": ["corn", "wheat", "soybeans", "deciduous_trees", "grapes"],
            "5a": ["corn", "soybeans", "tomatoes", "fruit_trees"],
            "5b": ["corn", "soybeans", "tomatoes", "fruit_trees", "peppers"],
            "6a": ["vegetables", "herbs", "fruit_trees", "ornamentals"],
            "6b": ["vegetables", "herbs", "fruit_trees", "ornamentals", "roses"],
            "7a": ["warm_season_vegetables", "citrus", "subtropical_plants"],
            "7b": ["warm_season_vegetables", "citrus", "subtropical_plants"],
            "8a": ["cotton", "rice", "citrus", "palms"],
            "8b": ["cotton", "rice", "citrus", "palms", "tropical_fruits"],
            "9a": ["tropical_crops", "year_round_vegetables", "tropical_trees"],
            "9b": ["tropical_crops", "year_round_vegetables", "tropical_trees"],
            "10a": ["tropical_plants", "exotic_fruits", "tropical_vegetables"],
            "10b": ["tropical_plants", "exotic_fruits", "tropical_vegetables"],
        }
        
        return plant_mapping.get(zone, ["diverse_plants"])
    
    def _estimate_growing_season(self, temp_range: Tuple[float, float]) -> int:
        """Estimate growing season length from temperature range."""
        
        avg_min_temp = temp_range[0]
        
        if avg_min_temp < -40:
            return 60
        elif avg_min_temp < -20:
            return 90
        elif avg_min_temp < 0:
            return 120
        elif avg_min_temp < 20:
            return 150
        else:
            return 200
    
    def _estimate_frost_dates(self, zone: str) -> Dict[str, str]:
        """Estimate frost dates for USDA zone."""
        
        # Simplified frost date estimation
        # In production, this would use detailed climate data
        
        frost_dates = {
            "1a": {"last_spring": "June 15", "first_fall": "August 15"},
            "1b": {"last_spring": "June 10", "first_fall": "August 20"},
            "2a": {"last_spring": "May 30", "first_fall": "September 1"},
            "2b": {"last_spring": "May 25", "first_fall": "September 5"},
            "3a": {"last_spring": "May 15", "first_fall": "September 15"},
            "3b": {"last_spring": "May 10", "first_fall": "September 20"},
            "4a": {"last_spring": "May 1", "first_fall": "October 1"},
            "4b": {"last_spring": "April 25", "first_fall": "October 5"},
            "5a": {"last_spring": "April 15", "first_fall": "October 15"},
            "5b": {"last_spring": "April 10", "first_fall": "October 20"},
            "6a": {"last_spring": "April 1", "first_fall": "October 30"},
            "6b": {"last_spring": "March 25", "first_fall": "November 5"},
            "7a": {"last_spring": "March 15", "first_fall": "November 15"},
            "7b": {"last_spring": "March 10", "first_fall": "November 20"},
            "8a": {"last_spring": "March 1", "first_fall": "November 30"},
            "8b": {"last_spring": "February 20", "first_fall": "December 10"},
            "9a": {"last_spring": "February 1", "first_fall": "December 15"},
            "9b": {"last_spring": "January 15", "first_fall": "December 20"},
            "10a": {"last_spring": "No frost", "first_fall": "No frost"},
            "10b": {"last_spring": "No frost", "first_fall": "No frost"},
        }
        
        return frost_dates.get(zone, {"last_spring": "April 15", "first_fall": "October 15"})


# Global API instance
usda_zone_api = USDAZoneAPI()