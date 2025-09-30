"""
Address Validation and Standardization Service
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

Comprehensive address validation and standardization service with USPS integration,
agricultural area verification, and postal database validation.
"""

import asyncio
import logging
import re
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import aiohttp
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class AddressValidationSeverity(str, Enum):
    """Severity levels for address validation issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AddressValidationIssue:
    """Represents an address validation issue."""
    severity: AddressValidationSeverity
    message: str
    field: Optional[str] = None
    agricultural_context: Optional[str] = None
    suggested_actions: List[str] = None


class AddressComponents(BaseModel):
    """Standardized address components."""
    
    street_number: Optional[str] = Field(None, description="Street number")
    street_name: Optional[str] = Field(None, description="Street name")
    street_type: Optional[str] = Field(None, description="Street type (St, Ave, Rd, etc.)")
    street_direction: Optional[str] = Field(None, description="Street direction (N, S, E, W)")
    unit_number: Optional[str] = Field(None, description="Apartment, suite, or unit number")
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State abbreviation")
    postal_code: Optional[str] = Field(None, description="ZIP code or postal code")
    country: str = Field(default="US", description="Country code")
    
    # Rural address components
    rural_route: Optional[str] = Field(None, description="Rural route number")
    box_number: Optional[str] = Field(None, description="PO Box number")
    highway_contract: Optional[str] = Field(None, description="Highway contract route")
    
    # Agricultural context
    county: Optional[str] = Field(None, description="County name")
    agricultural_district: Optional[str] = Field(None, description="Agricultural district")
    farm_service_agency: Optional[str] = Field(None, description="FSA office information")


class AddressValidationResult(BaseModel):
    """Result of address validation and standardization."""
    
    valid: bool = Field(..., description="Whether the address is valid")
    standardized_address: Optional[str] = Field(None, description="Standardized address string")
    components: Optional[AddressComponents] = Field(None, description="Parsed address components")
    confidence_score: float = Field(0.0, ge=0.0, le=1.0, description="Validation confidence score")
    
    # Validation details
    issues: List[AddressValidationIssue] = Field(default_factory=list, description="Validation issues found")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    
    # Agricultural context
    agricultural_area_verified: bool = Field(False, description="Whether location is verified agricultural area")
    agricultural_context: Optional[Dict[str, Any]] = Field(None, description="Agricultural context data")
    
    # Data sources
    validation_sources: List[str] = Field(default_factory=list, description="Sources used for validation")
    last_validated: datetime = Field(default_factory=datetime.utcnow, description="Last validation timestamp")


class USPSProvider:
    """USPS Address Validation API provider."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://secure.shippingapis.com/ShippingAPI.dll"
        self.session = None
    
    async def get_session(self):
        """Get aiohttp session."""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def validate_address(self, address_components: AddressComponents) -> Dict[str, Any]:
        """
        Validate address using USPS API.
        
        Args:
            address_components: AddressComponents to validate
            
        Returns:
            Dict with validation results
        """
        if not self.api_key:
            logger.warning("USPS API key not provided, skipping USPS validation")
            return {"valid": False, "error": "USPS API key not configured"}
        
        try:
            session = await self.get_session()
            
            # Build USPS API request
            request_data = {
                "API": "Verify",
                "XML": self._build_usps_xml(address_components)
            }
            
            async with session.get(self.base_url, params=request_data, timeout=10) as response:
                if response.status == 200:
                    response_text = await response.text()
                    return self._parse_usps_response(response_text)
                else:
                    logger.warning(f"USPS API returned status {response.status}")
                    return {"valid": False, "error": f"USPS API error: {response.status}"}
        
        except Exception as e:
            logger.error(f"USPS validation error: {e}")
            return {"valid": False, "error": f"USPS validation failed: {str(e)}"}
    
    def _build_usps_xml(self, components: AddressComponents) -> str:
        """Build USPS API XML request."""
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<AddressValidateRequest USERID="{self.api_key}">
    <Address>
        <Address1>{components.street_number or ''} {components.street_name or ''} {components.street_type or ''}</Address1>
        <Address2>{components.unit_number or ''}</Address2>
        <City>{components.city or ''}</City>
        <State>{components.state or ''}</State>
        <Zip5>{components.postal_code[:5] if components.postal_code else ''}</Zip5>
        <Zip4>{components.postal_code[5:] if components.postal_code and len(components.postal_code) > 5 else ''}</Zip4>
    </Address>
