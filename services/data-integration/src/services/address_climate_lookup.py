"""
Address-based Climate Zone Lookup Service
Provides climate zone detection from addresses using geocoding.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
import asyncio
import aiohttp
import re

from .coordinate_climate_detector import coordinate_climate_detector, CoordinateClimateData

logger = logging.getLogger(__name__)


@dataclass
class AddressClimateResult:
    """Result of address-based climate detection."""
    address: str
    geocoded_coordinates: Optional[Tuple[float, float]]
    climate_data: Optional[CoordinateClimateData]
    geocoding_confidence: float
    address_components: Dict
    lookup_method: str


class AddressClimateService:
    """Service for address-based climate zone lookup."""
    
    def __init__(self):
        self.geocoding_cache = {}
        self.state_zone_mapping = self._initialize_state_zone_mapping()
        self.zip_zone_mapping = self._initialize_zip_zone_mapping()
        self.county_zone_mapping = self._initialize_county_zone_mapping()
    
    async def get_climate_from_address(
        self,
        address: str,
        country: str = "US"
    ) -> AddressClimateResult:
        """
        Get climate zone from address.
        
        Args:
            address: Street address, city, state, or ZIP code
            country: Country code (default: US)
            
        Returns:
            AddressClimateResult with climate data
        """
        try:
            logger.info(f"Looking up climate zone for address: {address}")
            
            # Parse address components
            address_components = self._parse_address(address)
            
            # Try different lookup methods in order of preference
            result = None
            
            # Method 1: Full geocoding (most accurate)
            if self._is_full_address(address):
                result = await self._geocode_and_detect(address, address_components)
                if result and result.geocoding_confidence > 0.7:
                    return result
            
            # Method 2: ZIP code lookup
            if address_components.get('zip_code'):
                result = await self._lookup_by_zip_code(
                    address_components['zip_code'], address, address_components
                )
                if result:
                    return result
            
            # Method 3: State/county lookup
            if address_components.get('state'):
                result = await self._lookup_by_state_county(
                    address_components, address
                )
                if result:
                    return result
            
            # Method 4: City/state lookup with geocoding
            if address_components.get('city') and address_components.get('state'):
                city_state = f"{address_components['city']}, {address_components['state']}"
                result = await self._geocode_and_detect(city_state, address_components)
                if result:
                    return result
            
            # Fallback: Return result with low confidence
            return self._get_fallback_result(address, address_components)
            
        except Exception as e:
            logger.error(f"Error looking up climate from address {address}: {str(e)}")
            return self._get_error_result(address)
    
    def _parse_address(self, address: str) -> Dict:
        """Parse address into components."""
        
        components = {
            'original': address,
            'street': None,
            'city': None,
            'state': None,
            'zip_code': None,
            'country': 'US'
        }
        
        # Extract ZIP code
        zip_match = re.search(r'\b(\d{5}(?:-\d{4})?)\b', address)
        if zip_match:
            components['zip_code'] = zip_match.group(1)[:5]  # Take first 5 digits
        
        # Extract state (2-letter abbreviation or full name)
        state_patterns = [
            r'\b([A-Z]{2})\b',  # Two-letter abbreviation
            r'\b(Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New Hampshire|New Jersey|New Mexico|New York|North Carolina|North Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode Island|South Carolina|South Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West Virginia|Wisconsin|Wyoming)\b'
        ]
        
        for pattern in state_patterns:
            state_match = re.search(pattern, address, re.IGNORECASE)
            if state_match:
                components['state'] = state_match.group(1).upper()
                break
        
        # Simple city extraction (word before state or ZIP)
        if components['state']:
            city_pattern = r'([A-Za-z\s]+),?\s+' + re.escape(components['state'])
            city_match = re.search(city_pattern, address, re.IGNORECASE)
            if city_match:
                components['city'] = city_match.group(1).strip().title()
        
        return components
    
    def _is_full_address(self, address: str) -> bool:
        """Check if address appears to be a full street address."""
        
        # Look for street indicators
        street_indicators = [
            r'\d+\s+\w+\s+(st|street|ave|avenue|rd|road|dr|drive|ln|lane|blvd|boulevard|ct|court|pl|place|way|circle|cir)',
            r'\d+\s+[A-Za-z\s]+\s+(st|street|ave|avenue|rd|road|dr|drive|ln|lane|blvd|boulevard|ct|court|pl|place|way|circle|cir)'
        ]
        
        for pattern in street_indicators:
            if re.search(pattern, address, re.IGNORECASE):
                return True
        
        return False
    
    async def _geocode_and_detect(
        self,
        address: str,
        address_components: Dict
    ) -> Optional[AddressClimateResult]:
        """Geocode address and detect climate zone."""
        
        try:
            # Check cache first
            cache_key = address.lower().strip()
            if cache_key in self.geocoding_cache:
                cached_result = self.geocoding_cache[cache_key]
                logger.debug(f"Using cached geocoding result for {address}")
                return cached_result
            
            # Geocode address (simplified - in production would use real geocoding API)
            coordinates = await self._geocode_address(address)
            
            if not coordinates:
                return None
            
            latitude, longitude = coordinates
            
            # Detect climate zone from coordinates
            climate_data = await coordinate_climate_detector.detect_climate_from_coordinates(
                latitude, longitude, include_detailed_analysis=True
            )
            
            result = AddressClimateResult(
                address=address,
                geocoded_coordinates=coordinates,
                climate_data=climate_data,
                geocoding_confidence=0.8,  # Would come from geocoding API
                address_components=address_components,
                lookup_method="geocoding"
            )
            
            # Cache result
            self.geocoding_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Error geocoding address {address}: {str(e)}")
            return None
    
    async def _geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Geocode address to coordinates.
        
        Note: This is a simplified implementation. In production,
        this would integrate with a real geocoding service like Google Maps,
        Mapbox, or OpenStreetMap Nominatim.
        """
        
        # Simplified geocoding based on known locations
        # In production, this would make API calls to geocoding services
        
        known_locations = {
            'ames, iowa': (42.0308, -93.6319),
            'ames, ia': (42.0308, -93.6319),
            'des moines, iowa': (41.5868, -93.6250),
            'des moines, ia': (41.5868, -93.6250),
            'chicago, illinois': (41.8781, -87.6298),
            'chicago, il': (41.8781, -87.6298),
            'new york, new york': (40.7128, -74.0060),
            'new york, ny': (40.7128, -74.0060),
            'los angeles, california': (34.0522, -118.2437),
            'los angeles, ca': (34.0522, -118.2437),
            'miami, florida': (25.7617, -80.1918),
            'miami, fl': (25.7617, -80.1918),
            'denver, colorado': (39.7392, -104.9903),
            'denver, co': (39.7392, -104.9903),
            'seattle, washington': (47.6062, -122.3321),
            'seattle, wa': (47.6062, -122.3321),
        }
        
        address_key = address.lower().strip()
        
        # Direct lookup
        if address_key in known_locations:
            return known_locations[address_key]
        
        # Partial matching
        for known_addr, coords in known_locations.items():
            if known_addr in address_key or address_key in known_addr:
                return coords
        
        # State center coordinates as fallback
        state_centers = {
            'iowa': (42.0, -93.5),
            'ia': (42.0, -93.5),
            'illinois': (40.0, -89.0),
            'il': (40.0, -89.0),
            'california': (36.7, -119.7),
            'ca': (36.7, -119.7),
            'florida': (27.8, -81.7),
            'fl': (27.8, -81.7),
            'texas': (31.0, -100.0),
            'tx': (31.0, -100.0),
            'new york': (42.2, -74.9),
            'ny': (42.2, -74.9),
        }
        
        for state, coords in state_centers.items():
            if state in address_key:
                return coords
        
        return None
    
    async def _lookup_by_zip_code(
        self,
        zip_code: str,
        original_address: str,
        address_components: Dict
    ) -> Optional[AddressClimateResult]:
        """Lookup climate zone by ZIP code."""
        
        try:
            # Get coordinates for ZIP code
            coordinates = self._get_zip_coordinates(zip_code)
            
            if not coordinates:
                return None
            
            latitude, longitude = coordinates
            
            # Detect climate zone
            climate_data = await coordinate_climate_detector.detect_climate_from_coordinates(
                latitude, longitude, include_detailed_analysis=True
            )
            
            return AddressClimateResult(
                address=original_address,
                geocoded_coordinates=coordinates,
                climate_data=climate_data,
                geocoding_confidence=0.7,  # Lower confidence for ZIP-based lookup
                address_components=address_components,
                lookup_method="zip_code"
            )
            
        except Exception as e:
            logger.error(f"Error looking up ZIP code {zip_code}: {str(e)}")
            return None
    
    def _get_zip_coordinates(self, zip_code: str) -> Optional[Tuple[float, float]]:
        """Get coordinates for ZIP code (simplified implementation)."""
        
        # Simplified ZIP code mapping
        # In production, this would use a comprehensive ZIP code database
        
        zip_coords = {
            '50010': (42.0308, -93.6319),  # Ames, IA
            '50309': (41.5868, -93.6250),  # Des Moines, IA
            '60601': (41.8781, -87.6298),  # Chicago, IL
            '10001': (40.7128, -74.0060),  # New York, NY
            '90210': (34.0522, -118.2437), # Los Angeles, CA
            '33101': (25.7617, -80.1918),  # Miami, FL
            '80202': (39.7392, -104.9903),  # Denver, CO
            '98101': (47.6062, -122.3321),  # Seattle, WA
        }
        
        return zip_coords.get(zip_code)
    
    async def _lookup_by_state_county(
        self,
        address_components: Dict,
        original_address: str
    ) -> Optional[AddressClimateResult]:
        """Lookup climate zone by state/county."""
        
        try:
            state = address_components.get('state')
            if not state:
                return None
            
            # Get representative coordinates for state
            coordinates = self._get_state_coordinates(state)
            
            if not coordinates:
                return None
            
            latitude, longitude = coordinates
            
            # Detect climate zone
            climate_data = await coordinate_climate_detector.detect_climate_from_coordinates(
                latitude, longitude, include_detailed_analysis=True
            )
            
            return AddressClimateResult(
                address=original_address,
                geocoded_coordinates=coordinates,
                climate_data=climate_data,
                geocoding_confidence=0.5,  # Lower confidence for state-based lookup
                address_components=address_components,
                lookup_method="state_based"
            )
            
        except Exception as e:
            logger.error(f"Error looking up by state/county: {str(e)}")
            return None
    
    def _get_state_coordinates(self, state: str) -> Optional[Tuple[float, float]]:
        """Get representative coordinates for state."""
        
        state_coords = {
            'IA': (42.0, -93.5), 'IOWA': (42.0, -93.5),
            'IL': (40.0, -89.0), 'ILLINOIS': (40.0, -89.0),
            'CA': (36.7, -119.7), 'CALIFORNIA': (36.7, -119.7),
            'FL': (27.8, -81.7), 'FLORIDA': (27.8, -81.7),
            'TX': (31.0, -100.0), 'TEXAS': (31.0, -100.0),
            'NY': (42.2, -74.9), 'NEW YORK': (42.2, -74.9),
            'CO': (39.0, -105.5), 'COLORADO': (39.0, -105.5),
            'WA': (47.4, -121.5), 'WASHINGTON': (47.4, -121.5),
            'OR': (44.0, -121.0), 'OREGON': (44.0, -121.0),
            'MN': (45.0, -93.0), 'MINNESOTA': (45.0, -93.0),
            'WI': (44.3, -89.8), 'WISCONSIN': (44.3, -89.8),
            'MI': (43.3, -84.5), 'MICHIGAN': (43.3, -84.5),
            'OH': (40.4, -82.7), 'OHIO': (40.4, -82.7),
            'IN': (39.8, -86.1), 'INDIANA': (39.8, -86.1),
            'KY': (37.7, -84.9), 'KENTUCKY': (37.7, -84.9),
            'TN': (35.7, -86.0), 'TENNESSEE': (35.7, -86.0),
            'NC': (35.6, -79.8), 'NORTH CAROLINA': (35.6, -79.8),
            'SC': (33.8, -80.9), 'SOUTH CAROLINA': (33.8, -80.9),
            'GA': (33.0, -83.6), 'GEORGIA': (33.0, -83.6),
            'AL': (32.8, -86.8), 'ALABAMA': (32.8, -86.8),
            'MS': (32.7, -89.6), 'MISSISSIPPI': (32.7, -89.6),
            'LA': (31.1, -91.8), 'LOUISIANA': (31.1, -91.8),
            'AR': (34.9, -92.4), 'ARKANSAS': (34.9, -92.4),
            'MO': (38.4, -92.2), 'MISSOURI': (38.4, -92.2),
            'KS': (38.5, -96.7), 'KANSAS': (38.5, -96.7),
            'NE': (41.1, -98.0), 'NEBRASKA': (41.1, -98.0),
            'SD': (44.3, -99.9), 'SOUTH DAKOTA': (44.3, -99.9),
            'ND': (47.5, -99.8), 'NORTH DAKOTA': (47.5, -99.8),
            'MT': (47.1, -110.0), 'MONTANA': (47.1, -110.0),
            'WY': (42.8, -107.3), 'WYOMING': (42.8, -107.3),
            'ID': (44.2, -114.5), 'IDAHO': (44.2, -114.5),
            'UT': (40.2, -111.5), 'UTAH': (40.2, -111.5),
            'AZ': (33.7, -111.4), 'ARIZONA': (33.7, -111.4),
            'NV': (38.3, -117.1), 'NEVADA': (38.3, -117.1),
            'NM': (34.8, -106.2), 'NEW MEXICO': (34.8, -106.2),
            'OK': (35.6, -96.9), 'OKLAHOMA': (35.6, -96.9),
        }
        
        return state_coords.get(state.upper())
    
    def _initialize_state_zone_mapping(self) -> Dict:
        """Initialize state to climate zone mapping."""
        
        return {
            'IA': {'primary_zone': '5a', 'range': ['4b', '5a', '5b']},
            'IL': {'primary_zone': '5b', 'range': ['5a', '5b', '6a']},
            'CA': {'primary_zone': '9a', 'range': ['6a', '7a', '8a', '9a', '10a']},
            'FL': {'primary_zone': '9b', 'range': ['8b', '9a', '9b', '10a', '10b']},
            'TX': {'primary_zone': '8a', 'range': ['7a', '8a', '8b', '9a']},
            'NY': {'primary_zone': '6a', 'range': ['4a', '5a', '6a', '6b']},
            'CO': {'primary_zone': '5a', 'range': ['3a', '4a', '5a', '6a']},
            'WA': {'primary_zone': '8a', 'range': ['6a', '7a', '8a', '9a']},
        }
    
    def _initialize_zip_zone_mapping(self) -> Dict:
        """Initialize ZIP code to zone mapping (simplified)."""
        
        return {
            '500': '5a',  # Iowa ZIP codes starting with 500
            '501': '5a',  # Iowa ZIP codes starting with 501
            '606': '5b',  # Chicago area
            '607': '5b',  # Chicago area
            '902': '9a',  # Los Angeles area
            '331': '9b',  # Miami area
            '802': '5a',  # Denver area
            '981': '8a',  # Seattle area
        }
    
    def _initialize_county_zone_mapping(self) -> Dict:
        """Initialize county to zone mapping (simplified)."""
        
        return {
            'story_ia': '5a',      # Story County, Iowa
            'polk_ia': '5a',       # Polk County, Iowa
            'cook_il': '5b',       # Cook County, Illinois
            'los_angeles_ca': '9a', # Los Angeles County, CA
            'miami_dade_fl': '9b',  # Miami-Dade County, FL
        }
    
    def _get_fallback_result(
        self,
        address: str,
        address_components: Dict
    ) -> AddressClimateResult:
        """Get fallback result when other methods fail."""
        
        # Try to infer from state if available
        state = address_components.get('state')
        if state and state.upper() in ['IA', 'IOWA']:
            fallback_coords = (42.0, -93.5)
        elif state and state.upper() in ['CA', 'CALIFORNIA']:
            fallback_coords = (36.7, -119.7)
        elif state and state.upper() in ['FL', 'FLORIDA']:
            fallback_coords = (27.8, -81.7)
        else:
            fallback_coords = (39.0, -98.0)  # Geographic center of US
        
        return AddressClimateResult(
            address=address,
            geocoded_coordinates=fallback_coords,
            climate_data=None,
            geocoding_confidence=0.3,  # Low confidence
            address_components=address_components,
            lookup_method="fallback"
        )
    
    def _get_error_result(self, address: str) -> AddressClimateResult:
        """Get error result when lookup fails."""
        
        return AddressClimateResult(
            address=address,
            geocoded_coordinates=None,
            climate_data=None,
            geocoding_confidence=0.0,
            address_components={'error': 'lookup_failed'},
            lookup_method="error"
        )


# Global service instance
address_climate_service = AddressClimateService()