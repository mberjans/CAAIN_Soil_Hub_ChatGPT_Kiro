# Enhanced Crop Filtering Attributes Model Design

## Overview

This document outlines the design for enhancing the CropFilteringAttributes model in the CAAIN Soil Hub project. The goal is to improve the `pest_resistance_traits`, `market_class_filters`, `certification_filters`, and `seed_availability_filters` fields to provide more sophisticated filtering capabilities while maintaining backward compatibility.

## Current Model Structure

The existing `CropFilteringAttributes` model uses generic `Dict[str, Any]` for the four advanced filtering fields. This approach lacks structure, proper validation, and specialized functionality needed for complex filtering operations.

## Enhanced Design Requirements

### 1. pest_resistance_traits Enhancement

**Current State**: `pest_resistance_traits: Dict[str, Any] = Field(default_factory=dict)`

**Enhanced Design**: Complex pest resistance data with levels and additional metadata

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from datetime import datetime
from uuid import UUID

class PestResistanceLevel(str, Enum):
    """Levels of pest resistance."""
    SUSCEPTIBLE = "susceptible"
    LOW = "low"
    MODERATE = "moderate"
    GOOD = "good"
    HIGH = "high"
    RESISTANT = "resistant"
    IMMUNE = "immune"

class PestResistanceProfile(BaseModel):
    """Detailed pest resistance profile with metadata."""
    pest_name: str = Field(..., description="Name of the pest")
    resistance_level: PestResistanceLevel = Field(..., description="Level of resistance")
    resistance_gene: Optional[str] = Field(None, description="Specific resistance gene if known")
    effectiveness_rating: float = Field(ge=0.0, le=1.0, default=0.5, description="Effectiveness rating of resistance")
    research_status: str = Field(default="established", description="Research status of resistance trait")
    confidence: float = Field(ge=0.0, le=1.0, default=0.7, description="Confidence in the resistance data")
    source: Optional[str] = Field(None, description="Source of the resistance information")
    notes: Optional[List[str]] = Field(None, description="Additional notes about the resistance trait")
    last_updated: Optional[datetime] = Field(None, description="Last updated timestamp for this resistance trait")

class EnhancedPestResistanceTraits(BaseModel):
    """Enhanced pest resistance data structure."""
    profiles: Dict[str, PestResistanceProfile] = Field(
        default_factory=dict,
        description="Pest resistance profiles keyed by pest name"
    )
    
    def get_resistance_level(self, pest_name: str) -> Optional[str]:
        """Get the resistance level for a specific pest."""
        profile = self.profiles.get(pest_name)
        return profile.resistance_level.value if profile else None
    
    def resistance_meets_threshold(self, pest_name: str, threshold: PestResistanceLevel) -> bool:
        """Check if resistance to a pest meets or exceeds the threshold."""
        current_level = self.get_resistance_level(pest_name)
        if not current_level:
            return False
        return self._compare_resistance_levels(current_level, threshold)
    
    def _compare_resistance_levels(self, current: str, required: PestResistanceLevel) -> bool:
        """Compare resistance levels to determine if requirements are met."""
        level_rankings = {
            "susceptible": 0,
            "low": 1,
            "moderate": 2,
            "good": 3,
            "high": 4,
            "resistant": 4,
            "immune": 5
        }
        current_rank = level_rankings.get(current, 0)
        required_rank = level_rankings.get(required.value, 0)
        return current_rank >= required_rank
```

### 2. market_class_filters Enhancement

**Current State**: `market_class_filters: Dict[str, Any] = Field(default_factory=dict)`

**Enhanced Design**: Specialty market classifications like organic, non-GMO, heirloom, etc.

```python
class MarketClassType(str, Enum):
    """Types of market classifications."""
    ORGANIC = "organic"
    NON_GMO = "non_gmo"
    HEIRLOOM = "heirloom"
    HERITAGE = "heritage"
    SPECIALTY = "specialty"
    REGIONAL = "regional"
    LOCAL = "local"
    GOURMET = "gourmet"
    ORNAMENTAL = "ornamental"
    MEDICINAL = "medicinal"