</AddressValidateRequest>"""
        return xml
    
    def _parse_usps_response(self, response_text: str) -> Dict[str, Any]:
        """Parse USPS API response."""
        # Simplified parsing - in production would use proper XML parsing
        if "Address1" in response_text and "Error" not in response_text:
            return {
                "valid": True,
                "standardized": True,
                "source": "USPS"
            }
        else:
            return {
                "valid": False,
                "error": "Address not found in USPS database"
            }


class PostalCodeValidator:
    """Postal code validation and lookup service."""
    
    def __init__(self):
        self.us_zip_pattern = re.compile(r'^\d{5}(-\d{4})?$')
        self.canadian_postal_pattern = re.compile(r'^[A-Za-z]\d[A-Za-z] ?\d[A-Za-z]\d$')
    
    def validate_postal_code(self, postal_code: str, country: str = "US") -> Dict[str, Any]:
        """
        Validate postal code format and lookup information.
        
        Args:
            postal_code: Postal code to validate
            country: Country code (US, CA, etc.)
            
        Returns:
            Dict with validation results
        """
        if not postal_code:
            return {"valid": False, "error": "Postal code is required"}
        
        postal_code = postal_code.strip().upper()
        
        if country == "US":
            if not self.us_zip_pattern.match(postal_code):
                return {"valid": False, "error": "Invalid US ZIP code format"}
            
            # Extract ZIP code information
            zip5 = postal_code[:5]
            zip4 = postal_code[6:] if len(postal_code) > 5 else None
            
            return {
                "valid": True,
                "zip5": zip5,
                "zip4": zip4,
                "country": "US",
                "format": "US_ZIP"
            }
        
        elif country == "CA":
            if not self.canadian_postal_pattern.match(postal_code):
                return {"valid": False, "error": "Invalid Canadian postal code format"}
            
            return {
                "valid": True,
                "postal_code": postal_code,
                "country": "CA",
                "format": "CANADIAN_POSTAL"
            }
        
        else:
            return {"valid": False, "error": f"Unsupported country: {country}"}
    
    async def lookup_postal_code_info(self, postal_code: str, country: str = "US") -> Dict[str, Any]:
        """
        Lookup additional information for postal code.
        
        Args:
            postal_code: Postal code to lookup
            country: Country code
            
        Returns:
            Dict with postal code information
        """
        # Simplified implementation - in production would use actual postal databases
        if country == "US" and len(postal_code) >= 5:
            zip5 = postal_code[:5]
            
            # Mock postal code data - in production would use real database
            postal_info = {
                "zip5": zip5,
                "city": "Unknown City",
                "state": "Unknown State",
                "county": "Unknown County",
                "timezone": "Unknown",
                "area_code": "Unknown",
                "population": 0,
                "households": 0,
                "income_median": 0,
                "agricultural_area": True  # Default assumption for agricultural context
            }
            
            return postal_info
        
        return {"error": "Postal code lookup not available"}


class AddressStandardizer:
    """Address standardization service."""
    
    def __init__(self):
        # Common street type abbreviations
        self.street_types = {
            "street": "St", "avenue": "Ave", "road": "Rd", "drive": "Dr",
            "lane": "Ln", "court": "Ct", "place": "Pl", "circle": "Cir",
            "boulevard": "Blvd", "highway": "Hwy", "parkway": "Pkwy",
            "trail": "Trl", "way": "Way", "terrace": "Ter"
        }
        
        # Directional abbreviations
        self.directions = {
            "north": "N", "south": "S", "east": "E", "west": "W",
            "northeast": "NE", "northwest": "NW", "southeast": "SE", "southwest": "SW"
        }
        
        # State abbreviations
        self.state_abbreviations = {
            "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
            "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
            "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID",
            "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
            "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
            "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
            "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
            "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY",
            "north carolina": "NC", "north dakota": "ND", "ohio": "OH", "oklahoma": "OK",
            "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
            "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT",
            "vermont": "VT", "virginia": "VA", "washington": "WA", "west virginia": "WV",
            "wisconsin": "WI", "wyoming": "WY"
        }
    
    def standardize_address(self, address_string: str) -> AddressComponents:
        """
        Standardize address string into components.
        
        Args:
            address_string: Raw address string
            
        Returns:
            AddressComponents with standardized data
        """
        # Clean and normalize address string
        address_string = address_string.strip()
        
        # Parse address components
        components = self._parse_address_string(address_string)
        
        # Standardize components
        if components.street_type:
            components.street_type = self._standardize_street_type(components.street_type)
        
        if components.street_direction:
            components.street_direction = self._standardize_direction(components.street_direction)
        
        if components.state:
            components.state = self._standardize_state(components.state)
        
        if components.postal_code:
            components.postal_code = self._standardize_postal_code(components.postal_code)
        
        return components
    
    def _parse_address_string(self, address_string: str) -> AddressComponents:
        """Parse address string into components."""
        # Simplified parsing - in production would use more sophisticated parsing
        parts = address_string.split(',')
        
        if len(parts) >= 3:
            street_part = parts[0].strip()
            city_part = parts[1].strip()
            state_zip_part = parts[2].strip()
            
            # Parse street address
            street_components = self._parse_street_address(street_part)
            
            # Parse state and ZIP
            state, postal_code = self._parse_state_zip(state_zip_part)
            
            return AddressComponents(
                street_number=street_components.get('number'),
                street_name=street_components.get('name'),
                street_type=street_components.get('type'),
                street_direction=street_components.get('direction'),
                city=city_part,
                state=state,
                postal_code=postal_code
            )
        
        return AddressComponents()
    
    def _parse_street_address(self, street_part: str) -> Dict[str, str]:
        """Parse street address part."""
        words = street_part.split()
        
        if not words:
            return {}
        
        # Extract street number (first numeric part)
        street_number = None
        street_name_parts = []
        
        for i, word in enumerate(words):
            if word.isdigit():
                street_number = word
            else:
                street_name_parts = words[i:]
                break
        
        if not street_name_parts:
            return {"number": street_number}
        
        # Extract direction (first word if it's a known direction)
        street_direction = None
        if street_name_parts and street_name_parts[0].lower() in self.directions:
            street_direction = self.directions[street_name_parts[0].lower()]
            street_name_parts = street_name_parts[1:]
        
        # Extract street type (last word if it's a known type)
        street_type = None
        street_name = " ".join(street_name_parts)
        
        if street_name_parts:
            last_word = street_name_parts[-1].lower()
            if last_word in self.street_types:
                street_type = self.street_types[last_word]
                street_name = " ".join(street_name_parts[:-1])
        
        return {
            "number": street_number,
            "name": street_name,
            "type": street_type,
            "direction": street_direction
        }
    
    def _parse_state_zip(self, state_zip_part: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse state and ZIP code."""
        parts = state_zip_part.strip().split()
        
        if len(parts) >= 2:
            state = parts[0]
            postal_code = parts[1]
            return state, postal_code
        elif len(parts) == 1:
            # Could be either state or ZIP
            if parts[0].isdigit() or (len(parts[0]) == 5 and parts[0].isdigit()):
                return None, parts[0]  # ZIP code
            else:
                return parts[0], None  # State
        
        return None, None
    
    def _standardize_street_type(self, street_type: str) -> str:
        """Standardize street type abbreviation."""
        return self.street_types.get(street_type.lower(), street_type.upper())
    
    def _standardize_direction(self, direction: str) -> str:
        """Standardize directional abbreviation."""
        return self.directions.get(direction.lower(), direction.upper())
    
    def _standardize_state(self, state: str) -> str:
        """Standardize state abbreviation."""
        return self.state_abbreviations.get(state.lower(), state.upper())
    
    def _standardize_postal_code(self, postal_code: str) -> str:
        """Standardize postal code format."""
        # Remove spaces and convert to uppercase
        postal_code = postal_code.replace(" ", "").upper()
        
        # Add hyphen for US ZIP+4 format
        if len(postal_code) == 9 and postal_code.isdigit():
            return f"{postal_code[:5]}-{postal_code[5:]}"
        
        return postal_code


