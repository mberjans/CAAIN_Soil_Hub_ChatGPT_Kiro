"""
Cover Crop Data Models

Pydantic models for cover crop selection, species data, and recommendations.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import date, datetime
from enum import Enum


class CoverCropType(str, Enum):
    """Cover crop functional types."""
    LEGUME = "legume"
    GRASS = "grass"
    BRASSICA = "brassica"
    FORB = "forb"
    MIXTURE = "mixture"


class GrowingSeason(str, Enum):
    """Cover crop growing seasons."""
    WINTER = "winter"
    SUMMER = "summer"
    SPRING = "spring"
    FALL = "fall"
    YEAR_ROUND = "year_round"


class SoilBenefit(str, Enum):
    """Primary soil benefits from cover crops."""
    NITROGEN_FIXATION = "nitrogen_fixation"
    EROSION_CONTROL = "erosion_control"
    ORGANIC_MATTER = "organic_matter"
    COMPACTION_RELIEF = "compaction_relief"
    WEED_SUPPRESSION = "weed_suppression"
    PEST_MANAGEMENT = "pest_management"
    NUTRIENT_SCAVENGING = "nutrient_scavenging"
    SOIL_STRUCTURE = "soil_structure"


class CoverCropSpecies(BaseModel):
    """Individual cover crop species data."""
    
    species_id: str = Field(..., description="Unique species identifier")
    common_name: str = Field(..., description="Common name")
    scientific_name: str = Field(..., description="Scientific name")
    cover_crop_type: CoverCropType = Field(..., description="Functional type")
    
    # Climate requirements
    hardiness_zones: List[str] = Field(..., description="USDA hardiness zones")
    min_temp_f: Optional[float] = Field(None, description="Minimum temperature tolerance (°F)")
    max_temp_f: Optional[float] = Field(None, description="Maximum temperature tolerance (°F)")
    growing_season: GrowingSeason = Field(..., description="Primary growing season")
    
    # Soil requirements
    ph_range: Dict[str, float] = Field(..., description="pH tolerance range")
    drainage_tolerance: List[str] = Field(..., description="Drainage class tolerance")
    salt_tolerance: Optional[str] = Field(None, description="Salt tolerance level")
    
    # Growth characteristics
    seeding_rate_lbs_acre: Dict[str, float] = Field(..., description="Seeding rates by method")
    planting_depth_inches: float = Field(..., ge=0.0, description="Planting depth in inches")
    days_to_establishment: int = Field(..., ge=1, description="Days to establishment")
    biomass_production: str = Field(..., description="Biomass production level")
    
    # Soil benefits
    primary_benefits: List[SoilBenefit] = Field(..., description="Primary soil benefits")
    nitrogen_fixation_lbs_acre: Optional[float] = Field(None, ge=0, description="Nitrogen fixation potential")
    root_depth_feet: Optional[float] = Field(None, ge=0, description="Root depth in feet")
    
    # Agronomic considerations
    termination_methods: List[str] = Field(..., description="Termination options")
    cash_crop_compatibility: List[str] = Field(..., description="Compatible cash crops")
    potential_issues: Optional[List[str]] = Field(None, description="Potential problems")
    
    # Economic data
    seed_cost_per_acre: Optional[float] = Field(None, ge=0, description="Seed cost estimate")
    establishment_cost_per_acre: Optional[float] = Field(None, ge=0, description="Total establishment cost")
    
    @validator('ph_range')
    def validate_ph_range(cls, v):
        """Validate pH range."""
        if 'min' not in v or 'max' not in v:
            raise ValueError("pH range must include 'min' and 'max' values")
        if not (3.0 <= v['min'] <= 10.0) or not (3.0 <= v['max'] <= 10.0):
            raise ValueError("pH values must be between 3.0 and 10.0")
        if v['min'] >= v['max']:
            raise ValueError("Minimum pH must be less than maximum pH")
        return v


class SoilConditions(BaseModel):
    """Current soil conditions for cover crop selection."""
    
    ph: float = Field(..., ge=3.0, le=10.0, description="Current soil pH")
    organic_matter_percent: float = Field(..., ge=0.0, le=15.0, description="Organic matter percentage")
    drainage_class: str = Field(..., description="Soil drainage classification")
    texture: Optional[str] = Field(None, description="Soil texture class")
    compaction_issues: bool = Field(default=False, description="Soil compaction present")
    erosion_risk: str = Field(default="low", description="Erosion risk level")
    nitrogen_status: Optional[str] = Field(None, description="Nitrogen availability")
    previous_cover_crop: Optional[str] = Field(None, description="Previous cover crop")


class ClimateData(BaseModel):
    """Climate data for cover crop selection."""
    
    hardiness_zone: str = Field(..., description="USDA hardiness zone")
    average_annual_precipitation: Optional[float] = Field(None, ge=0, description="Annual precipitation (inches)")
    growing_season_length: Optional[int] = Field(None, ge=0, le=365, description="Growing season days")
    last_frost_date: Optional[date] = Field(None, description="Average last frost date")
    first_frost_date: Optional[date] = Field(None, description="Average first frost date")
    drought_risk: Optional[str] = Field(None, description="Drought risk level")
    heat_stress_risk: Optional[str] = Field(None, description="Heat stress risk")


class CoverCropObjectives(BaseModel):
    """Farmer objectives for cover crop selection."""
    
    primary_goals: List[SoilBenefit] = Field(..., description="Primary objectives")
    nitrogen_needs: bool = Field(default=False, description="Need nitrogen fixation")
    erosion_control_priority: bool = Field(default=False, description="Erosion control priority")
    organic_matter_goal: bool = Field(default=False, description="Organic matter improvement")
    weed_suppression_needed: bool = Field(default=False, description="Weed suppression needed")
    cash_crop_integration: Optional[str] = Field(None, description="Cash crop to integrate with")
    budget_per_acre: Optional[float] = Field(None, ge=0, description="Budget per acre")
    management_intensity: str = Field(default="moderate", description="Management intensity preference")


class CoverCropSelectionRequest(BaseModel):
    """Request for cover crop selection."""
    
    request_id: str = Field(..., description="Unique request identifier")
    location: Dict[str, Any] = Field(..., description="Location data with coordinates")
    soil_conditions: SoilConditions = Field(..., description="Current soil conditions")
    climate_data: Optional[ClimateData] = Field(None, description="Climate information")
    objectives: CoverCropObjectives = Field(..., description="Cover crop objectives")
    planting_window: Dict[str, date] = Field(..., description="Planting date range")
    field_size_acres: float = Field(..., gt=0, description="Field size in acres")
    farming_system: str = Field(default="conventional", description="Farming system type")
    equipment_constraints: Optional[List[str]] = Field(None, description="Equipment limitations")


class CoverCropRecommendation(BaseModel):
    """Individual cover crop recommendation."""
    
    species: CoverCropSpecies = Field(..., description="Recommended species")
    suitability_score: float = Field(..., ge=0.0, le=1.0, description="Suitability score")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="Confidence in recommendation")
    
    # Specific recommendations
    seeding_rate_recommendation: float = Field(..., ge=0, description="Recommended seeding rate (lbs/acre)")
    planting_date_recommendation: date = Field(..., description="Recommended planting date")
    termination_recommendation: str = Field(..., description="Recommended termination method")
    
    # Expected benefits
    expected_benefits: List[str] = Field(..., description="Expected benefits for this field")
    nitrogen_contribution: Optional[float] = Field(None, description="Expected N contribution (lbs/acre)")
    soil_improvement_score: float = Field(..., ge=0.0, le=1.0, description="Soil improvement potential")
    
    # Economic analysis
    cost_per_acre: Optional[float] = Field(None, ge=0, description="Estimated cost per acre")
    roi_estimate: Optional[float] = Field(None, description="ROI estimate percentage")
    
    # Implementation guidance
    management_notes: List[str] = Field(..., description="Management recommendations")
    potential_challenges: Optional[List[str]] = Field(None, description="Potential challenges")
    success_indicators: List[str] = Field(..., description="Success indicators to monitor")


class CoverCropMixture(BaseModel):
    """Cover crop mixture recommendation."""
    
    mixture_id: str = Field(..., description="Mixture identifier")
    mixture_name: str = Field(..., description="Mixture name")
    species_list: List[Dict[str, Any]] = Field(..., description="Species with seeding rates")
    total_seeding_rate: float = Field(..., ge=0, description="Total seeding rate (lbs/acre)")
    mixture_benefits: List[str] = Field(..., description="Combined benefits")
    complexity_level: str = Field(..., description="Management complexity")


class CoverCropSelectionResponse(BaseModel):
    """Response containing cover crop recommendations."""
    
    request_id: str = Field(..., description="Original request identifier")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    
    # Recommendations
    single_species_recommendations: List[CoverCropRecommendation] = Field(
        ..., description="Single species recommendations"
    )
    mixture_recommendations: Optional[List[CoverCropMixture]] = Field(
        None, description="Mixture recommendations"
    )
    
    # Analysis
    field_assessment: Dict[str, Any] = Field(..., description="Field condition analysis")
    climate_suitability: Dict[str, Any] = Field(..., description="Climate compatibility analysis")
    seasonal_considerations: List[str] = Field(..., description="Seasonal timing notes")
    
    # Guidance
    implementation_timeline: List[Dict[str, Any]] = Field(..., description="Implementation timeline")
    monitoring_recommendations: List[str] = Field(..., description="Monitoring guidelines")
    follow_up_actions: Optional[List[str]] = Field(None, description="Follow-up recommendations")
    
    # Metadata
    overall_confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score")
    data_sources: List[str] = Field(..., description="Data sources used")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }


class SpeciesLookupRequest(BaseModel):
    """Request for cover crop species information."""
    
    species_name: Optional[str] = Field(None, description="Species name to lookup")
    cover_crop_type: Optional[CoverCropType] = Field(None, description="Filter by type")
    hardiness_zone: Optional[str] = Field(None, description="Filter by hardiness zone")
    growing_season: Optional[GrowingSeason] = Field(None, description="Filter by season")
    primary_benefit: Optional[SoilBenefit] = Field(None, description="Filter by benefit")


class SpeciesLookupResponse(BaseModel):
    """Response with cover crop species information."""
    
    species_count: int = Field(..., description="Number of species returned")
    species_list: List[CoverCropSpecies] = Field(..., description="Matching species")
    filter_summary: Dict[str, Any] = Field(..., description="Applied filters summary")