class MarketClassProfile(BaseModel):
    """Profile for market class characteristics."""
    market_class: MarketClassType = Field(..., description="Type of market class")
    is_certified: bool = Field(default=True, description="Whether the crop is certified for this market class")
    certification_body: Optional[str] = Field(None, description="Certifying body if applicable")
    certification_date: Optional[datetime] = Field(None, description="Date of certification")
    expires_date: Optional[datetime] = Field(None, description="Expiration date of certification")
    market_premium: Optional[float] = Field(None, description="Expected premium for this market class")
    market_demand: str = Field(default="moderate", description="Level of market demand")
    target_audience: Optional[str] = Field(None, description="Primary target audience")
    unique_characteristics: List[str] = Field(default_factory=list, description="Unique characteristics of this market class")
    notes: Optional[List[str]] = Field(None, description="Additional notes about the market class")
    active: bool = Field(default=True, description="Whether this market class is currently active")

class EnhancedMarketClassFilters(BaseModel):
    """Enhanced market class filtering data structure."""
    profiles: Dict[MarketClassType, MarketClassProfile] = Field(
        default_factory=dict,
        description="Market class profiles keyed by market class type"
    )
    
    def supports_market_class(self, market_class: MarketClassType) -> bool:
        """Check if the crop supports a specific market class."""
        profile = self.profiles.get(market_class)
        return profile.is_certified if profile else False
    
    def get_market_premium(self, market_class: MarketClassType) -> Optional[float]:
        """Get the expected market premium for a specific market class."""
        profile = self.profiles.get(market_class)
        return profile.market_premium if profile and profile.active else None
    
    def get_all_active_classes(self) -> List[MarketClassType]:
        """Get all active market classes."""
        return [k for k, v in self.profiles.items() if v.active and v.is_certified]
```

### 3. certification_filters Enhancement

**Current State**: `certification_filters: Dict[str, Any] = Field(default_factory=dict)`

**Enhanced Design**: Various certifications like organic, non-GMO, fair trade, etc.

```python
class CertificationType(str, Enum):
    """Types of certifications."""
    USDA_ORGANIC = "usda_organic"
    EU_ORGANIC = "eu_organic"
    JAS_ORGANIC = "jas_organic"
    NON_GMO_PROJECT = "non_gmo_project"
    FAIR_TRADE = "fair_trade"
    RAIN_FOREST_ALLIANCE = "rain_forest_alliance"
    BIODIVERSITY_FRIENDLY = "biodiversity_friendly"
    ANIMAL_WELFARE = "animal_welfare"
    CARBON_NEUTRAL = "carbon_neutral"
    SUSTAINABLE_AGRICULTURE = "sustainable_agriculture"
    REGENERATIVE_ORGANIC = "regenerative_organic"

class CertificationProfile(BaseModel):
    """Profile for certification details."""
    certification_type: CertificationType = Field(..., description="Type of certification")
    certifying_body: str = Field(..., description="Organization providing the certification")
    certification_number: Optional[str] = Field(None, description="Certification number")
    issue_date: Optional[datetime] = Field(None, description="Date certification was issued")
    expiry_date: Optional[datetime] = Field(None, description="Date certification expires")
    status: str = Field(default="active", description="Current status of certification")
    scope: List[str] = Field(default_factory=list, description="Scope of certification")
    standards_complied: List[str] = Field(default_factory=list, description="Standards complied with")
    audit_schedule: Optional[List[datetime]] = Field(None, description="Scheduled audit dates")
    notes: Optional[List[str]] = Field(None, description="Additional notes about the certification")
    requirements: Dict[str, Any] = Field(default_factory=dict, description="Specific requirements for maintaining certification")
    compliance_status: str = Field(default="compliant", description="Compliance status")
    last_inspection_date: Optional[datetime] = Field(None, description="Date of last inspection")