class AgriculturalAreaValidator:
    """Agricultural area validation service."""
    
    def __init__(self):
        # Agricultural area indicators
        self.agricultural_indicators = [
            "farm", "ranch", "agricultural", "rural", "country", "field",
            "crop", "livestock", "dairy", "vineyard", "orchard"
        ]
        
        # Rural address patterns
        self.rural_patterns = [
            r"RR\s*\d+",  # Rural Route
            r"HC\s*\d+",  # Highway Contract
            r"Box\s*\d+",  # PO Box
            r"Route\s*\d+",  # Route
            r"County\s*Road\s*\d+",  # County Road
            r"CR\s*\d+"  # County Road abbreviation
        ]
    
    async def validate_agricultural_area(self, address_components: AddressComponents) -> Dict[str, Any]:
        """
        Validate if address is in agricultural area.
        
        Args:
            address_components: AddressComponents to validate
            
        Returns:
            Dict with agricultural area validation results
        """
        agricultural_score = 0.0
        indicators = []
        
        # Check street name for agricultural indicators
        if address_components.street_name:
            street_lower = address_components.street_name.lower()
            for indicator in self.agricultural_indicators:
                if indicator in street_lower:
                    agricultural_score += 0.3
                    indicators.append(f"Street name contains '{indicator}'")
        
        # Check for rural address patterns
        full_address = self._build_full_address(address_components)
        for pattern in self.rural_patterns:
            if re.search(pattern, full_address, re.IGNORECASE):
                agricultural_score += 0.4
                indicators.append(f"Rural address pattern detected: {pattern}")
        
        # Check for rural route or box number
        if address_components.rural_route or address_components.box_number:
            agricultural_score += 0.5
            indicators.append("Rural route or PO Box address")
        
        # Check postal code for rural areas (simplified)
        if address_components.postal_code:
            postal_info = await self._get_postal_code_agricultural_info(address_components.postal_code)
            if postal_info.get("agricultural_area", False):
                agricultural_score += 0.3
                indicators.append("Postal code in agricultural area")
        
        # Determine if agricultural (lower threshold for better detection)
        is_agricultural = agricultural_score >= 0.25
        
        return {
            "is_agricultural": is_agricultural,
            "agricultural_score": min(agricultural_score, 1.0),
            "indicators": indicators,
            "confidence": "high" if agricultural_score >= 0.6 else "medium" if agricultural_score >= 0.3 else "low"
        }
    
    def _build_full_address(self, components: AddressComponents) -> str:
        """Build full address string from components."""
        parts = []
        
        if components.street_number:
            parts.append(components.street_number)
        
        if components.street_direction:
            parts.append(components.street_direction)
        
        if components.street_name:
            parts.append(components.street_name)
        
        if components.street_type:
            parts.append(components.street_type)
        
        if components.unit_number:
            parts.append(components.unit_number)
        
        return " ".join(parts)
    
    async def _get_postal_code_agricultural_info(self, postal_code: str) -> Dict[str, Any]:
        """Get agricultural information for postal code."""
        # Simplified implementation - in production would use actual agricultural databases
        # This would integrate with USDA agricultural data
        
        # Mock data based on ZIP code ranges
        zip5 = postal_code[:5] if len(postal_code) >= 5 else postal_code
        
        # Some ZIP code ranges known to be agricultural
        agricultural_zips = [
            "50001", "50002", "50003",  # Iowa agricultural areas
            "60001", "60002",  # Illinois rural areas
            "70001", "70002",  # Louisiana rural areas
        ]
        
        return {
            "agricultural_area": zip5 in agricultural_zips,
            "rural_percentage": 0.8 if zip5 in agricultural_zips else 0.2,
            "primary_land_use": "agricultural" if zip5 in agricultural_zips else "mixed"
        }