class EnhancedCertificationFilters(BaseModel):
    """Enhanced certification filtering data structure."""
    profiles: Dict[CertificationType, CertificationProfile] = Field(
        default_factory=dict,
        description="Certification profiles keyed by certification type"
    )
    
    def has_certification(self, cert_type: CertificationType) -> bool:
        """Check if the crop has a specific certification."""
        profile = self.profiles.get(cert_type)
        return profile.status == "active" if profile else False
    
    def is_compliant_with_certification(self, cert_type: CertificationType) -> bool:
        """Check if the crop is compliant with a specific certification."""
        profile = self.profiles.get(cert_type)
        return profile.compliance_status == "compliant" if profile else False
    
    def get_certification_expiry_date(self, cert_type: CertificationType) -> Optional[datetime]:
        """Get the expiry date for a specific certification."""
        profile = self.profiles.get(cert_type)
        return profile.expiry_date if profile else None
    
    def get_active_certifications(self) -> List[CertificationType]:
        """Get all active certifications."""
        return [k for k, v in self.profiles.items() if v.status == "active"]
```

### 4. seed_availability_filters Enhancement

**Current State**: `seed_availability_filters: Dict[str, Any] = Field(default_factory=dict)`

**Enhanced Design**: Regional and supplier information for seed availability

```python
class SeedAvailabilityStatus(str, Enum):
    """Status of seed availability."""
    AVAILABLE = "available"
    LIMITED = "limited"
    OUT_OF_STOCK = "out_of_stock"
    SEASONAL = "seasonal"
    PRE_ORDER = "pre_order"
    DISCONTINUED = "discontinued"

class SupplierInfo(BaseModel):
    """Information about a seed supplier."""
    supplier_id: UUID = Field(..., description="Unique identifier for the supplier")
    supplier_name: str = Field(..., description="Name of the supplier")
    contact_info: Optional[str] = Field(None, description="Contact information")
    regions_served: List[str] = Field(default_factory=list, description="Regions where supplier operates")
    website: Optional[str] = Field(None, description="Supplier's website")
    minimum_order_quantity: Optional[int] = Field(None, description="Minimum order quantity")
    shipping_options: List[str] = Field(default_factory=list, description="Available shipping options")
    specializations: List[str] = Field(default_factory=list, description="Specialized seed types")
    certification_status: List[str] = Field(default_factory=list, description="Supplier certifications")

class RegionalAvailability(BaseModel):
    """Regional availability information."""
    region_code: str = Field(..., description="Region code (ISO, USDA zone, etc.)")
    region_name: str = Field(..., description="Full name of the region")
    availability_status: SeedAvailabilityStatus = Field(..., description="Current availability status")
    availability_date: Optional[datetime] = Field(None, description="Date when seeds will be available")
    quantity_available: Optional[int] = Field(None, description="Quantity available")
    seasonality: Optional[str] = Field(None, description="Seasonal availability pattern")
    regional_notes: Optional[List[str]] = Field(None, description="Regional-specific notes")
    supplier_details: Dict[str, SupplierInfo] = Field(default_factory=dict, description="Supplier details for this region")

class SeedVarietyAvailability(BaseModel):
    """Availability information for a specific seed variety."""
    variety_name: str = Field(..., description="Name of the seed variety")
    availability_status: SeedAvailabilityStatus = Field(..., description="Overall availability status")
    regional_availability: Dict[str, RegionalAvailability] = Field(default_factory=dict, description="Regional availability data")
    suppliers: Dict[str, SupplierInfo] = Field(default_factory=dict, description="Supplier information")
    minimum_order_quantity: Optional[int] = Field(None, description="Minimum order quantity")
    price_range: Optional[Dict[str, float]] = Field(None, description="Price range information")
    shipping_notes: Optional[str] = Field(None, description="Shipping availability notes")
    availability_notes: Optional[List[str]] = Field(None, description="General availability notes")
    last_updated: Optional[datetime] = Field(None, description="Last updated timestamp")