class AddressValidationService:
    """
    Comprehensive address validation and standardization service.
    
    Provides address validation, standardization, postal code validation,
    and agricultural area verification for farm location input.
    """
    
    def __init__(self, usps_api_key: Optional[str] = None):
        """Initialize the address validation service."""
        self.logger = logging.getLogger(__name__)
        
        # Initialize providers
        self.usps_provider = USPSProvider(usps_api_key)
        self.postal_validator = PostalCodeValidator()
        self.address_standardizer = AddressStandardizer()
        self.agricultural_validator = AgriculturalAreaValidator()
        
        # Validation configuration
        self.config = {
            'require_usps_validation': bool(usps_api_key),
            'agricultural_area_threshold': 0.25,
            'confidence_threshold': 0.6,  # Lower threshold for better usability
            'enable_caching': True,
            'cache_ttl_hours': 24
        }
    
    async def validate_and_standardize_address(
        self,
        address_string: str,
        include_agricultural_context: bool = True
    ) -> AddressValidationResult:
        """
        Validate and standardize an address string.
        
        Args:
            address_string: Raw address string to validate
            include_agricultural_context: Whether to include agricultural area validation
            
        Returns:
            AddressValidationResult with validation results
        """
        self.logger.info(f"Validating address: {address_string}")
        
        issues = []
        validation_sources = []
        
        try:
            # Step 1: Standardize address into components
            components = self.address_standardizer.standardize_address(address_string)
            validation_sources.append("address_standardizer")
            
            # Step 2: Validate postal code
            postal_validation = self.postal_validator.validate_postal_code(
                components.postal_code or "", components.country
            )
            
            if not postal_validation.get("valid", False):
                issues.append(AddressValidationIssue(
                    severity=AddressValidationSeverity.ERROR,
                    message=f"Invalid postal code: {postal_validation.get('error', 'Unknown error')}",
                    field="postal_code",
                    agricultural_context="Postal code validation ensures accurate location-based recommendations",
                    suggested_actions=[
                        "Verify postal code format",
                        "Check for typos in postal code",
                        "Use ZIP+4 format for US addresses"
                    ]
                ))
            else:
                validation_sources.append("postal_validator")
            
            # Step 3: USPS validation (if available)
            usps_result = None
            if self.config['require_usps_validation']:
                usps_result = await self.usps_provider.validate_address(components)
                if usps_result.get("valid", False):
                    validation_sources.append("usps")
                else:
                    issues.append(AddressValidationIssue(
                        severity=AddressValidationSeverity.WARNING,
                        message=f"USPS validation failed: {usps_result.get('error', 'Address not found')}",
                        field="address",
                        agricultural_context="USPS validation ensures address deliverability",
                        suggested_actions=[
                            "Verify address is complete and accurate",
                            "Check for typos in street name or number",
                            "Ensure address exists in postal database"
                        ]
                    ))
            
            # Step 4: Agricultural area validation
            agricultural_context = None
            if include_agricultural_context:
                agricultural_result = await self.agricultural_validator.validate_agricultural_area(components)
                agricultural_context = agricultural_result
                validation_sources.append("agricultural_validator")
                
                if not agricultural_result.get("is_agricultural", False):
                    issues.append(AddressValidationIssue(
                        severity=AddressValidationSeverity.INFO,
                        message="Address may not be in agricultural area",
                        agricultural_context="Agricultural area validation helps ensure relevant recommendations",
                        suggested_actions=[
                            "Verify this is an agricultural location",
                            "Provide additional context about farming operations",
                            "Consider using GPS coordinates for precise location"
                        ]
                    ))
            
            # Step 5: Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                postal_validation, usps_result, agricultural_context
            )
            
            # Step 6: Determine overall validity
            has_errors = any(issue.severity == AddressValidationSeverity.ERROR for issue in issues)
            is_valid = not has_errors and confidence_score >= self.config['confidence_threshold']
            
            # Step 7: Build standardized address string
            standardized_address = self._build_standardized_address(components)
            
            result = AddressValidationResult(
                valid=is_valid,
                standardized_address=standardized_address,
                components=components,
                confidence_score=confidence_score,
                issues=issues,
                warnings=[issue.message for issue in issues if issue.severity == AddressValidationSeverity.WARNING],
                errors=[issue.message for issue in issues if issue.severity == AddressValidationSeverity.ERROR],
                agricultural_area_verified=agricultural_context.get("is_agricultural", False) if agricultural_context else False,
                agricultural_context=agricultural_context,
                validation_sources=validation_sources
            )
            
            self.logger.info(f"Address validation completed: valid={is_valid}, confidence={confidence_score:.2f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Address validation error: {e}")
            return AddressValidationResult(
                valid=False,
                confidence_score=0.0,
                errors=[f"Address validation failed: {str(e)}"],
                validation_sources=["error"]
            )
    
    def _calculate_confidence_score(
        self,
        postal_validation: Dict[str, Any],
        usps_result: Optional[Dict[str, Any]],
        agricultural_context: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate overall confidence score."""
        score = 0.0
        
        # Postal code validation (40% weight)
        if postal_validation.get("valid", False):
            score += 0.4
        
        # USPS validation (40% weight)
        if usps_result and usps_result.get("valid", False):
            score += 0.4
        elif usps_result is None:  # USPS not available
            score += 0.2  # Partial credit for not being available
        
        # Agricultural context (20% weight)
        if agricultural_context and agricultural_context.get("is_agricultural", False):
            score += 0.2
        
        return min(score, 1.0)
    
    def _build_standardized_address(self, components: AddressComponents) -> str:
        """Build standardized address string from components."""
        parts = []
        
        # Street address
        street_parts = []
        if components.street_number:
            street_parts.append(components.street_number)
        if components.street_direction:
            street_parts.append(components.street_direction)
        if components.street_name:
            street_parts.append(components.street_name)
        if components.street_type:
            street_parts.append(components.street_type)
        if components.unit_number:
            street_parts.append(components.unit_number)
        
        if street_parts:
            parts.append(" ".join(street_parts))
        
        # City, State ZIP
        city_state_zip_parts = []
        if components.city:
            city_state_zip_parts.append(components.city)
        if components.state:
            city_state_zip_parts.append(components.state)
        if components.postal_code:
            city_state_zip_parts.append(components.postal_code)
        
        if city_state_zip_parts:
            parts.append(", ".join(city_state_zip_parts))
        
        return ", ".join(parts)
    
    async def validate_address_components(self, components: AddressComponents) -> AddressValidationResult:
        """
        Validate pre-parsed address components.
        
        Args:
            components: AddressComponents to validate
            
        Returns:
            AddressValidationResult with validation results
        """
        # Validate components directly without re-parsing
        issues = []
        validation_sources = []
        
        try:
            # Step 1: Validate postal code
            postal_validation = self.postal_validator.validate_postal_code(
                components.postal_code or "", components.country
            )
            
            if not postal_validation.get("valid", False):
                issues.append(AddressValidationIssue(
                    severity=AddressValidationSeverity.ERROR,
                    message=f"Invalid postal code: {postal_validation.get('error', 'Unknown error')}",
                    field="postal_code",
                    agricultural_context="Postal code validation ensures accurate location-based recommendations",
                    suggested_actions=[
                        "Verify postal code format",
                        "Check for typos in postal code",
                        "Use ZIP+4 format for US addresses"
                    ]
                ))
            else:
                validation_sources.append("postal_validator")
            
            # Step 2: USPS validation (if available)
            usps_result = None
            if self.config['require_usps_validation']:
                usps_result = await self.usps_provider.validate_address(components)
                if usps_result.get("valid", False):
                    validation_sources.append("usps")
                else:
                    issues.append(AddressValidationIssue(
                        severity=AddressValidationSeverity.WARNING,
                        message=f"USPS validation failed: {usps_result.get('error', 'Address not found')}",
                        field="address",
                        agricultural_context="USPS validation ensures address deliverability",
                        suggested_actions=[
                            "Verify address is complete and accurate",
                            "Check for typos in street name or number",
                            "Ensure address exists in postal database"
                        ]
                    ))
            
            # Step 3: Agricultural area validation
            agricultural_context = None
            agricultural_result = await self.agricultural_validator.validate_agricultural_area(components)
            agricultural_context = agricultural_result
            validation_sources.append("agricultural_validator")
            
            if not agricultural_result.get("is_agricultural", False):
                issues.append(AddressValidationIssue(
                    severity=AddressValidationSeverity.INFO,
                    message="Address may not be in agricultural area",
                    agricultural_context="Agricultural area validation helps ensure relevant recommendations",
                    suggested_actions=[
                        "Verify this is an agricultural location",
                        "Provide additional context about farming operations",
                        "Consider using GPS coordinates for precise location"
                    ]
                ))
            
            # Step 4: Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                postal_validation, usps_result, agricultural_context
            )
            
            # Step 5: Determine overall validity
            has_errors = any(issue.severity == AddressValidationSeverity.ERROR for issue in issues)
            is_valid = not has_errors and confidence_score >= self.config['confidence_threshold']
            
            # Step 6: Build standardized address string
            standardized_address = self._build_standardized_address(components)
            
            result = AddressValidationResult(
                valid=is_valid,
                standardized_address=standardized_address,
                components=components,
                confidence_score=confidence_score,
                issues=issues,
                warnings=[issue.message for issue in issues if issue.severity == AddressValidationSeverity.WARNING],
                errors=[issue.message for issue in issues if issue.severity == AddressValidationSeverity.ERROR],
                agricultural_area_verified=agricultural_context.get("is_agricultural", False) if agricultural_context else False,
                agricultural_context=agricultural_context,
                validation_sources=validation_sources
            )
            
            self.logger.info(f"Address components validation completed: valid={is_valid}, confidence={confidence_score:.2f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Address components validation error: {e}")
            return AddressValidationResult(
                valid=False,
                confidence_score=0.0,
                errors=[f"Address components validation failed: {str(e)}"],
                validation_sources=["error"]
            )
    
    async def batch_validate_addresses(
        self,
        addresses: List[str],
        include_agricultural_context: bool = True
    ) -> List[AddressValidationResult]:
        """
        Validate multiple addresses in batch.
        
        Args:
            addresses: List of address strings to validate
            include_agricultural_context: Whether to include agricultural context
            
        Returns:
            List of AddressValidationResult objects
        """
        self.logger.info(f"Batch validating {len(addresses)} addresses")
        
        # Process addresses concurrently
        tasks = [
            self.validate_and_standardize_address(addr, include_agricultural_context)
            for addr in addresses
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        validated_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Batch validation error for address {i}: {result}")
                validated_results.append(AddressValidationResult(
                    valid=False,
                    confidence_score=0.0,
                    errors=[f"Validation failed: {str(result)}"],
                    validation_sources=["error"]
                ))
            else:
                validated_results.append(result)
        
        self.logger.info(f"Batch validation completed: {len(validated_results)} results")
        return validated_results


# Export the service
__all__ = [
    'AddressValidationService', 'AddressValidationResult', 'AddressComponents',
    'AddressValidationIssue', 'AddressValidationSeverity', 'USPSProvider',
    'PostalCodeValidator', 'AddressStandardizer', 'AgriculturalAreaValidator'
]