class EnhancedSeedAvailabilityFilters(BaseModel):
    """Enhanced seed availability filtering data structure."""
    varieties: Dict[str, SeedVarietyAvailability] = Field(
        default_factory=dict,
        description="Availability information for different seed varieties"
    )
    
    def is_available_in_region(self, variety_name: str, region_code: str) -> bool:
        """Check if seeds are available in a specific region."""
        variety = self.varieties.get(variety_name)
        if not variety:
            return False
        region_availability = variety.regional_availability.get(region_code)
        return region_availability.availability_status in [
            SeedAvailabilityStatus.AVAILABLE,
            SeedAvailabilityStatus.SEASONAL,
            SeedAvailabilityStatus.PRE_ORDER
        ] if region_availability else False
    
    def get_suppliers_in_region(self, variety_name: str, region_code: str) -> List[SupplierInfo]:
        """Get suppliers available in a specific region for a variety."""
        variety = self.varieties.get(variety_name)
        if not variety or region_code not in variety.regional_availability:
            return []
        
        region = variety.regional_availability[region_code]
        return list(region.supplier_details.values())
    
    def get_regional_availability(self, variety_name: str, region_code: str) -> Optional[RegionalAvailability]:
        """Get detailed regional availability information."""
        variety = self.varieties.get(variety_name)
        if not variety:
            return None
        return variety.regional_availability.get(region_code)
    
    def get_all_varieties_available_in_region(self, region_code: str) -> List[str]:
        """Get all varieties available in a specific region."""
        available_varieties = []
        for variety_name, variety in self.varieties.items():
            region_availability = variety.regional_availability.get(region_code)
            if region_availability and region_availability.availability_status in [
                SeedAvailabilityStatus.AVAILABLE,
                SeedAvailabilityStatus.SEASONAL,
                SeedAvailabilityStatus.PRE_ORDER
            ]:
                available_varieties.append(variety_name)
        return available_varieties
```

## Enhanced CropFilteringAttributes Model

```python
class CropFilteringAttributes(BaseModel):
    """Comprehensive filtering attributes for advanced crop search with enhanced fields."""

    filter_id: Optional[UUID] = Field(None, description="Unique filter attributes identifier")
    crop_id: UUID = Field(..., description="Associated crop identifier")
    
    # Seasonality attributes
    planting_season: List[str] = Field(default_factory=lambda: ["spring"], description="Planting seasons")
    growing_season: List[str] = Field(default_factory=lambda: ["summer"], description="Growing seasons")
    harvest_season: List[str] = Field(default_factory=lambda: ["fall"], description="Harvest seasons")
    
    # Agricultural system compatibility
    farming_systems: List[str] = Field(default_factory=lambda: ["conventional"], description="Compatible farming systems")
    rotation_compatibility: List[str] = Field(default_factory=list, description="Rotation-compatible crops")
    intercropping_compatible: bool = Field(default=False, description="Suitable for intercropping")
    cover_crop_compatible: bool = Field(default=True, description="Works with cover crops")
    
    # Management characteristics
    management_complexity: Optional[ManagementComplexity] = Field(None, description="Management complexity level")
    input_requirements: Optional[InputRequirements] = Field(None, description="Input requirement level")
    labor_requirements: Optional[LaborRequirements] = Field(None, description="Labor requirement level")
    
    # Technology compatibility
    precision_ag_compatible: bool = Field(default=True, description="Precision agriculture compatible")
    gps_guidance_recommended: bool = Field(default=False, description="GPS guidance recommended")
    sensor_monitoring_beneficial: bool = Field(default=False, description="Benefits from sensor monitoring")
    
    # Sustainability attributes
    carbon_sequestration_potential: Optional[CarbonSequestrationPotential] = Field(None, description="Carbon sequestration potential")
    biodiversity_support: Optional[BiodiversitySupport] = Field(None, description="Biodiversity support level")
    pollinator_value: Optional[PollinatorValue] = Field(None, description="Pollinator support value")
    water_use_efficiency: Optional[WaterUseEfficiency] = Field(None, description="Water use efficiency")
    
    # Market and economic attributes
    market_stability: Optional[MarketStability] = Field(None, description="Market stability level")
    price_premium_potential: bool = Field(default=False, description="Potential for price premiums")
    value_added_opportunities: List[str] = Field(default_factory=list, description="Value-added processing opportunities")
    
    # Enhanced advanced filtering attributes
    pest_resistance_traits: Union[Dict[str, Any], EnhancedPestResistanceTraits] = Field(
        default_factory=EnhancedPestResistanceTraits,
        description="Enhanced pest resistance traits with levels and metadata"
    )
    market_class_filters: Union[Dict[str, Any], EnhancedMarketClassFilters] = Field(
        default_factory=EnhancedMarketClassFilters,
        description="Enhanced market class filters supporting specialty segmentation"
    )
    certification_filters: Union[Dict[str, Any], EnhancedCertificationFilters] = Field(
        default_factory=EnhancedCertificationFilters,
        description="Enhanced certification-based filters such as organic or non-GMO"
    )
    seed_availability_filters: Union[Dict[str, Any], EnhancedSeedAvailabilityFilters] = Field(
        default_factory=EnhancedSeedAvailabilityFilters,
        description="Enhanced seed availability filters across suppliers and regions"
    )

    # Metadata
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    # Validation methods to maintain backward compatibility and support enhanced functionality
    @validator('pest_resistance_traits', pre=True, always=True)
    def _validate_pest_resistance_traits(cls, value):
        """Handle both legacy dict and new enhanced model."""
        if isinstance(value, EnhancedPestResistanceTraits):
            return value
        if isinstance(value, dict):
            # Convert legacy dict format to enhanced model for backward compatibility
            try:
                # Attempt to create the enhanced model from the dict
                profiles = {}
                for pest_name, pest_data in value.items():
                    if isinstance(pest_data, dict):
                        profile = PestResistanceProfile(pest_name=pest_name, **pest_data)
                    else:
                        # If it's a simple value, create a basic profile
                        profile = PestResistanceProfile(
                            pest_name=pest_name,
                            resistance_level=PestResistanceLevel.MODERATE,
                            effectiveness_rating=0.5,
                            notes=[str(pest_data)] if pest_data else None
                        )
                    profiles[pest_name] = profile
                return EnhancedPestResistanceTraits(profiles=profiles)
            except Exception:
                # Fallback to empty enhanced model
                return EnhancedPestResistanceTraits()
        return EnhancedPestResistanceTraits()

    @validator('market_class_filters', pre=True, always=True)
    def _validate_market_class_filters(cls, value):
        """Handle both legacy dict and new enhanced model."""
        if isinstance(value, EnhancedMarketClassFilters):
            return value
        if isinstance(value, dict):
            # Convert legacy dict format to enhanced model for backward compatibility
            try:
                profiles = {}
                for class_name, class_data in value.items():
                    if isinstance(class_data, dict):
                        market_class = MarketClassType(class_name) if class_name in MarketClassType.__members__ else None
                        if market_class:
                            profile = MarketClassProfile(market_class=market_class, **class_data)
                            profiles[market_class] = profile
                    else:
                        # If it's a simple value, create a basic profile
                        if class_name in MarketClassType.__members__:
                            market_class = MarketClassType(class_name)
                            profile = MarketClassProfile(
                                market_class=market_class,
                                is_certified=bool(class_data) if class_data is not None else True
                            )
                            profiles[market_class] = profile
                return EnhancedMarketClassFilters(profiles=profiles)
            except Exception:
                # Fallback to empty enhanced model
                return EnhancedMarketClassFilters()
        return EnhancedMarketClassFilters()

    @validator('certification_filters', pre=True, always=True)
    def _validate_certification_filters(cls, value):
        """Handle both legacy dict and new enhanced model."""
        if isinstance(value, EnhancedCertificationFilters):
            return value
        if isinstance(value, dict):
            # Convert legacy dict format to enhanced model for backward compatibility
            try:
                profiles = {}
                for cert_name, cert_data in value.items():
                    if isinstance(cert_data, dict):
                        cert_type = CertificationType(cert_name) if cert_name in CertificationType.__members__ else None
                        if cert_type:
                            profile = CertificationProfile(certification_type=cert_type, **cert_data)
                            profiles[cert_type] = profile
                    else:
                        # If it's a simple value, create a basic profile
                        if cert_name in CertificationType.__members__:
                            cert_type = CertificationType(cert_name)
                            profile = CertificationProfile(
                                certification_type=cert_type,
                                certifying_body="Unknown",
                                status="active" if bool(cert_data) else "inactive"
                            )
                            profiles[cert_type] = profile
                return EnhancedCertificationFilters(profiles=profiles)
            except Exception:
                # Fallback to empty enhanced model
                return EnhancedCertificationFilters()
        return EnhancedCertificationFilters()

    @validator('seed_availability_filters', pre=True, always=True)
    def _validate_seed_availability_filters(cls, value):
        """Handle both legacy dict and new enhanced model."""
        if isinstance(value, EnhancedSeedAvailabilityFilters):
            return value
        if isinstance(value, dict):
            # Convert legacy dict format to enhanced model for backward compatibility
            try:
                varieties = {}
                for variety_name, variety_data in value.items():
                    if isinstance(variety_data, dict):
                        # Convert the variety data to the new format
                        regional_availability = {}
                        suppliers = {}
                        
                        # Process regional availability data if present
                        if 'regional_availability' in variety_data:
                            for region_code, region_data in variety_data['regional_availability'].items():
                                if isinstance(region_data, dict):
                                    # Process supplier details for this region
                                    region_suppliers = {}
                                    if 'suppliers' in region_data:
                                        for sup_id, sup_data in region_data['suppliers'].items():
                                            supplier_id = UUID(sup_data.get('supplier_id', str(uuid4()))) if 'supplier_id' in sup_data else uuid4()
                                            supplier_info = SupplierInfo(
                                                supplier_id=supplier_id,
                                                supplier_name=sup_data.get('supplier_name', ''),
                                                **{k: v for k, v in sup_data.items() if k != 'supplier_id'}
                                            )
                                            region_suppliers[sup_id] = supplier_info
                                    
                                    region_av = RegionalAvailability(
                                        region_code=region_code,
                                        region_name=region_data.get('region_name', region_code),
                                        availability_status=SeedAvailabilityStatus(region_data.get('availability_status', 'available')),
                                        supplier_details=region_suppliers,
                                        **{k: v for k, v in region_data.items() 
                                           if k not in ['region_code', 'region_name', 'availability_status', 'suppliers']}
                                    )
                                    regional_availability[region_code] = region_av
                        
                        # Process suppliers data if present
                        if 'suppliers' in variety_data:
                            for sup_id, sup_data in variety_data['suppliers'].items():
                                supplier_id = UUID(sup_data.get('supplier_id', str(uuid4()))) if 'supplier_id' in sup_data else uuid4()
                                supplier_info = SupplierInfo(
                                    supplier_id=supplier_id,
                                    supplier_name=sup_data.get('supplier_name', ''),
                                    **{k: v for k, v in sup_data.items() if k != 'supplier_id'}
                                )
                                suppliers[sup_id] = supplier_info
                        
                        # Create the variety availability model
                        variety_availability = SeedVarietyAvailability(
                            variety_name=variety_name,
                            availability_status=SeedAvailabilityStatus(variety_data.get('availability_status', 'available')),
                            regional_availability=regional_availability,
                            suppliers=suppliers,
                            **{k: v for k, v in variety_data.items() 
                               if k not in ['variety_name', 'availability_status', 'regional_availability', 'suppliers']}
                        )
                        varieties[variety_name] = variety_availability
                    else:
                        # If it's a simple value, create a basic availability entry
                        availability_status = SeedAvailabilityStatus.AVAILABLE if bool(variety_data) else SeedAvailabilityStatus.OUT_OF_STOCK
                        variety_availability = SeedVarietyAvailability(
                            variety_name=variety_name,
                            availability_status=availability_status
                        )
                        varieties[variety_name] = variety_availability
                
                return EnhancedSeedAvailabilityFilters(varieties=varieties)
            except Exception:
                # Fallback to empty enhanced model
                return EnhancedSeedAvailabilityFilters()
        return EnhancedSeedAvailabilityFilters()
```

## Backward Compatibility Strategy

The enhanced design maintains complete backward compatibility by:

1. **Union Types**: Using Union[Dict[str, Any], EnhancedModel] to accept both legacy and new formats
2. **Validation Converters**: The validator methods convert legacy dict format to enhanced models when possible
3. **Default Fallbacks**: Providing default enhanced models when conversion fails
4. **Optional Fields**: Keeping new fields optional so existing data remains valid

## Validation and Functionality Improvements

Each enhanced field now includes:
- Structured data models with proper validation
- Specific methods for querying and filtering
- Metadata support for better data management
- Consistent API for interacting with the data
- Improved error handling and fallback mechanisms

## Implementation Notes

1. The enhanced models should be implemented in the existing file to maintain consistency
2. Appropriate imports need to be added for the new enums and models
3. The validation methods ensure that existing data continues to work
4. New functionality is accessible through the enhanced models while maintaining the existing API